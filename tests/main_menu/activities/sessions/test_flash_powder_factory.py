from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _open_reward_target,
    _utility_row,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QMessageBox, QPushButton, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_flash_powder_factory_card_enters_configures_rewards_and_cashes_out_without_nested_scroll(self) -> None:
        from ankiscape.logic.agility_logic import default_agility_state_pure

        pd = _make_player_data()
        pd.update(default_agility_state_pure())
        pd.update(
            {
                "agility_level": 99,
                "thieving_level": 99,
                "herblore_level": 99,
                "current_utility": "flash_powder_factory",
                "activity_session": {"active_id": ""},
                "summoning_state": {"active_follower": {}},
            }
        )
        pd["agility_activity_currencies"]["brianpoints"] = 5_000
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "flash_powder_factory")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "flashPowderFactoryPanel")
        status = _find_named_label(dialog, "flashPowderFactoryStatusChip")
        summary = _find_named_label(dialog, "flashPowderFactorySummary")
        primary = _find_named_button(dialog, "flashPowderFactoryPrimaryButton")
        leave = _find_named_button(dialog, "flashPowderFactoryLeaveButton")
        mode = panel.findChild(QComboBox, "flashPowderFactoryModeCombo")
        strategy = panel.findChild(QComboBox, "flashPowderFactoryStrategyCombo")
        apparatus = panel.findChild(QComboBox, "flashPowderFactoryApparatusCombo")
        reward_page = _open_reward_target(dialog, "flash_powder_factory")
        rewards = reward_page.findChild(QComboBox, "flashPowderFactoryRewardCombo")
        buy = reward_page.findChild(QPushButton, "flashPowderFactoryRewardButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("Eight circuits", summary.text())
        self.assertTrue(leave.isHidden())

        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("enter_flash_powder_factory", {}),
        )
        self.assertEqual(pd["current_utility"], "flash_powder_factory")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertEqual(primary.text(), "Active for reviews")
        self.assertFalse(leave.isHidden())

        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertFalse(apparatus.isHidden())
        strategy.setCurrentIndex(strategy.findData("rogue_equipment"))
        apparatus.setCurrentIndex(apparatus.findData("opportunistic"))
        QApplication.processEvents()
        self.assertEqual(
            pd["agility_flash_powder_factory_policy"]["strategy"],
            "rogue_equipment",
        )
        self.assertEqual(
            pd["agility_flash_powder_factory_policy"]["apparatus_policy"],
            "opportunistic",
        )

        rewards.setCurrentIndex(rewards.findData("Rogue kit"))
        QApplication.processEvents()
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Rogue kit"], 1)

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_flash_powder_factory", {}),
        )
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

    def test_switching_from_flash_powder_factory_requires_and_honours_cashout_confirmation(self) -> None:
        from ankiscape.logic.agility_logic import default_agility_state_pure
        from ankiscape.logic.flash_powder_factory_logic import enter_flash_powder_factory_pure

        pd = _make_player_data()
        pd.update(default_agility_state_pure())
        pd.update(
            {
                "agility_level": 99,
                "thieving_level": 99,
                "herblore_level": 99,
                "activity_session": {"active_id": ""},
                "summoning_state": {"active_follower": {}},
            }
        )
        pd, ok, _info = enter_flash_powder_factory_pure(pd)
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
        self.assertEqual(pd["current_utility"], "flash_powder_factory")
        self.assertIn(
            "flash_powder_factory",
            pd["agility_activity_state"],
        )

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(
            self._agility_command_calls[-1],
            ("leave_flash_powder_factory", {}),
        )
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertNotIn(
            "flash_powder_factory",
            pd["agility_activity_state"],
        )
