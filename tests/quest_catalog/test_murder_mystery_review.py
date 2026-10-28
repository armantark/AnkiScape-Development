"""Murder Mystery's producer through real menu, answer, save and Undo owners."""

import copy
import random
import sys
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from tests.test_integration_smoke import (
    _DummyCol, _DummyMW, _FakeReviewer, _install_runtime_fakes, _load_addon_as_package,
)
from tests.test_early_quest_item_routes import _answer_review
from tests.quest_catalog.test_murder_mystery_opening import (
    QUEST_ID, ACTION, POT, DAGGER, OPENING_LINES, LATER_LINES,
)

PLAYER_KEY = 'ankiscape_player_data'


@contextmanager
def review_session(*, activity_feedback=False):
    original_modules, original_random = dict(sys.modules), random.getstate()
    try:
        _install_runtime_fakes()
        addon = _load_addon_as_package('ankiscape_murder_mystery_e2e')
        collection = _DummyCol()
        collection.set_config = lambda key, value: collection._store.__setitem__(key, copy.deepcopy(value))
        addon.mw = _DummyMW(collection)
        storage = sys.modules[f'{addon.__name__}.core.storage']
        storage.mw = addon.mw
        addon.storage_save_player_data = storage.save_player_data
        addon.storage_load_player_data = storage.load_player_data
        errors = []
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon.ui.update_menu_visibility = lambda *_args: None
        if not activity_feedback:
            addon._show_activity_gain = lambda _text: None
        addon._show_exp = lambda _amount: None
        addon.update_review_hud = lambda *_args: None
        constants = sys.modules[f'{addon.__name__}.core.constants']
        addon._state.player_data = storage.default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        addon._state.player_data['inventory']['Coins'] = 37
        addon._state.player_data = storage.migrate_loaded_data(
            addon._state.player_data, constants.ORE_DATA, constants.ITEM_DEFINITIONS,
        )
        addon._state.current_skill = 'None'
        addon._state.review_undo_stack.clear()
        addon.check_achievements(addon._state.player_data)
        yield addon, collection, errors
    finally:
        random.setstate(original_random)
        sys.modules.clear()
        sys.modules.update(original_modules)


def rows(addon):
    logic = sys.modules[f'{addon.__name__}.logic_pure.logic_pure_quest']
    return logic.quest_journal_rows_pure(addon._state.player_data, QUEST_ID, addon.QUEST_DATA)


def opening_state(addon):
    data = addon._state.player_data
    return {key: copy.deepcopy(data[key]) for key in (
        'inventory', 'quests', 'quest_action_proofs', 'quest_points', 'pending_skill_exp_rewards',
    )}


def prepare_answer(addon):
    addon._state.card_turned = True
    addon._state.answer_shown = True
    addon._state.exp_awarded = False


