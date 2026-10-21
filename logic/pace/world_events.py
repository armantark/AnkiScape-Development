"""Sub-day event slots use play time and never run through the daily gap."""

from typing import Any, Mapping

from .short_timers import cards_for_ticks_pure
from .world_clock import (
    CALENDAR_TICKS_PER_DAY, answered_cards_pure, calendar_ticks_pure, cards_to_next_world_day_pure,
    world_day_length_pure, world_day_start_ticks_pure,
)


def event_in_play_pure(data: Mapping[str, Any]) -> bool:
    return answered_cards_pure(data) > 0 and cards_to_next_world_day_pure(data) != world_day_length_pure(data)


def event_slot_tick_pure(data: Mapping[str, Any], interval_ticks: int) -> int:
    start = world_day_start_ticks_pure(data)
    return start + (calendar_ticks_pure(data) - start) // interval_ticks * interval_ticks


def next_event_tick_pure(data: Mapping[str, Any], interval_ticks: int) -> int:
    if not event_in_play_pure(data):
        return world_day_start_ticks_pure(data)
    return min(event_slot_tick_pure(data, interval_ticks) + interval_ticks,
               world_day_start_ticks_pure(data) + CALENDAR_TICKS_PER_DAY)


def chinchompa_slot_card_pure(data: Mapping[str, Any], *, next_slot: bool = False) -> int:
    card = answered_cards_pure(data)
    length = world_day_length_pure(data)
    start = card + cards_to_next_world_day_pure(data) - length
    slots = (start + (length + 3) // 4, start + (3 * length + 3) // 4)
    if next_slot:
        return next((slot for slot in slots if slot > card), start + length + (length + 3) // 4)
    return max((slot for slot in slots if slot <= card), default=0)


def cards_until_event_pure(data: Mapping[str, Any], tick: int, speed: int) -> int:
    if not event_in_play_pure(data):
        return 1
    return min(cards_for_ticks_pure(max(0, tick - calendar_ticks_pure(data)), speed),
               cards_to_next_world_day_pure(data) + 1)


def consumed_event_slot_pure(data: Mapping[str, Any], slot: int, previous: int) -> int:
    return slot if event_in_play_pure(data) else previous


def event_ticks_remaining_pure(data: Mapping[str, Any], interval: int, lifetime: int) -> int:
    if not event_in_play_pure(data):
        return 0
    return max(0, lifetime - (calendar_ticks_pure(data) - event_slot_tick_pure(data, interval)))
