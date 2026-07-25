"""runtime_actions_shared.py - split out of runtime_actions.py; see that module's header."""

from __future__ import annotations

import dataclasses

from typing import Any, Callable, Optional

try:
    from .constants import (
        BIRD_NEST_DROP_CHANCE,
        BIRD_NEST_DROP_TABLE,
        BIRD_NEST_OPEN_TABLES,
        COMBAT_BURST_TICKS,
        COMBAT_ENEMY_DATA,
        COMBAT_FOOD_DATA,
        COOKING_DATA,
        CRAFTING_DATA,
        DEFAULT_COMBAT_TARGET,
        DEFAULT_COOKING_TARGET,
        DEFAULT_FIREMAKING_TARGET,
        DEFAULT_FLETCHING_TARGET,
        DEFAULT_FISHING_TARGET,
        DEFAULT_HERBLORE_TARGET,
        DEFAULT_HUNTER_TARGET,
        DEFAULT_MINING_TARGET,
        DEFAULT_RUNECRAFTING_TARGET,
        DEFAULT_UTILITY_ACTIVITY,
        DEFAULT_WOODCUTTING_TARGET,
        EQUIPMENT_DATA,
        EXP_TABLE,
        FIREMAKING_DATA,
        FISHING_DATA,
        HUNTER_DATA,
        FLETCHING_DATA,
        HERBLORE_DATA,
        GLORY_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_TABLE,
        ITEM_DEFINITIONS,
        MINING_BONUS_ITEM_DATA,
        MINING_PICKAXE_DATA,
        MAGIC_DATA,
        DEFAULT_MAGIC_TARGET,
        ORE_DATA,
        PRAYER_DATA,
        DEFAULT_PRAYER_TARGET,
        QUEST_DATA,
        QUEST_UNLOCK_RULES,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        SMITHING_DATA,
        TREE_DATA,
        UTILITY_ACTIVITY_DATA,
        WOODCUTTING_AXE_DATA,
    )
    from .logic_pure import (
        COMBAT_GRAVE_RECOVERY_REVIEWS,
        apply_combat_burst_pure,
        apply_combat_finisher_pure,
        apply_cooking_action_pure,
        apply_crafting_pure,
        apply_firemaking_action_pure,
        apply_fishing_action_pure,
        apply_fletching_pure,
        apply_herblore_action_pure,
        apply_hunter_action_pure,
        apply_quest_combat_encounter_pure,
        apply_mining_action_pure,
        apply_magic_action_pure,
        apply_open_bird_nests_pure,
        apply_prayer_action_pure,
        apply_construction_action_pure,
        construction_target_locked_reasons_pure,
        owned_gilded_altar_burner_count_pure,
        owned_gilded_altar_marrentill_required_pure,
        owned_gilded_altar_access_reasons_pure,
        effective_gilded_altar_multiplier_pure,
        charge_training_urn_for_action_pure,
        intercept_bonecrusher_outputs_pure,
        prayer_gilded_search_step_pure,
        clear_prayer_gilded_stint_pure,
        prayer_target_locked_reasons_pure,
        apply_quest_progress_pure,
        apply_runecrafting_action_pure,
        runecrafting_locked_reasons_pure,
        apply_smithing_action_pure,
        apply_stronghold_step_pure,
        apply_knight_waves_step_pure,
        apply_mage_arena_step_pure,
        attune_mage_arena_spell_pure,
        knight_waves_locked_reasons_pure,
        mage_arena_locked_reasons_pure,
        apply_utility_activity_pure,
        apply_woodcutting_action_pure,
        apply_woodcutting_processing_action_pure,
        best_mining_pickaxe_pure,
        best_woodcutting_axe_pure,
        calculate_cooking_success_probability_pure,
        calculate_firemaking_success_probability_pure,
        calculate_fishing_success_probability_pure,
        fishing_agility_double_catch_chance_pure,
        calculate_hunter_success_probability_pure,
        calculate_mining_success_probability_pure,
        calculate_woodcutting_success_probability_pure,
        cooking_source_roll_chance_pure,
        firemaking_source_roll_chance_pure,
        calculate_new_level,
        can_chop_woodcutting_target_pure,
        can_craft_item_pure,
        can_attempt_quest_review_pure,
        can_progress_quest_pure,
        can_runecraft_target_pure,
        can_smith_item_pure,
        can_start_quest_pure,
        cooking_target_locked_reasons_pure,
        combat_target_locked_reasons_pure,
        eligible_fishing_fish_pure,
        equipment_bonus_state_pure,
        firemaking_target_locked_reasons_pure,
        fishing_method_locked_reasons_pure,
        fletching_material_requirements_pure,
        fletching_target_locked_reasons_pure,
        herblore_target_locked_reasons_pure,
        has_cooking_materials_pure,
        has_crafting_materials_pure,
        has_firemaking_materials_pure,
        has_fishing_bait_pure,
        has_hunter_materials_pure,
        has_ring_of_forging_pure,
        hunter_target_locked_reasons_pure,
        mining_target_locked_reasons_pure,
        red_sandstone_daily_state_pure,
        magic_target_locked_reasons_pure,
        normalize_xp_rewards_pure,
        quest_current_stage_blocker_reasons_pure,
        quest_current_stage_blockers_pure,
        quest_current_stage_resolvable_combat_blockers_pure,
        record_action_telemetry_pure,
        record_cadence_wait_telemetry_pure,
        record_achievement_progress_pure,
        consume_ring_of_forging_charge_pure,
        smithing_success_probability_pure,
        smithing_target_locked_reasons_pure,
        utility_activity_locked_reasons_pure,
        woodcutting_target_locked_reasons_pure,
        thieving_blackjack_threshold_pure,
        apply_thieving_damage_pure,
        thieving_loot_roll_pure,
        thieving_multi_pick_count_pure,
        thieving_roll_succeeds_pure,
        thieving_stall_cadence_profile_pure,
        thieving_success_probability_pure,
        thieving_target_locked_reasons_pure,
        thieving_wall_safe_roll_succeeds_pure,
        STRONGHOLD_STEP_NAMES,
        STRONGHOLD_TOTAL_STEPS,
    )
    from .skill_registry import get_skill
    from .farming_logic import (
        advance_farm_clock_pure,
        apply_farming_review_with_queue_pure,
        consume_next_farm_queue_step_pure,
    )
    from .construction_data import (
        CONSTRUCTION_DATA, DEFAULT_CONSTRUCTION_TARGET, NAIL_DATA, ROOM_DATA,
        SERVANT_DATA, WORKBENCH_TIERS,
    )
    from .shop_data import SHOP_PLAYER_BUY_PRICES
    from .smithing_data import DEFAULT_SMITHING_TARGET
    from .urn_data import URN_STATE_ITEM_NAMES, materialize_urn_layout_pure
    from .thieving_data import DEFAULT_THIEVING_TARGET, THIEVING_TARGETS
    from .agility_data import AGILITY_TARGETS_BY_ID, DEFAULT_AGILITY_TARGET
    from .agility_logic import (
        agility_target_locked_reasons_pure,
        apply_agility_command_pure,
        apply_agility_review_pure,
        sanitize_agility_state_pure,
    )
    from .flash_powder_factory_data import FLASH_POWDER_FACTORY_ACTIVITY_ID
    from .flash_powder_factory_logic import (
        apply_flash_powder_factory_review_pure,
        apply_factory_outfit_herblore_bonus_pure,
        factory_outfit_four_dose_eligible_pure,
        flash_powder_factory_view_pure,
    )
    from .pyramid_plunder_data import PYRAMID_PLUNDER_ACTIVITY_ID
    from .pyramid_plunder_logic import (
        apply_pyramid_plunder_review_pure,
        pyramid_plunder_view_pure,
    )
    from .werewolf_skullball_data import WEREWOLF_SKULLBALL_ACTIVITY_ID
    from .werewolf_skullball_logic import (
        apply_werewolf_skullball_review_pure,
        werewolf_skullball_view_pure,
    )
    from .gnome_ball_data import GNOME_BALL_ACTIVITY_ID
    from .gnome_ball_logic import (
        apply_gnome_ball_review_pure,
        gnome_ball_view_pure,
    )
    from .fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID
    from .fish_flingers_logic import (
        apply_fish_flingers_review_pure,
        fish_flingers_view_pure,
        fishing_outfit_multiplier_pure,
    )
    from .fishing_trawler_data import FISHING_TRAWLER_ACTIVITY_ID
    from .fishing_trawler_logic import (
        apply_fishing_trawler_review_pure,
        fishing_trawler_view_pure,
    )
    from .great_orb_project_data import GREAT_ORB_PROJECT_ACTIVITY_ID
    from .great_orb_project_logic import (
        apply_great_orb_project_review_pure,
        great_orb_project_view_pure,
    )
    from .court_cases_data import COURT_CASES_ACTIVITY_ID
    from .court_cases_logic import (
        apply_court_case_review_pure,
        court_cases_view_pure,
        filter_court_summons_outputs_pure,
    )
    from .circus_data import CIRCUS_ACTIVITY_ID
    from .circus_logic import apply_circus_review_pure, circus_view_pure
    from .trouble_brewing_data import TROUBLE_BREWING_ACTIVITY_ID
    from .trouble_brewing_logic import (
        apply_trouble_brewing_review_pure,
        trouble_brewing_view_pure,
    )
    from .castle_wars_data import CASTLE_WARS_ACTIVITY_ID
    from .castle_wars_logic import (
        apply_castle_wars_review_pure,
        castle_wars_view_pure,
    )
    from .pest_control_data import PEST_CONTROL_ACTIVITY_ID
    from .pest_control_logic import (
        apply_pest_control_review_pure,
        pest_control_view_pure,
    )
    from .barbarian_assault_data import BARBARIAN_ASSAULT_ACTIVITY_ID
    from .barbarian_assault_logic import (
        apply_barbarian_assault_review_pure,
        barbarian_assault_view_pure,
    )
    from .stronghold_player_safety_data import STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID
    from .stronghold_player_safety_logic import (
        apply_stronghold_player_safety_review_pure,
        stronghold_player_safety_view_pure,
    )
    from .soul_wars_data import SOUL_WARS_ACTIVITY_ID
    from .soul_wars_logic import (
        apply_soul_wars_review_pure,
        soul_wars_view_pure,
    )
    from .shades_of_mortton_data import SHADES_OF_MORTTON_ACTIVITY_ID
    from .shades_of_mortton_logic import (
        apply_shades_of_mortton_review_pure,
        shades_of_mortton_view_pure,
    )
    from .tzhaar_fight_pit_data import TZHAAR_FIGHT_PIT_ACTIVITY_ID
    from .tzhaar_fight_pit_logic import (
        apply_tzhaar_fight_pit_review_pure,
        tzhaar_fight_pit_view_pure,
    )
    from .varrock_museum_data import VARROCK_MUSEUM_ACTIVITY_ID
    from .varrock_museum_logic import (
        apply_varrock_museum_review_pure,
        varrock_museum_view_pure,
    )
    from .managing_miscellania_data import MANAGING_MISCELLANIA_ACTIVITY_ID
    from .managing_miscellania_logic import (
        apply_managing_miscellania_review_pure,
        managing_miscellania_view_pure,
    )
    from .agility_travel import (
        agility_travel_profile_pure,
        apply_run_energy_credit_pure,
        scheduled_travel_reviews_pure,
    )
    from .wicked_hood_logic import (
        bank_run_phase_label_pure,
        consume_wicked_hood_route_teleport_pure,
        runecrafting_route_phases_pure,
        wicked_hood_skip_active_outbound_pure,
    )
    from .cadence_kernel import EMBEDDED_PROBABILITY, RATE_LIMITED, advance_cadence_pure, default_cadence_profile_state_pure
    from .cadence_live import (
        LIVE_COMBAT_TICKS_PER_REVIEW,
        advance_live_cadence_route_pure,
        resolve_live_cadence_route_pure,
    )
    from .summoning_data import DEFAULT_SUMMONING_TARGET, SUMMONING_ACTIONS_BY_ID
    from .summoning_logic import (
        apply_summoning_training_action_pure,
        familiar_effective_roll_level_pure,
        restore_summoning_points_pure,
        summoning_action_locked_reasons_pure,
        summoning_action_requirements_pure,
    )
    from .slayer_logic import apply_slayer_kills_pure
    from .evil_tree_data import (
        EVIL_TREE_ELIGIBLE_BLESSING_TARGETS,
        EVIL_TREE_NEST_MULTIPLIER,
        EVIL_TREE_UTILITY_ID,
    )
    from .evil_tree_logic import apply_evil_tree_review_pure
    from .big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
    from .big_chinchompa_logic import (
        apply_big_chinchompa_review_pure,
        big_chinchompa_event_active_pure,
        consume_hunter_quota_ticket_pure,
    )
    from .shooting_star_data import (
        SHOOTING_STAR_ACTIVITY_ID,
        SHOOTING_STAR_ORE_BONUS_CHANCE,
    )
    from .shooting_star_logic import (
        apply_shooting_star_review_pure,
        shooting_star_event_mineable_pure,
    )
    from .fist_of_guthix_data import FIST_OF_GUTHIX_ACTIVITY_ID
    from .fist_of_guthix_logic import (
        apply_fist_of_guthix_review_pure,
        fist_of_guthix_can_review_pure,
    )
    from .fight_caves_data import FIGHT_CAVES_ACTIVITY_ID
    from .fight_caves_logic import (
        apply_fight_caves_review_pure,
        fight_caves_view_pure,
    )
    from .phoenix_lair_data import PHOENIX_LAIR_ACTIVITY_ID
    from .phoenix_lair_logic import (
        apply_phoenix_lair_review_pure,
        phoenix_lair_view_pure,
    )
    from .barrows_data import BARROWS_ACTIVITY_ID
    from .barrows_logic import apply_barrows_review_pure, barrows_view_pure
    from .stealing_creation_data import STEALING_CREATION_ACTIVITY_ID
    from .stealing_creation_logic import (
        apply_stealing_creation_review_pure,
        stealing_creation_view_pure,
    )
    from .sorceress_garden_data import SORCERESS_GARDEN_ACTIVITY_ID
    from .sorceress_garden_logic import (
        apply_sorceress_garden_review_pure,
        sorceress_garden_locked_reasons_pure,
        sorceress_garden_view_pure,
    )
    from .penguin_hide_and_seek_data import PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID
    from .penguin_hide_and_seek_logic import (
        apply_penguin_review_pure,
        penguin_view_pure,
    )
    from .vinesweeper_data import (
        COMPOST_POTION_ACTIVITY_ID,
        VINESWEEPER_ACTIVITY_ID,
    )
    from .vinesweeper_logic import (
        apply_compost_potion_pure,
        apply_vinesweeper_review_pure,
        vinesweeper_view_pure,
    )
    from .warriors_guild_data import WARRIORS_GUILD_ACTIVITIES
    from .warriors_guild_logic import (
        apply_warriors_guild_activity_pure,
        apply_warriors_guild_cyclops_kills_pure,
        apply_warriors_guild_cyclossus_kills_pure,
        consume_warriors_guild_cyclops_tokens_pure,
        sanitize_warriors_guild_state_pure,
        warriors_guild_activity_locked_reasons_pure,
    )
    from .livid_farm_data import LIVID_FARM_ACTIVITY_ID
    from .livid_farm_logic import (
        apply_livid_farm_reviews_pure,
        livid_farm_locked_reasons_pure,
    )
