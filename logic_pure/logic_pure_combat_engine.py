"""logic_pure_combat_engine.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from ..logic.equipment_instance_logic import (
    advance_equipped_condition_pure,
    discharge_equipped_on_unsafe_death_pure,
    sanitize_equipment_instance_state_pure,
    sync_equipment_instances_pure,
)
from ..data.equipment_condition_data import EQUIPMENT_CONDITION_DATA

from ..logic.warriors_guild_logic import (
    warriors_guild_cyclops_damage_multiplier_pure,
    warriors_guild_cyclops_locked_reasons_pure,
)

from ..data.prayer_data import (
    COMBAT_PRAYERS_BY_ID,
    AUTO_PRAYER_TICKS_PER_ITEM,
    PRAYER_MATERIALS,
    PRAYER_UPTIME_POLICIES,
    SAP_SOURCE,
    LEECH_SOURCE,
    resolve_prayer_selection_pure,
)

from ..data.magic_data import CASUAL_MAGIC_DIAL, DREAM_COST, SPELLBOOK_SWAP_COST, VENGEANCE_COST

from ..data.combat_data import (
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

from .logic_pure_combat_supplies import (  # noqa: F401  (re-export)
    _combat_advance_dragonfire_effects,
    _combat_advance_status_effects,
    _combat_apply_poison_effect_to_data,
    _combat_auto_drink_potions,
    _combat_auto_eat_food_available,
    _combat_bank_has_runes,
    _combat_bank_run_needed,
    _combat_bank_run_result,
    _combat_banked_antipoison_count,
    _combat_banked_auto_food_count,
    _combat_banked_dragonfire_potion_count,
    _combat_banked_finisher_count,
    _combat_banked_ranged_ammo_count,
    _combat_carried_slot_counts,
    _combat_consume_antipoison_if_needed,
    _combat_consume_dragonfire_if_needed,
    _combat_consume_loaded_rune_cost,
    _combat_consume_magic_runes,
    _combat_consume_ranged_ammo,
    _combat_custom_layout_view,
    _combat_deposit_loot,
    _combat_loaded_antipoison_count,
    _combat_loaded_dragonfire_potion_count,
    _combat_loaded_food_count,
    _combat_loaded_ranged_ammo,
    _combat_locks_can_bank_run,
    _combat_missing_loaded_runes,
    _combat_pick_potion_for_skill,
    _combat_progress_or_start_bank_run,
    _combat_ranged_strength_bonus,
    _combat_recover_current_levels,
    _combat_refill_antipoison_loadout,
    _combat_refill_context_supplies,
    _combat_refill_dragonfire_loadout,
    _combat_refill_finisher_loadout,
    _combat_refill_food_loadout,
    _combat_refill_hazard_loadout,
    _combat_refill_magic_rune_loadout,
    _combat_refill_ranged_ammo_loadout,
    _combat_refill_stat_potions,
    _combat_regenerate_special_attack_energy,
    _combat_relevant_potion_items,
    _combat_relevant_potion_skills,
    _combat_should_auto_flee,
    _combat_supply_slots_used,
    _combat_trim_food_to_capacity,
    _combat_try_pack_yak_winter_storage,
    _combat_void_shifter_escape_ready,
    _potion_boost_amount,
    apply_combat_poison_effect_pure,
    apply_combat_stat_boost_to_pure,
    combat_dragonfire_protection_pure,
    combat_poison_damage_for_ticks_pure,
    combat_poison_immunity_ticks_pure,
    combat_poison_ticks_for_initial_damage_pure,
    combat_status_summary_pure,
    prayer_potion_restore_amount_pure,
)

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
    _combat_select_enemy_attack_pure,
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
    _record_combat_observed_drops_pure,
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
    combat_observed_drop_item_names_pure,
    combat_observed_drops_for_target_pure,
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

from .logic_pure_urns import (  # noqa: F401  (re-export)
    active_urn_state_pure,
    carried_target_item_count_pure,
    charge_training_urn_for_action_pure,
    charge_training_urn_pure,
    full_urn_teleport_info_pure,
    intercept_bonecrusher_outputs_pure,
    nonempty_urn_count_pure,
    resolve_prayer_kill_effects_pure,
    teleport_full_urn_pure,
)

from .logic_pure_prayer import (  # noqa: F401  (re-export)
    CASTLE_WARS_HALO_DRAIN_PRAYERS,
    _highest_legal_prayer_candidate_pure,
    active_prayer_selection_pure,
    apply_prayer_action_pure,
    apply_prayer_selection_pure,
    clear_prayer_gilded_stint_pure,
    curse_expected_ramp_pure,
    prayer_drain_and_effective_uptime_pure,
    prayer_drain_for_ticks_pure,
    prayer_effect_state_pure,
    prayer_gilded_search_step_pure,
    prayer_selection_locked_reasons_pure,
    prayer_target_locked_reasons_pure,
    prayer_uptime_fraction_pure,
    sanitize_prayer_selection_pure,
)

from .logic_pure_magic import (  # noqa: F401  (re-export)
    MAGIC_CHARGE_DURATION_TICKS,
    TEMPORARY_EFFECT_TICKS_PER_ACTION,
    _HUMIDIFY_OUTPUTS,
    _LEATHER_OUTPUTS,
    _PIE_OUTPUTS,
    _STRINGABLE_AMULETS,
    _apply_farming_spell_pure,
    _apply_remote_farm_pure,
    _farming_spell_locked_reasons_pure,
    _livid_spell_locked_reasons_pure,
    _magic_dynamic_requirements_pure,
    _magic_quest_gate_complete_pure,
    advance_temporary_effects_pure,
    apply_magic_action_pure,
    effective_magic_rune_cost_pure,
    magic_target_locked_reasons_pure,
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

from .logic_pure_combat_supplies import (
    _combat_advance_dragonfire_effects,
    _combat_advance_status_effects,
    _combat_apply_poison_effect_to_data,
    _combat_auto_drink_potions,
    _combat_consume_antipoison_if_needed,
    _combat_consume_dragonfire_if_needed,
    _combat_consume_loaded_rune_cost,
    _combat_consume_magic_runes,
    _combat_consume_ranged_ammo,
    _combat_custom_layout_view,
    _combat_locks_can_bank_run,
    _combat_progress_or_start_bank_run,
    _combat_ranged_strength_bonus,
    _combat_recover_current_levels,
    _combat_refill_antipoison_loadout,
    _combat_refill_dragonfire_loadout,
    _combat_refill_finisher_loadout,
    _combat_refill_food_loadout,
    _combat_refill_hazard_loadout,
    _combat_refill_magic_rune_loadout,
    _combat_refill_ranged_ammo_loadout,
    _combat_refill_stat_potions,
    _combat_regenerate_special_attack_energy,
    _combat_should_auto_flee,
    _combat_trim_food_to_capacity,
    _combat_void_shifter_escape_ready,
    combat_dragonfire_protection_pure,
    combat_poison_damage_for_ticks_pure,
    combat_poison_immunity_ticks_pure,
    combat_poison_ticks_for_initial_damage_pure,
    combat_status_summary_pure,
)

from .logic_pure_combat_model import (
    COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM,
    COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
    COMBAT_POISON_NPC_ATTACK_CHANCE,
    COMBAT_REST_FULL_HEAL_REVIEWS,
    NATURAL_COMBAT_RECOVERY_LIFEPOINTS,
    SAFE_COMBAT_RECOVERY_LIFEPOINTS,
    SAFE_COMBAT_RECOVERY_TICKS,
    _COMBAT_XP_MODE_TO_STYLE_ID,
    _DEFAULT_COMBAT_AUTO_EAT_FOOD,
    _combat_accuracy,
    _combat_apply_magic_xp,
    _combat_apply_pvm_death,
    _combat_apply_triple_charm_reward,
    _combat_apply_unprotected_stat_drains,
    _combat_apply_wilderness_ambush,
    _combat_apply_xp,
    _combat_attack_bonus_from_totals,
    _combat_banked_hazard_count,
    _combat_base_skill_level,
    _combat_cap_damage_for_finisher,
    _combat_coerce_pack_mode,
    _combat_consume_auto_food,
    _combat_consume_hazard_dose,
    _combat_death_office_items,
    _combat_defence_bonus_from_totals,
    _combat_effective_player_attack_level,
    _combat_effective_player_defence_level,
    _combat_effective_player_magic_level,
    _combat_effective_player_ranged_level,
    _combat_effective_player_strength_level,
    _combat_enemy_attack_class,
    _combat_enemy_attack_style,
    _combat_enemy_bonuses,
    _combat_enemy_max_hit_old_hp,
    _combat_enemy_protection_class,
    _combat_environmental_hazard_spec,
    _combat_finisher_spec,
    _combat_loaded_hazard_count,
    _combat_magic_max_hit_old_hp,
    _combat_melee_max_hit_old_hp,
    _combat_npc_xp_multiplier,
    _combat_pending_supplemental_magic_costs_pure,
    _combat_protective_equipment_state,
    _combat_ranged_max_hit_old_hp,
    _combat_ranged_weapon_spec,
    _combat_reclaim_items_to_player,
    _combat_required_rune_cost_pure,
    _record_combat_observed_drops_pure,
    _combat_resolve_melee_slot,
    _combat_roll_drops,
    _combat_selected_magic_spell,
    _combat_selected_ranged_ammo,
    _combat_start_equipment_state,
    _combat_unprotected_damage_lifepoints,
    _combat_weakening_equipment_state,
    _combat_weapon_is_magic,
    _combat_weapon_is_ranged,
    apply_combat_preset_pure,
    apply_combat_target_overrides_pure,
    combat_attack_style_for_equipment_pure,
    combat_enemy_current_lifepoints_pure,
    combat_finisher_state_pure,
    combat_magic_preset_locked_reasons_pure,
    combat_max_lifepoints_pure,
    combat_melee_attack_type_pure,
    combat_target_locked_reasons_pure,
    combat_weapon_attack_style_slots_pure,
    combat_wilderness_equipment_risk_pure,
    derive_casual_combat_magic_pure,
    sanitize_combat_state_pure,
)

from .logic_pure_urns import (
    resolve_prayer_kill_effects_pure,
)

from .logic_pure_prayer import (
    CASTLE_WARS_HALO_DRAIN_PRAYERS,
    active_prayer_selection_pure,
    curse_expected_ramp_pure,
    prayer_drain_and_effective_uptime_pure,
    prayer_effect_state_pure,
    prayer_uptime_fraction_pure,
)

from .logic_pure_magic import (
    advance_temporary_effects_pure,
    effective_magic_rune_cost_pure,
)

from .logic_pure_equipment import (
    _equipment_bonus_value,
    _equipment_value,
    best_mining_pickaxe_pure,
    best_woodcutting_axe_pure,
    equipment_stat_totals_pure,
)

from .logic_pure_state import (
    COMBAT_GRAVE_RECOVERY_REVIEWS,
    _combat_stored_loadout,
    _copy_player_data_with_nested,
    _non_negative_float,
    _non_negative_int,
    _positive_int,
    _sanitize_combat_supply_loadout,
    _signed_int,
    default_combat_supply_loadout_pure,
)


def _combat_roll_damage_lifepoints(max_hit_old_hp, rng):
    # Darkan CombatFormula.kt rolls Utils.random(minHit=1, maxHit) on a landed
    # hit, and Utils.random(min, max) is min + nextInt(|max - min|): uniform
    # 1..maxHit-1 lifepoints, never 0 and never the displayed max (maxHit 1
    # always deals 1). A 0 can only come from the accuracy roll failing.
    max_damage = int(max(0.0, float(max_hit_old_hp) * 10.0))
    if max_damage <= 0:
        return 0
    spread = max_damage - 1
    if spread <= 0:
        return 1
    try:
        roll = float(rng())
    except (TypeError, ValueError):
        roll = 0.0
    return 1 + int(max(0.0, min(roll, 0.999999999)) * spread)


def combat_target_preview_pure(player_data, target_id, enemy_data=None, equipment_data=None):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    enemy = enemy_data.get(target_id)
    if enemy is None:
        return {"state": "blocked", "risk_band": "Blocked", "reasons": ("unknown enemy",)}
    equipment_data = equipment_data or {}
    reasons = combat_target_locked_reasons_pure(player_data, target_id, enemy_data, equipment_data=equipment_data)
    if reasons:
        return {"state": "blocked", "risk_band": "Blocked", "reasons": reasons}
    player_totals = equipment_stat_totals_pure(player_data.get("equipment", {}) or {}, equipment_data)
    enemy_totals = _combat_enemy_bonuses(enemy)
    style_id = combat_attack_style_for_equipment_pure(player_data, equipment_data)
    style = COMBAT_ATTACK_STYLE_DATA.get(style_id, COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE])
    combat_class = str(style.get("combat_class", "melee"))
    melee_style_type = (
        _combat_resolve_melee_slot(player_data, equipment_data)["style_type"]
        if combat_class == "melee"
        else None
    )
    spell_id, spell_spec = _combat_selected_magic_spell(player_data)
    if combat_class == "ranged":
        weapon_name, _weapon_equipment, weapon_spec = _combat_ranged_weapon_spec(player_data, equipment_data)
        ammo_name = _combat_selected_ranged_ammo(player_data, weapon_spec, target_id)
        player_attack_roll = _combat_effective_player_ranged_level(player_data, style_id) * (
            _combat_attack_bonus_from_totals(player_totals, "ranged") + 64
        )
    elif combat_class == "magic":
        weapon_name = None
        ammo_name = None
        player_attack_roll = _combat_effective_player_magic_level(player_data) * (
            _combat_attack_bonus_from_totals(player_totals, "magic") + 64
        )
    else:
        weapon_name = None
        ammo_name = None
        player_attack_roll = _combat_effective_player_attack_level(player_data, style_id) * (
            _combat_attack_bonus_from_totals(player_totals, style_type=melee_style_type) + 64
        )
    enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * (
        _combat_defence_bonus_from_totals(enemy_totals, combat_class, style_type=melee_style_type) + 64
    )
    accuracy = _combat_accuracy(player_attack_roll, enemy_defence_roll)
    if combat_class == "ranged":
        player_max_hit = _combat_ranged_max_hit_old_hp(
            _combat_effective_player_ranged_level(player_data, style_id),
            _combat_ranged_strength_bonus(player_totals, ammo_name),
        )
    elif combat_class == "magic":
        player_max_hit = _combat_magic_max_hit_old_hp(
            spell_spec,
            player_totals,
            player_data,
            spell_id,
        )
    else:
        player_max_hit = _combat_melee_max_hit_old_hp(
            _combat_effective_player_strength_level(player_data, style_id),
            _equipment_bonus_value(player_totals, "melee_strength"),
        )
    if enemy.get("warriors_guild_gate"):
        player_max_hit *= warriors_guild_cyclops_damage_multiplier_pure(
            player_data
        )
    enemy_max_hit = _combat_enemy_max_hit_old_hp(
        enemy,
        _positive_int(enemy.get("stats", {}).get("strength", 1), 1) + 8,
        _equipment_bonus_value(enemy_totals, "melee_strength"),
        enemy_totals,
    )
    weakening_equipment, weakening_active = _combat_weakening_equipment_state(
        player_data, enemy
    )
    if weakening_active:
        enemy_max_hit *= max(
            0.0,
            float(weakening_equipment.get("enemy_damage_multiplier", 1.0)),
        )
    protective_equipment, protection_active = _combat_protective_equipment_state(
        player_data, enemy, combat_class
    )
    unprotected_effect = (
        protective_equipment.get("unprotected_effect")
        if isinstance(protective_equipment, Mapping) and not protection_active
        else None
    )
    max_lp = combat_max_lifepoints_pure(player_data)
    current_lp = max(0, min(_positive_int(player_data.get("combat_lifepoints", max_lp), max_lp), max_lp))
    enemy_max_lp_hit = (
        _combat_unprotected_damage_lifepoints(unprotected_effect, max_lp)
        + (
            int(enemy_max_hit * 10)
            if isinstance(unprotected_effect, Mapping)
            and bool(unprotected_effect.get("additive_to_attack"))
            else 0
        )
        if isinstance(unprotected_effect, Mapping)
        else int(enemy_max_hit * 10)
    )
    dragonfire_state = combat_dragonfire_protection_pure(player_data, enemy)
    if dragonfire_state:
        dragonfire_spec = enemy.get("dragonfire", {})
        dragonfire_state = {
            **dragonfire_state,
            "chance_numerator": _positive_int(
                dragonfire_spec.get("chance_numerator", 1), 1
            ),
            "chance_denominator": _positive_int(
                dragonfire_spec.get("chance_denominator", 1), 1
            ),
        }
        enemy_max_lp_hit = max(
            enemy_max_lp_hit,
            _non_negative_int(dragonfire_state.get("max_hit", 0), 0),
        )
    encounter = player_data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
    loadout = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    bank_inventory = player_data.get("inventory", {}) or {}
    has_food = False
    for item_name in player_data.get("combat_auto_eat_food", _DEFAULT_COMBAT_AUTO_EAT_FOOD):
        if item_name not in COMBAT_FOOD_DATA:
            continue
        loadout_count = _non_negative_int((loadout.get("food", {}) or {}).get(item_name, 0), 0)
        bank_count = 0 if active_encounter else _non_negative_int(bank_inventory.get(item_name, 0), 0)
        if loadout_count + bank_count > 0:
            has_food = True
            break
    if enemy_max_lp_hit <= 0 or current_lp > enemy_max_lp_hit * 3:
        risk = "Safe"
    elif has_food:
        risk = "Food advised"
    else:
        risk = "Death possible"
    wilderness_spec = (
        enemy.get("wilderness_risk")
        if isinstance(enemy.get("wilderness_risk"), Mapping)
        else None
    )
    wilderness_risk = {}
    if wilderness_spec is not None:
        wilderness_risk = {
            **combat_wilderness_equipment_risk_pure(player_data, enemy),
            "ambush_chance": max(
                0.0,
                min(
                    1.0,
                    float(wilderness_spec.get("ambush_chance", 0.0) or 0.0),
                ),
            ),
            "max_hit": _positive_int(wilderness_spec.get("max_hit", 1), 1),
            "source_status": str(
                wilderness_spec.get("source_status", "") or ""
            ),
        }
        risk = "Wilderness risk"
    poison_damage = _positive_int(enemy.get("poison_damage", 0), 0)
    poison_immunity_ticks = combat_poison_immunity_ticks_pure(player_data)
    poison_lifepoints = 0
    if poison_damage > 0 and poison_immunity_ticks <= 0:
        poison_lifepoints = combat_poison_damage_for_ticks_pure(
            combat_poison_ticks_for_initial_damage_pure(poison_damage)
        )
        if risk == "Safe":
            risk = "Food advised"
    state = (
        "Wilderness risk"
        if wilderness_spec is not None
        else "Fighting"
        if active_encounter
        else "Ready"
    )
    protection_warning = (
        str(protective_equipment.get("warning", ""))
        if isinstance(protective_equipment, Mapping) and not protection_active
        else ""
    )
    finisher_state = combat_finisher_state_pure(
        player_data, target_id, enemy_data
    )
    hazard = _combat_environmental_hazard_spec(enemy)
    hazard_state = (
        {
            "display_name": str(
                hazard.get("display_name", "Environmental hazard")
            ),
            "loaded": _combat_loaded_hazard_count(player_data, hazard),
            "banked": _combat_banked_hazard_count(player_data, hazard),
            "reviews_per_dose": _positive_int(
                hazard.get("reviews_per_dose", 1), 1
            ),
            "source_status": str(hazard.get("source_status", "") or ""),
        }
        if hazard is not None
        else {}
    )
    return {
        "state": state,
        "risk_band": risk,
        "reasons": tuple(),
        "accuracy": accuracy,
        "enemy_max_hit": enemy_max_lp_hit,
        "player_lifepoints": current_lp,
        "player_max_lifepoints": max_lp,
        "enemy_lifepoints": combat_enemy_current_lifepoints_pure(player_data, target_id, enemy_data),
        "enemy_max_lifepoints": _positive_int(enemy.get("stats", {}).get("hitpoints", 0), 0),
        "player_max_hit": int(player_max_hit * 10),
        "ammo": ammo_name or "",
        "spell_id": spell_id if combat_class == "magic" else "",
        "spell": spell_spec.get("display_name", "") if combat_class == "magic" and isinstance(spell_spec, Mapping) else "",
        "runes": dict(spell_spec.get("rune_cost", {}) or {}) if combat_class == "magic" and isinstance(spell_spec, Mapping) else {},
        "weapon": weapon_name or "",
        "poison_damage": poison_lifepoints,
        "poison_chance": COMBAT_POISON_NPC_ATTACK_CHANCE if poison_damage > 0 and poison_immunity_ticks <= 0 else 0.0,
        "poison_immunity_ticks": poison_immunity_ticks,
        "protection_warning": protection_warning,
        "weakening_equipment": {
            "display_name": str(
                weakening_equipment.get("display_name", "Weakening equipment")
            ),
            "active": weakening_active,
            "enemy_accuracy_multiplier": float(
                weakening_equipment.get("enemy_accuracy_multiplier", 1.0)
            ),
            "enemy_damage_multiplier": float(
                weakening_equipment.get("enemy_damage_multiplier", 1.0)
            ),
        }
        if isinstance(weakening_equipment, Mapping)
        else {},
        "finisher": finisher_state,
        "environmental_hazard": hazard_state,
        "dragonfire": dragonfire_state,
        "wilderness_risk": wilderness_risk,
        "source": enemy.get("source", ""),
    }


def combat_enemy_pressure_attack_pure(
    player_data,
    enemy,
    equipment_data=None,
    rng=None,
):
    """Resolve one bounded incoming-only attack through ordinary Combat maths."""
    equipment_data = equipment_data or {}
    rng = rng or (lambda: 0.0)
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data, {"pressure": enemy}))
    player_totals = equipment_stat_totals_pure(
        data.get("equipment", {}) or {}, equipment_data
    )
    enemy_totals = _combat_enemy_bonuses(enemy)
    style_id = combat_attack_style_for_equipment_pure(data, equipment_data)
    player_style = COMBAT_ATTACK_STYLE_DATA.get(
        style_id, COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE]
    )
    player_class = str(player_style.get("combat_class", "melee"))
    enemy_style = _combat_enemy_attack_style(enemy, player_class)
    enemy_class = _combat_enemy_attack_class(enemy, player_class)
    enemy_attack_stat = (
        "attack"
        if enemy_style == "magic_melee"
        else {"magic": "magic", "ranged": "ranged"}.get(enemy_class, "attack")
    )
    enemy_attack_bonus = (
        _combat_attack_bonus_from_totals(enemy_totals, "melee", style_type="stab")
        if enemy_style == "magic_melee"
        else _combat_attack_bonus_from_totals(enemy_totals, enemy_class)
    )
    prayer_effects = prayer_effect_state_pure(data)
    enemy_attack_roll = (
        _positive_int(enemy.get("stats", {}).get(enemy_attack_stat, 1), 1) + 8
    ) * (enemy_attack_bonus + 64)
    player_defence_roll = (
        _combat_effective_player_defence_level(data, style_id)
        * float(prayer_effects.get("defence", 1.0))
        * (_combat_defence_bonus_from_totals(player_totals, enemy_class) + 64)
    )
    accuracy = _combat_accuracy(enemy_attack_roll, player_defence_roll)
    try:
        landed = float(rng()) < accuracy
    except (TypeError, ValueError):
        landed = False
    raw_damage = (
        _combat_roll_damage_lifepoints(
            _combat_enemy_max_hit_old_hp(
                enemy,
                _positive_int(enemy.get("stats", {}).get("strength", 1), 1) + 8,
                _equipment_bonus_value(enemy_totals, "melee_strength"),
                enemy_totals,
            ),
            rng,
        )
        if landed
        else 0
    )
    protection_class = _combat_enemy_protection_class(enemy, player_class)
    protection_key = {
        "magic": "protect_magic",
        "ranged": "protect_ranged",
    }.get(protection_class, "protect_melee")
    damage = int(
        raw_damage * (1.0 - float(prayer_effects.get(protection_key, 0.0)))
    )
    return {
        "attack_style": protection_class,
        "accuracy": accuracy,
        "landed": landed,
        "raw_damage": raw_damage,
        "damage": max(0, damage),
    }


def apply_safe_combat_recovery_pure(player_data, equipment_data=None):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    encounter = data.get("combat_encounter", {}) or {}
    encounter_target = (
        encounter.get("target_id") if isinstance(encounter, Mapping) else None
    )
    encounter_enemy = (
        COMBAT_ENEMY_DATA.get(encounter_target)
        if isinstance(encounter_target, str)
        else None
    )
    if isinstance(encounter_enemy, Mapping) and encounter_enemy.get(
        "wilderness_risk"
    ):
        data["combat_encounter"] = {}
    equipment_data = equipment_data or {}
    max_lp = combat_max_lifepoints_pure(data)
    current_lp = _non_negative_int(data.get("combat_lifepoints", max_lp), max_lp)
    rest_reviews = _non_negative_int(data.get("combat_rest_reviews", 0), 0)
    if current_lp > max_lp:
        data["combat_lifepoints"] = max(max_lp, current_lp - SAFE_COMBAT_RECOVERY_LIFEPOINTS)
    elif current_lp < max_lp:
        # Just left combat: heal to full over COMBAT_REST_FULL_HEAL_REVIEWS reviews
        # (a share of the missing LP each review, so the last one tops off). Once
        # that rest window is spent, fall back to the slow natural-regen trickle.
        missing = max_lp - current_lp
        turns_left = COMBAT_REST_FULL_HEAL_REVIEWS - rest_reviews
        if turns_left >= 1:
            heal = -(-missing // turns_left)  # ceil so the final rest review reaches full
        else:
            heal = NATURAL_COMBAT_RECOVERY_LIFEPOINTS
        effects = prayer_effect_state_pure(data)
        rapid_heal_multiplier = max(1.0, float(effects.get("rapid_heal", 0.0)))
        heal = max(heal, int(NATURAL_COMBAT_RECOVERY_LIFEPOINTS * rapid_heal_multiplier))
        data["combat_lifepoints"] = min(max_lp, current_lp + heal)
    data["combat_rest_reviews"] = rest_reviews + 1
    _combat_regenerate_special_attack_energy(data, SAFE_COMBAT_RECOVERY_TICKS)
    _combat_recover_current_levels(data, SAFE_COMBAT_RECOVERY_TICKS)
    _combat_consume_antipoison_if_needed(data)
    status_result = _combat_advance_status_effects(data, SAFE_COMBAT_RECOVERY_TICKS)
    if status_result.get("died"):
        _combat_apply_pvm_death(data, max_lp, "combat_poison_death")
        return data
    style = COMBAT_ATTACK_STYLE_DATA.get(
        combat_attack_style_for_equipment_pure(data, equipment_data),
        COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE],
    )
    combat_class = str(style.get("combat_class", "melee"))
    target_id = data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    _weapon_name, _equipment_spec, weapon_spec = _combat_ranged_weapon_spec(data, equipment_data)
    _spell_id, spell_spec = _combat_selected_magic_spell(data)
    bank_run_result = _combat_progress_or_start_bank_run(
        data,
        target_id,
        combat_class,
        weapon_spec,
        spell_spec,
        equipment_data,
    )
    if bank_run_result is not None:
        data["combat_last_result"] = bank_run_result
        return data
    data.update(
        sanitize_equipment_instance_state_pure(
            data, EQUIPMENT_CONDITION_DATA
        )
    )
    return data


def start_combat_grave_walk_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    grave = dict(data.get("combat_grave", {}) or {})
    if not grave.get("items") or grave.get("walk_reviews_remaining"):
        return data, False
    grave["walk_reviews_remaining"] = max(
        1, _positive_int(grave.get("travel_reviews", 1), 1)
    )
    data["combat_grave"] = grave
    return data, True


def advance_combat_grave_review_pure(player_data):
    """Advance a chosen walk-back and the universal gravestone expiry clock."""
    data = _copy_player_data_with_nested(player_data)
    grave = data.get("combat_grave", {}) or {}
    if not isinstance(grave, Mapping) or not grave.get("items"):
        return data
    grave = dict(grave)
    walking = _non_negative_int(grave.get("walk_reviews_remaining", 0), 0)
    if walking > 0:
        walking -= 1
        if walking <= 0:
            _combat_reclaim_items_to_player(
                data, grave.get("items", ()) or (), _combat_stored_loadout(grave)
            )
            data["combat_grave"] = {}
            data.update(sanitize_equipment_instance_state_pure(data, EQUIPMENT_CONDITION_DATA))
            return data
        grave["walk_reviews_remaining"] = walking
    remaining = max(0, _positive_int(grave.get("reviews_remaining", 1), 1) - 1)
    grave["reviews_remaining"] = remaining
    data["combat_grave"] = grave if remaining > 0 else {}
    return data


def combat_grave_banner_view_pure(player_data):
    """Return the compact always-visible recovery banner projection."""
    grave = player_data.get("combat_grave", {}) or {}
    grave_items = _combat_grave_items(grave)
    office = combat_death_office_summary_pure(player_data)
    parts = []
    if grave_items:
        remaining = _positive_int(
            grave.get("reviews_remaining", COMBAT_GRAVE_RECOVERY_REVIEWS),
            COMBAT_GRAVE_RECOVERY_REVIEWS,
        )
        walking = _non_negative_int(grave.get("walk_reviews_remaining", 0), 0)
        suffix = (
            f"walking back — {walking} reviews remaining"
            if walking
            else f"expires after {remaining} more reviews — click to walk back"
        )
        parts.append(f"⚰ Gravestone: {len(grave_items)} items — {suffix}")
    if office["item_count"]:
        parts.append(
            f"☠ Death's Office: {office['item_count']} items — reclaim for {office['reclaim_cost']:,} coins"
        )
    return {"visible": bool(parts), "text": "   •   ".join(parts)}


def combat_death_office_items_pure(player_data):
    return tuple(_combat_death_office_items(player_data.get("death_office", {}) or {}))


def combat_death_office_reclaim_cost_pure(player_data):
    return len(combat_death_office_items_pure(player_data)) * COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM


def combat_death_office_summary_pure(player_data):
    items = combat_death_office_items_pure(player_data)
    cost = len(items) * COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM
    inventory = player_data.get("inventory", {}) or {}
    coins = _non_negative_int(inventory.get("Coins", 0), 0) if isinstance(inventory, Mapping) else 0
    return {
        "items": items,
        "item_count": len(items),
        "reclaim_cost": cost,
        "coins": coins,
        "can_reclaim": bool(items) and coins >= cost,
    }


def reclaim_death_office_items_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    items = _combat_death_office_items(data.get("death_office", {}) or {})
    if not items:
        return player_data, False, "No gear is waiting in Death's Office."
    cost = len(items) * COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM
    inventory = dict(data.get("inventory", {}) or {})
    coins = _non_negative_int(inventory.get("Coins", 0), 0)
    if coins < cost:
        return player_data, False, f"Need {cost} Coins to reclaim this gear."
    inventory["Coins"] = coins - cost
    data["inventory"] = inventory
    _combat_reclaim_items_to_player(
        data,
        items,
        _combat_stored_loadout(data.get("death_office", {}) or {}),
    )
    data["death_office"] = {}
    data.update(
        sanitize_equipment_instance_state_pure(
            data, EQUIPMENT_CONDITION_DATA
        )
    )
    return data, True, ""


def _combat_drop_ownership_view(data, pending_drops):
    if not pending_drops:
        return data
    ownership_view = dict(data)
    inventory = dict(data.get("inventory", {}) or {})
    for item_name, amount in pending_drops.items():
        inventory[item_name] = _non_negative_int(
            inventory.get(item_name, 0), 0
        ) + _non_negative_int(amount, 0)
    ownership_view["inventory"] = inventory
    return ownership_view


def apply_combat_burst_pure(
    player_data,
    enemy_data=None,
    equipment_data=None,
    ticks=None,
    rng=None,
    *,
    live_cadence=False,
    stop_after_first_kill=False,
    safe_death=False,
    no_grave=False,
    allow_bank_run=True,
    player_damage_multiplier=1.0,
):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    equipment_data = equipment_data or {}
    rng = rng or (lambda: 0.0)
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data, enemy_data))
    target_id = data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    carried = data.get("carried_inventory")
    current_view = carried.get(target_id) if isinstance(carried, Mapping) else None
    if not isinstance(current_view, Mapping) or not current_view:
        repacked = _combat_custom_layout_view(data, target_id)
        if repacked:
            carried = dict(carried) if isinstance(carried, Mapping) else {}
            carried[target_id] = repacked
            data["carried_inventory"] = carried
    pinned_preset = (data.get("combat_target_presets", {}) or {}).get(target_id)
    if isinstance(pinned_preset, str):
        data, _applied = apply_combat_preset_pure(data, pinned_preset, target_id)
    else:
        data = apply_combat_target_overrides_pure(data, target_id)
    preset_reasons = combat_magic_preset_locked_reasons_pure(data)
    if preset_reasons:
        return player_data, False, {"reason": "combat_locked", "locked_reasons": preset_reasons}
    # Dream trades one review and one cast for its pinned 50 LP/minute healing
    # rate. It happens between fights before supplies or attack rolls.
    max_lp_for_dream = combat_max_lifepoints_pure(data)
    if (
        bool(data.get("combat_dream_thrift", False))
        and not combat_has_active_encounter_pure(data)
        and _non_negative_int(data.get("combat_lifepoints", max_lp_for_dream), max_lp_for_dream) < max_lp_for_dream
    ):
        dream_cost = effective_magic_rune_cost_pure(data, DREAM_COST)
        inventory = data.get("inventory", {}) or {}
        if all(_non_negative_int(inventory.get(rune, 0), 0) >= amount for rune, amount in dream_cost.items()):
            inventory = dict(inventory)
            for rune, amount in dream_cost.items():
                inventory[rune] -= amount
            data["inventory"] = inventory
            healed = min(50, max_lp_for_dream - _non_negative_int(data.get("combat_lifepoints", 0), 0))
            data["combat_lifepoints"] = _non_negative_int(data.get("combat_lifepoints", 0), 0) + healed
            data["magic_exp"] = float(data.get("magic_exp", 0.0) or 0.0) + 82.0
            result = {"reason": "dream", "healed": healed, "xp_rewards": {"magic_exp": 82.0}, "runes_used": dict(dream_cost), "ticks": 0, "ticks_elapsed": 0}
            data["combat_last_result"] = result
            return data, True, result
    if target_id not in enemy_data:
        locked_reasons = combat_target_locked_reasons_pure(data, target_id, enemy_data, equipment_data=equipment_data)
        return player_data, False, {"reason": "combat_locked", "locked_reasons": locked_reasons}
    style_id = combat_attack_style_for_equipment_pure(data, equipment_data)
    data["combat_attack_style"] = style_id
    style = COMBAT_ATTACK_STYLE_DATA.get(style_id, COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE])
    combat_class = str(style.get("combat_class", "melee"))
    # melee_style_type feeds the D1 attack/defence-type parity; melee_xp_style_id
    # captures the two-handed-sword aggressive/crush/SHARED xp anomaly (defaults to
    # style_id, so ranged/magic keep their existing xp path unchanged).
    melee_style_type = None
    melee_xp_style_id = style_id
    if combat_class == "melee":
        _melee_slot = _combat_resolve_melee_slot(data, equipment_data)
        melee_style_type = _melee_slot["style_type"]
        melee_xp_style_id = _COMBAT_XP_MODE_TO_STYLE_ID[_melee_slot["xp_mode"]]
    weapon_name, weapon_spec, ranged_weapon_spec = _combat_ranged_weapon_spec(data, equipment_data)
    spell_id, spell_spec = _combat_selected_magic_spell(data)
    borrowed_manual_cast = bool(spell_spec.get("borrowed_spell_id"))
    locked_reasons = combat_target_locked_reasons_pure(data, target_id, enemy_data, equipment_data=equipment_data)
    bank_run_result = (
        _combat_progress_or_start_bank_run(
            data,
            target_id,
            combat_class,
            ranged_weapon_spec,
            spell_spec,
            equipment_data,
            enemy_data,
        )
        if allow_bank_run
        else None
    )
    if bank_run_result is not None:
        if not _combat_locks_can_bank_run(locked_reasons):
            return player_data, False, {"reason": "combat_locked", "locked_reasons": locked_reasons}
        data["combat_last_result"] = bank_run_result
        return data, True, bank_run_result
    if locked_reasons:
        return player_data, False, {"reason": "combat_locked", "locked_reasons": locked_reasons}
    enemy = enemy_data[target_id]
    wilderness_equipment_risk = combat_wilderness_equipment_risk_pure(
        data,
        enemy,
    )
    finisher = _combat_finisher_spec(enemy)
    hazard = _combat_environmental_hazard_spec(enemy)
    hazard_supply = (
        _combat_consume_hazard_dose(data, hazard)
        if hazard is not None
        else None
    )
    if hazard is not None and hazard_supply is None:
        return player_data, False, {
            "reason": "combat_locked",
            "locked_reasons": (
                f"{hazard.get('display_name', 'Environmental hazard')}: "
                "filled Waterskin",
            ),
        }

    encounter = data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
    spellbook_swap_paid = bool(active_encounter and encounter.get("spellbook_swap_paid", False))
    vengeance_pending = bool(active_encounter and encounter.get("vengeance_pending", False))
    vengeance_cast_paid = bool(
        active_encounter and encounter.get("vengeance_cast_paid", False)
    )
    supplemental_used = {}
    supplemental_magic_xp = 0.0
    pending_supplemental = _combat_pending_supplemental_magic_costs_pure(
        data, equipment_data
    )
    if live_cadence and vengeance_cast_paid:
        pending_supplemental = tuple(
            row for row in pending_supplemental if row[0] != "vengeance"
        )
    for label, cost, xp in pending_supplemental:
        used = _combat_consume_loaded_rune_cost(data, cost)
        if used is None:
            return player_data, False, {"reason": "combat_locked", "locked_reasons": (f"{label.replace('_', ' ').title()} runes",)}
        for rune, amount in used.items():
            supplemental_used[rune] = supplemental_used.get(rune, 0) + amount
        supplemental_magic_xp += xp
        if label == "spellbook_swap":
            spellbook_swap_paid = True
        elif label == "vengeance":
            vengeance_pending = True
            vengeance_cast_paid = True

    # Auto-drink carried stat potions before the rolls are computed, so the boost
    # flows through the effective-level reads into this burst's max-hit/accuracy.
    stat_potion_events = _combat_auto_drink_potions(data, combat_class)
    dragonfire_potion_event = _combat_consume_dragonfire_if_needed(data, enemy)

    max_player_lp = combat_max_lifepoints_pure(data)
    player_lp = max(
        0,
        min(
            _non_negative_int(data.get("combat_lifepoints", max_player_lp), max_player_lp),
            max_player_lp + COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
        ),
    )
    enemy_max_lp = _positive_int(enemy.get("stats", {}).get("hitpoints", 1), 1)
    if active_encounter:
        enemy_lp = max(0, min(_positive_int(encounter.get("enemy_lifepoints", enemy_max_lp), enemy_max_lp), enemy_max_lp))
    else:
        enemy_lp = enemy_max_lp
    regeneration = (
        enemy.get("regeneration")
        if isinstance(enemy.get("regeneration"), Mapping)
        else None
    )
    enemy_regen_numerator = (
        _positive_int(regeneration.get("lifepoints_per_tick_numerator", 0), 0)
        if regeneration is not None
        else 0
    )
    enemy_regen_denominator = (
        _positive_int(regeneration.get("lifepoints_per_tick_denominator", 1), 1)
        if regeneration is not None
        else 1
    )
    enemy_regen_residual = (
        _non_negative_int(encounter.get("regeneration_residual", 0), 0)
        % enemy_regen_denominator
        if active_encounter and enemy_regen_numerator > 0
        else 0
    )
    retaliation_stop_lifepoints = _non_negative_int(
        enemy.get("retaliation_stop_lifepoints", 0), 0
    )
    retaliation_stopped = bool(
        retaliation_stop_lifepoints > 0
        and (
            enemy_lp <= retaliation_stop_lifepoints
            or (active_encounter and encounter.get("retaliation_stopped", False))
        )
    )

    player_totals = equipment_stat_totals_pure(data.get("equipment", {}) or {}, equipment_data)
    enemy_totals = _combat_enemy_bonuses(enemy)
    player_attack_speed = max(1, _positive_int(_equipment_value(weapon_spec, "attack_speed", 4), 4))
    if combat_class == "ranged":
        player_attack_speed = max(1, player_attack_speed + _signed_int(style.get("attack_speed_delta", 0), 0))
    elif combat_class == "magic":
        player_attack_speed = max(1, _positive_int(spell_spec.get("attack_speed", 5), 5))
    enemy_attack_speed = max(1, _positive_int(enemy.get("attack_speed", 4), 4))
    selected_prayers = tuple(active_prayer_selection_pure(data))
    equipped_items = data.get("equipment")
    halo_drain_multipliers = (
        {
            prayer_id: 2.0 / 3.0
            for prayer_id in selected_prayers
            if prayer_id in CASTLE_WARS_HALO_DRAIN_PRAYERS
        }
        if isinstance(equipped_items, Mapping)
        and str(equipped_items.get("head", "")) == "Saradomin halo"
        else {}
    )
    requested_prayer_uptime = (
        float(PRAYER_UPTIME_POLICIES.get(str(data.get("combat_prayer_uptime", "off")), 0.0))
        if live_cadence and selected_prayers
        else prayer_uptime_fraction_pure(data)
    )
    total_ticks = (
        1
        + (
            _non_negative_int(
                encounter.get("player_attack_ticks_remaining", 0),
                0,
            )
            if borrowed_manual_cast and live_cadence and active_encounter
            else 0
        )
        if borrowed_manual_cast
        else max(1, _positive_int(ticks, COMBAT_BURST_TICKS))
    )
    prayer_points_before = _non_negative_int(data.get("combat_prayer_points", 0), 0)
    prayer_counter_before = data.get("combat_prayer_drain_counter", 0.0)
    prayer_points_after, prayer_counter, prayer_uptime = (
        (
            prayer_points_before,
            prayer_counter_before,
            requested_prayer_uptime,
        )
        if live_cadence
        else prayer_drain_and_effective_uptime_pure(
            prayer_points_before,
            prayer_counter_before,
            selected_prayers,
            _equipment_bonus_value(player_totals, "prayer"),
            total_ticks,
            requested_prayer_uptime,
            halo_drain_multipliers,
        )
    )
    data["combat_prayer_points"] = prayer_points_after
    data["combat_prayer_drain_counter"] = prayer_counter
    prayer_effects = prayer_effect_state_pure(data, prayer_uptime)
    if prayer_points_after <= 0 and selected_prayers and not live_cadence:
        data["combat_selected_prayers"] = []

    # Curse ramps are reset for each fight. The burst EV uses the attacks a
    # single full-health enemy is expected to survive, bounded by this review.
    expected_attacks = (
        0
        if live_cadence
        else max(1, int(max(1, _positive_int(ticks, COMBAT_BURST_TICKS)) / player_attack_speed))
    )
    sap_ramp = curse_expected_ramp_pure(expected_attacks, "sap")
    leech_ramp = curse_expected_ramp_pure(expected_attacks, "leech")
    spell_effect = str(spell_spec.get("effect", "")) if combat_class == "magic" else ""
    spell_effect_value = float(spell_spec.get("effect_value", 0.0) or 0.0) if combat_class == "magic" else 0.0
    magic_effects_applied = (
        {
            str(effect)
            for effect in encounter.get("magic_effects_applied", ())
            if isinstance(effect, str)
        }
        if live_cadence and active_encounter
        else set()
    )
    magic_effect_applied = spell_effect in magic_effects_applied
    enemy_attack_factor = (
        max(
            0.01,
            min(
                1.0,
                _non_negative_float(
                    encounter.get("spell_enemy_attack_factor", 1.0),
                    1.0,
                ),
            ),
        )
        if live_cadence and active_encounter
        else 1.0
    )
    enemy_defence_factor = (
        max(
            0.01,
            min(
                1.0,
                _non_negative_float(
                    encounter.get("spell_enemy_defence_factor", 1.0),
                    1.0,
                ),
            ),
        )
        if live_cadence and active_encounter
        else 1.0
    )
    if spell_effect in {"attack_drain", "strength_drain", "magic_drain"} and (
        not live_cadence or not magic_effect_applied
    ):
        enemy_attack_factor *= max(0.0, 1.0 - spell_effect_value)
        if live_cadence:
            magic_effects_applied.add(spell_effect)
            magic_effect_applied = True
    if spell_effect in {"defence_drain"} and (
        not live_cadence or not magic_effect_applied
    ):
        enemy_defence_factor *= max(0.0, 1.0 - spell_effect_value)
        if live_cadence:
            magic_effects_applied.add(spell_effect)
            magic_effect_applied = True
    spell_enemy_attack_factor = enemy_attack_factor
    spell_enemy_defence_factor = enemy_defence_factor
    for prayer_id in selected_prayers:
        if prayer_id.startswith("sap_"):
            enemy_attack_factor *= 1.0 - sap_ramp["enemy_drain"] * prayer_uptime
            if prayer_id != "sap_spirit":
                enemy_defence_factor *= 1.0 - sap_ramp["enemy_drain"] * prayer_uptime
        elif prayer_id.startswith("leech_"):
            if prayer_id in ("leech_attack", "leech_ranged", "leech_magic", "leech_strength"):
                enemy_attack_factor *= 1.0 - leech_ramp["enemy_drain"] * prayer_uptime
            if prayer_id == "leech_defence":
                enemy_defence_factor *= 1.0 - leech_ramp["enemy_drain"] * prayer_uptime
            self_effect = 1.0 + leech_ramp["self_boost"] * prayer_uptime
            leech_effect_key = {
                "leech_attack": "attack", "leech_strength": "strength",
                "leech_defence": "defence", "leech_ranged": "ranged",
                "leech_magic": "magic",
            }.get(prayer_id)
            if leech_effect_key:
                prayer_effects[leech_effect_key] = max(float(prayer_effects.get(leech_effect_key, 1.0)), self_effect)
    if "turmoil" in selected_prayers:
        enemy_stats = enemy.get("stats", {}) or {}
        for key, enemy_key, base_bonus, enemy_bonus in (
            ("attack", "attack", .15, .15),
            ("defence", "defence", .15, .15),
            ("strength", "strength", .23, .10),
        ):
            player_base = max(1, _combat_base_skill_level(data, "defense" if key == "defence" else key, 1))
            enemy_level = _positive_int(enemy_stats.get(enemy_key, 1), 1)
            turmoil_level = player_base * (1.0 + base_bonus * prayer_uptime) + enemy_bonus * enemy_level * prayer_uptime
            prayer_effects[key] = max(float(prayer_effects.get(key, 1.0)), turmoil_level / player_base)

    selected_ammo = None
    if combat_class == "ranged":
        selected_ammo = _combat_selected_ranged_ammo(data, ranged_weapon_spec, target_id)
        player_attack_roll = _combat_effective_player_ranged_level(data, style_id) * float(prayer_effects.get("ranged_attack", prayer_effects.get("ranged", 1.0))) * (
            _combat_attack_bonus_from_totals(player_totals, "ranged") + 64
        )
        enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * enemy_defence_factor * (
            _combat_defence_bonus_from_totals(enemy_totals, "ranged") + 64
        )
        player_max_hit = _combat_ranged_max_hit_old_hp(
            _combat_effective_player_ranged_level(data, style_id) * float(prayer_effects.get("ranged_strength", prayer_effects.get("ranged", 1.0))),
            _combat_ranged_strength_bonus(player_totals, selected_ammo),
        )
    elif combat_class == "magic":
        player_attack_roll = _combat_effective_player_magic_level(data) * float(prayer_effects.get("magic", 1.0)) * (
            _combat_attack_bonus_from_totals(player_totals, "magic") + 64
        )
        enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * enemy_defence_factor * (
            _combat_defence_bonus_from_totals(enemy_totals, "magic") + 64
        )
        player_max_hit = _combat_magic_max_hit_old_hp(
            spell_spec,
            player_totals,
            data,
            spell_id,
        )
    else:
        player_attack_roll = _combat_effective_player_attack_level(data, style_id) * float(prayer_effects.get("attack", 1.0)) * (
            _combat_attack_bonus_from_totals(player_totals, style_type=melee_style_type) + 64
        )
        enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * enemy_defence_factor * (
            _combat_defence_bonus_from_totals(enemy_totals, style_type=melee_style_type) + 64
        )
        player_max_hit = _combat_melee_max_hit_old_hp(
            _combat_effective_player_strength_level(data, style_id) * float(prayer_effects.get("strength", 1.0)),
            _equipment_bonus_value(player_totals, "melee_strength"),
        )
    if enemy.get("warriors_guild_gate"):
        player_max_hit *= warriors_guild_cyclops_damage_multiplier_pure(data)
    player_accuracy = _combat_accuracy(player_attack_roll, enemy_defence_roll)

    # The enemy attacks with ITS style: a mage's accuracy comes off its magic
    # level + magic attack bonus, and the player resists with magic defence.
    enemy_style = _combat_enemy_attack_style(enemy, combat_class)
    enemy_class = _combat_enemy_attack_class(enemy, combat_class)
    magic_melee = enemy_style == "magic_melee"
    enemy_attack_stat = (
        "attack"
        if magic_melee
        else {"magic": "magic", "ranged": "ranged"}.get(enemy_class, "attack")
    )
    enemy_attack_bonus = (
        _combat_attack_bonus_from_totals(
            enemy_totals,
            "melee",
            style_type="stab",
        )
        if magic_melee
        else _combat_attack_bonus_from_totals(enemy_totals, enemy_class)
    )
    enemy_attack_roll = (
        _positive_int(enemy.get("stats", {}).get(enemy_attack_stat, 1), 1) + 8
    ) * enemy_attack_factor * (enemy_attack_bonus + 64)
    weakening_equipment, weakening_active = _combat_weakening_equipment_state(
        data, enemy
    )
    if weakening_active:
        enemy_attack_roll *= max(
            0.0,
            float(weakening_equipment.get("enemy_accuracy_multiplier", 1.0)),
        )
    player_defence_roll = _combat_effective_player_defence_level(data, style_id) * float(prayer_effects.get("defence", 1.0)) * (
        _combat_defence_bonus_from_totals(player_totals, enemy_class) + 64
    )
    enemy_accuracy = _combat_accuracy(enemy_attack_roll, player_defence_roll)
    enemy_max_hit = _combat_enemy_max_hit_old_hp(
        enemy,
        _positive_int(enemy.get("stats", {}).get("strength", 1), 1) + 8,
        _equipment_bonus_value(enemy_totals, "melee_strength"),
        enemy_totals,
    )
    if weakening_active:
        enemy_max_hit *= max(
            0.0,
            float(weakening_equipment.get("enemy_damage_multiplier", 1.0)),
        )
    protective_equipment, protection_active = _combat_protective_equipment_state(
        data, enemy, combat_class
    )
    start_equipment, start_equipment_active = _combat_start_equipment_state(
        data, enemy
    )
    unprotected_effect = (
        protective_equipment.get("unprotected_effect")
        if isinstance(protective_equipment, Mapping)
        and not protection_active
        and not protective_equipment.get("attack_kind")
        else None
    )

    next_player_attack = (
        _non_negative_int(encounter.get("player_attack_ticks_remaining", 0), 0)
        if live_cadence and active_encounter
        else 0
    )
    next_enemy_attack = (
        _non_negative_int(
            encounter.get("enemy_attack_ticks_remaining", enemy_attack_speed),
            enemy_attack_speed,
        )
        if live_cadence and active_encounter
        else enemy_attack_speed
    )
    curse_attack_count = (
        _non_negative_int(encounter.get("curse_attack_count", 0), 0)
        if live_cadence and active_encounter
        else 0
    )

    def _live_curse_adjustments(tick_uptime):
        enemy_drain = 0.0
        self_boost = 0.0
        if any(prayer_id.startswith("sap_") for prayer_id in selected_prayers):
            enemy_drain = max(
                enemy_drain,
                curse_expected_ramp_pure(curse_attack_count, "sap")["enemy_drain"],
            )
        if any(prayer_id.startswith("leech_") for prayer_id in selected_prayers):
            ramp = curse_expected_ramp_pure(curse_attack_count, "leech")
            enemy_drain = max(enemy_drain, ramp["enemy_drain"])
            self_boost = max(self_boost, ramp["self_boost"])
        return enemy_drain * tick_uptime, self_boost * tick_uptime

    def _live_prayer_factor(effect_key, tick_uptime):
        fallback_key = "ranged" if effect_key.startswith("ranged_") else effect_key
        full = float(prayer_effects.get(effect_key, prayer_effects.get(fallback_key, 1.0)))
        if prayer_uptime <= 0:
            return 1.0
        ratio = max(0.0, min(float(tick_uptime) / prayer_uptime, 1.0))
        return 1.0 + (full - 1.0) * ratio

    player_damage = 0
    player_hits_landed = 0
    enemy_damage = 0
    food_used = []
    potions_used = list(stat_potion_events)
    if dragonfire_potion_event:
        potions_used.append(dragonfire_potion_event)
    ammo_used = {}
    runes_used = {}
    for rune_name, amount in supplemental_used.items():
        runes_used[rune_name] = runes_used.get(rune_name, 0) + amount
    status_damage = {}
    status_applied = {}
    status_expired = []
    unprotected_attacks = 0
    stat_drains = {}
    enemy_specials = []
    automatic_finishers = 0
    enemy_healing = 0
    vampyre_bites = 0
    vampyre_bite_healing = 0
    dragonfire_attacks = 0
    dragonfire_damage = 0
    melee_recoil_damage = 0
    enemy_prayer_drain = 0
    dragonfire_effect_tick = 0
    bite_spec = enemy.get("bite") if isinstance(enemy.get("bite"), Mapping) else None
    xp_rewards = {"magic_exp": supplemental_magic_xp} if supplemental_magic_xp > 0 else {}
    drops = {}
    clue_refusal_reason = ""
    kills = 0
    killed = False
    died = False
    fled = False
    familiar_escape = False
    out_of_ammo = False
    out_of_runes = False
    npc_xp_multiplier = _combat_npc_xp_multiplier(enemy)
    ticks_elapsed = 0
    # This is a live combat review, so the out-of-combat rest window restarts from
    # zero; the next non-combat review begins healing you back toward full.
    data["combat_rest_reviews"] = 0

    for tick in range(total_ticks):
        ticks_elapsed = tick + 1
        if enemy_regen_numerator > 0:
            if enemy_lp < enemy_max_lp:
                enemy_regen_residual += enemy_regen_numerator
                healing = min(
                    enemy_max_lp - enemy_lp,
                    enemy_regen_residual // enemy_regen_denominator,
                )
                if healing > 0:
                    enemy_lp += healing
                    enemy_healing += healing
                    enemy_regen_residual -= healing * enemy_regen_denominator
            else:
                enemy_regen_residual = 0
        tick_prayer_uptime = prayer_uptime
        if live_cadence:
            (
                prayer_points_after,
                prayer_counter,
                tick_prayer_uptime,
            ) = prayer_drain_and_effective_uptime_pure(
                prayer_points_after,
                prayer_counter,
                selected_prayers,
                _equipment_bonus_value(player_totals, "prayer"),
                1,
                requested_prayer_uptime,
                halo_drain_multipliers,
            )
            data["combat_prayer_points"] = prayer_points_after
            data["combat_prayer_drain_counter"] = prayer_counter
        potion_event = _combat_consume_antipoison_if_needed(data)
        if potion_event:
            potions_used.append(potion_event)
        status_result = _combat_advance_status_effects(data, 1, player_lp, max_player_lp)
        player_lp = _non_negative_int(data.get("combat_lifepoints", player_lp), player_lp)
        for effect_name, amount in (status_result.get("damage", {}) or {}).items():
            status_damage[effect_name] = _non_negative_int(status_damage.get(effect_name, 0), 0) + _non_negative_int(amount, 0)
        status_expired.extend(status_result.get("expired", ()) or ())
        if status_result.get("died"):
            died = True
            break
        if status_result.get("damage"):
            player_lp, food_event = _combat_consume_auto_food(data, player_lp, max_player_lp, rng)
            if food_event:
                food_used.append(food_event)

        if status_result.get("damage") and _combat_void_shifter_escape_ready(
            data, player_lp, max_player_lp
        ):
            fled = True
            familiar_escape = True
            break
        if _combat_should_auto_flee(data, player_lp, max_player_lp):
            fled = True
            break

        if tick >= next_player_attack and enemy_lp > 0:
            next_player_attack += player_attack_speed
            if combat_class == "ranged":
                ammo_name = _combat_consume_ranged_ammo(data, ranged_weapon_spec, target_id)
                if ammo_name is None:
                    out_of_ammo = True
                    break
                selected_ammo = ammo_name
                ammo_used[ammo_name] = _non_negative_int(ammo_used.get(ammo_name, 0), 0) + 1
            elif combat_class == "magic":
                used = _combat_consume_magic_runes(data, spell_spec, target_id, equipment_data)
                if used is None:
                    out_of_runes = True
                    break
                for rune_name, amount in used.items():
                    runes_used[rune_name] = _non_negative_int(runes_used.get(rune_name, 0), 0) + amount
                if borrowed_manual_cast:
                    from ..logic.livid_farm_logic import consume_arcane_capacitor_charge_pure
                    data, charge_used, _charge_info = (
                        consume_arcane_capacitor_charge_pure(
                            data,
                            spell_spec["borrowed_spell_id"],
                        )
                    )
                    if not charge_used:
                        out_of_runes = True
                        break
                    data["combat_borrowed_power_spell"] = ""
            landed = False
            live_enemy_drain, live_self_boost = (
                _live_curse_adjustments(tick_prayer_uptime)
                if live_cadence
                else (0.0, 0.0)
            )
            live_player_accuracy = player_accuracy
            live_player_max_hit = player_max_hit
            if live_cadence:
                attack_effect_key = {
                    "ranged": "ranged_attack",
                    "magic": "magic",
                }.get(combat_class, "attack")
                strength_effect_key = {
                    "ranged": "ranged_strength",
                    "magic": "magic",
                }.get(combat_class, "strength")
                full_attack_factor = max(
                    0.000001,
                    float(
                        prayer_effects.get(
                            attack_effect_key,
                            prayer_effects.get(
                                "ranged" if combat_class == "ranged" else attack_effect_key,
                                1.0,
                            ),
                        )
                    ),
                )
                full_strength_factor = max(
                    0.000001,
                    float(
                        prayer_effects.get(
                            strength_effect_key,
                            prayer_effects.get(
                                "ranged" if combat_class == "ranged" else strength_effect_key,
                                1.0,
                            ),
                        )
                    ),
                )
                current_attack_factor = _live_prayer_factor(
                    attack_effect_key, tick_prayer_uptime
                )
                current_strength_factor = _live_prayer_factor(
                    strength_effect_key, tick_prayer_uptime
                )
                current_enemy_defence_factor = max(
                    0.01,
                    spell_enemy_defence_factor * (1.0 - live_enemy_drain),
                )
                live_player_accuracy = _combat_accuracy(
                    player_attack_roll / full_attack_factor * current_attack_factor,
                    enemy_defence_roll
                    / max(enemy_defence_factor, 0.000001)
                    * current_enemy_defence_factor,
                )
                live_player_max_hit = max(
                    0,
                    int(
                        player_max_hit
                        / full_strength_factor
                        * current_strength_factor
                        * (1.0 + live_self_boost)
                    ),
                )
            try:
                landed = float(rng()) < live_player_accuracy
            except (TypeError, ValueError):
                landed = False
            if enemy.get("protect_from_player_class") == combat_class:
                landed = False
            if landed:
                player_hits_landed += 1
            damage = _combat_roll_damage_lifepoints(live_player_max_hit, rng) if landed else 0
            try:
                damage = int(damage * max(0.0, float(player_damage_multiplier)))
            except (TypeError, ValueError, OverflowError):
                pass
            if live_cadence:
                curse_attack_count += 1
            damage, automatic_finisher = _combat_cap_damage_for_finisher(
                data, finisher, enemy_lp, damage
            )
            if automatic_finisher:
                automatic_finishers += 1
            if damage > 0:
                enemy_lp -= damage
                player_damage += damage
                if combat_class == "melee":
                    recoil = min(
                        player_lp,
                        _non_negative_int(enemy.get("melee_recoil_damage", 0), 0),
                    )
                    if recoil > 0:
                        player_lp -= recoil
                        melee_recoil_damage += recoil
                        if player_lp <= 0:
                            died = True
                if combat_class == "magic" and landed:
                    if spell_effect == "blood_heal":
                        player_lp = min(max_player_lp, player_lp + int(damage * spell_effect_value))
                    elif spell_effect == "freeze":
                        next_enemy_attack += max(0, int(spell_effect_value / .6))
                    elif spell_effect == "poison" and not magic_effect_applied:
                        if not bool(enemy.get("poison_immune", False)):
                            poison_ev, automatic_finisher = _combat_cap_damage_for_finisher(
                                data,
                                finisher,
                                enemy_lp,
                                max(0, int(spell_effect_value)),
                            )
                            if automatic_finisher:
                                automatic_finishers += 1
                            enemy_lp -= poison_ev
                            player_damage += poison_ev
                        magic_effect_applied = True
                        magic_effects_applied.add(spell_effect)
                    elif spell_effect == "defence_flat" and not magic_effect_applied:
                        enemy_defence_factor = max(.01, enemy_defence_factor - spell_effect_value / 100.0)
                        spell_enemy_defence_factor = enemy_defence_factor
                        magic_effect_applied = True
                        magic_effects_applied.add(spell_effect)
                soul_split_uptime = (
                    tick_prayer_uptime if live_cadence else prayer_uptime
                )
                soul_split_heal = int(
                    damage
                    * float(prayer_effects.get("soul_split", 0.0))
                    * (
                        soul_split_uptime / prayer_uptime
                        if prayer_uptime > 0
                        else 0.0
                    )
                )
                if soul_split_heal > 0:
                    player_lp = min(max_player_lp, player_lp + soul_split_heal)
            if combat_class == "magic":
                _combat_apply_magic_xp(xp_rewards, spell_spec, damage, npc_xp_multiplier)
            elif damage > 0:
                _combat_apply_xp(xp_rewards, melee_xp_style_id, damage, npc_xp_multiplier)
            if died and enemy_lp > 0:
                break
            if enemy_lp <= 0:
                kills += 1
                killed = True
                rolled_drops, refused_clue = _combat_roll_drops(
                    enemy,
                    rng,
                    _combat_drop_ownership_view(data, drops),
                    include_clue_refusal=True,
                )
                clue_refusal_reason = clue_refusal_reason or refused_clue
                kill_drops = _combat_apply_triple_charm_reward(data, rolled_drops)
                data, kill_drops, passive_prayer_xp, prayer_ticks, _prayer_effects = resolve_prayer_kill_effects_pure(
                    data,
                    target_id,
                    kill_drops,
                    bool(data.get("combat_auto_prayer_training")),
                )
                _record_combat_observed_drops_pure(data, target_id, kill_drops)
                if passive_prayer_xp > 0:
                    xp_rewards["prayer_exp"] = float(xp_rewards.get("prayer_exp", 0.0) or 0.0) + passive_prayer_xp
                next_player_attack += prayer_ticks
                for drop_name, drop_amount in kill_drops.items():
                    drops[drop_name] = _non_negative_int(drops.get(drop_name, 0), 0) + _non_negative_int(drop_amount, 0)
                # Chain into the next spawn of the same target for the remaining
                # tick budget instead of ending the burst on the first kill (the
                # old `break` wasted up to half of a ~30s review window). A fresh
                # enemy respawns at full LP and re-engages after its normal attack
                # delay, so it gets no free instant hit on the kill tick.
                if (
                    live_cadence
                    or stop_after_first_kill
                    or (
                        isinstance(start_equipment, Mapping)
                        and not start_equipment_active
                    )
                ):
                    break
                enemy_lp = enemy_max_lp
                next_enemy_attack = tick + 1 + enemy_attack_speed
                continue

        if (
            retaliation_stop_lifepoints > 0
            and enemy_lp <= retaliation_stop_lifepoints
        ):
            retaliation_stopped = True
        if tick >= next_enemy_attack and enemy_lp > 0 and not retaliation_stopped:
            next_enemy_attack += enemy_attack_speed
            attack_spec = _combat_select_enemy_attack_pure(enemy, rng)
            attack_kind = str(attack_spec.get("kind", "attack"))
            if attack_kind == "teleport":
                delay = _non_negative_int(
                    attack_spec.get("player_delay_ticks", 0), 0
                )
                next_player_attack += delay
                enemy_specials.append({"kind": "teleport", "delay_ticks": delay})
                break
            if attack_kind == "unequip":
                before_equipment = dict(data.get("equipment", {}) or {})
                slot_order = ("weapon",) + tuple(
                    sorted(slot for slot in before_equipment if slot != "weapon")
                )
                removed_item = ""
                removed_slot = ""
                for slot in slot_order:
                    item_name = before_equipment.get(slot)
                    if not isinstance(item_name, str) or not item_name:
                        continue
                    removed_item = item_name
                    removed_slot = slot
                    break
                if removed_item:
                    equipment = dict(before_equipment)
                    equipment.pop(removed_slot, None)
                    inventory = dict(data.get("inventory", {}) or {})
                    inventory[removed_item] = int(inventory.get(removed_item, 0) or 0) + 1
                    carried = dict(data.get("carried_inventory", {}) or {})
                    carried_view = dict(carried.get(target_id, {}) or {})
                    carried_view[removed_item] = (
                        int(carried_view.get(removed_item, 0) or 0) + 1
                    )
                    carried[target_id] = carried_view
                    data["equipment"] = equipment
                    data["inventory"] = inventory
                    data["carried_inventory"] = carried
                    data = sync_equipment_instances_pure(
                        data, before_equipment, EQUIPMENT_CONDITION_DATA
                    )
                enemy_specials.append(
                    {
                        "kind": "unequip",
                        "item": removed_item,
                        "slot": removed_slot,
                    }
                )
                break

            attack_enemy = enemy
            selected_style = attack_spec.get("style")
            if selected_style in {"melee", "ranged", "magic", "magic_melee"}:
                attack_enemy = dict(enemy)
                attack_enemy["attack_style"] = selected_style
                attack_enemy.pop("attack_style_by_player_class", None)
            enemy_style = _combat_enemy_attack_style(attack_enemy, combat_class)
            enemy_class = _combat_enemy_attack_class(attack_enemy, combat_class)
            magic_melee = enemy_style == "magic_melee"
            enemy_attack_stat = (
                "attack"
                if magic_melee
                else {"magic": "magic", "ranged": "ranged"}.get(
                    enemy_class, "attack"
                )
            )
            enemy_attack_bonus = (
                _combat_attack_bonus_from_totals(
                    enemy_totals, "melee", style_type="stab"
                )
                if magic_melee
                else _combat_attack_bonus_from_totals(enemy_totals, enemy_class)
            )
            enemy_attack_roll = (
                _positive_int(
                    attack_enemy.get("stats", {}).get(enemy_attack_stat, 1), 1
                )
                + 8
            ) * enemy_attack_factor * (enemy_attack_bonus + 64)
            if weakening_active:
                enemy_attack_roll *= max(
                    0.0,
                    float(
                        weakening_equipment.get("enemy_accuracy_multiplier", 1.0)
                    ),
                )
            player_defence_roll = (
                _combat_effective_player_defence_level(data, style_id)
                * float(prayer_effects.get("defence", 1.0))
                * (_combat_defence_bonus_from_totals(player_totals, enemy_class) + 64)
            )
            enemy_accuracy = _combat_accuracy(
                enemy_attack_roll, player_defence_roll
            )
            enemy_max_hit = _combat_enemy_max_hit_old_hp(
                attack_enemy,
                _positive_int(
                    attack_enemy.get("stats", {}).get("strength", 1), 1
                )
                + 8,
                _equipment_bonus_value(enemy_totals, "melee_strength"),
                enemy_totals,
            )
            if weakening_active:
                enemy_max_hit *= max(
                    0.0,
                    float(
                        weakening_equipment.get("enemy_damage_multiplier", 1.0)
                    ),
                )
            _combat_advance_dragonfire_effects(
                data, tick - dragonfire_effect_tick
            )
            dragonfire_effect_tick = tick
            dragonfire_potion_event = _combat_consume_dragonfire_if_needed(
                data, enemy
            )
            if dragonfire_potion_event:
                potions_used.append(dragonfire_potion_event)
            dragonfire_spec = (
                enemy.get("dragonfire")
                if isinstance(enemy.get("dragonfire"), Mapping)
                else None
            )
            dragonfire_attack = False
            if dragonfire_spec is not None:
                try:
                    dragonfire_attack = float(rng()) < (
                        _positive_int(
                            dragonfire_spec.get("chance_numerator", 1), 1
                        )
                        / _positive_int(
                            dragonfire_spec.get("chance_denominator", 1), 1
                        )
                    )
                except (TypeError, ValueError):
                    dragonfire_attack = False
            wyvern_breath_spec = (
                enemy.get("wyvern_breath")
                if attack_kind == "wyvern_breath"
                and isinstance(enemy.get("wyvern_breath"), Mapping)
                else None
            )
            if wyvern_breath_spec is not None:
                equipped_shield = str((data.get("equipment", {}) or {}).get("shield", ""))
                if protection_active:
                    breath_max_hit = _non_negative_int(
                        wyvern_breath_spec.get("shielded_max_hit", 0), 0
                    )
                    try:
                        breath_roll = max(
                            0.0, min(float(rng()), 0.999999999999)
                        )
                    except (TypeError, ValueError):
                        breath_roll = 0.0
                    damage = int(breath_roll * (breath_max_hit + 1))
                else:
                    breath_effect = (
                        protective_equipment.get("unprotected_effect")
                        if isinstance(protective_equipment, Mapping)
                        else None
                    )
                    damage = _combat_unprotected_damage_lifepoints(
                        breath_effect, max_player_lp, rng
                    )
                    unprotected_attacks += 1
                    breath_max_hit = _non_negative_int(
                        ((breath_effect or {}).get("damage") or {}).get("max", 0),
                        0,
                    )
                delay = _non_negative_int(
                    wyvern_breath_spec.get("player_delay_ticks", 0), 0
                )
                next_player_attack += delay
                enemy_specials.append(
                    {
                        "kind": "wyvern_breath",
                        "protected": bool(protection_active),
                        "shield_item": equipped_shield,
                        "max_hit": breath_max_hit,
                        "delay_ticks": delay,
                    }
                )
            elif dragonfire_attack:
                dragonfire_attacks += 1
                dragonfire_state = combat_dragonfire_protection_pure(
                    data,
                    enemy,
                    magic_prayer_active=bool(
                        tick_prayer_uptime > 0
                        and float(
                            prayer_effects.get("protect_magic", 0.0)
                        )
                        > 0.0
                    ),
                )
                dragonfire_max_hit = _non_negative_int(
                    dragonfire_state.get("max_hit", 0), 0
                )
                try:
                    dragonfire_roll = max(
                        0.0, min(float(rng()), 0.999999999999)
                    )
                except (TypeError, ValueError):
                    dragonfire_roll = 0.0
                damage = int(dragonfire_roll * (dragonfire_max_hit + 1))
            elif (
                isinstance(unprotected_effect, Mapping)
                and not bool(unprotected_effect.get("additive_to_attack"))
            ):
                damage = _combat_unprotected_damage_lifepoints(unprotected_effect, max_player_lp)
                unprotected_attacks += 1
                stat_drain_prayer = unprotected_effect.get(
                    "stat_drain_protection_prayer"
                )
                stat_drain_blocked = (
                    isinstance(stat_drain_prayer, str)
                    and tick_prayer_uptime > 0
                    and float(prayer_effects.get(stat_drain_prayer, 0.0)) > 0.0
                )
                attack_drains = (
                    {}
                    if stat_drain_blocked
                    else _combat_apply_unprotected_stat_drains(
                        data, unprotected_effect, rng
                    )
                )
                for skill_id, amount in attack_drains.items():
                    stat_drains[skill_id] = _non_negative_int(stat_drains.get(skill_id, 0), 0) + amount
                if attack_drains:
                    if combat_class == "ranged":
                        player_attack_roll = _combat_effective_player_ranged_level(data, style_id) * float(
                            prayer_effects.get("ranged_attack", prayer_effects.get("ranged", 1.0))
                        ) * (_combat_attack_bonus_from_totals(player_totals, "ranged") + 64)
                        player_max_hit = _combat_ranged_max_hit_old_hp(
                            _combat_effective_player_ranged_level(data, style_id) * float(
                                prayer_effects.get("ranged_strength", prayer_effects.get("ranged", 1.0))
                            ),
                            _combat_ranged_strength_bonus(player_totals, selected_ammo),
                        )
                    elif combat_class == "magic":
                        player_attack_roll = _combat_effective_player_magic_level(data) * float(
                            prayer_effects.get("magic", 1.0)
                        ) * (_combat_attack_bonus_from_totals(player_totals, "magic") + 64)
                        player_max_hit = _combat_magic_max_hit_old_hp(
                            spell_spec,
                            player_totals,
                            data,
                            spell_id,
                        )
                    else:
                        player_attack_roll = _combat_effective_player_attack_level(data, style_id) * float(
                            prayer_effects.get("attack", 1.0)
                        ) * (
                            _combat_attack_bonus_from_totals(
                                player_totals,
                                style_type=melee_style_type,
                            )
                            + 64
                        )
                        player_max_hit = _combat_melee_max_hit_old_hp(
                            _combat_effective_player_strength_level(data, style_id)
                            * float(prayer_effects.get("strength", 1.0)),
                            _equipment_bonus_value(player_totals, "melee_strength"),
                        )
                    player_accuracy = _combat_accuracy(player_attack_roll, enemy_defence_roll)
            else:
                landed = False
                live_enemy_accuracy = enemy_accuracy
                if live_cadence:
                    live_enemy_drain, _live_self_boost = (
                        _live_curse_adjustments(tick_prayer_uptime)
                    )
                    full_defence_factor = max(
                        0.000001, float(prayer_effects.get("defence", 1.0))
                    )
                    current_defence_factor = _live_prayer_factor(
                        "defence", tick_prayer_uptime
                    )
                    current_enemy_attack_factor = max(
                        0.01,
                        spell_enemy_attack_factor * (1.0 - live_enemy_drain),
                    )
                    live_enemy_accuracy = _combat_accuracy(
                        enemy_attack_roll
                        / max(enemy_attack_factor, 0.000001)
                        * current_enemy_attack_factor,
                        player_defence_roll
                        / full_defence_factor
                        * current_defence_factor,
                    )
                try:
                    landed = float(rng()) < live_enemy_accuracy
                except (TypeError, ValueError):
                    landed = False
                damage = _combat_roll_damage_lifepoints(enemy_max_hit, rng) if landed else 0
            raw_enemy_damage = damage
            prayer_drain_base = _non_negative_int(
                enemy.get("prayer_drain_base", 0), 0
            )
            if prayer_drain_base > 0:
                prayer_drain = prayer_drain_base
                if bool(enemy.get("prayer_drain_damage", False)):
                    prayer_drain += max(0, raw_enemy_damage)
                prayer_drain = min(prayer_points_after, prayer_drain)
                prayer_points_after -= prayer_drain
                enemy_prayer_drain += prayer_drain
                data["combat_prayer_points"] = prayer_points_after
            if (
                not dragonfire_attack
                and wyvern_breath_spec is None
                and (
                    not isinstance(unprotected_effect, Mapping)
                    or bool(
                        unprotected_effect.get(
                            "protection_prayer_applies"
                        )
                    )
                )
            ):
                protection_class = _combat_enemy_protection_class(
                    attack_enemy, combat_class
                )
                protection_key = {
                    "magic": "protect_magic",
                    "ranged": "protect_ranged",
                }.get(protection_class, "protect_melee")
                protection_scale = (
                    tick_prayer_uptime / prayer_uptime
                    if live_cadence and prayer_uptime > 0
                    else 1.0
                )
                damage = int(
                    damage
                    * (
                        1.0
                        - float(prayer_effects.get(protection_key, 0.0))
                        * protection_scale
                    )
                )
            if (
                isinstance(unprotected_effect, Mapping)
                and bool(unprotected_effect.get("additive_to_attack"))
            ):
                damage += _combat_unprotected_damage_lifepoints(
                    unprotected_effect, max_player_lp, rng
                )
                unprotected_attacks += 1
            damage = min(player_lp, damage)
            if dragonfire_attack:
                dragonfire_damage += damage
            if damage > 0:
                player_lp -= damage
                enemy_damage += damage
                if vengeance_pending:
                    (
                        reflected_vengeance,
                        automatic_finisher,
                    ) = _combat_cap_damage_for_finisher(
                        data,
                        finisher,
                        enemy_lp,
                        int(raw_enemy_damage * .75),
                    )
                    if automatic_finisher:
                        automatic_finishers += 1
                    if reflected_vengeance > 0:
                        enemy_lp -= reflected_vengeance
                        player_damage += reflected_vengeance
                    vengeance_pending = False
                deflect_scale = (
                    tick_prayer_uptime / prayer_uptime
                    if live_cadence and prayer_uptime > 0
                    else 1.0
                )
                reflected, automatic_finisher = _combat_cap_damage_for_finisher(
                    data,
                    finisher,
                    enemy_lp,
                    int(
                        raw_enemy_damage
                        * float(prayer_effects.get("deflect", 0.0))
                        * deflect_scale
                    ),
                )
                if automatic_finisher:
                    automatic_finishers += 1
                if reflected > 0:
                    enemy_lp -= reflected
                    player_damage += reflected
                if isinstance(bite_spec, Mapping) and enemy_lp > 0:
                    bite_numerator = _positive_int(
                        bite_spec.get("chance_numerator", 1), 1
                    )
                    bite_denominator = _positive_int(
                        bite_spec.get("chance_denominator", 1), 1
                    )
                    try:
                        bite_triggered = (
                            float(rng()) < bite_numerator / bite_denominator
                        )
                    except (TypeError, ValueError):
                        bite_triggered = False
                    if bite_triggered:
                        vampyre_bites += 1
                        bite_skills = tuple(
                            skill_id
                            for skill_id in (
                                bite_spec.get("stat_drain_skills", ()) or ()
                            )
                            if isinstance(skill_id, str)
                        )
                        if bite_skills:
                            try:
                                skill_roll = max(
                                    0.0, min(float(rng()), 0.999999999999)
                                )
                            except (TypeError, ValueError):
                                skill_roll = 0.0
                            drained_skill = bite_skills[
                                int(skill_roll * len(bite_skills))
                            ]
                            bite_drains = _combat_apply_unprotected_stat_drains(
                                data,
                                {
                                    "stat_drain": {
                                        "kind": "flat_to_floor",
                                        "amount": _positive_int(
                                            bite_spec.get(
                                                "stat_drain_amount", 1
                                            ),
                                            1,
                                        ),
                                        "floor": _positive_int(
                                            bite_spec.get(
                                                "stat_drain_floor", 1
                                            ),
                                            1,
                                        ),
                                        "skills": (drained_skill,),
                                    },
                                },
                            )
                            for skill_id, amount in bite_drains.items():
                                stat_drains[skill_id] = (
                                    _non_negative_int(
                                        stat_drains.get(skill_id, 0), 0
                                    )
                                    + amount
                                )
                        bite_healing = min(
                            max(0, damage),
                            _positive_int(bite_spec.get("max_heal", 1), 1),
                            max(0, enemy_max_lp - enemy_lp),
                        )
                        if bite_healing > 0:
                            enemy_lp += bite_healing
                            enemy_healing += bite_healing
                            vampyre_bite_healing += bite_healing
            if (
                0 < player_lp < max_player_lp * .10
                and tick_prayer_uptime > 0
                and float(prayer_effects.get("redemption", 0.0)) > 0
            ):
                # RuneScape Wiki Redemption oldid=6292830: heal 250% of Prayer
                # level below 10% LP, then consume every remaining prayer point.
                player_lp = min(
                    max_player_lp,
                    player_lp
                    + int(
                        _positive_int(data.get("prayer_level", 1), 1)
                        * 2.5
                        * tick_prayer_uptime
                    ),
                )
                data["combat_prayer_points"] = 0
                prayer_points_after = 0
                data["combat_prayer_drain_counter"] = 0.0
                prayer_counter = 0.0
                data["combat_selected_prayers"] = []
            if player_lp <= 0:
                died = True
                break
            if _combat_void_shifter_escape_ready(
                data, player_lp, max_player_lp
            ):
                fled = True
                familiar_escape = True
                break
            if enemy_lp <= 0:
                kills += 1
                killed = True
                rolled_drops, refused_clue = _combat_roll_drops(
                    enemy,
                    rng,
                    _combat_drop_ownership_view(data, drops),
                    include_clue_refusal=True,
                )
                clue_refusal_reason = clue_refusal_reason or refused_clue
                kill_drops = _combat_apply_triple_charm_reward(data, rolled_drops)
                data, kill_drops, passive_prayer_xp, prayer_ticks, _prayer_effects = resolve_prayer_kill_effects_pure(
                    data,
                    target_id,
                    kill_drops,
                    bool(data.get("combat_auto_prayer_training")),
                )
                _record_combat_observed_drops_pure(data, target_id, kill_drops)
                if passive_prayer_xp > 0:
                    xp_rewards["prayer_exp"] = float(xp_rewards.get("prayer_exp", 0.0) or 0.0) + passive_prayer_xp
                next_player_attack += prayer_ticks
                for drop_name, drop_amount in kill_drops.items():
                    drops[drop_name] = _non_negative_int(drops.get(drop_name, 0), 0) + _non_negative_int(drop_amount, 0)
                if (
                    live_cadence
                    or stop_after_first_kill
                    or (
                        isinstance(start_equipment, Mapping)
                        and not start_equipment_active
                    )
                ):
                    break
                enemy_lp = enemy_max_lp
                enemy_regen_residual = 0
                retaliation_stopped = False
                next_enemy_attack = tick + 1 + enemy_attack_speed
                continue
            player_lp, food_event = _combat_consume_auto_food(data, player_lp, max_player_lp, rng)
            if food_event:
                food_used.append(food_event)
            poison_damage = _positive_int(enemy.get("poison_damage", 0), 0)
            if poison_damage > 0:
                try:
                    poison_roll = float(rng())
                except (TypeError, ValueError):
                    poison_roll = 1.0
                if poison_roll < COMBAT_POISON_NPC_ATTACK_CHANCE:
                    applied, _reason = _combat_apply_poison_effect_to_data(data, poison_damage)
                    if applied:
                        status_applied["poison"] = combat_poison_damage_for_ticks_pure(
                            combat_poison_ticks_for_initial_damage_pure(poison_damage)
                        )
                        potion_event = _combat_consume_antipoison_if_needed(data)
                        if potion_event:
                            potions_used.append(potion_event)

    data, equipment_condition_events = advance_equipped_condition_pure(
        data, ticks_elapsed, EQUIPMENT_CONDITION_DATA
    )
    inventory = data.get("inventory", {}) or {}
    for item_name, amount in drops.items():
        inventory[item_name] = inventory.get(item_name, 0) + amount
    data["inventory"] = inventory

    for exp_key, amount in xp_rewards.items():
        data[exp_key] = data.get(exp_key, 0.0) + amount

    # Chaining means a single burst can defeat several enemies and still end in
    # a partial survivor or a death, so kills, death, and the carried encounter
    # are now independent rather than mutually exclusive branches.
    if kills > 0:
        kill_counts = dict(data.get("combat_kill_counts", {}) or {})
        kill_counts[target_id] = _positive_int(kill_counts.get(target_id, 0), 0) + kills
        data["combat_kill_counts"] = kill_counts

    death_burst = 0
    if died:
        if "wrath" in selected_prayers or "retribution" in selected_prayers:
            cap_multiplier = 2.5 if "wrath" in selected_prayers else .25
            try:
                death_roll = max(0.0, min(1.0, float(rng())))
            except (TypeError, ValueError):
                death_roll = 0.0
            death_burst, automatic_finisher = _combat_cap_damage_for_finisher(
                data,
                finisher,
                enemy_lp,
                int(
                    _positive_int(data.get("prayer_level", 1), 1)
                    * cap_multiplier
                    * death_roll
                ),
                allow_automatic=False,
            )
            if automatic_finisher:
                automatic_finishers += 1
            enemy_lp -= death_burst
            player_damage += death_burst
        if safe_death:
            data["combat_encounter"] = {}
            data["combat_status_effects"] = {}
            player_lp = max_player_lp
        else:
            player_lp = _combat_apply_pvm_death(
                data,
                max_player_lp,
                no_grave=no_grave,
            )
    elif fled or enemy_lp <= 0 or (enemy_lp >= enemy_max_lp and not live_cadence):
        # No partial progress to carry: the player fled, nothing was fought, or the
        # burst ended right after a kill respawned a fresh full-LP enemy.
        data["combat_encounter"] = {}
    else:
        next_encounter = {"target_id": target_id, "enemy_lifepoints": enemy_lp}
        if live_cadence:
            next_encounter.update(
                {
                    "player_attack_ticks_remaining": max(
                        0, next_player_attack - ticks_elapsed
                    ),
                    "enemy_attack_ticks_remaining": max(
                        0, next_enemy_attack - ticks_elapsed
                    ),
                    "curse_attack_count": curse_attack_count,
                    "magic_effects_applied": tuple(sorted(magic_effects_applied)),
                    "spell_enemy_attack_factor": spell_enemy_attack_factor,
                    "spell_enemy_defence_factor": spell_enemy_defence_factor,
                }
            )
        if enemy_regen_numerator > 0:
            next_encounter["regeneration_residual"] = enemy_regen_residual
        if retaliation_stop_lifepoints > 0 and retaliation_stopped:
            next_encounter["retaliation_stopped"] = True
        if spellbook_swap_paid:
            next_encounter["spellbook_swap_paid"] = True
        if bool(data.get("combat_vengeance", False)) or vengeance_pending:
            next_encounter["vengeance_pending"] = bool(vengeance_pending)
        if live_cadence and vengeance_cast_paid:
            next_encounter["vengeance_cast_paid"] = True
        data["combat_encounter"] = next_encounter

    if live_cadence and prayer_points_after <= 0 and selected_prayers:
        data["combat_selected_prayers"] = []

    _combat_advance_dragonfire_effects(
        data, ticks_elapsed - dragonfire_effect_tick
    )
    if live_cadence:
        data.update(
            advance_temporary_effects_pure(
                data,
                elapsed_ticks=ticks_elapsed,
                advance_dragonfire=False,
            )
        )
    _combat_regenerate_special_attack_energy(
        data, ticks_elapsed, exact=live_cadence
    )
    wilderness_ambush = None
    if not died and not fled:
        wilderness_ambush = _combat_apply_wilderness_ambush(
            data,
            enemy,
            player_lp,
            max_player_lp,
            rng,
            wilderness_equipment_risk,
        )
        if wilderness_ambush and wilderness_ambush.get("triggered"):
            food_event = wilderness_ambush.get("food_used")
            if food_event:
                food_used.append(food_event)
            if wilderness_ambush.get("died"):
                died = True
                player_lp = max_player_lp
            else:
                player_lp = _non_negative_int(
                    wilderness_ambush.get("lifepoints_after", player_lp),
                    player_lp,
                )
    data["combat_lifepoints"] = player_lp
    result = {
        "reason": "combat_burst",
        "target_id": target_id,
        "display_name": enemy.get("display_name", target_id),
        "ticks": total_ticks,
        "ticks_elapsed": ticks_elapsed,
        "player_damage": player_damage,
        "player_hits_landed": player_hits_landed,
        "enemy_damage": enemy_damage,
        "enemy_healing": enemy_healing,
        "vampyre_bites": vampyre_bites,
        "vampyre_bite_healing": vampyre_bite_healing,
        "dragonfire_attacks": dragonfire_attacks,
        "dragonfire_damage": dragonfire_damage,
        "melee_recoil_damage": melee_recoil_damage,
        "enemy_prayer_drain": enemy_prayer_drain,
        "safe_death": bool(died and safe_death),
        "dragonfire_protection": combat_dragonfire_protection_pure(
            data, enemy
        ),
        "enemy_retaliation_stopped": retaliation_stopped,
        "enemy_lifepoints": enemy_lp,
        "player_lifepoints": player_lp,
        "killed": killed,
        "kills": kills,
        "died": died,
        "fled": fled,
        "familiar_escape": familiar_escape,
        "wilderness_ambush": wilderness_ambush or {},
        "stop_reason": (
            "out_of_ammo" if out_of_ammo
            else "out_of_runes" if out_of_runes
            else "void_shifter" if familiar_escape
            else "auto_flee" if fled
            else ""
        ),
        "food_used": tuple(food_used),
        "potions_used": tuple(potions_used),
        "ammo_used": dict(ammo_used),
        "runes_used": dict(runes_used),
        "status_damage": dict(status_damage),
        "status_applied": dict(status_applied),
        "status_expired": tuple(dict.fromkeys(status_expired)),
        "unprotected_attacks": unprotected_attacks,
        "stat_drains": dict(stat_drains),
        "enemy_specials": tuple(enemy_specials),
        "finisher_ready": bool(
            finisher is not None
            and 0
            < enemy_lp
            <= _positive_int(finisher.get("threshold_lifepoints", 0), 0)
        ),
        "automatic_finishers": automatic_finishers,
        "hazard_supplies_used": (hazard_supply,) if hazard_supply else tuple(),
        "protection_warning": (
            str(protective_equipment.get("warning", ""))
            if isinstance(protective_equipment, Mapping) and not protection_active
            else ""
        ),
        "drops": drops,
        "clue_refusal_reason": clue_refusal_reason,
        "xp_rewards": xp_rewards,
        "prayer_points_before": prayer_points_before,
        "prayer_points_after": prayer_points_after,
        "prayers": selected_prayers,
        "prayer_uptime": prayer_uptime,
        "death_prayer_damage": death_burst if died else 0,
        "player_accuracy": player_accuracy,
        "enemy_accuracy": enemy_accuracy,
        "combat_class": combat_class,
        "weapon": weapon_name or "",
        "ammo": selected_ammo or "",
        "spell_id": spell_id if combat_class == "magic" else "",
        "spell": spell_spec.get("display_name", "") if combat_class == "magic" and isinstance(spell_spec, Mapping) else "",
        "borrowed_power": borrowed_manual_cast and bool(runes_used),
        "formula_source": (
            RANGED_FORMULA_SOURCE_PATH
            if combat_class == "ranged"
            else MAGIC_FORMULA_SOURCE_PATH
            if combat_class == "magic"
            else MELEE_FORMULA_SOURCE_PATH
        ),
        "xp_source": (
            RANGED_STRATEGY_SOURCE_PATH
            if combat_class == "ranged"
            else MAGIC_STRATEGY_SOURCE_PATH
            if combat_class == "magic"
            else MELEE_STRATEGY_SOURCE_PATH
        ),
        "equipment_condition_events": equipment_condition_events,
    }
    data["combat_last_result"] = result
    return data, True, result


def _blocked_toolbelt_rows(label, skill_label, skill_level, bound_ids, tool_data):
    """Attached tools of one family the player cannot use yet, weakest gate first."""
    rows: list = []
    for tool_id, spec in tool_data.items():
        if spec.get("status", "implemented") != "implemented":
            continue
        required = _non_negative_int(spec.get("level", 1), 1)
        if required <= skill_level or tool_id not in bound_ids:
            continue
        display_name = str(spec.get("display_name", tool_id))
        rows.append((label, display_name, skill_label, required))
    rows.sort(key=lambda row: (row[3], row[1]))
    return rows


def bank_gear_rows_pure(player_data, pickaxe_data, axe_data, _bonus_item_data):
    """Read-only Bank summary of explicitly attached and worn gear.

    Buying or looting a better gathering tool leaves it in the Bank. The active
    row changes only after the player uses the Bank's attach action. Attached
    tools above the player's level remain visible in ``toolbelt_blocked`` while
    the best usable attached tool stays active.

    Returns {"toolbelt": [(label, display_name), ...],
             "toolbelt_blocked": [(label, display_name, skill_label, level), ...],
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

    blocked_rows: list = []
    for label, skill_label, level_key, tool_data in (
        ("Pickaxe", "Mining", "mining_level", pickaxe_data),
        ("Hatchet", "Woodcutting", "woodcutting_level", axe_data),
    ):
        blocked_rows.extend(
            _blocked_toolbelt_rows(
                label,
                skill_label,
                _non_negative_int(player_data.get(level_key, 1), 1),
                _toolbelt_ids(toolbelt, skill_label.lower()),
                tool_data,
            )
        )

    equipped_rows: list = []
    equipment = player_data.get("equipment", {}) or {}
    if isinstance(equipment, Mapping):
        for slot, item_name in equipment.items():
            if isinstance(slot, str) and isinstance(item_name, str):
                equipped_rows.append((slot, item_name))
    return {
        "toolbelt": toolbelt_rows,
        "toolbelt_blocked": blocked_rows,
        "equipped": equipped_rows,
    }


def combat_supply_loadout_summary_pure(player_data):
    loadout = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    return {
        "food_loaded_items": dict(loadout.get("food", {}) or {}),
        "potions_loaded": sum(_non_negative_int(amount, 0) for amount in (loadout.get("potions", {}) or {}).values()),
        "potions_loaded_items": dict(loadout.get("potions", {}) or {}),
        "stat_potions_loaded": sum(_non_negative_int(amount, 0) for amount in (loadout.get("stat_potions", {}) or {}).values()),
        "stat_potions_loaded_items": dict(loadout.get("stat_potions", {}) or {}),
        "ammo_loaded": dict(loadout.get("ammo", {}) or {}),
        "runes_loaded": dict(loadout.get("runes", {}) or {}),
        "finishers_loaded": dict(loadout.get("finishers", {}) or {}),
        "hazards_loaded": dict(loadout.get("hazards", {}) or {}),
        "cannonballs_loaded": _non_negative_int(loadout.get("cannonballs", 0), 0),
    }


def combat_has_active_encounter_pure(player_data):
    encounter = player_data.get("combat_encounter", {}) or {}
    return (
        isinstance(encounter, Mapping)
        and isinstance(encounter.get("target_id"), str)
        and not bool(encounter.get("disengaged"))
    )


def request_combat_bank_run_now_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    if combat_has_active_encounter_pure(data):
        return data, False, "An active fight must end before making a bank run."
    active_run = data.get("combat_bank_run")
    if isinstance(active_run, Mapping) and _non_negative_int(
        active_run.get("reviews_remaining", 0), 0
    ) > 0:
        return data, True, ""
    target_id = data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    data["combat_bank_run"] = {
        "reviews_remaining": COMBAT_BANK_RUN_REVIEWS,
        "target_id": target_id,
    }
    return data, True, ""


def reconcile_combat_method_pure(player_data, updates, equipment_data=None):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    if combat_has_active_encounter_pure(data):
        return data, False, "Finish the active fight before changing combat method."
    data.update(updates)
    method_updates = {
        key: updates[key]
        for key in (
            "combat_action",
            "combat_attack_style",
            "combat_attack_style_type",
            "current_combat_spell",
            "combat_pack_mode",
        )
        if key in updates
    }
    data, ok, reason = unload_combat_supply_loadout_pure(data)
    if not ok:
        return data, False, reason
    data, ok, reason = refill_combat_supply_loadout_pure(data, equipment_data)
    data.update(method_updates)
    return data, ok, reason


def set_combat_pack_mode_pure(player_data, mode, equipment_data=None):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    data["combat_pack_mode"] = _combat_coerce_pack_mode(mode)
    data = derive_casual_combat_magic_pure(data)
    return reconcile_combat_method_pure(player_data, data, equipment_data)


def set_combat_auto_eat_threshold_pure(player_data, threshold_percent):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    data["combat_auto_eat_threshold_percent"] = max(1, min(_positive_int(threshold_percent, 40), 99))
    return data


def set_combat_auto_eat_food_pure(player_data, food_name):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    if not isinstance(food_name, str) or food_name not in COMBAT_FOOD_DATA:
        return data, False, "unsupported food"
    existing = data.get("combat_auto_eat_food", []) or []
    data["combat_auto_eat_food"] = [food_name] + [
        item_name
        for item_name in existing
        if isinstance(item_name, str) and item_name in COMBAT_FOOD_DATA and item_name != food_name
    ]
    return data, True, ""


def refill_combat_supply_loadout_pure(player_data, equipment_data=None):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    if combat_has_active_encounter_pure(data):
        return data, False, "An active fight cannot refill supplies between review bursts."
    _combat_refill_food_loadout(data)
    _combat_refill_antipoison_loadout(data)
    style = COMBAT_ATTACK_STYLE_DATA.get(
        combat_attack_style_for_equipment_pure(data, equipment_data or {}),
        COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE],
    )
    combat_class = str(style.get("combat_class", "melee"))
    _combat_refill_stat_potions(data, combat_class)
    if combat_class == "ranged":
        _weapon_name, _equipment_spec, weapon_spec = _combat_ranged_weapon_spec(data, equipment_data or {})
        _combat_refill_ranged_ammo_loadout(data, weapon_spec)
    _spell_id, spell_spec = _combat_selected_magic_spell(data)
    rune_cost = _combat_required_rune_cost_pure(data, combat_class, spell_spec, equipment_data or {})
    if rune_cost:
        _combat_refill_magic_rune_loadout(data, rune_cost)
    target_id = data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    enemy = COMBAT_ENEMY_DATA.get(target_id, {})
    _combat_refill_finisher_loadout(data, enemy)
    _combat_refill_dragonfire_loadout(data, enemy)
    _combat_refill_hazard_loadout(data, enemy)
    _combat_trim_food_to_capacity(data)
    return data, True, ""


