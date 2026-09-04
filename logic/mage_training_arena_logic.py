"""Pure review-driven Mage Training Arena rooms, policies, and reward shop."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..data.mage_training_arena_data import (
    MAGE_TRAINING_ARENA_ACTIVITY_ID,
    MAGE_TRAINING_ARENA_ALCHEMY_CASTS_PER_POINT,
    MAGE_TRAINING_ARENA_ALCHEMY_NATURE_RUNES_PER_POINT,
    MAGE_TRAINING_ARENA_APPROACHES,
    MAGE_TRAINING_ARENA_CHECKPOINT_RATES,
    MAGE_TRAINING_ARENA_DEFAULT_GOAL,
    MAGE_TRAINING_ARENA_ENCHANTMENT_REWARD_RUNES,
    MAGE_TRAINING_ARENA_FALLING_BONE_CHANCE,
    MAGE_TRAINING_ARENA_GRAVEYARD_REWARD_RUNES,
    MAGE_TRAINING_ARENA_MAZE_MOVES,
    MAGE_TRAINING_ARENA_POINT_CAPS,
    MAGE_TRAINING_ARENA_REWARDS,
    MAGE_TRAINING_ARENA_REWARDS_BY_ID,
    MAGE_TRAINING_ARENA_ROOM_IDS,
    MAGE_TRAINING_ARENA_ROOM_LEVELS,
    MAGE_TRAINING_ARENA_ROOM_POLICIES,
)
from ..logic_pure.logic_pure import combat_max_lifepoints_pure
from .cadence_kernel import (
    advance_cadence_pure,
    default_cadence_profile_state_pure,
    rate_limited_profile_pure,
    sanitize_cadence_profile_state_pure,
)


MAGE_TRAINING_ARENA_STATE_VERSION = 1
_VALID_APPROACHES = frozenset(row[0] for row in MAGE_TRAINING_ARENA_APPROACHES)
_ROOM_LABELS = dict(MAGE_TRAINING_ARENA_ROOM_POLICIES)
_VALID_ROOM_POLICIES = frozenset(_ROOM_LABELS)
_ROOM_CADENCE_PROFILES = {
    room_id: rate_limited_profile_pure(
        f"mage_training_arena:{room_id}",
        rate[0],
        rate[1],
    )
    for room_id, rate in MAGE_TRAINING_ARENA_CHECKPOINT_RATES.items()
}
_ENCHANTMENT_SPELLS = (
    (1, 7, 17.5, {"Cosmic rune": 1, "Water rune": 1}),
    (2, 27, 37.0, {"Cosmic rune": 1, "Air rune": 3}),
    (3, 49, 59.0, {"Cosmic rune": 1, "Fire rune": 5}),
    (4, 57, 67.0, {"Cosmic rune": 1, "Earth rune": 10}),
    (5, 68, 78.0, {"Cosmic rune": 1, "Earth rune": 15, "Water rune": 15}),
    (6, 87, 97.0, {"Cosmic rune": 1, "Earth rune": 20, "Fire rune": 20}),
)


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


def _blank_wallets() -> dict[str, int]:
    return {room_id: 0 for room_id in MAGE_TRAINING_ARENA_ROOM_IDS}


def _blank_room_counts() -> dict[str, int]:
    return {
        "telekinetic_mazes": 0,
        "alchemist_deposits": 0,
        "enchantment_shapes": 0,
        "graveyard_deposits": 0,
        "graveyard_bone_cursor": 0,
        "graveyard_fruit_residual": 0,
    }


def default_mage_training_arena_state_pure() -> dict[str, Any]:
    return {
        "version": MAGE_TRAINING_ARENA_STATE_VERSION,
        "completed": False,
        "active": False,
        "entries": 0,
        "progress_hat_owned": False,
        "room_policy": "auto",
        "approach": "fast_rewards",
        "reward_goal": MAGE_TRAINING_ARENA_DEFAULT_GOAL,
        "current_room": "",
        "wallets": _blank_wallets(),
        "room_counts": _blank_room_counts(),
        "cadence": {
            room_id: default_cadence_profile_state_pure()
            for room_id in MAGE_TRAINING_ARENA_ROOM_IDS
        },
        "purchases": {},
        "last_result": "",
    }


def sanitize_mage_training_arena_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_mage_training_arena_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    wallets_raw = source.get("wallets") if isinstance(source.get("wallets"), Mapping) else {}
    counts_raw = source.get("room_counts") if isinstance(source.get("room_counts"), Mapping) else {}
    cadence_raw = source.get("cadence") if isinstance(source.get("cadence"), Mapping) else {}
    purchases_raw = source.get("purchases") if isinstance(source.get("purchases"), Mapping) else {}
    room_policy = str(source.get("room_policy", "auto"))
    approach = str(source.get("approach", "fast_rewards"))
    goal = str(source.get("reward_goal", MAGE_TRAINING_ARENA_DEFAULT_GOAL))
    active = bool(source.get("active", False))
    current_room = str(source.get("current_room", ""))
    if current_room not in MAGE_TRAINING_ARENA_ROOM_IDS:
        current_room = ""
    if not active:
        current_room = ""
    return {
        **defaults,
        "completed": bool(source.get("completed", False)),
        "active": active,
        "entries": _int(source.get("entries")),
        "progress_hat_owned": bool(source.get("progress_hat_owned", False)),
        "room_policy": room_policy if room_policy in _VALID_ROOM_POLICIES else "auto",
        "approach": approach if approach in _VALID_APPROACHES else "fast_rewards",
        "reward_goal": goal if goal in MAGE_TRAINING_ARENA_REWARDS_BY_ID else MAGE_TRAINING_ARENA_DEFAULT_GOAL,
        "current_room": current_room,
        "wallets": {
            room_id: min(
                MAGE_TRAINING_ARENA_POINT_CAPS[room_id],
                _int(wallets_raw.get(room_id)),
            )
            for room_id in MAGE_TRAINING_ARENA_ROOM_IDS
        },
        "room_counts": {
            key: _int(counts_raw.get(key)) for key in defaults["room_counts"]
        },
        "cadence": {
            room_id: sanitize_cadence_profile_state_pure(cadence_raw.get(room_id))
            for room_id in MAGE_TRAINING_ARENA_ROOM_IDS
        },
        "purchases": {
            reward_id: _int(count)
            for reward_id, count in purchases_raw.items()
            if reward_id in MAGE_TRAINING_ARENA_REWARDS_BY_ID
        },
        "last_result": str(source.get("last_result", ""))[:500],
    }


def _inventory(data: Mapping[str, Any]) -> Mapping[str, Any]:
    value = data.get("inventory")
    return value if isinstance(value, Mapping) else {}


def _has_items(data: Mapping[str, Any], requirements: Mapping[str, int]) -> bool:
    inventory = _inventory(data)
    return all(_int(inventory.get(item)) >= amount for item, amount in requirements.items())


def _mutable_inventory(data: dict[str, Any]) -> dict[str, Any]:
    inventory = data.get("inventory")
    if not isinstance(inventory, dict):
        inventory = {}
        data["inventory"] = inventory
    return inventory


def _consume_items(data: dict[str, Any], requirements: Mapping[str, int]) -> None:
    inventory = _mutable_inventory(data)
    for item, amount in requirements.items():
        inventory[item] = _int(inventory.get(item)) - amount


def _grant_item(data: dict[str, Any], item: str, amount: int = 1) -> None:
    inventory = _mutable_inventory(data)
    inventory[item] = _int(inventory.get(item)) + amount


def _magic_level(data: Mapping[str, Any]) -> int:
    return max(1, _int(data.get("magic_level"), 1))


def _enchantment_spell(data: Mapping[str, Any], approach: str):
    magic_level = _magic_level(data)
    rows = _ENCHANTMENT_SPELLS if approach == "conserve_runes" else reversed(_ENCHANTMENT_SPELLS)
    return next((row for row in rows if magic_level >= row[1]), None)


def _room_requirements(
    data: Mapping[str, Any], state: Mapping[str, Any], room_id: str
) -> dict[str, int]:
    if room_id == "telekinetic":
        maze = _int(state["room_counts"].get("telekinetic_mazes"))
        moves = MAGE_TRAINING_ARENA_MAZE_MOVES[maze % len(MAGE_TRAINING_ARENA_MAZE_MOVES)]
        return {"Law rune": moves, "Air rune": moves}
    if room_id == "alchemist":
        high_alchemy = str(state["approach"]) == "fast_rewards" and _magic_level(data) >= 55
        fire_per_cast = 5 if high_alchemy else 3
        return {
            "Nature rune": MAGE_TRAINING_ARENA_ALCHEMY_NATURE_RUNES_PER_POINT,
            "Fire rune": fire_per_cast * MAGE_TRAINING_ARENA_ALCHEMY_CASTS_PER_POINT,
        }
    if room_id == "enchantment":
        spell = _enchantment_spell(data, str(state["approach"]))
        return dict(spell[3]) if spell else {}
    if room_id == "graveyard":
        peaches = bool(state.get("completed")) and _magic_level(data) >= 60
        return (
            {"Water rune": 4, "Earth rune": 2, "Nature rune": 2}
            if peaches
            else {"Water rune": 2, "Earth rune": 2, "Nature rune": 1}
        )
    return {}


def _room_locked_reasons(
    data: Mapping[str, Any], state: Mapping[str, Any], room_id: str
) -> tuple[str, ...]:
    reasons = []
    level = MAGE_TRAINING_ARENA_ROOM_LEVELS[room_id]
    if _magic_level(data) < level:
        reasons.append(f"Magic level {level}")
    requirements = _room_requirements(data, state, room_id)
    inventory = _inventory(data)
    for item, amount in requirements.items():
        held = _int(inventory.get(item))
        if held < amount:
            reasons.append(f"{amount} {item} ({held} held)")
    return tuple(reasons)


def _reward_costs_with_chain(data: Mapping[str, Any], reward_id: str) -> dict[str, int]:
    totals = _blank_wallets()
    inventory = _inventory(data)
    reward = MAGE_TRAINING_ARENA_REWARDS_BY_ID[reward_id]
    chain = []
    cursor = reward
    seen = set()
    while cursor and cursor.id not in seen:
        seen.add(cursor.id)
        chain.append(cursor)
        required = cursor.required_item
        if not required or _int(inventory.get(required)) > 0:
            break
        cursor = next(
            (row for row in MAGE_TRAINING_ARENA_REWARDS if row.output_item == required),
            None,
        )
    for row in chain:
        for room_id, amount in row.cost_map().items():
            totals[room_id] += amount
    return totals


def _auto_room(data: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    target = _reward_costs_with_chain(data, str(state["reward_goal"]))
    candidates = []
    for index, room_id in enumerate(MAGE_TRAINING_ARENA_ROOM_IDS):
        deficit = max(0, target[room_id] - _int(state["wallets"].get(room_id)))
        if deficit <= 0 or _room_locked_reasons(data, state, room_id):
            continue
        rate_num, rate_den = MAGE_TRAINING_ARENA_CHECKPOINT_RATES[room_id]
        workload = deficit * rate_den / rate_num
        rune_cost = sum(_room_requirements(data, state, room_id).values())
        tie = -rune_cost if state["approach"] == "conserve_runes" else -index
        candidates.append((workload, tie, room_id))
    return max(candidates, default=(0, 0, ""))[2]


def _selected_room(data: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    policy = str(state["room_policy"])
    return _auto_room(data, state) if policy == "auto" else policy


def _purchase_reason(data: Mapping[str, Any], state: Mapping[str, Any], reward_id: str) -> str:
    reward = MAGE_TRAINING_ARENA_REWARDS_BY_ID.get(reward_id)
    if reward is None:
        return "Unknown Mage Training Arena reward."
    if reward.unlock and bool(state.get("completed")):
        return "Bones to Peaches is already unlocked."
    if reward.required_item and _int(_inventory(data).get(reward.required_item)) <= 0:
        return f"Bring a {reward.required_item} for this wand upgrade."
    missing = [
        f"{amount - _int(state['wallets'].get(room_id)):,} more {room_id} points"
        for room_id, amount in reward.cost_map().items()
        if _int(state["wallets"].get(room_id)) < amount
    ]
    return "; ".join(missing)


def _entry_reasons(player_data: Mapping[str, Any]) -> tuple[str, ...]:
    active_session = player_data.get("activity_session")
    active_id = (
        str(active_session.get("active_id", ""))
        if isinstance(active_session, Mapping)
        else ""
    )
    reasons = []
    if _magic_level(player_data) < 7:
        reasons.append("Magic level 7")
    if active_id and active_id != MAGE_TRAINING_ARENA_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity")
    return tuple(reasons)


def mage_training_arena_can_review_pure(player_data: Mapping[str, Any]) -> bool:
    state = sanitize_mage_training_arena_state_pure(
        player_data.get("mage_training_arena")
    )
    room_id = _selected_room(player_data, state)
    return bool(
        state["active"]
        and room_id
        and not _room_locked_reasons(player_data, state, room_id)
    )


def mage_training_arena_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_mage_training_arena_state_pure(player_data.get("mage_training_arena"))
    entry_reasons = _entry_reasons(player_data)
    selected_room = _selected_room(player_data, state)
    room_rows = []
    for room_id in MAGE_TRAINING_ARENA_ROOM_IDS:
        locked = _room_locked_reasons(player_data, state, room_id)
        room_rows.append(
            {
                "id": room_id,
                "display_name": _ROOM_LABELS[room_id],
                "minimum_magic": MAGE_TRAINING_ARENA_ROOM_LEVELS[room_id],
                "locked_reasons": locked,
                "runnable": not locked,
                "points": state["wallets"][room_id],
                "cap": MAGE_TRAINING_ARENA_POINT_CAPS[room_id],
            }
        )
    reward_rows = []
    for reward in MAGE_TRAINING_ARENA_REWARDS:
        reason = _purchase_reason(player_data, state, reward.id)
        reward_rows.append(
            {
                "id": reward.id,
                "display_name": reward.display_name,
                "costs": reward.cost_map(),
                "required_item": reward.required_item,
                "purchase_enabled": not reason,
                "purchase_reason": reason,
                "purchased": _int(state["purchases"].get(reward.id)),
            }
        )
    selected_for_reviews = str(player_data.get("current_utility", "")) == MAGE_TRAINING_ARENA_ACTIVITY_ID
    active = state["active"]
    room_reasons = (
        _room_locked_reasons(player_data, state, selected_room)
        if selected_room
        else ("No needed room is runnable",)
    )
    goal_purchase_reason = _purchase_reason(
        player_data,
        state,
        state["reward_goal"],
    )
    return {
        **state,
        "can_enter": not entry_reasons and not active,
        "entry_reasons": entry_reasons,
        "selected_room": selected_room,
        "room_options": tuple(room_rows),
        "reward_options": tuple(reward_rows),
        "can_review": active and bool(selected_room) and not room_reasons,
        "review_reasons": room_reasons,
        "policy_controls_enabled": not active,
        "primary_label": (
            "Active for reviews" if active and selected_for_reviews else "Select for reviews" if active else "Enter Arena"
        ),
        "primary_enabled": (active and not selected_for_reviews) or (not active and not entry_reasons),
        "leave_visible": active,
        "purchase_enabled": not goal_purchase_reason,
        "purchase_reason": goal_purchase_reason,
        "wallet_text": " · ".join(
            f"{room_id.title()} {state['wallets'][room_id]:,}/{MAGE_TRAINING_ARENA_POINT_CAPS[room_id]:,}"
            for room_id in MAGE_TRAINING_ARENA_ROOM_IDS
        ),
        "status_text": state["last_result"] or "Choose a reward goal, room policy, and approach.",
    }


def set_mage_training_arena_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_mage_training_arena_state_pure(data.get("mage_training_arena"))
    if state["active"]:
        return data, False, {"reason": "Leave the Arena before changing its plan."}
    room_policy = str(payload.get("room_policy", state["room_policy"]))
    approach = str(payload.get("approach", state["approach"]))
    goal = str(payload.get("reward_goal", state["reward_goal"]))
    if room_policy not in _VALID_ROOM_POLICIES:
        return data, False, {"reason": "Unknown Mage Training Arena room policy."}
    if approach not in _VALID_APPROACHES:
        return data, False, {"reason": "Unknown Mage Training Arena approach."}
    if goal not in MAGE_TRAINING_ARENA_REWARDS_BY_ID:
        return data, False, {"reason": "Unknown Mage Training Arena reward goal."}
    state.update({"room_policy": room_policy, "approach": approach, "reward_goal": goal})
    state["last_result"] = "Mage Training Arena plan saved."
    data["mage_training_arena"] = state
    return data, True, {"message": state["last_result"]}


def enter_mage_training_arena_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_mage_training_arena_state_pure(data.get("mage_training_arena"))
    if state["active"]:
        return data, False, {"reason": "The Mage Training Arena is already active."}
    entry_reasons = _entry_reasons(data)
    if entry_reasons:
        return data, False, {"reason": "; ".join(entry_reasons) + "."}
    state["active"] = True
    state["entries"] += 1
    if not state["progress_hat_owned"]:
        state["progress_hat_owned"] = True
        _grant_item(data, "Progress hat")
    state["current_room"] = _selected_room(data, state)
    state["last_result"] = "Entered the Mage Training Arena and put on the Progress hat."
    data["mage_training_arena"] = state
    data["activity_session"] = {"active_id": MAGE_TRAINING_ARENA_ACTIVITY_ID}
    data["current_utility"] = MAGE_TRAINING_ARENA_ACTIVITY_ID
    return data, True, {"message": state["last_result"], "entry": state["entries"]}


def leave_mage_training_arena_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_mage_training_arena_state_pure(data.get("mage_training_arena"))
    if not state["active"]:
        return data, False, {"reason": "The Mage Training Arena is not active."}
    state["active"] = False
    state["current_room"] = ""
    state["last_result"] = "Left the Mage Training Arena lobby."
    data["mage_training_arena"] = state
    data["activity_session"] = {"active_id": ""}
    return data, True, {"message": state["last_result"]}


def purchase_mage_training_arena_reward_pure(
    player_data: Mapping[str, Any], reward_id: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_mage_training_arena_state_pure(data.get("mage_training_arena"))
    reward = MAGE_TRAINING_ARENA_REWARDS_BY_ID.get(reward_id)
    reason = _purchase_reason(data, state, reward_id)
    if reason:
        return data, False, {"reason": reason}
    for room_id, amount in reward.cost_map().items():
        state["wallets"][room_id] -= amount
    if reward.required_item:
        _consume_items(data, {reward.required_item: 1})
    if reward.output_item:
        _grant_item(data, reward.output_item, reward.output_count)
    if reward.unlock == "bones_to_peaches":
        state["completed"] = True
    state["purchases"][reward.id] = _int(state["purchases"].get(reward.id)) + 1
    state["last_result"] = f"Purchased {reward.display_name}."
    data["mage_training_arena"] = state
    return data, True, {"message": state["last_result"], "reward_id": reward.id}


def apply_mage_training_arena_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "set_policy":
        return set_mage_training_arena_policy_pure(player_data, body)
    if action_id == "enter":
        return enter_mage_training_arena_pure(player_data)
    if action_id == "leave":
        return leave_mage_training_arena_pure(player_data)
    if action_id == "purchase":
        reward_id = str(body.get("reward_id", ""))
        return purchase_mage_training_arena_reward_pure(player_data, reward_id)
    return copy.deepcopy(dict(player_data)), False, {"reason": "Unknown Mage Training Arena command."}


def _add_points(state: dict[str, Any], room_id: str, amount: int) -> int:
    before = _int(state["wallets"].get(room_id))
    after = min(MAGE_TRAINING_ARENA_POINT_CAPS[room_id], before + amount)
    state["wallets"][room_id] = after
    return after - before


def _reward_rune(options: tuple[str, ...], rng: Callable[[], float] | None) -> str:
    try:
        roll = max(0.0, min(0.999999999, float((rng or (lambda: 0.0))())))
    except (TypeError, ValueError, OverflowError):
        roll = 0.0
    return options[int(roll * len(options))]


def _graveyard_death(data: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    lost = min(10, state["wallets"]["graveyard"])
    state["wallets"]["graveyard"] -= lost
    state["active"] = False
    state["current_room"] = ""
    state["last_result"] = f"Falling bones defeated you; returned to the lobby and lost {lost} Graveyard points."
    data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
    data["mage_training_arena"] = state
    data["activity_session"] = {"active_id": ""}
    return {
        "advanced": True,
        "terminal": True,
        "died": True,
        "room": "graveyard",
        "points_gained": 0,
        "points_lost": lost,
        "magic_xp": 0.0,
        "message": state["last_result"],
    }


def apply_mage_training_arena_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    productive: bool = True,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_mage_training_arena_state_pure(data.get("mage_training_arena"))
    if not state["active"]:
        return data, False, {"reason": "Enter the Mage Training Arena before training."}
    if not productive:
        return data, True, {"advanced": False, "terminal": False, "message": "Again did not advance the Arena."}
    room_id = _selected_room(data, state)
    if not room_id:
        state["current_room"] = ""
        state["last_result"] = "The selected reward goal is funded; purchase it from the Rewards Guardian."
        data["mage_training_arena"] = state
        return data, True, {
            "advanced": False,
            "terminal": True,
            "goal_ready": True,
            "points_gained": 0,
            "magic_xp": 0.0,
            "message": state["last_result"],
        }
    reasons = _room_locked_reasons(data, state, room_id)
    if reasons:
        return data, False, {"reason": "; ".join(reasons) + "."}
    state["current_room"] = room_id

    step = advance_cadence_pure(
        _ROOM_CADENCE_PROFILES[room_id],
        state["cadence"][room_id],
    )
    state["cadence"][room_id] = step.state
    if not step.emitted:
        state["last_result"] = f"{_ROOM_LABELS[room_id]} progress continued; the next checkpoint is not ready."
        data["mage_training_arena"] = state
        return data, True, {
            "advanced": True,
            "terminal": False,
            "checkpoint": False,
            "room": room_id,
            "points_gained": 0,
            "magic_xp": 0.0,
            "message": state["last_result"],
        }

    falling_bone = False
    if room_id == "graveyard":
        try:
            falling_bone = float((rng or (lambda: 1.0))()) < MAGE_TRAINING_ARENA_FALLING_BONE_CHANCE
        except (TypeError, ValueError, OverflowError):
            falling_bone = False
        if falling_bone:
            current_lp = _int(
                data.get("combat_lifepoints"),
                combat_max_lifepoints_pure(data),
            )
            if current_lp <= 20:
                result = _graveyard_death(data, state)
                return data, True, result
            data["combat_lifepoints"] = current_lp - 20

    requirements = _room_requirements(data, state, room_id)
    if not _has_items(data, requirements):
        return copy.deepcopy(dict(player_data)), False, {"reason": "The room's required runes are no longer available."}
    _consume_items(data, requirements)
    points = 0
    magic_xp = 0.0
    extras = {}
    if room_id == "telekinetic":
        state["room_counts"]["telekinetic_mazes"] += 1
        maze_count = state["room_counts"]["telekinetic_mazes"]
        moves = requirements["Law rune"]
        points = 2
        magic_xp = 43.0 * moves
        extras["maze_moves"] = moves
        if maze_count % 5 == 0:
            points += 8
            magic_xp += 1_000.0
            _grant_item(data, "Law rune", 10)
            extras["five_maze_bonus"] = True
    elif room_id == "alchemist":
        state["room_counts"]["alchemist_deposits"] += 1
        points = 1
        ordinary_cast_xp = (
            65.0
            if state["approach"] == "fast_rewards" and _magic_level(data) >= 55
            else 31.0
        )
        magic_xp = 200.0 + ordinary_cast_xp * MAGE_TRAINING_ARENA_ALCHEMY_CASTS_PER_POINT
        _grant_item(data, "Coins", 10)
        extras["banked_coins"] = 10
        extras["alchemy_casts"] = MAGE_TRAINING_ARENA_ALCHEMY_CASTS_PER_POINT
    elif room_id == "enchantment":
        state["room_counts"]["enchantment_shapes"] += 1
        shape_count = state["room_counts"]["enchantment_shapes"]
        spell = _enchantment_spell(data, state["approach"])
        enchant_level = int(spell[0])
        points = 1 + (enchant_level if shape_count % 10 == 0 else 0)
        magic_xp = float(spell[2]) * 0.75
        if shape_count % 20 == 0:
            rune = _reward_rune(MAGE_TRAINING_ARENA_ENCHANTMENT_REWARD_RUNES, rng)
            _grant_item(data, rune, 3)
            extras["rune_reward"] = {rune: 3}
        extras["enchantment_level"] = enchant_level
    else:
        state["room_counts"]["graveyard_deposits"] += 1
        values = (1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4)
        cursor = state["room_counts"]["graveyard_bone_cursor"]
        fruit = state["room_counts"]["graveyard_fruit_residual"]
        peaches = bool(state["completed"]) and _magic_level(data) >= 60
        fruit_eaten = 1 if falling_bone else 0
        target_fruit = 16 + fruit_eaten
        bones = 0
        while fruit < target_fruit:
            fruit += values[cursor % len(values)]
            cursor += 1
            bones += 1
        state["room_counts"]["graveyard_bone_cursor"] = cursor % len(values)
        state["room_counts"]["graveyard_fruit_residual"] = fruit - target_fruit
        points = 1
        magic_xp = 65.0 if peaches else 25.0
        if fruit_eaten:
            maximum = combat_max_lifepoints_pure(data)
            data["combat_lifepoints"] = min(
                maximum,
                _int(data.get("combat_lifepoints"), maximum) + (80 if peaches else 20),
            )
        rune = _reward_rune(MAGE_TRAINING_ARENA_GRAVEYARD_REWARD_RUNES, rng)
        _grant_item(data, rune)
        extras["fruit"] = "peaches" if peaches else "bananas"
        extras["fruit_eaten"] = fruit_eaten
        extras["bones_collected"] = bones
        extras["rune_reward"] = {rune: 1}

    awarded = _add_points(state, room_id, points)
    data["magic_exp"] = _float(data.get("magic_exp")) + magic_xp
    state["current_room"] = _selected_room(data, state)
    state["last_result"] = (
        f"{_ROOM_LABELS[room_id]} checkpoint · "
        f"+{awarded} {room_id} point{'s' if awarded != 1 else ''}"
        + (f" · +{magic_xp:g} Magic XP" if magic_xp else "")
    )
    data["mage_training_arena"] = state
    return data, True, {
        "advanced": True,
        "terminal": False,
        "checkpoint": True,
        "room": room_id,
        "points_gained": awarded,
        "magic_xp": magic_xp,
        "message": state["last_result"],
        **extras,
    }
