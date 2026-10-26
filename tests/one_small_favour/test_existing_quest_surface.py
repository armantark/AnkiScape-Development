"""Existing quest and Bank widgets expose the opening at laptop geometry."""

import copy
import unittest
from unittest.mock import patch

from tests import test_main_menu_widget as menu_fixture
from tests.main_menu import fixtures as menu_class_fixture
from tests.one_small_favour.test_opening_transactions import player, progress
from ankiscape.core.constants import QUEST_DATA, QUEST_ITEM_IMAGES
from ankiscape.data.quest.one_small_favour import QUEST_ID, BLUNT_HATCHET
from ankiscape.logic_pure.quest.one_small_favour import FORESTER_REASON, RECOVER_REASON
from tests.test_runtime_actions import _context
from ankiscape.runtime.runtime_actions_quest import handle_quest_answer

if menu_fixture.HAS_AQT:
    from aqt.qt import QApplication, QColor, QIcon, QLabel, QLineEdit, QListWidget, QPalette, QPushButton, QScrollArea, QToolButton, Qt, QWidget, QMessageBox
    from PyQt6.QtTest import QTest


def pump():
    for _ in range(5):
        QApplication.processEvents()


@unittest.skipUnless(menu_fixture.HAS_AQT, 'Qt is unavailable; run the Qt lane')
class ExistingOpeningSurfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        menu_class_fixture.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = menu_class_fixture.MainMenuWidgetTest(methodName='runTest')
        self.menu.setUp()
        self.addCleanup(self.menu.tearDown)
        self.app = QApplication.instance()
        self.original_palette = self.app.palette()
        self.addCleanup(self.app.setPalette, self.original_palette)
        self.app.setStyle('Fusion')

    def palette(self, dark):
        palette = self.app.style().standardPalette()
        if dark:
            for role in (QPalette.ColorRole.Window, QPalette.ColorRole.Base, QPalette.ColorRole.Button):
                palette.setColor(role, QColor(40, 40, 40))
            for role in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText, QPalette.ColorRole.ButtonText):
                palette.setColor(role, QColor(235, 235, 235))
        self.app.setPalette(palette)

    def open(self, data):
        dialog = self.menu._open(data, current_skill='Mining')
        dialog.show()
        dialog.resize(720, 560)
        pump()
        menu_fixture._open_quests_tab(dialog)
        dialog.findChild(QLineEdit, 'questSearchInput').setText('One Small Favour')
        pump()
        menu_fixture._expand_quest_card(dialog, QUEST_ID)
        pump()
        return dialog

    def assert_journal(self, dialog, completed):
        body = dialog.findChild(QWidget, 'questBody_' + QUEST_ID)
        texts = [label.text() for label in body.findChildren(QLabel)]
        expected = QUEST_DATA[QUEST_ID]['journal_stages'][1]
        self.assertEqual(len(expected), 6)
        for line in expected:
            self.assertEqual(texts.count(f'<s>{line}</s>' if completed else line), 1)
        self.assertTrue(any(text.startswith('Requires: ') and 'Rune Mysteries' in text for text in texts))
        self.assertNotIn('Empty Pot', dialog.findChild(QPushButton, 'questAction_' + QUEST_ID).toolTip())
        self.assertGreater(body.height(), 0)
        self.assertGreater(dialog.width(), 0)
        scrolls = dialog.findChildren(QScrollArea)
        self.assertTrue(scrolls)
        self.assertTrue(all(scroll.horizontalScrollBar().maximum() == 0 for scroll in scrolls if scroll.isVisible()))

    def test_valid_prefixes_enable_existing_control_and_only_johanhus_finishes_journal(self):
        for dark in (False, True):
            self.palette(dark)
            data = player()
            for prefix in range(8):
                with self.subTest(dark=dark, prefix=prefix):
                    before = copy.deepcopy(data)
                    dialog = self.open(data)
                    self.assert_journal(dialog, prefix == 7)
                    button = dialog.findChild(QPushButton, 'questAction_' + QUEST_ID)
                    # Journal 2's original requirement remains authoritative after Johanhus.
                    self.assertEqual(button.isEnabled(), prefix < 7)
                    for key in ('inventory', 'quests', 'quest_action_proofs', 'current_quest'):
                        self.assertEqual(data[key], before[key])
                    dialog.close()
                    if prefix < 7:
                        data, ok, _ = progress(data)
                        self.assertTrue(ok)

    def test_custody_refusal_text_and_bank_retained_icon_and_discard(self):
        for dark in (False, True):
            self.palette(dark)
            for prefix, outside, reason in ((1, False, FORESTER_REASON), (3, True, RECOVER_REASON)):
                data = player(prefix)
                data['inventory'][BLUNT_HATCHET] = 0 if outside else 1
                if outside:
                    data['death_office'] = {'items': [BLUNT_HATCHET]}
                dialog = self.open(data)
                button = dialog.findChild(QPushButton, 'questAction_' + QUEST_ID)
                self.assertFalse(button.isEnabled())
                self._assert_refusal_dialog(data, reason)
                dialog.close()
            self._assert_bank()

    def _assert_refusal_dialog(self, data, reason):
        from ankiscape.ui import ui
        captured = []

        class CapturedWarning(QMessageBox):
            def exec(box):
                box.show()
                box.resize(500, 300)
                pump()
                captured.append(box.text())
                box.close()
                return 0

        ctx = _context(data)
        ctx.show_error_message = ui.show_error_message
        with patch.object(ui, 'QMessageBox', CapturedWarning):
            self.assertFalse(handle_quest_answer(ctx))
        self.assertIn(reason, captured[0])

    def _assert_bank(self):
        data = player(3)
        dialog = self.open(data)
        menu_fixture._open_bank_tab(dialog)
        pump()
        cell = dialog.findChild(QToolButton, 'bankGridItem::' + BLUNT_HATCHET)
        self.assertIsNotNone(cell)
        self.assertFalse(cell.icon().isNull())
        self.assertFalse(QIcon(QUEST_ITEM_IMAGES[BLUNT_HATCHET]).isNull())
        self.assertGreater(cell.width(), 0)
        menu = dialog._ankiscape_equip_menu_for(BLUNT_HATCHET)
        self.assertTrue(any(action.text() == 'Discard X…' for action in menu.actions()))
        # Keyboard navigation owns list selection in the existing sidebar.
        menu_fixture._open_equipment_tab(dialog)
        pump()
        slots = dialog.findChild(QListWidget, 'equipmentList')
        slots.setFocus()
        QTest.keyClick(slots, Qt.Key.Key_Home)
        pump()
        self.assertIsNotNone(slots.currentItem())
        self.assertFalse(any('Blunt hatchet' in slots.item(i).text() for i in range(slots.count())))
        dialog.close()
