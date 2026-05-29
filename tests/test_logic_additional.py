import unittest

from logic_pure import (
    calculate_new_level,
    calculate_probability_with_level,
    apply_woodcutting_pure,
    apply_mining_pure,
    apply_smelt_pure,
    can_smelt_any_bar_pure,
    create_soft_clay_pure,
    has_crafting_materials_pure,
    can_mine_ore_pure,
    can_cut_tree_pure,
    can_craft_item_pure,
)
from constants import EXP_TABLE as EXP_TABLE_LIST


class TestLogicAdditional(unittest.TestCase):
    def test_calculate_new_level_with_list_exp_table_boundaries(self):
        # Using the real list EXP table from constants
        # At exactly threshold for level 2, should level from 1 -> 2
        self.assertEqual(calculate_new_level(EXP_TABLE_LIST[1], 1, EXP_TABLE_LIST), 2)
        # Just below threshold should not level
        self.assertEqual(calculate_new_level(EXP_TABLE_LIST[1] - 1, 1, EXP_TABLE_LIST), 1)
        # Multi-level jump: pick a higher exp value
        self.assertEqual(calculate_new_level(EXP_TABLE_LIST[5], 1, EXP_TABLE_LIST), 6)

    def test_probability_helpers_boundary(self):
        # When r_action == success_probability, action should fail (strict <)
        inv = {}
        tree_data = {"Oak": {"exp": 15}}
        new_inv, exp, ok = apply_woodcutting_pure("Oak", inv, tree_data, r_action=0.5, success_probability=0.5)
        self.assertFalse(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(new_inv, inv)

    def test_apply_mining_gem_equality_boundary(self):
        ore_data = {"Iron ore": {"exp": 35}}
        gem_data = {
            "Uncut sapphire": {"probability": 0.5, "exp": 50},
            "Uncut emerald": {"probability": 0.5, "exp": 67.5},
        }
        inv = {}
        # Force success, but r_gem_chance == gem_drop_chance => no gem (strict <)
        new_inv, exp, ok, gem = apply_mining_pure(
            "Iron ore",
            inv,
            ore_data,
            gem_data,
            r_action=0.0,
            success_probability=1.0,
            r_gem_chance=1.0 / 256,
            r_gem_pick=0.2,
            gem_drop_chance=1.0 / 256,
        )
        self.assertTrue(ok)
        self.assertIsNone(gem)
        self.assertEqual(new_inv.get("Iron ore"), 1)
        self.assertAlmostEqual(exp, 35)

    def test_apply_mining_success_probability_extremes(self):
        ore_data = {"Iron ore": {"exp": 35}}
        inv = {}
        # p=1.0 should succeed for r_action < 1.0
        new_inv, exp, ok, gem = apply_mining_pure(
            "Iron ore", inv, ore_data, {}, r_action=0.9999, success_probability=1.0
        )
        self.assertTrue(ok)
        self.assertEqual(new_inv.get("Iron ore"), 1)
        # p=0.0 should always fail
        new_inv2, exp2, ok2, gem2 = apply_mining_pure(
            "Iron ore", inv, ore_data, {}, r_action=0.0, success_probability=0.0
        )
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertEqual(new_inv2, inv)

    def test_can_smelt_any_bar_level_and_materials(self):
        bar_data = {
            "Bronze bar": {"level": 1, "ore_required": {"Copper ore": 1, "Tin ore": 1}},
            "Iron bar": {"level": 15, "ore_required": {"Iron ore": 1}},
        }
        # Not enough level for Iron, not enough materials for Bronze
        self.assertFalse(can_smelt_any_bar_pure({}, 1, bar_data))
        # Enough materials for Bronze and level 1 => True
        inv = {"Copper ore": 1, "Tin ore": 1}
        self.assertTrue(can_smelt_any_bar_pure(inv, 1, bar_data))
        # High level but no materials => False
        self.assertFalse(can_smelt_any_bar_pure({}, 99, bar_data))

    def test_apply_smelt_pure_unknown_bar(self):
        bar_data = {"Bronze bar": {"level": 1, "exp": 6.2, "ore_required": {"Copper ore": 1, "Tin ore": 1}}}
        inv = {"Copper ore": 1, "Tin ore": 1}
        new_inv, exp, ok = apply_smelt_pure("Unknown", inv, bar_data={})
        self.assertFalse(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(new_inv, inv)

    def test_create_soft_clay_idempotent(self):
        inv = {"Clay": 2}
        new_inv1, ok1 = create_soft_clay_pure(inv)
        self.assertTrue(ok1)
        self.assertEqual(new_inv1.get("Clay"), 1)
        self.assertEqual(new_inv1.get("Soft clay"), 1)
        # Call again on the result; should reduce to 0 Clay and increment Soft clay
        new_inv2, ok2 = create_soft_clay_pure(new_inv1)
        self.assertTrue(ok2)
        self.assertEqual(new_inv2.get("Clay"), 0)
        self.assertEqual(new_inv2.get("Soft clay"), 2)
        # Original inventory remains unchanged
        self.assertEqual(inv.get("Clay"), 2)
        self.assertIsNone(inv.get("Soft clay"))

    def test_has_crafting_materials_false_when_zero(self):
        crafting_data = {"Soft clay": {"requirements": {"Clay": 1}}}
        self.assertFalse(has_crafting_materials_pure("Soft clay", {"Clay": 0}, crafting_data))

    def test_mining_and_woodcutting_gating_unknown_items(self):
        self.assertFalse(can_mine_ore_pure(1, "Unknown", {"Copper ore": {"level": 1}}))
        self.assertFalse(can_cut_tree_pure(1, "Unknown", {"Tree": {"level": 1}}))

    def test_can_craft_item_pure_missing_item(self):
        self.assertFalse(can_craft_item_pure(99, {}, "Missing", {"Soft clay": {"level": 1, "requirements": {}}}))

    def test_calculate_new_level_caps_at_99_with_list(self):
        # Very high exp should cap at 99
        self.assertEqual(calculate_new_level(10**9, 98, EXP_TABLE_LIST), 99)
        self.assertEqual(calculate_new_level(10**9, 99, EXP_TABLE_LIST), 99)


if __name__ == "__main__":
    unittest.main()
