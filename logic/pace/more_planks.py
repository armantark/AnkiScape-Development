"""Livid Farm's More Planks Please wish: a timed Plank Make bonus.

Every answered card spends the timer, Again included. A Plank Make cast on a
card that began inside the window may add the extra output
(``logic_pure/logic_pure_magic.py``).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...data.livid_farm_data import LIVID_FARM_MORE_PLANKS_MINUTES
from .short_timers import (
    STEP_TICKS,
    TICKS_PER_LEGACY_SHORT_REVIEW,
    TICKS_PER_SOURCE_MINUTE,
    cards_for_ticks_pure,
)

MORE_PLANKS_TICKS = LIVID_FARM_MORE_PLANKS_MINUTES * TICKS_PER_SOURCE_MINUTE


def _non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def more_planks_timer(source: Mapping[str, Any]) -> dict[str, Any]:
    """The wish's timer fields of a Livid Farm state, clamped.

    A state saved before ticks counted cards of two source minutes; it converts
    here, so a running wish keeps its remaining time.
    """
    if "more_planks_ticks_remaining" in source:
        ticks = _non_negative_int(source["more_planks_ticks_remaining"])
    else:
        ticks = (
            _non_negative_int(source.get("more_planks_reviews_remaining", 0))
            * TICKS_PER_LEGACY_SHORT_REVIEW
        )
    return {
        "more_planks_ticks_remaining": min(MORE_PLANKS_TICKS, ticks),
        "more_planks_active_this_review": bool(
            source.get("more_planks_active_this_review", False)
        ),
    }


def start_more_planks() -> dict[str, Any]:
    return {
        "more_planks_ticks_remaining": MORE_PLANKS_TICKS,
        "more_planks_active_this_review": False,
    }


def advance_more_planks(state: dict[str, Any], card_ticks: Any = STEP_TICKS) -> None:
    """Spend one answered card's time budget from the wish."""
    ticks = _non_negative_int(card_ticks)
    remaining = state["more_planks_ticks_remaining"]
    state["more_planks_active_this_review"] = ticks > 0 and remaining > 0
    state["more_planks_ticks_remaining"] = max(0, remaining - ticks)


def more_planks_reviews_left_pure(state: Mapping[str, Any], speed: int) -> int:
    """The cards the wish still lasts at this game speed."""
    return cards_for_ticks_pure(int(state["more_planks_ticks_remaining"]), speed)
