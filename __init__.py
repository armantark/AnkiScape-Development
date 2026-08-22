# __init__.py

from .core.constants import (
    COMBAT_ENEMY_DATA,
    CONSUMABLE_DATA,
    ORE_DATA,
    MINING_PICKAXE_DATA,
    TREE_DATA,
    WOODCUTTING_AXE_DATA,
    BAR_DATA,
    SMITHING_DATA,
    CRAFTING_DATA,
    COOKING_DATA,
    PRAYER_DATA,
    FLETCHING_DATA,
    FIREMAKING_DATA,
    HUNTER_DATA,
    RUNECRAFTING_DATA,
    RUNECRAFTING_POUCH_DATA,
    QUEST_DATA,
    QUEST_UNLOCK_RULES,
    CLAIM_DATA,
    UTILITY_ACTIVITY_DATA,
    ACTIVITY_SURFACE_ID,
    DEFAULT_UTILITY_ACTIVITY,
    EXP_TABLE,
    ORE_IMAGES,
    TREE_IMAGES,
    BAR_IMAGES,
    CRAFTED_ITEM_IMAGES,
    EQUIPMENT_DATA,
)
from .data.smithing_data import DEFAULT_SMITHING_TARGET
from .data.combat_data import DEFAULT_COMBAT_TARGET
from aqt import mw, gui_hooks
from anki.hooks import addHook, wrap
from aqt.reviewer import Reviewer
import copy
import random
import os
import datetime
from collections.abc import Mapping
from .logic_pure.logic_pure import (
    apply_consumable_pure,
    apply_impling_jar_open_pure,
    apply_item_pack_open_pure,
    combat_observed_drop_item_names_pure,
    smithing_target_locked_reasons_pure,
    has_crafting_materials_pure,
    crafting_target_locked_reasons_pure,
    fletching_target_locked_reasons_pure,
    cooking_target_locked_reasons_pure,
    hunter_target_locked_reasons_pure,
    can_runecraft_any_pure,
    quest_unlock_locked_reasons_pure,
    start_quest_pure,
    apply_quest_route_choice_pure,
    apply_claim_pure,
    apply_safe_combat_recovery_pure,
    advance_temporary_effects_pure,
    combat_dream_thrift_locked_reasons_pure,
    set_combat_auto_eat_threshold_pure,
    set_combat_pack_mode_pure,
    set_combat_auto_eat_food_pure,
    refill_combat_supply_loadout_pure,
    request_combat_bank_run_now_pure,
    unload_combat_supply_loadout_pure,
    reclaim_death_office_items_pure,
    start_combat_grave_walk_pure,
    firemaking_target_locked_reasons_pure,
    apply_utility_activity_pure,
    grant_stronghold_reward_pure,
    STRONGHOLD_REWARD_COINS,
    sanitize_review_action_multiplier,
    attach_tool_to_toolbelt_pure,
    can_equip_item_pure,
    equip_item_pure,
    unequip_item_pure,
    calculate_new_level,
    sanitize_prayer_selection_pure,
    apply_combat_preset_pure,
    save_combat_preset_pure,
    purchase_house_pure,
    purchase_house_option_pure,
    apply_prayer_selection_pure,
    apply_mage_arena_cape_action_pure,
    teleport_full_urn_pure,
    set_mage_arena_alignment_pure,
)
from .data.construction_data import ROOM_DATA, SERVANT_DATA, HOUSE_STYLE_DATA
from .logic.cadence_kernel import sanitize_cadence_kernel_enabled_pure
from .core.logic import (
    combat_level_up_check as _core_combat_level_up_check,
    level_up_check as _core_level_up_check,
    check_achievements,
)
from .logic_pure.logic_pure_combat_engine import player_combat_level_pure
from .ui.ui import (
    ExpPopup,
    show_error_message,
    show_tree_selection_dialog,
    show_ore_selection_dialog,
    refresh_skill_availability,
    is_main_menu_open,
    focus_main_menu_if_open,
    ensure_review_hud,
    update_review_hud,
    hide_review_hud,
    ensure_review_context_action_strip,
    update_review_context_action_strip,
    update_review_bank_run_button,
    ensure_review_status_badge,
    update_review_status_badge,
    update_review_fill_drawer,
    update_review_event_log_drawer,
    update_review_bank_run_button,
    hide_review_status_badge,
    migrate_legacy_settings,
)
from .ui import ui
from .logic import inventory_pure
from .logic.equipment_instance_logic import (
    is_condition_item_pure,
    remove_bank_equipment_instances_pure,
    sync_equipment_instances_pure,
)
from .data.equipment_condition_data import EQUIPMENT_CONDITION_DATA
from .logic.barrows_logic import apply_barrows_command_pure
from .logic.fist_of_guthix_logic import apply_fist_of_guthix_command_pure
from .logic.fight_caves_logic import apply_fight_caves_command_pure
from .logic.dagannoth_kings_logic import apply_dagannoth_kings_command_pure
from .logic.dungeoneering_logic import apply_dungeoneering_command_pure
from .logic.phoenix_lair_logic import (
    apply_phoenix_lair_command_pure,
    resolve_phoenix_egg_choice_pure,
)
from .data.bork_data import BORK_ACTIVITY_ID
from .logic.bork_logic import apply_bork_command_pure
from .logic.skeletal_horror_logic import apply_skeletal_horror_command_pure
from .logic.tears_of_guthix_logic import apply_tears_of_guthix_command_pure
from .logic.enchanted_key_logic import apply_enchanted_key_command_pure
from .logic.stealing_creation_logic import (
    apply_stealing_creation_command_pure,
    apply_stealing_creation_xp_bonus_pure,
    stealing_creation_tool_can_apply_pure,
)
from .logic.fish_flingers_logic import apply_fish_flingers_command_pure
from .logic.fishing_trawler_logic import apply_fishing_trawler_command_pure
from .logic.great_orb_project_logic import (
    apply_great_orb_project_command_pure,
    use_great_orb_project_teleport_tablet_pure,
)
from .logic.court_cases_logic import apply_court_cases_command_pure
from .logic.circus_logic import apply_circus_command_pure
from .logic.trouble_brewing_logic import (
    apply_trouble_brewing_command_pure,
    drink_trouble_brewing_rum_pure,
)
from .logic.castle_wars_logic import apply_castle_wars_command_pure
from .logic.pest_control_logic import apply_pest_control_command_pure
from .logic.conquest_logic import apply_conquest_command_pure
from .logic.barbarian_assault_logic import apply_barbarian_assault_command_pure
from .logic.stronghold_player_safety_logic import (
    apply_stronghold_player_safety_command_pure,
)
from .logic.soul_wars_logic import apply_soul_wars_command_pure
from .logic.shades_of_mortton_logic import apply_shades_of_mortton_command_pure
from .logic.achievement_diary_logic import apply_achievement_diary_command_pure
from .logic.music_log_logic import refresh_music_log_pure
from .logic.tzhaar_fight_pit_logic import apply_tzhaar_fight_pit_command_pure
from .data.duel_arena_data import DUEL_ARENA_ACTIVITY_ID
from .logic.duel_arena_logic import apply_duel_arena_command_pure
from .data.clan_wars_data import CLAN_WARS_ACTIVITY_ID
from .logic.clan_wars_logic import apply_clan_wars_command_pure
from .data.skeletal_horror_data import SKELETAL_HORROR_ACTIVITY_ID
from .data.troll_invasion_data import TROLL_INVASION_ACTIVITY_ID

from .logic.troll_invasion_logic import apply_troll_invasion_command_pure
from .logic.shattered_heart_logic import apply_shattered_heart_command_pure
from .data.mage_training_arena_data import MAGE_TRAINING_ARENA_ACTIVITY_ID
from .logic.mage_training_arena_logic import apply_mage_training_arena_command_pure
from .data.ranging_guild_data import RANGING_GUILD_ACTIVITY_ID
from .logic.ranging_guild_logic import apply_ranging_guild_command_pure
from .data.temple_trekking_data import TEMPLE_TREKKING_ACTIVITY_ID
from .logic.temple_trekking_logic import apply_temple_trekking_command_pure
from .data.mobilising_armies_data import MOBILISING_ARMIES_ACTIVITY_ID
from .logic.mobilising_armies_logic import apply_mobilising_armies_command_pure
from .data.item_values import ITEM_VALUES
from .data.gnome_restaurant_data import GNOME_RESTAURANT_ACTIVITY_ID
from .logic.gnome_restaurant_logic import apply_gnome_restaurant_command_pure
from .data.dominion_tower_data import DOMINION_TOWER_ACTIVITY_ID
from .logic.dominion_tower_logic import apply_dominion_tower_command_pure
from .data.crucible_data import CRUCIBLE_ACTIVITY_ID
from .logic.crucible_logic import apply_crucible_command_pure
from .data.goblin_raids_data import GOBLIN_RAIDS_ACTIVITY_ID
from .logic.goblin_raids_logic import (
    advance_goblin_raids_world_clock_pure,
    apply_goblin_cower_shield_bonus_pure,
    apply_goblin_raids_command_pure,
    goblin_cower_shield_can_apply_pure,
    goblin_raids_spawn_due_pure,
)
from .logic.treasure_trails_logic import (
    apply_treasure_trails_command_pure,
    treasure_trails_view_pure,
)
from .logic.daily_challenges_logic import (
    advance_daily_challenges_day_pure,
    apply_daily_challenges_command_pure,
    daily_challenges_view_pure,
)
from .logic.varrock_museum_logic import apply_varrock_museum_command_pure
from .logic.managing_miscellania_logic import (
    advance_managing_miscellania_world_clock_pure,
    apply_managing_miscellania_command_pure,
)
from .data.sorceress_garden_data import SORCERESS_GARDEN_ACTIVITY_ID
from .logic.sorceress_garden_logic import apply_sorceress_garden_command_pure
from .data.penguin_hide_and_seek_data import PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID
from .logic.penguin_hide_and_seek_logic import apply_penguin_command_pure
from .data.vinesweeper_data import VINESWEEPER_ACTIVITY_ID
from .logic.vinesweeper_logic import apply_vinesweeper_command_pure
from .core.injectors import inject_reviewer_floating_button as _inject_reviewer_floating_button
from .core.injectors import inject_overview_floating_button as _inject_overview_floating_button
from .core.injectors import register_deck_browser_button as _register_deck_browser_button
from .core.injectors import force_deck_browser_refresh as _force_deck_browser_refresh
from .core.storage import load_player_data as storage_load_player_data, save_player_data as storage_save_player_data
from .core.action_registry import (
    ACTIVITY_REVIEW_ACTION_DISPLAY_NAME,
    UTILITY_REVIEW_ACTION_DISPLAY_NAME,
    is_review_action,
    review_action_handler_key,
)
from .core.skill_registry import get_skill, trainable_skill_definitions
from .logic.shop_logic import advance_shop_market_clock_pure
from .logic.wicked_hood_logic import (
    advance_wicked_hood_review_day_pure,
    apply_wicked_hood_command_pure,
)
from .data.grand_exchange_data import GE_ITEM_CATALOG
from .logic.grand_exchange_logic import (
    ge_guide_prices_pure,
    advance_ge_market_tick_pure,
    apply_ge_frontend_action_pure,
    ge_frontend_projection_pure,
)
from .logic.dnd_favourites_logic import toggle_dnd_favourite_pure
from .logic.bank_layout_logic import reconcile_bank_layout_for_player_pure
from .logic.review_strip_logic import (
    record_review_event_pure,
    request_review_bank_run_pure,
)
from .logic.farming_logic import apply_farming_frontend_action_pure, farming_frontend_projection_pure
from .logic.agility_logic import apply_agility_command_pure
from .logic.skilling_boost_logic import (
    set_skilling_potion_target_enabled_pure,
)
from .logic.cooking_gauntlets_logic import (
    apply_family_gauntlet_conversion_pure,
    recover_family_gauntlets_pure,
    reconcile_cooking_equipment_pure,
    set_cooking_equipment_choice_pure,
)
from .data.cooking_gauntlets_data import FAMILY_GAUNTLET_ITEMS
from .logic.brawling_gloves_logic import set_brawling_wilderness_target_pure
from .logic.flash_powder_factory_logic import convert_rogue_kit_pure
from .core.review_context import (
    PIT_REWARD_CONTEXT_ID,
    SHOOTING_STAR_NOTICE_CONTEXT_ID,
    ignored_review_context_choice_pure,
)
from .data.phoenix_lair_data import PHOENIX_EGG_CONTEXT_ID
from .logic.agility_travel import agility_carried_weight_pure
from .logic.summoning_logic import (
    advance_summoning_world_tick_pure,
    claim_familiarisation_reward_pure,
    dismiss_familiar_pure,
    reclaim_familiar_cargo_pure,
    renew_familiar_pure,
    restore_summoning_points_pure,
    start_familiarisation_pure,
    set_winter_storage_priority_pure,
    summon_familiar_pure,
)
from .logic.slayer_logic import get_slayer_assignment_pure
from .data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from .logic.big_chinchompa_logic import (
    advance_big_chinchompa_world_clock_pure,
    apply_big_chinchompa_reward_purchase_pure,
    set_hunter_private_ground_pure,
)
from .data.evil_tree_data import EVIL_TREE_UTILITY_ID
from .logic.evil_tree_logic import (
    advance_evil_tree_world_clock_pure,
    evil_tree_spawn_due_pure,
)
from .data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
from .logic.shooting_star_logic import (
    advance_shooting_star_world_clock_pure,
    apply_shooting_star_exchange_pure,
    apply_shooting_star_join_pure,
    apply_shooting_star_notice_action_pure,
)
from .logic.warriors_guild_logic import (
    enter_warriors_guild_cyclops_room_pure,
    leave_warriors_guild_cyclops_room_pure,
    sanitize_warriors_guild_state_pure,
    set_warriors_guild_policy_pure,
    show_warriors_guild_defender_pure,
)
from .logic.livid_farm_logic import (
    advance_livid_farm_wish_effects_pure,
    apply_arcane_capacitor_charge_pure,
    apply_arcane_capacitor_remove_charge_pure,
    apply_livid_farm_wish_pure,
    set_livid_farm_routine_pure,
)
from .logic.pet_logic import (
    hatch_phoenix_egg_pure,
    let_out_pet_pure,
    release_pet_pure,
    store_active_pet_pure,
)
from .runtime import runtime_actions
from .runtime.runtime_actions import RuntimeActionContext
from .logic.cadence_coverage import SINGLE_TICK_UTILITY_IDS


global card_turned, exp_awarded, answer_shown

answer_shown = False
card_turned = False
exp_awarded = False

current_skill = "None"

_SPECIAL_ACTIVITY_TARGETS = {
    "stronghold_of_security",
    "knight_waves",
    "mage_arena",
    EVIL_TREE_UTILITY_ID,
    BIG_CHINCHOMPA_UTILITY_ID,
}


def _utility_surface_for_target(activity_id) -> str:
    target = str(activity_id or "")
    if (
        target in _SPECIAL_ACTIVITY_TARGETS
        or target.startswith("mage_arena_attune:")
        or UTILITY_ACTIVITY_DATA.get(target, {}).get("surface")
        == ACTIVITY_SURFACE_ID
    ):
        return ACTIVITY_REVIEW_ACTION_DISPLAY_NAME
    return UTILITY_REVIEW_ACTION_DISPLAY_NAME


def _normalize_legacy_utility_skill(skill) -> str:
    name = str(skill or "None")
    if name in {"Utility", "Utility / Activities"}:
        return _utility_surface_for_target(
            player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
        )
    return name


def start_activity_for_reviews(activity_id) -> bool:
    """Select one utility/activity target and its review surface atomically."""
    target = str(activity_id or "")
    if not target:
        return False
    if target == SHOOTING_STAR_ACTIVITY_ID:
        updated, joined, info = apply_shooting_star_join_pure(player_data)
        if not joined and info.get("unminable"):
            if not info.get("notice_created"):
                return False
            updated = record_review_event_pure(
                updated,
                "activity",
                str(info.get("event_log_text", "Star unminable at your level")),
            )
            player_data.clear()
            player_data.update(updated)
            _deactivate_current_skill()
            save_player_data()
            update_review_event_log_drawer(player_data)
            _update_review_context_surface()
            return False
        if not joined:
            return False
        player_data.clear()
        player_data.update(updated)
    player_data["current_utility"] = target
    save_skill(_utility_surface_for_target(target), None)
    save_player_data()
    return True

# --- Debug logging (centralized) ---
from .core.debug import debug_log  # size-rotated, disabled by default unless ANKISCAPE_DEBUG=1
try:
    from .core.debug import set_debug_enabled as _set_debug_enabled, is_debug_enabled as _is_debug_enabled
except Exception:
    def _set_debug_enabled(_enabled: bool) -> None:
        pass
    def _is_debug_enabled() -> bool:
        return False

_REVIEW_UNDO_STACK = []
_URN_TELEPORT_UNDO_STACK = []
_DIRECT_ACTION_UNDO_STACK = []
_MAX_REVIEW_UNDO_SNAPSHOTS = 30
_MAX_URN_TELEPORT_UNDO_SNAPSHOTS = 50
_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS = 50
_URN_TELEPORT_UNDO_OPERATION = "Teleport training urn"
_DIRECT_ACTION_UNDO_OPERATION = "AnkiScape direct action"
_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY = "ankiscape_review_action_multiplier"
_CADENCE_KERNEL_CONFIG_KEY = "ankiscape_cadence_kernel"
_LEGACY_XP_MULTIPLIER_CONFIG_KEY = "ankiscape_xp_multiplier"
_REVIEW_FEEDBACK_CONTEXT = None
_REVIEW_FEEDBACK_INITIAL_XP = 0.0
_REVIEW_FEEDBACK_FLUSHING = False


class _NamedExperience(float):
    """A numeric XP result that carries the skills which earned it."""

    def __new__(cls, amount, skill_names=(), breakdown=()):
        value = super().__new__(cls, float(amount))
        value.skill_names = tuple(
            dict.fromkeys(str(name) for name in skill_names if name)
        )
        totals = {}
        for name, skill_amount in breakdown:
            amount_value = float(skill_amount)
            if name and amount_value > 0:
                key = str(name)
                totals[key] = totals.get(key, 0.0) + amount_value
        if not totals and len(value.skill_names) == 1:
            totals[value.skill_names[0]] = float(value)
        value.breakdown = tuple(totals.items())
        return value

    @property
    def display_text(self) -> str:
        def amount_text(amount) -> str:
            value = float(amount)
            return f"{value:.1f}" if 0 < value < 1 else str(int(value))

        if len(self.breakdown) > 1:
            return " · ".join(
                f"{name} +{amount_text(amount)} XP"
                for name, amount in self.breakdown
            )
        message = f"+{amount_text(self)} XP"
        if self.skill_names:
            message += f" · {', '.join(self.skill_names)}"
        return message

    def __add__(self, other):
        return _NamedExperience(
            float(self) + float(other),
            (*self.skill_names, *getattr(other, "skill_names", ())),
            (*self.breakdown, *getattr(other, "breakdown", ())),
        )

    def __radd__(self, other):
        return _NamedExperience(
            float(other) + float(self),
            (*getattr(other, "skill_names", ()), *self.skill_names),
            (*getattr(other, "breakdown", ()), *self.breakdown),
        )

def show_review_popup():
    ui.show_review_popup()


# Classes moved to ui.py


def save_player_data():
    player_data.update(reconcile_bank_layout_for_player_pure(player_data))
    storage_save_player_data(player_data, current_skill)


def load_player_data():
    global player_data, current_skill
    player_data, current_skill = storage_load_player_data()
    current_skill = _normalize_legacy_utility_skill(current_skill)
    ui.update_menu_visibility(current_skill)

## Removed legacy get_exp_to_next_level stub; use logic_pure.get_exp_to_next_level in tests/pure logic.

# UI functions

