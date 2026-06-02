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
        QMenu,
        QGridLayout,
        QHBoxLayout,
        QButtonGroup,
        QRadioButton,
        QScrollArea,
        QProgressBar,
        QCheckBox,
        QSpinBox,
        QDesktopServices,
        QUrl,
    QEvent,
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
        FLETCHING_DATA,
        UTILITY_ACTIVITY_DATA,
        DEFAULT_UTILITY_ACTIVITY,
        ORE_IMAGES,
        TREE_IMAGES,
        BAR_IMAGES,
        GEM_IMAGES,
        CRAFTED_ITEM_IMAGES,
        FLETCHED_ITEM_IMAGES,
        UTILITY_ITEM_IMAGES,
        ACHIEVEMENTS,
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
        FLETCHING_DATA,
        UTILITY_ACTIVITY_DATA,
        DEFAULT_UTILITY_ACTIVITY,
        ORE_IMAGES,
        TREE_IMAGES,
        BAR_IMAGES,
        GEM_IMAGES,
        CRAFTED_ITEM_IMAGES,
        FLETCHED_ITEM_IMAGES,
        UTILITY_ITEM_IMAGES,
        ACHIEVEMENTS,
        current_dir,
    )
try:
    from .logic_pure import can_cut_tree_pure, can_mine_ore_pure, can_craft_item_pure, can_smelt_any_bar_pure, can_smith_item_pure, can_fletch_item_pure, can_perform_utility_activity_pure, can_chop_woodcutting_target_pure, best_woodcutting_axe_pure, can_mine_target_pure, best_mining_pickaxe_pure, can_open_bird_nests_pure, sanitize_review_action_multiplier, bank_gear_rows_pure
except Exception:
    from logic_pure import can_cut_tree_pure, can_mine_ore_pure, can_craft_item_pure, can_smelt_any_bar_pure, can_smith_item_pure, can_fletch_item_pure, can_perform_utility_activity_pure, can_chop_woodcutting_target_pure, best_woodcutting_axe_pure, can_mine_target_pure, best_mining_pickaxe_pure, can_open_bird_nests_pure, sanitize_review_action_multiplier, bank_gear_rows_pure  # type: ignore

try:
    from .skill_hub import CategoryView, SkillCardView, build_skill_hub, first_category_id
except Exception:
    from skill_hub import CategoryView, SkillCardView, build_skill_hub, first_category_id  # type: ignore

try:
    from .skill_registry import implemented_skill_definitions, implemented_review_skill_names, get_skill
except Exception:
    from skill_registry import implemented_skill_definitions, implemented_review_skill_names, get_skill  # type: ignore

try:
    from .constants import ITEM_DEFINITIONS
    from .item_registry import ItemDefinition, item_definitions_by_storage_key
except Exception:
    from constants import ITEM_DEFINITIONS  # type: ignore
    from item_registry import ItemDefinition, item_definitions_by_storage_key  # type: ignore

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
_MAIN_MENU_CTX = {"dialog": None, "smith_btn": None, "craft_btn": None, "fletch_btn": None, "warn_label": None}


# ---- registry-driven UI helpers -------------------------------------------
# These keep Stats/Bank/HUD in sync with the skill + item registries so a new
# playable skill (e.g. Fletching) surfaces everywhere without another hardcoded
# four-skill branch. Icons follow the existing convention: icon/<skill_id>_icon.png.

