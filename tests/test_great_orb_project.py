from __future__ import annotations

import copy
import json
from pathlib import Path
import struct
import sys
import types
import unittest
from unittest.mock import patch

import cadence_coverage
import constants
from great_orb_project_data import GREAT_ORB_PROJECT_ACTIVITY_ID
from great_orb_project_logic import (
    apply_great_orb_project_review_pure,
    buy_great_orb_project_reward_pure,
    enter_great_orb_project_pure,
    great_orb_project_view_pure,
    leave_great_orb_project_pure,
    set_great_orb_project_policy_pure,
)
from storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


ROOT = Path(__file__).resolve().parents[1]


def _player(**updates):
    player = {
        "inventory": {},
        "runecrafting_level": 50,
        "runecrafting_exp": 0.0,
        "activity_session": {"active_id": ""},
    }
    player.update(updates)
    return player


class GreatOrbProjectDataTests(unittest.TestCase):
    def test_activity_reward_items_and_normalized_asset_are_registered(self):
        spec = constants.UTILITY_ACTIVITY_DATA[GREAT_ORB_PROJECT_ACTIVITY_ID]
        self.assertEqual(spec["skill_requirements"], {"runecrafting": 50})
        self.assertEqual(spec["surface"], "activities")
        registered = {item.display_name for item in constants.ITEM_DEFINITIONS}
        self.assertIn("Pure essence", registered)
        self.assertIn("Air talisman", registered)

        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        for relative in ("activityicons/great_orb_project.png",):
            self.assertIn(relative, provenance)
            self.assertLessEqual(
                provenance[relative]["timestamp"], "2012-11-20T23:59:59Z"
            )
            header = (ROOT / relative).read_bytes()[:26]
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            width, height, bit_depth, color_type = struct.unpack(">IIBB", header[16:26])
            self.assertEqual((bit_depth, color_type), (8, 6))
            self.assertLessEqual(max(width, height), 64)

    def test_cadence_ledger_names_one_round_per_review(self):
        row = next(
            row
            for row in cadence_coverage.cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == GREAT_ORB_PROJECT_ACTIVITY_ID
        )
        self.assertEqual(row["route_kind"], "activity")
        self.assertIn("one complete altar round", row["source_reason"])
        self.assertIn("cannot begin another match", row["multiplier_behavior"])