def initialize_skill():
    global current_skill
    current_skill = mw.col.get_config("ankiscape_current_skill", default="None")
    normalized_skill = _normalize_legacy_utility_skill(current_skill)
    if normalized_skill != current_skill:
        current_skill = normalized_skill
        mw.col.set_config("ankiscape_current_skill", current_skill)
    ui.update_menu_visibility(current_skill)


def _initialize_debug_from_config():
    try:
        enabled = False
        if mw and getattr(mw, 'col', None):
            # New: developer mode controls logging
            enabled = bool(mw.col.get_config("ankiscape_developer_mode", False))
            # Back-compat: honor previous key if present and new key missing
            if not enabled:
                enabled = bool(mw.col.get_config("ankiscape_debug_enabled", False))
        _set_debug_enabled(enabled)
        if enabled:
            debug_log("debug: enabled from config on profile load (developer mode)")
    except Exception:
        pass


# --- Small helpers to reduce duplication ---
def _record_review_event(kind: str, text: str, *, persist: bool) -> None:
    """The single runtime seam behind every floating review notification."""

    updated = record_review_event_pure(player_data, kind, text)
    player_data["review_event_log"] = updated["review_event_log"]
    if persist:
        try:
            storage_save_player_data(player_data, current_skill)
        except (AttributeError, RuntimeError):
            pass
    try:
        update_review_event_log_drawer(player_data)
    except Exception:
        pass


def _show_exp(exp_gained, *, record_event: bool = True) -> None:
    """Record one XP drop, then display it when floating feedback is enabled."""
    try:
        skill_names = list(getattr(exp_gained, "skill_names", ()))
        if _REVIEW_FEEDBACK_CONTEXT is not None:
            try:
                _REVIEW_FEEDBACK_CONTEXT["xp"] += float(exp_gained)
            except (TypeError, ValueError):
                pass
            return
        if not skill_names and current_skill not in {"", "None"}:
            skill_names.append(str(current_skill))
        if not isinstance(exp_gained, _NamedExperience):
            exp_gained = _NamedExperience(exp_gained, skill_names)
        message = exp_gained.display_text
        if record_event:
            _record_review_event(
                "xp", message, persist=not _REVIEW_FEEDBACK_FLUSHING
            )
        # Respect user setting for floating XP (default True)
        show_xp = True
        try:
            if mw and getattr(mw, 'col', None):
                show_xp = bool(mw.col.get_config("ankiscape_floating_xp_enabled", True))
        except Exception:
            show_xp = True
        if show_xp:
            if not hasattr(mw, 'exp_popup'):
                mw.exp_popup = ExpPopup(mw)
            mw.exp_popup.show_exp(exp_gained)
        # Keep HUD progress in sync with new XP
        try:
            update_review_hud(player_data, current_skill)
        except Exception:
            pass
    except Exception:
        pass


def _refresh_open_carried_inventory() -> None:
    refresh_inventory = ui._MAIN_MENU_CTX.get("refresh_carried_inventory")
    if callable(refresh_inventory):
        refresh_inventory()


def _show_activity_gain(text: str) -> None:
    """Record and show a no-XP Utility or Activity result."""
    try:
        if _REVIEW_FEEDBACK_CONTEXT is not None:
            _REVIEW_FEEDBACK_CONTEXT["activity"].append(str(text))
            return
        message = str(text)
        _record_review_event(
            "activity", message, persist=not _REVIEW_FEEDBACK_FLUSHING
        )
        show_popup = True
        try:
            if mw and getattr(mw, "col", None):
                show_popup = bool(mw.col.get_config("ankiscape_floating_xp_enabled", True))
        except Exception:
            show_popup = True
        if show_popup:
            if not hasattr(mw, "exp_popup"):
                mw.exp_popup = ExpPopup(mw)
            mw.exp_popup.show_text(message)
    except Exception:
        pass


def _combine_activity_feedback(messages) -> str:
    plus_totals = {}
    opened_nests = 0
    for message in messages:
        text = str(message)
        if text.startswith("+"):
            parts = text[1:].split(" ", 1)
            if len(parts) == 2:
                try:
                    amount = int(parts[0])
                except ValueError:
                    amount = 0
                if amount > 0:
                    item = parts[1]
                    plus_totals[item] = plus_totals.get(item, 0) + amount
                    continue
        if text.startswith("Opened ") and " bird nest" in text:
            parts = text.split(" ", 2)
            if len(parts) >= 2:
                try:
                    opened_nests += int(parts[1])
                    continue
                except ValueError:
                    pass

    if plus_totals and len(plus_totals) == 1 and opened_nests == 0:
        item, amount = next(iter(plus_totals.items()))
        return f"+{amount} {item}"
    if opened_nests > 0 and not plus_totals:
        return f"Opened {opened_nests} bird nest{'s' if opened_nests != 1 else ''}"
    return messages[-1] if messages else ""


def _begin_review_feedback_context() -> None:
    global _REVIEW_FEEDBACK_CONTEXT, _REVIEW_FEEDBACK_INITIAL_XP
    initial_xp = _REVIEW_FEEDBACK_INITIAL_XP
    initial_exp = _implemented_exp_keys_snapshot()
    _REVIEW_FEEDBACK_CONTEXT = {
        "xp": float(initial_xp or 0.0),
        "skills": list(getattr(initial_xp, "skill_names", ())),
        "initial_exp": initial_exp,
        "recorded_exp": initial_exp,
        "combat_level_before": player_combat_level_pure(player_data),
        "activity": [],
    }
    _REVIEW_FEEDBACK_INITIAL_XP = 0.0


def _record_pending_review_xp_event() -> None:
    context = _REVIEW_FEEDBACK_CONTEXT
    if context is None:
        return
    recorded_exp = context.get("recorded_exp", {})
    breakdown = []
    for skill in trainable_skill_definitions():
        gained = float(player_data.get(skill.exp_key, 0) or 0) - float(
            recorded_exp.get(skill.exp_key, 0) or 0
        )
        if gained > 0:
            breakdown.append((skill.display_name, gained))
    if not breakdown:
        return
    total = sum(amount for _name, amount in breakdown)
    _record_review_event(
        "xp",
        _NamedExperience(
            total,
            (name for name, _amount in breakdown),
            breakdown,
        ).display_text,
        persist=False,
    )
    context["recorded_exp"] = _implemented_exp_keys_snapshot()


def level_up_check(skill, data) -> None:
    _record_pending_review_xp_event()
    _core_level_up_check(skill, data)


def _finish_review_feedback_context() -> None:
    global _REVIEW_FEEDBACK_CONTEXT, _REVIEW_FEEDBACK_FLUSHING
    context = _REVIEW_FEEDBACK_CONTEXT or {
        "xp": 0.0,
        "skills": [],
        "initial_exp": {},
        "activity": [],
    }
    _record_pending_review_xp_event()
    _REVIEW_FEEDBACK_CONTEXT = None
    _REVIEW_FEEDBACK_FLUSHING = True
    try:
        xp_total = context.get("xp", 0.0)
        try:
            xp_total = float(xp_total)
        except (TypeError, ValueError):
            xp_total = 0.0
        skill_names = list(context.get("skills", ()))
        initial_exp = context.get("initial_exp", {})
        breakdown = []
        for skill in trainable_skill_definitions():
            gained = float(player_data.get(skill.exp_key, 0) or 0) - float(
                initial_exp.get(skill.exp_key, 0) or 0
            )
            if gained > 0:
                breakdown.append((skill.display_name, gained))
                if skill.display_name not in skill_names:
                    skill_names.append(skill.display_name)
        activity_messages = context.get("activity", [])
        if xp_total > 0:
            _show_exp(
                _NamedExperience(xp_total, skill_names, breakdown),
                record_event=False,
            )
            for message in activity_messages:
                _record_review_event("activity", str(message), persist=False)
        elif activity_messages:
            combined = _combine_activity_feedback(activity_messages)
            if combined:
                _show_activity_gain(combined)
        try:
            update_review_hud(player_data, current_skill)
        except Exception:
            pass
        _core_combat_level_up_check(
            context["combat_level_before"],
            player_data,
        )
    finally:
        _REVIEW_FEEDBACK_FLUSHING = False


def _catalog_requirement_item_names(*catalogs) -> set[str]:
    names = set()
    for catalog in catalogs:
        for spec in catalog.values():
            if not isinstance(spec, Mapping):
                continue
            for key in ("requirements", "required_items", "tools"):
                values = spec.get(key, {})
                if isinstance(values, Mapping):
                    names.update(str(name) for name in values)
            material_options = spec.get("material_options", {})
            if isinstance(material_options, Mapping):
                for name, alternatives in material_options.items():
                    names.add(str(name))
                    if isinstance(alternatives, (tuple, list, set)):
                        names.update(str(alternative) for alternative in alternatives)
    return names


_SKILL_AVAILABILITY_INVENTORY_NAMES = _catalog_requirement_item_names(
    SMITHING_DATA,
    CRAFTING_DATA,
    FLETCHING_DATA,
    FIREMAKING_DATA,
    HUNTER_DATA,
    COOKING_DATA,
)
_SKILL_AVAILABILITY_LEVEL_KEYS = {
    "smithing_level",
    "crafting_level",
    "fletching_level",
    "firemaking_level",
    "hunter_level",
    "cooking_level",
    "runecrafting_level",
}
for _hunter_spec in HUNTER_DATA.values():
    _requirements = _hunter_spec.get("skill_requirements", {})
    if isinstance(_requirements, Mapping):
        _SKILL_AVAILABILITY_LEVEL_KEYS.update(
            f"{skill_id}_level" for skill_id in _requirements
        )
_SKILL_AVAILABILITY_QUEST_IDS = {"rune_mysteries"}
_SKILL_AVAILABILITY_ABILITY_IDS = set()
for _unlock_rule in QUEST_UNLOCK_RULES:
    if not isinstance(_unlock_rule, Mapping):
        continue
    if _unlock_rule.get("skill_id") not in {
        "crafting",
        "fletching",
        "firemaking",
        "hunter",
        "cooking",
        "runecrafting",
    }:
        continue
    for _requirement in _unlock_rule.get("requirements", ()) or ():
        if not isinstance(_requirement, Mapping):
            continue
        _quest_id = _requirement.get("quest_id")
        _ability_id = _requirement.get("ability_id")
        if isinstance(_quest_id, str) and _quest_id:
            _SKILL_AVAILABILITY_QUEST_IDS.add(_quest_id)
        if isinstance(_ability_id, str) and _ability_id:
            _SKILL_AVAILABILITY_ABILITY_IDS.add(_ability_id)
for _runecrafting_spec in RUNECRAFTING_DATA.values():
    for _key in (
        "component_rune",
        "consumed_talisman",
        "input_item",
        "talisman_item",
    ):
        _item_name = _runecrafting_spec.get(_key)
        if isinstance(_item_name, str) and _item_name:
            _SKILL_AVAILABILITY_INVENTORY_NAMES.add(_item_name)
    _SKILL_AVAILABILITY_INVENTORY_NAMES.update(
        str(item_name)
        for item_name in _runecrafting_spec.get("essence_items", ()) or ()
    )
_SKILL_AVAILABILITY_INVENTORY_NAMES.update(
    {"Pure essence", "Tiara", "Wicked hood"}
)
_SKILL_AVAILABILITY_INVENTORY_NAMES = tuple(
    sorted(_SKILL_AVAILABILITY_INVENTORY_NAMES)
)
_SKILL_AVAILABILITY_LEVEL_KEYS = tuple(sorted(_SKILL_AVAILABILITY_LEVEL_KEYS))
_SKILL_AVAILABILITY_QUEST_IDS = tuple(sorted(_SKILL_AVAILABILITY_QUEST_IDS))
_SKILL_AVAILABILITY_ABILITY_IDS = tuple(sorted(_SKILL_AVAILABILITY_ABILITY_IDS))
_SKILL_AVAILABILITY_CACHE_FINGERPRINT = None


def _freeze_skill_availability_value(value):
    if isinstance(value, Mapping):
        return tuple(
            sorted(
                (str(key), _freeze_skill_availability_value(item))
                for key, item in value.items()
            )
        )
    if isinstance(value, (tuple, list, set)):
        return tuple(_freeze_skill_availability_value(item) for item in value)
    return value


def _skill_availability_fingerprint():
    inventory = player_data.get("inventory", {}) or {}
    quests = player_data.get("quests", {}) or {}
    abilities = player_data.get("unlocked_abilities", ()) or ()
    current_runecrafting = str(player_data.get("current_runecrafting", "") or "")
    carried = player_data.get("carried_inventory", {}) or {}
    carried_view = carried.get(current_runecrafting, {}) if isinstance(carried, Mapping) else {}
    equipment = player_data.get("equipment", {}) or {}
    return (
        tuple((key, player_data.get(key, 1)) for key in _SKILL_AVAILABILITY_LEVEL_KEYS),
        _freeze_skill_availability_value(player_data.get("skilling_current_levels", {})),
        tuple((name, inventory.get(name, 0)) for name in _SKILL_AVAILABILITY_INVENTORY_NAMES),
        tuple(
            (
                quest_id,
                bool((quests.get(quest_id, {}) or {}).get("started")),
                bool((quests.get(quest_id, {}) or {}).get("completed")),
            )
            for quest_id in _SKILL_AVAILABILITY_QUEST_IDS
        ),
        tuple(
            (ability_id, ability_id in abilities)
            for ability_id in _SKILL_AVAILABILITY_ABILITY_IDS
        ),
        bool(player_data.get("magic_imbue_active", False)),
        equipment.get("head") if isinstance(equipment, Mapping) else None,
        _freeze_skill_availability_value(player_data.get("wicked_hood", {})),
        current_runecrafting,
        (
            carried_view.get("Wicked hood", 0)
            if isinstance(carried_view, Mapping)
            else 0
        ),
    )


def _refresh_skill_availability() -> None:
    """Refresh menu availability only when one of its real inputs changed."""
    global _SKILL_AVAILABILITY_CACHE_FINGERPRINT
    try:
        fingerprint = _skill_availability_fingerprint()
        if fingerprint == _SKILL_AVAILABILITY_CACHE_FINGERPRINT:
            return
        values = (
            can_smith_any(),
            any(
                not crafting_target_locked_reasons_pure(
                    player_data,
                    item_name,
                    CRAFTING_DATA,
                    QUEST_UNLOCK_RULES,
                )
                for item_name in CRAFTING_DATA.keys()
            ),
            any(
                not fletching_target_locked_reasons_pure(
                    player_data,
                    target_key,
                    FLETCHING_DATA,
                    QUEST_UNLOCK_RULES,
                )
                for target_key in FLETCHING_DATA.keys()
            ),
            any(
                not firemaking_target_locked_reasons_pure(
                    player_data,
                    target_key,
                    FIREMAKING_DATA,
                    QUEST_UNLOCK_RULES,
                )
                for target_key in FIREMAKING_DATA.keys()
            ),
            any(
                not hunter_target_locked_reasons_pure(
                    player_data,
                    target_key,
                    HUNTER_DATA,
                    QUEST_UNLOCK_RULES,
                )
                for target_key in HUNTER_DATA.keys()
            ),
            any(
                not cooking_target_locked_reasons_pure(
                    player_data,
                    target_key,
                    COOKING_DATA,
                    QUEST_UNLOCK_RULES,
                )
                for target_key in COOKING_DATA.keys()
            ),
            can_runecraft_any_pure(
                player_data,
                RUNECRAFTING_DATA,
                RUNECRAFTING_POUCH_DATA,
                QUEST_UNLOCK_RULES,
            ),
        )
        refresh_skill_availability(*values)
        _SKILL_AVAILABILITY_CACHE_FINGERPRINT = fingerprint
    except Exception:
        pass


def _review_action_multiplier() -> int:
    try:
        if mw and getattr(mw, 'col', None):
            raw_value = mw.col.get_config(_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY, None)
            if raw_value is None:
                raw_value = mw.col.get_config(_LEGACY_XP_MULTIPLIER_CONFIG_KEY, 1)
            return sanitize_review_action_multiplier(raw_value)
    except Exception:
        pass
    return 1


def _cadence_kernel_enabled() -> bool:
    try:
        if mw and getattr(mw, 'col', None):
            raw_value = mw.col.get_config(_CADENCE_KERNEL_CONFIG_KEY, True)
            return sanitize_cadence_kernel_enabled_pure(raw_value, default=True)
    except Exception:
        pass
    return True


def _award_skill_exp(
    exp_key: str,
    base_exp: float,
    *,
    action_skill_id: str | None = None,
) -> float:
    action_skill_id = str(action_skill_id or current_skill).lower()
    skill_id = str(exp_key).removesuffix("_exp")
    skill = get_skill(skill_id)
    skill_name = (
        skill.display_name if skill is not None else skill_id.replace("_", " ").title()
    )
    # The Goblin cower shield pays 25% bonus Attack, Defence and Constitution
    # experience out of a 1,000-experience budget, then turns cosmetic. It rides
    # the same seam the Stealing Creation tools use rather than a second one.
    if goblin_cower_shield_can_apply_pure(player_data, exp_key):
        shield_updated, shield_bonus, _shield_info = (
            apply_goblin_cower_shield_bonus_pure(player_data, exp_key, base_exp)
        )
        player_data.clear()
        player_data.update(shield_updated)
        base_exp = float(base_exp) + float(shield_bonus)
    if not stealing_creation_tool_can_apply_pure(
        player_data,
        exp_key,
        action_skill_id,
    ):
        player_data[exp_key] = player_data.get(exp_key, 0) + base_exp
        return _NamedExperience(base_exp, (skill_name,))
    updated, bonus_exp, _tool_info = apply_stealing_creation_xp_bonus_pure(
        player_data,
        exp_key,
        base_exp,
        random.random,
        action_skill_id=action_skill_id,
    )
    player_data.clear()
    player_data.update(updated)
    total_exp = float(base_exp) + float(bonus_exp)
    player_data[exp_key] = player_data.get(exp_key, 0) + total_exp
    return _NamedExperience(total_exp, (skill_name,))


def _update_review_context_surface() -> None:
    try:
        update_review_context_action_strip(
            player_data,
            resolve_review_context_action,
        )
    except Exception:
        pass


def commit_direct_action(apply_change, *, after_apply=None, selected_skill=None):
    """Run one mutating menu action as a single undoable Anki operation.

    `apply_change` receives the live save and returns `(updated, ok)`. Returning
    `ok=False` refuses the action: nothing is written and the random state is put
    back, so a refusal the player never saw cannot advance the sequence. Optional
    `after_apply` work runs after the undo entry exists but before the save commit.

    This is the seam. Before it existed the snapshot, custom-undo-entry, bounded
    stack and commit lived inline in `resolve_review_context_action`, which meant
    the reviewer context strip was the only surface in the add-on whose actions
    could be undone. Thirty-one command handlers mutated and saved without one.

    The snapshot deep-copies the save deliberately. Undo must restore nested
    state that the shallow-copy convention elsewhere leaves shared, so this is one
    of the few places a whole-save copy is load-bearing rather than waste.

    Returns True when the change was committed.
    """
    global current_skill
    before = {
        "player_data": copy.deepcopy(player_data),
        "random_state": random.getstate(),
        "current_skill": current_skill,
    }
    updated, ok = apply_change(player_data)
    if not ok:
        random.setstate(before["random_state"])
        return False
    updated = refresh_music_log_pure(updated)[0]
    try:
        mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
    except (AttributeError, RuntimeError):
        random.setstate(before["random_state"])
        return False
    _DIRECT_ACTION_UNDO_STACK.append(before)
    if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
        del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
    player_data.clear()
    player_data.update(updated)
    if selected_skill is not None:
        current_skill = _normalize_legacy_utility_skill(selected_skill)
        try:
            mw.col.set_config("ankiscape_current_skill", current_skill)
        except AttributeError:
            pass
        ui.update_menu_visibility(current_skill)
    if after_apply is not None:
        after_apply()
    save_player_data()
    try:
        mw.update_undo_actions()
    except (AttributeError, RuntimeError):
        pass
    return True


