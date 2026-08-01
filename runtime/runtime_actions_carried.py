"""runtime_actions_carried.py - split out of runtime_actions.py; see that module's header."""

from __future__ import annotations

import copy

import dataclasses

from typing import Any, Callable, Optional

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
    coal_bag_coal_pure,
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
    _admit_live_cadence,
)

from .runtime_actions_context import (
    RuntimeActionContext,
)


# Handler keys that draw from / fill the 28-slot carried inventory, mapped to the
# player_data key holding their selected target. Utility (no-XP batching) and
# quests do not take carried teeth, so they are absent.
_OVERLAY_TARGET_KEYS = {
    "mining": "current_ore",
    "woodcutting": "current_tree",
    "fishing": "current_fishing",
    "hunter": "current_hunter",
    "cooking": "current_cooking",
    "crafting": "current_craft",
    "fletching": "current_fletch",
    "firemaking": "current_firemaking",
    "smithing": "current_smith",
    "runecrafting": "current_runecrafting",
    "herblore": "current_herblore",
    "prayer": "current_prayer",
    "thieving": "current_thieving",
    "agility": "current_agility",
    "summoning": "current_summoning",
}


# A stackable occupies one slot for any quantity (then holds up to the int cap);
# use the real cache stackable set so a stack is not miscounted as N slots.
_OVERLAY_STACKABLE_NAMES: frozenset[str] = STACKABLE_ITEM_NAMES


# Processing skills draw recipe inputs from the carried pack (gated + consumed);
# gathering skills fill the pack with their product instead. Combat has its own
# supply_loadout system and is not routed through this wrapper at all.
_PROCESSING_HANDLER_KEYS = frozenset(
    {"cooking", "crafting", "fletching", "firemaking", "smithing", "runecrafting", "herblore", "prayer", "summoning"}
)


_PROCESSING_DATA_TABLES = {
    "woodcutting": (TREE_DATA, "current_tree", DEFAULT_WOODCUTTING_TARGET),
    "cooking": (COOKING_DATA, "current_cooking", DEFAULT_COOKING_TARGET),
    "crafting": (CRAFTING_DATA, "current_craft", "form_pot_unfired"),
    "fletching": (FLETCHING_DATA, "current_fletch", DEFAULT_FLETCHING_TARGET),
    "firemaking": (FIREMAKING_DATA, "current_firemaking", DEFAULT_FIREMAKING_TARGET),
    "smithing": (SMITHING_DATA, "current_smith", DEFAULT_SMITHING_TARGET),
    "runecrafting": (RUNECRAFTING_DATA, "current_runecrafting", DEFAULT_RUNECRAFTING_TARGET),
    "herblore": (HERBLORE_DATA, "current_herblore", DEFAULT_HERBLORE_TARGET),
    "prayer": (PRAYER_DATA, "current_prayer", DEFAULT_PRAYER_TARGET),
}


def _processing_requirements_for(
    handler_key: str,
    player_data: dict[str, Any],
    carried_inventory: dict[str, Any] | None = None,
) -> dict[str, int]:
    """The recipe inputs a processing target needs per action, ``{item: count}``.

    Read from each skill's own data table so this stays a thin lookup, not a
    handler rewrite. Runecrafting has no fixed ``requirements`` dict (any of its
    ``essence_items`` works); resolve it to the first stocked essence in the
    target's source order, so the pack has something concrete to carry.
    """
    if handler_key == "summoning":
        target = str(
            player_data.get("current_summoning", DEFAULT_SUMMONING_TARGET)
        )
        inventory = (
            carried_inventory
            if isinstance(carried_inventory, dict)
            else player_data.get("inventory", {})
        )
        return summoning_action_requirements_pure(
            player_data,
            target,
            inventory_override=inventory,
        )
    table_info = _PROCESSING_DATA_TABLES.get(handler_key)
    if table_info is None:
        return {}
    table, target_key, default_target = table_info
    target = player_data.get(target_key, default_target)
    spec = table.get(target)
    if not isinstance(spec, dict):
        return {}
    requirements = spec.get("requirements")
    if isinstance(requirements, dict) and requirements:
        if handler_key == "fletching":
            if carried_inventory:
                resolved = fletching_material_requirements_pure(target, carried_inventory, table)
                if resolved is not None:
                    return resolved
            resolved = fletching_material_requirements_pure(target, player_data.get("inventory", {}) or {}, table)
            if resolved is not None:
                return resolved
        resolved = {str(item): int(amount) for item, amount in requirements.items() if isinstance(item, str)}
        if handler_key == "smithing" and "Coal" in resolved:
            remaining_coal = max(
                0,
                resolved["Coal"] - coal_bag_coal_pure(player_data),
            )
            if remaining_coal:
                resolved["Coal"] = remaining_coal
            else:
                resolved.pop("Coal")
        if (
            handler_key == "prayer"
            and spec.get("method") == "gilded_altar"
            and player_data.get("prayer_gilded_mode", "hosted") == "owned"
        ):
            marrentill = owned_gilded_altar_marrentill_required_pure(player_data, str(target))
            if marrentill > 0:
                resolved["Clean marrentill"] = marrentill
        return resolved
    essence_items = spec.get("essence_items")
    if isinstance(essence_items, (list, tuple)) and essence_items:
        inventory = player_data.get("inventory", {}) or {}
        essence = next((item for item in essence_items if inventory.get(item, 0)), essence_items[0])
        return {essence: 1}
    return {}


