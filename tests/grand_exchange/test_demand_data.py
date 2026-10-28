import hashlib
import json
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS
from ankiscape.data import grand_exchange_data as catalog
from ankiscape.data.grand_exchange import sell_demand as demand


class DemandDataTests(unittest.TestCase):
    def test_reference_extract_hash_and_classification(self):
        raw = Path(demand.__file__).with_name("rs3_volume_highs.json").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "6510fa6b7a05e432692e03efe8a01b8287dac95a1c9bdec14686e7337fcea74e")
        self.assertEqual(raw.decode(), json.dumps(json.loads(raw), sort_keys=True,
                                                 separators=(",", ":")) + "\n")
        self.assertEqual(demand.REFERENCE_EXTRACT_SHA256, hashlib.sha256(raw).hexdigest())
        self.assertEqual(demand.REFERENCE_URL,
                         "https://secure.runescape.com/m=itemdb_rs/top100?list=0&scale=3")
        self.assertEqual(demand.REFERENCE_TITLE, "Most Traded Items")
        self.assertEqual(demand.REFERENCE_RETRIEVED, "2026-10-24")
        self.assertEqual(demand.REFERENCE_SELECTION, "Last 6 Months, Max column")
        self.assertIn("modern statistics", demand.REFERENCE_CLASSIFICATION)
        self.assertIn("Author-selected AnkiScape balance", demand.BALANCE_CLASSIFICATION)
        self.assertIn("not observed volumes", demand.BALANCE_CLASSIFICATION)
        self.assertEqual(demand.PLAYER_VOLUME_DIVISOR, 1000)
        self.assertEqual(demand.PUBLISHER_REVISION_ID, "not provided")
        self.assertEqual(demand.INDIVIDUAL_MAXIMUM_DATES, "not provided")
        self.assertEqual(len(demand.OWNER_ANSWERS), 3)
        self.assertIn("Do it yourself", demand.OWNER_ANSWERS[2])

    def test_sampled_capacities(self):
        expected = {
            "Air rune": 22800, "Astral rune": 16700, "Blood rune": 10900,
            "Body rune": 22100, "Cannonball": 11100, "Chaos rune": 10500,
            "Coal": 6900, "Death rune": 8100, "Dragon bones": 4500,
            "Earth rune": 15500, "Feather": 145700, "Fire rune": 27200,
            "Gold bar": 1700, "Gold ore": 1600, "Law rune": 36300,
            "Magic logs": 9300, "Maple logs": 11500, "Mind rune": 14300,
            "Nature rune": 16300, "Pure essence": 59900, "Raw rocktail": 2700,
            "Raw shark": 2100, "Soul rune": 10000, "Steel bar": 2300,
            "Uncut diamond": 2500, "Uncut dragonstone": 6100,
            "Vial of water": 6100, "Water rune": 33300,
            "Water talisman": 6500, "Yew logs": 2200,
        }
        self.assertEqual(set(expected), set(demand.RS3_VOLUME_HIGHS))
        for name, quantity in expected.items():
            with self.subTest(item=name):
                self.assertEqual(demand.daily_sell_demand_capacity_pure(name, 1), quantity)

    def test_yew_capacity_is_2200(self):
        self.assertEqual(demand.daily_sell_demand_capacity_pure("Yew logs", 25000), 2200)
        self.assertEqual(catalog.GE_ITEM_CATALOG["Yew logs"]["sell_demand_daily_quantity"], 2200)

    def test_unmapped_capacity_uses_scaled_existing_limit(self):
        self.assertEqual(demand.daily_sell_demand_capacity_pure("Unsampled", 25000), 2200)
        self.assertEqual(demand.daily_sell_demand_capacity_pure("Unsampled", 100), 8)

    def test_missing_limit_still_allows_one_sale_per_day(self):
        for limit in (None, 0, -1, 1, False):
            with self.subTest(limit=limit):
                self.assertEqual(demand.daily_sell_demand_capacity_pure("Unsampled", limit), 1)

    def test_catalog_membership_prices_and_buy_limits_are_unchanged(self):
        eligible = {
            item.storage_key: item for item in ITEM_DEFINITIONS
            if item.storage_key != "Coins" and item.tradeable
            and item.storage_key in catalog.EXCHANGEABLE_ITEM_NAMES
            and (catalog.PERIOD_GE_GUIDE_PRICES.get(item.storage_key, 0) > 0
                 or catalog.ITEM_VALUES.get(item.storage_key, 0) > 0)
        }
        self.assertEqual(set(catalog.GE_ITEM_CATALOG), set(eligible))
        for name, item in eligible.items():
            with self.subTest(item=name):
                self._assert_retained_catalog_entry(name, item)

    def _assert_retained_catalog_entry(self, name, item):
        spec = catalog.GE_ITEM_CATALOG[name]
        period = catalog.PERIOD_GE_GUIDE_PRICES.get(name, 0)
        cache = catalog.ITEM_VALUES.get(name, 0)
        limit = catalog.PERIOD_GE_BUY_LIMITS.get(name, 0)
        self.assertEqual(spec["guide_price"], period if period > 0 else cache)
        self.assertEqual(spec["buy_limit"], limit if limit > 0 else None)
        self.assertEqual(spec["guide_price_provenance"],
                         catalog.PERIOD_GE_PRICE_PROVENANCE.get(name, {}))
        self.assertEqual(spec["buy_limit_source"],
                         dict(catalog.PERIOD_GE_BUY_LIMIT_SOURCE) if limit > 0 else None)
        self.assertEqual(spec["cache_value"], cache if cache > 0 else None)
        self.assertEqual(spec["low_alchemy_value"], int(cache * .4) if cache > 0 else None)
        self.assertEqual(spec["high_alchemy_value"], int(cache * .6) if cache > 0 else None)
        self.assertEqual(spec["item_id"], item.id)
        self.assertEqual(spec["source_item_id"], item.source_item_id)
