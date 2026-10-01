"""runtime_actions_production.py - split out of runtime_actions.py; see that module's header."""

from __future__ import annotations

from typing import Any, Callable, Optional

from ..core.constants import (
    BIRD_NEST_DROP_CHANCE,
    BIRD_NEST_DROP_TABLE,
    BIRD_NEST_OPEN_TABLES,
    COMBAT_BURST_TICKS,
    COMBAT_ENEMY_DATA,
    COMBAT_FOOD_DATA,
    CONSUMABLE_DATA,
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
    GILDED_ALTAR_MULTIPLIER,
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
    apply_consumable_pure,
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
    reconcile_smithing_coal_bag_pure,
    recipe_without_belt_tools,
    smithing_inventory_with_coal_bag_pure,
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
from ..logic.cooking_gauntlets_logic import (
    cooking_gauntlets_beneficial_pure,
    cooking_gauntlets_worn_pure,
    reconcile_cooking_equipment_pure,
)
from ..core.skill_registry import get_skill
from ..logic.skilling_boost_logic import (
    skilling_effective_level_pure,
    skilling_potion_item_pure,
    skilling_potion_target_enabled_pure,
)
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
    apply_master_runecrafter_xp_bonus_pure,
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

from .runtime_actions_shared import (  # noqa: F401  (re-export)
    _COMBAT_EXP_SKILLS,
    _admit_live_cadence,
    _apply_brawling_actions,
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
    _admit_live_cadence,
    _award_action_xp_rewards,
    _charge_urn_for_action,
    _combat_review_ticks,
    _record_action,
    _refresh_combat_levels,
    _switch_material_failure_to_bankstanding,
    missing_materials_text,
)

from .runtime_actions_context import (
    RuntimeActionContext,
)


def _spec_output_items(spec: dict[str, Any], fallback_item: Optional[str] = None) -> dict[str, int]:
    outputs = spec.get("outputs")
    if isinstance(outputs, dict) and outputs:
        return {str(item): int(amount) for item, amount in outputs.items() if item and isinstance(amount, int) and amount > 0}
    output_item = fallback_item or spec.get("output_item")
    if not output_item:
        return {}
    try:
        output_qty = int(spec.get("output_qty", 1))
    except (TypeError, ValueError):
        output_qty = 1
    result = {str(output_item): max(output_qty, 1)}
    byproducts = spec.get("byproducts")
    if isinstance(byproducts, dict):
        for item, amount in byproducts.items():
            if item and isinstance(amount, int) and amount > 0:
                result[str(item)] = result.get(str(item), 0) + amount
    return result


def _auto_drink_skilling_potion_if_needed(
    ctx: RuntimeActionContext,
    skill_id: str,
    target_id: str,
    required_level: int,
) -> bool:
    player_data = ctx.player_data
    if skilling_effective_level_pure(player_data, skill_id) >= required_level:
        return True
    if not skilling_potion_target_enabled_pure(
        player_data, skill_id, target_id
    ):
        return False
    item_name = skilling_potion_item_pure(
        player_data.get("inventory", {}) or {}, skill_id
    )
    if not item_name:
        return False
    updated, result = apply_consumable_pure(player_data, item_name)
    if not result.get("allowed", False):
        return False

    carried = updated.get("carried_inventory", {})
    if isinstance(carried, dict):
        carried = {
            str(key): dict(value) if isinstance(value, dict) else {}
            for key, value in carried.items()
        }
        view = dict(carried.get(target_id, {}))
        if int(view.get(item_name, 0) or 0) > 0:
            # The carried overlay subtracts consumption; retain only the replacement here.
            leaves = str(CONSUMABLE_DATA[item_name].get("leaves", ""))
            if leaves:
                view[leaves] = int(view.get(leaves, 0) or 0) + 1
            carried[target_id] = view
            updated["carried_inventory"] = carried

    player_data.clear()
    player_data.update(updated)
    ctx.show_activity_gain(
        f"Drank {item_name} · {skill_id.title()} is temporarily level "
        f"{skilling_effective_level_pure(player_data, skill_id)}"
    )
    return skilling_effective_level_pure(player_data, skill_id) >= required_level


def handle_crafting_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    item = player_data.get("current_craft", "form_pot_unfired")
    spec = CRAFTING_DATA.get(item)
    display_name = spec.get("display_name", item) if spec else item
    if not spec:
        ctx.show_error_message("Unknown crafting target", "Choose a valid Crafting target before reviewing.")
        return False

    spec = recipe_without_belt_tools(player_data, spec)
    crafting_data = {item: spec}
    required_items = dict(spec.get("requirements", {}))
    required_items.update(spec.get("required_items", {}))
    if not has_crafting_materials_pure(item, player_data["inventory"], crafting_data):
        missing = missing_materials_text(required_items, player_data["inventory"])
        _switch_material_failure_to_bankstanding(ctx, f"You need {missing} to craft {display_name}.")
        return False

    _auto_drink_skilling_potion_if_needed(
        ctx, "crafting", str(item), int(spec["level"])
    )
    player_level = skilling_effective_level_pure(player_data, "crafting")
    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Crafting to make {display_name}.")
        return False

    thread_roll = min(int(ctx.random_random() * 5), 4) + 1 if spec.get("consume_thread_on_roll") else None
    new_inv, base_exp, ok = apply_crafting_pure(item, player_data["inventory"], crafting_data, thread_roll)
    if not ok:
        missing = missing_materials_text(required_items, player_data["inventory"])
        _switch_material_failure_to_bankstanding(ctx, f"You need {missing} to craft {display_name}.")
        return False

    player_data["inventory"] = new_inv
    _record_action(ctx, "crafting", item, True, expected_success_chance=1.0, output_items=_spec_output_items(spec))
    exp_gained = ctx.award_skill_exp("crafting_exp", base_exp)
    ctx.level_up_check("Crafting", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()

    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_fletching_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_fletch", DEFAULT_FLETCHING_TARGET)
    if target not in FLETCHING_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    spec = FLETCHING_DATA[target]
    display_name = spec.get("display_name", target)
    locked_reasons = fletching_target_locked_reasons_pure(player_data, target, FLETCHING_DATA, QUEST_UNLOCK_RULES)
    unlock_locked = tuple(
        reason
        for reason in locked_reasons
        if reason not in {"materials"} and not str(reason).startswith("Fletching level")
    )
    if unlock_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fletching target locked",
            f"{display_name} requires {', '.join(unlock_locked)}, so Fletching has been switched off.",
        )
        return False

    if "materials" in locked_reasons:
        missing_requirements = dict(spec.get("requirements", {}))
        missing_requirements.update(spec.get("required_items", {}))
        missing = missing_materials_text(missing_requirements, player_data["inventory"])
        _switch_material_failure_to_bankstanding(
            ctx, f"You need {missing} to make {display_name}."
        )
        return False

    _auto_drink_skilling_potion_if_needed(
        ctx, "fletching", str(target), int(spec["level"])
    )
    player_level = skilling_effective_level_pure(player_data, "fletching")

    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Fletching to make {display_name}.")
        return False

    new_inv, base_exp, ok = apply_fletching_pure(target, player_data["inventory"], FLETCHING_DATA)
    if not ok:
        missing_requirements = dict(spec.get("requirements", {}))
        missing_requirements.update(spec.get("required_items", {}))
        missing = missing_materials_text(missing_requirements, player_data["inventory"])
        _switch_material_failure_to_bankstanding(
            ctx, f"You need {missing} to make {display_name}."
        )
        return False

    player_data["inventory"] = new_inv
    _record_action(ctx, "fletching", target, True, expected_success_chance=1.0, output_items=_spec_output_items(spec))
    xp_rewards = normalize_xp_rewards_pure(spec, "fletching", base_exp)
    exp_gained = _award_action_xp_rewards(ctx, xp_rewards, "fletching")
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_herblore_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_herblore", DEFAULT_HERBLORE_TARGET)
    if target not in HERBLORE_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    spec = HERBLORE_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("herblore_level", 1)
    locked_reasons = herblore_target_locked_reasons_pure(player_data, target, HERBLORE_DATA, QUEST_UNLOCK_RULES)
    unlock_locked = tuple(
        reason
        for reason in locked_reasons
        if reason not in {"materials"} and not str(reason).startswith("Herblore level")
    )
    if unlock_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Herblore target locked",
            f"{display_name} requires {', '.join(unlock_locked)}, so Herblore has been switched off.",
        )
        return False

    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Herblore to make {display_name}.")
        return False

    new_inv, base_exp, ok = apply_herblore_action_pure(target, player_data["inventory"], HERBLORE_DATA)
    if not ok:
        missing = missing_materials_text(spec.get("requirements", {}), player_data["inventory"])
        _switch_material_failure_to_bankstanding(
            ctx, f"You need {missing} to make {display_name}."
        )
        return False

    equipment = player_data.get("equipment") or {}
    bonus_roll = (
        ctx.random_random()
        if factory_outfit_four_dose_eligible_pure(target, spec, equipment)
        else 0.5
    )
    new_inv, base_exp, factory_bonus = apply_factory_outfit_herblore_bonus_pure(
        target,
        new_inv,
        base_exp,
        spec,
        equipment,
        bonus_roll,
        HERBLORE_DATA,
    )

    player_data["inventory"] = new_inv
    output_items = _spec_output_items(spec)
    if factory_bonus.get("four_dose"):
        three_dose = str(spec.get("output_item", target))
        remaining = int(output_items.get(three_dose, 0) or 0) - 1
        if remaining > 0:
            output_items[three_dose] = remaining
        else:
            output_items.pop(three_dose, None)
        four_dose = str(factory_bonus["output_item"])
        output_items[four_dose] = int(output_items.get(four_dose, 0) or 0) + 1
    _record_action(
        ctx,
        "herblore",
        target,
        True,
        expected_success_chance=1.0,
        output_items=output_items,
    )
    xp_rewards = normalize_xp_rewards_pure(spec, "herblore", base_exp)
    exp_gained = _award_action_xp_rewards(ctx, xp_rewards, "herblore")
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_summoning_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = str(
        player_data.get("current_summoning", DEFAULT_SUMMONING_TARGET)
    )
    if target not in SUMMONING_ACTIONS_BY_ID:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    action = SUMMONING_ACTIONS_BY_ID[target]
    locked_reasons = summoning_action_locked_reasons_pure(player_data, target)
    level_reasons = tuple(
        reason
        for reason in locked_reasons
        if str(reason).startswith("Summoning level")
    )
    if level_reasons:
        ctx.show_error_message(
            "Insufficient level",
            f"You need {level_reasons[0]} for {action.display_name}.",
        )
        return False

    updated, ok, result = apply_summoning_training_action_pure(
        player_data, target
    )
    if not ok:
        missing = ", ".join(
            reason.removeprefix("Missing ")
            for reason in result.get("locked_reasons", ())
            if str(reason).startswith("Missing ")
        )
        _switch_material_failure_to_bankstanding(
            ctx,
            f"You need {missing or 'the source recipe'} for "
            f"{action.display_name.lower()}.",
        )
        return False

    player_data["inventory"] = updated["inventory"]
    output_item = str(result["output_item"])
    output_quantity = int(result["output_quantity"])
    _record_action(
        ctx,
        "summoning",
        target,
        True,
        expected_success_chance=1.0,
        output_items={output_item: output_quantity},
        primary_xp=float(result["xp"]),
    )
    exp_gained = ctx.award_skill_exp("summoning_exp", float(result["xp"]))
    ctx.level_up_check("Summoning", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    ctx.show_activity_gain(f"+{output_quantity} {output_item}")
    return True


def handle_prayer_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_prayer", DEFAULT_PRAYER_TARGET)
    if target not in PRAYER_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    spec = PRAYER_DATA[target]
    display_name = spec.get("display_name", target)
    locked = prayer_target_locked_reasons_pure(player_data, target, PRAYER_DATA)
    if locked:
        material_names = tuple(str(name) for name in spec.get("requirements", {}))
        materials_only = bool(material_names) and all(
            any(str(reason).startswith(f"{name} x") for name in material_names)
            for reason in locked
        )
        if materials_only:
            _switch_material_failure_to_bankstanding(
                ctx, f"{display_name} requires {', '.join(locked)}."
            )
        else:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Prayer target unavailable",
                f"{display_name} requires {', '.join(locked)}, so Prayer has been switched off.",
            )
        return False

    if spec.get("method") == "gilded_altar":
        mode = player_data.get("prayer_gilded_mode", "hosted")
        if mode == "owned":
            access_reasons = owned_gilded_altar_access_reasons_pure(player_data, target)
            if access_reasons:
                ctx.deactivate_current_skill()
                ctx.show_error_message(
                    "Owned gilded altar unavailable",
                    f"Owned gilded training requires {', '.join(access_reasons)}, so Prayer has been switched off.",
                )
                return False
            burner_count = owned_gilded_altar_burner_count_pure(player_data)
            stint = player_data.get("prayer_owned_altar_stint", {}) or {}
            if stint.get("target_id") != target:
                if burner_count > 0:
                    inventory = dict(player_data.get("inventory", {}) or {})
                    inventory["Clean marrentill"] = int(inventory.get("Clean marrentill", 0) or 0) - burner_count
                    player_data["inventory"] = inventory
                player_data["prayer_owned_altar_stint"] = {"target_id": target, "burners_lit": burner_count}
            player_data.update(clear_prayer_gilded_stint_pure(player_data))
        elif mode == "hosted":
            player_data["prayer_owned_altar_stint"] = {}
            searched, ready, remaining = prayer_gilded_search_step_pure(player_data, target, ctx.random_random)
            player_data.update(searched)
            if not ready:
                _record_action(ctx, "prayer", target, True, expected_success_chance=1.0)
                ctx.save_player_data()
                ctx.show_activity_gain(f"Finding a hosted gilded altar — {remaining} review{'s' if remaining != 1 else ''} left")
                return True
        else:
            ctx.deactivate_current_skill()
            ctx.show_error_message("Prayer target unavailable", "Choose hosted or owned gilded training before reviewing.")
            return False
    else:
        player_data.update(clear_prayer_gilded_stint_pure(player_data))
        player_data["prayer_owned_altar_stint"] = {}

    ctx, admitted = _admit_live_cadence(ctx, "prayer", target)
    if not admitted:
        return True
    new_inventory, base_exp, ok, outputs = apply_prayer_action_pure(target, player_data.get("inventory", {}), PRAYER_DATA)
    if not ok:
        _switch_material_failure_to_bankstanding(
            ctx, f"You no longer have the materials for {display_name}."
        )
        return False
    player_data["inventory"] = new_inventory
    player_data["prayer_actions_completed"] = int(player_data.get("prayer_actions_completed", 0) or 0) + 1
    if spec.get("method") == "bury":
        player_data["prayer_bury_count"] = int(player_data.get("prayer_bury_count", 0) or 0) + 1
    _record_action(ctx, "prayer", target, True, expected_success_chance=1.0, output_items=outputs)
    if spec.get("method") == "gilded_altar":
        source_base = base_exp / GILDED_ALTAR_MULTIPLIER
        base_exp = source_base * effective_gilded_altar_multiplier_pure(
            player_data,
            player_data.get("prayer_gilded_mode", "hosted"),
            target,
        )
    exp_gained = ctx.award_skill_exp("prayer_exp", base_exp)
    ctx.level_up_check("Prayer", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_construction_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_construction", DEFAULT_CONSTRUCTION_TARGET)
    if target not in CONSTRUCTION_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    spec = CONSTRUCTION_DATA[target]
    locked = construction_target_locked_reasons_pure(
        player_data, target, CONSTRUCTION_DATA, ROOM_DATA, SERVANT_DATA,
        NAIL_DATA, WORKBENCH_TIERS,
    )
    if locked:
        material_names = {
            str(name)
            for name in spec.get("requirements", {})
        } | {"Coins"}
        materials_only = bool(material_names) and all(
            any(str(reason).startswith(name) for name in material_names)
            for reason in locked
        )
        if materials_only:
            _switch_material_failure_to_bankstanding(
                ctx,
                f"{spec.get('display_name', target)} requires {', '.join(locked)}.",
            )
        else:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Construction target unavailable",
                f"{spec.get('display_name', target)} requires {', '.join(locked)}, so Construction has been switched off.",
            )
        return False
    updated, rewards, ok = apply_construction_action_pure(
        player_data, target, CONSTRUCTION_DATA, SERVANT_DATA, NAIL_DATA,
        ctx.random_random,
    )
    if not ok:
        _switch_material_failure_to_bankstanding(
            ctx,
            f"You no longer have the materials for {spec.get('display_name', target)}.",
        )
        return False
    player_data.update(updated)
    skill = "magic" if target.startswith("tablet_") else "construction"
    exp_gained = ctx.award_skill_exp(f"{skill}_exp", float(rewards.get(skill, 0.0) or 0.0))
    ctx.level_up_check("Magic" if skill == "magic" else "Construction", player_data)
    _record_action(
        ctx,
        "construction",
        target,
        True,
        expected_success_chance=1.0,
        output_items=rewards.get("outputs", {}),
        shattered_heart_skill_id=skill,
    )
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_firemaking_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_firemaking", DEFAULT_FIREMAKING_TARGET)
    if target not in FIREMAKING_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    spec = FIREMAKING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("firemaking_level", 1)
    success_level = effective_roll_level_pure(
        player_data, "firemaking", player_level
    )
    quest_locked = tuple(
        reason
        for reason in firemaking_target_locked_reasons_pure(player_data, target, FIREMAKING_DATA, QUEST_UNLOCK_RULES)
        if reason not in {"materials"} and not str(reason).startswith("Firemaking level")
    )
    if quest_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Firemaking target locked",
            f"{display_name} requires {', '.join(quest_locked)}, so Firemaking has been switched off.",
        )
        return False

    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Firemaking to burn {display_name}.")
        return False

    if not has_firemaking_materials_pure(target, player_data.get("inventory", {}), FIREMAKING_DATA):
        missing = missing_materials_text(spec.get("requirements", {}), player_data.get("inventory", {}))
        _switch_material_failure_to_bankstanding(
            ctx, f"You need {missing} to burn {display_name}."
        )
        return False

    embedded_probability = bool(
        ctx.cadence_live_enabled
        and resolve_live_cadence_route_pure("firemaking", target, player_data).mode
        == EMBEDDED_PROBABILITY
    )
    expected_success = (
        firemaking_source_roll_chance_pure(success_level, spec)
        if embedded_probability
        else calculate_firemaking_success_probability_pure(success_level, spec)
    )
    action_roll = ctx.random_random()
    proposed_outcome_success = (
        action_roll < firemaking_source_roll_chance_pure(success_level, spec)
    )
    new_inv, base_exp, ok, _output_item = apply_firemaking_action_pure(
        target,
        player_data.get("inventory", {}),
        FIREMAKING_DATA,
        player_level,
        action_roll,
        success_level,
        use_source_probability=embedded_probability,
    )
    if not ok:
        _record_action(
            ctx,
            "firemaking",
            target,
            False,
            expected_success_chance=expected_success,
            failure_kind="dry",
            proposed_outcome_success=proposed_outcome_success,
        )
        ctx.save_player_data()
        return True

    player_data["inventory"] = new_inv
    base_exp, _glove_events, _risk_events = _apply_brawling_actions(
        ctx, "firemaking", target, (base_exp,)
    )
    _record_action(
        ctx,
        "firemaking",
        target,
        True,
        expected_success_chance=expected_success,
        output_item=_output_item,
        primary_xp=base_exp,
        proposed_outcome_success=proposed_outcome_success,
    )
    exp_gained = ctx.award_skill_exp("firemaking_exp", base_exp)
    ctx.level_up_check("Firemaking", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_cooking_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_cooking", DEFAULT_COOKING_TARGET)
    if target not in COOKING_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    spec = COOKING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("cooking_level", 1)
    quest_locked = tuple(
        reason
        for reason in cooking_target_locked_reasons_pure(player_data, target, COOKING_DATA, QUEST_UNLOCK_RULES)
        if reason not in {"materials"} and not str(reason).startswith("Cooking level")
    )
    if quest_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Cooking target locked",
            f"{display_name} requires {', '.join(quest_locked)}, so Cooking has been switched off.",
        )
        return False

    if not spec.get("source_no_level_requirement") and player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Cooking to {str(display_name).lower()}.")
        return False

    if not has_cooking_materials_pure(target, player_data.get("inventory", {}), COOKING_DATA):
        missing = missing_materials_text(spec.get("requirements", {}), player_data.get("inventory", {}))
        _switch_material_failure_to_bankstanding(
            ctx, f"You need {missing} to {str(display_name).lower()}."
        )
        return False

    reconciled = reconcile_cooking_equipment_pure(
        player_data,
        target,
        beneficial=cooking_gauntlets_beneficial_pure(
            player_data, target, cadence_live_enabled=ctx.cadence_live_enabled
        ),
    )
    player_data.clear()
    player_data.update(reconciled)
    has_cooking_gauntlets = cooking_gauntlets_worn_pure(player_data)

    embedded_probability = bool(
        ctx.cadence_live_enabled
        and resolve_live_cadence_route_pure("cooking", target, player_data).mode
        == EMBEDDED_PROBABILITY
    )
    success_level = effective_roll_level_pure(player_data, "cooking", player_level)
    success_chance = (
        cooking_source_roll_chance_pure
        if embedded_probability
        else calculate_cooking_success_probability_pure
    )
    expected_success = success_chance(
        success_level, spec, has_cooking_gauntlets=has_cooking_gauntlets
    )
    roll = ctx.random_random()
    source_success = cooking_source_roll_chance_pure(
        success_level,
        spec,
        has_cooking_gauntlets=has_cooking_gauntlets,
    )
    source_runtime_action = bool(spec.get("source_success_formula") or spec.get("source_always_succeeds"))
    proposed_outcome_success = roll <= source_success if source_runtime_action else roll < source_success
    if spec.get("outcome_kind") == "maturity":
        expected_success = 1.0
        proposed_outcome_success = True
    byproduct_roll = ctx.random_random() if spec.get("byproduct_item") and roll <= expected_success else None
    inventory_before = dict(player_data.get("inventory", {}) or {})
    new_inv, base_exp, ok, output_item, burned = apply_cooking_action_pure(
        target,
        inventory_before,
        COOKING_DATA,
        # The roll level, not the raw one: the reported chance above and the
        # outcome here must be the same number.
        success_level,
        roll,
        byproduct_roll,
        use_source_probability=embedded_probability,
        has_cooking_gauntlets=has_cooking_gauntlets,
    )
    if not ok:
        return False

    player_data["inventory"] = new_inv
    if burned:
        failure_kind = str(spec.get("failure_kind", "burn"))
        _record_action(
            ctx,
            "cooking",
            target,
            False,
            expected_success_chance=expected_success,
            output_item=output_item,
            failure_kind=failure_kind,
            proposed_outcome_success=proposed_outcome_success,
        )
        if failure_kind == "burn":
            player_data["cooking_burn_count"] = player_data.get("cooking_burn_count", 0) + 1
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        if output_item:
            ctx.show_activity_gain(f"+1 {output_item}")
        return True

    _charge_urn_for_action(ctx, "cooking", target, spec, base_exp, output_item)
    output_items = {
        item_name: int(amount) - int(inventory_before.get(item_name, 0) or 0)
        for item_name, amount in new_inv.items()
        if int(amount) - int(inventory_before.get(item_name, 0) or 0) > 0
    }
    tracked_output_items = output_items if spec.get("byproducts") else None
    base_exp, _glove_events, _risk_events = _apply_brawling_actions(
        ctx, "cooking", target, (base_exp,)
    )
    _record_action(
        ctx,
        "cooking",
        target,
        True,
        expected_success_chance=expected_success,
        output_item=output_item if tracked_output_items is None else None,
        output_qty=output_items.get(output_item, 1) if output_item else 1,
        output_items=tracked_output_items,
        primary_xp=base_exp,
        proposed_outcome_success=proposed_outcome_success,
    )
    player_data["cooking_success_count"] = player_data.get("cooking_success_count", 0) + 1
    exp_gained = ctx.award_skill_exp("cooking_exp", base_exp)
    ctx.level_up_check("Cooking", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if spec.get("output_quantity_model") or spec.get("byproducts"):
        ctx.show_activity_gain(
            " · ".join(
                f"+{amount} {item_name}"
                for item_name, amount in output_items.items()
            )
        )
    if exp_gained:
        ctx.show_exp(exp_gained)
    return True


def handle_runecrafting_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_runecrafting", DEFAULT_RUNECRAFTING_TARGET)
    if target not in RUNECRAFTING_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    spec = RUNECRAFTING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("runecrafting_level", 1)

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Runecrafting for {display_name}.")
        return False

    rolls = [ctx.random_random() for _ in range(64)]
    prior_inventory = dict(player_data.get("inventory", {}) or {})
    new_data, base_exp, ok, message = apply_runecrafting_action_pure(
        player_data,
        target,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        rolls=rolls,
        quest_unlock_rules=QUEST_UNLOCK_RULES,
    )
    if not ok:
        reasons = runecrafting_locked_reasons_pure(
            player_data,
            target,
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
            QUEST_UNLOCK_RULES,
        )
        material_reasons = {
            "essence",
            "Pure essence",
            "Tiara",
            "Wicked hood",
            str(spec.get("component_rune", "")),
            str(spec.get("consumed_talisman", "")),
            str(spec.get("talisman_item", "")),
            "Runecrafting staff",
            str(spec.get("input_item", "")),
        }
        materials_only = bool(reasons) and all(
            str(reason) in material_reasons
            for reason in reasons
        )
        if materials_only:
            _switch_material_failure_to_bankstanding(
                ctx, f"{display_name} requires {', '.join(reasons)}."
            )
        else:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Runecrafting unavailable",
                f"{display_name} cannot run right now, so Runecrafting has been switched off.",
            )
        return False

    player_data.update(new_data)
    output_item = str(spec.get("output_item", ""))
    output_count = max(
        0,
        int((player_data.get("inventory", {}) or {}).get(output_item, 0) or 0)
        - int(prior_inventory.get(output_item, 0) or 0),
    ) if output_item else 0
    _record_action(
        ctx,
        "runecrafting",
        target,
        True,
        expected_success_chance=1.0,
        output_items={output_item: output_count} if output_count else {},
    )
    awarded_exp = apply_master_runecrafter_xp_bonus_pure(player_data, base_exp)
    exp_gained = ctx.award_skill_exp("runecrafting_exp", awarded_exp)
    ctx.level_up_check("Runecrafting", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if exp_gained > 0:
        ctx.show_exp(exp_gained)
    elif message:
        ctx.show_activity_gain(str(message))
    return True


def _switch_off_blocked_quest(ctx: RuntimeActionContext, quest_name: str, reasons: tuple[str, ...]) -> None:
    ctx.deactivate_current_skill()
    reason_lines = "\n".join(f"• {reason}" for reason in reasons)
    ctx.show_error_message("Quest blocked", f"{quest_name} is blocked:\n{reason_lines}\n\nQuesting has been switched off until this is resolved.")


def handle_quest_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    quest_id = player_data.get("current_quest", "rune_mysteries")
    if quest_id not in QUEST_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    quest = QUEST_DATA[quest_id]
    stage_blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
    combat_blockers = quest_current_stage_resolvable_combat_blockers_pure(player_data, quest_id, QUEST_DATA)
    if combat_blockers:
        new_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
            combat_blockers[0].get("encounter_id"),
            rng=ctx.random_random,
            equipment_data=EQUIPMENT_DATA,
            ticks=_combat_review_ticks(ctx),
            live_cadence=ctx.cadence_live_enabled,
        )
        if not ok:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Quest combat blocked",
                f"{quest.get('display_name', quest_id)} cannot resolve this battle yet.",
            )
            return False
        player_data.update(new_data)
        _record_action(ctx, "quest", f"{quest_id}:{result.get('encounter_id', 'combat')}", True, expected_success_chance=1.0)
        _refresh_combat_levels(ctx, result.get("xp_rewards", {}))
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        xp_total = 0.0
        for amount in (result.get("xp_rewards", {}) or {}).values():
            try:
                xp_total += float(amount or 0.0)
            except (TypeError, ValueError):
                pass
        if xp_total > 0:
            ctx.show_exp(xp_total)
        display_name = str(result.get("display_name") or "combat encounter")
        quantity_text = str(result.get("quantity_text") or "")
        if result.get("reason") == "quest_combat_bank_run":
            remaining = int(result.get("bank_run_reviews_remaining", 0) or 0)
            ctx.show_activity_gain(f"{display_name}: bank run ({remaining} reviews remaining)")
        elif result.get("died"):
            ctx.show_activity_gain(f"☠ YOU DIED — killed by {display_name}; gear moved to grave")
        elif result.get("killed"):
            ctx.show_activity_gain(f"Defeated {display_name}{quantity_text}")
        else:
            ctx.show_activity_gain(
                f"{display_name}: {int(result.get('player_damage', 0) or 0)} damage dealt, "
                f"{int(result.get('enemy_lifepoints', 0) or 0)} LP left"
            )
        return True
    stage_blocker_reasons = tuple(str(blocker.get("reason")) for blocker in stage_blockers)
    if stage_blocker_reasons:
        _switch_off_blocked_quest(ctx, quest.get("display_name", quest_id), stage_blocker_reasons)
        return False
    if not can_start_quest_pure(player_data, quest_id, QUEST_DATA):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Quest unavailable",
            f"{quest.get('display_name', quest_id)} cannot progress right now, so questing has been switched off.",
        )
        return False

    exp_before = ctx.implemented_exp_keys_snapshot()
    new_data, ok, completed_now, clue_reward_refusal_reason = (
        apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
            include_clue_refusal=True,
        )
    )
    if not ok:
        stage_blocker_reasons = quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
        if stage_blocker_reasons:
            _switch_off_blocked_quest(ctx, quest.get("display_name", quest_id), stage_blocker_reasons)
        return False
    player_data.update(new_data)
    _record_action(ctx, "quest", quest_id, True, expected_success_chance=1.0)
    if completed_now:
        ctx.show_quest_exp_delta(exp_before)
        ctx.deactivate_current_skill()
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if completed_now:
        display_name = str(quest.get("display_name", quest_id))
        ctx.show_activity_gain(f"{display_name} complete")
        if clue_reward_refusal_reason:
            ctx.show_activity_gain(clue_reward_refusal_reason)
        ctx.show_error_message(
            "Quest complete",
            f"{display_name} is complete, so questing has been switched off. "
            "Open the AnkiScape menu to pick another quest.",
        )
    else:
        state = player_data.get("quests", {}).get(quest_id, {})
        ctx.show_activity_gain(f"{quest.get('display_name', quest_id)} {state.get('progress', 0)}/{quest.get('stages', 1)}")
    return True


