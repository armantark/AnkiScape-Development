# storage_pure.py - Pure helpers for migrating and defaulting player data (no Anki deps)
import math
from typing import Dict, Iterable, Optional, Any

try:
    from .cadence_kernel import default_cadence_kernel_state_pure, sanitize_cadence_kernel_state_pure
    from . import inventory_pure
    from .cooking_data import DEFAULT_COOKING_TARGET, COOKING_TARGETS_BY_ID
    from .crafting_data import (
        DEFAULT_CRAFTING_TARGET,
        CRAFTING_RECIPES_BY_ID,
        LEGACY_CRAFTING_ITEM_MIGRATIONS,
        LEGACY_CRAFTING_TARGETS,
    )
    from .item_registry import ItemDefinition
    from .equipment_instance_logic import (
        default_equipment_instance_state_pure,
        sanitize_equipment_instance_state_pure,
    )
    from .equipment_condition_data import EQUIPMENT_CONDITION_DATA
    from .barrows_logic import default_barrows_state_pure, sanitize_barrows_state_pure
    from .fist_of_guthix_logic import (
        default_fist_of_guthix_state_pure,
        sanitize_fist_of_guthix_state_pure,
    )
    from .fight_caves_logic import (
        default_fight_caves_state_pure,
        sanitize_fight_caves_state_pure,
    )
    from .stealing_creation_logic import (
        default_stealing_creation_state_pure,
        sanitize_stealing_creation_state_pure,
    )
    from .urn_data import URN_PLAIN_TO_RUNED_ITEM, default_urn_state_pure, sanitize_urn_state_pure
    from .constants import (
        BAR_DATA,
        EXP_TABLE,
        FISHING_OUTPUT_ITEMS,
        GEM_DATA,
        HERBLORE_FINISHED_OUTPUT_ITEMS,
        MINING_OUTPUT_ITEMS,
        RUNECRAFTING_RUNE_OUTPUT_ITEMS,
        WOODCUTTING_LOG_ITEMS,
    )
    from .quest_data import DEFAULT_QUEST_TARGET, default_claim_states, default_quest_states
    from .runecrafting_data import DEFAULT_RUNECRAFTING_TARGET, RUNECRAFTING_TARGETS_BY_ID
    from .firemaking_data import DEFAULT_FIREMAKING_TARGET, FIREMAKING_TARGETS_BY_ID
    from .fishing_data import DEFAULT_FISHING_TARGET, FISHING_METHODS_BY_ID
    from .hunter_data import DEFAULT_HUNTER_TARGET, HUNTER_TARGETS_BY_ID
    from .herblore_data import DEFAULT_HERBLORE_TARGET, HERBLORE_TARGETS_BY_ID
    from .fletching_data import DEFAULT_FLETCHING_TARGET, FLETCHING_TARGETS_BY_ID, LEGACY_FLETCHING_TARGETS
    from .logic_pure import (
        default_action_telemetry_pure,
        default_achievement_progress_pure,
        default_combat_state_pure,
        default_mage_arena_state_pure,
        MAGE_ARENA_GOD_DATA,
        default_quest_combat_active_encounters_pure,
        default_quest_combat_config_pure,
        default_red_sandstone_daily_state_pure,
        default_stronghold_state_pure,
        calculate_new_level,
        sanitize_action_telemetry_pure,
        sanitize_achievement_progress_pure,
        sanitize_combat_state_pure,
        sanitize_mage_arena_state_pure,
        sanitize_quest_combat_active_encounters_pure,
        sanitize_quest_combat_config_pure,
        red_sandstone_daily_state_pure,
        sanitize_stronghold_state_pure,
    )
    from .shop_logic import default_shop_state_pure, sanitize_shop_state_pure
    from .grand_exchange_logic import default_ge_state_pure, sanitize_ge_state_pure
    from .big_chinchompa_data import (
        BIG_CHINCHOMPA_TICKET_BY_TARGET,
        WORLD_POPULATION_PROFILES,
    )
    from .big_chinchompa_logic import (
        default_big_chinchompa_state_pure,
        sanitize_big_chinchompa_state_pure,
    )
    from .evil_tree_logic import (
        default_evil_tree_state_pure,
        sanitize_evil_tree_state_pure,
    )
    from .shooting_star_logic import (
        default_shooting_star_state_pure,
        sanitize_shooting_star_state_pure,
    )
    from .sorceress_garden_logic import (
        default_sorceress_garden_state_pure,
        sanitize_sorceress_garden_state_pure,
    )
    from .penguin_hide_and_seek_logic import (
        default_penguin_state_pure,
        sanitize_penguin_state_pure,
    )
    from .pyramid_plunder_logic import (
        default_pyramid_plunder_state_pure,
        sanitize_pyramid_plunder_state_pure,
    )
    from .werewolf_skullball_data import WEREWOLF_SKULLBALL_ACTIVITY_ID
    from .werewolf_skullball_logic import (
        default_werewolf_skullball_state_pure,
        sanitize_werewolf_skullball_state_pure,
    )
    from .gnome_ball_data import GNOME_BALL_ACTIVITY_ID
    from .gnome_ball_logic import (
        default_gnome_ball_state_pure,
        sanitize_gnome_ball_state_pure,
    )
    from .fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID
    from .fish_flingers_logic import (
        default_fish_flingers_state_pure,
        sanitize_fish_flingers_state_pure,
    )
    from .vinesweeper_logic import (
        default_vinesweeper_state_pure,
        sanitize_vinesweeper_state_pure,
    )
    from .farming_logic import default_farming_state_pure, sanitize_farming_state_pure
    from .mining_data import DEFAULT_MINING_TARGET, DEFAULT_MINING_TOOLBELT, LEGACY_ORE_TARGETS
    from .smithing_data import (
        DEFAULT_SMITHING_TARGET,
        LEGACY_BAR_STORAGE_MIGRATIONS,
        LEGACY_SMITHING_TARGETS,
        SMITHING_RECIPES_BY_ID,
    )
    from .skill_registry import default_skill_state, default_target_state, planned_skill_definitions, trainable_skill_definitions
    from .summoning_data import DEFAULT_SUMMONING_TARGET, SUMMONING_ACTIONS_BY_ID
    from .summoning_logic import default_summoning_state_pure, sanitize_summoning_state_pure
    from .slayer_logic import sanitize_slayer_state_pure
    from .thieving_data import THIEVING_TARGETS
    from .agility_data import DEFAULT_AGILITY_TARGET
    from .agility_logic import default_agility_state_pure, sanitize_agility_state_pure
    from .livid_farm_logic import (
        default_livid_farm_state_pure,
        sanitize_livid_farm_state_pure,
    )
    from .review_context import (
        default_review_context_state_pure,
        sanitize_review_context_state_pure,
    )
    from .warriors_guild_logic import (
        default_warriors_guild_state_pure,
        sanitize_warriors_guild_state_pure,
    )
    from .woodcutting_data import (
        DEFAULT_WOODCUTTING_TOOLBELT,
        LEGACY_LOG_STORAGE_MIGRATIONS,
        LEGACY_TREE_TARGETS,
    )
