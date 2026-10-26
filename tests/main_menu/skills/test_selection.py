from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _cooking_row,
    _find_list_with_user_role,
    _find_smith_tree,
    _find_tree_with_user_role,
    _goto_cooking,
    _goto_smithing,
    _make_player_data,
    _smith_row,
    _smith_tree_items,
    _tree_row,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QAbstractItemView, QApplication, QColor, QLabel, QListWidget, QScrollArea, QTest, QToolButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_target_details_are_optional_live_and_provenance_free(self) -> None:
        pd = _make_player_data()
        pd["cooking_level"] = 33
        pd["inventory"] = {"Raw shrimps": 2, "Raw beef": 1}
        pd["current_cooking"] = "cook_shrimps"
        dialog = self._open(pd, current_skill="Cooking")
        dialog.show()
        QApplication.processEvents()

        tree = _goto_cooking(dialog)
        toggle = dialog.findChild(QToolButton, "targetDetailsToggle")
        panel = dialog.findChild(QWidget, "targetDetailsPanel")
        title = dialog.findChild(QLabel, "targetDetailsTitle")
        body = dialog.findChild(QLabel, "targetDetailsBody")
        details_scroll = dialog.findChild(QScrollArea, "targetDetailsScroll")

        self.assertTrue(toggle.isVisibleTo(dialog))
        self.assertFalse(panel.isVisibleTo(dialog))
        self.assertEqual(details_scroll.maximumHeight(), 190)
        self.assertEqual(title.text(), "Cook raw shrimps (Lvl 1)")
        self.assertIn("Success output: Shrimps x1", body.text())
        self.assertIn("Success chance:", body.text())
        self.assertNotIn("Source:", body.text())

        toggle.click()
        QApplication.processEvents()
        self.assertTrue(panel.isVisibleTo(dialog))
        self.assertEqual(toggle.arrowType(), Qt.ArrowType.DownArrow)

        beef = _cooking_row(tree, "cook_beef")
        tree.setCurrentItem(beef)
        QApplication.processEvents()
        self.assertEqual(title.text(), "Cook raw beef (Lvl 1)")
        self.assertIn("Success output: Cooked meat x1", body.text())
        self.assertTrue(panel.isVisibleTo(dialog))

        calls_before_locked_click = list(self._cooking_calls)
        shark = _cooking_row(tree, "cook_shark")
        tree.itemClicked.emit(shark, 0)
        QApplication.processEvents()
        self.assertEqual(title.text(), "Cook raw shark (Lvl 80)")
        self.assertIn("Locked due to:", body.text())
        self.assertEqual(self._cooking_calls, calls_before_locked_click)

        self._ui._MAIN_MENU_CTX["open_farming"]()
        QApplication.processEvents()
        farming_panel = dialog.findChild(QWidget, "targetDetailsPanel")
        self.assertFalse(farming_panel.isVisibleTo(dialog))
        dialog.deleteLater()

    def test_flat_target_details_use_the_current_registry_row(self) -> None:
        pd = _make_player_data()
        pd["mining_level"] = 33
        pd["current_ore"] = "copper"
        dialog = self._open(pd, current_skill="Mining")
        dialog.show()
        QApplication.processEvents()

        toggle = dialog.findChild(QToolButton, "targetDetailsToggle")
        title = dialog.findChild(QLabel, "targetDetailsTitle")
        body = dialog.findChild(QLabel, "targetDetailsBody")

        self.assertTrue(toggle.isVisibleTo(dialog))
        self.assertIn("Copper", title.text())
        self.assertIn("Output: Copper ore x1", body.text())
        self.assertIn("Best usable pickaxe: Bronze pickaxe", body.text())
        self.assertNotIn("Source:", body.text())

        ore_list = _find_list_with_user_role(dialog, "copper")
        runite = next(
            ore_list.item(index)
            for index in range(ore_list.count())
            if ore_list.item(index).data(Qt.ItemDataRole.UserRole) == "runite"
        )
        ore_list.itemClicked.emit(runite)
        QApplication.processEvents()
        self.assertIn("Runite", title.text())
        self.assertIn("Locked due to:", body.text())
        dialog.deleteLater()

    def test_flat_target_lists_mark_the_current_target(self) -> None:
        # The flat lists (Mining/Woodcutting/Firemaking/Fishing) lost their
        # visible current-target mark: QStyle's legacy selection rect renders
        # as a near-white wash under alternatingRowColors, so the row is
        # marked with the grouped tree's green brush instead.
        for skill, key, target in (
            ("Mining", "current_ore", "rune_essence"),
            ("Woodcutting", "current_tree", "tree"),
        ):
            pd = _make_player_data()
            pd[key] = target
            dialog = self._open(pd, current_skill=skill)
            try:
                dialog.show()
                QApplication.processEvents()
                target_list = next(
                    widget
                    for widget in dialog.findChildren(QListWidget)
                    if any("(Lvl" in widget.item(i).text() for i in range(widget.count()))
                )
                current = target_list.currentItem()
                self.assertIsNotNone(current, skill)
                self.assertEqual(
                    current.data(Qt.ItemDataRole.UserRole), target, skill
                )
                self.assertEqual(
                    current.background().color(), QColor(76, 175, 80, 120), skill
                )
                self.assertTrue(current.text().startswith("✓ "), skill)
                self.assertTrue(current.font().bold(), skill)
                self.assertFalse(current.isSelected(), skill)
                self.assertIn("QListWidget::item:selected", target_list.styleSheet())
                self.assertIn("rgba(66,133,244,0.35)", target_list.styleSheet())
            finally:
                dialog.deleteLater()

    def test_flat_target_highlight_tracks_the_last_clicked_target(self) -> None:
        pd = _make_player_data()
        pd["mining_level"] = 99
        pd["current_ore"] = "silver"
        dialog = self._open(pd, current_skill="Mining")
        dialog.show()
        QApplication.processEvents()
        target_list = next(
            widget
            for widget in dialog.findChildren(QListWidget)
            if any("Silver" in widget.item(i).text() for i in range(widget.count()))
        )
        silver = next(
            target_list.item(i)
            for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "silver"
        )
        coal = next(
            target_list.item(i)
            for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "coal"
        )

        target_list.itemClicked.emit(coal)
        QApplication.processEvents()

        self.assertEqual(target_list.currentItem(), coal)
        self.assertEqual(coal.background().color(), QColor(76, 175, 80, 120))
        self.assertTrue(coal.text().startswith("✓ "))
        self.assertFalse(silver.text().startswith("✓ "))
        self.assertTrue(coal.font().bold())
        self.assertNotEqual(silver.background().color(), QColor(76, 175, 80, 76))
        self.assertFalse(silver.font().bold())
        self.assertFalse(coal.isSelected())

    def test_skill_selector_hybridizes_at_twenty_five_rows(self) -> None:
        from ankiscape.core.target_metadata import TargetRowMetadata

        def _rows(count: int, *, grouped: bool = True) -> tuple[TargetRowMetadata, ...]:
            return tuple(
                TargetRowMetadata(
                    target_id=f"hybrid_{index}",
                    label=f"Hybrid target {index}",
                    tooltip=f"Target {index}",
                    current=index == 0,
                    group="other" if grouped else "",
                    sort_key=(index,),
                )
                for index in range(count)
            )

        dialogs = []
        try:
            with patch.object(self._ui, "crafting_target_rows", return_value=_rows(24)):
                flat_dialog = self._open(_make_player_data(), current_skill="Crafting")
            dialogs.append(flat_dialog)
            flat_dialog.show()
            flat_dialog.resize(900, 560)

            with patch.object(self._ui, "crafting_target_rows", return_value=_rows(25)):
                tree_dialog = self._open(_make_player_data(), current_skill="Crafting")
            dialogs.append(tree_dialog)
            tree_dialog.show()
            tree_dialog.resize(900, 560)

            for _ in range(4):
                QApplication.processEvents()

            flat = _find_list_with_user_role(flat_dialog, "hybrid_0")
            tree = _find_tree_with_user_role(tree_dialog, "hybrid_0")
            flat_current = flat.currentItem()
            tree_current = _tree_row(tree, "hybrid_0")
            flat.scrollToItem(flat_current)
            tree.scrollToItem(tree_current)
            QApplication.processEvents()

            self.assertEqual(flat.count(), 24)
            self.assertEqual(tree.topLevelItem(0).childCount(), 25)
            self.assertTrue(flat.alternatingRowColors())
            self.assertTrue(tree.alternatingRowColors())
            self.assertEqual(flat.visualItemRect(flat_current).height(), 30)
            self.assertEqual(tree.visualItemRect(tree_current).height(), 30)
            self.assertEqual(flat_current.background().color(), QColor(76, 175, 80, 120))
            self.assertEqual(tree_current.background(0).color(), QColor(76, 175, 80, 120))
            self.assertTrue(flat_current.text().startswith("✓ "))
            self.assertTrue(tree_current.text(0).startswith("✓ "))
            self.assertTrue(flat_current.font().bold())
            self.assertTrue(tree_current.font(0).bold())
        finally:
            for dialog in dialogs:
                dialog.deleteLater()

    def test_skill_selector_keeps_large_ungrouped_rows_flat(self) -> None:
        from ankiscape.core.target_metadata import TargetRowMetadata

        rows = tuple(
            TargetRowMetadata(
                target_id=f"ungrouped_{index}",
                label=f"Ungrouped target {index}",
                tooltip="No group metadata",
                current=index == 0,
            )
            for index in range(25)
        )
        with patch.object(self._ui, "crafting_target_rows", return_value=rows):
            dialog = self._open(_make_player_data(), current_skill="Crafting")
        try:
            dialog.show()
            dialog.resize(900, 560)
            for _ in range(4):
                QApplication.processEvents()
            selector = _find_list_with_user_role(dialog, "ungrouped_0")
            self.assertEqual(selector.count(), 25)
            with self.assertRaises(AssertionError):
                _find_tree_with_user_role(dialog, "ungrouped_0")
        finally:
            dialog.deleteLater()

    def test_grouped_target_highlight_tracks_a_real_last_click(self) -> None:
        pd = _make_player_data()
        pd["smithing_level"] = 99
        pd["inventory"] = {"Bronze bar": 10}
        pd["current_smith"] = "forge_bronze_dagger"
        dialog = self._open(pd)
        dialog.show()
        dialog.resize(900, 560)
        _goto_smithing(dialog)
        for _ in range(4):
            QApplication.processEvents()

        tree = _find_smith_tree(dialog)
        dagger = _smith_row(tree, "forge_bronze_dagger")
        hatchet = _smith_row(tree, "forge_bronze_hatchet")
        tree.scrollToItem(hatchet)
        QApplication.processEvents()
        QTest.mouseClick(
            tree.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            tree.visualItemRect(hatchet).center(),
        )
        QApplication.processEvents()

        self.assertEqual(self._smith_calls[-1], "forge_bronze_hatchet")
        self.assertIs(tree.currentItem(), hatchet)
        self.assertEqual(hatchet.background(0).color(), QColor(76, 175, 80, 120))
        self.assertTrue(hatchet.text(0).startswith("✓ "))
        self.assertFalse(dagger.text(0).startswith("✓ "))
        self.assertTrue(hatchet.font(0).bold())
        self.assertNotEqual(dagger.background(0).color(), QColor(76, 175, 80, 76))
        self.assertFalse(dagger.font(0).bold())
        self.assertFalse(hatchet.isSelected())
        dialog.deleteLater()

    def test_grouped_target_tree_styles_clicked_selection_separately_from_current_target(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze bar": 10}
        pd["current_smith"] = "forge_bronze_dagger"
        dialog = self._open(pd)
        dialog.show()
        dialog.resize(900, 560)
        _goto_smithing(dialog)
        for _ in range(3):
            QApplication.processEvents()

        tree = _find_smith_tree(dialog)
        current = tree.currentItem()
        self.assertIsNotNone(current)
        self.assertFalse(current.isSelected())
        clicked = next(
            item
            for item in _smith_tree_items(tree)
            if item.parent() is not None
            and item is not current
            and not item.isDisabled()
        )
        tree.setCurrentItem(clicked)

        self.assertTrue(clicked.isSelected())
        self.assertFalse(current.isSelected())
        self.assertEqual(
            tree.selectionMode(), QAbstractItemView.SelectionMode.SingleSelection
        )
        self.assertIn(
            "QTreeWidget::item:selected { color: palette(text); }",
            tree.styleSheet(),
        )
        self.assertNotIn("QTreeWidget::item:selected { border:", tree.styleSheet())
        self.assertNotIn("rgba(76,175,80", tree.styleSheet())
        self.assertEqual(current.background(0).color(), QColor(76, 175, 80, 120))
