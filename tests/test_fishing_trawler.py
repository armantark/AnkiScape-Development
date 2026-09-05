from __future__ import annotations

import copy
import json
from pathlib import Path
import struct
import sys
import types
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic import cadence_coverage
from ankiscape.core import constants
from ankiscape.data.fishing_trawler_data import (
    FISHING_TRAWLER_ACTIVITY_ID,
    FISHING_TRAWLER_TIGER_SHARK,
    FISHING_TRAWLER_TIGER_SHARK_TRIP_CHANCE,
)
from ankiscape.logic.fishing_trawler_logic import (
    apply_fishing_trawler_review_pure,
    enter_fishing_trawler_pure,
    fishing_trawler_view_pure,
    leave_fishing_trawler_pure,
    set_fishing_trawler_policy_pure,
)
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


ROOT = Path(__file__).resolve().parents[1]


def _player(**updates):
    player = {
        "inventory": {
            "Swamp paste": 60,
            "Rope": 4,
            "Bailing bucket": 1,
        },
        "fishing_level": 81,
        "fishing_exp": 0.0,
        "activity_session": {"active_id": ""},
    }
    player.update(updates)
    return player


class FishingTrawlerDataTests(unittest.TestCase):
    def test_period_tiger_shark_row_is_registered_exactly(self):
        self.assertEqual(FISHING_TRAWLER_TIGER_SHARK.item, "Raw tiger shark")
        self.assertEqual(FISHING_TRAWLER_TIGER_SHARK.level, 95)
        self.assertEqual(FISHING_TRAWLER_TIGER_SHARK.ordinary_xp, 80.0)
        self.assertEqual(FISHING_TRAWLER_TIGER_SHARK.source_item_id, 21520)
        self.assertEqual(FISHING_TRAWLER_TIGER_SHARK_TRIP_CHANCE, 0.20)

    def test_activity_supplies_rewards_and_asset_are_reachable(self):
        spec = constants.UTILITY_ACTIVITY_DATA[FISHING_TRAWLER_ACTIVITY_ID]
        self.assertEqual(spec["skill_requirements"], {"fishing": 15})
        self.assertEqual(spec["surface"], "activities")
        registered = {item.display_name for item in constants.ITEM_DEFINITIONS}
        for item in (
            "Swamp paste",
            "Rope",
            "Bailing bucket",
            "Raw sea turtle",
            "Raw manta ray",
            "Raw tiger shark",
        ):
            self.assertIn(item, registered)
        rope = next(
            item for item in constants.ITEM_DEFINITIONS if item.display_name == "Rope"
        )
        self.assertFalse(rope.stackable)
        self.assertEqual(rope.source_item_id, 954)
        tiger_items = {
            item.display_name: item
            for item in constants.ITEM_DEFINITIONS
            if item.display_name in {
                "Raw tiger shark",
                "Tiger shark",
                "Burnt tiger shark",
            }
        }
        self.assertEqual(tiger_items["Raw tiger shark"].source_item_id, 21520)
        self.assertEqual(tiger_items["Tiger shark"].source_item_id, 21521)
        self.assertEqual(tiger_items["Burnt tiger shark"].source_item_id, 21522)
        self.assertTrue(all(not item.tradeable for item in tiger_items.values()))
        self.assertTrue(all(not item.stackable for item in tiger_items.values()))
        self.assertTrue(all(item.asset_path for item in tiger_items.values()))

        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        relative = "activityicons/fishing_trawler.png"
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
        for relative in (
            "cookingitems/raw_tiger_shark.png",
            "cookingitems/tiger_shark.png",
        ):
            self.assertLessEqual(
                provenance[relative]["timestamp"],
                "2012-11-20T23:59:59Z",
            )
        self.assertIn(
            "visual art only",
            provenance["cookingitems/burnt_tiger_shark.png"]["source_note"],
        )

    def test_cadence_ledger_names_ten_event_pressure_handler(self):
        row = next(
            row
            for row in cadence_coverage.cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == FISHING_TRAWLER_ACTIVITY_ID
        )
        self.assertEqual(row["route_kind"], "activity")
        self.assertIn("ten-review", row["source_reason"])
        self.assertIn("not mapped to wall-clock", row["source_reason"])


