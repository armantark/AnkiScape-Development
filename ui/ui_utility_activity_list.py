"""ui_utility_activity_list.py - the Utilities and Activities lists and their search bar.

One builder draws both no-XP lists. The search bar is the shared
CatalogFilterBar the Skills target lists use, and a query goes through that
bar's matcher with the same fields: a row's name, its group and the group's
label. A query hides and ranks the existing rows within groups, because the
Activities panel outlives each visit and the hub's Minigames and D&D entries
show slices of the same items. Typing never selects or activates a row, so the
current utility or activity never changes while the player searches.
"""
import os
from typing import Optional

try:
    from aqt.qt import (  # type: ignore
        QAbstractItemView,
        QColor,
        QPalette,
        QSize,
        Qt,
        QTreeWidget,
        QTreeWidgetItem,
    )

    class _SearchItem(QTreeWidgetItem):
        def __lt__(self, other):
            return self.search_order < other.search_order

    # Flat activity rows have no group parent, so each row carries its group.
    _ACTIVITY_GROUP_ROLE = int(Qt.ItemDataRole.UserRole) + 1
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass

from ..core.constants import (
    ACTIVITY_SURFACE_ID,
    BIRD_NEST_OPEN_TABLES,
    COOKING_ITEM_IMAGES,
    DEFAULT_UTILITY_ACTIVITY,
    QUEST_UNLOCK_RULES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
    UTILITY_SURFACE_ID,
    current_dir,
)
from ..core.search_match import match_rank
from ..core.target_metadata import TargetRowMetadata, mage_arena_attunement_rows_pure, utility_activity_rows
from ..data.evil_tree_data import EVIL_TREE_UTILITY_ID
from ..logic.dnd_favourites_logic import dnd_activity_display_name_pure
from ..logic_pure.logic_pure import (
    KNIGHT_WAVES_TOTAL_STEPS,
    MAGE_ARENA_GOD_DATA,
    MAGE_ARENA_TOTAL_STEPS,
    STRONGHOLD_REWARD_COINS,
    STRONGHOLD_STEP_NAMES,
    STRONGHOLD_TOTAL_STEPS,
    knight_waves_locked_reasons_pure,
    mage_arena_locked_reasons_pure,
    sanitize_mage_arena_state_pure,
)
from .ui import (
    _ACTIVITY_GROUP_ICONS,
    _ACTIVITY_SELECTION_GROUPS,
    _KNIGHT_WAVES_UTILITY_KEY,
    _MAGE_ARENA_UTILITY_KEY,
    _STRONGHOLD_UTILITY_KEY,
    _UTILITY_GROUP_LABELS,
    CatalogFilterBar,
    _pixel_path_icon,
    activity_collapsed_groups,
    dim_text_color,
    dim_text_css,
    set_activity_group_collapsed,
)

_GROUP_ROLE_PREFIX = "__utility_group__:"


class UtilityActivityList:
    """The shared search bar above one Utilities or Activities tree.

    The surface lays out ``filter_bar`` above ``tree`` and wires the tree's
    clicks. ``marked_id`` is the saved utility or activity when the tree holds
    its row, else "".
    """

    def __init__(self, player_data: dict, *, is_activities: bool) -> None:
        self._current = player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
        self._noun = "activities" if is_activities else "utilities"
        self._group = ""
        self._held_expansion: Optional[list] = None
        self._empty_row = None
        self.filter_bar = CatalogFilterBar(
            placeholder=f"Search {self._noun}",
            search_object_name="utilityActivityTargetSearchInput",
        )
        self.tree = _styled_tree()
        marked = _fill_tree(self.tree, player_data, self._current, is_activities)
        self.marked_id = self._current if marked is not None else ""
        _remember_order(self.tree)
        self._apply_view()
        if marked is not None:
            _mark_row(self.tree, marked)
        if is_activities:
            _save_group_collapses(self.tree)
        self.filter_bar.search_input.textChanged.connect(
            lambda _text="": self._apply_view()
        )

    def show_group(self, group: object) -> None:
        """Show one hub slice of the Activities list (Minigames, D&D), or "" for the rest."""
        selected = str(group or "")
        self._group = selected if selected in _ACTIVITY_SELECTION_GROUPS else ""
        self._apply_view()
        current_item = self.tree.currentItem()
        if current_item is not None and current_item.isHidden():
            self.tree.clearSelection()
        if not self._group:
            return
        for item in _top_level_items(self.tree):
            if not item.isHidden() and _row_id(item) == self._current:
                _mark_row(self.tree, item)
                return

    def _apply_view(self) -> None:
        filtering = bool(self.filter_bar.query())
        # Search-driven opening is never saved as the player's own choice.
        self.tree.blockSignals(True)
        self._drop_empty_row()
        self._hold_expansion(filtering)
        _rank_tree(self.tree, self.filter_bar.query())
        shown = total = 0
        for item in _top_level_items(self.tree):
            in_view = _in_group_view(item, self._group)
            item.setHidden(not in_view)
            if in_view:
                item_shown, item_total = _filter_branch(
                    self.filter_bar, item, _flat_row_context(item), filtering
                )
                shown += item_shown
                total += item_total
        if filtering and not shown:
            self._add_empty_row()
        self.tree.blockSignals(False)
        self.filter_bar.set_count(shown, total)

    def _hold_expansion(self, filtering: bool) -> None:
        # A query opens every group that holds a match; clearing it puts back
        # the groups that were open before the search began.
        if filtering and self._held_expansion is None:
            self._held_expansion = [
                (item, item.isExpanded()) for item in _branches(self.tree)
            ]
        elif not filtering and self._held_expansion is not None:
            for item, expanded in self._held_expansion:
                item.setExpanded(expanded)
            self._held_expansion = None

    def _add_empty_row(self) -> None:
        empty = _SearchItem([f"No {self._noun} match this search."])
        empty.setFlags(Qt.ItemFlag.NoItemFlags)
        empty.setForeground(0, dim_text_color(self.tree))
        self.tree.addTopLevelItem(empty)
        self._empty_row = empty

    def _drop_empty_row(self) -> None:
        if self._empty_row is not None:
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(self._empty_row))
            self._empty_row = None


