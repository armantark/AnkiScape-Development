import json
import runpy
import tempfile
import unittest
from pathlib import Path

from item_values import EXCHANGEABLE_ITEM_NAMES, ITEM_VALUES, item_store_value
from inventory_pure import loot_should_pick_up
from tools.gen_item_values import build


class TestItemValues(unittest.TestCase):
    def test_values_are_positive_ints_and_nonempty(self):
        self.assertGreater(len(ITEM_VALUES), 100)
        self.assertTrue(all(isinstance(v, int) and v > 0 for v in ITEM_VALUES.values()))

    def test_known_and_unknown_lookups(self):
        # Spirit shards are a known cheap shop item; a made-up name is unknown.
        self.assertEqual(item_store_value("Spirit shards"), 25)
        self.assertIsNone(item_store_value("Definitely Not A Real Item"))

    def test_feeds_the_loot_filter(self):
        # A cheap item (25 value -> high-alch 15) falls below a 50 threshold, so
        # the filter would leave it; stackables are always taken.
        value = item_store_value("Spirit shards")
        self.assertFalse(loot_should_pick_up("Spirit shards", value, 50, set()))
        self.assertTrue(loot_should_pick_up("Spirit shards", value, 50, {"Spirit shards"}))

    def test_generated_table_exposes_cache_exchangeability(self):
        self.assertIn("Logs", EXCHANGEABLE_ITEM_NAMES)
        self.assertNotIn("Coins", EXCHANGEABLE_ITEM_NAMES)

    def test_generator_preserves_exchangeable_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "raw.json"
            output = root / "generated.py"
            raw.write_text(
                json.dumps(
                    {
                        "items": {
                            "1": {
                                "name": "Logs",
                                "value": 4,
                                "stackable": False,
                                "exchangeable": True,
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            counts = build(raw, output)
            generated = runpy.run_path(str(output))

            self.assertEqual(counts, (1, 0, 1))
            self.assertEqual(
                generated["EXCHANGEABLE_ITEM_NAMES_GENERATED"],
                frozenset({"Logs"}),
            )


if __name__ == "__main__":
    unittest.main()
