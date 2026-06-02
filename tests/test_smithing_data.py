import unittest

from smithing_data import (
    DEFAULT_SMITHING_TARGET,
    SMITHING_RECIPES,
    SMITHING_RECIPES_BY_ID,
    smithing_bars_as_dict,
    smithing_forge_recipe_ids,
    smithing_recipes_as_dict,
)


class TestSmithingData(unittest.TestCase):
    def test_source_generated_recipe_counts_and_defaults(self):
        self.assertEqual(len(SMITHING_RECIPES), 166)
        self.assertEqual(len(smithing_bars_as_dict()), 9)
        self.assertEqual(len(smithing_forge_recipe_ids()), 157)
        self.assertEqual(DEFAULT_SMITHING_TARGET, "smelt_bronze_bar")
        self.assertEqual(len(SMITHING_RECIPES_BY_ID), len(SMITHING_RECIPES))

    def test_smelt_table_matches_audited_source_values(self):
        bars = smithing_bars_as_dict()
        self.assertEqual(set(bars), {
            "Bronze bar",
            "Blurite bar",
            "Iron bar",
            "Silver bar",
            "Steel bar",
            "Gold bar",
            "Mithril bar",
            "Adamant bar",
            "Rune bar",
        })
        self.assertEqual(bars["Blurite bar"]["level"], 8)
        self.assertEqual(bars["Blurite bar"]["requirements"], {"Blurite ore": 1})
        self.assertAlmostEqual(bars["Silver bar"]["exp"], 13.7)
        self.assertEqual(bars["Steel bar"]["requirements"], {"Iron ore": 1, "Coal": 2})
        self.assertEqual(bars["Rune bar"]["requirements"], {"Runite ore": 1, "Coal": 8})

    def test_forge_xp_is_derived_from_bar_tier_and_shape(self):
        recipes = smithing_recipes_as_dict()
        xp_per_bar = {
            "Bronze bar": 12.5,
            "Blurite bar": 16.0,
            "Iron bar": 25.0,
            "Steel bar": 37.5,
            "Mithril bar": 50.0,
            "Adamant bar": 62.5,
            "Rune bar": 75.0,
        }
        for recipe_id in smithing_forge_recipe_ids():
            recipe = recipes[recipe_id]
            requirements = recipe["requirements"]
            self.assertEqual(len(requirements), 1, recipe_id)
            bar_name, bars_required = next(iter(requirements.items()))
            self.assertAlmostEqual(recipe["exp"], xp_per_bar[bar_name] * bars_required, msg=recipe_id)

    def test_forge_spot_checks_cover_levels_outputs_and_categories(self):
        recipes = smithing_recipes_as_dict()
        self.assertEqual(recipes["forge_bronze_platebody"]["level"], 18)
        self.assertAlmostEqual(recipes["forge_bronze_platebody"]["exp"], 62.5)
        self.assertEqual(recipes["forge_rune_platebody"]["level"], 99)
        self.assertAlmostEqual(recipes["forge_rune_platebody"]["exp"], 375.0)
        self.assertEqual(recipes["forge_blurite_bolts_unf"]["output_qty"], 10)
        self.assertEqual(recipes["forge_blurite_limbs"]["level"], 13)
        self.assertEqual(recipes["forge_iron_pickaxe"]["requirements"], {"Iron bar": 2})
        self.assertEqual(recipes["forge_iron_pickaxe"]["category"], "tool")
        self.assertEqual(recipes["forge_steel_studs"]["requirements"], {"Steel bar": 1})


if __name__ == "__main__":
    unittest.main()