except ImportError:  # pragma: no cover - flat import path used by tests
    from constants import (  # type: ignore
        BIRD_NEST_DROP_CHANCE,
        BIRD_NEST_DROP_TABLE,
        BIRD_NEST_OPEN_TABLES,
        COMBAT_BURST_TICKS,
        COMBAT_ENEMY_DATA,
        COMBAT_FOOD_DATA,
        COOKING_DATA,
        CRAFTING_DATA,
        DEFAULT_COMBAT_TARGET,
        DEFAULT_COOKING_TARGET,
        DEFAULT_FIREMAKING_TARGET,
        DEFAULT_FLETCHING_TARGET,
        DEFAULT_FISHING_TARGET,
        DEFAULT_HERBLORE_TARGET,
        DEFAULT_HUNTER_TARGET,
        DEFAULT_MINING_TARGET,
        DEFAULT_RUNECRAFTING_TARGET,
        DEFAULT_UTILITY_ACTIVITY,
        DEFAULT_WOODCUTTING_TARGET,
        EQUIPMENT_DATA,
        EXP_TABLE,
        FIREMAKING_DATA,
        FISHING_DATA,
        HUNTER_DATA,
        FLETCHING_DATA,
        HERBLORE_DATA,
        GLORY_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_TABLE,
        ITEM_DEFINITIONS,
        MINING_BONUS_ITEM_DATA,
        MINING_PICKAXE_DATA,
        MAGIC_DATA,
        DEFAULT_MAGIC_TARGET,
        ORE_DATA,
        PRAYER_DATA,
        DEFAULT_PRAYER_TARGET,
        QUEST_DATA,
        QUEST_UNLOCK_RULES,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        SMITHING_DATA,
        TREE_DATA,
        UTILITY_ACTIVITY_DATA,
        WOODCUTTING_AXE_DATA,
    )
    from logic_pure import (  # type: ignore
        COMBAT_GRAVE_RECOVERY_REVIEWS,
        apply_combat_burst_pure,
        apply_combat_finisher_pure,
        apply_cooking_action_pure,
        apply_crafting_pure,
        apply_firemaking_action_pure,
        apply_fishing_action_pure,
        apply_fletching_pure,
        apply_herblore_action_pure,
        apply_hunter_action_pure,
        apply_quest_combat_encounter_pure,
        apply_mining_action_pure,
        apply_magic_action_pure,
        apply_open_bird_nests_pure,
        apply_prayer_action_pure,
        apply_construction_action_pure,
        construction_target_locked_reasons_pure,
        owned_gilded_altar_burner_count_pure,
        owned_gilded_altar_marrentill_required_pure,
        owned_gilded_altar_access_reasons_pure,
        effective_gilded_altar_multiplier_pure,
        charge_training_urn_for_action_pure,
        intercept_bonecrusher_outputs_pure,
        prayer_gilded_search_step_pure,
        clear_prayer_gilded_stint_pure,
        prayer_target_locked_reasons_pure,
        apply_quest_progress_pure,
        apply_runecrafting_action_pure,
        runecrafting_locked_reasons_pure,
        apply_smithing_action_pure,
        apply_stronghold_step_pure,
        apply_knight_waves_step_pure,
        apply_mage_arena_step_pure,
        attune_mage_arena_spell_pure,
        knight_waves_locked_reasons_pure,
        mage_arena_locked_reasons_pure,
        apply_utility_activity_pure,
        apply_woodcutting_action_pure,
        apply_woodcutting_processing_action_pure,
        best_mining_pickaxe_pure,
        best_woodcutting_axe_pure,
        calculate_cooking_success_probability_pure,
        calculate_firemaking_success_probability_pure,
        calculate_fishing_success_probability_pure,
        fishing_agility_double_catch_chance_pure,
        calculate_hunter_success_probability_pure,
        calculate_mining_success_probability_pure,
        calculate_woodcutting_success_probability_pure,
        cooking_source_roll_chance_pure,
        firemaking_source_roll_chance_pure,
        calculate_new_level,
        can_chop_woodcutting_target_pure,
        can_craft_item_pure,
        can_attempt_quest_review_pure,
        can_progress_quest_pure,
        can_runecraft_target_pure,
        can_smith_item_pure,
        can_start_quest_pure,
        cooking_target_locked_reasons_pure,
        combat_target_locked_reasons_pure,
        eligible_fishing_fish_pure,
        equipment_bonus_state_pure,
        firemaking_target_locked_reasons_pure,
        fishing_method_locked_reasons_pure,
        fletching_material_requirements_pure,
        fletching_target_locked_reasons_pure,
        herblore_target_locked_reasons_pure,
        has_cooking_materials_pure,
        has_crafting_materials_pure,
        has_firemaking_materials_pure,
        has_fishing_bait_pure,
        has_hunter_materials_pure,
        has_ring_of_forging_pure,
        hunter_target_locked_reasons_pure,
        mining_target_locked_reasons_pure,
        red_sandstone_daily_state_pure,
        magic_target_locked_reasons_pure,
        normalize_xp_rewards_pure,
        quest_current_stage_blocker_reasons_pure,
        quest_current_stage_blockers_pure,
        quest_current_stage_resolvable_combat_blockers_pure,
        record_action_telemetry_pure,
        record_cadence_wait_telemetry_pure,
        record_achievement_progress_pure,
        consume_ring_of_forging_charge_pure,
        smithing_success_probability_pure,
        smithing_target_locked_reasons_pure,
        utility_activity_locked_reasons_pure,
        woodcutting_target_locked_reasons_pure,
        thieving_blackjack_threshold_pure,
        apply_thieving_damage_pure,
        thieving_loot_roll_pure,
        thieving_multi_pick_count_pure,
        thieving_roll_succeeds_pure,
        thieving_stall_cadence_profile_pure,
        thieving_success_probability_pure,
        thieving_target_locked_reasons_pure,
        thieving_wall_safe_roll_succeeds_pure,
        STRONGHOLD_STEP_NAMES,
        STRONGHOLD_TOTAL_STEPS,
    )
    from skill_registry import get_skill  # type: ignore
    from farming_logic import (  # type: ignore
        advance_farm_clock_pure,
        apply_farming_review_with_queue_pure,
        consume_next_farm_queue_step_pure,
    )
    from construction_data import (  # type: ignore
        CONSTRUCTION_DATA, DEFAULT_CONSTRUCTION_TARGET, NAIL_DATA, ROOM_DATA,
        SERVANT_DATA, WORKBENCH_TIERS,
    )
    from shop_data import SHOP_PLAYER_BUY_PRICES  # type: ignore
    from smithing_data import DEFAULT_SMITHING_TARGET  # type: ignore
    from urn_data import URN_STATE_ITEM_NAMES, materialize_urn_layout_pure  # type: ignore
    from thieving_data import DEFAULT_THIEVING_TARGET, THIEVING_TARGETS  # type: ignore
    from agility_data import AGILITY_TARGETS_BY_ID, DEFAULT_AGILITY_TARGET  # type: ignore
    from agility_logic import (  # type: ignore
        agility_target_locked_reasons_pure,
        apply_agility_command_pure,
        apply_agility_review_pure,
        sanitize_agility_state_pure,
    )
    from flash_powder_factory_data import (  # type: ignore
        FLASH_POWDER_FACTORY_ACTIVITY_ID,
    )
    from flash_powder_factory_logic import (  # type: ignore
        apply_flash_powder_factory_review_pure,
        apply_factory_outfit_herblore_bonus_pure,
        factory_outfit_four_dose_eligible_pure,
        flash_powder_factory_view_pure,
    )
    from pyramid_plunder_data import PYRAMID_PLUNDER_ACTIVITY_ID  # type: ignore
    from pyramid_plunder_logic import (  # type: ignore
        apply_pyramid_plunder_review_pure,
        pyramid_plunder_view_pure,
    )
    from werewolf_skullball_data import WEREWOLF_SKULLBALL_ACTIVITY_ID  # type: ignore
    from werewolf_skullball_logic import (  # type: ignore
        apply_werewolf_skullball_review_pure,
        werewolf_skullball_view_pure,
    )
    from gnome_ball_data import GNOME_BALL_ACTIVITY_ID  # type: ignore
    from gnome_ball_logic import (  # type: ignore
        apply_gnome_ball_review_pure,
        gnome_ball_view_pure,
    )
    from fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID  # type: ignore
    from fish_flingers_logic import (  # type: ignore
        apply_fish_flingers_review_pure,
        fish_flingers_view_pure,
        fishing_outfit_multiplier_pure,
    )
    from fishing_trawler_data import FISHING_TRAWLER_ACTIVITY_ID  # type: ignore
    from fishing_trawler_logic import (  # type: ignore
        apply_fishing_trawler_review_pure,
        fishing_trawler_view_pure,
    )
    from great_orb_project_data import GREAT_ORB_PROJECT_ACTIVITY_ID  # type: ignore
    from great_orb_project_logic import (  # type: ignore
        apply_great_orb_project_review_pure,
        great_orb_project_view_pure,
    )
    from court_cases_data import COURT_CASES_ACTIVITY_ID  # type: ignore
    from court_cases_logic import (  # type: ignore
        apply_court_case_review_pure,
        court_cases_view_pure,
        filter_court_summons_outputs_pure,
    )
    from circus_data import CIRCUS_ACTIVITY_ID  # type: ignore
    from circus_logic import (  # type: ignore
        apply_circus_review_pure,
        circus_view_pure,
    )
    from trouble_brewing_data import TROUBLE_BREWING_ACTIVITY_ID  # type: ignore
    from trouble_brewing_logic import (  # type: ignore
        apply_trouble_brewing_review_pure,
        trouble_brewing_view_pure,
    )
    from castle_wars_data import CASTLE_WARS_ACTIVITY_ID  # type: ignore
    from castle_wars_logic import (  # type: ignore
        apply_castle_wars_review_pure,
        castle_wars_view_pure,
    )
    from pest_control_data import PEST_CONTROL_ACTIVITY_ID  # type: ignore
    from pest_control_logic import (  # type: ignore
        apply_pest_control_review_pure,
        pest_control_view_pure,
    )
    from barbarian_assault_data import BARBARIAN_ASSAULT_ACTIVITY_ID  # type: ignore
    from barbarian_assault_logic import (  # type: ignore
        apply_barbarian_assault_review_pure,
        barbarian_assault_view_pure,
    )
    from stronghold_player_safety_data import (  # type: ignore
        STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID,
    )
    from stronghold_player_safety_logic import (  # type: ignore
        apply_stronghold_player_safety_review_pure,
        stronghold_player_safety_view_pure,
    )
    from soul_wars_data import SOUL_WARS_ACTIVITY_ID  # type: ignore
    from soul_wars_logic import (  # type: ignore
        apply_soul_wars_review_pure,
        soul_wars_view_pure,
    )
    from shades_of_mortton_data import (  # type: ignore
        SHADES_OF_MORTTON_ACTIVITY_ID,
    )
    from shades_of_mortton_logic import (  # type: ignore
        apply_shades_of_mortton_review_pure,
        shades_of_mortton_view_pure,
    )
    from tzhaar_fight_pit_data import TZHAAR_FIGHT_PIT_ACTIVITY_ID  # type: ignore
    from tzhaar_fight_pit_logic import (  # type: ignore
        apply_tzhaar_fight_pit_review_pure,
        tzhaar_fight_pit_view_pure,
    )
    from varrock_museum_data import VARROCK_MUSEUM_ACTIVITY_ID  # type: ignore
    from varrock_museum_logic import (  # type: ignore
        apply_varrock_museum_review_pure,
        varrock_museum_view_pure,
    )
    from managing_miscellania_data import MANAGING_MISCELLANIA_ACTIVITY_ID  # type: ignore
    from managing_miscellania_logic import (  # type: ignore
        apply_managing_miscellania_review_pure,
        managing_miscellania_view_pure,
    )
    from agility_travel import (  # type: ignore
        agility_travel_profile_pure,
        apply_run_energy_credit_pure,
        scheduled_travel_reviews_pure,
    )
    from wicked_hood_logic import (  # type: ignore
        bank_run_phase_label_pure,
        consume_wicked_hood_route_teleport_pure,
        runecrafting_route_phases_pure,
        wicked_hood_skip_active_outbound_pure,
    )
    from cadence_kernel import EMBEDDED_PROBABILITY, RATE_LIMITED, advance_cadence_pure, default_cadence_profile_state_pure  # type: ignore
    from cadence_live import (  # type: ignore
        LIVE_COMBAT_TICKS_PER_REVIEW,
        advance_live_cadence_route_pure,
        resolve_live_cadence_route_pure,
    )
    from summoning_data import DEFAULT_SUMMONING_TARGET, SUMMONING_ACTIONS_BY_ID  # type: ignore
    from summoning_logic import (  # type: ignore
        apply_summoning_training_action_pure,
        familiar_effective_roll_level_pure,
        restore_summoning_points_pure,
        summoning_action_locked_reasons_pure,
        summoning_action_requirements_pure,
    )
    from slayer_logic import apply_slayer_kills_pure  # type: ignore
    from evil_tree_data import (  # type: ignore
        EVIL_TREE_ELIGIBLE_BLESSING_TARGETS,
        EVIL_TREE_NEST_MULTIPLIER,
        EVIL_TREE_UTILITY_ID,
    )
    from evil_tree_logic import apply_evil_tree_review_pure  # type: ignore
    from big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID  # type: ignore
    from big_chinchompa_logic import (  # type: ignore
        apply_big_chinchompa_review_pure,
        big_chinchompa_event_active_pure,
        consume_hunter_quota_ticket_pure,
    )
    from shooting_star_data import (  # type: ignore
        SHOOTING_STAR_ACTIVITY_ID,
        SHOOTING_STAR_ORE_BONUS_CHANCE,
    )
    from shooting_star_logic import (  # type: ignore
        apply_shooting_star_review_pure,
        shooting_star_event_mineable_pure,
    )
    from fist_of_guthix_data import FIST_OF_GUTHIX_ACTIVITY_ID  # type: ignore
    from fist_of_guthix_logic import (  # type: ignore
        apply_fist_of_guthix_review_pure,
        fist_of_guthix_can_review_pure,
    )
    from fight_caves_data import FIGHT_CAVES_ACTIVITY_ID  # type: ignore
    from fight_caves_logic import (  # type: ignore
        apply_fight_caves_review_pure,
        fight_caves_view_pure,
    )
    from phoenix_lair_data import PHOENIX_LAIR_ACTIVITY_ID  # type: ignore
    from phoenix_lair_logic import (  # type: ignore
        apply_phoenix_lair_review_pure,
        phoenix_lair_view_pure,
    )
    from barrows_data import BARROWS_ACTIVITY_ID  # type: ignore
    from barrows_logic import apply_barrows_review_pure, barrows_view_pure  # type: ignore
    from stealing_creation_data import STEALING_CREATION_ACTIVITY_ID  # type: ignore
    from stealing_creation_logic import (  # type: ignore
        apply_stealing_creation_review_pure,
        stealing_creation_view_pure,
    )
    from sorceress_garden_data import SORCERESS_GARDEN_ACTIVITY_ID  # type: ignore
    from sorceress_garden_logic import (  # type: ignore
        apply_sorceress_garden_review_pure,
        sorceress_garden_locked_reasons_pure,
        sorceress_garden_view_pure,
    )
    from penguin_hide_and_seek_data import (  # type: ignore
        PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID,
    )
    from penguin_hide_and_seek_logic import (  # type: ignore
        apply_penguin_review_pure,
        penguin_view_pure,
    )
    from vinesweeper_data import (  # type: ignore
        COMPOST_POTION_ACTIVITY_ID,
        VINESWEEPER_ACTIVITY_ID,
    )
    from vinesweeper_logic import (  # type: ignore
        apply_compost_potion_pure,
        apply_vinesweeper_review_pure,
        vinesweeper_view_pure,
    )
    from warriors_guild_data import WARRIORS_GUILD_ACTIVITIES  # type: ignore
    from warriors_guild_logic import (  # type: ignore
        apply_warriors_guild_activity_pure,
        apply_warriors_guild_cyclops_kills_pure,
        apply_warriors_guild_cyclossus_kills_pure,
        consume_warriors_guild_cyclops_tokens_pure,
        sanitize_warriors_guild_state_pure,
        warriors_guild_activity_locked_reasons_pure,
    )
    from livid_farm_data import LIVID_FARM_ACTIVITY_ID  # type: ignore
    from livid_farm_logic import (  # type: ignore
        apply_livid_farm_reviews_pure,
        livid_farm_locked_reasons_pure,
    )

