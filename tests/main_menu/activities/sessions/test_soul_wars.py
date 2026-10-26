from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_main_tabs,
    _make_player_data,
    _open_reward_target,
    _tree_items,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QProgressBar, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_soul_wars_detail_plan_shop_and_active_state_are_live(self) -> None:
        from ankiscape.logic.soul_wars_logic import apply_soul_wars_command_pure

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
                "slayer_level": 40,
                "summoning_level": 1,
                "combat_supply_loadout": {"food": {}},
                "soul_wars_zeal": 30,
            }
        )
        command_calls = []

        def soul_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_soul_wars_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_soul_wars_command=soul_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "soul_wars"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "soulWarsPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "soulWarsIcon").pixmap().isNull())
        progress = panel.findChild(QProgressBar, "soulWarsProgress")
        self.assertFalse(progress.isVisible())

        reward_page = _open_reward_target(dialog, "soul_wars")
        reward = reward_page.findChild(QComboBox, "soulWarsRewardCombo")
        buy = reward_page.findChild(QPushButton, "soulWarsBuyCharmsButton")
        self.assertEqual(reward.currentData(), "Gold charm")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "buy_charms")
        self.assertGreater(pd["inventory"]["Gold charm"], 0)
        self.assertEqual(pd["soul_wars_zeal"], 26)
        tabs = _find_main_tabs(dialog)
        tabs.setCurrentIndex(
            next(index for index in range(tabs.count()) if tabs.tabText(index) == "Skills")
        )
        QApplication.processEvents()

        mode = panel.findChild(QComboBox, "soulWarsModeCombo")
        team = panel.findChild(QComboBox, "soulWarsTeamCombo")
        duty = panel.findChild(QComboBox, "soulWarsDutyCombo")
        mode.setCurrentIndex(mode.findData("advanced"))
        team.setCurrentIndex(team.findData("creation"))
        duty.setCurrentIndex(duty.findData("defend"))
        panel.findChild(QPushButton, "soulWarsPrimaryButton").click()
        QApplication.processEvents()

        self.assertEqual(command_calls[-1][0], "enter")
        self.assertEqual(pd["current_utility"], "soul_wars")
        self.assertEqual(pd["soul_wars"]["team"], "creation")
        self.assertEqual(pd["soul_wars"]["duty"], "defend")
        self.assertTrue(progress.isVisible())
        dialog.close()
