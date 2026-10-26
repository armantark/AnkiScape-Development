from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_main_tabs,
    _find_named_list,
    _make_player_data,
    _open_reward_target,
    _open_shop_tab,
    _tree_items,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QProgressBar, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_castle_wars_detail_shop_plan_and_siege_actions_are_live(self) -> None:
        from ankiscape.data.castle_wars_data import CASTLE_WARS_BALLISTA_PARTS
        from ankiscape.logic.castle_wars_logic import apply_castle_wars_command_pure

        pd = _make_player_data()
        pd["castle_wars_tickets"] = 20
        pd["castle_wars_games_played"] = 500
        for item_name in CASTLE_WARS_BALLISTA_PARTS:
            pd["inventory"][item_name] = 1
        pd["inventory"]["Ballista ammo"] = 2
        pd["inventory"]["Castlewars chinchompa"] = 1
        command_calls = []

        def castle_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_castle_wars_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_castle_wars_command=castle_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "castle_wars"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "castleWarsPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "castleWarsIcon").pixmap().isNull())
        self.assertFalse(panel.findChild(QProgressBar, "castleWarsProgress").isVisible())

        self.assertIsNone(panel.findChild(QWidget, "castleWarsRewardShop"))
        before_dialogs = len(self._captured)
        _open_shop_tab(dialog)
        rewards = _find_named_list(dialog, "rewardShopTargetList")
        castle_target = next(
            rewards.item(index)
            for index in range(rewards.count())
            if rewards.item(index).data(Qt.ItemDataRole.UserRole).get("target_id")
            == "castle_wars"
        )
        rewards.setCurrentItem(castle_target)
        QApplication.processEvents()
        self.assertEqual(len(self._captured), before_dialogs)
        shop = dialog.findChild(QWidget, "rewardShopPage_castle_wars")
        self.assertTrue(shop.isVisibleTo(dialog))
        reward = shop.findChild(QComboBox, "castleWarsRewardCombo")
        buy = shop.findChild(QPushButton, "castleWarsBuyButton")
        self.assertEqual(reward.currentData(), "basic_body")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Basic decorative platebody"], 1)
        self.assertEqual(pd["castle_wars_tickets"], 12)

        tabs = _find_main_tabs(dialog)
        tabs.setCurrentIndex(
            next(index for index in range(tabs.count()) if tabs.tabText(index) == "Skills")
        )
        QApplication.processEvents()
        mode = panel.findChild(QComboBox, "castleWarsModeCombo")
        duty = panel.findChild(QComboBox, "castleWarsDutyCombo")
        team = panel.findChild(QComboBox, "castleWarsTeamCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        duty.setCurrentIndex(duty.findData("defend"))
        team.setCurrentIndex(team.findData("zamorak"))
        panel.findChild(QPushButton, "castleWarsPrimaryButton").click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "castle_wars")
        self.assertEqual(pd["castle_wars"]["duty"], "defend")
        self.assertEqual(pd["castle_wars"]["team"], "zamorak")
        self.assertTrue(panel.findChild(QProgressBar, "castleWarsProgress").isVisible())

        shop = _open_reward_target(dialog, "castle_wars")
        self.assertTrue(
            shop.findChild(QWidget, "castleWarsRewardShop").isVisibleTo(dialog)
        )
        self.assertGreater(shop.height(), 0)
        self.assertFalse(shop.findChild(QPushButton, "castleWarsBuyButton").isEnabled())
        self.assertIn(
            "between matches",
            shop.findChild(QPushButton, "castleWarsBuyButton").toolTip(),
        )
        tabs.setCurrentIndex(
            next(index for index in range(tabs.count()) if tabs.tabText(index) == "Skills")
        )
        QApplication.processEvents()

        ballista = panel.findChild(QPushButton, "castleWarsBallistaButton")
        chinchompa = panel.findChild(QPushButton, "castleWarsChinchompaButton")
        self.assertTrue(ballista.isEnabled())
        self.assertTrue(chinchompa.isEnabled())
        ballista.click()
        chinchompa.click()
        QApplication.processEvents()
        self.assertTrue(pd["castle_wars"]["ballista_deployed"])
        self.assertEqual(pd["inventory"]["Castlewars chinchompa"], 0)
        dialog.close()
