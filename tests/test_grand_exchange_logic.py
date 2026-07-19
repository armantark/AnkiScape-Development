import unittest

from grand_exchange_logic import (
    GE_SLOT_COUNT,
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


if __name__ == "__main__":
    unittest.main()
