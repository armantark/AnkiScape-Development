"""Decision 9: calendar play uses the card budget, then skips the logout gap."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic.pace.world_clock import advance_world_clock_pure, calendar_ticks_pure


def counted(player):
    data = copy.deepcopy(player)
    data["shop_market_clock"]["answered_cards"] += 1
    return data


def clock_player(cards=0, ticks=0, length=240):
    return {
        "shop_market_clock": {"answered_cards": cards, "market_tick": 0},
        "world_clock": {"day": 0, "day_start_card": 0, "day_length": length, "in_day_ticks": ticks},
    }


class CalendarSpeedTests(unittest.TestCase):
    def test_play_and_logout_gap_make_one_calendar_day_at_each_speed(self):
        for speed, play_ticks in ((1, 1440), (10, 14400), (20, 28800)):
            with self.subTest(speed=speed):
                player = clock_player()
                for _ in range(239):
                    player, delta = advance_world_clock_pure(counted(player), speed=speed)
                    self.assertEqual(delta["after_ticks"] - delta["before_ticks"], 6 * speed)
                    self.assertFalse(delta["day_rolled"])
                self.assertEqual(calendar_ticks_pure(player) + 6 * speed, play_ticks)
                player, delta = advance_world_clock_pure(counted(player), speed=speed)
                self.assertEqual(calendar_ticks_pure(player), 144000)
                self.assertTrue(delta["day_rolled"])
                self.assertEqual(delta["after_ticks"] - delta["before_ticks"], 144000 - 239 * 6 * speed)
                self.assertEqual(player["world_clock"]["in_day_ticks"], 0)

    def test_migration_keeps_the_old_time_then_uses_the_new_speed(self):
        player = {"shop_market_clock": {"answered_cards": 81, "market_tick": 81}}
        self.assertEqual(calendar_ticks_pure(player), 48600)
        after, delta = advance_world_clock_pure(counted(player), speed=10)
        self.assertEqual(delta, {"before_ticks": 48600, "after_ticks": 48660, "day_rolled": False})
        self.assertEqual(calendar_ticks_pure(after), 48660)
        self.assertNotIn("world_clock", player)

    def test_length_is_adopted_only_at_the_boundary_and_next_card_uses_it(self):
        player = clock_player(238, 14280)
        player, _ = advance_world_clock_pure(counted(player), speed=10, next_day_length=500)
        self.assertEqual(player["world_clock"]["day_length"], 240)
        player, _ = advance_world_clock_pure(counted(player), speed=10, next_day_length=500)
        self.assertEqual(player["world_clock"], {"day": 1, "day_start_card": 240, "day_length": 500, "in_day_ticks": 0})
        player, _ = advance_world_clock_pure(counted(player), speed=1)
        self.assertEqual(calendar_ticks_pure(player), 144006)
        self.assertEqual(player["world_clock"]["day_length"], 500)

    def test_a_speed_change_uses_each_cards_own_budget_without_mutating_input(self):
        player = clock_player()
        original = copy.deepcopy(player)
        first, _ = advance_world_clock_pure(counted(player), speed=1)
        second, _ = advance_world_clock_pure(counted(first), speed=10)
        self.assertEqual(calendar_ticks_pure(second), 66)
        self.assertEqual(player, original)

    def test_the_largest_approved_day_stays_inside_twenty_four_hours(self):
        player = clock_player(999, 999 * 120, length=1000)
        after, delta = advance_world_clock_pure(counted(player), speed=20, next_day_length=1000)
        self.assertLess(delta["before_ticks"] + 120, 144000)
        self.assertEqual(after["world_clock"]["day_start_card"], 1000)
        self.assertEqual(after["world_clock"]["day_length"], 1000)
