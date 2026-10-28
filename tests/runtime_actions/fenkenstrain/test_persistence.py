"""Real Answer Card/Undo hooks and JSON-backed collection persistence."""
import copy
import random
import sys
from types import SimpleNamespace
import unittest

from . import support as s
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _DummyMW, _install_runtime_fakes, _load_addon_as_package


class PersistenceTest(unittest.TestCase):
    def _setup_addon(self):
        _install_runtime_fakes()
        addon = _load_addon_as_package("ankiscape_fenkenstrain_stage_two_e2e")
        collection = s._JsonCollection()
        addon.mw = _DummyMW(collection)
        storage = sys.modules[f"{addon.__name__}.core.storage"]
        storage.mw = addon.mw
        addon.storage_save_player_data = storage.save_player_data
        addon.storage_load_player_data = storage.load_player_data
        addon.ui.update_menu_visibility = lambda *_args: None
        addon.show_error_message = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._show_exp = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        sys.modules[f"{addon.__name__}.core.logic"].show_level_up_dialog = lambda *_args: None
        player = s._at_stage_two(Spade=1, Coins=50, **{"Air rune": 1, "Law rune": 1})
        player["current_magic"] = s.BRAIN_CAST
        addon._state.player_data = player
        addon._state.review_undo_stack.clear()
        addon.save_player_data()
        addon.load_player_data()
        return addon, collection

    def _assert_reopen(self, addon, collection, after):
        self.assertEqual(collection._store["ankiscape_player_data"], s.json.dumps(after))
        saved = collection.get_config("ankiscape_player_data")
        self.assertEqual({key for key in after if saved[key] != after[key]}, s.JSON_LIST_FIELDS)
        self.assertEqual({key: (saved[key], after[key]) for key in s.JSON_LIST_FIELDS},
                         dict.fromkeys(s.JSON_LIST_FIELDS, ([], ())))
        addon._state.player_data = {}
        addon._state.current_skill = "None"
        addon.load_player_data()
        self.assertEqual(addon._state.player_data, after)

    def _assert_review_undo_replay(self, addon, collection, skill, expected_delta, progress):
        addon._state.current_skill = skill
        addon.save_player_data()
        before = copy.deepcopy(addon._state.player_data)
        before_config = copy.deepcopy(collection._store)
        rng = random.getstate()
        _answer_review(addon)
        after = copy.deepcopy(addon._state.player_data)
        after_config = copy.deepcopy(collection._store)
        self.assertEqual(s._delta(before, after), expected_delta)
        self.assertEqual(after["quests"][s.QUEST_ID]["progress"], progress)
        addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(collection._store, before_config)
        random.setstate(rng)
        addon._state.current_skill = skill
        _answer_review(addon)
        self.assertEqual(addon._state.player_data, after)
        self.assertEqual(collection._store, after_config)
        self._assert_reopen(addon, collection, after)

    def _assert_purchase_save_rollback(self, addon, collection):
        before = copy.deepcopy(addon._state.player_data)
        # Match the Shop callback: replace the live dictionary, then the normal save.
        s._commit(addon._state.player_data, s.apply_shop_vendor_action_pure(addon._state.player_data, s.ROAVAR))
        addon.save_player_data()
        bought = copy.deepcopy(addon._state.player_data)
        self.assertEqual(s._delta(before, bought), s.BRAIN_PURCHASE)
        self._assert_reopen(addon, collection, bought)
        event_id = addon._state.player_data["shop_events"][-1]["event_id"]
        s._commit(addon._state.player_data, s.rollback_shop_event_pure(addon._state.player_data, event_id))
        addon.save_player_data()
        rolled_back = copy.deepcopy(addon._state.player_data)
        self.assertEqual(s._delta(bought, rolled_back), {"Coins": 50, "Pickled brain": -1})
        self.assertEqual(rolled_back["inventory"], before["inventory"])
        s._commit(addon._state.player_data, s.apply_shop_vendor_action_pure(addon._state.player_data, s.ROAVAR))
        addon.save_player_data()
        self.assertEqual(addon._state.player_data["inventory"], bought["inventory"])

    def _assert_route(self, route):
        modules, rng = dict(sys.modules), random.getstate()
        try:
            addon, collection = self._setup_addon()
            if route == "magic":
                self._assert_review_undo_replay(addon, collection, "Magic",
                                              {"Air rune": -1, "Law rune": -1, "Pickled brain": 1}, 2)
            else:
                self._assert_purchase_save_rollback(addon, collection)
            self._assert_review_undo_replay(addon, collection, "Quests", s.STAGE_OUTPUTS, 3)
            player = addon._state.player_data
            self.assertEqual(s._brain_casts(player), int(route == "magic"))
            self.assertEqual(player["inventory"]["Coins"], 50 if route == "magic" else 0)
        finally:
            random.setstate(rng)
            sys.modules.clear()
            sys.modules.update(modules)

    def test_both_routes_stage_undo_replay_json_reopen(self):
        for route in ("magic", "shop"):
            with self.subTest(route=route):
                self._assert_route(route)
