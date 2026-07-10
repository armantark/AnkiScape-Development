import unittest

from crafting_data import (
    CRAFTING_RECIPES,
    CRAFTING_RECIPES_BY_ID,
    DEFAULT_CRAFTING_TARGET,
    TANNING_ACTIVITIES,
    crafting_recipes_as_dict,
    tanning_activities_as_dict,
)


class TestCraftingData(unittest.TestCase):
    def test_recipe_ids_are_stable_and_unique(self):
        self.assertEqual(len(CRAFTING_RECIPES_BY_ID), len(CRAFTING_RECIPES))
        self.assertIn(DEFAULT_CRAFTING_TARGET, CRAFTING_RECIPES_BY_ID)

    def test_corrected_2011scape_values(self):
        data = crafting_recipes_as_dict()
        self.assertEqual(data["cut_emerald"]["exp"], 67.0)
        self.assertEqual(data["jewellery_sapphire_necklace"]["exp"], 55.0)
        self.assertEqual(data["spin_flax_to_bow_string"]["exp"], 15.0)
        self.assertNotIn("batch_size", data["spin_flax_to_bow_string"])
        self.assertEqual(data["silver_silver_bolts_unf"]["output_qty"], 10)

    def test_input_starved_high_tier_content_is_live(self):
        data = crafting_recipes_as_dict()
        self.assertIn("cut_dragonstone", data)
        self.assertIn("jewellery_dragonstone_ring", data)
        self.assertEqual(data["cut_dragonstone"]["requirements"], {"Uncut dragonstone": 1})
        self.assertEqual(data["jewellery_dragonstone_ring"]["requirements"], {"Gold bar": 1, "Dragonstone": 1})

    def test_every_recipe_has_output_and_source(self):
        for recipe in CRAFTING_RECIPES:
            self.assertTrue(recipe.output_item, recipe.id)
            self.assertTrue(recipe.source.endswith((".kt", ".kts")), recipe.id)

    def test_molten_glass_matches_furnace_source(self):
        # furnaces.plugin.kts handleMoltenGlass: 1 Soda ash + 1 Bucket of sand
        # -> Molten glass + the emptied Bucket back, 20.0 Crafting XP.
        data = crafting_recipes_as_dict()
        spec = data["glass_molten_glass"]
        self.assertEqual(spec["level"], 1)
        self.assertEqual(spec["exp"], 20.0)
        self.assertEqual(spec["requirements"], {"Soda ash": 1, "Bucket of sand": 1})
        self.assertEqual(spec["output_item"], "Molten glass")
        self.assertEqual(spec["byproducts"], {"Bucket": 1})
        self.assertEqual(spec["family"], "glass")
        self.assertTrue(spec["source"].endswith("furnaces/furnaces.plugin.kts"))

    def test_runtime_bound_crafting_remainder_matches_2011scape(self):
        data = crafting_recipes_as_dict()
        expected = {
            "glass_empty_candle_lantern": (4, 19.0, {"Molten glass": 1}, "Candle lantern", 4527),
            "glass_empty_oil_lamp": (12, 25.0, {"Molten glass": 1}, "Oil lamp", 4525),
            "glass_fishbowl": (42, 42.5, {"Molten glass": 1}, "Fishbowl", 6667),
            "glass_lantern_lens": (49, 55.0, {"Molten glass": 1}, "Lantern lens", 4542),
            "glass_empty_light_orb": (87, 70.0, {"Molten glass": 1}, "Empty light orb", 10980),
            "jewellery_ring_of_slaying_8": (75, 15.0, {"Gold bar": 1, "Enchanted gem": 1}, "Ring of slaying (8)", 13281),
            "silver_silvthrill_rod": (25, 55.0, {"Silver bar": 1, "Mithril bar": 1, "Sapphire": 1}, "Silvthrill rod", 7637),
            "silver_silvthrill_chain": (47, 100.0, {"Silver bar": 1, "Mithril bar": 1}, "Silvthril chain", 13154),
        }
        for recipe_id, (level, exp, requirements, output_item, source_item_id) in expected.items():
            self.assertEqual(data[recipe_id]["level"], level)
            self.assertEqual(data[recipe_id]["exp"], exp)
            self.assertEqual(data[recipe_id]["requirements"], requirements)
            self.assertEqual(data[recipe_id]["output_item"], output_item)
            self.assertEqual(data[recipe_id]["source_item_id"], source_item_id)
        self.assertIn("CRAFT_ROS", data["jewellery_ring_of_slaying_8"]["notes"])

    def test_item_combination_and_button_polishing_rows_match_2011scape(self):
        data = crafting_recipes_as_dict()
        expected = {
            "combine_strange_skull": (1, 0.0, {"Left skull half": 1, "Right skull half": 1}, "Strange skull", 9009),
            "combine_runed_sceptre": (1, 0.0, {"Bottom of sceptre": 1, "Top of sceptre": 1}, "Runed sceptre", 9012),
            "combine_skull_sceptre": (1, 0.0, {"Strange skull": 1, "Runed sceptre": 1}, "Skull sceptre", 9013),
            "combine_bullseye_lantern": (49, 0.0, {"Bullseye lantern": 1, "Lantern lens": 1}, "Bullseye lantern", 4546),
            "combine_bullseye_emerald_lantern": (49, 0.0, {"Bullseye lantern": 1, "Emerald lens": 1}, "Emerald lantern", 9064),
            "combine_oil_lantern": (50, 50.0, {"Oil lamp": 1, "Oil lantern frame": 1}, "Oil lantern", 4537),
            "combine_studded_chaps": (44, 42.0, {"Leather chaps": 1, "Steel studs": 1}, "Studded chaps", 1097),
            "combine_spiky_vambraces": (32, 6.0, {"Leather vambraces": 1, "Kebbit claws": 1}, "Spiky vambraces", 10077),
            "combine_green_spiky_vambraces": (32, 6.0, {"Green d'hide vambraces": 1, "Kebbit claws": 1}, "Green spiky vambraces", 10079),
            "combine_blue_spiky_vambraces": (32, 6.0, {"Blue d'hide vambraces": 1, "Kebbit claws": 1}, "Blue spiky vambraces", 10081),
            "combine_red_spiky_vambraces": (32, 6.0, {"Red d'hide vambraces": 1, "Kebbit claws": 1}, "Red spiky vambraces", 10083),
            "combine_black_spiky_vambraces": (32, 6.0, {"Black d'hide vambraces": 1, "Kebbit claws": 1}, "Black spiky vambraces", 10085),
            "chisel_crab_helmet": (15, 32.5, {"Fresh crab shell": 1}, "Crab helmet", 7539),
            "chisel_crab_claw": (15, 32.5, {"Fresh crab claw": 1}, "Crab claw", 7537),
            "combine_seaweed_net": (52, 83.0, {"Unfinished net": 1, "Bronze wire": 1}, "Empty seaweed net", 14859),
            "combine_armadyl_battlestaff": (77, 150.0, {"Battlestaff": 1, "Orb of armadyl": 1}, "Armadyl battlestaff", 21777),
            "string_gold_amulet": (1, 4.0, {"Gold amulet": 1, "Ball of wool": 1}, "Gold amulet", 1692),
            "string_sapphire_amulet": (1, 4.0, {"Sapphire amulet": 1, "Ball of wool": 1}, "Sapphire amulet", 1694),
            "string_emerald_amulet": (1, 4.0, {"Emerald amulet": 1, "Ball of wool": 1}, "Emerald amulet", 1696),
            "string_ruby_amulet": (1, 4.0, {"Ruby amulet": 1, "Ball of wool": 1}, "Ruby amulet", 1698),
            "string_diamond_amulet": (1, 4.0, {"Diamond amulet": 1, "Ball of wool": 1}, "Diamond amulet", 1700),
            "string_onyx_amulet": (1, 4.0, {"Onyx amulet": 1, "Ball of wool": 1}, "Onyx amulet", 6581),
            "string_unblessed_symbol": (1, 4.0, {"Unstrung symbol": 1, "Ball of wool": 1}, "Unblessed symbol", 1716),
            "string_unpowered_symbol": (1, 4.0, {"Unstrung emblem": 1, "Ball of wool": 1}, "Unpowered symbol", 1722),
            "polish_buttons": (3, 5.0, {"Buttons": 1}, "Polished buttons", 10496),
        }
        for recipe_id, (level, exp, requirements, output_item, source_item_id) in expected.items():
            self.assertEqual(data[recipe_id]["level"], level)
            self.assertEqual(data[recipe_id]["exp"], exp)
            self.assertEqual(data[recipe_id]["requirements"], requirements)
            self.assertEqual(data[recipe_id]["output_item"], output_item)
            self.assertEqual(data[recipe_id]["source_item_id"], source_item_id)
        self.assertEqual(data["chisel_crab_helmet"]["station"], "chisel")
        self.assertTrue(data["polish_buttons"]["source"].endswith("other/polished_button.plugin.kts"))

    def test_root_crossbow_strings_and_milestone_capes_match_runtime_actions(self):
        data = crafting_recipes_as_dict()
        for root in ("Oak", "Willow", "Maple", "Yew", "Magic", "Spirit"):
            recipe = data[f"spin_{root.lower()}_roots_to_crossbow_string"]
            self.assertEqual(recipe["level"], 10)
            self.assertEqual(recipe["exp"], 15.0)
            self.assertEqual(recipe["requirements"], {f"{root} roots": 1})
            self.assertEqual(recipe["output_item"], "Crossbow string")
            self.assertEqual(recipe["source_enum"], "CBOW_STRING1")
        for tier in range(10, 100, 10):
            recipe = data[f"weave_milestone_cape_{tier}"]
            self.assertEqual(recipe["level"], tier)
            self.assertEqual(recipe["exp"], float(tier))
            self.assertEqual(recipe["requirements"], {"Ball of wool": tier // 10})
            self.assertEqual(recipe["output_item"], f"Milestone cape ({tier})")
            self.assertEqual(recipe["source_item_id"], 20734 + tier // 10)
            self.assertIn("every skill", recipe["notes"])

    def test_leather_rows_match_2011scape(self):
        data = crafting_recipes_as_dict()
        leather_recipes = tuple(recipe for recipe in CRAFTING_RECIPES if recipe.family == "leather")
        self.assertEqual(len(leather_recipes), 27)
        self.assertTrue(all(recipe.required_items == (("Thread", 1),) for recipe in leather_recipes))
        self.assertTrue(all(recipe.consume_thread_on_roll for recipe in leather_recipes))
        expected = {
            "leather_leather_cowl": (9, 18.5, {"Leather": 1}, "Leather cowl"),
            "leather_leather_vambraces": (11, 22.0, {"Leather": 1}, "Leather vambraces"),
            "leather_leather_chaps": (18, 27.0, {"Leather": 1}, "Leather chaps"),
            "leather_coif": (38, 37.0, {"Leather": 1}, "Coif"),
            "leather_snakeskin_boots": (45, 30.0, {"Snakeskin": 6}, "Snakeskin boots"),
            "leather_snakeskin_vambraces": (47, 35.0, {"Snakeskin": 8}, "Snakeskin vambraces"),
            "leather_snakeskin_bandana": (48, 45.0, {"Snakeskin": 5}, "Snakeskin bandana"),
            "leather_snakeskin_chaps": (51, 50.0, {"Snakeskin": 12}, "Snakeskin chaps"),
            "leather_snakeskin_body": (53, 55.0, {"Snakeskin": 15}, "Snakeskin body"),
            "leather_yakhide_armour_10824": (43, 32.0, {"Cured yak-hide": 1}, "Yak-hide armour"),
            "leather_yakhide_armour": (46, 32.0, {"Cured yak-hide": 2}, "Yak-hide armour"),
            "leather_green_dhide_vambraces": (57, 62.0, {"Green dragon leather": 1}, "Green d'hide vambraces"),
            "leather_green_dhide_chaps": (60, 124.0, {"Green dragon leather": 2}, "Green d'hide chaps"),
            "leather_blue_dhide_vambraces": (66, 70.0, {"Blue dragon leather": 1}, "Blue d'hide vambraces"),
            "leather_blue_dhide_chaps": (68, 140.0, {"Blue dragon leather": 2}, "Blue d'hide chaps"),
            "leather_red_dhide_vambraces": (73, 78.0, {"Red dragon leather": 1}, "Red d'hide vambraces"),
            "leather_red_dhide_chaps": (75, 156.0, {"Red dragon leather": 2}, "Red d'hide chaps"),
            "leather_red_dhide_body": (77, 234.0, {"Red dragon leather": 3}, "Red d'hide body"),
            "leather_black_dhide_vambraces": (79, 86.0, {"Black dragon leather": 1}, "Black d'hide vambraces"),
            "leather_black_dhide_chaps": (82, 172.0, {"Black dragon leather": 2}, "Black d'hide chaps"),
        }
        self.assertEqual(len(TANNING_ACTIVITIES), 8)
        for recipe_id, (level, exp, requirements, output_item) in expected.items():
            self.assertEqual(data[recipe_id]["level"], level)
            self.assertEqual(data[recipe_id]["exp"], exp)
            self.assertEqual(data[recipe_id]["requirements"], requirements)
            self.assertEqual(data[recipe_id]["output_item"], output_item)
        for recipe in leather_recipes:
            self.assertEqual(data[recipe.id]["required_items"], {"Thread": 1})
            self.assertTrue(data[recipe.id]["consume_thread_on_roll"])

    def test_tanning_rows_match_2011scape(self):
        self.assertEqual(
            tuple(
                (activity.id, activity.raw_item, activity.output_item, activity.price, activity.source_enum)
                for activity in TANNING_ACTIVITIES
            ),
            (
                ("tan_soft_leather", "Cowhide", "Leather", 1, "SOFT_LEATHER"),
                ("tan_hard_leather", "Cowhide", "Hard leather", 3, "HARD_LEATHER"),
                ("tan_snakeskin", "Snake hide", "Snakeskin", 15, "SNAKESKIN"),
                ("tan_swamp_snakeskin", "Snake hide", "Snakeskin", 20, "SNAKESKIN_SWAMP"),
                ("tan_green_dragonhide", "Green dragonhide", "Green dragon leather", 20, "GREEN_DRAGONHIDE"),
                ("tan_blue_dragonhide", "Blue dragonhide", "Blue dragon leather", 20, "BLUE_DRAGONHIDE"),
                ("tan_red_dragonhide", "Red dragonhide", "Red dragon leather", 20, "RED_DRAGONHIDE"),
                ("tan_black_dragonhide", "Black dragonhide", "Black dragon leather", 20, "BLACK_DRAGONHIDE"),
            ),
        )
        self.assertEqual(tanning_activities_as_dict()["tan_black_dragonhide"]["batch_size"], 28)


if __name__ == "__main__":
    unittest.main()
