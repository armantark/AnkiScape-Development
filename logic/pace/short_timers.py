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


def cards_for_steps_pure(steps: int, speed: int) -> int:
    """The cards that many six-tick steps take at this game speed."""
    return math.ceil(max(0, steps) / max(1, int(speed or 1)))


def cards_for_ticks_pure(ticks: int, speed: int) -> int:
    """The cards a countdown still lasts at this game speed: every counter the
    player reads says cards, so it must be true at the speed being played."""
    return math.ceil(max(0, ticks) / card_ticks_pure(speed))


def minutes_for_ticks_pure(ticks: int) -> int:
    """Source minutes left, rounded up so a running timer never shows zero."""
    return math.ceil(max(0, ticks) / TICKS_PER_SOURCE_MINUTE)
