import unittest

from cooking_data import (
    COOKING_PREP_ACTIVITIES,
    COOKING_SOURCE_PATH,
    COOKING_TARGETS,
    COOKING_TARGETS_BY_ID,
    cooking_extra_items_as_dict,
    cooking_prep_activities_as_dict,
    cooking_targets_as_dict,
)


class TestCookingData(unittest.TestCase):
    def test_source_backed_targets_preserve_2011scape_rows(self):
        data = cooking_targets_as_dict()

        self.assertEqual(len(COOKING_TARGETS), 54)
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
        self.assertEqual(data["wet_flour_to_bread_dough"]["requirements"], {"Pot of flour": 1})
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
        self.assertFalse(extra["Crayfish"]["tradeable"])
        self.assertEqual(extra["Empty pot"]["category"], "crafted")
        self.assertEqual(extra["Bowl of water"]["category"], "material")
        self.assertEqual(extra["Clay"]["category"], "ore")


if __name__ == "__main__":
    unittest.main()
