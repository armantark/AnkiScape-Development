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
    from tests.test_main_menu_widget import QApplication, QComboBox, QListWidget, QMessageBox, QScrollArea, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_fight_caves_card_enters_targets_and_leaves_without_nested_scroll(self) -> None:
        from ankiscape.logic.fight_caves_logic import default_fight_caves_state_pure

        pd = _make_player_data()
        pd["fight_caves"] = default_fight_caves_state_pure()
        pd["activity_session"] = {"active_id": ""}
        pd["combat_encounter"] = {}
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "fight_caves")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "fightCavesPanel")
        status = _find_named_label(dialog, "fightCavesStatusChip")
        summary = _find_named_label(dialog, "fightCavesSummary")
        telegraph = _find_named_label(dialog, "fightCavesJadTelegraph")
        primary = _find_named_button(dialog, "fightCavesPrimaryButton")
        leave = _find_named_button(dialog, "fightCavesLeaveButton")
        roster = panel.findChild(QListWidget, "fightCavesRoster")
        mode = panel.findChild(QComboBox, "fightCavesModeCombo")
        target = panel.findChild(QComboBox, "fightCavesTargetCombo")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertTrue(telegraph.isHidden())
        self.assertTrue(leave.isHidden())
        self.assertEqual(roster.accessibleName(), "Fight Cave wave roster")
        self.assertEqual(roster.focusPolicy(), Qt.FocusPolicy.TabFocus)

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._fight_caves_calls[-1], ("enter", {}))
        self.assertTrue(pd["fight_caves"]["active"])
        self.assertEqual(pd["current_utility"], "fight_caves")
        self.assertEqual(self._activity_start_calls[-1], "fight_caves")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertIn("Wave 1/63", summary.text())
        self.assertEqual(roster.count(), 1)
        self.assertIn("Tz-Kih", roster.item(0).text())
        self.assertFalse(leave.isHidden())
        self.assertEqual(leave.text(), "Leave · claim 0 TokKul")

        advanced_index = mode.findData("advanced")
        mode.setCurrentIndex(advanced_index)
        QApplication.processEvents()
        self.assertEqual(
            self._fight_caves_calls[-1],
            ("set_mode", {"automation_mode": "advanced"}),
        )
        self.assertTrue(target.isEnabled())
        self.assertEqual(target.count(), 1)
        self.assertEqual(target.accessibleName(), "Fight Cave engaged target")

        pd["fight_caves"]["wave"] = 59
        pd["fight_caves"]["engaged_instance_id"] = ""
        pd["fight_caves"]["next_instance_id"] = 8
        pd["fight_caves"]["roster"] = []
        for index, enemy_id, lifepoints in (
            (1, "ket_zek", 1600),
            (2, "yt_mejkot", 800),
            (3, "tok_xil", 400),
            (4, "tz_kek_small", 100),
            (5, "tz_kek_small", 100),
            (6, "tz_kek_small", 100),
            (7, "tz_kek_small", 100),
        ):
            pd["fight_caves"]["roster"].append(
                {
                    "instance_id": f"fight-caves-{index}",
                    "enemy_id": enemy_id,
                    "lifepoints": lifepoints,
                    "encounter": {
                        "target_id": "fight_caves",
                        "enemy_lifepoints": lifepoints,
                    },
                    "heal_counter": 0,
                }
            )
        mode.setCurrentIndex(mode.findData("casual"))
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(6):
            QApplication.processEvents()
        self.assertEqual(roster.count(), 7)
        self.assertEqual(roster.verticalScrollBar().maximum(), 0)
        engaged_rows = [
            roster.item(index).text()
            for index in range(roster.count())
            if roster.item(index).text().startswith("▶")
        ]
        self.assertEqual(len(engaged_rows), 1)
        self.assertIn("Tok-Xil", engaged_rows[0])

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertTrue(pd["fight_caves"]["active"])
        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(self._fight_caves_calls[-1], ("leave", {}))
        self.assertFalse(pd["fight_caves"]["active"])
        self.assertEqual(status.text(), "READY")
        self.assertTrue(leave.isHidden())

        dialog.show()
        dialog.resize(900, 560)
        for _ in range(8):
            QApplication.processEvents()
        choose_another = _find_named_button(
            dialog, "activityChooseAnotherButton"
        )
        self.assertTrue(panel.isVisible())
        self.assertTrue(choose_another.isVisible())
        self.assertFalse(activity_tree.isVisible())
        choose_another.click()
        QApplication.processEvents()
        self.assertFalse(panel.isVisible())
        self.assertFalse(choose_another.isVisible())
        self.assertTrue(activity_tree.isVisible())
        tree_bottom = activity_tree.mapTo(
            dialog, activity_tree.rect().bottomRight()
        ).y()
        self.assertLessEqual(tree_bottom, dialog.contentsRect().bottom())
