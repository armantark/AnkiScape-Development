"""Pure Great Orb Project match, round, crafting, and reward-shop mechanics."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.great_orb_project_data import (
    GREAT_ORB_PROJECT_ACTIVITY_ID,
    GREAT_ORB_PROJECT_ALTARS,
    GREAT_ORB_PROJECT_CRAFTING_POLICIES,
    GREAT_ORB_PROJECT_DOCTRINES,
    GREAT_ORB_PROJECT_REWARDS,
    GREAT_ORB_PROJECT_TELEPORT_TABLETS_BY_ITEM,
    MASTER_RUNECRAFTER_REWARDS,
    STANDARD_RUNECRAFTER_REWARDS,
    GREAT_ORB_PROJECT_ROUNDS,
    GREAT_ORB_PROJECT_TEMP_CAPACITY,
    OMNI_TALISMAN_ACCESS_PAIRS,
    OMNI_TALISMAN_XP,
)
from ..data.runecrafting_data import (
    OMNI_TALISMAN_STAFF_ITEM,
    RUNECRAFTING_STAFF_ITEM,
)
from ..logic_pure.logic_pure_quest import quest_unlock_locked_reasons_pure
from .wicked_hood_logic import ensure_wicked_hood_state_pure


_MASTER_RUNECRAFTER_BONUSES = {
    item: xp_rate
    for _reward_id, item, _tokens, _source_item_id, _slot, _bonus, xp_rate in (
        MASTER_RUNECRAFTER_REWARDS
    )
}
_MASTER_RUNECRAFTER_ITEMS = frozenset(
    _MASTER_RUNECRAFTER_BONUSES
)
_STANDARD_RUNECRAFTER_BONUSES = {
    item: xp_rate
    for _reward_id, item, _tokens, _source_item_id, _slot, _bonus, xp_rate in (
        STANDARD_RUNECRAFTER_REWARDS
    )
}


def apply_master_runecrafter_xp_bonus_pure(
    player_data: Mapping[str, Any], base_xp: Any
) -> float:
    """Apply the worn-piece bonus, capped at 700 bonus XP per action."""
    xp = _non_negative_float(base_xp)
    equipment = player_data.get("equipment")
    worn = set(equipment.values()) if isinstance(equipment, Mapping) else set()
    worn_pieces = _MASTER_RUNECRAFTER_ITEMS.intersection(worn)
    rate = sum(_MASTER_RUNECRAFTER_BONUSES[item] for item in worn_pieces)
    if worn_pieces == _MASTER_RUNECRAFTER_ITEMS:
        rate += 0.01
    return xp + min(xp * rate, 700.0)


def apply_great_orb_project_xp_bonuses_pure(
    player_data: Mapping[str, Any], base_xp: Any
) -> float:
    """Apply the GOP-only standard outfit boost plus any Master bonus."""
    xp = _non_negative_float(base_xp)
    equipment = player_data.get("equipment")
    worn = set(equipment.values()) if isinstance(equipment, Mapping) else set()
    standard_rate = sum(
        rate for item, rate in _STANDARD_RUNECRAFTER_BONUSES.items() if item in worn
    )
    return (
        apply_master_runecrafter_xp_bonus_pure(player_data, xp)
        + xp * standard_rate
    )


GREAT_ORB_PROJECT_STATE_VERSION = 2
_VALID_MODES = frozenset({"casual", "advanced"})
_VALID_DOCTRINES = frozenset(key for key, _label in GREAT_ORB_PROJECT_DOCTRINES)
_VALID_CRAFTING_POLICIES = frozenset(
    key for key, _label in GREAT_ORB_PROJECT_CRAFTING_POLICIES
)


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _roll(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        parsed = 0.5
    return max(0.0, min(parsed, 0.999999))


def _non_negative_float(value: Any) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError, OverflowError):
        return 0.0


def use_great_orb_project_teleport_tablet_pure(
    player_data: Mapping[str, Any],
    item_name: Any,
    equipment_data: Mapping[str, Any],
    quest_unlock_rules: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Break one GOP tablet and queue its sourced Runecrafting route effect."""
    item = str(item_name)
    spec = GREAT_ORB_PROJECT_TELEPORT_TABLETS_BY_ITEM.get(item)
    if spec is None:
        return dict(player_data), False, {
            "reason": "That is not a Runecrafting teleport tablet."
        }

    data = ensure_wicked_hood_state_pure(player_data)
    inventory = dict(data.get("inventory", {}) or {})
    if _int(inventory.get(item)) <= 0:
        return data, False, {"reason": f"No {item} remains in the Bank."}

    altar_id = str(spec["altar_id"])
    target_id = str(spec["target_id"])
    if target_id:
        quest_reasons = quest_unlock_locked_reasons_pure(
            data, "runecrafting", target_id, quest_unlock_rules
        )
        if quest_reasons:
            return data, False, {"reason": str(quest_reasons[0])}
        if altar_id == "astral" and _int(inventory.get("Seal of passage")) <= 0:
            return data, False, {"reason": "Requires a Seal of passage."}
        if altar_id == "law":
            equipped = data.get("equipment")
            carried = data.get("carried_inventory")
            carried_view = (
                carried.get(target_id, {}) if isinstance(carried, Mapping) else {}
            )
            present = {
                str(value)
                for value in (
                    equipped.values() if isinstance(equipped, Mapping) else ()
                )
                if value
            }
            if isinstance(carried_view, Mapping):
                present.update(
                    str(name)
                    for name, quantity in carried_view.items()
                    if _int(quantity) > 0
                )
            prohibited = []
            for present_item in sorted(present):
                equipment = equipment_data.get(present_item)
                if equipment is None or present_item == "Law talisman staff":
                    continue
                slot = str(
                    equipment.get("slot", "")
                    if isinstance(equipment, Mapping)
                    else getattr(equipment, "slot", "")
                )
                bonuses = (
                    equipment.get("bonuses")
                    if isinstance(equipment, Mapping)
                    else getattr(equipment, "bonuses", None)
                )
                bonus_values = (
                    bonuses.values()
                    if isinstance(bonuses, Mapping)
                    else vars(bonuses).values()
                    if bonuses is not None and hasattr(bonuses, "__dict__")
                    else ()
                )
                if slot in {"weapon", "shield", "ammunition"} or any(
                    float(value or 0) != 0 for value in bonus_values
                ):
                    prohibited.append(present_item)
            if prohibited:
                return data, False, {
                    "reason": "Entrana forbids carried or equipped combat gear: "
                    + ", ".join(prohibited)
                    + "."
                }

        hood = data["wicked_hood"]
        pending = str(hood.get("pending_altar_teleport", "") or "")
        if pending:
            return data, False, {
                "reason": f"A teleport to the {pending.title()} altar is already queued."
            }
        active_run = data.get("skilling_bank_run")
        if (
            isinstance(active_run, Mapping)
            and active_run.get("target_id") in (None, target_id)
            and _int(active_run.get("reviews_remaining")) > 0
            and active_run.get("outbound_teleport_used") is True
        ):
            return data, False, {
                "reason": "This route's outbound leg has already been teleported."
            }

    inventory[item] -= 1
    if inventory[item] <= 0:
        inventory.pop(item, None)
    data["inventory"] = inventory
    if target_id:
        carried_root = dict(data.get("carried_inventory", {}) or {})
        carried_view = dict(carried_root.get(target_id, {}) or {})
        remaining = _int(inventory.get(item))
        if _int(carried_view.get(item)) > remaining:
            if remaining > 0:
                carried_view[item] = remaining
            else:
                carried_view.pop(item, None)
            carried_root[target_id] = carried_view
            data["carried_inventory"] = carried_root
        data["wicked_hood"]["pending_altar_teleport"] = altar_id
        data["current_runecrafting"] = target_id
    destination = str(spec["destination"])
    data["runecrafting_last_teleport"] = {
        "item": item,
        "altar_id": altar_id,
        "target_id": target_id,
        "destination": destination,
    }
    message = f"Broke {item}; teleported to {destination}."
    if target_id:
        message += " The next matching outbound route is skipped."
    return data, True, {
        "message": message,
        "item": item,
        "altar_id": altar_id,
        "target_id": target_id,
        "destination": destination,
    }


