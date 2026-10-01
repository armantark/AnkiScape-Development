"""logic_pure_smithing.py - split out of logic_pure.py; see that module's header."""

from __future__ import annotations

from typing import Mapping

from ..core.tool_belt import recipe_without_belt_tools
from ..data.dungeoneering_data import COAL_BAG_CAPACITY

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
    quest_unlock_locked_reasons_pure,
)

from .logic_pure_state import (
    _copy_player_data_with_nested,
    _positive_int,
    _requirements_from_spec,
)


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
    requirements = dict(_requirements_from_spec(spec))
    requirements.update(spec.get("required_items", {}))
    for material, amount in requirements.items():
        if inventory.get(material, 0) < amount:
            return False
    return True


def coal_bag_coal_pure(player_data):
    """Return the usable Coal held by the owned Dungeoneering Coal bag."""
    state = player_data.get("dungeoneering")
    if not isinstance(state, Mapping) or not state.get("coal_bag_owned"):
        return 0
    return min(
        COAL_BAG_CAPACITY,
        _non_negative_int(state.get("coal_bag_coal")),
    )


def smithing_inventory_with_coal_bag_pure(player_data):
    """Expose stored bag Coal to the existing Smithing material reducer."""
    inventory = dict(player_data.get("inventory", {}) or {})
    bag_coal = coal_bag_coal_pure(player_data)
    if bag_coal:
        inventory["Coal"] = _non_negative_int(inventory.get("Coal")) + bag_coal
    return inventory


def reconcile_smithing_coal_bag_pure(
    player_data,
    inventory_before,
    effective_inventory_after,
):
    """Reconcile one real Smithing result, consuming Coal from the bag first."""
    bag_coal = coal_bag_coal_pure(player_data)
    loose_coal = _non_negative_int((inventory_before or {}).get("Coal"))
    coal_after = _non_negative_int((effective_inventory_after or {}).get("Coal"))
    coal_consumed = max(0, loose_coal + bag_coal - coal_after)
    bag_consumed = min(bag_coal, coal_consumed)
    loose_consumed = max(0, coal_consumed - bag_consumed)

    inventory = dict(effective_inventory_after or {})
    loose_remaining = max(0, loose_coal - loose_consumed)
    if loose_remaining:
        inventory["Coal"] = loose_remaining
    else:
        inventory.pop("Coal", None)

    data = dict(player_data)
    state = dict(data.get("dungeoneering") or {})
    if bag_coal:
        state["coal_bag_coal"] = bag_coal - bag_consumed
        data["dungeoneering"] = state
    data["inventory"] = inventory
    return data, bag_consumed


def can_smith_item_pure(smithing_level, inventory, target, smithing_data):
    """Return True if level and materials allow one Smithing recipe action."""
    spec = smithing_data.get(target)
    if not spec:
        return False
    if smithing_level < spec.get("level", 1):
        return False
    return has_smithing_materials_pure(target, inventory, smithing_data)


def smithing_target_locked_reasons_pure(player_data, target, smithing_data, quest_unlock_rules=()):
    spec = smithing_data.get(target)
    if not spec:
        return ("unknown target",)
    reasons = []
    smithing_level = _positive_int(player_data.get("smithing_level", 1), 1)
    required_level = _positive_int(spec.get("level", 1), 1)
    if smithing_level < required_level:
        reasons.append(f"level {required_level}")
    if not has_smithing_materials_pure(
        target,
        smithing_inventory_with_coal_bag_pure(player_data),
        {target: recipe_without_belt_tools(player_data, spec)},
    ):
        reasons.append("materials")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "smithing",
            target,
            quest_unlock_rules,
        )
    )
    return tuple(dict.fromkeys(reasons))


def can_smith_any_pure(inventory, smithing_level, smithing_data):
    """Return True if any smelt or forge recipe can run right now."""
    return any(
        can_smith_item_pure(smithing_level, inventory, target, smithing_data)
        for target in smithing_data
    )


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


RING_OF_FORGING_ITEM = "Ring of forging"


RING_OF_FORGING_MAX_CHARGES = 140


def _equipment_has_ring_of_forging_pure(player_data):
    return (player_data.get("equipment", {}) or {}).get("ring") == RING_OF_FORGING_ITEM


def ring_of_forging_charges_pure(player_data):
    if not _equipment_has_ring_of_forging_pure(player_data):
        return 0
    charges = (player_data.get("item_charges", {}) or {}).get(RING_OF_FORGING_ITEM)
    if charges is None:
        return RING_OF_FORGING_MAX_CHARGES
    return max(0, _positive_int(charges, 0))


def has_ring_of_forging_pure(player_data):
    return ring_of_forging_charges_pure(player_data) > 0


def consume_ring_of_forging_charge_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    if not _equipment_has_ring_of_forging_pure(data):
        return data
    remaining = ring_of_forging_charges_pure(data) - 1
    item_charges = data.setdefault("item_charges", {})
    if remaining > 0:
        item_charges[RING_OF_FORGING_ITEM] = remaining
    else:
        item_charges.pop(RING_OF_FORGING_ITEM, None)
        data.setdefault("equipment", {}).pop("ring", None)
    return data


def calculate_iron_smelting_success_probability_pure(smithing_level, has_ring_of_forging=False):
    if has_ring_of_forging:
        return 1.0
    level = max(15, min(_positive_int(smithing_level, 15), 45))
    # SmeltingAction.rollIronBar: level.coerceAtMost(45).interpolate(50, 80,
    # 15, 45, 100) -> success iff nextInt(100) <= interp, i.e. probability
    # (interp + 1)/100 — the source curve is 51%..81%, not 50%..80%.
    interp = 50 + ((80 - 50) * (level - 15) // (45 - 15))
    return min(1.0, (interp + 1) / 100.0)


def smithing_success_probability_pure(target, spec, smithing_level, has_ring_of_forging=False):
    if target == "smelt_iron_bar" and (spec or {}).get("station") == "furnace":
        return calculate_iron_smelting_success_probability_pure(smithing_level, has_ring_of_forging)
    return 1.0


def apply_smithing_action_pure(
    target,
    inventory,
    smithing_data,
    smithing_level,
    r_action=0.0,
    has_ring_of_forging=False,
):
    """Apply one source-shaped Smithing action.

    Returns (inventory, base_exp, processed, output_item, failed). Iron smelting
    failure consumes ore and processes the action, but gives no bar or XP.
    """
    spec = smithing_data.get(target)
    if not spec or not has_smithing_materials_pure(target, inventory, smithing_data):
        return inventory, 0, False, None, False

    new_inv = dict(inventory)
    for material, amount in _requirements_from_spec(spec).items():
        new_inv[material] = new_inv.get(material, 0) - amount

    success_probability = smithing_success_probability_pure(
        target,
        spec,
        smithing_level,
        has_ring_of_forging=has_ring_of_forging,
    )
    try:
        roll = float(r_action)
    except (TypeError, ValueError):
        roll = 1.0
    if success_probability < 1.0 and roll >= success_probability:
        return new_inv, 0, True, None, True

    output_item = spec.get("output_item", target)
    output_qty = _positive_int(spec.get("output_qty", 1))
    new_inv[output_item] = new_inv.get(output_item, 0) + output_qty
    return new_inv, spec.get("exp", 0), True, output_item, False
