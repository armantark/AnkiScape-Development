"""Real answer hooks, one save per deed, and full Undo/replay of both routes."""

import copy
import sys
from types import SimpleNamespace
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.hazeel_opening import (
    BRANCH_DEEDS, CORRECT_VALVE_ACTIONS, ENDPOINT_SENTENCES, POISON, MARK, VALVE_KEY,
)
from ankiscape.logic_pure.quest.hazeel_journal import hazeel_completed_sentence_pure
from ankiscape.logic_pure.logic_pure_quest import can_attempt_quest_review_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.quest_catalog.hazeel_helpers import started_player, choose, branch_player, review
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _FakeReviewer, _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context

QUEST_ID = 'hazeel_cult'


def with_unrelated(player):
    player['inventory']['Feather'] = 23
    player['quest_action_proofs'].append('Unrelated genuine deed')
    return player


def action_count(player):
    return sum(row['successes'] for row in player['action_telemetry']['actions'].values()
               if row['skill_id'] == 'quest' and row['action_id'] == QUEST_ID)


class HazeelRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.original_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package('ankiscape_hazeel_e2e')
        addon = self.addon
        self.saved = []
        self.messages = []
        self.errors = []
        self.xp = []
        addon.show_error_message = lambda *args: self.errors.append(args)
        addon.save_player_data = lambda: self.saved.append(copy.deepcopy(addon._state.player_data))
        addon.check_achievements = lambda _data: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = self.messages.append
        addon._show_exp = self.xp.append
        addon.level_up_check = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        self._reset()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def _reset(self):
        self.addon._state.player_data = with_unrelated(started_player())
        self.addon._state.current_skill = 'Quests'
        self.addon._state.review_undo_stack.clear()
        self.saved.clear()
        self.messages.clear()
        self.errors.clear()
        self.xp.clear()

    def _select(self, branch):
        # A menu operation: selection is performed before the answer snapshot.
        self.addon._state.player_data = choose(self.addon._state.player_data, branch)

    def _assert_unchanged_unrelated(self, player):
        self.assertEqual(player['inventory']['Feather'], 23)
        self.assertIn('Unrelated genuine deed', player['quest_action_proofs'])

    def _assert_runtime_trace(self, branch, undo=False):
        actions = (*BRANCH_DEEDS[branch], *CORRECT_VALVE_ACTIONS)
        for index, action_id in enumerate(actions):
            if index == 2:
                self._select(branch)
            player = self.addon._state.player_data
            self.assertTrue(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
            before = copy.deepcopy(player)
            save_count = len(self.saved)
            message_count = len(self.messages)
            _answer_review(self.addon)
            after = copy.deepcopy(self.addon._state.player_data)
            self.assertEqual(len(self.saved), save_count + 1)
            self.assertEqual(action_count(after), index + 1)
            expected_messages = [hazeel_completed_sentence_pure(after, action_id)]
            if index == len(actions)-1:
                expected_messages += [ENDPOINT_SENTENCES[branch], 'Hazeel Cult 2/4']
            self.assertEqual(self.messages[message_count:], expected_messages)
            self._assert_unchanged_unrelated(after)
            self.assertEqual(self.errors, [])
            self.assertEqual(self.xp, [])
            if undo:
                self.addon._on_state_did_undo(SimpleNamespace(operation='Answer Card'))
                self.assertEqual(self.addon._state.player_data, before, action_id)
                self.addon._state.current_skill = 'Quests'
                _answer_review(self.addon)
                self.assertEqual(self.addon._state.player_data, after, action_id)
        self.assertEqual(after['quests'][QUEST_ID], dict(started=True, completed=False, progress=2))
        if branch == 'hazeel':
            self.assertEqual(after['inventory'][POISON], 0)
            self.assertEqual(after['inventory'][MARK], 1)
        self.assertEqual(len(after[VALVE_KEY]), 5)

    def test_real_answer_dispatch_both_openings(self):
        for branch in BRANCH_DEEDS:
            with self.subTest(branch=branch):
                self._reset()
                self._assert_runtime_trace(branch)

    def test_full_undo_and_replay_every_opening_action(self):
        for branch in BRANCH_DEEDS:
            with self.subTest(branch=branch):
                self._reset()
                self._assert_runtime_trace(branch, undo=True)

    def test_again_inactive_and_multiplier_do_not_perform_extra_deeds(self):
        addon = self.addon
        for player in (with_unrelated(started_player()), with_unrelated(branch_player('hazeel'))):
            addon._state.player_data = player
            before = copy.deepcopy(player)
            addon._state.card_turned = addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 1, lambda *_args: 'answered')
            self.assertEqual(addon._state.player_data['inventory'], before['inventory'])
            self.assertEqual(addon._state.player_data['quest_action_proofs'], before['quest_action_proofs'])
            addon._state.current_skill = 'Idle'
            inactive = copy.deepcopy(addon._state.player_data)
            _answer_review(addon)
            for key in ('inventory', 'quest_action_proofs', VALVE_KEY, 'quests'):
                self.assertEqual(addon._state.player_data[key], inactive[key])
            addon._state.current_skill = 'Quests'
        for multiplier in (1, 2, 10):
            for live in (False, True):
                player = with_unrelated(branch_player('hazeel'))
                calls = {'xp':[], 'saves':0, 'errors':[]}
                ctx = _context(player, calls, review_action_multiplier=multiplier)
                ctx.cadence_live_enabled = live
                self.assertTrue(handle_quest_answer(ctx))
                self.assertEqual(player['inventory'][POISON], 1)
                self.assertEqual(player['quests'][QUEST_ID]['progress'], 0)
                self.assertEqual(action_count(player), 1)
                self.assertTrue(handle_quest_answer(ctx))
                self.assertEqual(player['inventory'][POISON], 0)
                self.assertEqual(action_count(player), 2)
                self.assertNotIn(MARK, {k for k,v in player['inventory'].items() if v})
                self.assertEqual(calls['saves'], 2)
                self.assertEqual(calls['xp'], [])
                self._assert_unchanged_unrelated(player)

    def test_runtime_refusal_saves_nothing(self):
        player = with_unrelated(review(branch_player('hazeel')))
        player['inventory'][POISON] = 0
        before = copy.deepcopy(player)
        calls = {'xp':[], 'saves':0, 'errors':[]}
        self.assertFalse(handle_quest_answer(_context(player, calls)))
        self.assertEqual(player, before)
        self.assertEqual(calls['saves'], 0)
        self.assertEqual(action_count(player), 0)
        self.assertTrue(calls['deactivated'])
        self.assertEqual(calls['errors'][0][0], 'Quest blocked')
        self.assertIn('Needs Poison x1', calls['errors'][0][1])
        self._assert_unchanged_unrelated(player)
