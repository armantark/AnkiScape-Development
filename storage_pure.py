# storage_pure.py - Pure helpers for migrating and defaulting player data (no Anki deps)
from typing import Dict, Iterable, Optional, Any

try:
    from .cooking_data import DEFAULT_COOKING_TARGET, COOKING_TARGETS_BY_ID
    from .crafting_data import (
        DEFAULT_CRAFTING_TARGET,
        CRAFTING_RECIPES_BY_ID,
        LEGACY_CRAFTING_ITEM_MIGRATIONS,
        LEGACY_CRAFTING_TARGETS,
    )
    from .item_registry import ItemDefinition
    from .quest_data import DEFAULT_QUEST_TARGET, default_claim_states, default_quest_states
    from .runecrafting_data import DEFAULT_RUNECRAFTING_TARGET, RUNECRAFTING_TARGETS_BY_ID
    from .firemaking_data import DEFAULT_FIREMAKING_TARGET, FIREMAKING_TARGETS_BY_ID
    from .fishing_data import DEFAULT_FISHING_TARGET, FISHING_METHODS_BY_ID
    from .hunter_data import DEFAULT_HUNTER_TARGET, HUNTER_TARGETS_BY_ID
    from .fletching_data import DEFAULT_FLETCHING_TARGET, FLETCHING_TARGETS_BY_ID, LEGACY_FLETCHING_TARGETS
    from .logic_pure import default_action_telemetry_pure, sanitize_action_telemetry_pure
    from .mining_data import DEFAULT_MINING_TARGET, DEFAULT_MINING_TOOLBELT, LEGACY_ORE_TARGETS
    from .smithing_data import (
        DEFAULT_SMITHING_TARGET,
        LEGACY_BAR_STORAGE_MIGRATIONS,
        LEGACY_SMITHING_TARGETS,
        SMITHING_RECIPES_BY_ID,
    )
    from .skill_registry import default_skill_state, default_target_state, implemented_skill_definitions, planned_skill_definitions
    from .woodcutting_data import (
        DEFAULT_WOODCUTTING_TOOLBELT,
        LEGACY_LOG_STORAGE_MIGRATIONS,
        LEGACY_TREE_TARGETS,
    )
except ImportError:
    from cooking_data import DEFAULT_COOKING_TARGET, COOKING_TARGETS_BY_ID
    from crafting_data import (
        DEFAULT_CRAFTING_TARGET,
        CRAFTING_RECIPES_BY_ID,
        LEGACY_CRAFTING_ITEM_MIGRATIONS,
        LEGACY_CRAFTING_TARGETS,
    )
    from item_registry import ItemDefinition
    from quest_data import DEFAULT_QUEST_TARGET, default_claim_states, default_quest_states
    from runecrafting_data import DEFAULT_RUNECRAFTING_TARGET, RUNECRAFTING_TARGETS_BY_ID
    from firemaking_data import DEFAULT_FIREMAKING_TARGET, FIREMAKING_TARGETS_BY_ID
    from fishing_data import DEFAULT_FISHING_TARGET, FISHING_METHODS_BY_ID
    from hunter_data import DEFAULT_HUNTER_TARGET, HUNTER_TARGETS_BY_ID
    from fletching_data import DEFAULT_FLETCHING_TARGET, FLETCHING_TARGETS_BY_ID, LEGACY_FLETCHING_TARGETS
    from logic_pure import default_action_telemetry_pure, sanitize_action_telemetry_pure
    from mining_data import DEFAULT_MINING_TARGET, DEFAULT_MINING_TOOLBELT, LEGACY_ORE_TARGETS
    from smithing_data import (
        DEFAULT_SMITHING_TARGET,
        LEGACY_BAR_STORAGE_MIGRATIONS,
        LEGACY_SMITHING_TARGETS,
        SMITHING_RECIPES_BY_ID,
    )
    from skill_registry import default_skill_state, default_target_state, implemented_skill_definitions, planned_skill_definitions
    from woodcutting_data import (
        DEFAULT_WOODCUTTING_TOOLBELT,
        LEGACY_LOG_STORAGE_MIGRATIONS,
        LEGACY_TREE_TARGETS,
    )

