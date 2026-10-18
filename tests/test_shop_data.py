import json
import runpy
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.shop_data import (
    SHOP_COVERAGE_SUMMARY,
    SHOP_PLAYER_SELL_PRICES,
    SHOP_DATA,
    SHOP_DATA_VERSION,
    SHOP_SERVICES,
    SHOP_VENDOR_ACTIONS,
    shop_extra_items_as_dict,
)
from ankiscape.data.summoning_data import SUMMONING_POUCHES
from tools.generate_npc_shop_data import (
    MANUAL_ITEM_METADATA,
    SHOP_ACCESS_RULES,
    ItemMeta,
    build_catalog,
    build_player_sell_prices,
    rewrite_stock_exclusions_from_generated,
)


class TestShopData(unittest.TestCase):
    def test_lletya_shops_open_when_mournings_end_part_i_starts(self):
        expected = {
            "kind": "quest",
            "quest_id": "mournings_end_part_i",
            "stage": "started",
            "label": "Mourning's End Part I",
        }
        for shop_id in (
            "lletya_archery_shop",
            "lletya_food_store",
            "lletya_general_store",
            "lletya_seamstress",
        ):
            with self.subTest(shop=shop_id):
                self.assertEqual(SHOP_ACCESS_RULES[shop_id], expected)
                self.assertEqual(SHOP_DATA[shop_id]["access"], expected)

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

    def test_unimplemented_currency_shops_are_visible_locked(self):
        locked_currency_shops = [
            shop
            for shop in SHOP_DATA.values()
            if not shop["currency_implemented"]
        ]
        self.assertGreaterEqual(len(locked_currency_shops), 1)
        for shop in locked_currency_shops:
            self.assertFalse(shop["currency_implemented"])
            if shop["visibility"] == "hidden":
                self.assertEqual(shop["lock_reason"], "activity_or_reward_system_not_implemented")
                continue
            self.assertEqual(shop["visibility"], "visible_locked")
            self.assertEqual(shop["lock_reason"], "currency_not_implemented")

    def test_tzhaar_shops_use_live_tokkul_and_cutoff_buy_tables(self):
        expected = {
            "tzhaarhurleks_ore_and_gem_store": {
                438: (5, 30),
                436: (5, 30),
                440: (2, 25),
                1623: (1, 48),
                1621: (1, 97),
                6571: (1, 2_700_000),
                9194: (50, 13_000),
            },
            "tzhaarhurtels_equipment_store": {
                6522: (10, 375),
                6523: (10, 60_000),
                6524: (10, 67_500),
                6525: (10, 37_500),
                6526: (10, 52_500),
                6527: (10, 45_000),
                6528: (10, 75_000),
                6568: (10, 90_000),
            },
            "tzhaarmejrohs_rune_store": {
                554: (1000, 26),
                555: (1000, 26),
                556: (1000, 26),
                557: (1000, 26),
                558: (1000, 24),
                559: (1000, 24),
                562: (300, 210),
                560: (100, 465),
            },
        }

        for shop_id, expected_rows in expected.items():
            with self.subTest(shop_id=shop_id):
                shop = SHOP_DATA[shop_id]
                self.assertEqual(shop["currency_id"], 6529)
                self.assertEqual(shop["currency_item_name"], "Tokkul")
                self.assertTrue(shop["currency_implemented"])
                self.assertTrue(shop["buy_only"])
                self.assertEqual(shop["visibility"], "visible")
                self.assertEqual(
                    {
                        row["item_id"]: (row["default_quantity"], row["buy_price"])
                        for row in shop["stock"]
                    },
                    expected_rows,
                )
                self.assertTrue(all(row["disposition"] == "live" for row in shop["stock"]))

    def test_services_vendor_actions_and_extra_items_are_exported(self):
        self.assertEqual(len(SHOP_SERVICES), 84)
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
        thakkrad = SHOP_SERVICES["thakkrad_cure_yak_hide"]
        self.assertEqual(thakkrad["provider"], "Thakkrad Sigmundson")
        self.assertEqual(thakkrad["location"], "Neitiznot")
        self.assertEqual(thakkrad["price"], 5)
        self.assertEqual(thakkrad["inputs"][0]["item_name"], "Yak-hide")
        self.assertEqual(thakkrad["outputs"][0]["item_name"], "Cured yak-hide")
        self.assertEqual(
            thakkrad["access"],
            {
                "kind": "quest",
                "quest_id": "the_fremennik_isles",
                "stage": 5,
                "label": "The Fremennik Isles",
            },
        )
        self.assertIn("oldid 5967010", thakkrad["source"])
        self.assertIn("oldid 6225987", thakkrad["source"])
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

    def test_generator_activates_tokkul_and_applies_cutoff_price_overrides(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            shops = temp / "shops"
            shops.mkdir()
            (shops / "tzhaarhurleks_ore_and_gem_store.json").write_text(
                json.dumps(
                    {
                        "name": "TzHaar-Hur-Lek's Ore and Gem Store",
                        "currency": 6529,
                        "items": [
                            {"item": {"id": 1623, "amount": 1}},
                            {"item": {"id": 6571, "amount": 1}},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            items = temp / "items.yml"
            items.write_text(
                "\n".join(
                    (
                        '- id: 6529',
                        '  name: "Tokkul"',
                        '  tradeable: false',
                        '- id: 1623',
                        '  name: "Uncut sapphire"',
                        '  tradeable: true',
                        '- id: 6571',
                        '  name: "Uncut onyx"',
                        '  tradeable: true',
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            catalog, _ledger = build_catalog(
                shops,
                items,
                {
                    1623: {"value": 25, "sell_price": 5, "tokkul_buy_override": 37},
                    6571: {"value": 1_800_000, "sell_price": 360_000, "tokkul_buy_override": 2_700_000},
                },
            )

        shop = catalog["shops"][0]
        rows = {row["item_id"]: row for row in shop["stock"]}
        self.assertTrue(shop["currency_implemented"])
        self.assertTrue(shop["buy_only"])
        self.assertEqual(shop["visibility"], "visible")
        self.assertEqual(rows[1623]["buy_price"], 48)
        self.assertEqual(rows[1623]["price_policy"], "period_shop_table_override")
        self.assertEqual(rows[6571]["buy_price"], 2_700_000)
        self.assertTrue(all(row["disposition"] == "live" for row in rows.values()))

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
        self.assertEqual(SHOP_COVERAGE_SUMMARY["player_sell_price_count"], len(SHOP_PLAYER_SELL_PRICES))
        self.assertTrue(any(shop["id"] == "a_test_shop" and shop["disposition"] == "excluded" for shop in ledger["shops"]))

        papa_mambo = next(shop for shop in ledger["shops"] if shop["id"] == "papa_mambos_shop")
        excluded_rows = {
            row["item_id"]: row
            for row in papa_mambo["stock_rows"]
            if row["disposition"] == "excluded"
        }
        self.assertEqual(set(excluded_rows), {19897, 19902, 19907, 19912, 19917})
        self.assertTrue(all(row["lock_reason"] == "period_source_exclusion" for row in excluded_rows.values()))

    def test_coverage_names_identify_the_same_runtime_stock_rows(self):
        ledger = json.loads(Path("memory-bank/source-audits/npc-shop-coverage-ledger-2026-07-06.json").read_text())
        audit_rows = {row["id"]: row for shop in ledger["shops"] for row in shop["stock_rows"]}
        self.assertEqual(len(audit_rows), sum(len(shop["stock_rows"]) for shop in ledger["shops"]))
        mismatches = []
        for shop in SHOP_DATA.values():
            for row in shop["stock"]:
                audit_row = audit_rows[row["id"]]
                if (audit_row["item_id"], audit_row["item_name"]) != (row["item_id"], row["item_name"]):
                    mismatches.append(row["id"])
        self.assertEqual(mismatches, [])


class TestPlayerPriceIdentity(unittest.TestCase):
    ARROW_GROUPS = (
        (882, "Bronze arrow", "Bronze arrows"),
        (884, "Iron arrow", "Iron arrows"),
        (886, "Steel arrow", "Steel arrows"),
        (888, "Mithril arrow", "Mithril arrows"),
        (890, "Adamant arrow", "Adamant arrows"),
        (892, "Rune arrow", "Rune arrows"),
        (4160, "Broad arrow", "Broad arrows"),
    )
    PROJECTIONS = {
        "Bullseye lantern": (4546, "Bullseye lantern (empty)"),
        "Mining helmet": (5014, "Mining helmet (unlit)"),
        "Oil lamp": (4525, "Oil lamp (empty)"),
        "Oil lantern": (4535, "Oil lantern (empty)"),
    }

    # Cache values and collision metadata are synthetic identity sentinels,
    # separate from the historical price assertions above.
    def assert_price_identities(self, items, shops, expected_ids, cache_ids):
        prices = {
            item_id: {"value": 100_000 + item_id, "sell_price": 200_000 + item_id}
            for item_id in cache_ids
        }
        actual = build_player_sell_prices(items, prices, shops)
        expected = (
            {name: 200_000 + item_id for name, item_id in expected_ids.items()},
            {name: 100_000 + item_id for name, item_id in expected_ids.items()},
        )
        self.assertEqual(actual, expected)

    def test_price_projections_retain_generic_and_exact_lamp_identities(self):
        states = {
            4522: ("Oil lamp", "Oil lamp (unlit)"),
            4525: ("Oil lamp", "Oil lamp (empty)"),
            4535: ("Oil lantern", "Oil lantern (empty)"),
            4537: ("Oil lantern", "Oil lantern (unlit)"),
            4546: ("Bullseye lantern", "Bullseye lantern (empty)"),
            4548: ("Bullseye lantern", "Bullseye lantern (unlit)"),
            5014: ("Mining helmet", "Mining helmet (unlit)"),
        }
        items = {
            item_id: ItemMeta(item_id, legacy_name, True, None)
            for item_id, (legacy_name, _state_name) in states.items()
        }
        expected_ids = {name: item_id for item_id, (_legacy, name) in states.items()}
        expected_ids.update({name: item_id for name, (item_id, _state) in self.PROJECTIONS.items()})

        self.assert_price_identities(
            items, [deepcopy(SHOP_DATA["miltogs_lamps"])], expected_ids, states,
        )

    def test_projection_precedence_is_metadata_then_projection_then_live(self):
        for name, (projection_id, state_name) in self.PROJECTIONS.items():
            for has_live_row in (False, True):
                with self.subTest(name=name, live=has_live_row):
                    items = {
                        373: ItemMeta(373, name, True, None),
                        projection_id: ItemMeta(projection_id, name, True, None),
                    }
                    shops = [{"stock": [{
                        "item_id": 373, "item_name": name, "disposition": "live",
                    }]}] if has_live_row else []
                    expected_ids = {
                        name: 373 if has_live_row else projection_id,
                        state_name: projection_id,
                    }
                    self.assert_price_identities(items, shops, expected_ids, items)

    def test_arrow_aliases_merge_before_first_live_selection(self):
        for item_id, legacy, canonical in self.ARROW_GROUPS:
            with self.subTest(name=canonical):
                items = {
                    item_id: ItemMeta(item_id, legacy, True, None),
                    7552: ItemMeta(7552, legacy, True, None),
                    7553: ItemMeta(7553, legacy, False, None),
                }
                shops = [
                    {"stock": [{"item_id": item_id, "item_name": canonical, "disposition": "blocked"}]},
                    {"stock": [
                        {"item_id": 7552, "item_name": legacy, "disposition": "live"},
                        {"item_id": item_id, "item_name": canonical, "disposition": "live"},
                    ]},
                    {"stock": [{"item_id": 7553, "item_name": canonical, "disposition": "live"}]},
                ]
                self.assert_price_identities(items, shops, {canonical: 7552}, items)

    def test_arrow_fallback_uses_lowest_tradeable_original_after_aliasing(self):
        for item_id, legacy, canonical in self.ARROW_GROUPS:
            for lower_tradeable in (True, False):
                with self.subTest(name=canonical, lower_tradeable=lower_tradeable):
                    items = {
                        7553: ItemMeta(7553, legacy, True, None),
                        7552: ItemMeta(7552, legacy, True, None),
                        item_id: ItemMeta(item_id, legacy, lower_tradeable, None),
                    }
                    expected_id = item_id if lower_tradeable else 7552
                    self.assert_price_identities(items, [], {canonical: expected_id}, items)

    def test_mithril_price_keeps_live_888_over_singular_source_variants(self):
        items = {
            888: ItemMeta(888, "Mithril arrow", True, None),
            7552: ItemMeta(7552, "Mithril arrow", True, None),
            7553: ItemMeta(7553, "Mithril arrow", False, None),
        }
        shops = [{"stock": [{
            "item_id": 888, "item_name": "Mithril arrows", "disposition": "live",
        }]}]
        self.assert_price_identities(items, shops, {"Mithril arrows": 888}, items)

    def test_stock_precedence_preserves_shop_and_row_order(self):
        items = {373: ItemMeta(373, "Swordfish", True, None)}
        shops = [
            {"stock": [
                {"item_id": 373, "item_name": "Swordfish", "disposition": disposition}
                for disposition in ("blocked", "locked", "hidden", "excluded")
            ]},
            {"stock": [
                {"item_id": 7553, "item_name": "Swordfish", "disposition": "live"},
                {"item_id": 7552, "item_name": "Swordfish", "disposition": "live"},
            ]},
            {"stock": [{"item_id": 373, "item_name": "Swordfish", "disposition": "live"}]},
        ]
        self.assert_price_identities(items, shops, {"Swordfish": 7553}, (373, 7552, 7553))

    def test_manual_domain_requires_exact_false_and_absent_original(self):
        cases = (
            ("manual False", {"tradeable": False}, False, True, False),
            ("manual True", {"tradeable": True}, False, False, True),
            ("missing flag", {}, False, False, True),
            ("unknown flag", {"tradeable": None}, False, False, True),
            ("zero flag", {"tradeable": 0}, False, False, True),
            ("string flag", {"tradeable": "false"}, False, False, True),
            ("original nontradeable", {"tradeable": False}, True, False, True),
            ("not manual", None, False, False, True),
        )
        for label, manual, original_present, row_tradeable, eligible in cases:
            with self.subTest(case=label):
                metadata = {} if manual is None else {23035: manual}
                items = {23035: ItemMeta(23035, "Spiked gauntlets", False, None)} if original_present else {}
                shops = [{"stock": [{
                    "item_id": 23035, "item_name": "Spiked gauntlets",
                    "disposition": "live", "tradeable": row_tradeable,
                }]}]
                expected_ids = {"Spiked gauntlets": 23035} if eligible else {}
                with patch.dict(MANUAL_ITEM_METADATA, metadata, clear=True):
                    self.assert_price_identities(items, shops, expected_ids, (23035,))

    def test_excluded_manual_id_preserves_same_name_live_or_original_fallback(self):
        items = {373: ItemMeta(373, "Spiked gauntlets", True, None)}
        for has_eligible_live in (True, False):
            with self.subTest(eligible_live=has_eligible_live):
                rows = [{"item_id": 23035, "item_name": "Spiked gauntlets", "disposition": "live"}]
                if has_eligible_live:
                    rows.append({"item_id": 888, "item_name": "Spiked gauntlets", "disposition": "live"})
                expected_id = 888 if has_eligible_live else 373
                self.assert_price_identities(
                    items, [{"stock": rows}], {"Spiked gauntlets": expected_id}, (373, 888, 23035),
                )

    def test_cache_fields_preserve_independent_floor_and_enum_semantics(self):
        cases = (
            ("independent", {"value": 11, "sell_price": 29}, 29, 11),
            ("zero floor", {"value": 0, "sell_price": 0}, 1, 1),
            ("enum zero", {"value": 0, "sell_price": 0, "coin_buy_override": 0, "coin_sell_override": 0}, 0, 0),
            ("enum wins", {"value": 11, "sell_price": 29, "coin_buy_override": 5, "coin_sell_override": 7}, 7, 5),
            ("enum absent", {"value": 11, "sell_price": 29, "coin_buy_override": -1, "coin_sell_override": -1}, 29, 11),
            ("buy only", {"value": 31, "coin_sell_override": 97}, None, 31),
            ("sell only", {"value": -1, "sell_price": 17, "coin_buy_override": 97}, 17, None),
            ("negative sell", {"value": 19, "sell_price": -1, "coin_sell_override": 97}, None, 19),
            ("override without base", {"coin_buy_override": 97, "coin_sell_override": 89}, None, None),
            ("invalid base", {"value": "11", "sell_price": None}, None, None),
        )
        items = {373: ItemMeta(373, "Swordfish", True, None)}
        for label, cache_row, sell, buy in cases:
            with self.subTest(case=label):
                expected = (
                    {} if sell is None else {"Swordfish": sell},
                    {} if buy is None else {"Swordfish": buy},
                )
                self.assertEqual(build_player_sell_prices(items, {373: cache_row}, []), expected)

    def test_missing_selected_cache_does_not_choose_another_identity(self):
        fallback = {"value": 100_373, "sell_price": 200_373}
        cases = (
            ("live missing", "Swordfish", None, [{"stock": [
                {"item_id": 7552, "item_name": "Swordfish", "disposition": "live"},
                {"item_id": 373, "item_name": "Swordfish", "disposition": "live"},
            ]}], ({}, {})),
            ("live empty", "Swordfish", {7552: {}}, [{"stock": [{
                "item_id": 7552, "item_name": "Swordfish", "disposition": "live",
            }]}], ({}, {})),
            ("projection missing", "Oil lantern", None, [], ({}, {})),
            ("projection buy only", "Oil lantern", {4535: {"value": 83}}, [], ({}, {"Oil lantern": 83})),
        )
        for label, name, extra_prices, shops, expected in cases:
            with self.subTest(case=label):
                items = {373: ItemMeta(373, name, True, None)}
                prices = {373: fallback, **(extra_prices or {})}
                self.assertEqual(build_player_sell_prices(items, prices, shops), expected)

    def test_price_selection_preserves_complete_catalog_inputs_and_nontradeable_support(self):
        shops = deepcopy(list(SHOP_DATA.values()))
        rows = [row for shop in shops for row in shop["stock"]]
        items = {
            row["item_id"]: ItemMeta(row["item_id"], row["item_name"], row["tradeable"], None)
            for row in rows if row["item_id"] != 23035
        }
        prices = {
            row["item_id"]: {"value": 100_000 + row["item_id"], "sell_price": 200_000 + row["item_id"]}
            for row in rows
        }
        original_inputs = deepcopy((items, prices, shops, MANUAL_ITEM_METADATA))

        sell, buy = build_player_sell_prices(items, prices, shops)

        self.assertEqual((items, prices, shops, MANUAL_ITEM_METADATA), original_inputs)
        nontradeable_names = {
            row["item_name"] for row in rows
            if row["disposition"] == "live" and row["item_id"] in items and not row["tradeable"]
        }
        self.assertLessEqual(nontradeable_names, sell.keys())
        self.assertLessEqual(nontradeable_names, buy.keys())
        self.assertNotIn("Spiked gauntlets", sell)
        self.assertNotIn("Spiked gauntlets", buy)


if __name__ == "__main__":
    unittest.main()
