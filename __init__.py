# __init__.py

from .constants import (
    ORE_DATA,
    TREE_DATA,
    BAR_DATA,
    GEM_DATA,
    CRAFTING_DATA,
    FLETCHING_DATA,
    ORE_IMAGES,
    TREE_IMAGES,
    BAR_IMAGES,
    GEM_IMAGES,
    CRAFTED_ITEM_IMAGES,
)
from aqt import mw, gui_hooks
from anki.hooks import addHook, wrap
from aqt.reviewer import Reviewer
import time
import random
import os
import datetime
from .logic_pure import (
    calculate_probability_with_level,
    pick_gem,
    can_smelt_any_bar_pure,
    create_soft_clay_pure,
    has_crafting_materials_pure,
    can_craft_item_pure,
    apply_crafting_pure,
    apply_smelt_pure,
    apply_fletching_pure,
    apply_woodcutting_pure,
    apply_mining_pure,
    can_mine_ore_pure,
    can_cut_tree_pure,
)
from .logic import level_up_check, check_achievements, calculate_woodcutting_probability, calculate_mining_probability
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
        refresh_skill_availability(can_smelt_any_bar(), can_craft_any)
    except Exception:
        pass


def show_skill_selection():
    global current_skill
    selected = ui.show_skill_selection_dialog(current_skill, can_smelt_any_bar())
    if selected is None:
        return
    save_skill(selected, None)

def save_skill(skill, dialog):
    global current_skill
    if skill == "Smithing" and not can_smelt_any_bar():
        show_error_message("No Ores Available", "You don't have enough ores to smelt any bars. Mine some ores first!")
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
    item = player_data["current_craft"]

    # Check level and material requirements first
    if not has_crafting_materials(item):
        show_error_message("Insufficient materials", f"You don't have enough materials to craft {item}.")
        return

    # Apply crafting via pure function (handles Soft clay and crafted items)
    new_inv, exp_gained, ok = apply_crafting_pure(item, player_data["inventory"], CRAFTING_DATA)
    if not ok:
        show_error_message("Insufficient materials", f"You don't have enough materials to craft {item}.")
        return

    # Update player data and UI
    player_data["inventory"] = new_inv
    player_data["crafting_exp"] += exp_gained
    level_up_check("Crafting", player_data)
    check_achievements(player_data)
    save_player_data()

    # Refresh availability for Crafting/Smithing in the open menu (enables, never auto-selects)
    try:
        can_craft_any = any(
            can_craft_item_pure(player_data.get("crafting_level", 1), player_data.get("inventory", {}), item_name, CRAFTING_DATA)
            for item_name in CRAFTING_DATA.keys()
        )
        refresh_skill_availability(can_smelt_any_bar(), can_craft_any)
    except Exception:
        pass

    _refresh_skill_availability()
    _show_exp(exp_gained)


def on_fletching_answer():
    target = player_data.get("current_fletch", "Arrow shafts")
    spec = FLETCHING_DATA[target]
    player_level = player_data.get("fletching_level", 1)

    if player_level < spec["level"]:
        show_error_message("Insufficient level", f"You need level {spec['level']} Fletching to make {target}.")
        return

    new_inv, exp_gained, ok = apply_fletching_pure(target, player_data["inventory"], FLETCHING_DATA)
    if not ok:
        for material, amount in spec.get("requirements", {}).items():
            if player_data["inventory"].get(material, 0) < amount:
                show_error_message("Insufficient materials", f"You need {amount} {material} to make {target}.")
                break
        return

    player_data["inventory"] = new_inv
    player_data["fletching_exp"] += exp_gained
    level_up_check("Fletching", player_data)
    check_achievements(player_data)
    save_player_data()
    _show_exp(exp_gained)

def show_bar_selection():
    selected = ui.show_bar_selection_dialog(
        current_bar=player_data.get("current_bar", "Bronze bar"),
        smithing_level=player_data.get("smithing_level", 1),
        BAR_DATA=BAR_DATA,
        BAR_IMAGES=BAR_IMAGES,
    )
    if selected:
        player_data["current_bar"] = selected
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
        can_smelt_any_bar(),
        on_save_skill=lambda skill: save_skill(skill, None),
        on_set_ore=lambda ore: _set_value("current_ore", ore),
        on_set_tree=lambda tree: _set_value("current_tree", tree),
        on_set_bar=lambda bar: _set_value("current_bar", bar),
        on_set_craft=lambda item: _set_value("current_craft", item),
        on_set_fletch=lambda target: _set_value("current_fletch", target),
        on_set_floating_enabled=_set_floating_enabled,
        on_set_floating_position=_set_floating_position,
    )


