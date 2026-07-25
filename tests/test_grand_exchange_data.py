import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG, build_ge_item_catalog_pure
from ankiscape.generated.grand_exchange_period_generated import (
    PERIOD_GE_BUY_LIMIT_SOURCE,
    PERIOD_GE_BUY_LIMITS,
    PERIOD_GE_GUIDE_PRICES,
    PERIOD_GE_PRICE_PROVENANCE,
)
from ankiscape.core.item_registry import ItemDefinition
from tools.generate_ge_period_data import (
    _normalized_name,
    _parse_fields,
    _period_name_candidates,
)


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
    def test_harvester_normalizes_period_fraction_and_registry_aliases(self):
        self.assertEqual(_normalized_name("½ anchovy pizza"), "1/2 anchovy pizza")
        self.assertIn("Adamant arrow", _period_name_candidates("Adamant arrows"))
        self.assertIn("Adamant helm", _period_name_candidates("Adamant med helm"))

    def test_harvester_reads_literal_exchange_template_fields(self):
        fields = _parse_fields(
            "{{ExchangeItem\n"
            "|Item=Yew logs\n"
            "|ItemId=1515\n"
            "|Price=494\n"
            "|Limit=25000\n"
            "}}"
        )

        self.assertEqual(
            fields,
            {
                "item": "Yew logs",
                "itemid": "1515",
                "price": "494",
                "limit": "25000",
            },
        )

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
        self.assertEqual(catalog["Logs"]["low_alchemy_value"], 1)
        self.assertEqual(catalog["Logs"]["high_alchemy_value"], 2)
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

    def test_live_catalog_uses_period_prices_and_limits_when_the_identity_is_exact(self):
        self.assertIn("Logs", GE_ITEM_CATALOG)
        self.assertNotIn("Coins", GE_ITEM_CATALOG)
        self.assertEqual(GE_ITEM_CATALOG["Logs"]["guide_price"], 106)
        self.assertEqual(GE_ITEM_CATALOG["Logs"]["buy_limit"], 25_000)
        self.assertEqual(GE_ITEM_CATALOG["Logs"]["required_level"], 1)
        self.assertEqual(GE_ITEM_CATALOG["Logs"]["source_role"], "raw_material")
        self.assertEqual(GE_ITEM_CATALOG["Yew logs"]["required_level"], 60)
        self.assertEqual(
            GE_ITEM_CATALOG["Logs"]["guide_price_source"],
            "period_grand_exchange_database",
        )
        self.assertEqual(
            GE_ITEM_CATALOG["Logs"]["guide_price_provenance"]["oldid"],
            6_519_754,
        )
        self.assertEqual(
            GE_ITEM_CATALOG["Logs"]["buy_limit_source"]["oldid"],
            6_457_777,
        )

    def test_generated_period_rows_are_registered_and_cutoff_safe(self):
        self.assertLessEqual(set(PERIOD_GE_GUIDE_PRICES), set(GE_ITEM_CATALOG))
        self.assertLessEqual(set(PERIOD_GE_BUY_LIMITS), set(GE_ITEM_CATALOG))
        self.assertEqual(len(PERIOD_GE_GUIDE_PRICES), 1_354)
        self.assertEqual(len(PERIOD_GE_BUY_LIMITS), 1_672)
        self.assertEqual(PERIOD_GE_BUY_LIMIT_SOURCE["oldid"], 6_457_777)
        self.assertTrue(PERIOD_GE_PRICE_PROVENANCE)
        self.assertTrue(
            all(
                str(row["timestamp"]) < "2012-11-20T00:00:00Z"
                for row in PERIOD_GE_PRICE_PROVENANCE.values()
            )
        )
        # The later item revision wins when it conflicts with the October
        # aggregate table.
        self.assertEqual(PERIOD_GE_BUY_LIMITS["Basket"], 1_000)
        self.assertEqual(
            PERIOD_GE_PRICE_PROVENANCE["Basket"]["oldid"],
            6_540_082,
        )
        self.assertEqual(PERIOD_GE_GUIDE_PRICES["Split log"], 30)
        self.assertEqual(PERIOD_GE_BUY_LIMITS["Split log"], 1_000)
        self.assertEqual(
            PERIOD_GE_PRICE_PROVENANCE["Split log"]["oldid"],
            6_563_176,
        )
        self.assertEqual(PERIOD_GE_GUIDE_PRICES["Compost potion (4)"], 12_282)
        self.assertEqual(PERIOD_GE_BUY_LIMITS["Compost potion (4)"], 1_000)
        self.assertEqual(
            PERIOD_GE_PRICE_PROVENANCE["Compost potion (4)"]["oldid"],
            6_561_561,
        )

    def test_only_audited_unresolved_identities_remain_buy_limit_blocked(self):
        blocked = {
            name
            for name, row in GE_ITEM_CATALOG.items()
            if row["buy_limit"] is None
        }
        self.assertEqual(
            blocked,
            {
                "Arctic pyre logs",
                "Black warlock",
                "Cape",
                "Elemental talisman",
                "Eucalyptus pyre logs",
                "Feather headdress",
                "Fine cloth",
                "Flowers",
                "Fremennik cloak",
                "Fremennik shirt",
                "Loar remains",
                "Magic pyre logs",
                "Mahogany pyre logs",
                "Maple pyre logs",
                "Oak pyre logs",
                "Olive oil (1)",
                "Olive oil (2)",
                "Olive oil (4)",
                "Pirate bandana",
                "Pirate leggings",
                "Priest gown",
                "Pyre logs",
                "Robe top",
                "Ruby harvest",
                "Sacred oil (1)",
                "Sacred oil (2)",
                "Sacred oil (3)",
                "Sacred oil (4)",
                "Snowy knight",
                "Stripy pirate shirt",
                "Teak pyre logs",
                "Tribal top",
                "Villager armband",
                "Villager hat",
                "Villager robe",
                "Villager sandals",
                "Willow pyre logs",
                "Woven top",
                "Yew pyre logs",
            },
        )


if __name__ == "__main__":
    unittest.main()
