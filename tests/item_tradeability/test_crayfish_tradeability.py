import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import COOKING_DATA
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.logic.grand_exchange_logic import (
    advance_ge_market_tick_pure,
    collect_ge_offer_pure,
    default_ge_state_pure,
    place_ge_offer_pure,
)
from ankiscape.logic_pure.logic_pure import apply_cooking_action_pure


class CrayfishTradeabilityTest(unittest.TestCase):
    def test_cooked_crayfish_retains_custody_through_ge_round_trip(self):
        ingredients = {"Raw crayfish": 1, "Coins": 100}
        cooked, xp, processed, output, burned = apply_cooking_action_pure(
            "cook_crayfish", ingredients, COOKING_DATA, cooking_level=1, roll=0.0,
        )
        self.assertEqual((xp, processed, output, burned), (30.0, True, "Crayfish", False))
        self.assertEqual(cooked, {"Raw crayfish": 0, "Coins": 100, "Crayfish": 1})
        self.assertEqual(ingredients, {"Raw crayfish": 1, "Coins": 100})
        player = {**default_ge_state_pure(), "inventory": cooked}
        spec = GE_ITEM_CATALOG["Crayfish"]

        player, placed = place_ge_offer_pure(
            player, side="sell", item_name="Crayfish", quantity=1,
            unit_price=45, item_spec=spec,
        )
        self.assertTrue(placed["ok"])
        sell_id = placed["order"]["id"]
        self.assertEqual(placed["order"]["escrow_items"], 1)
        self.assertEqual(player["inventory"], {"Raw crayfish": 0, "Coins": 100, "Crayfish": 0})
        player["shop_market_clock"] = {"answered_cards": 1, "market_tick": 1}
        draws = iter((0.5, 0.0, 0.5, 1.0))
        player, filled = advance_ge_market_tick_pure(
            player, item_catalog=GE_ITEM_CATALOG, random_draw=lambda: next(draws),
        )
        self.assertEqual(len(filled["fills"]), 1)
        self.assertEqual(filled["fills"][0]["quantity"], 1)
        self.assertEqual(filled["fills"][0]["unit_price"], 45)
        self.assertEqual(player["ge_player_orders"][0]["escrow_items"], 0)
        self.assertEqual(player["ge_player_orders"][0]["collectible_coins"], 45)
        self.assertEqual(player["inventory"]["Coins"], 100)
        player, collected = collect_ge_offer_pure(player, sell_id)
        self.assertTrue(collected["ok"])
        self.assertEqual((collected["coins"], collected["items"]), (45, 0))
        self.assertEqual(player["inventory"]["Coins"], 145)
        self.assertEqual(player["ge_player_orders"], [])

        player, placed = place_ge_offer_pure(
            player, side="buy", item_name="Crayfish", quantity=1,
            unit_price=45, item_spec=spec,
        )
        self.assertTrue(placed["ok"])
        buy_id = placed["order"]["id"]
        self.assertEqual(placed["order"]["escrow_coins"], 45)
        self.assertEqual(player["inventory"], {"Raw crayfish": 0, "Coins": 100, "Crayfish": 0})
        player["shop_market_clock"] = {"answered_cards": 2, "market_tick": 2}
        draws = iter((0.5, 1.0, 0.5, 0.0, 0.5, 1.0))
        player, filled = advance_ge_market_tick_pure(
            player, item_catalog=GE_ITEM_CATALOG, random_draw=lambda: next(draws),
        )
        self.assertEqual(len(filled["fills"]), 1)
        self.assertEqual(filled["fills"][0]["quantity"], 1)
        self.assertEqual(filled["fills"][0]["unit_price"], 45)
        self.assertEqual(player["ge_player_orders"][0]["escrow_coins"], 0)
        self.assertEqual(player["ge_player_orders"][0]["collectible_items"], 1)
        self.assertEqual(player["inventory"]["Crayfish"], 0)
        player, collected = collect_ge_offer_pure(player, buy_id)
        self.assertTrue(collected["ok"])
        self.assertEqual((collected["coins"], collected["items"]), (0, 1))
        self.assertEqual(player["inventory"], {"Raw crayfish": 0, "Coins": 100, "Crayfish": 1})
        self.assertEqual(player["ge_player_orders"], [])