try:
    from .runtime_actions_context import (  # noqa: F401  (re-export)
        RuntimeActionContext,
    )
except ImportError:  # pragma: no cover - flat test imports
    from runtime_actions_context import (  # type: ignore  # noqa: F401
        RuntimeActionContext,
    )

try:
    from .runtime_actions_context import (
        RuntimeActionContext,
    )
except ImportError:  # pragma: no cover - flat test imports
    from runtime_actions_context import (  # type: ignore
        RuntimeActionContext,
    )


def missing_materials_text(requirements: dict[str, int], inventory: dict[str, Any]) -> str:
    missing = [
        f"{amount} {material}"
        for material, amount in requirements.items()
        if inventory.get(material, 0) < amount
    ]
    return ", ".join(missing) if missing else "materials"


def _switch_material_failure_to_bankstanding(ctx: RuntimeActionContext) -> None:
    if callable(ctx.switch_to_bankstanding):
        ctx.switch_to_bankstanding()
    else:
        ctx.deactivate_current_skill()


def fishing_materials_text(method_spec: dict[str, Any], inventory: dict[str, Any]) -> str:
    bait_options = tuple(method_spec.get("bait_options") or ())
    if not bait_options:
        return "materials"
    if len(bait_options) == 1:
        bait = bait_options[0]
        return f"1 {bait}"
    return "any of " + ", ".join(f"1 {bait}" for bait in bait_options)


