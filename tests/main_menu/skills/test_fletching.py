from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_artisan_skill_list,
    _find_fletching_tree,
    _fletching_group_node,
    _fletching_row,
    _make_player_data,
    _panel_title,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QPushButton
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_fletching_is_selectable_and_shows_grouped_target_tree(self) -> None:
        pd = _make_player_data()
        pd["fletching_level"] = 99
        pd["inventory"] = {
            "Logs": 1,
            "Headless arrows": 15,
            "Broad arrow heads": 15,
            "Long kebbit spike": 1,
            "Chisel": 1,
        }
        pd["current_fletch"] = "arrow_shafts"
        dialog = self._open(pd)

        artisan = next(b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        fletch_row = next(
            (i for i in range(skill_list.count()) if skill_list.item(i).text() == "Fletching"),
            None,
        )
        self.assertIsNotNone(fletch_row, "Fletching is missing from the Artisan skill list")
        skill_list.setCurrentRow(fletch_row)
        QApplication.processEvents()
        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Fletching"),
            f"panel did not switch to Fletching; still shows {title!r}",
        )
        tree = _find_fletching_tree(dialog)
        self.assertEqual(_fletching_group_node(tree, "whittling").text(0), "Whittling  (20)")
        self.assertIs(_fletching_row(tree, "arrow_shafts"), tree.currentItem())
        self.assertFalse(_fletching_row(tree, "arrow_shafts").isDisabled())
        broad = _fletching_row(tree, "broad_arrows")
        self.assertTrue(broad.isDisabled())
        self.assertIn("Broad Fletching", broad.toolTip(0))
        long_kebbit = _fletching_row(tree, "fletch_long_kebbit_bolts")
        self.assertFalse(long_kebbit.isDisabled())
        self.assertIn("Long kebbit spike x1", long_kebbit.toolTip(0))
        self.assertNotIn("Chisel x1", long_kebbit.toolTip(0))
