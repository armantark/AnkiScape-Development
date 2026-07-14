import unittest

from cadence_kernel import (
    CAP_ONE_ACTION,
    advance_cadence_pure,
    default_cadence_profile_state_pure,
)
from constants import ORE_DATA
from logic_pure import (
    apply_thieving_damage_pure,
    thieving_blackjack_threshold_pure,
    thieving_multi_pick_count_pure,
    thieving_roll_succeeds_pure,
    thieving_roll_threshold_pure,
    thieving_stall_cadence_profile_pure,
    thieving_success_probability_pure,
    thieving_wall_safe_roll_succeeds_pure,
    thieving_wall_safe_success_count_pure,
)
from runtime_actions import (
    RuntimeActionContext,
    can_start_action,
    handle_thieving_answer,
    handle_utility_answer,
)
from storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from thieving_data import PICKPOCKET_TARGETS, STALL_TARGETS


def _context(player_data, random_values=()):
    calls = {
        "activity": [],
        "deactivated": 0,
        "errors": [],
        "level_checks": [],
        "saves": 0,
        "xp": [],
    }
    random_iter = iter(random_values)

    def random_random():
        try:
            return next(random_iter)
        except StopIteration:
            return 0.0

    def award_skill_exp(exp_key, base_exp):
        player_data[exp_key] = float(player_data.get(exp_key, 0.0) or 0.0) + float(base_exp)
        return float(base_exp)

    ctx = RuntimeActionContext(
        player_data=player_data,
        random_random=random_random,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.__setitem__(
            "deactivated", calls["deactivated"] + 1
        ),
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda skill, _data: calls["level_checks"].append(skill),
        check_achievements=lambda _data: None,
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: None,
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda text: calls["activity"].append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )
    return ctx, calls


def _blackjack_state(*, fight_back=False):
    return {
        "current_thieving": "blackjack_menaphite_thug",
        "thieving_level": 65,
        "thieving_exp": 0.0,
        "thieving_attempt_count": 0,
        "thieving_success_count": 0,
        "thieving_failure_count": 0,
        "thieving_stunned": False,
        "thieving_fight_back_when_caught": fight_back,
        "thieving_blackjack_phase": "needs_lure",
        "thieving_blackjack_picks_remaining": 0,
        "combat_lifepoints": 100,
        "combat_encounter": {},
        "inventory": {"Willow blackjack": 1},
        "quests": {"the_feud": {"completed": True}},
        "completed_achievements": [],
    }