def _award_action_xp_rewards(ctx: RuntimeActionContext, xp_rewards: Any, owner_skill_id: str) -> float:
    rewards = normalize_xp_rewards_pure({"xp_rewards": xp_rewards})
    if not rewards:
        return 0.0
    primary_skill_id = owner_skill_id if any(reward.get("skill_id") == owner_skill_id for reward in rewards) else str(rewards[0].get("skill_id", ""))
    primary_amount = 0.0
    for reward in rewards:
        skill_id = str(reward.get("skill_id", ""))
        try:
            amount = float(reward.get("amount", 0.0) or 0.0)
        except (TypeError, ValueError):
            amount = 0.0
        if not skill_id or amount <= 0:
            continue
        skill = get_skill(skill_id)
        if skill is None:
            continue
        if skill.trainable:
            gained = ctx.award_skill_exp(skill.exp_key, amount)
            ctx.level_up_check(skill.display_name, ctx.player_data)
        else:
            ctx.award_hidden_skill_exp(skill.exp_key, skill.level_key, amount)
            gained = amount
        if skill_id == primary_skill_id:
            primary_amount = gained
    return primary_amount


def _combined_success_probability(probabilities: Any) -> float:
    dry_probability = 1.0
    for probability in probabilities:
        try:
            chance = float(probability)
        except (TypeError, ValueError):
            chance = 0.0
        dry_probability *= 1.0 - max(0.0, min(chance, 1.0))
    return max(0.0, min(1.0 - dry_probability, 1.0))


