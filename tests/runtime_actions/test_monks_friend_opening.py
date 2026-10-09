"""Monk's Friend opening reviews acquire the blanket before its return."""

import copy
import random
import sys
from contextlib import contextmanager
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_blockers_pure, start_quest_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _DummyCol, _DummyMW, _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


QUEST_ID = "monks_friend"
OPENING_ACTIONS = (
    "Hear Brother Omad's request to recover the child's stolen blanket",
    "Offer to recover the blanket and ask where the thieves hide",
    "Travel west from the monastery to the stone ring near the Clock Tower",
    "Enter the stone ring to reveal the hidden ladder",
    "Descend into the thieves' hideout",
    "Follow the southern path to the blanket table",
    "Recover the child's blanket from the thieves' hideout",
)


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["current_quest"] = QUEST_ID
    player["inventory"] = {"Coins": 37, "Logs": 2, "Jug of water": 1}
    return player


@contextmanager
def _review_session():
    original_modules = dict(sys.modules)
    original_random = random.getstate()
    try:
        _install_runtime_fakes()
        addon = _load_addon_as_package("ankiscape_monks_friend_opening_e2e")
        collection = _DummyCol()
        collection.set_config = lambda key, value: collection._store.__setitem__(key, copy.deepcopy(value))
        addon.mw = _DummyMW(collection)
        storage = sys.modules[f"{addon.__name__}.core.storage"]
        storage.mw = addon.mw
        addon.storage_save_player_data = storage.save_player_data
        addon.storage_load_player_data = storage.load_player_data
        errors = []
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon.ui.update_menu_visibility = lambda *_args: None
        addon._show_activity_gain = lambda _text: None
        addon._show_exp = lambda _amount: None
        addon.update_review_hud = lambda *_args: None
        addon._state.player_data = _player()
        addon._state.current_skill = "None"
        addon._state.review_undo_stack.clear()
        addon.check_achievements(addon._state.player_data)
        addon.save_player_data()
        addon.load_player_data()
        addon.save_player_data()
        yield addon, collection, errors
    finally:
        random.setstate(original_random)
        sys.modules.clear()
        sys.modules.update(original_modules)


