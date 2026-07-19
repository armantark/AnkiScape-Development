import unittest

from grand_exchange_data import GE_ITEM_CATALOG, build_ge_item_catalog_pure
from item_registry import ItemDefinition


def _item(name, *, tradeable=True):
    return ItemDefinition(
        id=f"material_{name.lower().replace(' ', '_')}",
        display_name=name,
        storage_key=name,
        category="material",
        asset_path=None,
        source="test",
        license_note="test",
        tradeable=tradeable,
    )


class GrandExchangeDataTest(unittest.TestCase):
    def test_catalog_intersects_registered_tradeable_and_cache_exchangeable_items(self):
        catalog = build_ge_item_catalog_pure(
            (
                _item("Logs"),
                _item("Quest token"),
                _item("Untradeable", tradeable=False),
                _item("Coins"),
            ),
            item_values={
                "Logs": 4,
                "Quest token": 50,
                "Untradeable": 10,
                "Coins": 1,
            },
            exchangeable_names={"Logs", "Untradeable", "Coins"},
        )

        self.assertEqual(tuple(catalog), ("Logs",))
        self.assertEqual(catalog["Logs"]["guide_price"], 4)
        self.assertEqual(
            catalog["Logs"]["guide_price_source"],
            "cache_value_fallback",
        )
        self.assertIsNone(catalog["Logs"]["buy_limit"])

    def test_period_rows_override_cache_values_without_widening_eligibility(self):
        catalog = build_ge_item_catalog_pure(
            (_item("Logs"), _item("Oak logs")),
            item_values={"Logs": 4, "Oak logs": 20},
            exchangeable_names={"Logs"},
            period_guide_prices={"Logs": 61, "Oak logs": 99},
            period_buy_limits={"Logs": 25_000, "Oak logs": 25_000},
        )

        self.assertEqual(tuple(catalog), ("Logs",))
        self.assertEqual(catalog["Logs"]["guide_price"], 61)
        self.assertEqual(catalog["Logs"]["buy_limit"], 25_000)
        self.assertEqual(
            catalog["Logs"]["guide_price_source"],
            "period_grand_exchange_database",
        )

    def test_live_catalog_is_registered_and_has_no_unsourced_buy_limit_claims(self):
        self.assertIn("Logs", GE_ITEM_CATALOG)
        self.assertNotIn("Coins", GE_ITEM_CATALOG)
        self.assertGreater(GE_ITEM_CATALOG["Logs"]["guide_price"], 0)
        self.assertEqual(
            {
                row["buy_limit_source"]
                for row in GE_ITEM_CATALOG.values()
            },
            {None},
        )


if __name__ == "__main__":
    unittest.main()
