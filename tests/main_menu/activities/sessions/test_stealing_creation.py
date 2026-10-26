from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_main_tabs,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _open_reward_target,
    _utility_row,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QMessageBox, QPushButton, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_stealing_creation_card_exposes_session_policy_and_reward_tools(self) -> None:
        from ankiscape.logic.stealing_creation_logic import default_stealing_creation_state_pure

        pd = _make_player_data()
        pd.update(
            {
                "attack_level": 80,
                "defense_level": 80,
                "woodcutting_level": 80,
                "construction_level": 80,
                "stealing_creation": default_stealing_creation_state_pure(),
                "activity_session": {"active_id": ""},
            }
        )
        pd["stealing_creation"]["points"] = 40
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "stealing_creation")
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "stealingCreationPanel")
        status = _find_named_label(dialog, "stealingCreationStatusChip")
        summary = _find_named_label(dialog, "stealingCreationSummary")
        primary = _find_named_button(dialog, "stealingCreationPrimaryButton")
        leave = _find_named_button(dialog, "stealingCreationLeaveButton")
        mode = panel.findChild(QComboBox, "stealingCreationModeCombo")
        duty = panel.findChild(QComboBox, "stealingCreationDutyCombo")
        method = panel.findChild(QComboBox, "stealingCreationGatherMethodCombo")
        clay_class = panel.findChild(QComboBox, "stealingCreationClassCombo")
        recipe = panel.findChild(QComboBox, "stealingCreationRecipeCombo")
        reward_page = _open_reward_target(dialog, "stealing_creation")
        form = reward_page.findChild(QComboBox, "stealingCreationRewardFormCombo")
        morphic = reward_page.findChild(QPushButton, "stealingCreationMorphicButton")
        volatile = reward_page.findChild(QPushButton, "stealingCreationVolatileButton")
        active_tool = panel.findChild(QComboBox, "stealingCreationActiveToolCombo")
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertIn("40 reward points", summary.text())
        self.assertTrue(leave.isHidden())
        self.assertEqual(duty.currentText(), "Automatic duty rotation")
        self.assertTrue(method.currentText().startswith("Automatic route · "))
        self.assertTrue(clay_class.currentText().startswith("Automatic · Class "))
        self.assertEqual(recipe.currentText(), "Automatic kiln loadout")
        self.assertEqual(method.currentData(), "chop")
        self.assertEqual(clay_class.currentData(), 5)
        self.assertEqual(recipe.currentData(), "scimitar")

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._stealing_creation_calls[-1], ("enter", {}))
        self.assertEqual(pd["current_utility"], "stealing_creation")
        self.assertEqual(self._activity_start_calls[-1], "stealing_creation")
        self.assertEqual(status.text(), "ACTIVE")
        self.assertIn("Review 0/20", summary.text())
        self.assertFalse(leave.isHidden())

        mode.setCurrentIndex(mode.findData("advanced"))
        QApplication.processEvents()
        self.assertTrue(duty.isEnabled())
        duty.setCurrentIndex(duty.findData("process"))
        method.setCurrentIndex(method.findData("mine"))
        clay_class.setCurrentIndex(clay_class.findData(3))
        recipe.setCurrentIndex(recipe.findData("platebody"))
        QApplication.processEvents()
        action_id, payload = self._stealing_creation_calls[-1]
        self.assertEqual(action_id, "set_policy")
        self.assertEqual(payload["selected_duty"], "process")
        self.assertEqual(payload["selected_gather_method"], "mine")
        self.assertEqual(payload["selected_class"], 3)
        self.assertEqual(payload["selected_recipe"], "platebody")

        form.setCurrentIndex(form.findData("needle"))
        morphic.click()
        QApplication.processEvents()
        self.assertEqual(self._stealing_creation_calls[-1][0], "buy_tool")
        self.assertEqual(pd["inventory"]["Proto-tool"], 1)
        self.assertEqual(pd["stealing_creation"]["points"], 20)
        self.assertEqual(active_tool.findData("morphic") >= 0, True)

        volatile.click()
        QApplication.processEvents()
        self.assertEqual(self._stealing_creation_calls[-1][0], "buy_tool")
        self.assertEqual(pd["inventory"]["Volatile clay tool"], 1)
        self.assertEqual(pd["stealing_creation"]["points"], 0)
        self.assertEqual(pd["stealing_creation"]["active_reward_tool"], "volatile")
        tabs = _find_main_tabs(dialog)
        tabs.setCurrentIndex(
            next(index for index in range(tabs.count()) if tabs.tabText(index) == "Skills")
        )
        QApplication.processEvents()

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            leave.click()
        QApplication.processEvents()
        self.assertEqual(self._stealing_creation_calls[-1], ("leave", {}))
        self.assertFalse(pd["stealing_creation"]["active_session"])
        self.assertEqual(status.text(), "READY")

        dialog.show()
        dialog.resize(900, 560)
        for _ in range(8):
            QApplication.processEvents()
        self.assertTrue(panel.isVisible())
        self.assertLessEqual(
            panel.mapTo(dialog, panel.rect().bottomRight()).y(),
            dialog.contentsRect().bottom(),
        )
