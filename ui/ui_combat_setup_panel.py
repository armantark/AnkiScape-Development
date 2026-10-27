"""ui_combat_setup_panel.py - the Equipment tab's combat setup column.

The current target and the max hit the next fight rolls against it, then every
setting that fight reads, in sight and grouped: Attack, Prayer, Food and loot,
Presets, Lunar spells. The saved settings and what the next fight gets from
them come from ``combat_setup_panel_view_pure``. Every change goes out through
the ``on_set_*`` callbacks the main menu was given, then ``on_changed``, the
main menu's refresh, re-reads this panel and rebuilds the combat target list,
so no readout lags behind its control. ``build_combat_setup_panel`` returns
the panel with its refresh, which the main menu also runs after gear changes.
"""

try:
    from aqt.qt import (  # type: ignore
        QCheckBox,
        QComboBox,
        QGridLayout,
        QHBoxLayout,
        QInputDialog,
        QLabel,
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
    combat_weapon_style_options_pure,
)
from ..logic_pure.logic_pure_combat_hud import (
    combat_setup_panel_view_pure,
    toggled_combat_prayer_selection_pure,
)
from .ui import _COMBAT_HUB_NAME, current_target_display_name, dim_text_css
from .ui_text_fit import FlowLayout, WrappingCheckBox, side_pair

_LABEL_STYLE = "color: palette(text);"

_UPTIME_CHOICES = (("All fight", "100"), ("70% of the fight", "70"), ("40% of the fight", "40"))


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
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
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
    _add_section_header(layout, "Attack")
    syncs.append(_add_action_row(layout, player_data, then_refresh(on_set_combat_action)))
    syncs.append(_add_style_row(layout, player_data, then_refresh(on_set_combat_style)))
    syncs.append(_add_spell_row(layout, then_refresh(on_set_combat_spell)))
    syncs.append(_add_borrowed_power_row(layout, player_data, send_config))
    syncs.append(_add_prayer_section(layout, player_data, send_config))
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
    header.setStyleSheet("color: palette(text); font-weight: 600; padding-top: 6px;")
    layout.addWidget(header)


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

    def sync(_view) -> None:
        # D2: the options are the equipped weapon's AttackStyleData slots, each
        # labeled with its attack type and the skills it trains; selecting one
        # stores both the weapon_style and the style_type.
        options = combat_weapon_style_options_pure(player_data, EQUIPMENT_ITEM_DATA)
        fixed = len(options) <= 1
        style_combo.setVisible(not fixed)
        fixed_style.setVisible(fixed)
        fixed_style.setText(combat_mode_text(player_data))
        style_combo.blockSignals(True)
        if [style_combo.itemData(i) for i in range(style_combo.count())] != [
            (option["weapon_style"], option["style_type"]) for option in options
        ]:
            style_combo.clear()
            for option in options:
                style_combo.addItem(
                    f"{option['display_name']} — {' + '.join(option['trained_skills'])}",
                    (option["weapon_style"], option["style_type"]),
                )
        current = next((index for index, option in enumerate(options) if option["is_current"]), 0)
        style_combo.setCurrentIndex(current)
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
    layout.addWidget(master)
    status = QLabel()
    status.setObjectName("combatPrayerStatusLabel")
    status.setWordWrap(True)
    status.setStyleSheet("color: palette(text);")
    layout.addWidget(status)
    book_combo = QComboBox()
    book_combo.setObjectName("combatPrayerBookCombo")
    book_combo.addItem("Standard prayers", "standard")
    book_combo.addItem("Ancient Curses", "curses")
    uptime_combo = QComboBox()
    uptime_combo.setObjectName("combatPrayerUptimeCombo")
    for label, value in _UPTIME_CHOICES:
        uptime_combo.addItem(label, value)
    choices = QWidget()
    choices_layout = FlowLayout(choices)
    choices_layout.setContentsMargins(0, 0, 0, 0)
    choices_layout.addWidget(side_pair("Book", book_combo, _LABEL_STYLE))
    choices_layout.addWidget(side_pair("Keep on", uptime_combo, _LABEL_STYLE))
    layout.addWidget(choices)
    hide_lower = QCheckBox("Hide lower-tier prayers")
    hide_lower.setObjectName("combatPrayerHideLowerCheck")
    layout.addWidget(hide_lower)
    sync_grid = _add_prayer_grid(layout, player_data, send_config, hide_lower)
    if send_config is not None:
        master.toggled.connect(lambda enabled: send_config("combat_prayers_enabled", bool(enabled)))
        book_combo.currentIndexChanged.connect(lambda _i: send_config("combat_prayer_book", book_combo.currentData()))
        uptime_combo.currentIndexChanged.connect(lambda _i: send_config("combat_prayer_uptime", uptime_combo.currentData()))

    def sync(view) -> None:
        _set_checked(master, view["prayers_enabled"])
        status.setText(view["prayer_status"])
        book_combo.model().item(book_combo.findData("curses")).setEnabled(view["curses_unlocked"])
        _set_combo_data(book_combo, view["prayer_book"])
        _set_combo_data(uptime_combo, view["prayer_uptime"])
        for widget in (book_combo, uptime_combo, hide_lower):
            widget.setEnabled(view["prayers_enabled"])
        sync_grid(view)

    return sync


