from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _open_reward_target,
    _utility_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QPushButton
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_big_chinchompa_panel_starts_event_and_runs_reward_shop(self) -> None:
        from ankiscape.logic.big_chinchompa_logic import (
            advance_big_chinchompa_world_clock_pure,
            default_big_chinchompa_state_pure,
        )
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "hunter_level": 99,
                "shop_market_clock": {"answered_cards": 60},
                "big_chinchompa": default_big_chinchompa_state_pure(),
                "evil_tree": default_evil_tree_state_pure(),
            }
        )
        pd["big_chinchompa"]["competence_points"] = 100
        active, _ = advance_evil_tree_world_clock_pure(pd)
        active, _ = advance_big_chinchompa_world_clock_pure(active)
        pd.clear()
        pd.update(active)
        dialog = self._open(pd)
        utility_tree = self._open_activities(dialog)

        status = _find_named_label(dialog, "bigChinchompaStatusChip")
        button = _find_named_button(dialog, "bigChinchompaSelectButton")
        fullness = _find_named_widget(dialog, "bigChinchompaFullness")
        self.assertIn("world min left", status.text())
        self.assertEqual(button.text(), "Start active event")
        self.assertFalse(fullness.isHidden())

        button.click()
        QApplication.processEvents()
        self.assertEqual(self._activity_start_calls[-1], "big_chinchompa")
        self.assertEqual(pd["current_utility"], "big_chinchompa")
        self.assertEqual(button.text(), "Active for reviews")

        evil_button = _find_named_button(dialog, "evilTreeSelectButton")
        self.assertTrue(evil_button.isEnabled())
        evil_button.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "evil_tree")
        self.assertEqual(button.text(), "Start active event")
        self.assertTrue(button.isEnabled())

        button.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "big_chinchompa")

        self.assertIsNone(
            dialog.findChild(QComboBox, "bigChinchompaPopulationProfile")
        )

        reward_page = _open_reward_target(dialog, "big_chinchompa")
        buy = reward_page.findChild(
            QPushButton, "bigChinchompaRewardBuyButton"
        )
        self.assertTrue(buy.isEnabled())
        self.assertIn("4 Competence", buy.toolTip())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Swamp lizard quota ticket"], 1)
        self.assertEqual(pd["big_chinchompa"]["competence_points"], 96)

        utility_tree = self._open_utility(dialog)
        bankstanding = _utility_row(utility_tree, "bankstanding")
        utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self._open_activities(dialog)
        button = _find_named_button(dialog, "bigChinchompaSelectButton")
        self.assertEqual(button.text(), "Start active event")
