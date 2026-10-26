"""Opening answers and actual Discard follow the real Collection's history."""

import copy
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import test_integration_smoke as fixture
from tests.one_small_favour.test_opening_transactions import player
from tests.test_storage_runtime import Collection
from ankiscape.data.quest.one_small_favour import QUEST_ID, BLUNT_HATCHET, OPENING_PROOFS


@unittest.skipIf(Collection is None, 'Anki runtime is not installed; Collection verification remains required')
class OpeningCollectionHistoryTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='ankiscape-favour-history-')
        self.addCleanup(temporary.cleanup)
        self.collection = Collection(str(Path(temporary.name) / 'collection.anki2'))
        self.addCleanup(self.collection.close)
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        self.addCleanup(random.setstate, random.getstate())
        timer = patch('time.time', return_value=1_793_000_000.0)
        timer.start()
        self.addCleanup(timer.stop)
        fixture._install_runtime_fakes()
        sys.modules['aqt'].mw = fixture._DummyMW(self.collection)
        reviewer_type = sys.modules['aqt.reviewer'].Reviewer
        reviewer_type._answerCard = self._scheduler_answer
        self.addon = fixture._load_addon_as_package('ankiscape_favour_collection')
        self.reviewer = reviewer_type()
        self.addon._state.player_data = player(started=False)
        self.addon._state.current_skill = 'Quests'
        for key in ('floating_xp_enabled', 'popups_enabled'):
            self.collection.set_config('ankiscape_' + key, False)
        self.collection.set_config('ankiscape_review_action_multiplier', 1)
        self.addon.save_player_data()
        self.addon.load_player_data()
        self.addon.save_player_data()
        self.cards = [self._new_card(str(index)) for index in range(8)]

    def _new_card(self, front):
        note = self.collection.new_note(self.collection.models.by_name('Basic'))
        note['Front'], note['Back'] = front, 'answer'
        self.collection.add_note(note, 1)
        return note.cards()[0]

    def _scheduler_answer(self, reviewer, ease):
        return self.collection.sched.answerCard(reviewer.card, ease)

    def _answer(self, card):
        final_opening = set(OPENING_PROOFS[:6]).issubset(self.addon._state.player_data['quest_action_proofs'])
        self.reviewer.card = card
        card.start_timer()
        hooks = sys.modules['aqt'].gui_hooks
        for callback in hooks.reviewer_did_show_question:
            callback(card)
        for callback in hooks.reviewer_did_show_answer:
            callback(card)
        self.reviewer._answerCard(3)
        self.assertEqual(self.collection.get_card(card.id).reps, 1)
        if final_opening:
            self.assertEqual(' '.join(self.addon._state.player_data['review_event_log'][-1]['text'].splitlines()),
                             OPENING_PROOFS[-1] + ' One Small Favour 2/8')

    def _checkpoint(self):
        data = copy.deepcopy(self.addon._state.player_data)
        saved = self.collection.get_config('ankiscape_player_data')
        self.assertEqual(saved, json.loads(json.dumps(data)))
        self.assertEqual(self.collection.get_config('ankiscape_current_skill'), 'Quests')
        history = self.collection.db.all('select cid, ease from revlog order by id')
        return data, saved, random.getstate(), history

    def _reopen(self):
        before = self._checkpoint()
        self.collection.close()
        self.collection.reopen()
        self.addon.load_player_data()
        self.assertEqual(self._checkpoint(), before)

    def _undo(self, operation, expected):
        self.assertEqual(self.collection.undo_status().undo, operation)
        changes = self.collection.undo()
        for callback in sys.modules['aqt'].gui_hooks.state_did_undo:
            callback(changes)
        self.assertEqual(self._checkpoint(), expected)

    def test_seven_contacts_and_discard_replacement_undo_and_reopen(self):
        history = []
        card_index = 0
        for index in range(7):
            before = self._checkpoint()
            card = self.cards[card_index]
            self._answer(card)
            history.append(('Answer Card', before, card))
            card_index += 1
            data = self.addon._state.player_data
            self.assertEqual(set(data['quest_action_proofs']), set(OPENING_PROOFS[:index + 1]))
            self.assertEqual(data['quests'][QUEST_ID]['progress'], 2 if index == 6 else 1)
            if index == 2:
                owned = self._checkpoint()
                self.assertTrue(self.addon.on_discard_item(BLUNT_HATCHET, 1))
                history.append(('AnkiScape direct action', owned, None))
                lost = self._checkpoint()
                replacement_card = self.cards[card_index]
                self._answer(replacement_card)
                history.append(('Answer Card', lost, replacement_card))
                card_index += 1
                self.assertEqual(self.addon._state.player_data['quest_action_proofs'], lost[0]['quest_action_proofs'])
        for operation, before, card in reversed(history):
            after = self._checkpoint()
            self._undo(operation, before)
            if card is None:
                self.assertTrue(self.addon.on_discard_item(BLUNT_HATCHET, 1))
            else:
                self.assertEqual(self.collection.get_card(card.id).reps, 0)
                self._answer(card)
            # Revlog IDs are wall-clock generated; compare the history's card/ease data.
            self.assertEqual(self._checkpoint(), after)
            self._undo(operation, before)
        self._reopen()

    def test_reopen_each_custody_checkpoint(self):
        for index in range(3):
            self._answer(self.cards[index])
            self._reopen()
        self.assertTrue(self.addon.on_discard_item(BLUNT_HATCHET, 1))
        self._reopen()
        self.assertEqual(self.addon._state.player_data['inventory'][BLUNT_HATCHET], 0)
        self._answer(self.cards[3])
        self._reopen()
        self.assertEqual(self.addon._state.player_data['inventory'][BLUNT_HATCHET], 1)
        self.assertEqual(set(self.addon._state.player_data['quest_action_proofs']), set(OPENING_PROOFS[:3]))
        self._answer(self.cards[4])
        self._reopen()
        self.assertEqual(self.addon._state.player_data['inventory'][BLUNT_HATCHET], 0)
