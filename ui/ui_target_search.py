"""ui_target_search.py - the search bar over every Skills-tab target list.

Combat and every skill filter through this one selector, so a query behaves
the same everywhere: it matches a row's name and its group, opens the groups
that hold a match, counts the visible rows, and keeps the saved target marked
only while it is visible. Typing never selects or activates a row.

A flat list shows each row's short name (ruling 4.29.8): the lock reason and
the extra catches of a Fishing spot stay in the row tooltip and the Details
panel, which keeps most rows on one line in a list that has little width.
Search still matches the full label.
"""
try:
    from aqt.qt import (  # type: ignore
        QAbstractItemView,
        QListWidget,
        QListWidgetItem,
        QSize,
        Qt,
        QTimer,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass

from ..core.search_match import match_rank
from .ui import CatalogFilterBar, dim_text_color

# Written by the Agility, Thieving and Summoning row builders in core/target_metadata.py.
_LOCK_SUFFIX = " \u2014 Locked: "
_ROW_PADDING = 1


def _add_empty_row(selector, text: str) -> None:
    if isinstance(selector, QTreeWidget):
        empty = QTreeWidgetItem([text])
        empty.setFlags(Qt.ItemFlag.NoItemFlags)
        empty.setForeground(0, dim_text_color(selector))
        selector.addTopLevelItem(empty)
        return
    empty = QListWidgetItem(text)
    empty.setFlags(Qt.ItemFlag.NoItemFlags)
    empty.setForeground(dim_text_color(selector))
    selector.addItem(empty)


def _scroll_saved_target_into_view(selector, live: dict) -> None:
    if live["widget"] is not selector:
        return
    try:
        current = selector.currentItem()
        if current is not None:
            selector.scrollToItem(
                current, QAbstractItemView.ScrollHint.PositionAtCenter
            )
    except RuntimeError:
        return


def _row_rank(filter_bar, row, group_labels: dict, match_tooltip: bool) -> int | None:
    group = row.group or ""
    details = (row.target_id, row.tooltip) if match_tooltip else ()
    return match_rank(
        filter_bar.query(), row.label,
        group,
        group_labels.get(group, group.replace("_", " ")),
        *details,
    )


def _ticked(extra_filter) -> bool:
    return extra_filter is not None and extra_filter[0].isChecked()


def _visible_rows(rows, filter_bar, group_labels: dict, match_tooltip: bool, extra_filter) -> tuple:
    ticked = _ticked(extra_filter)
    ranked = [(_row_rank(filter_bar, row, group_labels, match_tooltip), row)
              for row in rows if not ticked or extra_filter[1](row)]
    return tuple(row for _tier, row in sorted(
        (entry for entry in ranked if entry[0] is not None), key=lambda entry: entry[0]
    ))


def _opened_groups(saved_groups, visible: tuple, filtering: bool) -> set:
    # Search-driven opening joins the saved open groups but is never saved
    # itself: the selector connects its expand signals after it applies these.
    # The saved groups are read on every redraw because the player can open or
    # close a group between keystrokes.
    opened = set(saved_groups()) if saved_groups is not None else set()
    if filtering:
        opened |= {row.group or "other" for row in visible}
    return opened


def _drop_selector(layout, live: dict) -> None:
    previous = live["widget"]
    if previous is not None:
        layout.removeWidget(previous)
        previous.setParent(None)
        previous.deleteLater()


def build_searchable_target_selector(
    build_selector,
    rows,
    *,
    key: str,
    noun: str,
    group_labels=None,
    saved_groups=None,
    extra_filter=None,
    empty_text=None,
    match_tooltip: bool = False,
    **selector_options,
) -> "QWidget":
    """Return a search bar above the selector ``build_selector`` draws for ``rows``.

    ``saved_groups()`` returns the groups the player keeps open.
    ``extra_filter`` is ``(checkbox, accepts_row)``: while the box is ticked
    only accepted rows show. ``empty_text(query)`` words an empty result. The
    caller owns the box's toggle and re-filters through the returned widget's
    ``_ankiscape_render_targets``.
    """
    group_labels = group_labels or {}
    empty_text = empty_text or (lambda _query: f"No {noun} match this search.")
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    filter_bar = CatalogFilterBar(
        placeholder=f"Search {noun}",
        search_object_name=f"{key}TargetSearchInput",
    )
    if extra_filter is not None:
        filter_bar.add_filter(extra_filter[0])
    layout.addWidget(filter_bar)
    live = {"widget": None}

    def _render() -> None:
        _drop_selector(layout, live)
        visible = _visible_rows(rows, filter_bar, group_labels, match_tooltip, extra_filter)
        opened = _opened_groups(
            saved_groups, visible, _ticked(extra_filter) or bool(filter_bar.query())
        )
        selector = build_selector(
            visible, group_labels, expanded_groups=opened, **selector_options
        )
        selector.setObjectName(f"{key}TargetTree")
        if not visible:
            _add_empty_row(selector, empty_text(filter_bar.query()))
        filter_bar.set_count(len(visible), len(rows))
        layout.addWidget(selector, 1)
        live["widget"] = selector
        QTimer.singleShot(0, lambda: _scroll_saved_target_into_view(selector, live))

    filter_bar.search_input.textChanged.connect(lambda _text="": _render())
    container._ankiscape_render_targets = _render
    _render()
    return container


def short_target_row_label(label: str) -> str:
    """The label without its lock reason, extra catches folded into "+N more".

    A Fishing row keeps its place, because two spots can share their catches
    and differ only there ("... cave eel (Lvl 38) (Mort Myre)").
    """
    name = label.split(_LOCK_SUFFIX)[0]
    first, slash, rest = name.partition("/")
    if not slash:
        return name
    place = rest.rsplit("/", 1)[-1].partition(")")[2]
    return f"{first} +{rest.count('/') + 1} more{place}"


def style_flat_target_list(target_list) -> None:
    from .ui_tab_shop_widgets import WrappedRowDelegate

    target_list.setIconSize(QSize(28, 28))
    target_list.setAlternatingRowColors(True)
    target_list.setStyleSheet(
        f"QListWidget::item {{ min-height: 28px; padding: {_ROW_PADDING}px; }}"
        " QListWidget::item:selected { background: rgba(66,133,244,0.35);"
        " color: palette(text); }"
    )
    # A short row can still outgrow a narrow list, so it wraps instead of
    # hiding its end behind a sideways scroll.
    target_list.setWordWrap(True)
    target_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    target_list.setResizeMode(QListWidget.ResizeMode.Adjust)
    target_list.setItemDelegate(WrappedRowDelegate(target_list, _ROW_PADDING))
