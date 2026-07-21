"""Pure entry, policy, completion, and exit mechanics for Werewolf Skullball."""

from __future__ import annotations

import copy
import re
from collections import Counter
from collections.abc import Mapping
from typing import Any

try:
    from .werewolf_skullball_data import (
        WEREWOLF_SKULLBALL_ACTIVITY_ID,
        WEREWOLF_SKULLBALL_DECAY_PER_EXCESS_MOVE,
        WEREWOLF_SKULLBALL_DEFAULT_ROUTE,
        WEREWOLF_SKULLBALL_FULL_XP_MOVE_BUDGET,
        WEREWOLF_SKULLBALL_MAX_XP,
        WEREWOLF_SKULLBALL_MOVES,
        WEREWOLF_SKULLBALL_RING_ITEMS,
        WEREWOLF_SKULLBALL_ROUTE_PRESETS,
    )
except ImportError:  # pragma: no cover - flat test imports
    from werewolf_skullball_data import (  # type: ignore
        WEREWOLF_SKULLBALL_ACTIVITY_ID,
        WEREWOLF_SKULLBALL_DECAY_PER_EXCESS_MOVE,
        WEREWOLF_SKULLBALL_DEFAULT_ROUTE,
        WEREWOLF_SKULLBALL_FULL_XP_MOVE_BUDGET,
        WEREWOLF_SKULLBALL_MAX_XP,
        WEREWOLF_SKULLBALL_MOVES,
        WEREWOLF_SKULLBALL_RING_ITEMS,
        WEREWOLF_SKULLBALL_ROUTE_PRESETS,
    )


WEREWOLF_SKULLBALL_STATE_VERSION = 1
_MAX_CUSTOM_MOVES = 80


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def normalize_skullball_plan_pure(value: Any) -> tuple[str, ...]:
    if isinstance(value, (tuple, list)):
        raw_tokens = [str(token).upper() for token in value]
    else:
        raw_tokens = [
            token
            for token in re.split(r"[\s,;/|>\-]+", str(value or "").upper())
            if token
        ]
    tokens = tuple(token for token in raw_tokens if token in WEREWOLF_SKULLBALL_MOVES)
    if len(tokens) != len(raw_tokens) or not 10 <= len(tokens) <= _MAX_CUSTOM_MOVES:
        return ()
    return tokens


def _preset_plan(route_id: str) -> tuple[str, ...]:
    return normalize_skullball_plan_pure(
        WEREWOLF_SKULLBALL_ROUTE_PRESETS[route_id]["plan"]
    )


def werewolf_skullball_plan_xp_pure(value: Any) -> int:
    plan = normalize_skullball_plan_pure(value)
    if not plan:
        return 0
    excess = max(0, len(plan) - WEREWOLF_SKULLBALL_FULL_XP_MOVE_BUDGET)
    return max(
        0,
        WEREWOLF_SKULLBALL_MAX_XP
        - excess * WEREWOLF_SKULLBALL_DECAY_PER_EXCESS_MOVE,
    )


def default_werewolf_skullball_state_pure() -> dict[str, Any]:
    return {
        "werewolf_skullball": {},
        "werewolf_skullball_policy": {
            "automation_mode": "casual",
            "route": WEREWOLF_SKULLBALL_DEFAULT_ROUTE,
            "advanced_plan": " ".join(_preset_plan(WEREWOLF_SKULLBALL_DEFAULT_ROUTE)),
        },
        "werewolf_skullball_runs_completed": 0,
        "werewolf_skullball_last_result": "Ready to enter",
    }


def sanitize_werewolf_skullball_policy_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    if mode not in {"casual", "advanced"}:
        mode = "casual"
    route = str(source.get("route", WEREWOLF_SKULLBALL_DEFAULT_ROUTE))
    if route not in WEREWOLF_SKULLBALL_ROUTE_PRESETS:
        route = WEREWOLF_SKULLBALL_DEFAULT_ROUTE
    advanced_plan = normalize_skullball_plan_pure(source.get("advanced_plan"))
    if not advanced_plan:
        advanced_plan = _preset_plan(route)
    return {
        "automation_mode": mode,
        "route": route,
        "advanced_plan": " ".join(advanced_plan),
    }


