from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _find_main_tabs
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QPushButton, QSpinBox, QToolButton, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_live_theme_controls_use_palette_text_without_an_unreleased_review_link(self) -> None:
        utility_button = next(
            button
            for button in self.dialog.findChildren(QPushButton)
            if button.text() == "Utilities"
        )
        utility_button.click()
        QApplication.processEvents()
        self.assertIn("color: palette(text)", utility_button.styleSheet())

        stop_button = next(
            button
            for button in self.dialog.findChildren(QPushButton)
            if button.text() == "Stop training"
        )
        self.assertIn("color: palette(text)", stop_button.styleSheet())

        self.assertFalse(
            any(
                "ankiweb.net/shared/review" in label.text()
                for label in self.dialog.findChildren(QLabel)
            )
        )

        tabs = _find_main_tabs(self.dialog)
        help_button = self.dialog.findChild(QToolButton, "mainMenuHelpButton")
        self.assertIsNotNone(help_button)
        self.assertIsNone(tabs.cornerWidget(Qt.Corner.TopRightCorner))
        self.assertEqual(help_button.parentWidget().objectName(), "mainMenuFooter")

    def test_settings_expose_action_multiplier_under_gameplay(self) -> None:
        labels = [lbl.text() for lbl in self.dialog.findChildren(QLabel)]
        self.assertIn("Gameplay", labels)
        self.assertIn("Game speed:", labels)
        spin = self.dialog.findChild(QSpinBox, "settingsActionMultiplierSpin")
        self.assertIsNotNone(spin, "no action multiplier spin box found")
        self.assertEqual(spin.minimum(), 1)
        self.assertEqual(spin.maximum(), 20)
