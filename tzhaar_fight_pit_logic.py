"""Pure TzHaar Fight Pit last-standing and TokKul mechanics."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

try:
    from .logic_pure import (
        apply_combat_burst_pure,
        apply_thieving_damage_pure,
        combat_max_lifepoints_pure,
        player_combat_level_pure,
    )
    from .tzhaar_fight_pit_data import (
        TZHAAR_FIGHT_PIT_ACTIVITY_ID,
        TZHAAR_FIGHT_PIT_ATTRITION_DIVISOR,
        TZHAAR_FIGHT_PIT_COMBAT_TARGET_ID,
        TZHAAR_FIGHT_PIT_COMBAT_TICKS_PER_REVIEW,
        TZHAAR_FIGHT_PIT_FIRE_CAPE_ITEM,
        TZHAAR_FIGHT_PIT_POLICIES,
        TZHAAR_FIGHT_PIT_PRESSURE_DAMAGE_DIVISOR,
        TZHAAR_FIGHT_PIT_PRESSURE_START_REVIEW,
        TZHAAR_FIGHT_PIT_ROSTER_SIZE,
        TZHAAR_FIGHT_PIT_SOURCE,
        TZHAAR_FIGHT_PIT_TOKKUL_ITEM,
    )
except ImportError:  # pragma: no cover - flat imports used by tests
    from logic_pure import (  # type: ignore
        apply_combat_burst_pure,
        apply_thieving_damage_pure,
        combat_max_lifepoints_pure,
        player_combat_level_pure,
    )
    from tzhaar_fight_pit_data import (  # type: ignore
        TZHAAR_FIGHT_PIT_ACTIVITY_ID,
        TZHAAR_FIGHT_PIT_ATTRITION_DIVISOR,
        TZHAAR_FIGHT_PIT_COMBAT_TARGET_ID,
        TZHAAR_FIGHT_PIT_COMBAT_TICKS_PER_REVIEW,
        TZHAAR_FIGHT_PIT_FIRE_CAPE_ITEM,
        TZHAAR_FIGHT_PIT_POLICIES,
        TZHAAR_FIGHT_PIT_PRESSURE_DAMAGE_DIVISOR,
        TZHAAR_FIGHT_PIT_PRESSURE_START_REVIEW,
        TZHAAR_FIGHT_PIT_ROSTER_SIZE,
        TZHAAR_FIGHT_PIT_SOURCE,
        TZHAAR_FIGHT_PIT_TOKKUL_ITEM,
    )


TZHAAR_FIGHT_PIT_STATE_VERSION = 1
_VALID_POLICIES = frozenset(policy_id for policy_id, _label in TZHAAR_FIGHT_PIT_POLICIES)


def _int(value: Any, default: int = 0, *, minimum: int = 0, maximum: int = 2_147_483_647) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _empty_activity_session() -> dict[str, str]:
    return {"active_id": ""}


def default_tzhaar_fight_pit_state_pure() -> dict[str, Any]:
    return {
        "tzhaar_fight_pit": {},
        "tzhaar_fight_pit_policy": "casual",
        "tzhaar_fight_pit_matches": 0,
        "tzhaar_fight_pit_wins": 0,
        "tzhaar_fight_pit_losses": 0,
        "tzhaar_fight_pit_forfeits": 0,
        "tzhaar_fight_pit_tokkul_earned": 0,
        "tzhaar_fight_pit_last_result": "",
    }


def _opponent_stats(combat_level: int) -> dict[str, int]:
    core = max(1, min(99, round(combat_level * 0.75)))
    constitution = max(10, min(99, round(combat_level * 0.75 + 8)))
    return {
        "attack": core,
        "strength": core,
        "defence": core,
        "hitpoints": constitution * 10,
        "magic": core,
        "ranged": core,
    }


def _new_roster(player_data: Mapping[str, Any], match_number: int) -> list[dict[str, Any]]:
    player_level = player_combat_level_pure(player_data)
    offsets = (-12, 0, 12)
    roster = []
    for index in range(TZHAAR_FIGHT_PIT_ROSTER_SIZE):
        level = max(3, min(138, player_level + offsets[index]))
        maximum = _opponent_stats(level)["hitpoints"]
        roster.append(
            {
                "opponent_id": f"fight-pit-{match_number}-{index + 1}",
                "display_name": f"Fight Pit rival {index + 1} (level {level})",
                "combat_level": level,
                "lifepoints": maximum,
                "maximum_lifepoints": maximum,
                "encounter": {},
            }
        )
    return roster


def _sanitize_opponent(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    opponent_id = str(raw.get("opponent_id", ""))[:80]
    level = _int(raw.get("combat_level"), 3, minimum=3, maximum=138)
    maximum = _opponent_stats(level)["hitpoints"]
    lifepoints = _int(raw.get("lifepoints"), maximum, maximum=maximum)
    if not opponent_id or lifepoints <= 0:
        return {}
    encounter = raw.get("encounter")
    return {
        "opponent_id": opponent_id,
        "display_name": str(raw.get("display_name", f"Fight Pit rival (level {level})"))[:100],
        "combat_level": level,
        "lifepoints": lifepoints,
        "maximum_lifepoints": maximum,
        "encounter": copy.deepcopy(dict(encounter)) if isinstance(encounter, Mapping) else {},
    }


def sanitize_tzhaar_fight_pit_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    roster = []
    seen = set()
    for row in raw.get("roster", ()) or ():
        opponent = _sanitize_opponent(row)
        opponent_id = opponent.get("opponent_id")
        if opponent and opponent_id not in seen:
            seen.add(opponent_id)
            roster.append(opponent)
    if not roster:
        return {}
    engaged = str(raw.get("engaged_opponent_id", ""))[:80]
    if engaged not in seen:
        engaged = ""
    policy = str(raw.get("policy", "casual"))
    return {
        "version": TZHAAR_FIGHT_PIT_STATE_VERSION,
        "match_number": _int(raw.get("match_number"), 1, minimum=1),
        "review": _int(raw.get("review")),
        "policy": policy if policy in _VALID_POLICIES else "casual",
        "roster": roster,
        "engaged_opponent_id": engaged,
        "pending_tokkul": _int(raw.get("pending_tokkul")),
        "player_kills": _int(raw.get("player_kills"), maximum=TZHAAR_FIGHT_PIT_ROSTER_SIZE),
        "other_eliminations": _int(raw.get("other_eliminations"), maximum=TZHAAR_FIGHT_PIT_ROSTER_SIZE),
        "previous_combat_target": str(raw.get("previous_combat_target", ""))[:120],
    }


def sanitize_tzhaar_fight_pit_state_pure(player_data: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_tzhaar_fight_pit_state_pure()
    policy = str(source.get("tzhaar_fight_pit_policy", "casual"))
    session = sanitize_tzhaar_fight_pit_session_pure(source.get("tzhaar_fight_pit"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", TZHAAR_FIGHT_PIT_ACTIVITY_ID}:
        session = {}
    return {
        **defaults,
        "tzhaar_fight_pit": session,
        "tzhaar_fight_pit_policy": policy if policy in _VALID_POLICIES else "casual",
        "tzhaar_fight_pit_matches": _int(source.get("tzhaar_fight_pit_matches")),
        "tzhaar_fight_pit_wins": _int(source.get("tzhaar_fight_pit_wins")),
        "tzhaar_fight_pit_losses": _int(source.get("tzhaar_fight_pit_losses")),
        "tzhaar_fight_pit_forfeits": _int(source.get("tzhaar_fight_pit_forfeits")),
        "tzhaar_fight_pit_tokkul_earned": _int(source.get("tzhaar_fight_pit_tokkul_earned")),
        "tzhaar_fight_pit_last_result": str(source.get("tzhaar_fight_pit_last_result", ""))[:500],
    }


def _choose_opponent(session: Mapping[str, Any]) -> str:
    roster = list(session.get("roster", ()))
    if not roster:
        return ""
    reverse = str(session.get("policy")) == "aggressive"
    chosen = sorted(roster, key=lambda row: (int(row["combat_level"]), str(row["opponent_id"])), reverse=reverse)[0]
    return str(chosen["opponent_id"])


def _enemy_for(opponent: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    level = int(opponent["combat_level"])
    return {
        TZHAAR_FIGHT_PIT_COMBAT_TARGET_ID: {
            "display_name": str(opponent["display_name"]),
            "level": level,
            "group": "TzHaar Fight Pit",
            "stats": _opponent_stats(level),
            "bonuses": {},
            "attack_speed": 4,
            "drops": {"guaranteed": (), "tables": ()},
            "xp_multiplier": 1.0,
            "source": TZHAAR_FIGHT_PIT_SOURCE + "; disclosed bounded simulated opponent",
        }
    }


def _restore_match_resources(data: dict[str, Any]) -> None:
    data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
    data["combat_prayer_points"] = max(1, _int(data.get("prayer_level"), 1, minimum=1)) * 10
    data["combat_special_attack_energy"] = 100
    data["combat_status_effects"] = {}


def _finish(data: dict[str, Any], session: Mapping[str, Any], message: str) -> None:
    data["tzhaar_fight_pit"] = {}
    data["activity_session"] = _empty_activity_session()
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(session.get("previous_combat_target", ""))
    data["tzhaar_fight_pit_last_result"] = message
    _restore_match_resources(data)


def set_tzhaar_fight_pit_policy_pure(player_data: Mapping[str, Any], policy: str) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_tzhaar_fight_pit_state_pure(data)
    if state["tzhaar_fight_pit"]:
        return data, False, {"reason": "Finish or leave the current Fight Pit match first."}
    if policy not in _VALID_POLICIES:
        return data, False, {"reason": "Unknown Fight Pit policy."}
    data.update(state)
    data["tzhaar_fight_pit_policy"] = policy
    return data, True, {"message": "Fight Pit plan saved.", "policy": policy}


def enter_tzhaar_fight_pit_pure(player_data: Mapping[str, Any], policy: str | None = None) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_tzhaar_fight_pit_state_pure(data)
    if state["tzhaar_fight_pit"]:
        return data, False, {"reason": "A Fight Pit match is already active."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != TZHAAR_FIGHT_PIT_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {"reason": "Finish or leave the current Combat encounter first."}
    loadout = data.get("combat_supply_loadout")
    if isinstance(loadout, Mapping) and _int(loadout.get("cannonballs")) > 0:
        return data, False, {"reason": "Dwarf multicannons are not allowed in the Fight Pit."}
    selected_policy = str(policy or state["tzhaar_fight_pit_policy"])
    if selected_policy not in _VALID_POLICIES:
        return data, False, {"reason": "Unknown Fight Pit policy."}
    match_number = state["tzhaar_fight_pit_matches"] + 1
    session = {
        "version": TZHAAR_FIGHT_PIT_STATE_VERSION,
        "match_number": match_number,
        "review": 0,
        "policy": selected_policy,
        "roster": _new_roster(data, match_number),
        "engaged_opponent_id": "",
        "pending_tokkul": 0,
        "player_kills": 0,
        "other_eliminations": 0,
        "previous_combat_target": str(data.get("current_combat_target", ""))[:120],
    }
    session["engaged_opponent_id"] = _choose_opponent(session)
    data.update(state)
    data["tzhaar_fight_pit_policy"] = selected_policy
    data["tzhaar_fight_pit_matches"] = match_number
    data["tzhaar_fight_pit"] = session
    data["activity_session"] = {"active_id": TZHAAR_FIGHT_PIT_ACTIVITY_ID}
    data["current_utility"] = TZHAAR_FIGHT_PIT_ACTIVITY_ID
    data["combat_encounter"] = {}
    data["current_combat_target"] = TZHAAR_FIGHT_PIT_COMBAT_TARGET_ID
    data["tzhaar_fight_pit_last_result"] = "Entered the TzHaar Fight Pit against three simulated rivals."
    return data, True, {"message": data["tzhaar_fight_pit_last_result"], "roster": copy.deepcopy(session["roster"])}


def _fire_cape_equipped(data: Mapping[str, Any]) -> bool:
    equipment = data.get("equipment")
    if not isinstance(equipment, Mapping):
        return False
    cape = equipment.get("cape")
    if isinstance(cape, Mapping):
        cape = cape.get("item_name") or cape.get("name")
    return str(cape) == TZHAAR_FIGHT_PIT_FIRE_CAPE_ITEM


def _settle_win(data: dict[str, Any], session: Mapping[str, Any]) -> dict[str, Any]:
    base = int(session["pending_tokkul"])
    multiplier = 2 if _fire_cape_equipped(data) else 1
    reward = base * multiplier
    inventory = data.get("inventory")
    inventory = copy.deepcopy(dict(inventory)) if isinstance(inventory, Mapping) else {}
    inventory[TZHAAR_FIGHT_PIT_TOKKUL_ITEM] = _int(inventory.get(TZHAAR_FIGHT_PIT_TOKKUL_ITEM)) + reward
    data["inventory"] = inventory
    data["tzhaar_fight_pit_wins"] = _int(data.get("tzhaar_fight_pit_wins")) + 1
    data["tzhaar_fight_pit_tokkul_earned"] = _int(data.get("tzhaar_fight_pit_tokkul_earned")) + reward
    message = f"Fight Pit champion · +{reward:,} TokKul"
    if multiplier == 2:
        message += " · Fire cape doubled the reward"
    _finish(data, session, message)
    return {"terminal": True, "outcome": "win", "tokkul": reward, "base_tokkul": base, "fire_cape_multiplier": multiplier, "message": message}


def _settle_loss(data: dict[str, Any], session: Mapping[str, Any], *, reason: str) -> dict[str, Any]:
    data["tzhaar_fight_pit_losses"] = _int(data.get("tzhaar_fight_pit_losses")) + 1
    message = f"Safe Fight Pit defeat · {reason} · no TokKul awarded"
    _finish(data, session, message)
    return {"terminal": True, "outcome": "loss", "tokkul": 0, "message": message}


def _apply_other_attrition(session: dict[str, Any], engaged_id: str) -> list[str]:
    eliminated = []
    survivors = []
    for opponent in session["roster"]:
        if opponent["opponent_id"] == engaged_id:
            survivors.append(opponent)
            continue
        damage = max(1, int(opponent["maximum_lifepoints"]) // TZHAAR_FIGHT_PIT_ATTRITION_DIVISOR)
        opponent["lifepoints"] = max(0, int(opponent["lifepoints"]) - damage)
        opponent["encounter"] = {}
        if opponent["lifepoints"] <= 0:
            eliminated.append(str(opponent["opponent_id"]))
        else:
            survivors.append(opponent)
    session["roster"] = survivors
    session["other_eliminations"] += len(eliminated)
    return eliminated


def apply_tzhaar_fight_pit_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_tzhaar_fight_pit_state_pure(data)
    session = state["tzhaar_fight_pit"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != TZHAAR_FIGHT_PIT_ACTIVITY_ID:
        return data, False, {"reason": "Enter the TzHaar Fight Pit before training it."}
    data.update(state)
    if not session["engaged_opponent_id"]:
        session["engaged_opponent_id"] = _choose_opponent(session)
    opponent = next((row for row in session["roster"] if row["opponent_id"] == session["engaged_opponent_id"]), None)
    if opponent is None:
        return data, True, _settle_win(data, session)

    data["current_combat_target"] = TZHAAR_FIGHT_PIT_COMBAT_TARGET_ID
    encounter = copy.deepcopy(opponent["encounter"])
    encounter["target_id"] = TZHAAR_FIGHT_PIT_COMBAT_TARGET_ID
    encounter["enemy_lifepoints"] = int(opponent["lifepoints"])
    data["combat_encounter"] = encounter
    auto_flee = bool(data.get("combat_auto_flee", True))
    data["combat_auto_flee"] = False
    data, ok, combat = apply_combat_burst_pure(
        data,
        _enemy_for(opponent),
        equipment_data or {},
        ticks=TZHAAR_FIGHT_PIT_COMBAT_TICKS_PER_REVIEW,
        rng=rng or (lambda: 0.5),
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=True,
        allow_bank_run=False,
    )
    data["combat_auto_flee"] = auto_flee
    if not ok:
        return copy.deepcopy(dict(player_data)), False, {"reason": "Fight Pit combat setup is not runnable.", "combat": combat}
    session["review"] += 1
    if combat.get("died"):
        data["tzhaar_fight_pit"] = session
        return data, True, {"combat": combat, **_settle_loss(data, session, reason="you were eliminated")}

    player_kill = None
    if combat.get("killed"):
        player_kill = dict(opponent)
        session["roster"] = [row for row in session["roster"] if row["opponent_id"] != opponent["opponent_id"]]
        session["pending_tokkul"] += int(opponent["combat_level"])
        session["player_kills"] += 1
        session["engaged_opponent_id"] = ""
        data["combat_encounter"] = {}
    else:
        encounter_after = data.get("combat_encounter")
        if isinstance(encounter_after, Mapping):
            opponent["lifepoints"] = _int(encounter_after.get("enemy_lifepoints"), int(opponent["lifepoints"]), maximum=int(opponent["maximum_lifepoints"]))
            opponent["encounter"] = copy.deepcopy(dict(encounter_after))

    other_eliminated = _apply_other_attrition(session, str(session["engaged_opponent_id"]))
    if not session["roster"]:
        data["tzhaar_fight_pit"] = session
        return data, True, {"combat": combat, "player_kill": player_kill, "other_eliminated": other_eliminated, **_settle_win(data, session)}

    pressure = None
    if session["review"] >= TZHAAR_FIGHT_PIT_PRESSURE_START_REVIEW:
        damage = max(1, combat_max_lifepoints_pure(data) // TZHAAR_FIGHT_PIT_PRESSURE_DAMAGE_DIVISOR)
        data, pressure = apply_thieving_damage_pure(data, damage, source="tzhaar_fight_pit_pressure", safe_death=True)
        if pressure.get("died"):
            data["tzhaar_fight_pit"] = session
            return data, True, {"combat": combat, "pressure": pressure, **_settle_loss(data, session, reason="late-round arena pressure")}

    if not session["engaged_opponent_id"]:
        session["engaged_opponent_id"] = _choose_opponent(session)
    next_opponent = next(row for row in session["roster"] if row["opponent_id"] == session["engaged_opponent_id"])
    data["combat_encounter"] = copy.deepcopy(next_opponent["encounter"])
    data["tzhaar_fight_pit"] = session
    data["tzhaar_fight_pit_last_result"] = (
        f"Fight Pit · {len(session['roster'])} rivals remain · "
        f"{session['pending_tokkul']} pending TokKul"
    )
    return data, True, {
        "terminal": False,
        "combat": combat,
        "player_kill": player_kill,
        "other_eliminated": other_eliminated,
        "pressure": pressure,
        "message": data["tzhaar_fight_pit_last_result"],
    }


def leave_tzhaar_fight_pit_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_tzhaar_fight_pit_state_pure(data)
    session = state["tzhaar_fight_pit"]
    if not session:
        return data, False, {"reason": "No Fight Pit match is active."}
    data.update(state)
    data["tzhaar_fight_pit_forfeits"] += 1
    message = f"Left the Fight Pit · forfeited {session['pending_tokkul']} pending TokKul"
    _finish(data, session, message)
    return data, True, {"message": message, "forfeited_tokkul": session["pending_tokkul"]}


def apply_tzhaar_fight_pit_command_pure(player_data: Mapping[str, Any], action_id: str, payload: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "enter":
        return enter_tzhaar_fight_pit_pure(player_data, str(body.get("policy", "")) or None)
    if action_id == "leave":
        return leave_tzhaar_fight_pit_pure(player_data)
    if action_id == "set_policy":
        return set_tzhaar_fight_pit_policy_pure(player_data, str(body.get("policy", "")))
    return copy.deepcopy(dict(player_data)), False, {"reason": "Unknown Fight Pit command."}


def tzhaar_fight_pit_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_tzhaar_fight_pit_state_pure(player_data)
    session = state["tzhaar_fight_pit"]
    active = player_data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    encounter = player_data.get("combat_encounter")
    reasons = []
    if active_id and active_id != TZHAAR_FIGHT_PIT_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity.")
    if not session and isinstance(encounter, Mapping) and encounter:
        reasons.append("Finish or leave the current Combat encounter.")
    return {
        **state,
        "active": bool(session),
        "can_enter": not reasons and not session,
        "entry_reasons": tuple(reasons),
        "opponents_remaining": len(session.get("roster", ())) if session else 0,
        "fire_cape_multiplier": 2 if _fire_cape_equipped(player_data) else 1,
        "source": TZHAAR_FIGHT_PIT_SOURCE,
    }
