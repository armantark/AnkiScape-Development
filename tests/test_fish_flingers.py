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
from fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID
from fish_flingers_logic import (
    apply_fish_flingers_review_pure,
    buy_fish_flingers_reward_pure,
    enter_fish_flingers_pure,
    fish_flingers_view_pure,
    fishing_outfit_multiplier_pure,
    leave_fish_flingers_pure,
    sync_fish_flingers_tickets_pure,
)
from logic_pure import equip_item_pure
from storage_pure import default_player_data, migrate_loaded_data
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


ROOT = Path(__file__).resolve().parents[1]


def _player(**updates):
    player = {
        "inventory": {},
        "equipment": {},
        "fishing_level": 99,
        "shop_market_clock": {"answered_cards": 0, "market_tick": 0},
        "activity_session": {"active_id": ""},
    }
    player.update(updates)
    return player


class FishFlingersDataTests(unittest.TestCase):
    def test_activity_and_reward_items_are_registered(self):
        spec = constants.UTILITY_ACTIVITY_DATA[FISH_FLINGERS_ACTIVITY_ID]
        self.assertEqual(spec["group"], "distractions_and_diversions")
        self.assertEqual(spec["surface"], "activities")
        registered = {item.display_name for item in constants.ITEM_DEFINITIONS}
        for item in (
            "Fishing hat",
            "Fishing jacket",
            "Fishing waders",
            "Fishing boots",
            "Champion's tackle box",
        ):
            self.assertIn(item, registered)

    def test_cadence_ledger_names_the_finite_six_catch_handler(self):
        row = next(
            row
            for row in cadence_coverage.cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == FISH_FLINGERS_ACTIVITY_ID
        )
        self.assertEqual(row["route_kind"], "activity")
        self.assertIn("six-review", row["source_reason"])

    def test_outfit_is_equippable_and_all_assets_are_period_normalized(self):
        item = constants.EQUIPMENT_ITEM_DATA["Fishing hat"]
        self.assertEqual(item["slot"], "head")
        self.assertEqual(item["source_item_id"], 24427)
        inventory, equipment, equipped = equip_item_pure(
            "Fishing hat",
            {"Fishing hat": 1},
            {},
            constants.EQUIPMENT_ITEM_DATA,
        )
        self.assertTrue(equipped)
        self.assertEqual(inventory["Fishing hat"], 0)
        self.assertEqual(equipment, {"head": "Fishing hat"})

        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        paths = (
            "activityicons/fish_flingers.png",
            "activityitems/fishing_hat.png",
            "activityitems/fishing_jacket.png",
            "activityitems/fishing_waders.png",
            "activityitems/fishing_boots.png",
            "activityitems/beginner_s_tackle_box.png",
            "activityitems/basic_tackle_box.png",
            "activityitems/standard_tackle_box.png",
            "activityitems/professional_tackle_box.png",
            "activityitems/champion_s_tackle_box.png",
        )
        for relative in paths:
            self.assertIn(relative, provenance)
            self.assertLessEqual(
                provenance[relative]["timestamp"],
                "2012-11-20T23:59:59Z",
            )
            header = (ROOT / relative).read_bytes()[:26]
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            width, height, bit_depth, color_type = struct.unpack(">IIBB", header[16:26])
            self.assertEqual((bit_depth, color_type), (8, 6))
            self.assertLessEqual(max(width, height), 64)


