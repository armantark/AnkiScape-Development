from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _bank_grid_button,
    _bank_grid_buttons,
    _list_texts,
    _make_player_data,
    _open_bank_tab,
    _panel_title,
    _tree_items,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QListWidget, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_bank_toolbelt_attach_action_moves_mithril_hatchet_end_to_end(self) -> None:
        from ankiscape.core.constants import MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA
        from ankiscape.logic_pure.logic_pure_equipment import attach_tool_to_toolbelt_pure

        pd = _make_player_data()
        pd["woodcutting_level"] = 1
        pd["inventory"]["Mithril hatchet"] = 1

        def attach(item_name: str) -> bool:
            inventory, toolbelt, attached = attach_tool_to_toolbelt_pure(
                item_name,
                pd.get("inventory", {}),
                pd.get("toolbelt", {}),
                MINING_PICKAXE_DATA,
                WOODCUTTING_AXE_DATA,
            )
            if attached:
                pd["inventory"] = inventory
                pd["toolbelt"] = toolbelt
            return attached

        dialog = self._open(pd, on_attach_tool=attach)
        _open_bank_tab(dialog)
        menu = dialog._ankiscape_equip_menu_for("Mithril hatchet")
        action = next(
            candidate
            for candidate in menu.actions()
            if candidate.objectName() == "attachToolbeltAction"
        )
        self.assertEqual(action.text(), "Attach Mithril hatchet to toolbelt")
        self.assertTrue(action.isEnabled())

        action.trigger()
        QApplication.processEvents()

        self.assertNotIn("Mithril hatchet", pd["inventory"])
        self.assertIn("mithril_hatchet", pd["toolbelt"]["woodcutting"])
        gear_list = dialog.findChild(QListWidget, "gearList")
        self.assertTrue(
            any("Mithril hatchet — needs Woodcutting 21" == text for text in _list_texts(gear_list))
        )

    def test_bank_breaks_runecrafting_tablets_through_the_direct_action(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Air altar teleport": 2}
        used: list[str] = []

        def _use(item_name: str):
            used.append(item_name)
            pd["inventory"][item_name] -= 1
            return {"ok": True}

        dialog = self._open(
            pd,
            on_use_great_orb_project_teleport_tablet=_use,
        )
        row = _bank_grid_button(dialog, "Air altar teleport")
        self.assertFalse(row.icon().isNull())
        menu = dialog._ankiscape_equip_menu_for("Air altar teleport")
        action = next(
            action
            for action in menu.actions()
            if action.text() == "Break Air altar teleport"
        )
        self.assertEqual(
            action.objectName(), "breakRunecraftingTeleportTabletAction"
        )
        self.assertIn("skips its outbound leg", action.toolTip())
        action.trigger()
        QApplication.processEvents()
        self.assertEqual(used, ["Air altar teleport"])
        self.assertEqual(pd["inventory"]["Air altar teleport"], 1)

    def test_bank_offers_drink_action_for_consumables(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Beer": 2}
        pd["strength_level"] = 50
        pd["attack_level"] = 60
        pd["combat_lifepoints"] = 30
        consumed: list[str] = []

        def _consume(item_name: str):
            from ankiscape.logic_pure.logic_pure import apply_consumable_pure
            new_data, result = apply_consumable_pure(pd, item_name)
            if result.get("allowed"):
                pd.clear()
                pd.update(new_data)
                consumed.append(item_name)
                return result
            return None

        self._captured.clear()
        self._ui.show_main_menu(
            player_data=pd,
            current_skill="Mining",
            on_save_skill=lambda *a: None,
            on_set_ore=lambda *a: None,
            on_set_tree=lambda *a: None,
            on_set_bar=lambda *a: None,
            on_set_smith=lambda *a: None,
            on_set_craft=lambda *a: None,
            on_set_fletch=lambda *a: None,
            on_set_firemaking=lambda *a: None,
            on_set_fishing=lambda *a: None,
            on_set_cooking=lambda *a: None,
            on_set_utility=lambda *a: None,
            on_discard_item=lambda *a: True,
            on_consume_item=_consume,
        )
        dialog = self._captured[-1]
        menu = dialog._ankiscape_equip_menu_for("Beer")
        drink = next(a for a in menu.actions() if a.text() == "Drink Beer")
        self.assertTrue(drink.isEnabled())

        original_info = self._ui.QMessageBox.information
        self._ui.QMessageBox.information = lambda *a, **k: None
        try:
            drink.trigger()
            QApplication.processEvents()
        finally:
            self._ui.QMessageBox.information = original_info

        self.assertEqual(consumed, ["Beer"])
        self.assertEqual(pd["inventory"]["Beer"], 1)
        self.assertEqual(pd["combat_current_levels"], {"strength": 52, "attack": 56})

    def test_bank_uses_edible_verb_and_opens_all_supply_packs(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Summer pie": 1, "Vial pack": 2}
        opened: list[tuple[str, bool]] = []

        self._captured.clear()
        self._ui.show_main_menu(
            player_data=pd,
            current_skill="Mining",
            on_save_skill=lambda *a: None,
            on_set_ore=lambda *a: None,
            on_set_tree=lambda *a: None,
            on_set_bar=lambda *a: None,
            on_set_smith=lambda *a: None,
            on_set_craft=lambda *a: None,
            on_set_fletch=lambda *a: None,
            on_set_firemaking=lambda *a: None,
            on_set_fishing=lambda *a: None,
            on_set_cooking=lambda *a: None,
            on_set_utility=lambda *a: None,
            on_discard_item=lambda *a: True,
            on_consume_item=lambda *_args: None,
            on_open_item_pack=lambda item_name, open_all: opened.append((item_name, open_all)) or True,
        )
        dialog = self._captured[-1]

        pie_menu = dialog._ankiscape_equip_menu_for("Summer pie")
        self.assertTrue(any(action.text() == "Eat Summer pie" for action in pie_menu.actions()))

        pack_menu = dialog._ankiscape_equip_menu_for("Vial pack")
        open_all = next(action for action in pack_menu.actions() if action.text() == "Open all (2)")
        self.assertEqual(open_all.toolTip(), "Receive 100 Vial.")
        open_all.trigger()
        QApplication.processEvents()
        self.assertEqual(opened, [("Vial pack", True)])

    def test_bank_loots_filled_impling_jars(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Dragon impling jar": 1}
        looted: list[str] = []

        dialog = self._open(
            pd,
            on_open_impling_jar=lambda item_name: looted.append(item_name)
            or {"message": "You loot 105 Dragon dart tip."},
        )
        menu = dialog._ankiscape_equip_menu_for("Dragon impling jar")
        loot = next(action for action in menu.actions() if action.text() == "Loot Dragon impling jar")
        self.assertEqual(loot.objectName(), "lootImplingJarAction")
        self.assertTrue(loot.isEnabled())

        original_info = self._ui.QMessageBox.information
        self._ui.QMessageBox.information = lambda *a, **k: None
        try:
            loot.trigger()
            QApplication.processEvents()
        finally:
            self._ui.QMessageBox.information = original_info
        self.assertEqual(looted, ["Dragon impling jar"])

    def test_bank_converts_a_rogue_kit_to_any_period_tool(self) -> None:
        from ankiscape.logic.flash_powder_factory_logic import convert_rogue_kit_pure

        pd = _make_player_data()
        pd["inventory"] = {"Rogue kit": 2}
        converted: list[str] = []

        def _convert(output_item: str) -> bool:
            updated, ok, _info = convert_rogue_kit_pure(pd, output_item)
            if ok:
                pd.clear()
                pd.update(updated)
                converted.append(output_item)
            return ok

        dialog = self._open(pd, on_convert_rogue_kit=_convert)
        menu = dialog._ankiscape_equip_menu_for("Rogue kit")
        convert_action = next(
            action for action in menu.actions()
            if action.text() == "Convert Rogue kit to"
        )
        convert_menu = convert_action.menu()
        self.assertIsNotNone(convert_menu)
        self.assertEqual(
            [action.text() for action in convert_menu.actions()],
            ["Chisel", "Rope", "Tinderbox", "Spade"],
        )
        next(
            action for action in convert_menu.actions() if action.text() == "Rope"
        ).trigger()
        QApplication.processEvents()
        self.assertEqual(converted, ["Rope"])
        self.assertEqual(pd["inventory"]["Rogue kit"], 1)
        self.assertEqual(pd["inventory"]["Rope"], 1)

    def test_full_urn_bank_action_uses_stable_id_order_and_refreshes_immediately(self) -> None:
        from ankiscape.logic_pure.logic_pure import teleport_full_urn_pure
        from ankiscape.data.urn_data import URN_TIERS_BY_ID

        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        pd = _make_player_data()
        pd["mining_level"] = 1
        pd["mining_exp"] = 0.0
        pd.update(
            {
                "inventory": {tier.item_full: 1},
                "current_ore": "copper",
                "carried_inventory": {"copper": {tier.item_full: 1}},
            }
        )
        teleports: list[str] = []

        def _teleport(urn_id: str) -> bool:
            updated, _xp, ok, _skill_id = teleport_full_urn_pure(pd, urn_id)
            if ok:
                updated["mining_exp"] = tier.teleport_xp
                updated["mining_level"] = 2
                pd.clear()
                pd.update(updated)
                teleports.append(urn_id)
            return ok

        dialog = self._open(
            pd,
            current_skill="Mining",
            carried_pack_target_active=True,
            carried_advanced_state=True,
            on_set_carried_advanced=lambda _enabled: None,
            on_set_carried_layout_quantity=lambda _name, _quantity: True,
            on_teleport_training_urn=_teleport,
            on_discard_item=lambda _item, _quantity: True,
        )
        row = _bank_grid_button(dialog, tier.item_full)
        self.assertEqual(row.property("bankUrnId"), tier.id)
        self.assertIn(f"{tier.teleport_xp:g} Mining XP", row.toolTip())
        self.assertIn("Ready in the carried pack", row.toolTip())
        self.assertEqual(_panel_title(dialog), "Mining — Lv 1")

        menu = dialog._ankiscape_equip_menu_for(tier.item_full)
        actions = [action for action in menu.actions() if not action.isSeparator()]
        self.assertEqual(
            [action.text() for action in actions],
            ["Teleport urn", "Set carried quantity…", "Discard X…", "Organize"],
        )
        teleport = actions[0]
        self.assertEqual(teleport.objectName(), "teleportTrainingUrnAction")
        self.assertEqual(teleport.data(), tier.id)
        self.assertTrue(teleport.isEnabled())
        teleport.trigger()
        for _ in range(4):
            QApplication.processEvents()

        self.assertEqual(teleports, [tier.id])
        self.assertEqual(pd["mining_level"], 2)
        self.assertEqual(_panel_title(dialog), "Mining — Lv 2")
        self.assertFalse(
            any(button.property("bankItemName") == tier.item_full for button in _bank_grid_buttons(dialog))
        )
        dialog.deleteLater()

    def test_bank_drinks_each_trouble_brewing_rum_through_its_direct_action(self) -> None:
        pd = _make_player_data()
        pd["inventory"].update({"Red rum": 1, "Blue rum": 1})
        used = []

        def _drink(item_name):
            used.append(item_name)
            pd["inventory"].pop(item_name)
            return {"ok": True, "destination": "Trouble Brewing"}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_drink_trouble_brewing_rum=_drink,
        )
        for item_name in ("Red rum", "Blue rum"):
            menu = dialog._ankiscape_equip_menu_for(item_name)
            action = next(
                action
                for action in menu.actions()
                if action.objectName() == "drinkTroubleBrewingRumAction"
            )
            self.assertEqual(action.text(), f"Drink {item_name}")
            self.assertEqual(
                action.toolTip(),
                "Teleport to Trouble Brewing. Consumes one bottle.",
            )
            self.assertTrue(action.isEnabled())
            self.assertTrue(menu.toolTipsVisible())
            action.trigger()
            QApplication.processEvents()
        self.assertEqual(used, ["Red rum", "Blue rum"])

        pd["inventory"]["Red rum"] = 1
        pd["trouble_brewing"] = {"review": 0}
        active_menu = dialog._ankiscape_equip_menu_for("Red rum")
        active_action = next(
            action
            for action in active_menu.actions()
            if action.objectName() == "drinkTroubleBrewingRumAction"
        )
        self.assertFalse(active_action.isEnabled())
        self.assertIn("Finish or leave", active_action.toolTip())
        dialog.close()

    def test_bank_context_action_starts_a_trail_and_unlocks_its_card(self) -> None:
        from ankiscape.logic.treasure_trails_logic import (
            apply_treasure_trails_command_pure,
            default_treasure_trails_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_treasure_trails_state_pure())
        pd["inventory"] = {"Clue scroll (easy)": 1}
        pd["equipment"] = {}
        pd["activity_session"] = {"active_id": ""}
        command_calls = []

        def trails_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_treasure_trails_command_pure(
                pd, action_id, payload, lambda: 0.0
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_treasure_trails_command=trails_command,
        )
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(4):
            QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "treasure_trail"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "treasureTrailsPanel")
            if widget.isVisible()
        )
        read_button = panel.findChild(QPushButton, "treasureTrailsPrimary")
        self.assertFalse(read_button.isEnabled())
        self.assertIn(
            "Right-click the clue in the Bank",
            panel.findChild(QLabel, "treasureTrailsSummary").text(),
        )

        menu = dialog._ankiscape_equip_menu_for("Clue scroll (easy)")
        start_action = next(
            action for action in menu.actions() if action.text() == "Start trail"
        )
        self.assertEqual(start_action.objectName(), "startTreasureTrailAction")
        self.assertEqual(start_action.data(), "easy")
        self.assertTrue(start_action.isEnabled())
        start_action.trigger()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("start_from_bank", {"tier": "easy"}))
        tree.itemClicked.emit(item, 0)
        for _ in range(4):
            QApplication.processEvents()
        self.assertIn(
            "Following an easy trail",
            panel.findChild(QLabel, "treasureTrailsSummary").text(),
        )
        self.assertFalse(read_button.isEnabled())

        # Finish the trail outside the panel, the way ordinary reviews would.
        from ankiscape.logic.treasure_trails_logic import (
            apply_treasure_trail_review_pure,
        )

        while pd["treasure_trail"]:
            updated, ok, _result = apply_treasure_trail_review_pure(pd)
            self.assertTrue(ok)
            pd.clear()
            pd.update(updated)
        # Leave the card and come back, the way a player does after reviewing.
        casket = panel.findChild(QPushButton, "treasureTrailsCasket")
        dialog.findChild(QPushButton, "activityChooseAnotherButton").click()
        QApplication.processEvents()
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        self.assertTrue(casket.isEnabled())
        casket.click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "open_casket")
        self.assertNotIn("Casket (easy)", pd["inventory"])
        self.assertFalse(casket.isEnabled())
        dialog.close()
