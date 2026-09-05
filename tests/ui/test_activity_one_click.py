"""One-click activation regressions for activity cards in the main menu."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from tests import test_direct_action_undo_seam as _undo_seam
from tests import test_main_menu_widget as _main_menu
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_widget,
    _make_player_data,
    _utility_row,
)

if HAS_AQT:
    from aqt.qt import QApplication, QLabel, QMessageBox, QStackedWidget


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

    def test_declined_activity_switch_keeps_target_and_skips_start_callback(self) -> None:
        from ankiscape.logic.gnome_ball_logic import enter_gnome_ball_pure
        from ankiscape.logic.managing_miscellania_logic import (
            default_managing_miscellania_state_pure,
        )

        data = _make_player_data()
        data.update(default_managing_miscellania_state_pure())
        data.update({"equipment": {}, "activity_session": {"active_id": ""}})
        data["quests"]["throne_of_miscellania"] = {"completed": True}
        data, ok, _info = enter_gnome_ball_pure(data)
        self.assertTrue(ok)
        dialog = self.menu._open(data)
        tree = self.menu._open_activities(dialog)
        row = _utility_row(tree, "managing_miscellania")
        tree.setCurrentItem(row)
        tree.itemActivated.emit(row, 0)
        QApplication.processEvents()
        button = _find_named_button(dialog, "managingMiscellaniaSelectButton")
        before_calls = len(self.menu._activity_start_calls)

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            button.click()
        QApplication.processEvents()

        self.assertEqual(data["current_utility"], "gnome_ball")
        self.assertEqual(len(self.menu._activity_start_calls), before_calls)


class ActivityStartRuntimeTest(unittest.TestCase):
    """Exercise the real package seam without rediscovering its harness tests."""

    def setUp(self) -> None:
        self.seam = _undo_seam.DirectActionUndoSeamTest(methodName="runTest")
        self.seam.setUp()
        self.addon = self.seam.addon

    def tearDown(self) -> None:
        self.seam.tearDown()

    def test_shooting_star_start_is_one_undoable_transition(self) -> None:
        from ankiscape.logic.shooting_star_logic import (
            default_shooting_star_state_pure,
        )

        star_state = default_shooting_star_state_pure()
        star_state["active_event"] = {
            "event_id": "shooting-star-20",
            "slot_card": 20,
            "location": "Falador east mine",
            "starting_size": 1,
            "current_size": 1,
            "layer_remaining": 1_200,
        }
        self.addon._state.player_data = {
            "current_utility": "bankstanding",
            "mining_level": 10,
            "shooting_star": star_state,
        }
        self.addon._state.current_skill = "Mining"
        hud_calls = []
        self.addon.update_review_hud = lambda data, skill: hud_calls.append(
            (data.get("current_utility"), skill)
        )

        self.assertTrue(
            self.addon.start_activity_for_reviews("shooting_stars")
        )

        self.assertEqual(
            self.addon._state.player_data["current_utility"], "shooting_stars"
        )
        self.assertEqual(self.addon._state.current_skill, "Activities")
        self.assertEqual(len(self.seam.saves), 1)
        self.assertEqual(hud_calls, [("shooting_stars", "Activities")])
        self.assertEqual(
            self.seam.collection.entries, ["AnkiScape direct action"]
        )

        self.addon._on_state_did_undo(
            type("Changes", (), {"operation": "AnkiScape direct action"})()
        )
        self.assertEqual(
            self.addon._state.player_data["current_utility"], "bankstanding"
        )
        self.assertEqual(self.addon._state.current_skill, "Mining")

    def test_unminable_star_still_raises_one_persistent_notice(self) -> None:
        from ankiscape.logic.shooting_star_logic import (
            default_shooting_star_state_pure,
        )

        state = default_shooting_star_state_pure()
        state["active_event"] = {
            "event_id": "shooting-star-20",
            "slot_card": 20,
            "location": "Falador east mine",
            "starting_size": 9,
            "current_size": 9,
            "layer_remaining": 15,
        }
        calls = {"save": 0, "event_drawer": 0}
        popups = []
        self.addon.ui.show_bankstanding_dialog = popups.append
        self.addon._state.player_data = {
            "current_utility": "shooting_stars",
            "mining_level": 10,
            "shooting_star": state,
            "shop_market_clock": {"answered_cards": 20},
        }
        self.addon._state.current_skill = "Activities"
        self.addon.save_player_data = lambda: calls.__setitem__(
            "save", calls["save"] + 1
        )
        self.addon.update_review_event_log_drawer = lambda _data: calls.__setitem__(
            "event_drawer", calls["event_drawer"] + 1
        )
        self.addon._update_review_context_surface = lambda: None

        self.assertFalse(
            self.addon.start_activity_for_reviews("shooting_stars")
        )
        self.assertFalse(
            self.addon.start_activity_for_reviews("shooting_stars")
        )

        self.assertEqual(self.addon._state.current_skill, "Utilities")
        self.assertEqual(
            self.addon._state.player_data["current_utility"], "bankstanding"
        )
        self.assertEqual(calls, {"save": 1, "event_drawer": 1})
        self.assertEqual(len(popups), 1)
        self.assertIn("Star unminable at your level", popups[0])
        self.assertEqual(len(self.addon._state.player_data["review_event_log"]), 1)
        self.assertEqual(
            self.addon._state.player_data["shooting_star"]["notice"]["kind"],
            "unminable",
        )
