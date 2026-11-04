import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic.shop_fixtures import build_shop_fixture_player_data
from ankiscape.logic.shop_logic import (
    apply_shop_vendor_action_pure,
    preview_shop_vendor_action_pure,
)


class TestVendorActions(unittest.TestCase):
    def test_vendor_actions_are_one_per_interaction(self):
        # Dialogue parity: Karim hands over exactly one kebab per
        # conversation; requested bulk quantities clamp to a single use.
        data = build_shop_fixture_player_data()
        preview = preview_shop_vendor_action_pure(data, "karim_buy_kebab", 50)
        self.assertTrue(preview["allowed"])
        self.assertEqual(preview["quantity"], 1)
        updated, result = apply_shop_vendor_action_pure(data, "karim_buy_kebab", 50)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["quantity"], 1)
        self.assertEqual(updated["inventory"].get("Kebab", 0), data["inventory"].get("Kebab", 0) + 1)
        self.assertEqual(updated["inventory"]["Coins"], data["inventory"]["Coins"] - 1)

    def test_wyson_offers_spend_exact_coins_for_one_purchase(self):
        for action_id, price, leaves in (
            ("wyson_buy_two_woad_leaves", 20, 2),
            ("wyson_buy_one_woad_leaf", 15, 1),
        ):
            for coins in (price, 100):
                with self.subTest(action=action_id, coins=coins):
                    data = build_shop_fixture_player_data()
                    data["inventory"].update({"Coins": coins, "Woad leaf": 3})
                    preview = preview_shop_vendor_action_pure(data, action_id, 50)
                    self.assertTrue(preview["allowed"], preview)
                    self.assertEqual(preview["quantity"], 1)
                    updated, result = apply_shop_vendor_action_pure(data, action_id, 50)
                    self.assertTrue(result["allowed"], result)
                    self.assertEqual(result["quantity"], 1)
                    self.assertEqual(updated["inventory"], {
                        **data["inventory"], "Coins": coins - price, "Woad leaf": 3 + leaves,
                    })

    def test_wyson_refuses_without_enough_coins(self):
        for action_id, price in (
            ("wyson_buy_two_woad_leaves", 20),
            ("wyson_buy_one_woad_leaf", 15),
        ):
            for coins in (0, price - 1):
                with self.subTest(action=action_id, coins=coins):
                    data = build_shop_fixture_player_data()
                    data["inventory"].update({"Coins": coins, "Woad leaf": 3})
                    preview = preview_shop_vendor_action_pure(data, action_id)
                    self.assertFalse(preview["allowed"])
                    self.assertEqual(preview["reason"], "missing_requirements")
                    [missing] = preview["missing_requirements"]
                    self.assertEqual(
                        (missing["item_name"], missing["owned_quantity"], missing["shortfall"]),
                        ("Coins", coins, price - coins),
                    )
                    updated, result = apply_shop_vendor_action_pure(data, action_id)
                    self.assertFalse(result["allowed"])
                    self.assertEqual(result["reason"], "missing_requirements")
                    self.assertEqual(updated, data)
