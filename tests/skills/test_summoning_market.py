"""Pouch identity must survive registry composition and real market custody."""

import unittest
from copy import deepcopy
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS
from ankiscape.data import item_values
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.data.item_values import (
    EXCHANGEABLE_ITEM_NAMES,
    ITEM_VALUES,
    STACKABLE_ITEM_NAMES,
)
from ankiscape.data.shop_data import SHOP_SERVICES
from ankiscape.data.summoning_data import SUMMONING_POUCHES, SUMMONING_POUCHES_BY_ID
from ankiscape.generated.grand_exchange_period_generated import (
    PERIOD_GE_BUY_LIMITS,
    PERIOD_GE_GUIDE_PRICES,
)
from ankiscape.logic.grand_exchange_logic import (
    advance_ge_market_tick_pure,
    apply_ge_frontend_action_pure,
)
from ankiscape.logic.shop_fixtures import build_shop_fixture_player_data
from ankiscape.logic.shop_logic import apply_shop_service_pure, rollback_shop_event_pure


class SummoningMarketTest(unittest.TestCase):
    def test_registered_pouches_keep_identity_and_the_period_market_boundary(self):
        by_name = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for pouch in SUMMONING_POUCHES:
            with self.subTest(item=pouch.pouch_name):
                item = by_name[pouch.pouch_name]
                self.assertEqual(item.source_item_id, pouch.pouch_item_id)
                self.assertEqual(item.display_name, pouch.pouch_name)
                self.assertTrue(item.tradeable)
                if pouch.pouch_item_id == 21444:
                    self.assertNotIn(pouch.pouch_name, GE_ITEM_CATALOG)
                    self.assertNotIn(pouch.pouch_name, EXCHANGEABLE_ITEM_NAMES)
                    self.assertNotIn(pouch.pouch_name, PERIOD_GE_BUY_LIMITS)
                    continue
                row = GE_ITEM_CATALOG[pouch.pouch_name]
                self.assertEqual(row["source_item_id"], pouch.pouch_item_id)
                self.assertEqual(row["item_name"], pouch.pouch_name)
                expected_limit = 100 if pouch.pouch_item_id == 19622 else 5_000
                self.assertEqual(row["buy_limit"], expected_limit)
                self.assertEqual(row["buy_limit_source"]["oldid"], 6_457_777)
                if pouch.pouch_item_id not in {19622, 14623}:
                    self.assertNotIn(pouch.pouch_name, PERIOD_GE_GUIDE_PRICES)
                    self.assertEqual(row["guide_price"], ITEM_VALUES[pouch.pouch_name])
                    self.assertEqual(row["guide_price_source"], "cache_value_fallback")

    def test_exact_cache_aliases_supply_value_and_exchangeability_without_renaming(self):
        by_name = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for source_id, stored_name, cache_name, value in (
            (12053, "Vampire bat pouch", "Vampyre bat pouch", 2449),
            (12095, "Spirit cockatrice pouch", "Sp. cockatrice pouch", 2624),
            (12105, "Spirit coraxatrice pouch", "Sp. coraxatrice pouch", 2624),
            (12097, "Spirit guthatrice pouch", "Sp. guthatrice pouch", 2624),
            (12103, "Spirit pengatrice pouch", "Sp. pengatrice pouch", 2624),
            (12099, "Spirit saratrice pouch", "Sp. saratrice pouch", 2624),
            (12107, "Spirit vulatrice pouch", "Sp. vulatrice pouch", 2624),
            (12101, "Spirit zamatrice pouch", "Sp. zamatrice pouch", 2624),
        ):
            with self.subTest(item=stored_name):
                self.assertEqual(by_name[stored_name].source_item_id, source_id)
                self.assertEqual(ITEM_VALUES[stored_name], value)
                self.assertEqual(ITEM_VALUES[cache_name], value)
                self.assertIn(stored_name, EXCHANGEABLE_ITEM_NAMES)
                self.assertIn(cache_name, EXCHANGEABLE_ITEM_NAMES)
                self.assertNotIn(stored_name, STACKABLE_ITEM_NAMES)
                self.assertNotIn(cache_name, GE_ITEM_CATALOG)

    def test_aliases_preserve_real_cache_entries_and_support_an_absent_cache(self):
        with patch.dict(item_values.ITEM_VALUES_GENERATED, {"Spirit cockatrice pouch": 3141}):
            values, _, exchangeable = item_values._build_item_tables()
            self.assertEqual(values["Spirit cockatrice pouch"], 3141)
            self.assertEqual(values["Sp. cockatrice pouch"], 2624)
            self.assertNotIn("Spirit cockatrice pouch", exchangeable)
            self.assertIn("Sp. cockatrice pouch", exchangeable)
        with patch.multiple(
            item_values,
            ITEM_VALUES_GENERATED={},
            EXCHANGEABLE_ITEM_NAMES_GENERATED=frozenset(),
            STACKABLE_ITEM_NAMES_GENERATED=frozenset(),
        ):
            values, _, exchangeable = item_values._build_item_tables()
            self.assertTrue(values)
            self.assertEqual(exchangeable, frozenset())

    def test_bought_pouches_exchange_at_bogrog_undo_and_sell_through_real_market(self):
        for familiar_id in ("spiritwolf", "spiritcockatrice"):
            pouch = SUMMONING_POUCHES_BY_ID[familiar_id]
            name = pouch.pouch_name
            with self.subTest(item=name):
                player = build_shop_fixture_player_data()
                player["inventory"] = {"Coins": 20_000, "Spirit shards": 10}
                player["summoning_level"] = 99
                initial_coins = player["inventory"]["Coins"]
                guide = GE_ITEM_CATALOG[name]["guide_price"]
                player, placed = apply_ge_frontend_action_pure(
                    player, "place_offer",
                    {"side": "buy", "item_name": name, "quantity": 1, "unit_price": guide * 2},
                    item_catalog=GE_ITEM_CATALOG,
                )
                self.assertTrue(placed["ok"], placed)
                self.assertEqual(player["inventory"]["Coins"], initial_coins - guide * 2)
                self.assertEqual(player["inventory"].get(name, 0), 0)
                player["shop_market_clock"]["market_tick"] += 1
                player["shop_market_clock"]["answered_cards"] += 1
                filled, result = advance_ge_market_tick_pure(
                    player, item_catalog=GE_ITEM_CATALOG, random_draw=lambda: 0.0,
                )
                self.assertEqual(len(result["fills"]), 1, result)
                buy_price = result["fills"][0]["unit_price"]
                self.assertEqual(filled["ge_player_orders"][0]["status"], "complete")
                self.assertEqual(filled["inventory"].get(name, 0), 0)
                collected, result = apply_ge_frontend_action_pure(
                    filled, "collect_offer", {"order_id": placed["order"]["id"]},
                    item_catalog=GE_ITEM_CATALOG,
                )
                self.assertTrue(result["ok"], result)
                self.assertEqual(collected["inventory"][name], 1)
                self.assertEqual(collected["inventory"]["Coins"], initial_coins - buy_price)
                self.assertEqual(collected["ge_player_orders"], [])

                service_id = f"bogrog_exchange_{familiar_id}"
                service = SHOP_SERVICES[service_id]
                self.assertEqual(service["inputs"][0]["item_name"], name)
                self.assertEqual(service["inputs"][0]["item_id"], pouch.pouch_item_id)
                before = deepcopy(collected)
                exchanged, result = apply_shop_service_pure(collected, service_id, 1)
                self.assertTrue(result["allowed"], result)
                self.assertEqual(exchanged["inventory"][name], 0)
                self.assertEqual(exchanged["inventory"]["Spirit shards"], 10 + pouch.bogrog_shards)
                self.assertEqual(exchanged["inventory"]["Coins"], before["inventory"]["Coins"])
                self.assertEqual(exchanged["shop_market_clock"], before["shop_market_clock"])
                restored, result = rollback_shop_event_pure(exchanged, result["event_id"])
                self.assertTrue(result["allowed"], result)
                self.assertEqual(restored["inventory"], before["inventory"])

                selling, placed = apply_ge_frontend_action_pure(
                    restored, "place_offer",
                    {"side": "sell", "item_name": name, "quantity": 1, "unit_price": guide // 2},
                    item_catalog=GE_ITEM_CATALOG,
                )
                self.assertTrue(placed["ok"], placed)
                self.assertEqual(selling["inventory"][name], 0)
                self.assertEqual(selling["ge_player_orders"][0]["escrow_items"], 1)
                selling["shop_market_clock"]["market_tick"] += 1
                selling["shop_market_clock"]["answered_cards"] += 1
                filled, result = advance_ge_market_tick_pure(
                    selling, item_catalog=GE_ITEM_CATALOG, random_draw=lambda: 0.0,
                )
                self.assertEqual(len(result["fills"]), 1, result)
                sell_price = result["fills"][0]["unit_price"]
                self.assertEqual(filled["inventory"]["Coins"], initial_coins - buy_price)
                final, result = apply_ge_frontend_action_pure(
                    filled, "collect_offer", {"order_id": placed["order"]["id"]},
                    item_catalog=GE_ITEM_CATALOG,
                )
                self.assertTrue(result["ok"], result)
                self.assertEqual(final["inventory"][name], 0)
                self.assertEqual(final["inventory"]["Coins"], initial_coins - buy_price + sell_price)
                self.assertEqual(final["ge_player_orders"], [])


if __name__ == "__main__":
    unittest.main()
