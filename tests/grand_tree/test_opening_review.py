"""Installed review dispatch, selection and ordinary earned Agility eligibility."""

import copy
import random
import sys
import unittest
from contextlib import contextmanager
from unittest.mock import patch

import pkg_alias  # noqa: F401
from tests.test_integration_smoke import (
    _DummyCol, _DummyMW, _FakeReviewer, _install_runtime_fakes, _load_addon_as_package,
)
from tests.test_early_quest_item_routes import _answer_review
from ankiscape.data.quest.grand_tree import QUEST_ID, PROOFS, PHASE_NOTICES
from tests.grand_tree.test_opening_transactions import BARK, BOOK, SCROLL, BOUNDARIES

PLAYER_KEY = 'ankiscape_player_data'


@contextmanager
def review_session(eligible=True, capture_notices=True):
    original_modules, original_random = dict(sys.modules), random.getstate()
    try:
        _install_runtime_fakes()
        addon = _load_addon_as_package('ankiscape_grand_tree_e2e')
        collection = _DummyCol()
        collection.set_config = lambda key, value: collection._store.__setitem__(key, copy.deepcopy(value))
        addon.mw = _DummyMW(collection)
        storage = sys.modules[f'{addon.__name__}.core.storage']
        storage.mw = addon.mw
        addon.storage_save_player_data = storage.save_player_data
        addon.storage_load_player_data = storage.load_player_data
        errors, notices = [], []
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon.ui.update_menu_visibility = lambda *_: None
        if capture_notices:
            addon._show_activity_gain = notices.append
        addon._show_exp = lambda *_, **__: None
        addon.update_review_hud = lambda *_: None
        sys.modules[f'{addon.__name__}.core.logic'].show_level_up_dialog = lambda *_: None
        constants = sys.modules[f'{addon.__name__}.core.constants']
        addon._state.player_data = storage.default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        if eligible:
            addon._state.player_data = storage.migrate_loaded_data(
                addon._state.player_data, constants.ORE_DATA, constants.ITEM_DEFINITIONS,
            )
            addon._state.player_data['agility_level'] = 25
        addon._state.current_skill = 'None'
        addon._state.review_undo_stack.clear()
        addon.check_achievements(addon._state.player_data)
        yield addon, collection, errors, notices
    finally:
        random.setstate(original_random)
        sys.modules.clear()
        sys.modules.update(original_modules)


def rows(addon):
    logic = sys.modules[f'{addon.__name__}.logic_pure.logic_pure_quest']
    return logic.quest_journal_rows_pure(addon._state.player_data, QUEST_ID, addon.QUEST_DATA)


def activate(addon):
    if not addon.on_set_quest(QUEST_ID):
        raise AssertionError('Grand Tree selection refused')
    addon._select_review_action('Quests')


def prepare_answer(addon):
    addon._state.card_turned = True
    addon._state.answer_shown = True
    addon._state.exp_awarded = False


def reward_state(data):
    return {key: copy.deepcopy(value) for key, value in data.items()
            if key.endswith(('_exp', '_level')) or key in ('quest_points', 'pending_skill_exp_rewards', 'claims')}


