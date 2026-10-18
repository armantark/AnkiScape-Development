"""Tree Gnome opening reviews stop at Montai's six-log handoff."""

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
from ankiscape.logic_pure.logic_pure_quest import start_quest_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer, handle_woodcutting_answer
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _DummyCol, _DummyMW, _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


QUEST_ID = "tree_gnome_village"
OPENING_ACTIONS = (
    "Navigate the Gnome Maze and squeeze through the village fence",
    "Hear King Bolren's request to recover the stolen Orb of protection",
    "Agree to help King Bolren recover the stolen orb",
    "Follow Elkoy out of the Gnome Maze",
    "Reach Commander Montai on the battlefield",
    "Ask Commander Montai how to help the gnome battlefield",
    "Agree to gather six normal logs for Commander Montai",
)


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["current_quest"] = QUEST_ID
    player["inventory"] = {"Bronze hatchet": 1, "Coins": 37, "Logs": 8, "Oak logs": 2}
    return player


class TreeGnomeVillageOpeningTest(unittest.TestCase):
    def test_start_alone_records_no_opening_or_future_proofs(self):
        player = _player()
        before = copy.deepcopy(player)
        player, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        before["quests"][QUEST_ID] = {"started": True, "progress": 0, "completed": False}
        self.assertEqual(player, before)
        self.assertFalse(player.get("quest_action_proofs"))

    def test_first_review_records_the_complete_opening_in_order_without_consuming_logs(self):
        player = _player()
        inventory = copy.deepcopy(player["inventory"])
        experience = {key: value for key, value in player.items() if key.endswith("_exp")}
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
        self.assertEqual(player["inventory"], inventory)
        self.assertEqual({key: player[key] for key in experience}, experience)
        self.assertEqual(player["quest_points"], 0)
        self.assertEqual(player["pending_skill_exp_rewards"], {})
        self.assertFalse(player.get("quest_combat_encounters"))
        self.assertFalse(player.get("quest_route_states"))

    def test_ordinary_normal_chopping_supplies_the_atomic_six_log_handoff(self):
        player = _player()
        player["inventory"]["Logs"] = 0
        player["current_tree"] = "tree"
        player, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        for amount in range(1, 6):
            self.assertTrue(handle_woodcutting_answer(_context(player, random_values=(0.0,) + (0.99,) * 20)))
            self.assertEqual(player["inventory"]["Logs"], amount)
            self.assertFalse(player.get("quest_action_proofs"))
            self.assertEqual(player["quests"][QUEST_ID]["progress"], 0)
        self.assertTrue(handle_quest_answer(_context(player)))
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertFalse(handle_quest_answer(_context(player, calls)))
        self.assertEqual(player, before)
        self.assertEqual(calls["saves"], 0)
        self.assertEqual(calls["errors"], [("Quest blocked", "Tree Gnome Village is blocked:\n• Needs Logs x6\n\nQuesting has been switched off until this is resolved.")])
        self.assertTrue(handle_woodcutting_answer(_context(player, random_values=(0.0,) + (0.99,) * 20)))
        self.assertEqual(player["inventory"]["Logs"], 6)
        self.assertEqual(player["woodcutting_exp"], 150.0)
        inventory = copy.deepcopy(player["inventory"])
        experience = {key: value for key, value in player.items() if key.endswith("_exp")}
        self.assertTrue(handle_quest_answer(_context(player)))
        inventory["Logs"] = 0
        self.assertEqual(player["inventory"], inventory)
        self.assertEqual(player["quests"][QUEST_ID], {"started": True, "progress": 3, "completed": False})
        self.assertEqual(player["quest_action_proofs"], sorted(OPENING_ACTIONS))
        self.assertEqual({key: player[key] for key in experience}, experience)
        self.assertEqual(player["quest_points"], 0)
        self.assertFalse(player.get("quest_combat_encounters"))

    def test_genuine_reviews_match_controls_and_survive_undo_replay_save_and_reopen(self):
        original_modules = dict(sys.modules)
        original_random = random.getstate()
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_tree_gnome_opening_e2e")
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
            handoff_random = random.getstate()
            _answer_review(addon)
            handoff_control = copy.deepcopy(addon._state.player_data)
            handoff_control_config = copy.deepcopy(collection._store)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            addon._state.current_skill = "Quests"
            addon.save_player_data()
            self.assertEqual(addon._state.player_data, expected)
            self.assertEqual(collection._store, expected_config)
            random.setstate(handoff_random)
            _answer_review(addon)
            handoff = copy.deepcopy(handoff_control)
            handoff["quests"][QUEST_ID]["progress"] = 3
            handoff["inventory"]["Logs"] = 2
            # Consuming quest supplies refreshes Bank metadata on the normal save.
            handoff["bank_layout"]["items"]["Logs"].update(quantity=2, used_review=2)
            handoff["action_telemetry"]["actions"][f"quest:{QUEST_ID}"].update(
                attempts=2, successes=2, expected_successes=2.0,
            )
            handoff["achievement_progress"]["skills"]["quest"]["actions"][QUEST_ID] = 2
            handoff_config = copy.deepcopy(handoff_control_config)
            handoff_config.update(ankiscape_player_data=handoff, ankiscape_current_skill="Quests")
            self.assertEqual(addon._state.player_data, handoff, errors)
            self.assertEqual(collection._store, handoff_config)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, expected)
            self.assertEqual(collection._store, expected_config)
            random.setstate(handoff_random)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, handoff, errors)
            self.assertEqual(collection._store, handoff_config)
            addon._state.player_data = {}
            addon._state.current_skill = "None"
            addon.load_player_data()
            self.assertEqual(addon._state.player_data, handoff)
            self.assertEqual(addon._state.current_skill, "Quests")
            self.assertEqual(collection._store, handoff_config)
        finally:
            random.setstate(original_random)
            sys.modules.clear()
            sys.modules.update(original_modules)
