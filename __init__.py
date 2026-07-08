# __init__.py

from .constants import (
    COMBAT_ENEMY_DATA,
    CONSUMABLE_DATA,
    ORE_DATA,
    TREE_DATA,
    BAR_DATA,
    SMITHING_DATA,
    CRAFTING_DATA,
    COOKING_DATA,
    FLETCHING_DATA,
    FIREMAKING_DATA,
    HUNTER_DATA,
    RUNECRAFTING_DATA,
    RUNECRAFTING_POUCH_DATA,
    QUEST_DATA,
    QUEST_UNLOCK_RULES,
    CLAIM_DATA,
    UTILITY_ACTIVITY_DATA,
    DEFAULT_UTILITY_ACTIVITY,
    EXP_TABLE,
    ORE_IMAGES,
    TREE_IMAGES,
    BAR_IMAGES,
    CRAFTED_ITEM_IMAGES,
    EQUIPMENT_DATA,
)
from .smithing_data import DEFAULT_SMITHING_TARGET
from aqt import mw, gui_hooks
from anki.hooks import addHook, wrap
from aqt.reviewer import Reviewer
import copy
import time
import random
import os
import datetime
from .logic_pure import (
    apply_consumable_pure,
    combat_enemy_drop_item_names_pure,
    can_smith_any_pure,
    has_crafting_materials_pure,
    can_craft_item_pure,
    fletching_target_locked_reasons_pure,
    cooking_target_locked_reasons_pure,
    hunter_target_locked_reasons_pure,
    can_runecraft_any_pure,
    start_quest_pure,
    apply_quest_route_choice_pure,
    apply_claim_pure,
    apply_safe_combat_recovery_pure,
    set_combat_auto_eat_threshold_pure,
    set_combat_pack_mode_pure,
    set_combat_auto_eat_food_pure,
    refill_combat_supply_loadout_pure,
    unload_combat_supply_loadout_pure,
    reclaim_death_office_items_pure,
    firemaking_target_locked_reasons_pure,
    apply_utility_activity_pure,
    sanitize_review_action_multiplier,
    can_equip_item_pure,
    equip_item_pure,
    unequip_item_pure,
    calculate_new_level,
)
from .logic import level_up_check, check_achievements
from .ui import (
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
    migrate_legacy_settings,
)
from . import ui
from . import inventory_pure
from .deck_injection_pure import DeckBrowserContent as _DBC, inject_into_deck_browser_content
from .injectors import inject_reviewer_floating_button as _inject_reviewer_floating_button
from .injectors import inject_overview_floating_button as _inject_overview_floating_button
from .injectors import register_deck_browser_button as _register_deck_browser_button
from .injectors import force_deck_browser_refresh as _force_deck_browser_refresh
from .storage import load_player_data as storage_load_player_data, save_player_data as storage_save_player_data
from .action_registry import is_review_action, review_action_handler_key
from .skill_registry import implemented_skill_definitions
from .shop_logic import advance_shop_market_clock_pure
from . import runtime_actions
from .runtime_actions import RuntimeActionContext

global card_turned, exp_awarded, answer_shown

answer_shown = False
card_turned = False
exp_awarded = False

current_skill = "None"

# --- Debug logging (centralized) ---
from .debug import debug_log  # size-rotated, disabled by default unless ANKISCAPE_DEBUG=1
try:
    from .debug import set_debug_enabled as _set_debug_enabled, is_debug_enabled as _is_debug_enabled
except Exception:
    def _set_debug_enabled(_enabled: bool) -> None:
        pass
    def _is_debug_enabled() -> bool:
        return False

# Guard to avoid duplicate registrations
_ANKISCAPE_HOOKS_REGISTERED = False
_LAST_MENU_OPEN_TS = 0.0
_REVIEW_UNDO_STACK = []
_MAX_REVIEW_UNDO_SNAPSHOTS = 50
_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY = "ankiscape_review_action_multiplier"
_LEGACY_XP_MULTIPLIER_CONFIG_KEY = "ankiscape_xp_multiplier"
_REVIEW_FEEDBACK_CONTEXT = None

