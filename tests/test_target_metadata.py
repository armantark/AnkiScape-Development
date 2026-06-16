import os
import unittest

from constants import (
    BIRD_NEST_OPEN_TABLES,
    DEFAULT_FIREMAKING_TARGET,
    DEFAULT_FISHING_TARGET,
    DEFAULT_MINING_TARGET,
    DEFAULT_UTILITY_ACTIVITY,
    DEFAULT_WOODCUTTING_TARGET,
    FIREMAKING_DATA,
    FIREMAKING_ITEM_IMAGES,
    FISHING_DATA,
    FISHING_ITEM_IMAGES,
    FLETCHED_ITEM_IMAGES,
    FLETCHING_DATA,
    GEM_IMAGES,
    MINING_PICKAXE_DATA,
    ORE_DATA,
    ORE_IMAGES,
    TREE_DATA,
    TREE_IMAGES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
    WOODCUTTING_AXE_DATA,
)
from target_metadata import (
    TargetRowMetadata,
    firemaking_target_rows,
    fishing_target_rows,
    fletching_target_rows,
    mining_target_rows,
    utility_activity_rows,
    woodcutting_target_rows,
)


def _row(rows, target_id):
    for row in rows:
        if row.target_id == target_id:
            return row
    raise AssertionError(f"row {target_id!r} not found")


class TargetMetadataTest(unittest.TestCase):
    def test_mining_rows_preserve_current_icon_and_deferred_note_contract(self):
        rows = mining_target_rows(
            {
                "mining_level": 33,
                "inventory": {},
                "toolbelt": {"mining": ["bronze_pickaxe"]},
                "current_ore": "coal",
            },
            ORE_DATA,
            ORE_IMAGES,
            GEM_IMAGES,
            MINING_PICKAXE_DATA,
            DEFAULT_MINING_TARGET,
            {"coal": "Concentrated coal deposits are deferred."},
        )

        coal = _row(rows, "coal")
        runite = _row(rows, "runite")

        self.assertIsInstance(coal, TargetRowMetadata)
        self.assertEqual(coal.label, "Coal (Lvl 30)")
        self.assertTrue(coal.current)
        self.assertTrue(coal.enabled)
        self.assertEqual(coal.icon_path, ORE_IMAGES["Coal"])
        self.assertIn("Best usable pickaxe: Bronze pickaxe", coal.tooltip)
        self.assertIn("Concentrated coal deposits are deferred.", coal.tooltip)
        self.assertFalse(runite.enabled)
        self.assertIn("level 85", runite.tooltip)

    def test_woodcutting_rows_preserve_xp_only_and_tool_lock_contract(self):
        rows = woodcutting_target_rows(
            {
                "woodcutting_level": 1,
                "inventory": {},
                "toolbelt": {"woodcutting": []},
                "current_tree": "ivy",
            },
            TREE_DATA,
            TREE_IMAGES,
            WOODCUTTING_AXE_DATA,
            DEFAULT_WOODCUTTING_TARGET,
        )

        tree = _row(rows, "tree")
        ivy = _row(rows, "ivy")

        self.assertFalse(tree.enabled)
        self.assertIn("no usable hatchet", tree.tooltip)
        self.assertEqual(ivy.label, "Ivy (Lvl 68) — XP only")
        self.assertTrue(ivy.current)
        self.assertIn("XP only — produces no logs.", ivy.tooltip)

    def test_fletching_rows_preserve_stable_id_material_lock_and_current_target(self):
        rows = fletching_target_rows(
            {
                "fletching_level": 99,
                "inventory": {},
                "current_fletch": "arrow_shafts",
            },
            FLETCHING_DATA,
            FLETCHED_ITEM_IMAGES,
        )

        shafts = _row(rows, "arrow_shafts")

        self.assertEqual(shafts.label, "Arrow shafts (Logs) (Lvl 1)")
        self.assertTrue(shafts.current)
        self.assertFalse(shafts.enabled)
        self.assertEqual(shafts.icon_path, FLETCHED_ITEM_IMAGES["Arrow shafts"])
        self.assertIn("Logs x1 (you have 0)", shafts.tooltip)
        self.assertIn("Locked due to: materials", shafts.tooltip)

    def test_firemaking_rows_preserve_success_tooltip_and_default_current_target(self):
        rows = firemaking_target_rows(
            {
                "firemaking_level": 45,
                "inventory": {"Logs": 2, "Oak logs": 1},
            },
            FIREMAKING_DATA,
            FIREMAKING_ITEM_IMAGES,
            DEFAULT_FIREMAKING_TARGET,
        )

        logs = _row(rows, "logs")
        oak = _row(rows, "oak_logs")

        self.assertTrue(logs.current)
        self.assertTrue(oak.enabled)
        self.assertEqual(logs.icon_path, FIREMAKING_ITEM_IMAGES["Logs"])
        self.assertIn("Base XP: 40.0 per successful burn", logs.tooltip)
        self.assertIn("Input: Logs x1 (you have 2)", logs.tooltip)
        self.assertIn("Output: Ashes x1", logs.tooltip)
        self.assertIn("Success chance:", logs.tooltip)
        self.assertNotIn("FiremakingData.kt", logs.tooltip)

    def test_fishing_rows_preserve_material_and_side_level_gates(self):
        rows = fishing_target_rows(
            {
                "fishing_level": 48,
                "strength_level": 1,
                "agility_level": 1,
                "inventory": {},
            },
            FISHING_DATA,
            FISHING_ITEM_IMAGES,
            DEFAULT_FISHING_TARGET,
        )

        sardine = _row(rows, "catch_sardine_herring")
        leaping = _row(rows, "catch_leaping_fish")

        self.assertFalse(sardine.enabled)
        self.assertIn("Materials: Fishing bait x1 (you have 0)", sardine.tooltip)
        self.assertIn("materials", sardine.tooltip)
        self.assertFalse(leaping.enabled)
        self.assertIn("side levels", leaping.tooltip)
        self.assertNotIn("rod", leaping.tooltip.lower())
        self.assertNotIn("harpoon", leaping.tooltip.lower())

    def test_utility_rows_preserve_activity_icons_no_xp_text_and_locks(self):
        rows = utility_activity_rows(
            {"inventory": {}, "current_utility": "scavenge_chicken_feathers"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )

        feathers = _row(rows, "scavenge_chicken_feathers")
        nests = _row(rows, "open_bird_nest")

        self.assertTrue(feathers.current)
        self.assertTrue(feathers.enabled)
        self.assertEqual(os.path.basename(feathers.icon_path or ""), "scavenge_chicken_feathers.png")
        self.assertIn("No Crafting XP", feathers.tooltip)
        self.assertIn("Output: Feather x1", feathers.tooltip)
        self.assertIn("No materials required", feathers.tooltip)
        self.assertFalse(nests.enabled)
        self.assertIn("No XP", nests.tooltip)
        self.assertIn("Locked: cut trees until a bird nest drops.", nests.tooltip)


if __name__ == "__main__":
    unittest.main()
