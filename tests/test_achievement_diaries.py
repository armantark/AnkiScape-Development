"""Achievement Diaries: catalog integrity, progress, claiming, and migration.

Nothing here stubs the system under test. Player state is built from a real
``default_player_data`` and advanced with the real logic entry points, so a
green run means the diary graph actually works rather than that a fake agreed
with itself. The undo and review-dispatch layers live in
``test_achievement_diaries_integration.py``, which loads the add-on package.
"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    CLAIM_DATA,
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
)
from ankiscape.core.skill_registry import trainable_skill_definitions
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.achievement_diary_data import (
    ACHIEVEMENT_DIARY_CATALOG,
    BASE_CONDITION_KINDS,
    DiaryCondition,
    DiaryFamily,
    DiaryTask,
    DiaryTier,
    V108_DEED_REVALIDATION_SOURCE_IDS,
    diary_lamp_claim_id,
)
from ankiscape.logic.achievement_diary_derived import (
    DIARY_DERIVED_VALUE_CEILINGS,
    DIARY_DERIVED_VALUES,
)
from ankiscape.logic.achievement_diary_logic import (
    _award_task_coins,
    achievement_cabinet_view_pure,
    apply_achievement_diary_command_pure,
    claim_diary_tier_pure,
    condition_progress_pure,
    diary_tier_by_id_pure,
    diary_totals_pure,
    pin_diary_task_pure,
    refresh_achievement_diaries_pure,
    sanitize_achievement_diary_state_pure,
    task_progress_pure,
    tier_claim_state_pure,
    tier_reward_names_pure,
)
from ankiscape.logic.shop_logic import shop_diary_transaction_counter_key_pure
from ankiscape.logic_pure.logic_pure_claims import apply_claim_pure, claim_rows_pure
from ankiscape.logic_pure.logic_pure_equipment import can_equip_item_pure, equip_item_pure
from ankiscape.logic_pure.logic_pure_telemetry import record_achievement_progress_pure
from tests.achievement_diaries.test_catalog_scan import synthetic_items_yml
from tools.generate_achievement_diary_data import (
    FAMILIES,
    MORYTANIA_LEG_BONUSES,
    _equipment_rows,
    _requirement_conditions,
    resolve_condition_key,
)


ROOT = Path(__file__).resolve().parents[1]


class GeneratorSourceInputTest(unittest.TestCase):
    def test_equipment_rows_read_the_explicit_items_yml(self):
        items_yml, expected_ids = synthetic_items_yml()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "items.yml"
            source.write_text(items_yml, encoding="utf-8")
            rows = _equipment_rows(source)

        for item_name, (item_id, tier_index) in expected_ids.items():
            with self.subTest(item_name=item_name):
                block = rows.split(f"{item_name!r}: EquipmentItem(", 1)[1].split(
                    "    ),", 1
                )[0]
                self.assertIn(f"source_item_id={item_id}", block)
                self.assertIn(
                    f"bonuses=EquipmentBonuses(attack_stab={tier_index})",
                    block,
                )

    def test_rotated_skill_types_resolve_to_the_deeds_they_gate(self):
        harvest = (
            ROOT
            / "memory-bank/source-audits/achievement-diary-harvest-2026-07-26.json"
        )
        definitions = json.loads(harvest.read_text(encoding="utf-8"))[
            "task_definitions"
        ]
        cases = (
            (177, "Pyre At Will", "firemaking"),
            (199, "I'm a Lumberjack and I'm Okay", "woodcutting"),
            (333, "Make a Bolt For It", "fletching"),
        )

        for source_id, deed_name, expected_skill in cases:
            with self.subTest(deed=deed_name):
                task = definitions[str(source_id)]
                self.assertEqual(task["name"], deed_name)
                resolved_skills = {
                    condition[1]
                    for condition in _requirement_conditions(task)
                    if condition[0] == "skill_level"
                }
                self.assertIn(expected_skill, resolved_skills)


def _fresh():
    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


def _active_claim_family():
    shipped = next(
        family for family in ACHIEVEMENT_DIARY_CATALOG if family.id == "ardougne"
    )
    tiers = tuple(
        replace(
            tier,
            tasks=tuple(task for task in tier.tasks if not task.dormant),
            designed_task_count=0,
        )
        for tier in shipped.tiers
    )
    return replace(shipped, tiers=tiers)


def _set_counter(player, path, amount):
    node = player
    parts = path.split(".")
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = amount


def _complete_quest_for_reward(player, quest_id):
    from ankiscape.core.constants import QUEST_DATA
    from ankiscape.logic_pure.logic_pure_quest import apply_quest_progress_pure

    quest = QUEST_DATA[quest_id]
    prior_quests = {
        requirement["quest_id"]: copy.deepcopy(
            player["quests"].get(requirement["quest_id"])
        )
        for requirement in quest.get("required_quests", ())
    }
    prior_levels = {
        f"{requirement['skill_id']}_level": player.get(
            f"{requirement['skill_id']}_level"
        )
        for requirement in quest.get("required_skills", ())
    }
    for requirement in quest.get("required_quests", ()):
        player["quests"][requirement["quest_id"]] = {"completed": True}
    for requirement in quest.get("required_skills", ()):
        player[f"{requirement['skill_id']}_level"] = requirement["level"]

    final_stage = int(quest["stages"]) - 1
    player["quests"][quest_id] = {
        "started": True,
        "progress": final_stage,
        "completed": False,
    }
    final_requirement = next(
        (
            requirement
            for requirement in quest.get("stage_requirements", ())
            if int(requirement.get("stage", 0)) == final_stage
        ),
        {},
    )
    player.setdefault("quest_action_proofs", []).extend(
        final_requirement.get("required_actions", ())
    )
    player, ok, completed = apply_quest_progress_pure(player, quest_id, QUEST_DATA)
    assert ok and completed, quest_id
    for prerequisite_id, prior_state in prior_quests.items():
        if prior_state is None:
            player["quests"].pop(prerequisite_id, None)
        else:
            player["quests"][prerequisite_id] = prior_state
    for level_key, prior_level in prior_levels.items():
        if prior_level is None:
            player.pop(level_key, None)
        else:
            player[level_key] = prior_level
    return player


def _max_out_varrock_museum(player):
    """Drive the real museum to every Kudos point AnkiScape implements.

    Nothing here writes ``varrock_museum`` directly: the quiz and the specimen
    cases advance one review at a time through the live review entry point, and
    the quest stories go through Historian Minas' own command, so the figure the
    diary reads is one real play could actually produce.
    """
    from ankiscape.data.varrock_museum_data import (
        QUEST_KUDOS,
        QUIZ_DISPLAYS,
        SPECIMEN_DISPLAYS,
    )
    from ankiscape.logic.varrock_museum_logic import (
        apply_varrock_museum_command_pure,
        apply_varrock_museum_review_pure,
    )

    for _display in QUIZ_DISPLAYS:
        player, ok, info = apply_varrock_museum_review_pure(player)
        assert ok, info

    earned_items = {}
    for row in QUEST_KUDOS:
        quest_id = str(row["id"])
        required_item = row.get("required_item")
        if required_item:
            player = _complete_quest_for_reward(player, quest_id)
            item_name = str(required_item)
            quantity = int(player["inventory"].pop(item_name, 0))
            assert quantity > 0, item_name
            earned_items[item_name] = quantity
        else:
            player["quests"][quest_id] = {"completed": True}

    player["quests"]["the_dig_site"] = {"completed": True}
    player["equipment"] = dict(player.get("equipment") or {})
    player["equipment"]["hands"] = "Leather gloves"
    player["equipment"]["feet"] = "Leather boots"
    carried = dict(player.get("carried_inventory") or {})
    pack = dict(carried.get("varrock_museum") or {})
    pack.update({"Trowel": 1, "Rock pick": 1, "Specimen brush": 1})
    pack.update(earned_items)
    carried["varrock_museum"] = pack
    player["carried_inventory"] = carried

    player, ok, info = apply_varrock_museum_command_pure(
        player, "set_route", {"route": "cleaning"}
    )
    assert ok, info
    for _specimen in SPECIMEN_DISPLAYS:
        player, ok, info = apply_varrock_museum_review_pure(player)
        assert ok, info

    player, ok, info = apply_varrock_museum_command_pure(player, "claim_quest_stories")
    assert ok, info

    from ankiscape.data.shattered_heart_data import SHATTERED_HEART_SKILLS
    from ankiscape.logic.shattered_heart_logic import apply_shattered_heart_command_pure

    for skill in SHATTERED_HEART_SKILLS:
        for item_name in skill.rock_items:
            player["inventory"][item_name] = 1
    player, ok, info = apply_shattered_heart_command_pure(
        player, "add_completed_pairs"
    )
    assert ok, info
    return player


def _satisfy_condition(player, condition):
    """Put a real save into the exact durable state one condition reads."""
    if condition.kind == "skill_level":
        player[f"{condition.key}_level"] = max(
            condition.amount, int(player.get(f"{condition.key}_level", 1))
        )
    elif condition.kind == "quest":
        player.setdefault("quests", {})[condition.key] = {"completed": True}
    elif condition.kind == "hold_item":
        player["inventory"][condition.key] = condition.amount
    elif condition.kind in {"ledger_output", "ledger_action"}:
        skill_id, _, key = condition.key.partition(":")
        kwargs = (
            {"output_item": key, "output_qty": condition.amount}
            if condition.kind == "ledger_output"
            else {}
        )
        for _ in range(condition.amount if condition.kind == "ledger_action" else 1):
            record_achievement_progress_pure(player, skill_id, key, True, **kwargs)
    elif condition.kind == "ledger_action_family":
        from ankiscape.data.summoning_data import SUMMONING_ACTIONS_BY_ID

        skill_id, _, family_id = condition.key.partition(":")
        action_id = next(
            action_id
            for action_id, action in SUMMONING_ACTIONS_BY_ID.items()
            if action.family == family_id
        )
        for _ in range(condition.amount):
            record_achievement_progress_pure(player, skill_id, action_id, True)
    elif condition.kind == "counter":
        current, _need = condition_progress_pure(player, condition)
        _set_counter(player, condition.key, max(current, condition.amount))
    elif condition.kind == "combat_kill":
        player.setdefault("combat_kill_counts", {})[condition.key] = condition.amount
    elif condition.kind == "shop_transaction":
        transaction_type, _, remainder = condition.key.partition("|")
        shop_id, _, row_id = remainder.partition("|")
        counter_key = shop_diary_transaction_counter_key_pure(
            transaction_type,
            shop_id,
            row_id,
        )
        assert counter_key, condition.key
        player.setdefault("shop_transaction_counts", {})[counter_key] = condition.amount
    elif condition.kind == "state_equals":
        _set_counter(player, condition.key, condition.expected)
    elif condition.kind == "equipped_item":
        slot, _, item_name = condition.key.partition("|")
        player.setdefault("equipment", {})[slot] = item_name
    elif condition.kind == "any_of":
        _satisfy_condition(player, condition.alternatives[0])
    elif condition.kind == "derived_value":
        from ankiscape.logic.varrock_museum_logic import varrock_museum_kudos_pure

        assert condition.key == "varrock_museum_kudos", condition.key
        if varrock_museum_kudos_pure(player) < condition.amount:
            updated = _max_out_varrock_museum(dict(player))
            player.clear()
            player.update(updated)
    else:  # pragma: no cover - catalog integrity rejects unknown kinds
        raise AssertionError(f"unhandled condition kind {condition.kind}")
    return player


def _satisfy(player, task):
    for condition in task.conditions:
        _satisfy_condition(player, condition)
    return player


def _crafting_context(player, errors):
    """A real RuntimeActionContext, with the real achievement hook attached."""
    from ankiscape.core.logic import check_achievements
    from ankiscape.runtime.runtime_actions_shared import RuntimeActionContext

    def _award(exp_key, amount):
        player[exp_key] = float(player.get(exp_key, 0)) + float(amount)
        return amount

    return RuntimeActionContext(
        player_data=player,
        random_random=lambda: 0.5,
        show_error_message=lambda title, message: errors.append((title, message)),
        deactivate_current_skill=lambda: None,
        award_skill_exp=_award,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda *_args: None,
        check_achievements=check_achievements,
        save_player_data=lambda: None,
        refresh_skill_availability=lambda: None,
        show_exp=lambda _amount: None,
        show_activity_gain=lambda _message: None,
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


def _complete_tier(player, tier):
    for task in tier.tasks:
        _satisfy(player, task)
    return refresh_achievement_diaries_pure(player)[0]


class CatalogIntegrityTest(unittest.TestCase):
    def test_kudos_required_items_follow_player_finishable_quest_routes(self):
        from ankiscape.data.varrock_museum_data import QUEST_KUDOS
        from tools.audit_item_reachability import build_reachability_report

        routes = build_reachability_report()["routes"]
        required_items = {
            str(row["required_item"])
            for row in QUEST_KUDOS
            if row.get("required_item")
        }
        self.assertEqual(
            required_items - routes.keys(),
            {"Dagon'hai history", "Prophecy tablet"},
        )

    def test_every_family_carries_its_period_tiers(self):
        self.assertEqual(
            [family.id for family in ACHIEVEMENT_DIARY_CATALOG],
            [
                "ardougne",
                "falador",
                "fremennik",
                "karamja",
                "lumbridge",
                "morytania",
                "seers",
                "varrock",
                "burthorpe",
                "miscellaneous",
            ],
        )
        for family in ACHIEVEMENT_DIARY_CATALOG:
            expected = [1, 2, 3, 4] if family.kind == "regional" else [1]
            self.assertEqual([tier.index for tier in family.tiers], expected, family.id)

    def test_tier_effort_budget_follows_the_design_contract(self):
        for family in ACHIEVEMENT_DIARY_CATALOG:
            expected = [1, 2, 3, 4] if family.kind == "regional" else [1]
            self.assertEqual([tier.effort_multiplier for tier in family.tiers], expected)

    def test_ids_are_unique_and_no_condition_is_shared_between_families(self):
        task_ids = [
            task.id
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
        ]
        self.assertEqual(len(task_ids), len(set(task_ids)))
        source_ids = [
            task.source_id
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
        ]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        tier_ids = [
            tier.id for family in ACHIEVEMENT_DIARY_CATALOG for tier in family.tiers
        ]
        self.assertEqual(len(tier_ids), len(set(tier_ids)))

    def test_every_task_states_its_availability_and_cites_its_source(self):
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                for task in tier.tasks:
                    self.assertEqual(bool(task.conditions), not task.dormant, task.id)
                    self.assertTrue(task.name.strip(), task.id)
                    self.assertTrue(task.description.strip(), task.id)
                    self.assertIn("Darkan", task.source, task.id)
                    self.assertGreaterEqual(task.source_id, 0, task.id)

    def test_honest_stop_classification_is_explicit_and_complete(self):
        tasks = [
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
        ]
        quest_deed_source_ids = {
            task.source_id
            for task in tasks
            if any(condition.kind == "quest" for condition in task.conditions)
        }
        classifications = [
            "dormant"
            if task.dormant
            else "anchor"
            if task.curation_anchor
            else "quest_deed"
            if task.source_id in quest_deed_source_ids
            else "real_deed"
            for task in tasks
        ]

        self.assertEqual(len(tasks), 474)
        self.assertEqual(classifications.count("dormant"), 116)
        self.assertEqual(classifications.count("real_deed"), 333)
        self.assertEqual(classifications.count("anchor"), 22)
        self.assertEqual(classifications.count("quest_deed"), 3)
        self.assertEqual(quest_deed_source_ids, {440, 441, 451})

    def test_first_deed_tranche_uses_durable_predicates_not_requirement_gates(self):
        for source_id in V108_DEED_REVALIDATION_SOURCE_IDS:
            task = _task_by_source_id(source_id)
            kinds = {
                condition.kind
                for root in task.conditions
                for condition in (root, *root.alternatives)
            }
            self.assertTrue(
                kinds & {
                    "ledger_output",
                    "ledger_action",
                    "combat_kill",
                    "shop_transaction",
                },
                task.id,
            )
            self.assertFalse(kinds & {"skill_level", "quest"}, task.id)

        all_conditions = [condition for _task, condition in _every_condition()]
        self.assertTrue(any(c.kind == "ledger_output" for c in all_conditions))
        self.assertTrue(any(c.kind == "shop_transaction" for c in all_conditions))
        self.assertFalse(
            any(
                c.kind == "counter"
                and c.key.startswith(
                    ("achievement_progress.skills.", "shop_transaction_counts.")
                )
                for c in all_conditions
            )
        )

    def test_every_tier_advertises_only_rewards_it_can_actually_hand_over(self):
        """A tier must never name a reward slot it cannot fill.

        Burthorpe/Taverley shipped with an empty ``reward_item`` and no bundle,
        so claiming it granted nothing and printed a sentence with a hole where
        the item name belonged.
        """

        known = {row.storage_key for row in ITEM_DEFINITIONS}
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                items = tier_reward_names_pure(tier)
                if family.kind == "miscellaneous":
                    # Miscellaneous pays per task, so it owns no tier reward.
                    self.assertEqual(items, (), tier.id)
                    continue
                self.assertTrue(items, tier.id)
                if tier.reward_item:
                    self.assertIn(tier.reward_item, EQUIPMENT_DATA, tier.id)
                for name, count in tier.reward_bundle:
                    self.assertIn(name, known, name)
                    self.assertGreater(count, 0, name)

    def test_every_regional_lamp_has_a_distinct_sourced_bank_claim(self):
        expected = {}
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                if tier.lamp is None:
                    continue
                claim_id = diary_lamp_claim_id(tier.id)
                expected[claim_id] = tier
        self.assertEqual(len(expected), 32)
        self.assertTrue(expected.keys() <= CLAIM_DATA.keys())
        for claim_id, tier in expected.items():
            claim = CLAIM_DATA[claim_id]
            self.assertEqual(claim["required_diary_tier"], tier.id)
            self.assertEqual(claim["xp_amount"], float(tier.lamp.experience))
            self.assertEqual(claim["minimum_level"], tier.lamp.minimum_level)
            self.assertTrue(claim["source"], claim_id)

    def test_every_tier_has_a_roster(self):
        empty = [
            tier.id
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            if not tier.tasks
        ]
        self.assertEqual(empty, [])

    def test_cache_absence_does_not_drop_existing_pinned_requirement_rows(self):
        restored_source_ids = {
            0,
            97,
            107,
            125,
            188,
            192,
            209,
            257,
            267,
            268,
            291,
            952,
            963,
            964,
            971,
            983,
            985,
            993,
        }
        shipped = {
            task.source_id
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
        }
        self.assertTrue(restored_source_ids.issubset(shipped))

    def test_every_miscellaneous_task_has_a_live_coin_reward(self):
        family = next(
            family
            for family in ACHIEVEMENT_DIARY_CATALOG
            if family.id == "miscellaneous"
        )
        self.assertTrue(family.tiers[0].tasks)
        self.assertTrue(all(task.coin_reward == 100 for task in family.tiers[0].tasks))

    def test_implemented_activity_deeds_are_not_left_latent(self):
        tasks = {
            task.source_id: task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
        }
        for source_id in (3001, 3032, 3033):
            self.assertFalse(tasks[source_id].dormant, source_id)
            self.assertTrue(tasks[source_id].conditions, source_id)

    def test_regional_tiers_have_exact_twelve_slot_designed_rosters(self):
        for family in ACHIEVEMENT_DIARY_CATALOG:
            if family.kind != "regional":
                continue
            for tier in family.tiers:
                self.assertEqual(tier.designed_task_count, 12, tier.id)
                self.assertEqual(tier.total_tasks, 12, tier.id)
                self.assertEqual(len(tier.tasks), tier.total_tasks, tier.id)

    def test_progression_anchors_are_bounded_reachable_and_explicit(self):
        anchors = []
        for family in ACHIEVEMENT_DIARY_CATALOG:
            if family.kind != "regional":
                continue
            for tier in family.tiers:
                tier_anchors = [task for task in tier.tasks if task.curation_anchor]
                self.assertLessEqual(len(tier_anchors), 3, tier.id)
                anchors.extend(tier_anchors)
        self.assertEqual(len(anchors), 22)
        self.assertEqual(
            {task.id.split("_", 1)[0] for task in anchors},
            {"falador", "fremennik", "karamja", "seers"},
        )
        for task in anchors:
            self.assertFalse(task.dormant, task.id)
            self.assertTrue(task.conditions, task.id)
            self.assertIn("not a period task identity", task.source, task.id)

        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                authentic_levels = {
                    (condition.key, condition.amount)
                    for task in tier.tasks
                    if not task.curation_anchor
                    for condition in task.conditions
                    if condition.kind == "skill_level"
                }
                for anchor in (task for task in tier.tasks if task.curation_anchor):
                    condition = anchor.conditions[0]
                    self.assertNotIn(
                        (condition.key, condition.amount),
                        authentic_levels,
                        anchor.id,
                    )

    def test_cross_tier_curation_keeps_the_original_durable_identity(self):
        marker = "original period tier "
        moved = []
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                for task in tier.tasks:
                    if marker not in task.source:
                        continue
                    original_tier = task.source.split(marker, 1)[1].split(";", 1)[0]
                    self.assertTrue(
                        task.id.startswith(f"{family.id}_{original_tier}_"),
                        task.id,
                    )
                    moved.append(task)
        self.assertTrue(moved)

    def test_cutoff_denominators_are_the_recorded_534_tasks(self):
        totals = {
            family.id: sum(tier.total_tasks for tier in family.tiers)
            for family in ACHIEVEMENT_DIARY_CATALOG
        }
        regional = sum(
            total
            for family_id, total in totals.items()
            if family_id not in {"burthorpe", "miscellaneous"}
        )
        self.assertEqual(regional, 384)
        self.assertEqual(totals["burthorpe"], 55)
        self.assertEqual(totals["miscellaneous"], 95)
        self.assertEqual(sum(totals.values()), 534)

    def test_every_regional_tier_reward_item_is_real_wearable_equipment(self):
        """Guard against the inert-row failure: a reward nobody can ever wear."""
        for family in ACHIEVEMENT_DIARY_CATALOG:
            if family.kind != "regional":
                continue
            for tier in family.tiers:
                self.assertIn(tier.reward_item, EQUIPMENT_DATA, tier.id)
                self.assertTrue(EQUIPMENT_DATA[tier.reward_item].slot)

    def test_tier_reward_items_are_distinct_within_a_family(self):
        for family in ACHIEVEMENT_DIARY_CATALOG:
            items = [tier.reward_item for tier in family.tiers if tier.reward_item]
            self.assertEqual(len(items), len(set(items)), family.id)


def _every_condition():
    """Every shipped condition, alternatives included, with its task id."""
    for family in ACHIEVEMENT_DIARY_CATALOG:
        for tier in family.tiers:
            for task in tier.tasks:
                for condition in task.conditions:
                    yield task, condition
                    for alternative in condition.alternatives:
                        yield task, alternative


def _task_by_source_id(source_id):
    return next(
        task
        for family in ACHIEVEMENT_DIARY_CATALOG
        for tier in family.tiers
        for task in tier.tasks
        if task.source_id == source_id
    )


def _assert_task_credited(testcase, player, source_id):
    task = _task_by_source_id(source_id)
    testcase.assertTrue(task_progress_pure(player, task)[0], task.id)
    refreshed, newly = refresh_achievement_diaries_pure(player)
    completed = refreshed["achievement_diaries"]["completed_tasks"]
    testcase.assertTrue(task.id in newly or task.id in completed, task.id)


def _any_of_tasks():
    return [
        (task, condition)
        for family in ACHIEVEMENT_DIARY_CATALOG
        for tier in family.tiers
        for task in tier.tasks
        for condition in task.conditions
        if condition.kind == "any_of"
    ]


class ConditionKeyResolutionTest(unittest.TestCase):
    """A key nothing writes reads zero forever, and the panel never says so.

    That is the exact shape of the two defects this family shipped and then
    fixed: a ledger key filed under the wrong owning skill, and a counter path
    that resolved against nothing. Both rendered an honest-looking 0/1 while
    being impossible. This runs the generator's own resolution check over the
    shipped catalog, so a hand-edit cannot reintroduce either.
    """

    def test_every_condition_key_names_state_the_runtime_writes(self):
        failures = [
            f"{task.id}: {error}"
            for task, condition in _every_condition()
            if (
                error := resolve_condition_key(
                    condition.kind, condition.key, condition.expected
                )
            )
        ]
        self.assertEqual(failures, [])

    def test_the_resolver_rejects_the_shapes_it_exists_to_catch(self):
        """Guard the guard: a check that passes everything catches nothing."""
        self.assertTrue(resolve_condition_key("counter", "combat_kill_counts.no_such"))
        self.assertTrue(resolve_condition_key("counter", "no_such_activity.runs"))
        self.assertTrue(
            resolve_condition_key("ledger_action", "cooking:draw_bucket_of_water")
        )
        self.assertTrue(resolve_condition_key("ledger_action", "no_such_skill:thing"))
        self.assertEqual(
            resolve_condition_key("ledger_action", "utility:draw_bucket_of_water"), ""
        )
        self.assertTrue(resolve_condition_key("combat_kill", "no_such_enemy"))
        self.assertTrue(resolve_condition_key("quest", "no_such_quest"))
        self.assertTrue(resolve_condition_key("skill_level", "sailing"))
        self.assertTrue(resolve_condition_key("shop_transaction", "buy|no_shop|no_row"))
        self.assertTrue(
            resolve_condition_key("state_equals", "no_such.path", "anything")
        )
        self.assertTrue(
            resolve_condition_key("ledger_action_family", "summoning:no_such_family")
        )
        self.assertTrue(
            resolve_condition_key("equipped_item", "feet|Spiked gauntlets")
        )
        self.assertTrue(
            resolve_condition_key(
                "counter", "shop_transaction_counts.unconsumed_transaction"
            )
        )
        self.assertTrue(
            resolve_condition_key("counter", "fight_caves.kill_counts.tz_kih")
        )


class NewConditionDegradationTest(unittest.TestCase):
    def test_combat_kill_degrades_on_absent_or_wrong_typed_state(self):
        condition = DiaryCondition("combat_kill", "highwayman")
        self.assertEqual(condition_progress_pure({}, condition), (0, 1))
        self.assertEqual(
            condition_progress_pure(
                {"combat_kill_counts": "not a mapping"}, condition
            ),
            (0, 1),
        )

    def test_shop_transaction_degrades_on_absent_or_wrong_typed_state(self):
        condition = DiaryCondition(
            "shop_transaction",
            "buy|aemads_adventuring_supplies|aemads_adventuring_supplies:9:227",
        )
        self.assertEqual(condition_progress_pure({}, condition), (0, 1))
        self.assertEqual(
            condition_progress_pure(
                {"shop_transaction_counts": "not a mapping"}, condition
            ),
            (0, 1),
        )

    def test_shop_transaction_reads_the_durable_counter_not_bounded_history(self):
        condition = DiaryCondition(
            "shop_transaction",
            "buy|aemads_adventuring_supplies|aemads_adventuring_supplies:9:227",
            2,
        )
        self.assertEqual(
            condition_progress_pure(
                {
                    "shop_events": [],
                    "shop_transaction_counts": {"aemads_vial_of_water": 3},
                },
                condition,
            ),
            (3, 2),
        )

    def test_state_equals_degrades_on_absent_or_wrong_typed_state(self):
        condition = DiaryCondition(
            "state_equals",
            "farm_patches.taverley_potato.last_crop_id",
            expected="potato",
        )
        self.assertEqual(condition_progress_pure({}, condition), (0, 1))
        self.assertEqual(
            condition_progress_pure({"farm_patches": []}, condition), (0, 1)
        )

    def test_ledger_action_family_degrades_on_absent_or_wrong_typed_state(self):
        condition = DiaryCondition("ledger_action_family", "summoning:infuse")
        self.assertEqual(condition_progress_pure({}, condition), (0, 1))
        self.assertEqual(
            condition_progress_pure({"achievement_progress": []}, condition),
            (0, 1),
        )

    def test_equipped_item_degrades_on_absent_or_wrong_typed_state(self):
        condition = DiaryCondition("equipped_item", "hands|Spiked gauntlets")
        self.assertEqual(condition_progress_pure({}, condition), (0, 1))
        self.assertEqual(
            condition_progress_pure({"equipment": []}, condition), (0, 1)
        )


class StageOneRealPathTest(unittest.TestCase):
    def test_stage_one_combat_tasks_complete_through_real_combat_bursts(self):
        from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure
        from ankiscape.core.constants import COMBAT_ENEMY_DATA

        for source_id, enemy_id in (
            (124, "highwayman"),
            (135, "ice_giant"),
            (153, "rock_crab"),
            (161, "black_unicorn"),
        ):
            with self.subTest(source_id=source_id):
                player = _fresh()
                player.update(
                    current_combat_target=enemy_id,
                    attack_level=99,
                    strength_level=99,
                    defense_level=99,
                    constitution_level=99,
                    combat_lifepoints=990,
                )
                player, ok, result = apply_combat_burst_pure(
                    player,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                    ticks=500,
                    rng=lambda: 0.5,
                )
                self.assertTrue(ok, result)
                _assert_task_credited(self, player, source_id)

    def test_vial_deeds_completes_through_aemads_shop(self):
        from ankiscape.logic.shop_logic import apply_shop_buy_pure

        player = _fresh()
        player["inventory"]["Coins"] = 100
        player, result = apply_shop_buy_pure(
            player,
            "aemads_adventuring_supplies",
            "aemads_adventuring_supplies:9:227",
            1,
        )
        self.assertTrue(result["allowed"], result)
        _assert_task_credited(self, player, 15)

    def test_dibs_on_the_first_batch_completes_through_taverley_planting(self):
        from ankiscape.data.farming_data import FARMING_CROPS_BY_ID
        from ankiscape.logic.farming_logic import execute_farm_field_step_pure

        player = _fresh()
        crop = FARMING_CROPS_BY_ID["potato"]
        player["inventory"].update(
            {"Rake": 1, "Seed dibber": 1, "Spade": 1, crop.seed_item: crop.seeds}
        )
        player, ok, info = execute_farm_field_step_pure(
            player,
            {
                "kind": "plant",
                "patch_id": "taverley_potato",
                "crop_id": "potato",
                "compost_tier": "none",
            },
        )
        self.assertTrue(ok, info)
        _assert_task_credited(self, player, 544)

    def test_heel_boy_completes_through_summoning_a_spirit_wolf(self):
        from ankiscape.logic.summoning_logic import summon_familiar_pure

        player = _fresh()
        player["inventory"]["Spirit wolf pouch"] = 1
        player, ok, info = summon_familiar_pure(player, "spiritwolf")
        self.assertTrue(ok, info)
        _assert_task_credited(self, player, 557)

    def test_hold_item_tasks_complete_through_real_item_grants(self):
        from ankiscape.logic.shop_logic import (
            apply_shop_buy_pure,
            apply_shop_vendor_action_pure,
        )

        amulet_owner = _fresh()
        amulet_owner["inventory"]["Coins"] = 500
        amulet_owner, result = apply_shop_buy_pure(
            amulet_owner,
            "sarahs_farming_shop",
            "sarahs_farming_shop:0:12622",
            1,
        )
        self.assertTrue(result["allowed"], result)
        _assert_task_credited(self,amulet_owner, 115)

        beer_owner = _fresh()
        beer_owner["inventory"]["Coins"] = 10
        beer_owner, result = apply_shop_vendor_action_pure(
            beer_owner, "bartender_buy_beer", 1
        )
        self.assertTrue(result["allowed"], result)
        _assert_task_credited(self,beer_owner, 116)

    def test_fill_yer_bucket_completes_through_the_utility_runtime(self):
        from ankiscape.runtime.runtime_actions_utility import handle_utility_answer

        player = _fresh()
        player["current_utility"] = "draw_bucket_of_water"
        player["inventory"]["Bucket"] = 1
        self.assertTrue(handle_utility_answer(_crafting_context(player, [])))
        _assert_task_credited(self, player, 121)

    def test_a_gift_from_khazard_completes_through_the_summoning_runtime(self):
        from ankiscape.runtime.runtime_actions_production import handle_summoning_answer

        player = _fresh()
        player["current_summoning"] = "infuse_spiritwolf"
        player["inventory"].update(
            {"Pouch": 1, "Gold charm": 1, "Spirit shards": 7, "Wolf bones": 1}
        )
        self.assertTrue(handle_summoning_answer(_crafting_context(player, [])))
        _assert_task_credited(self, player, 13)

    def test_spiked_gauntlets_task_completes_through_shop_and_equip(self):
        from ankiscape.logic.shop_logic import apply_shop_buy_pure

        player = _fresh()
        player["inventory"]["Coins"] = 10
        player, result = apply_shop_buy_pure(
            player,
            "turaels_slayer_equipment",
            "turaels_slayer_equipment:22:23035",
            1,
        )
        self.assertTrue(result["allowed"], result)
        inventory, equipment, ok = equip_item_pure(
            "Spiked gauntlets",
            player["inventory"],
            player["equipment"],
            EQUIPMENT_DATA,
        )
        self.assertTrue(ok)
        player["inventory"] = inventory
        player["equipment"] = equipment
        _assert_task_credited(self, player, 551)

    def test_chain_store_requires_waynes_purchase_and_body_slot_equip(self):
        from ankiscape.logic.shop_logic import apply_shop_buy_pure

        task = _task_by_source_id(129)
        self.assertEqual(
            [(condition.kind, condition.key) for condition in task.conditions],
            [
                (
                    "shop_transaction",
                    "buy|waynes_chains|waynes_chains:3:1107",
                ),
                ("equipped_item", "body|Black chainbody"),
            ],
        )
        self.assertEqual(
            [(condition.kind, condition.key, condition.amount) for condition in task.access_gates],
            [("skill_level", "defense", 10)],
        )

        player = _fresh()
        player["defense_level"] = 9
        player = refresh_achievement_diaries_pure(player)[0]
        player["defense_level"] = 10
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertEqual(newly, ())
        self.assertFalse(task_progress_pure(player, task)[0])

        player["inventory"]["Coins"] = 10_000
        player, result = apply_shop_buy_pure(
            player,
            "waynes_chains",
            "waynes_chains:3:1107",
            1,
        )
        self.assertTrue(result["allowed"], result)
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertEqual(newly, ())
        self.assertFalse(task_progress_pure(player, task)[0])

        inventory, equipment, equipped = equip_item_pure(
            "Black chainbody",
            player["inventory"],
            player["equipment"],
            EQUIPMENT_DATA,
        )
        self.assertTrue(equipped)
        player["inventory"] = inventory
        player["equipment"] = equipment
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertEqual(newly, (task.id,))
        self.assertTrue(task_progress_pure(player, task)[0])
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertEqual(newly, ())


class StageTwoRealPathTest(unittest.TestCase):
    def test_ledger_output_task_completes_through_the_smithing_runtime(self):
        from ankiscape.runtime.runtime_actions_production import handle_smithing_answer

        player = _fresh()
        player["smithing_level"] = 30
        player["current_smith"] = "smelt_steel_bar"
        player["inventory"].update({"Iron ore": 1, "Coal": 2})

        self.assertTrue(handle_smithing_answer(_crafting_context(player, [])))
        self.assertEqual(
            player["achievement_progress"]["skills"]["smithing"]["outputs"][
                "Steel bar"
            ],
            1,
        )
        _assert_task_credited(self, player, 86)

    def test_the_fruit_of_the_sea_completes_through_lumbridge_shop_handlers(self):
        from ankiscape.logic.shop_logic import apply_shop_sell_pure

        from ankiscape.core.constants import FISHING_DATA
        from ankiscape.logic_pure.logic_pure_gathering import apply_fishing_action_pure

        player = _fresh()
        inventory, _exp, ok, output, _rewards = apply_fishing_action_pure(
            "catch_shrimp_anchovies",
            player["inventory"],
            FISHING_DATA,
            fishing_level=15,
            rolls=(1.0, 0.0),
        )
        self.assertTrue(ok)
        self.assertEqual(output, "Raw shrimps")
        player["inventory"] = inventory
        player, result = apply_shop_sell_pure(
            player, "lumbridge_fishing_supplies", "Raw shrimps", 1
        )
        self.assertTrue(result["allowed"], result)
        _assert_task_credited(self, player, 79)

    def test_play_dead_doggy_completes_through_a_real_ket_zek_kill(self):
        from ankiscape.logic.fight_caves_logic import (
            apply_fight_caves_command_pure,
            apply_fight_caves_review_pure,
        )

        player = _fresh()
        player.update(
            attack_level=99,
            strength_level=99,
            defense_level=99,
            constitution_level=99,
            combat_lifepoints=990,
            combat_auto_eat_food=[],
            combat_auto_flee_percent=0,
        )
        player, ok, info = apply_fight_caves_command_pure(player, "enter")
        self.assertTrue(ok, info)
        player["fight_caves"].update(
            wave=31,
            roster=[
                {
                    "instance_id": "diary-ket-zek",
                    "enemy_id": "ket_zek",
                    "lifepoints": 1,
                }
            ],
            engaged_instance_id="diary-ket-zek",
        )
        player, ok, result = apply_fight_caves_review_pure(
            player, lambda: 0.0, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        _assert_task_credited(self, player, 212)

    def test_grand_candle_completes_through_the_candle_maker_shop(self):
        from ankiscape.logic.shop_logic import apply_shop_buy_pure

        player = _fresh()
        player["inventory"]["Coins"] = 10
        player, result = apply_shop_buy_pure(
            player, "candle_shop", "candle_shop:0:36", 1
        )
        self.assertTrue(result["allowed"], result)
        _assert_task_credited(self, player, 230)

    def test_read_all_about_it_completes_through_bennys_vendor_action(self):
        from ankiscape.logic.shop_logic import apply_shop_vendor_action_pure

        player = _fresh()
        player["inventory"]["Coins"] = 100
        player, result = apply_shop_vendor_action_pure(
            player, "benny_buy_varrock_herald", 1
        )
        self.assertTrue(result["allowed"], result)
        _assert_task_credited(self, player, 263)

    def test_salt_in_the_wound_awards_live_dungeoneering_xp_and_keeps_empty_ledgers(self):
        player = _complete_quest_for_reward(_fresh(), "salt_in_the_wound")
        self.assertTrue(player["quests"]["salt_in_the_wound"]["completed"])
        self.assertEqual(player["dungeoneering_exp"], 5000.0)
        self.assertEqual(player["pending_skill_exp_rewards"], {})
        self.assertEqual(
            player["achievement_progress"]["skills"]["dungeoneering"],
            {"actions": {}, "outputs": {}},
        )

        reloaded = migrate_loaded_data(copy.deepcopy(player), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(reloaded["dungeoneering_exp"], 5000.0)
        self.assertEqual(reloaded["dungeoneering_level"], 20)
        self.assertEqual(reloaded["pending_skill_exp_rewards"], {})
        self.assertEqual(
            reloaded["achievement_progress"]["skills"]["dungeoneering"],
            {"actions": {}, "outputs": {}},
        )


class AnyOfConditionTest(unittest.TestCase):
    def test_the_catalog_ships_any_of_tasks(self):
        self.assertTrue(_any_of_tasks())

    def test_no_alternative_nests_another_disjunction(self):
        for _task, condition in _any_of_tasks():
            self.assertTrue(condition.alternatives)
            for alternative in condition.alternatives:
                self.assertIn(alternative.kind, BASE_CONDITION_KINDS)
                self.assertEqual(alternative.alternatives, ())

    def test_each_alternative_alone_credits_its_task(self):
        """One dead disjunct is invisible unless every one is driven alone.

        The surviving alternatives keep the panel showing honest progress, so a
        variant id that no longer exists would never surface in play.
        """
        for task, condition in _any_of_tasks():
            for index, alternative in enumerate(condition.alternatives):
                player = _fresh()
                for other in task.conditions:
                    if other is not condition:
                        _satisfy_condition(player, other)
                _satisfy_condition(player, alternative)
                self.assertTrue(
                    task_progress_pure(player, task)[0],
                    f"{task.id} alternative {index} ({alternative.key})",
                )
                _player, newly = refresh_achievement_diaries_pure(player)
                self.assertIn(task.id, newly, f"{task.id} alternative {index}")

    def test_no_any_of_task_is_free_on_a_default_save(self):
        player = _fresh()
        for task, _condition in _any_of_tasks():
            self.assertFalse(task_progress_pure(player, task)[0], task.id)

    def test_an_empty_or_unknown_disjunction_is_unsatisfiable(self):
        player = _fresh()
        empty = DiaryCondition("any_of", "", 1, "Nothing at all")
        self.assertEqual(condition_progress_pure(player, empty), (0, 1))
        unknown = DiaryCondition(
            "any_of",
            "",
            1,
            "Only unknown kinds",
            (DiaryCondition("no_such_kind", "whatever", 1, ""),),
        )
        self.assertEqual(condition_progress_pure(player, unknown), (0, 1))

    def test_progress_reports_the_closest_alternative(self):
        player = _fresh()
        player["attack_level"] = 40
        condition = DiaryCondition(
            "any_of",
            "",
            1,
            "Either ladder",
            (
                DiaryCondition("skill_level", "attack", 50, "Level 50 Attack"),
                DiaryCondition("skill_level", "strength", 99, "Level 99 Strength"),
            ),
        )
        self.assertEqual(condition_progress_pure(player, condition), (40, 50))


class DerivedValueConditionTest(unittest.TestCase):
    def _thresholds(self):
        return [
            (task, condition)
            for task, condition in _every_condition()
            if condition.kind == "derived_value"
        ]

    def test_the_catalog_ships_derived_value_tasks(self):
        self.assertTrue(self._thresholds())

    def test_museum_reaches_its_true_kudos_ceiling_through_real_handlers(self):
        """Earn the implemented ceiling without manufacturing gated items.

        One dropped specimen case costs ten, while an unreachable quest item
        silently costs its row's Kudos. This plays the museum to exhaustion
        through its real entry points and obtains every gated item from a live
        quest reward before asserting the ceiling.
        """
        player = _max_out_varrock_museum(_fresh())
        for name, ceiling in DIARY_DERIVED_VALUE_CEILINGS.items():
            reached = DIARY_DERIVED_VALUES[name](player)
            self.assertEqual(reached, ceiling, name)
            for task, condition in self._thresholds():
                if condition.key == name:
                    self.assertGreaterEqual(reached, condition.amount, task.id)

    def test_playing_the_museum_credits_the_kudos_tasks(self):
        tasks = [task for task, _condition in self._thresholds()]
        player = _fresh()
        for task in tasks:
            self.assertFalse(task_progress_pure(player, task)[0], task.id)
        player = _max_out_varrock_museum(player)
        player, newly = refresh_achievement_diaries_pure(player)
        for task in tasks:
            self.assertIn(task.id, newly, task.id)

    def test_an_unregistered_name_is_refused_at_import_time(self):
        from ankiscape.data import achievement_diary_data as module

        family = ACHIEVEMENT_DIARY_CATALOG[0]
        tier = family.tiers[0]
        broken = DiaryTask(
            "typo_task",
            "Typo",
            "Names a derivation nobody registered.",
            (DiaryCondition("derived_value", "varock_museum_kudos", 50, "Kudos"),),
            "test",
            -1,
        )
        original = module.ACHIEVEMENT_DIARY_CATALOG
        module.ACHIEVEMENT_DIARY_CATALOG = (
            DiaryFamily(
                family.id,
                family.name,
                family.kind,
                (
                    DiaryTier(
                        tier.id, tier.name, tier.index, tier.reward_item,
                        tier.reward_summary, (broken,),
                    ),
                ),
            ),
        )
        try:
            with self.assertRaises(ImportError):
                module._assert_derived_values_are_registered()
        finally:
            module.ACHIEVEMENT_DIARY_CATALOG = original

    def test_an_unregistered_name_never_reads_as_satisfied(self):
        """The runtime fallback is zero, so a typo can never pay out."""
        player = _max_out_varrock_museum(_fresh())
        unknown = DiaryCondition("derived_value", "varock_museum_kudos", 50, "Kudos")
        self.assertEqual(condition_progress_pure(player, unknown), (0, 50))
        known = DiaryCondition("derived_value", "varrock_museum_kudos", 50, "Kudos")
        self.assertEqual(
            condition_progress_pure(player, known)[0],
            DIARY_DERIVED_VALUE_CEILINGS["varrock_museum_kudos"],
        )


class TaskProgressTest(unittest.TestCase):
    def test_a_fresh_save_has_credited_nothing_it_cannot_prove(self):
        player = _fresh()
        totals = diary_totals_pure(player)
        self.assertEqual(totals["completed"], 0)
        self.assertGreater(totals["total"], 100)

    def test_meeting_a_task_condition_credits_it(self):
        player = _fresh()
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        task = next(
            task
            for tier in family.tiers
            for task in tier.tasks
            if not task.dormant
        )
        self.assertFalse(task_progress_pure(player, task)[0])
        player = _satisfy(player, task)
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertIn(task.id, newly)
        self.assertIn(task.id, player["achievement_diaries"]["completed_tasks"])

    def test_completion_is_sticky_after_the_proving_state_is_lost(self):
        player = _fresh()
        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.curation_anchor
        )
        condition = task.conditions[0]
        player = _satisfy(player, task)
        player = refresh_achievement_diaries_pure(player)[0]
        self.assertIn(task.id, player["achievement_diaries"]["completed_tasks"])

        player[f"{condition.key}_level"] = 1
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertEqual(newly, ())
        self.assertIn(task.id, player["achievement_diaries"]["completed_tasks"])

    def test_levels_alone_complete_only_the_twenty_two_curation_anchors(self):
        player = _fresh()
        anchors = {
            task.id
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.curation_anchor
        }
        for skill in trainable_skill_definitions():
            player[f"{skill.id}_level"] = 126

        player, newly = refresh_achievement_diaries_pure(player)

        self.assertEqual(len(anchors), 22)
        self.assertEqual(set(newly), anchors)
        self.assertEqual(
            set(player["achievement_diaries"]["completed_tasks"]), anchors
        )

    def test_each_quest_completion_deed_fires_only_on_its_own_quest(self):
        quest_deeds = [
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if any(condition.kind == "quest" for condition in task.conditions)
        ]
        self.assertEqual({task.source_id for task in quest_deeds}, {440, 441, 451})

        for task in quest_deeds:
            with self.subTest(task=task.id):
                condition = task.conditions[0]
                player = _fresh()
                player["quests"]["rat_catchers"] = {"completed": True}
                player, newly = refresh_achievement_diaries_pure(player)
                self.assertEqual(newly, ())

                player["quests"][condition.key] = {"completed": True}
                player, newly = refresh_achievement_diaries_pure(player)
                self.assertEqual(newly, (task.id,))

    def test_a_multi_condition_task_reports_conditions_met(self):
        player = _fresh()
        task = next(
            t
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for t in tier.tasks
            if len(t.conditions) > 1
        )
        satisfied, have, need = task_progress_pure(player, task)
        self.assertFalse(satisfied)
        self.assertEqual(need, len(task.conditions))
        self.assertLess(have, need)

    def test_every_shipped_task_can_flip_complete_in_real_save_state(self):
        tasks = [
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if not task.dormant
        ]
        player = _fresh()
        for task in tasks:
            _satisfy(player, task)
            self.assertTrue(task_progress_pure(player, task)[0], task.id)
        player, newly = refresh_achievement_diaries_pure(player)
        expected = {task.id for task in tasks}
        self.assertEqual(set(newly), expected)
        self.assertEqual(
            set(player["achievement_diaries"]["completed_tasks"]), expected
        )

    def test_dormant_tasks_have_no_predicate_and_never_complete_from_access_gates(self):
        dormant = [
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.dormant
        ]
        player = _fresh()
        for task in dormant:
            self.assertEqual(task.conditions, (), task.id)
            for access_gate in task.access_gates:
                _satisfy_condition(player, access_gate)
            self.assertEqual(task_progress_pure(player, task), (False, 0, 0), task.id)

        player, newly = refresh_achievement_diaries_pure(player)
        dormant_ids = {task.id for task in dormant}
        self.assertTrue(dormant_ids.isdisjoint(newly))
        self.assertTrue(
            dormant_ids.isdisjoint(player["achievement_diaries"]["completed_tasks"])
        )

        representative = dormant[0]
        player["achievement_diaries"]["completed_tasks"] = [representative.id]
        view = achievement_cabinet_view_pure(player, search=representative.name)
        row = next(
            row
            for family in view["families"]
            for tier in family["tiers"]
            for row in tier["tasks"]
        )
        self.assertTrue(row["latent"])
        self.assertFalse(row["completed"])
        self.assertFalse(row["staged"])
        self.assertEqual(row["need"], 0)

    def test_fight_pit_gameplay_pays_the_miscellaneous_task_reward(self):
        from ankiscape.logic.tzhaar_fight_pit_logic import enter_tzhaar_fight_pit_pure

        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.source_id == 3018
        )
        player = _fresh()
        before = int(player["inventory"].get("Coins", 0))
        player, ok, info = enter_tzhaar_fight_pit_pure(player)
        self.assertTrue(ok, info)
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertIn(task.id, newly)
        # One Fight Pit entry proves the Miscellaneous task and the Karamja
        # "TzHaar Wars" disjunction at once, so the payout is the coin curve
        # read at this task's own completion ordinal rather than a flat 100.
        self.assertEqual(
            player["inventory"]["Coins"] - before,
            100 * (newly.index(task.id) + 1),
        )

    def test_miscellaneous_reward_grows_with_completion_ordinal(self):
        from ankiscape.logic.tzhaar_fight_pit_logic import enter_tzhaar_fight_pit_pure

        prior = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.source_id == 538
        )
        player = _satisfy(_fresh(), prior)
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertEqual(newly, (prior.id,))
        before = int(player["inventory"].get("Coins", 0))
        completed_before = len(player["achievement_diaries"]["completed_tasks"])
        player, ok, info = enter_tzhaar_fight_pit_pure(player)
        self.assertTrue(ok, info)
        player, newly = refresh_achievement_diaries_pure(player)
        paid = next(
            task_id for task_id in newly if task_id.startswith("miscellaneous_")
        )
        ordinal = completed_before + newly.index(paid) + 1
        self.assertGreater(ordinal, 1)
        self.assertEqual(player["inventory"]["Coins"] - before, 100 * ordinal)

    def test_stale_task_ids_do_not_inflate_the_next_miscellaneous_reward(self):
        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            if family.id == "miscellaneous"
            for tier in family.tiers
            for task in tier.tasks
            if task.coin_reward
        )
        player = _fresh()
        player["achievement_diaries"]["completed_tasks"] = [
            "falador_medium_reach_level_60_fletching",
            "seers_hard_reach_level_65_firemaking",
            "seers_elite_reach_level_80_firemaking",
            task.id,
        ]
        before = int(player["inventory"].get("Coins", 0))

        player = _award_task_coins(player, (task.id,))

        self.assertEqual(
            player["inventory"]["Coins"] - before,
            task.coin_reward,
        )

    def test_burthorpe_course_gameplay_completes_lapping_it_up(self):
        from ankiscape.data.agility_data import AGILITY_TARGETS_BY_ID
        from ankiscape.logic.agility_logic import apply_agility_review_pure

        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.source_id == 574
        )
        player = _fresh()
        player["current_agility"] = "burthorpe_course"
        player["agility_course_state"] = {
            "target": "burthorpe_course",
            "stage": 0,
            "checkpoint": "start",
            "flawless": True,
            "lap_xp_valid": True,
            "requested_item_valid": True,
            "status": "Ready to start",
        }
        self.assertFalse(task_progress_pure(player, task)[0])
        for _stage in AGILITY_TARGETS_BY_ID["burthorpe_course"].stages:
            player, result = apply_agility_review_pure(
                player, (0.99, 0.99, 0.99, 0.99)
            )
        self.assertTrue(result["completed_lap"])
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertIn(task.id, newly)


class ClaimTest(unittest.TestCase):
    def setUp(self):
        self.family = _active_claim_family()
        self._tier_patch = patch.dict(
            "ankiscape.logic.achievement_diary_logic._TIERS_BY_ID",
            {tier.id: (self.family, tier) for tier in self.family.tiers},
        )
        self._tier_patch.start()
        self.addCleanup(self._tier_patch.stop)

    def test_burthorpe_bundle_waits_for_the_full_55_task_pool(self):
        """The authentic set reward exists, but dormant tasks keep it closed."""

        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "burthorpe")
        tier = family.tiers[0]
        player = _complete_tier(_fresh(), tier)
        before = copy.deepcopy(player["inventory"])

        player, ok, info = claim_diary_tier_pure(player, tier.id)

        self.assertFalse(ok)
        self.assertIn("outstanding", info["reason"])
        self.assertEqual(player["inventory"], before)
        self.assertFalse(tier.reward_item)
        self.assertTrue(tier.reward_bundle)
        self.assertEqual(tier.total_tasks, 55)
        self.assertTrue(any(task.dormant for task in tier.tasks))

    def test_a_tier_is_not_claimable_until_every_task_is_done(self):
        player = _fresh()
        tier = self.family.tiers[0]
        _updated, ok, info = claim_diary_tier_pure(player, tier.id)
        self.assertFalse(ok)
        self.assertIn("outstanding", info["reason"])

    def test_completing_a_tier_flips_it_to_ready_to_claim(self):
        family = self.family
        tier = family.tiers[0]
        player = _complete_tier(_fresh(), tier)
        claim_state = tier_claim_state_pure(player, family, tier)
        self.assertEqual(claim_state["status"], "Ready to Claim")
        self.assertTrue(claim_state["ready"])

    def test_cabinet_view_enables_a_completed_synthetic_tier(self):
        family = self.family
        tier = family.tiers[0]
        player = _complete_tier(_fresh(), tier)
        with patch(
            "ankiscape.logic.achievement_diary_logic.ACHIEVEMENT_DIARY_CATALOG",
            (family,),
        ):
            view = achievement_cabinet_view_pure(player, family_filter=family.id)

        tier_row = view["families"][0]["tiers"][0]
        self.assertEqual(tier_row["status"], "Ready to Claim")
        self.assertTrue(tier_row["ready"])

    def test_claiming_grants_the_item_and_creates_a_bank_claim_without_spending_it(self):
        family = self.family
        tier = family.tiers[0]
        player = _complete_tier(_fresh(), tier)
        before = float(player.get("mining_exp", 0))
        claim_id = diary_lamp_claim_id(tier.id)
        self.assertNotIn(claim_id, player["claims"])

        player, ok, info = claim_diary_tier_pure(player, tier.id)

        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"].get("Ardougne cloak 1"), 1)
        self.assertEqual(float(player["mining_exp"]), before)
        self.assertEqual(info["lamp_claim_id"], claim_id)
        self.assertFalse(player["claims"][claim_id]["claimed"])
        row = next(row for row in claim_rows_pure(player, CLAIM_DATA) if row["claim_id"] == claim_id)
        self.assertTrue(row["eligible"])
        self.assertEqual(row["xp_amount"], float(tier.lamp.experience))
        self.assertEqual(row["minimum_level"], tier.lamp.minimum_level)
        self.assertTrue(row["skill_options"])
        self.assertTrue(CLAIM_DATA[claim_id]["source"])

    def test_the_bank_claim_spends_the_lamp_once_on_the_chosen_skill(self):
        family = self.family
        tier = family.tiers[0]
        player = claim_diary_tier_pure(_complete_tier(_fresh(), tier), tier.id)[0]
        claim_id = diary_lamp_claim_id(tier.id)
        before = float(player["mining_exp"])

        player, ok = apply_claim_pure(player, claim_id, CLAIM_DATA, "mining")

        self.assertTrue(ok)
        self.assertEqual(
            float(player["mining_exp"]) - before, float(tier.lamp.experience)
        )
        self.assertTrue(player["claims"][claim_id]["claimed"])
        again, ok = apply_claim_pure(player, claim_id, CLAIM_DATA, "mining")
        self.assertFalse(ok)
        self.assertEqual(again["mining_exp"], player["mining_exp"])

    def test_a_tier_cannot_be_claimed_twice(self):
        family = self.family
        player = _complete_tier(_fresh(), family.tiers[0])
        player = claim_diary_tier_pure(player, family.tiers[0].id)[0]
        _again, ok, info = claim_diary_tier_pure(player, family.tiers[0].id)
        self.assertFalse(ok)
        self.assertIn("already claimed", info["reason"])

    def test_claiming_is_sequential_even_when_later_tasks_are_finished(self):
        family = self.family
        player = _fresh()
        for tier in family.tiers[:2]:
            player = _complete_tier(player, tier)
        _updated, ok, info = claim_diary_tier_pure(player, family.tiers[1].id)
        self.assertFalse(ok)
        self.assertIn("Claim Easy before Medium", info["reason"])

    def test_a_tier_upgrade_replaces_its_predecessor_without_duplicating(self):
        family = self.family
        player = _fresh()
        for tier in family.tiers[:2]:
            player = _complete_tier(player, tier)
        player = claim_diary_tier_pure(player, family.tiers[0].id)[0]
        player, ok, _info = claim_diary_tier_pure(player, family.tiers[1].id)
        self.assertTrue(ok)
        self.assertNotIn("Ardougne cloak 1", player["inventory"])
        self.assertEqual(player["inventory"].get("Ardougne cloak 2"), 1)

    def test_an_upgrade_replaces_the_worn_item_in_its_own_slot(self):
        family = self.family
        player = _fresh()
        for tier in family.tiers[:2]:
            player = _complete_tier(player, tier)
        player = claim_diary_tier_pure(player, family.tiers[0].id)[0]
        inventory, equipment, worn = equip_item_pure(
            "Ardougne cloak 1", player["inventory"], player["equipment"], EQUIPMENT_DATA
        )
        self.assertTrue(worn)
        player["inventory"], player["equipment"] = inventory, equipment
        player = claim_diary_tier_pure(player, family.tiers[1].id)[0]
        self.assertEqual(player["equipment"].get("cape"), "Ardougne cloak 2")
        self.assertFalse(player["inventory"].get("Ardougne cloak 1"))

    def test_no_tier_falls_through_the_empty_roster_claim_path(self):
        view = achievement_cabinet_view_pure(_fresh())
        rows = [tier for family in view["families"] for tier in family["tiers"]]
        for row in rows:
            self.assertGreater(row["total"], 0, row["tier_id"])
            self.assertNotEqual(
                row["status"], "Roster pending harvest", row["tier_id"]
            )

    def test_the_granted_item_can_actually_be_worn(self):
        family = self.family
        player = _complete_tier(_fresh(), family.tiers[0])
        player = claim_diary_tier_pure(player, family.tiers[0].id)[0]
        allowed, reason = can_equip_item_pure(
            "Ardougne cloak 1", EQUIPMENT_DATA, player
        )
        self.assertTrue(allowed, reason)


class MilestoneCapeTest(unittest.TestCase):
    """The design's one named repair: nine craftable, unwearable capes."""

    def test_every_milestone_cape_is_registered_equipment(self):
        for level in range(10, 100, 10):
            self.assertIn(f"Milestone cape ({level})", EQUIPMENT_DATA)

    def test_the_wear_gate_covers_every_trainable_skill(self):
        trainable = {skill.id for skill in trainable_skill_definitions()}
        for level in range(10, 100, 10):
            item = EQUIPMENT_DATA[f"Milestone cape ({level})"]
            self.assertEqual({skill for skill, _ in item.skill_requirements}, trainable)
            self.assertEqual({need for _, need in item.skill_requirements}, {level})

    def test_a_cape_is_refused_while_one_skill_is_short(self):
        player = _fresh()
        for skill in trainable_skill_definitions():
            player[f"{skill.id}_level"] = 10
        player["mining_level"] = 9
        allowed, reason = can_equip_item_pure(
            "Milestone cape (10)", EQUIPMENT_DATA, player
        )
        self.assertFalse(allowed)
        self.assertIn("10", reason)

    def test_a_cape_woven_through_the_real_crafting_path_can_be_worn(self):
        """The whole point of the repair, driven end to end.

        The cape is woven by the real Crafting review handler, not by poking the
        inventory, and then equipped through the real equipment path. Before this
        family, the second half was impossible: the nine capes had no equipment
        row at all.
        """
        from ankiscape.runtime.runtime_actions_production import handle_crafting_answer

        player = _fresh()
        for skill in trainable_skill_definitions():
            player[f"{skill.id}_level"] = 10
        player["inventory"]["Ball of wool"] = 1
        player["current_craft"] = "weave_milestone_cape_10"

        errors: list = []
        ctx = _crafting_context(player, errors)
        self.assertTrue(handle_crafting_answer(ctx), errors)
        self.assertEqual(player["inventory"].get("Milestone cape (10)"), 1)
        self.assertFalse(player["inventory"].get("Ball of wool"))

        allowed, reason = can_equip_item_pure(
            "Milestone cape (10)", EQUIPMENT_DATA, player
        )
        self.assertTrue(allowed, reason)
        inventory, equipment, worn = equip_item_pure(
            "Milestone cape (10)", player["inventory"], player["equipment"], EQUIPMENT_DATA
        )
        self.assertTrue(worn)
        self.assertEqual(equipment.get("cape"), "Milestone cape (10)")
        self.assertFalse(inventory.get("Milestone cape (10)"))

    def test_a_woven_cape_is_refused_while_one_skill_is_short(self):
        """Craftable and wearable are different gates, and both must bite."""
        from ankiscape.runtime.runtime_actions_production import handle_crafting_answer

        player = _fresh()
        player["crafting_level"] = 10
        player["inventory"]["Ball of wool"] = 1
        player["current_craft"] = "weave_milestone_cape_10"

        errors: list = []
        self.assertTrue(handle_crafting_answer(_crafting_context(player, errors)), errors)
        self.assertEqual(player["inventory"].get("Milestone cape (10)"), 1)

        allowed, _reason = can_equip_item_pure(
            "Milestone cape (10)", EQUIPMENT_DATA, player
        )
        self.assertFalse(allowed, "the all-skills wear gate did not bite")


