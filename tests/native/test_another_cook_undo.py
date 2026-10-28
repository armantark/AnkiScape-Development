"""Actual scheduler answers, collection Undo, rejection and reopen for the opening."""

import copy
import json
import sys
import unittest

from tests.native import test_real_undo_history as history
from tests.quest_catalog.another_cook.test_another_cook_transactions import (
    player, transaction_snapshot, QUEST_ID, COMMISSION, PREPARATION,
)


@unittest.skipIf(history.Collection is None, 'Anki runtime is not installed')
class AnotherCookRealUndoTest(unittest.TestCase):
    setUp = history.RealUndoHistoryTest.setUp
    _new_card = history.RealUndoHistoryTest._new_card
    _answer = history.RealUndoHistoryTest._answer

    def _scheduler_answer(self, reviewer, ease):
        if getattr(self, 'reject_next', False):
            self.reject_next = False
            reviewer.state = 'answer'
            raise RuntimeError('scheduler rejected answer')
        result = self.collection.sched.answerCard(reviewer.card, ease)
        reviewer.state = 'question'
        return result

    def _prepare_player(self):
        addon = self.addon
        addon.load_player_data()
        addon._state.player_data = player(inventory={'Ashes': 1, 'Fruit blast (9514)': 1})
        addon._state.current_skill = 'None'
        self.assertTrue(addon.on_set_quest(QUEST_ID))
        addon._select_review_action('Quests')
        self.collection.set_config('ankiscape_review_action_multiplier', 20)
        self.collection.set_config('ankiscape_floating_xp_enabled', False)
        self.collection.set_config('ankiscape_popups_enabled', False)
        addon.show_error_message = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._show_exp = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon.save_player_data()

    def _checkpoint(self):
        data = self.addon._state.player_data
        self.assertEqual(self.collection.get_config('ankiscape_player_data'), json.loads(json.dumps(data)))
        return copy.deepcopy(data), transaction_snapshot(data)

    def _undo(self, expected):
        self.assertEqual(self.collection.undo_status().undo, 'Answer Card')
        changes = self.collection.undo()
        for callback in sys.modules['aqt'].gui_hooks.state_did_undo:
            callback(changes)
        self.assertEqual(self._checkpoint(), expected)

    def test_scheduler_duplicate_undo_reanswer_both_transactions_exact_special_variant(self):
        initial = self._checkpoint()
        self._answer(self.cards[0])
        commissioned = self._checkpoint()
        self.assertEqual(commissioned[0]['inventory']['Coins'], 100)
        self.assertEqual(commissioned[0]['inventory']['Fruit blast (9514)'], 1)
        self.assertEqual(commissioned[0]['quest_action_proofs'], [COMMISSION])
        self.addon.on_answer_card(self.reviewer, 3, lambda *_args: None)
        self.assertEqual(self._checkpoint(), commissioned)
        self._undo(initial)
        self.assertEqual(self.collection.get_card(self.cards[0].id).reps, 0)
        self._answer(self.collection.get_card(self.cards[0].id))
        self.assertEqual(self._checkpoint(), commissioned)
        self._answer(self.cards[1])
        prepared = self._checkpoint()
        self.assertEqual(prepared[0]['inventory']['Coins'], 100)
        self.assertEqual(prepared[0]['inventory']['Fruit blast (9514)'], 0)
        self.assertEqual(prepared[0]['inventory']['Ashes'], 0)
        self.assertEqual(prepared[0]['inventory']['Dirty blast'], 1)
        self.assertEqual(prepared[0]['cooking_exp'], commissioned[0]['cooking_exp'] + 5)
        self.assertEqual(set(prepared[0]['quest_action_proofs']), {COMMISSION, PREPARATION})
        self.assertEqual(prepared[0]['quests'][QUEST_ID]['progress'], 2)
        self.addon.on_answer_card(self.reviewer, 3, lambda *_args: None)
        self.assertEqual(self._checkpoint(), prepared)
        self._undo(commissioned)
        self.assertEqual(self.collection.get_card(self.cards[1].id).reps, 0)
        self._answer(self.collection.get_card(self.cards[1].id))
        self.assertEqual(self._checkpoint(), prepared)

    def test_failed_scheduler_answers_rollback_both_boundaries(self):
        for card in self.cards:
            before = self._checkpoint()
            depth = len(self.addon._state.review_undo_stack)
            self.reject_next = True
            with self.assertRaisesRegex(RuntimeError, 'scheduler rejected'):
                self._answer(card)
            self.assertEqual(self._checkpoint(), before)
            self.assertEqual(self.collection.get_card(card.id).reps, 0)
            self.assertEqual(len(self.addon._state.review_undo_stack), depth)
            self._answer(card)
        self.assertEqual(self.addon._state.player_data['inventory']['Coins'], 100)

    def test_collection_close_reopen_both_boundaries_no_second_advance(self):
        for card in self.cards:
            self._answer(card)
            boundary = self._checkpoint()
            self.collection.close()
            self.collection.reopen()
            self.addon.load_player_data()
            self.assertEqual(self._checkpoint(), boundary)
        self.assertEqual(self.addon._state.player_data['inventory']['Coins'], 100)
        self.assertEqual(self.addon._state.player_data['quests'][QUEST_ID]['progress'], 2)
