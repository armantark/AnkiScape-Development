"""All six NPC clues use real runtime answers, complete Undo and replay."""

import copy
import random
import sys
import types
import unittest
from contextlib import contextmanager
from unittest.mock import patch

from tests import test_integration_smoke as smoke
from tests.treasure_trails.test_npc_catalog import (
    NEW_EXPECTED, contact_draws, fresh_player, owned_items,
)


@contextmanager
def isolated_runtime():
    modules_before = dict(sys.modules)
    random_before = random.getstate()
    try:
        smoke._install_runtime_fakes()
        yield smoke._load_addon_as_package('ankiscape_npc_review_undo')
    finally:
        random.setstate(random_before)
        sys.modules.clear()
        sys.modules.update(modules_before)


def checkpoint(addon):
    return (
        copy.deepcopy(addon._state.player_data),
        addon._state.current_skill,
        random.getstate(),
    )


def answer(addon, ease=3):
    addon._state.card_turned = True
    addon._state.answer_shown = True
    addon._state.exp_awarded = False
    return addon.on_answer_card(smoke._FakeReviewer(), ease, lambda _self, _ease: 'accepted')


def undo_answer(addon):
    addon._on_state_did_undo(types.SimpleNamespace(
        operation='Answer Card',
        changes=types.SimpleNamespace(study_queues=True, card=True),
    ))


class NpcReviewUndoTest(unittest.TestCase):
    def prepare(self, addon, index, length):
        """Capture the menu's real bank callback; suppress only presentation."""
        saved = []
        addon.save_player_data = lambda: saved.append((
            copy.deepcopy(addon._state.player_data), addon._state.current_skill,
        ))
        addon.check_achievements = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.ui.show_bankstanding_dialog = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = smoke._DummyMW(smoke._DummyCol({'ankiscape_review_action_multiplier': 1}))
        addon._state.player_data = fresh_player()
        addon._state.current_skill = 'Activities'
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        with patch.object(random, 'random', contact_draws(index, length)):
            result = captured['on_treasure_trails_command']('start_from_bank', {'tier': 'easy'})
        self.assertTrue(result['ok'], result)
        addon._state.current_skill = 'Activities'
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        self.assertEqual(addon.mw.col.custom_undo_entries, ['AnkiScape direct action'])
        self.assertEqual(addon._state.review_undo_stack, [])
        return saved

    def assert_restored(self, addon, before, direct_stack, saved):
        # Full equality includes retained state, telemetry, event log and clocks.
        self.assertEqual(checkpoint(addon), before)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(addon._state.direct_action_undo_stack, direct_stack)
        self.assertEqual(saved[-1], before[:2])

    def assert_view(self, addon, step_id, row, number, total):
        view = addon.treasure_trails_view_pure(addon._state.player_data)['step']
        self.assertEqual(view['step_id'], step_id)
        self.assertEqual(view['text'], row['text'])
        self.assertEqual((view['number'], view['total']), (number, total))
        self.assertEqual(view['blocked_reason'], '')

    def assert_completion(self, addon):
        data = addon._state.player_data
        self.assertEqual(owned_items(data), {'Logs': 2, 'Casket (easy)': 1})
        self.assertNotIn('Clue scroll (easy)', data['inventory'])
        self.assertEqual(data['treasure_trail'], {})
        self.assertEqual(data['treasure_trail_retained'], {})
        self.assertEqual(data['activity_session']['active_id'], '')
        self.assertEqual(data['treasure_trails_started'], 1)
        self.assertEqual(data['treasure_trails_completed'], 1)
        self.assertEqual(data['treasure_trails_caskets_opened'], 0)
        self.assertEqual(data['current_utility'], 'bankstanding')
        self.assertEqual(addon._state.current_skill, 'Utilities')

    def test_new_contacts_review_undo_replay_restores_nonterminal_progress(self):
        for index, (step_id, row) in enumerate(NEW_EXPECTED.items(), 9):
            with self.subTest(step_id=step_id), isolated_runtime() as addon:
                saved = self.prepare(addon, index, length=2)
                before = checkpoint(addon)
                direct_stack = copy.deepcopy(addon._state.direct_action_undo_stack)
                self.assertEqual(before[0]['treasure_trail']['steps'], [step_id, step_id])
                self.assert_view(addon, step_id, row, 1, 2)
                self.assertEqual(answer(addon, ease=1), 'accepted')
                self.assertEqual(addon._state.player_data['treasure_trail'], before[0]['treasure_trail'])
                self.assertEqual(addon._state.player_data['inventory'], before[0]['inventory'])
                self.assertEqual(addon._state.player_data['treasure_trails_completed'], 0)
                undo_answer(addon)
                self.assert_restored(addon, before, direct_stack, saved)
                self.assertEqual(answer(addon), 'accepted')
                progressed = checkpoint(addon)
                self.assertEqual(progressed[0]['treasure_trail']['index'], 1)
                self.assertEqual(progressed[0]['inventory'], before[0]['inventory'])
                self.assertEqual(progressed[0]['treasure_trails_completed'], 0)
                self.assert_view(addon, step_id, row, 2, 2)
                self.assertEqual(len(addon._state.review_undo_stack), 1)
                self.assertEqual(saved[-1], progressed[:2])
                undo_answer(addon)
                self.assert_restored(addon, before, direct_stack, saved)
                answer(addon)
                self.assertEqual(checkpoint(addon), progressed)
                self.assertEqual(saved[-1], progressed[:2])
                self.assertEqual(len(addon._state.review_undo_stack), 1)
                self.assertEqual(addon._state.direct_action_undo_stack, direct_stack)

    def test_new_contacts_review_undo_replay_restores_terminal_settlement(self):
        for index, (step_id, row) in enumerate(NEW_EXPECTED.items(), 9):
            with self.subTest(step_id=step_id), isolated_runtime() as addon:
                saved = self.prepare(addon, index, length=1)
                before = checkpoint(addon)
                direct_stack = copy.deepcopy(addon._state.direct_action_undo_stack)
                self.assertEqual(before[0]['treasure_trail']['steps'], [step_id])
                self.assert_view(addon, step_id, row, 1, 1)
                self.assertEqual(answer(addon), 'accepted')
                self.assert_completion(addon)
                completed = checkpoint(addon)
                self.assertEqual(saved[-1], completed[:2])
                self.assertEqual(len(addon._state.review_undo_stack), 1)
                undo_answer(addon)
                self.assert_restored(addon, before, direct_stack, saved)
                self.assert_view(addon, step_id, row, 1, 1)
                self.assertEqual(owned_items(addon._state.player_data), {'Clue scroll (easy)': 1, 'Logs': 2})
                answer(addon)
                self.assert_completion(addon)
                self.assertEqual(checkpoint(addon), completed)
                self.assertEqual(saved[-1], completed[:2])
                self.assertEqual(len(addon._state.review_undo_stack), 1)
                self.assertEqual(addon._state.direct_action_undo_stack, direct_stack)
