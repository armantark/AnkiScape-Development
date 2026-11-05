from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _make_player_data,
    _open_bank_tab,
    _open_equipment_tab,
    copy,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QComboBox, QLabel, QPoint, QPushButton, QScrollArea, QToolButton, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_carried_keep_drop_toggle_present_for_gathering_and_wired(self) -> None:
        from aqt.qt import QCheckBox

        calls: list = []
        dialog = self._open(
            _make_player_data(),
            carried_keep_drop_state="keep",
            on_set_carried_keep_drop=lambda drop: calls.append(drop),
        )
        _open_bank_tab(dialog)
        check = dialog.findChild(QCheckBox, "carriedKeepDropCheck")
        self.assertIsNotNone(check, "Keep/Drop toggle missing when a gathering target is active")
        self.assertFalse(check.isChecked())  # default keep
        check.setChecked(True)
        QApplication.processEvents()
        self.assertEqual(calls[-1], True)  # toggling to drop calls back with True
        dialog.deleteLater()

    def test_per_drop_loot_override_pill_present_and_wired(self) -> None:
        from aqt.qt import QCheckBox, QPushButton, QWidget

        calls: list = []
        rows = (
            {"item": "Bones", "mode": "keep"},
            {"item": "Raw chicken", "mode": "auto"},
        )
        dialog = self._open(
            _make_player_data(),
            loot_override_rows=rows,
            on_set_loot_override=lambda item, mode: calls.append((item, mode)),
        )
        # The per-drop overrides now live in the Combat setup panel (Equipment tab)
        # as icon cells with a binary Keep | Drop pill, behind an Advanced
        # disclosure. Neither segment lit means "Auto" (follow the value threshold).
        grid = dialog.findChild(QWidget, "combatLootOverrideGrid")
        self.assertIsNotNone(grid, "per-drop override grid missing")
        bones_keep = dialog.findChild(QPushButton, "lootOverrideKeep::Bones")
        bones_drop = dialog.findChild(QPushButton, "lootOverrideDrop::Bones")
        self.assertIsNotNone(bones_keep, "per-drop Keep segment missing")
        self.assertIsNotNone(bones_drop, "per-drop Drop segment missing")
        self.assertIsNone(
            dialog.findChild(QPushButton, "lootOverrideDrop::Feather"),
            "unobserved drops must not appear in the advanced control",
        )
        # Clicking Drop on a saved-Keep drop switches it to Leave and fires back.
        bones_drop.click()
        QApplication.processEvents()
        self.assertIn(("Bones", "leave"), calls)
        # Clicking the already-lit Drop segment again clears back to Auto.
        bones_drop.click()
        QApplication.processEvents()
        self.assertEqual(calls[-1], ("Bones", "auto"))

        # The simple "keep everything" toggle bulk-applies keep via the same callback.
        keep_all = dialog.findChild(QCheckBox, "combatLootKeepAllCheck")
        self.assertIsNotNone(keep_all)
        keep_all.setChecked(True)
        QApplication.processEvents()
        self.assertIn(("Raw chicken", "keep"), calls)
        dialog.deleteLater()

    def test_carried_keep_drop_toggle_absent_without_gathering_target(self) -> None:
        from aqt.qt import QCheckBox

        dialog = self._open(_make_player_data(), carried_keep_drop_state=None)
        self.assertIsNone(dialog.findChild(QCheckBox, "carriedKeepDropCheck"))
        dialog.deleteLater()

    def test_carried_layout_grid_present_wired_and_never_geometrically_compressed(self) -> None:
        # Regression guard: a plain QWidget housing 28 fixed-size cell buttons
        # defaults to a Preferred size policy, which a parent QVBoxLayout can
        # compress under space pressure -- silently clipping the grid down to a
        # sliver even though every cell reports its correct fixed size. Assert
        # actual Qt geometry (not a screenshot) so this can't regress unnoticed.
        from aqt.qt import QPushButton, QWidget

        quantity_calls: list = []
        clear_calls: list = []
        advanced_calls: list = []

        def get_cells():
            return tuple([("Iron ore", 1)] * 5 + [("Air rune", 5000)] + [(None, 0)] * 22)

        dialog = self._open(
            _make_player_data(),
            carried_pack_target_active=True,
            on_set_carried_advanced=lambda v: advanced_calls.append(v),
            carried_advanced_state=True,
            get_carried_layout_cells=get_cells,
            on_set_carried_layout_quantity=lambda name, quantity: quantity_calls.append(
                (name, quantity)
            ),
            on_clear_carried_layout=lambda: clear_calls.append(True),
        )
        # Layouts don't activate offscreen until the dialog is actually shown
        # (see .claude/rules/qt-offscreen-screenshots.md) -- without this, every
        # cell's geometry reads back as a stale (0, 0), masking the very
        # compression bug this test exists to catch.
        dialog.show()
        dialog.resize(560, 640)
        for _ in range(6):
            QApplication.processEvents()
        # The 28-slot editor now lives on the Equipment tab, always reachable.
        _open_equipment_tab(dialog)
        for _ in range(6):
            QApplication.processEvents()

        # The Auto|Custom segmented pill replaced the old advanced checkbox.
        # Custom mode is active (carried_advanced_state=True), so the manual
        # grid is the visible view.
        auto_btn = dialog.findChild(QPushButton, "carriedModeAuto")
        custom_btn = dialog.findChild(QPushButton, "carriedModeCustom")
        self.assertIsNotNone(auto_btn)
        self.assertIsNotNone(custom_btn)
        self.assertTrue(custom_btn.isChecked())

        grid = dialog.findChild(QWidget, "carriedLayoutGrid")
        self.assertIsNotNone(grid, "carried layout grid missing")
        self.assertTrue(grid.isVisibleTo(grid.window()))

        # All 28 cells exist and sit at their real, uncompressed geometry.
        cells = [dialog.findChild(QPushButton, f"carriedLayoutCell::{i}") for i in range(28)]
        self.assertTrue(all(cell is not None for cell in cells))
        # The container's actual size must equal its own sizeHint -- if a parent
        # layout compressed it, these would diverge (the bug this test guards).
        self.assertEqual(grid.size(), grid.sizeHint())
        for cell in cells:
            self.assertEqual(cell.size().width(), 44)
            self.assertEqual(cell.size().height(), 44)
        stack_caption = cells[5].findChild(QLabel, "carriedCellCaption")
        stack_icon = cells[5].findChild(QLabel, "carriedCellIcon")
        self.assertEqual(stack_caption.text(), "×5000")
        self.assertIsNotNone(stack_icon.pixmap())
        self.assertLessEqual(
            stack_caption.mapTo(cells[5], QPoint(0, 0)).x() + stack_caption.width(),
            cells[5].width(),
        )
        # Row 6 (the last of 7 rows) must be positioned below row 0, not clipped
        # into the same pixels -- the concrete symptom of the compression bug.
        self.assertGreater(cells[27].geometry().y(), cells[0].geometry().y() + 200)

        # Clicking a filled cell edits its absolute quantity via the callback.
        original_get_int = self._ui.QInputDialog.getInt
        self._ui.QInputDialog.getInt = lambda *a, **k: (7, True)
        try:
            cells[0].click()
            QApplication.processEvents()
        finally:
            self._ui.QInputDialog.getInt = original_get_int
        self.assertIn(("Iron ore", 7), quantity_calls)

        # Switching to Auto hides the grid and fires the callback.
        auto_btn.click()
        QApplication.processEvents()
        self.assertFalse(grid.isVisibleTo(grid.window()))
        self.assertIn(False, advanced_calls)

        # Clear button fires its callback.
        custom_btn.click()
        QApplication.processEvents()
        clear_btn = dialog.findChild(QPushButton, "carriedLayoutClearButton")
        self.assertIsNotNone(clear_btn)
        clear_btn.click()
        QApplication.processEvents()
        self.assertEqual(clear_calls, [True])
        dialog.deleteLater()

    def test_current_inventory_grid_merges_combat_loot_and_supplies_in_both_modes_and_tabs(self) -> None:
        pd = _make_player_data()
        pd["current_combat_target"] = "chicken"
        pd["inventory"] = {"Shark": 2, "Uncut sapphire": 1, "Coins": 500}
        pd["carried_inventory"] = {
            "chicken": {"Shark": 2, "Uncut sapphire": 1}
        }
        pd["combat_supply_loadout"] = {
            "food": {"Shark": 3, "Lobster": 3},
            "potions": {"Antipoison (4)": 1},
            "stat_potions": {"Prayer potion (4)": 1},
            "finishers": {},
            "hazards": {},
            "cannonballs": 25,
        }
        carried_items = [("Shark", 2), ("Uncut sapphire", 1), ("Coins", 500)]
        advanced_calls: list[bool] = []
        dialog = self._open(
            pd,
            current_skill="Combat",
            carried_auto_is_combat=True,
            carried_advanced_state=False,
            get_carried_inventory_items=lambda: tuple(carried_items),
            on_set_carried_advanced=lambda enabled: advanced_calls.append(enabled),
            carried_stackable_names=frozenset({"Cannonball"}),
        )
        dialog.show()
        dialog.resize(900, 560)
        _open_equipment_tab(dialog)
        for _ in range(6):
            QApplication.processEvents()

        with patch.object(
            self._ui,
            "combat_supply_loadout_summary_pure",
            wraps=self._ui.combat_supply_loadout_summary_pure,
        ) as supply_summary:
            self._ui._MAIN_MENU_CTX["refresh_carried_inventory"]()
            for _ in range(4):
                QApplication.processEvents()
        self.assertEqual(supply_summary.call_count, 1)

        inventory_before = copy.deepcopy(pd["inventory"])
        loadout_before = copy.deepcopy(pd["combat_supply_loadout"])
        primary_scroll = dialog.findChild(QScrollArea, "carriedCurrentInventory")
        self.assertTrue(dialog.findChild(QPushButton, "carriedModeAuto").isChecked())
        self.assertTrue(primary_scroll.isVisibleTo(dialog))
        self.assertEqual(
            dialog.findChild(QPushButton, "carriedCurrentItem::Shark")
            .findChild(QLabel, "carriedCellCaption")
            .text(),
            "×5",
        )
        self.assertIsNotNone(
            dialog.findChild(QPushButton, "carriedCurrentItem::Uncut sapphire")
        )
        antipoison = dialog.findChild(
            QPushButton, "carriedCurrentItem::Antipoison (4)"
        )
        self.assertIsNotNone(antipoison)
        antipoison_caption = antipoison.findChild(QLabel, "carriedCellCaption")
        self.assertGreaterEqual(
            antipoison_caption.width(),
            antipoison_caption.fontMetrics().horizontalAdvance("Antipoison (4)"),
        )
        self.assertEqual(
            dialog.findChild(QPushButton, "carriedCurrentItem::Cannonball")
            .findChild(QLabel, "carriedCellCaption")
            .text(),
            "×25",
        )
        self.assertIsNone(
            dialog.findChild(QPushButton, "carriedCurrentItem::Coins")
        )

        dialog.findChild(QPushButton, "carriedModeCustom").click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertTrue(primary_scroll.isVisibleTo(dialog))
        self.assertEqual(pd["inventory"], inventory_before)
        self.assertEqual(pd["combat_supply_loadout"], loadout_before)

        _open_bank_tab(dialog)
        header = dialog.findChild(QPushButton, "carriedInventoryHeader")
        self.assertFalse(header.isChecked())
        self.assertEqual(
            header.text(),
            "▸ Carried — 3 loot · 9 supplies · 12/28 slots",
        )
        self.assertNotIn("…", header.text())
        self.assertLessEqual(
            header.fontMetrics().horizontalAdvance(header.text()),
            header.contentsRect().width(),
        )
        if not header.isChecked():
            header.click()
        for _ in range(6):
            QApplication.processEvents()
        bank_scroll = dialog.findChild(QScrollArea, "carriedCurrentInventoryBank")
        self.assertTrue(bank_scroll.isVisibleTo(dialog))
        self.assertEqual(
            dialog.findChild(QPushButton, "carriedCurrentItemBank::Shark")
            .findChild(QLabel, "carriedCellCaption")
            .text(),
            "×5",
        )
        self.assertIsNone(
            dialog.findChild(QPushButton, "carriedCurrentItemBank::Coins")
        )
        dialog.findChild(QPushButton, "carriedModeAutoBank").click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertTrue(bank_scroll.isVisibleTo(dialog))
        self.assertEqual(pd["inventory"], inventory_before)
        self.assertEqual(pd["combat_supply_loadout"], loadout_before)
        self.assertEqual(advanced_calls, [True, False])
        dialog.deleteLater()

    def test_custom_pack_bank_grid_icons_quantity_menu_and_live_inventory(self) -> None:
        from ankiscape.core.constants import ITEM_DEFINITIONS
        from ankiscape.logic import inventory_pure

        pd = _make_player_data()
        pd["inventory"] = {"Iron ore": 20, "Bronze arrow": 11, "Coins": 100}
        for definition in ITEM_DEFINITIONS:
            if len(pd["inventory"]) >= 80:
                break
            pd["inventory"].setdefault(
                definition.storage_key, len(pd["inventory"]) + 1
            )
        layout: dict[str, int] = {}
        stackables = {"Coins"}
        carried_items = [("Iron ore", 2), ("Uncut sapphire", 1)]
        saved: list[dict] = []

        def get_cells():
            return tuple(inventory_pure.layout_to_grid_cells_pure(layout, stackables))

        def set_quantity(item_name: str, quantity: int) -> bool:
            updated, ok = inventory_pure.set_carried_layout_quantity_pure(
                layout,
                item_name,
                quantity,
                stackables,
            )
            if ok:
                layout.clear()
                layout.update(updated)
            return ok

        dialog = self._open(
            pd,
            carried_advanced_state=True,
            get_carried_layout_cells=get_cells,
            get_carried_inventory_items=lambda: tuple(carried_items),
            carried_stackable_names=stackables,
            on_set_carried_layout_quantity=set_quantity,
            on_save_player_data=lambda: saved.append(copy.deepcopy(pd)),
        )
        dialog.show()
        dialog.resize(900, 560)
        _open_equipment_tab(dialog)
        for _ in range(4):
            QApplication.processEvents()

        bank_grid = dialog.findChild(QScrollArea, "carriedBankPicker")
        self.assertIsNotNone(bank_grid)
        pack_grid = dialog.findChild(QWidget, "carriedLayoutGrid")
        self.assertGreater(
            bank_grid.mapTo(dialog, QPoint(0, 0)).x(),
            pack_grid.mapTo(dialog, QPoint(0, 0)).x() + pack_grid.width(),
        )
        combat_panel = dialog.findChild(QWidget, "equipmentCombatSetupPanel")
        equipment_scroll = combat_panel.parentWidget()
        while equipment_scroll is not None and not isinstance(equipment_scroll, QScrollArea):
            equipment_scroll = equipment_scroll.parentWidget()
        self.assertIsNotNone(equipment_scroll)
        self.assertEqual(equipment_scroll.horizontalScrollBar().maximum(), 0)

        def primary_bank_buttons() -> list[QPushButton]:
            return [
                button
                for button in bank_grid.findChildren(QPushButton)
                if button.objectName().startswith("carriedBankItem::")
            ]

        self.assertGreaterEqual(len(primary_bank_buttons()), 80)

        def assert_bank_grid_fits() -> tuple[int, int]:
            viewport = bank_grid.viewport()
            bank_buttons = primary_bank_buttons()
            viewport_left = viewport.mapToGlobal(QPoint(0, 0)).x()
            column_positions = {
                button.mapToGlobal(QPoint(0, 0)).x() - viewport_left
                for button in bank_buttons
            }
            for button in bank_buttons:
                left = button.mapToGlobal(QPoint(0, 0)).x() - viewport_left
                self.assertGreaterEqual(left, 0, button.objectName())
                self.assertLessEqual(
                    left + button.width(),
                    viewport.width(),
                    button.objectName(),
                )
            self.assertEqual(bank_grid.horizontalScrollBar().maximum(), 0)
            return bank_grid.width(), len(column_positions)

        width_at_900, columns_at_900 = assert_bank_grid_fits()
        self.assertGreater(columns_at_900, 2)
        dialog.resize(1200, 800)
        for _ in range(6):
            QApplication.processEvents()
        width_at_1200, columns_at_1200 = assert_bank_grid_fits()
        self.assertGreater(width_at_1200, width_at_900)
        self.assertGreater(columns_at_1200, columns_at_900)

        _open_bank_tab(dialog)
        dialog.resize(720, 540)
        carried_header = dialog.findChild(QPushButton, "carriedInventoryHeader")
        if not carried_header.isChecked():
            carried_header.click()
        for _ in range(6):
            QApplication.processEvents()
        bank_tab_scroll = dialog.findChild(QScrollArea, "bankTabScroll")
        self.assertIsNotNone(bank_tab_scroll)
        self.assertGreater(bank_tab_scroll.verticalScrollBar().maximum(), 0)
        self.assertEqual(bank_tab_scroll.horizontalScrollBar().maximum(), 0)

        bank_pack_grid = dialog.findChild(QWidget, "carriedLayoutGridBank")
        bank_tab_grid = dialog.findChild(QScrollArea, "carriedBankPickerBank")
        bank_current_inventory = dialog.findChild(
            QScrollArea, "carriedCurrentInventoryBank"
        )
        self.assertEqual(bank_pack_grid.height(), bank_pack_grid.sizeHint().height())
        self.assertTrue(bank_tab_grid.isHidden())
        self.assertEqual(bank_current_inventory.height(), 72)

        def assert_reachable_in_bank_tab(widget: QWidget) -> None:
            bank_tab_scroll.ensureWidgetVisible(widget, 0, 0)
            for _ in range(4):
                QApplication.processEvents()
            top = widget.mapTo(bank_tab_scroll.viewport(), QPoint(0, 0)).y()
            visible_height = max(
                0,
                min(bank_tab_scroll.viewport().height(), top + widget.height())
                - max(0, top),
            )
            self.assertEqual(visible_height, widget.height(), widget.objectName())

        assert_reachable_in_bank_tab(bank_pack_grid)
        assert_reachable_in_bank_tab(bank_current_inventory)
        main_bank_grid = dialog.findChild(QWidget, "bankGrid")
        self.assertGreater(
            len(
                [
                    button
                    for button in main_bank_grid.findChildren(QToolButton)
                    if button.objectName().startswith("bankGridItem::")
                ]
            ),
            2,
        )

        _open_equipment_tab(dialog)
        dialog.resize(760, 560)
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(equipment_scroll.horizontalScrollBar().maximum(), 0)
        assert_bank_grid_fits()

        iron_button = dialog.findChild(QPushButton, "carriedBankItem::Iron ore")
        self.assertIsNotNone(iron_button)
        iron_icon = iron_button.findChild(QLabel, "carriedCellIcon")
        iron_count = iron_button.findChild(QLabel, "carriedCellCaption")
        self.assertIsNotNone(iron_icon.pixmap())
        self.assertEqual(iron_count.text(), "×20")
        self.assertLessEqual(
            iron_count.mapTo(iron_button, QPoint(0, 0)).x() + iron_count.width(),
            iron_button.width(),
        )
        bronze_arrow = dialog.findChild(QPushButton, "carriedBankItem::Bronze arrow")
        self.assertEqual(
            bronze_arrow.findChild(QLabel, "carriedCellCaption").text(),
            "Bronze arrow\n×11",
        )
        iron_button.click()
        QApplication.processEvents()
        self.assertEqual(layout["Iron ore"], 1)
        first_pack_cell = dialog.findChild(QPushButton, "carriedLayoutCell::0")
        self.assertIsNotNone(
            first_pack_cell.findChild(QLabel, "carriedCellIcon").pixmap()
        )
        self.assertEqual(
            first_pack_cell.findChild(QLabel, "carriedCellCaption").text(), "×1"
        )
        self.assertIn("Iron ore", first_pack_cell.toolTip())

        menu = dialog._ankiscape_carried_add_menu_for("Iron ore", 20)
        self.assertEqual(
            [action.text() for action in menu.actions()],
            [
                "Add 1",
                "Add 5",
                "Add 10",
                "Add last X",
                "Add X…",
                "Add all",
                "Add all-but-one",
            ],
        )
        add_five = next(
            action
            for action in menu.actions()
            if action.objectName() == "carriedAddFiveAction"
        )
        add_five.trigger()
        QApplication.processEvents()
        self.assertEqual(layout["Iron ore"], 6)

        original_get_int = self._ui.QInputDialog.getInt
        self._ui.QInputDialog.getInt = lambda *a, **k: (7, True)
        try:
            add_x = next(
                action
                for action in menu.actions()
                if action.objectName() == "carriedAddXAction"
            )
            add_x.trigger()
            QApplication.processEvents()
        finally:
            self._ui.QInputDialog.getInt = original_get_int
        self.assertEqual(layout["Iron ore"], 13)
        refreshed_menu = dialog._ankiscape_carried_add_menu_for("Iron ore", 20)
        self.assertEqual(refreshed_menu.actions()[3].text(), "Add last X (7)")
        self.assertEqual(pd["carried_picker_last_x"], 7)
        self.assertEqual(saved[-1]["carried_picker_last_x"], 7)

        layout["Coins"] = 25
        coins_menu = dialog._ankiscape_carried_add_menu_for("Coins", 100)
        next(
            action
            for action in coins_menu.actions()
            if action.objectName() == "carriedAddAllButOneAction"
        ).trigger()
        QApplication.processEvents()
        self.assertEqual(layout["Coins"], 124)
        next(
            action
            for action in coins_menu.actions()
            if action.objectName() == "carriedAddAllAction"
        ).trigger()
        QApplication.processEvents()
        self.assertEqual(layout["Coins"], 224)

        current_loot = dialog.findChild(
            QPushButton,
            "carriedCurrentItem::Uncut sapphire",
        )
        current_inventory = dialog.findChild(QScrollArea, "carriedCurrentInventory")
        self.assertIsNotNone(current_loot)
        self.assertIn("Uncut sapphire ×1", current_loot.toolTip())
        self.assertTrue(current_loot.isEnabled())
        self.assertTrue(current_inventory.isVisibleTo(dialog))
        dialog.findChild(QPushButton, "carriedModeAuto").click()
        QApplication.processEvents()
        self.assertTrue(current_inventory.isVisibleTo(dialog))
        self.assertTrue(current_loot.isVisibleTo(dialog))

        carried_items[:] = [("Shark", 12)]
        self._ui._MAIN_MENU_CTX["refresh_carried_inventory"]()
        QApplication.processEvents()
        loaded_fish = dialog.findChild(QPushButton, "carriedCurrentItem::Shark")
        self.assertIsNotNone(loaded_fish)
        self.assertTrue(
            loaded_fish.findChild(QLabel, "carriedCellCaption").text().endswith("×12")
        )
        self.assertIn("Shark ×12", loaded_fish.toolTip())

        reopened = self._open(
            pd,
            carried_advanced_state=True,
            get_carried_layout_cells=get_cells,
            get_carried_inventory_items=lambda: (),
            carried_stackable_names=stackables,
            on_set_carried_layout_quantity=set_quantity,
        )
        reopened_menu = reopened._ankiscape_carried_add_menu_for("Iron ore", 20)
        self.assertEqual(reopened_menu.actions()[3].text(), "Add last X (7)")
        self.assertTrue(reopened_menu.actions()[3].isEnabled())
        reopened.deleteLater()
        dialog.deleteLater()

    def test_custom_pack_picker_plans_beyond_bank_stock_and_fills_available_slots(self) -> None:
        from ankiscape.logic import inventory_pure

        pd = _make_player_data()
        pd["inventory"] = {"Iron ore": 7}
        layout: dict[str, int] = {}

        def get_cells():
            return tuple(inventory_pure.layout_to_grid_cells_pure(layout, set()))

        def set_quantity(item_name: str, quantity: int) -> bool:
            updated, ok = inventory_pure.set_carried_layout_quantity_pure(
                layout,
                item_name,
                quantity,
                set(),
            )
            if ok:
                layout.clear()
                layout.update(updated)
            return ok

        dialog = self._open(
            pd,
            carried_advanced_state=True,
            get_carried_layout_cells=get_cells,
            on_set_carried_layout_quantity=set_quantity,
        )
        dialog.show()
        dialog.resize(900, 560)
        _open_equipment_tab(dialog)
        for _ in range(4):
            QApplication.processEvents()

        menu = dialog._ankiscape_carried_add_menu_for("Iron ore", 7)
        next(
            action
            for action in menu.actions()
            if action.objectName() == "carriedAddTenAction"
        ).trigger()
        QApplication.processEvents()
        self.assertEqual(layout["Iron ore"], 10)

        layout["Iron ore"] = 25
        pd["inventory"]["Iron ore"] = 20
        menu = dialog._ankiscape_carried_add_menu_for("Iron ore", 20)
        next(
            action
            for action in menu.actions()
            if action.objectName() == "carriedAddAllAction"
        ).trigger()
        QApplication.processEvents()
        self.assertEqual(layout["Iron ore"], inventory_pure.CARRIED_CAPACITY)

        layout.clear()
        pd["inventory"]["Iron ore"] = 40
        menu = dialog._ankiscape_carried_add_menu_for("Iron ore", 40)
        next(
            action
            for action in menu.actions()
            if action.objectName() == "carriedAddAllAction"
        ).trigger()
        QApplication.processEvents()
        self.assertEqual(layout["Iron ore"], inventory_pure.CARRIED_CAPACITY)
        dialog.deleteLater()

    def test_combat_supply_mode_dropdown_present_and_wired(self) -> None:
        from aqt.qt import QComboBox

        calls: list = []
        player = _make_player_data()
        player["combat_pack_mode"] = "balanced"
        dialog = self._open(
            player,
            current_skill="Combat",
            on_set_combat_pack_mode=lambda mode: calls.append(mode),
        )
        combo = dialog.findChild(QComboBox, "combatPackModeCombo")
        self.assertIsNotNone(combo, "combat supply-mode dropdown missing")
        self.assertEqual(
            [combo.itemData(i) for i in range(combo.count())],
            ["balanced", "max_output", "max_safety"],
        )
        self.assertEqual(combo.currentData(), "balanced")
        combo.setCurrentIndex(combo.findData("max_output"))
        QApplication.processEvents()
        self.assertIn("max_output", calls)
        dialog.deleteLater()

    def test_locked_dream_thrift_control_explains_its_requirements(self) -> None:
        player = _make_player_data()
        player["magic_level"] = 1
        player["quests"]["dream_mentor"] = {
            "started": False,
            "progress": 0,
            "completed": False,
        }
        dialog = self._open(player, current_skill="Combat")
        dream = dialog.findChild(QCheckBox, "combatDreamThriftCheck")
        self.assertIsNotNone(dream)
        self.assertFalse(dream.isEnabled())
        self.assertIn("79 Magic and Dream Mentor", dream.toolTip())
        dialog.deleteLater()

    def test_carried_layout_grid_reachable_without_an_active_pack_target(self) -> None:
        from aqt.qt import QPushButton, QWidget

        # Regression: the advanced editor used to disappear entirely when no pack
        # target was active. It now lives on the Equipment tab and is always
        # available so players can arrange their carried pack at any time.
        dialog = self._open(_make_player_data(), carried_pack_target_active=False)
        self.assertIsNotNone(dialog.findChild(QPushButton, "carriedModeAuto"))
        self.assertIsNotNone(dialog.findChild(QPushButton, "carriedModeCustom"))
        self.assertIsNotNone(dialog.findChild(QWidget, "carriedLayoutGrid"))
        dialog.deleteLater()
