import dataclasses
import unittest
from unittest.mock import patch

import runtime_actions

from runtime_actions import (
    RuntimeActionContext,
    answer_handler_for_key,
    can_start_action,
    handle_cooking_answer,
    handle_combat_answer,
    handle_crafting_answer,
    handle_firemaking_answer,
    handle_fishing_answer,
    handle_fletching_answer,
    handle_hunter_answer,
    handle_agility_answer,
    handle_herblore_answer,
    handle_quest_answer,
    handle_smithing_answer,
    handle_woodcutting_answer,
    run_answer_with_carried_overlay,
)


def _context(player_data, calls=None, random_values=None, review_action_multiplier=1):
    calls = calls if calls is not None else {"xp": [], "saves": 0, "errors": []}
    random_iter = iter(random_values or ())

    def award_skill_exp(exp_key, base_exp):
        player_data[exp_key] = player_data.get(exp_key, 0) + base_exp
        return base_exp

    def random_random():
        try:
            return next(random_iter)
        except StopIteration:
            return 0.0

    return RuntimeActionContext(
        player_data=player_data,
        random_random=random_random,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.setdefault("deactivated", True),
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda exp_key, _level_key, base_exp: player_data.__setitem__(
            exp_key,
            player_data.get(exp_key, 0) + base_exp,
        ),
        level_up_check=lambda _skill, _data: calls.setdefault("level_checks", []).append(_skill),
        check_achievements=lambda _data: calls.setdefault("achievement_checks", 0),
        save_player_data=lambda: calls.__setitem__("saves", calls.get("saves", 0) + 1),
        refresh_skill_availability=lambda: calls.setdefault("refreshes", 0),
        refresh_skill_availability_partial=lambda *_args: calls.setdefault("partial_refreshes", 0),
        can_smith_any=lambda: False,
        show_exp=lambda exp: calls["xp"].append(exp),
        show_activity_gain=lambda text: calls.setdefault("activity", []).append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
        review_action_multiplier=review_action_multiplier,
    )


def _quest_combat_mid_rolls(repeats=1000):
    return (0.5,) * repeats


