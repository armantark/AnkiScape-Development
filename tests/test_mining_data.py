import unittest

from mining_data import (
    DEFERRED_MINING_CONTENT,
    DEFERRED_MINING_PICKAXES,
    GLORY_GEM_DROP_CHANCE,
    INCIDENTAL_GEM_DROP_CHANCE,
    MINING_BONUS_ITEMS_BY_ID,
    MINING_PICKAXES_BY_ID,
    MINING_TARGETS_BY_ID,
    mining_extra_items_as_dict,
)


class TestMiningData(unittest.TestCase):
    def test_2011scape_target_table_contains_backend_parity_slice(self):
        self.assertEqual(
            set(MINING_TARGETS_BY_ID),
            {
                "rune_essence",
                "clay",
                "copper",
                "tin",
                "blurite",
                "limestone",
                "iron",
                "silver",
                "coal",
                "sandstone",
                "gold",
                "gem_rocks",
                "granite",
                "mithril",
                "adamantite",
                "runite",
            },
        )
        self.assertEqual(MINING_TARGETS_BY_ID["rune_essence"].alternate_output_item, "Pure essence")
        self.assertEqual(MINING_TARGETS_BY_ID["rune_essence"].alternate_output_level, 30)
        self.assertEqual(MINING_TARGETS_BY_ID["limestone"].base_exp, 26.5)
        self.assertEqual(MINING_TARGETS_BY_ID["runite"].respawn_time, 1200)

    def test_weighted_targets_keep_output_xp_and_tradeability(self):
        sandstone = MINING_TARGETS_BY_ID["sandstone"]
        granite = MINING_TARGETS_BY_ID["granite"]
        gem_rocks = MINING_TARGETS_BY_ID["gem_rocks"]

        self.assertEqual([output.base_exp for output in sandstone.weighted_outputs], [30.0, 40.0, 50.0, 60.0])
        self.assertEqual([output.item for output in granite.weighted_outputs], ["Granite (500g)", "Granite (2kg)", "Granite (5kg)"])
        self.assertEqual(sum(output.weight for output in gem_rocks.weighted_outputs), 128)
        self.assertTrue(all(output.tradeable for output in sandstone.weighted_outputs))

    def test_pickaxe_table_normalizes_source_anomalies(self):
        self.assertEqual(MINING_PICKAXES_BY_ID["bronze_pickaxe"].ticks_between_rolls, 8)
        self.assertEqual(MINING_PICKAXES_BY_ID["rune_pickaxe"].level, 41)
        self.assertEqual(MINING_PICKAXES_BY_ID["dragon_pickaxe"].item_id, 15261)
        self.assertEqual(MINING_PICKAXES_BY_ID["gilded_rune_pickaxe"].level, 41)
        self.assertEqual(MINING_PICKAXES_BY_ID["gilded_rune_pickaxe"].source_level, 1)
        self.assertEqual(DEFERRED_MINING_PICKAXES[0].id, "inferno_adze")
        self.assertFalse(DEFERRED_MINING_PICKAXES[0].tradeable)

    def test_bonus_items_and_tradability_are_explicit(self):
        items = mining_extra_items_as_dict()
        self.assertFalse(items["Blurite ore"]["tradeable"])
        self.assertTrue(items["Dragon pickaxe"]["tradeable"])
        self.assertTrue(items["Gilded rune pickaxe"]["tradeable"])
        self.assertFalse(items["Inferno adze"]["tradeable"])
        self.assertFalse(items["Varrock armour 1"]["tradeable"])
        self.assertFalse(items["Varrock armour 4"]["tradeable"])
        self.assertEqual(MINING_BONUS_ITEMS_BY_ID["varrock_armour_4"].tier, 4)
        self.assertEqual(MINING_BONUS_ITEMS_BY_ID["amulet_of_glory_4"].slot, "amulet")

    def test_gem_drop_chances_and_deferred_content_are_recorded(self):
        self.assertAlmostEqual(INCIDENTAL_GEM_DROP_CHANCE, 1 / 256)
        self.assertAlmostEqual(GLORY_GEM_DROP_CHANCE, 1 / 86)
        deferred = {entry.id: entry.status for entry in DEFERRED_MINING_CONTENT}
        self.assertEqual(deferred["concentrated_coal"], "deferred_dependency")
        self.assertEqual(deferred["shooting_stars"], "future_content")


if __name__ == "__main__":
    unittest.main()
