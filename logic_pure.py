# logic_pure.py - Pure logic functions for AnkiScape (no Anki dependencies)
from __future__ import annotations

from math import sqrt
from typing import Iterable, Mapping, Optional

try:
    from .equipment_data import EQUIPMENT_BONUS_FIELDS, EquipmentBonuses
except ImportError:
    from equipment_data import EQUIPMENT_BONUS_FIELDS, EquipmentBonuses

def get_exp_to_next_level(player_data, EXP_TABLE):
    """Return exp needed to reach the next level for Mining.
    Supports EXP_TABLE as list or dict. Uses mining_exp, falls back to legacy total_exp.
    When at or beyond max level or threshold missing, returns 0.
    """
    current_level = player_data.get("mining_level", player_data.get("level", 1))
    if current_level >= 99:
        return 0
    # Determine threshold for next level from EXP_TABLE
    if isinstance(EXP_TABLE, dict):
        threshold = EXP_TABLE.get(current_level)
    else:
        try:
            threshold = EXP_TABLE[current_level]
        except (IndexError, TypeError):
            threshold = None
    if threshold is None:
        return 0
    skill_exp = player_data.get("mining_exp", player_data.get("total_exp", 0))
    needed = threshold - skill_exp
    return needed if needed > 0 else 0

def calculate_new_level(skill_exp, current_level, EXP_TABLE):
    """
    Calculate the new level for a skill given experience, current level, and EXP_TABLE.
    Supports EXP_TABLE as a dict (level -> threshold) or a list where index (level-1) stores threshold.
    Returns the new level (int).
    """
    new_level = current_level
    while new_level < 99:
        # Determine threshold to reach next level (new_level+1)
        if isinstance(EXP_TABLE, dict):
            threshold = EXP_TABLE.get(new_level + 1)
        else:
            try:
                # In list form, index equals current level (new_level) for threshold to reach next level
                threshold = EXP_TABLE[new_level]
            except (IndexError, TypeError):
                threshold = None

        if threshold is None or skill_exp < threshold:
            break
        new_level += 1
    return new_level

def get_newly_completed_achievements(player_data, ACHIEVEMENTS):
    """
    Returns a list of achievement names that are newly completed (not yet in player_data["completed_achievements"])
    """
    completed = set(player_data.get("completed_achievements", []))
    newly_completed = []
    for name, data in ACHIEVEMENTS.items():
        if name not in completed and data["condition"](player_data):
            newly_completed.append(name)
    return newly_completed

def calculate_probability_with_level(player_level, base_probability, level_bonus_factor, source_probability, cap=0.95):
    """
    Compute success probability given a player's level and base probabilities.
    Probability = min(base_probability + player_level * level_bonus_factor, cap) * source_probability
    """
    level_bonus = player_level * level_bonus_factor
    return min(base_probability + level_bonus, cap) * source_probability

def pick_gem(gem_data, r):
    """
    Deterministically pick a gem given gem_data and a random draw r in [0, 1).
    gem_data: { name: { "probability": float }, ... }
    Returns the gem name, or None if r exceeds the total probability mass.
    """
    cumulative = 0.0
    for gem, data in gem_data.items():
        cumulative += data.get("probability", 0.0)
        if r < cumulative:
            return gem
    return None


def pick_weighted_item_pure(weighted_items, r, total_weight=None):
    """Pick an item from source-style weighted slots using a [0, 1) roll."""
    if total_weight is None:
        total_weight = sum(_positive_int(item.get("weight", 0), 0) for item in weighted_items)
    if total_weight <= 0:
        return None
    threshold = max(0.0, min(float(r), 0.999999999)) * total_weight
    cumulative = 0
    for item in weighted_items:
        cumulative += _positive_int(item.get("weight", 0), 0)
        if threshold < cumulative:
            return item.get("item")
    last = weighted_items[-1] if weighted_items else {}
    return last.get("item")

def _requirements_from_spec(spec):
    return spec.get("requirements") or spec.get("ore_required", {})


