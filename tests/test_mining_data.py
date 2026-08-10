import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.mining_data import (
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
                "living_rock_remains",
                "concentrated_coal",
                "concentrated_gold",
                "red_sandstone",
                "runite",
            },
        )
        self.assertEqual(MINING_TARGETS_BY_ID["rune_essence"].alternate_output_item, "Pure essence")
        self.assertEqual(MINING_TARGETS_BY_ID["rune_essence"].alternate_output_level, 30)
        self.assertEqual(MINING_TARGETS_BY_ID["limestone"].base_exp, 26.5)
        self.assertEqual(MINING_TARGETS_BY_ID["concentrated_coal"].level, 77)
        remains = MINING_TARGETS_BY_ID["living_rock_remains"]
        self.assertEqual(remains.level, 73)
        self.assertEqual(remains.base_exp, 25.0)
        self.assertEqual(remains.output_item, "Living minerals")
        self.assertEqual(remains.output_quantity_range, (5, 24))
        self.assertFalse(remains.allows_random_gems)
        self.assertEqual(MINING_TARGETS_BY_ID["concentrated_coal"].respawn_time, 300)
        self.assertFalse(MINING_TARGETS_BY_ID["concentrated_coal"].allows_random_gems)
        self.assertIn("stays available", MINING_TARGETS_BY_ID["concentrated_coal"].notes)
        self.assertEqual(MINING_TARGETS_BY_ID["concentrated_gold"].level, 80)
        self.assertEqual(MINING_TARGETS_BY_ID["concentrated_gold"].base_exp, 65.0)
        self.assertFalse(MINING_TARGETS_BY_ID["concentrated_gold"].allows_random_gems)
        self.assertIn("does not model rock depletion", MINING_TARGETS_BY_ID["concentrated_gold"].notes)
        self.assertEqual(MINING_TARGETS_BY_ID["runite"].respawn_time, 1200)

    def test_weighted_targets_keep_output_xp_and_tradeability(self):
        sandstone = MINING_TARGETS_BY_ID["sandstone"]
        granite = MINING_TARGETS_BY_ID["granite"]
        gem_rocks = MINING_TARGETS_BY_ID["gem_rocks"]

        self.assertEqual([output.base_exp for output in sandstone.weighted_outputs], [30.0, 40.0, 50.0, 60.0])
        self.assertEqual([output.item for output in granite.weighted_outputs], ["Granite (500g)", "Granite (2kg)", "Granite (5kg)"])
        self.assertEqual(sum(output.weight for output in gem_rocks.weighted_outputs), 128)
        self.assertTrue(all(output.tradeable for output in sandstone.weighted_outputs))

    def test_pickaxe_table_matches_source_levels_and_includes_inferno_adze(self):
        self.assertEqual(MINING_PICKAXES_BY_ID["bronze_pickaxe"].ticks_between_rolls, 8)
        self.assertEqual(MINING_PICKAXES_BY_ID["rune_pickaxe"].level, 41)
        self.assertEqual(MINING_PICKAXES_BY_ID["inferno_adze"].item_id, 13661)
        self.assertEqual(MINING_PICKAXES_BY_ID["inferno_adze"].level, 41)
        self.assertEqual(MINING_PICKAXES_BY_ID["inferno_adze"].ticks_between_rolls, 3)
        self.assertFalse(MINING_PICKAXES_BY_ID["inferno_adze"].tradeable)
        self.assertEqual(MINING_PICKAXES_BY_ID["dragon_pickaxe"].item_id, 15261)
        self.assertEqual(MINING_PICKAXES_BY_ID["gilded_steel_pickaxe"].level, 1)
        self.assertEqual(MINING_PICKAXES_BY_ID["gilded_adamant_pickaxe"].level, 1)
        self.assertEqual(MINING_PICKAXES_BY_ID["gilded_rune_pickaxe"].level, 1)
        self.assertEqual(DEFERRED_MINING_PICKAXES, ())

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

    def test_glory_runtime_bindings_include_trimmed_and_duplicate_name_aliases(self):
        expected_item_ids = {
            "amulet_of_glory": 8283,
            "amulet_of_glory_1": 1706,
            "amulet_of_glory_2": 1708,
            "amulet_of_glory_3": 1710,
            "amulet_of_glory_4": 1712,
            "amulet_of_glory_t": 10362,
            "amulet_of_glory_t1": 10360,
            "amulet_of_glory_t2": 10358,
            "amulet_of_glory_t3": 10356,
            "amulet_of_glory_t4": 10354,
            "amulet_of_glory_t_10719": 10719,
        }
        self.assertEqual(
            {bonus_id: MINING_BONUS_ITEMS_BY_ID[bonus_id].item_id for bonus_id in expected_item_ids},
            expected_item_ids,
        )
        self.assertEqual(MINING_BONUS_ITEMS_BY_ID["amulet_of_glory_t"].display_name, "Amulet of glory (t)")
        self.assertEqual(MINING_BONUS_ITEMS_BY_ID["amulet_of_glory_t_10719"].display_name, "Amulet of glory (t)")
        self.assertIn("duplicate-name", MINING_BONUS_ITEMS_BY_ID["amulet_of_glory_t_10719"].notes.lower())
        for bonus_id in (
            "amulet_of_glory_t",
            "amulet_of_glory_t1",
            "amulet_of_glory_t2",
            "amulet_of_glory_t3",
            "amulet_of_glory_t4",
            "amulet_of_glory_t_10719",
        ):
            self.assertTrue(MINING_BONUS_ITEMS_BY_ID[bonus_id].tradeable)

        items = mining_extra_items_as_dict()
        self.assertEqual(items["Amulet of glory"]["item_id"], 8283)
        self.assertEqual(items["Amulet of glory (t)"]["item_id"], 10362)
        for suffix, item_id in (("t1", 10360), ("t2", 10358), ("t3", 10356), ("t4", 10354)):
            self.assertEqual(items[f"Amulet of glory ({suffix})"]["item_id"], item_id)
        for suffix in ("t", "t1", "t2", "t3", "t4"):
            self.assertTrue(items[f"Amulet of glory ({suffix})"]["tradeable"])

    def test_gem_drop_chances_and_deferred_content_are_recorded(self):
        self.assertAlmostEqual(INCIDENTAL_GEM_DROP_CHANCE, 1 / 256)
        self.assertAlmostEqual(GLORY_GEM_DROP_CHANCE, 1 / 86)
        deferred = {entry.id: entry.status for entry in DEFERRED_MINING_CONTENT}
        self.assertNotIn("concentrated_coal", deferred)
        self.assertNotIn("concentrated_gold", deferred)
        self.assertEqual(deferred["shooting_stars"], "implemented_activity")
        # Ring of wealth's gem-rock double-gem/speed bonus is earmarked for the
        # future Enchanting/Magic system that produces the ring.
        self.assertEqual(deferred["ring_of_wealth_gem_bonus"], "deferred_dependency")
        rs_entry = next(e for e in DEFERRED_MINING_CONTENT if e.id == "ring_of_wealth_gem_bonus")
        self.assertIn("Enchant", rs_entry.reason)


if __name__ == "__main__":
    unittest.main()