class TestThievingPureMechanics(unittest.TestCase):
    def test_failure_damage_reuses_combat_auto_eat_and_death_state(self):
        fed, fed_result = apply_thieving_damage_pure(
            {
                "constitution_level": 10,
                "combat_lifepoints": 30,
                "combat_auto_eat_threshold_percent": 40,
                "combat_auto_eat_food": ["Lobster"],
                "combat_supply_loadout": {
                    "food": {"Lobster": 1},
                    "potions": {},
                    "stat_potions": {},
                    "ammo": {},
                    "runes": {},
                    "cannonballs": 0,
                },
            },
            10,
        )
        self.assertEqual(fed["combat_lifepoints"], 100)
        self.assertEqual(fed["combat_supply_loadout"]["food"], {})
        self.assertEqual(fed_result["food_used"]["item"], "Lobster")
        self.assertFalse(fed_result["died"])

        overhealed, _overhealed_result = apply_thieving_damage_pure(
            {"constitution_level": 10, "combat_lifepoints": 150},
            50,
        )
        self.assertEqual(overhealed["combat_lifepoints"], 100)

        dead, dead_result = apply_thieving_damage_pure(
            {
                "constitution_level": 10,
                "combat_lifepoints": 10,
                "equipment": {"weapon": "Bronze sword"},
            },
            20,
        )
        self.assertTrue(dead_result["died"])
        self.assertEqual(dead["combat_lifepoints"], 100)
        self.assertEqual(dead["equipment"], {})
        self.assertEqual(dead["combat_grave"]["items"], ["Bronze sword"])

    def test_pickpocket_roll_uses_inclusive_integer_thresholds(self):
        man = PICKPOCKET_TARGETS["pickpocket_man"]
        self.assertEqual(thieving_roll_threshold_pure(1, 180, 240), 180)
        self.assertTrue(thieving_roll_succeeds_pure(1, 180, 240, 180))
        self.assertFalse(thieving_roll_succeeds_pure(1, 180, 240, 181))
        self.assertEqual(thieving_success_probability_pure(1, man), 181 / 255)

        self.assertEqual(thieving_roll_threshold_pure(99, 180, 240), 240)
        self.assertTrue(thieving_roll_succeeds_pure(99, 180, 240, 240))
        self.assertFalse(thieving_roll_succeeds_pure(99, 180, 240, 241))
        self.assertEqual(thieving_success_probability_pure(99, man), 241 / 255)

    def test_wall_safe_uses_its_distinct_strict_source_roll(self):
        wall_safe = STALL_TARGETS["wall_safe"]
        self.assertEqual(thieving_wall_safe_success_count_pure(1, 8, 160), 9)
        self.assertEqual(thieving_wall_safe_success_count_pure(2, 8, 160), 9)
        self.assertEqual(thieving_wall_safe_success_count_pure(50, 8, 160), 85)
        self.assertEqual(thieving_wall_safe_success_count_pure(99, 8, 160), 161)
        self.assertTrue(thieving_wall_safe_roll_succeeds_pure(50, 8, 160, 84))
        self.assertFalse(thieving_wall_safe_roll_succeeds_pure(50, 8, 160, 85))
        self.assertEqual(thieving_success_probability_pure(50, wall_safe), 85 / 255)
        self.assertEqual(thieving_success_probability_pure(99, wall_safe), 161 / 255)

    def test_blackjack_hidden_roll_threshold_is_inclusive_at_level_65(self):
        threshold = thieving_blackjack_threshold_pure(65)
        self.assertEqual(threshold, 230)

        succeeds = _blackjack_state()
        succeeds["thieving_blackjack_phase"] = "ready_to_knockout"
        succeeds_ctx, _calls = _context(succeeds, random_values=(230 / 255,))
        self.assertFalse(handle_thieving_answer(succeeds_ctx))
        self.assertEqual(succeeds["thieving_blackjack_phase"], "knocked_out")

        fails = _blackjack_state()
        fails["thieving_blackjack_phase"] = "ready_to_knockout"
        fails_ctx, _calls = _context(fails, random_values=(231 / 255, 0.0))
        self.assertFalse(handle_thieving_answer(fails_ctx))
        self.assertEqual(fails["thieving_blackjack_phase"], "ready_to_knockout")
        self.assertTrue(fails["thieving_stunned"])

    def test_multi_pick_threshold_edges_match_2011scape(self):
        target_level = 40
        cases = (
            (49, 99, 1, 1),  # Thieving overshoot must reach ten.
            (50, 39, 1, 1),  # Agility must at least meet the target level.
            (50, 40, 1, 2),
            (59, 49, 1, 2),
            (60, 50, 1, 3),
            (69, 59, 1, 3),
            (70, 60, 1, 4),
            (99, 99, 0, 1),  # Only random(7) == 1 activates the bonus.
            (99, 99, 2, 1),
        )
        for thieving_level, agility_level, roll, expected in cases:
            with self.subTest(
                thieving_level=thieving_level,
                agility_level=agility_level,
                roll=roll,
            ):
                self.assertEqual(
                    thieving_multi_pick_count_pure(
                        thieving_level, agility_level, target_level, roll
                    ),
                    expected,
                )

    def test_all_18_stall_profiles_emit_exact_counts_in_26600_reviews(self):
        expected_counts = {
            "stall_vegetable": 26600,
            "stall_baker": 26600,
            "stall_crafting": 13300,
            "stall_monkey_food": 13300,
            "stall_monkey_general": 13300,
            "stall_tea": 13300,
            "stall_silk": 19950,
            "stall_wine": 9975,
            "stall_seed": 10640,
            "stall_fur": 9975,
            "stall_fish": 9975,
            "stall_crossbow": 10640,
            "wall_safe": 26600,
            "stall_silver": 3192,
            "stall_spice": 1200,
            "stall_magic": 1200,
            "stall_scimitar": 1200,
            "stall_gem": 532,
        }
        self.assertEqual(set(STALL_TARGETS), set(expected_counts))

        for target_id, expected in expected_counts.items():
            with self.subTest(target_id=target_id):
                profile = thieving_stall_cadence_profile_pure(
                    target_id, STALL_TARGETS[target_id]
                )
                state = default_cadence_profile_state_pure()
                for _ in range(26600):
                    state = advance_cadence_pure(profile, state).state
                self.assertEqual(state["assigned_reviews"], 26600)
                self.assertEqual(state["opportunities_emitted"], expected)
                if target_id in {"stall_vegetable", "stall_baker", "wall_safe"}:
                    self.assertEqual(profile.overflow_policy, CAP_ONE_ACTION)
                else:
                    self.assertIsNone(profile.overflow_policy)


