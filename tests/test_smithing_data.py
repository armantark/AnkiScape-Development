import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.smithing_data import (
    DEFAULT_SMITHING_TARGET,
    SMITHING_RECIPES,
    SMITHING_RECIPES_BY_ID,
    smithing_bars_as_dict,
    smithing_forge_recipe_ids,
    smithing_recipes_as_dict,
)


class TestSmithingData(unittest.TestCase):
    def test_source_generated_recipe_counts_and_defaults(self):
        self.assertEqual(len(SMITHING_RECIPES), 168)
        self.assertEqual(len(smithing_bars_as_dict()), 9)
        self.assertEqual(len(smithing_forge_recipe_ids()), 158)
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
            if recipe_id == "repair_dragon_sq_shield":
                continue
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

    def test_dragon_sq_shield_assembly_matches_live_plugin(self):
        recipe = smithing_recipes_as_dict()["repair_dragon_sq_shield"]
        self.assertEqual(recipe["station"], "anvil")
        self.assertEqual(recipe["level"], 60)
        self.assertAlmostEqual(recipe["exp"], 70.0)
        self.assertEqual(recipe["requirements"], {"Shield left half": 1, "Shield right half": 1})
        self.assertEqual(recipe["output_item"], "Dragon sq shield")
        self.assertEqual(recipe["output_qty"], 1)
        self.assertEqual(recipe["source_item_id"], 1187)
        self.assertEqual(recipe["source_enum"], "DRAGON_SQ_SHIELD")

    def test_cannonballs_match_pinned_pre_eoc_recipe(self):
        recipe = smithing_recipes_as_dict()["forge_cannonballs"]
        self.assertEqual(recipe["station"], "furnace_process")
        self.assertEqual(recipe["level"], 35)
        self.assertEqual(recipe["exp"], 25.6)
        self.assertEqual(recipe["requirements"], {"Steel bar": 1})
        self.assertEqual(recipe["required_items"], {"Ammo mould": 1})
        self.assertEqual(recipe["output_item"], "Cannonball")
        self.assertEqual(recipe["output_qty"], 4)
        self.assertEqual(recipe["source_item_id"], 2)
        self.assertIn("oldid=6541276", recipe["source"])


if __name__ == "__main__":
    unittest.main()