except ImportError:
    from cadence_kernel import default_cadence_kernel_state_pure, sanitize_cadence_kernel_state_pure
    import inventory_pure
    from cooking_data import DEFAULT_COOKING_TARGET, COOKING_TARGETS_BY_ID
    from crafting_data import (
        DEFAULT_CRAFTING_TARGET,
        CRAFTING_RECIPES_BY_ID,
        LEGACY_CRAFTING_ITEM_MIGRATIONS,
        LEGACY_CRAFTING_TARGETS,
    )
    from item_registry import ItemDefinition
    from equipment_instance_logic import (
        default_equipment_instance_state_pure,
        sanitize_equipment_instance_state_pure,
    )
    from equipment_condition_data import EQUIPMENT_CONDITION_DATA
    from barrows_logic import default_barrows_state_pure, sanitize_barrows_state_pure  # type: ignore
    from fist_of_guthix_logic import (  # type: ignore
        default_fist_of_guthix_state_pure,
        sanitize_fist_of_guthix_state_pure,
    )
    from fight_caves_logic import (  # type: ignore
        default_fight_caves_state_pure,
        sanitize_fight_caves_state_pure,
    )
    from stealing_creation_logic import (  # type: ignore
        default_stealing_creation_state_pure,
        sanitize_stealing_creation_state_pure,
    )
    from urn_data import URN_PLAIN_TO_RUNED_ITEM, default_urn_state_pure, sanitize_urn_state_pure
    from constants import (
        BAR_DATA,
        EXP_TABLE,
        FISHING_OUTPUT_ITEMS,
        GEM_DATA,
        HERBLORE_FINISHED_OUTPUT_ITEMS,
        MINING_OUTPUT_ITEMS,
        RUNECRAFTING_RUNE_OUTPUT_ITEMS,
        WOODCUTTING_LOG_ITEMS,
    )
    from quest_data import DEFAULT_QUEST_TARGET, default_claim_states, default_quest_states
    from runecrafting_data import DEFAULT_RUNECRAFTING_TARGET, RUNECRAFTING_TARGETS_BY_ID
    from firemaking_data import DEFAULT_FIREMAKING_TARGET, FIREMAKING_TARGETS_BY_ID
    from fishing_data import DEFAULT_FISHING_TARGET, FISHING_METHODS_BY_ID
    from hunter_data import DEFAULT_HUNTER_TARGET, HUNTER_TARGETS_BY_ID
    from herblore_data import DEFAULT_HERBLORE_TARGET, HERBLORE_TARGETS_BY_ID
    from fletching_data import DEFAULT_FLETCHING_TARGET, FLETCHING_TARGETS_BY_ID, LEGACY_FLETCHING_TARGETS
    from logic_pure import (
        default_action_telemetry_pure,
        default_achievement_progress_pure,
        default_combat_state_pure,
        default_mage_arena_state_pure,
        MAGE_ARENA_GOD_DATA,
        default_quest_combat_active_encounters_pure,
        default_quest_combat_config_pure,
        default_red_sandstone_daily_state_pure,
        default_stronghold_state_pure,
        calculate_new_level,
        sanitize_action_telemetry_pure,
        sanitize_achievement_progress_pure,
        sanitize_combat_state_pure,
        sanitize_mage_arena_state_pure,
        sanitize_quest_combat_active_encounters_pure,
        sanitize_quest_combat_config_pure,
        red_sandstone_daily_state_pure,
        sanitize_stronghold_state_pure,
    )
    from shop_logic import default_shop_state_pure, sanitize_shop_state_pure
    from grand_exchange_logic import default_ge_state_pure, sanitize_ge_state_pure
    from big_chinchompa_data import (  # type: ignore
        BIG_CHINCHOMPA_TICKET_BY_TARGET,
        WORLD_POPULATION_PROFILES,
    )
    from big_chinchompa_logic import (  # type: ignore
        default_big_chinchompa_state_pure,
        sanitize_big_chinchompa_state_pure,
    )
    from evil_tree_logic import (  # type: ignore
        default_evil_tree_state_pure,
        sanitize_evil_tree_state_pure,
    )
    from shooting_star_logic import (  # type: ignore
        default_shooting_star_state_pure,
        sanitize_shooting_star_state_pure,
    )
    from sorceress_garden_logic import (  # type: ignore
        default_sorceress_garden_state_pure,
        sanitize_sorceress_garden_state_pure,
    )
    from penguin_hide_and_seek_logic import (  # type: ignore
        default_penguin_state_pure,
        sanitize_penguin_state_pure,
    )
    from pyramid_plunder_logic import (  # type: ignore
        default_pyramid_plunder_state_pure,
        sanitize_pyramid_plunder_state_pure,
    )
    from werewolf_skullball_data import (  # type: ignore
        WEREWOLF_SKULLBALL_ACTIVITY_ID,
    )
    from werewolf_skullball_logic import (  # type: ignore
        default_werewolf_skullball_state_pure,
        sanitize_werewolf_skullball_state_pure,
    )
    from gnome_ball_data import GNOME_BALL_ACTIVITY_ID  # type: ignore
    from gnome_ball_logic import (  # type: ignore
        default_gnome_ball_state_pure,
        sanitize_gnome_ball_state_pure,
    )
    from fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID  # type: ignore
    from fish_flingers_logic import (  # type: ignore
        default_fish_flingers_state_pure,
        sanitize_fish_flingers_state_pure,
    )
    from vinesweeper_logic import (  # type: ignore
        default_vinesweeper_state_pure,
        sanitize_vinesweeper_state_pure,
    )
    from farming_logic import default_farming_state_pure, sanitize_farming_state_pure
    from mining_data import DEFAULT_MINING_TARGET, DEFAULT_MINING_TOOLBELT, LEGACY_ORE_TARGETS
    from smithing_data import (
        DEFAULT_SMITHING_TARGET,
        LEGACY_BAR_STORAGE_MIGRATIONS,
        LEGACY_SMITHING_TARGETS,
        SMITHING_RECIPES_BY_ID,
    )
    from skill_registry import default_skill_state, default_target_state, planned_skill_definitions, trainable_skill_definitions
    from summoning_data import DEFAULT_SUMMONING_TARGET, SUMMONING_ACTIONS_BY_ID
    from summoning_logic import default_summoning_state_pure, sanitize_summoning_state_pure
    from slayer_logic import sanitize_slayer_state_pure
    from thieving_data import THIEVING_TARGETS
    from agility_data import DEFAULT_AGILITY_TARGET  # type: ignore
    from agility_logic import default_agility_state_pure, sanitize_agility_state_pure
    from livid_farm_logic import (  # type: ignore
        default_livid_farm_state_pure,
        sanitize_livid_farm_state_pure,
    )
    from review_context import (  # type: ignore
        default_review_context_state_pure,
        sanitize_review_context_state_pure,
    )
    from warriors_guild_logic import (  # type: ignore
        default_warriors_guild_state_pure,
        sanitize_warriors_guild_state_pure,
    )
    from woodcutting_data import (
        DEFAULT_WOODCUTTING_TOOLBELT,
        LEGACY_LOG_STORAGE_MIGRATIONS,
        LEGACY_TREE_TARGETS,
    )

CURRENT_CONFIG_VERSION = 64
DEFAULT_UTILITY_ACTIVITY = "make_soft_clay"
# Temporary Utility bridges retired on 2026-07-06 once their outputs became
# live NPC shop stock (Feather, Fishing bait, and the Hunter gear bundle).
# Saves that still point at one migrate back to the default activity.
# 2026-07-07 added the shop-covered Cooking gather/scavenge bridges and
# buy_bucket (all outputs are live NPC shop stock at cache prices).
_RETIRED_UTILITY_ACTIVITIES = {
    "scavenge_chicken_feathers",
    "gather_fishing_bait",
    "buy_hunter_supplies",
    "buy_bucket",
    "gather_potatoes",
    "gather_onions",
    "gather_eggs",
    "gather_redberries",
    "gather_cooking_apples",
    "gather_tomatoes",
    "gather_cheese",
    "gather_cabbage",
    "gather_sweetcorn",
    "gather_spice",
    "scavenge_raw_chicken",
    "scavenge_raw_beef",
    "scavenge_raw_bear_meat",
    "scavenge_raw_rat_meat",
    "scavenge_raw_rabbit",
    "scavenge_raw_yak_meat",
    "gather_thin_snails",
}
_EQUIPMENT_SLOT_IDS = {
    "head",
    "cape",
    "neck",
    "ammunition",
    "weapon",
    "body",
    "shield",
    "legs",
    "hands",
    "feet",
    "ring",
}

def _default_inventory(ORE_DATA: Dict[str, Any], item_definitions: Optional[Iterable[ItemDefinition]] = None) -> Dict[str, int]:
    if item_definitions is None:
        inventory: Dict[str, int] = {}
        for spec in ORE_DATA.values():
            output_item = spec.get("output_item")
            if isinstance(output_item, str):
                inventory.setdefault(output_item, 0)
            alternate_output = spec.get("alternate_output_item")
            if isinstance(alternate_output, str):
                inventory.setdefault(alternate_output, 0)
            for weighted in spec.get("weighted_outputs", ()):
                if isinstance(weighted, dict) and isinstance(weighted.get("item"), str):
                    inventory.setdefault(str(weighted["item"]), 0)
        return inventory
    inventory: Dict[str, int] = {}
    for item in item_definitions:
        inventory.setdefault(item.storage_key, 0)
    for ore in ORE_DATA:
        inventory.setdefault(ore, 0)
    return inventory


