import unittest
from utils import safe_deduct_from_inventory

class TestInventoryUtils(unittest.TestCase):
    def setUp(self):
        self.player_data = {"inventory": {"Ore": 5}}

    def test_safe_deduct_success(self):
        result = safe_deduct_from_inventory("Ore", 3, self.player_data)
        self.assertTrue(result)
        self.assertEqual(self.player_data["inventory"]["Ore"], 2)

    def test_safe_deduct_failure(self):
        result = safe_deduct_from_inventory("Ore", 10, self.player_data)
        self.assertFalse(result)
        self.assertEqual(self.player_data["inventory"]["Ore"], 5)

if __name__ == "__main__":
    unittest.main()
