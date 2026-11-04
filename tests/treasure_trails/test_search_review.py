"""Search trails through the loaded menu, real review, storage and Undo owners."""

import copy
import random
import sys
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

from tests import test_integration_smoke as smoke
from tests.treasure_trails.test_search_catalog import (
    SEARCH_CASES, CLUE, CASKET, fresh_player, search_draws, no_draw,
)

PLAYER_KEY = 'ankiscape_player_data'


@contextmanager
def review_session():
    modules_before, random_before = dict(sys.modules), random.getstate()
    try:
        smoke._install_runtime_fakes()
        addon = smoke._load_addon_as_package('ankiscape_eight_searches_review')
        col = smoke._DummyCol({'ankiscape_review_action_multiplier': 1,
                               'ankiscape_floating_xp_enabled': False})
        col.set_config = lambda key, value: col._store.__setitem__(key, copy.deepcopy(value))
        addon.mw = smoke._DummyMW(col)
        storage = sys.modules[f'{addon.__name__}.core.storage']
        storage.mw = addon.mw
        addon.storage_save_player_data = storage.save_player_data
        addon.storage_load_player_data = storage.load_player_data
        constants = sys.modules[f'{addon.__name__}.core.constants']
        addon._state.player_data = storage.migrate_loaded_data(
            fresh_player(), constants.ORE_DATA, constants.ITEM_DEFINITIONS,
        )
        addon._state.current_skill = 'None'
        addon._state.review_undo_stack.clear()
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.ui.show_bankstanding_dialog = lambda *_args: None
        errors = []
        addon.show_error_message = lambda title, message: errors.append((title, message))
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu(initial_skill='Activities')
        yield addon, col, captured, errors
    finally:
        random.setstate(random_before)
        sys.modules.clear()
        sys.modules.update(modules_before)


def checkpoint(addon):
    """The entire save and persisted configuration, including clocks and telemetry."""
    return (copy.deepcopy(addon._state.player_data), addon._state.current_skill,
            random.getstate(), copy.deepcopy(addon.mw.col._store))


def answer(addon, ease=3):
    addon._state.card_turned = addon._state.answer_shown = True
    addon._state.exp_awarded = False
    return addon.on_answer_card(smoke._FakeReviewer(), ease, lambda *_args: 'accepted')


def undo(addon, operation='Answer Card'):
    addon._on_state_did_undo(SimpleNamespace(
        operation=operation, changes=SimpleNamespace(study_queues=True, card=True),
    ))


def selected_command(addon, callbacks, rng):
    """Control only selection RNG delivery; restore it before any review."""
    original = addon.apply_treasure_trails_command_pure

    def deliver(data, action, payload, _rng):
        return original(data, action, payload, rng)

    with patch.object(addon, 'apply_treasure_trails_command_pure', side_effect=deliver):
        return callbacks['on_treasure_trails_command']('start_from_bank', {'tier': 'easy'})