def show_review_popup():
    ui.show_review_popup()


# Classes moved to ui.py


def save_player_data():
    storage_save_player_data(player_data, current_skill)


def load_player_data():
    global player_data, current_skill
    player_data, current_skill = storage_load_player_data()
    ui.update_menu_visibility(current_skill)

## Removed legacy get_exp_to_next_level stub; use logic_pure.get_exp_to_next_level in tests/pure logic.

# UI functions

def initialize_skill():
    global current_skill
    current_skill = mw.col.get_config("ankiscape_current_skill", default="None")
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
def _show_exp(exp_gained) -> None:
    """Ensure the ExpPopup exists and display exp."""
    try:
        if _REVIEW_FEEDBACK_CONTEXT is not None:
            try:
                _REVIEW_FEEDBACK_CONTEXT["xp"] += float(exp_gained)
            except (TypeError, ValueError):
                pass
            return
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


def _show_activity_gain(text: str) -> None:
    """Floating 'ghost' confirmation for no-XP Utility/Activities (e.g. "+28 Flax").

    Reuses the floating XP popup so utility actions get the same lightweight
    feedback as XP skills, and respects the same floating-notification setting.
    """
    try:
        if _REVIEW_FEEDBACK_CONTEXT is not None:
            _REVIEW_FEEDBACK_CONTEXT["activity"].append(str(text))
            return
        show_popup = True
        try:
            if mw and getattr(mw, "col", None):
                show_popup = bool(mw.col.get_config("ankiscape_floating_xp_enabled", True))
        except Exception:
            show_popup = True
        if show_popup:
            if not hasattr(mw, "exp_popup"):
                mw.exp_popup = ExpPopup(mw)
            mw.exp_popup.show_text(text)
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
    global _REVIEW_FEEDBACK_CONTEXT
    _REVIEW_FEEDBACK_CONTEXT = {"xp": 0.0, "activity": []}


def _finish_review_feedback_context() -> None:
    global _REVIEW_FEEDBACK_CONTEXT
    context = _REVIEW_FEEDBACK_CONTEXT or {"xp": 0.0, "activity": []}
    _REVIEW_FEEDBACK_CONTEXT = None
    xp_total = context.get("xp", 0.0)
    try:
        xp_total = float(xp_total)
    except (TypeError, ValueError):
        xp_total = 0.0
    if xp_total > 0:
        _show_exp(xp_total)
        return
    activity_messages = context.get("activity", [])
    if activity_messages:
        combined = _combine_activity_feedback(activity_messages)
        if combined:
            _show_activity_gain(combined)
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


def _refresh_skill_availability() -> None:
    """Recompute and refresh Smithing/Crafting availability in the menu."""
    try:
        can_craft_any = any(
            can_craft_item_pure(
                player_data.get("crafting_level", 1),
                player_data.get("inventory", {}),
                item_name,
                CRAFTING_DATA,
            )
            for item_name in CRAFTING_DATA.keys()
        )
        can_fletch_any = any(
            not fletching_target_locked_reasons_pure(
                player_data,
                target_key,
                FLETCHING_DATA,
                QUEST_UNLOCK_RULES,
            )
            for target_key in FLETCHING_DATA.keys()
        )
        can_firemake_any = any(
            not firemaking_target_locked_reasons_pure(player_data, target_key, FIREMAKING_DATA, QUEST_UNLOCK_RULES)
            for target_key in FIREMAKING_DATA.keys()
        )
        can_hunt_any = any(
            not hunter_target_locked_reasons_pure(
                player_data,
                target_key,
                HUNTER_DATA,
                QUEST_UNLOCK_RULES,
            )
            for target_key in HUNTER_DATA.keys()
        )
        can_cook_any = any(
            not cooking_target_locked_reasons_pure(
                player_data,
                target_key,
                COOKING_DATA,
                QUEST_UNLOCK_RULES,
            )
            for target_key in COOKING_DATA.keys()
        )
        can_runecraft_any = can_runecraft_any_pure(player_data, RUNECRAFTING_DATA, RUNECRAFTING_POUCH_DATA, QUEST_UNLOCK_RULES)
        refresh_skill_availability(
            can_smith_any(),
            can_craft_any,
            can_fletch_any,
            can_firemake_any,
            can_hunt_any,
            can_cook_any,
            can_runecraft_any,
        )
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


