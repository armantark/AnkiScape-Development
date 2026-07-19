"""Runtime review-action handlers.

This module owns review action mutations without importing Anki or Qt. The
package entrypoint passes UI/save/achievement callbacks through
``RuntimeActionContext`` so ``__init__.py`` can stay focused on hooks and state
coordination.
"""

from __future__ import annotations

import copy
import dataclasses
from dataclasses import dataclass
from typing import Any, Callable, Optional

try:
    from .combat_session import (
        wilderness_combat_risk_confirmed,
        wilderness_combat_risk_fingerprint,
    )
except ImportError:
    from combat_session import (
        wilderness_combat_risk_confirmed,
        wilderness_combat_risk_fingerprint,
    )

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
    from .agility_travel import (
        agility_travel_profile_pure,
        apply_run_energy_credit_pure,
        scheduled_travel_reviews_pure,
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
    from agility_travel import (  # type: ignore
        agility_travel_profile_pure,
        apply_run_energy_credit_pure,
        scheduled_travel_reviews_pure,
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
    from . import inventory_pure
    from .item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES
except ImportError:  # pragma: no cover - exercised via flat imports in tests
    import inventory_pure
    from item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES


@dataclass
class RuntimeActionContext:
    player_data: dict[str, Any]
    random_random: Callable[[], float]
    show_error_message: Callable[[str, str], None]
    deactivate_current_skill: Callable[[], None]
    award_skill_exp: Callable[[str, float], float]
    award_hidden_skill_exp: Callable[[str, str, float], None]
    level_up_check: Callable[[str, dict[str, Any]], None]
    check_achievements: Callable[[dict[str, Any]], None]
    save_player_data: Callable[[], None]
    refresh_skill_availability: Callable[[], None]
    refresh_skill_availability_partial: Callable[..., None]
    can_smith_any: Callable[[], bool]
    show_exp: Callable[[float], None]
    show_activity_gain: Callable[[str], None]
    implemented_exp_keys_snapshot: Callable[[], dict[str, float]]
    show_quest_exp_delta: Callable[[dict[str, float]], None]
    review_action_multiplier: int = 1
    cadence_shadow_enabled: bool = False
    cadence_live_enabled: bool = False
    cadence_forced_opportunity: bool = False
    # Fired once when the Stronghold of Security is finished, so the UI can pop
    # the boot-choice reward dialog. Optional so older call sites keep working.
    prompt_stronghold_reward: Optional[Callable[[], None]] = None
    switch_to_bankstanding: Optional[Callable[[], None]] = None


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
    cleared. Handlers without carried teeth (utility, quests) run untouched.
    """
    target_key = _OVERLAY_TARGET_KEYS.get(handler_key)
    if target_key is None:
        return handler(ctx)

    player_data = ctx.player_data
    target_id = str(player_data.get(target_key, ""))
    is_processing = handler_key in _PROCESSING_HANDLER_KEYS
    is_agility = handler_key == "agility"
    # Keep/Drop is a gathering-only choice; processing always draws from (and
    # refills) its pack — there is no "drop the product" for a recipe's inputs.
    keep = True if is_processing else inventory_pure.carried_keep_for(player_data, target_id)
    view = dict((player_data.get("carried_inventory") or {}).get(target_id, {}))
    churn = (player_data.get("carried_churn") or {}).get(target_id, 0)
    bank_run = player_data.get("skilling_bank_run", {})
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
    if keep and not active_run:
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
    trip_due = bool(keep and (active_run or churn >= capacity or force))
    travel_profile = None
    run_energy_credit_used = 0
    reviews_cost = inventory_pure.SKILLING_BANK_RUN_REVIEWS
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
        reviews_cost = (
            scheduled_travel_reviews_pure(travel_profile, ctx.random_random())
            if travel_profile.adjusted_reviews > 0
            else 0
        )
        player_data["agility_last_travel"] = {
            "handler_key": handler_key,
            "target_id": target_id,
            "base_reviews": travel_profile.base_reviews,
            "adjusted_reviews": travel_profile.adjusted_reviews,
            "level_gain": travel_profile.level_gain,
            "weight_gain": travel_profile.weight_gain,
            "carried_weight_kg": travel_profile.carried_weight_kg,
            "effective_weight_kg": travel_profile.effective_weight_kg,
            "route_label": travel_profile.route_label,
            "source_status": travel_profile.source_status,
            "run_energy_credit_used_pct": run_energy_credit_used,
        }

    if trip_due and reviews_cost <= 0:
        new_state, new_view, new_churn = {}, {}, 0
        event = {"active": True, "started": True, "completed": True, "reviews_remaining": 0, "waived": True}
        act = True
        new_view = _repack_view_for_target(
            is_processing, advanced, layout, bank, requirements, capacity, casual_layout
        )
    else:
        new_state, new_view, new_churn, event, act = inventory_pure.carried_bank_run_gate_pure(
            view, churn, keep, _OVERLAY_STACKABLE_NAMES, target_id, bank_run,
            max(1, reviews_cost), capacity, force,
        )
        if event.get("started") and new_state:
            new_state["reviews_total"] = max(1, reviews_cost)
            new_state["route_label"] = travel_profile.route_label if travel_profile else "Running to the bank"

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
        route_label = str((new_state or bank_run or {}).get("route_label", "Running to the bank"))
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
            post_handler_view = inventory_pure.carried_fold_gains_pure(
                post_handler_view,
                gains,
                _OVERLAY_STACKABLE_NAMES,
            )
            _set_carried_target_map(player_data, "carried_inventory", target_id, post_handler_view)
            _set_carried_target_map(player_data, "carried_churn", target_id, new_churn + churn_delta)
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
    if info.get("status") == "executed":
        for skill, xp_key in (
            ("Farming", "farming_xp"),
            ("Woodcutting", "woodcutting_xp"),
            ("Agility", "agility_xp"),
            ("Magic", "magic_xp"),
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
        gained = sum(
            float(info.get(key, 0.0) or 0.0)
            for key in (
                "farming_xp",
                "woodcutting_xp",
                "agility_xp",
                "magic_xp",
            )
        )
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
    }


def handle_farming_queue_answer(ctx: RuntimeActionContext) -> bool:
    """Consume and persist one queued field step, including an invalid skip."""

    old_levels = _farming_levels_before_answer(ctx)
    updated, consumed, info = consume_next_farm_queue_step_pure(ctx.player_data, ctx.random_random)
    consumed = _apply_farming_queue_result(ctx, old_levels, updated, consumed, info)
    if consumed:
        ctx.save_player_data()
    return consumed


def handle_farming_review_answer(ctx: RuntimeActionContext) -> bool:
    """Apply one successful review's queued detour and eager clock tick once."""

    old_levels = _farming_levels_before_answer(ctx)
    updated, consumed, info = apply_farming_review_with_queue_pure(ctx.player_data, ctx.random_random)
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


def handle_combat_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target_id = player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    if target_id not in COMBAT_ENEMY_DATA:
        target_id = DEFAULT_COMBAT_TARGET
        player_data["current_combat_target"] = target_id

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
    drops = result.get("drops", {}) if isinstance(result, dict) else {}
    if not isinstance(drops, dict):
        drops = {}
    # Loot filter (owner: no auto-hoarding every tiny drop). The burst already
    # added the drops to the flat inventory, so leave below-value junk by removing
    # it again; stackables, coins, and unknown-value items are kept.
    if drops:
        threshold = player_data.get("loot_value_threshold", inventory_pure.DEFAULT_LOOT_VALUE_THRESHOLD)
        overrides = dict(player_data.get("loot_overrides") or {})
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
            carried = player_data.get("carried_inventory")
            if not isinstance(carried, dict):
                carried = {}
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
    return True


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


def _refresh_smithing_and_crafting_availability(ctx: RuntimeActionContext) -> None:
    player_data = ctx.player_data
    try:
        can_craft_any = any(
            can_craft_item_pure(player_data.get("crafting_level", 1), player_data.get("inventory", {}), item_name, CRAFTING_DATA)
            for item_name in CRAFTING_DATA.keys()
        )
        ctx.refresh_skill_availability_partial(ctx.can_smith_any(), can_craft_any)
    except Exception:
        pass

    ctx.refresh_skill_availability()


def handle_crafting_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    item = player_data.get("current_craft", "form_pot_unfired")
    spec = CRAFTING_DATA.get(item)
    display_name = spec.get("display_name", item) if spec else item
    if not spec:
        ctx.show_error_message("Unknown crafting target", "Choose a valid Crafting target before reviewing.")
        return False

    player_level = player_data.get("crafting_level", 1)
    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Crafting to make {display_name}.")
        return False

    required_items = dict(spec.get("requirements", {}))
    required_items.update(spec.get("required_items", {}))
    if not has_crafting_materials_pure(item, player_data["inventory"], CRAFTING_DATA):
        missing = missing_materials_text(required_items, player_data["inventory"])
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to craft {display_name}, so AnkiScape switched to "
            "Bankstanding. Choose another target when you are ready.",
        )
        return False

    thread_roll = min(int(ctx.random_random() * 5), 4) + 1 if spec.get("consume_thread_on_roll") else None
    new_inv, base_exp, ok = apply_crafting_pure(item, player_data["inventory"], CRAFTING_DATA, thread_roll)
    if not ok:
        missing = missing_materials_text(required_items, player_data["inventory"])
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to craft {display_name}, so AnkiScape switched to "
            "Bankstanding. Choose another target when you are ready.",
        )
        return False

    player_data["inventory"] = new_inv
    _record_action(ctx, "crafting", item, True, expected_success_chance=1.0, output_items=_spec_output_items(spec))
    exp_gained = ctx.award_skill_exp("crafting_exp", base_exp)
    ctx.level_up_check("Crafting", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()

    try:
        can_craft_any = any(
            can_craft_item_pure(player_data.get("crafting_level", 1), player_data.get("inventory", {}), item_name, CRAFTING_DATA)
            for item_name in CRAFTING_DATA.keys()
        )
        ctx.refresh_skill_availability_partial(ctx.can_smith_any(), can_craft_any)
    except Exception:
        pass

    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


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


def handle_utility_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    activity_key = player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
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
                f"☠ YOU DIED — {result['display_name']} failure"
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
        ctx.show_activity_gain(
            str(spec.get("status_message", display_name))
        )
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


def handle_fletching_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_fletch", DEFAULT_FLETCHING_TARGET)
    if target not in FLETCHING_DATA:
        target = DEFAULT_FLETCHING_TARGET
        player_data["current_fletch"] = target
    spec = FLETCHING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("fletching_level", 1)
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

    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Fletching to make {display_name}.")
        return False

    new_inv, base_exp, ok = apply_fletching_pure(target, player_data["inventory"], FLETCHING_DATA)
    if not ok:
        missing = missing_materials_text(spec.get("requirements", {}), player_data["inventory"])
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to make {display_name}, so AnkiScape switched to "
            "Bankstanding. Choose another target when you are ready.",
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
        target = DEFAULT_HERBLORE_TARGET
        player_data["current_herblore"] = target
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
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to make {display_name}, so AnkiScape switched to "
            "Bankstanding. Choose another target when you are ready.",
        )
        return False

    player_data["inventory"] = new_inv
    _record_action(ctx, "herblore", target, True, expected_success_chance=1.0, output_items=_spec_output_items(spec))
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
        target = DEFAULT_SUMMONING_TARGET
        player_data["current_summoning"] = target
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
        _switch_material_failure_to_bankstanding(ctx)
        missing = ", ".join(
            reason.removeprefix("Missing ")
            for reason in result.get("locked_reasons", ())
            if str(reason).startswith("Missing ")
        )
        ctx.show_error_message(
            "Out of Summoning materials",
            f"You need {missing or 'the source recipe'} for "
            f"{action.display_name.lower()}, so AnkiScape switched to Bankstanding.",
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
        target = DEFAULT_PRAYER_TARGET
        player_data["current_prayer"] = target
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
            _switch_material_failure_to_bankstanding(ctx)
        else:
            ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Prayer target unavailable",
            f"{display_name} requires {', '.join(locked)}, so "
            + (
                "AnkiScape switched to Bankstanding."
                if materials_only
                else "Prayer has been switched off."
            ),
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
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You no longer have the materials for {display_name}, so AnkiScape "
            "switched to Bankstanding.",
        )
        return False
    player_data["inventory"] = new_inventory
    player_data["prayer_actions_completed"] = int(player_data.get("prayer_actions_completed", 0) or 0) + 1
    if spec.get("method") == "bury":
        player_data["prayer_bury_count"] = int(player_data.get("prayer_bury_count", 0) or 0) + 1
    _record_action(ctx, "prayer", target, True, expected_success_chance=1.0, output_items=outputs)
    if spec.get("method") == "gilded_altar":
        source_base = base_exp / 3.5
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
        target = DEFAULT_CONSTRUCTION_TARGET
        player_data["current_construction"] = target
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
            _switch_material_failure_to_bankstanding(ctx)
        else:
            ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Construction target unavailable",
            f"{spec.get('display_name', target)} requires {', '.join(locked)}, so "
            + (
                "AnkiScape switched to Bankstanding."
                if materials_only
                else "Construction has been switched off."
            ),
        )
        return False
    updated, rewards, ok = apply_construction_action_pure(
        player_data, target, CONSTRUCTION_DATA, SERVANT_DATA, NAIL_DATA,
        ctx.random_random,
    )
    if not ok:
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You no longer have the materials for {spec.get('display_name', target)}, "
            "so AnkiScape switched to Bankstanding.",
        )
        return False
    player_data.update(updated)
    skill = "magic" if target.startswith("tablet_") else "construction"
    exp_gained = ctx.award_skill_exp(f"{skill}_exp", float(rewards.get(skill, 0.0) or 0.0))
    ctx.level_up_check("Magic" if skill == "magic" else "Construction", player_data)
    _record_action(ctx, "construction", target, True, expected_success_chance=1.0, output_items=rewards.get("outputs", {}))
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def _magic_alch_values() -> dict[str, int]:
    return {
        item.storage_key: int(SHOP_PLAYER_BUY_PRICES[item.storage_key])
        for item in ITEM_DEFINITIONS
        if bool(item.tradeable) and item.storage_key in SHOP_PLAYER_BUY_PRICES
    }