class TestThievingRuntime(unittest.TestCase):
    def test_failed_pickpocket_deals_damage_then_next_review_only_clears_stun(self):
        player_data = {
            "current_thieving": "pickpocket_man",
            "thieving_level": 1,
            "thieving_exp": 0.0,
            "thieving_attempt_count": 0,
            "thieving_success_count": 0,
            "thieving_failure_count": 0,
            "thieving_stunned": False,
            "combat_lifepoints": 100,
            "inventory": {},
            "quests": {},
            "completed_achievements": [],
        }
        ctx, calls = _context(player_data, random_values=(0.999, 0.0))

        self.assertFalse(handle_thieving_answer(ctx))
        self.assertEqual(player_data["combat_lifepoints"], 90)
        self.assertTrue(player_data["thieving_stunned"])
        self.assertEqual(player_data["thieving_attempt_count"], 1)
        self.assertEqual(player_data["thieving_failure_count"], 1)
        self.assertEqual(player_data["thieving_exp"], 0.0)

        self.assertFalse(handle_thieving_answer(ctx))
        self.assertFalse(player_data["thieving_stunned"])
        self.assertEqual(player_data["combat_lifepoints"], 90)
        self.assertEqual(player_data["thieving_attempt_count"], 1)
        self.assertEqual(player_data["thieving_failure_count"], 1)
        self.assertEqual(calls["saves"], 2)

    def test_failed_wall_safe_trap_deals_20_to_60_damage_and_stuns(self):
        for damage_roll, expected_damage in ((0.0, 20), (0.999999, 60)):
            with self.subTest(expected_damage=expected_damage):
                player_data = {
                    "current_thieving": "wall_safe",
                    "thieving_level": 50,
                    "thieving_exp": 0.0,
                    "thieving_attempt_count": 0,
                    "thieving_success_count": 0,
                    "thieving_failure_count": 0,
                    "thieving_stunned": False,
                    "combat_lifepoints": 100,
                    "cadence_profiles": {},
                    "inventory": {},
                    "quests": {},
                    "completed_achievements": [],
                }
                ctx, calls = _context(
                    player_data, random_values=(85 / 255, damage_roll)
                )

                self.assertFalse(handle_thieving_answer(ctx))
                self.assertEqual(
                    player_data["combat_lifepoints"], 100 - expected_damage
                )
                self.assertTrue(player_data["thieving_stunned"])
                self.assertEqual(player_data["thieving_attempt_count"], 1)
                self.assertEqual(player_data["thieving_failure_count"], 1)
                self.assertEqual(player_data["thieving_exp"], 0.0)
                self.assertIn("Trap sprung", calls["activity"][-1])

                self.assertFalse(handle_thieving_answer(ctx))
                self.assertFalse(player_data["thieving_stunned"])
                self.assertEqual(
                    player_data["combat_lifepoints"], 100 - expected_damage
                )
                self.assertEqual(player_data["thieving_attempt_count"], 1)

    def test_menaphite_lure_knockout_and_two_picks_are_four_review_actions(self):
        player_data = _blackjack_state()
        ctx, calls = _context(player_data, random_values=(0.0,))

        self.assertFalse(handle_thieving_answer(ctx))
        self.assertEqual(player_data["thieving_blackjack_phase"], "ready_to_knockout")
        self.assertEqual(player_data["thieving_exp"], 0.0)

        self.assertFalse(handle_thieving_answer(ctx))
        self.assertEqual(player_data["thieving_blackjack_phase"], "knocked_out")
        self.assertEqual(player_data["thieving_blackjack_picks_remaining"], 2)
        self.assertEqual(player_data["thieving_exp"], 10.0)

        self.assertFalse(handle_thieving_answer(ctx))
        self.assertEqual(player_data["inventory"]["Coins"], 60)
        self.assertEqual(player_data["thieving_blackjack_picks_remaining"], 1)

        self.assertFalse(handle_thieving_answer(ctx))
        self.assertEqual(player_data["inventory"]["Coins"], 120)
        self.assertEqual(player_data["thieving_blackjack_picks_remaining"], 0)
        self.assertEqual(player_data["thieving_blackjack_phase"], "ready_to_knockout")
        self.assertEqual(player_data["thieving_exp"], 285.0)
        self.assertEqual(player_data["thieving_attempt_count"], 4)
        self.assertEqual(player_data["thieving_success_count"], 2)
        self.assertEqual(calls["xp"], [10.0, 137.5, 137.5])
        self.assertEqual(calls["saves"], 4)

    def test_failed_knockout_can_start_real_fight_back_encounter(self):
        player_data = _blackjack_state(fight_back=True)
        ctx, calls = _context(player_data, random_values=(0.999, 0.0))

        self.assertFalse(handle_thieving_answer(ctx))  # lure
        self.assertFalse(handle_thieving_answer(ctx))  # failed knockout

        self.assertEqual(player_data["combat_lifepoints"], 100)
        self.assertTrue(player_data["thieving_stunned"])
        self.assertEqual(player_data["thieving_failure_count"], 1)
        self.assertEqual(player_data["current_combat_target"], "menaphite_thug")
        self.assertEqual(
            player_data["combat_encounter"],
            {"target_id": "menaphite_thug", "enemy_lifepoints": 600},
        )
        self.assertEqual(calls["deactivated"], 1)
        self.assertIn("fight started", calls["activity"][-1])
        self.assertNotIn("LP damage", calls["activity"][-1])

    def test_desert_phoenix_utility_is_quest_gated_and_awards_no_xp(self):
        player_data = {
            "current_utility": "grab_desert_phoenix_feather",
            "inventory": {},
            "quests": {"the_golem": {"completed": False}},
            "completed_achievements": [],
        }
        locked_ctx, locked_calls = _context(player_data)
        self.assertFalse(can_start_action(locked_ctx, "utility"))
        self.assertFalse(handle_utility_answer(locked_ctx))
        self.assertEqual(player_data["inventory"], {})
        self.assertEqual(locked_calls["deactivated"], 1)
        self.assertIn("The Golem", locked_calls["errors"][0][1])

        player_data["quests"]["the_golem"]["completed"] = True
        active_ctx, active_calls = _context(player_data)
        self.assertTrue(can_start_action(active_ctx, "utility"))
        self.assertTrue(handle_utility_answer(active_ctx))
        self.assertEqual(player_data["inventory"]["Phoenix feather"], 1)
        self.assertNotIn("thieving_exp", player_data)
        self.assertEqual(active_calls["xp"], [])
        self.assertEqual(active_calls["activity"], ["+1 Phoenix feather"])