class GreatOrbProjectLogicTests(unittest.TestCase):
    def test_entry_requires_level_fifty(self):
        _blocked, ok, info = enter_great_orb_project_pure(
            _player(runecrafting_level=49)
        )
        self.assertFalse(ok)
        self.assertIn("level 50", info["reason"])
        entered, ok, info = enter_great_orb_project_pure(_player())
        self.assertTrue(ok, info)
        self.assertEqual(
            entered["activity_session"]["active_id"],
            GREAT_ORB_PROJECT_ACTIVITY_ID,
        )

    def test_casual_match_resolves_eight_altars_xp_runes_and_exact_tokens(self):
        player, ok, info = enter_great_orb_project_pure(_player())
        self.assertTrue(ok, info)
        xp = 0.0
        for _ in range(8):
            player, result = apply_great_orb_project_review_pure(player, 0.99, 0.0)
            xp += result["xp"]
        self.assertTrue(result["terminal"])
        self.assertEqual(player["great_orb_project"]["tokens"], 1000)
        self.assertEqual(player["great_orb_project"]["games_completed"], 1)
        self.assertEqual(player["great_orb_project"]["games_won"], 1)
        self.assertEqual(player["activity_session"]["active_id"], "")
        self.assertEqual(xp, 990.0)
        self.assertEqual(player["inventory"]["Air rune"], 45)
        self.assertEqual(player["inventory"]["Nature rune"], 9)

    def test_advanced_barrier_and_save_policy_preserve_tradeoffs(self):
        player, ok, info = set_great_orb_project_policy_pure(
            _player(),
            {
                "automation_mode": "advanced",
                "doctrine": "barrier",
                "crafting_policy": "save_for_nature",
            },
        )
        self.assertTrue(ok, info)
        player, ok, info = enter_great_orb_project_pure(player)
        self.assertTrue(ok, info)
        dropped = 0
        for _ in range(8):
            player, result = apply_great_orb_project_review_pure(player, 0.99, 0.0)
            dropped += result["essence_dropped"]
        self.assertTrue(result["terminal"])
        self.assertFalse(result["participating"])
        self.assertGreater(dropped, 0)
        self.assertEqual(result["majority_bonus"], 200)
        self.assertEqual(player["great_orb_project"]["tokens"], 200)
        self.assertEqual(player["inventory"]["Nature rune"], 28)
        self.assertEqual(result["xp"], 504.0)

    def test_leave_forfeits_pending_tokens_but_keeps_already_crafted_runes(self):
        player, ok, _info = enter_great_orb_project_pure(_player())
        self.assertTrue(ok)
        player, result = apply_great_orb_project_review_pure(player, 0.99, 0.0)
        self.assertEqual(result["round_tokens"], 100)
        left, ok, info = leave_great_orb_project_pure(player)
        self.assertTrue(ok, info)
        self.assertEqual(left["great_orb_project"]["tokens"], 0)
        self.assertEqual(left["inventory"]["Air rune"], 45)
        self.assertIn("100 pending tokens forfeited", info["message"])

    def test_reward_shop_supports_buy_x_and_rejects_active_matches(self):
        player = _player(
            great_orb_project={
                "tokens": 1000,
                "automation_mode": "casual",
                "doctrine": "balanced",
                "crafting_policy": "craft_each_round",
                "active": {},
            }
        )
        player, ok, info = buy_great_orb_project_reward_pure(
            player, "pure_essence", 125
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"]["Pure essence"], 125)
        self.assertEqual(player["great_orb_project"]["tokens"], 875)
        player, ok, info = buy_great_orb_project_reward_pure(
            player, "air_talisman", 99
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"]["Air talisman"], 1)
        self.assertEqual(player["great_orb_project"]["tokens"], 825)
        active, ok, _info = enter_great_orb_project_pure(player)
        self.assertTrue(ok)
        _same, ok, info = buy_great_orb_project_reward_pure(
            active, "air_talisman"
        )
        self.assertFalse(ok)
        self.assertIn("Finish or leave", info["reason"])

    def test_view_exposes_lock_policy_shop_and_active_round(self):
        locked = great_orb_project_view_pure(_player(runecrafting_level=49))
        self.assertFalse(locked["eligible"])
        self.assertEqual(len(locked["rewards"]), 2)
        active, ok, _info = enter_great_orb_project_pure(_player())
        self.assertTrue(ok)
        view = great_orb_project_view_pure(active)
        self.assertTrue(view["active"])
        self.assertEqual(view["round_number"], 1)
        self.assertEqual(view["altar"], "Air altar")


class GreatOrbProjectStorageTests(unittest.TestCase):
    def test_default_and_v66_migration_sanitize_state(self):
        default = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        self.assertEqual(default["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(default["great_orb_project"]["tokens"], 0)
        migrated = migrate_loaded_data(
            {
                "config_version": 65,
                "runecrafting_level": 50,
                "great_orb_project": {
                    "tokens": -4,
                    "automation_mode": "invalid",
                    "active": {"round": 999, "saved_essence": 999},
                },
                "activity_session": {"active_id": GREAT_ORB_PROJECT_ACTIVITY_ID},
            },
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["great_orb_project"]["tokens"], 0)
        self.assertEqual(migrated["great_orb_project"]["automation_mode"], "casual")
        self.assertEqual(migrated["great_orb_project"]["active"]["round"], 7)
        self.assertEqual(migrated["great_orb_project"]["active"]["saved_essence"], 28)


class GreatOrbProjectHookTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_multiplier_finishes_one_match_and_undo_restores_state(self):
        addon = _load_addon_as_package("ankiscape_great_orb_project_hook")
        logic = sys.modules[f"{addon.__name__}.great_orb_project_logic"]
        storage = sys.modules[f"{addon.__name__}.storage_pure"]
        package_constants = sys.modules[f"{addon.__name__}.constants"]
        player = storage.default_player_data(
            package_constants.ORE_DATA,
            package_constants.ITEM_DEFINITIONS,
        )
        player["runecrafting_level"] = 50
        player, ok, _info = logic.enter_great_orb_project_pure(player)
        self.assertTrue(ok)
        addon.player_data = player
        addon.current_skill = "Activities"
        addon.exp_awarded = False
        addon._review_action_multiplier = lambda: 20
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda _amount: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon.player_data)
        with patch.object(addon.random, "random", side_effect=[0.99, 0.0] * 8) as rng:
            addon.on_good_answer(before)
        self.assertEqual(rng.call_count, 16)
        self.assertEqual(addon.player_data["great_orb_project"]["games_completed"], 1)
        self.assertGreater(addon.player_data["runecrafting_exp"], before["runecrafting_exp"])

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon.player_data, before)


if __name__ == "__main__":
    unittest.main()
