from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_tree_with_user_role,
    _icon_pixels,
    _make_player_data,
    _smith_tree_items,
    _tree_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QIcon, QListWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_summoning_uses_canonical_icon_and_complete_surface_target_tree(self) -> None:
        pd = _make_player_data()
        pd["summoning_level"] = 99
        pd["inventory"] = {
            "Pouch": 1,
            "Spirit shards": 7,
            "Gold charm": 1,
            "Wolf bones": 1,
        }
        dialog = self._open(pd, current_skill="Summoning")
        skill_list = next(
            widget
            for widget in dialog.findChildren(QListWidget)
            if "Summoning" in [
                widget.item(index).text() for index in range(widget.count())
            ]
        )
        summoning_item = next(
            skill_list.item(index)
            for index in range(skill_list.count())
            if skill_list.item(index).text() == "Summoning"
        )
        skill_list.setCurrentItem(summoning_item)
        QApplication.processEvents()
        tree = _find_tree_with_user_role(dialog, "infuse_spiritwolf")
        infuse_group = _tree_row(
            tree, "__summoning_group__:Infuse pouches"
        )
        scroll_group = _tree_row(
            tree, "__summoning_group__:Create scrolls"
        )

        self.assertFalse(summoning_item.icon().isNull())
        self.assertEqual(
            _icon_pixels(summoning_item.icon()),
            _icon_pixels(QIcon(self._ui.skill_icon_path_for("Summoning"))),
        )
        self.assertEqual(infuse_group.childCount(), 78)
        self.assertEqual(scroll_group.childCount(), 67)
        rows = [
            item
            for item in _smith_tree_items(tree)
            if not str(
                item.data(0, Qt.ItemDataRole.UserRole)
            ).startswith("__summoning_group__:")
        ]
        self.assertEqual(len(rows), 145)
        self.assertTrue(all(not item.icon(0).isNull() for item in rows))
