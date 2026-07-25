"""logic_pure_thieving.py - split out of logic_pure.py; see that module's header."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

try:
    from .inventory_pure import CARRIED_CAPACITY, apply_carried_layout_pure, carried_slots_used, clamp_carried_view_to_bank
except ImportError:
    from inventory_pure import CARRIED_CAPACITY, apply_carried_layout_pure, carried_slots_used, clamp_carried_view_to_bank

try:
    from .combat_data import (
        COMBAT_ATTACK_STYLE_DATA,
        COMBAT_ANTIPOISON_POTION_DATA,
        COMBAT_BURST_TICKS,
        COMBAT_ENEMY_DATA,
        COMBAT_FOOD_DATA,
        CONSUMABLE_DATA,
        KEBAB_DRAINABLE_SKILLS,
        COMBAT_MAGIC_STAFF_DATA,
        COMBAT_MAGIC_SPELL_DATA,
        COMBAT_RANGED_AMMO_DATA,
        COMBAT_RANGED_WEAPON_DATA,
        DEFAULT_COMBAT_ATTACK_STYLE,
        DEFAULT_COMBAT_SPELL,
        DEFAULT_COMBAT_TARGET,
        MAGIC_FORMULA_SOURCE_PATH,
        MAGIC_STRATEGY_SOURCE_PATH,
        MELEE_FORMULA_SOURCE_PATH,
        MELEE_STRATEGY_SOURCE_PATH,
        POTION_TYPE_SOURCE_PATH,
        RANGED_FORMULA_SOURCE_PATH,
        RANGED_STRATEGY_SOURCE_PATH,
        WEAPON_TYPE_ATTACK_STYLES,
        WEAPON_TYPE_UNARMED_STYLES,
    )
except ImportError:
    from combat_data import (  # type: ignore
        COMBAT_ATTACK_STYLE_DATA,
        COMBAT_ANTIPOISON_POTION_DATA,
        COMBAT_BURST_TICKS,
        COMBAT_ENEMY_DATA,
        COMBAT_FOOD_DATA,
        CONSUMABLE_DATA,
        KEBAB_DRAINABLE_SKILLS,
        COMBAT_MAGIC_STAFF_DATA,
        COMBAT_MAGIC_SPELL_DATA,
        COMBAT_RANGED_AMMO_DATA,
        COMBAT_RANGED_WEAPON_DATA,
        DEFAULT_COMBAT_ATTACK_STYLE,
        DEFAULT_COMBAT_SPELL,
        DEFAULT_COMBAT_TARGET,
        MAGIC_FORMULA_SOURCE_PATH,
        MAGIC_STRATEGY_SOURCE_PATH,
        MELEE_FORMULA_SOURCE_PATH,
        MELEE_STRATEGY_SOURCE_PATH,
        POTION_TYPE_SOURCE_PATH,
        RANGED_FORMULA_SOURCE_PATH,
        RANGED_STRATEGY_SOURCE_PATH,
        WEAPON_TYPE_ATTACK_STYLES,
        WEAPON_TYPE_UNARMED_STYLES,
    )

try:
    from .logic_pure_combat_model import (  # noqa: F401  (re-export)
        COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM,
        COMBAT_ENEMY_ATTACK_STYLES,
        COMBAT_FOOD_LOADOUT_CAPACITY,
        COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
        COMBAT_POISON_NPC_ATTACK_CHANCE,
        COMBAT_POISON_SOURCE_PATH,
        COMBAT_POISON_TICK_DELAY,
        COMBAT_POISON_TIMER_SOURCE_PATH,
        COMBAT_PRESET_FIELDS,
        COMBAT_REST_FULL_HEAL_REVIEWS,
        COMBAT_SPECIAL_ATTACK_MAX_ENERGY,
        COMBAT_SPECIAL_ATTACK_REGEN_PER_50_TICKS,
        COMBAT_STAT_DRAIN_RECOVERY_TICKS,
        NATURAL_COMBAT_RECOVERY_LIFEPOINTS,
        SAFE_COMBAT_RECOVERY_LIFEPOINTS,
        SAFE_COMBAT_RECOVERY_TICKS,
        _COMBAT_AFFECTABLE_SKILLS,
        _COMBAT_ANTIPOISON_SLOT_CAP,
        _COMBAT_DEFAULT_PACK_MODE,
        _COMBAT_DRAGONFIRE_POTION_SLOT_CAP,
        _COMBAT_DRAINABLE_SKILLS,
        _COMBAT_FOOD_CAP_BY_MODE,
        _COMBAT_MAGIC_EQUIPMENT_TYPES,
        _COMBAT_MELEE_STYLE_IDS,
        _COMBAT_MELEE_STYLE_TYPES,
        _COMBAT_POTION_FLASK_CAP_BY_MODE,
        _COMBAT_RANGED_STYLE_IDS,
        _COMBAT_VALID_PACK_MODES,
        _COMBAT_XP_MODE_TO_STYLE_ID,
        _DEFAULT_COMBAT_AUTO_EAT_FOOD,
        _carried_inventory_grave_counts,
        _combat_accuracy,
        _combat_apply_follower_death,
        _combat_apply_magic_xp,
        _combat_apply_pvm_death,
        _combat_apply_triple_charm_reward,
        _combat_apply_unprotected_stat_drains,
        _combat_apply_wilderness_ambush,
        _combat_apply_wilderness_death,
        _combat_apply_xp,
        _combat_attack_bonus_from_totals,
        _combat_banked_hazard_count,
        _combat_base_skill_level,
        _combat_cap_damage_for_finisher,
        _combat_coerce_pack_mode,
        _combat_consume_auto_food,
        _combat_consume_hazard_dose,
        _combat_consume_loaded_finisher,
        _combat_death_office_items,
        _combat_defence_bonus_from_totals,
        _combat_drop_requirements_met,
        _combat_effective_player_attack_level,
        _combat_effective_player_defence_level,
        _combat_effective_player_magic_level,
        _combat_effective_player_ranged_level,
        _combat_effective_player_strength_level,
        _combat_effective_rune_cost_pure,
        _combat_effective_skill_level,
        _combat_enemy_attack_class,
        _combat_enemy_attack_style,
        _combat_enemy_bonuses,
        _combat_enemy_max_hit_old_hp,
        _combat_enemy_protection_class,
        _combat_environmental_hazard_spec,
        _combat_equipped_item_count,
        _combat_equipped_weapon_name,
        _combat_finisher_charge_items,
        _combat_finisher_spec,
        _combat_food_slot_cap,
        _combat_hazard_dose_items,
        _combat_loaded_finisher_charge_state,
        _combat_loaded_finisher_count,
        _combat_loaded_hazard_count,
        _combat_magic_locked_reasons,
        _combat_magic_max_hit_old_hp,
        _combat_magic_missing_runes,
        _combat_magic_rune_count,
        _combat_melee_max_hit_old_hp,
        _combat_npc_xp_multiplier,
        _combat_pending_supplemental_magic_costs_pure,
        _combat_potion_flask_cap,
        _combat_preset_snapshot,
        _combat_protective_equipment_state,
        _combat_ranged_ammo_count,
        _combat_ranged_locked_reasons,
        _combat_ranged_max_hit_old_hp,
        _combat_ranged_weapon_spec,
        _combat_reclaim_items_to_player,
        _combat_required_rune_cost_pure,
        _combat_resolve_melee_slot,
        _combat_restricted_weapon_locked_reasons,
        _combat_roll_drop_table,
        _combat_roll_drops,
        _combat_selected_magic_spell,
        _combat_selected_ranged_ammo,
        _combat_slot_drop_quantity,
        _combat_spellbook_swap_applies_pure,
        _combat_start_equipment_state,
        _combat_supplemental_rune_cost_pure,
        _combat_unprotected_damage_lifepoints,
        _combat_weakening_equipment_state,
        _combat_weapon_equipment_type,
        _combat_weapon_is_magic,
        _combat_weapon_is_ranged,
        _combat_weapon_type_id,
        _sanitize_combat_current_levels,
        _sanitize_combat_recovery_progress,
        _sanitize_combat_status_effects,
        _set_combat_death_office_items,
        apply_combat_finisher_pure,
        apply_combat_preset_pure,
        apply_combat_stat_delta_pure,
        apply_combat_target_overrides_pure,
        charged_god_spell_max_hit_bonus_pure,
        combat_attack_style_for_equipment_pure,
        combat_enemy_current_lifepoints_pure,
        combat_enemy_drop_item_names_pure,
        combat_finisher_state_pure,
        combat_magic_preset_locked_reasons_pure,
        combat_max_lifepoints_pure,
        combat_melee_attack_type_pure,
        combat_staff_covered_runes_pure,
        combat_target_locked_reasons_pure,
        combat_weapon_attack_style_slots_pure,
        combat_wilderness_equipment_risk_pure,
        default_combat_state_pure,
        derive_casual_combat_magic_pure,
        sanitize_combat_state_pure,
        save_combat_preset_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_combat_model import (  # type: ignore  # noqa: F401
        COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM,
        COMBAT_ENEMY_ATTACK_STYLES,
        COMBAT_FOOD_LOADOUT_CAPACITY,
        COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
        COMBAT_POISON_NPC_ATTACK_CHANCE,
        COMBAT_POISON_SOURCE_PATH,
        COMBAT_POISON_TICK_DELAY,
        COMBAT_POISON_TIMER_SOURCE_PATH,
        COMBAT_PRESET_FIELDS,
        COMBAT_REST_FULL_HEAL_REVIEWS,
        COMBAT_SPECIAL_ATTACK_MAX_ENERGY,
        COMBAT_SPECIAL_ATTACK_REGEN_PER_50_TICKS,
        COMBAT_STAT_DRAIN_RECOVERY_TICKS,
        NATURAL_COMBAT_RECOVERY_LIFEPOINTS,
        SAFE_COMBAT_RECOVERY_LIFEPOINTS,
        SAFE_COMBAT_RECOVERY_TICKS,
        _COMBAT_AFFECTABLE_SKILLS,
        _COMBAT_ANTIPOISON_SLOT_CAP,
        _COMBAT_DEFAULT_PACK_MODE,
        _COMBAT_DRAGONFIRE_POTION_SLOT_CAP,
        _COMBAT_DRAINABLE_SKILLS,
        _COMBAT_FOOD_CAP_BY_MODE,
        _COMBAT_MAGIC_EQUIPMENT_TYPES,
        _COMBAT_MELEE_STYLE_IDS,
        _COMBAT_MELEE_STYLE_TYPES,
        _COMBAT_POTION_FLASK_CAP_BY_MODE,
        _COMBAT_RANGED_STYLE_IDS,
        _COMBAT_VALID_PACK_MODES,
        _COMBAT_XP_MODE_TO_STYLE_ID,
        _DEFAULT_COMBAT_AUTO_EAT_FOOD,
        _carried_inventory_grave_counts,
        _combat_accuracy,
        _combat_apply_follower_death,
        _combat_apply_magic_xp,
        _combat_apply_pvm_death,
        _combat_apply_triple_charm_reward,
        _combat_apply_unprotected_stat_drains,
        _combat_apply_wilderness_ambush,
        _combat_apply_wilderness_death,
        _combat_apply_xp,
        _combat_attack_bonus_from_totals,
        _combat_banked_hazard_count,
        _combat_base_skill_level,
        _combat_cap_damage_for_finisher,
        _combat_coerce_pack_mode,
        _combat_consume_auto_food,
        _combat_consume_hazard_dose,
        _combat_consume_loaded_finisher,
        _combat_death_office_items,
        _combat_defence_bonus_from_totals,
        _combat_drop_requirements_met,
        _combat_effective_player_attack_level,
        _combat_effective_player_defence_level,
        _combat_effective_player_magic_level,
        _combat_effective_player_ranged_level,
        _combat_effective_player_strength_level,
        _combat_effective_rune_cost_pure,
        _combat_effective_skill_level,
        _combat_enemy_attack_class,
        _combat_enemy_attack_style,
        _combat_enemy_bonuses,
        _combat_enemy_max_hit_old_hp,
        _combat_enemy_protection_class,
        _combat_environmental_hazard_spec,
        _combat_equipped_item_count,
        _combat_equipped_weapon_name,
        _combat_finisher_charge_items,
        _combat_finisher_spec,
        _combat_food_slot_cap,
        _combat_hazard_dose_items,
        _combat_loaded_finisher_charge_state,
        _combat_loaded_finisher_count,
        _combat_loaded_hazard_count,
        _combat_magic_locked_reasons,
        _combat_magic_max_hit_old_hp,
        _combat_magic_missing_runes,
        _combat_magic_rune_count,
        _combat_melee_max_hit_old_hp,
        _combat_npc_xp_multiplier,
        _combat_pending_supplemental_magic_costs_pure,
        _combat_potion_flask_cap,
        _combat_preset_snapshot,
        _combat_protective_equipment_state,
        _combat_ranged_ammo_count,
        _combat_ranged_locked_reasons,
        _combat_ranged_max_hit_old_hp,
        _combat_ranged_weapon_spec,
        _combat_reclaim_items_to_player,
        _combat_required_rune_cost_pure,
        _combat_resolve_melee_slot,
        _combat_restricted_weapon_locked_reasons,
        _combat_roll_drop_table,
        _combat_roll_drops,
        _combat_selected_magic_spell,
        _combat_selected_ranged_ammo,
        _combat_slot_drop_quantity,
        _combat_spellbook_swap_applies_pure,
        _combat_start_equipment_state,
        _combat_supplemental_rune_cost_pure,
        _combat_unprotected_damage_lifepoints,
        _combat_weakening_equipment_state,
        _combat_weapon_equipment_type,
        _combat_weapon_is_magic,
        _combat_weapon_is_ranged,
        _combat_weapon_type_id,
        _sanitize_combat_current_levels,
        _sanitize_combat_recovery_progress,
        _sanitize_combat_status_effects,
        _set_combat_death_office_items,
        apply_combat_finisher_pure,
        apply_combat_preset_pure,
        apply_combat_stat_delta_pure,
        apply_combat_target_overrides_pure,
        charged_god_spell_max_hit_bonus_pure,
        combat_attack_style_for_equipment_pure,
        combat_enemy_current_lifepoints_pure,
        combat_enemy_drop_item_names_pure,
        combat_finisher_state_pure,
        combat_magic_preset_locked_reasons_pure,
        combat_max_lifepoints_pure,
        combat_melee_attack_type_pure,
        combat_staff_covered_runes_pure,
        combat_target_locked_reasons_pure,
        combat_weapon_attack_style_slots_pure,
        combat_wilderness_equipment_risk_pure,
        default_combat_state_pure,
        derive_casual_combat_magic_pure,
        sanitize_combat_state_pure,
        save_combat_preset_pure,
    )

try:
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
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_state import (  # type: ignore  # noqa: F401
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

try:
    from .logic_pure_combat_model import (
        COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
        _combat_apply_pvm_death,
        _combat_consume_auto_food,
        combat_max_lifepoints_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_combat_model import (  # type: ignore
        COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
        _combat_apply_pvm_death,
        _combat_consume_auto_food,
        combat_max_lifepoints_pure,
    )

try:
    from .logic_pure_state import (
        _copy_player_data_with_nested,
        _non_negative_int,
        _positive_int,
        quest_completed_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_state import (  # type: ignore
        _copy_player_data_with_nested,
        _non_negative_int,
        _positive_int,
        quest_completed_pure,
    )


def thieving_roll_threshold_pure(level, minimum, maximum):
    """2011Scape's integer interpolation before the inclusive 0..254 roll."""
    level = max(1, min(_positive_int(level, 1), 99))
    minimum = _non_negative_int(minimum, 0)
    maximum = _non_negative_int(maximum, minimum)
    return minimum + ((maximum - minimum) * (level - 1) // 98)


def thieving_roll_succeeds_pure(level, minimum, maximum, roll):
    threshold = thieving_roll_threshold_pure(level, minimum, maximum)
    return _non_negative_int(roll, 255) <= threshold


def thieving_wall_safe_success_count_pure(level, minimum, maximum):
    """2011Scape wall-safe successes among the 255 possible integer rolls.

    Wall safes use the standalone three-argument ``interpolate`` helper and a
    strict ``> RANDOM.nextInt(255)`` comparison, unlike pickpockets' inclusive
    ``level.interpolate(..., cap=255)`` roll.
    """
    level = max(1, min(_positive_int(level, 1), 99))
    minimum = _non_negative_int(minimum, 0)
    maximum = _non_negative_int(maximum, minimum)
    return min(
        255,
        (minimum * (99 - level) // 98)
        + (maximum * (level - 1) // 98)
        + 1,
    )


def thieving_wall_safe_roll_succeeds_pure(level, minimum, maximum, roll):
    success_count = thieving_wall_safe_success_count_pure(level, minimum, maximum)
    return _non_negative_int(roll, 255) < success_count


def _consume_carried_auto_food_pure(
    data,
    target_id,
    current_lifepoints,
    max_lifepoints,
):
    threshold_percent = _positive_int(data.get("combat_auto_eat_threshold_percent", 40), 40)
    threshold = max(1, int(max_lifepoints * threshold_percent / 100.0))
    if current_lifepoints > threshold or current_lifepoints >= max_lifepoints:
        return current_lifepoints, None
    carried = data.get("carried_inventory")
    raw_view = carried.get(target_id) if isinstance(carried, Mapping) else None
    view = clamp_carried_view_to_bank(raw_view, data.get("inventory"))
    inventory = dict(data.get("inventory", {}) or {})
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        food = COMBAT_FOOD_DATA.get(item_name)
        available = min(
            _non_negative_int(view.get(item_name, 0), 0),
            _non_negative_int(inventory.get(item_name, 0), 0),
        )
        if not food or available <= 0:
            continue
        view[item_name] = available - 1
        inventory[item_name] = _non_negative_int(inventory.get(item_name, 0), 0) - 1
        if view[item_name] <= 0:
            view.pop(item_name, None)
        carried = dict(carried) if isinstance(carried, Mapping) else {}
        if view:
            carried[target_id] = view
        else:
            carried.pop(target_id, None)
        data["carried_inventory"] = carried
        data["inventory"] = inventory
        healed_by = _positive_int(food.get("heal_lifepoints", 0), 0)
        return min(max_lifepoints, current_lifepoints + healed_by), {
            "item": item_name,
            "healed_by": healed_by,
        }
    return current_lifepoints, None


def apply_thieving_damage_pure(
    player_data,
    damage,
    *,
    source="thieving_failure",
    carried_target_id=None,
    safe_death=False,
):
    """Apply a Thieving failure through Combat's food and death substrate."""
    data = _copy_player_data_with_nested(player_data)
    max_lifepoints = combat_max_lifepoints_pure(data)
    current_lifepoints = min(
        max_lifepoints + COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
        _non_negative_int(data.get("combat_lifepoints", max_lifepoints), max_lifepoints),
    )
    applied_damage = min(current_lifepoints, _non_negative_int(damage, 0))
    current_lifepoints -= applied_damage
    food_event = None
    died = current_lifepoints <= 0 and applied_damage > 0
    if died:
        if safe_death:
            data["combat_encounter"] = {}
            data["combat_status_effects"] = {}
            current_lifepoints = max_lifepoints
        else:
            current_lifepoints = _combat_apply_pvm_death(
                data,
                max_lifepoints,
                source,
                carried_target_id=carried_target_id,
            )
    elif applied_damage > 0:
        if isinstance(carried_target_id, str):
            current_lifepoints, food_event = _consume_carried_auto_food_pure(
                data,
                carried_target_id,
                current_lifepoints,
                max_lifepoints,
            )
        else:
            current_lifepoints, food_event = _combat_consume_auto_food(
                data, current_lifepoints, max_lifepoints, lambda: 0.0
            )
    data["combat_lifepoints"] = current_lifepoints
    return data, {
        "damage": applied_damage,
        "died": died,
        "safe_death": bool(died and safe_death),
        "food_used": food_event,
    }


def thieving_success_probability_pure(level, spec):
    if spec.get("kind") == "wall_safe":
        return thieving_wall_safe_success_count_pure(
            level, spec.get("min_chance", 0), spec.get("max_chance", 0)
        ) / 255.0
    threshold = thieving_roll_threshold_pure(
        level, spec.get("min_chance", 0), spec.get("max_chance", 0)
    )
    return min(threshold + 1, 255) / 255.0


def thieving_blackjack_threshold_pure(level, minimum=185, maximum=255):
    """Darkan core skillSuccess threshold used provisionally for knockout only."""
    level = max(1, min(_positive_int(level, 1), 99))
    minimum = _non_negative_int(minimum, 0)
    maximum = _non_negative_int(maximum, minimum)
    return min(254, minimum + ((maximum - minimum) * level // 99))


def thieving_multi_pick_count_pure(thieving_level, agility_level, target_level, roll):
    thieving_overshoot = _positive_int(thieving_level, 1) - _positive_int(target_level, 1)
    agility_overshoot = _positive_int(agility_level, 1) - _positive_int(target_level, 1)
    if thieving_overshoot < 10 or agility_overshoot < 0 or _non_negative_int(roll, 0) != 1:
        return 1
    if thieving_overshoot >= 30 and agility_overshoot >= 20:
        return 4
    if thieving_overshoot >= 20 and agility_overshoot >= 10:
        return 3
    return 2


def thieving_loot_roll_pure(spec, slot_roll, quantity_roll=0.0):
    """Return one exact weighted-table drop plus every guaranteed drop."""
    outputs = {
        str(item): _positive_int(quantity, 1)
        for item, quantity in (spec.get("guaranteed") or ())
    }
    total = _positive_int(spec.get("loot_total", 0), 1)
    loot = tuple(spec.get("loot") or ())
    if not loot or not spec.get("loot_total"):
        return outputs
    cursor = _non_negative_int(slot_roll, 0) % total
    for item, minimum, maximum, slots in loot:
        slots = _positive_int(slots, 1)
        if cursor < slots:
            minimum = _positive_int(minimum, 1)
            maximum = max(minimum, _positive_int(maximum, minimum))
            span = maximum - minimum + 1
            q_roll = max(0.0, min(float(quantity_roll), 0.999999999999))
            quantity = minimum + int(q_roll * span)
            outputs[str(item)] = outputs.get(str(item), 0) + quantity
            break
        cursor -= slots
    return outputs


def thieving_stall_cadence_profile_pure(target_id, spec):
    try:
        from .cadence_kernel import CAP_ONE_ACTION, rate_limited_profile_pure
    except ImportError:
        from cadence_kernel import CAP_ONE_ACTION, rate_limited_profile_pure
    ticks = _positive_int(spec.get("respawn_ticks", 1), 1)
    overflow = CAP_ONE_ACTION if 6000 > 1000 * ticks else None
    return rate_limited_profile_pure(
        f"thieving:{target_id}", 6000, ticks, overflow_policy=overflow
    )


def thieving_target_locked_reasons_pure(player_data, target_id, thieving_data):
    spec = thieving_data.get(target_id)
    if not spec:
        return ("unknown target",)
    reasons = []
    required_level = _positive_int(spec.get("level", 1), 1)
    if _positive_int(player_data.get("thieving_level", 1), 1) < required_level:
        reasons.append(f"Thieving level {required_level}")
    if spec.get("source_blocked"):
        reasons.append(str(spec.get("source_blocked_reason", "source values are not closed")))
    quest_gate = spec.get("quest_gate")
    if quest_gate and not quest_completed_pure(player_data, str(quest_gate)):
        reasons.append(str(spec.get("quest_gate_label", str(quest_gate).replace("_", " ").title())))
    required_items = tuple(spec.get("required_items_any") or ())
    inventory = player_data.get("inventory", {}) or {}
    equipment = player_data.get("equipment", {}) or {}
    equipped_items = set(equipment.values()) if isinstance(equipment, Mapping) else set()
    if required_items and not any(
        _non_negative_int(inventory.get(item, 0), 0) > 0 or item in equipped_items
        for item in required_items
    ):
        reasons.append("usable blackjack")
    encounter = player_data.get("combat_encounter") or {}
    if isinstance(encounter, Mapping) and encounter:
        reasons.append("active combat encounter")
    return tuple(dict.fromkeys(reasons))
