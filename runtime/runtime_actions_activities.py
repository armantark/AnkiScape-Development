"""runtime_actions_activities.py - split out of runtime_actions.py; see that module's header."""

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
from ..logic.fight_caves_logic import (
    apply_fight_caves_review_pure,
    fight_caves_view_pure,
)
from ..data.phoenix_lair_data import PHOENIX_LAIR_ACTIVITY_ID
from ..logic.phoenix_lair_logic import (
    apply_phoenix_lair_review_pure,
    phoenix_lair_view_pure,
)
from ..data.skeletal_horror_data import SKELETAL_HORROR_ACTIVITY_ID
from ..logic.skeletal_horror_logic import apply_skeletal_horror_review_pure
from ..data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID
from ..logic.tears_of_guthix_logic import apply_tears_of_guthix_review_pure
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


STRONGHOLD_UTILITY_KEY = "stronghold_of_security"


KNIGHT_WAVES_UTILITY_KEY = "knight_waves"


MAGE_ARENA_UTILITY_KEY = "mage_arena"


MAGE_ARENA_ATTUNE_PREFIX = "mage_arena_attune:"


def _handle_stronghold_answer(ctx: RuntimeActionContext) -> bool:
    """One review = one Stronghold level. Awards nothing en route; the final
    level flips the state to complete and pops the boot-choice reward dialog."""
    player_data = ctx.player_data
    info = apply_stronghold_step_pure(player_data)
    if not info["advanced"]:
        # Already cleared — nothing left to do, so switch off the activity.
        ctx.deactivate_current_skill()
        return False

    _record_action(ctx, "utility", STRONGHOLD_UTILITY_KEY, True, expected_success_chance=1.0)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()

    step = info["step"]
    if info["just_completed"]:
        ctx.deactivate_current_skill()
        ctx.show_activity_gain("Stronghold of Security cleared — claim your reward!")
        if callable(ctx.prompt_stronghold_reward):
            ctx.prompt_stronghold_reward()
    else:
        level_name = STRONGHOLD_STEP_NAMES[step - 1]
        ctx.show_activity_gain(f"Cleared the {level_name} ({step}/{STRONGHOLD_TOTAL_STEPS})")
    return True


