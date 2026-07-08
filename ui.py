# ui.py - UI components and dialogs for AnkiScape

import os
from typing import Optional
import datetime

try:
    from aqt import mw  # type: ignore
    from aqt.qt import *  # type: ignore
    # Explicit imports to satisfy static analysis and avoid star-import ambiguity
    from aqt.qt import (  # type: ignore
        Qt,
        QIcon,
        QSize,
        QTabWidget,
        QWidget,
        QVBoxLayout,
        QComboBox,
        QLabel,
        QPushButton,
        QListWidget,
        QListWidgetItem,
        QGraphicsOpacityEffect,
        QPropertyAnimation,
        QEasingCurve,
        QPoint,
        QMessageBox,
        QDialog,
        QPixmap,
        QPalette,
        QColor,
        QApplication,
        QMenu,
        QGridLayout,
        QHBoxLayout,
        QButtonGroup,
        QRadioButton,
        QScrollArea,
        QSizePolicy,
        QProgressBar,
        QCheckBox,
        QSpinBox,
        QInputDialog,
        QDesktopServices,
        QUrl,
        QEvent,
        QLineEdit,
        QToolButton,
    )
    HAS_QT = True
except Exception:
    # Running outside Anki/Qt environment (e.g., unit tests). Keep module importable.
    mw = None  # type: ignore
    HAS_QT = False

try:
    from .constants import (
        EXP_TABLE,
        ORE_DATA,
        MINING_OUTPUT_ITEMS,
        MINING_PICKAXE_DATA,
        MINING_BONUS_ITEM_DATA,
        DEFAULT_MINING_TARGET,
        TREE_DATA,
        WOODCUTTING_AXE_DATA,
        WOODCUTTING_LOG_ITEMS,
        DEFAULT_WOODCUTTING_TARGET,
        BIRD_NEST_OPEN_TABLES,
        BAR_DATA,
        SMITHING_DATA,
        DEFAULT_SMITHING_TARGET,
        GEM_DATA,
        CRAFTING_DATA,
        COOKING_DATA,
        FLETCHING_DATA,
        FLETCHING_GROUP_LABELS,
        FLETCHING_GROUP_ORDER,
        FIREMAKING_DATA,
        FISHING_DATA,
        HUNTER_DATA,
        HUNTER_GROUP_LABELS,
        HUNTER_GROUP_ORDER,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        QUEST_DATA,
        QUEST_UNLOCK_RULES,
        CLAIM_DATA,
        COMBAT_FOOD_DATA,
        COMBAT_ATTACK_STYLE_DATA,
        COMBAT_ENEMY_DATA,
        COMBAT_ENEMY_IMAGES,
        COMBAT_MAGIC_SPELL_DATA,
        COMBAT_TARGET_GROUP_ORDER,
        BINDING_NECKLACE_ITEM,
        DEFAULT_COMBAT_ATTACK_STYLE,
        DEFAULT_COMBAT_SPELL,
        DEFAULT_COMBAT_TARGET,
        FIREMAKING_LOG_ITEMS,
        FISHING_OUTPUT_ITEMS,
        RUNECRAFTING_GROUP_LABELS,
        UTILITY_ACTIVITY_DATA,
        DEFAULT_FIREMAKING_TARGET,
        DEFAULT_FISHING_TARGET,
        DEFAULT_HUNTER_TARGET,
        DEFAULT_COOKING_TARGET,
        DEFAULT_RUNECRAFTING_TARGET,
        DEFAULT_UTILITY_ACTIVITY,
        ORE_IMAGES,
        TREE_IMAGES,
        BAR_IMAGES,
        GEM_IMAGES,
        CRAFTED_ITEM_IMAGES,
        FLETCHED_ITEM_IMAGES,
        FIREMAKING_ITEM_IMAGES,
        FISHING_ITEM_IMAGES,
        HUNTER_ITEM_IMAGES,
        COOKING_ITEM_IMAGES,
        RUNECRAFTING_ITEM_IMAGES,
        UTILITY_ITEM_IMAGES,
        ACHIEVEMENTS,
        EQUIPMENT_SLOTS,
        EQUIPMENT_ITEM_DATA,
        current_dir,
    )
except Exception:
    # Fallback for direct module import in tests
    from constants import (  # type: ignore
        EXP_TABLE,
        ORE_DATA,
        MINING_OUTPUT_ITEMS,
        MINING_PICKAXE_DATA,
        MINING_BONUS_ITEM_DATA,
        DEFAULT_MINING_TARGET,
        TREE_DATA,
        WOODCUTTING_AXE_DATA,
        WOODCUTTING_LOG_ITEMS,
        DEFAULT_WOODCUTTING_TARGET,
        BIRD_NEST_OPEN_TABLES,
        BAR_DATA,
        SMITHING_DATA,
        DEFAULT_SMITHING_TARGET,
        GEM_DATA,
        CRAFTING_DATA,
        COOKING_DATA,
        FLETCHING_DATA,
        FLETCHING_GROUP_LABELS,
        FLETCHING_GROUP_ORDER,
        FIREMAKING_DATA,
        FISHING_DATA,
        HUNTER_DATA,
        HUNTER_GROUP_LABELS,
        HUNTER_GROUP_ORDER,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        QUEST_DATA,
        QUEST_UNLOCK_RULES,
        CLAIM_DATA,
        COMBAT_FOOD_DATA,
        COMBAT_ATTACK_STYLE_DATA,
        COMBAT_ENEMY_DATA,
        COMBAT_ENEMY_IMAGES,
        COMBAT_MAGIC_SPELL_DATA,
        COMBAT_TARGET_GROUP_ORDER,
        BINDING_NECKLACE_ITEM,
        DEFAULT_COMBAT_ATTACK_STYLE,
        DEFAULT_COMBAT_SPELL,
        DEFAULT_COMBAT_TARGET,
        FIREMAKING_LOG_ITEMS,
        FISHING_OUTPUT_ITEMS,
        RUNECRAFTING_GROUP_LABELS,
        UTILITY_ACTIVITY_DATA,
        DEFAULT_FIREMAKING_TARGET,
        DEFAULT_FISHING_TARGET,
        DEFAULT_HUNTER_TARGET,
        DEFAULT_COOKING_TARGET,
        DEFAULT_RUNECRAFTING_TARGET,
        DEFAULT_UTILITY_ACTIVITY,
        ORE_IMAGES,
        TREE_IMAGES,
        BAR_IMAGES,
        GEM_IMAGES,
        CRAFTED_ITEM_IMAGES,
        FLETCHED_ITEM_IMAGES,
        FIREMAKING_ITEM_IMAGES,
        FISHING_ITEM_IMAGES,
        HUNTER_ITEM_IMAGES,
        COOKING_ITEM_IMAGES,
        RUNECRAFTING_ITEM_IMAGES,
        UTILITY_ITEM_IMAGES,
        ACHIEVEMENTS,
        EQUIPMENT_SLOTS,
        EQUIPMENT_ITEM_DATA,
        current_dir,
    )
try:
    from .logic_pure import can_cut_tree_pure, can_mine_ore_pure, can_craft_item_pure, can_smelt_any_bar_pure, can_smith_item_pure, fletching_target_locked_reasons_pure, firemaking_target_locked_reasons_pure, calculate_firemaking_success_probability_pure, can_fish_method_pure, eligible_fishing_fish_pure, has_fishing_bait_pure, calculate_fishing_success_probability_pure, hunter_target_locked_reasons_pure, cooking_target_locked_reasons_pure, calculate_cooking_success_probability_pure, can_chop_woodcutting_target_pure, best_woodcutting_axe_pure, best_mining_pickaxe_pure, can_open_bird_nests_pure, sanitize_review_action_multiplier, bank_gear_rows_pure, can_equip_item_pure, equipment_stat_totals_pure, binding_necklace_charges_pure, can_runecraft_any_pure, claim_rows_pure, quest_journal_rows_pure, quest_locked_reasons_pure, quest_current_stage_blocker_reasons_pure, quest_current_stage_choices_pure, apply_quest_route_choice_pure, quest_availability_state_pure, quest_state_pure, can_attempt_quest_review_pure, combat_supply_loadout_summary_pure, combat_death_office_summary_pure, combat_target_locked_reasons_pure, combat_attack_style_for_equipment_pure, player_combat_level_pure
    from .skill_registry import get_skill
except Exception:
    from logic_pure import can_cut_tree_pure, can_mine_ore_pure, can_craft_item_pure, can_smelt_any_bar_pure, can_smith_item_pure, fletching_target_locked_reasons_pure, firemaking_target_locked_reasons_pure, calculate_firemaking_success_probability_pure, can_fish_method_pure, eligible_fishing_fish_pure, has_fishing_bait_pure, calculate_fishing_success_probability_pure, hunter_target_locked_reasons_pure, cooking_target_locked_reasons_pure, calculate_cooking_success_probability_pure, can_chop_woodcutting_target_pure, best_woodcutting_axe_pure, best_mining_pickaxe_pure, can_open_bird_nests_pure, sanitize_review_action_multiplier, bank_gear_rows_pure, can_equip_item_pure, equipment_stat_totals_pure, binding_necklace_charges_pure, can_runecraft_any_pure, claim_rows_pure, quest_journal_rows_pure, quest_locked_reasons_pure, quest_current_stage_blocker_reasons_pure, quest_current_stage_choices_pure, apply_quest_route_choice_pure, quest_availability_state_pure, quest_state_pure, can_attempt_quest_review_pure, combat_supply_loadout_summary_pure, combat_death_office_summary_pure, combat_target_locked_reasons_pure, combat_attack_style_for_equipment_pure, player_combat_level_pure  # type: ignore
    from skill_registry import get_skill  # type: ignore
try:
    from .logic_pure import combat_status_summary_pure, combat_hud_state_pure, combat_weapon_style_options_pure
except Exception:
    from logic_pure import combat_status_summary_pure, combat_hud_state_pure, combat_weapon_style_options_pure  # type: ignore

try:
    from .equipment_data import EQUIPMENT_BONUS_FIELDS
except Exception:
    from equipment_data import EQUIPMENT_BONUS_FIELDS  # type: ignore

try:
    from .skill_hub import CategoryView, SkillCardView, build_skill_hub, first_category_id
except Exception:
    from skill_hub import CategoryView, SkillCardView, build_skill_hub, first_category_id  # type: ignore

try:
    from .skill_registry import implemented_skill_definitions, implemented_review_skill_names, get_skill
except Exception:
    from skill_registry import implemented_skill_definitions, implemented_review_skill_names, get_skill  # type: ignore

try:
    from .achievement_metadata import (
        ACHIEVEMENT_DIFFICULTIES,
        achievement_difficulty_progress,
        achievement_progress,
        achievement_rows_for_difficulty,
    )
except Exception:
    from achievement_metadata import (  # type: ignore
        ACHIEVEMENT_DIFFICULTIES,
        achievement_difficulty_progress,
        achievement_progress,
        achievement_rows_for_difficulty,
    )

try:
    from .target_metadata import (
        TargetRowMetadata,
        combat_target_rows,
        cooking_target_rows,
        crafting_target_rows,
        firemaking_target_rows,
        fishing_target_rows,
        fletching_target_rows,
        hunter_target_rows,
        mining_target_rows,
        runecrafting_target_rows,
        smithing_target_rows,
        utility_activity_rows,
        woodcutting_target_rows,
    )
except Exception:
    from target_metadata import (  # type: ignore
        TargetRowMetadata,
        combat_target_rows,
        cooking_target_rows,
        crafting_target_rows,
        firemaking_target_rows,
        fishing_target_rows,
        fletching_target_rows,
        hunter_target_rows,
        mining_target_rows,
        runecrafting_target_rows,
        smithing_target_rows,
        utility_activity_rows,
        woodcutting_target_rows,
    )

try:
    from .shop_data import SHOP_DATA, SHOP_SERVICES, SHOP_VENDOR_ACTIONS
    from .shop_logic import (
        apply_shop_buy_pure,
        apply_shop_sell_pure,
        apply_shop_service_pure,
        apply_shop_vendor_action_pure,
        preview_shop_buy_pure,
        preview_shop_sell_pure,
        preview_shop_service_pure,
        preview_shop_vendor_action_pure,
        search_shop_catalog_pure,
        shop_history_rows_pure,
        shop_view_model_pure,
    )
except Exception:
    from shop_data import SHOP_DATA, SHOP_SERVICES, SHOP_VENDOR_ACTIONS  # type: ignore
    from shop_logic import (  # type: ignore
        apply_shop_buy_pure,
        apply_shop_sell_pure,
        apply_shop_service_pure,
        apply_shop_vendor_action_pure,
        preview_shop_buy_pure,
        preview_shop_sell_pure,
        preview_shop_service_pure,
        preview_shop_vendor_action_pure,
        search_shop_catalog_pure,
        shop_history_rows_pure,
        shop_view_model_pure,
    )

try:
    from .constants import ITEM_DEFINITIONS
    from .item_registry import ItemDefinition, item_definitions_by_storage_key
except Exception:
    from constants import ITEM_DEFINITIONS  # type: ignore
    from item_registry import ItemDefinition, item_definitions_by_storage_key  # type: ignore

try:
    from . import inventory_pure
except Exception:
    import inventory_pure  # type: ignore

# Central debug logger (support both package and flat import in tests)
try:
    from .debug import debug_log as _debug_log  # type: ignore
except Exception:
    try:
        from debug import debug_log as _debug_log  # type: ignore
    except Exception:
        def _debug_log(msg: str) -> None:
            pass

# Lightweight context for the open Main Menu to allow dynamic UI refreshes
_MAIN_MENU_CTX = {
    "dialog": None,
    "smith_btn": None,
    "craft_btn": None,
    "fletch_btn": None,
    "firemaking_btn": None,
    "hunter_btn": None,
    "cooking_btn": None,
    "runecrafting_btn": None,
    "warn_label": None,
}


# ---- registry-driven UI helpers -------------------------------------------
# These keep Stats/Bank/HUD in sync with the skill + item registries so a new
# playable skill (e.g. Fletching) surfaces everywhere without another hardcoded
# four-skill branch. Icons follow the existing convention: icon/<skill_id>_icon.png.

# Bank grouping order + labels. Categories come from item_registry.ItemCategory.
_ITEM_CATEGORY_ORDER = ("ore", "log", "fish", "food", "gem", "bar", "crafted", "fletched", "hunter", "runecrafting", "material", "equipment", "smithed", "tool")
_ITEM_CATEGORY_LABELS = {
    "ore": "Ores",
    "log": "Logs",
    "fish": "Fish",
    "food": "Food",
    "gem": "Gems",
    "bar": "Bars",
    "crafted": "Crafted",
    "fletched": "Fletched",
    "hunter": "Hunter",
    "runecrafting": "Runecrafting",
    "material": "Materials",
    "equipment": "Equipment",
    "smithed": "Smithed",
    "tool": "Tools",
}

# Friendly headers for the Crafting panel's family groups (CraftingRecipe.family
# -> display label). Anything not listed falls back to family.title(), so a new
# family group still renders a sensible header without a code change.
_CRAFT_FAMILY_LABELS = {
    "gems": "Gem cutting",
    "pottery": "Pottery",
    "spinning": "Spinning",
    "silver": "Silver",
    "jewellery": "Jewellery",
    "leather": "Leather",
    "glass": "Glassblowing",
    "battlestaff": "Battlestaves",
    "weaving": "Weaving",
    "combination": "Combinations",
}

_COOKING_FAMILY_LABELS = {
    "fish": "Fish",
    "eels": "Eels",
    "snails": "Snails",
    "bread": "Bread",
    "pies": "Pies",
    "stews": "Stews and curry",
    "vegetables": "Vegetables",
    "pizza": "Pizza",
    "meat": "Meat",
}

_UTILITY_GROUP_LABELS = {
    "cooking_prep": "Cooking prep",
    "gathering": "Gathering",
    "material_processing": "Material processing",
    "containers_opening": "Containers / opening",
}


def skill_icon_path_for(display_name: str) -> Optional[str]:
    """Resolve a skill's icon by registry id (icon/<id>_icon.png), else None.

    Falls back to the lowercased display name so skills added before their id is
    wired still find a matching file. Returns None when no asset exists, letting
    callers degrade gracefully instead of showing a broken image.
    """
    candidates = []
    skill = get_skill(display_name)
    if skill is not None:
        candidates.append(f"{skill.id}_icon.png")
    candidates.append(f"{display_name.lower()}_icon.png")
    for fname in candidates:
        path = os.path.join(current_dir, "icon", fname)
        if os.path.exists(path):
            return path
    return None


def playable_review_skill_names() -> tuple:
    """Display names of skills that earn XP during review, straight from the registry."""
    return tuple(implemented_review_skill_names())


# ---- dark-mode-safe text colors ------------------------------------------
# RECURRING BUG, READ BEFORE STYLING TEXT: ``palette(mid)`` / ``QPalette.Mid`` is
# a *frame/border* role, NOT a text role. In dark mode it resolves to a near-black
# grey, so using it as a text/foreground color makes the text invisible on the
# dark base (greyed/disabled rows "vanish"). It has bitten the Skills-hub buttons,
# the Smithing locked rows, and the Equipment empty slots. Never use palette(mid)
# (or QPalette.Mid) for text. For dimmed-but-legible text use the helpers below,
# which derive the color from the theme's actual Text role and just drop the
# alpha — guaranteed contrast in BOTH light and dark themes. (palette(mid) is fine
# for borders/frames, which is its intended role.)

def dim_text_color(widget=None) -> "QColor":
    """A dimmed-but-readable text QColor that works in light AND dark themes.

    Use for greyed/placeholder/disabled-row text (e.g. ``setForeground(...)``).
    """
    palette = widget.palette() if widget is not None else QApplication.palette()
    color = QColor(palette.color(QPalette.ColorRole.Text))
    color.setAlpha(150)
    return color


def dim_text_css(widget=None) -> str:
    """``rgba(...)`` form of :func:`dim_text_color` for Qt stylesheets.

    Stylesheets can't reference a dimmed text role (the stylesheet ``palette()``
    function only exposes solid roles, and ``mid`` is the trap we're avoiding), so
    bake an explicit rgba string from the live palette instead.
    """
    c = dim_text_color(widget)
    return f"rgba({c.red()}, {c.green()}, {c.blue()}, {c.alphaF():.2f})"


# ---- equipment surface helpers -------------------------------------------
# Why this lives here and not in logic_pure: these are *presentation* concerns
# (icon paths, compact human labels). The equip gate, swap, and stat-totalling
# are all pure and tested in logic_pure; the UI only reads them. The Equipment
# tab renders every EQUIPMENT_SLOTS row (greyed when empty) and right-click
# Equip/Unequip drives the backend on_equip_item / on_unequip_slot handlers.

# Friendly labels for the EquipmentBonuses stat block. Order mirrors how OSRS
# groups the worn-equipment screen so a future combat system's tooltip can reuse
# the same vocabulary without re-deriving it.
_EQUIPMENT_BONUS_LABELS = {
    "attack_stab": "Stab",
    "attack_slash": "Slash",
    "attack_crush": "Crush",
    "attack_magic": "Magic",
    "attack_ranged": "Range",
    "defence_stab": "Stab",
    "defence_slash": "Slash",
    "defence_crush": "Crush",
    "defence_magic": "Magic",
    "defence_ranged": "Range",
    "melee_strength": "Str",
    "ranged_strength": "Ranged Str",
    "magic_damage": "Magic Dmg",
    "prayer": "Prayer",
}
_EQUIPMENT_BONUS_GROUPS = (
    ("Attack bonuses", ("attack_stab", "attack_slash", "attack_crush", "attack_magic", "attack_ranged")),
    ("Defence bonuses", ("defence_stab", "defence_slash", "defence_crush", "defence_magic", "defence_ranged")),
    ("Other bonuses", ("melee_strength", "ranged_strength", "magic_damage", "prayer")),
)
# A handful of high-signal fields for the one-line summary on inventory rows, so
# the tooltip reads like the plan's "Stab +20, Slash +29, Str +25" example
# rather than dumping all 14 fields.
_EQUIPMENT_SUMMARY_FIELDS = (
    "attack_stab",
    "attack_slash",
    "attack_crush",
    "attack_ranged",
    "melee_strength",
    "ranged_strength",
    "defence_stab",
    "prayer",
)
# Matches the backend's can_equip_item_pure lock-reason wording ("Defense") so
# the inventory-row tooltip and the right-click lock reason speak with one voice.
_COMBAT_SKILL_LABELS = {
    "attack": "Attack",
    "defense": "Defense",
    "ranged": "Ranged",
    "strength": "Strength",
    "magic": "Magic",
    "prayer": "Prayer",
}
_COMBAT_SKILL_SHORT_LABELS = {
    "attack": "Atk",
    "defense": "Def",
    "ranged": "Rng",
    "strength": "Str",
    "magic": "Magic",
    "prayer": "Pray",
}


def _equipment_skill_requirements(spec) -> list[tuple[str, int]]:
    raw_requirements = spec.get("skill_requirements") or ()
    requirements: list[tuple[str, int]] = []
    if isinstance(raw_requirements, dict):
        requirement_iterable = raw_requirements.items()
    elif isinstance(raw_requirements, (tuple, list)):
        requirement_iterable = raw_requirements
    else:
        requirement_iterable = ()
    for requirement in requirement_iterable:
        if isinstance(requirement, dict):
            combat_skill = requirement.get("skill")
            raw_level = requirement.get("level")
        elif isinstance(requirement, (tuple, list)) and len(requirement) >= 2:
            combat_skill = requirement[0]
            raw_level = requirement[1]
        else:
            continue
        try:
            required = int(raw_level)
        except (TypeError, ValueError):
            continue
        if isinstance(combat_skill, str) and combat_skill and required > 1:
            requirements.append((combat_skill, required))
    if requirements:
        return requirements

    combat_skill = spec.get("combat_skill")
    try:
        required = int(spec.get("required_level", 1) or 1)
    except (TypeError, ValueError):
        required = 1
    if isinstance(combat_skill, str) and combat_skill and required > 1:
        return [(combat_skill, required)]
    return []


def _join_requirement_parts(parts: list[str]) -> str:
    if len(parts) <= 1:
        return "".join(parts)
    return ", ".join(parts[:-1]) + f" and {parts[-1]}"


def is_equippable_item(item_name: str) -> bool:
    return item_name in EQUIPMENT_ITEM_DATA


def equipment_slot_icon_path(slot_id: str) -> Optional[str]:
    """Path to the greyed OSRS placeholder for a worn slot, or None if unfetched.

    Slot art is developer-fetched by tools/fetch_equipment_assets.py into
    equipment_slots/<slot_id>.png. Missing files degrade to a text-only row.
    """
    path = os.path.join(current_dir, "equipment_slots", f"{slot_id}.png")
    return path if os.path.exists(path) else None


