"""Offscreen Qt proof of the pace rows (plan section 8; owner decisions 2, 8 and 10).

Run with the Qt venv:
    QT_QPA_PLATFORM=offscreen .venv-qt/bin/python run_tests.py tests.pace.test_pace_settings_qt
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from aqt.qt import QApplication, QCheckBox, QLabel, QSpinBox

    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from tests.pace.test_study_volume import RevlogCollection

SPEED_KEY = "ankiscape_review_action_multiplier"
FOLLOW_KEY = "ankiscape_world_day_follow_study_volume"
CARDS_KEY = "ankiscape_world_day_cards"


class PaceCollection(RevlogCollection):
    """A profile whose last seven completed Anki days each had 300 answers."""

    def __init__(self, store=None):
        super().__init__(store)
        for days_ago in range(1, 8):
            self.add_day(days_ago, 300)

    def set_config(self, key, value):
        self.store[key] = value


@unittest.skipUnless(HAS_AQT, "aqt (PyQt6) is not installed")
class PaceQtCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def collection(self, store=None) -> PaceCollection:
        col = PaceCollection(store)
        self.addCleanup(col.connection.close)
        return col

    def shown(self, widget):
        self.addCleanup(widget.deleteLater)
        widget.show()
        for _ in range(3):
            QApplication.processEvents()
        return widget


class SettingsRowsTests(PaceQtCase):
    def test_each_change_is_saved_and_the_hint_shows_only_for_a_fixed_day(self):
        from ankiscape.ui.ui_pace_settings import pace_settings_section

        col = self.collection({SPEED_KEY: 10, FOLLOW_KEY: True, CARDS_KEY: 500})
        section = self.shown(pace_settings_section(col))
        speed = section.findChild(QSpinBox, "settingsActionMultiplierSpin")
        follow = section.findChild(QCheckBox, "settingsWorldDayFollowToggle")
        cards = section.findChild(QSpinBox, "settingsWorldDayCardsSpin")
        hint = section.findChild(QLabel, "settingsWorldDaySuggestionHint")
        self.assertEqual((speed.value(), speed.maximum(), follow.isChecked()), (10, 20, True))
        self.assertEqual((cards.value(), cards.isEnabled(), hint.isVisible()), (300, False, False))

        follow.setChecked(False)
        self.assertEqual((cards.value(), cards.isEnabled(), hint.isVisible()), (500, True, True))
        self.assertIn("300", hint.text())
        cards.setValue(650)
        speed.setValue(20)
        self.assertEqual((col.store[SPEED_KEY], col.store[FOLLOW_KEY], col.store[CARDS_KEY]), (20, False, 650))

        follow.setChecked(True)
        self.assertEqual((cards.value(), cards.isEnabled(), hint.isVisible()), (300, False, False))
        self.assertEqual((col.store[FOLLOW_KEY], col.store[CARDS_KEY]), (True, 650))


if __name__ == "__main__":
    unittest.main()
