import copy
import json
import struct
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import constants
from agility_data import AGILITY_TARGETS
from agility_logic import apply_agility_command_pure
from cadence_coverage import cadence_coverage_rows_pure
from logic_pure import equip_item_pure
from storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from werewolf_skullball_data import (
    WEREWOLF_SKULLBALL_ACTIVITY_ID,
    WEREWOLF_SKULLBALL_RING_ITEMS,
    werewolf_skullball_extra_items_as_dict,
)
from werewolf_skullball_logic import (
    apply_werewolf_skullball_review_pure,
    enter_werewolf_skullball_pure,
    set_werewolf_skullball_policy_pure,
    werewolf_skullball_locked_reasons_pure,
    werewolf_skullball_view_pure,
)


ROOT = Path(__file__).resolve().parents[1]


def _player(**overrides):
    data = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
    data.update({"agility_level": 25, "equipment": {"ring": "Ring of Charos"}})
    data["quests"]["creature_of_fenkenstrain"] = {
        "started": True,
        "completed": True,
    }
    data.update(overrides)
    return data


class WerewolfSkullballPureTests(unittest.TestCase):
    def test_activity_registry_and_cadence_own_the_atomic_run(self):
        spec = constants.UTILITY_ACTIVITY_DATA[WEREWOLF_SKULLBALL_ACTIVITY_ID]
        self.assertEqual(spec["surface"], "activities")
        self.assertEqual(spec["skill_requirements"], {"agility": 25})
        self.assertNotIn(
            WEREWOLF_SKULLBALL_ACTIVITY_ID,
            {target.id for target in AGILITY_TARGETS},
        )
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == WEREWOLF_SKULLBALL_ACTIVITY_ID
        )
        self.assertEqual(row["mode"], "activity_group")
        self.assertEqual(row["source_status"], "sourced_with_disclosed_translation")
        self.assertIn("cannot begin a second run", row["multiplier_behavior"])

    def test_entry_requires_level_quest_and_equipped_ring(self):
        self.assertIn(
            "Agility level 25",
            werewolf_skullball_locked_reasons_pure(_player(agility_level=24)),
        )
        no_quest = _player()
        no_quest["quests"]["creature_of_fenkenstrain"]["completed"] = False
        self.assertIn(
            "complete Creature of Fenkenstrain",
            werewolf_skullball_locked_reasons_pure(no_quest),
        )
        inventory_only = _player(equipment={})
        inventory_only["inventory"]["Ring of Charos"] = 1
        self.assertIn(
            "equip a Ring of Charos",
            werewolf_skullball_locked_reasons_pure(inventory_only),
        )
        for ring in (*WEREWOLF_SKULLBALL_RING_ITEMS, "Ring of Charos (a)"):
            with self.subTest(ring=ring):
                self.assertEqual(
                    werewolf_skullball_locked_reasons_pure(
                        _player(equipment={"ring": ring})
                    ),
                    (),
                )

    def test_entry_rejects_another_persistent_activity(self):
        _same, ok, info = enter_werewolf_skullball_pure(
            _player(activity_session={"active_id": "barrows"})
        )
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

    def test_source_presets_complete_ten_goals_for_full_xp(self):
        expected = {
            "careful": (30, {"T": 14, "K": 5, "S": 11}),
            "balanced": (29, {"T": 13, "K": 4, "S": 12}),
            "fast": (27, {"T": 10, "K": 4, "S": 13}),
        }
        for route, (length, counts) in expected.items():
            with self.subTest(route=route):
                player, ok, _info = set_werewolf_skullball_policy_pure(
                    _player(), {"automation_mode": "casual", "route": route}
                )
                self.assertTrue(ok)
                player, ok, _info = enter_werewolf_skullball_pure(player)
                self.assertTrue(ok)
                updated, result = apply_werewolf_skullball_review_pure(player)
                self.assertEqual(result["xp"], 750.0)
                self.assertEqual(len(result["plan"]), length)
                self.assertEqual(result["move_counts"], counts)
                self.assertEqual(updated["werewolf_skullball"], {})
                self.assertEqual(updated["activity_session"], {"active_id": ""})
                self.assertEqual(updated["agility_activity_completions"]["skullball"], 1)

    def test_advanced_plan_uses_disclosed_move_count_decay(self):
        plan = " ".join(("T",) * 31)
        player, ok, _info = set_werewolf_skullball_policy_pure(
            _player(),
            {"automation_mode": "advanced", "route": "balanced", "advanced_plan": plan},
        )
        self.assertTrue(ok)
        player, ok, _info = enter_werewolf_skullball_pure(player)
        self.assertTrue(ok)
        _updated, result = apply_werewolf_skullball_review_pure(player)
        self.assertEqual(result["xp"], 742.0)
        self.assertEqual(result["route"], "custom")

        _same, ok, info = set_werewolf_skullball_policy_pure(
            _player(),
            {"automation_mode": "advanced", "route": "balanced", "advanced_plan": "T X S"},
        )
        self.assertFalse(ok)
        self.assertIn("10–80", info["reason"])

    def test_direct_commands_freeze_policy_and_leave_cleanly(self):
        player, result = apply_agility_command_pure(
            _player(),
            "set_werewolf_skullball_policy",
            {"automation_mode": "casual", "route": "fast"},
        )
        self.assertTrue(result["allowed"])
        player, result = apply_agility_command_pure(
            player, "enter_werewolf_skullball", {}
        )
        self.assertTrue(result["allowed"])
        frozen, result = apply_agility_command_pure(
            player,
            "set_werewolf_skullball_policy",
            {"automation_mode": "casual", "route": "careful"},
        )
        self.assertFalse(result["allowed"])
        self.assertEqual(werewolf_skullball_view_pure(frozen)["route"], "fast")
        left, result = apply_agility_command_pure(
            player, "leave_werewolf_skullball", {}
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(left["activity_session"], {"active_id": ""})

    def test_v62_migration_moves_selection_and_resets_only_partial_run(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 61,
                "current_agility": WEREWOLF_SKULLBALL_ACTIVITY_ID,
                "agility_activity_state": {
                    "skullball": {"goals": 6, "attempts": 9}
                },
                "agility_activity_completions": {"skullball": 4},
            },
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertNotEqual(migrated["current_agility"], WEREWOLF_SKULLBALL_ACTIVITY_ID)
        self.assertEqual(migrated["current_utility"], WEREWOLF_SKULLBALL_ACTIVITY_ID)
        self.assertNotIn("skullball", migrated["agility_activity_state"])
        self.assertEqual(migrated["agility_activity_completions"]["skullball"], 4)
        self.assertIn("partial Skullball run reset", migrated["werewolf_skullball_last_result"])

    def test_ring_equipment_and_assets_are_period_pinned_and_normalized(self):
        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        expected = {
            "activityicons/werewolf_skullball.png",
            "activityitems/ring_of_charos.png",
            "activityitems/ring_of_charos_a.png",
            "activityitems/ring_of_charos_a_i.png",
        }
        self.assertEqual(set(werewolf_skullball_extra_items_as_dict()), set(WEREWOLF_SKULLBALL_RING_ITEMS))
        for item_name in WEREWOLF_SKULLBALL_RING_ITEMS:
            self.assertEqual(constants.EQUIPMENT_ITEM_DATA[item_name]["slot"], "ring")
            inventory, equipment, equipped = equip_item_pure(
                item_name,
                {item_name: 1},
                {},
                constants.EQUIPMENT_DATA,
            )
            self.assertTrue(equipped)
            self.assertEqual(equipment, {"ring": item_name})
            self.assertEqual(inventory[item_name], 0)
        for relative in expected:
            with self.subTest(relative=relative):
                path = ROOT / relative
                self.assertTrue(path.exists())
                self.assertIn(relative, provenance)
                self.assertLessEqual(provenance[relative]["timestamp"], "2012-11-20T23:59:59Z")
                header = path.read_bytes()[:26]
                self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
                width, height, bit_depth, color_type = struct.unpack(">IIBB", header[16:26])
                self.assertEqual((bit_depth, color_type), (8, 6))
                self.assertLessEqual(max(width, height), 64)


class WerewolfSkullballHookTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_one_answer_completes_one_run_once_and_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_skullball_hook")
        logic = sys.modules[f"{addon.__name__}.werewolf_skullball_logic"]
        player, ok, _info = logic.enter_werewolf_skullball_pure(_player())
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
        before_xp = float(before["agility_exp"])
        with patch.object(addon.random, "random", side_effect=AssertionError("Skullball must not draw RNG")):
            addon.on_good_answer(before)
        self.assertEqual(addon.player_data["agility_exp"] - before_xp, 750.0)
        self.assertEqual(addon.player_data["werewolf_skullball_runs_completed"], 1)
        self.assertEqual(addon.player_data["werewolf_skullball"], {})

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon.player_data, before)


if __name__ == "__main__":
    unittest.main()