def _sanitize_thieving_state(data: Dict[str, Any]) -> None:
    default_target = default_target_state().get("current_thieving", "pickpocket_man")
    current_target = data.get("current_thieving")
    data["current_thieving"] = (
        current_target
        if isinstance(current_target, str) and current_target in THIEVING_TARGETS
        else default_target
    )
    for key in (
        "thieving_attempt_count",
        "thieving_success_count",
        "thieving_failure_count",
    ):
        value = data.get(key, 0)
        data[key] = value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0
    stunned = data.get("thieving_stunned", False)
    data["thieving_stunned"] = stunned if isinstance(stunned, bool) else False
    fight_back = data.get("thieving_fight_back_when_caught", False)
    data["thieving_fight_back_when_caught"] = fight_back if isinstance(fight_back, bool) else False
    phase = data.get("thieving_blackjack_phase", "needs_lure")
    phase = (
        phase
        if isinstance(phase, str) and phase in {"needs_lure", "ready_to_knockout", "knocked_out"}
        else "needs_lure"
    )
    picks = data.get("thieving_blackjack_picks_remaining", 0)
    picks = min(picks, 2) if isinstance(picks, int) and not isinstance(picks, bool) and picks >= 0 else 0
    if phase != "knocked_out":
        picks = 0
    elif picks == 0:
        phase = "ready_to_knockout"
    data["thieving_blackjack_phase"] = phase
    data["thieving_blackjack_picks_remaining"] = picks


def _achievement_seed_items() -> Dict[str, set[str]]:
    herblore_items: set[str] = set(HERBLORE_FINISHED_OUTPUT_ITEMS)
    for item_name in HERBLORE_FINISHED_OUTPUT_ITEMS:
        if not item_name.endswith(")") or " (" not in item_name:
            continue
        base, raw_dose = item_name.rsplit(" (", 1)
        try:
            max_dose = max(4, int(raw_dose[:-1]))
        except (TypeError, ValueError):
            continue
        herblore_items.update(f"{base} ({dose})" for dose in range(1, max_dose + 1))
        flask_base = base.replace(" potion", "")
        herblore_items.update(f"{flask_base} flask ({dose})" for dose in range(1, 7))
    return {
        "mining": set(MINING_OUTPUT_ITEMS) | set(GEM_DATA),
        "woodcutting": set(WOODCUTTING_LOG_ITEMS),
        "runecrafting": set(RUNECRAFTING_RUNE_OUTPUT_ITEMS),
        "smithing": set(BAR_DATA),
        "crafting": {"Empty pot", "Gold ring", "Sapphire", "Emerald", "Ruby", "Diamond"},
        "firemaking": {"Ashes"},
        "fishing": set(FISHING_OUTPUT_ITEMS),
        "herblore": herblore_items,
        "prayer": {"Ecto-token"},
        "agility": {"Agility arena ticket"},
    }


def _migrate_achievement_progress(data: Dict[str, Any]) -> None:
    """Seed the v37 ledger from the strongest non-destructive evidence available."""
    progress = default_achievement_progress_pure()
    skills = progress["skills"]
    telemetry = sanitize_action_telemetry_pure(data.get("action_telemetry"))
    for telemetry_record in telemetry.get("actions", {}).values():
        skill_id = str(telemetry_record.get("skill_id", ""))
        action_id = str(telemetry_record.get("action_id", ""))
        if not skill_id or not action_id:
            continue
        record = skills.setdefault(skill_id, {"actions": {}, "outputs": {}})
        successes = max(0, int(telemetry_record.get("successes", 0) or 0))
        record["actions"][action_id] = record["actions"].get(action_id, 0) + successes
        for item_name, amount in (telemetry_record.get("outputs", {}) or {}).items():
            amount = max(0, int(amount or 0))
            record["outputs"][str(item_name)] = record["outputs"].get(str(item_name), 0) + amount

    inventory = data.get("inventory", {}) or {}
    if isinstance(inventory, dict):
        for skill_id, item_names in _achievement_seed_items().items():
            for item_name in item_names:
                try:
                    held = max(0, int(inventory.get(item_name, 0) or 0))
                except (TypeError, ValueError):
                    held = 0
                if held:
                    record = skills.setdefault(
                        skill_id,
                        {"actions": {}, "outputs": {}},
                    )
                    record["outputs"][item_name] = max(record["outputs"].get(item_name, 0), held)
    data["achievement_progress"] = sanitize_achievement_progress_pure(progress)


def default_player_data(ORE_DATA: Dict[str, Any], item_definitions: Optional[Iterable[ItemDefinition]] = None) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "config_version": CURRENT_CONFIG_VERSION,
        "inventory": _default_inventory(ORE_DATA, item_definitions),
        "progress_to_next": 0,
        "completed_achievements": [],
        "achievement_progress": default_achievement_progress_pure(),
    }
    data.update(default_skill_state())
    data.update(_default_combat_state())
    data.update(default_combat_state_pure())
    data.update(_default_hidden_support_state())
    data.update(default_target_state())
    data["magic_charge_active"] = False
    data["magic_charge_ticks_remaining"] = 0
    data["mage_arena"] = default_mage_arena_state_pure()
    data["current_utility"] = DEFAULT_UTILITY_ACTIVITY
    data["current_quest"] = DEFAULT_QUEST_TARGET
    data["construction_actions_completed"] = 0
    data["construction_outputs_created"] = 0
    data["house_owned"] = False
    data["house_rooms_bought"] = {}
    data["house_servant"] = ""
    data["house_built_flags"] = {}
    data["house_style"] = "basic_wood"
    data["prayer_gilded_mode"] = "hosted"
    data["prayer_owned_altar_stint"] = {}
    data.update(default_urn_state_pure())
    data["cooking_success_count"] = 0
    data["cooking_burn_count"] = 0
    data["hunter_success_count"] = 0
    data["thieving_attempt_count"] = 0
    data["thieving_success_count"] = 0
    data["thieving_failure_count"] = 0
    data["thieving_stunned"] = False
    data["thieving_fight_back_when_caught"] = False
    data["thieving_blackjack_phase"] = "needs_lure"
    data["thieving_blackjack_picks_remaining"] = 0
    data["action_telemetry"] = default_action_telemetry_pure()
    data["toolbelt"] = _default_toolbelt()
    data["equipment"] = {}
    data.update(default_equipment_instance_state_pure())
    data["quests"] = default_quest_states()
    data["quest_points"] = 0
    data["quest_combat_config"] = default_quest_combat_config_pure()
    data["quest_combat_encounters"] = {}
    data["quest_combat_encounter_counts"] = {}
    data["quest_combat_active_encounters"] = default_quest_combat_active_encounters_pure()
    data["quest_stage_actions"] = {}
    data["quest_route_states"] = {}
    data["pending_skill_exp_rewards"] = {}
    data["claims"] = default_claim_states()
    data["wicked_hood"] = {"fed_altars": []}
    data["stronghold_of_security"] = default_stronghold_state_pure()
    data["runecrafting_pouches"] = {}
    data["item_charges"] = {}
    data["unlocked_abilities"] = []
    data.update(inventory_pure.default_carried_state())
    data.update(default_shop_state_pure())
    data["red_sandstone_daily"] = default_red_sandstone_daily_state_pure()
    data.update(default_ge_state_pure())
    data["world_population_profile"] = "normal"
    data["hunter_private_ground_targets"] = []
    data["big_chinchompa"] = default_big_chinchompa_state_pure()
    data["evil_tree"] = default_evil_tree_state_pure()
    data["shooting_star"] = default_shooting_star_state_pure()
    data["fist_of_guthix"] = default_fist_of_guthix_state_pure()
    data["fight_caves"] = default_fight_caves_state_pure()
    data["stealing_creation"] = default_stealing_creation_state_pure()
    data["barrows"] = default_barrows_state_pure()
    data.update(default_pyramid_plunder_state_pure())
    data.update(default_werewolf_skullball_state_pure())
    data.update(default_gnome_ball_state_pure())
    data.update(default_fish_flingers_state_pure())
    data["activity_session"] = {"active_id": ""}
    data["sorceress_garden"] = default_sorceress_garden_state_pure()
    data["penguin_hide_and_seek"] = default_penguin_state_pure()
    data["vinesweeper"] = default_vinesweeper_state_pure()
    data.update(default_farming_state_pure())
    data.update(default_agility_state_pure())
    data["livid_farm"] = default_livid_farm_state_pure()
    data.update(default_review_context_state_pure())
    data["warriors_guild"] = default_warriors_guild_state_pure()
    data["current_summoning"] = DEFAULT_SUMMONING_TARGET
    data["summoning_state"] = default_summoning_state_pure()
    data["pet_auto_care"] = True
    data.update(sanitize_slayer_state_pure(data))
    data["cadence_profiles"] = default_cadence_kernel_state_pure()
    return data