class FishFlingersLogicTests(unittest.TestCase):
    def test_daily_ticket_grant_uses_answered_cards_and_caps_at_ten(self):
        claimed = sync_fish_flingers_tickets_pure(_player())
        self.assertEqual(claimed["fish_flingers_tickets"], 2)
        same_day = sync_fish_flingers_tickets_pure(claimed)
        self.assertEqual(same_day["fish_flingers_tickets"], 2)
        same_day["shop_market_clock"]["answered_cards"] = 240 * 8
        capped = sync_fish_flingers_tickets_pure(same_day)
        self.assertEqual(capped["fish_flingers_tickets"], 10)
        self.assertEqual(capped["fish_flingers_last_ticket_day"], 8)

    def test_entry_consumes_one_ticket_and_requires_no_level_or_items(self):
        entered, ok, info = enter_fish_flingers_pure(
            _player(fishing_level=1, inventory={})
        )
        self.assertTrue(ok, info)
        self.assertEqual(entered["fish_flingers_tickets"], 1)
        self.assertEqual(
            entered["activity_session"]["active_id"], FISH_FLINGERS_ACTIVITY_ID
        )
        self.assertEqual(entered["current_utility"], FISH_FLINGERS_ACTIVITY_ID)
        _same, second_ok, _second_info = enter_fish_flingers_pure(entered)
        self.assertFalse(second_ok)

    def test_six_reviews_complete_event_and_award_source_shaped_currencies(self):
        player, ok, info = enter_fish_flingers_pure(_player())
        self.assertTrue(ok, info)
        result = {}
        efficiencies = []
        for _ in range(6):
            player, result = apply_fish_flingers_review_pure(
                player, 0.999, 0.0, 0.0
            )
            efficiencies.append(result["efficiency"])
        self.assertEqual(efficiencies, [0.5, 0.75, 1.0, 1.0, 1.0, 1.0])
        self.assertTrue(result["terminal"])
        self.assertEqual(player["fish_flingers"], {})
        self.assertEqual(player["activity_session"]["active_id"], "")
        self.assertEqual(player["fish_flingers_events_completed"], 1)
        self.assertEqual(result["fish_total"], 42)
        self.assertEqual(result["perfect_tackles"], 4)
        self.assertEqual(result["tokens"], 18)
        self.assertEqual(result["medals"], 3)
        self.assertNotIn("Master Angler", result["medal_labels"])
        self.assertGreater(result["xp"], 0)

    def test_leave_forfeits_progress_without_refunding_ticket(self):
        player, ok, _info = enter_fish_flingers_pure(_player())
        self.assertTrue(ok)
        player, _result = apply_fish_flingers_review_pure(player, 0.5, 0.5, 0.5)
        tickets = player["fish_flingers_tickets"]
        left, left_ok, info = leave_fish_flingers_pure(player)
        self.assertTrue(left_ok, info)
        self.assertEqual(left["fish_flingers_tickets"], tickets)
        self.assertEqual(left["fish_flingers"], {})
        self.assertIn("forfeited", left["fish_flingers_last_result"])

    def test_reward_shop_spends_tokens_but_retains_cumulative_medals(self):
        player = _player(
            fish_flingers_tokens=500,
            fish_flingers_medals=50,
            fish_flingers_last_ticket_day=0,
        )
        player, ok, info = buy_fish_flingers_reward_pure(player, "fishing_hat")
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"]["Fishing hat"], 1)
        self.assertEqual(player["fish_flingers_tokens"], 360)
        player, ok, info = buy_fish_flingers_reward_pure(
            player, "beginner_tackle_box"
        )
        self.assertTrue(ok, info)
        self.assertEqual(player["fish_flingers_medals"], 50)
        self.assertEqual(player["inventory"]["Beginner's tackle box"], 1)
        player["fish_flingers_tokens"] = 230
        upgraded, ok, info = buy_fish_flingers_reward_pure(
            player, "basic_tackle_box"
        )
        self.assertTrue(ok, info)
        self.assertNotIn("Beginner's tackle box", upgraded["inventory"])
        self.assertEqual(upgraded["inventory"]["Basic tackle box"], 1)

    def test_fishing_outfit_is_one_percent_per_piece_plus_full_set_bonus(self):
        self.assertEqual(fishing_outfit_multiplier_pure(_player()), 1.0)
        one = _player(equipment={"head": "Fishing hat"})
        self.assertAlmostEqual(fishing_outfit_multiplier_pure(one), 1.01)
        full = _player(
            equipment={
                "head": "Fishing hat",
                "body": "Fishing jacket",
                "legs": "Fishing waders",
                "feet": "Fishing boots",
            }
        )
        self.assertAlmostEqual(fishing_outfit_multiplier_pure(full), 1.05)

    def test_view_syncs_ticket_grant_without_mutating_input(self):
        source = _player()
        view = fish_flingers_view_pure(source)
        self.assertEqual(view["tickets"], 2)
        self.assertNotIn("fish_flingers_tickets", source)


class FishFlingersStorageTests(unittest.TestCase):
    def test_default_and_migration_include_sanitized_fish_flingers_state(self):
        default = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        self.assertEqual(default["fish_flingers"], {})
        migrated = migrate_loaded_data(
            {
                "config_version": 63,
                "fish_flingers": {"review": 999, "fish_caught": -4},
                "activity_session": {"active_id": FISH_FLINGERS_ACTIVITY_ID},
            },
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], 64)
        self.assertEqual(migrated["fish_flingers"]["review"], 5)
        self.assertEqual(migrated["fish_flingers"]["fish_caught"], 0)


class FishFlingersHookTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_multiplier_finishes_one_event_in_six_reviews_and_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_fish_flingers_hook")
        logic = sys.modules[f"{addon.__name__}.fish_flingers_logic"]
        storage = sys.modules[f"{addon.__name__}.storage_pure"]
        package_constants = sys.modules[f"{addon.__name__}.constants"]
        player = storage.default_player_data(
            package_constants.ORE_DATA,
            package_constants.ITEM_DEFINITIONS,
        )
        player["fishing_level"] = 99
        player, ok, _info = logic.enter_fish_flingers_pure(player)
        self.assertTrue(ok)
        addon.player_data = player
        addon.current_skill = "Utility / Activities"
        addon.exp_awarded = False
        addon._review_action_multiplier = lambda: 9
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda _amount: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon.player_data)
        before_xp = float(before["fishing_exp"])
        with patch.object(addon.random, "random", return_value=0.999) as rng:
            addon.on_good_answer(before)
        self.assertEqual(rng.call_count, 18)
        self.assertEqual(addon.player_data["fish_flingers_events_completed"], 1)
        self.assertEqual(addon.player_data["fish_flingers"], {})
        self.assertGreater(addon.player_data["fishing_exp"], before_xp)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon.player_data, before)


if __name__ == "__main__":
    unittest.main()
