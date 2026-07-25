"""Pure Castle Wars match, duty, reward, and equipment mechanics."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

try:
    from .castle_wars_data import (
        CASTLE_WARS_ACTIVITY_ID,
        CASTLE_WARS_BALLISTA_PARTS,
        CASTLE_WARS_BASIC_SET,
        CASTLE_WARS_CAPTURE_PROGRESS,
        CASTLE_WARS_CATAPULT_MAX,
        CASTLE_WARS_COMBAT_TARGET_ID,
        CASTLE_WARS_COMBAT_TICKS_PER_REVIEW,
        CASTLE_WARS_DUTIES,
        CASTLE_WARS_GATE_MAX,
        CASTLE_WARS_MATCH_REVIEWS,
        CASTLE_WARS_MAX_BARRICADES,
        CASTLE_WARS_OPPONENT_BURST_CHANCE,
        CASTLE_WARS_OPPONENT_CROWD_PROGRESS,
        CASTLE_WARS_PLAYER_CROWD_PROGRESS,
        CASTLE_WARS_PRESSURE_DAMAGE,
        CASTLE_WARS_REWARD_MINIMUM_REVIEWS,
        CASTLE_WARS_REWARDS,
        CASTLE_WARS_REWARDS_BY_ID,
        CASTLE_WARS_TEAMS,
        castle_wars_raider_enemy_pure,
    )
    from .logic_pure import apply_combat_burst_pure, combat_max_lifepoints_pure
except ImportError:  # pragma: no cover - flat test imports
    from castle_wars_data import (  # type: ignore
        CASTLE_WARS_ACTIVITY_ID,
        CASTLE_WARS_BALLISTA_PARTS,
        CASTLE_WARS_BASIC_SET,
        CASTLE_WARS_CAPTURE_PROGRESS,
        CASTLE_WARS_CATAPULT_MAX,
        CASTLE_WARS_COMBAT_TARGET_ID,
        CASTLE_WARS_COMBAT_TICKS_PER_REVIEW,
        CASTLE_WARS_DUTIES,
        CASTLE_WARS_GATE_MAX,
        CASTLE_WARS_MATCH_REVIEWS,
        CASTLE_WARS_MAX_BARRICADES,
        CASTLE_WARS_OPPONENT_BURST_CHANCE,
        CASTLE_WARS_OPPONENT_CROWD_PROGRESS,
        CASTLE_WARS_PLAYER_CROWD_PROGRESS,
        CASTLE_WARS_PRESSURE_DAMAGE,
        CASTLE_WARS_REWARD_MINIMUM_REVIEWS,
        CASTLE_WARS_REWARDS,
        CASTLE_WARS_REWARDS_BY_ID,
        CASTLE_WARS_TEAMS,
        castle_wars_raider_enemy_pure,
    )
    from logic_pure import (  # type: ignore
        apply_combat_burst_pure,
        combat_max_lifepoints_pure,
    )


CASTLE_WARS_STATE_VERSION = 1
_VALID_MODES = frozenset({"casual", "advanced"})
_VALID_DUTIES = frozenset(key for key, _label in CASTLE_WARS_DUTIES)
_VALID_TEAMS = frozenset(key for key, _label in CASTLE_WARS_TEAMS)


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def default_castle_wars_state_pure() -> dict[str, Any]:
    return {
        "castle_wars": {},
        "castle_wars_policy": {
            "automation_mode": "casual",
            "duty": "capture",
            "team": "balance",
        },
        "castle_wars_tickets": 0,
        "castle_wars_games_played": 0,
        "castle_wars_wins": 0,
        "castle_wars_draws": 0,
        "castle_wars_losses": 0,
        "castle_wars_last_result": "",
    }


def sanitize_castle_wars_policy_pure(raw: Any) -> dict[str, str]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    duty = str(source.get("duty", "capture"))
    team = str(source.get("team", "balance"))
    return {
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "duty": duty if duty in _VALID_DUTIES else "capture",
        "team": team if team in _VALID_TEAMS else "balance",
    }


def sanitize_castle_wars_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    mode = str(raw.get("automation_mode", "casual"))
    duty = str(raw.get("duty", "capture"))
    team = str(raw.get("team", "balance"))
    encounter = raw.get("encounter")
    return {
        "version": CASTLE_WARS_STATE_VERSION,
        "review": _int(raw.get("review"), maximum=CASTLE_WARS_MATCH_REVIEWS - 1),
        "player_score": _int(raw.get("player_score"), maximum=99),
        "opponent_score": _int(raw.get("opponent_score"), maximum=99),
        "player_capture_progress": _int(
            raw.get("player_capture_progress"),
            maximum=CASTLE_WARS_CAPTURE_PROGRESS - 1,
        ),
        "opponent_capture_progress": _int(
            raw.get("opponent_capture_progress"),
            maximum=CASTLE_WARS_CAPTURE_PROGRESS - 1,
        ),
        "barricades": _int(
            raw.get("barricades"), maximum=CASTLE_WARS_MAX_BARRICADES
        ),
        "gate_integrity": _int(
            raw.get("gate_integrity", CASTLE_WARS_GATE_MAX),
            CASTLE_WARS_GATE_MAX,
            maximum=CASTLE_WARS_GATE_MAX,
        ),
        "catapult_integrity": _int(
            raw.get("catapult_integrity", CASTLE_WARS_CATAPULT_MAX),
            CASTLE_WARS_CATAPULT_MAX,
            maximum=CASTLE_WARS_CATAPULT_MAX,
        ),
        "ballista_deployed": bool(raw.get("ballista_deployed", False)),
        "contribution": _int(raw.get("contribution"), maximum=999_999),
        "kills": _int(raw.get("kills"), maximum=99_999),
        "captures": _int(raw.get("captures"), maximum=99_999),
        "deaths": _int(raw.get("deaths"), maximum=99_999),
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "duty": duty if duty in _VALID_DUTIES else "capture",
        "team": team if team in _VALID_TEAMS else "balance",
        "previous_combat_target": str(raw.get("previous_combat_target", ""))[:120],
        "encounter": copy.deepcopy(encounter) if isinstance(encounter, Mapping) else {},
    }


def sanitize_castle_wars_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    session = sanitize_castle_wars_session_pure(source.get("castle_wars"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", CASTLE_WARS_ACTIVITY_ID}:
        session = {}
    return {
        "castle_wars": session,
        "castle_wars_policy": sanitize_castle_wars_policy_pure(
            source.get("castle_wars_policy")
        ),
        "castle_wars_tickets": _int(source.get("castle_wars_tickets")),
        "castle_wars_games_played": _int(source.get("castle_wars_games_played")),
        "castle_wars_wins": _int(source.get("castle_wars_wins")),
        "castle_wars_draws": _int(source.get("castle_wars_draws")),
        "castle_wars_losses": _int(source.get("castle_wars_losses")),
        "castle_wars_last_result": str(
            source.get("castle_wars_last_result", "") or ""
        )[:500],
    }


def set_castle_wars_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the roster state and session are rebuilt fresh, and
    # the combat encounter is assigned as a new object rather than edited in
    # place.
    data = dict(player_data)
    state = sanitize_castle_wars_state_pure(data)
    if state["castle_wars"]:
        return data, False, {"reason": "Finish or leave the current match first."}
    candidate = dict(state["castle_wars_policy"])
    candidate.update(dict(payload or {}))
    policy = sanitize_castle_wars_policy_pure(candidate)
    data.update(state)
    data["castle_wars_policy"] = policy
    return data, True, {"message": "Castle Wars plan saved.", "policy": policy}


def _loaded_food_count(data: Mapping[str, Any]) -> int:
    loadout = data.get("combat_supply_loadout")
    food = loadout.get("food") if isinstance(loadout, Mapping) else None
    return sum(_int(amount) for amount in food.values()) if isinstance(food, Mapping) else 0


def enter_castle_wars_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data, ok, info = set_castle_wars_policy_pure(player_data, payload)
    if not ok:
        return data, False, info
    state = sanitize_castle_wars_state_pure(data)
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != CASTLE_WARS_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {"reason": "Finish or leave the current Combat encounter first."}
    equipment = data.get("equipment")
    equipment = equipment if isinstance(equipment, Mapping) else {}
    blocked_slots = [slot for slot in ("head", "cape") if equipment.get(slot)]
    if blocked_slots:
        return data, False, {
            "reason": "Remove equipped helmets and capes before entering Castle Wars."
        }
    if _loaded_food_count(data) > 0:
        return data, False, {
            "reason": "Remove carried food from the Combat pack before entering Castle Wars."
        }

    policy = state["castle_wars_policy"]
    previous = str(data.get("current_combat_target", ""))[:120]
    encounter = {
        "target_id": CASTLE_WARS_COMBAT_TARGET_ID,
        "enemy_lifepoints": castle_wars_raider_enemy_pure()["stats"]["hitpoints"],
    }
    data.update(state)
    data["castle_wars"] = {
        "version": CASTLE_WARS_STATE_VERSION,
        "review": 0,
        "player_score": 0,
        "opponent_score": 0,
        "player_capture_progress": 0,
        "opponent_capture_progress": 0,
        "barricades": 0,
        "gate_integrity": CASTLE_WARS_GATE_MAX,
        "catapult_integrity": CASTLE_WARS_CATAPULT_MAX,
        "ballista_deployed": False,
        "contribution": 0,
        "kills": 0,
        "captures": 0,
        "deaths": 0,
        "automation_mode": policy["automation_mode"],
        "duty": policy["duty"],
        "team": policy["team"],
        "previous_combat_target": previous,
        "encounter": encounter,
    }
    data["activity_session"] = {"active_id": CASTLE_WARS_ACTIVITY_ID}
    data["current_utility"] = CASTLE_WARS_ACTIVITY_ID
    data["current_combat_target"] = CASTLE_WARS_COMBAT_TARGET_ID
    data["combat_encounter"] = copy.deepcopy(encounter)
    data["castle_wars_last_result"] = "Entered Castle Wars · ten match beats remain"
    return data, True, {"message": data["castle_wars_last_result"]}


def _end_match(data: dict[str, Any], session: Mapping[str, Any], message: str) -> None:
    data["castle_wars"] = {}
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == CASTLE_WARS_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(session.get("previous_combat_target", ""))
    data["castle_wars_last_result"] = message[:500]


def leave_castle_wars_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the roster state and session are rebuilt fresh, and
    # the combat encounter is assigned as a new object rather than edited in
    # place.
    data = dict(player_data)
    state = sanitize_castle_wars_state_pure(data)
    session = state["castle_wars"]
    if not session:
        return data, False, {"reason": "No Castle Wars match is active."}
    message = "Left Castle Wars; the unfinished match paid no tickets."
    _end_match(data, session, message)
    return data, True, {"message": message}


def castle_wars_damage_multiplier_pure(player_data: Mapping[str, Any]) -> float:
    equipment = player_data.get("equipment")
    equipped = set(equipment.values()) if isinstance(equipment, Mapping) else set()
    pieces = len(CASTLE_WARS_BASIC_SET.intersection(equipped))
    return {0: 1.0, 1: 1.04, 2: 1.06, 3: 1.10}[pieces]


def _choose_bottleneck_duty(session: Mapping[str, Any]) -> str:
    if int(session["gate_integrity"]) <= 45 or int(session["catapult_integrity"]) <= 45:
        return "repair"
    if int(session["barricades"]) < 2:
        return "barricade"
    if int(session["opponent_capture_progress"]) >= CASTLE_WARS_CAPTURE_PROGRESS - 1:
        return "defend"
    if int(session["player_capture_progress"]) >= CASTLE_WARS_CAPTURE_PROGRESS - 2:
        return "capture"
    return "capture"


def _choose_duty(session: Mapping[str, Any]) -> str:
    if session["automation_mode"] == "advanced":
        requested = str(session.get("duty", "capture"))
        return requested if requested in _VALID_DUTIES else "capture"
    return _choose_bottleneck_duty(session)


def _advance_capture(session: dict[str, Any], key: str, amount: int) -> int:
    progress_key = f"{key}_capture_progress"
    score_key = f"{key}_score"
    session[progress_key] += max(0, amount)
    scored = session[progress_key] // CASTLE_WARS_CAPTURE_PROGRESS
    if scored:
        session[score_key] += scored
        session[progress_key] %= CASTLE_WARS_CAPTURE_PROGRESS
    return scored


def _apply_pressure(session: dict[str, Any], amount: int) -> None:
    remaining = max(0, amount)
    while remaining > 0 and int(session["barricades"]) > 0:
        session["barricades"] -= 1
        remaining = max(0, remaining - CASTLE_WARS_PRESSURE_DAMAGE)
    if remaining > 0:
        session["gate_integrity"] = max(0, int(session["gate_integrity"]) - remaining)
        session["catapult_integrity"] = max(
            0, int(session["catapult_integrity"]) - max(1, remaining // 2)
        )


def _apply_noncombat_duty(data: dict[str, Any], session: dict[str, Any], duty: str) -> str:
    if duty == "capture":
        scored = _advance_capture(session, "player", 2)
        session["contribution"] += 2
        session["captures"] += scored
        return "Captured the enemy standard" if scored else "Advanced the standard run"
    if duty == "barricade":
        before = int(session["barricades"])
        session["barricades"] = min(CASTLE_WARS_MAX_BARRICADES, before + 2)
        built = int(session["barricades"]) - before
        session["contribution"] += built
        return f"Deployed {built} barricade{'s' if built != 1 else ''}"
    if duty == "repair":
        gate_before = int(session["gate_integrity"])
        catapult_before = int(session["catapult_integrity"])
        session["gate_integrity"] = min(CASTLE_WARS_GATE_MAX, gate_before + 30)
        session["catapult_integrity"] = min(
            CASTLE_WARS_CATAPULT_MAX, catapult_before + 30
        )
        repaired = (
            int(session["gate_integrity"]) - gate_before
            + int(session["catapult_integrity"]) - catapult_before
        )
        session["contribution"] += repaired
        return f"Repaired {repaired} defence integrity"
    if duty == "catapult":
        strength = 2
        if session["ballista_deployed"]:
            inventory = dict(data.get("inventory") or {})
            if _int(inventory.get("Ballista ammo")) > 0:
                inventory["Ballista ammo"] -= 1
                data["inventory"] = inventory
                strength = 4
        session["opponent_capture_progress"] = max(
            0, int(session["opponent_capture_progress"]) - strength
        )
        session["contribution"] += strength
        return "Fired the deployed ballista" if strength == 4 else "Fired a free catapult rock"
    if duty == "support":
        max_lp = combat_max_lifepoints_pure(data)
        current_lp = _int(data.get("combat_lifepoints", max_lp), max_lp)
        effects = dict(data.get("combat_status_effects") or {})
        before_energy = _int(data.get("agility_run_energy_credit_pct"), maximum=100)
        if current_lp >= max_lp and "poison" not in effects and before_energy >= 100:
            fallback = _choose_bottleneck_duty(session)
            return _apply_noncombat_duty(data, session, fallback)
        healed = min(max_lp - current_lp, max(1, max_lp // 10))
        data["combat_lifepoints"] = current_lp + healed
        effects.pop("poison", None)
        data["combat_status_effects"] = effects
        data["agility_run_energy_credit_pct"] = min(100, before_energy + 30)
        session["contribution"] += 1
        return f"Used a bandage · healed {healed} LP"
    return "Held position"


def _settle_match(data: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    player_score = int(session["player_score"])
    opponent_score = int(session["opponent_score"])
    if player_score > opponent_score:
        result_id, tickets = "win", 2
        data["castle_wars_wins"] = _int(data.get("castle_wars_wins")) + 1
    elif player_score == opponent_score:
        result_id, tickets = "draw", 1
        data["castle_wars_draws"] = _int(data.get("castle_wars_draws")) + 1
    else:
        result_id, tickets = "loss", 0
        data["castle_wars_losses"] = _int(data.get("castle_wars_losses")) + 1
    credited = int(session["review"]) >= CASTLE_WARS_REWARD_MINIMUM_REVIEWS
    if credited:
        data["castle_wars_games_played"] = _int(data.get("castle_wars_games_played")) + 1
        data["castle_wars_tickets"] = _int(data.get("castle_wars_tickets")) + tickets
    else:
        tickets = 0
    message = (
        f"Castle Wars {result_id} · {player_score}-{opponent_score} · "
        f"+{tickets} ticket{'s' if tickets != 1 else ''}"
    )
    _end_match(data, session, message)
    return {
        "terminal": True,
        "result": result_id,
        "tickets": tickets,
        "credited": credited,
        "message": message,
    }


def apply_castle_wars_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    productive: bool,
    duty: str | None = None,
    opponent_roll: float = 0.5,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the roster state and session are rebuilt fresh, and
    # the combat encounter is assigned as a new object rather than edited in
    # place.
    data = dict(player_data)
    state = sanitize_castle_wars_state_pure(data)
    session = state["castle_wars"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != CASTLE_WARS_ACTIVITY_ID:
        return data, False, {"reason": "Enter Castle Wars before training it."}

    chosen = "idle"
    combat_result: dict[str, Any] = {}
    detail = "Waited while both teams fought"
    if productive:
        chosen = str(duty or _choose_duty(session))
        if chosen not in _VALID_DUTIES:
            chosen = _choose_duty(session)
        if chosen == "defend":
            data["current_combat_target"] = CASTLE_WARS_COMBAT_TARGET_ID
            data["combat_encounter"] = copy.deepcopy(session["encounter"])
            data, ok, combat_result = apply_combat_burst_pure(
                data,
                {CASTLE_WARS_COMBAT_TARGET_ID: castle_wars_raider_enemy_pure()},
                equipment_data or {},
                ticks=CASTLE_WARS_COMBAT_TICKS_PER_REVIEW,
                rng=rng,
                live_cadence=True,
                stop_after_first_kill=True,
                safe_death=True,
                allow_bank_run=False,
                player_damage_multiplier=castle_wars_damage_multiplier_pure(data),
            )
            if not ok:
                # Shallow like the other refusals above: every caller drops
                # this save unread when ok is False.
                return dict(player_data), False, combat_result
            damage = _int(combat_result.get("player_damage"))
            session["contribution"] += damage
            if combat_result.get("killed"):
                session["kills"] += 1
                session["opponent_capture_progress"] = max(
                    0, int(session["opponent_capture_progress"]) - 2
                )
            if combat_result.get("died"):
                session["deaths"] += 1
                data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
                data["combat_status_effects"] = {}
            enemy_lp = castle_wars_raider_enemy_pure()["stats"]["hitpoints"]
            encounter = data.get("combat_encounter")
            if combat_result.get("killed") or combat_result.get("died") or not isinstance(encounter, Mapping):
                encounter = {
                    "target_id": CASTLE_WARS_COMBAT_TARGET_ID,
                    "enemy_lifepoints": enemy_lp,
                }
                data["combat_encounter"] = copy.deepcopy(encounter)
            session["encounter"] = copy.deepcopy(encounter)
            detail = f"Defended against a raider · {damage} damage"
        else:
            detail = _apply_noncombat_duty(data, session, chosen)

    _advance_capture(session, "player", CASTLE_WARS_PLAYER_CROWD_PROGRESS)
    opponent_progress = CASTLE_WARS_OPPONENT_CROWD_PROGRESS
    try:
        if float(opponent_roll) < CASTLE_WARS_OPPONENT_BURST_CHANCE:
            opponent_progress += 1
    except (TypeError, ValueError):
        pass
    _advance_capture(session, "opponent", opponent_progress)
    pressure = CASTLE_WARS_PRESSURE_DAMAGE + (5 if chosen == "idle" else 0)
    if chosen == "defend" and not combat_result.get("died"):
        pressure = max(0, pressure - 10)
    _apply_pressure(session, pressure)

    session["review"] += 1
    if int(session["review"]) >= CASTLE_WARS_MATCH_REVIEWS:
        settled = _settle_match(data, session)
        return data, True, {**combat_result, **settled, "duty": chosen, "detail": detail}

    data.update(state)
    data["castle_wars"] = session
    data["current_combat_target"] = CASTLE_WARS_COMBAT_TARGET_ID
    status = (
        f"Castle Wars · beat {int(session['review'])}/{CASTLE_WARS_MATCH_REVIEWS} · "
        f"score {int(session['player_score'])}-{int(session['opponent_score'])} · "
        f"{detail}"
    )
    data["castle_wars_last_result"] = status
    return data, True, {
        **combat_result,
        "terminal": False,
        "duty": chosen,
        "detail": detail,
        "status": status,
        "player_score": int(session["player_score"]),
        "opponent_score": int(session["opponent_score"]),
    }


def deploy_castle_wars_ballista_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the roster state and session are rebuilt fresh, and
    # the combat encounter is assigned as a new object rather than edited in
    # place.
    data = dict(player_data)
    state = sanitize_castle_wars_state_pure(data)
    session = state["castle_wars"]
    if not session:
        return data, False, {"reason": "Enter Castle Wars before deploying a ballista."}
    if session["ballista_deployed"]:
        return data, False, {"reason": "The ballista is already deployed."}
    inventory = data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    missing = [item for item in CASTLE_WARS_BALLISTA_PARTS if _int(inventory.get(item)) < 1]
    if missing:
        return data, False, {"reason": "Requires all four Castle Wars ballista parts."}
    data.update(state)
    session["ballista_deployed"] = True
    data["castle_wars"] = session
    return data, True, {"message": "Deployed the Castle Wars ballista."}


def deploy_castle_wars_chinchompa_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the roster state and session are rebuilt fresh, and
    # the combat encounter is assigned as a new object rather than edited in
    # place.
    data = dict(player_data)
    state = sanitize_castle_wars_state_pure(data)
    session = state["castle_wars"]
    if not session:
        return data, False, {"reason": "Enter Castle Wars before deploying a chinchompa."}
    inventory = dict(data.get("inventory") or {})
    if _int(inventory.get("Castlewars chinchompa")) < 1:
        return data, False, {"reason": "Requires a Castlewars chinchompa."}
    inventory["Castlewars chinchompa"] -= 1
    session["opponent_capture_progress"] = max(
        0, int(session["opponent_capture_progress"]) - 2
    )
    session["contribution"] += 2
    data.update(state)
    data["inventory"] = inventory
    data["castle_wars"] = session
    return data, True, {"message": "Deployed a Castlewars chinchompa."}


def buy_castle_wars_reward_pure(
    player_data: Mapping[str, Any], reward_id: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the roster state and session are rebuilt fresh, and
    # the combat encounter is assigned as a new object rather than edited in
    # place.
    data = dict(player_data)
    state = sanitize_castle_wars_state_pure(data)
    if state["castle_wars"]:
        return data, False, {"reason": "Finish the current Castle Wars match first."}
    reward = CASTLE_WARS_REWARDS_BY_ID.get(str(reward_id))
    if reward is None:
        return data, False, {"reason": "Unknown Castle Wars reward."}
    if state["castle_wars_games_played"] < reward.minimum_games:
        return data, False, {
            "reason": f"Requires {reward.minimum_games} credited Castle Wars games."
        }
    if state["castle_wars_tickets"] < reward.ticket_cost:
        return data, False, {"reason": f"Requires {reward.ticket_cost} Castle Wars tickets."}
    inventory = dict(data.get("inventory") or {})
    inventory[reward.item_name] = _int(inventory.get(reward.item_name)) + reward.quantity
    data.update(state)
    data["inventory"] = inventory
    data["castle_wars_tickets"] = state["castle_wars_tickets"] - reward.ticket_cost
    return data, True, {
        "message": f"Bought {reward.quantity} x {reward.item_name}.",
        "reward_id": reward.reward_id,
    }


def sell_castle_wars_reward_pure(
    player_data: Mapping[str, Any], reward_id: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the roster state and session are rebuilt fresh, and
    # the combat encounter is assigned as a new object rather than edited in
    # place.
    data = dict(player_data)
    state = sanitize_castle_wars_state_pure(data)
    if state["castle_wars"]:
        return data, False, {"reason": "Finish the current Castle Wars match first."}
    reward = CASTLE_WARS_REWARDS_BY_ID.get(str(reward_id))
    if reward is None:
        return data, False, {"reason": "Unknown Castle Wars reward."}
    inventory = dict(data.get("inventory") or {})
    if _int(inventory.get(reward.item_name)) < reward.quantity:
        return data, False, {"reason": f"Requires {reward.quantity} x {reward.item_name}."}
    inventory[reward.item_name] -= reward.quantity
    data.update(state)
    data["inventory"] = inventory
    data["castle_wars_tickets"] = state["castle_wars_tickets"] + reward.ticket_cost
    return data, True, {
        "message": f"Sold {reward.quantity} x {reward.item_name} for {reward.ticket_cost} tickets.",
        "reward_id": reward.reward_id,
    }


def castle_wars_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_castle_wars_state_pure(player_data)
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    rewards = tuple(
        {
            "reward_id": reward.reward_id,
            "item_name": reward.item_name,
            "ticket_cost": reward.ticket_cost,
            "quantity": reward.quantity,
            "minimum_games": reward.minimum_games,
            "owned": _int(inventory.get(reward.item_name)),
            "can_buy": (
                not state["castle_wars"]
                and state["castle_wars_tickets"] >= reward.ticket_cost
                and state["castle_wars_games_played"] >= reward.minimum_games
            ),
            "can_sell": (
                not state["castle_wars"]
                and _int(inventory.get(reward.item_name)) >= reward.quantity
            ),
        }
        for reward in CASTLE_WARS_REWARDS
    )
    equipment = player_data.get("equipment")
    equipment = equipment if isinstance(equipment, Mapping) else {}
    entry_reasons = []
    if equipment.get("head") or equipment.get("cape"):
        entry_reasons.append("Remove equipped helmets and capes.")
    if _loaded_food_count(player_data):
        entry_reasons.append("Remove carried food from the Combat pack.")
    return {
        **state,
        "active": bool(state["castle_wars"]),
        "entry_locked_reasons": tuple(entry_reasons),
        "damage_multiplier": castle_wars_damage_multiplier_pure(player_data),
        "rewards": rewards,
        "ballista_ready": all(
            _int(inventory.get(item)) >= 1 for item in CASTLE_WARS_BALLISTA_PARTS
        ),
    }


def apply_castle_wars_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    payload = payload if isinstance(payload, Mapping) else {}
    if action_id == "enter":
        return enter_castle_wars_pure(player_data, payload)
    if action_id == "leave":
        return leave_castle_wars_pure(player_data)
    if action_id == "set_policy":
        return set_castle_wars_policy_pure(player_data, payload)
    if action_id == "buy":
        return buy_castle_wars_reward_pure(player_data, str(payload.get("reward_id", "")))
    if action_id == "sell":
        return sell_castle_wars_reward_pure(player_data, str(payload.get("reward_id", "")))
    if action_id == "deploy_ballista":
        return deploy_castle_wars_ballista_pure(player_data)
    if action_id == "deploy_chinchompa":
        return deploy_castle_wars_chinchompa_pure(player_data)
    # Shallow: an unrecognised action changes nothing, and the caller discards
    # this save because ok is False.
    return dict(player_data), False, {"reason": "Unknown Castle Wars command."}
