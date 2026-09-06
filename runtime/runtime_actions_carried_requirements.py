"""Carried-overlay target requirements and pack construction."""

from __future__ import annotations

from typing import Any

from ..core.constants import (
    COMBAT_FOOD_DATA,
    COOKING_DATA,
    CRAFTING_DATA,
    DEFAULT_COOKING_TARGET,
    DEFAULT_FIREMAKING_TARGET,
    DEFAULT_FLETCHING_TARGET,
    DEFAULT_HERBLORE_TARGET,
    DEFAULT_PRAYER_TARGET,
    DEFAULT_RUNECRAFTING_TARGET,
    DEFAULT_WOODCUTTING_TARGET,
    FIREMAKING_DATA,
    FLETCHING_DATA,
    HERBLORE_DATA,
    PRAYER_DATA,
    RUNECRAFTING_DATA,
    SMITHING_DATA,
    TREE_DATA,
)
from ..core.skill_registry import CURRENT_SKILLS
from ..data.agility_data import AGILITY_TARGETS_BY_ID
from ..data.item_values import STACKABLE_ITEM_NAMES
from ..data.smithing_data import DEFAULT_SMITHING_TARGET
from ..data.summoning_data import DEFAULT_SUMMONING_TARGET
from ..data.urn_data import URN_STATE_ITEM_NAMES, materialize_urn_layout_pure
from ..logic import inventory_pure
from ..logic.skilling_boost_logic import (
    skilling_effective_level_pure,
    skilling_potion_item_pure,
    skilling_potion_target_enabled_pure,
)
from ..logic.summoning_logic import summoning_action_requirements_pure
from ..logic_pure.logic_pure import (
    coal_bag_coal_pure,
    fletching_material_requirements_pure,
    owned_gilded_altar_marrentill_required_pure,
)


# Handler keys that draw from / fill the 28-slot carried inventory, mapped to the
# player_data key holding their selected target. Utility (no-XP batching) and
# quests do not take carried teeth, so they are absent.
_OVERLAY_TARGET_KEYS = {
    "mining": "current_ore",
    "woodcutting": "current_tree",
    "fishing": "current_fishing",
    "hunter": "current_hunter",
    "cooking": "current_cooking",
    "crafting": "current_craft",
    "fletching": "current_fletch",
    "firemaking": "current_firemaking",
    "smithing": "current_smith",
    "runecrafting": "current_runecrafting",
    "herblore": "current_herblore",
    "prayer": "current_prayer",
    "thieving": "current_thieving",
    "agility": "current_agility",
    "summoning": "current_summoning",
}

# Every registered review handler is represented for the always-visible bank-run
# action. A None value means the surface has no separate target selector.
_BANK_RUN_TARGET_KEYS = {
    skill.review_handler_key: skill.current_target_key
    for skill in CURRENT_SKILLS
    if skill.review_handler_key
}
_BANK_RUN_TARGET_KEYS.update(
    {
        "utility": "current_utility",
        "quest": "current_quest",
    }
)


# A stackable occupies one slot for any quantity (then holds up to the int cap);
# use the real cache stackable set so a stack is not miscounted as N slots.
_OVERLAY_STACKABLE_NAMES: frozenset[str] = STACKABLE_ITEM_NAMES


# Processing skills draw recipe inputs from the carried pack (gated + consumed);
# gathering skills fill the pack with their product instead. Combat has its own
# supply_loadout system and is not routed through this wrapper at all.
_PROCESSING_HANDLER_KEYS = frozenset(
    {"cooking", "crafting", "fletching", "firemaking", "smithing", "runecrafting", "herblore", "prayer", "summoning"}
)


