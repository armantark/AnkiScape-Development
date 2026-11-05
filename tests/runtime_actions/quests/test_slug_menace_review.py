"""Real selection, answer dispatch, persistence and full Undo/replay owners."""
import copy
import json
import random
import sys
import unittest
from types import SimpleNamespace
from textwrap import fill
from unittest.mock import Mock, patch

import pkg_alias  # noqa: F401
from tests.quest_catalog.test_murder_mystery_review import review_session, prepare_answer, PLAYER_KEY
from tests.quest_catalog.slug_menace.test_slug_menace_opening import QUEST_ID, ACTIONS, eligible
from tests.test_early_quest_item_routes import _answer_review
from tests.test_integration_smoke import _FakeReviewer

SCAN = 'Scanned Mayor Hobb with Commorb v2: two life forms. Savant is unsure what it means.'


def select(addon, original=0):
    eligible(addon._state.player_data)
    addon._state.player_data['inventory']['Commorb'] = original
    before = copy.deepcopy(addon._state.player_data)
    assert addon.on_set_quest(QUEST_ID)
    addon._select_review_action('Quests')
    assert addon._state.player_data['inventory'] == before['inventory']
    assert addon._state.player_data['quest_action_proofs'] == before['quest_action_proofs']


def encoded(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'))


def runtime_state(addon):
    state = addon._state
    # These are the action snapshot's runtime owners; card-face flags belong to Anki.
    return (state.current_skill, random.getstate(),
            copy.deepcopy(state.pending_review_dialogs), state.pending_bankstanding_notice)


class TestSlugMenaceReview(unittest.TestCase):
    def test_both_orb_branches_one_action_one_handler_save_and_exact_feedback(self):
        for original in (0, 1):
            with self.subTest(original=original), review_session(activity_feedback=True) as (addon, collection, errors):
                select(addon, original)
                popup = Mock()
                addon.mw.exp_popup = popup
                before = copy.deepcopy(addon._state.player_data)
                runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
                ctx = addon._runtime_action_context()
                with patch.object(runtime, '_record_action', wraps=runtime._record_action) as action, \
                     patch.object(addon, 'storage_save_player_data', wraps=addon.storage_save_player_data) as save, \
                     patch.object(ctx, 'show_exp') as xp, \
                     patch.object(addon, '_runtime_action_context', return_value=ctx):
                    _answer_review(addon)
                action.assert_called_once()
                self.assertEqual(action.call_args.args[1:4], ('quest', QUEST_ID, True))
                save.assert_called_once()
                notice = fill(SCAN, width=40) + '\nThe Slug Menace 2/8'
                popup.show_text.assert_called_once_with(notice)
                xp.assert_not_called()
                data = addon._state.player_data
                self.assertEqual(data['review_event_log'][-1]['text'], notice)
                self.assertEqual(data['review_event_log'][-1]['kind'], 'activity')
                self.assertEqual(data['inventory'].get('Commorb', 0), 0)
                self.assertEqual(data['inventory']['Commorb v2'], 1)
                self.assertEqual(data['quest_action_proofs'], sorted(ACTIONS))
                self.assertEqual(data['quests'][QUEST_ID], dict(started=True, completed=False, progress=2))
                self.assertEqual(data['quest_points'], before['quest_points'])
                self.assertEqual(data['pending_skill_exp_rewards'], before['pending_skill_exp_rewards'])
                self.assertEqual({k: v for k, v in data.items() if k.endswith('_exp')},
                                 {k: v for k, v in before.items() if k.endswith('_exp')})
                self.assertEqual(encoded(collection._store[PLAYER_KEY]), encoded(data))
                self.assertEqual(errors, [])

    def test_again_and_another_selected_activity_do_no_opening(self):
        for mode in ('again', 'other'):
            with self.subTest(mode=mode), review_session() as (addon, collection, errors):
                select(addon, 1)
                if mode == 'other':
                    addon._select_review_action('None')
                before = copy.deepcopy(addon._state.player_data)
                prepare_answer(addon)
                addon.on_answer_card(_FakeReviewer(), 1 if mode == 'again' else 4, lambda *_: 'answered')
                for key in ('inventory', 'quests', 'quest_action_proofs', 'quest_points'):
                    self.assertEqual(addon._state.player_data[key], before[key])
                self.assertEqual(collection._store[PLAYER_KEY]['quest_action_proofs'], [])
                self.assertEqual(errors, [])

    def test_anki_rejection_or_exception_rolls_back_complete_encoded_state(self):
        for raises in (False, True):
            with self.subTest(raises=raises), review_session() as (addon, collection, _errors):
                select(addon, 1)
                prepare_answer(addon)
                before = encoded(addon._state.player_data)
                state = runtime_state(addon)

                def reject(*_args):
                    self.assertEqual(addon._state.player_data['inventory']['Commorb v2'], 1)
                    if raises:
                        raise RuntimeError('Anki rejected answer')
                    return 'vetoed'
                if raises:
                    with self.assertRaisesRegex(RuntimeError, 'Anki rejected'):
                        addon.on_answer_card(SimpleNamespace(state='answer'), 4, reject)
                else:
                    self.assertEqual(addon.on_answer_card(SimpleNamespace(state='answer'), 4, reject), 'vetoed')
                self.assertEqual(encoded(addon._state.player_data), before)
                self.assertEqual(encoded(collection._store[PLAYER_KEY]), before)
                self.assertEqual(runtime_state(addon), state)
                self.assertEqual(addon._state.review_undo_stack, [])

    def test_scan_refusal_after_custody_and_conversations_has_no_action_or_handler_save(self):
        with review_session() as (addon, collection, errors):
            select(addon, 1)
            data = addon._state.player_data
            data['carried_inventory'] = {'a': {'Commorb': 1}, 'b': {'Commorb': 1}}
            before = encoded(data)
            module = sys.modules[f'{addon.__name__}.logic_pure.quest.the_slug_menace']
            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            ctx = addon._runtime_action_context()
            with patch.object(module, '_perform_mayor_scan_pure', return_value=False) as scan:
                with patch.object(runtime, '_record_action') as action, patch.object(ctx, 'save_player_data') as save:
                    self.assertFalse(runtime.handle_quest_answer(ctx))
                    action.assert_not_called()
                    save.assert_not_called()
                self.assertEqual(scan.call_args.args[1], list(ACTIONS[:3]))
                self.assertEqual(encoded(data), before)
                _answer_review(addon)
            self.assertEqual(encoded(collection._store[PLAYER_KEY]), encoded(addon._state.player_data))
            for key in ('inventory', 'quests', 'carried_inventory', 'quest_action_proofs'):
                self.assertEqual(addon._state.player_data[key], json.loads(before)[key])
            self.assertEqual(errors[-1], ('Investigation not completed',
                                         "The mayor's scan could not be completed. No items or quest progress changed."))

    def test_full_undo_and_deterministic_replay_both_branches(self):
        for original in (0, 1):
            with self.subTest(original=original), review_session() as (addon, collection, _errors):
                select(addon, original)
                if original:
                    addon._state.player_data['carried_inventory'] = {'a': {'Commorb': 1}, 'b': {'Commorb': 1}}
                prepare_answer(addon)
                before, before_runtime = encoded(addon._state.player_data), runtime_state(addon)
                _answer_review(addon)
                earned, earned_runtime = encoded(addon._state.player_data), runtime_state(addon)
                self.assertEqual(len(addon._state.review_undo_stack), 1)
                addon._on_state_did_undo(SimpleNamespace(
                    operation='Answer Card', changes=SimpleNamespace(study_queues=True, card=True)))
                self.assertEqual(encoded(addon._state.player_data), before)
                self.assertEqual(encoded(collection._store[PLAYER_KEY]), before)
                self.assertEqual(runtime_state(addon), before_runtime)
                self.assertEqual(addon._state.review_undo_stack, [])
                _answer_review(addon)
                self.assertEqual(encoded(addon._state.player_data), earned)
                self.assertEqual(encoded(collection._store[PLAYER_KEY]), earned)
                self.assertEqual(runtime_state(addon), earned_runtime)

    def test_actual_storage_reopen_and_reselection_never_regrant(self):
        with review_session() as (addon, collection, _errors):
            select(addon, 1)
            _answer_review(addon)
            earned = encoded(addon._state.player_data)
            for _ in range(3):
                addon._state.player_data = {}
                addon.load_player_data()
                self.assertTrue(addon.on_set_quest(QUEST_ID))
                addon._select_review_action('Quests')
                self.assertEqual(encoded(addon._state.player_data), earned)
                self.assertEqual(encoded(collection._store[PLAYER_KEY]), earned)

    def test_supported_speed_and_cadence_one_card_stops_after_opening(self):
        for multiplier, cadence in ((1, False), (6, False), (1, True), (6, True)):
            with self.subTest(multiplier=multiplier, cadence=cadence), review_session() as (addon, collection, errors):
                collection.set_config(addon._REVIEW_ACTION_MULTIPLIER_CONFIG_KEY, multiplier)
                collection.set_config(addon._CADENCE_KERNEL_CONFIG_KEY, cadence)
                select(addon)
                self.assertEqual(addon._review_action_multiplier(), multiplier)
                self.assertEqual(addon._cadence_kernel_enabled(), cadence)
                _answer_review(addon)
                self.assertEqual(addon._state.player_data['quests'][QUEST_ID]['progress'], 2)
                self.assertEqual(addon._state.player_data['quest_action_proofs'], sorted(ACTIONS))
                self.assertEqual(errors, [])