def _default_combat_state() -> Dict[str, int]:
    state: Dict[str, int] = {}
    for skill in planned_skill_definitions():
        if skill.category != "combat":
            continue
        state[skill.level_key] = 10 if skill.id == "constitution" else 1
        state[skill.exp_key] = 0
    return state


def _default_hidden_support_state() -> Dict[str, int]:
    """Support skills with hidden XP side effects but no visible surface yet."""
    state: Dict[str, int] = {}
    for skill in planned_skill_definitions():
        if skill.id != "agility":
            continue
        state[skill.level_key] = 1
        state[skill.exp_key] = 0
    return state


def _default_toolbelt() -> Dict[str, list[str]]:
    defaults: Dict[str, list[str]] = {}
    for source in (DEFAULT_WOODCUTTING_TOOLBELT, DEFAULT_MINING_TOOLBELT):
        for skill, items in source.items():
            defaults.setdefault(skill, [])
            defaults[skill].extend(item for item in items if item not in defaults[skill])
    return defaults


def _migrate_legacy_mining_target(data: Dict[str, Any], ore_data: Dict[str, Any]) -> None:
    current_ore = data.get("current_ore")
    if isinstance(current_ore, str):
        data["current_ore"] = LEGACY_ORE_TARGETS.get(current_ore, current_ore)
    if data.get("current_ore") not in ore_data:
        data["current_ore"] = DEFAULT_MINING_TARGET


def _migrate_legacy_woodcutting_target(data: Dict[str, Any]) -> None:
    current_tree = data.get("current_tree")
    if isinstance(current_tree, str):
        data["current_tree"] = LEGACY_TREE_TARGETS.get(current_tree, current_tree)


def _migrate_legacy_smithing_target(data: Dict[str, Any]) -> None:
    current_smith = data.get("current_smith")
    current_bar = data.get("current_bar")
    try:
        config_version = int(data.get("config_version", 1))
    except (TypeError, ValueError):
        config_version = 1
    if isinstance(current_bar, str) and (config_version < 9 or not isinstance(current_smith, str)):
        current_smith = LEGACY_SMITHING_TARGETS.get(current_bar, current_bar)
    if isinstance(current_smith, str):
        current_smith = LEGACY_SMITHING_TARGETS.get(current_smith, current_smith)
    if not isinstance(current_smith, str) or current_smith not in SMITHING_RECIPES_BY_ID:
        current_smith = DEFAULT_SMITHING_TARGET
    data["current_smith"] = current_smith


def _migrate_legacy_crafting_target(data: Dict[str, Any]) -> None:
    current_craft = data.get("current_craft")
    if isinstance(current_craft, str):
        current_craft = LEGACY_CRAFTING_TARGETS.get(current_craft, current_craft)
    if current_craft == "":
        data["current_craft"] = current_craft
        return
    if not isinstance(current_craft, str) or current_craft not in CRAFTING_RECIPES_BY_ID:
        current_craft = DEFAULT_CRAFTING_TARGET
    data["current_craft"] = current_craft


def _migrate_firemaking_target(data: Dict[str, Any]) -> None:
    current_firemaking = data.get("current_firemaking")
    if not isinstance(current_firemaking, str) or current_firemaking not in FIREMAKING_TARGETS_BY_ID:
        current_firemaking = DEFAULT_FIREMAKING_TARGET
    data["current_firemaking"] = current_firemaking


def _migrate_fishing_target(data: Dict[str, Any]) -> None:
    current_fishing = data.get("current_fishing")
    if not isinstance(current_fishing, str) or current_fishing not in FISHING_METHODS_BY_ID:
        current_fishing = DEFAULT_FISHING_TARGET
    data["current_fishing"] = current_fishing


def _migrate_hunter_target(data: Dict[str, Any]) -> None:
    current_hunter = data.get("current_hunter")
    if not isinstance(current_hunter, str) or current_hunter not in HUNTER_TARGETS_BY_ID:
        current_hunter = DEFAULT_HUNTER_TARGET
    data["current_hunter"] = current_hunter


def _migrate_cooking_target(data: Dict[str, Any]) -> None:
    current_cooking = data.get("current_cooking")
    if not isinstance(current_cooking, str) or current_cooking not in COOKING_TARGETS_BY_ID:
        current_cooking = DEFAULT_COOKING_TARGET
    data["current_cooking"] = current_cooking


def _migrate_runecrafting_target(data: Dict[str, Any]) -> None:
    current_runecrafting = data.get("current_runecrafting")
    if not isinstance(current_runecrafting, str) or current_runecrafting not in RUNECRAFTING_TARGETS_BY_ID:
        current_runecrafting = DEFAULT_RUNECRAFTING_TARGET
    data["current_runecrafting"] = current_runecrafting


def _migrate_herblore_target(data: Dict[str, Any]) -> None:
    current_herblore = data.get("current_herblore")
    if not isinstance(current_herblore, str) or current_herblore not in HERBLORE_TARGETS_BY_ID:
        current_herblore = DEFAULT_HERBLORE_TARGET
    data["current_herblore"] = current_herblore


def _migrate_quest_state(data: Dict[str, Any]) -> None:
    quests = data.get("quests")
    clean_quests = default_quest_states()
    if isinstance(quests, dict):
        for quest_id, default_state in clean_quests.items():
            raw_state = quests.get(quest_id)
            if not isinstance(raw_state, dict):
                continue
            state = dict(default_state)
            state["started"] = bool(raw_state.get("started", state["started"]))
            state["completed"] = bool(raw_state.get("completed", state["completed"]))
            try:
                progress = int(raw_state.get("progress", state["progress"]))
            except (TypeError, ValueError):
                progress = int(state["progress"])
            state["progress"] = max(0, progress)
            if state["completed"] and state["progress"] < 1:
                state["progress"] = 1
            clean_quests[quest_id] = state
    data["quests"] = clean_quests
    try:
        data["quest_points"] = max(0, int(data.get("quest_points", 0)))
    except (TypeError, ValueError):
        data["quest_points"] = 0
    current_quest = data.get("current_quest")
    if not isinstance(current_quest, str) or current_quest not in clean_quests:
        current_quest = DEFAULT_QUEST_TARGET
    data["current_quest"] = current_quest


def _migrate_quest_flag_collection(data: Dict[str, Any], key: str) -> None:
    raw_collection = data.get(key)
    clean: Dict[str, list[str]] = {}
    if isinstance(raw_collection, dict):
        for quest_id, raw_flags in raw_collection.items():
            if not isinstance(quest_id, str):
                continue
            if isinstance(raw_flags, str):
                flags = [raw_flags]
            elif isinstance(raw_flags, dict):
                flags = [flag for flag, enabled in raw_flags.items() if isinstance(flag, str) and bool(enabled)]
            elif isinstance(raw_flags, (list, tuple, set)):
                flags = [flag for flag in raw_flags if isinstance(flag, str)]
            else:
                flags = []
            if flags:
                clean[quest_id] = sorted(set(flags))
    data[key] = clean


def _migrate_quest_combat_encounter_counts(data: Dict[str, Any]) -> None:
    raw_collection = data.get("quest_combat_encounter_counts")
    clean: Dict[str, Dict[str, int]] = {}
    if isinstance(raw_collection, dict):
        for quest_id, raw_counts in raw_collection.items():
            if not isinstance(quest_id, str) or not isinstance(raw_counts, dict):
                continue
            quest_counts: Dict[str, int] = {}
            for encounter_id, raw_count in raw_counts.items():
                if not isinstance(encounter_id, str):
                    continue
                try:
                    count = int(raw_count)
                except (TypeError, ValueError):
                    continue
                if count > 0:
                    quest_counts[encounter_id] = count
            if quest_counts:
                clean[quest_id] = quest_counts
    data["quest_combat_encounter_counts"] = clean


def _migrate_quest_stage_side_state(data: Dict[str, Any]) -> None:
    data["quest_combat_config"] = sanitize_quest_combat_config_pure(data.get("quest_combat_config"))
    _migrate_quest_flag_collection(data, "quest_combat_encounters")
    _migrate_quest_combat_encounter_counts(data)
    data["quest_combat_active_encounters"] = sanitize_quest_combat_active_encounters_pure(
        data.get("quest_combat_active_encounters")
    )
    _migrate_quest_flag_collection(data, "quest_stage_actions")
    _migrate_quest_flag_collection(data, "quest_route_states")


