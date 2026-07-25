"""Pure review-native Warriors' Guild transactions."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any, Callable

try:
    from .warriors_guild_data import (
        ANIMATED_ARMOUR_LOSS_CHANCE,
        ANIMATED_ARMOUR_TIERS,
        DEFENDER_TIERS,
        KEG_REVIEW_SUCCESS_CHANCE,
        MULTI_DAMAGE_MULTIPLIER,
        MULTI_CYCLOSSUS_CHANCE,
        MULTI_DEFENDER_CHANCE,
        MULTI_TOKEN_DRAIN_PER_100_TICKS,
        MULTI_TOKEN_ENTRY_COST,
        SINGLE_DEFENDER_CHANCE,
        SINGLE_CYCLOSSUS_CHANCE,
        SINGLE_TOKEN_DRAIN_PER_100_TICKS,
        SINGLE_TOKEN_ENTRY_COST,
        WARRIORS_GUILD_ACTIVITIES,
        WARRIORS_GUILD_ACTIVITY_IDS,
        WARRIORS_GUILD_TOKEN_KEYS,
    )
except ImportError:  # pragma: no cover - flat import path used by tests
    from warriors_guild_data import (  # type: ignore
        ANIMATED_ARMOUR_LOSS_CHANCE,
        ANIMATED_ARMOUR_TIERS,
        DEFENDER_TIERS,
        KEG_REVIEW_SUCCESS_CHANCE,
        MULTI_DAMAGE_MULTIPLIER,
        MULTI_CYCLOSSUS_CHANCE,
        MULTI_DEFENDER_CHANCE,
        MULTI_TOKEN_DRAIN_PER_100_TICKS,
        MULTI_TOKEN_ENTRY_COST,
        SINGLE_DEFENDER_CHANCE,
        SINGLE_CYCLOSSUS_CHANCE,
        SINGLE_TOKEN_DRAIN_PER_100_TICKS,
        SINGLE_TOKEN_ENTRY_COST,
        WARRIORS_GUILD_ACTIVITIES,
        WARRIORS_GUILD_ACTIVITY_IDS,
        WARRIORS_GUILD_TOKEN_KEYS,
    )


def _int(value: Any, default: int = 0, *, low: int = 0, high: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return max(low, min(parsed, high))


def _roll(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    if not math.isfinite(parsed):
        return 0.0
    return max(0.0, min(parsed, 0.999999999))


def default_warriors_guild_state_pure() -> dict[str, Any]:
    return {
        "tokens": {key: 0 for key in WARRIORS_GUILD_TOKEN_KEYS},
        "automation_mode": "casual",
        "payment_mode": "multi",
        "single_token": "attack",
        "in_cyclops_room": False,
        "cyclossus_pending": False,
        "token_drain_residual": 0,
        "shown_defender_index": -1,
        "activity_reviews": {activity_id: 0 for activity_id in WARRIORS_GUILD_ACTIVITY_IDS},
        "cyclops_kills": 0,
        "cyclossus_kills": 0,
        "defender_drops": 0,
    }


def sanitize_warriors_guild_state_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    defaults = default_warriors_guild_state_pure()
    raw_tokens = source.get("tokens")
    raw_tokens = raw_tokens if isinstance(raw_tokens, Mapping) else {}
    raw_reviews = source.get("activity_reviews")
    raw_reviews = raw_reviews if isinstance(raw_reviews, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    payment_mode = str(source.get("payment_mode", "multi"))
    single_token = str(source.get("single_token", "attack"))
    return {
        "tokens": {
            key: _int(raw_tokens.get(key), high=65535)
            for key in WARRIORS_GUILD_TOKEN_KEYS
        },
        "automation_mode": mode if mode in {"casual", "advanced"} else "casual",
        "payment_mode": payment_mode if payment_mode in {"single", "multi"} else "multi",
        "single_token": single_token if single_token in WARRIORS_GUILD_TOKEN_KEYS else "attack",
        "in_cyclops_room": bool(source.get("in_cyclops_room", False)),
        "cyclossus_pending": bool(source.get("cyclossus_pending", False)),
        "token_drain_residual": _int(source.get("token_drain_residual"), high=99),
        "shown_defender_index": _int(
            source.get("shown_defender_index", -1),
            default=-1,
            low=-1,
            high=len(DEFENDER_TIERS) - 2,
        ),
        "activity_reviews": {
            activity_id: _int(raw_reviews.get(activity_id))
            for activity_id in WARRIORS_GUILD_ACTIVITY_IDS
        },
        "cyclops_kills": _int(source.get("cyclops_kills")),
        "cyclossus_kills": _int(source.get("cyclossus_kills")),
        "defender_drops": _int(source.get("defender_drops")),
    }


def warriors_guild_entry_locked_reasons_pure(player_data: Mapping[str, Any]) -> tuple[str, ...]:
    attack = _int(player_data.get("attack_level"), default=1, low=1, high=99)
    strength = _int(player_data.get("strength_level"), default=1, low=1, high=99)
    if attack >= 99 or strength >= 99 or attack + strength >= 130:
        return ()
    return ("Attack + Strength 130, or 99 in either skill",)


def _highest_complete_armour(
    inventory: Mapping[str, Any],
) -> tuple[int, Mapping[str, Any]] | None:
    for index in range(len(ANIMATED_ARMOUR_TIERS) - 1, -1, -1):
        tier = ANIMATED_ARMOUR_TIERS[index]
        if all(_int(inventory.get(item_name)) >= 1 for item_name in tier["items"]):
            return index, tier
    return None


def warriors_guild_activity_locked_reasons_pure(
    player_data: Mapping[str, Any],
    activity_id: str,
) -> tuple[str, ...]:
    if activity_id not in WARRIORS_GUILD_ACTIVITIES:
        return ("unknown activity",)
    reasons = list(warriors_guild_entry_locked_reasons_pure(player_data))
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    equipment = player_data.get("equipment")
    equipment = equipment if isinstance(equipment, Mapping) else {}
    if activity_id == "warriors_guild_animated_armour" and _highest_complete_armour(inventory) is None:
        reasons.append("a matching full helm, platebody, and platelegs set")
    if activity_id == "warriors_guild_shot_put":
        occupied = tuple(slot for slot in ("weapon", "shield", "hands") if equipment.get(slot))
        if occupied:
            reasons.append("empty weapon, shield, and hands slots")
    if activity_id == "warriors_guild_keg_balance":
        occupied = tuple(slot for slot in ("head", "weapon", "shield", "hands") if equipment.get(slot))
        if occupied:
            reasons.append("empty head, weapon, shield, and hands slots")
    return tuple(dict.fromkeys(reasons))


def _casual_activity_id(player_data: Mapping[str, Any], state: Mapping[str, Any]) -> str | None:
    available = tuple(
        activity_id
        for activity_id in WARRIORS_GUILD_ACTIVITY_IDS
        if not warriors_guild_activity_locked_reasons_pure(player_data, activity_id)
    )
    if not available:
        return None
    tokens = state["tokens"]
    if len(available) == len(WARRIORS_GUILD_ACTIVITY_IDS):
        return min(
            available,
            key=lambda activity_id: (
                _int(tokens.get(WARRIORS_GUILD_ACTIVITIES[activity_id]["token_key"])),
                WARRIORS_GUILD_ACTIVITY_IDS.index(activity_id),
            ),
        )
    # If the five-way route is unavailable, Casual pursues the fastest viable
    # single-token balance. Values are the maximum tokens from one review.
    speed = {
        "warriors_guild_animated_armour": 80,
        "warriors_guild_attack_dummy": 5,
        "warriors_guild_catapult": 4,
        "warriors_guild_shot_put": 17,
        "warriors_guild_keg_balance": 10,
    }
    return max(available, key=lambda activity_id: (speed[activity_id], -WARRIORS_GUILD_ACTIVITY_IDS.index(activity_id)))


def warriors_guild_selected_activity_pure(
    player_data: Mapping[str, Any],
    requested_activity_id: str,
) -> str | None:
    state = sanitize_warriors_guild_state_pure(player_data.get("warriors_guild"))
    if state["automation_mode"] == "advanced":
        return requested_activity_id if requested_activity_id in WARRIORS_GUILD_ACTIVITIES else None
    return _casual_activity_id(player_data, state)


def _combat_xp_for_animated_armour(player_data: Mapping[str, Any], lifepoints: int) -> dict[str, float]:
    style = str(player_data.get("combat_attack_style", "accurate"))
    rewards: dict[str, float] = {"constitution_exp": lifepoints * 0.133}
    if style == "aggressive":
        rewards["strength_exp"] = lifepoints * 0.4
    elif style == "defensive":
        rewards["defense_exp"] = lifepoints * 0.4
    elif style == "controlled":
        for key in ("attack_exp", "strength_exp", "defense_exp"):
            rewards[key] = lifepoints * 0.133
    elif style.startswith("ranged"):
        rewards["ranged_exp"] = lifepoints * 0.4
    elif style.startswith("magic"):
        rewards["magic_exp"] = lifepoints * 0.2
    else:
        rewards["attack_exp"] = lifepoints * 0.4
    return rewards


def _shot_put_result(player_data: Mapping[str, Any], success_roll: float) -> dict[str, Any]:
    strength = _int(player_data.get("strength_level"), default=1, low=1, high=99)
    # The live add-on has review-trip cost rather than a mutable energy bar.
    # Use a full-energy room attempt and preserve the period post-2011 no-drain rule.
    score = strength + 100 + 30 - 22
    thresholds = (58, 71, 84, 97, 110, 124, 137, 150, 163, 176, 190, 203, 216)
    distance = next((index + 1 for index, threshold in enumerate(thresholds) if score < threshold), 14)
    success = _roll(success_roll) < min(1.0, score / 250.0)
    return {
        "success": success,
        "distance": distance,
        "token_gain": 3 + distance if success else 0,
        "xp_rewards": {"strength_exp": float(distance)} if success else {},
        "damage": 0 if success else 10,
    }


def apply_warriors_guild_activity_pure(
    player_data: Mapping[str, Any],
    requested_activity_id: str,
    rolls: tuple[float, ...] = (),
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_warriors_guild_state_pure returns a fresh
    # state including its tokens map, and inventory is rebuilt with dict()
    # before any write.
    data = dict(player_data)
    state = sanitize_warriors_guild_state_pure(data.get("warriors_guild"))
    activity_id = warriors_guild_selected_activity_pure(data, requested_activity_id)
    if activity_id is None:
        return data, False, {"reason": "no available Warriors' Guild activity"}
    locked = warriors_guild_activity_locked_reasons_pure(data, activity_id)
    if locked:
        return data, False, {"reason": ", ".join(locked), "activity_id": activity_id}

    activity = WARRIORS_GUILD_ACTIVITIES[activity_id]
    token_key = str(activity["token_key"])
    result: dict[str, Any] = {
        "activity_id": activity_id,
        "display_name": activity["display_name"],
        "token_key": token_key,
        "token_gain": 0,
        "xp_rewards": {},
        "damage": 0,
        "success": True,
    }
    first_roll = _roll(rolls[0] if rolls else 0.5)
    second_roll = _roll(rolls[1] if len(rolls) > 1 else 0.5)

    if activity_id == "warriors_guild_animated_armour":
        inventory = data.get("inventory")
        inventory = dict(inventory) if isinstance(inventory, Mapping) else {}
        _index, tier = _highest_complete_armour(inventory) or (0, ANIMATED_ARMOUR_TIERS[0])
        result["token_gain"] = int(tier["tokens"])
        result["armour_tier"] = str(tier["name"])
        result["xp_rewards"] = _combat_xp_for_animated_armour(data, int(tier["lifepoints"]))
        if first_roll < ANIMATED_ARMOUR_LOSS_CHANCE:
            items = tuple(tier["items"])
            lost_item = items[min(int(second_roll * len(items)), len(items) - 1)]
            inventory[lost_item] = max(0, _int(inventory.get(lost_item)) - 1)
            data["inventory"] = inventory
            result["lost_item"] = lost_item
    elif activity_id == "warriors_guild_attack_dummy":
        result["token_gain"] = 5
        result["xp_rewards"] = {"attack_exp": 15.0}
    elif activity_id == "warriors_guild_catapult":
        result["token_gain"] = 4
        result["xp_rewards"] = {"defense_exp": 10.0}
    elif activity_id == "warriors_guild_shot_put":
        result.update(_shot_put_result(data, first_roll))
    else:
        success = first_roll < KEG_REVIEW_SUCCESS_CHANCE
        result.update(
            {
                "success": success,
                "token_gain": 10 if success else 0,
                "xp_rewards": {"strength_exp": 6.0} if success else {},
                "damage": 0 if success else 20 + min(int(second_roll * 21), 20),
            }
        )

    if result["success"]:
        state["tokens"][token_key] = min(
            65535,
            _int(state["tokens"].get(token_key)) + _int(result["token_gain"]),
        )
    state["activity_reviews"][activity_id] = _int(state["activity_reviews"].get(activity_id)) + 1
    data["warriors_guild"] = state
    return data, True, result


def _all_activities_available(player_data: Mapping[str, Any]) -> bool:
    return all(
        not warriors_guild_activity_locked_reasons_pure(player_data, activity_id)
        for activity_id in WARRIORS_GUILD_ACTIVITY_IDS
    )


def _derived_casual_payment(player_data: Mapping[str, Any], state: Mapping[str, Any]) -> tuple[str, str]:
    if _all_activities_available(player_data):
        return "multi", str(state["single_token"])
    best_token = max(
        WARRIORS_GUILD_TOKEN_KEYS,
        key=lambda token: (_int(state["tokens"].get(token)), -WARRIORS_GUILD_TOKEN_KEYS.index(token)),
    )
    return "single", best_token


def enter_warriors_guild_cyclops_room_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_warriors_guild_state_pure returns a fresh
    # state including its tokens map, and inventory is rebuilt with dict()
    # before any write.
    data = dict(player_data)
    entry_locked = warriors_guild_entry_locked_reasons_pure(data)
    if entry_locked:
        return data, False, {"reason": entry_locked[0]}
    state = sanitize_warriors_guild_state_pure(data.get("warriors_guild"))
    payment_mode = str(state["payment_mode"])
    single_token = str(state["single_token"])
    if state["automation_mode"] == "casual":
        payment_mode, single_token = _derived_casual_payment(data, state)
    if payment_mode == "multi":
        missing = tuple(
            token
            for token in WARRIORS_GUILD_TOKEN_KEYS
            if _int(state["tokens"].get(token)) < MULTI_TOKEN_ENTRY_COST
        )
        if missing:
            return data, False, {
                "reason": "Need 30 of every Warriors' Guild token",
                "missing_tokens": missing,
            }
    elif _int(state["tokens"].get(single_token)) < SINGLE_TOKEN_ENTRY_COST:
        return data, False, {
            "reason": f"Need 200 {single_token} tokens",
            "missing_tokens": (single_token,),
        }
    state["payment_mode"] = payment_mode
    state["single_token"] = single_token
    state["in_cyclops_room"] = True
    state["cyclossus_pending"] = False
    state["token_drain_residual"] = 0
    data["warriors_guild"] = state
    return data, True, {
        "payment_mode": payment_mode,
        "single_token": single_token,
        "message": (
            "Entered using all five token balances"
            if payment_mode == "multi"
            else f"Entered using {single_token} tokens"
        ),
    }


def leave_warriors_guild_cyclops_room_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_warriors_guild_state_pure returns a fresh
    # state including its tokens map, and inventory is rebuilt with dict()
    # before any write.
    data = dict(player_data)
    state = sanitize_warriors_guild_state_pure(data.get("warriors_guild"))
    if not state["in_cyclops_room"]:
        return data, False, {"reason": "Not in the Cyclops room"}
    state["in_cyclops_room"] = False
    state["cyclossus_pending"] = False
    state["token_drain_residual"] = 0
    data["warriors_guild"] = state
    return data, True, {"message": "Left the Cyclops room"}


def set_warriors_guild_policy_pure(
    player_data: Mapping[str, Any],
    *,
    automation_mode: str | None = None,
    payment_mode: str | None = None,
    single_token: str | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_warriors_guild_state_pure returns a fresh
    # state including its tokens map, and inventory is rebuilt with dict()
    # before any write.
    data = dict(player_data)
    state = sanitize_warriors_guild_state_pure(data.get("warriors_guild"))
    if automation_mode is not None:
        if automation_mode not in {"casual", "advanced"}:
            return data, False, {"reason": "Unknown automation mode"}
        state["automation_mode"] = automation_mode
    if payment_mode is not None:
        if payment_mode not in {"single", "multi"}:
            return data, False, {"reason": "Unknown payment mode"}
        state["payment_mode"] = payment_mode
    if single_token is not None:
        if single_token not in WARRIORS_GUILD_TOKEN_KEYS:
            return data, False, {"reason": "Unknown token balance"}
        state["single_token"] = single_token
    data["warriors_guild"] = state
    return data, True, {"state": state}


def warriors_guild_cyclops_locked_reasons_pure(
    player_data: Mapping[str, Any],
    target_id: str = "cyclops",
) -> tuple[str, ...]:
    entry_locked = warriors_guild_entry_locked_reasons_pure(player_data)
    if entry_locked:
        return entry_locked
    state = sanitize_warriors_guild_state_pure(player_data.get("warriors_guild"))
    if not state["in_cyclops_room"]:
        return ("Enter the Warriors' Guild Cyclops room",)
    if state["payment_mode"] == "multi":
        if any(_int(state["tokens"].get(token)) <= 0 for token in WARRIORS_GUILD_TOKEN_KEYS):
            return ("Warriors' Guild tokens depleted",)
    elif _int(state["tokens"].get(state["single_token"])) <= 0:
        return ("Warriors' Guild tokens depleted",)
    if target_id == "cyclossus":
        if not state["cyclossus_pending"]:
            return ("Wait for a Cyclossus to appear",)
        equipment = player_data.get("equipment")
        equipment = equipment if isinstance(equipment, Mapping) else {}
        if equipment.get("shield") not in {"Rune defender", "Dragon defender"}:
            return ("Equip a Rune or Dragon defender",)
    elif state["cyclossus_pending"]:
        return ("Defeat the spawned Cyclossus first",)
    return ()


def warriors_guild_cyclops_damage_multiplier_pure(
    player_data: Mapping[str, Any],
) -> float:
    state = sanitize_warriors_guild_state_pure(player_data.get("warriors_guild"))
    return (
        MULTI_DAMAGE_MULTIPLIER
        if state["in_cyclops_room"] and state["payment_mode"] == "multi"
        else 1.0
    )


def consume_warriors_guild_cyclops_tokens_pure(
    player_data: Mapping[str, Any],
    ticks_elapsed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: sanitize_warriors_guild_state_pure returns a fresh
    # state including its tokens map, and inventory is rebuilt with dict()
    # before any write.
    data = dict(player_data)
    state = sanitize_warriors_guild_state_pure(data.get("warriors_guild"))
    ticks = _int(ticks_elapsed)
    if not state["in_cyclops_room"] or ticks <= 0:
        data["warriors_guild"] = state
        return data, {"drained": {}, "ejected": False}
    rate = (
        MULTI_TOKEN_DRAIN_PER_100_TICKS
        if state["payment_mode"] == "multi"
        else SINGLE_TOKEN_DRAIN_PER_100_TICKS
    )
    numerator = state["token_drain_residual"] + ticks * rate
    cost, state["token_drain_residual"] = divmod(numerator, 100)
    drained: dict[str, int] = {}
    if cost > 0:
        keys = WARRIORS_GUILD_TOKEN_KEYS if state["payment_mode"] == "multi" else (state["single_token"],)
        for key in keys:
            before = _int(state["tokens"].get(key))
            after = max(0, before - cost)
            state["tokens"][key] = after
            drained[key] = before - after
    ejected = (
        any(_int(state["tokens"].get(key)) <= 0 for key in WARRIORS_GUILD_TOKEN_KEYS)
        if state["payment_mode"] == "multi"
        else _int(state["tokens"].get(state["single_token"])) <= 0
    )
    if ejected:
        state["in_cyclops_room"] = False
        state["cyclossus_pending"] = False
        state["token_drain_residual"] = 0
    data["warriors_guild"] = state
    return data, {"drained": drained, "ejected": ejected}


def _owned_defender_indices(player_data: Mapping[str, Any]) -> tuple[int, ...]:
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    equipment = player_data.get("equipment")
    equipment = equipment if isinstance(equipment, Mapping) else {}
    equipped = set(equipment.values())
    return tuple(
        index
        for index, tier in enumerate(DEFENDER_TIERS)
        if _int(inventory.get(tier["name"])) > 0 or tier["name"] in equipped
    )


def next_warriors_guild_defender_index_pure(player_data: Mapping[str, Any]) -> int:
    state = sanitize_warriors_guild_state_pure(player_data.get("warriors_guild"))
    owned = _owned_defender_indices(player_data)
    best_owned = max(owned, default=-1)
    return max(0, min(len(DEFENDER_TIERS) - 1, state["shown_defender_index"] + 1, best_owned + 1))


def apply_warriors_guild_cyclops_kills_pure(
    player_data: Mapping[str, Any],
    kills: int,
    rng: Callable[[], float],
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: sanitize_warriors_guild_state_pure returns a fresh
    # state including its tokens map, and inventory is rebuilt with dict()
    # before any write.
    data = dict(player_data)
    state = sanitize_warriors_guild_state_pure(data.get("warriors_guild"))
    count = _int(kills)
    state["cyclops_kills"] += count
    chance = MULTI_DEFENDER_CHANCE if state["payment_mode"] == "multi" else SINGLE_DEFENDER_CHANCE
    cyclossus_chance = (
        MULTI_CYCLOSSUS_CHANCE
        if state["payment_mode"] == "multi"
        else SINGLE_CYCLOSSUS_CHANCE
    )
    drops: dict[str, int] = {}
    cyclossus_spawned = False
    inventory = data.get("inventory")
    inventory = dict(inventory) if isinstance(inventory, Mapping) else {}
    for _ in range(count):
        if _roll(rng()) < chance:
            defender = DEFENDER_TIERS[
                next_warriors_guild_defender_index_pure(
                    {**data, "inventory": inventory}
                )
            ]["name"]
            inventory[defender] = _int(inventory.get(defender)) + 1
            drops[defender] = drops.get(defender, 0) + 1
            state["defender_drops"] += 1
        if (
            state["in_cyclops_room"]
            and state["shown_defender_index"] >= 6
            and not state["cyclossus_pending"]
            and _roll(rng()) < cyclossus_chance
        ):
            state["cyclossus_pending"] = True
            cyclossus_spawned = True
    data["inventory"] = inventory
    data["warriors_guild"] = state
    return data, {
        "drops": drops,
        "chance": chance,
        "cyclossus_spawned": cyclossus_spawned,
        "cyclossus_chance": cyclossus_chance,
    }


def apply_warriors_guild_cyclossus_kills_pure(
    player_data: Mapping[str, Any],
    kills: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: sanitize_warriors_guild_state_pure returns a fresh
    # state including its tokens map, and inventory is rebuilt with dict()
    # before any write.
    data = dict(player_data)
    state = sanitize_warriors_guild_state_pure(data.get("warriors_guild"))
    count = _int(kills)
    if count > 0:
        state["cyclossus_kills"] += count
        state["cyclossus_pending"] = False
    data["warriors_guild"] = state
    return data, {"kills": count, "cleared": count > 0}


def show_warriors_guild_defender_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_warriors_guild_state_pure returns a fresh
    # state including its tokens map, and inventory is rebuilt with dict()
    # before any write.
    data = dict(player_data)
    state = sanitize_warriors_guild_state_pure(data.get("warriors_guild"))
    next_index = state["shown_defender_index"] + 1
    if next_index >= len(DEFENDER_TIERS) - 1:
        return data, False, {"reason": "Rune defender has already been shown"}
    defender = DEFENDER_TIERS[next_index]["name"]
    if next_index not in _owned_defender_indices(data):
        return data, False, {"reason": f"Obtain a {defender} first"}
    state["shown_defender_index"] = next_index
    data["warriors_guild"] = state
    return data, True, {
        "shown": defender,
        "next_defender": DEFENDER_TIERS[next_index + 1]["name"],
        "message": f"Kamfreena will now release Cyclopes that can drop {DEFENDER_TIERS[next_index + 1]['name']}.",
    }


def warriors_guild_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_warriors_guild_state_pure(player_data.get("warriors_guild"))
    next_index = next_warriors_guild_defender_index_pure(player_data)
    next_show = state["shown_defender_index"] + 1
    room_ready = True
    room_entry_reason = ""
    if not state["in_cyclops_room"]:
        _preview, room_ready, room_info = enter_warriors_guild_cyclops_room_pure(
            player_data
        )
        if not room_ready:
            room_entry_reason = str(room_info.get("reason", "") or "")
    return {
        **state,
        "entry_locked_reasons": warriors_guild_entry_locked_reasons_pure(player_data),
        "room_ready": room_ready,
        "room_entry_reason": room_entry_reason,
        "next_defender": DEFENDER_TIERS[next_index]["name"],
        "showable_defender": (
            DEFENDER_TIERS[next_show]["name"]
            if 0 <= next_show < len(DEFENDER_TIERS) - 1 and next_show in _owned_defender_indices(player_data)
            else ""
        ),
    }