def resolve_review_context_action(family_id: str, option_id: str) -> bool:
    """Resolve one explicit reviewer-context choice as a direct undoable action."""

    if family_id == SHOOTING_STAR_NOTICE_CONTEXT_ID:
        def _apply_star_notice(current):
            updated, ok, _result = apply_shooting_star_notice_action_pure(
                current,
                option_id,
            )
            return updated, ok

        committed = commit_direct_action(
            _apply_star_notice,
            selected_skill=(
                ACTIVITY_REVIEW_ACTION_DISPLAY_NAME
                if option_id == "mine"
                else None
            ),
        )
        if not committed:
            _update_review_context_surface()
            return False
        try:
            update_review_hud(player_data, current_skill)
            update_review_status_badge(
                player_data, _open_activities_sheet, _open_farming_sheet
            )
        except Exception:
            pass
        _update_review_context_surface()
        return True

    valid = (
        family_id == PIT_REWARD_CONTEXT_ID
        and option_id in {"take_xp", "gamble"}
    ) or (
        family_id == PHOENIX_EGG_CONTEXT_ID
        and option_id in {"clap", "kick"}
    )
    if not valid:
        return False
    before = {
        "player_data": copy.deepcopy(player_data),
        "random_state": random.getstate(),
    }
    if family_id == PHOENIX_EGG_CONTEXT_ID:
        updated, allowed, result = resolve_phoenix_egg_choice_pure(
            player_data,
            option_id,
            remember_choice=True,
        )
    else:
        action_id = (
            "gamble_pit_reward" if option_id == "gamble" else "claim_pit_reward"
        )
        roll = random.random() if option_id == "gamble" else 0.5
        updated, result = apply_agility_command_pure(
            player_data,
            action_id,
            {"remember_choice": True},
            roll=roll,
        )
        allowed = bool(result.get("allowed"))
    if not allowed:
        random.setstate(before["random_state"])
        _update_review_context_surface()
        return False
    try:
        mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
    except (AttributeError, RuntimeError):
        random.setstate(before["random_state"])
        return False
    _DIRECT_ACTION_UNDO_STACK.append(before)
    if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
        del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
    player_data.clear()
    player_data.update(updated)
    xp = float(result.get("xp", 0.0) or 0.0)
    if xp > 0:
        gained = _award_skill_exp("agility_exp", xp)
        level_up_check("Agility", player_data)
        _show_exp(gained)
    check_achievements(player_data)
    save_player_data()
    _refresh_skill_availability()
    try:
        mw.update_undo_actions()
        update_review_hud(player_data, current_skill)
    except AttributeError:
        pass
    _update_review_context_surface()
    return True


def _resolve_ignored_review_context_for_answer() -> float:
    pending = ignored_review_context_choice_pure(player_data)
    if pending is None:
        return 0.0
    family_id, option_id = pending
    if family_id == PHOENIX_EGG_CONTEXT_ID:
        updated, ok, _result = resolve_phoenix_egg_choice_pure(
            player_data,
            option_id,
        )
        if not ok:
            return 0.0
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        return 0.0
    if family_id != PIT_REWARD_CONTEXT_ID:
        return 0.0
    action_id = (
        "gamble_pit_reward" if option_id == "gamble" else "claim_pit_reward"
    )
    updated, result = apply_agility_command_pure(
        player_data,
        action_id,
        {},
        roll=random.random() if option_id == "gamble" else 0.5,
    )
    if not result.get("allowed"):
        return 0.0
    player_data.clear()
    player_data.update(updated)
    xp = float(result.get("xp", 0.0) or 0.0)
    if xp > 0:
        _award_skill_exp("agility_exp", xp)
        level_up_check("Agility", player_data)
        check_achievements(player_data)
    return xp


def _award_hidden_skill_exp(exp_key: str, level_key: str, base_exp: float) -> None:
    if base_exp <= 0:
        return
    player_data[exp_key] = player_data.get(exp_key, 0) + base_exp
    player_data[level_key] = calculate_new_level(
        player_data.get(exp_key, 0),
        player_data.get(level_key, 1),
        EXP_TABLE,
    )


def set_prayer_selection(material_id: str, ui_method_id: str) -> bool:
    updated, ok, _reasons = apply_prayer_selection_pure(player_data, material_id, ui_method_id, PRAYER_DATA)
    if not ok:
        return False
    player_data.clear()
    player_data.update(updated)
    save_player_data()
    update_review_hud(player_data, current_skill)
    return True


def teleport_training_urn(urn_id: str) -> bool:
    updated, base_xp, ok, skill_id = teleport_full_urn_pure(player_data, urn_id)
    skill = get_skill(skill_id)
    if not ok or skill is None:
        return False
    try:
        mw.col.add_custom_undo_entry(_URN_TELEPORT_UNDO_OPERATION)
    except (AttributeError, RuntimeError):
        return False

    _URN_TELEPORT_UNDO_STACK.append(copy.deepcopy(player_data))
    if len(_URN_TELEPORT_UNDO_STACK) > _MAX_URN_TELEPORT_UNDO_SNAPSHOTS:
        del _URN_TELEPORT_UNDO_STACK[:-_MAX_URN_TELEPORT_UNDO_SNAPSHOTS]

    player_data.clear()
    player_data.update(updated)
    gained = _award_skill_exp(skill.exp_key, base_xp)
    level_up_check(skill.display_name, player_data)
    check_achievements(player_data)
    save_player_data()
    try:
        mw.update_undo_actions()
    except AttributeError:
        pass
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    _show_exp(gained)
    return True


def _implemented_exp_keys_snapshot() -> dict[str, float]:
    return {
        skill.exp_key: float(player_data.get(skill.exp_key, 0) or 0)
        for skill in trainable_skill_definitions()
    }


def _show_quest_exp_delta(before: dict[str, float]) -> None:
    total = 0.0
    skill_names = []
    for skill in trainable_skill_definitions():
        old_exp = before.get(skill.exp_key, 0.0)
        try:
            new_exp = float(player_data.get(skill.exp_key, 0) or 0)
        except (TypeError, ValueError):
            new_exp = old_exp
        if new_exp > old_exp:
            total += new_exp - old_exp
            skill_names.append(skill.display_name)
            # Minimal/legacy saves can receive a Combat-stat quest reward before
            # the normal storage migration has seeded that stat's level key.
            player_data.setdefault(skill.level_key, 1)
            level_up_check(skill.display_name, player_data)
    if total > 0:
        _show_exp(_NamedExperience(total, skill_names))


def _show_runtime_exp(value) -> None:
    _show_exp(float(value) if _REVIEW_FEEDBACK_CONTEXT is not None else value)


def _runtime_action_context() -> RuntimeActionContext:
    return RuntimeActionContext(
        player_data=player_data,
        random_random=random.random,
        show_error_message=show_error_message,
        deactivate_current_skill=_deactivate_current_skill,
        award_skill_exp=_award_skill_exp,
        award_hidden_skill_exp=_award_hidden_skill_exp,
        level_up_check=level_up_check,
        check_achievements=check_achievements,
        save_player_data=save_player_data,
        refresh_skill_availability=_refresh_skill_availability,
        show_exp=_show_runtime_exp,
        show_activity_gain=_show_activity_gain,
        implemented_exp_keys_snapshot=_implemented_exp_keys_snapshot,
        show_quest_exp_delta=_show_quest_exp_delta,
        switch_to_bankstanding=_switch_to_bankstanding,
        review_action_multiplier=_review_action_multiplier(),
        cadence_shadow_enabled=False,
        cadence_live_enabled=_cadence_kernel_enabled(),
        prompt_stronghold_reward=_prompt_stronghold_reward,
        prompt_near_death=_prompt_near_death,
        refresh_carried_inventory=_refresh_open_carried_inventory,
    )


def _capture_player_data_snapshot(*, review_answer=False):
    if review_answer:
        before_player_data = dict(player_data)
        # Achievement checks append in place; review handlers replace their other
        # top-level values, so only this small list needs an independent copy.
        if "completed_achievements" in player_data:
            before_player_data["completed_achievements"] = copy.deepcopy(
                player_data["completed_achievements"]
            )
    else:
        before_player_data = copy.deepcopy(player_data)
    return {
        "player_data": before_player_data,
        "current_skill": current_skill,
        "random_state": random.getstate(),
    }


def _remember_review_award_snapshot(before_state) -> None:
    """Keep one complete deterministic transaction snapshot for answer undo."""
    before_player_data = before_state.get("player_data", before_state)
    changed_values = {}
    removed_keys = []
    all_keys = set(before_player_data) | set(player_data)
    for key in all_keys:
        had_before = key in before_player_data
        has_after = key in player_data
        if had_before and (not has_after or before_player_data[key] != player_data[key]):
            changed_values[key] = copy.deepcopy(before_player_data[key])
        elif not had_before and has_after:
            removed_keys.append(key)

    skill_changed = before_state.get("current_skill", current_skill) != current_skill
    random_changed = before_state.get("random_state") != random.getstate()
    if not changed_values and not removed_keys and not skill_changed and not random_changed:
        return

    _REVIEW_UNDO_STACK.append({
        "values": changed_values,
        "remove": removed_keys,
        "current_skill": before_state.get("current_skill", current_skill),
        "random_state": before_state.get("random_state"),
    })
    if len(_REVIEW_UNDO_STACK) > _MAX_REVIEW_UNDO_SNAPSHOTS:
        del _REVIEW_UNDO_STACK[:-_MAX_REVIEW_UNDO_SNAPSHOTS]


def _save_player_data_if_anki_ready() -> None:
    try:
        save_player_data()
    except AttributeError:
        pass


def _normalized_undo_operation(changes) -> str:
    if changes is None:
        return ""
    try:
        return " ".join(str(getattr(changes, "operation", "") or "").lower().split())
    except Exception:
        return ""


def _looks_like_review_undo(changes) -> bool:
    """Match only the Anki answer operation that owns the latest snapshot."""
    return _normalized_undo_operation(changes) in {"answer", "answer card"}


def _looks_like_urn_teleport_undo(changes) -> bool:
    return _normalized_undo_operation(changes) == _URN_TELEPORT_UNDO_OPERATION.lower()


def _looks_like_direct_action_undo(changes) -> bool:
    return _normalized_undo_operation(changes) == _DIRECT_ACTION_UNDO_OPERATION.lower()


def _restore_review_award_snapshot(snapshot) -> None:
    global player_data, current_skill
    for key in snapshot.get("remove", []):
        player_data.pop(key, None)
    for key, value in snapshot.get("values", {}).items():
        player_data[key] = copy.deepcopy(value)
    current_skill = snapshot.get("current_skill", current_skill)
    random_state = snapshot.get("random_state")
    if random_state is not None:
        random.setstate(random_state)

    save_player_data()
    try:
        ui.update_menu_visibility(current_skill)
    except Exception:
        pass
    try:
        update_review_hud(player_data, current_skill)
        update_review_status_badge(
            player_data, _open_activities_sheet, _open_farming_sheet
        )
        update_review_fill_drawer(player_data)
        update_review_event_log_drawer(player_data)
        _update_review_bank_run_surface()
        _update_review_context_surface()
    except Exception:
        pass
    try:
        _refresh_skill_availability()
    except Exception:
        pass


def _restore_urn_teleport_snapshot(snapshot) -> None:
    player_data.clear()
    player_data.update(copy.deepcopy(snapshot))
    save_player_data()
    try:
        update_review_hud(player_data, current_skill)
        update_review_status_badge(
            player_data, _open_activities_sheet, _open_farming_sheet
        )
        update_review_fill_drawer(player_data)
        update_review_event_log_drawer(player_data)
        _update_review_bank_run_surface()
        _update_review_context_surface()
    except Exception:
        pass


def _restore_direct_action_snapshot(snapshot) -> None:
    global current_skill
    player_data.clear()
    player_data.update(copy.deepcopy(snapshot["player_data"]))
    current_skill = snapshot.get("current_skill", current_skill)
    try:
        mw.col.set_config("ankiscape_current_skill", current_skill)
    except (AttributeError, RuntimeError):
        pass
    ui.update_menu_visibility(current_skill)
    random_state = snapshot.get("random_state")
    if random_state is not None:
        random.setstate(random_state)
    save_player_data()
    try:
        update_review_hud(player_data, current_skill)
        update_review_status_badge(
            player_data, _open_activities_sheet, _open_farming_sheet
        )
        update_review_fill_drawer(player_data)
        update_review_event_log_drawer(player_data)
        _update_review_bank_run_surface()
        _update_review_context_surface()
        _refresh_skill_availability()
    except Exception:
        pass


def _on_state_did_undo(changes=None) -> None:
    if _looks_like_direct_action_undo(changes):
        if _DIRECT_ACTION_UNDO_STACK:
            _restore_direct_action_snapshot(_DIRECT_ACTION_UNDO_STACK.pop())
        return
    if _looks_like_urn_teleport_undo(changes):
        if _URN_TELEPORT_UNDO_STACK:
            _restore_urn_teleport_snapshot(_URN_TELEPORT_UNDO_STACK.pop())
        return
    if not _REVIEW_UNDO_STACK or not _looks_like_review_undo(changes):
        return
    snapshot = _REVIEW_UNDO_STACK.pop()
    _restore_review_award_snapshot(snapshot)


def show_skill_selection():
    global current_skill
    selected = ui.show_skill_selection_dialog(current_skill, can_smith_any())
    if selected is None:
        return
    save_skill(selected, None)

def _deactivate_current_skill() -> None:
    """Turn the active skill off (current_skill -> "None").

    This remains the fallback for level, unlock, death, and configuration
    failures. Material exhaustion uses Bankstanding instead so the ordinary
    review-paced market clock keeps moving without repeated warnings.
    """
    global current_skill
    current_skill = "None"
    try:
        ui.update_menu_visibility(current_skill)
    except Exception:
        pass
    try:
        mw.col.set_config("ankiscape_current_skill", current_skill)
    except Exception:
        pass
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


def _switch_to_bankstanding() -> None:
    """Use the settled no-XP fallback after an action exhausts its inputs."""
    global current_skill
    current_skill = UTILITY_REVIEW_ACTION_DISPLAY_NAME
    player_data["current_utility"] = "bankstanding"
    try:
        ui.update_menu_visibility(current_skill)
    except Exception:
        pass
    try:
        mw.col.set_config("ankiscape_current_skill", current_skill)
    except Exception:
        pass
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


def _missing_materials_text(requirements, inventory) -> str:
    """Human-readable list of just the unmet requirements, e.g. "1 Unfired pot"."""
    missing = [
        f"{amount} {material}"
        for material, amount in requirements.items()
        if inventory.get(material, 0) < amount
    ]
    return ", ".join(missing) if missing else "materials"


def _fishing_materials_text(method_spec, inventory) -> str:
    bait_options = tuple(method_spec.get("bait_options") or ())
    if not bait_options:
        return "materials"
    if len(bait_options) == 1:
        bait = bait_options[0]
        return f"1 {bait}"
    return "any of " + ", ".join(f"1 {bait}" for bait in bait_options)


def save_skill(skill, dialog):
    global current_skill
    if skill == "Smithing" and not can_smith_any():
        show_error_message(
            "No Smithing Actions Available",
            "You don't have the level and materials for any Smithing recipe. Mine ore or pick another target first!",
        )
    else:
        current_skill = skill
        ui.update_menu_visibility(current_skill)
        # Persist immediately so the selection survives window close
        try:
            mw.col.set_config("ankiscape_current_skill", current_skill)
        except Exception:
            pass
        # Update the HUD immediately so users see the new skill progress without waiting for XP
        try:
            update_review_hud(player_data, current_skill)
        except Exception:
            pass
        if dialog:
            dialog.accept()

## menu visibility now handled by ui.update_menu_visibility

## show_achievement_dialog provided by ui.py

## show_level_up_dialog provided by ui.py

def show_craft_selection():
    selected = ui.show_craft_selection_dialog(
        current_craft=player_data.get("current_craft", ""),
        crafting_level=player_data.get("crafting_level", 1),
        inventory=player_data.get("inventory", {}),
        CRAFTING_DATA=CRAFTING_DATA,
        CRAFTED_ITEM_IMAGES=CRAFTED_ITEM_IMAGES,
    )
    if selected:
        player_data["current_craft"] = selected
        save_player_data()

def has_crafting_materials(item):
    return has_crafting_materials_pure(item, player_data["inventory"], CRAFTING_DATA)

def on_crafting_answer():
    return runtime_actions.handle_crafting_answer(_runtime_action_context())


def on_utility_answer():
    return runtime_actions.handle_utility_answer(_runtime_action_context())


def on_fletching_answer():
    return runtime_actions.handle_fletching_answer(_runtime_action_context())


def on_firemaking_answer():
    return runtime_actions.handle_firemaking_answer(_runtime_action_context())


def on_fishing_answer():
    return runtime_actions.handle_fishing_answer(_runtime_action_context())


def on_cooking_answer():
    return runtime_actions.handle_cooking_answer(_runtime_action_context())


def on_runecrafting_answer():
    return runtime_actions.handle_runecrafting_answer(_runtime_action_context())


def on_quest_answer():
    return runtime_actions.handle_quest_answer(_runtime_action_context())

def show_bar_selection():
    selected = ui.show_bar_selection_dialog(
        current_bar=player_data.get("current_bar", "Bronze bar"),
        smithing_level=player_data.get("smithing_level", 1),
        BAR_DATA=BAR_DATA,
        BAR_IMAGES=BAR_IMAGES,
    )
    if selected:
        player_data["current_bar"] = selected
        player_data["current_smith"] = _smelt_target_for_bar(selected)
        save_player_data()


def show_tree_selection():
    selected = show_tree_selection_dialog(
        current_tree=player_data.get("current_tree", ""),
        woodcutting_level=player_data.get("woodcutting_level", 1),
        TREE_DATA=TREE_DATA,
        TREE_IMAGES=TREE_IMAGES,
    )
    if selected:
        player_data["current_tree"] = selected
        save_player_data()

def show_ore_selection():
    selected = show_ore_selection_dialog(
        current_ore=player_data.get("current_ore", "Rune essence"),
        mining_level=player_data.get("mining_level", 1),
        ORE_DATA=ORE_DATA,
        ORE_IMAGES=ORE_IMAGES,
    )
    if selected:
        player_data["current_ore"] = selected
        save_player_data()


def _save_livid_farm_direct_action(before, updated, ok, info):
    if not ok:
        return {
            "ok": False,
            "message": str(
                info.get(
                    "message",
                    info.get("reason", "That Livid Farm action is unavailable."),
                )
            )
            .replace("_", " ")
            .capitalize(),
        }
    try:
        mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
    except (AttributeError, RuntimeError):
        return {"ok": False, "message": "Anki could not create an undo entry."}
    _DIRECT_ACTION_UNDO_STACK.append(before)
    if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
        del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
    player_data.clear()
    player_data.update(updated)
    save_player_data()
    _refresh_skill_availability()
    try:
        mw.update_undo_actions()
        update_review_hud(player_data, current_skill)
    except AttributeError:
        pass
    return {"ok": True, **info}


def on_livid_farm_wish(wish_id):
    before = _capture_player_data_snapshot()
    updated, ok, info = apply_livid_farm_wish_pure(
        player_data,
        wish_id,
    )
    return _save_livid_farm_direct_action(before, updated, ok, info)



def _open_farming_sheet(patch_id=None):
    try:
        if ui.focus_main_menu_if_open():
            navigate = ui._MAIN_MENU_CTX.get("open_farming")
            if navigate is not None:
                navigate(patch_id)
            return
    except Exception:
        pass
    _on_main_menu(initial_skill="Farming", initial_farming_patch_id=patch_id)