def _styled_tree() -> "QTreeWidget":
    tree = QTreeWidget()
    tree.setObjectName("utilityActivityTree")
    tree.setHeaderHidden(True)
    tree.setIconSize(QSize(28, 28))
    tree.setRootIsDecorated(True)
    tree.setIndentation(14)
    tree.setUniformRowHeights(True)
    tree.setMinimumHeight(140)
    tree_base = tree.palette().color(QPalette.ColorRole.Base)
    activity_selection = QColor(
        round((tree_base.red() * 0.70) + (76 * 0.30)),
        round((tree_base.green() * 0.70) + (175 * 0.30)),
        round((tree_base.blue() * 0.70) + (80 * 0.30)),
    ).name()
    tree.setStyleSheet(
        "QTreeWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); padding: 4px; }"
        " QTreeWidget::item { min-height: 32px; padding: 5px;"
        " border-radius: 6px; }"
        f" QTreeWidget::item:selected {{ background: {activity_selection};"
        " color: palette(text); }"
        f" QTreeWidget::branch:selected {{ background: {activity_selection}; }}"
        f" QTreeWidget::item:disabled {{ color: {dim_text_css(tree)}; }}"
    )
    return tree


def _fill_tree(tree, player_data: dict, current: str, is_activities: bool):
    """Add every row of the surface; return the item for the saved row, if any."""
    groups = _rows_by_group(_surface_rows(player_data, current, is_activities))
    collapsed = activity_collapsed_groups() if is_activities else set()
    marked = None
    for group, group_rows in groups.items():
        if group_rows and not (is_activities and group == "landmarks"):
            marked = _add_row_group(
                tree, group, group_rows, current, is_activities, collapsed
            ) or marked
    if is_activities:
        landmarks = _add_landmarks(tree, player_data, groups.get("landmarks", []), current)
        landmarks.setExpanded("landmarks" not in collapsed)
        marked = _marked_landmark(landmarks, player_data, current) or marked
    return marked


def _surface_rows(player_data: dict, current: str, is_activities: bool) -> tuple:
    rows = utility_activity_rows(
        player_data,
        UTILITY_ACTIVITY_DATA,
        {**UTILITY_ITEM_IMAGES, **COOKING_ITEM_IMAGES},
        BIRD_NEST_OPEN_TABLES,
        DEFAULT_UTILITY_ACTIVITY,
        QUEST_UNLOCK_RULES,
    )
    surface_id = ACTIVITY_SURFACE_ID if is_activities else UTILITY_SURFACE_ID
    rows = tuple(
        row
        for row in rows
        if UTILITY_ACTIVITY_DATA.get(row.target_id, {}).get("surface") == surface_id
    )
    if not is_activities:
        return rows
    return (
        *rows,
        TargetRowMetadata(
            target_id=EVIL_TREE_UTILITY_ID,
            label=dnd_activity_display_name_pure(EVIL_TREE_UTILITY_ID),
            tooltip=(
                "A review-clock world event. Open its panel for the live "
                "tree, blessing, and participation status."
            ),
            current=current == EVIL_TREE_UTILITY_ID,
            navigation_enabled=True,
            icon_path=_ACTIVITY_GROUP_ICONS["distractions_and_diversions"],
            group="distractions_and_diversions",
        ),
    )


