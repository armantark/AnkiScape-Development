"""ui_combat_setup_panel.py - the Equipment tab's combat setup column.

Everything from "Combat mode" to "Current target": the next-review action,
attack style, autocast, Borrowed Power, the prayer and auto-eat toggles, the
advanced preset editor, and the loot rules. The saved settings and unlocks it
draws come from ``combat_setup_panel_view_pure``; every change goes out through
the ``on_set_*`` callbacks the main menu was given. ``build_combat_setup_panel``
returns the panel with the refresh the main menu runs after gear changes.
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
        QSpinBox,
        Qt,
        QToolButton,
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
):
    """Return ``(panel, refresh)``; ``refresh`` re-reads the gear-dependent rows."""
    view = combat_setup_panel_view_pure(player_data)
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)

    mode_label = QLabel(f"Combat mode: {combat_mode_text(player_data)}")
    mode_label.setObjectName("combatModeLabel")
    mode_label.setStyleSheet("color: palette(text); font-weight: 600;")
    layout.addWidget(mode_label)

    refresh_action = _add_action_row(layout, player_data, view, on_set_combat_action)
    rebuild_style_combo = _add_style_row(layout, player_data, on_set_combat_style)
    _add_spell_row(layout, player_data, view, on_set_combat_spell)
    refresh_borrowed_power = _add_borrowed_power_row(layout, player_data, view, on_set_combat_prayer_config)

    # The casual "Auto-bury bones" box and the advanced editor's
    # "Auto-bury/scatter" box are one setting, so ticking either ticks both.
    auto_prayer_checks = []

    def _set_auto_prayer_training(checked: bool) -> None:
        for check in auto_prayer_checks:
            check.blockSignals(True)
            check.setChecked(bool(checked))
            check.blockSignals(False)
        if on_set_combat_prayer_config is not None:
            on_set_combat_prayer_config(
                "combat_auto_prayer_training", bool(checked)
            )

    def _auto_prayer_check(text: str, object_name: str) -> "QCheckBox":
        check = QCheckBox(text)
        check.setObjectName(object_name)
        check.setChecked(view["auto_prayer_training"])
        check.toggled.connect(_set_auto_prayer_training)
        auto_prayer_checks.append(check)
        return check

    _add_casual_toggles(layout, player_data, view, on_set_combat_prayer_config, _auto_prayer_check)
    _add_auto_eat_row(layout, view, on_set_combat_auto_eat_threshold)
    _add_advanced_editor(layout, player_data, view, on_set_combat_prayer_config, _auto_prayer_check)
    _add_loot_rules(
        layout,
        view,
        loot_override_rows,
        item_icon_path,
        on_set_loot_threshold,
        on_set_loot_override,
    )

    current_target_label = QLabel(
        f"Current target: {current_target_display_name(_COMBAT_HUB_NAME, player_data)}"
    )
    current_target_label.setObjectName("combatCurrentTargetLabel")
    current_target_label.setStyleSheet(
        "color: palette(text); font-weight: 600; padding-top: 2px;"
    )
    layout.addWidget(current_target_label)

    def refresh() -> None:
        fresh_view = combat_setup_panel_view_pure(player_data)
        mode_label.setText(f"Combat mode: {combat_mode_text(player_data)}")
        rebuild_style_combo()
        refresh_action(fresh_view)
        refresh_borrowed_power(fresh_view)
        current_target_label.setText(
            f"Current target: {current_target_display_name(_COMBAT_HUB_NAME, player_data)}"
        )

    layout.addStretch(1)
    return panel, refresh


def _add_action_row(layout, player_data, view, on_set_combat_action):
    action_row = QWidget()
    action_row_layout = QHBoxLayout(action_row)
    action_row_layout.setContentsMargins(0, 0, 0, 0)
    action_row_layout.setSpacing(8)
    action_row_layout.addWidget(QLabel("Next review"))
    action_combo = QComboBox()
    action_combo.setObjectName("combatActionCombo")
    action_row_layout.addWidget(action_combo, 1)
    layout.addWidget(action_row)

    def refresh(latest) -> None:
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
            if latest["finisher_chosen"] and state["available"]:
                action_combo.setCurrentIndex(1)
        action_combo.blockSignals(False)
        action_row.setVisible(bool(state["required"]))

    if on_set_combat_action is not None:
        action_combo.currentIndexChanged.connect(
            lambda _index: on_set_combat_action(
                str(action_combo.currentData())
            )
        )
    refresh(view)
    return refresh


def _add_style_row(layout, player_data, on_set_combat_style):
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
    style_combo_ref = {"combo": None}

    def rebuild() -> None:
        # D2: the options are the equipped weapon's actual AttackStyleData slots,
        # each labeled with its attack type (stab/slash/crush). Selecting a row
        # stores both the weapon_style and the style_type, so parity keys off the
        # exact slot the player picked.
        options = combat_weapon_style_options_pure(player_data, EQUIPMENT_ITEM_DATA)
        old = style_combo_ref["combo"]
        if old is not None:
            old.setParent(None)
            old.deleteLater()
            style_combo_ref["combo"] = None
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
        style_combo_ref["combo"] = combo
        style_row.setVisible(True)

    rebuild()
    return rebuild


def _add_spell_row(layout, player_data, view, on_set_combat_spell) -> None:
    spell_row = QWidget()
    spell_layout = QHBoxLayout(spell_row)
    spell_layout.setContentsMargins(0, 0, 0, 0)
    spell_layout.setSpacing(8)
    spell_label = QLabel("Autocast")
    spell_label.setStyleSheet("color: palette(text);")
    spell_combo = QComboBox()
    spell_combo.setObjectName("combatSpellCombo")
    selected_spell_index = 0
    for spell in view["spells"]:
        spell_combo.addItem(spell["name"], spell["id"])
        spell_index = spell_combo.count() - 1
        spell_combo.model().item(spell_index).setEnabled(spell["unlocked"])
        if spell["id"] == view["autocast_spell"]:
            selected_spell_index = spell_index
    spell_combo.setCurrentIndex(selected_spell_index)
    if on_set_combat_spell is not None:
        spell_combo.currentIndexChanged.connect(
            lambda _index: on_set_combat_spell(
                spell_combo.currentData()
            )
        )
    spell_layout.addWidget(spell_label)
    spell_layout.addWidget(spell_combo, 1)
    layout.addWidget(spell_row)
    spell_row.setVisible(combat_mode_text(player_data).lower().startswith("magic"))


def _add_borrowed_power_row(layout, player_data, view, on_set_combat_prayer_config):
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
        spell_id = borrowed_spell_ref["id"]
        if on_set_combat_prayer_config is not None:
            on_set_combat_prayer_config(
                "combat_borrowed_power_spell",
                spell_id if checked else "",
            )
        borrowed_button.setText(
            "One cast armed"
            if checked
            else "Cast once next review"
        )

    borrowed_button.clicked.connect(_set_armed)

    def refresh(latest) -> None:
        current = arcane_capacitor_status_pure(player_data)
        spell_id = str(current["spell_id"])
        borrowed_spell_ref["id"] = spell_id
        spell_name = str(
            COMBAT_MAGIC_SPELL_DATA.get(
                spell_id,
                {},
            ).get("display_name", spell_id)
        )
        charges = int(current["charges"])
        borrowed_name.setText(
            f"Borrowed Power · {spell_name} · {charges:,} charges"
        )
        borrowed_name.setToolTip(
            f"{charges:,} Arcane capacitor charges remaining."
        )
        visible = bool(
            current["equipped"]
            and spell_id in BORROWED_POWER_COMBAT_SPELLS
            and combat_mode_text(player_data).lower().startswith("magic")
        )
        armed = bool(visible and latest["borrowed_power_spell"] == spell_id)
        borrowed_button.blockSignals(True)
        borrowed_button.setChecked(armed)
        borrowed_button.setText(
            "One cast armed"
            if armed
            else "Cast once next review"
        )
        borrowed_button.setEnabled(
            visible and on_set_combat_prayer_config is not None
        )
        borrowed_button.blockSignals(False)
        borrowed_row.setVisible(visible)

    refresh(view)
    return refresh


def _add_casual_toggles(layout, player_data, view, on_set_combat_prayer_config, auto_prayer_check) -> None:
    casual_toggles = QWidget()
    casual_toggles.setObjectName("combatMagicCasualControls")
    casual_layout = QHBoxLayout(casual_toggles)
    casual_layout.setContentsMargins(0, 0, 0, 0)
    prayer_master = QCheckBox("Prayers/Curses")
    prayer_master.setObjectName("combatPrayerMasterCheck")
    prayer_master.setChecked(view["prayers_enabled"])
    dream_thrift = QCheckBox("Dream thrift")
    dream_thrift.setObjectName("combatDreamThriftCheck")
    dream_thrift.setChecked(view["dream_thrift"])
    casual_auto_prayer = auto_prayer_check("Auto-bury bones", "combatCasualAutoPrayerTrainingCheck")
    dream_reasons = combat_dream_thrift_locked_reasons_pure(player_data)
    dream_thrift.setEnabled(
        on_set_combat_prayer_config is not None and not dream_reasons
    )
    if dream_reasons:
        dream_thrift.setToolTip(f"Requires {dream_reasons[0]}.")
    if on_set_combat_prayer_config is not None:
        prayer_master.toggled.connect(lambda enabled: on_set_combat_prayer_config("combat_prayers_enabled", bool(enabled)))
        dream_thrift.toggled.connect(lambda enabled: on_set_combat_prayer_config("combat_dream_thrift", bool(enabled)))
    casual_layout.addWidget(prayer_master)
    casual_layout.addWidget(dream_thrift)
    casual_layout.addWidget(casual_auto_prayer)
    casual_layout.addStretch(1)
    layout.addWidget(casual_toggles)


def _add_auto_eat_row(layout, view, on_set_combat_auto_eat_threshold) -> None:
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
    threshold_spin.setValue(view["auto_eat_threshold"])
    if on_set_combat_auto_eat_threshold is not None:
        threshold_spin.valueChanged.connect(lambda value: on_set_combat_auto_eat_threshold(value))
    auto_eat_layout.addWidget(threshold_label)
    auto_eat_layout.addWidget(threshold_spin, 1)
    layout.addWidget(auto_eat_row)


def _add_advanced_editor(layout, player_data, view, on_set_combat_prayer_config, auto_prayer_check) -> None:
    advanced_toggle = QToolButton()
    advanced_toggle.setObjectName("combatAdvancedPresetToggle")
    advanced_toggle.setText("Advanced preset editor")
    advanced_toggle.setCheckable(True)
    advanced_toggle.setChecked(False)
    layout.addWidget(advanced_toggle)
    advanced_panel = QWidget()
    advanced_panel.setObjectName("combatAdvancedPresetPanel")
    advanced_layout = QVBoxLayout(advanced_panel)
    advanced_layout.setContentsMargins(0, 0, 0, 0)
    advanced_layout.setSpacing(8)
    advanced_panel.setVisible(False)
    advanced_toggle.toggled.connect(advanced_panel.setVisible)
    layout.addWidget(advanced_panel)

    prayer_header = QLabel("Prayer")
    prayer_header.setStyleSheet("color: palette(text); font-weight: 600;")
    advanced_layout.addWidget(prayer_header)
    _add_prayer_controls(advanced_layout, view, on_set_combat_prayer_config)
    _add_magic_advanced(advanced_layout, view, on_set_combat_prayer_config)
    _add_preset_scope(advanced_layout, view, on_set_combat_prayer_config)
    _add_prayer_grid(advanced_layout, player_data, view, on_set_combat_prayer_config)
    advanced_layout.addWidget(
        auto_prayer_check(
            "Auto-bury/scatter combat drops (costs simulated ticks)",
            "combatAutoPrayerTrainingCheck",
        )
    )


def _add_prayer_controls(advanced_layout, view, on_set_combat_prayer_config) -> None:
    prayer_controls = QWidget()
    prayer_controls_layout = QHBoxLayout(prayer_controls)
    prayer_controls_layout.setContentsMargins(0, 0, 0, 0)
    prayer_controls_layout.setSpacing(8)
    preset_combo = QComboBox()
    preset_combo.setObjectName("combatPresetCombo")
    for name in view["preset_names"]:
        preset_combo.addItem(name, name)
    preset_combo.setCurrentText(view["active_preset"])
    if on_set_combat_prayer_config is not None:
        preset_combo.currentTextChanged.connect(lambda name: on_set_combat_prayer_config("apply_preset", name))
    prayer_controls_layout.addWidget(QLabel("Preset"))
    prayer_controls_layout.addWidget(preset_combo, 1)
    save_preset = QPushButton("Save current…")
    save_preset.setObjectName("combatSavePresetButton")
    if on_set_combat_prayer_config is not None:
        def _save_current_preset() -> None:
            name, accepted = QInputDialog.getText(save_preset, "Save combat preset", "Preset name")
            if accepted and name.strip():
                on_set_combat_prayer_config("save_preset", name.strip())
        save_preset.clicked.connect(_save_current_preset)
    prayer_controls_layout.addWidget(save_preset)

    book_combo = QComboBox()
    book_combo.setObjectName("combatPrayerBookCombo")
    book_combo.addItem("Standard prayers", "standard")
    book_combo.addItem("Ancient Curses", "curses")
    curses_index = book_combo.findData("curses")
    if curses_index >= 0:
        book_combo.model().item(curses_index).setEnabled(view["curses_unlocked"])
    book_combo.setCurrentIndex(max(0, book_combo.findData(view["prayer_book"])))
    if on_set_combat_prayer_config is not None:
        book_combo.currentIndexChanged.connect(lambda _i: on_set_combat_prayer_config("combat_prayer_book", book_combo.currentData()))
    prayer_controls_layout.addWidget(book_combo)

    uptime_combo = QComboBox()
    uptime_combo.setObjectName("combatPrayerUptimeCombo")
    for label, value in (("Off", "off"), ("Conservative 40%", "40"), ("Aggressive 70%", "70"), ("Always 100%", "100")):
        uptime_combo.addItem(label, value)
    uptime_combo.setCurrentIndex(max(0, uptime_combo.findData(view["prayer_uptime"])))
    if on_set_combat_prayer_config is not None:
        uptime_combo.currentIndexChanged.connect(lambda _i: on_set_combat_prayer_config("combat_prayer_uptime", uptime_combo.currentData()))
    prayer_controls_layout.addWidget(uptime_combo)
    advanced_layout.addWidget(prayer_controls)


def _add_magic_advanced(advanced_layout, view, on_set_combat_prayer_config) -> None:
    magic_advanced = QWidget()
    magic_advanced_layout = QHBoxLayout(magic_advanced)
    magic_advanced_layout.setContentsMargins(0, 0, 0, 0)
    vengeance_check = QCheckBox("Vengeance")
    vengeance_check.setObjectName("combatVengeanceCheck")
    vengeance_check.setChecked(view["vengeance"])
    swap_combo = QComboBox()
    swap_combo.setObjectName("combatSpellbookSwapCombo")
    swap_combo.addItem("No Spellbook Swap", "")
    swap_combo.addItem("Swap autocast", str(view["autocast_spell"]))
    swap_combo.addItem("Swap Vengeance", "vengeance")
    swap_combo.addItem("Swap Dream", "dream")
    swap_combo.setCurrentIndex(max(0, swap_combo.findData(view["spellbook_swap"])))
    if on_set_combat_prayer_config is not None:
        vengeance_check.toggled.connect(lambda enabled: on_set_combat_prayer_config("combat_vengeance", bool(enabled)))
        swap_combo.currentIndexChanged.connect(lambda _i: on_set_combat_prayer_config("combat_spellbook_swap", str(swap_combo.currentData() or "")))
    magic_advanced_layout.addWidget(vengeance_check)
    magic_advanced_layout.addWidget(QLabel("One off-book effect"))
    magic_advanced_layout.addWidget(swap_combo, 1)
    advanced_layout.addWidget(magic_advanced)


def _add_preset_scope(advanced_layout, view, on_set_combat_prayer_config) -> None:
    preset_scope = QWidget()
    preset_scope_layout = QHBoxLayout(preset_scope)
    preset_scope_layout.setContentsMargins(0, 0, 0, 0)
    pin_preset = QCheckBox("Pin preset to this target")
    pin_preset.setObjectName("combatPinPresetCheck")
    pin_preset.setChecked(view["preset_pinned"])
    override_prayers = QCheckBox("Override prayers")
    override_prayers.setObjectName("combatOverridePrayersCheck")
    override_prayers.setChecked(view["prayers_overridden"])
    override_uptime = QCheckBox("Override uptime")
    override_uptime.setObjectName("combatOverridePrayerUptimeCheck")
    override_uptime.setChecked(view["uptime_overridden"])
    if on_set_combat_prayer_config is not None:
        pin_preset.toggled.connect(lambda enabled: on_set_combat_prayer_config("pin_target_preset", enabled))
        override_prayers.toggled.connect(lambda enabled: on_set_combat_prayer_config("target_override", ("combat_selected_prayers", enabled)))
        override_uptime.toggled.connect(lambda enabled: on_set_combat_prayer_config("target_override", ("combat_prayer_uptime", enabled)))
    preset_scope_layout.addWidget(pin_preset)
    preset_scope_layout.addWidget(override_prayers)
    preset_scope_layout.addWidget(override_uptime)
    advanced_layout.addWidget(preset_scope)


def _prayer_check(row) -> "QCheckBox":
    check = QCheckBox(row["label"])
    check.setObjectName(f"combatPrayerCheck::{row['id']}")
    check.setEnabled(row["unlocked"])
    if row["tooltip"]:
        check.setToolTip(row["tooltip"])
    check.setProperty("prayerLevel", row["level"])
    check.setProperty("prayerId", row["id"])
    return check


def _add_prayer_grid(advanced_layout, player_data, view, on_set_combat_prayer_config) -> None:
    hide_lower = QCheckBox("Hide lower-tier prayers")
    hide_lower.setObjectName("combatPrayerHideLowerCheck")
    advanced_layout.addWidget(hide_lower)
    prayer_grid = QWidget()
    prayer_grid.setObjectName("combatPrayerCheckboxGrid")
    prayer_grid_layout = QGridLayout(prayer_grid)
    prayer_grid_layout.setContentsMargins(0, 0, 0, 0)
    prayer_checks = []

    def _on_prayer_toggled(prayer_id: str, checked: bool) -> None:
        if on_set_combat_prayer_config is None:
            return
        on_set_combat_prayer_config(
            "combat_selected_prayers",
            toggled_combat_prayer_selection_pure(player_data, prayer_id, checked),
        )
        # The save drops prayers that conflict with the newly ticked one, so
        # the boxes re-read what was kept.
        _show_selected_prayers(prayer_checks, combat_setup_panel_view_pure(player_data)["selected_prayers"])

    for index, row in enumerate(view["prayers"]):
        check = _prayer_check(row)
        check.setChecked(row["id"] in view["selected_prayers"])
        check.toggled.connect(lambda checked, pid=row["id"]: _on_prayer_toggled(pid, checked))
        prayer_grid_layout.addWidget(check, index // 3, index % 3)
        prayer_checks.append(check)
    hide_lower.toggled.connect(lambda hidden: _hide_lower_prayers(prayer_checks, view["lower_tier_below"], hidden))
    advanced_layout.addWidget(prayer_grid)


def _show_selected_prayers(prayer_checks, active: set) -> None:
    for prayer_check in prayer_checks:
        prayer_check.blockSignals(True)
        prayer_check.setChecked(str(prayer_check.property("prayerId")) in active)
        prayer_check.blockSignals(False)


def _hide_lower_prayers(prayer_checks, lower_tier_below: int, hidden: bool) -> None:
    for check in prayer_checks:
        check.setVisible(not hidden or int(check.property("prayerLevel") or 1) >= lower_tier_below)


def _add_loot_rules(
    layout,
    view,
    loot_override_rows,
    item_icon_path,
    on_set_loot_threshold,
    on_set_loot_override,
) -> None:
    # ---- Loot from this enemy ----
    # Deciding what to pick up belongs with the live combat controls, not the
    # Bank tab. The default view is coarse: a value threshold plus a single
    # "keep everything" toggle. Per-drop overrides are opt-in behind an
    # "Advanced" disclosure, rendered as icon cells with a binary Keep | Drop
    # pill (neither segment lit = follow the value threshold).
    loot_header = QLabel("Loot")
    loot_header.setObjectName("combatLootHeader")
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
    loot_spin.setValue(view["loot_threshold"])
    if on_set_loot_threshold is not None:
        loot_spin.valueChanged.connect(lambda value: on_set_loot_threshold(int(value)))
    loot_row_layout.addWidget(loot_label)
    loot_row_layout.addWidget(loot_spin, 1)
    layout.addWidget(loot_row)

    if loot_override_rows:
        _add_loot_overrides(layout, loot_override_rows, item_icon_path, on_set_loot_override)


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
        keep_all_check.blockSignals(True)
        keep_all_check.setChecked(all_keep)
        keep_all_check.blockSignals(False)

    def _on_keep_all(checked: bool) -> None:
        for name, _mode in cells:
            _choose(name, "keep" if checked else "auto")

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
# means "Auto": that drop follows the "Leave loot under N gp" threshold.
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