def _record_action(
    ctx: RuntimeActionContext,
    skill_id: str,
    action_id: str,
    success: bool,
    *,
    expected_success_chance: Optional[float] = None,
    output_item: Optional[str] = None,
    output_qty: int = 1,
    output_items: Optional[dict[str, int]] = None,
    achievement_output_items: Optional[dict[str, int]] = None,
    failure_kind: Optional[str] = None,
    primary_xp: Any = 0,
    proposed_outcome_success: Any = None,
) -> None:
    record_action_telemetry_pure(
        ctx.player_data,
        skill_id,
        action_id,
        success,
        expected_success_chance=expected_success_chance,
        output_item=output_item,
        output_qty=output_qty,
        output_items=output_items,
        failure_kind=failure_kind,
    )
    progress_outputs = achievement_output_items
    if progress_outputs is None:
        progress_outputs = output_items
    record_achievement_progress_pure(
        ctx.player_data,
        skill_id,
        action_id,
        success,
        output_item=output_item if progress_outputs is None else None,
        output_qty=output_qty,
        output_items=progress_outputs,
    )
    if ctx.cadence_shadow_enabled:
        try:
            try:
                from .cadence_shadow import record_cadence_shadow_pure
            except ImportError:  # pragma: no cover - flat import path used by tests
                from cadence_shadow import record_cadence_shadow_pure  # type: ignore
            record_cadence_shadow_pure(
                ctx.player_data,
                skill_id,
                action_id,
                success,
                live_xp=primary_xp,
                proposed_outcome_success=proposed_outcome_success,
            )
        except Exception:
            # Observation must never make a live action fail.
            pass


