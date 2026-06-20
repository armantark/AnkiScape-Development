import unittest
from logic_pure import (
    get_exp_to_next_level,
    calculate_new_level,
    get_newly_completed_achievements,
    calculate_probability_with_level,
    pick_gem,
    can_smelt_any_bar_pure,
    can_smith_any_pure,
    can_smith_item_pure,
    create_soft_clay_pure,
    has_crafting_materials_pure,
    apply_crafting_pure,
    apply_utility_activity_pure,
    apply_fletching_pure,
    apply_cooking_action_pure,
    apply_firemaking_action_pure,
    apply_fishing_action_pure,
    apply_claim_pure,
    apply_quest_progress_pure,
    apply_runecrafting_action_pure,
    apply_smelt_pure,
    apply_smithing_action_pure,
    apply_smithing_pure,
    apply_woodcutting_pure,
    apply_woodcutting_action_pure,
    apply_mining_pure,
    apply_mining_action_pure,
    apply_open_bird_nests_pure,
    action_telemetry_key_pure,
    best_woodcutting_axe_pure,
    best_mining_pickaxe_pure,
    bank_gear_rows_pure,
    equipment_bonus_state_pure,
    can_equip_item_pure,
    equip_item_pure,
    unequip_item_pure,
    equipment_stat_totals_pure,
    normalize_review_success_probability_pure,
    record_action_telemetry_pure,
    summarize_action_telemetry_pure,
    calculate_woodcutting_success_probability_pure,
    woodcutting_source_roll_chance_pure,
    calculate_mining_success_probability_pure,
    mining_source_roll_chance_pure,
    can_mine_ore_pure,
    can_cut_tree_pure,
    can_craft_item_pure,
    can_fletch_item_pure,
    can_burn_any_firemaking_target_pure,
    can_burn_firemaking_target_pure,
    calculate_firemaking_success_probability_pure,
    firemaking_target_locked_reasons_pure,
    firemaking_source_roll_chance_pure,
    fishing_source_roll_chance_pure,
    calculate_fishing_success_probability_pure,
    calculate_hunter_success_probability_pure,
    hunter_source_roll_chance_pure,
    cooking_source_roll_chance_pure,
    calculate_cooking_success_probability_pure,
    cooking_target_locked_reasons_pure,
    can_cook_target_pure,
    can_fish_method_pure,
    eligible_fishing_fish_pure,
    has_fishing_bait_pure,
    can_perform_utility_activity_pure,
    utility_activity_locked_reasons_pure,
    hunter_target_locked_reasons_pure,
    apply_hunter_action_pure,
    can_runecraft_target_pure,
    binding_necklace_charges_pure,
    calculate_iron_smelting_success_probability_pure,
    claim_rows_pure,
    consume_ring_of_forging_charge_pure,
    has_ring_of_forging_pure,
    sanitize_review_action_multiplier,
    smithing_success_probability_pure,
    can_start_quest_pure,
    start_quest_pure,
    quest_locked_reasons_pure,
    quest_availability_state_pure,
    quest_unlock_locked_reasons_pure,
    fletching_target_locked_reasons_pure,
    normalize_xp_rewards_pure,
)
from storage_pure import default_player_data
from constants import (
    ACHIEVEMENTS,
    CLAIM_DATA,
    GLORY_GEM_DROP_CHANCE,
    INCIDENTAL_GEM_DROP_TABLE,
    ITEM_DEFINITIONS,
    MINING_BONUS_ITEM_DATA,
    MINING_PICKAXE_DATA,
    WOODCUTTING_AXE_DATA,
    ORE_DATA,
    TREE_DATA,
    EQUIPMENT_DATA,
    FIREMAKING_DATA,
    FISHING_DATA,
    FLETCHING_DATA,
    COOKING_DATA,
    QUEST_DATA,
    QUEST_UNLOCK_RULES,
    HUNTER_DATA,
    RUNECRAFTING_DATA,
    RUNECRAFTING_POUCH_DATA,
    UTILITY_ACTIVITY_DATA,
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

    def test_apply_smithing_pure_smelt_and_forge(self):
        smithing_data = {
            "smelt_bronze_bar": {
                "level": 1,
                "exp": 6.2,
                "requirements": {"Tin ore": 1, "Copper ore": 1},
                "output_item": "Bronze bar",
                "output_qty": 1,
                "station": "furnace",
            },
            "forge_iron_pickaxe": {
                "level": 20,
                "exp": 50.0,
                "requirements": {"Iron bar": 2},
                "output_item": "Iron pickaxe",
                "output_qty": 1,
                "station": "anvil",
            },
        }
        inv = {"Tin ore": 1, "Copper ore": 1, "Iron bar": 2}

        self.assertTrue(can_smith_any_pure(inv, 1, smithing_data))
        self.assertFalse(can_smith_item_pure(19, inv, "forge_iron_pickaxe", smithing_data))
        self.assertTrue(can_smith_item_pure(20, inv, "forge_iron_pickaxe", smithing_data))

        after_smelt, smelt_exp, smelt_ok = apply_smithing_pure("smelt_bronze_bar", inv, smithing_data)
        self.assertTrue(smelt_ok)
        self.assertAlmostEqual(smelt_exp, 6.2)
        self.assertEqual(after_smelt["Tin ore"], 0)
        self.assertEqual(after_smelt["Copper ore"], 0)
        self.assertEqual(after_smelt["Bronze bar"], 1)

        after_forge, forge_exp, forge_ok = apply_smithing_pure("forge_iron_pickaxe", inv, smithing_data)
        self.assertTrue(forge_ok)
        self.assertAlmostEqual(forge_exp, 50.0)
        self.assertEqual(after_forge["Iron bar"], 0)
        self.assertEqual(after_forge["Iron pickaxe"], 1)
        self.assertEqual(inv["Iron bar"], 2)

    def test_iron_smelting_success_probability_matches_source_curve(self):
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(15), 0.50)
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(30), 0.65)
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(45), 0.80)
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(99), 0.80)
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(15, has_ring_of_forging=True), 1.0)

    def test_apply_smithing_action_pure_models_iron_failure_only(self):
        smithing_data = {
            "smelt_iron_bar": {
                "level": 15,
                "exp": 12.5,
                "requirements": {"Iron ore": 1},
                "output_item": "Iron bar",
                "output_qty": 1,
                "station": "furnace",
            },
            "smelt_bronze_bar": {
                "level": 1,
                "exp": 6.2,
                "requirements": {"Tin ore": 1, "Copper ore": 1},
                "output_item": "Bronze bar",
                "output_qty": 1,
                "station": "furnace",
            },
        }

        failed_inv, failed_exp, processed, output_item, failed = apply_smithing_action_pure(
            "smelt_iron_bar",
            {"Iron ore": 1},
            smithing_data,
            15,
            r_action=0.99,
        )
        self.assertTrue(processed)
        self.assertTrue(failed)
        self.assertEqual(failed_exp, 0)
        self.assertIsNone(output_item)
        self.assertEqual(failed_inv["Iron ore"], 0)
        self.assertNotIn("Iron bar", failed_inv)

        success_inv, success_exp, processed, output_item, failed = apply_smithing_action_pure(
            "smelt_iron_bar",
            {"Iron ore": 1},
            smithing_data,
            15,
            r_action=0.0,
        )
        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output_item, "Iron bar")
        self.assertAlmostEqual(success_exp, 12.5)
        self.assertEqual(success_inv["Iron ore"], 0)
        self.assertEqual(success_inv["Iron bar"], 1)

        bronze_inv, bronze_exp, processed, output_item, failed = apply_smithing_action_pure(
            "smelt_bronze_bar",
            {"Tin ore": 1, "Copper ore": 1},
            smithing_data,
            1,
            r_action=1.0,
        )
        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output_item, "Bronze bar")
        self.assertAlmostEqual(bronze_exp, 6.2)
        self.assertEqual(bronze_inv["Bronze bar"], 1)

    def test_ring_of_forging_guarantees_iron_and_consumes_charges(self):
        smithing_data = {
            "smelt_iron_bar": {
                "level": 15,
                "exp": 12.5,
                "requirements": {"Iron ore": 1},
                "output_item": "Iron bar",
                "output_qty": 1,
                "station": "furnace",
            },
        }
        player_data = {"equipment": {"ring": "Ring of forging"}, "item_charges": {"Ring of forging": 2}}
        self.assertTrue(has_ring_of_forging_pure(player_data))
        self.assertEqual(smithing_success_probability_pure("smelt_iron_bar", smithing_data["smelt_iron_bar"], 15, True), 1.0)

        inv, exp, processed, output_item, failed = apply_smithing_action_pure(
            "smelt_iron_bar",
            {"Iron ore": 1},
            smithing_data,
            15,
            r_action=0.99,
            has_ring_of_forging=True,
        )
        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output_item, "Iron bar")
        self.assertAlmostEqual(exp, 12.5)
        self.assertEqual(inv["Iron bar"], 1)

        one_charge = consume_ring_of_forging_charge_pure(player_data)
        self.assertEqual(one_charge["item_charges"]["Ring of forging"], 1)
        crumbled = consume_ring_of_forging_charge_pure(one_charge)
        self.assertNotIn("ring", crumbled["equipment"])
        self.assertNotIn("Ring of forging", crumbled["item_charges"])

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

    def test_apply_feather_scavenging_batches_without_inputs_or_xp(self):
        inv = {}

        self.assertTrue(can_perform_utility_activity_pure(
            inv,
            "scavenge_chicken_feathers",
            UTILITY_ACTIVITY_DATA,
        ))

        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "scavenge_chicken_feathers",
            inv,
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 28)
        self.assertEqual(new_inv["Feather"], 28)
        self.assertEqual(inv, {})

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

    def test_apply_crafting_pure_ignores_batch_size_for_xp_actions(self):
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
        self.assertEqual(exp, 15)
        self.assertEqual(new_inv["Flax"], 29)
        self.assertEqual(new_inv["Bow string"], 1)
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

    def test_review_action_multiplier_validation(self):
        self.assertEqual(sanitize_review_action_multiplier("2.5"), 2)
        self.assertEqual(sanitize_review_action_multiplier("bad"), 1)
        self.assertEqual(sanitize_review_action_multiplier(True), 1)
        self.assertEqual(sanitize_review_action_multiplier(-5), 1)
        self.assertEqual(sanitize_review_action_multiplier(500), 10)

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
        tree_data = {"oak": {"exp": 15, "probability": 0.8, "output_item": "Oak logs"}}
        inv = {}
        # success when r < p
        new_inv, exp, ok = apply_woodcutting_pure("oak", inv, tree_data, r_action=0.1, success_probability=0.5)
        self.assertTrue(ok)
        self.assertEqual(exp, 15)
        self.assertEqual(new_inv.get("Oak logs"), 1)
        # failure when r >= p
        new_inv2, exp2, ok2 = apply_woodcutting_pure("oak", inv, tree_data, r_action=0.6, success_probability=0.5)
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertEqual(new_inv2, inv)

    def test_woodcutting_axe_selection_and_source_shaped_probability(self):
        axe_data = {
            "bronze_hatchet": {"display_name": "Bronze hatchet", "level": 1, "ratio": 1.0, "status": "implemented"},
            "rune_hatchet": {"display_name": "Rune hatchet", "level": 41, "ratio": 3.5, "status": "implemented"},
        }
        target = {"low_chance": 32, "high_chance": 100}

        bronze = best_woodcutting_axe_pure(50, {}, {"woodcutting": ["bronze_hatchet"]}, axe_data)
        rune = best_woodcutting_axe_pure(50, {"Rune hatchet": 1}, {"woodcutting": ["bronze_hatchet"]}, axe_data)

        self.assertEqual(bronze["display_name"], "Bronze hatchet")
        self.assertEqual(rune["display_name"], "Rune hatchet")
        self.assertGreater(
            calculate_woodcutting_success_probability_pure(50, target, rune),
            calculate_woodcutting_success_probability_pure(50, target, bronze),
        )

    def test_apply_woodcutting_action_awards_output_and_bird_nest(self):
        tree_data = {"tree": {"exp": 25.0, "output_item": "Logs", "low_chance": 64, "high_chance": 200}}
        axe = {"display_name": "Bronze hatchet", "level": 1, "ratio": 1.0, "status": "implemented"}
        nest_table = (
            {"item": "Bird's nest (seeds)", "weight": 65},
            {"item": "Bird's nest (ring)", "weight": 35},
        )

        new_inv, exp, ok, output_item, nest_item = apply_woodcutting_action_pure(
            "tree",
            {},
            tree_data,
            1,
            axe,
            r_action=0.0,
            r_nest_drop=0.0,
            r_nest_type=0.0,
            nest_drop_table=nest_table,
            nest_drop_chance=1.0,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 25.0)
        self.assertEqual(output_item, "Logs")
        self.assertEqual(nest_item, "Bird's nest (seeds)")
        self.assertEqual(new_inv["Logs"], 1)
        self.assertEqual(new_inv["Bird's nest (seeds)"], 1)

    def test_apply_woodcutting_action_ivy_awards_xp_without_output(self):
        tree_data = {"ivy": {"exp": 332.5, "output_item": None, "low_chance": 7, "high_chance": 11}}
        axe = {"display_name": "Dragon hatchet", "level": 61, "ratio": 3.75, "status": "implemented"}

        new_inv, exp, ok, output_item, nest_item = apply_woodcutting_action_pure(
            "ivy",
            {},
            tree_data,
            99,
            axe,
            r_action=0.0,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 332.5)
        self.assertIsNone(output_item)
        self.assertIsNone(nest_item)
        self.assertEqual(new_inv, {})

    def test_open_bird_nests_batches_random_contents_without_xp(self):
        tables = {
            "Bird's nest (seeds)": {
                "guaranteed_item": "Bird's nest (empty)",
                "total_weight": 2,
                "rolls": (
                    {"item": "Acorn", "weight": 1},
                    {"item": "Magic seed", "weight": 1},
                ),
            }
        }

        new_inv, ok, opened, outputs = apply_open_bird_nests_pure(
            {"Bird's nest (seeds)": 2},
            tables,
            rolls=[0.0, 0.75],
            batch_size=28,
        )

        self.assertTrue(ok)
        self.assertEqual(opened, 2)
        self.assertEqual(new_inv["Bird's nest (seeds)"], 0)
        self.assertEqual(new_inv["Bird's nest (empty)"], 2)
        self.assertEqual(new_inv["Acorn"], 1)
        self.assertEqual(new_inv["Magic seed"], 1)
        self.assertEqual(outputs["Bird's nest (empty)"], 2)

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

    def test_best_mining_pickaxe_prefers_best_owned_usable_tool(self):
        pickaxe = best_mining_pickaxe_pure(
            41,
            {"Rune pickaxe": 1, "Dragon pickaxe": 1},
            {"mining": ["bronze_pickaxe"]},
            MINING_PICKAXE_DATA,
        )
        self.assertEqual(pickaxe["display_name"], "Rune pickaxe")

        pickaxe = best_mining_pickaxe_pure(
            61,
            {"Rune pickaxe": 1, "Dragon pickaxe": 1},
            {"mining": ["bronze_pickaxe"]},
            MINING_PICKAXE_DATA,
        )
        self.assertEqual(pickaxe["display_name"], "Dragon pickaxe")

    def test_mining_success_probability_scales_by_pickaxe_and_target(self):
        bronze = MINING_PICKAXE_DATA["bronze_pickaxe"]
        rune = MINING_PICKAXE_DATA["rune_pickaxe"]
        iron = ORE_DATA["iron"]
        runite = ORE_DATA["runite"]

        self.assertGreater(
            calculate_mining_success_probability_pure(60, iron, rune),
            calculate_mining_success_probability_pure(60, iron, bronze),
        )
        self.assertGreater(
            calculate_mining_success_probability_pure(60, iron, rune),
            calculate_mining_success_probability_pure(60, runite, rune),
        )

    def test_apply_mining_action_outputs_pure_essence_without_random_gems(self):
        new_inv, exp, ok, output_item, gem, extra = apply_mining_action_pure(
            "rune_essence",
            {"Pure essence": 0, "Uncut sapphire": 0},
            ORE_DATA,
            30,
            MINING_PICKAXE_DATA["bronze_pickaxe"],
            0.0,
            0.0,
            0.0,
            0.0,
            INCIDENTAL_GEM_DROP_TABLE,
            1.0,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 5.0)
        self.assertEqual(output_item, "Pure essence")
        self.assertIsNone(gem)
        self.assertIsNone(extra)
        self.assertEqual(new_inv["Pure essence"], 1)
        self.assertEqual(new_inv["Uncut sapphire"], 0)

    def test_apply_mining_action_weighted_outputs_use_output_xp(self):
        new_inv, exp, ok, output_item, _gem, _extra = apply_mining_action_pure(
            "sandstone",
            {},
            ORE_DATA,
            35,
            MINING_PICKAXE_DATA["rune_pickaxe"],
            0.0,
            0.99,
        )

        self.assertTrue(ok)
        self.assertEqual(output_item, "Sandstone (10kg)")
        self.assertEqual(exp, 60.0)
        self.assertEqual(new_inv["Sandstone (10kg)"], 1)

    def test_apply_mining_action_gems_are_inventory_only_side_drops(self):
        new_inv, exp, ok, output_item, gem, _extra = apply_mining_action_pure(
            "iron",
            {"Iron ore": 0, "Uncut sapphire": 0},
            ORE_DATA,
            60,
            MINING_PICKAXE_DATA["rune_pickaxe"],
            0.0,
            0.0,
            0.0,
            0.99,
            INCIDENTAL_GEM_DROP_TABLE,
            GLORY_GEM_DROP_CHANCE,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 35.0)
        self.assertEqual(output_item, "Iron ore")
        self.assertEqual(gem, "Uncut sapphire")
        self.assertEqual(new_inv["Iron ore"], 1)
        self.assertEqual(new_inv["Uncut sapphire"], 1)

    def test_mining_bonus_state_and_varrock_extra_output(self):
        bonus_state = equipment_bonus_state_pure(
            {"neck": "Amulet of glory (4)", "body": "Varrock armour 1"},
            MINING_BONUS_ITEM_DATA,
        )

        self.assertTrue(bonus_state["has_glory"])
        self.assertEqual(bonus_state["varrock_armour_tier"], 1)

        new_inv, exp, ok, output_item, _gem, extra = apply_mining_action_pure(
            "coal",
            {"Coal": 0},
            ORE_DATA,
            60,
            MINING_PICKAXE_DATA["rune_pickaxe"],
            0.0,
            0.0,
            None,
            None,
            INCIDENTAL_GEM_DROP_TABLE,
            varrock_armour_tier=bonus_state["varrock_armour_tier"],
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 50.0)
        self.assertEqual(output_item, "Coal")
        self.assertEqual(extra, "Coal")
        self.assertEqual(new_inv["Coal"], 2)

    def test_can_equip_uses_real_combat_level_gate(self):
        ok, reason = can_equip_item_pure("Bronze platebody", EQUIPMENT_DATA, {"defense_level": 1})
        self.assertTrue(ok)
        self.assertEqual(reason, "")

        ok, reason = can_equip_item_pure("Rune platebody", EQUIPMENT_DATA, {"defense_level": 1})
        self.assertFalse(ok)
        self.assertEqual(reason, "Requires level 40 Defense")

    def test_equip_unequip_returns_displaced_items(self):
        inv = {"Bronze platebody": 1, "Iron platebody": 1}
        new_inv, equipment, ok = equip_item_pure("Bronze platebody", inv, {}, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(new_inv["Bronze platebody"], 0)
        self.assertEqual(equipment, {"body": "Bronze platebody"})

        new_inv, equipment, ok = equip_item_pure("Iron platebody", new_inv, equipment, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(new_inv["Iron platebody"], 0)
        self.assertEqual(new_inv["Bronze platebody"], 1)
        self.assertEqual(equipment, {"body": "Iron platebody"})

        new_inv, equipment, ok = unequip_item_pure("body", new_inv, equipment)
        self.assertTrue(ok)
        self.assertEqual(new_inv["Iron platebody"], 1)
        self.assertEqual(equipment, {})

    def test_two_handed_weapon_and_shield_displace_each_other(self):
        inv = {"Bronze 2h sword": 1, "Bronze sq shield": 1}
        inv, equipment, ok = equip_item_pure("Bronze sq shield", inv, {}, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(equipment, {"shield": "Bronze sq shield"})

        inv, equipment, ok = equip_item_pure("Bronze 2h sword", inv, equipment, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(equipment, {"weapon": "Bronze 2h sword"})
        self.assertEqual(inv["Bronze sq shield"], 1)

        inv, equipment, ok = equip_item_pure("Bronze sq shield", inv, equipment, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(equipment, {"shield": "Bronze sq shield"})
        self.assertEqual(inv["Bronze 2h sword"], 1)

    def test_equipment_stat_totals_sum_worn_bonuses(self):
        totals = equipment_stat_totals_pure(
            {"weapon": "Bronze sword", "body": "Bronze platebody"},
            EQUIPMENT_DATA,
        )
        self.assertEqual(totals.attack_stab, EQUIPMENT_DATA["Bronze sword"].bonuses.attack_stab)
        self.assertEqual(totals.defence_stab, EQUIPMENT_DATA["Bronze platebody"].bonuses.defence_stab)
        self.assertEqual(totals.melee_strength, EQUIPMENT_DATA["Bronze sword"].bonuses.melee_strength)

    def test_can_mine_and_cut_pure(self):
        ore_data = {"Copper ore": {"level": 1}, "Iron ore": {"level": 15}}
        tree_data = {"tree": {"level": 1}, "oak": {"level": 15}}
        self.assertTrue(can_mine_ore_pure(1, "Copper ore", ore_data))
        self.assertFalse(can_mine_ore_pure(1, "Iron ore", ore_data))
        self.assertTrue(can_cut_tree_pure(1, "tree", tree_data))
        self.assertFalse(can_cut_tree_pure(1, "oak", tree_data))

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
                "requirements": {"Logs": 1},
                "output_item": "Arrow shafts",
                "output_qty": 15,
            },
            "oak_shortbow_u": {
                "level": 20,
                "exp": 16.5,
                "requirements": {"Oak logs": 1},
                "output_item": "Oak shortbow (u)",
                "output_qty": 1,
            },
        }
        inv = {"Logs": 2}
        self.assertTrue(can_fletch_item_pure(1, inv, "arrow_shafts", fletching_data))

        new_inv, exp, ok = apply_fletching_pure("arrow_shafts", inv, fletching_data)
        self.assertTrue(ok)
        self.assertAlmostEqual(exp, 5.0)
        self.assertEqual(new_inv["Logs"], 1)
        self.assertEqual(new_inv["Arrow shafts"], 15)
        self.assertEqual(inv["Logs"], 2)

        self.assertFalse(can_fletch_item_pure(1, {"Oak logs": 1}, "oak_shortbow_u", fletching_data))
        new_inv2, exp2, ok2 = apply_fletching_pure("oak_shortbow_u", {}, fletching_data)
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertEqual(new_inv2, {})

    def test_action_telemetry_records_expected_observed_and_outputs(self):
        player_data = {}

        record_action_telemetry_pure(
            player_data,
            "fishing",
            "catch_mackerel_cod_bass",
            False,
            expected_success_chance=0.4,
            failure_kind="dry",
        )
        record_action_telemetry_pure(
            player_data,
            "fishing",
            "catch_mackerel_cod_bass",
            True,
            expected_success_chance=0.4,
            output_item="Raw mackerel",
        )

        key = action_telemetry_key_pure("fishing", "catch_mackerel_cod_bass")
        record = player_data["action_telemetry"]["actions"][key]
        self.assertEqual(record["attempts"], 2)
        self.assertEqual(record["successes"], 1)
        self.assertEqual(record["failures"], 1)
        self.assertAlmostEqual(record["expected_successes"], 0.8)
        self.assertEqual(record["current_dry_streak"], 0)
        self.assertEqual(record["longest_dry_streak"], 1)
        self.assertEqual(record["outputs"], {"Raw mackerel": 1})
        self.assertEqual(record["failure_kinds"], {"dry": 1})

        summary = summarize_action_telemetry_pure(player_data)[0]
        self.assertEqual(summary["key"], key)
        self.assertAlmostEqual(summary["observed_success_rate"], 0.5)
        self.assertAlmostEqual(summary["expected_success_rate"], 0.4)

    def test_review_success_normalization_is_shared_for_source_odds(self):
        mining_target = ORE_DATA["coal"]
        rune_pickaxe = MINING_PICKAXE_DATA["rune_pickaxe"]
        woodcutting_target = TREE_DATA["willow"]
        rune_hatchet = WOODCUTTING_AXE_DATA["rune_hatchet"]
        crayfish = FISHING_DATA["catch_crayfish"]["fish"][0]
        kebbit = HUNTER_DATA["catch_wild_kebbit"]
        shrimps = COOKING_DATA["cook_shrimps"]

        self.assertAlmostEqual(
            calculate_mining_success_probability_pure(60, mining_target, rune_pickaxe),
            normalize_review_success_probability_pure(mining_source_roll_chance_pure(60, mining_target, rune_pickaxe)),
        )
        self.assertAlmostEqual(
            calculate_woodcutting_success_probability_pure(60, woodcutting_target, rune_hatchet),
            normalize_review_success_probability_pure(woodcutting_source_roll_chance_pure(60, woodcutting_target, rune_hatchet)),
        )
        self.assertAlmostEqual(
            calculate_fishing_success_probability_pure(1, crayfish),
            normalize_review_success_probability_pure(fishing_source_roll_chance_pure(1, crayfish)),
        )
        self.assertAlmostEqual(
            calculate_hunter_success_probability_pure(23, kebbit),
            normalize_review_success_probability_pure(hunter_source_roll_chance_pure(23, kebbit)),
        )
        self.assertAlmostEqual(
            calculate_cooking_success_probability_pure(1, shrimps),
            normalize_review_success_probability_pure(cooking_source_roll_chance_pure(1, shrimps)),
        )

    def test_firemaking_source_chance_and_tier_curve(self):
        logs = FIREMAKING_DATA["logs"]
        magic = FIREMAKING_DATA["magic_logs"]

        self.assertAlmostEqual(firemaking_source_roll_chance_pure(1, logs), 65 / 255)
        self.assertEqual(firemaking_source_roll_chance_pure(99, logs), 1.0)
        self.assertLess(
            firemaking_source_roll_chance_pure(40, {"low_chance": 40, "high_chance": 200}),
            firemaking_source_roll_chance_pure(40, {"low_chance": 80, "high_chance": 300}),
        )

        logs_at_unlock = calculate_firemaking_success_probability_pure(1, logs)
        logs_overleveled = calculate_firemaking_success_probability_pure(45, logs)
        magic_at_unlock = calculate_firemaking_success_probability_pure(75, magic)
        magic_overleveled = calculate_firemaking_success_probability_pure(99, magic)

        self.assertGreaterEqual(logs_at_unlock, 0.40)
        self.assertLessEqual(logs_at_unlock, 0.50)
        self.assertGreater(logs_overleveled, logs_at_unlock)
        self.assertGreater(logs_overleveled, magic_at_unlock)
        self.assertGreater(magic_overleveled, magic_at_unlock)
        self.assertLessEqual(magic_overleveled, 0.95)

    def test_firemaking_gating_and_action_application(self):
        self.assertTrue(can_burn_firemaking_target_pure(1, {"Logs": 1}, "logs", FIREMAKING_DATA))
        self.assertFalse(can_burn_firemaking_target_pure(1, {}, "logs", FIREMAKING_DATA))
        self.assertFalse(can_burn_firemaking_target_pure(14, {"Oak logs": 1}, "oak_logs", FIREMAKING_DATA))
        self.assertTrue(can_burn_any_firemaking_target_pure({"Logs": 1}, 1, FIREMAKING_DATA))
        self.assertFalse(can_burn_any_firemaking_target_pure({"Oak logs": 1}, 1, FIREMAKING_DATA))

        inv = {"Logs": 2, "Ashes": 4}
        new_inv, exp, ok, output_item = apply_firemaking_action_pure(
            "logs",
            inv,
            FIREMAKING_DATA,
            1,
            r_action=0.0,
        )
        self.assertTrue(ok)
        self.assertAlmostEqual(exp, 40.0)
        self.assertEqual(output_item, "Ashes")
        self.assertEqual(new_inv["Logs"], 1)
        self.assertEqual(new_inv["Ashes"], 5)
        self.assertEqual(inv["Logs"], 2)

        failed_inv, failed_exp, failed_ok, failed_output = apply_firemaking_action_pure(
            "logs",
            inv,
            FIREMAKING_DATA,
            1,
            r_action=1.0,
        )
        self.assertFalse(failed_ok)
        self.assertEqual(failed_exp, 0)
        self.assertIsNone(failed_output)
        self.assertEqual(failed_inv, inv)

    def test_fishing_source_odds_and_scaled_probability(self):
        crayfish = FISHING_DATA["catch_crayfish"]["fish"][0]
        shark = FISHING_DATA["catch_sharks"]["fish"][0]

        self.assertAlmostEqual(fishing_source_roll_chance_pure(1, crayfish), 58 / 255)
        self.assertEqual(fishing_source_roll_chance_pure(99, crayfish), 1.0)
        self.assertLess(
            fishing_source_roll_chance_pure(76, shark),
            fishing_source_roll_chance_pure(99, shark),
        )

        scaled = calculate_fishing_success_probability_pure(1, crayfish)
        self.assertGreater(scaled, fishing_source_roll_chance_pure(1, crayfish))
        self.assertLessEqual(calculate_fishing_success_probability_pure(99, crayfish), 0.95)
        mackerel = FISHING_DATA["catch_mackerel_cod_bass"]["fish"][0]
        self.assertGreater(calculate_fishing_success_probability_pure(18, mackerel), 0.35)

    def test_fishing_ordered_rolls_and_bait_consumed_only_on_catch(self):
        inv = {"Fishing bait": 1}

        dry_inv, dry_exp, dry_ok, dry_output, dry_rewards = apply_fishing_action_pure(
            "catch_sardine_herring",
            inv,
            FISHING_DATA,
            fishing_level=10,
            rolls=(1.0, 1.0),
        )
        self.assertFalse(dry_ok)
        self.assertEqual(dry_exp, 0)
        self.assertIsNone(dry_output)
        self.assertEqual(dry_rewards, ())
        self.assertEqual(dry_inv["Fishing bait"], 1)

        catch_inv, catch_exp, catch_ok, catch_output, rewards = apply_fishing_action_pure(
            "catch_sardine_herring",
            inv,
            FISHING_DATA,
            fishing_level=10,
            rolls=(0.0, 0.0),
        )
        self.assertTrue(catch_ok)
        self.assertEqual(catch_output, "Raw sardine")
        self.assertAlmostEqual(catch_exp, 20.0)
        self.assertEqual(rewards, ({"skill_id": "fishing", "amount": 20.0},))
        self.assertEqual(catch_inv["Fishing bait"], 0)
        self.assertEqual(catch_inv["Raw sardine"], 1)
        self.assertEqual(inv["Fishing bait"], 1)

    def test_fishing_mixed_outputs_respect_source_order_after_level_filter(self):
        low_level_fish = eligible_fishing_fish_pure(
            FISHING_DATA["catch_shrimp_anchovies"],
            fishing_level=1,
        )
        self.assertEqual([fish["output_item"] for fish in low_level_fish], ["Raw shrimps"])

        inv, exp, ok, output_item, _rewards = apply_fishing_action_pure(
            "catch_shrimp_anchovies",
            {},
            FISHING_DATA,
            fishing_level=15,
            rolls=(1.0, 0.0),
        )
        self.assertTrue(ok)
        self.assertEqual(output_item, "Raw shrimps")
        self.assertAlmostEqual(exp, 10.0)
        self.assertEqual(inv["Raw shrimps"], 1)

        inv2, exp2, ok2, output_item2, _rewards2 = apply_fishing_action_pure(
            "catch_shrimp_anchovies",
            {},
            FISHING_DATA,
            fishing_level=15,
            rolls=(0.0, 0.0),
        )
        self.assertTrue(ok2)
        self.assertEqual(output_item2, "Raw anchovies")
        self.assertAlmostEqual(exp2, 40.0)
        self.assertEqual(inv2["Raw anchovies"], 1)

    def test_fishing_side_level_gates_and_hidden_side_xp_rewards(self):
        self.assertFalse(can_fish_method_pure(48, {"Feather": 1}, "catch_leaping_fish", FISHING_DATA, 14, 15))
        self.assertFalse(can_fish_method_pure(48, {"Feather": 1}, "catch_leaping_fish", FISHING_DATA, 15, 14))
        self.assertTrue(can_fish_method_pure(48, {"Feather": 1}, "catch_leaping_fish", FISHING_DATA, 15, 15))

        inv, exp, ok, output_item, rewards = apply_fishing_action_pure(
            "catch_leaping_fish",
            {"Feather": 1},
            FISHING_DATA,
            fishing_level=48,
            strength_level=15,
            agility_level=15,
            rolls=(0.0,),
        )
        self.assertTrue(ok)
        self.assertEqual(output_item, "Leaping trout")
        self.assertAlmostEqual(exp, 50.0)
        self.assertEqual(
            rewards,
            (
                {"skill_id": "fishing", "amount": 50.0},
                {"skill_id": "strength", "amount": 5.0},
                {"skill_id": "agility", "amount": 5.0},
            ),
        )
        self.assertEqual(inv["Feather"], 0)

    def test_xp_rewards_normalization_combines_duplicate_skills_and_falls_back(self):
        rewards = normalize_xp_rewards_pure(
            {
                "xp_rewards": (
                    {"skill_id": "fishing", "amount": 10},
                    {"skill_id": "fishing", "amount": 2.5},
                    ("agility", 3),
                    {"skill_id": "", "amount": 99},
                )
            }
        )
        self.assertEqual(
            rewards,
            (
                {"skill_id": "fishing", "amount": 12.5},
                {"skill_id": "agility", "amount": 3.0},
            ),
        )
        self.assertEqual(
            normalize_xp_rewards_pure({}, "fletching", 5),
            ({"skill_id": "fletching", "amount": 5.0},),
        )

    def test_fishing_material_gates_and_utility_bait_batch(self):
        self.assertTrue(has_fishing_bait_pure({"Fishing bait": 1}, FISHING_DATA["catch_sardine_herring"]))
        self.assertFalse(has_fishing_bait_pure({}, FISHING_DATA["catch_sardine_herring"]))
        self.assertTrue(has_fishing_bait_pure({"Caviar": 1}, FISHING_DATA["catch_leaping_fish"]))
        self.assertFalse(can_fish_method_pure(5, {}, "catch_sardine_herring", FISHING_DATA))

        self.assertTrue(can_perform_utility_activity_pure({}, "gather_fishing_bait", UTILITY_ACTIVITY_DATA))
        inv, exp, ok, processed = apply_utility_activity_pure(
            "gather_fishing_bait",
            {},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 28)
        self.assertEqual(inv["Fishing bait"], 28)

    def test_utility_activity_supports_one_shot_multi_output_purchase(self):
        inv, exp, ok, processed = apply_utility_activity_pure(
            "buy_hunter_supplies",
            {"Coins": 500},
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 1)
        self.assertEqual(inv["Coins"], 0)
        self.assertEqual(inv["Bird snare"], 1)
        self.assertEqual(inv["Box trap"], 1)
        self.assertEqual(inv["Butterfly jar"], 10)
        self.assertEqual(inv["Impling jar"], 10)

    def test_hunter_reusable_tools_gate_targets_without_being_consumed(self):
        self.assertEqual(
            hunter_target_locked_reasons_pure(
                {"hunter_level": 1, "inventory": {}},
                "catch_crimson_swift",
                HUNTER_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Bird snare",),
        )

        inv, exp, ok, _output_item, _rewards = apply_hunter_action_pure(
            "catch_crimson_swift",
            {"Bird snare": 1},
            HUNTER_DATA,
            1,
            0.0,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 34.0)
        self.assertEqual(inv["Bird snare"], 1)
        self.assertEqual(inv["Red feather"], 5)

        butterfly_inv, _exp, butterfly_ok, _output_item, _rewards = apply_hunter_action_pure(
            "catch_ruby_harvest",
            {"Butterfly net": 1, "Butterfly jar": 1},
            HUNTER_DATA,
            15,
            0.0,
        )
        self.assertTrue(butterfly_ok)
        self.assertEqual(butterfly_inv["Butterfly net"], 1)
        self.assertEqual(butterfly_inv["Butterfly jar"], 0)

    def test_cooking_source_odds_and_scaled_probability(self):
        shrimps = COOKING_DATA["cook_shrimps"]
        shark = COOKING_DATA["cook_shark"]

        self.assertAlmostEqual(cooking_source_roll_chance_pure(1, shrimps), 128 / 255)
        self.assertEqual(cooking_source_roll_chance_pure(99, shrimps), 1.0)
        self.assertLess(
            cooking_source_roll_chance_pure(80, shark),
            cooking_source_roll_chance_pure(99, shark),
        )

        scaled = calculate_cooking_success_probability_pure(1, shrimps)
        self.assertGreater(scaled, cooking_source_roll_chance_pure(1, shrimps))
        self.assertLessEqual(calculate_cooking_success_probability_pure(99, shrimps), 0.98)

    def test_cooking_success_and_burn_consume_raw_item(self):
        self.assertTrue(can_cook_target_pure(1, {"Raw beef": 2}, "render_beef_sinew", COOKING_DATA))
        self.assertFalse(can_cook_target_pure(1, {}, "render_beef_sinew", COOKING_DATA))
        self.assertFalse(can_cook_target_pure(79, {"Raw shark": 1}, "cook_shark", COOKING_DATA))

        cooked_inv, cooked_exp, cooked_ok, cooked_output, cooked_burned = apply_cooking_action_pure(
            "render_beef_sinew",
            {"Raw beef": 2},
            COOKING_DATA,
            cooking_level=1,
            roll=0.0,
        )
        self.assertTrue(cooked_ok)
        self.assertFalse(cooked_burned)
        self.assertEqual(cooked_output, "Sinew")
        self.assertAlmostEqual(cooked_exp, 30.0)
        self.assertEqual(cooked_inv["Raw beef"], 1)
        self.assertEqual(cooked_inv["Sinew"], 1)

        burnt_inv, burnt_exp, burnt_ok, burnt_output, burnt_burned = apply_cooking_action_pure(
            "cook_shrimps",
            {"Raw shrimps": 1},
            COOKING_DATA,
            cooking_level=1,
            roll=1.0,
        )
        self.assertTrue(burnt_ok)
        self.assertTrue(burnt_burned)
        self.assertEqual(burnt_exp, 0)
        self.assertEqual(burnt_output, "Burnt shrimp")
        self.assertEqual(burnt_inv["Raw shrimps"], 0)
        self.assertEqual(burnt_inv["Burnt shrimp"], 1)

    def test_rune_mysteries_progresses_on_reviews_and_rewards_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        player_data, ok = start_quest_pure(player_data, "rune_mysteries", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "rune_mysteries")

        completed_now = False
        for _ in range(6):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "rune_mysteries",
                QUEST_DATA,
            )
            self.assertTrue(ok)

        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["rune_mysteries"]["completed"])
        self.assertEqual(player_data["quests"]["rune_mysteries"]["progress"], 6)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["inventory"]["Air talisman"], 1)
        self.assertEqual(player_data["runecrafting_exp"], 250)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {"magic_exp": 250.0})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "rune_mysteries",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["inventory"]["Air talisman"], 1)
        self.assertEqual(after_complete["runecrafting_exp"], 250)
        self.assertEqual(after_complete["pending_skill_exp_rewards"], {"magic_exp": 250.0})

    def test_unlock_quests_enforce_strict_start_requirements(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["crafting_level"] = 31
        player_data["woodcutting_level"] = 36

        reasons = quest_locked_reasons_pure(player_data, "lost_city", QUEST_DATA)
        self.assertEqual(reasons, ())

        lunar_reasons = quest_locked_reasons_pure(player_data, "lunar_diplomacy", QUEST_DATA)
        self.assertIn("The Fremennik Trials", lunar_reasons)
        self.assertIn("Lost City", lunar_reasons)
        self.assertIn("Rune Mysteries", lunar_reasons)
        self.assertIn("Shilo Village", lunar_reasons)
        self.assertIn("Defence 40 (not implemented)", lunar_reasons)
        self.assertIn("Herblore 5 (not implemented)", lunar_reasons)
        self.assertIn("Magic 65 (not implemented)", lunar_reasons)
        self.assertFalse(can_start_quest_pure(player_data, "lunar_diplomacy", QUEST_DATA))

    def test_quest_availability_separates_start_locks_from_progress(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            quest_availability_state_pure(player_data, "lost_city", QUEST_DATA),
            "locked",
        )
        self.assertEqual(
            quest_availability_state_pure(player_data, "cooks_assistant", QUEST_DATA),
            "can_start",
        )

        player_data["quests"]["lost_city"] = {"started": True, "progress": 1, "completed": False}
        self.assertEqual(
            quest_availability_state_pure(player_data, "lost_city", QUEST_DATA),
            "in_progress",
        )

        player_data["quests"]["lost_city"] = {"started": True, "progress": 6, "completed": True}
        self.assertEqual(
            quest_availability_state_pure(player_data, "lost_city", QUEST_DATA),
            "completed",
        )

    def test_lost_city_completion_unlocks_cosmic_runecrafting_gate(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["crafting_level"] = 31
        player_data["woodcutting_level"] = 36

        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "runecrafting", "craft_cosmic_runes", QUEST_UNLOCK_RULES),
            ("Lost City",),
        )

        for _ in range(6):
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, "lost_city", QUEST_DATA)
            self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["lost_city"]["completed"])
        self.assertEqual(player_data["quest_points"], 3)
        self.assertEqual(player_data["inventory"]["Dramen staff"], 1)
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "runecrafting", "craft_cosmic_runes", QUEST_UNLOCK_RULES),
            (),
        )

    def test_quest_completion_awards_implemented_xp_and_parks_unimplemented_xp(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["lunar_diplomacy"] = {"started": True, "progress": 7, "completed": False}

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "lunar_diplomacy",
            QUEST_DATA,
        )

        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["inventory"]["Astral rune"], 50)
        self.assertEqual(player_data["runecrafting_exp"], 5000)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {"magic_exp": 5000.0})

    def test_generated_quest_blocks_on_requirements_and_parks_unimplemented_xp(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        reasons = quest_locked_reasons_pure(player_data, "dragon_slayer", QUEST_DATA)
        self.assertIn("33 quest points", reasons)
        self.assertFalse(can_start_quest_pure(player_data, "dragon_slayer", QUEST_DATA))

        player_data["quest_points"] = 33
        player_data["quests"]["dragon_slayer"] = {
            "started": True,
            "progress": QUEST_DATA["dragon_slayer"]["stages"] - 1,
            "completed": False,
        }
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "dragon_slayer", QUEST_DATA)

        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quest_points"], 35)
        self.assertEqual(
            player_data["pending_skill_exp_rewards"],
            {"defense_exp": 18650.0, "strength_exp": 18650.0},
        )

    def test_fishing_unlock_rules_cover_swan_song_and_tai_bwo_wannai_trio(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_monkfish", QUEST_UNLOCK_RULES),
            ("Swan Song",),
        )
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_karambwan", QUEST_UNLOCK_RULES),
            ("Tai Bwo Wannai Trio",),
        )
        player_data["quests"]["swan_song"] = {"started": True, "progress": 6, "completed": True}
        player_data["quests"]["tai_bwo_wannai_trio"] = {"started": True, "progress": 6, "completed": True}
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_monkfish", QUEST_UNLOCK_RULES),
            (),
        )
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_karambwan", QUEST_UNLOCK_RULES),
            (),
        )

    def test_ability_unlock_rules_cover_barbarian_fishing_and_broad_fletching(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["fishing_level"] = 99
        player_data["fletching_level"] = 99
        player_data["inventory"].update(
            {
                "Feather": 10,
                "Headless arrows": 15,
                "Broad arrow heads": 15,
                "Unfinished broad bolts": 10,
            }
        )

        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_leaping_fish", QUEST_UNLOCK_RULES),
            ("Barbarian Fishing",),
        )
        self.assertEqual(
            fletching_target_locked_reasons_pure(player_data, "broad_arrows", FLETCHING_DATA, QUEST_UNLOCK_RULES),
            ("Broad Fletching",),
        )

        player_data["unlocked_abilities"] = ["barbarian_fishing", "broad_fletching"]
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_leaping_fish", QUEST_UNLOCK_RULES),
            (),
        )
        self.assertEqual(
            fletching_target_locked_reasons_pure(player_data, "broad_arrows", FLETCHING_DATA, QUEST_UNLOCK_RULES),
            (),
        )

    def test_shilo_village_gates_current_gem_rocks_target(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "mining", "gem_rocks", QUEST_UNLOCK_RULES),
            ("Shilo Village",),
        )

        player_data["quests"]["shilo_village"] = {"started": True, "progress": 7, "completed": True}
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "mining", "gem_rocks", QUEST_UNLOCK_RULES),
            (),
        )

    def test_region_precedent_quest_locks_cover_morytania_and_neitiznot_targets(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["fishing_level"] = 99
        player_data["cooking_level"] = 99
        player_data["firemaking_level"] = 99
        player_data["inventory"].update(
            {
                "Fishing bait": 1,
                "Slimy eel": 1,
                "Thin snail": 1,
                "Raw yak meat": 1,
                "Arctic pine logs": 1,
            }
        )

        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_slimy_eel", QUEST_UNLOCK_RULES),
            ("Priest in Peril",),
        )
        self.assertEqual(
            cooking_target_locked_reasons_pure(player_data, "cook_slimy_eel", COOKING_DATA, QUEST_UNLOCK_RULES),
            ("Priest in Peril",),
        )
        self.assertEqual(
            cooking_target_locked_reasons_pure(player_data, "cook_thin_snail", COOKING_DATA, QUEST_UNLOCK_RULES),
            ("Priest in Peril",),
        )
        self.assertEqual(
            utility_activity_locked_reasons_pure(
                player_data,
                "gather_thin_snails",
                UTILITY_ACTIVITY_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Priest in Peril",),
        )
        self.assertEqual(
            firemaking_target_locked_reasons_pure(
                player_data,
                "arctic_pine_logs",
                FIREMAKING_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("The Fremennik Isles",),
        )
        self.assertEqual(
            cooking_target_locked_reasons_pure(player_data, "cook_yak", COOKING_DATA, QUEST_UNLOCK_RULES),
            ("The Fremennik Isles",),
        )
        self.assertEqual(
            utility_activity_locked_reasons_pure(
                player_data,
                "scavenge_raw_yak_meat",
                UTILITY_ACTIVITY_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("The Fremennik Isles",),
        )

        player_data["quests"]["priest_in_peril"] = {"started": True, "progress": 6, "completed": True}
        player_data["quests"]["the_fremennik_isles"] = {"started": True, "progress": 6, "completed": True}
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_slimy_eel", QUEST_UNLOCK_RULES),
            (),
        )
        self.assertEqual(
            cooking_target_locked_reasons_pure(player_data, "cook_slimy_eel", COOKING_DATA, QUEST_UNLOCK_RULES),
            (),
        )
        self.assertEqual(
            firemaking_target_locked_reasons_pure(
                player_data,
                "arctic_pine_logs",
                FIREMAKING_DATA,
                QUEST_UNLOCK_RULES,
            ),
            (),
        )
        self.assertEqual(
            utility_activity_locked_reasons_pure(
                player_data,
                "scavenge_raw_yak_meat",
                UTILITY_ACTIVITY_DATA,
                QUEST_UNLOCK_RULES,
            ),
            (),
        )

    def test_wicked_hood_claim_requires_rune_mysteries(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        rows = claim_rows_pure(player_data, CLAIM_DATA)
        self.assertEqual(rows[0]["locked_reasons"], ("quest",))

        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        claimed_data, ok = apply_claim_pure(player_data, "wicked_hood", CLAIM_DATA)
        self.assertTrue(ok)
        self.assertEqual(claimed_data["inventory"]["Wicked hood"], 1)
        self.assertTrue(claimed_data["claims"]["wicked_hood"]["claimed"])

        claimed_again, ok = apply_claim_pure(claimed_data, "wicked_hood", CLAIM_DATA)
        self.assertFalse(ok)
        self.assertEqual(claimed_again["inventory"]["Wicked hood"], 1)

    def test_quest_completion_grants_generated_item_rewards(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        data, progressed, completed = apply_quest_progress_pure(player_data, "cooks_assistant", QUEST_DATA)
        self.assertTrue(progressed)
        self.assertFalse(completed)
        data, progressed, completed = apply_quest_progress_pure(data, "cooks_assistant", QUEST_DATA)

        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertEqual(data["quest_points"], 1)
        self.assertEqual(data["inventory"]["Coins"], 500)
        self.assertEqual(data["inventory"]["Sardine"], 20)
        self.assertEqual(data["cooking_exp"], 300.0)

    def test_xp_lamp_claim_grants_chosen_skill_or_parks_unimplemented_skill(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["mining_level"] = 30
        player_data["quests"]["one_small_favour"] = {"started": True, "progress": 7, "completed": True}
        claimed_data, ok = apply_claim_pure(player_data, "one_small_favour_xp_lamp_1", CLAIM_DATA, "mining")

        self.assertTrue(ok)
        self.assertEqual(claimed_data["mining_exp"], player_data["mining_exp"] + 10000)
        self.assertTrue(claimed_data["claims"]["one_small_favour_xp_lamp_1"]["claimed"])

        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["stolen_hearts"] = {"started": True, "progress": 3, "completed": True}
        claimed_data, ok = apply_claim_pure(player_data, "stolen_hearts_xp_lamp_2", CLAIM_DATA, "agility")

        self.assertTrue(ok)
        self.assertEqual(claimed_data["pending_skill_exp_rewards"]["agility_exp"], 250.0)
        self.assertTrue(claimed_data["claims"]["stolen_hearts_xp_lamp_2"]["claimed"])

    def test_standard_runecrafting_uses_talisman_capacity_and_prefers_rune_essence(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["inventory"]["Air talisman"] = 1
        player_data["inventory"]["Rune essence"] = 30
        player_data["inventory"]["Pure essence"] = 30

        self.assertTrue(can_runecraft_target_pure(
            player_data,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        ))
        new_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "+27 Air rune")
        self.assertAlmostEqual(exp, 135.0)
        self.assertEqual(new_data["inventory"]["Rune essence"], 3)
        self.assertEqual(new_data["inventory"]["Pure essence"], 30)
        self.assertEqual(new_data["inventory"]["Air rune"], 27)

    def test_runecrafting_tiara_and_small_pouch_raise_trip_capacity(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["equipment"]["head"] = "Air tiara"
        player_data["inventory"]["Small pouch"] = 1
        player_data["inventory"]["Rune essence"] = 31

        new_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "+31 Air rune")
        self.assertAlmostEqual(exp, 155.0)
        self.assertEqual(new_data["inventory"]["Rune essence"], 0)
        self.assertEqual(new_data["inventory"]["Air rune"], 31)
        self.assertEqual(new_data["inventory"]["Small pouch"], 1)
        self.assertEqual(new_data["runecrafting_pouches"]["small"], {"degradation": 0})

    def test_combination_runecrafting_uses_binding_necklace_charge_counter(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["runecrafting_level"] = 23
        player_data["equipment"]["head"] = "Earth tiara"
        player_data["equipment"]["neck"] = "Binding necklace"
        player_data["inventory"]["Pure essence"] = 26
        player_data["inventory"]["Fire rune"] = 26
        player_data["inventory"]["Fire talisman"] = 1

        self.assertEqual(binding_necklace_charges_pure(player_data), 15)
        new_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "combo_lava_at_earth",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "+26 Lava rune")
        self.assertAlmostEqual(exp, 260.0)
        self.assertEqual(new_data["inventory"]["Pure essence"], 0)
        self.assertEqual(new_data["inventory"]["Fire rune"], 0)
        self.assertEqual(new_data["inventory"]["Fire talisman"], 0)
        self.assertEqual(new_data["inventory"]["Lava rune"], 26)
        self.assertEqual(new_data["equipment"]["neck"], "Binding necklace")
        self.assertEqual(new_data["item_charges"]["Binding necklace"], 14)

    def test_binding_necklace_breaks_at_zero_charges(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["runecrafting_level"] = 23
        player_data["equipment"]["head"] = "Earth tiara"
        player_data["equipment"]["neck"] = "Binding necklace"
        player_data["item_charges"]["Binding necklace"] = 1
        player_data["inventory"]["Pure essence"] = 1
        player_data["inventory"]["Fire rune"] = 1
        player_data["inventory"]["Fire talisman"] = 1

        new_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "combo_lava_at_earth",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "+1 Lava rune")
        self.assertAlmostEqual(exp, 10.0)
        self.assertNotIn("neck", new_data["equipment"])
        self.assertNotIn("Binding necklace", new_data["item_charges"])

    def test_wicked_hood_feed_consumes_access_item_and_unlocks_altar_capacity(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["inventory"]["Wicked hood"] = 1
        player_data["inventory"]["Air talisman"] = 1
        player_data["inventory"]["Rune essence"] = 28

        fed_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "feed_air_talisman_to_hood",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(message, "Air talisman fed")
        self.assertEqual(fed_data["inventory"]["Air talisman"], 0)
        self.assertEqual(fed_data["wicked_hood"]["fed_altars"], ["air"])

        crafted_data, exp, ok, message = apply_runecrafting_action_pure(
            fed_data,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(message, "+28 Air rune")
        self.assertAlmostEqual(exp, 140.0)
        self.assertEqual(crafted_data["inventory"]["Rune essence"], 0)
        self.assertEqual(crafted_data["inventory"]["Air rune"], 28)

    def test_firemaking_achievements_unlock_from_ashes_inventory(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"]["Ashes"] = 1

        newly_completed = get_newly_completed_achievements(player_data, ACHIEVEMENTS)

        self.assertIn("First Fire", newly_completed)

    def test_bank_gear_rows_shows_active_tool_not_just_bound(self):
        # Owns a rune pickaxe in the bank; only bronze is bound. Since the
        # toolbelt is auto-resolved, the Bank should surface the rune pickaxe
        # (the tool actually used) once the player can use it.
        pd = {
            "mining_level": 41,
            "woodcutting_level": 1,
            "inventory": {"Rune pickaxe": 1},
            "toolbelt": {"mining": ["bronze_pickaxe"], "woodcutting": ["bronze_hatchet"]},
            "equipment": {},
        }
        gear = bank_gear_rows_pure(pd, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA, MINING_BONUS_ITEM_DATA)
        pick = dict(gear["toolbelt"])
        self.assertEqual(pick["Pickaxe"], "Rune pickaxe")
        self.assertEqual(pick["Hatchet"], "Bronze hatchet")
        self.assertEqual(gear["equipped"], [])

    def test_bank_gear_rows_lists_equipped_with_slot(self):
        bonus_id = next(iter(MINING_BONUS_ITEM_DATA))
        pd = {
            "mining_level": 1,
            "woodcutting_level": 1,
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"], "woodcutting": ["bronze_hatchet"]},
            "equipment": {"neck": MINING_BONUS_ITEM_DATA[bonus_id]["display_name"]},
        }
        gear = bank_gear_rows_pure(pd, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA, MINING_BONUS_ITEM_DATA)
        self.assertEqual(len(gear["equipped"]), 1)
        slot, name = gear["equipped"][0]
        self.assertEqual(slot, "neck")
        self.assertEqual(name, MINING_BONUS_ITEM_DATA[bonus_id]["display_name"])

if __name__ == "__main__":
    unittest.main()