def default_great_orb_project_state_pure() -> dict[str, Any]:
    return {
        "great_orb_project": {
            "version": GREAT_ORB_PROJECT_STATE_VERSION,
            "tokens": 0,
            "games_completed": 0,
            "games_won": 0,
            "automation_mode": "casual",
            "doctrine": "balanced",
            "crafting_policy": "craft_each_round",
            "omni_talisman_xp_claimed": False,
            "active": {},
        },
        "great_orb_project_last_result": "",
        "runecrafting_last_teleport": {},
    }


def _sanitize_active(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    return {
        "round": _int(raw.get("round"), maximum=GREAT_ORB_PROJECT_ROUNDS - 1),
        "rounds_won": _int(raw.get("rounds_won"), maximum=GREAT_ORB_PROJECT_ROUNDS),
        "rounds_lost": _int(raw.get("rounds_lost"), maximum=GREAT_ORB_PROJECT_ROUNDS),
        "rounds_tied": _int(raw.get("rounds_tied"), maximum=GREAT_ORB_PROJECT_ROUNDS),
        "pending_tokens": _int(raw.get("pending_tokens"), maximum=100_000),
        "saved_essence": _int(
            raw.get("saved_essence"), maximum=GREAT_ORB_PROJECT_TEMP_CAPACITY
        ),
        "crafted_essence": _int(raw.get("crafted_essence"), maximum=100_000),
        "xp_earned": _non_negative_float(raw.get("xp_earned")),
        "participating_rounds": _int(
            raw.get("participating_rounds"), maximum=GREAT_ORB_PROJECT_ROUNDS
        ),
    }


def sanitize_great_orb_project_state_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("automation_mode", "casual"))
    doctrine = str(source.get("doctrine", "balanced"))
    crafting = str(source.get("crafting_policy", "craft_each_round"))
    return {
        "version": GREAT_ORB_PROJECT_STATE_VERSION,
        "tokens": _int(source.get("tokens")),
        "games_completed": _int(source.get("games_completed")),
        "games_won": _int(source.get("games_won")),
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "doctrine": doctrine if doctrine in _VALID_DOCTRINES else "balanced",
        "crafting_policy": (
            crafting
            if crafting in _VALID_CRAFTING_POLICIES
            else "craft_each_round"
        ),
        "omni_talisman_xp_claimed": bool(
            source.get("omni_talisman_xp_claimed")
        ),
        "active": _sanitize_active(source.get("active")),
    }


