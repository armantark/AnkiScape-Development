from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_reward_target, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QProgressBar, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_barbarian_assault_tutorial_shop_plan_and_active_state_are_live(self) -> None:
        from ankiscape.logic.barbarian_assault_logic import apply_barbarian_assault_command_pure

        pd = _make_player_data()
        pd["barbarian_assault_points"] = {
            role_id: 100
            for role_id in ("attacker", "collector", "defender", "healer")
        }
        command_calls = []

        def barbarian_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_barbarian_assault_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_barbarian_assault_command=barbarian_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "barbarian_assault"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "barbarianAssaultPanel")
            if widget.isVisible()
        )
        self.assertFalse(
            panel.findChild(QLabel, "barbarianAssaultIcon").pixmap().isNull()
        )
        progress = panel.findChild(QProgressBar, "barbarianAssaultProgress")
        self.assertFalse(progress.isVisible())

        tutorial = panel.findChild(QPushButton, "barbarianAssaultTutorialButton")
        self.assertTrue(tutorial.isVisible())
        tutorial.click()
        QApplication.processEvents()
        self.assertTrue(pd["barbarian_assault_tutorial_complete"])

        reward_page = _open_reward_target(dialog, "barbarian_assault")
        buy = reward_page.findChild(QPushButton, "barbarianAssaultBuyBootsButton")
        self.assertTrue(buy.isVisibleTo(dialog))
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Runner boots"], 1)
        self.assertEqual(set(pd["barbarian_assault_points"].values()), {0})

        tree = self._open_activities(dialog)
        tree.setCurrentItem(item)
        tree.itemActivated.emit(item, 0)
        QApplication.processEvents()
        mode = panel.findChild(QComboBox, "barbarianAssaultModeCombo")
        role = panel.findChild(QComboBox, "barbarianAssaultRoleCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        role.setCurrentIndex(role.findData("defender"))
        panel.findChild(QPushButton, "barbarianAssaultPrimaryButton").click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "barbarian_assault")
        self.assertEqual(pd["barbarian_assault"]["role"], "defender")
        self.assertTrue(progress.isVisible())
        dialog.close()
