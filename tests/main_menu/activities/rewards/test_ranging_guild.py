from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_ranging_guild_activity_page_enters_claims_and_buys_reward(self) -> None:
        from ankiscape.data.ranging_guild_data import RANGING_GUILD_TICKET_ITEM
        from ankiscape.logic.ranging_guild_logic import (
            apply_ranging_guild_command_pure,
            default_ranging_guild_state_pure,
        )

        pd = _make_player_data()
        pd["ranged_level"] = 40
        pd["inventory"]["Coins"] = 200
        pd["inventory"]["Bronze arrows"] = 0
        pd["equipment"] = {
            "weapon": "Shortbow",
            "ammunition": "Bronze arrows",
        }
        pd["ranging_guild"] = default_ranging_guild_state_pure()
        command_calls = []

        def ranging_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_ranging_guild_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_ranging_guild_command=ranging_command,
        )
        dialog.show()
        dialog.resize(dialog.width(), 560)
        for _ in range(4):
            QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "ranging_guild"
        )
        tree.itemClicked.emit(item, 0)
        for _ in range(4):
            QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "rangingGuildPanel")
            if widget.isVisible()
        )
        self.assertLessEqual(panel.sizeHint().height(), 560)
        primary = panel.findChild(QPushButton, "rangingGuildPrimaryButton")
        primary.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("enter", {}))
        self.assertEqual(pd["inventory"]["Coins"], 0)
        self.assertEqual(pd["inventory"]["Bronze arrows"], 10)

        pd["ranging_guild"].update(
            {"active": False, "pending_claim": True, "shots_fired": 10, "score": 120}
        )
        pd["activity_session"] = {"active_id": ""}
        panel.refresh()
        primary.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("claim", {}))
        self.assertEqual(pd["inventory"][RANGING_GUILD_TICKET_ITEM], 12)

        reward = panel.findChild(QComboBox, "rangingGuildRewardCombo")
        reward.setCurrentIndex(reward.findData("coif"))
        purchase = panel.findChild(QPushButton, "rangingGuildPurchaseButton")
        self.assertFalse(reward.itemIcon(reward.currentIndex()).isNull())
        purchase.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("purchase", {"reward_id": "coif"}))
        self.assertEqual(pd["inventory"]["Coif"], 1)
        self.assertEqual(pd["inventory"][RANGING_GUILD_TICKET_ITEM], 0)
        dialog.close()