CURRENT_CONFIG_VERSION = 19
DEFAULT_UTILITY_ACTIVITY = "make_soft_clay"
_EQUIPMENT_SLOT_IDS = {
    "head",
    "cape",
    "neck",
    "ammunition",
    "weapon",
    "body",
    "shield",
    "legs",
    "hands",
    "feet",
    "ring",
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
    data.update(_default_combat_state())
    data.update(_default_hidden_support_state())
    data.update(default_target_state())
    data["current_utility"] = DEFAULT_UTILITY_ACTIVITY
    data["current_quest"] = DEFAULT_QUEST_TARGET
    data["cooking_success_count"] = 0
    data["cooking_burn_count"] = 0
    data["hunter_success_count"] = 0
    data["action_telemetry"] = default_action_telemetry_pure()
    data["toolbelt"] = _default_toolbelt()
    data["equipment"] = {}
    data["quests"] = default_quest_states()
    data["quest_points"] = 0
    data["pending_skill_exp_rewards"] = {}
    data["claims"] = default_claim_states()
    data["wicked_hood"] = {"fed_altars": []}
    data["runecrafting_pouches"] = {}
    data["item_charges"] = {}
    data["unlocked_abilities"] = []
    return data


def _default_combat_state() -> Dict[str, int]:
    state: Dict[str, int] = {}
    for skill in planned_skill_definitions():
        if skill.category != "combat":
            continue
        state[skill.level_key] = 10 if skill.id == "constitution" else 1
        state[skill.exp_key] = 0
    return state


def _default_hidden_support_state() -> Dict[str, int]:
    """Support skills with hidden XP side effects but no visible surface yet."""
    state: Dict[str, int] = {}
    for skill in planned_skill_definitions():
        if skill.id != "agility":
            continue
        state[skill.level_key] = 1
        state[skill.exp_key] = 0
    return state


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


def _migrate_legacy_smithing_target(data: Dict[str, Any]) -> None:
    current_smith = data.get("current_smith")
    current_bar = data.get("current_bar")
    try:
        config_version = int(data.get("config_version", 1))
    except (TypeError, ValueError):
        config_version = 1
    if isinstance(current_bar, str) and (config_version < 9 or not isinstance(current_smith, str)):
        current_smith = LEGACY_SMITHING_TARGETS.get(current_bar, current_bar)
    if isinstance(current_smith, str):
        current_smith = LEGACY_SMITHING_TARGETS.get(current_smith, current_smith)
    if not isinstance(current_smith, str) or current_smith not in SMITHING_RECIPES_BY_ID:
        current_smith = DEFAULT_SMITHING_TARGET
    data["current_smith"] = current_smith


def _migrate_legacy_crafting_target(data: Dict[str, Any]) -> None:
    current_craft = data.get("current_craft")
    if isinstance(current_craft, str):
        current_craft = LEGACY_CRAFTING_TARGETS.get(current_craft, current_craft)
    if current_craft == "":
        data["current_craft"] = current_craft
        return
    if not isinstance(current_craft, str) or current_craft not in CRAFTING_RECIPES_BY_ID:
        current_craft = DEFAULT_CRAFTING_TARGET
    data["current_craft"] = current_craft


def _migrate_firemaking_target(data: Dict[str, Any]) -> None:
    current_firemaking = data.get("current_firemaking")
    if not isinstance(current_firemaking, str) or current_firemaking not in FIREMAKING_TARGETS_BY_ID:
        current_firemaking = DEFAULT_FIREMAKING_TARGET
    data["current_firemaking"] = current_firemaking


def _migrate_fishing_target(data: Dict[str, Any]) -> None:
    current_fishing = data.get("current_fishing")
    if not isinstance(current_fishing, str) or current_fishing not in FISHING_METHODS_BY_ID:
        current_fishing = DEFAULT_FISHING_TARGET
    data["current_fishing"] = current_fishing


def _migrate_hunter_target(data: Dict[str, Any]) -> None:
    current_hunter = data.get("current_hunter")
    if not isinstance(current_hunter, str) or current_hunter not in HUNTER_TARGETS_BY_ID:
        current_hunter = DEFAULT_HUNTER_TARGET
    data["current_hunter"] = current_hunter


def _migrate_cooking_target(data: Dict[str, Any]) -> None:
    current_cooking = data.get("current_cooking")
    if not isinstance(current_cooking, str) or current_cooking not in COOKING_TARGETS_BY_ID:
        current_cooking = DEFAULT_COOKING_TARGET
    data["current_cooking"] = current_cooking


def _migrate_runecrafting_target(data: Dict[str, Any]) -> None:
    current_runecrafting = data.get("current_runecrafting")
    if not isinstance(current_runecrafting, str) or current_runecrafting not in RUNECRAFTING_TARGETS_BY_ID:
        current_runecrafting = DEFAULT_RUNECRAFTING_TARGET
    data["current_runecrafting"] = current_runecrafting


def _migrate_quest_state(data: Dict[str, Any]) -> None:
    quests = data.get("quests")
    clean_quests = default_quest_states()
    if isinstance(quests, dict):
        for quest_id, default_state in clean_quests.items():
            raw_state = quests.get(quest_id)
            if not isinstance(raw_state, dict):
                continue
            state = dict(default_state)
            state["started"] = bool(raw_state.get("started", state["started"]))
            state["completed"] = bool(raw_state.get("completed", state["completed"]))
            try:
                progress = int(raw_state.get("progress", state["progress"]))
            except (TypeError, ValueError):
                progress = int(state["progress"])
            state["progress"] = max(0, progress)
            if state["completed"] and state["progress"] < 1:
                state["progress"] = 1
            clean_quests[quest_id] = state
    data["quests"] = clean_quests
    try:
        data["quest_points"] = max(0, int(data.get("quest_points", 0)))
    except (TypeError, ValueError):
        data["quest_points"] = 0
    current_quest = data.get("current_quest")
    if not isinstance(current_quest, str) or current_quest not in clean_quests:
        current_quest = DEFAULT_QUEST_TARGET
    data["current_quest"] = current_quest


def _migrate_pending_skill_exp_rewards(data: Dict[str, Any]) -> None:
    raw_pending = data.get("pending_skill_exp_rewards")
    implemented_exp_keys = {skill.exp_key for skill in implemented_skill_definitions()}
    clean_pending: Dict[str, float] = {}
    if isinstance(raw_pending, dict):
        for exp_key, raw_amount in raw_pending.items():
            if not isinstance(exp_key, str):
                continue
            try:
                amount = float(raw_amount)
            except (TypeError, ValueError):
                continue
            if amount <= 0:
                continue
            if exp_key in implemented_exp_keys:
                try:
                    existing = float(data.get(exp_key, 0) or 0)
                except (TypeError, ValueError):
                    existing = 0.0
                data[exp_key] = existing + amount
            else:
                clean_pending[exp_key] = clean_pending.get(exp_key, 0.0) + amount
    data["pending_skill_exp_rewards"] = clean_pending


def _migrate_claim_state(data: Dict[str, Any]) -> None:
    claims = data.get("claims")
    clean_claims = default_claim_states()
    if isinstance(claims, dict):
        for claim_id, default_state in clean_claims.items():
            raw_state = claims.get(claim_id)
            if isinstance(raw_state, dict):
                clean_claims[claim_id] = {"claimed": bool(raw_state.get("claimed", default_state["claimed"]))}
            elif isinstance(raw_state, bool):
                clean_claims[claim_id] = {"claimed": raw_state}
    data["claims"] = clean_claims


def _migrate_runecrafting_side_state(data: Dict[str, Any]) -> None:
    hood = data.get("wicked_hood")
    fed_altars = []
    if isinstance(hood, dict):
        raw_fed = hood.get("fed_altars", [])
        if isinstance(raw_fed, str):
            fed_altars = [raw_fed]
        elif isinstance(raw_fed, (list, tuple, set)):
            fed_altars = [altar for altar in raw_fed if isinstance(altar, str)]
    data["wicked_hood"] = {"fed_altars": sorted(set(fed_altars))}

    pouches = data.get("runecrafting_pouches")
    clean_pouches: Dict[str, Dict[str, int]] = {}
    if isinstance(pouches, dict):
        for pouch_id, raw_state in pouches.items():
            if not isinstance(pouch_id, str) or not isinstance(raw_state, dict):
                continue
            try:
                degradation = max(0, int(raw_state.get("degradation", 0)))
            except (TypeError, ValueError):
                degradation = 0
            clean_pouches[pouch_id] = {"degradation": degradation}
    data["runecrafting_pouches"] = clean_pouches

    charges = data.get("item_charges")
    clean_charges: Dict[str, int] = {}
    if isinstance(charges, dict):
        for item_name, raw_charges in charges.items():
            if not isinstance(item_name, str):
                continue
            try:
                charge_count = int(raw_charges)
            except (TypeError, ValueError):
                continue
            if charge_count > 0:
                clean_charges[item_name] = charge_count
    data["item_charges"] = clean_charges


def _migrate_unlocked_abilities(data: Dict[str, Any]) -> None:
    raw_abilities = data.get("unlocked_abilities")
    if isinstance(raw_abilities, str):
        abilities = [raw_abilities]
    elif isinstance(raw_abilities, (list, tuple, set)):
        abilities = [ability for ability in raw_abilities if isinstance(ability, str)]
    else:
        abilities = []
    data["unlocked_abilities"] = sorted(set(abilities))


def _migrate_fletching_target(data: Dict[str, Any]) -> None:
    current_fletch = data.get("current_fletch")
    if isinstance(current_fletch, str):
        current_fletch = LEGACY_FLETCHING_TARGETS.get(current_fletch, current_fletch)
    if not isinstance(current_fletch, str) or current_fletch not in FLETCHING_TARGETS_BY_ID:
        current_fletch = DEFAULT_FLETCHING_TARGET
    data["current_fletch"] = current_fletch


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


def _migrate_legacy_bar_inventory(inventory: Dict[str, int]) -> None:
    for legacy_key, new_key in LEGACY_BAR_STORAGE_MIGRATIONS.items():
        if legacy_key not in inventory:
            continue
        try:
            amount = int(inventory.get(legacy_key, 0))
        except (TypeError, ValueError):
            amount = 0
        if amount:
            inventory[new_key] = inventory.get(new_key, 0) + amount
        inventory.pop(legacy_key, None)


def _migrate_legacy_crafting_inventory(inventory: Dict[str, int]) -> None:
    for legacy_key, new_key in LEGACY_CRAFTING_ITEM_MIGRATIONS.items():
        if legacy_key not in inventory:
            continue
        try:
            amount = int(inventory.get(legacy_key, 0))
        except (TypeError, ValueError):
            amount = 0
        if amount:
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


def _migrate_equipment(data: Dict[str, Any]) -> None:
    equipment = data.get("equipment")
    clean_equipment: Dict[str, str] = {}
    if isinstance(equipment, dict):
        for slot, item_name in equipment.items():
            if isinstance(slot, str) and slot in _EQUIPMENT_SLOT_IDS and isinstance(item_name, str):
                clean_equipment[slot] = item_name
    data["equipment"] = clean_equipment
    data.pop("owned_equipment", None)


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
    for key, value in _default_combat_state().items():
        data.setdefault(key, value)
    for key, value in _default_hidden_support_state().items():
        data.setdefault(key, value)
    for key, value in default_target_state().items():
        data.setdefault(key, value)
    data.setdefault("current_utility", DEFAULT_UTILITY_ACTIVITY)
    _migrate_legacy_mining_target(data, ORE_DATA)
    _migrate_legacy_woodcutting_target(data)
    _migrate_legacy_smithing_target(data)
    _migrate_legacy_crafting_target(data)
    _migrate_fletching_target(data)
    _migrate_firemaking_target(data)
    _migrate_fishing_target(data)
    _migrate_hunter_target(data)
    _migrate_cooking_target(data)
    _migrate_runecrafting_target(data)
    _migrate_quest_state(data)
    _migrate_pending_skill_exp_rewards(data)
    _migrate_claim_state(data)
    _migrate_runecrafting_side_state(data)
    _migrate_unlocked_abilities(data)
    _migrate_toolbelt(data)
    _migrate_equipment(data)

    # Ensure inventory exists and has registered item keys while preserving
    # arbitrary existing entries from older or experimental saves.
    inv = data.get("inventory") or {}
    if not isinstance(inv, dict):
        inv = {}
    for item_key in _default_inventory(ORE_DATA, item_definitions):
        inv.setdefault(item_key, 0)
    _migrate_legacy_log_inventory(inv)
    _migrate_legacy_bar_inventory(inv)
    _migrate_legacy_crafting_inventory(inv)
    data["inventory"] = inv

    # Ensure achievements structure exists
    data.setdefault("completed_achievements", [])
    data.setdefault("cooking_success_count", 0)
    data.setdefault("cooking_burn_count", 0)
    data.setdefault("hunter_success_count", 0)
    data["action_telemetry"] = sanitize_action_telemetry_pure(data.get("action_telemetry"))

    # Progress key retained (not critical)
    data.setdefault("progress_to_next", 0)

    # Bump version to current
    data["config_version"] = CURRENT_CONFIG_VERSION
    return data
