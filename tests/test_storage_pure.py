import unittest

from storage_pure import (
    default_player_data,
    migrate_loaded_data,
    CURRENT_CONFIG_VERSION,
)
from constants import ITEM_DEFINITIONS, ORE_DATA, TREE_DATA, BAR_DATA, GEM_DATA, CRAFTING_DATA, FLETCHING_DATA


class TestStoragePure(unittest.TestCase):
    def test_default_player_data_has_expected_keys(self):
        data = default_player_data(ORE_DATA)
        # Core keys
        for key in [
            "config_version",
            "mining_level",
            "woodcutting_level",
            "smithing_level",
            "crafting_level",
            "fletching_level",
            "mining_exp",
            "woodcutting_exp",
            "smithing_exp",
            "crafting_exp",
            "fletching_exp",
            "current_craft",
            "current_fletch",
            "current_ore",
            "current_tree",
            "current_bar",
            "inventory",
            "progress_to_next",
            "completed_achievements",
        ]:
            self.assertIn(key, data)
        # Inventory seeded with ore keys
        for ore in ORE_DATA:
            self.assertIn(ore, data["inventory"])  # zero by default
        self.assertEqual(data["config_version"], CURRENT_CONFIG_VERSION)

    def test_default_player_data_can_seed_registered_items(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        fletching_outputs = [spec["output_item"] for spec in FLETCHING_DATA.values()]
        for item_name in list(ORE_DATA) + list(TREE_DATA) + list(BAR_DATA) + list(GEM_DATA) + list(CRAFTING_DATA) + fletching_outputs:
            self.assertIn(item_name, data["inventory"])
            self.assertEqual(data["inventory"][item_name], 0)

    def test_migrate_from_old_schema_total_exp(self):
        old = {
            "total_exp": 123,
            "inventory": {"Copper ore": 2},
            # missing many keys on purpose
        }
        migrated = migrate_loaded_data(old, ORE_DATA)
        # total_exp -> mining_exp, and other exp fields defaulted
        self.assertEqual(migrated["mining_exp"], 123)
        self.assertIn("woodcutting_exp", migrated)
        self.assertIn("smithing_exp", migrated)
        self.assertIn("crafting_exp", migrated)
        # Ensure smithing/crafting defaults
        self.assertEqual(migrated["smithing_level"], 1)
        self.assertEqual(migrated["crafting_level"], 1)
        self.assertEqual(migrated["current_bar"], "Bronze bar")
        self.assertEqual(migrated["current_craft"], "")
        # Inventory preserved and completed with ore keys
        self.assertEqual(migrated["inventory"]["Copper ore"], 2)
        for ore in ORE_DATA:
            self.assertIn(ore, migrated["inventory"])  # completed
        # Version bumped
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)

    def test_migrate_can_seed_registered_items_without_losing_custom_entries(self):
        migrated = migrate_loaded_data(
            {"inventory": {"Mystery item": 7, "Oak": 3}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["inventory"]["Mystery item"], 7)
        self.assertEqual(migrated["inventory"]["Oak"], 3)
        self.assertIn("Bronze bar", migrated["inventory"])
        self.assertIn("Uncut sapphire", migrated["inventory"])
        self.assertIn("Arrow shafts", migrated["inventory"])

    def test_migrate_idempotent(self):
        base = {"mining_exp": 10, "inventory": {}}
        first = migrate_loaded_data(base, ORE_DATA)
        second = migrate_loaded_data(first, ORE_DATA)
        self.assertEqual(first, second)

    def test_migrate_handles_bad_inventory(self):
        base = {"mining_exp": 10, "inventory": 5}  # not a dict
        migrated = migrate_loaded_data(base, ORE_DATA)
        self.assertIsInstance(migrated["inventory"], dict)
        for ore in ORE_DATA:
            self.assertIn(ore, migrated["inventory"])  # seeded


if __name__ == "__main__":
    unittest.main()