def unload_combat_supply_loadout_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    if combat_has_active_encounter_pure(data):
        return data, False, "An active fight cannot unload supplies between review bursts."
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    inventory = dict(data.get("inventory", {}) or {})
    for key in ("food", "potions", "stat_potions", "ammo", "runes", "finishers", "hazards"):
        for item_name, amount in (loadout.get(key, {}) or {}).items():
            if isinstance(item_name, str):
                inventory[item_name] = _non_negative_int(inventory.get(item_name, 0), 0) + _non_negative_int(amount, 0)
    cannonballs = _non_negative_int(loadout.get("cannonballs", 0), 0)
    if cannonballs > 0:
        inventory["Cannonball"] = _non_negative_int(inventory.get("Cannonball", 0), 0) + cannonballs
    data["inventory"] = inventory
    data["combat_supply_loadout"] = default_combat_supply_loadout_pure()
    return data, True, ""


def player_combat_level_pure(player_data):
    attack = _positive_int(player_data.get("attack_level", 1), 1)
    defence = _positive_int(player_data.get("defense_level", 1), 1)
    strength = _positive_int(player_data.get("strength_level", 1), 1)
    constitution = _positive_int(player_data.get("constitution_level", 10), 10)
    prayer = _positive_int(player_data.get("prayer_level", 1), 1)
    ranged = _positive_int(player_data.get("ranged_level", 1), 1)
    magic = _positive_int(player_data.get("magic_level", 1), 1)
    summoning = _positive_int(player_data.get("summoning_level", 1), 1)
    base = 0.25 * (defence + constitution + int(prayer * 0.5) + int(summoning * 0.5))
    melee = base + 0.325 * (attack + strength)
    ranged_score = base + 0.325 * (int(ranged * 0.5) + ranged)
    magic_score = base + 0.325 * (int(magic * 0.5) + magic)
    return int(max(melee, ranged_score, magic_score))