def handle_magic_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_magic", DEFAULT_MAGIC_TARGET)
    if target not in MAGIC_DATA:
        target = DEFAULT_MAGIC_TARGET
        player_data["current_magic"] = target
    spec = MAGIC_DATA[target]
    display_name = str(spec.get("display_name", target))

    def _magic_materials_only(reasons) -> bool:
        gate_reason = (
            str(spec.get("quest_gate")).replace("_", " ").title()
            if spec.get("quest_gate")
            else ""
        )
        for reason in reasons:
            text = str(reason)
            if (
                " level " in f" {text} "
                or (gate_reason and text == gate_reason)
                or text.startswith(("Attune ", "Choose "))
                or (
                    target in {"cure_plant", "fertile_soil"}
                    and " x" not in text
                )
            ):
                return False
        return bool(reasons)

    if ctx.cadence_live_enabled:
        locked = magic_target_locked_reasons_pure(
            player_data, target, MAGIC_DATA, _magic_alch_values()
        )
        if locked:
            materials_only = _magic_materials_only(locked)
            if materials_only:
                _switch_material_failure_to_bankstanding(ctx)
            else:
                ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Magic target unavailable",
                f"{display_name} requires {', '.join(locked)}, so "
                + (
                    "AnkiScape switched to Bankstanding."
                    if materials_only
                    else "Magic has been switched off."
                ),
            )
            return False
        ctx, admitted = _admit_live_cadence(ctx, "magic", target)
        if not admitted:
            return True
    new_data, magic_xp, secondary, outputs, ok, message = apply_magic_action_pure(
        player_data, target, MAGIC_DATA, _magic_alch_values(), ctx.random_random
    )
    if not ok:
        reasons = magic_target_locked_reasons_pure(player_data, target, MAGIC_DATA, _magic_alch_values())
        materials_only = _magic_materials_only(reasons)
        if materials_only:
            _switch_material_failure_to_bankstanding(ctx)
        else:
            ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Magic target unavailable",
            f"{display_name} requires {', '.join(reasons) or message}, so "
            + (
                "AnkiScape switched to Bankstanding."
                if materials_only
                else "Magic has been switched off."
            ),
        )
        return False

    player_data.clear()
    player_data.update(new_data)
    player_data["magic_actions_completed"] = int(player_data.get("magic_actions_completed", 0) or 0) + 1
    _record_action(ctx, "magic", target, True, expected_success_chance=1.0, output_items=outputs)
    exp_gained = ctx.award_skill_exp("magic_exp", magic_xp)
    ctx.level_up_check("Magic", player_data)
    for skill_id, amount in secondary.items():
        if float(amount or 0) <= 0:
            continue
        ctx.award_hidden_skill_exp(f"{skill_id}_exp", f"{skill_id}_level", float(amount))
        ctx.level_up_check(skill_id.title(), player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    if target == "monster_examine":
        examined = player_data.get("magic_last_examine", {}) or {}
        stats = examined.get("stats", {}) or {}
        ctx.show_activity_gain(f"{examined.get('display_name', 'Target')}: {stats}")
    return True


def handle_firemaking_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_firemaking", DEFAULT_FIREMAKING_TARGET)
    if target not in FIREMAKING_DATA:
        target = DEFAULT_FIREMAKING_TARGET
        player_data["current_firemaking"] = target
    spec = FIREMAKING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("firemaking_level", 1)
    success_level = familiar_effective_roll_level_pure(
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
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to burn {display_name}, so AnkiScape switched to "
            "Bankstanding. Choose another target when you are ready.",
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


def handle_fishing_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_fishing", DEFAULT_FISHING_TARGET)
    if target not in FISHING_DATA:
        target = DEFAULT_FISHING_TARGET
        player_data["current_fishing"] = target
    spec = FISHING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("fishing_level", 1)
    success_level = familiar_effective_roll_level_pure(
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

    player_data["inventory"] = new_inv
    _charge_urn_for_action(ctx, "fishing", target, spec, base_exp, _output_item)
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
    success_level = familiar_effective_roll_level_pure(
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
    )
    if not ok:
        _record_action(ctx, "hunter", target, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()
        return True

    player_data["inventory"] = new_inv
    produced_outputs = _spec_output_items(spec, _output_item)
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
    return True


def handle_cooking_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_cooking", DEFAULT_COOKING_TARGET)
    if target not in COOKING_DATA:
        target = DEFAULT_COOKING_TARGET
        player_data["current_cooking"] = target
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
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to {str(display_name).lower()}, so AnkiScape "
            "switched to Bankstanding. Choose another target when you are ready.",
        )
        return False

    embedded_probability = bool(
        ctx.cadence_live_enabled
        and resolve_live_cadence_route_pure("cooking", target, player_data).mode
        == EMBEDDED_PROBABILITY
    )
    expected_success = (
        cooking_source_roll_chance_pure(player_level, spec)
        if embedded_probability
        else calculate_cooking_success_probability_pure(player_level, spec)
    )
    roll = ctx.random_random()
    source_success = cooking_source_roll_chance_pure(player_level, spec)
    source_runtime_action = bool(spec.get("source_success_formula") or spec.get("source_always_succeeds"))
    proposed_outcome_success = roll <= source_success if source_runtime_action else roll < source_success
    byproduct_roll = ctx.random_random() if spec.get("byproduct_item") and roll <= expected_success else None
    inventory_before = dict(player_data.get("inventory", {}) or {})
    new_inv, base_exp, ok, output_item, burned = apply_cooking_action_pure(
        target,
        inventory_before,
        COOKING_DATA,
        player_level,
        roll,
        byproduct_roll,
        use_source_probability=embedded_probability,
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
    ctx.show_exp(exp_gained)
    return True


def handle_runecrafting_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_runecrafting", DEFAULT_RUNECRAFTING_TARGET)
    if target not in RUNECRAFTING_DATA:
        target = DEFAULT_RUNECRAFTING_TARGET
        player_data["current_runecrafting"] = target
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
            str(spec.get("input_item", "")),
        }
        materials_only = bool(reasons) and all(
            str(reason) in material_reasons
            for reason in reasons
        )
        if materials_only:
            _switch_material_failure_to_bankstanding(ctx)
        else:
            ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Runecrafting unavailable",
            f"{display_name} cannot run right now, so "
            + (
                "AnkiScape switched to Bankstanding."
                if materials_only
                else "Runecrafting has been switched off."
            ),
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
    exp_gained = ctx.award_skill_exp("runecrafting_exp", base_exp)
    ctx.level_up_check("Runecrafting", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if exp_gained > 0:
        ctx.show_exp(exp_gained)
    elif message:
        ctx.show_activity_gain(str(message))
    return True


def handle_quest_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    quest_id = player_data.get("current_quest", "rune_mysteries")
    if quest_id not in QUEST_DATA:
        quest_id = "rune_mysteries"
        player_data["current_quest"] = quest_id
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
            ticks=None if ctx.cadence_live_enabled else _combat_review_ticks(ctx),
            stop_after_first_kill=ctx.cadence_live_enabled,
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
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Quest blocked",
            f"{quest.get('display_name', quest_id)} is blocked: {', '.join(stage_blocker_reasons)}. "
            "Questing has been switched off until the current stage requirements are met.",
        )
        return False
    if not can_start_quest_pure(player_data, quest_id, QUEST_DATA):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Quest unavailable",
            f"{quest.get('display_name', quest_id)} cannot progress right now, so questing has been switched off.",
        )
        return False

    exp_before = ctx.implemented_exp_keys_snapshot()
    new_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
    if not ok:
        stage_blocker_reasons = quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
        if stage_blocker_reasons:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Quest blocked",
                f"{quest.get('display_name', quest_id)} is blocked: {', '.join(stage_blocker_reasons)}. "
                "Questing has been switched off until the current stage requirements are met.",
            )
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
        target = DEFAULT_SMITHING_TARGET
        player_data["current_smith"] = target
    spec = SMITHING_DATA[target]
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
    expected_success_chance = smithing_success_probability_pure(
        target,
        spec,
        player_level,
        has_ring_of_forging=has_forging_ring,
    )
    roll = ctx.random_random() if expected_success_chance < 1.0 else 0.0
    new_inv, base_exp, processed, output_item, failed = apply_smithing_action_pure(
        target,
        player_data["inventory"],
        SMITHING_DATA,
        player_level,
        roll,
        has_ring_of_forging=has_forging_ring,
    )
    if not processed:
        missing_requirements = dict(spec.get("requirements", {}))
        missing_requirements.update(spec.get("required_items", {}))
        missing = missing_materials_text(missing_requirements, player_data["inventory"])
        _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to make {display_name}, so AnkiScape switched to "
            "Bankstanding. Choose another target when you are ready.",
        )
        return False

    player_data["inventory"] = new_inv
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
        _refresh_smithing_and_crafting_availability(ctx)
        ctx.show_activity_gain("The ore was too impure")
        return True

    _charge_urn_for_action(ctx, "smithing", target, spec, base_exp, output_item)
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

    _refresh_smithing_and_crafting_availability(ctx)
    ctx.show_exp(exp_gained)
    return True


