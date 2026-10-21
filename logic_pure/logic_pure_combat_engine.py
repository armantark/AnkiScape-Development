"""logic_pure_combat_engine.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional
from .combat_lure import prepare_combat_lure_encounter_pure
from .logic_pure_combat_outcome import _combat_tick_stop_reason, _combat_result_stop_reason
from .logic_pure_combat_setup import _combat_spell_enemy_state

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
    _combat_trim_food_to_capacity,
    _combat_void_shifter_escape_ready,
    combat_dragonfire_protection_pure,
    combat_status_summary_pure,
)

from .logic_pure_combat_food import _combat_preview_food_available  # noqa: F401  (re-export)

from .logic_pure_combat_model import (
    COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM,
    COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
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
    _combat_apply_xp,
    _combat_attack_bonus_from_totals,
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
    _combat_weakening_equipment_state,
    _combat_weapon_is_magic,
    _combat_weapon_is_ranged,
    combat_attack_style_for_equipment_pure,
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
    prayer_drain_and_effective_uptime_pure,
    prayer_effect_state_pure,
)

from .logic_pure_magic import (
    advance_temporary_effects_pure,
    effective_magic_rune_cost_pure,
)

from .logic_pure_equipment import (
    _equipment_bonus_value,
    _equipment_value,
    belt_groups_pure,
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


from .logic_pure_combat_specials import _combat_enemy_poison_application
from .logic_pure_combat_hud import (
    _combat_hud_enemy_bar,
    _combat_hud_last_fight,
    _combat_hud_player_bars,
    _combat_hud_finisher_text,
)
from .logic_pure_combat_risk import (
    _combat_preview_target_context,
    _combat_preview_with_risk,
)
from .logic_pure_combat_outcome import (
    _combat_advance_status_tick,
    _combat_bank_burst_rewards,
    _combat_settle_burst_outcome,
    _combat_settle_wilderness_ambush,
)
from .logic_pure_combat_curses import _combat_curse_drains, _combat_turmoil_boosts
from .logic_pure_combat_loadout import _combat_prepare_target_loadout, _combat_target_loadout
from .logic_pure_combat_setup import (
    _combat_enemy_start_lifepoints,
    _combat_prayer_request,
    _combat_prayer_tick,
    _combat_resume_attack_clocks,
    _combat_start_prayer,
    _combat_switch_off_spent_prayers,
)
from .logic_pure_combat_live import (
    _combat_live_enemy_accuracy,
    _combat_live_player_rolls,
)
from .logic_pure_combat_enemy_turn import (
    _combat_apply_redemption,
    _combat_enemy_breathes_dragonfire,
    _combat_enemy_damage_after_prayers,
    _combat_enemy_regeneration,
    _combat_enemy_special_damage,
    _combat_prepare_enemy_attack,
    _combat_rebound_enemy_hit,
    _combat_regenerate_enemy,
)
from .logic_pure_combat_player_turn import (
    _combat_land_player_hit,
    _combat_soul_split_heal,
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


def _combat_roll_hit(accuracy, max_hit_old_hp, rng, blocked=False):
    """Roll whether an attack lands, then its damage. A blocked attack still
    spends its accuracy roll, so blocking never shifts the later draws."""
    try:
        landed = float(rng()) < accuracy
    except (TypeError, ValueError):
        landed = False
    landed = landed and not blocked
    return landed, _combat_roll_damage_lifepoints(max_hit_old_hp, rng) if landed else 0


def combat_target_preview_pure(player_data, target_id, enemy_data=None, equipment_data=None):
    enemy_data, enemy, equipment_data, reasons = _combat_preview_target_context(
        player_data, target_id, enemy_data, equipment_data
    )
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
    weapon_name = ammo_name = None
    if combat_class == "ranged":
        weapon_name, _weapon_equipment, weapon_spec = _combat_ranged_weapon_spec(player_data, equipment_data)
        ammo_name = _combat_selected_ranged_ammo(player_data, weapon_spec, target_id)
    if combat_class == "magic":
        player_attack_roll = _combat_effective_player_magic_level(player_data) * (
            _combat_attack_bonus_from_totals(player_totals, "magic") + 64
        )
        player_max_hit = _combat_magic_max_hit_old_hp(
            spell_spec,
            player_totals,
            player_data,
            spell_id,
        )
    else:
        # Combat drinks loaded potions, then rolls with this target's prayer
        # setup drained across one ordinary review burst, so the preview
        # projects that same hit. Magic keeps its own projection above until
        # the owner's Magic decision.
        loadout = _combat_target_loadout(player_data, target_id)
        _combat_auto_drink_potions(loadout, combat_class)
        selected_prayers, halo_drain_multipliers, requested_uptime = _combat_prayer_request(loadout, False)
        _points, _counter, prayer_uptime = prayer_drain_and_effective_uptime_pure(
            _non_negative_int(loadout.get("combat_prayer_points", 0), 0),
            loadout.get("combat_prayer_drain_counter", 0.0),
            selected_prayers,
            _equipment_bonus_value(player_totals, "prayer"),
            COMBAT_BURST_TICKS,
            requested_uptime,
            halo_drain_multipliers,
        )
        player_attack_roll, player_max_hit = _combat_player_attack_rolls(
            loadout, combat_class, style_id, melee_style_type, player_totals,
            prayer_effect_state_pure(loadout, prayer_uptime), ammo_name, spell_spec, spell_id,
        )
    enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * (
        _combat_defence_bonus_from_totals(enemy_totals, combat_class, style_type=melee_style_type) + 64
    )
    accuracy = _combat_accuracy(player_attack_roll, enemy_defence_roll)
    if enemy.get("warriors_guild_gate"):
        player_max_hit *= warriors_guild_cyclops_damage_multiplier_pure(
            player_data
        )
    return _combat_preview_with_risk(
        player_data,
        target_id,
        enemy,
        enemy_data,
        enemy_totals,
        combat_class,
        accuracy,
        {
            "player_max_hit": int(player_max_hit * 10),
            "ammo": ammo_name or "",
            "spell_id": spell_id if combat_class == "magic" else "",
            "spell": spell_spec.get("display_name", "") if combat_class == "magic" and isinstance(spell_spec, Mapping) else "",
            "runes": dict(spell_spec.get("rune_cost", {}) or {}) if combat_class == "magic" and isinstance(spell_spec, Mapping) else {},
            "weapon": weapon_name or "",
        },
    )


def combat_enemy_pressure_attack_pure(
    player_data, enemy, equipment_data=None, rng=None, *,
    automatic_protection_prayer=None,
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
    prayer_effects = prayer_effect_state_pure(data, automatic_protection_prayer=automatic_protection_prayer)
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
    equipment_data = equipment_data or {}
    if isinstance(encounter_enemy, Mapping) and encounter_enemy.get(
        "wilderness_risk"
    ):
        data["combat_encounter"] = {}
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
        bank_run_result["stop_reason"] = "bank_trip"
        data["combat_last_result"] = bank_run_result
        return data
    # A stale loadout must not deliver an instant restock: the repair stays
    # behind the bank-run gate so any refill rides the normal cadence.
    data = repair_combat_supply_loadout_class_pure(data, equipment_data)
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


def _combat_settle_kill_rewards(data, enemy, target_id, rng, drops, xp_rewards):
    rolled_drops, refused_clue = _combat_roll_drops(
        enemy,
        rng,
        _combat_drop_ownership_view(data, drops),
        include_clue_refusal=True,
    )
    kill_drops = _combat_apply_triple_charm_reward(data, rolled_drops)
    _record_combat_observed_drops_pure(data, target_id, kill_drops)
    data, kill_drops, passive_prayer_xp, prayer_ticks, _prayer_effects = resolve_prayer_kill_effects_pure(
        data,
        target_id,
        kill_drops,
        bool(data.get("combat_auto_prayer_training")),
    )
    if passive_prayer_xp > 0:
        xp_rewards["prayer_exp"] = float(xp_rewards.get("prayer_exp", 0.0) or 0.0) + passive_prayer_xp
    for drop_name, drop_amount in kill_drops.items():
        drops[drop_name] = _non_negative_int(drops.get(drop_name, 0), 0) + _non_negative_int(drop_amount, 0)
    return data, refused_clue, prayer_ticks


def _combat_enemy_attack_rolls(
    data,
    enemy,
    combat_class,
    style_id,
    player_totals,
    enemy_totals,
    prayer_effects,
    enemy_attack_factor,
    weakening_equipment,
    weakening_active,
):
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
    return enemy_attack_roll, player_defence_roll, enemy_accuracy, enemy_max_hit


def _combat_player_attack_rolls(
    data, combat_class, style_id, melee_style_type, player_totals,
    prayer_effects, selected_ammo, spell_spec, spell_id,
):
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
    return player_attack_roll, player_max_hit


def _combat_apply_enemy_unequip_special(data, target_id):
    before_equipment = dict(data.get("equipment", {}) or {})
    slot_order = ("weapon",) + tuple(sorted(slot for slot in before_equipment if slot != "weapon"))
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
    return data, {"kind": "unequip", "item": removed_item, "slot": removed_slot}


def _combat_kill_stop_reason(data, live_cadence, kills, limit, allow_bank_run, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data):
    if not live_cadence:
        return ""
    if limit is not None and kills >= limit:
        return "slayer_task_complete"
    if allow_bank_run and _combat_bank_run_needed(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data):
        return "bank_trip"
    return ""


def apply_combat_burst_pure(
    player_data,
    enemy_data=None,
    equipment_data=None,
    ticks=None,
    rng=None,
    *,
    live_cadence=False,
    stop_after_first_kill=False,
    stop_after_kills=None,
    stop_on_danger=False,
    safe_death=False,
    no_grave=False,
    allow_bank_run=True,
    player_damage_multiplier=1.0,
    automatic_protection_prayer=None,
):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    equipment_data = equipment_data or {}
    rng = rng or (lambda: 0.0)
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data, enemy_data))
    target_id = data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    data = _combat_prepare_target_loadout(data, target_id)
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

    encounter, active_encounter, stop_after_first_kill = prepare_combat_lure_encounter_pure(data, enemy, target_id, stop_after_first_kill)
    magic_supplements_enabled = combat_class == "magic"
    spellbook_swap_paid = bool(
        magic_supplements_enabled
        and active_encounter
        and encounter.get("spellbook_swap_paid", False)
    )
    vengeance_pending = bool(
        magic_supplements_enabled
        and active_encounter
        and encounter.get("vengeance_pending", False)
    )
    vengeance_cast_paid = bool(
        magic_supplements_enabled
        and active_encounter
        and encounter.get("vengeance_cast_paid", False)
    )
    supplemental_used = {}
    supplemental_magic_xp = 0.0
    pending_supplemental = (
        _combat_pending_supplemental_magic_costs_pure(data, equipment_data)
        if magic_supplements_enabled
        else ()
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
    enemy_max_lp, enemy_lp, retaliation_stop_lifepoints, retaliation_stopped = (
        _combat_enemy_start_lifepoints(enemy, encounter, active_encounter)
    )
    enemy_regen_numerator, enemy_regen_denominator, enemy_regen_residual = (
        _combat_enemy_regeneration(enemy, encounter, active_encounter)
    )

    player_totals = equipment_stat_totals_pure(data.get("equipment", {}) or {}, equipment_data)
    enemy_totals = _combat_enemy_bonuses(enemy)
    player_attack_speed = max(1, _positive_int(_equipment_value(weapon_spec, "attack_speed", 4), 4))
    if combat_class == "ranged":
        player_attack_speed = max(1, player_attack_speed + _signed_int(style.get("attack_speed_delta", 0), 0))
    elif combat_class == "magic":
        player_attack_speed = max(1, _positive_int(spell_spec.get("attack_speed", 5), 5))
    enemy_attack_speed = max(1, _positive_int(enemy.get("attack_speed", 4), 4))
    selected_prayers, halo_drain_multipliers, requested_prayer_uptime = (
        _combat_prayer_request(data, live_cadence, automatic_protection_prayer)
    )
    prayer_bonus = _equipment_bonus_value(player_totals, "prayer")
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
    (
        prayer_points_before,
        prayer_points_after,
        prayer_counter,
        prayer_uptime,
        prayer_effects,
    ) = _combat_start_prayer(
        data, selected_prayers, prayer_bonus, total_ticks,
        requested_prayer_uptime, halo_drain_multipliers, live_cadence, automatic_protection_prayer,
    )

    spell_effect = str(spell_spec.get("effect", "")) if combat_class == "magic" else ""
    spell_effect_value = float(spell_spec.get("effect_value", 0.0) or 0.0) if combat_class == "magic" else 0.0
    magic_effects_applied, magic_effect_applied, enemy_attack_factor, enemy_defence_factor = (
        _combat_spell_enemy_state(encounter, live_cadence and active_encounter, live_cadence, spell_effect, spell_effect_value)
    )
    spell_enemy_attack_factor = enemy_attack_factor
    spell_enemy_defence_factor = enemy_defence_factor
    # Curse ramps are reset for each fight. The burst EV uses the attacks a
    # single full-health enemy is expected to survive, bounded by this review.
    expected_attacks = (
        0
        if live_cadence
        else max(1, int(max(1, _positive_int(ticks, COMBAT_BURST_TICKS)) / player_attack_speed))
    )
    enemy_attack_factor, enemy_defence_factor = _combat_curse_drains(
        selected_prayers, expected_attacks, prayer_uptime, prayer_effects,
        enemy_attack_factor, enemy_defence_factor,
    )
    if "turmoil" in selected_prayers:
        _combat_turmoil_boosts(data, enemy, prayer_uptime, prayer_effects)

    selected_ammo = (
        _combat_selected_ranged_ammo(data, ranged_weapon_spec, target_id)
        if combat_class == "ranged"
        else None
    )
    enemy_defence_roll = (_positive_int(enemy.get("stats", {}).get("defence", 1), 1) + 8) * enemy_defence_factor * (
        _combat_defence_bonus_from_totals(enemy_totals, combat_class, style_type=melee_style_type) + 64
    )
    player_attack_roll, player_max_hit = _combat_player_attack_rolls(
        data, combat_class, style_id, melee_style_type, player_totals,
        prayer_effects, selected_ammo, spell_spec, spell_id,
    )
    if enemy.get("warriors_guild_gate"):
        player_max_hit *= warriors_guild_cyclops_damage_multiplier_pure(data)
    player_accuracy = _combat_accuracy(player_attack_roll, enemy_defence_roll)

    weakening_equipment, weakening_active = _combat_weakening_equipment_state(
        data, enemy
    )
    enemy_attack_roll, player_defence_roll, enemy_accuracy, enemy_max_hit = (
        _combat_enemy_attack_rolls(
            data, enemy, combat_class, style_id, player_totals, enemy_totals,
            prayer_effects, enemy_attack_factor, weakening_equipment,
            weakening_active,
        )
    )
    protective_equipment, protection_active = _combat_protective_equipment_state(
        data, enemy, combat_class
    )
    start_equipment_active = _combat_start_equipment_state(data, enemy)[1]
    unprotected_effect = (
        protective_equipment.get("unprotected_effect")
        if isinstance(protective_equipment, Mapping)
        and not protection_active
        and not protective_equipment.get("attack_kind")
        else None
    )

    next_player_attack, next_enemy_attack, curse_attack_count = (
        _combat_resume_attack_clocks(
            encounter, live_cadence and active_encounter, enemy_attack_speed
        )
    )

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
    stat_drains = {}
    enemy_specials = []
    automatic_finishers = 0
    enemy_counts = {
        "enemy_healing": 0,
        "vampyre_bites": 0,
        "vampyre_bite_healing": 0,
        "dragonfire_attacks": 0,
        "dragonfire_damage": 0,
        "enemy_prayer_drain": 0,
        "unprotected_attacks": 0,
    }
    melee_recoil_damage = 0
    dragonfire_effect_tick = 0
    xp_rewards = {"magic_exp": supplemental_magic_xp} if supplemental_magic_xp > 0 else {}
    drops = {}
    clue_refusal_reason = ""
    kills = 0
    stop_on_kill = live_cadence or stop_after_first_kill or not start_equipment_active
    died = False
    fled = False
    familiar_escape = False
    out_of_ammo = False
    out_of_runes = False
    npc_xp_multiplier = _combat_npc_xp_multiplier(enemy)
    ticks_elapsed = 0
    stop_reason = ""
    # This is a live combat review, so the out-of-combat rest window restarts from
    # zero; the next non-combat review begins healing you back toward full.
    data["combat_rest_reviews"] = 0

    for tick in range(total_ticks):
        ticks_elapsed = tick + 1
        poison_before = bool((data.get("combat_status_effects") or {}).get("poison"))
        enemy_lp, enemy_regen_residual = _combat_regenerate_enemy(
            enemy_lp, enemy_max_lp, enemy_regen_residual,
            enemy_regen_numerator, enemy_regen_denominator, enemy_counts,
        )
        prayer_points_after, prayer_counter, tick_prayer_uptime, prayer_scale = (
            _combat_prayer_tick(
                data, live_cadence, prayer_points_after, prayer_counter,
                prayer_uptime, selected_prayers, prayer_bonus,
                requested_prayer_uptime, halo_drain_multipliers,
            )
        )
        player_lp, status_stop = _combat_advance_status_tick(
            data, player_lp, max_player_lp, rng,
            potions_used, food_used, status_damage, status_expired,
        )
        if status_stop == "died":
            died = True
            break
        if status_stop:
            fled = True
            familiar_escape = status_stop == "void_shifter"
            break
        stop_reason = _combat_tick_stop_reason(data, live_cadence and stop_on_danger, player_lp, max_player_lp, prayer_points_after, selected_prayers, poison_before)
        if stop_reason:
            fled = stop_reason == "fled"
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
            live_player_accuracy, live_player_max_hit = (
                _combat_live_player_rolls(
                    combat_class, player_attack_roll, player_max_hit,
                    enemy_defence_roll, enemy_defence_factor,
                    spell_enemy_defence_factor, prayer_effects, prayer_uptime,
                    tick_prayer_uptime, selected_prayers, curse_attack_count,
                )
                if live_cadence
                else (player_accuracy, player_max_hit)
            )
            landed, damage = _combat_roll_hit(
                live_player_accuracy, live_player_max_hit, rng,
                blocked=enemy.get("protect_from_player_class") == combat_class,
            )
            player_hits_landed += landed
            if live_cadence:
                curse_attack_count += 1
            damage, automatic_finisher, recoil = _combat_land_player_hit(
                data, enemy, finisher, combat_class, damage,
                player_damage_multiplier, enemy_lp, player_lp,
            )
            automatic_finishers += automatic_finisher
            if damage > 0:
                enemy_lp -= damage
                player_damage += damage
                player_lp -= recoil
                melee_recoil_damage += recoil
                if recoil > 0 and player_lp <= 0:
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
                player_lp = _combat_soul_split_heal(
                    player_lp, max_player_lp, damage, prayer_effects,
                    prayer_uptime, tick_prayer_uptime,
                )
            if combat_class == "magic":
                _combat_apply_magic_xp(xp_rewards, spell_spec, damage, npc_xp_multiplier)
            elif damage > 0:
                _combat_apply_xp(xp_rewards, melee_xp_style_id, damage, npc_xp_multiplier)
            if died and enemy_lp > 0:
                break
            if enemy_lp <= 0:
                kills += 1
                data, refused_clue, prayer_ticks = _combat_settle_kill_rewards(
                    data, enemy, target_id, rng, drops, xp_rewards
                )
                clue_refusal_reason = clue_refusal_reason or refused_clue
                next_player_attack += prayer_ticks
                # Chain into the next spawn of the same target for the remaining
                # tick budget instead of ending the burst on the first kill (the
                # old `break` wasted up to half of a ~30s review window). A fresh
                # enemy respawns at full LP and re-engages after its normal attack
                # delay, so it gets no free instant hit on the kill tick.
                stop_reason = _combat_kill_stop_reason(
                    data, live_cadence and stop_on_danger, kills, stop_after_kills, allow_bank_run,
                    target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data,
                )
                if stop_reason or stop_on_kill:
                    break
                enemy_lp, enemy_regen_residual, retaliation_stopped = enemy_max_lp, 0, False
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
            attack_kind, attack_enemy, player_delay = _combat_prepare_enemy_attack(
                enemy, attack_spec, enemy_specials
            )
            next_player_attack += player_delay
            if attack_kind == "unequip":
                data, unequip_event = _combat_apply_enemy_unequip_special(
                    data, target_id
                )
                enemy_specials.append(unequip_event)
            if attack_enemy is None:
                break
            enemy_attack_roll, player_defence_roll, enemy_accuracy, enemy_max_hit = (
                _combat_enemy_attack_rolls(
                    data, attack_enemy, combat_class, style_id, player_totals, enemy_totals,
                    prayer_effects, enemy_attack_factor, weakening_equipment,
                    weakening_active,
                )
            )
            dragonfire_attack = _combat_enemy_breathes_dragonfire(
                data, enemy, tick - dragonfire_effect_tick, rng, potions_used
            )
            dragonfire_effect_tick = tick
            damage, ignores_protection, player_delay, attack_drained = _combat_enemy_special_damage(
                data, enemy, attack_kind, dragonfire_attack, protective_equipment,
                protection_active, unprotected_effect, prayer_effects,
                tick_prayer_uptime, max_player_lp, rng, enemy_counts,
                enemy_specials, stat_drains,
            )
            next_player_attack += player_delay
            if attack_drained:
                player_attack_roll, player_max_hit = _combat_player_attack_rolls(
                    data, combat_class, style_id, melee_style_type, player_totals,
                    prayer_effects, selected_ammo, spell_spec, spell_id,
                )
                player_accuracy = _combat_accuracy(player_attack_roll, enemy_defence_roll)
            if damage is None:
                live_enemy_accuracy = (
                    _combat_live_enemy_accuracy(
                        enemy_attack_roll, player_defence_roll,
                        enemy_attack_factor, spell_enemy_attack_factor,
                        prayer_effects, prayer_uptime, tick_prayer_uptime,
                        selected_prayers, curse_attack_count,
                    )
                    if live_cadence
                    else enemy_accuracy
                )
                _landed, damage = _combat_roll_hit(live_enemy_accuracy, enemy_max_hit, rng)
            raw_enemy_damage = damage
            damage, prayer_points_after = _combat_enemy_damage_after_prayers(
                data, enemy, attack_enemy, combat_class, raw_enemy_damage,
                ignores_protection, unprotected_effect, prayer_effects, prayer_scale, player_lp,
                max_player_lp, prayer_points_after, rng, enemy_counts,
            )
            if dragonfire_attack:
                enemy_counts["dragonfire_damage"] += damage
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
                enemy_lp, reflected, automatic_finisher = _combat_rebound_enemy_hit(
                    data, enemy, finisher, raw_enemy_damage, damage,
                    prayer_effects, prayer_scale, enemy_lp, enemy_max_lp, rng,
                    enemy_counts, stat_drains,
                )
                automatic_finishers += automatic_finisher
                player_damage += reflected
            player_lp, prayer_points_after, prayer_counter = _combat_apply_redemption(
                data, player_lp, max_player_lp, prayer_effects,
                tick_prayer_uptime, prayer_points_after, prayer_counter,
            )
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
                data, refused_clue, prayer_ticks = _combat_settle_kill_rewards(
                    data, enemy, target_id, rng, drops, xp_rewards
                )
                clue_refusal_reason = clue_refusal_reason or refused_clue
                next_player_attack += prayer_ticks
                stop_reason = _combat_kill_stop_reason(
                    data, live_cadence and stop_on_danger, kills, stop_after_kills, allow_bank_run,
                    target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data,
                )
                if stop_reason or stop_on_kill:
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
            potion_event = _combat_enemy_poison_application(
                data, poison_damage, rng, status_applied
            )
            if potion_event:
                potions_used.append(potion_event)
        stop_reason = _combat_tick_stop_reason(data, live_cadence and stop_on_danger, player_lp, max_player_lp, prayer_points_after, selected_prayers, poison_before)
        if stop_reason:
            fled = stop_reason == "fled"
            break

    data, equipment_condition_events = _combat_bank_burst_rewards(
        data, ticks_elapsed, drops, xp_rewards
    )
    player_lp, death_burst, carry_encounter = _combat_settle_burst_outcome(
        data, target_id, kills, died, fled, player_lp, max_player_lp,
        enemy_lp, enemy_max_lp, selected_prayers, finisher, rng,
        live_cadence=live_cadence, safe_death=safe_death, no_grave=no_grave, enemy=enemy,
    )
    enemy_lp -= death_burst
    player_damage += death_burst
    if carry_encounter:
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
        if magic_supplements_enabled and (
            bool(data.get("combat_vengeance", False)) or vengeance_pending
        ):
            next_encounter["vengeance_pending"] = bool(vengeance_pending)
        if live_cadence and vengeance_cast_paid:
            next_encounter["vengeance_cast_paid"] = True
        data["combat_encounter"] = next_encounter

    if live_cadence:
        _combat_switch_off_spent_prayers(data, prayer_points_after, selected_prayers)

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
        wilderness_ambush, player_lp, died = _combat_settle_wilderness_ambush(
            data, enemy, player_lp, max_player_lp, rng,
            wilderness_equipment_risk, food_used,
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
        "enemy_healing": enemy_counts["enemy_healing"],
        "vampyre_bites": enemy_counts["vampyre_bites"],
        "vampyre_bite_healing": enemy_counts["vampyre_bite_healing"],
        "dragonfire_attacks": enemy_counts["dragonfire_attacks"],
        "dragonfire_damage": enemy_counts["dragonfire_damage"],
        "melee_recoil_damage": melee_recoil_damage,
        "enemy_prayer_drain": enemy_counts["enemy_prayer_drain"],
        "safe_death": bool(died and safe_death),
        "dragonfire_protection": combat_dragonfire_protection_pure(
            data, enemy
        ),
        "enemy_retaliation_stopped": retaliation_stopped,
        "enemy_lifepoints": enemy_lp,
        "player_lifepoints": player_lp,
        "killed": kills > 0,
        "kills": kills,
        "died": died,
        "fled": fled,
        "familiar_escape": familiar_escape,
        "wilderness_ambush": wilderness_ambush or {},
        "stop_reason": _combat_result_stop_reason(stop_reason, died, fled, familiar_escape, out_of_ammo, out_of_runes, live_cadence),
        "food_used": tuple(food_used),
        "potions_used": tuple(potions_used),
        "ammo_used": dict(ammo_used),
        "runes_used": dict(runes_used),
        "status_damage": dict(status_damage),
        "status_applied": dict(status_applied),
        "status_expired": tuple(dict.fromkeys(status_expired)),
        "unprotected_attacks": enemy_counts["unprotected_attacks"],
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
        "death_prayer_damage": death_burst,
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
    """Read-only Bank summary of the tool belt.

    Buying or looting a better gathering tool leaves it in the Bank. The active
    row changes only after the player uses the Bank's attach action. Attached
    tools above the player's level remain visible in ``toolbelt_blocked`` while
    the best usable attached tool stays active. Every other 2012 belt tool is
    listed by its belt group with its belt and Add-to-toolbelt state.

    Returns {"toolbelt": [(label, display_name), ...],
             "toolbelt_blocked": [(label, display_name, skill_label, level), ...],
             "belt_groups": ((group, ((tool_name, on_belt, add_refusal), ...)), ...)}.
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

    return {
        "toolbelt": toolbelt_rows,
        "toolbelt_blocked": blocked_rows,
        "belt_groups": belt_groups_pure(player_data),
    }


