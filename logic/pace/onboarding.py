"""The pace question every profile answers once (owner decisions 1, 8 and 10).

The dialog renders this plan and decides nothing. Every answer writes all three
pace settings explicitly: the recommended speed is now x10, so an existing
player who never touched the old setting would otherwise move to x10 silently.
"""

from __future__ import annotations

from typing import Any, NamedTuple

from ...data.fish_flingers_data import FISH_FLINGERS_EVENT_TICKS
from ...logic_pure.logic_pure_progression import sanitize_review_action_multiplier
from .short_timers import cards_for_ticks_pure
from .world_clock import (
    hours_of_play_per_world_day_pure,
    sanitize_world_day_cards_pure,
    suggested_world_day_cards_pure,
)

RECOMMENDED_SPEED = 10


class PaceSettings(NamedTuple):
    speed: int
    follow_study_volume: bool
    # The fixed length; a followed day takes the suggestion instead.
    world_day_cards: int


class PaceOnboardingPlan(NamedTuple):
    existing_player: bool
    current: PaceSettings
    recommended: PaceSettings
    # Closing the dialog (X or Esc) is not a choice, so it writes what the
    # player would otherwise play: a new player gets the recommendation and
    # an existing player keeps the pace of the save.
    on_close: PaceSettings


def pace_onboarding_plan_pure(
    *,
    existing_player: bool,
    speed: Any,
    legacy_speed: Any,
    follow_study_volume: Any,
    world_day_cards: Any,
    suggestion: int,
) -> PaceOnboardingPlan:
    """Plan the dialog from the raw stored settings; ``None`` means a setting was never stored.

    Only an existing player falls back to the pre-speed XP multiplier key, the
    speed that player's save was played at; a missing speed otherwise plays x1.
    """
    if speed is None and existing_player:
        speed = legacy_speed
    current = PaceSettings(
        sanitize_review_action_multiplier(1 if speed is None else speed),
        follow_study_volume is True,
        sanitize_world_day_cards_pure(world_day_cards),
    )
    recommended = PaceSettings(RECOMMENDED_SPEED, True, suggestion)
    return PaceOnboardingPlan(
        existing_player, current, recommended, current if existing_player else recommended
    )


def pace_text_fields_pure(settings: PaceSettings, study_median: int | None) -> dict[str, Any]:
    """The true numbers the pace texts quote for one choice of settings."""
    cards = suggested_world_day_cards_pure(study_median) if settings.follow_study_volume else settings.world_day_cards
    return {
        "speed": settings.speed,
        "cards": cards,
        "play": _play_time(hours_of_play_per_world_day_pure(cards, settings.speed)),
        "fish_flingers_cards": cards_for_ticks_pure(FISH_FLINGERS_EVENT_TICKS, settings.speed),
    }


def _play_time(hours: float) -> str:
    # Whole minutes: a world day lasts from 6 minutes (100 cards at 1x) to 20 hours (1,000 at 20x).
    whole_hours, minutes = divmod(round(hours * 60), 60)
    if not whole_hours:
        return f"{minutes} min"
    return f"{whole_hours} h {minutes} min" if minutes else f"{whole_hours} h"