_PROCESSING_DATA_TABLES = {
    "woodcutting": (TREE_DATA, "current_tree", DEFAULT_WOODCUTTING_TARGET),
    "cooking": (COOKING_DATA, "current_cooking", DEFAULT_COOKING_TARGET),
    "crafting": (CRAFTING_DATA, "current_craft", "form_pot_unfired"),
    "fletching": (FLETCHING_DATA, "current_fletch", DEFAULT_FLETCHING_TARGET),
    "firemaking": (FIREMAKING_DATA, "current_firemaking", DEFAULT_FIREMAKING_TARGET),
    "smithing": (SMITHING_DATA, "current_smith", DEFAULT_SMITHING_TARGET),
    "runecrafting": (RUNECRAFTING_DATA, "current_runecrafting", DEFAULT_RUNECRAFTING_TARGET),
    "herblore": (HERBLORE_DATA, "current_herblore", DEFAULT_HERBLORE_TARGET),
    "prayer": (PRAYER_DATA, "current_prayer", DEFAULT_PRAYER_TARGET),
}


def _processing_requirements_for(
    handler_key: str,
    player_data: dict[str, Any],
    carried_inventory: dict[str, Any] | None = None,
) -> dict[str, int]:
    """The recipe inputs a processing target needs per action, ``{item: count}``.

    Read from each skill's own data table so this stays a thin lookup, not a
    handler rewrite. Runecrafting has no fixed ``requirements`` dict (any of its
    ``essence_items`` works); resolve it to the first stocked essence in the
    target's source order, so the pack has something concrete to carry.
    """
    if handler_key == "summoning":
        target = str(
            player_data.get("current_summoning", DEFAULT_SUMMONING_TARGET)
        )
        inventory = (
            carried_inventory
            if isinstance(carried_inventory, dict)
            else player_data.get("inventory", {})
        )
        return summoning_action_requirements_pure(
            player_data,
            target,
            inventory_override=inventory,
        )
    table_info = _PROCESSING_DATA_TABLES.get(handler_key)
    if table_info is None:
        return {}
    table, target_key, default_target = table_info
    target = player_data.get(target_key, default_target)
    spec = table.get(target)
    if not isinstance(spec, dict):
        return {}
    requirements = spec.get("requirements")
    if isinstance(requirements, dict) and requirements:
        if handler_key == "fletching":
            if carried_inventory:
                resolved = fletching_material_requirements_pure(target, carried_inventory, table)
                if resolved is not None:
                    return resolved
            resolved = fletching_material_requirements_pure(target, player_data.get("inventory", {}) or {}, table)
            if resolved is not None:
                return resolved
        resolved = {str(item): int(amount) for item, amount in requirements.items() if isinstance(item, str)}
        if handler_key == "smithing" and "Coal" in resolved:
            remaining_coal = max(
                0,
                resolved["Coal"] - coal_bag_coal_pure(player_data),
            )
            if remaining_coal:
                resolved["Coal"] = remaining_coal
            else:
                resolved.pop("Coal")
        if (
            handler_key == "prayer"
            and spec.get("method") == "gilded_altar"
            and player_data.get("prayer_gilded_mode", "hosted") == "owned"
        ):
            marrentill = owned_gilded_altar_marrentill_required_pure(player_data, str(target))
            if marrentill > 0:
                resolved["Clean marrentill"] = marrentill
        return resolved
    essence_items = spec.get("essence_items")
    if isinstance(essence_items, (list, tuple)) and essence_items:
        inventory = player_data.get("inventory", {}) or {}
        essence = next((item for item in essence_items if inventory.get(item, 0)), essence_items[0])
        return {essence: 1}
    return {}


def _processing_presence_requirements_for(handler_key: str, player_data: dict[str, Any]) -> dict[str, int]:
    """Non-material recipe gates that must be present but are not per-action inputs."""
    table_info = _PROCESSING_DATA_TABLES.get(handler_key)
    if table_info is None:
        return {}
    table, target_key, default_target = table_info
    spec = table.get(player_data.get(target_key, default_target))
    required_items = spec.get("required_items", {}) if isinstance(spec, dict) else {}
    if not isinstance(required_items, dict):
        return {}
    return {str(item): int(amount) for item, amount in required_items.items() if isinstance(item, str)}