def sanitize_werewolf_skullball_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    route = str(raw.get("route", WEREWOLF_SKULLBALL_DEFAULT_ROUTE))
    if route not in WEREWOLF_SKULLBALL_ROUTE_PRESETS and route != "custom":
        route = WEREWOLF_SKULLBALL_DEFAULT_ROUTE
    plan = normalize_skullball_plan_pure(raw.get("plan"))
    if not plan:
        plan = _preset_plan(
            route if route in WEREWOLF_SKULLBALL_ROUTE_PRESETS else WEREWOLF_SKULLBALL_DEFAULT_ROUTE
        )
    mode = "advanced" if route == "custom" else "casual"
    return {
        "version": WEREWOLF_SKULLBALL_STATE_VERSION,
        "automation_mode": mode,
        "route": route,
        "plan": " ".join(plan),
    }


def sanitize_werewolf_skullball_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_werewolf_skullball_state_pure()
    session = sanitize_werewolf_skullball_session_pure(
        source.get("werewolf_skullball")
    )
    active_session = source.get("activity_session")
    active_id = (
        str(active_session.get("active_id", ""))
        if isinstance(active_session, Mapping)
        else ""
    )
    if session and active_id not in {"", WEREWOLF_SKULLBALL_ACTIVITY_ID}:
        session = {}
    return {
        "werewolf_skullball": session,
        "werewolf_skullball_policy": sanitize_werewolf_skullball_policy_pure(
            source.get("werewolf_skullball_policy")
        ),
        "werewolf_skullball_runs_completed": _int(
            source.get("werewolf_skullball_runs_completed")
        ),
        "werewolf_skullball_last_result": str(
            source.get(
                "werewolf_skullball_last_result",
                defaults["werewolf_skullball_last_result"],
            )
            or defaults["werewolf_skullball_last_result"]
        )[:320],
    }


def _quest_complete(player_data: Mapping[str, Any]) -> bool:
    quests = player_data.get("quests")
    quest = quests.get("creature_of_fenkenstrain") if isinstance(quests, Mapping) else None
    return isinstance(quest, Mapping) and bool(quest.get("completed"))


def _equipped_ring(player_data: Mapping[str, Any]) -> str:
    equipment = player_data.get("equipment")
    ring = str(equipment.get("ring", "")) if isinstance(equipment, Mapping) else ""
    accepted = {item.casefold() for item in WEREWOLF_SKULLBALL_RING_ITEMS}
    return ring if ring.casefold() in accepted else ""


