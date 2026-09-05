import json
import itertools
import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core import constants
from ankiscape.logic.agility_logic import apply_agility_command_pure
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.data.pyramid_plunder_data import (
    PYRAMID_PLUNDER_ACTIVITY_ID,
    PYRAMID_PLUNDER_ROOM_DATA,
    pyramid_plunder_extra_items_as_dict,
)
from ankiscape.logic.pyramid_plunder_logic import (
    _room_bundle,
    _stackable_names,
    apply_pyramid_plunder_review_pure,
    enter_pyramid_plunder_pure,
    leave_pyramid_plunder_pure,
    pyramid_plunder_locked_reasons_pure,
    pyramid_plunder_view_pure,
    sanitize_pyramid_plunder_state_pure,
    set_pyramid_plunder_priority_pure,
)
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from tests.test_integration_smoke import (
    _install_runtime_fakes,
    _load_addon_as_package,
)


ROOT = Path(__file__).resolve().parents[1]


def _player(**overrides):
    data = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
    data.update(
        {
            "thieving_level": 91,
            "strength_level": 99,
            "runecrafting_level": 99,
            "combat_lifepoints": 990,
        }
    )
    data["quests"]["icthlarins_little_helper"] = {
        "started": True,
        "completed": False,
    }
    data.update(overrides)
    return data


def _entered(**overrides):
    data, ok, info = enter_pyramid_plunder_pure(_player(**overrides))
    if not ok:
        raise AssertionError(info)
    return data