def handle_woodcutting_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    tree = player_data.get("current_tree", DEFAULT_WOODCUTTING_TARGET)
    if tree not in TREE_DATA:
        tree = DEFAULT_WOODCUTTING_TARGET
        player_data["current_tree"] = tree
    spec = TREE_DATA[tree]
    player_level = player_data.get("woodcutting_level", 1)
    success_level = familiar_effective_roll_level_pure(
        player_data, "woodcutting", player_level
    )

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Woodcutting to chop {spec.get('display_name', tree)}.")
        return False

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
        BIRD_NEST_DROP_CHANCE,
        r_inferno_adze,
        success_level,
    )
    if ok:
        if "logs_cut_today" not in player_data:
            player_data["logs_cut_today"] = 0
        player_data["logs_cut_today"] += 1
        player_data["inventory"] = new_inv
        _charge_urn_for_action(ctx, "woodcutting", tree, spec, base_exp, output_item)
        output_items: dict[str, int] = {}
        for item_name in (output_item, nest_item):
            if item_name:
                output_items[item_name] = output_items.get(item_name, 0) + 1
        _record_action(
            ctx,
            "woodcutting",
            tree,
            True,
            expected_success_chance=expected_success,
            output_items=output_items,
            achievement_output_items=(
                output_items
                if output_item is not None or not spec.get("output_item")
                else {str(spec.get("output_item")): 1, **output_items}
            ),
            primary_xp=base_exp,
        )
        exp_gained = ctx.award_skill_exp("woodcutting_exp", base_exp)
        ctx.level_up_check("Woodcutting", player_data)
        if output_item is None and spec.get("output_item") and axe_spec.get("incinerates_logs", False):
            ctx.award_skill_exp("firemaking_exp", base_exp)
            ctx.level_up_check("Firemaking", player_data)
        ctx.check_achievements(player_data)
        ctx.save_player_data()
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
    success_level = familiar_effective_roll_level_pure(
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

    new_inv, base_exp, ok, output_item, gem, extra_output = apply_mining_action_pure(
        ore,
        player_data.get("inventory", {}),
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
    if ok:
        if "ores_mined_today" not in player_data:
            player_data["ores_mined_today"] = 0
        player_data["ores_mined_today"] += 1
        player_data["inventory"] = new_inv
        _charge_urn_for_action(ctx, "mining", ore, ore_spec, base_exp, output_item)
        output_items: dict[str, int] = {}
        for item_name in (output_item, gem, extra_output):
            if item_name:
                output_items[item_name] = output_items.get(item_name, 0) + 1
        _record_action(
            ctx,
            "mining",
            ore,
            True,
            expected_success_chance=expected_success,
            output_items=output_items,
            primary_xp=base_exp,
        )
        exp_gained = ctx.award_skill_exp("mining_exp", base_exp)
        ctx.level_up_check("Mining", player_data)
        ctx.check_achievements(player_data)
        ctx.save_player_data()

        ctx.refresh_skill_availability()
        ctx.show_exp(exp_gained)
    else:
        _record_action(ctx, "mining", ore, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()
    return True


def _can_start_fletching_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_fletch", DEFAULT_FLETCHING_TARGET)
    return not fletching_target_locked_reasons_pure(
        ctx.player_data,
        target,
        FLETCHING_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_herblore_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_herblore", DEFAULT_HERBLORE_TARGET)
    return not herblore_target_locked_reasons_pure(
        ctx.player_data,
        target,
        HERBLORE_DATA,
        QUEST_UNLOCK_RULES,
    )


def _thieving_rng_index(ctx: RuntimeActionContext, size: int) -> int:
    return min(max(int(ctx.random_random() * max(size, 1)), 0), max(size - 1, 0))


def _thieving_grant_outputs(player_data: dict[str, Any], outputs: dict[str, int]) -> None:
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


def handle_agility_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target_id = str(player_data.get("current_agility", DEFAULT_AGILITY_TARGET))
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


def _can_start_prayer_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_prayer", DEFAULT_PRAYER_TARGET)
    if prayer_target_locked_reasons_pure(ctx.player_data, target, PRAYER_DATA):
        return False
    if str(target).startswith("gilded_altar_") and ctx.player_data.get("prayer_gilded_mode") == "owned":
        return not owned_gilded_altar_access_reasons_pure(ctx.player_data, target)
    return True


def _can_start_magic_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_magic", DEFAULT_MAGIC_TARGET)
    return not magic_target_locked_reasons_pure(ctx.player_data, target, MAGIC_DATA, _magic_alch_values())


def _can_start_construction_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_construction", DEFAULT_CONSTRUCTION_TARGET)
    return not construction_target_locked_reasons_pure(
        ctx.player_data, target, CONSTRUCTION_DATA, ROOM_DATA, SERVANT_DATA,
        NAIL_DATA, WORKBENCH_TIERS,
    )


def _can_start_firemaking_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_firemaking", DEFAULT_FIREMAKING_TARGET)
    return not firemaking_target_locked_reasons_pure(
        ctx.player_data,
        target,
        FIREMAKING_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_fishing_action(ctx: RuntimeActionContext) -> bool:
    return not fishing_method_locked_reasons_pure(
        ctx.player_data,
        ctx.player_data.get("current_fishing", DEFAULT_FISHING_TARGET),
        FISHING_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_hunter_action(ctx: RuntimeActionContext) -> bool:
    return not hunter_target_locked_reasons_pure(
        ctx.player_data,
        ctx.player_data.get("current_hunter", DEFAULT_HUNTER_TARGET),
        HUNTER_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_cooking_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_cooking", DEFAULT_COOKING_TARGET)
    return not cooking_target_locked_reasons_pure(
        ctx.player_data,
        target,
        COOKING_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_runecrafting_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_runecrafting", DEFAULT_RUNECRAFTING_TARGET)
    return can_runecraft_target_pure(
        ctx.player_data,
        target,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_combat_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    return not combat_target_locked_reasons_pure(
        ctx.player_data,
        target,
        COMBAT_ENEMY_DATA,
        equipment_data=EQUIPMENT_DATA,
    )


def _can_start_quest_action(ctx: RuntimeActionContext) -> bool:
    quest_id = ctx.player_data.get("current_quest", "rune_mysteries")
    return can_attempt_quest_review_pure(ctx.player_data, quest_id, QUEST_DATA)


def _can_start_crafting_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_craft", "form_pot_unfired")
    return can_craft_item_pure(
        ctx.player_data.get("crafting_level", 1),
        ctx.player_data.get("inventory", {}),
        target,
        CRAFTING_DATA,
    )


def _can_start_smithing_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_smith", DEFAULT_SMITHING_TARGET)
    return not smithing_target_locked_reasons_pure(
        ctx.player_data,
        target,
        SMITHING_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_utility_action(ctx: RuntimeActionContext) -> bool:
    activity_key = ctx.player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
    if activity_key == STRONGHOLD_UTILITY_KEY:
        state = ctx.player_data.get("stronghold_of_security") or {}
        return not state.get("completed")
    if activity_key == KNIGHT_WAVES_UTILITY_KEY:
        return not knight_waves_locked_reasons_pure(ctx.player_data)
    if activity_key == MAGE_ARENA_UTILITY_KEY:
        return not mage_arena_locked_reasons_pure(ctx.player_data)
    if str(activity_key).startswith(MAGE_ARENA_ATTUNE_PREFIX):
        god_id = str(activity_key).removeprefix(MAGE_ARENA_ATTUNE_PREFIX)
        _updated, ok, _info = attune_mage_arena_spell_pure(
            ctx.player_data,
            god_id,
        )
        return ok
    if activity_key == LIVID_FARM_ACTIVITY_ID:
        return not livid_farm_locked_reasons_pure(ctx.player_data)
    return not utility_activity_locked_reasons_pure(
        ctx.player_data,
        activity_key,
        UTILITY_ACTIVITY_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_thieving_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_thieving", DEFAULT_THIEVING_TARGET)
    return not thieving_target_locked_reasons_pure(
        ctx.player_data, target, THIEVING_TARGETS
    )


def _can_start_agility_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_agility", DEFAULT_AGILITY_TARGET)
    return not agility_target_locked_reasons_pure(ctx.player_data, str(target))


def _can_start_woodcutting_action(ctx: RuntimeActionContext) -> bool:
    return can_chop_woodcutting_target_pure(
        ctx.player_data.get("woodcutting_level", 1),
        ctx.player_data.get("current_tree", DEFAULT_WOODCUTTING_TARGET),
        TREE_DATA,
        ctx.player_data.get("inventory", {}),
        ctx.player_data.get("toolbelt", {}),
        WOODCUTTING_AXE_DATA,
    )


def _can_start_mining_action(ctx: RuntimeActionContext) -> bool:
    return not mining_target_locked_reasons_pure(
        ctx.player_data,
        ctx.player_data.get("current_ore", DEFAULT_MINING_TARGET),
        ORE_DATA,
        MINING_PICKAXE_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_summoning_action(ctx: RuntimeActionContext) -> bool:
    target = str(
        ctx.player_data.get("current_summoning", DEFAULT_SUMMONING_TARGET)
    )
    return not summoning_action_locked_reasons_pure(
        ctx.player_data, target
    )


CAN_START_HANDLERS: dict[str, Callable[[RuntimeActionContext], bool]] = {
    "mining": _can_start_mining_action,
    "woodcutting": _can_start_woodcutting_action,
    "smithing": _can_start_smithing_action,
    "crafting": _can_start_crafting_action,
    "fletching": _can_start_fletching_action,
    "firemaking": _can_start_firemaking_action,
    "fishing": _can_start_fishing_action,
    "hunter": _can_start_hunter_action,
    "cooking": _can_start_cooking_action,
    "runecrafting": _can_start_runecrafting_action,
    "herblore": _can_start_herblore_action,
    "prayer": _can_start_prayer_action,
    "magic": _can_start_magic_action,
    "construction": _can_start_construction_action,
    "thieving": _can_start_thieving_action,
    "agility": _can_start_agility_action,
    "summoning": _can_start_summoning_action,
    "combat": _can_start_combat_action,
    "utility": _can_start_utility_action,
    "quest": _can_start_quest_action,
}


ANSWER_HANDLERS: dict[str, Callable[[RuntimeActionContext], bool]] = {
    "mining": handle_mining_answer,
    "woodcutting": handle_woodcutting_answer,
    "smithing": handle_smithing_answer,
    "crafting": handle_crafting_answer,
    "fletching": handle_fletching_answer,
    "firemaking": handle_firemaking_answer,
    "fishing": handle_fishing_answer,
    "hunter": handle_hunter_answer,
    "cooking": handle_cooking_answer,
    "runecrafting": handle_runecrafting_answer,
    "herblore": handle_herblore_answer,
    "prayer": handle_prayer_answer,
    "magic": handle_magic_answer,
    "construction": handle_construction_answer,
    "thieving": handle_thieving_answer,
    "agility": handle_agility_answer,
    "summoning": handle_summoning_answer,
    "combat": handle_combat_answer,
    "utility": handle_utility_answer,
    "quest": handle_quest_answer,
}


def can_start_action(ctx: RuntimeActionContext, handler_key: Optional[str]) -> bool:
    checker = CAN_START_HANDLERS.get(str(handler_key or ""))
    return checker(ctx) if checker is not None else True


def answer_handler_for_key(handler_key: Optional[str]) -> Optional[Callable[[RuntimeActionContext], bool]]:
    return ANSWER_HANDLERS.get(str(handler_key or ""))
