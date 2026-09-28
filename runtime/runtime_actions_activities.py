"""runtime_actions_activities.py - split out of runtime_actions.py; see that module's header."""

from __future__ import annotations

from collections.abc import Mapping

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
from ..logic_pure.achievement_diary_events import (
    record_direct_diary_event_pure,
)
from ..logic_pure.logic_pure import (
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
from ..data.shop_data import SHOP_PLAYER_BUY_PRICES
from ..data.smithing_data import DEFAULT_SMITHING_TARGET
from ..data.urn_data import URN_STATE_ITEM_NAMES, materialize_urn_layout_pure
from ..data.thieving_data import DEFAULT_THIEVING_TARGET, THIEVING_TARGETS
from ..data.agility_data import AGILITY_TARGETS_BY_ID, DEFAULT_AGILITY_TARGET
from ..logic.agility_logic import (
    agility_maximum_failure_damage_pure,
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
from ..logic.conquest_logic import apply_conquest_review_pure
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
from ..logic.tzhaar_fight_pit_logic import (
    apply_tzhaar_fight_pit_review_pure,
    tzhaar_fight_pit_view_pure,
)
from ..data.duel_arena_data import DUEL_ARENA_ACTIVITY_ID
from ..logic.duel_arena_logic import apply_duel_arena_review_pure
from ..data.clan_wars_data import CLAN_WARS_ACTIVITY_ID
from ..data.troll_invasion_data import (
    TROLL_INVASION_ACTIVITY_ID,
    TROLL_INVASION_REPAIR_MODE,
)
from ..data.mage_training_arena_data import MAGE_TRAINING_ARENA_ACTIVITY_ID
from ..data.crucible_data import CRUCIBLE_ACTIVITY_ID
from ..data.goblin_raids_data import GOBLIN_RAIDS_ACTIVITY_ID
from ..data.treasure_trails_data import TREASURE_TRAILS_ACTIVITY_ID
from ..logic.treasure_trails_logic import apply_treasure_trail_review_pure
from ..logic.clan_wars_logic import apply_clan_wars_review_pure
from ..logic.troll_invasion_logic import apply_troll_invasion_review_pure
from ..logic.mage_training_arena_logic import apply_mage_training_arena_review_pure
from ..data.ranging_guild_data import RANGING_GUILD_ACTIVITY_ID
from ..logic.ranging_guild_logic import apply_ranging_guild_review_pure
from ..data.temple_trekking_data import TEMPLE_TREKKING_ACTIVITY_ID
from ..logic.temple_trekking_logic import apply_temple_trekking_review_pure
from ..data.mobilising_armies_data import MOBILISING_ARMIES_ACTIVITY_ID
from ..logic.mobilising_armies_logic import apply_mobilising_armies_review_pure
from ..data.gnome_restaurant_data import GNOME_RESTAURANT_ACTIVITY_ID
from ..logic.gnome_restaurant_logic import apply_gnome_restaurant_review_pure
from ..data.dominion_tower_data import DOMINION_TOWER_ACTIVITY_ID
from ..logic.dominion_tower_logic import apply_dominion_tower_review_pure
from ..logic.crucible_logic import apply_crucible_review_pure
from ..logic.goblin_raids_logic import apply_goblin_raids_review_pure
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
from ..logic.review_strip_logic import record_review_event_pure
from ..data.fist_of_guthix_data import FIST_OF_GUTHIX_ACTIVITY_ID
from ..logic.fist_of_guthix_logic import (
    apply_fist_of_guthix_review_pure,
    fist_of_guthix_can_review_pure,
)
from ..data.fight_caves_data import FIGHT_CAVES_ACTIVITY_ID
from ..logic.fight_caves_logic import (
    apply_fight_caves_review_pure,
    fight_caves_view_pure,
)
from ..data.dagannoth_kings_data import DAGANNOTH_KINGS_ACTIVITY_ID
from ..logic.dagannoth_kings_logic import (
    apply_dagannoth_kings_review_pure,
)
from ..data.dungeoneering_data import DUNGEONEERING_ACTIVITY_ID
from ..logic.dungeoneering_logic import apply_dungeoneering_review_pure
from ..data.phoenix_lair_data import PHOENIX_LAIR_ACTIVITY_ID
from ..logic.phoenix_lair_logic import (
    apply_phoenix_lair_review_pure,
    phoenix_lair_view_pure,
)
from ..data.bork_data import BORK_ACTIVITY_ID
from ..data.skeletal_horror_data import SKELETAL_HORROR_ACTIVITY_ID
from ..logic.bork_logic import apply_bork_review_pure
from ..logic.skeletal_horror_logic import apply_skeletal_horror_review_pure
from ..data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID
from ..logic.tears_of_guthix_logic import apply_tears_of_guthix_review_pure
from ..data.enchanted_key_data import ENCHANTED_KEY_ACTIVITY_ID
from ..logic.enchanted_key_logic import apply_enchanted_key_review_pure
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

from .runtime_actions_shared import (
    _award_action_xp_rewards,
    _record_action,
    _refresh_combat_levels,
    _switch_material_failure_to_bankstanding,
)

from .runtime_actions_context import (
    RuntimeActionContext,
)


from .runtime_actions_activities_shared import (  # noqa: F401  (re-export)
    STRONGHOLD_UTILITY_KEY,
    KNIGHT_WAVES_UTILITY_KEY,
    MAGE_ARENA_UTILITY_KEY,
    MAGE_ARENA_ATTUNE_PREFIX,
    _activity_session_is_current,
)


from .runtime_actions_activities_training import (  # noqa: F401  (re-export)
    _handle_stronghold_answer,
    _handle_knight_waves_answer,
    _handle_mage_arena_answer,
    _handle_mage_arena_attunement_answer,
    _handle_livid_farm_answer,
)


from .runtime_actions_activities_distractions import (  # noqa: F401  (re-export)
    _handle_evil_tree_answer,
    _handle_big_chinchompa_answer,
    _handle_shooting_star_answer,
)


def _handle_fist_of_guthix_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_fist_of_guthix_review_pure(
        ctx.player_data,
        rng=ctx.random_random,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fist of Guthix unavailable",
            str(result.get("reason", "Talk to Fiara before entering the arena.")),
        )
        return False

    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        FIST_OF_GUTHIX_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=total_xp,
    )
    skill_names = {
        "attack_exp": "Attack",
        "strength_exp": "Strength",
        "defense_exp": "Defence",
        "constitution_exp": "Constitution",
        "magic_exp": "Magic",
        "ranged_exp": "Ranged",
    }
    for exp_key, skill_name in skill_names.items():
        if float(xp_rewards.get(exp_key, 0.0) or 0.0) > 0:
            ctx.level_up_check(skill_name, ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)

    if result.get("match_complete"):
        match = result.get("match_result", {}) or {}
        ctx.show_activity_gain(
            f"Fist of Guthix {str(match.get('outcome', 'complete'))} · "
            f"{int(match.get('player_charges', 0)):,}–"
            f"{int(match.get('opponent_charges', 0)):,} charges · "
            f"+{int(match.get('tokens', 0))} tokens"
        )
    elif result.get("round_complete"):
        ctx.show_activity_gain(
            f"Round {int(result.get('round', 0))} complete · "
            f"{int(result.get('charges', 0)):,} charges · "
            f"now {str(result.get('next_role', '')).title()}"
        )
    else:
        ctx.show_activity_gain(
            f"FoG {str(result.get('player_role', '')).title()} · "
            f"+{int(result.get('charge_gained', 0))} charges · "
            f"{int(result.get('charge_total', 0)):,}/5,000"
        )
    return True


from .runtime_actions_activities_encounters import (  # noqa: F401  (re-export)
    _handle_fight_caves_answer,
)


def _handle_dagannoth_kings_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_dagannoth_kings_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Dagannoth Kings unavailable",
            str(result.get("reason", "Enter the boss room before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        DAGANNOTH_KINGS_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=total_xp,
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(
        str(result.get("status", "Dagannoth Kings review complete"))
    )
    return True


from .runtime_actions_activities_encounters import (  # noqa: F401  (re-export)
    handle_dungeoneering_answer,
    _handle_phoenix_lair_answer,
    _handle_skeletal_horror_answer,
    _handle_bork_answer,
)


from .runtime_actions_activities_distractions import (  # noqa: F401  (re-export)
    _handle_tears_of_guthix_answer,
    _handle_enchanted_key_answer,
)


from .runtime_actions_activities_encounters import (  # noqa: F401  (re-export)
    _handle_barrows_answer,
)


from .runtime_actions_activities_competitions import (  # noqa: F401  (re-export)
    _handle_stealing_creation_answer,
)


from .runtime_actions_activities_distractions import (  # noqa: F401  (re-export)
    _handle_sorceress_garden_answer,
    _handle_penguin_answer,
    _handle_vinesweeper_answer,
)


from .runtime_actions_activities_training import (  # noqa: F401  (re-export)
    handle_flash_powder_factory_answer,
    _handle_pyramid_plunder_answer,
    _handle_werewolf_skullball_answer,
    _handle_gnome_ball_answer,
    _handle_fish_flingers_answer,
    _handle_fishing_trawler_answer,
    _handle_great_orb_project_answer,
)


from .runtime_actions_activities_distractions import (  # noqa: F401  (re-export)
    _handle_court_cases_answer,
    _handle_circus_answer,
)


from .runtime_actions_activities_competitions import (  # noqa: F401  (re-export)
    handle_trouble_brewing_answer,
)


def handle_castle_wars_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    view = castle_wars_view_pure(ctx.player_data)
    duty: str | None = None
    session = view.get("castle_wars")
    if isinstance(session, dict) and session.get("automation_mode") == "advanced":
        duty = str(session.get("duty", duty))
    updated, ok, result = apply_castle_wars_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
        duty=duty,
        opponent_roll=ctx.random_random(),
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Castle Wars unavailable",
            str(result.get("reason", "Enter Castle Wars before training.")),
        )
        return False
    xp_rewards = dict(result.get("xp_rewards") or {})
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    record_direct_diary_event_pure(
        ctx.player_data,
        True,
        "castle_wars_review",
        duty=str(result.get("duty", "")),
    )
    _record_action(
        ctx,
        "utility",
        CASTLE_WARS_ACTIVITY_ID,
        productive,
        expected_success_chance=1.0,
        failure_kind="safe_death" if result.get("died") else None,
        primary_xp=sum(float(amount or 0.0) for amount in xp_rewards.values()),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    xp_total = sum(float(amount or 0.0) for amount in xp_rewards.values())
    if xp_total > 0:
        ctx.show_exp(xp_total)
    ctx.show_activity_gain(str(result.get("message") or result.get("status") or "Castle Wars beat resolved"))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


from .runtime_actions_activities_competitions import (  # noqa: F401  (re-export)
    handle_pest_control_answer,
    handle_conquest_answer,
    handle_barbarian_assault_answer,
)


from .runtime_actions_activities_distractions import (  # noqa: F401  (re-export)
    handle_varrock_museum_answer,
    handle_stronghold_player_safety_answer,
)


from .runtime_actions_activities_competitions import (  # noqa: F401  (re-export)
    handle_soul_wars_answer,
)


from .runtime_actions_activities_encounters import (  # noqa: F401  (re-export)
    handle_shades_of_mortton_answer,
)


def handle_tzhaar_fight_pit_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_tzhaar_fight_pit_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "TzHaar Fight Pit unavailable",
            str(result.get("reason", "Enter the Fight Pit before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    combat = dict(result.get("combat") or {})
    xp_rewards = dict(combat.get("xp_rewards") or {})
    lost = result.get("outcome") == "loss"
    _record_action(
        ctx,
        "utility",
        TZHAAR_FIGHT_PIT_ACTIVITY_ID,
        not lost,
        expected_success_chance=1.0,
        failure_kind="safe_death" if lost else None,
        primary_xp=sum(float(value or 0.0) for value in xp_rewards.values()),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("message") or "Fight Pit beat resolved"))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


from .runtime_actions_activities_competitions import (  # noqa: F401  (re-export)
    handle_duel_arena_answer,
    handle_clan_wars_answer,
    handle_troll_invasion_answer,
)


from .runtime_actions_activities_training import (  # noqa: F401  (re-export)
    handle_mage_training_arena_answer,
    handle_ranging_guild_answer,
)


def _report_temple_trekking_unavailable(ctx: RuntimeActionContext, result: dict) -> None:
    state = ctx.player_data.get("temple_trekking")
    if not (
        _activity_session_is_current(ctx, TEMPLE_TREKKING_ACTIVITY_ID)
        and isinstance(state, Mapping)
        and state.get("session")
    ):
        _switch_material_failure_to_bankstanding(ctx)
    ctx.show_error_message(
        "Temple Trekking unavailable",
        str(result.get("reason", "Start or resume a trek before training.")),
    )


def _record_temple_trekking_advance(
    ctx: RuntimeActionContext,
    result: dict,
    combat: dict,
    xp_rewards: dict,
) -> None:
    player_died = bool(result.get("player_died") or combat.get("died"))
    companion_died = bool(result.get("companion_died"))
    outputs = (
        {str(result["token_item"]): 1}
        if result.get("completed") and result.get("token_item")
        else None
    )
    _record_action(
        ctx,
        "utility",
        TEMPLE_TREKKING_ACTIVITY_ID,
        not player_died and not companion_died,
        expected_success_chance=1.0,
        failure_kind="dangerous_death" if player_died else "escort_failure" if companion_died else None,
        output_items=outputs,
        primary_xp=sum(float(value or 0.0) for value in xp_rewards.values()),
    )


def handle_temple_trekking_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_temple_trekking_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
        productive=productive,
    )
    if not ok:
        _report_temple_trekking_unavailable(ctx, result)
        return False
    if not productive and not result.get("advanced"):
        return True
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    combat = dict(result.get("combat") or {})
    xp_rewards = dict(combat.get("xp_rewards") or {})
    if result.get("advanced"):
        _record_temple_trekking_advance(ctx, result, combat, xp_rewards)
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("message") or "Temple Trekking event resolved"))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


from .runtime_actions_activities_competitions import (  # noqa: F401  (re-export)
    handle_mobilising_armies_answer,
)


def handle_gnome_restaurant_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_gnome_restaurant_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
    )
    if not ok:
        state = ctx.player_data.get("gnome_restaurant")
        if not (
            _activity_session_is_current(ctx, GNOME_RESTAURANT_ACTIVITY_ID)
            and isinstance(state, Mapping)
            and state.get("order")
        ):
            _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Gnome Restaurant unavailable",
            str(result.get("reason", "Take a delivery job before reviewing.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    if result.get("advanced"):
        _record_action(
            ctx,
            "utility",
            GNOME_RESTAURANT_ACTIVITY_ID,
            True,
            expected_success_chance=1.0,
            output_items=dict(result.get("output_items") or {}),
        )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("message") or "Gnome Restaurant delivery"))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_dominion_tower_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_dominion_tower_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        state = ctx.player_data.get("dominion_tower")
        if not (
            _activity_session_is_current(ctx, DOMINION_TOWER_ACTIVITY_ID)
            and isinstance(state, Mapping)
            and state.get("mode")
            and state.get("roster")
        ):
            _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Dominion Tower unavailable",
            str(result.get("reason", "Enter the tower before training it.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards") or {})
    _record_action(
        ctx,
        "utility",
        DOMINION_TOWER_ACTIVITY_ID,
        not result.get("player_died"),
        expected_success_chance=1.0,
        failure_kind="safe_death" if result.get("player_died") else None,
        primary_xp=sum(float(value or 0.0) for value in xp_rewards.values()),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("status") or "Dominion Tower round resolved"))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


from .runtime_actions_activities_encounters import (  # noqa: F401  (re-export)
    handle_goblin_raids_answer,
)


from .runtime_actions_activities_competitions import (  # noqa: F401  (re-export)
    handle_crucible_answer,
)


from .runtime_actions_activities_distractions import (  # noqa: F401  (re-export)
    _handle_managing_miscellania_answer,
)


from .runtime_actions_activities_training import (  # noqa: F401  (re-export)
    handle_agility_answer,
)


from .runtime_actions_activities_distractions import (  # noqa: F401  (re-export)
    handle_treasure_trail_answer,
)
