"""Keyboard selection stays on screen through the log and Equipment viewports."""

from __future__ import annotations

import unittest
from itertools import product

from tests import test_main_menu_widget as _main_menu
from tests.ui_flows.test_pets_visible_rows import visible_rect

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPushButton, QScrollArea, Qt, QTreeWidget
    from PyQt6.QtTest import QTest


def _pump():
    for _ in range(6):
        QApplication.processEvents()


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PetsKeyboardVisibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        app = QApplication.instance()
        self.addCleanup(app.setFont, app.font())
        self.addCleanup(app.setPalette, app.palette())

    def tearDown(self):
        self.menu.tearDown()

    def _open_pets(self, width):
        from tests.ui_flows.test_first_cell_selection import _player

        dialog = self.menu._open(_player(), current_skill="Mining")
        dialog.show()
        dialog.resize(width, 560)
        _main_menu._open_equipment_tab(dialog)
        dialog.findChild(QPushButton, "summoningPetsToggle").click()
        _pump()
        self.assertEqual((dialog.width(), dialog.height()), (width, 560))
        pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
        first = pets.indexFromItem(pets.topLevelItem(0))
        # Click the actual visible part of Acquisition, without scrolling any ancestor.
        cell = pets.visualRect(first.siblingAtColumn(3)).intersected(visible_rect(pets.viewport()))
        self.assertFalse(cell.isEmpty())
        QTest.mouseClick(pets.viewport(), Qt.MouseButton.LeftButton, pos=cell.center())
        _pump()
        self._assert_selected_visible(pets, 0)
        return dialog, pets

    def _assert_selected_visible(self, pets, row):
        index = pets.indexFromItem(pets.topLevelItem(row))
        self.assertEqual(pets.selectionModel().selectedIndexes(), [index])
        self.assertEqual(pets.currentItem(), pets.topLevelItem(row))
        # Test real window clipping, not just the tree's larger internal viewport.
        room = pets.visualRect(index.siblingAtColumn(3))
        visible = visible_rect(pets.viewport())
        self.assertGreaterEqual(room.top(), visible.top(), index.data())
        self.assertLessEqual(room.bottom(), visible.bottom(), index.data())
        point = room.intersected(visible).center()
        self.assertIs(QApplication.widgetAt(pets.viewport().mapToGlobal(point)), pets.viewport(), index.data())

    def test_end_and_home_keep_the_selected_pet_visible_at_both_window_widths_and_fonts(self):
        from tests.ui_flows.test_first_cell_selection import _dark_palette

        app = QApplication.instance()
        original_font = app.font()
        themes = (("light", app.style().standardPalette()), ("dark", _dark_palette()))
        for (theme, palette), scale, width in product(themes, (1.0, 1.5), (720, 980)):
            app.setPalette(palette)
            font = app.font()
            font.setPointSizeF(original_font.pointSizeF() * scale)
            app.setFont(font)
            with self.subTest(theme=theme, scale=scale, width=width):
                dialog, pets = self._open_pets(width)
                last = pets.topLevelItemCount() - 1
                self.assertEqual(pets.topLevelItem(last).text(0), "TzRek-Jad")
                for key, row in ((Qt.Key.Key_End, last), (Qt.Key.Key_Home, 0), (Qt.Key.Key_End, last)):
                    QTest.keyClick(pets, key)
                    _pump()
                    self._assert_selected_visible(pets, row)
                dialog.close()

    def test_arrow_keys_keep_every_wrapped_row_visible_in_both_directions(self):
        app = QApplication.instance()
        original_font = app.font()
        for scale, width in product((1.0, 1.5), (720, 980)):
            font = app.font()
            font.setPointSizeF(original_font.pointSizeF() * scale)
            app.setFont(font)
            with self.subTest(scale=scale, width=width):
                dialog, pets = self._open_pets(width)
                last = pets.topLevelItemCount() - 1
                self.assertGreater(last, 40)
                for key, rows in ((Qt.Key.Key_Down, range(1, last + 1)), (Qt.Key.Key_Up, range(last - 1, -1, -1))):
                    for row in rows:
                        QTest.keyClick(pets, key)
                        _pump()
                        self._assert_selected_visible(pets, row)
                self.assertEqual(pets.height(), 210)
                self.assertEqual(pets.verticalScrollMode(), QTreeWidget.ScrollMode.ScrollPerItem)
                dialog.close()

    def test_home_and_end_reveal_an_unchanged_current_pet_after_manual_scrolling(self):
        for width in (720, 980):
            with self.subTest(width=width):
                dialog, pets = self._open_pets(width)
                outer = pets.parentWidget()
                while not isinstance(outer, QScrollArea):
                    outer = outer.parentWidget()
                bar = outer.verticalScrollBar()
                last = pets.topLevelItemCount() - 1
                for key, row in ((Qt.Key.Key_End, last), (Qt.Key.Key_Home, 0)):
                    QTest.keyClick(pets, key)
                    _pump()
                    self._assert_selected_visible(pets, row)
                    manual_position = bar.maximum()
                    bar.setValue(manual_position)
                    _pump()
                    self.assertEqual(bar.value(), manual_position)
                    room = pets.visualRect(pets.currentIndex())
                    visible = visible_rect(pets.viewport())
                    self.assertFalse(visible.contains(room), "Manual scrolling must hide the current pet for this check")
                    QTest.keyClick(pets, key)
                    _pump()
                    self._assert_selected_visible(pets, row)
                dialog.close()


if __name__ == "__main__":
    unittest.main()