# Which skill exp keys each attack style feeds, mirroring _combat_apply_xp /
# _combat_apply_magic_xp so the HUD chips and the Combat stats screen name
# exactly the skills a burst will train. Constitution is always trained on damage
# and is appended separately.
_COMBAT_STYLE_XP_KEYS = {
    "accurate": ("attack_exp",),
    "aggressive": ("strength_exp",),
    "defensive": ("defense_exp",),
    "controlled": ("attack_exp", "strength_exp", "defense_exp"),
    "ranged_accurate": ("ranged_exp",),
    "ranged_rapid": ("ranged_exp",),
    "ranged_longrange": ("ranged_exp", "defense_exp"),
    "magic_standard": ("magic_exp",),
}


_COMBAT_EXP_KEY_DISPLAY = {
    "attack_exp": "Attack",
    "strength_exp": "Strength",
    "defense_exp": "Defence",
    "ranged_exp": "Ranged",
    "magic_exp": "Magic",
    "constitution_exp": "Constitution",
}


def combat_attack_style_trained_skills_pure(style_id):
    """Display names of the skills a given attack style trains, Constitution last."""
    keys = _COMBAT_STYLE_XP_KEYS.get(style_id, _COMBAT_STYLE_XP_KEYS[DEFAULT_COMBAT_ATTACK_STYLE])
    ordered = list(keys) + ["constitution_exp"]
    return tuple(_COMBAT_EXP_KEY_DISPLAY[key] for key in ordered)


