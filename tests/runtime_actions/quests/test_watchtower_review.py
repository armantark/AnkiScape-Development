"""Real answer wrapper, shallow snapshots and Watchtower investigation custody."""

import copy
from contextlib import contextmanager
import random
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.quest_catalog.test_watchtower_opening import player, PROOFS, QUEST_ID
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _FakeReviewer, _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context

MESSAGES = (
    'The Watchtower Wizard asked you to investigate the missing power crystals. You can now use the ladder.',
    'You searched the bushes outside the Watchtower and found Fingernails. Return them to the Wizard.',
    'The Wizard took the Fingernails and identified the thieves as Skavids, servants of the ogres. He asked you to recover the four crystals.',
)


@contextmanager
def review_session(phase=0):
    original_modules, original_rng = dict(sys.modules), random.getstate()
    try:
        _install_runtime_fakes()
        addon = _load_addon_as_package('ankiscape_watchtower_e2e')
        saved, messages, errors = [], [], []
        addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
        addon.show_error_message = lambda *args: errors.append(args)
        addon.check_achievements = lambda _data: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = messages.append
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon._state.player_data = player(phase)
        addon._state.current_skill = 'Quests'
        addon._state.review_undo_stack.clear()
        yield addon, saved, messages, errors
    finally:
        random.setstate(original_rng)
        sys.modules.clear()
        sys.modules.update(original_modules)


def checkpoint(addon):
    state = addon._state
    return (copy.deepcopy(state.player_data), state.current_skill, random.getstate(),
            list(state.pending_review_dialogs), state.pending_bankstanding_notice)


def prepare_answer(addon):
    addon._state.card_turned = addon._state.answer_shown = True
    addon._state.exp_awarded = False


def investigation(data):
    return tuple(copy.deepcopy(data[key]) for key in ('inventory', 'quests', 'quest_action_proofs'))


