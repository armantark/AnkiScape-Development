"""Pure Phase-3 cadence shadow telemetry.

Shadow mode advances exact rate envelopes and records what the cadence kernel
would have admitted, but it never supplies an outcome to live gameplay.  Its
state is deliberately separate from ``cadence_profiles`` so a later migration
cannot inherit observational credit as live progress.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping

from ..logic.cadence_kernel import (
    CAP_ONE_ACTION,
    R,
    advance_cadence_pure,
    default_cadence_profile_state_pure,
    rate_limited_profile_pure,
    sanitize_cadence_profile_state_pure,
)
from ..tools.sourced_xp_rates import BY_SKILL


SHADOW_VERSION = 1
SHADOW_STATE_KEY = "cadence_shadow"
SOURCE_READY = "sourced"
SOURCE_BLOCKED = "source_blocked"
BOTH_EMIT = "both_emit"
NEITHER_EMIT = "neither_emit"
RANGE_SPLIT = "range_split"

_SKILL_NAMES = {
    "mining": "Mining",
    "woodcutting": "Woodcutting",
    "fishing": "Fishing",
    "hunter": "Hunter",
    "cooking": "Cooking",
    "firemaking": "Firemaking",
}

# Runtime selections and the rate ledger do not always use the same identity.
# Every non-identical mapping below is pinned by the cited row's action wording;
# anything not listed remains source_blocked rather than being guessed.
_SOURCE_ROUTE_KEYS = {
    "mining": {
        "iron": "iron",
        "concentrated_gold": "gold",
    },
    "woodcutting": {
        "tree": "tree",
        "oak": "oak",
        "willow": "willow",
        "maple": "maple",
        "yew": "yew",
        "magic": "magic",
        "ivy": "ivy",
    },
    "fishing": {
        "catch_sharks": "shark",
        "catch_monkfish": "monkfish",
        "catch_trout_salmon": "trout",
        "catch_rocktail": "rocktail",
    },
    "hunter": {
        "catch_red_chinchompa": "catch_red_chinchompa",
        "catch_chinchompa": "catch_chinchompa",
        "catch_red_salamander": "catch_red_salamander",
        "catch_black_salamander": "catch_black_salamander",
        "catch_orange_salamander": "catch_orange_salamander",
        "catch_dark_kebbit": "catch_dark_kebbit",
        "catch_spotted_kebbit": "catch_spotted_kebbit",
        "barehand_black_warlock": "barehand_black_warlock",
    },
    "cooking": {
        "cook_lobster": "cook_lobster",
        "cook_monkfish": "cook_monkfish",
        "cook_shark": "cook_shark",
        "cook_tuna": "cook_tuna",
    },
    "firemaking": {"magic_logs": "magic_logs"},
}

_BLOCKED_REASONS = {
    ("mining", "gold"): "the pinned gold rate is concentrated gold, not the ordinary gold-rock route",
    ("mining", "runite"): "the pre-cutoff record gives only coins/hour, not XP/hour",
    ("fishing", "catch_rocktail"): "the quote includes an undecomposable urn contribution",
    ("fishing", "catch_leaping_fish"): "the live mixed route is not compatible with the sturgeon-only rate",
    ("hunter", "catch_black_warlock"): "the available rate is for barehand catching, not the net route",
}

_EMBEDDED_OUTCOME_SKILLS = frozenset({"cooking", "firemaking"})
_EXPLICIT_OVERFLOW_PROFILES = frozenset(
    {
        "mining:iron",
        "cooking:cook_lobster",
        "cooking:cook_monkfish",
        "cooking:cook_shark",
        "cooking:cook_tuna",
        "firemaking:magic_logs",
    }
)


def _non_negative_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool) or isinstance(value, float):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return parsed if parsed >= 0 else default


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool) or value is None:
        return Fraction(0, 1)
    if isinstance(value, (tuple, list)) and len(value) == 2:
        numerator = _non_negative_int(value[0])
        denominator = _non_negative_int(value[1], 1)
        return Fraction(numerator, denominator or 1)
    try:
        return max(Fraction(str(value)), Fraction(0, 1))
    except (ValueError, TypeError, ZeroDivisionError):
        return Fraction(0, 1)


def fraction_pair_pure(value: Any) -> list[int]:
    exact = _fraction(value)
    return [exact.numerator, exact.denominator]


def _add_fraction_pair(left: Any, right: Any) -> list[int]:
    return fraction_pair_pure(_fraction(left) + _fraction(right))


def default_cadence_shadow_state_pure() -> dict[str, Any]:
    return {"version": SHADOW_VERSION, "profiles": {}, "routes": {}}


def sanitize_cadence_shadow_state_pure(raw_state: Any) -> dict[str, Any]:
    state = default_cadence_shadow_state_pure()
    if not isinstance(raw_state, Mapping):
        return state

    raw_profiles = raw_state.get("profiles", {})
    if isinstance(raw_profiles, Mapping):
        for profile_id, raw_envelope in raw_profiles.items():
            if not isinstance(profile_id, str) or not profile_id or not isinstance(raw_envelope, Mapping):
                continue
            state["profiles"][profile_id] = {
                "low": sanitize_cadence_profile_state_pure(raw_envelope.get("low", {})),
                "high": sanitize_cadence_profile_state_pure(raw_envelope.get("high", {})),
            }

    raw_routes = raw_state.get("routes", {})
    if isinstance(raw_routes, Mapping):
        for profile_id, raw_route in raw_routes.items():
            if not isinstance(profile_id, str) or not profile_id or not isinstance(raw_route, Mapping):
                continue
            allowed = {
                "profile_id",
                "skill_id",
                "action_id",
                "source_status",
                "source_blocked_reason",
                "source_key",
                "source_level",
                "source_includes",
                "source_citation",
                "low_actions_per_hour",
                "high_actions_per_hour",
                "low_overflow_policy",
                "high_overflow_policy",
                "last_proposed_decision",
                "assigned_reviews",
                "live_successes",
                "live_failures",
                "proposed_low_emissions",
                "proposed_high_emissions",
                "range_splits",
                "live_xp",
                "proposed_low_xp",
                "proposed_high_xp",
                "source_low_xp_hour",
                "source_high_xp_hour",
                "source_xp_per_action",
            }
            route = {key: raw_route[key] for key in allowed if key in raw_route}
            for key in (
                "assigned_reviews",
                "live_successes",
                "live_failures",
                "proposed_low_emissions",
                "proposed_high_emissions",
                "range_splits",
            ):
                route[key] = _non_negative_int(route.get(key, 0))
            for key in (
                "live_xp",
                "proposed_low_xp",
                "proposed_high_xp",
                "source_low_xp_hour",
                "source_high_xp_hour",
                "source_xp_per_action",
                "low_actions_per_hour",
                "high_actions_per_hour",
            ):
                route[key] = fraction_pair_pure(route.get(key, (0, 1)))
            route["source_level"] = _non_negative_int(route.get("source_level", 0))
            route["source_includes"] = [
                str(value) for value in route.get("source_includes", ()) if isinstance(value, str)
            ]
            for key in ("source_key", "source_citation", "source_blocked_reason", "last_proposed_decision"):
                route[key] = str(route.get(key, "")) if isinstance(route.get(key, ""), str) else ""
            for key in ("low_overflow_policy", "high_overflow_policy"):
                route[key] = CAP_ONE_ACTION if route.get(key) == CAP_ONE_ACTION else None
            route["skill_id"] = str(route.get("skill_id", profile_id.split(":", 1)[0]))
            route["action_id"] = str(route.get("action_id", profile_id.split(":", 1)[-1]))
            route["profile_id"] = profile_id
            route["source_status"] = (
                SOURCE_READY if route.get("source_status") == SOURCE_READY else SOURCE_BLOCKED
            )
            state["routes"][profile_id] = route
    return state


def _base_xp_hour_fraction(rate: Any, value: int) -> Fraction:
    divisor = Fraction(6, 5) if "urns" in rate.includes else Fraction(1, 1)
    return Fraction(int(value), 1) / divisor


def resolve_cadence_shadow_rate_pure(skill_id: str, action_id: str) -> dict[str, Any]:
    skill_key = str(skill_id).lower()
    action_key = str(action_id)
    profile_id = f"{skill_key}:{action_key}"
    skill_name = _SKILL_NAMES.get(skill_key)
    source_key = _SOURCE_ROUTE_KEYS.get(skill_key, {}).get(action_key)
    blocked_reason = _BLOCKED_REASONS.get((skill_key, action_key))
    if skill_name is None or source_key is None:
        return {
            "profile_id": profile_id,
            "skill_id": skill_key,
            "action_id": action_key,
            "source_status": SOURCE_BLOCKED,
            "source_blocked_reason": blocked_reason or "no compatible pre-cutoff XP/hour rate",
        }

    rate = BY_SKILL.get(skill_name, {}).get(source_key)
    if rate is None:
        return {
            "profile_id": profile_id,
            "skill_id": skill_key,
            "action_id": action_key,
            "source_status": SOURCE_BLOCKED,
            "source_blocked_reason": "no compatible pre-cutoff XP/hour rate",
        }

    if (skill_key, action_key) == ("fishing", "catch_rocktail"):
        # The only honest display is the quoted urn-inclusive 48k.  The ledger
        # explicitly forbids decomposing it into a cadence-setting base rate.
        source_low = Fraction(rate.low_xp_hr, 1)
        source_high = Fraction(rate.high_xp_hr, 1)
    else:
        source_low = _base_xp_hour_fraction(rate, rate.low_xp_hr)
        source_high = _base_xp_hour_fraction(rate, rate.high_xp_hr)
    xp_per_action = _fraction(rate.xp_per_action)
    low_actions = source_low / xp_per_action
    high_actions = source_high / xp_per_action
    uses_rate_profile = skill_key not in _EMBEDDED_OUTCOME_SKILLS
    low_overflow_policy = (
        CAP_ONE_ACTION if low_actions > R and profile_id in _EXPLICIT_OVERFLOW_PROFILES else None
    )
    high_overflow_policy = (
        CAP_ONE_ACTION if high_actions > R and profile_id in _EXPLICIT_OVERFLOW_PROFILES else None
    )
    if uses_rate_profile and high_actions > R and profile_id not in _EXPLICIT_OVERFLOW_PROFILES:
        blocked_reason = (
            f"{high_actions.numerator}/{high_actions.denominator} actions/hour exceeds R without an approved overflow"
        )
    return {
        "profile_id": profile_id,
        "skill_id": skill_key,
        "action_id": action_key,
        "source_status": SOURCE_BLOCKED if blocked_reason else SOURCE_READY,
        "source_blocked_reason": blocked_reason or "",
        "source_key": source_key,
        "source_low_xp_hour": fraction_pair_pure(source_low),
        "source_high_xp_hour": fraction_pair_pure(source_high),
        "source_xp_per_action": fraction_pair_pure(xp_per_action),
        "source_level": int(rate.level),
        "source_includes": list(rate.includes),
        "source_citation": str(rate.citation),
        "low_actions_per_hour": fraction_pair_pure(low_actions),
        "high_actions_per_hour": fraction_pair_pure(high_actions),
        "low_overflow_policy": low_overflow_policy,
        "high_overflow_policy": high_overflow_policy,
    }


def _profile_for_bound(profile_id: str, actions_per_hour: Fraction, overflow_policy: Any = None):
    return rate_limited_profile_pure(
        profile_id,
        actions_per_hour.numerator,
        actions_per_hour.denominator,
        overflow_policy=overflow_policy,
    )


def record_cadence_shadow_pure(
    player_data: dict[str, Any],
    skill_id: str,
    action_id: str,
    live_success: bool,
    *,
    live_xp: Any = 0,
    proposed_outcome_success: Any = None,
) -> dict[str, Any]:
    """Record one completed live attempt and return its shadow aggregate row."""

    if str(skill_id).lower() not in _SKILL_NAMES:
        return {}

    state = sanitize_cadence_shadow_state_pure(player_data.get(SHADOW_STATE_KEY))
    player_data[SHADOW_STATE_KEY] = state
    resolved = resolve_cadence_shadow_rate_pure(skill_id, action_id)
    profile_id = resolved["profile_id"]
    routes = state["routes"]
    route = routes.setdefault(
        profile_id,
        {
            **resolved,
            "assigned_reviews": 0,
            "live_successes": 0,
            "live_failures": 0,
            "live_xp": [0, 1],
            "proposed_low_emissions": 0,
            "proposed_high_emissions": 0,
            "proposed_low_xp": [0, 1],
            "proposed_high_xp": [0, 1],
            "range_splits": 0,
        },
    )
    route["assigned_reviews"] += 1
    route["live_successes" if live_success else "live_failures"] += 1
    route["live_xp"] = _add_fraction_pair(route.get("live_xp"), live_xp)

    if resolved["source_status"] != SOURCE_READY:
        route["last_proposed_decision"] = SOURCE_BLOCKED
        return route

    if resolved["skill_id"] in _EMBEDDED_OUTCOME_SKILLS:
        proposed_success = bool(proposed_outcome_success)
        emitted = int(proposed_success)
        route["proposed_low_emissions"] += emitted
        route["proposed_high_emissions"] += emitted
        if proposed_success:
            source_xp = resolved["source_xp_per_action"]
            route["proposed_low_xp"] = _add_fraction_pair(route.get("proposed_low_xp"), source_xp)
            route["proposed_high_xp"] = _add_fraction_pair(route.get("proposed_high_xp"), source_xp)
        route["last_proposed_decision"] = BOTH_EMIT if proposed_success else NEITHER_EMIT
        return route

    profiles = state["profiles"].setdefault(
        profile_id,
        {
            "low": default_cadence_profile_state_pure(opening_ready=False),
            "high": default_cadence_profile_state_pure(opening_ready=False),
        },
    )
    low_rate = _fraction(resolved["low_actions_per_hour"])
    high_rate = _fraction(resolved["high_actions_per_hour"])
    low_step = advance_cadence_pure(
        _profile_for_bound(f"{profile_id}:low", low_rate, resolved.get("low_overflow_policy")),
        profiles["low"],
    )
    high_step = advance_cadence_pure(
        _profile_for_bound(f"{profile_id}:high", high_rate, resolved.get("high_overflow_policy")),
        profiles["high"],
    )
    profiles["low"] = low_step.state
    profiles["high"] = high_step.state

    route["proposed_low_emissions"] += int(low_step.emitted)
    route["proposed_high_emissions"] += int(high_step.emitted)
    source_xp = resolved["source_xp_per_action"]
    if low_step.emitted:
        route["proposed_low_xp"] = _add_fraction_pair(route.get("proposed_low_xp"), source_xp)
    if high_step.emitted:
        route["proposed_high_xp"] = _add_fraction_pair(route.get("proposed_high_xp"), source_xp)

    if low_step.emitted and high_step.emitted:
        decision = BOTH_EMIT
    elif not low_step.emitted and not high_step.emitted:
        decision = NEITHER_EMIT
    else:
        decision = RANGE_SPLIT
        route["range_splits"] += 1
    route["last_proposed_decision"] = decision
    return route


def cadence_shadow_report_rows_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    state = sanitize_cadence_shadow_state_pure(player_data.get(SHADOW_STATE_KEY))
    rows = []
    for profile_id, route in sorted(state["routes"].items()):
        assigned = route["assigned_reviews"]
        current = (_fraction(route["live_xp"]) * R / assigned) if assigned else Fraction(0, 1)
        proposed_low = (
            _fraction(route["proposed_low_xp"]) * R / assigned if assigned else Fraction(0, 1)
        )
        proposed_high = (
            _fraction(route["proposed_high_xp"]) * R / assigned if assigned else Fraction(0, 1)
        )
        rows.append(
            {
                **route,
                "profile_id": profile_id,
                "current_xp_hour": fraction_pair_pure(current),
                "proposed_low_xp_hour": fraction_pair_pure(proposed_low),
                "proposed_high_xp_hour": fraction_pair_pure(proposed_high),
            }
        )
    return tuple(rows)
