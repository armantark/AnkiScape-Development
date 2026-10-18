"""A real Bank hatchet attachment earns My Axe Is My Buddy, with Undo and storage."""

import copy
import json
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.logic import check_achievements
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.core.tool_belt import tool_on_belt
from ankiscape.logic.achievement_diary_logic import diary_tier_by_id_pure
from ankiscape.logic.shop_logic import apply_shop_buy_pure
from ankiscape.runtime.runtime_actions import handle_thieving_answer
from tests.test_achievement_diary_ledger_wiring import _runtime_context
from tests.test_direct_action_undo_seam import _FakeCollection
from tests.test_integration_smoke import _DummyMW, _install_runtime_fakes, _load_addon_as_package
from tests.runtime_actions.test_sawmill_plank_diary import _JsonCollection


TASK_ID = "burthorpe_period_my_axe_is_my_buddy"


class ToolBeltDiaryTest(unittest.TestCase):
    def setUp(self):
        self.original_modules = dict(sys.modules)
        self.addCleanup(self._restore_modules)
        _install_runtime_fakes()
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.collection = _JsonCollection(self.directory.name)
        self.collection.add_custom_undo_entry = _FakeCollection().add_custom_undo_entry
        sys.modules["aqt"].mw = _DummyMW(self.collection)
        self.addon = _load_addon_as_package("ankiscape_tool_belt_diary")
        self.addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.addon._state.current_skill = "Mining"
        self.errors = []
        self.addon.show_error_message = lambda title, message: self.errors.append((title, message))
        popups = patch.object(sys.modules[f"{self.addon.__name__}.core.logic"], "_popups_enabled", return_value=False)
        popups.start()
        self.addCleanup(popups.stop)

    def _restore_modules(self):
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def _earn_hatchet(self, item="Iron hatchet", row="bobs_brilliant_axes:1:1349", reviews=19):
        player = self.addon._state.player_data
        player["current_thieving"] = "pickpocket_man"
        coins = player["inventory"].get("Coins", 0)
        for _ in range(reviews):
            errors = []
            self.assertTrue(handle_thieving_answer(_runtime_context(player, errors, (0.0,) + (0.99,) * 7)))
            self.assertEqual(errors, [])
        self.assertEqual(player["inventory"]["Coins"], coins + 3 * reviews)
        player, result = apply_shop_buy_pure(player, "bobs_brilliant_axes", row)
        self.assertTrue(result["allowed"], result)
        self.assertEqual(player["inventory"][item], 1)
        self.addon._state.player_data = player

    def _assert_deed(self, player, count):
        self.assertEqual(player["achievement_diaries"]["completed_tasks"].count(TASK_ID), count)
        _family, tier = diary_tier_by_id_pure("burthorpe_period")
        task = next(task for task in tier.tasks if task.id == TASK_ID)
        self.assertTrue(task.conditions, "source 561 must have a live event condition")
        token = task.conditions[0].key.rsplit(".", 1)[-1]
        self.assertEqual(player["achievement_diaries"]["event_counts"].get(token, 0), count)

    def test_earned_attachment_saves_reloads_undoes_and_replays_once(self):
        self._earn_hatchet()
        addon = self.addon
        addon.save_player_data()
        before = copy.deepcopy(addon._state.player_data)
        self._assert_deed(before, 0)
        self.assertTrue(addon.on_attach_tool("Iron hatchet"))
        self.assertEqual(self.errors, [])
        self.assertNotIn("Iron hatchet", addon._state.player_data["inventory"])
        self.assertIn("iron_hatchet", addon._state.player_data["toolbelt"]["woodcutting"])
        self._assert_deed(addon._state.player_data, 1)
        loaded, skill = addon.storage_load_player_data()
        self.assertEqual(skill, "Mining")
        self._assert_deed(loaded, 1)
        self.assertEqual(loaded["toolbelt"], addon._state.player_data["toolbelt"])
        addon._on_state_did_undo(SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, before)
        undone, _ = addon.storage_load_player_data()
        expected = migrate_loaded_data(json.loads(json.dumps(before)), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(undone, expected)
        self.assertTrue(addon.on_attach_tool("Iron hatchet"))
        replayed, _ = addon.storage_load_player_data()
        self._assert_deed(replayed, 1)
        before_refusal = copy.deepcopy(addon._state.player_data)
        saved = self.collection.path.read_bytes()
        self.assertFalse(addon.on_attach_tool("Iron hatchet"))
        self.assertEqual(addon._state.player_data, before_refusal)
        self.assertEqual(self.collection.path.read_bytes(), saved)
        self._earn_hatchet("Steel hatchet", "bobs_brilliant_axes:2:1353", 67)
        self.assertTrue(addon.on_attach_tool("Steel hatchet"))
        self._assert_deed(addon._state.player_data, 1)
        retained, _ = addon.storage_load_player_data()
        self._assert_deed(retained, 1)

    def test_seeded_belt_and_other_tool_updates_cannot_backfill_the_deed(self):
        addon = self.addon
        player = addon._state.player_data
        player["toolbelt"]["woodcutting"] = ("bronze_hatchet", "iron_hatchet")
        player["inventory"].update({"Iron pickaxe": 1, "Chain link mould": 1})
        check_achievements(player)
        loaded = migrate_loaded_data(json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS)
        check_achievements(loaded)
        self._assert_deed(loaded, 0)
        self.assertTrue(addon.on_attach_tool("Iron pickaxe"))
        self.assertTrue(addon.on_attach_tool("Chain link mould"))
        self._assert_deed(addon._state.player_data, 0)
        before = copy.deepcopy(addon._state.player_data)
        saved = self.collection.path.read_bytes()
        for tool in ("Iron hatchet", "Knife", "Tinderbox", "Rune hatchet"):
            self.assertFalse(addon.on_attach_tool(tool))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(self.collection.path.read_bytes(), saved)

    def test_non_weapon_equip_does_not_complete_or_save_the_gauntlets_deed(self):
        addon = self.addon
        player = addon._state.player_data
        player["inventory"].update({"Spiked gauntlets": 1, "Iron pickaxe": 1, "Chain link mould": 1})
        task = "burthorpe_period_these_aren_t_oven_gloves"
        self.assertIsNone(player["equipment"].get("weapon"))
        self.assertNotIn(task, player["achievement_diaries"]["completed_tasks"])
        self.assertTrue(addon.on_equip_item("Spiked gauntlets"))
        self.assertEqual(self.errors, [])
        self.assertEqual(player["equipment"]["hands"], "Spiked gauntlets")
        self.assertIsNone(player["equipment"].get("weapon"))
        self.assertNotIn(task, player["achievement_diaries"]["completed_tasks"])
        for tool in (None, "Iron pickaxe", "Chain link mould"):
            if tool is not None:
                self.assertTrue(addon.on_attach_tool(tool))
            loaded, _ = addon.storage_load_player_data()
            self.assertEqual(loaded["equipment"], player["equipment"])
            self.assertNotIn(task, addon._state.player_data["achievement_diaries"]["completed_tasks"])
            self.assertNotIn(task, loaded["achievement_diaries"]["completed_tasks"])

    def test_knife_and_tinderbox_are_present_without_any_saved_belt_state(self):
        for player in ({}, {"toolbelt": {}, "toolbelt_added": []}):
            for tool in ("Knife", "Tinderbox"):
                with self.subTest(player=player, tool=tool):
                    self.assertTrue(tool_on_belt(player, tool))

    def test_undo_entry_refusal_cannot_record_or_save_a_successful_pure_attachment(self):
        self._earn_hatchet()
        addon = self.addon
        addon.save_player_data()
        before = copy.deepcopy(addon._state.player_data)
        saved = self.collection.path.read_bytes()
        self.collection.add_custom_undo_entry = _FakeCollection(accepts=False).add_custom_undo_entry
        self.assertFalse(addon.on_attach_tool("Iron hatchet"))
        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(self.collection.path.read_bytes(), saved)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self._assert_deed(addon._state.player_data, 0)


if __name__ == "__main__":
    unittest.main()
