from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _bank_grid_button,
    _bank_grid_buttons,
    _bank_grid_texts,
    _find_named_label,
    _find_named_line_edit,
    _find_named_widget,
    _make_player_data,
    _open_bank_tab,
    _open_equipment_tab,
    copy,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QComboBox, QEvent, QLabel, QLineEdit, QListWidget, QObject, QPoint, QPushButton, QScrollArea, QSignalSpy, QTest, QTimer, QToolButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_bank_catalog_is_built_only_on_first_selection(self) -> None:
        self.assertIsNone(self.dialog.findChild(QWidget, "bankGrid"))
        self.assertIsNone(self.dialog.findChild(QListWidget, "gearList"))

        _open_bank_tab(self.dialog)

        bank_grid = self.dialog.findChild(QWidget, "bankGrid")
        gear_list = self.dialog.findChild(QListWidget, "gearList")
        self.assertIsNotNone(bank_grid)
        self.assertIsNotNone(gear_list)
        self.assertGreater(
            len(_bank_grid_buttons(self.dialog))
            + len(bank_grid.findChildren(QLabel)),
            0,
        )
        self.assertGreater(gear_list.count(), 0)

        _open_equipment_tab(self.dialog)
        _open_bank_tab(self.dialog)
        self.assertIs(self.dialog.findChild(QWidget, "bankGrid"), bank_grid)

    def test_bank_search_filters_rows_and_categories_without_mutating_state(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Logs": 5,
            "Bronze bar": 2,
            "Arrow shafts": 30,
            "Feather": 50,
            "Bronze arrowtips": 15,
        }
        original_inventory = dict(pd["inventory"])
        dialog = self._open(pd)
        _open_bank_tab(dialog)
        search = _find_named_line_edit(dialog, "bankSearchInput")
        summary = _find_named_label(dialog, "bankSearchInputSummary")

        search.setText("arrow shafts")
        self.assertTrue((search_timeout := QSignalSpy(search.findChild(QTimer).timeout)).wait(1000))
        texts = _bank_grid_texts(dialog)
        self.assertIn("Fletched", texts)
        self.assertIn("Arrow shafts x30", texts)
        self.assertNotIn("Logs", texts)
        self.assertNotIn("Bronze bar x2", texts)
        self.assertEqual(summary.text(), "Showing 1/5")
        self.assertEqual(pd["inventory"], original_inventory)

        search.setText("materials")
        self.assertTrue(search_timeout.wait(1000))
        texts = _bank_grid_texts(dialog)
        self.assertIn("Materials", texts)
        self.assertIn("Feather x50", texts)
        self.assertNotIn("Arrow shafts x30", texts)

        search.setText("nothing-here")
        self.assertTrue(search_timeout.wait(1000))
        self.assertEqual(_bank_grid_texts(dialog), ["No Bank items match your search."])
        self.assertEqual(summary.text(), "Showing 0/5")

        search.clear()
        self.assertTrue(search_timeout.wait(1000))
        texts = _bank_grid_texts(dialog)
        self.assertIn("Logs x5", texts)
        self.assertIn("Arrow shafts x30", texts)
        self.assertEqual(summary.text(), "Showing 5/5")
        self.assertEqual(pd["inventory"], original_inventory)

    def test_bank_search_coalesces_renders_without_rebuilding_adjacent_controls(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Coal": 10, "Logs": 5, "Shrimps": 3}
        projection_calls: list[bool] = []

        def projection() -> dict:
            projection_calls.append(True)
            return {"items": ()}

        dialog = self._open(pd, get_ge_projection=projection)
        _open_bank_tab(dialog)
        search = _find_named_line_edit(dialog, "bankSearchInput")
        timer = search.findChild(QTimer)
        carried_button = dialog.findChild(QPushButton, "carriedBankItem::Coal")
        tab_button = dialog.findChild(QToolButton, "bankTab::main")
        self.assertIsNotNone(timer)
        self.assertIsNotNone(carried_button)
        self.assertIsNotNone(tab_button)
        projection_call_count = len(projection_calls)
        self.assertGreater(projection_call_count, 0)

        created_cells: list[str] = []

        class BankGridRenderProbe(QObject):
            def eventFilter(self, watched, event):
                if event.type() == QEvent.Type.ChildAdded:
                    child = event.child()
                    if isinstance(child, QToolButton) and child.objectName().startswith(
                        "bankGridItem::"
                    ):
                        created_cells.append(child.objectName())
                return False

        grid = _find_named_widget(dialog, "bankGrid")
        render_probe = BankGridRenderProbe(grid)
        grid.installEventFilter(render_probe)
        search.setText("c")
        search.setText("co")
        search.setText("coal")
        timer.stop()
        timer.timeout.emit()
        grid.removeEventFilter(render_probe)

        self.assertEqual(created_cells, ["bankGridItem::Coal"])
        self.assertEqual(len(projection_calls), projection_call_count)
        self.assertEqual(
            _find_named_label(dialog, "bankSearchInputSummary").text(),
            "Showing 1/3",
        )
        self.assertIs(
            dialog.findChild(QPushButton, "carriedBankItem::Coal"), carried_button
        )
        self.assertIs(dialog.findChild(QToolButton, "bankTab::main"), tab_button)

    def test_bank_frame_a_uses_twelve_54_pixel_columns_and_280_pixel_detail(self) -> None:
        from ankiscape.core.constants import ITEM_DEFINITIONS

        pd = _make_player_data()
        item_names = [definition.storage_key for definition in ITEM_DEFINITIONS[:14]]
        pd["inventory"] = {
            item_name: index + 1 for index, item_name in enumerate(item_names)
        }
        dialog = self._open(pd)
        _open_bank_tab(dialog)
        dialog.resize(1280, 752)
        dialog.show()
        for _ in range(4):
            QApplication.processEvents()

        frame = _find_named_widget(dialog, "bankFrameA")
        grid = _find_named_widget(dialog, "bankGrid")
        right = _find_named_widget(dialog, "bankRightColumn")
        outer_scroll = dialog.findChild(QScrollArea, "bankTabScroll")
        self.assertFalse(frame.isHidden())
        self.assertEqual(right.width(), 280)
        self.assertEqual(outer_scroll.horizontalScrollBar().maximum(), 0)
        self.assertIsNotNone(dialog.findChild(QLineEdit, "bankSearchInput"))
        self.assertIsNotNone(dialog.findChild(QComboBox, "bankSortCombo"))
        self.assertIsNotNone(dialog.findChild(QPushButton, "bankDropModeSwap"))
        self.assertIsNotNone(dialog.findChild(QPushButton, "bankDropModeInsert"))
        self.assertIsNotNone(dialog.findChild(QPushButton, "carriedInventoryHeader"))

        auto = dialog.findChild(QCheckBox, "bankAutoCategoriesCheck")
        auto.setChecked(False)
        for _ in range(3):
            QApplication.processEvents()
        cells = [
            button
            for button in grid.findChildren(QToolButton)
            if button.objectName().startswith("bankGridItem::")
        ]
        self.assertEqual(len(cells), 14)
        self.assertTrue(all(cell.size().width() == 54 for cell in cells))
        first_row_y = min(cell.mapTo(grid, QPoint(0, 0)).y() for cell in cells)
        first_row_x = sorted(
            cell.mapTo(grid, QPoint(0, 0)).x()
            for cell in cells
            if cell.mapTo(grid, QPoint(0, 0)).y() == first_row_y
        )
        self.assertEqual(len(first_row_x), 12)
        self.assertEqual(
            [right_x - left_x for left_x, right_x in zip(first_row_x, first_row_x[1:])],
            [54] * 11,
        )
        self.assertEqual(
            grid.findChild(QLabel, "bankGridEmpty"),
            None,
        )

    def test_bank_selection_keeps_cells_and_keyboard_focus_alive(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Coal": 10, "Logs": 5}
        dialog = self._open(pd)
        coal = _bank_grid_button(dialog, "Coal")
        logs = _bank_grid_button(dialog, "Logs")
        coal.setFocus()
        coal.click()
        QApplication.processEvents()
        self.assertIs(_bank_grid_button(dialog, "Coal"), coal)
        self.assertIs(_bank_grid_button(dialog, "Logs"), logs)
        self.assertNotEqual(coal.focusPolicy(), Qt.FocusPolicy.NoFocus)
        self.assertIn("Coal ×10", _find_named_label(dialog, "bankSelectedItem").text())

        pd["inventory"]["Coal"] = 42
        dialog._ankiscape_refresh_equipment()
        QApplication.processEvents()
        self.assertIn("Coal ×42", _find_named_label(dialog, "bankSelectedItem").text())

    def test_bank_cell_shift_f10_opens_its_keyboard_organization_menu(self) -> None:
        button = self._ui._BankDropButton(item_name="Coal")
        button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        requested: list[QPoint] = []
        button.customContextMenuRequested.connect(requested.append)
        QTest.keyClick(
            button,
            Qt.Key.Key_F10,
            Qt.KeyboardModifier.ShiftModifier,
        )
        self.assertEqual(len(requested), 1)

    def test_bank_large_quantity_is_compact_but_exact_in_accessible_copy(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Coins": 12_345_678}
        dialog = self._open(pd)
        coins = _bank_grid_button(dialog, "Coins")
        self.assertEqual(coins.text(), "×12.3M")
        self.assertIn("12,345,678", coins.accessibleName())
        self.assertIn("12,345,678", coins.toolTip())

    def test_bank_auto_categories_and_computed_sort_control_drag_state(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Logs": 5, "Bronze bar": 2, "Feather": 50}
        dialog = self._open(pd)
        _open_bank_tab(dialog)
        grid = _find_named_widget(dialog, "bankGrid")
        self.assertGreater(
            len(
                [
                    label
                    for label in grid.findChildren(QLabel)
                    if label.objectName().startswith("bankCategoryHeader::")
                ]
            ),
            0,
        )

        auto = dialog.findChild(QCheckBox, "bankAutoCategoriesCheck")
        auto.setChecked(False)
        QApplication.processEvents()
        self.assertEqual(
            [
                label
                for label in grid.findChildren(QLabel)
                if label.objectName().startswith("bankCategoryHeader::")
            ],
            [],
        )

        sort = dialog.findChild(QComboBox, "bankSortCombo")
        sort.setCurrentIndex(sort.findData("alphabetical"))
        QApplication.processEvents()
        computed_cells = [
            button
            for button in grid.findChildren(QToolButton)
            if button.objectName().startswith("bankGridItem::")
        ]
        self.assertTrue(computed_cells)
        self.assertTrue(all(not button.drag_enabled for button in computed_cells))
        sort.setCurrentIndex(sort.findData("manual"))
        QApplication.processEvents()
        manual_cells = [
            button
            for button in grid.findChildren(QToolButton)
            if button.objectName().startswith("bankGridItem::")
        ]
        self.assertTrue(all(button.drag_enabled for button in manual_cells))

    def test_bank_drop_guard_and_keyboard_organization_follow_sort_rules(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Coal": 10, "Logs": 5, "Shrimps": 3}
        dialog = self._open(pd)
        _open_bank_tab(dialog)
        self.assertFalse(dialog._ankiscape_bank_can_drop_item_on_cell("Coal", "Logs"))

        categorized_organize = next(
            action.menu()
            for action in dialog._ankiscape_equip_menu_for("Logs").actions()
            if action.text() == "Organize"
        )
        self.assertFalse(categorized_organize.actions()[0].isEnabled())
        self.assertFalse(categorized_organize.actions()[1].isEnabled())

        auto = dialog.findChild(QCheckBox, "bankAutoCategoriesCheck")
        auto.setChecked(False)
        QApplication.processEvents()
        self.assertTrue(dialog._ankiscape_bank_can_drop_item_on_cell("Coal", "Logs"))

        organize = next(
            action.menu()
            for action in dialog._ankiscape_equip_menu_for("Logs").actions()
            if action.text() == "Organize"
        )
        self.assertEqual(
            [action.text() for action in organize.actions() if not action.isSeparator()],
            ["Move earlier", "Move later", "Move to new tab"],
        )
        self.assertTrue(organize.actions()[0].isEnabled())
        organize.actions()[0].trigger()
        QApplication.processEvents()
        self.assertEqual(pd["bank_layout"]["items"]["Logs"]["position"], 0)
        self.assertEqual(pd["bank_layout"]["items"]["Coal"]["position"], 1)

        sort = dialog.findChild(QComboBox, "bankSortCombo")
        sort.setCurrentIndex(sort.findData("alphabetical"))
        QApplication.processEvents()
        self.assertFalse(dialog._ankiscape_bank_can_drop_item_on_cell("Coal", "Logs"))
        computed_organize = next(
            action.menu()
            for action in dialog._ankiscape_equip_menu_for("Logs").actions()
            if action.text() == "Organize"
        )
        self.assertFalse(computed_organize.actions()[0].isEnabled())
        self.assertFalse(computed_organize.actions()[1].isEnabled())

    def test_bank_grid_drop_seams_apply_insert_swap_and_tab_lifecycle(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Coal": 10, "Logs": 5, "Shrimps": 3}
        saved: list[dict] = []
        dialog = self._open(
            pd,
            on_save_player_data=lambda: saved.append(copy.deepcopy(pd)),
        )
        _open_bank_tab(dialog)

        dialog._ankiscape_bank_drop_item_on_new_tab("Coal")
        custom_tab = pd["bank_layout"]["selected_tab"]
        self.assertNotEqual(custom_tab, "main")
        main_button = dialog.findChild(QToolButton, "bankTab::main")
        custom_button = dialog.findChild(QToolButton, f"bankTab::{custom_tab}")
        main_button.click()
        QApplication.processEvents()
        self.assertIs(dialog.findChild(QToolButton, "bankTab::main"), main_button)
        self.assertIs(dialog.findChild(QToolButton, f"bankTab::{custom_tab}"), custom_button)
        custom_button.click()
        QApplication.processEvents()
        self.assertIs(dialog.findChild(QToolButton, f"bankTab::{custom_tab}"), custom_button)
        self.assertEqual(
            _find_named_label(dialog, "bankSearchInputSummary").text(),
            "Showing 1/1",
        )
        dialog._ankiscape_bank_drop_item_on_tab("Logs", custom_tab)
        self.assertEqual(pd["bank_layout"]["items"]["Coal"]["tab_id"], custom_tab)
        self.assertEqual(pd["bank_layout"]["items"]["Logs"]["tab_id"], custom_tab)

        dialog.findChild(QCheckBox, "bankAutoCategoriesCheck").setChecked(False)
        dialog.findChild(QPushButton, "bankDropModeInsert").click()
        dialog._ankiscape_bank_drop_item_on_cell("Coal", "Logs")
        self.assertEqual(pd["bank_layout"]["items"]["Logs"]["position"], 0)
        self.assertEqual(pd["bank_layout"]["items"]["Coal"]["position"], 1)

        dialog.findChild(QPushButton, "bankDropModeSwap").click()
        dialog._ankiscape_bank_drop_item_on_cell("Coal", "Logs")
        self.assertEqual(pd["bank_layout"]["items"]["Coal"]["position"], 0)
        self.assertEqual(pd["bank_layout"]["items"]["Logs"]["position"], 1)

        tab_button = dialog.findChild(QToolButton, f"bankTab::{custom_tab}")
        self.assertIsNotNone(tab_button)
        self.assertEqual(tab_button.text(), "Tab 1")
        self.assertFalse(tab_button.icon().isNull())
        tab_menu = dialog._ankiscape_bank_tab_menu_for(custom_tab)
        self.assertEqual(
            [action.text() for action in tab_menu.actions() if not action.isSeparator()],
            ["Rename…", "Choose icon…", "Move tab left", "Move tab right", "Delete tab"],
        )

        dialog._ankiscape_bank_drop_item_on_new_tab("Shrimps")
        second_tab = pd["bank_layout"]["selected_tab"]
        self.assertNotEqual(second_tab, custom_tab)
        first_tab_menu = dialog._ankiscape_bank_tab_menu_for(custom_tab)
        move_right = next(
            action for action in first_tab_menu.actions() if action.text() == "Move tab right"
        )
        self.assertTrue(move_right.isEnabled())
        move_right.trigger()
        QApplication.processEvents()
        self.assertEqual(
            [tab["id"] for tab in pd["bank_layout"]["tabs"]],
            ["main", second_tab, custom_tab],
        )
        dialog._ankiscape_bank_drop_item_on_tab("Shrimps", "main")
        self.assertNotIn(second_tab, [tab["id"] for tab in pd["bank_layout"]["tabs"]])
        dialog._ankiscape_bank_delete_tab(custom_tab)
        self.assertEqual([tab["id"] for tab in pd["bank_layout"]["tabs"]], ["main"])
        self.assertEqual(pd["bank_layout"]["items"]["Coal"]["tab_id"], "main")
        self.assertEqual(pd["bank_layout"]["items"]["Logs"]["tab_id"], "main")
        self.assertTrue(saved)