class PyramidPlunderPureTests(unittest.TestCase):
    def test_registry_room_table_and_cadence_contract_are_reachable(self):
        spec = constants.UTILITY_ACTIVITY_DATA[PYRAMID_PLUNDER_ACTIVITY_ID]
        self.assertEqual(spec["surface"], "activities")
        self.assertEqual(spec["skill_requirements"], {"thieving": 21})
        self.assertEqual(PYRAMID_PLUNDER_ROOM_DATA[4]["urn_xp"], 215.0)
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == PYRAMID_PLUNDER_ACTIVITY_ID
        )
        self.assertEqual(row["mode"], "activity_group")
        self.assertEqual(row["source_status"], "sourced_with_fallbacks")
        self.assertIn("up to M rooms", row["multiplier_behavior"])
        self.assertNotIn("Onion", _stackable_names())

    def test_entry_gates_accept_quest_or_charged_sceptre_and_reject_other_sessions(self):
        low = _player(thieving_level=20)
        self.assertIn("Thieving level 21", pyramid_plunder_locked_reasons_pure(low))

        no_quest = _player()
        no_quest["quests"]["icthlarins_little_helper"] = {
            "started": False,
            "completed": False,
        }
        self.assertTrue(pyramid_plunder_locked_reasons_pure(no_quest))
        no_quest["inventory"]["Pharaoh's sceptre (1)"] = 1
        self.assertEqual(pyramid_plunder_locked_reasons_pure(no_quest), ())

        blocked = _player(activity_session={"active_id": "barrows"})
        _same, ok, info = enter_pyramid_plunder_pure(blocked)
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

    def test_entry_builds_slot_accurate_auto_and_advanced_packs(self):
        player = _player()
        player["inventory"].update({"Shark": 8, "Super antipoison (4)": 1})
        entered, ok, info = enter_pyramid_plunder_pure(player)
        self.assertTrue(ok)
        self.assertEqual(info["pack"], {"Shark": 8, "Super antipoison (4)": 1})
        self.assertEqual(pyramid_plunder_view_pure(entered)["pack_slots"], 9)

        advanced = _player()
        advanced["inventory"]["Shark"] = 27
        advanced["carried_advanced_targets"][PYRAMID_PLUNDER_ACTIVITY_ID] = True
        advanced["carried_layout"][PYRAMID_PLUNDER_ACTIVITY_ID] = {"Shark": 27}
        entered, ok, info = enter_pyramid_plunder_pure(advanced)
        self.assertTrue(ok)
        self.assertEqual(info["pack"], {"Shark": 27})
        self.assertEqual(pyramid_plunder_view_pure(entered)["pack_slots"], 27)

    def test_priorities_resolve_the_settled_room_bundles(self):
        self.assertEqual(_room_bundle("max_xp", 1, 8), ())
        self.assertEqual(_room_bundle("max_xp", 7, 8), ("urn",) * 13)
        self.assertEqual(_room_bundle("balanced", 6, 8), ("chest",))
        self.assertEqual(
            _room_bundle("balanced", 7, 8),
            ("chest",) + ("urn",) * 13,
        )
        self.assertEqual(
            _room_bundle("treasure", 8, 8),
            ("chest", "sarcophagus", "engraved"),
        )

    def test_multiplier_resolves_rooms_and_stops_at_natural_completion(self):
        entered = _entered()
        rolls = itertools.cycle((0.25, 0.99, 0.99, 0.99))
        updated, result = apply_pyramid_plunder_review_pure(
            entered, lambda: next(rolls), rooms=20
        )
        self.assertTrue(result["terminal"])
        self.assertTrue(result["completed"])
        self.assertEqual(result["rooms_completed"], 8)
        self.assertEqual(updated["pyramid_plunder_runs_completed"], 1)
        self.assertEqual(updated["activity_session"], {"active_id": ""})
        self.assertEqual(result["xp"]["thieving"], 20870.0)

    def test_multiplier_matches_two_sequential_room_transactions(self):
        entered = _entered()
        entered["pyramid_plunder"]["room"] = 7
        values = tuple(itertools.islice(itertools.cycle((0.25, 0.99, 0.99, 0.99)), 104))
        batched_rolls = iter(values)
        batched, batched_result = apply_pyramid_plunder_review_pure(
            entered,
            lambda: next(batched_rolls),
            rooms=2,
        )

        sequential_rolls = iter(values)
        first, first_result = apply_pyramid_plunder_review_pure(
            entered,
            lambda: next(sequential_rolls),
        )
        sequential, second_result = apply_pyramid_plunder_review_pure(
            first,
            lambda: next(sequential_rolls),
        )
        self.assertEqual(batched, sequential)
        self.assertEqual(
            batched_result["xp"]["thieving"],
            first_result["xp"]["thieving"] + second_result["xp"]["thieving"],
        )
        self.assertTrue(second_result["terminal"])

    def test_scarab_damage_poison_and_carried_antipoison_share_combat_state(self):
        player = _player(pyramid_plunder_priority="balanced")
        player["inventory"]["Super antipoison (4)"] = 1
        entered, ok, _info = enter_pyramid_plunder_pure(player)
        self.assertTrue(ok)
        updated, result = apply_pyramid_plunder_review_pure(entered, lambda: 0.0)
        self.assertEqual(result["xp"]["thieving"], 50.0)
        self.assertEqual(result["hazards"][0]["source"], "pyramid_plunder_scarab")
        self.assertEqual(result["hazards"][0]["poison"], 38)
        self.assertEqual(result["hazards"][0]["antipoison"], "Super antipoison (4)")
        self.assertNotIn("poison", updated["combat_status_effects"])
        self.assertIn("poison_immunity", updated["combat_status_effects"])
        self.assertEqual(updated["inventory"]["Super antipoison (3)"], 1)

    def test_death_uses_grave_and_ends_the_run(self):
        player = _player(
            pyramid_plunder_priority="balanced",
            combat_lifepoints=30,
        )
        player["inventory"]["Shark"] = 2
        entered, ok, _info = enter_pyramid_plunder_pure(player)
        self.assertTrue(ok)
        updated, result = apply_pyramid_plunder_review_pure(entered, lambda: 0.0)
        self.assertTrue(result["died"])
        self.assertTrue(result["terminal"])
        self.assertEqual(updated["pyramid_plunder"], {})
        self.assertEqual(updated["activity_session"], {"active_id": ""})
        self.assertEqual(updated["combat_grave"]["items"], ["Shark", "Shark"])
        self.assertGreater(updated["combat_grave"]["reviews_remaining"], 0)
        self.assertIn("sent to grave", updated["pyramid_plunder_last_result"])

    def test_pharaoh_sceptre_banks_directly_and_immediately_expels(self):
        entered = _entered(pyramid_plunder_priority="balanced")
        rolls = iter((0.99, 0.0))
        updated, result = apply_pyramid_plunder_review_pure(
            entered, lambda: next(rolls)
        )
        self.assertTrue(result["terminal"])
        self.assertIn("expelled", result["reason"])
        self.assertEqual(updated["inventory"]["Pharaoh's sceptre (3)"], 1)
        self.assertEqual(result["outputs"], {"Pharaoh's sceptre (3)": 1})

    def test_retained_loot_fills_the_last_slot_and_banks_the_haul(self):
        player = _player(pyramid_plunder_priority="treasure")
        player["inventory"]["Shark"] = 27
        player["carried_advanced_targets"][PYRAMID_PLUNDER_ACTIVITY_ID] = True
        player["carried_layout"][PYRAMID_PLUNDER_ACTIVITY_ID] = {"Shark": 27}
        entered, ok, _info = enter_pyramid_plunder_pure(player)
        self.assertTrue(ok)
        rolls = iter((0.99, 0.99, 0.0, 0.0))
        updated, result = apply_pyramid_plunder_review_pure(
            entered, lambda: next(rolls)
        )
        self.assertTrue(result["terminal"])
        self.assertIn("inventory filled", result["reason"])
        self.assertEqual(updated["inventory"]["Pottery scarab"], 1)
        self.assertNotIn(
            PYRAMID_PLUNDER_ACTIVITY_ID,
            updated["carried_inventory"],
        )

    def test_priority_and_leave_are_direct_commands_with_sanitized_persistence(self):
        player, result = apply_agility_command_pure(
            _player(),
            "set_pyramid_plunder_priority",
            {"priority": "treasure"},
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(player["pyramid_plunder_priority"], "treasure")
        player, result = apply_agility_command_pure(
            player, "enter_pyramid_plunder", {}
        )
        self.assertTrue(result["allowed"])
        unchanged, result = apply_agility_command_pure(
            player,
            "set_pyramid_plunder_priority",
            {"priority": "max_xp"},
        )
        self.assertFalse(result["allowed"])
        self.assertEqual(unchanged["pyramid_plunder"]["priority"], "treasure")
        left, result = apply_agility_command_pure(
            player, "leave_pyramid_plunder", {}
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(left["pyramid_plunder"], {})

        migrated = migrate_loaded_data(
            {
                "config_version": 60,
                "pyramid_plunder": {"room": 99, "max_room": 3, "priority": "bad"},
                "activity_session": {"active_id": ""},
            },
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["pyramid_plunder"]["room"], 3)
        self.assertEqual(migrated["pyramid_plunder"]["priority"], "max_xp")
        self.assertEqual(
            migrated["activity_session"],
            {"active_id": PYRAMID_PLUNDER_ACTIVITY_ID},
        )
        self.assertEqual(
            sanitize_pyramid_plunder_state_pure(migrated),
            sanitize_pyramid_plunder_state_pure(migrated),
        )

    def test_assets_are_period_pinned_reachable_and_normalized(self):
        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        expected = {
            "activityicons/pyramid_plunder.png",
            *{
                f"activityitems/{'_'.join(__import__('re').findall(r'[a-z0-9]+', name.lower()))}.png"
                for name in pyramid_plunder_extra_items_as_dict()
            },
        }
        for relative in expected:
            with self.subTest(relative=relative):
                path = ROOT / relative
                self.assertTrue(path.exists())
                self.assertIn(relative, provenance)
                self.assertLessEqual(provenance[relative]["timestamp"], "2012-11-20T23:59:59Z")
                header = path.read_bytes()[:26]
                self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
                width, height, bit_depth, color_type = struct.unpack(
                    ">IIBB",
                    header[16:26],
                )
                self.assertEqual((bit_depth, color_type), (8, 6))
                self.assertLessEqual(max(width, height), 64)


class PyramidPlunderHookTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_good_answer_awards_three_room_bundle_once(self):
        addon = _load_addon_as_package("ankiscape_pyramid_plunder_hook")
        logic = sys.modules[f"{addon.__name__}.logic.pyramid_plunder_logic"]
        player = _player()
        player, ok, _info = logic.enter_pyramid_plunder_pure(player)
        self.assertTrue(ok)
        addon._state.player_data = player
        addon._state.current_skill = "Utility / Activities"
        addon._state.exp_awarded = False
        addon._review_action_multiplier = lambda: 3
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda _amount: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        addon._remember_review_award_snapshot = lambda _before: None
        before = float(addon._state.player_data["thieving_exp"])
        with patch.object(addon.random, "random", return_value=0.99):
            addon.on_good_answer()
        self.assertEqual(addon._state.player_data["pyramid_plunder"]["room"], 4)
        self.assertEqual(addon._state.player_data["thieving_exp"] - before, 230.0)


if __name__ == "__main__":
    unittest.main()
