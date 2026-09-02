"""Canonical ledger compilation and real-runtime diary deed coverage."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.logic.achievement_diary_logic import task_progress_pure
from ankiscape.logic_pure.achievement_diary_events import (
    encode_diary_event_rule_pure,
    record_achievement_diary_event_pure,
)
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    handle_firemaking_answer,
    handle_mining_answer,
    handle_runecrafting_answer,
    handle_thieving_answer,
)
from ankiscape.runtime.runtime_actions_shared import _apply_farming_queue_result
from tools.achievement_diary_ledger import _condition_from_spec, _conditions_from_row
from tools.generate_achievement_diary_data import resolve_condition_key


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
    def test_live_and_dormant_ledger_rows_match_the_generated_catalog(self):
        rows = [
            json.loads(line)
            for line in (
                ROOT
                / "memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl"
            ).read_text(encoding="utf-8").splitlines()
        ]
        tasks = {
            task.id: task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
        }

        self.assertEqual(len(rows), 320)
        self.assertEqual(
            {
                disposition: sum(row["disposition"] == disposition for row in rows)
                for disposition in ("active", "translated", "dormant")
            },
            {"active": 43, "translated": 30, "dormant": 247},
        )
        self.assertEqual(
            [row["task_id"] for row in rows if row["task_id"] not in tasks],
            [],
        )
        for row in rows:
            with self.subTest(task_id=row["task_id"]):
                task = tasks[row["task_id"]]
                self.assertEqual(
                    bool(task.conditions),
                    row["disposition"] in {"active", "translated"},
                )
                self.assertEqual(
                    list(row),
                    [
                        "task_id", "source_id", "family", "current_tier",
                        "original_tier", "designed_trigger", "wiring",
                        "source_citation", "disposition", "future_system", "notes",
                    ],
                )
                self.assertNotIn("\nWiring: ", row["designed_trigger"])
                self.assertEqual(
                    isinstance(row["wiring"], list) and bool(row["wiring"]),
                    row["disposition"] in {"active", "translated"},
                )

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
    @staticmethod
    def _context(player, random_values=()):
        return _runtime_context(player, [], random_values)

    @staticmethod
    def _is_complete(player, task_id):
        return task_id in player.get("achievement_diaries", {}).get(
            "completed_tasks", ()
        )

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
