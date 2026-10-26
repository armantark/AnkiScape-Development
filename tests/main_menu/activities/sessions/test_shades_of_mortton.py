from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_shades_of_mortton_detail_routes_plan_and_direct_actions(self) -> None:
        from ankiscape.logic.shades_of_mortton_logic import (
            apply_shades_of_mortton_command_pure,
            default_shades_of_mortton_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_shades_of_mortton_state_pure())
        pd.update(
            {
                "quests": {"shades_of_mortton": {"completed": True}},
                "firemaking_level": 80,
                "inventory": {
                    "Logs": 1,
                    "Sacred oil (4)": 1,
                    "Olive oil (4)": 1,
                    "Bronze key red": 1,
                    "Tinderbox": 1,
                },
            }
        )
        command_calls = []

        def mortton_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_shades_of_mortton_command_pure(
                pd,
                action_id,
                payload,
                rng=lambda: 0.0,
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_shades_of_mortton_command=mortton_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "shades_of_mortton"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "shadesOfMorttonPanel")
            if widget.isVisible()
        )
        self.assertFalse(
            panel.findChild(QLabel, "shadesOfMorttonIcon").pixmap().isNull()
        )
        pyre_combo = panel.findChild(QComboBox, "shadesOfMorttonPyreLogsCombo")
        self.assertFalse(pyre_combo.itemIcon(0).isNull())
        panel.findChild(QPushButton, "shadesOfMorttonMakePyreLogsButton").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "make_pyre_logs")
        self.assertEqual(pd["inventory"]["Pyre logs"], 1)

        key_combo = panel.findChild(QComboBox, "shadesOfMorttonKeyCombo")
        key_combo.setCurrentIndex(key_combo.findData("Bronze key red"))
        panel.findChild(QPushButton, "shadesOfMorttonOpenChestButton").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "open_bronze_chest")
        self.assertEqual(pd["shades_of_mortton_chests_opened"], 1)

        mode = panel.findChild(QComboBox, "shadesOfMorttonModeCombo")
        duty = panel.findChild(QComboBox, "shadesOfMorttonDutyCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        duty.setCurrentIndex(duty.findData("combat"))
        panel.findChild(QPushButton, "shadesOfMorttonPrimaryButton").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "shades_of_mortton")
        self.assertEqual(pd["shades_of_mortton_policy"]["duty"], "combat")

        pd["shades_of_mortton"].update(
            {"temple_repair": 99, "sanctity_tenths": 110, "altar_lit": False}
        )
        panel.findChild(QPushButton, "shadesOfMorttonSavePlanButton").click()
        QApplication.processEvents()
        light = panel.findChild(QPushButton, "shadesOfMorttonLightAltarButton")
        self.assertTrue(light.isEnabled())
        light.click()
        QApplication.processEvents()
        self.assertTrue(pd["shades_of_mortton"]["altar_lit"])
        dialog.close()
