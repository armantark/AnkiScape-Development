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
    from tests.test_main_menu_widget import QApplication, QComboBox, QLineEdit, QMessageBox, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_werewolf_skullball_card_configures_enters_and_leaves_without_nested_scroll(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 25,
                "equipment": {"ring": "Ring of Charos"},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        pd["quests"]["creature_of_fenkenstrain"] = {
            "started": True,
            "completed": True,
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "werewolf_skullball")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "werewolfSkullballPanel")
        status = _find_named_label(dialog, "werewolfSkullballStatusChip")
        summary = _find_named_label(dialog, "werewolfSkullballSummary")
        primary = _find_named_button(dialog, "werewolfSkullballPrimaryButton")
        leave = _find_named_button(dialog, "werewolfSkullballLeaveButton")
        mode = panel.findChild(QComboBox, "werewolfSkullballModeCombo")
        route = panel.findChild(QComboBox, "werewolfSkullballRouteCombo")
        plan = panel.findChild(QLineEdit, "werewolfSkullballPlanEdit")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("10 goals", summary.text())
        self.assertTrue(plan.isHidden())
        self.assertTrue(leave.isHidden())

        route.setCurrentIndex(route.findData("fast"))
        QApplication.processEvents()
        self.assertEqual(pd["werewolf_skullball_policy"]["route"], "fast")
        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertFalse(plan.isHidden())
        with patch.object(self._ui, "show_error_message"):
            plan.setText("T X S")
            plan.editingFinished.emit()
            QApplication.processEvents()
        self.assertEqual(plan.text(), "T X S")
        self.assertEqual(mode.currentData(), "advanced")
        plan.setText(" ".join(("T",) * 31))
        plan.editingFinished.emit()
        QApplication.processEvents()
        self.assertIn("742 Agility XP", summary.text())
        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            [call[0] for call in self._agility_command_calls[-2:]],
            ["set_werewolf_skullball_policy", "enter_werewolf_skullball"],
        )
        self.assertEqual(pd["current_utility"], "werewolf_skullball")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertEqual(primary.text(), "Active for reviews")
        self.assertFalse(leave.isHidden())
        self.assertFalse(mode.isEnabled())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_werewolf_skullball", {}),
        )
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

    def test_werewolf_skullball_failed_entry_preserves_current_selection(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 25,
                "equipment": {"ring": "Ring of Charos"},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        pd["quests"]["creature_of_fenkenstrain"] = {
            "started": True,
            "completed": True,
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "werewolf_skullball")
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        primary = _find_named_button(dialog, "werewolfSkullballPrimaryButton")
        pd["equipment"] = {}
        with patch.object(self._ui, "show_error_message"):
            primary.click()
            QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd.get("werewolf_skullball", {}), {})

    def test_locked_werewolf_skullball_row_opens_requirement_card_in_real_qt(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 1,
                "equipment": {},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "werewolf_skullball")
        self.assertFalse(row.isDisabled())
        activity_tree.setCurrentItem(row)
        activity_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()

        status = _find_named_label(dialog, "werewolfSkullballStatusChip")
        summary = _find_named_label(dialog, "werewolfSkullballSummary")
        primary = _find_named_button(dialog, "werewolfSkullballPrimaryButton")
        self.assertEqual(status.text(), "LOCKED")
        self.assertIn("Agility level 25", summary.text())
        self.assertIn("Creature of Fenkenstrain", summary.text())
        self.assertIn("equip a Ring of Charos", summary.text())
        self.assertFalse(primary.isEnabled())
        self.assertEqual(pd["current_utility"], "bankstanding")

    def test_switching_from_werewolf_skullball_requires_and_honours_leave_confirmation(self) -> None:
        from ankiscape.logic.werewolf_skullball_logic import enter_werewolf_skullball_pure

        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 25,
                "equipment": {"ring": "Ring of Charos"},
                "activity_session": {"active_id": ""},
            }
        )
        pd["quests"]["creature_of_fenkenstrain"] = {
            "started": True,
            "completed": True,
        }
        pd, ok, _info = enter_werewolf_skullball_pure(pd)
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
        self.assertEqual(pd["current_utility"], "werewolf_skullball")
        self.assertTrue(pd["werewolf_skullball"])

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_werewolf_skullball", {}),
        )
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd["werewolf_skullball"], {})
