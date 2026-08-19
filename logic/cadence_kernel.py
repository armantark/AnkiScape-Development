"""Pure foreground-action cadence contracts and exact residual scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, Mapping, Optional


R = 1000
CADENCE_VERSION = 1

PASSTHROUGH = "passthrough"
RATE_LIMITED = "rate_limited"
EMBEDDED_PROBABILITY = "embedded_probability"
COMBAT_TICKS = "combat_ticks"
ADMISSION_MODES = frozenset(
    {PASSTHROUGH, RATE_LIMITED, EMBEDDED_PROBABILITY, COMBAT_TICKS}
)

CAP_ONE_ACTION = "cap_one_action"
OVERFLOW_POLICIES = frozenset({CAP_ONE_ACTION})

CADENCE_WAIT = "cadence_wait"
OPPORTUNITY = "opportunity"


@dataclass(frozen=True)
class CadenceProfile:
    """Immutable cadence contract for one selectable action route."""

    profile_id: str
    mode: str
    increment_numerator: int = 1
    threshold_denominator: int = 1
    cadence_version: int = CADENCE_VERSION
    overflow_policy: Optional[str] = None


@dataclass(frozen=True)
class CadenceStepResult:
    """Result of advancing one active profile by one eligible review."""

    outcome: str
    emitted: bool
    state: Dict[str, Any]


@dataclass(frozen=True)
class ResourceLock:
    """A route-local unavailable resource that does not lock the actor."""

    resource_id: str
    reason: str = ""


@dataclass(frozen=True)
class ActorLock:
    """An actor commitment that prevents switching to another route."""

    actor_id: str
    reason: str = ""


def _integer(value: Any, *, minimum: int, default: int) -> int:
    if isinstance(value, bool) or isinstance(value, float):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return parsed if parsed >= minimum else default


def _require_integer(name: str, value: Any, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer greater than or equal to {minimum}")
    return value


def sanitize_cadence_kernel_enabled_pure(value: Any, default: bool = False) -> bool:
    """Return a strict boolean feature flag using the caller's declared default."""

    return value if isinstance(value, bool) else bool(default)


def default_cadence_profile_state_pure(
    *,
    opening_ready: bool = True,
    cadence_version: int = CADENCE_VERSION,
) -> Dict[str, Any]:
    """Return a new serializable residual state for one cadence profile."""

    return {
        "credit": 0,
        "opening_ready": bool(opening_ready),
        "assigned_reviews": 0,
        "opportunities_emitted": 0,
        "cadence_version": _integer(
            cadence_version,
            minimum=1,
            default=CADENCE_VERSION,
        ),
    }


def sanitize_cadence_profile_state_pure(raw_state: Any) -> Dict[str, Any]:
    """Sanitize the five persisted fields for one profile without floats."""

    state = default_cadence_profile_state_pure()
    if not isinstance(raw_state, Mapping):
        return state
    state["credit"] = _integer(raw_state.get("credit"), minimum=0, default=0)
    opening_ready = raw_state.get("opening_ready")
    state["opening_ready"] = opening_ready if isinstance(opening_ready, bool) else True
    state["assigned_reviews"] = _integer(
        raw_state.get("assigned_reviews"), minimum=0, default=0
    )
    state["opportunities_emitted"] = _integer(
        raw_state.get("opportunities_emitted"), minimum=0, default=0
    )
    state["cadence_version"] = _integer(
        raw_state.get("cadence_version"),
        minimum=1,
        default=CADENCE_VERSION,
    )
    return state


def default_cadence_kernel_state_pure() -> Dict[str, Dict[str, Any]]:
    """Return the route-keyed persisted kernel state for a new player."""

    return {}


def sanitize_cadence_kernel_state_pure(raw_state: Any) -> Dict[str, Dict[str, Any]]:
    """Sanitize saved profile states while retaining every valid profile id."""

    if not isinstance(raw_state, Mapping):
        return default_cadence_kernel_state_pure()
    return {
        profile_id: sanitize_cadence_profile_state_pure(profile_state)
        for profile_id, profile_state in raw_state.items()
        if isinstance(profile_id, str) and profile_id and isinstance(profile_state, Mapping)
    }


