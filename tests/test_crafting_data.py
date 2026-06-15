import unittest

from crafting_data import CRAFTING_RECIPES, CRAFTING_RECIPES_BY_ID, DEFAULT_CRAFTING_TARGET, crafting_recipes_as_dict


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


if __name__ == "__main__":
    unittest.main()