def _rows_by_group(rows: tuple) -> dict:
    groups: dict = {group: [] for group in _UTILITY_GROUP_LABELS}
    for row in rows:
        spec = UTILITY_ACTIVITY_DATA.get(row.target_id, {})
        group = str(spec.get("group") or row.group or "material_processing")
        groups.setdefault(group, []).append(row)
    return groups


def _add_row_group(tree, group: str, rows: list, current: str, is_activities: bool, collapsed: set):
    """Add one group's rows, under a header unless the hub lists the group flat.

    Return the item for the saved row, if the group holds it.
    """
    if is_activities:
        rows = sorted(rows, key=lambda row: str(row.label).casefold())
    flat = is_activities and group in _ACTIVITY_SELECTION_GROUPS
    parent = None if flat else _group_header(tree, group)
    marked = None
    for row in rows:
        child = _group_row_item(row, group)
        if parent is None:
            tree.addTopLevelItem(child)
        else:
            parent.addChild(child)
        if row.target_id == current:
            marked = child
    if parent is not None:
        parent.setExpanded(group not in collapsed if is_activities else marked is not None)
    return marked


def _group_header(tree, group: str) -> "QTreeWidgetItem":
    # The view writes the visible-row count after the label.
    header = _SearchItem([_group_label(group)])
    header.setData(0, Qt.ItemDataRole.UserRole, f"{_GROUP_ROLE_PREFIX}{group}")
    header.setFlags(Qt.ItemFlag.ItemIsEnabled)
    font = header.font(0)
    font.setBold(True)
    header.setFont(0, font)
    tree.addTopLevelItem(header)
    return header


def _group_row_item(row, group: str) -> "QTreeWidgetItem":
    item = _row_item(row.label, row.target_id, row.tooltip, row.icon_path)
    item.setData(0, _ACTIVITY_GROUP_ROLE, group)
    if not row.navigation_enabled:
        item.setDisabled(True)
    return item


def _row_item(label: str, row_id: str, tooltip: str, icon_path=None) -> "QTreeWidgetItem":
    item = _SearchItem([label])
    item.setData(0, Qt.ItemDataRole.UserRole, row_id)
    item.setToolTip(0, tooltip)
    icon = _pixel_path_icon(icon_path, 28) if icon_path else None
    if icon is not None:
        item.setIcon(0, icon)
    return item


def _add_landmarks(tree, player_data: dict, landmark_rows: list, current: str) -> "QTreeWidgetItem":
    """Add the Landmarks group under its header and return the header.

    Stronghold of Security, Knight Waves and Mage Arena are step counters, not
    repeatable UTILITY_ACTIVITY_DATA activities, so they are injected by hand.
    """
    parent = _group_header(tree, "landmarks")
    parent.addChild(_stronghold_item(player_data))
    for row in landmark_rows:
        parent.addChild(_row_item(row.label, row.target_id, row.tooltip, row.icon_path))
    parent.addChild(_knight_waves_item(player_data))
    mage_arena = sanitize_mage_arena_state_pure(player_data.get("mage_arena"))
    parent.addChild(_mage_arena_item(player_data, mage_arena))
    step = max(0, min(int(mage_arena.get("step", 0) or 0), MAGE_ARENA_TOTAL_STEPS))
    if mage_arena.get("completed"):
        _add_mage_arena_statues(parent, player_data, mage_arena, current)
    elif step == MAGE_ARENA_TOTAL_STEPS - 1:
        _add_alignment_choices(parent)
    return parent


def _marked_landmark(landmarks, player_data: dict, current: str):
    # A finished step counter is no longer something to resume.
    finished = {
        _STRONGHOLD_UTILITY_KEY: (player_data.get("stronghold_of_security") or {}).get("completed"),
        _KNIGHT_WAVES_UTILITY_KEY: (player_data.get("knight_waves") or {}).get("completed"),
        _MAGE_ARENA_UTILITY_KEY: sanitize_mage_arena_state_pure(
            player_data.get("mage_arena")
        ).get("completed"),
    }
    if finished.get(current):
        return None
    for index in range(landmarks.childCount()):
        if _row_id(landmarks.child(index)) == current:
            return landmarks.child(index)
    return None


def _landmark_icon(name: str) -> str:
    return os.path.join(current_dir, "icon", name)