class TestThievingStorage(unittest.TestCase):
    def test_pending_thieving_xp_reward_migrates_exactly_once(self):
        migrated = migrate_loaded_data(
            {"pending_skill_exp_rewards": {"thieving_exp": 500.0}},
            ORE_DATA,
        )
        self.assertEqual(migrated["thieving_exp"], 500.0)
        self.assertGreater(migrated["thieving_level"], 1)
        self.assertEqual(migrated["pending_skill_exp_rewards"], {})

        reloaded = migrate_loaded_data(migrated, ORE_DATA)
        self.assertEqual(reloaded["thieving_exp"], 500.0)
        self.assertEqual(reloaded["pending_skill_exp_rewards"], {})

    def test_migration_sanitizes_thieving_state_and_preserves_unknown_inventory(self):
        migrated = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "current_thieving": "not_a_target",
                "thieving_attempt_count": -1,
                "thieving_success_count": True,
                "thieving_failure_count": "7",
                "thieving_stunned": "yes",
                "thieving_fight_back_when_caught": 1,
                "thieving_blackjack_phase": "invalid",
                "thieving_blackjack_picks_remaining": 99,
                "inventory": {"User experimental item": 4},
            },
            ORE_DATA,
        )

        self.assertEqual(migrated["current_thieving"], "pickpocket_man")
        self.assertEqual(migrated["thieving_attempt_count"], 0)
        self.assertEqual(migrated["thieving_success_count"], 0)
        self.assertEqual(migrated["thieving_failure_count"], 0)
        self.assertFalse(migrated["thieving_stunned"])
        self.assertFalse(migrated["thieving_fight_back_when_caught"])
        self.assertEqual(migrated["thieving_blackjack_phase"], "needs_lure")
        self.assertEqual(migrated["thieving_blackjack_picks_remaining"], 0)
        self.assertEqual(migrated["inventory"]["User experimental item"], 4)

    def test_migration_caps_valid_knocked_out_pick_count(self):
        migrated = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "current_thieving": "blackjack_menaphite_thug",
                "thieving_blackjack_phase": "knocked_out",
                "thieving_blackjack_picks_remaining": 7,
            },
            ORE_DATA,
        )
        self.assertEqual(migrated["thieving_blackjack_phase"], "knocked_out")
        self.assertEqual(migrated["thieving_blackjack_picks_remaining"], 2)

        exhausted = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "current_thieving": "blackjack_menaphite_thug",
                "thieving_blackjack_phase": "knocked_out",
                "thieving_blackjack_picks_remaining": 0,
            },
            ORE_DATA,
        )
        self.assertEqual(exhausted["thieving_blackjack_phase"], "ready_to_knockout")
        self.assertEqual(exhausted["thieving_blackjack_picks_remaining"], 0)


if __name__ == "__main__":
    unittest.main()