def _award_skill_exp(exp_key: str, base_exp: float) -> float:
    player_data[exp_key] = player_data.get(exp_key, 0) + base_exp
    return base_exp


def _award_hidden_skill_exp(exp_key: str, level_key: str, base_exp: float) -> None:
    if base_exp <= 0:
        return
    player_data[exp_key] = player_data.get(exp_key, 0) + base_exp
    player_data[level_key] = calculate_new_level(
        player_data.get(exp_key, 0),
        player_data.get(level_key, 1),
        EXP_TABLE,
    )


def _implemented_exp_keys_snapshot() -> dict[str, float]:
    return {
        skill.exp_key: float(player_data.get(skill.exp_key, 0) or 0)
        for skill in implemented_skill_definitions()
    }


def _show_quest_exp_delta(before: dict[str, float]) -> None:
    total = 0.0
    for skill in implemented_skill_definitions():
        old_exp = before.get(skill.exp_key, 0.0)
        try:
            new_exp = float(player_data.get(skill.exp_key, 0) or 0)
        except (TypeError, ValueError):
            new_exp = old_exp
        if new_exp > old_exp:
            total += new_exp - old_exp
            level_up_check(skill.display_name, player_data)
    if total > 0:
        _show_exp(total)


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
        refresh_skill_availability_partial=refresh_skill_availability,
        can_smith_any=can_smith_any,
        show_exp=_show_exp,
        show_activity_gain=_show_activity_gain,
        implemented_exp_keys_snapshot=_implemented_exp_keys_snapshot,
        show_quest_exp_delta=_show_quest_exp_delta,
        review_action_multiplier=_review_action_multiplier(),
    )


def _capture_player_data_snapshot():
    return copy.deepcopy(player_data)


def _remember_review_award_snapshot(before_state) -> None:
    """Keep only keys changed by a successful review reward for Anki undo."""
    changed_values = {}
    removed_keys = []
    all_keys = set(before_state) | set(player_data)
    for key in all_keys:
        had_before = key in before_state
        has_after = key in player_data
        if had_before and (not has_after or before_state[key] != player_data[key]):
            changed_values[key] = copy.deepcopy(before_state[key])
        elif not had_before and has_after:
            removed_keys.append(key)

    if not changed_values and not removed_keys:
        return

    _REVIEW_UNDO_STACK.append({"values": changed_values, "remove": removed_keys})
    if len(_REVIEW_UNDO_STACK) > _MAX_REVIEW_UNDO_SNAPSHOTS:
        del _REVIEW_UNDO_STACK[:-_MAX_REVIEW_UNDO_SNAPSHOTS]


def _call_on_good_answer_with_snapshot(before_state) -> None:
    try:
        on_good_answer(before_state)
    except TypeError as exc:
        try:
            on_good_answer()
        except TypeError:
            raise exc


def _save_player_data_if_anki_ready() -> None:
    try:
        save_player_data()
    except AttributeError:
        pass


