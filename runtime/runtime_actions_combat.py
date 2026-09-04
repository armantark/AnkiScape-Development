"""runtime_actions_combat.py - split out of runtime_actions.py; see that module's header."""

from __future__ import annotations

from ..logic.combat_session import (
    wilderness_combat_risk_confirmed,
    wilderness_combat_risk_fingerprint,
)

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
    active_prayer_selection_pure,
    combat_near_death_without_food_pure,
    COMBAT_BANK_RUN_REVIEWS,
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
    combat_observed_drop_item_names_pure,
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
    repair_combat_supply_loadout_class_pure,
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

from ..logic import inventory_pure
from ..data.item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES

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
    _combat_review_ticks,
    _record_action,
    _refresh_combat_levels,
)

from .runtime_actions_context import (
    RuntimeActionContext,
)


def handle_combat_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target_id = player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    if target_id not in COMBAT_ENEMY_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False

    enemy = COMBAT_ENEMY_DATA.get(target_id, {})
    wilderness_fingerprint = wilderness_combat_risk_fingerprint(
        player_data,
        target_id,
        enemy,
    )
    if wilderness_fingerprint and not wilderness_combat_risk_confirmed(
        wilderness_fingerprint
    ):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Wilderness confirmation required",
            "Combat has been switched off. Reopen AnkiScape, review the current "
            "kept/lost equipment preview, and confirm this Wilderness target.",
        )
        return False

    if combat_near_death_without_food_pure(player_data):
        # Nothing to eat and nothing to fetch: the next exchange can end the run,
        # so refuse the review rather than resolve it. The bank-run path already
        # covers the recoverable case where the bank still holds food.
        ctx.deactivate_current_skill(
            "Lifepoints are critical and there is no food left in your pack or bank."
        )
        if callable(ctx.prompt_near_death):
            ctx.prompt_near_death("combat")
        else:
            ctx.show_error_message(
                "You are about to die",
                "Lifepoints are critical and you have no food left, in the pack "
                "or the bank. Combat has been switched off.",
            )
        return False

    locked_reasons = combat_target_locked_reasons_pure(
        player_data,
        target_id,
        COMBAT_ENEMY_DATA,
        equipment_data=EQUIPMENT_DATA,
    )
    if locked_reasons:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Combat unavailable",
            f"{enemy.get('display_name', target_id)} cannot be fought yet: {', '.join(locked_reasons)}.",
        )
        return False

    observed_item_names = set(
        combat_observed_drop_item_names_pure(player_data, target_id)
    )

    active_prayer_selection = tuple(active_prayer_selection_pure(player_data))
    using_finisher = player_data.get("combat_action") == "finisher"
    if using_finisher:
        new_data, ok, result = apply_combat_finisher_pure(
            player_data,
            COMBAT_ENEMY_DATA,
            rng=ctx.random_random,
        )
    else:
        new_data, ok, result = apply_combat_burst_pure(
            player_data,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=_combat_review_ticks(ctx),
            rng=ctx.random_random,
            live_cadence=ctx.cadence_live_enabled,
        )
    if not ok:
        if using_finisher:
            player_data["combat_action"] = "attack"
            reason = str(result.get("reason", "finisher_unavailable"))
            ctx.show_error_message(
                "Finisher unavailable",
                reason.replace("_", " ").capitalize() + ".",
            )
            ctx.save_player_data()
            return False
        ctx.deactivate_current_skill()
        reasons = result.get("locked_reasons") if isinstance(result, dict) else None
        reason_text = ", ".join(reasons) if reasons else "the selected target is unavailable"
        ctx.show_error_message("Combat unavailable", f"Combat has been switched off because {reason_text}.")
        return False

    guild_result = {}
    if (
        target_id in {"cyclops", "cyclossus"}
        and result.get("reason") == "combat_burst"
    ):
        payment_state = sanitize_warriors_guild_state_pure(
            new_data.get("warriors_guild")
        )
        new_data, token_result = consume_warriors_guild_cyclops_tokens_pure(
            new_data,
            int(result.get("ticks_elapsed", 0) or 0),
        )
        if target_id == "cyclops":
            new_data, defender_result = apply_warriors_guild_cyclops_kills_pure(
                new_data,
                int(result.get("kills", 0) or 0),
                ctx.random_random,
            )
            if defender_result.get("cyclossus_spawned"):
                new_data["current_combat_target"] = "cyclossus"
        else:
            new_data, defender_result = apply_warriors_guild_cyclossus_kills_pure(
                new_data,
                int(result.get("kills", 0) or 0),
            )
            if defender_result.get("cleared"):
                new_data["current_combat_target"] = "cyclops"
        guild_result = {
            "tokens": token_result,
            "defenders": defender_result,
        }
        if payment_state["payment_mode"] == "multi" and int(result.get("kills", 0) or 0) > 0:
            extra_bones = int(result.get("kills", 0) or 0)
            inventory = dict(new_data.get("inventory", {}) or {})
            inventory["Big bones"] = int(inventory.get("Big bones", 0) or 0) + extra_bones
            new_data["inventory"] = inventory
            result_drops = dict(result.get("drops", {}) or {})
            result_drops["Big bones"] = int(result_drops.get("Big bones", 0) or 0) + extra_bones
            result["drops"] = result_drops
        defender_drops = dict(defender_result.get("drops", {}) or {})
        if defender_drops:
            result_drops = dict(result.get("drops", {}) or {})
            for item_name, amount in defender_drops.items():
                result_drops[item_name] = int(result_drops.get(item_name, 0) or 0) + int(amount)
            result["drops"] = result_drops
        if result.get("died") or result.get("fled"):
            guild_state = sanitize_warriors_guild_state_pure(
                new_data.get("warriors_guild")
            )
            guild_state["in_cyclops_room"] = False
            guild_state["cyclossus_pending"] = False
            guild_state["token_drain_residual"] = 0
            new_data["warriors_guild"] = guild_state
            new_data["current_combat_target"] = "cyclops"
        result["warriors_guild"] = guild_result

    new_data, slayer_result = apply_slayer_kills_pure(
        new_data,
        target_id=str(result.get("target_id", target_id)),
        kills=int(result.get("kills", 0) or 0),
        enemy_data=COMBAT_ENEMY_DATA,
    )
    slayer_xp = float(slayer_result.get("slayer_xp", 0.0) or 0.0)
    if slayer_xp > 0:
        xp_rewards = dict(result.get("xp_rewards", {}) or {})
        xp_rewards["slayer_exp"] = slayer_xp
        result["xp_rewards"] = xp_rewards
    result["slayer"] = slayer_result
    player_data.update(new_data)
    player_data.update(
        repair_combat_supply_loadout_class_pure(player_data, EQUIPMENT_DATA)
    )
    drops = result.get("drops", {}) if isinstance(result, dict) else {}
    if not isinstance(drops, dict):
        drops = {}
    # Loot filter (owner: no auto-hoarding every tiny drop). The burst already
    # added the drops to the flat inventory, so leave below-value junk by removing
    # it again; stackables, coins, and unknown-value items are kept.
    # First-seen seeding reads the learning record, not the post-bury drop list:
    # auto-bury consumes bones before this point, but the kill above still
    # learned them, and the default must exist before auto-bury is ever turned
    # off and the filter has to decide the bone's fate.
    overrides = dict(player_data.get("loot_overrides") or {})
    for item_name in set(combat_observed_drop_item_names_pure(player_data, target_id)) - observed_item_names:
        overrides.setdefault(item_name, "keep")
    player_data["loot_overrides"] = overrides
    if drops:
        threshold = player_data.get("loot_value_threshold", inventory_pure.DEFAULT_LOOT_VALUE_THRESHOLD)
        if target_id in {"cyclops", "cyclossus"}:
            for item_name in (
                guild_result.get("defenders", {}).get("drops", {})
                if isinstance(guild_result, dict)
                else {}
            ):
                overrides[str(item_name)] = "keep"
        drops, left = inventory_pure.filter_loot_pure(
            drops, ITEM_VALUES, threshold, STACKABLE_ITEM_NAMES, overrides
        )
        if left:
            inventory = player_data.get("inventory", {}) or {}
            for item_name, amount in left.items():
                inventory[item_name] = max(0, int(inventory.get(item_name, 0) or 0) - amount)
            player_data["inventory"] = inventory
        # A kill can precede death in the same review burst. The pure death path
        # cannot grave those drops before this runtime-level loot filter decides
        # which ones were actually picked up, so move kept fatal-burst loot into
        # the new grave here instead of recreating a carried view after death.
        wilderness_death = bool(
            (result.get("wilderness_ambush") or {}).get("died")
        )
        if drops and result.get("died") and not wilderness_death:
            grave = dict(player_data.get("combat_grave", {}) or {})
            grave_items = list(grave.get("items", ()) or ())
            inventory = dict(player_data.get("inventory", {}) or {})
            for item_name, amount in drops.items():
                if item_name == "Coins":
                    continue
                risked = min(max(0, int(amount or 0)), max(0, int(inventory.get(item_name, 0) or 0)))
                if risked <= 0:
                    continue
                inventory[item_name] -= risked
                grave_items.extend([item_name] * risked)
            if grave_items:
                grave["items"] = grave_items
                grave.setdefault("reviews_remaining", COMBAT_GRAVE_RECOVERY_REVIEWS)
                grave.setdefault("source", "combat_death")
                player_data["combat_grave"] = grave
            player_data["inventory"] = inventory
        # Kept loot competes for carried slots: fold it into the combat target's
        # carried view (coins excluded) so it drops on a later death and, once the
        # pack fills, forces a bank run alongside supply depletion. Banking deposits it.
        elif drops:
            current_carried = player_data.get("carried_inventory")
            carried = dict(current_carried) if isinstance(current_carried, dict) else {}
            existing = carried.get(target_id) if isinstance(carried.get(target_id), dict) else {}
            carried[target_id] = inventory_pure.carried_fold_gains_pure(existing, drops, STACKABLE_ITEM_NAMES)
            player_data["carried_inventory"] = carried
    _record_action(
        ctx,
        "combat",
        str(result.get("target_id", target_id)),
        True,
        expected_success_chance=1.0,
        output_items={str(item): int(amount) for item, amount in drops.items() if isinstance(item, str)},
        kills=int(result.get("kills", 0) or 0),
        enemy_combat_level=int(
            (COMBAT_ENEMY_DATA.get(str(result.get("target_id", target_id))) or {}).get("level", 0)
            or 0
        ),
        achievement_event_fields={
            "active_prayer_selection": active_prayer_selection,
        },
    )
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

    food_used = result.get("food_used", ()) or ()
    if food_used:
        eaten: dict[str, int] = {}
        for event in food_used:
            if not isinstance(event, dict):
                continue
            item_name = str(event.get("item") or "")
            if item_name:
                eaten[item_name] = eaten.get(item_name, 0) + 1
        remaining_food = (
            (player_data.get("combat_supply_loadout") or {}).get("food") or {}
        )
        for item_name, amount in eaten.items():
            left = max(0, int(remaining_food.get(item_name, 0) or 0))
            ctx.show_activity_gain(f"Ate {amount} × {item_name} · {left} left")

    for special in result.get("enemy_specials", ()) or ():
        if not isinstance(special, dict):
            continue
        if special.get("kind") == "teleport":
            ctx.show_activity_gain(
                "Chaos Elemental teleported you · next attack delayed"
            )
        elif special.get("kind") == "unequip":
            item_name = str(special.get("item") or "")
            ctx.show_activity_gain(
                f"Chaos Elemental removed {item_name}"
                if item_name
                else "Chaos Elemental tried to remove your equipment"
            )
        elif special.get("kind") == "wyvern_breath":
            if special.get("protected"):
                shield_item = str(special.get("shield_item") or "")
                ctx.show_activity_gain(
                    f"Wyvern ice breath · protected by {shield_item} · next attack delayed"
                )
            else:
                ctx.show_activity_gain(
                    "Wyvern ice breath · unprotected · next attack delayed"
                )

    display_name = str(result.get("display_name") or "enemy")
    kills = int(result.get("kills", 0) or 0)
    kill_phrase = f"{kills} × {display_name}" if kills != 1 else display_name
    dragonfire_attacks = int(result.get("dragonfire_attacks", 0) or 0)
    dragonfire_damage = int(result.get("dragonfire_damage", 0) or 0)
    dragonfire_suffix = (
        f" · {dragonfire_damage} dragonfire LP from "
        f"{dragonfire_attacks} breath{'s' if dragonfire_attacks != 1 else ''}"
        if dragonfire_attacks > 0
        else ""
    )
    wilderness_ambush = result.get("wilderness_ambush") or {}
    if result.get("died") and wilderness_ambush.get("died"):
        lost_count = len(wilderness_ambush.get("lost_items", ()) or ())
        kept_count = len(wilderness_ambush.get("kept_items", ()) or ())
        ctx.show_activity_gain(
            "☠ PKER AMBUSH — "
            f"lost {lost_count} equipped item{'s' if lost_count != 1 else ''}; "
            f"kept {kept_count}; no grave"
        )
    elif result.get("died"):
        if kills > 0:
            ctx.show_activity_gain(f"☠ YOU DIED — defeated {kill_phrase} first; gear moved to grave")
        else:
            ctx.show_activity_gain(f"☠ YOU DIED — killed by {display_name}; gear moved to grave")
    elif result.get("fled"):
        # Auto-flee is the "you can't win this" signal: switch combat off entirely
        # (current_skill -> "None"), exactly like running out of materials for an
        # artisan activity, so the next review doesn't walk straight back into the
        # same losing fight. The player re-opens the menu to resume.
        ctx.deactivate_current_skill()
        prefix = f"Defeated {kill_phrase}, then f" if kills > 0 else "F"
        ctx.show_activity_gain(f"{prefix}led {display_name} — out of food; combat switched off to stop you dying")
    elif wilderness_ambush.get("triggered"):
        damage = int(wilderness_ambush.get("damage", 0) or 0)
        ctx.show_activity_gain(
            f"⚠ PKer ambush — took {damage} LP; "
            f"{display_name} encounter reset"
        )
    elif kills > 0:
        slayer_suffix = ""
        if int(slayer_result.get("credited_kills", 0) or 0) > 0:
            slayer_suffix = (
                " · Slayer assignment complete"
                if slayer_result.get("completed")
                else f" · {int(slayer_result.get('remaining', 0) or 0)} Slayer kills left"
            )
        guild_suffix = ""
        defender_drops = (
            guild_result.get("defenders", {}).get("drops", {})
            if isinstance(guild_result, dict)
            else {}
        )
        if defender_drops:
            guild_suffix += " · " + ", ".join(
                f"{amount} × {item_name}"
                for item_name, amount in defender_drops.items()
            )
        if (
            isinstance(guild_result, dict)
            and guild_result.get("defenders", {}).get("cyclossus_spawned")
        ):
            guild_suffix += " · a Cyclossus appeared"
        if (
            isinstance(guild_result, dict)
            and guild_result.get("tokens", {}).get("ejected")
        ):
            guild_suffix += " · tokens depleted; left the Cyclops room"
        ctx.show_activity_gain(
            f"Defeated {kill_phrase}{slayer_suffix}{guild_suffix}"
            f"{dragonfire_suffix}"
        )
    elif result.get("reason") == "combat_bank_run":
        # The review was a travel leg, not an exchange: say so instead of the
        # zero-damage line contradicting the strip's bank-run display.
        if result.get("bank_run_completed"):
            ctx.show_activity_gain("Bank run — arrived and restocked")
        else:
            route = bank_run_phase_label_pure(
                player_data.get("combat_bank_run")
            )
            remaining = max(
                0, int(result.get("bank_run_reviews_remaining", 0) or 0)
            )
            ctx.show_activity_gain(
                f"Bank run — {route} · {COMBAT_BANK_RUN_REVIEWS - remaining}"
                f"/{COMBAT_BANK_RUN_REVIEWS} travel reviews"
            )
    else:
        enemy_healing = int(result.get("enemy_healing", 0) or 0)
        vampyre_bites = int(result.get("vampyre_bites", 0) or 0)
        if vampyre_bites > 0:
            healing_phrase = (
                f", {enemy_healing} LP healed by "
                f"{vampyre_bites} bite{'s' if vampyre_bites != 1 else ''}"
            )
        else:
            healing_phrase = (
                f", {enemy_healing} LP regenerated" if enemy_healing > 0 else ""
            )
        ctx.show_activity_gain(
            f"{display_name}: {int(result.get('player_damage', 0) or 0)} damage dealt, "
            f"{int(result.get('enemy_lifepoints', 0) or 0)} LP left"
            f"{healing_phrase}{dragonfire_suffix}"
        )
    clue_refusal_reason = str(result.get("clue_refusal_reason", ""))
    if clue_refusal_reason:
        ctx.show_activity_gain(clue_refusal_reason)
    return True
