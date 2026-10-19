"""Pure Summoning transactions and follower lifecycle."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any, Callable, Optional

from ..data.item_values import STACKABLE_ITEM_NAMES
from .pet_logic import advance_active_pet_pure, sanitize_pet_instances_pure
from ..data.summoning_data import (
    DEFAULT_SUMMONING_TARGET,
    SUMMONING_ACTIONS_BY_ID,
    SUMMONING_POUCHES_BY_ID,
    SUMMONING_POUCHES_BY_NAME,
)
from .pace.short_timers import STEP_TICKS, cards_for_ticks_pure
from .pace.summoning_clock import (
    SPECIAL_MOVE_POINTS_MAX,
    TRIPLE_CHARM_TIMER_KEY,
    advance_summoning_timers,
    drop_familiar_storage,
    familiar_lifetime,
    renewal_window_open,
    sanitize_cargo_events,
    sanitize_familiar_timers,
    sanitize_summoning_timers,
    triple_charm_duration,
)


FAMILIARISATION_COOLDOWN_REVIEWS = 1680
FAMILIARISATION_MAX_SEGMENTS = 4
FAMILIARISATION_SHARDS_PER_SUCCESS = 15
FAMILIARISATION_SHARD_CAP = 60
FAMILIARISATION_ACTIVITY_ID = "familiarisation"
FAMILIARISATION_INGREDIENT_REWARD_ROWS = (
    {
        "minimum_level": 1,
        "source_shards": 40,
        "items": {"Raw rabbit": 27, "Raw beef": 42},
    },
    {
        "minimum_level": 48,
        "source_shards": 60,
        "items": {"Raw shark": 19, "Goat horn dust": 22},
    },
)
_FAMILIAR_SKILL_ROLL_BOOSTS = {
    ("lavatitan", "mining"): 10,
    ("lavatitan", "firemaking"): 10,
    ("arcticbear", "hunter"): 7,
    ("granitelobster", "fishing"): 4,
    ("beaver", "woodcutting"): 2,
}
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
        "raw_shards": 0,
        "awaiting_reward": False,
        "cooldown_reviews_remaining": 0,
        "reward_sequence": 0,
    }


def default_summoning_state_pure() -> dict[str, Any]:
    return {
        "summoning_points_current": 1,
        "special_move_points_current": SPECIAL_MOVE_POINTS_MAX,
        "special_move_recharge_residual": 0,
        "active_follower": {},
        "target_policies": {},
        "cargo_events": [],
        "cargo_next_event_id": 1,
        "pet_instances": {},
        "pet_next_instance_id": 1,
        TRIPLE_CHARM_TIMER_KEY: 0,
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
    sanitize_familiar_timers(clean)
    clean["lifepoints"] = _clean_int(raw.get("lifepoints"), 0, minimum=0)
    clean["max_lifepoints"] = _clean_int(
        raw.get("max_lifepoints"), clean["lifepoints"], minimum=0
    )
    clean["storage"] = _clean_inventory(raw.get("storage"))
    clean["hidden_in_spirit_plane"] = bool(raw.get("hidden_in_spirit_plane", False))
    clean["policy_lapse_reason"] = str(raw.get("policy_lapse_reason", ""))
    return clean


def _sanitize_familiarisation(raw: Any) -> dict[str, Any]:
    default = default_familiarisation_state_pure()
    if not isinstance(raw, Mapping):
        return default
    active = bool(raw.get("active", False))
    segments = _clean_int(
        raw.get("segments"), 0, minimum=0, maximum=FAMILIARISATION_MAX_SEGMENTS
    )
    shards = _clean_int(
        raw.get("raw_shards"),
        0,
        minimum=0,
        maximum=FAMILIARISATION_SHARD_CAP,
    )
    awaiting = bool(raw.get("awaiting_reward", False))
    if active:
        # Older sessions counted Again as a segment; only earned shards record success.
        segments = shards // FAMILIARISATION_SHARDS_PER_SUCCESS
    if active and segments >= FAMILIARISATION_MAX_SEGMENTS:
        active = False
        awaiting = True
    return {
        "active": active,
        "segments": segments,
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
    events = sanitize_cargo_events(source.get("cargo_events"))
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
    instances = sanitize_pet_instances_pure(source.get("pet_instances"))
    active_follower = _sanitize_active_follower(
        source.get("active_follower")
    )
    if (
        active_follower.get("kind") == "pet"
        and active_follower.get("entity_id") not in instances
    ):
        active_follower = {}
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
        **sanitize_summoning_timers(source),
        "active_follower": active_follower,
        "target_policies": {
            str(target): dict(policy)
            for target, policy in policies.items()
            if isinstance(target, str) and isinstance(policy, Mapping)
        },
        "cargo_events": events,
        "cargo_next_event_id": next_event,
        "pet_instances": instances,
        "pet_next_instance_id": _clean_int(
            source.get("pet_next_instance_id"), 1, minimum=1
        ),
        "familiarisation": _sanitize_familiarisation(
            source.get("familiarisation")
        ),
        "event_log": [
            copy.deepcopy(dict(entry))
            if isinstance(entry, Mapping)
            else str(entry)
            for entry in event_log[-50:]
        ],
    }


def familiarisation_view_pure(player_data: Mapping[str, Any], speed: int) -> dict[str, Any]:
    """The complete Familiarisation status consumed by every UI surface."""

    state = sanitize_summoning_state_pure(
        player_data.get("summoning_state"),
        summoning_level=_clean_int(player_data.get("summoning_level"), 1, minimum=1),
    )
    activity = state["familiarisation"]
    return {
        **activity,
        "ready": bool(
            not activity["active"]
            and not activity["awaiting_reward"]
            and activity["cooldown_reviews_remaining"] <= 0
        ),
        "triple_charm_reviews_remaining": cards_for_ticks_pure(
            state[TRIPLE_CHARM_TIMER_KEY], speed
        ),
        "max_segments": FAMILIARISATION_MAX_SEGMENTS,
        "shard_cap": FAMILIARISATION_SHARD_CAP,
    }


def familiar_reviews_remaining_pure(follower: Mapping[str, Any], speed: int) -> int:
    """The cards a familiar still lasts at this game speed."""
    timers = dict(follower)
    sanitize_familiar_timers(timers)
    return cards_for_ticks_pure(timers["remaining_ticks"], speed)


def triple_charms_active_pure(player_data: Mapping[str, Any]) -> bool:
    state = player_data.get("summoning_state")
    return (
        isinstance(state, Mapping)
        and sanitize_summoning_timers(state)[TRIPLE_CHARM_TIMER_KEY] > 0
    )


def _copy_player_data(player_data: Mapping[str, Any]) -> dict[str, Any]:
    # Shallow on purpose: callers replace whole keys rather than writing through
    # nested values, and a whole-save deep copy cost 2.07 ms on every review.
    return dict(player_data)


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
) -> tuple[dict[str, Any], bool, dict[str, int]]:
    """Refill to the level; a sanitizing-only change restores zero points."""
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    restored = level - state["summoning_points_current"]
    state["summoning_points_current"] = level
    updated["summoning_state"] = state
    return updated, updated != player_data, {"summoning_points_restored": restored}


def familiar_effective_roll_level_pure(
    player_data: Mapping[str, Any],
    skill_id: str,
    base_level: Any,
) -> int:
    """Apply a live familiar's sourced invisible boost to success rolls only."""
    base = _clean_int(base_level, 1, minimum=1)
    state = player_data.get("summoning_state", {}) or {}
    follower = state.get("active_follower", {}) or {}
    if follower.get("kind") != "familiar":
        return base
    boost = _FAMILIAR_SKILL_ROLL_BOOSTS.get(
        (str(follower.get("entity_id", "")), str(skill_id)),
        0,
    )
    return base + boost