def _prayer_check(row) -> "QCheckBox":
    check = WrappingCheckBox(row["label"])
    check.setObjectName(f"combatPrayerCheck::{row['id']}")
    if row["tooltip"]:
        check.setToolTip(row["tooltip"])
    check.setProperty("prayerLevel", row["level"])
    check.setProperty("prayerId", row["id"])
    return check


def _add_prayer_grid(layout, player_data, send_config, hide_lower):
    prayer_grid = QWidget()
    prayer_grid.setObjectName("combatPrayerCheckboxGrid")
    grid_layout = FlowLayout(prayer_grid, fill=True)
    grid_layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(prayer_grid)
    checks = {}
    lower_tier = {"below": 1}

    def _on_toggled(prayer_id: str, checked: bool) -> None:
        if send_config is not None:
            send_config("combat_selected_prayers", toggled_combat_prayer_selection_pure(player_data, prayer_id, checked))

    def _hide_lower(hidden: bool) -> None:
        for check in checks.values():
            check.setVisible(not hidden or int(check.property("prayerLevel") or 1) >= lower_tier["below"])

    hide_lower.toggled.connect(_hide_lower)

    def sync(view) -> None:
        # The book decides which prayers exist, so a book change rebuilds the
        # boxes; otherwise they re-read what the save kept after conflicts.
        if list(checks) != [row["id"] for row in view["prayers"]]:
            _rebuild_prayer_boxes(grid_layout, checks, view["prayers"], _on_toggled)
        lower_tier["below"] = view["lower_tier_below"]
        for row in view["prayers"]:
            check = checks[row["id"]]
            _set_checked(check, row["id"] in view["selected_prayers"])
            check.setEnabled(row["unlocked"] and view["prayers_enabled"])
        _hide_lower(hide_lower.isChecked())

    return sync


def _rebuild_prayer_boxes(grid_layout, checks, rows, on_toggled) -> None:
    for check in checks.values():
        check.setParent(None)
        check.deleteLater()
    checks.clear()
    for row in rows:
        check = _prayer_check(row)
        check.toggled.connect(lambda checked, pid=row["id"]: on_toggled(pid, checked))
        grid_layout.addWidget(check)
        checks[row["id"]] = check


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
    pin_preset = WrappingCheckBox()
    pin_preset.setObjectName("combatPinPresetCheck")
    remember_prayers = WrappingCheckBox()
    remember_prayers.setObjectName("combatOverridePrayersCheck")
    remember_uptime = WrappingCheckBox()
    remember_uptime.setObjectName("combatOverridePrayerUptimeCheck")
    for check in (pin_preset, remember_prayers, remember_uptime):
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
        remember_uptime.toggled.connect(lambda enabled: send_config("target_override", ("combat_prayer_uptime", enabled)))

    def sync(view) -> None:
        target = _target_name(player_data)
        preset_combo.blockSignals(True)
        preset_combo.clear()
        preset_combo.addItems(view["preset_names"])
        preset_combo.setCurrentText(view["active_preset"])
        preset_combo.blockSignals(False)
        for check, text, checked in (
            (pin_preset, f"Always use this preset against {target}", view["preset_pinned"]),
            (remember_prayers, f"Remember these prayers for {target}", view["prayers_overridden"]),
            (remember_uptime, f"Remember this prayer uptime for {target}", view["uptime_overridden"]),
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
