from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_list_with_item_prefix,
    _find_main_tabs,
    _find_skill_list,
    _list_texts,
    _make_player_data,
    _open_ge_tab,
    _tree_items,
    _utility_row,
    cached_property,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QEvent, QListWidget, QPushButton, QTreeWidget, QWidget, Qt
from tests.main_menu import dialog_factory


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(dialog_factory.DialogFactory, unittest.TestCase):
    app: "QApplication"

    dialog = cached_property(lambda self: self._open(_make_player_data(), current_skill="Mining"))

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        from ankiscape.ui import ui
        from ankiscape.logic.combat_session import reset_wilderness_combat_confirmations

        reset_wilderness_combat_confirmations()
        self._preexisting_windows = set(QApplication.topLevelWidgets())
        self._captured: list = []
        # Records recipe IDs the Smithing list persists via on_set_smith so tests
        # can assert selection wiring without real mouse events.
        self._smith_calls: list = []
        # Same seam for the family-grouped Crafting tree (on_set_craft).
        self._craft_calls: list = []
        self._skilling_potion_calls: list = []
        # Same seams for Utility/Activities selection and activation.
        self._utility_calls: list = []
        self._activity_start_calls: list = []
        # Same seam for Firemaking target selection.
        self._firemaking_calls: list = []
        # Same seam for Fishing target selection.
        self._fishing_calls: list = []
        # Same seam for Hunter target selection.
        self._hunter_calls: list = []
        # Same seam for Cooking target selection.
        self._cooking_calls: list = []
        # Same seam for Runecrafting target selection.
        self._runecrafting_calls: list = []
        self._herblore_calls: list = []
        # Same seams for Combat target/style/spell selection.
        self._combat_calls: list = []
        self._combat_action_calls: list = []
        self._combat_style_calls: list = []
        self._combat_spell_calls: list = []
        self._combat_threshold_calls: list = []
        self._combat_food_calls: list = []
        self._combat_refill_calls: list = []
        self._combat_unload_calls: list = []
        self._prayer_calls: list = []
        self._magic_calls: list = []
        self._construction_calls: list = []
        self._thieving_calls: list = []
        self._agility_calls: list = []
        self._summoning_calls: list = []
        self._slayer_command_calls: list = []
        self._agility_command_calls: list = []
        self._warriors_guild_calls: list = []
        self._livid_farm_calls: list = []
        self._big_chinchompa_calls: list = []
        self._shooting_star_calls: list = []
        self._fist_of_guthix_calls: list = []
        self._sorceress_garden_calls: list = []
        self._penguin_calls: list = []
        self._vinesweeper_calls: list = []
        self._fight_caves_calls: list = []
        self._dagannoth_kings_calls: list = []
        self._phoenix_lair_calls: list = []
        self._skeletal_horror_calls: list = []
        self._tears_of_guthix_calls: list = []
        self._enchanted_key_calls: list = []
        self._barrows_calls: list = []
        self._stealing_creation_calls: list = []
        self._fish_flingers_calls: list = []
        self._fishing_trawler_calls: list = []
        self._great_orb_project_calls: list = []
        self._managing_miscellania_calls: list = []
        self._thieving_fight_back_calls: list = []
        self._farming_calls: list = []
        self._mage_arena_calls: list = []
        self._magic_alch_calls: list = []
        self._farming_spell_patch_calls: list = []
        self._prayer_config_calls: list = []
        self._death_office_calls: list = []
        # Quests and Bank Claims are review-adjacent but not levelled skills.
        self._quest_calls: list = []
        self._quest_choice_calls: list = []
        self._claim_calls: list = []
        # Seam for the Stronghold of Security landmark's "claim reward" click.
        self._stronghold_claim_calls: list = []

        # Intercept through a subclass: restoring a monkeypatched PyQt method
        # descriptor with setattr permanently corrupts its binding in this process.
        self._orig_dialog = ui.QDialog
        captured = self._captured

        class CapturingDialog(self._orig_dialog):
            def exec(instance):  # type: ignore[no-untyped-def]
                captured.append(instance)
                return 0

        ui.QDialog = CapturingDialog

        # Developer mode on so the registry surfaces every category/skill.
        self._orig_cfg = ui.get_config_bool
        ui.get_config_bool = lambda key, default=True: (
            True if key == "ankiscape_developer_mode" else default
        )

        self._ui = ui

    def tearDown(self) -> None:
        self._ui.QDialog = self._orig_dialog
        self._ui.get_config_bool = self._orig_cfg
        # Detached panels outlive their dialog, and every later app-wide restyle repolishes leaked windows.
        for window in set(QApplication.topLevelWidgets()) - self._preexisting_windows:
            window.deleteLater()
        QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def _goto_slayer(self, dialog: "QDialog") -> None:
        next(
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == "Support"
        ).click()
        QApplication.processEvents()
        skill_list = next(
            widget
            for widget in dialog.findChildren(QListWidget)
            if "Slayer" in _list_texts(widget)
        )
        row = _list_texts(skill_list).index("Slayer")
        skill_list.setCurrentRow(row)
        QApplication.processEvents()

    def _open_ge_with_active_buy_offer(self):
        from ankiscape.logic.grand_exchange_logic import (
            apply_ge_frontend_action_pure,
            ge_frontend_projection_pure,
        )

        player = _make_player_data()
        player["inventory"] = {"Coins": 100_000}
        catalog = {
            "Logs": {
                "guide_price": 200,
                "buy_limit": 25_000,
                "tradeable": True,
                "exchangeable": True,
                "category": "logs",
            }
        }
        updated, placed = apply_ge_frontend_action_pure(
            player,
            "place_offer",
            {"side": "buy", "item_name": "Logs", "quantity": 7, "unit_price": 1_234},
            item_catalog=catalog,
        )
        self.assertTrue(placed.get("ok"), placed)
        player.clear()
        player.update(updated)
        calls = []

        def projection():
            return ge_frontend_projection_pure(player, item_catalog=catalog)

        def action(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated_player, info = apply_ge_frontend_action_pure(
                player,
                action_id,
                payload,
                item_catalog=catalog,
            )
            if info.get("ok") and action_id != "preview_offer":
                player.clear()
                player.update(updated_player)
            return {**info, "projection": projection()}

        dialog = self._open(
            player,
            get_ge_projection=projection,
            on_ge_action=action,
        )
        _open_ge_tab(dialog)
        return dialog, player, calls

    def _open_with_equip(self, pd: dict) -> "QDialog":
        """Open the menu with equip/unequip wired to the real pure logic.

        The frontend test seam mirrors what __init__.on_equip_item /
        on_unequip_slot do (run the pure mutation, persist into player_data) so
        the menu -> handler -> refresh contract is exercised end to end without
        Anki's global state.
        """
        from ankiscape.logic_pure.logic_pure import equip_item_pure, unequip_item_pure
        from ankiscape.core.constants import EQUIPMENT_ITEM_DATA

        def _equip(item_name: str) -> bool:
            inv, equipment, ok = equip_item_pure(
                item_name,
                pd.get("inventory", {}) or {},
                pd.get("equipment", {}) or {},
                EQUIPMENT_ITEM_DATA,
            )
            if ok:
                pd["inventory"] = inv
                pd["equipment"] = equipment
            return ok

        def _unequip(slot: str) -> bool:
            inv, equipment, ok = unequip_item_pure(
                slot,
                pd.get("inventory", {}) or {},
                pd.get("equipment", {}) or {},
            )
            if ok:
                pd["inventory"] = inv
                pd["equipment"] = equipment
            return ok

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
            on_set_fishing=lambda *a: None,
            on_set_utility=lambda *a: None,
            on_equip_item=_equip,
            on_unequip_slot=_unequip,
        )
        self.assertTrue(self._captured, "show_main_menu did not call dialog.exec()")
        return self._captured[-1]

    def _open_no_xp_surface(
        self, dialog: "QDialog", surface_name: str
    ) -> "QTreeWidget":
        tabs = _find_main_tabs(dialog)
        skills_index = next(
            index for index in range(tabs.count()) if tabs.tabText(index) == "Skills"
        )
        tabs.setCurrentIndex(skills_index)
        QApplication.processEvents()
        cat = next(
            b for b in dialog.findChildren(QPushButton) if b.text() == surface_name
        )
        cat.click()
        QApplication.processEvents()
        expected_target = (
            "livid_farm" if surface_name == "Activities" else "make_soft_clay"
        )
        for tree in dialog.findChildren(QTreeWidget):
            if any(
                item.data(0, Qt.ItemDataRole.UserRole) == expected_target
                for item in _tree_items(tree)
            ):
                return tree
        raise AssertionError(
            f"{surface_name} tree with {expected_target!r} was not found"
        )

    def _open_utility(self, dialog: "QDialog") -> "QTreeWidget":
        return self._open_no_xp_surface(dialog, "Utilities")

    def _open_activities(self, dialog: "QDialog") -> "QTreeWidget":
        return self._open_no_xp_surface(dialog, "Activities")

    def _open_activity_detail(
        self, dialog: "QDialog", activity_id: str
    ) -> "QTreeWidget":
        tree = self._open_activities(dialog)
        row = _utility_row(tree, activity_id)
        tree.setCurrentItem(row)
        tree.itemActivated.emit(row, 0)
        QApplication.processEvents()
        return tree

    def _open_circus_panel(self, dialog: "QDialog") -> "QWidget":
        self._open_activity_detail(dialog, "big_top_bonanza")
        return next(
            panel
            for panel in dialog.findChildren(QWidget, "circusPanel")
            if panel.isVisible()
        )

    def _open_woodcutting(self, dialog: "QDialog") -> "QListWidget":
        skill_list = _find_skill_list(dialog)
        wc_row = next(
            i for i in range(skill_list.count()) if skill_list.item(i).text() == "Woodcutting"
        )
        skill_list.setCurrentRow(wc_row)
        QApplication.processEvents()
        return _find_list_with_item_prefix(dialog, "Oak ")

    def _wc_row(self, tree_list: "QListWidget", prefix: str) -> "QListWidgetItem":
        return next(
            tree_list.item(i) for i in range(tree_list.count())
            if tree_list.item(i).text().removeprefix("✓ ").startswith(prefix)
        )

    def _open_mining(self, dialog: "QDialog") -> "QListWidget":
        skill_list = _find_skill_list(dialog)
        mining_row = next(
            i for i in range(skill_list.count()) if skill_list.item(i).text() == "Mining"
        )
        skill_list.setCurrentRow(mining_row)
        QApplication.processEvents()
        # Copper is a stable, always-present low-level rock row.
        return _find_list_with_item_prefix(dialog, "Copper ")

    def _ore_row(self, ore_list: "QListWidget", prefix: str) -> "QListWidgetItem":
        return next(
            ore_list.item(i) for i in range(ore_list.count())
            if ore_list.item(i).text().removeprefix("✓ ").startswith(prefix)
        )