class SearchReviewTest(unittest.TestCase):
    def start(self, addon, callbacks, step_id):
        result = selected_command(addon, callbacks, search_draws(step_id))
        self.assertTrue(result['ok'], result)
        self.assertEqual(addon._state.player_data['treasure_trail'], dict(
            version=1, tier='easy', steps=[step_id, step_id], index=0,
        ))
        # Bank Start must select reviews itself, including on a fresh profile.
        # A separate activity-selection callback hid the native selection gap.
        self.assertEqual(addon._state.current_skill, 'Activities')
        addon.check_achievements(addon._state.player_data)
        addon.save_player_data()
        addon.load_player_data()
        addon.save_player_data()

    def assert_view(self, addon, step_id, text, index):
        data = addon._state.player_data
        self.assertEqual(data['treasure_trail']['steps'], [step_id, step_id])
        self.assertEqual(data['treasure_trail']['index'], index)
        step = addon.treasure_trails_view_pure(data)['step']
        self.assertEqual((step['step_id'], step['text']), (step_id, text))

    def assert_transition(self, addon, step_id, text, index):
        data = addon._state.player_data
        self.assertEqual(data['treasure_trails_started'], 1)
        self.assertEqual(data['treasure_trails_completed'], index)
        self.assertEqual(data['treasure_trails_caskets_opened'], 0)
        self.assertEqual(data['treasure_trail_retained'], {})
        self.assertEqual(data['inventory'].get(CASKET, 0), index)
        self.assertEqual(data['inventory'].get(CLUE, 0), 1 - index)
        if index == 0:
            self.assert_view(addon, step_id, text, 1)
            self.assertEqual(data['activity_session'], {'active_id': 'treasure_trail'})
        else:
            self.assertEqual(data['treasure_trail'], {})
            self.assertEqual(data['activity_session'], {'active_id': ''})
            self.assertEqual(data['current_utility'], 'bankstanding')
            self.assertEqual(addon._state.current_skill, 'Utilities')
        telemetry = data['action_telemetry']['actions']['utility:treasure_trail']
        self.assertEqual(telemetry['successes'], index + 1)
        self.assertEqual(telemetry['attempts'], index + 1)
        self.assertEqual(telemetry['failures'], 0)

    def assert_review_replays(self, addon, step_id, text, index):
        before = checkpoint(addon)
        self.assertEqual(answer(addon), 'accepted')
        self.assert_transition(addon, step_id, text, index)
        after = checkpoint(addon)
        self.assertEqual(after[3][PLAYER_KEY], after[0])
        undo(addon)
        self.assertEqual(checkpoint(addon), before)
        self.assertEqual(answer(addon), 'accepted')
        self.assertEqual(checkpoint(addon), after)

    def test_each_search_complete_review_undo_replays(self):
        for step_id, text in SEARCH_CASES:
            with self.subTest(step_id=step_id), review_session() as (addon, _col, callbacks, errors):
                self.start(addon, callbacks, step_id)
                self.assert_view(addon, step_id, text, 0)
                self.assert_review_replays(addon, step_id, text, 0)
                self.assert_review_replays(addon, step_id, text, 1)
                self.assertEqual(errors, [])

    def test_again_does_not_resolve_new_search(self):
        for step_id, text in SEARCH_CASES:
            with self.subTest(step_id=step_id), review_session() as (addon, _col, callbacks, errors):
                self.start(addon, callbacks, step_id)
                before = copy.deepcopy(addon._state.player_data)
                self.assertEqual(answer(addon, ease=1), 'accepted')
                data = addon._state.player_data
                for key in ('treasure_trail', 'treasure_trail_retained', 'inventory',
                            'treasure_trails_completed', 'treasure_trails_caskets_opened'):
                    self.assertEqual(data[key], before[key], key)
                self.assert_view(addon, step_id, text, 0)
                self.assertEqual(errors, [])

    def assert_open_rewards(self, addon, before, result):
        self.assertTrue(result['ok'], result)
        self.assertTrue(result['rewards'])
        expected = dict(before['inventory'])
        expected.pop(CASKET)
        for item, quantity in result['rewards'].items():
            expected[item] = expected.get(item, 0) + quantity
        self.assertEqual(addon._state.player_data['inventory'], expected)
        self.assertEqual(addon._state.player_data['treasure_trails_caskets_opened'],
                         before['treasure_trails_caskets_opened'] + 1)

    def test_earned_casket_open_undo_replays(self):
        for step_id, _text in SEARCH_CASES:
            with self.subTest(step_id=step_id), review_session() as (addon, col, callbacks, errors):
                self.start(addon, callbacks, step_id)
                answer(addon)
                answer(addon)
                self.assertEqual(addon._state.player_data['inventory'].get(CASKET), 1)
                before = checkpoint(addon)
                command = callbacks['on_treasure_trails_command']
                result = command('open_casket', {'tier': 'easy'})
                self.assert_open_rewards(addon, before[0], result)
                after = checkpoint(addon)
                self.assertEqual(col._store[PLAYER_KEY], after[0])
                undo(addon, 'AnkiScape direct action')
                self.assertEqual(checkpoint(addon), before)
                self.assertEqual(command('open_casket', {'tier': 'easy'}), result)
                self.assertEqual(checkpoint(addon), after)
                self.assertEqual(errors, [])

    def assert_reopen(self, addon, col, key, expected):
        addon.save_player_data()
        stored = copy.deepcopy(col._store)
        addon._state.player_data = {}
        addon._state.current_skill = 'None'
        addon.load_player_data()
        data = addon._state.player_data
        self.assertEqual(data[key], expected)
        self.assertEqual(data['inventory'].get(CLUE), 1)
        self.assertEqual(data['inventory'].get(CASKET, 0), 0)
        self.assertEqual(data['treasure_trails_started'], 1)
        self.assertEqual(data['treasure_trails_completed'], 0)
        self.assertEqual(data['treasure_trails_caskets_opened'], 0)
        self.assertEqual(col._store, stored)
        self.assertEqual(data[key], stored[PLAYER_KEY][key])
        self.assertEqual(data, stored[PLAYER_KEY])
        self.assertEqual(addon._state.current_skill, stored['ankiscape_current_skill'])

    def test_real_save_load_preserves_new_active_and_retained_progress(self):
        for step_id, text in SEARCH_CASES:
            with self.subTest(step_id=step_id), review_session() as (addon, col, callbacks, errors):
                self.start(addon, callbacks, step_id)
                answer(addon)
                trail = copy.deepcopy(addon._state.player_data['treasure_trail'])
                self.assertEqual(trail['index'], 1)
                self.assert_reopen(addon, col, 'treasure_trail', trail)
                self.assert_view(addon, step_id, text, 1)
                result = callbacks['on_treasure_trails_command']('abandon', {})
                self.assertTrue(result['ok'], result)
                self.assert_reopen(addon, col, 'treasure_trail_retained', trail)
                before_inventory = copy.deepcopy(addon._state.player_data['inventory'])
                self.assertTrue(selected_command(addon, callbacks, no_draw)['ok'])
                self.assert_view(addon, step_id, text, 1)
                data = addon._state.player_data
                self.assertEqual(data['treasure_trails_started'], 1)
                self.assertEqual(data['treasure_trail_retained'], {})
                self.assertEqual(data['inventory'], before_inventory)
                self.assertEqual(col._store[PLAYER_KEY], data)
                self.assertEqual(errors, [])
