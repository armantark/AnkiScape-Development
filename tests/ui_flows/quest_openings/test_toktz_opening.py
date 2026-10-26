"""The ordinary menu projects the opening without performing any interaction."""

import copy
import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as menu
from tests.quest_catalog.test_toktz_opening import (
    player, advance, opening_snapshot, QUEST_ID, TABLET, GUIDE, COMPLETED_LINES, PENDING_LINES,
    LEGACY_LINE, RECOVERY_INSTRUCTION,
)

if menu.HAS_AQT:
    from aqt.qt import QApplication, QLabel, QLineEdit, QPushButton, QScrollArea, QWidget
    from tests.ui_flows.test_desert_treasure_mirror_journal_ui import _dark_palette
    from tests.ui_flows.qt_text_fit import text_fit_defects


def pump():
    for _ in range(6):
        QApplication.processEvents()


@unittest.skipUnless(menu.HAS_AQT, 'aqt/PyQt6 not installed (use Qt lane)')
class ToktzOpeningPresentationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        menu.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = menu.MainMenuWidgetTest(methodName='runTest')
        self.menu.setUp()
        self.original_palette = QApplication.palette()
        self.original_style = QApplication.style().objectName()

    def tearDown(self):
        self.menu.tearDown()
        QApplication.setStyle(self.original_style)
        QApplication.setPalette(self.original_palette)
        pump()

    def open_journal(self, data):
        dialog = self.menu._open(data, current_skill='Mining')
        dialog.show()
        dialog.resize(720, 560)
        pump()
        menu._open_quests_tab(dialog)
        dialog.findChild(QLineEdit, 'questSearchInput').setText('TokTz-Ket-Dill')
        menu._expand_quest_card(dialog, QUEST_ID)
        pump()
        return dialog

    def labels(self, dialog):
        body = dialog.findChild(QWidget, 'questBody_' + QUEST_ID)
        layout = body.layout()
        labels = [layout.itemAt(index).widget() for index in range(layout.count())
                  if isinstance(layout.itemAt(index).widget(), QLabel)]
        texts = [label.text() for label in labels]
        start = texts.index('Stage 1') + 1
        end = texts.index('Stage 2') if 'Stage 2' in texts else len(labels)
        return body, labels[start:end]

    def assert_fits(self, dialog, body, labels):
        self.assertEqual((dialog.width(), dialog.height()), (720, 560))
        self.assertTrue(body.isVisible())
        self.assertEqual(text_fit_defects(body), [])
        for label in labels:
            self.assertTrue(label.wordWrap())
            self.assertLessEqual(label.heightForWidth(label.width()), label.height())
        page = dialog.findChild(QWidget, 'questSearchInputBar').parentWidget()
        scroll = page.findChild(QScrollArea)
        self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
        self.assertGreater(scroll.viewport().height(), 0)

    def test_each_pending_instruction_and_completed_endpoint_in_both_palettes(self):
        for dark in (False, True):
            QApplication.setStyle('Fusion')
            QApplication.setPalette(_dark_palette() if dark else QApplication.style().standardPalette())
            self._assert_phases()

    def _assert_phases(self):
        data = player()
        for index in range(6):
            before = opening_snapshot(data)
            dialog = self.open_journal(data)
            body, labels = self.labels(dialog)
            expected = COMPLETED_LINES if index == 5 else COMPLETED_LINES[:index] + (PENDING_LINES[index],)
            rendered = tuple('<s>' + text + '</s>' for text in expected) if index == 5 else expected
            self.assertEqual(tuple(label.text() for label in labels), rendered)
            self.assert_fits(dialog, body, labels)
            if index < 5:
                self.assertTrue(dialog.findChild(QPushButton, 'questAction_' + QUEST_ID).isEnabled())
            self.assertEqual(opening_snapshot(data), before)
            dialog.close()
            pump()
            if index < 5:
                data, success, _ = advance(data)
                self.assertTrue(success)

    def test_expansion_selection_and_reopening_are_not_reviews(self):
        data = player()
        inventory = copy.deepcopy(data['inventory'])
        dialog = self.open_journal(data)
        button = dialog.findChild(QPushButton, 'questAction_' + QUEST_ID)
        self.assertTrue(button.isEnabled())
        button.click()
        pump()
        self.assertEqual(self.menu._quest_calls, [QUEST_ID])
        self.assertEqual(data['inventory'], inventory)
        self.assertEqual(data['quest_action_proofs'], [])
        self.assertEqual(data['quests'][QUEST_ID]['progress'], 0)
        dialog.close()
        pump()
        before = opening_snapshot(data)
        reopened = self.open_journal(data)
        self.assertEqual(tuple(label.text() for label in self.labels(reopened)[1]), (PENDING_LINES[0],))
        self.assertEqual(opening_snapshot(data), before)

    def test_recovery_and_legacy_neutral_row_are_truthful(self):
        for dark in (False, True):
            QApplication.setStyle('Fusion')
            QApplication.setPalette(_dark_palette() if dark else QApplication.style().standardPalette())
            data = player(2, progress=1)
            data['inventory'].pop(TABLET)
            self._assert_readonly_row(data, COMPLETED_LINES[:2] + (RECOVERY_INSTRUCTION,))
            for completed in (False, True):
                legacy = player(2, progress=5, completed=completed)
                self._assert_readonly_row(legacy, (LEGACY_LINE,))

    def _assert_readonly_row(self, data, expected):
        before = opening_snapshot(data)
        dialog = self.open_journal(data)
        body, labels = self.labels(dialog)
        self.assertEqual(tuple(label.text() for label in labels), expected)
        self.assertTrue(all('<s>' not in label.text() for label in labels))
        self.assert_fits(dialog, body, labels)
        self.assertEqual(opening_snapshot(data), before)
        dialog.close()
        pump()

    def test_both_inventory_names_have_non_null_icons(self):
        data = player()
        for _ in range(5):
            data, success, _done = advance(data)
            self.assertTrue(success)
        dialog = self.open_journal(data)
        before = opening_snapshot(data)
        menu._open_bank_tab(dialog)
        pump()
        for name in (TABLET, GUIDE):
            button = menu._bank_grid_button(dialog, name)
            self.assertIn(name, button.toolTip())
            self.assertFalse(button.icon().isNull())
        self.assertEqual(opening_snapshot(data), before)
