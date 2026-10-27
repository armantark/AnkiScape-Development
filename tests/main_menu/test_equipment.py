from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _bank_grid_button,
    _equip_slot_row,
    _find_equipment_list,
    _find_main_tabs,
    _make_player_data,
    _open_equipment_tab,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QPalette, QPoint, QPushButton, QSpinBox, QTreeWidget, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_equipment_follower_panel_projects_familiars_and_complete_pet_log(self) -> None:
        from ankiscape.logic.summoning_logic import default_summoning_state_pure, summon_familiar_pure

        pd = _make_player_data()
        pd["summoning_level"] = 99
        pd["inventory"] = {"Spirit wolf pouch": 1}
        pd["summoning_state"] = default_summoning_state_pure()
        calls = []

        def command(action_id, payload):
            calls.append((action_id, dict(payload)))
            if action_id != "summon":
                return {"ok": False}
            updated, ok, info = summon_familiar_pure(
                pd, str(payload.get("familiar_id", ""))
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, **info}

        dialog = self._open(
            pd,
            current_skill="Summoning",
            on_summoning_command=command,
        )
        dialog.show()
        _open_equipment_tab(dialog)
        QApplication.processEvents()

        panel = dialog.findChild(QWidget, "summoningFollowerPanel")
        summary = dialog.findChild(QLabel, "summoningFollowerSummary")
        picker = dialog.findChild(QComboBox, "summoningFamiliarPicker")
        summon = dialog.findChild(QPushButton, "summoningSummonButton")
        pets = dialog.findChild(QTreeWidget, "summoningPetsLog")
        self.assertIsNotNone(panel)
        self.assertEqual(summary.text(), "No follower active.")
        self.assertEqual(pets.topLevelItemCount(), 44)

        picker.setCurrentIndex(picker.findData("spiritwolf"))
        summon.click()
        QApplication.processEvents()

        self.assertEqual(calls, [("summon", {"familiar_id": "spiritwolf"})])
        self.assertIn("Spirit wolf", summary.text())
        self.assertIn("review(s) remain", summary.text())
        self.assertIsNone(
            panel.findChild(
                QPushButton, "summoningStartFamiliarisationButton"
            )
        )
        dialog.deleteLater()

    def test_pets_surface_hatches_banked_phoenix_eggs_at_level_72(self) -> None:
        from ankiscape.logic.pet_logic import hatch_phoenix_egg_pure
        from ankiscape.logic.summoning_logic import default_summoning_state_pure

        pd = _make_player_data()
        pd["summoning_level"] = 72
        pd["inventory"] = {"Phoenix egg": 1, "Cracked phoenix egg": 1}
        pd["summoning_state"] = default_summoning_state_pure()
        calls = []

        def command(action_id, payload):
            calls.append((action_id, dict(payload)))
            if action_id != "hatch_phoenix_egg":
                return {"ok": False}
            updated, ok, info = hatch_phoenix_egg_pure(
                pd, str(payload.get("item_name", ""))
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "instance_id": info if ok else "", "reason": info}

        dialog = self._open(
            pd,
            current_skill="Summoning",
            on_summoning_command=command,
        )
        dialog.show()
        _open_equipment_tab(dialog)
        QApplication.processEvents()

        toggle = dialog.findChild(QPushButton, "summoningPetsToggle")
        row = dialog.findChild(QWidget, "summoningPhoenixEggRow")
        label = dialog.findChild(QLabel, "summoningPhoenixEggLabel")
        cute = dialog.findChild(QPushButton, "summoningHatchCutePhoenixButton")
        mean = dialog.findChild(QPushButton, "summoningHatchMeanPhoenixButton")
        toggle.click()
        QApplication.processEvents()
        self.assertFalse(row.isHidden())
        self.assertEqual(label.text(), "Phoenix eggs")
        self.assertEqual(cute.text(), "Hatch Cute · 1")
        self.assertEqual(mean.text(), "Hatch Mean · 1")
        self.assertIn("Phoenix egg", cute.toolTip())
        self.assertIn("Cracked phoenix egg", mean.toolTip())

        cute.click()
        QApplication.processEvents()
        self.assertEqual(
            calls[-1],
            ("hatch_phoenix_egg", {"item_name": "Phoenix egg"}),
        )
        self.assertEqual(pd["inventory"]["Phoenix egg"], 0)
        self.assertEqual(cute.text(), "Hatch Cute · 0")
        self.assertTrue(
            any(
                instance["pet_id"] == "cute_phoenix_eggling"
                for instance in pd["summoning_state"]["pet_instances"].values()
            )
        )
        dialog.deleteLater()

    def test_pets_surface_explains_phoenix_egg_level_gate_inline(self) -> None:
        from ankiscape.logic.summoning_logic import default_summoning_state_pure

        pd = _make_player_data()
        pd["summoning_level"] = 71
        pd["inventory"] = {"Phoenix egg": 1}
        pd["summoning_state"] = default_summoning_state_pure()
        dialog = self._open(pd, current_skill="Summoning")
        dialog.show()
        _open_equipment_tab(dialog)
        toggle = dialog.findChild(QPushButton, "summoningPetsToggle")
        toggle.click()
        QApplication.processEvents()

        label = dialog.findChild(QLabel, "summoningPhoenixEggLabel")
        cute = dialog.findChild(QPushButton, "summoningHatchCutePhoenixButton")
        self.assertEqual(label.text(), "Phoenix eggs · needs Summoning 72")
        self.assertFalse(cute.isEnabled())
        dialog.deleteLater()

    def test_pack_yak_panel_exposes_target_priority_and_advanced_threshold(self) -> None:
        pd = _make_player_data()
        pd["summoning_level"] = 99
        pd["carried_inventory"] = {
            "copper": {"Copper ore": 4, "Winter storage scroll": 2}
        }
        pd["summoning_state"] = {
            "summoning_points_current": 99,
            "special_move_points_current": 60,
            "active_follower": {
                "kind": "familiar",
                "entity_id": "packyak",
                "remaining_reviews": 10,
                "max_reviews": 10,
                "lifepoints": 7100,
                "max_lifepoints": 7100,
                "storage": {},
            },
            "target_policies": {
                "copper": {
                    "winter_storage_priority": ["Copper ore"],
                    "winter_storage_threshold_free_slots": 3,
                }
            },
        }
        calls = []
        dialog = self._open(
            pd,
            current_skill="Mining",
            active_carried_target_id="copper",
            carried_pack_target_active=True,
            carried_advanced_state=True,
            on_summoning_command=lambda action_id, payload: calls.append(
                (action_id, dict(payload))
            )
            or {"ok": True},
        )
        dialog.show()
        _open_equipment_tab(dialog)
        QApplication.processEvents()

        row = dialog.findChild(QWidget, "summoningWinterStorageRow")
        picker = dialog.findChild(QComboBox, "summoningWinterStoragePicker")
        threshold = dialog.findChild(
            QSpinBox, "summoningWinterStorageThreshold"
        )
        save = dialog.findChild(
            QPushButton, "summoningWinterStorageSetButton"
        )
        self.assertFalse(row.isHidden())
        self.assertEqual(picker.currentData(), "Copper ore")
        self.assertFalse(threshold.isHidden())
        self.assertEqual(threshold.value(), 3)

        threshold.setValue(2)
        save.click()
        QApplication.processEvents()
        self.assertEqual(
            calls,
            [
                (
                    "set_winter_storage_priority",
                    {
                        "target_id": "copper",
                        "item_name": "Copper ore",
                        "threshold_free_slots": 2,
                    },
                )
            ],
        )
        dialog.deleteLater()

    def test_urn_teleport_eligibility_and_passives_stay_non_equipment(self) -> None:
        from ankiscape.data.urn_data import URN_TIERS_BY_ID

        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        pd = _make_player_data()
        pd.update(
            {
                "inventory": {
                    tier.item_full: 1,
                    tier.item_r: 1,
                    "Bonecrusher": 1,
                    "Ectoplasmator": 1,
                },
                "current_ore": "copper",
                "carried_inventory": {"tin": {tier.item_full: 1}},
            }
        )
        dialog = self._open(
            pd,
            current_skill="Mining",
            on_teleport_training_urn=lambda _urn_id: True,
            on_discard_item=lambda _item, _quantity: True,
        )
        full_menu = dialog._ankiscape_equip_menu_for(tier.item_full)
        teleport = next(action for action in full_menu.actions() if action.text() == "Teleport urn")
        self.assertFalse(teleport.isEnabled())
        self.assertIn("current Mining target", teleport.toolTip())

        runed_menu = dialog._ankiscape_equip_menu_for(tier.item_r)
        self.assertNotIn("Teleport urn", [action.text() for action in runed_menu.actions()])

        for passive in ("Bonecrusher", "Ectoplasmator"):
            row = _bank_grid_button(dialog, passive)
            self.assertFalse(row.icon().isNull(), f"{passive} row has no icon")
            menu = dialog._ankiscape_equip_menu_for(passive)
            self.assertFalse(any(action.text().startswith("Equip") for action in menu.actions()))
        dialog.deleteLater()

    def test_family_gauntlet_conversion_is_available_from_bank_and_equipment(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Family gauntlets": 1, "Coins": 0}
        pd["equipment"] = {}
        pd["quests"]["family_crest"] = {
            "started": True,
            "progress": 16,
            "completed": True,
        }
        commands = []

        def command(action, payload):
            commands.append((action, dict(payload)))
            return {"ok": True, "message": "Converted"}

        dialog = self._open(
            pd,
            current_skill="Cooking",
            on_cooking_gauntlets_command=command,
        )
        bank_menu = dialog._ankiscape_equip_menu_for("Family gauntlets")
        bank_action = next(
            action
            for action in bank_menu.actions()
            if action.objectName() == "convertCookingGauntletsAction"
        )
        self.assertEqual(bank_action.text(), "Enchant for Cooking")
        self.assertTrue(bank_action.isEnabled())
        bank_action.trigger()
        QApplication.processEvents()
        self.assertEqual(
            commands[-1],
            ("convert", {"item_name": "Family gauntlets"}),
        )
        dialog.deleteLater()

        worn = _make_player_data()
        worn["inventory"] = {"Coins": 25_000}
        worn["equipment"] = {"hands": "Goldsmith gauntlets"}
        worn["quests"]["family_crest"] = {
            "started": True,
            "progress": 16,
            "completed": True,
        }
        dialog = self._open(
            worn,
            current_skill="Cooking",
            on_cooking_gauntlets_command=command,
        )
        worn_menu = dialog._ankiscape_unequip_menu_for("hands")
        worn_action = next(
            action
            for action in worn_menu.actions()
            if action.objectName() == "convertWornCookingGauntletsAction"
        )
        self.assertEqual(
            worn_action.text(), "Re-enchant for Cooking (25,000 Coins)"
        )
        self.assertTrue(worn_action.isEnabled())
        dialog.deleteLater()

    def test_equipment_tab_renders_all_eleven_slots(self) -> None:
        from ankiscape.core.constants import EQUIPMENT_SLOTS

        equip_list = _find_equipment_list(self.dialog)
        rendered_slots = {
            equip_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(equip_list.count())
        }
        for slot in EQUIPMENT_SLOTS:
            self.assertIn(slot.id, rendered_slots, f"slot {slot.id!r} not rendered")
        # Empty save -> every slot shows the greyed "(empty)" placeholder.
        empties = [
            equip_list.item(i).text()
            for i in range(equip_list.count())
            if equip_list.item(i).data(Qt.ItemDataRole.UserRole + 1) is None
        ]
        self.assertEqual(len(empties), len(EQUIPMENT_SLOTS))
        self.assertTrue(all("(empty)" in t for t in empties))
        # Slot placeholder art is fetched into equipment_slots/, so empty rows
        # should carry the greyed OSRS slot icon (graceful text-only if absent).
        from ankiscape.ui import ui as _ui
        if _ui.equipment_slot_icon_path("head"):
            head_row = _equip_slot_row(equip_list, "head")
            self.assertFalse(head_row.icon().isNull(), "head slot has no placeholder icon")

    def test_equipment_points_header_renders_and_refreshes_live_values(self) -> None:
        player_data = _make_player_data()
        player_data.update(
            {
                "constitution_level": 73,
                "combat_lifepoints": 512,
                "prayer_level": 50,
                "combat_prayer_points": 310,
                "summoning_level": 42,
                "summoning_state": {"summoning_points_current": 17},
            }
        )
        dialog = self._open(player_data)
        _open_equipment_tab(dialog)
        dialog.show()
        dialog.resize(1000, 560)
        for _ in range(3):
            QApplication.processEvents()

        header = dialog.findChild(QWidget, "equipmentPointsHeader")
        life = dialog.findChild(QLabel, "equipmentPoint_lifepoints")
        prayer = dialog.findChild(QLabel, "equipmentPoint_prayer")
        summoning = dialog.findChild(QLabel, "equipmentPoint_summoning")
        self.assertIsNotNone(header)
        self.assertTrue(header.isVisible())
        self.assertGreater(header.height(), 0)
        self.assertEqual(life.text(), "Life points  512 / 730")
        self.assertEqual(prayer.text(), "Prayer points  31 / 50")
        self.assertEqual(summoning.text(), "Summoning points  17 / 42")

        player_data.update(
            {
                "constitution_level": 80,
                "combat_lifepoints": 321,
                "prayer_level": 70,
                "combat_prayer_points": 125,
                "summoning_level": 55,
                "summoning_state": {"summoning_points_current": 9},
            }
        )
        dialog._ankiscape_refresh_equipment()
        for _ in range(3):
            QApplication.processEvents()

        self.assertEqual(life.text(), "Life points  321 / 800")
        self.assertEqual(prayer.text(), "Prayer points  12 / 70")
        self.assertEqual(summoning.text(), "Summoning points  9 / 55")

    def test_equipment_tab_heads_the_combat_settings_with_the_current_target(self) -> None:
        player_data = _make_player_data()
        player_data["current_combat_target"] = "giant_rat"
        dialog = self._open(player_data)
        _open_equipment_tab(dialog)
        dialog.show()
        dialog.resize(1000, 560)
        for _ in range(4):
            QApplication.processEvents()

        target = dialog.findChild(QLabel, "combatCurrentTargetLabel")
        max_hit = dialog.findChild(QLabel, "combatMaxHitLabel")
        self.assertEqual(target.text(), "Current target: Giant rat")
        self.assertRegex(max_hit.text(), r"^Your max hit: \d+ LP · accuracy \d+%$")
        self.assertLess(target.mapTo(dialog, QPoint(0, 0)).y(), max_hit.mapTo(dialog, QPoint(0, 0)).y())

    def test_empty_slot_text_is_dark_mode_safe_not_palette_mid(self) -> None:
        # Regression guard for the recurring "greyed text vanishes in dark mode"
        # bug: empty-slot labels must use the dim-text helper (derived from the
        # readable Text role with reduced alpha), never QPalette.Mid (a border
        # role that renders near-black on a dark base).
        from ankiscape.ui import ui as _ui
        from aqt.qt import QPalette

        equip_list = _find_equipment_list(self.dialog)
        head_row = _equip_slot_row(equip_list, "head")
        fg = head_row.foreground().color()
        mid = equip_list.palette().color(QPalette.ColorRole.Mid)
        expected = _ui.dim_text_color(equip_list)
        self.assertEqual(fg.rgba(), expected.rgba(), "empty slot not using dim_text_color")
        self.assertLess(fg.alpha(), 255, "dim text should be semi-transparent")
        self.assertNotEqual(
            (fg.red(), fg.green(), fg.blue(), fg.alpha()),
            (mid.red(), mid.green(), mid.blue(), mid.alpha()),
            "empty slot text fell back to palette(mid) (invisible in dark mode)",
        )

    def test_bronze_item_exposes_enabled_equip(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze platebody": 1}
        dialog = self._open_with_equip(pd)
        menu = dialog._ankiscape_equip_menu_for("Bronze platebody")
        action = menu.actions()[0]
        self.assertEqual(action.text(), "Equip")
        self.assertTrue(action.isEnabled(), "bronze (req 1) Equip should be enabled")

    def test_rune_item_exposes_disabled_equip_with_reason(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Rune platebody": 1}
        dialog = self._open_with_equip(pd)
        menu = dialog._ankiscape_equip_menu_for("Rune platebody")
        action = menu.actions()[0]
        # Defence defaults to level 1, rune needs 40 -> locked with the reason.
        self.assertFalse(action.isEnabled(), "rune Equip should be locked at default combat")
        self.assertIn("Requires level 40 Defense", action.text())

    def test_equipping_moves_item_to_slot_and_out_of_inventory(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze platebody": 1}
        dialog = self._open_with_equip(pd)
        menu = dialog._ankiscape_equip_menu_for("Bronze platebody")
        menu.actions()[0].trigger()
        QApplication.processEvents()
        # Backend state: moved out of inventory into the body slot.
        self.assertEqual(pd["equipment"].get("body"), "Bronze platebody")
        self.assertEqual(pd["inventory"].get("Bronze platebody", 0), 0)
        # Frontend reflects it: the body slot row now names the item.
        equip_list = _find_equipment_list(dialog)
        body_row = _equip_slot_row(equip_list, "body")
        self.assertIn("Bronze platebody", body_row.text())
        self.assertEqual(body_row.data(Qt.ItemDataRole.UserRole + 1), "Bronze platebody")

    def test_equipping_and_removing_capacitor_refreshes_borrowed_power_row(self) -> None:
        from ankiscape.data.livid_farm_data import ARCANE_CAPACITOR_CHARGED

        pd = _make_player_data()
        pd.update(
            {
                "combat_attack_style": "magic_standard",
                "magic_level": 99,
                "inventory": {ARCANE_CAPACITOR_CHARGED: 1},
                "equipment": {"weapon": "Staff of air"},
                "livid_farm": {
                    "borrowed_power_claimed": True,
                    "arcane_capacitor_spell": "wind_wave",
                    "arcane_capacitor_charges": 12,
                },
            }
        )
        dialog = self._open_with_equip(pd)
        _open_equipment_tab(dialog)
        dialog.show()
        QApplication.processEvents()
        row = dialog.findChild(QWidget, "combatBorrowedPowerRow")
        self.assertFalse(row.isVisible())

        equip_menu = dialog._ankiscape_equip_menu_for(
            ARCANE_CAPACITOR_CHARGED
        )
        equip_menu.actions()[0].trigger()
        QApplication.processEvents()

        self.assertTrue(row.isVisible())
        self.assertIn("12 charges", row.findChild(QLabel).text())

        unequip_menu = dialog._ankiscape_unequip_menu_for("neck")
        self.assertIsNotNone(unequip_menu)
        unequip_menu.actions()[0].trigger()
        QApplication.processEvents()
        self.assertFalse(row.isVisible())

    def test_unequip_returns_item_to_inventory(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {}
        pd["equipment"] = {"body": "Bronze platebody"}
        dialog = self._open_with_equip(pd)
        equip_list = _find_equipment_list(dialog)
        body_row = _equip_slot_row(equip_list, "body")
        self.assertIn("Bronze platebody", body_row.text())
        menu = dialog._ankiscape_unequip_menu_for("body")
        self.assertIsNotNone(menu, "filled slot should offer an Unequip action")
        menu.actions()[0].trigger()
        QApplication.processEvents()
        self.assertNotIn("body", pd["equipment"])
        self.assertEqual(pd["inventory"].get("Bronze platebody", 0), 1)
        # Slot returns to the greyed placeholder.
        equip_list = _find_equipment_list(dialog)
        self.assertIn("(empty)", _equip_slot_row(equip_list, "body").text())

    def test_empty_slot_offers_no_unequip_menu(self) -> None:
        dialog = self._open_with_equip(_make_player_data())
        self.assertIsNone(dialog._ankiscape_unequip_menu_for("body"))

    def test_equipping_two_hander_clears_shield(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze 2h sword": 1}
        pd["equipment"] = {"shield": "Bronze kiteshield"}
        dialog = self._open_with_equip(pd)
        menu = dialog._ankiscape_equip_menu_for("Bronze 2h sword")
        menu.actions()[0].trigger()
        QApplication.processEvents()
        # 2h occupies the weapon slot and forces the shield off (back to bank).
        self.assertEqual(pd["equipment"].get("weapon"), "Bronze 2h sword")
        self.assertNotIn("shield", pd["equipment"])
        self.assertEqual(pd["inventory"].get("Bronze kiteshield", 0), 1)
        equip_list = _find_equipment_list(dialog)
        self.assertIn("(empty)", _equip_slot_row(equip_list, "shield").text())
        self.assertIn("Bronze 2h sword", _equip_slot_row(equip_list, "weapon").text())

    def test_stat_totals_reflect_worn_set(self) -> None:
        from ankiscape.core.constants import EQUIPMENT_ITEM_DATA

        pd = _make_player_data()
        pd["equipment"] = {"body": "Bronze platebody", "head": "Bronze full helm"}
        dialog = self._open_with_equip(pd)
        totals = next(
            lbl for lbl in dialog.findChildren(QLabel)
            if lbl.objectName() == "equipmentTotals"
        )
        text = totals.text()
        # Bronze platebody defence_stab 15 + Bronze full helm defence_stab 4 = 19.
        expected = (
            EQUIPMENT_ITEM_DATA["Bronze platebody"]["bonuses"]["defence_stab"]
            + EQUIPMENT_ITEM_DATA["Bronze full helm"]["bonuses"]["defence_stab"]
        )
        self.assertIn(f"Stab +{expected}", text)
        self.assertIn("Defence bonuses", text)

    def test_equippable_bank_row_has_bonus_tooltip(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Rune scimitar": 1}
        dialog = self._open_with_equip(pd)
        scim = _bank_grid_button(dialog, "Rune scimitar")
        tip = scim.toolTip()
        self.assertIn("Requires level 40 Attack", tip)
        self.assertIn("Attack bonuses", tip)

    def test_surefooted_aura_activates_from_the_equipment_tab(self) -> None:
        # Auras have a cooldown, so they keep a control — in their own
        # inventory inside the Equipment tab, not on the skill panel.
        pd = _make_player_data()
        pd["inventory"] = {"Surefooted aura": 1}
        dialog = self._open(pd, current_skill="Agility")
        dialog.show()
        QApplication.processEvents()
        tabs = _find_main_tabs(dialog)
        index = next(i for i in range(tabs.count()) if tabs.tabText(i) == "Equipment")
        tabs.setCurrentIndex(index)
        QApplication.processEvents()

        panel = dialog.findChild(QWidget, "equipmentAuraPanel")
        self.assertIsNotNone(panel)
        self.assertTrue(panel.isVisibleTo(dialog))
        activate = dialog.findChild(QPushButton, "equipmentAuraActivateButton")
        self.assertIsNotNone(activate)
        self.assertTrue(activate.isEnabled())
        activate.click()
        QApplication.processEvents()

        self.assertEqual(
            self._agility_command_calls[-1], ("activate_surefooted", {})
        )
        charges = pd.get("agility_effect_charges", {})
        self.assertEqual(charges.get("surefooted_reviews"), 333)
        # The row rebuilds from the view: cooling down, so no second activation.
        activate = dialog.findChild(QPushButton, "equipmentAuraActivateButton")
        self.assertFalse(activate.isEnabled())

        # Without an aura the inventory stays out of the way entirely.
        pd2 = _make_player_data()
        dialog2 = self._open(pd2, current_skill="Agility")
        dialog2.show()
        QApplication.processEvents()
        tabs2 = _find_main_tabs(dialog2)
        tabs2.setCurrentIndex(
            next(i for i in range(tabs2.count()) if tabs2.tabText(i) == "Equipment")
        )
        QApplication.processEvents()
        panel2 = dialog2.findChild(QWidget, "equipmentAuraPanel")
        self.assertIsNotNone(panel2)
        self.assertFalse(panel2.isVisibleTo(dialog2))
        dialog2.deleteLater()