class TestRuntimeActions(unittest.TestCase):
    def test_fatal_agility_failure_deactivates_and_reports_shared_grave_death(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "agility_exp": 0.0,
            "combat_lifepoints": 10,
            "hitpoints_level": 10,
            "inventory": {},
            "equipment": {"weapon": "Bronze sword"},
            "completed_achievements": [],
        }

        self.assertTrue(handle_agility_answer(_context(player_data, calls, random_values=(0.0, 0.5, 0.5, 0.5))))

        self.assertTrue(calls["deactivated"])
        self.assertEqual(player_data["combat_grave"]["items"], ["Bronze sword"])
        self.assertEqual(player_data["combat_grave"]["source"], "agility_failure")
        self.assertTrue(any("YOU DIED" in text for text in calls["activity"]))

    def test_barehanded_butterfly_awards_atomic_hunter_and_agility_xp_without_an_item(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "hunter_level": 80,
            "hunter_exp": 0.0,
            "agility_level": 75,
            "agility_exp": 0.0,
            "current_hunter": "barehand_ruby_harvest",
            "completed_achievements": [],
        }

        self.assertTrue(handle_hunter_answer(_context(player_data, calls, random_values=(0.0,))))

        self.assertEqual(player_data["inventory"], {})
        self.assertEqual(player_data["hunter_exp"], 300.0)
        self.assertEqual(player_data["agility_exp"], 50.0)
        self.assertEqual(calls["xp"], [300.0])

    def test_agility_double_catch_adds_one_shark_without_extra_fishing_xp(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "fishing_level": 99,
            "fishing_exp": 0.0,
            "agility_level": 76,
            "current_fishing": "catch_sharks",
            "completed_achievements": [],
        }

        self.assertTrue(handle_fishing_answer(_context(player_data, calls, random_values=(0.0, 0.0))))

        self.assertEqual(player_data["inventory"], {"Raw shark": 2})
        self.assertEqual(player_data["fishing_exp"], 110.0)
        self.assertEqual(calls["xp"], [110.0])
        telemetry = player_data["action_telemetry"]["actions"]["fishing:catch_sharks"]
        self.assertEqual(telemetry["outputs"], {"Raw shark": 2})

    def test_overload_handler_records_primary_output_and_four_vials(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        inputs = {
            "Extreme attack (3)": 1,
            "Extreme strength (3)": 1,
            "Extreme defence (3)": 1,
            "Extreme magic (3)": 1,
            "Extreme ranging (3)": 1,
            "Clean torstol": 1,
        }
        player_data = {
            "inventory": inputs,
            "herblore_level": 96,
            "herblore_exp": 0.0,
            "current_herblore": "finished_overload",
            "completed_achievements": [],
        }

        self.assertTrue(handle_herblore_answer(_context(player_data, calls)))

        self.assertEqual(player_data["inventory"]["Overload (3)"], 1)
        self.assertEqual(player_data["inventory"]["Vial"], 4)
        self.assertEqual(player_data["herblore_exp"], 1000.0)
        telemetry = player_data["action_telemetry"]["actions"]["herblore:finished_overload"]
        self.assertEqual(telemetry["outputs"], {"Overload (3)": 1, "Vial": 4})
        self.assertEqual(calls["xp"], [1000.0])

    def test_super_prayer_recipe_consumes_only_wyvern_bonemeal(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {
                "Prayer potion (3)": 1,
                "Wyvern bonemeal": 1,
                "Bonemeal": 7,
            },
            "herblore_level": 94,
            "herblore_exp": 0.0,
            "current_herblore": "finished_super_prayer",
            "completed_achievements": [],
        }

        self.assertTrue(handle_herblore_answer(_context(player_data, calls)))

        self.assertEqual(player_data["inventory"]["Prayer potion (3)"], 0)
        self.assertEqual(player_data["inventory"]["Wyvern bonemeal"], 0)
        self.assertEqual(player_data["inventory"]["Bonemeal"], 7)
        self.assertEqual(player_data["inventory"]["Super prayer (3)"], 1)
        self.assertEqual(player_data["herblore_exp"], 270.0)
        telemetry = player_data["action_telemetry"]["actions"]["herblore:finished_super_prayer"]
        self.assertEqual(telemetry["outputs"], {"Super prayer (3)": 1})
        self.assertEqual(calls["xp"], [270.0])

    def test_woodcutting_inferno_adze_incinerates_logs_for_firemaking_xp(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Inferno adze": 1},
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "firemaking_exp": 0.0,
            "current_tree": "tree",
            "completed_achievements": [],
        }

        ok = handle_woodcutting_answer(_context(player_data, calls, random_values=(0.0, 1.0, 0.0, 0.0)))

        self.assertTrue(ok)
        self.assertNotIn("Logs", player_data["inventory"])
        self.assertEqual(player_data["woodcutting_exp"], 25.0)
        self.assertEqual(player_data["firemaking_exp"], 25.0)
        self.assertEqual(calls["level_checks"], ["Woodcutting", "Firemaking"])

    def test_fletching_handler_mutates_player_data_through_context(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        ok = handle_fletching_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Logs"], 0)
        self.assertEqual(player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(player_data["fletching_exp"], 5.0)
        telemetry = player_data["action_telemetry"]["actions"]["fletching:arrow_shafts"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(telemetry["outputs"], {"Arrow shafts": 15})
        self.assertAlmostEqual(telemetry["expected_successes"], 1.0)
        self.assertEqual(calls["xp"], [5.0])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])

    def test_fletching_handler_and_carried_overlay_consume_selected_coloured_feathers(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Arrow shafts": 30, "Feather": 30, "Blue feather": 30},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "headless_arrows",
            "completed_achievements": [],
            "carried_advanced_targets": {"headless_arrows": True},
            "carried_layout": {"headless_arrows": {"Arrow shafts": 15, "Blue feather": 15}},
        }

        ok = run_answer_with_carried_overlay(
            _context(player_data, calls),
            "fletching",
            handle_fletching_answer,
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Arrow shafts"], 15)
        self.assertEqual(player_data["inventory"]["Feather"], 30)
        self.assertEqual(player_data["inventory"]["Blue feather"], 15)
        self.assertEqual(player_data["inventory"]["Headless arrows"], 15)
        self.assertNotIn("headless_arrows", player_data["carried_inventory"])
        self.assertAlmostEqual(player_data["fletching_exp"], 15.0)
        self.assertNotIn("activity", calls)
        self.assertEqual(player_data["skilling_bank_run"], {})

    def test_crafting_handler_and_carried_overlay_reconcile_thread_consumption(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leather": 1, "Thread": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "leather_leather_gloves",
            "completed_achievements": [],
            "carried_advanced_targets": {"leather_leather_gloves": True},
            "carried_layout": {"leather_leather_gloves": {"Leather": 1, "Thread": 1}},
        }

        ok = run_answer_with_carried_overlay(
            _context(player_data, calls, random_values=(0.0,)),
            "crafting",
            handle_crafting_answer,
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"], {"Leather": 0, "Thread": 0, "Leather gloves": 1})
        self.assertNotIn("leather_leather_gloves", player_data["carried_inventory"])
        self.assertAlmostEqual(player_data["crafting_exp"], 13.8)
        self.assertEqual(calls["errors"], [])

    def test_crafting_carried_overlay_requires_and_retains_mould(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Gold bar": 1, "Ring mould": 1},
            "crafting_level": 5,
            "crafting_exp": 0,
            "current_craft": "jewellery_gold_ring",
            "completed_achievements": [],
            "carried_advanced_targets": {"jewellery_gold_ring": True},
            "carried_layout": {"jewellery_gold_ring": {"Gold bar": 1, "Ring mould": 1}},
        }

        self.assertTrue(run_answer_with_carried_overlay(
            _context(player_data, calls), "crafting", handle_crafting_answer
        ))
        self.assertEqual(player_data["inventory"], {"Gold bar": 0, "Ring mould": 1, "Gold ring": 1})
        self.assertEqual(player_data["carried_inventory"]["jewellery_gold_ring"], {"Ring mould": 1})
        self.assertAlmostEqual(player_data["crafting_exp"], 15.0)

    def test_cannonball_advanced_pack_carries_and_retains_ammo_mould(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Steel bar": 1, "Ammo mould": 1},
            "smithing_level": 35,
            "smithing_exp": 0.0,
            "crafting_level": 1,
            "current_smith": "forge_cannonballs",
            "quests": {"dwarf_cannon": {"completed": True}},
            "completed_achievements": [],
            "carried_advanced_targets": {"forge_cannonballs": True},
            "carried_layout": {"forge_cannonballs": {"Steel bar": 1, "Ammo mould": 1}},
        }
        ctx = _context(player_data, calls)

        self.assertTrue(run_answer_with_carried_overlay(ctx, "smithing", handle_smithing_answer))

        self.assertEqual(player_data["inventory"], {"Steel bar": 0, "Ammo mould": 1, "Cannonball": 4})
        self.assertEqual(player_data["carried_inventory"]["forge_cannonballs"], {"Ammo mould": 1})
        self.assertAlmostEqual(player_data["smithing_exp"], 25.6)
        self.assertEqual(calls["errors"], [])

    def test_unfired_clay_ring_carried_overlay_reconciles_and_retains_mould(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Soft clay": 1, "Ring mould": 1},
            "crafting_level": 4,
            "crafting_exp": 0,
            "current_craft": "form_clay_ring_unfired",
            "completed_achievements": [],
            "carried_advanced_targets": {"form_clay_ring_unfired": True},
            "carried_layout": {"form_clay_ring_unfired": {"Soft clay": 1, "Ring mould": 1}},
        }

        self.assertTrue(run_answer_with_carried_overlay(
            _context(player_data, calls), "crafting", handle_crafting_answer
        ))
        self.assertEqual(
            player_data["inventory"], {"Soft clay": 0, "Ring mould": 1, "Clay ring (unfired)": 1}
        )
        self.assertEqual(player_data["carried_inventory"]["form_clay_ring_unfired"], {"Ring mould": 1})
        self.assertAlmostEqual(player_data["crafting_exp"], 11.3)
        self.assertEqual(calls["errors"], [])

    def test_crafting_carried_overlay_retains_one_thread_across_leather_actions(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leather": 27, "Thread": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "leather_leather_gloves",
            "completed_achievements": [],
            "carried_advanced_targets": {"leather_leather_gloves": True},
            "carried_layout": {"leather_leather_gloves": {"Leather": 27, "Thread": 1}},
        }
        ctx = _context(player_data, calls, random_values=(0.2, 0.2))

        self.assertTrue(run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer))
        self.assertEqual(player_data["carried_inventory"]["leather_leather_gloves"], {"Leather": 26, "Thread": 1})
        self.assertTrue(run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer))

        self.assertEqual(player_data["inventory"], {"Leather": 25, "Thread": 1, "Leather gloves": 2})
        self.assertEqual(player_data["carried_inventory"]["leather_leather_gloves"], {"Leather": 25, "Thread": 1})
        self.assertNotIn("activity", calls)
        self.assertEqual(calls["errors"], [])

    def test_crafting_advanced_layout_refills_consumed_thread_from_bank_before_resuming(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leather": 27, "Thread": 5},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "leather_leather_gloves",
            "completed_achievements": [],
            "carried_advanced_targets": {"leather_leather_gloves": True},
            "carried_layout": {"leather_leather_gloves": {"Leather": 27, "Thread": 1}},
        }
        ctx = _context(player_data, calls, random_values=(0.0, 0.2))

        # The first source roll consumes the carried Thread. Crafting is a
        # stationary bank method, so the next review repacks and crafts in one
        # atomic action instead of inventing a movement review.
        self.assertTrue(run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer))
        self.assertEqual(player_data["inventory"], {"Leather": 26, "Thread": 4, "Leather gloves": 1})
        self.assertEqual(player_data["carried_inventory"]["leather_leather_gloves"], {"Leather": 26})
        self.assertTrue(run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer))
        self.assertEqual(player_data["inventory"], {"Leather": 25, "Thread": 4, "Leather gloves": 2})
        self.assertEqual(player_data["carried_inventory"]["leather_leather_gloves"], {"Leather": 25, "Thread": 1})
        self.assertAlmostEqual(player_data["crafting_exp"], 27.6)
        self.assertEqual(calls["xp"], [13.8, 13.8])
        self.assertNotIn("activity", calls)
        self.assertNotIn("deactivated", calls)
        self.assertEqual(calls["errors"], [])

    def test_combat_full_loot_pack_forces_a_bank_run_that_deposits_it(self):
        # A full carried loot pack (28 slots) forces a bank run: the answer banks
        # instead of fighting, the loot is deposited (view cleared, but the items
        # stay in the flat inventory), and no kill happens this answer.
        full_loot = {f"Trophy {i}": 1 for i in range(28)}
        player_data = {
            "inventory": dict(full_loot),
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "constitution_exp": 0.0,
            "carried_inventory": {"chicken": dict(full_loot)},
            "completed_achievements": [],
        }
        calls = {"xp": [], "saves": 0, "errors": []}
        # The combat bank run costs two review answers; the loot deposits on
        # completion, and no kill happens while banking.
        handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))
        self.assertEqual(player_data.get("carried_inventory", {}).get("chicken"), dict(full_loot))
        handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))

        # Loot deposited: view cleared, items still banked, no kill credited.
        self.assertIsNone(player_data.get("carried_inventory", {}).get("chicken"))
        self.assertEqual(player_data["inventory"]["Trophy 0"], 1)
        self.assertEqual(player_data.get("combat_kill_counts", {}).get("chicken", 0), 0)

    def test_stackable_loot_counts_as_one_slot_and_does_not_prematurely_bank(self):
        # A huge feather stack (stackable) occupies a single slot, so it must not
        # trigger a bank run the way 28 distinct unstackables would.
        player_data = {
            "inventory": {"Feather": 2_000_000},
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "constitution_exp": 0.0,
            "carried_inventory": {"chicken": {"Feather": 2_000_000}},
            "completed_achievements": [],
        }
        calls = {"xp": [], "saves": 0, "errors": []}
        handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))
        # No bank run: the fight happened this answer (a kill was credited).
        self.assertEqual(player_data.get("combat_kill_counts", {}).get("chicken", 0), 1)

    def test_combat_handler_runs_review_burst_and_records_drops(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["combat_kill_counts"], {"chicken": 1})
        self.assertGreater(player_data["attack_exp"], 0.0)
        self.assertGreater(player_data["constitution_exp"], 0.0)
        # Loot filter: Bones (value 1, unstackable) fall below the default
        # threshold and are left; Raw chicken (value 60) is kept; Feathers are
        # stackable so always kept.
        self.assertEqual(player_data["inventory"].get("Bones", 0), 0)
        self.assertEqual(player_data["inventory"]["Raw chicken"], 1)
        self.assertEqual(player_data["inventory"]["Feather"], 5)
        # Kept loot also folds into the combat target's carried view (it competes
        # for slots and drops on death); coins would be excluded.
        self.assertEqual(player_data["carried_inventory"]["chicken"], {"Raw chicken": 1, "Feather": 5})
        telemetry = player_data["action_telemetry"]["actions"]["combat:chicken"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["successes"], 1)
        # Telemetry records the loot actually kept (Bones were filtered out).
        self.assertEqual(telemetry["outputs"], {"Raw chicken": 1, "Feather": 5})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Chicken"])
        self.assertEqual(len(calls["xp"]), 1)

    def test_fatal_combat_burst_graves_loot_earned_before_death(self):
        enemy = {
            "display_name": "Fatal looter",
            "level": 99,
            "group": "Test",
            "stats": {"attack": 99, "strength": 99, "defence": 1, "hitpoints": 1},
            "bonuses": {},
            "attack_speed": 1,
            "drops": {"guaranteed": (("Feather", 1),), "tables": ()},
            "source": "test",
        }
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "fatal_looter",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 1,
            "combat_auto_flee": False,
            "combat_auto_eat_food": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 1,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }
        calls = {"xp": [], "saves": 0, "errors": []}

        with patch.dict(runtime_actions.COMBAT_ENEMY_DATA, {"fatal_looter": enemy}):
            ok = handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0, 0.999999]))

        self.assertTrue(ok)
        self.assertTrue(player_data["combat_last_result"]["died"])
        self.assertEqual(player_data["combat_last_result"]["kills"], 1)
        self.assertIn("Feather", player_data["combat_grave"]["items"])
        self.assertEqual(player_data["inventory"].get("Feather", 0), 0)
        self.assertNotIn("fatal_looter", player_data.get("carried_inventory", {}))

    def test_combat_handler_runs_ranged_review_with_starter_bow_and_arrows(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Shortbow"},
            "current_combat_target": "chicken",
            "combat_attack_style": "ranged_accurate",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {"ammo": {"Bronze arrows": 2}},
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "ranged_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "ranged_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["combat_kill_counts"], {"chicken": 1})
        self.assertEqual(player_data["inventory"].get("Bronze arrows", 0), 0)
        # Chain kills keep firing after the first kill within the tick budget, so
        # the second carried arrow is spent on the follow-up shot too.
        self.assertEqual(player_data["combat_supply_loadout"]["ammo"], {})
        self.assertEqual(player_data["attack_exp"], 0.0)
        self.assertGreater(player_data["ranged_exp"], 0.0)
        self.assertGreater(player_data["constitution_exp"], 0.0)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Chicken"])

    def test_combat_handler_runs_magic_review_with_wind_strike_runes(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Staff"},
            "current_combat_target": "chicken",
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "wind_strike",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {"runes": {"Air rune": 1, "Mind rune": 1}},
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "ranged_level": 1,
            "magic_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "ranged_exp": 0.0,
            "magic_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls, [0.999999]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"].get("Air rune", 0), 0)
        self.assertEqual(player_data["inventory"].get("Mind rune", 0), 0)
        self.assertEqual(player_data["combat_supply_loadout"]["runes"], {})
        self.assertEqual(player_data["combat_last_result"]["combat_class"], "magic")
        self.assertEqual(player_data["combat_last_result"]["spell"], "Wind Strike")
        self.assertEqual(player_data["combat_last_result"]["stop_reason"], "out_of_runes")
        self.assertAlmostEqual(player_data["magic_exp"], 5.5)
        self.assertEqual(player_data["constitution_exp"], 0.0)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["xp"], [5.5])
        self.assertEqual(calls["activity"], ["Chicken: 0 damage dealt, 30 LP left"])

    def test_combat_handler_uses_staff_substitution_for_magic_runes(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Staff of air"},
            "current_combat_target": "chicken",
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "wind_strike",
            "combat_lifepoints": 100,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {"runes": {"Mind rune": 1}},
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "ranged_level": 1,
            "magic_level": 99,
            "constitution_level": 10,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "ranged_exp": 0.0,
            "magic_exp": 0.0,
            "constitution_exp": 0.0,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls, [0.999999]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"].get("Air rune", 0), 0)
        self.assertEqual(player_data["inventory"].get("Mind rune", 0), 0)
        self.assertEqual(player_data["combat_supply_loadout"]["runes"], {})
        self.assertEqual(player_data["combat_last_result"]["runes_used"], {"Mind rune": 1})
        self.assertAlmostEqual(player_data["magic_exp"], 5.5)
        self.assertEqual(calls["errors"], [])

    def test_combat_handler_deactivates_magic_without_runes(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Staff"},
            "current_combat_target": "chicken",
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "wind_strike",
            "combat_lifepoints": 100,
            "magic_level": 99,
            "constitution_level": 10,
            "completed_achievements": [],
        }

        ok = handle_combat_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["saves"], 0)
        self.assertEqual(calls["errors"][0][0], "Combat unavailable")
        self.assertIn("Air rune x1", calls["errors"][0][1])
        self.assertIn("Mind rune x1", calls["errors"][0][1])

    def test_handler_key_registry_and_readiness_share_runtime_module(self):
        self.assertIs(answer_handler_for_key("fletching"), handle_fletching_answer)
        self.assertIs(answer_handler_for_key("hunter"), handle_hunter_answer)
        self.assertIs(answer_handler_for_key("combat"), handle_combat_answer)

        player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "current_fletch": "arrow_shafts",
        }
        self.assertTrue(can_start_action(_context(player_data), "fletching"))

        player_data["inventory"] = {}
        self.assertFalse(can_start_action(_context(player_data), "fletching"))

        combat_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "combat_lifepoints": 100,
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "constitution_level": 10,
        }
        self.assertTrue(can_start_action(_context(combat_data), "combat"))
        combat_data.update(
            {
                "inventory": {"Bronze arrows": 1},
                "equipment": {"weapon": "Shortbow"},
                "combat_attack_style": "ranged_accurate",
                "ranged_level": 1,
            }
        )
        self.assertTrue(can_start_action(_context(combat_data), "combat"))
        combat_data["inventory"] = {}
        self.assertFalse(can_start_action(_context(combat_data), "combat"))
        combat_data.update(
            {
                "combat_attack_style": "magic_standard",
                "equipment": {"weapon": "Staff"},
                "inventory": {"Air rune": 1, "Mind rune": 1},
                "magic_level": 1,
                "current_combat_spell": "wind_strike",
            }
        )
        self.assertTrue(can_start_action(_context(combat_data), "combat"))
        combat_data["inventory"] = {}
        self.assertFalse(can_start_action(_context(combat_data), "combat"))
        combat_data.update(
            {
                "equipment": {"weapon": "Staff of air"},
                "inventory": {"Mind rune": 1},
            }
        )
        self.assertTrue(can_start_action(_context(combat_data), "combat"))
        self.assertTrue(can_start_action(_context(player_data), "unknown"))

        hunter_data = {
            "inventory": {"Logs": 1},
            "hunter_level": 23,
            "current_hunter": "catch_wild_kebbit",
        }
        self.assertTrue(can_start_action(_context(hunter_data), "hunter"))

        hunter_data["inventory"] = {}
        self.assertFalse(can_start_action(_context(hunter_data), "hunter"))

    def test_quest_completion_warns_and_switches_off(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Research notes": 1},
            "current_quest": "rune_mysteries",
            "quests": {"rune_mysteries": {"started": True, "progress": 5, "completed": False}},
            "quest_stage_actions": {"rune_mysteries": ["Return Aubury's research notes to Sedridor"]},
            "quest_points": 0,
            "runecrafting_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertTrue(player_data["quests"]["rune_mysteries"]["completed"])
        self.assertEqual(player_data["inventory"]["Air talisman"], 1)
        self.assertEqual(player_data["inventory"]["Research notes"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["activity"], ["Rune Mysteries complete"])
        self.assertEqual(calls["errors"][0][0], "Quest complete")
        self.assertIn("Rune Mysteries is complete", calls["errors"][0][1])
        self.assertIn("questing has been switched off", calls["errors"][0][1])

    def test_quest_answer_runs_the_final_tears_of_guthix_stage_before_completion(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Bullseye lantern (empty)": 1, "Sapphire": 1},
            "current_quest": "tears_of_guthix",
            "quests": {"tears_of_guthix": {"started": True, "progress": 2, "completed": False}},
            "quest_stage_actions": {
                "tears_of_guthix": ["Complete Tears of Guthix stage 2 objective"]
            },
            "quest_points": 0,
            "crafting_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        self.assertTrue(handle_quest_answer(_context(player_data, calls)))
        self.assertEqual(player_data["quests"]["tears_of_guthix"]["progress"], 3)
        self.assertFalse(player_data["quests"]["tears_of_guthix"]["completed"])
        self.assertNotIn("deactivated", calls)
        self.assertEqual(calls["activity"], ["Tears of Guthix 3/4"])

        self.assertFalse(handle_quest_answer(_context(player_data, calls)))
        self.assertTrue(calls["deactivated"])
        self.assertEqual(player_data["quests"]["tears_of_guthix"]["progress"], 3)
        self.assertIn("Needs Sapphire lantern (lit) x1", calls["errors"][-1][1])

        player_data["inventory"]["Sapphire lantern (lit)"] = 1
        player_data["quest_stage_actions"]["tears_of_guthix"].append(
            "Complete Tears of Guthix stage 3 objective"
        )
        self.assertTrue(handle_quest_answer(_context(player_data, calls)))
        self.assertTrue(player_data["quests"]["tears_of_guthix"]["completed"])
        self.assertEqual(player_data["quests"]["tears_of_guthix"]["progress"], 4)
        self.assertEqual(player_data["crafting_exp"], 1000.0)
        self.assertEqual(calls["activity"][-1], "Tears of Guthix complete")

    def test_quest_stage_blocker_deactivates_without_progress_or_reward(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "the_knights_sword",
            "quests": {"the_knights_sword": {"started": True, "progress": 2, "completed": False}},
            "quest_points": 0,
            "smithing_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["the_knights_sword"]["progress"], 2)
        self.assertFalse(player_data["quests"]["the_knights_sword"]["completed"])
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["smithing_exp"], 0)
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Redberry pie x1", calls["errors"][0][1])

    def test_quest_choice_blocker_deactivates_without_progress_or_reward(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "shield_of_arrav",
            "quests": {"shield_of_arrav": {"started": True, "progress": 4, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["shield_of_arrav"]["progress"], 4)
        self.assertFalse(player_data["quests"]["shield_of_arrav"]["completed"])
        self.assertEqual(player_data["quest_points"], 0)
        self.assertNotIn("quest_route_states", player_data)
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Choose path: Phoenix Gang or Black Arm Gang", calls["errors"][0][1])

    def test_quest_answer_blocks_witchs_house_mouse_puzzle_without_stage_item(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Magnet": 1},
            "current_quest": "witchs_house",
            "quests": {"witchs_house": {"started": True, "progress": 4, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["witchs_house"]["progress"], 4)
        self.assertFalse(player_data["quests"]["witchs_house"]["completed"])
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Cheese x1", calls["errors"][0][1])
        self.assertIn("Use cheese on the mouse hole", calls["errors"][0][1])

    def test_quest_answer_blocks_biohazard_guidor_without_priest_gown(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {
                "Liquid honey": 1,
                "Ethenea": 1,
                "Sulphuric broline": 1,
                "Plague sample": 1,
                "Touch paper": 1,
            },
            "current_quest": "biohazard",
            "quests": {"biohazard": {"started": True, "progress": 11, "completed": False}},
            "quest_route_states": {
                "biohazard": ["Reach Guidor's house without Varrock guards confiscating the vials"]
            },
            "quest_stage_actions": {
                "biohazard": [
                    "Give sulphuric broline to Hops",
                    "Give ethenea to Da Vinci",
                    "Give liquid honey to Chancy",
                    "Collect the sulphuric broline from Hops in Varrock",
                    "Collect the ethenea from Da Vinci in Varrock",
                    "Collect the liquid honey from Chancy in Varrock",
                    "Enter Guidor's room wearing priest gowns",
                    "Give Guidor the vials, plague sample, and touch paper",
                ]
            },
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 11)
        self.assertFalse(player_data["quests"]["biohazard"]["completed"])
        self.assertEqual(player_data["inventory"]["Liquid honey"], 1)
        self.assertEqual(player_data["inventory"]["Touch paper"], 1)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Priest gown x2", calls["errors"][0][1])

    def test_quest_answer_blocks_heroes_final_without_fire_feather(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Lava eel": 1, "Thieves' armband": 1},
            "current_quest": "heroes_quest",
            "quests": {"heroes_quest": {"started": True, "progress": 12, "completed": False}},
            "quest_stage_actions": {
                "heroes_quest": ["Hand Achietties the Lava eel, Thieves' armband, and Fire feather"]
            },
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["heroes_quest"]["progress"], 12)
        self.assertFalse(player_data["quests"]["heroes_quest"]["completed"])
        self.assertEqual(player_data["inventory"]["Lava eel"], 1)
        self.assertEqual(player_data["inventory"]["Thieves' armband"], 1)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Fire feather x1", calls["errors"][0][1])

    def test_quest_answer_blocks_family_crest_jewellery_without_two_rubies(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {
                "Perfect gold bar": 2,
                "Ruby": 1,
                "Ring mould": 1,
                "Necklace mould": 1,
            },
            "current_quest": "family_crest",
            "quests": {"family_crest": {"started": True, "progress": 10, "completed": False}},
            "quest_stage_actions": {
                "family_crest": ["Craft the perfect ruby ring and perfect ruby necklace"]
            },
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["family_crest"]["progress"], 10)
        self.assertFalse(player_data["quests"]["family_crest"]["completed"])
        self.assertEqual(player_data["inventory"]["Perfect gold bar"], 2)
        self.assertEqual(player_data["inventory"]["Ruby"], 1)
        self.assertEqual(player_data["inventory"].get("Perfect ruby ring", 0), 0)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Ruby x2", calls["errors"][0][1])

    def test_quest_answer_blocks_temple_of_ikov_fire_warrior_without_bow_option(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Ice arrows": 1},
            "current_quest": "temple_of_ikov",
            "quests": {"temple_of_ikov": {"started": True, "progress": 7, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["temple_of_ikov"]["progress"], 7)
        self.assertFalse(player_data["quests"]["temple_of_ikov"]["completed"])
        self.assertEqual(player_data["inventory"]["Ice arrows"], 1)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(calls["saves"], 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Needs Yew shortbow x1 or Yew longbow x1", calls["errors"][0][1])

    def test_quest_stage_progress_accepts_required_tools_from_equipment(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"body": "Iron chainbody", "head": "Bronze med helm"},
            "current_quest": "black_knights_fortress",
            "quests": {"black_knights_fortress": {"started": True, "progress": 1, "completed": False}},
            "quest_stage_actions": {"black_knights_fortress": ["Infiltrate the Black Knights' Fortress"]},
            "quest_points": 12,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["black_knights_fortress"]["progress"], 2)
        self.assertFalse(player_data["quests"]["black_knights_fortress"]["completed"])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Black Knights' Fortress 2/5"])

    def test_quest_answer_progresses_dwarf_cannon_repairs_without_goblin_gate(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Hammer": 1},
            "current_quest": "dwarf_cannon",
            "quests": {"dwarf_cannon": {"started": True, "progress": 1, "completed": False}},
            "quest_stage_actions": {"dwarf_cannon": ["Accept replacement railings from Captain Lawgof"]},
            "quest_points": 0,
            "crafting_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["dwarf_cannon"]["progress"], 2)
        self.assertFalse(player_data["quests"]["dwarf_cannon"]["completed"])
        self.assertEqual(player_data["inventory"]["Railing"], 6)
        self.assertEqual(player_data["inventory"]["Hammer"], 1)
        self.assertEqual(player_data["quest_combat_encounters"], {})
        self.assertEqual(player_data["quest_combat_encounter_counts"], {})
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["crafting_exp"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Dwarf Cannon 2/14"])

        calls = {"xp": [], "saves": 0, "errors": []}
        player_data["quest_stage_actions"] = {"dwarf_cannon": []}

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["dwarf_cannon"]["progress"], 3)
        self.assertEqual(player_data["inventory"]["Railing"], 0)
        self.assertEqual(player_data["inventory"]["Hammer"], 1)
        self.assertEqual(calls["activity"], ["Dwarf Cannon 3/14"])

    def test_quest_answer_blocks_and_progresses_fishing_contest_pass_gate(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "fishing_contest",
            "quests": {"fishing_contest": {"started": True, "progress": 1, "completed": False}},
            "quest_points": 0,
            "fishing_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["fishing_contest"]["progress"], 1)
        self.assertEqual(player_data["inventory"], {})
        self.assertEqual(player_data["fishing_exp"], 0)
        self.assertEqual(calls["saves"], 0)
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Receive a fishing pass from Austri or Vestri", calls["errors"][0][1])

        calls = {"xp": [], "saves": 0, "errors": []}
        player_data["quest_stage_actions"] = {
            "fishing_contest": ["Receive a fishing pass from Austri or Vestri"]
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertFalse(player_data["quests"]["fishing_contest"]["completed"])
        self.assertEqual(player_data["quests"]["fishing_contest"]["progress"], 2)
        self.assertEqual(player_data["inventory"]["Fishing pass"], 1)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(player_data["fishing_exp"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Fishing Contest 2/7"])

    def test_quest_answer_blocks_and_progresses_sheep_herder_feed_gate(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "sheep_herder",
            "quests": {"sheep_herder": {"started": True, "progress": 1, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["sheep_herder"]["progress"], 1)
        self.assertEqual(player_data["inventory"], {})
        self.assertEqual(calls["saves"], 0)
        self.assertEqual(calls["errors"][0][0], "Quest blocked")
        self.assertIn("Accept poisoned sheep feed from Councillor Halgrive", calls["errors"][0][1])

        calls = {"xp": [], "saves": 0, "errors": []}
        player_data["quest_stage_actions"] = {
            "sheep_herder": ["Accept poisoned sheep feed from Councillor Halgrive"]
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertFalse(player_data["quests"]["sheep_herder"]["completed"])
        self.assertEqual(player_data["quests"]["sheep_herder"]["progress"], 2)
        self.assertEqual(player_data["inventory"]["Sheep feed"], 1)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Sheep Herder 2/6"])

    def test_quest_answer_progresses_waterfall_book_gate(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "waterfall_quest",
            "quests": {"waterfall_quest": {"started": True, "progress": 2, "completed": False}},
            "quest_stage_actions": {"waterfall_quest": ["Search the Baxtorian bookcase", "Read the Book on Baxtorian"]},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertFalse(player_data["quests"]["waterfall_quest"]["completed"])
        self.assertEqual(player_data["quests"]["waterfall_quest"]["progress"], 3)
        self.assertEqual(player_data["inventory"]["Book on Baxtorian"], 1)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Waterfall Quest 3/6"])

    def test_quest_answer_completes_priest_in_peril_only_after_essence_gate(self):
        blocked_calls = {"xp": [], "saves": 0, "errors": []}
        blocked_data = {
            "inventory": {"Pure essence": 24},
            "current_quest": "priest_in_peril",
            "quests": {"priest_in_peril": {"started": True, "progress": 8, "completed": False}},
            "quest_points": 0,
            "prayer_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(blocked_data, blocked_calls))

        self.assertFalse(ok)
        self.assertEqual(blocked_data["quests"]["priest_in_peril"]["progress"], 8)
        self.assertFalse(blocked_data["quests"]["priest_in_peril"]["completed"])
        self.assertEqual(blocked_data["inventory"].get("Wolfbane dagger", 0), 0)
        self.assertEqual(blocked_data["prayer_exp"], 0)
        self.assertEqual(blocked_calls["saves"], 0)
        self.assertIn("Needs Rune essence x50 or Pure essence x25", blocked_calls["errors"][0][1])

        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Pure essence": 25, "Rune essence": 2},
            "current_quest": "priest_in_peril",
            "quests": {"priest_in_peril": {"started": True, "progress": 8, "completed": False}},
            "quest_points": 0,
            "prayer_exp": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertTrue(player_data["quests"]["priest_in_peril"]["completed"])
        self.assertEqual(player_data["quests"]["priest_in_peril"]["progress"], 9)
        self.assertEqual(player_data["inventory"]["Pure essence"], 0)
        self.assertEqual(player_data["inventory"]["Rune essence"], 2)
        self.assertEqual(player_data["inventory"]["Wolfbane dagger"], 1)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["prayer_exp"], 1406.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"][0][0], "Quest complete")

    def test_quest_answer_blocks_holy_grail_titan_stage_without_excalibur(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Magic whistle": 1},
            "current_quest": "holy_grail",
            "quests": {"holy_grail": {"started": True, "progress": 5, "completed": False}},
            "quest_route_states": {
                "holy_grail": ["Reach the Fisher Realm crossing at the six stone heads"]
            },
            "quest_stage_actions": {
                "holy_grail": ["Blow the Magic whistle at the six stone heads"]
            },
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 120,
            "strength_level": 120,
            "defense_level": 120,
            "constitution_level": 120,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["quests"]["holy_grail"]["progress"], 5)
        self.assertFalse(player_data["quests"]["holy_grail"]["completed"])
        self.assertNotIn("quest_combat_encounters", player_data)
        self.assertEqual(player_data["inventory"].get("Grail bell", 0), 0)
        self.assertEqual(calls["saves"], 0)
        self.assertIn("Needs Excalibur", calls["errors"][0][1])

    def test_quest_answer_resolves_source_backed_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Stake": 1, "Stake hammer": 1},
            "current_quest": "vampyre_slayer",
            "quests": {"vampyre_slayer": {"started": True, "progress": 3, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 35,
            "constitution_level": 40,
            "prayer_level": 20,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["vampyre_slayer"]["progress"], 3)
        self.assertFalse(player_data["quests"]["vampyre_slayer"]["completed"])
        self.assertEqual(player_data["quest_combat_encounters"], {"vampyre_slayer": ["vampyre_slayer_count_draynor_37"]})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Count Draynor"])

    def test_quest_answer_resolves_source_backed_demon_slayer_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Silverlight": 1},
            "current_quest": "demon_slayer",
            "quests": {"demon_slayer": {"started": True, "progress": 7, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 30,
            "strength_level": 30,
            "defense_level": 30,
            "constitution_level": 30,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 7)
        self.assertFalse(player_data["quests"]["demon_slayer"]["completed"])
        self.assertEqual(player_data["quest_combat_encounters"], {"demon_slayer": ["demon_slayer_delrith_27"]})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Delrith"])

    def test_quest_answer_resolves_style_aware_magic_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "another_slice_of_h_a_m",
            "quests": {"another_slice_of_h_a_m": {"started": True, "progress": 4, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_combat_encounters": {"another_slice_of_h_a_m": ["another_slice_of_h_a_m_sigmund_64"]},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["another_slice_of_h_a_m"]["progress"], 4)
        self.assertFalse(player_data["quests"]["another_slice_of_h_a_m"]["completed"])
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {
                "another_slice_of_h_a_m": [
                    "another_slice_of_h_a_m_h_a_m_mage_30",
                    "another_slice_of_h_a_m_sigmund_64",
                ]
            },
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated H.A.M. mage"])

    def test_quest_answer_resolves_beast_fallback_ranged_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "toktz_ket_dill",
            "quests": {"toktz_ket_dill": {"started": True, "progress": 6, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 50,
            "strength_level": 50,
            "defense_level": 50,
            "constitution_level": 50,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["toktz_ket_dill"]["progress"], 6)
        self.assertFalse(player_data["quests"]["toktz_ket_dill"]["completed"])
        self.assertEqual(player_data["quest_combat_encounter_counts"], {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 1}})
        self.assertEqual(player_data["quest_combat_encounters"], {})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Lava monster"])

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["toktz_ket_dill"]["progress"], 6)
        self.assertFalse(player_data["quests"]["toktz_ket_dill"]["completed"])
        self.assertEqual(player_data["quest_combat_encounter_counts"], {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 2}})
        self.assertEqual(player_data["quest_combat_encounters"], {"toktz_ket_dill": ["toktz_ket_dill_lava_monster_47"]})
        self.assertEqual(calls["saves"], 2)
        self.assertEqual(calls["activity"], ["Defeated Lava monster", "Defeated Lava monster"])

    def test_quest_answer_resolves_a_souls_bane_first_fear_reaper_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "a_souls_bane",
            "quests": {"a_souls_bane": {"started": True, "progress": 3, "completed": False}},
            "quest_stage_actions": {"a_souls_bane": ["Fill the rage meter with an anger weapon"]},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 100,
            "strength_level": 100,
            "defense_level": 100,
            "constitution_level": 100,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["a_souls_bane"]["progress"], 3)
        self.assertFalse(player_data["quests"]["a_souls_bane"]["completed"])
        self.assertEqual(player_data["quest_combat_encounter_counts"], {"a_souls_bane": {"a_souls_bane_fear_reaper_42": 1}})
        self.assertEqual(player_data["quest_combat_encounters"], {})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Fear reaper"])

    def test_quest_answer_resolves_death_to_dorgeshuun_senior_guard_quantity(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Pickaxe": 1},
            "current_quest": "death_to_the_dorgeshuun",
            "quests": {"death_to_the_dorgeshuun": {"started": True, "progress": 5, "completed": False}},
            "quest_route_states": {"death_to_the_dorgeshuun": ["Reach the Tears of Guthix cavern"]},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_combat_encounters": {"death_to_the_dorgeshuun": ["death_to_the_dorgeshuun_sigmund_50"]},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 100,
            "strength_level": 100,
            "defense_level": 100,
            "constitution_level": 100,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["death_to_the_dorgeshuun"]["progress"], 5)
        self.assertFalse(player_data["quests"]["death_to_the_dorgeshuun"]["completed"])
        self.assertEqual(
            player_data["quest_combat_encounter_counts"],
            {"death_to_the_dorgeshuun": {"death_to_the_dorgeshuun_senior_ham_guard_22": 1}},
        )
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {"death_to_the_dorgeshuun": ["death_to_the_dorgeshuun_sigmund_50"]},
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Senior H.A.M. guard"])

    def test_quest_answer_resolves_conflict_overridden_dad_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Coins": 12},
            "current_quest": "troll_stronghold",
            "quests": {"troll_stronghold": {"started": True, "progress": 2, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_combat_encounters": {
                "troll_stronghold": ["troll_stronghold_twig_troll_71", "troll_stronghold_troll_general_171"]
            },
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 100,
            "strength_level": 100,
            "defense_level": 100,
            "constitution_level": 100,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(
            _context(player_data, calls, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10)
        )

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["troll_stronghold"]["progress"], 2)
        self.assertFalse(player_data["quests"]["troll_stronghold"]["completed"])
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {
                "troll_stronghold": [
                    "troll_stronghold_dad_101",
                    "troll_stronghold_troll_general_171",
                    "troll_stronghold_twig_troll_71",
                ]
            },
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Dad"])

    def test_broad_fletching_requires_ability_before_review_reward(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Headless arrows": 15, "Broad arrow heads": 15},
            "fletching_level": 99,
            "fletching_exp": 0,
            "current_fletch": "broad_arrows",
            "completed_achievements": [],
            "unlocked_abilities": [],
        }

        ok = handle_fletching_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["inventory"]["Broad arrow heads"], 15)
        self.assertEqual(player_data["fletching_exp"], 0)
        self.assertEqual(calls["errors"][0][0], "Fletching target locked")
        self.assertIn("Broad Fletching", calls["errors"][0][1])
        self.assertTrue(calls["deactivated"])

        player_data["unlocked_abilities"] = ["broad_fletching"]
        calls = {"xp": [], "saves": 0, "errors": []}
        ok = handle_fletching_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Headless arrows"], 0)
        self.assertEqual(player_data["inventory"]["Broad arrows"], 15)
        self.assertAlmostEqual(player_data["fletching_exp"], 150.0)
        self.assertEqual(calls["xp"], [150.0])

    def test_hunter_handler_consumes_materials_and_awards_outputs_on_success(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Logs": 1},
            "hunter_level": 23,
            "hunter_exp": 0,
            "current_hunter": "catch_wild_kebbit",
            "hunter_success_count": 0,
            "completed_achievements": [],
        }

        ok = handle_hunter_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Logs"], 0)
        self.assertEqual(player_data["inventory"]["Bones"], 1)
        self.assertEqual(player_data["inventory"]["Kebbit claws"], 1)
        self.assertAlmostEqual(player_data["hunter_exp"], 128.0)
        self.assertEqual(player_data["hunter_success_count"], 1)
        self.assertEqual(calls["xp"], [128.0])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])

    def test_hunter_quest_lock_deactivates_review_target(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "hunter_level": 99,
            "hunter_exp": 0,
            "current_hunter": "catch_ferret",
            "hunter_success_count": 0,
            "quests": {},
            "completed_achievements": [],
        }

        ok = handle_hunter_answer(_context(player_data, calls))

        self.assertFalse(ok)
        self.assertEqual(player_data["hunter_exp"], 0)
        self.assertEqual(player_data["hunter_success_count"], 0)
        self.assertEqual(calls["errors"][0][0], "Hunter target locked")
        self.assertIn("Eagles' Peak", calls["errors"][0][1])
        self.assertTrue(calls["deactivated"])

    def test_fishing_dry_attempt_records_telemetry_and_saves(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "fishing_level": 18,
            "fishing_exp": 0,
            "current_fishing": "catch_mackerel_cod_bass",
            "completed_achievements": [],
        }

        ok = handle_fishing_answer(_context(player_data, calls, random_values=[1.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["fishing_exp"], 0)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["saves"], 1)
        telemetry = player_data["action_telemetry"]["actions"]["fishing:catch_mackerel_cod_bass"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["failures"], 1)
        self.assertEqual(telemetry["failure_kinds"], {"dry": 1})
        self.assertGreater(telemetry["expected_successes"], 0.35)
        self.assertEqual(telemetry["current_dry_streak"], 1)

    def test_cooking_burn_records_failed_attempt_with_output(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Raw shrimps": 1},
            "cooking_level": 1,
            "cooking_exp": 0,
            "current_cooking": "cook_shrimps",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        ok = handle_cooking_answer(_context(player_data, calls, random_values=[1.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Raw shrimps"], 0)
        self.assertEqual(player_data["inventory"]["Burnt shrimp"], 1)
        self.assertEqual(player_data["cooking_success_count"], 0)
        self.assertEqual(player_data["cooking_burn_count"], 1)
        self.assertEqual(calls["saves"], 1)
        telemetry = player_data["action_telemetry"]["actions"]["cooking:cook_shrimps"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["failures"], 1)
        self.assertEqual(telemetry["failure_kinds"], {"burn": 1})
        self.assertEqual(telemetry["outputs"], {"Burnt shrimp": 1})

    def test_lava_eel_cooking_always_succeeds_with_source_xp(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Raw lava eel": 1},
            "cooking_level": 53,
            "cooking_exp": 0,
            "current_cooking": "cook_lava_eel",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        ok = handle_cooking_answer(_context(player_data, calls, random_values=[1.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"], {"Raw lava eel": 0, "Lava eel": 1})
        self.assertEqual(player_data["cooking_exp"], 30.0)
        self.assertEqual(player_data["cooking_success_count"], 1)
        self.assertEqual(player_data["cooking_burn_count"], 0)
        self.assertEqual(calls["xp"], [30.0])
        self.assertEqual(calls["saves"], 1)

    def test_cooking_runtime_extra_gutting_uses_source_rolls(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leaping sturgeon": 1},
            "cooking_level": 80,
            "cooking_exp": 0,
            "current_cooking": "gut_leaping_sturgeon",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        ok = handle_cooking_answer(_context(player_data, calls, random_values=[1.0, 5.0 / 6.0]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"], {"Leaping sturgeon": 0, "Caviar": 1, "Fish offcuts": 1})
        self.assertEqual(player_data["cooking_exp"], 15.0)
        self.assertEqual(player_data["cooking_success_count"], 1)
        self.assertEqual(calls["xp"], [15.0])
        self.assertEqual(calls["saves"], 1)
        telemetry = player_data["action_telemetry"]["actions"]["cooking:gut_leaping_sturgeon"]
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(telemetry["outputs"], {"Caviar": 1})

        failed_data = {
            "inventory": {"Leaping trout": 1},
            "cooking_level": 1,
            "cooking_exp": 0,
            "current_cooking": "gut_leaping_trout",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }
        self.assertTrue(handle_cooking_answer(_context(failed_data, calls, random_values=[1.0])))
        self.assertEqual(failed_data["inventory"], {"Leaping trout": 0})
        self.assertEqual(failed_data["cooking_burn_count"], 0)
        failed_telemetry = failed_data["action_telemetry"]["actions"]["cooking:gut_leaping_trout"]
        self.assertEqual(failed_telemetry["failure_kinds"], {"gut": 1})

    def test_cooking_runtime_extra_honors_source_no_level_requirement(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Leaping trout": 1},
            "cooking_level": 0,
            "cooking_exp": 0,
            "current_cooking": "gut_leaping_trout",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }

        self.assertTrue(handle_cooking_answer(_context(player_data, calls, random_values=[0.0, 0.0])))
        self.assertEqual(player_data["inventory"], {"Leaping trout": 0, "Roe": 1, "Fish offcuts": 1})
        self.assertEqual(player_data["cooking_exp"], 10.0)
        self.assertEqual(calls["errors"], [])

        ordinary_calls = {"xp": [], "saves": 0, "errors": []}
        ordinary_data = {
            "inventory": {"Raw shrimps": 1},
            "cooking_level": 0,
            "current_cooking": "cook_shrimps",
        }
        self.assertFalse(handle_cooking_answer(_context(ordinary_data, ordinary_calls)))
        self.assertEqual(ordinary_calls["errors"], [("Insufficient level", "You need level 1 Cooking to cook raw shrimps.")])

    def test_smithing_iron_failure_consumes_ore_and_records_telemetry(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Iron ore": 1},
            "smithing_level": 15,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "smelt_iron_bar",
            "completed_achievements": [],
        }

        ok = handle_smithing_answer(_context(player_data, calls, random_values=[0.99]))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Iron ore"], 0)
        self.assertNotIn("Iron bar", player_data["inventory"])
        self.assertEqual(player_data["smithing_exp"], 0)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["The ore was too impure"])
        telemetry = player_data["action_telemetry"]["actions"]["smithing:smelt_iron_bar"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["failures"], 1)
        self.assertEqual(telemetry["failure_kinds"], {"smelt_fail": 1})
        self.assertAlmostEqual(telemetry["expected_successes"], 0.51)

    def test_smithing_dragon_sq_shield_assembly_consumes_both_halves(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Shield left half": 1, "Shield right half": 1},
            "smithing_level": 60,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "repair_dragon_sq_shield",
            "quests": {"dorics_quest": {"completed": False}},
            "completed_achievements": [],
        }

        ok = handle_smithing_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"], {"Shield left half": 0, "Shield right half": 0, "Dragon sq shield": 1})
        self.assertAlmostEqual(player_data["smithing_exp"], 70.0)
        self.assertEqual(calls["xp"], [70.0])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        telemetry = player_data["action_telemetry"]["actions"]["smithing:repair_dragon_sq_shield"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["successes"], 1)

    def test_smithing_cannonballs_requires_quest_and_preserves_ammo_mould(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {"Steel bar": 1, "Ammo mould": 1},
            "smithing_level": 35,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "forge_cannonballs",
            "quests": {"dwarf_cannon": {"completed": False}},
            "completed_achievements": [],
        }

        self.assertFalse(handle_smithing_answer(_context(player_data, calls)))
        self.assertTrue(calls.get("deactivated"))
        self.assertIn("Dwarf Cannon", calls["errors"][0][1])

        calls = {"xp": [], "saves": 0, "errors": []}
        player_data["quests"]["dwarf_cannon"]["completed"] = True
        self.assertTrue(handle_smithing_answer(_context(player_data, calls)))
        self.assertEqual(player_data["inventory"], {"Steel bar": 0, "Ammo mould": 1, "Cannonball": 4})
        self.assertEqual(player_data["smithing_exp"], 25.6)
        telemetry = player_data["action_telemetry"]["actions"]["smithing:forge_cannonballs"]
        self.assertEqual(telemetry["outputs"], {"Cannonball": 4})


class TestCarriedOverlayWrapper(unittest.TestCase):
    """The overlay wrapper that runs a skilling tick through the 28-slot pack."""

    def _mining_ctx(self, player_data):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        ctx = _context(player_data, calls)
        return ctx, calls

    def _fake_gather(self, ctx):
        # Stand-in gathering handler: one Coal per acting tick.
        inv = ctx.player_data.setdefault("inventory", {})
        inv["Coal"] = inv.get("Coal", 0) + 1
        return True

    def test_gathering_banks_on_the_29th_answer_with_no_xp(self):
        player_data = {"inventory": {}, "current_ore": "copper_ore"}
        for _ in range(28):
            ctx, calls = self._mining_ctx(player_data)
            result = run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
            self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Coal"], 28)
        self.assertEqual(player_data["carried_inventory"]["copper_ore"], {"Coal": 28})
        self.assertEqual(player_data["carried_churn"]["copper_ore"], 28)

        # 29th answer buys the bank-run: handler is not called (Coal stays 28),
        # a bank-run toast fires, and the pack + churn reset.
        ctx, calls = self._mining_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
        self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Coal"], 28)
        self.assertTrue(any("Bank run" in msg for msg in calls["activity"]))
        self.assertNotIn("copper_ore", player_data.get("carried_inventory", {}))
        self.assertNotIn("copper_ore", player_data.get("carried_churn", {}))

        # 30th gathers again from a fresh pack.
        ctx, calls = self._mining_ctx(player_data)
        run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
        self.assertEqual(player_data["inventory"]["Coal"], 29)
        self.assertEqual(player_data["carried_inventory"]["copper_ore"], {"Coal": 1})

    def test_drop_mode_destroys_the_product_never_banks_and_keeps_nothing(self):
        # Drop is power-gathering: XP is kept, the product is destroyed. Previously
        # Drop kept every gathered item AND paid no bank-run review, so it strictly
        # dominated Keep and the whole Keep/Drop tradeoff was meaningless.
        player_data = {
            "inventory": {},
            "current_ore": "copper_ore",
            "carried_keep_drop": {"copper_ore": "drop"},
        }
        for _ in range(40):
            ctx, calls = self._mining_ctx(player_data)
            result = run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
            self.assertTrue(result)
            self.assertEqual(calls["activity"], [])  # never a bank-run toast
        # 40 gathers, XP awarded by the handler, but zero materials kept.
        self.assertEqual(player_data["inventory"].get("Coal", 0), 0)
        self.assertEqual(player_data.get("carried_inventory", {}), {})
        self.assertEqual(player_data.get("carried_churn", {}), {})

    def test_drop_mode_still_consumes_real_inputs_only_the_product_is_dropped(self):
        # A consumed input (fishing bait) is a real cost and must not be refunded;
        # only the produced item is destroyed.
        def bait_fish(ctx):
            inv = ctx.player_data.setdefault("inventory", {})
            if inv.get("Fishing bait", 0) < 1:
                return False
            inv["Fishing bait"] -= 1
            inv["Raw fish"] = inv.get("Raw fish", 0) + 1
            return True

        player_data = {
            "inventory": {"Fishing bait": 5},
            "current_fishing": "x",
            "carried_keep_drop": {"x": "drop"},
        }
        ctx, _calls = self._mining_ctx(player_data)
        run_answer_with_carried_overlay(ctx, "fishing", bait_fish)
        self.assertEqual(player_data["inventory"]["Fishing bait"], 4)  # consumed, not refunded
        self.assertEqual(player_data["inventory"].get("Raw fish", 0), 0)  # dropped

    def test_coal_bag_defers_the_bank_run(self):
        # Owning a Coal bag raises coal capacity to 55, so 40 gathers do not bank
        # (they would without the bag, which banks at 28).
        player_data = {"inventory": {"Coal bag": 1}, "current_ore": "coal_rock"}
        for _ in range(40):
            ctx, calls = self._mining_ctx(player_data)
            run_answer_with_carried_overlay(ctx, "mining", self._fake_gather)
            self.assertEqual(calls["activity"], [])  # no bank-run yet
        self.assertEqual(player_data["carried_churn"]["coal_rock"], 40)
        self.assertEqual(player_data["inventory"]["Coal"], 40)

    def test_a_dry_gather_produces_no_churn_and_folds_nothing(self):
        # A gather can succeed as a review but roll no product (a dry action). It
        # must not churn or fold, or an unlucky streak would rack up phantom slots
        # and force bank runs with nothing to deposit.
        def dry_gather(ctx):
            return True  # counted as an action, but produced nothing

        player_data = {"inventory": {}, "current_ore": "copper"}
        for _ in range(50):
            ctx, _calls = self._mining_ctx(player_data)
            run_answer_with_carried_overlay(ctx, "mining", dry_gather)
        self.assertEqual(player_data.get("carried_churn", {}), {})
        self.assertEqual(player_data.get("carried_inventory", {}), {})

    def test_untracked_handler_key_runs_untouched(self):
        player_data = {"inventory": {}}
        marker = {"called": False}

        def handler(ctx):
            marker["called"] = True
            return True

        ctx, calls = self._mining_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "quest", handler)
        self.assertTrue(result)
        self.assertTrue(marker["called"])
        self.assertNotIn("carried_inventory", player_data)


class TestProcessingPackOverlay(unittest.TestCase):
    """Processing skills draw recipe inputs from the carried pack, not the bank."""

    def _firemaking_ctx(self, player_data):
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
        return _context(player_data, calls, random_values=[0.0] * 200), calls

    def _base_player_data(self, logs):
        return {
            "inventory": {"Logs": logs},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }

    def test_first_engagement_primes_the_pack_for_free_and_acts(self):
        player_data = self._base_player_data(5)
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)

        self.assertTrue(result)
        self.assertEqual(calls["activity"], [])  # no bank-run toast on priming
        self.assertEqual(player_data["inventory"]["Logs"], 4)
        self.assertEqual(player_data["inventory"]["Ashes"], 1)
        # The pack was seeded with all 5 logs, then one was consumed.
        self.assertEqual(player_data["carried_inventory"]["logs"], {"Logs": 4})
        self.assertIn("logs", player_data["carried_primed_targets"])

    def test_pack_depletes_then_forces_a_bank_run_leaving_bank_remainder(self):
        # 30 logs but a 28-slot pack: the pack primes to 28, 28 actions drain it,
        # and 2 logs never left the bank.
        player_data = self._base_player_data(30)
        for _ in range(28):
            ctx, calls = self._firemaking_ctx(player_data)
            result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)
            self.assertTrue(result)
            self.assertEqual(calls["activity"], [])
        self.assertEqual(player_data["inventory"]["Ashes"], 28)
        self.assertEqual(player_data["inventory"]["Logs"], 2)
        self.assertEqual(player_data["carried_inventory"].get("logs", {}), {})

        # The pack is dry but the bank has 2 more: this answer is spent banking,
        # not firemaking (no XP tick, a bank-run toast, no additional Ashes).
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)
        self.assertTrue(result)
        self.assertTrue(any("Bank run" in msg for msg in calls["activity"]))
        self.assertEqual(player_data["inventory"]["Ashes"], 28)
        self.assertEqual(player_data["carried_inventory"]["logs"], {"Logs": 2})

        # And firemaking resumes from the repacked (now 2-log) pack.
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)
        self.assertTrue(result)
        self.assertEqual(player_data["inventory"]["Ashes"], 29)
        self.assertEqual(player_data["inventory"]["Logs"], 1)

    def test_out_of_materials_in_both_pack_and_bank_fails_normally_no_forced_loop(self):
        player_data = self._base_player_data(0)
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)
        # The handler's own "out of materials" path fires; no bank-run is forced
        # since the bank cannot supply it either.
        self.assertFalse(result)
        self.assertEqual(calls["activity"], [])
        self.assertTrue(calls.get("deactivated"))

    def test_scoped_inventory_never_leaks_the_capped_bank_to_saves_or_achievements(self):
        # While a processing tick runs, player_data["inventory"] is temporarily
        # capped to what the pack holds. The handler must not persist that or
        # evaluate achievements against it: a save would write a truncated bank to
        # disk, and a "own N logs" achievement would see only the pack's 28.
        observed = {"saves": [], "achievements": []}
        player_data = {
            "inventory": {"Logs": 100},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        calls = {"xp": [], "errors": [], "activity": []}
        ctx = _context(player_data, calls, random_values=[0.0] * 20)
        ctx = dataclasses.replace(
            ctx,
            save_player_data=lambda: observed["saves"].append(player_data["inventory"].get("Logs")),
            check_achievements=lambda data: observed["achievements"].append(data["inventory"].get("Logs")),
        )

        run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)

        # Bank truly went 100 -> 99 (one log burned), even though the pack held 28.
        self.assertEqual(player_data["inventory"]["Logs"], 99)
        self.assertEqual(observed["achievements"], [99])
        self.assertNotIn(27, observed["saves"])
        self.assertEqual(observed["saves"], [99])

    def test_skill_availability_is_computed_from_the_bank_not_the_capped_pack(self):
        # Same leak class: the availability UI must reflect the real bank, or a
        # skill/recipe can look unavailable while the bank is full of materials.
        from runtime_actions import handle_crafting_answer

        observed = {"refresh": [], "partial": []}
        player_data = {
            "inventory": {"Uncut opal": 100},
            "crafting_level": 99,
            "crafting_exp": 0,
            "current_craft": "cut_opal",
            "completed_achievements": [],
        }
        calls = {"xp": [], "errors": [], "activity": []}
        ctx = _context(player_data, calls, random_values=[0.0] * 20)
        ctx = dataclasses.replace(
            ctx,
            refresh_skill_availability=lambda: observed["refresh"].append(
                player_data["inventory"].get("Uncut opal")),
            refresh_skill_availability_partial=lambda *_a: observed["partial"].append(
                player_data["inventory"].get("Uncut opal")),
        )

        run_answer_with_carried_overlay(ctx, "crafting", handle_crafting_answer)

        self.assertEqual(player_data["inventory"]["Uncut opal"], 99)
        # One full refresh, after reconciliation, seeing the true bank (not 27).
        self.assertEqual(observed["refresh"], [99])
        self.assertEqual(observed["partial"], [])  # suppressed inside the scope

    def test_churn_per_action_matches_real_runescape_trip_lengths(self):
        # Balance guard for the invented churn=28 knob. Cross-checked against RS:
        # smelting bronze carries 14 tin + 14 copper, so 14 smelts per trip; fletching
        # 28 logs into *stacking* arrow shafts is 28 actions per trip. Regression here
        # means slot accounting has drifted (e.g. a stackable read as unstackable,
        # which once made Fletching bank every other action).
        import runtime_actions as RA

        cases = [
            ("fletching", "current_fletch", "arrow_shafts", {"Logs": 500}, "fletching_level", 1),
            ("firemaking", "current_firemaking", "logs", {"Logs": 500}, "firemaking_level", 1),
            ("cooking", "current_cooking", "cook_shrimps", {"Raw shrimps": 500}, "cooking_level", 1),
            ("smithing", "current_smith", "smelt_bronze_bar",
             {"Tin ore": 500, "Copper ore": 500}, "smithing_level", 2),
        ]
        for key, target_key, target, inventory, level_key, expected_churn in cases:
            with self.subTest(skill=key):
                player_data = {
                    "inventory": dict(inventory), target_key: target,
                    level_key: 99, f"{key}_exp": 0, "completed_achievements": [],
                }
                calls = {"xp": [], "errors": [], "activity": []}
                ctx = _context(player_data, calls, random_values=[0.0] * 40)
                run_answer_with_carried_overlay(ctx, key, RA.answer_handler_for_key(key))
                self.assertEqual(player_data["carried_churn"][target], expected_churn)

    def test_advanced_layout_seeds_the_pack_instead_of_the_casual_full_fill(self):
        player_data = self._base_player_data(100)
        player_data["carried_advanced_targets"] = {"logs": True}
        player_data["carried_layout"] = {"logs": {"Logs": 6}}
        ctx, calls = self._firemaking_ctx(player_data)
        result = run_answer_with_carried_overlay(ctx, "firemaking", handle_firemaking_answer)

        self.assertTrue(result)
        # Seeded to the saved layout's 6, not a casual full-capacity fill of 28;
        # only the 1 log actually consumed leaves the real bank (99 stay banked).
        self.assertEqual(player_data["inventory"]["Logs"], 99)
        self.assertEqual(player_data["carried_inventory"]["logs"], {"Logs": 5})


if __name__ == "__main__":
    unittest.main()
