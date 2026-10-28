import json
import unittest
from copy import deepcopy

import pkg_alias  # noqa: F401
from ankiscape.core.storage_pure import migrate_loaded_data
from ankiscape.logic import grand_exchange_logic as ge
from ankiscape.logic.grand_exchange.demand import advance_sell_demand_pure
from tests.grand_exchange.test_sell_demand import (
    SPEC, player, place, tick, pool, assert_sell_conservation,
)


class DemandPersistenceTests(unittest.TestCase):
    def _lifecycle(self, data, operation, *args, **kwargs):
        before = deepcopy(data)
        result, status = operation(data, *args, **kwargs)
        self.assertTrue(status["ok"], status)
        self.assertEqual(data, before)
        self.assertEqual(pool(result), pool(data))
        return result

    def test_edit_cancel_collect_replace_cannot_refill(self):
        data = player()
        for _ in range(6):
            data = place(data, 100)
        data, result = tick(data, 8)
        sold = sum(fill["quantity"] for fill in result["fills"])
        proceeds = sum(fill["quantity"] * fill["unit_price"] for fill in result["fills"])
        self.assertEqual(sold, 10)
        data = self._lifecycle(data, ge.collect_ge_offer_pure, 1)
        data = self._lifecycle(data, ge.edit_ge_offer_pure, 1,
                               remaining_quantity=50, unit_price=2, item_spec=SPEC, confirmed=True)
        assert_sell_conservation(self, data, sold=sold, proceeds=proceeds)
        for order in list(data["ge_player_orders"]):
            data = self._lifecycle(data, ge.cancel_ge_offer_pure, order["id"])
            assert_sell_conservation(self, data, sold=sold, proceeds=proceeds)
        data = self._lifecycle(data, ge.collect_all_ge_offers_pure)
        self.assertEqual(data["ge_player_orders"], [])
        assert_sell_conservation(self, data, sold=sold, proceeds=proceeds)
        data = place(data, 1000)
        data, result = tick(data, 8)
        self.assertEqual(result["fills"], [])
        self.assertEqual(pool(data)["credit"], 0)
        assert_sell_conservation(self, data, sold=sold, proceeds=proceeds)
        # Combine partial collection and cancellation for adjacent buy accounting.
        bought, fills = tick(place(player(), 1000, side="buy"), 8)
        spend = sum(fill["quantity"] * fill["unit_price"] for fill in fills["fills"])
        quantity = sum(fill["quantity"] for fill in fills["fills"])
        bought = self._lifecycle(bought, ge.collect_ge_offer_pure, 1)
        order = bought["ge_player_orders"][0]
        self.assertEqual(bought["inventory"]["Coins"] + order["escrow_coins"] + spend, 1000000)
        bought = self._lifecycle(bought, ge.cancel_ge_offer_pure, 1)
        order = bought["ge_player_orders"][0]
        self.assertEqual(bought["inventory"]["Coins"] + order["collectible_coins"] + spend, 1000000)
        bought = self._lifecycle(bought, ge.collect_all_ge_offers_pure)
        self.assertEqual(bought["inventory"]["Coins"] + spend, 1000000)
        self.assertEqual(bought["inventory"]["Logs"], 10000 + quantity)

    def test_json_and_storage_migration_preserve_spent_demand(self):
        data, _ = tick(place(player()), 8)
        before = deepcopy(data)
        restored = json.loads(json.dumps(data))
        sanitized = ge.sanitize_ge_state_pure(restored)
        self.assertEqual(sanitized["ge_market_state"], data["ge_market_state"])
        migrated = migrate_loaded_data(restored, {})
        self.assertEqual(migrated["ge_market_state"], data["ge_market_state"])
        self.assertEqual(migrated["ge_player_orders"], data["ge_player_orders"])
        self.assertEqual(restored, before)
        for state in (restored, migrated):
            updated, _ = tick(state, 9)
            self.assertEqual(pool(updated)["credit"], 10)
            self.assertEqual(updated["ge_player_orders"], state["ge_player_orders"])
        projection_source = deepcopy(data)
        ge.ge_frontend_projection_pure(projection_source, item_catalog={"Logs": SPEC})
        self.assertEqual(projection_source, data)

    def test_legacy_initialization_occurs_once(self):
        for version in (None, 1):
            with self.subTest(version=version):
                data = place(player())
                market = data["ge_market_state"]
                market["items"] = {"Logs": {"last_processed_tick": 7},
                                   "Coal": {"sell_demand": {"capacity": 10, "credit": 0, "last_tick": 7}}}
                if version is None:
                    market.pop("version")
                else:
                    market["version"] = version
                before = deepcopy(data)
                loaded = ge.sanitize_ge_state_pure(data)
                self.assertEqual(data, before)
                self.assertEqual(loaded["ge_market_state"]["version"], 2)
                self.assertEqual(pool(loaded), {"uninitialized": True})
                self.assertEqual(pool(loaded, "Coal")["credit"], 0)
                data.update(loaded)
                data, result = tick(data, 1000)
                self.assertEqual(sum(fill["quantity"] for fill in result["fills"]), 10)
                self.assertEqual(pool(data)["credit"], 0)  # No catch-up on initialization.
                data.update(ge.sanitize_ge_state_pure(data))
                data, result = tick(data, 1001)
                self.assertEqual(result["fills"], [])
                self.assertEqual(pool(data)["credit"], 10)

    def test_version_two_missing_or_malformed_demand_fails_closed(self):
        valid = {"capacity": 10, "credit": 0, "last_tick": 7}
        malformed = [None, {}, {"capacity": 10}, "bad", {"uninitialized": 1},
                     {"uninitialized": True, "extra": 1}]
        for field in ("capacity", "credit", "last_tick"):
            for value in (True, False, "1", 1.5, -1, None):
                malformed.append({**valid, field: value})
        malformed.extend(({**valid, "capacity": 0}, {**valid, "capacity": ge.GE_MAX_OFFER_QUANTITY + 1},
                          {**valid, "credit": 2401}, {**valid, "last_tick": 9}))
        cases = [{}, *({"sell_demand": record} for record in malformed)]
        for state in [None, "corrupt", *cases]:
            with self.subTest(state=state):
                data = place(player())
                data["ge_market_state"]["items"]["Logs"] = state
                data, result = tick(data, 8)
                self.assertEqual(result["fills"], [])
                self.assertEqual(pool(data), {"capacity": 10, "credit": 0, "last_tick": 8})
                self.assertEqual(data["ge_player_orders"][0]["escrow_items"], 1000)
                assert_sell_conservation(self, data, proceeds=0)
        # Metadata changes preserve spent credit and recover only elapsed current capacity.
        for capacity, credit, expected in ((20, 1000, 1010), (20, 4000, 2400), (5, 0, 10)):
            state = {"sell_demand": {"capacity": capacity, "credit": credit, "last_tick": 7}}
            advance_sell_demand_pure(state, item_name="Logs", item_spec=SPEC, market_tick=8, new_item=False)
            self.assertEqual(state["sell_demand"]["credit"], expected)
        state = {}
        advance_sell_demand_pure(state, item_name="Logs",
                                 item_spec={**SPEC, "sell_demand_daily_quantity": ge.GE_MAX_OFFER_QUANTITY + 1},
                                 market_tick=8, new_item=True)
        self.assertEqual(state["sell_demand"]["capacity"], ge.GE_MAX_OFFER_QUANTITY)

    def test_dormant_item_recovers_only_elapsed_capacity(self):
        data, _ = tick(place(player()), 8)
        data = self._lifecycle(data, ge.cancel_ge_offer_pure, 1)
        data = self._lifecycle(data, ge.collect_all_ge_offers_pure)
        data, result = tick(data, 32)
        self.assertEqual(result["fills"], [])
        self.assertEqual(pool(data), {"capacity": 10, "credit": 0, "last_tick": 8})
        data = place(data)
        data, result = tick(data, 33)
        self.assertEqual(sum(fill["quantity"] for fill in result["fills"]), 1)
        self.assertEqual(pool(data), {"capacity": 10, "credit": 10, "last_tick": 33})
        assert_sell_conservation(self, data, sold=11)

    def test_repeated_same_tick_is_idempotent(self):
        data, _ = tick(place(player()), 8)
        before = deepcopy(data)
        for _ in range(3):
            data, result = tick(data, 8)
            self.assertEqual(result["fills"], [])
            self.assertEqual(data, before)
