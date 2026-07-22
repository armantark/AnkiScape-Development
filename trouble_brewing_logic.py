"""Pure Trouble Brewing race, sabotage, reward, and policy mechanics."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

try:
    from .trouble_brewing_data import (
        TROUBLE_BREWING_ACTIVITY_ID,
        TROUBLE_BREWING_BOILER_BATCH_FUEL,
        TROUBLE_BREWING_BOILER_COUNT,
        TROUBLE_BREWING_BOILER_MAX_FUEL,
        TROUBLE_BREWING_BOILER_START_FUEL,
        TROUBLE_BREWING_BOTTLE_XP,
        TROUBLE_BREWING_CONTRIBUTION_CAP,
        TROUBLE_BREWING_DUTIES,
        TROUBLE_BREWING_DUTY_XP,
        TROUBLE_BREWING_EVENT_REVIEWS,
        TROUBLE_BREWING_OPPONENT_BATCH_PROGRESS,
        TROUBLE_BREWING_OPPONENT_EXTRA_PROGRESS_CHANCE,
        TROUBLE_BREWING_OPPONENT_SABOTAGE_CHANCE,
        TROUBLE_BREWING_PLAYER_SABOTAGE_PROGRESS,
        TROUBLE_BREWING_PLAYER_SABOTAGE_REVIEWS,
        TROUBLE_BREWING_RECIPE,
        TROUBLE_BREWING_REWARDS_BY_ID,
    )
except ImportError:  # pragma: no cover - flat test imports
    from trouble_brewing_data import (  # type: ignore
        TROUBLE_BREWING_ACTIVITY_ID,
        TROUBLE_BREWING_BOILER_BATCH_FUEL,
        TROUBLE_BREWING_BOILER_COUNT,
        TROUBLE_BREWING_BOILER_MAX_FUEL,
        TROUBLE_BREWING_BOILER_START_FUEL,
        TROUBLE_BREWING_BOTTLE_XP,
        TROUBLE_BREWING_CONTRIBUTION_CAP,
        TROUBLE_BREWING_DUTIES,
        TROUBLE_BREWING_DUTY_XP,
        TROUBLE_BREWING_EVENT_REVIEWS,
        TROUBLE_BREWING_OPPONENT_BATCH_PROGRESS,
        TROUBLE_BREWING_OPPONENT_EXTRA_PROGRESS_CHANCE,
        TROUBLE_BREWING_OPPONENT_SABOTAGE_CHANCE,
        TROUBLE_BREWING_PLAYER_SABOTAGE_PROGRESS,
        TROUBLE_BREWING_PLAYER_SABOTAGE_REVIEWS,
        TROUBLE_BREWING_RECIPE,
        TROUBLE_BREWING_REWARDS_BY_ID,
    )


TROUBLE_BREWING_STATE_VERSION = 1
_VALID_MODES = frozenset({"casual", "advanced"})
_VALID_DUTIES = frozenset(key for key, _label in TROUBLE_BREWING_DUTIES)
_XP_SKILLS = tuple(
    sorted(
        {
            skill
            for values in (*TROUBLE_BREWING_DUTY_XP.values(), TROUBLE_BREWING_BOTTLE_XP)
            for skill in values
        }
    )
)


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _float(value: Any, default: float = 0.0, *, maximum: float = 1_000_000_000.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0.0, min(parsed, maximum))


def _roll(value: Any) -> float:
    return min(_float(value, 0.5, maximum=0.999999), 0.999999)


def _quest_completed(data: Mapping[str, Any], quest_id: str) -> bool:
    quests = data.get("quests")
    if not isinstance(quests, Mapping):
        return False
    state = quests.get(quest_id)
    return isinstance(state, Mapping) and bool(state.get("completed"))


def default_trouble_brewing_state_pure() -> dict[str, Any]:
    return {
        "trouble_brewing": {},
        "trouble_brewing_policy": {
            "automation_mode": "casual",
            "duty": "water",
        },
        "trouble_brewing_pieces_of_eight": 0,
        "trouble_brewing_games_completed": 0,
        "trouble_brewing_last_result": "",
    }


def sanitize_trouble_brewing_policy_pure(raw: Any) -> dict[str, str]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    duty = str(source.get("duty", "water"))
    return {
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "duty": duty if duty in _VALID_DUTIES else "water",
    }


def sanitize_trouble_brewing_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    stores_raw = raw.get("stores")
    stores_raw = stores_raw if isinstance(stores_raw, Mapping) else {}
    xp_raw = raw.get("xp")
    xp_raw = xp_raw if isinstance(xp_raw, Mapping) else {}
    boilers_raw = raw.get("boilers")
    boilers_raw = boilers_raw if isinstance(boilers_raw, (list, tuple)) else ()
    boilers = [
        _int(
            boilers_raw[index] if index < len(boilers_raw) else TROUBLE_BREWING_BOILER_START_FUEL,
            maximum=TROUBLE_BREWING_BOILER_MAX_FUEL,
        )
        for index in range(TROUBLE_BREWING_BOILER_COUNT)
    ]
    mode = str(raw.get("automation_mode", "casual"))
    duty = str(raw.get("duty", "water"))
    return {
        "version": TROUBLE_BREWING_STATE_VERSION,
        "review": _int(raw.get("review"), maximum=TROUBLE_BREWING_EVENT_REVIEWS - 1),
        "stores": {
            ingredient: _int(stores_raw.get(ingredient), maximum=999)
            for ingredient in TROUBLE_BREWING_RECIPE
        },
        "boilers": boilers,
        "pending_bottle": bool(raw.get("pending_bottle", False)),
        "packed_rum": _int(raw.get("packed_rum"), maximum=999),
        "spilled_rum": _int(raw.get("spilled_rum"), maximum=999),
        "opponent_progress": _int(
            raw.get("opponent_progress"),
            maximum=TROUBLE_BREWING_OPPONENT_BATCH_PROGRESS - 1,
        ),
        "opponent_rum": _int(raw.get("opponent_rum"), maximum=999),
        "opponent_slowed": _int(
            raw.get("opponent_slowed"),
            maximum=TROUBLE_BREWING_PLAYER_SABOTAGE_REVIEWS,
        ),
        "repair_required": bool(raw.get("repair_required", False)),
        "contribution": _int(raw.get("contribution"), maximum=9999),
        "xp": {skill: _float(xp_raw.get(skill)) for skill in _XP_SKILLS},
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "duty": duty if duty in _VALID_DUTIES else "water",
    }


def sanitize_trouble_brewing_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    session = sanitize_trouble_brewing_session_pure(source.get("trouble_brewing"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", TROUBLE_BREWING_ACTIVITY_ID}:
        session = {}
    return {
        "trouble_brewing": session,
        "trouble_brewing_policy": sanitize_trouble_brewing_policy_pure(
            source.get("trouble_brewing_policy")
        ),
        "trouble_brewing_pieces_of_eight": _int(
            source.get("trouble_brewing_pieces_of_eight")
        ),
        "trouble_brewing_games_completed": _int(
            source.get("trouble_brewing_games_completed")
        ),
        "trouble_brewing_last_result": str(
            source.get("trouble_brewing_last_result", "") or ""
        )[:500],
    }


def set_trouble_brewing_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_trouble_brewing_state_pure(data)
    if state["trouble_brewing"]:
        return data, False, {"reason": "Finish or leave the current game first."}
    candidate = dict(state["trouble_brewing_policy"])
    candidate.update(dict(payload or {}))
    policy = sanitize_trouble_brewing_policy_pure(candidate)
    data.update(state)
    data["trouble_brewing_policy"] = policy
    return data, True, {"message": "Trouble Brewing plan saved.", "policy": policy}


def enter_trouble_brewing_pure(
    player_data: Mapping[str, Any],
    policy_payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if policy_payload:
        data, ok, info = set_trouble_brewing_policy_pure(player_data, policy_payload)
        if not ok:
            return data, False, info
    else:
        data = copy.deepcopy(dict(player_data))
    state = sanitize_trouble_brewing_state_pure(data)
    if state["trouble_brewing"]:
        return data, False, {"reason": "A Trouble Brewing game is already active."}
    if _int(data.get("cooking_level"), 1) < 40:
        return data, False, {"reason": "Requires level 40 Cooking."}
    if not _quest_completed(data, "cabin_fever"):
        return data, False, {"reason": "Complete Cabin Fever first."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != TROUBLE_BREWING_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}

    policy = state["trouble_brewing_policy"]
    data.update(state)
    data["trouble_brewing"] = {
        "version": TROUBLE_BREWING_STATE_VERSION,
        "review": 0,
        "stores": {ingredient: 0 for ingredient in TROUBLE_BREWING_RECIPE},
        "boilers": [TROUBLE_BREWING_BOILER_START_FUEL] * TROUBLE_BREWING_BOILER_COUNT,
        "pending_bottle": False,
        "packed_rum": 0,
        "spilled_rum": 0,
        "opponent_progress": 0,
        "opponent_rum": 0,
        "opponent_slowed": 0,
        "repair_required": False,
        "contribution": 0,
        "xp": {skill: 0.0 for skill in _XP_SKILLS},
        "automation_mode": policy["automation_mode"],
        "duty": policy["duty"],
    }
    data["activity_session"] = {"active_id": TROUBLE_BREWING_ACTIVITY_ID}
    data["current_utility"] = TROUBLE_BREWING_ACTIVITY_ID
    data["trouble_brewing_last_result"] = "Joined the blue team · sixteen duty beats remain"
    return data, True, {"message": data["trouble_brewing_last_result"]}


def _add_xp(session: dict[str, Any], duty: str) -> None:
    for skill, amount in TROUBLE_BREWING_DUTY_XP.get(duty, {}).items():
        session["xp"][skill] = float(session["xp"].get(skill, 0.0)) + amount


def _casual_duty(session: Mapping[str, Any]) -> str:
    if bool(session["repair_required"]):
        return "repair"
    if bool(session["pending_bottle"]):
        return "pack_rum"
    if min(int(value) for value in session["boilers"]) < TROUBLE_BREWING_BOILER_BATCH_FUEL:
        return "tend_boilers"
    stores = session["stores"]
    for ingredient in (
        "water",
        "coloured_water",
        "sweetgrubs",
        "scrapey_bark",
        "bitternut",
    ):
        if int(stores[ingredient]) < TROUBLE_BREWING_RECIPE[ingredient]:
            return ingredient
    return "water"


def _apply_player_duty(session: dict[str, Any], duty: str) -> str:
    if session["repair_required"]:
        session["repair_required"] = False
        _add_xp(session, "repair")
        return "Repaired the sabotaged brewing line"
    if duty in TROUBLE_BREWING_RECIPE:
        quantity = TROUBLE_BREWING_RECIPE[duty]
        session["stores"][duty] += quantity
        session["contribution"] += quantity
        _add_xp(session, duty)
        return f"Added {quantity} {duty.replace('_', ' ')}"
    if duty == "tend_boilers":
        session["boilers"] = [
            min(TROUBLE_BREWING_BOILER_MAX_FUEL, int(fuel) + TROUBLE_BREWING_BOILER_BATCH_FUEL)
            for fuel in session["boilers"]
        ]
        _add_xp(session, duty)
        return "Fed and lit all three boilers"
    if duty == "pack_rum":
        if session["pending_bottle"]:
            session["pending_bottle"] = False
            session["packed_rum"] += 1
            return "Packed one bottle of rum"
        return "No finished rum was ready to pack"
    if duty == "sabotage":
        session["opponent_progress"] = max(
            0,
            int(session["opponent_progress"]) - TROUBLE_BREWING_PLAYER_SABOTAGE_PROGRESS,
        )
        session["opponent_slowed"] = TROUBLE_BREWING_PLAYER_SABOTAGE_REVIEWS
        _add_xp(session, duty)
        return "Sabotaged the opposing brewing line"
    return "Waited beside the brewing line"


def _brew_player_batch(session: dict[str, Any]) -> bool:
    if min(int(value) for value in session["boilers"]) < TROUBLE_BREWING_BOILER_BATCH_FUEL:
        return False
    if any(
        int(session["stores"][ingredient]) < quantity
        for ingredient, quantity in TROUBLE_BREWING_RECIPE.items()
    ):
        return False
    for ingredient, quantity in TROUBLE_BREWING_RECIPE.items():
        session["stores"][ingredient] -= quantity
    if session["pending_bottle"]:
        session["spilled_rum"] += 1
    session["pending_bottle"] = True
    return True


def _advance_opponent(session: dict[str, Any], opponent_roll: float) -> None:
    if int(session["opponent_slowed"]) > 0:
        session["opponent_slowed"] -= 1
        return
    progress = 1
    if _roll(opponent_roll) < TROUBLE_BREWING_OPPONENT_EXTRA_PROGRESS_CHANCE:
        progress += 1
    session["opponent_progress"] += progress
    if session["opponent_progress"] >= TROUBLE_BREWING_OPPONENT_BATCH_PROGRESS:
        session["opponent_progress"] -= TROUBLE_BREWING_OPPONENT_BATCH_PROGRESS
        session["opponent_rum"] += 1


def _decay_boilers(session: dict[str, Any]) -> None:
    session["boilers"] = [max(0, int(fuel) - 1) for fuel in session["boilers"]]


def _finish_game(data: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    if session["pending_bottle"]:
        session["spilled_rum"] += 1
        session["pending_bottle"] = False
    pieces = min(TROUBLE_BREWING_CONTRIBUTION_CAP, int(session["contribution"]))
    pieces += 2 * int(session["packed_rum"])
    skill_xp = dict(session["xp"])
    for skill, amount in TROUBLE_BREWING_BOTTLE_XP.items():
        skill_xp[skill] = float(skill_xp.get(skill, 0.0)) + amount * int(session["packed_rum"])
    player_rum = int(session["packed_rum"])
    opponent_rum = int(session["opponent_rum"])
    outcome = "won" if player_rum > opponent_rum else "drew" if player_rum == opponent_rum else "lost"
    data["trouble_brewing_pieces_of_eight"] = _int(
        data.get("trouble_brewing_pieces_of_eight")
    ) + pieces
    data["trouble_brewing_games_completed"] = _int(
        data.get("trouble_brewing_games_completed")
    ) + 1
    data["trouble_brewing"] = {}
    data["activity_session"] = {"active_id": ""}
    data["trouble_brewing_last_result"] = (
        f"Game {outcome} {player_rum}-{opponent_rum} · {pieces} Pieces of Eight"
    )
    return {
        "terminal": True,
        "outcome": outcome,
        "player_rum": player_rum,
        "opponent_rum": opponent_rum,
        "pieces_of_eight": pieces,
        "skill_xp": skill_xp,
        "message": data["trouble_brewing_last_result"],
    }


def apply_trouble_brewing_review_pure(
    player_data: Mapping[str, Any],
    *,
    productive: bool,
    duty: str | None = None,
    opponent_roll: float = 0.5,
    sabotage_roll: float = 0.5,
) -> tuple[dict[str, Any], dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    session = sanitize_trouble_brewing_session_pure(data.get("trouble_brewing"))
    if not session:
        return data, {"terminal": False, "reason": "No Trouble Brewing game is active."}

    chosen = "idle"
    status = "No duty completed"
    if productive:
        chosen = (
            _casual_duty(session)
            if session["automation_mode"] == "casual"
            else str(duty or session["duty"])
        )
        if chosen not in _VALID_DUTIES and chosen != "repair":
            chosen = session["duty"]
        status = _apply_player_duty(session, chosen)

    brewed = _brew_player_batch(session)
    _advance_opponent(session, opponent_roll)
    if (
        not session["repair_required"]
        and chosen != "repair"
        and int(session["review"]) >= 2
        and _roll(sabotage_roll) < TROUBLE_BREWING_OPPONENT_SABOTAGE_CHANCE
    ):
        session["repair_required"] = True
    _decay_boilers(session)
    session["review"] += 1

    if session["review"] >= TROUBLE_BREWING_EVENT_REVIEWS:
        result = _finish_game(data, session)
        result.update({"duty": chosen, "status": status, "brewed": brewed})
        return data, result

    data["trouble_brewing"] = session
    data["trouble_brewing_last_result"] = (
        f"{status} · beat {session['review']}/{TROUBLE_BREWING_EVENT_REVIEWS}"
    )
    return data, {
        "terminal": False,
        "duty": chosen,
        "status": status,
        "brewed": brewed,
        "repair_required": session["repair_required"],
        "reviews_remaining": TROUBLE_BREWING_EVENT_REVIEWS - int(session["review"]),
        "skill_xp": {},
        "message": data["trouble_brewing_last_result"],
    }


def leave_trouble_brewing_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    if not sanitize_trouble_brewing_session_pure(data.get("trouble_brewing")):
        return data, False, {"reason": "No Trouble Brewing game is active."}
    data["trouble_brewing"] = {}
    data["activity_session"] = {"active_id": ""}
    data["trouble_brewing_last_result"] = "Left Trouble Brewing; match rewards were forfeited."
    return data, True, {"message": data["trouble_brewing_last_result"]}


def buy_trouble_brewing_reward_pure(
    player_data: Mapping[str, Any], reward_id: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    if sanitize_trouble_brewing_session_pure(data.get("trouble_brewing")):
        return data, False, {"reason": "Finish or leave the current game first."}
    reward = TROUBLE_BREWING_REWARDS_BY_ID.get(str(reward_id))
    if reward is None:
        return data, False, {"reason": "Unknown Trouble Brewing reward."}
    wallet = _int(data.get("trouble_brewing_pieces_of_eight"))
    if wallet < reward.pieces_of_eight:
        return data, False, {
            "reason": f"Requires {reward.pieces_of_eight} Pieces of Eight."
        }
    inventory = dict(data.get("inventory") or {})
    inventory[reward.display_name] = _int(inventory.get(reward.display_name)) + 1
    data["inventory"] = inventory
    data["trouble_brewing_pieces_of_eight"] = wallet - reward.pieces_of_eight
    data["trouble_brewing_last_result"] = f"Bought {reward.display_name}."
    return data, True, {"message": data["trouble_brewing_last_result"]}


def apply_trouble_brewing_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "enter":
        return enter_trouble_brewing_pure(player_data, body)
    if action_id == "leave":
        return leave_trouble_brewing_pure(player_data)
    if action_id == "set_policy":
        return set_trouble_brewing_policy_pure(player_data, body)
    if action_id == "buy_reward":
        return buy_trouble_brewing_reward_pure(
            player_data,
            str(body.get("reward_id", "")),
        )
    return copy.deepcopy(dict(player_data)), False, {
        "reason": "Unknown Trouble Brewing action."
    }


def trouble_brewing_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_trouble_brewing_state_pure(player_data)
    session = state["trouble_brewing"]
    reasons: list[str] = []
    if _int(player_data.get("cooking_level"), 1) < 40:
        reasons.append("Cooking 40")
    if not _quest_completed(player_data, "cabin_fever"):
        reasons.append("Cabin Fever")
    return {
        "locked_reasons": tuple(reasons),
        "active": bool(session),
        "session": session,
        "policy": state["trouble_brewing_policy"],
        "pieces_of_eight": state["trouble_brewing_pieces_of_eight"],
        "games_completed": state["trouble_brewing_games_completed"],
        "last_result": state["trouble_brewing_last_result"],
        "duties": TROUBLE_BREWING_DUTIES,
        "rewards": tuple(
            {
                "reward_id": reward.reward_id,
                "display_name": reward.display_name,
                "pieces_of_eight": reward.pieces_of_eight,
            }
            for reward in TROUBLE_BREWING_REWARDS_BY_ID.values()
        ),
    }
