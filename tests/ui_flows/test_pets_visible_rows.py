"""Pets must be reachable through the real window, including ancestor clipping."""

from __future__ import annotations

import unittest
from itertools import product

from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPushButton, QRect, QScrollArea, Qt, QTreeWidget
    from PyQt6.QtTest import QTest


def _pump():
    for _ in range(6):
        QApplication.processEvents()


def visible_rect(widget):
    """Widget coordinates clipped by every ancestor, up to the actual window."""
    visible = widget.rect()
    parent = widget.parentWidget()
    while parent is not None:
        bounds = QRect(widget.mapFrom(parent, parent.contentsRect().topLeft()), parent.contentsRect().size())
        visible = visible.intersected(bounds)
        parent = parent.parentWidget()
    return visible


def reveal_widget(widget, rect=None):
    rect = widget.rect() if rect is None else rect
    parent = widget.parentWidget()
    while parent is not None:
        if isinstance(parent, QScrollArea):
            # A fixed-height log can exceed its expansion viewport. Reveal the
            # requested cell instead of always aligning the bottom of the log.
            viewport = parent.viewport()
            bounds = QRect(widget.mapTo(viewport, rect.topLeft()), rect.size())
            shift = bounds.top() if bounds.top() < 0 else max(bounds.bottom() - viewport.rect().bottom(), 0)
            bar = parent.verticalScrollBar()
            bar.setValue(bar.value() + shift)
            _pump()
        parent = parent.parentWidget()


def assert_pet_rows_visible(test, pets, rows):
    """Scroll both views and require the complete Acquisition cell to be on screen."""
    reveal_widget(pets)
    for row in rows:
        cell = row.siblingAtColumn(3)
        pets.scrollTo(cell, QTreeWidget.ScrollHint.PositionAtTop)
        _pump()
        room = pets.visualRect(cell)
        reveal_widget(pets.viewport(), room)
        test.assertTrue(visible_rect(pets.viewport()).contains(room), row.data())
        test.assertIs(QApplication.widgetAt(pets.viewport().mapToGlobal(room.center())), pets.viewport(), row.data())


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PetsVisibleRowsTest(unittest.TestCase):
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

    def _assert_window(self, dialog, width):
        dialog.resize(width, 560)
        _pump()
        self.assertEqual((dialog.width(), dialog.height()), (width, 560))
        pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
        rows = [pets.indexFromItem(pets.topLevelItem(i)) for i in range(pets.topLevelItemCount())]
        self.assertIn("Cat", [row.data() for row in rows])
        self.assertIn("TzRek-Jad", [row.data() for row in rows])
        assert_pet_rows_visible(self, pets, rows)
        self.assertEqual(pets.height(), 210)
        self.assertEqual(pets.verticalScrollMode(), QTreeWidget.ScrollMode.ScrollPerItem)
        cat = next(row for row in rows if row.data() == "Cat")
        assert_pet_rows_visible(self, pets, [cat])
        QTest.mouseClick(pets.viewport(), Qt.MouseButton.LeftButton,
                         pos=pets.visualRect(cat.siblingAtColumn(3)).center())
        self.assertEqual([(i.column(), i.data()) for i in pets.selectionModel().selectedIndexes()], [(0, "Cat")])
        for name in ("summoningLetOutPetButton", "summoningReleasePetButton"):
            button = dialog.findChild(QPushButton, name)
            reveal_widget(button)
            self.assertTrue(visible_rect(button).contains(button.rect()), f"{name}: {visible_rect(button)} / {button.rect()}")
            self.assertIs(QApplication.widgetAt(button.mapToGlobal(button.rect().center())), button)

    def test_every_pet_and_its_actions_are_visible_in_short_light_and_dark_windows(self):
        from tests.ui_flows.test_first_cell_selection import _dark_palette, _player

        app = QApplication.instance()
        original_font = app.font()
        themes = (("light", app.style().standardPalette()), ("dark", _dark_palette()))
        for (theme, palette), scale in product(themes, (1.0, 1.5)):
            app.setPalette(palette)
            font = app.font()
            font.setPointSizeF(original_font.pointSizeF() * scale)
            app.setFont(font)
            dialog = self.menu._open(_player(), current_skill="Mining")
            dialog.show()
            dialog.resize(720, 560)
            _main_menu._open_equipment_tab(dialog)
            dialog.findChild(QPushButton, "summoningPetsToggle").click()
            _pump()
            for width in (720, 980, 720):
                with self.subTest(theme=theme, scale=scale, width=width):
                    self._assert_window(dialog, width)
            dialog.close()


if __name__ == "__main__":
    unittest.main()
