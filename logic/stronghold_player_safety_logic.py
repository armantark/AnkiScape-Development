"""Pure landmark, chest, lamp, reclaim, and Combat-entry mechanics."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

try:
    from .skill_registry import get_skill
    from .stronghold_player_safety_data import (
        COCKROACH_SOLDIER_TARGET_ID,
        SAFETY_GLOVES_ITEM,
        STRONGHOLD_LANDMARKS,
    )
except ImportError:  # pragma: no cover - flat test imports
    from skill_registry import get_skill  # type: ignore
    from stronghold_player_safety_data import (  # type: ignore
        COCKROACH_SOLDIER_TARGET_ID,
        SAFETY_GLOVES_ITEM,
        STRONGHOLD_LANDMARKS,
    )


STRONGHOLD_PLAYER_SAFETY_STATE_VERSION = 1


def _int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return max(0, default)


def default_stronghold_player_safety_state_pure() -> dict[str, Any]:
    return {
        "version": STRONGHOLD_PLAYER_SAFETY_STATE_VERSION,
        "stage": 0,
        "crevice_unlocked": False,
        "chest_claimed": False,
        "lamps_remaining": 0,
        "safety_first_emote_unlocked": False,
        "last_result": "Follow the jail-cell poster route to the reward chest.",
    }


def sanitize_stronghold_player_safety_state_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    stage = min(len(STRONGHOLD_LANDMARKS), _int(source.get("stage")))
    chest_claimed = bool(source.get("chest_claimed")) and stage == len(
        STRONGHOLD_LANDMARKS
    )
    return {
        "version": STRONGHOLD_PLAYER_SAFETY_STATE_VERSION,
        "stage": stage,
        "crevice_unlocked": stage >= 2,
        "chest_claimed": chest_claimed,
        "lamps_remaining": min(2, _int(source.get("lamps_remaining"))) if chest_claimed else 0,
        "safety_first_emote_unlocked": chest_claimed
        and bool(source.get("safety_first_emote_unlocked", True)),
        "last_result": str(
            source.get(
                "last_result",
                "Follow the jail-cell poster route to the reward chest.",
            )
            or "Follow the jail-cell poster route to the reward chest."
        )[:500],
    }


def _owns_item(player_data: Mapping[str, Any], item_name: str) -> bool:
    inventory = player_data.get("inventory")
    if isinstance(inventory, Mapping) and _int(inventory.get(item_name)) > 0:
        return True
    equipment = player_data.get("equipment")
    if isinstance(equipment, Mapping) and item_name in equipment.values():
        return True
    for key in ("combat_grave", "death_office"):
        store = player_data.get(key)
        if not isinstance(store, Mapping):
            continue
        items = store.get("items", ())
        if isinstance(items, (tuple, list)) and item_name in items:
            return True
    return False


def stronghold_player_safety_view_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    state = sanitize_stronghold_player_safety_state_pure(
        player_data.get("stronghold_player_safety")
    )
    active_encounter = player_data.get("combat_encounter")
    soldier_active = (
        isinstance(active_encounter, Mapping)
        and active_encounter.get("target_id") == COCKROACH_SOLDIER_TARGET_ID
    )
    encounter_active = isinstance(active_encounter, Mapping) and bool(
        active_encounter.get("target_id")
    )
    activity_session = player_data.get("activity_session")
    persistent_activity_active = (
        isinstance(activity_session, Mapping)
        and bool(activity_session.get("active_id"))
    )
    gloves_owned = _owns_item(player_data, SAFETY_GLOVES_ITEM)
    return {
        **state,
        "stage_count": len(STRONGHOLD_LANDMARKS),
        "complete": state["stage"] == len(STRONGHOLD_LANDMARKS),
        "next_landmark": (
            dict(STRONGHOLD_LANDMARKS[state["stage"]])
            if state["stage"] < len(STRONGHOLD_LANDMARKS)
            else None
        ),
        "can_review": state["stage"] < len(STRONGHOLD_LANDMARKS),
        "can_claim_chest": state["stage"] == len(STRONGHOLD_LANDMARKS)
        and not state["chest_claimed"],
        "gloves_owned": gloves_owned,
        "can_reclaim_gloves": state["chest_claimed"] and not gloves_owned,
        "can_fight_soldier": (
            state["stage"] >= 2
            and not encounter_active
            and not persistent_activity_active
        ),
        "soldier_active": soldier_active,
    }


def apply_stronghold_player_safety_review_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_stronghold_player_safety_state_pure returns
    # a fresh state, and inventory is rebuilt with dict() before any write.
    data = dict(player_data)
    state = sanitize_stronghold_player_safety_state_pure(
        data.get("stronghold_player_safety")
    )
    data["stronghold_player_safety"] = state
    if state["stage"] >= len(STRONGHOLD_LANDMARKS):
        return data, False, {"reason": "The reward-chest route is complete."}
    landmark = STRONGHOLD_LANDMARKS[state["stage"]]
    state["stage"] += 1
    if state["stage"] >= 2:
        state["crevice_unlocked"] = True
    state["last_result"] = str(landmark["result"])
    return data, True, {
        "action_id": str(landmark["id"]),
        "stage": state["stage"],
        "status": state["last_result"],
        "terminal": state["stage"] == len(STRONGHOLD_LANDMARKS),
    }


def apply_stronghold_player_safety_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: sanitize_stronghold_player_safety_state_pure returns
    # a fresh state, and inventory is rebuilt with dict() before any write.
    data = dict(player_data)
    state = sanitize_stronghold_player_safety_state_pure(
        data.get("stronghold_player_safety")
    )
    data["stronghold_player_safety"] = state
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "claim_chest":
        if state["stage"] != len(STRONGHOLD_LANDMARKS):
            return data, False, {"reason": "Reach the reward chest first."}
        if state["chest_claimed"]:
            return data, False, {"reason": "The one-time chest reward is already claimed."}
        inventory = dict(data.get("inventory", {}) or {})
        inventory["Coins"] = _int(inventory.get("Coins")) + 10_000
        inventory[SAFETY_GLOVES_ITEM] = _int(inventory.get(SAFETY_GLOVES_ITEM)) + 1
        data["inventory"] = inventory
        state["chest_claimed"] = True
        state["lamps_remaining"] = 2
        state["safety_first_emote_unlocked"] = True
        state["last_result"] = (
            "Opened the chest · 10,000 coins, Safety gloves, two 500-XP lamps, "
            "and the Safety First emote."
        )
        return data, True, {
            "items": {"Coins": 10_000, SAFETY_GLOVES_ITEM: 1},
            "lamps": 2,
            "message": state["last_result"],
        }

    if action_id == "claim_lamp":
        if state["lamps_remaining"] <= 0:
            return data, False, {"reason": "No Stronghold XP lamp remains."}
        skill_id = str(payload.get("skill_id", ""))
        skill = get_skill(skill_id)
        if skill is None or not skill.trainable:
            return data, False, {"reason": "Choose a trainable skill."}
        data[skill.exp_key] = float(data.get(skill.exp_key, 0.0) or 0.0) + 500.0
        state["lamps_remaining"] -= 1
        state["last_result"] = f"Used a 500-XP lamp on {skill.display_name}."
        return data, True, {
            "skill_id": skill.id,
            "xp": {skill.id: 500.0},
            "message": state["last_result"],
        }

    if action_id == "reclaim_gloves":
        if not state["chest_claimed"]:
            return data, False, {"reason": "Claim the reward chest first."}
        if _owns_item(data, SAFETY_GLOVES_ITEM):
            return data, False, {"reason": "You still own Safety gloves."}
        inventory = dict(data.get("inventory", {}) or {})
        inventory[SAFETY_GLOVES_ITEM] = 1
        data["inventory"] = inventory
        state["last_result"] = "Reclaimed Safety gloves from the chest."
        return data, True, {
            "items": {SAFETY_GLOVES_ITEM: 1},
            "message": state["last_result"],
        }

    if action_id == "start_soldier_fight":
        if state["stage"] < 2:
            return data, False, {"reason": "Reach the soldier room first."}
        activity_session = data.get("activity_session")
        if (
            isinstance(activity_session, Mapping)
            and activity_session.get("active_id")
        ):
            return data, False, {
                "reason": "Finish or leave the active persistent activity first."
            }
        encounter = data.get("combat_encounter")
        if isinstance(encounter, Mapping) and encounter.get("target_id"):
            return data, False, {"reason": "Finish or leave the current Combat encounter first."}
        data["current_combat_target"] = COCKROACH_SOLDIER_TARGET_ID
        data["combat_action"] = "attack"
        data["combat_encounter"] = {
            "target_id": COCKROACH_SOLDIER_TARGET_ID,
            "enemy_lifepoints": 960,
        }
        state["last_result"] = "Entered a repeatable Cockroach soldier encounter."
        return data, True, {
            "target_id": COCKROACH_SOLDIER_TARGET_ID,
            "switch_skill": "Combat",
            "message": state["last_result"],
        }

    return data, False, {"reason": "Unknown Stronghold command."}