def _open_activities_sheet(activity_id=None):
    try:
        if ui.focus_main_menu_if_open():
            navigate = ui._MAIN_MENU_CTX.get("open_activity")
            if navigate is not None:
                navigate(activity_id)
            return
    except Exception:
        pass
    _on_main_menu(initial_skill="Activities", initial_activity_id=activity_id)


def _open_grand_exchange_sheet():
    try:
        if ui.focus_main_menu_if_open():
            navigate = ui._MAIN_MENU_CTX.get("open_grand_exchange")
            if navigate is not None:
                navigate()
            return
    except Exception:
        pass
    _on_main_menu(initial_global_tab="Grand Exchange")


def _active_review_bank_run_target(handler_key: str) -> str:
    if handler_key == "combat":
        return str(player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET) or "")
    target_key = runtime_actions._OVERLAY_TARGET_KEYS.get(handler_key)
    return str(player_data.get(target_key, "") or "") if target_key else ""


def on_request_review_bank_run() -> bool:
    """Queue the current activity's existing review-paced bank-run path."""

    handler_key = review_action_handler_key(current_skill)
    target_id = _active_review_bank_run_target(handler_key)
    committed = commit_direct_action(
        lambda data: request_review_bank_run_pure(data, handler_key, target_id)
    )
    _update_review_bank_run_surface()
    return committed


def _update_review_bank_run_surface() -> None:
    handler_key = review_action_handler_key(current_skill)
    update_review_bank_run_button(
        player_data,
        handler_key,
        on_request_review_bank_run,
        target_id=_active_review_bank_run_target(handler_key),
    )


