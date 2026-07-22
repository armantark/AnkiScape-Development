"""Pure pet ownership, follower-slot, and review-driven care transactions."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any, Optional

try:
    from .pet_data import (
        PETS_BY_ID,
        PET_ADULT_HUNGER_PER_REVIEW,
        PET_BABY_HUNGER_PER_REVIEW,
        PET_FEED_HUNGER_REDUCTION,
        PET_GROWTH_REVIEWS_PER_STAGE,
        pet_display_foods,
    )
    from .cooking_data import COOKING_TARGETS
    from .fishing_data import fishing_output_items
except ImportError:
    from pet_data import (
        PETS_BY_ID,
        PET_ADULT_HUNGER_PER_REVIEW,
        PET_BABY_HUNGER_PER_REVIEW,
        PET_FEED_HUNGER_REDUCTION,
        PET_GROWTH_REVIEWS_PER_STAGE,
        pet_display_foods,
    )
    from cooking_data import COOKING_TARGETS
    from fishing_data import fishing_output_items


_RAW_FISH = frozenset(fishing_output_items())
_COOKED_FISH = frozenset(
    target.cooked_item for target in COOKING_TARGETS if target.family == "fish"
)
_RAW_MEAT = frozenset(
    target.raw_item for target in COOKING_TARGETS if target.family == "meat"
)


def _clean_int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        return max(minimum, int(value))
    except (TypeError, ValueError, OverflowError):
        return max(minimum, default)


def _clean_float(
    value: Any, default: float = 0.0, *, minimum: float = 0.0, maximum: float = 100.0
) -> float:
    try:
        clean = float(value)
    except (TypeError, ValueError, OverflowError):
        clean = default
    return min(maximum, max(minimum, clean))


def sanitize_pet_instances_pure(raw: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, Mapping):
        return {}
    instances = {}
    for instance_id, candidate in raw.items():
        if not isinstance(instance_id, str) or not isinstance(candidate, Mapping):
            continue
        pet_id = str(candidate.get("pet_id", ""))
        pet = PETS_BY_ID.get(pet_id)
        if pet is None:
            continue
        stage = min(
            _clean_int(candidate.get("stage"), 0),
            max(0, pet.stage_count - 1),
        )
        location = str(candidate.get("location", "bank"))
        if location not in {"bank", "carried", "menagerie", "active"}:
            location = "bank"
        instances[instance_id] = {
            "pet_id": pet_id,
            "stage": stage,
            "growth": _clean_float(candidate.get("growth")),
            "hunger": _clean_float(candidate.get("hunger")),
            "location": location,
            "variant": min(
                _clean_int(candidate.get("variant"), 0),
                max(0, pet.colour_count - 1),
            ),
            "name": str(candidate.get("name", "")),
            "policy_lapse_reason": str(
                candidate.get("policy_lapse_reason", "")
            ),
        }
    return instances


def acquire_pet_pure(
    player_data: Mapping[str, Any],
    pet_id: str,
    *,
    location: str = "bank",
    variant: int = 0,
) -> tuple[dict[str, Any], bool, str]:
    pet = PETS_BY_ID.get(pet_id)
    if pet is None or not pet.obtainable:
        return dict(player_data), False, "unavailable_pet"
    if _clean_int(player_data.get("summoning_level"), 1, minimum=1) < pet.summoning_level:
        return dict(player_data), False, "summoning_level"
    updated = copy.deepcopy(dict(player_data))
    state = dict(updated.get("summoning_state", {}) or {})
    instances = sanitize_pet_instances_pure(state.get("pet_instances"))
    sequence = _clean_int(state.get("pet_next_instance_id"), 1, minimum=1)
    instance_id = f"pet-{sequence}"
    while instance_id in instances:
        sequence += 1
        instance_id = f"pet-{sequence}"
    instances[instance_id] = {
        "pet_id": pet.id,
        "stage": 0,
        "growth": 0.0,
        "hunger": 0.0,
        "location": location if location in {"bank", "carried", "menagerie"} else "bank",
        "variant": min(max(0, int(variant)), max(0, pet.colour_count - 1)),
        "name": "",
        "policy_lapse_reason": "",
    }
    state["pet_instances"] = instances
    state["pet_next_instance_id"] = sequence + 1
    updated["summoning_state"] = state
    return updated, True, instance_id


def let_out_pet_pure(
    player_data: Mapping[str, Any],
    instance_id: str,
) -> tuple[dict[str, Any], bool, str]:
    updated = copy.deepcopy(dict(player_data))
    state = dict(updated.get("summoning_state", {}) or {})
    follower = state.get("active_follower", {}) or {}
    if follower:
        return dict(player_data), False, "follower_slot_occupied"
    instances = sanitize_pet_instances_pure(state.get("pet_instances"))
    instance = instances.get(instance_id)
    if instance is None or instance["location"] == "active":
        return dict(player_data), False, "unknown_pet"
    pet = PETS_BY_ID[instance["pet_id"]]
    if _clean_int(updated.get("summoning_level"), 1, minimum=1) < pet.summoning_level:
        return dict(player_data), False, "summoning_level"
    instance["location"] = "active"
    instance["policy_lapse_reason"] = ""
    instances[instance_id] = instance
    state["pet_instances"] = instances
    state["active_follower"] = {
        "kind": "pet",
        "entity_id": instance_id,
        "remaining_reviews": 0,
        "max_reviews": 0,
        "storage": {},
        "hidden_in_spirit_plane": False,
        "policy_lapse_reason": "",
    }
    updated["summoning_state"] = state
    return updated, True, "active"


def store_active_pet_pure(
    player_data: Mapping[str, Any],
    *,
    location: str = "bank",
) -> tuple[dict[str, Any], bool]:
    if location not in {"bank", "carried", "menagerie"}:
        return dict(player_data), False
    updated = copy.deepcopy(dict(player_data))
    state = dict(updated.get("summoning_state", {}) or {})
    follower = state.get("active_follower", {}) or {}
    if follower.get("kind") != "pet":
        return dict(player_data), False
    instance_id = str(follower.get("entity_id", ""))
    instances = sanitize_pet_instances_pure(state.get("pet_instances"))
    instance = instances.get(instance_id)
    if instance is None:
        return dict(player_data), False
    instance["location"] = location
    instances[instance_id] = instance
    state["pet_instances"] = instances
    state["active_follower"] = {}
    updated["summoning_state"] = state
    return updated, True


def release_pet_pure(
    player_data: Mapping[str, Any],
    instance_id: str,
) -> tuple[dict[str, Any], bool, str]:
    updated = copy.deepcopy(dict(player_data))
    state = dict(updated.get("summoning_state", {}) or {})
    instances = sanitize_pet_instances_pure(state.get("pet_instances"))
    instance = instances.get(instance_id)
    if instance is None:
        return dict(player_data), False, "unknown_pet"
    pet = PETS_BY_ID[instance["pet_id"]]
    if pet.release_source_blocked:
        return dict(player_data), False, "reacquisition_source_blocked"
    follower = state.get("active_follower", {}) or {}
    if (
        follower.get("kind") == "pet"
        and follower.get("entity_id") == instance_id
    ):
        state["active_follower"] = {}
    del instances[instance_id]
    state["pet_instances"] = instances
    updated["summoning_state"] = state
    return updated, True, "released"


def hatch_phoenix_egg_pure(
    player_data: Mapping[str, Any],
    item_name: str,
) -> tuple[dict[str, Any], bool, str]:
    """Hatch a banked Phoenix egg once the source Summoning gate is met."""

    egg_to_pet = {
        "Phoenix egg": "cute_phoenix_eggling",
        "Cracked phoenix egg": "mean_phoenix_eggling",
    }
    pet_id = egg_to_pet.get(item_name)
    if pet_id is None:
        return copy.deepcopy(dict(player_data)), False, "unknown_phoenix_egg"
    if _clean_int(player_data.get("summoning_level"), 1, minimum=1) < 72:
        return copy.deepcopy(dict(player_data)), False, "summoning_level"
    inventory = player_data.get("inventory")
    if not isinstance(inventory, Mapping) or _clean_int(inventory.get(item_name)) <= 0:
        return copy.deepcopy(dict(player_data)), False, "missing_phoenix_egg"
    updated = copy.deepcopy(dict(player_data))
    bank = dict(updated.get("inventory", {}) or {})
    bank[item_name] = _clean_int(bank.get(item_name)) - 1
    updated["inventory"] = bank
    acquired, ok, instance_id = acquire_pet_pure(updated, pet_id)
    if not ok:
        return copy.deepcopy(dict(player_data)), False, instance_id
    return acquired, True, instance_id


def pet_compatible_carried_foods_pure(
    pet_id: str, carried: Mapping[str, Any]
) -> tuple[str, ...]:
    pet = PETS_BY_ID.get(pet_id)
    if pet is None:
        return ()
    categories = {food.casefold() for food in pet.foods}
    explicit = {food.casefold() for food in pet_display_foods(pet)}
    compatible = []
    for item_name, amount in carried.items():
        if not isinstance(item_name, str) or _clean_int(amount, 0) <= 0:
            continue
        folded = item_name.casefold()
        allowed = folded in explicit
        if "fish" in categories:
            allowed = allowed or item_name in _RAW_FISH
            if not pet.food_summary.casefold().startswith("raw fish"):
                allowed = allowed or item_name in _COOKED_FISH
        if "raw fish" in categories:
            allowed = allowed or item_name in _RAW_FISH
        if "raw meat" in categories:
            allowed = allowed or item_name in _RAW_MEAT
        if "chicken" in categories:
            allowed = allowed or item_name == "Raw chicken"
        if pet.id == "baby_troll":
            allowed = True
        if allowed:
            compatible.append(item_name)
    return tuple(compatible)


def advance_active_pet_pure(
    player_data: Mapping[str, Any],
    *,
    active_carried_target: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    updated = copy.deepcopy(dict(player_data))
    state = dict(updated.get("summoning_state", {}) or {})
    follower = state.get("active_follower", {}) or {}
    result = {
        "fed_item": None,
        "grew": False,
        "returned_home": False,
        "instance_id": None,
    }
    if follower.get("kind") != "pet":
        return updated, result
    instance_id = str(follower.get("entity_id", ""))
    instances = sanitize_pet_instances_pure(state.get("pet_instances"))
    instance = instances.get(instance_id)
    if instance is None:
        state["active_follower"] = {}
        updated["summoning_state"] = state
        return updated, result
    pet = PETS_BY_ID[instance["pet_id"]]
    result["instance_id"] = instance_id
    hunger_gain = (
        PET_BABY_HUNGER_PER_REVIEW
        if instance["stage"] == 0 and pet.stage_count > 1
        else PET_ADULT_HUNGER_PER_REVIEW
    )
    next_hunger = min(100.0, instance["hunger"] + hunger_gain)
    carried_root = updated.get("carried_inventory", {})
    carried_packs = (
        dict(carried_root) if isinstance(carried_root, Mapping) else {}
    )
    carried = (
        dict(carried_packs.get(active_carried_target, {}) or {})
        if active_carried_target
        else {}
    )
    auto_care = bool(updated.get("pet_auto_care", True))
    foods = pet_compatible_carried_foods_pure(pet.id, carried)
    if auto_care and next_hunger >= 75.0:
        food = next(
            (
                item_name
                for item_name in foods
                if _clean_int(carried.get(item_name), 0) > 0
            ),
            None,
        )
        if food:
            carried[food] -= 1
            instance["hunger"] = max(
                0.0, instance["hunger"] - PET_FEED_HUNGER_REDUCTION
            )
            next_hunger = min(100.0, instance["hunger"] + hunger_gain)
            carried_packs[active_carried_target] = carried
            updated["carried_inventory"] = carried_packs
            inventory = dict(updated.get("inventory", {}) or {})
            inventory[food] = max(0, _clean_int(inventory.get(food), 0) - 1)
            updated["inventory"] = inventory
            result["fed_item"] = food
    if next_hunger >= 100.0 and auto_care:
        instance["location"] = "bank"
        instance["policy_lapse_reason"] = "Out of pet food"
        instances[instance_id] = instance
        state["pet_instances"] = instances
        state["active_follower"] = {}
        updated["summoning_state"] = state
        result["returned_home"] = True
        return updated, result
    instance["hunger"] = next_hunger
    if instance["stage"] < pet.stage_count - 1:
        instance["growth"] += 100.0 / PET_GROWTH_REVIEWS_PER_STAGE
        if instance["growth"] >= 100.0:
            instance["stage"] += 1
            instance["growth"] = 0.0
            result["grew"] = True
    instances[instance_id] = instance
    state["pet_instances"] = instances
    updated["summoning_state"] = state
    return updated, result