def sanitize_great_orb_project_player_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    data = dict(player_data or {})
    state = sanitize_great_orb_project_state_pure(data.get("great_orb_project"))
    activity = data.get("activity_session")
    active_id = (
        str(activity.get("active_id", ""))
        if isinstance(activity, Mapping)
        else ""
    )
    if state["active"] and active_id not in {"", GREAT_ORB_PROJECT_ACTIVITY_ID}:
        state["active"] = {}
    inventory = data.get("inventory")
    equipment = data.get("equipment")
    hood = data.get("wicked_hood")
    if not state["omni_talisman_xp_claimed"] and (
        isinstance(inventory, Mapping)
        and (
            _int(inventory.get("Omni-talisman")) > 0
            or _int(inventory.get("Omni-tiara")) > 0
            or _int(inventory.get(OMNI_TALISMAN_STAFF_ITEM)) > 0
        )
        or isinstance(equipment, Mapping)
        and (
            equipment.get("head") == "Omni-tiara"
            or equipment.get("weapon") == OMNI_TALISMAN_STAFF_ITEM
        )
        or isinstance(hood, Mapping)
        and bool(hood.get("omni_fed"))
    ):
        state["omni_talisman_xp_claimed"] = True
    return {
        "great_orb_project": state,
        "great_orb_project_last_result": str(
            data.get("great_orb_project_last_result", "") or ""
        )[:400],
    }


