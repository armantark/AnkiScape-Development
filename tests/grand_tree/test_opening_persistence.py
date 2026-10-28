"""Complete live/save Undo, replay, rejection and reopen boundaries."""

import copy
import random
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.data.quest.grand_tree import QUEST_ID, PROOFS, EVENTS
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import migrate_loaded_data
from ankiscape.logic_pure.logic_pure_quest import can_attempt_quest_review_pure, quest_journal_rows_pure
from tests.grand_tree.test_opening_review import (
    review_session, activate, rows, prepare_answer, PLAYER_KEY,
)
from tests.grand_tree.test_opening_transactions import player_at, BARK, BOOK, SCROLL
from tests.test_early_quest_item_routes import _answer_review

try:
    from anki.collection import Collection
    from anki.utils import to_json_bytes, from_json_bytes
except ImportError:
    Collection = None


def undo(addon):
    addon._on_state_did_undo(SimpleNamespace(
        operation='Answer Card', changes=SimpleNamespace(study_queues=True, card=True),
    ))


def snapshot(addon, collection):
    return dict(live=copy.deepcopy(addon._state.player_data), saved=copy.deepcopy(collection._store),
                skill=addon._state.current_skill, rng=random.getstate(), journal=rows(addon))


class OpeningPersistenceTest(unittest.TestCase):
    def test_every_boundary_full_undo_replay_and_saved_reopen(self):
        with review_session() as (addon, collection, errors, _notices):
            activate(addon)
            for boundary in range(4):
                addon.save_player_data()
                before = snapshot(addon, collection)
                _answer_review(addon)
                after = snapshot(addon, collection)
                self.assertNotEqual(after['live'], before['live'])
                self.assertEqual(after['saved'][PLAYER_KEY], after['live'])
                undo(addon)
                self.assertEqual(snapshot(addon, collection), before)
                _answer_review(addon)
                self.assertEqual(snapshot(addon, collection), after)
                self._assert_read_only(addon)
                addon._state.player_data = {}
                addon.load_player_data()
                self.assertEqual(snapshot(addon, collection), after)
                count = (1, 2, 3, 5)[boundary]
                self.assertEqual(addon._state.player_data['quest_action_proofs'], sorted(PROOFS[:count]))
            self.assertEqual(errors, [])

    def _assert_read_only(self, addon):
        before = copy.deepcopy(addon._state.player_data)
        for _ in range(4):
            rows(addon)
            logic = sys.modules[f'{addon.__name__}.logic_pure.logic_pure_quest']
            logic.can_attempt_quest_review_pure(addon._state.player_data, QUEST_ID, addon.QUEST_DATA)
        self.assertEqual(addon._state.player_data, before)

    def test_anki_answer_veto_and_exception_restore_every_bundle(self):
        for raises in (False, True):
            with review_session() as (addon, collection, _errors, _notices):
                activate(addon)
                for boundary in range(4):
                    self._assert_rejection(addon, collection, boundary, raises)
                    _answer_review(addon)

    def _assert_rejection(self, addon, collection, boundary, raises):
        addon.save_player_data()
        before = snapshot(addon, collection)
        stack_before = list(addon._state.review_undo_stack)
        prepare_answer(addon)

        def reject(*_):
            expected = (1, 2, 3, 5)[boundary]
            self.assertEqual(addon._state.player_data['quest_action_proofs'], sorted(PROOFS[:expected]))
            if raises:
                raise RuntimeError('Anki rejected answer')
            return 'vetoed'

        reviewer = SimpleNamespace(state='answer')
        if raises:
            with self.assertRaisesRegex(RuntimeError, 'Anki rejected'):
                addon.on_answer_card(reviewer, 4, reject)
        else:
            self.assertEqual(addon.on_answer_card(reviewer, 4, reject), 'vetoed')
        self.assertEqual(snapshot(addon, collection), before)
        self.assertEqual(addon._state.review_undo_stack, stack_before)

    def test_late_refusal_keeps_entire_runtime_and_saved_state(self):
        for boundary in (0, 3):
            with review_session() as (addon, collection, _errors, _notices):
                activate(addon)
                for _ in range(boundary):
                    _answer_review(addon)
                self._assert_late_refusal(addon, collection, boundary)

    def _assert_late_refusal(self, addon, collection, boundary):
        module = sys.modules[f'{addon.__name__}.logic_pure.quest.grand_tree']
        addon.save_player_data()
        before = snapshot(addon, collection)
        recorder = module.record_runtime_quest_action_proofs_pure
        change = module._change_item

        def refuse_book(inventory, name, delta):
            return False if name == BOOK else change(inventory, name, delta)

        def refuse_warning(data, *event):
            return False if event == EVENTS[4] else recorder(data, *event)

        target = '_change_item' if boundary == 0 else 'record_runtime_quest_action_proofs_pure'
        refusal = refuse_book if boundary == 0 else refuse_warning
        runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
        ctx = addon._runtime_action_context()
        with patch.object(module, target, side_effect=refusal):
            with patch.object(ctx, 'deactivate_current_skill'), patch.object(ctx, 'show_error_message'):
                self._assert_handler_refuses(runtime, ctx)
            self.assertEqual(snapshot(addon, collection), before)
            # Answer-level telemetry may change on a refused action; custody and deeds cannot.
            _answer_review(addon)
        self.assertEqual(addon._state.player_data['inventory'], before['live']['inventory'])
        self.assertEqual(addon._state.player_data['quests'], before['live']['quests'])
        self.assertEqual(addon._state.player_data['quest_action_proofs'], before['live']['quest_action_proofs'])
        refused = snapshot(addon, collection)
        self.assertEqual(refused['saved'][PLAYER_KEY], refused['live'])
        undo(addon)
        self.assertEqual(snapshot(addon, collection), before)
        _answer_review(addon)
        self.assertEqual(len(addon._state.player_data['quest_action_proofs']), (1, 5)[boundary == 3])

    def _assert_handler_refuses(self, runtime, ctx):
        with patch.object(runtime, '_record_action') as record, patch.object(ctx, 'save_player_data') as save:
            self.assertFalse(runtime.handle_quest_answer(ctx))
            record.assert_not_called()
            save.assert_not_called()

    def test_fresh_item_old_objective_and_legacy_saves_gain_no_inferred_deeds(self):
        states = [player_at(), player_at(), player_at(), player_at(4), player_at(4)]
        states[0]['quests'][QUEST_ID] = dict(started=False, progress=0, completed=False)
        states[1]['inventory'].update({BARK: 3, BOOK: 4, SCROLL: 5})
        states[2]['quest_action_proofs'] = ['Complete The Grand Tree stage 1 objective', 'Complete The Grand Tree stage 2 objective']
        for player in states[3:]:
            player['quest_action_proofs'] = []
        states[4]['quests'][QUEST_ID].update(progress=7, completed=True)
        for player in states:
            self._assert_legacy_projection(player)

    def _assert_legacy_projection(self, player):
        # Migrate once before comparison, then prove repeated ordinary loading is stable.
        data = migrate_loaded_data(copy.deepcopy(player), ORE_DATA, ITEM_DEFINITIONS)
        before = copy.deepcopy(data)
        for _ in range(3):
            journal = quest_journal_rows_pure(data, QUEST_ID, QUEST_DATA)
            can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA)
            data = migrate_loaded_data(copy.deepcopy(data), ORE_DATA, ITEM_DEFINITIONS)
            self.assertEqual(data, before)
            self.assertFalse(any(row['completed'] for row in journal if row['stage'] in (1, 2)))
        self.assertFalse(set(PROOFS) & set(data['quest_action_proofs']))

    @unittest.skipUnless(Collection is not None, 'Anki encoding/backend needs the Qt lane')
    def test_real_anki_encoded_save_undo_and_reopen_at_every_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            collection = Collection(str(Path(directory) / 'opening.anki2'))
            try:
                self._assert_encoded_boundaries(collection)
            finally:
                collection.close()

    def _assert_encoded_boundaries(self, collection):
        with review_session() as (addon, _fake_collection, _errors, _notices):
            addon.mw.col = collection
            activate(addon)
            for _ in range(4):
                self._assert_encoded_boundary(addon, collection)

    def _assert_encoded_boundary(self, addon, collection):
        addon.save_player_data()
        before = copy.deepcopy(addon._state.player_data)
        saved_before = collection.get_config(PLAYER_KEY)
        encoded_before = to_json_bytes(before)
        self.assertEqual(saved_before, from_json_bytes(encoded_before))
        skill_before, rng_before, rows_before = addon._state.current_skill, random.getstate(), rows(addon)
        _answer_review(addon)
        earned, earned_rng = copy.deepcopy(addon._state.player_data), random.getstate()
        saved_after = collection.get_config(PLAYER_KEY)
        self.assertEqual(saved_after, from_json_bytes(to_json_bytes(earned)))
        undo(addon)
        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(collection.get_config(PLAYER_KEY), saved_before)
        self.assertEqual(collection.get_config(PLAYER_KEY), from_json_bytes(encoded_before))
        self.assertEqual((addon._state.current_skill, random.getstate(), rows(addon)), (skill_before, rng_before, rows_before))
        _answer_review(addon)
        self.assertEqual(addon._state.player_data, earned)
        self.assertEqual(random.getstate(), earned_rng)
        self.assertEqual(collection.get_config(PLAYER_KEY), saved_after)
        addon.load_player_data()
        expected_loaded = migrate_loaded_data(copy.deepcopy(saved_after), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(addon._state.player_data, expected_loaded)
        self.assertEqual(collection.get_config(PLAYER_KEY), saved_after)
