from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _utility_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_barrows_card_enters_selects_repairs_and_suspends_without_nested_scroll(self) -> None:
        from ankiscape.logic.barrows_logic import default_barrows_state_pure

        pd = _make_player_data()
        pd["barrows"] = default_barrows_state_pure()
        pd["activity_session"] = {"active_id": ""}
        pd["combat_encounter"] = {}
        pd["inventory"]["Coins"] = 500_000
        pd["inventory"]["Verac's flail 50"] = 1
        pd["equipment_instances"] = {
            "equipment-7": {
                "family_id": "barrows_verac",
                "item_name": "Verac's flail 50",
                "condition": 45_000,
                "location": "bank",
            }
        }
        pd["equipment_instance_next_id"] = 8
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "barrows")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "barrowsPanel")
        status = _find_named_label(dialog, "barrowsStatusChip")
        summary = _find_named_label(dialog, "barrowsSummary")
        primary = _find_named_button(dialog, "barrowsPrimaryButton")
        leave = _find_named_button(dialog, "barrowsLeaveButton")
        mode = panel.findChild(QComboBox, "barrowsModeCombo")
        brother = panel.findChild(QComboBox, "barrowsBrotherCombo")
        repair = panel.findChild(QComboBox, "barrowsRepairCombo")
        repair_button = _find_named_button(dialog, "barrowsRepairButton")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("dangerous death", summary.text())
        self.assertTrue(leave.isHidden())
        self.assertEqual(repair.count(), 1)

        repair_button.click()
        QApplication.processEvents()
        self.assertEqual(self._barrows_calls[-1][0], "repair")
        self.assertEqual(pd["inventory"]["Verac's flail"], 1)

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._barrows_calls[-1], ("enter", {}))
        self.assertEqual(pd["current_utility"], "barrows")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertFalse(leave.isHidden())

        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertEqual(
            self._barrows_calls[-1],
            ("set_mode", {"automation_mode": "advanced"}),
        )
        self.assertFalse(brother.isHidden())
        self.assertGreater(brother.count(), 1)
        brother.setCurrentIndex(1)
        QApplication.processEvents()
        self.assertEqual(self._barrows_calls[-1][0], "select_brother")

        pd["barrows"].update(
            {
                "phase": "tunnels",
                "surface_queue": [],
                "selected_brother": "",
                "start_room": 0,
                "current_room": 0,
                "usable_edges": [
                    "0-1",
                    "0-3",
                    "1-2",
                    "2-5",
                    "3-4",
                    "5-8",
                    "6-7",
                    "7-8",
                ],
                "revealed_rooms": [0, 1, 3, 4],
            }
        )
        mode.setCurrentIndex(mode.findData("casual"))
        QApplication.processEvents()
        room_buttons = [
            _find_named_button(dialog, f"barrowsRoom{room}Button")
            for room in range(9)
        ]
        self.assertTrue(all(not button.isHidden() for button in room_buttons))
        self.assertTrue(any(button.text() == "?" for button in room_buttons))

        leave.click()
        QApplication.processEvents()
        self.assertEqual(self._barrows_calls[-1], ("leave", {}))
        self.assertEqual(status.text(), "SUSPENDED")
        self.assertTrue(pd["barrows"]["suspended"])
