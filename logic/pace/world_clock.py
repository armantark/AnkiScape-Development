"""The shared world clock: the one world day every calendar consumer reads.

``shop_market_clock.answered_cards`` counts answered cards. This module turns
that count into world days, weeks and months, so daily and weekly content no
longer divide the count by a private day length of their own.

A world day spans ``day_length`` answered cards. Inside the day the calendar
runs six ticks per unit of game speed per card; the rest of the 24 hours passes
at the day's boundary.
"""

from __future__ import annotations

from typing import Any, Mapping

from .short_timers import card_ticks_pure

CALENDAR_TICKS_PER_DAY = 144_000  # 24 hours of 0.6-second game ticks
DEFAULT_WORLD_DAY_CARDS = 240
# Migration alone retains the old six calendar minutes per card.
CARD_CALENDAR_TICKS = CALENDAR_TICKS_PER_DAY // DEFAULT_WORLD_DAY_CARDS
DAYS_PER_WEEK = 7
DAYS_PER_MONTH = 30


def _int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    return _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0


def _sanitized_clock(raw: Any) -> dict[str, int]:
    source = raw if isinstance(raw, Mapping) else {}
    return {
        "day": _int(source.get("day")),
        "day_start_card": _int(source.get("day_start_card")),
        "day_length": _int(source.get("day_length")) or DEFAULT_WORLD_DAY_CARDS,
        "in_day_ticks": _int(source.get("in_day_ticks")),
    }


def _clock_at(player_data: Mapping[str, Any], card: int) -> dict[str, int]:
    """Return the clock as it stands once ``card`` cards have been answered.

    A save without a clock starts at day 0 on card 0, which derives the same
    240-card days the calendar has always used, so no save needs migrating.
    The clock moves on every answered card; if the count moved without it,
    the days in between keep the stored day's length.
    """
    stored = player_data.get("world_clock")
    clock = _sanitized_clock(stored)
    elapsed_days = (card - clock["day_start_card"]) // clock["day_length"]
    if not elapsed_days and isinstance(stored, Mapping):
        return clock
    day_start_card = clock["day_start_card"] + elapsed_days * clock["day_length"]
    return {
        "day": max(0, clock["day"] + elapsed_days),
        "day_start_card": day_start_card,
        "day_length": clock["day_length"],
        "in_day_ticks": (card - day_start_card) * CARD_CALENDAR_TICKS,
    }


def _current_clock(player_data: Mapping[str, Any]) -> dict[str, int]:
    return _clock_at(player_data, _answered_cards(player_data))


def advance_world_clock_pure(
    player_data: Mapping[str, Any], *, speed: int = 1,
    next_day_length: int = DEFAULT_WORLD_DAY_CARDS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Move the clock over the card that ``shop_market_clock`` just counted.

    The host calls this once after every answered card, Again included.
    """
    data = dict(player_data)
    card = _answered_cards(data)
    clock = _clock_at(data, max(0, card - 1))
    before_ticks = clock["day"] * CALENDAR_TICKS_PER_DAY + clock["in_day_ticks"]
    clock["in_day_ticks"] += card_ticks_pure(speed)
    day_end_card = clock["day_start_card"] + clock["day_length"]
    day_rolled = card >= day_end_card
    if day_rolled:
        clock = {
            "day": clock["day"] + 1,
            "day_start_card": day_end_card,
            "day_length": max(100, min(1_000, int(next_day_length))),
            "in_day_ticks": 0,
        }
    data["world_clock"] = clock
    return data, {
        "before_ticks": before_ticks,
        "after_ticks": calendar_ticks_pure(data),
        "day_rolled": day_rolled,
    }


def calendar_minutes_pure(player_data: Mapping[str, Any]) -> float:
    return calendar_ticks_pure(player_data) / 100


def world_day_index_pure(player_data: Mapping[str, Any]) -> int:
    return _current_clock(player_data)["day"]


def world_week_index_pure(player_data: Mapping[str, Any]) -> int:
    return world_day_index_pure(player_data) // DAYS_PER_WEEK


def world_month_index_pure(player_data: Mapping[str, Any]) -> int:
    return world_day_index_pure(player_data) // DAYS_PER_MONTH


def cards_until_world_day_pure(player_data: Mapping[str, Any], day: int) -> int:
    """Return the cards left before world ``day`` begins.

    Days after the current one are counted at its length, because a later
    day's length is only chosen when that day starts.
    """
    clock = _current_clock(player_data)
    day_start_card = clock["day_start_card"] + (day - clock["day"]) * clock["day_length"]
    return day_start_card - _answered_cards(player_data)


def cards_to_next_world_day_pure(player_data: Mapping[str, Any]) -> int:
    return cards_until_world_day_pure(player_data, world_day_index_pure(player_data) + 1)


def cards_to_next_world_week_pure(player_data: Mapping[str, Any]) -> int:
    next_week_day = (world_week_index_pure(player_data) + 1) * DAYS_PER_WEEK
    return cards_until_world_day_pure(player_data, next_week_day)


def calendar_ticks_pure(player_data: Mapping[str, Any]) -> int:
    clock = _current_clock(player_data)
    return clock["day"] * CALENDAR_TICKS_PER_DAY + clock["in_day_ticks"]


def world_day_start_ticks_pure(player_data: Mapping[str, Any]) -> int:
    return world_day_index_pure(player_data) * CALENDAR_TICKS_PER_DAY
