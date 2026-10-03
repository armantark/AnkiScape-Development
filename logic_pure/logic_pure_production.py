"""logic_pure_production.py - split out of logic_pure.py; see that module's header."""

from __future__ import annotations

from math import comb, floor, sqrt

from typing import Iterable, Mapping, Optional

from ..core.tool_belt import recipe_without_belt_tools
from ..logic.skilling_boost_logic import skilling_target_level_available_pure

from .logic_pure_gathering import (  # noqa: F401  (re-export)
    _AGILITY_DOUBLE_CATCH_LEVELS,
    _hunter_outputs_from_spec,
    _scape2011_interpolate_255,
    apply_fishing_action_pure,
    apply_hunter_action_pure,
    apply_mining_action_pure,
    apply_mining_pure,
    apply_open_bird_nests_pure,
    apply_woodcutting_action_pure,
    apply_woodcutting_processing_action_pure,
    apply_woodcutting_pure,
    calculate_fishing_success_probability_pure,
    calculate_hunter_success_probability_pure,
    calculate_mining_success_probability_pure,
    calculate_woodcutting_success_probability_pure,
    can_chop_woodcutting_target_pure,
    can_cut_tree_pure,
    can_fish_any_pure,
    can_fish_method_pure,
    can_hunt_target_pure,
    can_mine_ore_pure,
    can_mine_target_pure,
    can_open_bird_nests_pure,
    eligible_fishing_fish_pure,
    fishing_agility_double_catch_chance_pure,
    fishing_method_locked_reasons_pure,
    fishing_source_roll_chance_pure,
    has_fishing_bait_pure,
    has_hunter_materials_pure,
    has_hunter_tools_pure,
    hunter_source_roll_chance_pure,
    hunter_target_locked_reasons_pure,
    mining_source_roll_chance_pure,
    mining_target_locked_reasons_pure,
    missing_hunter_tools_pure,
    woodcutting_source_roll_chance_pure,
    woodcutting_target_locked_reasons_pure,
)

from .logic_pure_quest import (  # noqa: F401  (re-export)
    QUEST_COMBAT_DEFAULT_BURST_TICKS,
    _QUEST_COMBAT_BONUS_ALIASES,
    _QUEST_COMBAT_PREREQUISITE_BLOCKER_KINDS,
    _QUEST_NONCOMBAT_STAGE_BLOCKER_KINDS,
    _QUEST_ROUTE_INHERITANCE,
    _apply_quest_xp_rewards,
    _apply_skill_xp_reward,
    _consume_quest_current_stage_items,
    _dedupe_quest_blockers,
    _has_quest_tool,
    _quest_blocker,
    _quest_choice_current_stage,
    _quest_choice_options,
    _quest_choice_selected,
    _quest_choice_stage,
    _quest_choices_for_stage,
    _quest_combat_attack_style,
    _quest_combat_bonuses,
    _quest_combat_completed_count,
    _quest_combat_configs,
    _quest_combat_default_rng,
    _quest_combat_display,
    _quest_combat_enemy_spec,
    _quest_combat_normalized_bonuses,
    _quest_combat_remaining_count,
    _quest_combat_required_stat_keys,
    _quest_combat_stats,
    _quest_combat_target_id,
    _quest_combat_total_quantity,
    _quest_current_stage_choice_blockers,
    _quest_current_stage_encounter_by_id,
    _quest_current_stage_rows,
    _quest_current_stage_selected_requirements,
    _quest_flag_completed,
    _quest_item_option_reason,
    _quest_item_requirement_text,
    _quest_requirement_blockers,
    _quest_route_completed,
    _quest_stage_item_option_groups,
    _quest_stage_item_pairs,
    _quest_stage_requirement_variant,
    _quest_stage_strings,
    _requirements_for_unlock_rule,
    _skill_requirement_reason,
    _target_ids_for_unlock_rule,
    _trainable_exp_keys,
    ability_unlocked_pure,
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    apply_quest_route_choice_pure,
    can_attempt_quest_review_pure,
    can_progress_quest_pure,
    can_start_quest_pure,
    default_quest_combat_active_encounters_pure,
    normalize_xp_rewards_pure,
    primary_xp_reward_amount_pure,
    quest_availability_state_pure,
    quest_combat_encounter_has_stats_pure,
    quest_combat_encounter_ready_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_current_stage_blockers_pure,
    quest_current_stage_choices_pure,
    quest_current_stage_pure,
    quest_current_stage_resolvable_combat_blockers_pure,
    quest_journal_rows_pure,
    quest_locked_reasons_pure,
    quest_unlock_locked_reasons_pure,
    start_quest_pure,
    target_unlock_locked_reasons_pure,
)

