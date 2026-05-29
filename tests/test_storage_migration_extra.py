import unittest

from storage_pure import migrate_loaded_data, default_player_data, CURRENT_CONFIG_VERSION
from constants import ORE_DATA


class TestStorageMigrationExtra(unittest.TestCase):
    def test_inventory_none_becomes_dict(self):
        data = {"inventory": None}
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertIsInstance(out["inventory"], dict)
        for ore in ORE_DATA:
            self.assertIn(ore, out["inventory"])  # seeded

    def test_missing_inventory_key(self):
        data = {}
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertIsInstance(out["inventory"], dict)
        for ore in ORE_DATA:
            self.assertIn(ore, out["inventory"])  # seeded

    def test_total_exp_preserved_when_mining_exp_present(self):
        # Current behavior: if mining_exp exists, total_exp is not migrated/popped
        data = {"total_exp": 123, "mining_exp": 999}
        out = migrate_loaded_data(data, ORE_DATA)
        self.assertEqual(out["mining_exp"], 999)
        self.assertIn("total_exp", out)

    def test_default_player_data_sets_current_defaults(self):
        base = default_player_data(ORE_DATA)
        self.assertEqual(base["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(base["current_bar"], "Bronze bar")
        self.assertEqual(base["current_ore"], "Rune essence")
        self.assertEqual(base["current_tree"], "Tree")
        self.assertEqual(base["current_craft"], "")


if __name__ == "__main__":
    unittest.main()
