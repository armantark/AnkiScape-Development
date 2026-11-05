from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _find_skill_list, _make_player_data, _panel_title
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_selecting_woodcutting_updates_panel(self) -> None:
        skill_list = _find_skill_list(self.dialog)
        wc_row = next(
            i for i in range(skill_list.count())
            if skill_list.item(i).text() == "Woodcutting"
        )
        skill_list.setCurrentRow(wc_row)
        QApplication.processEvents()
        title = _panel_title(self.dialog)
        self.assertTrue(
            title.startswith("Woodcutting"),
            f"panel did not switch to Woodcutting; still shows {title!r}",
        )

    def test_woodcutting_list_shows_friendly_names_not_stable_ids(self) -> None:
        tree_list = self._open_woodcutting(self.dialog)
        texts = [tree_list.item(i).text() for i in range(tree_list.count())]
        # Friendly display names, not raw IDs like "oak"/"tree".
        self.assertTrue(any(t.startswith("Oak (Lvl\xa015)") for t in texts), texts)
        self.assertTrue(any(t.startswith("✓ Tree (Lvl\xa01)") for t in texts), texts)
        self.assertFalse(any(t == "oak" or t == "tree" for t in texts), texts)

    def test_woodcutting_ivy_marked_xp_only_no_logs(self) -> None:
        tree_list = self._open_woodcutting(self.dialog)
        ivy = self._wc_row(tree_list, "Ivy ")
        self.assertIn("XP only", ivy.text())
        self.assertIn("produces no logs", ivy.toolTip())

    def test_woodcutting_tooltip_shows_output_and_best_hatchet(self) -> None:
        tree_list = self._open_woodcutting(self.dialog)
        oak = self._wc_row(tree_list, "Oak ")
        tip = oak.toolTip()
        self.assertIn("Oak logs", tip)
        self.assertIn("Bronze hatchet", tip)  # seeded toolbelt is the best usable

    def test_woodcutting_high_level_tree_locked_with_level_reason(self) -> None:
        tree_list = self._open_woodcutting(self.dialog)
        magic = self._wc_row(tree_list, "Magic ")  # level 75, player is 33
        self.assertFalse(
            bool(magic.flags() & Qt.ItemFlag.ItemIsEnabled),
            "Magic should be locked at level 33",
        )
        self.assertIn("level 75", magic.toolTip())

    def test_woodcutting_locks_all_trees_when_no_usable_hatchet(self) -> None:
        pd = _make_player_data()
        pd["toolbelt"] = {"woodcutting": []}  # no bound tool, no hatchet item
        dialog = self._open(pd)
        tree_list = self._open_woodcutting(dialog)
        tree = self._wc_row(tree_list, "Tree ")
        self.assertFalse(
            bool(tree.flags() & Qt.ItemFlag.ItemIsEnabled),
            "Tree should lock without a usable hatchet",
        )
        self.assertIn("no usable hatchet", tree.toolTip())

    def test_woodcutting_split_row_uses_material_gate_and_period_icon(self) -> None:
        pd = _make_player_data()
        pd["woodcutting_level"] = 54
        pd["inventory"] = {"Arctic pine logs": 1}
        pd["toolbelt"] = {"woodcutting": []}
        pd["quests"]["the_fremennik_isles"] = {"started": True}
        dialog = self._open(pd)
        tree_list = self._open_woodcutting(dialog)
        split = self._wc_row(tree_list, "Split Arctic pine logs ")
        self.assertTrue(bool(split.flags() & Qt.ItemFlag.ItemIsEnabled))
        self.assertIn("Arctic pine logs x1 (you have 1)", split.toolTip())
        self.assertNotIn("hatchet", split.toolTip().lower())
        self.assertFalse(split.icon().isNull())
        self.assertIn(
            "Select what to Chop or Split",
            [label.text() for label in dialog.findChildren(QLabel)],
        )

    def test_special_woodcutting_rows_show_icons_and_the_arctic_route_gate(self) -> None:
        pd = _make_player_data()
        pd["woodcutting_level"] = 99
        pd["toolbelt"] = {"woodcutting": ["rune_hatchet"]}
        pd["quests"].pop("the_fremennik_isles", None)
        dialog = self._open(pd)
        tree_list = self._open_woodcutting(dialog)

        arctic = self._wc_row(tree_list, "Arctic pine ")
        eucalyptus = self._wc_row(tree_list, "Eucalyptus ")
        self.assertFalse(bool(arctic.flags() & Qt.ItemFlag.ItemIsEnabled))
        self.assertIn("Start The Fremennik Isles", arctic.toolTip())
        self.assertFalse(arctic.icon().isNull())
        self.assertTrue(bool(eucalyptus.flags() & Qt.ItemFlag.ItemIsEnabled))
        self.assertFalse(eucalyptus.icon().isNull())
