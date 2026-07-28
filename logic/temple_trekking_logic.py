"""Pure seeded Temple Trekking escort sessions and reward-token redemption."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..data.temple_trekking_data import (
    TEMPLE_TREKKING_ACTIVITY_ID,
    TEMPLE_TREKKING_COMBAT_EVENT_IDS,
    TEMPLE_TREKKING_COMBAT_TARGET_ID,
    TEMPLE_TREKKING_COMBAT_TICKS,
    TEMPLE_TREKKING_COMPANION_BASE_LIFEPOINTS,
    TEMPLE_TREKKING_COMPANION_FOOD_CAP,
    TEMPLE_TREKKING_COMPANION_FOOD_HEAL,
    TEMPLE_TREKKING_COMPANION_FOOD_ITEM,
    TEMPLE_TREKKING_COMPANION_XP_PER_SUCCESS,
    TEMPLE_TREKKING_COMPANIONS,
    TEMPLE_TREKKING_COMPANIONS_BY_ID,
    TEMPLE_TREKKING_DEFAULT_COMPANIONS,
    TEMPLE_TREKKING_DEFAULT_REWARD,
    TEMPLE_TREKKING_DESTINATIONS,
    TEMPLE_TREKKING_DIRECTION_QUESTS,
    TEMPLE_TREKKING_DIRECTIONS,
    TEMPLE_TREKKING_EVENTS_BY_ID,
    TEMPLE_TREKKING_EVENTS_PER_TREK,
    TEMPLE_TREKKING_NONCOMBAT_EVENT_IDS,
    TEMPLE_TREKKING_REWARDS,
    TEMPLE_TREKKING_REWARDS_BY_ID,
    TEMPLE_TREKKING_ROUTES,
    TEMPLE_TREKKING_ROUTES_BY_ID,
    TEMPLE_TREKKING_START_POINTS,
    TEMPLE_TREKKING_TOKEN_COLORS,
    TEMPLE_TREKKING_TOKEN_ITEMS,
    TEMPLE_TREKKING_TOKEN_SCORE_THRESHOLDS,
    temple_trekking_enemy_pure,
)
from ..logic_pure.logic_pure import apply_combat_burst_pure, combat_max_lifepoints_pure


TEMPLE_TREKKING_STATE_VERSION = 1
_DIFFICULTY_SCORE = {"easy": 0, "medium": 1, "hard": 2}
_VALID_DIRECTIONS = frozenset(row[0] for row in TEMPLE_TREKKING_DIRECTIONS)
_VALID_ROUTES = frozenset(row.id for row in TEMPLE_TREKKING_ROUTES)


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _inventory(data: Mapping[str, Any]) -> Mapping[str, Any]:
    value = data.get("inventory")
    return value if isinstance(value, Mapping) else {}


def _mutable_inventory(data: dict[str, Any]) -> dict[str, Any]:
    inventory = data.get("inventory")
    if not isinstance(inventory, dict):
        inventory = {}
        data["inventory"] = inventory
    return inventory


def _held(data: Mapping[str, Any], item: str) -> int:
    return _int(_inventory(data).get(item))


def _consume(data: dict[str, Any], item: str, amount: int) -> None:
    inventory = _mutable_inventory(data)
    inventory[item] = _int(inventory.get(item)) - amount


def _grant(data: dict[str, Any], item: str, amount: int) -> None:
    inventory = _mutable_inventory(data)
    inventory[item] = _int(inventory.get(item)) + amount


def _quest_complete(data: Mapping[str, Any], quest_id: str) -> bool:
    quests = data.get("quests")
    quest = quests.get(quest_id) if isinstance(quests, Mapping) else None
    return isinstance(quest, Mapping) and bool(quest.get("completed"))


def default_temple_trekking_state_pure() -> dict[str, Any]:
    return {
        "version": TEMPLE_TREKKING_STATE_VERSION,
        "policy": {
            "direction": "trek",
            "route": "easy",
            "companion": TEMPLE_TREKKING_DEFAULT_COMPANIONS["trek"],
            "reward": TEMPLE_TREKKING_DEFAULT_REWARD,
        },
        "companion_levels": {row.id: 1 for row in TEMPLE_TREKKING_COMPANIONS},
        "companion_food": 0,
        "treks_started": 0,
        "treks_completed": 0,
        "treks_failed": 0,
        "treks_abandoned": 0,
        "completions": {"easy_easy": 0, "medium_medium": 0, "hard_hard": 0},
        "tokens_redeemed": 0,
        "session": {},
        "last_result": "",
    }


def _sanitize_policy(raw: Any) -> dict[str, str]:
    source = raw if isinstance(raw, Mapping) else {}
    direction = str(source.get("direction", "trek"))
    if direction not in _VALID_DIRECTIONS:
        direction = "trek"
    route = str(source.get("route", "easy"))
    if route not in _VALID_ROUTES:
        route = "easy"
    companion_id = str(source.get("companion", TEMPLE_TREKKING_DEFAULT_COMPANIONS[direction]))
    companion = TEMPLE_TREKKING_COMPANIONS_BY_ID.get(companion_id)
    if companion is None or companion.direction != direction:
        companion_id = TEMPLE_TREKKING_DEFAULT_COMPANIONS[direction]
    reward = str(source.get("reward", TEMPLE_TREKKING_DEFAULT_REWARD))
    if reward not in TEMPLE_TREKKING_REWARDS_BY_ID:
        reward = TEMPLE_TREKKING_DEFAULT_REWARD
    return {
        "direction": direction,
        "route": route,
        "companion": companion_id,
        "reward": reward,
    }


def _sanitize_nodes(raw: Any) -> list[str]:
    if not isinstance(raw, (list, tuple)):
        return []
    nodes = [str(value) for value in raw if str(value) in TEMPLE_TREKKING_EVENTS_BY_ID]
    return nodes[:TEMPLE_TREKKING_EVENTS_PER_TREK]


def _sanitize_session(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    direction = str(raw.get("direction", ""))
    route_id = str(raw.get("route", ""))
    companion_id = str(raw.get("companion", ""))
    companion = TEMPLE_TREKKING_COMPANIONS_BY_ID.get(companion_id)
    nodes = _sanitize_nodes(raw.get("nodes"))
    if (
        direction not in _VALID_DIRECTIONS
        or route_id not in _VALID_ROUTES
        or companion is None
        or companion.direction != direction
        or len(nodes) != TEMPLE_TREKKING_EVENTS_PER_TREK
    ):
        return {}
    cursor = min(_int(raw.get("cursor")), len(nodes) - 1)
    route = TEMPLE_TREKKING_ROUTES_BY_ID[route_id]
    maximum = max(
        1,
        _int(
            raw.get("companion_max_lifepoints"),
            TEMPLE_TREKKING_COMPANION_BASE_LIFEPOINTS[companion.difficulty],
        ),
    )
    lifepoints = min(maximum, _int(raw.get("companion_lifepoints"), maximum))
    if lifepoints <= 0:
        return {}
    event_id = nodes[cursor]
    enemies = _int(
        raw.get("enemies_remaining"),
        route.enemy_count if event_id in TEMPLE_TREKKING_COMBAT_EVENT_IDS else 0,
        maximum=route.enemy_count,
    )
    encounter = raw.get("encounter")
    return {
        "version": TEMPLE_TREKKING_STATE_VERSION,
        "trek_number": max(1, _int(raw.get("trek_number"), 1)),
        "direction": direction,
        "route": route_id,
        "companion": companion_id,
        "nodes": nodes,
        "cursor": cursor,
        "companion_lifepoints": lifepoints,
        "companion_max_lifepoints": maximum,
        "enemies_remaining": enemies,
        "encounter": copy.deepcopy(dict(encounter)) if isinstance(encounter, Mapping) else {},
        "previous_combat_target": str(raw.get("previous_combat_target", ""))[:120],
    }


def sanitize_temple_trekking_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_temple_trekking_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    levels = source.get("companion_levels") if isinstance(source.get("companion_levels"), Mapping) else {}
    completions = source.get("completions") if isinstance(source.get("completions"), Mapping) else {}
    return {
        **defaults,
        "policy": _sanitize_policy(source.get("policy")),
        "companion_levels": {
            row.id: max(1, min(99, _int(levels.get(row.id), 1)))
            for row in TEMPLE_TREKKING_COMPANIONS
        },
        "companion_food": min(
            TEMPLE_TREKKING_COMPANION_FOOD_CAP,
            _int(source.get("companion_food")),
        ),
        "treks_started": _int(source.get("treks_started")),
        "treks_completed": _int(source.get("treks_completed")),
        "treks_failed": _int(source.get("treks_failed")),
        "treks_abandoned": _int(source.get("treks_abandoned")),
        "completions": {
            key: _int(completions.get(key)) for key in defaults["completions"]
        },
        "tokens_redeemed": _int(source.get("tokens_redeemed")),
        "session": _sanitize_session(source.get("session")),
        "last_result": str(source.get("last_result", ""))[:500],
    }


def _event_sequence(trek_number: int) -> list[str]:
    seed = max(0, trek_number - 1)
    noncombat = TEMPLE_TREKKING_NONCOMBAT_EVENT_IDS
    combat = TEMPLE_TREKKING_COMBAT_EVENT_IDS
    return [
        noncombat[seed % len(noncombat)],
        combat[seed % len(combat)],
        noncombat[(seed + 1) % len(noncombat)],
        combat[(seed + 1) % len(combat)],
    ]


def _companion_max_lifepoints(state: Mapping[str, Any], companion_id: str) -> int:
    companion = TEMPLE_TREKKING_COMPANIONS_BY_ID[companion_id]
    level = _int(state["companion_levels"].get(companion_id), 1)
    return TEMPLE_TREKKING_COMPANION_BASE_LIFEPOINTS[companion.difficulty] + (level - 1) * 10


def _token_color(route_id: str, companion_id: str) -> str:
    companion = TEMPLE_TREKKING_COMPANIONS_BY_ID[companion_id]
    score = TEMPLE_TREKKING_ROUTES_BY_ID[route_id].difficulty + _DIFFICULTY_SCORE[companion.difficulty]
    blue_max, yellow_max = TEMPLE_TREKKING_TOKEN_SCORE_THRESHOLDS
    return "blue" if score <= blue_max else "yellow" if score <= yellow_max else "red"


def _entry_reasons(data: Mapping[str, Any], policy: Mapping[str, str]) -> tuple[str, ...]:
    reasons = []
    quest_id = TEMPLE_TREKKING_DIRECTION_QUESTS[policy["direction"]]
    if not _quest_complete(data, quest_id):
        reasons.append(f"Complete {quest_id.replace('_', ' ').title()}")
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != TEMPLE_TREKKING_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity")
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        reasons.append("Finish or leave the current Combat encounter")
    return tuple(reasons)


def set_temple_trekking_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_temple_trekking_state_pure(data.get("temple_trekking"))
    if state["session"]:
        return data, False, {"reason": "Finish or abandon the active trek first."}
    candidate = dict(state["policy"])
    candidate.update({key: payload[key] for key in candidate if key in payload})
    normalized = _sanitize_policy(candidate)
    if any(str(candidate[key]) != normalized[key] for key in candidate):
        return data, False, {"reason": "Unknown or mismatched Temple Trekking plan."}
    state["policy"] = normalized
    state["last_result"] = "Temple Trekking plan saved."
    data["temple_trekking"] = state
    return data, True, {"message": state["last_result"]}


def prepare_druid_pouch_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    if not _quest_complete(data, "nature_spirit"):
        return data, False, {"reason": "Complete Nature Spirit first."}
    if _held(data, "Druid pouch") > 0:
        return data, False, {"reason": "A filled Druid pouch is already in the Bank."}
    if _held(data, "Silver sickle (b)") <= 0:
        return data, False, {"reason": "A Silver sickle (b) is required to gather Mort Myre flora."}
    _grant(data, "Druid pouch", 1)
    state = sanitize_temple_trekking_state_pure(data.get("temple_trekking"))
    state["last_result"] = "Used Bloom in Mort Myre Swamp and filled a Druid pouch."
    data["temple_trekking"] = state
    return data, True, {"message": state["last_result"]}


def stock_temple_trekking_food_pure(
    player_data: Mapping[str, Any], quantity: int
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_temple_trekking_state_pure(data.get("temple_trekking"))
    if state["session"]:
        return data, False, {"reason": "Change the shared follower food pack between treks."}
    room = TEMPLE_TREKKING_COMPANION_FOOD_CAP - state["companion_food"]
    amount = min(room, max(0, _int(quantity)), _held(data, TEMPLE_TREKKING_COMPANION_FOOD_ITEM))
    if amount <= 0:
        return data, False, {"reason": "No Lobster can be added to the follower food pack."}
    _consume(data, TEMPLE_TREKKING_COMPANION_FOOD_ITEM, amount)
    state["companion_food"] += amount
    state["last_result"] = f"Loaded {amount} Lobster into the shared follower pack."
    data["temple_trekking"] = state
    return data, True, {"message": state["last_result"], "loaded": amount}


def enter_temple_trekking_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_temple_trekking_state_pure(data.get("temple_trekking"))
    if state["session"]:
        data["activity_session"] = {"active_id": TEMPLE_TREKKING_ACTIVITY_ID}
        data["current_utility"] = TEMPLE_TREKKING_ACTIVITY_ID
        return data, True, {"message": "Resumed the interrupted trek."}
    reasons = _entry_reasons(data, state["policy"])
    if reasons:
        return data, False, {"reason": "; ".join(reasons) + "."}
    trek_number = state["treks_started"] + 1
    companion_id = state["policy"]["companion"]
    maximum = _companion_max_lifepoints(state, companion_id)
    nodes = _event_sequence(trek_number)
    first_event = nodes[0]
    route = TEMPLE_TREKKING_ROUTES_BY_ID[state["policy"]["route"]]
    state["treks_started"] = trek_number
    state["session"] = {
        "version": TEMPLE_TREKKING_STATE_VERSION,
        "trek_number": trek_number,
        "direction": state["policy"]["direction"],
        "route": route.id,
        "companion": companion_id,
        "nodes": nodes,
        "cursor": 0,
        "companion_lifepoints": maximum,
        "companion_max_lifepoints": maximum,
        "enemies_remaining": route.enemy_count if first_event in TEMPLE_TREKKING_COMBAT_EVENT_IDS else 0,
        "encounter": {},
        "previous_combat_target": str(data.get("current_combat_target", ""))[:120],
    }
    companion = TEMPLE_TREKKING_COMPANIONS_BY_ID[companion_id]
    state["last_result"] = f"Set out with {companion.display_name} on the {route.display_name.lower()}."
    data["temple_trekking"] = state
    data["activity_session"] = {"active_id": TEMPLE_TREKKING_ACTIVITY_ID}
    data["current_utility"] = TEMPLE_TREKKING_ACTIVITY_ID
    data["combat_encounter"] = {}
    return data, True, {"message": state["last_result"]}


def _finish_session(data: dict[str, Any], state: dict[str, Any], message: str) -> None:
    session = state["session"]
    data["current_combat_target"] = str(session.get("previous_combat_target", ""))
    data["combat_encounter"] = {}
    data["activity_session"] = {"active_id": ""}
    state["session"] = {}
    state["last_result"] = message[:500]
    data["temple_trekking"] = state


def abandon_temple_trekking_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_temple_trekking_state_pure(data.get("temple_trekking"))
    if not state["session"]:
        return data, False, {"reason": "No Temple Trekking journey is active."}
    state["treks_abandoned"] += 1
    _finish_session(data, state, "Abandoned the trek and received no reward token.")
    return data, True, {"message": state["last_result"], "outcome": "abandoned"}


def _fail_trek(
    data: dict[str, Any], state: dict[str, Any], reason: str, *, player_died: bool
) -> dict[str, Any]:
    session = state["session"]
    start = TEMPLE_TREKKING_START_POINTS[session["direction"]]
    state["treks_failed"] += 1
    if player_died:
        grave = data.get("combat_grave")
        if isinstance(grave, dict) and grave:
            grave["location"] = start
    message = f"Temple Trekking failed · {reason} · no reward token."
    _finish_session(data, state, message)
    return {
        "advanced": True,
        "terminal": True,
        "failed": True,
        "player_died": player_died,
        "companion_died": not player_died,
        "message": message,
    }


def _complete_trek(data: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    session = state["session"]
    companion = TEMPLE_TREKKING_COMPANIONS_BY_ID[session["companion"]]
    route = TEMPLE_TREKKING_ROUTES_BY_ID[session["route"]]
    color = _token_color(route.id, companion.id)
    token_item = TEMPLE_TREKKING_TOKEN_ITEMS[color]
    _grant(data, token_item, 1)
    state["treks_completed"] += 1
    level_before = state["companion_levels"][companion.id]
    state["companion_levels"][companion.id] = min(
        99,
        level_before + TEMPLE_TREKKING_COMPANION_XP_PER_SUCCESS,
    )
    if route.id == companion.difficulty:
        state["completions"][f"{route.id}_{companion.difficulty}"] += 1
    destination = TEMPLE_TREKKING_DESTINATIONS[session["direction"]]
    message = f"Reached {destination} with {companion.display_name} · {color} reward token."
    _finish_session(data, state, message)
    return {
        "advanced": True,
        "terminal": True,
        "completed": True,
        "token_color": color,
        "token_item": token_item,
        "message": message,
    }


def _advance_node(data: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    session = state["session"]
    session["cursor"] += 1
    session["encounter"] = {}
    data["combat_encounter"] = {}
    if session["cursor"] >= len(session["nodes"]):
        return _complete_trek(data, state)
    next_event = session["nodes"][session["cursor"]]
    route = TEMPLE_TREKKING_ROUTES_BY_ID[session["route"]]
    session["enemies_remaining"] = (
        route.enemy_count if next_event in TEMPLE_TREKKING_COMBAT_EVENT_IDS else 0
    )
    return None


def _apply_companion_pressure(data: dict[str, Any], state: dict[str, Any]) -> tuple[int, bool]:
    session = state["session"]
    route = TEMPLE_TREKKING_ROUTES_BY_ID[session["route"]]
    before = session["companion_lifepoints"]
    session["companion_lifepoints"] = max(0, before - route.companion_pressure)
    ate = False
    if (
        session["companion_lifepoints"] > 0
        and session["companion_lifepoints"] <= session["companion_max_lifepoints"] // 2
        and state["companion_food"] > 0
    ):
        state["companion_food"] -= 1
        session["companion_lifepoints"] = min(
            session["companion_max_lifepoints"],
            session["companion_lifepoints"] + TEMPLE_TREKKING_COMPANION_FOOD_HEAL,
        )
        ate = True
    return before - session["companion_lifepoints"], ate


def _resolve_noncombat_event(
    data: dict[str, Any], state: dict[str, Any], event_id: str
) -> tuple[bool, dict[str, Any]]:
    event = TEMPLE_TREKKING_EVENTS_BY_ID[event_id]
    session = state["session"]
    if event.required_item and _held(data, event.required_item) <= 0:
        return False, {"reason": f"{event.required_item} is required for {event.display_name}."}
    if event.consume_count:
        if _held(data, event.required_item) < event.consume_count:
            return False, {"reason": f"{event.consume_count} {event.required_item} are required for {event.display_name}."}
        _consume(data, event.required_item, event.consume_count)
    if event_id == "abidor_crank":
        data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
        session["companion_lifepoints"] = session["companion_max_lifepoints"]
    terminal = _advance_node(data, state)
    message = f"Resolved {event.display_name}."
    state["last_result"] = terminal["message"] if terminal else message
    data["temple_trekking"] = state
    return True, terminal or {
        "advanced": True,
        "terminal": False,
        "event_id": event_id,
        "message": message,
    }


def apply_temple_trekking_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    equipment_data: Mapping[str, Any] | None = None,
    productive: bool = True,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_temple_trekking_state_pure(data.get("temple_trekking"))
    session = state["session"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != TEMPLE_TREKKING_ACTIVITY_ID:
        return data, False, {"reason": "Start or resume a Temple Trekking journey first."}
    if not productive:
        return data, True, {"advanced": False, "terminal": False, "message": "Again did not advance the trek."}
    event_id = session["nodes"][session["cursor"]]
    event = TEMPLE_TREKKING_EVENTS_BY_ID[event_id]
    if event.kind != "combat":
        ok, result = _resolve_noncombat_event(data, state, event_id)
        return data, ok, result
    if event.required_item and _held(data, event.required_item) <= 0:
        return data, False, {"reason": f"{event.required_item} is required for {event.display_name}."}

    companion_damage, companion_ate = _apply_companion_pressure(data, state)
    if session["companion_lifepoints"] <= 0:
        result = _fail_trek(
            data,
            state,
            f"{TEMPLE_TREKKING_COMPANIONS_BY_ID[session['companion']].display_name} fell",
            player_died=False,
        )
        return data, True, {**result, "companion_damage": companion_damage}

    enemy = temple_trekking_enemy_pure(event_id, session["route"])
    data["current_combat_target"] = TEMPLE_TREKKING_COMBAT_TARGET_ID
    encounter = copy.deepcopy(session["encounter"])
    encounter["target_id"] = TEMPLE_TREKKING_COMBAT_TARGET_ID
    encounter.setdefault("enemy_lifepoints", enemy["stats"]["hitpoints"])
    data["combat_encounter"] = encounter
    data, ok, combat = apply_combat_burst_pure(
        data,
        {TEMPLE_TREKKING_COMBAT_TARGET_ID: enemy},
        equipment_data or {},
        ticks=TEMPLE_TREKKING_COMBAT_TICKS,
        rng=rng or (lambda: 0.5),
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=False,
        allow_bank_run=False,
    )
    if not ok:
        return copy.deepcopy(dict(player_data)), False, combat
    if combat.get("died"):
        result = _fail_trek(data, state, "the player died", player_died=True)
        return data, True, {
            **combat,
            **result,
            "companion_damage": companion_damage,
            "companion_ate": companion_ate,
        }
    if combat.get("killed"):
        session["enemies_remaining"] = max(0, session["enemies_remaining"] - 1)
        session["encounter"] = {}
        data["combat_encounter"] = {}
        if session["enemies_remaining"] <= 0:
            if event_id == "shades":
                session["companion_lifepoints"] = min(
                    session["companion_max_lifepoints"],
                    session["companion_lifepoints"] + 100,
                )
            terminal = _advance_node(data, state)
            if terminal:
                return data, True, {
                    **combat,
                    **terminal,
                    "event_id": event_id,
                    "companion_damage": companion_damage,
                    "companion_ate": companion_ate,
                }
    else:
        session["encounter"] = copy.deepcopy(data.get("combat_encounter") or {})

    state["last_result"] = (
        f"{event.display_name} · {session['enemies_remaining']} enemies remain · "
        f"companion {session['companion_lifepoints']}/{session['companion_max_lifepoints']} LP"
    )
    data["temple_trekking"] = state
    return data, True, {
        "advanced": True,
        "terminal": False,
        "event_id": event_id,
        "combat": combat,
        "enemies_remaining": session["enemies_remaining"],
        "companion_damage": companion_damage,
        "companion_ate": companion_ate,
        "message": state["last_result"],
    }


def redeem_temple_trekking_token_pure(
    player_data: Mapping[str, Any],
    color: str,
    reward_id: str,
    roll: float,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_temple_trekking_state_pure(data.get("temple_trekking"))
    if color not in TEMPLE_TREKKING_TOKEN_COLORS:
        return data, False, {"reason": "Unknown Temple Trekking reward token."}
    reward = TEMPLE_TREKKING_REWARDS_BY_ID.get(reward_id)
    if reward is None:
        return data, False, {"reason": "Unknown Temple Trekking reward choice."}
    token_item = TEMPLE_TREKKING_TOKEN_ITEMS[color]
    if _held(data, token_item) <= 0:
        return data, False, {"reason": f"No {token_item} is held."}
    minimum, maximum = reward.ranges[color]
    bounded = max(0.0, min(_float(roll), 0.999999999))
    quantity = minimum + int(bounded * (maximum - minimum + 1))
    outputs = {}
    _consume(data, token_item, 1)
    for item_name, multiplier in reward.outputs:
        amount = quantity * multiplier
        _grant(data, item_name, amount)
        outputs[item_name] = amount
    state["tokens_redeemed"] += 1
    state["last_result"] = (
        f"Redeemed a {color} token for "
        + ", ".join(f"{amount} {item}" for item, amount in outputs.items())
        + "."
    )
    data["temple_trekking"] = state
    return data, True, {
        "message": state["last_result"],
        "reward_id": reward_id,
        "color": color,
        "outputs": outputs,
    }


def apply_temple_trekking_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "set_policy":
        return set_temple_trekking_policy_pure(player_data, body)
    if action_id == "prepare_pouch":
        return prepare_druid_pouch_pure(player_data)
    if action_id == "stock_food":
        return stock_temple_trekking_food_pure(player_data, _int(body.get("quantity"), 1))
    if action_id == "enter":
        return enter_temple_trekking_pure(player_data)
    if action_id == "abandon":
        return abandon_temple_trekking_pure(player_data)
    if action_id == "redeem":
        return redeem_temple_trekking_token_pure(
            player_data,
            str(body.get("color", "")),
            str(body.get("reward_id", "")),
            _float(body.get("roll")),
        )
    return copy.deepcopy(dict(player_data)), False, {"reason": "Unknown Temple Trekking command."}


def temple_trekking_can_review_pure(player_data: Mapping[str, Any]) -> bool:
    state = sanitize_temple_trekking_state_pure(player_data.get("temple_trekking"))
    return bool(state["session"])


def temple_trekking_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_temple_trekking_state_pure(player_data.get("temple_trekking"))
    session = state["session"]
    policy = state["policy"]
    reasons = _entry_reasons(player_data, policy) if not session else ()
    companion_id = session["companion"] if session else policy["companion"]
    companion = TEMPLE_TREKKING_COMPANIONS_BY_ID[companion_id]
    route_id = session["route"] if session else policy["route"]
    route = TEMPLE_TREKKING_ROUTES_BY_ID[route_id]
    event_id = session["nodes"][session["cursor"]] if session else ""
    event = TEMPLE_TREKKING_EVENTS_BY_ID.get(event_id)
    selected_for_reviews = str(player_data.get("current_utility", "")) == TEMPLE_TREKKING_ACTIVITY_ID
    token_counts = {
        color: _held(player_data, item_name)
        for color, item_name in TEMPLE_TREKKING_TOKEN_ITEMS.items()
    }
    reward_id = policy["reward"]
    available_colors = tuple(color for color in TEMPLE_TREKKING_TOKEN_COLORS if token_counts[color] > 0)
    return {
        **state,
        "active": bool(session),
        "entry_reasons": reasons,
        "can_enter": not session and not reasons,
        "policy_controls_enabled": not session,
        "direction_options": tuple(
            {
                "id": direction,
                "display_name": label,
                "unlocked": _quest_complete(player_data, TEMPLE_TREKKING_DIRECTION_QUESTS[direction]),
            }
            for direction, label in TEMPLE_TREKKING_DIRECTIONS
        ),
        "route_options": tuple(
            {"id": row.id, "display_name": row.display_name}
            for row in TEMPLE_TREKKING_ROUTES
        ),
        "companion_options": tuple(
            {
                "id": row.id,
                "display_name": row.display_name,
                "difficulty": row.difficulty,
                "level": state["companion_levels"][row.id],
            }
            for row in TEMPLE_TREKKING_COMPANIONS
            if row.direction == policy["direction"]
        ),
        "reward_options": tuple(
            {"id": row.id, "display_name": row.display_name}
            for row in TEMPLE_TREKKING_REWARDS
        ),
        "companion_name": companion.display_name,
        "companion_difficulty": companion.difficulty,
        "companion_level": state["companion_levels"][companion.id],
        "companion_lifepoints": (
            session["companion_lifepoints"]
            if session
            else _companion_max_lifepoints(state, companion.id)
        ),
        "companion_max_lifepoints": (
            session["companion_max_lifepoints"]
            if session
            else _companion_max_lifepoints(state, companion.id)
        ),
        "route_name": route.display_name,
        "event_name": event.display_name if event else "Ready at the start point",
        "event_kind": event.kind if event else "",
        "event_index": session["cursor"] + 1 if session else 0,
        "event_count": len(session["nodes"]) if session else TEMPLE_TREKKING_EVENTS_PER_TREK,
        "enemies_remaining": session["enemies_remaining"] if session else 0,
        "primary_label": (
            "Selected for reviews"
            if session and selected_for_reviews
            else "Select for reviews"
            if session
            else "Start trek"
        ),
        "primary_enabled": (bool(session) and not selected_for_reviews) or (not session and not reasons),
        "abandon_visible": bool(session),
        "food_load_enabled": not session and state["companion_food"] < TEMPLE_TREKKING_COMPANION_FOOD_CAP and _held(player_data, TEMPLE_TREKKING_COMPANION_FOOD_ITEM) > 0,
        "pouch_prepare_enabled": (
            not session
            and _quest_complete(player_data, "nature_spirit")
            and _held(player_data, "Druid pouch") <= 0
            and _held(player_data, "Silver sickle (b)") > 0
        ),
        "token_counts": token_counts,
        "available_token_colors": available_colors,
        "redeem_enabled": bool(available_colors),
        "redeem_reason": "" if available_colors else "Earn a reward token by completing a trek.",
        "selected_reward": reward_id,
        "status_text": state["last_result"] or "Choose a direction, route, companion, and token reward.",
    }
