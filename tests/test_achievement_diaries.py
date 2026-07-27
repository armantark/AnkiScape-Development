"""Achievement Diaries: catalog integrity, progress, claiming, and migration.

Nothing here stubs the system under test. Player state is built from a real
``default_player_data`` and advanced with the real logic entry points, so a
green run means the diary graph actually works rather than that a fake agreed
with itself. The undo and review-dispatch layers live in
``test_achievement_diaries_integration.py``, which loads the add-on package.
"""

from __future__ import annotations

import copy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
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
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.logic.achievement_diary_logic import (
    achievement_cabinet_view_pure,
    apply_achievement_diary_command_pure,
    claim_diary_tier_pure,
    diary_tier_by_id_pure,
    diary_totals_pure,
    pin_diary_task_pure,
    refresh_achievement_diaries_pure,
    task_progress_pure,
)
from ankiscape.logic_pure.logic_pure_equipment import can_equip_item_pure, equip_item_pure
from ankiscape.logic_pure.logic_pure_telemetry import record_achievement_progress_pure


def _fresh():
    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


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


def _satisfy(player, task):
    """Put a real save into the exact durable state each condition reads."""
    for condition in task.conditions:
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
        elif condition.kind == "counter":
            _set_counter(player, condition.key, condition.amount)
        else:  # pragma: no cover - catalog integrity rejects unknown kinds
            raise AssertionError(f"unhandled condition kind {condition.kind}")
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
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
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

    def test_every_task_states_a_requirement_and_cites_its_source(self):
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                for task in tier.tasks:
                    self.assertTrue(task.conditions, task.id)
                    self.assertTrue(task.name.strip(), task.id)
                    self.assertIn("Darkan", task.source, task.id)
                    self.assertGreaterEqual(task.source_id, 0, task.id)

    def test_every_tier_has_a_roster(self):
        empty = [
            tier.id
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            if not tier.tasks
        ]
        self.assertEqual(empty, [])

    def test_regional_tiers_respect_the_twelve_task_curation_budget(self):
        for family in ACHIEVEMENT_DIARY_CATALOG:
            if family.kind != "regional":
                continue
            for tier in family.tiers:
                self.assertLessEqual(len(tier.tasks), 12, tier.id)

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


