import json
import unittest

import pkg_alias  # noqa: F401
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.shop_fixtures import build_shop_fixture_player_data
from ankiscape.logic.shop_logic import (
    advance_shop_market_clock_pure,
    apply_shop_buy_pure,
    apply_shop_sell_pure,
    rollback_shop_event_pure,
    shop_view_model_pure,
)


class TestShopRestock(unittest.TestCase):
    def setUp(self):
        self.player = build_shop_fixture_player_data()
        self.shop_id = "lumbridge_fishing_supplies"

    def buy(self, item_name, quantity=1):
        row = next(row for row in SHOP_DATA[self.shop_id]["stock"] if row["item_name"] == item_name)
        self.player, result = apply_shop_buy_pure(self.player, self.shop_id, row["id"], quantity)
        self.assertTrue(result["allowed"], result)
        self.assertEqual(result["quantity"], quantity)
        return result

    def stock(self, item_name, player=None):
        view = shop_view_model_pure(self.player if player is None else player, self.shop_id)
        return next((row["current_quantity"] for row in view["rows"] if row["item_name"] == item_name), 0)

    def advance_and_buy_bait(self, reviews):
        self.player = advance_shop_market_clock_pure(self.player, answered_cards=reviews)
        self.buy("Fishing bait")
        self.player = json.loads(json.dumps(self.player))

    def test_purchases_preserve_accumulated_restock_time(self):
        self.buy("Small fishing net", 5)
        control = advance_shop_market_clock_pure(self.player, answered_cards=50)
        self.assertEqual(self.stock("Small fishing net", control), 1)
        for expected in (0, 1, 1, 2):
            self.advance_and_buy_bait(25)
            self.assertEqual(self.stock("Small fishing net"), expected)

    def test_completed_intervals_keep_their_remainder(self):
        self.buy("Small fishing net", 5)
        self.advance_and_buy_bait(75)
        self.assertEqual(self.stock("Small fishing net"), 1)
        self.advance_and_buy_bait(25)
        self.assertEqual(self.stock("Small fishing net"), 2)

    def test_rows_with_different_intervals_restock_independently(self):
        self.shop_id = "burthorpe_guard_quartermaster"
        self.buy("Bronze sword", 20)
        self.buy("Bronze arrows", 200)
        for reviews, swords, arrows in ((5, 0, 5), (5, 1, 10), (5, 1, 15), (5, 2, 20)):
            self.player = advance_shop_market_clock_pure(self.player, answered_cards=reviews)
            self.buy("Air rune")
            self.assertEqual(self.stock("Bronze sword"), swords)
            self.assertEqual(self.stock("Bronze arrows"), arrows)

    def test_overstock_decays_despite_intervening_purchases(self):
        self.player["inventory"]["Small fishing net"] = 2
        self.player, result = apply_shop_sell_pure(self.player, self.shop_id, "Small fishing net", 2)
        self.assertTrue(result["allowed"], result)
        for expected in (7, 6, 6, 5):
            self.advance_and_buy_bait(25)
            self.assertEqual(self.stock("Small fishing net"), expected)

    def test_temporary_stock_expires_despite_intervening_purchases(self):
        self.shop_id = "lumbridge_general_store"
        self.player, result = apply_shop_sell_pure(self.player, self.shop_id, "Beer", 1)
        self.assertTrue(result["allowed"], result)
        self.assertTrue(result["temporary_stock"])
        for expected in (1, 0):
            self.player = advance_shop_market_clock_pure(self.player, answered_cards=25)
            self.buy("Empty pot")
            self.assertEqual(self.stock("Beer"), expected)

    def test_undo_preserves_the_purchased_rows_restock_progress(self):
        self.buy("Small fishing net", 2)
        self.player = advance_shop_market_clock_pure(self.player, answered_cards=25)
        bought = self.buy("Small fishing net")
        self.player, result = rollback_shop_event_pure(self.player, bought["event_id"])
        self.assertTrue(result["allowed"], result)
        self.assertEqual(self.stock("Small fishing net"), 3)
        self.advance_and_buy_bait(25)
        self.assertEqual(self.stock("Small fishing net"), 4)

    def test_full_stock_does_not_bank_time_for_later_purchases(self):
        self.buy("Small fishing net", 5)
        self.player = advance_shop_market_clock_pure(self.player, answered_cards=275)
        self.buy("Small fishing net", 5)
        self.advance_and_buy_bait(25)
        self.assertEqual(self.stock("Small fishing net"), 0)

    def test_selling_past_default_does_not_carry_shortage_time_into_decay(self):
        self.buy("Small fishing net", 2)
        self.player = advance_shop_market_clock_pure(self.player, answered_cards=40)
        self.player["inventory"]["Small fishing net"] = 3
        self.player, result = apply_shop_sell_pure(self.player, self.shop_id, "Small fishing net", 3)
        self.assertTrue(result["allowed"], result)
        self.advance_and_buy_bait(10)
        self.assertEqual(self.stock("Small fishing net"), 6)

    def test_buying_past_default_does_not_carry_decay_time_into_shortage(self):
        self.player["inventory"]["Small fishing net"] = 1
        self.player, result = apply_shop_sell_pure(self.player, self.shop_id, "Small fishing net", 1)
        self.assertTrue(result["allowed"], result)
        self.player = advance_shop_market_clock_pure(self.player, answered_cards=49)
        self.buy("Small fishing net", 6)
        self.advance_and_buy_bait(1)
        self.assertEqual(self.stock("Small fishing net"), 0)
