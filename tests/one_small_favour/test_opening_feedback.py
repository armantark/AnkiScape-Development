"""Opening notices survive the real review feedback, event log and Undo owners."""

import copy
import json
import random
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tests.one_small_favour.test_opening_transactions import player
from tests.one_small_favour.test_review_dispatch import RuntimeFixture
from tests.test_combat_quest_gate import _answer_review
from ankiscape.data.quest.one_small_favour import OPENING_DEEDS, OPENING_PROOFS, QUEST_ID
from ankiscape.logic_pure.quest.review_steps import quest_review_message_pure


FINAL_NOTICE = ('One Small Favour: obtain Johanhus’s\n'
                'request for one month’s supply of\n'
                'chickens from Fred\nOne Small Favour 2/8')


class OpeningFeedbackTest(RuntimeFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(random.setstate, random.getstate())
        timer = patch('time.time', return_value=1_793_000_000.0)
        timer.start()
        self.addCleanup(timer.stop)
        self.addon._show_activity_gain = self.show_activity_gain
        self.popup = Mock()
        self.addon.mw.exp_popup = self.popup
        self.addon.update_review_event_log_drawer = lambda _data: None
        self.collection.set_config = lambda key, value: self.collection._store.__setitem__(key, self._encoded(value))

    @staticmethod
    def _encoded(value):
        return json.loads(json.dumps(value))

    def _prepare(self, prefix=0, *, floating=True):
        self.collection.set_config('ankiscape_floating_xp_enabled', floating)
        self.addon._state.player_data = player(prefix, started=bool(prefix))
        self.addon.save_player_data()
        self.addon.load_player_data()
        self.addon.save_player_data()
        self.saved.clear()

    def test_all_seven_notices_reach_popup_and_persisted_event_log(self):
        self._prepare()
        for index, notice in enumerate(OPENING_PROOFS):
            _answer_review(self.addon)
            expected = FINAL_NOTICE if index == 6 else notice
            self.popup.show_text.assert_called_with(expected)
            data = self.addon._state.player_data
            self.assertEqual(data['review_event_log'][-1]['text'], expected)
            self.assertEqual(self.collection.get_config('ankiscape_player_data'), self._encoded(data))
            self.assertEqual(len(self.saved), index + 1)
        self.assertEqual(self.popup.show_text.call_count, 7)
        self.assertEqual([row['text'] for row in data['review_event_log']],
                         [*OPENING_PROOFS[:6], FINAL_NOTICE])

    def test_johanhus_notice_survives_undo_reanswer_with_floating_feedback_on_or_off(self):
        for floating in (True, False):
            with self.subTest(floating=floating):
                self._prepare(6, floating=floating)
                self.popup.reset_mock()
                before = copy.deepcopy(self.addon._state.player_data)
                _answer_review(self.addon)
                after = copy.deepcopy(self.addon._state.player_data)
                self.assertEqual(after['quests'][QUEST_ID]['progress'], 2)
                self.assertEqual(after['review_event_log'][-1]['text'], FINAL_NOTICE)
                self.assertEqual(self.popup.show_text.call_count, int(floating))
                self.addon._on_state_did_undo(SimpleNamespace(operation='Answer Card'))
                self.assertEqual(self.addon._state.player_data, before)
                self.assertEqual(self.collection.get_config('ankiscape_player_data'), self._encoded(before))
                _answer_review(self.addon)
                self.assertEqual(self.addon._state.player_data, after)
                self.assertEqual(self.collection.get_config('ankiscape_player_data'), self._encoded(after))
                self.assertEqual(self.popup.show_text.call_count, 2 * int(floating))

    def test_adapter_retains_johanhus_exact_notice_and_progress_request(self):
        self.assertEqual(quest_review_message_pure(OPENING_DEEDS[-1]['event_id']),
                         ((OPENING_PROOFS[-1],), True))
