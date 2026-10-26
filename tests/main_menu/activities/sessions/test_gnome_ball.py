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
    from tests.test_main_menu_widget import QApplication, QMessageBox, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_gnome_ball_card_enters_and_leaves_without_nested_scroll(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "equipment": {},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "gnome_ball")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "gnomeBallPanel")
        status = _find_named_label(dialog, "gnomeBallStatusChip")
        summary = _find_named_label(dialog, "gnomeBallSummary")
        primary = _find_named_button(dialog, "gnomeBallPrimaryButton")
        bank_reward = _find_named_button(dialog, "gnomeBallBankRewardButton")
        leave = _find_named_button(dialog, "gnomeBallLeaveButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("52 Agility + 52 Ranged XP", summary.text())
        self.assertIn("tackle risk", summary.text())
        ready_status_style = status.styleSheet()
        self.assertTrue(bank_reward.isHidden())
        self.assertTrue(leave.isHidden())

        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("enter_gnome_ball", {}),
        )
        self.assertEqual(pd["current_utility"], "gnome_ball")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertNotEqual(status.styleSheet(), ready_status_style)
        self.assertEqual(primary.text(), "Active for reviews")
        self.assertIn("Beat 1/3", summary.text())
        self.assertFalse(leave.isHidden())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_gnome_ball", {}),
        )
        self.assertEqual(status.text(), "READY")
        self.assertIn("Left Gnome Ball", summary.text())
        self.assertTrue(leave.isHidden())

    def test_gnome_ball_card_banks_the_carried_referee_reward(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "gnome_ball",
                "activity_session": {"active_id": ""},
                "gnome_ball": {},
                "gnome_ball_runs_completed": 1,
                "inventory": {"Gnomeball": 2},
                "carried_inventory": {"gnome_ball": {"Gnomeball": 1}},
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "gnome_ball")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        summary = _find_named_label(dialog, "gnomeBallSummary")
        bank_reward = _find_named_button(dialog, "gnomeBallBankRewardButton")
        self.assertIn("Gnomeball carried", summary.text())
        self.assertFalse(bank_reward.isHidden())

        bank_reward.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("bank_gnomeball_reward", {}),
        )
        self.assertEqual(pd["inventory"]["Gnomeball"], 2)
        self.assertNotIn(
            "Gnomeball",
            pd.get("carried_inventory", {}).get("gnome_ball", {}),
        )
        self.assertIn("another can be awarded", summary.text())
        self.assertTrue(bank_reward.isHidden())

    def test_locked_gnome_ball_row_opens_weapon_requirement_card(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "equipment": {"weapon": "Bronze sword"},
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "gnome_ball")
        self.assertFalse(row.isDisabled())
        activity_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()

        status = _find_named_label(dialog, "gnomeBallStatusChip")
        summary = _find_named_label(dialog, "gnomeBallSummary")
        primary = _find_named_button(dialog, "gnomeBallPrimaryButton")
        self.assertEqual(status.text(), "LOCKED")
        self.assertIn("only a Gnomeball is allowed", summary.text())
        self.assertFalse(primary.isEnabled())
        self.assertEqual(pd["current_utility"], "bankstanding")

    def test_switching_from_gnome_ball_requires_and_honours_leave_confirmation(self) -> None:
        from ankiscape.logic.gnome_ball_logic import enter_gnome_ball_pure

        pd = _make_player_data()
        pd.update({"equipment": {}, "activity_session": {"active_id": ""}})
        pd, ok, _info = enter_gnome_ball_pure(pd)
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
        self.assertEqual(pd["current_utility"], "gnome_ball")
        self.assertTrue(pd["gnome_ball"])

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_gnome_ball", {}),
        )
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(pd["gnome_ball"], {})