def handle_smithing_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_smith", DEFAULT_SMITHING_TARGET)
    if target not in SMITHING_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    spec = recipe_without_belt_tools(player_data, SMITHING_DATA[target])
    display_name = spec.get("display_name", spec.get("output_item", target))
    player_level = player_data["smithing_level"]

    locked_reasons = smithing_target_locked_reasons_pure(player_data, target, SMITHING_DATA, QUEST_UNLOCK_RULES)
    quest_locked = tuple(
        reason for reason in locked_reasons if reason != "materials" and not str(reason).startswith("level ")
    )
    if quest_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Smithing target locked",
            f"{display_name} requires {', '.join(quest_locked)}, so Smithing has been switched off.",
        )
        return False

    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Smithing to make {display_name}.")
        return False

    has_forging_ring = has_ring_of_forging_pure(player_data)
    success_level = effective_roll_level_pure(player_data, "smithing", player_level)
    expected_success_chance = smithing_success_probability_pure(
        target,
        spec,
        success_level,
        has_ring_of_forging=has_forging_ring,
    )
    roll = ctx.random_random() if expected_success_chance < 1.0 else 0.0
    inventory_before = dict(player_data["inventory"])
    effective_inventory = smithing_inventory_with_coal_bag_pure(player_data)
    new_inv, base_exp, processed, output_item, failed = apply_smithing_action_pure(
        target,
        effective_inventory,
        {target: spec},
        success_level,
        roll,
        has_ring_of_forging=has_forging_ring,
    )
    if not processed:
        missing_requirements = dict(spec.get("requirements", {}))
        missing_requirements.update(spec.get("required_items", {}))
        missing = missing_materials_text(missing_requirements, effective_inventory)
        _switch_material_failure_to_bankstanding(
            ctx, f"You need {missing} to make {display_name}."
        )
        return False

    reconciled, _bag_coal_consumed = reconcile_smithing_coal_bag_pure(
        player_data,
        inventory_before,
        new_inv,
    )
    player_data["inventory"] = reconciled["inventory"]
    if "dungeoneering" in reconciled:
        player_data["dungeoneering"] = reconciled["dungeoneering"]
    if target == "smelt_iron_bar" and has_forging_ring:
        ring_data = consume_ring_of_forging_charge_pure(player_data)
        player_data["equipment"] = ring_data.get("equipment", {}) or {}
        player_data["item_charges"] = ring_data.get("item_charges", {}) or {}

    if failed:
        _record_action(
            ctx,
            "smithing",
            target,
            False,
            expected_success_chance=expected_success_chance,
            failure_kind="smelt_fail",
        )
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        ctx.show_activity_gain("The ore was too impure")
        return True

    _charge_urn_for_action(ctx, "smithing", target, spec, base_exp, output_item)
    base_exp, _glove_events, _risk_events = _apply_brawling_actions(
        ctx, "smithing", target, (base_exp,)
    )
    _record_action(
        ctx,
        "smithing",
        target,
        True,
        expected_success_chance=expected_success_chance,
        output_items=_spec_output_items(spec, output_item),
    )
    exp_gained = ctx.award_skill_exp("smithing_exp", base_exp)
    ctx.level_up_check("Smithing", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()

    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True