class FishingTrawlerLogicTests(unittest.TestCase):
    def test_tiger_shark_requires_level_ninety_five_and_is_capped_at_one_per_trip(self):
        outputs_by_level = {}
        for level in (94, 95):
            player, ok, info = enter_fishing_trawler_pure(
                _player(fishing_level=level)
            )
            self.assertTrue(ok, info)
            for _ in range(10):
                player, result = apply_fishing_trawler_review_pure(player, 0.10)
            self.assertTrue(result["terminal"])
            outputs_by_level[level] = result["outputs"]

        self.assertNotIn("Raw tiger shark", outputs_by_level[94])
        self.assertEqual(outputs_by_level[95]["Raw tiger shark"], 1)

    def test_entry_requires_level_fifteen_and_reserves_configured_supplies(self):
        _blocked, ok, info = enter_fishing_trawler_pure(
            _player(fishing_level=14)
        )
        self.assertFalse(ok)
        self.assertIn("level 15", info["reason"])

        entered, ok, info = enter_fishing_trawler_pure(_player())
        self.assertTrue(ok, info)
        self.assertEqual(
            entered["activity_session"]["active_id"],
            FISHING_TRAWLER_ACTIVITY_ID,
        )
        self.assertEqual(entered["inventory"], {})
        self.assertEqual(
            entered["fishing_trawler"]["supplies"],
            {"Swamp paste": 60, "Rope": 4, "Bailing bucket": 1},
        )

    def test_casual_trip_completes_in_ten_reviews_banks_haul_and_returns_supplies(self):
        player, ok, info = enter_fishing_trawler_pure(_player())
        self.assertTrue(ok, info)
        duties = []
        for _ in range(10):
            player, result = apply_fishing_trawler_review_pure(player, 0.9)
            duties.append(result["duty"])
        self.assertTrue(result["terminal"])
        self.assertFalse(result["sunk"])
        self.assertEqual(player["fishing_trawler"], {})
        self.assertEqual(player["activity_session"]["active_id"], "")
        self.assertEqual(player["fishing_trawler_trips_completed"], 1)
        self.assertEqual(sum(result["outputs"].values()), 11)
        self.assertEqual(result["xp"], 266.4)
        self.assertIn("repair_leak", duties)
        self.assertIn("bail", duties)
        self.assertIn("repair_net", duties)
        self.assertIn("fish", duties)
        self.assertEqual(player["inventory"]["Bailing bucket"], 1)
        self.assertEqual(player["inventory"]["Swamp paste"], 20)
        self.assertEqual(player["inventory"]["Rope"], 2)
        self.assertEqual(player["inventory"]["Raw manta ray"], 4)

    def test_trip_without_supplies_sinks_and_awards_no_haul(self):
        player, ok, info = enter_fishing_trawler_pure(
            _player(fishing_level=15, inventory={})
        )
        self.assertTrue(ok, info)
        for _ in range(10):
            player, result = apply_fishing_trawler_review_pure(player, 0.5)
            if result["terminal"]:
                break
        self.assertTrue(result["sunk"])
        self.assertEqual(result["outputs"], {})
        self.assertEqual(result["xp"], 0.0)
        self.assertEqual(player["fishing_trawler_trips_sunk"], 1)
        self.assertNotIn("Raw anchovies", player["inventory"])

    def test_advanced_policy_and_layout_are_saved_only_between_trips(self):
        player, ok, info = set_fishing_trawler_policy_pure(
            _player(),
            {
                "automation_mode": "advanced",
                "priority": "catch_first",
                "layout": {
                    "Swamp paste": 20,
                    "Rope": 2,
                    "Bailing bucket": 1,
                },
            },
        )
        self.assertTrue(ok, info)
        view = fishing_trawler_view_pure(player)
        self.assertEqual(view["automation_mode"], "advanced")
        self.assertEqual(view["priority"], "catch_first")
        self.assertEqual(view["layout"]["Swamp paste"], 20)
        player, ok, info = enter_fishing_trawler_pure(player)
        self.assertTrue(ok, info)
        _same, changed, info = set_fishing_trawler_policy_pure(
            player, {"priority": "water_first"}
        )
        self.assertFalse(changed)
        self.assertIn("Finish or leave", info["reason"])

    def test_layout_capacity_counts_paste_as_stackable_and_rope_buckets_individually(self):
        _same, ok, info = set_fishing_trawler_policy_pure(
            _player(),
            {
                "layout": {
                    "Swamp paste": 999,
                    "Rope": 20,
                    "Bailing bucket": 8,
                }
            },
        )
        self.assertFalse(ok)
        self.assertIn("29/28 slots", info["reason"])

    def test_leave_returns_unused_supplies_and_forfeits_progress(self):
        player, ok, _info = enter_fishing_trawler_pure(_player())
        self.assertTrue(ok)
        player, _result = apply_fishing_trawler_review_pure(player, 0.5)
        left, ok, info = leave_fishing_trawler_pure(player)
        self.assertTrue(ok, info)
        self.assertEqual(left["fishing_trawler"], {})
        self.assertEqual(left["inventory"]["Swamp paste"], 60)
        self.assertEqual(left["inventory"]["Rope"], 4)
        self.assertEqual(left["inventory"]["Bailing bucket"], 1)
        self.assertIn("haul forfeited", left["fishing_trawler_last_result"])


