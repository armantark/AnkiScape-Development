import unittest

from shop_data import SHOP_DATA
from shop_fixtures import build_shop_fixture_player_data, build_shop_frontend_fixtures
from shop_logic import (
    advance_shop_market_clock_pure,
    apply_shop_buy_pure,
    apply_shop_sell_pure,
    apply_shop_service_pure,
    apply_shop_transaction_pure,
    apply_shop_vendor_action_pure,
    default_shop_state_pure,
    preview_shop_buy_pure,
    preview_shop_sell_pure,
    preview_shop_service_pure,
    preview_shop_vendor_action_pure,
    rollback_shop_event_pure,
    sanitize_shop_state_pure,
    search_shop_catalog_pure,
    shop_history_rows_pure,
    shop_view_model_pure,
)


def _live_shop_and_row():
    for shop in SHOP_DATA.values():
        for row in shop["stock"]:
            if shop["visibility"] == "visible" and row["disposition"] == "live":
                return shop, row
    raise AssertionError("no live stock row")


def _locked_shop_and_row():
    for shop in SHOP_DATA.values():
        for row in shop["stock"]:
            if row["visibility"] == "visible_locked":
                return shop, row
    raise AssertionError("no locked stock row")


def _general_store():
    for shop in SHOP_DATA.values():
        if shop["visibility"] == "visible" and shop["general_store"]:
            return shop
    raise AssertionError("no visible general store")


def _specialist_without_beer():
    for shop in SHOP_DATA.values():
        if shop["visibility"] == "visible" and not shop["general_store"] and all(row["item_name"] != "Beer" for row in shop["stock"]):
            return shop
    raise AssertionError("no visible specialist shop without beer")


