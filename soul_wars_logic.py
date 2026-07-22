"""Pure Soul Wars match, objective, safe-death, and charm-shop mechanics."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

try:
    from .logic_pure import (
        apply_combat_burst_pure,
        combat_max_lifepoints_pure,
        player_combat_level_pure,
    )
    from .soul_wars_data import (
        SOUL_WARS_ACTIVITY_ID,
        SOUL_WARS_ACTIVITY_MAX,
        SOUL_WARS_AVATAR_LIFEPOINTS,
        SOUL_WARS_AVATAR_STARTING_SLAYER,
        SOUL_WARS_BONE_PRAYER_RESTORE,
        SOUL_WARS_CHARM_REWARDS,
        SOUL_WARS_CHARM_REWARDS_BY_ITEM,
        SOUL_WARS_COMBAT_TARGET_ID,
        SOUL_WARS_CONTROL_DUTY_PROGRESS,
        SOUL_WARS_CONTROL_HOLD_PROGRESS,
        SOUL_WARS_CONTROL_LIMIT,
        SOUL_WARS_DUTY_IDS,
        SOUL_WARS_EVENT_REVIEWS,
        SOUL_WARS_OPPONENT_AVATAR_DAMAGE,
        SOUL_WARS_OPPONENT_CONTROL_PROGRESS,
        SOUL_WARS_OPPONENT_FRAGMENT_PRESSURE,
        SOUL_WARS_TEAM_ATTACK_SLAYER,
        SOUL_WARS_TEAM_AVATAR_DAMAGE,
        SOUL_WARS_TEAM_FRAGMENT_PRESSURE,
        SOUL_WARS_TEAM_IDS,
        SOUL_WARS_ZEAL_BY_OUTCOME,
        SOUL_WARS_ZEAL_CAP,
        soul_wars_avatar_enemy_pure,
        soul_wars_charm_quantity_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure import (  # type: ignore
        apply_combat_burst_pure,
        combat_max_lifepoints_pure,
        player_combat_level_pure,
    )
    from soul_wars_data import (  # type: ignore
        SOUL_WARS_ACTIVITY_ID,
        SOUL_WARS_ACTIVITY_MAX,
        SOUL_WARS_AVATAR_LIFEPOINTS,
        SOUL_WARS_AVATAR_STARTING_SLAYER,
        SOUL_WARS_BONE_PRAYER_RESTORE,
        SOUL_WARS_CHARM_REWARDS,
        SOUL_WARS_CHARM_REWARDS_BY_ITEM,
        SOUL_WARS_COMBAT_TARGET_ID,
        SOUL_WARS_CONTROL_DUTY_PROGRESS,
        SOUL_WARS_CONTROL_HOLD_PROGRESS,
        SOUL_WARS_CONTROL_LIMIT,
        SOUL_WARS_DUTY_IDS,
        SOUL_WARS_EVENT_REVIEWS,
        SOUL_WARS_OPPONENT_AVATAR_DAMAGE,
        SOUL_WARS_OPPONENT_CONTROL_PROGRESS,
        SOUL_WARS_OPPONENT_FRAGMENT_PRESSURE,
        SOUL_WARS_TEAM_ATTACK_SLAYER,
        SOUL_WARS_TEAM_AVATAR_DAMAGE,
        SOUL_WARS_TEAM_FRAGMENT_PRESSURE,
        SOUL_WARS_TEAM_IDS,
        SOUL_WARS_ZEAL_BY_OUTCOME,
        SOUL_WARS_ZEAL_CAP,
        soul_wars_avatar_enemy_pure,
        soul_wars_charm_quantity_pure,
    )


SOUL_WARS_STATE_VERSION = 1
_VALID_MODES = frozenset({"casual", "advanced"})


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _signed_int(value: Any, *, limit: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = 0
    return max(-limit, min(parsed, limit))


def _rng_value(rng) -> float:
    try:
        return max(0.0, min(0.999999999, float(rng())))
    except (TypeError, ValueError, StopIteration):
        return 0.5


def default_soul_wars_state_pure() -> dict[str, Any]:
    return {
        "soul_wars": {},
        "soul_wars_policy": {
            "automation_mode": "casual",
            "duty": "fragments",
            "team": "balance",
        },
        "soul_wars_zeal": 0,
        "soul_wars_games_played": 0,
        "soul_wars_wins": 0,
        "soul_wars_draws": 0,
        "soul_wars_losses": 0,
        "soul_wars_kicks": 0,
        "soul_wars_last_result": "",
    }


def sanitize_soul_wars_policy_pure(raw: Any) -> dict[str, str]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    duty = str(source.get("duty", "fragments"))
    team = str(source.get("team", "balance"))
    return {
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "duty": duty if duty in SOUL_WARS_DUTY_IDS else "fragments",
        "team": team if team in SOUL_WARS_TEAM_IDS else "balance",
    }


def sanitize_soul_wars_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    mode = str(raw.get("automation_mode", "casual"))
    duty = str(raw.get("duty", "fragments"))
    team = str(raw.get("team", "balance"))
    encounter = raw.get("encounter")
    return {
        "version": SOUL_WARS_STATE_VERSION,
        "review": _int(raw.get("review"), maximum=SOUL_WARS_EVENT_REVIEWS - 1),
        "player_score": _int(raw.get("player_score"), maximum=99),
        "opponent_score": _int(raw.get("opponent_score"), maximum=99),
        "enemy_avatar_lifepoints": _int(
            raw.get("enemy_avatar_lifepoints", SOUL_WARS_AVATAR_LIFEPOINTS),
            SOUL_WARS_AVATAR_LIFEPOINTS,
            maximum=SOUL_WARS_AVATAR_LIFEPOINTS,
        ),
        "friendly_avatar_lifepoints": _int(
            raw.get("friendly_avatar_lifepoints", SOUL_WARS_AVATAR_LIFEPOINTS),
            SOUL_WARS_AVATAR_LIFEPOINTS,
            maximum=SOUL_WARS_AVATAR_LIFEPOINTS,
        ),
        "enemy_avatar_slayer": _int(
            raw.get("enemy_avatar_slayer", SOUL_WARS_AVATAR_STARTING_SLAYER),
            SOUL_WARS_AVATAR_STARTING_SLAYER,
            maximum=SOUL_WARS_AVATAR_STARTING_SLAYER,
        ),
        "friendly_avatar_slayer": _int(
            raw.get("friendly_avatar_slayer", SOUL_WARS_AVATAR_STARTING_SLAYER),
            SOUL_WARS_AVATAR_STARTING_SLAYER,
            maximum=SOUL_WARS_AVATAR_STARTING_SLAYER,
        ),
        "fragments": _int(raw.get("fragments"), maximum=999),
        "control_balance": _signed_int(
            raw.get("control_balance"), limit=SOUL_WARS_CONTROL_LIMIT
        ),
        "activity": max(
            1,
            _int(
                raw.get("activity", SOUL_WARS_ACTIVITY_MAX),
                SOUL_WARS_ACTIVITY_MAX,
                maximum=SOUL_WARS_ACTIVITY_MAX,
            ),
        ),
        "contribution": _int(raw.get("contribution"), maximum=999_999),
        "deaths": _int(raw.get("deaths"), maximum=99_999),
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "duty": duty if duty in SOUL_WARS_DUTY_IDS else "fragments",
        "team": team if team in SOUL_WARS_TEAM_IDS else "balance",
        "previous_combat_target": str(raw.get("previous_combat_target", ""))[:120],
        "encounter": copy.deepcopy(encounter) if isinstance(encounter, Mapping) else {},
    }


def sanitize_soul_wars_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    session = sanitize_soul_wars_session_pure(source.get("soul_wars"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", SOUL_WARS_ACTIVITY_ID}:
        session = {}
    return {
        "soul_wars": session,
        "soul_wars_policy": sanitize_soul_wars_policy_pure(
            source.get("soul_wars_policy")
        ),
        "soul_wars_zeal": _int(
            source.get("soul_wars_zeal"), maximum=SOUL_WARS_ZEAL_CAP
        ),
        "soul_wars_games_played": _int(source.get("soul_wars_games_played")),
        "soul_wars_wins": _int(source.get("soul_wars_wins")),
        "soul_wars_draws": _int(source.get("soul_wars_draws")),
        "soul_wars_losses": _int(source.get("soul_wars_losses")),
        "soul_wars_kicks": _int(source.get("soul_wars_kicks")),
        "soul_wars_last_result": str(source.get("soul_wars_last_result", "") or "")[:500],
    }


def set_soul_wars_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_soul_wars_state_pure(data)
    if state["soul_wars"]:
        return data, False, {"reason": "Finish or leave the current match first."}
    candidate = dict(state["soul_wars_policy"])
    candidate.update(dict(payload or {}))
    policy = sanitize_soul_wars_policy_pure(candidate)
    data.update(state)
    data["soul_wars_policy"] = policy
    return data, True, {"message": "Soul Wars plan saved.", "policy": policy}


def _loaded_food_count(data: Mapping[str, Any]) -> int:
    loadout = data.get("combat_supply_loadout")
    food = loadout.get("food") if isinstance(loadout, Mapping) else None
    return sum(_int(amount) for amount in food.values()) if isinstance(food, Mapping) else 0


def enter_soul_wars_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_soul_wars_state_pure(data)
    if state["soul_wars"]:
        return data, False, {"reason": "A Soul Wars match is already active."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != SOUL_WARS_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {"reason": "Finish or leave the current Combat encounter first."}
    equipment = data.get("equipment")
    equipment = equipment if isinstance(equipment, Mapping) else {}
    if equipment.get("cape"):
        return data, False, {"reason": "Remove your equipped cape before entering Soul Wars."}
    if _loaded_food_count(data):
        return data, False, {
            "reason": "Remove carried food from the Combat pack before entering Soul Wars."
        }

    candidate = dict(state["soul_wars_policy"])
    candidate.update(dict(payload or {}))
    policy = sanitize_soul_wars_policy_pure(candidate)
    previous = str(data.get("current_combat_target", ""))[:120]
    data.update(state)
    data["soul_wars_policy"] = policy
    data["soul_wars"] = {
        "version": SOUL_WARS_STATE_VERSION,
        "review": 0,
        "player_score": 0,
        "opponent_score": 0,
        "enemy_avatar_lifepoints": SOUL_WARS_AVATAR_LIFEPOINTS,
        "friendly_avatar_lifepoints": SOUL_WARS_AVATAR_LIFEPOINTS,
        "enemy_avatar_slayer": SOUL_WARS_AVATAR_STARTING_SLAYER,
        "friendly_avatar_slayer": SOUL_WARS_AVATAR_STARTING_SLAYER,
        "fragments": 0,
        "control_balance": 0,
        "activity": SOUL_WARS_ACTIVITY_MAX,
        "contribution": 0,
        "deaths": 0,
        "automation_mode": policy["automation_mode"],
        "duty": policy["duty"],
        "team": policy["team"],
        "previous_combat_target": previous,
        "encounter": {},
    }
    data["activity_session"] = {"active_id": SOUL_WARS_ACTIVITY_ID}
    data["current_utility"] = SOUL_WARS_ACTIVITY_ID
    data["combat_encounter"] = {}
    data["soul_wars_last_result"] = "Entered Soul Wars · twelve match beats remain"
    return data, True, {"message": data["soul_wars_last_result"]}


def _restore_match_resources(data: dict[str, Any]) -> None:
    data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
    data["combat_prayer_points"] = max(1, _int(data.get("prayer_level"), 1)) * 10
    data["combat_special_attack_energy"] = 100
    data["agility_run_energy_credit_pct"] = 100
    summoning = data.get("summoning_state")
    if isinstance(summoning, Mapping):
        summoning_state = copy.deepcopy(dict(summoning))
        summoning_state["summoning_points_current"] = max(
            1, _int(data.get("summoning_level"), 1)
        )
        data["summoning_state"] = summoning_state


def _end_match(data: dict[str, Any], session: Mapping[str, Any], message: str) -> None:
    data["soul_wars"] = {}
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == SOUL_WARS_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(session.get("previous_combat_target", ""))
    _restore_match_resources(data)
    data["soul_wars_last_result"] = message[:500]


def _finish_match(data: dict[str, Any], session: Mapping[str, Any]) -> dict[str, Any]:
    player_score = int(session["player_score"])
    opponent_score = int(session["opponent_score"])
    outcome = "win" if player_score > opponent_score else "loss" if player_score < opponent_score else "draw"
    zeal_before = _int(data.get("soul_wars_zeal"), maximum=SOUL_WARS_ZEAL_CAP)
    zeal_after = min(SOUL_WARS_ZEAL_CAP, zeal_before + SOUL_WARS_ZEAL_BY_OUTCOME[outcome])
    awarded = zeal_after - zeal_before
    data["soul_wars_zeal"] = zeal_after
    data["soul_wars_games_played"] = _int(data.get("soul_wars_games_played")) + 1
    counter_key = {
        "win": "soul_wars_wins",
        "draw": "soul_wars_draws",
        "loss": "soul_wars_losses",
    }[outcome]
    data[counter_key] = _int(data.get(counter_key)) + 1
    message = (
        f"Soul Wars {outcome} · {player_score}-{opponent_score} avatar defeats · "
        f"+{awarded} Zeal"
    )
    _end_match(data, session, message)
    return {
        "terminal": True,
        "outcome": outcome,
        "zeal": awarded,
        "player_score": player_score,
        "opponent_score": opponent_score,
        "message": message,
    }


def _kick_for_inactivity(data: dict[str, Any], session: Mapping[str, Any]) -> dict[str, Any]:
    data["soul_wars_kicks"] = _int(data.get("soul_wars_kicks")) + 1
    message = "Removed from Soul Wars for inactivity · no Zeal"
    _end_match(data, session, message)
    return {
        "terminal": True,
        "kicked": True,
        "zeal": 0,
        "message": message,
    }


def _control_name(session: Mapping[str, Any]) -> str:
    balance = int(session["control_balance"])
    return "player" if balance > 0 else "opponent" if balance < 0 else "neutral"


def _choose_duty(data: Mapping[str, Any], session: Mapping[str, Any]) -> str:
    if session["automation_mode"] == "advanced":
        requested = str(session.get("duty", "fragments"))
        return requested if requested in SOUL_WARS_DUTY_IDS else "fragments"
    if int(session["control_balance"]) <= 0:
        return "control"
    if int(session["friendly_avatar_lifepoints"]) <= 3_000:
        return "defend"
    slayer_level = max(1, _int(data.get("slayer_level"), 1))
    if int(session["enemy_avatar_slayer"]) <= slayer_level:
        return "avatar"
    return "fragments"


def _score_avatar(session: dict[str, Any], side: str) -> None:
    score_key = f"{side}_score"
    if side == "player":
        lp_key = "enemy_avatar_lifepoints"
        slayer_key = "enemy_avatar_slayer"
    else:
        lp_key = "friendly_avatar_lifepoints"
        slayer_key = "friendly_avatar_slayer"
    if int(session[lp_key]) > 0:
        return
    session[score_key] += 1
    session[lp_key] = SOUL_WARS_AVATAR_LIFEPOINTS
    session[slayer_key] = SOUL_WARS_AVATAR_STARTING_SLAYER
    if side == "player":
        session["encounter"] = {}


def _apply_opponent_pressure(session: dict[str, Any]) -> None:
    session["control_balance"] = max(
        -SOUL_WARS_CONTROL_LIMIT,
        int(session["control_balance"]) - SOUL_WARS_OPPONENT_CONTROL_PROGRESS,
    )
    if int(session["control_balance"]) < 0:
        session["friendly_avatar_slayer"] = max(
            0,
            int(session["friendly_avatar_slayer"]) - SOUL_WARS_OPPONENT_FRAGMENT_PRESSURE,
        )
        if int(session["friendly_avatar_slayer"]) <= SOUL_WARS_TEAM_ATTACK_SLAYER:
            session["friendly_avatar_lifepoints"] = max(
                0,
                int(session["friendly_avatar_lifepoints"])
                - SOUL_WARS_OPPONENT_AVATAR_DAMAGE,
            )
            _score_avatar(session, "opponent")


def _apply_team_avatar_pressure(session: dict[str, Any]) -> int:
    if (
        int(session["control_balance"]) <= 0
        or int(session["enemy_avatar_slayer"]) > SOUL_WARS_TEAM_ATTACK_SLAYER
    ):
        return 0
    damage = min(
        SOUL_WARS_TEAM_AVATAR_DAMAGE,
        int(session["enemy_avatar_lifepoints"]),
    )
    session["enemy_avatar_lifepoints"] -= damage
    _score_avatar(session, "player")
    return damage


def _apply_fragment_duty(data: Mapping[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    slayer_level = max(1, _int(data.get("slayer_level"), 1))
    gathered = 2 if slayer_level >= 52 else 1
    source = "jelly" if slayer_level >= 52 else "pyrefiend" if slayer_level >= 30 else "dropped fragment"
    session["fragments"] += gathered
    session["control_balance"] = min(
        SOUL_WARS_CONTROL_LIMIT,
        int(session["control_balance"]) + SOUL_WARS_CONTROL_HOLD_PROGRESS,
    )
    offered = 0
    requirement_reduced = 0
    if int(session["control_balance"]) > 0:
        offered = int(session["fragments"])
        session["fragments"] = 0
        requirement_reduced = min(
            int(session["enemy_avatar_slayer"]),
            offered + SOUL_WARS_TEAM_FRAGMENT_PRESSURE,
        )
        session["enemy_avatar_slayer"] -= requirement_reduced
    return {
        "gathered": gathered,
        "fragment_source": source,
        "offered": offered,
        "requirement_reduced": requirement_reduced,
    }


def _apply_defend_duty(data: dict[str, Any], session: dict[str, Any], rng) -> dict[str, Any]:
    session["control_balance"] = min(
        SOUL_WARS_CONTROL_LIMIT,
        int(session["control_balance"]) + SOUL_WARS_CONTROL_HOLD_PROGRESS,
    )
    raised = _rng_value(rng) < 0.5 and int(session["friendly_avatar_slayer"]) < 100
    if raised:
        session["friendly_avatar_slayer"] += 1
    prayer_max = max(1, _int(data.get("prayer_level"), 1)) * 10
    before = _int(data.get("combat_prayer_points"), prayer_max, maximum=prayer_max)
    after = min(prayer_max, before + SOUL_WARS_BONE_PRAYER_RESTORE)
    data["combat_prayer_points"] = after
    return {"avatar_requirement_raised": raised, "prayer_restored": after - before}


def _apply_avatar_duty(
    data: dict[str, Any], session: dict[str, Any], rng, equipment_data: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    slayer_level = max(1, _int(data.get("slayer_level"), 1))
    requirement = int(session["enemy_avatar_slayer"])
    if slayer_level < requirement:
        return data, {
            "blocked": True,
            "reason": f"Enemy avatar requires Slayer {requirement}; current level is {slayer_level}.",
        }
    session["control_balance"] = min(
        SOUL_WARS_CONTROL_LIMIT,
        int(session["control_balance"]) + SOUL_WARS_CONTROL_HOLD_PROGRESS,
    )
    encounter = {
        "target_id": SOUL_WARS_COMBAT_TARGET_ID,
        "enemy_lifepoints": int(session["enemy_avatar_lifepoints"]),
    }
    data["current_combat_target"] = SOUL_WARS_COMBAT_TARGET_ID
    data["combat_encounter"] = copy.deepcopy(encounter)
    data, ok, result = apply_combat_burst_pure(
        data,
        {SOUL_WARS_COMBAT_TARGET_ID: soul_wars_avatar_enemy_pure()},
        equipment_data,
        ticks=6,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=True,
        allow_bank_run=False,
    )
    if not ok:
        return data, {"combat_failed": True, **result}
    encounter_after = data.get("combat_encounter")
    if result.get("killed"):
        session["enemy_avatar_lifepoints"] = 0
        session["encounter"] = {}
    elif isinstance(encounter_after, Mapping):
        session["enemy_avatar_lifepoints"] = _int(
            encounter_after.get("enemy_lifepoints"),
            int(session["enemy_avatar_lifepoints"]),
            maximum=SOUL_WARS_AVATAR_LIFEPOINTS,
        )
        session["encounter"] = copy.deepcopy(dict(encounter_after))
    if result.get("died"):
        session["deaths"] += 1
        session["fragments"] = 0
        session["activity"] = SOUL_WARS_ACTIVITY_MAX
        _restore_match_resources(data)
    _score_avatar(session, "player")
    return data, result


def apply_soul_wars_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    productive: bool,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_soul_wars_state_pure(data)
    session = state["soul_wars"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != SOUL_WARS_ACTIVITY_ID:
        return data, False, {"reason": "Enter Soul Wars before training it."}

    data.update(state)
    _apply_opponent_pressure(session)
    session["review"] += 1
    if not productive:
        session["activity"] -= 1
        if int(session["activity"]) <= 0:
            return data, True, _kick_for_inactivity(data, session)
        data["soul_wars"] = session
        data["soul_wars_last_result"] = (
            f"No Soul Wars duty completed · activity {session['activity']}/{SOUL_WARS_ACTIVITY_MAX}"
        )
        if int(session["review"]) >= SOUL_WARS_EVENT_REVIEWS:
            return data, True, {"duty": "idle", **_finish_match(data, session)}
        return data, True, {
            "terminal": False,
            "duty": "idle",
            "control": _control_name(session),
            "message": data["soul_wars_last_result"],
        }

    duty = _choose_duty(data, session)
    duty_result: dict[str, Any] = {}
    if duty == "control":
        session["control_balance"] = min(
            SOUL_WARS_CONTROL_LIMIT,
            int(session["control_balance"]) + SOUL_WARS_CONTROL_DUTY_PROGRESS,
        )
    elif duty == "fragments":
        duty_result = _apply_fragment_duty(data, session)
    elif duty == "defend":
        duty_result = _apply_defend_duty(data, session, rng)
    else:
        data, duty_result = _apply_avatar_duty(
            data, session, rng, equipment_data or {}
        )
        if duty_result.get("combat_failed"):
            return copy.deepcopy(dict(player_data)), False, duty_result

    participated = not bool(duty_result.get("blocked"))
    if participated:
        session["activity"] = SOUL_WARS_ACTIVITY_MAX
        session["contribution"] += 1
    else:
        session["activity"] -= 1
        if int(session["activity"]) <= 0:
            return data, True, {"duty": duty, **duty_result, **_kick_for_inactivity(data, session)}

    crowd_damage = _apply_team_avatar_pressure(session) if participated else 0
    data["soul_wars"] = session
    data["combat_encounter"] = copy.deepcopy(session["encounter"])
    control = _control_name(session)
    data["soul_wars_last_result"] = (
        f"Soul Wars {duty} · score {session['player_score']}-{session['opponent_score']} · "
        f"obelisk {control}"
    )
    if int(session["review"]) >= SOUL_WARS_EVENT_REVIEWS:
        return data, True, {
            "duty": duty,
            "crowd_avatar_damage": crowd_damage,
            **duty_result,
            **_finish_match(data, session),
        }
    return data, True, {
        "terminal": False,
        "duty": duty,
        "control": control,
        "crowd_avatar_damage": crowd_damage,
        **duty_result,
        "message": data["soul_wars_last_result"],
    }


def leave_soul_wars_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_soul_wars_state_pure(data)
    session = state["soul_wars"]
    if not session:
        return data, False, {"reason": "No Soul Wars match is active."}
    data.update(state)
    message = "Left Soul Wars; the unfinished match paid no Zeal."
    _end_match(data, session, message)
    return data, True, {"message": message}


def buy_soul_wars_charms_pure(
    player_data: Mapping[str, Any], item_name: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_soul_wars_state_pure(data)
    if state["soul_wars"]:
        return data, False, {"reason": "Finish or leave the current match first."}
    reward = SOUL_WARS_CHARM_REWARDS_BY_ITEM.get(str(item_name))
    if reward is None:
        return data, False, {"reason": "Unknown Soul Wars charm reward."}
    combat_level = player_combat_level_pure(data)
    quantity = soul_wars_charm_quantity_pure(reward.item_name, combat_level)
    if quantity <= 0:
        return data, False, {"reason": "Charm rewards require combat level 13."}
    zeal = state["soul_wars_zeal"]
    if zeal < reward.zeal_cost:
        return data, False, {"reason": f"Requires {reward.zeal_cost} Zeal."}
    inventory = copy.deepcopy(data.get("inventory", {}))
    inventory = inventory if isinstance(inventory, dict) else {}
    inventory[reward.item_name] = _int(inventory.get(reward.item_name)) + quantity
    data.update(state)
    data["inventory"] = inventory
    data["soul_wars_zeal"] = zeal - reward.zeal_cost
    data["soul_wars_last_result"] = (
        f"Bought {quantity} {reward.item_name}{'' if quantity == 1 else 's'} "
        f"for {reward.zeal_cost} Zeal."
    )
    return data, True, {
        "message": data["soul_wars_last_result"],
        "item": reward.item_name,
        "quantity": quantity,
        "zeal_spent": reward.zeal_cost,
    }


def apply_soul_wars_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "enter":
        return enter_soul_wars_pure(player_data, body)
    if action_id == "leave":
        return leave_soul_wars_pure(player_data)
    if action_id == "set_policy":
        return set_soul_wars_policy_pure(player_data, body)
    if action_id == "buy_charms":
        return buy_soul_wars_charms_pure(
            player_data,
            str(body.get("item_name", "")),
        )
    return copy.deepcopy(dict(player_data)), False, {
        "reason": "Unknown Soul Wars command."
    }


def soul_wars_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_soul_wars_state_pure(player_data)
    session = state["soul_wars"]
    combat_level = player_combat_level_pure(player_data)
    reasons: list[str] = []
    active = player_data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != SOUL_WARS_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity.")
    encounter = player_data.get("combat_encounter")
    if not session and isinstance(encounter, Mapping) and encounter:
        reasons.append("Finish or leave the current Combat encounter.")
    equipment = player_data.get("equipment")
    if isinstance(equipment, Mapping) and equipment.get("cape"):
        reasons.append("Remove your equipped cape.")
    if _loaded_food_count(player_data):
        reasons.append("Remove carried food from the Combat pack.")
    return {
        **state,
        "active": bool(session),
        "can_enter": not reasons and not session,
        "entry_reasons": tuple(reasons),
        "reviews_remaining": (
            max(0, SOUL_WARS_EVENT_REVIEWS - int(session["review"])) if session else 0
        ),
        "control": _control_name(session) if session else "neutral",
        "combat_level": combat_level,
        "rewards": tuple(
            {
                "item": reward.item_name,
                "cost": reward.zeal_cost,
                "quantity": soul_wars_charm_quantity_pure(reward.item_name, combat_level),
                "affordable": (
                    not session
                    and state["soul_wars_zeal"] >= reward.zeal_cost
                    and soul_wars_charm_quantity_pure(reward.item_name, combat_level) > 0
                ),
            }
            for reward in SOUL_WARS_CHARM_REWARDS
        ),
    }