def _migrate_pending_skill_exp_rewards(data: Dict[str, Any]) -> None:
    raw_pending = data.get("pending_skill_exp_rewards")
    trainable_by_exp_key = {skill.exp_key: skill for skill in trainable_skill_definitions()}
    clean_pending: Dict[str, float] = {}
    if isinstance(raw_pending, dict):
        for exp_key, raw_amount in raw_pending.items():
            if not isinstance(exp_key, str):
                continue
            try:
                amount = float(raw_amount)
            except (TypeError, ValueError, OverflowError):
                continue
            if not math.isfinite(amount) or amount <= 0:
                continue
            if exp_key in trainable_by_exp_key:
                try:
                    existing = float(data.get(exp_key, 0) or 0)
                except (TypeError, ValueError, OverflowError):
                    existing = 0.0
                if not math.isfinite(existing) or existing < 0:
                    existing = 0.0
                skill = trainable_by_exp_key[exp_key]
                try:
                    current_level = max(1, int(data.get(skill.level_key, 1) or 1))
                except (TypeError, ValueError, OverflowError):
                    current_level = 1
                total = existing + amount
                if not math.isfinite(total):
                    continue
                data[exp_key] = total
                data[skill.level_key] = calculate_new_level(
                    total,
                    current_level,
                    EXP_TABLE,
                )
            else:
                clean_pending[exp_key] = clean_pending.get(exp_key, 0.0) + amount
    data["pending_skill_exp_rewards"] = clean_pending


def _migrate_claim_state(data: Dict[str, Any]) -> None:
    claims = data.get("claims")
    clean_claims = default_claim_states()
    if isinstance(claims, dict):
        for claim_id, default_state in clean_claims.items():
            raw_state = claims.get(claim_id)
            if isinstance(raw_state, dict):
                clean_claims[claim_id] = {"claimed": bool(raw_state.get("claimed", default_state["claimed"]))}
            elif isinstance(raw_state, bool):
                clean_claims[claim_id] = {"claimed": raw_state}
    data["claims"] = clean_claims


def _migrate_runecrafting_side_state(data: Dict[str, Any]) -> None:
    hood = data.get("wicked_hood")
    fed_altars = []
    if isinstance(hood, dict):
        raw_fed = hood.get("fed_altars", [])
        if isinstance(raw_fed, str):
            fed_altars = [raw_fed]
        elif isinstance(raw_fed, (list, tuple, set)):
            fed_altars = [altar for altar in raw_fed if isinstance(altar, str)]
    data["wicked_hood"] = {"fed_altars": sorted(set(fed_altars))}

    pouches = data.get("runecrafting_pouches")
    clean_pouches: Dict[str, Dict[str, int]] = {}
    if isinstance(pouches, dict):
        for pouch_id, raw_state in pouches.items():
            if not isinstance(pouch_id, str) or not isinstance(raw_state, dict):
                continue
            try:
                degradation = max(0, int(raw_state.get("degradation", 0)))
            except (TypeError, ValueError):
                degradation = 0
            clean_pouches[pouch_id] = {"degradation": degradation}
    data["runecrafting_pouches"] = clean_pouches

    charges = data.get("item_charges")
    clean_charges: Dict[str, int] = {}
    if isinstance(charges, dict):
        for item_name, raw_charges in charges.items():
            if not isinstance(item_name, str):
                continue
            try:
                charge_count = int(raw_charges)
            except (TypeError, ValueError):
                continue
            if charge_count > 0:
                clean_charges[item_name] = charge_count
    data["item_charges"] = clean_charges


def _migrate_unlocked_abilities(data: Dict[str, Any]) -> None:
    raw_abilities = data.get("unlocked_abilities")
    if isinstance(raw_abilities, str):
        abilities = [raw_abilities]
    elif isinstance(raw_abilities, (list, tuple, set)):
        abilities = [ability for ability in raw_abilities if isinstance(ability, str)]
    else:
        abilities = []
    data["unlocked_abilities"] = sorted(set(abilities))


def _migrate_fletching_target(data: Dict[str, Any]) -> None:
    current_fletch = data.get("current_fletch")
    if isinstance(current_fletch, str):
        current_fletch = LEGACY_FLETCHING_TARGETS.get(current_fletch, current_fletch)
    if not isinstance(current_fletch, str) or current_fletch not in FLETCHING_TARGETS_BY_ID:
        current_fletch = DEFAULT_FLETCHING_TARGET
    data["current_fletch"] = current_fletch


def _migrate_legacy_log_inventory(inventory: Dict[str, int]) -> None:
    for legacy_key, new_key in LEGACY_LOG_STORAGE_MIGRATIONS.items():
        if legacy_key not in inventory:
            continue
        try:
            amount = int(inventory.get(legacy_key, 0))
        except (TypeError, ValueError):
            amount = 0
        if new_key is not None and amount:
            inventory[new_key] = inventory.get(new_key, 0) + amount
        inventory.pop(legacy_key, None)


def _migrate_legacy_bar_inventory(inventory: Dict[str, int]) -> None:
    for legacy_key, new_key in LEGACY_BAR_STORAGE_MIGRATIONS.items():
        if legacy_key not in inventory:
            continue
        try:
            amount = int(inventory.get(legacy_key, 0))
        except (TypeError, ValueError):
            amount = 0
        if amount:
            inventory[new_key] = inventory.get(new_key, 0) + amount
        inventory.pop(legacy_key, None)


def _migrate_legacy_crafting_inventory(inventory: Dict[str, int]) -> None:
    for legacy_key, new_key in LEGACY_CRAFTING_ITEM_MIGRATIONS.items():
        if legacy_key not in inventory:
            continue
        try:
            amount = int(inventory.get(legacy_key, 0))
        except (TypeError, ValueError):
            amount = 0
        if amount:
            inventory[new_key] = inventory.get(new_key, 0) + amount
        inventory.pop(legacy_key, None)


def _migrate_toolbelt(data: Dict[str, Any]) -> None:
    toolbelt = data.get("toolbelt")
    if not isinstance(toolbelt, dict):
        toolbelt = {}
    defaults = _default_toolbelt()
    for skill, default_items in defaults.items():
        existing = toolbelt.get(skill)
        if isinstance(existing, str):
            items = [existing]
        elif isinstance(existing, list):
            items = [item for item in existing if isinstance(item, str)]
        elif isinstance(existing, tuple):
            items = [item for item in existing if isinstance(item, str)]
        else:
            items = []
        for default_item in default_items:
            if default_item not in items:
                items.append(default_item)
        toolbelt[skill] = items
    data["toolbelt"] = toolbelt


def _migrate_equipment(data: Dict[str, Any]) -> None:
    equipment = data.get("equipment")
    clean_equipment: Dict[str, str] = {}
    if isinstance(equipment, dict):
        for slot, item_name in equipment.items():
            if isinstance(slot, str) and slot in _EQUIPMENT_SLOT_IDS and isinstance(item_name, str):
                clean_equipment[slot] = LEGACY_CRAFTING_ITEM_MIGRATIONS.get(item_name, item_name)
    data["equipment"] = clean_equipment
    data.pop("owned_equipment", None)


def _merge_renamed_item_quantity(store: Any, old_name: str, new_name: str) -> None:
    if not isinstance(store, dict) or old_name not in store:
        return
    try:
        amount = max(0, int(store.get(old_name, 0) or 0))
    except (TypeError, ValueError):
        amount = 0
    try:
        existing = max(0, int(store.get(new_name, 0) or 0))
    except (TypeError, ValueError):
        existing = 0
    store[new_name] = existing + amount
    store.pop(old_name, None)


