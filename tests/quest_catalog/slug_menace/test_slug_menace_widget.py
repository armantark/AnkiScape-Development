"""Existing quest controls and journal rendering, with real laid-out Qt widgets."""
import copy
import html
import sys
import unittest
from itertools import product
from unittest.mock import patch

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as menu
from tests.main_menu.fixtures import MainMenuWidgetTest
from tests.quest_catalog.test_murder_mystery_review import review_session, PLAYER_KEY
from tests.quest_catalog.slug_menace.test_slug_menace_opening import QUEST_ID, LINES, player, advance, eligible
from ankiscape.data.quest.stage_overrides.members.later.the_slug_menace import LEGACY_OPENING_JOURNAL


@unittest.skipUnless(menu.HAS_AQT, 'aqt/PyQt6 required')
class TestSlugMenaceWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.fixture = MainMenuWidgetTest(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.app = self.fixture.app
        palette, style = self.app.palette(), self.app.style().objectName()
        self.addCleanup(self.app.setPalette, palette)
        self.addCleanup(self.app.setStyle, style)

    def palette(self, dark):
        from aqt.qt import QColor, QPalette
        self.app.setStyle('Fusion')
        palette = self.app.style().standardPalette()
        if dark:
            for role, color in ((QPalette.ColorRole.Window, '#353535'),
                                (QPalette.ColorRole.Base, '#242424'),
                                (QPalette.ColorRole.Button, '#353535'),
                                (QPalette.ColorRole.Text, '#eeeeee'),
                                (QPalette.ColorRole.WindowText, '#eeeeee'),
                                (QPalette.ColorRole.ButtonText, '#eeeeee')):
                palette.setColor(role, QColor(color))
        self.app.setPalette(palette)

    def open_quest(self, data):
        dialog = self.fixture._open(data)
        dialog.show()
        dialog.resize(dialog.sizeHint())
        menu._open_quests_tab(dialog)
        menu._expand_quest_card(dialog, QUEST_ID)
        for _ in range(3):
            self.app.processEvents()
        return dialog

    def assert_lines_and_geometry(self, dialog, lines, struck):
        body = dialog.findChild(menu.QWidget, 'questBody_' + QUEST_ID)
        labels = body.findChildren(menu.QLabel)
        for line in lines:
            matches = [label for label in labels if line in html.unescape(label.text())]
            self.assertEqual(len(matches), 1, line)
            label = matches[0]
            self.assertTrue(label.wordWrap())
            self.assertEqual('<s>' in label.text(), struck, label.text())
            self.assertGreater(label.width(), 0)
            self.assertGreater(label.height(), 0)
            self.assertLessEqual(label.width(), body.width())
        self.assertFalse(dialog.grab().isNull())

    def assert_both_sizes(self, dialog, lines, struck):
        for height in (dialog.height(), 560):
            dialog.resize(dialog.width(), height)
            for _ in range(3):
                self.app.processEvents()
            self.assert_lines_and_geometry(dialog, lines, struck)

    def test_eligible_existing_action_and_five_wrapped_lines_in_both_palettes(self):
        for dark in (False, True):
            self.palette(dark)
            data = player()
            data['current_quest'] = ''
            before = copy.deepcopy(data)
            dialog = self.open_quest(data)
            button = dialog.findChild(menu.QPushButton, 'questAction_' + QUEST_ID)
            self.assertTrue(button.isEnabled())
            button.click()
            self.app.processEvents()
            self.assertEqual(self.fixture._quest_calls[-1], QUEST_ID)
            for height in (dialog.height(), 560):
                dialog.resize(dialog.width(), height)
                for _ in range(3):
                    self.app.processEvents()
                self.assert_lines_and_geometry(dialog, LINES, False)
            self.assertEqual(data['inventory'], before['inventory'])
            self.assertEqual(data['quest_action_proofs'], [])
            dialog.close()

    def test_real_start_retains_opening_after_collapse_and_expand_without_reopening_menu(self):
        qt_modules = {name: module for name, module in sys.modules.items()
                      if name == 'aqt' or name.startswith('aqt.')}
        for dark, original in product((False, True), (0, 1)):
            with self.subTest(dark=dark, original=original), review_session() as (addon, collection, errors), \
                    patch.dict(sys.modules, qt_modules):
                self.palette(dark)
                data = eligible(addon._state.player_data)
                data['inventory'] = {'Coins': 37, 'Commorb': original}
                before = copy.deepcopy(data)
                show_menu = self.fixture._ui.show_main_menu

                def show_with_real_start(**kwargs):
                    kwargs.update(on_set_quest=addon.on_set_quest, on_save_skill=addon._select_review_action)
                    return show_menu(**kwargs)

                with patch.object(self.fixture._ui, 'show_main_menu', side_effect=show_with_real_start):
                    dialog = self.open_quest(data)
                button = dialog.findChild(menu.QPushButton, 'questAction_' + QUEST_ID)
                self.assertEqual(button.text(), 'Start quest')
                self.assertTrue(button.isEnabled())
                button.click()
                self.app.processEvents()
                self.assertTrue(data['quests'][QUEST_ID]['started'])
                self.assertEqual(data['quests'][QUEST_ID]['progress'], 0)
                self.assertEqual(button.text(), 'Currently active')
                toggle = dialog.findChild(menu.QPushButton, 'questToggle_' + QUEST_ID)
                body = dialog.findChild(menu.QWidget, 'questBody_' + QUEST_ID)
                toggle.click()
                self.app.processEvents()
                self.assertTrue(body.isHidden())
                menu._expand_quest_card(dialog, QUEST_ID)
                self.assert_both_sizes(dialog, LINES, False)
                for key in ('inventory', 'carried_inventory', 'quest_action_proofs', 'quest_points'):
                    self.assertEqual(data[key], before[key])
                self.assertEqual(collection._store[PLAYER_KEY], data)
                self.assertEqual(errors, [])
                dialog.close()

    def test_earned_opening_struck_and_legacy_summary_unstruck_no_later_completion(self):
        earned, ok, completed = advance(player())
        self.assertEqual((ok, completed), (True, False))
        for dark in (False, True):
            self.palette(dark)
            for data, lines, struck in ((earned, LINES, True), (player(2), LEGACY_OPENING_JOURNAL, False)):
                before = copy.deepcopy(data)
                dialog = self.open_quest(data)
                self.assert_both_sizes(dialog, lines, struck)
                body = dialog.findChild(menu.QWidget, 'questBody_' + QUEST_ID)
                later = [label.text() for label in body.findChildren(menu.QLabel) if 'stage 2 objective' in label.text()]
                self.assertTrue(later)
                self.assertFalse(any('<s>' in text for text in later))
                for key in ('inventory', 'quests', 'quest_action_proofs', 'quest_points'):
                    self.assertEqual(data[key], before[key])
                dialog.close()