def _on_main_menu(
    initial_skill=None,
    initial_farming_patch_id=None,
    initial_activity_id=None,
    initial_global_tab=None,
):
    def _set_skilling_potion_target(
        skill_id: str, target_id: str, enabled: bool
    ) -> bool:
        table = CRAFTING_DATA if skill_id == "crafting" else (
            FLETCHING_DATA if skill_id == "fletching" else {}
        )
        if target_id not in table:
            return False

        def _change(current):
            updated, ok = set_skilling_potion_target_enabled_pure(
                current, skill_id, target_id, enabled
            )
            if ok and enabled:
                updated[
                    "current_craft"
                    if skill_id == "crafting"
                    else "current_fletch"
                ] = target_id
            return updated, ok

        committed = commit_direct_action(_change)
        if committed:
            _refresh_skill_availability()
            try:
                update_review_hud(player_data, current_skill)
            except Exception:
                pass
        return committed

    def _set_cooking_target(target_id: str) -> bool:
        if target_id not in COOKING_DATA:
            return False

        def _change(current):
            updated = dict(current)
            updated["current_cooking"] = target_id
            updated = reconcile_cooking_equipment_pure(
                updated,
                target_id,
                beneficial=bool(
                    COOKING_DATA[target_id].get("cooking_gauntlet_no_burn_level")
                ),
            )
            return updated, True

        committed = commit_direct_action(_change)
        if committed:
            _refresh_skill_availability()
            try:
                update_review_hud(player_data, current_skill)
            except Exception:
                pass
        return committed

    def _set_cooking_equipment_choice(
        target_id: str, choice: str
    ) -> bool:
        if target_id not in COOKING_DATA:
            return False

        def _change(current):
            updated, ok = set_cooking_equipment_choice_pure(
                current, target_id, choice
            )
            if ok and updated.get("current_cooking") == target_id:
                updated = reconcile_cooking_equipment_pure(
                    updated,
                    target_id,
                    beneficial=bool(
                        COOKING_DATA[target_id].get(
                            "cooking_gauntlet_no_burn_level"
                        )
                    ),
                )
            return updated, ok

        return commit_direct_action(_change)

    def _set_brawling_wilderness_target(
        skill_id: str, target_id: str, enabled: bool
    ) -> bool:
        def _change(current):
            updated = set_brawling_wilderness_target_pure(
                current, skill_id, target_id, enabled
            )
            return updated, updated != current

        return commit_direct_action(_change)

    def _apply_cooking_gauntlets_command(command: str, payload=None):
        body = payload if isinstance(payload, dict) else {}
        result = {"message": "That gauntlet action is unavailable."}

        def _change(current):
            nonlocal result
            if command == "convert":
                updated, ok, message = apply_family_gauntlet_conversion_pure(
                    current, str(body.get("item_name", ""))
                )
            elif command == "recover":
                updated, ok, message = recover_family_gauntlets_pure(current)
            else:
                return dict(current), False
            result = {"message": message}
            return updated, ok

        committed = commit_direct_action(_change)
        if committed:
            _refresh_skill_availability()
        return {"ok": committed, **result}

    def _set_floating_enabled(val: bool):
        try:
            mw.col.set_config("ankiscape_floating_enabled", bool(val))
        except Exception:
            pass
        # Re-inject on current screens for immediate effect
        try:
            _inject_reviewer_floating_button()
            ui.ensure_review_strip()
        except Exception:
            pass
        try:
            _inject_overview_floating_button()
        except Exception:
            pass

    def _set_floating_position(pos: str):
        try:
            if pos not in ("left", "right", "center", "hud-right"):
                pos = "hud-right"
            mw.col.set_config("ankiscape_floating_position", pos)
        except Exception:
            pass
        try:
            _inject_reviewer_floating_button()
        except Exception:
            pass
        try:
            _inject_overview_floating_button()
        except Exception:
            pass

    # Keep/Drop is a gathering choice (power-gather = drop the product for the
    # fastest XP). Resolve it against the currently-selected gathering target.
    _GATHERING_HANDLER_KEYS = {"mining", "woodcutting", "fishing", "hunter"}

    def _current_gathering_target():
        handler_key = review_action_handler_key(current_skill)
        if handler_key not in _GATHERING_HANDLER_KEYS:
            return None
        target_key = runtime_actions._OVERLAY_TARGET_KEYS.get(handler_key)
        target_id = player_data.get(target_key) if target_key else None
        return str(target_id) if target_id else None

    def _current_gathering_keep_drop_state():
        target_id = _current_gathering_target()
        if target_id is None:
            return None
        return (player_data.get("carried_keep_drop") or {}).get(target_id, "keep")

    def _set_carried_keep_drop(drop: bool):
        target_id = _current_gathering_target()
        if target_id is None:
            return
        keep_drop = player_data.get("carried_keep_drop")
        if not isinstance(keep_drop, dict):
            keep_drop = {}
        if drop:
            keep_drop[target_id] = "drop"
        else:
            keep_drop.pop(target_id, None)
        player_data["carried_keep_drop"] = keep_drop
        save_player_data()

    def _current_combat_loot_rows():
        # Advanced per-drop loot control for the enemy currently selected. Each row
        # is {item, mode} where mode is auto/keep/leave from loot_overrides.
        if review_action_handler_key(current_skill) != "combat":
            return ()
        target_id = player_data.get("current_combat_target")
        overrides = player_data.get("loot_overrides") or {}
        rows = []
        for item_name in combat_observed_drop_item_names_pure(player_data, target_id):
            rows.append({"item": item_name, "mode": overrides.get(item_name, "auto")})
        return tuple(rows)

    def _set_loot_override(item_name: str, mode: str):
        overrides = player_data.get("loot_overrides")
        if not isinstance(overrides, dict):
            overrides = {}
        if mode in ("keep", "leave"):
            overrides[item_name] = mode
        else:
            overrides.pop(item_name, None)
        player_data["loot_overrides"] = overrides
        save_player_data()

    # The 4x7 carried-pack grid applies to every skilling target the overlay
    # tracks (gathering AND processing) — a superset of the gathering-only
    # Keep/Drop toggle above.
    def _current_carried_pack_target():
        handler_key = review_action_handler_key(current_skill)
        if handler_key == "combat":
            target_id = player_data.get("current_combat_target")
        elif (
            handler_key == "utility"
            and player_data.get("current_utility")
            in {
                runtime_actions.PYRAMID_PLUNDER_ACTIVITY_ID,
                runtime_actions.GNOME_BALL_ACTIVITY_ID,
                runtime_actions.PHOENIX_LAIR_ACTIVITY_ID,
            }
        ):
            target_id = player_data.get("current_utility")
        else:
            target_key = runtime_actions._OVERLAY_TARGET_KEYS.get(handler_key)
            target_id = player_data.get(target_key) if target_key else None
        return str(target_id) if target_id else None

    def _current_carried_advanced_state():
        target_id = _current_carried_pack_target()
        if target_id is None:
            return False
        return target_id in (player_data.get("carried_advanced_targets") or {})

    def _current_carried_layout_cells():
        # Exactly 28 (item_name_or_None, display_count) cells, slot-accurate
        # (stackables get one cell showing their full count; unstackables get
        # one cell per unit) — pure display math, already capacity-capped.
        target_id = _current_carried_pack_target()
        if target_id is None:
            return tuple((None, 0) for _ in range(inventory_pure.CARRIED_CAPACITY))
        layout = (player_data.get("carried_layout") or {}).get(target_id, {})
        return tuple(
            inventory_pure.layout_to_grid_cells_pure(layout, runtime_actions._OVERLAY_STACKABLE_NAMES)
        )

    def _current_carried_inventory_items():
        target_id = _current_carried_pack_target()
        if target_id is None:
            return ()
        carried = (player_data.get("carried_inventory") or {}).get(target_id, {})
        return tuple(
            (item_name, int(amount))
            for item_name, amount in carried.items()
            if int(amount) > 0
        )

    def _current_carried_auto_summary():
        handler_key = review_action_handler_key(current_skill)
        target_id = _current_carried_pack_target()
        if target_id is None or handler_key == "combat":
            return ""
        current_view = inventory_pure.clamp_carried_view_to_bank(
            (player_data.get("carried_inventory") or {}).get(target_id, {}),
            player_data.get("inventory", {}),
        )
        if handler_key == "agility":
            target = runtime_actions.AGILITY_TARGETS_BY_ID.get(target_id)
            casual_layout = runtime_actions._agility_casual_layout_for(player_data, target_id)
            projected = inventory_pure.apply_carried_layout_pure(
                player_data.get("inventory", {}) or {},
                casual_layout,
                inventory_pure.CARRIED_CAPACITY,
                runtime_actions._OVERLAY_STACKABLE_NAMES,
            )
            view = current_view if target_id in (player_data.get("carried_primed_targets") or {}) else projected
            carried_weight, effective_weight = agility_carried_weight_pure(
                view,
                player_data.get("equipment", {}),
            )
            foods = [
                f"{item_name} x{int(amount)}"
                for item_name, amount in view.items()
                if item_name in runtime_actions.COMBAT_FOOD_DATA and int(amount or 0) > 0
            ]
            missing = runtime_actions._agility_carried_requirement_gaps(
                player_data,
                target_id,
                view,
            )
            target_name = target.display_name if target is not None else target_id
            slots = inventory_pure.carried_slots_used(view, runtime_actions._OVERLAY_STACKABLE_NAMES)
            return (
                f"{target_name} Auto pack · {slots}/{inventory_pure.CARRIED_CAPACITY} slots\n"
                f"Food: {', '.join(foods) if foods else 'none banked'}\n"
                f"Requirements: {'missing ' + ', '.join(missing) if missing else 'ready'}\n"
                f"Weight: {carried_weight:g} kg carried · {effective_weight:g} kg effective"
            )
        slots = inventory_pure.carried_slots_used(
            current_view,
            runtime_actions._OVERLAY_STACKABLE_NAMES,
        )
        return f"{target_id} Auto pack · {slots}/{inventory_pure.CARRIED_CAPACITY} slots"

    def _current_carried_bank_run_summary():
        if review_action_handler_key(current_skill) == "combat":
            return ""
        run = player_data.get("skilling_bank_run", {}) or {}
        remaining = int(run.get("reviews_remaining", 0) or 0) if isinstance(run, dict) else 0
        if remaining > 0:
            route = str(run.get("route_label", "Running to the bank"))
            return f"Bank run: {route} · {remaining} review{'s' if remaining != 1 else ''} remaining"
        return "Bank run: ready"

    def _set_carried_advanced(enabled: bool):
        target_id = _current_carried_pack_target()
        if target_id is None:
            return
        advanced = player_data.get("carried_advanced_targets")
        if not isinstance(advanced, dict):
            advanced = {}
        if enabled:
            advanced[target_id] = True
        else:
            advanced.pop(target_id, None)
        player_data["carried_advanced_targets"] = advanced
        save_player_data()

    def _set_carried_layout_quantity(item_name: str, quantity: int):
        target_id = _current_carried_pack_target()
        if target_id is None:
            return False
        raw_layout = player_data.get("carried_layout")
        layout = dict(raw_layout) if isinstance(raw_layout, dict) else {}
        target_layout, ok = inventory_pure.set_carried_layout_quantity_pure(
            layout.get(target_id, {}),
            item_name,
            quantity,
            runtime_actions._OVERLAY_STACKABLE_NAMES,
        )
        if not ok:
            return False
        if target_layout:
            layout[target_id] = target_layout
        else:
            layout.pop(target_id, None)
        player_data["carried_layout"] = layout
        save_player_data()
        return True

    def _clear_carried_layout():
        target_id = _current_carried_pack_target()
        if target_id is None:
            return
        layout = player_data.get("carried_layout")
        if isinstance(layout, dict):
            layout.pop(target_id, None)
            player_data["carried_layout"] = layout
        save_player_data()

    def _apply_house_result(result):
        updated, ok = result
        if ok:
            player_data.update(updated)
            save_player_data()
        return ok

    def _purchase_house():
        return _apply_house_result(purchase_house_pure(player_data))

    def _purchase_room(room_id):
        return _apply_house_result(purchase_house_option_pure(player_data, room_id, ROOM_DATA, kind="room"))

    def _hire_servant(servant_id):
        if not servant_id:
            player_data["house_servant"] = ""
            save_player_data()
            return True
        return _apply_house_result(purchase_house_option_pure(player_data, servant_id, SERVANT_DATA, kind="servant"))

    def _set_house_style(style_id):
        if style_id == player_data.get("house_style"):
            return True
        return _apply_house_result(purchase_house_option_pure(player_data, style_id, HOUSE_STYLE_DATA, kind="style"))

    def _get_farming_projection():
        return farming_frontend_projection_pure(player_data)

    def _get_ge_projection():
        return ge_frontend_projection_pure(
            player_data,
            item_catalog=GE_ITEM_CATALOG,
        )

    def _apply_ge_action(action_id, payload):
        if action_id == "preview_offer":
            _unchanged, info = apply_ge_frontend_action_pure(
                player_data,
                action_id,
                payload,
                item_catalog=GE_ITEM_CATALOG,
            )
            return {
                **info,
                "projection": _get_ge_projection(),
            }
        result = {}
        accepted = False

        def _change(current):
            nonlocal accepted
            updated, info = apply_ge_frontend_action_pure(
                current,
                action_id,
                payload,
                item_catalog=GE_ITEM_CATALOG,
            )
            result["info"] = info
            accepted = bool(info.get("ok"))
            return updated, accepted

        def _after_apply():
            if action_id in {"place_offer", "collect_offer", "collect_all"}:
                result["bank_run_triggered"] = _trigger_active_bank_run()
                result["info"] = {
                    **result["info"],
                    "bank_run_triggered": result["bank_run_triggered"],
                }
            check_achievements(player_data)
            _refresh_skill_availability()
            try:
                update_review_hud(player_data, current_skill)
            except AttributeError:
                pass

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not accepted:
                # The pure function refused: report its refusal, as before.
                return {
                    **result["info"],
                    "projection": _get_ge_projection(),
                }
            # The change was accepted but no undo entry could be created, so
            # nothing was written and the player must not be told it worked.
            return {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
                "projection": _get_ge_projection(),
            }
        return {
            **result["info"],
            "projection": _get_ge_projection(),
        }

    def _apply_farming_action(action_id, payload):
        change_ok = False
        change_message = ""

        def _change(current):
            nonlocal change_ok, change_message
            updated, change_ok, change_message = apply_farming_frontend_action_pure(
                current, action_id, payload
            )
            return updated, change_ok

        def _after_apply():
            check_achievements(player_data)

        committed = commit_direct_action(_change, after_apply=_after_apply)
        try:
            update_review_status_badge(
                player_data, _open_activities_sheet, _open_farming_sheet
            )
            update_review_fill_drawer(player_data)
        except Exception:
            pass
        if not committed:
            if change_ok:
                # The change applied but Anki refused the undo entry, so nothing
                # was written; never report the successful info here.
                return {
                    "ok": False,
                    "reason": "undo_unavailable",
                    "message": "Anki could not create an undo entry.",
                    "projection": farming_frontend_projection_pure(player_data),
                }
            return {
                "ok": False,
                "message": change_message,
                "projection": farming_frontend_projection_pure(player_data),
            }
        return {
            "ok": True,
            "message": change_message,
            "projection": farming_frontend_projection_pure(player_data),
        }

    def _apply_mage_arena_action(action_id, god_id):
        if action_id == "select_alignment":
            info = {}
            refused = False

            def _change(current):
                nonlocal info, refused
                updated, ok, info = set_mage_arena_alignment_pure(
                    current,
                    god_id,
                )
                refused = not ok
                return updated, ok

            if not commit_direct_action(_change):
                if refused:
                    show_error_message(
                        "Cannot choose alignment",
                        str(info.get("reason", "That alignment is unavailable.")),
                    )
                else:
                    # Main wrote and saved without an undo entry, so this
                    # failure mode only exists since the seam. The choice was
                    # not written; silent loss would leave the player believing
                    # it took.
                    show_error_message(
                        "Alignment unchanged",
                        "Anki could not create an undo entry, so the choice "
                        "was not applied.",
                    )
                return False
            return True
        if action_id != "cape":
            return False

        info = {}
        refused = False

        def _cape_change(current):
            nonlocal info, refused
            updated, ok, info = apply_mage_arena_cape_action_pure(
                current,
                god_id,
            )
            refused = not ok
            return updated, ok

        if not commit_direct_action(_cape_change):
            if refused:
                show_error_message(
                    "Cannot use Mage Arena statue",
                    str(info.get("reason", "That statue action is unavailable.")),
                )
            return False
        _refresh_skill_availability()
        _show_activity_gain(f"Claimed {info.get('cape', 'god cape')}.")
        return True

    def _toggle_dnd_favourite(activity_id):
        """Pin or unpin one Distraction on the reviewer badge, undoably."""
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = toggle_dnd_favourite_pure(current, activity_id)
            return updated, ok

        if not commit_direct_action(_change):
            return {
                "ok": False,
                "message": str(
                    info.get("reason") or "Anki could not create an undo entry."
                ),
                **info,
            }
        _refresh_review_surfaces()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        return {"ok": True, **info}

    def _apply_agility_command(action_id, payload):
        if action_id == "set_activity_auto_stop":
            outcome = {}

            def _apply_safety_toggle(current):
                updated, result = apply_agility_command_pure(
                    current, action_id, payload, roll=0.5
                )
                outcome.update(result)
                return updated, bool(result.get("allowed"))

            committed = commit_direct_action(
                _apply_safety_toggle,
                after_apply=_refresh_skill_availability,
            )
            if committed:
                try:
                    update_review_hud(player_data, current_skill)
                except AttributeError:
                    pass
                _update_review_context_surface()
            return {"ok": committed, **outcome}

        result = {}
        allowed = False

        def _change(current):
            nonlocal result, allowed
            pit_reward = (current.get("agility_activity_state") or {}).get(
                "pit_reward"
            )
            roll = (
                random.random()
                if action_id == "gamble_pit_reward" and pit_reward
                else 0.5
            )
            updated, result = apply_agility_command_pure(
                current, action_id, payload, roll=roll
            )
            allowed = bool(result.get("allowed"))
            return updated, allowed

        def _after_apply():
            xp = float(result.get("xp", 0.0) or 0.0)
            if xp > 0:
                skill_id = str(result.get("skill_id", "agility")).lower()
                skill_name = skill_id.replace("_", " ").title()
                gained = _award_skill_exp(f"{skill_id}_exp", xp)
                level_up_check(skill_name, player_data)
                _show_exp(gained)
            check_achievements(player_data)

        committed = commit_direct_action(_change, after_apply=_after_apply)
        if not committed:
            if not allowed:
                return {"ok": False, **result}
            return {"ok": False, "message": "Anki could not create an undo entry"}
        _refresh_skill_availability()
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        _update_review_context_surface()
        return {"ok": True, **result}

    def _apply_warriors_guild_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        if action_id == "set_policy":
            updated, ok, info = set_warriors_guild_policy_pure(
                player_data,
                automation_mode=str(payload.get("automation_mode", "casual")),
                payment_mode=str(payload.get("payment_mode", "multi")),
                single_token=str(payload.get("single_token", "attack")),
            )
            if not ok:
                return {
                    "ok": False,
                    "message": str(info.get("reason", "That policy is unavailable.")),
                }
            if not commit_direct_action(lambda _current: (updated, True)):
                return {"ok": False, "message": "Could not save the policy."}
            return {"ok": True, **info}

        if action_id not in ("enter_room", "leave_room", "show_defender"):
            return {"ok": False, "message": "Unknown Warriors' Guild command."}

        info = {}
        refused = False

        def _change(current):
            nonlocal info, refused
            if action_id == "enter_room":
                updated, ok, info = enter_warriors_guild_cyclops_room_pure(current)
            elif action_id == "leave_room":
                updated, ok, info = leave_warriors_guild_cyclops_room_pure(current)
            else:
                updated, ok, info = show_warriors_guild_defender_pure(current)
            refused = not ok
            return updated, ok

        if not commit_direct_action(_change):
            if refused:
                return {
                    "ok": False,
                    "message": str(info.get("reason", "That action is unavailable.")),
                }
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_big_chinchompa_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        if action_id == "set_private_ground":
            updated, ok, info = set_hunter_private_ground_pure(
                player_data,
                str(payload.get("target_id", "")),
                bool(payload.get("enabled", False)),
            )
            if not ok:
                return {
                    "ok": False,
                    "message": str(
                        info.get("reason", "That private ground is unavailable.")
                    ),
                }
            if not commit_direct_action(lambda _current: (updated, True)):
                return {
                    "ok": False,
                    "message": "Could not save the private ground.",
                }
            return {"ok": True, **info}
        if action_id != "buy_reward":
            return {
                "ok": False,
                "message": "Unknown Big Chinchompa command.",
            }

        info = {}
        old_hunter_level = int(player_data.get("hunter_level", 1) or 1)

        def _change(current):
            nonlocal info
            updated, ok, info = apply_big_chinchompa_reward_purchase_pure(
                current,
                str(payload.get("reward_id", "")),
                exp_table=EXP_TABLE,
            )
            return updated, ok

        def _after_apply():
            hunter_xp = float(info.get("hunter_xp", 0.0) or 0.0)
            if hunter_xp > 0:
                player_data["hunter_level"] = old_hunter_level
                level_up_check("Hunter", player_data)
                _show_exp(_NamedExperience(hunter_xp, ("Hunter",)))
            check_achievements(player_data)

        if not commit_direct_action(_change, after_apply=_after_apply):
            if info.get("reason"):
                return {
                    "ok": False,
                    "message": str(info.get("reason", "That reward is unavailable.")),
                }
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_shooting_star_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        if action_id != "exchange":
            return {
                "ok": False,
                "message": "Unknown Shooting Star command.",
            }

        info = {}
        pure_ok = False

        def _change(current):
            nonlocal info, pure_ok
            updated, ok, info = apply_shooting_star_exchange_pure(current)
            pure_ok = ok
            return updated, ok

        def _after_apply():
            check_achievements(player_data)

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not pure_ok:
                return {
                    "ok": False,
                    "message": str(
                        info.get("reason", "The Star sprite cannot reward you.")
                    ),
                }
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_fist_of_guthix_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        info = {}
        pure_ok = False

        def _change(current):
            nonlocal info, pure_ok
            updated, ok, info = apply_fist_of_guthix_command_pure(
                current,
                str(action_id),
                payload,
            )
            pure_ok = ok
            return updated, ok

        def _after_apply():
            check_achievements(player_data)

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not pure_ok:
                # The pure function refused: report its own refusal.
                return {
                    "ok": False,
                    "message": str(info.get("reason", "Fist of Guthix action failed.")),
                }
            # The change applied but Anki refused the undo entry, so nothing
            # was written and the player must not be told it worked.
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_sorceress_garden_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        # Preferences used to skip undo registration while still saving, which
        # made the Garden's policy boundary the one mutation here you could not
        # take back. Every action now registers.
        result = {}
        pure_ok = False

        def _change(current):
            nonlocal pure_ok, result
            updated, ok, info = apply_sorceress_garden_command_pure(
                current,
                str(action_id),
                payload,
            )
            pure_ok = bool(ok)
            result = {"ok": pure_ok, "info": info}
            return updated, pure_ok

        def _after_apply():
            _refresh_skill_availability()
            try:
                update_review_hud(player_data, current_skill)
            except AttributeError:
                pass

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not pure_ok:
                # The pure function refused: report its refusal, as before.
                return {
                    "ok": False,
                    "message": str(
                        result["info"].get("reason", "Garden action failed.")
                    ),
                }
            # The change was accepted but no undo entry could be created, so
            # nothing was written and the player must not be told it worked.
            return {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            }
        return {"ok": True, **result["info"]}

    def _apply_penguin_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        exp_before = _implemented_exp_keys_snapshot()

        info = {}
        pure_ok = False

        def _change(current):
            nonlocal info, pure_ok
            updated, ok, info = apply_penguin_command_pure(
                current,
                str(action_id),
                payload,
            )
            pure_ok = ok
            return updated, ok

        def _after_apply():
            if action_id == "redeem_xp":
                skill_name = str(info.get("skill_name", ""))
                if skill_name:
                    level_up_check(skill_name, player_data)
                _show_quest_exp_delta(exp_before)
            check_achievements(player_data)
            _refresh_skill_availability()
            if info.get("message"):
                _show_activity_gain(str(info["message"]))
            try:
                update_review_hud(player_data, current_skill)
            except AttributeError:
                pass

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not pure_ok:
                # The penguin command itself refused: report its refusal.
                return {
                    "ok": False,
                    "message": str(info.get("reason", "Penguin action failed.")),
                }
            # The command was accepted but no undo entry could be created, so
            # nothing was written and the player must not be told it worked.
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        return {"ok": True, **info}

    def _apply_vinesweeper_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        exp_before = _implemented_exp_keys_snapshot()
        updated, ok, info = apply_vinesweeper_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Vinesweeper action failed.")),
                **{
                    key: info[key]
                    for key in ("requires_confirmation", "follower_kind")
                    if key in info
                },
            }
        if not commit_direct_action(lambda _current: (updated, True)):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        if action_id == "redeem_farming_xp":
            level_up_check("Farming", player_data)
            _show_quest_exp_delta(exp_before)
        check_achievements(player_data)
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            # commit_direct_action already refreshed Anki's undo menu.
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_dungeoneering_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        updated, ok, info = apply_dungeoneering_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Dungeoneering action failed.")),
            }
        if not commit_direct_action(lambda _current: (updated, True)):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        check_achievements(player_data)
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_fight_caves_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        result = {}
        accepted = False

        def _change(current):
            nonlocal accepted
            updated, ok, info = apply_fight_caves_command_pure(
                current,
                str(action_id),
                payload,
            )
            result.clear()
            result.update(info)
            accepted = bool(ok)
            return updated, accepted

        def _after_apply():
            check_achievements(player_data)

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not accepted:
                return {
                    "ok": False,
                    "message": str(
                        result.get("reason", "Fight Cave action failed.")
                    ),
                    **{
                        key: result[key]
                        for key in ("requires_confirmation", "follower_kind")
                        if key in result
                    },
                }
            # The change was accepted but no undo entry could be created, so
            # nothing was written and the player must not be told it worked.
            return {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        if result.get("message"):
            _show_activity_gain(str(result["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **result}

    def _apply_dagannoth_kings_command(action_id, payload):
        info = {}
        accepted = False

        def _change(current):
            nonlocal accepted, info
            updated, ok, info = apply_dagannoth_kings_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            accepted = ok
            return updated, ok

        def _after_apply():
            check_achievements(player_data)
            _refresh_skill_availability()
            if info.get("message"):
                _show_activity_gain(str(info["message"]))
            try:
                update_review_hud(player_data, current_skill)
            except AttributeError:
                pass

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not accepted:
                # The pure function refused: report its refusal, as before.
                return {
                    "ok": False,
                    "message": str(
                        info.get("reason", "Dagannoth Kings action failed.")
                    ),
                }
            # Accepted but no undo entry could be created: nothing was written.
            return {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            }
        return {"ok": True, **info}

    def _apply_phoenix_lair_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        info = {}
        pure_ok = False

        def _change(current):
            nonlocal info, pure_ok
            updated, ok, info = apply_phoenix_lair_command_pure(
                current,
                str(action_id),
                payload,
                rng=random.random,
                equipment_data=EQUIPMENT_DATA,
            )
            pure_ok = ok
            return updated, ok

        def _after_apply():
            check_achievements(player_data)

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not pure_ok:
                # The pure function refused: report its refusal, as before.
                return {
                    "ok": False,
                    "message": str(info.get("reason", "Phoenix Lair action failed.")),
                }
            # The change was accepted but no undo entry could be created, so
            # nothing was written and the player must not be told it worked.
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_enchanted_key_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        updated, ok, info = apply_enchanted_key_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Enchanted key action failed.")),
            }
        if not commit_direct_action(lambda _current: (updated, True)):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        check_achievements(player_data)
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_tears_of_guthix_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        updated, ok, info = apply_tears_of_guthix_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Tears of Guthix action failed.")),
            }
        if not commit_direct_action(lambda _current: (updated, True)):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        check_achievements(player_data)
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_skeletal_horror_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        updated, ok, info = apply_skeletal_horror_command_pure(
            player_data,
            str(action_id),
            payload,
            equipment_data=EQUIPMENT_DATA,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Skeletal Horror action failed.")),
            }
        if not commit_direct_action(lambda _current: (updated, True)):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        check_achievements(player_data)
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_bork_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        updated, ok, info = apply_bork_command_pure(
            player_data,
            str(action_id),
            payload,
            equipment_data=EQUIPMENT_DATA,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Bork action failed.")),
            }
        if not commit_direct_action(lambda _current: (updated, True)):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        check_achievements(player_data)
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_barrows_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        result = {}
        accepted = False

        def _change(current):
            nonlocal accepted
            updated, ok, info = apply_barrows_command_pure(
                current,
                str(action_id),
                payload,
                random.random,
            )
            result["info"] = info
            accepted = ok
            return updated, ok

        def _after_apply():
            check_achievements(player_data)
            _refresh_skill_availability()
            if result["info"].get("message"):
                _show_activity_gain(str(result["info"]["message"]))
            try:
                update_review_hud(player_data, current_skill)
            except AttributeError:
                pass

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not accepted:
                # The pure function refused: report its refusal, as before.
                return {
                    "ok": False,
                    "message": str(
                        result.get("info", {}).get(
                            "reason", "Barrows action failed."
                        )
                    ),
                }
            # The change was accepted but no undo entry could be created, so
            # nothing was written and the player must not be told it worked.
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        return {"ok": True, **result["info"]}

    def _apply_stealing_creation_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        result = {}
        accepted = False

        def _change(current):
            nonlocal accepted
            updated, ok, info = apply_stealing_creation_command_pure(
                current,
                str(action_id),
                payload,
                random.random,
            )
            result["info"] = info
            accepted = bool(ok)
            return updated, accepted

        def _after_apply():
            check_achievements(player_data)
            _refresh_skill_availability()
            try:
                update_review_hud(player_data, current_skill)
            except AttributeError:
                pass

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not accepted:
                # The pure function refused: report its refusal, as before.
                info = result["info"]
                return {
                    "ok": False,
                    "message": str(
                        info.get("reason", "Stealing Creation action failed.")
                    ),
                    **{
                        key: info[key]
                        for key in ("requires_confirmation", "follower_kind")
                        if key in info
                    },
                }
            # The change was accepted but no undo entry could be created, so
            # nothing was written and the player must not be told it worked.
            return {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            }
        info = result["info"]
        if info.get("status"):
            _show_activity_gain(str(info["status"]))
        return {"ok": True, **info}

    def _apply_fish_flingers_command(action_id, payload):
        updated, ok, info = apply_fish_flingers_command_pure(
            player_data,
            str(action_id),
            payload if isinstance(payload, dict) else {},
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Fish Flingers action failed.")),
            }
        if not commit_direct_action(lambda _current: (updated, True)):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        check_achievements(player_data)
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            # commit_direct_action already refreshed Anki's undo menu.
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_fishing_trawler_command(action_id, payload):
        accepted = False
        refusal_message = "Fishing Trawler action failed."
        result = {"info": {}}

        def _change(current):
            nonlocal accepted, refusal_message
            updated, ok, info = apply_fishing_trawler_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            accepted = bool(ok)
            if not ok:
                refusal_message = str(
                    info.get("reason", "Fishing Trawler action failed.")
                )
            result["info"] = info
            return updated, accepted

        def _after_apply():
            check_achievements(player_data)
            _refresh_skill_availability()
            if result["info"].get("message"):
                _show_activity_gain(str(result["info"]["message"]))
            try:
                # commit_direct_action already refreshed Anki's undo menu.
                update_review_hud(player_data, current_skill)
            except AttributeError:
                pass

        committed = commit_direct_action(_change, after_apply=_after_apply)
        if not committed:
            if not accepted:
                # The pure function refused: report its refusal, as before.
                return {"ok": False, "message": refusal_message}
            # The change was accepted but no undo entry could be created, so
            # nothing was written; never report the successful info here.
            return {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            }
        return {"ok": True, **result["info"]}

    def _apply_great_orb_project_command(action_id, payload):
        exp_before = _implemented_exp_keys_snapshot()
        info = {}
        pure_ok = False

        def _change(current):
            nonlocal info, pure_ok
            updated, ok, info = apply_great_orb_project_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            pure_ok = ok
            return updated, ok

        def _after_apply():
            if float(info.get("xp", 0.0) or 0.0) > 0:
                level_up_check("Runecrafting", player_data)
                _show_quest_exp_delta(exp_before)
            check_achievements(player_data)

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not pure_ok:
                return {
                    "ok": False,
                    "message": str(
                        info.get("reason", "Great Orb Project action failed.")
                    ),
                }
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_court_cases_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        accepted = False
        result = {}

        def _change(current):
            nonlocal accepted
            updated, ok, info = apply_court_cases_command_pure(
                current,
                str(action_id),
                payload,
            )
            accepted = ok
            result["info"] = info
            return updated, ok

        def _after_apply():
            check_achievements(player_data)
            _refresh_skill_availability()
            if result["info"].get("message"):
                _show_activity_gain(str(result["info"]["message"]))
            try:
                update_review_hud(player_data, current_skill)
            except AttributeError:
                pass

        if not commit_direct_action(_change, after_apply=_after_apply):
            if not accepted:
                # The pure function refused: report its refusal, as before.
                return {
                    "ok": False,
                    "message": str(
                        result["info"].get("reason", "Court Cases action failed.")
                    ),
                }
            # The change was accepted but no undo entry could be created, so
            # nothing was written and the player must not be told it worked.
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        return {"ok": True, **result["info"]}

    def _apply_circus_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_circus_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Big Top Bonanza action failed.")),
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message") and str(action_id) != "set_queue":
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_trouble_brewing_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_trouble_brewing_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Trouble Brewing action failed.")),
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_castle_wars_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_castle_wars_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Castle Wars action failed.")),
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_pest_control_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_pest_control_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Pest Control action failed.")),
                **info,
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_barbarian_assault_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_barbarian_assault_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(
                    info.get("reason", "Barbarian Assault action failed.")
                ),
                **info,
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_varrock_museum_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        before = _capture_player_data_snapshot()
        exp_before = _implemented_exp_keys_snapshot()
        updated, ok, info = apply_varrock_museum_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Museum action failed.")),
                **info,
            }
        if action_id != "set_route":
            try:
                mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
            except (AttributeError, RuntimeError):
                return {
                    "ok": False,
                    "message": "Anki could not create an undo entry.",
                }
            _DIRECT_ACTION_UNDO_STACK.append(before)
            if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
                del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        xp = info.get("xp")
        if isinstance(xp, dict):
            for skill_id in xp:
                skill = get_skill(str(skill_id))
                level_up_check(
                    skill.display_name if skill is not None else str(skill_id),
                    player_data,
                )
            _show_quest_exp_delta(exp_before)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_stronghold_player_safety_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        before = _capture_player_data_snapshot()
        exp_before = _implemented_exp_keys_snapshot()
        updated, ok, info = apply_stronghold_player_safety_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Stronghold action failed.")),
                **info,
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        xp = info.get("xp")
        if isinstance(xp, dict):
            for skill_id in xp:
                skill = get_skill(str(skill_id))
                level_up_check(
                    skill.display_name if skill is not None else str(skill_id),
                    player_data,
                )
            _show_quest_exp_delta(exp_before)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_soul_wars_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_soul_wars_command_pure(
            player_data,
            str(action_id),
            payload,
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Soul Wars action failed.")),
                **info,
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_shades_of_mortton_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_shades_of_mortton_command_pure(
            player_data,
            str(action_id),
            payload,
            rng=random.random,
        )
        if not ok:
            random.setstate(before["random_state"])
            return {
                "ok": False,
                "message": str(info.get("reason", "Mort'ton action failed.")),
                **info,
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            random.setstate(before["random_state"])
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        skill_rows = {
            "crafting": ("crafting_exp", "Crafting"),
            "firemaking": ("firemaking_exp", "Firemaking"),
            "prayer": ("prayer_exp", "Prayer"),
        }
        total_gained = 0.0
        for skill_id, amount in dict(info.get("skill_xp") or {}).items():
            if skill_id not in skill_rows or float(amount or 0.0) <= 0:
                continue
            exp_key, display_name = skill_rows[skill_id]
            total_gained += _award_skill_exp(exp_key, float(amount))
            level_up_check(display_name, player_data)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if total_gained > 0:
            _show_exp(total_gained)
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_treasure_trails_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        updated, ok, info = apply_treasure_trails_command_pure(
            player_data, str(action_id), payload, random.random
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "That Treasure Trails action is unavailable.")),
            }
        if not commit_direct_action(lambda _current: (updated, True)):
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        return {"ok": True, **info}

    def _apply_daily_challenges_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        view = daily_challenges_view_pure(player_data)
        # The Quartermaster values a hand-in at the exchange's live guide price,
        # so the coins in the bag track the market rather than a fixed table.
        credited_items = {
            item_name
            for row in view["rows"]
            for item_name in _daily_challenge_credited_items(row["instance_id"])
        }
        updated, ok, info = apply_daily_challenges_command_pure(
            player_data,
            str(action_id),
            payload,
            ge_guide_prices_pure(player_data, credited_items, GE_ITEM_CATALOG),
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "That Daily Challenge action is unavailable.")),
            }
        if not commit_direct_action(lambda _current: (updated, True)):
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        return {"ok": True, **info}

    def _daily_challenge_credited_items(instance_id):
        for row in player_data.get("daily_challenges", ()) or ():
            if isinstance(row, dict) and str(row.get("instance_id")) == str(instance_id):
                credited = row.get("credited")
                return tuple(credited) if isinstance(credited, dict) else ()
        return ()

    def _apply_tzhaar_fight_pit_command(action_id, payload):
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_tzhaar_fight_pit_command_pure(
            player_data,
            str(action_id),
            payload if isinstance(payload, dict) else {},
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Fight Pit action failed.")),
                **info,
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_achievement_diary_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_achievement_diary_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {"ok": False, "message": str(info["reason"]), **info}
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_duel_arena_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_duel_arena_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {
                    "ok": False,
                    "message": str(info["reason"]),
                    **info,
                }
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_goblin_raids_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_goblin_raids_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {
                    "ok": False,
                    "message": str(info["reason"]),
                    **info,
                }
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_crucible_command(action_id, payload):
        info = {}
        body = dict(payload) if isinstance(payload, dict) else {}
        # The bounty fee is quoted against live guide prices, so the catalog
        # travels with the command rather than being re-derived in the panel.
        if action_id == "enter":
            body.setdefault("price_catalog", GE_ITEM_CATALOG)

        def _change(current):
            nonlocal info
            updated, ok, info = apply_crucible_command_pure(
                current,
                str(action_id),
                body,
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {
                    "ok": False,
                    "message": str(info["reason"]),
                    **info,
                }
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_clan_wars_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_clan_wars_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {
                    "ok": False,
                    "message": str(info["reason"]),
                    **info,
                }
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_conquest_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_conquest_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
                random.random,
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {
                    "ok": False,
                    "message": str(info["reason"]),
                    **info,
                }
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_troll_invasion_command(action_id, payload):
        info = {}
        awarded_xp = 0.0

        def _change(current):
            nonlocal info
            updated, ok, info = apply_troll_invasion_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            return updated, ok

        def _after_apply():
            nonlocal awarded_xp
            skill = get_skill(str(info.get("skill_id", "")))
            rewards = dict(info.get("xp_rewards") or {})
            if skill is None or float(rewards.get(skill.exp_key, 0.0) or 0.0) <= 0:
                return
            awarded_xp = _award_skill_exp(
                skill.exp_key,
                float(rewards[skill.exp_key]),
                action_skill_id=skill.id,
            )
            level_up_check(skill.display_name, player_data)
            info["awarded_xp"] = awarded_xp
            info["message"] = (
                f"Read the Troll Invasion reward book · +{awarded_xp:,.0f} "
                f"{skill.display_name} XP at "
                f"{float(info.get('completion_fraction', 0.0)):.1%} completion."
            )

        if not commit_direct_action(_change, after_apply=_after_apply):
            if info.get("reason"):
                return {"ok": False, "message": str(info["reason"]), **info}
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        if awarded_xp > 0:
            _show_exp(awarded_xp)
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_shattered_heart_command(action_id, payload):
        info = {}
        awarded_xp = 0.0

        def _change(current):
            nonlocal info
            updated, ok, info = apply_shattered_heart_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            return updated, ok

        def _after_apply():
            nonlocal awarded_xp
            for skill_id, amount in dict(info.get("skill_xp") or {}).items():
                skill = get_skill(str(skill_id))
                if skill is None or float(amount or 0.0) <= 0:
                    continue
                awarded_xp += _award_skill_exp(
                    skill.exp_key,
                    float(amount),
                    action_skill_id=skill.id,
                )
                level_up_check(skill.display_name, player_data)
            if awarded_xp > 0:
                info["awarded_xp"] = awarded_xp
            check_achievements(player_data)

        if not commit_direct_action(_change, after_apply=_after_apply):
            if info.get("reason"):
                return {"ok": False, "message": str(info["reason"]), **info}
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        if awarded_xp > 0:
            _show_exp(awarded_xp)
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_mage_training_arena_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_mage_training_arena_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {"ok": False, "message": str(info["reason"]), **info}
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_ranging_guild_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_ranging_guild_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
            )
            return updated, ok

        if not commit_direct_action(
            _change,
            after_apply=lambda: check_achievements(player_data),
        ):
            if info.get("reason"):
                return {"ok": False, "message": str(info["reason"]), **info}
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_dominion_tower_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_dominion_tower_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
                random.random,
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {"ok": False, "message": str(info["reason"]), **info}
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_temple_trekking_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_temple_trekking_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
                random.random,
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {"ok": False, "message": str(info["reason"]), **info}
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_mobilising_armies_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_mobilising_armies_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
                random.random,
                item_values=ITEM_VALUES,
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {"ok": False, "message": str(info["reason"]), **info}
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_gnome_restaurant_command(action_id, payload):
        info = {}

        def _change(current):
            nonlocal info
            updated, ok, info = apply_gnome_restaurant_command_pure(
                current,
                str(action_id),
                payload if isinstance(payload, dict) else {},
                random.random,
            )
            return updated, ok

        if not commit_direct_action(_change):
            if info.get("reason"):
                return {"ok": False, "message": str(info["reason"]), **info}
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_managing_miscellania_command(action_id, payload):
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_managing_miscellania_command_pure(
            player_data,
            str(action_id),
            payload if isinstance(payload, dict) else {},
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "Kingdom action failed.")),
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {
                "ok": False,
                "message": "Anki could not create an undo entry.",
            }
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_livid_farm_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        if action_id == "set_routine":
            updated, ok, info = set_livid_farm_routine_pure(
                player_data,
                payload.get("routine", "complete"),
            )
            if not ok:
                return {
                    "ok": False,
                    "message": str(
                        info.get("reason", "That routine is unavailable.")
                    )
                    .replace("_", " ")
                    .capitalize(),
                }
            if not commit_direct_action(lambda _current: (updated, True)):
                return {"ok": False, "message": "Could not save the routine."}
            return {"ok": True, **info}
        if action_id == "buy_wish":
            return on_livid_farm_wish(payload.get("wish_id", ""))
        before = _capture_player_data_snapshot()
        if action_id == "charge_capacitor":
            updated, ok, info = apply_arcane_capacitor_charge_pure(
                player_data,
                payload.get("spell_id", ""),
            )
        elif action_id == "remove_capacitor_charge":
            updated, ok, info = apply_arcane_capacitor_remove_charge_pure(
                player_data,
            )
        else:
            return {"ok": False, "message": "Unknown Livid Farm command."}
        return _save_livid_farm_direct_action(
            before,
            updated,
            ok,
            info,
        )

    def _apply_summoning_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        info = {}
        if action_id == "summon":
            updated, ok, info = summon_familiar_pure(
                player_data, str(payload.get("familiar_id", ""))
            )
        elif action_id == "dismiss":
            updated, ok, info = dismiss_familiar_pure(player_data)
        elif action_id == "renew":
            updated, ok, info = renew_familiar_pure(player_data)
        elif action_id == "restore_points":
            updated = restore_summoning_points_pure(player_data)
            ok = updated != player_data
        elif action_id == "reclaim_cargo":
            updated, ok, reclaimed = reclaim_familiar_cargo_pure(
                player_data, int(payload.get("event_id", 0) or 0)
            )
            info = {"reclaimed": reclaimed}
        elif action_id == "start_familiarisation":
            updated, ok = start_familiarisation_pure(player_data)
        elif action_id == "claim_familiarisation":
            updated, ok, info = claim_familiarisation_reward_pure(
                player_data, str(payload.get("choice", ""))
            )
        elif action_id == "set_winter_storage_priority":
            updated, ok = set_winter_storage_priority_pure(
                player_data,
                str(payload.get("target_id", "")),
                str(payload.get("item_name", "")),
                payload.get("threshold_free_slots", 0),
            )
        elif action_id == "let_out_pet":
            updated, ok, reason = let_out_pet_pure(
                player_data, str(payload.get("instance_id", ""))
            )
            info = {"reason": reason}
        elif action_id == "store_pet":
            updated, ok = store_active_pet_pure(
                player_data, location=str(payload.get("location", "bank"))
            )
        elif action_id == "release_pet":
            updated, ok, reason = release_pet_pure(
                player_data, str(payload.get("instance_id", ""))
            )
            info = {"reason": reason}
        elif action_id == "hatch_phoenix_egg":
            updated, ok, reason = hatch_phoenix_egg_pure(
                player_data, str(payload.get("item_name", ""))
            )
            info = {"reason": reason, "instance_id": reason if ok else ""}
        else:
            return {"ok": False, "message": "Unknown Summoning command."}
        if not ok:
            reason = str(info.get("reason", "That action is unavailable."))
            return {"ok": False, "message": reason.replace("_", " ").capitalize()}
        before = {
            "player_data": copy.deepcopy(player_data),
            "random_state": random.getstate(),
        }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        summon_xp = float(info.get("summon_xp", 0.0) or 0.0)
        if summon_xp > 0:
            _award_skill_exp("summoning_exp", summon_xp)
            level_up_check("Summoning", player_data)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_wicked_hood_command(action_id, payload):
        payload = dict(payload) if isinstance(payload, dict) else {}
        if action_id == "teleport":
            altar_id = str(payload.get("altar_id", "") or "")
            target_id = next(
                (
                    candidate
                    for candidate, spec in RUNECRAFTING_DATA.items()
                    if spec.get("kind") == "standard"
                    and spec.get("altar_id") == altar_id
                ),
                "",
            )
            quest_reasons = quest_unlock_locked_reasons_pure(
                player_data,
                "runecrafting",
                target_id,
                QUEST_UNLOCK_RULES,
            )
            if quest_reasons:
                payload["locked_reason"] = str(quest_reasons[0])
        before = _capture_player_data_snapshot()
        updated, ok, info = apply_wicked_hood_command_pure(
            player_data, str(action_id), payload
        )
        if not ok:
            return {
                "ok": False,
                "message": str(info.get("reason", "That Wicked hood action is unavailable.")),
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            random.setstate(before["random_state"])
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        if info.get("message"):
            _show_activity_gain(str(info["message"]))
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _apply_slayer_command(action_id, payload):
        payload = payload if isinstance(payload, dict) else {}
        if action_id == "set_combat_filter":
            player_data["slayer_combat_filter"] = bool(
                payload.get("enabled", False)
            )
            save_player_data()
            return {
                "ok": True,
                "combat_filter": player_data["slayer_combat_filter"],
            }
        if action_id != "get_assignment":
            return {"ok": False, "message": "Unknown Slayer command."}

        before = {
            "player_data": copy.deepcopy(player_data),
            "random_state": random.getstate(),
        }
        updated, ok, info = get_slayer_assignment_pure(
            player_data,
            master_id=str(payload.get("master_id", "turael_spria")),
            rng=random.random,
        )
        if not ok:
            random.setstate(before["random_state"])
            return {
                "ok": False,
                "message": str(info.get("reason", "That action is unavailable."))
                .replace("_", " ")
                .capitalize(),
            }
        try:
            mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
        except (AttributeError, RuntimeError):
            random.setstate(before["random_state"])
            return {"ok": False, "message": "Anki could not create an undo entry."}
        _DIRECT_ACTION_UNDO_STACK.append(before)
        if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
            del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
        player_data.clear()
        player_data.update(updated)
        save_player_data()
        _refresh_skill_availability()
        try:
            mw.update_undo_actions()
            update_review_hud(player_data, current_skill)
        except AttributeError:
            pass
        return {"ok": True, **info}

    def _start_grave_walk():
        return commit_direct_action(start_combat_grave_walk_pure)

    ui.show_main_menu(
        player_data,
        current_skill,
        on_save_skill=lambda skill: save_skill(skill, None),
        on_set_ore=lambda ore: _set_value("current_ore", ore),
        on_set_tree=lambda tree: _set_value("current_tree", tree),
        on_set_bar=_set_legacy_bar_target,
        on_set_smith=lambda recipe_id: _set_value("current_smith", recipe_id),
        on_set_craft=lambda item: _set_value("current_craft", item),
        on_set_fletch=lambda target: _set_value("current_fletch", target),
        on_set_skilling_potion_target=_set_skilling_potion_target,
        on_set_firemaking=lambda target: _set_value("current_firemaking", target),
        on_set_fishing=lambda target: _set_value("current_fishing", target),
        on_set_hunter=lambda target: _set_value("current_hunter", target),
        on_set_cooking=_set_cooking_target,
        on_set_cooking_equipment_choice=_set_cooking_equipment_choice,
        on_cooking_gauntlets_command=_apply_cooking_gauntlets_command,
        on_set_brawling_wilderness_target=_set_brawling_wilderness_target,
        on_set_runecrafting=lambda target: _set_value("current_runecrafting", target),
        on_set_herblore=lambda target: _set_value("current_herblore", target),
        on_set_thieving=lambda target: _set_value("current_thieving", target),
        on_set_thieving_fight_back=lambda enabled: _set_value(
            "thieving_fight_back_when_caught", bool(enabled)
        ),
        on_set_agility=lambda target: _set_value("current_agility", target),
        on_set_summoning=lambda target: _set_value(
            "current_summoning", target
        ),
        on_summoning_command=_apply_summoning_command,
        on_wicked_hood_command=_apply_wicked_hood_command,
        on_slayer_command=_apply_slayer_command,
        on_agility_command=_apply_agility_command,
        on_achievement_diary_command=_apply_achievement_diary_command,
        on_warriors_guild_command=_apply_warriors_guild_command,
        on_big_chinchompa_command=_apply_big_chinchompa_command,
        on_shooting_star_command=_apply_shooting_star_command,
        on_fist_of_guthix_command=_apply_fist_of_guthix_command,
        on_sorceress_garden_command=_apply_sorceress_garden_command,
        on_penguin_command=_apply_penguin_command,
        on_vinesweeper_command=_apply_vinesweeper_command,
        on_dungeoneering_command=_apply_dungeoneering_command,
        on_fight_caves_command=_apply_fight_caves_command,
        on_dagannoth_kings_command=_apply_dagannoth_kings_command,
        on_phoenix_lair_command=_apply_phoenix_lair_command,
        on_skeletal_horror_command=_apply_skeletal_horror_command,
        on_bork_command=_apply_bork_command,
        on_tears_of_guthix_command=_apply_tears_of_guthix_command,
        on_enchanted_key_command=_apply_enchanted_key_command,
        on_barrows_command=_apply_barrows_command,
        on_stealing_creation_command=_apply_stealing_creation_command,
        on_fish_flingers_command=_apply_fish_flingers_command,
        on_fishing_trawler_command=_apply_fishing_trawler_command,
        on_great_orb_project_command=_apply_great_orb_project_command,
        on_court_cases_command=_apply_court_cases_command,
        on_circus_command=_apply_circus_command,
        on_trouble_brewing_command=_apply_trouble_brewing_command,
        on_castle_wars_command=_apply_castle_wars_command,
        on_pest_control_command=_apply_pest_control_command,
        on_conquest_command=_apply_conquest_command,
        on_barbarian_assault_command=_apply_barbarian_assault_command,
        on_stronghold_player_safety_command=(
            _apply_stronghold_player_safety_command
        ),
        on_soul_wars_command=_apply_soul_wars_command,
        on_shades_of_mortton_command=_apply_shades_of_mortton_command,
        on_tzhaar_fight_pit_command=_apply_tzhaar_fight_pit_command,
        on_duel_arena_command=_apply_duel_arena_command,
        on_clan_wars_command=_apply_clan_wars_command,
        on_troll_invasion_command=_apply_troll_invasion_command,
        on_shattered_heart_command=_apply_shattered_heart_command,
        on_mage_training_arena_command=_apply_mage_training_arena_command,
        on_ranging_guild_command=_apply_ranging_guild_command,
        on_temple_trekking_command=_apply_temple_trekking_command,
        on_mobilising_armies_command=_apply_mobilising_armies_command,
        on_gnome_restaurant_command=_apply_gnome_restaurant_command,
        on_dominion_tower_command=_apply_dominion_tower_command,
        on_crucible_command=_apply_crucible_command,
        on_goblin_raids_command=_apply_goblin_raids_command,
        on_daily_challenges_command=_apply_daily_challenges_command,
        on_treasure_trails_command=_apply_treasure_trails_command,
        on_varrock_museum_command=_apply_varrock_museum_command,
        on_managing_miscellania_command=_apply_managing_miscellania_command,
        on_livid_farm_command=_apply_livid_farm_command,
        on_set_prayer_selection=set_prayer_selection,
        on_set_magic=lambda target: _set_value("current_magic", target),
        on_set_construction=lambda target: _set_value("current_construction", target),
        on_purchase_house=_purchase_house,
        on_purchase_room=_purchase_room,
        on_hire_servant=_hire_servant,
        on_set_house_style=_set_house_style,
        on_set_magic_alchemy_item=lambda item: _set_value("magic_alchemy_item", item),
        on_set_farming_spell_patch=lambda patch: _set_value("farming_spell_patch", patch),
        on_set_utility=lambda activity: _set_value("current_utility", activity),
        on_start_activity=start_activity_for_reviews,
        on_set_carried_keep_drop=_set_carried_keep_drop,
        carried_keep_drop_state=_current_gathering_keep_drop_state(),
        on_set_loot_threshold=lambda value: _set_value("loot_value_threshold", value),
        on_set_loot_override=_set_loot_override,
        loot_override_rows=_current_combat_loot_rows(),
        carried_pack_target_active=_current_carried_pack_target() is not None,
        active_carried_target_id=_current_carried_pack_target(),
        on_set_carried_advanced=_set_carried_advanced,
        carried_advanced_state=_current_carried_advanced_state(),
        # A callback, not a snapshot: the grid re-reads live player_data after
        # every quantity edit/clear, so it refreshes without rebuilding the dialog.
        get_carried_layout_cells=_current_carried_layout_cells,
        get_carried_inventory_items=_current_carried_inventory_items,
        on_set_carried_layout_quantity=_set_carried_layout_quantity,
        on_clear_carried_layout=_clear_carried_layout,
        carried_stackable_names=runtime_actions._OVERLAY_STACKABLE_NAMES,
        get_carried_auto_summary=_current_carried_auto_summary,
        get_carried_bank_run_summary=_current_carried_bank_run_summary,
        carried_auto_is_combat=review_action_handler_key(current_skill) == "combat",
        on_set_combat=_set_combat_target,
        on_set_combat_action=lambda action: _set_value("combat_action", action),
        on_set_combat_style=_set_combat_attack_style,
        on_set_combat_spell=lambda spell: _set_value("current_combat_spell", spell),
        on_set_combat_auto_eat_threshold=on_set_combat_auto_eat_threshold,
        on_set_combat_pack_mode=on_set_combat_pack_mode,
        on_set_combat_prayer_config=_set_combat_prayer_config,
        on_set_combat_auto_eat_food=on_set_combat_auto_eat_food,
        on_refill_combat_loadout=on_refill_combat_loadout,
        on_unload_combat_loadout=on_unload_combat_loadout,
        on_reclaim_death_office=on_reclaim_death_office,
        on_start_grave_walk=_start_grave_walk,
        on_favourite_dnd=_toggle_dnd_favourite,
        on_set_quest=on_set_quest,
        on_set_quest_route_choice=on_set_quest_route_choice,
        on_claim_reward=on_claim_reward,
        on_claim_stronghold_reward=_claim_stronghold_reward,
        on_mage_arena_action=_apply_mage_arena_action,
        on_set_floating_enabled=_set_floating_enabled,
        on_set_floating_position=_set_floating_position,
        on_attach_tool=on_attach_tool,
        on_equip_item=on_equip_item,
        on_unequip_slot=on_unequip_slot,
        on_discard_item=on_discard_item,
        on_consume_item=on_consume_item,
        on_drink_trouble_brewing_rum=on_drink_trouble_brewing_rum,
        on_use_great_orb_project_teleport_tablet=(
            on_use_great_orb_project_teleport_tablet
        ),
        on_open_item_pack=on_open_item_pack,
        on_open_impling_jar=on_open_impling_jar,
        on_convert_rogue_kit=on_convert_rogue_kit,
        on_teleport_training_urn=teleport_training_urn,
        get_ge_projection=_get_ge_projection,
        on_ge_action=_apply_ge_action,
        get_farming_projection=_get_farming_projection,
        on_farming_action=_apply_farming_action,
        initial_skill=initial_skill,
        initial_farming_patch_id=initial_farming_patch_id,
        initial_activity_id=initial_activity_id,
        initial_global_tab=initial_global_tab,
        on_check_achievements=check_achievements,
        on_save_player_data=save_player_data,
    )


def _smelt_target_for_bar(bar_name: str) -> str:
    for target, spec in SMITHING_DATA.items():
        if spec.get("station") == "furnace" and spec.get("output_item") == bar_name:
            return target
    return DEFAULT_SMITHING_TARGET


def _set_legacy_bar_target(bar_name: str):
    player_data["current_bar"] = bar_name
    _set_value("current_smith", _smelt_target_for_bar(bar_name))


def _set_combat_attack_style(selection):
    """The combat style combo emits a (weapon_style, style_type) pair so the
    orthogonal attack-type field is stored alongside the weapon_style. Set the
    weapon_style directly, then persist+refresh once via the style_type write."""
    weapon_style, style_type = selection
    player_data["combat_attack_style"] = weapon_style
    _set_value("combat_attack_style_type", style_type)


def _set_combat_target(target):
    player_data["combat_action"] = "attack"
    if target not in {"cyclops", "cyclossus"}:
        guild_state = sanitize_warriors_guild_state_pure(
            player_data.get("warriors_guild")
        )
        if guild_state["in_cyclops_room"]:
            guild_state["in_cyclops_room"] = False
            guild_state["cyclossus_pending"] = False
            guild_state["token_drain_residual"] = 0
            player_data["warriors_guild"] = guild_state
    _set_value("current_combat_target", target)


def _set_value(key: str, value):
    player_data[key] = value
    save_player_data()
    # Reflect target/activity changes on the in-review HUD immediately. For XP
    # skills the HUD shows level/progress (so the target swap is not visible
    # there), but for Utilities/Activities the HUD shows the active target name,
    # so switching e.g. "Gather flax" -> "Make soft clay" must update the study
    # screen right away rather than waiting for the next card.
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


def _set_combat_prayer_config(key: str, value):
    if key == "combat_dream_thrift" and bool(value):
        reasons = combat_dream_thrift_locked_reasons_pure(player_data)
        if reasons:
            show_error_message("Dream unavailable", f"Dream requires {reasons[0]}.")
            return False
    if key == "apply_preset":
        new_data, ok = apply_combat_preset_pure(player_data, str(value), player_data.get("current_combat_target"))
        if ok:
            _save_combat_state_update(new_data)
        return ok
    if key == "save_preset":
        new_data, ok = save_combat_preset_pure(player_data, str(value))
        if ok:
            _save_combat_state_update(new_data)
        return ok
    if key == "pin_target_preset":
        target_id = str(player_data.get("current_combat_target", ""))
        pins = dict(player_data.get("combat_target_presets", {}) or {})
        if bool(value):
            pins[target_id] = str(player_data.get("combat_active_preset", "Default"))
        else:
            pins.pop(target_id, None)
        player_data["combat_target_presets"] = pins
        save_player_data()
        return True
    if key == "target_override":
        field, enabled = value
        target_id = str(player_data.get("current_combat_target", ""))
        overrides = dict(player_data.get("combat_target_overrides", {}) or {})
        target_overrides = dict(overrides.get(target_id, {}) or {})
        if enabled:
            current = player_data.get(str(field))
            target_overrides[str(field)] = list(current) if isinstance(current, list) else current
        else:
            target_overrides.pop(str(field), None)
        if target_overrides:
            overrides[target_id] = target_overrides
        else:
            overrides.pop(target_id, None)
        player_data["combat_target_overrides"] = overrides
        save_player_data()
        return True
    player_data[key] = value
    if key == "combat_prayer_book" and value == "curses":
        temple = ((player_data.get("quests", {}) or {}).get("the_temple_at_senntisten") or {})
        if not temple.get("completed"):
            player_data[key] = "standard"
    player_data["combat_selected_prayers"] = list(
        sanitize_prayer_selection_pure(player_data, player_data.get("combat_selected_prayers", ()))
    )
    target_id = str(player_data.get("current_combat_target", ""))
    overrides = player_data.get("combat_target_overrides", {}) or {}
    if isinstance(overrides.get(target_id), dict) and key in overrides[target_id]:
        overrides[target_id][key] = list(player_data[key]) if isinstance(player_data[key], list) else player_data[key]
    save_player_data()
    return True


def _save_combat_state_update(new_data, *, evaluate_achievements=False):
    player_data.update(new_data)
    if evaluate_achievements:
        check_achievements(player_data)
    save_player_data()
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


def on_set_combat_auto_eat_threshold(threshold_percent):
    _save_combat_state_update(set_combat_auto_eat_threshold_pure(player_data, threshold_percent))
    return True


def on_set_combat_pack_mode(mode):
    new_data, ok, reason = set_combat_pack_mode_pure(
        player_data, mode, EQUIPMENT_DATA
    )
    if not ok:
        show_error_message("Cannot change combat supplies", reason)
        return False
    _save_combat_state_update(new_data, evaluate_achievements=True)
    return True


def on_set_combat_auto_eat_food(food_name):
    new_data, ok, reason = set_combat_auto_eat_food_pure(player_data, food_name)
    if not ok:
        show_error_message("Cannot configure food", reason or "Choose a supported combat food.")
        return False
    _save_combat_state_update(new_data)
    return True


def _request_active_bank_run_state(data):
    handler_key = review_action_handler_key(current_skill)
    skill = get_skill(current_skill)
    completes_immediately = False
    if handler_key == "combat" or (skill is not None and skill.id == "slayer"):
        new_data, ok, reason = request_combat_bank_run_now_pure(data)
    elif handler_key in runtime_actions._BANK_RUN_TARGET_KEYS:
        target_key = runtime_actions._BANK_RUN_TARGET_KEYS[handler_key]
        target_id = (data.get(target_key) if target_key else None) or handler_key
        new_data, ok, reason = inventory_pure.request_carried_bank_run_now_pure(
            data, target_id
        )
    elif handler_key is not None or (skill is not None and skill.implemented):
        # Registry-backed surfaces without a review handler are already bank-side.
        new_data = restore_summoning_points_pure(data)
        ok, reason = True, ""
        completes_immediately = True
    else:
        new_data, ok, reason = data, False, "No active target can make a bank run."
    return new_data, ok, reason, completes_immediately


def _trigger_active_bank_run() -> bool:
    new_data, ok, _reason, completes_immediately = _request_active_bank_run_state(
        player_data
    )
    if not ok:
        return False
    player_data.clear()
    player_data.update(new_data)
    if completes_immediately:
        _show_activity_gain("Bank run — arrived and ready")
        _refresh_open_carried_inventory()
    return True


def on_do_bank_run_now():
    """Run or request the active skill/activity's bank visit."""
    new_data, ok, reason, completes_immediately = _request_active_bank_run_state(
        player_data
    )
    if not ok:
        show_error_message("Cannot make a bank run", reason)
        return False
    _save_combat_state_update(new_data)
    if completes_immediately:
        _show_activity_gain("Bank run — arrived and ready")
        _refresh_open_carried_inventory()
    return True


def on_refill_combat_loadout():
    new_data, ok, reason = refill_combat_supply_loadout_pure(player_data, EQUIPMENT_DATA)
    if not ok:
        show_error_message("Cannot refill combat supplies", reason)
        return False
    _save_combat_state_update(new_data)
    return True


def on_unload_combat_loadout():
    new_data, ok, reason = unload_combat_supply_loadout_pure(player_data)
    if not ok:
        show_error_message("Cannot unload combat supplies", reason)
        return False
    _save_combat_state_update(new_data, evaluate_achievements=True)
    return True


def on_reclaim_death_office():
    new_data, ok, reason = reclaim_death_office_items_pure(player_data)
    if not ok:
        show_error_message("Cannot reclaim gear", reason)
        return False
    _save_combat_state_update(new_data, evaluate_achievements=True)
    return True


def on_set_quest(quest_id):
    if quest_id not in QUEST_DATA:
        show_error_message("Unknown quest", "Choose a valid quest before reviewing.")
        return False
    new_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
    if not ok:
        show_error_message("Cannot start quest", "You do not meet this quest's requirements.")
        return False
    player_data.update(new_data)
    save_player_data()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    return True


def on_set_quest_route_choice(quest_id, route_id):
    new_data, ok = apply_quest_route_choice_pure(player_data, quest_id, QUEST_DATA, route_id)
    if not ok:
        show_error_message("Cannot choose quest path", "That path is not available right now.")
        return False
    player_data.update(new_data)
    save_player_data()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    return True


def on_claim_reward(claim_id, selected_skill_id=None):
    before = {"player_data": copy.deepcopy(player_data), "random_state": random.getstate()}
    exp_before = _implemented_exp_keys_snapshot()
    new_data, ok = apply_claim_pure(player_data, claim_id, CLAIM_DATA, selected_skill_id)
    if not ok:
        show_error_message("Cannot claim reward", "That claim is not available right now.")
        return False
    try:
        mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
    except (AttributeError, RuntimeError):
        return False
    _DIRECT_ACTION_UNDO_STACK.append(before)
    if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
        del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
    player_data.clear()
    player_data.update(new_data)
    _show_quest_exp_delta(exp_before)
    check_achievements(player_data)
    save_player_data()
    _refresh_skill_availability()
    try:
        mw.update_undo_actions()
    except AttributeError:
        pass
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    return True


def _claim_stronghold_reward() -> bool:
    """Open the boot-choice dialog and grant the Stronghold reward. Safe to call
    from the hub card or, deferred, when the run completes mid-review."""
    state = player_data.get("stronghold_of_security") or {}
    if not state.get("completed") or state.get("boots_choice") is not None:
        return False
    choice = ui.show_stronghold_reward_dialog()
    if not choice:
        return False
    before = {"player_data": copy.deepcopy(player_data), "random_state": random.getstate()}
    updated = copy.deepcopy(player_data)
    if not grant_stronghold_reward_pure(updated, choice):
        return False
    try:
        mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
    except (AttributeError, RuntimeError):
        return False
    _DIRECT_ACTION_UNDO_STACK.append(before)
    if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
        del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
    player_data.clear()
    player_data.update(updated)
    check_achievements(player_data)
    save_player_data()
    _refresh_skill_availability()
    _show_activity_gain(f"Claimed {choice} and {STRONGHOLD_REWARD_COINS:,} coins from the Stronghold of Security!")
    try:
        mw.update_undo_actions()
    except AttributeError:
        pass
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    return True


def _prompt_near_death(source: str) -> None:
    """Ask whether to leave when a review is refused for near-death with no food.

    Deferred to the event loop for the same reason the Stronghold prompt is: the
    modal must not open inside Anki's answer-card processing. The handler has
    already switched training off, so declining simply leaves the player parked
    where they are.
    """

    try:
        from aqt.qt import QTimer  # type: ignore
    except Exception:
        QTimer = None  # type: ignore

    def _ask() -> None:
        try:
            from aqt.qt import QMessageBox  # type: ignore
        except Exception:
            return
        label = "the activity" if source != "combat" else "combat"
        answer = QMessageBox.question(
            mw,
            "You are about to die",
            f"Lifepoints are critical and there is no food left in your pack or "
            f"your bank.\n\n{label.capitalize()} has been switched off so the "
            f"next review cannot kill you. Walk away from the fight as well?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        # Yes also walks away from the open encounter, so the next session does
        # not resume standing in front of the thing that nearly killed you.
        # Training is already off either way; declining just keeps the fight
        # pending.
        player_data["combat_encounter"] = {}
        _save_player_data_if_anki_ready()
        _refresh_skill_availability()

    if QTimer is not None:
        QTimer.singleShot(0, _ask)
    else:
        _ask()


def _prompt_stronghold_reward() -> None:
    """Fired from the review-answer handler the moment the Stronghold is cleared.
    Deferred to the event loop so the boot-choice modal never pops in the middle
    of Anki's answer-card processing."""
    try:
        from aqt.qt import QTimer  # type: ignore
    except Exception:
        QTimer = None  # type: ignore
    if QTimer is not None:
        QTimer.singleShot(0, _claim_stronghold_reward)
    else:
        _claim_stronghold_reward()


def initialize_menu():
    debug_log("initialize_menu: creating AnkiScape menu")
    ui.create_menu(on_main_menu=_on_main_menu)
    # Refresh Deck Browser so injected content becomes visible after login
    try:
        debug_log("initialize_menu: forcing deck browser refresh")
        _force_deck_browser_refresh()
    except Exception:
        debug_log("initialize_menu: deck browser refresh failed")
        pass


# Main functionality

def on_smithing_answer():
    return runtime_actions.handle_smithing_answer(_runtime_action_context())


def on_woodcutting_answer():
    return runtime_actions.handle_woodcutting_answer(_runtime_action_context())

def on_mining_answer():
    return runtime_actions.handle_mining_answer(_runtime_action_context())


def on_attach_tool(item_name):
    new_inventory, new_toolbelt, attached = attach_tool_to_toolbelt_pure(
        item_name,
        player_data.get("inventory", {}) or {},
        player_data.get("toolbelt", {}) or {},
        MINING_PICKAXE_DATA,
        WOODCUTTING_AXE_DATA,
    )
    if not attached:
        show_error_message(
            "Cannot attach tool",
            f"You need an unattached {item_name} in your Bank.",
        )
        return False
    player_data["inventory"] = new_inventory
    player_data["toolbelt"] = new_toolbelt
    save_player_data()
    return True


def on_equip_item(item_name):
    ok, reason = can_equip_item_pure(item_name, EQUIPMENT_DATA, player_data)
    if not ok:
        show_error_message("Cannot equip item", reason)
        return False
    def _apply(current):
        before_equipment = dict(current.get("equipment", {}) or {})
        new_inventory, new_equipment, equipped = equip_item_pure(
            item_name,
            current.get("inventory", {}) or {},
            current.get("equipment", {}) or {},
            EQUIPMENT_DATA,
        )
        if not equipped:
            return dict(current), False
        updated = dict(current)
        updated["inventory"] = new_inventory
        updated["equipment"] = new_equipment
        updated.update(
            sync_equipment_instances_pure(
                updated, before_equipment, EQUIPMENT_CONDITION_DATA
            )
        )
        return updated, True

    if item_name in FAMILY_GAUNTLET_ITEMS:
        equipped = commit_direct_action(_apply)
    else:
        updated, equipped = _apply(player_data)
        if equipped:
            player_data.clear()
            player_data.update(updated)
            save_player_data()
    if not equipped:
        show_error_message("Cannot equip item", f"You need {item_name} in your bank to equip it.")
    return equipped


def on_unequip_slot(slot):
    item_name = (player_data.get("equipment", {}) or {}).get(slot)

    def _apply(current):
        before_equipment = dict(current.get("equipment", {}) or {})
        new_inventory, new_equipment, unequipped = unequip_item_pure(
            slot,
            current.get("inventory", {}) or {},
            current.get("equipment", {}) or {},
        )
        if not unequipped:
            return dict(current), False
        updated = dict(current)
        updated["inventory"] = new_inventory
        updated["equipment"] = new_equipment
        updated.update(
            sync_equipment_instances_pure(
                updated, before_equipment, EQUIPMENT_CONDITION_DATA
            )
        )
        return updated, True

    if item_name in FAMILY_GAUNTLET_ITEMS:
        unequipped = commit_direct_action(_apply)
    else:
        updated, unequipped = _apply(player_data)
        if unequipped:
            player_data.clear()
            player_data.update(updated)
            save_player_data()
    if not unequipped:
        show_error_message("Cannot unequip item", "That equipment slot is already empty.")
    return unequipped


def on_discard_item(item_name, quantity):
    """Discard an exact Bank quantity as one separately undoable direct action."""
    if is_condition_item_pure(item_name, EQUIPMENT_CONDITION_DATA):
        updated = remove_bank_equipment_instances_pure(
            player_data, item_name, quantity, EQUIPMENT_CONDITION_DATA
        )
        before_count = int((player_data.get("inventory", {}) or {}).get(item_name, 0) or 0)
        after_count = int((updated.get("inventory", {}) or {}).get(item_name, 0) or 0)
        inventory, ok = updated.get("inventory", {}), after_count == before_count - int(quantity)
    else:
        updated = None
        inventory, ok = inventory_pure.discard_inventory_quantity_pure(
            player_data.get("inventory", {}) or {},
            item_name,
            quantity,
        )
    if not ok:
        return False
    before = {"player_data": copy.deepcopy(player_data), "random_state": random.getstate()}
    try:
        mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
    except (AttributeError, RuntimeError):
        return False
    _DIRECT_ACTION_UNDO_STACK.append(before)
    if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
        del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
    if updated is not None:
        player_data.update(updated)
    else:
        player_data["inventory"] = inventory
    save_player_data()
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    try:
        mw.update_undo_actions()
    except AttributeError:
        pass
    return True


def on_consume_item(item_name):
    """Apply one Bank consumable atomically and make the direct action undoable."""
    before = {"player_data": copy.deepcopy(player_data), "random_state": random.getstate()}
    new_data, result = apply_consumable_pure(player_data, item_name, rng=random.random)
    if not result.get("allowed"):
        random.setstate(before["random_state"])
        return None
    try:
        mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
    except (AttributeError, RuntimeError):
        random.setstate(before["random_state"])
        return None
    _DIRECT_ACTION_UNDO_STACK.append(before)
    if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
        del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
    player_data.clear()
    player_data.update(new_data)
    save_player_data()
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    try:
        mw.update_undo_actions()
    except AttributeError:
        pass
    return result


def on_use_great_orb_project_teleport_tablet(item_name):
    """Break one GOP tablet through the shared direct-action undo seam."""
    info = {}

    def _change(data):
        updated, ok, result = use_great_orb_project_teleport_tablet_pure(
            data,
            item_name,
            EQUIPMENT_DATA,
            QUEST_UNLOCK_RULES,
        )
        info.update(result)
        return updated, ok

    if not commit_direct_action(_change):
        show_error_message(
            "Cannot use teleport tablet",
            str(info.get("reason", "That teleport tablet is unavailable.")),
        )
        return None
    message = str(info.get("message", ""))
    if message:
        _show_activity_gain(message)
    return {"ok": True, **info}


def on_drink_trouble_brewing_rum(item_name):
    """Drink one Trouble Brewing rum through the shared direct-action seam."""
    info = {}

    def _change(data):
        updated, ok, result = drink_trouble_brewing_rum_pure(data, item_name)
        info.update(result)
        return updated, ok

    if not commit_direct_action(_change):
        show_error_message(
            "Cannot drink rum",
            str(info.get("reason", "That Trouble Brewing rum is unavailable.")),
        )
        return None
    message = str(info.get("message", ""))
    if message:
        _show_activity_gain(message)
    return {"ok": True, **info}


def on_open_item_pack(item_name, open_all=False):
    result = {}

    def _change(data):
        inventory, outcome = apply_item_pack_open_pure(
            data.get("inventory", {}) or {},
            item_name,
            open_all=bool(open_all),
        )
        result.update(outcome)
        updated = dict(data)
        updated["inventory"] = inventory
        return updated, bool(outcome.get("allowed"))

    if not commit_direct_action(_change):
        return None
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except AttributeError:
        pass
    return result


def on_open_impling_jar(item_name):
    result = {}

    def _change(data):
        inventory, outcome = apply_impling_jar_open_pure(
            data.get("inventory", {}) or {},
            item_name,
            rng=random.random,
        )
        result.update(outcome)
        updated = dict(data)
        updated["inventory"] = inventory
        return updated, bool(outcome.get("allowed"))

    if not commit_direct_action(_change):
        return None
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except AttributeError:
        pass
    return result


def on_convert_rogue_kit(output_item):
    """Convert one Rogue kit into its chosen tool as an undoable Bank action."""
    before = {
        "player_data": copy.deepcopy(player_data),
        "random_state": random.getstate(),
    }
    updated, ok, info = convert_rogue_kit_pure(player_data, str(output_item))
    if not ok:
        return None
    try:
        mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
    except (AttributeError, RuntimeError):
        return None
    _DIRECT_ACTION_UNDO_STACK.append(before)
    if len(_DIRECT_ACTION_UNDO_STACK) > _MAX_DIRECT_ACTION_UNDO_SNAPSHOTS:
        del _DIRECT_ACTION_UNDO_STACK[:-_MAX_DIRECT_ACTION_UNDO_SNAPSHOTS]
    player_data.clear()
    player_data.update(updated)
    save_player_data()
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
        mw.update_undo_actions()
    except AttributeError:
        pass
    return info


def _can_start_current_action() -> bool:
    handler_key = review_action_handler_key(current_skill)
    return runtime_actions.can_start_action(_runtime_action_context(), handler_key)


def _registered_answer_handler(skill):
    handler_key = review_action_handler_key(skill)
    return runtime_actions.answer_handler_for_key(handler_key)


_COMBAT_RECOVERY_STATE_KEYS = (
    "combat_lifepoints",
    "combat_special_attack_energy",
    "combat_current_levels",
    "combat_status_effects",
    "combat_supply_loadout",
    "combat_grave",
)


def _apply_safe_combat_recovery_after_review(save_callback=save_player_data) -> None:
    if not any(key in player_data for key in _COMBAT_RECOVERY_STATE_KEYS):
        return
    before_state = copy.deepcopy(player_data)
    recovered = apply_safe_combat_recovery_pure(player_data, EQUIPMENT_DATA)
    if recovered == before_state:
        return
    player_data.update(recovered)
    save_callback()
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


def _advance_world_events_after_review() -> None:
    """Advance all review-clock world events inside the answer transaction.

    The clocks advance silently, following the Managing Miscellania precedent:
    these events cannot be acted on from the reviewer, and because this runs
    after _finish_review_feedback_context() every message here escaped the
    per-review coalescing and became its own popup. The live state now lives on
    the reviewer D&D badge and the Activities "Live world events" strip.
    """

    spawn_due = evil_tree_spawn_due_pure(player_data)
    updated, _events = advance_evil_tree_world_clock_pure(
        player_data,
        tier_roll=random.random() if spawn_due else 0.0,
        location_roll=random.random() if spawn_due else 0.0,
    )
    player_data.update(updated)

    big_updated, _big_events = advance_big_chinchompa_world_clock_pure(
        player_data
    )
    player_data.update(big_updated)

    star_updated, _star_events = advance_shooting_star_world_clock_pure(
        player_data
    )
    player_data.update(star_updated)

    goblin_due = goblin_raids_spawn_due_pure(player_data)
    goblin_updated, _goblin_events = advance_goblin_raids_world_clock_pure(
        player_data,
        site_roll=random.random() if goblin_due else 0.0,
    )
    player_data.update(goblin_updated)


def on_good_answer(before_state=None, *, defer_commit=False):
    global current_skill, exp_awarded
    if exp_awarded:
        return
    handler = _registered_answer_handler(current_skill)
    has_farm_step = bool(player_data.get("farm_queue"))
    if handler or has_farm_step:
        if before_state is None:
            before_state = _capture_player_data_snapshot()
        handler_key = review_action_handler_key(current_skill)
        review_progressed = False
        review_ctx = _runtime_action_context()
        review_ctx.save_player_data = lambda: None
        _begin_review_feedback_context()
        try:
            if has_farm_step:
                # A consumed or execution-time-invalid Farming step owns this
                # successful review and is never multiplied by skill bonuses.
                review_progressed = runtime_actions.handle_farming_queue_answer(review_ctx)
            elif handler_key == "combat":
                review_progressed = handler(review_ctx) is not False
            else:
                action_ticks = (
                    1
                    if handler_key in {"thieving", "agility", "dungeoneering"}
                    or (
                        handler_key == "utility"
                        and player_data.get("current_utility")
                        in SINGLE_TICK_UTILITY_IDS
                    )
                    or (handler_key == "quest" and _cadence_kernel_enabled())
                    else _review_action_multiplier()
                )
                for tick_index in range(action_ticks):
                    if tick_index > 0 and not _can_start_current_action():
                        break
                    result = runtime_actions.run_answer_with_carried_overlay(
                        review_ctx, handler_key, handler
                    )
                    if result is not False:
                        review_progressed = True
                    if result is False or current_skill == "None":
                        break
                if review_progressed and handler_key not in ("quest", "thieving", "agility"):
                    _apply_safe_combat_recovery_after_review(review_ctx.save_player_data)
        finally:
            _finish_review_feedback_context()
            # The background clock and active action form one persisted review
            # transaction, including rejected handlers and safe recovery.
            _advance_world_events_after_review()
            if not defer_commit:
                _save_player_data_if_anki_ready()
                _remember_review_award_snapshot(before_state)

    exp_awarded = True


## Removed roll_gem wrapper; mining uses apply_mining_pure directly.


def _active_review_carried_target():
    handler_key = review_action_handler_key(current_skill)
    if handler_key == "combat":
        target_id = player_data.get("current_combat_target")
    elif (
        handler_key == "utility"
        and player_data.get("current_utility")
        in {
            runtime_actions.PYRAMID_PLUNDER_ACTIVITY_ID,
            runtime_actions.GNOME_BALL_ACTIVITY_ID,
        }
    ):
        target_id = player_data.get("current_utility")
    else:
        target_key = runtime_actions._OVERLAY_TARGET_KEYS.get(handler_key)
        target_id = player_data.get(target_key) if target_key else None
    return str(target_id) if target_id else None


def on_answer_card(self, ease, _old):
    global card_turned, exp_awarded, answer_shown, _REVIEW_FEEDBACK_INITIAL_XP
    review_answered = card_turned and answer_shown
    successful_answer = ease > 1
    before_state = (
        _capture_player_data_snapshot(review_answer=True) if review_answered else None
    )
    context_xp = (
        _resolve_ignored_review_context_for_answer() if review_answered else 0.0
    )
    had_farm_step = bool(player_data.get("farm_queue"))
    farm_preempted = False
    if review_answered:
        runtime_actions.advance_shared_review_state_for_review(
            _runtime_action_context()
        )
        player_data.update(
            advance_livid_farm_wish_effects_pure(
                player_data,
                1,
            )
        )
        try:
            player_data.update(advance_shop_market_clock_pure(player_data))
            player_data.update(advance_wicked_hood_review_day_pure(player_data))
        except Exception:
            pass
        try:
            challenge_updated, _challenge_events = (
                advance_daily_challenges_day_pure(player_data, random.random)
            )
            player_data.update(challenge_updated)
        except Exception:
            pass
        try:
            miscellania_updated, _miscellania_events = (
                advance_managing_miscellania_world_clock_pure(player_data)
            )
            player_data.update(miscellania_updated)
        except Exception:
            pass
        try:
            ge_updated, ge_events = advance_ge_market_tick_pure(
                player_data,
                item_catalog=GE_ITEM_CATALOG,
            )
            player_data.update(ge_updated)
            if ge_events.get("fills"):
                _trigger_active_bank_run()
        except Exception:
            pass
        try:
            summoning_updated, _summoning_events = (
                advance_summoning_world_tick_pure(
                    player_data,
                    successful_answer=successful_answer,
                    active_carried_target=_active_review_carried_target(),
                )
            )
            player_data.update(summoning_updated)
        except Exception:
            pass
        live_combat = (
            _cadence_kernel_enabled()
            and review_action_handler_key(current_skill) == "combat"
        )
        if successful_answer and not live_combat:
            player_data.update(
                advance_temporary_effects_pure(
                    player_data,
                    _review_action_multiplier(),
                )
            )
        elif (
            not successful_answer
            and _cadence_kernel_enabled()
            and review_action_handler_key(current_skill) == "combat"
        ):
            encounter = player_data.get("combat_encounter", {}) or {}
            if isinstance(encounter, dict) and encounter.get("target_id"):
                player_data["combat_encounter"] = {
                    **encounter,
                    "disengaged": True,
                }
        if successful_answer and had_farm_step:
            _begin_review_feedback_context()
            try:
                farm_preempted = runtime_actions.handle_farming_review_answer(
                    _runtime_action_context()
                )
            finally:
                _finish_review_feedback_context()
        else:
            runtime_actions.advance_farming_clock_for_review(_runtime_action_context())
    if successful_answer and review_answered and not exp_awarded and farm_preempted:
        if context_xp > 0:
            _show_exp(context_xp)
            context_xp = 0.0
        _advance_world_events_after_review()
        exp_awarded = True
    elif successful_answer and review_answered and not exp_awarded and is_review_action(current_skill):
        _REVIEW_FEEDBACK_INITIAL_XP = context_xp
        context_xp = 0.0
        on_good_answer(before_state, defer_commit=True)
        exp_awarded = True
    elif review_answered and before_state is not None:
        activity_state = player_data.get("agility_activity_state") or {}
        if (
            (
                (
                    review_action_handler_key(current_skill) == "utility"
                    and player_data.get("current_utility")
                    == runtime_actions.FLASH_POWDER_FACTORY_ACTIVITY_ID
                )
                or (
                    review_action_handler_key(current_skill) == "agility"
                    and player_data.get("current_agility")
                    == runtime_actions.FLASH_POWDER_FACTORY_ACTIVITY_ID
                )
            )
            and isinstance(activity_state, dict)
            and activity_state.get(
                runtime_actions.FLASH_POWDER_FACTORY_ACTIVITY_ID
            )
        ):
            runtime_actions.handle_flash_powder_factory_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.TROUBLE_BREWING_ACTIVITY_ID
            and runtime_actions.trouble_brewing_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_trouble_brewing_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.CASTLE_WARS_ACTIVITY_ID
            and runtime_actions.castle_wars_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_castle_wars_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.PEST_CONTROL_ACTIVITY_ID
            and runtime_actions.pest_control_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_pest_control_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.BARBARIAN_ASSAULT_ACTIVITY_ID
            and runtime_actions.barbarian_assault_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_barbarian_assault_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.SOUL_WARS_ACTIVITY_ID
            and runtime_actions.soul_wars_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_soul_wars_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.SHADES_OF_MORTTON_ACTIVITY_ID
            and runtime_actions.shades_of_mortton_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_shades_of_mortton_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.CLAN_WARS_ACTIVITY_ID
            and runtime_actions.clan_wars_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_clan_wars_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.TROLL_INVASION_ACTIVITY_ID
            and bool(player_data.get("troll_invasion"))
        ):
            runtime_actions.handle_troll_invasion_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.MAGE_TRAINING_ARENA_ACTIVITY_ID
            and runtime_actions.mage_training_arena_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_mage_training_arena_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.RANGING_GUILD_ACTIVITY_ID
            and runtime_actions.ranging_guild_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_ranging_guild_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.MOBILISING_ARMIES_ACTIVITY_ID
            and runtime_actions.mobilising_armies_can_review_pure(player_data)
        ):
            runtime_actions.handle_mobilising_armies_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.TEMPLE_TREKKING_ACTIVITY_ID
            and runtime_actions.temple_trekking_can_review_pure(player_data)
        ):
            runtime_actions.handle_temple_trekking_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.GNOME_RESTAURANT_ACTIVITY_ID
            and runtime_actions.gnome_restaurant_view_pure(player_data).get("order")
        ):
            runtime_actions.handle_gnome_restaurant_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.CRUCIBLE_ACTIVITY_ID
            and runtime_actions.crucible_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_crucible_answer(
                _runtime_action_context(),
                productive=False,
            )
        elif (
            review_action_handler_key(current_skill) == "utility"
            and player_data.get("current_utility")
            == runtime_actions.GOBLIN_RAIDS_ACTIVITY_ID
            and runtime_actions.goblin_raids_view_pure(player_data).get("active")
        ):
            runtime_actions.handle_goblin_raids_answer(
                _runtime_action_context(),
                productive=False,
            )
        if context_xp > 0:
            _show_exp(context_xp)
            context_xp = 0.0
        _advance_world_events_after_review()
    if context_xp > 0:
        _show_exp(context_xp)
    card_turned = False
    answer_shown = False  # Reset for the next card
    try:
        result = _old(self, ease)
    finally:
        if review_answered and before_state is not None:
            _save_player_data_if_anki_ready()
            _remember_review_award_snapshot(before_state)
    try:
        update_review_status_badge(
            player_data, _open_activities_sheet, _open_farming_sheet
        )
        update_review_fill_drawer(player_data)
        update_review_event_log_drawer(player_data)
        _update_review_bank_run_surface()
    except Exception:
        pass
    _update_review_context_surface()
    return result


