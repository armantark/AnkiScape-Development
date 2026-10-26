from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_reward_target, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_troll_invasion_keeps_plan_reward_and_redeems_book_in_shop(self) -> None:
        from ankiscape.logic.troll_invasion_logic import (
            apply_troll_invasion_command_pure,
            default_troll_invasion_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_troll_invasion_state_pure())
        pd["troll_invasion_reward_fractions"] = [1.0]
        pd["inventory"]["Troll Invasion reward book"] = 1
        command_calls = []

        def command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_troll_invasion_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(pd, on_troll_invasion_command=command)
        dialog.show()
        activity_tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(activity_tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "troll_invasion"
        )
        activity_tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "trollInvasionPanel")
            if widget.isVisible()
        )
        policy_reward = panel.findChild(
            QComboBox, "trollInvasionRewardSkillCombo"
        )
        self.assertTrue(policy_reward.isVisibleTo(dialog))

        reward_page = _open_reward_target(dialog, "troll_invasion")
        shop_reward = reward_page.findChild(
            QComboBox, "trollInvasionShopRewardSkillCombo"
        )
        redeem = reward_page.findChild(QPushButton, "trollInvasionRedeemButton")
        self.assertTrue(shop_reward.isVisibleTo(dialog))
        self.assertTrue(redeem.isEnabled())
        redeem.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("redeem_book", {"skill_id": "agility"}))
        self.assertEqual(pd["troll_invasion_reward_fractions"], [])
        self.assertEqual(pd["troll_invasion_books_redeemed"], 1)
        dialog.close()
