import os
import unittest

from constants import (
    BIRD_NEST_OPEN_TABLES,
    BAR_IMAGES,
    COMBAT_ENEMY_DATA,
    COOKING_DATA,
    COOKING_ITEM_IMAGES,
    CRAFTED_ITEM_IMAGES,
    CRAFTING_DATA,
    DEFAULT_COMBAT_TARGET,
    DEFAULT_COOKING_TARGET,
    DEFAULT_FIREMAKING_TARGET,
    DEFAULT_FISHING_TARGET,
    DEFAULT_HUNTER_TARGET,
    DEFAULT_MINING_TARGET,
    DEFAULT_RUNECRAFTING_TARGET,
    DEFAULT_SMITHING_TARGET,
    DEFAULT_UTILITY_ACTIVITY,
    DEFAULT_WOODCUTTING_TARGET,
    FIREMAKING_DATA,
    FIREMAKING_ITEM_IMAGES,
    FISHING_DATA,
    FISHING_ITEM_IMAGES,
    FLETCHED_ITEM_IMAGES,
    FLETCHING_DATA,
    GEM_IMAGES,
    HUNTER_DATA,
    HUNTER_ITEM_IMAGES,
    EQUIPMENT_ITEM_DATA,
    MINING_PICKAXE_DATA,
    ORE_DATA,
    ORE_IMAGES,
    QUEST_UNLOCK_RULES,
    RUNECRAFTING_DATA,
    RUNECRAFTING_ITEM_IMAGES,
    RUNECRAFTING_POUCH_DATA,
    SMITHING_DATA,
    TREE_DATA,
    TREE_IMAGES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
    WOODCUTTING_AXE_DATA,
)
from target_metadata import (
    TargetRowMetadata,
    combat_target_rows,
    cooking_target_rows,
    crafting_target_rows,
    firemaking_target_rows,
    fishing_target_rows,
    fletching_target_rows,
    hunter_target_rows,
    mining_target_rows,
    runecrafting_target_rows,
    smithing_target_rows,
    utility_activity_rows,
    woodcutting_target_rows,
)


def _row(rows, target_id):
    for row in rows:
        if row.target_id == target_id:
            return row
    raise AssertionError(f"row {target_id!r} not found")


