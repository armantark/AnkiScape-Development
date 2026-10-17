import subprocess
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

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
    _price_row,
)


ROOT = Path(__file__).resolve().parents[1]


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
    def test_harvester_supports_documented_direct_invocation(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "generate_ge_period_data.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("usage: generate_ge_period_data.py <output-py>", completed.stderr)
        self.assertNotIn("ModuleNotFoundError", completed.stderr)

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

    def test_harvester_tries_singular_exchange_page_after_plural_title(self):
        revision = {
            "title": "Exchange:Black claw",
            "revid": 6_586_107,
            "timestamp": "2012-11-19T13:11:15Z",
            "content": (
                "{{ExchangeItem\n"
                "|Item=Black claws\n"
                "|ItemId=3098\n"
                "|Price=6,772\n"
                "|Limit=100\n"
                "}}"
            ),
        }
        with patch(
            "tools.generate_ge_period_data._fetch_cutoff_revision",
            side_effect=(None, revision),
        ) as fetch_revision:
            item_name, row = _price_row(
                "Black claws",
                ("Black claws", "Black claw"),
            )

        self.assertEqual(item_name, "Black claws")
        self.assertEqual(row["price"], 6_772)
        self.assertEqual(row["page_limit"], 100)
        self.assertEqual(
            [call.args[0] for call in fetch_revision.call_args_list],
            ["Exchange:Black claws", "Exchange:Black claw"],
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
        crayfish = GE_ITEM_CATALOG["Crayfish"]
        self.assertEqual(crayfish["source_item_id"], 13433)
        self.assertEqual(crayfish["guide_price"], 45)
        self.assertEqual(crayfish["cache_value"], 5)
        self.assertEqual(crayfish["buy_limit"], 10_000)
        self.assertEqual(crayfish["guide_price_source"], "period_grand_exchange_database")
        self.assertEqual(
            crayfish["guide_price_provenance"],
            {
                "price": 45,
                "page_title": "Exchange:Crayfish",
                "oldid": 6_570_435,
                "timestamp": "2012-11-18T03:19:45Z",
                "price_date": "03:19, November 18, 2012 (UTC)",
                "page_item": "Crayfish",
                "item_id": 13433,
                "cache_value": 5,
                "page_limit": 10_000,
            },
        )
        self.assertEqual(GE_ITEM_CATALOG["Raw crayfish"]["source_item_id"], 13435)
        self.assertEqual(GE_ITEM_CATALOG["Raw crayfish"]["guide_price"], 58)
        self.assertEqual(GE_ITEM_CATALOG["Raw crayfish"]["buy_limit"], 20_000)
        self.assertNotIn("Burnt crayfish", GE_ITEM_CATALOG)

    def test_black_and_white_equipment_families_reach_the_live_catalog(self):
        for item_name, source_item_id, guide_price in (
            ("Black scimitar", 1327, 3_282),
            ("Black mace", 1426, 976),
            ("Black claws", 3098, 6_772),
            ("Black spear", 4580, 283),
            ("White scimitar", 6611, 1_846),
        ):
            with self.subTest(item_name=item_name):
                row = GE_ITEM_CATALOG[item_name]
                self.assertEqual(row["source_item_id"], source_item_id)
                self.assertEqual(row["category"], "equipment")
                self.assertEqual(row["guide_price"], guide_price)
                self.assertEqual(row["buy_limit"], 100)

    def test_offline_regeneration_preserves_all_committed_rows(self):
        from tools.generate_ge_period_data import main

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "grand_exchange_period_generated.py"
            with patch("sys.argv", ["generate_ge_period_data.py", str(output)]), patch(
                "tools.generate_ge_period_data.harvest",
                side_effect=AssertionError("normal regeneration must not harvest"),
            ):
                main()
                first = output.read_bytes()
                main()
                self.assertEqual(output.read_bytes(), first)
            self.assertEqual(
                first,
                (ROOT / "generated/grand_exchange_period_generated.py").read_bytes(),
            )

    def test_generated_period_rows_are_registered_and_cutoff_safe(self):
        self.assertLessEqual(set(PERIOD_GE_GUIDE_PRICES), set(GE_ITEM_CATALOG))
        self.assertLessEqual(set(PERIOD_GE_BUY_LIMITS), set(GE_ITEM_CATALOG))
        self.assertEqual(len(PERIOD_GE_GUIDE_PRICES), 1_444)
        self.assertEqual(len(PERIOD_GE_BUY_LIMITS), 1_839)
        self.assertNotIn("Steel spear (kp)", PERIOD_GE_GUIDE_PRICES)
        self.assertNotIn("Steel spear (kp)", PERIOD_GE_BUY_LIMITS)
        self.assertNotIn("Steel spear (kp)", GE_ITEM_CATALOG)
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

    def test_crafting_and_fletching_potion_families_have_period_market_rows(self):
        expected = {
            "Crafting potion (1)": (1_125, 5_625_628),
            "Crafting potion (2)": (1_414, 6_549_672),
            "Crafting potion (4)": (1_918, 6_519_240),
            "Crafting flask (6)": (7_208, 6_570_434),
            "Fletching potion (1)": (39, 6_540_299),
            "Fletching potion (2)": (43, 5_625_964),
            "Fletching potion (4)": (42, 6_570_590),
            "Fletching flask (6)": (3_125, 6_570_588),
        }
        for item_name, (price, oldid) in expected.items():
            with self.subTest(item_name=item_name):
                self.assertEqual(PERIOD_GE_GUIDE_PRICES[item_name], price)
                self.assertEqual(PERIOD_GE_BUY_LIMITS[item_name], 1_000)
                self.assertEqual(
                    PERIOD_GE_PRICE_PROVENANCE[item_name]["oldid"], oldid
                )
        self.assertEqual(PERIOD_GE_GUIDE_PRICES["Compost potion (4)"], 12_282)
        self.assertEqual(PERIOD_GE_BUY_LIMITS["Compost potion (4)"], 1_000)
        self.assertEqual(
            PERIOD_GE_PRICE_PROVENANCE["Compost potion (4)"]["oldid"],
            6_561_561,
        )
        self.assertEqual(PERIOD_GE_GUIDE_PRICES["Ale yeast"], 31)
        self.assertEqual(PERIOD_GE_BUY_LIMITS["Ale yeast"], 100)
        self.assertEqual(PERIOD_GE_GUIDE_PRICES["Dwarven stout (m)"], 25_372)
        self.assertEqual(PERIOD_GE_BUY_LIMITS["Dwarven stout (m)"], 100)

    def test_uncharged_and_fully_charged_glory_reach_the_live_catalog(self):
        # The 2012 GE traded the uncharged and fully charged amulets under their
        # own names; partly charged ones did not.
        # https://runescape.wiki/w/Amulet_of_glory?oldid=6469621
        for item_name, price, oldid in (
            ("Amulet of glory", 10_157, 6_570_084),
            ("Amulet of glory (4)", 10_965, 6_570_085),
        ):
            row = GE_ITEM_CATALOG[item_name]
            self.assertEqual(row["guide_price"], price)
            self.assertEqual(row["buy_limit"], 100)
            self.assertEqual(row["category"], "equipment")
            self.assertEqual(
                PERIOD_GE_PRICE_PROVENANCE[item_name]["oldid"], oldid
            )
        for item_name in (
            "Amulet of glory (1)",
            "Amulet of glory (2)",
            "Amulet of glory (3)",
            "Amulet of glory (t1)",
            "Amulet of glory (t2)",
            "Amulet of glory (t3)",
        ):
            self.assertNotIn(item_name, GE_ITEM_CATALOG)
            self.assertNotIn(item_name, PERIOD_GE_GUIDE_PRICES)

    def test_mage_training_arena_equipment_has_period_market_rows(self):
        expected = {
            "Infinity boots": (677_237, 10, 6_549_641),
            "Infinity bottoms": (4_248_199, 10, 6_519_647),
            "Infinity gloves": (1_753_011, 10, 6_562_407),
            "Infinity hat": (2_551_706, 10, 6_570_751),
            "Infinity top": (3_234_233, 10, 6_562_411),
            "Mages' book": (3_115_395, 10, 6_562_622),
        }
        for item_name, (price, limit, oldid) in expected.items():
            with self.subTest(item_name=item_name):
                self.assertEqual(PERIOD_GE_GUIDE_PRICES[item_name], price)
                self.assertEqual(PERIOD_GE_BUY_LIMITS[item_name], limit)
                self.assertEqual(
                    PERIOD_GE_PRICE_PROVENANCE[item_name]["oldid"],
                    oldid,
                )

    def test_shades_bronze_chest_poisoned_daggers_have_period_buy_limits(self):
        self.assertEqual(PERIOD_GE_BUY_LIMITS["Black dagger (p)"], 100)
        self.assertEqual(PERIOD_GE_BUY_LIMITS["Mithril dagger (p)"], 100)

    def test_oyster_has_its_period_buy_limit_without_an_invented_price(self):
        # Calculator:Grand Exchange buying limits oldid 6457777 lists the
        # unopened shell separately from Oyster pearl and Oyster pearls.
        row = GE_ITEM_CATALOG["Oyster"]
        self.assertEqual(row["source_item_id"], 407)
        self.assertTrue(row["tradeable"])
        self.assertEqual(row["buy_limit"], 500)
        self.assertEqual(row["buy_limit_source"]["oldid"], 6_457_777)
        self.assertNotIn("Oyster", PERIOD_GE_GUIDE_PRICES)
        self.assertEqual(row["guide_price_source"], "cache_value_fallback")

    def test_only_audited_unresolved_identities_remain_buy_limit_blocked(self):
        blocked = {
            name
            for name, row in GE_ITEM_CATALOG.items()
            if row["buy_limit"] is None
        }
        self.assertNotIn("Steel spear (kp)", GE_ITEM_CATALOG)
        self.assertEqual(
            blocked,
            {
                "Black warlock",
                "Cape",
                "Feather headdress",
                "Flowers",
                "Fremennik cloak",
                # Exchange item per its 2012-06-25 page (oldid 5827384), absent from the limit table.
                "Fremennik round shield",
                "Fremennik shirt",
                "Pirate bandana",
                "Pirate leggings",
                "Priest gown",
                "Robe top",
                "Ruby harvest",
                "Snowy knight",
                "Stripy pirate shirt",
                "Tribal top",
                "Villager armband",
                "Villager hat",
                "Villager robe",
                "Villager sandals",
                "Woven top",
            },
        )


if __name__ == "__main__":
    unittest.main()
