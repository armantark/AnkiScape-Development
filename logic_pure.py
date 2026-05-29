# logic_pure.py - Pure logic functions for AnkiScape (no Anki dependencies)

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

def can_smelt_any_bar_pure(inventory, smithing_level, bar_data):
    """
    Return True if at least one bar can be smelted given the player's smithing_level and inventory.
    bar_data format: { bar_name: {"level": int, "ore_required": {ore: amount}} }
    """
    for _, data in bar_data.items():
        if smithing_level >= data.get("level", 0):
            if all(inventory.get(ore, 0) >= amount for ore, amount in data.get("ore_required", {}).items()):
                return True
    return False

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
    new_inv = dict(inventory)
    for material, amount in spec.get("requirements", {}).items():
        new_inv[material] = new_inv.get(material, 0) - amount
    new_inv[item] = new_inv.get(item, 0) + 1
    exp = spec.get("exp", 0)
    return new_inv, exp, True

def apply_smelt_pure(bar_name, inventory, bar_data):
    """
    Attempt to smelt a specific bar. Returns (new_inventory, exp, success).
    Does not mutate input inventory. Only checks materials; level checks should be handled by caller.
    bar_data format: { bar_name: {"exp": float, "ore_required": {ore: amount}} }
    """
    spec = bar_data.get(bar_name)
    if not spec:
        return inventory, 0, False
    requirements = spec.get("ore_required", {})
    # Check materials
    if not all(inventory.get(ore, 0) >= amount for ore, amount in requirements.items()):
        return inventory, 0, False
    # Deduct and add bar
    new_inv = dict(inventory)
    for ore, amount in requirements.items():
        new_inv[ore] = new_inv.get(ore, 0) - amount
    new_inv[bar_name] = new_inv.get(bar_name, 0) + 1
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
    new_inv[tree_name] = new_inv.get(tree_name, 0) + 1
    exp = tree_data[tree_name].get("exp", 0)
    return new_inv, exp, True

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
