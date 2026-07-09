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

    def test_leather_rows_match_2011scape(self):
        data = crafting_recipes_as_dict()
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