def _looks_like_review_undo(changes) -> bool:
    """Best-effort guard so unrelated undo events do not consume reward history."""
    if changes is None:
        return True
    try:
        operation = str(getattr(changes, "operation", "") or "").lower()
        if any(token in operation for token in ("answer", "review", "card")):
            return True
    except Exception:
        pass
    try:
        nested_changes = getattr(changes, "changes", None)
        if nested_changes is not None:
            return bool(getattr(nested_changes, "study_queues", False) or getattr(nested_changes, "card", False))
    except Exception:
        pass
    return False


def _restore_review_award_snapshot(snapshot) -> None:
    global player_data
    for key in snapshot.get("remove", []):
        player_data.pop(key, None)
    for key, value in snapshot.get("values", {}).items():
        player_data[key] = copy.deepcopy(value)

    save_player_data()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    try:
        _refresh_skill_availability()
    except Exception:
        pass


def _on_state_did_undo(changes=None) -> None:
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

    Processing skills consume materials, so a target whose materials are
    exhausted would otherwise re-raise the same "out of materials" error on every
    single card. Switching AnkiScape off stops the nag and matches the intended
    flow: the player re-opens the menu and picks another target/activity to
    resume. Persisted + HUD-refreshed so the reviewer reflects the off state.
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



def _on_main_menu():
    def _set_floating_enabled(val: bool):
        try:
            mw.col.set_config("ankiscape_floating_enabled", bool(val))
        except Exception:
            pass
        # Re-inject on current screens for immediate effect
        try:
            _inject_reviewer_floating_button()
        except Exception:
            pass
        try:
            _inject_overview_floating_button()
        except Exception:
            pass

    def _set_floating_position(pos: str):
        try:
            if pos not in ("left", "right"):
                pos = "right"
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
        enemy = COMBAT_ENEMY_DATA.get(target_id) if isinstance(target_id, str) else None
        if not enemy:
            return ()
        overrides = player_data.get("loot_overrides") or {}
        rows = []
        for item_name in combat_enemy_drop_item_names_pure(enemy):
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

    def _add_to_carried_layout(item_name: str, delta: int):
        target_id = _current_carried_pack_target()
        if target_id is None:
            return
        layout = player_data.get("carried_layout")
        if not isinstance(layout, dict):
            layout = {}
        target_layout = dict(layout.get(target_id, {}))
        new_count = max(0, int(target_layout.get(item_name, 0)) + int(delta))
        if new_count > 0:
            target_layout[item_name] = new_count
        else:
            target_layout.pop(item_name, None)
        if target_layout:
            layout[target_id] = target_layout
        else:
            layout.pop(target_id, None)
        player_data["carried_layout"] = layout
        save_player_data()

    def _clear_carried_layout():
        target_id = _current_carried_pack_target()
        if target_id is None:
            return
        layout = player_data.get("carried_layout")
        if isinstance(layout, dict):
            layout.pop(target_id, None)
            player_data["carried_layout"] = layout
        save_player_data()

    ui.show_main_menu(
        player_data,
        current_skill,
        can_smith_any(),
        on_save_skill=lambda skill: save_skill(skill, None),
        on_set_ore=lambda ore: _set_value("current_ore", ore),
        on_set_tree=lambda tree: _set_value("current_tree", tree),
        on_set_bar=_set_legacy_bar_target,
        on_set_smith=lambda recipe_id: _set_value("current_smith", recipe_id),
        on_set_craft=lambda item: _set_value("current_craft", item),
        on_set_fletch=lambda target: _set_value("current_fletch", target),
        on_set_firemaking=lambda target: _set_value("current_firemaking", target),
        on_set_fishing=lambda target: _set_value("current_fishing", target),
        on_set_hunter=lambda target: _set_value("current_hunter", target),
        on_set_cooking=lambda target: _set_value("current_cooking", target),
        on_set_runecrafting=lambda target: _set_value("current_runecrafting", target),
        on_set_utility=lambda activity: _set_value("current_utility", activity),
        on_set_carried_keep_drop=_set_carried_keep_drop,
        carried_keep_drop_state=_current_gathering_keep_drop_state(),
        on_set_loot_threshold=lambda value: _set_value("loot_value_threshold", value),
        on_set_loot_override=_set_loot_override,
        loot_override_rows=_current_combat_loot_rows(),
        carried_pack_target_active=_current_carried_pack_target() is not None,
        on_set_carried_advanced=_set_carried_advanced,
        carried_advanced_state=_current_carried_advanced_state(),
        # A callback, not a snapshot: the grid re-reads live player_data after
        # every add/clear, so it can refresh without rebuilding the whole dialog.
        get_carried_layout_cells=_current_carried_layout_cells,
        on_add_to_carried_layout=_add_to_carried_layout,
        on_clear_carried_layout=_clear_carried_layout,
        on_set_combat=lambda target: _set_value("current_combat_target", target),
        on_set_combat_style=lambda style: _set_value("combat_attack_style", style),
        on_set_combat_spell=lambda spell: _set_value("current_combat_spell", spell),
        on_set_combat_auto_eat_threshold=on_set_combat_auto_eat_threshold,
        on_set_combat_pack_mode=on_set_combat_pack_mode,
        on_set_combat_auto_eat_food=on_set_combat_auto_eat_food,
        on_refill_combat_loadout=on_refill_combat_loadout,
        on_unload_combat_loadout=on_unload_combat_loadout,
        on_reclaim_death_office=on_reclaim_death_office,
        on_set_quest=on_set_quest,
        on_set_quest_route_choice=on_set_quest_route_choice,
        on_claim_reward=on_claim_reward,
        on_set_floating_enabled=_set_floating_enabled,
        on_set_floating_position=_set_floating_position,
        on_equip_item=on_equip_item,
        on_unequip_slot=on_unequip_slot,
        on_discard_item=on_discard_item,
        on_consume_item=on_consume_item,
    )


