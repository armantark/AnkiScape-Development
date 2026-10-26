from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _ADDON_DIR,
    _bank_grid_button,
    _bank_grid_texts,
    _find_bank_grid,
    _find_gear_list,
    _icon_pixels,
    _make_player_data,
    os,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QIcon, QPushButton
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_bank_groups_fletched_and_material_items_with_icons(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Logs": 5,
            "Bronze bar": 2,
            "Arrow shafts": 30,
            "Feather": 50,
            "Bronze arrowtips": 15,
        }
        dialog = self._open(pd)
        texts = _bank_grid_texts(dialog)
        for header in ("Logs", "Bars", "Fletched", "Materials"):
            self.assertIn(header, texts, f"missing bank category header {header!r}")
        self.assertTrue(any(t.startswith("Arrow shafts x30") for t in texts))
        self.assertTrue(any(t.startswith("Feather x50") for t in texts))
        # Registered fletched item should carry an icon from its ItemDefinition.
        arrow_row = _bank_grid_button(dialog, "Arrow shafts")
        self.assertFalse(arrow_row.icon().isNull(), "Arrow shafts row has no icon")

    def test_bank_uses_the_unholy_mould_asset(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Unholy mould": 1}
        dialog = self._open(pd)

        row = _bank_grid_button(dialog, "Unholy mould")
        expected = QIcon(
            os.path.join(_ADDON_DIR, "crafteditems", "unholy_mould.png")
        )
        self.assertFalse(row.icon().isNull())
        self.assertEqual(_icon_pixels(row.icon()), _icon_pixels(expected))

    def test_bank_groups_firemaking_logs_and_ashes_with_icons(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Arctic pine logs": 3,
            "Cursed magic logs": 1,
            "Ashes": 2,
        }
        dialog = self._open(pd)
        texts = _bank_grid_texts(dialog)
        for header in ("Logs", "Materials"):
            self.assertIn(header, texts, f"missing bank category header {header!r}")
        self.assertTrue(any(t.startswith("Arctic pine logs x3") for t in texts))
        self.assertTrue(any(t.startswith("Ashes x2") for t in texts))
        ashes_row = _bank_grid_button(dialog, "Ashes")
        self.assertFalse(ashes_row.icon().isNull(), "Ashes row has no icon")

    def test_bank_groups_fish_and_bait_with_icons(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Raw crayfish": 3,
            "Raw shark": 1,
            "Fishing bait": 12,
        }
        dialog = self._open(pd)
        texts = _bank_grid_texts(dialog)
        for header in ("Fish", "Materials"):
            self.assertIn(header, texts, f"missing bank category header {header!r}")
        self.assertTrue(any(t.startswith("Raw crayfish x3") for t in texts))
        self.assertTrue(any(t.startswith("Fishing bait x12") for t in texts))
        crayfish_row = _bank_grid_button(dialog, "Raw crayfish")
        bait_row = _bank_grid_button(dialog, "Fishing bait")
        self.assertFalse(crayfish_row.icon().isNull(), "Raw crayfish row has no icon")
        self.assertFalse(bait_row.icon().isNull(), "Fishing bait row has no icon")

    def test_bank_groups_runecrafting_items_with_icons(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Air rune": 120,
            "Air talisman": 1,
            "Small pouch": 1,
            "Binding necklace": 1,
            "Wicked hood": 1,
        }
        dialog = self._open(pd)
        texts = _bank_grid_texts(dialog)
        self.assertIn("Runecrafting", texts)
        for item_name in ("Air rune", "Air talisman", "Small pouch", "Binding necklace", "Wicked hood"):
            self.assertTrue(any(t.startswith(f"{item_name} x") for t in texts), f"{item_name} missing from bank")
            row = _bank_grid_button(dialog, item_name)
            self.assertFalse(row.icon().isNull(), f"{item_name} row has no icon")

    def test_bank_groups_food_with_icons_and_discard_x_prompt(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Shrimps": 3}
        discards: list[tuple[str, int]] = []

        def _discard(item_name: str, quantity: int) -> bool:
            discards.append((item_name, quantity))
            pd["inventory"][item_name] -= quantity
            return True

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
            on_discard_item=_discard,
        )
        dialog = self._captured[-1]
        texts = _bank_grid_texts(dialog)
        self.assertIn("Food", texts)
        self.assertTrue(any(t.startswith("Shrimps x3") for t in texts))
        shrimp_row = _bank_grid_button(dialog, "Shrimps")
        self.assertFalse(shrimp_row.icon().isNull(), "Shrimps row has no icon")

        menu = dialog._ankiscape_equip_menu_for("Shrimps")
        action = menu.actions()[0]
        self.assertEqual(action.text(), "Discard X…")
        self.assertTrue(action.isEnabled())

        original_get_int = self._ui.QInputDialog.getInt
        self._ui.QInputDialog.getInt = lambda *a, **k: (2, True)
        try:
            action.trigger()
            QApplication.processEvents()
        finally:
            self._ui.QInputDialog.getInt = original_get_int
        self.assertEqual(discards, [("Shrimps", 2)])
        self.assertEqual(pd["inventory"]["Shrimps"], 1)

    def test_bank_gear_lives_in_separate_panel_from_striped_inventory(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Logs": 5}
        dialog = self._open(pd)
        bank = _find_bank_grid(dialog)
        gear = _find_gear_list(dialog)
        # The gear panel must be a distinct widget from the striped inventory,
        # and must not carry the alternating-row striping.
        self.assertIsNot(gear, bank, "gear shares the inventory list")
        self.assertFalse(gear.alternatingRowColors(), "gear panel is striped")
        bank_texts = _bank_grid_texts(dialog)
        self.assertNotIn("Toolbelt", bank_texts, "Toolbelt leaked into inventory list")
        gear_texts = [gear.item(i).text() for i in range(gear.count())]
        self.assertIn("Toolbelt", dialog.findChild(QPushButton, "toolbeltHeader").text(), "missing Toolbelt header")
        self.assertTrue(any(t.startswith("Pickaxe: ") for t in gear_texts), f"no pickaxe row in {gear_texts}")
        self.assertTrue(any(t.startswith("Hatchet: ") for t in gear_texts), f"no hatchet row in {gear_texts}")
        # Worn equipment moved to its own tab; the Bank gear strip is toolbelt
        # only now and must not still carry the old "Equipped" placeholder.
        self.assertNotIn("Equipped", gear_texts, "Equipped header leaked into Bank gear strip")
        self.assertNotIn("Nothing equipped yet.", gear_texts)
        pick_row = next(
            gear.item(i) for i in range(gear.count())
            if gear.item(i).text().startswith("Pickaxe: ")
        )
        self.assertFalse(pick_row.icon().isNull(), "pickaxe gear row has no icon")
