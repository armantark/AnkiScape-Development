from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_skill_list,
    _find_stats_button,
    _make_player_data,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QColor, QComboBox, QLabel, QListWidget, QPalette, QPushButton, QToolButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_farming_sheet_is_openable_without_train_button_or_target_prompt(self) -> None:
        farming_dialog = self._open(_make_player_data(), current_skill="Mining", initial_skill="Farming")
        farming_dialog.show()
        farming_dialog.resize(900, 560)
        for _ in range(6):
            QApplication.processEvents()
        panel = farming_dialog.findChild(QWidget, "farmingSkillPanel")
        self.assertIsNotNone(panel)
        self.assertIsNotNone(farming_dialog.findChild(QWidget, "farmingFarmSheet"))
        self.assertEqual(len([widget for widget in farming_dialog.findChildren(QWidget) if widget.objectName().startswith("farmingPatchCard::")]), 52)
        self.assertEqual(len([widget for widget in farming_dialog.findChildren(QLabel) if widget.objectName().startswith("farmingPatchVisual::")]), 52)
        self.assertEqual(len([widget for widget in farming_dialog.findChildren(QLabel) if widget.objectName().startswith("farmingCompostBinVisual::")]), 6)
        self.assertFalse(any(button.text() in {"Train this skill", "Currently training"} and button.isVisible() for button in farming_dialog.findChildren(QPushButton)))
        self.assertFalse(any(label.text() == "Select a target" and label.isVisible() for label in farming_dialog.findChildren(QLabel)))
        self.assertLessEqual(farming_dialog.minimumHeight(), 560)
        scroll = farming_dialog.findChild(QWidget, "farmingFarmScroll")
        self.assertGreater(scroll.height(), 0)
        self.assertIsNone(
            farming_dialog.findChild(
                QComboBox,
                "farmingPatchCropCombo::varrock_white_tree",
            )
        )
        white_tree_summary = farming_dialog.findChild(
            QLabel,
            "farmingPatchSummary::varrock_white_tree",
        )
        self.assertEqual(
            white_tree_summary.text(),
            "White Tree · Requires Garden of Tranquillity.",
        )
        white_tree_current = farming_dialog.findChild(
            QLabel,
            "farmingPatchCurrent::varrock_white_tree",
        )
        self.assertEqual(
            white_tree_current.text(),
            "Current: Locked",
        )

    def test_farming_livid_allotment_identifies_its_one_use_lifecycle(self) -> None:
        player_data = _make_player_data()
        player_data["farm_livid_patch_active"] = True
        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        QApplication.processEvents()

        summary = dialog.findChild(
            QLabel,
            "farmingPatchSummary::livid_farm_allotment",
        )
        self.assertIsNotNone(summary)
        self.assertIn("one-use", summary.text())
        dialog.deleteLater()

    def test_farming_plan_change_calls_unified_callback_immediately(self) -> None:
        farming_dialog = self._open(_make_player_data(), current_skill="Mining", initial_skill="Farming")
        farming_dialog.show()
        for _ in range(4):
            QApplication.processEvents()
        combo = farming_dialog.findChild(QComboBox, "farmingPatchCropCombo::falador_allotment_north")
        self.assertIsNotNone(combo)
        potato = combo.findData("potato")
        self.assertGreaterEqual(potato, 0)
        combo.setCurrentIndex(potato)
        QApplication.processEvents()
        self.assertTrue(self._farming_calls)
        action_id, payload = self._farming_calls[-1]
        self.assertEqual(action_id, "set_plan")
        self.assertEqual(payload["patch_id"], "falador_allotment_north")
        self.assertEqual(payload["crop_id"], "potato")

    def test_farming_sheet_can_activate_owned_juju_potion(self) -> None:
        player_data = _make_player_data()
        player_data["inventory"] = {"Juju farming potion (3)": 1}
        farming_dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        farming_dialog.show()
        for _ in range(4):
            QApplication.processEvents()

        activate = farming_dialog.findChild(QPushButton, "farmingActivateJujuButton")
        self.assertIsNotNone(activate)
        self.assertTrue(activate.isEnabled())
        self.assertIn("(3)", activate.text())
        activate.click()
        QApplication.processEvents()

        self.assertEqual(
            self._farming_calls[-1],
            ("activate_juju_farming_potion", {"item_name": "Juju farming potion (3)"}),
        )
        self.assertEqual(player_data["inventory"].get("Juju farming potion (3)", 0), 0)
        self.assertEqual(player_data["inventory"]["Juju farming potion (2)"], 1)
        self.assertGreater(player_data["farm_juju_active_until"], 0)

    def test_farming_stats_selector_is_present_but_farming_is_not_review_active(self) -> None:
        farming_button = _find_stats_button(self.dialog, "farming")
        self.assertEqual(
            farming_button.accessibleName(),
            "Farming, current level 33, base level 33",
        )
        skill_list = _find_skill_list(self.dialog)
        farming_item = next(skill_list.item(i) for i in range(skill_list.count()) if skill_list.item(i).text() == "Farming")
        self.assertTrue(bool(farming_item.flags() & Qt.ItemFlag.ItemIsEnabled))

    def test_farming_sheet_geometry_is_stable_at_default_and_laptop_heights_in_dark_mode(self) -> None:
        old_palette = QApplication.palette()
        old_style = QApplication.style().objectName()
        dark = QPalette()
        dark.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        dark.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        dark.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
        dark.setColor(QPalette.ColorRole.ButtonText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Mid, QColor(95, 95, 95))
        QApplication.setStyle("Fusion")
        QApplication.setPalette(dark)
        dialog = None
        try:
            dialog = self._open(_make_player_data(), current_skill="Mining", initial_skill="Farming")
            dialog.show()
            for _ in range(6):
                QApplication.processEvents()
            scroll = dialog.findChild(QWidget, "farmingFarmScroll")
            sheet = dialog.findChild(QWidget, "farmingFarmSheet")
            self.assertGreater(dialog.height(), 0)
            self.assertGreater(scroll.viewport().height(), 0)
            self.assertGreater(sheet.height(), scroll.viewport().height())
            self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)

            dialog.resize(900, 560)
            for _ in range(6):
                QApplication.processEvents()
            self.assertEqual((dialog.width(), dialog.height()), (900, 560))
            self.assertLessEqual(dialog.minimumHeight(), 560)
            self.assertGreater(scroll.viewport().height(), 0)
            self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
            text = dialog.palette().color(QPalette.ColorRole.Text)
            base = dialog.palette().color(QPalette.ColorRole.Base)
            self.assertGreater(text.lightness(), base.lightness())
        finally:
            if dialog is not None:
                dialog.deleteLater()
            QApplication.setPalette(old_palette)
            QApplication.setStyle(old_style)

    def test_farming_location_and_patch_details_use_progressive_disclosure(self) -> None:
        dialog = self._open(_make_player_data(), current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        location = dialog.findChild(QToolButton, "farmingLocationToggle::falador")
        card = dialog.findChild(QWidget, "farmingPatchCard::falador_allotment_north")
        expand = dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north")
        details = dialog.findChild(QWidget, "farmingPatchDetails::falador_allotment_north")
        self.assertFalse(location.isChecked())
        self.assertFalse(card.isVisible())
        self.assertFalse(details.isVisible())

        location.click()
        for _ in range(3):
            QApplication.processEvents()
        self.assertTrue(location.isChecked())
        self.assertTrue(card.isVisible())
        self.assertFalse(details.isVisible())
        expand.click()
        for _ in range(3):
            QApplication.processEvents()
        self.assertTrue(expand.isChecked())
        self.assertTrue(details.isVisible())
        dialog.deleteLater()

    def test_disabled_farming_controls_cannot_mutate_state(self) -> None:
        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {"Rake": 1, "Seed dibber": 1, "Potato seed": 2}
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        location = dialog.findChild(QToolButton, "farmingLocationToggle::falador")
        location.click()
        QApplication.processEvents()
        expand = dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north")
        expand.click()
        QApplication.processEvents()
        combo = dialog.findChild(QComboBox, "farmingPatchCropCombo::falador_allotment_north")
        watermelon_index = combo.findData("watermelon")
        self.assertGreaterEqual(watermelon_index, 0)
        self.assertFalse(combo.model().item(watermelon_index).isEnabled())
        before = dict(player_data.get("farm_plans", {}))
        combo.setCurrentIndex(watermelon_index)
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(player_data.get("farm_plans", {}), before)
        self.assertIsNone(player_data.get("farm_plans", {}).get("falador_allotment_north"))
        dialog.deleteLater()

    def test_farming_plan_and_queue_actions_refresh_the_visible_sheet_immediately(self) -> None:
        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 6}
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingLocationToggle::falador").click()
        QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north").click()
        QApplication.processEvents()
        combo = dialog.findChild(QComboBox, "farmingPatchCropCombo::falador_allotment_north")
        combo.setCurrentIndex(combo.findData("potato"))
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(player_data["farm_plans"]["falador_allotment_north"]["crop_id"], "potato")
        summary = dialog.findChild(QLabel, "farmingPatchSummary::falador_allotment_north")
        primary = dialog.findChild(QPushButton, "farmingPatchPrimaryAction::falador_allotment_north")
        self.assertIn("Empty", summary.text())
        self.assertEqual(primary.text(), "Queue plant")
        self.assertTrue(primary.isEnabled())

        primary.click()
        for _ in range(5):
            QApplication.processEvents()
        queue = dialog.findChild(QListWidget, "farmingQueueList")
        summary = dialog.findChild(QLabel, "farmingSummaryLabel")
        self.assertEqual(queue.count(), 1)
        self.assertIn("1 queued", summary.text())
        self.assertEqual(queue.item(0).data(Qt.ItemDataRole.UserRole), "farm_step_00000001")
        dialog.deleteLater()

    def test_farming_preset_row_applies_plans_without_queuing(self) -> None:
        from ankiscape.logic.farming_logic import save_farm_preset_pure, set_farm_plan_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 99
        planned, ok, _ = set_farm_plan_pure(
            player_data,
            "falador_allotment_north",
            "potato",
            watering_intent=False,
            cure_intent=True,
        )
        self.assertTrue(ok)
        saved, ok, _ = save_farm_preset_pure(
            planned, "Morning run", ("falador_allotment_north",)
        )
        self.assertTrue(ok)
        preset_id = saved["farm_selected_preset"]
        changed, ok, _ = set_farm_plan_pure(
            saved, "falador_allotment_north", "onion"
        )
        self.assertTrue(ok)
        player_data.clear()
        player_data.update(changed)

        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        for _ in range(5):
            QApplication.processEvents()

        preset = dialog.findChild(QComboBox, "farmingPresetCombo")
        modified = dialog.findChild(QLabel, "farmingPresetModifiedLabel")
        apply_button = dialog.findChild(QPushButton, "farmingPresetApplyButton")
        manage = dialog.findChild(QToolButton, "farmingPresetManageButton")
        self.assertEqual(preset.currentData(), preset_id)
        self.assertEqual(modified.text(), "modified")
        self.assertTrue(apply_button.isEnabled())
        self.assertIsNotNone(manage.menu())
        self.assertEqual(player_data["farm_queue"], [])

        apply_button.click()
        for _ in range(5):
            QApplication.processEvents()

        self.assertEqual(
            player_data["farm_plans"]["falador_allotment_north"]["crop_id"],
            "potato",
        )
        self.assertEqual(player_data["farm_queue"], [])
        self.assertEqual(
            dialog.findChild(QLabel, "farmingPresetModifiedLabel").text(),
            "",
        )
        dialog.deleteLater()

    def test_farming_patch_actions_keep_readable_widths_at_supported_dialog_sizes(self) -> None:
        from ankiscape.logic.farming_logic import set_farm_plan_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {
            "Rake": 1,
            "Seed dibber": 1,
            "Spade": 1,
            "Potato seed": 3,
            "Compost": 2,
        }
        updated, ok, _ = set_farm_plan_pure(player_data, "falador_allotment_north", "potato")
        self.assertTrue(ok)
        player_data.clear()
        player_data.update(updated)
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        for width, height in ((720, 540), (900, 560)):
            dialog.resize(width, height)
            for _ in range(5):
                QApplication.processEvents()
            self.assertEqual((dialog.width(), dialog.height()), (width, height))
            location = dialog.findChild(QToolButton, "farmingLocationToggle::falador")
            if not location.isChecked():
                location.click()
                QApplication.processEvents()
            expand = dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north")
            if not expand.isChecked():
                expand.click()
                QApplication.processEvents()
            buttons = [
                dialog.findChild(QPushButton, "farmingPatchPlanButton::falador_allotment_north"),
                dialog.findChild(QPushButton, "farmingPatchPrimaryAction::falador_allotment_north"),
                dialog.findChild(QPushButton, "farmingPatchHarvestReplantButton::falador_allotment_north"),
            ]
            for button in buttons:
                self.assertIsNotNone(button)
                self.assertGreaterEqual(button.width(), button.sizeHint().width())
        dialog.deleteLater()

    def test_farming_queue_selection_reorder_remove_clear_and_full_run(self) -> None:
        from ankiscape.logic.farming_logic import set_farm_plan_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 6}
        for patch_id in ("falador_allotment_north", "falador_allotment_south"):
            updated, ok, _ = set_farm_plan_pure(player_data, patch_id, "potato")
            self.assertTrue(ok)
            player_data.clear()
            player_data.update(updated)
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        full_run = dialog.findChild(QPushButton, "farmingQueueFullRunButton")
        self.assertTrue(full_run.isEnabled())
        full_run.click()
        for _ in range(5):
            QApplication.processEvents()
        queue = dialog.findChild(QListWidget, "farmingQueueList")
        self.assertEqual(queue.count(), 2)
        first_id = queue.item(0).data(Qt.ItemDataRole.UserRole)
        second_id = queue.item(1).data(Qt.ItemDataRole.UserRole)
        queue.setCurrentRow(1)
        QApplication.processEvents()
        up = dialog.findChild(QPushButton, "farmingQueueMoveUpButton")
        self.assertTrue(up.isEnabled())
        up.click()
        for _ in range(4):
            QApplication.processEvents()
        queue = dialog.findChild(QListWidget, "farmingQueueList")
        self.assertEqual(queue.item(0).data(Qt.ItemDataRole.UserRole), second_id)
        self.assertEqual(queue.item(1).data(Qt.ItemDataRole.UserRole), first_id)

        queue.setCurrentRow(0)
        QApplication.processEvents()
        dialog.findChild(QPushButton, "farmingQueueRemoveButton").click()
        for _ in range(4):
            QApplication.processEvents()
        queue = dialog.findChild(QListWidget, "farmingQueueList")
        self.assertEqual(queue.count(), 1)
        self.assertEqual(queue.item(0).data(Qt.ItemDataRole.UserRole), first_id)
        dialog.findChild(QPushButton, "farmingQueueClearButton").click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(dialog.findChild(QListWidget, "farmingQueueList").count(), 0)
        self.assertEqual(player_data["farm_queue"], [])
        dialog.deleteLater()
