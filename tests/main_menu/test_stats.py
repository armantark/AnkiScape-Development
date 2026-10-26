from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _find_stats_button, _make_player_data
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_stats_tab_shows_registered_skill_details(self) -> None:
        for skill_id, skill_name in (
            ("fletching", "Fletching"),
            ("firemaking", "Firemaking"),
            ("fishing", "Fishing"),
            ("runecrafting", "Runecrafting"),
        ):
            with self.subTest(skill=skill_name):
                dialog = self._open(_make_player_data(), current_skill="Mining")
                try:
                    _find_stats_button(dialog, skill_id).click()
                    QApplication.processEvents()
                    labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
                    self.assertIn(f"{skill_name} Stats", labels)
                    self.assertIn("Current / Base Level:", labels)
                finally:
                    dialog.deleteLater()

    def test_stats_grid_shows_live_current_level_over_base_level(self) -> None:
        player_data = _make_player_data()
        player_data["combat_current_levels"] = {
            "attack": 40,
            "strength": 29,
        }
        player_data["agility_effective_boost"] = 5
        player_data["agility_boost_actions_remaining"] = 4
        dialog = self._open(player_data)
        try:
            self.assertEqual(_find_stats_button(dialog, "attack").text(), "40 / 1")
            self.assertEqual(_find_stats_button(dialog, "strength").text(), "29 / 1")
            self.assertEqual(_find_stats_button(dialog, "agility").text(), "38 / 33")
            self.assertEqual(_find_stats_button(dialog, "mining").text(), "33 / 33")
            _find_stats_button(dialog, "attack").click()
            QApplication.processEvents()
            labels = [label.text() for label in dialog.findChildren(QLabel)]
            self.assertIn("Current / Base Level:", labels)
            self.assertIn("40 / 1", labels)
        finally:
            dialog.deleteLater()