def combat_weapon_style_options_pure(player_data, equipment_data=None):
    """UI-ready attack-style options for the equipped weapon (D2 per-weapon slots).

    For a melee weapon this is one row per AttackStyleData slot, each carrying the
    weapon_style and style_type to persist, a display name that names the attack
    type (e.g. "Aggressive (Crush)"), the skills it actually trains, and whether it
    is the current selection. Ranged/magic keep the class-filtered
    COMBAT_ATTACK_STYLE_DATA rows with a fixed "auto" style_type. Each row is
    ``{weapon_style, style_type, display_name, trained_skills, is_current}``."""
    if _combat_weapon_is_ranged(player_data, equipment_data) or _combat_weapon_is_magic(player_data, equipment_data):
        current = combat_attack_style_for_equipment_pure(player_data, equipment_data)
        combat_class = str(COMBAT_ATTACK_STYLE_DATA.get(current, {}).get("combat_class", "ranged"))
        return [
            {
                "weapon_style": sid,
                "style_type": "auto",
                "display_name": str(spec.get("display_name", sid)),
                "trained_skills": combat_attack_style_trained_skills_pure(sid),
                "is_current": sid == current,
            }
            for sid, spec in COMBAT_ATTACK_STYLE_DATA.items()
            if str(spec.get("combat_class")) == combat_class
        ]
    slots = combat_weapon_attack_style_slots_pure(player_data, equipment_data)
    current_slot = _combat_resolve_melee_slot(player_data, equipment_data)
    return [
        {
            "weapon_style": slot["weapon_style"],
            "style_type": slot["style_type"],
            "display_name": f"{slot['weapon_style'].title()} ({slot['style_type'].title()})",
            "trained_skills": combat_attack_style_trained_skills_pure(
                _COMBAT_XP_MODE_TO_STYLE_ID[slot["xp_mode"]]
            ),
            "is_current": slot is current_slot,
        }
        for slot in slots
    ]