def _smelt_target_for_bar(bar_name: str) -> str:
    for target, spec in SMITHING_DATA.items():
        if spec.get("station") == "furnace" and spec.get("output_item") == bar_name:
            return target
    return DEFAULT_SMITHING_TARGET


def _set_legacy_bar_target(bar_name: str):
    player_data["current_bar"] = bar_name
    _set_value("current_smith", _smelt_target_for_bar(bar_name))


def _set_value(key: str, value):
    player_data[key] = value
    save_player_data()
    # Reflect target/activity changes on the in-review HUD immediately. For XP
    # skills the HUD shows level/progress (so the target swap is not visible
    # there), but for Utility/Activities the HUD shows the active activity name,
    # so switching e.g. "Gather flax" -> "Make soft clay" must update the study
    # screen right away rather than waiting for the next card.
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


def _save_combat_state_update(new_data):
    player_data.update(new_data)
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
    _save_combat_state_update(set_combat_pack_mode_pure(player_data, mode))
    return True


def on_set_combat_auto_eat_food(food_name):
    new_data, ok, reason = set_combat_auto_eat_food_pure(player_data, food_name)
    if not ok:
        show_error_message("Cannot configure food", reason or "Choose a supported combat food.")
        return False
    _save_combat_state_update(new_data)
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
    _save_combat_state_update(new_data)
    return True


def on_reclaim_death_office():
    new_data, ok, reason = reclaim_death_office_items_pure(player_data)
    if not ok:
        show_error_message("Cannot reclaim gear", reason)
        return False
    _save_combat_state_update(new_data)
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
    new_data, ok = apply_claim_pure(player_data, claim_id, CLAIM_DATA, selected_skill_id)
    if not ok:
        show_error_message("Cannot claim reward", "That claim is not available right now.")
        return False
    player_data.update(new_data)
    check_achievements(player_data)
    save_player_data()
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    return True


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


