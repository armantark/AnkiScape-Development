from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_list_with_user_role,
    _find_skill_list,
    _make_player_data,
    _panel_title,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_fishing_is_selectable_and_shows_output_first_target_list(self) -> None:
        pd = _make_player_data()
        pd["fishing_level"] = 48
        pd["strength_level"] = 15
        pd["agility_level"] = 15
        pd["inventory"] = {"Fishing bait": 2, "Feather": 1}
        pd["current_fishing"] = "catch_sardine_herring"
        dialog = self._open(pd)

        skill_list = _find_skill_list(dialog)
        fishing_row = next(
            (i for i in range(skill_list.count()) if skill_list.item(i).text() == "Fishing"),
            None,
        )
        self.assertIsNotNone(fishing_row, "Fishing is missing from the Gathering skill list")
        skill_list.setCurrentRow(fishing_row)
        QApplication.processEvents()

        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Fishing"),
            f"panel did not switch to Fishing; still shows {title!r}",
        )
        target_list = _find_list_with_user_role(dialog, "catch_sardine_herring")
        sardine_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_sardine_herring"
        )
        mackerel_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_mackerel_cod_bass"
        )
        crayfish_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_crayfish"
        )
        cave_eel_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_cave_eel"
        )

        self.assertTrue(crayfish_row.text().startswith("Catch crayfish"))
        self.assertEqual(sardine_row.text(), "✓ Catch sardine (Lvl 5) +1 more")
        self.assertEqual(mackerel_row.text(), "Catch mackerel (Lvl 16) +2 more")
        self.assertEqual(cave_eel_row.text(), "Catch slimy eel (Lvl 28) +1 more (Lumbridge Swamp Caves)")
        self.assertFalse(cave_eel_row.icon().isNull())
        tip = sardine_row.toolTip()
        self.assertIn("Outputs: Raw sardine", tip)
        self.assertIn("Raw herring", tip)
        self.assertIn("Base XP: 20-30 per catch", tip)
        self.assertIn("Materials: Fishing bait x1 (you have 2)", tip)
        self.assertNotIn("rod", tip.lower())
        self.assertNotIn("net", tip.lower())
        self.assertNotIn("harpoon", tip.lower())

        target_list.itemClicked.emit(crayfish_row)
        QApplication.processEvents()
        self.assertEqual(self._fishing_calls[-1], "catch_crayfish")

    def test_fishing_locked_rows_are_inert_and_explain_material_or_side_gate(self) -> None:
        pd = _make_player_data()
        pd["fishing_level"] = 48
        pd["strength_level"] = 1
        pd["agility_level"] = 1
        pd["inventory"] = {}
        dialog = self._open(pd)

        skill_list = _find_skill_list(dialog)
        fishing_row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Fishing")
        skill_list.setCurrentRow(fishing_row)
        QApplication.processEvents()
        target_list = _find_list_with_user_role(dialog, "catch_sardine_herring")
        bait_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_sardine_herring"
        )
        leaping_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "catch_leaping_fish"
        )

        self.assertFalse(bait_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("materials", bait_row.toolTip())
        self.assertFalse(leaping_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("side levels", leaping_row.toolTip())
        target_list.itemClicked.emit(bait_row)
        target_list.itemClicked.emit(leaping_row)
        QApplication.processEvents()
        self.assertEqual(self._fishing_calls, [])
