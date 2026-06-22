import unittest

from runtime_actions import (
    RuntimeActionContext,
    answer_handler_for_key,
    can_start_action,
    handle_cooking_answer,
    handle_fishing_answer,
    handle_fletching_answer,
    handle_hunter_answer,
    handle_quest_answer,
    handle_smithing_answer,
)


def _context(player_data, calls=None, random_values=None):
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
    )


class TestRuntimeActions(unittest.TestCase):
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

    def test_handler_key_registry_and_readiness_share_runtime_module(self):
        self.assertIs(answer_handler_for_key("fletching"), handle_fletching_answer)
        self.assertIs(answer_handler_for_key("hunter"), handle_hunter_answer)

        player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "current_fletch": "arrow_shafts",
        }
        self.assertTrue(can_start_action(_context(player_data), "fletching"))

        player_data["inventory"] = {}
        self.assertFalse(can_start_action(_context(player_data), "fletching"))
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
        self.assertEqual(player_data["pending_skill_exp_rewards"], {"prayer_exp": 1406.0})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"][0][0], "Quest complete")

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

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["vampyre_slayer"]["progress"], 3)
        self.assertFalse(player_data["quests"]["vampyre_slayer"]["completed"])
        self.assertEqual(player_data["quest_combat_encounters"], {"vampyre_slayer": ["vampyre_slayer_count_draynor_37"]})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Count Draynor"])

    def test_quest_answer_resolves_darkan_backed_generated_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "demon_slayer",
            "quests": {"demon_slayer": {"started": True, "progress": 3, "completed": False}},
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

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 3)
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

        ok = handle_quest_answer(_context(player_data, calls))

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

    def test_quest_answer_resolves_split_golem_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "spirits_of_the_elid",
            "quests": {"spirits_of_the_elid": {"started": True, "progress": 4, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 90,
            "strength_level": 90,
            "defense_level": 90,
            "constitution_level": 90,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["spirits_of_the_elid"]["progress"], 4)
        self.assertFalse(player_data["quests"]["spirits_of_the_elid"]["completed"])
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {"spirits_of_the_elid": ["spirits_of_the_elid_black_golem_75"]},
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Black golem"])

    def test_quest_answer_resolves_identical_source_generated_combat_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "elemental_workshop_i",
            "quests": {"elemental_workshop_i": {"started": True, "progress": 2, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["elemental_workshop_i"]["progress"], 2)
        self.assertFalse(player_data["quests"]["elemental_workshop_i"]["completed"])
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {"elemental_workshop_i": ["elemental_workshop_i_earth_elemental_35"]},
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Earth Elemental"])

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

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["toktz_ket_dill"]["progress"], 6)
        self.assertFalse(player_data["quests"]["toktz_ket_dill"]["completed"])
        self.assertEqual(player_data["quest_combat_encounter_counts"], {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 1}})
        self.assertEqual(player_data["quest_combat_encounters"], {})
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Lava monster"])

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["toktz_ket_dill"]["progress"], 6)
        self.assertFalse(player_data["quests"]["toktz_ket_dill"]["completed"])
        self.assertEqual(player_data["quest_combat_encounter_counts"], {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 2}})
        self.assertEqual(player_data["quest_combat_encounters"], {"toktz_ket_dill": ["toktz_ket_dill_lava_monster_47"]})
        self.assertEqual(calls["saves"], 2)
        self.assertEqual(calls["activity"], ["Defeated Lava monster", "Defeated Lava monster"])

    def test_quest_answer_resolves_witchs_house_first_form_before_stage_progress(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "current_quest": "witchs_house",
            "quests": {"witchs_house": {"started": True, "progress": 2, "completed": False}},
            "quest_combat_config": {"resolver_enabled": True},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
            "completed_achievements": [],
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 60,
            "constitution_level": 60,
            "prayer_level": 1,
        }

        ok = handle_quest_answer(_context(player_data, calls))

        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["witchs_house"]["progress"], 2)
        self.assertFalse(player_data["quests"]["witchs_house"]["completed"])
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {"witchs_house": ["witchs_house_witchs_experiment_first_form"]},
        )
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["activity"], ["Defeated Witch's experiment (Skavid form)"])

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

        ok = handle_quest_answer(_context(player_data, calls))

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
            "inventory": {},
            "current_quest": "death_to_the_dorgeshuun",
            "quests": {"death_to_the_dorgeshuun": {"started": True, "progress": 5, "completed": False}},
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

        ok = handle_quest_answer(_context(player_data, calls))

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

        ok = handle_quest_answer(_context(player_data, calls))

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
        self.assertAlmostEqual(telemetry["expected_successes"], 0.5)


if __name__ == "__main__":
    unittest.main()