def on_equip_item(item_name):
    ok, reason = can_equip_item_pure(item_name, EQUIPMENT_DATA, player_data)
    if not ok:
        show_error_message("Cannot equip item", reason)
        return False
    new_inventory, new_equipment, equipped = equip_item_pure(
        item_name,
        player_data.get("inventory", {}) or {},
        player_data.get("equipment", {}) or {},
        EQUIPMENT_DATA,
    )
    if not equipped:
        show_error_message("Cannot equip item", f"You need {item_name} in your bank to equip it.")
        return False
    player_data["inventory"] = new_inventory
    player_data["equipment"] = new_equipment
    save_player_data()
    return True


def on_unequip_slot(slot):
    new_inventory, new_equipment, unequipped = unequip_item_pure(
        slot,
        player_data.get("inventory", {}) or {},
        player_data.get("equipment", {}) or {},
    )
    if not unequipped:
        show_error_message("Cannot unequip item", "That equipment slot is already empty.")
        return False
    player_data["inventory"] = new_inventory
    player_data["equipment"] = new_equipment
    save_player_data()
    return True


def on_discard_item(item_name):
    inventory = dict(player_data.get("inventory", {}) or {})
    if int(inventory.get(item_name, 0) or 0) <= 0:
        return False
    inventory[item_name] = 0
    player_data["inventory"] = inventory
    save_player_data()
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    return True


def on_consume_item(item_name):
    """Eat/drink a stat-affecting consumable from the Bank (Kebab, Beer).
    Direct player action like discard: applies the source effect, saves, and
    returns the result dict (or None when nothing was consumed)."""
    new_data, result = apply_consumable_pure(player_data, item_name)
    if not result.get("allowed"):
        return None
    player_data.clear()
    player_data.update(new_data)
    save_player_data()
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass
    return result


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


def _apply_safe_combat_recovery_after_review() -> None:
    if not any(key in player_data for key in _COMBAT_RECOVERY_STATE_KEYS):
        return
    before_state = copy.deepcopy(player_data)
    recovered = apply_safe_combat_recovery_pure(player_data, EQUIPMENT_DATA)
    if recovered == before_state:
        return
    player_data.update(recovered)
    save_player_data()
    _refresh_skill_availability()
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


def on_good_answer(before_state=None):
    global current_skill, exp_awarded
    if exp_awarded:
        return
    handler = _registered_answer_handler(current_skill)
    if handler:
        if before_state is None:
            before_state = _capture_player_data_snapshot()
        handler_key = review_action_handler_key(current_skill)
        review_progressed = False
        _begin_review_feedback_context()
        try:
            if handler_key == "combat":
                review_progressed = handler(_runtime_action_context()) is not False
            else:
                for tick_index in range(_review_action_multiplier()):
                    if tick_index > 0 and not _can_start_current_action():
                        break
                    result = runtime_actions.run_answer_with_carried_overlay(
                        _runtime_action_context(), handler_key, handler
                    )
                    if result is not False:
                        review_progressed = True
                    if result is False or current_skill == "None":
                        break
                if review_progressed and handler_key not in ("quest",):
                    _apply_safe_combat_recovery_after_review()
        finally:
            _finish_review_feedback_context()
            _remember_review_award_snapshot(before_state)

    exp_awarded = True


## Removed roll_gem wrapper; mining uses apply_mining_pure directly.


def on_answer_card(self, ease, _old):
    global card_turned, exp_awarded, answer_shown
    review_answered = card_turned and answer_shown
    before_state = _capture_player_data_snapshot() if review_answered else None
    if review_answered:
        try:
            player_data.update(advance_shop_market_clock_pure(player_data))
        except Exception:
            pass
    if ease > 1 and is_review_action(current_skill) and review_answered and not exp_awarded:
        _call_on_good_answer_with_snapshot(before_state)
        exp_awarded = True
    elif review_answered and before_state is not None:
        _save_player_data_if_anki_ready()
        _remember_review_award_snapshot(before_state)
    card_turned = False
    answer_shown = False  # Reset for the next card
    return _old(self, ease)


