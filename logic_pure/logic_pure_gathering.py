"""logic_pure_gathering.py - split out of logic_pure.py; see that module's header."""

from __future__ import annotations

from math import comb, floor, sqrt

from typing import Iterable, Mapping, Optional

from ..data.mining_data import MINING_REVIEW_DAY_CARDS, RED_SANDSTONE_DAILY_CAP

from .logic_pure_quest import (  # noqa: F401  (re-export)
    QUEST_COMBAT_CONFIG_VERSION,
    QUEST_COMBAT_DEFAULT_BURST_TICKS,
    QUEST_COMBAT_RESOLVER_ENABLED_KEY,
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
    default_quest_combat_config_pure,
    normalize_xp_rewards_pure,
    primary_xp_reward_amount_pure,
    quest_availability_state_pure,
    quest_combat_encounter_has_stats_pure,
    quest_combat_encounter_ready_pure,
    quest_combat_resolver_enabled_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_current_stage_blockers_pure,
    quest_current_stage_choices_pure,
    quest_current_stage_pure,
    quest_current_stage_resolvable_combat_blockers_pure,
    quest_journal_rows_pure,
    quest_locked_reasons_pure,
    quest_unlock_locked_reasons_pure,
    sanitize_quest_combat_config_pure,
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

from .logic_pure_equipment import (  # noqa: F401  (re-export)
    _combat_level_key,
    _combat_skill_label,
    _equipment_bonus_value,
    _equipment_bonuses,
    _equipment_skill_requirements,
    _equipment_value,
    _mage_arena_god_for_item,
    _normalized_equipment_slot,
    _toolbelt_ids,
    best_mining_pickaxe_pure,
    best_woodcutting_axe_pure,
    can_equip_item_pure,
    equip_item_pure,
    equipment_bonus_state_pure,
    equipment_stat_totals_pure,
    unequip_item_pure,
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

from .logic_pure_quest import (
    normalize_xp_rewards_pure,
    primary_xp_reward_amount_pure,
    quest_unlock_locked_reasons_pure,
    target_unlock_locked_reasons_pure,
)

from .logic_pure_progression import (
    REVIEW_SUCCESS_CAP,
    REVIEW_SUCCESS_MINIMUM,
    REVIEW_SUCCESS_SCALE,
    normalize_review_success_probability_pure,
    pick_gem,
    pick_weighted_item_pure,
    red_sandstone_daily_remaining_pure,
)

from .logic_pure_equipment import (
    best_mining_pickaxe_pure,
    best_woodcutting_axe_pure,
)

from .logic_pure_state import (
    _non_negative_float,
    _non_negative_int,
    _positive_int,
)


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


def _scape2011_interpolate_255(low, high, level):
    # MiscExt.kt 3-arg interpolate: floor(low*(99-level)/98 +
    # floor(high*(level-1)/98) + 1). Success in Mining/Woodcutting is
    # `interp > nextInt(255)`, i.e. probability interp/255.
    level = max(1, min(int(level), 99))
    return floor((int(low) * (99 - level)) / 98.0 + floor((int(high) * (level - 1)) / 98.0) + 1)


def mining_source_roll_chance_pure(mining_level, target_spec, pickaxe_spec):
    """Exact 2011Scape mining roll (Mining.kt): the interpolated chance is
    ratio-free in source (the pickaxe sets roll cadence via
    ticksBetweenRolls); AnkiScape folds that cadence into the per-action
    chance as a declared adaptation of the one-roll-per-review model."""
    interpolated = float(_scape2011_interpolate_255(
        target_spec.get("low_chance", 0), target_spec.get("high_chance", 0), _positive_int(mining_level, 1)
    ))
    ratio = float(pickaxe_spec.get("ratio", 1.0))
    # Mining.kt gives PickaxeType.DRAGON an accumulator: +0.2 per swing, and
    # each fifth swing rolls again at 1.12x base. AnkiScape folds that bonus
    # into every roll as a declared simplification of the same source
    # constant, keyed on the stable pickaxe id (gilded variants share it).
    if _non_negative_int(pickaxe_spec.get("item_id"), 0) == 15261:  # Dragon pickaxe
        ratio *= 1.12
    return max(0.0, min((interpolated * ratio) / 255.0, 1.0))


def calculate_mining_success_probability_pure(
    mining_level,
    target_spec,
    pickaxe_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Translate source mining odds into one review-scale success probability."""
    source_chance = mining_source_roll_chance_pure(mining_level, target_spec, pickaxe_spec)
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def mining_target_locked_reasons_pure(player_data, target_id, ore_data, pickaxe_data, quest_unlock_rules=()):
    spec = ore_data.get(target_id)
    if not spec:
        return ("unknown target",)
    reasons = []
    mining_level = _positive_int(player_data.get("mining_level", 1), 1)
    if mining_level < _positive_int(spec.get("level", 1), 1):
        reasons.append(f"Mining level {spec.get('level', 1)}")
    if best_mining_pickaxe_pure(
        mining_level,
        player_data.get("inventory", {}) or {},
        player_data.get("toolbelt", {}) or {},
        pickaxe_data,
    ) is None:
        reasons.append("no usable pickaxe")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "mining",
            target_id,
            quest_unlock_rules,
        )
    )
    if (
        target_id == "red_sandstone"
        and red_sandstone_daily_remaining_pure(player_data) <= 0
    ):
        reasons.append(
            f"{RED_SANDSTONE_DAILY_CAP} Red sandstone already mined this review day"
        )
    return tuple(dict.fromkeys(reasons))


def can_mine_target_pure(mining_level, target_id, ore_data, inventory, toolbelt, pickaxe_data):
    spec = ore_data.get(target_id)
    if not spec:
        return False
    if mining_level < spec.get("level", 1):
        return False
    return best_mining_pickaxe_pure(mining_level, inventory, toolbelt, pickaxe_data) is not None


def woodcutting_source_roll_chance_pure(woodcutting_level, target_spec, axe_spec):
    """Exact 2011Scape chop roll (Woodcutting.kt): the axe ratio scales the
    chance inputs (truncated to int) before the shared interpolate helper,
    and success is `interp > nextInt(255)`."""
    ratio = float(axe_spec.get("ratio", 1.0))
    low = int(float(target_spec.get("low_chance", 0)) * ratio)
    high = int(float(target_spec.get("high_chance", 0)) * ratio)
    interpolated = _scape2011_interpolate_255(low, high, _positive_int(woodcutting_level, 1))
    return max(0.0, min(interpolated / 255.0, 1.0))


def calculate_woodcutting_success_probability_pure(
    woodcutting_level,
    target_spec,
    axe_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Translate source chop odds into a review-scale success probability.

    2011Scape rolls every few game ticks; AnkiScape rolls once per eligible card.
    The square-root adapter preserves ordering and tool upgrades while avoiding
    extremely dry high-tier trees at normal review cadence.
    """
    source_chance = woodcutting_source_roll_chance_pure(woodcutting_level, target_spec, axe_spec)
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def can_chop_woodcutting_target_pure(woodcutting_level, target_id, tree_data, inventory, toolbelt, axe_data):
    spec = tree_data.get(target_id)
    if not spec:
        return False
    if woodcutting_level < spec.get("level", 1):
        return False
    return best_woodcutting_axe_pure(woodcutting_level, inventory, toolbelt, axe_data) is not None


def woodcutting_target_locked_reasons_pure(
    player_data,
    target_id,
    tree_data,
    axe_data,
    target_unlock_rules=(),
):
    spec = tree_data.get(target_id)
    if not isinstance(spec, Mapping):
        return ("Unknown Woodcutting target",)

    reasons = []
    level = _positive_int(player_data.get("woodcutting_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if level < required_level:
        reasons.append(f"level {required_level}")
    reasons.extend(
        target_unlock_locked_reasons_pure(
            player_data,
            "woodcutting",
            target_id,
            target_unlock_rules,
        )
    )

    if spec.get("action_type") == "processing":
        inventory = player_data.get("inventory", {}) or {}
        requirements = spec.get("requirements", {})
        if isinstance(inventory, Mapping) and isinstance(requirements, Mapping):
            for item_name, amount in requirements.items():
                need = max(0, _positive_int(amount, 0))
                if _positive_int(inventory.get(item_name, 0), 0) < need:
                    reasons.append(f"missing {item_name} x{need}")
    elif best_woodcutting_axe_pure(
        level,
        player_data.get("inventory", {}),
        player_data.get("toolbelt", {}),
        axe_data,
    ) is None:
        reasons.append("no usable hatchet")
    return tuple(dict.fromkeys(reasons))


def apply_woodcutting_processing_action_pure(
    target_id,
    inventory,
    tree_data,
    woodcutting_level,
):
    spec = tree_data.get(target_id)
    if (
        not isinstance(spec, Mapping)
        or spec.get("action_type") != "processing"
        or woodcutting_level < spec.get("level", 1)
    ):
        return inventory, 0.0, False, None

    requirements = spec.get("requirements", {})
    if not isinstance(requirements, Mapping):
        return inventory, 0.0, False, None
    for item_name, amount in requirements.items():
        if inventory.get(item_name, 0) < amount:
            return inventory, 0.0, False, None

    output_item = spec.get("output_item")
    if not isinstance(output_item, str) or not output_item:
        return inventory, 0.0, False, None

    updated = dict(inventory)
    for item_name, amount in requirements.items():
        updated[item_name] = max(0, updated.get(item_name, 0) - amount)
    output_quantity = max(1, _positive_int(spec.get("output_quantity", 1), 1))
    updated[output_item] = updated.get(output_item, 0) + output_quantity
    return updated, float(spec.get("exp", 0.0) or 0.0), True, output_item


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
    r_inferno_adze=None,
    success_level=None,
):
    spec = tree_data.get(target_id)
    if not spec or not axe_spec:
        return inventory, 0, False, None, None
    success_probability = calculate_woodcutting_success_probability_pure(
        woodcutting_level if success_level is None else success_level,
        spec,
        axe_spec,
    )
    if r_action >= success_probability:
        return inventory, 0, False, None, None

    new_inv = dict(inventory)
    output_item = spec.get("output_item")
    if (
        output_item
        and axe_spec.get("incinerates_logs", False)
        and r_inferno_adze is not None
        and r_inferno_adze < axe_spec.get("incinerate_chance", 0.0)
    ):
        output_item = None
    elif output_item:
        output_quantity = max(1, _positive_int(spec.get("output_quantity", 1), 1))
        new_inv[output_item] = new_inv.get(output_item, 0) + output_quantity

    nest_item = None
    if r_nest_drop is not None and r_nest_type is not None and nest_drop_table and r_nest_drop < nest_drop_chance:
        nest_item = pick_weighted_item_pure(nest_drop_table, r_nest_type)
        if nest_item:
            new_inv[nest_item] = new_inv.get(nest_item, 0) + 1

    return new_inv, spec.get("exp", 0), True, output_item, nest_item


def fishing_source_roll_chance_pure(fishing_level, fish_spec):
    """Exact 2011Scape fish roll (Fish.kt: level.interpolate(min, max, 1, 99,
    255)): integer-division linear interpolation, success iff
    nextInt(255) <= interp, i.e. probability (interp + 1)/255."""
    low = int(_non_negative_float(fish_spec.get("min_chance", 0), 0.0))
    high = int(_non_negative_float(fish_spec.get("max_chance", 0), 0.0))
    level = max(1, min(_positive_int(fishing_level, 1), 99))
    interp = low + ((high - low) * (level - 1)) // 98
    return max(0.0, min((interp + 1) / 255.0, 1.0))


def calculate_fishing_success_probability_pure(
    fishing_level,
    fish_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Translate source Fishing odds into one review-scale success probability."""
    source_chance = fishing_source_roll_chance_pure(fishing_level, fish_spec)
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def eligible_fishing_fish_pure(method_spec, fishing_level, strength_level=1, agility_level=1):
    """Fish rows whose Fishing and hidden side-level gates are currently met."""
    eligible = []
    for fish in method_spec.get("fish", ()):
        if fishing_level < _positive_int(fish.get("level", 1), 1):
            continue
        strength_req = fish.get("strength_level")
        if strength_req is not None and strength_level < _positive_int(strength_req, 1):
            continue
        agility_req = fish.get("agility_level")
        if agility_req is not None and agility_level < _positive_int(agility_req, 1):
            continue
        eligible.append(fish)
    return tuple(eligible)


def has_fishing_bait_pure(inventory, method_spec):
    """Return True if the method has no consumable bait or any allowed bait is held."""
    bait_options = tuple(method_spec.get("bait_options") or ())
    if not bait_options:
        return True
    return any(inventory.get(bait, 0) > 0 for bait in bait_options)


def can_fish_method_pure(fishing_level, inventory, target_id, fishing_data, strength_level=1, agility_level=1):
    """Return True if a Fishing target can make at least one source roll now."""
    method_spec = fishing_data.get(target_id)
    if not method_spec:
        return False
    if fishing_level < method_spec.get("level", 1):
        return False
    if not has_fishing_bait_pure(inventory, method_spec):
        return False
    return bool(eligible_fishing_fish_pure(method_spec, fishing_level, strength_level, agility_level))


def fishing_method_locked_reasons_pure(player_data, target_id, fishing_data, quest_unlock_rules=()):
    method_spec = fishing_data.get(target_id)
    if not method_spec:
        return ("unknown target",)
    reasons = []
    fishing_level = _positive_int(player_data.get("fishing_level", 1), 1)
    strength_level = _positive_int(player_data.get("strength_level", 1), 1)
    agility_level = _positive_int(player_data.get("agility_level", 1), 1)
    inventory = player_data.get("inventory", {}) or {}
    if fishing_level < _positive_int(method_spec.get("level", 1), 1):
        reasons.append(f"Fishing level {method_spec.get('level', 1)}")
    if not has_fishing_bait_pure(inventory, method_spec):
        reasons.append("materials")
    if (
        fishing_level >= _positive_int(method_spec.get("level", 1), 1)
        and not eligible_fishing_fish_pure(method_spec, fishing_level, strength_level, agility_level)
    ):
        reasons.append("side levels")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "fishing",
            target_id,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def can_fish_any_pure(inventory, fishing_level, fishing_data, strength_level=1, agility_level=1):
    """Return True if any Fishing method can be attempted now."""
    return any(
        can_fish_method_pure(fishing_level, inventory, target, fishing_data, strength_level, agility_level)
        for target in fishing_data
    )


def apply_fishing_action_pure(
    target_id,
    inventory,
    fishing_data,
    fishing_level,
    strength_level=1,
    agility_level=1,
    rolls=(),
    success_level=None,
):
    """Apply one ordered source-shaped Fishing attempt.

    Returns (inventory, base_fishing_exp, success, output_item, xp_rewards).
    Bait is consumed only after a catch, mirroring the 2011Scape runtime.
    """
    method_spec = fishing_data.get(target_id)
    if not method_spec:
        return inventory, 0, False, None, tuple()
    if not can_fish_method_pure(fishing_level, inventory, target_id, fishing_data, strength_level, agility_level):
        return inventory, 0, False, None, tuple()

    roll_iter = iter(rolls or ())
    for fish in eligible_fishing_fish_pure(method_spec, fishing_level, strength_level, agility_level):
        try:
            roll = float(next(roll_iter))
        except (StopIteration, TypeError, ValueError):
            roll = 1.0
        success_probability = calculate_fishing_success_probability_pure(
            fishing_level if success_level is None else success_level,
            fish,
        )
        if roll >= success_probability:
            continue

        new_inv = dict(inventory)
        for bait in method_spec.get("bait_options") or ():
            if new_inv.get(bait, 0) > 0:
                new_inv[bait] = new_inv.get(bait, 0) - 1
                break
        output_item = fish.get("output_item")
        if output_item:
            new_inv[output_item] = new_inv.get(output_item, 0) + 1

        xp_rewards = normalize_xp_rewards_pure(fish, "fishing", fish.get("exp", 0))
        return new_inv, primary_xp_reward_amount_pure(xp_rewards, "fishing"), True, output_item, xp_rewards

    return inventory, 0, False, None, tuple()


_AGILITY_DOUBLE_CATCH_LEVELS = {
    "Raw tuna": 35,
    "Raw swordfish": 50,
    "Raw shark": 76,
}


def fishing_agility_double_catch_chance_pure(output_item, agility_level):
    """Return the bounded pre-EOC Agility double-catch yield chance.

    The eligible fish and unlock levels are period-sourced. The surviving
    update text only calls the probability small, so 10% is the named
    ``ankiscape_fishing_double_catch_fallback`` until a quantitative period
    row replaces it. The extra fish never carries extra Fishing XP.
    """
    required = _AGILITY_DOUBLE_CATCH_LEVELS.get(str(output_item))
    if required is None or _positive_int(agility_level, 1) < required:
        return 0.0
    return 0.10


def _hunter_outputs_from_spec(spec):
    raw_outputs = spec.get("outputs", {})
    if isinstance(raw_outputs, Mapping):
        return {
            str(item): _positive_int(amount, 1)
            for item, amount in raw_outputs.items()
            if isinstance(item, str) and item
        }
    output_item = spec.get("output_item")
    if isinstance(output_item, str) and output_item:
        return {output_item: _positive_int(spec.get("output_qty", 1), 1)}
    return {}


def hunter_source_roll_chance_pure(hunter_level, target_spec):
    """Exact Darkan Hunter catch odds (Utils.skillSuccess, verified by
    bytecode disassembly of core-2.0.5.jar): chance = int(rate1 +
    (rate99 - rate1) * level / 99), clamped to 0..256, success iff
    nextInt(255) <= chance, i.e. probability (chance + 1)/255."""
    if bool(target_spec.get("deterministic", False)):
        return 1.0
    low = int(_non_negative_float(target_spec.get("rate1", 128), 128.0))
    high = int(_non_negative_float(target_spec.get("rate99", 256), 256.0))
    level = max(1, _positive_int(hunter_level, 1))
    chance = int(low + (high - low) * (level / 99.0))
    chance = max(0, min(chance, 256))
    return max(0.0, min((chance + 1) / 255.0, 1.0))


def calculate_hunter_success_probability_pure(
    hunter_level,
    target_spec,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Translate source Hunter odds into one review-scale success probability."""
    if bool(target_spec.get("deterministic", False)):
        return 1.0
    source_chance = hunter_source_roll_chance_pure(hunter_level, target_spec)
    return normalize_review_success_probability_pure(source_chance, minimum, scale, cap)


def has_hunter_materials_pure(target, inventory, hunter_data):
    """Return True when inventory satisfies a Hunter target's consumable needs."""
    spec = hunter_data.get(target)
    if not spec:
        return False
    requirements = spec.get("requirements", {})
    if not isinstance(requirements, Mapping):
        return True
    for material, amount in requirements.items():
        if inventory.get(material, 0) < _positive_int(amount, 1):
            return False
    return True


def missing_hunter_tools_pure(target, inventory, hunter_data):
    """Return reusable Hunter tools missing from inventory/bank state."""
    spec = hunter_data.get(target)
    if not spec:
        return ("unknown target",)
    tools = spec.get("tools", {})
    if not isinstance(tools, Mapping):
        return tuple()
    missing = []
    for tool, amount in tools.items():
        required = _positive_int(amount, 1)
        if inventory.get(tool, 0) < required:
            missing.append(str(tool))
    return tuple(missing)


def has_hunter_tools_pure(target, inventory, hunter_data):
    return not missing_hunter_tools_pure(target, inventory, hunter_data)


def hunter_target_locked_reasons_pure(player_data, target, hunter_data, quest_unlock_rules=()):
    spec = hunter_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    hunter_level = _positive_int(player_data.get("hunter_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if hunter_level < required_level:
        reasons.append(f"Hunter level {required_level}")
    skill_requirements = spec.get("skill_requirements", {})
    if isinstance(skill_requirements, Mapping):
        for skill_id, required in skill_requirements.items():
            required_level = _positive_int(required, 1)
            current_level = _positive_int(player_data.get(f"{skill_id}_level", 1), 1)
            if current_level < required_level:
                reasons.append(f"{str(skill_id).replace('_', ' ').title()} level {required_level}")
    if not has_hunter_materials_pure(target, player_data.get("inventory", {}) or {}, hunter_data):
        reasons.append("materials")
    reasons.extend(missing_hunter_tools_pure(target, player_data.get("inventory", {}) or {}, hunter_data))
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "hunter",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def can_hunt_target_pure(hunter_level, inventory, target, hunter_data):
    spec = hunter_data.get(target)
    if not spec:
        return False
    if hunter_level < _positive_int(spec.get("level", 1), 1):
        return False
    return has_hunter_materials_pure(target, inventory, hunter_data) and has_hunter_tools_pure(target, inventory, hunter_data)


def apply_hunter_action_pure(
    target,
    inventory,
    hunter_data,
    hunter_level,
    r_action,
    success_level=None,
    r_secondary_rolls=(),
):
    """Apply one Hunter attempt and return inventory, XP, success, output, rewards."""
    spec = hunter_data.get(target)
    if not spec or not can_hunt_target_pure(hunter_level, inventory, target, hunter_data):
        return inventory, 0, False, None, tuple()
    success_probability = calculate_hunter_success_probability_pure(
        hunter_level if success_level is None else success_level,
        spec,
    )
    if float(r_action) >= success_probability:
        return inventory, 0, False, None, tuple()

    new_inv = dict(inventory)
    requirements = spec.get("requirements", {})
    if isinstance(requirements, Mapping):
        for material, amount in requirements.items():
            new_inv[material] = new_inv.get(material, 0) - _positive_int(amount, 1)
    outputs = _hunter_outputs_from_spec(spec)
    for item_name, amount in outputs.items():
        new_inv[item_name] = new_inv.get(item_name, 0) + amount

    for table, (r_chance, r_pick) in zip(
        spec.get("secondary_drop_tables") or (),
        r_secondary_rolls or (),
    ):
        secondary_outputs = table.get("outputs") or ()
        if not secondary_outputs or float(r_chance) >= float(
            table.get("chance", 0.0) or 0.0
        ):
            continue
        item_name = pick_weighted_item_pure(secondary_outputs, r_pick)
        output = next(
            (row for row in secondary_outputs if row.get("item") == item_name),
            None,
        )
        if output:
            new_inv[item_name] = new_inv.get(item_name, 0) + _positive_int(
                output.get("amount", 1),
                1,
            )

    primary_output = spec.get("primary_output") or spec.get("output_item")
    xp_rewards = normalize_xp_rewards_pure(spec, "hunter", spec.get("exp", 0))
    return new_inv, primary_xp_reward_amount_pure(xp_rewards, "hunter"), True, primary_output, xp_rewards


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
    success_level=None,
):
    """Apply one source-shaped Anki Mining attempt.

    Returns (inventory, base_exp, success, output_item, gem_item, extra_output).
    Random gem drops are inventory-only side drops; they do not add Mining XP.
    """
    spec = ore_data.get(target_id)
    if not spec or not pickaxe_spec:
        return inventory, 0, False, None, None, None
    success_probability = calculate_mining_success_probability_pure(
        mining_level if success_level is None else success_level,
        spec,
        pickaxe_spec,
    )
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
        minimum_quantity, maximum_quantity = spec.get(
            "output_quantity_range", (1, 1)
        )
        minimum_quantity = max(1, int(minimum_quantity))
        maximum_quantity = max(minimum_quantity, int(maximum_quantity))
        quantity_roll = min(
            max(float(r_output if r_output is not None else 0.0), 0.0),
            0.999999999999,
        )
        output_quantity = minimum_quantity + int(
            quantity_roll * (maximum_quantity - minimum_quantity + 1)
        )
        new_inv[output_item] = new_inv.get(output_item, 0) + output_quantity

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
