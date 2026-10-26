from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _utility_row,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QMessageBox, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_pyramid_plunder_card_configures_enters_and_leaves_without_nested_scroll(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "thieving_level": 91,
                "strength_level": 99,
                "runecrafting_level": 99,
                "current_utility": "pyramid_plunder",
                "activity_session": {"active_id": ""},
                "carried_inventory": {},
                "carried_layout": {},
                "carried_advanced_targets": {},
                "pyramid_plunder": {},
                "pyramid_plunder_priority": "max_xp",
                "pyramid_plunder_runs_completed": 0,
                "pyramid_plunder_last_result": "Ready to enter",
            }
        )
        pd["quests"]["icthlarins_little_helper"] = {
            "started": True,
            "completed": False,
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "pyramid_plunder")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "pyramidPlunderPanel")
        status = _find_named_label(dialog, "pyramidPlunderStatusChip")
        summary = _find_named_label(dialog, "pyramidPlunderSummary")
        primary = _find_named_button(dialog, "pyramidPlunderPrimaryButton")
        leave = _find_named_button(dialog, "pyramidPlunderLeaveButton")
        priority = panel.findChild(QComboBox, "pyramidPlunderPriorityCombo")
        priority_label = _find_named_label(
            dialog,
            "pyramidPlunderPriorityLabel",
        )
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("Rooms 1–8", summary.text())
        self.assertEqual(priority_label.text(), "Priority")
        self.assertTrue(leave.isHidden())

        priority.setCurrentIndex(priority.findData("treasure"))
        QApplication.processEvents()
        self.assertEqual(pd["pyramid_plunder_priority"], "treasure")
        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("enter_pyramid_plunder", {}),
        )
        self.assertEqual(pd["current_utility"], "pyramid_plunder")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertEqual(primary.text(), "Active for reviews")
        self.assertFalse(leave.isHidden())
        self.assertFalse(priority.isEnabled())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_pyramid_plunder", {}),
        )
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

    def test_pyramid_plunder_failed_entry_preserves_current_selection(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "thieving_level": 91,
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "carried_inventory": {},
                "carried_layout": {},
                "carried_advanced_targets": {},
            }
        )
        pd["quests"]["icthlarins_little_helper"] = {
            "started": True,
            "completed": False,
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "pyramid_plunder")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        primary = _find_named_button(dialog, "pyramidPlunderPrimaryButton")
        pd["quests"]["icthlarins_little_helper"] = {
            "started": False,
            "completed": False,
        }
        with patch.object(self._ui, "show_error_message"):
            primary.click()
            QApplication.processEvents()

        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd.get("pyramid_plunder", {}), {})

    def test_switching_from_pyramid_plunder_requires_and_honours_bank_confirmation(self) -> None:
        from ankiscape.logic.pyramid_plunder_logic import enter_pyramid_plunder_pure

        pd = _make_player_data()
        pd.update(
            {
                "thieving_level": 91,
                "activity_session": {"active_id": ""},
                "carried_inventory": {},
                "carried_layout": {},
                "carried_advanced_targets": {},
            }
        )
        pd["quests"]["icthlarins_little_helper"] = {
            "started": True,
            "completed": False,
        }
        pd, ok, _info = enter_pyramid_plunder_pure(pd)
        self.assertTrue(ok)
        dialog = self._open(pd)
        utility_tree = self._open_utility(dialog)
        bankstanding = _utility_row(utility_tree, "bankstanding")

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "pyramid_plunder")
        self.assertTrue(pd["pyramid_plunder"])

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_pyramid_plunder", {}),
        )
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd["pyramid_plunder"], {})