def _bonus_value(bonuses, key: str) -> int:
    if isinstance(bonuses, dict):
        value = bonuses.get(key, 0)
    else:
        value = getattr(bonuses, key, 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _format_bonus(value: int) -> str:
    return f"+{value}" if value >= 0 else str(value)


def equipment_requirement_text(item_name: str) -> str:
    """e.g. 'Requires level 40 Attack', or '' for no-requirement gear (req 1)."""
    spec = EQUIPMENT_ITEM_DATA.get(item_name)
    if not spec:
        return ""
    requirements = _equipment_skill_requirements(spec)
    if not requirements:
        return ""
    parts = [
        f"level {required} {_COMBAT_SKILL_LABELS.get(combat_skill, str(combat_skill).title())}"
        for combat_skill, required in requirements
    ]
    return f"Requires {_join_requirement_parts(parts)}"


def equipment_summary_text(item_name: str) -> str:
    """Compact one-line bonus + requirement summary for tooltips/rows.

    Picks the high-signal offensive/strength fields so the line stays short
    (the plan's "Stab +20, Slash +29, Str +25, Req 40 Atk" shape) instead of
    listing every zeroed stat.
    """
    spec = EQUIPMENT_ITEM_DATA.get(item_name)
    if not spec:
        return ""
    bonuses = spec.get("bonuses", {})
    parts = []
    for field in _EQUIPMENT_SUMMARY_FIELDS:
        value = _bonus_value(bonuses, field)
        if value:
            parts.append(f"{_EQUIPMENT_BONUS_LABELS[field]} {_format_bonus(value)}")
    requirements = _equipment_skill_requirements(spec)
    if requirements:
        req_parts = [
            f"{required} {_COMBAT_SKILL_SHORT_LABELS.get(combat_skill, str(combat_skill).title())}"
            for combat_skill, required in requirements
        ]
        parts.append(f"Req {', '.join(req_parts)}")
    return ", ".join(parts)


def equipment_full_tooltip(item_name: str, lock_reason: str = "") -> str:
    """Multi-line worn-stat breakdown for a slot/inventory row tooltip."""
    spec = EQUIPMENT_ITEM_DATA.get(item_name)
    if not spec:
        return ""
    bonuses = spec.get("bonuses", {})
    lines = [item_name]
    requirement = equipment_requirement_text(item_name)
    if requirement:
        lines.append(requirement)
    if lock_reason:
        lines.append(lock_reason)
    for group_label, fields in _EQUIPMENT_BONUS_GROUPS:
        cells = [
            f"{_EQUIPMENT_BONUS_LABELS[field]} {_format_bonus(_bonus_value(bonuses, field))}"
            for field in fields
        ]
        lines.append(f"{group_label}: " + ", ".join(cells))
    return "\n".join(lines)


# Utility / Activities is intentionally NOT a registry skill: it has no XP, level,
# or exp key. The backend routes it through these display names + `current_utility`,
# so the hub surfaces it as a synthetic, visually-distinct entry.
_UTILITY_HUB_NAME = "Utility / Activities"
_UTILITY_SKILL_NAMES = {"Utility", _UTILITY_HUB_NAME}
_COMBAT_HUB_NAME = "Combat"
# The individual skills a combat burst can train, with their player_data level
# and exp keys. Constitution defaults to level 10 (RS classic); everything else
# to 1. Order mirrors the RS combat tab. Prayer/Summoning are excluded — combat
# reviews don't feed them (see _combat_apply_xp).
_COMBAT_SKILL_BARS = (
    ("Attack", "attack_level", "attack_exp", 1),
    ("Strength", "strength_level", "strength_exp", 1),
    ("Defence", "defense_level", "defense_exp", 1),
    ("Ranged", "ranged_level", "ranged_exp", 1),
    ("Magic", "magic_level", "magic_exp", 1),
    ("Constitution", "constitution_level", "constitution_exp", 10),
)
_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY = "ankiscape_review_action_multiplier"
_LEGACY_XP_MULTIPLIER_CONFIG_KEY = "ankiscape_xp_multiplier"

# Backend (mining_data.DEFERRED_MINING_CONTENT) deliberately defers the
# "concentrated" coal/gold deposits: their 2011Scape distinction is Living Rock
# Caverns depletion behavior, which AnkiScape's review loop doesn't model. We
# surface that as honest tooltip copy on the ordinary rows rather than letting a
# player wonder why concentrated variants are missing. Keyed by stable target ID.
_MINING_DEFERRED_VARIANT_NOTES = {
    "coal": "Concentrated coal deposits are deferred (Living Rock Caverns depletion isn't modeled); this row mines ordinary coal.",
    "gold": "Concentrated gold deposits are deferred (Living Rock Caverns depletion isn't modeled); this row mines ordinary gold.",
}


# Item sprites are pre-trimmed at build time (see tools/trim_icons.py and the
# fetch_assets.py alpha-trim step), so the UI just uses plain QIcon(path) — no
# runtime cropping. Re-run tools/trim_icons.py if a freshly added sprite ever
# looks small in its icon box.


def _item_def_for(storage_key: str) -> Optional["ItemDefinition"]:
    return _ITEM_DEFS_BY_KEY.get(storage_key)


def _item_icon_path(item_name: str) -> Optional[str]:
    definition = _item_def_for(item_name)
    asset_path = definition.asset_path if definition is not None else None
    if asset_path and os.path.exists(asset_path):
        return asset_path
    return None


# Wiki sprites range from ~12px to ~40px and QIcon never upscales, so raw
# QIcon(path) renders small pixel art tiny next to normal-sized art. This
# helper normalizes every icon to the slot size with nearest-neighbor scaling
# (crisp pixels, no blur), sized for the screen's device pixel ratio.
_PIXEL_ICON_CACHE: dict = {}


def _pixel_item_icon(item_name: str, size: int) -> Optional["QIcon"]:
    icon_path = _item_icon_path(item_name)
    if not icon_path:
        return None
    key = (icon_path, size)
    icon = _PIXEL_ICON_CACHE.get(key)
    if icon is not None:
        return icon
    pixmap = QPixmap(icon_path)
    if pixmap.isNull():
        return None
    try:
        ratio = float(QApplication.primaryScreen().devicePixelRatio())
    except Exception:
        ratio = 1.0
    target = max(1, int(size * ratio))
    pixmap = pixmap.scaled(
        target,
        target,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.FastTransformation,
    )
    pixmap.setDevicePixelRatio(ratio)
    icon = QIcon(pixmap)
    _PIXEL_ICON_CACHE[key] = icon
    return icon


def grouped_inventory(inventory: dict) -> list:
    """Group owned items by registry category in display order.

    Returns a list of (category_label, [(item_name, amount, asset_path), ...]).
    Items the registry doesn't know about fall into a trailing "Other" group so
    nothing silently disappears from the bank.
    """
    buckets: dict = {cat: [] for cat in _ITEM_CATEGORY_ORDER}
    other: list = []
    for name in sorted(inventory.keys()):
        amount = inventory.get(name, 0) or 0
        if amount <= 0:
            continue
        definition = _item_def_for(name)
        asset_path = definition.asset_path if definition is not None else None
        row = (name, amount, asset_path)
        if definition is not None and definition.category in buckets:
            buckets[definition.category].append(row)
        else:
            other.append(row)
    groups: list = []
    for cat in _ITEM_CATEGORY_ORDER:
        if buckets[cat]:
            groups.append((_ITEM_CATEGORY_LABELS[cat], buckets[cat]))
    if other:
        groups.append(("Other", other))
    return groups


# Built once: storage_key -> ItemDefinition (category + asset_path lookups).
_ITEM_DEFS_BY_KEY = item_definitions_by_storage_key(ITEM_DEFINITIONS)

def get_config_bool(key: str, default: bool = True) -> bool:
    """Safely read a boolean config from Anki's profile; fallback to default when unavailable.
    This helper avoids importing aqt in callers and is easy to monkeypatch in tests.
    """
    try:
        if mw and getattr(mw, 'col', None):
            return bool(mw.col.get_config(key, default))
    except Exception:
        pass
    return bool(default)

_SMITH_EXPANDED_CONFIG_KEY = "ankiscape_smith_expanded_tiers"


def smith_expanded_tiers() -> set:
    """Return the set of Smithing metal-tier groups the user has expanded.

    Persisted as a plain list in Anki's profile config so the Smithing panel can
    open with the same groups expanded across sessions. Returns an empty set
    (everything collapsed) when config is unavailable, e.g. in headless tests.
    """
    try:
        if mw and getattr(mw, 'col', None):
            value = mw.col.get_config(_SMITH_EXPANDED_CONFIG_KEY, [])
            if isinstance(value, (list, tuple)):
                return {str(tier) for tier in value}
    except Exception:
        pass
    return set()


def set_smith_tier_expanded(tier: str, expanded: bool) -> None:
    """Persist a single Smithing metal-tier group's expand/collapse state."""
    try:
        if not (mw and getattr(mw, 'col', None)):
            return
        current = smith_expanded_tiers()
        if expanded:
            current.add(tier)
        else:
            current.discard(tier)
        mw.col.set_config(_SMITH_EXPANDED_CONFIG_KEY, sorted(current))
    except Exception:
        pass


_CRAFT_EXPANDED_CONFIG_KEY = "ankiscape_craft_expanded_families"


def craft_expanded_families() -> set:
    """Return the set of Crafting family groups the user has expanded.

    The Crafting panel groups recipes by family (Gem cutting, Pottery,
    Jewellery, ...). This mirrors the Smithing tier persistence so the panel
    reopens with the same families expanded across sessions; returns an empty
    set (everything collapsed) when config is unavailable, e.g. headless tests.
    """
    try:
        if mw and getattr(mw, 'col', None):
            value = mw.col.get_config(_CRAFT_EXPANDED_CONFIG_KEY, [])
            if isinstance(value, (list, tuple)):
                return {str(family) for family in value}
    except Exception:
        pass
    return set()


def set_craft_family_expanded(family: str, expanded: bool) -> None:
    """Persist a single Crafting family group's expand/collapse state."""
    try:
        if not (mw and getattr(mw, 'col', None)):
            return
        current = craft_expanded_families()
        if expanded:
            current.add(family)
        else:
            current.discard(family)
        mw.col.set_config(_CRAFT_EXPANDED_CONFIG_KEY, sorted(current))
    except Exception:
        pass


def is_floating_xp_enabled() -> bool:
    """Return True if floating XP popups are enabled (default True)."""
    return get_config_bool("ankiscape_floating_xp_enabled", True)

def is_popups_enabled() -> bool:
    """Return True if achievement/level-up popups are enabled (default True)."""
    return get_config_bool("ankiscape_popups_enabled", True)

def migrate_legacy_settings() -> None:
    """One-time migration from legacy setting keys to the current schema.
    - ankiscape_hud_progress_enabled -> ankiscape_review_hud_enabled (only if new key unset).
    Safe to call multiple times; it won't override explicit user choices.
    """
    try:
        if mw and getattr(mw, 'col', None):
            # Only migrate if the old key exists (value not None) and the new key hasn't been set.
            try:
                old_val = mw.col.get_config("ankiscape_hud_progress_enabled")  # type: ignore[call-arg]
            except TypeError:
                # Older get_config requires a default; use sentinel None to detect existence
                old_val = mw.col.get_config("ankiscape_hud_progress_enabled", None)
            new_exists = mw.col.get_config("ankiscape_review_hud_enabled", None) is not None
            if old_val is not None and not new_exists:
                mw.col.set_config("ankiscape_review_hud_enabled", bool(old_val))
    except Exception:
        # Never let migration issues impact runtime
        pass

def is_main_menu_open() -> bool:
    """Return True if the consolidated main menu dialog is currently visible."""
    try:
        dlg = _MAIN_MENU_CTX.get("dialog")
        return bool(dlg) and getattr(dlg, "isVisible", lambda: False)()
    except Exception:
        return False

def focus_main_menu_if_open() -> bool:
    """If the main menu is open, bring it to front and return True; otherwise False."""
    try:
        dlg = _MAIN_MENU_CTX.get("dialog")
        if dlg and getattr(dlg, "isVisible", lambda: False)():
            try:
                if hasattr(dlg, "raise_"):
                    dlg.raise_()
                if hasattr(dlg, "activateWindow"):
                    dlg.activateWindow()
            except Exception:
                pass
            return True
    except Exception:
        pass
    return False

def refresh_skill_availability(
    can_smelt_any_bar: bool,
    can_craft_any_item: bool,
    can_fletch_any_item: bool = False,
    can_firemake_any_item: bool = False,
    can_hunt_any_item: bool = False,
    can_cook_any_item: bool = False,
    can_runecraft_any_item: bool = False,
):
    """Auto-enable processing-skill buttons when they become available while the menu is open.
    Never auto-selects the skill; users must choose it explicitly. Only enables; does not disable.

    Optional processing-skill booleans default to False so older two-argument
    callers keep working until they pass the newer skills too.
    """
    try:
        # Smithing
        s_btn = _MAIN_MENU_CTX.get("smith_btn")
        if s_btn is not None and can_smelt_any_bar and not s_btn.isEnabled():
            s_btn.setEnabled(True)
            s_btn.setToolTip("Smithing")
        # Crafting
        c_btn = _MAIN_MENU_CTX.get("craft_btn")
        if c_btn is not None and can_craft_any_item and not c_btn.isEnabled():
            c_btn.setEnabled(True)
            c_btn.setToolTip("Crafting")
        # Fletching
        f_btn = _MAIN_MENU_CTX.get("fletch_btn")
        if f_btn is not None and can_fletch_any_item and not f_btn.isEnabled():
            f_btn.setEnabled(True)
            f_btn.setToolTip("Fletching")
        # Firemaking
        fm_btn = _MAIN_MENU_CTX.get("firemaking_btn")
        if fm_btn is not None and can_firemake_any_item and not fm_btn.isEnabled():
            fm_btn.setEnabled(True)
            fm_btn.setToolTip("Firemaking")
        # Hunter
        h_btn = _MAIN_MENU_CTX.get("hunter_btn")
        if h_btn is not None and can_hunt_any_item and not h_btn.isEnabled():
            h_btn.setEnabled(True)
            h_btn.setToolTip("Hunter")
        # Cooking
        cook_btn = _MAIN_MENU_CTX.get("cooking_btn")
        if cook_btn is not None and can_cook_any_item and not cook_btn.isEnabled():
            cook_btn.setEnabled(True)
            cook_btn.setToolTip("Cooking")
        # Runecrafting
        rc_btn = _MAIN_MENU_CTX.get("runecrafting_btn")
        if rc_btn is not None and can_runecraft_any_item and not rc_btn.isEnabled():
            rc_btn.setEnabled(True)
            rc_btn.setToolTip("Runecrafting")
        # Clear warning text if any became available
        if (
            (s_btn is not None and s_btn.isEnabled())
            or (c_btn is not None and c_btn.isEnabled())
            or (f_btn is not None and f_btn.isEnabled())
            or (fm_btn is not None and fm_btn.isEnabled())
            or (h_btn is not None and h_btn.isEnabled())
            or (cook_btn is not None and cook_btn.isEnabled())
            or (rc_btn is not None and rc_btn.isEnabled())
        ):
            warn = _MAIN_MENU_CTX.get("warn_label")
            if warn is not None and hasattr(warn, "setText"):
                warn.setText("")
    except Exception:
        pass


def compute_level_progress(level: int, exp: float, exp_table: list) -> tuple[int, float, int]:
    """Pure helper for computing percent, remaining XP, and target level.
    Returns (percent, xp_remaining, target_level). Clamps values sensibly.
    - At max level (99 or end of table), always return 100% and 0 remaining.
    """
    try:
        lvl = max(1, int(level))
        xp = float(exp or 0)
        table_len = len(exp_table)

        # If at or above the maximum supported level, treat progress as complete.
        # Many games cap at 99; also guard when lvl maps to the last index of the table.
        if lvl >= 99 or lvl >= table_len:
            return 100, 0.0, 99

        # Compute thresholds for the current level segment
        prev = float(exp_table[lvl - 1]) if (lvl - 1) < table_len else 0.0
        nxt = float(exp_table[lvl]) if lvl < table_len else prev

        # If thresholds are degenerate (e.g., at end), treat as maxed
        if nxt <= prev:
            return 100, 0.0, 99

        # Clamp percent to [0, 100] and remaining to >= 0
        span = nxt - prev
        pct_float = ((xp - prev) / span) * 100.0
        if xp >= nxt:
            pct = 100
            remain = 0.0
        else:
            pct = int(max(0.0, min(100.0, pct_float)))
            remain = max(0.0, nxt - xp)

        target_lv = min(lvl + 1, 99)
        return pct, remain, target_lv
    except Exception:
        # Fallback on error: show safe defaults and a reasonable next target
        try:
            safe_lvl = max(1, int(level))
        except Exception:
            safe_lvl = 1
        return 0, 0.0, min(safe_lvl + 1, 99)


# Maps a skill id to the data table that resolves its current-target id into a
# human-readable display name. Registry-driven (skill_registry supplies the
# current_target_key/default_target) so the HUD label is just a literal echo of
# whatever the player picked in the menu — no per-skill verb phrasing.
_SKILL_TARGET_TABLES = {
    "mining": ORE_DATA,
    "woodcutting": TREE_DATA,
    "smithing": SMITHING_DATA,
    "crafting": CRAFTING_DATA,
    "fletching": FLETCHING_DATA,
    "firemaking": FIREMAKING_DATA,
    "fishing": FISHING_DATA,
    "hunter": HUNTER_DATA,
    "cooking": COOKING_DATA,
    "runecrafting": RUNECRAFTING_DATA,
}


def current_target_display_name(skill: str, player_data: dict) -> Optional[str]:
    """Return the display name of the skill's currently selected target.

    Returns None when the skill has no selectable target (e.g. combat/support)
    or cannot be resolved, so callers can simply hide the label.
    """
    if skill == "Quests":
        quest_id = player_data.get("current_quest")
        quest = QUEST_DATA.get(quest_id) if isinstance(quest_id, str) else None
        if isinstance(quest, dict):
            return str(quest.get("display_name", quest_id))
        return None
    if skill == _COMBAT_HUB_NAME:
        target_id = player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
        enemy = COMBAT_ENEMY_DATA.get(target_id) if isinstance(target_id, str) else None
        if isinstance(enemy, dict):
            return str(enemy.get("display_name", target_id))
        return None
    sd = get_skill(skill or "")
    if sd is None or sd.current_target_key is None:
        return None
    target_id = player_data.get(sd.current_target_key) or sd.default_target
    if not target_id:
        return None
    table = _SKILL_TARGET_TABLES.get(sd.id)
    spec = table.get(target_id) if table else None
    if isinstance(spec, dict):
        return str(spec.get("display_name", target_id))
    return str(target_id)


# UI Classes
if HAS_QT:
    # Shared HUD theme
    _HUD_ACCENT = "#4CAF50"  # Material green (player health)
    _HUD_ENEMY = "#E53935"  # Material red (enemy health)
    _HUD_BG = "rgba(20, 20, 20, 180)"
    _HUD_BORDER = "rgba(255, 255, 255, 60)"

    class ReviewHUD(QWidget):
        """A compact overlay shown on the review screen (lower center).
        Displays current skill (icon + name), level, and progress to next level.
        """
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            # Important: keep this as a child widget inside Anki's main window.
            # Avoid ToolTip/Window flags that would make it a top-level, always-on-top window
            # and leak over other macOS apps.
            try:
                self.setWindowFlags(Qt.WindowType.Widget)
            except Exception:
                pass
            self.setAutoFillBackground(False)
            self.setObjectName("AnkiScapeReviewHUD")

            # Layout
            root = QHBoxLayout(self)
            root.setContentsMargins(12, 10, 12, 10)
            root.setSpacing(10)

            self.icon_lbl = QLabel()
            self.icon_lbl.setFixedSize(28, 28)
            root.addWidget(self.icon_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

            info = QVBoxLayout()
            info.setContentsMargins(0, 0, 0, 0)
            info.setSpacing(4)
            self.title_lbl = QLabel("Skill")
            self.title_lbl.setStyleSheet("color: white; font-weight: 600;")
            info.addWidget(self.title_lbl)

            # Progress row
            self.progress = QProgressBar()
            self.progress.setTextVisible(False)
            self.progress.setFixedHeight(12)
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            self.progress.setStyleSheet(
                f"""
                QProgressBar {{
                    background-color: rgba(255,255,255,0.15);
                    border: 1px solid {_HUD_BORDER};
                    border-radius: 6px;
                }}
                QProgressBar::chunk {{
                    background-color: {_HUD_ACCENT};
                    border-radius: 5px;
                }}
                """
            )
            info.addWidget(self.progress)

            self.sub_lbl = QLabel("")
            self.sub_lbl.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 11px;")
            info.addWidget(self.sub_lbl)

            # Small line echoing the target currently selected in the menu
            # (e.g. "Pot (unfired)"). Updated live via set_data whenever the
            # player changes their selection.
            self.target_lbl = QLabel("")
            self.target_lbl.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 10px;")
            info.addWidget(self.target_lbl)

            # Combat-only: a second health bar for the enemy, and a chip line
            # naming the skills the current attack style trains plus the running
            # kill count. Hidden for every non-combat skill (see set_data).
            self.enemy_progress = QProgressBar()
            self.enemy_progress.setTextVisible(False)
            self.enemy_progress.setFixedHeight(8)
            self.enemy_progress.setRange(0, 100)
            self.enemy_progress.setValue(0)
            self.enemy_progress.setStyleSheet(
                f"""
                QProgressBar {{
                    background-color: rgba(255,255,255,0.15);
                    border: 1px solid {_HUD_BORDER};
                    border-radius: 5px;
                }}
                QProgressBar::chunk {{
                    background-color: {_HUD_ENEMY};
                    border-radius: 4px;
                }}
                """
            )
            info.addWidget(self.enemy_progress)

            self.chips_lbl = QLabel("")
            self.chips_lbl.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 10px;")
            info.addWidget(self.chips_lbl)

            root.addLayout(info, 1)

            # Aesthetic container style
            self.setStyleSheet(
                f"""
                QWidget#AnkiScapeReviewHUD {{
                    background: {_HUD_BG};
                    border: 1px solid {_HUD_BORDER};
                    border-radius: 10px;
                }}
                """
            )

            # Shadow for better contrast if available
            try:
                from aqt.qt import QGraphicsDropShadowEffect  # type: ignore
                shadow = QGraphicsDropShadowEffect(self)
                shadow.setBlurRadius(18)
                shadow.setOffset(0, 2)
                shadow.setColor(Qt.GlobalColor.black)
                self.setGraphicsEffect(shadow)
            except Exception:
                pass

            # Track parent resize/move to keep position
            try:
                if parent is not None:
                    parent.installEventFilter(self)
            except Exception:
                pass

            self.hide()

        def _skill_icon_path(self, skill: str) -> Optional[str]:
            # Registry-driven: resolves icon/<skill_id>_icon.png for any playable
            # skill (Fletching included) instead of a fixed four-skill map.
            return skill_icon_path_for(skill)

        def _placeholder_icon_path(self) -> Optional[str]:
            p = os.path.join(current_dir, "crafteditems", "None.png")
            return p if os.path.exists(p) else None

        def set_data(self, player_data: dict, skill: str) -> None:
            """Update HUD content from player data and currently active skill."""
            skill = skill or "None"
            combat_status = combat_status_summary_pure(player_data)
            # Enemy bar + chips are combat-only; keep them hidden unless the
            # combat branch below explicitly turns them on.
            self.enemy_progress.setVisible(False)
            self.chips_lbl.setVisible(False)
            if skill in _UTILITY_SKILL_NAMES:
                # Utility / Activities has no level or XP; show the active activity
                # and make the no-XP nature explicit instead of a progress bar.
                activity_key = player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
                spec = UTILITY_ACTIVITY_DATA.get(activity_key, {})
                activity_name = str(spec.get("display_name", "Material prep"))
                ip = skill_icon_path_for(skill) or self._placeholder_icon_path()
                if ip:
                    pm = QPixmap(ip)
                    self.icon_lbl.setPixmap(pm.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    self.icon_lbl.clear()
                self.title_lbl.setText(_UTILITY_HUB_NAME)
                status_suffix = f" • {combat_status}" if combat_status else ""
                self.sub_lbl.setText(f"{activity_name} • material prep (no XP){status_suffix}")
                try:
                    self.progress.setVisible(False)
                    self.sub_lbl.setVisible(True)
                    # Activity name already shown in sub_lbl for Utility.
                    self.target_lbl.setText("")
                    self.target_lbl.setVisible(False)
                except Exception:
                    pass
                self.adjustSize()
                self._reposition()
                self.show()
                return
            if skill == _COMBAT_HUB_NAME:
                state = combat_hud_state_pure(player_data)
                ip = os.path.join(current_dir, "icon", "attack_icon.png")
                if not os.path.exists(ip):
                    ip = self._placeholder_icon_path()
                if ip:
                    pm = QPixmap(ip)
                    self.icon_lbl.setPixmap(pm.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    self.icon_lbl.clear()
                self.title_lbl.setText(f"Combat — Lv {state['combat_level']}")

                # Player health bar
                self.progress.setVisible(True)
                self.progress.setValue(state["player_pct"])
                status_suffix = f" • {state['status']}" if state["status"] else ""
                self.sub_lbl.setVisible(True)
                self.sub_lbl.setText(
                    f"You {state['player_lifepoints']}/{state['player_max_lifepoints']} LP{status_suffix}"
                )

                # Enemy name + health bar
                self.target_lbl.setText(state["enemy_name"])
                self.target_lbl.setVisible(True)
                self.enemy_progress.setVisible(True)
                self.enemy_progress.setValue(state["enemy_pct"])

                # Chip line: which skills this attack style trains, plus kills so far
                trains = " • ".join(state["trained_skills"])
                kills = state["kills_total"]
                kill_txt = f"⚔ {kills} {'kill' if kills == 1 else 'kills'}"
                self.chips_lbl.setText(f"Trains {trains}   {kill_txt}")
                self.chips_lbl.setVisible(True)

                self.adjustSize()
                self._reposition()
                self.show()
                return
            if skill == "Quests":
                quest_id = player_data.get("current_quest")
                quest = QUEST_DATA.get(quest_id) if isinstance(quest_id, str) else None
                state = quest_state_pure(player_data, quest_id) if isinstance(quest_id, str) else {"progress": 0, "completed": False}
                total = int(quest.get("stages", 1) if isinstance(quest, dict) else 1)
                progress = int(state.get("progress", 0) or 0)
                quest_name = str(quest.get("display_name", "Quest") if isinstance(quest, dict) else "Quest")
                ip = os.path.join(current_dir, "icon", "achievement_icon.png")
                if os.path.exists(ip):
                    pm = QPixmap(ip)
                    self.icon_lbl.setPixmap(pm.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    self.icon_lbl.clear()
                self.title_lbl.setText("Quests")
                self.progress.setVisible(True)
                self.progress.setValue(100 if state.get("completed") else int((progress / max(1, total)) * 100))
                self.sub_lbl.setVisible(True)
                quest_status = "Completed" if state.get("completed") else f"Stage {progress}/{total}"
                if combat_status:
                    quest_status = f"{quest_status} • {combat_status}"
                self.sub_lbl.setText(quest_status)
                self.target_lbl.setText(quest_name)
                self.target_lbl.setVisible(True)
                self.adjustSize()
                self._reposition()
                self.show()
                return
            if skill not in playable_review_skill_names():
                # No skill selected: show placeholder state
                ip = self._placeholder_icon_path()
                if ip:
                    pm = QPixmap(ip)
                    self.icon_lbl.setPixmap(pm.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    self.icon_lbl.clear()
                self.title_lbl.setText("No skill selected")
                self.progress.setValue(0)
                no_skill_status = "Open AnkiScape menu to choose a skill"
                if combat_status:
                    no_skill_status = f"{no_skill_status} • {combat_status}"
                self.sub_lbl.setText(no_skill_status)
                # Always show progress/subtext when HUD is enabled
                try:
                    self.progress.setVisible(True)
                    self.sub_lbl.setVisible(True)
                    self.target_lbl.setText("")
                    self.target_lbl.setVisible(False)
                except Exception:
                    pass
                self.adjustSize()
                self._reposition()
                self.show()
                return

            # Icon
            ip = self._skill_icon_path(skill)
            if ip:
                pm = QPixmap(ip)
                self.icon_lbl.setPixmap(pm.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.icon_lbl.clear()

            level_key = f"{skill.lower()}_level"
            exp_key = f"{skill.lower()}_exp"
            level = int(player_data.get(level_key, 1) or 1)
            exp = float(player_data.get(exp_key, 0) or 0)
            self.title_lbl.setText(f"{skill} — Lv {level}")

            # Compute progress within current level via pure helper
            pct, remain, target_lv = compute_level_progress(level, exp, EXP_TABLE)
            self.progress.setValue(pct)
            progress_text = f"{pct}% to Lv {target_lv} • {remain:,.0f} XP to next"
            if combat_status:
                progress_text = f"{progress_text} • {combat_status}"
            self.sub_lbl.setText(progress_text)

            # Echo the currently selected menu target (e.g. "Pot (unfired)").
            target_name = current_target_display_name(skill, player_data)

            # Always show progress/subtext when HUD is enabled
            try:
                self.progress.setVisible(True)
                self.sub_lbl.setVisible(True)
                if target_name:
                    self.target_lbl.setText(target_name)
                    self.target_lbl.setVisible(True)
                else:
                    self.target_lbl.setText("")
                    self.target_lbl.setVisible(False)
            except Exception:
                pass

            self.adjustSize()
            self._reposition()
            self.show()

        def _reposition(self) -> None:
            try:
                par = self.parent() if self.parent() is not None else mw
                if par is None:
                    return
                pw = par.width()
                ph = par.height()
                self.adjustSize()
                w = min(max(self.width(), 360), 520)
                h = self.height()
                x = int((pw - w) / 2)
                # Keep clear of bottom actions/status; give more breathing room
                y = int(ph - h - 72)
                self.setFixedWidth(w)
                self.move(x, y)
            except Exception:
                pass

        def eventFilter(self, obj, event):  # type: ignore[override]
            try:
                et = event.type()
                if et in (QEvent.Type.Resize, QEvent.Type.Move, QEvent.Type.Show):
                    self._reposition()
            except Exception:
                pass
            return False

    class ExpPopup(QLabel):
        """Floating XP indicator that fades and floats above the HUD (lower center)."""
        def __init__(self, parent):
            super().__init__(parent)
            self.setStyleSheet(
                f"""
                QLabel {{
                    background: {_HUD_BG};
                    color: white;
                    border: 1px solid {_HUD_BORDER};
                    border-radius: 10px;
                    padding: 6px 10px;
                    font-weight: 700;
                }}
                """
            )
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.hide()

        def show_exp(self, exp):
            # Format like +25 XP, color accent via left border
            self.show_text(f"+{int(exp)} XP")

        def show_text(self, text: str):
            # Generic floating "ghost" indicator. Used for XP gains and, for no-XP
            # Utility/Activities, for item gains like "+28 Flax" so the player gets
            # the same confirmation that a review action actually happened.
            self.setText(str(text))
            self.adjustSize()
            self.show()

            # Position: centered horizontally, just above the HUD
            try:
                par = self.parent() if self.parent() is not None else mw
                hud = _REVIEW_HUD
                base_y = (hud.y() - 14) if (hud and hud.isVisible()) else (par.height() - 140)
                x = int((par.width() - self.width()) / 2)
                y = int(base_y)
                self.move(x, y)
            except Exception:
                # Fallback to lower center
                self.move(max(10, int((self.parent().width() - self.width()) / 2)), self.parent().height() - 140)

            # Animations
            self.opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self.opacity_effect)
            self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_animation.setDuration(1800)
            self.fade_animation.setStartValue(1.0)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.fade_animation.finished.connect(self.hide)

            self.float_animation = QPropertyAnimation(self, b"pos")
            self.float_animation.setDuration(1800)
            start_pos = self.pos()
            end_pos = start_pos - QPoint(0, 36)
            self.float_animation.setStartValue(start_pos)
            self.float_animation.setEndValue(end_pos)
            self.float_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.fade_animation.start()
            self.float_animation.start()
else:
    # Minimal placeholder to keep references safe during tests
    class ExpPopup:
        def __init__(self, parent):
            pass

        def show_exp(self, exp):
            pass

        def show_text(self, text):
            pass

    class ReviewHUD:
        def __init__(self, parent=None):
            pass
        def set_data(self, player_data: dict, skill: str) -> None:
            pass

# UI Functions
# ...existing code...
# Move all dialog, popup, and menu functions here from __init__.py

# --- Review HUD management ---
_REVIEW_HUD = None  # type: ignore

def _cleanup_extra_huds() -> None:
    """Hide and delete any stray HUD widgets from prior versions or reloads.
    Ensures only a single child HUD exists under mw and no top-level HUDs remain.
    """
    if not HAS_QT:
        return
    try:
        try:
            from aqt.qt import QApplication  # type: ignore
        except Exception:
            QApplication = None  # type: ignore
        # Remove top-level HUDs that may have been created with ToolTip flags
        if QApplication is not None:
            for w in QApplication.topLevelWidgets():
                try:
                    if getattr(w, "objectName", lambda: "")() == "AnkiScapeReviewHUD":
                        if _REVIEW_HUD is None or w is not _REVIEW_HUD:
                            try:
                                w.hide()
                            except Exception:
                                pass
                            try:
                                w.deleteLater()
                            except Exception:
                                pass
                except Exception:
                    pass
        # Also remove duplicate children under mw
        par = mw
        if par is not None:
            from aqt.qt import QWidget as _QW  # type: ignore
            for child in par.findChildren(_QW, "AnkiScapeReviewHUD"):
                if _REVIEW_HUD is None or child is not _REVIEW_HUD:
                    try:
                        child.hide()
                    except Exception:
                        pass
                    try:
                        child.deleteLater()
                    except Exception:
                        pass
    except Exception:
        pass

def ensure_review_hud() -> None:
    """Create the Review HUD if missing and attach to mw."""
    global _REVIEW_HUD
    try:
        if not HAS_QT:
            return
        # Proactively clean up any leftover HUD windows from previous runs
        _cleanup_extra_huds()
        if _REVIEW_HUD is None:
            parent = mw
            if parent is None:
                return
            _REVIEW_HUD = ReviewHUD(parent)
            try:
                # Ensure correct parenting in case older instances detached
                _REVIEW_HUD.setParent(parent)
            except Exception:
                pass
        # ensure on top and visible (content set by update call)
        try:
            _REVIEW_HUD.raise_()
        except Exception:
            pass
    except Exception:
        pass

def update_review_hud(player_data: dict, current_skill: str) -> None:
    """Update and show the Review HUD based on current data."""
    try:
        if not HAS_QT:
            return
        # Respect setting to fully disable the review HUD visuals
        if not get_config_bool("ankiscape_review_hud_enabled", True):
            try:
                if _REVIEW_HUD is not None and hasattr(_REVIEW_HUD, "hide"):
                    _REVIEW_HUD.hide()
            except Exception:
                pass
            return
        ensure_review_hud()
        if _REVIEW_HUD is not None:
            _REVIEW_HUD.set_data(player_data, current_skill)
    except Exception:
        pass

def hide_review_hud() -> None:
    """Hide the HUD if it exists (used outside of review screens)."""
    try:
        if _REVIEW_HUD is not None and hasattr(_REVIEW_HUD, "hide"):
            _REVIEW_HUD.hide()
    except Exception:
        pass

def show_error_message(title: str, message: str):
    """Centralized error dialog helper."""
    error_dialog = QMessageBox(mw)
    error_dialog.setIcon(QMessageBox.Icon.Warning)
    # Force the standard warning glyph. On macOS QMessageBox otherwise falls back
    # to the host app's icon (the Python/Anki "folder" the user saw) for the body
    # icon, which looks like a bug. The style's SP_MessageBoxWarning is a proper
    # caution triangle on every platform.
    try:
        from aqt.qt import QStyle, QApplication
        style = (mw.style() if mw is not None else None) or QApplication.style()
        warning = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        pm = warning.pixmap(48, 48)
        if not pm.isNull():
            error_dialog.setIconPixmap(pm)
    except Exception:
        pass
    error_dialog.setWindowTitle(title)
    error_dialog.setText(message)
    error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    error_dialog.exec()


def show_level_up_dialog(skill: str):
    """Level-up dialog with a skill icon."""
    dialog = QDialog(mw)
    dialog.setWindowTitle("Level Up!")
    dialog.setFixedSize(380, 200)
    layout = QVBoxLayout()

    # Icon row (registry-driven so new skills like Fletching show their icon)
    icon_path = skill_icon_path_for(skill)
    if icon_path:
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

    msg = QLabel(f"Congratulations! You've advanced a {skill} level!")
    msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(msg)

    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)
    layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

    dialog.setLayout(layout)
    dialog.exec()


def show_achievement_dialog(achievement: str, data: dict):
    """Achievement dialog with an icon."""
    dialog = QDialog(mw)
    dialog.setWindowTitle("Achievement Unlocked!")
    dialog.setFixedSize(420, 240)
    layout = QVBoxLayout()

    # Try a specific icon based on achievement name, otherwise use generic
    icon_path = os.path.join(current_dir, "icon", f"{achievement.lower().replace(' ', '_')}.png")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(current_dir, "icon", "achievement_icon.png")
    if os.path.exists(icon_path):
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

    title = QLabel(achievement)
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 16px; font-weight: bold;")
    layout.addWidget(title)

    desc = QLabel(data.get("description", ""))
    desc.setWordWrap(True)
    layout.addWidget(desc, alignment=Qt.AlignmentFlag.AlignCenter)

    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)
    layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

    dialog.setLayout(layout)
    dialog.exec()


def create_menu(on_main_menu):
    """Create a single AnkiScape > Menu entry that opens the consolidated window."""
    menu = QMenu("AnkiScape", mw)
    mw.form.menubar.addMenu(menu)
    main_action = menu.addAction("Menu")
    main_action.triggered.connect(on_main_menu)


def update_menu_visibility(current_skill: str):
    """No-op: single consolidated menu item is always visible."""
    return


def _combat_loadout_summary_text(player_data: dict) -> str:
    summary = combat_supply_loadout_summary_pure(player_data)

    def _mapping_text(mapping: object) -> str:
        if not isinstance(mapping, dict) or not mapping:
            return "none loaded"
        return ", ".join(f"{item} x{amount}" for item, amount in mapping.items())

    return (
        f"Food: {summary.get('food_loaded', 0)} loaded\n"
        f"Potions: {_mapping_text(summary.get('potions_loaded_items'))}\n"
        f"Stat potions: {_mapping_text(summary.get('stat_potions_loaded_items'))}\n"
        f"Ammo: {_mapping_text(summary.get('ammo_loaded'))}\n"
        f"Runes: {_mapping_text(summary.get('runes_loaded'))}"
    )


def show_main_menu(
    player_data: dict,
    current_skill: str,
    can_smelt_any_bar: bool,
    on_save_skill,
    on_set_ore,
    on_set_tree,
    on_set_bar,
    on_set_craft,
    on_set_smith=None,
    on_set_fletch=None,
    on_set_firemaking=None,
    on_set_fishing=None,
    on_set_hunter=None,
    on_set_cooking=None,
    on_set_runecrafting=None,
    on_set_utility=None,
    on_set_carried_keep_drop=None,
    carried_keep_drop_state=None,
    on_set_loot_threshold=None,
    on_set_loot_override=None,
    loot_override_rows=(),
    carried_pack_target_active=False,
    on_set_carried_advanced=None,
    carried_advanced_state=False,
    get_carried_layout_cells=None,
    on_add_to_carried_layout=None,
    on_clear_carried_layout=None,
    on_set_combat=None,
    on_set_combat_style=None,
    on_set_combat_spell=None,
    on_set_combat_auto_eat_threshold=None,
    on_set_combat_auto_eat_food=None,
    on_set_combat_pack_mode=None,
    on_refill_combat_loadout=None,
    on_unload_combat_loadout=None,
    on_reclaim_death_office=None,
    on_set_quest=None,
    on_set_quest_route_choice=None,
    on_claim_reward=None,
    on_set_floating_enabled=None,
    on_set_floating_position=None,
    on_equip_item=None,
    on_unequip_slot=None,
    on_discard_item=None,
    on_consume_item=None,
):
    """Show the consolidated window.

    The top bar is limited to global sections (Skills, Bank, Stats,
    Achievements, Settings). Per-skill navigation lives inside the Skills hub
    as category -> skill -> target list, driven by the skill registry.
    Callbacks apply changes and handle persistence in the caller.
    """
    _debug_log("ui.show_main_menu: enter")
    dialog = QDialog(mw)
    dialog.setWindowTitle("AnkiScape Menu")
    dialog.setMinimumWidth(720)
    dialog.setMinimumHeight(620)

    layout = QVBoxLayout()
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    tabs = QTabWidget()
    tabs.setDocumentMode(True)

    # ---- Skills hub (registry-driven) -------------------------------------
    # The top bar now holds global sections only. Skill navigation lives inside
    # this single tab as category filter -> skill list -> target list. Normal
    # mode shows playable skills only; developer mode also surfaces the planned
    # 2011-era catalog so future skills can be inspected before they are coded.
    skills_tab = QWidget()
    s_layout = QVBoxLayout(skills_tab)
    s_layout.setContentsMargins(12, 12, 12, 12)
    s_layout.setSpacing(8)

    # Active-skill status line. ``warn`` is reused by the live availability hook
    # (refresh_skill_availability) so it must stay a stable reference.
    status_row = QWidget()
    status_layout = QHBoxLayout(status_row)
    status_layout.setContentsMargins(0, 0, 0, 0)
    status_layout.setSpacing(8)
    active_label = QLabel("")
    active_label.setStyleSheet("font-weight: 600; color: palette(text);")
    stop_btn = QPushButton("Stop training")
    stop_btn.setToolTip("Stop training (no skill earns progress during reviews)")
    stop_btn.setStyleSheet(
        "QPushButton { padding: 5px 12px; border: 1px solid #ff5c5c;"
        " border-radius: 6px; color: #ff8a8a; background: rgba(255,92,92,0.12); }"
        " QPushButton:hover { background: rgba(255,92,92,0.22); }"
        # Disabled: dim_text_css for the label (palette(mid) is a border role and
        # vanishes in dark mode); palette(mid) stays only on the border.
        f" QPushButton:disabled {{ color: {dim_text_css(stop_btn)}; border-color: palette(mid);"
        " background: transparent; }"
    )
    status_layout.addWidget(active_label)
    status_layout.addStretch(1)
    status_layout.addWidget(stop_btn)
    s_layout.addWidget(status_row)
    warn = QLabel("")
    warn.setStyleSheet("color: red;")
    s_layout.addWidget(warn)

    include_planned = get_config_bool("ankiscape_developer_mode", False)
    hub = build_skill_hub(include_planned=include_planned)

    combat_card = SkillCardView(
        skill_id="combat",
        display_name=_COMBAT_HUB_NAME,
        category="combat",
        implemented=True,
        selectable_for_review=True,
    )
    combat_inserted = False
    combat_hub = []
    for category in hub:
        if category.category_id == "combat":
            skills = tuple(skill for skill in category.skills if skill.display_name != _COMBAT_HUB_NAME)
            combat_hub.append(
                CategoryView(
                    category_id=category.category_id,
                    display_name=category.display_name,
                    skills=(combat_card,) + skills,
                )
            )
            combat_inserted = True
        else:
            combat_hub.append(category)
    if not combat_inserted:
        combat_hub.append(CategoryView(category_id="combat", display_name=_COMBAT_HUB_NAME, skills=(combat_card,)))
    hub = tuple(combat_hub)

    # Append a synthetic Utility / Activities category. It is not a registry
    # skill (no XP/level), so it is injected at the view layer and rendered with
    # its own no-XP target list rather than the level-based skill panel.
    utility_card = SkillCardView(
        skill_id="utility",
        display_name=_UTILITY_HUB_NAME,
        category="utility",
        implemented=True,
        selectable_for_review=True,
    )
    hub = hub + (
        CategoryView(category_id="utility", display_name=_UTILITY_HUB_NAME, skills=(utility_card,)),
    )

    _active_choices = set(playable_review_skill_names()) | {_COMBAT_HUB_NAME, "Quests"} | _UTILITY_SKILL_NAMES

    # Mutable selection state (nested closures cannot rebind plain locals).
    state = {
        "category": first_category_id(hub),
        "skill": "",
        "active": current_skill if current_skill in _active_choices else "None",
    }

    # ---- availability + active-skill helpers ----
    def _craft_available() -> bool:
        try:
            level = player_data.get("crafting_level", 1)
            inv = player_data.get("inventory", {})
            return any(can_craft_item_pure(level, inv, n, CRAFTING_DATA) for n in CRAFTING_DATA)
        except Exception:
            return False

    def _fletch_available() -> bool:
        try:
            return any(
                not fletching_target_locked_reasons_pure(player_data, target, FLETCHING_DATA, QUEST_UNLOCK_RULES)
                for target in FLETCHING_DATA
            )
        except Exception:
            return False

    def _firemaking_available() -> bool:
        try:
            return any(
                not firemaking_target_locked_reasons_pure(player_data, target, FIREMAKING_DATA, QUEST_UNLOCK_RULES)
                for target in FIREMAKING_DATA
            )
        except Exception:
            return False

    def _hunter_available() -> bool:
        try:
            return any(
                not hunter_target_locked_reasons_pure(player_data, target, HUNTER_DATA, QUEST_UNLOCK_RULES)
                for target in HUNTER_DATA
            )
        except Exception:
            return False

    def _cooking_available() -> bool:
        try:
            return any(
                not cooking_target_locked_reasons_pure(player_data, target, COOKING_DATA, QUEST_UNLOCK_RULES)
                for target in COOKING_DATA
            )
        except Exception:
            return False

    def _runecrafting_available() -> bool:
        try:
            return can_runecraft_any_pure(player_data, RUNECRAFTING_DATA, RUNECRAFTING_POUCH_DATA, QUEST_UNLOCK_RULES)
        except Exception:
            return False

    def _combat_available() -> bool:
        try:
            return any(
                not combat_target_locked_reasons_pure(
                    player_data,
                    target,
                    COMBAT_ENEMY_DATA,
                    equipment_data=EQUIPMENT_ITEM_DATA,
                )
                for target in COMBAT_ENEMY_DATA
            )
        except Exception:
            return False

    def _skill_available(display_name: str) -> bool:
        if display_name == _COMBAT_HUB_NAME:
            return _combat_available()
        if display_name == "Smithing":
            return bool(can_smelt_any_bar)
        if display_name == "Crafting":
            return _craft_available()
        if display_name == "Fletching":
            return _fletch_available()
        if display_name == "Firemaking":
            return _firemaking_available()
        if display_name == "Hunter":
            return _hunter_available()
        if display_name == "Cooking":
            return _cooking_available()
        if display_name == "Runecrafting":
            return _runecrafting_available()
        # Utility / Activities is always trainable: gather_* activities need no
        # inputs, so there is always at least one runnable activity.
        return True

    def _refresh_active_label() -> None:
        active = state["active"]
        if active and active != "None":
            active_label.setText(f"Training: {active}")
            stop_btn.setEnabled(True)
        else:
            active_label.setText("Training: nothing selected")
            stop_btn.setEnabled(False)

    def _set_active(display_name: str) -> None:
        # Mirror the original gating: never let users train a skill they cannot
        # actually progress, and explain why instead of silently selecting it.
        if display_name == "Smithing" and not can_smelt_any_bar:
            warn.setText("You don't have enough ores to smelt any bars. Mine some ores first!")
            return
        if display_name == "Crafting" and not _craft_available():
            warn.setText("You can't craft anything yet. Gather materials or level up first!")
            return
        if display_name == "Fletching" and not _fletch_available():
            warn.setText("You can't fletch anything yet. Cut some logs or level up first!")
            return
        if display_name == "Firemaking" and not _firemaking_available():
            warn.setText("You can't burn anything yet. Cut or acquire logs first!")
            return
        if display_name == "Hunter" and not _hunter_available():
            warn.setText("You can't hunt anything yet. Gather jars/materials, complete unlocks, or level up first!")
            return
        if display_name == "Runecrafting" and not _runecrafting_available():
            warn.setText("You can't runecraft anything yet. Complete Rune Mysteries and gather access items first!")
            return
        if display_name == _COMBAT_HUB_NAME and not _combat_available():
            warn.setText("You can't fight any source-backed combat target yet.")
            return
        warn.setText("")
        state["active"] = display_name
        on_save_skill(display_name)
        _refresh_active_label()
        _render_panel()

    def _stop_training() -> None:
        warn.setText("")
        state["active"] = "None"
        on_save_skill("None")
        _refresh_active_label()
        _render_panel()

    stop_btn.clicked.connect(lambda _=False: _stop_training())

    # ---- target list builders (one per implemented skill) ----
    def _build_flat_target_list(rows: tuple[TargetRowMetadata, ...], on_select=None) -> QListWidget:
        target_list = QListWidget()
        target_list.setIconSize(QSize(28, 28))
        target_list.setAlternatingRowColors(True)
        for row in rows:
            item = QListWidgetItem(row.label)
            item.setData(Qt.ItemDataRole.UserRole, row.target_id)
            if row.icon_path and os.path.exists(row.icon_path):
                item.setIcon(QIcon(row.icon_path))
            if not row.enabled:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            item.setToolTip(row.tooltip)
            target_list.addItem(item)
            if row.current:
                target_list.setCurrentItem(item)

        def _on_target_selected(item: QListWidgetItem):
            # Skip locked rows: Qt still emits clicks/activations for disabled
            # items even though selection is blocked.
            if item and on_select is not None and (item.flags() & Qt.ItemFlag.ItemIsEnabled):
                on_select(item.data(Qt.ItemDataRole.UserRole))

        target_list.itemClicked.connect(_on_target_selected)
        target_list.itemActivated.connect(_on_target_selected)
        return target_list

    def _item_asset_paths() -> dict:
        return {
            storage_key: definition.asset_path
            for storage_key, definition in _ITEM_DEFS_BY_KEY.items()
            if definition.asset_path
        }

    def _build_grouped_target_tree(
        rows: tuple[TargetRowMetadata, ...],
        group_labels: dict,
        group_role_prefix: str,
        on_select=None,
        confirm_select=None,
        group_order: Optional[list] = None,
        expanded_groups: Optional[set] = None,
        set_group_expanded=None,
    ) -> QTreeWidget:
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setIconSize(QSize(28, 28))
        tree.setRootIsDecorated(True)
        tree.setIndentation(14)
        tree.setUniformRowHeights(True)
        tree.setStyleSheet(
            "QTreeWidget { border: 1px solid palette(mid); border-radius: 8px;"
            " background: palette(base); color: palette(text); padding: 4px; }"
            " QTreeWidget::item { padding: 5px; border-radius: 6px; }"
            " QTreeWidget::item:selected { background: rgba(76,175,80,0.30); color: palette(text); }"
            f" QTreeWidget::item:disabled {{ color: {dim_text_css(tree)}; }}"
        )

        ordered_groups = list(group_order or [])
        groups: dict = {group: [] for group in ordered_groups}
        for row in rows:
            group = row.group or "other"
            if group not in groups:
                groups[group] = []
                ordered_groups.append(group)
            groups[group].append(row)

        selected_child = None
        rows_by_target = {row.target_id: row for row in rows}
        expanded_groups = expanded_groups or set()
        for group in ordered_groups:
            group_rows = groups.get(group, [])
            if not group_rows:
                continue
            label = group_labels.get(group, str(group).replace("_", " ").title())
            parent = QTreeWidgetItem([f"{label}  ({len(group_rows)})"])
            parent.setData(0, Qt.ItemDataRole.UserRole, f"{group_role_prefix}{group}")
            parent.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = parent.font(0)
            font.setBold(True)
            parent.setFont(0, font)
            tree.addTopLevelItem(parent)

            group_has_current = False
            for row in sorted(group_rows, key=lambda r: r.sort_key or (r.label,)):
                child = QTreeWidgetItem([row.label])
                child.setData(0, Qt.ItemDataRole.UserRole, row.target_id)
                if row.icon_path and os.path.exists(row.icon_path):
                    child.setIcon(0, QIcon(row.icon_path))
                if not row.enabled:
                    child.setDisabled(True)
                child.setToolTip(0, row.tooltip)
                parent.addChild(child)
                if row.current:
                    selected_child = child
                    group_has_current = True
            parent.setExpanded(group in expanded_groups or group_has_current)

        if selected_child is not None:
            tree.setCurrentItem(selected_child)

        def _on_target_clicked(item: "QTreeWidgetItem", _column: int = 0):
            if item is None or item.isDisabled():
                return
            target_id = item.data(0, Qt.ItemDataRole.UserRole)
            if not target_id or str(target_id).startswith(group_role_prefix):
                return
            if on_select is not None:
                row = rows_by_target.get(target_id)
                if confirm_select is not None and row is not None and not confirm_select(row):
                    return
                on_select(target_id)

        def _group_id(item: "QTreeWidgetItem") -> Optional[str]:
            role = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(role, str) and role.startswith(group_role_prefix):
                return role[len(group_role_prefix):]
            return None

        tree.itemClicked.connect(_on_target_clicked)
        tree.itemActivated.connect(_on_target_clicked)
        if set_group_expanded is not None:
            tree.itemExpanded.connect(lambda it: (_group_id(it) and set_group_expanded(_group_id(it), True)))
            tree.itemCollapsed.connect(lambda it: (_group_id(it) and set_group_expanded(_group_id(it), False)))
        return tree

    def _build_ore_list() -> QListWidget:
        return _build_flat_target_list(
            mining_target_rows(
                player_data,
                ORE_DATA,
                ORE_IMAGES,
                GEM_IMAGES,
                MINING_PICKAXE_DATA,
                DEFAULT_MINING_TARGET,
                _MINING_DEFERRED_VARIANT_NOTES,
                QUEST_UNLOCK_RULES,
            ),
            on_set_ore,
        )

    def _build_tree_list() -> QListWidget:
        return _build_flat_target_list(
            woodcutting_target_rows(
                player_data,
                TREE_DATA,
                TREE_IMAGES,
                WOODCUTTING_AXE_DATA,
                DEFAULT_WOODCUTTING_TARGET,
            ),
            on_set_tree,
        )

    def _build_smith_list() -> QTreeWidget:
        def _set_smith_target(recipe_id: str) -> None:
            if on_set_smith is not None:
                on_set_smith(recipe_id)
                return
            spec = SMITHING_DATA.get(recipe_id, {})
            if spec.get("station") == "furnace":
                on_set_bar(spec.get("output_item", recipe_id))

        images = dict(BAR_IMAGES)
        images.update(_item_asset_paths())
        return _build_grouped_target_tree(
            smithing_target_rows(
                player_data,
                SMITHING_DATA,
                images,
                DEFAULT_SMITHING_TARGET,
                QUEST_UNLOCK_RULES,
            ),
            {},
            "__tier__:",
            _set_smith_target,
            expanded_groups=set(smith_expanded_tiers()),
            set_group_expanded=set_smith_tier_expanded,
        )

    def _build_craft_list() -> QTreeWidget:
        return _build_grouped_target_tree(
            crafting_target_rows(
                player_data,
                CRAFTING_DATA,
                CRAFTED_ITEM_IMAGES,
                QUEST_UNLOCK_RULES,
            ),
            _CRAFT_FAMILY_LABELS,
            "__family__:",
            on_set_craft,
            expanded_groups=set(craft_expanded_families()),
            set_group_expanded=set_craft_family_expanded,
        )

    def _build_fletch_list() -> QTreeWidget:
        return _build_grouped_target_tree(
            fletching_target_rows(player_data, FLETCHING_DATA, FLETCHED_ITEM_IMAGES, QUEST_UNLOCK_RULES),
            FLETCHING_GROUP_LABELS,
            "__fletching_group__:",
            on_set_fletch,
            group_order=list(FLETCHING_GROUP_ORDER),
        )

    def _build_firemaking_list() -> QListWidget:
        return _build_flat_target_list(
            firemaking_target_rows(
                player_data,
                FIREMAKING_DATA,
                FIREMAKING_ITEM_IMAGES,
                DEFAULT_FIREMAKING_TARGET,
                QUEST_UNLOCK_RULES,
            ),
            on_set_firemaking,
        )

    def _build_fishing_list() -> QListWidget:
        return _build_flat_target_list(
            fishing_target_rows(
                player_data,
                FISHING_DATA,
                FISHING_ITEM_IMAGES,
                DEFAULT_FISHING_TARGET,
                QUEST_UNLOCK_RULES,
            ),
            on_set_fishing,
        )

    def _build_hunter_list() -> QTreeWidget:
        return _build_grouped_target_tree(
            hunter_target_rows(
                player_data,
                HUNTER_DATA,
                HUNTER_ITEM_IMAGES,
                DEFAULT_HUNTER_TARGET,
                QUEST_UNLOCK_RULES,
            ),
            HUNTER_GROUP_LABELS,
            "__hunter_group__:",
            on_set_hunter,
            group_order=list(HUNTER_GROUP_ORDER),
        )

    def _build_cooking_list() -> QTreeWidget:
        images = dict(COOKING_ITEM_IMAGES)
        images.update(_item_asset_paths())
        return _build_grouped_target_tree(
            cooking_target_rows(
                player_data,
                COOKING_DATA,
                images,
                DEFAULT_COOKING_TARGET,
                QUEST_UNLOCK_RULES,
            ),
            _COOKING_FAMILY_LABELS,
            "__cooking_family__:",
            on_set_cooking,
        )

    def _build_runecrafting_list() -> QTreeWidget:
        return _build_grouped_target_tree(
            runecrafting_target_rows(
                player_data,
                RUNECRAFTING_DATA,
                RUNECRAFTING_ITEM_IMAGES,
                RUNECRAFTING_POUCH_DATA,
                DEFAULT_RUNECRAFTING_TARGET,
                QUEST_UNLOCK_RULES,
            ),
            RUNECRAFTING_GROUP_LABELS,
            "__runecrafting_group__:",
            on_set_runecrafting,
            group_order=list(RUNECRAFTING_GROUP_LABELS),
        )

    def _combat_mode_text() -> str:
        style_id = combat_attack_style_for_equipment_pure(player_data, EQUIPMENT_ITEM_DATA)
        spec = COMBAT_ATTACK_STYLE_DATA.get(style_id, COMBAT_ATTACK_STYLE_DATA.get(DEFAULT_COMBAT_ATTACK_STYLE, {}))
        return str(spec.get("display_name", style_id)).replace("Ranged ", "Ranged ").title()

    def _combat_bank_run_text() -> str:
        bank_run_raw = player_data.get("combat_bank_run", {}) or {}
        bank_run_remaining = 0
        if isinstance(bank_run_raw, dict):
            try:
                bank_run_remaining = max(0, int(bank_run_raw.get("reviews_remaining", 0) or 0))
            except (TypeError, ValueError):
                bank_run_remaining = 0
        return (
            f"Bank run: {bank_run_remaining} review{'s' if bank_run_remaining != 1 else ''} remaining"
            if bank_run_remaining
            else "Bank run: ready"
        )

    _combat_setup_refreshers: list = []

    def _build_combat_setup_panel() -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        mode_label = QLabel(f"Combat mode: {_combat_mode_text()}")
        mode_label.setObjectName("combatModeLabel")
        mode_label.setStyleSheet("color: palette(text); font-weight: 600;")
        layout.addWidget(mode_label)

        # Attack-style picker. The valid styles depend on the equipped weapon's
        # combat class (melee/ranged); a magic weapon has a single fixed style, so
        # the combo is omitted and the mode label above already reads "Magic".
        # The combo is rebuilt on refresh so swapping weapons re-scopes the options.
        style_row = QWidget()
        style_row_layout = QHBoxLayout(style_row)
        style_row_layout.setContentsMargins(0, 0, 0, 0)
        style_row_layout.setSpacing(8)
        style_label = QLabel("Attack style")
        style_label.setStyleSheet("color: palette(text);")
        style_row_layout.addWidget(style_label)
        layout.addWidget(style_row)
        _style_combo_ref = {"combo": None}

        def _rebuild_style_combo() -> None:
            # D2: the options are the equipped weapon's actual AttackStyleData slots,
            # each labeled with its attack type (stab/slash/crush). Selecting a row
            # stores both the weapon_style and the style_type, so parity keys off the
            # exact slot the player picked.
            options = combat_weapon_style_options_pure(player_data, EQUIPMENT_ITEM_DATA)
            old = _style_combo_ref["combo"]
            if old is not None:
                old.setParent(None)
                old.deleteLater()
                _style_combo_ref["combo"] = None
            if len(options) <= 1:
                # Magic (single fixed style) — no selector needed.
                style_row.setVisible(False)
                return
            combo = QComboBox()
            combo.setObjectName("combatStyleCombo")
            current_index = 0
            for index, option in enumerate(options):
                # Spell out which skills each slot trains, so the choice of XP is
                # visible at the point of selection (e.g. "Aggressive (Crush) —
                # Attack + Strength + Defence + Constitution" for the 2h shared slot).
                trains = " + ".join(option["trained_skills"])
                combo.addItem(
                    f"{option['display_name']} — {trains}",
                    (option["weapon_style"], option["style_type"]),
                )
                if option["is_current"]:
                    current_index = index
            combo.setCurrentIndex(current_index)
            if on_set_combat_style is not None:
                combo.currentIndexChanged.connect(
                    lambda _index, c=combo: on_set_combat_style(c.currentData())
                )
            style_row_layout.addWidget(combo, 1)
            _style_combo_ref["combo"] = combo
            style_row.setVisible(True)

        _rebuild_style_combo()

        spell_row = QWidget()
        spell_layout = QHBoxLayout(spell_row)
        spell_layout.setContentsMargins(0, 0, 0, 0)
        spell_layout.setSpacing(8)
        spell_label = QLabel("Spell")
        spell_label.setStyleSheet("color: palette(text);")
        spell_combo = QComboBox()
        spell_combo.setObjectName("combatSpellCombo")
        current_spell = player_data.get("current_combat_spell", DEFAULT_COMBAT_SPELL)
        selected_spell_index = 0
        for spell_id, spec in COMBAT_MAGIC_SPELL_DATA.items():
            spell_combo.addItem(str(spec.get("display_name", spell_id)), spell_id)
            if spell_id == current_spell:
                selected_spell_index = spell_combo.count() - 1
        spell_combo.setCurrentIndex(selected_spell_index)
        if on_set_combat_spell is not None:
            spell_combo.currentIndexChanged.connect(
                lambda _index: on_set_combat_spell(spell_combo.currentData() or DEFAULT_COMBAT_SPELL)
            )
        spell_layout.addWidget(spell_label)
        spell_layout.addWidget(spell_combo, 1)
        layout.addWidget(spell_row)

        auto_eat_row = QWidget()
        auto_eat_layout = QHBoxLayout(auto_eat_row)
        auto_eat_layout.setContentsMargins(0, 0, 0, 0)
        auto_eat_layout.setSpacing(8)
        threshold_label = QLabel("Auto-eat")
        threshold_label.setStyleSheet("color: palette(text);")
        threshold_spin = QSpinBox()
        threshold_spin.setObjectName("combatAutoEatThresholdSpin")
        threshold_spin.setRange(1, 99)
        threshold_spin.setSuffix("%")
        try:
            threshold_value = int(player_data.get("combat_auto_eat_threshold_percent", 40) or 40)
        except (TypeError, ValueError):
            threshold_value = 40
        threshold_spin.setValue(max(1, min(threshold_value, 99)))
        if on_set_combat_auto_eat_threshold is not None:
            threshold_spin.valueChanged.connect(lambda value: on_set_combat_auto_eat_threshold(value))
        auto_eat_layout.addWidget(threshold_label)
        auto_eat_layout.addWidget(threshold_spin, 1)
        layout.addWidget(auto_eat_row)

        # ---- Loot from this enemy ----
        # Deciding what to pick up belongs with the live combat controls, not the
        # Bank tab. The default view is coarse: a value threshold plus a single
        # "keep everything" toggle. Per-drop overrides are opt-in behind an
        # "Advanced" disclosure, rendered as icon cells with a binary Keep | Drop
        # pill (neither segment lit = follow the value threshold).
        loot_header = QLabel("Loot")
        loot_header.setStyleSheet("color: palette(text); font-weight: 600;")
        layout.addWidget(loot_header)

        loot_row = QWidget()
        loot_row_layout = QHBoxLayout(loot_row)
        loot_row_layout.setContentsMargins(0, 0, 0, 0)
        loot_row_layout.setSpacing(8)
        loot_label = QLabel("Leave loot under")
        loot_label.setStyleSheet("color: palette(text);")
        loot_spin = QSpinBox()
        loot_spin.setObjectName("combatLootThresholdSpin")
        loot_spin.setRange(0, 100000)
        loot_spin.setSingleStep(5)
        loot_spin.setSuffix(" gp value")
        try:
            _loot_threshold = int(player_data.get("loot_value_threshold", inventory_pure.DEFAULT_LOOT_VALUE_THRESHOLD))
        except (TypeError, ValueError):
            _loot_threshold = inventory_pure.DEFAULT_LOOT_VALUE_THRESHOLD
        loot_spin.setValue(max(0, _loot_threshold))
        if on_set_loot_threshold is not None:
            loot_spin.valueChanged.connect(lambda value: on_set_loot_threshold(int(value)))
        loot_row_layout.addWidget(loot_label)
        loot_row_layout.addWidget(loot_spin, 1)
        layout.addWidget(loot_row)

        if loot_override_rows:
            _LOOT_MODES = ("auto", "keep", "leave")
            loot_cell_state: dict = {}
            loot_pill_refreshers: dict = {}

            def _apply_loot_cell(item_name: str, mode: str) -> None:
                loot_cell_state[item_name] = mode
                refresh = loot_pill_refreshers.get(item_name)
                if refresh is not None:
                    refresh(mode)

            keep_all_check = QCheckBox("Keep every drop from this enemy")
            keep_all_check.setObjectName("combatLootKeepAllCheck")

            def _sync_keep_all() -> None:
                names = [str(r.get("item", "")) for r in loot_override_rows if str(r.get("item", ""))]
                all_keep = bool(names) and all(loot_cell_state.get(n) == "keep" for n in names)
                keep_all_check.blockSignals(True)
                keep_all_check.setChecked(all_keep)
                keep_all_check.blockSignals(False)

            def _on_keep_all(checked: bool) -> None:
                mode = "keep" if checked else "auto"
                for _r in loot_override_rows:
                    name = str(_r.get("item", ""))
                    if not name:
                        continue
                    _apply_loot_cell(name, mode)
                    if on_set_loot_override is not None:
                        on_set_loot_override(name, mode)

            keep_all_check.toggled.connect(_on_keep_all)
            layout.addWidget(keep_all_check)

            loot_adv_check = QCheckBox("Advanced: keep or drop specific drops")
            loot_adv_check.setObjectName("combatLootAdvancedCheck")
            layout.addWidget(loot_adv_check)

            loot_grid_container = QWidget()
            loot_grid_container.setObjectName("combatLootOverrideGrid")
            loot_grid_layout = QGridLayout(loot_grid_container)
            loot_grid_layout.setContentsMargins(0, 2, 0, 2)
            loot_grid_layout.setSpacing(6)
            _LOOT_GRID_COLS = 2

            # Each drop gets a joined two-segment pill — Keep | Drop. Neither
            # segment lit means "Auto": that drop follows the "Leave loot under N
            # gp" threshold. Clicking a lit segment again clears back to Auto, so
            # the binary switch still reaches all three backend modes the engine
            # understands (auto / keep / leave).
            def _seg_css(side: str, active: bool, accent: str) -> str:
                radius = (
                    "border-top-left-radius:6px;border-bottom-left-radius:6px;border-right:none;"
                    if side == "left"
                    else "border-top-right-radius:6px;border-bottom-right-radius:6px;"
                )
                if active:
                    face = f"background:{accent};color:palette(text);font-weight:600;"
                else:
                    face = f"background:transparent;color:{dim_text_css(loot_grid_container)};"
                return (
                    f"QPushButton{{border:1px solid palette(mid);{radius}"
                    f"padding:2px 12px;font-size:11px;{face}}}"
                )

            def _set_loot_mode(name: str, new_mode: str) -> None:
                _apply_loot_cell(name, new_mode)
                if on_set_loot_override is not None:
                    on_set_loot_override(name, new_mode)
                _sync_keep_all()

            _cell_idx = 0
            for _r in loot_override_rows:
                item_name = str(_r.get("item", ""))
                if not item_name:
                    continue
                mode = str(_r.get("mode", "auto"))
                if mode not in _LOOT_MODES:
                    mode = "auto"
                cell = QWidget()
                cell.setObjectName(f"combatLootCell{_cell_idx}")
                cell_layout = QHBoxLayout(cell)
                cell_layout.setContentsMargins(2, 2, 2, 2)
                cell_layout.setSpacing(8)
                icon_label = QLabel()
                _def = _item_def_for(item_name)
                _icon = _bank_icon_path(item_name, _def.asset_path if _def is not None else None)
                if _icon:
                    icon_label.setPixmap(QPixmap(_icon).scaled(22, 22, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                icon_label.setFixedWidth(24)
                name_label = QLabel(item_name)
                name_label.setStyleSheet("color: palette(text); font-size: 11px;")
                keep_btn = QPushButton("Keep")
                keep_btn.setObjectName(f"lootOverrideKeep::{item_name}")
                keep_btn.setFixedHeight(24)
                drop_btn = QPushButton("Drop")
                drop_btn.setObjectName(f"lootOverrideDrop::{item_name}")
                drop_btn.setFixedHeight(24)
                keep_btn.setEnabled(on_set_loot_override is not None)
                drop_btn.setEnabled(on_set_loot_override is not None)

                def _refresh_pill(new_mode: str, kb=keep_btn, db=drop_btn) -> None:
                    kb.setStyleSheet(_seg_css("left", new_mode == "keep", "rgba(76,175,80,0.35)"))
                    db.setStyleSheet(_seg_css("right", new_mode == "leave", "rgba(192,69,59,0.35)"))

                loot_pill_refreshers[item_name] = _refresh_pill
                keep_btn.clicked.connect(
                    lambda _c=False, name=item_name: _set_loot_mode(
                        name, "auto" if loot_cell_state.get(name) == "keep" else "keep"
                    )
                )
                drop_btn.clicked.connect(
                    lambda _c=False, name=item_name: _set_loot_mode(
                        name, "auto" if loot_cell_state.get(name) == "leave" else "leave"
                    )
                )
                pill = QWidget()
                pill_layout = QHBoxLayout(pill)
                pill_layout.setContentsMargins(0, 0, 0, 0)
                pill_layout.setSpacing(0)
                pill_layout.addWidget(keep_btn)
                pill_layout.addWidget(drop_btn)
                cell_layout.addWidget(icon_label)
                cell_layout.addWidget(name_label, 1)
                cell_layout.addWidget(pill)
                _apply_loot_cell(item_name, mode)
                loot_grid_layout.addWidget(cell, _cell_idx // _LOOT_GRID_COLS, _cell_idx % _LOOT_GRID_COLS)
                _cell_idx += 1

            loot_grid_container.setVisible(False)
            loot_adv_check.toggled.connect(lambda checked: loot_grid_container.setVisible(bool(checked)))
            layout.addWidget(loot_grid_container)
            _sync_keep_all()

        def _refresh_combat_setup_panel() -> None:
            mode_label.setText(f"Combat mode: {_combat_mode_text()}")
            _rebuild_style_combo()

        _combat_setup_refreshers.append(_refresh_combat_setup_panel)

        layout.addStretch(1)
        return panel

    def _build_combat_skill_bars() -> QWidget:
        # Per-skill XP progress, the same read-out the gathering/artisan skills
        # get on the Stats screen — so the player can see combat XP land in
        # Attack/Strength/Defence/Constitution (and Ranged/Magic) individually
        # rather than as one opaque drop.
        box = QWidget()
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(4)
        heading = QLabel("Combat XP")
        heading.setStyleSheet("color: palette(text); font-weight: 600;")
        box_layout.addWidget(heading)
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(4)
        grid.setColumnStretch(1, 1)
        for row, (display, level_key, exp_key, default_level) in enumerate(_COMBAT_SKILL_BARS):
            level = int(player_data.get(level_key, default_level) or default_level)
            exp = round(player_data.get(exp_key, 0) or 0, 1)
            pct, remain, target_lv = compute_level_progress(level, exp, EXP_TABLE)
            name_lbl = QLabel(f"{display} Lv {level}")
            name_lbl.setStyleSheet("color: palette(text); font-size: 11px;")
            bar = QProgressBar()
            bar.setTextVisible(False)
            bar.setFixedHeight(10)
            bar.setRange(0, 100)
            bar.setValue(pct)
            bar.setToolTip(
                f"{display}: level {level} • {exp:,.0f} XP"
                + (f" • {remain:,.0f} to Lv {target_lv}" if level < 99 else " • max level")
            )
            grid.addWidget(name_lbl, row, 0)
            grid.addWidget(bar, row, 1)
        box_layout.addLayout(grid)
        return box

    def _build_combat_list() -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(_build_combat_skill_bars())

        combat_images = _item_asset_paths()
        combat_rows = combat_target_rows(
            player_data,
            COMBAT_ENEMY_DATA,
            combat_images,
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
            COMBAT_ENEMY_IMAGES,
        )

        def _confirm_combat_target(row: TargetRowMetadata) -> bool:
            if not row.requires_confirmation:
                return True
            answer = QMessageBox.question(
                container,
                row.confirmation_title or "Confirm combat target",
                row.confirmation_message or "This combat target may kill you. Select it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            return answer == QMessageBox.StandardButton.Yes

        tree = _build_grouped_target_tree(
            combat_rows,
            {group: group for group in COMBAT_TARGET_GROUP_ORDER},
            "__combat_group__:",
            on_set_combat,
            confirm_select=_confirm_combat_target,
            group_order=list(COMBAT_TARGET_GROUP_ORDER),
        )
        layout.addWidget(tree, 1)
        return container

    def _build_utility_list() -> QTreeWidget:
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setIconSize(QSize(28, 28))
        tree.setRootIsDecorated(True)
        tree.setIndentation(14)
        tree.setUniformRowHeights(True)
        tree.setStyleSheet(
            "QTreeWidget { border: 1px solid palette(mid); border-radius: 8px;"
            " background: palette(base); color: palette(text); padding: 4px; }"
            " QTreeWidget::item { padding: 5px; border-radius: 6px; }"
            " QTreeWidget::item:selected { background: rgba(76,175,80,0.30); color: palette(text); }"
            f" QTreeWidget::item:disabled {{ color: {dim_text_css(tree)}; }}"
        )
        rows = utility_activity_rows(
            player_data,
            UTILITY_ACTIVITY_DATA,
            {**UTILITY_ITEM_IMAGES, **COOKING_ITEM_IMAGES},
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
            QUEST_UNLOCK_RULES,
        )
        current = player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
        ordered_groups = list(_UTILITY_GROUP_LABELS)
        groups = {group: [] for group in ordered_groups}
        for row in rows:
            spec = UTILITY_ACTIVITY_DATA.get(row.target_id, {})
            group = str(spec.get("group", "material_processing"))
            if group not in groups:
                groups[group] = []
                ordered_groups.append(group)
            groups[group].append(row)

        selected_child = None
        for group in ordered_groups:
            group_rows = groups.get(group, [])
            if not group_rows:
                continue
            label = _UTILITY_GROUP_LABELS.get(group, group.replace("_", " ").title())
            parent = QTreeWidgetItem([f"{label}  ({len(group_rows)})"])
            parent.setData(0, Qt.ItemDataRole.UserRole, f"__utility_group__:{group}")
            parent.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = parent.font(0)
            font.setBold(True)
            parent.setFont(0, font)
            tree.addTopLevelItem(parent)
            group_has_current = False
            for row in group_rows:
                child = QTreeWidgetItem([row.label])
                child.setData(0, Qt.ItemDataRole.UserRole, row.target_id)
                if row.icon_path and os.path.exists(row.icon_path):
                    child.setIcon(0, QIcon(row.icon_path))
                if not row.enabled:
                    child.setDisabled(True)
                child.setToolTip(0, row.tooltip)
                parent.addChild(child)
                if row.target_id == current:
                    selected_child = child
                    group_has_current = True
            parent.setExpanded(group_has_current)

        if selected_child is not None:
            tree.setCurrentItem(selected_child)

        def _on_utility_clicked(item: "QTreeWidgetItem", _column: int = 0):
            if item is None or item.isDisabled():
                return
            activity_id = item.data(0, Qt.ItemDataRole.UserRole)
            if not activity_id or str(activity_id).startswith("__utility_group__"):
                return
            if on_set_utility is not None:
                on_set_utility(activity_id)

        tree.itemClicked.connect(_on_utility_clicked)
        tree.itemActivated.connect(_on_utility_clicked)
        return tree

    _TARGET_BUILDERS = {
        "Mining": _build_ore_list,
        "Woodcutting": _build_tree_list,
        "Smithing": _build_smith_list,
        "Crafting": _build_craft_list,
        "Fletching": _build_fletch_list,
        "Firemaking": _build_firemaking_list,
        "Fishing": _build_fishing_list,
        "Hunter": _build_hunter_list,
        "Cooking": _build_cooking_list,
        "Runecrafting": _build_runecrafting_list,
        _COMBAT_HUB_NAME: _build_combat_list,
        _UTILITY_HUB_NAME: _build_utility_list,
    }
    _TARGET_PROMPTS = {
        "Mining": "Select Ore to Mine",
        "Woodcutting": "Select Tree to Cut",
        "Smithing": "Select what to Smelt or Forge",
        "Crafting": "Select Item to Craft",
        "Fletching": "Select Item to Fletch",
        "Firemaking": "Select Logs to Burn",
        "Fishing": "Select Fish to Catch",
        "Hunter": "Select Creature to Hunt",
        "Cooking": "Select Food to Cook",
        "Runecrafting": "Select Runecrafting Action",
        _COMBAT_HUB_NAME: "Select Enemy",
        _UTILITY_HUB_NAME: "Select an Activity (no XP)",
    }

    def _skill_icon_path(display_name: str) -> str:
        return skill_icon_path_for(display_name) or os.path.join(current_dir, "icon", "achievement_icon.png")

    # ---- three-pane layout: categories | skills | target panel ----
    panes = QWidget()
    panes_layout = QHBoxLayout(panes)
    panes_layout.setContentsMargins(0, 0, 0, 0)
    panes_layout.setSpacing(12)

    _CAT_STYLE = (
        "QPushButton { text-align: left; padding: 8px 10px;"
        " border: 1px solid palette(mid); border-radius: 8px;"
        " color: palette(text); background: palette(base); }"
        " QPushButton:hover { border-color: palette(dark); }"
    )
    _CAT_STYLE_SEL = (
        "QPushButton { text-align: left; padding: 8px 10px;"
        " border: 2px solid #4CAF50; border-radius: 8px;"
        " font-weight: 600; color: #d6ffe5; background: rgba(76,175,80,0.18); }"
    )

    cat_col = QWidget()
    cat_layout = QVBoxLayout(cat_col)
    cat_layout.setContentsMargins(0, 0, 0, 0)
    cat_layout.setSpacing(6)
    lbl = QLabel("Categories")
    lbl.setStyleSheet("font-weight: 600; color: palette(text);")
    cat_layout.addWidget(lbl)
    cat_buttons: dict = {}
    for cat in hub:
        cb = QPushButton(cat.display_name)
        cb.setStyleSheet(_CAT_STYLE)
        cb.setCursor(Qt.CursorShape.PointingHandCursor)
        cat_layout.addWidget(cb)
        cat_buttons[cat.category_id] = cb
        cb.clicked.connect(lambda _=False, c=cat.category_id: _select_category(c))
    cat_layout.addStretch(1)
    cat_col.setFixedWidth(170)
    panes_layout.addWidget(cat_col)

    skill_col = QWidget()
    skill_col_layout = QVBoxLayout(skill_col)
    skill_col_layout.setContentsMargins(0, 0, 0, 0)
    skill_col_layout.setSpacing(6)
    lbl2 = QLabel("Skills")
    lbl2.setStyleSheet("font-weight: 600; color: palette(text);")
    skill_col_layout.addWidget(lbl2)
    # A QListWidget handles clicking, keyboard nav, selection highlight, and
    # disabled rows natively. Earlier hand-rolled QToolButtons were unreliable
    # (stale signals / overlay hit-testing), so we lean on the proven pattern
    # already used by the target lists below.
    skill_list_widget = QListWidget()
    skill_list_widget.setIconSize(QSize(28, 28))
    skill_list_widget.setStyleSheet(
        "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 4px; }"
        " QListWidget::item { padding: 6px; border-radius: 6px; }"
        " QListWidget::item:selected { background: rgba(76,175,80,0.30);"
        " color: palette(text); }"
    )
    skill_col_layout.addWidget(skill_list_widget, 1)
    skill_col.setFixedWidth(190)
    panes_layout.addWidget(skill_col)
    # Guard so programmatic selection (on category switch) does not recurse.
    _skill_guard = {"on": False}

    panel_holder = QWidget()
    panel_layout = QVBoxLayout(panel_holder)
    panel_layout.setContentsMargins(0, 0, 0, 0)
    panel_layout.setSpacing(8)
    panes_layout.addWidget(panel_holder, 1)

    s_layout.addWidget(panes, 1)

    def _cards_for(category_id: str):
        for cat in hub:
            if cat.category_id == category_id:
                return cat.skills
        return ()

    def _clear_layout(target_layout) -> None:
        child = target_layout.takeAt(0)
        while child:
            w = child.widget()
            if w is not None:
                w.hide()
                w.setParent(None)
                w.deleteLater()
            child = target_layout.takeAt(0)

    def _render_skill_list() -> None:
        _skill_guard["on"] = True
        skill_list_widget.clear()
        cards = _cards_for(state["category"])
        for card in cards:
            it = QListWidgetItem(card.display_name)
            it.setData(Qt.ItemDataRole.UserRole, card.display_name)
            ip = _skill_icon_path(card.display_name)
            if os.path.exists(ip):
                it.setIcon(QIcon(ip))
            if not card.implemented:
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                it.setToolTip("Planned skill — not yet playable (shown because Developer Mode is on)")
            skill_list_widget.addItem(it)
            if card.display_name == state["skill"]:
                skill_list_widget.setCurrentItem(it)
        _skill_guard["on"] = False

    def _on_skill_row(current, _previous) -> None:
        guard = _skill_guard["on"]
        name = current.data(Qt.ItemDataRole.UserRole) if current is not None else None
        _debug_log(f"hub.skill_row: name={name!r} guard={guard} state_skill={state['skill']!r}")
        if guard or current is None:
            return
        if name and name != state["skill"]:
            _select_hub_skill(name)

    skill_list_widget.currentItemChanged.connect(_on_skill_row)
    skill_list_widget.itemClicked.connect(lambda it: _on_skill_row(it, None))

    def _render_panel() -> None:
        _clear_layout(panel_layout)
        # Drop stale references before rebuild; repopulated if Smithing/Crafting
        # is the visible panel so the live availability hook can re-enable them.
        _MAIN_MENU_CTX["smith_btn"] = None
        _MAIN_MENU_CTX["craft_btn"] = None
        _MAIN_MENU_CTX["fletch_btn"] = None
        _MAIN_MENU_CTX["firemaking_btn"] = None
        _MAIN_MENU_CTX["hunter_btn"] = None
        _MAIN_MENU_CTX["cooking_btn"] = None
        _MAIN_MENU_CTX["runecrafting_btn"] = None
        name = state["skill"]
        _debug_log(f"hub.render_panel: skill={name!r} cat={state['category']!r}")
        card = next((c for c in _cards_for(state["category"]) if c.display_name == name), None)
        if card is None:
            hint = QLabel("Select a skill to begin.")
            hint.setStyleSheet("color: palette(text); font-size: 11px;")
            panel_layout.addWidget(hint)
            panel_layout.addStretch(1)
            return

        is_utility = name in _UTILITY_SKILL_NAMES
        is_combat = name == _COMBAT_HUB_NAME
        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(8)
        if is_utility:
            # No level/XP for Utility; keep the title bare and flag the no-XP nature.
            title = QLabel(name)
        elif is_combat:
            title = QLabel(f"{name} — Lv {player_combat_level_pure(player_data)}")
        elif card.implemented:
            level = player_data.get(f"{name.lower()}_level", 1)
            title = QLabel(f"{name} — Lv {level}")
        else:
            title = QLabel(name)
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: palette(text);")
        hl.addWidget(title)
        hl.addStretch(1)

        if card.implemented and card.selectable_for_review:
            train_btn = QPushButton()
            if state["active"] == name:
                train_btn.setText("Currently active" if is_utility else "Currently training")
                train_btn.setEnabled(False)
                train_btn.setStyleSheet(
                    "QPushButton { padding: 6px 12px; border: 1px solid #4CAF50;"
                    " border-radius: 6px; color: #4CAF50; background: rgba(76,175,80,0.12); }"
                )
            else:
                available = _skill_available(name)
                train_btn.setText("Start activity" if is_utility else "Train this skill")
                train_btn.setEnabled(available)
                train_btn.setStyleSheet(
                    # Use the base/text palette pairing (same as the category and
                    # list widgets) rather than button/buttonText: on macOS dark
                    # mode the button face renders light, which washed out the
                    # text. base+text stays legible in both themes.
                    "QPushButton { padding: 6px 12px; border: 1px solid palette(mid);"
                    " border-radius: 6px; color: palette(text); background: palette(base); }"
                    " QPushButton:hover { border-color: #4CAF50; }"
                    f" QPushButton:disabled {{ color: {dim_text_css(train_btn)}; }}"
                )
                if not available:
                    if name == "Smithing":
                        train_btn.setToolTip("Mine ores until you can smelt a bar.")
                    elif name == "Crafting":
                        train_btn.setToolTip("Gather materials or level up to craft an item.")
                    elif name == "Fletching":
                        train_btn.setToolTip("Cut logs or level up to fletch an item.")
                    elif name == "Firemaking":
                        train_btn.setToolTip("Cut or acquire logs before training Firemaking.")
                    elif name == "Hunter":
                        train_btn.setToolTip("Gather jars/materials, complete unlocks, or level up before training Hunter.")
                    elif name == "Cooking":
                        train_btn.setToolTip("Gather raw food or prep ingredients before training Cooking.")
                    elif name == "Runecrafting":
                        train_btn.setToolTip("Complete Rune Mysteries and gather essence plus altar access.")
                    elif name == _COMBAT_HUB_NAME:
                        train_btn.setToolTip("Select an available enemy.")
            train_btn.clicked.connect(lambda _=False, n=name: _set_active(n))
            hl.addWidget(train_btn)
            if name == "Smithing":
                _MAIN_MENU_CTX["smith_btn"] = train_btn
            elif name == "Crafting":
                _MAIN_MENU_CTX["craft_btn"] = train_btn
            elif name == "Fletching":
                _MAIN_MENU_CTX["fletch_btn"] = train_btn
            elif name == "Firemaking":
                _MAIN_MENU_CTX["firemaking_btn"] = train_btn
            elif name == "Hunter":
                _MAIN_MENU_CTX["hunter_btn"] = train_btn
            elif name == "Cooking":
                _MAIN_MENU_CTX["cooking_btn"] = train_btn
            elif name == "Runecrafting":
                _MAIN_MENU_CTX["runecrafting_btn"] = train_btn
        panel_layout.addWidget(header)

        if is_utility:
            note = QLabel("Material prep — earns no XP. Each successful review processes a batch.")
            note.setWordWrap(True)
            # palette(mid) is a border role and renders near-black in dark mode;
            # use palette(text) (smaller/italic) so the note stays readable.
            note.setStyleSheet("color: palette(text); font-size: 11px; font-style: italic;")
            panel_layout.addWidget(note)

        if not card.implemented:
            note = QLabel("This skill is planned but not yet playable.")
            note.setWordWrap(True)
            note.setStyleSheet("color: palette(text); font-size: 11px;")
            panel_layout.addWidget(note)
            panel_layout.addStretch(1)
            return

        builder = _TARGET_BUILDERS.get(name)
        if builder is not None:
            prompt_lbl = QLabel(_TARGET_PROMPTS.get(name, "Select a target"))
            prompt_lbl.setStyleSheet("color: palette(text);")
            panel_layout.addWidget(prompt_lbl)
            panel_layout.addWidget(builder(), 1)
        else:
            panel_layout.addWidget(QLabel("No targets available yet."))
            panel_layout.addStretch(1)

    def _update_cat_btn_styles() -> None:
        for cid, cbtn in cat_buttons.items():
            cbtn.setStyleSheet(_CAT_STYLE_SEL if cid == state["category"] else _CAT_STYLE)

    def _select_hub_skill(name: str) -> None:
        # NOTE: must not be named ``_select_skill`` — the Stats tab defines its
        # own ``_select_skill`` later in this same function scope, and the later
        # binding would shadow this one, silently routing hub clicks into the
        # Stats selector and leaving the hub panel stale.
        _debug_log(f"hub.select_skill: {name!r}")
        state["skill"] = name
        _render_panel()

    def _select_category(category_id: str) -> None:
        _debug_log(f"hub.select_category: {category_id!r}")
        state["category"] = category_id
        _update_cat_btn_styles()
        cards = _cards_for(category_id)
        first = next(
            (c.display_name for c in cards if c.implemented),
            cards[0].display_name if cards else "",
        )
        state["skill"] = first
        _render_skill_list()
        _render_panel()

    def _initial_category() -> str:
        active = state["active"]
        for cat in hub:
            for card in cat.skills:
                if card.display_name == active and card.implemented:
                    return cat.category_id
        return first_category_id(hub)

    # Store dialog + warn for the live availability refresh hook used during
    # reviews (auto-enables Smithing/Crafting once materials are gathered).
    _MAIN_MENU_CTX["dialog"] = dialog
    _MAIN_MENU_CTX["warn_label"] = warn
    try:
        dialog.finished.connect(
            lambda _=None: _MAIN_MENU_CTX.update(
                {
                    "dialog": None,
                    "smith_btn": None,
                    "craft_btn": None,
                    "fletch_btn": None,
                    "firemaking_btn": None,
                    "hunter_btn": None,
                    "cooking_btn": None,
                    "runecrafting_btn": None,
                    "warn_label": None,
                }
            )
        )
    except Exception:
        pass

    _refresh_active_label()
    if hub:
        init_cat = _initial_category()
        _select_category(init_cat)
    else:
        panel_layout.addWidget(QLabel("No skills available."))

    tabs.addTab(skills_tab, "Skills")
    tabs.setTabToolTip(tabs.indexOf(skills_tab), "Pick a category, choose a skill, then select what to train on")

    # ---- Shop tab ---------------------------------------------------------
    # Frontend boundary: the tab is deliberately thin. It renders backend view
    # models and calls preview/apply APIs; it does not calculate prices, sell
    # policy, stock behavior, service eligibility, or hidden reward-shop state.
    shop_tab = QWidget()
    shop_tab.setObjectName("shopTab")
    shop_layout = QVBoxLayout(shop_tab)
    shop_layout.setContentsMargins(12, 12, 12, 12)
    shop_layout.setSpacing(8)

    shop_search = QLineEdit()
    shop_search.setObjectName("shopSearchInput")
    shop_search.setPlaceholderText("Search shops or items")
    shop_search.setClearButtonEnabled(True)
    shop_search.setStyleSheet(
        "QLineEdit { padding: 7px 10px; border: 1px solid palette(mid);"
        " border-radius: 8px; color: palette(text); background: palette(base); }"
    )
    shop_layout.addWidget(shop_search)

    shop_selector = QListWidget()
    shop_selector.setObjectName("shopSelectionList")
    # Max height is managed by _sync_shop_detail_visibility: full height while
    # browsing, compact while a shop's detail panel is open.
    shop_selector.setMinimumHeight(116)
    shop_selector.setIconSize(QSize(24, 24))
    shop_selector.setAlternatingRowColors(True)
    shop_selector.setStyleSheet(
        "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 3px; }"
        " QListWidget::item { padding: 5px 7px; border-radius: 6px; }"
        " QListWidget::item:selected { background: rgba(76,175,80,0.30); color: palette(text); }"
    )
    shop_layout.addWidget(shop_selector, 1)

    shop_placeholder = QLabel("Click a shop to browse its stock, prices, and services.")
    shop_placeholder.setObjectName("shopDetailPlaceholder")
    shop_placeholder.setStyleSheet(f"color: {dim_text_css(shop_placeholder)}; padding: 2px;")
    shop_layout.addWidget(shop_placeholder)

    shop_shell = QWidget()
    shop_shell.setObjectName("shopDetailShell")
    shop_shell.setStyleSheet(
        "QWidget#shopDetailShell { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); }"
    )
    shop_shell_layout = QVBoxLayout(shop_shell)
    shop_shell_layout.setContentsMargins(10, 8, 10, 10)
    shop_shell_layout.setSpacing(8)

    shop_header = QWidget()
    shop_header_layout = QHBoxLayout(shop_header)
    shop_header_layout.setContentsMargins(0, 0, 0, 0)
    shop_header_layout.setSpacing(8)
    shop_title = QLabel("Select a shop")
    shop_title.setObjectName("shopDetailTitle")
    shop_title.setStyleSheet("font-size: 14px; font-weight: 700; color: palette(text);")
    shop_meta = QLabel("")
    shop_meta.setObjectName("shopDetailMeta")
    shop_meta.setStyleSheet(f"color: {dim_text_css(shop_meta)};")
    shop_collapse_btn = QToolButton()
    shop_collapse_btn.setObjectName("shopDetailCollapseButton")
    shop_collapse_btn.setText("Close ✕")
    shop_collapse_btn.setToolTip("Collapse this shop panel and return to the shop list")
    shop_collapse_btn.setStyleSheet(
        "QToolButton { border: 1px solid palette(mid); border-radius: 6px;"
        " padding: 2px 8px; color: palette(text); background: transparent; }"
        " QToolButton:hover { border-color: #4CAF50; }"
    )
    shop_header_layout.addWidget(shop_title, 1)
    shop_header_layout.addWidget(shop_meta)
    shop_header_layout.addWidget(shop_collapse_btn)
    shop_shell_layout.addWidget(shop_header)

    shop_mode_tabs = QTabWidget()
    shop_mode_tabs.setObjectName("shopModeTabs")
    shop_mode_tabs.setDocumentMode(True)

    buy_page = QWidget()
    buy_layout = QVBoxLayout(buy_page)
    buy_layout.setContentsMargins(0, 0, 0, 0)
    buy_layout.setSpacing(6)
    stock_scroll = QScrollArea()
    stock_scroll.setObjectName("shopStockScroll")
    stock_scroll.setWidgetResizable(True)
    # One full tile row is the hard floor (short Anki windows must compress
    # gracefully, never overlap); taller dialogs stretch to show more rows.
    stock_scroll.setMinimumHeight(86)
    stock_scroll.setStyleSheet("QScrollArea#shopStockScroll { border: 1px solid palette(mid); border-radius: 8px; }")
    stock_content = QWidget()
    stock_grid = QGridLayout(stock_content)
    stock_grid.setContentsMargins(6, 6, 6, 6)
    stock_grid.setSpacing(6)
    # Pack tiles top-left instead of letting the grid center/stretch them
    # across leftover space (which produced floating tiles and huge gaps).
    # Column 6 and row 199 are virtual stretch-only cells past any real tile.
    stock_grid.setColumnStretch(6, 1)
    stock_grid.setRowStretch(199, 1)
    stock_scroll.setWidget(stock_content)
    buy_layout.addWidget(stock_scroll, 1)
    shop_mode_tabs.addTab(buy_page, "Buy Items")

    sell_page = QWidget()
    sell_layout = QVBoxLayout(sell_page)
    sell_layout.setContentsMargins(0, 0, 0, 0)
    sell_layout.setSpacing(6)
    sell_hint = QLabel("Select an item from your bank to sell to this shop.")
    sell_hint.setObjectName("shopSellHint")
    sell_hint.setStyleSheet(f"color: {dim_text_css(sell_hint)};")
    sell_layout.addWidget(sell_hint)
    sell_inventory = QListWidget()
    sell_inventory.setObjectName("shopSellInventoryList")
    sell_inventory.setIconSize(QSize(24, 24))
    sell_inventory.setAlternatingRowColors(True)
    sell_inventory.setStyleSheet(
        "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 3px; }"
        " QListWidget::item { padding: 5px 7px; border-radius: 6px; }"
        " QListWidget::item:selected { background: rgba(76,175,80,0.30); color: palette(text); }"
    )
    sell_layout.addWidget(sell_inventory, 1)
    shop_mode_tabs.addTab(sell_page, "Sell Items")
    shop_shell_layout.addWidget(shop_mode_tabs, 4)

    transaction_panel = QWidget()
    transaction_panel.setObjectName("shopTransactionPanel")
    transaction_panel.setStyleSheet(
        "QWidget#shopTransactionPanel { border: 1px solid palette(mid); border-radius: 8px;"
        " background: rgba(255,255,255,0.03); }"
    )
    transaction_layout = QVBoxLayout(transaction_panel)
    transaction_layout.setContentsMargins(8, 6, 8, 8)
    transaction_layout.setSpacing(5)
    shop_selected_label = QLabel("Select an item")
    shop_selected_label.setObjectName("shopSelectedItemLabel")
    shop_selected_label.setStyleSheet("font-weight: 600; color: palette(text);")
    transaction_layout.addWidget(shop_selected_label)
    quantity_row = QWidget()
    quantity_layout = QHBoxLayout(quantity_row)
    quantity_layout.setContentsMargins(0, 0, 0, 0)
    quantity_layout.setSpacing(5)
    quantity_layout.addWidget(QLabel("Qty:"))
    shop_quantity_buttons = {}
    for amount in (1, 5, 10, 50):
        btn = QPushButton(str(amount))
        btn.setObjectName(f"shopQty{amount}Button")
        btn.setMaximumWidth(44)
        shop_quantity_buttons[amount] = btn
        quantity_layout.addWidget(btn)
    shop_custom_qty = QSpinBox()
    shop_custom_qty.setObjectName("shopCustomQuantitySpin")
    shop_custom_qty.setRange(1, 999999)
    shop_custom_qty.setValue(1)
    shop_custom_qty.setMaximumWidth(92)
    quantity_layout.addWidget(shop_custom_qty)
    shop_all_qty = QPushButton("All")
    shop_all_qty.setObjectName("shopQtyAllButton")
    shop_all_qty.setMaximumWidth(50)
    quantity_layout.addWidget(shop_all_qty)
    quantity_layout.addStretch(1)
    shop_action_btn = QPushButton("Buy")
    shop_action_btn.setObjectName("shopTransactionButton")
    quantity_layout.addWidget(shop_action_btn)
    transaction_layout.addWidget(quantity_row)
    shop_preview_label = QLabel("Preview unavailable")
    shop_preview_label.setObjectName("shopPreviewLabel")
    shop_preview_label.setWordWrap(True)
    shop_preview_label.setStyleSheet(f"color: {dim_text_css(shop_preview_label)};")
    transaction_layout.addWidget(shop_preview_label)
    shop_shell_layout.addWidget(transaction_panel)

    # Services and vendor actions are not ordinary stock rows; frame them as
    # their own panel so they read as a separate section, not trailing widgets.
    services_panel = QWidget()
    services_panel.setObjectName("shopServicesPanel")
    services_panel.setStyleSheet(
        "QWidget#shopServicesPanel { border: 1px solid palette(mid); border-radius: 8px;"
        " background: rgba(255,255,255,0.03); }"
    )
    services_panel_layout = QVBoxLayout(services_panel)
    services_panel_layout.setContentsMargins(8, 6, 8, 8)
    services_panel_layout.setSpacing(5)
    # Hug the content: in provider mode this panel is the only section, and
    # without a cap it stretches and floats its rows mid-air.
    services_panel.setMaximumHeight(190)
    services_header = QLabel("Services / Vendor Actions")
    services_header.setObjectName("shopServicesHeader")
    services_header.setStyleSheet("font-weight: 600; color: palette(text);")
    services_panel_layout.addWidget(services_header)
    service_row = QWidget()
    service_row_layout = QHBoxLayout(service_row)
    service_row_layout.setContentsMargins(0, 0, 0, 0)
    service_row_layout.setSpacing(8)
    service_list = QListWidget()
    service_list.setObjectName("shopServiceList")
    service_list.setMaximumHeight(72)
    service_list.setIconSize(QSize(24, 24))
    service_list.setAlternatingRowColors(True)
    service_list.setStyleSheet(
        "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 3px; }"
        " QListWidget::item { padding: 5px 7px; border-radius: 6px; }"
        " QListWidget::item:selected { background: rgba(76,175,80,0.30); color: palette(text); }"
    )
    service_row_layout.addWidget(service_list, 1)
    service_controls = QWidget()
    service_controls_layout = QVBoxLayout(service_controls)
    service_controls_layout.setContentsMargins(0, 0, 0, 0)
    service_controls_layout.setSpacing(5)
    service_qty = QSpinBox()
    service_qty.setObjectName("shopServiceQuantitySpin")
    service_qty.setRange(1, 999999)
    service_qty.setValue(1)
    # Vendor actions are one interaction per use (dialogue parity, owner
    # decision 2026-07-07); the backend clamps quantity to 1, so the spinner
    # is hidden until a genuinely batchable instant service exists.
    service_qty.setVisible(False)
    service_controls_layout.addWidget(service_qty)
    service_use_btn = QPushButton("Use")
    service_use_btn.setObjectName("shopServiceUseButton")
    service_controls_layout.addWidget(service_use_btn)
    service_controls_layout.addStretch(1)
    service_row_layout.addWidget(service_controls)
    services_panel_layout.addWidget(service_row)
    service_preview = QLabel("")
    service_preview.setObjectName("shopServicePreviewLabel")
    service_preview.setWordWrap(True)
    service_preview.setStyleSheet(f"color: {dim_text_css(service_preview)};")
    services_panel_layout.addWidget(service_preview)
    shop_shell_layout.addWidget(services_panel)

    history_header = QWidget()
    history_header_layout = QHBoxLayout(history_header)
    history_header_layout.setContentsMargins(0, 0, 0, 0)
    history_header_layout.setSpacing(8)
    history_label = QLabel("Recent Shop Activity")
    history_label.setStyleSheet("font-weight: 600; color: palette(text);")
    global_history_btn = QPushButton("Global recent")
    global_history_btn.setObjectName("shopGlobalHistoryButton")
    global_history_btn.setCheckable(True)
    history_header_layout.addWidget(history_label)
    history_header_layout.addStretch(1)
    history_header_layout.addWidget(global_history_btn)
    shop_shell_layout.addWidget(history_header)
    local_history = QListWidget()
    local_history.setObjectName("shopLocalHistoryList")
    local_history.setMaximumHeight(44)
    local_history.setStyleSheet(
        "QListWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 3px; }"
        " QListWidget::item { padding: 4px 6px; }"
    )
    global_history = QListWidget()
    global_history.setObjectName("shopGlobalHistoryList")
    global_history.setMaximumHeight(44)
    global_history.setVisible(False)
    global_history.setStyleSheet(local_history.styleSheet())
    shop_shell_layout.addWidget(local_history)
    shop_shell_layout.addWidget(global_history)

    shop_toast = QLabel("")
    shop_toast.setObjectName("shopToastLabel")
    shop_toast.setWordWrap(True)
    shop_toast.setStyleSheet("color: #4CAF50; font-weight: 600;")
    shop_toast.setVisible(False)
    shop_shell_layout.addWidget(shop_toast)
    # Absorbs leftover height so sections stay top-aligned (dominant in
    # provider mode, where every stretchy section is hidden).
    shop_shell_layout.addStretch(1)
    shop_layout.addWidget(shop_shell, 3)

    shop_state = {
        "shop_id": "",
        "row_id": "",
        "sell_item": "",
        # Selected service/vendor provider (Ellis, Bartender, ...). Providers
        # are their own selector entries because the backend attaches services
        # to NPC providers, not to any shop.
        "provider": "",
        "service_kind": "",
        "service_id": "",
    }

    def _safe_object_suffix(value: str) -> str:
        return "".join(ch if ch.isalnum() else "_" for ch in value)[:80]

    def _visible_shop_defs() -> list:
        return [
            shop for shop in SHOP_DATA.values()
            if shop.get("visibility") != "hidden"
        ]

    def _shop_live_row_count(shop: dict) -> int:
        return sum(
            1 for row in shop.get("stock", [])
            if shop.get("visibility") == "visible" and row.get("disposition") == "live"
        )

    def _shop_selector_sort_key(shop: dict) -> tuple:
        return (
            _shop_live_row_count(shop) == 0,
            shop.get("visibility") != "visible",
            str(shop.get("display_name", "")),
        )

    def _sync_shop_detail_visibility(detail_open: bool) -> None:
        # Browse-first: the shop list owns the tab until a shop is opened, and
        # gets its height back when the detail panel is collapsed.
        shop_shell.setVisible(detail_open)
        shop_placeholder.setVisible(not detail_open)
        shop_selector.setMaximumHeight(104 if detail_open else 16777215)

    def _visible_service_defs() -> list:
        rows = []
        for service in SHOP_SERVICES.values():
            if service.get("visibility") == "visible":
                rows.append(("service", service))
        for action in SHOP_VENDOR_ACTIONS.values():
            if action.get("visibility") == "visible":
                rows.append(("vendor_action", action))
        return rows

    def _format_shop_price(value, currency_name: str) -> str:
        if value is None:
            return "N/A"
        try:
            amount = int(value)
        except (TypeError, ValueError):
            return "N/A"
        return f"{amount:,} {currency_name}"

    def _inventory_count_for_ui(item_name: str) -> int:
        inventory = player_data.get("inventory", {}) or {}
        try:
            return max(0, int(inventory.get(item_name, 0) or 0))
        except (TypeError, ValueError):
            return 0

    def _format_requirement_rows(rows: list) -> str:
        parts = []
        for row in rows[:3]:
            if not isinstance(row, dict):
                continue
            item_name = str(row.get("item_name", "Item"))
            owned = int(row.get("owned_quantity", 0) or 0)
            required = int(row.get("required_quantity", 0) or 0)
            parts.append(f"{item_name} {owned:,}/{required:,}")
        return "; ".join(parts)

    def _preview_denial_text(preview: dict, fallback: str = "") -> str:
        reason = str(preview.get("reason") or fallback or "unavailable")
        if reason == "insufficient_currency":
            currency = str(preview.get("currency_item_name", "Coins"))
            required = int(preview.get("required_currency", 0) or 0)
            owned = int(preview.get("currency_owned", 0) or 0)
            return f"Need {required:,} {currency}, you have {owned:,}."
        if reason == "missing_item":
            item_name = str(preview.get("item_name", "item"))
            owned = int(preview.get("owned_quantity", 0) or 0)
            return f"You have {owned:,} x {item_name}."
        if reason == "missing_requirements":
            missing = preview.get("missing_requirements", [])
            detail = _format_requirement_rows(missing if isinstance(missing, list) else [])
            return f"Missing requirements: {detail}." if detail else "Missing requirements."
        return fallback or reason

    def _service_icon_item_name(row: dict) -> str:
        for key in ("outputs", "inputs"):
            for item in row.get(key, []):
                item_name = item.get("item_name")
                if isinstance(item_name, str) and _item_icon_path(item_name):
                    return item_name
        return ""

    def _set_list_item_icon(item: QListWidgetItem, item_name: str) -> None:
        icon = _pixel_item_icon(item_name, 24)
        if icon is not None:
            item.setIcon(icon)

    def _replace_player_data(new_data: dict) -> None:
        player_data.clear()
        player_data.update(new_data)

    def _persist_shop_state() -> None:
        try:
            on_save_skill(state.get("active", current_skill) or "None")
        except Exception:
            pass

    def _refresh_after_shop_mutation(message: str) -> None:
        shop_toast.setText(message)
        shop_toast.setVisible(bool(message))
        _populate_shop_selector()
        _render_shop_detail()
        _populate_sell_inventory()
        _populate_shop_history()
        try:
            _refresh_equipment_views()
        except Exception:
            pass

    def _shop_view() -> dict:
        # No default shop: until the user clicks a shop, there is no detail
        # view. An invalid/stale id degrades to the browse state rather than
        # silently swapping in a different shop.
        shop_id = shop_state["shop_id"]
        if not shop_id or all(shop.get("id") != shop_id for shop in _visible_shop_defs()):
            shop_state["shop_id"] = ""
            return {"exists": False, "rows": []}
        return shop_view_model_pure(player_data, shop_id)

    def _selected_buy_row(view: dict | None = None) -> Optional[dict]:
        view = view if view is not None else _shop_view()
        rows = view.get("rows", []) if isinstance(view, dict) else []
        if not rows:
            return None
        row = next((candidate for candidate in rows if candidate.get("id") == shop_state["row_id"]), None)
        if row is None:
            row = rows[0]
            shop_state["row_id"] = row.get("id", "")
        return row

    def _stock_tile_text(row: dict, currency_name: str) -> str:
        return str(row.get("item_name", "Item"))

    def _shop_row_tooltip(row: dict, currency_name: str) -> str:
        parts = [str(row.get("item_name", "Item"))]
        stock = f"{int(row.get('current_quantity', 0) or 0):,}/{int(row.get('default_quantity', 0) or 0):,}"
        parts.append(f"Stock: {stock}")
        parts.append(f"Buy: {_format_shop_price(row.get('buy_price'), currency_name)}")
        parts.append(f"Sell: {_format_shop_price(row.get('sell_price'), currency_name)}")
        if row.get("lock_reason"):
            parts.append(f"Locked: {row.get('lock_reason')}")
        if row.get("price_source"):
            parts.append(str(row.get("price_source")))
        if row.get("source"):
            parts.append(str(row.get("source")))
        return "\n".join(parts)

    def _render_stock_grid() -> None:
        _clear_layout(stock_grid)
        view = _shop_view()
        rows = view.get("rows", []) if view.get("exists") else []
        if not rows:
            empty = QLabel("No stock rows available.")
            empty.setStyleSheet(f"color: {dim_text_css(empty)};")
            stock_grid.addWidget(empty, 0, 0)
            return
        currency_name = str(view.get("currency_item_name", "Coins"))
        selected_row_id = shop_state["row_id"]
        for index, row in enumerate(rows):
            row_id = str(row.get("id", ""))
            btn = QToolButton()
            btn.setText(_stock_tile_text(row, currency_name))
            btn.setObjectName(f"shopStockTile_{_safe_object_suffix(row_id)}")
            btn.setProperty("shopRowId", row_id)
            btn.setMinimumSize(104, 66)
            icon = _pixel_item_icon(str(row.get("item_name", "")), 32)
            if icon is not None:
                btn.setIcon(icon)
                btn.setIconSize(QSize(32, 32))
            if hasattr(btn, "setToolButtonStyle"):
                try:
                    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)  # type: ignore[attr-defined]
                except Exception:
                    pass
            btn.setCheckable(True)
            btn.setChecked(row_id == selected_row_id)
            btn.setToolTip(_shop_row_tooltip(row, currency_name))
            border = "#4CAF50" if row_id == selected_row_id else "palette(mid)"
            foreground = dim_text_css(btn) if row.get("lock_reason") else "palette(text)"
            btn.setStyleSheet(
                f"QToolButton {{ text-align: center; padding: 5px; border: 1px solid {border};"
                f" border-radius: 6px; color: {foreground}; background: rgba(255,255,255,0.03); }}"
                " QToolButton:hover { border-color: #4CAF50; }"
            )
            btn.clicked.connect(lambda _=False, rid=row_id: _select_stock_row(rid))
            stock_grid.addWidget(btn, index // 6, index % 6)

    def _select_stock_row(row_id: str) -> None:
        shop_state["row_id"] = row_id
        _render_stock_grid()
        _refresh_transaction_panel()

    def _populate_sell_inventory() -> None:
        current = shop_state.get("sell_item", "")
        sell_inventory.clear()
        inventory = player_data.get("inventory", {}) or {}
        items = [
            (name, int(amount or 0))
            for name, amount in sorted(inventory.items())
            if isinstance(name, str) and int(amount or 0) > 0
        ]
        if not items:
            empty = QListWidgetItem("Your bank has no sellable items.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            sell_inventory.addItem(empty)
            shop_state["sell_item"] = ""
            return
        selected_item = current if any(name == current for name, _amount in items) else items[0][0]
        shop_state["sell_item"] = selected_item
        for name, amount in items:
            item = QListWidgetItem(f"{name} x{amount:,}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            _set_list_item_icon(item, name)
            sell_inventory.addItem(item)
            if name == selected_item:
                sell_inventory.setCurrentItem(item)

    def _set_quantity(value: int) -> None:
        shop_custom_qty.blockSignals(True)
        shop_custom_qty.setValue(max(1, min(999999, int(value))))
        shop_custom_qty.blockSignals(False)
        _refresh_transaction_panel()

    def _set_all_quantity() -> None:
        if shop_mode_tabs.currentIndex() == 0:
            row = _selected_buy_row()
            if row is not None:
                _set_quantity(max(1, int(row.get("current_quantity", 1) or 1)))
                return
        else:
            item_name = shop_state.get("sell_item", "")
            if item_name:
                _set_quantity(max(1, _inventory_count_for_ui(item_name)))

    def _refresh_transaction_panel() -> None:
        view = _shop_view()
        shop_id = str(view.get("shop_id", ""))
        qty = int(shop_custom_qty.value())
        if shop_mode_tabs.currentIndex() == 0:
            row = _selected_buy_row(view)
            if row is None:
                shop_selected_label.setText("Select an item")
                shop_preview_label.setText("No stock row selected.")
                shop_action_btn.setText("Buy")
                shop_action_btn.setEnabled(False)
                return
            item_name = str(row.get("item_name", "Item"))
            price = _format_shop_price(row.get("buy_price"), str(view.get("currency_item_name", "Coins")))
            stock = f"{int(row.get('current_quantity', 0) or 0):,}/{int(row.get('default_quantity', 0) or 0):,}"
            shop_selected_label.setText(f"{item_name} · Stock {stock} · Buy {price}")
            preview = preview_shop_buy_pure(player_data, shop_id, str(row.get("id", "")), qty)
            if preview.get("allowed"):
                amount = int(preview.get("quantity", qty) or qty)
                total = int(preview.get("total_price", 0) or 0)
                currency = str(preview.get("currency_item_name", view.get("currency_item_name", "Coins")))
                owned_currency = int(preview.get("currency_owned", _inventory_count_for_ui(currency)) or 0)
                suffix = " (clamped)" if preview.get("clamped") else ""
                shop_preview_label.setText(f"Buy {amount:,} x {item_name} for {total:,} {currency}. You have {owned_currency:,} {currency}.{suffix}")
                shop_action_btn.setText(f"Buy {amount:,}")
                shop_action_btn.setEnabled(True)
            else:
                shop_preview_label.setText(_preview_denial_text(preview, str(row.get("lock_reason", ""))))
                shop_action_btn.setText("Buy")
                shop_action_btn.setEnabled(False)
        else:
            item_name = shop_state.get("sell_item", "")
            shop_action_btn.setText("Sell")
            if not item_name:
                shop_selected_label.setText("Select an item")
                shop_preview_label.setText("No bank item selected.")
                shop_action_btn.setEnabled(False)
                return
            owned = _inventory_count_for_ui(item_name)
            shop_selected_label.setText(f"{item_name} · You have {owned:,}")
            preview = preview_shop_sell_pure(player_data, shop_id, item_name, qty)
            if preview.get("allowed"):
                amount = int(preview.get("quantity", qty) or qty)
                total = int(preview.get("total_price", 0) or 0)
                currency = str(preview.get("currency_item_name", view.get("currency_item_name", "Coins")))
                owned = int(preview.get("owned_quantity", _inventory_count_for_ui(item_name)) or 0)
                suffix = " (clamped)" if preview.get("clamped") else ""
                shop_preview_label.setText(f"Sell {amount:,} x {item_name} for {total:,} {currency}. You have {owned:,} x {item_name}.{suffix}")
                shop_action_btn.setText(f"Sell {amount:,}")
                shop_action_btn.setEnabled(True)
            else:
                shop_preview_label.setText(_preview_denial_text(preview))
                shop_action_btn.setEnabled(False)

    def _confirm_wilderness_purchase(view: dict) -> bool:
        # Owner-declared ambush risk: confirm once per session before buying
        # in the Wilderness (same precedent as dangerous combat targets).
        if not view.get("wilderness") or shop_state.get("wilderness_confirmed"):
            return True
        answer = QMessageBox.question(
            dialog,
            "Wilderness purchase",
            "This shop is in the Wilderness: every 28 items bought risks an"
            " ambush that can kill you. Buy here anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False
        shop_state["wilderness_confirmed"] = True
        return True

    def _ambush_toast_suffix(result: dict) -> str:
        ambush = result.get("wilderness_ambush") or {}
        if not ambush.get("triggered"):
            return ""
        if ambush.get("died"):
            return " You were ambushed and killed — your gear is in a grave!"
        return f" You were ambushed for {int(ambush.get('damage', 0) or 0)} damage!"

    def _apply_shop_transaction() -> None:
        view = _shop_view()
        shop_id = str(view.get("shop_id", ""))
        qty = int(shop_custom_qty.value())
        if shop_mode_tabs.currentIndex() == 0:
            row = _selected_buy_row(view)
            if row is None:
                return
            if not _confirm_wilderness_purchase(view):
                return
            new_data, result = apply_shop_buy_pure(player_data, shop_id, str(row.get("id", "")), qty)
            if not result.get("allowed"):
                _refresh_transaction_panel()
                return
            _replace_player_data(new_data)
            _persist_shop_state()
            _refresh_after_shop_mutation(
                f"Bought {int(result.get('quantity', 0) or 0):,} x {result.get('item_name', row.get('item_name', 'item'))}."
                + _ambush_toast_suffix(result)
            )
        else:
            item_name = shop_state.get("sell_item", "")
            if not item_name:
                return
            new_data, result = apply_shop_sell_pure(player_data, shop_id, item_name, qty)
            if not result.get("allowed"):
                _refresh_transaction_panel()
                return
            _replace_player_data(new_data)
            _persist_shop_state()
            _refresh_after_shop_mutation(f"Sold {int(result.get('quantity', 0) or 0):,} x {item_name}.")

    def _service_text(kind: str, row: dict) -> str:
        label = "Service" if kind == "service" else "Vendor"
        provider = str(row.get("provider", ""))
        price = _format_shop_price(row.get("price", 0), str(row.get("currency_item_name", "Coins")))
        outputs = ", ".join(
            f"{item.get('item_name')} x{item.get('quantity', 1)}"
            for item in row.get("outputs", [])[:2]
        )
        right = f" -> {outputs}" if outputs else ""
        return f"{label}: {row.get('display_name', row.get('id'))} · {provider} · {price}{right}"

    def _populate_services() -> None:
        current_id = shop_state.get("service_id", "")
        service_list.clear()
        rows = _visible_service_defs()
        provider = shop_state.get("provider", "")
        if provider:
            rows = [(kind, row) for kind, row in rows if str(row.get("provider", "")) == provider]
        if not rows:
            empty = QListWidgetItem("No live services or vendor actions.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            service_list.addItem(empty)
            return
        selected = current_id if any(row.get("id") == current_id for _kind, row in rows) else rows[0][1].get("id", "")
        shop_state["service_id"] = str(selected)
        for kind, row in rows:
            item = QListWidgetItem(_service_text(kind, row))
            item.setData(Qt.ItemDataRole.UserRole, {"kind": kind, "id": row.get("id", "")})
            _set_list_item_icon(item, _service_icon_item_name(row))
            service_list.addItem(item)
            if row.get("id") == selected:
                shop_state["service_kind"] = kind
                service_list.setCurrentItem(item)
        _refresh_service_preview()

    def _selected_service_def() -> tuple[str, Optional[dict]]:
        kind = shop_state.get("service_kind", "")
        service_id = shop_state.get("service_id", "")
        if kind == "service":
            return kind, SHOP_SERVICES.get(service_id)
        if kind == "vendor_action":
            return kind, SHOP_VENDOR_ACTIONS.get(service_id)
        return "", None

    def _refresh_service_preview() -> None:
        kind, row = _selected_service_def()
        if row is None:
            service_preview.setText("Select a service or vendor action.")
            service_use_btn.setEnabled(False)
            return
        qty = int(service_qty.value())
        if kind == "service":
            preview = preview_shop_service_pure(player_data, str(row.get("id", "")), qty)
        else:
            preview = preview_shop_vendor_action_pure(player_data, str(row.get("id", "")), qty)
        if preview.get("allowed"):
            amount = int(preview.get("quantity", qty) or qty)
            total = int(preview.get("total_price", 0) or 0)
            currency = str(preview.get("currency_item_name", row.get("currency_item_name", "Coins")))
            suffix = " (clamped)" if preview.get("clamped") else ""
            requirement_text = _format_requirement_rows(preview.get("requirements", []) if isinstance(preview.get("requirements"), list) else [])
            requirement_suffix = f" Have: {requirement_text}." if requirement_text else ""
            service_preview.setText(f"Use {row.get('display_name', row.get('id'))} {amount:,} time(s) for {total:,} {currency}.{requirement_suffix}{suffix}")
            service_use_btn.setEnabled(True)
        else:
            service_preview.setText(_preview_denial_text(preview, str(row.get("lock_reason", ""))))
            service_use_btn.setEnabled(False)

    def _apply_service_transaction() -> None:
        kind, row = _selected_service_def()
        if row is None:
            return
        qty = int(service_qty.value())
        if kind == "service":
            new_data, result = apply_shop_service_pure(player_data, str(row.get("id", "")), qty)
        else:
            new_data, result = apply_shop_vendor_action_pure(player_data, str(row.get("id", "")), qty)
        if not result.get("allowed"):
            _refresh_service_preview()
            return
        _replace_player_data(new_data)
        _persist_shop_state()
        _refresh_after_shop_mutation(f"Used {row.get('display_name', 'vendor action')} {int(result.get('quantity', 0) or 0):,} time(s).")
        _refresh_service_preview()

    def _populate_shop_history() -> None:
        local_history.clear()
        global_history.clear()
        view = _shop_view()
        shop_id = str(view.get("shop_id", ""))
        local_rows = shop_history_rows_pure(player_data, shop_id=shop_id, limit=4)
        global_rows = shop_history_rows_pure(player_data, limit=8)
        if not local_rows:
            empty = QListWidgetItem("No recent activity for this shop.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            local_history.addItem(empty)
        else:
            for event in local_rows:
                local_history.addItem(QListWidgetItem(str(event.get("display", event.get("event_id", "Shop event")))))
        if not global_rows:
            empty = QListWidgetItem("No global shop activity yet.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            global_history.addItem(empty)
        else:
            for event in global_rows:
                global_history.addItem(QListWidgetItem(str(event.get("display", event.get("event_id", "Shop event")))))

    def _set_shop_detail_mode(mode: str) -> None:
        # "shop": stock/sell/transaction/history. "provider": services only —
        # the backend attaches services to provider NPCs, never to shops, so a
        # shop detail must not advertise unrelated global services.
        is_shop = mode == "shop"
        shop_mode_tabs.setVisible(is_shop)
        transaction_panel.setVisible(is_shop)
        history_header.setVisible(is_shop)
        local_history.setVisible(is_shop)
        if not is_shop:
            global_history.setVisible(False)
            global_history_btn.setChecked(False)
        services_panel.setVisible(not is_shop)

    def _render_shop_detail() -> None:
        provider = shop_state.get("provider", "")
        if provider:
            provider_rows = [
                (kind, row)
                for kind, row in _visible_service_defs()
                if str(row.get("provider", "")) == provider
            ]
            if not provider_rows:
                shop_state["provider"] = ""
                _sync_shop_detail_visibility(False)
                return
            _sync_shop_detail_visibility(True)
            _set_shop_detail_mode("provider")
            shop_title.setText(provider)
            location = next(
                (str(row.get("location", "")) for _kind, row in provider_rows if row.get("location")),
                "",
            )
            shop_meta.setText(location)
            _populate_services()
            return
        view = _shop_view()
        if not view.get("exists"):
            shop_state["row_id"] = ""
            _sync_shop_detail_visibility(False)
            return
        _sync_shop_detail_visibility(True)
        _set_shop_detail_mode("shop")
        shop_title.setText(str(view.get("display_name", "NPC shop")))
        currency_name = str(view.get("currency_item_name", "Coins"))
        meta_parts = [f"{currency_name}: {_inventory_count_for_ui(currency_name):,} owned"]
        if view.get("wilderness"):
            meta_parts.append("Wilderness — you can be attacked")
        if view.get("general_store"):
            meta_parts.append("General store")
        if view.get("lock_reason"):
            meta_parts.append(str(view.get("lock_reason")))
        shop_meta.setText(" · ".join(meta_parts))
        if not shop_state["row_id"] and view.get("rows"):
            shop_state["row_id"] = str(view["rows"][0].get("id", ""))
        _render_stock_grid()
        _populate_sell_inventory()
        _refresh_transaction_panel()
        _populate_shop_history()

    def _shop_selector_label_from_result(result: dict) -> str:
        kind = result.get("kind")
        if kind == "stock":
            price = _format_shop_price(result.get("buy_price"), "Coins")
            stock = f"{int(result.get('current_quantity', 0) or 0):,}/{int(result.get('default_quantity', 0) or 0):,}"
            lock = f" · {result.get('lock_reason')}" if result.get("lock_reason") else ""
            return f"{result.get('item_name')} · {result.get('shop_name')} · Stock {stock} · {price}{lock}"
        label = "Service" if kind == "service" else "Vendor"
        lock = f" · {result.get('lock_reason')}" if result.get("lock_reason") else ""
        return f"{label}: {result.get('display_name')} · {result.get('provider')} · {result.get('price', 0):,} {result.get('currency_item_name', 'Coins')}{lock}"

    def _populate_shop_selector() -> None:
        current_shop_id = shop_state.get("shop_id", "")
        query = shop_search.text().strip()
        shop_selector.clear()
        if query:
            results = search_shop_catalog_pure(player_data, query, include_locked=True, include_hidden=False, limit=80).get("results", [])
            if results:
                selected_item = None
                for result in results:
                    item = QListWidgetItem(_shop_selector_label_from_result(result))
                    item.setData(Qt.ItemDataRole.UserRole, dict(result))
                    if result.get("kind") == "stock":
                        _set_list_item_icon(item, str(result.get("item_name", "")))
                    elif result.get("kind") in {"service", "vendor_action"}:
                        source = SHOP_SERVICES if result.get("kind") == "service" else SHOP_VENDOR_ACTIONS
                        service_row = source.get(str(result.get("id", "")), {})
                        _set_list_item_icon(item, _service_icon_item_name(service_row))
                    if result.get("visibility") == "visible_locked" or result.get("lock_reason"):
                        item.setForeground(dim_text_color(shop_selector))
                    shop_selector.addItem(item)
                    if result.get("kind") == "stock" and result.get("shop_id") == current_shop_id and selected_item is None:
                        selected_item = item
                if selected_item is not None:
                    shop_selector.blockSignals(True)
                    shop_selector.setCurrentItem(selected_item)
                    shop_selector.blockSignals(False)
                return
            empty = QListWidgetItem("No visible shop stock, service, or vendor action matches this search.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            shop_selector.addItem(empty)
            return
        visible = sorted(_visible_shop_defs(), key=_shop_selector_sort_key)
        for shop in visible:
            view = shop_view_model_pure(player_data, str(shop.get("id", "")))
            rows = view.get("rows", [])
            live_count = sum(1 for row in rows if row.get("can_buy"))
            locked_count = sum(1 for row in rows if row.get("lock_reason"))
            suffix = []
            if live_count:
                suffix.append(f"{live_count} live")
            if locked_count:
                suffix.append(f"{locked_count} locked")
            if shop.get("general_store"):
                suffix.append("general store")
            if shop.get("lock_reason"):
                suffix.append(str(shop.get("lock_reason")))
            label = f"{shop.get('display_name', shop.get('id'))} · " + (" · ".join(suffix) if suffix else "read-only")
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, {"kind": "shop", "shop_id": shop.get("id", "")})
            icon_name = next(
                (
                    str(row.get("item_name", ""))
                    for row in rows
                    if _item_icon_path(str(row.get("item_name", "")))
                ),
                "",
            )
            _set_list_item_icon(item, icon_name)
            if shop.get("visibility") != "visible":
                item.setForeground(dim_text_color(shop_selector))
            shop_selector.addItem(item)
            if shop.get("id") == current_shop_id:
                shop_selector.blockSignals(True)
                shop_selector.setCurrentItem(item)
                shop_selector.blockSignals(False)
        # Service/vendor providers browse as their own entries after the shops;
        # the backend ties services to NPC providers, not shops.
        providers: dict = {}
        for kind, row in _visible_service_defs():
            providers.setdefault(str(row.get("provider", "")), []).append((kind, row))
        current_provider = shop_state.get("provider", "")
        for provider in sorted(name for name in providers if name):
            provider_rows = providers[provider]
            location = next(
                (str(row.get("location", "")) for _kind, row in provider_rows if row.get("location")),
                "",
            )
            count = len(provider_rows)
            parts = [provider]
            if location:
                parts.append(location)
            parts.append(f"{count} service{'s' if count != 1 else ''}")
            item = QListWidgetItem(" · ".join(parts))
            item.setData(Qt.ItemDataRole.UserRole, {"kind": "provider", "provider": provider})
            icon_name = next(
                (
                    _service_icon_item_name(row)
                    for _kind, row in provider_rows
                    if _service_icon_item_name(row)
                ),
                "",
            )
            _set_list_item_icon(item, icon_name)
            shop_selector.addItem(item)
            if provider == current_provider:
                shop_selector.blockSignals(True)
                shop_selector.setCurrentItem(item)
                shop_selector.blockSignals(False)

    def _collapse_shop_detail() -> None:
        shop_state["shop_id"] = ""
        shop_state["row_id"] = ""
        shop_state["provider"] = ""
        shop_selector.blockSignals(True)
        shop_selector.clearSelection()
        shop_selector.setCurrentItem(None)
        shop_selector.blockSignals(False)
        _render_shop_detail()

    def _on_shop_selector_clicked(item: QListWidgetItem) -> None:
        payload = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if not isinstance(payload, dict):
            return
        kind = payload.get("kind")
        if kind == "shop":
            shop_state["shop_id"] = str(payload.get("shop_id", ""))
            shop_state["row_id"] = ""
            shop_state["provider"] = ""
            _render_shop_detail()
            return
        if kind == "stock":
            shop_state["shop_id"] = str(payload.get("shop_id", ""))
            shop_state["row_id"] = str(payload.get("row_id", ""))
            shop_state["provider"] = ""
            _render_shop_detail()
            return
        if kind == "provider":
            shop_state["provider"] = str(payload.get("provider", ""))
            shop_state["shop_id"] = ""
            shop_state["row_id"] = ""
            _render_shop_detail()
            return
        if kind in {"service", "vendor_action"}:
            source = SHOP_SERVICES if kind == "service" else SHOP_VENDOR_ACTIONS
            service_row = source.get(str(payload.get("id", "")), {})
            shop_state["provider"] = str(service_row.get("provider", ""))
            shop_state["shop_id"] = ""
            shop_state["row_id"] = ""
            shop_state["service_kind"] = str(kind)
            shop_state["service_id"] = str(payload.get("id", ""))
            _render_shop_detail()
            _refresh_service_preview()

    def _on_sell_item_clicked(item: QListWidgetItem) -> None:
        item_name = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if isinstance(item_name, str):
            shop_state["sell_item"] = item_name
            _refresh_transaction_panel()

    def _on_service_clicked(item: QListWidgetItem) -> None:
        payload = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if isinstance(payload, dict):
            shop_state["service_kind"] = str(payload.get("kind", ""))
            shop_state["service_id"] = str(payload.get("id", ""))
            _refresh_service_preview()

    shop_search.textChanged.connect(lambda _text="": (_populate_shop_selector(), _render_shop_detail()))
    shop_selector.itemClicked.connect(_on_shop_selector_clicked)
    shop_selector.currentItemChanged.connect(lambda current, _previous: _on_shop_selector_clicked(current) if current is not None else None)
    sell_inventory.itemClicked.connect(_on_sell_item_clicked)
    sell_inventory.currentItemChanged.connect(lambda current, _previous: _on_sell_item_clicked(current) if current is not None else None)
    shop_mode_tabs.currentChanged.connect(lambda _index=0: _refresh_transaction_panel())
    for amount, btn in shop_quantity_buttons.items():
        btn.clicked.connect(lambda _=False, qty=amount: _set_quantity(qty))
    shop_custom_qty.valueChanged.connect(lambda _value=1: _refresh_transaction_panel())
    shop_all_qty.clicked.connect(lambda _=False: _set_all_quantity())
    shop_action_btn.clicked.connect(lambda _=False: _apply_shop_transaction())
    service_list.itemClicked.connect(_on_service_clicked)
    service_list.currentItemChanged.connect(lambda current, _previous: _on_service_clicked(current) if current is not None else None)
    service_qty.valueChanged.connect(lambda _value=1: _refresh_service_preview())
    service_use_btn.clicked.connect(lambda _=False: _apply_service_transaction())
    global_history_btn.toggled.connect(lambda checked=False: global_history.setVisible(bool(checked)))
    shop_collapse_btn.clicked.connect(lambda _=False: _collapse_shop_detail())

    _populate_shop_selector()
    _populate_services()
    _render_shop_detail()

    tabs.addTab(shop_tab, "Shop")
    tabs.setTabToolTip(tabs.indexOf(shop_tab), "Browse source-backed NPC shops and vendor services")

    # ---- Quests tab --------------------------------------------------------
    quests_tab = QWidget()
    q_layout = QVBoxLayout(quests_tab)
    q_layout.setContentsMargins(12, 12, 12, 12)
    q_layout.setSpacing(8)

    quest_top = QWidget()
    quest_top_layout = QHBoxLayout(quest_top)
    quest_top_layout.setContentsMargins(0, 0, 0, 0)
    quest_points_label = QLabel(f"Quest points: {int(player_data.get('quest_points', 0) or 0)}")
    quest_points_label.setStyleSheet("font-weight: 600; color: palette(text);")
    sort_label = QLabel("Sort")
    sort_label.setStyleSheet(f"color: {dim_text_css(sort_label)};")
    quest_sort_combo = QComboBox()
    quest_sort_combo.setObjectName("questSortCombo")
    quest_sort_modes = (
        "Release Order",
        "Progress",
        "Difficulty",
        "Free/Members",
        "Timeline",
        "Length",
    )
    quest_sort_combo.addItems(list(quest_sort_modes))
    quest_top_layout.addWidget(quest_points_label)
    quest_top_layout.addStretch(1)
    quest_top_layout.addWidget(sort_label)
    quest_top_layout.addWidget(quest_sort_combo)
    q_layout.addWidget(quest_top)

    difficulty_order = {"Novice": 0, "Intermediate": 1, "Experienced": 2, "Master": 3, "Grandmaster": 4, "Special": 5}
    length_order = {
        "Short": 0,
        "Short to Medium": 1,
        "Medium": 2,
        "Medium to Long": 3,
        "Long": 4,
        "Long to Very Long": 5,
        "Very Long": 6,
        "Very, Very Long": 7,
    }
    timeline_order = {"Fifth Age": 0, "Ambiguous": 1, "Sixth Age": 2}

    quest_filter_row = QWidget()
    quest_filter_layout = QHBoxLayout(quest_filter_row)
    quest_filter_layout.setContentsMargins(0, 0, 0, 0)
    quest_filter_layout.setSpacing(8)

    hide_completed_cb = QCheckBox("Hide completed")
    hide_completed_cb.setObjectName("questHideCompletedCheck")
    hide_locked_cb = QCheckBox("Hide unable to start")
    hide_locked_cb.setObjectName("questHideLockedCheck")

    access_filter_combo = QComboBox()
    access_filter_combo.setObjectName("questAccessFilterCombo")
    access_filter_combo.addItems(("All access", "Free quests", "Members quests"))

    difficulty_filter_combo = QComboBox()
    difficulty_filter_combo.setObjectName("questDifficultyFilterCombo")
    difficulty_filter_combo.addItems(("All difficulties", *difficulty_order.keys()))

    length_filter_combo = QComboBox()
    length_filter_combo.setObjectName("questLengthFilterCombo")
    length_filter_combo.addItems(("All lengths", *length_order.keys()))

    timeline_filter_combo = QComboBox()
    timeline_filter_combo.setObjectName("questTimelineFilterCombo")
    timeline_filter_combo.addItems(("All timelines", *timeline_order.keys()))

    quest_filter_summary = QLabel("")
    quest_filter_summary.setObjectName("questFilterSummaryLabel")
    quest_filter_summary.setStyleSheet(f"color: {dim_text_css(quest_filter_summary)};")

    def _quest_filter_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"color: {dim_text_css(label)};")
        return label

    quest_filter_layout.addWidget(hide_completed_cb)
    quest_filter_layout.addWidget(hide_locked_cb)
    for label_text, combo in (
        ("Access", access_filter_combo),
        ("Difficulty", difficulty_filter_combo),
        ("Length", length_filter_combo),
        ("Timeline", timeline_filter_combo),
    ):
        quest_filter_layout.addWidget(_quest_filter_label(label_text))
        quest_filter_layout.addWidget(combo)
    quest_filter_layout.addStretch(1)
    quest_filter_layout.addWidget(quest_filter_summary)
    q_layout.addWidget(quest_filter_row)

    quest_scroll = QScrollArea()
    quest_scroll.setWidgetResizable(True)
    quest_scroll.setStyleSheet("border: none;")
    quest_content = QWidget()
    quest_content_layout = QVBoxLayout(quest_content)
    quest_content_layout.setContentsMargins(0, 0, 0, 0)
    quest_content_layout.setSpacing(10)

    def _short_stage_blocker_text(reasons: tuple) -> str:
        if not reasons:
            return ""
        shown = [str(reason) for reason in reasons[:3]]
        extra = len(reasons) - len(shown)
        if extra > 0:
            shown.append(f"+{extra} more")
        return "Blocked: " + ", ".join(shown)

    def _quest_choice_button_name(quest_id: str, route_id: str) -> str:
        safe_route = "".join(ch if ch.isalnum() else "_" for ch in str(route_id).lower()).strip("_")
        return f"questChoice_{quest_id}_{safe_route}"

    def _short_choice_text(choice_rows: tuple) -> str:
        if not choice_rows:
            return ""
        labels = tuple(
            str(option.get("label") or option.get("route_id") or "")
            for option in tuple(choice_rows[0].get("options", ()) or ())
            if option
        )
        if not labels:
            return "Choose path"
        return "Choose path: " + " or ".join(labels)

    def _quest_status_text(quest_id: str, state: dict, quest: dict) -> str:
        if state.get("completed"):
            return "Completed"
        if state.get("started"):
            blocker_text = _short_stage_blocker_text(
                quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
            )
            if blocker_text:
                return blocker_text
            return f"Stage {int(state.get('progress', 0) or 0)}/{int(quest.get('stages', 1) or 1)}"
        choice_text = _short_choice_text(quest_current_stage_choices_pure(player_data, quest_id, QUEST_DATA))
        if choice_text:
            return choice_text
        return "Not started"

    def _quest_button_text(state: dict) -> str:
        if state.get("completed"):
            return "Completed"
        if state["started"] and state["progress"] > 0:
            return "Continue quest"
        return "Start quest"

    expanded_quests = {}

    def _quest_progress_rank(q_state: dict) -> int:
        if q_state.get("started") and not q_state.get("completed"):
            return 0
        if not q_state.get("completed"):
            return 1
        return 2

    def _quest_sort_key(item: tuple[str, dict], mode: str) -> tuple:
        quest_id, quest = item
        q_state = quest_state_pure(player_data, quest_id)
        release_key = str(quest.get("release_date", "9999-99-99"))
        release_order = int(quest.get("release_order", 9999) or 9999)
        name = str(quest.get("display_name", quest_id))
        if mode == "Progress":
            return (_quest_progress_rank(q_state), release_order, release_key, name)
        if mode == "Difficulty":
            return (difficulty_order.get(str(quest.get("difficulty", "")), 99), release_order, release_key, name)
        if mode == "Free/Members":
            return (1 if quest.get("members") else 0, release_order, release_key, name)
        if mode == "Timeline":
            return (timeline_order.get(str(quest.get("timeline", "")), 99), release_order, release_key, name)
        if mode == "Length":
            return (length_order.get(str(quest.get("length", "")), 99), release_order, release_key, name)
        return (release_order, release_key, name)

    def _short_lock_text(reasons: tuple) -> str:
        if not reasons:
            return ""
        shown = [str(reason) for reason in reasons[:5]]
        extra = len(reasons) - len(shown)
        if extra > 0:
            shown.append(f"+{extra} more")
        return "Requires: " + ", ".join(shown)

    def _quest_matches_filters(quest_id: str, quest: dict) -> bool:
        availability = quest_availability_state_pure(player_data, quest_id, QUEST_DATA)
        if hide_completed_cb.isChecked() and availability == "completed":
            return False
        if hide_locked_cb.isChecked() and availability == "locked":
            return False

        access_filter = access_filter_combo.currentText()
        if access_filter == "Free quests" and quest.get("members"):
            return False
        if access_filter == "Members quests" and not quest.get("members"):
            return False

        difficulty_filter = difficulty_filter_combo.currentText()
        if difficulty_filter != "All difficulties" and str(quest.get("difficulty", "")) != difficulty_filter:
            return False

        length_filter = length_filter_combo.currentText()
        if length_filter != "All lengths" and str(quest.get("length", "")) != length_filter:
            return False

        timeline_filter = timeline_filter_combo.currentText()
        if timeline_filter != "All timelines" and str(quest.get("timeline", "")) != timeline_filter:
            return False
        return True

    def _clear_quest_cards() -> None:
        while quest_content_layout.count():
            item = quest_content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def _set_quest_route_choice(quest_id: str, route_id: str) -> None:
        if on_set_quest_route_choice is not None:
            if on_set_quest_route_choice(quest_id, route_id) is False:
                return
        else:
            new_data, ok = apply_quest_route_choice_pure(player_data, quest_id, QUEST_DATA, route_id)
            if not ok:
                return
            player_data.update(new_data)
        warn.setText("")
        _rebuild_quest_cards()

    def _set_quest_active(quest_id: str, button: QPushButton, status_label: QLabel) -> None:
        if quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA):
            return
        choice_text = _short_choice_text(quest_current_stage_choices_pure(player_data, quest_id, QUEST_DATA))
        if choice_text:
            warn.setText(choice_text)
            return
        if quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA) and not can_attempt_quest_review_pure(player_data, quest_id, QUEST_DATA):
            return
        if on_set_quest is not None and on_set_quest(quest_id) is False:
            return
        state["active"] = "Quests"
        on_save_skill("Quests")
        _refresh_active_label()
        q_state = quest_state_pure(player_data, quest_id)
        quest = QUEST_DATA.get(quest_id, {})
        button.setText("Currently active")
        button.setEnabled(False)
        status_label.setText(_quest_status_text(quest_id, q_state, quest))

    def _add_quest_card(quest_id: str, quest: dict) -> None:
        q_state = quest_state_pure(player_data, quest_id)
        lock_reasons = () if q_state.get("completed") else quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA)
        lock_text = _short_lock_text(lock_reasons)
        stage_blocker_reasons = () if q_state.get("completed") else quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
        stage_blocker_text = _short_stage_blocker_text(stage_blocker_reasons)
        choice_rows = () if q_state.get("completed") else quest_current_stage_choices_pure(player_data, quest_id, QUEST_DATA)
        choice_text = _short_choice_text(choice_rows)
        if choice_text and not stage_blocker_text:
            stage_blocker_text = choice_text
        active_this_quest = state["active"] == "Quests" and player_data.get("current_quest") == quest_id
        default_expanded = bool(choice_rows or (q_state.get("started") and not q_state.get("completed") and active_this_quest))
        expanded = expanded_quests.get(quest_id, default_expanded)

        card = QWidget()
        card.setObjectName(f"questCard_{quest_id}")
        card.setStyleSheet("border: 1px solid palette(mid); border-radius: 6px; background: palette(base);")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(6)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        toggle_btn = QPushButton("v" if expanded else ">")
        toggle_btn.setObjectName(f"questToggle_{quest_id}")
        toggle_btn.setFixedWidth(28)
        toggle_btn.setToolTip("Show or hide quest journal")
        title = QLabel(str(quest.get("display_name", quest_id)))
        title.setStyleSheet("font-weight: 700; color: palette(text);")
        title.setToolTip(stage_blocker_text or lock_text or str(quest.get("source", "")))
        status = QLabel(_quest_status_text(quest_id, q_state, quest))
        status.setStyleSheet(f"color: {dim_text_css(status)};")
        quest_btn = QPushButton(_quest_button_text(q_state))
        quest_btn.setObjectName(f"questAction_{quest_id}")
        quest_review_ready = can_attempt_quest_review_pure(player_data, quest_id, QUEST_DATA)
        quest_btn.setEnabled(
            not q_state.get("completed")
            and state["active"] != "Quests"
            and not lock_reasons
            and not choice_rows
            and (not stage_blocker_reasons or quest_review_ready)
        )
        if lock_text:
            quest_btn.setToolTip(lock_text)
            header.setToolTip(lock_text)
        if stage_blocker_text:
            quest_btn.setToolTip(stage_blocker_text)
            header.setToolTip(stage_blocker_text)
        if active_this_quest:
            quest_btn.setText("Currently active")
            quest_btn.setEnabled(False)
        quest_btn.clicked.connect(lambda _=False, qid=quest_id, btn=quest_btn, lbl=status: _set_quest_active(qid, btn, lbl))
        header_layout.addWidget(toggle_btn)
        header_layout.addWidget(title)
        header_layout.addWidget(status)
        header_layout.addStretch(1)
        header_layout.addWidget(quest_btn)
        card_layout.addWidget(header)

        body = QWidget()
        body.setObjectName(f"questBody_{quest_id}")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 4, 0, 0)
        body_layout.setSpacing(5)

        if not q_state.get("started"):
            start = QLabel(str(quest.get("start_point", "")))
            start.setWordWrap(True)
            start.setStyleSheet("color: palette(text);")
            body_layout.addWidget(start)
        requirements = tuple(quest.get("requirements", ()) or ())
        if requirements:
            req_label = QLabel("Requires: " + ", ".join(str(req) for req in requirements))
            req_label.setWordWrap(True)
            req_label.setStyleSheet(f"color: {dim_text_css(req_label)};")
            body_layout.addWidget(req_label)
        unlocks = tuple(quest.get("unlocks", ()) or ())
        if unlocks:
            unlock_label = QLabel("Unlocks: " + ", ".join(str(unlock) for unlock in unlocks))
            unlock_label.setWordWrap(True)
            unlock_label.setStyleSheet(f"color: {dim_text_css(unlock_label)};")
            body_layout.addWidget(unlock_label)
        for choice in choice_rows:
            prompt_label = QLabel(str(choice.get("prompt") or "Choose path"))
            prompt_label.setWordWrap(True)
            prompt_label.setStyleSheet("font-weight: 600; color: palette(text);")
            body_layout.addWidget(prompt_label)
            choice_row = QWidget()
            choice_row_layout = QHBoxLayout(choice_row)
            choice_row_layout.setContentsMargins(0, 0, 0, 0)
            choice_row_layout.setSpacing(6)
            for option in tuple(choice.get("options", ()) or ()):
                route_id = str(option.get("route_id") or "")
                label = str(option.get("label") or route_id or "Choose")
                choice_btn = QPushButton(label)
                choice_btn.setObjectName(_quest_choice_button_name(quest_id, route_id))
                choice_btn.setToolTip(str(option.get("description") or label))
                choice_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                choice_btn.setStyleSheet(
                    "QPushButton { padding: 4px 10px; border: 1px solid palette(mid);"
                    " border-radius: 6px; color: palette(text); background: palette(base); }"
                    " QPushButton:hover { border-color: #4CAF50; }"
                )
                choice_btn.clicked.connect(
                    lambda _=False, qid=quest_id, rid=route_id: _set_quest_route_choice(qid, rid)
                )
                choice_row_layout.addWidget(choice_btn)
            choice_row_layout.addStretch(1)
            body_layout.addWidget(choice_row)
        for row in quest_journal_rows_pure(player_data, quest_id, QUEST_DATA):
            stage_label = QLabel(f"Stage {row['stage']}")
            stage_label.setStyleSheet("font-weight: 600; color: palette(text);")
            body_layout.addWidget(stage_label)
            for line in row.get("lines", ()):
                text = str(line)
                if row.get("completed"):
                    text = f"<s>{text}</s>"
                line_label = QLabel(text)
                line_label.setWordWrap(True)
                line_label.setTextFormat(Qt.TextFormat.RichText)
                line_label.setStyleSheet("color: palette(text);")
                body_layout.addWidget(line_label)

        body.setVisible(expanded)
        card_layout.addWidget(body)

        def _toggle_quest() -> None:
            new_expanded = not body.isVisible()
            expanded_quests[quest_id] = new_expanded
            body.setVisible(new_expanded)
            toggle_btn.setText("v" if new_expanded else ">")

        toggle_btn.clicked.connect(_toggle_quest)
        quest_content_layout.addWidget(card)

    def _rebuild_quest_cards() -> None:
        _clear_quest_cards()
        mode = quest_sort_combo.currentText() or "Release Order"
        visible_count = 0
        for quest_id, quest in sorted(QUEST_DATA.items(), key=lambda item: _quest_sort_key(item, mode)):
            if not _quest_matches_filters(quest_id, quest):
                continue
            _add_quest_card(quest_id, quest)
            visible_count += 1
        if visible_count == 0:
            empty_label = QLabel("No quests match the current filters.")
            empty_label.setObjectName("questEmptyFilterLabel")
            empty_label.setWordWrap(True)
            empty_label.setStyleSheet(f"color: {dim_text_css(empty_label)};")
            quest_content_layout.addWidget(empty_label)
        quest_filter_summary.setText(f"Showing {visible_count}/{len(QUEST_DATA)}")
        quest_content_layout.addStretch(1)

    quest_sort_combo.currentTextChanged.connect(lambda _text: _rebuild_quest_cards())
    hide_completed_cb.toggled.connect(lambda _checked: _rebuild_quest_cards())
    hide_locked_cb.toggled.connect(lambda _checked: _rebuild_quest_cards())
    for combo in (access_filter_combo, difficulty_filter_combo, length_filter_combo, timeline_filter_combo):
        combo.currentTextChanged.connect(lambda _text: _rebuild_quest_cards())
    _rebuild_quest_cards()
    quest_scroll.setWidget(quest_content)
    q_layout.addWidget(quest_scroll, 1)
    tabs.addTab(quests_tab, "Quests")
    if os.path.exists(ach_icon_path := os.path.join(current_dir, "icon", "achievement_icon.png")):
        tabs.setTabIcon(tabs.indexOf(quests_tab), QIcon(ach_icon_path))
    tabs.setTabToolTip(tabs.indexOf(quests_tab), "View quest journals and active quest progress")

    # Stats tab (inline, single-skill view with icon selectors)
    stats_tab = QWidget()
    st_layout = QVBoxLayout(stats_tab)
    st_layout.setContentsMargins(12, 12, 12, 12)
    st_layout.setSpacing(8)

    # Skill selectors with icons
    selector = QWidget()
    sel_layout = QHBoxLayout(selector)
    sel_layout.setSpacing(12)
    sel_layout.setContentsMargins(0, 0, 0, 0)

    # Helper to create a details panel for a specific skill
    def _mk_skill_details(skill_name: str) -> QWidget:
        block = QWidget()
        b_layout = QVBoxLayout(block)
        b_layout.setSpacing(8)
        title = QLabel(f"{skill_name} Stats")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        b_layout.addWidget(title)
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)
        level = player_data.get(f"{skill_name.lower()}_level", 1)
        exp = round(player_data.get(f"{skill_name.lower()}_exp", 0), 1)
        grid.addWidget(QLabel(f"{skill_name} Level:"), 0, 0)
        grid.addWidget(QLabel(str(level)), 0, 1)
        grid.addWidget(QLabel("Total Experience:"), 1, 0)
        grid.addWidget(QLabel(f"{exp:,}"), 1, 1)
        if level < 99:
            exp_to_next = round(max(0, EXP_TABLE[level] - exp), 1)
            grid.addWidget(QLabel("Experience to Next Level:"), 2, 0)
            grid.addWidget(QLabel(f"{exp_to_next:,}"), 2, 1)
        prog = QProgressBar()
        try:
            progress_percentage = (exp - EXP_TABLE[level - 1]) / (EXP_TABLE[level] - EXP_TABLE[level - 1]) * 100
            prog.setValue(int(max(0, min(100, progress_percentage))))
        except Exception:
            prog.setValue(0)
        grid.addWidget(QLabel("Level Progress:"), 3, 0)
        grid.addWidget(prog, 3, 1)
        b_layout.addLayout(grid)
        return block

    # Details container (will switch based on selected skill)
    details_container = QWidget()
    details_layout = QVBoxLayout(details_container)
    details_layout.setContentsMargins(0, 0, 0, 0)

    # Skill selectors come from the registry so every playable skill (Fletching
    # and any future skill) gets a Stats panel automatically. Icons resolve by
    # convention; the achievement icon is a safe fallback for skills lacking art.
    _ach_fallback = os.path.join(current_dir, "icon", "achievement_icon.png")
    skills_info = [
        (name, skill_icon_path_for(name) or _ach_fallback)
        for name in playable_review_skill_names()
    ]

    # Import here to keep headless safety for static analyzers
    try:
        from aqt.qt import QToolButton as StatsToolButton  # type: ignore
    except Exception:
        StatsToolButton = QPushButton  # fallback for typing

    button_group = QButtonGroup()
    button_group.setExclusive(True)
    buttons = {}
    for idx, (name, icon_path) in enumerate(skills_info):
        btn = StatsToolButton()
        btn.setCheckable(True)
        btn.setToolTip(name)
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
        # Small label under icon
        btn.setText(name)
        if hasattr(btn, "setToolButtonStyle"):
            try:
                btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)  # type: ignore[attr-defined]
            except Exception:
                pass
        btn.setIconSize(QSize(48, 48))
        btn.setAutoRaise(True)
        # Visual feedback styles
        btn.setStyleSheet(
            """
            QToolButton { border: 1px solid #cccccc; border-radius: 8px; padding: 6px; }
            QToolButton:hover { border-color: #999999; }
            QToolButton:checked { border: 2px solid #4CAF50; background-color: #e8f5e9; }
            """
        )
        button_group.addButton(btn, idx)
        sel_layout.addWidget(btn)
        buttons[name] = btn
        # Connect per-button click to select and persist
        btn.clicked.connect(lambda _checked=False, n=name: (
            _select_skill(n),
            (mw and getattr(mw, 'col', None) and mw.col.set_config("ankiscape_stats_selected_skill", n))
        ))

    st_layout.addWidget(selector)

    # Update details when a skill is selected
    def _select_skill(skill_name: str):
        # Clear previous content. hide()+setParent(None) before deleteLater so
        # the old details block is removed from view immediately; deleteLater
        # alone is async and would briefly overlap the new block.
        child = details_layout.takeAt(0)
        while child:
            w = child.widget()
            if w is not None:
                w.hide()
                w.setParent(None)
                w.deleteLater()
            child = details_layout.takeAt(0)
        # Add new details
        details_layout.addWidget(_mk_skill_details(skill_name))

    # No idClicked usage; handled per-button above

    # Initial selection
    # Load persisted selection if available; fall back to current_skill then Mining
    persisted = None
    try:
        if mw and getattr(mw, 'col', None):
            persisted = mw.col.get_config("ankiscape_stats_selected_skill", None)
    except Exception:
        persisted = None
    initial_skill = persisted if persisted in {n for n, _ in skills_info} else (current_skill if current_skill in {n for n, _ in skills_info} else "Mining")
    initial_index = next((i for i, (n, _) in enumerate(skills_info) if n == initial_skill), 0)
    button_group.button(initial_index).setChecked(True)
    _select_skill(initial_skill)

    st_layout.addWidget(details_container)
    # Defer adding Stats tab until after Bank to satisfy desired ordering (Bank then Stats)
    ach_icon_path = os.path.join(current_dir, "icon", "achievement_icon.png")

    # Achievements tab
    # Bank tab (all inventory items)
    bank_tab = QWidget()
    bk_layout = QVBoxLayout(bank_tab)
    bk_layout.setContentsMargins(12, 12, 12, 12)
    bk_layout.setSpacing(8)

    # Carried inventory overlay — the 28-slot pack the review loop draws from and
    # banks when full. Collapsible header. Casual packing is inferred (even split
    # for processing, action-filled for gathering) with approximate bank runs;
    # players who want to tune it use the advanced 4x7 grid below.
    def _carried_panel_summary_text() -> str:
        carried = player_data.get("carried_inventory") or {}
        run = player_data.get("skilling_bank_run") or {}
        total_slots = 0
        carried_targets = 0
        for view in carried.values():
            if isinstance(view, dict) and view:
                total_slots += inventory_pure.carried_slots_used(view, frozenset())
                carried_targets += 1
        if run:
            status = f"Banking… {int(run.get('reviews_remaining', 0))} review(s) left"
        elif total_slots:
            status = f"{total_slots} slot(s) held across {carried_targets} target(s)"
        else:
            status = "Pack empty — nothing carried yet"
        return (
            f"{status}. The pack fills to {inventory_pure.CARRIED_CAPACITY} slots "
            "as you gather or process, then a bank run costs one review."
        )

    carried_header = QPushButton("▸  Carried inventory")
    carried_header.setObjectName("carriedInventoryHeader")
    carried_header.setCheckable(True)
    carried_header.setChecked(False)
    carried_header.setStyleSheet("QPushButton { text-align: left; font-weight: 600; border: none; padding: 4px 2px; }")

    carried_body = QWidget()
    carried_body.setVisible(False)
    cb_layout = QVBoxLayout(carried_body)
    cb_layout.setContentsMargins(10, 2, 4, 6)
    cb_layout.setSpacing(6)

    # Keep/Drop toggle — only meaningful for a gathering target (power-gather =
    # drop the product for the fastest XP, no banking). Absent otherwise.
    if carried_keep_drop_state is not None:
        keep_drop_check = QCheckBox("Drop gathered products (power-gather, no banking)")
        keep_drop_check.setObjectName("carriedKeepDropCheck")
        keep_drop_check.setChecked(carried_keep_drop_state == "drop")
        if on_set_carried_keep_drop is not None:
            keep_drop_check.toggled.connect(lambda checked: on_set_carried_keep_drop(bool(checked)))
        cb_layout.addWidget(keep_drop_check)

    # Carried-pack section — one control with two mutually-exclusive views of the
    # same 28 slots, switched by an Auto | Custom pill:
    #   * Auto   — pick a supply mode (Balanced/Max output/Max safety); the game
    #              auto-fills food + stat potions and refills them at bank runs.
    #   * Custom — hand-arrange an exact {item: count} 28-slot layout the game
    #              refills verbatim.
    # The same section is built on both the Equipment and Bank tabs, so the
    # registries below keep every instance in sync: one grid refresher per section
    # repaints its own 28 cells, one switch setter per section reflects the
    # advanced flag without re-firing the backend, and one auto-view refresher per
    # section keeps its supply summary + bank-run text (and pack-mode combo)
    # current. carried_mode_state is the single source of truth the bank context
    # menu reads to decide whether "Add to carried layout" applies.
    carried_grid_refreshers: list = []
    carried_switch_setters: list = []
    carried_section_refreshers: list = []
    carried_mode_state = {"advanced": bool(carried_advanced_state)}
    _dim_cell = dim_text_css(carried_body)
    _CARRIED_CELL_FILLED_CSS = (
        "QPushButton { border: 1px solid palette(mid); border-radius: 4px; "
        "background: transparent; color: palette(text); font-size: 9px; padding: 2px; }"
        "QPushButton:hover { border: 1px solid palette(highlight); }"
    )
    _CARRIED_CELL_EMPTY_CSS = (
        "QPushButton { border: 1px dashed palette(mid); border-radius: 4px; "
        "background: transparent; color: " + _dim_cell + "; font-size: 9px; }"
        "QPushButton:hover { border: 1px solid palette(highlight); }"
    )

    def _refresh_carried_layout_grid() -> None:
        for _refresh in carried_grid_refreshers:
            _refresh()

    def _refresh_carried_sections() -> None:
        for _refresh in carried_section_refreshers:
            _refresh()

    def _pack_pickable_items() -> list:
        """Distinct bank item names offered by the empty-slot picker."""
        inv = player_data.get("inventory", {}) or {}
        names: list = []
        for _label, rows in grouped_inventory(inv):
            for name, _amount, _asset in rows:
                if name and name not in names:
                    names.append(name)
        return names

    def _prompt_add_to_pack() -> None:
        """Empty-slot click: pick a bank item to add to the custom pack."""
        if on_add_to_carried_layout is None:
            return
        names = _pack_pickable_items()
        if not names:
            QMessageBox.information(dialog, "Carried pack", "Your bank is empty — nothing to add.")
            return
        choice, ok = QInputDialog.getItem(dialog, "Add to carried pack", "Item:", names, 0, False)
        if ok and choice:
            on_add_to_carried_layout(str(choice), 1)
            _refresh_carried_layout_grid()

    def _sync_carried_switches(advanced: bool) -> None:
        carried_mode_state["advanced"] = bool(advanced)
        for setter in carried_switch_setters:
            setter(bool(advanced))

    def _build_carried_pack_section(primary: bool) -> QWidget:
        """One carried-pack control (Auto | Custom pill + both views).

        Built on both the Equipment and Bank tabs; `primary` (Equipment) carries
        the canonical object names the tests query, while the secondary instance
        suffixes "Bank" so every object name stays unique in the widget tree.
        """
        name_suffix = "" if primary else "Bank"
        container = QWidget()
        section_layout = QVBoxLayout(container)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(6)

        # --- Auto | Custom segmented switch ---
        def _switch_css(side: str, active: bool) -> str:
            radius = (
                "border-top-left-radius:6px;border-bottom-left-radius:6px;border-right:none;"
                if side == "left"
                else "border-top-right-radius:6px;border-bottom-right-radius:6px;"
            )
            if active:
                face = "background:palette(highlight);color:palette(highlighted-text);font-weight:600;"
            else:
                face = f"background:transparent;color:{dim_text_css(container)};"
            return f"QPushButton{{border:1px solid palette(mid);{radius}padding:3px 18px;font-size:11px;{face}}}"

        auto_btn = QPushButton("Auto")
        auto_btn.setObjectName(f"carriedModeAuto{name_suffix}")
        auto_btn.setCheckable(True)
        custom_btn = QPushButton("Custom")
        custom_btn.setObjectName(f"carriedModeCustom{name_suffix}")
        custom_btn.setCheckable(True)

        auto_view = QWidget()
        custom_view = QWidget()

        def _apply_mode(advanced: bool) -> None:
            auto_btn.setChecked(not advanced)
            custom_btn.setChecked(advanced)
            auto_btn.setStyleSheet(_switch_css("left", not advanced))
            custom_btn.setStyleSheet(_switch_css("right", advanced))
            auto_view.setVisible(not advanced)
            custom_view.setVisible(advanced)

        carried_switch_setters.append(_apply_mode)

        def _on_switch(advanced: bool) -> None:
            _apply_mode(bool(advanced))
            if on_set_carried_advanced is not None:
                on_set_carried_advanced(bool(advanced))
            _sync_carried_switches(bool(advanced))

        auto_btn.clicked.connect(lambda _c=False: _on_switch(False))
        custom_btn.clicked.connect(lambda _c=False: _on_switch(True))

        switch_row = QWidget()
        switch_layout = QHBoxLayout(switch_row)
        switch_layout.setContentsMargins(0, 0, 0, 0)
        switch_layout.setSpacing(0)
        switch_layout.addWidget(auto_btn)
        switch_layout.addWidget(custom_btn)
        switch_layout.addStretch(1)
        section_layout.addWidget(switch_row)

        # --- Auto view: supply mode + summary + bank run + Clear inventory ---
        auto_layout = QVBoxLayout(auto_view)
        auto_layout.setContentsMargins(0, 2, 0, 0)
        auto_layout.setSpacing(6)

        supply_mode_row = QWidget()
        supply_mode_layout = QHBoxLayout(supply_mode_row)
        supply_mode_layout.setContentsMargins(0, 0, 0, 0)
        supply_mode_layout.setSpacing(8)
        supply_mode_label = QLabel("Supply mode")
        supply_mode_label.setStyleSheet("color: palette(text);")
        supply_mode_combo = QComboBox()
        supply_mode_combo.setObjectName(f"combatPackModeCombo{name_suffix}")
        for _label, _mode_id in (("Balanced", "balanced"), ("Max output", "max_output"), ("Max safety", "max_safety")):
            supply_mode_combo.addItem(_label, _mode_id)
        supply_mode_combo.setCurrentIndex(max(0, supply_mode_combo.findData(str(player_data.get("combat_pack_mode", "balanced")))))

        def _on_pack_mode(_index: int) -> None:
            if on_set_combat_pack_mode is not None:
                on_set_combat_pack_mode(supply_mode_combo.currentData() or "balanced")
            _refresh_carried_sections()

        supply_mode_combo.currentIndexChanged.connect(_on_pack_mode)
        supply_mode_layout.addWidget(supply_mode_label)
        supply_mode_layout.addWidget(supply_mode_combo, 1)
        auto_layout.addWidget(supply_mode_row)

        supply_summary = QLabel(_combat_loadout_summary_text(player_data))
        supply_summary.setObjectName(f"combatLoadoutSummaryLabel{name_suffix}")
        supply_summary.setWordWrap(True)
        supply_summary.setStyleSheet(f"color: {dim_text_css(supply_summary)};")
        auto_layout.addWidget(supply_summary)

        bank_run_label = QLabel(_combat_bank_run_text())
        bank_run_label.setObjectName(f"combatBankRunLabel{name_suffix}")
        bank_run_label.setWordWrap(True)
        bank_run_label.setStyleSheet(f"color: {dim_text_css(bank_run_label)};")
        auto_layout.addWidget(bank_run_label)

        clear_inv_btn = QPushButton("Clear inventory")
        clear_inv_btn.setObjectName(f"combatClearInventoryButton{name_suffix}")
        clear_inv_btn.setStyleSheet("QPushButton { padding: 2px 10px; }")
        clear_inv_btn.setEnabled(on_unload_combat_loadout is not None)

        def _on_clear_inventory(_checked=False) -> None:
            if on_unload_combat_loadout is not None:
                on_unload_combat_loadout()
            _refresh_carried_sections()

        clear_inv_btn.clicked.connect(_on_clear_inventory)
        clear_inv_row = QWidget()
        clear_inv_layout = QHBoxLayout(clear_inv_row)
        clear_inv_layout.setContentsMargins(0, 0, 0, 0)
        clear_inv_layout.addWidget(clear_inv_btn)
        clear_inv_layout.addStretch(1)
        auto_layout.addWidget(clear_inv_row)
        section_layout.addWidget(auto_view)

        def _refresh_auto_view() -> None:
            supply_summary.setText(_combat_loadout_summary_text(player_data))
            bank_run_label.setText(_combat_bank_run_text())
            _mode = str(player_data.get("combat_pack_mode", "balanced"))
            supply_mode_combo.blockSignals(True)
            supply_mode_combo.setCurrentIndex(max(0, supply_mode_combo.findData(_mode)))
            supply_mode_combo.blockSignals(False)

        carried_section_refreshers.append(_refresh_auto_view)

        # --- Custom view: hand-arranged 28-slot grid + Clear layout ---
        custom_layout = QVBoxLayout(custom_view)
        custom_layout.setContentsMargins(0, 2, 0, 0)
        custom_layout.setSpacing(6)

        _CARRIED_CELL_SIZE = 44
        _CARRIED_CELL_SPACING = 4
        _CARRIED_GRID_COLS = 4
        _CARRIED_GRID_ROWS = inventory_pure.CARRIED_CAPACITY // _CARRIED_GRID_COLS

        cell_buttons: list = []
        cell_items: list = [None] * inventory_pure.CARRIED_CAPACITY

        grid_container = QWidget()
        grid_container.setObjectName(f"carriedLayoutGrid{name_suffix}")
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(0, 4, 0, 4)
        grid_layout.setSpacing(_CARRIED_CELL_SPACING)
        for i in range(inventory_pure.CARRIED_CAPACITY):
            cell_btn = QPushButton()
            cell_btn.setObjectName(f"carriedLayoutCell{name_suffix}::{i}")
            cell_btn.setFlat(True)
            cell_btn.setFixedSize(_CARRIED_CELL_SIZE, _CARRIED_CELL_SIZE)

            def _on_cell_clicked(_checked=False, idx=i):
                name = cell_items[idx]
                if name:
                    if on_add_to_carried_layout is not None:
                        on_add_to_carried_layout(name, -1)
                        _refresh_carried_layout_grid()
                else:
                    _prompt_add_to_pack()

            cell_btn.clicked.connect(_on_cell_clicked)
            grid_layout.addWidget(cell_btn, i // _CARRIED_GRID_COLS, i % _CARRIED_GRID_COLS)
            cell_buttons.append(cell_btn)
        # A plain QWidget's default (Preferred) size policy lets a parent
        # QVBoxLayout compress it below its sizeHint when the dialog is short on
        # room — that would clip a 7-row grid of fixed-size buttons down to a
        # sliver. Fixed policy + an exact sizeHint-matching size guarantees all 28
        # cells always get their real, non-negotiable geometry.
        grid_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        _grid_margins = grid_layout.contentsMargins()
        grid_container.setFixedSize(
            _CARRIED_GRID_COLS * _CARRIED_CELL_SIZE + (_CARRIED_GRID_COLS - 1) * _CARRIED_CELL_SPACING
            + _grid_margins.left() + _grid_margins.right(),
            _CARRIED_GRID_ROWS * _CARRIED_CELL_SIZE + (_CARRIED_GRID_ROWS - 1) * _CARRIED_CELL_SPACING
            + _grid_margins.top() + _grid_margins.bottom(),
        )
        grid_row = QWidget()
        grid_row_layout = QHBoxLayout(grid_row)
        grid_row_layout.setContentsMargins(0, 0, 0, 0)
        grid_row_layout.addWidget(grid_container)
        grid_row_layout.addStretch(1)
        custom_layout.addWidget(grid_row)

        pack_hint = QLabel("Click an empty slot (or right-click a bank item) to add it. Click a filled slot to remove one.")
        pack_hint.setWordWrap(True)
        pack_hint.setStyleSheet(f"color: {dim_text_css(container)}; font-size: 10px;")
        custom_layout.addWidget(pack_hint)

        clear_layout_btn = QPushButton("Clear layout")
        clear_layout_btn.setObjectName(f"carriedLayoutClearButton{name_suffix}")
        clear_layout_btn.setStyleSheet("QPushButton { padding: 2px 10px; }")

        def _on_clear_layout(_checked=False) -> None:
            if on_clear_carried_layout is not None:
                on_clear_carried_layout()
            _refresh_carried_layout_grid()

        clear_layout_btn.clicked.connect(_on_clear_layout)
        clear_layout_row = QWidget()
        clear_layout_row_layout = QHBoxLayout(clear_layout_row)
        clear_layout_row_layout.setContentsMargins(0, 0, 0, 0)
        clear_layout_row_layout.addWidget(clear_layout_btn)
        clear_layout_row_layout.addStretch(1)
        custom_layout.addWidget(clear_layout_row)
        section_layout.addWidget(custom_view)

        def _refresh_grid() -> None:
            if get_carried_layout_cells is not None:
                cells = tuple(get_carried_layout_cells())
            else:
                cells = ((None, 0),) * inventory_pure.CARRIED_CAPACITY
            for idx, cell_button in enumerate(cell_buttons):
                item_name, count = cells[idx] if idx < len(cells) else (None, 0)
                cell_items[idx] = item_name
                if item_name:
                    count = int(count)
                    cell_button.setText(f"{item_name}\n×{count}" if count > 1 else str(item_name))
                    suffix = f" ×{count}" if count > 1 else ""
                    cell_button.setToolTip(f"{item_name}{suffix} — click to remove one")
                    cell_button.setEnabled(on_add_to_carried_layout is not None)
                    cell_button.setStyleSheet(_CARRIED_CELL_FILLED_CSS)
                else:
                    cell_button.setText("+")
                    cell_button.setToolTip("Empty slot — click to add a bank item")
                    cell_button.setEnabled(on_add_to_carried_layout is not None)
                    cell_button.setStyleSheet(_CARRIED_CELL_EMPTY_CSS)

        carried_grid_refreshers.append(_refresh_grid)

        _apply_mode(bool(carried_mode_state["advanced"]))
        _refresh_grid()
        _refresh_auto_view()
        return container

    # The per-enemy loot filter stays on the Equipment tab (with the live combat
    # controls); the Bank keeps a pointer so players still discover it from here.
    carried_pointer = QLabel("Set per-enemy loot filters in the Equipment tab.")
    carried_pointer.setObjectName("carriedEquipmentPointer")
    carried_pointer.setWordWrap(True)
    carried_pointer.setStyleSheet(f"color: {dim_text_css(carried_pointer)};")
    cb_layout.addWidget(carried_pointer)

    carried_summary = QLabel(_carried_panel_summary_text())
    carried_summary.setObjectName("carriedInventorySummary")
    carried_summary.setWordWrap(True)
    carried_summary.setStyleSheet(f"color: {dim_text_css(carried_summary)};")
    cb_layout.addWidget(carried_summary)

    # A second carried-pack section (secondary instance) so the Auto|Custom
    # switch and the 28-slot grid are reachable right here on the Bank tab.
    cb_layout.addWidget(_build_carried_pack_section(primary=False))

    def _toggle_carried_body(checked: bool) -> None:
        carried_body.setVisible(bool(checked))
        carried_header.setText(("▾  Carried inventory") if checked else ("▸  Carried inventory"))

    carried_header.toggled.connect(_toggle_carried_body)

    def _refresh_carried_panel() -> None:
        carried_summary.setText(_carried_panel_summary_text())
        _refresh_carried_sections()
        _refresh_carried_layout_grid()

    bk_layout.addWidget(carried_header)
    bk_layout.addWidget(carried_body)

    bank_list = QListWidget()
    bank_list.setIconSize(QSize(28, 28))
    bank_list.setAlternatingRowColors(True)
    bank_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    # Inventory is grouped by item-registry category (Ores, Logs, ..., Fletched,
    # Materials) so newly registered items appear cleanly without per-skill
    # branches. Each item's icon comes from its ItemDefinition.asset_path, with a
    # legacy image-map fallback for anything predating the manifest.
    _legacy_icon_maps = (
        ORE_IMAGES,
        TREE_IMAGES,
        BAR_IMAGES,
        GEM_IMAGES,
        CRAFTED_ITEM_IMAGES,
        FLETCHED_ITEM_IMAGES,
        FIREMAKING_ITEM_IMAGES,
        FISHING_ITEM_IMAGES,
        COOKING_ITEM_IMAGES,
    )

    def _bank_icon_path(item_name: str, asset_path) -> Optional[str]:
        if asset_path and os.path.exists(asset_path):
            return asset_path
        for image_map in _legacy_icon_maps:
            candidate = image_map.get(item_name)
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    def _make_header_item(label: str, marker: str) -> QListWidgetItem:
        header = QListWidgetItem(label)
        header.setFlags(Qt.ItemFlag.NoItemFlags)
        header_font = header.font()
        header_font.setBold(True)
        header.setFont(header_font)
        header.setData(Qt.ItemDataRole.UserRole, marker)
        return header

    # Equip/Unequip mutate player_data via the backend handlers, so the Bank
    # inventory and the Equipment tab must both re-read after an action. The
    # Equipment tab registers its repaint here so a single call refreshes both
    # without rebuilding the whole dialog.
    _equipment_refreshers: list = []

    def _refresh_equipment_views() -> None:
        _populate_bank_list()
        _populate_death_office()
        for refresher in _equipment_refreshers:
            refresher()
        for refresher in _combat_setup_refreshers:
            refresher()
        if state.get("skill") == _COMBAT_HUB_NAME:
            _render_panel()

    def _populate_bank_list() -> None:
        _refresh_carried_panel()
        bank_list.clear()
        inv = player_data.get("inventory", {}) or {}
        groups = grouped_inventory(inv)
        if not groups:
            empty = QListWidgetItem("Your bank is empty — train a skill to gather items.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            bank_list.addItem(empty)
        for category_label, rows in groups:
            bank_list.addItem(_make_header_item(category_label, "__header__"))
            for item_name, amount, asset_path in rows:
                li = QListWidgetItem(f"{item_name} x{amount}")
                icon_path = _bank_icon_path(item_name, asset_path)
                if icon_path:
                    li.setIcon(QIcon(icon_path))
                # The plain item name is stashed on every inventory row so the
                # right-click handler can resolve equippability without parsing
                # the "Name xN" label back apart.
                li.setData(Qt.ItemDataRole.UserRole, item_name)
                if is_equippable_item(item_name):
                    ok, reason = can_equip_item_pure(item_name, EQUIPMENT_ITEM_DATA, player_data)
                    li.setToolTip(equipment_full_tooltip(item_name, "" if ok else reason))
                bank_list.addItem(li)

    claims_box = QWidget()
    claims_box.setObjectName("bankClaimsBox")
    claims_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
    claims_layout = QVBoxLayout(claims_box)
    claims_layout.setContentsMargins(0, 0, 0, 0)
    claims_layout.setSpacing(6)

    death_office_box = QWidget()
    death_office_box.setObjectName("deathOfficeBox")
    death_office_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
    death_office_layout = QVBoxLayout(death_office_box)
    death_office_layout.setContentsMargins(0, 0, 0, 0)
    death_office_layout.setSpacing(6)

    def _skill_display(skill_id: str) -> str:
        skill = get_skill(skill_id)
        return skill.display_name if skill is not None else skill_id.replace("_", " ").title()

    def _skill_level(skill_id: str) -> int:
        skill = get_skill(skill_id)
        level_key = skill.level_key if skill is not None else f"{skill_id}_level"
        try:
            return int(player_data.get(level_key, 1))
        except (TypeError, ValueError):
            return 1

    def _claim_skill_tooltip(row: dict) -> str:
        options = tuple(str(skill_id) for skill_id in row.get("skill_options", ()) or ())
        minimum_level = int(row.get("minimum_level", 1) or 1)
        if not options:
            return ""
        if len(options) > 8:
            label = "Any listed skill"
        else:
            label = ", ".join(_skill_display(skill_id) for skill_id in options[:8])
        if minimum_level > 1:
            return f"Choose: {label}. Minimum level: {minimum_level}."
        return f"Choose: {label}."

    def _claim_metadata(row: dict) -> str:
        if str(row.get("claim_type", "item")) == "xp_lamp":
            amount = row.get("xp_amount", 0)
            amount_text = f"{int(amount):,}" if float(amount or 0).is_integer() else f"{float(amount or 0):,.1f}"
            tooltip = _claim_skill_tooltip(row)
            return f"{amount_text} XP lamp" + (f" · {tooltip}" if tooltip else "")
        if str(row.get("claim_type", "item")) == "item_bundle":
            items = tuple(row.get("items", ()) or ())
            preview = []
            for item in items[:3]:
                if isinstance(item, (tuple, list)) and len(item) >= 2:
                    preview.append(f"{item[0]} x{item[1]}")
            if len(items) > len(preview):
                preview.append(f"+{len(items) - len(preview)} more")
            item_count = len(items)
            suffix = f" - {', '.join(preview)}" if preview else ""
            return f"{item_count} item stack{'s' if item_count != 1 else ''}{suffix}"
        return "Ready to claim"

    def _claim_bundle_tooltip(row: dict) -> str:
        items = tuple(row.get("items", ()) or ())
        lines = []
        for item in items:
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                lines.append(f"{item[0]} x{item[1]}")
        return "\n".join(lines)

    def _claim_item_icon_path(row: dict) -> Optional[str]:
        item_name = str(row.get("item_name", row.get("display_name", "")))
        if str(row.get("claim_type", "item")) == "item_bundle":
            items = tuple(row.get("items", ()) or ())
            first = items[0] if items else ()
            if isinstance(first, (tuple, list)) and first and isinstance(first[0], str):
                item_name = first[0]
        definition = _item_def_for(item_name)
        asset_path = definition.asset_path if definition is not None else None
        return _bank_icon_path(item_name, asset_path)

    def _claim_requirement_text(row: dict) -> str:
        claim_id = str(row.get("claim_id", ""))
        claim = CLAIM_DATA.get(claim_id, {}) if isinstance(CLAIM_DATA, dict) else {}
        parts = []
        for reason in tuple(row.get("locked_reasons", ())):
            if str(reason) == "quest":
                quest_id = claim.get("required_quest") if isinstance(claim, dict) else None
                quest = QUEST_DATA.get(str(quest_id), {}) if quest_id else {}
                parts.append(str(quest.get("display_name") or "source quest"))
            else:
                parts.append(str(reason))
        return ", ".join(parts) if parts else "requirements"

    def _claim_locked_summary(locked_rows: list) -> tuple[str, str]:
        primary = next((row for row in locked_rows if row.get("claim_id") == "wicked_hood"), locked_rows[0])
        name = str(primary.get("display_name", primary.get("claim_id", "Reward")))
        requirements = _claim_requirement_text(primary)
        count = len(locked_rows)
        text = f"{count} locked reward{'s' if count != 1 else ''}. {name} requires: {requirements}."
        if count > 1:
            text += f" {count - 1} more hidden."
        detail_lines = [
            f"{row.get('display_name', row.get('claim_id', 'Reward'))}: {_claim_requirement_text(row)}"
            for row in locked_rows[:8]
        ]
        if count > len(detail_lines):
            detail_lines.append(f"...and {count - len(detail_lines)} more")
        return text, "\n".join(detail_lines)

    def _choose_claim_skill(row: dict) -> Optional[str]:
        options = tuple(str(skill_id) for skill_id in row.get("skill_options", ()) or ())
        minimum_level = int(row.get("minimum_level", 1) or 1)
        eligible = [skill_id for skill_id in options if _skill_level(skill_id) >= minimum_level]
        if not eligible:
            QMessageBox.warning(claims_box, "No eligible skill", f"This lamp requires level {minimum_level} in an allowed skill.")
            return None
        labels = [_skill_display(skill_id) for skill_id in eligible]
        choice, ok = QInputDialog.getItem(claims_box, "Claim XP lamp", "Skill:", labels, 0, False)
        if not ok:
            return None
        try:
            return eligible[labels.index(choice)]
        except ValueError:
            return None

    def _populate_claims() -> None:
        _clear_layout(claims_layout)
        rows = claim_rows_pure(player_data, CLAIM_DATA)
        unclaimed = [row for row in rows if not row.get("claimed")]
        actionable = [row for row in unclaimed if row.get("eligible")]
        locked = [row for row in unclaimed if not row.get("eligible")]
        if not rows:
            claims_box.setVisible(False)
            return
        claims_box.setVisible(True)
        header = QLabel("Bank Claims")
        header.setObjectName("bankClaimsHeader")
        header.setStyleSheet("font-weight: 600; color: palette(text);")
        claims_layout.addWidget(header)
        max_claim_height = header.sizeHint().height()

        if not actionable and not locked:
            empty = QLabel("All Bank Claims caught up.")
            empty.setObjectName("bankClaimsCaughtUp")
            empty.setStyleSheet(f"color: {dim_text_css(empty)};")
            claims_layout.addWidget(empty)
            claims_box.setMaximumHeight(max_claim_height + claims_layout.spacing() + empty.sizeHint().height() + 4)
            return

        rows_host = QWidget()
        rows_host.setObjectName("bankClaimsRows")
        rows_layout = QVBoxLayout(rows_host)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(4)
        rendered_rows = 0

        for row in actionable:
            claim_row = QWidget()
            claim_row.setObjectName("bankClaimRow")
            crl = QHBoxLayout(claim_row)
            crl.setContentsMargins(6, 4, 6, 4)
            crl.setSpacing(8)
            item_name = str(row.get("item_name", row.get("display_name", "")))
            claim_type = str(row.get("claim_type", "item"))
            icon_label = QLabel()
            icon_label.setObjectName("bankClaimIcon")
            icon_label.setFixedSize(28, 28)
            icon_label.setStyleSheet("background: rgba(255, 255, 255, 0.08); border: 1px solid palette(mid); border-radius: 4px;")
            icon_path = _claim_item_icon_path(row)
            if icon_path:
                icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
                icon_label.setStyleSheet("")
            if claim_type == "xp_lamp":
                title_text = str(row.get("display_name", item_name))
            elif claim_type == "item_bundle":
                title_text = str(row.get("display_name", item_name))
            else:
                title_text = f"{row.get('display_name', item_name)} x{row.get('quantity', 1)}"
            copy = QWidget()
            copy_layout = QVBoxLayout(copy)
            copy_layout.setContentsMargins(0, 0, 0, 0)
            copy_layout.setSpacing(1)
            label = QLabel(title_text)
            label.setObjectName("bankClaimTitle")
            label.setStyleSheet("color: palette(text); font-weight: 600;")
            if claim_type == "xp_lamp":
                label.setToolTip(_claim_skill_tooltip(row))
            metadata = QLabel(_claim_metadata(row))
            metadata.setObjectName("bankClaimMetadata")
            metadata.setStyleSheet(f"color: {dim_text_css(metadata)};")
            if claim_type == "xp_lamp":
                metadata.setToolTip(_claim_skill_tooltip(row))
            elif claim_type == "item_bundle":
                bundle_tooltip = _claim_bundle_tooltip(row)
                label.setToolTip(bundle_tooltip)
                metadata.setToolTip(bundle_tooltip)
            copy_layout.addWidget(label)
            copy_layout.addWidget(metadata)
            claim_btn = QPushButton("Claim")
            claim_btn.setObjectName("bankClaimAction")
            if claim_type == "xp_lamp":
                claim_btn.setText("Choose skill")
                claim_btn.setToolTip(_claim_skill_tooltip(row))

            def _do_claim(_checked: bool = False, claim_id=row.get("claim_id"), claim_row=row) -> None:
                if on_claim_reward is None or not isinstance(claim_id, str):
                    return
                selected_skill_id = None
                if str(claim_row.get("claim_type", "item")) == "xp_lamp":
                    selected_skill_id = _choose_claim_skill(claim_row)
                    if selected_skill_id is None:
                        return
                if on_claim_reward(claim_id, selected_skill_id):
                    _populate_claims()
                    _refresh_equipment_views()

            claim_btn.clicked.connect(_do_claim)
            crl.addWidget(icon_label)
            crl.addWidget(copy)
            crl.addStretch(1)
            crl.addWidget(claim_btn)
            rows_layout.addWidget(claim_row)
            rendered_rows += 1

        if rendered_rows:
            scroll = QScrollArea()
            scroll.setObjectName("bankClaimsScrollArea")
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea#bankClaimsScrollArea { border: none; }")
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setWidget(rows_host)
            row_height = max(rows_host.sizeHint().height() // rendered_rows, 42)
            scroll_height = (row_height * 3) + 10
            scroll.setMaximumHeight(scroll_height)
            claims_layout.addWidget(scroll)
            max_claim_height += claims_layout.spacing() + scroll_height
        else:
            rows_host.deleteLater()

        if locked:
            summary_text, summary_tooltip = _claim_locked_summary(locked)
            summary = QLabel(summary_text)
            summary.setObjectName("bankClaimsLockedSummary")
            summary.setWordWrap(True)
            summary.setStyleSheet(f"color: {dim_text_css(summary)};")
            if summary_tooltip:
                summary.setToolTip(summary_tooltip)
            claims_layout.addWidget(summary)
            max_claim_height += claims_layout.spacing() + summary.sizeHint().height()

        claims_box.setMaximumHeight(max_claim_height + 4)

    def _death_office_items_tooltip(items: tuple) -> str:
        if not items:
            return ""
        counts: dict[str, int] = {}
        for item_name in items:
            if isinstance(item_name, str):
                counts[item_name] = counts.get(item_name, 0) + 1
        return "\n".join(f"{item_name} x{amount}" for item_name, amount in counts.items())

    def _populate_death_office() -> None:
        _clear_layout(death_office_layout)
        summary = combat_death_office_summary_pure(player_data)
        items = tuple(summary.get("items", ()) or ())
        if not items:
            death_office_box.setVisible(False)
            return
        death_office_box.setVisible(True)
        header = QLabel("Death's Office")
        header.setObjectName("deathOfficeHeader")
        header.setStyleSheet("font-weight: 600; color: palette(text);")
        death_office_layout.addWidget(header)

        row = QWidget()
        row.setObjectName("deathOfficeRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(6, 4, 6, 4)
        row_layout.setSpacing(8)

        first_item = next((item for item in items if isinstance(item, str)), "")
        icon_label = QLabel()
        icon_label.setObjectName("deathOfficeIcon")
        icon_label.setFixedSize(28, 28)
        icon_label.setStyleSheet("background: rgba(255, 255, 255, 0.08); border: 1px solid palette(mid); border-radius: 4px;")
        if first_item:
            definition = _item_def_for(first_item)
            asset_path = definition.asset_path if definition is not None else None
            icon_path = _bank_icon_path(first_item, asset_path)
            if icon_path:
                icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
                icon_label.setStyleSheet("")

        copy = QWidget()
        copy_layout = QVBoxLayout(copy)
        copy_layout.setContentsMargins(0, 0, 0, 0)
        copy_layout.setSpacing(1)
        item_count = int(summary.get("item_count", len(items)) or len(items))
        title = QLabel(f"{item_count} reclaimed gear item{'s' if item_count != 1 else ''}")
        title.setObjectName("deathOfficeTitle")
        title.setStyleSheet("color: palette(text); font-weight: 600;")
        tooltip = _death_office_items_tooltip(items)
        if tooltip:
            title.setToolTip(tooltip)
        cost = int(summary.get("reclaim_cost", 0) or 0)
        coins = int(summary.get("coins", 0) or 0)
        metadata = QLabel(f"Cost: {cost:,} Coins · Bank: {coins:,} Coins")
        metadata.setObjectName("deathOfficeMetadata")
        metadata.setStyleSheet(f"color: {dim_text_css(metadata)};")
        if tooltip:
            metadata.setToolTip(tooltip)
        copy_layout.addWidget(title)
        copy_layout.addWidget(metadata)

        reclaim_btn = QPushButton("Reclaim")
        reclaim_btn.setObjectName("deathOfficeReclaimAction")
        reclaim_btn.setEnabled(bool(summary.get("can_reclaim")) and on_reclaim_death_office is not None)
        if not summary.get("can_reclaim"):
            reclaim_btn.setToolTip(f"Need {cost:,} Coins to reclaim this gear.")

        def _do_reclaim(_checked: bool = False) -> None:
            if on_reclaim_death_office is None:
                return
            if on_reclaim_death_office():
                _refresh_equipment_views()

        reclaim_btn.clicked.connect(_do_reclaim)
        row_layout.addWidget(icon_label)
        row_layout.addWidget(copy)
        row_layout.addStretch(1)
        row_layout.addWidget(reclaim_btn)
        death_office_layout.addWidget(row)
        death_office_box.setMaximumHeight(
            header.sizeHint().height() + death_office_layout.spacing() + row.sizeHint().height() + 4
        )

    def _build_bank_equip_menu(item_name: str) -> "QMenu":
        """Right-click menu for an inventory row.

        Exposed as a builder (rather than only an inline exec) so the offscreen
        tests can assert action state without spawning a native popup.
        """
        menu = QMenu(bank_list)
        if is_equippable_item(item_name):
            ok, reason = can_equip_item_pure(item_name, EQUIPMENT_ITEM_DATA, player_data)
            action = menu.addAction("Equip" if ok else f"Equip ({reason})")
            action.setEnabled(bool(ok) and on_equip_item is not None)
            if not ok and reason:
                action.setToolTip(reason)

            def _do_equip(_checked: bool = False) -> None:
                if on_equip_item is None:
                    return
                if on_equip_item(item_name):
                    _refresh_equipment_views()

            action.triggered.connect(_do_equip)
            menu.addSeparator()

        amount = int((player_data.get("inventory", {}) or {}).get(item_name, 0) or 0)

        try:
            from .constants import CONSUMABLE_DATA  # type: ignore
        except Exception:
            try:
                from constants import CONSUMABLE_DATA  # type: ignore
            except Exception:
                CONSUMABLE_DATA = {}
        if item_name in CONSUMABLE_DATA:
            verb = "Eat" if CONSUMABLE_DATA[item_name].get("kind") == "kebab_random" else "Drink"
            consume_action = menu.addAction(f"{verb} {item_name}")
            consume_action.setEnabled(amount > 0 and on_consume_item is not None)

            def _do_consume(_checked: bool = False) -> None:
                if on_consume_item is None:
                    return
                result = on_consume_item(item_name)
                if result:
                    _refresh_equipment_views()
                    message = str(result.get("message", ""))
                    if message:
                        QMessageBox.information(bank_list, item_name, message)

            consume_action.triggered.connect(_do_consume)
            menu.addSeparator()

        if carried_mode_state["advanced"] and on_add_to_carried_layout is not None:
            add_to_layout_action = menu.addAction("Add to carried layout")
            add_to_layout_action.triggered.connect(
                lambda _checked=False, name=item_name: (
                    on_add_to_carried_layout(name, 1),
                    _refresh_carried_layout_grid(),
                )
            )
            menu.addSeparator()

        discard_action = menu.addAction(f"Discard all ({amount})")
        discard_action.setEnabled(amount > 0 and on_discard_item is not None)

        def _do_discard(_checked: bool = False) -> None:
            if on_discard_item is None:
                return
            answer = QMessageBox.question(
                bank_list,
                "Discard all?",
                f"Discard all {amount} {item_name} from your bank?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes and on_discard_item(item_name):
                _refresh_equipment_views()

        discard_action.triggered.connect(_do_discard)
        return menu

    def _bank_context_menu(pos) -> None:
        item = bank_list.itemAt(pos)
        if item is None:
            return
        item_name = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(item_name, str):
            return
        menu = _build_bank_equip_menu(item_name)
        menu.exec(bank_list.viewport().mapToGlobal(pos))

    bank_list.customContextMenuRequested.connect(_bank_context_menu)
    _populate_death_office()
    bk_layout.addWidget(death_office_box)
    _populate_claims()
    bk_layout.addWidget(claims_box)
    _populate_bank_list()
    bk_layout.addWidget(bank_list, 1)

    # Gear sits in its own pinned panel below the scrollable, striped inventory
    # (the owner wanted it "outside the striped window"). The toolbelt is
    # auto-resolved — best owned tool wins — so we show the active
    # pickaxe/hatchet. Worn equipment now has its own dedicated Equipment tab,
    # so the Bank panel is toolbelt-only.
    gear_list = QListWidget()
    gear_list.setObjectName("gearList")
    gear_list.setIconSize(QSize(28, 28))
    gear_list.setAlternatingRowColors(False)
    gear_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
    gear_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    gear_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def _add_gear_row(text: str, item_name: str) -> None:
        li = QListWidgetItem(text)
        definition = _item_def_for(item_name)
        asset_path = definition.asset_path if definition is not None else None
        icon_path = _bank_icon_path(item_name, asset_path)
        if icon_path:
            li.setIcon(QIcon(icon_path))
        li.setFlags(Qt.ItemFlag.ItemIsEnabled)
        li.setData(Qt.ItemDataRole.UserRole, "__gear__")
        gear_list.addItem(li)

    gear = bank_gear_rows_pure(player_data, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA, MINING_BONUS_ITEM_DATA)
    gear_list.addItem(_make_header_item("Toolbelt", "__gear_header__"))
    if gear["toolbelt"]:
        for slot_label, display_name in gear["toolbelt"]:
            _add_gear_row(f"{slot_label}: {display_name}", display_name)
    else:
        empty_tb = QListWidgetItem("No tools yet.")
        empty_tb.setFlags(Qt.ItemFlag.NoItemFlags)
        empty_tb.setData(Qt.ItemDataRole.UserRole, "__gear_empty__")
        gear_list.addItem(empty_tb)

    # Hug contents so the panel is a fixed strip, never its own scroller.
    _gear_h = 2 * gear_list.frameWidth() + 6
    for _i in range(gear_list.count()):
        _row_h = gear_list.sizeHintForRow(_i)
        _gear_h += _row_h if _row_h > 0 else 30
    gear_list.setFixedHeight(_gear_h)
    bk_layout.addWidget(gear_list)
    tabs.addTab(bank_tab, "Bank")
    tabs.setTabToolTip(tabs.indexOf(bank_tab), "View all your items")

    # ---- Equipment tab (dedicated worn-slot list + summed stat totals) ----
    # All 11 OSRS worn slots always render (greyed placeholder when empty) so the
    # layout is stable and discoverable; filled slots show the item + its icon
    # and expose right-click Unequip. The totals panel sums the worn set via the
    # pure equipment_stat_totals_pure so a future combat system reads the exact
    # same numbers the player sees.
    equipment_tab = QWidget()
    eq_layout = QVBoxLayout(equipment_tab)
    eq_layout.setContentsMargins(12, 12, 12, 12)
    eq_layout.setSpacing(8)

    eq_caption = QLabel("Right-click a worn item to unequip. Right-click bank gear to equip.")
    eq_caption.setStyleSheet(f"color: {dim_text_css(eq_caption)};")
    eq_layout.addWidget(eq_caption)

    # The Equipment tab can grow tall (worn slots + totals + the 28-slot carried
    # editor on the left, the combat setup + loot controls on the right), so the
    # whole body scrolls. The worn-slot list is sized to its content (no inner
    # scrollbar) to avoid a scroller-inside-a-scroller.
    eq_scroll = QScrollArea()
    eq_scroll.setWidgetResizable(True)
    eq_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    eq_content = QWidget()
    eq_content_layout = QHBoxLayout(eq_content)
    eq_content_layout.setContentsMargins(0, 0, 0, 0)
    eq_content_layout.setSpacing(12)

    eq_left = QWidget()
    eq_left_layout = QVBoxLayout(eq_left)
    eq_left_layout.setContentsMargins(0, 0, 0, 0)
    eq_left_layout.setSpacing(8)

    equip_list = QListWidget()
    equip_list.setObjectName("equipmentList")
    equip_list.setIconSize(QSize(28, 28))
    equip_list.setAlternatingRowColors(True)
    equip_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    equip_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    eq_left_layout.addWidget(equip_list)

    totals_label = QLabel("")
    totals_label.setObjectName("equipmentTotals")
    totals_label.setWordWrap(True)
    totals_label.setStyleSheet("font-family: monospace; color: palette(text);")
    eq_left_layout.addWidget(totals_label)

    # Carried pack — worn and carried gear belong together, so the primary
    # carried-pack section (Auto|Custom switch + both views) lives here beside
    # the worn slots.
    carried_pack_header = QLabel("Carried pack")
    carried_pack_header.setStyleSheet("color: palette(text); font-weight: 600;")
    eq_left_layout.addWidget(carried_pack_header)
    eq_left_layout.addWidget(_build_carried_pack_section(primary=True))
    eq_left_layout.addStretch(1)

    combat_setup_panel = _build_combat_setup_panel()
    combat_setup_panel.setObjectName("equipmentCombatSetupPanel")
    eq_content_layout.addWidget(eq_left, 2)
    eq_content_layout.addWidget(combat_setup_panel, 1)
    eq_scroll.setWidget(eq_content)
    eq_layout.addWidget(eq_scroll, 1)

    def _populate_equipment() -> None:
        equip_list.clear()
        equipment = player_data.get("equipment", {}) or {}
        for slot in EQUIPMENT_SLOTS:
            slot_id = slot.id
            item_name = equipment.get(slot_id) if isinstance(equipment, dict) else None
            if isinstance(item_name, str) and item_name:
                li = QListWidgetItem(f"{slot.label}: {item_name}")
                definition = _item_def_for(item_name)
                asset_path = definition.asset_path if definition is not None else None
                icon_path = _bank_icon_path(item_name, asset_path) or equipment_slot_icon_path(slot_id)
                if icon_path:
                    li.setIcon(QIcon(icon_path))
                tooltip = equipment_full_tooltip(item_name)
                if item_name == BINDING_NECKLACE_ITEM:
                    tooltip += f"\nCharges remaining: {binding_necklace_charges_pure(player_data)}"
                li.setToolTip(tooltip)
                li.setData(Qt.ItemDataRole.UserRole, slot_id)
                li.setData(Qt.ItemDataRole.UserRole + 1, item_name)
            else:
                li = QListWidgetItem(f"{slot.label}: (empty)")
                slot_icon = equipment_slot_icon_path(slot_id)
                if slot_icon:
                    li.setIcon(QIcon(slot_icon))
                # Greyed, non-actionable placeholder row (still hit-testable so
                # the row stays visible; the unequip menu no-ops on empties).
                # dim_text_color (not palette(mid)) so it stays legible in dark mode.
                li.setForeground(dim_text_color(equip_list))
                li.setData(Qt.ItemDataRole.UserRole, slot_id)
                li.setData(Qt.ItemDataRole.UserRole + 1, None)
            equip_list.addItem(li)
        # Size the worn-slot list to its content so all slots stay visible and the
        # Equipment tab's own scroll area (not a nested list scrollbar) handles
        # overflow.
        _eq_h = 2 * equip_list.frameWidth() + 6
        for _i in range(equip_list.count()):
            _row_h = equip_list.sizeHintForRow(_i)
            _eq_h += _row_h if _row_h > 0 else 30
        equip_list.setFixedHeight(_eq_h)
        _populate_equipment_totals()

    def _populate_equipment_totals() -> None:
        equipment = player_data.get("equipment", {}) or {}
        totals = equipment_stat_totals_pure(equipment, EQUIPMENT_ITEM_DATA)
        lines = ["Equipment stats"]
        for group_label, fields in _EQUIPMENT_BONUS_GROUPS:
            cells = [
                f"{_EQUIPMENT_BONUS_LABELS[field]} {_format_bonus(_bonus_value(totals, field))}"
                for field in fields
            ]
            lines.append(f"{group_label}: " + ", ".join(cells))
        totals_label.setText("\n".join(lines))

    def _build_slot_unequip_menu(slot_id: str):
        """Right-click menu for a filled Equipment slot (None when empty)."""
        equipment = player_data.get("equipment", {}) or {}
        item_name = equipment.get(slot_id) if isinstance(equipment, dict) else None
        if not isinstance(item_name, str) or not item_name:
            return None
        menu = QMenu(equip_list)
        action = menu.addAction(f"Unequip {item_name}")
        action.setEnabled(on_unequip_slot is not None)

        def _do_unequip(_checked: bool = False) -> None:
            if on_unequip_slot is None:
                return
            if on_unequip_slot(slot_id):
                _refresh_equipment_views()

        action.triggered.connect(_do_unequip)
        return menu

    def _equipment_context_menu(pos) -> None:
        item = equip_list.itemAt(pos)
        if item is None:
            return
        slot_id = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(slot_id, str):
            return
        menu = _build_slot_unequip_menu(slot_id)
        if menu is not None:
            menu.exec(equip_list.viewport().mapToGlobal(pos))

    equip_list.customContextMenuRequested.connect(_equipment_context_menu)
    _equipment_refreshers.append(_populate_equipment)
    _populate_equipment()

    tabs.addTab(equipment_tab, "Equipment")
    tabs.setTabToolTip(tabs.indexOf(equipment_tab), "View and manage your worn equipment")

    # Test seams: expose the menu builders so offscreen tests can assert the
    # Equip/Unequip wiring (enabled state, lock reason, action effect) without a
    # native popup. Harmless in production.
    dialog._ankiscape_equip_menu_for = _build_bank_equip_menu  # type: ignore[attr-defined]
    dialog._ankiscape_unequip_menu_for = _build_slot_unequip_menu  # type: ignore[attr-defined]
    dialog._ankiscape_refresh_equipment = _refresh_equipment_views  # type: ignore[attr-defined]

    # Now add the Stats tab (after Bank) and set its icon/tooltip
    tabs.addTab(stats_tab, "Stats")
    if os.path.exists(ach_icon_path):
        tabs.setTabIcon(tabs.indexOf(stats_tab), QIcon(ach_icon_path))
    tabs.setTabToolTip(tabs.indexOf(stats_tab), "View your skill stats")

    # Achievements tab (inline, themed)
    ach_tab = QWidget()
    a_layout = QVBoxLayout(ach_tab)
    a_layout.setContentsMargins(12, 12, 12, 12)
    a_layout.setSpacing(8)
    a_tabs = QTabWidget()
    a_tabs.setDocumentMode(True)

    def _make_achievement_card(title: str, desc: str, completed: bool) -> QWidget:
        card = QWidget()
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(10)
        # Icon
        icon_label = QLabel()
        icon_path = os.path.join(current_dir, "icon", f"{title.lower().replace(' ', '_')}.png")
        pixmap = QPixmap(icon_path) if os.path.exists(icon_path) else QPixmap(os.path.join(current_dir, "icon", "achievement_icon.png"))
        icon_label.setPixmap(pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        card_layout.addWidget(icon_label)
        # Info
        info = QWidget()
        il = QVBoxLayout(info)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(2)
        name = QLabel(title)
        name.setStyleSheet("font-weight: 600;")
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        il.addWidget(name)
        il.addWidget(desc_label)
        card_layout.addWidget(info, 1)
        # Status
        status = QLabel("✓" if completed else "")
        status.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: 700;")
        card_layout.addWidget(status, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        # Themed card style (palette-aware)
        card.setStyleSheet(
            "border: 1px solid palette(mid); border-radius: 6px; background-color: palette(base);"
        )
        return card

    for difficulty in ACHIEVEMENT_DIFFICULTIES:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        rows = achievement_rows_for_difficulty(ACHIEVEMENTS, player_data, difficulty)
        done, total = achievement_difficulty_progress(ACHIEVEMENTS, player_data, difficulty)
        header = QLabel(f"{difficulty} • {done}/{total} completed")
        header.setStyleSheet("font-weight: 600; margin: 0 0 6px 0;")
        tab_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(8)
        for row in rows:
            card = _make_achievement_card(row.name, row.description, row.completed)
            cl.addWidget(card)
        cl.addStretch(1)
        scroll.setWidget(content)
        tab_layout.addWidget(scroll)
        a_tabs.addTab(tab, difficulty)

    a_layout.addWidget(a_tabs)

    completed_count, total_count, progress_percentage = achievement_progress(ACHIEVEMENTS, player_data)
    progress_row = QWidget()
    prl = QHBoxLayout(progress_row)
    prl.setContentsMargins(0, 0, 0, 0)
    prl.setSpacing(8)
    progress_label = QLabel(f"Completed: {completed_count}/{total_count} ({progress_percentage:.1f}%)")
    prl.addWidget(progress_label)
    progress_bar = QProgressBar()
    progress_bar.setValue(int(progress_percentage))
    progress_bar.setTextVisible(False)
    prl.addWidget(progress_bar, 1)
    a_layout.addWidget(progress_row)

    tabs.addTab(ach_tab, "Achievements")
    if os.path.exists(ach_icon_path):
        tabs.setTabIcon(tabs.indexOf(ach_tab), QIcon(ach_icon_path))
    tabs.setTabToolTip(tabs.indexOf(ach_tab), "Review your achievements")

    # Settings tab (controls)
    settings_tab = QWidget()
    set_layout = QVBoxLayout(settings_tab)
    set_layout.setContentsMargins(12, 12, 12, 12)
    set_layout.setSpacing(10)

    # Load current settings (safe defaults if config unavailable)
    floating_enabled = True
    floating_position = "hud-right"
    floating_xp_enabled = True
    popups_enabled = True
    review_hud_enabled = True
    try:
        if mw and getattr(mw, 'col', None):
            floating_enabled = bool(mw.col.get_config("ankiscape_floating_enabled", True))
            pos = mw.col.get_config("ankiscape_floating_position", "hud-right")
            floating_position = pos if pos in ("left", "right", "center", "hud-right") else "hud-right"
        floating_xp_enabled = get_config_bool("ankiscape_floating_xp_enabled", True)
        popups_enabled = get_config_bool("ankiscape_popups_enabled", True)
        review_hud_enabled = get_config_bool("ankiscape_review_hud_enabled", True)
    except Exception:
        pass

    # Settings are grouped into clear sections (Gameplay, Notifications, Floating
    # Widget, Developer). Controls are created first, then assembled, so the
    # section order is easy to read and reorder without touching wiring.
    try:
        from aqt.qt import QFrame  # type: ignore
    except Exception:
        QFrame = None  # type: ignore

    def _section_title(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: 600;")
        return lbl

    def _add_divider() -> None:
        if QFrame is not None:
            div = QFrame()
            div.setFrameShape(QFrame.Shape.HLine)
            div.setFrameShadow(QFrame.Shadow.Sunken)
            set_layout.addWidget(div)

    # ---- Gameplay: review action multiplier + experience HUD ----
    current_multiplier = 1
    try:
        if mw and getattr(mw, "col", None):
            raw_multiplier = mw.col.get_config(_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY, None)
            if raw_multiplier is None:
                raw_multiplier = mw.col.get_config(_LEGACY_XP_MULTIPLIER_CONFIG_KEY, 1)
            current_multiplier = sanitize_review_action_multiplier(raw_multiplier)
    except Exception:
        current_multiplier = 1

    xp_mult_row = QWidget()
    xmr = QHBoxLayout(xp_mult_row)
    xmr.setContentsMargins(0, 0, 0, 0)
    xmr.setSpacing(8)
    xmr.addWidget(QLabel("Actions per review:"))
    xp_mult_spin = QSpinBox()
    xp_mult_spin.setRange(1, 10)
    xp_mult_spin.setSingleStep(1)
    xp_mult_spin.setSuffix("x")
    xp_mult_spin.setValue(current_multiplier)
    xp_mult_spin.setMaximumWidth(120)
    xmr.addWidget(xp_mult_spin)
    xmr.addStretch(1)

    xp_mult_help = QLabel(
        "Each successful review runs this many game action ticks. XP rises because more actions run; "
        "items, rolls, and material use scale with it."
    )
    xp_mult_help.setWordWrap(True)
    xp_mult_help.setStyleSheet("color: palette(mid); font-size: 11px;")

    review_hud_cb = QCheckBox("Enable experience HUD")
    review_hud_cb.setChecked(review_hud_enabled)

    # ---- Notifications: floating XP + popups ----
    xp_cb = QCheckBox("Enable floating XP")
    xp_cb.setChecked(floating_xp_enabled)
    popups_cb = QCheckBox("Enable achievements and level up pop ups")
    popups_cb.setChecked(popups_enabled)

    # ---- Floating Widget: enable + position ----
    enabled_cb = QCheckBox("Enable widget")
    enabled_cb.setChecked(floating_enabled)
    pos_row = QWidget()
    prl = QHBoxLayout(pos_row)
    prl.setContentsMargins(0, 0, 0, 0)
    prl.setSpacing(12)
    prl.addWidget(QLabel("Widget Position:"))
    rb_group = QButtonGroup(pos_row)
    rb_right = QRadioButton("Bottom right")
    rb_left = QRadioButton("Bottom left")
    rb_center = QRadioButton("Under XP bar")
    rb_hud_right = QRadioButton("Right of bar")
    rb_group.addButton(rb_right)
    rb_group.addButton(rb_left)
    rb_group.addButton(rb_center)
    rb_group.addButton(rb_hud_right)
    rb_right.setChecked(floating_position == "right")
    rb_left.setChecked(floating_position == "left")
    rb_center.setChecked(floating_position == "center")
    rb_hud_right.setChecked(floating_position == "hud-right")
    prl.addWidget(rb_left)
    prl.addWidget(rb_center)
    prl.addWidget(rb_hud_right)
    prl.addWidget(rb_right)
    prl.addStretch(1)

    # ---- assemble sections in order ----
    set_layout.addWidget(_section_title("Gameplay"))
    set_layout.addWidget(xp_mult_row)
    set_layout.addWidget(xp_mult_help)
    set_layout.addWidget(review_hud_cb)
    _add_divider()
    set_layout.addWidget(_section_title("Notifications"))
    set_layout.addWidget(xp_cb)
    set_layout.addWidget(popups_cb)
    _add_divider()
    set_layout.addWidget(_section_title("Floating Widget"))
    set_layout.addWidget(enabled_cb)
    set_layout.addWidget(pos_row)
    _add_divider()

    # ---- behavior wiring ----
    def _sync_pos_enabled():
        rb_left.setEnabled(enabled_cb.isChecked())
        rb_right.setEnabled(enabled_cb.isChecked())
        rb_center.setEnabled(enabled_cb.isChecked())
        rb_hud_right.setEnabled(enabled_cb.isChecked())
    _sync_pos_enabled()
    enabled_cb.stateChanged.connect(lambda _=None: _sync_pos_enabled())

    if callable(on_set_floating_enabled):
        enabled_cb.stateChanged.connect(lambda _=None: on_set_floating_enabled(bool(enabled_cb.isChecked())))
    if callable(on_set_floating_position):
        rb_left.toggled.connect(lambda checked=False: checked and on_set_floating_position("left"))
        rb_right.toggled.connect(lambda checked=False: checked and on_set_floating_position("right"))
        rb_center.toggled.connect(lambda checked=False: checked and on_set_floating_position("center"))
        rb_hud_right.toggled.connect(lambda checked=False: checked and on_set_floating_position("hud-right"))

    def _apply_review_action_multiplier(value: int) -> None:
        # Clamp before persisting so the backend sees an integer action count.
        safe = sanitize_review_action_multiplier(value)
        try:
            if mw and getattr(mw, "col", None):
                mw.col.set_config(_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY, safe)
        except Exception:
            pass
    xp_mult_spin.valueChanged.connect(lambda v: _apply_review_action_multiplier(int(v)))

    def _persist_bool(key: str, val: bool):
        try:
            if mw and getattr(mw, 'col', None):
                mw.col.set_config(key, bool(val))
        except Exception:
            pass

    def _apply_xp_enabled(flag: bool):
        _persist_bool("ankiscape_floating_xp_enabled", flag)

    def _apply_popups_enabled(flag: bool):
        _persist_bool("ankiscape_popups_enabled", flag)

    def _apply_review_hud_enabled(flag: bool):
        _persist_bool("ankiscape_review_hud_enabled", flag)
        try:
            if not flag:
                if _REVIEW_HUD is not None and hasattr(_REVIEW_HUD, "hide"):
                    _REVIEW_HUD.hide()
            else:
                # If enabled, attempt to refresh HUD position/visibility
                if _REVIEW_HUD is not None and hasattr(_REVIEW_HUD, "show"):
                    _REVIEW_HUD.show()
        except Exception:
            pass

    xp_cb.stateChanged.connect(lambda _=None: _apply_xp_enabled(bool(xp_cb.isChecked())))
    popups_cb.stateChanged.connect(lambda _=None: _apply_popups_enabled(bool(popups_cb.isChecked())))
    review_hud_cb.stateChanged.connect(lambda _=None: _apply_review_hud_enabled(bool(review_hud_cb.isChecked())))

    # Developer Mode controls: master toggle, reveals debug/diagnostics
    dev_block = QWidget()
    dev_layout = QVBoxLayout(dev_block)
    dev_layout.setContentsMargins(0, 8, 0, 0)
    dev_layout.setSpacing(6)
    dev_title = QLabel("Developer Mode")
    dev_title.setStyleSheet("font-weight: 600;")
    dev_layout.addWidget(dev_title)
    dev_row = QWidget()
    drl = QHBoxLayout(dev_row)
    drl.setContentsMargins(0, 0, 0, 0)
    drl.setSpacing(8)
    dev_toggle = QCheckBox("Enable developer mode (turns on debug logs)")
    dev_enabled = False
    try:
        if mw and getattr(mw, 'col', None):
            dev_enabled = bool(mw.col.get_config("ankiscape_developer_mode", False))
            # Back-compat: migrate previous key if set
            if not dev_enabled and bool(mw.col.get_config("ankiscape_debug_enabled", False)):
                dev_enabled = True
                mw.col.set_config("ankiscape_developer_mode", True)
    except Exception:
        dev_enabled = False
    dev_toggle.setChecked(dev_enabled)
    drl.addWidget(dev_toggle)
    drl.addStretch(1)
    dev_layout.addWidget(dev_row)

    # Inner panel (shown only when developer mode enabled)
    dev_inner = QWidget()
    dev_inner_layout = QVBoxLayout(dev_inner)
    dev_inner_layout.setContentsMargins(12, 6, 0, 0)
    dev_inner_layout.setSpacing(6)
    # Row: Clear Logs + Run Tests
    tools_row = QWidget()
    trl = QHBoxLayout(tools_row)
    trl.setContentsMargins(0, 0, 0, 0)
    trl.setSpacing(8)
    clear_btn = QPushButton("Clear Logs")
    run_tests_btn = QPushButton("Run Unit Tests")
    trl.addWidget(clear_btn)
    trl.addWidget(run_tests_btn)
    trl.addStretch(1)
    dev_inner_layout.addWidget(tools_row)

    def _apply_dev_enabled(flag: bool):
        try:
            if mw and getattr(mw, 'col', None):
                mw.col.set_config("ankiscape_developer_mode", bool(flag))
        except Exception:
            pass
        # Tie developer mode to debug enablement
        try:
            try:
                from .debug import set_debug_enabled  # type: ignore
            except Exception:
                from debug import set_debug_enabled  # type: ignore
            set_debug_enabled(bool(flag))
        except Exception:
            pass
        # Show/Hide inner panel
        try:
            dev_inner.setVisible(bool(flag))
        except Exception:
            pass
        if flag:
            _debug_log("developer_mode: enabled via UI")
    dev_toggle.stateChanged.connect(lambda _=None: _apply_dev_enabled(bool(dev_toggle.isChecked())))

    def _clear_logs():
        try:
            # Remove base and rotated files
            base = os.path.join(os.path.dirname(__file__), "ankiscape_debug.log")
            paths = [base] + [f"{base}.{i}" for i in range(1, 6)]
            removed_any = False
            for p in paths:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                        removed_any = True
                except Exception:
                    pass
            # Feedback: lightweight message box
            try:
                msg = QMessageBox(mw)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Logs cleared")
                msg.setText("Debug logs have been cleared." if removed_any else "No log files found to clear.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
            except Exception:
                pass
        except Exception:
            pass
    clear_btn.clicked.connect(_clear_logs)

    def _run_tests_and_log():
        # Run tests in-process to avoid OS handlers opening files with Anki app.
        try:
            _debug_log("developer_mode: running unit tests via UI (in-process)")
            import sys, io, unittest, traceback
            root = os.path.dirname(os.path.abspath(__file__))
            if root not in sys.path:
                sys.path.insert(0, root)
            loader = unittest.TestLoader()
            suite = loader.discover(start_dir=os.path.join(root, "tests"), pattern="test_*.py")
            buf = io.StringIO()
            runner = unittest.TextTestRunner(stream=buf, verbosity=2)
            result = runner.run(suite)
            output = buf.getvalue()
            code = 0 if result.wasSuccessful() else 1
            for line in output.splitlines():
                _debug_log(f"tests: {line}")
            _debug_log(f"developer_mode: tests finished rc={code}, failures={len(result.failures)}, errors={len(result.errors)}")
            # User feedback
            msg = QMessageBox(mw)
            msg.setIcon(QMessageBox.Icon.Information if code == 0 else QMessageBox.Icon.Warning)
            msg.setWindowTitle("Unit Tests Result")
            msg.setText("All tests passed." if code == 0 else "Some tests failed. See debug log for details.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        except Exception:
            try:
                _debug_log("developer_mode: test run failed with exception")
                _debug_log(traceback.format_exc())
            except Exception:
                pass
    run_tests_btn.clicked.connect(_run_tests_and_log)

    dev_inner.setVisible(dev_enabled)
    dev_layout.addWidget(dev_inner)
    set_layout.addWidget(dev_block)

    tabs.addTab(settings_tab, "Settings")
    # Set Settings icon if present
    try:
        settings_icon = os.path.join(current_dir, "icon", "settings_icon.png")
        if os.path.exists(settings_icon):
            tabs.setTabIcon(tabs.indexOf(settings_tab), QIcon(settings_icon))
    except Exception:
        pass
    tabs.setTabToolTip(tabs.indexOf(settings_tab), "Configure widget, experience HUD, notifications, and developer tools")

    layout.addWidget(tabs)

    # Footer with a subtle review link
    footer = QWidget()
    f_layout = QHBoxLayout(footer)
    f_layout.setContentsMargins(0, 8, 0, 0)
    f_layout.setSpacing(8)
    hint = QLabel("Enjoying AnkiScape?")
    link = QLabel('<a href="https://ankiweb.net/shared/review/1808450369">Leave a review</a>')
    link.setOpenExternalLinks(True)
    link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    hint.setStyleSheet("color: #666;")
    link.setStyleSheet("color: #4CAF50;")
    f_layout.addWidget(hint)
    f_layout.addWidget(link)
    f_layout.addStretch(1)
    close = QPushButton("Close")
    close.clicked.connect(dialog.accept)
    f_layout.addWidget(close)
    layout.addWidget(footer)
    dialog.setLayout(layout)
    _debug_log("ui.show_main_menu: about to exec")
    dialog.exec()
    _debug_log("ui.show_main_menu: dialog closed")


def show_tree_selection_dialog(current_tree: str, woodcutting_level: int, TREE_DATA: dict, TREE_IMAGES: dict) -> Optional[str]:
    """Render a Tree Selection dialog and return the chosen tree name or None if cancelled."""
    dialog = QDialog(mw)
    dialog.setWindowTitle("Tree Selection")
    dialog.setMinimumWidth(400)
    layout = QVBoxLayout()

    title_label = QLabel("Select Tree to Cut")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 15px;")
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    grid_layout = QGridLayout()
    row, col = 0, 0
    button_group = QButtonGroup(dialog)

    for tree_name, tree_data in TREE_DATA.items():
        # tree_name is a stable target ID; show the friendly display name and
        # look up the legacy icon by that name (some IDs have no bundled image).
        display = str(tree_data.get("display_name", tree_name))
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)

        icon_path = TREE_IMAGES.get(display)
        if icon_path and os.path.exists(icon_path):
            tree_image = QLabel()
            pixmap = QPixmap(icon_path)
            tree_image.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
            tree_layout.addWidget(tree_image, alignment=Qt.AlignmentFlag.AlignCenter)

        tree_info = QLabel(f"{display}\nLevel: {tree_data['level']}")
        tree_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tree_layout.addWidget(tree_info)

        radio_button = QRadioButton()
        radio_button.setChecked(tree_name == current_tree)
        if not can_cut_tree_pure(woodcutting_level, tree_name, TREE_DATA):
            radio_button.setEnabled(False)
            tree_widget.setStyleSheet("color: gray;")
        button_group.addButton(radio_button)
        radio_button.tree_name = tree_name
        tree_layout.addWidget(radio_button, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout.addWidget(tree_widget, row, col)
        col += 1
        if col > 2:
            col = 0
            row += 1

    layout.addLayout(grid_layout)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    if dialog.exec():
        selected_button = button_group.checkedButton()
        if selected_button:
            return selected_button.tree_name
    return None


def show_ore_selection_dialog(current_ore: str, mining_level: int, ORE_DATA: dict, ORE_IMAGES: dict) -> Optional[str]:
    """Render an Ore Selection dialog and return the chosen ore name or None if cancelled."""
    dialog = QDialog(mw)
    dialog.setWindowTitle("Ore Selection")
    dialog.setMinimumWidth(400)
    layout = QVBoxLayout()

    title_label = QLabel("Select Ore to Mine")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 15px;")
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    grid_layout = QGridLayout()
    row, col = 0, 0
    button_group = QButtonGroup(dialog)

    for ore, data in ORE_DATA.items():
        display_name = data.get("display_name", ore)
        ore_widget = QWidget()
        ore_layout = QVBoxLayout(ore_widget)

        # output_item is None for variable-output rocks (Sandstone/Granite/Gem
        # rocks), so fall back to the display name instead of resolving None.
        icon_path = ORE_IMAGES.get(data.get("output_item") or display_name)
        if icon_path:
            ore_image = QLabel()
            pixmap = QPixmap(icon_path)
            ore_image.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
            ore_layout.addWidget(ore_image, alignment=Qt.AlignmentFlag.AlignCenter)

        ore_info = QLabel(f"{display_name}\nLevel: {data['level']}")
        ore_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ore_layout.addWidget(ore_info)

        radio_button = QRadioButton()
        radio_button.setChecked(ore == current_ore)
        if not can_mine_ore_pure(mining_level, ore, ORE_DATA):
            radio_button.setEnabled(False)
            ore_widget.setStyleSheet("color: gray;")
        button_group.addButton(radio_button)
        radio_button.ore_name = ore
        ore_layout.addWidget(radio_button, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout.addWidget(ore_widget, row, col)
        col += 1
        if col > 2:
            col = 0
            row += 1

    layout.addLayout(grid_layout)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    if dialog.exec():
        selected_button = button_group.checkedButton()
        if selected_button:
            return selected_button.ore_name
    return None


def show_bar_selection_dialog(current_bar: str, smithing_level: int, BAR_DATA: dict, BAR_IMAGES: dict) -> Optional[str]:
    dialog = QDialog(mw)
    dialog.setWindowTitle("Bar Selection")
    dialog.setMinimumWidth(400)
    layout = QVBoxLayout()

    title_label = QLabel("Select Bar to Smelt")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 15px;")
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    grid_layout = QGridLayout()
    row, col = 0, 0
    button_group = QButtonGroup(dialog)

    for bar_name, bar_data in BAR_DATA.items():
        bar_widget = QWidget()
        bar_layout = QVBoxLayout(bar_widget)

        bar_image = QLabel()
        pixmap = QPixmap(BAR_IMAGES[bar_name])
        bar_image.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        bar_layout.addWidget(bar_image, alignment=Qt.AlignmentFlag.AlignCenter)

        bar_info = QLabel(f"{bar_name}\nLevel: {bar_data['level']}")
        bar_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar_layout.addWidget(bar_info)

        radio_button = QRadioButton()
        radio_button.setChecked(bar_name == current_bar)
        if bar_data.get("level", 1) > smithing_level:
            radio_button.setEnabled(False)
            bar_widget.setStyleSheet("color: gray;")
        button_group.addButton(radio_button)
        radio_button.bar_name = bar_name
        bar_layout.addWidget(radio_button, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout.addWidget(bar_widget, row, col)
        col += 1
        if col > 2:
            col = 0
            row += 1

    layout.addLayout(grid_layout)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    if dialog.exec():
        selected_button = button_group.checkedButton()
        if selected_button:
            return selected_button.bar_name
    return None


def show_craft_selection_dialog(current_craft: str, crafting_level: int, inventory: dict, CRAFTING_DATA: dict, CRAFTED_ITEM_IMAGES: dict) -> Optional[str]:
    dialog = QDialog(mw)
    dialog.setWindowTitle("Craft Selection")
    dialog.setMinimumWidth(400)
    dialog.setMinimumHeight(500)

    layout = QVBoxLayout()
    title_label = QLabel("Select Item to Craft")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 15px;")
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setStyleSheet("border: none;")

    scroll_content = QWidget()
    grid_layout = QGridLayout(scroll_content)
    grid_layout.setSpacing(10)

    row, col = 0, 0
    button_group = QButtonGroup(dialog)

    for item, data in CRAFTING_DATA.items():
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)

        item_image = QLabel()
        pixmap = QPixmap(CRAFTED_ITEM_IMAGES.get(item, ""))
        item_image.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        item_layout.addWidget(item_image, alignment=Qt.AlignmentFlag.AlignCenter)

        item_info = QLabel(f"{item}\nLevel: {data['level']}")
        item_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(item_info)

        radio_button = QRadioButton()
        radio_button.setChecked(item == current_craft)
        if not can_craft_item_pure(crafting_level, inventory, item, CRAFTING_DATA):
            radio_button.setEnabled(False)
            item_widget.setStyleSheet("color: gray;")

        button_group.addButton(radio_button)
        radio_button.item_name = item
        item_layout.addWidget(radio_button, alignment=Qt.AlignmentFlag.AlignCenter)

        grid_layout.addWidget(item_widget, row, col)
        col += 1
        if col > 2:
            col = 0
            row += 1

    scroll_area.setWidget(scroll_content)
    layout.addWidget(scroll_area)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    if dialog.exec():
        selected_button = button_group.checkedButton()
        if selected_button:
            return selected_button.item_name
    return None


def show_skill_selection_dialog(current_skill: str, can_smelt_any_bar: bool) -> Optional[str]:
    """Skill selection dialog that returns the chosen skill or None if cancelled.
    Disables Smithing when no bars can be smelted (per provided boolean).
    """
    dialog = QDialog(mw)
    dialog.setWindowTitle("Skill Selection")
    layout = QVBoxLayout()

    skill_combo = QComboBox()
    skills = ["None", "Mining", "Woodcutting", "Smithing", "Crafting"]
    skill_combo.addItems(skills)
    skill_combo.setCurrentText(current_skill)
    layout.addWidget(skill_combo)

    warning_label = QLabel("")
    warning_label.setStyleSheet("color: red;")
    layout.addWidget(warning_label)

    def update_warning():
        if skill_combo.currentText() == "Smithing" and not can_smelt_any_bar:
            warning_label.setText("You don't have enough ores to smelt any bars. Mine some ores first!")
            save_button.setEnabled(False)
        else:
            warning_label.setText("")
            save_button.setEnabled(True)

    skill_combo.currentTextChanged.connect(lambda _: update_warning())

    button_layout = QHBoxLayout()
    cancel_button = QPushButton("Cancel")
    save_button = QPushButton("Save")

    cancel_button.clicked.connect(dialog.reject)
    save_button.clicked.connect(dialog.accept)

    button_layout.addWidget(cancel_button)
    button_layout.addWidget(save_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    update_warning()

    if dialog.exec():
        return skill_combo.currentText()
    return None


def show_review_popup():
    # Deprecated: replaced by footer link in the main menu.
    return


def show_stats(player_data: dict, current_skill: str):
    """Render the Stats dialog using provided player_data and current_skill."""
    try:
        dialog = QDialog(mw)
        dialog.setWindowTitle("AnkiScape Stats")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(700)

        dialog.setStyleSheet(
            """
            QDialog { background-color: @CANVAS; }
            QLabel { color: @TEXT; }
            QTabWidget::pane { border: 1px solid @BORDER; background-color: @CANVAS; border-radius: 5px; }
            QTabBar::tab { background-color: @BUTTON; color: @TEXT; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background-color: @CANVAS; border-bottom: 2px solid @ACCENT; }
            QTabBar::tab:hover { background-color: @HOVER; }
            """
        )

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        status_label = QLabel(f"Current Skill: {current_skill}")
        status_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: @ACCENT;
            padding: 10px;
            background-color: @CANVAS;
            border-radius: 5px;
            """
        )
        main_layout.addWidget(status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        tabs = QTabWidget()

        def create_label(text, is_header=False):
            label = QLabel(text)
            if is_header:
                label.setStyleSheet(
                    """
                    font-size: 16px;
                    font-weight: bold;
                    color: @ACCENT;
                    margin-top: 15px;
                    margin-bottom: 10px;
                    """
                )
            else:
                label.setStyleSheet("font-size: 14px;")
            return label

        def create_skill_tab(skill_name):
            tab = QWidget()
            tab_layout = QVBoxLayout()
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("border: none;")
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(10)
            scroll_layout.setContentsMargins(20, 20, 20, 20)

            scroll_layout.addWidget(create_label(f"{skill_name} Stats", True))
            stats_layout = QGridLayout()
            stats_layout.setColumnStretch(1, 1)
            stats_layout.setHorizontalSpacing(15)
            stats_layout.setVerticalSpacing(10)

            level = player_data.get(f"{skill_name.lower()}_level", 1)
            exp = round(player_data.get(f"{skill_name.lower()}_exp", 0), 1)

            stats_layout.addWidget(create_label(f"{skill_name} Level:"), 0, 0)
            stats_layout.addWidget(create_label(str(level), True), 0, 1)
            stats_layout.addWidget(create_label("Total Experience:"), 1, 0)
            stats_layout.addWidget(create_label(f"{exp:,}", True), 1, 1)

            if level < 99:
                exp_to_next = round(max(0, EXP_TABLE[level] - exp), 1)
                stats_layout.addWidget(create_label("Experience to Next Level:"), 2, 0)
                stats_layout.addWidget(create_label(f"{exp_to_next:,}", True), 2, 1)

            progress_bar = QProgressBar()
            progress_percentage = (exp - EXP_TABLE[level - 1]) / (EXP_TABLE[level] - EXP_TABLE[level - 1]) * 100
            progress_bar.setValue(int(progress_percentage))
            progress_bar.setFormat("")
            progress_bar.setStyleSheet(
                """
                QProgressBar {
                    border: 1px solid @BORDER;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: @ACCENT;
                    border-radius: 5px;
                }
                """
            )
            stats_layout.addWidget(create_label("Level Progress:"), 3, 0)
            stats_layout.addWidget(progress_bar, 3, 1)

            scroll_layout.addLayout(stats_layout)

            scroll_layout.addWidget(create_label(f"{skill_name} Inventory", True))
            inventory_layout = QGridLayout()
            inventory_layout.setColumnStretch(1, 1)
            inventory_layout.setHorizontalSpacing(15)
            inventory_layout.setVerticalSpacing(10)

            row = 0
            for item, amount in player_data.get("inventory", {}).items():
                if (
                    (skill_name == "Mining" and (item in MINING_OUTPUT_ITEMS or item in GEM_DATA))
                    # Woodcutting stores real log items (Logs, Oak logs, Bark), not
                    # the stable tree IDs that now key TREE_DATA.
                    or (skill_name == "Woodcutting" and item in WOODCUTTING_LOG_ITEMS)
                    or (skill_name == "Smithing" and item in BAR_DATA)
                    or (skill_name == "Crafting" and item in CRAFTING_DATA)
                    or (skill_name == "Fletching" and (_item_def_for(item) is not None and _item_def_for(item).category == "fletched"))
                    or (skill_name == "Firemaking" and (item in FIREMAKING_LOG_ITEMS or item in FIREMAKING_ITEM_IMAGES))
                    or (skill_name == "Fishing" and item in FISHING_OUTPUT_ITEMS)
                ):
                    item_image = QLabel()
                    _item_def = _item_def_for(item)
                    pixmap = QPixmap(
                        ORE_IMAGES.get(item)
                        or BAR_IMAGES.get(item)
                        or GEM_IMAGES.get(item)
                        or CRAFTED_ITEM_IMAGES.get(item)
                        or FLETCHED_ITEM_IMAGES.get(item)
                        or FIREMAKING_ITEM_IMAGES.get(item)
                        or FISHING_ITEM_IMAGES.get(item)
                        or (_item_def.asset_path if _item_def and _item_def.asset_path else "")
                    )
                    item_image.setPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
                    inventory_layout.addWidget(item_image, row, 0)

                    inventory_layout.addWidget(create_label(item), row, 1)
                    inventory_layout.addWidget(create_label(str(amount), True), row, 2)
                    row += 1

            scroll_layout.addLayout(inventory_layout)

            scroll_content.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_content)
            tab_layout.addWidget(scroll_area)
            tab.setLayout(tab_layout)
            return tab

        for skill_name in playable_review_skill_names():
            tabs.addTab(create_skill_tab(skill_name), skill_name)

        main_layout.addWidget(tabs)
        dialog.setLayout(main_layout)
        dialog.exec()

    except Exception as e:
        print(f"Error in show_stats: {str(e)}")
        import traceback
        traceback.print_exc()


def show_achievements(player_data: dict):
    """Render the Achievements dialog based on provided player_data."""
    dialog = QDialog(mw)
    dialog.setWindowTitle("Achievements")
    dialog.setMinimumWidth(700)
    dialog.setMinimumHeight(500)

    dialog.setStyleSheet(
        """
        QDialog {
            background-color: #f5f5f5;
        }
        """
    )

    layout = QVBoxLayout()

    title_label = QLabel("Achievements")
    title_label.setStyleSheet(
        """
        font-size: 28px;
        font-weight: bold;
        color: #333333;
        margin-bottom: 20px;
        """
    )
    layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    tabs = QTabWidget()
    tabs.setStyleSheet(
        """
        QTabWidget::pane {
            border: none;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #333333;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #4CAF50;
        }
        QTabBar::tab:hover {
            background-color: #d0d0d0;
        }
        """
    )

    for difficulty in ACHIEVEMENT_DIFFICULTIES:
        tab = QWidget()
        tab_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        for row in achievement_rows_for_difficulty(ACHIEVEMENTS, player_data, difficulty):
            achievement_widget = QWidget()
            achievement_layout = QHBoxLayout()

            icon_label = QLabel()
            icon_path = os.path.join(current_dir, "icon", f"{row.name.lower().replace(' ', '_')}.png")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
            else:
                pixmap = QPixmap(os.path.join(current_dir, "icon", "achievement_icon.png"))
            icon_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio))
            achievement_layout.addWidget(icon_label)

            info_widget = QWidget()
            info_layout = QVBoxLayout()
            name_label = QLabel(row.name)
            name_label.setStyleSheet("font-weight: bold; color: #333333; font-size: 16px;")
            desc_label = QLabel(row.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666666; font-size: 14px;")
            info_layout.addWidget(name_label)
            info_layout.addWidget(desc_label)
            info_widget.setLayout(info_layout)
            achievement_layout.addWidget(info_widget, stretch=1)

            status_label = QLabel("✓" if row.completed else "")
            status_label.setStyleSheet("color: #4CAF50; font-size: 24px; font-weight: bold;")
            achievement_layout.addWidget(status_label)

            achievement_widget.setLayout(achievement_layout)
            achievement_widget.setStyleSheet(
                f"""
                background-color: {'#e8f5e9' if row.completed else 'white'};
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
                """
            )

            scroll_layout.addWidget(achievement_widget)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        tab_layout.addWidget(scroll_area)
        tab.setLayout(tab_layout)
        tabs.addTab(tab, difficulty)

    layout.addWidget(tabs)

    completed_count, total_count, progress_percentage = achievement_progress(ACHIEVEMENTS, player_data)
    progress_label = QLabel(f"Completed: {completed_count}/{total_count} ({progress_percentage:.1f}%)")
    progress_label.setStyleSheet(
        """
        font-size: 18px;
        margin-top: 20px;
        color: #333333;
        """
    )
    layout.addWidget(progress_label, alignment=Qt.AlignmentFlag.AlignCenter)

    progress_bar = QProgressBar()
    progress_bar.setValue(int(progress_percentage))
    progress_bar.setTextVisible(False)
    progress_bar.setStyleSheet(
        """
        QProgressBar {
            border: none;
            background-color: #e0e0e0;
            border-radius: 4px;
            height: 8px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 4px;
        }
        """
    )
    layout.addWidget(progress_bar)

    dialog.setLayout(layout)
    dialog.exec()
