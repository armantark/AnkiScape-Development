"""Watchtower uses the existing journal controls and registered Bank icon."""

import copy
import random
import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as fixture
from tests.main_menu import fixtures as menu_fixture
from tests.quest_catalog.test_watchtower_opening import player, journal, advance, QUEST_ID
from ankiscape.data.quest import watchtower_opening as source
from ankiscape.core.constants import QUEST_ITEM_IMAGES
from ankiscape.logic.bank_layout_logic import reconcile_bank_layout_for_player_pure


@unittest.skipUnless(fixture.HAS_AQT, 'Qt/Anki runtime is not installed')
class WatchtowerOpeningUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        menu_fixture.MainMenuWidgetTest.setUpClass()
        cls.app = menu_fixture.MainMenuWidgetTest.app

    def setUp(self):
        # Compose only fixture setup and opening helpers; inheriting its full
        # suite would discover hundreds of unrelated tests a second time.
        self.harness = menu_fixture.MainMenuWidgetTest('runTest')
        self.harness.setUp()
        self.addCleanup(self.harness.tearDown)
        original = self.app.palette()
        self.addCleanup(self.app.setPalette, original)
        self.app.setStyle('Fusion')

    def _palette(self, dark):
        palette = fixture.QPalette()
        roles = fixture.QPalette.ColorRole
        colors = {
            roles.Window: '#2d2d2d' if dark else '#eeeeee',
            roles.WindowText: '#eeeeee' if dark else '#202020',
            roles.Base: '#202020' if dark else '#ffffff',
            roles.Text: '#eeeeee' if dark else '#202020',
            roles.Button: '#373737' if dark else '#eeeeee',
            roles.ButtonText: '#eeeeee' if dark else '#202020',
            roles.Mid: '#080808' if dark else '#888888',
        }
        for role, color in colors.items():
            palette.setColor(role, fixture.QColor(color))
        self.app.setPalette(palette)

    def _open(self, data):
        dialog = self.harness._open(data, current_skill='Mining')
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(3):
            self.app.processEvents()
        fixture._open_quests_tab(dialog)
        fixture._expand_quest_card(dialog, QUEST_ID)
        for _ in range(3):
            self.app.processEvents()
        return dialog

    def _body_text(self, dialog):
        body = dialog.findChild(fixture.QWidget, 'questBody_watchtower')
        return body, [label.text() for label in body.findChildren(fixture.QLabel)]

    def test_phase_journals_toggle_availability_and_geometry_in_both_palettes(self):
        for dark in (False, True):
            self._palette(dark)
            for phase in range(4):
                self._assert_phase(phase)

    def _assert_phase(self, phase):
        data = reconcile_bank_layout_for_player_pure(player(phase, stage=2 if phase == 3 else 1))
        before, rng = copy.deepcopy(data), random.getstate()
        dialog = self._open(data)
        body, texts = self._body_text(dialog)
        expected = journal(data)[0]
        rendered = [f'<s>{line}</s>' if expected['completed'] else line for line in expected['lines']]
        self.assertTrue(set(rendered) <= set(texts))
        action = dialog.findChild(fixture.QPushButton, 'questAction_watchtower')
        self.assertEqual(action.isEnabled(), phase < 3)
        toggle = dialog.findChild(fixture.QPushButton, 'questToggle_watchtower')
        toggle.click()
        self.app.processEvents()
        self.assertTrue(body.isHidden())
        toggle.click()
        self.app.processEvents()
        self.assertFalse(body.isHidden())
        self.assertGreater(body.width(), 0)
        card = dialog.findChild(fixture.QWidget, 'questCard_watchtower')
        self.assertLessEqual(body.geometry().right(), card.width())
        self.assertLessEqual(action.geometry().right(), action.parentWidget().width())
        self.assertEqual(data, before)
        self.assertEqual(random.getstate(), rng)
        dialog.close()

    def test_selecting_existing_control_does_not_perform_commission(self):
        data = player(started=False, stage=0)
        before = copy.deepcopy(data)
        dialog = self._open(data)
        action = dialog.findChild(fixture.QPushButton, 'questAction_watchtower')
        self.assertTrue(action.isEnabled())
        action.click()
        self.app.processEvents()
        self.assertEqual(self.harness._quest_calls, [QUEST_ID])
        self.assertEqual(data, before)
        self.assertEqual(data['quest_action_proofs'], [])
        self.assertEqual(data['inventory'], {})

    def test_missing_clue_disables_control_and_refuses_without_journal_mutation(self):
        data = player(2)
        data['inventory']['Fingernails'] = 0
        before = copy.deepcopy(data)
        dialog = self._open(data)
        action = dialog.findChild(fixture.QPushButton, 'questAction_watchtower')
        self.assertFalse(action.isEnabled())
        self.assertIn('Needs Fingernails x1', action.toolTip())
        action.click()
        self.assertEqual(self.harness._quest_calls, [])
        self.assertEqual(advance(data), (data, False, False))
        self.assertIn(source.PENDING_JOURNAL[2], self._body_text(dialog)[1])
        self.assertEqual(data, before)

    def test_legacy_row_is_uncompleted_and_later_rows_preserved(self):
        data = player(stage=3)
        before = copy.deepcopy(data)
        dialog = self._open(data)
        texts = self._body_text(dialog)[1]
        self.assertIn(source.LEGACY_JOURNAL[0], texts)
        self.assertNotIn(f'<s>{source.LEGACY_JOURNAL[0]}</s>', texts)
        self.assertNotIn(source.COMPLETED_JOURNAL[0], texts)
        self.assertIn('Complete Watchtower stage 3 objective using the pinned source guide.', texts)
        self.assertEqual(data, before)

    def test_clue_icon_resolves_on_existing_bank_surface(self):
        data = reconcile_bank_layout_for_player_pure(player(2))
        before = copy.deepcopy(data)
        dialog = self._open(data)
        fixture._open_bank_tab(dialog)
        self.app.processEvents()
        button = fixture._bank_grid_button(dialog, 'Fingernails')
        self.assertFalse(button.icon().isNull())
        expected = fixture.QIcon(QUEST_ITEM_IMAGES['Fingernails'])
        self.assertEqual(fixture._icon_pixels(button.icon()), fixture._icon_pixels(expected))
        self.assertEqual(data, before)