def _processing_presence_requirements_for(handler_key: str, player_data: dict[str, Any]) -> dict[str, int]:
    """Non-material recipe gates that must be present but are not per-action inputs."""
    table_info = _PROCESSING_DATA_TABLES.get(handler_key)
    if table_info is None:
        return {}
    table, target_key, default_target = table_info
    spec = table.get(player_data.get(target_key, default_target))
    required_items = spec.get("required_items", {}) if isinstance(spec, dict) else {}
    if not isinstance(required_items, dict):
        return {}
    return {str(item): int(amount) for item, amount in required_items.items() if isinstance(item, str)}


def _agility_target_can_damage(target_id: str) -> bool:
    target = AGILITY_TARGETS_BY_ID.get(target_id)
    if target is None:
        return False
    return (
        target.activity_kind in {"brimhaven", "gnome_ball"}
        or any(stage.can_fail for stage in target.stages)
    )


def _agility_equipment_satisfies(equipped_items: set[str], item_name: str) -> bool:
    wanted = item_name.casefold()
    return any(
        candidate.casefold() == wanted
        or (wanted == "crossbow" and "crossbow" in candidate.casefold())
        for candidate in equipped_items
    )


def _agility_casual_layout_for(player_data: dict[str, Any], target_id: str) -> dict[str, int]:
    """Build Auto mode's ordered requirement-and-food pack for one target."""

    target = AGILITY_TARGETS_BY_ID.get(target_id)
    if target is None:
        return {}
    bank = player_data.get("inventory", {}) or {}
    equipment = player_data.get("equipment", {}) or {}
    equipped_items = {
        str(item)
        for item in equipment.values()
        if isinstance(item, str)
    } if isinstance(equipment, dict) else set()
    layout: dict[str, int] = {}
    for item_name in target.required_items:
        if not _agility_equipment_satisfies(equipped_items, item_name) and int(bank.get(item_name, 0) or 0) > 0:
            layout[item_name] = 1
    for item_options in target.required_item_options:
        if any(_agility_equipment_satisfies(equipped_items, item_name) for item_name in item_options):
            continue
        stocked = next(
            (item_name for item_name in item_options if int(bank.get(item_name, 0) or 0) > 0),
            None,
        )
        if stocked is not None:
            layout[stocked] = 1
    if _agility_target_can_damage(target_id):
        for item_name in player_data.get("combat_auto_eat_food", ()) or ():
            if item_name not in COMBAT_FOOD_DATA:
                continue
            available = int(bank.get(item_name, 0) or 0)
            if available > 0:
                layout[item_name] = available
    return layout


def _agility_carried_requirement_gaps(
    player_data: dict[str, Any],
    target_id: str,
    view: dict[str, Any],
) -> tuple[str, ...]:
    target = AGILITY_TARGETS_BY_ID.get(target_id)
    if target is None:
        return ()
    equipment = player_data.get("equipment", {}) or {}
    equipped_items = {
        str(item)
        for item in equipment.values()
        if isinstance(item, str)
    } if isinstance(equipment, dict) else set()
    missing = [
        item_name
        for item_name in target.required_items
        if not _agility_equipment_satisfies(equipped_items, item_name)
        and int(view.get(item_name, 0) or 0) <= 0
    ]
    for item_options in target.required_item_options:
        if any(_agility_equipment_satisfies(equipped_items, item_name) for item_name in item_options):
            continue
        if not any(int(view.get(item_name, 0) or 0) > 0 for item_name in item_options):
            missing.append(f"{item_options[0]} or another valid alternative")
    return tuple(missing)


def _set_carried_target_map(player_data: dict[str, Any], map_key: str, target_id: str, value) -> None:
    container = player_data.get(map_key)
    if not isinstance(container, dict):
        container = {}
    if value:
        container[target_id] = value
    else:
        container.pop(target_id, None)
    player_data[map_key] = container


