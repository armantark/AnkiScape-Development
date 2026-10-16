"""The Prayer skill panel: the selected method's line, then the target list.

``prayer_panel_view_pure`` owns what the panel says and whether the gilded
altar mode box shows; this module only draws it.
"""

try:
    from aqt.qt import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget  # type: ignore
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass

from ..core.constants import DEFAULT_PRAYER_TARGET, PRAYER_DATA, PRAYER_GROUP_ORDER, PRAYER_ITEM_IMAGES
from ..core.target_metadata import prayer_target_rows
from ..data.prayer_data import prayer_selection_from_target_pure
from ..logic_pure.logic_pure_prayer import prayer_panel_view_pure


def _gilded_mode_row(view: dict, apply_selection) -> "QHBoxLayout":
    row = QHBoxLayout()
    label = QLabel("Gilded altar mode")
    label.setObjectName("prayerGildedModeLabel")
    row.addWidget(label)
    mode = QComboBox()
    mode.setObjectName("prayerGildedModeCombo")
    for index, (mode_id, text, reasons) in enumerate(view["gilded_mode_options"]):
        mode.addItem(text, mode_id)
        item = mode.model().item(index)
        item.setEnabled(not reasons)
        if reasons:
            item.setToolTip("Locked due to: " + ", ".join(reasons))
    mode.setCurrentIndex(mode.findData(view["gilded_mode"]))

    def _on_mode_changed(_index: int) -> None:
        ui_method = "gilded_owned" if mode.currentData() == "owned" else "gilded_hosted"
        if not apply_selection(view["material_id"], ui_method):
            mode.blockSignals(True)
            mode.setCurrentIndex(mode.findData(view["gilded_mode"]))
            mode.blockSignals(False)

    mode.currentIndexChanged.connect(_on_mode_changed)
    row.addWidget(mode, 1)
    return row


def build_prayer_panel(player_data, searchable_selector, on_set_prayer_selection, render_panel) -> "QWidget":
    """Return the Prayer panel; a successful selection redraws it through ``render_panel``.

    ``searchable_selector(rows, **options)`` draws the shared Skills target
    search; the caller passes it in so this module imports no other UI module.
    """
    view = prayer_panel_view_pure(player_data, PRAYER_DATA)
    panel = QWidget()
    panel.setObjectName("prayerSkillPanel")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)

    def _apply_selection(material_id: str, ui_method: str) -> bool:
        if on_set_prayer_selection is None or not on_set_prayer_selection(material_id, ui_method):
            return False
        render_panel()
        return True

    def _select_target(target_id: str) -> None:
        selection = prayer_selection_from_target_pure(target_id, view["gilded_mode"])
        if selection is not None:
            _apply_selection(*selection)

    status = QLabel(view["status"])
    status.setObjectName("prayerMethodStatus")
    status.setWordWrap(True)
    layout.addWidget(status)
    if view["show_gilded_mode"]:
        layout.addLayout(_gilded_mode_row(view, _apply_selection))
    layout.addWidget(searchable_selector(
        prayer_target_rows(player_data, PRAYER_DATA, PRAYER_ITEM_IMAGES, DEFAULT_PRAYER_TARGET),
        key="prayer",
        noun="bones and ashes",
        group_labels={group: group for group in PRAYER_GROUP_ORDER},
        group_role_prefix="__prayer_group__:",
        on_select=_select_target,
        group_order=list(PRAYER_GROUP_ORDER),
    ), 1)
    return panel
