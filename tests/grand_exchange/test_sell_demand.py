import unittest
from copy import deepcopy

import pkg_alias  # noqa: F401
from ankiscape.logic import grand_exchange_logic as ge
from ankiscape.logic.grand_exchange.demand import (
    advance_sell_demand_pure, consume_sell_demand_pure, sell_demand_remaining_pure,
)

# Explicit synthetic balance fixtures; production catalog values come from data.
SPEC = {"tradeable": True, "exchangeable": True, "guide_price": 100,
        "buy_limit": 100, "sell_demand_daily_quantity": 10}
CATALOG = {"Logs": SPEC, "Coal": SPEC}


def player(quantity=10000):
    data = {**ge.default_ge_state_pure(),
            "inventory": {"Coins": 1000000, "Logs": quantity, "Coal": quantity, "Yew logs": quantity},
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7}}
    data["ge_market_state"]["last_processed_tick"] = 7
    return data


def place(data, quantity=1000, *, name="Logs", side="sell", price=None, spec=SPEC):
    before = deepcopy(data)
    result, status = ge.place_ge_offer_pure(
        data, side=side, item_name=name, quantity=quantity,
        unit_price=price if price is not None else (1 if side == "sell" else 150),
        item_spec=spec, confirmed=True,
    )
    assert status["ok"], status
    assert data == before, "placement mutated its caller"
    return result


def tick(data, at, *, catalog=CATALOG, draw=lambda: 0.0):
    before = deepcopy(data)
    source = deepcopy(data)
    source["shop_market_clock"] = {"answered_cards": at, "market_tick": at}
    result = ge.advance_ge_market_tick_pure(source, item_catalog=catalog, random_draw=draw)
    assert data == before, "market mutated its caller"
    assert source["ge_market_state"] == before["ge_market_state"]
    return result


def pool(data, name="Logs"):
    return data["ge_market_state"]["items"][name]["sell_demand"]


def assert_sell_conservation(test, data, starting=10000, sold=None, name="Logs", proceeds=None):
    orders = [order for order in data["ge_player_orders"] if order["item_name"] == name]
    if sold is None:
        sold = sum(order["completed_quantity"] for order in orders)
    test.assertEqual(starting, data["inventory"].get(name, 0)
                     + sum(order["escrow_items"] + order["collectible_items"] for order in orders)
                     + sold)
    if proceeds is not None:
        test.assertEqual(data["inventory"]["Coins"] - 1000000
                         + sum(order["collectible_coins"] for order in orders), proceeds)