def _migrate_legacy_crafting_item_references(data: Dict[str, Any]) -> None:
    for collection_key in ("carried_inventory", "carried_layout"):
        collection = data.get(collection_key)
        if not isinstance(collection, dict):
            continue
        for item_store in collection.values():
            if isinstance(item_store, dict):
                _migrate_legacy_crafting_inventory(item_store)

    overrides = data.get("loot_overrides")
    if isinstance(overrides, dict):
        for old_name, new_name in LEGACY_CRAFTING_ITEM_MIGRATIONS.items():
            if old_name not in overrides:
                continue
            overrides.setdefault(new_name, overrides[old_name])
            overrides.pop(old_name, None)

    for state_key in ("combat_grave", "death_office"):
        state = data.get(state_key)
        if not isinstance(state, dict):
            continue
        items = state.get("items")
        if isinstance(items, list):
            state["items"] = [
                LEGACY_CRAFTING_ITEM_MIGRATIONS.get(item_name, item_name)
                if isinstance(item_name, str)
                else item_name
                for item_name in items
            ]
        loadout = state.get("loadout")
        if isinstance(loadout, dict):
            state["loadout"] = {
                slot: LEGACY_CRAFTING_ITEM_MIGRATIONS.get(item_name, item_name)
                if isinstance(item_name, str)
                else item_name
                for slot, item_name in loadout.items()
            }

    alchemy_item = data.get("magic_alchemy_item")
    if isinstance(alchemy_item, str):
        data["magic_alchemy_item"] = LEGACY_CRAFTING_ITEM_MIGRATIONS.get(alchemy_item, alchemy_item)


def _migrate_plain_urn_item_stores(data: Dict[str, Any]) -> None:
    inventory = data.get("inventory")
    for old_name, new_name in URN_PLAIN_TO_RUNED_ITEM.items():
        _merge_renamed_item_quantity(inventory, old_name, new_name)

    for collection_key in ("carried_inventory", "carried_layout"):
        collection = data.get(collection_key)
        if not isinstance(collection, dict):
            continue
        for item_store in collection.values():
            for old_name, new_name in URN_PLAIN_TO_RUNED_ITEM.items():
                _merge_renamed_item_quantity(item_store, old_name, new_name)

    for state_key in ("combat_grave", "death_office"):
        state = data.get(state_key)
        if not isinstance(state, dict) or not isinstance(state.get("items"), list):
            continue
        state["items"] = [URN_PLAIN_TO_RUNED_ITEM.get(item_name, item_name) for item_name in state["items"]]


def _merge_target_key(collection: Any, old_target: str, new_target: str) -> None:
    if not isinstance(collection, dict) or old_target not in collection:
        return
    old_value = collection.pop(old_target)
    if new_target not in collection:
        collection[new_target] = old_value
        return
    current = collection[new_target]
    if isinstance(current, dict) and isinstance(old_value, dict):
        merged = dict(current)
        for key, value in old_value.items():
            if isinstance(value, int) and not isinstance(value, bool) and isinstance(merged.get(key), int) and not isinstance(merged.get(key), bool):
                merged[key] += value
            else:
                merged.setdefault(key, value)
        collection[new_target] = merged
    elif isinstance(current, bool) and isinstance(old_value, bool):
        collection[new_target] = current or old_value
    elif isinstance(current, int) and isinstance(old_value, int):
        collection[new_target] = current + old_value


def _migrate_ancient_gilded_target(data: Dict[str, Any]) -> None:
    old_target = "gilded_altar_ancient_bones"
    new_target = "bury_ancient_bones"
    if data.get("current_prayer") == old_target:
        data["current_prayer"] = new_target
    for state_key in ("prayer_owned_altar_stint", "prayer_gilded_house_search"):
        state = data.get(state_key)
        if isinstance(state, dict) and state.get("target_id") == old_target:
            data[state_key] = {}
    for collection_key in (
        "carried_inventory",
        "carried_churn",
        "carried_layout",
        "carried_advanced_targets",
        "carried_primed_targets",
    ):
        _merge_target_key(data.get(collection_key), old_target, new_target)
    bank_run = data.get("skilling_bank_run")
    if isinstance(bank_run, dict) and bank_run.get("target_id") == old_target:
        bank_run["target_id"] = new_target


