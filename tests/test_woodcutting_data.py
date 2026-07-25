import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.woodcutting_data import (
    BIRD_NEST_DROP_CHANCE,
    BIRD_NEST_DROP_TABLE,
    BIRD_NEST_OPEN_TABLES_BY_INPUT,
    DEFERRED_WOODCUTTING_AXES,
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
            "split_arctic_pine_logs",
            "yew",
            "ivy",
            "magic",
        })
        self.assertNotIn("redwood", WOODCUTTING_TARGETS_BY_ID)
        self.assertEqual(WOODCUTTING_TARGETS_BY_ID["tree"].output_item, "Logs")
        self.assertEqual(WOODCUTTING_TARGETS_BY_ID["hollow"].output_item, "Bark")
        self.assertEqual(
            WOODCUTTING_TARGETS_BY_ID["split_arctic_pine_logs"].requirements,
            (("Arctic pine logs", 1),),
        )
        self.assertIsNone(WOODCUTTING_TARGETS_BY_ID["ivy"].output_item)
        self.assertEqual(WOODCUTTING_TARGETS_BY_ID["magic"].base_exp, 250.0)

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
