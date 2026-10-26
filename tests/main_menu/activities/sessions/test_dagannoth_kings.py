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
    from tests.test_main_menu_widget import QApplication, QComboBox, QListWidget, QMessageBox, QScrollArea, QSize
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_dagannoth_kings_card_uses_period_icons_and_persistent_room_controls(self) -> None:
        from ankiscape.logic.dagannoth_kings_logic import (
            default_dagannoth_kings_state_pure,
        )

        pd = _make_player_data()
        pd["dagannoth_kings"] = default_dagannoth_kings_state_pure()
        pd["activity_session"] = {"active_id": ""}
        pd["combat_encounter"] = {}
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "dagannoth_kings")
        self.assertFalse(row.icon(0).isNull())
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "dagannothKingsPanel")
        status = _find_named_label(dialog, "dagannothKingsStatusChip")
        summary = _find_named_label(dialog, "dagannothKingsSummary")
        warning = _find_named_label(dialog, "dagannothKingsDangerWarning")
        primary = _find_named_button(dialog, "dagannothKingsPrimaryButton")
        leave = _find_named_button(dialog, "dagannothKingsLeaveButton")
        roster = panel.findChild(QListWidget, "dagannothKingsRoster")
        mode = panel.findChild(QComboBox, "dagannothKingsModeCombo")
        target = panel.findChild(QComboBox, "dagannothKingsTargetCombo")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("font-weight: 700", status.styleSheet())
        self.assertTrue(leave.isHidden())
        self.assertIn("roster pressure", summary.text().lower())
        self.assertIn("dangerous death", warning.text().lower())
        self.assertIn("font-weight: 700", warning.styleSheet())
        self.assertEqual(roster.iconSize(), QSize(28, 28))
        self.assertEqual(target.iconSize(), QSize(28, 28))
        self.assertEqual(
            target.toolTip(), "Switch to Advanced mode to choose a target."
        )

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._dagannoth_kings_calls[-1], ("enter", {}))
        self.assertTrue(pd["dagannoth_kings"]["active"])
        self.assertEqual(pd["current_utility"], "dagannoth_kings")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertEqual(roster.count(), 3)
        self.assertEqual(
            [roster.item(index).text().split(" ·", 1)[0].lstrip("▶ ") for index in range(3)],
            ["Dagannoth Prime", "Dagannoth Supreme", "Dagannoth Rex"],
        )
        self.assertTrue(
            all(not roster.item(index).icon().isNull() for index in range(3))
        )

        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertEqual(
            self._dagannoth_kings_calls[-1],
            ("set_mode", {"automation_mode": "advanced"}),
        )
        self.assertTrue(target.isEnabled())
        self.assertEqual(target.toolTip(), "Choose which living king to engage.")
        target.setCurrentIndex(target.findData("dagannoth_rex"))
        QApplication.processEvents()
        self.assertEqual(
            self._dagannoth_kings_calls[-1],
            ("select_target", {"enemy_id": "dagannoth_rex"}),
        )
        self.assertEqual(pd["dagannoth_kings"]["engaged_enemy_id"], "dagannoth_rex")

        dialog.show()
        dialog.resize(900, 560)
        for _ in range(8):
            QApplication.processEvents()
        choose_another = _find_named_button(dialog, "activityChooseAnotherButton")
        primary_bottom = primary.mapTo(dialog, primary.rect().bottomLeft()).y()
        choose_another_top = choose_another.mapTo(
            dialog, choose_another.rect().topLeft()
        ).y()
        self.assertLess(primary_bottom, choose_another_top)

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(self._dagannoth_kings_calls[-1], ("leave", {}))
        self.assertFalse(pd["dagannoth_kings"]["active"])
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())