def _stronghold_item(player_data: dict) -> "QTreeWidgetItem":
    state = player_data.get("stronghold_of_security") or {}
    completed = bool(state.get("completed"))
    claimed = state.get("boots_choice") is not None
    step = max(0, min(int(state.get("step", 0) or 0), STRONGHOLD_TOTAL_STEPS))
    if completed and not claimed:
        label = "Stronghold of Security — Claim your reward ✨"
        tooltip = (
            f"Cleared! Click to choose your boots and collect {STRONGHOLD_REWARD_COINS:,} coins."
        )
    elif completed:
        label = f"Stronghold of Security ✓  ({state.get('boots_choice')})"
        tooltip = "Completed. Reward already claimed."
    else:
        next_name = STRONGHOLD_STEP_NAMES[step] if step < STRONGHOLD_TOTAL_STEPS else STRONGHOLD_STEP_NAMES[-1]
        label = f"Stronghold of Security — {step}/{STRONGHOLD_TOTAL_STEPS}  (next: {next_name})"
        tooltip = (
            "A one-time landmark. Set it as your activity and each review clears "
            "one level. No XP along the way, but coins and boots at the end."
        )
    item = _row_item(label, _STRONGHOLD_UTILITY_KEY, tooltip, _landmark_icon("attack_icon.png"))
    item.setDisabled(completed and claimed)
    return item


def _knight_waves_item(player_data: dict) -> "QTreeWidgetItem":
    state = player_data.get("knight_waves") or {}
    step = max(0, min(int(state.get("step", 0) or 0), KNIGHT_WAVES_TOTAL_STEPS))
    completed = bool(state.get("completed"))
    locked = knight_waves_locked_reasons_pure(player_data)
    label = (
        "Knight Waves Training Ground ✓"
        if completed
        else f"Knight Waves Training Ground — {step}/{KNIGHT_WAVES_TOTAL_STEPS}"
    )
    tooltip = (
        "Defeat eight knights, one per review. Completion grants 20,000 XP in Attack, Strength, Defence, and Constitution and unlocks Chivalry/Piety."
        + (f"\nLocked due to: {', '.join(locked)}" if locked and not completed else "")
    )
    item = _row_item(label, _KNIGHT_WAVES_UTILITY_KEY, tooltip, _landmark_icon("prayer_icon.png"))
    item.setDisabled(bool(completed or locked))
    return item


def _mage_arena_item(player_data: dict, state: dict) -> "QTreeWidgetItem":
    step = max(0, min(int(state.get("step", 0) or 0), MAGE_ARENA_TOTAL_STEPS))
    completed = bool(state.get("completed"))
    alignment = str(state.get("alignment", "") or "")
    locked = mage_arena_locked_reasons_pure(player_data)
    alignment_label = (
        MAGE_ARENA_GOD_DATA[alignment]["display_name"]
        if alignment in MAGE_ARENA_GOD_DATA
        else ""
    )
    label = (
        f"Mage Arena ✓ · {alignment_label or 'choose alignment'}"
        if completed
        else f"Mage Arena — {step}/{MAGE_ARENA_TOTAL_STEPS} Kolodion forms"
    )
    tooltip = (
        "Defeat Kolodion's five forms, one per review. Choose an alignment before the final form; completion grants its cape, staff, and attunement."
        + (f"\nLocked due to: {', '.join(locked)}" if locked and not completed else "")
    )
    item = _row_item(label, _MAGE_ARENA_UTILITY_KEY, tooltip, _landmark_icon("magic_icon.png"))
    item.setDisabled(bool(completed or locked))
    return item


def _sub_group(parent, title: str) -> "QTreeWidgetItem":
    item = _SearchItem([title])
    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    parent.addChild(item)
    return item


def _add_alignment_choices(parent) -> None:
    choices = _sub_group(parent, "Choose alignment for the final form")
    for god_id, row in MAGE_ARENA_GOD_DATA.items():
        choices.addChild(
            _row_item(
                row["display_name"],
                f"__mage_alignment__:{god_id}",
                f"Final victory grants the {row['cape']} and {row['staff']} and attunes {row['spell_name']}.",
            )
        )
    choices.setExpanded(True)


def _add_mage_arena_statues(parent, player_data: dict, state: dict, current: str) -> None:
    statues = _sub_group(parent, "Mage Arena statues")
    alignment = str(state.get("alignment", "") or "")
    attunements = {row.target_id: row for row in mage_arena_attunement_rows_pure(player_data)}
    for god_id, row in MAGE_ARENA_GOD_DATA.items():
        statues.addChild(
            _row_item(
                _cape_label(row["cape"], god_id, alignment),
                f"__mage_cape__:{god_id}",
                "Instant statue action. Any other god cape is destroyed or replaced; only one may be owned.",
            )
        )
        attunement = attunements.get(f"mage_arena_attune:{god_id}")
        if attunement is not None:
            statues.addChild(_group_row_item(attunement, "landmarks"))
    statues.setExpanded(str(current).startswith("mage_arena_attune:"))


