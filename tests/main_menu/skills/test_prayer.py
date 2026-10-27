from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_row
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QComboBox, QLabel, QListWidget, QPushButton, QTreeWidget, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_prayer_tree_groups_methods_and_locked_rows_ignore_clicks(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {}
        dialog = self._open(pd, current_skill="Prayer")
        tree = next(
            tree for tree in dialog.findChildren(QTreeWidget)
            if any(
                str(tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)).startswith("__prayer_group__:")
                for i in range(tree.topLevelItemCount())
            )
        )
        groups = [tree.topLevelItem(i).text(0).split("  (")[0] for i in range(tree.topLevelItemCount())]
        self.assertEqual(groups, ["Bury", "Scatter", "Ectofuntus", "Gilded altar"])
        bury = tree.topLevelItem(0)
        bones = next(bury.child(i) for i in range(bury.childCount()) if bury.child(i).data(0, Qt.ItemDataRole.UserRole) == "bury_bones")
        self.assertTrue(bones.isDisabled())
        before = list(self._prayer_calls)
        tree.itemClicked.emit(bones, 0)
        QApplication.processEvents()
        self.assertEqual(self._prayer_calls, before)

    def test_prayer_unlocked_row_selects_by_stable_target_id(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bones": 1}
        dialog = self._open(pd, current_skill="Prayer")
        tree = next(
            tree for tree in dialog.findChildren(QTreeWidget)
            if tree.findItems("✓ Bones — 4.5 XP", Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive, 0)
        )
        row = tree.findItems("✓ Bones — 4.5 XP", Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive, 0)[0]
        self.assertFalse(row.isDisabled())
        tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._prayer_calls[-1], ("bones", "base"))
        self.assertEqual(pd["current_prayer"], "bury_bones")

    def test_prayer_gilded_mode_rates_rows_and_readiness_refresh_live(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "prayer_level": 99,
                "current_prayer": "gilded_altar_dragon_bones",
                "prayer_gilded_mode": "hosted",
                "prayer_owned_altar_stint": {},
                "prayer_gilded_house_search": {},
                "house_owned": True,
                "house_rooms_bought": {"chapel": True},
                "house_built_flags": {"guilded_altar": True},
                "inventory": {"Dragon bones": 3, "Clean marrentill": 2},
            }
        )
        dialog = self._open(pd, current_skill="Mining")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(6):
            QApplication.processEvents()
        next(button for button in dialog.findChildren(QPushButton) if button.text() == "Combat").click()
        for _ in range(4):
            QApplication.processEvents()
        skill_list = next(
            widget
            for widget in dialog.findChildren(QListWidget)
            if {"Combat", "Prayer"}.issubset({widget.item(i).text() for i in range(widget.count())})
        )
        prayer_row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Prayer")
        skill_list.setCurrentRow(prayer_row)
        for _ in range(6):
            QApplication.processEvents()

        mode_label = dialog.findChild(QLabel, "prayerGildedModeLabel")
        mode = dialog.findChild(QComboBox, "prayerGildedModeCombo")
        self.assertEqual(mode_label.text(), "Gilded altar mode")
        self.assertEqual(mode.itemText(mode.findData("hosted")), "Hosted - 350% XP")
        self.assertEqual(mode.itemText(mode.findData("owned")), "Owned - 250% XP (0/2 burners)")
        self.assertEqual(mode.currentData(), "hosted")

        mode.setCurrentIndex(mode.findData("owned"))
        for _ in range(6):
            QApplication.processEvents()
        self.assertEqual(self._prayer_calls[-1], ("dragon_bones", "gilded_owned"))
        self.assertEqual(pd["prayer_gilded_mode"], "owned")
        mode = dialog.findChild(QComboBox, "prayerGildedModeCombo")
        tree = dialog.findChild(QTreeWidget, "prayerTargetTree")
        row = _tree_row(tree, "gilded_altar_dragon_bones")
        self.assertEqual(mode.currentData(), "owned")
        self.assertEqual(row.text(0), "✓ Dragon bones — 180 XP")
        self.assertIn("Owned · 250% XP · 0/2 burners", row.toolTip(0))
        self.assertIn("none required (0 burners)", row.toolTip(0))
        self.assertFalse(row.isDisabled())
        self.assertTrue(dialog.findChild(QPushButton, "prayerTrainButton").isEnabled())

        pd["house_built_flags"]["marble_burner"] = True
        mode.setCurrentIndex(mode.findData("hosted"))
        for _ in range(6):
            QApplication.processEvents()
        mode = dialog.findChild(QComboBox, "prayerGildedModeCombo")
        self.assertEqual(mode.itemText(mode.findData("owned")), "Owned - 300% XP (1/2 burners)")

        pd["house_built_flags"]["mahogany_burner"] = True
        mode.setCurrentIndex(mode.findData("owned"))
        for _ in range(6):
            QApplication.processEvents()
        mode = dialog.findChild(QComboBox, "prayerGildedModeCombo")
        tree = dialog.findChild(QTreeWidget, "prayerTargetTree")
        row = _tree_row(tree, "gilded_altar_dragon_bones")
        self.assertEqual(mode.currentData(), "owned")
        self.assertEqual(mode.currentText(), "Owned - 350% XP (2/2 burners)")
        self.assertEqual(row.text(0), "✓ Dragon bones — 252 XP")
        self.assertIn("Clean marrentill x2", row.toolTip(0))

        for width, height in ((720, 540), (900, 560)):
            dialog.resize(width, height)
            for _ in range(6):
                QApplication.processEvents()
            panel = dialog.findChild(QWidget, "prayerSkillPanel")
            tree = dialog.findChild(QTreeWidget, "prayerTargetTree")
            self.assertGreater(panel.height(), 0)
            self.assertGreater(tree.viewport().height(), 0)
            self.assertEqual(tree.horizontalScrollBar().maximum(), 0)
        dialog.deleteLater()

    def test_piety_gate_copy_names_and_enforces_defence_70(self) -> None:
        pd = _make_player_data()
        pd["prayer_level"] = 99
        pd["defense_level"] = 69
        pd["knight_waves"] = {"completed": True}
        dialog = self._open(pd)
        piety = dialog.findChild(QCheckBox, "combatPrayerCheck::piety")
        self.assertIsNotNone(piety)
        self.assertIn("Def 70", piety.text())
        self.assertIn("70 Defence", piety.toolTip())
        self.assertFalse(piety.isEnabled())

        pd["defense_level"] = 70
        unlocked_dialog = self._open(pd)
        unlocked = unlocked_dialog.findChild(QCheckBox, "combatPrayerCheck::piety")
        self.assertTrue(unlocked.isEnabled())