def on_card_did_show(card):
    # Flags only. This runs on BOTH the question and answer hooks, so any
    # surface refresh here is duplicate work — _on_rev_show_question and
    # _on_rev_show_answer own the refresh and run after this in each list.
    global card_turned, exp_awarded, answer_shown
    card_turned = True
    exp_awarded = False
    answer_shown = False


def on_show_answer(reviewer):
    global answer_shown
    answer_shown = True


## show_error_message now provided by ui.show_error_message


def can_smith_any():
    return any(
        not smithing_target_locked_reasons_pure(
            player_data, target, SMITHING_DATA, QUEST_UNLOCK_RULES
        )
        for target in SMITHING_DATA
    )


def can_smelt_any_bar():
    """Compatibility name for UI paths that still label Smithing as smelting."""
    return can_smith_any()

def create_soft_clay():
    new_inv, _exp, ok, _processed = apply_utility_activity_pure(
        DEFAULT_UTILITY_ACTIVITY,
        player_data["inventory"],
        UTILITY_ACTIVITY_DATA,
    )
    if ok:
        player_data["inventory"] = new_inv
    return ok

# Removed legacy safe_deduct_from_inventory; use utils.safe_deduct_from_inventory where needed.

# Initialization and hooks
def initialize_exp_popup():
    if not hasattr(mw, "exp_popup"):
        mw.exp_popup = ExpPopup(mw)


