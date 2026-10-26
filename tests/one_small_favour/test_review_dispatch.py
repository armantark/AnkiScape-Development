"""Registered answers perform exactly one contact, regardless of pacing."""

import copy
import sys
import unittest
from unittest.mock import Mock, patch

from tests.one_small_favour.test_opening_transactions import player, progress
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import (
    _FakeReviewer, _install_runtime_fakes, _load_addon_as_package, _DummyMW, _DummyCol,
)
from tests.test_runtime_actions import _context
from ankiscape.data.quest.one_small_favour import (
    QUEST_ID, BLUNT_HATCHET, OPENING_PROOFS, REPLACEMENT_MESSAGE,
)
from ankiscape.logic_pure.quest_action_proofs import record_runtime_quest_action_proofs_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer


class RuntimeFixture:
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        _install_runtime_fakes()
        self.collection = _DummyCol({})
        sys.modules['aqt'].mw = _DummyMW(self.collection)
        self.addon = _load_addon_as_package('ankiscape_favour_review')
        addon = self.addon
        self.saved, self.messages, self.errors = [], [], []
        addon.show_error_message = lambda *args: self.errors.append(args)
        addon.check_achievements = lambda _data: None
        addon._refresh_skill_availability = lambda: None
        self.show_activity_gain = addon._show_activity_gain
        addon._show_activity_gain = self.messages.append
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon._state.player_data = player(started=False)
        addon._state.current_skill = 'Quests'
        addon._state.review_undo_stack.clear()
        addon._state.direct_action_undo_stack.clear()
        real_save = addon.save_player_data

        def save():
            real_save()
            self.saved.append(copy.deepcopy(addon._state.player_data))

        addon.save_player_data = save


class OpeningReviewTest(RuntimeFixture, unittest.TestCase):
    def test_seven_registered_answers_save_once_and_show_each_exact_notice(self):
        addon = self.addon
        for index, notice in enumerate(OPENING_PROOFS):
            _answer_review(addon)
            self.assertEqual(len(self.saved), index + 1)
            self.assertEqual(' '.join(self.messages[index].splitlines()[:-1]) if index == 6 else self.messages[index], notice)
            self.assertEqual(addon._state.player_data['quests'][QUEST_ID]['progress'], 2 if index == 6 else 1)
            self.assertEqual(set(addon._state.player_data['quest_action_proofs']), set(OPENING_PROOFS[:index + 1]))
        self.assertEqual(self.messages[-1].splitlines()[-1], 'One Small Favour 2/8')
        self.assertEqual(self.errors, [])

    def test_again_and_another_selected_skill_do_not_supply_a_deed(self):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)
        addon._state.card_turned = addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 1, lambda *_args: 'answered')
        self.assertEqual(addon._state.player_data['quests'], before['quests'])
        self.assertEqual(addon._state.player_data['quest_action_proofs'], [])
        addon._state.current_skill = 'Woodcutting'
        _answer_review(addon)
        self.assertEqual(addon._state.player_data['quest_action_proofs'], [])
        self.assertEqual(addon._state.player_data['inventory'][BLUNT_HATCHET], 0)

    def test_custody_refusal_saves_nothing_and_reports_the_existing_blocker(self):
        addon = self.addon
        addon._state.player_data = player(1)
        addon._state.player_data['inventory'][BLUNT_HATCHET] = 1
        before = copy.deepcopy(addon._state.player_data)
        self.assertFalse(addon.on_quest_answer())
        for key in ('inventory', 'quests', 'quest_action_proofs'):
            self.assertEqual(addon._state.player_data[key], before[key])
        self.assertEqual(self.saved, [])
        self.assertIn('cannot give you another Blunt hatchet', self.errors[0][1])

    def test_old_sentinel_and_generic_telemetry_supply_no_opening_proof(self):
        data = player()
        data['quest_action_proofs'] = ['Complete One Small Favour stage 1 objective']
        self.assertFalse(record_runtime_quest_action_proofs_pure(data, 'quest', QUEST_ID))
        after, ok, _ = progress(data)
        self.assertTrue(ok)
        self.assertEqual(set(after['quest_action_proofs']) & set(OPENING_PROOFS), {OPENING_PROOFS[0]})
        self.assertEqual(after['inventory'][BLUNT_HATCHET], 0)

    def test_multipliers_and_cadence_never_collapse_contacts_or_replacement(self):
        for multiplier in (1, 2, 10):
            for live in (False, True):
                with self.subTest(multiplier=multiplier, live=live):
                    data = player(started=False)
                    calls = {'xp': [], 'saves': 0, 'errors': []}
                    ctx = _context(data, calls, review_action_multiplier=multiplier)
                    ctx.cadence_live_enabled = live
                    for index in range(3):
                        self.assertTrue(handle_quest_answer(ctx))
                        self.assertEqual(set(data['quest_action_proofs']), set(OPENING_PROOFS[:index + 1]))
                    data['inventory'][BLUNT_HATCHET] = 0
                    self.assertTrue(handle_quest_answer(ctx))
                    self.assertEqual(calls['activity'][-1], REPLACEMENT_MESSAGE)
                    self.assertEqual(set(data['quest_action_proofs']), set(OPENING_PROOFS[:3]))
                    for index in range(3, 7):
                        self.assertTrue(handle_quest_answer(ctx))
                        self.assertEqual(set(data['quest_action_proofs']), set(OPENING_PROOFS[:index + 1]))
                    self.assertEqual(calls['saves'], 8)
                    self.assertEqual(calls['activity'][:-1], [*OPENING_PROOFS[:3], REPLACEMENT_MESSAGE, *OPENING_PROOFS[3:6]])
                    self.assertEqual(' '.join(calls['activity'][-1].splitlines()), OPENING_PROOFS[-1] + ' One Small Favour 2/8')

    def test_entrance_has_no_rng_call_and_no_thieving_xp(self):
        data = player(5)
        calls = {'xp': [], 'saves': 0, 'errors': []}
        ctx = _context(data, calls)
        ctx.random_random = Mock(side_effect=AssertionError('entrance must not roll'))
        before = data['thieving_exp']
        self.assertTrue(handle_quest_answer(ctx))
        self.assertEqual(data['thieving_exp'], before)
        ctx.random_random.assert_not_called()
