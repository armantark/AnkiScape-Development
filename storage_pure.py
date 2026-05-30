# storage_pure.py - Pure helpers for migrating and defaulting player data (no Anki deps)
from typing import Dict, Iterable, Optional, Any

try:
    from .item_registry import ItemDefinition
    from .skill_registry import default_skill_state, default_target_state
except ImportError:
    from item_registry import ItemDefinition
    from skill_registry import default_skill_state, default_target_state

CURRENT_CONFIG_VERSION = 6
DEFAULT_UTILITY_ACTIVITY = "make_soft_clay"

_LEGACY_FLETCHING_TARGETS = {
    "Arrow shafts": "arrow_shafts",
    "Shortbow (u)": "shortbow_u",
    "Oak shortbow (u)": "oak_shortbow_u",
    "Willow shortbow (u)": "willow_shortbow_u",
    "Maple shortbow (u)": "maple_shortbow_u",
    "Yew shortbow (u)": "yew_shortbow_u",
    "Magic shortbow (u)": "magic_shortbow_u",
}


def _default_inventory(ORE_DATA: Dict[str, Any], item_definitions: Optional[Iterable[ItemDefinition]] = None) -> Dict[str, int]:
    if item_definitions is None:
        return {ore: 0 for ore in ORE_DATA}
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
    return data


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
    if isinstance(data.get("current_fletch"), str):
        data["current_fletch"] = _LEGACY_FLETCHING_TARGETS.get(data["current_fletch"], data["current_fletch"])
    if data.get("current_craft") == "Soft clay":
        data["current_craft"] = ""
        data["current_utility"] = DEFAULT_UTILITY_ACTIVITY

    # Ensure inventory exists and has registered item keys while preserving
    # arbitrary existing entries from older or experimental saves.
    inv = data.get("inventory") or {}
    if not isinstance(inv, dict):
        inv = {}
    for item_key in _default_inventory(ORE_DATA, item_definitions):
        inv.setdefault(item_key, 0)
    data["inventory"] = inv

    # Ensure achievements structure exists
    data.setdefault("completed_achievements", [])

    # Progress key retained (not critical)
    data.setdefault("progress_to_next", 0)

    # Bump version to current
    data["config_version"] = CURRENT_CONFIG_VERSION
    return data
