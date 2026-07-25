"""Pure Pest Control entry, shared assault, rewards, and Void seal mechanics."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

try:
    from .logic_pure import apply_combat_burst_pure, player_combat_level_pure
    from .pet_logic import store_active_pet_pure
    from .summoning_logic import dismiss_familiar_pure
    from .pest_control_data import (
        PEST_CONTROL_ACTIVITY_ID,
        PEST_CONTROL_COMBAT_TARGET_ID,
        PEST_CONTROL_COMMENDATION_CAP,
        PEST_CONTROL_DEFENCE_RELIEF,
        PEST_CONTROL_DUTIES,
        PEST_CONTROL_EVENT_REVIEWS,
        PEST_CONTROL_FRONTS,
        PEST_CONTROL_LANDERS,
        PEST_CONTROL_LANDERS_BY_ID,
        PEST_CONTROL_PORTAL_COUNT,
        PEST_CONTROL_PORTAL_HEAL,
        PEST_CONTROL_SEAL_RELIEF,
        PEST_CONTROL_VOID_KNIGHT_LIFEPOINTS,
        VOID_SEAL_COST,
        VOID_SEAL_ITEMS,
        pest_control_portal_enemy_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure import apply_combat_burst_pure, player_combat_level_pure  # type: ignore
    from pet_logic import store_active_pet_pure  # type: ignore
    from summoning_logic import dismiss_familiar_pure  # type: ignore
    from pest_control_data import (  # type: ignore
        PEST_CONTROL_ACTIVITY_ID,
        PEST_CONTROL_COMBAT_TARGET_ID,
        PEST_CONTROL_COMMENDATION_CAP,
        PEST_CONTROL_DEFENCE_RELIEF,
        PEST_CONTROL_DUTIES,
        PEST_CONTROL_EVENT_REVIEWS,
        PEST_CONTROL_FRONTS,
        PEST_CONTROL_LANDERS,
        PEST_CONTROL_LANDERS_BY_ID,
        PEST_CONTROL_PORTAL_COUNT,
        PEST_CONTROL_PORTAL_HEAL,
        PEST_CONTROL_SEAL_RELIEF,
        PEST_CONTROL_VOID_KNIGHT_LIFEPOINTS,
        VOID_SEAL_COST,
        VOID_SEAL_ITEMS,
        pest_control_portal_enemy_pure,
    )


PEST_CONTROL_STATE_VERSION = 1
_VALID_MODES = frozenset({"casual", "advanced"})
_VALID_DUTIES = frozenset(duty for duty, _label in PEST_CONTROL_DUTIES)


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _active_follower(player_data: Mapping[str, Any]) -> Mapping[str, Any]:
    state = player_data.get("summoning_state")
    if not isinstance(state, Mapping):
        return {}
    follower = state.get("active_follower")
    return follower if isinstance(follower, Mapping) else {}


def _dismiss_follower(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, str]:
    follower = _active_follower(player_data)
    kind = str(follower.get("kind", ""))
    # Shallow on purpose: both exits dismiss nothing, and the two dismissal
    # helpers below build their own copies rather than writing to this save.
    if not kind:
        return dict(player_data), True, ""
    if kind == "familiar":
        updated, ok, _info = dismiss_familiar_pure(player_data)
        return updated, ok, kind
    if kind == "pet":
        updated, ok = store_active_pet_pure(player_data, location="bank")
        return updated, ok, kind
    return dict(player_data), False, kind


def default_pest_control_state_pure() -> dict[str, Any]:
    return {
        "pest_control": {},
        "pest_control_policy": {
            "automation_mode": "casual",
            "lander_id": "novice",
            "duty": "assault",
        },
        "pest_control_commendations": 0,
        "pest_control_games_won": 0,
        "pest_control_games_lost": 0,
        "pest_control_last_result": "",
    }


def sanitize_pest_control_policy_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    lander_id = str(source.get("lander_id", "novice"))
    duty = str(source.get("duty", "assault"))
    return {
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "lander_id": lander_id if lander_id in PEST_CONTROL_LANDERS_BY_ID else "novice",
        "duty": duty if duty in _VALID_DUTIES else "assault",
    }


def sanitize_pest_control_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    lander_id = str(raw.get("lander_id", "novice"))
    if lander_id not in PEST_CONTROL_LANDERS_BY_ID:
        lander_id = "novice"
    lander = PEST_CONTROL_LANDERS_BY_ID[lander_id]
    portal_index = _int(raw.get("portal_index"), maximum=PEST_CONTROL_PORTAL_COUNT - 1)
    portal_lifepoints = _int(
        raw.get("portal_lifepoints", lander.portal_lifepoints),
        lander.portal_lifepoints,
        maximum=lander.portal_lifepoints,
    )
    mode = str(raw.get("automation_mode", "casual"))
    duty = str(raw.get("duty", "assault"))
    encounter = raw.get("encounter")
    return {
        "version": PEST_CONTROL_STATE_VERSION,
        "review": _int(raw.get("review"), maximum=PEST_CONTROL_EVENT_REVIEWS - 1),
        "lander_id": lander_id,
        "portal_index": portal_index,
        "portal_lifepoints": max(1, portal_lifepoints),
        "knight_lifepoints": _int(
            raw.get("knight_lifepoints", PEST_CONTROL_VOID_KNIGHT_LIFEPOINTS),
            PEST_CONTROL_VOID_KNIGHT_LIFEPOINTS,
            maximum=PEST_CONTROL_VOID_KNIGHT_LIFEPOINTS,
        ),
        "contribution": _int(raw.get("contribution"), maximum=999_999),
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "duty": duty if duty in _VALID_DUTIES else "assault",
        "previous_combat_target": str(raw.get("previous_combat_target", ""))[:120],
        "encounter": copy.deepcopy(encounter) if isinstance(encounter, Mapping) else {},
    }


def sanitize_pest_control_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    session = sanitize_pest_control_session_pure(source.get("pest_control"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", PEST_CONTROL_ACTIVITY_ID}:
        session = {}
    return {
        "pest_control": session,
        "pest_control_policy": sanitize_pest_control_policy_pure(
            source.get("pest_control_policy")
        ),
        "pest_control_commendations": _int(
            source.get("pest_control_commendations"),
            maximum=PEST_CONTROL_COMMENDATION_CAP,
        ),
        "pest_control_games_won": _int(source.get("pest_control_games_won")),
        "pest_control_games_lost": _int(source.get("pest_control_games_lost")),
        "pest_control_last_result": str(
            source.get("pest_control_last_result", "") or ""
        )[:500],
    }


def _best_lander_id(combat_level: int) -> str:
    eligible = [
        lander for lander in PEST_CONTROL_LANDERS if combat_level >= lander.combat_level
    ]
    return eligible[-1].lander_id if eligible else "novice"


def set_pest_control_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the pest control state and session are rebuilt fresh,
    # and the follower alias this module reads is never written.
    data = dict(player_data)
    state = sanitize_pest_control_state_pure(data)
    if state["pest_control"]:
        return data, False, {"reason": "Finish or leave the current game first."}
    candidate = dict(state["pest_control_policy"])
    candidate.update(dict(payload or {}))
    policy = sanitize_pest_control_policy_pure(candidate)
    if policy["automation_mode"] == "advanced":
        required = PEST_CONTROL_LANDERS_BY_ID[policy["lander_id"]].combat_level
        actual = player_combat_level_pure(data)
        if actual < required:
            return data, False, {
                "reason": f"{policy['lander_id'].title()} lander requires combat level {required}."
            }
    data.update(state)
    data["pest_control_policy"] = policy
    return data, True, {"message": "Pest Control plan saved.", "policy": policy}


def _seal_charge(item_name: str) -> int:
    if item_name not in VOID_SEAL_ITEMS:
        return 0
    return int(item_name.removeprefix("Void seal (").removesuffix(")"))


def _has_void_seal(player_data: Mapping[str, Any]) -> bool:
    equipment = player_data.get("equipment")
    if isinstance(equipment, Mapping) and str(equipment.get("neck", "")) in VOID_SEAL_ITEMS:
        return True
    inventory = player_data.get("inventory")
    return isinstance(inventory, Mapping) and any(
        _int(inventory.get(item_name)) > 0 for item_name in VOID_SEAL_ITEMS
    )


def _consume_void_seal_charge(data: dict[str, Any]) -> tuple[bool, int]:
    equipment = dict(data.get("equipment") or {})
    equipped = str(equipment.get("neck", ""))
    if equipped in VOID_SEAL_ITEMS:
        charge = _seal_charge(equipped)
        if charge > 1:
            equipment["neck"] = f"Void seal ({charge - 1})"
        else:
            equipment.pop("neck", None)
        data["equipment"] = equipment
        return True, charge - 1

    inventory = dict(data.get("inventory") or {})
    for item_name in VOID_SEAL_ITEMS:
        if _int(inventory.get(item_name)) <= 0:
            continue
        charge = _seal_charge(item_name)
        remaining = _int(inventory.get(item_name)) - 1
        if remaining:
            inventory[item_name] = remaining
        else:
            inventory.pop(item_name, None)
        if charge > 1:
            next_name = f"Void seal ({charge - 1})"
            inventory[next_name] = _int(inventory.get(next_name)) + 1
        data["inventory"] = inventory
        return True, charge - 1
    return False, 0


def enter_pest_control_pure(
    player_data: Mapping[str, Any],
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    payload = dict(payload or {})
    data, ok, info = set_pest_control_policy_pure(player_data, payload)
    if not ok:
        return data, False, info
    state = sanitize_pest_control_state_pure(data)
    if state["pest_control"]:
        return data, False, {"reason": "A Pest Control game is already active."}
    combat_level = player_combat_level_pure(data)
    if combat_level < 40:
        return data, False, {"reason": "Pest Control requires combat level 40."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != PEST_CONTROL_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {"reason": "Finish or leave the current Combat encounter first."}
    follower = _active_follower(data)
    if follower and not bool(payload.get("confirm_dismiss_follower", False)):
        return data, False, {
            "reason": "Pets and familiars cannot board the lander.",
            "requires_confirmation": True,
            "follower_kind": str(follower.get("kind", "follower")),
        }
    dismissed = ""
    if follower:
        data, ok, dismissed = _dismiss_follower(data)
        if not ok:
            # Shallow rollback: the dismissal helpers return new saves instead
            # of writing to this one, so nothing nested here was touched.
            return dict(player_data), False, {
                "reason": "The active follower could not be dismissed safely."
            }
        state = sanitize_pest_control_state_pure(data)

    policy = state["pest_control_policy"]
    lander_id = (
        _best_lander_id(combat_level)
        if policy["automation_mode"] == "casual"
        else policy["lander_id"]
    )
    lander = PEST_CONTROL_LANDERS_BY_ID[lander_id]
    previous = str(data.get("current_combat_target", ""))[:120]
    data.update(state)
    data["pest_control"] = {
        "version": PEST_CONTROL_STATE_VERSION,
        "review": 0,
        "lander_id": lander_id,
        "portal_index": 0,
        "portal_lifepoints": lander.portal_lifepoints,
        "knight_lifepoints": PEST_CONTROL_VOID_KNIGHT_LIFEPOINTS,
        "contribution": 0,
        "automation_mode": policy["automation_mode"],
        "duty": policy["duty"],
        "previous_combat_target": previous,
        "encounter": {
            "target_id": PEST_CONTROL_COMBAT_TARGET_ID,
            "enemy_lifepoints": lander.portal_lifepoints,
        },
    }
    data["activity_session"] = {"active_id": PEST_CONTROL_ACTIVITY_ID}
    data["current_utility"] = PEST_CONTROL_ACTIVITY_ID
    data["current_combat_target"] = PEST_CONTROL_COMBAT_TARGET_ID
    data["combat_encounter"] = copy.deepcopy(data["pest_control"]["encounter"])
    data["pest_control_last_result"] = (
        f"Boarded the {lander.display_name.lower()} · first portal front ready"
    )
    return data, True, {
        "message": data["pest_control_last_result"],
        "lander_id": lander_id,
        "dismissed_follower": dismissed,
    }


def _end_game(data: dict[str, Any], session: Mapping[str, Any], message: str) -> None:
    data["pest_control"] = {}
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == PEST_CONTROL_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(session.get("previous_combat_target", ""))
    data["pest_control_last_result"] = message[:500]


def leave_pest_control_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the pest control state and session are rebuilt fresh,
    # and the follower alias this module reads is never written.
    data = dict(player_data)
    state = sanitize_pest_control_state_pure(data)
    session = state["pest_control"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != PEST_CONTROL_ACTIVITY_ID:
        return data, False, {"reason": "No Pest Control game is active."}
    message = "Left Pest Control; the unfinished game paid no reward."
    _end_game(data, session, message)
    return data, True, {"message": message}


def _choose_duty(data: Mapping[str, Any], session: Mapping[str, Any]) -> str:
    if session["automation_mode"] == "advanced":
        requested = str(session.get("duty", "assault"))
        return requested if requested in _VALID_DUTIES else "assault"
    if int(session["knight_lifepoints"]) <= 900:
        return "seal" if _has_void_seal(data) else "defend"
    return "assault"


def _win_game(data: dict[str, Any], session: Mapping[str, Any]) -> dict[str, Any]:
    lander = PEST_CONTROL_LANDERS_BY_ID[str(session["lander_id"])]
    combat_level = player_combat_level_pure(data)
    coins = combat_level * 10
    before = _int(data.get("pest_control_commendations"))
    after = min(PEST_CONTROL_COMMENDATION_CAP, before + lander.commendations)
    awarded = after - before
    data["pest_control_commendations"] = after
    data["coins"] = _int(data.get("coins")) + coins
    data["pest_control_games_won"] = _int(data.get("pest_control_games_won")) + 1
    message = (
        f"Pest Control won · +{coins:,} coins · +{awarded} commendations"
    )
    _end_game(data, session, message)
    return {
        "terminal": True,
        "won": True,
        "coins": coins,
        "commendations": awarded,
        "message": message,
    }


def _lose_game(data: dict[str, Any], session: Mapping[str, Any], reason: str) -> dict[str, Any]:
    data["pest_control_games_lost"] = _int(data.get("pest_control_games_lost")) + 1
    message = f"Pest Control lost · {reason} · no reward"
    _end_game(data, session, message)
    return {
        "terminal": True,
        "won": False,
        "coins": 0,
        "commendations": 0,
        "message": message,
    }


def apply_pest_control_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    productive: bool,
    duty: str | None = None,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the pest control state and session are rebuilt fresh,
    # and the follower alias this module reads is never written.
    data = dict(player_data)
    state = sanitize_pest_control_state_pure(data)
    session = state["pest_control"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != PEST_CONTROL_ACTIVITY_ID:
        return data, False, {"reason": "Enter Pest Control before training it."}

    lander = PEST_CONTROL_LANDERS_BY_ID[str(session["lander_id"])]
    front_index = int(session["portal_index"])
    front = PEST_CONTROL_FRONTS[front_index]
    chosen = "idle"
    combat_result: dict[str, Any] = {}
    relief = 0
    if productive:
        chosen = str(duty or _choose_duty(data, session))
        if chosen not in _VALID_DUTIES:
            chosen = _choose_duty(data, session)
        if chosen == "assault":
            data["current_combat_target"] = PEST_CONTROL_COMBAT_TARGET_ID
            data["combat_encounter"] = copy.deepcopy(session["encounter"])
            enemy = pest_control_portal_enemy_pure(session["lander_id"], front_index)
            data, ok, combat_result = apply_combat_burst_pure(
                data,
                {PEST_CONTROL_COMBAT_TARGET_ID: enemy},
                equipment_data or {},
                ticks=6,
                rng=rng,
                live_cadence=True,
                stop_after_first_kill=True,
                safe_death=True,
                allow_bank_run=False,
            )
            if not ok:
                # Shallow rollback: the combat engine copies its own input, so
                # no nested value of the caller's save was written through.
                return dict(player_data), False, combat_result
            player_damage = _int(combat_result.get("player_damage"))
            session["portal_lifepoints"] = _int(
                combat_result.get("enemy_lifepoints", session["portal_lifepoints"]),
                maximum=lander.portal_lifepoints,
            )
            session["contribution"] += player_damage
            session["encounter"] = copy.deepcopy(data.get("combat_encounter") or {})
        elif chosen == "defend":
            relief = PEST_CONTROL_DEFENCE_RELIEF
            session["contribution"] += 50
        else:
            used, remaining = _consume_void_seal_charge(data)
            if not used:
                chosen = "defend"
                relief = PEST_CONTROL_DEFENCE_RELIEF
                session["contribution"] += 50
            else:
                relief = PEST_CONTROL_SEAL_RELIEF
                combat_result["seal_charges_remaining"] = remaining

    crowd_damage = (
        lander.crowd_portal_damage * front.crowd_damage_numerator // 100
        + front.crowd_damage_bonus
    )
    portal_healing = min(
        front.portal_healing,
        max(0, lander.portal_lifepoints - int(session["portal_lifepoints"])),
    )
    session["portal_lifepoints"] = max(
        0,
        int(session["portal_lifepoints"]) + portal_healing - crowd_damage,
    )
    portal_destroyed = int(session["portal_lifepoints"]) <= 0
    if portal_destroyed:
        session["portal_index"] += 1
        if int(session["portal_index"]) >= PEST_CONTROL_PORTAL_COUNT:
            result = _win_game(data, session)
            return data, True, {
                **combat_result,
                **result,
                "duty": chosen,
                "portal_destroyed": True,
                "crowd_damage": crowd_damage,
                "portal_healing": portal_healing,
            }
        session["knight_lifepoints"] = min(
            PEST_CONTROL_VOID_KNIGHT_LIFEPOINTS,
            int(session["knight_lifepoints"]) + PEST_CONTROL_PORTAL_HEAL,
        )

    pressure = max(0, front.knight_pressure - relief)
    session["knight_lifepoints"] = max(
        0, int(session["knight_lifepoints"]) - pressure
    )
    if int(session["knight_lifepoints"]) <= 0:
        result = _lose_game(data, session, "the Void Knight fell")
        return data, True, {
            **combat_result,
            **result,
            "duty": chosen,
            "portal_destroyed": portal_destroyed,
            "crowd_damage": crowd_damage,
            "portal_healing": portal_healing,
            "knight_pressure": pressure,
        }

    if portal_destroyed:
        session["portal_lifepoints"] = lander.portal_lifepoints
        session["encounter"] = {
            "target_id": PEST_CONTROL_COMBAT_TARGET_ID,
            "enemy_lifepoints": lander.portal_lifepoints,
        }
        data["combat_encounter"] = copy.deepcopy(session["encounter"])
    else:
        session["encounter"] = copy.deepcopy(data.get("combat_encounter") or {})
        session["encounter"]["target_id"] = PEST_CONTROL_COMBAT_TARGET_ID
        session["encounter"]["enemy_lifepoints"] = int(session["portal_lifepoints"])
        data["combat_encounter"] = copy.deepcopy(session["encounter"])

    session["review"] += 1
    if int(session["review"]) >= PEST_CONTROL_EVENT_REVIEWS:
        result = _lose_game(data, session, "the lander returned before every portal fell")
        return data, True, {
            **combat_result,
            **result,
            "duty": chosen,
            "portal_destroyed": portal_destroyed,
            "crowd_damage": crowd_damage,
            "portal_healing": portal_healing,
            "knight_pressure": pressure,
        }

    data.update(state)
    data["pest_control"] = session
    data["current_combat_target"] = PEST_CONTROL_COMBAT_TARGET_ID
    status = (
        f"Pest Control · portal {int(session['portal_index']) + 1}/4 · "
        f"{chosen.replace('_', ' ')} · portal {int(session['portal_lifepoints']):,} LP · "
        f"knight {int(session['knight_lifepoints']):,} LP"
    )
    data["pest_control_last_result"] = status
    return data, True, {
        **combat_result,
        "terminal": False,
        "won": False,
        "duty": chosen,
        "portal_destroyed": portal_destroyed,
        "crowd_damage": crowd_damage,
        "portal_healing": portal_healing,
        "knight_pressure": pressure,
        "portal_index": int(session["portal_index"]),
        "portal_lifepoints": int(session["portal_lifepoints"]),
        "knight_lifepoints": int(session["knight_lifepoints"]),
        "contribution": int(session["contribution"]),
        "status": status,
    }


def buy_void_seal_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the pest control state and session are rebuilt fresh,
    # and the follower alias this module reads is never written.
    data = dict(player_data)
    state = sanitize_pest_control_state_pure(data)
    if state["pest_control"]:
        return data, False, {"reason": "Finish the current Pest Control game first."}
    wallet = state["pest_control_commendations"]
    if wallet < VOID_SEAL_COST:
        return data, False, {"reason": f"Requires {VOID_SEAL_COST} commendations."}
    inventory = dict(data.get("inventory") or {})
    inventory["Void seal (8)"] = _int(inventory.get("Void seal (8)")) + 1
    data.update(state)
    data["inventory"] = inventory
    data["pest_control_commendations"] = wallet - VOID_SEAL_COST
    return data, True, {"message": "Bought a Void seal (8)."}


def pest_control_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_pest_control_state_pure(player_data)
    session = state["pest_control"]
    combat_level = player_combat_level_pure(player_data)
    policy = state["pest_control_policy"]
    available = tuple(
        {
            "lander_id": lander.lander_id,
            "display_name": lander.display_name,
            "combat_level": lander.combat_level,
            "portal_lifepoints": lander.portal_lifepoints,
            "commendations": lander.commendations,
            "eligible": combat_level >= lander.combat_level,
        }
        for lander in PEST_CONTROL_LANDERS
    )
    return {
        **state,
        "active": bool(session),
        "combat_level": combat_level,
        "entry_locked_reason": (
            "" if combat_level >= 40 else "Requires combat level 40."
        ),
        "available_landers": available,
        "selected_lander_id": (
            str(session.get("lander_id"))
            if session
            else (
                _best_lander_id(combat_level)
                if policy["automation_mode"] == "casual"
                else policy["lander_id"]
            )
        ),
        "seal_available": _has_void_seal(player_data),
        "seal_cost": VOID_SEAL_COST,
        "commendation_cap": PEST_CONTROL_COMMENDATION_CAP,
    }


def apply_pest_control_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if action_id == "enter":
        return enter_pest_control_pure(player_data, payload)
    if action_id == "leave":
        return leave_pest_control_pure(player_data)
    if action_id == "set_policy":
        return set_pest_control_policy_pure(player_data, payload)
    if action_id == "buy_void_seal":
        return buy_void_seal_pure(player_data)
    # Shallow on purpose: nothing ran, and callers discard the save they get
    # back on a failed command.
    return dict(player_data), False, {"reason": "Unknown Pest Control command."}
