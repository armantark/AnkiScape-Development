from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _icon_pixels,
    _make_player_data,
    _tree_items,
    _tree_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QTreeWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_magic_surface_has_bank_alchemy_picker_and_locked_click_guard(self) -> None:
        from ankiscape.core.constants import MAGIC_SPELL_IMAGES

        pd = _make_player_data()
        pd["magic_level"] = 99
        pd["inventory"] = {"Rune platebody": 1, "Air rune": 3, "Fire rune": 1, "Law rune": 1}
        pd["farming_spell_patch"] = "falador_allotment_north"
        dialog = self._open(pd, current_skill="Magic")
        picker = dialog.findChild(QComboBox, "magicAlchemyItemCombo")
        farming_picker = dialog.findChild(QComboBox, "magicFarmingPatchCombo")
        tree = dialog.findChild(QTreeWidget, "magicTargetTree")
        self.assertIsNotNone(picker)
        self.assertIsNotNone(farming_picker)
        self.assertIsNotNone(tree)
        self.assertGreaterEqual(picker.findData("Rune platebody"), 0)
        self.assertEqual(farming_picker.currentData(), "falador_allotment_north")
        self.assertEqual(farming_picker.count(), 53)
        low_alchemy = _tree_row(tree, "low_alchemy")
        self.assertFalse(low_alchemy.icon(0).isNull())
        self.assertEqual(
            _icon_pixels(low_alchemy.icon(0)),
            _icon_pixels(
                self._ui._pixel_path_icon(
                    MAGIC_SPELL_IMAGES["low_alchemy"],
                    28,
                )
            ),
        )
        farming_picker.setCurrentIndex(farming_picker.findData("falador_allotment_south"))
        QApplication.processEvents()
        self.assertEqual(self._farming_spell_patch_calls[-1], "falador_allotment_south")
        locked = next(
            item for item in _tree_items(tree)
            if item.data(0, Qt.ItemDataRole.UserRole) == "kharyrll_teleport"
        )
        self.assertTrue(locked.isDisabled())
        before = list(self._magic_calls)
        tree.itemClicked.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._magic_calls, before)

    def test_magic_alchemy_picker_refreshes_target_readiness(self) -> None:
        pd = _make_player_data()
        pd.update({
            "magic_level": 99,
            "inventory": {"Rune platebody": 1, "Fire rune": 3, "Nature rune": 1},
            "magic_alchemy_item": "",
        })
        dialog = self._open(pd, current_skill="Magic")
        tree = dialog.findChild(QTreeWidget, "magicTargetTree")
        self.assertTrue(_tree_row(tree, "low_alchemy").isDisabled())

        picker = dialog.findChild(QComboBox, "magicAlchemyItemCombo")
        picker.setCurrentIndex(picker.findData("Rune platebody"))
        QApplication.processEvents()

        tree = dialog.findChild(QTreeWidget, "magicTargetTree")
        self.assertFalse(_tree_row(tree, "low_alchemy").isDisabled())

    def test_magic_surface_projects_livid_unlocks_and_real_consumer_blocks(self) -> None:
        pd = _make_player_data()
        pd.update({
            "magic_level": 99,
            "current_magic": "make_black_dragon_leather",
            "inventory": {
                "Astral rune": 100,
                "Law rune": 100,
                "Cosmic rune": 100,
                "Air rune": 100,
                "Water rune": 100,
                "Earth rune": 100,
                "Nature rune": 100,
                "Fire rune": 100,
                "Body rune": 100,
                "Black dragonhide": 5,
            },
            "quests": {
                "lunar_diplomacy": {"completed": True},
                "dream_mentor": {"completed": True},
                "my_arms_big_adventure": {"completed": True},
            },
            "livid_farm": {
                "unlocked_spells": [
                    "south_falador_teleport",
                    "repair_rune_pouch",
                    "north_ardougne_teleport",
                    "remote_farm",
                    "spiritualise_food",
                    "make_leather",
                ],
            },
        })
        dialog = self._open(pd, current_skill="Magic")
        tree = dialog.findChild(QTreeWidget, "magicTargetTree")

        self.assertFalse(_tree_row(tree, "south_falador_teleport").isDisabled())
        self.assertFalse(_tree_row(tree, "remote_farm").isDisabled())
        self.assertFalse(
            _tree_row(tree, "make_black_dragon_leather").isDisabled()
        )
        repair = _tree_row(tree, "repair_rune_pouch")
        spiritualise = _tree_row(tree, "spiritualise_food")
        self.assertTrue(repair.isDisabled())
        self.assertTrue(spiritualise.isDisabled())
        self.assertIn(
            "Pouch strengthening is not available yet",
            repair.toolTip(0),
        )
        self.assertIn(
            "Familiar food effects are not available yet",
            spiritualise.toolTip(0),
        )
        self.assertIn(
            "Destination: South Falador gate",
            _tree_row(tree, "south_falador_teleport").toolTip(0),
        )

        dialog.show()
        dialog.resize(720, 540)
        for _ in range(6):
            QApplication.processEvents()
        leather_row = _tree_row(tree, "make_black_dragon_leather")
        self.assertIn("Input: Black dragonhide x1–5", leather_row.toolTip(0))
        self.assertFalse(leather_row.icon(0).isNull())
        self.assertGreater(tree.viewport().height(), 0)
        self.assertEqual(tree.horizontalScrollBar().maximum(), 0)
