import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.woodcutting_data import (
    ARCTIC_PINE_SOURCE,
    BIRD_NEST_DROP_CHANCE,
    BIRD_NEST_DROP_TABLE,
    BIRD_NEST_OPEN_TABLES_BY_INPUT,
    CURLY_ROOT_SOURCE,
    DEFERRED_WOODCUTTING_AXES,
    EUCALYPTUS_SOURCE,
    WOODCUTTING_AXES_BY_ID,
    WOODCUTTING_TARGETS_BY_ID,
)


class TestWoodcuttingData(unittest.TestCase):
    def test_2011scape_target_table_contains_expected_parity_slice(self):
        self.assertEqual(set(WOODCUTTING_TARGETS_BY_ID), {
            "tree",
            "achey",
            "oak",
            "willow",
            "teak",
            "maple",
            "hollow",
            "mahogany",
            "arctic_pine",
            "split_arctic_pine_logs",
            "eucalyptus",
            "yew",
            "ivy",
            "magic",
            "curly_jade_root",
        })
        self.assertNotIn("redwood", WOODCUTTING_TARGETS_BY_ID)
        self.assertEqual(WOODCUTTING_TARGETS_BY_ID["tree"].output_item, "Logs")
        self.assertEqual(WOODCUTTING_TARGETS_BY_ID["hollow"].output_item, "Bark")
        self.assertEqual(
            WOODCUTTING_TARGETS_BY_ID["split_arctic_pine_logs"].requirements,
            (("Arctic pine logs", 1),),
        )
        arctic = WOODCUTTING_TARGETS_BY_ID["arctic_pine"]
        self.assertEqual((arctic.level, arctic.base_exp), (54, 140.2))
        self.assertEqual(
            (arctic.output_item, arctic.source_item_id),
            ("Arctic pine logs", 10810),
        )
        self.assertEqual(
            (
                arctic.deplete_chance,
                arctic.respawn_time,
                arctic.low_chance,
                arctic.high_chance,
            ),
            (8, 14, 8, 25),
        )
        self.assertEqual(arctic.source, ARCTIC_PINE_SOURCE)
        eucalyptus = WOODCUTTING_TARGETS_BY_ID["eucalyptus"]
        self.assertEqual((eucalyptus.level, eucalyptus.base_exp), (58, 165.0))
        self.assertEqual(
            (eucalyptus.output_item, eucalyptus.source_item_id),
            ("Eucalyptus logs", 12581),
        )
        self.assertEqual(
            (
                eucalyptus.deplete_chance,
                eucalyptus.respawn_time,
                eucalyptus.low_chance,
                eucalyptus.high_chance,
            ),
            (8, 99, 4, 12),
        )
        self.assertEqual(eucalyptus.source, EUCALYPTUS_SOURCE)
        self.assertIsNone(WOODCUTTING_TARGETS_BY_ID["ivy"].output_item)
        self.assertEqual(WOODCUTTING_TARGETS_BY_ID["magic"].base_exp, 250.0)
        curly = WOODCUTTING_TARGETS_BY_ID["curly_jade_root"]
        self.assertEqual(
            (
                curly.level,
                curly.base_exp,
                curly.output_item,
                curly.source_item_id,
                curly.output_quantity,
            ),
            (83, 161.6, "Curly root", 21350, 4),
        )
        self.assertEqual((curly.low_chance, curly.high_chance), (128, 256))
        self.assertEqual((curly.deplete_chance, curly.respawn_time), (0, 0))
        self.assertFalse(curly.output_stackable)
        self.assertFalse(curly.output_tradeable)
        self.assertEqual(curly.source, CURLY_ROOT_SOURCE)

    def test_hatchet_table_includes_inferno_adze_incineration(self):
        self.assertEqual(WOODCUTTING_AXES_BY_ID["bronze_hatchet"].ratio, 1.0)
        self.assertEqual(WOODCUTTING_AXES_BY_ID["rune_hatchet"].level, 41)
        self.assertEqual(WOODCUTTING_AXES_BY_ID["dragon_hatchet"].ratio, 3.75)
        self.assertEqual(WOODCUTTING_AXES_BY_ID["inferno_adze"].level, 61)
        self.assertEqual(WOODCUTTING_AXES_BY_ID["inferno_adze"].ratio, 3.75)
        self.assertTrue(WOODCUTTING_AXES_BY_ID["inferno_adze"].incinerates_logs)
        self.assertEqual(WOODCUTTING_AXES_BY_ID["inferno_adze"].incinerate_chance, 1 / 2)
        self.assertEqual(DEFERRED_WOODCUTTING_AXES, ())

    def test_bird_nest_source_tables_are_weighted(self):
        self.assertAlmostEqual(BIRD_NEST_DROP_CHANCE, 1 / 257)
        self.assertEqual(sum(item.weight for item in BIRD_NEST_DROP_TABLE), 100)
        self.assertEqual(BIRD_NEST_OPEN_TABLES_BY_INPUT["Bird's nest (seeds)"].total_weight, 1024)
        self.assertEqual(BIRD_NEST_OPEN_TABLES_BY_INPUT["Bird's nest (ring)"].total_weight, 100)


if __name__ == "__main__":
    unittest.main()
