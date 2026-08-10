import json
import runpy
import tempfile
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.shop_data import (
    SHOP_COVERAGE_SUMMARY,
    SHOP_DATA,
    SHOP_DATA_VERSION,
    SHOP_SERVICES,
    SHOP_VENDOR_ACTIONS,
    shop_extra_items_as_dict,
)
from ankiscape.data.summoning_data import SUMMONING_POUCHES
from tools.generate_npc_shop_data import build_catalog, rewrite_stock_exclusions_from_generated


class TestShopData(unittest.TestCase):
    def test_shop_only_items_preserve_source_identity_and_stackability(self):
        expected = {
            "Bag of salt": (4161, True),
            "Rock hammer": (4162, False),
            "Ice cooler": (6696, True),
            "Fungicide spray 10": (7421, False),
        }
        extra_items = shop_extra_items_as_dict()
        for item_name, (item_id, stackable) in expected.items():
            with self.subTest(item_name=item_name):
                self.assertEqual(extra_items[item_name]["source_item_id"], item_id)
                self.assertEqual(extra_items[item_name]["stackable"], stackable)

    def test_slayer_shops_name_spiked_gauntlets_as_the_period_item(self):
        rows = [
            row
            for shop in SHOP_DATA.values()
            for row in shop["stock"]
            if row["item_id"] == 23035
        ]

        self.assertEqual(len(rows), 8)
        self.assertEqual({row["item_name"] for row in rows}, {"Spiked gauntlets"})
        self.assertEqual({row["buy_price"] for row in rows}, {6})

    def test_miltog_lantern_states_keep_exact_names_and_prices(self):
        from ankiscape.data.shop_data import SHOP_EXTRA_ITEM_DATA, SHOP_PLAYER_BUY_PRICES, SHOP_PLAYER_SELL_PRICES

        rows = {
            row["item_id"]: row
            for row in SHOP_DATA["miltogs_lamps"]["stock"]
            if row["item_id"] in {4522, 4525, 4535, 4537, 4546, 4548, 5014}
        }
        expected = {
            4522: ("Oil lamp (unlit)", 28, 8),
            4525: ("Oil lamp (empty)", 25, 7),
            4535: ("Oil lantern (empty)", 120, 36),
            4537: ("Oil lantern (unlit)", 125, 37),
            4546: ("Bullseye lantern (empty)", 400, 120),
            4548: ("Bullseye lantern (unlit)", 420, 126),
            5014: ("Mining helmet (unlit)", 900, 270),
        }
        for item_id, (item_name, buy_price, sell_price) in expected.items():
            self.assertEqual(rows[item_id]["item_name"], item_name)
            self.assertEqual(SHOP_PLAYER_BUY_PRICES[item_name], buy_price)
            self.assertEqual(SHOP_PLAYER_SELL_PRICES[item_name], sell_price)
            self.assertIn(item_name, SHOP_EXTRA_ITEM_DATA)
    def test_generated_catalog_covers_all_source_shop_files_with_dispositions(self):
        self.assertEqual(SHOP_DATA_VERSION, 1)
        self.assertEqual(SHOP_COVERAGE_SUMMARY["source_shop_count"], 274)
        self.assertEqual(SHOP_COVERAGE_SUMMARY["runtime_shop_count"], 273)
        self.assertEqual(SHOP_COVERAGE_SUMMARY["excluded_shop_count"], 1)
        self.assertGreater(SHOP_COVERAGE_SUMMARY["stock_row_count"], 2700)
        self.assertGreater(SHOP_COVERAGE_SUMMARY["live_stock_row_count"], SHOP_COVERAGE_SUMMARY["locked_stock_row_count"])
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
                    self.assertIsInstance(row["sell_price"], int)
                    self.assertEqual(shop["currency_id"], 995)
                    self.assertTrue(shop["currency_implemented"])

    def test_coin_stock_uses_darkan_cache_price_policy_without_unresolved_price_locks(self):
        unresolved_rows = [
            (shop, row)
            for shop in SHOP_DATA.values()
            for row in shop["stock"]
            if row["lock_reason"] == "price_policy_unresolved" or row["price_policy"] == "cache_price_unresolved"
        ]
        self.assertEqual(unresolved_rows, [])
        self.assertTrue(
            any(row["price_policy"] == "darkan_shop_cache_price" for shop in SHOP_DATA.values() for row in shop["stock"])
        )

    def test_feather_rows_are_live_with_darkan_cache_prices(self):
        feather_rows = [
            (shop, row)
            for shop in SHOP_DATA.values()
            for row in shop["stock"]
            if row["item_name"] == "Feather"
        ]
        self.assertGreaterEqual(len(feather_rows), 2)
        for shop, row in feather_rows:
            self.assertEqual(shop["currency_id"], 995)
            self.assertEqual(row["disposition"], "live")
            self.assertEqual(row["lock_reason"], "")
            self.assertIsInstance(row["buy_price"], int)

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
        self.assertEqual(len(SHOP_SERVICES), 83)
        self.assertEqual(
            {
                service_id
                for service_id in SHOP_SERVICES
                if service_id.startswith("bogrog_exchange_")
            },
            {
                f"bogrog_exchange_{pouch.id}"
                for pouch in SUMMONING_POUCHES
                if pouch.bogrog_level is not None
                and pouch.bogrog_shards is not None
            },
        )
        bob = SHOP_SERVICES["bob_barter_decant_four"]
        self.assertEqual(bob["provider"], "Bob Barter (herbs)")
        self.assertEqual(bob["location"], "Grand Exchange")
        self.assertEqual(bob["action_type"], "decant_potions_to_dose")
        self.assertEqual(bob["default_target_dose"], 4)
        self.assertEqual(bob["price"], 0)
        self.assertIn("oldid 6222086", bob["source"])
        blandebir = SHOP_SERVICES["blandebir_fill_ale_yeast"]
        self.assertEqual(blandebir["provider"], "Blandebir")
        self.assertEqual(blandebir["location"], "Keldagrim")
        self.assertEqual(blandebir["price"], 25)
        self.assertEqual(blandebir["inputs"][0]["item_name"], "Empty pot")
        self.assertEqual(blandebir["outputs"][0]["item_name"], "Ale yeast")
        self.assertTrue(blandebir["batchable"])
        self.assertEqual(
            blandebir["access"],
            {
                "kind": "quest",
                "quest_id": "the_giant_dwarf",
                "stage": "started",
                "label": "The Giant Dwarf",
            },
        )
        self.assertIn("oldid 4227753", blandebir["source"])
        for service_id, action_type in (
            ("teplin_fill_potion_flasks", "fill_potion_flasks"),
            ("teplin_decant_flasks_to_vials", "decant_flasks_to_vials"),
        ):
            with self.subTest(service_id=service_id):
                teplin = SHOP_SERVICES[service_id]
                self.assertEqual(teplin["provider"], "Teplin Macagan")
                self.assertEqual(teplin["location"], "Oo'glog")
                self.assertEqual(teplin["action_type"], action_type)
                self.assertEqual(teplin["price"], 0)
                self.assertEqual(
                    teplin["access"],
                    {
                        "kind": "quest",
                        "quest_id": "as_a_first_resort",
                        "label": "As a First Resort",
                    },
                )
                self.assertIn("oldid 6225976", teplin["source"])
                self.assertIn("oldid 6394714", teplin["source"])
        leon = SHOP_SERVICES["leon_fletch_long_kebbit_bolts"]
        self.assertEqual(leon["provider"], "Leon")
        self.assertEqual(leon["location"], "Yanille")
        self.assertEqual(leon["price"], 40)
        self.assertEqual(
            leon["inputs"],
            [
                {
                    "item_id": 10107,
                    "quantity": 1,
                    "item_name": "Long kebbit spike",
                    "tradeable": True,
                }
            ],
        )
        self.assertEqual(
            leon["outputs"],
            [
                {
                    "item_id": 10159,
                    "quantity": 6,
                    "item_name": "Long kebbit bolts",
                    "tradeable": True,
                }
            ],
        )
        self.assertEqual(leon["action_type"], "item_conversion")
        self.assertTrue(leon["batchable"])
        self.assertIn("oldid 6484443", leon["source"])
        for pouch in SUMMONING_POUCHES:
            service = SHOP_SERVICES.get(f"bogrog_exchange_{pouch.id}")
            if pouch.bogrog_level is None or pouch.bogrog_shards is None:
                self.assertIsNone(service)
                continue
            self.assertEqual(service["provider"], "Bogrog")
            self.assertTrue(service["batchable"])
            self.assertEqual(service["required_level"], pouch.bogrog_level)
            self.assertEqual(
                service["inputs"][0]["item_name"], pouch.pouch_name
            )
            self.assertEqual(
                service["outputs"][0]["quantity"], pouch.bogrog_shards
            )
        self.assertIn("bartender_buy_beer", SHOP_VENDOR_ACTIONS)
        self.assertIn("benny_buy_varrock_herald", SHOP_VENDOR_ACTIONS)
        self.assertIn("karim_buy_kebab", SHOP_VENDOR_ACTIONS)
        extra_items = shop_extra_items_as_dict()
        for item_name in ("Beer", "Silk", "Newspaper"):
            self.assertIn(item_name, extra_items)
        # Conversion inputs/outputs register through the Utility/combat paths
        # now, not through the shop catalog export.
        self.assertNotIn("Leather", extra_items)

    def test_player_price_tables_follow_darkan_price_math(self):
        """Absolute Darkan sell parity (owner decision 2026-07-06): the
        tables are Shop.java getSellPrice/getBuyPrice for each name's
        canonical id — floored to 1, never clamped or name-minimized."""
        from ankiscape.data.shop_data import SHOP_PLAYER_BUY_PRICES, SHOP_PLAYER_SELL_PRICES

        self.assertGreater(len(SHOP_PLAYER_SELL_PRICES), 6000)
        self.assertTrue(all(price >= 1 for price in SHOP_PLAYER_SELL_PRICES.values()))
        self.assertTrue(all(price >= 1 for price in SHOP_PLAYER_BUY_PRICES.values()))
        # Canonical id = the id live shops stock: Swordfish is id 373
        # (sellPrice 120), not the 3-coin variant id that no shop stocks.
        self.assertEqual(SHOP_PLAYER_SELL_PRICES["Swordfish"], 120)
        # Rasolo's custom 1-coin Poison id is canonical for its name, and its
        # own cache sellPrice is 1 — the engine allows no flip profit here.
        self.assertEqual(SHOP_PLAYER_SELL_PRICES["Poison"], 1)

    def test_generator_excludes_contaminated_farming_stock_without_renumbering_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            shops = temp / "shops"
            shops.mkdir()
            (shops / "papa_mambos_shop.json").write_text(
                json.dumps({
                    "name": "Papa Mambo's Shop",
                    "items": [
                        {"item": {"id": 19922, "amount": 10}},
                        {"item": {"id": 19897, "amount": 10}, "customPrice": 10000},
                        {"item": {"id": 19967, "amount": 10}},
                    ],
                }),
                encoding="utf-8",
            )
            items = temp / "items.yml"
            items.write_text(
                "\n".join((
                    '- id: 19922', '  name: "Red blossom seed"', '  tradeable: true',
                    '- id: 19897', '  name: "Erzille seed"', '  tradeable: true',
                    '- id: 19967', '  name: "Juju teleport spiritbag"', '  tradeable: true',
                )) + "\n",
                encoding="utf-8",
            )
            prices = {
                item_id: {"value": 10, "sell_price": 3}
                for item_id in (19922, 19897, 19967)
            }

            catalog, ledger = build_catalog(shops, items, prices)

        runtime_rows = catalog["shops"][0]["stock"]
        self.assertEqual(
            [row["id"] for row in runtime_rows],
            ["papa_mambos_shop:0:19922", "papa_mambos_shop:2:19967"],
        )
        audit_rows = ledger["shops"][0]["stock_rows"]
        excluded = next(row for row in audit_rows if row["item_id"] == 19897)
        self.assertEqual(excluded["id"], "papa_mambos_shop:1:19897")
        self.assertEqual(excluded["disposition"], "excluded")
        self.assertEqual(excluded["lock_reason"], "period_source_exclusion")
        self.assertEqual(catalog["summary"]["excluded_stock_row_count"], 1)
        self.assertEqual(ledger["summary"], catalog["summary"])

    def test_generator_recovers_spiked_gauntlets_missing_from_legacy_items_yml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            shops = temp / "shops"
            shops.mkdir()
            (shops / "slayer_equipment.json").write_text(
                json.dumps(
                    {
                        "name": "Slayer Equipment",
                        "items": [{"item": {"id": 23035, "amount": 10}}],
                    }
                ),
                encoding="utf-8",
            )
            items = temp / "items.yml"
            items.write_text("", encoding="utf-8")

            catalog, ledger = build_catalog(
                shops,
                items,
                {23035: {"value": 6, "sell_price": 1}},
            )

        row = catalog["shops"][0]["stock"][0]
        self.assertEqual(row["item_name"], "Spiked gauntlets")
        self.assertEqual(row["item_id"], 23035)
        self.assertEqual(row["buy_price"], 6)
        self.assertEqual(row["disposition"], "live")
        self.assertEqual(row["lock_reason"], "")
        self.assertEqual(ledger["summary"], catalog["summary"])

    def test_focused_regeneration_keeps_runtime_and_audit_outputs_consistent(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            runtime_out = temp / "shop_data.py"
            ledger_out = temp / "shop_ledger.json"
            summary_out = temp / "shop_summary.md"
            summary = rewrite_stock_exclusions_from_generated(
                repo_root / "data" / "shop_data.py",
                runtime_out,
                existing_ledger_path=repo_root / "memory-bank/source-audits/npc-shop-coverage-ledger-2026-07-06.json",
                ledger_output_path=ledger_out,
                summary_output_path=summary_out,
            )
            generated = runpy.run_path(str(runtime_out))
            ledger = json.loads(ledger_out.read_text(encoding="utf-8"))
            summary_text = summary_out.read_text(encoding="utf-8")

        self.assertEqual(generated["SHOP_COVERAGE_SUMMARY"], summary)
        self.assertEqual(ledger["summary"], summary)
        self.assertEqual(summary["excluded_stock_row_count"], 5)
        runtime_ids = {row["id"] for row in generated["SHOP_DATA"]["papa_mambos_shop"]["stock"]}
        audit_live_ids = {
            row["id"]
            for shop in ledger["shops"]
            if shop["id"] == "papa_mambos_shop"
            for row in shop["stock_rows"]
            if row["disposition"] != "excluded"
        }
        self.assertEqual(audit_live_ids, runtime_ids)
        self.assertIn("papa_mambos_shop:8:19967", runtime_ids)
        self.assertTrue(summary_text.endswith("\n"))

    def test_machine_readable_ledger_matches_catalog_summary(self):
        ledger_path = Path("memory-bank/source-audits/npc-shop-coverage-ledger-2026-07-06.json")
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(ledger["shop_data_version"], SHOP_DATA_VERSION)
        self.assertEqual(ledger["summary"], SHOP_COVERAGE_SUMMARY)
        self.assertTrue(any(shop["id"] == "a_test_shop" and shop["disposition"] == "excluded" for shop in ledger["shops"]))

        papa_mambo = next(shop for shop in ledger["shops"] if shop["id"] == "papa_mambos_shop")
        excluded_rows = {
            row["item_id"]: row
            for row in papa_mambo["stock_rows"]
            if row["disposition"] == "excluded"
        }
        self.assertEqual(set(excluded_rows), {19897, 19902, 19907, 19912, 19917})
        self.assertTrue(all(row["lock_reason"] == "period_source_exclusion" for row in excluded_rows.values()))


if __name__ == "__main__":
    unittest.main()