def _skilling_potion_requirement_for(
    handler_key: str,
    player_data: dict[str, Any],
    target_id: str,
    carried_inventory: dict[str, Any],
    *,
    advanced: bool,
) -> dict[str, int]:
    if handler_key not in {"crafting", "fletching"}:
        return {}
    table = CRAFTING_DATA if handler_key == "crafting" else FLETCHING_DATA
    spec = table.get(target_id, {})
    required_level = int(spec.get("level", 1) or 1)
    if (
        skilling_effective_level_pure(player_data, handler_key) >= required_level
        or not skilling_potion_target_enabled_pure(
            player_data, handler_key, target_id
        )
    ):
        return {}
    item_name = skilling_potion_item_pure(carried_inventory, handler_key)
    if not item_name and not advanced:
        item_name = skilling_potion_item_pure(
            player_data.get("inventory", {}) or {}, handler_key
        )
    return {item_name: 1} if item_name else {}


def _agility_target_can_damage(target_id: str) -> bool:
    target = AGILITY_TARGETS_BY_ID.get(target_id)
    if target is None:
        return False
    return (
        target.activity_kind in {"brimhaven", "gnome_ball"}
        or any(stage.can_fail for stage in target.stages)
    )


def _agility_equipment_satisfies(equipped_items: set[str], item_name: str) -> bool:
    wanted = item_name.casefold()
    return any(
        candidate.casefold() == wanted
        or (wanted == "crossbow" and "crossbow" in candidate.casefold())
        for candidate in equipped_items
    )


def _agility_casual_layout_for(player_data: dict[str, Any], target_id: str) -> dict[str, int]:
    """Build Auto mode's ordered requirement-and-food pack for one target."""

    target = AGILITY_TARGETS_BY_ID.get(target_id)
    if target is None:
        return {}
    bank = player_data.get("inventory", {}) or {}
    equipment = player_data.get("equipment", {}) or {}
    equipped_items = {
        str(item)
        for item in equipment.values()
        if isinstance(item, str)
    } if isinstance(equipment, dict) else set()
    layout: dict[str, int] = {}
    for item_name in target.required_items:
        if not _agility_equipment_satisfies(equipped_items, item_name) and int(bank.get(item_name, 0) or 0) > 0:
            layout[item_name] = 1
    for item_options in target.required_item_options:
        if any(_agility_equipment_satisfies(equipped_items, item_name) for item_name in item_options):
            continue
        stocked = next(
            (item_name for item_name in item_options if int(bank.get(item_name, 0) or 0) > 0),
            None,
        )
        if stocked is not None:
            layout[stocked] = 1
    if _agility_target_can_damage(target_id):
        for item_name in player_data.get("combat_auto_eat_food", ()) or ():
            if item_name not in COMBAT_FOOD_DATA:
                continue
            available = int(bank.get(item_name, 0) or 0)
            if available > 0:
                layout[item_name] = available
    return layout


def _agility_carried_requirement_gaps(
    player_data: dict[str, Any],
    target_id: str,
    view: dict[str, Any],
) -> tuple[str, ...]:
    target = AGILITY_TARGETS_BY_ID.get(target_id)
    if target is None:
        return ()
    equipment = player_data.get("equipment", {}) or {}
    equipped_items = {
        str(item)
        for item in equipment.values()
        if isinstance(item, str)
    } if isinstance(equipment, dict) else set()
    missing = [
        item_name
        for item_name in target.required_items
        if not _agility_equipment_satisfies(equipped_items, item_name)
        and int(view.get(item_name, 0) or 0) <= 0
    ]
    for item_options in target.required_item_options:
        if any(_agility_equipment_satisfies(equipped_items, item_name) for item_name in item_options):
            continue
        if not any(int(view.get(item_name, 0) or 0) > 0 for item_name in item_options):
            missing.append(f"{item_options[0]} or another valid alternative")
    return tuple(missing)


