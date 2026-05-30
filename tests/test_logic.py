import unittest
from logic_pure import (
    get_exp_to_next_level,
    calculate_new_level,
    get_newly_completed_achievements,
    calculate_probability_with_level,
    pick_gem,
    can_smelt_any_bar_pure,
    create_soft_clay_pure,
    has_crafting_materials_pure,
    apply_crafting_pure,
    apply_utility_activity_pure,
    apply_fletching_pure,
    apply_smelt_pure,
    apply_woodcutting_pure,
    apply_mining_pure,
    can_mine_ore_pure,
    can_cut_tree_pure,
    can_craft_item_pure,
    can_fletch_item_pure,
    can_perform_utility_activity_pure,
    sanitize_xp_multiplier,
    scale_skill_exp_pure,
)

class TestLogic(unittest.TestCase):
    def test_get_exp_to_next_level(self):
        player_data = {"mining_level": 10, "total_exp": 1000}
        EXP_TABLE = {10: 1500}
        result = get_exp_to_next_level(player_data, EXP_TABLE)
        self.assertEqual(result, 500)

    def test_max_level(self):
        player_data = {"mining_level": 99, "total_exp": 200000}
        EXP_TABLE = {99: 200000}
        result = get_exp_to_next_level(player_data, EXP_TABLE)
        self.assertEqual(result, 0)

    def test_get_newly_completed_achievements_basic(self):
        # Mock achievements and player data
        achievements = {
            "A": {"condition": lambda p: p["score"] >= 10},
            "B": {"condition": lambda p: p["score"] >= 20},
            "C": {"condition": lambda p: p["score"] >= 30},
        }
        player_data = {"score": 25, "completed_achievements": ["A"]}
        result = get_newly_completed_achievements(player_data, achievements)
        self.assertIn("B", result)
        self.assertNotIn("A", result)
        self.assertNotIn("C", result)

    def test_get_newly_completed_achievements_none(self):
        achievements = {
            "A": {"condition": lambda p: p["score"] >= 10},
            "B": {"condition": lambda p: p["score"] >= 20},
        }
        player_data = {"score": 5, "completed_achievements": []}
        result = get_newly_completed_achievements(player_data, achievements)
        self.assertEqual(result, [])

    def test_get_newly_completed_achievements_all(self):
        achievements = {
            "A": {"condition": lambda p: True},
            "B": {"condition": lambda p: True},
        }
        player_data = {"score": 100, "completed_achievements": []}
        result = get_newly_completed_achievements(player_data, achievements)
        self.assertCountEqual(result, ["A", "B"])

    def test_calculate_new_level_basic(self):
        EXP_TABLE = {1: 0, 2: 100, 3: 300, 4: 600, 5: 1000}
        self.assertEqual(calculate_new_level(50, 1, EXP_TABLE), 1)
        self.assertEqual(calculate_new_level(150, 1, EXP_TABLE), 2)
        self.assertEqual(calculate_new_level(350, 2, EXP_TABLE), 3)

    def test_calculate_new_level_multiple_level_up(self):
        EXP_TABLE = {1: 0, 2: 100, 3: 300, 4: 600, 5: 1000}
        self.assertEqual(calculate_new_level(1200, 1, EXP_TABLE), 5)

    def test_calculate_new_level_max_level(self):
        EXP_TABLE = {98: 10000, 99: 20000}
        self.assertEqual(calculate_new_level(25000, 98, EXP_TABLE), 99)
        self.assertEqual(calculate_new_level(25000, 99, EXP_TABLE), 99)

    def test_calculate_probability_with_level(self):
        # Low level, no cap hit
        prob = calculate_probability_with_level(
            player_level=0,
            base_probability=0.8,
            level_bonus_factor=0.02,
            source_probability=0.5,
            cap=0.95,
        )
        self.assertAlmostEqual(prob, 0.4)

        # Higher level, cap applies: (0.8 + 10*0.02)=1.0 -> capped to 0.95; 0.95*0.5=0.475
        prob = calculate_probability_with_level(
            player_level=10,
            base_probability=0.8,
            level_bonus_factor=0.02,
            source_probability=0.5,
            cap=0.95,
        )
        self.assertAlmostEqual(prob, 0.475)

    def test_pick_gem(self):
        gem_data = {
            "Sapphire": {"probability": 0.5},
            "Emerald": {"probability": 0.3},
            "Ruby": {"probability": 0.2},
        }
        self.assertEqual(pick_gem(gem_data, 0.2), "Sapphire")
        self.assertEqual(pick_gem(gem_data, 0.6), "Emerald")
        self.assertEqual(pick_gem(gem_data, 0.85), "Ruby")
        # When r exceeds total probability mass (1.0 exactly picks last), use 0.99 -> Ruby, 1.1 -> None
        self.assertEqual(pick_gem(gem_data, 0.99), "Ruby")
        partial = {
            "Sapphire": {"probability": 0.4},
            "Emerald": {"probability": 0.4},
        }
        self.assertIsNone(pick_gem(partial, 0.9))

    def test_can_smelt_any_bar_pure(self):
        bar_data = {
            "Bronze bar": {"level": 1, "ore_required": {"Copper ore": 1, "Tin ore": 1}},
            "Iron bar": {"level": 15, "ore_required": {"Iron ore": 1}},
        }
        inv = {"Copper ore": 1, "Tin ore": 1}
        self.assertTrue(can_smelt_any_bar_pure(inv, 1, bar_data))
        self.assertFalse(can_smelt_any_bar_pure({}, 99, bar_data))
        self.assertFalse(can_smelt_any_bar_pure({"Copper ore": 1}, 99, bar_data))

    def test_create_soft_clay_pure(self):
        inv = {"Clay": 2}
        new_inv, ok = create_soft_clay_pure(inv)
        self.assertTrue(ok)
        self.assertEqual(new_inv["Clay"], 1)
        self.assertEqual(new_inv.get("Soft clay"), 1)
        # Original inventory not mutated
        self.assertEqual(inv["Clay"], 2)
        # Failure path
        new_inv2, ok2 = create_soft_clay_pure({})
        self.assertFalse(ok2)
        self.assertEqual(new_inv2, {})

    def test_apply_utility_activity_batches_without_xp(self):
        utility_data = {
            "make_soft_clay": {
                "requirements": {"Clay": 1},
                "output_item": "Soft clay",
                "output_qty": 1,
                "batch_size": 28,
            }
        }
        inv = {"Clay": 3}
        self.assertTrue(can_perform_utility_activity_pure(inv, "make_soft_clay", utility_data))

        new_inv, exp, ok, processed = apply_utility_activity_pure("make_soft_clay", inv, utility_data)

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 3)
        self.assertEqual(new_inv["Clay"], 0)
        self.assertEqual(new_inv["Soft clay"], 3)
        self.assertEqual(inv["Clay"], 3)

    def test_apply_utility_activity_caps_at_batch_size(self):
        utility_data = {
            "make_soft_clay": {
                "requirements": {"Clay": 1},
                "output_item": "Soft clay",
                "output_qty": 1,
                "batch_size": 28,
            }
        }
        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "make_soft_clay",
            {"Clay": 40},
            utility_data,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 28)
        self.assertEqual(new_inv["Clay"], 12)
        self.assertEqual(new_inv["Soft clay"], 28)

    def test_apply_utility_activity_can_generate_batch_without_inputs(self):
        utility_data = {
            "gather_wool": {
                "requirements": {},
                "output_item": "Wool",
                "output_qty": 1,
                "batch_size": 28,
            }
        }
        new_inv, exp, ok, processed = apply_utility_activity_pure("gather_wool", {}, utility_data)

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 28)
        self.assertEqual(new_inv["Wool"], 28)

    def test_has_crafting_materials_and_apply(self):
        crafting_data = {
            "Soft clay": {"level": 1, "exp": 0, "requirements": {"Clay": 1}},
            "Gold ring": {"level": 5, "exp": 15, "requirements": {"Gold bar": 1}},
        }
        inv = {"Clay": 1, "Gold bar": 1}
        self.assertTrue(has_crafting_materials_pure("Soft clay", inv, crafting_data))
        self.assertTrue(has_crafting_materials_pure("Gold ring", inv, crafting_data))

        new_inv, exp, ok = apply_crafting_pure("Soft clay", inv, crafting_data)
        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(new_inv.get("Soft clay"), 1)
        self.assertEqual(new_inv.get("Clay"), 0)

        new_inv2, exp2, ok2 = apply_crafting_pure("Gold ring", inv, crafting_data)
        self.assertTrue(ok2)
        self.assertEqual(exp2, 15)
        self.assertEqual(new_inv2.get("Gold ring"), 1)
        self.assertEqual(new_inv2.get("Gold bar"), 0)

    def test_apply_crafting_pure_batches_station_actions(self):
        crafting_data = {
            "Bow string": {
                "level": 10,
                "exp": 15,
                "requirements": {"Flax": 1},
                "batch_size": 28,
            }
        }
        inv = {"Flax": 30}

        new_inv, exp, ok = apply_crafting_pure("Bow string", inv, crafting_data)

        self.assertTrue(ok)
        self.assertEqual(exp, 420)
        self.assertEqual(new_inv["Flax"], 2)
        self.assertEqual(new_inv["Bow string"], 28)
        self.assertEqual(inv["Flax"], 30)

    def test_apply_crafting_pure_respects_output_quantity(self):
        crafting_data = {
            "Silver bolts (unf)": {
                "level": 21,
                "exp": 50,
                "requirements": {"Silver bar": 1},
                "output_qty": 10,
            }
        }

        new_inv, exp, ok = apply_crafting_pure("Silver bolts (unf)", {"Silver bar": 1}, crafting_data)

        self.assertTrue(ok)
        self.assertEqual(exp, 50)
        self.assertEqual(new_inv["Silver bar"], 0)
        self.assertEqual(new_inv["Silver bolts (unf)"], 10)

    def test_xp_multiplier_validation_and_scaling(self):
        self.assertEqual(sanitize_xp_multiplier("2.5"), 2.5)
        self.assertEqual(sanitize_xp_multiplier("bad"), 1.0)
        self.assertEqual(sanitize_xp_multiplier(True), 1.0)
        self.assertEqual(sanitize_xp_multiplier(-5), 0.0)
        self.assertEqual(sanitize_xp_multiplier(500), 100.0)
        self.assertEqual(scale_skill_exp_pure(6.3, 2), 12.6)

    def test_apply_smelt_pure(self):
        bar_data = {
            "Bronze bar": {"level": 1, "exp": 6.2, "ore_required": {"Copper ore": 1, "Tin ore": 1}},
            "Iron bar": {"level": 15, "exp": 12.5, "ore_required": {"Iron ore": 1}},
        }
        inv = {"Copper ore": 1, "Tin ore": 1}
        new_inv, exp, ok = apply_smelt_pure("Bronze bar", inv, bar_data)
        self.assertTrue(ok)
        self.assertAlmostEqual(exp, 6.2)
        self.assertEqual(new_inv.get("Bronze bar"), 1)
        self.assertEqual(new_inv.get("Copper ore"), 0)
        self.assertEqual(new_inv.get("Tin ore"), 0)

        # Failure when missing materials
        inv2 = {"Copper ore": 1}
        new_inv2, exp2, ok2 = apply_smelt_pure("Bronze bar", inv2, bar_data)
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertEqual(new_inv2, inv2)

    def test_apply_woodcutting_pure(self):
        tree_data = {"Oak": {"exp": 15, "probability": 0.8}}
        inv = {}
        # success when r < p
        new_inv, exp, ok = apply_woodcutting_pure("Oak", inv, tree_data, r_action=0.1, success_probability=0.5)
        self.assertTrue(ok)
        self.assertEqual(exp, 15)
        self.assertEqual(new_inv.get("Oak"), 1)
        # failure when r >= p
        new_inv2, exp2, ok2 = apply_woodcutting_pure("Oak", inv, tree_data, r_action=0.6, success_probability=0.5)
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertEqual(new_inv2, inv)

    def test_apply_mining_pure_with_gem(self):
        ore_data = {"Iron ore": {"exp": 35, "probability": 0.8}}
        gem_data = {
            "Uncut sapphire": {"probability": 0.5, "exp": 50},
            "Uncut emerald": {"probability": 0.5, "exp": 67.5},
        }
        inv = {}
        # Force success and gem drop; pick first gem via r_gem_pick
        new_inv, exp, ok, gem = apply_mining_pure(
            "Iron ore", inv, ore_data, gem_data,
            r_action=0.1, success_probability=0.5,
            r_gem_chance=0.0, r_gem_pick=0.1, gem_drop_chance=1.0  # make drop guaranteed for test
        )
        self.assertTrue(ok)
        self.assertEqual(gem, "Uncut sapphire")
        self.assertEqual(new_inv.get("Iron ore"), 1)
        self.assertEqual(new_inv.get("Uncut sapphire"), 1)
        self.assertAlmostEqual(exp, 35 + 50)
        # Failure when action doesn't succeed
        new_inv2, exp2, ok2, gem2 = apply_mining_pure(
            "Iron ore", inv, ore_data, gem_data,
            r_action=0.9, success_probability=0.5,
            r_gem_chance=0.0, r_gem_pick=0.1,
        )
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertIsNone(gem2)
        self.assertEqual(new_inv2, inv)

    def test_can_mine_and_cut_pure(self):
        ore_data = {"Copper ore": {"level": 1}, "Iron ore": {"level": 15}}
        tree_data = {"Tree": {"level": 1}, "Oak": {"level": 15}}
        self.assertTrue(can_mine_ore_pure(1, "Copper ore", ore_data))
        self.assertFalse(can_mine_ore_pure(1, "Iron ore", ore_data))
        self.assertTrue(can_cut_tree_pure(1, "Tree", tree_data))
        self.assertFalse(can_cut_tree_pure(1, "Oak", tree_data))

    def test_can_craft_item_pure(self):
        crafting_data = {
            "Gold ring": {"level": 5, "requirements": {"Gold bar": 1}},
            "Soft clay": {"level": 1, "requirements": {"Clay": 1}},
        }
        inv = {"Gold bar": 1, "Clay": 1}
        self.assertFalse(can_craft_item_pure(1, inv, "Gold ring", crafting_data))  # level too low
        self.assertTrue(can_craft_item_pure(5, inv, "Gold ring", crafting_data))
        self.assertTrue(can_craft_item_pure(1, inv, "Soft clay", crafting_data))
        self.assertFalse(can_craft_item_pure(1, {}, "Soft clay", crafting_data))  # missing material

    def test_apply_fletching_pure(self):
        fletching_data = {
            "arrow_shafts": {
                "level": 1,
                "exp": 5.0,
                "requirements": {"Tree": 1},
                "output_item": "Arrow shafts",
                "output_qty": 15,
            },
            "oak_shortbow_u": {
                "level": 20,
                "exp": 16.5,
                "requirements": {"Oak": 1},
                "output_item": "Oak shortbow (u)",
                "output_qty": 1,
            },
        }
        inv = {"Tree": 2}
        self.assertTrue(can_fletch_item_pure(1, inv, "arrow_shafts", fletching_data))

        new_inv, exp, ok = apply_fletching_pure("arrow_shafts", inv, fletching_data)
        self.assertTrue(ok)
        self.assertAlmostEqual(exp, 5.0)
        self.assertEqual(new_inv["Tree"], 1)
        self.assertEqual(new_inv["Arrow shafts"], 15)
        self.assertEqual(inv["Tree"], 2)

        self.assertFalse(can_fletch_item_pure(1, {"Oak": 1}, "oak_shortbow_u", fletching_data))
        new_inv2, exp2, ok2 = apply_fletching_pure("oak_shortbow_u", {}, fletching_data)
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertEqual(new_inv2, {})

if __name__ == "__main__":
    unittest.main()
