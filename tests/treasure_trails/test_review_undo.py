"""Complete real review and earned-casket transactions for the three searches."""

import copy
import random
import sys
import types
import unittest
from contextlib import contextmanager
from unittest.mock import patch

from tests import test_integration_smoke as smoke
from tests.treasure_trails.test_three_searches import (
    NEW_ROWS, CLUE, CASKET, SAILOR, selection_draws,
)


@contextmanager
def isolated_addon():
    modules = dict(sys.modules)
    rng_state = random.getstate()
    try:
        smoke._install_runtime_fakes()
        yield smoke._load_addon_as_package('ankiscape_three_searches_review')
    finally:
        random.setstate(rng_state)
        sys.modules.clear()
        sys.modules.update(modules)


def prepare(test, addon):
    """Stub external sinks, keeping dispatch, clocks and transaction code live."""
    addon.mw = smoke._DummyMW(smoke._DummyCol({
        'ankiscape_review_action_multiplier': 1,
        'ankiscape_floating_xp_enabled': False,
    }))
    addon.save_player_data = lambda: None
    addon.check_achievements = lambda *_args: None
    addon.update_review_hud = lambda *_args: None
    addon._refresh_skill_availability = lambda: None
    addon._show_activity_gain = lambda *_args: None
    addon._show_exp = lambda *_args: None
    addon.ui.show_bankstanding_dialog = lambda *_args: None
    addon.show_error_message = lambda _title, message: test.fail(message)
    storage = sys.modules[f'{addon.__name__}.core.storage_pure']
    constants = sys.modules[f'{addon.__name__}.core.constants']
    addon._state.player_data = storage.default_player_data(
        constants.ORE_DATA, constants.ITEM_DEFINITIONS
    )
    addon._state.player_data.update(
        inventory={CLUE: 1, 'Coins': 73, 'Logs': 4}, equipment={},
        activity_session={'active_id': ''}, treasure_trail={}, treasure_trail_retained={},
    )
    addon._state.current_skill = 'Activities'
    captured = {}
    addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
    addon._on_main_menu(initial_skill='Activities')
    return captured['on_treasure_trails_command']


def start(test, addon, step_id, length):
    callback = prepare(test, addon)
    ids = [step_id] if length == 1 else [step_id, SAILOR]
    with patch.object(addon.random, 'random', selection_draws(ids)):
        result = callback('start_from_bank', {'tier': 'easy'})
    # The real RNG is restored before any review baseline is taken.
    test.assertTrue(result['ok'], result)
    test.assertEqual(addon._state.player_data['treasure_trail']['steps'], ids)
    test.assertEqual(addon._state.player_data['treasure_trails_started'], 1)
    test.assertEqual(addon._state.current_skill, 'Activities')
    test.assertEqual(len(addon._state.direct_action_undo_stack), 1)
    return callback


def snapshot(addon):
    state = addon._state
    return {
        'save': copy.deepcopy(state.player_data),
        'skill': state.current_skill,
        'rng': random.getstate(),
        'review': copy.deepcopy(state.review_undo_stack),
        'direct': copy.deepcopy(state.direct_action_undo_stack),
        'notice': copy.deepcopy(state.pending_bankstanding_notice),
        'dialogs': list(state.pending_review_dialogs),
    }


def answer(addon, ease=4):
    addon._state.card_turned = True
    addon._state.answer_shown = True
    addon._state.exp_awarded = False
    return addon.on_answer_card(smoke._FakeReviewer(), ease, lambda *_args: 'answered')


def undo(addon, operation):
    addon._on_state_did_undo(types.SimpleNamespace(
        operation=operation, changes=types.SimpleNamespace(study_queues=True, card=True),
    ))