class TargetMetadataTest(unittest.TestCase):
    def test_combat_rows_expose_enabled_source_backed_enemy_targets(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "giant_rat",
                "combat_attack_style": "accurate",
                "attack_level": 10,
                "strength_level": 10,
                "defense_level": 10,
                "constitution_level": 10,
                "inventory": {"Shark": 2},
                "equipment": {},
                "combat_auto_eat_food": ["Shark"],
                "combat_supply_loadout": {"food": {"Shark": 1}},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        chicken = _row(rows, "chicken")
        giant_rat = _row(rows, "giant_rat")
        spider = _row(rows, "spider")
        giant_spider = _row(rows, "giant_spider")
        cow = _row(rows, "cow")
        cow_calf = _row(rows, "cow_calf")
        highwayman = _row(rows, "highwayman")
        seagull = _row(rows, "seagull")

        self.assertTrue(chicken.enabled)
        self.assertTrue(giant_rat.current)
        self.assertEqual(giant_rat.group, "Lumbridge")
        self.assertIn("Giant rat · combat level 2", giant_rat.tooltip)
        self.assertIn("Enemy LP: 50/50", giant_rat.tooltip)
        self.assertIn("Food: Shark x1 loaded + 2 bank", giant_rat.tooltip)
        self.assertIn("Raw rat meat", giant_rat.tooltip)
        self.assertIn("giant_rat_level_2.plugin.kts", giant_rat.tooltip)
        self.assertEqual(spider.group, "Spiders")
        self.assertIn("Gold charm x1 (5/200)", spider.tooltip)
        self.assertEqual(giant_spider.group, "Spiders")
        self.assertIn("Air rune x4-6 (7/48)", giant_spider.tooltip)
        self.assertIn("Staff of air", giant_spider.tooltip)
        self.assertIn("giant_spider_level_2.plugin.kts", giant_spider.tooltip)
        self.assertEqual(cow.sort_key[:2], (2, "Cow"))
        self.assertEqual(cow_calf.group, "Lumbridge")
        self.assertIn("Cowhide", cow_calf.tooltip)
        self.assertEqual(highwayman.group, "Humanoids")
        self.assertIn("Cape x1", highwayman.tooltip)
        self.assertIn("Iron bolts x2-12 (1/20)", highwayman.tooltip)
        self.assertIn("highwayman_level_5.plugin.kts", highwayman.tooltip)
        self.assertEqual(seagull.group, "Coastal")
        self.assertEqual(seagull.sort_key[:2], (2, "Seagull"))

    def test_smithing_grouped_rows_preserve_tier_sort_and_lock_reasons(self):
        rows = smithing_target_rows(
            {
                "smithing_level": 33,
                "inventory": {},
                "current_smith": "smelt_bronze_bar",
            },
            SMITHING_DATA,
            BAR_IMAGES,
            DEFAULT_SMITHING_TARGET,
        )

        bronze = _row(rows, "smelt_bronze_bar")
        rune_platebody = _row(rows, "forge_rune_platebody")

        self.assertEqual(bronze.group, "Bronze")
        self.assertTrue(bronze.current)
        self.assertFalse(bronze.enabled)
        self.assertIn("materials", bronze.locked_reasons)
        self.assertIn("Copper ore x1 (you have 0)", bronze.tooltip)
        self.assertEqual(bronze.sort_key[:2], (1, 0))
        self.assertFalse(rune_platebody.enabled)
        self.assertIn("level 99", rune_platebody.locked_reasons)
        self.assertNotIn("hammer", bronze.tooltip.lower())

    def test_crafting_grouped_rows_preserve_family_material_locks_and_live_targets(self):
        rows = crafting_target_rows(
            {
                "crafting_level": 99,
                "inventory": {},
                "current_craft": "cut_dragonstone",
            },
            CRAFTING_DATA,
            CRAFTED_ITEM_IMAGES,
        )

        dragonstone = _row(rows, "cut_dragonstone")
        gold_ring = _row(rows, "jewellery_gold_ring")

        self.assertEqual(dragonstone.group, "gems")
        self.assertTrue(dragonstone.current)
        self.assertFalse(dragonstone.enabled)
        self.assertEqual(dragonstone.locked_reasons, ("materials",))
        self.assertIn("Uncut dragonstone", dragonstone.tooltip)
        self.assertNotIn("input-starved", dragonstone.label.lower())
        self.assertNotIn("coming soon", dragonstone.tooltip.lower())
        self.assertEqual(gold_ring.group, "jewellery")

    def test_cooking_grouped_rows_apply_quest_unlock_rules_once(self):
        player_data = {
            "cooking_level": 99,
            "inventory": {"Slimy eel": 1, "Raw yak meat": 1},
            "quests": {},
            "current_cooking": "cook_slimy_eel",
        }
        rows = cooking_target_rows(
            player_data,
            COOKING_DATA,
            COOKING_ITEM_IMAGES,
            DEFAULT_COOKING_TARGET,
            QUEST_UNLOCK_RULES,
        )

        slimy_eel = _row(rows, "cook_slimy_eel")
        yak = _row(rows, "cook_yak")
        self.assertEqual(slimy_eel.group, "eels")
        self.assertTrue(slimy_eel.current)
        self.assertFalse(slimy_eel.enabled)
        self.assertEqual(slimy_eel.locked_reasons, ("Priest in Peril",))
        self.assertIn("Locked due to: Priest in Peril", slimy_eel.tooltip)
        self.assertFalse(yak.enabled)
        self.assertEqual(yak.locked_reasons, ("The Fremennik Isles",))

        player_data["quests"] = {
            "priest_in_peril": {"started": True, "progress": 6, "completed": True},
            "the_fremennik_isles": {"started": True, "progress": 6, "completed": True},
        }
        unlocked_rows = cooking_target_rows(
            player_data,
            COOKING_DATA,
            COOKING_ITEM_IMAGES,
            DEFAULT_COOKING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "cook_slimy_eel").enabled)
        self.assertTrue(_row(unlocked_rows, "cook_yak").enabled)

    def test_mining_rows_preserve_current_icon_and_deferred_note_contract(self):
        rows = mining_target_rows(
            {
                "mining_level": 33,
                "inventory": {},
                "toolbelt": {"mining": ["bronze_pickaxe"]},
                "current_ore": "coal",
            },
            ORE_DATA,
            ORE_IMAGES,
            GEM_IMAGES,
            MINING_PICKAXE_DATA,
            DEFAULT_MINING_TARGET,
            {"coal": "Concentrated coal deposits are deferred."},
        )

        coal = _row(rows, "coal")
        runite = _row(rows, "runite")

        self.assertIsInstance(coal, TargetRowMetadata)
        self.assertEqual(coal.label, "Coal (Lvl 30)")
        self.assertTrue(coal.current)
        self.assertTrue(coal.enabled)
        self.assertEqual(coal.icon_path, ORE_IMAGES["Coal"])
        self.assertIn("Best usable pickaxe: Bronze pickaxe", coal.tooltip)
        self.assertIn("Concentrated coal deposits are deferred.", coal.tooltip)
        self.assertFalse(runite.enabled)
        self.assertIn("level 85", runite.tooltip)

    def test_mining_rows_apply_quest_unlock_rules(self):
        rows = mining_target_rows(
            {
                "mining_level": 33,
                "inventory": {},
                "toolbelt": {"mining": ["bronze_pickaxe"]},
                "current_ore": "rune_essence",
            },
            ORE_DATA,
            ORE_IMAGES,
            GEM_IMAGES,
            MINING_PICKAXE_DATA,
            DEFAULT_MINING_TARGET,
            quest_unlock_rules=QUEST_UNLOCK_RULES,
        )

        rune_essence = _row(rows, "rune_essence")
        self.assertFalse(rune_essence.enabled)
        self.assertIn("Locked due to: Rune Mysteries", rune_essence.tooltip)

    def test_woodcutting_rows_preserve_xp_only_and_tool_lock_contract(self):
        rows = woodcutting_target_rows(
            {
                "woodcutting_level": 1,
                "inventory": {},
                "toolbelt": {"woodcutting": []},
                "current_tree": "ivy",
            },
            TREE_DATA,
            TREE_IMAGES,
            WOODCUTTING_AXE_DATA,
            DEFAULT_WOODCUTTING_TARGET,
        )

        tree = _row(rows, "tree")
        ivy = _row(rows, "ivy")

        self.assertFalse(tree.enabled)
        self.assertIn("no usable hatchet", tree.tooltip)
        self.assertEqual(ivy.label, "Ivy (Lvl 68) — XP only")
        self.assertTrue(ivy.current)
        self.assertIn("XP only — produces no logs.", ivy.tooltip)

    def test_fletching_rows_preserve_stable_id_material_lock_and_current_target(self):
        rows = fletching_target_rows(
            {
                "fletching_level": 99,
                "inventory": {},
                "current_fletch": "arrow_shafts",
            },
            FLETCHING_DATA,
            FLETCHED_ITEM_IMAGES,
            QUEST_UNLOCK_RULES,
        )

        shafts = _row(rows, "arrow_shafts")

        self.assertEqual(shafts.label, "Arrow shafts (Logs) (Lvl 1)")
        self.assertTrue(shafts.current)
        self.assertFalse(shafts.enabled)
        self.assertEqual(shafts.icon_path, FLETCHED_ITEM_IMAGES["Arrow shafts"])
        self.assertEqual(shafts.group, "whittling")
        self.assertIn("Logs x1 (you have 0)", shafts.tooltip)
        self.assertIn("Locked due to: materials", shafts.tooltip)

    def test_fletching_rows_apply_broad_fletching_unlock_rule(self):
        player_data = {
            "fletching_level": 99,
            "inventory": {
                "Headless arrows": 15,
                "Broad arrow heads": 15,
                "Unfinished broad bolts": 10,
                "Feather": 10,
            },
            "current_fletch": "broad_arrows",
            "unlocked_abilities": [],
        }
        rows = fletching_target_rows(player_data, FLETCHING_DATA, FLETCHED_ITEM_IMAGES, QUEST_UNLOCK_RULES)

        broad_arrows = _row(rows, "broad_arrows")
        broad_bolts = _row(rows, "feather_broad_bolts")

        self.assertEqual(broad_arrows.group, "arrows")
        self.assertFalse(broad_arrows.enabled)
        self.assertIn("Broad Fletching", broad_arrows.tooltip)
        self.assertFalse(broad_bolts.enabled)
        self.assertIn("Broad Fletching", broad_bolts.tooltip)

        player_data["unlocked_abilities"] = ["broad_fletching"]
        unlocked_rows = fletching_target_rows(player_data, FLETCHING_DATA, FLETCHED_ITEM_IMAGES, QUEST_UNLOCK_RULES)
        self.assertTrue(_row(unlocked_rows, "broad_arrows").enabled)
        self.assertTrue(_row(unlocked_rows, "feather_broad_bolts").enabled)

    def test_firemaking_rows_preserve_success_tooltip_and_default_current_target(self):
        rows = firemaking_target_rows(
            {
                "firemaking_level": 45,
                "inventory": {"Logs": 2, "Oak logs": 1},
            },
            FIREMAKING_DATA,
            FIREMAKING_ITEM_IMAGES,
            DEFAULT_FIREMAKING_TARGET,
        )

        logs = _row(rows, "logs")
        oak = _row(rows, "oak_logs")

        self.assertTrue(logs.current)
        self.assertTrue(oak.enabled)
        self.assertEqual(logs.icon_path, FIREMAKING_ITEM_IMAGES["Logs"])
        self.assertIn("Base XP: 40.0 per successful burn", logs.tooltip)
        self.assertIn("Input: Logs x1 (you have 2)", logs.tooltip)
        self.assertIn("Output: Ashes x1", logs.tooltip)
        self.assertIn("Success chance:", logs.tooltip)
        self.assertNotIn("FiremakingData.kt", logs.tooltip)

    def test_firemaking_rows_apply_region_quest_unlock_rules(self):
        player_data = {
            "firemaking_level": 99,
            "inventory": {"Arctic pine logs": 1},
            "current_firemaking": "arctic_pine_logs",
            "quests": {},
        }
        rows = firemaking_target_rows(
            player_data,
            FIREMAKING_DATA,
            FIREMAKING_ITEM_IMAGES,
            DEFAULT_FIREMAKING_TARGET,
            QUEST_UNLOCK_RULES,
        )

        arctic_pine = _row(rows, "arctic_pine_logs")
        self.assertFalse(arctic_pine.enabled)
        self.assertIn("The Fremennik Isles", arctic_pine.tooltip)

        player_data["quests"]["the_fremennik_isles"] = {"started": True, "progress": 6, "completed": True}
        unlocked_rows = firemaking_target_rows(
            player_data,
            FIREMAKING_DATA,
            FIREMAKING_ITEM_IMAGES,
            DEFAULT_FIREMAKING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "arctic_pine_logs").enabled)

    def test_fishing_rows_preserve_material_and_side_level_gates(self):
        rows = fishing_target_rows(
            {
                "fishing_level": 48,
                "strength_level": 1,
                "agility_level": 1,
                "inventory": {},
            },
            FISHING_DATA,
            FISHING_ITEM_IMAGES,
            DEFAULT_FISHING_TARGET,
        )

        sardine = _row(rows, "catch_sardine_herring")
        shrimp = _row(rows, "catch_shrimp_anchovies")
        leaping = _row(rows, "catch_leaping_fish")

        self.assertEqual(shrimp.label, "Catch shrimp (Lvl 1)/anchovies (Lvl 15)")
        self.assertEqual(sardine.label, "Catch sardine (Lvl 5)/herring (Lvl 10)")
        self.assertEqual(
            leaping.label,
            "Catch leaping trout (Lvl 48)/leaping salmon (Lvl 58)/leaping sturgeon (Lvl 70)",
        )
        self.assertFalse(sardine.enabled)
        self.assertIn("Materials: Fishing bait x1 (you have 0)", sardine.tooltip)
        self.assertIn("materials", sardine.tooltip)
        self.assertFalse(leaping.enabled)
        self.assertIn("side levels", leaping.tooltip)
        self.assertNotIn("rod", leaping.tooltip.lower())
        self.assertNotIn("harpoon", leaping.tooltip.lower())

    def test_fishing_rows_apply_quest_unlock_rules(self):
        rows = fishing_target_rows(
            {
                "fishing_level": 99,
                "strength_level": 99,
                "agility_level": 99,
                "inventory": {"Fishing bait": 1},
            },
            FISHING_DATA,
            FISHING_ITEM_IMAGES,
            DEFAULT_FISHING_TARGET,
            QUEST_UNLOCK_RULES,
        )

        monkfish = _row(rows, "catch_monkfish")
        karambwan = _row(rows, "catch_karambwan")
        slimy_eel = _row(rows, "catch_slimy_eel")
        self.assertFalse(monkfish.enabled)
        self.assertIn("Swan Song", monkfish.tooltip)
        self.assertFalse(karambwan.enabled)
        self.assertIn("Tai Bwo Wannai Trio", karambwan.tooltip)
        self.assertFalse(slimy_eel.enabled)
        self.assertIn("Priest in Peril", slimy_eel.tooltip)

    def test_hunter_rows_preserve_material_locks_and_current_target(self):
        rows = hunter_target_rows(
            {
                "hunter_level": 23,
                "inventory": {"Logs": 1},
                "current_hunter": "catch_wild_kebbit",
            },
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )

        wild_kebbit = _row(rows, "catch_wild_kebbit")
        barb_tailed = _row(rows, "catch_barb_tailed_kebbit")

        self.assertEqual(wild_kebbit.group, "deadfall")
        self.assertTrue(wild_kebbit.current)
        self.assertTrue(wild_kebbit.enabled)
        self.assertEqual(wild_kebbit.icon_path, HUNTER_ITEM_IMAGES["Kebbit claws"])
        self.assertIn("Outputs: Bones x1, Kebbit claws x1", wild_kebbit.tooltip)
        self.assertIn("Base XP: 128.0 per successful catch", wild_kebbit.tooltip)
        self.assertIn("Success chance:", wild_kebbit.tooltip)
        self.assertIn("Logs x1 (you have 1)", wild_kebbit.tooltip)
        self.assertIn("Reusable tools:", wild_kebbit.tooltip)
        self.assertIn("No reusable tools required", wild_kebbit.tooltip)
        self.assertFalse(barb_tailed.enabled)
        self.assertEqual(barb_tailed.locked_reasons, ("Hunter level 33",))

        locked_rows = hunter_target_rows(
            {
                "hunter_level": 23,
                "inventory": {},
                "current_hunter": "catch_wild_kebbit",
            },
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )
        locked_wild_kebbit = _row(locked_rows, "catch_wild_kebbit")
        self.assertFalse(locked_wild_kebbit.enabled)
        self.assertEqual(locked_wild_kebbit.locked_reasons, ("materials",))
        self.assertIn("Locked due to: materials", locked_wild_kebbit.tooltip)

        bird_rows = hunter_target_rows(
            {
                "hunter_level": 1,
                "inventory": {},
                "current_hunter": "catch_crimson_swift",
            },
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )
        crimson_swift = _row(bird_rows, "catch_crimson_swift")
        self.assertFalse(crimson_swift.enabled)
        self.assertEqual(crimson_swift.locked_reasons, ("Bird snare",))
        self.assertIn("Bird snare x1 (you have 0)", crimson_swift.tooltip)

    def test_hunter_rows_apply_quest_unlock_rules(self):
        player_data = {
            "hunter_level": 99,
            "inventory": {
                "Box trap": 1,
                "Butterfly net": 1,
                "Impling jar": 1,
                "Small fishing net": 1,
                "Rope": 1,
            },
            "quests": {},
            "current_hunter": "catch_ferret",
        }
        rows = hunter_target_rows(
            player_data,
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )

        ferret = _row(rows, "catch_ferret")
        pirate = _row(rows, "catch_pirate_impling_world")
        swamp_lizard = _row(rows, "catch_swamp_lizard")
        self.assertFalse(ferret.enabled)
        self.assertEqual(ferret.locked_reasons, ("Eagles' Peak",))
        self.assertIn("Eagles' Peak", ferret.tooltip)
        self.assertFalse(pirate.enabled)
        self.assertIn("Rocking Out", pirate.tooltip)
        self.assertFalse(swamp_lizard.enabled)
        self.assertIn("Priest in Peril", swamp_lizard.tooltip)

        player_data["quests"] = {
            "eagles_peak": {"started": True, "progress": 6, "completed": True},
            "rocking_out": {"started": True, "progress": 6, "completed": True},
            "priest_in_peril": {"started": True, "progress": 6, "completed": True},
        }
        unlocked_rows = hunter_target_rows(
            player_data,
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "catch_ferret").enabled)
        self.assertTrue(_row(unlocked_rows, "catch_pirate_impling_world").enabled)
        self.assertTrue(_row(unlocked_rows, "catch_swamp_lizard").enabled)

    def test_runecrafting_rows_apply_quest_unlock_rules(self):
        player_data = {
            "runecrafting_level": 99,
            "inventory": {"Pure essence": 1, "Cosmic talisman": 1},
            "equipment": {},
            "wicked_hood": {"fed_altars": []},
            "runecrafting_pouches": {},
            "quests": {
                "rune_mysteries": {"started": True, "progress": 6, "completed": True},
            },
            "current_runecrafting": "craft_cosmic_runes",
        }
        rows = runecrafting_target_rows(
            player_data,
            RUNECRAFTING_DATA,
            RUNECRAFTING_ITEM_IMAGES,
            RUNECRAFTING_POUCH_DATA,
            DEFAULT_RUNECRAFTING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        cosmic = _row(rows, "craft_cosmic_runes")
        self.assertFalse(cosmic.enabled)
        self.assertEqual(cosmic.locked_reasons, ("Lost City",))
        self.assertEqual(cosmic.group, "standard")
        self.assertEqual(cosmic.sort_key[:1], (27,))
        self.assertIn("Lost City", cosmic.tooltip)

        player_data["quests"]["lost_city"] = {"started": True, "progress": 6, "completed": True}
        unlocked_rows = runecrafting_target_rows(
            player_data,
            RUNECRAFTING_DATA,
            RUNECRAFTING_ITEM_IMAGES,
            RUNECRAFTING_POUCH_DATA,
            DEFAULT_RUNECRAFTING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "craft_cosmic_runes").enabled)

    def test_utility_rows_preserve_activity_icons_no_xp_text_and_locks(self):
        rows = utility_activity_rows(
            {"inventory": {}, "current_utility": "scavenge_chicken_feathers"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )

        feathers = _row(rows, "scavenge_chicken_feathers")
        nests = _row(rows, "open_bird_nest")

        self.assertTrue(feathers.current)
        self.assertTrue(feathers.enabled)
        self.assertEqual(os.path.basename(feathers.icon_path or ""), "scavenge_chicken_feathers.png")
        self.assertIn("No skill XP", feathers.tooltip)
        self.assertIn("Output: Feather x1", feathers.tooltip)
        self.assertIn("No materials required", feathers.tooltip)
        self.assertFalse(nests.enabled)
        self.assertIn("No XP", nests.tooltip)
        self.assertIn("Locked: cut trees until a bird nest drops.", nests.tooltip)

        hunter_supplies = _row(rows, "buy_hunter_supplies")
        self.assertFalse(hunter_supplies.enabled)
        self.assertIn("Runs once, then switches off", hunter_supplies.tooltip)
        self.assertIn("Bird snare x1", hunter_supplies.tooltip)
        self.assertIn("Butterfly jar x10", hunter_supplies.tooltip)
        self.assertIn("Coins x500 (you have 0)", hunter_supplies.tooltip)

        funded_rows = utility_activity_rows(
            {"inventory": {"Coins": 500}, "current_utility": "buy_hunter_supplies"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )
        funded_hunter_supplies = _row(funded_rows, "buy_hunter_supplies")
        self.assertTrue(funded_hunter_supplies.current)
        self.assertTrue(funded_hunter_supplies.enabled)
        self.assertEqual(os.path.basename(funded_hunter_supplies.icon_path or ""), "bird_snare.png")

    def test_utility_rows_apply_region_quest_unlock_rules(self):
        rows = utility_activity_rows(
            {"inventory": {}, "current_utility": "gather_thin_snails"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
            QUEST_UNLOCK_RULES,
        )

        snails = _row(rows, "gather_thin_snails")
        yak = _row(rows, "scavenge_raw_yak_meat")
        self.assertFalse(snails.enabled)
        self.assertIn("Priest in Peril", snails.tooltip)
        self.assertFalse(yak.enabled)
        self.assertIn("The Fremennik Isles", yak.tooltip)

        unlocked_rows = utility_activity_rows(
            {
                "inventory": {},
                "quests": {
                    "priest_in_peril": {"started": True, "progress": 6, "completed": True},
                    "the_fremennik_isles": {"started": True, "progress": 6, "completed": True},
                },
            },
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "gather_thin_snails").enabled)
        self.assertTrue(_row(unlocked_rows, "scavenge_raw_yak_meat").enabled)


if __name__ == "__main__":
    unittest.main()
