"""Keyboard navigation after a count click must update the player's current view."""

from __future__ import annotations

import unittest

from tests import test_main_menu_widget as _main_menu
from tests.ui_flows import test_first_cell_selection as _selection

if _main_menu.HAS_AQT:
    from aqt.qt import QAbstractItemView, QApplication, QLabel, QLineEdit, QProxyStyle, QStyle, Qt
    from PyQt6.QtTest import QTest

    class _MacMovementStyle(QProxyStyle):
        """Exercise macOS's current-index rules even on the offscreen Fusion lane."""

        def styleHint(self, hint, option=None, widget=None, returnData=None):
            if hint == QStyle.StyleHint.SH_ItemView_MovementWithoutUpdatingSelection:
                return 0
            if hint == QStyle.StyleHint.SH_ItemView_ScrollMode:
                return QAbstractItemView.ScrollMode.ScrollPerPixel.value
            return super().styleHint(hint, option, widget, returnData)


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class TreeKeyboardNavigationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        app = QApplication.instance()
        previous_style = app.style().objectName()
        self.addCleanup(app.setStyle, previous_style)
        app.setStyle(_MacMovementStyle("Fusion"))
        self.flow = _selection.FirstCellSelectionTest(methodName="runTest")
        self.flow.setUp()

    def tearDown(self) -> None:
        self.flow.tearDown()

    def test_down_after_a_music_count_click_opens_the_selected_family_and_target(self) -> None:
        tree = self.flow._tab_tree("collectionsFamilyTree")()
        dialog = tree.window()
        title = dialog.findChild(QLabel, "collectionsDetailTitle")
        search = dialog.findChild(QLineEdit, "collectionsSearch")
        music = tree.topLevelItem(0)
        count = tree.indexFromItem(music, 1)
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=tree.visualRect(count).center())
        _selection._pump()
        self.assertEqual(title.text(), "Music Log")
        changes = []
        tree.currentItemChanged.connect(lambda item, _previous: changes.append(item.text(0)))
        for item in (tree.topLevelItem(1), tree.topLevelItem(1).child(0)):
            search.setText("no matching collection")
            QTest.keyClick(tree, Qt.Key.Key_Down)
            _selection._pump()
            with self.subTest(name=item.text(0)):
                self.assertIs(tree.currentItem(), item)
                self.assertEqual(_selection._selected_cells(tree), [(0, item.text(0))])
                self.assertEqual(title.text(), item.text(0))
                self.assertEqual(search.text(), "")
                self.assertEqual(changes[-1:], [item.text(0)])

    def test_arrow_after_a_nonfirst_column_click_updates_current_item_signals_in_all_four_trees(self) -> None:
        for name in _selection._TAB_TREES:
            live = self.flow._tab_tree(name)
            tree = live()
            QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=self.flow._point(tree, 1))
            _selection._pump()
            expected = _selection._rows(tree)[2].data()
            model = tree.selectionModel()
            changes = []
            # Challenges rebuilds its items during currentItemChanged. Read
            # the live current item rather than keeping the old signal item.
            tree.currentItemChanged.connect(lambda *_args: changes.append(tree.currentItem().text(0)))
            QTest.keyClick(tree, Qt.Key.Key_Down)
            _selection._pump()
            with self.subTest(tree=name):
                self.assertEqual(changes, [expected])
                self.assertEqual(tree.currentItem().text(0), expected)
                self.assertEqual(tree.currentColumn(), 0)
                self.assertEqual(_selection._selected_cells(tree), [(0, expected)])
                self.assertTrue(tree.currentItem().isSelected())
                self.assertIs(tree.selectionModel(), model)

    def test_navigation_keys_move_the_current_item_as_well_as_the_highlight(self) -> None:
        _window, (_plain, tree) = self.flow._side_by_side()
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=self.flow._point(tree, 2))
        for key, row in ((Qt.Key.Key_End, 5), (Qt.Key.Key_Up, 4),
                         (Qt.Key.Key_Home, 0), (Qt.Key.Key_Down, 1)):
            QTest.keyClick(tree, key)
            _selection._pump()
            with self.subTest(key=key):
                self.assertEqual(tree.currentItem().text(0), f"Row {row}")
                self.assertEqual(tree.currentColumn(), 0)
                self.assertEqual(_selection._selected_cells(tree), [(0, f"Row {row}")])

    def test_keyboard_search_after_a_nonfirst_column_click_keeps_a_safe_current_selection(self) -> None:
        _window, (_plain, tree) = self.flow._side_by_side()
        tree.topLevelItem(5).setText(2, "Zulu note")
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=self.flow._point(tree, 1))
        QTest.keyClick(tree, Qt.Key.Key_Z)
        _selection._pump()
        self.assertEqual(tree.currentItem().text(0), "Row 5")
        self.assertEqual(_selection._selected_cells(tree), [(0, "Row 5")])
        self.assertTrue(tree.currentItem().isSelected())

    def test_select_key_reselects_the_first_cell_after_a_nonfirst_column_click(self) -> None:
        _window, (_plain, tree) = self.flow._side_by_side()
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=self.flow._point(tree, 2))
        tree.clearSelection()
        QTest.keyClick(tree, Qt.Key.Key_Select)
        _selection._pump()
        self.assertEqual(_selection._selected_cells(tree), [(0, "Row 2")])
        self.assertEqual(tree.currentItem().text(0), "Row 2")
        self.assertTrue(tree.currentItem().isSelected())

    def test_pets_keep_item_scrolling_when_the_platform_defaults_to_pixel_scrolling(self) -> None:
        tree = self.flow._tab_tree("summoningPetsLog")()
        self.assertEqual(tree.height(), 210)
        self.assertEqual(tree.verticalScrollMode(), QAbstractItemView.ScrollMode.ScrollPerItem)
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=self.flow._point(tree, 0))
        QTest.keyClick(tree, Qt.Key.Key_End)
        _selection._pump()
        last = tree.topLevelItem(tree.topLevelItemCount() - 1)
        self.assertIs(tree.currentItem(), last)
        self.assertEqual(_selection._selected_cells(tree), [(0, last.text(0))])
        self.assertTrue(tree.viewport().rect().contains(tree.visualItemRect(last)))


if __name__ == "__main__":
    unittest.main()