def set_winter_storage_priority_pure(
    player_data: Mapping[str, Any],
    target_id: str,
    item_name: str,
    threshold_free_slots: Any = 0,
) -> tuple[dict[str, Any], bool]:
    if not target_id:
        return dict(player_data), False
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    policies = dict(state.get("target_policies", {}) or {})
    policy = dict(policies.get(target_id, {}) or {})
    if item_name:
        carried = (updated.get("carried_inventory", {}) or {}).get(
            target_id, {}
        )
        if (
            not isinstance(carried, Mapping)
            or _clean_int(carried.get(item_name), 0, minimum=0) <= 0
        ):
            return dict(player_data), False
        policy["winter_storage_priority"] = [item_name]
        advanced = bool(
            (updated.get("carried_advanced_targets", {}) or {}).get(target_id)
        )
        policy["winter_storage_threshold_free_slots"] = (
            _clean_int(threshold_free_slots, 0, minimum=0, maximum=27)
            if advanced
            else 0
        )
    else:
        policy.pop("winter_storage_priority", None)
        policy.pop("winter_storage_threshold_free_slots", None)
    policies[target_id] = policy
    state["target_policies"] = policies
    updated["summoning_state"] = state
    return updated, True


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
        **familiar_lifetime(pouch),
        "lifepoints": pouch.lifepoints or 0,
        "max_lifepoints": pouch.lifepoints or 0,
        "storage": {},
        "hidden_in_spirit_plane": False,
        "policy_lapse_reason": "",
        "bunyip_heal_residual": 0,
    }
    updated["inventory"] = inventory
    updated["summoning_state"] = state
    return updated, True, {
        "reason": "summoned",
        "familiar_id": pouch.id,
        "summon_xp": pouch.summon_xp,
    }


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
    cargo_event = drop_familiar_storage(state, follower, source="dismissal")
    familiar_id = str(follower["entity_id"])
    state["active_follower"] = {}
    updated["summoning_state"] = state
    return updated, True, {
        "reason": "dismissed",
        "familiar_id": familiar_id,
        "cargo_event": cargo_event,
    }


