"""Pure Summoning transactions and follower lifecycle."""

from __future__ import annotations

import copy
import math
from collections.abc import Mapping
from typing import Any, Callable, Optional

try:
    from .item_values import STACKABLE_ITEM_NAMES
    from .summoning_data import (
        DEFAULT_SUMMONING_TARGET,
        SOURCE_DURATION_UNITS_PER_REVIEW,
        SUMMONING_ACTIONS_BY_ID,
        SUMMONING_POUCHES_BY_ID,
        SUMMONING_POUCHES_BY_NAME,
    )
except ImportError:
    from item_values import STACKABLE_ITEM_NAMES
    from summoning_data import (
        DEFAULT_SUMMONING_TARGET,
        SOURCE_DURATION_UNITS_PER_REVIEW,
        SUMMONING_ACTIONS_BY_ID,
        SUMMONING_POUCHES_BY_ID,
        SUMMONING_POUCHES_BY_NAME,
    )


SPECIAL_MOVE_POINTS_MAX = 60
SPECIAL_MOVE_POINT_RECOVERY_PER_REVIEW = SPECIAL_MOVE_POINTS_MAX
CARGO_RECLAIM_SOURCE_MINUTES = 5
CARGO_RECLAIM_REVIEWS = math.ceil(
    CARGO_RECLAIM_SOURCE_MINUTES / SOURCE_DURATION_UNITS_PER_REVIEW
)
FAMILIARISATION_COOLDOWN_REVIEWS = 1680
FAMILIARISATION_MAX_SEGMENTS = 4
FAMILIARISATION_STARTING_FOCUS = 3
FAMILIARISATION_SHARDS_PER_SUCCESS = 15
FAMILIARISATION_SHARD_CAP = 60
_ESSENCE_ONLY_FAMILIARS = frozenset(
    {"abyssalparasite", "abyssallurker", "abyssaltitan"}
)
_BLANK_ESSENCE_NAMES = frozenset({"Rune essence", "Pure essence"})


def _clean_int(
    value: Any,
    default: int = 0,
    *,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
) -> int:
    try:
        clean = int(value)
    except (TypeError, ValueError, OverflowError):
        clean = default
    if minimum is not None:
        clean = max(minimum, clean)
    if maximum is not None:
        clean = min(maximum, clean)
    return clean


def _clean_inventory(raw: Any) -> dict[str, int]:
    if not isinstance(raw, Mapping):
        return {}
    return {
        str(item_name): _clean_int(amount, 0, minimum=0)
        for item_name, amount in raw.items()
        if isinstance(item_name, str) and _clean_int(amount, 0, minimum=0) > 0
    }


def default_familiarisation_state_pure() -> dict[str, Any]:
    return {
        "active": False,
        "segments": 0,
        "focus": FAMILIARISATION_STARTING_FOCUS,
        "raw_shards": 0,
        "awaiting_reward": False,
        "cooldown_reviews_remaining": 0,
        "reward_sequence": 0,
    }


def default_summoning_state_pure() -> dict[str, Any]:
    return {
        "summoning_points_current": 1,
        "special_move_points_current": SPECIAL_MOVE_POINTS_MAX,
        "active_follower": {},
        "target_policies": {},
        "cargo_events": [],
        "cargo_next_event_id": 1,
        "familiarisation": default_familiarisation_state_pure(),
        "event_log": [],
    }


