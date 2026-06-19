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

    def test_every_fletching_manifest_item_has_a_resolvable_icon(self):
        missing = [
            item_name
            for item_name in fletching_item_names()
            if item_name not in FLETCHED_ITEM_IMAGES or not os.path.exists(FLETCHED_ITEM_IMAGES[item_name])
        ]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
