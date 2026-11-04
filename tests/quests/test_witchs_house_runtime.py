"""Review dispatch and the existing quest controls commit one earned deed."""

import copy
import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.witchs_house import (
    QUEST_ID, DIARY, LEATHER_GLOVES, BACKROOM_KEY, BALL, READ_DIARY, PASS_GATE,
    TAKE_DIARY, TAKE_KEY, TAKE_BALL,
)
from ankiscape.logic_pure.logic_pure_quest import can_attempt_quest_review_pure
from ankiscape.logic_pure.quest.review_services import (
    quest_review_service_phase_pure, quest_review_service_ready_pure,
)
from ankiscape.runtime import runtime_actions_quest
from tests import test_main_menu_widget as menu_fixture
from tests import test_integration_smoke as runtime_fixture
from tests.main_menu.fixtures import MainMenuWidgetTest
from tests.test_runtime_actions import _context
from tests.test_early_quest_item_routes import _answer_review
from .test_witchs_house import player_at, blockers, finished_fights


def runtime_player(stage):
    player = player_at(stage, () if stage in (3, 4) else (READ_DIARY,))
    if stage == 4:
        player['inventory'][DIARY] = 1
    if stage == 6:
        player['equipment']['hands'] = LEATHER_GLOVES
    if stage == 14:
        finished_fights(player)
    return player


class WitchsHouseRuntimeTest(unittest.TestCase):
    def test_acquisition_read_gate_fountain_and_both_recoveries_save_and_record_once(self):
        cases = ((3, None, TAKE_DIARY), (4, None, READ_DIARY), (6, None, PASS_GATE),
                 (10, None, TAKE_KEY), (11, 'recover_key', TAKE_KEY), (14, 'recover_ball', TAKE_BALL))
        for stage, phase, proof in cases:
            with self.subTest(stage=stage):
                player = runtime_player(stage)
                reasons = blockers(player)
                self.assertEqual(quest_review_service_phase_pure(player, QUEST_ID, reasons), phase)
                self.assertEqual(quest_review_service_ready_pure(player, QUEST_ID, reasons), phase is not None)
                self.assertTrue(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
                calls = {'xp': [], 'saves': 0, 'errors': []}
                with patch.object(runtime_actions_quest, '_record_action') as record:
                    self.assertTrue(runtime_actions_quest.handle_quest_answer(_context(player, calls)))
                record.assert_called_once()
                self.assertEqual(calls['saves'], 1)
                self.assertEqual(calls['errors'], [])
                self.assertIn(proof, player['quest_action_proofs'])
                self.assertEqual(player['quests'][QUEST_ID]['progress'], stage if phase else stage + 1)
                self.assertEqual(player['quest_points'], 0)
                self.assertEqual(calls['xp'], [])
                if phase:
                    notice = 'Recovered the backroom key from the fountain.' if stage == 11 else "Recovered Harvey's ball from the shed."
                    self.assertEqual(calls['activity'], [notice])
                    self.assertEqual(player['inventory'][BACKROOM_KEY if stage == 11 else BALL], 1)

    def test_refusals_deactivate_without_item_proof_progress_reward_or_save(self):
        for stage in (4, 5, 6, 7, 10, 11, 13, 14):
            with self.subTest(stage=stage):
                player = player_at(stage)
                player['inventory'][LEATHER_GLOVES] = 1
                before = copy.deepcopy(player)
                calls = {'xp': [], 'saves': 0, 'errors': []}
                with patch.object(runtime_actions_quest, '_record_action') as record:
                    self.assertFalse(runtime_actions_quest.handle_quest_answer(_context(player, calls)))
                record.assert_not_called()
                self.assertEqual(player, before)
                self.assertEqual(calls['saves'], 0)
                self.assertTrue(calls['deactivated'])
                self.assertEqual(calls['xp'], [])
                self.assertEqual(calls['errors'][0][0], 'Quest blocked')

    def test_real_review_dispatch_preserves_separate_pickup_and_read_transactions(self):
        with patch.dict(sys.modules):
            runtime_fixture._install_runtime_fakes()
            addon = runtime_fixture._load_addon_as_package('ankiscape_witch_dispatch')
            addon._state.player_data = player_at(3)
            addon._state.current_skill = 'Quests'
            addon._state.review_undo_stack.clear()
            saved = []
            addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
            addon.check_achievements = lambda _data: None
            addon._refresh_skill_availability = lambda: None
            addon._show_activity_gain = lambda _text: None
            addon._show_exp = lambda _exp: None
            addon.level_up_check = lambda *_args: None
            addon.update_review_hud = lambda *_args: None
            addon.show_error_message = lambda *_args: None
            _answer_review(addon)
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0]['inventory'][DIARY], 1)
            self.assertIn(TAKE_DIARY, saved[0]['quest_action_proofs'])
            self.assertNotIn(READ_DIARY, saved[0]['quest_action_proofs'])
            _answer_review(addon)
            self.assertEqual(len(saved), 2)
            self.assertEqual(saved[1]['inventory'][DIARY], 1)
            self.assertIn(READ_DIARY, saved[1]['quest_action_proofs'])
            self.assertEqual(len(addon._state.review_undo_stack), 2)


@unittest.skipUnless(menu_fixture.HAS_AQT, 'aqt/PyQt6 required')
class WitchsHouseControlsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.fixture = MainMenuWidgetTest(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)

    def open_quest(self, player):
        dialog = self.fixture._open(player)
        menu_fixture._open_quests_tab(dialog)
        dialog.show()
        dialog.resize(760, 560)
        for _ in range(3):
            menu_fixture.QApplication.processEvents()
        action = dialog.findChild(menu_fixture.QPushButton, 'questAction_witchs_house')
        self.assertIsNotNone(action)
        self.assertGreater(action.height(), 0)
        self.assertGreater(action.width(), 0)
        return dialog, action

    def test_diary_blocks_but_held_quest_gloves_enable_existing_controls(self):
        for stage, reason in ((4, "Needs Diary (Witch's House) x1"), (6, 'Wear insulating gloves to pass the electric gate')):
            player = player_at(stage, (READ_DIARY,) if stage == 6 else ())
            player['inventory'][LEATHER_GLOVES] = 1
            dialog, action = self.open_quest(player)
            self.assertEqual(action.isEnabled(), stage == 6)
            if stage == 4:
                self.assertIn(reason, action.toolTip())
            self.assertEqual(self.fixture._quest_calls, [])
            dialog.close()

    def test_equipped_gloves_and_both_recovery_contexts_select_through_existing_controls(self):
        for stage in (6, 11, 14):
            player = player_at(stage, (READ_DIARY,))
            if stage == 6:
                player['equipment']['hands'] = LEATHER_GLOVES
            if stage == 14:
                finished_fights(player)
            dialog, action = self.open_quest(player)
            self.assertTrue(action.isEnabled())
            action.click()
            menu_fixture.QApplication.processEvents()
            self.assertEqual(self.fixture._quest_calls[-1], QUEST_ID)
            dialog.close()