class PinAndCommandTest(unittest.TestCase):
    def test_pinning_moves_the_task_to_the_top_of_its_tier(self):
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        tier = family.tiers[0]
        target = tier.tasks[-1]
        player, ok, _info = pin_diary_task_pure(_fresh(), target.id)
        self.assertTrue(ok)
        view = achievement_cabinet_view_pure(player, family_filter="varrock")
        rows = view["families"][0]["tiers"][0]["tasks"]
        self.assertEqual(rows[0]["task_id"], target.id)
        self.assertTrue(rows[0]["pinned"])

    def test_sanitizer_clears_a_pin_for_a_removed_task(self):
        player = _fresh()
        player["achievement_diaries"][
            "pinned_task"
        ] = "falador_medium_reach_level_60_fletching"

        sanitized = sanitize_achievement_diary_state_pure(player)

        self.assertEqual(sanitized["achievement_diaries"]["pinned_task"], "")

    def test_pinning_the_pinned_task_clears_the_pin(self):
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        target = family.tiers[0].tasks[0]
        player = pin_diary_task_pure(_fresh(), target.id)[0]
        player = pin_diary_task_pure(player, target.id)[0]
        self.assertEqual(player["achievement_diaries"]["pinned_task"], "")

    def test_only_one_task_can_be_pinned(self):
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        first, second = family.tiers[0].tasks[0], family.tiers[0].tasks[1]
        player = pin_diary_task_pure(_fresh(), first.id)[0]
        player = pin_diary_task_pure(player, second.id)[0]
        self.assertEqual(player["achievement_diaries"]["pinned_task"], second.id)

    def test_an_unknown_command_refuses_without_writing(self):
        player = _fresh()
        before = copy.deepcopy(player)
        updated, ok, info = apply_achievement_diary_command_pure(player, "nope", {})
        self.assertFalse(ok)
        self.assertIn("Unknown", info["reason"])
        self.assertEqual(updated, before)

    def test_commands_never_write_through_the_caller_save(self):
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        player = _complete_tier(_fresh(), family.tiers[0])
        frozen = copy.deepcopy(player)
        apply_achievement_diary_command_pure(
            player, "claim_tier", {"tier_id": family.tiers[0].id}
        )
        self.assertEqual(player["inventory"], frozen["inventory"])
        self.assertEqual(player["achievement_diaries"], frozen["achievement_diaries"])


