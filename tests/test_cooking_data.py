import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.cooking_data import (
    BARLEY_MALT_SOURCE,
    COOKING_PREP_ACTIVITIES,
    COOKING_SOURCE_PATH,
    COOKING_TARGETS,
    COOKING_TARGETS_BY_ID,
    GUT_FISH_SOURCE_PATH,
    LAVA_EEL_WIKI_SOURCE,
    SEAWEED_COOKING_SOURCE_PATH,
    TIGER_SHARK_WIKI_SOURCE,
    cooking_extra_items_as_dict,
    cooking_prep_activities_as_dict,
    cooking_targets_as_dict,
)


class TestCookingData(unittest.TestCase):
    def test_source_backed_targets_preserve_2011scape_rows(self):
        data = cooking_targets_as_dict()

        self.assertEqual(len(COOKING_TARGETS), 92)
        self.assertEqual(set(data), set(COOKING_TARGETS_BY_ID))
        self.assertEqual(data["cook_shrimps"]["level"], 1)
        self.assertEqual(data["cook_shrimps"]["exp"], 30.0)
        self.assertEqual(data["cook_shrimps"]["requirements"], {"Raw shrimps": 1})
        self.assertEqual(data["cook_shrimps"]["output_item"], "Shrimps")
        self.assertEqual(data["cook_shrimps"]["burnt_item"], "Burnt shrimp")
        self.assertEqual(data["cook_shrimps"]["low_chance"], 128)
        self.assertEqual(data["cook_shrimps"]["high_chance"], 512)
        self.assertEqual(data["cook_shrimps"]["source"], COOKING_SOURCE_PATH)

        self.assertEqual(data["cook_summer_pie"]["level"], 95)
        self.assertEqual(data["cook_summer_pie"]["exp"], 260.0)
        self.assertEqual(data["cook_rocktail"]["level"], 93)
        self.assertEqual(data["cook_rocktail"]["exp"], 225.0)
        self.assertEqual(data["cook_tiger_shark"]["level"], 95)
        self.assertEqual(data["cook_tiger_shark"]["exp"], 230.0)
        self.assertEqual(
            data["cook_tiger_shark"]["requirements"],
            {"Raw tiger shark": 1},
        )
        self.assertEqual(data["cook_tiger_shark"]["output_item"], "Tiger shark")
        self.assertEqual(data["cook_tiger_shark"]["burnt_item"], "Burnt tiger shark")
        self.assertEqual(data["cook_tiger_shark"]["source"], TIGER_SHARK_WIKI_SOURCE)
        self.assertEqual(data["cook_lava_eel"]["level"], 53)
        self.assertEqual(data["cook_lava_eel"]["requirements"], {"Raw lava eel": 1})
        self.assertEqual(data["cook_lava_eel"]["output_item"], "Lava eel")
        self.assertEqual(data["cook_lava_eel"]["exp"], 30.0)
        self.assertEqual(data["cook_lava_eel"]["source"], LAVA_EEL_WIKI_SOURCE)
        self.assertTrue(data["cook_lava_eel"]["source_always_succeeds"])
        poison = data["cook_poison_karambwan"]
        self.assertEqual(poison["level"], 1)
        self.assertEqual(poison["requirements"], {"Raw karambwan": 1})
        self.assertEqual(poison["output_item"], "Poison karambwan")
        self.assertEqual(poison["burnt_item"], "Burnt karambwan")
        self.assertEqual(poison["exp"], 80.0)
        self.assertEqual(poison["source_success_formula"]["minimum"], 0.5)
        self.assertEqual(poison["source_success_formula"]["level_divisor"], 20.0)

        thorough = data["cook_karambwan_thoroughly"]
        self.assertEqual(thorough["level"], 30)
        self.assertEqual(thorough["requirements"], {"Raw karambwan": 1})
        self.assertEqual(thorough["output_item"], "Cooked karambwan")
        self.assertEqual(thorough["exp"], 190.0)
        self.assertTrue(thorough["source_always_succeeds"])

        karambwanji = data["cook_karambwanji"]
        self.assertEqual(karambwanji["level"], 1)
        self.assertEqual(karambwanji["requirements"], {"Raw karambwanji": 1})
        self.assertEqual(karambwanji["output_item"], "Karambwanji")
        self.assertEqual(karambwanji["burnt_item"], "Ashes")
        self.assertEqual(karambwanji["exp"], 10.0)
        self.assertEqual(karambwanji["source_success_formula"]["level_divisor"], 28.0)
        items = cooking_extra_items_as_dict()
        self.assertEqual(items["Raw karambwan"]["item_id"], 3142)
        self.assertTrue(items["Raw karambwan"]["tradeable"])
        self.assertEqual(items["Cooked karambwan"]["item_id"], 3144)
        self.assertTrue(items["Cooked karambwan"]["tradeable"])
        self.assertEqual(items["Poison karambwan"]["item_id"], 3146)
        self.assertFalse(items["Poison karambwan"]["tradeable"])
        self.assertEqual(items["Burnt karambwan"]["item_id"], 3148)
        self.assertFalse(items["Burnt karambwan"]["tradeable"])
        self.assertEqual(items["Karambwanji"]["item_id"], 3151)
        self.assertFalse(items["Karambwanji"]["tradeable"])
        malt = data["malt_barley"]
        self.assertEqual(malt["requirements"], {"Barley": 1})
        self.assertEqual(malt["output_item"], "Barley malt")
        self.assertEqual(malt["level"], 1)
        self.assertEqual(malt["exp"], 0.0)
        self.assertTrue(malt["source_always_succeeds"])
        self.assertEqual(malt["source"], BARLEY_MALT_SOURCE)
        self.assertEqual(items["Barley"]["item_id"], 6006)
        self.assertFalse(items["Barley"]["stackable"])
        self.assertEqual(items["Barley malt"]["item_id"], 6008)
        self.assertFalse(items["Barley malt"]["stackable"])
        self.assertFalse(items["Ale yeast"]["stackable"])
        wine = data["make_wine"]
        self.assertEqual(wine["level"], 35)
        self.assertEqual(wine["exp"], 200.0)
        self.assertEqual(
            wine["requirements"],
            {"Grapes": 1, "Jug of water": 1},
        )
        self.assertEqual(wine["output_item"], "Jug of wine")
        self.assertEqual(wine["alternate_output_item"], "Jug of bad wine")
        self.assertTrue(wine["alternate_is_failure"])
        self.assertEqual(wine["alternate_output_exp"], 0.0)
        self.assertEqual(wine["failure_kind"], "bad_wine")
        self.assertEqual(wine["source_success_formula"]["minimum"], 0.6)
        self.assertEqual(wine["source_success_formula"]["level_divisor"], 68.0)
        self.assertEqual(data["cook_spider_on_a_stick"]["level"], 16)
        self.assertEqual(data["cook_spider_on_a_stick"]["exp"], 80.0)
        self.assertEqual(
            data["cook_spider_on_a_stick"]["requirements"],
            {"Raw spider on stick": 1},
        )
        self.assertEqual(
            data["cook_spider_on_a_stick"]["output_item"], "Spider on stick"
        )
        self.assertEqual(
            data["cook_spider_on_a_stick"]["burnt_item"], "Burnt spider"
        )

    def test_dwarven_stout_rows_model_one_full_vat_and_optional_stuff(self):
        data = cooking_targets_as_dict()
        ordinary = data["brew_dwarven_stout"]
        boosted = data["brew_dwarven_stout_with_the_stuff"]

        expected_materials = {
            "Ale yeast": 1,
            "Bucket of water": 2,
            "Barley malt": 2,
            "Hammerstone hops": 4,
            "Beer glass": 8,
        }
        self.assertEqual(ordinary["requirements"], expected_materials)
        self.assertEqual(boosted["requirements"], {**expected_materials, "The stuff": 1})
        for row, chance in ((ordinary, 0.10), (boosted, 0.75)):
            self.assertEqual(row["level"], 19)
            self.assertEqual(row["exp"], 215.0)
            self.assertEqual(row["output_item"], "Dwarven stout (m)")
            self.assertEqual(row["output_qty"], 8)
            self.assertEqual(row["alternate_output_item"], "Dwarven stout")
            self.assertEqual(row["alternate_output_qty"], 8)
            self.assertEqual(row["byproducts"], {"Bucket": 2})
            self.assertEqual(row["source_success_formula"]["base"], chance)

        items = cooking_extra_items_as_dict()
        self.assertEqual(items["Ale yeast"]["item_id"], 5767)
        self.assertEqual(items["Dwarven stout"]["item_id"], 1913)
        self.assertEqual(items["Dwarven stout (m)"]["item_id"], 5747)
        self.assertEqual(items["The stuff"]["category"], "material")

    def test_runtime_extra_targets_preserve_live_source_rows(self):
        data = cooking_targets_as_dict()

        self.assertEqual(data["gut_leaping_trout"]["requirements"], {"Leaping trout": 1})
        self.assertEqual(data["gut_leaping_trout"]["output_item"], "Roe")
        self.assertEqual(data["gut_leaping_trout"]["exp"], 10.0)
        self.assertEqual(data["gut_leaping_trout"]["source"], GUT_FISH_SOURCE_PATH)
        self.assertTrue(data["gut_leaping_trout"]["source_no_level_requirement"])
        self.assertEqual(data["gut_leaping_trout"]["byproduct_chance"], 0.5)
        self.assertEqual(data["gut_leaping_salmon"]["byproduct_chance"], 0.75)
        self.assertEqual(data["gut_leaping_sturgeon"]["output_item"], "Caviar")
        self.assertEqual(data["gut_leaping_sturgeon"]["exp"], 15.0)
        self.assertEqual(data["gut_leaping_sturgeon"]["byproduct_chance"], 5.0 / 6.0)
        self.assertEqual(data["burn_seaweed"]["requirements"], {"Seaweed": 1})
        self.assertEqual(data["burn_seaweed"]["output_item"], "Soda ash")
        self.assertEqual(data["burn_seaweed"]["exp"], 1.0)
        self.assertTrue(data["burn_seaweed"]["source_always_succeeds"])
        self.assertEqual(data["burn_seaweed"]["source"], SEAWEED_COOKING_SOURCE_PATH)

    def test_secondary_sinew_targets_are_distinct_stable_actions(self):
        data = cooking_targets_as_dict()

        self.assertEqual(data["cook_beef"]["output_item"], "Cooked meat")
        self.assertEqual(data["render_beef_sinew"]["output_item"], "Sinew")
        self.assertEqual(data["render_beef_sinew"]["requirements"], {"Raw beef": 1})
        self.assertEqual(data["render_beef_sinew"]["output_variant"], "secondary")
        self.assertEqual(data["render_bear_sinew"]["output_item"], "Sinew")

    def test_prep_activities_are_no_xp_utility_bridges(self):
        data = cooking_prep_activities_as_dict()

        self.assertEqual(len(data), len(COOKING_PREP_ACTIVITIES))
        self.assertEqual(data["gather_grain"]["requirements"], {})
        self.assertEqual(data["gather_grain"]["output_item"], "Grain")
        self.assertEqual(data["gather_grain"]["group"], "gathering")
        self.assertEqual(data["grind_grain_to_flour"]["requirements"], {"Grain": 1, "Empty pot": 1})
        self.assertEqual(
            data["wet_flour_to_bread_dough"]["requirements"],
            {"Pot of flour": 1, "Bucket of water": 1},
        )
        self.assertEqual(
            data["wet_flour_to_pizza_base"]["outputs"],
            {"Pizza base": 1, "Empty pot": 1, "Bucket": 1},
        )
        self.assertEqual(data["draw_bucket_of_water"]["requirements"], {"Bucket": 1})
        self.assertEqual(
            data["skewer_spider_on_a_stick"]["requirements"],
            {"Spider carcass": 1, "Skewer stick": 1},
        )
        self.assertEqual(
            data["skewer_spider_on_a_stick"]["output_item"],
            "Raw spider on stick",
        )
        # Shop-covered gather bridges and buy_bucket retired 2026-07-07:
        # their outputs are live NPC shop stock at cache prices.
        for retired in ("buy_bucket", "gather_potatoes", "gather_cheese", "scavenge_raw_yak_meat", "gather_thin_snails"):
            self.assertNotIn(retired, data)
        self.assertEqual(data["make_pie_shell"]["requirements"], {"Pastry dough": 1, "Pie dish": 1})
        self.assertEqual(
            data["assemble_uncooked_pizza"]["requirements"],
            {"Pizza base": 1, "Tomato": 1, "Cheese": 1},
        )
        self.assertEqual(data["assemble_uncooked_pizza"]["batch_size"], 28)

    def test_extra_items_use_food_category_and_burnt_junk_tradeability(self):
        extra = cooking_extra_items_as_dict()

        self.assertEqual(extra["Shrimps"]["category"], "food")
        self.assertEqual(extra["Cooked meat"]["category"], "food")
        self.assertEqual(extra["Burnt fish"]["category"], "food")
        self.assertFalse(extra["Burnt fish"]["tradeable"])
        self.assertFalse(extra["Burnt shrimp"]["tradeable"])
        self.assertEqual(extra["Crayfish"]["item_id"], 13433)
        self.assertTrue(extra["Crayfish"]["tradeable"])
        self.assertEqual(extra["Raw crayfish"]["item_id"], 13435)
        self.assertFalse(extra["Raw crayfish"]["tradeable"])
        self.assertEqual(extra["Burnt crayfish"]["item_id"], 13437)
        self.assertFalse(extra["Burnt crayfish"]["tradeable"])
        self.assertFalse(extra["Raw lava eel"]["tradeable"])
        self.assertFalse(extra["Lava eel"]["tradeable"])
        self.assertEqual(extra["Spider carcass"]["item_id"], 6291)
        self.assertEqual(extra["Raw spider on stick"]["item_id"], 6293)
        self.assertEqual(extra["Spider on stick"]["item_id"], 6297)
        self.assertEqual(extra["Burnt spider"]["item_id"], 6301)
        self.assertFalse(extra["Burnt spider"]["tradeable"])
        self.assertEqual(extra["Skewer stick"]["category"], "crafted")
        self.assertTrue(extra["Skewer stick"]["tradeable"])
        self.assertEqual(extra["Grapes"]["item_id"], 1987)
        self.assertEqual(extra["Jug of water"]["item_id"], 1937)
        self.assertEqual(extra["Jug of wine"]["item_id"], 1993)
        self.assertEqual(extra["Jug of bad wine"]["item_id"], 1991)
        self.assertFalse(extra["Jug of bad wine"]["tradeable"])
        self.assertEqual(extra["Empty pot"]["category"], "crafted")
        self.assertEqual(extra["Bowl of water"]["category"], "material")
        self.assertEqual(extra["Clay"]["category"], "ore")


if __name__ == "__main__":
    unittest.main()