class OpeningReviewTest(unittest.TestCase):
    def assert_boundary(self, addon, boundary):
        data = addon._state.player_data
        progress, count = BOUNDARIES[boundary]
        self.assertEqual(data['quests'][QUEST_ID], dict(started=True, progress=progress, completed=False))
        self.assertEqual(set(data['quest_action_proofs']) & set(PROOFS), set(PROOFS[:count]))
        self.assertEqual(tuple(data['inventory'].get(item, 0) for item in (BARK, BOOK, SCROLL)),
                         ((0, 0, 0), (1, 1, 0), (0, 1, 1), (0, 1, 1), (0, 1, 1))[boundary])

    def test_actual_selection_activation_and_four_real_answers(self):
        with review_session() as (addon, collection, errors, notices):
            rewards = reward_state(addon._state.player_data)
            activate(addon)
            self.assert_boundary(addon, 0)
            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            for boundary, phase in enumerate(PHASE_NOTICES, 1):
                with patch.object(runtime, '_record_action', wraps=runtime._record_action) as record:
                    _answer_review(addon)
                self.assert_boundary(addon, boundary)
                quest_records = [c for c in record.call_args_list if c.args[1:3] == ('quest', QUEST_ID)]
                self.assertEqual(len(quest_records), 1)
                self.assertEqual(' '.join(notices[-1].splitlines()), PHASE_NOTICES[phase])
                self.assertEqual(collection._store[PLAYER_KEY], addon._state.player_data)
                self.assertEqual(reward_state(addon._state.player_data), rewards)
            earned = copy.deepcopy(addon._state.player_data)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data['inventory'], earned['inventory'])
            self.assertEqual(addon._state.player_data['quest_action_proofs'], earned['quest_action_proofs'])
            self.assertEqual(addon._state.player_data['quests'][QUEST_ID], earned['quests'][QUEST_ID])
            self.assertTrue(any('stage 3 objective' in message for _, message in errors))

    def test_again_performs_no_bundle_at_every_boundary(self):
        with review_session() as (addon, collection, errors, _notices):
            activate(addon)
            for _ in range(4):
                before = copy.deepcopy(addon._state.player_data)
                prepare_answer(addon)
                addon.on_answer_card(_FakeReviewer(), 1, lambda *_: 'answered')
                self.assertEqual(addon._state.player_data['inventory'], before['inventory'])
                self.assertEqual(addon._state.player_data['quest_action_proofs'], before['quest_action_proofs'])
                self.assertEqual(addon._state.player_data['quests'], before['quests'])
                self.assertEqual(collection._store[PLAYER_KEY]['inventory'], before['inventory'])
                _answer_review(addon)
            self.assertEqual(errors, [])

    def test_runtime_handler_records_and_saves_once_per_success(self):
        with review_session() as (addon, _collection, errors, notices):
            activate(addon)
            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            ctx = addon._runtime_action_context()
            rewards = reward_state(ctx.player_data)
            for boundary, phase in enumerate(PHASE_NOTICES, 1):
                with patch.object(runtime, '_record_action', wraps=runtime._record_action) as record:
                    with patch.object(ctx, 'save_player_data', wraps=ctx.save_player_data) as save:
                        self.assertTrue(runtime.handle_quest_answer(ctx))
                record.assert_called_once_with(ctx, 'quest', QUEST_ID, True, expected_success_chance=1.0)
                save.assert_called_once_with()
                self.assert_boundary(addon, boundary)
                self.assertEqual(' '.join(notices[-1].splitlines()), PHASE_NOTICES[phase])
                self.assertEqual(reward_state(ctx.player_data), rewards)
            self.assertEqual(errors, [])

    def test_agility_24_selection_and_eligibility_loss_after_selection(self):
        with review_session() as (addon, _collection, _errors, _notices):
            addon._state.player_data['agility_level'] = 24
            before = copy.deepcopy(addon._state.player_data)
            self.assertFalse(addon.on_set_quest(QUEST_ID))
            self.assertEqual(addon._state.player_data, before)
            addon._state.player_data['agility_level'] = 25
            activate(addon)
            addon._state.player_data['agility_level'] = 24
            before = copy.deepcopy(addon._state.player_data)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data['inventory'], before['inventory'])
            self.assertEqual(addon._state.player_data['quests'], before['quests'])
            self.assertEqual(addon._state.player_data['quest_action_proofs'], [])
            self.assertNotEqual(addon._state.current_skill, 'Quests')

    def test_default_player_earns_agility_25_on_gnome_course_then_opens_quest(self):
        with review_session(eligible=False) as (addon, _collection, errors, notices):
            initial = copy.deepcopy(addon._state.player_data)
            self.assertEqual(initial['agility_level'], 1)
            self.assertEqual(initial['agility_exp'], 0)
            self.assertFalse(addon.on_set_quest(QUEST_ID))
            errors.clear()
            addon._set_value('current_agility', 'gnome_normal')
            addon._select_review_action('Agility')
            answers = self._earn_agility_25(addon)
            self.assertGreater(answers, 0)
            self.assertGreater(addon._state.player_data['agility_exp'], initial['agility_exp'])
            self.assertEqual(addon._state.player_data['quest_action_proofs'], [])
            self.assertTrue(all(addon._state.player_data['inventory'].get(item, 0) == 0 for item in (BARK, BOOK, SCROLL)))
            activate(addon)
            rewards = reward_state(addon._state.player_data)
            for boundary in range(1, 5):
                _answer_review(addon)
                self.assert_boundary(addon, boundary)
            self.assertEqual(reward_state(addon._state.player_data), rewards)
            self.assertEqual([' '.join(notice.splitlines()) for notice in notices[-4:]], list(PHASE_NOTICES.values()))
            self.assertFalse(any(s['completed'] for q, s in addon._state.player_data['quests'].items() if q != QUEST_ID))
            self.assertEqual(errors, [])

    def _earn_agility_25(self, addon):
        for answers in range(5000):
            if addon._state.player_data['agility_level'] >= 25:
                return answers
            self.assertEqual(addon._state.current_skill, 'Agility')
            _answer_review(addon)
        self.fail('5,000-answer test timeout while earning Agility 25')
