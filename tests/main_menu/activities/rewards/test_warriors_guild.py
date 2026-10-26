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
    from tests.test_main_menu_widget import QApplication, QComboBox
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_warriors_guild_panel_exposes_tokens_policy_and_room_state(self) -> None:
        pd = _make_player_data()
        pd["attack_level"] = 99
        pd["strength_level"] = 99
        pd["current_utility"] = "warriors_guild_animated_armour"
        pd["inventory"].update(
            {
                "Rune full helm": 1,
                "Rune platebody": 1,
                "Rune platelegs": 1,
            }
        )
        dialog = self._open(pd)
        utility_tree = self._open_activity_detail(
            dialog, "warriors_guild_animated_armour"
        )
        dialog.show()
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "warriorsGuildPanel")
        self.assertTrue(panel.isVisible())
        token_label = _find_named_label(dialog, "warriorsGuildTokenBalances")
        self.assertIn("Combat 0", token_label.text())
        self.assertIn("Balance 0", token_label.text())
        room_button = _find_named_button(dialog, "warriorsGuildRoomButton")
        self.assertFalse(room_button.isEnabled())
        self.assertIn("Need 30 of every", room_button.toolTip())

        for activity_id in (
            "warriors_guild_animated_armour",
            "warriors_guild_attack_dummy",
            "warriors_guild_catapult",
            "warriors_guild_shot_put",
            "warriors_guild_keg_balance",
        ):
            self.assertFalse(
                _utility_row(utility_tree, activity_id).icon(0).isNull(),
                activity_id,
            )

        automation = _find_named_widget(dialog, "warriorsGuildAutomationMode")
        self.assertIsInstance(automation, QComboBox)
        automation.setCurrentIndex(automation.findData("advanced"))
        QApplication.processEvents()
        self.assertEqual(
            self._warriors_guild_calls[-1][0],
            "set_policy",
        )
        self.assertEqual(pd["warriors_guild"]["automation_mode"], "advanced")
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        show_button = _find_named_button(
            dialog,
            "warriorsGuildShowDefender",
        )
        self.assertGreaterEqual(
            show_button.width(),
            show_button.sizeHint().width(),
        )
        next_label = _find_named_label(dialog, "warriorsGuildNextDefender")
        self.assertGreaterEqual(
            next_label.width(),
            next_label.sizeHint().width(),
        )