class FishingTrawlerStorageTests(unittest.TestCase):
    def test_default_and_v65_migration_include_sanitized_trawler_state(self):
        default = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        self.assertEqual(default["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(default["fishing_trawler"], {})
        migrated = migrate_loaded_data(
            {
                "config_version": 64,
                "fishing_level": 99,
                "fishing_trawler": {
                    "review": 999,
                    "water": 999,
                    "supplies": {"Swamp paste": -4},
                },
                "activity_session": {"active_id": FISHING_TRAWLER_ACTIVITY_ID},
            },
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["fishing_trawler"]["review"], 9)
        self.assertEqual(migrated["fishing_trawler"]["water"], 100)
        self.assertEqual(
            migrated["activity_session"]["active_id"],
            FISHING_TRAWLER_ACTIVITY_ID,
        )


class FishingTrawlerHookTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_multiplier_finishes_one_trip_and_undo_restores_bank_and_session(self):
        addon = _load_addon_as_package("ankiscape_fishing_trawler_hook")
        logic = sys.modules[f"{addon.__name__}.logic.fishing_trawler_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        package_constants = sys.modules[f"{addon.__name__}.core.constants"]
        player = storage.default_player_data(
            package_constants.ORE_DATA,
            package_constants.ITEM_DEFINITIONS,
        )
        player.update(
            {
                "fishing_level": 81,
                "inventory": {
                    **player["inventory"],
                    "Swamp paste": 60,
                    "Rope": 4,
                    "Bailing bucket": 1,
                },
            }
        )
        player, ok, _info = logic.enter_fishing_trawler_pure(player)
        self.assertTrue(ok)
        addon._state.player_data = player
        addon._state.current_skill = "Activities"
        addon._state.exp_awarded = False
        addon._review_action_multiplier = lambda: 20
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda _amount: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon._state.player_data)
        with patch.object(addon.random, "random", return_value=0.9) as rng:
            addon.on_good_answer(before)
        self.assertEqual(rng.call_count, 10)
        self.assertEqual(addon._state.player_data["fishing_trawler_trips_completed"], 1)
        self.assertGreater(addon._state.player_data["fishing_exp"], before["fishing_exp"])

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, before)


if __name__ == "__main__":
    unittest.main()