def _record_cadence_wait(ctx: RuntimeActionContext, skill_id: str, action_id: str) -> None:
    record_cadence_wait_telemetry_pure(ctx.player_data, skill_id, action_id)
    ctx.show_activity_gain("Cadence — no action opportunity this review")
    ctx.save_player_data()


def _admit_live_cadence(
    ctx: RuntimeActionContext,
    skill_id: str,
    action_id: str,
) -> tuple[RuntimeActionContext, bool]:
    if not ctx.cadence_live_enabled:
        return ctx, True
    declaration, admitted = advance_live_cadence_route_pure(
        ctx.player_data, skill_id, action_id
    )
    if not admitted:
        _record_cadence_wait(ctx, skill_id, action_id)
        return ctx, False
    if declaration.mode == RATE_LIMITED:
        return dataclasses.replace(ctx, cadence_forced_opportunity=True), True
    return ctx, True


def _charge_urn_for_action(
    ctx: RuntimeActionContext,
    skill_id: str,
    action_id: str,
    action_spec: dict[str, Any],
    base_xp: float,
    output_item: Optional[str] = None,
) -> dict[str, Any]:
    updated, info = charge_training_urn_for_action_pure(
        ctx.player_data,
        skill_id,
        action_id,
        action_spec,
        base_xp,
        output_item,
        action_id,
    )
    # The pure result may repair a dangling pointer even when this action did not
    # charge XP, so always apply it rather than keying state updates to `charged`.
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    return info


