# __init__.py

from .constants import (
    ORE_DATA,
    TREE_DATA,
    BAR_DATA,
    SMITHING_DATA,
    GEM_DATA,
    CRAFTING_DATA,
    FLETCHING_DATA,
    UTILITY_ACTIVITY_DATA,
    DEFAULT_UTILITY_ACTIVITY,
    DEFAULT_MINING_TARGET,
    DEFAULT_WOODCUTTING_TARGET,
    MINING_PICKAXE_DATA,
    MINING_BONUS_ITEM_DATA,
    INCIDENTAL_GEM_DROP_CHANCE,
    INCIDENTAL_GEM_DROP_TABLE,
    GLORY_GEM_DROP_CHANCE,
    WOODCUTTING_AXE_DATA,
    BIRD_NEST_DROP_CHANCE,
    BIRD_NEST_DROP_TABLE,
    BIRD_NEST_OPEN_TABLES,
    ORE_IMAGES,
    TREE_IMAGES,
    BAR_IMAGES,
    GEM_IMAGES,
    CRAFTED_ITEM_IMAGES,
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
    calculate_probability_with_level,
    pick_gem,
    can_smith_any_pure,
    can_smith_item_pure,
    create_soft_clay_pure,
    has_crafting_materials_pure,
    can_craft_item_pure,
    can_fletch_item_pure,
    can_perform_utility_activity_pure,
    apply_crafting_pure,
    apply_utility_activity_pure,
    apply_open_bird_nests_pure,
    apply_smithing_pure,
    apply_fletching_pure,
    apply_woodcutting_action_pure,
    apply_mining_action_pure,
    sanitize_review_action_multiplier,
    can_mine_ore_pure,
    can_cut_tree_pure,
    best_woodcutting_axe_pure,
    best_mining_pickaxe_pure,
    mining_bonus_state_pure,
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
from .deck_injection_pure import DeckBrowserContent as _DBC, inject_into_deck_browser_content
from .injectors import inject_reviewer_floating_button as _inject_reviewer_floating_button
from .injectors import inject_overview_floating_button as _inject_overview_floating_button
from .injectors import register_deck_browser_button as _register_deck_browser_button
from .injectors import force_deck_browser_refresh as _force_deck_browser_refresh
from .storage import load_player_data as storage_load_player_data, save_player_data as storage_save_player_data
from .skill_registry import is_review_skill, review_handler_key

global card_turned, exp_awarded, answer_shown

answer_shown = False
card_turned = False
exp_awarded = False

current_skill = "None"
_UTILITY_SKILL_NAMES = {"Utility", "Utility / Activities"}

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
        inventory = player_data.get("inventory", {})
        can_craft_any = any(
            can_craft_item_pure(
                player_data.get("crafting_level", 1),
                inventory,
                item_name,
                CRAFTING_DATA,
            )
            for item_name in CRAFTING_DATA.keys()
        )
        can_fletch_any = any(
            can_fletch_item_pure(
                player_data.get("fletching_level", 1),
                inventory,
                target_key,
                FLETCHING_DATA,
            )
            for target_key in FLETCHING_DATA.keys()
        )
        refresh_skill_availability(can_smith_any(), can_craft_any, can_fletch_any)
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
    item = player_data.get("current_craft", "")
    spec = CRAFTING_DATA.get(item)
    if not spec:
        show_error_message("Unknown crafting target", "Choose a valid Crafting target before reviewing.")
        return False

    player_level = player_data.get("crafting_level", 1)
    if player_level < spec["level"]:
        show_error_message("Insufficient level", f"You need level {spec['level']} Crafting to make {item}.")
        return False

    # Check level and material requirements first. Name the *specific* missing
    # material (e.g. "Pot" needs an "Unfired pot", not Soft clay directly) so the
    # player understands the pottery/processing chain instead of seeing a generic
    # "not enough materials" that contradicts a full bank of the wrong item.
    if not has_crafting_materials(item):
        missing = _missing_materials_text(spec.get("requirements", {}), player_data["inventory"])
        _deactivate_current_skill()
        show_error_message(
            "Out of materials",
            f"You need {missing} to craft {item}, so Crafting has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    # Apply crafting via pure function (handles Soft clay and crafted items)
    new_inv, base_exp, ok = apply_crafting_pure(item, player_data["inventory"], CRAFTING_DATA)
    if not ok:
        missing = _missing_materials_text(spec.get("requirements", {}), player_data["inventory"])
        _deactivate_current_skill()
        show_error_message(
            "Out of materials",
            f"You need {missing} to craft {item}, so Crafting has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    # Update player data and UI
    player_data["inventory"] = new_inv
    exp_gained = _award_skill_exp("crafting_exp", base_exp)
    level_up_check("Crafting", player_data)
    check_achievements(player_data)
    save_player_data()

    # Refresh availability for Crafting/Smithing in the open menu (enables, never auto-selects)
    try:
        can_craft_any = any(
            can_craft_item_pure(player_data.get("crafting_level", 1), player_data.get("inventory", {}), item_name, CRAFTING_DATA)
            for item_name in CRAFTING_DATA.keys()
        )
        refresh_skill_availability(can_smith_any(), can_craft_any)
    except Exception:
        pass

    _refresh_skill_availability()
    _show_exp(exp_gained)
    return True


def on_utility_answer():
    activity_key = player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
    if activity_key not in UTILITY_ACTIVITY_DATA:
        activity_key = DEFAULT_UTILITY_ACTIVITY
        player_data["current_utility"] = activity_key
    spec = UTILITY_ACTIVITY_DATA[activity_key]
    display_name = spec.get("display_name", activity_key)

    if not can_perform_utility_activity_pure(player_data.get("inventory", {}), activity_key, UTILITY_ACTIVITY_DATA):
        requirements = spec.get("requirements", {})
        # Out of materials: switch the activity off so it stops firing this error
        # on every card, and point the player back to the menu to pick another.
        _deactivate_current_skill()
        if requirements:
            missing = _missing_materials_text(requirements, player_data.get("inventory", {}))
            show_error_message(
                "Out of materials",
                f"You're out of {missing} for {display_name}, so it's been switched off. "
                "Open the AnkiScape menu to pick another activity.",
            )
        else:
            show_error_message(
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
        rolls = [random.random() for _ in range(batch_size)]
        new_inv, ok, processed, _outputs = apply_open_bird_nests_pure(
            player_data.get("inventory", {}),
            BIRD_NEST_OPEN_TABLES,
            rolls=rolls,
            batch_size=batch_size,
        )
        if not ok:
            show_error_message("Unavailable activity", f"{display_name} is not available right now.")
            return False
        player_data["inventory"] = new_inv
        check_achievements(player_data)
        save_player_data()
        _refresh_skill_availability()
        _show_activity_gain(f"Opened {processed} bird nest{'s' if processed != 1 else ''}")
        return True

    new_inv, _exp, ok, processed = apply_utility_activity_pure(
        activity_key,
        player_data.get("inventory", {}),
        UTILITY_ACTIVITY_DATA,
    )
    if not ok:
        show_error_message("Unavailable activity", f"{display_name} is not available right now.")
        return False

    player_data["inventory"] = new_inv
    check_achievements(player_data)
    save_player_data()
    _refresh_skill_availability()

    # Confirm the action happened: utility earns no XP, so without this floating
    # "+N <item>" the player gets no signal that the review did anything.
    output_item = str(spec.get("output_item", activity_key))
    try:
        output_qty = max(int(spec.get("output_qty", 1)), 1)
    except (TypeError, ValueError):
        output_qty = 1
    gained = output_qty * max(int(processed), 0)
    if gained > 0:
        _show_activity_gain(f"+{gained} {output_item}")
    return True


def on_fletching_answer():
    target = player_data.get("current_fletch", "arrow_shafts")
    if target not in FLETCHING_DATA:
        target = "arrow_shafts"
        player_data["current_fletch"] = target
    spec = FLETCHING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("fletching_level", 1)

    if player_level < spec["level"]:
        show_error_message("Insufficient level", f"You need level {spec['level']} Fletching to make {display_name}.")
        return False

    new_inv, base_exp, ok = apply_fletching_pure(target, player_data["inventory"], FLETCHING_DATA)
    if not ok:
        for material, amount in spec.get("requirements", {}).items():
            if player_data["inventory"].get(material, 0) < amount:
                show_error_message("Insufficient materials", f"You need {amount} {material} to make {display_name}.")
                break
        return False

    player_data["inventory"] = new_inv
    exp_gained = _award_skill_exp("fletching_exp", base_exp)
    level_up_check("Fletching", player_data)
    check_achievements(player_data)
    save_player_data()
    _refresh_skill_availability()
    _show_exp(exp_gained)
    return True

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
        on_set_utility=lambda activity: _set_value("current_utility", activity),
        on_set_floating_enabled=_set_floating_enabled,
        on_set_floating_position=_set_floating_position,
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
    target = player_data.get("current_smith", DEFAULT_SMITHING_TARGET)
    if target not in SMITHING_DATA:
        target = DEFAULT_SMITHING_TARGET
        player_data["current_smith"] = target
    spec = SMITHING_DATA[target]
    display_name = spec.get("display_name", spec.get("output_item", target))
    player_level = player_data["smithing_level"]

    if player_level < spec["level"]:
        show_error_message("Insufficient level", f"You need level {spec['level']} Smithing to make {display_name}.")
        return False

    new_inv, base_exp, ok = apply_smithing_pure(target, player_data["inventory"], SMITHING_DATA)
    if not ok:
        missing = _missing_materials_text(spec.get("requirements", {}), player_data["inventory"])
        _deactivate_current_skill()
        show_error_message(
            "Out of materials",
            f"You need {missing} to make {display_name}, so Smithing has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    player_data["inventory"] = new_inv
    exp_gained = _award_skill_exp("smithing_exp", base_exp)
    level_up_check("Smithing", player_data)
    check_achievements(player_data)
    save_player_data()

    # Refresh availability for Crafting/Smithing in the open menu after processing.
    try:
        can_craft_any = any(
            can_craft_item_pure(player_data.get("crafting_level", 1), player_data.get("inventory", {}), item_name, CRAFTING_DATA)
            for item_name in CRAFTING_DATA.keys()
        )
        refresh_skill_availability(can_smith_any(), can_craft_any)
    except Exception:
        pass

    _refresh_skill_availability()
    _show_exp(exp_gained)
    return True


def on_woodcutting_answer():
    tree = player_data.get("current_tree", DEFAULT_WOODCUTTING_TARGET)
    if tree not in TREE_DATA:
        tree = DEFAULT_WOODCUTTING_TARGET
        player_data["current_tree"] = tree
    spec = TREE_DATA[tree]
    player_level = player_data.get("woodcutting_level", 1)

    if player_level < spec.get("level", 1):
        show_error_message("Insufficient level", f"You need level {spec['level']} Woodcutting to chop {spec.get('display_name', tree)}.")
        return False

    axe_spec = best_woodcutting_axe_pure(
        player_level,
        player_data.get("inventory", {}),
        player_data.get("toolbelt", {}),
        WOODCUTTING_AXE_DATA,
    )
    if axe_spec is None:
        _deactivate_current_skill()
        show_error_message(
            "No usable hatchet",
            "You need a usable hatchet to train Woodcutting. Woodcutting has been switched off.",
        )
        return False

    r_action = random.random()
    r_nest_drop = random.random()
    r_nest_type = random.random()
    new_inv, base_exp, ok, _output_item, _nest_item = apply_woodcutting_action_pure(
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
    )
    if ok:
        if "logs_cut_today" not in player_data:
            player_data["logs_cut_today"] = 0
        player_data["logs_cut_today"] += 1
        player_data["inventory"] = new_inv
        exp_gained = _award_skill_exp("woodcutting_exp", base_exp)
        level_up_check("Woodcutting", player_data)
        check_achievements(player_data)
        save_player_data()

    _show_exp(base_exp if not ok else exp_gained)
    return True

def on_mining_answer():
    ore = player_data.get("current_ore", DEFAULT_MINING_TARGET)
    if ore not in ORE_DATA:
        ore = DEFAULT_MINING_TARGET
        player_data["current_ore"] = ore
    ore_spec = ORE_DATA[ore]
    player_level = player_data["mining_level"]

    if player_level < ore_spec.get("level", 1):
        show_error_message("Insufficient level", f"You need level {ore_spec['level']} Mining to mine {ore_spec.get('display_name', ore)}.")
        return False

    pickaxe_spec = best_mining_pickaxe_pure(
        player_level,
        player_data.get("inventory", {}),
        player_data.get("toolbelt", {}),
        MINING_PICKAXE_DATA,
    )
    if pickaxe_spec is None:
        _deactivate_current_skill()
        show_error_message(
            "Missing pickaxe",
            "You need a usable pickaxe to train Mining. Mining has been switched off.",
        )
        return False

    bonus_state = mining_bonus_state_pure(player_data.get("owned_equipment", ()), MINING_BONUS_ITEM_DATA)
    gem_drop_chance = GLORY_GEM_DROP_CHANCE if bonus_state["has_glory"] else INCIDENTAL_GEM_DROP_CHANCE
    r_action = random.random()
    r_output = random.random()
    r_gem_chance = random.random()
    r_gem_pick = random.random()

    new_inv, base_exp, ok, _output_item, _gem, _extra_output = apply_mining_action_pure(
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
    )
    if ok:
        if "ores_mined_today" not in player_data:
            player_data["ores_mined_today"] = 0
        player_data["ores_mined_today"] += 1
        player_data["inventory"] = new_inv
        exp_gained = _award_skill_exp("mining_exp", base_exp)
        level_up_check("Mining", player_data)
        check_achievements(player_data)
        save_player_data()

        # If the main menu is open, auto-enable Smithing/Crafting when they become possible.
        _refresh_skill_availability()
        _show_exp(exp_gained)
    return True


def _can_start_current_action() -> bool:
    if current_skill == "Fletching":
        target = player_data.get("current_fletch", "arrow_shafts")
        return can_fletch_item_pure(
            player_data.get("fletching_level", 1),
            player_data.get("inventory", {}),
            target,
            FLETCHING_DATA,
        )
    if current_skill == "Crafting":
        target = player_data.get("current_craft", "")
        return can_craft_item_pure(
            player_data.get("crafting_level", 1),
            player_data.get("inventory", {}),
            target,
            CRAFTING_DATA,
        )
    if current_skill == "Smithing":
        target = player_data.get("current_smith", DEFAULT_SMITHING_TARGET)
        return can_smith_item_pure(
            player_data.get("smithing_level", 1),
            player_data.get("inventory", {}),
            target,
            SMITHING_DATA,
        )
    if current_skill in _UTILITY_SKILL_NAMES:
        activity_key = player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
        return can_perform_utility_activity_pure(
            player_data.get("inventory", {}),
            activity_key,
            UTILITY_ACTIVITY_DATA,
        )
    if current_skill == "Woodcutting":
        target = player_data.get("current_tree", DEFAULT_WOODCUTTING_TARGET)
        spec = TREE_DATA.get(target)
        if not spec or player_data.get("woodcutting_level", 1) < spec.get("level", 1):
            return False
        return best_woodcutting_axe_pure(
            player_data.get("woodcutting_level", 1),
            player_data.get("inventory", {}),
            player_data.get("toolbelt", {}),
            WOODCUTTING_AXE_DATA,
        ) is not None
    if current_skill == "Mining":
        target = player_data.get("current_ore", DEFAULT_MINING_TARGET)
        spec = ORE_DATA.get(target)
        if not spec or player_data.get("mining_level", 1) < spec.get("level", 1):
            return False
        return best_mining_pickaxe_pure(
            player_data.get("mining_level", 1),
            player_data.get("inventory", {}),
            player_data.get("toolbelt", {}),
            MINING_PICKAXE_DATA,
        ) is not None
    return True


_REVIEW_HANDLERS = {
    "mining": on_mining_answer,
    "woodcutting": on_woodcutting_answer,
    "smithing": on_smithing_answer,
    "crafting": on_crafting_answer,
    "fletching": on_fletching_answer,
    "utility": on_utility_answer,
}


def _registered_answer_handler(skill):
    if skill in _UTILITY_SKILL_NAMES:
        return _REVIEW_HANDLERS.get("utility")
    handler_key = review_handler_key(skill)
    if handler_key is None:
        return None
    return _REVIEW_HANDLERS.get(handler_key)


def on_good_answer():
    global current_skill, exp_awarded
    if exp_awarded:
        return
    handler = _registered_answer_handler(current_skill)
    if handler:
        before_state = _capture_player_data_snapshot()
        _begin_review_feedback_context()
        try:
            for tick_index in range(_review_action_multiplier()):
                if tick_index > 0 and not _can_start_current_action():
                    break
                result = handler()
                if result is False or current_skill == "None":
                    break
        finally:
            _finish_review_feedback_context()
            _remember_review_award_snapshot(before_state)

    exp_awarded = True


## Removed roll_gem wrapper; mining uses apply_mining_pure directly.


def on_answer_card(self, ease, _old):
    global card_turned, exp_awarded, answer_shown
    if ease > 1 and (is_review_skill(current_skill) or current_skill in _UTILITY_SKILL_NAMES) and card_turned and not exp_awarded and answer_shown:
        on_good_answer()
        exp_awarded = True
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
