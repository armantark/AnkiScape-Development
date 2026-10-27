"""ui_combat_setup_panel.py - the Equipment tab's combat setup column.

The current target and the max hit the next fight rolls against it, then every
setting that fight reads, in sight and grouped: Prayer, Attack, Food and loot,
Presets, Lunar spells. Prayer comes first because it is the group a player
changes between fights. The saved settings and what the next fight gets from
them come from ``combat_setup_panel_view_pure``. Every change goes out through
the ``on_set_*`` callbacks the main menu was given, then ``on_changed``, the
main menu's refresh, re-reads this panel and rebuilds the combat target list,
so no readout lags behind its control. ``build_combat_setup_panel`` returns
the panel with its refresh, which the main menu also runs after gear changes.
"""

import os

try:
    from aqt.qt import (  # type: ignore
        QCheckBox,
        QComboBox,
        QGridLayout,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLayout,
        QPixmap,
        QPushButton,
        QSizePolicy,
        QSpinBox,
        Qt,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass

from ..core.constants import (
    COMBAT_ATTACK_STYLE_DATA,
    COMBAT_MAGIC_SPELL_DATA,
    DEFAULT_COMBAT_ATTACK_STYLE,
    EQUIPMENT_ITEM_DATA,
)
from ..data.livid_farm_data import BORROWED_POWER_COMBAT_SPELLS
from ..logic.livid_farm_logic import arcane_capacitor_status_pure
from ..logic_pure.logic_pure import (
    combat_attack_style_for_equipment_pure,
    combat_dream_thrift_locked_reasons_pure,
    combat_hud_state_pure,
)
from ..logic_pure.logic_pure_combat_hud import (
    combat_setup_panel_view_pure,
    toggled_combat_prayer_selection_pure,
)
from .ui import _COMBAT_HUB_NAME, current_target_display_name, dim_text_css
from .ui_text_fit import FlowLayout, WrappingCheckBox, on_resize, side_pair

_LABEL_STYLE = "color: palette(text);"

_PRAYER_TIME_CHOICES = (("Whole fight", "100"), ("70% of the fight", "70"), ("40% of the fight", "40"))
_CHECK_MARK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon", "check_mark.svg")


def combat_mode_text(player_data: dict) -> str:
    style_id = combat_attack_style_for_equipment_pure(player_data, EQUIPMENT_ITEM_DATA)
    spec = COMBAT_ATTACK_STYLE_DATA.get(style_id, COMBAT_ATTACK_STYLE_DATA.get(DEFAULT_COMBAT_ATTACK_STYLE, {}))
    return str(spec.get("display_name", style_id)).title()


def build_combat_setup_panel(
    player_data,
    *,
    loot_override_rows,
    item_icon_path,
    on_set_combat_action,
    on_set_combat_style,
    on_set_combat_spell,
    on_set_combat_prayer_config,
    on_set_combat_auto_eat_threshold,
    on_set_loot_threshold,
    on_set_loot_override,
    on_changed=None,
):
    """Return ``(panel, refresh)``; ``refresh`` re-reads every section."""
    panel = QWidget()
    panel.setStyleSheet(_check_box_css(panel))
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    syncs = []

    def refresh() -> None:
        latest = combat_setup_panel_view_pure(player_data, EQUIPMENT_ITEM_DATA)
        for sync in syncs:
            sync(latest)

    def then_refresh(callback):
        """Send one change, then let every readout re-read the save."""
        if callback is None:
            return None

        def send(*args):
            result = callback(*args)
            (on_changed or refresh)()
            return result

        return send

    send_config = then_refresh(on_set_combat_prayer_config)
    syncs.append(_add_target_header(layout, player_data))
    syncs.append(_add_prayer_section(layout, player_data, send_config))
    _add_section_header(layout, "Attack")
    syncs.append(_add_action_row(layout, player_data, then_refresh(on_set_combat_action)))
    syncs.append(_add_style_row(layout, player_data, then_refresh(on_set_combat_style)))
    syncs.append(_add_spell_row(layout, then_refresh(on_set_combat_spell)))
    syncs.append(_add_borrowed_power_row(layout, player_data, send_config))
    syncs.append(_add_food_and_loot(layout, on_set_combat_auto_eat_threshold, send_config, on_set_loot_threshold))
    if loot_override_rows:
        _add_loot_overrides(layout, loot_override_rows, item_icon_path, on_set_loot_override)
    syncs.append(_add_presets(layout, player_data, send_config))
    syncs.append(_add_lunar_spells(layout, player_data, send_config))
    layout.addStretch(1)
    refresh()
    return panel, refresh


def _row(layout, *widgets, grow=-1):
    """One line of widgets; the one at ``grow`` takes the spare width, or the
    line keeps its natural widths when ``grow`` is None."""
    row = QWidget()
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_layout.setSpacing(8)
    grown = None if grow is None else widgets[grow]
    for widget in widgets:
        row_layout.addWidget(widget, 1 if widget is grown else 0)
    if grown is None:
        row_layout.addStretch(1)
    layout.addWidget(row)
    return row


def _text_label(text: str) -> "QLabel":
    label = QLabel(text)
    label.setStyleSheet(_LABEL_STYLE)
    return label


def _add_section_header(layout, text: str) -> None:
    header = QLabel(text)
    header.setStyleSheet("color: palette(text); font-weight: 600; padding-top: 4px;")
    layout.addWidget(header)


def _check_box_css(panel) -> str:
    """Boxes drawn from the theme's text colour, so an empty box keeps its
    outline on a dark base and a disabled label stays readable on a light one.
    A prayer the game picked ticks blue; the player's own choices tick green."""
    dim = dim_text_css(panel)
    readable = dim_text_css(panel, 200)
    faint = dim.rsplit(",", 1)[0] + ", 0.35)"
    mark = _CHECK_MARK.replace(os.sep, "/")
    return (
        f"QCheckBox:disabled {{ color: {readable}; }}"
        f"QCheckBox::indicator {{ width: 13px; height: 13px; border: 1px solid {dim}; border-radius: 3px; background: palette(base); }}"
        f"QCheckBox::indicator:disabled {{ border-color: {faint}; }}"
        f"QCheckBox::indicator:checked {{ border-color: #46b96a; background: #2f8f4e; image: url({mark}); }}"
        "QCheckBox::indicator:checked:disabled { border-color: rgba(70, 185, 106, 0.45); background: rgba(47, 143, 78, 0.45); }"
        'QCheckBox[picked="true"]::indicator:checked { border-color: #5b9be0; background: #2f6fb8; }'
    )


def _set_checked(check, checked: bool) -> None:
    check.blockSignals(True)
    check.setChecked(bool(checked))
    check.blockSignals(False)


def _set_combo_data(combo, value) -> None:
    combo.blockSignals(True)
    combo.setCurrentIndex(max(0, combo.findData(value)))
    combo.blockSignals(False)


def _target_name(player_data) -> str:
    return current_target_display_name(_COMBAT_HUB_NAME, player_data) or "this target"


def _add_target_header(layout, player_data):
    target_label = QLabel()
    target_label.setObjectName("combatCurrentTargetLabel")
    target_label.setStyleSheet("color: palette(text); font-weight: 600;")
    layout.addWidget(target_label)
    max_hit_label = QLabel()
    max_hit_label.setObjectName("combatMaxHitLabel")
    max_hit_label.setWordWrap(True)
    max_hit_label.setStyleSheet("color: palette(text);")
    max_hit_label.setToolTip("Counts your gear, attack style, loaded potions and the prayers below.")
    layout.addWidget(max_hit_label)

    def sync(view) -> None:
        target_label.setText(f"Current target: {_target_name(player_data)}")
        max_hit_label.setText(view["max_hit_text"])

    return sync


def _add_action_row(layout, player_data, on_set_combat_action):
    action_combo = QComboBox()
    action_combo.setObjectName("combatActionCombo")
    action_row = _row(layout, _text_label("Next review"), action_combo)

    def sync(view) -> None:
        hud = combat_hud_state_pure(player_data)
        state = hud["finisher"]
        action_combo.blockSignals(True)
        action_combo.clear()
        action_combo.addItem("Attack", "attack")
        if state["required"]:
            action_combo.addItem(state["action_label"], "finisher")
            finisher_item = action_combo.model().item(1)
            finisher_item.setEnabled(bool(state["available"]))
            finisher_item.setToolTip(hud["finisher_tooltip"])
            if view["finisher_chosen"] and state["available"]:
                action_combo.setCurrentIndex(1)
        action_combo.blockSignals(False)
        action_row.setVisible(bool(state["required"]))

    if on_set_combat_action is not None:
        action_combo.currentIndexChanged.connect(
            lambda _index: on_set_combat_action(str(action_combo.currentData()))
        )
    return sync


def _add_style_row(layout, player_data, on_set_combat_style):
    # The valid styles depend on the equipped weapon's combat class; a magic
    # weapon has one fixed style, so the row names it instead of offering a
    # choice. The combo is rebuilt only when the weapon changes its options.
    style_combo = QComboBox()
    style_combo.setObjectName("combatStyleCombo")
    fixed_style = QLabel()
    fixed_style.setObjectName("combatFixedStyleLabel")
    fixed_style.setStyleSheet(_LABEL_STYLE)
    fixed_style.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    _row(layout, _text_label("Attack style"), style_combo, fixed_style, grow=1)

    style_combo.setToolTip("Every style also trains Constitution.")

    def sync(view) -> None:
        # D2: the options are the equipped weapon's AttackStyleData slots;
        # selecting one stores both the weapon_style and the style_type.
        styles = view["styles"]
        fixed = len(styles) <= 1
        style_combo.setVisible(not fixed)
        fixed_style.setVisible(fixed)
        fixed_style.setText(combat_mode_text(player_data))
        style_combo.blockSignals(True)
        if [style_combo.itemData(i) for i in range(style_combo.count())] != [style["data"] for style in styles]:
            style_combo.clear()
            for style in styles:
                style_combo.addItem(style["label"], style["data"])
        style_combo.setCurrentIndex(next((index for index, style in enumerate(styles) if style["current"]), 0))
        style_combo.blockSignals(False)

    if on_set_combat_style is not None:
        style_combo.currentIndexChanged.connect(lambda _index: on_set_combat_style(style_combo.currentData()))
    return sync


def _add_spell_row(layout, on_set_combat_spell):
    spell_combo = QComboBox()
    spell_combo.setObjectName("combatSpellCombo")
    spell_row = _row(layout, _text_label("Autocast"), spell_combo)

    def sync(view) -> None:
        spell_combo.blockSignals(True)
        spell_combo.clear()
        for spell in view["spells"]:
            spell_combo.addItem(spell["name"], spell["id"])
            spell_combo.model().item(spell_combo.count() - 1).setEnabled(spell["unlocked"])
        spell_combo.setCurrentIndex(max(0, spell_combo.findData(view["autocast_spell"])))
        spell_combo.blockSignals(False)
        spell_row.setVisible(view["magic_mode"])

    if on_set_combat_spell is not None:
        spell_combo.currentIndexChanged.connect(lambda _index: on_set_combat_spell(spell_combo.currentData()))
    return sync


def _add_borrowed_power_row(layout, player_data, send_config):
    borrowed_row = QWidget()
    borrowed_row.setObjectName("combatBorrowedPowerRow")
    borrowed_layout = QVBoxLayout(borrowed_row)
    borrowed_layout.setContentsMargins(0, 0, 0, 0)
    borrowed_layout.setSpacing(4)
    borrowed_name = QLabel()
    borrowed_name.setObjectName("combatBorrowedPowerSpell")
    borrowed_name.setStyleSheet("color: palette(text);")
    borrowed_layout.addWidget(borrowed_name)
    borrowed_button = QPushButton()
    borrowed_button.setObjectName("combatBorrowedPowerButton")
    borrowed_button.setCheckable(True)
    borrowed_button.setToolTip(
        "The next Combat review performs one manual Borrowed Power cast, "
        "then returns to the selected autocast."
    )
    borrowed_layout.addWidget(borrowed_button)
    layout.addWidget(borrowed_row)
    borrowed_spell_ref = {"id": ""}

    def _set_armed(checked: bool) -> None:
        if send_config is not None:
            send_config("combat_borrowed_power_spell", borrowed_spell_ref["id"] if checked else "")

    borrowed_button.clicked.connect(_set_armed)

    def sync(view) -> None:
        current = arcane_capacitor_status_pure(player_data)
        spell_id = str(current["spell_id"])
        borrowed_spell_ref["id"] = spell_id
        spell_name = str(COMBAT_MAGIC_SPELL_DATA.get(spell_id, {}).get("display_name", spell_id))
        charges = int(current["charges"])
        borrowed_name.setText(f"Borrowed Power · {spell_name} · {charges:,} charges")
        borrowed_name.setToolTip(f"{charges:,} Arcane capacitor charges remaining.")
        visible = bool(current["equipped"] and spell_id in BORROWED_POWER_COMBAT_SPELLS and view["magic_mode"])
        armed = bool(visible and view["borrowed_power_spell"] == spell_id)
        _set_checked(borrowed_button, armed)
        borrowed_button.setText("One cast armed" if armed else "Cast once next review")
        borrowed_button.setEnabled(visible and send_config is not None)
        borrowed_row.setVisible(visible)

    return sync


def _add_prayer_section(layout, player_data, send_config):
    _add_section_header(layout, "Prayer")
    master = QCheckBox("Use prayers in fights")
    master.setObjectName("combatPrayerMasterCheck")
    book_combo = QComboBox()
    book_combo.setObjectName("combatPrayerBookCombo")
    book_combo.addItem("Standard prayers", "standard")
    book_combo.addItem("Ancient Curses", "curses")
    time_combo = QComboBox()
    time_combo.setObjectName("combatPrayerUptimeCombo")
    for label, value in _PRAYER_TIME_CHOICES:
        time_combo.addItem(label, value)
    hide_lower = QCheckBox("Hide lower-tier prayers")
    hide_lower.setObjectName("combatPrayerHideLowerCheck")
    auto_pick = QPushButton("Pick the best for me")
    auto_pick.setObjectName("combatPrayerAutoPickButton")
    choices = QWidget()
    choices_layout = FlowLayout(choices)
    choices_layout.setContentsMargins(0, 0, 0, 0)
    for widget in (
        master,
        side_pair("Book", book_combo, _LABEL_STYLE),
        side_pair("Prayer time", time_combo, _LABEL_STYLE),
        auto_pick,
    ):
        choices_layout.addWidget(widget)
    layout.addWidget(choices)
    status = QLabel()
    status.setObjectName("combatPrayerStatusLabel")
    status.setWordWrap(True)
    status.setStyleSheet(_LABEL_STYLE)
    layout.addWidget(status)
    sync_grid = _add_prayer_grid(layout, player_data, send_config, hide_lower)
    layout.addWidget(hide_lower)
    locked = QLabel()
    locked.setObjectName("combatLockedPrayersLabel")
    locked.setWordWrap(True)
    locked.setStyleSheet(f"color: {dim_text_css(locked, 200)};")
    layout.addWidget(locked)
    if send_config is not None:
        master.toggled.connect(lambda enabled: send_config("combat_prayers_enabled", bool(enabled)))
        book_combo.currentIndexChanged.connect(lambda _i: send_config("combat_prayer_book", book_combo.currentData()))
        time_combo.currentIndexChanged.connect(lambda _i: send_config("combat_prayer_uptime", time_combo.currentData()))
        auto_pick.clicked.connect(lambda _checked=False: send_config("combat_selected_prayers", []))

    def sync(view) -> None:
        _set_checked(master, view["prayers_enabled"])
        status.setText(view["prayer_status"])
        book_combo.model().item(book_combo.findData("curses")).setEnabled(view["curses_unlocked"])
        _set_combo_data(book_combo, view["prayer_book"])
        _set_combo_data(time_combo, view["prayer_uptime"])
        for widget in (book_combo, time_combo, hide_lower):
            widget.setEnabled(view["prayers_enabled"])
        auto_pick.setEnabled(view["prayers_enabled"] and not view["prayers_picked"] and send_config is not None)
        sync_grid(view)
        locked.setText(view["locked_prayers_text"])
        locked.setVisible(bool(view["locked_prayers_text"]))

    return sync


def _prayer_check(row) -> "QCheckBox":
    # One line each, so every row of the grid is the same height.
    check = QCheckBox(row["label"])
    check.setObjectName(f"combatPrayerCheck::{row['id']}")
    check.setToolTip(row["tooltip"])
    check.setProperty("prayerLevel", row["level"])
    check.setProperty("prayerId", row["id"])
    return check


_PRAYER_COLUMNS = 3


def _add_prayer_grid(layout, player_data, send_config, hide_lower):
    grid = _PrayerGrid(player_data, send_config, hide_lower)
    layout.addWidget(grid.widget)
    return grid.sync


class _PrayerGrid:
    """The prayer boxes on one line each, in two or three equal columns as the
    width allows, so they line up in even rows; hidden boxes give up their
    cells. The grid asks only for two columns' width, so the column can still
    narrow from three columns to two."""

    def __init__(self, player_data, send_config, hide_lower):
        self._player_data = player_data
        self._send_config = send_config
        self._hide_lower = hide_lower
        self.widget = QWidget()
        self.widget.setObjectName("combatPrayerCheckboxGrid")
        self._layout = QGridLayout(self.widget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setHorizontalSpacing(12)
        self._layout.setVerticalSpacing(4)
        self._layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self._column_width = 1
        self._checks = {}
        self._lower_tier_below = 1
        self._placed = None
        hide_lower.toggled.connect(lambda _hidden: self._show_tiers())
        on_resize(self.widget, self._place)

    def sync(self, view) -> None:
        # The book decides which prayers exist, so a book change rebuilds the
        # boxes; otherwise they re-read what the save kept after conflicts.
        if list(self._checks) != [row["id"] for row in view["prayers"]]:
            self._rebuild(view["prayers"])
        self._lower_tier_below = view["lower_tier_below"]
        for row in view["prayers"]:
            check = self._checks[row["id"]]
            _set_checked(check, row["id"] in view["selected_prayers"])
            check.setEnabled(view["prayers_enabled"])
            if check.property("picked") != view["prayers_picked"]:
                check.setProperty("picked", view["prayers_picked"])
                check.style().unpolish(check)
                check.style().polish(check)
        self._show_tiers()

    def _rebuild(self, rows) -> None:
        for check in self._checks.values():
            check.setParent(None)
            check.deleteLater()
        self._checks.clear()
        for row in rows:
            check = _prayer_check(row)
            check.setParent(self.widget)
            check.toggled.connect(lambda checked, pid=row["id"]: self._toggled(pid, checked))
            self._checks[row["id"]] = check
        spacing = self._layout.horizontalSpacing()
        self._column_width = max((check.sizeHint().width() for check in self._checks.values()), default=1) + spacing
        self.widget.setMinimumWidth(min(2, len(rows)) * self._column_width - spacing)
        self._placed = None

    def _toggled(self, prayer_id: str, checked: bool) -> None:
        if self._send_config is not None:
            self._send_config(
                "combat_selected_prayers",
                toggled_combat_prayer_selection_pure(self._player_data, prayer_id, checked),
            )

    def _show_tiers(self) -> None:
        hidden = self._hide_lower.isChecked()
        for check in self._checks.values():
            check.setVisible(not hidden or int(check.property("prayerLevel") or 1) >= self._lower_tier_below)
        self._place()

    def _place(self) -> None:
        shown = [check for check in self._checks.values() if not check.isHidden()]
        columns = max(min(2, len(shown)) or 1, min(_PRAYER_COLUMNS, self.widget.width() // self._column_width))
        key = (columns, tuple(id(check) for check in shown))
        if key == self._placed:
            return
        self._placed = key
        while self._layout.count():
            self._layout.takeAt(0)
        for index, check in enumerate(shown):
            self._layout.addWidget(check, index // columns, index % columns)
        for column in range(_PRAYER_COLUMNS):
            self._layout.setColumnStretch(column, 1 if column < columns else 0)


def _add_food_and_loot(layout, on_set_auto_eat, send_config, on_set_loot_threshold):
    _add_section_header(layout, "Food and loot")
    auto_eat = QSpinBox()
    auto_eat.setObjectName("combatAutoEatThresholdSpin")
    auto_eat.setRange(1, 99)
    auto_eat.setSuffix("% life points")
    _row(layout, _text_label("Auto-eat at"), auto_eat)
    auto_bury = WrappingCheckBox("Auto-bury bones and scatter ashes (costs simulated ticks)")
    auto_bury.setObjectName("combatAutoPrayerTrainingCheck")
    layout.addWidget(auto_bury)
    loot_spin = QSpinBox()
    loot_spin.setObjectName("combatLootThresholdSpin")
    loot_spin.setRange(0, 100000)
    loot_spin.setSingleStep(5)
    loot_spin.setSuffix(" coins")
    _row(layout, _text_label("Leave loot worth under"), loot_spin)
    if on_set_auto_eat is not None:
        auto_eat.valueChanged.connect(lambda value: on_set_auto_eat(value))
    if send_config is not None:
        auto_bury.toggled.connect(lambda checked: send_config("combat_auto_prayer_training", bool(checked)))
    if on_set_loot_threshold is not None:
        loot_spin.valueChanged.connect(lambda value: on_set_loot_threshold(int(value)))

    def sync(view) -> None:
        for spin, value in ((auto_eat, view["auto_eat_threshold"]), (loot_spin, view["loot_threshold"])):
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)
        _set_checked(auto_bury, view["auto_prayer_training"])

    return sync


def _add_presets(layout, player_data, send_config):
    _add_section_header(layout, "Presets")
    preset_combo = QComboBox()
    preset_combo.setObjectName("combatPresetCombo")
    save_preset = QPushButton("Save as new preset…")
    save_preset.setObjectName("combatSavePresetButton")
    _row(layout, _text_label("Preset"), preset_combo, save_preset, grow=1)
    # COMBAT_PRESET_FIELDS, in the words of this column and the carried pack.
    saves = QLabel(
        "A preset saves your prayers, prayer time, auto-eat, auto-bury, autocast, "
        "Lunar spells and supply mode. Attack style and loot stay as they are."
    )
    saves.setWordWrap(True)
    saves.setStyleSheet(f"color: {dim_text_css(saves)};")
    layout.addWidget(saves)
    summary = QLabel()
    summary.setObjectName("combatTargetSummaryLabel")
    summary.setWordWrap(True)
    summary.setStyleSheet("color: palette(text); font-weight: 600;")
    layout.addWidget(summary)
    pin_preset = WrappingCheckBox()
    pin_preset.setObjectName("combatPinPresetCheck")
    remember_prayers = WrappingCheckBox()
    remember_prayers.setObjectName("combatOverridePrayersCheck")
    remember_time = WrappingCheckBox()
    remember_time.setObjectName("combatOverridePrayerUptimeCheck")
    for check in (pin_preset, remember_prayers, remember_time):
        layout.addWidget(check)
    if send_config is not None:
        preset_combo.currentTextChanged.connect(lambda name: send_config("apply_preset", name))

        def _save_current_preset() -> None:
            name, accepted = QInputDialog.getText(save_preset, "Save combat preset", "Preset name")
            if accepted and name.strip():
                send_config("save_preset", name.strip())

        save_preset.clicked.connect(_save_current_preset)
        pin_preset.toggled.connect(lambda enabled: send_config("pin_target_preset", enabled))
        remember_prayers.toggled.connect(lambda enabled: send_config("target_override", ("combat_selected_prayers", enabled)))
        remember_time.toggled.connect(lambda enabled: send_config("target_override", ("combat_prayer_uptime", enabled)))

    def sync(view) -> None:
        preset_combo.blockSignals(True)
        preset_combo.clear()
        preset_combo.addItems(view["preset_names"])
        preset_combo.setCurrentText(view["active_preset"])
        preset_combo.blockSignals(False)
        target = _target_name(player_data)
        summary.setText(view["target_summary"])
        for check, text, checked in (
            (pin_preset, f"Switch to preset “{view['pinned_preset'] or view['active_preset']}” whenever I fight {target}", bool(view["pinned_preset"])),
            (remember_prayers, f"Keep the prayers ticked now for {target}, whatever I tick for other targets", view["prayers_overridden"]),
            (remember_time, f"Keep this prayer time for {target}, whatever I choose for other targets", view["uptime_overridden"]),
        ):
            check.setText(text)
            _set_checked(check, checked)

    return sync


def _add_lunar_spells(layout, player_data, send_config):
    _add_section_header(layout, "Lunar spells")
    vengeance = QCheckBox("Vengeance")
    vengeance.setObjectName("combatVengeanceCheck")
    dream_thrift = QCheckBox("Dream thrift")
    dream_thrift.setObjectName("combatDreamThriftCheck")
    _row(layout, vengeance, dream_thrift, grow=None)
    swap_combo = QComboBox()
    swap_combo.setObjectName("combatSpellbookSwapCombo")
    _row(layout, _text_label("Spellbook Swap"), swap_combo)
    dream_reasons = combat_dream_thrift_locked_reasons_pure(player_data)
    dream_thrift.setEnabled(send_config is not None and not dream_reasons)
    if dream_reasons:
        dream_thrift.setToolTip(f"Requires {dream_reasons[0]}.")
    if send_config is not None:
        vengeance.toggled.connect(lambda enabled: send_config("combat_vengeance", bool(enabled)))
        dream_thrift.toggled.connect(lambda enabled: send_config("combat_dream_thrift", bool(enabled)))
        swap_combo.currentIndexChanged.connect(
            lambda _i: send_config("combat_spellbook_swap", str(swap_combo.currentData() or ""))
        )

    def sync(view) -> None:
        _set_checked(vengeance, view["vengeance"])
        _set_checked(dream_thrift, view["dream_thrift"])
        swap_combo.blockSignals(True)
        swap_combo.clear()
        for label, value in (
            ("No Spellbook Swap", ""),
            ("Swap autocast", str(view["autocast_spell"])),
            ("Swap Vengeance", "vengeance"),
            ("Swap Dream", "dream"),
        ):
            swap_combo.addItem(label, value)
        swap_combo.setCurrentIndex(max(0, swap_combo.findData(view["spellbook_swap"])))
        swap_combo.blockSignals(False)

    return sync


_LOOT_MODES = ("auto", "keep", "leave")
_LOOT_GRID_COLS = 2


def _loot_override_cells(loot_override_rows) -> list:
    """(item, mode) per named drop; an unknown mode follows the value threshold."""
    cells = []
    for row in loot_override_rows:
        item_name = str(row.get("item", ""))
        mode = str(row.get("mode", "auto"))
        if item_name:
            cells.append((item_name, mode if mode in _LOOT_MODES else "auto"))
    return cells


def _add_loot_overrides(layout, loot_override_rows, item_icon_path, on_set_loot_override) -> None:
    # The default view is coarse: a value threshold plus a single "keep
    # everything" toggle. Per-drop overrides are opt-in, rendered as icon cells
    # with a binary Keep | Drop pill (neither segment lit = follow the value
    # threshold).
    cells = _loot_override_cells(loot_override_rows)
    loot_cell_state: dict = {}
    loot_pill_refreshers: dict = {}

    def _choose(item_name: str, mode: str) -> None:
        loot_cell_state[item_name] = mode
        loot_pill_refreshers[item_name](mode)
        if on_set_loot_override is not None:
            on_set_loot_override(item_name, mode)

    keep_all_check = QCheckBox("Keep every drop from this enemy")
    keep_all_check.setObjectName("combatLootKeepAllCheck")

    def _sync_keep_all() -> None:
        all_keep = bool(cells) and all(loot_cell_state.get(name) == "keep" for name, _mode in cells)
        _set_checked(keep_all_check, all_keep)

    def _on_keep_all(checked: bool) -> None:
        for name, _mode in cells:
            _choose(name, "keep" if checked else "auto")

    keep_all_check.toggled.connect(_on_keep_all)
    layout.addWidget(keep_all_check)

    loot_adv_check = QCheckBox("Keep or drop specific drops")
    loot_adv_check.setObjectName("combatLootAdvancedCheck")
    layout.addWidget(loot_adv_check)

    loot_grid_container = QWidget()
    loot_grid_container.setObjectName("combatLootOverrideGrid")
    loot_grid_layout = QGridLayout(loot_grid_container)
    loot_grid_layout.setContentsMargins(0, 2, 0, 2)
    loot_grid_layout.setSpacing(6)

    def _toggle_loot_mode(name: str, mode: str) -> None:
        _choose(name, "auto" if loot_cell_state.get(name) == mode else mode)
        _sync_keep_all()

    for cell_idx, (item_name, mode) in enumerate(cells):
        cell, refresh_pill = _loot_cell(
            loot_grid_container,
            cell_idx,
            item_name,
            item_icon_path(item_name),
            enabled=on_set_loot_override is not None,
            on_click=_toggle_loot_mode,
        )
        loot_pill_refreshers[item_name] = refresh_pill
        loot_cell_state[item_name] = mode
        refresh_pill(mode)
        loot_grid_layout.addWidget(cell, cell_idx // _LOOT_GRID_COLS, cell_idx % _LOOT_GRID_COLS)

    loot_grid_container.setVisible(False)
    loot_adv_check.toggled.connect(lambda checked: loot_grid_container.setVisible(bool(checked)))
    layout.addWidget(loot_grid_container)
    _sync_keep_all()


# Each drop gets a joined two-segment pill — Keep | Drop. Neither segment lit
# means "Auto": that drop follows the "Leave loot worth under" threshold.
# Clicking a lit segment again clears back to Auto, so the binary switch still
# reaches all three backend modes the engine understands (auto / keep / leave).
def _loot_segment_css(container, side: str, active: bool, accent: str) -> str:
    radius = (
        "border-top-left-radius:6px;border-bottom-left-radius:6px;border-right:none;"
        if side == "left"
        else "border-top-right-radius:6px;border-bottom-right-radius:6px;"
    )
    if active:
        face = f"background:{accent};color:palette(text);font-weight:600;"
    else:
        face = f"background:transparent;color:{dim_text_css(container)};"
    return (
        f"QPushButton{{border:1px solid palette(mid);{radius}"
        f"padding:2px 12px;font-size:11px;{face}}}"
    )


def _loot_cell(container, cell_idx, item_name, icon_path, *, enabled, on_click):
    cell = QWidget()
    cell.setObjectName(f"combatLootCell{cell_idx}")
    cell_layout = QHBoxLayout(cell)
    cell_layout.setContentsMargins(2, 2, 2, 2)
    cell_layout.setSpacing(8)
    icon_label = QLabel()
    if icon_path:
        icon_label.setPixmap(QPixmap(icon_path).scaled(22, 22, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    icon_label.setFixedWidth(24)
    name_label = QLabel(item_name)
    name_label.setStyleSheet("color: palette(text); font-size: 11px;")
    keep_btn = QPushButton("Keep")
    keep_btn.setObjectName(f"lootOverrideKeep::{item_name}")
    keep_btn.setFixedHeight(24)
    drop_btn = QPushButton("Drop")
    drop_btn.setObjectName(f"lootOverrideDrop::{item_name}")
    drop_btn.setFixedHeight(24)
    keep_btn.setEnabled(enabled)
    drop_btn.setEnabled(enabled)

    def refresh_pill(new_mode: str) -> None:
        keep_btn.setStyleSheet(_loot_segment_css(container, "left", new_mode == "keep", "rgba(76,175,80,0.35)"))
        drop_btn.setStyleSheet(_loot_segment_css(container, "right", new_mode == "leave", "rgba(192,69,59,0.35)"))

    keep_btn.clicked.connect(lambda _c=False: on_click(item_name, "keep"))
    drop_btn.clicked.connect(lambda _c=False: on_click(item_name, "leave"))
    pill = QWidget()
    pill_layout = QHBoxLayout(pill)
    pill_layout.setContentsMargins(0, 0, 0, 0)
    pill_layout.setSpacing(0)
    pill_layout.addWidget(keep_btn)
    pill_layout.addWidget(drop_btn)
    cell_layout.addWidget(icon_label)
    cell_layout.addWidget(name_label, 1)
    cell_layout.addWidget(pill)
    return cell, refresh_pill
