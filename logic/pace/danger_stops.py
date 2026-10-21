"""The shared danger projections that end a card before its budget is spent."""

from typing import NamedTuple

from ...logic_pure.logic_pure_combat_food import _combat_auto_eat_food_available, combat_max_lifepoints_pure
from ...logic_pure.logic_pure_state import _non_negative_int, _positive_int


class CardDangerState(NamedTuple):
    low_lp_no_food: bool
    stunned: bool
    poisoned: bool
    prayer_points: int
    prayers_selected: bool
    bank_trip: bool


def low_lifepoints_without_food_pure(data, lifepoints=None, maximum=None) -> bool:
    if lifepoints is None:
        lifepoints = data.get("combat_lifepoints")
    if lifepoints is None:
        return False
    maximum = combat_max_lifepoints_pure(data) if maximum is None else maximum
    percent = _positive_int(data.get("combat_auto_eat_threshold_percent", 40), 40)
    return lifepoints <= max(1, int(maximum * percent / 100.0)) and not _combat_auto_eat_food_available(data)


def card_danger_state_pure(data) -> CardDangerState:
    """Copy only the five danger projections, before a handler mutates its save."""
    return CardDangerState(
        low_lifepoints_without_food_pure(data),
        bool(data.get("thieving_stunned") or data.get("card_tick_debt")),
        bool((data.get("combat_status_effects") or {}).get("poison")),
        _non_negative_int(data.get("combat_prayer_points", 0), 0),
        bool(data.get("combat_selected_prayers")),
        bool(data.get("skilling_bank_run")),
    )


def card_danger_stop_pure(before: CardDangerState, after: CardDangerState) -> str:
    if after.low_lp_no_food:
        return "low_lp_no_food"
    if before.prayer_points > 0 and after.prayer_points == 0 and before.prayers_selected:
        return "prayer_empty"
    transitions = (
        (before.stunned, after.stunned, "stun"),
        (before.poisoned, after.poisoned, "poison_started"),
        (before.bank_trip, after.bank_trip, "bank_trip"),
    )
    return next((reason for old, new, reason in transitions if new and not old), "")