def advance_farming_clock_for_review(ctx: RuntimeActionContext) -> dict[str, Any]:
    """Advance the background farm clock once for any answered review card."""

    updated, info = advance_farm_clock_pure(ctx.player_data, 1, ctx.random_random)
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    return info


def _apply_farming_queue_result(
    ctx: RuntimeActionContext,
    old_levels: dict[str, int],
    updated: dict[str, Any],
    consumed: bool,
    info: dict[str, Any],
) -> bool:
    if not consumed:
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    if info.get("status") in {"executed", "continuing"}:
        for skill, xp_key in (
            ("Farming", "farming_xp"),
            ("Woodcutting", "woodcutting_xp"),
            ("Agility", "agility_xp"),
            ("Magic", "magic_xp"),
            ("Slayer", "slayer_xp"),
        ):
            if float(info.get(xp_key, 0.0) or 0.0) <= 0:
                continue
            level_key = f"{skill.lower()}_level"
            awarded_level = int(ctx.player_data.get(level_key, old_levels[skill]) or old_levels[skill])
            ctx.player_data[level_key] = old_levels[skill]
            ctx.level_up_check(skill, ctx.player_data)
            ctx.player_data[level_key] = max(
                awarded_level,
                int(ctx.player_data.get(level_key, old_levels[skill]) or old_levels[skill]),
            )
        combat_rewards = info.get("xp_rewards", {})
        _refresh_combat_levels(ctx, combat_rewards)
        gained = sum(
            float(info.get(key, 0.0) or 0.0)
            for key in (
                "farming_xp",
                "woodcutting_xp",
                "agility_xp",
                "magic_xp",
                "slayer_xp",
            )
        )
        if isinstance(combat_rewards, dict):
            gained += sum(float(value or 0.0) for value in combat_rewards.values())
        if gained > 0:
            ctx.show_exp(gained)
    else:
        ctx.show_activity_gain(f"Farm detour skipped: {info.get('message', 'step is no longer valid')}")
    ctx.check_achievements(ctx.player_data)
    ctx.refresh_skill_availability()
    return True