# Bank grouping order + labels. Categories come from item_registry.ItemCategory.
_ITEM_CATEGORY_ORDER = ("ore", "log", "gem", "bar", "crafted", "fletched", "material")
_ITEM_CATEGORY_LABELS = {
    "ore": "Ores",
    "log": "Logs",
    "gem": "Gems",
    "bar": "Bars",
    "crafted": "Crafted",
    "fletched": "Fletched",
    "material": "Materials",
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


# Utility / Activities is intentionally NOT a registry skill: it has no XP, level,
# or exp key. The backend routes it through these display names + `current_utility`,
# so the hub surfaces it as a synthetic, visually-distinct entry.
_UTILITY_HUB_NAME = "Utility / Activities"
_UTILITY_SKILL_NAMES = {"Utility", _UTILITY_HUB_NAME}
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

def refresh_skill_availability(can_smelt_any_bar: bool, can_craft_any_item: bool, can_fletch_any_item: bool = False):
    """Auto-enable processing-skill buttons when they become available while the menu is open.
    Never auto-selects the skill; users must choose it explicitly. Only enables; does not disable.

    ``can_fletch_any_item`` defaults to False so existing two-argument callers
    (the runtime review hook) keep working until they also pass Fletching.
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
        # Clear warning text if any became available
        if (
            (s_btn is not None and s_btn.isEnabled())
            or (c_btn is not None and c_btn.isEnabled())
            or (f_btn is not None and f_btn.isEnabled())
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


# UI Classes
if HAS_QT:
    # Shared HUD theme
    _HUD_ACCENT = "#4CAF50"  # Material green
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
                self.sub_lbl.setText(f"{activity_name} • material prep (no XP)")
                try:
                    self.progress.setVisible(False)
                    self.sub_lbl.setVisible(True)
                except Exception:
                    pass
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
                self.sub_lbl.setText("Open AnkiScape menu to choose a skill")
                # Always show progress/subtext when HUD is enabled
                try:
                    self.progress.setVisible(True)
                    self.sub_lbl.setVisible(True)
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
            self.sub_lbl.setText(f"{pct}% to Lv {target_lv} • {remain:,.0f} XP to next")

            # Always show progress/subtext when HUD is enabled
            try:
                self.progress.setVisible(True)
                self.sub_lbl.setVisible(True)
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
    on_set_utility=None,
    on_set_floating_enabled=None,
    on_set_floating_position=None,
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
        " QPushButton:disabled { color: palette(mid); border-color: palette(mid);"
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

    _active_choices = set(playable_review_skill_names()) | _UTILITY_SKILL_NAMES

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
            level = player_data.get("fletching_level", 1)
            inv = player_data.get("inventory", {})
            return any(can_fletch_item_pure(level, inv, n, FLETCHING_DATA) for n in FLETCHING_DATA)
        except Exception:
            return False

    def _skill_available(display_name: str) -> bool:
        if display_name == "Smithing":
            return bool(can_smelt_any_bar)
        if display_name == "Crafting":
            return _craft_available()
        if display_name == "Fletching":
            return _fletch_available()
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
    def _build_ore_list() -> QListWidget:
        # ORE_DATA is keyed by stable target IDs ("rune_essence", "coal", ...).
        # Mirrors _build_tree_list: the row text shows the friendly display name +
        # level, the chosen ID is stored on the item and persisted via on_set_ore,
        # and lock reasons distinguish level from a missing usable pickaxe. Lock
        # state and best-pickaxe come straight from the backend pure helpers
        # (can_mine_target_pure / best_mining_pickaxe_pure) so source rules aren't
        # re-derived in Qt. Variable-output rocks (Sandstone, Granite, Gem rocks)
        # and the essence -> Pure essence upgrade are labelled inline + in tooltips.
        ore_list = QListWidget()
        ore_list.setIconSize(QSize(28, 28))
        ore_list.setAlternatingRowColors(True)
        lvl_have = player_data.get("mining_level", 1)
        inv = player_data.get("inventory", {})
        toolbelt = player_data.get("toolbelt", {})
        best_pick = best_mining_pickaxe_pure(lvl_have, inv, toolbelt, MINING_PICKAXE_DATA)
        best_pick_name = best_pick.get("display_name", "a pickaxe") if best_pick else None
        for target_id, data in ORE_DATA.items():
            display_name = str(data.get("display_name", target_id))
            lvl_req = data.get("level", 1)
            output_item = data.get("output_item")
            weighted = data.get("weighted_outputs", ()) or ()
            alt_item = data.get("alternate_output_item")
            alt_level = data.get("alternate_output_level")

            label = f"{display_name} (Lvl {lvl_req})"
            if weighted:
                label += " — variable output"
            elif isinstance(alt_item, str) and isinstance(alt_level, int):
                label += f" — {alt_item} at Lvl {alt_level}+"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, target_id)

            # Icons are keyed by real item names; weighted rocks have no single
            # output_item so use the first weighted item as the representative
            # icon (e.g. Gem rocks -> Uncut opal). Gem outputs live in GEM_IMAGES,
            # ores in ORE_IMAGES, so consult both.
            icon_key = output_item or display_name
            if not output_item and weighted:
                first = weighted[0]
                icon_key = first.get("item", display_name) if isinstance(first, dict) else display_name
            icon_path = ORE_IMAGES.get(icon_key) or GEM_IMAGES.get(icon_key)
            if icon_path and os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))

            if weighted:
                names = ", ".join(
                    str(w.get("item")) for w in weighted if isinstance(w, dict) and w.get("item")
                )
                output_line = f"Output: variable — {names}"
            elif isinstance(alt_item, str) and isinstance(alt_level, int):
                output_line = (
                    f"Output: {output_item} x1 "
                    f"(becomes {alt_item} at Mining level {alt_level}+)"
                )
            elif output_item:
                output_line = f"Output: {output_item} x1"
            else:
                output_line = "Output: none"

            tooltip = (
                f"Requires Mining level {lvl_req}. You have {lvl_have}.\n"
                f"{output_line}\n"
                f"Base XP: {data.get('exp', 0)} per ore\n"
                f"Best usable pickaxe: {best_pick_name or 'none — get a pickaxe'}"
            )
            # Player-facing notes/anomalies (essence upgrade, equal-weight
            # simplifications, OSRS gem-rate cross-check) come from backend data.
            # The dev-facing `source` audit path is intentionally not shown.
            note = data.get("notes")
            if note:
                tooltip += f"\nNote: {note}"
            deferred_note = _MINING_DEFERRED_VARIANT_NOTES.get(target_id)
            if deferred_note:
                tooltip += f"\nNote: {deferred_note}"

            if not can_mine_target_pure(lvl_have, target_id, ORE_DATA, inv, toolbelt, MINING_PICKAXE_DATA):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                reason = []
                if lvl_have < lvl_req:
                    reason.append(f"level {lvl_req}")
                if best_pick is None:
                    reason.append("no usable pickaxe")
                if reason:
                    tooltip += "\nLocked due to: " + ", ".join(reason)
            item.setToolTip(tooltip)
            ore_list.addItem(item)
            if target_id == player_data.get("current_ore", DEFAULT_MINING_TARGET):
                ore_list.setCurrentItem(item)

        def _on_ore_selected(item: QListWidgetItem):
            if item:
                on_set_ore(item.data(Qt.ItemDataRole.UserRole))
        ore_list.itemClicked.connect(_on_ore_selected)
        ore_list.itemActivated.connect(_on_ore_selected)
        return ore_list

    def _build_tree_list() -> QListWidget:
        # TREE_DATA is keyed by stable target IDs ("tree", "oak", ...). The row
        # text shows the friendly display name + level; the chosen ID is stored on
        # the item and persisted via on_set_tree. Locks distinguish level from a
        # missing usable hatchet, and Ivy is flagged as XP-only (no log output).
        tree_list = QListWidget()
        tree_list.setIconSize(QSize(28, 28))
        tree_list.setAlternatingRowColors(True)
        lvl_have = player_data.get("woodcutting_level", 1)
        inv = player_data.get("inventory", {})
        toolbelt = player_data.get("toolbelt", {})
        best_axe = best_woodcutting_axe_pure(lvl_have, inv, toolbelt, WOODCUTTING_AXE_DATA)
        best_axe_name = best_axe.get("display_name", "a hatchet") if best_axe else None
        for target_id, data in TREE_DATA.items():
            display = str(data.get("display_name", target_id))
            output_item = data.get("output_item")
            lvl_req = data.get("level", 1)
            xp_only = output_item is None
            label = f"{display} (Lvl {lvl_req})"
            if xp_only:
                label += " — XP only"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, target_id)
            # TREE_IMAGES is keyed by the legacy display-name filename ("Oak").
            t_icon = TREE_IMAGES.get(display)
            if t_icon and os.path.exists(t_icon):
                item.setIcon(QIcon(t_icon))
            output_line = "XP only — produces no logs." if xp_only else f"Output: {output_item} x1"
            tooltip = (
                f"Requires Woodcutting level {lvl_req}. You have {lvl_have}.\n"
                f"{output_line}\n"
                f"Base XP: {data.get('exp', 0)} per chop\n"
                f"Best usable hatchet: {best_axe_name or 'none — get a hatchet'}"
            )
            # The dev-facing `source` audit path is intentionally not shown.
            if not can_chop_woodcutting_target_pure(lvl_have, target_id, TREE_DATA, inv, toolbelt, WOODCUTTING_AXE_DATA):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                reason = []
                if lvl_have < lvl_req:
                    reason.append(f"level {lvl_req}")
                if best_axe is None:
                    reason.append("no usable hatchet")
                if reason:
                    tooltip += "\nLocked due to: " + ", ".join(reason)
            item.setToolTip(tooltip)
            tree_list.addItem(item)
            if target_id == player_data.get("current_tree", DEFAULT_WOODCUTTING_TARGET):
                tree_list.setCurrentItem(item)

        def _on_tree_selected(item: QListWidgetItem):
            if item:
                on_set_tree(item.data(Qt.ItemDataRole.UserRole))
        tree_list.itemClicked.connect(_on_tree_selected)
        tree_list.itemActivated.connect(_on_tree_selected)
        return tree_list

    def _smith_tier_of(spec: dict) -> str:
        # Metal-type label that unifies a smelt bar with the forge items made from
        # it: smelt rows use their bar output, forge rows use their (single) bar
        # requirement. "Bronze bar" / "Rune bar" -> "Bronze" / "Rune".
        if spec.get("station") == "furnace":
            return str(spec.get("output_item", "")).replace(" bar", "").strip() or "Other"
        reqs = spec.get("requirements", {}) or {}
        return str(next(iter(reqs), "")).replace(" bar", "").strip() or "Other"

    def _build_smith_list() -> QTreeWidget:
        # SMITHING_DATA is one unified table keyed by stable recipe IDs
        # ("smelt_bronze_bar", "forge_rune_platebody", ...). With ~166 recipes a
        # flat list is a wall of rows, so this is a QTreeWidget grouped by metal
        # type (Bronze, Iron, ... Rune): each tier is a collapsible parent holding
        # its smelt bar first, then the forge items made from it. Groups are
        # collapsed by default and the expand/collapse state is persisted per tier
        # (smith_expanded_tiers / set_smith_tier_expanded); the group holding the
        # current target is always expanded so the selection stays visible.
        #
        # The chosen recipe ID lives on the child item and is persisted via
        # on_set_smith; the legacy on_set_bar (bar-name setter) is a smelt-only
        # fallback. Lock reasons come straight from can_smith_item_pure: level or
        # missing inputs only (no hammer/tool gate — the toolbelt is gathering-only).
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
            " QTreeWidget::item:disabled { color: palette(mid); }"
        )
        lvl_have = player_data.get("smithing_level", 1)
        inv = player_data.get("inventory", {})
        current = player_data.get("current_smith", DEFAULT_SMITHING_TARGET)
        cur_spec = SMITHING_DATA.get(current)
        cur_tier = _smith_tier_of(cur_spec) if cur_spec else None
        expanded = smith_expanded_tiers()

        def _icon_for(output_item: str):
            # Bars resolve via the registry (built with BAR_IMAGES); forged items
            # resolve via SMITHING_EXTRA_ITEM_IMAGES. A missing asset leaves the
            # row text-only.
            definition = _ITEM_DEFS_BY_KEY.get(output_item)
            return (definition.asset_path if definition and definition.asset_path else None) or BAR_IMAGES.get(output_item)

        def _make_child(recipe_id: str, spec: dict) -> "QTreeWidgetItem":
            display_name = str(spec.get("display_name", spec.get("output_item", recipe_id)))
            lvl_req = spec.get("level", 1)
            output_item = str(spec.get("output_item", display_name))
            output_qty = spec.get("output_qty", 1) or 1
            reqs = spec.get("requirements", {}) or {}
            station_word = "Smelt" if spec.get("station") == "furnace" else "Forge"

            label = f"{display_name} (Lvl {lvl_req})"
            if output_qty > 1:
                label += f" — makes {output_qty}"
            child = QTreeWidgetItem([label])
            child.setData(0, Qt.ItemDataRole.UserRole, recipe_id)

            icon_path = _icon_for(output_item)
            if icon_path and os.path.exists(icon_path):
                child.setIcon(0, QIcon(icon_path))

            mat_lines = [f"  {mat} x{amt} (you have {inv.get(mat, 0)})" for mat, amt in reqs.items()]
            mat_text = "\n".join(mat_lines) if mat_lines else "  none"
            tooltip = (
                f"{station_word} · requires Smithing level {lvl_req}. You have {lvl_have}.\n"
                f"Output: {output_item} x{output_qty}\n"
                f"Base XP: {spec.get('exp', 0)} per action\n"
                f"Materials:\n{mat_text}"
            )
            if not can_smith_item_pure(lvl_have, inv, recipe_id, SMITHING_DATA):
                child.setDisabled(True)
                reason = []
                if lvl_have < lvl_req:
                    reason.append(f"level {lvl_req}")
                if any(inv.get(mat, 0) < amt for mat, amt in reqs.items()):
                    reason.append("materials")
                if reason:
                    tooltip += "\nLocked due to: " + ", ".join(reason)
            child.setToolTip(0, tooltip)
            return child

        # Group recipes by metal tier, preserving the smelt-bar progression order
        # (Bronze, Blurite, Iron, Silver, Steel, Gold, Mithril, Adamant, Rune)
        # that SMITHING_DATA already lists smelt rows in.
        order: list = []
        groups: dict = {}
        for recipe_id, spec in SMITHING_DATA.items():
            tier = _smith_tier_of(spec)
            if tier not in groups:
                groups[tier] = []
                order.append(tier)
            groups[tier].append((recipe_id, spec))

        selected_child = None
        for tier in order:
            parent = QTreeWidgetItem([f"{tier}  ({len(groups[tier])})"])
            parent.setData(0, Qt.ItemDataRole.UserRole, f"__tier__:{tier}")
            parent.setFlags(Qt.ItemFlag.ItemIsEnabled)  # selectable-off; expand still works
            font = parent.font(0)
            font.setBold(True)
            parent.setFont(0, font)
            tree.addTopLevelItem(parent)
            # Within a metal group, order by required level (then smelt before
            # forge on ties so the bar leads, then name) — a low→high progression
            # reads far better than the source/BarProducts emit order.
            ordered = sorted(
                groups[tier],
                key=lambda rs: (
                    rs[1].get("level", 1),
                    0 if rs[1].get("station") == "furnace" else 1,
                    str(rs[1].get("display_name", "")),
                ),
            )
            for recipe_id, spec in ordered:
                child = _make_child(recipe_id, spec)
                parent.addChild(child)
                if recipe_id == current:
                    selected_child = child
            # Collapsed by default; expanded if the user previously expanded this
            # tier or it holds the current target. Set before connecting the
            # expand/collapse signals so building doesn't rewrite persisted state.
            parent.setExpanded(tier in expanded or tier == cur_tier)

        if selected_child is not None:
            tree.setCurrentItem(selected_child)

        def _on_smith_clicked(item: "QTreeWidgetItem", _column: int = 0):
            if item is None:
                return
            recipe_id = item.data(0, Qt.ItemDataRole.UserRole)
            if not recipe_id or str(recipe_id).startswith("__tier__"):
                return
            if on_set_smith is not None:
                on_set_smith(recipe_id)
            else:
                spec = SMITHING_DATA.get(recipe_id, {})
                if spec.get("station") == "furnace":
                    on_set_bar(spec.get("output_item", recipe_id))

        def _tier_label(item: "QTreeWidgetItem") -> Optional[str]:
            role = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(role, str) and role.startswith("__tier__:"):
                return role.split(":", 1)[1]
            return None

        tree.itemClicked.connect(_on_smith_clicked)
        tree.itemActivated.connect(_on_smith_clicked)
        tree.itemExpanded.connect(
            lambda it: (_tier_label(it) and set_smith_tier_expanded(_tier_label(it), True))
        )
        tree.itemCollapsed.connect(
            lambda it: (_tier_label(it) and set_smith_tier_expanded(_tier_label(it), False))
        )
        return tree

    def _build_craft_list() -> QListWidget:
        craft_list = QListWidget()
        craft_list.setIconSize(QSize(28, 28))
        craft_list.setAlternatingRowColors(True)
        for item_name, spec in CRAFTING_DATA.items():
            item = QListWidgetItem(f"{item_name} (Lvl {spec['level']})")
            item.setData(Qt.ItemDataRole.UserRole, item_name)
            c_icon = CRAFTED_ITEM_IMAGES.get(item_name)
            if c_icon and os.path.exists(c_icon):
                item.setIcon(QIcon(c_icon))
            lvl_req = spec.get('level', 1)
            lvl_have = player_data.get("crafting_level", 1)
            inv = player_data.get('inventory', {})
            reqs = spec.get('requirements', {})
            materials_ok = True
            mat_lines = []
            for mat, amt in reqs.items():
                have = inv.get(mat, 0)
                if have < amt:
                    materials_ok = False
                mat_lines.append(f"{mat} x{amt} (you have {have})")
            mat_text = "\n".join(mat_lines) if mat_lines else "No materials required"
            output_item = spec.get("output_item", item_name)
            output_qty = spec.get("output_qty", 1)
            batch_size = spec.get("batch_size", 1)
            output_line = f"Output: {output_item} x{output_qty}"
            if batch_size and batch_size > 1:
                output_line += f" (up to {batch_size} per successful card)"
            tooltip = (
                f"Requires Crafting level {lvl_req}. You have {lvl_have}.\n"
                f"{output_line}\nMaterials:\n{mat_text}"
            )
            if not can_craft_item_pure(player_data.get("crafting_level", 1), player_data.get("inventory", {}), item_name, CRAFTING_DATA):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                reason = []
                if lvl_have < lvl_req:
                    reason.append(f"level {lvl_req}")
                if not materials_ok:
                    reason.append("materials")
                if reason:
                    tooltip += "\nLocked due to: " + ", ".join(reason)
            item.setToolTip(tooltip)
            craft_list.addItem(item)
            if item_name == player_data.get("current_craft"):
                craft_list.setCurrentItem(item)

        def _on_craft_selected(item: QListWidgetItem):
            if item:
                on_set_craft(item.data(Qt.ItemDataRole.UserRole))
        craft_list.itemClicked.connect(_on_craft_selected)
        craft_list.itemActivated.connect(_on_craft_selected)
        return craft_list

    def _build_fletch_list() -> QListWidget:
        # Fletching is a processing skill like Crafting: it consumes logs and
        # produces fletched items, so the row gating mirrors the craft list.
        fletch_list = QListWidget()
        fletch_list.setIconSize(QSize(28, 28))
        fletch_list.setAlternatingRowColors(True)
        for target_key, spec in FLETCHING_DATA.items():
            display_name = spec.get("display_name", target_key)
            output_item = spec.get("output_item", display_name)
            output_qty = spec.get("output_qty", 1)
            item = QListWidgetItem(f"{display_name} (Lvl {spec['level']})")
            item.setData(Qt.ItemDataRole.UserRole, target_key)
            f_icon = FLETCHED_ITEM_IMAGES.get(output_item)
            if f_icon and os.path.exists(f_icon):
                item.setIcon(QIcon(f_icon))
            lvl_req = spec.get('level', 1)
            lvl_have = player_data.get("fletching_level", 1)
            inv = player_data.get('inventory', {})
            reqs = spec.get('requirements', {})
            materials_ok = True
            mat_lines = []
            for mat, amt in reqs.items():
                have = inv.get(mat, 0)
                if have < amt:
                    materials_ok = False
                mat_lines.append(f"{mat} x{amt} (you have {have})")
            mat_text = "\n".join(mat_lines) if mat_lines else "No materials required"
            tooltip = (
                f"Requires Fletching level {lvl_req}. You have {lvl_have}.\n"
                f"Output: {output_item} x{output_qty}\nMaterials:\n{mat_text}"
            )
            if not can_fletch_item_pure(lvl_have, inv, target_key, FLETCHING_DATA):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                reason = []
                if lvl_have < lvl_req:
                    reason.append(f"level {lvl_req}")
                if not materials_ok:
                    reason.append("materials")
                if reason:
                    tooltip += "\nLocked due to: " + ", ".join(reason)
            item.setToolTip(tooltip)
            fletch_list.addItem(item)
            if target_key == player_data.get("current_fletch"):
                fletch_list.setCurrentItem(item)

        def _on_fletch_selected(item: QListWidgetItem):
            if item and on_set_fletch is not None:
                on_set_fletch(item.data(Qt.ItemDataRole.UserRole))
        fletch_list.itemClicked.connect(_on_fletch_selected)
        fletch_list.itemActivated.connect(_on_fletch_selected)
        return fletch_list

    def _build_utility_list() -> QListWidget:
        # Utility / Activities are no-XP material prep. Each successful card runs
        # a batch (up to batch_size, capped by inventory), so tooltips lead with
        # the batch + no-XP framing to set expectations apart from XP skills.
        utility_list = QListWidget()
        utility_list.setIconSize(QSize(28, 28))
        utility_list.setAlternatingRowColors(True)
        inv = player_data.get("inventory", {})
        for activity_key, spec in UTILITY_ACTIVITY_DATA.items():
            label = str(spec.get("display_name", activity_key))
            batch_size = spec.get("batch_size", 1)
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, activity_key)

            # Bird-nest opening consumes nests (no fixed "output_item"); its
            # contents are rolled from source tables, so it gets bespoke tooltip
            # + lock handling rather than the requirement/output framing.
            openable_items = spec.get("openable_items")
            if openable_items:
                have_nests = sum(inv.get(nest, 0) for nest in openable_items)
                tooltip = (
                    f"Opens up to {batch_size} bird nests per successful card. No XP.\n"
                    "Rolls source seed / ring / egg contents into your bank.\n"
                    f"Bird nests held: {have_nests} (drop while Woodcutting)"
                )
                if not can_open_bird_nests_pure(inv, BIRD_NEST_OPEN_TABLES):
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    tooltip += "\nLocked: cut trees until a bird nest drops."
            else:
                output_item = str(spec.get("output_item", label))
                output_qty = spec.get("output_qty", 1)
                u_icon = UTILITY_ITEM_IMAGES.get(output_item)
                if u_icon and os.path.exists(u_icon):
                    item.setIcon(QIcon(u_icon))
                reqs = spec.get("requirements", {})
                if reqs:
                    mat_lines = [f"{mat} x{amt} (you have {inv.get(mat, 0)})" for mat, amt in reqs.items()]
                    mat_text = "\n".join(mat_lines)
                else:
                    mat_text = "No materials required"
                tooltip = (
                    f"Processes up to {batch_size} per successful card. No Crafting XP.\n"
                    f"Output: {output_item} x{output_qty} per item\nMaterials:\n{mat_text}"
                )
                if not can_perform_utility_activity_pure(inv, activity_key, UTILITY_ACTIVITY_DATA):
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    tooltip += "\nLocked: gather the required materials first."
            item.setToolTip(tooltip)
            utility_list.addItem(item)
            if activity_key == player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY):
                utility_list.setCurrentItem(item)

        def _on_utility_selected(item: QListWidgetItem):
            if item and on_set_utility is not None:
                on_set_utility(item.data(Qt.ItemDataRole.UserRole))
        utility_list.itemClicked.connect(_on_utility_selected)
        utility_list.itemActivated.connect(_on_utility_selected)
        return utility_list

    _TARGET_BUILDERS = {
        "Mining": _build_ore_list,
        "Woodcutting": _build_tree_list,
        "Smithing": _build_smith_list,
        "Crafting": _build_craft_list,
        "Fletching": _build_fletch_list,
        _UTILITY_HUB_NAME: _build_utility_list,
    }
    _TARGET_PROMPTS = {
        "Mining": "Select Ore to Mine",
        "Woodcutting": "Select Tree to Cut",
        "Smithing": "Select what to Smelt or Forge",
        "Crafting": "Select Item to Craft",
        "Fletching": "Select Item to Fletch",
        _UTILITY_HUB_NAME: "Select an Activity (no XP)",
    }

    def _skill_icon_path(display_name: str) -> str:
        icon_files = {
            "Mining": "mining_icon.png",
            "Woodcutting": "woodcutting_icon.png",
            "Smithing": "smithing_icon.png",
            "Crafting": "crafting_icon.png",
            "Fletching": "fletching_icon.png",
        }
        return os.path.join(current_dir, "icon", icon_files.get(display_name, "achievement_icon.png"))

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
        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(8)
        if is_utility:
            # No level/XP for Utility; keep the title bare and flag the no-XP nature.
            title = QLabel(name)
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
                    " QPushButton:disabled { color: palette(mid); }"
                )
                if not available:
                    if name == "Smithing":
                        train_btn.setToolTip("Mine ores until you can smelt a bar.")
                    elif name == "Crafting":
                        train_btn.setToolTip("Gather materials or level up to craft an item.")
                    elif name == "Fletching":
                        train_btn.setToolTip("Cut logs or level up to fletch an item.")
            train_btn.clicked.connect(lambda _=False, n=name: _set_active(n))
            hl.addWidget(train_btn)
            if name == "Smithing":
                _MAIN_MENU_CTX["smith_btn"] = train_btn
            elif name == "Crafting":
                _MAIN_MENU_CTX["craft_btn"] = train_btn
            elif name == "Fletching":
                _MAIN_MENU_CTX["fletch_btn"] = train_btn
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
                {"dialog": None, "smith_btn": None, "craft_btn": None, "fletch_btn": None, "warn_label": None}
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
        from aqt.qt import QToolButton  # type: ignore
    except Exception:
        QToolButton = QPushButton  # fallback for typing

    button_group = QButtonGroup()
    button_group.setExclusive(True)
    buttons = {}
    for idx, (name, icon_path) in enumerate(skills_info):
        btn = QToolButton()
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
    bank_list = QListWidget()
    bank_list.setIconSize(QSize(28, 28))
    bank_list.setAlternatingRowColors(True)
    # Inventory is grouped by item-registry category (Ores, Logs, ..., Fletched,
    # Materials) so newly registered items appear cleanly without per-skill
    # branches. Each item's icon comes from its ItemDefinition.asset_path, with a
    # legacy image-map fallback for anything predating the manifest.
    inv = player_data.get("inventory", {})
    _legacy_icon_maps = (ORE_IMAGES, TREE_IMAGES, BAR_IMAGES, GEM_IMAGES, CRAFTED_ITEM_IMAGES, FLETCHED_ITEM_IMAGES)

    def _bank_icon_path(item_name: str, asset_path) -> Optional[str]:
        if asset_path and os.path.exists(asset_path):
            return asset_path
        for image_map in _legacy_icon_maps:
            candidate = image_map.get(item_name)
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    def _add_bank_header(label: str) -> None:
        header = QListWidgetItem(label)
        header.setFlags(Qt.ItemFlag.NoItemFlags)
        header_font = header.font()
        header_font.setBold(True)
        header.setFont(header_font)
        header.setData(Qt.ItemDataRole.UserRole, "__header__")
        bank_list.addItem(header)

    def _add_gear_row(text: str, item_name: str) -> None:
        li = QListWidgetItem(text)
        definition = _item_def_for(item_name)
        asset_path = definition.asset_path if definition is not None else None
        icon_path = _bank_icon_path(item_name, asset_path)
        if icon_path:
            li.setIcon(QIcon(icon_path))
        li.setFlags(Qt.ItemFlag.ItemIsEnabled)
        li.setData(Qt.ItemDataRole.UserRole, "__gear__")
        bank_list.addItem(li)

    groups = grouped_inventory(inv)
    if not groups:
        empty = QListWidgetItem("Your bank is empty — train a skill to gather items.")
        empty.setFlags(Qt.ItemFlag.NoItemFlags)
        bank_list.addItem(empty)
    for category_label, rows in groups:
        _add_bank_header(category_label)
        for item_name, amount, asset_path in rows:
            li = QListWidgetItem(f"{item_name} x{amount}")
            icon_path = _bank_icon_path(item_name, asset_path)
            if icon_path:
                li.setIcon(QIcon(icon_path))
            bank_list.addItem(li)

    # Gear lives below the inventory: the toolbelt is auto-resolved (best owned
    # tool wins) so we show the active pickaxe/hatchet, and owned_equipment
    # shares one "Equipped" space until real armour/weapon slots exist.
    gear = bank_gear_rows_pure(player_data, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA, MINING_BONUS_ITEM_DATA)
    if gear["toolbelt"]:
        _add_bank_header("Toolbelt")
        for slot_label, display_name in gear["toolbelt"]:
            _add_gear_row(f"{slot_label}: {display_name}", display_name)
    _add_bank_header("Equipped")
    if gear["equipped"]:
        for slot_label, display_name in gear["equipped"]:
            _add_gear_row(f"{display_name} — {slot_label}", display_name)
    else:
        empty_eq = QListWidgetItem("Nothing equipped yet.")
        empty_eq.setFlags(Qt.ItemFlag.NoItemFlags)
        empty_eq.setData(Qt.ItemDataRole.UserRole, "__gear_empty__")
        bank_list.addItem(empty_eq)
    bk_layout.addWidget(bank_list)
    tabs.addTab(bank_tab, "Bank")
    tabs.setTabToolTip(tabs.indexOf(bank_tab), "View all your items")

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

    difficulties = ["Easy", "Moderate", "Difficult", "Very Challenging"]
    for difficulty in difficulties:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        # Count per difficulty
        items = [(n, d) for n, d in ACHIEVEMENTS.items() if d.get("difficulty") == difficulty]
        done = sum(1 for n, _ in items if n in player_data.get("completed_achievements", []))
        header = QLabel(f"{difficulty} • {done}/{len(items)} completed")
        header.setStyleSheet("font-weight: 600; margin: 0 0 6px 0;")
        tab_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(8)
        for name, data in items:
            card = _make_achievement_card(name, data.get("description", ""), name in player_data.get("completed_achievements", []))
            cl.addWidget(card)
        cl.addStretch(1)
        scroll.setWidget(content)
        tab_layout.addWidget(scroll)
        a_tabs.addTab(tab, difficulty)

    a_layout.addWidget(a_tabs)

    completed_count = len(player_data.get("completed_achievements", []))
    total_count = len(ACHIEVEMENTS)
    progress_percentage = (completed_count / max(1, total_count)) * 100
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
    floating_position = "right"
    floating_xp_enabled = True
    popups_enabled = True
    review_hud_enabled = True
    try:
        if mw and getattr(mw, 'col', None):
            floating_enabled = bool(mw.col.get_config("ankiscape_floating_enabled", True))
            pos = mw.col.get_config("ankiscape_floating_position", "right")
            floating_position = pos if pos in ("left", "right") else "right"
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
    rb_group.addButton(rb_right)
    rb_group.addButton(rb_left)
    rb_right.setChecked(floating_position == "right")
    rb_left.setChecked(floating_position == "left")
    prl.addWidget(rb_left)
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
    _sync_pos_enabled()
    enabled_cb.stateChanged.connect(lambda _=None: _sync_pos_enabled())

    if callable(on_set_floating_enabled):
        enabled_cb.stateChanged.connect(lambda _=None: on_set_floating_enabled(bool(enabled_cb.isChecked())))
    if callable(on_set_floating_position):
        rb_left.toggled.connect(lambda checked=False: checked and on_set_floating_position("left"))
        rb_right.toggled.connect(lambda checked=False: checked and on_set_floating_position("right"))

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
                ):
                    item_image = QLabel()
                    _item_def = _item_def_for(item)
                    pixmap = QPixmap(
                        ORE_IMAGES.get(item)
                        or BAR_IMAGES.get(item)
                        or GEM_IMAGES.get(item)
                        or CRAFTED_ITEM_IMAGES.get(item)
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

        tabs.addTab(create_skill_tab("Mining"), "Mining")
        tabs.addTab(create_skill_tab("Woodcutting"), "Woodcutting")
        tabs.addTab(create_skill_tab("Smithing"), "Smithing")
        tabs.addTab(create_skill_tab("Crafting"), "Crafting")

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

    difficulties = ["Easy", "Moderate", "Difficult", "Very Challenging"]

    for difficulty in difficulties:
        tab = QWidget()
        tab_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        for achievement, data in ACHIEVEMENTS.items():
            if data["difficulty"] == difficulty:
                achievement_widget = QWidget()
                achievement_layout = QHBoxLayout()

                icon_label = QLabel()
                icon_path = os.path.join(current_dir, "icon", f"{achievement.lower().replace(' ', '_')}.png")
                if os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                else:
                    pixmap = QPixmap(os.path.join(current_dir, "icon", "achievement_icon.png"))
                icon_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio))
                achievement_layout.addWidget(icon_label)

                info_widget = QWidget()
                info_layout = QVBoxLayout()
                name_label = QLabel(achievement)
                name_label.setStyleSheet("font-weight: bold; color: #333333; font-size: 16px;")
                desc_label = QLabel(data["description"])
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("color: #666666; font-size: 14px;")
                info_layout.addWidget(name_label)
                info_layout.addWidget(desc_label)
                info_widget.setLayout(info_layout)
                achievement_layout.addWidget(info_widget, stretch=1)

                completed = achievement in player_data["completed_achievements"]
                status_label = QLabel("✓" if completed else "")
                status_label.setStyleSheet("color: #4CAF50; font-size: 24px; font-weight: bold;")
                achievement_layout.addWidget(status_label)

                achievement_widget.setLayout(achievement_layout)
                achievement_widget.setStyleSheet(
                    f"""
                    background-color: {'#e8f5e9' if completed else 'white'};
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

    completed_count = len(player_data["completed_achievements"])
    total_count = len(ACHIEVEMENTS)
    progress_percentage = (completed_count / total_count) * 100
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
