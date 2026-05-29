import unittest

from utils import safe_deduct_from_inventory


class TestInventoryUtilsEdgeCases(unittest.TestCase):
    def test_zero_amount_no_change_success(self):
        data = {"inventory": {"Ore": 2}}
        ok = safe_deduct_from_inventory("Ore", 0, data)
        self.assertTrue(ok)
        self.assertEqual(data["inventory"]["Ore"], 2)

    def test_exact_amount_reaches_zero(self):
        data = {"inventory": {"Ore": 2}}
        ok = safe_deduct_from_inventory("Ore", 2, data)
        self.assertTrue(ok)
        self.assertEqual(data["inventory"]["Ore"], 0)

    def test_missing_item_is_treated_as_zero(self):
        data = {"inventory": {}}
        ok = safe_deduct_from_inventory("Ore", 1, data)
        self.assertFalse(ok)
        self.assertNotIn("Ore", data["inventory"])  # unchanged

    def test_insufficient_amount_fails_and_does_not_mutate(self):
        data = {"inventory": {"Ore": 1}}
        ok = safe_deduct_from_inventory("Ore", 2, data)
        self.assertFalse(ok)
        self.assertEqual(data["inventory"]["Ore"], 1)

    def test_inventory_reference_is_mutated_in_place(self):
        inv = {"Ore": 5}
        data = {"inventory": inv}
        ok = safe_deduct_from_inventory("Ore", 3, data)
        self.assertTrue(ok)
        self.assertIs(data["inventory"], inv)
        self.assertEqual(inv["Ore"], 2)


if __name__ == "__main__":
    unittest.main()