def on_card_did_show(card):
    global card_turned, exp_awarded, answer_shown
    card_turned = True
    exp_awarded = False
    answer_shown = False
    # Ensure/update HUD when a review card is shown
    try:
        ensure_review_hud()
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


def on_show_answer(reviewer):
    global answer_shown
    answer_shown = True
    # Keep HUD in sync when flipping
    try:
        update_review_hud(player_data, current_skill)
    except Exception:
        pass


## show_error_message now provided by ui.show_error_message


def can_smith_any():
    return can_smith_any_pure(player_data["inventory"], player_data["smithing_level"], SMITHING_DATA)


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
    mw.exp_popup = ExpPopup(mw)


# Flexible wrappers to handle version differences in hook signatures
def _on_rev_show_question(*_args, **_kwargs):
    _inject_reviewer_floating_button()
    try:
        from .ui import get_config_bool  # type: ignore
        if get_config_bool("ankiscape_review_hud_enabled", True):
            ensure_review_hud()
            update_review_hud(player_data, current_skill)
    except Exception:
        pass

def _on_rev_show_answer(*_args, **_kwargs):
    _inject_reviewer_floating_button()
    try:
        from .ui import get_config_bool  # type: ignore
        if get_config_bool("ankiscape_review_hud_enabled", True):
            ensure_review_hud()
            update_review_hud(player_data, current_skill)
    except Exception:
        pass

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
    from . import hooks as _hooks
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

# Menu is created on profile load via initialize_menu

    # --- Handle JS bridge messages from injected buttons ---
    def _on_js_message(handled, message, context):  # type: ignore[no-redef]
        """Respond to messages sent via pycmd() in injected JS."""
        try:
            if isinstance(message, str):
                if message == "ankiscape_open_menu":
                    debug_log("bridge: ankiscape_open_menu received")
                    global _LAST_MENU_OPEN_TS
                    now = time.time()
                    if is_main_menu_open():
                        debug_log("bridge: menu already open; focusing")
                        try:
                            focus_main_menu_if_open()
                        except Exception:
                            pass
                    elif now - _LAST_MENU_OPEN_TS > 0.4:  # debounce
                        _LAST_MENU_OPEN_TS = now
                        debug_log("bridge: opening main menu via _on_main_menu")
                        try:
                            try:
                                from aqt.qt import QTimer  # type: ignore
                            except Exception:
                                QTimer = None  # type: ignore
                            if QTimer is not None:
                                QTimer.singleShot(0, _on_main_menu)
                                debug_log("bridge: scheduled _on_main_menu with QTimer")
                            else:
                                _on_main_menu()
                                debug_log("bridge: called _on_main_menu directly (no QTimer)")
                        except Exception:
                            debug_log("bridge: _on_main_menu raised; swallowed")
                            pass
                    return (True, message)
                if message.startswith("ankiscape_log:"):
                    try:
                        debug_log(f"js: {message[len('ankiscape_log:'):]}")
                    except Exception:
                        pass
                    # Not handled; allow default processing to continue
                    return (handled, message)
                # Hardening: do not intercept native Anki navigation messages
                try:
                    low = message.lower()
                except Exception:
                    low = ""
                if (
                    low.startswith("open:")
                    or low in ("decks", "add", "browse", "stats", "sync")
                    or low == "study" or low == "review" or low == "start"
                    or low.startswith("study") or low.startswith("review") or low.startswith("start")
                    or low in ("preview", "previewer", "card-info", "addcards")
                ):
                    return (False, message)
        except Exception:
            debug_log("bridge: exception in _on_js_message")
            pass
        # Default: do not intercept messages we don't recognize
        try:
            if isinstance(message, str):
                return (False, message)
        except Exception:
            pass
        return (handled, message)

    # Note: JS bridge hook is registered in injectors.register_deck_browser_button
    # to keep one consistent handler and predictable order.

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
