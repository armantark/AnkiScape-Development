"""Pure review-native Vinesweeper mechanics and direct reward commands."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..logic.pet_logic import store_active_pet_pure
from ..logic.summoning_logic import dismiss_familiar_pure
from ..data.vinesweeper_data import (
    COMPOST_POTION_DOSES,
    VINESWEEPER_FLAG_CAP,
    VINESWEEPER_FLAG_COIN_PRICE,
    VINESWEEPER_FLAG_POINT_PRICE,
    VINESWEEPER_FREE_FLAGS,
    VINESWEEPER_OGLEROOT_COIN_PRICE,
    VINESWEEPER_RABBIT_HUNTER_XP,
    VINESWEEPER_REWARDS,
    VINESWEEPER_REWARDS_BY_ID,
)


VINESWEEPER_STATE_VERSION = 1


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    if parsed != parsed or parsed in (float("inf"), float("-inf")):
        return default
    return parsed


def default_vinesweeper_state_pure() -> dict[str, Any]:
    return {
        "version": VINESWEEPER_STATE_VERSION,
        "active": False,
        "free_flags_claimed": False,
        "flags": 0,
        "points": 0,
        "ogleroots": 0,
        "operations": 0,
        "safe_uncover_count": 0,
        "correct_flag_count": 0,
        "mistake_count": 0,
        "rabbits_repulsed": 0,
        "last_result": "",
        "paused_reason": "",
    }


def sanitize_vinesweeper_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_vinesweeper_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    return {
        **defaults,
        "active": bool(source.get("active", False)),
        "free_flags_claimed": bool(source.get("free_flags_claimed", False)),
        "flags": min(VINESWEEPER_FLAG_CAP, _int(source.get("flags"))),
        "points": _int(source.get("points")),
        "ogleroots": min(28, _int(source.get("ogleroots"))),
        "operations": _int(source.get("operations")),
        "safe_uncover_count": _int(source.get("safe_uncover_count")),
        "correct_flag_count": _int(source.get("correct_flag_count")),
        "mistake_count": _int(source.get("mistake_count")),
        "rabbits_repulsed": _int(source.get("rabbits_repulsed")),
        "last_result": str(source.get("last_result", ""))[:360],
        "paused_reason": str(source.get("paused_reason", ""))[:160],
    }


def _inventory(data: Mapping[str, Any]) -> dict[str, int]:
    raw = data.get("inventory")
    if not isinstance(raw, Mapping):
        return {}
    return {str(name): _int(amount) for name, amount in raw.items()}


def apply_compost_potion_pure(
    inventory: Mapping[str, Any],
) -> tuple[dict[str, int], bool, dict[str, Any]]:
    updated = {
        str(name): _int(amount)
        for name, amount in inventory.items()
        if isinstance(name, str)
    }
    if updated.get("Compost", 0) <= 0:
        return updated, False, {"reason": "One bucket of Compost is required."}
    dose_index = next(
        (index for index, name in enumerate(COMPOST_POTION_DOSES) if updated.get(name, 0) > 0),
        None,
    )
    if dose_index is None:
        return updated, False, {"reason": "A Compost potion dose is required."}
    source = COMPOST_POTION_DOSES[dose_index]
    updated["Compost"] -= 1
    updated[source] -= 1
    updated["Supercompost"] = updated.get("Supercompost", 0) + 1
    if dose_index + 1 < len(COMPOST_POTION_DOSES):
        remainder = COMPOST_POTION_DOSES[dose_index + 1]
        updated[remainder] = updated.get(remainder, 0) + 1
    else:
        remainder = "Vial"
        updated[remainder] = updated.get(remainder, 0) + 1
    return updated, True, {
        "source_potion": source,
        "remainder": remainder,
        "outputs": {"Supercompost": 1, remainder: 1},
    }


def _has_spade(player_data: Mapping[str, Any]) -> bool:
    if _int(_inventory(player_data).get("Spade")) > 0:
        return True
    toolbelt = player_data.get("toolbelt")
    if not isinstance(toolbelt, Mapping):
        return False
    return any(
        "Spade" in values
        for values in toolbelt.values()
        if isinstance(values, (list, tuple, set))
    )


def _active_follower(player_data: Mapping[str, Any]) -> Mapping[str, Any]:
    summoning = player_data.get("summoning_state")
    if not isinstance(summoning, Mapping):
        return {}
    follower = summoning.get("active_follower")
    return follower if isinstance(follower, Mapping) else {}


def vinesweeper_xp_point_cost_pure(farming_level: Any) -> float:
    level = min(99, max(1, _int(farming_level, 1, minimum=1)))
    if level >= 40:
        return 1.0
    return 1.0 + (40 - level) * (6.75 / 39.0)


def vinesweeper_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_vinesweeper_state_pure(player_data.get("vinesweeper"))
    follower = _active_follower(player_data)
    level = min(99, max(1, _int(player_data.get("farming_level"), 1, minimum=1)))
    return {
        **state,
        "has_spade": _has_spade(player_data),
        "flag_cap": VINESWEEPER_FLAG_CAP,
        "follower_active": bool(follower),
        "follower_kind": str(follower.get("kind", "")),
        "can_enter": _has_spade(player_data),
        "farming_level": level,
        "xp_point_cost": vinesweeper_xp_point_cost_pure(level),
        "rewards": tuple(
            {
                "id": reward.id,
                "display_name": reward.display_name,
                "item_name": reward.item_name,
                "point_price": reward.point_price,
            }
            for reward in VINESWEEPER_REWARDS
        ),
    }


def _replace_flag(data: dict[str, Any], state: dict[str, Any]) -> str:
    if state["flags"] > 0:
        return ""
    inventory = _inventory(data)
    coins = _int(inventory.get("Coins"))
    if coins >= VINESWEEPER_FLAG_COIN_PRICE:
        inventory["Coins"] = coins - VINESWEEPER_FLAG_COIN_PRICE
        data["inventory"] = inventory
        state["flags"] = 1
        return "500 coins"
    if state["points"] >= VINESWEEPER_FLAG_POINT_PRICE:
        state["points"] -= VINESWEEPER_FLAG_POINT_PRICE
        state["flags"] = 1
        return "50 points"
    state["active"] = False
    state["paused_reason"] = "No flag and neither 500 coins nor 50 points is available."
    return "paused"


def _flag_reward(farming_level: int, roll: float, segment_start: float, segment_size: float) -> int:
    position = max(0.0, min(0.999999, (roll - segment_start) / segment_size))
    band = min(4, int(position * 5))
    return min(325, 100 + farming_level * 2 + band * 25)


def apply_vinesweeper_review_pure(
    player_data: Mapping[str, Any],
    rolls: Sequence[float],
    *,
    operations: int = 1,
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: the board state is rebuilt by the module sanitizer
    # before any flag is replaced, and the follower alias is only read.
    data = dict(player_data)
    state = sanitize_vinesweeper_state_pure(data.get("vinesweeper"))
    data["vinesweeper"] = state
    if not state["active"]:
        return data, {"allowed": False, "reason": "Enter Vinesweeper before training it."}

    maximum = max(1, _int(operations, 1, minimum=1))
    clean_rolls = [max(0.0, min(0.999999, _float(value))) for value in rolls]
    farming_level = min(99, max(1, _int(data.get("farming_level"), 1, minimum=1)))
    point_delta = 0
    flag_delta = 0
    coin_delta = 0
    hunter_xp = 0.0
    completed = 0
    outcomes: list[str] = []
    payments: list[str] = []

    for index in range(min(maximum, len(clean_rolls))):
        roll = clean_rolls[index]
        requires_flag = roll >= 0.45
        if requires_flag and state["flags"] <= 0:
            coins_before = _int(_inventory(data).get("Coins"))
            points_before = state["points"]
            payment = _replace_flag(data, state)
            if payment == "paused":
                outcomes.append("paused: no replacement flag")
                break
            payments.append(payment)
            coin_delta += _int(_inventory(data).get("Coins")) - coins_before
            point_delta += state["points"] - points_before
            flag_delta += 1

        if roll < 0.45:
            state["points"] += 1
            point_delta += 1
            state["safe_uncover_count"] += 1
            if roll < 0.05:
                state["ogleroots"] = min(28, state["ogleroots"] + 1)
                outcomes.append("uncovered safe ground (+1 point) and found an Ogleroot")
            else:
                outcomes.append("uncovered safe ground (+1 point)")
        elif roll < 0.80:
            award = _flag_reward(farming_level, roll, 0.45, 0.35)
            state["points"] += award
            point_delta += award
            state["correct_flag_count"] += 1
            outcomes.append(f"correctly flagged a seed (+{award} points)")
        elif roll < 0.90:
            loss = min(10, state["points"])
            state["points"] -= loss
            point_delta -= loss
            state["mistake_count"] += 1
            outcomes.append(f"dug up a seed (-{loss} points)")
        elif roll < 0.95:
            state["flags"] -= 1
            flag_delta -= 1
            state["mistake_count"] += 1
            outcomes.append("placed a mistaken flag (-1 flag)")
        else:
            inventory = _inventory(data)
            if state["ogleroots"] > 0:
                state["ogleroots"] -= 1
                root_source = "stored Ogleroot"
            elif _int(inventory.get("Coins")) >= VINESWEEPER_OGLEROOT_COIN_PRICE:
                inventory["Coins"] -= VINESWEEPER_OGLEROOT_COIN_PRICE
                data["inventory"] = inventory
                coin_delta -= VINESWEEPER_OGLEROOT_COIN_PRICE
                root_source = "10-coin Ogleroot"
            else:
                state["flags"] -= 1
                flag_delta -= 1
                state["mistake_count"] += 1
                outcomes.append("a rabbit reached the seed (-1 flag, no points)")
                state["operations"] += 1
                completed += 1
                continue
            award = _flag_reward(farming_level, roll, 0.95, 0.05)
            state["points"] += award
            point_delta += award
            hunter_xp += VINESWEEPER_RABBIT_HUNTER_XP
            state["rabbits_repulsed"] += 1
            outcomes.append(
                f"repelled a rabbit with a {root_source} (+{award} points, +30 Hunter XP)"
            )

        state["operations"] += 1
        completed += 1

    state["paused_reason"] = "" if state["active"] else state["paused_reason"]
    status = "; ".join(outcomes) if outcomes else "Vinesweeper made no operation."
    if payments:
        status += " · replacement flag: " + ", ".join(payments)
    state["last_result"] = status[:360]
    data["vinesweeper"] = state
    return data, {
        "allowed": True,
        "completed_operations": completed,
        "outcomes": tuple(outcomes),
        "point_delta": point_delta,
        "flag_delta": flag_delta,
        "coin_delta": coin_delta,
        "hunter_xp": hunter_xp,
        "paused": not state["active"],
        "status": state["last_result"],
    }


def _dismiss_follower_for_entry(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, str]:
    follower = _active_follower(player_data)
    kind = str(follower.get("kind", ""))
    if not kind:
        # Shallow on purpose: nothing was dismissed, and the entry path that
        # continues from here only writes top-level keys.
        return dict(player_data), True, ""
    if kind == "familiar":
        updated, ok, _info = dismiss_familiar_pure(player_data)
        return updated, ok, "familiar"
    if kind == "pet":
        updated, ok = store_active_pet_pure(player_data, location="bank")
        return updated, ok, "pet"
    # Shallow on purpose: this is the failure return, and its only caller
    # discards the save it gets back.
    return dict(player_data), False, kind


def apply_vinesweeper_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the board state is rebuilt by the module sanitizer
    # before any flag is replaced, and the follower alias is only read.
    data = dict(player_data)
    state = sanitize_vinesweeper_state_pure(data.get("vinesweeper"))
    data["vinesweeper"] = state
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "enter":
        if not _has_spade(data):
            return data, False, {"reason": "A spade or tool-belt spade is required."}
        follower = _active_follower(data)
        if follower and not bool(payload.get("confirm_dismiss_follower", False)):
            return data, False, {
                "reason": "Your active follower must be dismissed before entering.",
                "requires_confirmation": True,
                "follower_kind": str(follower.get("kind", "follower")),
            }
        dismissed_kind = ""
        if follower:
            data, ok, dismissed_kind = _dismiss_follower_for_entry(data)
            if not ok:
                # Shallow on purpose: the un-dismissed original is returned
                # unchanged, and every caller discards it when ok is False.
                return dict(player_data), False, {
                    "reason": "The active follower could not be dismissed safely."
                }
            state = sanitize_vinesweeper_state_pure(data.get("vinesweeper"))
        if not state["free_flags_claimed"]:
            state["free_flags_claimed"] = True
            state["flags"] = VINESWEEPER_FREE_FLAGS
        state["active"] = True
        state["paused_reason"] = ""
        state["last_result"] = "Entered Winkin's Farm. The next successful review resolves one operation."
        data["vinesweeper"] = state
        return data, True, {
            "message": state["last_result"],
            "dismissed_follower_kind": dismissed_kind,
            "flags": state["flags"],
        }

    if action_id == "leave":
        refund = state["ogleroots"] * VINESWEEPER_OGLEROOT_COIN_PRICE
        if refund:
            inventory = _inventory(data)
            inventory["Coins"] = _int(inventory.get("Coins")) + refund
            data["inventory"] = inventory
        state["ogleroots"] = 0
        state["active"] = False
        state["paused_reason"] = ""
        state["last_result"] = (
            f"Left Winkin's Farm · refunded {refund} coins for excess Ogleroots."
            if refund
            else "Left Winkin's Farm."
        )
        data["vinesweeper"] = state
        return data, True, {"message": state["last_result"], "coin_refund": refund}

    if action_id == "buy_reward":
        reward = VINESWEEPER_REWARDS_BY_ID.get(str(payload.get("reward_id", "")))
        quantity = max(1, _int(payload.get("quantity"), 1, minimum=1))
        if reward is None:
            return data, False, {"reason": "Choose a Vinesweeper reward."}
        if reward.id == "flag":
            quantity = min(quantity, VINESWEEPER_FLAG_CAP - state["flags"])
            if quantity <= 0:
                return data, False, {"reason": "You already hold the maximum of 10 flags."}
        cost = reward.point_price * quantity
        if state["points"] < cost:
            return data, False, {"reason": f"That purchase costs {cost:,} Vinesweeper points."}
        state["points"] -= cost
        if reward.id == "flag":
            state["flags"] += quantity
        else:
            inventory = _inventory(data)
            inventory[reward.item_name] = _int(inventory.get(reward.item_name)) + quantity
            data["inventory"] = inventory
        state["last_result"] = (
            f"Bought {quantity} × {reward.display_name} for {cost:,} Vinesweeper points."
        )
        data["vinesweeper"] = state
        return data, True, {
            "message": state["last_result"],
            "reward_id": reward.id,
            "item_name": reward.item_name,
            "quantity": quantity,
            "points_spent": cost,
        }

    if action_id == "redeem_farming_xp":
        points = min(state["points"], max(1, _int(payload.get("points"), state["points"], minimum=1)))
        if points <= 0:
            return data, False, {"reason": "You have no Vinesweeper points to redeem."}
        level = min(99, max(1, _int(data.get("farming_level"), 1, minimum=1)))
        point_cost = vinesweeper_xp_point_cost_pure(level)
        xp = points / point_cost
        data["farming_exp"] = _float(data.get("farming_exp")) + xp
        state["points"] -= points
        xp_display = f"{xp:,.0f}" if xp.is_integer() else f"{xp:,.1f}"
        state["last_result"] = (
            f"Redeemed {points:,} Vinesweeper points for {xp_display} Farming XP."
        )
        data["vinesweeper"] = state
        return data, True, {
            "message": state["last_result"],
            "points_spent": points,
            "farming_xp": xp,
            "point_cost": point_cost,
        }

    return data, False, {"reason": "Unknown Vinesweeper command."}
