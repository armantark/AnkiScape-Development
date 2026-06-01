import unittest

from storage_pure import (
    default_player_data,
    migrate_loaded_data,
    CURRENT_CONFIG_VERSION,
)
from constants import ITEM_DEFINITIONS, ORE_DATA, TREE_DATA, BAR_DATA, GEM_DATA, CRAFTING_DATA, FLETCHING_DATA, UTILITY_ACTIVITY_DATA, WOODCUTTING_LOG_ITEMS


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
            "current_utility",
            "current_ore",
            "current_tree",
            "current_bar",
            "inventory",
            "progress_to_next",
            "completed_achievements",
            "toolbelt",
        ]:
            self.assertIn(key, data)
        # Inventory seeded with ore keys
        for ore in ORE_DATA:
            self.assertIn(ore, data["inventory"])  # zero by default
        self.assertEqual(data["config_version"], CURRENT_CONFIG_VERSION)

    def test_default_player_data_can_seed_registered_items(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        fletching_outputs = [spec["output_item"] for spec in FLETCHING_DATA.values()]
        fletching_materials = [
            material
            for spec in FLETCHING_DATA.values()
            for material in spec.get("requirements", {})
            if material not in WOODCUTTING_LOG_ITEMS
        ]
        utility_outputs = [spec["output_item"] for spec in UTILITY_ACTIVITY_DATA.values() if "output_item" in spec]
        for item_name in (
            list(ORE_DATA)
            + list(WOODCUTTING_LOG_ITEMS)
            + list(BAR_DATA)
            + list(GEM_DATA)
            + list(CRAFTING_DATA)
            + fletching_outputs
            + fletching_materials
            + utility_outputs
        ):
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
        self.assertEqual(migrated["current_utility"], "make_soft_clay")
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
        self.assertNotIn("Oak", migrated["inventory"])
        self.assertEqual(migrated["inventory"]["Oak logs"], 3)
        self.assertIn("Bronze bar", migrated["inventory"])
        self.assertIn("Uncut sapphire", migrated["inventory"])
        self.assertIn("Arrow shafts", migrated["inventory"])
        self.assertIn("Feather", migrated["inventory"])
        self.assertIn("Soft clay", migrated["inventory"])
        self.assertIn("Wool", migrated["inventory"])
        self.assertIn("Flax", migrated["inventory"])
        self.assertIn("bronze_hatchet", migrated["toolbelt"]["woodcutting"])

    def test_migrate_legacy_woodcutting_target_and_logs(self):
        migrated = migrate_loaded_data(
            {
                "current_tree": "Magic",
                "inventory": {"Tree": 2, "Magic": 4, "Redwood": 99, "Mystery item": 1},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["current_tree"], "magic")
        self.assertEqual(migrated["inventory"]["Logs"], 2)
        self.assertEqual(migrated["inventory"]["Magic logs"], 4)
        self.assertNotIn("Tree", migrated["inventory"])
        self.assertNotIn("Magic", migrated["inventory"])
        self.assertNotIn("Redwood", migrated["inventory"])
        self.assertEqual(migrated["inventory"]["Mystery item"], 1)

    def test_migrate_moves_legacy_soft_clay_target_to_utility(self):
        migrated = migrate_loaded_data(
            {"current_craft": "Soft clay", "inventory": {"Clay": 4}},
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["current_craft"], "")
        self.assertEqual(migrated["current_utility"], "make_soft_clay")
        self.assertEqual(migrated["inventory"]["Clay"], 4)

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