def combat_hud_state_pure(player_data, enemy_data=None, equipment_data=None):
    """Structured view the combat HUD renders: player and enemy health bars, the
    skills the current attack style trains (the XP chips), and the running kill
    count. Kept pure so the Qt widget stays a thin renderer."""
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    max_lp = combat_max_lifepoints_pure(player_data)
    current_lp = max(0, min(_non_negative_int(player_data.get("combat_lifepoints", max_lp), max_lp), max_lp))
    prayer_max = _positive_int(player_data.get("prayer_level", 1), 1)
    prayer_current = min(
        prayer_max * 10,
        _non_negative_int(
            player_data.get("combat_prayer_points", prayer_max * 10),
            prayer_max * 10,
        ),
    ) // 10
    summoning_max = _positive_int(player_data.get("summoning_level", 1), 1)
    summoning_state = player_data.get("summoning_state", {}) or {}
    summoning_current = min(
        summoning_max,
        _non_negative_int(
            summoning_state.get("summoning_points_current", summoning_max)
            if isinstance(summoning_state, Mapping)
            else summoning_max,
            summoning_max,
        ),
    )

    target_id = player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    enemy = enemy_data.get(target_id) if isinstance(target_id, str) else None
    if isinstance(enemy, Mapping):
        enemy_name = str(enemy.get("display_name", target_id))
        enemy_max_lp = _positive_int(enemy.get("stats", {}).get("hitpoints", 1), 1)
    else:
        enemy_name = "Enemy"
        enemy_max_lp = 0
    encounter = player_data.get("combat_encounter", {}) or {}
    carried = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id and enemy_max_lp > 0
    if carried:
        enemy_lp = max(0, min(_positive_int(encounter.get("enemy_lifepoints", enemy_max_lp), enemy_max_lp), enemy_max_lp))
    else:
        enemy_lp = enemy_max_lp

    style_id = combat_attack_style_for_equipment_pure(player_data, equipment_data)
    style = COMBAT_ATTACK_STYLE_DATA.get(style_id, {})
    # xp_style_id captures the two-handed-sword aggressive/crush/SHARED anomaly so
    # the XP chips name the skills actually trained, not what weapon_style implies.
    _melee_style_type, xp_style_id = combat_melee_attack_type_pure(player_data, equipment_data)

    kills_total = _non_negative_int((player_data.get("combat_kill_counts", {}) or {}).get(target_id, 0), 0)
    last = player_data.get("combat_last_result", {}) or {}
    last = last if isinstance(last, Mapping) else {}
    last_kills = _non_negative_int(last.get("kills", 0), 0)
    if last.get("died"):
        last_outcome = "died"
    elif last.get("fled"):
        last_outcome = "fled"
    else:
        last_outcome = ""

    def _pct(value, ceiling):
        return int((min(value, ceiling) / ceiling) * 100) if ceiling > 0 else 0

    finisher = combat_finisher_state_pure(player_data, target_id, enemy_data)
    status = combat_status_summary_pure(player_data)
    if finisher["ready"]:
        finisher_status = (
            f"Finisher ready: {finisher['action_label']}"
            if finisher["available"]
            else f"Finisher blocked: no loaded {finisher['item']}"
        )
        status = f"{status} · {finisher_status}" if status else finisher_status
    return {
        "combat_level": player_combat_level_pure(player_data),
        "player_lifepoints": current_lp,
        "player_max_lifepoints": max_lp,
        "player_pct": _pct(current_lp, max_lp),
        "prayer_points": prayer_current,
        "prayer_max_points": prayer_max,
        "summoning_points": summoning_current,
        "summoning_max_points": summoning_max,
        "enemy_name": enemy_name,
        "enemy_lifepoints": enemy_lp,
        "enemy_max_lifepoints": enemy_max_lp,
        "enemy_pct": _pct(enemy_lp, enemy_max_lp),
        "enemy_carried": bool(carried),
        "attack_style_id": style_id,
        "attack_style_name": str(style.get("display_name", style_id)),
        "trained_skills": combat_attack_style_trained_skills_pure(xp_style_id),
        "kills_total": kills_total,
        "last_kills": last_kills,
        "last_outcome": last_outcome,
        "status": status,
        "finisher": finisher,
    }
