"""Tribal Totem reviews complete the opening before taking the address label."""

import copy
import random
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_quest import quest_locked_reasons_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _install_runtime_fakes,
    _load_addon_as_package,
)
from tests.test_runtime_actions import _context


QUEST_ID = "tribal_totem"
OPENING_ACTIONS = (
    "Agree to recover the stolen Rantuki totem for Kangai Mau",
    "Reach Handelmort Mansion in East Ardougne",
    "Attempt to enter Handelmort Mansion",
    "Ask Horacio about Handelmort Mansion security",
    "Ask Wizard Cromperty about the teleportation block",
    "Request Wizard Cromperty's initial crate teleport to locate the RPDT block",
)
RPDT_ACTIONS = (
    "Reach the Ardougne RPDT depot",
    "Take Lord Handelmort's address label from the RPDT crate",
)


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(current_quest=QUEST_ID, thieving_level=21)
    player["inventory"].update({"Coins": 0, "Tinderbox": 1, "Lobster": 4})
    player["equipment"]["weapon"] = "Bronze sword"
    player["quests"]["rune_mysteries"] = {"started": True, "progress": 2, "completed": False}
    return player


class TribalTotemOpeningTest(unittest.TestCase):
    def test_thieving_twenty_refuses_before_any_opening_action_or_save(self):
        player = _player()
        player["thieving_level"] = 20
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        with patch.object(
            quest_action_proofs, "quest_action_proofs_after_event_pure",
            wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
        ) as events:
            self.assertEqual(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA), ("Thieving 21",))
            self.assertFalse(handle_quest_answer(_context(player, calls)))
        self.assertEqual(events.call_args_list, [])
        self.assertEqual(player, before)
        self.assertEqual(calls["saves"], 0)
        self.assertEqual(calls["xp"], [])

    def test_opening_completes_all_six_actions_without_a_fee_or_future_items(self):
        player = _player()
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        with patch.object(
            quest_action_proofs, "quest_action_proofs_after_event_pure",
            wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
        ) as events:
            self.assertTrue(handle_quest_answer(_context(player, calls)))
        self.assertEqual(
            [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"],
            [f"{QUEST_ID}:{action}" for action in OPENING_ACTIONS],
        )
        self.assertEqual(player["quest_action_proofs"], sorted(OPENING_ACTIONS))
        self.assertEqual(player["quests"][QUEST_ID], {"started": True, "progress": 2, "completed": False})
        self.assertEqual(player["inventory"], before["inventory"])
        self.assertEqual(player["equipment"], before["equipment"])
        self.assertEqual({key: value for key, value in player.items() if key.endswith("_exp")},
                         {key: value for key, value in before.items() if key.endswith("_exp")})
        self.assertEqual(player["quest_points"], before["quest_points"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 1)

    def test_genuine_review_control_undo_replay_reopen_and_next_stage(self):
        original_modules = dict(sys.modules)
        original_random_state = random.getstate()
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_tribal_totem_e2e")
            collection = _DummyCol()
            collection.set_config = lambda key, value: collection._store.__setitem__(key, copy.deepcopy(value))
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
            addon._state.player_data = _player()
            addon._state.current_skill = "None"
            addon._state.review_undo_stack.clear()
            addon.check_achievements(addon._state.player_data)
            addon.save_player_data()
            addon.load_player_data()
            addon.save_player_data()
            before = copy.deepcopy(addon._state.player_data)
            before_config = copy.deepcopy(collection._store)
            review_random_state = random.getstate()
            _answer_review(addon)
            control = copy.deepcopy(addon._state.player_data)
            control_config = copy.deepcopy(collection._store)
            self.assertEqual(control["quests"], before["quests"])
            self.assertEqual(control["quest_action_proofs"], before["quest_action_proofs"])
            self.assertNotEqual(control, before)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store, before_config)
            addon._state.current_skill = "Quests"
            addon.save_player_data()
            quest_before_config = copy.deepcopy(collection._store)
            random.setstate(review_random_state)
            proofs = sys.modules[f"{addon.__name__}.logic_pure.quest_action_proofs"]
            with patch.object(
                proofs, "quest_action_proofs_after_event_pure",
                wraps=proofs.quest_action_proofs_after_event_pure,
            ) as events:
                _answer_review(addon)
            self.assertEqual(
                [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"],
                [f"{QUEST_ID}:{action}" for action in OPENING_ACTIONS],
            )
            after = copy.deepcopy(addon._state.player_data)
            expected = copy.deepcopy(control)
            expected["quests"][QUEST_ID] = {"started": True, "progress": 2, "completed": False}
            expected["quest_action_proofs"] = sorted(OPENING_ACTIONS)
            expected["action_telemetry"]["actions"][f"quest:{QUEST_ID}"] = {
                "skill_id": "quest", "action_id": QUEST_ID, "attempts": 1,
                "successes": 1, "failures": 0, "expected_successes": 1.0,
                "current_dry_streak": 0, "longest_dry_streak": 0, "outputs": {},
                "failure_kinds": {}, "last_success": True, "last_expected_success_chance": 1.0,
            }
            expected["achievement_progress"]["skills"]["quest"] = {"actions": {QUEST_ID: 1}, "outputs": {}}
            self.assertEqual(after, expected)
            expected_config = copy.deepcopy(control_config)
            expected_config["ankiscape_player_data"] = expected
            expected_config["ankiscape_current_skill"] = "Quests"
            self.assertEqual(collection._store, expected_config)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store, quest_before_config)
            random.setstate(review_random_state)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, after)
            self.assertEqual(collection._store, expected_config)
            addon._state.player_data = {}
            addon._state.current_skill = "None"
            addon.load_player_data()
            self.assertEqual(addon._state.player_data, after)
            self.assertEqual(addon._state.current_skill, "Quests")
            self.assertEqual(collection._store, expected_config)
            with patch.object(
                proofs, "quest_action_proofs_after_event_pure",
                wraps=proofs.quest_action_proofs_after_event_pure,
            ) as events:
                _answer_review(addon)
            self.assertEqual(
                [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"],
                [f"{QUEST_ID}:{action}" for action in RPDT_ACTIONS],
            )
            self.assertEqual(addon._state.player_data["quests"][QUEST_ID],
                             {"started": True, "progress": 3, "completed": False})
            self.assertEqual(addon._state.player_data["quest_action_proofs"], sorted(OPENING_ACTIONS + RPDT_ACTIONS))
            self.assertEqual(addon._state.player_data["inventory"], {**after["inventory"], "Address label": 1})
            self.assertEqual(collection.get_config("ankiscape_player_data"), addon._state.player_data)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, after)
            self.assertEqual(collection._store, expected_config)
        finally:
            random.setstate(original_random_state)
            sys.modules.clear()
            sys.modules.update(original_modules)
