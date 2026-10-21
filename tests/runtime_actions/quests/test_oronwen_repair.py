"""Real answer dispatch, persistence and review undo for Oronwen's custody."""

import copy
import sys
from types import SimpleNamespace
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.oronwen_repair_data import (
    QUEST_ID, REPAIR_INPUTS, REPAIRED_TROUSERS, PENDING_KEY,
)
from ankiscape.data.quest_action_proof_data import ORONWEN_REPAIR_PROOF
from ankiscape.logic_pure.logic_pure_quest import can_attempt_quest_review_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.quest_catalog.test_oronwen_repair import _player
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _FakeReviewer, _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context

HAND_IN_MESSAGE = "Oronwen took the damaged trousers, 2 Silk and 1 Bear fur. Review one more card to collect the repaired trousers."
COLLECT_MESSAGE = "Oronwen returned the repaired mourner trousers."
PROGRESS_MESSAGE = "Mourning's End Part I 4/8"


class OronwenRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.original_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_oronwen_e2e")
        addon = self.addon
        self.saved = []
        self.messages = []
        self.errors = []
        addon.show_error_message = lambda *args: self.errors.append(args)
        addon.save_player_data = lambda: self.saved.append(copy.deepcopy(addon._state.player_data))
        addon.check_achievements = lambda _data: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = self.messages.append
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon._state.player_data = _player()
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def _undo(self):
        self.addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))

    def test_answer_dispatch_saves_each_phase_once_and_shows_exact_messages(self):
        addon = self.addon
        self.assertTrue(can_attempt_quest_review_pure(addon._state.player_data, QUEST_ID, QUEST_DATA))
        _answer_review(addon)
        self.assertEqual(len(self.saved), 1)
        self.assertEqual(self.messages, [HAND_IN_MESSAGE])
        self.assertIs(self.saved[0][PENDING_KEY], True)
        self.assertEqual(self.saved[0]["quests"][QUEST_ID]["progress"], 3)
        self.assertEqual(self.saved[0]["inventory"].get(REPAIRED_TROUSERS, 0), 0)
        self.assertNotIn(ORONWEN_REPAIR_PROOF, self.saved[0]["quest_action_proofs"])
        self.assertTrue(can_attempt_quest_review_pure(addon._state.player_data, QUEST_ID, QUEST_DATA))
        _answer_review(addon)
        self.assertEqual(len(self.saved), 2)
        self.assertEqual(self.messages, [HAND_IN_MESSAGE, COLLECT_MESSAGE, PROGRESS_MESSAGE])
        self.assertEqual(self.saved[-1]["inventory"][REPAIRED_TROUSERS], 1)
        self.assertEqual(self.saved[-1]["quests"][QUEST_ID]["progress"], 4)
        self.assertIn(ORONWEN_REPAIR_PROOF, self.saved[-1]["quest_action_proofs"])
        self.assertEqual(self.errors, [])

    def test_undo_both_phases_then_reanswer_produces_only_one_repaired_pair(self):
        addon = self.addon
        original = copy.deepcopy(addon._state.player_data)
        _answer_review(addon)
        pending = copy.deepcopy(addon._state.player_data)
        _answer_review(addon)
        self._undo()
        player = addon._state.player_data
        self.assertIs(player[PENDING_KEY], True)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
        self.assertEqual(player["inventory"], pending["inventory"])
        self.assertEqual(player["inventory"].get(REPAIRED_TROUSERS, 0), 0)
        self.assertNotIn(ORONWEN_REPAIR_PROOF, player["quest_action_proofs"])
        self._undo()
        player = addon._state.player_data
        self.assertIs(player[PENDING_KEY], False)
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
        self.assertEqual(player["inventory"], original["inventory"])
        for name, quantity in REPAIR_INPUTS:
            self.assertEqual(player["inventory"][name], quantity)
        addon._state.current_skill = "Quests"
        _answer_review(addon)
        _answer_review(addon)
        self.assertEqual(addon._state.player_data["inventory"][REPAIRED_TROUSERS], 1)
        self.assertEqual(addon._state.player_data["quests"][QUEST_ID]["progress"], 4)

    def test_again_and_other_activity_do_not_hand_in_or_collect(self):
        addon = self.addon
        for phase in ("hand_in", "collect"):
            with self.subTest(phase=phase):
                player = addon._state.player_data
                inventory = copy.deepcopy(player["inventory"])
                pending = player[PENDING_KEY]
                addon._state.card_turned = addon._state.answer_shown = True
                addon._state.exp_awarded = False
                addon.on_answer_card(_FakeReviewer(), 1, lambda *_args: "answered")
                self.assertEqual(addon._state.player_data["inventory"], inventory)
                self.assertIs(addon._state.player_data[PENDING_KEY], pending)
                addon._state.current_skill = "Woodcutting"
                _answer_review(addon)
                player = addon._state.player_data
                self.assertIs(player[PENDING_KEY], pending)
                self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
                self.assertNotIn(ORONWEN_REPAIR_PROOF, player["quest_action_proofs"])
                for name, _ in REPAIR_INPUTS:
                    self.assertEqual(player["inventory"][name], inventory[name])
                self.assertEqual(player["inventory"].get(REPAIRED_TROUSERS, 0), 0)
                addon._state.current_skill = "Quests"
                if phase == "hand_in":
                    _answer_review(addon)
        self.assertNotIn(COLLECT_MESSAGE, self.messages)

    def test_review_cadence_never_collapses_two_phases(self):
        for multiplier in (1, 2, 10):
            for live in (False, True):
                with self.subTest(multiplier=multiplier, live=live):
                    player = _player()
                    calls = {"xp": [], "saves": 0, "errors": []}
                    ctx = _context(player, calls, review_action_multiplier=multiplier)
                    ctx.cadence_live_enabled = live
                    self.assertTrue(handle_quest_answer(ctx))
                    self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
                    self.assertIs(player[PENDING_KEY], True)
                    self.assertEqual(player["inventory"].get(REPAIRED_TROUSERS, 0), 0)
                    self.assertTrue(handle_quest_answer(ctx))
                    self.assertEqual(player["quests"][QUEST_ID]["progress"], 4)
                    self.assertEqual(player["inventory"][REPAIRED_TROUSERS], 1)
                    self.assertEqual(calls["activity"], [HAND_IN_MESSAGE, COLLECT_MESSAGE, PROGRESS_MESSAGE])
                    self.assertEqual(calls["saves"], 2)

    def test_other_stage_blockers_keep_existing_refusal_and_save_nothing(self):
        player = _player()
        player["inventory"]["Feather"] = 0
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertFalse(handle_quest_answer(_context(player, calls)))
        self.assertEqual(player, before)
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
