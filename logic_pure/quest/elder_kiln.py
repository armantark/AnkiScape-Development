"""The Elder Kiln's egg-hatching exercise: admission, commands and the logical step.

Every reducer returns detached state and leaves inventory, equipment, runes and
experience untouched. Only _complete_hatch_pure records the hatch, and only on
the live transition that reaches 100%.
"""

from copy import deepcopy

from ...data.quest.elder_kiln import (
    BANDS, COOLING_STEP, HATCH_EVENT, HEAT_BOUNDS, HELPER_CALL, HELPER_COOLDOWN, HELPER_HEAT,
    HELPER_IDS, HELPER_NAMES, HELPER_WARNING, MARKER_INTERVAL, PROGRESS_COMPLETE, PROGRESS_STEP,
    QUEST_ID, SPELL_DELTAS, SPELL_IDS, STATE_KEY,
)
from ...data.quest_action_proof_data import ELDER_KILN_HATCH_PROOF
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure
from ..quest_action_proofs import quest_action_proof_completed_pure, record_runtime_quest_action_proofs_pure
from .elder_kiln_state import sanitize_elder_kiln_state_pure, transient_defaults_pure

LIVE_PHASES = ("preparing", "active")
TERMINAL_PHASES = ("failed", "hatched")
# Waiting returns control at the first of these; a marker draw bounds it.
WAIT_STOP_EVENTS = frozenset({
    "left_band", "marker", "helper_warning", "helper_impact", "helper_skip", "failed", "hatched",
})


def elder_kiln_opening_applies_pure(player_data, quest_id):
    if quest_id != QUEST_ID:
        return False
    state = quest_state_pure(player_data, quest_id)
    return (
        not state["completed"] and state["progress"] in (0, 1)
        and not quest_action_proof_completed_pure(player_data, ELDER_KILN_HATCH_PROOF)
    )


def _is_hatch_blocker(blocker):
    return blocker.get("kind") == "required_action" and blocker.get("action_id") == ELDER_KILN_HATCH_PROOF


def elder_kiln_admission_reasons_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons):
    """Base-level entry skills and every blocker except the opening's own missing deed."""
    if quest_id not in quest_data or not elder_kiln_opening_applies_pure(player_data, quest_id):
        return ("The hatching opening is not available",)
    reasons = [f"Requires {reason}" for reason in eligibility_reasons(player_data, quest_id, quest_data)]
    reasons.extend(str(blocker.get("reason")) for blocker in blockers if not _is_hatch_blocker(blocker))
    return tuple(dict.fromkeys(reasons))


def elder_kiln_review_ready_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons):
    return elder_kiln_opening_applies_pure(player_data, quest_id) and not elder_kiln_admission_reasons_pure(
        player_data, quest_id, quest_data, blockers, eligibility_reasons,
    )


def _clamp_heat(value):
    low, high = HEAT_BOUNDS
    return max(low, min(high, value))


def _in_band(state):
    low, high = BANDS[state["band"] - 1]
    return low <= state["heat"] <= high


def offer_elder_kiln_help_pure(attempt):
    if attempt["phase"] != "request":
        return None
    return dict(attempt, phase="preparing", attempt=attempt["attempt"] + 1), (("offered",),)


def retry_elder_kiln_attempt_pure(attempt):
    if attempt["phase"] != "failed":
        return None
    return {"phase": "preparing", **transient_defaults_pure(), "attempt": attempt["attempt"] + 1}, (("retried",),)


def _helper_fires(state, name, events):
    if state["heat"] < BANDS[state["band"] - 1][0]:
        state["heat"] = _clamp_heat(state["heat"] + HELPER_HEAT)
        events.append(("helper_impact", name))
    else:
        events.append(("helper_skip", name))


def _advance_helper(state, index, events):
    helper, name = HELPER_IDS[index], HELPER_NAMES[index]
    state[f"{helper}_remaining"] -= 1
    if state[f"{helper}_remaining"] > 0:
        return
    if state[f"{helper}_phase"] == "warning":
        _helper_fires(state, name, events)
        state[f"{helper}_phase"], state[f"{helper}_remaining"] = "cooldown", HELPER_COOLDOWN
    else:
        state[f"{helper}_phase"], state[f"{helper}_remaining"] = "warning", HELPER_WARNING
        events.append(("helper_warning", name))


def _apply_progress(state, events):
    delta = PROGRESS_STEP if _in_band(state) else -PROGRESS_STEP
    state["progress"] = max(0, min(PROGRESS_COMPLETE, state["progress"] + delta))
    if state["phase"] == "preparing" and state["progress"] > 0:
        state["phase"] = "active"
        events.append(("activated",))
    elif state["phase"] == "active" and state["progress"] == 0:
        state["phase"] = "failed"
        events.append(("failed",))
    if state["phase"] == "active" and state["progress"] == PROGRESS_COMPLETE:
        state["phase"] = "hatched"
        events.append(("hatched",))


