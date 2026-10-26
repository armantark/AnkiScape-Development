from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _utility_row,
    copy,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_evil_tree_panel_reports_countdown_and_starts_active_event(self) -> None:
        from ankiscape.logic.evil_tree_logic import advance_evil_tree_world_clock_pure, default_evil_tree_state_pure

        pd = _make_player_data()
        pd["shop_market_clock"] = {"answered_cards": 100}
        pd["world_clock"] = {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 11_880}
        pd["evil_tree"] = {**default_evil_tree_state_pure(), "next_spawn_tick": 12_000}
        countdown_dialog = self._open(pd)
        self._open_activities(countdown_dialog)
        self.assertEqual(
            _find_named_label(countdown_dialog, "evilTreeStatusChip").text(),
            "Next in 20 reviews",
        )
        self.assertFalse(
            _find_named_button(
                countdown_dialog, "evilTreeSelectButton"
            ).isEnabled()
        )
        due = copy.deepcopy(pd)
        due["world_clock"]["in_day_ticks"] = 12_000
        due_dialog = self._open(due)
        self._open_activities(due_dialog)
        self.assertEqual(
            _find_named_label(due_dialog, "evilTreeStatusChip").text(),
            "Next review",
        )

        pd["world_clock"]["in_day_ticks"] = 12_000
        active, _ = advance_evil_tree_world_clock_pure(pd)
        pd.clear()
        pd.update(active)
        active_dialog = self._open(pd)
        utility_tree = self._open_activities(active_dialog)
        button = _find_named_button(active_dialog, "evilTreeSelectButton")
        self.assertEqual(button.text(), "Start full event")
        self.assertTrue(button.isEnabled())
        self.assertIn(
            "Nurture → Prepare → Fell",
            _find_named_label(active_dialog, "evilTreeDetail").text(),
        )

        button.click()
        QApplication.processEvents()
        self.assertEqual(self._activity_start_calls[-1], "evil_tree")
        self.assertEqual(pd["current_utility"], "evil_tree")
        self.assertEqual(button.text(), "Active for reviews")
        self.assertFalse(button.isEnabled())
        utility_tree = self._open_utility(active_dialog)
        bankstanding = _utility_row(utility_tree, "bankstanding")
        utility_tree.itemClicked.emit(bankstanding, 0)
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "bankstanding")
        self._open_activities(active_dialog)
        button = _find_named_button(active_dialog, "evilTreeSelectButton")
        self.assertEqual(button.text(), "Start full event")
        self.assertTrue(button.isEnabled())

    def test_evil_tree_panel_makes_nurture_only_gate_explicit(self) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "woodcutting_level": 1,
                "firemaking_level": 1,
                "farming_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "evil_tree": default_evil_tree_state_pure(),
            }
        )
        active, _ = advance_evil_tree_world_clock_pure(
            pd, tier_roll=0.8, location_roll=0.0
        )
        pd.clear()
        pd.update(active)
        dialog = self._open(pd)
        self._open_activities(dialog)

        button = _find_named_button(dialog, "evilTreeSelectButton")
        detail = _find_named_label(dialog, "evilTreeDetail").text()
        self.assertEqual(button.text(), "Start nurture only")
        self.assertTrue(button.isEnabled())
        self.assertIn("cannot fell", detail)
        self.assertIn("75 Woodcutting", detail)
        self.assertIn("75 Firemaking", detail)

    def test_evil_tree_panel_disables_daily_limit_with_reason(self) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "shop_market_clock": {"answered_cards": 20},
                "evil_tree": default_evil_tree_state_pure(),
            }
        )
        active, _ = advance_evil_tree_world_clock_pure(pd)
        active["evil_tree"]["participations_today"] = 2
        dialog = self._open(active)
        self._open_activities(dialog)

        button = _find_named_button(dialog, "evilTreeSelectButton")
        self.assertEqual(button.text(), "Unavailable")
        self.assertFalse(button.isEnabled())
        self.assertIn(
            "Two Evil Tree interactions used this review day",
            _find_named_label(dialog, "evilTreeDetail").text(),
        )

    def test_activities_world_events_strip_summarizes_evil_tree_and_star(
        self,
    ) -> None:
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            default_evil_tree_state_pure,
        )
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "mining_level": 99,
                "shop_market_clock": {"answered_cards": 20},
                "evil_tree": default_evil_tree_state_pure(),
                "shooting_star": default_shooting_star_state_pure(),
            }
        )
        active, _ = advance_evil_tree_world_clock_pure(pd)
        active["evil_tree"]["blessing_ticks_remaining"] = 12  # two speed-1 cards
        active["evil_tree"]["blessing_tier"] = "normal"
        active, _ = advance_shooting_star_world_clock_pure(active)
        dialog = self._open(active)
        activity_tree = self._open_activities(dialog)

        strip = _find_named_widget(dialog, "activityWorldEventsStrip")
        body = _find_named_label(dialog, "activityWorldEventsBody")
        self.assertTrue(strip.isVisibleTo(dialog))
        self.assertIn("evil tree", body.text().lower())
        self.assertIn("Evil Tree blessing · 2 reviews left", body.text())
        self.assertIn("Shooting Star size", body.text())

        # Opening a card suppresses that card's own row, so the strip never
        # duplicates the detail already on screen.
        star_row = _utility_row(activity_tree, "shooting_stars")
        activity_tree.itemActivated.emit(star_row, 0)
        QApplication.processEvents()
        self.assertNotIn("Shooting Star size", body.text())
        self.assertIn("evil tree", body.text().lower())
        self.assertIn("Evil Tree blessing · 2 reviews left", body.text())