class MonksFriendOpeningTest(unittest.TestCase):
    def test_start_alone_records_no_conversation_travel_or_pickup(self):
        player = _player()
        before = copy.deepcopy(player)
        player, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        before["quests"][QUEST_ID] = {"started": True, "progress": 0, "completed": False}
        self.assertEqual(player, before)
        self.assertFalse(player.get("quest_action_proofs"))
        self.assertEqual(player["inventory"].get("Child's blanket", 0), 0)

    def test_first_review_runs_the_complete_opening_and_recovers_one_blanket(self):
        player = _player()
        inventory = copy.deepcopy(player["inventory"])
        experience = {key: value for key, value in player.items() if key.endswith("_exp")}
        self.assertFalse(player["quests"][QUEST_ID]["started"])
        self.assertFalse(player.get("quest_action_proofs"))
        self.assertEqual(player["inventory"].get("Child's blanket", 0), 0)
        with patch.object(
            quest_action_proofs, "quest_action_proofs_after_event_pure",
            wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
        ) as events:
            self.assertTrue(handle_quest_answer(_context(player)))
        self.assertEqual(
            [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"],
            [f"{QUEST_ID}:{action}" for action in OPENING_ACTIONS],
        )
        self.assertEqual(player["quest_action_proofs"], sorted(OPENING_ACTIONS))
        self.assertEqual(player["quests"][QUEST_ID], {"started": True, "progress": 2, "completed": False})
        self.assertEqual(player["inventory"], {**inventory, "Child's blanket": 1})
        self.assertEqual({key: player[key] for key in experience}, experience)
        self.assertEqual(player["quest_points"], 0)
        self.assertEqual(player["pending_skill_exp_rewards"], {})
        self.assertFalse(player.get("quest_combat_encounters"))
        self.assertFalse(player.get("quest_route_states"))

    def test_missing_blanket_refuses_atomically_and_return_consumes_only_one(self):
        player = _player()
        self.assertTrue(handle_quest_answer(_context(player)))
        player["inventory"]["Child's blanket"] = 0
        before = copy.deepcopy(player)
        blockers = quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA)
        self.assertEqual([(row["kind"], row["reason"]) for row in blockers], [("missing_item", "Needs Child's blanket x1")])
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertFalse(handle_quest_answer(_context(player, calls)))
        self.assertEqual(player, before)
        self.assertEqual(calls["saves"], 0)
        self.assertEqual(calls["errors"], [("Quest blocked", "Monk's Friend is blocked:\n• Needs Child's blanket x1\n\nQuesting has been switched off until this is resolved.")])
        player["inventory"]["Child's blanket"] = 2
        inventory = copy.deepcopy(player["inventory"])
        experience = {key: value for key, value in player.items() if key.endswith("_exp")}
        self.assertTrue(handle_quest_answer(_context(player)))
        inventory["Child's blanket"] = 1
        self.assertEqual(player["inventory"], inventory)
        self.assertEqual(player["quests"][QUEST_ID], {"started": True, "progress": 3, "completed": False})
        self.assertEqual(player["quest_action_proofs"], sorted(OPENING_ACTIONS))
        self.assertEqual({key: player[key] for key in experience}, experience)
        self.assertEqual(player["quest_points"], 0)

    def test_genuine_opening_and_return_match_controls_undo_replay_save_and_reopen(self):
        with _review_session() as (addon, collection, errors):
            before = copy.deepcopy(addon._state.player_data)
            before_config = copy.deepcopy(collection._store)
            review_random = random.getstate()
            _answer_review(addon)
            control = copy.deepcopy(addon._state.player_data)
            control_config = copy.deepcopy(collection._store)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store, before_config)
            addon._state.current_skill = "Quests"
            addon.save_player_data()
            quest_before_config = copy.deepcopy(collection._store)
            random.setstate(review_random)
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
            expected = copy.deepcopy(control)
            expected["quests"][QUEST_ID] = {"started": True, "progress": 2, "completed": False}
            expected["quest_action_proofs"] = sorted(OPENING_ACTIONS)
            expected["inventory"]["Child's blanket"] = 1
            expected["bank_layout"]["items"]["Child's blanket"] = {
                "tab_id": "main", "position": 3, "added_review": 1, "used_review": 1, "quantity": 1,
            }
            expected["action_telemetry"]["actions"][f"quest:{QUEST_ID}"] = {
                "skill_id": "quest", "action_id": QUEST_ID, "attempts": 1, "successes": 1,
                "failures": 0, "expected_successes": 1.0, "current_dry_streak": 0,
                "longest_dry_streak": 0, "outputs": {}, "failure_kinds": {},
                "last_success": True, "last_expected_success_chance": 1.0,
            }
            expected["achievement_progress"]["skills"]["quest"] = {"actions": {QUEST_ID: 1}, "outputs": {}}
            expected_config = copy.deepcopy(control_config)
            expected_config.update(ankiscape_player_data=expected, ankiscape_current_skill="Quests")
            self.assertEqual(addon._state.player_data, expected, errors)
            self.assertEqual(collection._store, expected_config)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store, quest_before_config)
            random.setstate(review_random)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, expected, errors)
            self.assertEqual(collection._store, expected_config)
            addon._state.player_data = {}
            addon._state.current_skill = "None"
            addon.load_player_data()
            self.assertEqual(addon._state.player_data, expected)
            self.assertEqual(addon._state.current_skill, "Quests")
            self.assertEqual(collection._store, expected_config)
            addon._state.current_skill = "None"
            addon.save_player_data()
            return_random = random.getstate()
            _answer_review(addon)
            return_control = copy.deepcopy(addon._state.player_data)
            return_control_config = copy.deepcopy(collection._store)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            addon._state.current_skill = "Quests"
            addon.save_player_data()
            self.assertEqual(addon._state.player_data, expected)
            self.assertEqual(collection._store, expected_config)
            random.setstate(return_random)
            _answer_review(addon)
            returned = copy.deepcopy(return_control)
            returned["quests"][QUEST_ID]["progress"] = 3
            returned["inventory"]["Child's blanket"] = 0
            del returned["bank_layout"]["items"]["Child's blanket"]
            returned["action_telemetry"]["actions"][f"quest:{QUEST_ID}"].update(
                attempts=2, successes=2, expected_successes=2.0,
            )
            returned["achievement_progress"]["skills"]["quest"]["actions"][QUEST_ID] = 2
            returned_config = copy.deepcopy(return_control_config)
            returned_config.update(ankiscape_player_data=returned, ankiscape_current_skill="Quests")
            self.assertEqual(addon._state.player_data, returned, errors)
            self.assertEqual(collection._store, returned_config)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, expected)
            self.assertEqual(collection._store, expected_config)
            random.setstate(return_random)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, returned, errors)
            self.assertEqual(collection._store, returned_config)
            addon._state.player_data = {}
            addon._state.current_skill = "None"
            addon.load_player_data()
            self.assertEqual(addon._state.player_data, returned)
            self.assertEqual(addon._state.current_skill, "Quests")
            self.assertEqual(collection._store, returned_config)