# Flexible wrappers to handle version differences in hook signatures
def _refresh_review_surfaces() -> None:
    """The one refresh of every reviewer overlay, per surface event."""
    try:
        from .ui.ui import get_config_bool  # type: ignore
        if get_config_bool("ankiscape_review_hud_enabled", True):
            ensure_review_hud()
            update_review_hud(player_data, current_skill)
        ensure_review_context_action_strip()
        _update_review_context_surface()
        ensure_review_status_badge()
        update_review_status_badge(
            player_data, _open_activities_sheet, _open_farming_sheet
        )
        update_review_fill_drawer(player_data, _open_grand_exchange_sheet)
        update_review_event_log_drawer(player_data)
        _update_review_bank_run_surface()
    except Exception:
        pass

def _on_rev_show_question(*_args, **_kwargs):
    _inject_reviewer_floating_button()
    _refresh_review_surfaces()

def _on_rev_show_answer(*_args, **_kwargs):
    # The injected #ankiscape-float node lives on document.body and survives
    # Anki's per-card innerHTML swap, so injecting once per card is enough.
    _refresh_review_surfaces()

# Ensure the floating button is injected on the deck Overview as it refreshes
def _on_overview_did_refresh(overview):
    try:
        _inject_overview_floating_button(overview)
    except Exception:
        pass
    # Hide HUD off the review screen
    try:
        hide_review_hud()
    except Exception:
        pass

