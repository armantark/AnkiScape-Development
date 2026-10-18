"""Short timers: persisted countdowns whose source value is a duration of time.

Owner assumption 4 (2026-10-15): a short timer counts 0.6-second game ticks and
drains by the time budget of each card, so it lasts the same play time at every
game speed. The class of every countdown, and the source of its value, is
recorded in ``memory-bank/simulation-time-boundary-2026-07-16.md``.
"""

from __future__ import annotations

import math

from ..cadence_live import LIVE_COMBAT_TICKS_PER_REVIEW


TICKS_PER_SOURCE_MINUTE = 100
# One six-tick kernel step: the time budget of one card at speed 1.
STEP_TICKS = LIVE_COMBAT_TICKS_PER_REVIEW
# Saves from before ticks counted a short duration in answered cards of two
# source minutes each, so a running timer converts at this rate.
TICKS_PER_LEGACY_SHORT_REVIEW = 2 * TICKS_PER_SOURCE_MINUTE


def card_ticks_pure(speed: int) -> int:
    """The time budget one card buys: six ticks per unit of game speed."""
    return STEP_TICKS * max(1, int(speed or 1))


def steps_for_ticks_pure(ticks: int) -> int:
    """The six-tick steps a countdown still lasts: its cards at speed 1."""
    return math.ceil(max(0, ticks) / STEP_TICKS)


def minutes_for_ticks_pure(ticks: int) -> int:
    """Source minutes left, rounded up so a running timer never shows zero."""
    return math.ceil(max(0, ticks) / TICKS_PER_SOURCE_MINUTE)
