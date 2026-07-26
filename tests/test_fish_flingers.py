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
from ankiscape.logic import fish_flingers_logic
from ankiscape.core import constants
from ankiscape.data.fish_flingers_data import (
    FISH_FLINGERS_EFFICIENCY,
    FISH_FLINGERS_EVENT_REVIEWS,
    FISH_FLINGERS_ACTIVITY_ID,
    FISH_FLINGERS_COMMUNAL_DEPLETION,
    FISH_FLINGERS_LOCATIONS,
    FISH_FLINGERS_ROTATION_ROUTE,
    FISH_FLINGERS_SPECIES,
    FISH_FLINGERS_STOCK_MAX,
)
from ankiscape.logic.fish_flingers_logic import (
    FISH_FLINGERS_STATE_VERSION,
    apply_fish_flingers_review_pure,
    buy_fish_flingers_reward_pure,
    enter_fish_flingers_pure,
    fish_flingers_view_pure,
    fishing_outfit_multiplier_pure,
    leave_fish_flingers_pure,
    sanitize_fish_flingers_session_pure,
    sync_fish_flingers_tickets_pure,
)
from ankiscape.logic_pure.logic_pure import equip_item_pure
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
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
    def test_sourced_species_locations_and_distribution_are_complete(self):
        self.assertEqual(
            {row["name"] for row in FISH_FLINGERS_SPECIES},
            {"Bass", "Cod", "Herring", "Pike", "Salmon", "Trout"},
        )
        self.assertEqual(
            {row["name"] for row in FISH_FLINGERS_LOCATIONS},
            {"Lake", "River", "Beach", "Docks"},
        )
        location_counts = [
            sum(
                1
                for _species, route_location in FISH_FLINGERS_ROTATION_ROUTE
                if route_location == index
            )
            for index in range(len(FISH_FLINGERS_LOCATIONS))
        ]
        self.assertEqual(sorted(location_counts), [1, 1, 2, 2])
        self.assertEqual(
            {species for species, _location in FISH_FLINGERS_ROTATION_ROUTE},
            set(range(6)),
        )

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
        session = entered["fish_flingers"]
        self.assertEqual(session["version"], FISH_FLINGERS_STATE_VERSION)
        self.assertEqual(session["species_index"], 0)
        self.assertEqual(session["location_index"], 0)
        self.assertEqual(session["stock"], FISH_FLINGERS_STOCK_MAX)
        self.assertEqual(session["rotation_index"], 0)
        _same, second_ok, _second_info = enter_fish_flingers_pure(entered)
        self.assertFalse(second_ok)

    def test_a_full_event_completes_and_awards_source_shaped_currencies(self):
        player, ok, info = enter_fish_flingers_pure(_player())
        self.assertTrue(ok, info)
        result = {}
        efficiencies = []
        for _ in range(FISH_FLINGERS_EVENT_REVIEWS):
            player, result = apply_fish_flingers_review_pure(
                player, 0.999, 0.0, 0.0
            )
            efficiencies.append(result["efficiency"])
        self.assertEqual(efficiencies, list(FISH_FLINGERS_EFFICIENCY))
        self.assertTrue(result["terminal"])
        self.assertEqual(player["fish_flingers"], {})
        self.assertEqual(player["activity_session"]["active_id"], "")
        self.assertEqual(player["fish_flingers_events_completed"], 1)
        # A flawless event yields exactly the sourced Master Angler threshold:
        # the ramp finishes on review three, so perfect tackles equal the event
        # length minus two.
        self.assertEqual(
            result["perfect_tackles"], FISH_FLINGERS_EVENT_REVIEWS - 2
        )
        self.assertEqual(
            result["tokens"],
            result["fish_total"] // 4
            + min(3, result["big_fish"])
            + min(3, result["assists"] // 2)
            + min(3, result["perfect_tackles"] // 2),
        )
        # Master Angler is the point of the eight-review length: at six reviews
        # perfect tackles were fixed at four forever, so the sourced six-tackle
        # medal could never be earned and this test asserted its absence.
        self.assertIn("Master Angler", result["medal_labels"])
        self.assertIn("Junior Angler", result["medal_labels"])
        self.assertEqual(result["medals"], len(result["medal_labels"]))
        self.assertGreater(result["xp"], 0)

    def test_species_location_stock_and_communal_pressure_change_outcomes(self):
        active, ok, info = enter_fish_flingers_pure(_player())
        self.assertTrue(ok, info)
        for _review in range(3):
            active, _result = apply_fish_flingers_review_pure(
                active, 0.999, 0.999, 0.999
            )
        active_view = fish_flingers_view_pure(active)
        self.assertEqual(active_view["species"], "Cod")
        self.assertEqual(active_view["location"], "River")
        self.assertEqual(active_view["stock"], FISH_FLINGERS_STOCK_MAX)

        def changed_rows(rows, index, **updates):
            changed = [dict(row) for row in rows]
            changed[index].update(updates)
            return tuple(changed)

        _baseline_player, baseline = apply_fish_flingers_review_pure(
            active, 0.999, 0.999, 0.999
        )
        with patch.object(
            fish_flingers_logic,
            "FISH_FLINGERS_SPECIES",
            changed_rows(FISH_FLINGERS_SPECIES, 1, catch_modifier=3),
        ):
            _changed_player, species_catch = apply_fish_flingers_review_pure(
                active, 0.999, 0.999, 0.999
            )
        self.assertNotEqual(species_catch["fish_caught"], baseline["fish_caught"])


        with patch.object(
            fish_flingers_logic,
            "FISH_FLINGERS_LOCATIONS",
            changed_rows(FISH_FLINGERS_LOCATIONS, 1, catch_modifier=2),
        ):
            _changed_player, location_catch = apply_fish_flingers_review_pure(
                active, 0.999, 0.999, 0.999
            )
        self.assertNotEqual(location_catch["fish_caught"], baseline["fish_caught"])


        fading_player, rich_catch = apply_fish_flingers_review_pure(
            active, 0.999, 0.999, 0.999
        )
        _low_player, fading_catch = apply_fish_flingers_review_pure(
            fading_player, 0.999, 0.999, 0.999
        )
        self.assertEqual(rich_catch["species"], fading_catch["species"])
        self.assertEqual(rich_catch["location"], fading_catch["location"])
        self.assertGreater(rich_catch["fish_caught"], fading_catch["fish_caught"])

        def pressure_path(pressure):
            player, path_ok, path_info = enter_fish_flingers_pure(_player())
            self.assertTrue(path_ok, path_info)
            rows = []
            with patch.object(
                fish_flingers_logic,
                "FISH_FLINGERS_COMMUNAL_DEPLETION",
                pressure,
            ):
                for _review in range(4):
                    player, result = apply_fish_flingers_review_pure(
                        player, 0.0, 0.999, 0.999
                    )
                    rows.append(result)
            return rows

        normal_path = pressure_path(FISH_FLINGERS_COMMUNAL_DEPLETION)
        pressured_path = pressure_path(FISH_FLINGERS_COMMUNAL_DEPLETION * 2)
        self.assertEqual(normal_path[0]["fish_caught"], pressured_path[0]["fish_caught"])
        self.assertLess(pressured_path[0]["stock_after"], normal_path[0]["stock_after"])
        self.assertNotEqual(
            [row["fish_caught"] for row in pressured_path[1:]],
            [row["fish_caught"] for row in normal_path[1:]],
        )

    def test_real_events_deplete_stock_and_reach_the_full_rotation_route(self):
        player = _player(fishing_level=1)
        route_seen = set()
        rotations = 0
        terminal_exhaustions = 0
        # Six events at a low catch roll: the terminal-exhaustion branch only
        # occurs when the last review happens to empty the stock, which is a
        # coincidence of roll and length rather than something a fixed short run
        # guarantees. The earlier version depended on that coincidence.
        for event_index in range(6):
            player["shop_market_clock"] = {
                "answered_cards": event_index * 240,
                "market_tick": 0,
            }
            player, ok, info = enter_fish_flingers_pure(player)
            self.assertTrue(ok, info)
            for review_index in range(FISH_FLINGERS_EVENT_REVIEWS):
                player, result = apply_fish_flingers_review_pure(
                    player, 0.01, 0.999, 0.999
                )
                route_seen.add((result["species"], result["location"]))
                rotations += int(result["rotated"])
                if event_index == 0 and review_index == 0:
                    self.assertEqual(
                        result["stock_after"],
                        FISH_FLINGERS_STOCK_MAX
                        - result["fish_caught"]
                        - FISH_FLINGERS_COMMUNAL_DEPLETION,
                    )
                if result["terminal"] and result["stock_after"] == 0:
                    terminal_exhaustions += 1
                    self.assertFalse(result["rotated"])
                    self.assertNotIn("stock rotated", result["status"])
            self.assertTrue(result["terminal"])
            self.assertEqual(player["fish_flingers"], {})

        self.assertEqual(
            route_seen,
            {
                ("Bass", "Lake"),
                ("Cod", "River"),
                ("Herring", "Beach"),
                ("Pike", "Beach"),
                ("Salmon", "Docks"),
                ("Trout", "Docks"),
            },
        )
        self.assertGreater(rotations, 0)
        self.assertGreater(terminal_exhaustions, 0)

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
        # Tokens and medals are EARNED here rather than assigned. The earlier
        # version opened by writing 500 tokens and 50 medals into the fixture,
        # which certified the shop's arithmetic but would have passed unchanged
        # if reward accrual had broken entirely.
        # Sixty events: the three purchases below need 480 tokens, and the basic
        # tackle box additionally requires 50 cumulative medals, so a shorter run
        # would fail on the requirement rather than on the behaviour under test.
        player = _player(fishing_level=1)
        for event_index in range(60):
            player["shop_market_clock"] = {
                "answered_cards": event_index * 240,
                "market_tick": 0,
            }
            player, entered, info = enter_fish_flingers_pure(player)
            self.assertTrue(entered, info)
            for _ in range(FISH_FLINGERS_EVENT_REVIEWS):
                player, _result = apply_fish_flingers_review_pure(
                    player, 0.999, 0.999, 0.999
                )
        earned_tokens = int(player["fish_flingers_tokens"])
        earned_medals = int(player["fish_flingers_medals"])
        self.assertGreater(earned_tokens, 0, "playing must yield tokens")
        self.assertGreater(earned_medals, 0, "playing must yield medals")

        player, ok, info = buy_fish_flingers_reward_pure(player, "fishing_hat")
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"]["Fishing hat"], 1)
        self.assertEqual(player["fish_flingers_tokens"], earned_tokens - 140)
        player, ok, info = buy_fish_flingers_reward_pure(
            player, "beginner_tackle_box"
        )
        self.assertTrue(ok, info)
        self.assertEqual(
            player["fish_flingers_medals"],
            earned_medals,
            "medals are cumulative currency and must survive a token purchase",
        )
        self.assertEqual(player["inventory"]["Beginner's tackle box"], 1)
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

    def test_active_view_exposes_all_outcome_affecting_stock_context(self):
        player, ok, info = enter_fish_flingers_pure(_player())
        self.assertTrue(ok, info)
        view = fish_flingers_view_pure(player)
        self.assertEqual(view["species"], "Bass")
        self.assertEqual(view["location"], "Lake")
        self.assertEqual(view["stock"], FISH_FLINGERS_STOCK_MAX)
        self.assertEqual(view["stock_percent"], 100)
        self.assertEqual(view["stock_label"], "Rich")
        self.assertEqual(view["rotation"], "1/6")
        self.assertEqual(view["communal_pressure"], FISH_FLINGERS_COMMUNAL_DEPLETION)
        self.assertIn("per review", view["communal_pressure_label"])

        player, result = apply_fish_flingers_review_pure(
            player, 0.5, 0.999, 0.999
        )
        weighted_view = fish_flingers_view_pure(player)


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
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        # The sanitizer clamps to the last review index of an event.
        self.assertEqual(
            migrated["fish_flingers"]["review"], FISH_FLINGERS_EVENT_REVIEWS - 1
        )
        self.assertEqual(migrated["fish_flingers"]["fish_caught"], 0)
        self.assertEqual(
            migrated["fish_flingers"]["version"], FISH_FLINGERS_STATE_VERSION
        )
        self.assertEqual(migrated["fish_flingers"]["stock"], FISH_FLINGERS_STOCK_MAX)

        repaired = sanitize_fish_flingers_session_pure(
            {
                "version": 999,
                "review": "bad",
                "rotation_index": 999,
                "species_index": -2,
                "location_index": 999,
                "stock": -50,
            }
        )
        self.assertEqual(repaired["version"], FISH_FLINGERS_STATE_VERSION)
        self.assertEqual(repaired["rotation_index"], 5)
        self.assertEqual(repaired["species_index"], 0)
        self.assertEqual(repaired["location_index"], 3)
        self.assertEqual(repaired["stock"], 1)


class FishFlingersHookTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_multiplier_finishes_one_event_and_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_fish_flingers_hook")
        logic = sys.modules[f"{addon.__name__}.logic.fish_flingers_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        package_constants = sys.modules[f"{addon.__name__}.core.constants"]
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
        # Three rolls per review: catch, big fish, assist.
        self.assertEqual(rng.call_count, FISH_FLINGERS_EVENT_REVIEWS * 3)
        self.assertEqual(addon.player_data["fish_flingers_events_completed"], 1)
        self.assertEqual(addon.player_data["fish_flingers"], {})
        self.assertGreater(addon.player_data["fishing_exp"], before_xp)
        self.assertIn(" at ", addon.player_data["fish_flingers_last_result"])
        self.assertIn("stock", addon.player_data["fish_flingers_last_result"])

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon.player_data, before)


if __name__ == "__main__":
    unittest.main()
