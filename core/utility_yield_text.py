"""What one card of a batch utility makes, in the words its tooltip uses.

The review handler runs a utility's batch once per six-tick step until the
card's time budget is spent, so one card at game speed N runs N batches: Pick
cabbages gathers 28 at 1x and 280 at 10x. Activities run their own handlers,
so their rows keep the batch alone.
"""

from __future__ import annotations

from collections.abc import Mapping

from ..logic.pace.short_timers import STEP_TICKS, card_ticks_pure
from .constants import UTILITY_SURFACE_ID


def _per_card(batch_size: object, speed: int) -> str:
    return f"{int(batch_size) * (card_ticks_pure(speed) // STEP_TICKS):,}"


def utility_run_text_pure(spec: Mapping[str, object], speed: int) -> str:
    batch_size = spec.get("batch_size", 1)
    if spec.get("deactivate_after_run"):
        return "Runs once, then switches off. No skill XP."
    if spec.get("surface") != UTILITY_SURFACE_ID:
        return f"Processes up to {batch_size} per successful card. No skill XP."
    verb = "Gathers" if spec.get("group") == "gathering" else "Processes"
    return f"{verb} up to {_per_card(batch_size, speed)} per successful card at {speed}x game speed. No skill XP."


def bird_nest_run_text_pure(batch_size: object, speed: int) -> str:
    return f"Opens up to {_per_card(batch_size, speed)} bird nests per successful card at {speed}x game speed. No XP."