def _set_value(key: str, value):
    player_data[key] = value
    save_player_data()


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
    bar = player_data["current_bar"]
    bar_spec = BAR_DATA[bar]
    player_level = player_data["smithing_level"]

    if player_level < bar_spec["level"]:
        show_error_message("Insufficient level", f"You need level {bar_spec['level']} Smithing to smelt {bar}.")
        return

    # Use pure smelt application
    new_inv, exp_gained, ok = apply_smelt_pure(bar, player_data["inventory"], BAR_DATA)
    if not ok:
        # Find first missing ore to provide a helpful message
        for ore, amount in bar_spec["ore_required"].items():
            if player_data["inventory"].get(ore, 0) < amount:
                show_error_message("Insufficient ore", f"You need {amount} {ore} to smelt {bar}.")
                break
        return

    player_data["inventory"] = new_inv
    player_data["smithing_exp"] += exp_gained
    level_up_check("Smithing", player_data)
    check_achievements(player_data)
    save_player_data()

    # Refresh availability for Crafting/Smithing in the open menu after smelting
    try:
        can_craft_any = any(
            can_craft_item_pure(player_data.get("crafting_level", 1), player_data.get("inventory", {}), item_name, CRAFTING_DATA)
            for item_name in CRAFTING_DATA.keys()
        )
        refresh_skill_availability(can_smelt_any_bar(), can_craft_any)
    except Exception:
        pass

    _refresh_skill_availability()
    _show_exp(exp_gained)


def on_woodcutting_answer():
    tree = player_data["current_tree"]
    spec = TREE_DATA[tree]
    player_level = player_data["woodcutting_level"]

    woodcutting_probability = calculate_woodcutting_probability(player_level, spec["probability"])
    r_action = random.random()
    new_inv, exp_gained, ok = apply_woodcutting_pure(tree, player_data["inventory"], TREE_DATA, r_action, woodcutting_probability)
    if ok:
        if "logs_cut_today" not in player_data:
            player_data["logs_cut_today"] = 0
        player_data["logs_cut_today"] += 1
        player_data["inventory"] = new_inv
        player_data["woodcutting_exp"] += exp_gained
        level_up_check("Woodcutting", player_data)
        check_achievements(player_data)
        save_player_data()

    _show_exp(exp_gained)

def on_mining_answer():
    ore = player_data["current_ore"]
    ore_spec = ORE_DATA[ore]
    player_level = player_data["mining_level"]

    mining_probability = calculate_mining_probability(player_level, ore_spec["probability"])
    r_action = random.random()
    r_gem_chance = random.random()
    r_gem_pick = random.random()

    new_inv, exp_gained, ok, _gem = apply_mining_pure(
        ore,
        player_data["inventory"],
        ORE_DATA,
        GEM_DATA,
        r_action,
        mining_probability,
        r_gem_chance,
        r_gem_pick,
        gem_drop_chance=1/256,
    )
    if ok:
        if "ores_mined_today" not in player_data:
            player_data["ores_mined_today"] = 0
        player_data["ores_mined_today"] += 1
        player_data["inventory"] = new_inv
        player_data["mining_exp"] += exp_gained
        level_up_check("Mining", player_data)
        check_achievements(player_data)
        save_player_data()

        # If the main menu is open, auto-enable Smithing/Crafting when they become possible.
        _refresh_skill_availability()
        _show_exp(exp_gained)


_REVIEW_HANDLERS = {
    "mining": on_mining_answer,
    "woodcutting": on_woodcutting_answer,
    "smithing": on_smithing_answer,
    "crafting": on_crafting_answer,
    "fletching": on_fletching_answer,
}


def _registered_answer_handler(skill):
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
        handler()

    exp_awarded = True


## Removed roll_gem wrapper; mining uses apply_mining_pure directly.


def on_answer_card(self, ease, _old):
    global card_turned, exp_awarded, answer_shown
    if ease > 1 and is_review_skill(current_skill) and card_turned and not exp_awarded and answer_shown:
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


def can_smelt_any_bar():
    return can_smelt_any_bar_pure(player_data["inventory"], player_data["smithing_level"], BAR_DATA)

def create_soft_clay():
    new_inv, ok = create_soft_clay_pure(player_data["inventory"]) 
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