# Centralized hook registration
try:
    from .core import hooks as _hooks
    _hooks.register_hooks(
        {
            "profile_loaded": [
                load_player_data,
                initialize_exp_popup,
                initialize_skill,
                _initialize_debug_from_config,
                migrate_legacy_settings,
                initialize_menu,
                (lambda: _register_deck_browser_button()),
            ],
            # Order matters: on_card_did_show clears answer_shown, so it must
            # stay ahead of on_show_answer, which sets it.
            "reviewer_question": [on_card_did_show, _on_rev_show_question],
            "reviewer_answer": [on_card_did_show, on_show_answer, _on_rev_show_answer],
            "answer_wrapper": on_answer_card,
            "state_did_undo": [_on_state_did_undo],
        }
    )
    # Overview: inject after refresh so the icon is always present on the Study Now screen
    try:
        try:
            gui_hooks.overview_did_refresh.remove(_on_overview_did_refresh)  # type: ignore[attr-defined]
        except Exception:
            pass
        gui_hooks.overview_did_refresh.append(_on_overview_did_refresh)  # type: ignore[attr-defined]
    except Exception:
        # Fallback for environments without overview_did_refresh: defer after will_refresh
        try:
            from aqt.qt import QTimer  # type: ignore
        except Exception:
            QTimer = None  # type: ignore
        def _on_overview_will_refresh(overview):
            if QTimer is not None:
                try:
                    QTimer.singleShot(0, lambda: _inject_overview_floating_button(overview))
                except Exception:
                    pass
            else:
                try:
                    _inject_overview_floating_button(overview)
                except Exception:
                    pass
        try:
            try:
                gui_hooks.overview_will_refresh.remove(_on_overview_will_refresh)  # type: ignore[attr-defined]
            except Exception:
                pass
            gui_hooks.overview_will_refresh.append(_on_overview_will_refresh)  # type: ignore[attr-defined]
        except Exception:
            pass
except Exception:
    # Fallback: in case hooks module import fails, keep behavior by direct registration
    try:
        addHook("profileLoaded", load_player_data)
        addHook("profileLoaded", initialize_exp_popup)
        addHook("profileLoaded", initialize_skill)
        addHook("profileLoaded", migrate_legacy_settings)
        addHook("profileLoaded", initialize_menu)
        addHook("profileLoaded", lambda: _register_deck_browser_button())
    except Exception:
        pass
    try:
        gui_hooks.reviewer_did_show_question.append(on_card_did_show)
        gui_hooks.reviewer_did_show_answer.append(on_card_did_show)
        gui_hooks.reviewer_did_show_answer.append(on_show_answer)
        gui_hooks.reviewer_did_show_question.append(_on_rev_show_question)
        gui_hooks.reviewer_did_show_answer.append(_on_rev_show_answer)
        Reviewer._answerCard = wrap(Reviewer._answerCard, on_answer_card, "around")
        try:
            gui_hooks.state_did_undo.remove(_on_state_did_undo)  # type: ignore[attr-defined]
        except Exception:
            pass
        try:
            gui_hooks.state_did_undo.append(_on_state_did_undo)  # type: ignore[attr-defined]
        except Exception:
            pass
        # Overview: inject after refresh so the icon is always present on the Study Now screen
        try:
            try:
                gui_hooks.overview_did_refresh.remove(_on_overview_did_refresh)  # type: ignore[attr-defined]
            except Exception:
                pass
            gui_hooks.overview_did_refresh.append(_on_overview_did_refresh)  # type: ignore[attr-defined]
        except Exception:
            pass
    except Exception:
        pass

try:
    try:
        gui_hooks.profile_will_close.remove(hide_review_hud)  # type: ignore[attr-defined]
    except Exception:
        pass
    gui_hooks.profile_will_close.append(hide_review_hud)  # type: ignore[attr-defined]
except Exception:
    pass

# Menu is created on profile load via initialize_menu

# --- Deck Browser bottom button integration ---


def _force_deck_browser_refresh():
    """Trigger a Deck Browser rerender so injected content becomes visible immediately."""
    try:
        db = getattr(mw, "deckBrowser", None)
        if db is None:
            debug_log("force_refresh: no deckBrowser present")
            return
        # Prefer refresh when available, otherwise renderPage
        if hasattr(db, "refresh"):
            debug_log("force_refresh: calling deckBrowser.refresh()")
            db.refresh()
        elif hasattr(db, "renderPage"):
            debug_log("force_refresh: calling deckBrowser.renderPage()")
            db.renderPage()
        else:
            debug_log("force_refresh: deckBrowser has no refresh or renderPage")
    except Exception:
        debug_log("force_refresh: failed to refresh")
        pass