def migrate_loaded_data(
    loaded: Dict[str, Any],
    ORE_DATA: Dict[str, Any],
    item_definitions: Optional[Iterable[ItemDefinition]] = None,
) -> Dict[str, Any]:
    # Start from copy
    data = dict(loaded) if loaded else {}

    # Add config_version if missing
    if "config_version" not in data:
        data["config_version"] = 1
    try:
        loaded_config_version = int(data.get("config_version", 1))
    except (TypeError, ValueError):
        loaded_config_version = 1

    # Migration: old schema used total_exp (treated as mining_exp), and no per-skill exp
    if "total_exp" in data and "mining_exp" not in data:
        data["mining_exp"] = data.pop("total_exp")
        data.setdefault("woodcutting_exp", 0)
        data.setdefault("smithing_exp", 0)
        data.setdefault("crafting_exp", 0)

    # Registry-backed defaults preserve today's flat save keys while removing
    # the need to hand-add keys for each playable skill.
    for key, value in default_skill_state().items():
        data.setdefault(key, value)
    for key, value in _default_combat_state().items():
        data.setdefault(key, value)
    for key, value in default_combat_state_pure().items():
        data.setdefault(key, value)
    for key, value in _default_hidden_support_state().items():
        data.setdefault(key, value)
    for key, value in default_target_state().items():
        data.setdefault(key, value)
    data.setdefault("current_utility", DEFAULT_UTILITY_ACTIVITY)
    if data.get("current_utility") in _RETIRED_UTILITY_ACTIVITIES:
        data["current_utility"] = DEFAULT_UTILITY_ACTIVITY
    _migrate_legacy_mining_target(data, ORE_DATA)
    _migrate_legacy_woodcutting_target(data)
    _migrate_legacy_smithing_target(data)
    _migrate_legacy_crafting_target(data)
    _migrate_fletching_target(data)
    _migrate_firemaking_target(data)
    _migrate_fishing_target(data)
    _migrate_hunter_target(data)
    _migrate_cooking_target(data)
    _migrate_runecrafting_target(data)
    _migrate_herblore_target(data)
    _migrate_quest_state(data)
    _migrate_quest_stage_side_state(data)
    _migrate_pending_skill_exp_rewards(data)
    _migrate_claim_state(data)
    _migrate_runecrafting_side_state(data)
    _migrate_unlocked_abilities(data)
    _migrate_toolbelt(data)
    _migrate_equipment(data)
    data.update(sanitize_shop_state_pure(data))
    # v51: Red sandstone's source daily allowance is translated onto the
    # established 240-answer world day; no wall-clock value is persisted.
    data["red_sandstone_daily"] = red_sandstone_daily_state_pure(data)
    data.update(sanitize_ge_state_pure(data))
    population_profile = str(
        data.get("world_population_profile", "normal")
    ).lower()
    data["world_population_profile"] = (
        population_profile
        if population_profile in WORLD_POPULATION_PROFILES
        else "normal"
    )
    private_targets = data.get("hunter_private_ground_targets")
    data["hunter_private_ground_targets"] = (
        [
            target_id
            for target_id in dict.fromkeys(
                str(value) for value in private_targets
            )
            if target_id in BIG_CHINCHOMPA_TICKET_BY_TARGET
        ]
        if isinstance(private_targets, (list, tuple))
        else []
    )
    data["big_chinchompa"] = sanitize_big_chinchompa_state_pure(
        data.get("big_chinchompa")
    )
    data["evil_tree"] = sanitize_evil_tree_state_pure(data.get("evil_tree"))
    data["shooting_star"] = sanitize_shooting_star_state_pure(
        data.get("shooting_star")
    )
    data["fist_of_guthix"] = sanitize_fist_of_guthix_state_pure(
        data.get("fist_of_guthix")
    )
    data["fight_caves"] = sanitize_fight_caves_state_pure(
        data.get("fight_caves")
    )
    data["stealing_creation"] = sanitize_stealing_creation_state_pure(
        data.get("stealing_creation")
    )
    data["barrows"] = sanitize_barrows_state_pure(data.get("barrows"))
    data.update(sanitize_pyramid_plunder_state_pure(data))
    data.update(sanitize_werewolf_skullball_state_pure(data))
    data.update(sanitize_gnome_ball_state_pure(data))
    data.update(sanitize_fish_flingers_state_pure(data))
    raw_activity_session = data.get("activity_session")
    active_session_id = (
        str(raw_activity_session.get("active_id", ""))[:80]
        if isinstance(raw_activity_session, dict)
        else ""
    )
    if data["fight_caves"]["active"]:
        active_session_id = "fight_caves"
        data["stealing_creation"]["active_session"] = {}
        data["barrows"]["active"] = False
        data["barrows"]["suspended"] = True
        data["pyramid_plunder"] = {}
        data["werewolf_skullball"] = {}
        data["gnome_ball"] = {}
        data["fish_flingers"] = {}
    elif data["stealing_creation"]["active_session"]:
        active_session_id = "stealing_creation"
        data["barrows"]["active"] = False
        data["barrows"]["suspended"] = True
        data["pyramid_plunder"] = {}
        data["werewolf_skullball"] = {}
        data["gnome_ball"] = {}
        data["fish_flingers"] = {}
    elif data["barrows"]["active"]:
        active_session_id = "barrows"
        data["pyramid_plunder"] = {}
        data["werewolf_skullball"] = {}
        data["gnome_ball"] = {}
        data["fish_flingers"] = {}
    elif data["pyramid_plunder"]:
        active_session_id = "pyramid_plunder"
        data["werewolf_skullball"] = {}
        data["gnome_ball"] = {}
        data["fish_flingers"] = {}
    elif data["werewolf_skullball"]:
        active_session_id = WEREWOLF_SKULLBALL_ACTIVITY_ID
        data["gnome_ball"] = {}
        data["fish_flingers"] = {}
    elif data["gnome_ball"]:
        active_session_id = GNOME_BALL_ACTIVITY_ID
        data["fish_flingers"] = {}
    elif data["fish_flingers"]:
        active_session_id = FISH_FLINGERS_ACTIVITY_ID
    elif active_session_id in {
        WEREWOLF_SKULLBALL_ACTIVITY_ID,
        GNOME_BALL_ACTIVITY_ID,
        FISH_FLINGERS_ACTIVITY_ID,
    }:
        active_session_id = ""
    data["activity_session"] = {"active_id": active_session_id}
    data["sorceress_garden"] = sanitize_sorceress_garden_state_pure(
        data.get("sorceress_garden")
    )
    data["penguin_hide_and_seek"] = sanitize_penguin_state_pure(
        data.get("penguin_hide_and_seek")
    )
    data["vinesweeper"] = sanitize_vinesweeper_state_pure(
        data.get("vinesweeper")
    )

    # Ensure inventory exists and has registered item keys while preserving
    # arbitrary existing entries from older or experimental saves.
    inv = data.get("inventory") or {}
    if not isinstance(inv, dict):
        inv = {}
    for item_key in _default_inventory(ORE_DATA, item_definitions):
        inv.setdefault(item_key, 0)
    _migrate_legacy_log_inventory(inv)
    _migrate_legacy_bar_inventory(inv)
    _migrate_legacy_crafting_inventory(inv)
    data["inventory"] = inv

    # Migrate every persisted reference before the carried-state sanitizer
    # clamps saved views against the already-renamed bank.
    _migrate_legacy_crafting_item_references(data)

    # Seed the carried-inventory overlay keys on old saves. Coins stay canonical
    # in the flat inventory (the money pouch is just that balance surfaced under a
    # pouch label); the overlay and death-drop exclude coins, so no coin store is
    # moved and no balance can be stranded.
    inventory_pure.sanitize_carried_state(data)

    # Ensure achievements structure exists
    data.setdefault("completed_achievements", [])
    data.setdefault("cooking_success_count", 0)
    data.setdefault("cooking_burn_count", 0)
    data.setdefault("hunter_success_count", 0)
    data["action_telemetry"] = sanitize_action_telemetry_pure(data.get("action_telemetry"))
    data["stronghold_of_security"] = sanitize_stronghold_state_pure(data.get("stronghold_of_security"))
    # v28: the drain-only combat_stat_drains scaffolding was generalized
    # into signed combat_current_levels; the dead key is dropped (it was
    # never populated) and sanitize seeds the new one.
    data.pop("combat_stat_drains", None)
    # v29: combat globals are preserved as the initial named preset; Prayer's
    # pending-XP migration is handled by the standard planned-skill path above.
    if loaded_config_version < 29:
        data["combat_presets"] = {}
        data["combat_active_preset"] = "Default"
    # v30: Magic becomes a complete standalone skill without replacing the
    # magic_level/magic_exp values already trained through Combat. New combat
    # spell options extend each v29 named preset in place.
    if loaded_config_version < 30:
        data.setdefault("current_magic", "low_alchemy")
        data.setdefault("magic_alchemy_item", "")
        data.setdefault("magic_actions_completed", 0)
        data.setdefault("magic_imbue_active", False)
        data.setdefault("magic_charge_active", False)
        data.setdefault("mage_arena", {"step": 0, "completed": False})
        data.setdefault("mage_training_arena", {"completed": False})
        presets = data.get("combat_presets", {}) or {}
        if isinstance(presets, dict):
            for preset in presets.values():
                if isinstance(preset, dict):
                    preset.setdefault("current_combat_spell", data.get("current_combat_spell", "wind_strike"))
                    preset.setdefault("combat_vengeance", False)
                    preset.setdefault("combat_dream_thrift", False)
                    preset.setdefault("combat_spellbook_swap", "")
    # v31: Construction's house sheet and owned gilded-altar state. Every
    # setdefault is deliberately additive so unknown/future save keys survive.
    if loaded_config_version < 31:
        data.setdefault("current_construction", "crude_wooden_chair")
        data.setdefault("construction_actions_completed", 0)
        data.setdefault("construction_outputs_created", 0)
        data.setdefault("house_owned", False)
        data.setdefault("house_rooms_bought", {})
        data.setdefault("house_servant", "")
        data.setdefault("house_built_flags", {})
        data.setdefault("house_style", "basic_wood")
        data.setdefault("prayer_gilded_mode", "hosted")
        data.setdefault("prayer_owned_altar_stint", {})
    # v32: Farming is a background clock plus persistent patch/bin/queue state.
    # Sanitization below is additive and retains unknown future keys and rows.
    if loaded_config_version < 32:
        for key, value in default_farming_state_pure().items():
            data.setdefault(key, value)
    # v33: shared six-skill urn state, passive telemetry, authentic runed-item
    # names, and retirement of the unsupported Ancient-bones altar target.
    if loaded_config_version < 33:
        for key, value in default_urn_state_pure().items():
            data.setdefault(key, value)
        _migrate_plain_urn_item_stores(data)
        _migrate_ancient_gilded_target(data)
    # v34: dormant route-keyed cadence residuals. The migration is additive;
    # no live action reads or advances this state in Phase 1.
    if loaded_config_version < 34:
        data.setdefault("cadence_profiles", default_cadence_kernel_state_pure())
    # v35: complete Thieving identity and review-side state. The target itself
    # is registry-backed; the remaining keys are additive and stay flat.
    if loaded_config_version < 35:
        data.setdefault("current_thieving", default_target_state().get("current_thieving", "pickpocket_man"))
        data.setdefault("thieving_attempt_count", 0)
        data.setdefault("thieving_success_count", 0)
        data.setdefault("thieving_failure_count", 0)
        data.setdefault("thieving_stunned", False)
        data.setdefault("thieving_fight_back_when_caught", False)
        data.setdefault("thieving_blackjack_phase", "needs_lure")
        data.setdefault("thieving_blackjack_picks_remaining", 0)
    # v36: complete Agility course/activity state. Pending Agility XP is applied
    # by the standard trainable-skill migration above in the same load.
    if loaded_config_version < 36:
        for key, value in default_agility_state_pure().items():
            data.setdefault(key, value)
    # v37: action-worded achievements use durable, action-owner progress rather
    # than disposable Bank balances. Existing telemetry and holdings establish
    # a conservative minimum; completed achievement names remain sticky.
    if loaded_config_version < 37:
        _migrate_achievement_progress(data)
    # v38: Charge stops being an indefinite boolean and uses the global
    # review-driven temporary-effect clock. An active legacy spell receives one
    # full sourced duration because no elapsed review count was persisted.
    if loaded_config_version < 38:
        data.setdefault(
            "magic_charge_ticks_remaining",
            700 if bool(data.get("magic_charge_active", False)) else 0,
        )
    # v39: Farming whole-farm presets and explicit plan automation fields.
    # The Farming sanitizer supplies additive defaults and strips transient
    # payment/spell state from saved preset snapshots.
    if loaded_config_version < 39:
        for key, value in default_farming_state_pure().items():
            data.setdefault(key, value)
    # v40: Mage Arena alignment/attunements and Farming cure-route preference.
    # Both nested structures are normalized again below so the migration stays
    # additive and idempotent for partial or future-shaped payloads.
    if loaded_config_version < 40:
        data.setdefault("mage_arena", default_mage_arena_state_pure())
        legacy_arena = data.get("mage_arena", {}) or {}
        legacy_alignment = str(legacy_arena.get("alignment", "") or "")
        if (
            bool(legacy_arena.get("completed"))
            and legacy_alignment in MAGE_ARENA_GOD_DATA
            and not legacy_arena.get("attuned_spells")
        ):
            legacy_arena["attuned_spells"] = [
                MAGE_ARENA_GOD_DATA[legacy_alignment]["spell_id"]
            ]
    # v41: complete Summoning training and the shared follower-state substrate.
    # The sanitizer remains additive so the later pet and ability catalogs can
    # extend the nested state without another destructive rewrite.
    if loaded_config_version < 41:
        data.setdefault("current_summoning", DEFAULT_SUMMONING_TARGET)
        data.setdefault("summoning_state", default_summoning_state_pure())
    # v42: persistent pet entities and the default-on Casual care policy.
    if loaded_config_version < 42:
        data.setdefault("pet_auto_care", True)
    # v43: the first complete Slayer master pool and its flat assignment state.
    if loaded_config_version < 43:
        data.update(sanitize_slayer_state_pure(data))
    # v44: deterministic Grand Exchange state and the Ironman access toggle.
    if loaded_config_version < 44:
        data.update(sanitize_ge_state_pure(data))
    # v45: The Pit invitation policy and generic reviewer-context preferences.
    if loaded_config_version < 45:
        for key, value in default_review_context_state_pure().items():
            data.setdefault(key, value)
    # v61: Pyramid Plunder becomes a persistent dangerous activity. The
    # sanitizer below repairs a partial run without disturbing future fields.
    if loaded_config_version < 61:
        for key, value in default_pyramid_plunder_state_pure().items():
            data.setdefault(key, value)
    # v62: Werewolf Skullball moves from an invented multi-review Agility stub
    # to its settled, atomic Activities run. Partial legacy goal state cannot be
    # translated honestly, but completion counters remain untouched.
    if loaded_config_version < 62:
        for key, value in default_werewolf_skullball_state_pure().items():
            data.setdefault(key, value)
        if str(data.get("current_agility", "")) == WEREWOLF_SKULLBALL_ACTIVITY_ID:
            data["current_agility"] = DEFAULT_AGILITY_TARGET
            data["current_utility"] = WEREWOLF_SKULLBALL_ACTIVITY_ID
        activities = data.get("agility_activity_state")
        if isinstance(activities, dict) and activities.pop("skullball", None):
            data["werewolf_skullball_last_result"] = (
                "Legacy partial Skullball run reset; choose a route and enter again"
            )
    # v63: Gnome Ball moves from the invented five-review Agility stub to its
    # settled three-beat Activities match. Partial legacy goal state has no
    # faithful beat mapping; completion counters remain untouched.
    if loaded_config_version < 63:
        for key, value in default_gnome_ball_state_pure().items():
            data.setdefault(key, value)
        if str(data.get("current_agility", "")) == GNOME_BALL_ACTIVITY_ID:
            data["current_agility"] = DEFAULT_AGILITY_TARGET
            data["current_utility"] = GNOME_BALL_ACTIVITY_ID
        activities = data.get("agility_activity_state")
        if isinstance(activities, dict):
            legacy_session = activities.pop("gnome_ball", None)
            if legacy_session:
                data["gnome_ball_last_result"] = (
                    "Legacy partial Gnome Ball match reset; enter again"
                )
    # v64: Fish Flingers adds a six-review persistent activity and its
    # simulated-day ticket/currency ledgers.
    if loaded_config_version < 64:
        for key, value in default_fish_flingers_state_pure().items():
            data.setdefault(key, value)
    # These defaults are also required for a new v30-shaped payload assembled
    # outside load_player_data (tests, imports, or a future alternate frontend).
    data.setdefault("current_magic", "low_alchemy")
    data.setdefault("magic_alchemy_item", "")
    data.setdefault("magic_actions_completed", 0)
    data.setdefault("magic_imbue_active", False)
    data.setdefault("magic_charge_active", False)
    try:
        charge_ticks = max(0, int(data.get(
            "magic_charge_ticks_remaining",
            700 if bool(data.get("magic_charge_active", False)) else 0,
        ) or 0))
    except (TypeError, ValueError, OverflowError):
        charge_ticks = 0
    data["magic_charge_ticks_remaining"] = charge_ticks
    data["magic_charge_active"] = charge_ticks > 0
    data["mage_arena"] = sanitize_mage_arena_state_pure(data.get("mage_arena"))
    data.setdefault("mage_training_arena", {"completed": False})
    data.setdefault("current_construction", "crude_wooden_chair")
    data.setdefault("construction_actions_completed", 0)
    data.setdefault("construction_outputs_created", 0)
    data.setdefault("house_owned", False)
    data.setdefault("house_rooms_bought", {})
    data.setdefault("house_servant", "")
    data.setdefault("house_built_flags", {})
    data.setdefault("house_style", "basic_wood")
    data.setdefault("prayer_gilded_mode", "hosted")
    data.setdefault("prayer_owned_altar_stint", {})
    for key, value in default_urn_state_pure().items():
        data.setdefault(key, value)
    # Always repair invalid/dangling urn pointers and progress. This is a load
    # invariant, not a schema migration; valid partial urns remain valid in bank.
    data.update(sanitize_urn_state_pure(data))
    data.update(sanitize_farming_state_pure(data))
    data.update(sanitize_agility_state_pure(data))
    data.update(sanitize_pyramid_plunder_state_pure(data))
    data.update(sanitize_werewolf_skullball_state_pure(data))
    data.update(sanitize_gnome_ball_state_pure(data))
    data.update(sanitize_fish_flingers_state_pure(data))
    data["livid_farm"] = sanitize_livid_farm_state_pure(
        data.get("livid_farm")
    )
    data.update(sanitize_review_context_state_pure(data))
    current_summoning = str(
        data.get("current_summoning", DEFAULT_SUMMONING_TARGET)
    )
    if current_summoning not in SUMMONING_ACTIONS_BY_ID:
        current_summoning = DEFAULT_SUMMONING_TARGET
    data["current_summoning"] = current_summoning
    data["summoning_state"] = sanitize_summoning_state_pure(
        data.get("summoning_state"),
        summoning_level=data.get("summoning_level", 1),
    )
    data["warriors_guild"] = sanitize_warriors_guild_state_pure(
        data.get("warriors_guild")
    )
    data["pet_auto_care"] = bool(data.get("pet_auto_care", True))
    data.update(sanitize_slayer_state_pure(data))
    data.update(sanitize_ge_state_pure(data))
    _sanitize_thieving_state(data)
    data["cadence_profiles"] = sanitize_cadence_kernel_state_pure(
        data.get("cadence_profiles")
    )
    data["achievement_progress"] = sanitize_achievement_progress_pure(
        data.get("achievement_progress")
    )
    if "cadence_shadow" in data:
        try:
            try:
                from .cadence_shadow import sanitize_cadence_shadow_state_pure
            except ImportError:  # pragma: no cover - flat import path used by tests
                from cadence_shadow import sanitize_cadence_shadow_state_pure  # type: ignore
            data["cadence_shadow"] = sanitize_cadence_shadow_state_pure(data["cadence_shadow"])
        except ImportError:
            # A disabled optional observer must never make an existing save unloadable.
            pass
    data.update(sanitize_combat_state_pure(data))
    data.update(
        sanitize_equipment_instance_state_pure(
            data, EQUIPMENT_CONDITION_DATA
        )
    )
    combat_current_levels = data.get("combat_current_levels")
    if isinstance(combat_current_levels, dict) and "prayer" in combat_current_levels:
        try:
            stale_prayer_level = int(combat_current_levels["prayer"])
            base_prayer_level = max(1, int(data.get("prayer_level", 1) or 1))
        except (TypeError, ValueError, OverflowError):
            stale_prayer_level = base_prayer_level = 1
        if stale_prayer_level > base_prayer_level:
            combat_current_levels = dict(combat_current_levels)
            combat_current_levels.pop("prayer", None)
            data["combat_current_levels"] = combat_current_levels

    # Progress key retained (not critical)
    data.setdefault("progress_to_next", 0)

    # Never relabel a save from a newer schema as the current one.
    data["config_version"] = max(loaded_config_version, CURRENT_CONFIG_VERSION)
    return data
