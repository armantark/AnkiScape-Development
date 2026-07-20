import os
import unittest
from unittest.mock import patch

import runtime_actions
from constants import (
    ITEM_DEFINITIONS,
    QUEST_UNLOCK_RULES,
    TREE_DATA,
    TREE_IMAGES,
    WOODCUTTING_AXE_DATA,
)
from item_registry import item_definitions_by_storage_key
from logic_pure import (
    apply_woodcutting_processing_action_pure,
    target_unlock_locked_reasons_pure,
    woodcutting_target_locked_reasons_pure,
)
from runtime_actions import (
    RuntimeActionContext,
    handle_woodcutting_answer,
    run_answer_with_carried_overlay,
)
from target_metadata import woodcutting_target_rows


TARGET_ID = "split_arctic_pine_logs"


def _player_data() -> dict:
    return {
        "inventory": {"Arctic pine logs": 2},
        "toolbelt": {"woodcutting": []},
        "woodcutting_level": 54,
        "woodcutting_exp": 0.0,
        "current_tree": TARGET_ID,
        "quests": {"the_fremennik_isles": {"started": True}},
        "completed_achievements": [],
    }


def _context(player_data: dict, calls: dict) -> RuntimeActionContext:
    def award_skill_exp(exp_key: str, amount: float) -> float:
        player_data[exp_key] = float(player_data.get(exp_key, 0.0) or 0.0) + amount
        return amount

    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: 0.0,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda skill, _data: calls["levels"].append(skill),
        check_achievements=lambda _data: calls.__setitem__(
            "achievements", calls["achievements"] + 1
        ),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: None,
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda text: calls["activity"].append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class WoodcuttingSplitTest(unittest.TestCase):
    def test_source_contract_and_item_identity_are_registered(self):
        spec = TREE_DATA[TARGET_ID]
        self.assertEqual(spec["requirements"], {"Arctic pine logs": 1})
        self.assertEqual(spec["output_item"], "Split log")
        self.assertEqual(spec["source_item_id"], 10812)
        self.assertEqual(spec["exp"], 42.5)
        self.assertFalse(spec["stackable"])
        self.assertTrue(spec["tradeable"])

        item = item_definitions_by_storage_key(ITEM_DEFINITIONS)["Split log"]
        self.assertEqual(item.source_item_id, 10812)
        self.assertFalse(item.stackable)
        self.assertTrue(item.tradeable)
        self.assertEqual(item.asset_path, TREE_IMAGES["Split Arctic pine logs"])
        self.assertTrue(os.path.exists(item.asset_path))

    def test_processing_action_consumes_one_log_without_a_hatchet(self):
        updated, xp, ok, output = apply_woodcutting_processing_action_pure(
            TARGET_ID,
            {"Arctic pine logs": 1},
            TREE_DATA,
            54,
        )
        self.assertTrue(ok)
        self.assertEqual(xp, 42.5)
        self.assertEqual(output, "Split log")
        self.assertEqual(updated, {"Arctic pine logs": 0, "Split log": 1})

    def test_started_quest_gate_unlocks_before_completion(self):
        locked = target_unlock_locked_reasons_pure(
            {},
            "woodcutting",
            TARGET_ID,
            QUEST_UNLOCK_RULES,
        )
        self.assertEqual(locked, ("Start The Fremennik Isles",))
        self.assertFalse(
            target_unlock_locked_reasons_pure(
                {"quests": {"the_fremennik_isles": {"started": True}}},
                "woodcutting",
                TARGET_ID,
                QUEST_UNLOCK_RULES,
            )
        )
        self.assertFalse(
            target_unlock_locked_reasons_pure(
                {"quests": {"the_fremennik_isles": {"completed": True}}},
                "firemaking",
                "arctic_pine_logs",
                QUEST_UNLOCK_RULES,
            )
        )

    def test_target_row_shows_materials_and_does_not_require_hatchet(self):
        player = _player_data()
        rows = woodcutting_target_rows(
            player,
            TREE_DATA,
            TREE_IMAGES,
            WOODCUTTING_AXE_DATA,
            "tree",
            QUEST_UNLOCK_RULES,
        )
        row = next(row for row in rows if row.target_id == TARGET_ID)
        self.assertTrue(row.enabled)
        self.assertIn("Arctic pine logs x1 (you have 2)", row.tooltip)
        self.assertIn("Base XP: 42.5 per split", row.tooltip)
        self.assertNotIn("hatchet", row.tooltip.lower())
        self.assertTrue(row.icon_path and os.path.exists(row.icon_path))

    def test_runtime_awards_one_atomic_split(self):
        player = _player_data()
        calls = {
            "errors": [],
            "levels": [],
            "achievements": 0,
            "saves": 0,
            "xp": [],
            "activity": [],
        }
        self.assertTrue(handle_woodcutting_answer(_context(player, calls)))
        self.assertEqual(
            player["inventory"],
            {"Arctic pine logs": 1, "Split log": 1},
        )
        self.assertEqual(player["woodcutting_exp"], 42.5)
        self.assertEqual(calls["levels"], ["Woodcutting"])
        self.assertEqual(calls["xp"], [42.5])
        self.assertFalse(calls["errors"])
        self.assertEqual(
            player["action_telemetry"]["actions"][
                "woodcutting:split_arctic_pine_logs"
            ]["outputs"],
            {"Split log": 1},
        )

    def test_carried_overlay_treats_split_as_processing(self):
        player = _player_data()
        calls = {
            "errors": [],
            "levels": [],
            "achievements": 0,
            "saves": 0,
            "xp": [],
            "activity": [],
        }
        with patch.object(
            runtime_actions,
            "_admit_live_cadence",
            side_effect=lambda ctx, _handler_key, _target_id: (ctx, True),
        ):
            self.assertTrue(
                run_answer_with_carried_overlay(
                    _context(player, calls),
                    "woodcutting",
                    handle_woodcutting_answer,
                )
            )
        self.assertEqual(player["inventory"]["Arctic pine logs"], 1)
        self.assertEqual(player["inventory"]["Split log"], 1)
        self.assertEqual(
            player["carried_inventory"][TARGET_ID],
            {"Arctic pine logs": 1},
        )
        self.assertNotIn("Split log", player["carried_inventory"][TARGET_ID])

    def test_missing_material_remains_a_real_lock(self):
        player = _player_data()
        player["inventory"] = {}
        reasons = woodcutting_target_locked_reasons_pure(
            player,
            TARGET_ID,
            TREE_DATA,
            WOODCUTTING_AXE_DATA,
            QUEST_UNLOCK_RULES,
        )
        self.assertEqual(reasons, ("missing Arctic pine logs x1",))


if __name__ == "__main__":
    unittest.main()
