"""Space after a non-first-column click must preserve safe, visible row selection."""

from __future__ import annotations

import unittest

from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures
from tests.ui_flows import test_first_cell_selection as _selection

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, Qt
    from PyQt6.QtTest import QSignalSpy, QTest


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class TreeSpaceSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.flow = _selection.FirstCellSelectionTest(methodName="runTest")
        self.flow.setUp()

    def tearDown(self) -> None:
        self.flow.tearDown()

    def _click_cell(self, tree, column):
        tree.clearSelection()
        index = _selection._rows(tree)[2].siblingAtColumn(column)
        expected = index.siblingAtColumn(0).data()
        tree.scrollTo(index)
        _selection._pump()
        point = tree.visualRect(index).center()
        self.assertEqual(tree.indexAt(point), index)
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=point)
        _selection._pump()
        self.assertEqual(_selection._selected_cells(tree), [(0, expected)])
        return expected

    def test_space_after_clicking_each_other_column_keeps_selection_in_the_first_column(self) -> None:
        modifiers = (Qt.KeyboardModifier.NoModifier, Qt.KeyboardModifier.ControlModifier,
                     Qt.KeyboardModifier.ShiftModifier)
        for name in _selection._TAB_TREES:
            live = self.flow._tab_tree(name)
            for column in range(1, live().columnCount()):
                for modifier in modifiers:
                    with self.subTest(tree=name, column=column, modifier=modifier):
                        tree = live()
                        expected = self._click_cell(tree, column)
                        model = tree.selectionModel()
                        current = QSignalSpy(tree.currentItemChanged)
                        QTest.keyClick(tree, Qt.Key.Key_Space, modifier)
                        _selection._pump()
                        # Ctrl+Space retains Qt's toggle-off behavior.
                        selected = [] if modifier == Qt.KeyboardModifier.ControlModifier else [(0, expected)]
                        self.assertEqual(_selection._selected_cells(live()), selected)
                        self.assertEqual(live().currentItem().text(0), expected)
                        self.assertEqual(live().currentItem().isSelected(), bool(selected))
                        self.assertIs(live().selectionModel(), model)
                        self.assertEqual(len(current), 0)

    def test_space_reselects_the_current_row_with_item_selection_signals(self) -> None:
        tree = self.flow._tab_tree("collectionsFamilyTree")()
        expected = self._click_cell(tree, 1)
        tree.clearSelection()
        observed = []
        tree.itemSelectionChanged.connect(lambda: observed.append((
            _selection._selected_cells(tree), tree.currentItem().text(0), tree.currentItem().isSelected()
        )))
        QTest.keyClick(tree, Qt.Key.Key_Space)
        _selection._pump()
        self.assertEqual(observed, [([(0, expected)], expected, True)])
        self.assertEqual(_selection._selected_cells(tree), [(0, expected)])

    def test_space_after_a_count_click_keeps_the_full_row_highlight_in_both_themes(self) -> None:
        app = QApplication.instance()
        self.addCleanup(app.setPalette, app.palette())
        states = ("focused", "unfocused", "hover on another column, focused",
                  "hover on another column, unfocused", "inactive window")
        for theme, palette in (("light", app.style().standardPalette()), ("dark", _selection._dark_palette())):
            app.setPalette(palette)
            window, trees = self.flow._side_by_side()
            try:
                for tree in trees:
                    if tree is trees[1]:
                        self._click_cell(tree, 1)
                    else:
                        cell = _selection._rows(tree)[2].siblingAtColumn(1)
                        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=tree.visualRect(cell).center())
                    QTest.keyClick(tree, Qt.Key.Key_Space)
                for state in states:
                    with self.subTest(theme=theme, state=state):
                        plain, first_cell = self.flow._grab_pair(window, trees, 2, state)
                        self.assertEqual(plain, first_cell, "Space lost the full-row highlight")
            finally:
                window.close()


if __name__ == "__main__":
    unittest.main()
