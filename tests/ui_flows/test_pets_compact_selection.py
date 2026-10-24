"""Pets keeps its controls and selection in short windows and after menu rebuilds."""

from __future__ import annotations

import unittest
from itertools import product

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests.ui_flows.test_first_cell_selection import _dark_palette, _player, _rows, _selected_cells
from tests.ui_flows.test_tree_text_fit import _pump
from tests.ui_flows.test_pets_visible_rows import reveal_widget, visible_rect

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPoint, QPushButton, QRect, Qt, QTreeWidget
    from PyQt6.QtTest import QSignalSpy, QTest

    from tests.ui_flows.qt_text_fit import _cell_text_clipped, _view_item_option


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class PetsCompactSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        app = QApplication.instance()
        self.addCleanup(app.setPalette, app.palette())
        self.addCleanup(app.setFont, app.font())

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _open(self, player=None, **kwargs):
        dialog = self.menu._open(player or _player(), current_skill="Mining", **kwargs)
        dialog.show()
        dialog.resize(720, 560)
        _pump()
        _main_menu._open_equipment_tab(dialog)
        dialog.findChild(QPushButton, "summoningPetsToggle").click()
        _pump()
        return dialog, dialog.findChild(QTreeWidget, "summoningPetsLog")

    def _reveal(self, pets, index):
        pets.scrollTo(index, QTreeWidget.ScrollHint.PositionAtTop)
        _pump()
        reveal_widget(pets.viewport(), pets.visualRect(index))
        point = pets.visualRect(index).center()
        self.assertTrue(visible_rect(pets.viewport()).contains(pets.visualRect(index)),
                        f"{index.data()}: cell={pets.visualRect(index)}, visible={visible_rect(pets.viewport())}")
        self.assertIs(QApplication.widgetAt(pets.viewport().mapToGlobal(point)), pets.viewport())
        return point

    def _assert_compact_pets_geometry(self, dialog, pets):
        self.assertEqual(dialog.size().height(), 560)
        self.assertEqual(pets.height(), 210)
        self.assertEqual(pets.verticalScrollMode(), QTreeWidget.ScrollMode.ScrollPerItem)
        body = pets.parentWidget()
        self.assertTrue(body.rect().contains(pets.geometry()))
        actions = [dialog.findChild(QPushButton, name) for name in (
            "summoningHatchCutePhoenixButton", "summoningHatchMeanPhoenixButton",
            "summoningLetOutPetButton", "summoningReleasePetButton",
        )]
        actions = [action for action in actions if action.isVisible()]
        self.assertEqual(len(actions), 4)
        for action in actions:
            bounds = QRect(action.mapTo(body, QPoint()), action.size())
            self.assertFalse(bounds.intersects(pets.geometry()), action.objectName())
            self.assertTrue(body.rect().contains(bounds), action.objectName())
        return actions

    def _assert_pet_rows_reachable(self, pets):
        option = _view_item_option(pets)
        names = []
        for index in _rows(pets):
            acquisition = index.siblingAtColumn(3)
            point = self._reveal(pets, acquisition)
            self.assertFalse(_cell_text_clipped(pets, option, acquisition), index.data())
            if index.data() == "Cat":
                QTest.mouseClick(pets.viewport(), Qt.MouseButton.LeftButton, pos=point)
                _pump()
                self.assertEqual(_selected_cells(pets), [(0, "Cat")])
            names.append(index.data())
        self.assertIn("Cat", names)
        self.assertGreater(len(names), 40)

    def _assert_acquisition_width(self, pets, scale, width):
        if scale == 1.0:
            self.assertEqual(pets.horizontalScrollBar().maximum(), 0)
            return
        self.assertGreaterEqual(pets.columnWidth(3), 30 * pets.fontMetrics().averageCharWidth())
        if width == 720:
            self.assertGreater(pets.horizontalScrollBar().maximum(), 0)

    def _assert_actions_reachable(self, pets, actions):
        for action in actions:
            reveal_widget(action)
            self.assertTrue(visible_rect(action).contains(action.rect()))
            self.assertIs(QApplication.widgetAt(action.mapToGlobal(action.rect().center())), action)

    def test_compact_pets_and_actions_never_overlap_and_each_row_can_be_reached(self) -> None:
        from ankiscape.logic.pet_logic import acquire_pet_pure

        app = QApplication.instance()
        original_font = app.font()
        player, ok, _instance_id = acquire_pet_pure(_player(), "cat")
        self.assertTrue(ok)
        player["summoning_level"] = 72
        player["inventory"] = {"Phoenix egg": 1, "Cracked phoenix egg": 1}
        themes = (("light", app.style().standardPalette()), ("dark", _dark_palette()))
        for (theme, palette), scale in product(themes, (1.0, 1.5)):
            app.setPalette(palette)
            font = app.font()
            font.setPointSizeF(original_font.pointSizeF() * scale)
            app.setFont(font)
            dialog, pets = self._open(player)
            for width in (980, 720, 980):
                with self.subTest(theme=theme, scale=scale, width=width):
                    dialog.resize(width, 560)
                    _pump()
                    actions = self._assert_compact_pets_geometry(dialog, pets)
                    self._assert_pet_rows_reachable(pets)
                    self._assert_acquisition_width(pets, scale, width)
                    self._assert_actions_reachable(pets, actions)
            dialog.close()

    def _assert_tree_pointer_and_keyboard_selection(self, dialog, name):
        tabs = _main_menu._find_main_tabs(dialog)
        label = "Challenges" if name == "challengeTree" else "Collections"
        tabs.setCurrentIndex(next(i for i in range(tabs.count()) if tabs.tabText(i) == label))
        _pump()
        if name == "collectionsDropTargets":
            navigation = dialog.findChild(QTreeWidget, "collectionsFamilyTree")
            navigation.setCurrentItem(navigation.topLevelItem(1))
            _pump()
        tree = next(tree for tree in dialog.findChildren(QTreeWidget)
                    if tree.objectName() == name and tree.isVisible())
        model = tree.selectionModel()
        current = QSignalSpy(tree.currentItemChanged)
        selection = QSignalSpy(tree.itemSelectionChanged)
        row = _rows(tree)[2]
        expected = row.data()
        cell = row.siblingAtColumn(tree.columnCount() - 1)
        tree.scrollTo(cell)
        _pump()
        point = tree.visualRect(cell).center()
        self.assertEqual(tree.indexAt(point), cell)
        self.assertIs(QApplication.widgetAt(tree.viewport().mapToGlobal(point)), tree.viewport())
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=point)
        _pump()
        self.assertEqual(_selected_cells(tree), [(0, expected)])
        self.assertTrue(tree.currentItem().isSelected())
        expected = _rows(tree)[3].data()
        QTest.keyClick(tree, Qt.Key.Key_Down)
        _pump()
        self.assertEqual(_selected_cells(tree), [(0, expected)])
        self.assertTrue(tree.currentItem().isSelected())
        self.assertIs(tree.selectionModel(), model)
        self.assertGreaterEqual(len(current), 2)
        # Challenges rebuilds its items with signals blocked on current-item changes.
        self.assertGreaterEqual(len(selection), 1 if name == "challengeTree" else 2)

    def test_other_trees_accept_pointer_and_keyboard_selection_after_menu_recreation(self) -> None:
        app = QApplication.instance()
        themes = (("light", app.style().standardPalette()), ("dark", _dark_palette()))
        for (theme, palette), opened in product(themes, range(2)):
            app.setPalette(palette)
            dialog, _pets = self._open()
            for name in ("collectionsFamilyTree", "collectionsDropTargets", "challengeTree"):
                with self.subTest(theme=theme, opened=opened, tree=name):
                    self._assert_tree_pointer_and_keyboard_selection(dialog, name)
            dialog.close()
            dialog.deleteLater()
            _pump()

    def _assert_pets_pointer_keyboard_signals(self, pets):
        model = pets.selectionModel()
        current = QSignalSpy(pets.currentItemChanged)
        selection = QSignalSpy(pets.itemSelectionChanged)
        cat = next(index for index in _rows(pets) if index.data() == "Cat")
        for column in (1, 2, 3):
            cell = cat.siblingAtColumn(column)
            point = self._reveal(pets, cell)
            QTest.mouseClick(pets.viewport(), Qt.MouseButton.LeftButton, pos=point)
            _pump()
            self.assertEqual(_selected_cells(pets), [(0, "Cat")])
            self.assertTrue(pets.currentItem().isSelected())
            QTest.keyClick(pets, Qt.Key.Key_Down)
            _pump()
            self.assertEqual(_selected_cells(pets), [(0, pets.indexBelow(cat).data())])
            self.assertTrue(pets.currentItem().isSelected())
        self.assertIs(pets.selectionModel(), model)
        self.assertGreaterEqual(len(current), 6)
        self.assertGreaterEqual(len(selection), 6)
        self.assertEqual(sum(item.isSelected() for item in (
            pets.topLevelItem(row) for row in range(pets.topLevelItemCount())
        )), 1)

    def _assert_let_out_selected_cat(self, dialog, pets, calls, instance_id):
        model = pets.selectionModel()
        cat = next(index for index in _rows(pets) if index.data() == "Cat")
        # The action consumes the selected instance, even from a non-first cell.
        point = self._reveal(pets, cat.siblingAtColumn(3))
        QTest.mouseClick(pets.viewport(), Qt.MouseButton.LeftButton, pos=point)
        button = dialog.findChild(QPushButton, "summoningLetOutPetButton")
        self.assertTrue(button.isEnabled())
        reveal_widget(button)
        _pump()
        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        _pump()
        self.assertEqual(calls, [("let_out_pet", {"instance_id": instance_id})])
        # The command recreates log items; they still use the original Qt model.
        self.assertIs(pets.selectionModel(), model)
        cat = next(index for index in _rows(pets) if index.data() == "Cat")
        self.assertEqual(cat.siblingAtColumn(1).data(), "Active")
        point = self._reveal(pets, cat.siblingAtColumn(3))
        QTest.mouseClick(pets.viewport(), Qt.MouseButton.LeftButton, pos=point)
        _pump()
        self.assertEqual(_selected_cells(pets), [(0, "Cat")])
        self.assertTrue(pets.currentItem().isSelected())

    def test_reopened_pets_pointer_keyboard_and_item_signals_keep_one_first_cell(self) -> None:
        from ankiscape.logic.pet_logic import acquire_pet_pure, let_out_pet_pure

        player, ok, instance_id = acquire_pet_pure(_player(), "cat")
        self.assertTrue(ok)
        calls = []

        def command(action, payload):
            calls.append((action, payload))
            updated, ok, reason = let_out_pet_pure(player, payload["instance_id"])
            self.assertTrue(ok, reason)
            player.clear()
            player.update(updated)
            return {"ok": ok}

        for opened in range(2):
            dialog, pets = self._open(player, on_summoning_command=command)
            self._assert_pets_pointer_keyboard_signals(pets)
            if opened == 1:
                self._assert_let_out_selected_cat(dialog, pets, calls, instance_id)
            dialog.close()
            dialog.deleteLater()
            _pump()


if __name__ == "__main__":
    unittest.main()
