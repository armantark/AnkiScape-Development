from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _FakeCol,
    _find_smith_tree,
    _goto_smithing,
    _make_player_data,
    _smith_row,
    _smith_tier_node,
    _smith_tree_items,
    re,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_cannonball_row_shows_quest_gate_mould_and_icon(self) -> None:
        pd = _make_player_data()
        pd["smithing_level"] = 35
        pd["current_smith"] = "forge_cannonballs"
        pd["inventory"] = {"Steel bar": 1, "Ammo mould": 1}
        pd["quests"]["dwarf_cannon"] = {"completed": True}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        row = _smith_row(_find_smith_tree(dialog), "forge_cannonballs")

        self.assertFalse(row.isDisabled())
        self.assertFalse(row.icon(0).isNull())
        self.assertIn("Output: Cannonball x4", row.toolTip(0))
        self.assertIn("Required tools:", row.toolTip(0))
        self.assertIn("Ammo mould x1", row.toolTip(0))

    def test_smithing_groups_recipes_by_metal_tier(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Tin ore": 5, "Copper ore": 5, "Bronze bar": 5}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        tier_labels = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__tier__:Bronze", tier_labels)
        self.assertIn("__tier__:Rune", tier_labels)
        # A metal group unifies its smelt bar with the forge items made from it:
        # the Bronze node parents both smelt_bronze_bar and a bronze forge recipe.
        bronze = _smith_tier_node(tree, "Bronze")
        child_ids = {bronze.child(i).data(0, Qt.ItemDataRole.UserRole) for i in range(bronze.childCount())}
        self.assertIn("smelt_bronze_bar", child_ids)
        self.assertIn("forge_bronze_dagger", child_ids)

    def test_smithing_children_sorted_by_level_within_a_metal(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Rune bar": 20}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        rune = _smith_tier_node(tree, "Rune")
        levels = [
            int(re.search(r"\(Lvl (\d+)\)", rune.child(i).text(0)).group(1))
            for i in range(rune.childCount())
        ]
        self.assertEqual(levels, sorted(levels), f"Rune group not level-ordered: {levels}")
        # Sanity: the smelt bar (Lvl 85) leads its level tie ahead of forge rows.
        self.assertEqual(rune.child(0).data(0, Qt.ItemDataRole.UserRole), "smelt_rune_bar")

    def test_smithing_groups_collapsed_by_default_except_current_target(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze bar": 10}
        pd["current_smith"] = "forge_bronze_dagger"  # Bronze tier
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        # The group holding the current target is expanded so the selection shows.
        self.assertTrue(_smith_tier_node(tree, "Bronze").isExpanded())
        # Every other metal group starts collapsed to tame the ~166-row panel.
        self.assertFalse(_smith_tier_node(tree, "Rune").isExpanded())
        self.assertFalse(_smith_tier_node(tree, "Adamant").isExpanded())

    def test_smithing_rows_carry_stable_recipe_ids_not_display_names(self) -> None:
        pd = _make_player_data()
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        roles = [it.data(0, Qt.ItemDataRole.UserRole) for it in _smith_tree_items(tree)]
        self.assertIn("smelt_bronze_bar", roles)
        self.assertIn("forge_rune_platebody", roles)
        # Recipe children store the stable id, never the human display name.
        self.assertNotIn("Bronze bar", roles)
        self.assertNotIn("Rune platebody", roles)

    def test_smithing_locks_rows_for_level_and_for_missing_materials(self) -> None:
        pd = _make_player_data()  # smithing_level 33, empty inventory
        pd["inventory"] = {}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        # Rune platebody (Lvl 99) is above level -> locked with a level reason.
        rune = _smith_row(tree, "forge_rune_platebody")
        self.assertTrue(rune.isDisabled())
        self.assertIn("level 99", rune.toolTip(0))
        # Bronze bar is in-level but there are no ores -> locked with materials.
        bronze = _smith_row(tree, "smelt_bronze_bar")
        self.assertTrue(bronze.isDisabled())
        self.assertIn("materials", bronze.toolTip(0))
        # No hammer/tool gate is ever surfaced (toolbelt is gathering-only).
        self.assertNotIn("hammer", bronze.toolTip(0).lower())

    def test_smithing_tooltip_shows_output_xp_owned_counts_and_no_source(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Iron bar": 1}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        # Iron pickaxe needs 2 Iron bars; the tooltip should reflect output + owned.
        pick = _smith_row(tree, "forge_iron_pickaxe")
        tip = pick.toolTip(0)
        self.assertIn("Output: Iron pickaxe x1", tip)
        self.assertIn("Base XP:", tip)
        self.assertIn("Iron bar x2 (you have 1)", tip)
        # The dev-facing source enum/path was removed from player tooltips.
        self.assertNotIn("Source", tip)
        # Owning only 1 of 2 required bars keeps it locked on materials.
        self.assertTrue(pick.isDisabled())

    def test_smithing_unlocks_with_materials_and_persists_recipe_id(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze bar": 10}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        dagger = _smith_row(tree, "forge_bronze_dagger")
        self.assertFalse(dagger.isDisabled())
        tree.itemClicked.emit(dagger, 0)
        QApplication.processEvents()
        self.assertEqual(self._smith_calls[-1], "forge_bronze_dagger")

    def test_smithing_clicking_a_tier_node_does_not_persist_a_target(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze bar": 10}
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        before = list(self._smith_calls)
        tree.itemClicked.emit(_smith_tier_node(tree, "Rune"), 0)
        QApplication.processEvents()
        self.assertEqual(self._smith_calls, before, "tier headers must not set a target")

    def test_smithing_highlights_current_target_on_open(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Bronze bar": 10}
        pd["current_smith"] = "forge_bronze_dagger"
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        current = tree.currentItem()
        self.assertIsNotNone(current)
        self.assertEqual(current.data(0, Qt.ItemDataRole.UserRole), "forge_bronze_dagger")

    def test_smithing_collapse_state_persists_across_reopen(self) -> None:
        # Collapse state is a UI pref persisted in Anki config. mw is None in the
        # headless harness, so inject a tiny dict-backed config to prove the
        # expand -> persist -> reopen-expanded loop actually round-trips.
        from ankiscape.ui import ui

        # Subclass QWidget so show_main_menu can still parent its QDialog to mw.
        class _FakeMw(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.col = _FakeCol()

        orig_mw = ui.mw
        ui.mw = _FakeMw()
        try:
            pd = _make_player_data()
            pd["inventory"] = {"Bronze bar": 10}
            dialog = self._open(pd)
            _goto_smithing(dialog)
            tree = _find_smith_tree(dialog)
            rune = _smith_tier_node(tree, "Rune")
            self.assertFalse(rune.isExpanded())
            rune.setExpanded(True)  # emits itemExpanded -> persists "Rune"
            QApplication.processEvents()
            self.assertIn("Rune", ui.smith_expanded_tiers())

            # Reopen: the Rune group should now come up expanded from config.
            dialog2 = self._open(pd)
            _goto_smithing(dialog2)
            tree2 = _find_smith_tree(dialog2)
            self.assertTrue(_smith_tier_node(tree2, "Rune").isExpanded())
        finally:
            ui.mw = orig_mw

    def test_smithing_disabled_row_click_does_not_change_target(self) -> None:
        # Same disabled-row click guard on the Smithing tree.
        pd = _make_player_data()
        pd["inventory"] = {}  # no bars -> every smith recipe locked on materials
        dialog = self._open(pd)
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        locked = _smith_row(tree, "smelt_bronze_bar")
        self.assertTrue(locked.isDisabled())
        before = list(self._smith_calls)
        tree.itemClicked.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._smith_calls, before, "locked smith target must not be selectable")