class TestMurderMysteryReview(unittest.TestCase):
    def assert_opening_earned(self, addon, before):
        data = addon._state.player_data
        expected = dict(before['inventory'])
        expected.update({POT: expected.get(POT, 0) + 1, DAGGER: expected.get(DAGGER, 0) + 1})
        self.assertEqual(data['inventory'], expected)
        self.assertEqual(data['quest_action_proofs'], [ACTION])
        self.assertEqual(data['quests'][QUEST_ID], dict(started=True, progress=2, completed=False))
        for key in ('quest_points', 'pending_skill_exp_rewards'):
            self.assertEqual(data[key], before[key])
        self.assertEqual(rows(addon), (
            dict(stage=1, lines=OPENING_LINES, completed=True, current=False),
            dict(stage=2, lines=LATER_LINES, completed=False, current=True),
        ))

    def test_menu_start_then_real_answer(self):
        with review_session() as (addon, collection, errors):
            before = opening_state(addon)
            self.assertEqual(before['quest_action_proofs'], [])
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            addon._select_review_action('Quests')
            self.assertEqual(addon._state.player_data['inventory'], before['inventory'])
            self.assertEqual(addon._state.player_data['quest_action_proofs'], [])
            self.assertEqual(addon._state.player_data['quests'][QUEST_ID]['progress'], 0)
            self.assertEqual(rows(addon)[0]['lines'], OPENING_LINES)
            _answer_review(addon)
            self.assert_opening_earned(addon, before)
            self.assertEqual(collection._store[PLAYER_KEY], addon._state.player_data)
            self.assertEqual(errors, [])

    def test_failed_ease_does_not_search(self):
        with review_session() as (addon, collection, errors):
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            addon._select_review_action('Quests')
            before = opening_state(addon)
            prepare_answer(addon)
            addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: 'answered')
            self.assertEqual(opening_state(addon), before)
            self.assertEqual(collection._store[PLAYER_KEY]['quest_action_proofs'], [])
            self.assertEqual(errors, [])

    def test_undo_replay_restores_items_proof_journal(self):
        with review_session() as (addon, collection, _errors):
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            addon._select_review_action('Quests')
            before = copy.deepcopy(addon._state.player_data)
            before_skill, before_rng, before_rows = addon._state.current_skill, random.getstate(), rows(addon)
            _answer_review(addon)
            self.assert_opening_earned(addon, before)
            earned = copy.deepcopy(addon._state.player_data)
            earned_rng = random.getstate()
            self.assertEqual(len(addon._state.review_undo_stack), 1)
            addon._on_state_did_undo(SimpleNamespace(
                operation='Answer Card', changes=SimpleNamespace(study_queues=True, card=True),
            ))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store[PLAYER_KEY], before)
            self.assertEqual(addon._state.current_skill, before_skill)
            self.assertEqual(random.getstate(), before_rng)
            self.assertEqual(rows(addon), before_rows)
            self.assertEqual(addon._state.review_undo_stack, [])
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, earned)
            self.assertEqual(random.getstate(), earned_rng)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data['inventory'], earned['inventory'])
            self.assertEqual(addon._state.player_data['quest_action_proofs'], [ACTION])
            self.assertEqual(addon._state.player_data['quests'][QUEST_ID]['progress'], 2)

    def test_saved_opening_reopens_without_regrant(self):
        with review_session() as (addon, collection, _errors):
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            addon._select_review_action('Quests')
            _answer_review(addon)
            earned, earned_rows = opening_state(addon), rows(addon)
            addon.save_player_data()
            persisted = copy.deepcopy(collection._store[PLAYER_KEY])
            addon._state.player_data = {}
            addon.load_player_data()
            self.assertEqual(opening_state(addon), earned)
            self.assertEqual(rows(addon), earned_rows)
            self.assertEqual(collection._store[PLAYER_KEY], persisted)
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            addon._select_review_action('Quests')
            addon.load_player_data()
            self.assertEqual(opening_state(addon), earned)
            self.assertEqual(rows(addon), earned_rows)
            _answer_review(addon)
            self.assertEqual(opening_state(addon), earned)

    def test_answer_rejection_and_late_grant_refusal_rollback(self):
        for raises in (False, True):
            with self.subTest(raises=raises):
                self._assert_anki_rejection(raises)
        with review_session() as (addon, collection, errors):
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            addon._select_review_action('Quests')
            before = copy.deepcopy(addon._state.player_data)
            module = sys.modules[f'{addon.__name__}.logic_pure.quest.murder_mystery']
            real_grant = module._grant_opening_item_pure

            def late_refusal(inventory, name, quantity):
                if name == DAGGER:
                    return False
                return real_grant(inventory, name, quantity)

            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            ctx = addon._runtime_action_context()
            with patch.object(module, '_grant_opening_item_pure', side_effect=late_refusal) as grant:
                with patch.object(runtime, '_record_action') as action, patch.object(ctx, 'save_player_data') as save:
                    self.assertFalse(runtime.handle_quest_answer(ctx))
                    action.assert_not_called()
                    save.assert_not_called()
                self.assertEqual([c.args[1] for c in grant.call_args_list], [POT, DAGGER])
                self.assertEqual(addon._state.player_data, before)
                _answer_review(addon)
            for key, value in opening_state_from(before).items():
                self.assertEqual(addon._state.player_data[key], value)
                self.assertEqual(collection._store[PLAYER_KEY][key], value)
            self.assertEqual(errors[-1], ('Evidence not collected',
                                         'The evidence could not be collected. No items or quest progress changed.'))
            self.assertEqual(rows(addon)[0]['completed'], False)

    def _assert_anki_rejection(self, raises):
        with review_session() as (addon, collection, _errors):
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            addon._select_review_action('Quests')
            before, before_rows = copy.deepcopy(addon._state.player_data), rows(addon)
            before_rng, before_skill = random.getstate(), addon._state.current_skill
            prepare_answer(addon)
            reviewer = SimpleNamespace(state='answer')

            def reject(_reviewer, _ease):
                self.assertEqual(addon._state.player_data['inventory'][POT], 1)
                self.assertEqual(addon._state.player_data['quest_action_proofs'], [ACTION])
                if raises:
                    raise RuntimeError('Anki rejected answer')
                return 'vetoed'

            if raises:
                with self.assertRaisesRegex(RuntimeError, 'Anki rejected'):
                    addon.on_answer_card(reviewer, 4, reject)
            else:
                self.assertEqual(addon.on_answer_card(reviewer, 4, reject), 'vetoed')
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store[PLAYER_KEY], before)
            self.assertEqual(addon._state.current_skill, before_skill)
            self.assertEqual(random.getstate(), before_rng)
            self.assertEqual(rows(addon), before_rows)
            self.assertEqual(addon._state.review_undo_stack, [])


def opening_state_from(data):
    return {key: data[key] for key in (
        'inventory', 'quests', 'quest_action_proofs', 'quest_points', 'pending_skill_exp_rewards',
    )}