def _finish_step(state, rng, events):
    state["steps"] += 1
    if state["steps"] % MARKER_INTERVAL == 0:
        state["band"] = 1 + min(len(BANDS) - 1, int(rng() * len(BANDS)))
        events.append(("marker", state["band"]))
    state["heat"] = _clamp_heat(state["heat"] - COOLING_STEP)


def elder_kiln_step_pure(attempt, rng):
    """One logical step: helpers, progress, then (unless terminal) counter, markers and cooling."""
    if attempt["phase"] not in LIVE_PHASES:
        return None
    state, events = dict(attempt), []
    was_in_band = _in_band(state)
    for index in range(len(HELPER_IDS)):
        _advance_helper(state, index, events)
    _apply_progress(state, events)
    if state["phase"] not in TERMINAL_PHASES:
        _finish_step(state, rng, events)
    if was_in_band and not _in_band(state):
        events.append(("left_band",))
    return state, tuple(events)


def cast_elder_kiln_spell_pure(attempt, spell_id, rng):
    if attempt["phase"] not in LIVE_PHASES or spell_id not in SPELL_IDS:
        return None
    heated = dict(attempt, heat=_clamp_heat(attempt["heat"] + SPELL_DELTAS[SPELL_IDS.index(spell_id)]))
    return elder_kiln_step_pure(heated, rng)


def wait_elder_kiln_until_change_pure(attempt, rng):
    """Repeat the step until something the player should react to; never casts."""
    if attempt["phase"] not in LIVE_PHASES:
        return None
    state, events = attempt, []
    for _ in range(MARKER_INTERVAL):
        state, step_events = elder_kiln_step_pure(state, rng)
        events.extend(step_events)
        if any(event[0] in WAIT_STOP_EVENTS for event in step_events):
            break
    return state, tuple(events)


def _attempt_command(attempt, command, rng):
    if command == "offer":
        return offer_elder_kiln_help_pure(attempt)
    if command == "retry":
        return retry_elder_kiln_attempt_pure(attempt)
    if command == "wait_step":
        return elder_kiln_step_pure(attempt, rng)
    if command == "wait_change":
        return wait_elder_kiln_until_change_pure(attempt, rng)
    if isinstance(command, str) and command.startswith("cast:"):
        return cast_elder_kiln_spell_pure(attempt, command.removeprefix("cast:"), rng)
    return None


def _complete_hatch_pure(player_data):
    """The sole hatch-proof producer, reached only from a live 100% transition."""
    if player_data[STATE_KEY]["phase"] != "hatched":
        return False
    return record_runtime_quest_action_proofs_pure(player_data, *HATCH_EVENT)


def elder_kiln_attempt_pure(player_data):
    """The stored attempt as play would see it; malformed or unproven state is the request."""
    proven = quest_action_proof_completed_pure(player_data, ELDER_KILN_HATCH_PROOF)
    return sanitize_elder_kiln_state_pure(player_data.get(STATE_KEY), proven)


def _refused(player_data):
    """An unchanged but detached copy, so the caller never holds its input."""
    return deepcopy(player_data), False, ()


def apply_elder_kiln_command_pure(player_data, quest_id, command, rng):
    """Returns (player data, accepted, events); a refused command changes nothing."""
    if not elder_kiln_opening_applies_pure(player_data, quest_id):
        return _refused(player_data)
    if not quest_state_pure(player_data, quest_id)["started"]:
        return _refused(player_data)
    result = _attempt_command(elder_kiln_attempt_pure(player_data), command, rng)
    if result is None:
        return _refused(player_data)
    attempt, events = result
    data = _copy_player_data_with_nested(player_data)
    data[STATE_KEY] = attempt
    if attempt["phase"] == "hatched" and not _complete_hatch_pure(data):
        return _refused(player_data)
    return data, True, events


def _helper_warnings(attempt):
    """The Mejs call out only while an attempt is under way."""
    if attempt["phase"] not in LIVE_PHASES:
        return ()
    return tuple(
        f"{name}: {HELPER_CALL}" for helper, name in zip(HELPER_IDS, HELPER_NAMES)
        if attempt[f"{helper}_phase"] == "warning"
    )


def elder_kiln_observation_pure(player_data, events=(), accepted=True):
    """Everything a presenter repaints from; reading never writes state or proofs."""
    attempt = elder_kiln_attempt_pure(player_data)
    low, high = BANDS[attempt["band"] - 1]
    return {
        **attempt, "band_low": low, "band_high": high, "heat_bounds": HEAT_BOUNDS,
        "in_band": low <= attempt["heat"] <= high, "warnings": _helper_warnings(attempt),
        "events": tuple(events), "accepted": accepted,
        "can_offer": attempt["phase"] == "request", "can_play": attempt["phase"] in LIVE_PHASES,
        "can_retry": attempt["phase"] == "failed",
    }