def _cape_label(cape: str, god_id: str, alignment: str) -> str:
    if not alignment:
        return f"Choose {cape}"
    return f"Reclaim {cape}" if god_id == alignment else f"Switch to {cape}"


def _top_level_items(tree) -> list:
    return [tree.topLevelItem(index) for index in range(tree.topLevelItemCount())]


def _children(item) -> list:
    return [item.child(index) for index in range(item.childCount())]


def _branches(tree) -> list:
    found = []
    pending = _top_level_items(tree)
    while pending:
        item = pending.pop()
        if item.childCount():
            found.append(item)
            pending.extend(_children(item))
    return found


def _row_id(item):
    return item.data(0, Qt.ItemDataRole.UserRole)


def _group_id(item) -> str:
    role = _row_id(item)
    if isinstance(role, str) and role.startswith(_GROUP_ROLE_PREFIX):
        return role[len(_GROUP_ROLE_PREFIX):]
    return ""


def _group_label(group: str) -> str:
    return _UTILITY_GROUP_LABELS.get(group, group.replace("_", " ").title())


def _in_group_view(item, group: str) -> bool:
    item_group = str(item.data(0, _ACTIVITY_GROUP_ROLE) or "")
    if group:
        return item_group == group
    return item_group not in _ACTIVITY_SELECTION_GROUPS


def _flat_row_context(item) -> tuple:
    # A flat activity row matches on its group the way a row under a header does.
    group = str(item.data(0, _ACTIVITY_GROUP_ROLE) or "")
    return (group, _group_label(group)) if group else ()


def _remember_order(tree) -> None:
    group_positions = {}
    for index, item in enumerate(_top_level_items(tree)):
        group = item.data(0, _ACTIVITY_GROUP_ROLE)
        item.group_position = group_positions.setdefault(group, index) if group else index
        _remember_branch_order(item, index)


def _remember_branch_order(item, index) -> None:
    item.original_position = index
    item.search_order = (index,)
    for child_index, child in enumerate(_children(item)):
        _remember_branch_order(child, child_index)


def _rank_tree(tree, query: str) -> None:
    for item in _top_level_items(tree):
        rank = _rank_branch(item, query, _flat_row_context(item))
        item.search_order = (item.group_position, rank, item.original_position)
    tree.sortItems(0, Qt.SortOrder.AscendingOrder)


def _rank_branch(item, query: str, context: tuple) -> int:
    rank = match_rank(query, item.text(0), *context)
    tier = 5 if rank is None else rank
    if item.childCount():
        group = _group_id(item)
        inner = (*context, group, _group_label(group)) if group else (*context, item.text(0))
        for child in _children(item):
            child_tier = _rank_branch(child, query, inner)
            child.search_order = (child_tier, child.original_position)
        return 0
    return tier


def _filter_branch(filter_bar, item, context: tuple, filtering: bool) -> tuple:
    """Hide the rows under ``item`` that miss the query; return its (shown, total) rows.

    A row matches on its own text first, then on the headers above it, so a
    group name finds every row in the group.
    """
    if not item.childCount():
        hit = filter_bar.matches_text(item.text(0), *context)
        item.setHidden(not hit)
        return int(hit), 1
    group = _group_id(item)
    inner = (*context, group, _group_label(group)) if group else (*context, item.text(0))
    counts = [_filter_branch(filter_bar, child, inner, filtering) for child in _children(item)]
    shown = sum(count[0] for count in counts)
    item.setHidden(not shown)
    if filtering and shown:
        item.setExpanded(True)
    if group:
        rows = sum(1 for child in _children(item) if _row_id(child) and not child.isHidden())
        item.setText(0, f"{_group_label(group)}  ({rows})")
    return shown, sum(count[1] for count in counts)


def _mark_row(tree, item) -> None:
    ancestor = item.parent()
    while ancestor is not None:
        ancestor.setExpanded(True)
        ancestor = ancestor.parent()
    tree.setCurrentItem(item)
    tree.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)


def _save_group_collapses(tree) -> None:
    tree.itemExpanded.connect(lambda item: _save_group_collapse(item, False))
    tree.itemCollapsed.connect(lambda item: _save_group_collapse(item, True))


def _save_group_collapse(item, collapsed: bool) -> None:
    group = _group_id(item)
    if group:
        set_activity_group_collapsed(group, collapsed)
