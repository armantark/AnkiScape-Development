"""Notify for the Cook's preparation XP while preserving completion handling."""

import sys
import unittest
from unittest.mock import Mock, patch

import pkg_alias  # noqa: F401
from ankiscape.runtime.runtime_actions_quest import handle_quest_answer
from tests.quest_catalog.another_cook.test_another_cook_runtime import configure
from tests.quest_catalog.test_murder_mystery_review import review_session
from tests.test_early_quest_item_routes import _answer_review
from tests.test_runtime_actions import _context


class QuestXpNotificationsTest(unittest.TestCase):
    def test_commission_is_silent_and_preparation_notifies_and_checks_cooking_level(self):
        with review_session() as (addon, _collection, errors):
            configure(addon, {'Ashes': 1, 'Fruit blast (9514)': 1})
            constants = sys.modules[f'{addon.__name__}.core.constants']
            data = addon._state.player_data
            data['cooking_exp'] = constants.EXP_TABLE[10] - 1
            before = addon._implemented_exp_keys_snapshot()
            with (
                patch.object(addon, '_show_quest_exp_delta', wraps=addon._show_quest_exp_delta) as notify,
                patch.object(addon, '_show_exp') as show_exp,
                patch.object(addon, 'level_up_check', wraps=addon.level_up_check) as check_level,
            ):
                _answer_review(addon)
                notify.assert_not_called()
                show_exp.assert_not_called()
                check_level.assert_not_called()
                _answer_review(addon)
                notify.assert_called_once_with(before)
                show_exp.assert_called_once()
                gain = show_exp.call_args.args[0]
                self.assertEqual(float(gain), 5.0)
                self.assertEqual(gain.skill_names, ('Cooking',))
                check_level.assert_called_once_with('Cooking', data)
                self.assertEqual(data['cooking_exp'], before['cooking_exp'] + 5.0)
                self.assertEqual(data['cooking_level'], 11)
                self.assertFalse(data['quests'][data['current_quest']]['completed'])
                self.assertEqual(errors, [])

    def test_completion_still_invokes_notifier_even_without_xp(self):
        data = {
            'inventory': {'Research notes': 1},
            'current_quest': 'rune_mysteries',
            'quests': {'rune_mysteries': dict(started=True, progress=5, completed=False)},
            'quest_action_proofs': ["Return Aubury's research notes to Sedridor"],
            'quest_points': 0,
            'runecrafting_exp': 0,
            'pending_skill_exp_rewards': {},
            'completed_achievements': [],
        }
        calls = {'xp': [], 'saves': 0, 'errors': []}
        context = _context(data, calls)
        context.show_quest_exp_delta = Mock()
        self.assertTrue(handle_quest_answer(context))
        context.show_quest_exp_delta.assert_called_once_with({})
        self.assertTrue(data['quests']['rune_mysteries']['completed'])
        self.assertTrue(calls['deactivated'])
        self.assertEqual(calls['errors'][0][0], 'Quest complete')
        self.assertEqual(calls['saves'], 1)
