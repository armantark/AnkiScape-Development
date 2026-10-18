"""The shared world clock keeps today's 240-card calendar exactly."""

import copy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.pace.world_clock import (
    advance_world_clock_pure,
    calendar_ticks_pure,
    cards_to_next_world_day_pure,
    cards_to_next_world_week_pure,
    cards_until_world_day_pure,
    world_day_index_pure,
    world_day_start_ticks_pure,
    world_month_index_pure,
    world_week_index_pure,
)


def _save(answered_cards: int) -> dict:
    return {"shop_market_clock": {"answered_cards": answered_cards, "market_tick": answered_cards}}


def _answer(player: dict) -> dict:
    """Count one card the way the answer hook does: the card counter first, then the clock."""
    counted = copy.deepcopy(player)
    counted["shop_market_clock"]["answered_cards"] += 1
    return advance_world_clock_pure(counted)


def _readings(player: dict) -> tuple:
    return (
        world_day_index_pure(player),
        world_week_index_pure(player),
        world_month_index_pure(player),
        cards_to_next_world_day_pure(player),
        cards_to_next_world_week_pure(player),
        calendar_ticks_pure(player),
    )


def _card_count_readings(answered: int) -> tuple:
    """What every consumer computed from the card count before the shared clock."""
    return (
        answered // 240,
        answered // 1_680,
        answered // 7_200,
        240 - answered % 240,
        1_680 - answered % 1_680,
        answered * 600,
    )


class WorldClockTest(unittest.TestCase):
    def test_answered_cards_roll_the_day_at_cards_240_and_480(self):
        player = _save(0)
        days = {}
        for _card in range(481):
            player = _answer(player)
            answered = player["shop_market_clock"]["answered_cards"]
            days[answered] = dict(player["world_clock"])
            self.assertEqual(_readings(player), _card_count_readings(answered))

        self.assertEqual(days[239], {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 143_400})
        self.assertEqual(days[240], {"day": 1, "day_start_card": 240, "day_length": 240, "in_day_ticks": 0})
        self.assertEqual(days[479]["day"], 1)
        self.assertEqual(days[480], {"day": 2, "day_start_card": 480, "day_length": 240, "in_day_ticks": 0})

    def test_a_save_without_a_clock_derives_the_card_count_calendar(self):
        for answered in (0, 239, 240, 1_679, 1_680, 7_200):
            with self.subTest(answered=answered):
                self.assertEqual(_readings(_save(answered)), _card_count_readings(answered))
                # Its first answer continues that calendar instead of restarting it.
                answered_once = _answer(_save(answered))
                self.assertEqual(_readings(answered_once), _card_count_readings(answered + 1))

    def test_a_card_count_moved_without_the_clock_keeps_counting_whole_days(self):
        player = _save(250)
        player["world_clock"] = {"day": 1, "day_start_card": 240, "day_length": 240, "in_day_ticks": 6_000}
        for answered in (0, 250, 1_000, 7_200):
            with self.subTest(answered=answered):
                player["shop_market_clock"]["answered_cards"] = answered
                self.assertEqual(_readings(player), _card_count_readings(answered))

    def test_the_day_start_and_any_later_day_are_read_in_cards_and_ticks(self):
        player = _save(250)
        self.assertEqual(world_day_start_ticks_pure(player), 144_000)
        self.assertEqual(calendar_ticks_pure(player), 150_000)
        self.assertEqual(cards_until_world_day_pure(player, 3), 470)
        self.assertEqual(cards_until_world_day_pure(player, 1), -10)

    def test_advancing_never_writes_through_the_callers_save(self):
        player = _save(239)
        player["world_clock"] = {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 143_400}
        player["shop_market_clock"]["answered_cards"] = 240
        baseline = copy.deepcopy(player)
        advanced = advance_world_clock_pure(player)
        self.assertEqual(player, baseline)
        self.assertEqual(advanced["world_clock"]["day"], 1)
        self.assertIsNot(advanced["world_clock"], player["world_clock"])


if __name__ == "__main__":
    unittest.main()