def _combat_supply_loadout_class_compatible_pure(player_data, equipment_data=None):
    loadout = _sanitize_combat_supply_loadout(
        player_data.get("combat_supply_loadout")
    )
    style = COMBAT_ATTACK_STYLE_DATA.get(
        combat_attack_style_for_equipment_pure(player_data, equipment_data or {}),
        COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE],
    )
    combat_class = str(style.get("combat_class", "melee"))
    relevant_stat_potions = set(_combat_relevant_potion_items(combat_class))
    return (
        (combat_class == "ranged" or not loadout.get("ammo"))
        and (combat_class == "magic" or not loadout.get("runes"))
        and all(
            item_name in relevant_stat_potions
            for item_name in (loadout.get("stat_potions", {}) or {})
        )
    )


def repair_combat_supply_loadout_class_pure(player_data, equipment_data=None):
    if _combat_supply_loadout_class_compatible_pure(player_data, equipment_data):
        return player_data
    repaired, _ok, _reason = reconcile_combat_method_pure(
        player_data, {}, equipment_data
    )
    return repaired


def combat_supply_loadout_summary_pure(player_data, equipment_data=None):
    loadout = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    style = COMBAT_ATTACK_STYLE_DATA.get(
        combat_attack_style_for_equipment_pure(player_data, equipment_data or {}),
        COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE],
    )
    combat_class = str(style.get("combat_class", "melee"))
    relevant_stat_potions = set(_combat_relevant_potion_items(combat_class))
    # _sanitize_combat_supply_loadout guarantees every section exists with
    # positive-int quantities, so the summary only projects and class-gates.
    stat_potions = {
        item_name: amount
        for item_name, amount in loadout["stat_potions"].items()
        if item_name in relevant_stat_potions
    }
    return {
        "food_loaded_items": dict(loadout["food"]),
        "potions_loaded": sum(loadout["potions"].values()),
        "potions_loaded_items": dict(loadout["potions"]),
        "stat_potions_loaded": sum(stat_potions.values()),
        "stat_potions_loaded_items": stat_potions,
        "ammo_loaded": dict(loadout["ammo"]) if combat_class == "ranged" else {},
        "runes_loaded": dict(loadout["runes"]) if combat_class == "magic" else {},
        "finishers_loaded": dict(loadout["finishers"]),
        "hazards_loaded": dict(loadout["hazards"]),
        "cannonballs_loaded": loadout["cannonballs"],
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
    data["combat_encounter"] = {}
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
    data.update(updates)
    data, _ok, _reason = unload_combat_supply_loadout_pure(data)
    return refill_combat_supply_loadout_pure(data, equipment_data)


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
    player_bars = _combat_hud_player_bars(player_data)
    target_id = player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    enemy_bar = _combat_hud_enemy_bar(player_data, target_id, enemy_data)

    style_id = combat_attack_style_for_equipment_pure(player_data, equipment_data)
    style = COMBAT_ATTACK_STYLE_DATA.get(style_id, {})
    # xp_style_id captures the two-handed-sword aggressive/crush/SHARED anomaly so
    # the XP chips name the skills actually trained, not what weapon_style implies.
    _melee_style_type, xp_style_id = combat_melee_attack_type_pure(player_data, equipment_data)

    last_fight = _combat_hud_last_fight(player_data, target_id)
    finisher = combat_finisher_state_pure(player_data, target_id, enemy_data)
    return {
        "combat_level": player_combat_level_pure(player_data),
        **player_bars,
        **enemy_bar,
        "attack_style_id": style_id,
        "attack_style_name": str(style.get("display_name", style_id)),
        "trained_skills": combat_attack_style_trained_skills_pure(xp_style_id),
        **last_fight,
        "status": combat_status_summary_pure(player_data),
        **_combat_hud_finisher_text(finisher),
        "finisher": finisher,
    }
