"""Bedroom searches through the menu, real answer transaction, storage and Undo."""

import copy
import random
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tests.quest_catalog.test_murder_mystery_review import review_session, prepare_answer, rows, PLAYER_KEY
from tests.quest_catalog.test_murder_mystery_opening import QUEST_ID, ACTION, POT, DAGGER
from tests.test_early_quest_item_routes import _answer_review
from tests.test_integration_smoke import _FakeReviewer


def silver_module(addon):
    return sys.modules[f'{addon.__name__}.logic_pure.quest.murder_mystery']


def next_target(addon):
    return silver_module(addon).next_murder_mystery_silver_search_pure(addon._state.player_data)


def undo(addon):
    addon._on_state_did_undo(SimpleNamespace(
        operation='Answer Card', changes=SimpleNamespace(study_queues=True, card=True),
    ))


def quest_state(data):
    return {key: copy.deepcopy(data[key]) for key in (
        'inventory', 'equipment', 'quests', 'quest_action_proofs', 'quest_points', 'pending_skill_exp_rewards',
    )}


def start_and_open(addon):
    addon.on_set_quest(QUEST_ID)
    addon._select_review_action('Quests')
    _answer_review(addon)


class TestMurderMysterySilverReview(unittest.TestCase):
    def assert_delta(self, before, after, row, mode):
        expected = quest_state(before)
        if mode != 'proof':
            expected['inventory'][row['name']] = expected['inventory'].get(row['name'], 0) + 1
        if mode != 'replacement':
            expected['quest_action_proofs'] = sorted(set(expected['quest_action_proofs']) | {row['proof_id']})
        self.assertEqual(quest_state(after), expected)
        self.assertEqual(after['quests'][QUEST_ID], dict(started=True, completed=False, progress=2))
        self.assertEqual((after['inventory'][POT], after['inventory'][DAGGER]), (1, 1))
        self.assertIn(ACTION, after['quest_action_proofs'])

    def assert_review_undo_replay(self, addon, collection, row, mode):
        before = copy.deepcopy(addon._state.player_data)
        skill, rng, journal = addon._state.current_skill, random.getstate(), rows(addon)
        target = next_target(addon)
        _answer_review(addon)
        earned, earned_rng = copy.deepcopy(addon._state.player_data), random.getstate()
        self.assert_delta(before, earned, row, mode)
        self.assertEqual(collection._store[PLAYER_KEY], earned)
        undo(addon)
        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(collection._store[PLAYER_KEY], before)
        self.assertEqual(addon._state.current_skill, skill)
        self.assertEqual(random.getstate(), rng)
        self.assertEqual(rows(addon), journal)
        self.assertEqual(next_target(addon), target)
        _answer_review(addon)
        self.assertEqual(addon._state.player_data, earned)
        self.assertEqual(random.getstate(), earned_rng)
        self.assertEqual(collection._store[PLAYER_KEY], earned)
        self.assert_reload(addon, collection)

    def assert_reload(self, addon, collection):
        earned = copy.deepcopy(addon._state.player_data)
        target, journal = next_target(addon), rows(addon)
        addon._state.player_data = {}
        addon.load_player_data()
        self.assertEqual(addon._state.player_data, earned)
        self.assertEqual(collection._store[PLAYER_KEY], earned)
        self.assertEqual(next_target(addon), target)
        self.assertEqual(rows(addon), journal)

    def test_six_real_reviews_save_undo_replay_and_reopen_independently(self):
        with review_session() as (addon, collection, errors):
            start_and_open(addon)
            messages = []
            addon._show_activity_gain = messages.append
            searches = silver_module(addon).SILVER_SEARCHES
            for row in searches:
                messages.clear()
                self.assert_review_undo_replay(addon, collection, row, 'new')
                self.assertEqual(messages, [f"Searched {row['owner']}'s barrel and collected one {row['name']}."] * 2)
            self.assertIsNone(next_target(addon))
            self.assertEqual(set(addon._state.player_data['quest_action_proofs']), {ACTION} | {r['proof_id'] for r in searches})
            self.assertEqual(errors, [])

    def test_proof_only_advanced_custody_and_each_replacement_are_undoable(self):
        with review_session() as (addon, collection, errors):
            start_and_open(addon)
            searches = silver_module(addon).SILVER_SEARCHES
            for row in searches:
                addon._state.player_data['inventory'][row['dusted_name']] = 3
                addon.save_player_data()
                messages = []
                addon._show_activity_gain = messages.append
                self.assert_review_undo_replay(addon, collection, row, 'proof')
                self.assertEqual(messages, [f"Searched {row['owner']}'s barrel; your existing evidence was kept."] * 2)
            for row in searches:
                addon._state.player_data['inventory'].pop(row['dusted_name'])
                addon.save_player_data()
                messages.clear()
                self.assert_review_undo_replay(addon, collection, row, 'replacement')
                self.assertEqual(messages, [f"Searched {row['owner']}'s barrel and recovered one {row['name']}."] * 2)
            self.assertEqual(errors, [])

    def test_again_never_performs_initial_or_replacement_search(self):
        with review_session() as (addon, collection, errors):
            start_and_open(addon)
            for _ in range(7):
                before, target = quest_state(addon._state.player_data), next_target(addon)
                prepare_answer(addon)
                addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: 'answered')
                self.assertEqual(quest_state(addon._state.player_data), before)
                self.assertEqual(quest_state(collection._store[PLAYER_KEY]), before)
                self.assertEqual(next_target(addon), target)
                _answer_review(addon)
            addon._state.player_data['inventory'].pop('Silver necklace')
            before = quest_state(addon._state.player_data)
            prepare_answer(addon)
            addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: 'answered')
            self.assertEqual(quest_state(addon._state.player_data), before)
            self.assertEqual(next_target(addon)['owner'], 'Anna')
            self.assertTrue(all(title == 'Bedroom search refused' for title, _ in errors))

    def test_direct_handler_refusals_never_record_or_save(self):
        with review_session() as (addon, collection, errors):
            start_and_open(addon)
            module = silver_module(addon)
            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            ctx = addon._runtime_action_context()
            addon._state.player_data['inventory']['Silver necklace'] = -1
            before = copy.deepcopy(addon._state.player_data)
            with patch.object(runtime, '_record_action') as record, patch.object(ctx, 'save_player_data') as save:
                self.assertFalse(runtime.handle_quest_answer(ctx))
                record.assert_not_called()
                save.assert_not_called()
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(errors[-1], ('Bedroom search refused', module.INVALID_CUSTODY))
            addon._state.player_data['inventory'].pop('Silver necklace')
            before = copy.deepcopy(addon._state.player_data)
            with patch.object(module, '_grant_opening_item_pure', return_value=False):
                with patch.object(runtime, '_record_action') as record, patch.object(ctx, 'save_player_data') as save:
                    self.assertFalse(runtime.handle_quest_answer(ctx))
                    record.assert_not_called()
                    save.assert_not_called()
                self.assertEqual(addon._state.player_data, before)
                _answer_review(addon)
            self.assertEqual(quest_state(addon._state.player_data), quest_state(before))
            self.assertEqual(quest_state(collection._store[PLAYER_KEY]), quest_state(before))
            # The review itself still has its ordinary answer/Undo effects.
            self.assertGreater(len(addon._state.review_undo_stack), 1)
            undo(addon)
            self.assertEqual(addon._state.player_data, before)

    def test_invalid_custody_containers_refuse_before_generic_stage_inspection(self):
        with review_session() as (addon, _collection, errors):
            start_and_open(addon)
            module = silver_module(addon)
            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            ctx = addon._runtime_action_context()
            for key in ('inventory', 'equipment'):
                original = addon._state.player_data[key]
                for value in (None, [], 'invalid'):
                    addon._state.player_data[key] = value
                    before = copy.deepcopy(addon._state.player_data)
                    with patch.object(runtime, '_record_action') as record, patch.object(ctx, 'save_player_data') as save:
                        self.assertFalse(runtime.handle_quest_answer(ctx))
                        record.assert_not_called()
                        save.assert_not_called()
                    self.assertEqual(addon._state.player_data, before)
                    self.assertEqual(errors[-1], ('Bedroom search refused', module.INVALID_CUSTODY))
                addon._state.player_data[key] = original

    def test_exhausted_and_rechecked_eligibility_report_the_actual_reason(self):
        with review_session() as (addon, _collection, errors):
            start_and_open(addon)
            module = silver_module(addon)
            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            ctx = addon._runtime_action_context()
            quest = runtime.QUEST_DATA[QUEST_ID]
            with patch.dict(quest, {'required_quest_points': 999}):
                with patch.object(runtime, '_record_action') as record, patch.object(ctx, 'save_player_data') as save:
                    self.assertFalse(runtime.handle_quest_answer(ctx))
                    record.assert_not_called()
                    save.assert_not_called()
            self.assertEqual(errors[-1], ('Bedroom search refused', '999 quest points'))
            for _ in range(6):
                _answer_review(addon)
            before = copy.deepcopy(addon._state.player_data)
            with patch.object(runtime, '_record_action') as record, patch.object(ctx, 'save_player_data') as save:
                self.assertFalse(runtime.handle_quest_answer(ctx))
                record.assert_not_called()
                save.assert_not_called()
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(errors[-1], ('Bedroom search refused', module.NO_SEARCH))

    def test_anki_veto_and_exception_roll_back_searches_proofs_and_replacements(self):
        for mode in ('new', 'proof', 'replacement'):
            for raises in (False, True):
                with self.subTest(mode=mode, raises=raises):
                    self.assert_anki_rejection(mode, raises)

    def assert_anki_rejection(self, mode, raises):
        with review_session() as (addon, collection, _errors):
            start_and_open(addon)
            if mode == 'proof':
                addon._state.player_data['inventory']["Anna's print"] = 4
            if mode == 'replacement':
                for _ in range(6):
                    _answer_review(addon)
                addon._state.player_data['inventory'].pop('Silver necklace')
            addon.save_player_data()
            before = copy.deepcopy(addon._state.player_data)
            skill, rng, journal, target = addon._state.current_skill, random.getstate(), rows(addon), next_target(addon)
            prepare_answer(addon)
            reviewer = SimpleNamespace(state='answer')

            def reject(_reviewer, _ease):
                self.assert_delta(before, addon._state.player_data, target, mode)
                if raises:
                    raise RuntimeError('Anki rejected bedroom search')
                return 'vetoed'

            if raises:
                with self.assertRaisesRegex(RuntimeError, 'Anki rejected bedroom'):
                    addon.on_answer_card(reviewer, 4, reject)
            else:
                self.assertEqual(addon.on_answer_card(reviewer, 4, reject), 'vetoed')
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store[PLAYER_KEY], before)
            self.assertEqual(addon._state.current_skill, skill)
            self.assertEqual(random.getstate(), rng)
            self.assertEqual(rows(addon), journal)
            self.assertEqual(next_target(addon), target)
