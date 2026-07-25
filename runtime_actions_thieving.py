"""runtime_actions_thieving.py - split out of runtime_actions.py; see that module's header."""

from __future__ import annotations

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
    from .runtime_actions_shared import (  # noqa: F401  (re-export)
        _COMBAT_EXP_SKILLS,
        _admit_live_cadence,
        _apply_farming_queue_result,
        _award_action_xp_rewards,
        _charge_urn_for_action,
        _combat_review_ticks,
        _combined_success_probability,
        _farming_levels_before_answer,
        _record_action,
        _record_cadence_wait,
        _refresh_combat_levels,
        _switch_material_failure_to_bankstanding,
        advance_farming_clock_for_review,
        fishing_materials_text,
        handle_farming_queue_answer,
        handle_farming_review_answer,
        missing_materials_text,
    )
except ImportError:  # pragma: no cover - flat test imports
    from runtime_actions_shared import (  # type: ignore  # noqa: F401
        _COMBAT_EXP_SKILLS,
        _admit_live_cadence,
        _apply_farming_queue_result,
        _award_action_xp_rewards,
        _charge_urn_for_action,
        _combat_review_ticks,
        _combined_success_probability,
        _farming_levels_before_answer,
        _record_action,
        _record_cadence_wait,
        _refresh_combat_levels,
        _switch_material_failure_to_bankstanding,
        advance_farming_clock_for_review,
        fishing_materials_text,
        handle_farming_queue_answer,
        handle_farming_review_answer,
        missing_materials_text,
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
    from .runtime_actions_shared import (
        _award_action_xp_rewards,
        _record_action,
    )
except ImportError:  # pragma: no cover - flat test imports
    from runtime_actions_shared import (  # type: ignore
        _award_action_xp_rewards,
        _record_action,
    )

try:
    from .runtime_actions_context import (
        RuntimeActionContext,
    )
except ImportError:  # pragma: no cover - flat test imports
    from runtime_actions_context import (  # type: ignore
        RuntimeActionContext,
    )


def _thieving_rng_index(ctx: RuntimeActionContext, size: int) -> int:
    return min(max(int(ctx.random_random() * max(size, 1)), 0), max(size - 1, 0))


def _thieving_grant_outputs(player_data: dict[str, Any], outputs: dict[str, int]) -> None:
    outputs = filter_court_summons_outputs_pure(player_data, outputs)
    inventory = dict(player_data.get("inventory", {}) or {})
    for item_name, amount in outputs.items():
        inventory[item_name] = int(inventory.get(item_name, 0) or 0) + max(int(amount), 0)
    player_data["inventory"] = inventory


def _thieving_failure(ctx: RuntimeActionContext, target: str, spec: dict[str, Any]) -> bool:
    player_data = ctx.player_data
    wall_safe = spec.get("kind") == "wall_safe"
    default_low = 20 if wall_safe else int(spec.get("failure_damage", 0) or 0)
    default_high = 60 if wall_safe else default_low
    low = int(spec.get("damage_min", default_low) or 0)
    high = max(low, int(spec.get("damage_max", default_high) or default_high))
    fight_back = bool(
        spec.get("kind") == "blackjack"
        and player_data.get("thieving_fight_back_when_caught")
    )
    damage = 0 if fight_back else low + _thieving_rng_index(ctx, high - low + 1) if high else 0
    damage_result = {"damage": 0, "died": False, "food_used": None}
    if damage > 0:
        damaged_data, damage_result = apply_thieving_damage_pure(
            player_data, damage, source="thieving_failure"
        )
        player_data.update(damaged_data)
    player_data["thieving_stunned"] = True
    player_data["thieving_failure_count"] = int(player_data.get("thieving_failure_count", 0) or 0) + 1
    _record_action(
        ctx, "thieving", target, False,
        failure_kind="trap" if wall_safe else "caught",
    )
    if fight_back:
        player_data["current_combat_target"] = "menaphite_thug"
        player_data["combat_encounter"] = {
            "target_id": "menaphite_thug",
            "enemy_lifepoints": 600,
        }
        ctx.deactivate_current_skill()
        ctx.show_activity_gain("Caught — Menaphite Thug fight started")
    elif damage_result.get("died"):
        ctx.deactivate_current_skill()
        ctx.show_activity_gain("☠ YOU DIED — Thieving failure; gear moved to grave")
    elif wall_safe:
        ctx.show_activity_gain(f"Trap sprung — {damage_result['damage']} LP damage; next review clears the stun")
    else:
        ctx.show_activity_gain(f"Caught — {damage_result['damage']} LP damage; next review clears the stun")
    food_used = damage_result.get("food_used")
    if food_used:
        ctx.show_activity_gain(
            f"Auto-ate {food_used['item']} (+{food_used['healed_by']} LP)"
        )
    ctx.save_player_data()
    return False


def _thieving_award_success(
    ctx: RuntimeActionContext,
    target: str,
    spec: dict[str, Any],
    *,
    xp: float | None = None,
    fixed_outputs: dict[str, int] | None = None,
    loot_count: int = 1,
) -> None:
    outputs: dict[str, int] = dict(fixed_outputs or {})
    if fixed_outputs is None:
        for _ in range(max(loot_count, 1)):
            rolled = thieving_loot_roll_pure(
                spec,
                _thieving_rng_index(ctx, int(spec.get("loot_total", 1) or 1)),
                ctx.random_random(),
            )
            for item_name, amount in rolled.items():
                outputs[item_name] = outputs.get(item_name, 0) + amount
    _thieving_grant_outputs(ctx.player_data, outputs)
    base_xp = float(spec.get("xp", 0.0) if xp is None else xp)
    gained = _award_action_xp_rewards(
        ctx, ({"skill_id": "thieving", "amount": base_xp},), "thieving"
    )
    ctx.player_data["thieving_success_count"] = int(ctx.player_data.get("thieving_success_count", 0) or 0) + 1
    _record_action(
        ctx, "thieving", target, True,
        expected_success_chance=thieving_success_probability_pure(
            ctx.player_data.get("thieving_level", 1), spec
        ) if "min_chance" in spec else 1.0,
        output_items=outputs, primary_xp=base_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.refresh_skill_availability()
    ctx.show_exp(gained)


def handle_thieving_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = str(player_data.get("current_thieving", DEFAULT_THIEVING_TARGET))
    if target not in THIEVING_TARGETS:
        target = DEFAULT_THIEVING_TARGET
        player_data["current_thieving"] = target
    spec = THIEVING_TARGETS[target]
    locked = thieving_target_locked_reasons_pure(player_data, target, THIEVING_TARGETS)
    if locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Thieving target locked",
            f"{spec.get('display_name', target)} requires {', '.join(locked)}, so Thieving has been switched off.",
        )
        return False

    if player_data.get("thieving_stunned"):
        player_data["thieving_stunned"] = False
        ctx.show_activity_gain("Recovered from the stun — no Thieving attempt this review")
        ctx.save_player_data()
        return False

    kind = spec.get("kind")
    if kind in {"stall", "wall_safe"}:
        profile = thieving_stall_cadence_profile_pure(target, spec)
        profiles = dict(player_data.get("cadence_profiles", {}) or {})
        step = advance_cadence_pure(
            profile,
            profiles.get(profile.profile_id, default_cadence_profile_state_pure()),
        )
        profiles[profile.profile_id] = step.state
        player_data["cadence_profiles"] = profiles
        if not step.emitted:
            record_cadence_wait_telemetry_pure(
                player_data,
                "thieving",
                target,
            )
            ctx.show_activity_gain("Stall restocking — cadence advanced")
            ctx.save_player_data()
            return True

    player_data["thieving_attempt_count"] = int(player_data.get("thieving_attempt_count", 0) or 0) + 1

    if kind == "blackjack":
        phase = str(player_data.get("thieving_blackjack_phase", "needs_lure"))
        if phase == "needs_lure":
            player_data["thieving_blackjack_phase"] = "ready_to_knockout"
            ctx.show_activity_gain("Menaphite thug lured — next review attempts the knockout")
            ctx.save_player_data()
            return False
        if phase == "knocked_out":
            _thieving_award_success(
                ctx, target, spec,
                fixed_outputs={"Coins": int(spec.get("coins", 60) or 60)},
            )
            remaining = max(0, int(player_data.get("thieving_blackjack_picks_remaining", 2) or 0) - 1)
            player_data["thieving_blackjack_picks_remaining"] = remaining
            if remaining <= 0:
                player_data["thieving_blackjack_phase"] = "ready_to_knockout"
            ctx.save_player_data()
            return False
        threshold = thieving_blackjack_threshold_pure(
            player_data.get("thieving_level", 1),
            spec.get("knockout_min_chance", 185),
            spec.get("knockout_max_chance", 255),
        )
        if _thieving_rng_index(ctx, 255) > threshold:
            return _thieving_failure(ctx, target, spec)
        player_data["thieving_blackjack_phase"] = "knocked_out"
        player_data["thieving_blackjack_picks_remaining"] = 2
        knockout_xp = float(spec.get("knockout_xp", 10.0) or 0.0)
        gained = _award_action_xp_rewards(
            ctx, ({"skill_id": "thieving", "amount": knockout_xp},), "thieving"
        )
        ctx.show_exp(gained)
        ctx.show_activity_gain("Knockout succeeded — two guaranteed picks available")
        ctx.save_player_data()
        return False

    level = player_data.get("thieving_level", 1)
    if kind in {"pickpocket", "wall_safe"}:
        chance = thieving_success_probability_pure(level, spec)
        roll = _thieving_rng_index(ctx, 255)
        succeeds = (
            thieving_wall_safe_roll_succeeds_pure(
                level, spec["min_chance"], spec["max_chance"], roll
            )
            if kind == "wall_safe"
            else thieving_roll_succeeds_pure(
                level, spec["min_chance"], spec["max_chance"], roll
            )
        )
        if not succeeds:
            return _thieving_failure(ctx, target, spec)

    loot_count = 1
    if kind == "pickpocket":
        loot_count = thieving_multi_pick_count_pure(
            level,
            player_data.get("agility_level", 1),
            spec.get("level", 1),
            _thieving_rng_index(ctx, 8),
        )
    _thieving_award_success(ctx, target, spec, loot_count=loot_count)
    ctx.save_player_data()
    return True
