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
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QPushButton, QScrollArea, QSpinBox
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_vinesweeper_card_enters_buys_real_rewards_and_redeems_xp(self) -> None:
        from ankiscape.logic.vinesweeper_logic import default_vinesweeper_state_pure

        pd = _make_player_data()
        pd["inventory"]["Spade"] = 1
        pd["farming_level"] = 40
        farming_exp_before = float(pd["farming_exp"])
        pd["vinesweeper"] = default_vinesweeper_state_pure()
        pd["vinesweeper"]["points"] = 200
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        vinesweeper_row = _utility_row(activity_tree, "vinesweeper")
        activity_tree.setCurrentItem(vinesweeper_row)
        activity_tree.itemActivated.emit(vinesweeper_row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "vinesweeperPanel")
        status = _find_named_label(dialog, "vinesweeperStatusChip")
        primary = _find_named_button(dialog, "vinesweeperPrimaryButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._vinesweeper_calls[-1], ("enter", {}))
        self.assertEqual(pd["current_utility"], "vinesweeper")
        self.assertEqual(self._activity_start_calls[-1], "vinesweeper")
        self.assertEqual(pd["vinesweeper"]["flags"], 10)
        self.assertEqual(status.text(), "ACTIVE")
        self.assertEqual(primary.accessibleName(), "Leave Winkin's Farm")

        reward_page = _open_reward_target(dialog, "vinesweeper")
        reward = reward_page.findChild(QComboBox, "vinesweeperRewardCombo")
        quantity = reward_page.findChild(QSpinBox, "vinesweeperRewardQuantity")
        buy = reward_page.findChild(QPushButton, "vinesweeperBuyRewardButton")
        redeem = reward_page.findChild(QPushButton, "vinesweeperRedeemXpButton")
        self.assertTrue(redeem.isVisibleTo(dialog))
        self.assertEqual(reward.count(), 46)
        self.assertEqual(reward.accessibleName(), "Vinesweeper reward")
        self.assertEqual(quantity.accessibleName(), "Reward quantity")

        pd["vinesweeper"]["flags"] = 7
        flag_index = reward.findData("flag")
        reward.setCurrentIndex(flag_index)
        quantity.setValue(10)
        QApplication.processEvents()
        self.assertTrue(buy.isEnabled())
        self.assertEqual(buy.text(), "Buy · 150 pt")
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["vinesweeper"]["flags"], 10)
        self.assertEqual(pd["vinesweeper"]["points"], 50)

        cabbage_index = reward.findData("cabbage_seed")
        reward.setCurrentIndex(cabbage_index)
        quantity.setValue(2)
        QApplication.processEvents()
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Cabbage seed"], 2)
        self.assertEqual(pd["vinesweeper"]["points"], 30)

        redeem.click()
        QApplication.processEvents()
        self.assertEqual(pd["vinesweeper"]["points"], 0)
        self.assertEqual(pd["farming_exp"], farming_exp_before + 30.0)
        self.assertFalse(redeem.isEnabled())
