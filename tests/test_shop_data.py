import json
import unittest
from pathlib import Path

from shop_data import (
    SHOP_COVERAGE_SUMMARY,
    SHOP_DATA,
    SHOP_DATA_VERSION,
    SHOP_SERVICES,
    SHOP_VENDOR_ACTIONS,
    shop_extra_items_as_dict,
)


class TestShopData(unittest.TestCase):
    def test_generated_catalog_covers_all_source_shop_files_with_dispositions(self):
        self.assertEqual(SHOP_DATA_VERSION, 1)
        self.assertEqual(SHOP_COVERAGE_SUMMARY["source_shop_count"], 274)
        self.assertEqual(SHOP_COVERAGE_SUMMARY["runtime_shop_count"], 273)
        self.assertEqual(SHOP_COVERAGE_SUMMARY["excluded_shop_count"], 1)
        self.assertGreater(SHOP_COVERAGE_SUMMARY["stock_row_count"], 2700)
        self.assertGreater(SHOP_COVERAGE_SUMMARY["locked_stock_row_count"], SHOP_COVERAGE_SUMMARY["live_stock_row_count"])
        self.assertNotIn("a_test_shop", SHOP_DATA)

    def test_every_stock_row_has_runtime_disposition_and_source(self):
        for shop in SHOP_DATA.values():
            for row in shop["stock"]:
                self.assertIn(row["disposition"], {"live", "locked", "hidden", "blocked"})
                self.assertIn(row["visibility"], {"visible", "visible_locked", "hidden"})
                self.assertIsInstance(row["source_path"], str)
                self.assertTrue(row["source_path"].endswith(".json"))
                if row["disposition"] == "live":
                    self.assertIsInstance(row["buy_price"], int)
                    self.assertEqual(shop["currency_id"], 995)
                    self.assertTrue(shop["currency_implemented"])

    def test_feather_rows_are_present_but_fail_closed_without_cache_price(self):
        feather_rows = [
            (shop, row)
            for shop in SHOP_DATA.values()
            for row in shop["stock"]
            if row["item_name"] == "Feather"
        ]
        self.assertGreaterEqual(len(feather_rows), 2)
        for _shop, row in feather_rows:
            self.assertIn(row["disposition"], {"locked", "blocked"})
            if row["disposition"] == "locked":
                self.assertEqual(row["lock_reason"], "price_policy_unresolved")

    def test_non_coin_shops_are_visible_locked(self):
        non_coin_shops = [shop for shop in SHOP_DATA.values() if shop["currency_id"] != 995]
        self.assertGreaterEqual(len(non_coin_shops), 1)
        for shop in non_coin_shops:
            self.assertFalse(shop["currency_implemented"])
            if shop["visibility"] == "hidden":
                self.assertEqual(shop["lock_reason"], "activity_or_reward_system_not_implemented")
                continue
            self.assertEqual(shop["visibility"], "visible_locked")
            self.assertEqual(shop["lock_reason"], "currency_not_implemented")

    def test_services_vendor_actions_and_extra_items_are_exported(self):
        self.assertIn("al_kharid_tanner_soft_leather", SHOP_SERVICES)
        self.assertIn("sawmill_oak_plank", SHOP_SERVICES)
        self.assertIn("bartender_buy_beer", SHOP_VENDOR_ACTIONS)
        self.assertIn("benny_buy_varrock_herald", SHOP_VENDOR_ACTIONS)
        extra_items = shop_extra_items_as_dict()
        for item_name in ("Beer", "Silk", "Newspaper", "Cowhide", "Leather", "Oak plank"):
            self.assertIn(item_name, extra_items)

    def test_machine_readable_ledger_matches_catalog_summary(self):
        ledger_path = Path("memory-bank/source-audits/npc-shop-coverage-ledger-2026-07-06.json")
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(ledger["shop_data_version"], SHOP_DATA_VERSION)
        self.assertEqual(ledger["summary"]["source_shop_count"], SHOP_COVERAGE_SUMMARY["source_shop_count"])
        self.assertTrue(any(shop["id"] == "a_test_shop" and shop["disposition"] == "excluded" for shop in ledger["shops"]))


if __name__ == "__main__":
    unittest.main()