def _sanitize_active_follower(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    kind = str(raw.get("kind", ""))
    entity_id = str(raw.get("entity_id", ""))
    if kind not in {"familiar", "pet"} or not entity_id:
        return {}
    if kind == "familiar" and entity_id not in SUMMONING_POUCHES_BY_ID:
        return {}
    clean = dict(raw)
    clean["kind"] = kind
    clean["entity_id"] = entity_id
    clean["remaining_reviews"] = _clean_int(
        raw.get("remaining_reviews"), 0, minimum=0
    )
    clean["max_reviews"] = _clean_int(
        raw.get("max_reviews"), clean["remaining_reviews"], minimum=0
    )
    clean["lifepoints"] = _clean_int(raw.get("lifepoints"), 0, minimum=0)
    clean["max_lifepoints"] = _clean_int(
        raw.get("max_lifepoints"), clean["lifepoints"], minimum=0
    )
    clean["storage"] = _clean_inventory(raw.get("storage"))
    clean["hidden_in_spirit_plane"] = bool(raw.get("hidden_in_spirit_plane", False))
    clean["policy_lapse_reason"] = str(raw.get("policy_lapse_reason", ""))
    return clean


def _sanitize_cargo_events(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, (list, tuple)):
        return []
    events: list[dict[str, Any]] = []
    seen: set[int] = set()
    for candidate in raw:
        if not isinstance(candidate, Mapping):
            continue
        event_id = _clean_int(candidate.get("event_id"), 0, minimum=1)
        items = _clean_inventory(candidate.get("items"))
        remaining = _clean_int(
            candidate.get("remaining_reviews"), 0, minimum=0
        )
        if event_id in seen or not items or remaining <= 0:
            continue
        seen.add(event_id)
        events.append(
            {
                "event_id": event_id,
                "familiar_id": str(candidate.get("familiar_id", "")),
                "items": items,
                "remaining_reviews": remaining,
                "source": str(candidate.get("source", "expiry")),
            }
        )
    return sorted(events, key=lambda event: event["event_id"])[-20:]


def _sanitize_familiarisation(raw: Any) -> dict[str, Any]:
    default = default_familiarisation_state_pure()
    if not isinstance(raw, Mapping):
        return default
    active = bool(raw.get("active", False))
    segments = _clean_int(
        raw.get("segments"), 0, minimum=0, maximum=FAMILIARISATION_MAX_SEGMENTS
    )
    focus = _clean_int(
        raw.get("focus"),
        FAMILIARISATION_STARTING_FOCUS,
        minimum=0,
        maximum=FAMILIARISATION_STARTING_FOCUS,
    )
    shards = _clean_int(
        raw.get("raw_shards"),
        0,
        minimum=0,
        maximum=FAMILIARISATION_SHARD_CAP,
    )
    awaiting = bool(raw.get("awaiting_reward", False))
    if active and (
        segments >= FAMILIARISATION_MAX_SEGMENTS
        or focus <= 0
        or shards >= FAMILIARISATION_SHARD_CAP
    ):
        active = False
        awaiting = True
    return {
        "active": active,
        "segments": segments,
        "focus": focus,
        "raw_shards": shards,
        "awaiting_reward": awaiting,
        "cooldown_reviews_remaining": _clean_int(
            raw.get("cooldown_reviews_remaining"), 0, minimum=0
        ),
        "reward_sequence": _clean_int(
            raw.get("reward_sequence"), 0, minimum=0
        ),
    }


def sanitize_summoning_state_pure(
    raw: Any,
    *,
    summoning_level: int = 1,
) -> dict[str, Any]:
    default = default_summoning_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    maximum = max(1, _clean_int(summoning_level, 1, minimum=1))
    events = _sanitize_cargo_events(source.get("cargo_events"))
    next_event = max(
        _clean_int(source.get("cargo_next_event_id"), 1, minimum=1),
        max((event["event_id"] for event in events), default=0) + 1,
    )
    policies = source.get("target_policies")
    if not isinstance(policies, Mapping):
        policies = {}
    event_log = source.get("event_log")
    if not isinstance(event_log, (list, tuple)):
        event_log = []
    return {
        "summoning_points_current": _clean_int(
            source.get("summoning_points_current"),
            default["summoning_points_current"],
            minimum=0,
            maximum=maximum,
        ),
        "special_move_points_current": _clean_int(
            source.get("special_move_points_current"),
            SPECIAL_MOVE_POINTS_MAX,
            minimum=0,
            maximum=SPECIAL_MOVE_POINTS_MAX,
        ),
        "active_follower": _sanitize_active_follower(
            source.get("active_follower")
        ),
        "target_policies": {
            str(target): dict(policy)
            for target, policy in policies.items()
            if isinstance(target, str) and isinstance(policy, Mapping)
        },
        "cargo_events": events,
        "cargo_next_event_id": next_event,
        "familiarisation": _sanitize_familiarisation(
            source.get("familiarisation")
        ),
        "event_log": [str(entry) for entry in event_log[-50:]],
    }


def _copy_player_data(player_data: Mapping[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(dict(player_data))


def _selected_tertiary(
    pouch: Any,
    inventory: Mapping[str, Any],
) -> Optional[str]:
    if pouch.tertiary_mode == "all":
        return None
    return next(
        (
            item_name
            for item_name in pouch.tertiaries
            if _clean_int(inventory.get(item_name), 0, minimum=0) > 0
        ),
        pouch.tertiaries[0] if pouch.tertiaries else None,
    )


def summoning_action_requirements_pure(
    player_data: Mapping[str, Any],
    target_id: str,
    *,
    inventory_override: Optional[Mapping[str, Any]] = None,
) -> dict[str, int]:
    action = SUMMONING_ACTIONS_BY_ID.get(target_id)
    if action is None:
        return {}
    inventory = (
        inventory_override
        if isinstance(inventory_override, Mapping)
        else player_data.get("inventory", {})
    )
    if not isinstance(inventory, Mapping):
        inventory = {}
    if action.family == "scroll":
        input_item = next(
            (
                item_name
                for item_name in action.input_items
                if _clean_int(inventory.get(item_name), 0, minimum=0) > 0
            ),
            action.input_items[0],
        )
        return {input_item: 1}
    pouch = SUMMONING_POUCHES_BY_ID[action.familiar_id]
    requirements = {
        "Pouch": 1,
        "Spirit shards": pouch.shards,
    }
    if pouch.charm:
        requirements[pouch.charm] = 1
    if pouch.tertiary_mode == "all":
        requirements.update({item_name: 1 for item_name in pouch.tertiaries})
    else:
        selected = _selected_tertiary(pouch, inventory)
        if selected:
            requirements[selected] = 1
    return requirements


def summoning_action_locked_reasons_pure(
    player_data: Mapping[str, Any],
    target_id: str,
    *,
    inventory_override: Optional[Mapping[str, Any]] = None,
) -> tuple[str, ...]:
    action = SUMMONING_ACTIONS_BY_ID.get(target_id)
    if action is None:
        return ("Unknown Summoning target",)
    reasons: list[str] = []
    level = _clean_int(player_data.get("summoning_level"), 1, minimum=1)
    if level < action.level:
        reasons.append(f"Summoning level {action.level}")
    inventory = (
        inventory_override
        if isinstance(inventory_override, Mapping)
        else player_data.get("inventory", {})
    )
    if not isinstance(inventory, Mapping):
        inventory = {}
    requirements = summoning_action_requirements_pure(
        player_data, target_id, inventory_override=inventory
    )
    missing = [
        item_name
        for item_name, amount in requirements.items()
        if _clean_int(inventory.get(item_name), 0, minimum=0) < amount
    ]
    if missing:
        reasons.append("Missing " + ", ".join(missing))
    return tuple(reasons)


def apply_summoning_training_action_pure(
    player_data: Mapping[str, Any],
    target_id: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    action = SUMMONING_ACTIONS_BY_ID.get(target_id)
    if action is None:
        return dict(player_data), False, {"reason": "unknown_target"}
    reasons = summoning_action_locked_reasons_pure(player_data, target_id)
    if reasons:
        return dict(player_data), False, {
            "reason": "locked",
            "locked_reasons": reasons,
        }
    updated = _copy_player_data(player_data)
    inventory = dict(updated.get("inventory", {}) or {})
    requirements = summoning_action_requirements_pure(updated, target_id)
    for item_name, amount in requirements.items():
        inventory[item_name] = _clean_int(
            inventory.get(item_name), 0, minimum=0
        ) - amount
    inventory[action.output_item] = (
        _clean_int(inventory.get(action.output_item), 0, minimum=0)
        + action.output_quantity
    )
    updated["inventory"] = inventory
    return updated, True, {
        "action_id": action.id,
        "family": action.family,
        "xp": action.xp,
        "output_item": action.output_item,
        "output_quantity": action.output_quantity,
        "requirements": requirements,
    }


def restore_summoning_points_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    updated = _copy_player_data(player_data)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"),
        summoning_level=_clean_int(updated.get("summoning_level"), 1, minimum=1),
    )
    state["summoning_points_current"] = max(
        1, _clean_int(updated.get("summoning_level"), 1, minimum=1)
    )
    updated["summoning_state"] = state
    return updated


def summon_familiar_pure(
    player_data: Mapping[str, Any],
    familiar_id: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    pouch = SUMMONING_POUCHES_BY_ID.get(familiar_id)
    if pouch is None:
        return dict(player_data), False, {"reason": "unknown_familiar"}
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    if state["active_follower"]:
        return dict(player_data), False, {"reason": "follower_slot_occupied"}
    if level < pouch.level:
        return dict(player_data), False, {
            "reason": "level",
            "required_level": pouch.level,
        }
    inventory = dict(updated.get("inventory", {}) or {})
    if _clean_int(inventory.get(pouch.pouch_name), 0, minimum=0) <= 0:
        return dict(player_data), False, {"reason": "missing_pouch"}
    if state["summoning_points_current"] < pouch.summoning_point_cost:
        return dict(player_data), False, {
            "reason": "summoning_points",
            "required_points": pouch.summoning_point_cost,
        }
    inventory[pouch.pouch_name] -= 1
    state["summoning_points_current"] -= pouch.summoning_point_cost
    state["active_follower"] = {
        "kind": "familiar",
        "entity_id": pouch.id,
        "remaining_reviews": pouch.lifetime_reviews,
        "max_reviews": pouch.lifetime_reviews,
        "lifepoints": pouch.lifepoints or 0,
        "max_lifepoints": pouch.lifepoints or 0,
        "storage": {},
        "hidden_in_spirit_plane": False,
        "policy_lapse_reason": "",
    }
    updated["inventory"] = inventory
    updated["summoning_state"] = state
    return updated, True, {
        "reason": "summoned",
        "familiar_id": pouch.id,
        "summon_xp": pouch.summon_xp,
    }


def _drop_familiar_storage(
    state: dict[str, Any],
    follower: Mapping[str, Any],
    *,
    source: str,
) -> Optional[dict[str, Any]]:
    storage = _clean_inventory(follower.get("storage"))
    if not storage:
        return None
    event = {
        "event_id": state["cargo_next_event_id"],
        "familiar_id": str(follower.get("entity_id", "")),
        "items": storage,
        "remaining_reviews": CARGO_RECLAIM_REVIEWS,
        "source": source,
    }
    state["cargo_next_event_id"] += 1
    state["cargo_events"].append(event)
    state["cargo_events"] = state["cargo_events"][-20:]
    return event


def dismiss_familiar_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    follower = state["active_follower"]
    if follower.get("kind") != "familiar":
        return dict(player_data), False, {"reason": "no_active_familiar"}
    cargo_event = _drop_familiar_storage(state, follower, source="dismissal")
    familiar_id = str(follower["entity_id"])
    state["active_follower"] = {}
    updated["summoning_state"] = state
    return updated, True, {
        "reason": "dismissed",
        "familiar_id": familiar_id,
        "cargo_event": cargo_event,
    }


def renew_familiar_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    follower = state["active_follower"]
    if follower.get("kind") != "familiar":
        return dict(player_data), False, {"reason": "no_active_familiar"}
    pouch = SUMMONING_POUCHES_BY_ID.get(str(follower["entity_id"]))
    if pouch is None:
        return dict(player_data), False, {"reason": "unknown_familiar"}
    if follower["remaining_reviews"] > pouch.renewal_window_reviews:
        return dict(player_data), False, {"reason": "too_early"}
    inventory = dict(updated.get("inventory", {}) or {})
    if _clean_int(inventory.get(pouch.pouch_name), 0, minimum=0) <= 0:
        return dict(player_data), False, {"reason": "missing_pouch"}
    inventory[pouch.pouch_name] -= 1
    follower["remaining_reviews"] = pouch.lifetime_reviews
    follower["max_reviews"] = pouch.lifetime_reviews
    follower["lifepoints"] = follower.get("max_lifepoints", pouch.lifepoints or 0)
    state["active_follower"] = follower
    updated["inventory"] = inventory
    updated["summoning_state"] = state
    return updated, True, {"reason": "renewed", "familiar_id": pouch.id}


def familiar_storage_transfer_pure(
    player_data: Mapping[str, Any],
    item_name: str,
    quantity: int,
    *,
    to_familiar: bool,
    in_combat: bool = False,
) -> tuple[dict[str, Any], bool]:
    if in_combat:
        return dict(player_data), False
    amount = _clean_int(quantity, 0, minimum=0)
    if not item_name or amount <= 0:
        return dict(player_data), False
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    follower = state["active_follower"]
    if follower.get("kind") != "familiar":
        return dict(player_data), False
    pouch = SUMMONING_POUCHES_BY_ID.get(str(follower["entity_id"]))
    if pouch is None or pouch.bob_capacity <= 0:
        return dict(player_data), False
    essence_only = pouch.id in _ESSENCE_ONLY_FAMILIARS
    if essence_only != (item_name in _BLANK_ESSENCE_NAMES):
        return dict(player_data), False
    inventory = dict(updated.get("inventory", {}) or {})
    storage = dict(follower.get("storage", {}) or {})
    source = inventory if to_familiar else storage
    destination = storage if to_familiar else inventory
    if _clean_int(source.get(item_name), 0, minimum=0) < amount:
        return dict(player_data), False
    if to_familiar:
        used_slots = sum(
            (
                1
                if stored_name in STACKABLE_ITEM_NAMES
                and stored_name not in _BLANK_ESSENCE_NAMES
                else _clean_int(count, 0, minimum=0)
            )
            for stored_name, count in storage.items()
            if _clean_int(count, 0, minimum=0) > 0
        )
        added_slots = (
            0
            if item_name in storage
            and item_name in STACKABLE_ITEM_NAMES
            and item_name not in _BLANK_ESSENCE_NAMES
            else (
                1
                if item_name in STACKABLE_ITEM_NAMES
                and item_name not in _BLANK_ESSENCE_NAMES
                else amount
            )
        )
        if used_slots + added_slots > pouch.bob_capacity:
            return dict(player_data), False
    source[item_name] = _clean_int(source.get(item_name), 0, minimum=0) - amount
    destination[item_name] = _clean_int(
        destination.get(item_name), 0, minimum=0
    ) + amount
    follower["storage"] = storage
    state["active_follower"] = follower
    updated["inventory"] = inventory
    updated["summoning_state"] = state
    return updated, True


def reclaim_familiar_cargo_pure(
    player_data: Mapping[str, Any],
    event_id: int,
) -> tuple[dict[str, Any], bool, dict[str, int]]:
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    wanted = _clean_int(event_id, 0, minimum=1)
    event = next(
        (candidate for candidate in state["cargo_events"] if candidate["event_id"] == wanted),
        None,
    )
    if event is None:
        return dict(player_data), False, {}
    inventory = dict(updated.get("inventory", {}) or {})
    for item_name, amount in event["items"].items():
        inventory[item_name] = _clean_int(
            inventory.get(item_name), 0, minimum=0
        ) + amount
    state["cargo_events"] = [
        candidate
        for candidate in state["cargo_events"]
        if candidate["event_id"] != wanted
    ]
    updated["inventory"] = inventory
    updated["summoning_state"] = state
    return updated, True, dict(event["items"])


def start_familiarisation_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool]:
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    activity = state["familiarisation"]
    if (
        activity["active"]
        or activity["awaiting_reward"]
        or activity["cooldown_reviews_remaining"] > 0
    ):
        return dict(player_data), False
    state["familiarisation"] = {
        "active": True,
        "segments": 0,
        "focus": FAMILIARISATION_STARTING_FOCUS,
        "raw_shards": 0,
        "awaiting_reward": False,
        "cooldown_reviews_remaining": FAMILIARISATION_COOLDOWN_REVIEWS,
        "reward_sequence": activity["reward_sequence"],
    }
    updated["summoning_state"] = state
    return updated, True


def apply_familiarisation_segment_pure(
    player_data: Mapping[str, Any],
    *,
    successful_answer: bool,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    activity = dict(state["familiarisation"])
    if not activity["active"]:
        return dict(player_data), False, {"reason": "inactive"}
    activity["segments"] += 1
    if successful_answer:
        activity["raw_shards"] = min(
            FAMILIARISATION_SHARD_CAP,
            activity["raw_shards"] + FAMILIARISATION_SHARDS_PER_SUCCESS,
        )
    else:
        activity["focus"] = max(0, activity["focus"] - 1)
    ended = (
        activity["segments"] >= FAMILIARISATION_MAX_SEGMENTS
        or activity["focus"] <= 0
        or activity["raw_shards"] >= FAMILIARISATION_SHARD_CAP
    )
    if ended:
        activity["active"] = False
        activity["awaiting_reward"] = True
    state["familiarisation"] = activity
    updated["summoning_state"] = state
    return updated, True, {
        "reason": "segment",
        "ended": ended,
        "segments": activity["segments"],
        "focus": activity["focus"],
        "raw_shards": activity["raw_shards"],
    }


def advance_summoning_world_tick_pure(
    player_data: Mapping[str, Any],
    *,
    successful_answer: Optional[bool] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    result: dict[str, Any] = {
        "expired_familiar": None,
        "expired_cargo_event": None,
        "lost_cargo_events": [],
        "familiarisation": None,
    }

    retained_events: list[dict[str, Any]] = []
    for event in state["cargo_events"]:
        event = dict(event)
        event["remaining_reviews"] -= 1
        if event["remaining_reviews"] <= 0:
            result["lost_cargo_events"].append(event)
        else:
            retained_events.append(event)
    state["cargo_events"] = retained_events

    activity = dict(state["familiarisation"])
    activity["cooldown_reviews_remaining"] = max(
        0, activity["cooldown_reviews_remaining"] - 1
    )
    if activity["active"] and successful_answer is not None:
        activity["segments"] += 1
        if successful_answer:
            activity["raw_shards"] = min(
                FAMILIARISATION_SHARD_CAP,
                activity["raw_shards"] + FAMILIARISATION_SHARDS_PER_SUCCESS,
            )
        else:
            activity["focus"] = max(0, activity["focus"] - 1)
        ended = (
            activity["segments"] >= FAMILIARISATION_MAX_SEGMENTS
            or activity["focus"] <= 0
            or activity["raw_shards"] >= FAMILIARISATION_SHARD_CAP
        )
        if ended:
            activity["active"] = False
            activity["awaiting_reward"] = True
        result["familiarisation"] = {
            "ended": ended,
            "segments": activity["segments"],
            "focus": activity["focus"],
            "raw_shards": activity["raw_shards"],
        }
    state["familiarisation"] = activity
    state["special_move_points_current"] = min(
        SPECIAL_MOVE_POINTS_MAX,
        state["special_move_points_current"]
        + SPECIAL_MOVE_POINT_RECOVERY_PER_REVIEW,
    )

    follower = state["active_follower"]
    if follower.get("kind") == "familiar":
        follower = dict(follower)
        follower["remaining_reviews"] = max(
            0, _clean_int(follower.get("remaining_reviews"), 0) - 1
        )
        state["summoning_points_current"] = max(
            0, state["summoning_points_current"] - 1
        )
        if follower["remaining_reviews"] <= 0:
            result["expired_familiar"] = follower["entity_id"]
            result["expired_cargo_event"] = _drop_familiar_storage(
                state, follower, source="expiry"
            )
            state["active_follower"] = {}
        else:
            state["active_follower"] = follower

    updated["summoning_state"] = state
    return updated, result


def use_familiar_special_pure(
    player_data: Mapping[str, Any],
    effect: Callable[[dict[str, Any], Any], tuple[dict[str, Any], bool, Any]],
) -> tuple[dict[str, Any], bool, Any]:
    """Atomically consume a carried matching scroll and special points.

    The effect callback owns source-specific behavior. It receives the copied
    player data and active pouch row; resource costs commit only when the effect
    succeeds.
    """
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    follower = state["active_follower"]
    if follower.get("kind") != "familiar":
        return dict(player_data), False, {"reason": "no_active_familiar"}
    pouch = SUMMONING_POUCHES_BY_ID.get(str(follower["entity_id"]))
    if pouch is None:
        return dict(player_data), False, {"reason": "unknown_familiar"}
    inventory = dict(updated.get("inventory", {}) or {})
    if _clean_int(inventory.get(pouch.scroll_name), 0, minimum=0) <= 0:
        return dict(player_data), False, {"reason": "missing_scroll"}
    if state["special_move_points_current"] < pouch.special_points:
        return dict(player_data), False, {"reason": "special_points"}
    effected, ok, result = effect(updated, pouch)
    if not ok:
        return dict(player_data), False, result
    inventory = dict(effected.get("inventory", {}) or {})
    if _clean_int(inventory.get(pouch.scroll_name), 0, minimum=0) <= 0:
        return dict(player_data), False, {"reason": "scroll_changed"}
    inventory[pouch.scroll_name] -= 1
    effected["inventory"] = inventory
    effected_state = sanitize_summoning_state_pure(
        effected.get("summoning_state"), summoning_level=level
    )
    effected_state["special_move_points_current"] -= pouch.special_points
    effected["summoning_state"] = effected_state
    return effected, True, result


assert CARGO_RECLAIM_REVIEWS == 3
assert DEFAULT_SUMMONING_TARGET in SUMMONING_ACTIONS_BY_ID