def _farming_levels_before_answer(ctx: RuntimeActionContext) -> dict[str, int]:
    return {
        "Farming": int(ctx.player_data.get("farming_level", 1) or 1),
        "Woodcutting": int(ctx.player_data.get("woodcutting_level", 1) or 1),
        "Agility": int(ctx.player_data.get("agility_level", 1) or 1),
        "Magic": int(ctx.player_data.get("magic_level", 1) or 1),
        "Slayer": int(ctx.player_data.get("slayer_level", 1) or 1),
    }


def handle_farming_queue_answer(ctx: RuntimeActionContext) -> bool:
    """Consume and persist one queued field step, including an invalid skip."""

    old_levels = _farming_levels_before_answer(ctx)
    updated, consumed, info = consume_next_farm_queue_step_pure(
        ctx.player_data,
        ctx.random_random,
        ctx.review_action_multiplier,
    )
    consumed = _apply_farming_queue_result(ctx, old_levels, updated, consumed, info)
    if consumed:
        ctx.save_player_data()
    return consumed


def handle_farming_review_answer(ctx: RuntimeActionContext) -> bool:
    """Apply one successful review's queued detour and eager clock tick once."""

    old_levels = _farming_levels_before_answer(ctx)
    updated, consumed, info = apply_farming_review_with_queue_pure(
        ctx.player_data,
        ctx.random_random,
        ctx.review_action_multiplier,
    )
    consumed = _apply_farming_queue_result(ctx, old_levels, updated, consumed, info)
    if consumed:
        ctx.save_player_data()
    return consumed


_COMBAT_EXP_SKILLS = {
    "attack_exp": "attack",
    "strength_exp": "strength",
    "defense_exp": "defense",
    "constitution_exp": "constitution",
    "ranged_exp": "ranged",
    "magic_exp": "magic",
    "prayer_exp": "prayer",
    "slayer_exp": "slayer",
}


def _combat_review_ticks(ctx: RuntimeActionContext) -> int:
    try:
        multiplier = int(ctx.review_action_multiplier)
    except (TypeError, ValueError):
        multiplier = 1
    ticks_per_review = (
        LIVE_COMBAT_TICKS_PER_REVIEW
        if ctx.cadence_live_enabled
        else COMBAT_BURST_TICKS
    )
    return ticks_per_review * max(1, multiplier)


def _refresh_combat_levels(ctx: RuntimeActionContext, xp_rewards: Any) -> None:
    if not isinstance(xp_rewards, dict):
        return
    for exp_key, amount in xp_rewards.items():
        try:
            gained = float(amount or 0.0)
        except (TypeError, ValueError):
            gained = 0.0
        if gained <= 0:
            continue
        skill = get_skill(_COMBAT_EXP_SKILLS.get(str(exp_key), ""))
        if skill is None:
            continue
        ctx.player_data[skill.level_key] = calculate_new_level(
            ctx.player_data.get(skill.exp_key, 0),
            ctx.player_data.get(skill.level_key, 1),
            EXP_TABLE,
        )
        ctx.level_up_check(skill.display_name, ctx.player_data)
