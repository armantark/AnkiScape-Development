import os
import unittest

from constants import FLETCHED_ITEM_IMAGES, FLETCHING_DATA
from fletching_data import BROAD_FLETCHING_ABILITY, fletching_item_names


class TestFletchingData(unittest.TestCase):
    def test_source_backed_rows_replace_pilot_arrow_shaft_rows(self):
        self.assertEqual(FLETCHING_DATA["arrow_shafts"]["requirements"], {"Logs": 1})
        self.assertEqual(FLETCHING_DATA["arrow_shafts"]["output_qty"], 15)
        self.assertAlmostEqual(FLETCHING_DATA["arrow_shafts"]["exp"], 5.0)
        for removed_target in (
            "oak_arrow_shafts",
            "willow_arrow_shafts",
            "maple_arrow_shafts",
            "yew_arrow_shafts",
            "magic_arrow_shafts",
        ):
            self.assertNotIn(removed_target, FLETCHING_DATA)

    def test_representative_whittling_stringing_and_special_rows_match_source(self):
        self.assertEqual(FLETCHING_DATA["wooden_stock"]["level"], 9)
        self.assertEqual(FLETCHING_DATA["wooden_stock"]["requirements"], {"Logs": 1})
        self.assertEqual(FLETCHING_DATA["wooden_stock"]["output_item"], "Wooden stock")
        self.assertAlmostEqual(FLETCHING_DATA["wooden_stock"]["exp"], 6.0)

        self.assertEqual(FLETCHING_DATA["string_magic_longbow"]["requirements"], {"Magic longbow (u)": 1, "Bow string": 1})
        self.assertEqual(FLETCHING_DATA["string_magic_longbow"]["output_item"], "Magic longbow")
        self.assertAlmostEqual(FLETCHING_DATA["string_magic_longbow"]["exp"], 91.5)

        self.assertEqual(FLETCHING_DATA["flighted_ogre_arrows"]["requirements"], {"Ogre arrow shaft": 6, "Feather": 24})
        self.assertEqual(FLETCHING_DATA["flighted_ogre_arrows"]["output_qty"], 6)
        self.assertAlmostEqual(FLETCHING_DATA["flighted_ogre_arrows"]["exp"], 5.4)
        self.assertNotIn("string_comp_ogre_bow", FLETCHING_DATA)

    def test_arrows_bolts_darts_and_pre_eoc_bolt_tips_are_present(self):
        broad = FLETCHING_DATA["broad_arrows"]
        self.assertEqual(broad["level"], 52)
        self.assertEqual(broad["requirements"], {"Headless arrows": 15, "Broad arrow heads": 15})
        self.assertEqual(broad["unlock_abilities"], (BROAD_FLETCHING_ABILITY,))
        self.assertEqual(broad["xp_rewards"], ({"skill_id": "fletching", "amount": 150.0},))

        broad_bolts = FLETCHING_DATA["feather_broad_bolts"]
        self.assertEqual(broad_bolts["level"], 55)
        self.assertEqual(broad_bolts["requirements"], {"Unfinished broad bolts": 10, "Feather": 10})
        self.assertEqual(broad_bolts["output_item"], "Broad-tipped bolts")
        self.assertEqual(broad_bolts["unlock_abilities"], (BROAD_FLETCHING_ABILITY,))

        self.assertEqual(FLETCHING_DATA["cut_onyx_bolt_tips"]["requirements"], {"Onyx": 1})
        self.assertEqual(FLETCHING_DATA["cut_onyx_bolt_tips"]["output_qty"], 24)
        self.assertAlmostEqual(FLETCHING_DATA["cut_onyx_bolt_tips"]["exp"], 9.0)
        self.assertEqual(FLETCHING_DATA["tip_dragon_bolts"]["requirements"], {"Runite bolts": 10, "Dragon bolt tips": 10})
        self.assertEqual(FLETCHING_DATA["attach_mithril_grapple"]["requirements"], {"Mithril bolts": 1, "Mith grapple tip": 1})
        self.assertEqual(FLETCHING_DATA["fletch_dragon_darts"]["level"], 95)
        self.assertEqual(FLETCHING_DATA["fletch_dragon_darts"]["requirements"], {"Dragon dart tip": 10, "Feather": 10})

    def test_crossbow_assembly_rows_match_2011scape_combinations(self):
        expected = {
            "combine_bronze_cbow_u": (9, {"Bronze limbs": 1, "Wooden stock": 1}, "Bronze c'bow (u)", 9454),
            "combine_bronze_crossbow": (9, {"Bronze c'bow (u)": 1, "Crossbow string": 1}, "Bronze crossbow", 9174),
            "combine_blurite_cbow_u": (24, {"Blurite limbs": 1, "Oak stock": 1}, "Blurite c'bow (u)", 9456),
            "combine_blurite_crossbow": (24, {"Blurite c'bow (u)": 1, "Crossbow string": 1}, "Blurite crossbow", 9176),
            "combine_iron_cbow_u": (39, {"Iron limbs": 1, "Willow stock": 1}, "Iron c'bow (u)", 9457),
            "combine_iron_crossbow": (39, {"Iron c'bow (u)": 1, "Crossbow string": 1}, "Iron crossbow", 9177),
            "combine_steel_cbow_u": (46, {"Steel limbs": 1, "Teak stock": 1}, "Steel c'bow (u)", 9459),
            "combine_steel_crossbow": (46, {"Steel c'bow (u)": 1, "Crossbow string": 1}, "Steel crossbow", 9179),
            "combine_mithril_cbow_u": (54, {"Mithril limbs": 1, "Maple stock": 1}, "Mithril c'bow (u)", 9461),
            "combine_mithril_crossbow": (54, {"Mithril c'bow (u)": 1, "Crossbow string": 1}, "Mith crossbow", 9181),
            "combine_adamant_cbow_u": (61, {"Adamantite limbs": 1, "Mahogany stock": 1}, "Adamant c'bow (u)", 9463),
            "combine_adamant_crossbow": (61, {"Adamant c'bow (u)": 1, "Crossbow string": 1}, "Adamant crossbow", 9183),
            "combine_rune_cbow_u": (69, {"Runite limbs": 1, "Yew stock": 1}, "Runite c'bow (u)", 9465),
            "combine_rune_crossbow": (69, {"Runite c'bow (u)": 1, "Crossbow string": 1}, "Rune crossbow", 9185),
        }
        for target_id, (level, requirements, output_item, source_item_id) in expected.items():
            row = FLETCHING_DATA[target_id]
            self.assertEqual(row["group"], "combination")
            self.assertEqual(row["action"], "combine")
            self.assertEqual(row["level"], level)
            self.assertEqual(row["exp"], 0.0)
            self.assertEqual(row["requirements"], requirements)
            self.assertEqual(row["output_item"], output_item)
            self.assertEqual(row["source_item_id"], source_item_id)
            self.assertTrue(row["source"].endswith("items/combine/CombinationData.kt"))
        self.assertNotIn("fletch_bronze_javelins", FLETCHING_DATA)

    def test_every_fletching_manifest_item_has_a_resolvable_icon(self):
        missing = [
            item_name
            for item_name in fletching_item_names()
            if item_name not in FLETCHED_ITEM_IMAGES or not os.path.exists(FLETCHED_ITEM_IMAGES[item_name])
        ]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
