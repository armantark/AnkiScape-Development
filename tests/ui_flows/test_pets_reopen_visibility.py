"""Reopening Pets must reveal its current row through the short Equipment page."""

from __future__ import annotations

from itertools import product
import unittest

from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures
from tests.ui_flows.test_first_cell_selection import _dark_palette, _player
from tests.ui_flows.test_pets_visible_rows import reveal_widget, visible_rect
from tests.ui_flows.test_tree_text_fit import _pump

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPushButton, Qt, QTreeWidget
    from PyQt6.QtTest import QTest


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PetsReopenVisibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = _main_menu_fixtures.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        app = QApplication.instance()
        self.addCleanup(app.setPalette, app.palette())
        self.addCleanup(app.setFont, app.font())

    def tearDown(self):
        self.menu.tearDown()

    def _click_toggle(self, toggle):
        reveal_widget(toggle)
        self.assertTrue(visible_rect(toggle).contains(toggle.rect()))
        self.assertIs(QApplication.widgetAt(toggle.mapToGlobal(toggle.rect().center())), toggle)
        QTest.mouseClick(toggle, Qt.MouseButton.LeftButton)
        _pump()

    def _assert_current_row_reachable(self, pets):
        index = pets.currentIndex().siblingAtColumn(0)
        self.assertEqual(pets.selectionModel().selectedIndexes(), [index])
        self.assertTrue(pets.currentItem().isSelected())
        # At large fonts Acquisition scrolls horizontally; the entire row must
        # still fit vertically through every ancestor, not just inside the log.
        room = pets.visualRect(index.siblingAtColumn(3))
        room.setLeft(max(0, room.left()))
        room.setRight(min(pets.viewport().rect().right(), room.right()))
        self.assertFalse(room.isEmpty())
        self.assertTrue(visible_rect(pets.viewport()).contains(room), pets.currentItem().text(0))
        self.assertIs(QApplication.widgetAt(pets.viewport().mapToGlobal(room.center())), pets.viewport())
        self.assertEqual(pets.height(), 210)
        self.assertEqual(pets.verticalScrollMode(), QTreeWidget.ScrollMode.ScrollPerItem)

    def _assert_reopening_reveals_current_pet(self, width):
        dialog = self.menu._open(_player(), current_skill="Mining")
        try:
            dialog.show()
            dialog.resize(width, 560)
            _main_menu._open_equipment_tab(dialog)
            _pump()
            toggle = dialog.findChild(QPushButton, "summoningPetsToggle")
            self._click_toggle(toggle)
            pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
            pets.setFocus()
            QTest.keyClick(pets, Qt.Key.Key_End)
            _pump()
            self.assertEqual(pets.currentItem().text(0), "TzRek-Jad")
            self._assert_current_row_reachable(pets)
            self._click_toggle(toggle)
            self.assertFalse(pets.isVisible())
            self._click_toggle(toggle)
            self.assertTrue(pets.isVisible())
            self.assertEqual(pets.currentItem().text(0), "TzRek-Jad")
            self._assert_current_row_reachable(pets)
            QTest.keyClick(pets, Qt.Key.Key_Home)
            _pump()
            self.assertEqual(pets.currentItem().text(0), "Baby Troll")
            self._assert_current_row_reachable(pets)
            self.assertEqual((dialog.width(), dialog.height()), (width, 560))
        finally:
            dialog.close()

    def test_reopening_pets_reveals_the_unchanged_current_row_at_both_fonts_sizes_and_themes(self):
        app = QApplication.instance()
        original_font = app.font()
        themes = (("light", app.style().standardPalette()), ("dark", _dark_palette()))
        for (theme, palette), scale, width in product(themes, (1.0, 1.5), (720, 980)):
            app.setPalette(palette)
            font = app.font()
            font.setPointSizeF(original_font.pointSizeF() * scale)
            app.setFont(font)
            with self.subTest(theme=theme, scale=scale, width=width):
                self._assert_reopening_reveals_current_pet(width)
