"""Choose the next world-day length from collection settings and completed study days."""

from ..logic.pace.world_clock import (
    DEFAULT_WORLD_DAY_CARDS,
    advance_world_clock_pure,
    sanitize_world_day_cards_pure,
    suggested_world_day_cards_pure,
    world_day_length_pure,
    world_day_rolls_on_next_card_pure,
)

from ..logic.shop.state import count_answered_cards_pure

WORLD_DAY_FOLLOW_CONFIG_KEY = "ankiscape_world_day_follow_study_volume"
WORLD_DAY_CARDS_CONFIG_KEY = "ankiscape_world_day_cards"
_SECONDS_PER_DAY = 86400


def daily_study_counts(collection) -> list[int]:
    """Read the 60 completed Anki days before the scheduler's current day.

    Revlog IDs are milliseconds. ease=0 rows are manual reschedules. Empty days
    are absent from the grouped result because the rule counts study days.
    """
    end = (collection.sched.day_cutoff - _SECONDS_PER_DAY) * 1000
    span = _SECONDS_PER_DAY * 1000
    start = end - 60 * span
    rows = collection.db.all(
        "select count(*) from revlog where id >= ? and id < ? and ease > 0 "
        "group by (id - ?) / ? order by min(id)",
        start, end, start, span,
    )
    return [int(row[0]) for row in rows]


def next_world_day_length(collection, player_data) -> int:
    """Query only on a boundary card, before Anki writes that card's revlog row."""
    if not world_day_rolls_on_next_card_pure(player_data):
        return world_day_length_pure(player_data)
    if collection is None:
        return DEFAULT_WORLD_DAY_CARDS
    if collection.get_config(WORLD_DAY_FOLLOW_CONFIG_KEY, False) is True:
        return suggested_world_day_cards_pure(daily_study_counts(collection))
    return sanitize_world_day_cards_pure(collection.get_config(WORLD_DAY_CARDS_CONFIG_KEY, DEFAULT_WORLD_DAY_CARDS))


def advance_world_clock_for_answer(player_data, collection, *, speed):
    next_length = next_world_day_length(collection, player_data)
    counted = count_answered_cards_pure(player_data)
    return advance_world_clock_pure(counted, speed=speed, next_day_length=next_length)
