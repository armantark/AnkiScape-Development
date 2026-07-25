import copy
import json
import struct
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core import constants
from ankiscape.data.agility_data import AGILITY_TARGETS
from ankiscape.logic.agility_logic import apply_agility_command_pure
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.data.gnome_ball_data import GNOME_BALL_ACTIVITY_ID
from ankiscape.logic.gnome_ball_logic import (
    apply_gnome_ball_review_pure,
    enter_gnome_ball_pure,
    gnome_ball_locked_reasons_pure,
    gnome_ball_tackle_chance_pure,
    leave_gnome_ball_pure,
)
from ankiscape.logic_pure.logic_pure import equip_item_pure
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


ROOT = Path(__file__).resolve().parents[1]


def _player(**overrides):
    data = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
    data.update({"agility_level": 1, "equipment": {}})
    data.update(overrides)
    return data


def _complete(player, roll=1.0):
    current, ok, _info = enter_gnome_ball_pure(player)
    if not ok:
        raise AssertionError("test setup could not enter Gnome Ball")
    results = []
    for _beat in range(3):
        current, result = apply_gnome_ball_review_pure(current, roll)
        results.append(result)
    return current, results


class GnomeBallPureTests(unittest.TestCase):
    def test_activity_registry_and_cadence_own_three_match_beats(self):
        spec = constants.UTILITY_ACTIVITY_DATA[GNOME_BALL_ACTIVITY_ID]
        self.assertEqual(spec["surface"], "activities")
        self.assertEqual(spec["skill_requirements"], {})
        self.assertNotIn(
            GNOME_BALL_ACTIVITY_ID,
            {target.id for target in AGILITY_TARGETS},
        )
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == GNOME_BALL_ACTIVITY_ID
        )
        self.assertEqual(row["mode"], "source_blocked_activity")
        self.assertEqual(row["source_status"], "source_blocked")
        self.assertIn("terminal fifth goal", row["multiplier_behavior"])

    def test_entry_only_rejects_a_non_gnomeball_weapon_or_another_activity(self):
        self.assertEqual(gnome_ball_locked_reasons_pure(_player()), ())
        self.assertEqual(
            gnome_ball_locked_reasons_pure(
                _player(equipment={"weapon": "Gnomeball"})
            ),
            (),
        )
        reasons = gnome_ball_locked_reasons_pure(
            _player(equipment={"weapon": "Bronze sword"})
        )
        self.assertIn("only a Gnomeball is allowed", reasons[0])
        _same, ok, info = enter_gnome_ball_pure(
            _player(activity_session={"active_id": "barrows"})
        )
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

    def test_entry_prepares_auto_or_custom_food_for_the_dangerous_match(self):
        automatic = _player(
            inventory={"Shark": 3, "Lobster": 4},
            combat_auto_eat_food=["Shark", "Lobster"],
        )
        entered, ok, info = enter_gnome_ball_pure(automatic)
        self.assertTrue(ok)
        self.assertEqual(info["pack"], {"Shark": 3, "Lobster": 4})
        self.assertEqual(
            entered["carried_inventory"][GNOME_BALL_ACTIVITY_ID],
            info["pack"],
        )

        custom = _player(
            inventory={"Shark": 3, "Lobster": 4},
            carried_advanced_targets={GNOME_BALL_ACTIVITY_ID: True},
            carried_layout={GNOME_BALL_ACTIVITY_ID: {"Lobster": 2}},
        )
        entered, ok, info = enter_gnome_ball_pure(custom)
        self.assertTrue(ok)
        self.assertEqual(info["pack"], {"Lobster": 2})

    def test_three_beats_pay_period_goal_xp_to_both_skills(self):
        completed, results = _complete(_player())
        self.assertEqual(
            [(row["goals"], row["agility_xp"], row["ranged_xp"]) for row in results],
            [((1, 2), 9.0, 9.0), ((3, 4), 13.0, 13.0), ((5,), 30.0, 30.0)],
        )
        self.assertEqual(completed["gnome_ball"], {})
        self.assertEqual(completed["activity_session"], {"active_id": ""})
        self.assertEqual(completed["gnome_ball_runs_completed"], 1)
        self.assertEqual(completed["agility_activity_completions"]["gnome_ball"], 1)

    def test_tackle_fallback_damages_without_erasing_a_survived_beat(self):
        self.assertAlmostEqual(gnome_ball_tackle_chance_pure(1), 0.20)
        self.assertAlmostEqual(gnome_ball_tackle_chance_pure(99), 0.05)
        entered, ok, _info = enter_gnome_ball_pure(
            _player(combat_lifepoints=100)
        )
        self.assertTrue(ok)
        updated, result = apply_gnome_ball_review_pure(entered, 0.0)
        self.assertTrue(result["tackled"])
        self.assertEqual(result["damage"], 10)
        self.assertEqual(result["goals"], (1, 2))
        self.assertEqual(result["agility_xp"], 9.0)
        self.assertEqual(updated["gnome_ball"]["beat"], 1)

    def test_lethal_tackle_uses_grave_channel_and_aborts_without_xp(self):
        player = _player(
            combat_lifepoints=10,
            equipment={"weapon": "Gnomeball", "head": "Leather cowl"},
        )
        entered, ok, _info = enter_gnome_ball_pure(player)
        self.assertTrue(ok)
        updated, result = apply_gnome_ball_review_pure(entered, 0.0)
        self.assertTrue(result["died"])
        self.assertTrue(result["terminal"])
        self.assertEqual(result["agility_xp"], 0.0)
        self.assertEqual(updated["gnome_ball"], {})
        self.assertEqual(updated["activity_session"], {"active_id": ""})
        self.assertIn("Gnomeball", updated["combat_grave"]["items"])

    def test_referee_checks_carried_not_banked_gnomeballs(self):
        banked = _player()
        banked["inventory"]["Gnomeball"] = 1
        completed, results = _complete(banked)
        self.assertEqual(results[-1]["outputs"], {"Gnomeball": 1})
        self.assertEqual(completed["inventory"]["Gnomeball"], 2)

        carried = _player(
            carried_inventory={GNOME_BALL_ACTIVITY_ID: {"Gnomeball": 1}}
        )
        completed, results = _complete(carried)
        self.assertEqual(results[-1]["outputs"], {})
        self.assertEqual(completed["inventory"]["Gnomeball"], 0)

        equipped, results = _complete(
            _player(equipment={"weapon": "Gnomeball"})
        )
        self.assertEqual(results[-1]["outputs"], {})
        self.assertEqual(equipped["inventory"]["Gnomeball"], 0)

    def test_direct_commands_enter_and_leave_without_awarding_progress(self):
        player, result = apply_agility_command_pure(
            _player(), "enter_gnome_ball", {}
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(player["current_utility"], GNOME_BALL_ACTIVITY_ID)
        left, result = apply_agility_command_pure(
            player, "leave_gnome_ball", {}
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(left["gnome_ball"], {})
        self.assertEqual(left["gnome_ball_runs_completed"], 0)
        self.assertFalse(leave_gnome_ball_pure(left)[1])

    def test_v63_migration_resets_partial_match_and_preserves_completions(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 62,
                "current_agility": GNOME_BALL_ACTIVITY_ID,
                "agility_activity_state": {
                    "gnome_ball": {"goal": 3, "attempts": 7}
                },
                "agility_activity_completions": {"gnome_ball": 4},
            },
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertNotEqual(migrated["current_agility"], GNOME_BALL_ACTIVITY_ID)
        self.assertEqual(migrated["current_utility"], GNOME_BALL_ACTIVITY_ID)
        self.assertNotIn("gnome_ball", migrated["agility_activity_state"])
        self.assertEqual(migrated["agility_activity_completions"]["gnome_ball"], 4)
        self.assertIn("partial Gnome Ball match reset", migrated["gnome_ball_last_result"])

    def test_period_item_is_equippable_and_its_asset_is_normalized(self):
        item = constants.EQUIPMENT_ITEM_DATA["Gnomeball"]
        self.assertEqual(item["slot"], "weapon")
        self.assertEqual(item["source_item_id"], 751)
        inventory, equipment, equipped = equip_item_pure(
            "Gnomeball",
            {"Gnomeball": 1},
            {},
            constants.EQUIPMENT_DATA,
        )
        self.assertTrue(equipped)
        self.assertEqual(inventory["Gnomeball"], 0)
        self.assertEqual(equipment, {"weapon": "Gnomeball"})

        relative = "agilityitems/gnomeball.png"
        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
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


class GnomeBallHookTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_multiplier_finishes_one_match_in_three_draws_and_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_gnome_ball_hook")
        logic = sys.modules[f"{addon.__name__}.logic.gnome_ball_logic"]
        player, ok, _info = logic.enter_gnome_ball_pure(_player())
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
        before_agility = float(before["agility_exp"])
        before_ranged = float(before["ranged_exp"])
        with patch.object(addon.random, "random", side_effect=(0.99, 0.99, 0.99)) as rng:
            addon.on_good_answer(before)
        self.assertEqual(rng.call_count, 3)
        self.assertEqual(addon.player_data["agility_exp"] - before_agility, 52.0)
        self.assertEqual(addon.player_data["ranged_exp"] - before_ranged, 52.0)
        self.assertEqual(addon.player_data["gnome_ball_runs_completed"], 1)
        self.assertEqual(addon.player_data["gnome_ball"], {})

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon.player_data, before)


if __name__ == "__main__":
    unittest.main()
