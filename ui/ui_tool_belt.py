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
        QPalette,
        QSize,
        Qt,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps imports safe
    pass

from .ui import dim_text_color, dim_text_css


def _belt_tool_html(tool_name: str, icon_path) -> str:
    # Non-breaking spaces keep an icon and its multi-word name on one line.
    name = escape(tool_name).replace(" ", "&nbsp;")
    if not icon_path:
        return name
    return f'<img src="{escape(icon_path)}" width="18" height="18" align="middle">&nbsp;{name}'


def _belt_groups_widget(belt_groups, item_icon_path) -> "QWidget":
    belt_tools = QWidget()
    belt_tools.setObjectName("toolBeltAlwaysPanel")
    belt_layout = QGridLayout(belt_tools)
    belt_layout.setContentsMargins(8, 0, 8, 8)
    belt_layout.setHorizontalSpacing(10)
    belt_layout.setVerticalSpacing(6)
    belt_layout.setColumnStretch(1, 1)
    for row_index, (group, tool_names) in enumerate(belt_groups):
        group_label = QLabel(group)
        group_label.setStyleSheet("font-weight: 600;")
        tools_label = QLabel(
            " &nbsp; ".join(_belt_tool_html(name, item_icon_path(name)) for name in tool_names)
        )
        tools_label.setObjectName("toolBeltGroupTools")
        tools_label.setTextFormat(Qt.TextFormat.RichText)
        tools_label.setWordWrap(True)
        for column, label in enumerate((group_label, tools_label)):
            label.setToolTip("Always on your tool belt.")
            belt_layout.addWidget(label, row_index, column, Qt.AlignmentFlag.AlignTop)
    return belt_tools


def _gear_item(text: str, marker: str) -> "QListWidgetItem":
    item = QListWidgetItem(text)
    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    item.setData(Qt.ItemDataRole.UserRole, marker)
    return item


def _populate_gear_list(gear_list, gear, make_header_item, item_icon_path) -> None:
    gear_list.clear()
    gear_list.addItem(make_header_item("Toolbelt", "__gear_header__"))
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


def build_bank_tool_belt_panel(gear_rows, make_header_item, item_icon_path):
    """Return the attach hint, the panel, and the callback that repopulates it.

    The panel sits below the striped Bank inventory (the owner wanted it
    "outside the striped window"). The pickaxe and hatchet rows change only
    through the Bank attach action; the belt groups never change.
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

    gear_list = QListWidget()
    gear_list.setObjectName("gearList")
    gear_list.setFrameShape(QFrame.Shape.NoFrame)
    gear_list.setIconSize(QSize(28, 28))
    gear_list.setAlternatingRowColors(False)
    gear_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
    gear_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    gear_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    panel_layout.addWidget(gear_list)
    panel_layout.addWidget(_belt_groups_widget(gear_rows()["belt_groups"], item_icon_path))

    def populate() -> None:
        _populate_gear_list(gear_list, gear_rows(), make_header_item, item_icon_path)

    return hint, panel, populate
