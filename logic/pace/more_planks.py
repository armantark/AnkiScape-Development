"""Livid Farm's More Planks Please wish: a timed Plank Make bonus.

Every answered card spends the timer, Again included. A Plank Make cast on a
card that began inside the window may add the extra output
(``logic_pure/logic_pure_magic.py``).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...data.livid_farm_data import LIVID_FARM_MORE_PLANKS_REVIEWS


def _non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def more_planks_timer(source: Mapping[str, Any]) -> dict[str, Any]:
    """The wish's timer fields of a Livid Farm state, clamped."""
    return {
        "more_planks_reviews_remaining": min(
            LIVID_FARM_MORE_PLANKS_REVIEWS,
            _non_negative_int(source.get("more_planks_reviews_remaining", 0)),
        ),
        "more_planks_active_this_review": bool(
            source.get("more_planks_active_this_review", False)
        ),
    }


def start_more_planks() -> dict[str, Any]:
    return {
        "more_planks_reviews_remaining": LIVID_FARM_MORE_PLANKS_REVIEWS,
        "more_planks_active_this_review": False,
    }


def advance_more_planks(state: dict[str, Any], answered_cards: Any) -> None:
    cards = _non_negative_int(answered_cards)
    remaining = state["more_planks_reviews_remaining"]
    state["more_planks_active_this_review"] = cards > 0 and remaining > 0
    state["more_planks_reviews_remaining"] = max(0, remaining - cards)


def more_planks_reviews_left_pure(state: Mapping[str, Any]) -> int:
    return int(state["more_planks_reviews_remaining"])