def can_smelt_any_bar_pure(inventory, smithing_level, bar_data):
    """
    Return True if at least one bar can be smelted given the player's smithing_level and inventory.
    bar_data format: { bar_name: {"level": int, "ore_required": {ore: amount}} }
    """
    for _, data in bar_data.items():
        if data.get("station") not in (None, "furnace"):
            continue
        if smithing_level >= data.get("level", 0):
            if all(inventory.get(material, 0) >= amount for material, amount in _requirements_from_spec(data).items()):
                return True
    return False


def has_smithing_materials_pure(target, inventory, smithing_data):
    """Return True when inventory satisfies a Smithing recipe's material needs."""
    spec = smithing_data.get(target)
    if not spec:
        return False
    for material, amount in _requirements_from_spec(spec).items():
        if inventory.get(material, 0) < amount:
            return False
    return True


def can_smith_item_pure(smithing_level, inventory, target, smithing_data):
    """Return True if level and materials allow one Smithing recipe action."""
    spec = smithing_data.get(target)
    if not spec:
        return False
    if smithing_level < spec.get("level", 1):
        return False
    return has_smithing_materials_pure(target, inventory, smithing_data)


def can_smith_any_pure(inventory, smithing_level, smithing_data):
    """Return True if any smelt or forge recipe can run right now."""
    return any(
        can_smith_item_pure(smithing_level, inventory, target, smithing_data)
        for target in smithing_data
    )


def sanitize_review_action_multiplier(value, default=1, minimum=1, maximum=10):
    """Return the integer number of game action ticks one review can run."""
    if isinstance(value, bool):
        return default
    try:
        multiplier = float(value)
    except (TypeError, ValueError):
        return default
    if multiplier != multiplier:
        return default
    if multiplier < minimum:
        return minimum
    if multiplier > maximum:
        return maximum
    return int(multiplier)


def sanitize_xp_multiplier(value, default=1.0, minimum=0.0, maximum=100.0):
    """Compatibility wrapper for old configs/tests; review rewards no longer use it."""
    if isinstance(value, bool):
        return default
    try:
        multiplier = float(value)
    except (TypeError, ValueError):
        return default
    if multiplier != multiplier:
        return default
    if multiplier < minimum:
        return minimum
    if multiplier > maximum:
        return maximum
    return multiplier


def create_soft_clay_pure(inventory):
    """
    Deduct 1 "Clay" and add 1 "Soft clay" if possible.
    Returns (new_inventory, success: bool). Does not mutate input.
    """
    current_clay = inventory.get("Clay", 0)
    if current_clay > 0:
        new_inv = dict(inventory)
        new_inv["Clay"] = current_clay - 1
        new_inv["Soft clay"] = new_inv.get("Soft clay", 0) + 1
        return new_inv, True
    return inventory, False