class WatchtowerReviewTest(unittest.TestCase):
    def test_real_dispatch_exact_feedback_and_one_handler_save_each(self):
        with review_session() as (addon, saved, messages, errors):
            for phase in range(3):
                _answer_review(addon)
                self.assertEqual(len(saved), phase + 1)
                self.assertEqual([' '.join(text.split()) for text in messages], list(MESSAGES[:phase + 1]))
                self.assertEqual(saved[-1]['quest_action_proofs'], sorted(PROOFS[:phase + 1]))
                self.assertEqual(saved[-1]['quests'][QUEST_ID]['progress'], 2 if phase == 2 else 1)
                self.assertEqual(saved[-1]['inventory'].get('Fingernails', 0), 1 if phase == 1 else 0)
            self.assertEqual(errors, [])

    def test_undo_replay_every_answer_restores_complete_checkpoint(self):
        with review_session() as (addon, _saved, _messages, _errors):
            data = addon._state.player_data
            data.pop('activity_session', None)
            data.pop('action_telemetry', None)
            data['unrelated_nested'] = {'keep': [1, {'value': 2}]}
            for phase in range(3):
                before = checkpoint(addon)
                # Guard the production snapshot: review_answer=True deliberately
                # shares nested stores, so transactions must replace them.
                shallow = addon._capture_player_data_snapshot(review_answer=True)
                self.assertIs(shallow['player_data']['inventory'], data['inventory'])
                _answer_review(addon)
                earned = checkpoint(addon)
                self.assertEqual(len(addon._state.review_undo_stack), phase + 1)
                addon._on_state_did_undo(SimpleNamespace(operation='Answer Card'))
                self.assertEqual(checkpoint(addon), before)
                _answer_review(addon)
                self.assertEqual(checkpoint(addon), earned)
                data = addon._state.player_data
                self.assertEqual(data['quest_action_proofs'], sorted(PROOFS[:phase + 1]))
                self.assertEqual(data['inventory'].get('Fingernails', 0), 1 if phase == 1 else 0)

    def test_anki_veto_and_answer_exception_rollback_every_phase(self):
        for phase in range(3):
            for raises in (False, True):
                with self.subTest(phase=phase, raises=raises):
                    self._assert_rejection(phase, raises)

    def _assert_rejection(self, phase, raises):
        with review_session(phase) as (addon, _saved, _messages, _errors):
            state = addon._state
            state.pending_review_dialogs.append(lambda: None)
            state.pending_bankstanding_notice = None
            before = checkpoint(addon)
            prepare_answer(addon)
            reviewer = SimpleNamespace(state='answer')

            def reject(_reviewer, _ease):
                self.assertIn(PROOFS[phase], state.player_data['quest_action_proofs'])
                state.pending_review_dialogs.append(lambda: None)
                state.pending_bankstanding_notice = {'reason': 'candidate notice', 'show_dialog': False}
                random.random()
                if raises:
                    raise RuntimeError('Anki rejected answer')
                return 'vetoed'
            if raises:
                with self.assertRaisesRegex(RuntimeError, 'Anki rejected'):
                    addon.on_answer_card(reviewer, 4, reject)
            else:
                self.assertEqual(addon.on_answer_card(reviewer, 4, reject), 'vetoed')
            self.assertEqual(checkpoint(addon), before)
            self.assertEqual(state.review_undo_stack, [])
            self.assertTrue(state.answer_shown)

    def test_again_and_another_activity_preserve_investigation_each_phase(self):
        for phase in range(3):
            with review_session(phase) as (addon, _saved, messages, _errors):
                before = investigation(addon._state.player_data)
                prepare_answer(addon)
                addon.on_answer_card(_FakeReviewer(), 1, lambda *_args: 'answered')
                self.assertEqual(investigation(addon._state.player_data), before)
                addon._state.current_skill = 'Woodcutting'
                _answer_review(addon)
                # Other activity may produce logs; it cannot touch opening custody.
                current = addon._state.player_data
                self.assertEqual(current['quests'], before[1])
                self.assertEqual(current['quest_action_proofs'], before[2])
                self.assertEqual(current['inventory'].get('Fingernails', 0), before[0].get('Fingernails', 0))
                self.assertFalse(any(' '.join(message.split()) in MESSAGES for message in messages))

    def test_multipliers_and_both_cadences_perform_one_phase_per_answer(self):
        for multiplier in (1, 2, 10):
            for live in (False, True):
                self._assert_cadence(multiplier, live)

    def _assert_cadence(self, multiplier, live):
        data = player()
        calls = {'xp': [], 'saves': 0, 'errors': []}
        ctx = _context(data, calls, review_action_multiplier=multiplier)
        ctx.cadence_live_enabled = live
        for phase in range(3):
            self.assertTrue(handle_quest_answer(ctx))
            self.assertEqual(data['quest_action_proofs'], sorted(PROOFS[:phase + 1]))
            self.assertEqual(data['quests'][QUEST_ID]['progress'], 2 if phase == 2 else 1)
            self.assertEqual(data['inventory'].get('Fingernails', 0), 1 if phase == 1 else 0)
            self.assertEqual(calls['saves'], phase + 1)
        self.assertEqual([' '.join(text.split()) for text in calls['activity']], list(MESSAGES))
        self.assertEqual(calls['xp'], [])
        self._assert_wrapper_cadence(multiplier, live)

    def _assert_wrapper_cadence(self, multiplier, live):
        with review_session() as (addon, saved, messages, errors):
            addon._review_action_multiplier = lambda: multiplier
            addon._cadence_kernel_enabled = lambda: live
            for phase in range(3):
                _answer_review(addon)
                data = addon._state.player_data
                self.assertEqual(data['quest_action_proofs'], sorted(PROOFS[:phase + 1]))
                self.assertEqual(data['quests'][QUEST_ID]['progress'], 2 if phase == 2 else 1)
                self.assertEqual(data['inventory'].get('Fingernails', 0), 1 if phase == 1 else 0)
                self.assertEqual(len(saved), phase + 1)
            self.assertEqual([' '.join(text.split()) for text in messages], list(MESSAGES))
            self.assertEqual(errors, [])

    def test_ordinary_blocker_matches_equivalent_wrapper_control(self):
        with review_session(2) as (addon, _saved, _messages, errors):
            addon._state.player_data['inventory']['Fingernails'] = 0
            before = checkpoint(addon)
            opening = investigation(before[0])
            _answer_review(addon)
            blocked = checkpoint(addon)
            self.assertEqual(investigation(blocked[0]), opening)
            self.assertIn('Needs Fingernails x1', errors[0][1])
            addon._state.player_data = copy.deepcopy(before[0])
            addon._state.current_skill = before[1]
            random.setstate(before[2])
            # Equivalent non-investigation blocker has the same normal wrapper
            # clocks, telemetry and deactivation effects as a missing clue.
            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            with patch.object(runtime, 'quest_review_ready_pure', return_value=False):
                with patch.object(runtime, 'apply_quest_progress_pure') as service:
                    _answer_review(addon)
                service.assert_not_called()
            self.assertEqual(checkpoint(addon), blocked)

    def test_failed_mutation_and_proof_do_not_record_or_save_handler(self):
        with review_session() as (addon, saved, _messages, _errors):
            service = sys.modules[f'{addon.__name__}.logic_pure.quest.watchtower']
            runtime = sys.modules[f'{addon.__name__}.runtime.runtime_actions_quest']
            before = checkpoint(addon)
            with patch.object(service, 'record_runtime_quest_action_proofs_pure', return_value=False):
                with patch.object(runtime, '_record_action') as record:
                    self.assertFalse(runtime.handle_quest_answer(_context(addon._state.player_data)))
                record.assert_not_called()
            self.assertEqual(checkpoint(addon), before)
            self.assertEqual(saved, [])
