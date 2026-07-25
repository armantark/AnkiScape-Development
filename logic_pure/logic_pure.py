# logic_pure.py - Pure logic functions for AnkiScape (no Anki dependencies)
#
# The definitions now live in the ``logic_pure_*`` modules, one per domain, and
# this file re-exports every one of them so existing callers keep importing from
# ``logic_pure``. The modules import strictly left-to-right along the dependency
# order recorded below, which is what keeps the graph acyclic:
#
#   state -> progression/telemetry/landmarks -> equipment/magic/construction/urns
#         -> prayer -> combat_model -> combat_supplies -> combat_engine
#         -> quest/consumables/claims -> gathering/production/runecrafting/smithing/thieving
#
# A test that patches a name must patch it on the module that DEFINES it. A
# caller resolves the name from its own module globals, so rebinding the
# re-exported attribute here is silently a no-op.
from __future__ import annotations

from math import comb, floor, sqrt
from typing import Iterable, Mapping, Optional

from ..data.equipment_data import EQUIPMENT_BONUS_FIELDS, EquipmentBonuses

from ..logic.equipment_instance_logic import (
    advance_equipped_condition_pure,
    discharge_equipped_on_unsafe_death_pure,
    sanitize_equipment_instance_state_pure,
)
from ..data.equipment_condition_data import EQUIPMENT_CONDITION_DATA

from ..logic.inventory_pure import CARRIED_CAPACITY, apply_carried_layout_pure, carried_slots_used, clamp_carried_view_to_bank

from ..logic.wicked_hood_logic import (
    apply_wicked_hood_upgrade_pure,
    wicked_hood_fed_altars_pure,
    wicked_hood_operable_pure,
)

from ..logic.court_cases_logic import filter_court_summons_outputs_pure

try:
    from ..data.item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES
except ImportError:  # values not generated in this checkout
    ITEM_VALUES = {}
    STACKABLE_ITEM_NAMES = frozenset()

from ..core.skill_registry import get_skill, trainable_skill_definitions

from ..data.mining_data import MINING_REVIEW_DAY_CARDS, RED_SANDSTONE_DAILY_CAP

from ..logic.warriors_guild_logic import (
    warriors_guild_cyclops_damage_multiplier_pure,
    warriors_guild_cyclops_locked_reasons_pure,
)

from ..data.potion_data import POTION_FAMILIES, potion_dose_name, potion_flask_name

from ..data.pack_data import ITEM_PACK_DATA

from ..data.prayer_data import (
    COMBAT_PRAYERS_BY_ID,
    AUTO_PRAYER_TICKS_PER_ITEM,
    PRAYER_MATERIALS,
    PRAYER_UPTIME_POLICIES,
    SAP_SOURCE,
    LEECH_SOURCE,
    resolve_prayer_selection_pure,
)

from ..data.prayer_passive_data import (
    BONECRUSHER_ITEM_NAME,
    ECTOPLASMATOR_ITEM_NAME,
    ECTOPLASMATOR_XP_BY_ENEMY_ID,
)
from ..data.urn_data import (
    MAX_NONEMPTY_URNS_PER_SKILL,
    URN_CARRIED_TARGET_KEYS,
    URN_TIERS_BY_FULL_ITEM,
    URN_TIERS_BY_ID,
    URN_TIERS_BY_SKILL,
    materialize_urn_layout_pure,
    sanitize_urn_state_pure,
    urn_action_event_pure,
    urn_tier_accepts_event_pure,
)

from ..data.magic_data import CASUAL_MAGIC_DIAL, DREAM_COST, SPELLBOOK_SWAP_COST, VENGEANCE_COST

from ..data.livid_farm_data import BORROWED_POWER_COMBAT_SPELLS

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

# --- split re-exports (additive; see the module docstrings) ---
from ..logic_pure.logic_pure_thieving import (  # noqa: F401  (re-export)
    _consume_carried_auto_food_pure,
    apply_thieving_damage_pure,
    thieving_blackjack_threshold_pure,
    thieving_loot_roll_pure,
    thieving_multi_pick_count_pure,
    thieving_roll_succeeds_pure,
    thieving_roll_threshold_pure,
    thieving_stall_cadence_profile_pure,
    thieving_success_probability_pure,
    thieving_target_locked_reasons_pure,
    thieving_wall_safe_roll_succeeds_pure,
    thieving_wall_safe_success_count_pure,
)

from ..logic_pure.logic_pure_smithing import (  # noqa: F401  (re-export)
    RING_OF_FORGING_ITEM,
    RING_OF_FORGING_MAX_CHARGES,
    _equipment_has_ring_of_forging_pure,
    apply_smelt_pure,
    apply_smithing_action_pure,
    apply_smithing_pure,
    calculate_iron_smelting_success_probability_pure,
    can_smelt_any_bar_pure,
    can_smith_any_pure,
    can_smith_item_pure,
    consume_ring_of_forging_charge_pure,
    create_soft_clay_pure,
    has_ring_of_forging_pure,
    has_smithing_materials_pure,
    ring_of_forging_charges_pure,
    smithing_success_probability_pure,
    smithing_target_locked_reasons_pure,
)

