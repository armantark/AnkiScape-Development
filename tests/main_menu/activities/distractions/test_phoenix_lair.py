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
    from tests.test_main_menu_widget import QApplication, QLabel, QMessageBox, QProgressBar, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_phoenix_lair_card_is_compact_period_art_and_abandonment_is_confirmed(self) -> None:
        from ankiscape.logic.phoenix_lair_logic import default_phoenix_lair_state_pure

        pd = _make_player_data()
        pd["phoenix_lair"] = default_phoenix_lair_state_pure()
        pd["activity_session"] = {"active_id": ""}
        pd["combat_encounter"] = {}
        pd["quests"]["in_pyre_need"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["slayer_level"] = 99
        pd["inventory"].update({"Knife": 1, "Secateurs": 1, "Tinderbox": 1})
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "phoenix_lair")
        self.assertFalse(row.icon(0).isNull())
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "phoenixLairPanel")
        icon = panel.findChild(QLabel, "phoenixLairIcon")
        status = _find_named_label(dialog, "phoenixLairStatusChip")
        summary = _find_named_label(dialog, "phoenixLairSummary")
        mechanics = _find_named_label(dialog, "phoenixLairMechanics")
        primary = _find_named_button(dialog, "phoenixLairPrimaryButton")
        leave = _find_named_button(dialog, "phoenixLairLeaveButton")
        progress = panel.findChild(QProgressBar, "phoenixLairProgress")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertIsNotNone(icon.pixmap())
        self.assertFalse(icon.pixmap().isNull())
        self.assertEqual(icon.width(), 28)
        self.assertEqual(status.text(), "READY")
        self.assertIn("non-resumable dangerous PvM", summary.text())
        self.assertIn("Phoenix egg: 1 in 1,000 per completion", summary.text())
        self.assertNotIn("abstraction", summary.text())
        self.assertIn("compressed", mechanics.text())
        self.assertTrue(leave.isHidden())

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._phoenix_lair_calls[-1], ("enter", {}))
        self.assertTrue(pd["phoenix_lair"]["active"])
        self.assertEqual(pd["current_utility"], "phoenix_lair")
        self.assertEqual(status.text(), "GUARDIAN FRONT")
        self.assertTrue(progress.isVisible() or not dialog.isVisible())
        self.assertIn("next attack:", summary.text())
        self.assertFalse(leave.isHidden())

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertTrue(pd["phoenix_lair"]["active"])
        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(self._phoenix_lair_calls[-1], ("leave", {}))
        self.assertFalse(pd["phoenix_lair"]["active"])
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

    def test_phoenix_lair_advanced_mode_opens_with_belt_tools_missing_from_the_pack(self) -> None:
        from ankiscape.logic.phoenix_lair_logic import default_phoenix_lair_state_pure

        pd = _make_player_data()
        pd["phoenix_lair"] = default_phoenix_lair_state_pure()
        pd["activity_session"] = {"active_id": ""}
        pd["combat_encounter"] = {}
        pd["quests"]["in_pyre_need"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["slayer_level"] = 99
        pd["inventory"].update({"Knife": 1, "Secateurs": 1, "Tinderbox": 1})
        pd["carried_advanced_targets"] = {"phoenix_lair": True}
        pd["carried_layout"] = {
            "phoenix_lair": {
                "Knife": 1,
                "Secateurs": 1,
            }
        }
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "phoenix_lair")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        status = _find_named_label(dialog, "phoenixLairStatusChip")
        summary = _find_named_label(dialog, "phoenixLairSummary")
        primary = _find_named_button(dialog, "phoenixLairPrimaryButton")
        # The tinderbox is a 2012 tool belt tool, so the pack without it still enters.
        self.assertEqual(status.text(), "READY")
        self.assertNotIn("Tinderbox", summary.text())
        self.assertTrue(primary.isEnabled())
