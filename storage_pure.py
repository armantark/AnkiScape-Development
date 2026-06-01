# storage_pure.py - Pure helpers for migrating and defaulting player data (no Anki deps)
from typing import Dict, Iterable, Optional, Any

try:
    from .item_registry import ItemDefinition
    from .mining_data import DEFAULT_MINING_TARGET, DEFAULT_MINING_TOOLBELT, LEGACY_ORE_TARGETS
    from .skill_registry import default_skill_state, default_target_state
    from .woodcutting_data import (
        DEFAULT_WOODCUTTING_TOOLBELT,
        LEGACY_LOG_STORAGE_MIGRATIONS,
        LEGACY_TREE_TARGETS,
    )
except ImportError:
    from item_registry import ItemDefinition
    from mining_data import DEFAULT_MINING_TARGET, DEFAULT_MINING_TOOLBELT, LEGACY_ORE_TARGETS
    from skill_registry import default_skill_state, default_target_state
    from woodcutting_data import (
        DEFAULT_WOODCUTTING_TOOLBELT,
        LEGACY_LOG_STORAGE_MIGRATIONS,
        LEGACY_TREE_TARGETS,
    )

CURRENT_CONFIG_VERSION = 8
DEFAULT_UTILITY_ACTIVITY = "make_soft_clay"

_LEGACY_FLETCHING_TARGETS = {
    "Arrow shafts": "arrow_shafts",
    "Shortbow (u)": "shortbow_u",
    "Oak shortbow (u)": "oak_shortbow_u",
    "Willow shortbow (u)": "willow_shortbow_u",
    "Maple shortbow (u)": "maple_shortbow_u",
    "Yew shortbow (u)": "yew_shortbow_u",
    "Magic shortbow (u)": "magic_shortbow_u",
    "redwood_arrow_shafts": "arrow_shafts",
}


def _default_inventory(ORE_DATA: Dict[str, Any], item_definitions: Optional[Iterable[ItemDefinition]] = None) -> Dict[str, int]:
    if item_definitions is None:
        inventory: Dict[str, int] = {}
        for spec in ORE_DATA.values():
            output_item = spec.get("output_item")
            if isinstance(output_item, str):
                inventory.setdefault(output_item, 0)
            alternate_output = spec.get("alternate_output_item")
            if isinstance(alternate_output, str):
                inventory.setdefault(alternate_output, 0)
            for weighted in spec.get("weighted_outputs", ()):
                if isinstance(weighted, dict) and isinstance(weighted.get("item"), str):
                    inventory.setdefault(str(weighted["item"]), 0)
        return inventory
    inventory: Dict[str, int] = {}
    for item in item_definitions:
        inventory.setdefault(item.storage_key, 0)
    for ore in ORE_DATA:
        inventory.setdefault(ore, 0)
    return inventory


def default_player_data(ORE_DATA: Dict[str, Any], item_definitions: Optional[Iterable[ItemDefinition]] = None) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "config_version": CURRENT_CONFIG_VERSION,
        "inventory": _default_inventory(ORE_DATA, item_definitions),
        "progress_to_next": 0,
        "completed_achievements": [],
    }
    data.update(default_skill_state())
    data.update(default_target_state())
    data["current_utility"] = DEFAULT_UTILITY_ACTIVITY
    data["toolbelt"] = _default_toolbelt()
    data["owned_equipment"] = []
    return data


def _default_toolbelt() -> Dict[str, list[str]]:
    defaults: Dict[str, list[str]] = {}
    for source in (DEFAULT_WOODCUTTING_TOOLBELT, DEFAULT_MINING_TOOLBELT):
        for skill, items in source.items():
            defaults.setdefault(skill, [])
            defaults[skill].extend(item for item in items if item not in defaults[skill])
    return defaults


def _migrate_legacy_mining_target(data: Dict[str, Any], ore_data: Dict[str, Any]) -> None:
    current_ore = data.get("current_ore")
    if isinstance(current_ore, str):
        data["current_ore"] = LEGACY_ORE_TARGETS.get(current_ore, current_ore)
    if data.get("current_ore") not in ore_data:
        data["current_ore"] = DEFAULT_MINING_TARGET


def _migrate_legacy_woodcutting_target(data: Dict[str, Any]) -> None:
    current_tree = data.get("current_tree")
    if isinstance(current_tree, str):
        data["current_tree"] = LEGACY_TREE_TARGETS.get(current_tree, current_tree)