from ..logic_pure.logic_pure_runecrafting import (  # noqa: F401  (re-export)
    _altar_access_item_names,
    _altar_for_target,
    _available_essence_count,
    _consume_essence_ordered,
    _degrade_used_pouches,
    _fed_altars,
    _pouch_capacity_after_degradation,
    _repair_degraded_pouches,
    _runecrafting_multiplier_info,
    _standard_output_count,
    apply_runecrafting_action_pure,
    binding_necklace_charges_pure,
    can_runecraft_any_pure,
    can_runecraft_target_pure,
    runecrafting_altar_access_source_pure,
    runecrafting_locked_reasons_pure,
    runecrafting_pouch_capacity_pure,
    runecrafting_standard_base_capacity_pure,
    runecrafting_unlocked_pure,
)

from ..logic_pure.logic_pure_production import (  # noqa: F401  (re-export)
    _max_batches_for_requirements,
    _utility_outputs_from_spec,
    apply_cooking_action_pure,
    apply_crafting_pure,
    apply_firemaking_action_pure,
    apply_fletching_pure,
    apply_herblore_action_pure,
    apply_utility_activity_pure,
    calculate_cooking_success_probability_pure,
    calculate_firemaking_success_probability_pure,
    can_burn_any_firemaking_target_pure,
    can_burn_firemaking_target_pure,
    can_burn_firemaking_target_with_unlocks_pure,
    can_cook_target_pure,
    can_craft_item_pure,
    can_fletch_item_pure,
    can_herblore_target_pure,
    can_perform_utility_activity_pure,
    cheese_wheel_slice_probability_pure,
    cheese_wheel_slice_yield_pure,
    cooking_source_roll_chance_pure,
    cooking_target_locked_reasons_pure,
    crafting_target_locked_reasons_pure,
    firemaking_source_roll_chance_pure,
    firemaking_target_locked_reasons_pure,
    fletching_material_requirements_pure,
    fletching_target_locked_reasons_pure,
    has_cooking_materials_pure,
    has_crafting_materials_pure,
    has_firemaking_materials_pure,
    has_fletching_materials_pure,
    has_herblore_materials_pure,
    herblore_target_locked_reasons_pure,
    utility_activity_locked_reasons_pure,
)

from ..logic_pure.logic_pure_gathering import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_consumables import (  # noqa: F401  (re-export)
    _consumable_heal,
    apply_consumable_pure,
    apply_item_pack_open_pure,
)

from ..logic_pure.logic_pure_claims import (  # noqa: F401  (re-export)
    _claim_bundle_items,
    _skill_level_for_reward,
    apply_claim_pure,
    claim_locked_reasons_pure,
    claim_rows_pure,
)

from ..logic_pure.logic_pure_quest import (  # noqa: F401  (re-export)
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
    _mark_quest_stage_actions,
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

from ..logic_pure.logic_pure_combat_engine import (  # noqa: F401  (re-export)
    _COMBAT_EXP_KEY_DISPLAY,
    _COMBAT_STYLE_XP_KEYS,
    _combat_roll_damage_lifepoints,
    apply_combat_burst_pure,
    apply_safe_combat_recovery_pure,
    bank_gear_rows_pure,
    combat_attack_style_trained_skills_pure,
    combat_death_office_items_pure,
    combat_death_office_reclaim_cost_pure,
    combat_death_office_summary_pure,
    combat_enemy_pressure_attack_pure,
    combat_has_active_encounter_pure,
    combat_hud_state_pure,
    combat_supply_loadout_summary_pure,
    combat_target_preview_pure,
    combat_weapon_style_options_pure,
    player_combat_level_pure,
    reclaim_death_office_items_pure,
    refill_combat_supply_loadout_pure,
    set_combat_auto_eat_food_pure,
    set_combat_auto_eat_threshold_pure,
    set_combat_pack_mode_pure,
    unload_combat_supply_loadout_pure,
)

from ..logic_pure.logic_pure_combat_supplies import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_combat_model import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_urns import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_telemetry import (  # noqa: F401  (re-export)
    action_telemetry_key_pure,
    default_achievement_progress_pure,
    default_action_telemetry_pure,
    record_achievement_progress_pure,
    record_action_telemetry_pure,
    record_cadence_wait_telemetry_pure,
    sanitize_achievement_progress_pure,
    sanitize_action_telemetry_pure,
    summarize_action_telemetry_pure,
)

from ..logic_pure.logic_pure_prayer import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_construction import (  # noqa: F401  (re-export)
    _LECTERN_SLOTS,
    _construction_has_workbench,
    _construction_nail_stock,
    _consume_construction_nails,
    apply_construction_action_pure,
    construction_target_locked_reasons_pure,
    effective_gilded_altar_multiplier_pure,
    owned_gilded_altar_access_reasons_pure,
    owned_gilded_altar_burner_count_pure,
    owned_gilded_altar_effective_burners_pure,
    owned_gilded_altar_marrentill_required_pure,
    purchase_house_option_pure,
    purchase_house_pure,
)

from ..logic_pure.logic_pure_magic import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_progression import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_equipment import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_landmarks import (  # noqa: F401  (re-export)
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
    landmark_hud_progress_pure,
    mage_arena_locked_reasons_pure,
    sanitize_knight_waves_state_pure,
    sanitize_mage_arena_state_pure,
    sanitize_stronghold_state_pure,
    set_mage_arena_alignment_pure,
)

from ..logic_pure.logic_pure_state import (  # noqa: F401  (re-export)
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



















































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































# --- Thieving -------------------------------------------------------------