def validate_overflow_policy_pure(
    actions_per_hour_numerator: int,
    actions_per_hour_denominator: int = 1,
    *,
    overflow_policy: Optional[str] = None,
) -> None:
    """Reject a source rate above ``R`` unless it declares ``cap_one_action``."""

    numerator = _require_integer(
        "actions_per_hour_numerator", actions_per_hour_numerator, minimum=1
    )
    denominator = _require_integer(
        "actions_per_hour_denominator", actions_per_hour_denominator, minimum=1
    )
    if overflow_policy is not None and overflow_policy not in OVERFLOW_POLICIES:
        raise ValueError(f"unknown overflow policy: {overflow_policy}")
    if numerator > R * denominator and overflow_policy != CAP_ONE_ACTION:
        raise ValueError(
            f"rates above {R} actions/hour must declare {CAP_ONE_ACTION}"
        )


def rate_limited_profile_pure(
    profile_id: str,
    actions_per_hour_numerator: int,
    actions_per_hour_denominator: int = 1,
    *,
    cadence_version: int = CADENCE_VERSION,
    overflow_policy: Optional[str] = None,
) -> CadenceProfile:
    """Build an exact rate-limited profile from an integer/rational hourly rate."""

    validate_overflow_policy_pure(
        actions_per_hour_numerator,
        actions_per_hour_denominator,
        overflow_policy=overflow_policy,
    )
    source_rate = Fraction(
        _require_integer(
            "actions_per_hour_numerator", actions_per_hour_numerator, minimum=1
        ),
        _require_integer(
            "actions_per_hour_denominator", actions_per_hour_denominator, minimum=1
        ),
    )
    if source_rate > R:
        increment_numerator = threshold_denominator = 1
    else:
        per_review = source_rate / R
        increment_numerator = per_review.numerator
        threshold_denominator = per_review.denominator
    profile = CadenceProfile(
        profile_id=profile_id,
        mode=RATE_LIMITED,
        increment_numerator=increment_numerator,
        threshold_denominator=threshold_denominator,
        cadence_version=cadence_version,
        overflow_policy=overflow_policy,
    )
    validate_cadence_profile_pure(profile)
    return profile


def validate_cadence_profile_pure(profile: CadenceProfile) -> None:
    """Validate a profile before any residual state is advanced."""

    if not isinstance(profile, CadenceProfile):
        raise ValueError("profile must be a CadenceProfile")
    if not isinstance(profile.profile_id, str) or not profile.profile_id:
        raise ValueError("profile_id must be a non-empty string")
    if profile.mode not in ADMISSION_MODES:
        raise ValueError(f"unknown admission mode: {profile.mode}")
    numerator = _require_integer(
        "increment_numerator", profile.increment_numerator, minimum=0
    )
    denominator = _require_integer(
        "threshold_denominator", profile.threshold_denominator, minimum=1
    )
    _require_integer("cadence_version", profile.cadence_version, minimum=1)
    if profile.overflow_policy is not None and profile.overflow_policy not in OVERFLOW_POLICIES:
        raise ValueError(f"unknown overflow policy: {profile.overflow_policy}")
    if profile.mode in (PASSTHROUGH, EMBEDDED_PROBABILITY) and (
        numerator,
        denominator,
    ) != (1, 1):
        raise ValueError(f"{profile.mode} profiles must use a 1/1 frequency")
    if profile.mode == RATE_LIMITED:
        if numerator < 1:
            raise ValueError("rate_limited profiles require a positive numerator")
        if numerator > denominator:
            raise ValueError("rate_limited profiles cannot exceed one opportunity per review")
    if profile.overflow_policy == CAP_ONE_ACTION and (numerator, denominator) != (1, 1):
        raise ValueError("cap_one_action profiles must use the capped 1/1 frequency")


def advance_cadence_pure(
    profile: CadenceProfile,
    raw_state: Mapping[str, Any],
) -> CadenceStepResult:
    """Advance one active profile for one eligible successful review."""

    validate_cadence_profile_pure(profile)
    state = sanitize_cadence_profile_state_pure(raw_state)
    state["credit"] = min(state["credit"], profile.threshold_denominator - 1)
    if state["cadence_version"] != profile.cadence_version:
        raise ValueError("persisted cadence_version does not match the profile")

    state["assigned_reviews"] += 1
    emitted = profile.mode in (PASSTHROUGH, EMBEDDED_PROBABILITY, COMBAT_TICKS)
    if profile.mode == RATE_LIMITED:
        if state["opening_ready"]:
            state["opening_ready"] = False
            emitted = True
        else:
            state["credit"] += profile.increment_numerator
            if state["credit"] >= profile.threshold_denominator:
                state["credit"] -= profile.threshold_denominator
                emitted = True

    if emitted:
        state["opportunities_emitted"] += 1
    return CadenceStepResult(
        outcome=OPPORTUNITY if emitted else CADENCE_WAIT,
        emitted=emitted,
        state=state,
    )
