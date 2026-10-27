"""Answer dispatch persists the commission's inventory, receipt and progress together."""

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure_quest import start_quest_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.quest_catalog.test_nature_spirit_opening import (
    QUEST_ID, RECEIPT, TALK, earned_prerequisite_player, pie_balances,
)
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import (
    _DummyCol, _DummyMW, _FakeReviewer, _install_runtime_fakes, _load_addon_as_package,
)
from tests.test_runtime_actions import _context
from tests.test_storage_runtime import Collection


def _quest_events(player):
    return player.get("action_telemetry", {}).get("actions", {}).get("quest:nature_spirit", {})


class NatureSpiritOpeningRuntimeTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        _install_runtime_fakes()
        self.collection = _DummyCol()
        sys.modules["aqt"].mw = _DummyMW(self.collection)
        self.addon = _load_addon_as_package("ankiscape_nature_spirit_review")
        addon = self.addon
        addon.load_player_data()
        self.earned = earned_prerequisite_player(self)
        self.saved = []
        self.errors = []
        original_save = addon.save_player_data

        def save():
            self.saved.append(copy.deepcopy(addon._state.player_data))
            original_save()

        addon.save_player_data = save
        addon.show_error_message = lambda *args: self.errors.append(args)
        addon.check_achievements = lambda _data: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda *_args: None
        addon._show_exp = lambda *_args: None
        addon.level_up_check = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        self._select_earned()

    def _select_earned(self):
        player, ok = start_quest_pure(copy.deepcopy(self.earned), QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.addon._state.player_data = player
        self.addon._state.current_skill = "Quests"
        self.addon._state.review_undo_stack.clear()
        self.saved.clear()
        self.errors.clear()

    def _assert_opening(self, player):
        self.assertEqual(pie_balances(player), (3, 3))
        self.assertIn(TALK, player["quest_action_proofs"])
        self.assertEqual(player["quest_action_proofs"].count(RECEIPT), 1)
        self.assertEqual(player["quests"][QUEST_ID], dict(started=True, progress=2, completed=False))
        self.assertEqual(_quest_events(player)["attempts"], 1)
        self.assertEqual(_quest_events(player)["successes"], 1)

    def test_review_saves_supply_receipt_and_progress_together(self):
        # Inspect the handler's save independently from review clock housekeeping.
        player = copy.deepcopy(self.addon._state.player_data)
        calls = {"xp": [], "saves": 0, "errors": []}
        ctx = _context(player, calls)
        handler_snapshots = []
        ctx.save_player_data = lambda: handler_snapshots.append(copy.deepcopy(player))
        self.assertTrue(handle_quest_answer(ctx))
        self.assertEqual(len(handler_snapshots), 1)
        self._assert_opening(handler_snapshots[0])
        _answer_review(self.addon)
        self.assertEqual(len(self.saved), 1)
        for snapshot in self.saved:
            self._assert_opening(snapshot)
        self._assert_opening(self.addon._state.player_data)
        self.assertEqual(len(self.addon._state.review_undo_stack), 1)
        self.assertEqual(self.errors, [])

    def test_refused_review_has_no_supply_or_receipt(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["current_quest"] = QUEST_ID
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertFalse(handle_quest_answer(_context(player, calls)))
        self.assertEqual(player, before)
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"], [("Quest unavailable", "Nature Spirit cannot progress right now, so questing has been switched off.")])
        self.addon._state.player_data = player
        _answer_review(self.addon)
        # The generic reviewer may save its clocks, but no successful quest event.
        for snapshot in [self.addon._state.player_data, *self.saved]:
            self.assertEqual(pie_balances(snapshot), (0, 0))
            self.assertNotIn(RECEIPT, snapshot["quest_action_proofs"])
            self.assertEqual(snapshot["quests"][QUEST_ID], before["quests"][QUEST_ID])
            self.assertEqual(_quest_events(snapshot), {})
        self.assertEqual(self.errors, calls["errors"])
        self.assertNotEqual(self.addon._state.current_skill, "Quests")

    def test_again_other_activity_and_selection_do_not_accept(self):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)
        self.assertEqual(pie_balances(before), (0, 0))
        self.assertNotIn(RECEIPT, before["quest_action_proofs"])
        addon._state.card_turned = addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 1, lambda *_args: "answered")
        addon._state.current_skill = "Woodcutting"
        _answer_review(addon)
        for snapshot in [addon._state.player_data, *self.saved]:
            self.assertEqual(pie_balances(snapshot), (0, 0))
            self.assertNotIn(RECEIPT, snapshot["quest_action_proofs"])
            self.assertEqual(snapshot["quests"][QUEST_ID], before["quests"][QUEST_ID])
            self.assertEqual(_quest_events(snapshot), {})

    def test_one_opening_stage_per_card_at_each_speed(self):
        for multiplier in (1, 2, 10):
            for live in (False, True):
                with self.subTest(multiplier=multiplier, cadence_live_enabled=live):
                    self._select_earned()
                    self.collection.set_config("ankiscape_review_action_multiplier", multiplier)
                    self.collection.set_config("ankiscape_cadence_kernel", live)
                    self.assertEqual(self.addon._review_action_multiplier(), multiplier)
                    self.assertEqual(self.addon._cadence_kernel_enabled(), live)
                    _answer_review(self.addon)
                    self._assert_opening(self.addon._state.player_data)
                    self.assertEqual(len(self.saved), 1)
                    self._assert_opening(self.saved[0])

    @unittest.skipIf(Collection is None, "Anki runtime is not installed")
    def test_saved_reopen_does_not_regrant(self):
        with tempfile.TemporaryDirectory(prefix="ankiscape-commission-") as directory:
            collection = Collection(str(Path(directory) / "collection.anki2"))
            try:
                sys.modules["aqt"].mw.col = collection
                _answer_review(self.addon)
                saved = collection.get_config("ankiscape_player_data")
                self._assert_opening(saved)
                collection.close()
                collection.reopen()
                self.addon.load_player_data()
                self._assert_opening(self.addon._state.player_data)
                self.assertEqual(collection.get_config("ankiscape_player_data"), saved)
                self.assertEqual(len(self.saved), 1)
            finally:
                collection.close()
