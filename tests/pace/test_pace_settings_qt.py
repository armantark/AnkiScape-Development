"""Offscreen Qt proof of the pace rows (plan section 8; owner decisions 2, 8 and 10).

Run with the Qt venv:
    QT_QPA_PLATFORM=offscreen .venv-qt/bin/python run_tests.py tests.pace.test_pace_settings_qt
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from aqt.qt import QApplication, QCheckBox, QLabel, QPushButton, QSpinBox, Qt, QTimer, QWidget
    from PyQt6.QtTest import QTest

    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from tests import allow_modal_dialogs
from tests.pace.test_study_volume import RevlogCollection

SPEED_KEY = "ankiscape_review_action_multiplier"
FOLLOW_KEY = "ankiscape_world_day_follow_study_volume"
CARDS_KEY = "ankiscape_world_day_cards"
ANSWERED_KEY = "ankiscape_pace_dialog_answered"
LEGACY_SPEED_KEY = "ankiscape_xp_multiplier"
A_SAVE = {"ankiscape_player_data": {"mining_level": 12}}


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


def _click(name):
    def press(dialog):
        dialog.findChild(QPushButton, name).click()

    return press


def _escape(dialog):
    QTest.keyClick(dialog, Qt.Key.Key_Escape)


def _close_window(dialog):
    dialog.close()


def _apply_x15_fixed_400(dialog):
    dialog.findChild(QSpinBox, "settingsActionMultiplierSpin").setValue(15)
    dialog.findChild(QCheckBox, "settingsWorldDayFollowToggle").setChecked(False)
    dialog.findChild(QSpinBox, "settingsWorldDayCardsSpin").setValue(400)
    dialog.findChild(QPushButton, "paceDialogApplyButton").click()


class OnboardingPathTests(PaceQtCase):
    """Plan 7.2: what each player sees and what each answer writes, through the profile-load step."""

    def answer(self, store, action):
        from ankiscape.ui import ui_pace_settings

        col = self.collection(store)
        main = QWidget()
        main.col = col
        self.addCleanup(main.deleteLater)
        seen = []

        def act():
            dialog = QApplication.activeModalWidget()
            seen.append(dialog.findChild(QLabel, "paceDialogCurrentLine").text())
            action(dialog)

        QTimer.singleShot(0, act)
        with patch.object(ui_pace_settings, "mw", main), allow_modal_dialogs():
            ui_pace_settings.run_pace_onboarding()
        written = tuple(col.store.get(key) for key in (SPEED_KEY, FOLLOW_KEY, CARDS_KEY, ANSWERED_KEY))
        return written, seen

    def test_each_answer_writes_all_three_settings(self):
        recommended = (10, True, 300, True)
        paths = (
            ("new player keeps", {}, _click("paceDialogKeepButton"), (1, False, 240, True)),
            ("new player presses Esc", {}, _escape, recommended),
            ("new player closes the window", {}, _close_window, recommended),
            ("new player applies a choice", {}, _apply_x15_fixed_400, (15, False, 400, True)),
            ("existing player keeps", {**A_SAVE, LEGACY_SPEED_KEY: 4}, _click("paceDialogKeepButton"), (4, False, 240, True)),
            ("existing player presses Esc", {**A_SAVE, SPEED_KEY: 3}, _escape, (3, False, 240, True)),
            ("existing player applies", {**A_SAVE, SPEED_KEY: 3}, _click("paceDialogApplyButton"), recommended),
        )
        for name, store, action, expected in paths:
            with self.subTest(name):
                self.assertEqual(self.answer(store, action)[0], expected)

    def test_the_current_line_quotes_the_current_pace(self):
        _, seen = self.answer({**A_SAVE, LEGACY_SPEED_KEY: 4}, _escape)
        self.assertEqual(len(seen), 1)
        for field in ("speed=4", "cards=240", "hours=0.96", "fish_flingers_cards=42"):
            self.assertIn(field, seen[0])

    def test_an_answered_profile_is_never_asked_again(self):
        from ankiscape.ui import ui_pace_settings

        col = self.collection({ANSWERED_KEY: True, SPEED_KEY: 7})
        main = QWidget()
        main.col = col
        self.addCleanup(main.deleteLater)
        with patch.object(ui_pace_settings, "mw", main), patch.object(ui_pace_settings.PaceDialog, "exec") as shown:
            ui_pace_settings.run_pace_onboarding()
        shown.assert_not_called()
        self.assertEqual(col.store, {ANSWERED_KEY: True, SPEED_KEY: 7})


if __name__ == "__main__":
    unittest.main()