def set_great_orb_project_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_great_orb_project_player_state_pure rebuilds
    # all its keys, and inventory is rebuilt with dict() before every write.
    data = dict(player_data)
    sanitized = sanitize_great_orb_project_player_state_pure(data)
    state = sanitized["great_orb_project"]
    if state["active"]:
        return data, False, {"reason": "Finish or leave the current match first."}
    body = dict(payload or {})
    mode = str(body.get("automation_mode", state["automation_mode"]))
    doctrine = str(body.get("doctrine", state["doctrine"]))
    crafting = str(body.get("crafting_policy", state["crafting_policy"]))
    if mode not in _VALID_MODES:
        return data, False, {"reason": "Unknown Great Orb Project automation mode."}
    if doctrine not in _VALID_DOCTRINES:
        return data, False, {"reason": "Unknown Great Orb Project doctrine."}
    if crafting not in _VALID_CRAFTING_POLICIES:
        return data, False, {"reason": "Unknown Great Orb Project crafting policy."}
    state.update(
        {
            "automation_mode": mode,
            "doctrine": doctrine,
            "crafting_policy": crafting,
        }
    )
    data.update(sanitized)
    data["great_orb_project"] = state
    data["great_orb_project_last_result"] = "Great Orb Project policy saved."
    return data, True, {"message": data["great_orb_project_last_result"]}


def enter_great_orb_project_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if payload:
        data, ok, info = set_great_orb_project_policy_pure(player_data, payload)
        if not ok:
            return data, False, info
    else:
        # Shallow on purpose: sanitize_great_orb_project_player_state_pure
        # rebuilds all its keys, and inventory is rebuilt with dict() before
        # every write.
        data = dict(player_data)
    sanitized = sanitize_great_orb_project_player_state_pure(data)
    state = sanitized["great_orb_project"]
    if state["active"]:
        return data, False, {"reason": "A Great Orb Project match is already active."}
    if _int(data.get("runecrafting_level"), 1, maximum=99) < 50:
        return data, False, {"reason": "Requires level 50 Runecrafting."}
    activity = data.get("activity_session")
    active_id = (
        str(activity.get("active_id", ""))
        if isinstance(activity, Mapping)
        else ""
    )
    if active_id and active_id != GREAT_ORB_PROJECT_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    state["active"] = {
        "round": 0,
        "rounds_won": 0,
        "rounds_lost": 0,
        "rounds_tied": 0,
        "pending_tokens": 0,
        "saved_essence": 0,
        "crafted_essence": 0,
        "xp_earned": 0.0,
        "participating_rounds": 0,
    }
    data.update(sanitized)
    data["great_orb_project"] = state
    data["activity_session"] = {"active_id": GREAT_ORB_PROJECT_ACTIVITY_ID}
    data["current_utility"] = GREAT_ORB_PROJECT_ACTIVITY_ID
    data["great_orb_project_last_result"] = "Great Orb Project · Air altar ready"
    return data, True, {"message": data["great_orb_project_last_result"]}


def _round_scores(doctrine: str, player_roll: Any, opponent_roll: Any) -> tuple[int, int, bool]:
    player = 7 + int(_roll(player_roll) * 7)
    opponent = 7 + int(_roll(opponent_roll) * 7)
    participating = doctrine != "barrier"
    if doctrine == "attract":
        player += 4
    elif doctrine == "repel":
        opponent -= 4
    elif doctrine == "barrier":
        player += 1
        opponent -= 3
    else:
        player += 2
        opponent -= 1
    return max(0, player), max(0, opponent), participating


