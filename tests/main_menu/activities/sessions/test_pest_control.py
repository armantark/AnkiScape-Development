from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_reward_target, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QProgressBar, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_pest_control_detail_plan_shop_and_active_state_are_live(self) -> None:
        from ankiscape.logic.pest_control_logic import apply_pest_control_command_pure

        pd = _make_player_data()
        pd.update(
            {
                "attack_level": 40,
                "strength_level": 40,
                "defense_level": 40,
                "constitution_level": 40,
                "ranged_level": 40,
                "magic_level": 40,
                "prayer_level": 40,
                "summoning_level": 1,
                "pest_control_commendations": 170,
                "conquest_rating": 1_250,
            }
        )
        command_calls = []

        def pest_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_pest_control_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_pest_control_command=pest_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "pest_control"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "pestControlPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "pestControlIcon").pixmap().isNull())
        self.assertFalse(panel.findChild(QProgressBar, "pestControlProgress").isVisible())

        reward_page = _open_reward_target(dialog, "pest_control")
        buy = reward_page.findChild(QPushButton, "pestControlBuySealButton")
        self.assertTrue(buy.isVisibleTo(dialog))
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Void seal (8)"], 1)
        self.assertEqual(pd["pest_control_commendations"], 160)
        deflector = reward_page.findChild(
            QPushButton, "pestControlBuyDeflectorButton"
        )
        self.assertTrue(deflector.isEnabled())
        deflector.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Void knight deflector"], 1)
        self.assertEqual(pd["pest_control_commendations"], 10)

        tree = self._open_activities(dialog)
        tree.setCurrentItem(item)
        tree.itemActivated.emit(item, 0)
        QApplication.processEvents()
        mode = panel.findChild(QComboBox, "pestControlModeCombo")
        lander = panel.findChild(QComboBox, "pestControlLanderCombo")
        duty = panel.findChild(QComboBox, "pestControlDutyCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        lander.setCurrentIndex(lander.findData("novice"))
        duty.setCurrentIndex(duty.findData("defend"))
        panel.findChild(QPushButton, "pestControlPrimaryButton").click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "pest_control")
        self.assertEqual(pd["pest_control"]["duty"], "defend")
        self.assertTrue(panel.findChild(QProgressBar, "pestControlProgress").isVisible())
        dialog.close()
