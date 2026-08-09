"""Pure Fishing Trawler entry, pressure, duty, haul, and policy mechanics."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.fishing_trawler_data import (
    FISHING_TRAWLER_ACTIVITY_ID,
    FISHING_TRAWLER_BAIL_AMOUNT,
    FISHING_TRAWLER_COMMON_CATCHES,
    FISHING_TRAWLER_CREW_WATER_OFFSET,
    FISHING_TRAWLER_DEFAULT_LAYOUT,
    FISHING_TRAWLER_DUTIES,
    FISHING_TRAWLER_EVENT_REVIEWS,
    FISHING_TRAWLER_LAYOUT_CAPACITY,
    FISHING_TRAWLER_PASTE_PER_LEAK,
    FISHING_TRAWLER_PRESSURE_EVENTS,
    FISHING_TRAWLER_SINK_WATER,
    FISHING_TRAWLER_TIGER_SHARK,
    FISHING_TRAWLER_TIGER_SHARK_TRIP_CHANCE,
)


FISHING_TRAWLER_STATE_VERSION = 1
_VALID_MODES = frozenset({"casual", "advanced"})
_VALID_PRIORITIES = frozenset(key for key, _label in FISHING_TRAWLER_DUTIES)


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _roll(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        parsed = 0.5
    return max(0.0, min(parsed, 0.999999))


def default_fishing_trawler_state_pure() -> dict[str, Any]:
    return {
        "fishing_trawler": {},
        "fishing_trawler_policy": {
            "automation_mode": "casual",
            "priority": "balanced",
            "layout": dict(FISHING_TRAWLER_DEFAULT_LAYOUT),
        },
        "fishing_trawler_trips_completed": 0,
        "fishing_trawler_trips_sunk": 0,
        "fishing_trawler_last_result": "",
    }


def sanitize_fishing_trawler_policy_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    if mode not in _VALID_MODES:
        mode = "casual"
    priority = str(source.get("priority", "balanced"))
    if priority not in _VALID_PRIORITIES:
        priority = "balanced"
    raw_layout = source.get("layout")
    layout_source = raw_layout if isinstance(raw_layout, Mapping) else {}
    return {
        "automation_mode": mode,
        "priority": priority,
        "layout": {
            item: _int(layout_source.get(item, quantity), maximum=9999)
            for item, quantity in FISHING_TRAWLER_DEFAULT_LAYOUT.items()
        },
    }


def sanitize_fishing_trawler_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    supplies = raw.get("supplies")
    supply_source = supplies if isinstance(supplies, Mapping) else {}
    mode = str(raw.get("automation_mode", "casual"))
    priority = str(raw.get("priority", "balanced"))
    return {
        "version": FISHING_TRAWLER_STATE_VERSION,
        "review": _int(raw.get("review"), maximum=FISHING_TRAWLER_EVENT_REVIEWS - 1),
        "water": _int(raw.get("water"), maximum=FISHING_TRAWLER_SINK_WATER),
        "leaks": _int(raw.get("leaks"), maximum=20),
        "net_intact": bool(raw.get("net_intact", True)),
        "contribution": _int(raw.get("contribution"), maximum=999),
        "haul_quality": _int(raw.get("haul_quality"), maximum=999),
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "priority": priority if priority in _VALID_PRIORITIES else "balanced",
        "supplies": {
            item: _int(supply_source.get(item), maximum=9999)
            for item in FISHING_TRAWLER_DEFAULT_LAYOUT
        },
    }


def sanitize_fishing_trawler_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    session = sanitize_fishing_trawler_session_pure(source.get("fishing_trawler"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", FISHING_TRAWLER_ACTIVITY_ID}:
        session = {}
    return {
        "fishing_trawler": session,
        "fishing_trawler_policy": sanitize_fishing_trawler_policy_pure(
            source.get("fishing_trawler_policy")
        ),
        "fishing_trawler_trips_completed": _int(
            source.get("fishing_trawler_trips_completed")
        ),
        "fishing_trawler_trips_sunk": _int(source.get("fishing_trawler_trips_sunk")),
        "fishing_trawler_last_result": str(
            source.get("fishing_trawler_last_result", "") or ""
        )[:400],
    }


def set_fishing_trawler_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_fishing_trawler_state_pure rebuilds all its
    # keys, and inventory is rebuilt with dict() before the haul is added.
    data = dict(player_data)
    state = sanitize_fishing_trawler_state_pure(data)
    if state["fishing_trawler"]:
        return data, False, {"reason": "Finish or leave the current trip first."}
    body = dict(payload or {})
    candidate = dict(state["fishing_trawler_policy"])
    candidate.update(
        {
            key: body[key]
            for key in ("automation_mode", "priority", "layout")
            if key in body
        }
    )
    policy = sanitize_fishing_trawler_policy_pure(candidate)
    slots = fishing_trawler_layout_slots_pure(policy["layout"])
    if slots > FISHING_TRAWLER_LAYOUT_CAPACITY:
        return data, False, {
            "reason": (
                f"That layout uses {slots}/{FISHING_TRAWLER_LAYOUT_CAPACITY} slots. "
                "Swamp paste stacks; rope and bailing buckets do not."
            )
        }
    data.update(state)
    data["fishing_trawler_policy"] = policy
    return data, True, {"message": "Fishing Trawler plan saved.", "policy": policy}


def fishing_trawler_layout_slots_pure(layout: Mapping[str, Any]) -> int:
    paste_slots = 1 if _int(layout.get("Swamp paste")) > 0 else 0
    return (
        paste_slots
        + _int(layout.get("Rope"), maximum=FISHING_TRAWLER_LAYOUT_CAPACITY)
        + _int(
            layout.get("Bailing bucket"),
            maximum=FISHING_TRAWLER_LAYOUT_CAPACITY,
        )
    )


def _return_supplies(data: dict[str, Any], supplies: Mapping[str, Any]) -> None:
    inventory = dict(data.get("inventory") or {})
    for item in FISHING_TRAWLER_DEFAULT_LAYOUT:
        quantity = _int(supplies.get(item))
        if quantity:
            inventory[item] = _int(inventory.get(item)) + quantity
    data["inventory"] = inventory


def _finish_trip(data: dict[str, Any], supplies: Mapping[str, Any]) -> None:
    _return_supplies(data, supplies)
    data["fishing_trawler"] = {}
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == FISHING_TRAWLER_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}


def enter_fishing_trawler_pure(
    player_data: Mapping[str, Any],
    policy_payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if policy_payload:
        data, ok, info = set_fishing_trawler_policy_pure(
            player_data, policy_payload
        )
        if not ok:
            return data, False, info
    else:
        # Shallow on purpose: sanitize_fishing_trawler_state_pure rebuilds all
        # its keys, and inventory is rebuilt with dict() before the haul is
        # added.
        data = dict(player_data)
    state = sanitize_fishing_trawler_state_pure(data)
    if state["fishing_trawler"]:
        return data, False, {"reason": "A Fishing Trawler trip is already active."}
    if _int(data.get("fishing_level"), 1) < 15:
        return data, False, {"reason": "Requires level 15 Fishing."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != FISHING_TRAWLER_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}

    policy = state["fishing_trawler_policy"]
    inventory = dict(data.get("inventory") or {})
    requested = policy["layout"]
    supplies = {
        item: min(_int(inventory.get(item)), _int(requested.get(item)))
        for item in FISHING_TRAWLER_DEFAULT_LAYOUT
    }
    for item, quantity in supplies.items():
        remaining = _int(inventory.get(item)) - quantity
        if remaining:
            inventory[item] = remaining
        else:
            inventory.pop(item, None)
    data.update(state)
    data["inventory"] = inventory
    data["fishing_trawler"] = {
        "version": FISHING_TRAWLER_STATE_VERSION,
        "review": 0,
        "water": 0,
        "leaks": 0,
        "net_intact": True,
        "contribution": 0,
        "haul_quality": 0,
        "automation_mode": policy["automation_mode"],
        "priority": policy["priority"],
        "supplies": supplies,
    }
    data["activity_session"] = {"active_id": FISHING_TRAWLER_ACTIVITY_ID}
    data["current_utility"] = FISHING_TRAWLER_ACTIVITY_ID
    data["fishing_trawler_last_result"] = "Boarded the Fishing Trawler · first swell ready"
    return data, True, {
        "message": data["fishing_trawler_last_result"],
        "supplies": supplies,
    }


def _available_actions(session: Mapping[str, Any]) -> set[str]:
    supplies = session["supplies"]
    actions = {"fish"}
    if int(session["leaks"]) > 0 and int(supplies["Swamp paste"]) >= FISHING_TRAWLER_PASTE_PER_LEAK:
        actions.add("repair_leak")
    if int(session["water"]) > 0 and int(supplies["Bailing bucket"]) > 0:
        actions.add("bail")
    if not bool(session["net_intact"]) and int(supplies["Rope"]) > 0:
        actions.add("repair_net")
    return actions


def _choose_duty(session: Mapping[str, Any]) -> str:
    available = _available_actions(session)
    water = int(session["water"])
    leaks = int(session["leaks"])
    net_intact = bool(session["net_intact"])
    mode = str(session["automation_mode"])
    priority = str(session["priority"])

    if mode == "casual" or priority == "balanced":
        order = (
            ("bail", water >= 70),
            ("repair_leak", leaks >= 2),
            ("repair_net", not net_intact),
            ("bail", water >= 45),
            ("repair_leak", leaks > 0),
            ("fish", True),
        )
    elif priority == "water_first":
        order = (("bail", water >= 30), ("repair_leak", leaks > 0), ("repair_net", not net_intact), ("fish", True))
    elif priority == "maintenance_first":
        order = (("repair_leak", leaks > 0), ("repair_net", not net_intact), ("bail", water >= 45), ("fish", True))
    else:
        order = (("bail", water >= 85), ("repair_leak", leaks >= 3), ("repair_net", not net_intact and water >= 70), ("fish", True))
    for action, useful in order:
        if useful and action in available:
            return action
    return "fish"


def _apply_duty(session: dict[str, Any], duty: str) -> None:
    supplies = session["supplies"]
    if duty == "repair_leak":
        supplies["Swamp paste"] -= FISHING_TRAWLER_PASTE_PER_LEAK
        session["leaks"] -= 1
        session["water"] = max(0, int(session["water"]) - 8)
        session["contribution"] += 3
        session["haul_quality"] += 1
    elif duty == "bail":
        session["water"] = max(0, int(session["water"]) - FISHING_TRAWLER_BAIL_AMOUNT)
        session["contribution"] += 2
        session["haul_quality"] += 1
    elif duty == "repair_net":
        supplies["Rope"] -= 1
        session["net_intact"] = True
        session["contribution"] += 3
        session["haul_quality"] += 1
    else:
        session["contribution"] += 1
        if session["net_intact"]:
            session["haul_quality"] += 3


def _award_haul(
    data: dict[str, Any], session: Mapping[str, Any], reward_roll: Any
) -> tuple[dict[str, int], float]:
    level = max(1, _int(data.get("fishing_level"), 1, maximum=99))
    eligible = tuple(
        catch for catch in FISHING_TRAWLER_COMMON_CATCHES if level >= catch.level
    )
    if not eligible:
        return {}, 0.0
    quality = int(session["haul_quality"])
    count = max(1, min(14, 8 + quality // 5))
    roll = _roll(reward_roll)
    tiger_shark = (
        level >= FISHING_TRAWLER_TIGER_SHARK.level
        and roll < FISHING_TRAWLER_TIGER_SHARK_TRIP_CHANCE
    )
    if level >= FISHING_TRAWLER_TIGER_SHARK.level:
        if tiger_shark:
            selector_roll = roll / FISHING_TRAWLER_TIGER_SHARK_TRIP_CHANCE
        else:
            selector_roll = (
                roll - FISHING_TRAWLER_TIGER_SHARK_TRIP_CHANCE
            ) / (1.0 - FISHING_TRAWLER_TIGER_SHARK_TRIP_CHANCE)
    else:
        selector_roll = roll
    top_bias = min(len(eligible) - 1, int(selector_roll * len(eligible)))
    outputs: dict[str, int] = {}
    xp = 0.0
    if tiger_shark:
        outputs[FISHING_TRAWLER_TIGER_SHARK.item] = 1
        xp += FISHING_TRAWLER_TIGER_SHARK.ordinary_xp * 0.40
    for index in range(count - int(tiger_shark)):
        catch = eligible[max(0, top_bias - (index % min(3, len(eligible))))]
        outputs[catch.item] = outputs.get(catch.item, 0) + 1
        xp += catch.ordinary_xp * 0.40
    inventory = dict(data.get("inventory") or {})
    for item, quantity in outputs.items():
        inventory[item] = _int(inventory.get(item)) + quantity
    data["inventory"] = inventory
    return outputs, round(xp, 1)


def apply_fishing_trawler_review_pure(
    player_data: Mapping[str, Any], reward_roll: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: sanitize_fishing_trawler_state_pure rebuilds all its
    # keys, and inventory is rebuilt with dict() before the haul is added.
    data = dict(player_data)
    state = sanitize_fishing_trawler_state_pure(data)
    session = state["fishing_trawler"]
    if not session:
        return data, {"allowed": False, "reason": "Board the Fishing Trawler before training."}

    event = FISHING_TRAWLER_PRESSURE_EVENTS[int(session["review"])]
    session["water"] = min(
        FISHING_TRAWLER_SINK_WATER,
        max(
            0,
            int(session["water"])
            + event.water
            + int(session["leaks"]) * 5
            - FISHING_TRAWLER_CREW_WATER_OFFSET,
        ),
    )
    session["leaks"] = min(20, int(session["leaks"]) + event.leaks)
    if event.tears_net:
        session["net_intact"] = False

    duty = _choose_duty(session)
    _apply_duty(session, duty)
    next_review = int(session["review"]) + 1
    sunk = int(session["water"]) >= FISHING_TRAWLER_SINK_WATER
    terminal = sunk or next_review >= FISHING_TRAWLER_EVENT_REVIEWS
    outputs: dict[str, int] = {}
    xp = 0.0
    if terminal:
        supplies = dict(session["supplies"])
        if sunk:
            data["fishing_trawler_trips_sunk"] = state["fishing_trawler_trips_sunk"] + 1
        else:
            outputs, xp = _award_haul(data, session, reward_roll)
            data["fishing_trawler_trips_completed"] = state["fishing_trawler_trips_completed"] + 1
        _finish_trip(data, supplies)
    else:
        session["review"] = next_review
        data.update(state)
        data["fishing_trawler"] = session

    duty_labels = {
        "repair_leak": "repaired a leak",
        "bail": "bailed water",
        "repair_net": "repaired the net",
        "fish": "worked the net",
    }
    if sunk:
        status = f"Fishing Trawler · {event.label} · boat sank · no haul"
    elif terminal:
        haul_count = sum(outputs.values())
        status = f"Fishing Trawler · docked · {haul_count} fish banked · {xp:g} Fishing XP"
    else:
        status = (
            f"Fishing Trawler · {event.label} · {duty_labels[duty]} · "
            f"water {session['water']}% · leaks {session['leaks']} · {next_review}/10"
        )
    data["fishing_trawler_last_result"] = status
    return data, {
        "allowed": True,
        "action_id": FISHING_TRAWLER_ACTIVITY_ID,
        "success": not sunk,
        "expected_success_chance": 1.0,
        "duty": duty,
        "water": int(session["water"]),
        "leaks": int(session["leaks"]),
        "net_intact": bool(session["net_intact"]),
        "contribution": int(session["contribution"]),
        "haul_quality": int(session["haul_quality"]),
        "outputs": outputs,
        "xp": xp,
        "sunk": sunk,
        "terminal": terminal,
        "completed_activity": terminal and not sunk,
        "status": status,
    }


def leave_fishing_trawler_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_fishing_trawler_state_pure rebuilds all its
    # keys, and inventory is rebuilt with dict() before the haul is added.
    data = dict(player_data)
    state = sanitize_fishing_trawler_state_pure(data)
    session = state["fishing_trawler"]
    if not session:
        return data, False, {"reason": "No Fishing Trawler trip is active."}
    progress = int(session["review"])
    _finish_trip(data, session["supplies"])
    data["fishing_trawler_last_result"] = (
        f"Left the Fishing Trawler after {progress}/10 duties · haul forfeited"
    )
    return data, True, {"message": data["fishing_trawler_last_result"]}


def apply_fishing_trawler_command_pure(
    player_data: Mapping[str, Any], action_id: Any, payload: Mapping[str, Any] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    action = str(action_id)
    if action == "enter_fishing_trawler":
        return enter_fishing_trawler_pure(player_data, payload)
    if action == "leave_fishing_trawler":
        return leave_fishing_trawler_pure(player_data)
    if action == "set_fishing_trawler_policy":
        return set_fishing_trawler_policy_pure(player_data, payload)
    # Shallow on purpose: nothing is written here, and every other failure
    # branch already hands back the same shallow copy, which the only caller
    # (_apply_fishing_trawler_command) discards whenever ok is False.
    return dict(player_data), False, {"reason": "Unknown Fishing Trawler action."}


def fishing_trawler_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_fishing_trawler_state_pure(player_data)
    session = state["fishing_trawler"]
    policy = state["fishing_trawler_policy"]
    inventory = player_data.get("inventory")
    bank = inventory if isinstance(inventory, Mapping) else {}
    layout = policy["layout"]
    return {
        "active": bool(session),
        "can_review": bool(session),
        "eligible": _int(player_data.get("fishing_level"), 1) >= 15,
        "review": int(session.get("review", 0)),
        "reviews_total": FISHING_TRAWLER_EVENT_REVIEWS,
        "water": int(session.get("water", 0)),
        "leaks": int(session.get("leaks", 0)),
        "net_intact": bool(session.get("net_intact", True)),
        "contribution": int(session.get("contribution", 0)),
        "haul_quality": int(session.get("haul_quality", 0)),
        "supplies": dict(session.get("supplies", {})),
        "automation_mode": str(session.get("automation_mode", policy["automation_mode"])),
        "priority": str(session.get("priority", policy["priority"])),
        "layout": dict(layout),
        "layout_slots": fishing_trawler_layout_slots_pure(layout),
        "layout_capacity": FISHING_TRAWLER_LAYOUT_CAPACITY,
        "bank_supplies": {item: _int(bank.get(item)) for item in layout},
        "trips_completed": state["fishing_trawler_trips_completed"],
        "trips_sunk": state["fishing_trawler_trips_sunk"],
        "last_result": state["fishing_trawler_last_result"],
    }
