"""Q9/F5 keep the noon origin while the HUD follows calendar hours."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic.pace.world_clock import simulated_clock_text_pure


class CalendarHudTests(unittest.TestCase):
    def test_the_clock_uses_played_calendar_hours_instead_of_answer_count(self):
        for ticks, expected in ((0, "12:00 PM"), (5999, "12:00 PM"), (6000, "1:00 PM"), (14400, "2:00 PM")):
            with self.subTest(ticks=ticks):
                player = {
                    "shop_market_clock": {"answered_cards": 100},
                    "world_clock": {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": ticks},
                }
                self.assertEqual(simulated_clock_text_pure(player), expected)

    def test_migration_retains_every_hour_and_a_new_day_restarts_at_noon(self):
        for cards, expected in ((0, "12:00 PM"), (10, "1:00 PM"), (120, "12:00 AM"), (239, "11:00 AM"), (240, "12:00 PM")):
            with self.subTest(cards=cards):
                self.assertEqual(simulated_clock_text_pure({"shop_market_clock": {"answered_cards": cards}}), expected)
        player = {"shop_market_clock": {"answered_cards": 500}, "world_clock": {
            "day": 2, "day_start_card": 500, "day_length": 300, "in_day_ticks": 0,
        }}
        self.assertEqual(simulated_clock_text_pure(player), "12:00 PM")