def werewolf_skullball_locked_reasons_pure(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if _int(player_data.get("agility_level"), 1) < 25:
        reasons.append("Agility level 25")
    if not _quest_complete(player_data):
        reasons.append("complete Creature of Fenkenstrain")
    if not _equipped_ring(player_data):
        reasons.append("equip a Ring of Charos")
    return tuple(reasons)


def set_werewolf_skullball_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_werewolf_skullball_state_pure(data)
    if state["werewolf_skullball"]:
        return data, False, {"reason": "Finish the active run before changing its route."}
    body = dict(payload or {})
    current = state["werewolf_skullball_policy"]
    mode = str(body.get("automation_mode", current["automation_mode"]))
    route = str(body.get("route", current["route"]))
    if mode not in {"casual", "advanced"}:
        return data, False, {"reason": "Choose Casual or Advanced mode."}
    if route not in WEREWOLF_SKULLBALL_ROUTE_PRESETS:
        return data, False, {"reason": "Choose a valid Casual route."}
    plan = normalize_skullball_plan_pure(
        body.get("advanced_plan", current["advanced_plan"])
    )
    if mode == "advanced" and not plan:
        return data, False, {
            "reason": "Custom routes need 10–80 Tap/Kick/Shoot tokens (T, K, or S)."
        }
    if not plan:
        plan = _preset_plan(route)
    data["werewolf_skullball_policy"] = {
        "automation_mode": mode,
        "route": route,
        "advanced_plan": " ".join(plan),
    }
    label = "Custom" if mode == "advanced" else WEREWOLF_SKULLBALL_ROUTE_PRESETS[route]["label"]
    data["werewolf_skullball_last_result"] = f"Route policy set · {label}"
    return data, True, {"message": data["werewolf_skullball_last_result"]}


def enter_werewolf_skullball_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_werewolf_skullball_state_pure(data)
    if state["werewolf_skullball"]:
        return data, False, {"reason": "A Werewolf Skullball run is already active."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != WEREWOLF_SKULLBALL_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    locked = werewolf_skullball_locked_reasons_pure(data)
    if locked:
        return data, False, {"reason": ", ".join(locked), "locked_reasons": locked}

    policy = state["werewolf_skullball_policy"]
    advanced = policy["automation_mode"] == "advanced"
    route = "custom" if advanced else policy["route"]
    plan = (
        normalize_skullball_plan_pure(policy["advanced_plan"])
        if advanced
        else _preset_plan(policy["route"])
    )
    data.update(state)
    data["werewolf_skullball"] = {
        "version": WEREWOLF_SKULLBALL_STATE_VERSION,
        "automation_mode": policy["automation_mode"],
        "route": route,
        "plan": " ".join(plan),
    }
    data["activity_session"] = {"active_id": WEREWOLF_SKULLBALL_ACTIVITY_ID}
    data["current_utility"] = WEREWOLF_SKULLBALL_ACTIVITY_ID
    label = "Custom" if advanced else WEREWOLF_SKULLBALL_ROUTE_PRESETS[route]["label"]
    data["werewolf_skullball_last_result"] = f"Entered Werewolf Skullball · {label} route"
    return data, True, {"message": data["werewolf_skullball_last_result"], "route": route}


def _finish_session(data: dict[str, Any]) -> None:
    data["werewolf_skullball"] = {}
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == WEREWOLF_SKULLBALL_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}


def apply_werewolf_skullball_review_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    session = sanitize_werewolf_skullball_session_pure(
        data.get("werewolf_skullball")
    )
    if not session:
        return data, {"allowed": False, "reason": "Enter Werewolf Skullball before training."}
    plan = normalize_skullball_plan_pure(session["plan"])
    xp = werewolf_skullball_plan_xp_pure(plan)
    counts = Counter(plan)
    route = str(session["route"])
    if route in WEREWOLF_SKULLBALL_ROUTE_PRESETS:
        route_spec = WEREWOLF_SKULLBALL_ROUTE_PRESETS[route]
        label = str(route_spec["label"])
        character = str(route_spec["character"])
        notable = str(route_spec["notable"])
    else:
        label = "Custom"
        character = "player-authored route"
        notable = "bounded custom move plan"
    completions = dict(data.get("agility_activity_completions") or {})
    completions["skullball"] = _int(completions.get("skullball")) + 1
    data["agility_activity_completions"] = completions
    data["werewolf_skullball_runs_completed"] = _int(
        data.get("werewolf_skullball_runs_completed")
    ) + 1
    status = (
        f"Werewolf Skullball · {label} · {character} · {len(plan)} moves "
        f"({counts['T']} tap, {counts['K']} kick, {counts['S']} shoot) · "
        f"{notable} · {xp} Agility XP"
    )
    data["werewolf_skullball_last_result"] = status
    _finish_session(data)
    return data, {
        "allowed": True,
        "action_id": WEREWOLF_SKULLBALL_ACTIVITY_ID,
        "success": True,
        "expected_success_chance": 1.0,
        "xp": float(xp),
        "route": route,
        "plan": plan,
        "move_counts": dict(counts),
        "terminal": True,
        "completed_activity": True,
        "status": status,
    }


def leave_werewolf_skullball_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    session = sanitize_werewolf_skullball_session_pure(
        data.get("werewolf_skullball")
    )
    if not session:
        return data, False, {"reason": "No Werewolf Skullball run is active."}
    _finish_session(data)
    data["werewolf_skullball_last_result"] = "Left Werewolf Skullball before the run"
    return data, True, {"message": data["werewolf_skullball_last_result"]}


def werewolf_skullball_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_werewolf_skullball_state_pure(player_data)
    session = state["werewolf_skullball"]
    policy = state["werewolf_skullball_policy"]
    route = str(session.get("route", policy["route"]))
    if session:
        active_plan = normalize_skullball_plan_pure(session.get("plan"))
    elif policy["automation_mode"] == "advanced":
        active_plan = normalize_skullball_plan_pure(policy["advanced_plan"])
    else:
        active_plan = _preset_plan(policy["route"])
    label = (
        "Custom"
        if route == "custom" or policy["automation_mode"] == "advanced"
        else WEREWOLF_SKULLBALL_ROUTE_PRESETS[route]["label"]
    )
    return {
        "active": bool(session),
        "can_review": bool(session),
        "locked_reasons": werewolf_skullball_locked_reasons_pure(player_data),
        "automation_mode": str(session.get("automation_mode", policy["automation_mode"])),
        "route": route if route in WEREWOLF_SKULLBALL_ROUTE_PRESETS else policy["route"],
        "route_label": label,
        "advanced_plan": policy["advanced_plan"],
        "active_move_count": len(active_plan),
        "projected_xp": werewolf_skullball_plan_xp_pure(active_plan),
        "runs_completed": state["werewolf_skullball_runs_completed"],
        "last_result": state["werewolf_skullball_last_result"],
        "equipped_ring": _equipped_ring(player_data),
    }
