"""One-click activation regressions for activity cards in the main menu."""

from __future__ import annotations

import unittest

from tests import test_main_menu_widget as _main_menu
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_widget,
    _make_player_data,
    _utility_row,
)

if HAS_AQT:
    from aqt.qt import QApplication, QLabel, QStackedWidget


def _training_text(dialog) -> str:
    return next(
        label.text()
        for label in dialog.findChildren(QLabel)
        if label.text().startswith("Training:")
    )


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ActivityOneClickTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    @staticmethod
    def _active_star_data() -> dict:
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        data = _make_player_data()
        data.update(
            {
                "current_utility": "bankstanding",
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_shooting_star_world_clock_pure(data)
        return active

    def test_shooting_star_starts_from_activities_and_master_list(self) -> None:
        direct = self._active_star_data()
        dialog = self.menu._open(direct, current_skill="Mining")
        tree = self.menu._open_activities(dialog)
        row = _utility_row(tree, "shooting_stars")
        tree.setCurrentItem(row)
        tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        button = _find_named_button(dialog, "shootingStarSelectButton")
        self.assertEqual(button.text(), "Mine this star")
        self.assertEqual(direct["current_utility"], "bankstanding")
        self.assertEqual(self.menu._activity_start_calls, [])
        self.assertEqual(_training_text(dialog), "Training: Mining")

        button.click()
        QApplication.processEvents()
        self.assertEqual(direct["current_utility"], "shooting_stars")
        self.assertEqual(self.menu._activity_start_calls, ["shooting_stars"])
        self.assertEqual(_training_text(dialog), "Training: Activities")

        master = self._active_star_data()
        master_dialog = self.menu._open(master, current_skill="Mining")
        before_calls = len(self.menu._activity_start_calls)
        self.menu._ui._MAIN_MENU_CTX["open_activity"]("shooting_stars")
        QApplication.processEvents()
        details = _find_named_widget(master_dialog, "utilityActivityDetailsStack")
        panel = _find_named_widget(master_dialog, "shootingStarPanel")
        master_button = _find_named_button(
            master_dialog, "shootingStarSelectButton"
        )
        self.assertIsInstance(details, QStackedWidget)
        self.assertEqual(details.currentWidget(), panel)
        self.assertEqual(master_button.text(), "Mine this star")
        self.assertEqual(master["current_utility"], "bankstanding")
        self.assertEqual(len(self.menu._activity_start_calls), before_calls)

        master_button.click()
        QApplication.processEvents()
        self.assertEqual(master["current_utility"], "shooting_stars")
        self.assertEqual(
            self.menu._activity_start_calls[before_calls:], ["shooting_stars"]
        )
        self.assertEqual(_training_text(master_dialog), "Training: Activities")

    def test_evil_tree_nurture_only_starts_activities(self) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        data = _make_player_data()
        data.update(
            {
                "current_utility": "bankstanding",
                "woodcutting_level": 1,
                "firemaking_level": 1,
                "farming_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "evil_tree": default_evil_tree_state_pure(),
            }
        )
        active, _ = advance_evil_tree_world_clock_pure(
            data, tier_roll=0.8, location_roll=0.0
        )
        dialog = self.menu._open(active, current_skill="Mining")
        self.menu._open_activities(dialog)
        button = _find_named_button(dialog, "evilTreeSelectButton")
        self.assertEqual(button.text(), "Start nurture only")

        button.click()
        QApplication.processEvents()
        self.assertEqual(active["current_utility"], "evil_tree")
        self.assertEqual(self.menu._activity_start_calls[-1], "evil_tree")
        self.assertEqual(_training_text(dialog), "Training: Activities")
