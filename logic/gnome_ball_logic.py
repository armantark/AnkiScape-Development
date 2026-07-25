"""Pure entry, three-beat match, reward, and exit mechanics for Gnome Ball."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.combat_data import COMBAT_FOOD_DATA
from ..data.gnome_ball_data import (
    GNOME_BALL_ACTIVITY_ID,
    GNOME_BALL_BEATS,
    GNOME_BALL_COMPLETION_BONUS_XP,
    GNOME_BALL_GOAL_XP,
    GNOME_BALL_TACKLE_ENTRY_CHANCE,
    GNOME_BALL_TACKLE_RESIDUAL_CHANCE,
)
from ..logic.inventory_pure import CARRIED_CAPACITY, apply_carried_layout_pure
from ..data.item_values import STACKABLE_ITEM_NAMES
from ..logic_pure.logic_pure import apply_thieving_damage_pure


GNOME_BALL_STATE_VERSION = 1
_BEAT_SCORES = (0, 2, 4)


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0


def default_gnome_ball_state_pure() -> dict[str, Any]:
    return {
        "gnome_ball": {},
        "gnome_ball_runs_completed": 0,
        "gnome_ball_last_result": "Ready to enter",
    }


def sanitize_gnome_ball_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    beat = _int(raw.get("beat"), maximum=len(GNOME_BALL_BEATS) - 1)
    return {
        "version": GNOME_BALL_STATE_VERSION,
        "beat": beat,
        "score": _BEAT_SCORES[beat],
    }


def sanitize_gnome_ball_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_gnome_ball_state_pure()
    session = sanitize_gnome_ball_session_pure(source.get("gnome_ball"))
    active_session = source.get("activity_session")
    active_id = (
        str(active_session.get("active_id", ""))
        if isinstance(active_session, Mapping)
        else ""
    )
    if session and active_id not in {"", GNOME_BALL_ACTIVITY_ID}:
        session = {}
    return {
        "gnome_ball": session,
        "gnome_ball_runs_completed": _int(source.get("gnome_ball_runs_completed")),
        "gnome_ball_last_result": str(
            source.get(
                "gnome_ball_last_result",
                defaults["gnome_ball_last_result"],
            )
            or defaults["gnome_ball_last_result"]
        )[:320],
    }


def _equipped_weapon(player_data: Mapping[str, Any]) -> str:
    equipment = player_data.get("equipment")
    return (
        str(equipment.get("weapon", ""))
        if isinstance(equipment, Mapping)
        else ""
    )


def gnome_ball_locked_reasons_pure(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    weapon = _equipped_weapon(player_data)
    if weapon and weapon.casefold() != "gnomeball":
        return ("unequip your weapon (only a Gnomeball is allowed)",)
    return ()


def gnome_ball_tackle_chance_pure(agility_level: Any) -> float:
    level = max(1, min(_int(agility_level, 1), 99))
    progress = (level - 1) / 98
    return (
        GNOME_BALL_TACKLE_ENTRY_CHANCE
        - (
            GNOME_BALL_TACKLE_ENTRY_CHANCE
            - GNOME_BALL_TACKLE_RESIDUAL_CHANCE
        )
        * progress
    )


def _tackle_damage(player_data: Mapping[str, Any]) -> int:
    current = max(1, _int(player_data.get("combat_lifepoints"), 100))
    return max(10, min(current // 10, 100))


def _finish_session(data: dict[str, Any]) -> None:
    data["gnome_ball"] = {}
    active = data.get("activity_session")
    if (
        isinstance(active, Mapping)
        and str(active.get("active_id", "")) == GNOME_BALL_ACTIVITY_ID
    ):
        data["activity_session"] = {"active_id": ""}


def _carried_gnomeball(player_data: Mapping[str, Any]) -> bool:
    carried_by_target = player_data.get("carried_inventory")
    carried = (
        carried_by_target.get(GNOME_BALL_ACTIVITY_ID)
        if isinstance(carried_by_target, Mapping)
        else None
    )
    if isinstance(carried, Mapping) and _int(carried.get("Gnomeball")) > 0:
        return True
    return _equipped_weapon(player_data).casefold() == "gnomeball"


def _prepare_pack(player_data: Mapping[str, Any]) -> dict[str, int]:
    advanced = player_data.get("carried_advanced_targets")
    custom = isinstance(advanced, Mapping) and bool(
        advanced.get(GNOME_BALL_ACTIVITY_ID)
    )
    layouts = player_data.get("carried_layout")
    if custom and isinstance(layouts, Mapping):
        raw_layout = layouts.get(GNOME_BALL_ACTIVITY_ID, {})
        layout = dict(raw_layout) if isinstance(raw_layout, Mapping) else {}
    else:
        inventory = player_data.get("inventory")
        bank = inventory if isinstance(inventory, Mapping) else {}
        layout = {}
        for item_name in player_data.get("combat_auto_eat_food", ()) or ():
            if item_name not in COMBAT_FOOD_DATA:
                continue
            available = _int(bank.get(item_name))
            if available > 0:
                layout[str(item_name)] = available
    inventory = player_data.get("inventory")
    return apply_carried_layout_pure(
        inventory if isinstance(inventory, Mapping) else {},
        layout,
        CARRIED_CAPACITY,
        STACKABLE_ITEM_NAMES,
    )


def enter_gnome_ball_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_gnome_ball_state_pure rebuilds all its keys,
    # and the session state is the only thing written back.
    data = dict(player_data)
    state = sanitize_gnome_ball_state_pure(data)
    if state["gnome_ball"]:
        return data, False, {"reason": "A Gnome Ball match is already active."}
    active = data.get("activity_session")
    active_id = (
        str(active.get("active_id", ""))
        if isinstance(active, Mapping)
        else ""
    )
    if active_id and active_id != GNOME_BALL_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    locked = gnome_ball_locked_reasons_pure(data)
    if locked:
        return data, False, {"reason": ", ".join(locked), "locked_reasons": locked}
    data.update(state)
    carried = dict(data.get("carried_inventory") or {})
    existing_pack = carried.get(GNOME_BALL_ACTIVITY_ID)
    if not isinstance(existing_pack, Mapping) or not existing_pack:
        carried[GNOME_BALL_ACTIVITY_ID] = _prepare_pack(data)
    data["carried_inventory"] = carried
    data["gnome_ball"] = {
        "version": GNOME_BALL_STATE_VERSION,
        "beat": 0,
        "score": 0,
    }
    data["activity_session"] = {"active_id": GNOME_BALL_ACTIVITY_ID}
    data["current_utility"] = GNOME_BALL_ACTIVITY_ID
    data["gnome_ball_last_result"] = "Entered Gnome Ball · opening beat ready"
    return data, True, {
        "message": data["gnome_ball_last_result"],
        "pack": dict(carried[GNOME_BALL_ACTIVITY_ID]),
    }


def apply_gnome_ball_review_pure(
    player_data: Mapping[str, Any],
    tackle_roll: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: sanitize_gnome_ball_state_pure rebuilds all its keys,
    # and the session state is the only thing written back.
    data = dict(player_data)
    session = sanitize_gnome_ball_session_pure(data.get("gnome_ball"))
    if not session:
        return data, {"allowed": False, "reason": "Enter Gnome Ball before training."}
    beat = int(session["beat"])
    beat_spec = GNOME_BALL_BEATS[beat]
    chance = gnome_ball_tackle_chance_pure(data.get("agility_level"))
    tackled = max(0.0, min(_float(tackle_roll), 1.0)) < chance
    damage = 0
    damage_result: dict[str, Any] = {}
    if tackled:
        damaged, damage_result = apply_thieving_damage_pure(
            data,
            _tackle_damage(data),
            source="gnome_ball_tackle",
            carried_target_id=GNOME_BALL_ACTIVITY_ID,
        )
        data.clear()
        data.update(damaged)
        damage = int(damage_result.get("damage", 0) or 0)
        if damage_result.get("died"):
            _finish_session(data)
            data["gnome_ball_last_result"] = (
                f"Gnome Ball · tackled for {damage} LP · match lost on death"
            )
            return data, {
                "allowed": True,
                "action_id": GNOME_BALL_ACTIVITY_ID,
                "success": False,
                "expected_success_chance": 1.0,
                "tackle_chance": chance,
                "tackled": True,
                "damage": damage,
                "died": True,
                "goals": (),
                "agility_xp": 0.0,
                "ranged_xp": 0.0,
                "outputs": {},
                "terminal": True,
                "completed_activity": False,
                "status": data["gnome_ball_last_result"],
            }

    goals = tuple(int(goal) for goal in beat_spec["goals"])
    xp = sum(float(GNOME_BALL_GOAL_XP[goal - 1]) for goal in goals)
    final = beat == len(GNOME_BALL_BEATS) - 1
    if final:
        xp += GNOME_BALL_COMPLETION_BONUS_XP
    score = goals[-1]
    outputs: dict[str, int] = {}
    if final:
        if not _carried_gnomeball(data):
            inventory = dict(data.get("inventory") or {})
            inventory["Gnomeball"] = _int(inventory.get("Gnomeball")) + 1
            data["inventory"] = inventory
            outputs["Gnomeball"] = 1
        completions = dict(data.get("agility_activity_completions") or {})
        completions["gnome_ball"] = _int(completions.get("gnome_ball")) + 1
        data["agility_activity_completions"] = completions
        data["gnome_ball_runs_completed"] = _int(
            data.get("gnome_ball_runs_completed")
        ) + 1
        _finish_session(data)
    else:
        data["gnome_ball"] = {
            "version": GNOME_BALL_STATE_VERSION,
            "beat": beat + 1,
            "score": score,
        }

    tackle_text = f" · tackled for {damage} LP" if tackled else ""
    reward_text = (
        " · referee awarded a Gnomeball"
        if outputs
        else " · referee withheld a duplicate carried Gnomeball"
        if final
        else ""
    )
    data["gnome_ball_last_result"] = (
        f"Gnome Ball · {beat_spec['label']} beat · goals "
        f"{goals[0]}{'–' + str(goals[-1]) if len(goals) > 1 else ''} scored"
        f"{tackle_text} · {xp:g} Agility + {xp:g} Ranged XP{reward_text}"
    )
    return data, {
        "allowed": True,
        "action_id": GNOME_BALL_ACTIVITY_ID,
        "success": True,
        "expected_success_chance": 1.0,
        "tackle_chance": chance,
        "tackled": tackled,
        "damage": damage,
        "died": False,
        "goals": goals,
        "score": score,
        "agility_xp": xp,
        "ranged_xp": xp,
        "outputs": outputs,
        "terminal": final,
        "completed_activity": final,
        "status": data["gnome_ball_last_result"],
    }


def leave_gnome_ball_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_gnome_ball_state_pure rebuilds all its keys,
    # and the session state is the only thing written back.
    data = dict(player_data)
    session = sanitize_gnome_ball_session_pure(data.get("gnome_ball"))
    if not session:
        return data, False, {"reason": "No Gnome Ball match is active."}
    score = int(session["score"])
    _finish_session(data)
    data["gnome_ball_last_result"] = f"Left Gnome Ball at {score}/5 goals"
    return data, True, {"message": data["gnome_ball_last_result"]}


def gnome_ball_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_gnome_ball_state_pure(player_data)
    session = state["gnome_ball"]
    beat = int(session.get("beat", 0))
    score = int(session.get("score", 0))
    return {
        "active": bool(session),
        "can_review": bool(session),
        "locked_reasons": gnome_ball_locked_reasons_pure(player_data),
        "beat": beat,
        "beat_number": beat + 1 if session else 0,
        "beat_label": str(GNOME_BALL_BEATS[beat]["label"]) if session else "Opening",
        "score": score,
        "tackle_chance": gnome_ball_tackle_chance_pure(
            player_data.get("agility_level")
        ),
        "lifepoints": _int(player_data.get("combat_lifepoints"), 100),
        "runs_completed": state["gnome_ball_runs_completed"],
        "last_result": state["gnome_ball_last_result"],
    }