def _handle_knight_waves_answer(ctx: RuntimeActionContext) -> bool:
    new_data, ok, info = apply_knight_waves_step_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message("Knight Waves locked", ", ".join(info.get("locked_reasons", ())))
        return False
    ctx.player_data.update(new_data)
    _record_action(ctx, "utility", KNIGHT_WAVES_UTILITY_KEY, True, expected_success_chance=1.0)
    for skill in ("Attack", "Strength", "Defence", "Constitution") if info.get("completed") else ():
        ctx.level_up_check(skill, ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if info.get("completed"):
        ctx.deactivate_current_skill()
        ctx.show_activity_gain("Knight Waves complete — Chivalry and Piety unlocked")
    else:
        ctx.show_activity_gain(f"Knight Waves: {info.get('step', 0)}/8 knights defeated")
    return True


def _handle_mage_arena_answer(ctx: RuntimeActionContext) -> bool:
    new_data, ok, info = apply_mage_arena_step_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message("Mage Arena locked", ", ".join(info.get("locked_reasons", ())))
        return False
    ctx.player_data.update(new_data)
    _record_action(ctx, "utility", MAGE_ARENA_UTILITY_KEY, True, expected_success_chance=1.0)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if info.get("completed"):
        ctx.deactivate_current_skill()
        ctx.show_activity_gain(
            f"Mage Arena complete — {str(info.get('alignment', '')).title()} cape, staff, and spell attunement claimed"
        )
    else:
        ctx.show_activity_gain(f"Mage Arena: {info.get('step', 0)}/5 Kolodion forms defeated")
    return True


def _handle_mage_arena_attunement_answer(
    ctx: RuntimeActionContext,
    activity_key: str,
) -> bool:
    god_id = activity_key.removeprefix(MAGE_ARENA_ATTUNE_PREFIX)
    new_data, ok, info = attune_mage_arena_spell_pure(ctx.player_data, god_id)
    if not ok:
        ctx.deactivate_current_skill()
        reason = str(info.get("reason", "attunement unavailable")).replace("_", " ")
        ctx.show_error_message("Mage Arena attunement locked", reason)
        return False
    ctx.player_data.clear()
    ctx.player_data.update(new_data)
    _record_action(
        ctx,
        "utility",
        activity_key,
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.deactivate_current_skill()
    ctx.show_activity_gain(
        f"{info.get('spell_name', 'God spell')} attuned for use outside the Mage Arena"
    )
    return True


def _handle_livid_farm_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_livid_farm_reviews_pure(
        ctx.player_data,
        ctx.review_action_multiplier,
        rng=ctx.random_random,
    )
    if not ok:
        locked = tuple(result.get("locked_reasons", ()))
        missing = dict(result.get("missing_runes", {}) or {})
        if locked:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Livid Farm locked",
                "Livid Farm requires " + ", ".join(map(str, locked)) + ".",
            )
        elif missing:
            _switch_material_failure_to_bankstanding(ctx)
            missing_text = ", ".join(
                f"{amount} {rune_name}"
                for rune_name, amount in missing.items()
            )
            ctx.show_error_message(
                "Out of Livid Farm runes",
                f"The next atomic review needs {missing_text}. "
                "Nothing was consumed, and AnkiScape switched to Bankstanding.",
            )
        return False

    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    xp_reward_rows = tuple(
        {"skill_id": skill_id, "amount": amount}
        for skill_id, amount in xp_rewards.items()
    )
    primary_xp = _award_action_xp_rewards(ctx, xp_reward_rows, "magic")
    _record_action(
        ctx,
        "utility",
        LIVID_FARM_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=primary_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    cycles = int(result.get("cycles", 0) or 0)
    points = int(result.get("points", 0) or 0)
    parts = [
        f"Livid Farm · {cycles} cycle{'s' if cycles != 1 else ''}",
        f"+{points:,} Produce",
    ]
    distractions = tuple(result.get("distractions", ()))
    completed_distractions = [
        row for row in distractions if row.get("completed")
    ]
    skipped_distractions = [
        row for row in distractions if not row.get("completed")
    ]
    if completed_distractions:
        parts.append(
            "distraction: "
            + ", ".join(str(row.get("display_name", "")) for row in completed_distractions)
        )
    if skipped_distractions:
        parts.append(
            "skipped unfunded "
            + ", ".join(str(row.get("display_name", "")) for row in skipped_distractions)
        )
    unlocks = tuple(result.get("new_unlocks", ()))
    if unlocks:
        parts.append(
            "unlocked "
            + ", ".join(str(row.get("display_name", "")) for row in unlocks)
        )
    ctx.show_activity_gain(" · ".join(parts))
    return True


def _handle_evil_tree_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    woodcutting_level = int(player_data.get("woodcutting_level", 1) or 1)
    has_hatchet = best_woodcutting_axe_pure(
        woodcutting_level,
        player_data.get("inventory", {}),
        player_data.get("toolbelt", {}),
        WOODCUTTING_AXE_DATA,
    ) is not None
    state = player_data.get("evil_tree")
    session = state.get("session") if isinstance(state, dict) else None
    reward_rolls = (
        tuple(ctx.random_random() for _ in range(4))
        if isinstance(session, dict) and session.get("phase") == "fell"
        else ()
    )
    updated, ok, result = apply_evil_tree_review_pure(
        player_data,
        has_usable_hatchet=has_hatchet,
        reward_rolls=reward_rolls,
    )
    if not ok:
        ctx.show_error_message(
            "Evil Tree unavailable",
            str(result.get("reason", "This Evil Tree can no longer be trained.")),
        )
        ctx.deactivate_current_skill()
        return False

    player_data.clear()
    player_data.update(updated)
    phase = str(result.get("phase", ""))
    xp = result.get("xp", {}) or {}
    outputs = result.get("outputs", {}) or {}
    if phase == "nurture":
        _record_action(
            ctx,
            "farming",
            "evil_tree_nurture",
            True,
            expected_success_chance=1.0,
            primary_xp=float(xp.get("Farming", 0.0) or 0.0),
        )
    elif phase == "prepare":
        _record_action(
            ctx,
            "woodcutting",
            "evil_tree_roots",
            True,
            expected_success_chance=1.0,
            output_items=outputs,
            primary_xp=float(xp.get("Woodcutting", 0.0) or 0.0),
        )
    elif phase == "fell":
        _record_action(
            ctx,
            "woodcutting",
            "evil_tree_fell",
            True,
            expected_success_chance=1.0,
            output_items=outputs,
            primary_xp=float(xp.get("Woodcutting", 0.0) or 0.0),
        )
        _record_action(
            ctx,
            "firemaking",
            "evil_tree_kindling",
            True,
            expected_success_chance=1.0,
            primary_xp=float(xp.get("Firemaking", 0.0) or 0.0),
        )

    for skill_name in xp:
        ctx.level_up_check(str(skill_name), player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()

    xp_text = " · ".join(
        f"+{float(amount):,.6g} {skill_name} XP"
        for skill_name, amount in xp.items()
    )
    if result.get("completed") and result.get("partial"):
        message = f"Nurtured {result['tier_name']} · {xp_text} · nurture-only visit complete"
    elif result.get("completed"):
        reward_text = ", ".join(
            f"{int(amount):,} {item_name}"
            for item_name, amount in outputs.items()
        )
        message = (
            f"Felled {result['tier_name']} · {xp_text} · {reward_text} · "
            f"blessing {int(result.get('blessing_reviews', 0))} reviews"
        )
    elif phase == "nurture":
        message = f"Nurtured {result['tier_name']} · {xp_text} · next: chop roots"
    else:
        message = f"Prepared {result['tier_name']} · {xp_text} · next: fell and burn"
    ctx.show_activity_gain(message)

    if result.get("completed"):
        ctx.deactivate_current_skill()
    return True


def _handle_big_chinchompa_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_big_chinchompa_review_pure(
        ctx.player_data,
        circuits=max(1, int(ctx.review_action_multiplier or 1)),
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Big Chinchompa unavailable",
            str(result.get("reason", "No Big Chinchompa event is active.")),
        )
        return False

    ctx.player_data.clear()
    ctx.player_data.update(updated)
    hunter_xp = float(result.get("hunter_xp", 0.0) or 0.0)
    _record_action(
        ctx,
        "utility",
        BIG_CHINCHOMPA_UTILITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=hunter_xp,
    )
    gained = _award_action_xp_rewards(
        ctx,
        ({"skill_id": "hunter", "amount": hunter_xp},),
        "hunter",
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(gained)
    point_text = (
        "point cap reached"
        if result.get("personal_cap_reached")
        else f"+{int(result.get('event_points', 0) or 0)} event points"
    )
    ctx.show_activity_gain(
        f"Released {int(result.get('moths', 0) or 0)} "
        f"{str(result.get('tier_name', 'soporith moth')).lower()}s · "
        f"{point_text} · {float(result.get('fullness_percent', 0.0)):.0f}% full"
    )
    return True


def _handle_shooting_star_answer(ctx: RuntimeActionContext) -> bool:
    mining_level = int(ctx.player_data.get("mining_level", 1) or 1)
    pickaxe = best_mining_pickaxe_pure(
        mining_level,
        ctx.player_data.get("inventory", {}),
        ctx.player_data.get("toolbelt", {}),
        MINING_PICKAXE_DATA,
    )
    bonus_state = equipment_bonus_state_pure(
        ctx.player_data.get("equipment", {}) or {},
        MINING_BONUS_ITEM_DATA,
    )
    gem_chance = (
        GLORY_GEM_DROP_CHANCE
        if bonus_state["has_glory"]
        else INCIDENTAL_GEM_DROP_CHANCE
    )
    updated, ok, result = apply_shooting_star_review_pure(
        ctx.player_data,
        has_usable_pickaxe=pickaxe is not None,
        gem_roll=ctx.random_random(),
        gem_pick_roll=ctx.random_random(),
        gem_drop_chance=gem_chance,
        gem_drop_table=INCIDENTAL_GEM_DROP_TABLE,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Shooting Star unavailable",
            str(result.get("reason", "No mineable Shooting Star is active.")),
        )
        return False

    ctx.player_data.clear()
    ctx.player_data.update(updated)
    mining_xp = float(result.get("mining_xp", 0.0) or 0.0)
    outputs: dict[str, int] = {}
    dust_added = int(result.get("dust_added", 0) or 0)
    if dust_added > 0:
        outputs["Stardust"] = dust_added
    gem = str(result.get("gem", "") or "")
    if gem:
        outputs[gem] = outputs.get(gem, 0) + 1
    if result.get("waiting"):
        _record_action(
            ctx,
            "mining",
            SHOOTING_STAR_ACTIVITY_ID,
            False,
            expected_success_chance=1.0,
            failure_kind="waiting_for_layer",
            primary_xp=mining_xp,
        )
    else:
        _record_action(
            ctx,
            "mining",
            SHOOTING_STAR_ACTIVITY_ID,
            True,
            expected_success_chance=1.0,
            output_items=outputs,
            primary_xp=mining_xp,
        )
    gained = ctx.award_skill_exp("mining_exp", mining_xp)
    ctx.level_up_check("Mining", ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)

    if result.get("waiting"):
        ctx.show_activity_gain(
            f"Size {int(result.get('current_size', 0))} requires "
            f"level {int(result.get('required_level', 0))} · "
            "waiting for public miners to expose a lower layer"
        )
    elif result.get("tag_only"):
        ctx.show_activity_gain(
            f"First-finder tag · +{mining_xp:,.6g} Mining XP · "
            "bring a pickaxe to mine stardust"
        )
        ctx.deactivate_current_skill()
    else:
        parts = [
            f"Mined size {int(result.get('mined_size', 0))} stardust",
            f"+{mining_xp:,.6g} Mining XP",
        ]
        if result.get("tag_xp"):
            parts.append("first-finder tag")
        if dust_added:
            parts.append(
                f"{int(result.get('dust_total', 0))}/200 stardust"
            )
        elif result.get("dust_cap_reached"):
            parts.append("stardust cap reached; XP continues")
        if gem:
            parts.append(f"+1 {gem}")
        if result.get("sprite_released"):
            parts.append("Star sprite released")
            ctx.deactivate_current_skill()
        ctx.show_activity_gain(" · ".join(parts))
    return True


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


def _handle_fight_caves_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_fight_caves_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fight Cave unavailable",
            str(result.get("reason", "Enter the Fight Cave before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        FIGHT_CAVES_ACTIVITY_ID,
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
    ctx.show_activity_gain(str(result.get("status", "Fight Cave review complete")))
    return True


def _handle_phoenix_lair_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_phoenix_lair_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Phoenix Lair unavailable",
            str(result.get("reason", "Enter the Phoenix Lair before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        PHOENIX_LAIR_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=total_xp,
    )
    _refresh_combat_levels(ctx, xp_rewards)
    for exp_key, skill_name in {
        "firemaking_exp": "Firemaking",
        "fletching_exp": "Fletching",
        "crafting_exp": "Crafting",
        "slayer_exp": "Slayer",
    }.items():
        if float(xp_rewards.get(exp_key, 0.0) or 0.0) > 0:
            ctx.level_up_check(skill_name, ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "Phoenix Lair review complete")))
    return True


def _handle_skeletal_horror_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_skeletal_horror_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Skeletal Horror unavailable",
            str(result.get("reason", "Enter the lair before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        SKELETAL_HORROR_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        failure_kind="safe_death" if result.get("died") else None,
        primary_xp=total_xp,
        output_items=(
            {"Clue scroll (elite)": 1}
            if result.get("clue_dropped")
            else None
        ),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    for exp_key, skill_name in {
        "slayer_exp": "Slayer",
        "prayer_exp": "Prayer",
    }.items():
        if float(xp_rewards.get(exp_key, 0.0) or 0.0) > 0:
            ctx.level_up_check(skill_name, ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(
        str(result.get("status", "Skeletal Horror review complete"))
    )
    return True


def _handle_tears_of_guthix_answer(ctx: RuntimeActionContext) -> bool:
    """One answered card is one collection beat; the multiplier repeats beats."""
    updated, ok, result = apply_tears_of_guthix_review_pure(
        ctx.player_data,
        ctx.random_random,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Tears of Guthix unavailable",
            str(result.get("reason", "Enter Juna's cavern before collecting.")),
        )
        return False
    for _ in range(max(1, int(ctx.review_action_multiplier or 1)) - 1):
        if result.get("completed"):
            break
        updated, repeated_ok, repeated = apply_tears_of_guthix_review_pure(
            updated,
            ctx.random_random,
        )
        if not repeated_ok:
            break
        result = repeated
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        TEARS_OF_GUTHIX_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=total_xp,
    )
    if result.get("reward_skill_name"):
        ctx.level_up_check(str(result["reward_skill_name"]), ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "Tears collected")))
    return True


def _handle_barrows_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_barrows_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Barrows unavailable",
            str(result.get("reason", "Enter or resume Barrows before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        BARROWS_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=total_xp,
        output_items=dict(result.get("rewards", {}) or {}),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("complete") or result.get("outcome") == "death":
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "Barrows review complete")))
    return True


def _handle_stealing_creation_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_stealing_creation_review_pure(
        ctx.player_data,
        ctx.random_random,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Stealing Creation unavailable",
            str(result.get("reason", "Enter Stealing Creation before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        STEALING_CREATION_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if result.get("complete"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(
        str(result.get("status", "Stealing Creation duty complete"))
    )
    return True


def _handle_sorceress_garden_answer(ctx: RuntimeActionContext) -> bool:
    view = sorceress_garden_view_pure(ctx.player_data)
    harvest = str(view.get("harvest_mode", "fruit"))
    if harvest == "alternate":
        harvest = str(view.get("alternate_next", "fruit"))
    herb_rolls = (
        (ctx.random_random(), ctx.random_random())
        if harvest == "herbs"
        else ()
    )
    updated, result = apply_sorceress_garden_review_pure(
        ctx.player_data,
        herb_rolls,
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Sorceress's Garden locked",
            "Requires " + ", ".join(result.get("locked_reasons", ())),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    farming_xp = float(result.get("farming_xp", 0.0) or 0.0)
    thieving_xp = float(result.get("thieving_xp", 0.0) or 0.0)
    gained = ctx.award_skill_exp("farming_exp", farming_xp)
    ctx.level_up_check("Farming", ctx.player_data)
    if thieving_xp > 0:
        ctx.award_skill_exp("thieving_exp", thieving_xp)
        ctx.level_up_check("Thieving", ctx.player_data)
    _record_action(
        ctx,
        "farming",
        str(result.get("action_id", SORCERESS_GARDEN_ACTIVITY_ID)),
        True,
        expected_success_chance=1.0,
        output_items=dict(result.get("outputs", {}) or {}),
        primary_xp=farming_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Garden trip complete")))
    return True


def _handle_penguin_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_penguin_review_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Penguin Hide and Seek unavailable",
            str(result.get("reason", "Select an unspotted penguin first.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        str(result.get("action_id", PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID)),
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("status", "Penguin spied")))
    return True


def _handle_vinesweeper_answer(ctx: RuntimeActionContext) -> bool:
    operations = max(1, int(ctx.review_action_multiplier or 1))
    updated, result = apply_vinesweeper_review_pure(
        ctx.player_data,
        tuple(ctx.random_random() for _ in range(operations)),
        operations=operations,
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Vinesweeper unavailable",
            str(result.get("reason", "Enter Winkin's Farm before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    hunter_xp = float(result.get("hunter_xp", 0.0) or 0.0)
    gained = 0.0
    if hunter_xp > 0:
        gained = ctx.award_skill_exp("hunter_exp", hunter_xp)
        ctx.level_up_check("Hunter", ctx.player_data)
    completed = int(result.get("completed_operations", 0) or 0)
    if completed:
        _record_action(
            ctx,
            "utility",
            VINESWEEPER_ACTIVITY_ID,
            True,
            expected_success_chance=1.0,
            primary_xp=hunter_xp,
        )
    if result.get("paused"):
        ctx.deactivate_current_skill()
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(
        str(result.get("status", "Vinesweeper operation complete"))
    )
    return True


def handle_flash_powder_factory_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, result = apply_flash_powder_factory_review_pure(
        ctx.player_data,
        tuple(ctx.random_random() for _ in range(4)) if productive else (),
        productive=productive,
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Flash Powder Factory unavailable",
            str(result.get("reason", "Enter the factory before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        FLASH_POWDER_FACTORY_ACTIVITY_ID,
        bool(result.get("success", False)),
        expected_success_chance=1.0,
        output_items=result.get("outputs") or {},
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("status", "Flash powder circuit complete"))
    )
    if result.get("completed_activity"):
        ctx.deactivate_current_skill()
    return True


def _handle_pyramid_plunder_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_pyramid_plunder_review_pure(
        ctx.player_data,
        ctx.random_random,
        rooms=max(1, int(ctx.review_action_multiplier or 1)),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Pyramid Plunder unavailable",
            str(result.get("reason", "Enter Pyramid Plunder before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp = result.get("xp") or {}
    gained = 0.0
    for skill_id, label in (
        ("thieving", "Thieving"),
        ("strength", "Strength"),
        ("runecrafting", "Runecrafting"),
    ):
        amount = float(xp.get(skill_id, 0.0) or 0.0)
        if amount > 0:
            gained += ctx.award_skill_exp(f"{skill_id}_exp", amount)
            ctx.level_up_check(label, ctx.player_data)
    _record_action(
        ctx,
        "utility",
        PYRAMID_PLUNDER_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=float(xp.get("thieving", 0.0) or 0.0),
        output_items=result.get("outputs") or {},
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Pyramid Plunder room resolved")))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_werewolf_skullball_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_werewolf_skullball_review_pure(ctx.player_data)
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Werewolf Skullball unavailable",
            str(result.get("reason", "Enter Werewolf Skullball before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp = float(result.get("xp", 0.0) or 0.0)
    gained = ctx.award_skill_exp("agility_exp", xp) if xp > 0 else 0.0
    if xp > 0:
        ctx.level_up_check("Agility", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        WEREWOLF_SKULLBALL_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Werewolf Skullball run complete")))
    ctx.deactivate_current_skill()
    return True


def _handle_gnome_ball_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_gnome_ball_review_pure(
        ctx.player_data,
        ctx.random_random(),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Gnome Ball unavailable",
            str(result.get("reason", "Enter Gnome Ball before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    agility_xp = float(result.get("agility_xp", 0.0) or 0.0)
    ranged_xp = float(result.get("ranged_xp", 0.0) or 0.0)
    gained = 0.0
    if agility_xp > 0:
        gained += ctx.award_skill_exp("agility_exp", agility_xp)
        ctx.level_up_check("Agility", ctx.player_data)
    if ranged_xp > 0:
        gained += ctx.award_skill_exp("ranged_exp", ranged_xp)
        ctx.level_up_check("Ranged", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        GNOME_BALL_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=float(
            result.get("expected_success_chance", 1.0) or 0.0
        ),
        output_items=result.get("outputs") or {},
        failure_kind="death" if result.get("died") else None,
        primary_xp=agility_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Gnome Ball beat resolved")))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_fish_flingers_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_fish_flingers_review_pure(
        ctx.player_data,
        ctx.random_random(),
        ctx.random_random(),
        ctx.random_random(),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fish Flingers unavailable",
            str(result.get("reason", "Enter Fish Flingers before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    base_xp = float(result.get("xp", 0.0) or 0.0)
    awarded_xp = base_xp * fishing_outfit_multiplier_pure(ctx.player_data)
    gained = 0.0
    if awarded_xp > 0:
        gained = ctx.award_skill_exp("fishing_exp", awarded_xp)
        ctx.level_up_check("Fishing", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        FISH_FLINGERS_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=awarded_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(
        str(result.get("status", "Fish Flingers catch resolved"))
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_fishing_trawler_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_fishing_trawler_review_pure(
        ctx.player_data,
        ctx.random_random(),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fishing Trawler unavailable",
            str(result.get("reason", "Board the trawler before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    base_xp = float(result.get("xp", 0.0) or 0.0)
    awarded_xp = base_xp * fishing_outfit_multiplier_pure(ctx.player_data)
    gained = 0.0
    if awarded_xp > 0:
        gained = ctx.award_skill_exp("fishing_exp", awarded_xp)
        ctx.level_up_check("Fishing", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        FISHING_TRAWLER_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=1.0,
        output_items=result.get("outputs") or {},
        failure_kind="sunk" if result.get("sunk") else None,
        primary_xp=awarded_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(
        str(result.get("status", "Fishing Trawler duty resolved"))
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_great_orb_project_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_great_orb_project_review_pure(
        ctx.player_data,
        ctx.random_random(),
        ctx.random_random(),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Great Orb Project unavailable",
            str(result.get("reason", "Enter the Great Orb Project before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = 0.0
    if base_xp > 0:
        gained = ctx.award_skill_exp("runecrafting_exp", base_xp)
        ctx.level_up_check("Runecrafting", ctx.player_data)
    output_item = str(result.get("output_item", ""))
    output_quantity = int(result.get("output_quantity", 0) or 0)
    outputs = {output_item: output_quantity} if output_item and output_quantity else {}
    _record_action(
        ctx,
        "utility",
        GREAT_ORB_PROJECT_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=float(
            result.get("expected_success_chance", 0.5) or 0.0
        ),
        output_items=outputs,
        primary_xp=base_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(
        str(result.get("status", "Great Orb Project round resolved"))
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_court_cases_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_court_case_review_pure(ctx.player_data)
    if not result.get("allowed"):
        ctx.show_error_message(
            "Court Cases awaiting a choice",
            str(result.get("reason", "Open a court case before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = 0.0
    xp_skill = str(result.get("xp_skill", ""))
    if base_xp > 0 and xp_skill in {"attack", "defense"}:
        gained = ctx.award_skill_exp(f"{xp_skill}_exp", base_xp)
        ctx.level_up_check(
            "Attack" if xp_skill == "attack" else "Defence",
            ctx.player_data,
        )
    _record_action(
        ctx,
        "utility",
        COURT_CASES_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=float(
            result.get("expected_success_chance", 1.0) or 0.0
        ),
        output_items={
            str(item): int(amount)
            for item, amount in dict(result.get("rewards") or {}).items()
        },
        primary_xp=base_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Court case advanced")))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_circus_answer(ctx: RuntimeActionContext) -> bool:
    view = circus_view_pure(ctx.player_data)
    selected_id = str(view.get("selected_performance", "agility"))
    selected_row = next(
        (
            row
            for row in view.get("performances", ())
            if str(row.get("id", "")) == selected_id
        ),
        {},
    )
    routine = tuple(selected_row.get("routine", ()))
    attempts = (
        len(routine)
        if view.get("automation_mode") == "advanced" and routine
        else int(selected_row.get("max_attempts", 10) or 10)
    )
    updated, result = apply_circus_review_pure(
        ctx.player_data,
        tuple(ctx.random_random() for _ in range(attempts)),
    )
    if not result.get("allowed"):
        ctx.show_error_message(
            "Big Top Bonanza unavailable",
            str(result.get("reason", "Choose an available Circus performance.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    skill_id = str(result.get("skill_id", ""))
    skill_rows = {
        "magic": ("magic_exp", "Magic"),
        "ranged": ("ranged_exp", "Ranged"),
        "agility": ("agility_exp", "Agility"),
        "firemaking": ("firemaking_exp", "Firemaking"),
        "thieving": ("thieving_exp", "Thieving"),
    }
    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = 0.0
    if base_xp > 0 and skill_id in skill_rows:
        exp_key, display_name = skill_rows[skill_id]
        gained = ctx.award_skill_exp(exp_key, base_xp)
        ctx.level_up_check(display_name, ctx.player_data)
    _record_action(
        ctx,
        "utility",
        CIRCUS_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=float(
            result.get("expected_success_chance", 0.0) or 0.0
        ),
        output_items={
            str(item): int(amount)
            for item, amount in dict(result.get("outputs") or {}).items()
        },
        primary_xp=base_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Circus performance resolved")))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_trouble_brewing_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    view = trouble_brewing_view_pure(ctx.player_data)
    duty = str(view.get("policy", {}).get("duty", "water"))
    session = view.get("session")
    if isinstance(session, dict):
        duty = str(session.get("duty", duty))
    updated, result = apply_trouble_brewing_review_pure(
        ctx.player_data,
        productive=productive,
        duty=duty,
        opponent_roll=ctx.random_random(),
        sabotage_roll=ctx.random_random(),
    )
    if result.get("reason"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Trouble Brewing unavailable",
            str(result["reason"]),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    skill_rows = {
        "agility": ("agility_exp", "Agility"),
        "cooking": ("cooking_exp", "Cooking"),
        "crafting": ("crafting_exp", "Crafting"),
        "firemaking": ("firemaking_exp", "Firemaking"),
        "woodcutting": ("woodcutting_exp", "Woodcutting"),
    }
    total_gained = 0.0
    skill_xp = dict(result.get("skill_xp") or {})
    for skill_id, amount in skill_xp.items():
        if skill_id not in skill_rows or float(amount or 0.0) <= 0:
            continue
        exp_key, display_name = skill_rows[skill_id]
        total_gained += ctx.award_skill_exp(exp_key, float(amount))
        ctx.level_up_check(display_name, ctx.player_data)
    _record_action(
        ctx,
        "utility",
        TROUBLE_BREWING_ACTIVITY_ID,
        productive,
        expected_success_chance=1.0,
        primary_xp=sum(float(value or 0.0) for value in skill_xp.values()),
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_gained > 0:
        ctx.show_exp(total_gained)
    ctx.show_activity_gain(str(result.get("message", "Trouble Brewing beat resolved")))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


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
    for exp_key, amount in xp_rewards.items():
        updated[exp_key] = float(updated.get(exp_key, 0.0) or 0.0) + float(amount)
    ctx.player_data.clear()
    ctx.player_data.update(updated)
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


def handle_pest_control_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    view = pest_control_view_pure(ctx.player_data)
    duty: str | None = None
    session = view.get("pest_control")
    if isinstance(session, dict) and session.get("automation_mode") == "advanced":
        duty = str(session.get("duty", duty))
    updated, ok, result = apply_pest_control_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
        duty=duty,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Pest Control unavailable",
            str(result.get("reason", "Enter Pest Control before training.")),
        )
        return False
    xp_rewards = dict(result.get("xp_rewards") or {})
    for exp_key, amount in xp_rewards.items():
        updated[exp_key] = float(updated.get(exp_key, 0.0) or 0.0) + float(amount)
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        PEST_CONTROL_ACTIVITY_ID,
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
    ctx.show_activity_gain(
        str(result.get("message") or result.get("status") or "Pest Control beat resolved")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_barbarian_assault_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_barbarian_assault_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Barbarian Assault unavailable",
            str(result.get("reason", "Enter Barbarian Assault before training.")),
        )
        return False
    xp_rewards = dict(result.get("xp_rewards") or {})
    for exp_key, amount in xp_rewards.items():
        updated[exp_key] = float(updated.get(exp_key, 0.0) or 0.0) + float(amount)
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        BARBARIAN_ASSAULT_ACTIVITY_ID,
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
    ctx.show_activity_gain(
        str(
            result.get("message")
            or result.get("status")
            or "Barbarian Assault beat resolved"
        )
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_varrock_museum_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_varrock_museum_review_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Varrock Museum unavailable",
            str(result.get("reason", "Choose an unfinished museum route.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        VARROCK_MUSEUM_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("status") or "Varrock Museum landmark completed")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_stronghold_player_safety_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_stronghold_player_safety_review_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Stronghold of Player Safety unavailable",
            str(result.get("reason", "Choose an unfinished Stronghold landmark.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("status") or "Stronghold landmark completed")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_soul_wars_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_soul_wars_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Soul Wars unavailable",
            str(result.get("reason", "Enter Soul Wars before training.")),
        )
        return False
    xp_rewards = dict(result.get("xp_rewards") or {})
    for exp_key, amount in xp_rewards.items():
        updated[exp_key] = float(updated.get(exp_key, 0.0) or 0.0) + float(amount)
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        SOUL_WARS_ACTIVITY_ID,
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
    ctx.show_activity_gain(
        str(result.get("message") or "Soul Wars beat resolved")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_shades_of_mortton_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_shades_of_mortton_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
        population=str(ctx.player_data.get("world_population_profile", "normal")),
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Shades of Mort'ton unavailable",
            str(result.get("reason", "Enter Shades of Mort'ton before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    skill_rows = {
        "crafting": ("crafting_exp", "Crafting"),
        "firemaking": ("firemaking_exp", "Firemaking"),
        "prayer": ("prayer_exp", "Prayer"),
    }
    total_gained = 0.0
    skill_xp = dict(result.get("skill_xp") or {})
    combat_xp = dict(result.get("xp_rewards") or {})
    for skill_id, amount in skill_xp.items():
        if skill_id not in skill_rows or float(amount or 0.0) <= 0:
            continue
        exp_key, display_name = skill_rows[skill_id]
        total_gained += ctx.award_skill_exp(exp_key, float(amount))
        ctx.level_up_check(display_name, ctx.player_data)
    _record_action(
        ctx,
        "utility",
        SHADES_OF_MORTTON_ACTIVITY_ID,
        productive,
        expected_success_chance=1.0,
        failure_kind="dangerous_combat_death" if result.get("died") else None,
        primary_xp=(
            sum(float(value or 0.0) for value in skill_xp.values())
            + sum(float(value or 0.0) for value in combat_xp.values())
        ),
    )
    _refresh_combat_levels(ctx, combat_xp)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_gained > 0:
        ctx.show_exp(total_gained)
    ctx.show_activity_gain(
        str(result.get("status") or "Shades of Mort'ton beat resolved")
    )
    return True


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
    _record_action(
        ctx,
        "utility",
        TZHAAR_FIGHT_PIT_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        failure_kind="safe_death" if result.get("outcome") == "loss" else None,
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


def _handle_managing_miscellania_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_managing_miscellania_review_pure(ctx.player_data)
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Managing Miscellania unavailable",
            str(result.get("reason", "No approval work is available.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = ctx.award_skill_exp("woodcutting_exp", base_xp)
    ctx.level_up_check("Woodcutting", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        MANAGING_MISCELLANIA_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=base_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Kingdom approval increased")))
    if not managing_miscellania_view_pure(ctx.player_data).get("can_train", False):
        ctx.deactivate_current_skill()
    return True


def handle_agility_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target_id = str(player_data.get("current_agility", DEFAULT_AGILITY_TARGET))
    if target_id == FLASH_POWDER_FACTORY_ACTIVITY_ID:
        return handle_flash_powder_factory_answer(ctx)
    if target_id not in AGILITY_TARGETS_BY_ID:
        target_id = DEFAULT_AGILITY_TARGET
        player_data["current_agility"] = target_id
    locked = agility_target_locked_reasons_pure(player_data, target_id)
    if locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Agility target locked",
            f"{AGILITY_TARGETS_BY_ID[target_id].display_name} requires {', '.join(locked)}, so Agility has been switched off.",
        )
        return False

    lap_counts_before = dict(sanitize_agility_state_pure(player_data)["agility_lap_counts"])
    pit_offer_before = bool(player_data.get("agility_pit_offer", False))
    pit_origin_before = str(player_data.get("agility_pit_origin_course", "") or "")
    current_agility_before = str(player_data.get("current_agility", target_id) or target_id)
    equipment_before = dict(player_data.get("equipment", {}) or {})
    inventory_before = dict(player_data.get("inventory", {}) or {})
    xp_charges_before = dict(player_data.get("agility_effect_charges", {}) or {})
    updated, result = apply_agility_review_pure(
        player_data,
        tuple(ctx.random_random() for _ in range(4)),
    )
    if not result.get("allowed"):
        return False
    player_data.clear()
    player_data.update(updated)

    damage = int(result.get("damage", 0) or 0)
    if damage > 0:
        wilderness_ambush = bool((result.get("wilderness_ambush") or {}).get("triggered"))
        deferred_pit_accept = bool(
            wilderness_ambush
            and result.get("completed_lap")
            and player_data.get("current_agility") == "the_pit"
            and player_data.get("agility_pit_offer")
        )
        if deferred_pit_accept:
            # The Wilderness ambush resolves before the lap reward. Restore the
            # pre-entry carried state so a fatal hit cannot bank-protect hand
            # equipment by auto-accepting The Pit one transaction too early.
            player_data["current_agility"] = current_agility_before
            player_data["agility_pit_origin_course"] = pit_origin_before
            player_data["equipment"] = equipment_before
            player_data["inventory"] = inventory_before
        damaged, damage_result = apply_thieving_damage_pure(
            player_data,
            damage,
            source="agility_wilderness_pker" if wilderness_ambush else "agility_failure",
            carried_target_id=target_id,
        )
        player_data.clear()
        player_data.update(damaged)
        result["damage_result"] = damage_result
        if deferred_pit_accept and not damage_result.get("died"):
            accepted, accept_result = apply_agility_command_pure(
                player_data,
                "accept_pit_offer",
                {},
            )
            if accept_result.get("allowed"):
                player_data.clear()
                player_data.update(accepted)
        if damage_result.get("died"):
            ctx.deactivate_current_skill()
            if wilderness_ambush and result.get("completed_lap"):
                player_data["agility_lap_counts"] = lap_counts_before
                player_data["agility_pit_offer"] = pit_offer_before
                player_data["agility_pit_origin_course"] = pit_origin_before
                player_data["current_agility"] = current_agility_before
                charges = dict(player_data.get("agility_effect_charges", {}) or {})
                for modifier in result.get("xp_modifiers", ()) or ():
                    item_name = modifier.get("item") if isinstance(modifier, dict) else None
                    if not isinstance(item_name, str):
                        continue
                    if item_name in xp_charges_before:
                        charges[item_name] = xp_charges_before[item_name]
                    else:
                        charges.pop(item_name, None)
                player_data["agility_effect_charges"] = charges
                result.update({
                    "xp": 0.0,
                    "base_xp": 0.0,
                    "xp_modifiers": (),
                    "success": False,
                    "completed_lap": False,
                    "failure_kind": "wilderness_pker_death",
                    "reward_forfeited": True,
                })
                death_status = "Wilderness PKer ambush · died before the lap reward"
                player_data["agility_status"] = death_status
                result["status"] = death_status

    outputs = {
        str(item): int(quantity)
        for item, quantity in (result.get("outputs") or {}).items()
        if int(quantity) > 0
    }
    if outputs:
        inventory = dict(player_data.get("inventory", {}) or {})
        for item, quantity in outputs.items():
            inventory[item] = int(inventory.get(item, 0) or 0) + quantity
        player_data["inventory"] = inventory

    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = ctx.award_skill_exp("agility_exp", base_xp) if base_xp > 0 else 0.0
    if base_xp > 0:
        ctx.level_up_check("Agility", player_data)
    cross_rewards = tuple(
        {"skill_id": str(skill_id), "amount": float(amount)}
        for skill_id, amount in (result.get("cross_skill_rewards") or ())
        if float(amount) > 0
    )
    if cross_rewards:
        _award_action_xp_rewards(ctx, cross_rewards, str(cross_rewards[0]["skill_id"]))
    achievement_outputs = dict(outputs)
    tickets = int(result.get("tickets", 0) or 0)
    if tickets > 0:
        achievement_outputs["Agility arena ticket"] = tickets
    _record_action(
        ctx,
        "agility",
        str(result.get("action_id", target_id)),
        bool(result.get("success")),
        expected_success_chance=result.get("expected_success_chance"),
        output_items=outputs,
        achievement_output_items=achievement_outputs,
        failure_kind=result.get("failure_kind"),
        primary_xp=base_xp,
    )
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", player_data.get("agility_status", "Agility action complete"))))
    damage_result = result.get("damage_result") or {}
    if damage_result.get("died"):
        cause = "Wilderness PKer ambush" if (result.get("wilderness_ambush") or {}).get("triggered") else "Agility failure"
        ctx.show_activity_gain(f"☠ YOU DIED — {cause}; carried pack and gear moved to grave")
    elif damage_result.get("food_used"):
        food = damage_result["food_used"]
        ctx.show_activity_gain(f"Auto-ate {food['item']} (+{food['healed_by']} LP)")
    return True
