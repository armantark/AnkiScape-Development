"""Pure substrate for persistent multi-enemy boss rooms."""

from __future__ import annotations

import copy
import math
from collections.abc import Mapping, Sequence
from typing import Any

from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    apply_thieving_damage_pure,
    combat_enemy_pressure_attack_pure,
)


BOSS_ROOM_STATE_VERSION = 1


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        return max(minimum, int(value))
    except (TypeError, ValueError):
        return max(minimum, default)


def default_boss_room_state_pure() -> dict[str, Any]:
    return {
        "version": BOSS_ROOM_STATE_VERSION,
        "active": False,
        "roster": [],
        "engaged_enemy_id": "",
        "automation_mode": "casual",
        "previous_combat_target": "",
        "trip_kills": 0,
        "total_kills": 0,
        "kill_counts": {},
        "trips": 0,
        "last_result": "",
    }


def _encounter(raw: Any, target_id: str, lifepoints: int) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    result = {
        str(key): copy.deepcopy(value)
        for key, value in source.items()
        if isinstance(key, str)
    }
    result["target_id"] = target_id
    result["enemy_lifepoints"] = lifepoints
    return result


def _new_member(enemy_id: str, enemy_data: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    maximum = _int(enemy_data[enemy_id]["stats"]["hitpoints"], 1, minimum=1)
    return {
        "enemy_id": enemy_id,
        "lifepoints": maximum,
        "respawn_ticks": 0,
        "encounter": _encounter({}, enemy_id, maximum),
    }


def sanitize_boss_room_state_pure(
    raw: Any,
    enemy_data: Mapping[str, Mapping[str, Any]],
    enemy_ids: Sequence[str],
) -> dict[str, Any]:
    defaults = default_boss_room_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    supplied = {}
    for row in source.get("roster", ()) or ():
        if isinstance(row, Mapping):
            enemy_id = str(row.get("enemy_id", ""))
            if enemy_id in enemy_data and enemy_id not in supplied:
                supplied[enemy_id] = row

    roster = []
    for enemy_id in enemy_ids:
        spec = enemy_data[enemy_id]
        maximum = _int(spec["stats"]["hitpoints"], 1, minimum=1)
        row = supplied.get(enemy_id)
        if row is None:
            roster.append(_new_member(enemy_id, enemy_data))
            continue
        lifepoints = min(maximum, _int(row.get("lifepoints")))
        respawn_ticks = _int(row.get("respawn_ticks")) if lifepoints <= 0 else 0
        roster.append(
            {
                "enemy_id": enemy_id,
                "lifepoints": lifepoints,
                "respawn_ticks": respawn_ticks,
                "encounter": (
                    _encounter(row.get("encounter"), enemy_id, lifepoints)
                    if lifepoints > 0
                    else {}
                ),
            }
        )

    mode = str(source.get("automation_mode", "casual"))
    if mode not in {"casual", "advanced"}:
        mode = "casual"
    engaged = str(source.get("engaged_enemy_id", ""))
    if not any(
        row["enemy_id"] == engaged and row["lifepoints"] > 0 for row in roster
    ):
        engaged = ""
    raw_counts = source.get("kill_counts")
    counts = {
        enemy_id: _int(raw_counts.get(enemy_id))
        for enemy_id in enemy_ids
        if isinstance(raw_counts, Mapping) and _int(raw_counts.get(enemy_id)) > 0
    }
    active = bool(source.get("active", False))
    return {
        **defaults,
        "active": active,
        "roster": roster if active else [],
        "engaged_enemy_id": engaged if active else "",
        "automation_mode": mode,
        "previous_combat_target": str(source.get("previous_combat_target", ""))[:120],
        "trip_kills": _int(source.get("trip_kills")) if active else 0,
        "total_kills": _int(source.get("total_kills")),
        "kill_counts": counts,
        "trips": _int(source.get("trips")),
        "last_result": str(source.get("last_result", ""))[:500],
    }


def _alive_member(state: Mapping[str, Any], enemy_id: str) -> dict[str, Any] | None:
    return next(
        (
            row
            for row in state.get("roster", ())
            if row.get("enemy_id") == enemy_id and _int(row.get("lifepoints")) > 0
        ),
        None,
    )


def _engaged_member(
    state: dict[str, Any], enemy_data: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any] | None:
    selected = _alive_member(state, str(state.get("engaged_enemy_id", "")))
    if state["automation_mode"] == "advanced" and selected is not None:
        return selected
    alive = [row for row in state["roster"] if _int(row.get("lifepoints")) > 0]
    if not alive:
        return None
    selected = min(
        alive,
        key=lambda row: (
            _int(enemy_data[row["enemy_id"]].get("priority"), 99),
            str(row["enemy_id"]),
        ),
    )
    state["engaged_enemy_id"] = selected["enemy_id"]
    return selected


def _advance_respawns(
    state: dict[str, Any],
    enemy_data: Mapping[str, Mapping[str, Any]],
    ticks: int,
) -> tuple[str, ...]:
    respawned = []
    for row in state["roster"]:
        if _int(row.get("lifepoints")) > 0:
            continue
        remaining = max(0, _int(row.get("respawn_ticks")) - ticks)
        row["respawn_ticks"] = remaining
        if remaining == 0:
            enemy_id = row["enemy_id"]
            maximum = _int(
                enemy_data[enemy_id]["stats"]["hitpoints"], 1, minimum=1
            )
            row["lifepoints"] = maximum
            row["encounter"] = _encounter({}, enemy_id, maximum)
            respawned.append(enemy_id)
    return tuple(respawned)


def boss_room_view_pure(
    player_data: Mapping[str, Any],
    *,
    state_key: str,
    enemy_data: Mapping[str, Mapping[str, Any]],
    enemy_ids: Sequence[str],
    review_ticks: int,
) -> dict[str, Any]:
    state = sanitize_boss_room_state_pure(
        player_data.get(state_key), enemy_data, enemy_ids
    )
    display = copy.deepcopy(state)
    engaged = _engaged_member(display, enemy_data) if display["active"] else None
    engaged_id = engaged["enemy_id"] if engaged is not None else ""
    return {
        **state,
        "roster_view": tuple(
            {
                "enemy_id": row["enemy_id"],
                "display_name": enemy_data[row["enemy_id"]]["display_name"],
                "lifepoints": row["lifepoints"],
                "max_lifepoints": enemy_data[row["enemy_id"]]["stats"]["hitpoints"],
                "attack_style": enemy_data[row["enemy_id"]]["attack_style"],
                "respawn_reviews": (
                    math.ceil(_int(row.get("respawn_ticks")) / max(1, review_ticks))
                    if row["lifepoints"] <= 0
                    else 0
                ),
                "engaged": row["enemy_id"] == engaged_id,
            }
            for row in state["roster"]
        ),
    }


def _end_room(
    data: dict[str, Any], state: dict[str, Any], state_key: str, outcome: str
) -> None:
    previous = state.get("previous_combat_target")
    state["active"] = False
    state["roster"] = []
    state["engaged_enemy_id"] = ""
    state["trip_kills"] = 0
    state["last_result"] = outcome[:500]
    data[state_key] = state
    data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(previous or "")


def apply_boss_room_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None,
    *,
    activity_id: str,
    display_name: str,
    state_key: str,
    enemy_data: Mapping[str, Mapping[str, Any]],
    enemy_ids: Sequence[str],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_boss_room_state_pure(
        data.get(state_key), enemy_data, enemy_ids
    )
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "enter":
        if state["active"]:
            data["activity_session"] = {"active_id": activity_id}
            return data, True, {"message": f"Resumed {display_name}."}
        active_session = data.get("activity_session")
        if isinstance(active_session, Mapping) and active_session.get("active_id"):
            return data, False, {"reason": "Another persistent activity is active."}
        encounter = data.get("combat_encounter")
        if isinstance(encounter, Mapping) and encounter.get("target_id"):
            return data, False, {"reason": "Finish or leave the current Combat encounter first."}
        state.update(
            {
                "active": True,
                "roster": [_new_member(enemy_id, enemy_data) for enemy_id in enemy_ids],
                "engaged_enemy_id": "",
                "previous_combat_target": str(data.get("current_combat_target", "")),
                "trip_kills": 0,
                "trips": state["trips"] + 1,
                "last_result": f"Entered {display_name}.",
            }
        )
        data[state_key] = state
        data["activity_session"] = {"active_id": activity_id}
        return data, True, {"message": state["last_result"]}

    if action_id == "leave":
        if not state["active"]:
            return data, False, {"reason": f"No {display_name} session is active."}
        kills = state["trip_kills"]
        _end_room(data, state, state_key, f"Left {display_name} after {kills} kills.")
        return data, True, {"message": state["last_result"], "trip_kills": kills}

    if action_id == "set_mode":
        mode = str(payload.get("automation_mode", "casual"))
        if mode not in {"casual", "advanced"}:
            return data, False, {"reason": "Unknown targeting mode."}
        state["automation_mode"] = mode
        if mode == "casual":
            state["engaged_enemy_id"] = ""
        data[state_key] = state
        return data, True, {"message": f"Targeting mode: {mode}."}

    if action_id == "select_target":
        if state["automation_mode"] != "advanced":
            return data, False, {"reason": "Choose Advanced targeting first."}
        enemy_id = str(payload.get("enemy_id", ""))
        if _alive_member(state, enemy_id) is None:
            return data, False, {"reason": "That boss is not currently alive."}
        state["engaged_enemy_id"] = enemy_id
        data[state_key] = state
        return data, True, {"message": f"Targeting {enemy_data[enemy_id]['display_name']}."}

    return data, False, {"reason": "Unknown boss-room command."}


def apply_boss_room_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    activity_id: str,
    display_name: str,
    state_key: str,
    enemy_data: Mapping[str, Mapping[str, Any]],
    enemy_ids: Sequence[str],
    review_ticks: int,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_boss_room_state_pure(
        data.get(state_key), enemy_data, enemy_ids
    )
    if not state["active"]:
        return data, False, {"reason": f"Enter {display_name} before training."}
    equipment_data = equipment_data or {}
    respawned = _advance_respawns(state, enemy_data, review_ticks)
    engaged = _engaged_member(state, enemy_data)
    data[state_key] = state
    data["activity_session"] = {"active_id": activity_id}
    if engaged is None:
        waiting = min(
            (_int(row.get("respawn_ticks")) for row in state["roster"]),
            default=0,
        )
        status = f"{display_name} is quiet · next respawn in {math.ceil(waiting / max(1, review_ticks))} reviews"
        state["last_result"] = status[:500]
        return data, True, {"status": state["last_result"], "respawned": respawned}

    enemy_id = engaged["enemy_id"]
    data["current_combat_target"] = enemy_id
    data["combat_encounter"] = _encounter(
        engaged.get("encounter"), enemy_id, engaged["lifepoints"]
    )
    existing_alive = {
        row["enemy_id"] for row in state["roster"] if _int(row.get("lifepoints")) > 0
    }
    data, ok, combat_result = apply_combat_burst_pure(
        data,
        {enemy_id: copy.deepcopy(enemy_data[enemy_id])},
        equipment_data,
        ticks=review_ticks,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=False,
        allow_bank_run=False,
    )
    if not ok:
        return dict(player_data), False, combat_result
    if combat_result.get("died") or combat_result.get("fled"):
        outcome = "Defeated in" if combat_result.get("died") else "Fled"
        _end_room(data, state, state_key, f"{outcome} {display_name}.")
        return data, True, {
            **combat_result,
            "outcome": state["last_result"],
            "status": state["last_result"],
        }

    killed = bool(combat_result.get("killed"))
    if killed:
        engaged["lifepoints"] = 0
        engaged["respawn_ticks"] = _int(
            enemy_data[enemy_id].get("respawn_delay"), 1, minimum=1
        )
        engaged["encounter"] = {}
        state["engaged_enemy_id"] = ""
        state["trip_kills"] += 1
        state["total_kills"] += 1
        counts = dict(state.get("kill_counts", {}) or {})
        counts[enemy_id] = _int(counts.get(enemy_id)) + 1
        state["kill_counts"] = counts
        data["combat_encounter"] = {}
    else:
        engaged["lifepoints"] = max(
            1,
            _int(
                combat_result.get("enemy_lifepoints"),
                engaged["lifepoints"],
                minimum=1,
            ),
        )
        engaged["encounter"] = _encounter(
            data.get("combat_encounter"), enemy_id, engaged["lifepoints"]
        )

    pressure_damage = 0
    pressure_styles = []
    for row in state["roster"]:
        other_id = row["enemy_id"]
        if other_id == enemy_id or other_id not in existing_alive or row["lifepoints"] <= 0:
            continue
        pressure = combat_enemy_pressure_attack_pure(
            data, enemy_data[other_id], equipment_data, rng
        )
        pressure_damage += _int(pressure.get("damage"))
        pressure_styles.append(str(pressure.get("attack_style", "melee")))
    pressure_result: dict[str, Any] = {"damage": 0, "died": False, "food_used": None}
    if pressure_damage > 0:
        data, pressure_result = apply_thieving_damage_pure(
            data,
            pressure_damage,
            source=f"{activity_id}_pressure",
            carried_target_id=activity_id,
            safe_death=False,
        )
    if pressure_result.get("died"):
        _end_room(data, state, state_key, f"Defeated by {display_name} roster pressure.")
        return data, True, {
            **combat_result,
            "died": True,
            "pressure_damage": int(pressure_result.get("damage", 0) or 0),
            "outcome": state["last_result"],
            "status": state["last_result"],
        }

    enemy_name = enemy_data[enemy_id]["display_name"]
    status = (
        f"Defeated {enemy_name} · respawns in "
        f"{math.ceil(engaged['respawn_ticks'] / max(1, review_ticks))} reviews"
        if killed
        else f"{enemy_name}: {engaged['lifepoints']:,}/{enemy_data[enemy_id]['stats']['hitpoints']:,} LP"
    )
    if pressure_result.get("damage"):
        status += f" · roster pressure {int(pressure_result['damage'])} LP"
    if respawned:
        names = ", ".join(enemy_data[row]["display_name"] for row in respawned)
        status += f" · respawned: {names}"
    state["last_result"] = status[:500]
    data[state_key] = state
    data["activity_session"] = {"active_id": activity_id}
    return data, True, {
        **combat_result,
        "engaged_enemy_id": enemy_id,
        "pressure_damage": int(pressure_result.get("damage", 0) or 0),
        "pressure_styles": tuple(pressure_styles),
        "pressure_food_used": pressure_result.get("food_used"),
        "respawned": respawned,
        "status": state["last_result"],
    }
