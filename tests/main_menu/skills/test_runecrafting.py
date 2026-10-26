from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _goto_runecrafting,
    _make_player_data,
    _panel_title,
    _runecrafting_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_runecrafting_is_selectable_and_shows_grouped_targets(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 23
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        pd["inventory"] = {
            "Rune essence": 31,
            "Air talisman": 1,
            "Pure essence": 26,
            "Fire rune": 26,
            "Fire talisman": 1,
            "Runecrafting staff": 1,
        }
        pd["equipment"] = {"head": "Earth tiara"}
        dialog = self._open(pd)
        tree = _goto_runecrafting(dialog)

        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Runecrafting"),
            f"panel did not switch to Runecrafting; still shows {title!r}",
        )
        group_roles = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__runecrafting_group__:standard", group_roles)
        self.assertIn("__runecrafting_group__:combination", group_roles)
        self.assertIn("__runecrafting_group__:tiara", group_roles)
        self.assertIn("__runecrafting_group__:staff", group_roles)
        self.assertNotIn("__runecrafting_group__:hood", group_roles)

        air = _runecrafting_row(tree, "craft_air_runes")
        lava = _runecrafting_row(tree, "combo_lava_at_earth")
        blood = _runecrafting_row(tree, "craft_blood_runes")
        air_staff = _runecrafting_row(tree, "bind_air_talisman_staff")
        self.assertFalse(air.isDisabled())
        self.assertFalse(lava.isDisabled())
        self.assertFalse(air_staff.isDisabled())
        self.assertTrue(blood.isDisabled())
        self.assertFalse(air.icon(0).isNull(), "Runecrafting target row has no icon")
        self.assertIn("Output: Air rune", air.toolTip(0))
        self.assertIn("Pure essence", lava.toolTip(0))
        self.assertFalse(air_staff.icon(0).isNull())
        self.assertIn("Permanently binds", air_staff.toolTip(0))
        self.assertIn("Runecrafting staff (1)", air_staff.toolTip(0))
        self.assertIn("Locked due to:", blood.toolTip(0))

        tree.itemClicked.emit(air, 0)
        QApplication.processEvents()
        self.assertEqual(self._runecrafting_calls[-1], "craft_air_runes")

    def test_runecrafting_locked_rows_are_inert(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 1
        pd["inventory"] = {"Rune essence": 28}
        dialog = self._open(pd)
        tree = _goto_runecrafting(dialog)
        air = _runecrafting_row(tree, "craft_air_runes")

        self.assertTrue(air.isDisabled())
        self.assertIn("Rune Mysteries", air.toolTip(0))
        before = list(self._runecrafting_calls)
        tree.itemClicked.emit(air, 0)
        tree.itemActivated.emit(air, 0)
        QApplication.processEvents()
        self.assertEqual(self._runecrafting_calls, before, "locked runecrafting target must not be selectable")
