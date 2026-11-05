from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _ADDON_DIR,
    _find_artisan_skill_list,
    _find_tree_with_user_role,
    _icon_pixels,
    _make_player_data,
    _smith_tree_items,
    _tree_row,
    os,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QIcon, QPushButton, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_overload_row_has_rs_wiki_icon_inputs_and_vial_byproduct(self) -> None:
        pd = _make_player_data()
        pd["herblore_level"] = 96
        pd["current_herblore"] = "finished_overload"
        pd["inventory"] = {
            "Extreme attack (3)": 1,
            "Extreme strength (3)": 1,
            "Extreme defence (3)": 1,
            "Extreme magic (3)": 1,
            "Extreme ranging (3)": 1,
            "Clean torstol": 1,
        }
        dialog = self._open(pd, current_skill="Herblore")
        artisan = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        herblore_row = next(
            index for index in range(skill_list.count()) if skill_list.item(index).text() == "Herblore"
        )
        skill_list.setCurrentRow(herblore_row)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "finished_overload")
        overload = _tree_row(tree, "finished_overload")

        self.assertFalse(overload.isDisabled())
        self.assertFalse(overload.icon(0).isNull())
        self.assertIn("Base XP: 1000", overload.toolTip(0))
        self.assertIn("Byproduct: Vial x4", overload.toolTip(0))
        self.assertIn("Extreme ranging (3) x1", overload.toolTip(0))

    def test_herblore_uses_its_skill_icon_and_icons_every_overworld_action(self) -> None:
        pd = _make_player_data()
        pd["herblore_level"] = 99
        pd["current_herblore"] = "clean_guam"
        dialog = self._open(pd, current_skill="Herblore")
        artisan = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        herblore_item = next(
            skill_list.item(index)
            for index in range(skill_list.count())
            if skill_list.item(index).text() == "Herblore"
        )
        skill_list.setCurrentItem(herblore_item)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "clean_guam")
        clean_group = _tree_row(tree, "__herblore_group__:clean")
        unf_group = _tree_row(tree, "__herblore_group__:unf")
        finished_group = _tree_row(tree, "__herblore_group__:finished")

        self.assertFalse(herblore_item.icon().isNull())
        self.assertEqual(
            _icon_pixels(herblore_item.icon()),
            _icon_pixels(QIcon(self._ui.skill_icon_path_for("Herblore"))),
        )
        self.assertNotEqual(
            _icon_pixels(herblore_item.icon()),
            _icon_pixels(QIcon(os.path.join(_ADDON_DIR, "icon", "achievement_icon.png"))),
        )
        self.assertEqual(clean_group.childCount(), 27)
        self.assertEqual(unf_group.childCount(), 22)
        self.assertEqual(finished_group.childCount(), 70)
        action_rows = [
            item
            for item in _smith_tree_items(tree)
            if not str(item.data(0, Qt.ItemDataRole.UserRole)).startswith("__herblore_group__:")
        ]
        self.assertEqual(len(action_rows), 119)
        self.assertTrue(all(not item.icon(0).isNull() for item in action_rows))
        self.assertNotIn(
            "clean_sagawort",
            {item.data(0, Qt.ItemDataRole.UserRole) for item in _smith_tree_items(tree)},
        )

    def test_shrink_me_quick_row_exposes_recipe_lock_icon_and_selection(self) -> None:
        pd = _make_player_data()
        pd["herblore_level"] = 52
        pd["current_herblore"] = "clean_guam"
        dialog = self._open(pd, current_skill="Herblore")
        artisan = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        herblore_item = next(
            skill_list.item(index)
            for index in range(skill_list.count())
            if skill_list.item(index).text() == "Herblore"
        )
        skill_list.setCurrentItem(herblore_item)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "finished_shrink_me_quick")
        row = _tree_row(tree, "finished_shrink_me_quick")

        self.assertFalse(row.isDisabled())
        self.assertFalse(row.icon(0).isNull())
        self.assertIn("Base XP: 6", row.toolTip(0))
        self.assertIn("Tarromin potion (unf) x1", row.toolTip(0))
        self.assertIn("Shrunk ogleroot x1", row.toolTip(0))

        before = list(self._herblore_calls)
        tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._herblore_calls, before)

        pd["inventory"] = {
            "Tarromin potion (unf)": 1,
            "Shrunk ogleroot": 1,
        }
        dialog = self._open(pd, current_skill="Herblore")
        artisan = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        herblore_item = next(
            skill_list.item(index)
            for index in range(skill_list.count())
            if skill_list.item(index).text() == "Herblore"
        )
        skill_list.setCurrentItem(herblore_item)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "finished_shrink_me_quick")
        row = _tree_row(tree, "finished_shrink_me_quick")
        self.assertFalse(row.isDisabled())

        tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._herblore_calls[-1], "finished_shrink_me_quick")
