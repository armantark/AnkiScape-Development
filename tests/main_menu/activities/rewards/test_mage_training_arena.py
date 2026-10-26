from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_reward_target, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_mage_training_arena_shop_buys_selected_reward_and_plan_goal_stays_live(self) -> None:
        from ankiscape.logic.mage_training_arena_logic import (
            apply_mage_training_arena_command_pure,
            default_mage_training_arena_state_pure,
        )

        pd = _make_player_data()
        pd["magic_level"] = 99
        pd["mage_training_arena"] = default_mage_training_arena_state_pure()
        pd["mage_training_arena"]["reward_goal"] = "cosmic_rune"
        for room_id in pd["mage_training_arena"]["wallets"]:
            pd["mage_training_arena"]["wallets"][room_id] = 10_000
        command_calls = []

        def arena_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_mage_training_arena_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_mage_training_arena_command=arena_command,
        )
        dialog.show()
        dialog.resize(dialog.width(), 560)
        for _ in range(4):
            QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "mage_training_arena"
        )
        tree.itemClicked.emit(item, 0)
        for _ in range(4):
            QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "mageTrainingArenaPanel")
            if widget.isVisible()
        )
        visible = panel.visibleRegion().boundingRect()
        self.assertEqual(visible.width(), panel.width())
        self.assertEqual(visible.height(), panel.height())
        self.assertEqual(panel.width(), panel.parentWidget().width())
        reward_page = _open_reward_target(dialog, "mage_training_arena")
        purchase = reward_page.findChild(
            QPushButton, "mageTrainingArenaPurchaseButton"
        )

        reward = reward_page.findChild(QComboBox, "mageTrainingArenaRewardCombo")
        self.assertEqual(reward.count(), 25)
        self.assertEqual(
            (reward.iconSize().width(), reward.iconSize().height()),
            (24, 24),
        )
        for reward_id in (
            "infinity_gloves",
            "mages_book",
            "bones_to_peaches",
            "mist_rune",
            "blood_rune",
        ):
            index = reward.findData(reward_id)
            self.assertGreaterEqual(index, 0)
            self.assertFalse(reward.itemIcon(index).isNull())
        reward.setCurrentIndex(reward.findData("bones_to_peaches"))
        purchase.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("purchase", {"reward_id": "bones_to_peaches"}))
        self.assertTrue(pd["mage_training_arena"]["completed"])
        self.assertEqual(pd["mage_training_arena"]["reward_goal"], "cosmic_rune")

        tree = self._open_activities(dialog)
        tree.setCurrentItem(item)
        tree.itemActivated.emit(item, 0)
        QApplication.processEvents()
        goal = panel.findChild(QComboBox, "mageTrainingArenaGoalCombo")
        save = panel.findChild(QPushButton, "mageTrainingArenaSaveButton")
        self.assertEqual(goal.count(), 25)
        self.assertEqual(
            (goal.iconSize().width(), goal.iconSize().height()),
            (24, 24),
        )
        self.assertFalse(goal.itemIcon(goal.findData("infinity_top")).isNull())
        self.assertFalse(goal.itemIcon(goal.findData("bones_to_peaches")).isNull())
        self.assertTrue(goal.isVisibleTo(dialog))
        self.assertTrue(save.isVisibleTo(dialog))
        goal.setCurrentIndex(goal.findData("bones_to_peaches"))
        save.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "set_policy")
        self.assertEqual(command_calls[-1][1]["reward_goal"], "bones_to_peaches")
        self.assertEqual(pd["mage_training_arena"]["reward_goal"], "bones_to_peaches")
        dialog.close()