class CabinetViewTest(unittest.TestCase):
    def test_every_task_and_tier_is_visible_from_the_beginning(self):
        view = achievement_cabinet_view_pure(_fresh())
        self.assertEqual(len(view["families"]), len(ACHIEVEMENT_DIARY_CATALOG))
        for family in view["families"]:
            expected = 4 if family["kind"] == "regional" else 1
            self.assertEqual(len(family["tiers"]), expected)

    def test_shipped_catalog_has_no_ready_to_claim_tiers_during_honest_stop(self):
        view = achievement_cabinet_view_pure(_fresh())
        tiers = [
            tier
            for family in view["families"]
            for tier in family["tiers"]
        ]
        self.assertEqual(len(tiers), 34)
        self.assertEqual(
            sum(tier["status"] == "Ready to Claim" for tier in tiers),
            0,
        )

    def test_the_view_never_reports_a_moving_denominator_percentage(self):
        view = achievement_cabinet_view_pure(_fresh())
        self.assertNotIn("percentage", view)
        self.assertEqual(view["total"], diary_totals_pure(_fresh())["total"])

    def test_filters_narrow_the_rendered_rows(self):
        player = _fresh()
        everything = achievement_cabinet_view_pure(player)
        one_family = achievement_cabinet_view_pure(player, family_filter="varrock")
        self.assertEqual(len(one_family["families"]), 1)
        self.assertLess(len(one_family["families"]), len(everything["families"]))

        easy_only = achievement_cabinet_view_pure(player, tier_filter="Easy")
        for family in easy_only["families"]:
            self.assertTrue(all(tier["name"] == "Easy" for tier in family["tiers"]))

    def test_the_search_matches_the_period_task_name(self):
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        needle = family.tiers[0].tasks[0].name
        view = achievement_cabinet_view_pure(
            _fresh(), family_filter="varrock", search=needle
        )
        rows = [row for tier in view["families"][0]["tiers"] for row in tier["tasks"]]
        self.assertTrue(rows)
        self.assertTrue(all(needle.lower() in row["name"].lower() for row in rows))

    def test_the_completion_filter_splits_done_from_outstanding(self):
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        player = _complete_tier(_fresh(), family.tiers[0])
        done = achievement_cabinet_view_pure(
            player, family_filter="varrock", completion_filter="complete"
        )
        rows = done["families"][0]["tiers"][0]["tasks"]
        self.assertTrue(rows)
        self.assertTrue(all(row["completed"] for row in rows))