def _migrate_legacy_log_inventory(inventory: Dict[str, int]) -> None:
    for legacy_key, new_key in LEGACY_LOG_STORAGE_MIGRATIONS.items():
        if legacy_key not in inventory:
            continue
        try:
            amount = int(inventory.get(legacy_key, 0))
        except (TypeError, ValueError):
            amount = 0
        if new_key is not None and amount:
            inventory[new_key] = inventory.get(new_key, 0) + amount
        inventory.pop(legacy_key, None)


def _migrate_toolbelt(data: Dict[str, Any]) -> None:
    toolbelt = data.get("toolbelt")
    if not isinstance(toolbelt, dict):
        toolbelt = {}
    defaults = _default_toolbelt()
    for skill, default_items in defaults.items():
        existing = toolbelt.get(skill)
        if isinstance(existing, str):
            items = [existing]
        elif isinstance(existing, list):
            items = [item for item in existing if isinstance(item, str)]
        elif isinstance(existing, tuple):
            items = [item for item in existing if isinstance(item, str)]
        else:
            items = []
        for default_item in default_items:
            if default_item not in items:
                items.append(default_item)
        toolbelt[skill] = items
    data["toolbelt"] = toolbelt


def _migrate_owned_equipment(data: Dict[str, Any]) -> None:
    owned = data.get("owned_equipment")
    if isinstance(owned, str):
        items = [owned]
    elif isinstance(owned, list):
        items = [item for item in owned if isinstance(item, str)]
    elif isinstance(owned, tuple):
        items = [item for item in owned if isinstance(item, str)]
    else:
        items = []
    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    data["owned_equipment"] = deduped


def migrate_loaded_data(
    loaded: Dict[str, Any],
    ORE_DATA: Dict[str, Any],
    item_definitions: Optional[Iterable[ItemDefinition]] = None,
) -> Dict[str, Any]:
    # Start from copy
    data = dict(loaded) if loaded else {}

    # Add config_version if missing
    if "config_version" not in data:
        data["config_version"] = 1

    # Migration: old schema used total_exp (treated as mining_exp), and no per-skill exp
    if "total_exp" in data and "mining_exp" not in data:
        data["mining_exp"] = data.pop("total_exp")
        data.setdefault("woodcutting_exp", 0)
        data.setdefault("smithing_exp", 0)
        data.setdefault("crafting_exp", 0)

    # Registry-backed defaults preserve today's flat save keys while removing
    # the need to hand-add keys for each playable skill.
    for key, value in default_skill_state().items():
        data.setdefault(key, value)
    for key, value in default_target_state().items():
        data.setdefault(key, value)
    data.setdefault("current_utility", DEFAULT_UTILITY_ACTIVITY)
    _migrate_legacy_mining_target(data, ORE_DATA)
    _migrate_legacy_woodcutting_target(data)
    if isinstance(data.get("current_fletch"), str):
        data["current_fletch"] = _LEGACY_FLETCHING_TARGETS.get(data["current_fletch"], data["current_fletch"])
    if data.get("current_fletch") not in (
        "arrow_shafts",
        "oak_arrow_shafts",
        "willow_arrow_shafts",
        "maple_arrow_shafts",
        "yew_arrow_shafts",
        "magic_arrow_shafts",
        "headless_arrows",
        "bronze_arrows",
        "iron_arrows",
        "steel_arrows",
        "mithril_arrows",
        "adamant_arrows",
        "rune_arrows",
        "shortbow_u",
        "oak_shortbow_u",
        "willow_shortbow_u",
        "maple_shortbow_u",
        "yew_shortbow_u",
        "magic_shortbow_u",
    ):
        data["current_fletch"] = "arrow_shafts"
    if data.get("current_craft") == "Soft clay":
        data["current_craft"] = ""
        data["current_utility"] = DEFAULT_UTILITY_ACTIVITY
    _migrate_toolbelt(data)
    _migrate_owned_equipment(data)

    # Ensure inventory exists and has registered item keys while preserving
    # arbitrary existing entries from older or experimental saves.
    inv = data.get("inventory") or {}
    if not isinstance(inv, dict):
        inv = {}
    for item_key in _default_inventory(ORE_DATA, item_definitions):
        inv.setdefault(item_key, 0)
    _migrate_legacy_log_inventory(inv)
    data["inventory"] = inv

    # Ensure achievements structure exists
    data.setdefault("completed_achievements", [])

    # Progress key retained (not critical)
    data.setdefault("progress_to_next", 0)

    # Bump version to current
    data["config_version"] = CURRENT_CONFIG_VERSION
    return data
