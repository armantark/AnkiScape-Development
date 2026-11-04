"""Real answer dispatch, collection persistence and Undo of complete interactions."""

import copy
from contextlib import contextmanager
import random
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.runtime.runtime_actions_quest import handle_quest_answer
from tests.quest_catalog.test_murder_mystery_review import review_session, PLAYER_KEY, prepare_answer
from tests.quest_catalog.test_toktz_opening import (
    player, QUEST_ID, TABLET, GUIDE, PROOFS, COMPLETED_LINES, RECOVERY_MESSAGE,
)
from tests.test_early_quest_item_routes import _answer_review
from tests.test_integration_smoke import _FakeReviewer
from tests.test_runtime_actions import _context


@contextmanager
def session(prefix=0, guide=0):
    with review_session() as (addon, collection, errors):
        constants = sys.modules[f'{addon.__name__}.core.constants']
        storage = sys.modules[f'{addon.__name__}.core.storage']
        data = player(prefix, started=False if prefix == 0 else True, progress=1 if prefix else 0)
        if guide:
            data['inventory'][GUIDE] = guide
        addon._state.player_data = storage.migrate_loaded_data(data, constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        addon.save_player_data()
        messages = []
        addon._show_activity_gain = messages.append
        assert addon.on_set_quest(QUEST_ID)
        addon._select_review_action('Quests')
        yield addon, collection, errors, messages


def rows(addon):
    logic = sys.modules[f'{addon.__name__}.logic_pure.logic_pure_quest']
    return logic.quest_journal_rows_pure(addon._state.player_data, QUEST_ID, addon.QUEST_DATA)


def snapshot(addon):
    data = addon._state.player_data
    return {key: copy.deepcopy(data.get(key)) for key in (
        'inventory', 'quests', 'quest_action_proofs', 'quest_points', 'pending_skill_exp_rewards',
        'quest_route_states', 'quest_combat_encounters',
    )}, rows(addon)


def undo(addon):
    addon._on_state_did_undo(SimpleNamespace(
        operation='Answer Card', changes=SimpleNamespace(study_queues=True, card=True),
    ))


class ToktzRuntimeTest(unittest.TestCase):
    def test_five_reviews_save_once_record_once_reload_each_transaction(self):
        with session() as (addon, collection, errors, messages):
            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            before = copy.deepcopy(addon._state.player_data)
            with patch.object(runtime, '_record_action', wraps=runtime._record_action) as record, patch.object(addon, 'save_player_data', wraps=addon.save_player_data) as save:
                for index in range(5):
                    _answer_review(addon)
                    self.assertEqual(record.call_count, index + 1)
                    self.assertEqual(save.call_count, index + 1)
                    self.assertEqual(addon._state.player_data['quest_action_proofs'], sorted(PROOFS[:index + 1]))
                    self.assertEqual(addon._state.player_data['quests'][QUEST_ID]['progress'], 2 if index == 4 else 1)
                    self.assertEqual(messages, list(COMPLETED_LINES[:index + 1]))
                    saved = snapshot(addon)
                    self.assertEqual(collection._store[PLAYER_KEY], addon._state.player_data)
                    addon.load_player_data()
                    self.assertEqual(snapshot(addon), saved)
            self.assertEqual(errors, [])
            self.assertEqual(addon._state.player_data['quest_points'], before['quest_points'])
            self.assertEqual(addon._state.player_data['pending_skill_exp_rewards'], before['pending_skill_exp_rewards'])
            for key, value in before.items():
                if key.endswith('_exp'):
                    self.assertEqual(addon._state.player_data[key], value)

    def test_undo_each_interaction_and_replay_matches_persistence(self):
        for owned_guide in (0, 1):
            with session(guide=owned_guide) as (addon, collection, errors, _messages):
                for index in range(5):
                    before, before_rng = copy.deepcopy(addon._state.player_data), random.getstate()
                    before_rows = rows(addon)
                    _answer_review(addon)
                    earned, earned_rng = copy.deepcopy(addon._state.player_data), random.getstate()
                    earned_rows = rows(addon)
                    undo(addon)
                    self.assertEqual(addon._state.player_data, before)
                    self.assertEqual(collection._store[PLAYER_KEY], before)
                    self.assertEqual(rows(addon), before_rows)
                    self.assertEqual(random.getstate(), before_rng)
                    if index == 4:
                        self.assertEqual(addon._state.player_data['inventory'].get(GUIDE, 0), owned_guide)
                    _answer_review(addon)
                    self.assertEqual(addon._state.player_data, earned)
                    self.assertEqual(collection._store[PLAYER_KEY], earned)
                    self.assertEqual(rows(addon), earned_rows)
                    self.assertEqual(random.getstate(), earned_rng)
                self.assertEqual(errors, [])

    def test_recovery_undo_replay_then_librarian(self):
        with session(2) as (addon, collection, errors, messages):
            addon._state.player_data['inventory'].pop(TABLET)
            addon.save_player_data()
            before, before_rows = copy.deepcopy(addon._state.player_data), rows(addon)
            _answer_review(addon)
            earned = copy.deepcopy(addon._state.player_data)
            self.assertEqual(messages, [RECOVERY_MESSAGE])
            self.assertEqual(earned['quest_action_proofs'], sorted(PROOFS[:2]))
            self.assertEqual(earned['quests'], before['quests'])
            undo(addon)
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store[PLAYER_KEY], before)
            self.assertEqual(rows(addon), before_rows)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, earned)
            addon.load_player_data()
            self.assertEqual(addon._state.player_data['inventory'][TABLET], 1)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data['quest_action_proofs'], sorted(PROOFS[:3]))
            self.assertEqual(addon._state.player_data['inventory'][TABLET], 1)
            self.assertEqual(errors, [])

    def test_again_and_another_activity_do_no_opening_deed(self):
        with session() as (addon, collection, _errors, messages):
            before = snapshot(addon)
            prepare_answer(addon)
            addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: 'answered')
            self.assertEqual(snapshot(addon), before)
            addon._state.player_data['current_utility'] = 'bankstanding'
            addon._select_review_action('Utility')
            _answer_review(addon)
            self.assertEqual(snapshot(addon), before)
            self.assertEqual(collection._store[PLAYER_KEY]['quest_action_proofs'], [])
            self.assertNotIn(COMPLETED_LINES[0], messages)

    def test_interruption_before_anki_commit_rolls_back_complete_interaction(self):
        for prefix in range(5):
            for raises in (False, True):
                self._assert_interrupted(prefix, raises)

    def _assert_interrupted(self, prefix, raises):
        with session(prefix) as (addon, collection, _errors, _messages):
            before, before_rows = copy.deepcopy(addon._state.player_data), rows(addon)
            before_rng, before_skill = random.getstate(), addon._state.current_skill
            prepare_answer(addon)

            def reject(_reviewer, _ease):
                self.assertEqual(addon._state.player_data['quest_action_proofs'], sorted(PROOFS[:prefix + 1]))
                if raises:
                    raise RuntimeError('Anki rejected answer')
                return 'vetoed'
            if raises:
                with self.assertRaisesRegex(RuntimeError, 'Anki rejected'):
                    addon.on_answer_card(SimpleNamespace(state='answer'), 4, reject)
            else:
                self.assertEqual(addon.on_answer_card(SimpleNamespace(state='answer'), 4, reject), 'vetoed')
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store[PLAYER_KEY], before)
            self.assertEqual(rows(addon), before_rows)
            self.assertEqual(random.getstate(), before_rng)
            self.assertEqual(addon._state.current_skill, before_skill)

    def test_delivery_refusal_has_specific_message_without_success_side_effects(self):
        for prefix in (1, 4):
            with session(prefix) as (addon, collection, errors, messages):
                module = sys.modules[f'{addon.__name__}.logic_pure.quest.toktz_opening']
                runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
                ctx = addon._runtime_action_context()
                before = copy.deepcopy(addon._state.player_data)

                def fail(inventory, name):
                    inventory[name] = 1
                    return False
                with patch.object(module, '_grant_unique_opening_item_pure', side_effect=fail), patch.object(runtime, '_record_action') as record, patch.object(ctx, 'save_player_data') as save:
                    self.assertFalse(runtime.handle_quest_answer(ctx))
                    record.assert_not_called()
                    save.assert_not_called()
                self.assertEqual(addon._state.player_data, before)
                self.assertEqual(collection._store[PLAYER_KEY], before)
                self.assertEqual(messages, [])
                self.assertEqual(errors[-1], ('Quest item not received', 'The quest item could not be added. No opening progress was saved.'))

    def test_multiplier_and_cadence_keep_five_interactions(self):
        for multiplier in (1, 2, 10):
            for cadence in (False, True):
                self._assert_cadence(multiplier, cadence)

    def _assert_cadence(self, multiplier, cadence):
        data = player()
        calls = {'xp': [], 'saves': 0, 'errors': []}
        ctx = _context(data, calls, review_action_multiplier=multiplier)
        ctx.cadence_live_enabled = cadence
        with patch('ankiscape.runtime.runtime_actions_quest._record_action') as record:
            for index in range(5):
                self.assertTrue(handle_quest_answer(ctx))
                self.assertEqual(record.call_count, index + 1)
                self.assertEqual(calls['saves'], index + 1)
                self.assertEqual(data['quest_action_proofs'], sorted(PROOFS[:index + 1]))
        self.assertEqual(calls['activity'], list(COMPLETED_LINES))
        self.assertEqual(calls['xp'], [])
        self.assertEqual(data['inventory'][TABLET], 1)
        self.assertEqual(data['inventory'][GUIDE], 1)
        self.assertEqual(data['quest_points'], 0)

    def test_unrelated_blocker_keeps_ordinary_refusal(self):
        data = player()
        calls = {'xp': [], 'saves': 0, 'errors': []}
        ctx = _context(data, calls)
        unrelated = ({'kind': 'required_inventory', 'reason': 'Need unrelated item'},)
        with patch('ankiscape.runtime.runtime_actions_quest.quest_current_stage_blockers_pure', return_value=unrelated), patch(
            'ankiscape.logic_pure.logic_pure_quest.quest_current_stage_blockers_pure', return_value=unrelated,
        ):
            self.assertFalse(handle_quest_answer(ctx))
        self.assertEqual(calls['saves'], 0)
        self.assertEqual(calls['errors'][0][0], 'Quest blocked')
        self.assertEqual(data['quest_action_proofs'], [])