def _positive_int(value, default=1):
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _max_batches_for_requirements(requirements, inventory, batch_size):
    if not requirements:
        return batch_size
    possible = batch_size
    for material, amount in requirements.items():
        per_batch = _positive_int(amount)
        possible = min(possible, inventory.get(material, 0) // per_batch)
    return possible

def has_crafting_materials_pure(item, inventory, crafting_data):
    """Return True if inventory satisfies crafting requirements for the given item.
    Unknown items return False.
    """
    spec = crafting_data.get(item)
    if not spec:
        return False
    requirements = spec.get("requirements", {})
    for material, amount in requirements.items():
        if inventory.get(material, 0) < amount:
            return False
    return True

def apply_crafting_pure(item, inventory, crafting_data):
    """If inventory meets requirements, deduct inputs and return (new_inventory, exp, success).
    Does not mutate input inventory. Unknown items return (inventory, 0, False).
    """
    spec = crafting_data.get(item)
    if not spec or not has_crafting_materials_pure(item, inventory, crafting_data):
        return inventory, 0, False
    requirements = spec.get("requirements", {})
    # Crafting is XP-bearing; batching is reserved for no-XP Utility/Activities.
    batch_count = _max_batches_for_requirements(requirements, inventory, 1)
    if batch_count <= 0:
        return inventory, 0, False
    new_inv = dict(inventory)
    for material, amount in requirements.items():
        new_inv[material] = new_inv.get(material, 0) - (_positive_int(amount) * batch_count)
    output_item = spec.get("output_item", item)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + (output_qty * batch_count)
    exp = spec.get("exp", 0) * batch_count
    return new_inv, exp, True


def can_perform_utility_activity_pure(inventory, activity_key, utility_activity_data):
    """Return True if a no-XP Utility/Activity can run for at least one batch."""
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return False
    openable_items = spec.get("openable_items")
    if openable_items:
        return any(inventory.get(item_name, 0) > 0 for item_name in openable_items)
    requirements = spec.get("requirements", {})
    batch_size = _positive_int(spec.get("batch_size", 1))
    return _max_batches_for_requirements(requirements, inventory, batch_size) > 0


def apply_utility_activity_pure(activity_key, inventory, utility_activity_data):
    """Apply a no-XP Utility/Activity and return (inventory, exp, success, processed)."""
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return inventory, 0, False, 0
    requirements = spec.get("requirements", {})
    batch_size = _positive_int(spec.get("batch_size", 1))
    batch_count = _max_batches_for_requirements(requirements, inventory, batch_size)
    if batch_count <= 0:
        return inventory, 0, False, 0

    new_inv = dict(inventory)
    for material, amount in requirements.items():
        new_inv[material] = new_inv.get(material, 0) - (_positive_int(amount) * batch_count)
    output_item = spec.get("output_item", activity_key)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + (output_qty * batch_count)
    return new_inv, 0, True, batch_count

def apply_smelt_pure(bar_name, inventory, bar_data):
    """
    Attempt to smelt a specific bar. Returns (new_inventory, exp, success).
    Does not mutate input inventory. Only checks materials; level checks should be handled by caller.
    bar_data format: { bar_name: {"exp": float, "ore_required": {ore: amount}} }
    """
    spec = bar_data.get(bar_name)
    if not spec:
        return inventory, 0, False
    requirements = _requirements_from_spec(spec)
    # Check materials
    if not all(inventory.get(ore, 0) >= amount for ore, amount in requirements.items()):
        return inventory, 0, False
    # Deduct and add bar
    new_inv = dict(inventory)
    for ore, amount in requirements.items():
        new_inv[ore] = new_inv.get(ore, 0) - amount
    output_item = spec.get("output_item", bar_name)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True


def apply_smithing_pure(target, inventory, smithing_data):
    """Apply one source-backed Smithing recipe, smelt or forge.

    Smithing actions are XP-bearing, so this intentionally does not honor a
    recipe-level batch size. Review pacing runs multiple normal actions when the
    global actions-per-review setting is greater than one.
    """
    spec = smithing_data.get(target)
    if not spec or not has_smithing_materials_pure(target, inventory, smithing_data):
        return inventory, 0, False

    new_inv = dict(inventory)
    for material, amount in _requirements_from_spec(spec).items():
        new_inv[material] = new_inv.get(material, 0) - amount

    output_item = spec.get("output_item", target)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True

def apply_woodcutting_pure(tree_name, inventory, tree_data, r_action, success_probability):
    """
    Attempt a woodcutting action. Returns (new_inventory, exp_gained, success).
    Does not mutate input inventory. The caller provides a random draw and success probability.
    """
    success = r_action < success_probability
    if not success:
        return inventory, 0, False
    new_inv = dict(inventory)
    output_item = tree_data[tree_name].get("output_item", tree_name)
    if output_item:
        new_inv[output_item] = new_inv.get(output_item, 0) + 1
    exp = tree_data[tree_name].get("exp", 0)
    return new_inv, exp, True


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
        if best is None or spec.get("ratio", 0) > best.get("ratio", 0):
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
        if best is None or power > best_power:
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
    combat_skill = _equipment_value(spec, "combat_skill", None)
    level_key = _combat_level_key(combat_skill)
    required_level = _positive_int(_equipment_value(spec, "required_level", 1), 1)
    if level_key is None:
        return True, ""
    current_level = _positive_int(player_data.get(level_key, 1), 1)
    if current_level < required_level:
        return False, f"Requires level {required_level} {_combat_skill_label(combat_skill)}"
    return True, ""


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


def bank_gear_rows_pure(player_data, pickaxe_data, axe_data, _bonus_item_data):
    """Read-only gear summary the Bank tab renders below the inventory.

    Why surface the *best owned* tool rather than the raw bound toolbelt id:
    the toolbelt is auto-resolved (best_*_pure already picks the strongest
    usable tool from bound ids + bank items), and the owner has decided that
    binding a tool is "basically a formality." Showing the active tool keeps
    the bank honest as the player smiths/loots upgrades, without any equip step.

    Worn equipment now lives in player_data["equipment"]. The Bank frontend still
    uses this read-only summary until the dedicated Equipment tab lands.

    Returns {"toolbelt": [(label, display_name), ...],
             "equipped": [(slot, display_name), ...]}.
    """
    inventory = player_data.get("inventory", {}) or {}
    toolbelt = player_data.get("toolbelt", {}) or {}
    toolbelt_rows: list = []
    pick = best_mining_pickaxe_pure(
        player_data.get("mining_level", 1), inventory, toolbelt, pickaxe_data
    )
    if pick is not None:
        toolbelt_rows.append(("Pickaxe", str(pick.get("display_name", ""))))
    axe = best_woodcutting_axe_pure(
        player_data.get("woodcutting_level", 1), inventory, toolbelt, axe_data
    )
    if axe is not None:
        toolbelt_rows.append(("Hatchet", str(axe.get("display_name", ""))))

    equipped_rows: list = []
    equipment = player_data.get("equipment", {}) or {}
    if isinstance(equipment, Mapping):
        for slot, item_name in equipment.items():
            if isinstance(slot, str) and isinstance(item_name, str):
                equipped_rows.append((slot, item_name))
    return {"toolbelt": toolbelt_rows, "equipped": equipped_rows}


def mining_source_roll_chance_pure(mining_level, target_spec, pickaxe_spec):
    """Approximate the 2011Scape raw mining roll before Anki pacing is applied."""
    low = float(target_spec.get("low_chance", 0))
    high = float(target_spec.get("high_chance", 0))
    level_progress = max(0.0, min((float(mining_level) - 1.0) / 98.0, 1.0))
    interpolated = low + ((high - low) * level_progress)
    ratio = float(pickaxe_spec.get("ratio", 1.0))
    if "dragon" in str(pickaxe_spec.get("display_name", "")).lower():
        ratio *= 1.12
    return max(0.0, min((interpolated * ratio) / 255.0, 1.0))


def calculate_mining_success_probability_pure(mining_level, target_spec, pickaxe_spec, minimum=0.05, scale=0.62, cap=0.95):
    """Translate source mining odds into one review-scale success probability."""
    source_chance = mining_source_roll_chance_pure(mining_level, target_spec, pickaxe_spec)
    return max(0.0, min(minimum + (sqrt(source_chance) * scale), cap))


def can_mine_target_pure(mining_level, target_id, ore_data, inventory, toolbelt, pickaxe_data):
    spec = ore_data.get(target_id)
    if not spec:
        return False
    if mining_level < spec.get("level", 1):
        return False
    return best_mining_pickaxe_pure(mining_level, inventory, toolbelt, pickaxe_data) is not None


def woodcutting_source_roll_chance_pure(woodcutting_level, target_spec, axe_spec):
    """Approximate the 2011Scape raw chop roll before Anki pacing is applied."""
    low = float(target_spec.get("low_chance", 0)) * float(axe_spec.get("ratio", 1.0))
    high = float(target_spec.get("high_chance", 0)) * float(axe_spec.get("ratio", 1.0))
    level_progress = max(0.0, min((float(woodcutting_level) - 1.0) / 98.0, 1.0))
    interpolated = low + ((high - low) * level_progress)
    return max(0.0, min(interpolated / 255.0, 1.0))


def calculate_woodcutting_success_probability_pure(woodcutting_level, target_spec, axe_spec, minimum=0.20, scale=0.72, cap=0.95):
    """Translate source chop odds into a review-scale success probability.

    2011Scape rolls every few game ticks; AnkiScape rolls once per eligible card.
    The square-root adapter preserves ordering and tool upgrades while avoiding
    extremely dry high-tier trees at normal review cadence.
    """
    source_chance = woodcutting_source_roll_chance_pure(woodcutting_level, target_spec, axe_spec)
    return max(0.0, min(minimum + (sqrt(source_chance) * scale), cap))


def can_chop_woodcutting_target_pure(woodcutting_level, target_id, tree_data, inventory, toolbelt, axe_data):
    spec = tree_data.get(target_id)
    if not spec:
        return False
    if woodcutting_level < spec.get("level", 1):
        return False
    return best_woodcutting_axe_pure(woodcutting_level, inventory, toolbelt, axe_data) is not None


def apply_woodcutting_action_pure(
    target_id,
    inventory,
    tree_data,
    woodcutting_level,
    axe_spec,
    r_action,
    r_nest_drop=None,
    r_nest_type=None,
    nest_drop_table=None,
    nest_drop_chance=0.0,
):
    spec = tree_data.get(target_id)
    if not spec or not axe_spec:
        return inventory, 0, False, None, None
    success_probability = calculate_woodcutting_success_probability_pure(woodcutting_level, spec, axe_spec)
    if r_action >= success_probability:
        return inventory, 0, False, None, None

    new_inv = dict(inventory)
    output_item = spec.get("output_item")
    if output_item:
        new_inv[output_item] = new_inv.get(output_item, 0) + 1

    nest_item = None
    if r_nest_drop is not None and r_nest_type is not None and nest_drop_table and r_nest_drop < nest_drop_chance:
        nest_item = pick_weighted_item_pure(nest_drop_table, r_nest_type)
        if nest_item:
            new_inv[nest_item] = new_inv.get(nest_item, 0) + 1

    return new_inv, spec.get("exp", 0), True, output_item, nest_item


def can_open_bird_nests_pure(inventory, nest_open_tables):
    return any(inventory.get(input_item, 0) > 0 for input_item in nest_open_tables)


def apply_open_bird_nests_pure(inventory, nest_open_tables, rolls=(), batch_size=28):
    """Open up to batch_size source bird nests and return inert contents."""
    remaining = _positive_int(batch_size, 28)
    roll_iter = iter(rolls or ())
    new_inv = dict(inventory)
    opened = 0
    outputs = {}
    for input_item, table in nest_open_tables.items():
        while remaining > 0 and new_inv.get(input_item, 0) > 0:
            new_inv[input_item] = new_inv.get(input_item, 0) - 1
            opened += 1
            remaining -= 1

            guaranteed_item = table.get("guaranteed_item")
            if guaranteed_item:
                new_inv[guaranteed_item] = new_inv.get(guaranteed_item, 0) + 1
                outputs[guaranteed_item] = outputs.get(guaranteed_item, 0) + 1

            weighted_items = table.get("rolls", ())
            total_weight = table.get("total_weight")
            try:
                roll = next(roll_iter)
            except StopIteration:
                roll = 0.0
            rolled_item = pick_weighted_item_pure(weighted_items, roll, total_weight)
            if rolled_item:
                new_inv[rolled_item] = new_inv.get(rolled_item, 0) + 1
                outputs[rolled_item] = outputs.get(rolled_item, 0) + 1
    return new_inv, opened > 0, opened, outputs

def apply_mining_pure(
    ore_name,
    inventory,
    ore_data,
    gem_data,
    r_action,
    success_probability,
    r_gem_chance=None,
    r_gem_pick=None,
    gem_drop_chance=1/256,
):
    """
    Attempt a mining action. Returns (new_inventory, exp_gained, success, gem_name).
    If success, may also award a gem using provided randoms and gem_drop_chance.
    Does not mutate input inventory.
    """
    success = r_action < success_probability
    if not success:
        return inventory, 0, False, None
    new_inv = dict(inventory)
    new_inv[ore_name] = new_inv.get(ore_name, 0) + 1
    exp = ore_data[ore_name].get("exp", 0)

    gem_name = None
    if r_gem_chance is not None and r_gem_pick is not None and r_gem_chance < gem_drop_chance:
        gem_name = pick_gem(gem_data, r_gem_pick)
        if gem_name:
            new_inv[gem_name] = new_inv.get(gem_name, 0) + 1
            exp += gem_data[gem_name].get("exp", 0)
    return new_inv, exp, True, gem_name


def apply_mining_action_pure(
    target_id,
    inventory,
    ore_data,
    mining_level,
    pickaxe_spec,
    r_action,
    r_output=None,
    r_gem_chance=None,
    r_gem_pick=None,
    gem_drop_table=(),
    gem_drop_chance=1 / 256,
    varrock_armour_tier=0,
):
    """Apply one source-shaped Anki Mining attempt.

    Returns (inventory, base_exp, success, output_item, gem_item, extra_output).
    Random gem drops are inventory-only side drops; they do not add Mining XP.
    """
    spec = ore_data.get(target_id)
    if not spec or not pickaxe_spec:
        return inventory, 0, False, None, None, None
    success_probability = calculate_mining_success_probability_pure(mining_level, spec, pickaxe_spec)
    if r_action >= success_probability:
        return inventory, 0, False, None, None, None

    new_inv = dict(inventory)
    output_item = spec.get("output_item")
    base_exp = spec.get("exp", 0)
    weighted_outputs = spec.get("weighted_outputs", ())
    if weighted_outputs:
        picked = pick_weighted_item_pure(weighted_outputs, 0.0 if r_output is None else r_output)
        if picked:
            output_item = picked
            for weighted in weighted_outputs:
                if weighted.get("item") == picked:
                    base_exp = weighted.get("exp", base_exp)
                    break
    alternate_output_item = spec.get("alternate_output_item")
    alternate_output_level = spec.get("alternate_output_level")
    if isinstance(alternate_output_item, str) and isinstance(alternate_output_level, int) and mining_level >= alternate_output_level:
        output_item = alternate_output_item

    if output_item:
        new_inv[output_item] = new_inv.get(output_item, 0) + 1

    extra_output = None
    required_varrock_tier = spec.get("varrock_armour_tier")
    if (
        output_item
        and isinstance(required_varrock_tier, int)
        and required_varrock_tier > 0
        and varrock_armour_tier >= required_varrock_tier
    ):
        extra_output = output_item
        new_inv[output_item] = new_inv.get(output_item, 0) + 1

    gem_item = None
    if (
        spec.get("allows_random_gems", True)
        and r_gem_chance is not None
        and r_gem_pick is not None
        and gem_drop_table
        and r_gem_chance < gem_drop_chance
    ):
        gem_item = pick_weighted_item_pure(gem_drop_table, r_gem_pick)
        if gem_item:
            new_inv[gem_item] = new_inv.get(gem_item, 0) + 1

    return new_inv, base_exp, True, output_item, gem_item, extra_output


def can_mine_ore_pure(mining_level, ore_name, ore_data):
    """Return True if mining_level meets the ore's required level."""
    spec = ore_data.get(ore_name)
    if not spec:
        return False
    return mining_level >= spec.get("level", 1)


def can_cut_tree_pure(woodcutting_level, tree_name, tree_data):
    """Return True if woodcutting_level meets the tree's required level."""
    spec = tree_data.get(tree_name)
    if not spec:
        return False
    return woodcutting_level >= spec.get("level", 1)


def can_craft_item_pure(crafting_level, inventory, item, crafting_data):
    """Return True if level and materials allow crafting the item."""
    spec = crafting_data.get(item)
    if not spec:
        return False
    if crafting_level < spec.get("level", 1):
        return False
    return has_crafting_materials_pure(item, inventory, crafting_data)


def has_fletching_materials_pure(target, inventory, fletching_data):
    """Return True when inventory satisfies a Fletching target's material needs."""
    spec = fletching_data.get(target)
    if not spec:
        return False
    for material, amount in spec.get("requirements", {}).items():
        if inventory.get(material, 0) < amount:
            return False
    return True


def can_fletch_item_pure(fletching_level, inventory, target, fletching_data):
    """Return True if level and materials allow the Fletching target."""
    spec = fletching_data.get(target)
    if not spec:
        return False
    if fletching_level < spec.get("level", 1):
        return False
    return has_fletching_materials_pure(target, inventory, fletching_data)


def apply_fletching_pure(target, inventory, fletching_data):
    """Consume logs and produce the selected Fletching output.

    Fletching is intentionally modeled as a processing skill like Crafting:
    the caller handles level checks so UI/runtime code can report a precise
    locked reason, while this pure function owns inventory mutation safety.
    """
    spec = fletching_data.get(target)
    if not spec or not has_fletching_materials_pure(target, inventory, fletching_data):
        return inventory, 0, False

    new_inv = dict(inventory)
    for material, amount in spec.get("requirements", {}).items():
        new_inv[material] = new_inv.get(material, 0) - amount

    output_item = spec.get("output_item", target)
    output_qty = spec.get("output_qty", 1)
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True


def firemaking_source_roll_chance_pure(firemaking_level, target_spec):
    """Approximate the 2011Scape raw Firemaking roll before Anki pacing."""
    low = float(target_spec.get("low_chance", 65))
    high = float(target_spec.get("high_chance", 513))
    level_progress = max(0.0, min((float(firemaking_level) - 1.0) / 98.0, 1.0))
    interpolated = low + ((high - low) * level_progress)
    return max(0.0, min(interpolated / 255.0, 1.0))


def calculate_firemaking_success_probability_pure(
    firemaking_level,
    target_spec,
    minimum=0.30,
    scale=0.65,
    overlevel_window=40,
    cap=0.95,
):
    """Translate source lighting odds into one review-scale success probability.

    The source chance mostly depends on Firemaking level, not the log tier. To
    make higher-level logs feel slower near unlock in AnkiScape, this adapter
    also applies a target-level curve: old logs become comfortable as the player
    overlevels them, while newly unlocked logs start stickier.
    """
    source_chance = firemaking_source_roll_chance_pure(firemaking_level, target_spec)
    source_adapter = min(0.20 + (sqrt(source_chance) * 0.72), cap)
    required_level = _positive_int(target_spec.get("level", 1), 1)
    overlevel = max(0.0, float(firemaking_level) - float(required_level))
    window = max(float(overlevel_window), 1.0)
    tier_progress = max(0.0, min((overlevel + 1.0) / window, 1.0))
    tier_adapter = min(minimum + (sqrt(tier_progress) * scale), cap)
    return max(0.0, min(source_adapter, tier_adapter, cap))


def has_firemaking_materials_pure(target, inventory, firemaking_data):
    """Return True when inventory has the log/root for one Firemaking action."""
    spec = firemaking_data.get(target)
    if not spec:
        return False
    for material, amount in spec.get("requirements", {}).items():
        if inventory.get(material, 0) < amount:
            return False
    return True


def can_burn_firemaking_target_pure(firemaking_level, inventory, target, firemaking_data):
    """Return True if level and materials allow one Firemaking attempt."""
    spec = firemaking_data.get(target)
    if not spec:
        return False
    if firemaking_level < spec.get("level", 1):
        return False
    return has_firemaking_materials_pure(target, inventory, firemaking_data)


def can_burn_any_firemaking_target_pure(inventory, firemaking_level, firemaking_data):
    """Return True if any Firemaking target can be attempted right now."""
    return any(
        can_burn_firemaking_target_pure(firemaking_level, inventory, target, firemaking_data)
        for target in firemaking_data
    )


def apply_firemaking_action_pure(target, inventory, firemaking_data, firemaking_level, r_action):
    """Apply one Firemaking attempt.

    Returns (inventory, base_exp, success, output_item). Failed attempts consume
    no log and award no XP/items, matching AnkiScape's gathering-style pacing.
    """
    spec = firemaking_data.get(target)
    if not spec or not has_firemaking_materials_pure(target, inventory, firemaking_data):
        return inventory, 0, False, None
    success_probability = calculate_firemaking_success_probability_pure(firemaking_level, spec)
    if r_action >= success_probability:
        return inventory, 0, False, None

    new_inv = dict(inventory)
    for material, amount in spec.get("requirements", {}).items():
        new_inv[material] = new_inv.get(material, 0) - amount
    output_item = spec.get("output_item", "Ashes")
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True, output_item
