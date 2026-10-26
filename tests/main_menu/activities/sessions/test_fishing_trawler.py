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
    from tests.test_main_menu_widget import QApplication, QComboBox, QMessageBox, QProgressBar, QScrollArea, QSpinBox
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_fishing_trawler_card_saves_plan_boards_and_returns_supplies_on_leave(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "fishing_level": 81,
                "inventory": {
                    **pd["inventory"],
                    "Swamp paste": 60,
                    "Rope": 4,
                    "Bailing bucket": 1,
                },
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "fishing_trawler")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "fishingTrawlerPanel")
        summary = _find_named_label(dialog, "fishingTrawlerSummary")
        status = _find_named_label(dialog, "fishingTrawlerStatusChip")
        mode = panel.findChild(QComboBox, "fishingTrawlerModeCombo")
        priority = panel.findChild(QComboBox, "fishingTrawlerPriorityCombo")
        paste = panel.findChild(QSpinBox, "fishingTrawlerPasteSpin")
        rope = panel.findChild(QSpinBox, "fishingTrawlerRopeSpin")
        bucket = panel.findChild(QSpinBox, "fishingTrawlerBucketsSpin")
        save = _find_named_button(dialog, "fishingTrawlerSavePlanButton")
        primary = _find_named_button(dialog, "fishingTrawlerPrimaryButton")
        leave = _find_named_button(dialog, "fishingTrawlerLeaveButton")
        water = panel.findChild(QProgressBar, "fishingTrawlerWater")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "DOCKED · 0 landed · 0 sunk")
        self.assertIn("Ten useful duties", summary.text())
        self.assertTrue(water.isHidden())

        mode.setCurrentIndex(mode.findData("advanced"))
        priority.setCurrentIndex(priority.findData("catch_first"))
        paste.setValue(20)
        rope.setValue(2)
        bucket.setValue(1)
        save.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fishing_trawler_calls[-1],
            (
                "set_fishing_trawler_policy",
                {
                    "automation_mode": "advanced",
                    "priority": "catch_first",
                    "layout": {
                        "Swamp paste": 20,
                        "Rope": 2,
                        "Bailing bucket": 1,
                    },
                },
            ),
        )

        # Boarding atomically persists the visible plan, even when the user
        # changed it after the last explicit Save.
        paste.setValue(30)

        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fishing_trawler_calls[-1],
            (
                "enter_fishing_trawler",
                {
                    "automation_mode": "advanced",
                    "priority": "catch_first",
                    "layout": {
                        "Swamp paste": 30,
                        "Rope": 2,
                        "Bailing bucket": 1,
                    },
                },
            ),
        )
        self.assertEqual(pd["current_utility"], "fishing_trawler")
        self.assertEqual(primary.text(), "Active for reviews")
        self.assertIn("AT SEA", status.text())
        self.assertFalse(water.isHidden())
        self.assertFalse(mode.isEnabled())
        self.assertFalse(save.isEnabled())
        self.assertEqual(pd["inventory"]["Swamp paste"], 30)

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(
            self._fishing_trawler_calls[-1],
            ("leave_fishing_trawler", {}),
        )
        self.assertTrue(leave.isHidden())
        self.assertEqual(pd["inventory"]["Swamp paste"], 60)
        self.assertIn("haul forfeited", summary.text())

    def test_fishing_trawler_level_gate_is_visible_without_hover(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_utility": "bankstanding",
                "activity_session": {"active_id": ""},
                "fishing_level": 14,
            }
        )
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "fishing_trawler")
        self.assertFalse(row.isDisabled())
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()
        status = _find_named_label(dialog, "fishingTrawlerStatusChip")
        summary = _find_named_label(dialog, "fishingTrawlerSummary")
        primary = _find_named_button(dialog, "fishingTrawlerPrimaryButton")
        self.assertEqual(status.text(), "LOCKED · 0 landed · 0 sunk")
        self.assertIn("Requires level 15 Fishing", summary.text())
        self.assertFalse(primary.isEnabled())
