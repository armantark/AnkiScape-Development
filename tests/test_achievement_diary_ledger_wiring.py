"""Canonical ledger compilation and real-runtime diary deed coverage."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_UNLOCK_RULES,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.data.agility_data import AGILITY_TARGETS_BY_ID
from ankiscape.logic.achievement_diary_logic import (
    refresh_achievement_diaries_pure,
    task_progress_pure,
)
from ankiscape.logic.shop_logic import (
    SHOP_DIARY_TRANSACTION_KEYS,
    apply_shop_service_pure,
    rollback_shop_event_pure,
    shop_diary_transaction_counter_key_pure,
)
from ankiscape.logic.great_orb_project_logic import (
    use_great_orb_project_teleport_tablet_pure,
)
from ankiscape.logic.managing_miscellania_logic import (
    default_managing_miscellania_state_pure,
)
from ankiscape.logic.court_cases_logic import apply_court_cases_command_pure
from ankiscape.logic.shades_of_mortton_logic import enter_shades_of_mortton_pure
from ankiscape.logic.temple_trekking_logic import apply_temple_trekking_command_pure
from ankiscape.logic_pure.achievement_diary_events import (
    encode_diary_event_rule_pure,
    record_achievement_diary_event_pure,
)
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    _handle_livid_farm_answer,
    handle_agility_answer,
    handle_castle_wars_answer,
    handle_combat_answer,
    handle_firemaking_answer,
    handle_mining_answer,
    handle_runecrafting_answer,
    handle_shades_of_mortton_answer,
    handle_thieving_answer,
    run_answer_with_carried_overlay,
)
from ankiscape.runtime.runtime_actions_shared import _apply_farming_queue_result
from tools.achievement_diary_ledger import (
    _DIRECT_EVENT_EMITTERS,
    _LIVE_DISPOSITIONS,
    _condition_from_spec,
    _conditions_from_row,
    _validate_completion_seams,
)
from tools.generate_achievement_diary_data import _task_block, resolve_condition_key


ROOT = Path(__file__).resolve().parents[1]


def _runtime_context(player, errors, random_values=()):
    from ankiscape.core.logic import check_achievements

    rolls = iter(random_values)

    def award(exp_key, amount):
        player[exp_key] = float(player.get(exp_key, 0.0) or 0.0) + float(amount)
        return amount

    return RuntimeActionContext(
        player_data=player, random_random=lambda: next(rolls, 0.5),
        show_error_message=lambda title, message: errors.append((title, message)),
        deactivate_current_skill=lambda _reason=None: None, award_skill_exp=award,
        award_hidden_skill_exp=lambda *_args: None, level_up_check=lambda *_args: None,
        check_achievements=check_achievements, save_player_data=lambda: None,
        refresh_skill_availability=lambda: None, show_exp=lambda _amount: None,
        show_activity_gain=lambda _message: None, implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class CurationLedgerWiringTest(unittest.TestCase):
    @staticmethod
    def _ledger_rows():
        return [
            json.loads(line)
            for line in (
                ROOT
                / "memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl"
            ).read_text(encoding="utf-8").splitlines()
        ]

    def test_ledger_census_and_catalog_ids_are_exact(self):
        rows = self._ledger_rows()
        task_ids = {
            task.id
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
        }
        self.assertEqual(len(rows), 320)
        self.assertEqual(
            {
                disposition: sum(row["disposition"] == disposition for row in rows)
                for disposition in (
                    "active", "translated", "swapped", "invented", "dormant"
                )
            },
            {
                "active": 42, "translated": 125, "swapped": 0,
                "invented": 37, "dormant": 116,
            },
        )
        self.assertEqual([row["task_id"] for row in rows if row["task_id"] not in task_ids], [])

    def test_ledger_row_schema_and_wiring_match_disposition(self):
        for row in self._ledger_rows():
            with self.subTest(task_id=row["task_id"]):
                expected_fields = [
                    "task_id", "source_id", "family", "current_tier",
                    "original_tier", "designed_trigger", "wiring",
                    "source_citation", "disposition", "future_system", "notes",
                ]
                if row["disposition"] in {"translated", "invented"}:
                    expected_fields += ["designed_name", "designed_description"]
                    self.assertTrue(row["designed_name"])
                    self.assertTrue(row["designed_description"])
                self.assertEqual(list(row), expected_fields)
                self.assertNotIn("\nWiring: ", row["designed_trigger"])
                self.assertEqual(
                    isinstance(row["wiring"], list) and bool(row["wiring"]),
                    row["disposition"] in _LIVE_DISPOSITIONS,
                )

    def test_checked_catalog_never_activates_a_dormant_ledger_row(self):
        rows = {row["task_id"]: row for row in self._ledger_rows()}
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                for task in tier.tasks:
                    if task.id in rows and task.conditions:
                        self.assertIn(rows[task.id]["disposition"], _LIVE_DISPOSITIONS)

    def test_single_action_threshold_does_not_read_cumulative_output(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.id == "falador_hard_mass_production"
        )
        for amount in (139, 1):
            record_achievement_diary_event_pure(
                player,
                {
                    "type": "action",
                    "skill_id": "runecrafting",
                    "action_id": "craft_mind_runes",
                    "success": True,
                    "outputs": {"Mind rune": amount},
                    "kills": 0,
                },
            )
        self.assertEqual(task_progress_pure(player, task), (False, 0, 1))

        record_achievement_diary_event_pure(
            player,
            {
                "type": "action",
                "skill_id": "runecrafting",
                "action_id": "craft_mind_runes",
                "success": True,
                "outputs": {"Mind rune": 140},
                "kills": 0,
            },
        )
        self.assertEqual(task_progress_pure(player, task), (True, 1, 1))

    def test_ordered_event_condition_advances_only_in_order(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.id == "varrock_easy_pot_stop"
        )
        fire = {
            "type": "action",
            "skill_id": "crafting",
            "action_id": "fire_bowl",
            "success": True,
            "outputs": {},
            "kills": 0,
        }
        form = {**fire, "action_id": "form_bowl_unfired"}

        record_achievement_diary_event_pure(player, fire)
        self.assertFalse(task_progress_pure(player, task)[0])
        record_achievement_diary_event_pure(player, form)
        self.assertFalse(task_progress_pure(player, task)[0])
        record_achievement_diary_event_pure(player, fire)
        self.assertTrue(task_progress_pure(player, task)[0])

    def test_event_key_resolver_rejects_an_unwritten_action(self):
        key = encode_diary_event_rule_pure(
            {
                "match": {
                    "eq": {
                        "type": "action",
                        "skill_id": "mining",
                        "action_id": "no_such_ore",
                        "success": True,
                    }
                }
            }
        )
        self.assertIn("never recorded", resolve_condition_key("counter", key))

    def test_event_key_resolver_rejects_an_unsupported_direct_event_value(self):
        key = encode_diary_event_rule_pure(
            {
                "match": {
                    "eq": {
                        "type": "temple_trekking_command",
                        "action_id": "no_such_command",
                    }
                }
            }
        )
        self.assertIn(
            "unsupported temple_trekking_command action_id",
            resolve_condition_key("counter", key),
        )

    def test_event_key_resolver_rejects_a_direct_type_without_an_emitter(self):
        key = encode_diary_event_rule_pure(
            {
                "match": {
                    "eq": {
                        "type": "temple_trekking_command",
                        "action_id": "prepare_pouch",
                    }
                }
            }
        )
        with patch.dict(_DIRECT_EVENT_EMITTERS, {}, clear=True):
            self.assertIn(
                "unsupported direct-event type 'temple_trekking_command'",
                resolve_condition_key("counter", key),
            )

    def test_generator_rejects_an_unknown_ledger_condition_kind(self):
        with self.assertRaisesRegex(SystemExit, "unsupported condition kind"):
            _condition_from_spec(
                {"kind": "typo", "label": "Never valid"},
                "synthetic_task",
            )

    def test_live_row_without_wiring_fails_closed(self):
        with self.assertRaisesRegex(SystemExit, "no valid wiring clause"):
            _conditions_from_row(
                {
                    "task_id": "synthetic_live",
                    "disposition": "active",
                    "designed_trigger": "Reviewed prose only",
                    "wiring": None,
                }
            )

    def test_dormant_row_with_wiring_is_rejected(self):
        with self.assertRaisesRegex(SystemExit, "carries wiring"):
            _conditions_from_row(
                {
                    "task_id": "synthetic_dormant",
                    "disposition": "dormant",
                    "designed_trigger": "Reviewed prose only",
                    "wiring": [{"kind": "counter"}],
                }
            )

    def test_generator_emits_the_designed_invented_task_text(self):
        block = _task_block(
            "ardougne",
            "easy",
            {"id": 0, "name": "Boot Camp", "description": "Source deed"},
            "synthetic source",
            conditions_override=(),
        )
        self.assertIn("'Ball Control'", block)
        self.assertIn("'Complete a Gnome Ball action.'", block)
        self.assertNotIn("'Boot Camp'", block)
        self.assertNotIn("'Source deed'", block)

    def test_invented_row_with_wiring_compiles_as_live(self):
        self.assertEqual(
            _conditions_from_row(
                {
                    "task_id": "synthetic_invented",
                    "disposition": "invented",
                    "wiring": [
                        {
                            "kind": "counter",
                            "key": "deliberate_action",
                            "amount": 2,
                            "label": "Do the deliberate thing twice",
                        }
                    ],
                }
            ),
            [("counter", "deliberate_action", 2, "Do the deliberate thing twice")],
        )

    def test_duplicate_completion_seam_names_both_tasks(self):
        first = {
            "task_id": "first_task",
            "disposition": "translated",
            "wiring": [{
                "kind": "event",
                "label": "First label",
                "rule": {"match": {"eq": {
                    "type": "action", "action_id": "same_action",
                    "success": True,
                }}},
            }],
        }
        duplicate = {
            "task_id": "second_task",
            "disposition": "invented",
            "wiring": [{
                "kind": "event",
                "label": "Different label",
                "rule": {"match": {"eq": {
                    "success": True, "action_id": "same_action",
                    "type": "action",
                }}},
            }],
        }
        with self.assertRaisesRegex(
            SystemExit, "first_task.*second_task.*share completion seams"
        ):
            _validate_completion_seams({
                "first_task": first,
                "second_task": duplicate,
            })

        duplicate["wiring"][0]["rule"]["match"]["eq"]["action_id"] = "other_action"
        _validate_completion_seams({
            "first_task": first,
            "second_task": duplicate,
        })

    def test_gop_tablet_records_the_durable_altar_event(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"]["Air altar teleport"] = 1
        rule = {
            "match": {
                "eq": {
                    "type": "great_orb_project_teleport",
                    "altar_id": "air",
                }
            }
        }
        key = encode_diary_event_rule_pure(rule)
        with patch(
            "ankiscape.logic_pure.achievement_diary_events._event_conditions_by_type",
            return_value={
                "great_orb_project_teleport": (("synthetic", key, 1, rule),)
            },
        ):
            updated, ok, info = use_great_orb_project_teleport_tablet_pure(
                player, "Air altar teleport", EQUIPMENT_DATA, QUEST_UNLOCK_RULES
            )
        self.assertTrue(ok, info)
        token = key.split(".")[-1]
        self.assertEqual(
            updated["achievement_diaries"]["event_counts"][token],
            1,
        )

    def test_shop_diary_mapping_matches_the_live_ledger_exactly(self):
        rows = [
            json.loads(line)
            for line in (
                ROOT
                / "memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl"
            ).read_text(encoding="utf-8").splitlines()
        ]
        used = set()
        for row in rows:
            for spec in row.get("wiring") or ():
                if spec.get("kind") != "shop_transaction":
                    continue
                transaction_type, shop_id, detail_id = spec["key"].split("|", 2)
                counter_key = shop_diary_transaction_counter_key_pure(
                    transaction_type, shop_id, detail_id
                )
                self.assertTrue(counter_key, row["task_id"])
                used.add(counter_key)
        pre_ledger = {
            "aemads_vial_of_water",
            "lumbridge_raw_shrimps_sale",
            "candle_maker_candle",
            "benny_varrock_herald",
            "waynes_black_chainbody",
        }
        self.assertEqual(SHOP_DIARY_TRANSACTION_KEYS, pre_ledger | used)
        self.assertEqual(len(SHOP_DIARY_TRANSACTION_KEYS), 54)

    def test_shop_service_uses_its_service_id_for_durable_diary_credit(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"].update({"Coins": 5, "Yak-hide": 1})
        player["quests"] = {
            "the_fremennik_isles": {"started": True, "progress": 5}
        }

        updated, result = apply_shop_service_pure(
            player, "thakkrad_cure_yak_hide", 1
        )

        self.assertTrue(result["allowed"], result)
        event = updated["shop_events"][-1]
        self.assertEqual(
            (event["type"], event["shop_id"], event["row_id"], event["service_id"]),
            ("service", "", None, "thakkrad_cure_yak_hide"),
        )
        self.assertEqual(
            updated["shop_transaction_counts"],
            {"fremennik_medium_cool_story_bro": 1},
        )
        restored, undo = rollback_shop_event_pure(updated, result["event_id"])
        self.assertTrue(undo["allowed"], undo)
        self.assertEqual(restored["shop_transaction_counts"], {})

    def test_skipped_farming_result_cannot_complete_a_chop_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.id == "falador_elite_i_swear_i_heard_it_scream"
        )
        old_levels = {
            skill: player[f"{skill.lower()}_level"]
            for skill in ("Farming", "Woodcutting", "Agility", "Magic", "Slayer")
        }
        _apply_farming_queue_result(
            _runtime_context(player, []),
            old_levels,
            copy.deepcopy(player),
            True,
            {
                "status": "skipped",
                "kind": "chop",
                "patch_id": "falador_tree",
                "crop_id": "magic",
                "outputs": {},
            },
        )
        self.assertFalse(task_progress_pure(player, task)[0])

    def test_farming_output_replacement_cannot_credit_the_removed_crop(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.id == "ardougne_medium_what_a_melon"
        )
        old_levels = {
            skill: player[f"{skill.lower()}_level"]
            for skill in ("Farming", "Woodcutting", "Agility", "Magic", "Slayer")
        }
        updated = copy.deepcopy(player)
        info = {
            "status": "executed",
            "kind": "harvest",
            "crop_id": "watermelon",
            "outputs": {"Watermelon": 1},
            "farming_xp": 1.0,
        }
        with patch(
            "ankiscape.runtime.runtime_actions_shared.apply_shattered_heart_skilling_hook_pure",
            return_value=(
                copy.deepcopy(updated),
                True,
                {"replaced_outputs": {"Watermelon": 1}},
            ),
        ):
            _apply_farming_queue_result(
                _runtime_context(player, []),
                old_levels,
                updated,
                True,
                info,
            )
        self.assertFalse(task_progress_pure(player, task)[0])

    def test_fire_cape_wiring_uses_the_owner_selected_equipped_candidate(self):
        row = next(
            json.loads(line)
            for line in (
                ROOT / "memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl"
            ).read_text(encoding="utf-8").splitlines()
            if '"task_id": "karamja_elite_the_power_of_lava"' in line
        )
        self.assertEqual(
            row["wiring"],
            [
                {
                    "kind": "state_equals",
                    "key": "activity_session.active_id",
                    "amount": 1,
                    "label": "Be in a TzHaar activity",
                    "expected": "tzhaar_fight_pit",
                },
                {
                    "kind": "equipped_item",
                    "key": "cape|Fire cape",
                    "amount": 1,
                    "label": "Equip a Fire cape",
                },
            ],
        )


class CurationLedgerRuntimeExecutionTest(unittest.TestCase):
    def setUp(self):
        popups = patch("ankiscape.core.logic._popups_enabled", return_value=False)
        popups.start()
        self.addCleanup(popups.stop)

    @staticmethod
    def _context(player, random_values=()):
        return _runtime_context(player, [], random_values)

    @staticmethod
    def _is_complete(player, task_id):
        return task_id in player.get("achievement_diaries", {}).get(
            "completed_tasks", ()
        )

    @staticmethod
    def _complete_pure_result(player):
        updated, _newly = refresh_achievement_diaries_pure(player)
        return updated

    def test_real_pouch_preparation_completes_bloom_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["nature_spirit"].update(
            {"started": True, "progress": 99, "completed": True}
        )
        player["inventory"].update({"Silver sickle (b)": 1, "Druid pouch": 1})
        task_id = "morytania_easy_blooming_marvellous"
        self.assertFalse(self._is_complete(player, task_id))

        player, ok, info = apply_temple_trekking_command_pure(
            player, "prepare_pouch"
        )
        self.assertTrue(ok, info)
        player = self._complete_pure_result(player)

        self.assertTrue(self._is_complete(player, task_id))

    def test_real_court_cases_entry_with_derived_piety_completes_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["kings_ransom"].update(
            {"started": True, "progress": 99, "completed": True}
        )
        player["knight_waves"] = {"completed": True}
        player.update(
            {
                "attack_level": 70,
                "defense_level": 70,
                "prayer_level": 70,
                "combat_prayer_book": "standard",
                "combat_prayers_enabled": True,
                "combat_selected_prayers": ["piety"],
            }
        )
        task_id = "seers_hard_prayer_of_attorney"
        self.assertFalse(self._is_complete(player, task_id))

        player, ok, info = apply_court_cases_command_pure(
            player, "enter", {"role": "prosecution", "automation_mode": "casual"}
        )
        self.assertTrue(ok, info)
        player = self._complete_pure_result(player)

        self.assertTrue(self._is_complete(player, task_id))

    @unittest.skip(
        "Great Orb item 13 is held in memory-bank/pending/gop-achievement-check-2026-09-01.patch pending the owner's ruling."
    )
    def test_real_blood_altar_tablet_checks_diary_before_next_teleport(self):
        original_modules = dict(sys.modules)
        try:
            from tests.test_great_orb_project import (
                _DummyCol,
                _DummyMW,
                _install_runtime_fakes,
                _load_addon_as_package,
            )

            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_great_orb_diary_direct")
            storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
            package_constants = sys.modules[f"{addon.__name__}.core.constants"]
            captured = {}
            addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
            addon.mw = _DummyMW(_DummyCol())
            addon.save_player_data = lambda: None
            addon.update_review_hud = lambda *_args: None
            addon._refresh_skill_availability = lambda: None
            addon._show_activity_gain = lambda *_args: None
            addon.current_skill = "Bankstanding"
            player = storage.default_player_data(
                package_constants.ORE_DATA, package_constants.ITEM_DEFINITIONS
            )
            player["runecrafting_level"] = 50
            player["quests"]["legacy_of_seergaze"].update(
                {"started": True, "progress": 99, "completed": True}
            )
            player["inventory"]["Blood altar teleport"] = 1
            addon.player_data = player

            addon._on_main_menu()
            result = captured["on_use_great_orb_project_teleport_tablet"](
                "Blood altar teleport"
            )

            self.assertTrue(result["ok"], result)
            self.assertIn(
                "morytania_hard_runecraft_carrier",
                addon.player_data["achievement_diaries"]["completed_tasks"],
            )
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_real_livid_farm_review_does_not_emit_shades_event(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["lunar_diplomacy"].update(
            {"started": True, "progress": 99, "completed": True}
        )
        player.update(
            {
                "magic_level": 99,
                "agility_level": 99,
                "crafting_level": 99,
                "farming_level": 99,
                "construction_level": 99,
            }
        )
        player["inventory"].update(
            {
                "Astral rune": 1_000,
                "Nature rune": 1_000,
                "Law rune": 1_000,
                "Earth rune": 1_000,
                "Water rune": 1_000,
            }
        )

        with patch(
            "ankiscape.runtime.runtime_actions_activities_training."
            "record_direct_diary_event_pure"
        ) as record_event:
            self.assertTrue(
                _handle_livid_farm_answer(
                    self._context(player, random_values=(0.5,) * 64)
                )
            )

        self.assertNotIn(
            "shades_of_mortton_review",
            [call.args[2] for call in record_event.call_args_list],
        )

    def test_real_castle_wars_catapult_review_completes_artillery_deed(self):
        from ankiscape.logic.castle_wars_logic import enter_castle_wars_pure

        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["catapult_construction"].update(
            {"started": True, "progress": 99, "completed": True}
        )
        player.update(
            {
                "current_utility": "castle_wars",
                "construction_level": 99,
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
                "ranged_level": 99,
                "magic_level": 99,
                "prayer_level": 99,
            }
        )
        player, ok, info = enter_castle_wars_pure(
            player,
            {"automation_mode": "advanced", "duty": "catapult"},
        )
        self.assertTrue(ok, info)
        task_id = "ardougne_hard_artillery_strike"
        self.assertFalse(self._is_complete(player, task_id))

        self.assertTrue(
            handle_castle_wars_answer(
                self._context(player, random_values=(0.9,) * 32)
            )
        )

        self.assertTrue(self._is_complete(player, task_id))

    def test_real_bank_run_with_non_coin_item_completes_bank_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update(
            {
                "current_ore": "copper_ore",
                "carried_inventory": {"copper_ore": {"Coal": 28}},
                "carried_churn": {"copper_ore": 28},
            }
        )
        player["inventory"]["Coal"] = 28
        task_id = "burthorpe_period_bank_on_it"
        self.assertFalse(self._is_complete(player, task_id))
        acted = []

        self.assertTrue(
            run_answer_with_carried_overlay(
                self._context(player, random_values=(0.0,) * 64),
                "mining",
                lambda _ctx: acted.append(True) or True,
            )
        )

        self.assertEqual(acted, [])
        self.assertTrue(self._is_complete(player, task_id))

    def test_real_shades_review_with_flamtaer_hammer_completes_repair_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["shades_of_mortton"].update(
            {"started": True, "progress": 99, "completed": True}
        )
        player["inventory"].update(
            {
                "Flamtaer hammer": 1,
                "Timber beam": 1,
                "Limestone brick": 1,
                "Swamp paste": 5,
            }
        )
        player, ok, info = enter_shades_of_mortton_pure(player)
        self.assertTrue(ok, info)
        task_id = "morytania_medium_flamtaer_will_get_you_everywhere"
        self.assertFalse(self._is_complete(player, task_id))

        self.assertTrue(
            handle_shades_of_mortton_answer(
                self._context(player, random_values=(0.0,) * 8)
            )
        )

        self.assertTrue(self._is_complete(player, task_id))

    def test_real_miscellania_collection_completes_mahogany_deed(self):
        original_modules = dict(sys.modules)
        try:
            from tests.test_undo_seam_miscellania import (
                _DummyMW,
                _FakeCollection,
                _load_addon,
            )

            addon = _load_addon()
            addon.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
            addon.player_data["quests"]["throne_of_miscellania"].update(
                {"started": True, "progress": 99, "completed": True}
            )
            addon.player_data.update(default_managing_miscellania_state_pure())
            state = addon.player_data["managing_miscellania"]
            state["production_credit"] = 2_000_000
            state["allocations"]["hardwood"] = 10
            state["variants"]["hardwood"] = "mahogany"
            addon.save_player_data = lambda: None
            addon.mw = _DummyMW(_FakeCollection())
            addon.update_review_hud = lambda *_args: None
            addon._refresh_skill_availability = lambda: None
            captured = {}
            addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
            addon._on_main_menu(initial_skill="Activities")
            task_id = "fremennik_hard_a_periodic_table"
            self.assertFalse(self._is_complete(addon.player_data, task_id))

            result = captured["on_managing_miscellania_command"]("collect", {})

            self.assertTrue(result["ok"], result)
            self.assertGreater(
                addon.player_data["inventory"].get("Mahogany logs", 0), 0
            )
            self.assertTrue(self._is_complete(addon.player_data, task_id))
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_real_skeleton_kill_with_active_soul_split_completes_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["the_temple_at_senntisten"].update(
            {"started": True, "progress": 99, "completed": True}
        )
        player.update(
            {
                "current_combat_target": "skeleton_level_21",
                "strength_level": 99,
                "defense_level": 99,
                "prayer_level": 99,
                "constitution_level": 99,
                "combat_lifepoints": 990,
                "combat_prayer_book": "curses",
                "combat_prayers_enabled": True,
                "combat_prayer_uptime": "100",
                "combat_prayer_points": 9900,
                "combat_selected_prayers": ["soul_split"],
                "combat_encounter": {
                    "target_id": "skeleton_level_21",
                    "enemy_lifepoints": 1,
                },
            }
        )
        task_id = "varrock_elite_splitting_headache"
        self.assertFalse(self._is_complete(player, task_id))

        self.assertTrue(
            handle_combat_answer(
                self._context(player, random_values=(0.0,) * 128)
            )
        )

        self.assertTrue(self._is_complete(player, task_id))

    def test_real_advanced_barbarian_lap_completes_agile_top_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        target = AGILITY_TARGETS_BY_ID["barbarian_advanced"]
        player.update(
            {
                "current_agility": target.id,
                "agility_level": 99,
                "bar_crawl_completed": True,
                "equipment": {"body": "Agile top"},
                "agility_course_state": {
                    "target": target.id,
                    "stage": len(target.stages) - 1,
                    "checkpoint": "start",
                    "flawless": True,
                    "lap_xp_valid": True,
                    "requested_item_valid": True,
                    "status": "",
                },
            }
        )
        task_id = "fremennik_elite_limber_lumber_jumper"
        self.assertFalse(self._is_complete(player, task_id))

        self.assertTrue(
            handle_agility_answer(
                self._context(player, random_values=(0.99, 0.0, 0.99, 0.99))
            )
        )

        self.assertTrue(self._is_complete(player, task_id))

    def test_real_answer_context_defers_agility_deed_dialog_until_return(self):
        original_modules = dict(sys.modules)
        try:
            from tests.test_integration_smoke import (
                _install_runtime_fakes,
                _load_addon_as_package,
            )

            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_diary_dialog_deferral")
            package = addon.__name__
            storage = sys.modules[f"{package}.core.storage_pure"]
            constants = sys.modules[f"{package}.core.constants"]
            agility_data = sys.modules[f"{package}.data.agility_data"]
            runtime_actions = sys.modules[f"{package}.runtime.runtime_actions"]
            logic = sys.modules[f"{package}.core.logic"]
            target = agility_data.AGILITY_TARGETS_BY_ID["barbarian_advanced"]
            addon.player_data = storage.default_player_data(
                constants.ORE_DATA, constants.ITEM_DEFINITIONS
            )
            addon.save_player_data = lambda: None
            addon._refresh_skill_availability = lambda: None
            addon._show_activity_gain = lambda _message: None
            addon.player_data.update(
                {
                    "current_agility": target.id,
                    "agility_level": 99,
                    "bar_crawl_completed": True,
                    "equipment": {"body": "Agile top"},
                    "agility_course_state": {
                        "target": target.id,
                        "stage": len(target.stages) - 1,
                        "checkpoint": "start",
                        "flawless": True,
                        "lap_xp_valid": True,
                        "requested_item_valid": True,
                        "status": "",
                    },
                }
            )
            dialogs = []
            inside_answer = True
            drain_calls = 0
            real_drain = addon._show_pending_review_dialogs

            def _show_dialog(title, data):
                if inside_answer:
                    self.fail(
                        "show_achievement_dialog reached QDialog.exec inside "
                        "handle_agility_answer"
                    )
                dialogs.append((title, data))

            def _answer_returns(_reviewer, _ease):
                nonlocal inside_answer
                inside_answer = False
                return "answered"

            def _drain_pending_dialogs():
                nonlocal drain_calls
                drain_calls += 1
                real_drain()

            addon.current_skill = "Agility"
            addon.card_turned = True
            addon.answer_shown = True
            addon.exp_awarded = False
            with (
                patch.object(logic, "_popups_enabled", return_value=True),
                patch.object(logic, "show_achievement_dialog", _show_dialog),
                patch.object(
                    addon,
                    "_show_pending_review_dialogs",
                    _drain_pending_dialogs,
                ),
                patch.object(addon.random, "random", return_value=0.99),
            ):
                result = addon.on_answer_card(object(), 4, _answer_returns)

            self.assertEqual(result, "answered")
            self.assertEqual(
                [title for title, _data in dialogs].count(
                    "Limber Lumber Jumper"
                ),
                1,
            )
            self.assertEqual(drain_calls, 1)
            self.assertEqual(addon._PENDING_REVIEW_DIALOGS, [])
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_real_mining_review_completes_translated_iron_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update({"current_ore": "iron", "mining_level": 99})
        task_id = "lumbridge_easy_iron_on"
        self.assertFalse(self._is_complete(player, task_id))

        self.assertTrue(
            handle_mining_answer(
                self._context(
                    player, random_values=(0.0, 0.99, 0.99, 0.99, 0.99)
                )
            )
        )

        self.assertEqual(player["inventory"]["Iron ore"], 1)
        self.assertTrue(self._is_complete(player, task_id))

    def test_real_firemaking_review_completes_translated_campfire_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update({"current_firemaking": "logs", "firemaking_level": 99})
        player["inventory"]["Logs"] = 1
        task_id = "lumbridge_easy_camping_trip"
        self.assertFalse(self._is_complete(player, task_id))

        self.assertTrue(
            handle_firemaking_answer(
                self._context(player, random_values=(0.0,) * 8)
            )
        )

        self.assertTrue(self._is_complete(player, task_id))

    def test_real_failed_guard_attempt_completes_active_attempt_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update(
            {
                "current_thieving": "pickpocket_guard",
                "thieving_level": 40,
            }
        )
        task_id = "ardougne_easy_yoink"
        self.assertFalse(self._is_complete(player, task_id))

        self.assertFalse(
            handle_thieving_answer(
                self._context(player, random_values=(0.99,) * 8)
            )
        )

        self.assertTrue(self._is_complete(player, task_id))

    def test_real_runecrafting_review_completes_active_batch_deed(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update(
            {
                "current_runecrafting": "craft_mind_runes",
                "runecrafting_level": 99,
            }
        )
        player["inventory"]["Rune essence"] = 18
        player["inventory"]["Mind talisman"] = 1
        player["quests"]["rune_mysteries"].update(
            {"started": True, "progress": 6, "completed": True}
        )
        task_id = "falador_hard_mass_production"
        self.assertFalse(self._is_complete(player, task_id))

        self.assertTrue(
            handle_runecrafting_answer(
                self._context(player, random_values=(0.0,) * 64)
            )
        )

        self.assertGreaterEqual(
            player["action_telemetry"]["actions"][
                "runecrafting:craft_mind_runes"
            ]["outputs"]["Mind rune"],
            140,
        )
        self.assertTrue(self._is_complete(player, task_id))


if __name__ == "__main__":
    unittest.main()