def _set_carried_target_map(player_data: dict[str, Any], map_key: str, target_id: str, value) -> None:
    existing = player_data.get(map_key)
    container = dict(existing) if isinstance(existing, dict) else {}
    if value:
        container[target_id] = value
    else:
        container.pop(target_id, None)
    player_data[map_key] = container


def _carried_target_view(player_data: dict[str, Any], target_id: str) -> dict[str, int]:
    carried = player_data.get("carried_inventory")
    view = carried.get(target_id) if isinstance(carried, dict) else None
    return dict(view) if isinstance(view, dict) else {}


def _without_urn_substitutions(inventory: dict[str, Any]) -> dict[str, Any]:
    return {item_name: amount for item_name, amount in inventory.items() if item_name not in URN_STATE_ITEM_NAMES}


def _pack_can_supply(view: dict[str, Any], requirements: dict[str, int]) -> bool:
    return all(int(view.get(item, 0) or 0) >= need for item, need in requirements.items())


def _bank_can_supply(bank: dict[str, Any], requirements: dict[str, int]) -> bool:
    return all(int(bank.get(item, 0) or 0) >= need for item, need in requirements.items())


def _owned_bag_capacities(bank: dict[str, Any]) -> dict[str, int]:
    """{material: bag capacity} for each bag the player owns (Coal bag -> Coal: 27)."""
    return {
        material: extra
        for bag_name, (material, extra) in inventory_pure.BAG_DEFINITIONS.items()
        if int(bank.get(bag_name, 0) or 0) > 0
    }


def _repack_view_for_target(
    is_processing: bool,
    advanced: bool,
    layout: dict[str, int],
    bank: dict[str, Any],
    requirements: dict[str, int],
    capacity: int,
    casual_layout: dict[str, int] | None = None,
    casual_requirements: dict[str, int] | None = None,
) -> dict[str, int]:
    """The freshly-packed carried view after a completed bank run.

    Advanced targets replay their saved layout (capped by the bank). Casual
    processing targets get their recipe inputs split by
    ``pack_processing_inputs_pure``. Casual gathering targets start empty — the
    gathered product fills the pack from actions, it is never pre-loaded.
    """
    if advanced:
        # The grid is 28 cells and an inventory is 28 slots. Never pass the
        # bag-inflated capacity here: that would hand the bag's extra room to every
        # item in the layout, not just the bagged material (bags-in-the-grid is a
        # separate, unbuilt feature).
        return inventory_pure.apply_carried_layout_pure(
            bank,
            materialize_urn_layout_pure(bank, layout),
            inventory_pure.CARRIED_CAPACITY,
            _OVERLAY_STACKABLE_NAMES,
        )
    if casual_layout:
        return inventory_pure.apply_carried_layout_pure(
            bank,
            casual_layout,
            inventory_pure.CARRIED_CAPACITY,
            _OVERLAY_STACKABLE_NAMES,
        )
    if is_processing:
        extras = inventory_pure.apply_carried_layout_pure(
            bank,
            casual_requirements or {},
            inventory_pure.CARRIED_CAPACITY,
            _OVERLAY_STACKABLE_NAMES,
        )
        recipe_capacity = max(
            0,
            inventory_pure.CARRIED_CAPACITY
            - inventory_pure.carried_slots_used(
                extras, _OVERLAY_STACKABLE_NAMES
            ),
        )
        # Pack against the real 28 slots and let the packer model the bag (which
        # holds its material in one slot). Inflating `capacity` instead would hand
        # the extra room to every material, not just the bagged one.
        packed = inventory_pure.pack_processing_inputs_pure(
            bank, requirements, recipe_capacity,
            _OVERLAY_STACKABLE_NAMES, _owned_bag_capacities(bank),
        )
        for item_name, amount in extras.items():
            packed[item_name] = packed.get(item_name, 0) + amount
        return packed
    return {}
