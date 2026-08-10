"""runtime_actions_utility.py - split out of runtime_actions.py; see that module's header."""

from __future__ import annotations

from ..core.constants import (
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
from ..logic_pure.logic_pure import (
    COMBAT_GRAVE_RECOVERY_REVIEWS,
    apply_combat_burst_pure,
    apply_combat_finisher_pure,
    apply_cooking_action_pure,
    apply_crafting_pure,
    apply_crystal_chest_pure,
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
from ..core.skill_registry import get_skill
from ..logic.farming_logic import (
    advance_farm_clock_pure,
    apply_farming_review_with_queue_pure,
    consume_next_farm_queue_step_pure,
)
from ..data.construction_data import (
    CONSTRUCTION_DATA, DEFAULT_CONSTRUCTION_TARGET, NAIL_DATA, ROOM_DATA,
    SERVANT_DATA, WORKBENCH_TIERS,
)
from ..data.crystal_chest_data import (
    CRYSTAL_CHEST_ACTIVITY_ID,
    CRYSTAL_CHEST_REWARDS,
    CRYSTAL_CHEST_RING_IMPROVEMENT_CHANCE,
)
from ..data.shop_data import SHOP_PLAYER_BUY_PRICES
from ..data.smithing_data import DEFAULT_SMITHING_TARGET
from ..data.urn_data import URN_STATE_ITEM_NAMES, materialize_urn_layout_pure
from ..data.thieving_data import DEFAULT_THIEVING_TARGET, THIEVING_TARGETS
from ..data.agility_data import AGILITY_TARGETS_BY_ID, DEFAULT_AGILITY_TARGET
from ..logic.agility_logic import (
    agility_target_locked_reasons_pure,
    apply_agility_command_pure,
    apply_agility_review_pure,
    sanitize_agility_state_pure,
)
from ..data.flash_powder_factory_data import FLASH_POWDER_FACTORY_ACTIVITY_ID
from ..logic.flash_powder_factory_logic import (
    apply_flash_powder_factory_review_pure,
    apply_factory_outfit_herblore_bonus_pure,
    factory_outfit_four_dose_eligible_pure,
    flash_powder_factory_view_pure,
)
from ..data.pyramid_plunder_data import PYRAMID_PLUNDER_ACTIVITY_ID
from ..logic.pyramid_plunder_logic import (
    apply_pyramid_plunder_review_pure,
    pyramid_plunder_view_pure,
)
from ..data.werewolf_skullball_data import WEREWOLF_SKULLBALL_ACTIVITY_ID
from ..logic.werewolf_skullball_logic import (
    apply_werewolf_skullball_review_pure,
    werewolf_skullball_view_pure,
)
from ..data.gnome_ball_data import GNOME_BALL_ACTIVITY_ID
from ..logic.gnome_ball_logic import (
    apply_gnome_ball_review_pure,
    gnome_ball_view_pure,
)
from ..data.fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID
from ..logic.fish_flingers_logic import (
    apply_fish_flingers_review_pure,
    fish_flingers_view_pure,
    fishing_outfit_multiplier_pure,
)
from ..data.fishing_trawler_data import FISHING_TRAWLER_ACTIVITY_ID
from ..logic.fishing_trawler_logic import (
    apply_fishing_trawler_review_pure,
    fishing_trawler_view_pure,
)
from ..data.great_orb_project_data import GREAT_ORB_PROJECT_ACTIVITY_ID
from ..logic.great_orb_project_logic import (
    apply_great_orb_project_review_pure,
    great_orb_project_view_pure,
)
from ..data.court_cases_data import COURT_CASES_ACTIVITY_ID
from ..logic.court_cases_logic import (
    apply_court_case_review_pure,
    court_cases_view_pure,
    filter_court_summons_outputs_pure,
)
from ..data.circus_data import CIRCUS_ACTIVITY_ID
from ..logic.circus_logic import apply_circus_review_pure, circus_view_pure
from ..data.trouble_brewing_data import TROUBLE_BREWING_ACTIVITY_ID
from ..logic.trouble_brewing_logic import (
    apply_trouble_brewing_review_pure,
    trouble_brewing_view_pure,
)
from ..data.castle_wars_data import CASTLE_WARS_ACTIVITY_ID
from ..logic.castle_wars_logic import (
    apply_castle_wars_review_pure,
    castle_wars_view_pure,
)
from ..data.pest_control_data import PEST_CONTROL_ACTIVITY_ID
from ..logic.pest_control_logic import (
    apply_pest_control_review_pure,
    pest_control_view_pure,
)
from ..data.conquest_data import CONQUEST_ACTIVITY_ID
from ..logic.conquest_logic import conquest_view_pure
from ..data.barbarian_assault_data import BARBARIAN_ASSAULT_ACTIVITY_ID
from ..logic.barbarian_assault_logic import (
    apply_barbarian_assault_review_pure,
    barbarian_assault_view_pure,
)
from ..data.stronghold_player_safety_data import STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID
from ..logic.stronghold_player_safety_logic import (
    apply_stronghold_player_safety_review_pure,
    stronghold_player_safety_view_pure,
)
from ..data.soul_wars_data import SOUL_WARS_ACTIVITY_ID
from ..logic.soul_wars_logic import (
    apply_soul_wars_review_pure,
    soul_wars_view_pure,
)
from ..data.shades_of_mortton_data import SHADES_OF_MORTTON_ACTIVITY_ID
from ..logic.shades_of_mortton_logic import (
    apply_shades_of_mortton_review_pure,
    shades_of_mortton_view_pure,
)
from ..data.tzhaar_fight_pit_data import TZHAAR_FIGHT_PIT_ACTIVITY_ID
from ..data.treasure_trails_data import TREASURE_TRAILS_ACTIVITY_ID
from ..logic.tzhaar_fight_pit_logic import (
    apply_tzhaar_fight_pit_review_pure,
    tzhaar_fight_pit_view_pure,
)
from ..data.duel_arena_data import DUEL_ARENA_ACTIVITY_ID
from ..data.clan_wars_data import CLAN_WARS_ACTIVITY_ID
from ..data.troll_invasion_data import TROLL_INVASION_ACTIVITY_ID
from ..data.mage_training_arena_data import MAGE_TRAINING_ARENA_ACTIVITY_ID
from ..logic.mage_training_arena_logic import mage_training_arena_view_pure
from ..data.temple_trekking_data import TEMPLE_TREKKING_ACTIVITY_ID
from ..logic.temple_trekking_logic import temple_trekking_view_pure
from ..data.mobilising_armies_data import MOBILISING_ARMIES_ACTIVITY_ID
from ..logic.mobilising_armies_logic import mobilising_armies_view_pure
from ..data.gnome_restaurant_data import GNOME_RESTAURANT_ACTIVITY_ID
from ..logic.gnome_restaurant_logic import gnome_restaurant_view_pure
from ..data.dominion_tower_data import DOMINION_TOWER_ACTIVITY_ID
from ..logic.dominion_tower_logic import dominion_tower_view_pure
from ..data.crucible_data import CRUCIBLE_ACTIVITY_ID
from ..data.goblin_raids_data import GOBLIN_RAIDS_ACTIVITY_ID
from ..data.varrock_museum_data import VARROCK_MUSEUM_ACTIVITY_ID
from ..logic.varrock_museum_logic import (
    apply_varrock_museum_review_pure,
    varrock_museum_view_pure,
)
from ..data.managing_miscellania_data import MANAGING_MISCELLANIA_ACTIVITY_ID
from ..logic.managing_miscellania_logic import (
    apply_managing_miscellania_review_pure,
    managing_miscellania_view_pure,
)
from ..logic.agility_travel import (
    agility_travel_profile_pure,
    apply_run_energy_credit_pure,
    scheduled_travel_reviews_pure,
)
from ..logic.wicked_hood_logic import (
    bank_run_phase_label_pure,
    consume_wicked_hood_route_teleport_pure,
    runecrafting_route_phases_pure,
    wicked_hood_skip_active_outbound_pure,
)
from ..logic.cadence_kernel import EMBEDDED_PROBABILITY, RATE_LIMITED, advance_cadence_pure, default_cadence_profile_state_pure
from ..logic.cadence_live import (
    LIVE_COMBAT_TICKS_PER_REVIEW,
    advance_live_cadence_route_pure,
    resolve_live_cadence_route_pure,
)
from ..data.summoning_data import DEFAULT_SUMMONING_TARGET, SUMMONING_ACTIONS_BY_ID
from ..logic.summoning_logic import (
    apply_summoning_training_action_pure,
    familiar_effective_roll_level_pure,
    restore_summoning_points_pure,
    summoning_action_locked_reasons_pure,
    summoning_action_requirements_pure,
)
from ..logic.slayer_logic import apply_slayer_kills_pure
from ..data.evil_tree_data import (
    EVIL_TREE_ELIGIBLE_BLESSING_TARGETS,
    EVIL_TREE_NEST_MULTIPLIER,
    EVIL_TREE_UTILITY_ID,
)
from ..logic.evil_tree_logic import apply_evil_tree_review_pure
from ..data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from ..logic.big_chinchompa_logic import (
    apply_big_chinchompa_review_pure,
    big_chinchompa_event_active_pure,
    consume_hunter_quota_ticket_pure,
)
from ..data.shooting_star_data import (
    SHOOTING_STAR_ACTIVITY_ID,
    SHOOTING_STAR_ORE_BONUS_CHANCE,
)
from ..logic.shooting_star_logic import (
    apply_shooting_star_review_pure,
    shooting_star_event_mineable_pure,
)
from ..data.fist_of_guthix_data import FIST_OF_GUTHIX_ACTIVITY_ID
from ..logic.fist_of_guthix_logic import (
    apply_fist_of_guthix_review_pure,
    fist_of_guthix_can_review_pure,
)
from ..data.fight_caves_data import FIGHT_CAVES_ACTIVITY_ID
from ..data.dagannoth_kings_data import DAGANNOTH_KINGS_ACTIVITY_ID
from ..logic.fight_caves_logic import (
    apply_fight_caves_review_pure,
    fight_caves_view_pure,
)
from ..data.phoenix_lair_data import PHOENIX_LAIR_ACTIVITY_ID
from ..logic.phoenix_lair_logic import (
    apply_phoenix_lair_review_pure,
    phoenix_lair_view_pure,
)
from ..data.bork_data import BORK_ACTIVITY_ID
from ..data.skeletal_horror_data import SKELETAL_HORROR_ACTIVITY_ID
from ..logic.bork_logic import bork_view_pure
from ..logic.skeletal_horror_logic import skeletal_horror_view_pure
from ..data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID
from ..data.enchanted_key_data import ENCHANTED_KEY_ACTIVITY_ID
from ..data.barrows_data import BARROWS_ACTIVITY_ID
from ..logic.barrows_logic import apply_barrows_review_pure, barrows_view_pure
from ..data.stealing_creation_data import STEALING_CREATION_ACTIVITY_ID
from ..logic.stealing_creation_logic import (
    apply_stealing_creation_review_pure,
    stealing_creation_view_pure,
)
from ..data.sorceress_garden_data import SORCERESS_GARDEN_ACTIVITY_ID
from ..logic.sorceress_garden_logic import (
    apply_sorceress_garden_review_pure,
    sorceress_garden_locked_reasons_pure,
    sorceress_garden_view_pure,
)
from ..data.penguin_hide_and_seek_data import PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID
from ..logic.penguin_hide_and_seek_logic import (
    apply_penguin_review_pure,
    penguin_view_pure,
)
from ..data.vinesweeper_data import (
    COMPOST_POTION_ACTIVITY_ID,
    VINESWEEPER_ACTIVITY_ID,
)
from ..logic.vinesweeper_logic import (
    apply_compost_potion_pure,
    apply_vinesweeper_review_pure,
    vinesweeper_view_pure,
)
from ..data.warriors_guild_data import WARRIORS_GUILD_ACTIVITIES
from ..logic.warriors_guild_logic import (
    apply_warriors_guild_activity_pure,
    apply_warriors_guild_cyclops_kills_pure,
    apply_warriors_guild_cyclossus_kills_pure,
    consume_warriors_guild_cyclops_tokens_pure,
    sanitize_warriors_guild_state_pure,
    warriors_guild_activity_locked_reasons_pure,
)
from ..data.livid_farm_data import LIVID_FARM_ACTIVITY_ID
from ..logic.livid_farm_logic import (
    apply_livid_farm_reviews_pure,
    livid_farm_locked_reasons_pure,
)

from .runtime_actions_production import (  # noqa: F401  (re-export)
    _refresh_smithing_and_crafting_availability,
    _spec_output_items,
    handle_construction_answer,
    handle_cooking_answer,
    handle_crafting_answer,
    handle_firemaking_answer,
    handle_fletching_answer,
    handle_herblore_answer,
    handle_prayer_answer,
    handle_quest_answer,
    handle_runecrafting_answer,
    handle_smithing_answer,
    handle_summoning_answer,
)

from .runtime_actions_activities import (  # noqa: F401  (re-export)
    KNIGHT_WAVES_UTILITY_KEY,
    MAGE_ARENA_ATTUNE_PREFIX,
    MAGE_ARENA_UTILITY_KEY,
    STRONGHOLD_UTILITY_KEY,
    _handle_barrows_answer,
    _handle_big_chinchompa_answer,
    _handle_circus_answer,
    _handle_court_cases_answer,
    _handle_evil_tree_answer,
    _handle_fight_caves_answer,
    _handle_dagannoth_kings_answer,
    _handle_fish_flingers_answer,
    _handle_fishing_trawler_answer,
    _handle_fist_of_guthix_answer,
    _handle_gnome_ball_answer,
    _handle_great_orb_project_answer,
    _handle_knight_waves_answer,
    _handle_livid_farm_answer,
    _handle_mage_arena_answer,
    _handle_mage_arena_attunement_answer,
    _handle_managing_miscellania_answer,
    _handle_penguin_answer,
    _handle_phoenix_lair_answer,
    _handle_bork_answer,
    _handle_skeletal_horror_answer,
    _handle_tears_of_guthix_answer,
    _handle_enchanted_key_answer,
    _handle_pyramid_plunder_answer,
    _handle_shooting_star_answer,
    _handle_sorceress_garden_answer,
    _handle_stealing_creation_answer,
    _handle_stronghold_answer,
    _handle_vinesweeper_answer,
    _handle_werewolf_skullball_answer,
    handle_agility_answer,
    handle_barbarian_assault_answer,
    handle_castle_wars_answer,
    handle_flash_powder_factory_answer,
    handle_pest_control_answer,
    handle_conquest_answer,
    handle_shades_of_mortton_answer,
    handle_soul_wars_answer,
    handle_stronghold_player_safety_answer,
    handle_trouble_brewing_answer,
    handle_treasure_trail_answer,
    handle_tzhaar_fight_pit_answer,
    handle_duel_arena_answer,
    handle_clan_wars_answer,
    handle_troll_invasion_answer,
    handle_mage_training_arena_answer,
    handle_temple_trekking_answer,
    handle_mobilising_armies_answer,
    handle_gnome_restaurant_answer,
    handle_dominion_tower_answer,
    handle_crucible_answer,
    handle_goblin_raids_answer,
    handle_varrock_museum_answer,
)

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

from .runtime_actions_context import (  # noqa: F401  (re-export)
    RuntimeActionContext,
)

from .runtime_actions_production import (
    _spec_output_items,
)

from .runtime_actions_activities import (
    KNIGHT_WAVES_UTILITY_KEY,
    MAGE_ARENA_ATTUNE_PREFIX,
    MAGE_ARENA_UTILITY_KEY,
    STRONGHOLD_UTILITY_KEY,
    _handle_barrows_answer,
    _handle_big_chinchompa_answer,
    _handle_circus_answer,
    _handle_court_cases_answer,
    _handle_evil_tree_answer,
    _handle_fight_caves_answer,
    _handle_dagannoth_kings_answer,
    _handle_fish_flingers_answer,
    _handle_fishing_trawler_answer,
    _handle_fist_of_guthix_answer,
    _handle_gnome_ball_answer,
    _handle_great_orb_project_answer,
    _handle_knight_waves_answer,
    _handle_livid_farm_answer,
    _handle_mage_arena_answer,
    _handle_mage_arena_attunement_answer,
    _handle_managing_miscellania_answer,
    _handle_penguin_answer,
    _handle_phoenix_lair_answer,
    _handle_pyramid_plunder_answer,
    _handle_shooting_star_answer,
    _handle_sorceress_garden_answer,
    _handle_stealing_creation_answer,
    _handle_stronghold_answer,
    _handle_vinesweeper_answer,
    _handle_werewolf_skullball_answer,
    handle_barbarian_assault_answer,
    handle_castle_wars_answer,
    handle_flash_powder_factory_answer,
    handle_pest_control_answer,
    handle_conquest_answer,
    handle_shades_of_mortton_answer,
    handle_soul_wars_answer,
    handle_stronghold_player_safety_answer,
    handle_trouble_brewing_answer,
    handle_treasure_trail_answer,
    handle_tzhaar_fight_pit_answer,
    handle_duel_arena_answer,
    handle_clan_wars_answer,
    handle_troll_invasion_answer,
    handle_mage_training_arena_answer,
    handle_temple_trekking_answer,
    handle_mobilising_armies_answer,
    handle_gnome_restaurant_answer,
    handle_dominion_tower_answer,
    handle_crucible_answer,
    handle_goblin_raids_answer,
    handle_varrock_museum_answer,
)

from .runtime_actions_shared import (
    _record_action,
    _refresh_combat_levels,
    _switch_material_failure_to_bankstanding,
    missing_materials_text,
)

from .runtime_actions_context import (
    RuntimeActionContext,
)


def handle_utility_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    activity_key = player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
    if activity_key == EVIL_TREE_UTILITY_ID:
        return _handle_evil_tree_answer(ctx)
    if activity_key == BIG_CHINCHOMPA_UTILITY_ID:
        return _handle_big_chinchompa_answer(ctx)
    if activity_key == SHOOTING_STAR_ACTIVITY_ID:
        return _handle_shooting_star_answer(ctx)
    if activity_key == FIST_OF_GUTHIX_ACTIVITY_ID:
        return _handle_fist_of_guthix_answer(ctx)
    if activity_key == FIGHT_CAVES_ACTIVITY_ID:
        return _handle_fight_caves_answer(ctx)
    if activity_key == DAGANNOTH_KINGS_ACTIVITY_ID:
        return _handle_dagannoth_kings_answer(ctx)
    if activity_key == PHOENIX_LAIR_ACTIVITY_ID:
        return _handle_phoenix_lair_answer(ctx)
    if activity_key == SKELETAL_HORROR_ACTIVITY_ID:
        return _handle_skeletal_horror_answer(ctx)
    if activity_key == BORK_ACTIVITY_ID:
        return _handle_bork_answer(ctx)
    if activity_key == TEARS_OF_GUTHIX_ACTIVITY_ID:
        return _handle_tears_of_guthix_answer(ctx)
    if activity_key == ENCHANTED_KEY_ACTIVITY_ID:
        return _handle_enchanted_key_answer(ctx)
    if activity_key == BARROWS_ACTIVITY_ID:
        return _handle_barrows_answer(ctx)
    if activity_key == STEALING_CREATION_ACTIVITY_ID:
        return _handle_stealing_creation_answer(ctx)
    if activity_key == SORCERESS_GARDEN_ACTIVITY_ID:
        return _handle_sorceress_garden_answer(ctx)
    if activity_key == PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID:
        return _handle_penguin_answer(ctx)
    if activity_key == VINESWEEPER_ACTIVITY_ID:
        return _handle_vinesweeper_answer(ctx)
    if activity_key == FLASH_POWDER_FACTORY_ACTIVITY_ID:
        return handle_flash_powder_factory_answer(ctx)
    if activity_key == PYRAMID_PLUNDER_ACTIVITY_ID:
        return _handle_pyramid_plunder_answer(ctx)
    if activity_key == WEREWOLF_SKULLBALL_ACTIVITY_ID:
        return _handle_werewolf_skullball_answer(ctx)
    if activity_key == GNOME_BALL_ACTIVITY_ID:
        return _handle_gnome_ball_answer(ctx)
    if activity_key == FISH_FLINGERS_ACTIVITY_ID:
        return _handle_fish_flingers_answer(ctx)
    if activity_key == FISHING_TRAWLER_ACTIVITY_ID:
        return _handle_fishing_trawler_answer(ctx)
    if activity_key == GREAT_ORB_PROJECT_ACTIVITY_ID:
        return _handle_great_orb_project_answer(ctx)
    if activity_key == COURT_CASES_ACTIVITY_ID:
        return _handle_court_cases_answer(ctx)
    if activity_key == CIRCUS_ACTIVITY_ID:
        return _handle_circus_answer(ctx)
    if activity_key == TROUBLE_BREWING_ACTIVITY_ID:
        return handle_trouble_brewing_answer(ctx)
    if activity_key == CASTLE_WARS_ACTIVITY_ID:
        return handle_castle_wars_answer(ctx)
    if activity_key == PEST_CONTROL_ACTIVITY_ID:
        return handle_pest_control_answer(ctx)
    if activity_key == CONQUEST_ACTIVITY_ID:
        return handle_conquest_answer(ctx)
    if activity_key == BARBARIAN_ASSAULT_ACTIVITY_ID:
        return handle_barbarian_assault_answer(ctx)
    if activity_key == STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID:
        return handle_stronghold_player_safety_answer(ctx)
    if activity_key == SOUL_WARS_ACTIVITY_ID:
        return handle_soul_wars_answer(ctx)
    if activity_key == SHADES_OF_MORTTON_ACTIVITY_ID:
        return handle_shades_of_mortton_answer(ctx)
    if activity_key == TZHAAR_FIGHT_PIT_ACTIVITY_ID:
        return handle_tzhaar_fight_pit_answer(ctx)
    if activity_key == DUEL_ARENA_ACTIVITY_ID:
        return handle_duel_arena_answer(ctx)
    if activity_key == CLAN_WARS_ACTIVITY_ID:
        return handle_clan_wars_answer(ctx)
    if activity_key == TROLL_INVASION_ACTIVITY_ID:
        return handle_troll_invasion_answer(ctx)
    if activity_key == MAGE_TRAINING_ARENA_ACTIVITY_ID:
        return handle_mage_training_arena_answer(ctx)
    if activity_key == TEMPLE_TREKKING_ACTIVITY_ID:
        return handle_temple_trekking_answer(ctx)
    if activity_key == MOBILISING_ARMIES_ACTIVITY_ID:
        return handle_mobilising_armies_answer(ctx)
    if activity_key == GNOME_RESTAURANT_ACTIVITY_ID:
        return handle_gnome_restaurant_answer(ctx)
    if activity_key == DOMINION_TOWER_ACTIVITY_ID:
        return handle_dominion_tower_answer(ctx)
    if activity_key == CRUCIBLE_ACTIVITY_ID:
        return handle_crucible_answer(ctx)
    if activity_key == GOBLIN_RAIDS_ACTIVITY_ID:
        return handle_goblin_raids_answer(ctx)
    if activity_key == TREASURE_TRAILS_ACTIVITY_ID:
        return handle_treasure_trail_answer(ctx)
    if activity_key == VARROCK_MUSEUM_ACTIVITY_ID:
        return handle_varrock_museum_answer(ctx)
    if activity_key == MANAGING_MISCELLANIA_ACTIVITY_ID:
        return _handle_managing_miscellania_answer(ctx)
    if activity_key == STRONGHOLD_UTILITY_KEY:
        return _handle_stronghold_answer(ctx)
    if activity_key == KNIGHT_WAVES_UTILITY_KEY:
        return _handle_knight_waves_answer(ctx)
    if activity_key == MAGE_ARENA_UTILITY_KEY:
        return _handle_mage_arena_answer(ctx)
    if str(activity_key).startswith(MAGE_ARENA_ATTUNE_PREFIX):
        return _handle_mage_arena_attunement_answer(ctx, str(activity_key))
    if activity_key == LIVID_FARM_ACTIVITY_ID:
        return _handle_livid_farm_answer(ctx)
    if activity_key in WARRIORS_GUILD_ACTIVITIES:
        selected = (
            activity_key
            if activity_key in WARRIORS_GUILD_ACTIVITIES
            else ""
        )
        locked = warriors_guild_activity_locked_reasons_pure(
            player_data,
            selected,
        )
        mode = sanitize_warriors_guild_state_pure(
            player_data.get("warriors_guild")
        )["automation_mode"]
        if locked and mode == "advanced":
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Warriors' Guild activity locked",
                f"{WARRIORS_GUILD_ACTIVITIES[selected]['display_name']} requires {', '.join(locked)}.",
            )
            return False
        updated, ok, result = apply_warriors_guild_activity_pure(
            player_data,
            selected,
            (ctx.random_random(), ctx.random_random()),
        )
        if not ok:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Warriors' Guild activity locked",
                str(result.get("reason", "No activity is available.")),
            )
            return False
        xp_rewards = dict(result.get("xp_rewards", {}) or {})
        for exp_key, amount in xp_rewards.items():
            updated[exp_key] = float(updated.get(exp_key, 0.0) or 0.0) + float(amount)
        player_data.clear()
        player_data.update(updated)
        damage_result = {"damage": 0, "died": False, "food_used": None}
        if int(result.get("damage", 0) or 0) > 0:
            damaged, damage_result = apply_thieving_damage_pure(
                player_data,
                int(result["damage"]),
                source="warriors_guild_failure",
            )
            player_data.clear()
            player_data.update(damaged)
        _record_action(
            ctx,
            "utility",
            str(result["activity_id"]),
            bool(result.get("success")),
            expected_success_chance=1.0,
            failure_kind="activity_failure" if not result.get("success") else "",
        )
        _refresh_combat_levels(ctx, xp_rewards)
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        if damage_result.get("died"):
            ctx.deactivate_current_skill()
            ctx.show_activity_gain(
                f"☠ YOU DIED — {result['display_name']} failure; gear moved to grave"
            )
            return True
        if result.get("success"):
            armour = (
                f" · {result['armour_tier']} suit"
                if result.get("armour_tier")
                else ""
            )
            loss = (
                f" · lost {result['lost_item']}"
                if result.get("lost_item")
                else ""
            )
            ctx.show_activity_gain(
                f"{result['display_name']}: +{int(result['token_gain'])} "
                f"{result['token_key']} tokens{armour}{loss}"
            )
        else:
            ctx.show_activity_gain(
                f"{result['display_name']} failed — "
                f"{int(damage_result.get('damage', 0) or 0)} LP damage"
            )
        return True
    if activity_key not in UTILITY_ACTIVITY_DATA:
        activity_key = DEFAULT_UTILITY_ACTIVITY
        player_data["current_utility"] = activity_key
    spec = UTILITY_ACTIVITY_DATA[activity_key]
    display_name = spec.get("display_name", activity_key)

    locked_reasons = utility_activity_locked_reasons_pure(player_data, activity_key, UTILITY_ACTIVITY_DATA, QUEST_UNLOCK_RULES)
    quest_locked = tuple(reason for reason in locked_reasons if reason != "materials")
    if quest_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Activity locked",
            f"{display_name} requires {', '.join(quest_locked)}, so it's been switched off. "
            "Open the AnkiScape menu to pick another activity.",
        )
        return False

    if locked_reasons:
        requirements = spec.get("requirements", {})
        if requirements:
            missing = missing_materials_text(requirements, player_data.get("inventory", {}))
            _switch_material_failure_to_bankstanding(ctx)
            ctx.show_error_message(
                "Out of materials",
                f"You're out of {missing} for {display_name}, so AnkiScape switched "
                "to Bankstanding. Choose another activity when you are ready.",
            )
        else:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Activity switched off",
                f"{display_name} can't run right now, so it's been switched off. "
                "Open the AnkiScape menu to pick another activity.",
            )
        return False

    if activity_key == COMPOST_POTION_ACTIVITY_ID:
        new_inv, ok, compost_result = apply_compost_potion_pure(
            player_data.get("inventory", {})
        )
        if not ok:
            _switch_material_failure_to_bankstanding(ctx)
            ctx.show_error_message(
                "Unavailable activity",
                str(compost_result.get("reason", "Compost potion inputs are missing.")),
            )
            return False
        player_data["inventory"] = new_inv
        _record_action(
            ctx,
            "utility",
            activity_key,
            True,
            expected_success_chance=1.0,
            output_items=dict(compost_result.get("outputs", {}) or {}),
        )
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        ctx.show_activity_gain(
            f"Upgraded 1 Compost to Supercompost · {compost_result['remainder']} remains"
        )
        return True

    if activity_key == "open_bird_nest":
        batch_size = 28
        try:
            batch_size = max(int(spec.get("batch_size", 28)), 1)
        except (TypeError, ValueError):
            batch_size = 28
        rolls = [ctx.random_random() for _ in range(batch_size)]
        new_inv, ok, processed, _outputs = apply_open_bird_nests_pure(
            player_data.get("inventory", {}),
            BIRD_NEST_OPEN_TABLES,
            rolls=rolls,
            batch_size=batch_size,
        )
        if not ok:
            _switch_material_failure_to_bankstanding(ctx)
            ctx.show_error_message(
                "Unavailable activity",
                f"{display_name} is out of inputs, so AnkiScape switched to Bankstanding.",
            )
            return False
        player_data["inventory"] = new_inv
        _record_action(ctx, "utility", activity_key, True, expected_success_chance=1.0, output_items=_outputs)
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        ctx.show_activity_gain(f"Opened {processed} bird nest{'s' if processed != 1 else ''}")
        return True

    if activity_key == CRYSTAL_CHEST_ACTIVITY_ID:
        equipment = player_data.get("equipment", {})
        ring_of_wealth = (
            isinstance(equipment, dict)
            and "Ring of wealth" in equipment.values()
        )
        reward_roll = ctx.random_random()
        wealth_trigger_roll = ctx.random_random() if ring_of_wealth else 1.0
        wealth_reward_roll = (
            ctx.random_random()
            if ring_of_wealth
            and wealth_trigger_roll < CRYSTAL_CHEST_RING_IMPROVEMENT_CHANCE
            else 0.0
        )
        new_inv, ok, _reward_id, outputs, improved = apply_crystal_chest_pure(
            player_data.get("inventory", {}),
            CRYSTAL_CHEST_REWARDS,
            reward_roll,
            ring_of_wealth=ring_of_wealth,
            wealth_trigger_roll=wealth_trigger_roll,
            wealth_reward_roll=wealth_reward_roll,
            wealth_improvement_chance=CRYSTAL_CHEST_RING_IMPROVEMENT_CHANCE,
        )
        if not ok:
            _switch_material_failure_to_bankstanding(ctx)
            ctx.show_error_message(
                "Unavailable activity",
                "Open Crystal chest is out of keys, so AnkiScape switched to Bankstanding.",
            )
            return False
        player_data["inventory"] = new_inv
        _record_action(
            ctx,
            "utility",
            activity_key,
            True,
            expected_success_chance=1.0,
            output_items=outputs,
        )
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        reward_text = ", ".join(
            f"{item} x{amount}" for item, amount in outputs.items()
        )
        suffix = " · Ring of Wealth improved the roll" if improved else ""
        ctx.show_activity_gain(f"Opened Crystal chest · {reward_text}{suffix}")
        return True

    new_inv, _exp, ok, processed = apply_utility_activity_pure(
        activity_key,
        player_data.get("inventory", {}),
        UTILITY_ACTIVITY_DATA,
    )
    if not ok:
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Unavailable activity",
            f"{display_name} is out of inputs, so AnkiScape switched to Bankstanding.",
        )
        return False

    player_data["inventory"] = new_inv
    output_items = {item: amount * max(int(processed), 0) for item, amount in _spec_output_items(spec).items()}
    _record_action(ctx, "utility", activity_key, True, expected_success_chance=1.0, output_items=output_items)
    if spec.get("deactivate_after_run"):
        ctx.deactivate_current_skill()
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()

    if spec.get("no_op"):
        # A no-op activity produces nothing by definition and the HUD already
        # reads "idle at the Bank", so restating it every review is pure noise.
        return True
    outputs = spec.get("outputs", {})
    if isinstance(outputs, dict) and outputs:
        if spec.get("deactivate_after_run"):
            ctx.show_activity_gain(str(display_name).replace("Buy ", "Bought ", 1))
        else:
            total_outputs = sum(max(int(amount), 1) for amount in outputs.values() if isinstance(amount, int))
            gained = total_outputs * max(int(processed), 0)
            if gained > 0:
                ctx.show_activity_gain(f"+{gained} items")
    else:
        output_item = str(spec.get("output_item", activity_key))
        try:
            output_qty = max(int(spec.get("output_qty", 1)), 1)
        except (TypeError, ValueError):
            output_qty = 1
        gained = output_qty * max(int(processed), 0)
        if gained > 0:
            ctx.show_activity_gain(f"+{gained} {output_item}")
    return True
