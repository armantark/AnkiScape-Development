"""logic_pure_equipment.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from ..data.equipment_data import EQUIPMENT_BONUS_FIELDS, EquipmentBonuses

from .logic_pure_landmarks import (  # noqa: F401  (re-export)
    KNIGHT_WAVES_TOTAL_STEPS,
    KNIGHT_WAVES_XP_REWARD,
    MAGE_ARENA_GOD_CAPES,
    MAGE_ARENA_GOD_DATA,
    MAGE_ARENA_GOD_STAVES,
    MAGE_ARENA_SPELL_TO_GOD,
    MAGE_ARENA_STEP_NAMES,
    MAGE_ARENA_TOTAL_STEPS,
    STRONGHOLD_BOOT_CHOICES,
    STRONGHOLD_REWARD_COINS,
    STRONGHOLD_STEP_NAMES,
    STRONGHOLD_TOTAL_STEPS,
    _owns_or_equips_pure,
    apply_knight_waves_step_pure,
    apply_mage_arena_cape_action_pure,
    apply_mage_arena_step_pure,
    apply_stronghold_step_pure,
    attune_mage_arena_spell_pure,
    default_knight_waves_state_pure,
    default_mage_arena_state_pure,
    default_stronghold_state_pure,
    grant_stronghold_reward_pure,
    knight_waves_locked_reasons_pure,
    mage_arena_locked_reasons_pure,
    sanitize_knight_waves_state_pure,
    sanitize_mage_arena_state_pure,
    sanitize_stronghold_state_pure,
    set_mage_arena_alignment_pure,
)

from .logic_pure_state import (  # noqa: F401  (re-export)
    COMBAT_BANK_RUN_REVIEWS,
    COMBAT_GRAVE_RECOVERY_REVIEWS,
    _COMBAT_DRAGONFIRE_POTION_BY_DOSE,
    _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES,
    _COMBAT_STAT_POTION_BY_DOSE,
    _COMBAT_STAT_POTION_ITEM_NAMES,
    _build_combat_potion_dose_lookup,
    _combat_grave_items,
    _combat_stored_loadout,
    _copy_player_data_with_nested,
    _non_negative_float,
    _non_negative_int,
    _positive_int,
    _requirements_from_spec,
    _sanitize_combat_bank_run,
    _sanitize_combat_grave_state,
    _sanitize_combat_supply_loadout,
    _sanitize_death_office_state,
    _signed_int,
    default_combat_supply_loadout_pure,
    quest_completed_pure,
    quest_state_pure,
    sanitize_quest_combat_active_encounters_pure,
)

from .logic_pure_landmarks import (
    MAGE_ARENA_GOD_CAPES,
    MAGE_ARENA_GOD_DATA,
    MAGE_ARENA_GOD_STAVES,
)

from .logic_pure_state import (
    _positive_int,
)


def _toolbelt_ids(toolbelt, skill_key):
    if not isinstance(toolbelt, Mapping):
        return set()
    raw = toolbelt.get(skill_key, ())
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, Iterable):
        return {item for item in raw if isinstance(item, str)}
    return set()


def best_woodcutting_axe_pure(woodcutting_level, inventory, toolbelt, axe_data):
    """Return the best usable axe spec, considering bound tools and owned items."""
    bound_ids = _toolbelt_ids(toolbelt, "woodcutting")
    best = None
    for axe_id, spec in axe_data.items():
        if spec.get("status", "implemented") != "implemented":
            continue
        display_name = spec.get("display_name", axe_id)
        owned = axe_id in bound_ids or inventory.get(display_name, 0) > 0
        if not owned or woodcutting_level < spec.get("level", 1):
            continue
        if best is None or spec.get("ratio", 0) >= best.get("ratio", 0):
            best = spec
    return best


def best_mining_pickaxe_pure(mining_level, inventory, toolbelt, pickaxe_data):
    """Return the best usable pickaxe spec, considering bound tools and owned items."""
    bound_ids = _toolbelt_ids(toolbelt, "mining")
    best = None
    best_power = 0.0
    for pickaxe_id, spec in pickaxe_data.items():
        if spec.get("status", "implemented") != "implemented":
            continue
        display_name = spec.get("display_name", pickaxe_id)
        owned = pickaxe_id in bound_ids or inventory.get(display_name, 0) > 0
        if not owned or mining_level < spec.get("level", 1):
            continue
        power = float(spec.get("ratio", 0))
        if "dragon" in str(spec.get("display_name", "")).lower():
            power *= 1.12
        if best is None or power >= best_power:
            best = spec
            best_power = power
    return best


def _equipment_value(spec: object, key: str, default: object = None) -> object:
    if isinstance(spec, Mapping):
        return spec.get(key, default)
    return getattr(spec, key, default)


def _equipment_bonuses(spec: object) -> object:
    bonuses = _equipment_value(spec, "bonuses", None)
    return bonuses if bonuses is not None else EquipmentBonuses()


def _equipment_bonus_value(bonuses: object, key: str) -> int:
    if isinstance(bonuses, Mapping):
        value = bonuses.get(key, 0)
    else:
        value = getattr(bonuses, key, 0)
    if isinstance(value, bool):
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _normalized_equipment_slot(slot: object) -> str:
    if not isinstance(slot, str):
        return ""
    return {"amulet": "neck", "chest": "body"}.get(slot, slot)


def _combat_level_key(combat_skill: object) -> Optional[str]:
    if not isinstance(combat_skill, str) or not combat_skill:
        return None
    return f"{combat_skill}_level"


def _equipment_skill_requirements(spec: object) -> tuple[tuple[str, int, str], ...]:
    raw_requirements = _equipment_value(spec, "skill_requirements", ())
    parsed: list[tuple[str, int, str]] = []
    if isinstance(raw_requirements, Mapping):
        requirement_iterable = raw_requirements.items()
    elif isinstance(raw_requirements, (tuple, list)):
        requirement_iterable = raw_requirements
    else:
        requirement_iterable = ()
    for requirement in requirement_iterable:
        if isinstance(requirement, Mapping):
            combat_skill = requirement.get("skill")
            raw_level = requirement.get("level")
        elif isinstance(requirement, (tuple, list)) and len(requirement) >= 2:
            combat_skill = requirement[0]
            raw_level = requirement[1]
        else:
            continue
        level_key = _combat_level_key(combat_skill)
        required_level = _positive_int(raw_level, 1)
        if isinstance(combat_skill, str) and level_key is not None and required_level > 1:
            parsed.append((combat_skill, required_level, level_key))
    if parsed:
        return tuple(parsed)

    combat_skill = _equipment_value(spec, "combat_skill", None)
    level_key = _combat_level_key(combat_skill)
    required_level = _positive_int(_equipment_value(spec, "required_level", 1), 1)
    if isinstance(combat_skill, str) and level_key is not None and required_level > 1:
        return ((combat_skill, required_level, level_key),)
    return ()


def _combat_skill_label(combat_skill: object) -> str:
    labels = {
        "attack": "Attack",
        "defense": "Defense",
        "ranged": "Ranged",
        "strength": "Strength",
        "magic": "Magic",
        "prayer": "Prayer",
        "constitution": "Constitution",
    }
    if isinstance(combat_skill, str):
        return labels.get(combat_skill, combat_skill.replace("_", " ").title())
    return "Combat"


def equipment_bonus_state_pure(equipment: Mapping[str, str], bonus_item_data: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    """Summarize Mining bonuses from explicitly worn equipment slots."""
    has_glory = False
    varrock_tier = 0
    equipped_by_slot = {
        _normalized_equipment_slot(slot): item_name
        for slot, item_name in equipment.items()
        if isinstance(slot, str) and isinstance(item_name, str)
    }
    for spec in bonus_item_data.values():
        display_name = spec.get("display_name")
        slot = _normalized_equipment_slot(spec.get("equipment_slot"))
        if not isinstance(display_name, str) or equipped_by_slot.get(slot) != display_name:
            continue
        if spec.get("equipment_type") == "gem_chance":
            has_glory = True
        if spec.get("equipment_type") == "extra_ore":
            varrock_tier = max(varrock_tier, _positive_int(spec.get("tier", 0), 0))
    return {"has_glory": has_glory, "varrock_armour_tier": varrock_tier}


def can_equip_item_pure(
    item_name: str,
    equipment_data: Mapping[str, object],
    player_data: Mapping[str, object],
) -> tuple[bool, str]:
    spec = equipment_data.get(item_name)
    if spec is None:
        return False, "Item is not equippable"
    for combat_skill, required_level, level_key in _equipment_skill_requirements(spec):
        current_level = _positive_int(player_data.get(level_key, 1), 1)
        if current_level < required_level:
            return False, f"Requires level {required_level} {_combat_skill_label(combat_skill)}"
    equipment = player_data.get("equipment", {}) or {}
    item_god = _mage_arena_god_for_item(item_name)
    if item_name in MAGE_ARENA_GOD_STAVES:
        cape = equipment.get("cape")
        cape_god = _mage_arena_god_for_item(cape)
        if cape_god and cape_god != item_god:
            return False, f"{item_name} cannot be equipped with {cape}"
    elif item_name in MAGE_ARENA_GOD_CAPES:
        weapon = equipment.get("weapon")
        weapon_god = _mage_arena_god_for_item(weapon)
        if weapon_god and weapon_god != item_god:
            return False, f"{item_name} cannot be equipped with {weapon}"
    return True, ""


def _mage_arena_god_for_item(item_name):
    for god_id, row in MAGE_ARENA_GOD_DATA.items():
        if item_name in {row["cape"], row["staff"]}:
            return god_id
    return None


def equip_item_pure(
    item_name: str,
    inventory: Mapping[str, int],
    equipment: Mapping[str, str],
    equipment_data: Mapping[str, object],
) -> tuple[dict[str, int], dict[str, str], bool]:
    spec = equipment_data.get(item_name)
    if spec is None:
        return dict(inventory), dict(equipment), False
    slot = _equipment_value(spec, "slot", None)
    if not isinstance(slot, str) or not slot:
        return dict(inventory), dict(equipment), False
    owned_qty = inventory.get(item_name, 0)
    if owned_qty <= 0:
        return dict(inventory), dict(equipment), False
    item_god = _mage_arena_god_for_item(item_name)
    if item_name in MAGE_ARENA_GOD_STAVES:
        equipped_god = _mage_arena_god_for_item(equipment.get("cape"))
        if equipped_god and equipped_god != item_god:
            return dict(inventory), dict(equipment), False
    elif item_name in MAGE_ARENA_GOD_CAPES:
        equipped_god = _mage_arena_god_for_item(equipment.get("weapon"))
        if equipped_god and equipped_god != item_god:
            return dict(inventory), dict(equipment), False

    new_inventory = dict(inventory)
    new_equipment = {
        equipped_slot: equipped_item
        for equipped_slot, equipped_item in equipment.items()
        if isinstance(equipped_slot, str) and isinstance(equipped_item, str)
    }
    new_inventory[item_name] = owned_qty - 1

    displaced = new_equipment.get(slot)
    if displaced:
        new_inventory[displaced] = new_inventory.get(displaced, 0) + 1
    new_equipment[slot] = item_name

    two_handed = bool(_equipment_value(spec, "two_handed", False))
    if slot == "weapon" and two_handed:
        shield_item = new_equipment.pop("shield", None)
        if shield_item:
            new_inventory[shield_item] = new_inventory.get(shield_item, 0) + 1
    elif slot == "shield":
        weapon_item = new_equipment.get("weapon")
        if weapon_item:
            weapon_spec = equipment_data.get(weapon_item)
            if bool(_equipment_value(weapon_spec, "two_handed", False)):
                removed_weapon = new_equipment.pop("weapon")
                new_inventory[removed_weapon] = new_inventory.get(removed_weapon, 0) + 1

    return new_inventory, new_equipment, True


def unequip_item_pure(
    slot: str,
    inventory: Mapping[str, int],
    equipment: Mapping[str, str],
) -> tuple[dict[str, int], dict[str, str], bool]:
    if slot not in equipment or not isinstance(equipment.get(slot), str):
        return dict(inventory), dict(equipment), False
    new_inventory = dict(inventory)
    new_equipment = {
        equipped_slot: equipped_item
        for equipped_slot, equipped_item in equipment.items()
        if isinstance(equipped_slot, str) and isinstance(equipped_item, str)
    }
    item_name = new_equipment.pop(slot)
    new_inventory[item_name] = new_inventory.get(item_name, 0) + 1
    return new_inventory, new_equipment, True


def equipment_stat_totals_pure(
    equipment: Mapping[str, str],
    equipment_data: Mapping[str, object],
) -> EquipmentBonuses:
    totals = {field: 0 for field in EQUIPMENT_BONUS_FIELDS}
    for item_name in equipment.values():
        if not isinstance(item_name, str):
            continue
        spec = equipment_data.get(item_name)
        if spec is None:
            continue
        bonuses = _equipment_bonuses(spec)
        for field in EQUIPMENT_BONUS_FIELDS:
            totals[field] += _equipment_bonus_value(bonuses, field)
    return EquipmentBonuses(**totals)
