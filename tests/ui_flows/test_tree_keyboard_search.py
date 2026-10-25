"""Typing in any tree column must keep the matched row selected in column zero."""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests.ui_flows import test_first_cell_selection as _selection

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QHBoxLayout, Qt, QTreeWidget, QTreeWidgetItem, QWidget
    from PyQt6.QtTest import QSignalSpy, QTest


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class TreeKeyboardSearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.flow = _selection.FirstCellSelectionTest(methodName="runTest")
        self.flow.setUp()

    def tearDown(self) -> None:
        self.flow.tearDown()

    def test_typing_acquisition_selects_cat_and_keeps_item_signals(self) -> None:
        pets = self.flow._tab_tree("summoningPetsLog")()
        QTest.mouseClick(pets.viewport(), Qt.MouseButton.LeftButton, pos=self.flow._point(pets, 0))
        model = pets.selectionModel()
        self.assertEqual(pets.currentColumn(), 3)
        current = QSignalSpy(pets.currentItemChanged)
        selections, current_rows = [], []

        def selection_changed():
            selections.append(_selection._selected_cells(pets))
            current_rows.append(pets.currentItem().text(0))

        pets.itemSelectionChanged.connect(selection_changed)
        QTest.keyClicks(pets, "Gertrude")
        _selection._pump()
        self.assertEqual(_selection._selected_cells(pets), [(0, "Cat")])
        self.assertEqual(pets.currentItem().text(0), "Cat")
        self.assertTrue(pets.currentItem().isSelected())
        self.assertIs(pets.selectionModel(), model)
        self.assertGreater(len(current), 0)
        self.assertGreater(len(selections), 0)
        self.assertTrue(all(len(cells) == 1 and cells[0][0] == 0 for cells in selections), selections)
        self.assertEqual(current_rows, [cells[0][1] for cells in selections])
        self.assertEqual(sum(item.isSelected() for item in (
            pets.topLevelItem(row) for row in range(pets.topLevelItemCount())
        )), 1)

    def test_typing_a_name_selects_one_first_cell_in_each_tab_tree(self) -> None:
        for name in _selection._TAB_TREES:
            with self.subTest(tree=name):
                live = self.flow._tab_tree(name)
                tree = live()
                row = next(index for index in reversed(_selection._rows(tree)) if index.data().isascii())
                expected = row.data()
                tree.setCurrentItem(tree.topLevelItem(0))
                QTest.keyClicks(tree, expected)
                _selection._pump()
                self.assertEqual(_selection._selected_cells(live()), [(0, expected)])
                self.assertEqual(live().currentItem().text(0), expected)
                self.assertTrue(live().currentItem().isSelected())

    def _search_pair(self, column):
        from ankiscape.ui.ui_first_cell_tree import FirstCellSelectionTree

        window = QWidget()
        layout = QHBoxLayout(window)
        trees = (QTreeWidget(), FirstCellSelectionTree())
        for tree in trees:
            tree.setHeaderLabels(["Name", "State", "Acquisition"])
            tree.setRootIsDecorated(False)
            tree.setFixedSize(380, 200)
            tree.addTopLevelItems([
                QTreeWidgetItem([name, name + " state", name + " route"])
                for name in ("Other", "Gertrude", "George", "Gnome")
            ])
            layout.addWidget(tree)
        window.show()
        _selection._pump()
        for tree in trees:
            index = tree.indexFromItem(tree.topLevelItem(0), column)
            QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=tree.visualRect(index).center())
        return window, trees

    def _assert_search_sequence(self, trees):
        # Repeated keys cycle and a miss keeps the selection.
        for text, expected in (("g", "Gertrude"), ("g", "George"), ("g", "Gnome"), ("zzz", "Gnome")):
            images = []
            for tree in trees:
                tree.setFocus()
                QTest.keyClicks(tree, text)
                _selection._pump()
                self.assertEqual(tree.currentItem().text(0), expected)
                images.append(tree.grab().toImage())
            self.assertEqual(_selection._selected_cells(trees[1]), [(0, expected)])
            self.assertEqual(images[0], images[1], "search lost the full-row highlight")

    def test_a_current_match_can_be_reselected_and_a_miss_keeps_selection_empty(self) -> None:
        for query, expected in (("Other", [(0, "Other")]), ("Missing", [])):
            with self.subTest(query=query):
                window, trees = self._search_pair(2)
                try:
                    for tree in trees:
                        tree.clearSelection()
                        QTest.keyClicks(tree, query)
                        _selection._pump()
                        self.assertEqual(tree.currentItem().text(0), "Other")
                        self.assertEqual(tree.currentItem().isSelected(), bool(expected))
                    self.assertEqual(_selection._selected_cells(trees[1]), expected)
                finally:
                    window.close()

    def test_search_matches_qt_in_every_column_and_keeps_the_full_row_highlight(self) -> None:
        app = QApplication.instance()
        self.addCleanup(app.setPalette, app.palette())
        themes = (("light", app.style().standardPalette()), ("dark", _selection._dark_palette()))
        for theme, palette in themes:
            app.setPalette(palette)
            for column in range(3):
                with self.subTest(theme=theme, column=column):
                    window, trees = self._search_pair(column)
                    try:
                        self._assert_search_sequence(trees)
                    finally:
                        window.close()


if __name__ == "__main__":
    unittest.main()
