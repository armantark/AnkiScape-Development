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
    apply_firemaking_action_pure,
    apply_smelt_pure,
    apply_smithing_pure,
    apply_woodcutting_pure,
    apply_woodcutting_action_pure,
    apply_mining_pure,
    apply_mining_action_pure,
    apply_open_bird_nests_pure,
    best_woodcutting_axe_pure,
    best_mining_pickaxe_pure,
    bank_gear_rows_pure,
    equipment_bonus_state_pure,
    can_equip_item_pure,
    equip_item_pure,
    unequip_item_pure,
    equipment_stat_totals_pure,
    calculate_woodcutting_success_probability_pure,
    calculate_mining_success_probability_pure,
    can_mine_ore_pure,
    can_cut_tree_pure,
    can_craft_item_pure,
    can_fletch_item_pure,
    can_burn_any_firemaking_target_pure,
    can_burn_firemaking_target_pure,
    calculate_firemaking_success_probability_pure,
    firemaking_source_roll_chance_pure,
    can_perform_utility_activity_pure,
    sanitize_review_action_multiplier,
)
from storage_pure import default_player_data
from constants import (
    ACHIEVEMENTS,
    GLORY_GEM_DROP_CHANCE,
    INCIDENTAL_GEM_DROP_TABLE,
    ITEM_DEFINITIONS,
    MINING_BONUS_ITEM_DATA,
    MINING_PICKAXE_DATA,
    WOODCUTTING_AXE_DATA,
    ORE_DATA,
    EQUIPMENT_DATA,
    FIREMAKING_DATA,
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
