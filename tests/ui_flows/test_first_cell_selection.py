"""Multi-column tab trees keep row selection in the first cell and still look and act row-selected.

Qt 6.11's macOS accessibility bridge crashed Anki whenever an accessibility
client read the selected children of a tree with whole-row selection (see
ui/ui_first_cell_tree.py). Every way a player selects a row, mouse, drag,
modifier clicks, keyboard and code, must leave exactly one selected cell, in
column 0, of the row the player meant; and the tree must paint that row
exactly like a plain row-selected QTreeWidget. Rows are compared by their
first-column text because the Challenges tab rebuilds its items whenever the
current item changes.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures

if _main_menu.HAS_AQT:
    from aqt.qt import (
        QApplication,
        QColor,
        QEvent,
        QHBoxLayout,
        QHoverEvent,
        QLineEdit,
        QMouseEvent,
        QPalette,
        QPointF,
        QPushButton,
        Qt,
        QTreeWidget,
        QTreeWidgetItem,
        QWidget,
    )
    from PyQt6.QtTest import QTest

_CHALLENGES = ("mining_copper_ore", "mining_tin_ore", "cooking_chicken", "woodcutting_oak_logs")
_TAB_TREES = ("collectionsFamilyTree", "collectionsDropTargets", "summoningPetsLog", "challengeTree")


def _pump() -> None:
    for _ in range(4):
        QApplication.processEvents()


def _player() -> dict:
    from ankiscape.logic.daily_challenges_logic import default_daily_challenges_state_pure
    from ankiscape.logic.summoning_logic import default_summoning_state_pure

    player = _main_menu._make_player_data()
    player["summoning_state"] = default_summoning_state_pure()
    player.update(default_daily_challenges_state_pure())
    player["daily_challenges"] = [
        {"instance_id": f"{challenge_id}-1", "challenge_id": challenge_id,
         "day": 1, "progress": 0, "credited": {}}
        for challenge_id in _CHALLENGES
    ]
    return player


def _rows(tree) -> list:
    """First-column indexes in view order."""
    rows, index = [], tree.indexFromItem(tree.topLevelItem(0))
    while index.isValid():
        rows.append(index)
        index = tree.indexBelow(index)
    return rows


def _selected_cells(tree) -> list:
    return [
        (index.column(), tree.itemFromIndex(index).text(0))
        for index in tree.selectionModel().selectedIndexes()
    ]


def _dark_palette() -> "QPalette":
    palette = QPalette()
    for role, color in (
        (QPalette.ColorRole.Window, QColor(45, 45, 45)),
        (QPalette.ColorRole.WindowText, QColor(230, 230, 230)),
        (QPalette.ColorRole.Base, QColor(30, 30, 30)),
        (QPalette.ColorRole.Button, QColor(45, 45, 45)),
        (QPalette.ColorRole.ButtonText, QColor(230, 230, 230)),
        (QPalette.ColorRole.AlternateBase, QColor(40, 40, 40)),
        (QPalette.ColorRole.Text, QColor(230, 230, 230)),
        (QPalette.ColorRole.Highlight, QColor(42, 130, 218)),
        (QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)),
    ):
        palette.setColor(role, color)
    return palette


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class FirstCellSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu_fixtures.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _tab_tree(self, name: str):
        dialog = self.menu._open(_player(), current_skill="Mining")
        dialog.show()
        dialog.resize(980, 560)
        _pump()
        tabs = _main_menu._find_main_tabs(dialog)
        label = {"collectionsFamilyTree": "Collections", "collectionsDropTargets": "Collections",
                 "summoningPetsLog": "Equipment", "challengeTree": "Challenges"}[name]
        tabs.setCurrentIndex(next(i for i in range(tabs.count()) if tabs.tabText(i) == label))
        _pump()
        if name == "collectionsDropTargets":
            navigation = dialog.findChild(QTreeWidget, "collectionsFamilyTree")
            navigation.setCurrentItem(navigation.topLevelItem(1))
            _pump()
        if name == "summoningPetsLog":
            dialog.findChild(QPushButton, "summoningPetsToggle").click()
            _pump()
        return lambda: next(
            tree for tree in dialog.findChildren(QTreeWidget)
            if tree.objectName() == name and tree.isVisible()
        )

    def _point(self, tree, row: int):
        """Centre of the row's last cell, after checking the pointer really lands in that column."""
        index = _rows(tree)[row].siblingAtColumn(tree.columnCount() - 1)
        tree.scrollTo(index)
        _pump()
        point = tree.visualRect(index).center()
        self.assertEqual(tree.indexAt(point), index)
        return point

    def _drag(self, tree, rows) -> None:
        points = [self._point(tree, row) for row in rows]
        viewport = tree.viewport()
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, points[0])
        for point in points[1:]:
            QApplication.sendEvent(viewport, QMouseEvent(
                QEvent.Type.MouseMove, QPointF(point), QPointF(viewport.mapToGlobal(point)),
                Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier,
            ))
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, points[-1])
        _pump()

    def _assert_every_path_selects_one_first_cell(self, name: str) -> None:
        live = self._tab_tree(name)
        tree = live()
        self.assertGreater(tree.columnCount(), 1)
        self.assertGreaterEqual(len(_rows(tree)), 4)
        self.assertEqual(tree.selectionMode(), QTreeWidget.SelectionMode.SingleSelection)

        def text(row: int) -> str:
            return _rows(live())[row].data()

        def click(row: int, modifier=None) -> None:
            tree = live()
            QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton,
                             modifier or Qt.KeyboardModifier.NoModifier, self._point(tree, row))
            _pump()

        steps = (
            ("click in the last column", lambda: click(1), 1),
            ("drag across three rows", lambda: self._drag(live(), (0, 1, 2)), 2),
            ("shift-click", lambda: click(1, Qt.KeyboardModifier.ShiftModifier), 1),
            ("ctrl-click another row", lambda: click(3, Qt.KeyboardModifier.ControlModifier), 3),
            ("ctrl+A", lambda: QTest.keyClick(live(), Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier), 3),
            ("setCurrentItem", lambda: live().setCurrentItem(live().itemFromIndex(_rows(live())[0])), 0),
            ("down arrow", lambda: QTest.keyClick(live(), Qt.Key.Key_Down), 1),
        )
        for label, action, row in steps:
            with self.subTest(tree=name, step=label):
                expected = text(row)
                action()
                _pump()
                self.assertEqual(_selected_cells(live()), [(0, expected)])
                self.assertEqual(live().currentItem().text(0), expected)

    def test_every_selection_path_on_each_tab_tree(self) -> None:
        for name in _TAB_TREES:
            self._assert_every_path_selects_one_first_cell(name)

    def _side_by_side(self, first_cell_tree=None):
        from ankiscape.ui.ui_first_cell_tree import FirstCellSelectionTree

        window = QWidget()
        layout = QHBoxLayout(window)
        window.elsewhere = QLineEdit()
        layout.addWidget(window.elsewhere)
        trees = (QTreeWidget(), (first_cell_tree or FirstCellSelectionTree)())
        for tree in trees:
            tree.setHeaderLabels(["Name", "Count", "Note"])
            tree.setRootIsDecorated(False)
            tree.setAlternatingRowColors(True)
            tree.addTopLevelItems(
                [QTreeWidgetItem([f"Row {row}", f"{row}/7", f"Note for row {row}"]) for row in range(6)]
            )
            tree.setFixedSize(360, 200)
            layout.addWidget(tree)
        window.show()
        _pump()
        window.activateWindow()
        _pump()
        return window, trees

    def _deactivate(self, window) -> None:
        other = QWidget()
        other.show()
        other.activateWindow()
        _pump()
        self.assertFalse(window.isActiveWindow())

    @staticmethod
    def _hover(tree, index) -> None:
        middle = QPointF(tree.visualRect(index).center())
        QApplication.sendEvent(tree.viewport(), QHoverEvent(QEvent.Type.HoverMove, middle, middle, middle))

    def _grab_pair(self, window, trees, row: int, state: str) -> list:
        """Both trees' images in one state. Focus is set per grab: only one tree can hold it."""
        if state == "inactive window":
            self._deactivate(window)
        images = []
        for tree in trees:
            (window.elsewhere if "unfocused" in state else tree).setFocus()
            if state.startswith("hover"):
                self._hover(tree, _rows(tree)[row].siblingAtColumn(1))
            _pump()
            images.append(tree.grab().toImage())
        return images

    def test_a_selected_row_paints_exactly_like_a_row_selected_tree(self) -> None:
        app = QApplication.instance()
        self.addCleanup(app.setPalette, app.palette())
        states = ("focused", "unfocused", "hover on another column, focused",
                  "hover on another column, unfocused", "inactive window")
        for theme, palette in (("light", app.style().standardPalette()), ("dark", _dark_palette())):
            app.setPalette(palette)
            for row in (1, 2):  # one plain and one alternate-coloured row
                window, trees = self._side_by_side()
                for tree in trees:
                    QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton,
                                     Qt.KeyboardModifier.NoModifier, self._point(tree, row))
                for state in states:
                    plain, first_cell = self._grab_pair(window, trees, row, state)
                    with self.subTest(theme=theme, row=row, state=state):
                        self.assertTrue(plain == first_cell, "selected row differs from a row-selected tree")

    def test_dark_capture_palette_has_legible_button_text(self) -> None:
        palette = _dark_palette()
        for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
            with self.subTest(group=group):
                self.assertLess(palette.color(group, QPalette.ColorRole.Button).lightness(), 64)
                self.assertGreater(palette.color(group, QPalette.ColorRole.ButtonText).lightness(), 200)

    def test_a_click_selects_the_first_cell_while_column_zero_is_scrolled_away(self) -> None:
        _window, (_plain, tree) = self._side_by_side()
        tree.setColumnWidth(0, 300)
        tree.setColumnWidth(1, 300)
        _pump()
        tree.horizontalScrollBar().setValue(tree.horizontalScrollBar().maximum())
        _pump()
        self.assertLess(tree.columnViewportPosition(0) + tree.columnWidth(0), 0)
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, self._point(tree, 3))
        self.assertEqual(_selected_cells(tree), [(0, "Row 3")])

    def test_the_pins_hold_one_first_cell_over_a_base_that_starts_in_extended_selection(self) -> None:
        """The pins, not QTreeView's defaults, keep the selection to one cell."""
        from ankiscape.ui.ui_first_cell_tree import FirstCellSelectionTree

        class ExtendedTree(QTreeWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)

        class PinnedTree(FirstCellSelectionTree, ExtendedTree):
            pass

        _window, (_plain, tree) = self._side_by_side(PinnedTree)
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, self._point(tree, 1))
        QTest.keyClick(tree, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        _pump()
        self.assertEqual(_selected_cells(tree), [(0, "Row 1")])
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.ShiftModifier, self._point(tree, 3))
        _pump()
        self.assertEqual(_selected_cells(tree), [(0, "Row 3")])

    def test_every_multi_column_tree_the_tabs_build_keeps_one_first_cell_selected(self) -> None:
        dialog = self.menu._open(_player(), current_skill="Mining")
        dialog.show()
        tabs = _main_menu._find_main_tabs(dialog)
        for index in range(tabs.count()):
            tabs.setCurrentIndex(index)
            _pump()
        navigation = dialog.findChild(QTreeWidget, "collectionsFamilyTree")
        navigation.setCurrentItem(navigation.topLevelItem(1))
        _pump()
        checked = set()
        for tree in dialog.findChildren(QTreeWidget):
            if tree.columnCount() < 2 or not tree.topLevelItemCount():
                continue
            last = tree.topLevelItem(tree.topLevelItemCount() - 1)
            expected = last.text(0)
            tree.setCurrentItem(last)
            with self.subTest(tree=tree.objectName()):
                self.assertEqual(_selected_cells(tree), [(0, expected)])
            checked.add(tree.objectName())
        self.assertLessEqual(set(_TAB_TREES), checked)


if __name__ == "__main__":
    unittest.main()
