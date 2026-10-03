import copy
import sys
import types
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    BIRD_NEST_OPEN_TABLES, DEFAULT_UTILITY_ACTIVITY, QUEST_DATA,
    QUEST_UNLOCK_RULES, UTILITY_ACTIVITY_DATA, UTILITY_ITEM_IMAGES,
)
from ankiscape.core.target_metadata import utility_activity_rows
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_blockers_pure
from tests.test_combat_quest_gate import _answer_review, _maxed_player_for_quest
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


QUEST = "the_eyes_of_glouphrie"
PROOF = "Collect a bucket of sap from an evergreen tree"
ACTIVITY = "collect_evergreen_sap"


class TestEvergreenSapReview(unittest.TestCase):
    def setUp(self):
        self.original_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_evergreen_sap_e2e")
        self.addon.check_achievements = lambda _data: None
        self.addon.save_player_data = lambda: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon._show_activity_gain = lambda _text: None
        self.addon._show_exp = lambda _amount: None
        self.addon.level_up_check = lambda _skill, _data: None
        self.addon.update_review_hud = lambda _data, _skill: None
        self.errors = []
        self.addon.show_error_message = lambda *error: self.errors.append(error)
        self.player = _maxed_player_for_quest(QUEST)
        self.player["quests"][QUEST] = {
            "started": True, "progress": 3, "completed": False,
        }
        self.player["current_utility"] = ACTIVITY
        self.player["current_quest"] = QUEST
        self.player["inventory"].update({"Bucket": 2, "Knife": 1, "Mud rune": 1})
        self.addon._state.player_data = self.player
        self.addon._state.current_skill = "Utility"
        self.addon._state.review_undo_stack.clear()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def test_sap_review_advances_stage_and_undo_restores_both_reviews(self):
        before = copy.deepcopy(self.player)
        self.assertEqual(before["quest_action_proofs"], [])
        self.assertIn(PROOF, {
            blocker.get("action_id") for blocker in
            quest_current_stage_blockers_pure(self.player, QUEST, QUEST_DATA)
        })
        _answer_review(self.addon)

        after = self.addon._state.player_data
        self.assertFalse(self.errors)
        self.assertIn(PROOF, after["quest_action_proofs"])
        self.assertEqual(after["inventory"]["Bucket"], 1)
        self.assertEqual(after["inventory"]["Bucket of sap"], 1)
        self.assertEqual(after["inventory"]["Knife"], before["inventory"]["Knife"])
        self.assertEqual(after["woodcutting_exp"], before["woodcutting_exp"])
        self.assertEqual(quest_current_stage_blockers_pure(after, QUEST, QUEST_DATA), ())
        rows = utility_activity_rows(
            after, UTILITY_ACTIVITY_DATA, UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES, DEFAULT_UTILITY_ACTIVITY, QUEST_UNLOCK_RULES,
        )
        self.assertTrue(next(row for row in rows if row.target_id == ACTIVITY).enabled)
        sap_inventory = copy.deepcopy(after["inventory"])

        self.addon._state.current_skill = "Quests"
        _answer_review(self.addon)
        self.assertEqual(self.addon._state.player_data["quests"][QUEST]["progress"], 4)

        self.addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.player = self.addon._state.player_data
        self.assertEqual(self.player["quests"][QUEST]["progress"], 3)
        self.assertEqual(self.player["inventory"], sap_inventory)
        self.assertEqual(self.player["quest_action_proofs"], [PROOF])

        self.addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.player = self.addon._state.player_data
        self.assertEqual(self.player["inventory"], before["inventory"])
        self.assertEqual(self.player["quest_action_proofs"], [])
        self.assertEqual(self.player["quests"][QUEST]["progress"], 3)

    def test_missing_bucket_refuses_without_output_or_proof(self):
        self.player["inventory"]["Bucket"] = 0
        before = copy.deepcopy(self.player["inventory"])

        _answer_review(self.addon)

        self.assertEqual(self.addon._state.player_data["inventory"], before)
        self.assertNotIn(PROOF, self.addon._state.player_data["quest_action_proofs"])
        self.assertEqual(self.addon._state.player_data["current_utility"], "bankstanding")

    def test_successful_chopping_does_not_collect_sap_or_emit_proof(self):
        self.player["current_tree"] = "tree"
        self.player["toolbelt"] = {"woodcutting": ["bronze_hatchet"]}
        self.addon._state.current_skill = "Woodcutting"
        with patch.object(self.addon.random, "random", return_value=0.0):
            _answer_review(self.addon)

        after = self.addon._state.player_data
        self.assertEqual(after["action_telemetry"]["actions"]["woodcutting:tree"]["successes"], 1)
        self.assertEqual(after["inventory"]["Bucket"], 2)
        self.assertEqual(after["inventory"].get("Bucket of sap", 0), 0)
        self.assertNotIn(PROOF, after["quest_action_proofs"])