def _carried_target_view(player_data: dict[str, Any], target_id: str) -> dict[str, int]:
    carried = player_data.get("carried_inventory")
    view = carried.get(target_id) if isinstance(carried, dict) else None
    return dict(view) if isinstance(view, dict) else {}


def _without_urn_substitutions(inventory: dict[str, Any]) -> dict[str, Any]:
    return {item_name: amount for item_name, amount in inventory.items() if item_name not in URN_STATE_ITEM_NAMES}


def _pack_can_supply(view: dict[str, Any], requirements: dict[str, int]) -> bool:
    return all(int(view.get(item, 0) or 0) >= need for item, need in requirements.items())


def _bank_can_supply(bank: dict[str, Any], requirements: dict[str, int]) -> bool:
    return all(int(bank.get(item, 0) or 0) >= need for item, need in requirements.items())


def _owned_bag_capacities(bank: dict[str, Any]) -> dict[str, int]:
    """{material: bag capacity} for each bag the player owns (Coal bag -> Coal: 27)."""
    return {
        material: extra
        for bag_name, (material, extra) in inventory_pure.BAG_DEFINITIONS.items()
        if int(bank.get(bag_name, 0) or 0) > 0
    }


def _repack_view_for_target(
    is_processing: bool,
    advanced: bool,
    layout: dict[str, int],
    bank: dict[str, Any],
    requirements: dict[str, int],
    capacity: int,
    casual_layout: dict[str, int] | None = None,
) -> dict[str, int]:
    """The freshly-packed carried view after a completed bank run.

    Advanced targets replay their saved layout (capped by the bank). Casual
    processing targets get their recipe inputs split by
    ``pack_processing_inputs_pure``. Casual gathering targets start empty — the
    gathered product fills the pack from actions, it is never pre-loaded.
    """
    if advanced:
        # The grid is 28 cells and an inventory is 28 slots. Never pass the
        # bag-inflated capacity here: that would hand the bag's extra room to every
        # item in the layout, not just the bagged material (bags-in-the-grid is a
        # separate, unbuilt feature).
        return inventory_pure.apply_carried_layout_pure(
            bank,
            materialize_urn_layout_pure(bank, layout),
            inventory_pure.CARRIED_CAPACITY,
            _OVERLAY_STACKABLE_NAMES,
        )
    if casual_layout:
        return inventory_pure.apply_carried_layout_pure(
            bank,
            casual_layout,
            inventory_pure.CARRIED_CAPACITY,
            _OVERLAY_STACKABLE_NAMES,
        )
    if is_processing:
        # Pack against the real 28 slots and let the packer model the bag (which
        # holds its material in one slot). Inflating `capacity` instead would hand
        # the extra room to every material, not just the bagged one.
        return inventory_pure.pack_processing_inputs_pure(
            bank, requirements, inventory_pure.CARRIED_CAPACITY,
            _OVERLAY_STACKABLE_NAMES, _owned_bag_capacities(bank),
        )
    return {}


def _try_pack_yak_winter_storage_overlay(
    player_data: dict[str, Any],
    target_id: str,
    view: dict[str, int],
    churn: int,
    capacity: int,
    *,
    advanced: bool,
    force_bank: bool,
) -> tuple[dict[str, int], int, bool]:
    """Use one carried Winter Storage scroll before an otherwise-due trip."""
    state = player_data.get("summoning_state", {}) or {}
    follower = state.get("active_follower", {}) or {}
    if (
        force_bank
        or follower.get("kind") != "familiar"
        or follower.get("entity_id") != "packyak"
        or int(state.get("special_move_points_current", 0) or 0) < 12
    ):
        return view, churn, False
    policy = (state.get("target_policies", {}) or {}).get(target_id, {}) or {}
    priority = policy.get("winter_storage_priority", ()) or ()
    if isinstance(priority, str):
        priority = (priority,)
    threshold = (
        max(
            0,
            min(
                27,
                int(policy.get("winter_storage_threshold_free_slots", 0) or 0),
            ),
        )
        if advanced
        else 0
    )
    if churn < max(1, capacity - threshold):
        return view, churn, False
    scroll_name = "Winter storage scroll"
    if int(view.get(scroll_name, 0) or 0) <= 0:
        return view, churn, False
    selected = next(
        (
            item_name
            for item_name in priority
            if isinstance(item_name, str)
            and item_name != scroll_name
            and int(view.get(item_name, 0) or 0) > 0
            and (
                item_name not in _OVERLAY_STACKABLE_NAMES
                or int(view.get(item_name, 0) or 0) == 1
            )
        ),
        None,
    )
    if selected is None:
        return view, churn, False

    updated_view = dict(view)
    updated_view[selected] = int(updated_view.get(selected, 0) or 0) - 1
    updated_view[scroll_name] = int(updated_view.get(scroll_name, 0) or 0) - 1
    updated_view = {
        item_name: amount
        for item_name, amount in updated_view.items()
        if amount > 0
    }
    inventory = dict(player_data.get("inventory", {}) or {})
    inventory[scroll_name] = max(
        0, int(inventory.get(scroll_name, 0) or 0) - 1
    )
    player_data["inventory"] = inventory
    updated_state = dict(state)
    updated_state["special_move_points_current"] = (
        int(updated_state.get("special_move_points_current", 0) or 0) - 12
    )
    updated_state["event_log"] = (
        list(updated_state.get("event_log", []))
        + [
            {
                "kind": "winter_storage",
                "target_id": target_id,
                "item": selected,
                "xp": 4.8,
            }
        ]
    )[-50:]
    player_data["summoning_state"] = updated_state
    player_data["summoning_exp"] = (
        float(player_data.get("summoning_exp", 0.0) or 0.0) + 4.8
    )
    return updated_view, max(0, churn - 1), True


