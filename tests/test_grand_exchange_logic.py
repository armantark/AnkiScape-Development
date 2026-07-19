import unittest
from copy import deepcopy

from grand_exchange_logic import (
    GE_BUY_LIMIT_WINDOW_CARDS,
    GE_SLOT_COUNT,
    advance_ge_market_tick_pure,
    cancel_ge_offer_pure,
    collect_all_ge_offers_pure,
    collect_ge_offer_pure,
    default_ge_state_pure,
    place_ge_offer_pure,
    preview_ge_offer_pure,
    sanitize_ge_state_pure,
    set_ironman_mode_pure,
)


LOGS = {
    "tradeable": True,
    "exchangeable": True,
    "guide_price": 100,
    "buy_limit": 25_000,
}


def _player(**inventory):
    return {
        **default_ge_state_pure(),
        "inventory": {"Coins": 10_000, "Logs": 20, **inventory},
        "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
    }


class GrandExchangeLogicTest(unittest.TestCase):
    @staticmethod
    def _advance(
        player,
        *,
        market_tick,
        draws=(0.5, 0.0, 0.5, 1.0),
        item_spec=LOGS,
    ):
        player["shop_market_clock"] = {
            "answered_cards": market_tick,
            "market_tick": market_tick,
        }
        draw_iter = iter(draws)
        return advance_ge_market_tick_pure(
            player,
            item_catalog={"Logs": item_spec},
            random_draw=lambda: next(draw_iter),
        )

    def test_default_and_sanitized_state_are_bounded(self):
        state = sanitize_ge_state_pure(
            {
                "ironman_mode": 1,
                "ge_market_state": {
                    "last_processed_tick": "-4",
                    "rng_seed": "9",
                    "rng_cursor": "3",
                    "items": {"Logs": {"true_price": 101}},
                },
                "ge_player_orders": [
                    {
                        "id": index + 1,
                        "side": "buy",
                        "item_name": "Logs",
                        "original_quantity": 1,
                        "remaining_quantity": 1,
                        "submitted_unit_price": 100,
                        "escrow_coins": 100,
                        "status": "open",
                    }
                    for index in range(GE_SLOT_COUNT + 2)
                ],
                "ge_next_order_id": 2,
            }
        )

        self.assertTrue(state["ironman_mode"])
        self.assertEqual(state["ge_market_state"]["last_processed_tick"], 0)
        self.assertEqual(state["ge_market_state"]["rng_seed"], 9)
        self.assertEqual(len(state["ge_player_orders"]), GE_SLOT_COUNT)
        self.assertEqual(state["ge_next_order_id"], GE_SLOT_COUNT + 1)

    def test_sanitizer_cannot_turn_corrupt_escrow_into_assets(self):
        state = sanitize_ge_state_pure(
            {
                "ge_player_orders": [
                    {
                        "id": 1,
                        "side": "buy",
                        "item_name": "Logs",
                        "original_quantity": 1,
                        "remaining_quantity": 1,
                        "completed_quantity": 0,
                        "submitted_unit_price": 100,
                        "escrow_coins": 999_999,
                        "escrow_items": 999,
                        "collectible_coins": 999_999,
                        "collectible_items": 999,
                        "status": "open",
                    },
                    {
                        "id": 2,
                        "side": "sell",
                        "item_name": "Logs",
                        "original_quantity": 2,
                        "remaining_quantity": 2,
                        "completed_quantity": 0,
                        "submitted_unit_price": 100,
                        "escrow_coins": 999_999,
                        "escrow_items": 999,
                        "collectible_coins": 999_999,
                        "collectible_items": 999,
                        "status": "open",
                    },
                ]
            }
        )

        buy, sell = state["ge_player_orders"]
        self.assertEqual(buy["escrow_coins"], 100)
        self.assertEqual(buy["escrow_items"], 0)
        self.assertEqual(buy["collectible_coins"], 0)
        self.assertEqual(buy["collectible_items"], 0)
        self.assertEqual(sell["escrow_coins"], 0)
        self.assertEqual(sell["escrow_items"], 2)
        self.assertEqual(sell["collectible_coins"], 0)
        self.assertEqual(sell["collectible_items"], 0)

        dropped = sanitize_ge_state_pure(
            {
                "ge_player_orders": [
                    {
                        "id": 1,
                        "side": "buy",
                        "item_name": "Logs",
                        "original_quantity": 1,
                        "remaining_quantity": 1,
                        "submitted_unit_price": 100,
                        "escrow_coins": 0,
                        "status": "open",
                    }
                ]
            }
        )
        self.assertEqual(dropped["ge_player_orders"], [])

    def test_market_tick_recovers_corrupt_nested_item_state(self):
        player = _player()
        player["ge_market_state"].update(
            {
                "last_processed_tick": 7,
                "items": {
                    "Logs": {
                        "anchor_price": "bad",
                        "guide_price": 0,
                        "player_impact_bps": "bad",
                        "ambient_bps": None,
                        "shock_peak_bps": "bad",
                        "last_processed_tick": 7,
                    }
                },
            }
        )
        player, _result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=1,
            unit_price=50,
            item_spec=LOGS,
        )

        advanced, result = self._advance(
            player,
            market_tick=8,
            draws=(0.5, 1.0, 0.5, 1.0),
        )

        self.assertEqual(result["fills"], [])
        item_state = advanced["ge_market_state"]["items"]["Logs"]
        self.assertEqual(item_state["anchor_price"], 100)
        self.assertEqual(item_state["guide_price"], 100)
        self.assertEqual(item_state["player_impact_bps"], 0)
        self.assertEqual(item_state["ambient_bps"], 0)

    def test_offer_rejects_values_outside_signed_item_bounds(self):
        player = _player(Coins=10**30)
        for quantity, unit_price in (
            (2_147_483_648, 1),
            (1, 2_147_483_648),
        ):
            with self.subTest(quantity=quantity, unit_price=unit_price):
                preview = preview_ge_offer_pure(
                    player,
                    side="buy",
                    item_name="Logs",
                    quantity=quantity,
                    unit_price=unit_price,
                    item_spec=LOGS,
                )
                self.assertFalse(preview["ok"])
                self.assertEqual(preview["reason"], "invalid_offer")

    def test_preview_rejects_unknown_untradeable_and_unsourced_buy_rows(self):
        player = _player()
        cases = (
            (None, "unknown_item"),
            ({"tradeable": False, "guide_price": 100, "buy_limit": 100}, "untradeable_item"),
            ({"tradeable": True, "exchangeable": False, "guide_price": 100, "buy_limit": 100}, "not_exchangeable"),
            ({"tradeable": True, "exchangeable": True, "buy_limit": 100}, "guide_price_unavailable"),
            ({"tradeable": True, "exchangeable": True, "guide_price": 100}, "buy_limit_unavailable"),
        )
        for spec, reason in cases:
            with self.subTest(reason=reason):
                result = preview_ge_offer_pure(
                    player,
                    side="buy",
                    item_name="Logs",
                    quantity=1,
                    unit_price=100,
                    item_spec=spec,
                )
                self.assertFalse(result["ok"])
                self.assertEqual(result["reason"], reason)

    def test_buy_offer_reserves_coins_and_uses_shared_market_tick(self):
        updated, result = place_ge_offer_pure(
            _player(),
            side="buy",
            item_name="Logs",
            quantity=5,
            unit_price=110,
            item_spec=LOGS,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(updated["inventory"]["Coins"], 9_450)
        order = updated["ge_player_orders"][0]
        self.assertEqual(order["escrow_coins"], 550)
        self.assertEqual(order["escrow_items"], 0)
        self.assertEqual(order["created_market_tick"], 7)

    def test_offer_preview_uses_the_persisted_live_guide_price(self):
        player = _player()
        player["ge_market_state"]["items"] = {
            "Logs": {"guide_price": 105}
        }

        preview = preview_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=1,
            unit_price=105,
            item_spec=LOGS,
        )

        self.assertTrue(preview["ok"])
        self.assertEqual(preview["guide_price"], 105)

    def test_high_alchemy_is_soft_pressure_not_a_hard_price_floor(self):
        alch_logs = {**LOGS, "high_alchemy_value": 200}
        player = _player()
        player["ge_market_state"]["last_processed_tick"] = 7
        player, _result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=1,
            unit_price=50,
            item_spec=alch_logs,
        )

        advanced, result = self._advance(
            player,
            market_tick=8,
            draws=(0.5, 1.0),
            item_spec=alch_logs,
        )

        self.assertEqual(result["fills"], [])
        item_state = advanced["ge_market_state"]["items"]["Logs"]
        self.assertEqual(item_state["current_alchemy_pressure_bps"], 1_500)
        self.assertEqual(item_state["true_price"], 115)
        self.assertLess(item_state["true_price"], 200)

    def test_sell_offer_reserves_only_the_selected_quantity(self):
        updated, result = place_ge_offer_pure(
            _player(),
            side="sell",
            item_name="Logs",
            quantity=3,
            unit_price=90,
            item_spec=LOGS,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(updated["inventory"]["Logs"], 17)
        self.assertEqual(updated["ge_player_orders"][0]["escrow_items"], 3)
        self.assertEqual(updated["inventory"]["Coins"], 10_000)

    def test_high_or_extreme_offer_requires_explicit_confirmation(self):
        player = _player(Coins=2_000_000)
        unchanged, blocked = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=10_000,
            unit_price=100,
            item_spec=LOGS,
        )
        self.assertFalse(blocked["ok"])
        self.assertEqual(blocked["reason"], "confirmation_required")
        self.assertEqual(unchanged["inventory"]["Coins"], 2_000_000)

        accepted, result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=10_000,
            unit_price=100,
            item_spec=LOGS,
            confirmed=True,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(accepted["inventory"]["Coins"], 1_000_000)

    def test_eight_uncleared_offers_own_all_slots(self):
        player = _player()
        for _index in range(GE_SLOT_COUNT):
            player, result = place_ge_offer_pure(
                player,
                side="sell",
                item_name="Logs",
                quantity=1,
                unit_price=100,
                item_spec=LOGS,
            )
            self.assertTrue(result["ok"])
        blocked, result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=1,
            unit_price=100,
            item_spec=LOGS,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "no_offer_slot")
        self.assertEqual(len(blocked["ge_player_orders"]), GE_SLOT_COUNT)

    def test_cancel_moves_remaining_escrow_to_collection_until_collected(self):
        player, placed = place_ge_offer_pure(
            _player(),
            side="buy",
            item_name="Logs",
            quantity=5,
            unit_price=100,
            item_spec=LOGS,
        )
        order_id = placed["order"]["id"]
        cancelled, result = cancel_ge_offer_pure(player, order_id)
        self.assertTrue(result["ok"])
        self.assertEqual(cancelled["inventory"]["Coins"], 9_500)
        self.assertEqual(cancelled["ge_player_orders"][0]["collectible_coins"], 500)
        self.assertEqual(cancelled["ge_player_orders"][0]["status"], "cancelled")

        collected, result = collect_ge_offer_pure(cancelled, order_id)
        self.assertTrue(result["ok"])
        self.assertEqual(result["coins"], 500)
        self.assertEqual(collected["inventory"]["Coins"], 10_000)
        self.assertEqual(collected["ge_player_orders"], [])

    def test_collect_partial_fill_keeps_open_remainder_in_slot(self):
        player, placed = place_ge_offer_pure(
            _player(),
            side="buy",
            item_name="Logs",
            quantity=5,
            unit_price=100,
            item_spec=LOGS,
        )
        order = player["ge_player_orders"][0]
        order.update(
            {
                "remaining_quantity": 3,
                "completed_quantity": 2,
                "escrow_coins": 300,
                "collectible_coins": 20,
                "collectible_items": 2,
                "status": "partial",
            }
        )

        collected, result = collect_ge_offer_pure(player, placed["order"]["id"])
        self.assertTrue(result["ok"])
        self.assertEqual(collected["inventory"]["Coins"], 9_520)
        self.assertEqual(collected["inventory"]["Logs"], 22)
        self.assertEqual(len(collected["ge_player_orders"]), 1)
        self.assertEqual(collected["ge_player_orders"][0]["remaining_quantity"], 3)

    def test_collect_all_handles_buy_items_and_sell_coins(self):
        player, buy = place_ge_offer_pure(
            _player(),
            side="buy",
            item_name="Logs",
            quantity=2,
            unit_price=100,
            item_spec=LOGS,
        )
        player, sell = place_ge_offer_pure(
            player,
            side="sell",
            item_name="Logs",
            quantity=2,
            unit_price=100,
            item_spec=LOGS,
        )
        buy_order, sell_order = player["ge_player_orders"]
        buy_order.update(
            remaining_quantity=0,
            completed_quantity=2,
            escrow_coins=0,
            collectible_items=2,
            status="complete",
        )
        sell_order.update(
            remaining_quantity=0,
            completed_quantity=2,
            escrow_items=0,
            collectible_coins=200,
            status="complete",
        )

        collected, result = collect_all_ge_offers_pure(player)
        self.assertTrue(result["ok"])
        self.assertEqual(result["coins"], 200)
        self.assertEqual(result["items"], {"Logs": 2})
        self.assertEqual(collected["inventory"], {"Coins": 10_000, "Logs": 20})
        self.assertEqual(collected["ge_player_orders"], [])

    def test_ironman_cannot_enable_until_every_slot_is_cleared(self):
        player, _result = place_ge_offer_pure(
            _player(),
            side="sell",
            item_name="Logs",
            quantity=1,
            unit_price=100,
            item_spec=LOGS,
        )
        unchanged, blocked = set_ironman_mode_pure(player, True)
        self.assertFalse(blocked["ok"])
        self.assertFalse(unchanged["ironman_mode"])

        enabled, result = set_ironman_mode_pure(_player(), True)
        self.assertTrue(result["ok"])
        self.assertTrue(enabled["ironman_mode"])
        preview = preview_ge_offer_pure(
            enabled,
            side="buy",
            item_name="Logs",
            quantity=1,
            unit_price=100,
            item_spec=LOGS,
        )
        self.assertEqual(preview["reason"], "ironman_mode")

    def test_buy_fill_preserves_escrow_and_price_improvement(self):
        player = _player()
        player["ge_market_state"]["last_processed_tick"] = 7
        player, _result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=5,
            unit_price=110,
            item_spec=LOGS,
        )

        advanced, result = self._advance(player, market_tick=8)

        self.assertEqual(len(result["fills"]), 1)
        fill = result["fills"][0]
        self.assertEqual(fill["unit_price"], 100)
        self.assertGreater(fill["price_improvement"], 0)
        quantity = fill["quantity"]
        order = advanced["ge_player_orders"][0]
        self.assertEqual(order["completed_quantity"], quantity)
        self.assertEqual(order["escrow_coins"], 550 - 110 * quantity)
        self.assertEqual(order["collectible_items"], quantity)
        self.assertEqual(order["collectible_coins"], 10 * quantity)
        self.assertEqual(
            order["escrow_coins"] + order["collectible_coins"],
            550 - fill["unit_price"] * quantity,
        )
        self.assertGreaterEqual(
            advanced["ge_market_state"]["items"]["Logs"]["player_impact_bps"],
            25,
        )

    def test_sell_fill_moves_only_filled_escrow_and_applies_downward_impact(self):
        player = _player()
        player["ge_market_state"]["last_processed_tick"] = 7
        player, _result = place_ge_offer_pure(
            player,
            side="sell",
            item_name="Logs",
            quantity=5,
            unit_price=90,
            item_spec=LOGS,
        )

        advanced, result = self._advance(player, market_tick=8)

        fill = result["fills"][0]
        quantity = fill["quantity"]
        order = advanced["ge_player_orders"][0]
        self.assertEqual(fill["unit_price"], 100)
        self.assertEqual(order["escrow_items"], 5 - quantity)
        self.assertEqual(order["collectible_coins"], 100 * quantity)
        self.assertLessEqual(
            advanced["ge_market_state"]["items"]["Logs"]["player_impact_bps"],
            -25,
        )

    def test_buy_limit_clamps_fills_and_resets_after_four_market_hours(self):
        limited_logs = {**LOGS, "buy_limit": 2}
        player = _player()
        player["ge_market_state"]["last_processed_tick"] = 7
        player, _result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=5,
            unit_price=150,
            item_spec=limited_logs,
        )

        first, result = self._advance(
            player,
            market_tick=8,
            draws=(0.5, 0.0, 1.0, 0.0),
            item_spec=limited_logs,
        )
        self.assertEqual(result["fills"][0]["quantity"], 2)
        self.assertEqual(first["ge_buy_limit_usage"]["Logs"]["bought"], 2)

        blocked, result = self._advance(
            first,
            market_tick=9,
            draws=(0.5, 1.0, 0.5, 0.0, 0.5, 1.0),
            item_spec=limited_logs,
        )
        self.assertEqual(result["fills"], [])
        self.assertEqual(blocked["ge_player_orders"][0]["completed_quantity"], 2)

        reset_tick = 8 + GE_BUY_LIMIT_WINDOW_CARDS
        reset, result = self._advance(
            blocked,
            market_tick=reset_tick,
            draws=(0.5, 1.0, 0.5, 0.0, 1.0, 0.0),
            item_spec=limited_logs,
        )
        self.assertEqual(result["fills"][0]["quantity"], 2)
        self.assertEqual(reset["ge_buy_limit_usage"]["Logs"]["bought"], 2)
        self.assertEqual(
            reset["ge_buy_limit_usage"]["Logs"]["window_start_tick"],
            reset_tick,
        )

    def test_skipped_interval_uses_bounded_draws_and_is_deterministic(self):
        player = _player()
        player["ge_market_state"]["last_processed_tick"] = 7
        player, _result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=5,
            unit_price=80,
            item_spec=LOGS,
        )
        skipped = deepcopy(player)
        skipped["shop_market_clock"] = {
            "answered_cards": 107,
            "market_tick": 107,
        }

        first, first_result = advance_ge_market_tick_pure(
            skipped,
            item_catalog={"Logs": LOGS},
        )
        second, second_result = advance_ge_market_tick_pure(
            deepcopy(skipped),
            item_catalog={"Logs": LOGS},
        )

        self.assertEqual(first, second)
        self.assertEqual(first_result, second_result)
        self.assertLessEqual(first["ge_market_state"]["rng_cursor"], 6)
        self.assertEqual(first_result["elapsed_ticks"], 100)

    def test_new_offer_never_receives_market_ticks_from_before_creation(self):
        player = _player()
        player["shop_market_clock"] = {
            "answered_cards": 100,
            "market_tick": 100,
        }
        player["ge_market_state"]["last_processed_tick"] = 0
        player, _result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=2,
            unit_price=150,
            item_spec=LOGS,
        )

        current, result = self._advance(player, market_tick=100, draws=())
        self.assertEqual(result["fills"], [])
        self.assertEqual(current["ge_player_orders"][0]["completed_quantity"], 0)

        advanced, result = self._advance(
            current,
            market_tick=101,
            draws=(0.5, 1.0, 0.5, 0.0, 0.5, 1.0),
        )
        self.assertEqual(len(result["fills"]), 1)
        self.assertGreater(
            advanced["ge_player_orders"][0]["completed_quantity"],
            0,
        )

    def test_crossing_day_boundary_updates_guide_from_prior_trade_vwap(self):
        player = _player()
        player["shop_market_clock"] = {"answered_cards": 239, "market_tick": 239}
        player["ge_market_state"].update(
            {
                "last_processed_tick": 239,
                "items": {
                    "Logs": {
                        "anchor_price": 100,
                        "guide_price": 100,
                        "true_price": 100,
                        "last_processed_tick": 239,
                        "last_guide_update_tick": 0,
                        "item_seed": 1,
                    }
                },
            }
        )
        player["ge_trade_history"] = {
            "Logs": {
                "window_start_tick": 0,
                "quantity": 10,
                "notional": 2_000,
            }
        }
        player, _result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=1,
            unit_price=50,
            item_spec=LOGS,
        )

        advanced, result = self._advance(
            player,
            market_tick=241,
            draws=(0.5, 1.0, 0.5, 1.0),
        )

        self.assertEqual(result["fills"], [])
        item_state = advanced["ge_market_state"]["items"]["Logs"]
        self.assertEqual(item_state["guide_price"], 105)
        self.assertEqual(item_state["last_guide_update_tick"], 240)
        self.assertEqual(
            advanced["ge_trade_history"]["Logs"],
            {"window_start_tick": 240, "quantity": 0, "notional": 0},
        )

    def test_fill_on_day_boundary_is_recorded_in_the_new_trade_window(self):
        player = _player()
        player["shop_market_clock"] = {"answered_cards": 239, "market_tick": 239}
        player["ge_market_state"].update(
            {
                "last_processed_tick": 239,
                "items": {
                    "Logs": {
                        "anchor_price": 100,
                        "guide_price": 100,
                        "true_price": 100,
                        "last_processed_tick": 239,
                        "last_guide_update_tick": 0,
                        "item_seed": 1,
                    }
                },
            }
        )
        player, _result = place_ge_offer_pure(
            player,
            side="buy",
            item_name="Logs",
            quantity=2,
            unit_price=150,
            item_spec=LOGS,
        )

        advanced, result = self._advance(
            player,
            market_tick=240,
            draws=(0.5, 1.0, 0.5, 0.0, 0.5, 1.0),
        )

        quantity = result["fills"][0]["quantity"]
        self.assertEqual(
            advanced["ge_trade_history"]["Logs"],
            {
                "window_start_tick": 240,
                "quantity": quantity,
                "notional": 100 * quantity,
            },
        )


if __name__ == "__main__":
    unittest.main()
