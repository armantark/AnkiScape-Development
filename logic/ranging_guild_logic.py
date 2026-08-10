"""Pure ten-shot Ranging Guild competition and ticket exchange mechanics."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..data.combat_data import COMBAT_RANGED_WEAPON_DATA
from ..data.equipment_data import EQUIPMENT_DATA
from ..data.ranging_guild_data import (
    RANGING_GUILD_ACTIVITY_ID,
    RANGING_GUILD_BANDS_BY_ID,
    RANGING_GUILD_ENTRY_ARROWS,
    RANGING_GUILD_ENTRY_COINS,
    RANGING_GUILD_ENTRY_LEVEL,
    RANGING_GUILD_QUALITY_THRESHOLDS,
    RANGING_GUILD_REWARDS,
    RANGING_GUILD_REWARDS_BY_ID,
    RANGING_GUILD_SHOTS,
    RANGING_GUILD_TICKET_ITEM,
)
from ..logic_pure.logic_pure import (
    combat_attack_style_for_equipment_pure,
    equipment_stat_totals_pure,
)


RANGING_GUILD_STATE_VERSION = 1


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _unit(value: Any) -> float:
    try:
        return max(0.0, min(0.999999999999, float(value)))
    except (TypeError, ValueError, OverflowError):
        return 0.0


def _float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    return parsed if parsed >= 0.0 and parsed == parsed and parsed != float("inf") else 0.0


def _inventory(data: Mapping[str, Any]) -> Mapping[str, Any]:
    value = data.get("inventory")
    return value if isinstance(value, Mapping) else {}


def _mutable_inventory(data: dict[str, Any]) -> dict[str, Any]:
    inventory = data.get("inventory")
    if not isinstance(inventory, dict):
        inventory = {}
        data["inventory"] = inventory
    return inventory


def _effective_ranged_level(data: Mapping[str, Any]) -> int:
    base = max(1, _int(data.get("ranged_level"), 1, maximum=120))
    current = data.get("combat_current_levels")
    if not isinstance(current, Mapping) or "ranged" not in current:
        return base
    return max(1, _int(current.get("ranged"), base, maximum=120))


def _equipment(data: Mapping[str, Any]) -> Mapping[str, Any]:
    value = data.get("equipment")
    return value if isinstance(value, Mapping) else {}


def ranging_guild_shot_locked_reasons_pure(
    data: Mapping[str, Any],
) -> tuple[str, ...]:
    equipment = _equipment(data)
    weapon = str(equipment.get("weapon", "") or "")
    ammunition = str(equipment.get("ammunition", "") or "")
    weapon_data = COMBAT_RANGED_WEAPON_DATA.get(weapon)
    reasons: list[str] = []
    if not isinstance(weapon_data, Mapping) or "Bronze arrows" not in tuple(
        weapon_data.get("compatible_ammo", ())
    ):
        reasons.append("Equip a bow that can fire Bronze arrows")
    if ammunition != "Bronze arrows":
        reasons.append("Equip Bronze arrows")
    if _int(_inventory(data).get("Bronze arrows")) <= 0:
        reasons.append("No Bronze arrows remain")
    return tuple(reasons)


def ranging_guild_entry_locked_reasons_pure(
    data: Mapping[str, Any],
) -> tuple[str, ...]:
    reasons: list[str] = []
    state = sanitize_ranging_guild_state_pure(data.get("ranging_guild"))
    if state["active"]:
        reasons.append("A competition is already active")
    if state["pending_claim"]:
        reasons.append("Claim the previous competition's tickets")
    session = data.get("activity_session")
    active_id = (
        str(session.get("active_id", "")) if isinstance(session, Mapping) else ""
    )
    if active_id and active_id != RANGING_GUILD_ACTIVITY_ID:
        reasons.append("Leave the current activity first")
    if _effective_ranged_level(data) < RANGING_GUILD_ENTRY_LEVEL:
        reasons.append(f"Ranged level {RANGING_GUILD_ENTRY_LEVEL}")
    if _int(_inventory(data).get("Coins")) < RANGING_GUILD_ENTRY_COINS:
        reasons.append(f"{RANGING_GUILD_ENTRY_COINS} Coins")
    equipment_reasons = ranging_guild_shot_locked_reasons_pure(data)
    reasons.extend(reason for reason in equipment_reasons if reason != "No Bronze arrows remain")
    return tuple(reasons)


def default_ranging_guild_state_pure() -> dict[str, Any]:
    return {
        "version": RANGING_GUILD_STATE_VERSION,
        "active": False,
        "shots_fired": 0,
        "score": 0,
        "pending_claim": False,
        "last_score": 0,
        "competitions_started": 0,
        "competitions_completed": 0,
        "exchange_purchases": 0,
        "purchases": {},
        "last_outcome": "",
        "last_result": "",
    }


def sanitize_ranging_guild_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_ranging_guild_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    active = bool(source.get("active", False))
    shots_fired = _int(source.get("shots_fired"), maximum=RANGING_GUILD_SHOTS)
    pending_claim = bool(source.get("pending_claim", False))
    if pending_claim:
        active = False
        shots_fired = RANGING_GUILD_SHOTS
    if not active and not pending_claim:
        shots_fired = 0
    purchases = source.get("purchases")
    return {
        **defaults,
        "active": active,
        "shots_fired": shots_fired,
        "score": _int(source.get("score"), maximum=1_000) if active or pending_claim else 0,
        "pending_claim": pending_claim,
        "last_score": _int(source.get("last_score"), maximum=1_000),
        "competitions_started": _int(source.get("competitions_started")),
        "competitions_completed": _int(source.get("competitions_completed")),
        "exchange_purchases": _int(source.get("exchange_purchases")),
        "purchases": {
            reward_id: _int(count)
            for reward_id, count in (purchases.items() if isinstance(purchases, Mapping) else ())
            if reward_id in RANGING_GUILD_REWARDS_BY_ID
        },
        "last_outcome": str(source.get("last_outcome", ""))[:40],
        "last_result": str(source.get("last_result", ""))[:500],
    }


def enter_ranging_guild_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    reasons = ranging_guild_entry_locked_reasons_pure(player_data)
    if reasons:
        return copy.deepcopy(dict(player_data)), False, {"reason": reasons[0]}
    data = copy.deepcopy(dict(player_data))
    inventory = _mutable_inventory(data)
    inventory["Coins"] = _int(inventory.get("Coins")) - RANGING_GUILD_ENTRY_COINS
    inventory["Bronze arrows"] = _int(inventory.get("Bronze arrows")) + RANGING_GUILD_ENTRY_ARROWS
    state = sanitize_ranging_guild_state_pure(data.get("ranging_guild"))
    state.update(
        {
            "active": True,
            "shots_fired": 0,
            "score": 0,
            "pending_claim": False,
            "competitions_started": state["competitions_started"] + 1,
            "last_outcome": "",
            "last_result": "Competition started: 10 Bronze arrows supplied.",
        }
    )
    data["ranging_guild"] = state
    data["activity_session"] = {"active_id": RANGING_GUILD_ACTIVITY_ID}
    return data, True, {"message": state["last_result"]}


def ranging_guild_outcome_pure(
    player_data: Mapping[str, Any],
    roll: Any,
) -> tuple[str, int]:
    equipment = _equipment(player_data)
    totals = equipment_stat_totals_pure(equipment, EQUIPMENT_DATA)
    style = combat_attack_style_for_equipment_pure(player_data, EQUIPMENT_DATA)
    quality = (
        int(_unit(roll) * 160)
        + _effective_ranged_level(player_data)
        + int(totals.attack_ranged) // 2
        + (15 if style == "ranged_accurate" else 0)
    )
    for threshold, outcome_id in RANGING_GUILD_QUALITY_THRESHOLDS:
        if quality < threshold:
            return outcome_id, quality
    return "bullseye", quality


def apply_ranging_guild_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    productive: bool = True,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_ranging_guild_state_pure(data.get("ranging_guild"))
    data["ranging_guild"] = state
    if not state["active"]:
        return data, False, {"reason": "Enter the Ranging Guild competition first."}
    if not productive:
        return data, True, {"advanced": False, "ranged_xp": 0.0, "message": "Shot deferred."}
    reasons = ranging_guild_shot_locked_reasons_pure(data)
    if reasons:
        return data, False, {"reason": reasons[0]}

    inventory = _mutable_inventory(data)
    inventory["Bronze arrows"] = _int(inventory.get("Bronze arrows")) - 1
    outcome_id, quality = ranging_guild_outcome_pure(
        data,
        (rng or (lambda: 0.0))(),
    )
    band = RANGING_GUILD_BANDS_BY_ID[outcome_id]
    doubled = "Hati paws" in set(map(str, _equipment(data).values()))
    ranged_xp = band.ranged_xp * (2.0 if doubled else 1.0)
    data["ranged_exp"] = _float(data.get("ranged_exp")) + ranged_xp
    state["shots_fired"] += 1
    state["score"] += band.score
    state["last_outcome"] = outcome_id
    terminal = state["shots_fired"] >= RANGING_GUILD_SHOTS
    if terminal:
        state["active"] = False
        state["pending_claim"] = True
        state["competitions_completed"] += 1
        data["activity_session"] = {"active_id": ""}
    state["last_result"] = (
        f"{band.display_name}: +{band.score} score, +{ranged_xp:g} Ranged XP."
    )
    if terminal:
        state["last_result"] += (
            f" Final score {state['score']}; "
            f"claim {state['score'] // 10} tickets."
        )
    return data, True, {
        "advanced": True,
        "terminal": terminal,
        "outcome_id": outcome_id,
        "quality": quality,
        "score": band.score,
        "ranged_xp": ranged_xp,
        "hati_paws_doubled": doubled,
        "message": state["last_result"],
    }


def claim_ranging_guild_tickets_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_ranging_guild_state_pure(data.get("ranging_guild"))
    data["ranging_guild"] = state
    if not state["pending_claim"]:
        return data, False, {"reason": "No completed competition is waiting to be claimed."}
    tickets = state["score"] // 10
    inventory = _mutable_inventory(data)
    inventory[RANGING_GUILD_TICKET_ITEM] = _int(
        inventory.get(RANGING_GUILD_TICKET_ITEM)
    ) + tickets
    state["last_score"] = state["score"]
    state["score"] = 0
    state["shots_fired"] = 0
    state["pending_claim"] = False
    state["last_result"] = f"Claimed {tickets} archery tickets."
    return data, True, {"tickets": tickets, "message": state["last_result"]}


def purchase_ranging_guild_reward_pure(
    player_data: Mapping[str, Any],
    reward_id: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    reward = RANGING_GUILD_REWARDS_BY_ID.get(str(reward_id))
    if reward is None:
        return data, False, {"reason": "Unknown Ranging Guild reward."}
    inventory = _mutable_inventory(data)
    tickets = _int(inventory.get(RANGING_GUILD_TICKET_ITEM))
    if tickets < reward.ticket_cost:
        return data, False, {"reason": f"Requires {reward.ticket_cost} archery tickets."}
    inventory[RANGING_GUILD_TICKET_ITEM] = tickets - reward.ticket_cost
    inventory[reward.item_name] = _int(inventory.get(reward.item_name)) + reward.quantity
    state = sanitize_ranging_guild_state_pure(data.get("ranging_guild"))
    state["purchases"][reward.id] = _int(state["purchases"].get(reward.id)) + 1
    state["exchange_purchases"] += 1
    state["last_result"] = f"Purchased {reward.display_name}."
    data["ranging_guild"] = state
    return data, True, {
        "reward_id": reward.id,
        "item_name": reward.item_name,
        "quantity": reward.quantity,
        "message": state["last_result"],
    }


def leave_ranging_guild_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_ranging_guild_state_pure(data.get("ranging_guild"))
    if not state["active"]:
        return data, False, {"reason": "No Ranging Guild competition is active."}
    state["active"] = False
    state["shots_fired"] = 0
    state["score"] = 0
    state["last_result"] = "Left the competition; unfinished score forfeited."
    data["ranging_guild"] = state
    data["activity_session"] = {"active_id": ""}
    return data, True, {"message": state["last_result"]}


def ranging_guild_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_ranging_guild_state_pure(player_data.get("ranging_guild"))
    inventory = _inventory(player_data)
    entry_reasons = ranging_guild_entry_locked_reasons_pure(player_data)
    shot_reasons = ranging_guild_shot_locked_reasons_pure(player_data) if state["active"] else ()
    claim_tickets = state["score"] // 10 if state["pending_claim"] else 0
    reward_options = []
    tickets = _int(inventory.get(RANGING_GUILD_TICKET_ITEM))
    for reward in RANGING_GUILD_REWARDS:
        reward_options.append(
            {
                "id": reward.id,
                "label": reward.display_name,
                "item_name": reward.item_name,
                "quantity": reward.quantity,
                "cost": reward.ticket_cost,
                "purchase_enabled": tickets >= reward.ticket_cost,
                "purchase_reason": (
                    ""
                    if tickets >= reward.ticket_cost
                    else f"Requires {reward.ticket_cost} tickets."
                ),
            }
        )
    if state["pending_claim"]:
        primary_label = f"Claim {claim_tickets} tickets"
        primary_enabled = True
    elif state["active"]:
        primary_label = "Select for reviews"
        primary_enabled = not shot_reasons
    else:
        primary_label = "Enter competition"
        primary_enabled = not entry_reasons
    return {
        **state,
        "tickets": tickets,
        "claim_tickets": claim_tickets,
        "shots_remaining": RANGING_GUILD_SHOTS - state["shots_fired"],
        "entry_reasons": entry_reasons,
        "shot_reasons": shot_reasons,
        "primary_label": primary_label,
        "primary_enabled": primary_enabled,
        "leave_visible": state["active"],
        "reward_options": tuple(reward_options),
        "last_result": state["last_result"],
    }


def ranging_guild_can_review_pure(player_data: Mapping[str, Any]) -> bool:
    state = sanitize_ranging_guild_state_pure(player_data.get("ranging_guild"))
    return bool(state["active"] and not ranging_guild_shot_locked_reasons_pure(player_data))


def apply_ranging_guild_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    payload = payload if isinstance(payload, Mapping) else {}
    if action_id == "enter":
        return enter_ranging_guild_pure(player_data)
    if action_id == "claim":
        return claim_ranging_guild_tickets_pure(player_data)
    if action_id == "purchase":
        return purchase_ranging_guild_reward_pure(
            player_data,
            str(payload.get("reward_id", "")),
        )
    if action_id == "leave":
        return leave_ranging_guild_pure(player_data)
    return copy.deepcopy(dict(player_data)), False, {"reason": "Unknown Ranging Guild action."}