def run_answer_with_carried_overlay(ctx: RuntimeActionContext, handler_key: str, handler) -> bool:
    """Run one skilling tick through the 28-slot carried overlay.

    Gathering skills fill the pack with their product (Keep) or bypass it
    entirely (Drop); the pack banks when full. Processing skills instead *draw*
    their recipe inputs from the pack: the handler only sees as much of each
    required material as the pack currently holds, so the pack — not the
    infinite bank — is what limits actions-per-trip. This is what gives the
    advanced 4x7 layout real consequence: a well-arranged pack (matching a
    recipe's true ratio) yields more actions before a bank-run than an even
    casual split.

    Before the tick, the gate decides whether this answer is spent banking
    instead of acting: churn reaching capacity (either skill), or — processing
    only — the pack running out of a required input the bank could still
    supply. On a completed bank run the pack is repacked from the bank (casual
    preset / processing split, or the advanced saved layout) rather than simply
    cleared. Handlers without carried teeth run untouched unless the player
    explicitly spends that review on a bank run.
    """
    player_data = ctx.player_data
    target_key = _OVERLAY_TARGET_KEYS.get(handler_key)
    if target_key is None:
        if (
            str(player_data.get("review_bank_run_requested_handler", "") or "")
            == handler_key
        ):
            player_data.pop("review_bank_run_requested_handler", None)
            player_data.update(restore_summoning_points_pure(player_data))
            ctx.show_activity_gain("Bank run — arrived at the bank")
            ctx.save_player_data()
            return True
        return handler(ctx)

    target_id = str(player_data.get(target_key, ""))
    evil_tree_state = player_data.get("evil_tree")
    if not isinstance(evil_tree_state, dict):
        evil_tree_state = {}
    evil_tree_overflow = bool(
        handler_key == "woodcutting"
        and target_id in EVIL_TREE_ELIGIBLE_BLESSING_TARGETS
        and int(
            evil_tree_state.get("blessing_reviews_remaining", 0) or 0
        )
        > 0
    )
    target_spec = TREE_DATA.get(target_id, {}) if handler_key == "woodcutting" else {}
    is_processing = (
        handler_key in _PROCESSING_HANDLER_KEYS
        or target_spec.get("action_type") == "processing"
    )
    is_agility = handler_key == "agility"
    # Keep/Drop is a gathering-only choice; processing always draws from (and
    # refills) its pack — there is no "drop the product" for a recipe's inputs.
    keep = True if is_processing else inventory_pure.carried_keep_for(player_data, target_id)
    view = dict((player_data.get("carried_inventory") or {}).get(target_id, {}))
    churn = (player_data.get("carried_churn") or {}).get(target_id, 0)
    bank_run = player_data.get("skilling_bank_run", {})
    manual_bank_run = (
        str(player_data.get("review_bank_run_requested_target", "") or "")
        == target_id
    )
    advanced = inventory_pure.carried_advanced_for(player_data, target_id)
    layout = (player_data.get("carried_layout") or {}).get(target_id, {})
    bank = player_data.get("inventory", {}) or {}
    casual_layout = _agility_casual_layout_for(player_data, target_id) if is_agility else {}
    # A carried bag raises the bank-run threshold for its material (fewer trips).
    owned_bags = {
        bag for bag in inventory_pure.BAG_DEFINITIONS
        if int(bank.get(bag, 0) or 0) > 0
    }
    capacity = inventory_pure.effective_carried_capacity(view, owned_bags)

    carried_materials = view if view else layout if advanced else {}
    requirements = (
        _processing_requirements_for(handler_key, player_data, carried_materials)
        if is_processing else {}
    )
    presence_requirements = (
        _processing_presence_requirements_for(handler_key, player_data)
        if is_processing else {}
    )

    # First-ever engagement with a processing target seeds the pack for free —
    # you already "have inventory" the moment you arrive, same as gathering
    # starting empty; the review cost is only for *refilling after depletion*,
    # never for the initial load (owner: no free banking, but this isn't a trip).
    primed = target_id in (player_data.get("carried_primed_targets") or {})
    if (is_processing and requirements or is_agility) and not primed:
        view = _repack_view_for_target(
            is_processing,
            advanced,
            layout,
            bank,
            requirements,
            capacity,
            casual_layout,
        )
        _set_carried_target_map(player_data, "carried_primed_targets", target_id, True)
        _set_carried_target_map(player_data, "carried_inventory", target_id, view)
    elif handler_key == "hunter" and advanced and layout and not view:
        # Hunter is gathering, but target-carried passives still need the saved
        # Custom pack on the first trip rather than waiting for a bank-run cycle.
        view = _repack_view_for_target(False, True, layout, bank, {}, capacity)
        _set_carried_target_map(player_data, "carried_inventory", target_id, view)

    if is_agility and advanced:
        missing = _agility_carried_requirement_gaps(player_data, target_id, view)
        if missing:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Agility pack incomplete",
                f"Custom mode must carry or equip {', '.join(missing)} for "
                f"{AGILITY_TARGETS_BY_ID[target_id].display_name}.",
            )
            return False

    # Presence-only gates stay out of per-action packing: in default mode they
    # remain available from the bank. An advanced layout explicitly carries
    # them, however, so an emptied presence slot must trigger the normal refill
    # when the bank can restore the saved layout.
    refill_requirements = dict(requirements)
    if advanced:
        for item_name, need in presence_requirements.items():
            refill_requirements[item_name] = max(refill_requirements.get(item_name, 0), need)
    force = bool(
        is_processing and refill_requirements
        and not _pack_can_supply(view, refill_requirements)
        and _bank_can_supply(bank, refill_requirements)
    )
    desired_agility_view = (
        _repack_view_for_target(
            False,
            advanced,
            layout,
            bank,
            {},
            capacity,
            casual_layout,
        )
        if is_agility
        else {}
    )
    if desired_agility_view:
        force = force or any(
            int(view.get(item_name, 0) or 0) <= 0 and int(bank.get(item_name, 0) or 0) > 0
            for item_name in desired_agility_view
        )

    target_altar = (
        str((RUNECRAFTING_DATA.get(target_id) or {}).get("altar_id", ""))
        if handler_key == "runecrafting"
        else ""
    )
    active_target_matches = (
        isinstance(bank_run, dict)
        and bank_run.get("target_id") in (None, target_id)
        and int(bank_run.get("reviews_remaining", 0) or 0) > 0
    )
    if target_altar and active_target_matches:
        teleported_data, pending_teleport_used = consume_wicked_hood_route_teleport_pure(
            player_data, target_altar
        )
        if pending_teleport_used:
            player_data.clear()
            player_data.update(teleported_data)
            bank_run, _outbound_removed = wicked_hood_skip_active_outbound_pure(
                bank_run
            )
            player_data["skilling_bank_run"] = bank_run
            if not bank_run:
                view = _repack_view_for_target(
                    is_processing,
                    advanced,
                    layout,
                    bank,
                    requirements,
                    capacity,
                    casual_layout,
                )
                churn = 0
                force = False
                _set_carried_target_map(
                    player_data, "carried_inventory", target_id, view
                )
                _set_carried_target_map(
                    player_data, "carried_churn", target_id, churn
                )

    active_run = isinstance(bank_run, dict) and int(bank_run.get("reviews_remaining", 0) or 0) > 0
    action_ctx = ctx
    cadence_admitted = False
    cadence_profiles_present = "cadence_profiles" in player_data
    cadence_profiles_before = copy.deepcopy(player_data.get("cadence_profiles"))
    cadence_profiles_after_admission = None

    def restore_cadence_profiles_after_rejection() -> None:
        if not cadence_admitted:
            return
        if player_data.get("cadence_profiles") != cadence_profiles_after_admission:
            # A handler may own a second scheduler under the same route key
            # (Thieving stalls and wall safes). Once that scheduler advances,
            # the review was a real action attempt rather than an eligibility
            # rejection, so its cadence must survive an unsuccessful outcome.
            return
        if cadence_profiles_present:
            player_data["cadence_profiles"] = copy.deepcopy(
                cadence_profiles_before
            )
        else:
            player_data.pop("cadence_profiles", None)

    if keep and not active_run and handler_key not in {"magic", "prayer"}:
        action_ctx, cadence_admitted = _admit_live_cadence(
            ctx, handler_key, target_id
        )
        if not cadence_admitted:
            return True
        cadence_profiles_after_admission = copy.deepcopy(
            player_data.get("cadence_profiles")
        )
    winter_storage_before = None
    if keep and not active_run and not manual_bank_run:
        winter_storage_before = copy.deepcopy(player_data)
        view, churn, winter_storage_used = _try_pack_yak_winter_storage_overlay(
            player_data,
            target_id,
            view,
            int(churn or 0),
            capacity,
            advanced=advanced,
            force_bank=force,
        )
        if winter_storage_used:
            bank = player_data.get("inventory", {}) or {}
            _set_carried_target_map(
                player_data, "carried_inventory", target_id, view
            )
            _set_carried_target_map(
                player_data, "carried_churn", target_id, churn
            )
        else:
            winter_storage_before = None
    trip_due = bool(
        manual_bank_run
        or (
            keep
            and (
                active_run
                or (churn >= capacity and not evil_tree_overflow)
                or force
            )
        )
    )
    travel_profile = None
    run_energy_credit_used = 0
    reviews_cost = inventory_pure.SKILLING_BANK_RUN_REVIEWS
    route_phases = ()
    outbound_teleport_used = False
    if active_run:
        reviews_cost = max(1, int(bank_run.get("reviews_total", bank_run.get("reviews_remaining", 1)) or 1))
    elif trip_due:
        travel_profile = agility_travel_profile_pure(
            handler_key,
            target_id,
            int(player_data.get("agility_level", 1) or 1),
            view,
            player_data.get("equipment", {}),
        )
        travel_profile, run_energy_credit_used = apply_run_energy_credit_pure(
            travel_profile,
            player_data.get("agility_run_energy_credit_pct", 0),
        )
        if run_energy_credit_used:
            player_data["agility_run_energy_credit_pct"] = 0
        # The only new RNG draw happens at the moment a trip is actually due.
        scheduled_reviews = (
            scheduled_travel_reviews_pure(travel_profile, ctx.random_random())
            if travel_profile.adjusted_reviews > 0
            else 0
        )
        if target_altar:
            teleported_data, outbound_teleport_used = consume_wicked_hood_route_teleport_pure(
                player_data, target_altar
            )
            if outbound_teleport_used:
                player_data.clear()
                player_data.update(teleported_data)
            route_phases = runecrafting_route_phases_pure(
                scheduled_reviews, skip_outbound=outbound_teleport_used
            )
            reviews_cost = sum(int(phase["reviews"]) for phase in route_phases)
        else:
            reviews_cost = scheduled_reviews
        player_data["agility_last_travel"] = {
            "handler_key": handler_key,
            "target_id": target_id,
            "base_reviews": travel_profile.base_reviews,
            "adjusted_reviews": travel_profile.adjusted_reviews,
            "scheduled_reviews": scheduled_reviews,
            "charged_reviews": reviews_cost,
            "level_gain": travel_profile.level_gain,
            "weight_gain": travel_profile.weight_gain,
            "carried_weight_kg": travel_profile.carried_weight_kg,
            "effective_weight_kg": travel_profile.effective_weight_kg,
            "route_label": travel_profile.route_label,
            "source_status": travel_profile.source_status,
            "run_energy_credit_used_pct": run_energy_credit_used,
            "outbound_teleport_used": outbound_teleport_used,
        }

    if trip_due and reviews_cost <= 0:
        new_state, new_view, new_churn = {}, {}, 0
        event = {"active": True, "started": True, "completed": True, "reviews_remaining": 0, "waived": True}
        act = True
        new_view = _repack_view_for_target(
            is_processing, advanced, layout, bank, requirements, capacity, casual_layout
        )
    else:
        gate_churn = min(int(churn or 0), capacity - 1) if evil_tree_overflow and not active_run else churn
        new_state, new_view, new_churn, event, act = inventory_pure.carried_bank_run_gate_pure(
            view,
            gate_churn,
            keep or manual_bank_run,
            _OVERLAY_STACKABLE_NAMES,
            target_id,
            bank_run,
            max(1, reviews_cost),
            capacity,
            force or manual_bank_run,
        )
        if evil_tree_overflow and act:
            new_churn = int(churn or 0)
        if event.get("started") and new_state:
            new_state["reviews_total"] = max(1, reviews_cost)
            new_state["route_label"] = travel_profile.route_label if travel_profile else "Running to the bank"
            if route_phases:
                new_state["route_phases"] = list(route_phases)
            if outbound_teleport_used:
                new_state["outbound_teleport_used"] = True

    if manual_bank_run and (event.get("started") or event.get("completed")):
        player_data.pop("review_bank_run_requested_target", None)

    if event.get("completed"):
        player_data.update(restore_summoning_points_pure(player_data))

    if not act:
        restore_cadence_profiles_after_rejection()
        if event.get("completed"):
            new_view = _repack_view_for_target(
                is_processing, advanced, layout, bank, requirements, capacity, casual_layout
            )
        player_data["skilling_bank_run"] = new_state
        _set_carried_target_map(player_data, "carried_inventory", target_id, new_view)
        _set_carried_target_map(player_data, "carried_churn", target_id, new_churn)
        total = int((new_state or bank_run or {}).get("reviews_total", reviews_cost) or reviews_cost)
        remaining = int(event.get("reviews_remaining", 0) or 0)
        route_label = bank_run_phase_label_pure(new_state or bank_run)
        progress = max(1, total - remaining)
        ctx.show_activity_gain(
            f"Bank run — {route_label} · {min(progress, total)}/{total} travel reviews"
            if not event.get("completed")
            else f"Bank run — {route_label} · arrived and restocked"
        )
        ctx.save_player_data()
        return True

    # Handlers that substitute carried items (urn runed -> active -> full) must
    # see the actual trip view, including a just-seeded first trip.
    _set_carried_target_map(player_data, "carried_inventory", target_id, new_view)
    if not cadence_admitted and handler_key not in {"magic", "prayer"}:
        action_ctx, cadence_admitted = _admit_live_cadence(
            ctx, handler_key, target_id
        )
        if not cadence_admitted:
            return True
        cadence_profiles_after_admission = copy.deepcopy(
            player_data.get("cadence_profiles")
        )

    if is_processing and requirements:
        # Scope the handler's input access to what the pack holds, run it, then
        # reconcile: the real bank only loses what was actually consumed, and the
        # pack is decremented by the same amount. Every other item (outputs,
        # byproducts) passes through untouched, since it was never capped.
        scoped_inventory = dict(bank)
        for item_name, need in requirements.items():
            scoped_inventory[item_name] = min(int(bank.get(item_name, 0) or 0), int(new_view.get(item_name, 0) or 0))
        carried_presence_requirements = presence_requirements if advanced else {}
        for item_name, need in carried_presence_requirements.items():
            scoped_inventory[item_name] = min(int(bank.get(item_name, 0) or 0), int(new_view.get(item_name, 0) or 0))
        scoped_alternatives = set()
        if handler_key == "fletching":
            spec = FLETCHING_DATA.get(target_id, {})
            for alternatives in spec.get("material_options", {}).values():
                if not isinstance(alternatives, (list, tuple)):
                    continue
                for option in alternatives:
                    if isinstance(option, str):
                        scoped_alternatives.add(option)
                        if option not in requirements:
                            scoped_inventory.pop(option, None)

        # While the inventory is scoped it does NOT reflect the real bank, so the
        # handler must not persist it or evaluate anything against it. Suppress the
        # handler's save, achievement check, and skill-availability refreshes for the
        # duration and fire them once afterwards against the reconciled bank.
        # Without this a save inside the handler writes the capped bank to disk,
        # achievements gated on a bank quantity see only what fits in the pack, and
        # the skill-availability UI is computed from the pack rather than the bank.
        # `deactivate_current_skill` is deliberately left live: it must still fire
        # when materials genuinely run out, and the bank-run gate above already
        # prevents the handler from ever seeing an under-supplied pack.
        deferred_achievement_check = []
        deferred_availability_refresh = []
        scoped_ctx = dataclasses.replace(
            action_ctx,
            save_player_data=lambda: None,
            check_achievements=lambda _data: deferred_achievement_check.append(True),
            refresh_skill_availability=lambda: deferred_availability_refresh.append(True),
            # Its return value only feeds the suppressed partial refresh below.
            refresh_skill_availability_partial=lambda *_args: deferred_availability_refresh.append(True),
        )
        player_data["inventory"] = scoped_inventory
        result = handler(scoped_ctx)
        if result is False and winter_storage_before is not None:
            player_data.clear()
            player_data.update(winter_storage_before)
            restore_cadence_profiles_after_rejection()
            ctx.save_player_data()
            return False
        after_scoped = player_data.get("inventory", {}) or {}
        new_view = _carried_target_view(player_data, target_id)
        reconciled = dict(after_scoped)
        for option in scoped_alternatives - requirements.keys():
            if option in bank:
                reconciled[option] = bank[option]
            else:
                reconciled.pop(option, None)
        for item_name, _need in requirements.items():
            true_before = int(bank.get(item_name, 0) or 0)
            capped_before = int(scoped_inventory.get(item_name, 0) or 0)
            after_amount = int(after_scoped.get(item_name, 0) or 0)
            consumed = max(0, capped_before - after_amount)
            reconciled[item_name] = max(0, true_before - consumed)
            if consumed > 0:
                new_view[item_name] = max(0, int(new_view.get(item_name, 0) or 0) - consumed)
        for item_name, _need in carried_presence_requirements.items():
            true_before = int(bank.get(item_name, 0) or 0)
            capped_before = int(scoped_inventory.get(item_name, 0) or 0)
            after_amount = int(after_scoped.get(item_name, 0) or 0)
            consumed = max(0, capped_before - after_amount)
            reconciled[item_name] = max(0, true_before - consumed)
            if consumed > 0:
                new_view[item_name] = max(0, int(new_view.get(item_name, 0) or 0) - consumed)
        new_view = {name: count for name, count in new_view.items() if count > 0}
        player_data["inventory"] = reconciled
        if result is not False:
            player_data["skilling_bank_run"] = new_state
            churn_delta = inventory_pure.carried_action_churn_pure(
                _without_urn_substitutions(bank),
                _without_urn_substitutions(reconciled),
                _OVERLAY_STACKABLE_NAMES,
            )
            _set_carried_target_map(player_data, "carried_inventory", target_id, new_view)
            _set_carried_target_map(player_data, "carried_churn", target_id, new_churn + churn_delta)
        # Always run against the true bank, even on a failed tick, so a suppressed
        # save can never leave the capped inventory as the last thing written.
        if deferred_achievement_check:
            ctx.check_achievements(player_data)
        if deferred_availability_refresh:
            ctx.refresh_skill_availability()
        if result is False:
            restore_cadence_profiles_after_rejection()
        ctx.save_player_data()
        return result

    inv_before = dict(bank)
    result = handler(action_ctx)
    if result is False and winter_storage_before is not None:
        player_data.clear()
        player_data.update(winter_storage_before)
        restore_cadence_profiles_after_rejection()
        ctx.save_player_data()
        return False
    if result is not False:
        player_data["skilling_bank_run"] = new_state
        inv_after = player_data.get("inventory", {}) or {}
        post_handler_view = _carried_target_view(player_data, target_id)
        gains = {
            item_name: amount
            for item_name, amount in inventory_pure.inventory_delta_gains(inv_before, inv_after).items()
            if item_name not in URN_STATE_ITEM_NAMES
        }
        if keep:
            # Keep accrues churn and folds ordinary products into the post-handler
            # pack. Urn substitutions already happened in that pack and are not
            # products, Drop targets, or churn.
            churn_delta = inventory_pure.carried_action_churn_pure(
                _without_urn_substitutions(inv_before),
                _without_urn_substitutions(inv_after),
                _OVERLAY_STACKABLE_NAMES,
            )
            overflow_items: dict[str, int] = {}
            if evil_tree_overflow:
                post_handler_view, overflow_items = (
                    inventory_pure.carried_fold_gains_with_overflow_pure(
                        post_handler_view,
                        gains,
                        _OVERLAY_STACKABLE_NAMES,
                        capacity,
                    )
                )
            else:
                post_handler_view = inventory_pure.carried_fold_gains_pure(
                    post_handler_view,
                    gains,
                    _OVERLAY_STACKABLE_NAMES,
                )
            _set_carried_target_map(player_data, "carried_inventory", target_id, post_handler_view)
            _set_carried_target_map(
                player_data,
                "carried_churn",
                target_id,
                min(capacity, new_churn + churn_delta)
                if evil_tree_overflow
                else new_churn + churn_delta,
            )
            if overflow_items:
                ctx.show_activity_gain(
                    "Evil Tree blessing: full-pack gains sent directly to the Bank"
                )
        elif gains:
            # Drop is power-gathering: ordinary gains are destroyed, while an urn's
            # carried runed/active/full substitution remains a physical carried item.
            drained = dict(inv_after)
            for item_name, gained in gains.items():
                drained[item_name] = max(0, int(drained.get(item_name, 0) or 0) - int(gained))
            player_data["inventory"] = {name: count for name, count in drained.items() if count > 0}
        ctx.save_player_data()
    else:
        restore_cadence_profiles_after_rejection()
    return result