class SellDemandTests(unittest.TestCase):
    def test_offer_size_cannot_enlarge_demand(self):
        for quantity in (1000, 9000):
            with self.subTest(quantity=quantity):
                data, result = tick(place(player(), quantity), 8)
                self.assertEqual(sum(fill["quantity"] for fill in result["fills"]), 10)
                self.assertEqual(pool(data), {"capacity": 10, "credit": 0, "last_tick": 8})
                assert_sell_conservation(self, data, proceeds=1000)

    def test_split_offers_share_one_allowance(self):
        data = player()
        for _ in range(6):
            data = place(data, 3)
        data, result = tick(data, 8)
        self.assertEqual(sum(fill["quantity"] for fill in result["fills"]), 10)
        self.assertEqual([order["completed_quantity"] for order in data["ge_player_orders"]],
                         [2, 2, 2, 2, 2, 0])
        self.assertEqual(pool(data)["credit"], 0)
        assert_sell_conservation(self, data)

    def test_other_items_have_independent_pools(self):
        data = place(place(player()), name="Coal")
        data, result = tick(data, 8)
        self.assertEqual([fill["quantity"] for fill in result["fills"]], [10, 10])
        self.assertEqual(pool(data)["credit"], 0)
        self.assertEqual(pool(data, "Coal")["credit"], 0)
        assert_sell_conservation(self, data)
        assert_sell_conservation(self, data, name="Coal")

    def test_exhaustion_preserves_escrow_and_has_no_settlement(self):
        data, _ = tick(place(player()), 8)
        order = data["ge_player_orders"][0]
        state = data["ge_market_state"]["items"]["Logs"]
        before = deepcopy(data)
        draws = []
        fill = ge._fill_order_for_tick_pure(
            data, order, item_spec=SPEC, item_state=state, market_tick=8, elapsed=1,
            random_draw=lambda: draws.append(0.0) or 0.0,
        )
        self.assertIsNone(fill)
        self.assertEqual(len(draws), 4)  # Keep probability and size draws even when exhausted.
        expected = deepcopy(before)
        expected["ge_market_state"]["rng_cursor"] += 4
        self.assertEqual(data, expected)
        self.assertEqual(order["status"], "partial")
        self.assertEqual(order["escrow_items"], 990)
        assert_sell_conservation(self, data, proceeds=1000)

    def test_fractional_recovery_and_daily_saturation(self):
        state = {}
        advance_sell_demand_pure(state, item_name="Logs", item_spec=SPEC, market_tick=8, new_item=True)
        self.assertEqual(state["sell_demand"]["credit"], 2400)
        consume_sell_demand_pure(state, 10)
        for at, credit, whole in ((9, 10, 0), (32, 240, 1), (248, 2400, 10), (9999, 2400, 10)):
            advance_sell_demand_pure(state, item_name="Logs", item_spec=SPEC, market_tick=at, new_item=False)
            self.assertEqual(state["sell_demand"]["credit"], credit)
            self.assertEqual(sell_demand_remaining_pure(state), whole)
        consume_sell_demand_pure(state, 10)
        advance_sell_demand_pure(state, item_name="Logs", item_spec=SPEC, market_tick=9999, new_item=False)
        self.assertEqual(state["sell_demand"]["credit"], 0)
        yew = {"sell_demand": {"capacity": 2200, "credit": 0, "last_tick": 7}}
        advance_sell_demand_pure(yew, item_name="Yew logs", item_spec={"buy_limit": 25000},
                                 market_tick=8, new_item=False)
        self.assertEqual(sell_demand_remaining_pure(yew), 9)
        consume_sell_demand_pure(yew, 9)
        self.assertEqual(yew["sell_demand"]["credit"], 40)
        self.assertEqual(sell_demand_remaining_pure(yew), 0)

    def test_once_per_item_recovery(self):
        data = player()
        for _ in range(6):
            data = place(data, 1000)
        data, _ = tick(data, 8)
        data, result = tick(data, 32)
        self.assertEqual(sum(fill["quantity"] for fill in result["fills"]), 1)
        self.assertEqual(pool(data), {"capacity": 10, "credit": 0, "last_tick": 32})
        # Production Yew calibration: a second offer shares the nine whole units
        # recovered by one tick, with forty fractional credits left over.
        yew_spec = {**SPEC, "sell_demand_daily_quantity": 2200}
        data = place(place(player(), 3000, name="Yew logs", spec=yew_spec),
                     3000, name="Yew logs", spec=yew_spec)
        data["ge_market_state"]["items"]["Yew logs"] = {
            "sell_demand": {"capacity": 2200, "credit": 0, "last_tick": 7}}
        data, result = tick(data, 8, catalog={"Yew logs": yew_spec})
        self.assertEqual([fill["quantity"] for fill in result["fills"]], [9])
        self.assertEqual(pool(data, "Yew logs")["credit"], 40)

    def test_repeated_and_skipped_intervals_have_equal_demand(self):
        data, _ = tick(place(player()), 8)
        data, _ = ge.edit_ge_offer_pure(
            data, 1, remaining_quantity=990, unit_price=1000,
            item_spec=SPEC, confirmed=True,
        )
        repeated = deepcopy(data)
        # Uncompetitive price refuses sales even across the skipped interval.
        for at in range(9, 33):
            repeated, _ = tick(repeated, at, draw=lambda: .999999)
        skipped, _ = tick(data, 32, draw=lambda: .999999)
        self.assertEqual(pool(repeated), pool(skipped))
        self.assertEqual(pool(skipped)["credit"], 240)

    def test_buy_fills_do_not_consume_or_directly_refill_sell_demand(self):
        data, _ = tick(place(player()), 8)
        data, _ = ge.cancel_ge_offer_pure(data, 1)
        data, _ = ge.collect_all_ge_offers_pure(data)
        data = place(data, 1000, side="buy")
        data, result = tick(data, 9)
        fill = result["fills"][0]
        self.assertEqual(fill["quantity"], 100)
        self.assertLess(fill["unit_price"], 150)
        self.assertEqual(pool(data)["credit"], 10)
        order = data["ge_player_orders"][0]
        self.assertEqual(order["escrow_coins"] + order["collectible_coins"]
                         + fill["quantity"] * fill["unit_price"], 150000)
        self.assertEqual(order["collectible_items"], 100)
        blocked, result = tick(data, 10)
        self.assertEqual(result["fills"], [])
        self.assertEqual(pool(blocked)["credit"], 20)
        self.assertEqual(blocked["ge_player_orders"], data["ge_player_orders"])

    def test_actual_filled_value_drives_impact(self):
        data = place(player())
        state = {"true_price": 100, "anchor_price": 100, "item_seed": 1,
                 "sell_demand": {"capacity": 10, "credit": 240, "last_tick": 8}}
        fill = ge._fill_order_for_tick_pure(
            data, data["ge_player_orders"][0], item_spec=SPEC, item_state=state,
            market_tick=8, elapsed=1, random_draw=lambda: 0.0,
        )
        self.assertEqual(fill["quantity"], 1)
        self.assertEqual(fill["impact_bps"], -25)
        self.assertEqual(data["ge_trade_history"]["Logs"]["notional"], 100)
        self.assertEqual(data["ge_player_orders"][0]["collectible_coins"], 100)
        self.assertEqual(data["ge_player_orders"][0]["escrow_items"], 999)
        self.assertEqual(state["sell_demand"]["credit"], 0)
        assert_sell_conservation(self, data, proceeds=100)
