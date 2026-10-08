"""First Resort opening reviews and the first catering handoff stay bounded."""

import copy
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA, QUEST_UNLOCK_RULES
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_quest import (
    quest_locked_reasons_pure,
    target_unlock_locked_reasons_pure,
)
from ankiscape.runtime.runtime_actions import handle_quest_answer, handle_woodcutting_answer
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


QUEST_ID = "as_a_first_resort"
OPENING_ACTIONS = (
    "Head to Oo'glog East of Mobilising Armies and talk to Chief Tess.",
    "Talk to Balnea in the Oo'glog bank.",
)


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(current_quest=QUEST_ID, firemaking_level=51, hunter_level=48, woodcutting_level=58)
    player["quests"]["zogre_flesh_eaters"] = {
        "started": True, "progress": QUEST_DATA["zogre_flesh_eaters"]["stages"], "completed": True,
    }
    player["inventory"] = {"Bronze hatchet": 1, "Tinderbox": 1, "Coins": 37, "Logs": 2}
    return player


class FirstResortOpeningTest(unittest.TestCase):
    def test_missing_zogre_prerequisite_refuses_before_opening_actions(self):
        player = _player()
        player["quests"]["zogre_flesh_eaters"] = {"started": False, "progress": 0, "completed": False}
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertEqual(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA), ("Zogre Flesh Eaters",))
        self.assertFalse(handle_quest_answer(_context(player, calls)))
        self.assertEqual(player, before)
        self.assertEqual(calls["saves"], 0)

    def test_unstarted_review_runs_chief_tess_then_balnea_without_future_materials(self):
        player = _player()
        before_inventory = copy.deepcopy(player["inventory"])
        self.assertFalse(player["quests"][QUEST_ID]["started"])
        self.assertFalse(player.get("quest_action_proofs"))
        with patch.object(
            quest_action_proofs,
            "quest_action_proofs_after_event_pure",
            wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
        ) as events:
            self.assertTrue(handle_quest_answer(_context(player)))
        opening_events = [
            call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"
        ]
        self.assertEqual(opening_events, [f"{QUEST_ID}:{action}" for action in OPENING_ACTIONS])
        self.assertEqual(player["quest_action_proofs"], sorted(OPENING_ACTIONS))
        self.assertEqual(player["quests"][QUEST_ID], {"started": True, "progress": 2, "completed": False})
        self.assertEqual(player["inventory"], before_inventory)

    def test_each_start_skill_gate_refuses_without_starting_or_recording_actions(self):
        for skill, level in (("firemaking", 50), ("hunter", 47), ("woodcutting", 57)):
            with self.subTest(skill=skill):
                player = _player()
                player[f"{skill}_level"] = level
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)

    def test_ordinary_chopping_supplies_exact_handoff_and_later_reviews_stay_held(self):
        player = _player()
        self.assertTrue(handle_quest_answer(_context(player)))
        for tree, count, item in (("achey", 8, "Achey tree logs"), ("eucalyptus", 10, "Eucalyptus logs")):
            player["current_tree"] = tree
            for _ in range(count):
                self.assertTrue(handle_woodcutting_answer(_context(player, random_values=(0.0,) + (0.99,) * 20)))
            self.assertEqual(player["inventory"][item], count)
        before_exp = {skill: player[f"{skill}_exp"] for skill in ("firemaking", "hunter", "woodcutting")}
        before_inventory = copy.deepcopy(player["inventory"])
        self.assertTrue(handle_quest_answer(_context(player)))
        expected_inventory = {**before_inventory, "Achey tree logs": 0, "Eucalyptus logs": 0}
        self.assertEqual(player["inventory"], expected_inventory)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
        for _ in range(2):
            self.assertFalse(handle_quest_answer(_context(player)))
            self.assertEqual(player["inventory"], expected_inventory)
            self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
        self.assertFalse(player["quests"][QUEST_ID]["completed"])
        self.assertEqual(player["quest_points"], 0)
        self.assertNotIn("Casket", player["inventory"])
        self.assertEqual({skill: player[f"{skill}_exp"] for skill in before_exp}, before_exp)
        for skill, target in (("mining", "red_sandstone"), ("hunter", "catch_wimpy_bird"), ("utility", "make_robust_glass")):
            self.assertTrue(target_unlock_locked_reasons_pure(player, skill, target, QUEST_UNLOCK_RULES))

    def test_missing_either_log_stack_refuses_atomically_and_can_resume(self):
        for missing, amount in (("Achey tree logs", 7), ("Eucalyptus logs", 9)):
            with self.subTest(missing=missing):
                player = _player()
                self.assertTrue(handle_quest_answer(_context(player)))
                del player["inventory"]["Logs"]
                player["inventory"].update({"Achey tree logs": 8, "Eucalyptus logs": 10})
                player["inventory"][missing] = amount
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)
                player["inventory"][missing] += 1
                self.assertTrue(handle_quest_answer(_context(player)))
                self.assertEqual(player["inventory"]["Achey tree logs"], 0)
                self.assertEqual(player["inventory"]["Eucalyptus logs"], 0)
                self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)

    def test_handoff_preserves_surplus_logs_tools_and_unrelated_items(self):
        player = _player()
        self.assertTrue(handle_quest_answer(_context(player)))
        player["inventory"].update({"Achey tree logs": 12, "Eucalyptus logs": 17, "Raw chompy": 2, "Primweed": 3})
        expected = {**player["inventory"], "Achey tree logs": 4, "Eucalyptus logs": 7}
        self.assertTrue(handle_quest_answer(_context(player)))
        self.assertEqual(player["inventory"], expected)
        self.assertFalse(handle_quest_answer(_context(player)))
        self.assertEqual(player["inventory"], expected)

    def test_saved_handoff_and_undo_restore_both_opening_and_consumption(self):
        original_modules = dict(sys.modules)
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_first_resort_e2e")
            saved = []
            errors = []
            addon.show_error_message = lambda title, message: errors.append((title, message))
            addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
            addon.check_achievements = lambda _data: None
            addon._refresh_skill_availability = lambda: None
            addon._show_activity_gain = lambda _text: None
            addon._show_exp = lambda _amount: None
            addon.level_up_check = lambda *_args: None
            addon.update_review_hud = lambda *_args: None
            player = _player()
            player["inventory"].update({"Achey tree logs": 8, "Eucalyptus logs": 10})
            addon._state.player_data = player
            addon._state.current_skill = "Quests"
            addon._state.review_undo_stack.clear()
            before_inventory = copy.deepcopy(player["inventory"])
            _answer_review(addon)
            self.assertEqual(saved[-1]["quest_action_proofs"], sorted(OPENING_ACTIONS))
            self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 2, errors)
            _answer_review(addon)
            self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 3, errors)
            self.assertEqual(saved[-1]["inventory"]["Achey tree logs"], 0)
            self.assertEqual(saved[-1]["inventory"]["Eucalyptus logs"], 0)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            restored = addon._state.player_data
            self.assertEqual(restored["quests"][QUEST_ID]["progress"], 2)
            self.assertEqual(restored["inventory"], before_inventory)
            self.assertEqual(restored["quest_action_proofs"], sorted(OPENING_ACTIONS))
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertFalse(addon._state.player_data["quests"][QUEST_ID]["started"])
            self.assertFalse(addon._state.player_data.get("quest_action_proofs"))
            addon._state.current_skill = "Quests"
            _answer_review(addon)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data["quests"][QUEST_ID]["progress"], 3, errors)
            self.assertEqual(addon._state.player_data["inventory"]["Achey tree logs"], 0)
            self.assertEqual(addon._state.player_data["inventory"]["Eucalyptus logs"], 0)
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)
