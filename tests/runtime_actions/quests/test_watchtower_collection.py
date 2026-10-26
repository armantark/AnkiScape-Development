"""Actual Collection answer/Undo/replay and configuration reload for each deed."""

import copy
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests import test_integration_smoke as fixture
from tests.test_storage_runtime import Collection
from tests.quest_catalog.test_watchtower_opening import QUEST_ID, PROOFS


@unittest.skipIf(Collection is None, 'Anki runtime is not installed')
class WatchtowerCollectionTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='ankiscape-watchtower-')
        self.addCleanup(temporary.cleanup)
        self.collection = Collection(str(Path(temporary.name) / 'collection.anki2'))
        self.addCleanup(self.collection.close)
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        self.addCleanup(random.setstate, random.getstate())
        random.seed(261024)
        fixture._install_runtime_fakes()
        sys.modules['aqt'].mw = fixture._DummyMW(self.collection)
        reviewer_type = sys.modules['aqt.reviewer'].Reviewer
        reviewer_type._answerCard = self._scheduler_answer
        self.addon = fixture._load_addon_as_package('ankiscape_watchtower_collection')
        self.reviewer = reviewer_type()
        self.addon.load_player_data()
        self.addon._state.current_skill = 'Quests'
        data = self.addon._state.player_data
        data.update(current_quest=QUEST_ID, agility_level=25, herblore_level=14,
                    magic_level=14, mining_level=40, thieving_level=15)
        data['quests'][QUEST_ID] = dict(started=True, completed=False, progress=0)
        self.collection.set_config('ankiscape_review_action_multiplier', 1)
        self.collection.set_config('ankiscape_floating_xp_enabled', False)
        self.collection.set_config('ankiscape_popups_enabled', False)
        self.addon.save_player_data()
        # Establish canonical persisted defaults through the real load path.
        self.addon.load_player_data()
        self.addon.save_player_data()
        self.cards = [self._new_card(str(index)) for index in range(3)]

    def _new_card(self, front):
        note = self.collection.new_note(self.collection.models.by_name('Basic'))
        note['Front'], note['Back'] = front, 'answer'
        self.collection.add_note(note, 1)
        return note.cards()[0]

    def _scheduler_answer(self, reviewer, ease):
        return self.collection.sched.answerCard(reviewer.card, ease)

    def _answer(self, card):
        self.reviewer.card = card
        card.start_timer()
        hooks = sys.modules['aqt'].gui_hooks
        for callback in hooks.reviewer_did_show_question:
            callback(card)
        for callback in hooks.reviewer_did_show_answer:
            callback(card)
        self.reviewer._answerCard(3)
        self.assertEqual(self.collection.get_card(card.id).reps, 1)

    def _checkpoint(self):
        data = self.addon._state.player_data
        saved = self.collection.get_config('ankiscape_player_data')
        canonical = json.loads(json.dumps(data))
        self.assertEqual({key: (saved.get(key), canonical.get(key)) for key in set(saved) | set(canonical)
                          if saved.get(key) != canonical.get(key)}, {})
        self.assertEqual(self.collection.get_config('ankiscape_current_skill'), 'Quests')
        return copy.deepcopy(data), random.getstate(), self.addon._state.current_skill

    def _undo_replay(self, card, before, earned):
        self.assertEqual(self.collection.undo_status().undo, 'Answer Card')
        changes = self.collection.undo()
        self.assertEqual(changes.operation, 'Answer Card')
        for callback in sys.modules['aqt'].gui_hooks.state_did_undo:
            callback(changes)
        self.assertEqual(self._checkpoint(), before)
        self.assertEqual(self.collection.get_card(card.id).reps, 0)
        self._answer(self.collection.get_card(card.id))
        self.assertEqual(self._checkpoint(), earned)

    def _reopen(self, expected):
        self.collection.close()
        self.collection.reopen()
        self.addon._state.player_data = {}
        self.addon._state.current_skill = 'None'
        self.addon.load_player_data()
        self.assertEqual(self._checkpoint(), expected)

    def test_all_three_deeds_undo_replay_and_survive_actual_collection_reopen(self):
        for index, card in enumerate(self.cards):
            before = self._checkpoint()
            self._answer(card)
            earned = self._checkpoint()
            self.assertEqual(earned[0]['quest_action_proofs'], sorted(PROOFS[:index + 1]))
            self.assertEqual(earned[0]['inventory']['Fingernails'], 1 if index == 1 else 0)
            self.assertEqual(earned[0]['quests'][QUEST_ID]['progress'], 2 if index == 2 else 1)
            self._undo_replay(card, before, earned)
            self._reopen(earned)
            self._reopen(earned)
