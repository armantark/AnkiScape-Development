"""The once-per-profile pace question (plan 7.2; owner decisions 1, 8 and 10)."""

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.pace.onboarding import (
    PaceSettings,
    pace_onboarding_plan_pure,
    pace_text_fields_pure,
)
from ankiscape.logic.pace.world_clock import world_day_setting_view_pure
from ankiscape.ui.ui_pace_settings import study_volume_text

NEVER_STORED = {"speed": None, "legacy_speed": None, "follow_study_volume": None, "world_day_cards": None}


def _plan(existing_player, suggestion=240, **stored):
    return pace_onboarding_plan_pure(
        existing_player=existing_player, suggestion=suggestion, **{**NEVER_STORED, **stored}
    )


class ThePlanForEachPlayerTests(unittest.TestCase):
    def test_a_new_player_sees_x1_and_closing_takes_the_recommendation(self):
        plan = _plan(False, suggestion=310, legacy_speed=4)
        self.assertEqual(plan.current, PaceSettings(1, False, 240))
        self.assertEqual(plan.recommended, PaceSettings(10, True, 310))
        self.assertEqual(plan.on_close, plan.recommended)

    def test_an_existing_player_keeps_the_stored_speed_and_closing_keeps_it(self):
        plan = _plan(True, speed=3, legacy_speed=7)
        self.assertEqual(plan.current, PaceSettings(3, False, 240))
        self.assertEqual(plan.recommended, PaceSettings(10, True, 240))
        self.assertEqual(plan.on_close, plan.current)

    def test_an_existing_player_without_a_speed_falls_back_to_the_old_xp_key_then_x1(self):
        self.assertEqual(_plan(True, legacy_speed=7).current.speed, 7)
        self.assertEqual(_plan(True).current.speed, 1)

    def test_stored_world_day_settings_are_what_play_reads(self):
        plan = _plan(True, speed=20, follow_study_volume=True, world_day_cards=5000)
        self.assertEqual(plan.current, PaceSettings(20, True, 1000))


class TheTrueNumbersTests(unittest.TestCase):
    def test_hours_of_2012_play_per_world_day_and_fish_flingers_cards_per_game(self):
        rows = {
            speed: pace_text_fields_pure(PaceSettings(speed, False, 240), study_median=400)
            for speed in (1, 10, 20)
        }
        self.assertEqual(
            [(row["play"], row["fish_flingers_cards"]) for row in rows.values()],
            [("14 min", 167), ("2 h 24 min", 17), ("4 h 48 min", 9)],
        )

    def test_a_followed_day_is_measured_at_the_suggestion(self):
        fields = pace_text_fields_pure(PaceSettings(10, True, 240), study_median=400)
        self.assertEqual((fields["cards"], fields["play"]), (400, "4 h"))

    def test_the_suggestion_names_the_median_when_a_bound_or_the_default_replaces_it(self):
        cases = {
            62: ("100 cards", "minimum", "62 cards"),
            1240: ("1,000 cards", "maximum", "1,240 cards"),
            None: ("240 cards", "7 study days"),
        }
        for median, parts in cases.items():
            with self.subTest(median):
                for part in parts:
                    self.assertIn(part, study_volume_text(median))
        self.assertEqual(study_volume_text(300), "300 cards, your median per study day")


class TheWorldDayRowTests(unittest.TestCase):
    def test_following_shows_the_suggestion_locked_and_a_fixed_day_is_editable(self):
        self.assertEqual(tuple(world_day_setting_view_pure(True, 500, 310)), (310, False))
        self.assertEqual(tuple(world_day_setting_view_pure(False, 500, 310)), (500, True))


if __name__ == "__main__":
    unittest.main()
