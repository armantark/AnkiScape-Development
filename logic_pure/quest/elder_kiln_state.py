"""The Elder Kiln's one flat hatching attempt: defaults, detached copies, sanitation.

Sanitation never reads quest progress, never writes proofs and never infers a
hatch: a hatched attempt survives only beside its genuine proof.
"""

from collections.abc import Mapping

from ...data.quest.elder_kiln import (
    BANDS, HEAT_BOUNDS, HELPER_COOLDOWN, HELPER_IDS, HELPER_INITIAL_DELAY, HELPER_WARNING,
    INITIAL_BAND, INITIAL_HEAT, INITIAL_PROGRESS, PROGRESS_COMPLETE,
)

PHASES = ("request", "preparing", "active", "failed", "hatched")
HELPER_PHASES = ("delay", "warning", "cooldown")
FIELDS = (
    "phase", "heat", "progress", "band", "steps", "attempt",
    "ak_phase", "ak_remaining", "jeh_phase", "jeh_remaining",
)


def _initial_helper(index):
    delay = HELPER_INITIAL_DELAY[index]
    return ("delay", delay) if delay > 0 else ("warning", HELPER_WARNING)


def transient_defaults_pure():
    """The contracted start of an attempt, without its phase or attempt number."""
    state = {"heat": INITIAL_HEAT, "progress": INITIAL_PROGRESS, "band": INITIAL_BAND, "steps": 0}
    for index, helper in enumerate(HELPER_IDS):
        state[f"{helper}_phase"], state[f"{helper}_remaining"] = _initial_helper(index)
    return state


def default_elder_kiln_state_pure():
    return {"phase": "request", **transient_defaults_pure(), "attempt": 0}


def copy_elder_kiln_state_pure(raw):
    """An independent copy for transactions; it performs no sanitation or migration."""
    return dict(raw) if isinstance(raw, Mapping) else default_elder_kiln_state_pure()


def _is_int(value):
    return type(value) is int


def _helper_valid(state, index):
    helper = HELPER_IDS[index]
    phase, remaining = state[f"{helper}_phase"], state[f"{helper}_remaining"]
    limits = {"delay": HELPER_INITIAL_DELAY[index], "warning": HELPER_WARNING, "cooldown": HELPER_COOLDOWN}
    return phase in HELPER_PHASES and _is_int(remaining) and 1 <= remaining <= limits[phase]


def _phase_consistent(state, hatch_proven):
    phase, progress = state["phase"], state["progress"]
    if phase == "request":
        return state == default_elder_kiln_state_pure()
    if state["attempt"] < 1:
        return False
    if phase == "active":
        return 0 < progress < PROGRESS_COMPLETE
    if phase == "hatched":
        return progress == PROGRESS_COMPLETE and hatch_proven
    return progress == 0


def _scalars_valid(state):
    low, high = HEAT_BOUNDS
    numbers = (state["heat"], state["progress"], state["band"], state["steps"], state["attempt"])
    return (
        all(_is_int(value) for value in numbers)
        and low <= state["heat"] <= high
        and 0 <= state["progress"] <= PROGRESS_COMPLETE
        and 1 <= state["band"] <= len(BANDS)
        and state["steps"] >= 0 and state["attempt"] >= 0
    )


def elder_kiln_state_valid_pure(raw, hatch_proven):
    if not isinstance(raw, Mapping) or set(raw) != set(FIELDS):
        return False
    state = dict(raw)
    if state["phase"] not in PHASES or not _scalars_valid(state):
        return False
    if not all(_helper_valid(state, index) for index in range(len(HELPER_IDS))):
        return False
    return _phase_consistent(state, hatch_proven)


def sanitize_elder_kiln_state_pure(raw, hatch_proven):
    """A fresh valid attempt; anything malformed or unproven resets to the request."""
    if elder_kiln_state_valid_pure(raw, hatch_proven):
        return {field: raw[field] for field in FIELDS}
    return default_elder_kiln_state_pure()
