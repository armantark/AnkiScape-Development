from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _craft_family_node,
    _craft_row,
    _find_artisan_skill_list,
    _find_craft_tree,
    _find_named_widget,
    _goto_crafting,
    _icon_pixels,
    _make_player_data,
    _panel_title,
    _tree_items,
    re,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QColor, QPushButton, QToolButton, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_switching_category_then_selecting_crafting_updates_panel(self) -> None:
        # The user reported the same stale-panel bug under Artisan -> Crafting,
        # so exercise the cross-category path too, not just the first category.
        artisan = next(
            b for b in self.dialog.findChildren(QPushButton) if b.text() == "Artisan"
        )
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(self.dialog)
        craft_row = next(
            i for i in range(skill_list.count())
            if skill_list.item(i).text() == "Crafting"
        )
        skill_list.setCurrentRow(craft_row)
        QApplication.processEvents()
        title = _panel_title(self.dialog)
        self.assertTrue(
            title.startswith("Crafting"),
            f"panel did not switch to Crafting; still shows {title!r}",
        )

    def test_soft_clay_left_crafting_and_is_now_a_utility_activity(self) -> None:
        # Open Crafting target tree and assert Soft clay is no longer a target.
        tree = _goto_crafting(self.dialog)
        craft_texts = [it.text(0) for it in _tree_items(tree)]
        self.assertFalse(
            any(t.startswith("Soft clay") for t in craft_texts),
            f"Soft clay should not be a Crafting target anymore: {craft_texts}",
        )
        # And it now lives under Utilities, not Activities.
        utility_tree = self._open_utility(self.dialog)
        skill_column_label = _find_named_widget(
            self.dialog, "skillColumnLabel"
        )
        self.assertEqual(skill_column_label.text(), "Selection")
        skill_list = _find_named_widget(self.dialog, "skillListWidget")
        utility_icon = skill_list.item(0).icon()
        util_texts = [it.text(0) for it in _tree_items(utility_tree)]
        self.assertIn("Make soft clay", util_texts)
        self.assertIn("Gather wool", util_texts)
        self.assertIn("Gather grain", util_texts)
        self.assertIn("Make bread dough", util_texts)
        self.assertIn("Bankstanding", util_texts)
        economy = next(
            item
            for item in _tree_items(utility_tree)
            if item.data(0, Qt.ItemDataRole.UserRole)
            == "__utility_group__:economy"
        )
        self.assertIn(
            "Bankstanding",
            [economy.child(index).text(0) for index in range(economy.childCount())],
        )
        # Retired 2026-07-06: outputs are live NPC shop stock now.
        self.assertNotIn("Scavenge chicken feathers", util_texts)
        self.assertNotIn("Gather fishing bait", util_texts)
        self.assertNotIn("Buy Hunter supplies", util_texts)
        activities_tree = self._open_activities(self.dialog)
        activity_icon = skill_list.item(0).icon()
        self.assertFalse(utility_icon.isNull())
        self.assertFalse(activity_icon.isNull())
        self.assertNotEqual(utility_icon.cacheKey(), activity_icon.cacheKey())
        activity_texts = [it.text(0) for it in _tree_items(activities_tree)]
        self.assertNotIn("Make soft clay", activity_texts)
        self.assertIn("Livid Farm", activity_texts)
        minigames = skill_list.item(1)
        dnds = skill_list.item(2)
        self.assertFalse(minigames.icon().isNull())
        self.assertFalse(dnds.icon().isNull())
        self.assertNotEqual(
            _icon_pixels(minigames.icon()),
            _icon_pixels(dnds.icon()),
        )
        skill_list.setCurrentItem(minigames)
        QApplication.processEvents()
        self.assertEqual(
            {
                activities_tree.topLevelItem(index).data(
                    0, Qt.ItemDataRole.UserRole
                )
                for index in range(activities_tree.topLevelItemCount())
                if not activities_tree.topLevelItem(index).isHidden()
            },
            {
                "fist_of_guthix",
                "sorceress_garden",
                "livid_farm",
                "vinesweeper",
                "fight_caves",
                "stealing_creation",
                "barrows",
                "flash_powder_factory",
                "pyramid_plunder",
                "werewolf_skullball",
                "gnome_ball",
                "fishing_trawler",
                "great_orb_project",
                "trouble_brewing",
                "castle_wars",
                "conquest",
                "pest_control",
                "barbarian_assault",
                "soul_wars",
                "shades_of_mortton",
                "tzhaar_fight_pit",
                "duel_arena",
                "clan_wars",
                "mage_training_arena",
                "temple_trekking",
                "mobilising_armies",
                "gnome_restaurant",
                "dominion_tower",
                "crucible",
                "ranging_guild",
            },
        )
        skill_list.setCurrentItem(dnds)
        QApplication.processEvents()
        self.assertEqual(
            {
                activities_tree.topLevelItem(index).data(
                    0, Qt.ItemDataRole.UserRole
                )
                for index in range(activities_tree.topLevelItemCount())
                if not activities_tree.topLevelItem(index).isHidden()
            },
            {
                "big_chinchompa",
                "familiarisation",
                "penguin_hide_and_seek",
                "shooting_stars",
                "court_cases",
                "big_top_bonanza",
                "fish_flingers",
                "phoenix_lair",
                "skeletal_horror",
                "tears_of_guthix",
                "enchanted_key",
                "evil_tree",
                "goblin_raids",
                "troll_invasion",
                "shattered_heart",
                "treasure_trail",
                "bork",
            },
        )
        self.assertTrue(
            any(text.startswith("Warriors' Guild") for text in activity_texts)
        )

    def test_crafting_groups_recipes_by_family(self) -> None:
        tree = _goto_crafting(self.dialog)
        family_roles = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__family__:gems", family_roles)
        self.assertIn("__family__:jewellery", family_roles)
        # The Gem-cutting family parents the stable cut recipe IDs.
        gems = _craft_family_node(tree, "gems")
        child_ids = {gems.child(i).data(0, Qt.ItemDataRole.UserRole) for i in range(gems.childCount())}
        self.assertIn("cut_emerald", child_ids)
        self.assertIn("cut_sapphire", child_ids)

    def test_crafting_rows_carry_stable_recipe_ids_not_display_names(self) -> None:
        tree = _goto_crafting(self.dialog)
        roles = [it.data(0, Qt.ItemDataRole.UserRole) for it in _tree_items(tree)]
        self.assertIn("jewellery_sapphire_necklace", roles)
        self.assertNotIn("Sapphire necklace", roles)
        # Display-name collisions (e.g. the strung "Dragonstone ammy") are exactly
        # why targets are keyed by stable id, never by output name.
        self.assertIn("jewellery_dragonstone_ammy", roles)
        self.assertIn("string_dragonstone_amulet", roles)

    def test_crafting_children_sorted_by_level_within_a_family(self) -> None:
        tree = _goto_crafting(self.dialog)
        jewellery = _craft_family_node(tree, "jewellery")
        levels = [
            int(re.search(r"\(Lvl (\d+)\)", jewellery.child(i).text(0)).group(1))
            for i in range(jewellery.childCount())
        ]
        self.assertEqual(levels, sorted(levels), f"jewellery not level-ordered: {levels}")

    def test_crafting_dependency_heavy_targets_are_wired_like_any_other(self) -> None:
        # Dragonstone/onyx/hide/glass/battlestaff targets are NOT hidden, NOT
        # special-cased, and carry no distinct tag/label/state. They are simply,
        # emergently un-runnable because the player holds 0 of a material with no
        # source yet — identical to a Sapphire ring with 0 sapphires. The only
        # gate is the normal missing-material check.
        pd = _make_player_data()
        pd["inventory"] = {}
        pd["crafting_level"] = 99
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        for rid in (
            "cut_dragonstone",
            "cut_onyx",
            "jewellery_onyx_amulet",
            "leather_black_dhide_body",
            "glass_beer_glass",
            "battlestaff_water_battlestaff",
        ):
            row = _craft_row(tree, rid)
            # Present and visible, with no special "input-starved"/"coming soon"
            # wording on the row — wired exactly like every other target.
            self.assertNotIn("input-starved", row.text(0).lower(), rid)
            self.assertNotIn("coming soon", row.text(0).lower(), rid)
            # Locked only on materials (level 99 is met), same as any other recipe
            # whose materials you lack.
            self.assertTrue(row.isDisabled(), f"{rid} should be material-gated")
            self.assertIn("materials", row.toolTip(0))
            self.assertNotIn("level", row.toolTip(0).split("Locked due to:")[-1])

    def test_crafting_disabled_row_click_does_not_change_target(self) -> None:
        # Bug fix: itemClicked fires on disabled rows, so clicking a locked target
        # must NOT make it active (otherwise the next review fails with
        # "you don't have X"). Empty inventory locks every craft on materials.
        pd = _make_player_data()
        pd["inventory"] = {}
        pd["crafting_level"] = 99
        pd["current_craft"] = None
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        locked = _craft_row(tree, "cut_dragonstone")
        self.assertTrue(locked.isDisabled())
        before = list(self._craft_calls)
        tree.itemClicked.emit(locked, 0)
        tree.itemActivated.emit(locked, 0)
        QApplication.processEvents()
        self.assertEqual(self._craft_calls, before, "locked target must not be selectable")

    def test_crafting_details_can_enable_target_local_potion_use(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {
            "Soft clay": 2,
            "Ring mould": 1,
            "Crafting potion (3)": 1,
        }
        pd["crafting_level"] = 1
        pd["current_craft"] = "form_pot_unfired"
        dialog = self._open(pd, current_skill="Crafting")
        tree = _goto_crafting(dialog)
        boosted = _craft_row(tree, "form_clay_ring_unfired")
        self.assertTrue(boosted.isDisabled())

        tree.itemClicked.emit(boosted, 0)
        details = dialog.findChild(QToolButton, "targetDetailsToggle")
        self.assertIsNotNone(details)
        details.click()
        QApplication.processEvents()
        toggle = dialog.findChild(
            QCheckBox,
            "skillingPotionTargetToggle::crafting::form_clay_ring_unfired",
        )
        self.assertIsNotNone(toggle)
        self.assertEqual(toggle.text(), "Use Crafting potion (+3) when needed")
        toggle.click()
        QApplication.processEvents()

        self.assertEqual(
            self._skilling_potion_calls[-1],
            ("crafting", "form_clay_ring_unfired", True),
        )
        self.assertEqual(pd["current_craft"], "form_clay_ring_unfired")
        rebuilt = _find_craft_tree(dialog)
        self.assertFalse(
            _craft_row(rebuilt, "form_clay_ring_unfired").isDisabled()
        )

    def test_crafting_tooltip_shows_output_xp_and_owned_counts(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Gold bar": 1}  # sapphire necklace needs a bar + sapphire
        pd["crafting_level"] = 99
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        row = _craft_row(tree, "jewellery_sapphire_necklace")
        tip = row.toolTip(0)
        self.assertIn("Output: Sapphire necklace x1", tip)
        self.assertIn("Base XP:", tip)
        self.assertIn("Gold bar x1 (you have 1)", tip)
        self.assertIn("Sapphire x1 (you have 0)", tip)
        self.assertTrue(row.isDisabled())  # missing the sapphire

    def test_crafting_unlocks_with_materials_and_persists_recipe_id(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Gold bar": 5, "Ring mould": 1}
        pd["crafting_level"] = 99
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        ring = _craft_row(tree, "jewellery_gold_ring")
        self.assertFalse(ring.isDisabled())
        tree.itemClicked.emit(ring, 0)
        QApplication.processEvents()
        self.assertEqual(self._craft_calls[-1], "jewellery_gold_ring")

    def test_crafting_clicking_a_family_node_does_not_persist_a_target(self) -> None:
        tree = _goto_crafting(self.dialog)
        before = list(self._craft_calls)
        tree.itemClicked.emit(_craft_family_node(tree, "jewellery"), 0)
        QApplication.processEvents()
        self.assertEqual(self._craft_calls, before, "family headers must not set a target")

    def test_crafting_highlights_current_target_and_expands_its_family(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Gold bar": 5, "Ring mould": 1}
        pd["crafting_level"] = 99
        pd["current_craft"] = "jewellery_gold_ring"
        dialog = self._open(pd)
        tree = _goto_crafting(dialog)
        current = tree.currentItem()
        self.assertIsNotNone(current)
        self.assertEqual(current.data(0, Qt.ItemDataRole.UserRole), "jewellery_gold_ring")
        self.assertEqual(
            current.background(0).color(),
            QColor(76, 175, 80, 120),
        )
        self.assertTrue(current.text(0).startswith("✓ "))
        # The family holding the current target opens so the selection is visible.
        self.assertTrue(_craft_family_node(tree, "jewellery").isExpanded())
        # Unrelated families stay collapsed to tame the panel.
        self.assertFalse(_craft_family_node(tree, "gems").isExpanded())
