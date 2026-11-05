from __future__ import annotations
import unittest
from unittest.mock import patch
from tests.test_main_menu_widget import (
    HAS_AQT,
    _ADDON_DIR,
    _bank_grid_texts,
    _find_tree_with_user_role,
    _icon_pixels,
    _make_player_data,
    _open_bank_tab,
    _open_equipment_tab,
    _tree_row,
    os,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QComboBox, QIcon, QLabel, QListWidget, QPushButton, QSpinBox, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_combat_finisher_action_only_enables_in_the_source_lp_window(self) -> None:
        ordinary = _make_player_data()
        ordinary["current_combat_target"] = "chicken"
        ordinary_dialog = self._open(ordinary, current_skill="Combat")
        ordinary_combo = ordinary_dialog.findChild(QComboBox, "combatActionCombo")
        self.assertIsNotNone(ordinary_combo)
        self.assertTrue(ordinary_combo.parentWidget().isHidden())

        blocked = _make_player_data()
        blocked.update(
            {
                "current_combat_target": "desert_lizard",
                "slayer_level": 99,
                "combat_encounter": {
                    "target_id": "desert_lizard",
                    "enemy_lifepoints": 31,
                },
                "combat_supply_loadout": {
                    "finishers": {"Ice cooler": 1},
                    "hazards": {"Waterskin (4)": 1},
                },
            }
        )
        blocked_dialog = self._open(blocked, current_skill="Combat")
        blocked_combo = blocked_dialog.findChild(QComboBox, "combatActionCombo")
        self.assertFalse(blocked_combo.parentWidget().isHidden())
        self.assertFalse(blocked_combo.model().item(1).isEnabled())

        ready = _make_player_data()
        ready.update(
            {
                "current_combat_target": "desert_lizard",
                "slayer_level": 99,
                "combat_encounter": {
                    "target_id": "desert_lizard",
                    "enemy_lifepoints": 30,
                },
                "combat_supply_loadout": {
                    "finishers": {"Ice cooler": 1},
                    "hazards": {"Waterskin (4)": 1},
                },
            }
        )
        ready_dialog = self._open(ready, current_skill="Combat")
        combo = ready_dialog.findChild(QComboBox, "combatActionCombo")

        self.assertFalse(combo.parentWidget().isHidden())
        self.assertEqual(
            [combo.itemData(index) for index in range(combo.count())],
            ["attack", "finisher"],
        )
        self.assertEqual(combo.itemText(1), "Use Ice cooler")
        self.assertTrue(combo.model().item(1).isEnabled())
        tree = _find_tree_with_user_role(ready_dialog, "desert_lizard")
        lizard = _tree_row(tree, "desert_lizard")
        self.assertFalse(lizard.icon(0).isNull())
        self.assertIn("Finisher: Use Ice cooler at 1–30 LP", lizard.toolTip(0))
        self.assertIn(
            "Desert heat: 1 Waterskin dose per Combat review",
            lizard.toolTip(0),
        )
        combo.setCurrentIndex(1)
        QApplication.processEvents()
        self.assertEqual(self._combat_action_calls[-1], "finisher")

        reusable = _make_player_data()
        reusable.update(
            {
                "current_combat_target": "gargoyle",
                "slayer_level": 99,
                "combat_encounter": {
                    "target_id": "gargoyle",
                    "enemy_lifepoints": 89,
                },
                "combat_supply_loadout": {
                    "finishers": {"Rock hammer": 1},
                },
            }
        )
        reusable_dialog = self._open(reusable, current_skill="Combat")
        reusable_combo = reusable_dialog.findChild(QComboBox, "combatActionCombo")
        self.assertEqual(reusable_combo.itemText(1), "Smash with Rock hammer")
        self.assertTrue(reusable_combo.model().item(1).isEnabled())
        self.assertIn(
            "reusable Rock hammer",
            reusable_combo.model().item(1).toolTip(),
        )
        gargoyle_tree = _find_tree_with_user_role(reusable_dialog, "gargoyle")
        self.assertFalse(_tree_row(gargoyle_tree, "gargoyle").icon(0).isNull())

        charged = _make_player_data()
        charged.update(
            {
                "current_combat_target": "mutated_zygomite_level_74",
                "slayer_level": 57,
                "quests": {"lost_city": {"completed": True}},
                "combat_encounter": {
                    "target_id": "mutated_zygomite_level_74",
                    "enemy_lifepoints": 19,
                },
                "combat_supply_loadout": {
                    "finishers": {
                        "Fungicide spray 6": 1,
                        "Fungicide": 1,
                    },
                },
            }
        )
        charged_dialog = self._open(charged, current_skill="Combat")
        charged_combo = charged_dialog.findChild(QComboBox, "combatActionCombo")
        self.assertEqual(charged_combo.itemText(1), "Spray with fungicide")
        self.assertTrue(charged_combo.model().item(1).isEnabled())
        self.assertIn(
            "Spends one Fungicide spray charge",
            charged_combo.model().item(1).toolTip(),
        )
        charged_tree = _find_tree_with_user_role(
            charged_dialog, "mutated_zygomite_level_74"
        )
        zygomite_74 = _tree_row(charged_tree, "mutated_zygomite_level_74")
        zygomite_86 = _tree_row(charged_tree, "mutated_zygomite_level_86")
        self.assertFalse(zygomite_74.icon(0).isNull())
        self.assertFalse(zygomite_86.icon(0).isNull())
        self.assertIn("6 spray charges + 1 canister reloads", zygomite_74.toolTip(0))
        self.assertIn("Encounter: Pick the fungi", zygomite_74.toolTip(0))

        ordinary_dialog.deleteLater()
        blocked_dialog.deleteLater()
        ready_dialog.deleteLater()
        reusable_dialog.deleteLater()
        charged_dialog.deleteLater()

    def test_combat_sidebar_hides_combat_only_stat_skills(self) -> None:
        from ankiscape.ui import ui

        combat_button = next(b for b in self.dialog.findChildren(QPushButton) if b.text() == "Combat")
        combat_button.click()
        QApplication.processEvents()

        skill_list = next(
            lw for lw in self.dialog.findChildren(QListWidget)
            if any(lw.item(i).text() == "Combat" for i in range(lw.count()))
        )
        texts = [skill_list.item(i).text() for i in range(skill_list.count())]
        self.assertEqual(texts, ["Combat", "Prayer", "Magic", "Summoning"])
        combat_item = next(
            skill_list.item(i)
            for i in range(skill_list.count())
            if skill_list.item(i).text() == "Combat"
        )
        self.assertEqual(
            _icon_pixels(combat_item.icon()),
            _icon_pixels(
                QIcon(
                    os.path.join(_ADDON_DIR, "icon", "combat_icon.png")
                )
            ),
        )
        for hidden in ("Attack", "Constitution", "Defense", "Ranged", "Strength"):
            self.assertNotIn(hidden, texts)

    def test_combat_xp_bars_use_each_combat_skill_icon(self) -> None:
        dialog = self._open(_make_player_data(), current_skill="Combat")
        expected = {
            "Attack": "attack_icon.png",
            "Strength": "strength_icon.png",
            "Defence": "defense_icon.png",
            "Ranged": "ranged_icon.png",
            "Magic": "magic_icon.png",
            "Constitution": "constitution_icon.png",
        }
        rendered = {}
        for skill, filename in expected.items():
            label = dialog.findChild(
                QLabel, f"combatXpIcon{skill.replace(' ', '')}"
            )
            self.assertIsNotNone(label)
            self.assertIsNotNone(label.pixmap())
            icon = QIcon(label.pixmap())
            self.assertEqual(
                self._ui.skill_icon_path_for(skill),
                os.path.join(_ADDON_DIR, "icon", filename),
            )
            rendered[skill] = _icon_pixels(icon)
        self.assertEqual(len(set(rendered.values())), len(expected))

    def test_combat_death_possible_target_requires_confirmation(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_lifepoints": 20,
                "constitution_level": 10,
                "inventory": {},
                "combat_auto_eat_food": ["Shark"],
                "combat_supply_loadout": {},
            }
        )
        dialog = self._open(pd, current_skill="Combat")

        tree = _find_tree_with_user_role(dialog, "barbarian_level_10")
        barbarian = _tree_row(tree, "barbarian_level_10")
        original_question = self._ui.QMessageBox.question
        questions = []
        try:
            def _deny(*args, **kwargs):  # type: ignore[no-untyped-def]
                questions.append(args)
                return self._ui.QMessageBox.StandardButton.No

            self._ui.QMessageBox.question = _deny
            tree.itemClicked.emit(barbarian, 0)
            QApplication.processEvents()
            self.assertEqual(self._combat_calls, [])
            self.assertEqual(questions[0][1], "Confirm dangerous combat")
            self.assertIn("Death possible", questions[0][2])

            self._ui.QMessageBox.question = lambda *a, **k: self._ui.QMessageBox.StandardButton.Yes
            tree.itemClicked.emit(barbarian, 0)
            QApplication.processEvents()
            self.assertEqual(self._combat_calls[-1], "barbarian_level_10")
        finally:
            self._ui.QMessageBox.question = original_question

    def test_wilderness_combat_confirmation_is_cached_for_the_session_risk_set(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "constitution_level": 99,
                "combat_lifepoints": 990,
                "equipment": {
                    "weapon": "Rune sword",
                    "body": "Rune platebody",
                    "head": "Rune full helm",
                    "shield": "Iron kiteshield",
                },
            }
        )
        dialog = self._open(pd, current_skill="Combat")
        tree = _find_tree_with_user_role(dialog, "earth_warrior")
        earth_warrior = _tree_row(tree, "earth_warrior")
        original_question = self._ui.QMessageBox.question
        questions = []
        try:
            def _accept(*args, **kwargs):  # type: ignore[no-untyped-def]
                questions.append(args)
                return self._ui.QMessageBox.StandardButton.Yes

            self._ui.QMessageBox.question = _accept
            tree.itemClicked.emit(earth_warrior, 0)
            tree.itemClicked.emit(earth_warrior, 0)
            QApplication.processEvents()

            self.assertEqual(len(questions), 1)
            self.assertEqual(questions[0][1], "Confirm Wilderness combat")
            self.assertIn("creates no grave", questions[0][2])
            self.assertEqual(
                self._combat_calls[-2:],
                ["earth_warrior", "earth_warrior"],
            )
        finally:
            self._ui.QMessageBox.question = original_question

    def test_combat_derives_style_from_equipment_and_exposes_spell_on_equipment_tab(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "magic_standard",
                "current_combat_spell": "wind_strike",
                "magic_level": 10,
                "inventory": {'Air rune': 6, 'Mind rune': 6},
                "equipment": {"weapon": "Staff"},
                "combat_supply_loadout": {}, 'carried_inventory': {"chicken": {"Air rune": 1, "Mind rune": 1}},
            }
        )
        dialog = self._open(pd, current_skill="Combat")

        style_combo = dialog.findChild(QComboBox, "combatStyleCombo")
        spell_combo = dialog.findChild(QComboBox, "combatSpellCombo")
        fixed_style = dialog.findChild(QLabel, "combatFixedStyleLabel")
        self.assertTrue(style_combo.isHidden())
        self.assertFalse(spell_combo.parentWidget().isHidden())
        self.assertFalse(fixed_style.isHidden())
        self.assertIn("Magic", fixed_style.text())
        self.assertEqual(spell_combo.currentData(), "wind_strike")
        self.assertEqual(spell_combo.currentText(), "Wind Strike")
        for spell_id in ("water_strike", "earth_strike", "fire_strike", "wind_bolt", "fire_blast", "fire_wave"):
            self.assertGreaterEqual(spell_combo.findData(spell_id), 0)

        tree = _find_tree_with_user_role(dialog, "chicken")
        chicken = _tree_row(tree, "chicken")
        self.assertIn("Spell: Wind Strike", chicken.toolTip(0))
        self.assertIn("Rune: Air rune x1; 1 loaded + 5 bank", chicken.toolTip(0))

        fire_index = spell_combo.findData("fire_strike")
        spell_combo.setCurrentIndex(fire_index)
        QApplication.processEvents()
        self.assertEqual(self._combat_spell_calls[-1], "fire_strike")

        fire_wave_index = spell_combo.findData("fire_wave")
        spell_combo.setCurrentIndex(fire_wave_index)
        QApplication.processEvents()
        self.assertEqual(self._combat_spell_calls[-1], "fire_wave")

    def test_combat_exposes_bound_borrowed_power_as_one_manual_cast(self) -> None:
        from ankiscape.data.livid_farm_data import ARCANE_CAPACITOR_CHARGED

        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "magic_standard",
                "current_combat_spell": "wind_strike",
                "magic_level": 99,
                "equipment": {
                    "weapon": "Staff of air",
                    "neck": ARCANE_CAPACITOR_CHARGED,
                },
                "livid_farm": {
                    "borrowed_power_claimed": True,
                    "arcane_capacitor_spell": "wind_wave",
                    "arcane_capacitor_charges": 12,
                },
            }
        )
        dialog = self._open(pd, current_skill="Combat")
        _open_equipment_tab(dialog)
        dialog.show()
        QApplication.processEvents()

        row = dialog.findChild(QWidget, "combatBorrowedPowerRow")
        spell = dialog.findChild(QLabel, "combatBorrowedPowerSpell")
        button = dialog.findChild(QPushButton, "combatBorrowedPowerButton")
        self.assertTrue(row.isVisible())
        self.assertEqual(
            spell.text(),
            "Borrowed Power · Wind Wave · 12 charges",
        )
        self.assertEqual(button.text(), "Cast once next review")
        self.assertEqual(
            button.geometry().left(),
            spell.geometry().left(),
        )

        button.click()
        QApplication.processEvents()

        self.assertEqual(
            self._prayer_config_calls[-1],
            ("combat_borrowed_power_spell", "wind_wave"),
        )
        self.assertEqual(pd["combat_borrowed_power_spell"], "wind_wave")
        self.assertEqual(button.text(), "One cast armed")

    def test_ranged_weapon_exposes_attack_style_selector_and_wires_it(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "ranged_accurate",
                "equipment": {"weapon": "Shortbow"},
                "ranged_level": 20,
            }
        )
        dialog = self._open(pd, current_skill="Combat")

        style_combo = dialog.findChild(QComboBox, "combatStyleCombo")
        self.assertIsNotNone(style_combo, "ranged weapon should expose an attack-style selector")
        # Only ranged styles are offered (never melee/magic).
        # Ranged combo data is a (weapon_style, style_type) pair; ranged has no
        # per-hit stab/slash/crush choice, so style_type is always "auto".
        ids = [style_combo.itemData(i) for i in range(style_combo.count())]
        self.assertEqual(
            ids,
            [
                ("ranged_accurate", "auto"),
                ("ranged_rapid", "auto"),
                ("ranged_longrange", "auto"),
            ],
        )
        self.assertEqual(style_combo.currentData(), ("ranged_accurate", "auto"))
        # Selecting a style persists it via on_set_combat_style.
        style_combo.setCurrentIndex(ids.index(("ranged_rapid", "auto")))
        QApplication.processEvents()
        self.assertEqual(self._combat_style_calls[-1], ("ranged_rapid", "auto"))

    def test_melee_weapon_style_selector_offers_only_melee_styles(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "aggressive",
                "equipment": {"weapon": "Bronze longsword"},
            }
        )
        dialog = self._open(pd, current_skill="Combat")

        style_combo = dialog.findChild(QComboBox, "combatStyleCombo")
        self.assertIsNotNone(style_combo)
        # A longsword's four slots each carry their own attack type; the combo
        # data is a (weapon_style, style_type) pair per slot.
        ids = [style_combo.itemData(i) for i in range(style_combo.count())]
        self.assertEqual(
            ids,
            [
                ("accurate", "slash"),
                ("aggressive", "slash"),
                ("controlled", "stab"),
                ("defensive", "slash"),
            ],
        )
        self.assertEqual(style_combo.currentData(), ("aggressive", "slash"))
        style_combo.setCurrentIndex(ids.index(("defensive", "slash")))
        QApplication.processEvents()
        self.assertEqual(self._combat_style_calls[-1], ("defensive", "slash"))

    def test_combat_repairs_stale_loadout_before_exposing_controls(self) -> None:
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data

        pd = _make_player_data()
        pd.update(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "inventory": {'Fire rune': 150, 'Air rune': 5, 'Mind rune': 5},
                "current_combat_target": "chicken",
                "combat_auto_eat_threshold_percent": 55,
                "combat_auto_eat_food": ["Lobster", "Shrimps"],
                "combat_supply_loadout": {'food': {"Lobster": 3}, 'potions': {"Antipoison (1)": 1}}, 'equipment': {'ammunition': "Bronze arrows"}, 'equipment_ammunition_count': 10, 'carried_inventory': {"chicken": {"Air rune": 5, "Mind rune": 5, "Fire rune": 50}},
            }
        )
        pd = migrate_loaded_data(pd, ORE_DATA, ITEM_DEFINITIONS)
        dialog = self._open(pd, current_skill="Combat")

        # The supply-mode summary and bank-run status moved into the carried-pack
        # section's Auto view; Refill was removed (supplies auto-refill at bank
        # runs) and Unload became a plain "Clear inventory" button.
        threshold_spin = dialog.findChild(QSpinBox, "combatAutoEatThresholdSpin")
        summary_label = dialog.findChild(QLabel, "combatLoadoutSummaryLabel")
        bank_run_label = dialog.findChild(QLabel, "combatBankRunLabel")
        clear_button = dialog.findChild(QPushButton, "combatClearInventoryButton")

        self.assertIsNotNone(threshold_spin)
        self.assertIsNone(dialog.findChild(QComboBox, "combatFoodCombo"))
        self.assertIsNotNone(summary_label)
        self.assertIsNotNone(bank_run_label)
        self.assertIsNotNone(clear_button)
        self.assertIsNone(dialog.findChild(QPushButton, "combatRefillLoadoutButton"))
        self.assertEqual(threshold_spin.value(), 55)
        self.assertIn("Food: Lobster x3", summary_label.text())
        self.assertIn("Potions: Antipoison (1) x1", summary_label.text())
        self.assertIn("Ammo: none loaded", summary_label.text())
        self.assertIn("Runes: none loaded", summary_label.text())
        self.assertIn("ready", bank_run_label.text())
        _open_bank_tab(dialog)
        bank_texts = _bank_grid_texts(dialog)
        self.assertIn("Air rune x5", bank_texts)
        self.assertIn("Mind rune x5", bank_texts)
        self.assertIn("Bronze arrows x10", bank_texts)
        self.assertIn("Fire rune x150", bank_texts)

        threshold_spin.setValue(60)
        QApplication.processEvents()
        self.assertEqual(self._combat_threshold_calls[-1], 60)

        clear_button.click()
        QApplication.processEvents()
        self.assertEqual(self._combat_unload_calls, [True])
        self.assertIn("Fire rune x150", _bank_grid_texts(dialog))

    def test_equipping_weapon_refreshes_equipment_combat_mode(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "combat_attack_style": "accurate",
                "inventory": {"Shortbow": 1},
                "ranged_level": 1,
            }
        )
        dialog = self._open_with_equip(pd)
        style_combo = dialog.findChild(QComboBox, "combatStyleCombo")
        self.assertIn("Accurate", style_combo.currentText())

        menu = dialog._ankiscape_equip_menu_for("Shortbow")
        action = next(action for action in menu.actions() if action.text() == "Equip")
        action.trigger()
        QApplication.processEvents()

        self.assertEqual(pd["equipment"], {"weapon": "Shortbow"})
        self.assertEqual(style_combo.currentData(), ("ranged_accurate", "auto"))

    def test_every_combat_setting_is_in_sight_in_a_short_dialog(self) -> None:
        pd = _make_player_data()
        pd["equipment"] = {"weapon": "Staff of air"}
        dialog = self._open(pd)
        _open_equipment_tab(dialog)
        dialog.resize(900, 560)
        dialog.show()
        QApplication.processEvents()
        panel = dialog.findChild(QWidget, "equipmentCombatSetupPanel")
        for kind, name in (
            (QComboBox, "combatSpellCombo"),
            (QCheckBox, "combatPrayerMasterCheck"),
            (QComboBox, "combatPrayerUptimeCombo"),
            (QSpinBox, "combatAutoEatThresholdSpin"),
            (QCheckBox, "combatAutoPrayerTrainingCheck"),
            (QSpinBox, "combatLootThresholdSpin"),
            (QComboBox, "combatPresetCombo"),
            (QCheckBox, "combatPinPresetCheck"),
            (QCheckBox, "combatOverridePrayersCheck"),
            (QCheckBox, "combatOverridePrayerUptimeCheck"),
            (QCheckBox, "combatVengeanceCheck"),
            (QComboBox, "combatSpellbookSwapCombo"),
        ):
            with self.subTest(name=name):
                self.assertTrue(dialog.findChild(kind, name).isVisibleTo(panel))
        auto_bury = dialog.findChild(QCheckBox, "combatAutoPrayerTrainingCheck")
        auto_bury.setChecked(True)
        QApplication.processEvents()
        self.assertEqual(self._prayer_config_calls[-1], ("combat_auto_prayer_training", True))
        scroll = panel.parentWidget()
        while not hasattr(scroll, "horizontalScrollBar"):
            scroll = scroll.parentWidget()
        self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)

    def test_a_ticked_prayer_box_updates_its_readouts_and_the_target_tooltip_at_once(self) -> None:
        pd = _make_player_data()
        pd.update({
            "attack_level": 70, "strength_level": 72, "prayer_level": 43, "combat_prayer_points": 430,
            "current_combat_target": "chicken", "combat_attack_style": "aggressive",
            "equipment": {"weapon": "Rune scimitar"}, "combat_prayers_enabled": False,
        })
        dialog = self._open(pd, current_skill="Combat")
        status = dialog.findChild(QLabel, "combatPrayerStatusLabel")
        max_hit = dialog.findChild(QLabel, "combatMaxHitLabel")
        burst = dialog.findChild(QCheckBox, "combatPrayerCheck::burst_of_strength")
        self.assertIn("Your max hit: 140 LP", _tree_row(_find_tree_with_user_role(dialog, "chicken"), "chicken").toolTip(0))
        self.assertTrue(status.isHidden())
        self.assertFalse(burst.isEnabled())

        dialog.findChild(QCheckBox, "combatPrayerMasterCheck").click()
        QApplication.processEvents()
        picked = {
            prayer_id for prayer_id in ("thick_skin", "steel_skin", "ultimate_strength", "incredible_reflexes")
            if dialog.findChild(QCheckBox, f"combatPrayerCheck::{prayer_id}").isChecked()
        }
        ultimate = dialog.findChild(QCheckBox, "combatPrayerCheck::ultimate_strength")
        self.assertEqual(picked, {"steel_skin", "ultimate_strength", "incredible_reflexes"})
        self.assertTrue(ultimate.property("picked"))
        auto_pick = dialog.findChild(QPushButton, "combatPrayerAutoPickButton")
        self.assertEqual((auto_pick.text(), auto_pick.isEnabled()), ("Auto-picked", False))
        self.assertTrue(max_hit.text().startswith("Max hit: 160 LP"))

        burst.click()
        QApplication.processEvents()

        # Burst of Strength shares Ultimate Strength's slot, so only that box swaps.
        self.assertEqual(pd["combat_selected_prayers"], ["burst_of_strength", "incredible_reflexes", "steel_skin"])
        self.assertFalse(ultimate.isChecked())
        swap_note = dialog.findChild(QLabel, "combatPrayerSwapNote")
        self.assertEqual(swap_note.text(), "Burst of Strength replaced Ultimate Strength.")
        self.assertFalse(swap_note.isHidden())
        self.assertFalse(burst.property("picked"))
        self.assertTrue(status.isHidden())
        self.assertTrue(max_hit.text().startswith("Max hit: 150 LP"))
        self.assertIn("Your max hit: 150 LP", _tree_row(_find_tree_with_user_role(dialog, "chicken"), "chicken").toolTip(0))

        dialog.findChild(QPushButton, "combatPrayerAutoPickButton").click()
        QApplication.processEvents()
        self.assertEqual(pd["combat_selected_prayers"], [])
        self.assertTrue(ultimate.isChecked())
        self.assertTrue(swap_note.isHidden())

    def test_unticked_prayers_keep_the_ticks_as_saved_choices(self) -> None:
        pd = _make_player_data()
        pd.update({
            "prayer_level": 43, "combat_prayer_points": 430,
            "combat_selected_prayers": ["burst_of_strength"], "combat_prayers_enabled": False,
        })
        dialog = self._open(pd)
        burst = dialog.findChild(QCheckBox, "combatPrayerCheck::burst_of_strength")
        auto_pick = dialog.findChild(QPushButton, "combatPrayerAutoPickButton")
        self.assertTrue(burst.isChecked())
        self.assertFalse(burst.isEnabled())
        self.assertTrue(dialog.findChild(QLabel, "combatPrayerStatusLabel").isHidden())
        self.assertFalse(auto_pick.isEnabled())
        self.assertEqual(auto_pick.toolTip(), "Prayers are off.")
        self.assertEqual(pd["combat_selected_prayers"], ["burst_of_strength"])

    def test_saving_a_preset_for_the_target_switches_the_target_to_it(self) -> None:
        from ankiscape.ui import ui_combat_setup_panel as panel

        pd = _make_player_data()
        pd.update({"prayer_level": 43, "combat_prayer_points": 430, "current_combat_target": "chicken"})
        dialog = self._open(pd)
        save = dialog.findChild(QPushButton, "combatSavePresetButton")
        self.assertEqual(save.text(), "Save preset…")
        build = panel.preset_save_dialog

        def named(parent, target):
            built, name, switch = build(parent, target)
            self.assertTrue(switch.isChecked())
            self.assertEqual(switch.text(), "Use against Chicken")
            name.setText("Chickens")
            built.exec = lambda: panel.QDialog.DialogCode.Accepted
            return built, name, switch

        with patch.object(panel, "preset_save_dialog", named):
            save.click()
        QApplication.processEvents()
        self.assertIn("Chickens", pd["combat_presets"])
        self.assertEqual(pd["combat_target_presets"], {"chicken": "Chickens"})
        self.assertTrue(
            dialog.findChild(QLabel, "combatTargetSummaryLabel").text().startswith("Against Chicken: Chickens preset · ")
        )

    def test_the_target_summary_shows_what_its_preset_and_kept_settings_give_fights(self) -> None:
        pd = _make_player_data()
        pd.update({
            "prayer_level": 43, "combat_prayer_points": 430, "current_combat_target": "chicken",
            "combat_presets": {"Default": {}, "Slayer": {"combat_selected_prayers": ["steel_skin"]}},
        })
        dialog = self._open(pd)
        summary = dialog.findChild(QLabel, "combatTargetSummaryLabel")
        self.assertEqual(
            summary.text(),
            "Against Chicken: auto-picked prayers for the whole fight",
        )
        dialog.findChild(QComboBox, "combatPresetCombo").setCurrentText("Slayer")
        dialog.findChild(QCheckBox, "combatPinPresetCheck").click()
        dialog.findChild(QCheckBox, "combatOverridePrayerUptimeCheck").click()
        QApplication.processEvents()
        self.assertEqual(
            summary.text(),
            "Against Chicken: Slayer preset · Steel Skin for the whole fight",
        )
        self.assertEqual(dialog.findChild(QCheckBox, "combatPinPresetCheck").text(), "Use preset “Slayer” against Chicken")

    def test_choosing_a_preset_or_book_redraws_the_boxes_it_changed(self) -> None:
        pd = _make_player_data()
        pd.update({
            "prayer_level": 99, "defense_level": 99, "combat_prayer_points": 990,
            "quests": {**pd.get("quests", {}), "the_temple_at_senntisten": {"completed": True}},
            "combat_presets": {
                "Default": {"combat_selected_prayers": [], "combat_auto_eat_threshold_percent": 40},
                "Slayer": {"combat_selected_prayers": ["steel_skin"], "combat_auto_eat_threshold_percent": 70},
            },
        })
        dialog = self._open(pd)
        dialog.findChild(QComboBox, "combatPresetCombo").setCurrentText("Slayer")
        QApplication.processEvents()
        self.assertTrue(dialog.findChild(QCheckBox, "combatPrayerCheck::steel_skin").isChecked())
        self.assertEqual(dialog.findChild(QSpinBox, "combatAutoEatThresholdSpin").value(), 70)

        book = dialog.findChild(QComboBox, "combatPrayerBookCombo")
        book.setCurrentIndex(book.findData("curses"))
        QApplication.processEvents()
        self.assertIsNotNone(dialog.findChild(QCheckBox, "combatPrayerCheck::turmoil"))
        self.assertIsNone(dialog.findChild(QCheckBox, "combatPrayerCheck::steel_skin"))

    def test_combat_prayer_controls_show_preset_picker_and_gate_curses(self) -> None:
        dialog = self._open(_make_player_data())
        preset = dialog.findChild(QComboBox, "combatPresetCombo")
        book = dialog.findChild(QComboBox, "combatPrayerBookCombo")
        self.assertIsNotNone(preset)
        self.assertEqual([preset.itemText(i) for i in range(preset.count())], ["Default"])
        curses_index = book.findData("curses")
        self.assertFalse(book.model().item(curses_index).isEnabled())
        self.assertIsNotNone(dialog.findChild(QPushButton, "combatSavePresetButton"))
        self.assertIsNotNone(dialog.findChild(QCheckBox, "combatPinPresetCheck"))

    def test_combat_prayer_checkbox_conflicts_are_reflected_in_widgets(self) -> None:
        pd = _make_player_data()
        pd["prayer_level"] = 99
        pd["knight_waves"] = {"completed": True}
        dialog = self._open(pd)
        clarity = dialog.findChild(QCheckBox, "combatPrayerCheck::clarity_of_thought")
        strength = dialog.findChild(QCheckBox, "combatPrayerCheck::burst_of_strength")
        eagle = dialog.findChild(QCheckBox, "combatPrayerCheck::eagle_eye")
        clarity.click()
        strength.click()
        eagle.click()
        QApplication.processEvents()
        checked = {check.objectName() for check in (clarity, strength, eagle) if check.isChecked()}
        self.assertEqual(checked, {"combatPrayerCheck::eagle_eye"})
