from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _FakeCol,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _open_reward_target,
    _utility_row,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QMessageBox, QProgressBar, QPushButton, QScrollArea, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_fish_flingers_card_enters_shops_and_leaves_without_nested_scroll(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "shop_market_clock": {"answered_cards": 0, "market_tick": 0},
                "fish_flingers_tokens": 140,
                "fish_flingers_medals": 0,
                "fish_flingers_last_ticket_day": -1,
            }
        )
        dialog = self._open(pd)
        dialog.show()
        dialog.resize(720, 560)
        for _ in range(3):
            QApplication.processEvents()
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "fish_flingers")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "bankstanding")

        panel = _find_named_widget(dialog, "fishFlingersPanel")
        summary = _find_named_label(dialog, "fishFlingersSummary")
        currency = _find_named_label(dialog, "fishFlingersCurrencyChip")
        primary = _find_named_button(dialog, "fishFlingersPrimaryButton")
        leave = _find_named_button(dialog, "fishFlingersLeaveButton")
        progress = panel.findChild(QProgressBar, "fishFlingersProgress")
        reward_page = _open_reward_target(dialog, "fish_flingers")
        reward = reward_page.findChild(QComboBox, "fishFlingersRewardCombo")
        buy = reward_page.findChild(QPushButton, "fishFlingersBuyButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertIn("READY · 2 tickets", currency.text())
        self.assertIn("8 catches over 167 cards", summary.text())
        self.assertEqual(primary.text(), "Start activity")
        self.assertTrue(progress.isHidden())
        self.assertEqual(reward.currentData(), "fishing_hat")
        self.assertEqual(
            reward.sizeAdjustPolicy(),
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon,
        )
        self.assertTrue(buy.isEnabled())
        basic_index = reward.findData("basic_tackle_box")
        self.assertIn("upgrade Beginner's tackle box", reward.itemText(basic_index))

        buy.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fish_flingers_calls[-1],
            ("buy_fish_flingers_reward", {"reward_id": "fishing_hat"}),
        )
        self.assertEqual(pd["inventory"]["Fishing hat"], 1)
        self.assertIn("0 tokens", currency.text())
        self.assertIn("Requires 140 Fishing tokens", buy.toolTip())

        primary.click()
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(
            self._fish_flingers_calls[-1],
            ("enter_fish_flingers", {}),
        )
        self.assertEqual(self._activity_start_calls[-1], "fish_flingers")
        self.assertTrue(
            any(
                label.text() == "Training: Activities"
                for label in dialog.findChildren(QLabel)
            )
        )
        self.assertEqual(pd["current_utility"], "fish_flingers")
        self.assertEqual(primary.text(), "Active for reviews")
        self.assertIn("ACTIVE", currency.text())
        self.assertIn("Bass at Lake", summary.text())
        self.assertIn("stock 24/24 (100%, Rich)", summary.text())
        self.assertIn("rotation 1/6", summary.text())
        self.assertIn("communal pressure 3 stock lost per catch", summary.text())
        self.assertIn("palette(text)", summary.styleSheet())
        self.assertGreaterEqual(summary.height(), summary.sizeHint().height())
        self.assertLessEqual(panel.width(), dialog.width())
        self.assertEqual(progress.format(), "%v of 8 landed")
        self.assertFalse(progress.isHidden())
        self.assertFalse(leave.isHidden())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fish_flingers_calls[-1],
            ("leave_fish_flingers", {}),
        )
        self.assertTrue(leave.isHidden())
        self.assertIn("forfeited", summary.text())

    def test_fish_flingers_names_its_length_in_cards_at_the_game_speed(self) -> None:
        # The ten-minute event is 1,000 ticks; a card at speed 10 spends 60.
        from ankiscape.ui import ui

        class _FakeMw(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.col = _FakeCol()
                self.col.set_config("ankiscape_review_action_multiplier", 10)

        with patch.object(ui, "mw", _FakeMw()):
            pd = _make_player_data()
            pd.update({"activity_session": {"active_id": ""}, "fish_flingers_last_ticket_day": -1})
            dialog = self._open(pd)
            dialog.show()
            activity_tree = self._open_activities(dialog)
            row = _utility_row(activity_tree, "fish_flingers")
            activity_tree.setCurrentItem(row)
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()
            summary = _find_named_label(dialog, "fishFlingersSummary")
            self.assertIn("8 catches over 17 cards", summary.text())