class TaskProgressTest(unittest.TestCase):
    def test_a_fresh_save_has_credited_nothing_it_cannot_prove(self):
        player = _fresh()
        totals = diary_totals_pure(player)
        self.assertEqual(totals["completed"], 0)
        self.assertGreater(totals["total"], 100)

    def test_meeting_a_task_condition_credits_it(self):
        player = _fresh()
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        task = family.tiers[0].tasks[0]
        self.assertFalse(task_progress_pure(player, task)[0])
        player = _satisfy(player, task)
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertIn(task.id, newly)
        self.assertIn(task.id, player["achievement_diaries"]["completed_tasks"])

    def test_completion_is_sticky_after_the_proving_state_is_lost(self):
        player = _fresh()
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        task = next(
            t
            for tier in family.tiers
            for t in tier.tasks
            if t.conditions[0].kind == "skill_level"
        )
        player = _satisfy(player, task)
        player = refresh_achievement_diaries_pure(player)[0]
        self.assertIn(task.id, player["achievement_diaries"]["completed_tasks"])

        player[f"{task.conditions[0].key}_level"] = 1
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertEqual(newly, ())
        self.assertIn(task.id, player["achievement_diaries"]["completed_tasks"])

    def test_retroactive_credit_arrives_without_a_review(self):
        """Levels and quests receive retroactive credit, per the design."""
        player = _fresh()
        player["mining_level"] = 99
        player["crafting_level"] = 99
        player, newly = refresh_achievement_diaries_pure(player)
        self.assertTrue(newly)

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
    def _varrock(self):
        return next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")

    def test_a_tier_is_not_claimable_until_every_task_is_done(self):
        player = _fresh()
        tier = self._varrock().tiers[0]
        _updated, ok, info = claim_diary_tier_pure(player, tier.id)
        self.assertFalse(ok)
        self.assertIn("outstanding", info["reason"])

    def test_completing_a_tier_flips_it_to_ready_to_claim(self):
        player = _complete_tier(_fresh(), self._varrock().tiers[0])
        view = achievement_cabinet_view_pure(player, family_filter="varrock")
        self.assertEqual(view["families"][0]["tiers"][0]["status"], "Ready to Claim")
        self.assertTrue(view["families"][0]["tiers"][0]["ready"])

    def test_claiming_grants_the_tier_item_and_its_lamp(self):
        family = self._varrock()
        player = _complete_tier(_fresh(), family.tiers[0])
        before = float(player.get("mining_exp", 0))
        player, ok, info = claim_diary_tier_pure(player, family.tiers[0].id, lamp_skill="mining")
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"].get("Varrock armour 1"), 1)
        self.assertEqual(
            float(player["mining_exp"]) - before, float(family.tiers[0].lamp.experience)
        )

    def test_a_tier_cannot_be_claimed_twice(self):
        family = self._varrock()
        player = _complete_tier(_fresh(), family.tiers[0])
        player = claim_diary_tier_pure(player, family.tiers[0].id, lamp_skill="mining")[0]
        _again, ok, info = claim_diary_tier_pure(player, family.tiers[0].id, lamp_skill="mining")
        self.assertFalse(ok)
        self.assertIn("already claimed", info["reason"])

    def test_claiming_is_sequential_even_when_later_tasks_are_finished(self):
        family = self._varrock()
        player = _fresh()
        for tier in family.tiers[:2]:
            player = _complete_tier(player, tier)
        _updated, ok, info = claim_diary_tier_pure(player, family.tiers[1].id, lamp_skill="mining")
        self.assertFalse(ok)
        self.assertIn("Claim Easy before Medium", info["reason"])

    def test_a_tier_upgrade_replaces_its_predecessor_without_duplicating(self):
        family = self._varrock()
        player = _fresh()
        for tier in family.tiers[:2]:
            player = _complete_tier(player, tier)
        player = claim_diary_tier_pure(player, family.tiers[0].id, lamp_skill="mining")[0]
        player, ok, _info = claim_diary_tier_pure(
            player, family.tiers[1].id, lamp_skill="mining"
        )
        self.assertTrue(ok)
        self.assertNotIn("Varrock armour 1", player["inventory"])
        self.assertEqual(player["inventory"].get("Varrock armour 2"), 1)

    def test_an_upgrade_replaces_the_worn_item_in_its_own_slot(self):
        family = self._varrock()
        player = _fresh()
        for tier in family.tiers[:2]:
            player = _complete_tier(player, tier)
        player = claim_diary_tier_pure(player, family.tiers[0].id, lamp_skill="mining")[0]
        inventory, equipment, worn = equip_item_pure(
            "Varrock armour 1", player["inventory"], player["equipment"], EQUIPMENT_DATA
        )
        self.assertTrue(worn)
        player["inventory"], player["equipment"] = inventory, equipment
        player = claim_diary_tier_pure(player, family.tiers[1].id, lamp_skill="mining")[0]
        self.assertEqual(player["equipment"].get("body"), "Varrock armour 2")
        self.assertFalse(player["inventory"].get("Varrock armour 1"))

    def test_no_tier_falls_through_the_empty_roster_claim_path(self):
        view = achievement_cabinet_view_pure(_fresh())
        rows = [tier for family in view["families"] for tier in family["tiers"]]
        for row in rows:
            self.assertGreater(row["total"], 0, row["tier_id"])
            self.assertNotEqual(
                row["status"], "Roster pending harvest", row["tier_id"]
            )

    def test_the_granted_item_can_actually_be_worn(self):
        family = self._varrock()
        player = _complete_tier(_fresh(), family.tiers[0])
        player = claim_diary_tier_pure(player, family.tiers[0].id, lamp_skill="mining")[0]
        allowed, reason = can_equip_item_pure(
            "Varrock armour 1", EQUIPMENT_DATA, player
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
            player, "claim_tier", {"tier_id": family.tiers[0].id, "lamp_skill": "mining"}
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

    def test_completing_the_whole_catalog_awards_taskmaster(self):
        player = _fresh()
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                player = _complete_tier(player, tier)
        self.assertTrue(player["achievement_diaries"]["taskmaster"])
        self.assertTrue(achievement_cabinet_view_pure(player)["taskmaster"])


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
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "varrock")
        player = _complete_tier(player, family.tiers[0])
        player = claim_diary_tier_pure(player, family.tiers[0].id, lamp_skill="mining")[0]
        claimed = list(player["achievement_diaries"]["claimed_tiers"])

        loaded = migrate_loaded_data(
            copy.deepcopy(player), ORE_DATA, ITEM_DEFINITIONS
        )
        self.assertEqual(loaded["achievement_diaries"]["claimed_tiers"], claimed)

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