def assert_review_result(test, addon, before, step_id, length):
    save = addon._state.player_data
    test.assertEqual(save['treasure_trails_started'], 1)
    test.assertEqual(save['treasure_trails_caskets_opened'], 0)
    test.assertEqual(save['treasure_trail_retained'], {})
    test.assertEqual(addon._state.direct_action_undo_stack, before['direct'])
    test.assertEqual(len(addon._state.review_undo_stack), len(before['review']) + 1)
    test.assertEqual(addon._state.review_undo_stack[:-1], before['review'])
    if length == 2:
        test.assertEqual(save['treasure_trail'], {
            'version': 1, 'tier': 'easy', 'steps': [step_id, SAILOR], 'index': 1,
        })
        test.assertEqual(save['inventory'], before['save']['inventory'])
        test.assertEqual(save['treasure_trails_completed'], 0)
        test.assertEqual(save['activity_session'], {'active_id': 'treasure_trail'})
        test.assertEqual(save['current_utility'], 'treasure_trail')
        test.assertEqual(addon._state.current_skill, 'Activities')
    else:
        test.assertEqual(save['treasure_trail'], {})
        test.assertEqual(save['inventory'], {CASKET: 1, 'Coins': 73, 'Logs': 4})
        test.assertEqual(save['treasure_trails_completed'], 1)
        test.assertEqual(save['activity_session'], {'active_id': ''})
        test.assertEqual(save['current_utility'], 'bankstanding')
        test.assertEqual(addon._state.current_skill, 'Utilities')


def assert_review_replay(test, addon, step_id, length):
    start(test, addon, step_id, length)
    before = snapshot(addon)
    test.assertEqual(answer(addon), 'answered')
    assert_review_result(test, addon, before, step_id, length)
    after = snapshot(addon)
    undo(addon, 'Answer Card')
    test.assertEqual(snapshot(addon), before)
    test.assertEqual(answer(addon), 'answered')
    test.assertEqual(snapshot(addon), after)


def assert_opened(test, addon, before, expected):
    save = addon._state.player_data
    test.assertEqual(save['inventory'], expected['inventory'])
    test.assertNotIn(CASKET, save['inventory'])
    test.assertNotEqual(save['inventory'], before['save']['inventory'])
    test.assertEqual(save['treasure_trails_completed'], 1)
    test.assertEqual(save['treasure_trails_caskets_opened'], 1)
    test.assertEqual(addon._state.review_undo_stack, before['review'])
    test.assertEqual(addon._state.direct_action_undo_stack[:-1], before['direct'])
    test.assertEqual(len(addon._state.direct_action_undo_stack), len(before['direct']) + 1)


def assert_casket_replay(test, addon, step_id):
    callback = start(test, addon, step_id, 1)
    test.assertEqual(answer(addon), 'answered')
    test.assertEqual(addon._state.player_data['inventory'].get(CASKET), 1)
    before = snapshot(addon)
    # Clone the real RNG to check every earned reward without spending its draws.
    reward_rng = random.Random()
    reward_rng.setstate(before['rng'])
    logic = sys.modules[f'{addon.__name__}.logic.treasure_trails_logic']
    expected, ok, info = logic.apply_treasure_trails_command_pure(
        before['save'], 'open_casket', {'tier': 'easy'}, reward_rng.random
    )
    test.assertTrue(ok, info)
    test.assertTrue(info['rewards'])
    test.assertTrue(callback('open_casket', {'tier': 'easy'})['ok'])
    assert_opened(test, addon, before, expected)
    test.assertEqual(random.getstate(), reward_rng.getstate())
    after = snapshot(addon)
    undo(addon, 'AnkiScape direct action')
    test.assertEqual(snapshot(addon), before)
    test.assertTrue(callback('open_casket', {'tier': 'easy'})['ok'])
    test.assertEqual(snapshot(addon), after)


class ThreeSearchReviewUndoTest(unittest.TestCase):
    def test_each_new_search_review_undo_and_replay_restores_the_complete_transaction(self):
        for step_id, _ in NEW_ROWS:
            for length in (2, 1):
                with self.subTest(step_id=step_id, length=length), isolated_addon() as addon:
                    assert_review_replay(self, addon, step_id, length)

    def test_an_unsuccessful_review_does_not_resolve_a_new_search(self):
        for step_id, _ in NEW_ROWS:
            with self.subTest(step_id=step_id), isolated_addon() as addon:
                start(self, addon, step_id, 1)
                before = snapshot(addon)
                self.assertEqual(answer(addon, ease=1), 'answered')
                after = addon._state.player_data
                for key in ('treasure_trail', 'treasure_trail_retained', 'inventory',
                            'treasure_trails_started', 'treasure_trails_completed',
                            'treasure_trails_caskets_opened'):
                    self.assertEqual(after[key], before['save'][key], key)

    def test_earned_casket_open_undo_and_replay_preserves_settlement(self):
        for step_id, _ in NEW_ROWS:
            with self.subTest(step_id=step_id), isolated_addon() as addon:
                assert_casket_replay(self, addon, step_id)
