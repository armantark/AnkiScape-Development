"""Pure Barbarian Assault tutorial, wave, Queen, point, and reward mechanics."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

try:
    from .logic_pure import apply_combat_burst_pure, combat_max_lifepoints_pure
    from .barbarian_assault_data import (
        BARBARIAN_ASSAULT_ACTIVITY_ID,
        BARBARIAN_ASSAULT_COMBAT_TARGET_ID,
        BARBARIAN_ASSAULT_OMEGA_DAMAGE,
        BARBARIAN_ASSAULT_POINT_STORAGE_MAX,
        BARBARIAN_ASSAULT_QUEEN_EGGS,
        BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS,
        BARBARIAN_ASSAULT_QUEEN_PRESSURE_DAMAGE,
        BARBARIAN_ASSAULT_ROLE_IDS,
        RUNNER_BOOTS_COST_PER_ROLE,
        barbarian_assault_front_enemy_pure,
        barbarian_assault_wave_points_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure import apply_combat_burst_pure, combat_max_lifepoints_pure  # type: ignore
    from barbarian_assault_data import (  # type: ignore
        BARBARIAN_ASSAULT_ACTIVITY_ID,
        BARBARIAN_ASSAULT_COMBAT_TARGET_ID,
        BARBARIAN_ASSAULT_OMEGA_DAMAGE,
        BARBARIAN_ASSAULT_POINT_STORAGE_MAX,
        BARBARIAN_ASSAULT_QUEEN_EGGS,
        BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS,
        BARBARIAN_ASSAULT_QUEEN_PRESSURE_DAMAGE,
        BARBARIAN_ASSAULT_ROLE_IDS,
        RUNNER_BOOTS_COST_PER_ROLE,
        barbarian_assault_front_enemy_pure,
        barbarian_assault_wave_points_pure,
    )


BARBARIAN_ASSAULT_STATE_VERSION = 1
_VALID_MODES = frozenset({"casual", "advanced"})


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _empty_points() -> dict[str, int]:
    return {role_id: 0 for role_id in BARBARIAN_ASSAULT_ROLE_IDS}


def _sanitize_points(raw: Any) -> dict[str, int]:
    source = raw if isinstance(raw, Mapping) else {}
    return {
        role_id: _int(
            source.get(role_id), maximum=BARBARIAN_ASSAULT_POINT_STORAGE_MAX
        )
        for role_id in BARBARIAN_ASSAULT_ROLE_IDS
    }


def _best_role(points: Mapping[str, Any]) -> str:
    return min(
        BARBARIAN_ASSAULT_ROLE_IDS,
        key=lambda role_id: (_int(points.get(role_id)), BARBARIAN_ASSAULT_ROLE_IDS.index(role_id)),
    )


def _wave_encounter(wave: int) -> dict[str, Any]:
    enemy = barbarian_assault_front_enemy_pure(wave)
    return {
        "target_id": BARBARIAN_ASSAULT_COMBAT_TARGET_ID,
        "enemy_lifepoints": int(enemy["stats"]["hitpoints"]),
    }


def default_barbarian_assault_state_pure() -> dict[str, Any]:
    return {
        "barbarian_assault": {},
        "barbarian_assault_policy": {
            "automation_mode": "casual",
            "role": "attacker",
        },
        "barbarian_assault_tutorial_complete": False,
        "barbarian_assault_points": _empty_points(),
        "barbarian_assault_queen_credit": False,
        "barbarian_assault_queen_kills": 0,
        "barbarian_assault_runs_completed": 0,
        "barbarian_assault_last_result": "",
    }


def sanitize_barbarian_assault_policy_pure(raw: Any) -> dict[str, str]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    role = str(source.get("role", "attacker"))
    return {
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "role": role if role in BARBARIAN_ASSAULT_ROLE_IDS else "attacker",
    }


def sanitize_barbarian_assault_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    wave = max(1, min(_int(raw.get("wave"), 1), 10))
    phase = "queen" if wave == 10 and str(raw.get("phase")) == "queen" else "wave"
    role = str(raw.get("role", "attacker"))
    encounter = raw.get("encounter")
    return {
        "version": BARBARIAN_ASSAULT_STATE_VERSION,
        "wave": wave,
        "phase": phase,
        "role": role if role in BARBARIAN_ASSAULT_ROLE_IDS else "attacker",
        "automation_mode": (
            str(raw.get("automation_mode"))
            if str(raw.get("automation_mode")) in _VALID_MODES
            else "casual"
        ),
        "queen_lifepoints": (
            _int(
                raw.get("queen_lifepoints", BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS),
                BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS,
                maximum=BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS,
            )
            if phase == "queen"
            else BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS
        ),
        "omega_eggs": (
            _int(raw.get("omega_eggs"), maximum=BARBARIAN_ASSAULT_QUEEN_EGGS)
            if phase == "queen"
            else 0
        ),
        "previous_combat_target": str(raw.get("previous_combat_target", ""))[:120],
        "encounter": copy.deepcopy(encounter) if isinstance(encounter, Mapping) else _wave_encounter(wave),
    }


def sanitize_barbarian_assault_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    session = sanitize_barbarian_assault_session_pure(source.get("barbarian_assault"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", BARBARIAN_ASSAULT_ACTIVITY_ID}:
        session = {}
    return {
        "barbarian_assault": session,
        "barbarian_assault_policy": sanitize_barbarian_assault_policy_pure(
            source.get("barbarian_assault_policy")
        ),
        "barbarian_assault_tutorial_complete": bool(
            source.get("barbarian_assault_tutorial_complete", False)
        ),
        "barbarian_assault_points": _sanitize_points(
            source.get("barbarian_assault_points")
        ),
        "barbarian_assault_queen_credit": bool(
            source.get("barbarian_assault_queen_credit", False)
        ),
        "barbarian_assault_queen_kills": _int(
            source.get("barbarian_assault_queen_kills")
        ),
        "barbarian_assault_runs_completed": _int(
            source.get("barbarian_assault_runs_completed")
        ),
        "barbarian_assault_last_result": str(
            source.get("barbarian_assault_last_result", "") or ""
        )[:500],
    }


def complete_barbarian_assault_tutorial_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the assault state and session are rebuilt fresh, so
    # the wave and queen writes land in new objects.
    data = dict(player_data)
    state = sanitize_barbarian_assault_state_pure(data)
    if state["barbarian_assault_tutorial_complete"]:
        return data, False, {"reason": "Captain Cain's tutorial is already complete."}
    data.update(state)
    data["barbarian_assault_tutorial_complete"] = True
    data["barbarian_assault_last_result"] = "Completed Captain Cain's role tutorial."
    return data, True, {"message": data["barbarian_assault_last_result"]}


def set_barbarian_assault_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the assault state and session are rebuilt fresh, so
    # the wave and queen writes land in new objects.
    data = dict(player_data)
    state = sanitize_barbarian_assault_state_pure(data)
    candidate = dict(state["barbarian_assault_policy"])
    candidate.update(dict(payload or {}))
    policy = sanitize_barbarian_assault_policy_pure(candidate)
    session = state["barbarian_assault"]
    if session and session["phase"] == "queen" and policy != state["barbarian_assault_policy"]:
        return data, False, {"reason": "Finish or restart wave 10 before changing roles."}
    data.update(state)
    data["barbarian_assault_policy"] = policy
    if session:
        session["automation_mode"] = policy["automation_mode"]
        session["role"] = (
            _best_role(state["barbarian_assault_points"])
            if policy["automation_mode"] == "casual"
            else policy["role"]
        )
        data["barbarian_assault"] = session
    data["barbarian_assault_last_result"] = "Barbarian Assault role plan saved."
    return data, True, {"message": data["barbarian_assault_last_result"], "policy": policy}


def enter_barbarian_assault_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if payload:
        data, ok, info = set_barbarian_assault_policy_pure(player_data, payload)
        if not ok:
            return data, False, info
    else:
        # Shallow on purpose: the assault state and session are rebuilt fresh,
        # so the wave and queen writes land in new objects.
        data = dict(player_data)
    state = sanitize_barbarian_assault_state_pure(data)
    if state["barbarian_assault"]:
        return data, False, {"reason": "A Barbarian Assault run is already active."}
    if not state["barbarian_assault_tutorial_complete"]:
        return data, False, {
            "reason": "Complete Captain Cain's tutorial first.",
            "requires_tutorial": True,
        }
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != BARBARIAN_ASSAULT_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {
            "reason": "Finish or leave the current Combat encounter first."
        }

    policy = state["barbarian_assault_policy"]
    role = (
        _best_role(state["barbarian_assault_points"])
        if policy["automation_mode"] == "casual"
        else policy["role"]
    )
    previous = str(data.get("current_combat_target", ""))[:120]
    data.update(state)
    data["barbarian_assault"] = {
        "version": BARBARIAN_ASSAULT_STATE_VERSION,
        "wave": 1,
        "phase": "wave",
        "role": role,
        "automation_mode": policy["automation_mode"],
        "queen_lifepoints": BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS,
        "omega_eggs": 0,
        "previous_combat_target": previous,
        "encounter": _wave_encounter(1),
    }
    data["activity_session"] = {"active_id": BARBARIAN_ASSAULT_ACTIVITY_ID}
    data["current_utility"] = BARBARIAN_ASSAULT_ACTIVITY_ID
    data["current_combat_target"] = BARBARIAN_ASSAULT_COMBAT_TARGET_ID
    data["combat_encounter"] = copy.deepcopy(data["barbarian_assault"]["encounter"])
    data["barbarian_assault_last_result"] = f"Entered wave 1 as {role}."
    return data, True, {"message": data["barbarian_assault_last_result"], "role": role}


def _restore_previous_target(data: dict[str, Any], session: Mapping[str, Any]) -> None:
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(session.get("previous_combat_target", ""))


def _restart_wave_after_safe_death(
    data: dict[str, Any], session: dict[str, Any]
) -> dict[str, Any]:
    session["phase"] = "wave"
    session["queen_lifepoints"] = BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS
    session["omega_eggs"] = 0
    session["encounter"] = _wave_encounter(int(session["wave"]))
    data["combat_encounter"] = copy.deepcopy(session["encounter"])
    data["barbarian_assault"] = session
    data["barbarian_assault_last_result"] = (
        f"Safe death · wave {session['wave']} restarted with no points."
    )
    return {
        "terminal": False,
        "safe_death": True,
        "wave_restarted": True,
        "message": data["barbarian_assault_last_result"],
    }


def _apply_queen_pressure(data: dict[str, Any]) -> dict[str, Any]:
    max_lifepoints = combat_max_lifepoints_pure(data)
    current = _int(data.get("combat_lifepoints"), max_lifepoints)
    damage = min(current, BARBARIAN_ASSAULT_QUEEN_PRESSURE_DAMAGE)
    died = damage > 0 and current - damage <= 0
    data["combat_lifepoints"] = max_lifepoints if died else current - damage
    if died:
        data["combat_encounter"] = {}
        data["combat_status_effects"] = {}
    return {
        "damage": damage,
        "died": died,
        "safe_death": died,
        "food_used": None,
    }


def _award_points(
    data: dict[str, Any], wave: int, role: str
) -> dict[str, int]:
    wallet = _sanitize_points(data.get("barbarian_assault_points"))
    proposed = barbarian_assault_wave_points_pure(wave, role)
    awarded: dict[str, int] = {}
    for role_id in BARBARIAN_ASSAULT_ROLE_IDS:
        before = wallet[role_id]
        after = min(
            BARBARIAN_ASSAULT_POINT_STORAGE_MAX,
            before + proposed[role_id],
        )
        wallet[role_id] = after
        awarded[role_id] = after - before
    data["barbarian_assault_points"] = wallet
    return awarded


def _advance_after_wave(
    data: dict[str, Any], session: dict[str, Any], awarded: Mapping[str, int]
) -> dict[str, Any]:
    completed = int(session["wave"])
    completed_role = str(session["role"])
    session["wave"] = completed + 1
    points = _sanitize_points(data.get("barbarian_assault_points"))
    if session["automation_mode"] == "casual":
        session["role"] = _best_role(points)
    session["encounter"] = _wave_encounter(int(session["wave"]))
    data["combat_encounter"] = copy.deepcopy(session["encounter"])
    data["barbarian_assault"] = session
    gained = sum(int(value) for value in awarded.values())
    data["barbarian_assault_last_result"] = (
        f"Wave {completed} complete · +{gained} {completed_role} Honour points · "
        f"wave {session['wave']} ready"
    )
    return {
        "terminal": False,
        "wave_completed": completed,
        "points": dict(awarded),
        "message": data["barbarian_assault_last_result"],
    }


def _finish_run(
    data: dict[str, Any], session: dict[str, Any], awarded: Mapping[str, int]
) -> dict[str, Any]:
    data["barbarian_assault_queen_credit"] = True
    data["barbarian_assault_queen_kills"] = _int(
        data.get("barbarian_assault_queen_kills")
    ) + 1
    data["barbarian_assault_runs_completed"] = _int(
        data.get("barbarian_assault_runs_completed")
    ) + 1
    data["barbarian_assault"] = {}
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == BARBARIAN_ASSAULT_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}
    _restore_previous_target(data, session)
    gained = sum(int(value) for value in awarded.values())
    data["barbarian_assault_last_result"] = (
        f"Penance Queen defeated with eight Omega eggs · +{gained} Honour points."
    )
    return {
        "terminal": True,
        "won": True,
        "queen_defeated": True,
        "points": dict(awarded),
        "message": data["barbarian_assault_last_result"],
    }


def apply_barbarian_assault_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    productive: bool,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the assault state and session are rebuilt fresh, so
    # the wave and queen writes land in new objects.
    data = dict(player_data)
    state = sanitize_barbarian_assault_state_pure(data)
    session = state["barbarian_assault"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != BARBARIAN_ASSAULT_ACTIVITY_ID:
        return data, False, {"reason": "Enter Barbarian Assault before training it."}

    if session["phase"] == "queen":
        if not productive:
            damage = _apply_queen_pressure(data)
            if damage["died"]:
                return data, True, {**damage, **_restart_wave_after_safe_death(data, session)}
            data["barbarian_assault"] = session
            data["barbarian_assault_last_result"] = "The Queen attacked while no Omega egg was prepared."
            return data, True, {
                "terminal": False,
                "duty": "idle",
                **damage,
                "message": data["barbarian_assault_last_result"],
            }

        session["omega_eggs"] += 1
        damage_to_queen = min(
            BARBARIAN_ASSAULT_OMEGA_DAMAGE,
            int(session["queen_lifepoints"]),
        )
        session["queen_lifepoints"] -= damage_to_queen
        if int(session["omega_eggs"]) >= BARBARIAN_ASSAULT_QUEEN_EGGS:
            session["queen_lifepoints"] = 0
        if int(session["queen_lifepoints"]) <= 0:
            awarded = _award_points(data, 10, str(session["role"]))
            return data, True, {
                "duty": str(session["role"]),
                "omega_egg": True,
                "queen_damage": damage_to_queen,
                **_finish_run(data, session, awarded),
            }
        data["barbarian_assault"] = session
        data["barbarian_assault_last_result"] = (
            f"Omega egg {session['omega_eggs']}/{BARBARIAN_ASSAULT_QUEEN_EGGS} fired · "
            f"Queen {session['queen_lifepoints']} LP"
        )
        return data, True, {
            "terminal": False,
            "duty": str(session["role"]),
            "omega_egg": True,
            "queen_damage": damage_to_queen,
            "damage": 0,
            "died": False,
            "safe_death": False,
            "food_used": None,
            "message": data["barbarian_assault_last_result"],
        }

    if not productive:
        data["barbarian_assault"] = session
        data["barbarian_assault_last_result"] = (
            f"No {session['role']} duty completed · wave {session['wave']} remains ready."
        )
        return data, True, {
            "terminal": False,
            "duty": "idle",
            "message": data["barbarian_assault_last_result"],
        }

    combat_result: dict[str, Any] = {}
    if session["role"] == "attacker":
        data["current_combat_target"] = BARBARIAN_ASSAULT_COMBAT_TARGET_ID
        data["combat_encounter"] = copy.deepcopy(session["encounter"])
        enemy = barbarian_assault_front_enemy_pure(int(session["wave"]))
        data, ok, combat_result = apply_combat_burst_pure(
            data,
            {BARBARIAN_ASSAULT_COMBAT_TARGET_ID: enemy},
            equipment_data or {},
            ticks=6,
            rng=rng,
            live_cadence=True,
            stop_after_first_kill=True,
            safe_death=True,
            allow_bank_run=False,
        )
        if not ok:
            # Shallow on purpose: this is a rejection, and every caller
            # (runtime_actions_activities.handle_barbarian_assault_answer,
            # __init__._apply_barbarian_assault_command) discards the save it
            # gets back when ok is False, so nothing writes into it.
            return dict(player_data), False, combat_result
        if combat_result.get("died"):
            return data, True, {
                **combat_result,
                **_restart_wave_after_safe_death(data, session),
            }

    if int(session["wave"]) == 10:
        session["phase"] = "queen"
        session["queen_lifepoints"] = BARBARIAN_ASSAULT_QUEEN_LIFEPOINTS
        session["omega_eggs"] = 0
        session["encounter"] = {}
        data["combat_encounter"] = {}
        data["barbarian_assault"] = session
        data["barbarian_assault_last_result"] = (
            "Wave 10 Penance cleared · build and fire eight Omega eggs."
        )
        return data, True, {
            **combat_result,
            "terminal": False,
            "wave_front_cleared": 10,
            "queen_started": True,
            "message": data["barbarian_assault_last_result"],
        }

    awarded = _award_points(data, int(session["wave"]), str(session["role"]))
    return data, True, {
        **combat_result,
        "duty": str(session["role"]),
        **_advance_after_wave(data, session, awarded),
    }


def leave_barbarian_assault_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the assault state and session are rebuilt fresh, so
    # the wave and queen writes land in new objects.
    data = dict(player_data)
    session = sanitize_barbarian_assault_state_pure(data)["barbarian_assault"]
    if not session:
        return data, False, {"reason": "No Barbarian Assault run is active."}
    data["barbarian_assault"] = {}
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == BARBARIAN_ASSAULT_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}
    _restore_previous_target(data, session)
    data["barbarian_assault_last_result"] = (
        "Left Barbarian Assault; current-wave progress was forfeited."
    )
    return data, True, {"message": data["barbarian_assault_last_result"]}


def buy_runner_boots_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the assault state and session are rebuilt fresh, so
    # the wave and queen writes land in new objects.
    data = dict(player_data)
    state = sanitize_barbarian_assault_state_pure(data)
    if state["barbarian_assault"]:
        return data, False, {"reason": "Finish or leave the current run first."}
    missing = [
        role_id
        for role_id, points in state["barbarian_assault_points"].items()
        if points < RUNNER_BOOTS_COST_PER_ROLE
    ]
    if missing:
        return data, False, {
            "reason": "Runner boots require 100 Honour points in every role."
        }
    data.update(state)
    data["barbarian_assault_points"] = {
        role_id: points - RUNNER_BOOTS_COST_PER_ROLE
        for role_id, points in state["barbarian_assault_points"].items()
    }
    inventory = dict(data.get("inventory") or {})
    inventory["Runner boots"] = _int(inventory.get("Runner boots")) + 1
    data["inventory"] = inventory
    data["barbarian_assault_last_result"] = "Bought Runner boots."
    return data, True, {"message": data["barbarian_assault_last_result"]}


def barbarian_assault_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_barbarian_assault_state_pure(player_data)
    session = state["barbarian_assault"]
    points = state["barbarian_assault_points"]
    active = bool(session)
    locked_reasons: list[str] = []
    if not state["barbarian_assault_tutorial_complete"]:
        locked_reasons.append("Complete Captain Cain's tutorial")
    if not active:
        activity_session = player_data.get("activity_session")
        active_id = (
            str(activity_session.get("active_id", ""))
            if isinstance(activity_session, Mapping)
            else ""
        )
        if active_id and active_id != BARBARIAN_ASSAULT_ACTIVITY_ID:
            locked_reasons.append("Finish the active persistent activity")
        encounter = player_data.get("combat_encounter")
        if isinstance(encounter, Mapping) and encounter:
            locked_reasons.append("Finish or leave the current Combat encounter")
    return {
        **state,
        "active": active,
        "session": session,
        "can_enter": not active and not locked_reasons,
        "can_buy_runner_boots": (
            not active
            and all(value >= RUNNER_BOOTS_COST_PER_ROLE for value in points.values())
        ),
        "locked_reasons": locked_reasons,
    }


def apply_barbarian_assault_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "tutorial":
        return complete_barbarian_assault_tutorial_pure(player_data)
    if action_id == "set_policy":
        return set_barbarian_assault_policy_pure(player_data, body)
    if action_id == "enter":
        return enter_barbarian_assault_pure(player_data, body)
    if action_id == "leave":
        return leave_barbarian_assault_pure(player_data)
    if action_id == "buy_runner_boots":
        return buy_runner_boots_pure(player_data)
    # Shallow on purpose: nothing is written to this save, and the only caller
    # (__init__._apply_barbarian_assault_command) discards it when ok is False.
    return dict(player_data), False, {
        "reason": "Unknown Barbarian Assault action."
    }
