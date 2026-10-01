"""Bank tool belt panel: the attached pickaxe and hatchet, then the 2012 belt."""

from html import escape

try:
    from aqt.qt import (  # type: ignore
        QFrame,
        QGridLayout,
        QIcon,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMenu,
        QPalette,
        QPushButton,
        QSize,
        Qt,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps imports safe
    pass

from . import ui as _ui
from .ui import dim_text_color, dim_text_css

# The panel is an affordance, not a task surface, so a player who has learned
# the belt can fold it away for good; Anki's profile config keeps that choice.
_EXPANDED_CONFIG_KEY = "ankiscape_tool_belt_expanded"
_ON_BELT_TIP = "Always on your tool belt."
_ADDABLE_TIP = "Not on your tool belt yet. Right-click to add it."


def _tool_belt_expanded() -> bool:
    col = getattr(_ui.mw, "col", None)
    return bool(col.get_config(_EXPANDED_CONFIG_KEY, True)) if col else True


def _set_tool_belt_expanded(expanded: bool) -> None:
    col = getattr(_ui.mw, "col", None)
    if col:
        col.set_config(_EXPANDED_CONFIG_KEY, expanded)


def _belt_tool_html(tool_name: str, icon_path, on_belt: bool, dim_css: str) -> str:
    # Non-breaking spaces keep an icon and its multi-word name on one line.
    name = escape(tool_name).replace(" ", "&nbsp;")
    if icon_path:
        name = f'<img src="{escape(icon_path)}" width="18" height="18" align="middle">&nbsp;{name}'
    if on_belt:
        return name
    # A link lets the label report which greyed tool the pointer is over.
    return f'<a href="{escape(tool_name)}" style="color: {dim_css}; text-decoration: none;">{name}</a>'


def _hover_tool(label, tool: str) -> None:
    label.setProperty("hoveredTool", tool)
    label.setToolTip(_ADDABLE_TIP if tool else _ON_BELT_TIP)


def _belt_groups_widget(belt_groups, item_icon_path, show_add_menu):
    belt_tools = QWidget()
    belt_tools.setObjectName("toolBeltAlwaysPanel")
    belt_layout = QGridLayout(belt_tools)
    belt_layout.setContentsMargins(8, 0, 8, 8)
    belt_layout.setHorizontalSpacing(10)
    belt_layout.setVerticalSpacing(6)
    belt_layout.setColumnStretch(1, 1)
    tools_labels = []
    for row_index, (group, _tools) in enumerate(belt_groups):
        group_label = QLabel(group)
        group_label.setStyleSheet("font-weight: 600;")
        group_label.setToolTip(_ON_BELT_TIP)
        tools_label = QLabel()
        tools_label.setObjectName("toolBeltGroupTools")
        tools_label.setTextFormat(Qt.TextFormat.RichText)
        tools_label.setWordWrap(True)
        tools_label.setToolTip(_ON_BELT_TIP)
        tools_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
        tools_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tools_label.linkHovered.connect(lambda tool, label=tools_label: _hover_tool(label, tool))
        tools_label.customContextMenuRequested.connect(
            lambda pos, label=tools_label: show_add_menu(label, pos)
        )
        belt_layout.addWidget(group_label, row_index, 0, Qt.AlignmentFlag.AlignTop)
        belt_layout.addWidget(tools_label, row_index, 1, Qt.AlignmentFlag.AlignTop)
        tools_labels.append(tools_label)

    def populate(groups) -> None:
        dim_css = dim_text_css(belt_tools)
        for tools_label, (_group, tools) in zip(tools_labels, groups):
            tools_label.setText(
                " &nbsp; ".join(
                    _belt_tool_html(name, item_icon_path(name), on_belt, dim_css)
                    for name, on_belt, _refusal in tools
                )
            )

    return belt_tools, populate


def _gear_item(text: str, marker: str) -> "QListWidgetItem":
    item = QListWidgetItem(text)
    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    item.setData(Qt.ItemDataRole.UserRole, marker)
    return item


def _populate_gear_list(gear_list, gear, item_icon_path) -> None:
    gear_list.clear()
    for slot_label, display_name in gear["toolbelt"]:
        row = _gear_item(f"{slot_label}: {display_name}", "__gear__")
        icon_path = item_icon_path(display_name)
        if icon_path:
            row.setIcon(QIcon(icon_path))
        gear_list.addItem(row)
    if not gear["toolbelt"]:
        empty_tb = _gear_item("No pickaxe or hatchet attached.", "__gear_empty__")
        empty_tb.setFlags(Qt.ItemFlag.NoItemFlags)
        gear_list.addItem(empty_tb)
    # Attached upgrades stay visible even while their use level is blocked.
    for slot_label, display_name, skill_label, required_level in gear["toolbelt_blocked"]:
        blocked = _gear_item(f"{display_name} — needs {skill_label} {required_level}", "__gear_blocked__")
        blocked.setToolTip(
            f"This {slot_label.lower()} is attached, but it needs {skill_label} level "
            f"{required_level} before it becomes active."
        )
        blocked.setForeground(dim_text_color(gear_list))
        gear_list.addItem(blocked)

    # Hug contents so the panel is a fixed strip, never its own scroller.
    gear_height = 6
    for row_index in range(gear_list.count()):
        row_height = gear_list.sizeHintForRow(row_index)
        gear_height += row_height if row_height > 0 else 30
    gear_list.setFixedHeight(gear_height)


def build_bank_tool_belt_panel(gear_rows, item_icon_path, on_attach_tool, refresh_views):
    """Return the attach hint, the panel, and the callback that repopulates it.

    The panel sits below the striped Bank inventory (the owner wanted it
    "outside the striped window") and folds from its header. The pickaxe and
    hatchet rows change through the Bank attach action; a greyed quest tool
    changes through its own right-click Add action, which also uses
    ``on_attach_tool`` and then ``refresh_views`` to redraw the Bank.
    """
    hint = QLabel("Right-click a Bank hatchet or pickaxe to attach it to the toolbelt.")
    hint.setObjectName("toolbeltAttachHint")
    hint.setWordWrap(True)
    hint.setStyleSheet(f"color: {dim_text_css(hint)}; font-size: 10px;")

    panel = QFrame()
    panel.setObjectName("toolbeltPanel")
    panel.setFrameShape(QFrame.Shape.StyledPanel)
    panel.setBackgroundRole(QPalette.ColorRole.Base)
    panel.setAutoFillBackground(True)
    panel_layout = QVBoxLayout(panel)
    panel_layout.setContentsMargins(0, 0, 0, 0)
    panel_layout.setSpacing(0)

    header = QPushButton()
    header.setObjectName("toolbeltHeader")
    header.setCheckable(True)
    header.setStyleSheet("QPushButton { text-align: left; font-weight: 600; border: none; padding: 6px 8px; }")
    body = QWidget()
    body_layout = QVBoxLayout(body)
    body_layout.setContentsMargins(0, 0, 0, 0)
    body_layout.setSpacing(0)

    def _show_expanded(expanded: bool) -> None:
        header.setText(f"{'▾' if expanded else '▸'} Toolbelt")
        body.setVisible(expanded)

    def _toggle(expanded: bool) -> None:
        _show_expanded(expanded)
        _set_tool_belt_expanded(expanded)

    header.setChecked(_tool_belt_expanded())
    _show_expanded(header.isChecked())
    header.toggled.connect(_toggle)
    panel_layout.addWidget(header)
    panel_layout.addWidget(body)

    gear_list = QListWidget()
    gear_list.setObjectName("gearList")
    gear_list.setFrameShape(QFrame.Shape.NoFrame)
    gear_list.setIconSize(QSize(28, 28))
    gear_list.setAlternatingRowColors(False)
    gear_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
    gear_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    gear_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    body_layout.addWidget(gear_list)

    refusals: dict = {}

    def _show_add_menu(label, pos) -> None:
        tool = str(label.property("hoveredTool") or "")
        if tool not in refusals:
            return
        refusal = refusals[tool]
        menu = QMenu(label)
        action = menu.addAction(f"Add to tool belt ({refusal})" if refusal else "Add to tool belt")
        action.setObjectName("addToolBeltAction")
        action.setEnabled(not refusal and on_attach_tool is not None)

        def _add(_checked: bool = False) -> None:
            if on_attach_tool(tool):
                refresh_views()

        action.triggered.connect(_add)
        menu.exec(label.mapToGlobal(pos))

    gear = gear_rows()
    belt_tools, populate_belt = _belt_groups_widget(gear["belt_groups"], item_icon_path, _show_add_menu)
    body_layout.addWidget(belt_tools)

    def populate() -> None:
        gear = gear_rows()
        _populate_gear_list(gear_list, gear, item_icon_path)
        populate_belt(gear["belt_groups"])
        refusals.clear()
        refusals.update(
            (name, refusal)
            for _group, tools in gear["belt_groups"]
            for name, on_belt, refusal in tools
            if not on_belt
        )

    return hint, panel, populate