def apply_follower_player_death_pure(
    player_data: Mapping[str, Any],
    *,
    protected_carried_pet_id: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply the unsafe-death follower boundary without creating pet graves."""

    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    follower = state["active_follower"]
    result = {
        "lost_pet_ids": [],
        "familiar_id": None,
        "cargo_event": None,
    }
    instances = dict(state.get("pet_instances", {}) or {})
    if follower.get("kind") == "pet":
        instance_id = str(follower.get("entity_id", ""))
        if instance_id in instances:
            del instances[instance_id]
            result["lost_pet_ids"].append(instance_id)
    elif follower.get("kind") == "familiar":
        result["familiar_id"] = str(follower.get("entity_id", ""))
        result["cargo_event"] = drop_familiar_storage(
            state, follower, source="player_death"
        )
    for instance_id, instance in tuple(instances.items()):
        if (
            instance.get("location") == "carried"
            and instance_id != protected_carried_pet_id
        ):
            del instances[instance_id]
            result["lost_pet_ids"].append(instance_id)
    state["pet_instances"] = instances
    state["active_follower"] = {}
    if result["lost_pet_ids"] or result["familiar_id"]:
        state["event_log"] = (
            list(state.get("event_log", []))
            + [
                {
                    "kind": "unsafe_player_death",
                    "lost_pet_ids": list(result["lost_pet_ids"]),
                    "familiar_id": result["familiar_id"],
                }
            ]
        )[-50:]
    updated["summoning_state"] = state
    return updated, result


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
    if not renewal_window_open(follower):
        return dict(player_data), False, {"reason": "too_early"}
    inventory = dict(updated.get("inventory", {}) or {})
    if _clean_int(inventory.get(pouch.pouch_name), 0, minimum=0) <= 0:
        return dict(player_data), False, {"reason": "missing_pouch"}
    inventory[pouch.pouch_name] -= 1
    follower.update(familiar_lifetime(pouch))
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
    activity_session = updated.get("activity_session")
    active_activity_id = (
        str(activity_session.get("active_id", ""))
        if isinstance(activity_session, Mapping)
        else ""
    )
    if active_activity_id not in {"", FAMILIARISATION_ACTIVITY_ID}:
        return dict(player_data), False
    state["familiarisation"] = {
        "active": True,
        "segments": 0,
        "raw_shards": 0,
        "awaiting_reward": False,
        "cooldown_reviews_remaining": FAMILIARISATION_COOLDOWN_REVIEWS,
        "reward_sequence": activity["reward_sequence"],
    }
    updated["summoning_state"] = state
    updated["activity_session"] = {"active_id": FAMILIARISATION_ACTIVITY_ID}
    return updated, True


def claim_familiarisation_reward_pure(
    player_data: Mapping[str, Any],
    choice: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if choice not in {"ingredients", "triple_charms"}:
        return dict(player_data), False, {"reason": "unknown_reward"}
    updated = _copy_player_data(player_data)
    level = _clean_int(updated.get("summoning_level"), 1, minimum=1)
    state = sanitize_summoning_state_pure(
        updated.get("summoning_state"), summoning_level=level
    )
    activity = dict(state["familiarisation"])
    if not activity["awaiting_reward"]:
        return dict(player_data), False, {"reason": "reward_unavailable"}
    shards = _clean_int(activity.get("raw_shards"), 0, minimum=0)
    sequence = _clean_int(activity.get("reward_sequence"), 0, minimum=0)
    result: dict[str, Any] = {
        "reason": "reward_claimed",
        "choice": choice,
        "raw_shards": shards,
    }
    if choice == "triple_charms":
        ticks = triple_charm_duration(shards)
        state[TRIPLE_CHARM_TIMER_KEY] = max(state[TRIPLE_CHARM_TIMER_KEY], ticks)
        result["ticks"] = ticks
    else:
        reward_row = max(
            (
                row
                for row in FAMILIARISATION_INGREDIENT_REWARD_ROWS
                if level >= int(row["minimum_level"])
            ),
            key=lambda row: int(row["minimum_level"]),
        )
        awarded: dict[str, int] = {}
        source_shards = int(reward_row["source_shards"])
        if shards > 0:
            inventory = dict(updated.get("inventory", {}) or {})
            for item_name, source_amount in reward_row["items"].items():
                amount = max(1, int(source_amount) * shards // source_shards)
                inventory[item_name] = _clean_int(
                    inventory.get(item_name), 0, minimum=0
                ) + amount
                awarded[item_name] = amount
            updated["inventory"] = inventory
        result["ingredients"] = awarded
        result["ingredient_tier_level"] = int(reward_row["minimum_level"])
        result["source_shards"] = source_shards
    activity["awaiting_reward"] = False
    activity["reward_sequence"] = sequence + 1
    state["familiarisation"] = activity
    updated["summoning_state"] = state
    activity_session = updated.get("activity_session")
    if (
        isinstance(activity_session, Mapping)
        and str(activity_session.get("active_id", ""))
        == FAMILIARISATION_ACTIVITY_ID
    ):
        updated["activity_session"] = {"active_id": ""}
    return updated, True, result


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
    activity_session = updated.get("activity_session")
    active_activity_id = (
        str(activity_session.get("active_id", ""))
        if isinstance(activity_session, Mapping)
        else ""
    )
    if active_activity_id not in {"", FAMILIARISATION_ACTIVITY_ID}:
        return dict(player_data), False, {"reason": "activity_conflict"}
    if successful_answer:
        activity["segments"] += 1
        activity["raw_shards"] = min(
            FAMILIARISATION_SHARD_CAP,
            activity["raw_shards"] + FAMILIARISATION_SHARDS_PER_SUCCESS,
        )
    ended = activity["segments"] >= FAMILIARISATION_MAX_SEGMENTS
    if ended:
        activity["active"] = False
        activity["awaiting_reward"] = True
    state["familiarisation"] = activity
    updated["summoning_state"] = state
    updated["activity_session"] = {"active_id": FAMILIARISATION_ACTIVITY_ID}
    return updated, True, {
        "reason": "segment",
        "ended": ended,
        "segments": activity["segments"],
        "raw_shards": activity["raw_shards"],
    }


def _advance_familiarisation_world_tick(
    player_data: dict[str, Any], state: dict[str, Any], successful_answer: Optional[bool]
) -> tuple[dict[str, Any], Optional[dict[str, Any]]]:
    activity = dict(state["familiarisation"])
    activity["cooldown_reviews_remaining"] = max(
        0, activity["cooldown_reviews_remaining"] - 1
    )
    state["familiarisation"] = activity
    player_data["summoning_state"] = state
    if not activity["active"] or successful_answer is None:
        return player_data, None
    updated, ok, result = apply_familiarisation_segment_pure(
        player_data, successful_answer=successful_answer
    )
    if ok:
        del result["reason"]
    return updated, result


def advance_summoning_world_tick_pure(
    player_data: Mapping[str, Any],
    *,
    successful_answer: Optional[bool] = None,
    active_carried_target: Optional[str] = None,
    card_ticks: int = STEP_TICKS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Advance the Summoning world over one answered card's time budget."""
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
        "passive_healing": 0,
        "pet": None,
    }

    updated, familiarisation_result = _advance_familiarisation_world_tick(
        updated, state, successful_answer
    )
    state = updated["summoning_state"]
    if familiarisation_result is not None:
        result["familiarisation"] = familiarisation_result
    timers = advance_summoning_timers(updated, state, card_ticks)
    result["lost_cargo_events"] = timers["lost_cargo_events"]
    result["passive_healing"] = timers["passive_healing"]
    if expired := timers["expired"]:
        result["expired_familiar"] = expired["entity_id"]
        result["expired_cargo_event"] = drop_familiar_storage(
            state, expired, source="expiry"
        )
        state["active_follower"] = {}

    updated["summoning_state"] = state
    if state["active_follower"].get("kind") == "pet":
        updated, pet_result = advance_active_pet_pure(
            updated,
            active_carried_target=active_carried_target,
        )
        result["pet"] = pet_result
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


assert DEFAULT_SUMMONING_TARGET in SUMMONING_ACTIONS_BY_ID
