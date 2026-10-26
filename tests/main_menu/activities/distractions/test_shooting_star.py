from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _make_player_data,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_shooting_star_selects_from_utilities_without_building_activities(self) -> None:
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_shooting_star_world_clock_pure(pd)
        pd.clear()
        pd.update(active)
        dialog = self._open(pd, current_skill="Mining")
        dialog.show()
        dialog.resize(1200, 560)
        self._open_utility(dialog)
        for _ in range(4):
            QApplication.processEvents()

        select = _find_named_button(dialog, "shootingStarSelectButton")
        select.click()
        QApplication.processEvents()

        self.assertEqual(pd["current_utility"], "shooting_stars")
        self.assertEqual(self._activity_start_calls, ["shooting_stars"])
        self.assertEqual(select.text(), "Active for reviews")
        self.assertTrue(
            any(
                label.text() == "Training: Activities"
                for label in dialog.findChildren(QLabel)
            )
        )

    def test_shooting_star_panel_selects_and_exchanges_without_spawn_controls(self) -> None:
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_shooting_star_world_clock_pure(pd)
        pd.clear()
        pd.update(active)
        dialog = self._open(pd)
        self._open_activities(dialog)

        status = _find_named_label(dialog, "shootingStarStatusChip")
        select = _find_named_button(dialog, "shootingStarSelectButton")
        self.assertTrue(status.text().startswith("Size "))
        self.assertEqual(select.text(), "Mine this star")
        self.assertTrue(select.isEnabled())
        self.assertTrue(
            _find_named_button(dialog, "shootingStarExchangeButton").isHidden()
        )

        select.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "shooting_stars")
        self.assertEqual(self._activity_start_calls[-1], "shooting_stars")
        self.assertEqual(select.text(), "Active for reviews")

        for object_name in (
            "shootingStarAutomationMode",
            "shootingStarMinimumSize",
            "shootingStarMaximumSize",
            "shootingStarPopulationProfile",
        ):
            self.assertIsNone(dialog.findChild(QComboBox, object_name))

        event = pd["shooting_star"]["active_event"]
        event.update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_card": 22,
            }
        )
        pd["inventory"]["Stardust"] = 200
        reward_dialog = self._open(pd)
        self._open_activities(reward_dialog)
        exchange = _find_named_button(
            reward_dialog, "shootingStarExchangeButton"
        )
        self.assertFalse(exchange.isHidden())
        self.assertTrue(exchange.isEnabled())
        exchange.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Cosmic rune"], 152)
        self.assertEqual(pd["inventory"]["Astral rune"], 52)
        self.assertEqual(pd["inventory"]["Gold ore"], 20)
        self.assertEqual(pd["inventory"]["Coins"], 50_002)
        self.assertEqual(pd["inventory"]["Stardust"], 0)
        self.assertEqual(
            pd["shooting_star"]["ore_bonus_ticks_remaining"], 1_500
        )