from .logic_pure_progression import (  # noqa: F401  (re-export)
    REVIEW_SUCCESS_CAP,
    REVIEW_SUCCESS_MINIMUM,
    REVIEW_SUCCESS_SCALE,
    calculate_new_level,
    calculate_probability_with_level,
    default_red_sandstone_daily_state_pure,
    get_exp_to_next_level,
    get_newly_completed_achievements,
    normalize_review_success_probability_pure,
    pick_gem,
    pick_weighted_item_pure,
    red_sandstone_daily_remaining_pure,
    red_sandstone_daily_state_pure,
    red_sandstone_review_day_pure,
    sanitize_red_sandstone_daily_state_pure,
    sanitize_review_action_multiplier,
    sanitize_xp_multiplier,
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

from .logic_pure_gathering import (
    _scape2011_interpolate_255,
)

from .logic_pure_quest import (
    quest_unlock_locked_reasons_pure,
    target_unlock_locked_reasons_pure,
)

from .logic_pure_progression import (
    REVIEW_SUCCESS_CAP,
    REVIEW_SUCCESS_MINIMUM,
    REVIEW_SUCCESS_SCALE,
    normalize_review_success_probability_pure,
)

from .logic_pure_state import (
    _positive_int,
)


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
    requirements = dict(spec.get("requirements", {}))
    requirements.update(spec.get("required_items", {}))
    for material, amount in requirements.items():
        if inventory.get(material, 0) < amount:
            return False
    return True


def apply_crafting_pure(item, inventory, crafting_data, random_roll=None):
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
    if spec.get("consume_thread_on_roll") and random_roll == 1:
        new_inv["Thread"] = new_inv.get("Thread", 0) - 1
    output_item = spec.get("output_item", item)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + (output_qty * batch_count)
    # Source-backed byproducts (e.g. molten glass returns the emptied bucket).
    for byproduct, amount in (spec.get("byproducts") or {}).items():
        new_inv[byproduct] = new_inv.get(byproduct, 0) + (_positive_int(amount) * batch_count)
    exp = spec.get("exp", 0) * batch_count
    return new_inv, exp, True


def utility_activity_material_requirements_pure(activity_key, inventory, utility_activity_data):
    """Resolve the exact consumable materials for a no-XP Utility/Activity."""
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return None
    requirements = dict(spec.get("requirements", {}))
    for material, alternatives in spec.get("material_options", {}).items():
        amount = requirements.get(material)
        if amount is None:
            continue
        selected = next(
            (option for option in alternatives if inventory.get(option, 0) >= amount),
            None,
        )
        if selected is None:
            return None
        del requirements[material]
        requirements[selected] = amount
    return requirements


def can_perform_utility_activity_pure(inventory, activity_key, utility_activity_data):
    """Return True if a no-XP Utility/Activity can run for at least one batch."""
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return False
    for option_group in spec.get("required_item_options", ()):
        if not any(inventory.get(item_name, 0) > 0 for item_name in option_group):
            return False
    openable_items = spec.get("openable_items")
    if openable_items:
        return any(inventory.get(item_name, 0) > 0 for item_name in openable_items)
    requirements = utility_activity_material_requirements_pure(
        activity_key, inventory, utility_activity_data
    )
    if requirements is None:
        return False
    batch_size = _positive_int(spec.get("batch_size", 1))
    if _max_batches_for_requirements(requirements, inventory, batch_size) <= 0:
        return False
    any_requirements = spec.get("any_requirements")
    if isinstance(any_requirements, (list, tuple, set)) and any_requirements:
        return any(inventory.get(str(item_name), 0) > 0 for item_name in any_requirements)
    return True


def utility_activity_locked_reasons_pure(player_data, activity_key, utility_activity_data, quest_unlock_rules=()):
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return ("unknown activity",)
    reasons = []
    inventory = player_data.get("inventory", {}) or {}
    if not can_perform_utility_activity_pure(inventory, activity_key, utility_activity_data):
        reasons.append("materials")
    firemaking_level = spec.get("firemaking_level")
    if isinstance(firemaking_level, int) and player_data.get("firemaking_level", 1) < firemaking_level:
        reasons.append(f"Firemaking {firemaking_level}")
    skill_requirements = spec.get("skill_requirements")
    if isinstance(skill_requirements, Mapping):
        for skill_id, required_level in skill_requirements.items():
            level = _positive_int(required_level)
            if _positive_int(player_data.get(f"{skill_id}_level", 1), 1) < level:
                reasons.append(f"{str(skill_id).title()} {level}")
    if spec.get("requires_unskulled") and player_data.get("combat_wilderness_skulled"):
        reasons.append("remove Wilderness skull")
    if spec.get("requires_no_follower"):
        summoning_state = player_data.get("summoning_state")
        follower = (
            summoning_state.get("active_follower")
            if isinstance(summoning_state, Mapping)
            else None
        )
        if isinstance(follower, Mapping) and follower:
            reasons.append("dismiss active follower")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "utility",
            activity_key,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def _utility_outputs_from_spec(spec):
    outputs = spec.get("outputs")
    if isinstance(outputs, Mapping):
        return {
            str(item): _positive_int(amount, 1)
            for item, amount in outputs.items()
            if isinstance(item, str) and item
        }
    output_item = spec.get("output_item")
    if isinstance(output_item, str) and output_item:
        return {output_item: _positive_int(spec.get("output_qty", 1), 1)}
    return {}


def crystal_chest_reward_for_roll_pure(reward_table, roll):
    """Resolve one measured Crystal chest reward row from a normalized roll."""
    total_weight = sum(max(int(row.weight), 0) for row in reward_table)
    if total_weight <= 0:
        return None
    try:
        normalized = float(roll)
    except (TypeError, ValueError):
        normalized = 0.0
    normalized = max(0.0, min(normalized, 0.9999999999999999))
    slot = min(int(normalized * total_weight + 1e-9), total_weight - 1)
    cumulative = 0
    for row in reward_table:
        cumulative += max(int(row.weight), 0)
        if slot < cumulative:
            return row
    return reward_table[-1] if reward_table else None


def apply_crystal_chest_pure(
    inventory,
    reward_table,
    reward_roll,
    *,
    ring_of_wealth=False,
    wealth_trigger_roll=1.0,
    wealth_reward_roll=0.0,
    wealth_improvement_chance=0.0,
):
    """Consume one Crystal key and award the guaranteed dragonstone bundle."""
    if inventory.get("Crystal key", 0) <= 0:
        return inventory, False, "", {}, False

    reward = crystal_chest_reward_for_roll_pure(reward_table, reward_roll)
    if reward is None:
        return inventory, False, "", {}, False

    improved = False
    if ring_of_wealth and float(wealth_trigger_roll) < float(wealth_improvement_chance):
        alternate = crystal_chest_reward_for_roll_pure(reward_table, wealth_reward_roll)
        if (
            alternate is not None
            and int(alternate.value_rank) > int(reward.value_rank)
        ):
            reward = alternate
            improved = True

    outputs = {item: int(amount) for item, amount in reward.outputs}
    updated = dict(inventory)
    updated["Crystal key"] = updated.get("Crystal key", 0) - 1
    for item, amount in outputs.items():
        updated[item] = updated.get(item, 0) + amount
    return updated, True, str(reward.id), outputs, improved


def apply_utility_activity_pure(
    activity_key, inventory, utility_activity_data, r_output=None
):
    """Apply a no-XP Utility/Activity and return (inventory, exp, success, processed)."""
    spec = utility_activity_data.get(activity_key)
    if not spec or not can_perform_utility_activity_pure(
        inventory,
        activity_key,
        utility_activity_data,
    ):
        return inventory, 0, False, 0
    if spec.get("no_op"):
        return dict(inventory), 0, True, 1
    requirements = utility_activity_material_requirements_pure(
        activity_key, inventory, utility_activity_data
    )
    batch_size = _positive_int(spec.get("batch_size", 1))
    batch_count = _max_batches_for_requirements(requirements, inventory, batch_size)
    if batch_count <= 0:
        return inventory, 0, False, 0

    new_inv = dict(inventory)
    for material, amount in requirements.items():
        new_inv[material] = new_inv.get(material, 0) - (_positive_int(amount) * batch_count)
    outputs = _utility_outputs_from_spec(spec)
    weighted_outputs = spec.get("weighted_outputs", ())
    if weighted_outputs:
        total_weight = sum(
            _positive_int(row.get("weight", 0), 0)
            for row in weighted_outputs
            if isinstance(row, Mapping)
        ) + _positive_int(spec.get("non_bone_output_weight", 0), 0)
        roll = max(0.0, min(float(0.0 if r_output is None else r_output), 0.999999999))
        slot = int(roll * total_weight) if total_weight else 0
        cursor = 0
        outputs = {}
        for row in weighted_outputs:
            if not isinstance(row, Mapping):
                continue
            cursor += _positive_int(row.get("weight", 0), 0)
            if slot < cursor:
                item_name = row.get("item")
                if isinstance(item_name, str) and item_name:
                    outputs[item_name] = _positive_int(row.get("quantity", 1), 1)
                break
    elif not outputs:
        outputs = {activity_key: 1}
    for output_item, output_qty in outputs.items():
        new_inv[output_item] = new_inv.get(output_item, 0) + (output_qty * batch_count)
    return new_inv, 0, True, batch_count


def can_craft_item_pure(crafting_level, inventory, item, crafting_data):
    """Return True if level and materials allow crafting the item."""
    spec = crafting_data.get(item)
    if not spec:
        return False
    if crafting_level < spec.get("level", 1):
        return False
    return has_crafting_materials_pure(item, inventory, crafting_data)


def crafting_target_locked_reasons_pure(player_data, target, crafting_data, quest_unlock_rules=()):
    spec = crafting_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    required_level = _positive_int(spec.get("level", 1), 1)
    if not skilling_target_level_available_pure(
        player_data, "crafting", str(target), required_level
    ):
        reasons.append(f"level {required_level}")
    for skill_id, level in spec.get("skill_requirements", {}).items():
        if _positive_int(player_data.get(f"{skill_id}_level", 1), 1) < level:
            reasons.append(f"{skill_id.title()} level {level}")
    belt_recipe = {target: recipe_without_belt_tools(player_data, spec)}
    if not has_crafting_materials_pure(target, player_data.get("inventory", {}) or {}, belt_recipe):
        reasons.append("materials")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "crafting",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def fletching_material_requirements_pure(target, inventory, fletching_data):
    """Resolve a Fletching target's exact material consumption from inventory."""
    spec = fletching_data.get(target)
    if not spec:
        return None
    requirements = dict(spec.get("requirements", {}))
    for material, alternatives in spec.get("material_options", {}).items():
        amount = requirements.get(material)
        if amount is None:
            continue
        selected = next(
            (option for option in alternatives if inventory.get(option, 0) >= amount),
            None,
        )
        if selected is None:
            return None
        del requirements[material]
        requirements[selected] = amount
    for material, amount in requirements.items():
        if inventory.get(material, 0) < amount:
            return None
    return requirements


def has_fletching_materials_pure(target, inventory, fletching_data):
    """Return True when inventory satisfies a Fletching target's material needs."""
    spec = fletching_data.get(target)
    if not spec or fletching_material_requirements_pure(target, inventory, fletching_data) is None:
        return False
    for item_name, amount in spec.get("required_items", {}).items():
        if inventory.get(item_name, 0) < amount:
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


def fletching_target_locked_reasons_pure(player_data, target, fletching_data, target_unlock_rules=()):
    spec = fletching_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    required_level = _positive_int(spec.get("level", 1), 1)
    if not skilling_target_level_available_pure(
        player_data, "fletching", str(target), required_level
    ):
        reasons.append(f"Fletching level {required_level}")
    belt_recipe = {target: recipe_without_belt_tools(player_data, spec)}
    if not has_fletching_materials_pure(target, player_data.get("inventory", {}) or {}, belt_recipe):
        reasons.append("materials")
    reasons.extend(
        target_unlock_locked_reasons_pure(
            player_data,
            "fletching",
            target,
            target_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def apply_fletching_pure(target, inventory, fletching_data):
    """Consume logs and produce the selected Fletching output.

    Fletching is intentionally modeled as a processing skill like Crafting:
    the caller handles level checks so UI/runtime code can report a precise
    locked reason, while this pure function owns inventory mutation safety.
    """
    spec = fletching_data.get(target)
    if not spec or not has_fletching_materials_pure(target, inventory, fletching_data):
        return inventory, 0, False

    requirements = fletching_material_requirements_pure(target, inventory, fletching_data)
    if requirements is None:
        return inventory, 0, False

    new_inv = dict(inventory)
    for material, amount in requirements.items():
        new_inv[material] = new_inv.get(material, 0) - amount

    output_item = spec.get("output_item", target)
    output_qty = spec.get("output_qty", 1)
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True


def has_herblore_materials_pure(target, inventory, herblore_data):
    """Return True when inventory satisfies a Herblore target's material needs."""
    spec = herblore_data.get(target)
    if not spec:
        return False
    for material, amount in spec.get("requirements", {}).items():
        if inventory.get(material, 0) < amount:
            return False
    return True


def can_herblore_target_pure(herblore_level, inventory, target, herblore_data):
    """Return True if level and materials allow the Herblore target."""
    spec = herblore_data.get(target)
    if not spec:
        return False
    if herblore_level < spec.get("level", 1):
        return False
    return has_herblore_materials_pure(target, inventory, herblore_data)


def herblore_target_locked_reasons_pure(player_data, target, herblore_data, target_unlock_rules=()):
    spec = herblore_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    herblore_level = _positive_int(player_data.get("herblore_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if herblore_level < required_level:
        reasons.append(f"Herblore level {required_level}")
    if not has_herblore_materials_pure(target, player_data.get("inventory", {}) or {}, herblore_data):
        reasons.append("materials")
    reasons.extend(
        target_unlock_locked_reasons_pure(
            player_data,
            "herblore",
            target,
            target_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def apply_herblore_action_pure(target, inventory, herblore_data):
    """Consume herblore inputs and produce the selected output.

    The three pipeline stages (clean → unfinished → finished) share this one
    processing path; each stage's XP is baked into the target's ``exp`` field
    from HerbData.kt / PotionData.kt (herb XP for clean, zero for unfinished,
    recipe XP for finished), so no stage-specific branching is needed here.
    """
    spec = herblore_data.get(target)
    if not spec or not has_herblore_materials_pure(target, inventory, herblore_data):
        return inventory, 0, False

    new_inv = dict(inventory)
    for material, amount in spec.get("requirements", {}).items():
        new_inv[material] = new_inv.get(material, 0) - amount

    output_item = spec.get("output_item", target)
    output_qty = spec.get("output_qty", 1)
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    for byproduct, amount in (spec.get("byproducts") or {}).items():
        new_inv[byproduct] = new_inv.get(byproduct, 0) + _positive_int(amount)
    return new_inv, spec.get("exp", 0), True


def has_cooking_materials_pure(target, inventory, cooking_data):
    """Return True when inventory has the raw/prepared item for one Cooking action."""
    spec = cooking_data.get(target)
    if not spec:
        return False
    requirements = spec.get("requirements", {})
    return all(inventory.get(material, 0) >= amount for material, amount in requirements.items())


def can_cook_target_pure(cooking_level, inventory, target, cooking_data):
    """Return True when level and materials permit one Cooking action."""
    spec = cooking_data.get(target)
    if not spec:
        return False
    if not spec.get("source_no_level_requirement") and int(cooking_level or 1) < _positive_int(spec.get("level", 1), 1):
        return False
    return has_cooking_materials_pure(target, inventory, cooking_data)


def cooking_target_locked_reasons_pure(player_data, target, cooking_data, quest_unlock_rules=()):
    spec = cooking_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    cooking_level = _positive_int(player_data.get("cooking_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if not spec.get("source_no_level_requirement") and cooking_level < required_level:
        reasons.append(f"Cooking level {required_level}")
    if not has_cooking_materials_pure(target, player_data.get("inventory", {}) or {}, cooking_data):
        reasons.append("materials")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "cooking",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def cooking_source_roll_chance_pure(
    cooking_level, target_spec, *, has_cooking_gauntlets=False
):
    """Return the target's declared source or registered reconstruction roll.

    Ordinary food uses the exact 2011Scape ``CookingAction.kt`` interpolation;
    exceptional targets carry their own explicitly sourced or placeholder
    formula in data.
    """
    source_formula = target_spec.get("source_success_formula")
    if isinstance(source_formula, Mapping):
        if "minimum" in source_formula and "level_divisor" in source_formula:
            return min(
                1.0,
                max(
                    float(source_formula["minimum"]),
                    float(cooking_level) / float(source_formula["level_divisor"]),
                ),
            )
        base = float(source_formula["base"])
        level_multiplier = float(source_formula["level_multiplier"])
        level_range = float(source_formula["level_range"])
        cap = float(source_formula["cap"])
        divisor = float(source_formula["divisor"])
        return min(base + level_multiplier * (float(cooking_level) - 1) / level_range, cap) / divisor
    if target_spec.get("source_always_succeeds"):
        return 1.0
    no_burn_level = _positive_int(
        target_spec.get("cooking_gauntlet_no_burn_level", 0), 0
    )
    if has_cooking_gauntlets and no_burn_level and cooking_level >= no_burn_level:
        return 1.0
    interpolated = _scape2011_interpolate_255(
        target_spec.get("low_chance", 1),
        target_spec.get("high_chance", 255),
        _positive_int(cooking_level, 1),
    )
    return max(0.0, min(interpolated / 255.0, 1.0))


def calculate_cooking_success_probability_pure(
    cooking_level,
    target_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
    *,
    has_cooking_gauntlets=False,
):
    """Translate source Cooking odds into one review-scale success probability."""
    source_chance = cooking_source_roll_chance_pure(
        cooking_level,
        target_spec,
        has_cooking_gauntlets=has_cooking_gauntlets,
    )
    if (
        target_spec.get("source_success_formula")
        or target_spec.get("source_always_succeeds")
        or (has_cooking_gauntlets and source_chance >= 1.0)
    ):
        return source_chance
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def cheese_wheel_slice_probability_pure(cooking_level):
    """Return the calibrated per-trial chance for one of 30 bonus slices.

    The period record fixes a five-slice minimum, observes an 8.87 mean at
    level 57, and reports roughly 695 slices per 27 wheels at level 99. The
    original formula is source-blocked, so the smallest bounded abstraction is
    a 30-trial binomial whose probability interpolates those two observations.
    """
    level = max(1, min(_positive_int(cooking_level, 1), 99))
    level_57_probability = (8.87 - 5.0) / 30.0
    level_99_probability = ((695.0 / 27.0) - 5.0) / 30.0
    probability = level_57_probability + (
        (level - 57) * (level_99_probability - level_57_probability) / 42.0
    )
    return max(0.0, min(probability, 1.0))


def cheese_wheel_slice_yield_pure(cooking_level, roll):
    """Resolve the period-shaped five-to-thirty-five cheese yield in one roll."""
    probability = cheese_wheel_slice_probability_pure(cooking_level)
    value = max(0.0, min(float(roll), 1.0))
    cumulative = 0.0
    for bonus_slices in range(31):
        cumulative += (
            comb(30, bonus_slices)
            * (probability ** bonus_slices)
            * ((1.0 - probability) ** (30 - bonus_slices))
        )
        if value < cumulative or bonus_slices == 30:
            return 5 + bonus_slices
    return 35


def apply_cooking_action_pure(
    target,
    inventory,
    cooking_data,
    cooking_level,
    roll,
    byproduct_roll=None,
    *,
    use_source_probability=False,
    has_cooking_gauntlets=False,
):
    """Apply one Cooking action.

    Returns (inventory, exp, processed, output_item, burned). A failed burn still
    counts as processed because the raw input was consumed and a burnt item was
    produced; it simply awards zero XP.
    """
    spec = cooking_data.get(target)
    if not spec or not has_cooking_materials_pure(target, inventory, cooking_data):
        return inventory, 0, False, None, False

    new_inv = dict(inventory)
    for material, amount in spec.get("requirements", {}).items():
        new_inv[material] = new_inv.get(material, 0) - amount

    success_probability = (
        cooking_source_roll_chance_pure(
            cooking_level,
            spec,
            has_cooking_gauntlets=has_cooking_gauntlets,
        )
        if use_source_probability
        else calculate_cooking_success_probability_pure(
            cooking_level,
            spec,
            has_cooking_gauntlets=has_cooking_gauntlets,
        )
    )
    source_runtime_action = bool(spec.get("source_success_formula") or spec.get("source_always_succeeds"))
    succeeded = float(roll) <= success_probability if source_runtime_action else float(roll) < success_probability
    if succeeded:
        output_item = spec.get("output_item", target)
        output_qty = _positive_int(spec.get("output_qty", 1), 1)
        if spec.get("output_quantity_model") == "cheese_wheel_slices":
            output_qty = cheese_wheel_slice_yield_pure(cooking_level, roll)
        new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
        for byproduct, amount in (spec.get("byproducts") or {}).items():
            new_inv[byproduct] = new_inv.get(byproduct, 0) + _positive_int(amount)
        byproduct_item = spec.get("byproduct_item")
        if isinstance(byproduct_item, str) and byproduct_item and byproduct_roll is not None:
            if float(byproduct_roll) <= float(spec.get("byproduct_chance", 0.0)):
                new_inv[byproduct_item] = new_inv.get(byproduct_item, 0) + 1
        base_exp = spec.get("exp", 0)
        if float(spec.get("xp_per_output", 0.0) or 0.0) > 0.0:
            base_exp = output_qty * float(spec["xp_per_output"])
        return new_inv, base_exp, True, output_item, False

    alternate_output = spec.get("alternate_output_item")
    if isinstance(alternate_output, str) and alternate_output:
        output_qty = _positive_int(spec.get("alternate_output_qty", 1), 1)
        new_inv[alternate_output] = new_inv.get(alternate_output, 0) + output_qty
        for byproduct, amount in (spec.get("byproducts") or {}).items():
            new_inv[byproduct] = new_inv.get(byproduct, 0) + _positive_int(amount)
        alternate_exp = float(spec.get("alternate_output_exp", -1.0))
        if alternate_exp < 0.0:
            alternate_exp = float(spec.get("exp", 0))
        return (
            new_inv,
            alternate_exp,
            True,
            alternate_output,
            bool(spec.get("alternate_is_failure")),
        )

    burnt_item = spec.get("burnt_item")
    if isinstance(burnt_item, str) and burnt_item:
        new_inv[burnt_item] = new_inv.get(burnt_item, 0) + 1
    else:
        burnt_item = None
    return new_inv, 0, True, burnt_item, True


def firemaking_source_roll_chance_pure(firemaking_level, target_spec):
    """Exact 2011Scape Firemaking roll (FiremakingAction.kt): the shared
    3-arg interpolate helper (floors + 1) with success on
    interp > nextInt(255)."""
    interpolated = _scape2011_interpolate_255(
        target_spec.get("low_chance", 65),
        target_spec.get("high_chance", 513),
        _positive_int(firemaking_level, 1),
    )
    return max(0.0, min(interpolated / 255.0, 1.0))


def calculate_firemaking_success_probability_pure(
    firemaking_level,
    target_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    overlevel_window=40,
    cap=REVIEW_SUCCESS_CAP,
    tier_minimum=0.30,
    tier_scale=0.65,
):
    """Translate source lighting odds into one review-scale success probability.

    The source chance mostly depends on Firemaking level, not the log tier. To
    make higher-level logs feel slower near unlock in AnkiScape, this adapter
    also applies a target-level curve: old logs become comfortable as the player
    overlevels them, while newly unlocked logs start stickier.
    """
    source_chance = firemaking_source_roll_chance_pure(firemaking_level, target_spec)
    source_adapter = normalize_review_success_probability_pure(source_chance, minimum, scale, cap)
    required_level = _positive_int(target_spec.get("level", 1), 1)
    overlevel = max(0.0, float(firemaking_level) - float(required_level))
    window = max(float(overlevel_window), 1.0)
    tier_progress = max(0.0, min((overlevel + 1.0) / window, 1.0))
    tier_adapter = normalize_review_success_probability_pure(tier_progress, tier_minimum, tier_scale, cap)
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


def firemaking_target_locked_reasons_pure(player_data, target, firemaking_data, quest_unlock_rules=()):
    spec = firemaking_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    firemaking_level = _positive_int(player_data.get("firemaking_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if firemaking_level < required_level:
        reasons.append(f"Firemaking level {required_level}")
    if not has_firemaking_materials_pure(target, player_data.get("inventory", {}) or {}, firemaking_data):
        reasons.append("materials")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "firemaking",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def can_burn_firemaking_target_with_unlocks_pure(player_data, target, firemaking_data, quest_unlock_rules=()):
    return not firemaking_target_locked_reasons_pure(player_data, target, firemaking_data, quest_unlock_rules)


def can_burn_any_firemaking_target_pure(inventory, firemaking_level, firemaking_data):
    """Return True if any Firemaking target can be attempted right now."""
    return any(
        can_burn_firemaking_target_pure(firemaking_level, inventory, target, firemaking_data)
        for target in firemaking_data
    )


def apply_firemaking_action_pure(
    target,
    inventory,
    firemaking_data,
    firemaking_level,
    r_action,
    success_level=None,
    *,
    use_source_probability=False,
):
    """Apply one Firemaking attempt.

    Returns (inventory, base_exp, success, output_item). Failed attempts consume
    no log and award no XP/items, matching AnkiScape's gathering-style pacing.
    """
    spec = firemaking_data.get(target)
    if not spec or not has_firemaking_materials_pure(target, inventory, firemaking_data):
        return inventory, 0, False, None
    effective_level = firemaking_level if success_level is None else success_level
    success_probability = (
        firemaking_source_roll_chance_pure(effective_level, spec)
        if use_source_probability
        else calculate_firemaking_success_probability_pure(effective_level, spec)
    )
    if r_action >= success_probability:
        return inventory, 0, False, None

    new_inv = dict(inventory)
    for material, amount in spec.get("requirements", {}).items():
        new_inv[material] = new_inv.get(material, 0) - amount
    output_item = spec.get("output_item", "Ashes")
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True, output_item