def _rune_multiplier(level: int, divisor: int) -> int:
    return max(1, level // divisor + 1)


def _craft_essence(
    data: dict[str, Any], altar_index: int, essence: int
) -> tuple[int, float]:
    if essence <= 0:
        return 0, 0.0
    altar = GREAT_ORB_PROJECT_ALTARS[altar_index]
    level = max(1, min(_int(data.get("runecrafting_level"), 1), 99))
    runes = essence * _rune_multiplier(level, altar.multiplier_divisor)
    inventory = dict(data.get("inventory") or {})
    inventory[altar.rune] = _int(inventory.get(altar.rune)) + runes
    data["inventory"] = inventory
    return runes, round(essence * altar.base_xp * 2.0, 1)


def _finish_match(data: dict[str, Any]) -> None:
    activity = data.get("activity_session")
    if (
        isinstance(activity, Mapping)
        and str(activity.get("active_id", "")) == GREAT_ORB_PROJECT_ACTIVITY_ID
    ):
        data["activity_session"] = {"active_id": ""}


def apply_great_orb_project_review_pure(
    player_data: Mapping[str, Any], player_roll: Any, opponent_roll: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: sanitize_great_orb_project_player_state_pure rebuilds
    # all its keys, and inventory is rebuilt with dict() before every write.
    data = dict(player_data)
    sanitized = sanitize_great_orb_project_player_state_pure(data)
    state = sanitized["great_orb_project"]
    active = state["active"]
    if not active:
        return data, {"allowed": False, "reason": "Enter the Great Orb Project before training."}

    round_index = int(active["round"])
    altar = GREAT_ORB_PROJECT_ALTARS[round_index]
    doctrine = "balanced" if state["automation_mode"] == "casual" else state["doctrine"]
    player_score, opponent_score, participating = _round_scores(
        doctrine, player_roll, opponent_roll
    )
    if player_score > opponent_score:
        result = "won"
        active["rounds_won"] += 1
        round_tokens = 100
    elif player_score < opponent_score:
        result = "lost"
        active["rounds_lost"] += 1
        round_tokens = 10
    else:
        result = "tied"
        active["rounds_tied"] += 1
        round_tokens = 25
    if not participating:
        round_tokens = 0
    else:
        active["participating_rounds"] += 1
    active["pending_tokens"] += round_tokens

    essence_awarded = min(14, 4 + (player_score + opponent_score) // 4)
    capacity = GREAT_ORB_PROJECT_TEMP_CAPACITY - int(active["saved_essence"])
    essence_kept = min(capacity, essence_awarded)
    essence_dropped = essence_awarded - essence_kept
    active["saved_essence"] += essence_kept
    terminal = round_index + 1 >= GREAT_ORB_PROJECT_ROUNDS
    craft_now = state["crafting_policy"] == "craft_each_round" or terminal
    runes = 0
    xp = 0.0
    if craft_now:
        essence_crafted = int(active["saved_essence"])
        runes, xp = _craft_essence(data, round_index, essence_crafted)
        xp = apply_great_orb_project_xp_bonuses_pure(data, xp)
        active["saved_essence"] = 0
        active["crafted_essence"] += essence_crafted
        active["xp_earned"] = float(active["xp_earned"]) + xp

    total_tokens = 0
    majority_bonus = 0
    if terminal:
        if active["rounds_won"] > active["rounds_lost"]:
            majority_bonus = 200
            state["games_won"] += 1
        elif active["rounds_won"] == active["rounds_lost"]:
            majority_bonus = 100
        total_tokens = int(active["pending_tokens"]) + majority_bonus
        state["tokens"] += total_tokens
        state["games_completed"] += 1
        state["active"] = {}
        _finish_match(data)
    else:
        active["round"] = round_index + 1
        state["active"] = active

    data.update(sanitized)
    data["great_orb_project"] = state
    detail = (
        f"{altar.label} {result} {player_score}-{opponent_score} · "
        f"{essence_awarded} essence"
    )
    if essence_dropped:
        detail += f" ({essence_dropped} left behind)"
    if xp:
        detail += f" · {runes} {altar.rune}s · {xp:g} Runecrafting XP"
    if terminal:
        detail += f" · match complete · {total_tokens} tokens"
    else:
        detail += f" · {round_index + 1}/8 rounds"
    data["great_orb_project_last_result"] = "Great Orb Project · " + detail
    return data, {
        "allowed": True,
        "action_id": GREAT_ORB_PROJECT_ACTIVITY_ID,
        "success": result != "lost",
        "expected_success_chance": 0.5,
        "altar_id": altar.id,
        "altar_label": altar.label,
        "doctrine": doctrine,
        "player_score": player_score,
        "opponent_score": opponent_score,
        "round_result": result,
        "participating": participating,
        "round_tokens": round_tokens,
        "majority_bonus": majority_bonus,
        "tokens": total_tokens,
        "essence_awarded": essence_awarded,
        "essence_dropped": essence_dropped,
        "saved_essence": int(active.get("saved_essence", 0)),
        "output_item": altar.rune if runes else "",
        "output_quantity": runes,
        "xp": xp,
        "terminal": terminal,
        "completed_activity": terminal,
        "status": data["great_orb_project_last_result"],
    }


def leave_great_orb_project_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_great_orb_project_player_state_pure rebuilds
    # all its keys, and inventory is rebuilt with dict() before every write.
    data = dict(player_data)
    sanitized = sanitize_great_orb_project_player_state_pure(data)
    state = sanitized["great_orb_project"]
    active = state["active"]
    if not active:
        return data, False, {"reason": "No Great Orb Project match is active."}
    progress = int(active["round"])
    forfeited = int(active["pending_tokens"])
    state["active"] = {}
    data.update(sanitized)
    data["great_orb_project"] = state
    _finish_match(data)
    data["great_orb_project_last_result"] = (
        f"Left Great Orb Project after {progress}/8 rounds · "
        f"{forfeited} pending tokens forfeited"
    )
    return data, True, {"message": data["great_orb_project_last_result"]}


def _missing_omni_access_pure(inventory: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        talisman.removesuffix(" talisman")
        for talisman, tiara in OMNI_TALISMAN_ACCESS_PAIRS
        if _int(inventory.get(talisman)) <= 0 and _int(inventory.get(tiara)) <= 0
    )


def _great_orb_reward_locked_reason_pure(
    player_data: Mapping[str, Any],
    state: Mapping[str, Any],
    reward_id: str,
    reward: Mapping[str, Any],
) -> str:
    if _int(player_data.get("runecrafting_level"), 1, maximum=99) < 50:
        return "Requires level 50 Runecrafting."
    if state.get("active"):
        return "Finish or leave the current match first."
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    if reward_id == "omni_talisman":
        if _int(inventory.get("Omni-talisman")) > 0:
            return "You already have an Omni-talisman."
        if not state.get("omni_talisman_xp_claimed"):
            missing = _missing_omni_access_pure(inventory)
            if missing:
                return "Show Elriss one talisman or tiara for: " + ", ".join(missing) + "."
        return ""
    if reward_id == "omni_tiara":
        if _int(inventory.get("Omni-talisman")) <= 0:
            return "Requires an Omni-talisman."
        if _int(inventory.get("Tiara")) <= 0:
            return "Requires a Tiara."
        return ""
    if reward_id == "omni_talisman_staff":
        if _int(inventory.get("Omni-talisman")) <= 0:
            return "Requires an Omni-talisman."
        if _int(inventory.get(RUNECRAFTING_STAFF_ITEM)) <= 0:
            return f"Requires a {RUNECRAFTING_STAFF_ITEM}."
        return ""
    cost = int(reward.get("tokens", 0) or 0)
    return (
        ""
        if int(state.get("tokens", 0) or 0) >= cost
        else f"Requires {cost:,} Runecrafting Guild tokens."
    )


def buy_great_orb_project_reward_pure(
    player_data: Mapping[str, Any], reward_id: Any, quantity: Any = 1
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_great_orb_project_player_state_pure rebuilds
    # all its keys, and inventory is rebuilt with dict() before every write.
    data = dict(player_data)
    sanitized = sanitize_great_orb_project_player_state_pure(data)
    state = sanitized["great_orb_project"]
    if state["active"]:
        return data, False, {"reason": "Finish or leave the current match first."}
    if _int(data.get("runecrafting_level"), 1, maximum=99) < 50:
        return data, False, {"reason": "Requires level 50 Runecrafting."}
    reward = GREAT_ORB_PROJECT_REWARDS.get(str(reward_id))
    if reward is None:
        return data, False, {"reason": "Unknown Great Orb Project reward."}
    inventory = dict(data.get("inventory") or {})
    if str(reward_id) == "omni_talisman":
        if _int(inventory.get("Omni-talisman")) > 0:
            return data, False, {"reason": "You already have an Omni-talisman."}
        first_claim = not state["omni_talisman_xp_claimed"]
        missing = _missing_omni_access_pure(inventory) if first_claim else ()
        if missing:
            return data, False, {
                "reason": "Show Elriss one talisman or tiara for: " + ", ".join(missing) + "."
            }
        inventory["Omni-talisman"] = 1
        xp = OMNI_TALISMAN_XP if first_claim else 0.0
        if xp:
            data["runecrafting_exp"] = _non_negative_float(
                data.get("runecrafting_exp")
            ) + xp
            state["omni_talisman_xp_claimed"] = True
        data.update(sanitized)
        data["great_orb_project"] = state
        data["inventory"] = inventory
        data["great_orb_project_last_result"] = (
            "Wizard Elriss · Omni-talisman claimed"
            + (" · 13,605 Runecrafting XP" if xp else "")
        )
        return data, True, {
            "message": data["great_orb_project_last_result"],
            "item": "Omni-talisman",
            "quantity": 1,
            "tokens_spent": 0,
            "xp": xp,
        }
    if str(reward_id) == "omni_tiara":
        if _int(inventory.get("Omni-talisman")) <= 0:
            return data, False, {"reason": "Requires an Omni-talisman."}
        if _int(inventory.get("Tiara")) <= 0:
            return data, False, {"reason": "Requires a Tiara."}
        inventory["Omni-talisman"] -= 1
        inventory["Tiara"] -= 1
        inventory["Omni-tiara"] = _int(inventory.get("Omni-tiara")) + 1
        data.update(sanitized)
        data["great_orb_project"] = state
        data["inventory"] = inventory
        data["great_orb_project_last_result"] = (
            "Wizard Korvak · Omni-talisman and Tiara combined into an Omni-tiara"
        )
        return data, True, {
            "message": data["great_orb_project_last_result"],
            "item": "Omni-tiara",
            "quantity": 1,
            "tokens_spent": 0,
        }
    if str(reward_id) == "omni_talisman_staff":
        if _int(inventory.get("Omni-talisman")) <= 0:
            return data, False, {"reason": "Requires an Omni-talisman."}
        if _int(inventory.get(RUNECRAFTING_STAFF_ITEM)) <= 0:
            return data, False, {
                "reason": f"Requires a {RUNECRAFTING_STAFF_ITEM}."
            }
        inventory["Omni-talisman"] -= 1
        inventory[RUNECRAFTING_STAFF_ITEM] -= 1
        inventory[OMNI_TALISMAN_STAFF_ITEM] = (
            _int(inventory.get(OMNI_TALISMAN_STAFF_ITEM)) + 1
        )
        data.update(sanitized)
        data["great_orb_project"] = state
        data["inventory"] = inventory
        data["great_orb_project_last_result"] = (
            "Wizard Korvak · Omni-talisman and Runecrafting staff combined "
            "into an Omni-talisman staff"
        )
        return data, True, {
            "message": data["great_orb_project_last_result"],
            "item": OMNI_TALISMAN_STAFF_ITEM,
            "quantity": 1,
            "tokens_spent": 0,
        }
    purchases = (
        max(1, min(_int(quantity, 1), 10_000))
        if str(reward_id) == "pure_essence"
        else 1
    )
    cost = int(reward["tokens"]) * purchases
    if int(state["tokens"]) < cost:
        return data, False, {
            "reason": f"Requires {cost:,} Runecrafting Guild tokens."
        }
    item = str(reward["item"])
    item_quantity = int(reward.get("quantity", 1)) * purchases
    inventory[item] = _int(inventory.get(item)) + item_quantity
    state["tokens"] -= cost
    data.update(sanitized)
    data["great_orb_project"] = state
    data["inventory"] = inventory
    data["great_orb_project_last_result"] = (
        f"Wizard Elriss · {item} x{item_quantity} · {cost:,} tokens"
    )
    return data, True, {
        "message": data["great_orb_project_last_result"],
        "item": item,
        "quantity": item_quantity,
        "tokens_spent": cost,
    }


def apply_great_orb_project_command_pure(
    player_data: Mapping[str, Any],
    action_id: Any,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    action = str(action_id)
    body = dict(payload or {})
    if action == "set_great_orb_project_policy":
        return set_great_orb_project_policy_pure(player_data, body)
    if action == "enter_great_orb_project":
        return enter_great_orb_project_pure(player_data, body)
    if action == "leave_great_orb_project":
        return leave_great_orb_project_pure(player_data)
    if action == "buy_great_orb_project_reward":
        return buy_great_orb_project_reward_pure(
            player_data, body.get("reward_id"), body.get("quantity", 1)
        )
    # Shallow on purpose: nothing is written to this save, and the only caller
    # (__init__._apply_great_orb_project_command) discards it when ok is False.
    return dict(player_data), False, {
        "reason": "Unknown Great Orb Project action."
    }


def great_orb_project_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    sanitized = sanitize_great_orb_project_player_state_pure(player_data)
    state = sanitized["great_orb_project"]
    active = state["active"]
    round_index = int(active.get("round", 0))
    eligible = _int(player_data.get("runecrafting_level"), 1, maximum=99) >= 50
    rewards = []
    for reward_id, row in GREAT_ORB_PROJECT_REWARDS.items():
        locked_reason = _great_orb_reward_locked_reason_pure(
            player_data, state, reward_id, row
        )
        rewards.append(
            {
                "id": reward_id,
                **row,
                "affordable": not locked_reason,
                "locked_reason": locked_reason,
            }
        )
    return {
        "activity_id": GREAT_ORB_PROJECT_ACTIVITY_ID,
        "eligible": eligible,
        "active": bool(active),
        "can_review": bool(active),
        "tokens": int(state["tokens"]),
        "games_completed": int(state["games_completed"]),
        "games_won": int(state["games_won"]),
        "automation_mode": str(state["automation_mode"]),
        "doctrine": str(state["doctrine"]),
        "crafting_policy": str(state["crafting_policy"]),
        "round": round_index,
        "round_number": round_index + 1 if active else 0,
        "altar": GREAT_ORB_PROJECT_ALTARS[round_index].label if active else "Air altar",
        "rounds_won": int(active.get("rounds_won", 0)),
        "rounds_lost": int(active.get("rounds_lost", 0)),
        "rounds_tied": int(active.get("rounds_tied", 0)),
        "pending_tokens": int(active.get("pending_tokens", 0)),
        "saved_essence": int(active.get("saved_essence", 0)),
        "crafted_essence": int(active.get("crafted_essence", 0)),
        "xp_earned": float(active.get("xp_earned", 0.0)),
        "last_result": sanitized["great_orb_project_last_result"],
        "omni_talisman_xp_claimed": bool(state["omni_talisman_xp_claimed"]),
        "rewards": tuple(rewards),
    }