class TaskmasterTest(unittest.TestCase):
    def test_taskmaster_needs_every_task_in_every_family(self):
        player = _fresh()
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        for tier in family.tiers:
            player = _complete_tier(player, tier)
        self.assertFalse(player["achievement_diaries"]["taskmaster"])

    def test_completing_every_obtainable_row_does_not_bypass_dormant_cutoff_tasks(self):
        player = _fresh()
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                player = _complete_tier(player, tier)
        self.assertFalse(player["achievement_diaries"]["taskmaster"])
        self.assertFalse(achievement_cabinet_view_pure(player)["taskmaster"])
        self.assertEqual(diary_totals_pure(player)["total"], 534)
        obtainable = sum(
            not task.dormant
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
        )
        self.assertEqual(diary_totals_pure(player)["completed"], obtainable)


class MigrationTest(unittest.TestCase):
    def test_the_config_version_advanced_for_this_family(self):
        self.assertGreaterEqual(CURRENT_CONFIG_VERSION, 88)

    def test_an_old_save_gains_the_ledger_and_keeps_its_completions(self):
        legacy = _fresh()
        legacy["config_version"] = 87
        legacy.pop("achievement_diaries")
        legacy["completed_achievements"] = ["First Steps", "Rune Mysteries"]
        legacy["unknown_future_field"] = {"keep": "me"}

        loaded = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)
        self.assertIn("achievement_diaries", loaded)
        self.assertEqual(
            loaded["completed_achievements"], ["First Steps", "Rune Mysteries"]
        )
        self.assertEqual(loaded["unknown_future_field"], {"keep": "me"})

    def test_migration_credits_only_what_the_old_save_can_prove(self):
        legacy = _fresh()
        legacy["config_version"] = 87
        legacy.pop("achievement_diaries")
        loaded = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(loaded["achievement_diaries"]["completed_tasks"], [])

    def test_migration_carries_a_level_the_old_save_really_had(self):
        legacy = _fresh()
        legacy["config_version"] = 87
        legacy.pop("achievement_diaries")
        legacy["mining_level"] = 99
        legacy["crafting_level"] = 99
        loaded = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)
        self.assertTrue(loaded["achievement_diaries"]["completed_tasks"])

    def test_a_current_save_is_not_reseeded_on_reload(self):
        player = _fresh()
        family = _active_claim_family()
        tier = family.tiers[0]
        player = _complete_tier(player, tier)
        with patch.dict(
            "ankiscape.logic.achievement_diary_logic._TIERS_BY_ID",
            {row.id: (family, row) for row in family.tiers},
        ):
            player, ok, info = claim_diary_tier_pure(player, tier.id)
        self.assertTrue(ok, info)
        claimed = list(player["achievement_diaries"]["claimed_tiers"])

        loaded = migrate_loaded_data(
            copy.deepcopy(player), ORE_DATA, ITEM_DEFINITIONS
        )
        self.assertEqual(loaded["achievement_diaries"]["claimed_tiers"], claimed)

    def test_pre_bank_claim_save_retires_lamps_already_paid_as_direct_xp(self):
        player = _fresh()
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        tier = family.tiers[0]
        player = _complete_tier(player, tier)
        player["config_version"] = 106
        player["achievement_diaries"]["claimed_tiers"] = [tier.id]
        player["inventory"][tier.reward_item] = 1
        player["mining_exp"] += float(tier.lamp.experience)
        paid_exp = player["mining_exp"]
        claim_id = diary_lamp_claim_id(tier.id)
        player["claims"].pop(claim_id, None)

        loaded = migrate_loaded_data(player, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(loaded["mining_exp"], paid_exp)
        self.assertTrue(loaded["claims"][claim_id]["claimed"])
        row = next(row for row in claim_rows_pure(loaded, CLAIM_DATA) if row["claim_id"] == claim_id)
        self.assertTrue(row["claimed"])
        self.assertFalse(row["eligible"])

    def test_a_corrupt_ledger_is_repaired_rather_than_fatal(self):
        player = _fresh()
        player["achievement_diaries"] = {"completed_tasks": "nonsense", "claimed_tiers": 7}
        loaded = migrate_loaded_data(player, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(loaded["achievement_diaries"]["completed_tasks"], [])
        self.assertEqual(loaded["achievement_diaries"]["claimed_tiers"], [])


class AssetCoverageTest(unittest.TestCase):
    """Period art, with its provenance recorded, for every reward the tab shows."""

    def _root(self):
        import os

        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_every_manifest_asset_exists_and_is_recorded(self):
        import json
        import os

        from tools.fetch_achievement_diary_assets import asset_manifest

        with open(os.path.join(self._root(), "assets_provenance.json"), encoding="utf-8") as handle:
            provenance = json.load(handle)
        for request, _size in asset_manifest():
            self.assertTrue(os.path.exists(request.output_path), request.output_path)
            relative = os.path.relpath(request.output_path, self._root())
            self.assertIn(relative, provenance)

    def test_no_diary_asset_came_from_after_the_cutoff(self):
        import json
        import os

        with open(os.path.join(self._root(), "assets_provenance.json"), encoding="utf-8") as handle:
            provenance = json.load(handle)
        late = [
            path
            for path, record in provenance.items()
            if "diary_" in path and str(record.get("timestamp", "")) > "2012-11-20"
        ]
        self.assertEqual(late, [], "post-cutoff art is not period art")

    def test_the_manifest_covers_every_tier_reward_item(self):
        from tools.fetch_achievement_diary_assets import DIARY_REWARD_ITEMS

        wanted = {
            tier.reward_item
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            if tier.reward_item
        }
        self.assertEqual(wanted, set(DIARY_REWARD_ITEMS))

    def test_every_named_taskmaster_keeps_its_registered_portrait(self):
        import os

        from tools.fetch_achievement_diary_assets import asset_manifest

        wanted = {
            family.taskmaster: family.taskmaster_chathead_asset_path
            for family in ACHIEVEMENT_DIARY_CATALOG
            if family.taskmaster
        }
        manifest = {
            request.item_name: os.path.relpath(request.output_path, self._root())
            for request, _size in asset_manifest()
            if "chathead" in request.output_path.name
        }
        self.assertEqual(wanted, manifest)
        self.assertEqual(
            [
                family.id
                for family in ACHIEVEMENT_DIARY_CATALOG
                if not family.taskmaster and family.taskmaster_chathead_asset_path
            ],
            [],
        )
        for path in wanted.values():
            self.assertTrue(os.path.exists(os.path.join(self._root(), path)), path)


class TierLookupTest(unittest.TestCase):
    def test_every_tier_id_resolves_back_to_its_family(self):
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                found = diary_tier_by_id_pure(tier.id)
                self.assertIsNotNone(found)
                self.assertEqual(found[0].id, family.id)

    def test_an_unknown_tier_is_refused(self):
        self.assertIsNone(diary_tier_by_id_pure("not_a_tier"))
        self.assertFalse(claim_diary_tier_pure(_fresh(), "not_a_tier")[1])


if __name__ == "__main__":
    unittest.main()
