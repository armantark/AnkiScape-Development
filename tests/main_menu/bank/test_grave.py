from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QPushButton
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_grave_banner_renders_live_recovery_state_and_disappears_after_reclaim(self) -> None:
        from ankiscape.logic_pure.logic_pure import (
            advance_combat_grave_review_pure,
            start_combat_grave_walk_pure,
        )

        player_data = _make_player_data()
        player_data.update({
            "combat_grave": {
                "items": ["Bronze sword", "Shark"],
                "reviews_remaining": 5,
                "source": "agility_failure",
                "loadout": {"weapon": "Bronze sword"},
            },
            "death_office": {
                "items": ["Wooden shield"],
                "source": "combat_stacked_grave",
            },
        })

        def start_walk():
            updated, ok = start_combat_grave_walk_pure(player_data)
            if ok:
                player_data.clear()
                player_data.update(updated)
            return ok

        player_data["combat_grave"]["travel_reviews"] = 1
        dialog = self._open(
            player_data,
            current_skill="Agility",
            on_start_grave_walk=start_walk,
        )
        try:
            dialog.show()
            QApplication.processEvents()
            banner = dialog.findChild(QPushButton, "graveRecoveryBanner")
            self.assertIsNotNone(banner)
            self.assertTrue(banner.isVisibleTo(dialog))
            self.assertIn("Gravestone: 2 items", banner.text())
            self.assertIn("expires after 5 more reviews", banner.text())
            self.assertIn("click to walk back", banner.text())
            self.assertIn("Death's Office: 1 items", banner.text())
            self.assertIn("reclaim for 100 coins", banner.text())
            self.assertIn("palette(text)", banner.styleSheet())
            self.assertNotIn("color: palette(mid)", banner.styleSheet().lower())
            self.assertTrue(banner.isEnabled())
            banner.click()
            QApplication.processEvents()
            self.assertEqual(player_data["combat_grave"]["walk_reviews_remaining"], 1)
        finally:
            dialog.deleteLater()

        player_data["death_office"] = {}
        updated = advance_combat_grave_review_pure(player_data)
        player_data.clear()
        player_data.update(updated)
        reclaimed_dialog = self._open(player_data, current_skill="Agility")
        try:
            reclaimed_dialog.show()
            QApplication.processEvents()
            banner = reclaimed_dialog.findChild(QPushButton, "graveRecoveryBanner")
            self.assertIsNotNone(banner)
            self.assertFalse(banner.isVisibleTo(reclaimed_dialog))
        finally:
            reclaimed_dialog.deleteLater()
