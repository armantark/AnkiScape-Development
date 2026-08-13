"""runtime_actions_gathering.py - split out of runtime_actions.py; see that module's header."""

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
from ..logic.cape_logic import effective_roll_level_pure
from ..logic.summoning_logic import (
    apply_summoning_training_action_pure,
    familiar_effective_roll_level_pure,
    restore_summoning_points_pure,
    summoning_action_locked_reasons_pure,
    summoning_action_requirements_pure,
)
from ..logic.slayer_logic import apply_slayer_kills_pure
from ..logic import inventory_pure
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

from .runtime_actions_shared import (  # noqa: F401  (re-export)
    _COMBAT_EXP_SKILLS,
    _admit_live_cadence,
    _apply_farming_queue_result,
    _award_action_xp_rewards,
    _apply_brawling_actions,
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

from .runtime_actions_shared import (
    _award_action_xp_rewards,
    _charge_urn_for_action,
    _combined_success_probability,
    _record_action,
    _switch_material_failure_to_bankstanding,
    fishing_materials_text,
    missing_materials_text,
)

from .runtime_actions_context import (
    RuntimeActionContext,
)


def handle_fishing_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_fishing", DEFAULT_FISHING_TARGET)
    if target not in FISHING_DATA:
        target = DEFAULT_FISHING_TARGET
        player_data["current_fishing"] = target
    spec = FISHING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("fishing_level", 1)
    success_level = effective_roll_level_pure(
        player_data, "fishing", player_level
    )
    strength_level = player_data.get("strength_level", 1)
    agility_level = player_data.get("agility_level", 1)
    inventory = player_data.get("inventory", {})

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Fishing to {str(display_name).lower()}.")
        return False

    if not has_fishing_bait_pure(inventory, spec):
        missing = fishing_materials_text(spec, inventory)
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to {str(display_name).lower()}, so AnkiScape "
            "switched to Bankstanding. Choose another target when you are ready.",
        )
        return False

    eligible = eligible_fishing_fish_pure(spec, player_level, strength_level, agility_level)
    if not eligible:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Insufficient level",
            f"You do not meet the side-level requirements for {display_name}, so Fishing has been switched off.",
        )
        return False
    locked_reasons = fishing_method_locked_reasons_pure(player_data, target, FISHING_DATA, QUEST_UNLOCK_RULES)
    if locked_reasons:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fishing target locked",
            f"{display_name} requires {', '.join(locked_reasons)}, so Fishing has been switched off.",
        )
        return False

    expected_success = (
        1.0
        if ctx.cadence_forced_opportunity
        else _combined_success_probability(
            calculate_fishing_success_probability_pure(success_level, fish)
            for fish in eligible
        )
    )
    rolls = (
        [0.0 for _ in eligible]
        if ctx.cadence_forced_opportunity
        else [ctx.random_random() for _ in eligible]
    )
    new_inv, base_exp, ok, _output_item, xp_rewards = apply_fishing_action_pure(
        target,
        inventory,
        FISHING_DATA,
        player_level,
        strength_level,
        agility_level,
        rolls=rolls,
        success_level=success_level,
    )
    if not ok:
        _record_action(ctx, "fishing", target, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()
        return True

    output_qty = 1
    double_chance = fishing_agility_double_catch_chance_pure(_output_item, agility_level)
    if double_chance > 0 and ctx.random_random() < double_chance and _output_item:
        new_inv = dict(new_inv)
        new_inv[_output_item] = int(new_inv.get(_output_item, 0) or 0) + 1
        output_qty = 2

    outfit_multiplier = fishing_outfit_multiplier_pure(player_data)
    if outfit_multiplier > 1.0:
        base_exp *= outfit_multiplier
        xp_rewards = tuple(
            {
                **reward,
                "amount": float(reward.get("amount", 0.0) or 0.0)
                * outfit_multiplier,
            }
            if str(reward.get("skill_id", "")) == "fishing"
            else reward
            for reward in xp_rewards
        )

    player_data["inventory"] = new_inv
    _charge_urn_for_action(ctx, "fishing", target, spec, base_exp, _output_item)
    base_exp, _glove_events, _risk_events = _apply_brawling_actions(
        ctx, "fishing", target, (base_exp,)
    )
    xp_rewards = tuple(
        {**reward, "amount": base_exp}
        if str(reward.get("skill_id", "")) == "fishing"
        else reward
        for reward in xp_rewards
    )
    _record_action(
        ctx,
        "fishing",
        target,
        True,
        expected_success_chance=expected_success,
        output_item=_output_item,
        output_qty=output_qty,
        primary_xp=base_exp,
    )
    exp_gained = _award_action_xp_rewards(
        ctx,
        xp_rewards or ({"skill_id": "fishing", "amount": base_exp},),
        "fishing",
    )
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_hunter_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_hunter", DEFAULT_HUNTER_TARGET)
    if target not in HUNTER_DATA:
        target = DEFAULT_HUNTER_TARGET
        player_data["current_hunter"] = target
    spec = HUNTER_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("hunter_level", 1)
    success_level = effective_roll_level_pure(
        player_data, "hunter", player_level
    )
    inventory = player_data.get("inventory", {})

    locked_reasons = hunter_target_locked_reasons_pure(player_data, target, HUNTER_DATA, QUEST_UNLOCK_RULES)
    unlock_locked = tuple(
        reason
        for reason in locked_reasons
        if reason not in {"materials"} and not str(reason).startswith("Hunter level")
    )
    if unlock_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Hunter target locked",
            f"{display_name} requires {', '.join(unlock_locked)}, so Hunter has been switched off.",
        )
        return False

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Hunter to {str(display_name).lower()}.")
        return False

    if not has_hunter_materials_pure(target, inventory, HUNTER_DATA):
        missing = missing_materials_text(spec.get("requirements", {}), inventory)
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to {str(display_name).lower()}, so AnkiScape "
            "switched to Bankstanding. Choose another target when you are ready.",
        )
        return False

    expected_success = (
        1.0
        if ctx.cadence_forced_opportunity
        else calculate_hunter_success_probability_pure(success_level, spec)
    )
    new_inv, base_exp, ok, _output_item, xp_rewards = apply_hunter_action_pure(
        target,
        inventory,
        HUNTER_DATA,
        player_level,
        0.0 if ctx.cadence_forced_opportunity else ctx.random_random(),
        success_level,
        ctx.random_random() if spec.get("secondary_outputs") else None,
        ctx.random_random() if spec.get("secondary_outputs") else None,
    )
    if not ok:
        _record_action(ctx, "hunter", target, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()
        return True

    player_data["inventory"] = new_inv
    actual_gains = inventory_pure.inventory_delta_gains(inventory, new_inv)
    produced_outputs = _spec_output_items(spec, _output_item)
    produced_outputs.update(
        {
            item_name: amount
            for item_name, amount in actual_gains.items()
            if item_name not in produced_outputs
        }
    )
    passive_data, retained_outputs, bonecrusher_info = intercept_bonecrusher_outputs_pure(
        player_data,
        target,
        produced_outputs,
    )
    player_data.clear()
    player_data.update(passive_data)
    if bonecrusher_info["consumed"]:
        inventory = dict(player_data.get("inventory", {}) or {})
        for item_name, amount in bonecrusher_info["consumed"].items():
            inventory[item_name] = max(0, int(inventory.get(item_name, 0) or 0) - int(amount))
        player_data["inventory"] = inventory
    ticketed, quota_ticket = consume_hunter_quota_ticket_pure(
        player_data,
        str(target),
    )
    player_data.clear()
    player_data.update(ticketed)
    _record_action(
        ctx,
        "hunter",
        target,
        True,
        expected_success_chance=expected_success,
        output_items=retained_outputs,
        primary_xp=base_exp,
    )
    player_data["hunter_success_count"] = player_data.get("hunter_success_count", 0) + 1
    action_rewards = list(xp_rewards or ({"skill_id": "hunter", "amount": base_exp},))
    if bonecrusher_info["prayer_xp"]:
        action_rewards.append({"skill_id": "prayer", "amount": bonecrusher_info["prayer_xp"]})
    exp_gained = _award_action_xp_rewards(
        ctx,
        action_rewards,
        "hunter",
    )
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    if quota_ticket:
        remaining = int(
            (player_data.get("inventory", {}) or {}).get(quota_ticket, 0)
            or 0
        )
        ctx.show_activity_gain(
            f"Private ground catch · used 1 {quota_ticket} · "
            f"{remaining} remaining"
        )
    return True


def handle_woodcutting_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    tree = player_data.get("current_tree", DEFAULT_WOODCUTTING_TARGET)
    if tree not in TREE_DATA:
        tree = DEFAULT_WOODCUTTING_TARGET
        player_data["current_tree"] = tree
    spec = TREE_DATA[tree]
    player_level = player_data.get("woodcutting_level", 1)
    success_level = effective_roll_level_pure(
        player_data, "woodcutting", player_level
    )

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Woodcutting to chop {spec.get('display_name', tree)}.")
        return False

    locked_reasons = woodcutting_target_locked_reasons_pure(
        player_data,
        tree,
        TREE_DATA,
        WOODCUTTING_AXE_DATA,
        QUEST_UNLOCK_RULES,
    )
    if spec.get("action_type") != "processing":
        locked_reasons = tuple(
            reason for reason in locked_reasons if reason != "no usable hatchet"
        )
    if locked_reasons:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Woodcutting target locked",
            f"{spec.get('display_name', tree)} requires "
            f"{', '.join(locked_reasons)}, so Woodcutting has been switched off.",
        )
        return False

    if spec.get("action_type") == "processing":
        new_inv, base_exp, ok, output_item = (
            apply_woodcutting_processing_action_pure(
                tree,
                player_data.get("inventory", {}),
                TREE_DATA,
                player_level,
            )
        )
        if not ok:
            return False
        player_data["inventory"] = new_inv
        output_quantity = max(1, int(spec.get("output_quantity", 1) or 1))
        _record_action(
            ctx,
            "woodcutting",
            tree,
            True,
            expected_success_chance=1.0,
            output_items={str(output_item): output_quantity},
            primary_xp=base_exp,
        )
        exp_gained = ctx.award_skill_exp("woodcutting_exp", base_exp)
        ctx.level_up_check("Woodcutting", player_data)
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.show_activity_gain(
            f"Split 1 Arctic pine log into {output_quantity} Split log"
        )
        ctx.show_exp(exp_gained)
        return True

    axe_spec = best_woodcutting_axe_pure(
        player_level,
        player_data.get("inventory", {}),
        player_data.get("toolbelt", {}),
        WOODCUTTING_AXE_DATA,
    )
    if axe_spec is None:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "No usable hatchet",
            "You need a usable hatchet to train Woodcutting. Woodcutting has been switched off.",
        )
        return False

    r_action = 0.0 if ctx.cadence_forced_opportunity else ctx.random_random()
    r_nest_drop = ctx.random_random()
    r_nest_type = ctx.random_random()
    r_inferno_adze = ctx.random_random() if axe_spec.get("incinerates_logs", False) and spec.get("output_item") else None
    evil_tree_state = player_data.get("evil_tree")
    if not isinstance(evil_tree_state, dict):
        evil_tree_state = {}
    blessing_active = bool(
        tree in EVIL_TREE_ELIGIBLE_BLESSING_TARGETS
        and int(
            evil_tree_state.get("blessing_reviews_remaining", 0) or 0
        )
        > 0
    )
    nest_drop_chance = min(
        1.0,
        BIRD_NEST_DROP_CHANCE
        * (EVIL_TREE_NEST_MULTIPLIER if blessing_active else 1.0),
    )
    expected_success = (
        1.0
        if ctx.cadence_forced_opportunity
        else calculate_woodcutting_success_probability_pure(
            success_level, spec, axe_spec
        )
    )
    new_inv, base_exp, ok, output_item, nest_item = apply_woodcutting_action_pure(
        tree,
        player_data.get("inventory", {}),
        TREE_DATA,
        player_level,
        axe_spec,
        r_action,
        r_nest_drop,
        r_nest_type,
        BIRD_NEST_DROP_TABLE,
        nest_drop_chance,
        r_inferno_adze,
        success_level,
    )
    if ok:
        successful_actions = 1
        total_base_exp = float(base_exp)
        action_outputs = [(output_item, nest_item, float(base_exp))]
        continuation_succeeded = False
        if blessing_active:
            continuation_inv, continuation_exp, continuation_succeeded, continuation_output, continuation_nest = (
                apply_woodcutting_action_pure(
                    tree,
                    new_inv,
                    TREE_DATA,
                    player_level,
                    axe_spec,
                    ctx.random_random(),
                    ctx.random_random(),
                    ctx.random_random(),
                    BIRD_NEST_DROP_TABLE,
                    nest_drop_chance,
                    (
                        ctx.random_random()
                        if axe_spec.get("incinerates_logs", False)
                        and spec.get("output_item")
                        else None
                    ),
                    success_level,
                )
            )
            if continuation_succeeded:
                new_inv = continuation_inv
                successful_actions += 1
                total_base_exp += float(continuation_exp)
                action_outputs.append(
                    (
                        continuation_output,
                        continuation_nest,
                        float(continuation_exp),
                    )
                )
        if "logs_cut_today" not in player_data:
            player_data["logs_cut_today"] = 0
        player_data["logs_cut_today"] += successful_actions
        player_data["inventory"] = new_inv
        output_items: dict[str, int] = {}
        primary_outputs: dict[str, int] = {}
        output_quantity = max(1, int(spec.get("output_quantity", 1) or 1))
        incinerated_xp = 0.0
        incinerated_count = 0
        for action_output, action_nest, action_exp in action_outputs:
            _charge_urn_for_action(
                ctx,
                "woodcutting",
                tree,
                spec,
                action_exp,
                action_output,
            )
            if action_output:
                primary_outputs[action_output] = (
                    primary_outputs.get(action_output, 0) + output_quantity
                )
                output_items[action_output] = (
                    output_items.get(action_output, 0) + output_quantity
                )
            if action_nest:
                output_items[action_nest] = output_items.get(action_nest, 0) + 1
            if (
                action_output is None
                and spec.get("output_item")
                and axe_spec.get("incinerates_logs", False)
            ):
                incinerated_xp += action_exp
                incinerated_count += 1
        achievement_outputs = dict(output_items)
        if incinerated_count and spec.get("output_item"):
            source_output = str(spec["output_item"])
            achievement_outputs[source_output] = (
                achievement_outputs.get(source_output, 0)
                + incinerated_count * output_quantity
            )
        total_base_exp, _glove_events, _risk_events = _apply_brawling_actions(
            ctx,
            "woodcutting",
            tree,
            tuple(action_exp for _output, _nest, action_exp in action_outputs),
        )
        _record_action(
            ctx,
            "woodcutting",
            tree,
            True,
            expected_success_chance=expected_success,
            output_items=output_items,
            achievement_output_items=achievement_outputs,
            primary_xp=total_base_exp,
            shattered_heart_output_items=primary_outputs,
        )
        exp_gained = ctx.award_skill_exp("woodcutting_exp", total_base_exp)
        ctx.level_up_check("Woodcutting", player_data)
        if incinerated_xp:
            ctx.award_skill_exp("firemaking_exp", incinerated_xp)
            ctx.level_up_check("Firemaking", player_data)
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        if blessing_active:
            ctx.show_activity_gain(
                "Evil Tree blessing: one non-chaining continuation chop succeeded"
                if continuation_succeeded
                else "Evil Tree blessing: the continuation chop yielded no log"
            )
    else:
        _record_action(ctx, "woodcutting", tree, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()

    ctx.show_exp(base_exp if not ok else exp_gained)
    return True


def handle_mining_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    ore = player_data.get("current_ore", DEFAULT_MINING_TARGET)
    if ore not in ORE_DATA:
        ore = DEFAULT_MINING_TARGET
        player_data["current_ore"] = ore
    ore_spec = ORE_DATA[ore]
    player_level = player_data["mining_level"]
    success_level = effective_roll_level_pure(
        player_data, "mining", player_level
    )

    if player_level < ore_spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {ore_spec['level']} Mining to mine {ore_spec.get('display_name', ore)}.")
        return False

    pickaxe_spec = best_mining_pickaxe_pure(
        player_level,
        player_data.get("inventory", {}),
        player_data.get("toolbelt", {}),
        MINING_PICKAXE_DATA,
    )
    if pickaxe_spec is None:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Missing pickaxe",
            "You need a usable pickaxe to train Mining. Mining has been switched off.",
        )
        return False
    locked_reasons = mining_target_locked_reasons_pure(player_data, ore, ORE_DATA, MINING_PICKAXE_DATA, QUEST_UNLOCK_RULES)
    if locked_reasons:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Mining target locked",
            f"{ore_spec.get('display_name', ore)} requires {', '.join(locked_reasons)}, so Mining has been switched off.",
        )
        return False

    bonus_state = equipment_bonus_state_pure(player_data.get("equipment", {}) or {}, MINING_BONUS_ITEM_DATA)
    gem_drop_chance = GLORY_GEM_DROP_CHANCE if bonus_state["has_glory"] else INCIDENTAL_GEM_DROP_CHANCE
    r_action = 0.0 if ctx.cadence_forced_opportunity else ctx.random_random()
    r_output = ctx.random_random()
    r_gem_chance = ctx.random_random()
    r_gem_pick = ctx.random_random()
    expected_success = (
        1.0
        if ctx.cadence_forced_opportunity
        else calculate_mining_success_probability_pure(
            success_level, ore_spec, pickaxe_spec
        )
    )

    inventory_before = dict(player_data.get("inventory", {}) or {})
    new_inv, base_exp, ok, output_item, gem, extra_output = apply_mining_action_pure(
        ore,
        inventory_before,
        ORE_DATA,
        player_level,
        pickaxe_spec,
        r_action,
        r_output,
        r_gem_chance,
        r_gem_pick,
        INCIDENTAL_GEM_DROP_TABLE,
        gem_drop_chance,
        bonus_state["varrock_armour_tier"],
        success_level,
    )
    shooting_star_state = player_data.get("shooting_star")
    ore_bonus_active = bool(
        isinstance(shooting_star_state, dict)
        and int(
            shooting_star_state.get("ore_bonus_ticks_remaining", 0) or 0
        )
        > 0
    )
    ore_bonus_output = None
    output_label = str(output_item or "")
    if (
        ok
        and ore_bonus_active
        and output_label
        and (
            " ore" in output_label.lower()
            or output_label == "Red sandstone"
        )
        and ctx.random_random() < SHOOTING_STAR_ORE_BONUS_CHANCE
    ):
        ore_bonus_output = output_label
        new_inv[output_label] = int(new_inv.get(output_label, 0) or 0) + 1
    if ok:
        if "ores_mined_today" not in player_data:
            player_data["ores_mined_today"] = 0
        player_data["ores_mined_today"] += 1
        if ore == "red_sandstone":
            daily_state = red_sandstone_daily_state_pure(player_data)
            daily_state["mined"] = int(daily_state["mined"]) + 1
            player_data["red_sandstone_daily"] = daily_state
        player_data["inventory"] = new_inv
        _charge_urn_for_action(ctx, "mining", ore, ore_spec, base_exp, output_item)
        base_exp, _glove_events, _risk_events = _apply_brawling_actions(
            ctx, "mining", ore, (base_exp,)
        )
        output_items: dict[str, int] = {}
        primary_outputs: dict[str, int] = {}
        if output_item:
            previous_quantity = int(inventory_before.get(output_item, 0) or 0)
            primary_quantity = int(new_inv.get(output_item, 0) or 0) - previous_quantity
            primary_quantity -= int(extra_output == output_item)
            primary_quantity -= int(ore_bonus_output == output_item)
            if primary_quantity > 0:
                primary_outputs[output_item] = primary_quantity
                output_items[output_item] = primary_quantity
        for item_name in (gem, extra_output, ore_bonus_output):
            if item_name:
                output_items[item_name] = output_items.get(item_name, 0) + 1
        for item_name in (extra_output, ore_bonus_output):
            if item_name:
                primary_outputs[item_name] = primary_outputs.get(item_name, 0) + 1
        _record_action(
            ctx,
            "mining",
            ore,
            True,
            expected_success_chance=expected_success,
            output_items=output_items,
            primary_xp=base_exp,
            shattered_heart_output_items=primary_outputs,
        )
        exp_gained = ctx.award_skill_exp("mining_exp", base_exp)
        ctx.level_up_check("Mining", player_data)
        ctx.check_achievements(player_data)
        ctx.save_player_data()

        ctx.refresh_skill_availability()
        ctx.show_exp(exp_gained)
        if ore_bonus_output:
            ctx.show_activity_gain(
                f"Star sprite bonus: +1 {ore_bonus_output}"
            )
    else:
        _record_action(ctx, "mining", ore, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()
    return True
