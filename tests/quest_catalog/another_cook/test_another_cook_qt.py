"""Use the existing deferred quest cards at laptop height in both palettes."""

import copy
import unittest

from tests.main_menu import fixtures
from tests import test_main_menu_widget as menu
from tests.quest_catalog.another_cook.test_another_cook_transactions import (
    player, advance, transaction_snapshot, QUEST_ID, STATIC_JOURNAL, COMMISSION_JOURNAL, PREPARED_LINE,
)

if menu.HAS_AQT:
    from aqt.qt import QColor, QLabel, QLineEdit, QPalette, QPushButton, QScrollArea, Qt, QWidget


@unittest.skipUnless(menu.HAS_AQT, 'aqt/PyQt6 not installed (use .venv-qt)')
class AnotherCookQtTest(fixtures.MainMenuWidgetTest):
    def test_existing_card_activation_and_truthful_journal_in_light_palette(self):
        self._assert_palette(False)

    def test_existing_card_activation_and_truthful_journal_in_fusion_dark_palette(self):
        self._assert_palette(True)

    def _assert_palette(self, dark):
        before_palette, before_style = self.app.palette(), self.app.style().objectName()
        self.addCleanup(self.app.setPalette, before_palette)
        self.addCleanup(self.app.setStyle, before_style)
        self.app.setStyle('Fusion')
        palette = self.app.style().standardPalette()
        if dark:
            for role, color in ((QPalette.ColorRole.Window, '#353535'), (QPalette.ColorRole.Base, '#232323'),
                                (QPalette.ColorRole.Button, '#353535'), (QPalette.ColorRole.Text, '#eeeeee'),
                                (QPalette.ColorRole.WindowText, '#eeeeee'), (QPalette.ColorRole.ButtonText, '#eeeeee')):
                palette.setColor(role, QColor(color))
        self.app.setPalette(palette)
        started = player()
        started['quests'][QUEST_ID].update(started=True, progress=0)
        commissioned, ok, _ = advance(started)
        self.assertTrue(ok)
        inputs = copy.deepcopy(commissioned)
        inputs['inventory'].update({'Ashes': 1, 'Fruit blast': 1})
        special = copy.deepcopy(commissioned)
        special['inventory'].update({'Ashes': 1, 'Fruit blast (9514)': 1})
        premade = copy.deepcopy(commissioned)
        premade['inventory'].update({'Ashes': 1, "Premade fr' blast": 1})
        prepared, ok, _ = advance(inputs)
        self.assertTrue(ok)
        for data, enabled, lines, completed in (
            (started, True, STATIC_JOURNAL, False),
            (commissioned, False, COMMISSION_JOURNAL, False),
            (inputs, True, COMMISSION_JOURNAL, False),
            (special, True, COMMISSION_JOURNAL, False),
            (premade, False, COMMISSION_JOURNAL, False),
            (prepared, False, COMMISSION_JOURNAL[:2] + (PREPARED_LINE,), True),
        ):
            with self.subTest(dark=dark, lines=lines, enabled=enabled):
                self._assert_card(data, enabled, lines, completed)

    def _assert_card(self, data, enabled, lines, completed):
        before = transaction_snapshot(data)
        dialog = self._open(data, current_skill='Mining')
        dialog.show()
        dialog.resize(1080, 560)
        for _ in range(3):
            self.app.processEvents()
        menu._open_quests_tab(dialog)
        search = dialog.findChild(QLineEdit, 'questSearchInput')
        search.setText("Another Cook's Quest")
        self.app.processEvents()
        menu._expand_quest_card(dialog, QUEST_ID)
        for _ in range(3):
            self.app.processEvents()
        button = dialog.findChild(QPushButton, 'questAction_' + QUEST_ID)
        self.assertEqual(button.isEnabled(), enabled)
        body = dialog.findChild(QWidget, 'questBody_' + QUEST_ID)
        self.assertTrue(body.isVisible())
        labels = body.findChildren(QLabel)
        texts = [label.text() for label in labels]
        for line in lines:
            expected = f'<s>{line}</s>' if completed else line
            self.assertEqual(texts.count(expected), 1)
            label = next(label for label in labels if label.text() == expected)
            self.assertTrue(label.wordWrap())
            self.assertGreater(label.width(), 100)
            self.assertGreaterEqual(label.height(), label.heightForWidth(label.width()))
            self.assertIn('palette(text)', label.styleSheet())
            text = label.palette().color(QPalette.ColorRole.Text)
            base = label.palette().color(QPalette.ColorRole.Base)
            self.assertGreater(abs(text.lightnessF() - base.lightnessF()), 0.5)
        self.assertGreaterEqual(button.width(), button.fontMetrics().horizontalAdvance(button.text()) + 2)
        self.assertGreater(button.height(), 15)
        scrolls = [scroll for scroll in dialog.findChildren(QScrollArea) if scroll.isVisible()]
        self.assertTrue(scrolls)
        for scroll in scrolls:
            self.assertGreater(scroll.viewport().height(), 80)
            self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
        self.assertEqual(transaction_snapshot(data), before)
        dialog.close()