class TestShopLogic(unittest.TestCase):
    def test_default_and_sanitize_shop_state(self):
        default_state = default_shop_state_pure()
        self.assertEqual(default_state["shop_data_version"], 1)
        self.assertEqual(default_state["shop_market_clock"]["market_tick"], 0)

        sanitized = sanitize_shop_state_pure(
            {
                "shop_market_clock": {"answered_cards": "4", "market_tick": "7"},
                "shop_stock_state": {"bad": {"rows": {"row": {"current_quantity": "-10"}}}},
                "shop_events": [{"event_id": "shop_evt_1"}],
                "shop_next_event_id": "3",
            }
        )
        self.assertEqual(sanitized["shop_market_clock"]["answered_cards"], 4)
        self.assertEqual(sanitized["shop_market_clock"]["market_tick"], 7)
        self.assertEqual(sanitized["shop_next_event_id"], 3)

    def test_market_clock_advances_on_answered_cards(self):
        data = build_shop_fixture_player_data()
        advanced = advance_shop_market_clock_pure(data, answered_cards=10)
        self.assertEqual(advanced["shop_market_clock"]["answered_cards"], 10)
        self.assertEqual(advanced["shop_market_clock"]["market_tick"], 10)
        self.assertEqual(data["shop_market_clock"]["market_tick"], 0)

    def test_buy_live_stock_records_event_and_rollback_restores_state(self):
        shop, row = _live_shop_and_row()
        data = build_shop_fixture_player_data()
        before_stock = row["default_quantity"]

        updated, result = apply_shop_buy_pure(data, shop["id"], row["id"], 2)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["quantity"], min(2, before_stock))
        self.assertEqual(updated["inventory"][row["item_name"]], data["inventory"].get(row["item_name"], 0) + result["quantity"])
        self.assertEqual(updated["inventory"]["Coins"], data["inventory"]["Coins"] - result["total_price"])
        view = shop_view_model_pure(updated, shop["id"])
        bought_row = next(view_row for view_row in view["rows"] if view_row["id"] == row["id"])
        self.assertEqual(bought_row["current_quantity"], before_stock - result["quantity"])

        rolled_back, rollback_result = rollback_shop_event_pure(updated, result["event_id"])
        self.assertTrue(rollback_result["allowed"])
        self.assertEqual(rolled_back["inventory"]["Coins"], data["inventory"]["Coins"])
        self.assertEqual(rolled_back["inventory"].get(row["item_name"], 0), data["inventory"].get(row["item_name"], 0))
        rolled_back_view = shop_view_model_pure(rolled_back, shop["id"])
        restored_row = next(view_row for view_row in rolled_back_view["rows"] if view_row["id"] == row["id"])
        self.assertEqual(restored_row["current_quantity"], before_stock)

    def test_locked_stock_fails_closed(self):
        shop, row = _locked_shop_and_row()
        data = build_shop_fixture_player_data()
        preview = preview_shop_buy_pure(data, shop["id"], row["id"], 1)
        self.assertFalse(preview["allowed"])
        self.assertEqual(preview["reason"], "currency_not_implemented")

    def test_previews_include_current_player_state_counts(self):
        shop, row = _live_shop_and_row()
        data = build_shop_fixture_player_data()
        data["inventory"]["Coins"] = 0

        buy_preview = preview_shop_buy_pure(data, shop["id"], row["id"], 1)
        self.assertFalse(buy_preview["allowed"])
        self.assertEqual(buy_preview["reason"], "insufficient_currency")
        self.assertEqual(buy_preview["currency_owned"], 0)
        self.assertEqual(buy_preview["required_currency"], row["buy_price"])
        self.assertEqual(buy_preview["currency_item_name"], "Coins")

        sell_shop = _general_store()
        sell_preview = preview_shop_sell_pure(data, sell_shop["id"], "Beer", 1)
        self.assertTrue(sell_preview["allowed"])
        self.assertEqual(sell_preview["owned_quantity"], data["inventory"]["Beer"])

        data["inventory"]["Beer glass"] = 0
        vendor_preview = preview_shop_vendor_action_pure(data, "bartender_sell_beer_glass", 1)
        self.assertFalse(vendor_preview["allowed"])
        self.assertEqual(vendor_preview["reason"], "missing_requirements")
        self.assertIn(
            {"item_name": "Beer glass", "required_quantity": 1, "owned_quantity": 0, "shortfall": 1, "kind": "item"},
            vendor_preview["missing_requirements"],
        )

    def test_restock_uses_market_tick_for_touched_shop(self):
        shop, row = _live_shop_and_row()
        data = build_shop_fixture_player_data()
        updated, result = apply_shop_buy_pure(data, shop["id"], row["id"], 2)
        self.assertTrue(result["allowed"])
        advanced = advance_shop_market_clock_pure(updated, answered_cards=row["restock_ticks"])
        view = shop_view_model_pure(advanced, shop["id"])
        restocked_row = next(view_row for view_row in view["rows"] if view_row["id"] == row["id"])
        self.assertGreaterEqual(restocked_row["current_quantity"], row["default_quantity"] - result["quantity"] + 1)

    def test_general_store_accepts_tradeable_player_sold_temp_stock(self):
        shop = _general_store()
        data = build_shop_fixture_player_data()
        updated, result = apply_shop_sell_pure(data, shop["id"], "Beer", 1)
        self.assertTrue(result["allowed"])
        self.assertTrue(result["temporary_stock"])
        self.assertEqual(updated["inventory"]["Beer"], data["inventory"]["Beer"] - 1)
        self.assertEqual(updated["inventory"]["Coins"], data["inventory"]["Coins"] + result["total_price"])
        view = shop_view_model_pure(updated, shop["id"])
        self.assertTrue(any(row["item_name"] == "Beer" and row["current_quantity"] == 1 for row in view["rows"]))

    def test_specialist_shop_rejects_non_stock_sells(self):
        shop = _specialist_without_beer()
        data = build_shop_fixture_player_data()
        preview = preview_shop_sell_pure(data, shop["id"], "Beer", 1)
        self.assertFalse(preview["allowed"])
        self.assertEqual(preview["reason"], "specialist_shop_stock_only")

    def test_services_vendor_actions_and_generic_transaction_wrapper(self):
        # Processing conversions (tanning, sawmill) are review-paced
        # Utility/Activities now, not instant shop services; the service APIs
        # stay as a fail-closed contract slot for future instant services.
        data = build_shop_fixture_player_data()
        service_preview = preview_shop_service_pure(data, "al_kharid_tanner_soft_leather", 1)
        self.assertFalse(service_preview["allowed"])
        self.assertEqual(service_preview["reason"], "unknown_service")

        after_news, news_result = apply_shop_vendor_action_pure(data, "benny_buy_varrock_herald", 1)
        self.assertTrue(news_result["allowed"])
        self.assertEqual(after_news["inventory"]["Newspaper"], 1)

        after_beer, beer_result = apply_shop_transaction_pure(after_news, "vendor_action", action_id="bartender_buy_beer", quantity=1)
        self.assertTrue(beer_result["allowed"])
        self.assertEqual(after_beer["inventory"]["Beer"], after_news["inventory"]["Beer"] + 1)

    def test_search_history_and_fixture_bundle(self):
        data = build_shop_fixture_player_data()
        search = search_shop_catalog_pure(data, "Feather", include_locked=True, limit=10)
        self.assertGreaterEqual(len(search["results"]), 1)
        fixtures = build_shop_frontend_fixtures()
        for key in (
            "normal_coin_stock_shop",
            "feather_multi_shop_search",
            "locked_read_only_shop",
            "player_sold_stock",
            "vendor_action_transaction",
            "history",
        ):
            self.assertIn(key, fixtures)
        self.assertTrue(fixtures["player_sold_stock"]["result"]["allowed"])
        self.assertGreaterEqual(len(fixtures["history"]), 3)

        shop, row = _live_shop_and_row()
        updated, result = apply_shop_buy_pure(data, shop["id"], row["id"], 1)
        self.assertTrue(result["allowed"])
        history = shop_history_rows_pure(updated, shop["id"])
        self.assertEqual(history[0]["type"], "buy")

    def test_primary_skill_outputs_sell_at_general_stores(self):
        # Coin-loop guarantee: representative gathered/crafted/combat outputs
        # must resolve a Shop.java sell price even when no shop stocks them
        # (SHOP_PLAYER_SELL_PRICES fallback), so income is never fail-closed.
        outputs = (
            "Logs", "Oak logs", "Willow logs", "Maple logs", "Yew logs",
            "Iron ore", "Coal", "Gold ore", "Mithril ore",
            "Bronze bar", "Iron bar", "Steel bar", "Silver bar",
            "Raw shrimps", "Raw trout", "Raw lobster", "Raw swordfish",
            "Uncut sapphire", "Uncut emerald", "Uncut ruby",
            "Bones", "Big bones", "Cowhide", "Leather", "Hard leather",
            "Wool", "Ball of wool", "Flax", "Bow string",
            "Grey wolf fur", "Feather", "Arrow shaft", "Sapphire ring",
        )
        general = _general_store()
        data = build_shop_fixture_player_data()
        for item_name in outputs:
            data["inventory"][item_name] = 5
            preview = preview_shop_sell_pure(data, general["id"], item_name, 1)
            self.assertTrue(preview["allowed"], f"{item_name}: {preview.get('reason')}")
            self.assertGreaterEqual(int(preview["unit_price"]), 1, item_name)

    def test_gather_sell_buy_coin_loop_end_to_end(self):
        # A coinless player sells gathered goods to a general store, then
        # spends the proceeds on shop stock; both legs record history events.
        general = _general_store()
        feather_shop = next(
            shop for shop in SHOP_DATA.values()
            if shop["visibility"] == "visible"
            and any(r["item_name"] == "Feather" and r["disposition"] == "live" for r in shop["stock"])
        )
        feather_row = next(r for r in feather_shop["stock"] if r["item_name"] == "Feather")

        data = build_shop_fixture_player_data()
        data["inventory"]["Coins"] = 0
        data["inventory"]["Oak logs"] = 20

        sell_preview = preview_shop_sell_pure(data, general["id"], "Oak logs", 20)
        self.assertTrue(sell_preview["allowed"], sell_preview.get("reason"))
        data, sell_result = apply_shop_sell_pure(data, general["id"], "Oak logs", 20)
        self.assertTrue(sell_result["allowed"])
        earned = int(sell_result["total_price"])
        self.assertGreater(earned, 0)
        self.assertEqual(data["inventory"]["Coins"], earned)
        self.assertEqual(data["inventory"]["Oak logs"], 0)

        unit = int(feather_row["buy_price"])
        affordable = max(1, min(5, earned // unit))
        data, buy_result = apply_shop_buy_pure(data, feather_shop["id"], feather_row["id"], affordable)
        self.assertTrue(buy_result["allowed"], buy_result.get("reason"))
        self.assertEqual(data["inventory"].get("Feather", 0), int(buy_result["quantity"]))
        self.assertEqual(
            data["inventory"]["Coins"],
            earned - int(buy_result["total_price"]),
        )
        types = [event["type"] for event in shop_history_rows_pure(data, limit=4)]
        self.assertIn("sell", types)
        self.assertIn("buy", types)


if __name__ == "__main__":
    unittest.main()
