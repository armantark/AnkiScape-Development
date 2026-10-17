import ast
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.agility_data import (
    AGILITY_ITEM_IMAGES,
    AGILITY_SHORTCUTS,
    AGILITY_TARGETS_BY_ID,
    ALL_AGILITY_SHORTCUTS,
    DORGESH_ROUTE_OPTIONS,
)
from ankiscape.logic.agility_logic import (
    PIT_INVITATION_COURSE_IDS,
    agility_effective_level_pure,
    agility_failure_probability_pure,
    agility_target_locked_reasons_pure,
    apply_agility_command_pure,
    apply_agility_review_pure,
    default_agility_state_pure,
    sanitize_agility_state_pure,
)
from ankiscape.logic.agility_travel import (
    agility_carried_weight_pure,
    agility_travel_profile_pure,
    apply_run_energy_credit_pure,
    scheduled_travel_reviews_pure,
)
from ankiscape.logic_pure.logic_pure import fishing_agility_double_catch_chance_pure


class TestAgilityCourseData(unittest.TestCase):
    def test_agility_gameplay_modules_do_not_read_wall_clock_time(self):
        repo_root = Path(__file__).resolve().parents[1]
        forbidden_modules = {"time", "datetime"}
        for filename in ("data/agility_data.py", "logic/agility_logic.py", "logic/agility_travel.py"):
            with self.subTest(filename=filename):
                tree = ast.parse((repo_root / filename).read_text(encoding="utf-8"))
                imported = {
                    alias.name.split(".", 1)[0]
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Import)
                    for alias in node.names
                }
                imported.update(
                    node.module.split(".", 1)[0]
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module
                )
                self.assertTrue(
                    imported.isdisjoint(forbidden_modules),
                    f"{filename} must derive gameplay time from answered reviews, never the wall clock",
                )

    def test_period_course_lap_totals(self):
        expected = {
            "burthorpe_course": 79.5,
            "gnome_normal": 86.5,
            "gnome_advanced": 725.0,
            "barbarian_normal": 139.5,
            "barbarian_advanced": 740.7,
            "wilderness_course": 586.5,
            "agility_pyramid": 1014.0,
            "ape_atoll": 580.0,
            "werewolf_course": 540.0,
            "dorgesh_kaan": 2375.0,
            "penguin_course": 540.0,
            "bandos_throne_room": 380.0,
        }
        for target_id, total in expected.items():
            with self.subTest(target_id=target_id):
                target = AGILITY_TARGETS_BY_ID[target_id]
                self.assertAlmostEqual(
                    sum(stage.xp for stage in target.stages) + target.completion_bonus,
                    total,
                )

    def test_failure_profiles_respect_known_mastery_and_residual_shapes(self):
        gnome = AGILITY_TARGETS_BY_ID["gnome_advanced"]
        signpost = next(stage for stage in gnome.stages if stage.id == "signpost")
        self.assertAlmostEqual(agility_failure_probability_pure(signpost, gnome, 85), 0.40)
        self.assertEqual(agility_failure_probability_pure(signpost, gnome, 89), 0.0)

        werewolf = AGILITY_TARGETS_BY_ID["werewolf_course"]
        deathslide = next(stage for stage in werewolf.stages if stage.id == "deathslide")
        self.assertGreater(
            agility_failure_probability_pure(
                deathslide,
                werewolf,
                60,
                strength_level=60,
                carried_weight_kg=20,
            ),
            agility_failure_probability_pure(
                deathslide,
                werewolf,
                60,
                strength_level=60,
                carried_weight_kg=0,
            ),
        )
        self.assertEqual(
            agility_failure_probability_pure(deathslide, werewolf, 93, strength_level=1),
            0.0,
        )

    def test_complete_shortcut_and_dorgesh_route_registries_are_stable(self):
        self.assertEqual(len(AGILITY_SHORTCUTS), 62)
        self.assertEqual(len(ALL_AGILITY_SHORTCUTS), 68)
        self.assertEqual(len({row.id for row in ALL_AGILITY_SHORTCUTS}), 68)
        self.assertEqual([row.id for row in DORGESH_ROUTE_OPTIONS], ["pure", "grapple", "mixed"])
        self.assertTrue(DORGESH_ROUTE_OPTIONS[0].active)
        self.assertIsNone(DORGESH_ROUTE_OPTIONS[1].agility_xp)

    def test_every_registered_agility_image_exists(self):
        missing = [name for name, path in AGILITY_ITEM_IMAGES.items() if not Path(path).is_file()]
        self.assertEqual(missing, [])

    def test_travel_weight_clamps_and_stationary_routes_never_gain_fake_movement(self):
        carried, effective = agility_carried_weight_pure(
            {"Dragon bones": 28},
            {"body": "Agile top", "legs": "Agile legs"},
        )
        self.assertEqual(carried, 42.0)
        self.assertEqual(effective, 20.0)
        profile = agility_travel_profile_pure(
            "crafting", "leather_leather_gloves", 99, {"Dragon bones": 28}, {"body": "Agile top"}
        )
        self.assertEqual(profile.base_reviews, 0.0)
        self.assertEqual(profile.adjusted_reviews, 0.0)
        self.assertEqual(profile.weight_gain, 0.0)

    def test_fractional_travel_schedule_uses_only_the_due_trip_roll(self):
        profile = agility_travel_profile_pure("prayer", "gilded_altar_dragon_bones", 99, {"Dragon bones": 28}, {})
        self.assertEqual(scheduled_travel_reviews_pure(profile, 0.0), 3)
        self.assertEqual(scheduled_travel_reviews_pure(profile, 0.999), 2)

    def test_partial_run_energy_restore_reduces_only_a_moving_trip(self):
        moving = agility_travel_profile_pure(
            "prayer",
            "gilded_altar_dragon_bones",
            1,
            {"Dragon bones": 28},
            {},
        )
        credited, used = apply_run_energy_credit_pure(moving, 17)
        self.assertEqual(used, 17)
        self.assertAlmostEqual(
            credited.adjusted_reviews,
            moving.adjusted_reviews * 0.83,
        )

        stationary = agility_travel_profile_pure(
            "herblore",
            "clean_guam",
            1,
            {},
            {},
        )
        unchanged, used = apply_run_energy_credit_pure(stationary, 17)
        self.assertEqual(unchanged, stationary)
        self.assertEqual(used, 0)

    def test_double_catch_is_limited_to_the_three_period_fish(self):
        self.assertEqual(fishing_agility_double_catch_chance_pure("Raw tuna", 35), 0.10)
        self.assertEqual(fishing_agility_double_catch_chance_pure("Raw swordfish", 50), 0.10)
        self.assertEqual(fishing_agility_double_catch_chance_pure("Raw shark", 76), 0.10)
        self.assertEqual(fishing_agility_double_catch_chance_pure("Baron shark", 99), 0.0)


class TestAgilityPureEngine(unittest.TestCase):
    def test_dorgesh_course_accepts_any_exact_lit_source_state(self):
        player = {
            **default_agility_state_pure(),
            "agility_level": 99,
            "quests": {
                "death_to_the_dorgeshuun": {"started": True, "progress": 6, "completed": True},
            },
            "inventory": {},
            "equipment": {},
        }

        missing = agility_target_locked_reasons_pure(player, "dorgesh_kaan")
        self.assertIn("Lit torch or another valid alternative", missing)

        player["inventory"]["Bullseye lantern (lit)"] = 1
        self.assertEqual(agility_target_locked_reasons_pure(player, "dorgesh_kaan"), ())

        player["inventory"].clear()
        player["equipment"]["head"] = "Mining helmet (lit)"
        self.assertEqual(agility_target_locked_reasons_pure(player, "dorgesh_kaan"), ())

    def test_pit_invitation_stays_satisfied_while_six_review_challenge_is_active(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "the_pit",
            "agility_level": 99,
            "agility_pit_offer": True,
            "inventory": {},
        }

        player, first = apply_agility_review_pure(player, (0.99, 0.0, 0.5, 0.5))

        self.assertTrue(first["allowed"])
        self.assertFalse(player["agility_pit_offer"])
        self.assertEqual(player["agility_activity_state"]["pit"]["reviews"], 1)
        self.assertEqual(agility_target_locked_reasons_pure(player, "the_pit"), ())
        player, second = apply_agility_review_pure(player, (0.99, 0.0, 0.5, 0.5))
        self.assertTrue(second["allowed"])
        self.assertEqual(player["agility_activity_state"]["pit"]["reviews"], 2)

    def test_corrupt_pit_session_does_not_bypass_talent_scout_invitation(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "the_pit",
            "agility_level": 99,
            "agility_activity_state": {"pit": {"unexpected": True}},
            "inventory": {},
        }

        updated, result = apply_agility_review_pure(player, (0.99, 0.0, 0.5, 0.5))

        self.assertFalse(result["allowed"])
        self.assertNotIn("pit", updated["agility_activity_state"])
        self.assertEqual(
            agility_target_locked_reasons_pure(updated, "the_pit"),
            ("Talent Scout invitation",),
        )

    def test_only_period_eligible_courses_issue_pit_invitations(self):
        for target_id in ("burthorpe_course",):
            with self.subTest(target_id=target_id):
                target = AGILITY_TARGETS_BY_ID[target_id]
                player = {
                    **default_agility_state_pure(),
                    "current_agility": target_id,
                    "agility_level": 99,
                    "inventory": {},
                    "equipment": {},
                }
                player["agility_course_state"] = {
                    "target": target_id,
                    "stage": len(target.stages) - 1,
                    "checkpoint": "start",
                    "flawless": True,
                    "lap_xp_valid": True,
                    "requested_item_valid": True,
                    "status": "",
                }

                updated, result = apply_agility_review_pure(
                    player, (0.99, 0.0, 0.99, 0.99)
                )

                self.assertTrue(result["completed_lap"])
                self.assertFalse(updated["agility_pit_offer"])
                self.assertEqual(updated["current_agility"], target_id)

        self.assertEqual(
            PIT_INVITATION_COURSE_IDS,
            {
                "gnome_normal",
                "gnome_advanced",
                "barbarian_normal",
                "barbarian_advanced",
                "agility_pyramid",
                "ape_atoll",
                "wilderness_course",
                "werewolf_course",
                "dorgesh_kaan",
            },
        )

    def test_eligible_invitation_auto_accepts_and_stows_both_hand_slots(self):
        target = AGILITY_TARGETS_BY_ID["gnome_normal"]
        player = {
            **default_agility_state_pure(),
            "current_agility": target.id,
            "agility_level": 99,
            "inventory": {},
            "equipment": {
                "weapon": "Dragon scimitar",
                "shield": "Dragon defender",
                "head": "Agile top",
            },
        }
        player["agility_course_state"] = {
            "target": target.id,
            "stage": len(target.stages) - 1,
            "checkpoint": "start",
            "flawless": True,
            "lap_xp_valid": True,
            "requested_item_valid": True,
            "status": "",
        }

        updated, result = apply_agility_review_pure(
            player, (0.99, 0.0, 0.99, 0.99)
        )

        self.assertTrue(result["completed_lap"])
        self.assertTrue(updated["agility_pit_offer"])
        self.assertEqual(updated["agility_pit_origin_course"], target.id)
        self.assertEqual(updated["current_agility"], "the_pit")
        self.assertEqual(updated["equipment"], {"head": "Agile top"})
        self.assertEqual(
            updated["inventory"],
            {"Dragon scimitar": 1, "Dragon defender": 1},
        )
        self.assertIn("Talent Scout invitation accepted", updated["agility_status"])

    def test_manual_invitation_policy_and_familiar_confirmation(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "ape_atoll",
            "agility_pit_offer": True,
            "agility_pit_origin_course": "ape_atoll",
            "agility_pit_auto_accept": False,
            "inventory": {},
            "equipment": {"weapon": "Dragon scimitar"},
            "summoning_state": {
                "active_follower": {
                    "kind": "familiar",
                    "entity_id": "spiritwolf",
                    "remaining_reviews": 10,
                    "max_reviews": 10,
                    "storage": {},
                }
            },
        }

        blocked, result = apply_agility_command_pure(player, "accept_pit_offer")
        self.assertFalse(result["allowed"])
        self.assertTrue(result["requires_familiar_dismissal"])
        self.assertEqual(blocked["current_agility"], "ape_atoll")

        accepted, result = apply_agility_command_pure(
            player,
            "accept_pit_offer",
            {"dismiss_familiar": True},
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(accepted["current_agility"], "the_pit")
        self.assertEqual(accepted["summoning_state"]["active_follower"], {})
        self.assertEqual(accepted["inventory"]["Dragon scimitar"], 1)

        declined, result = apply_agility_command_pure(
            player,
            "decline_pit_offer",
        )
        self.assertTrue(result["allowed"])
        self.assertFalse(declined["agility_pit_offer"])
        self.assertEqual(declined["agility_pit_origin_course"], "")

    def test_pit_completion_returns_to_origin_and_remembers_reward_choice(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "the_pit",
            "agility_level": 50,
            "agility_pit_offer": True,
            "agility_pit_origin_course": "ape_atoll",
            "inventory": {},
            "equipment": {},
        }
        for _ in range(6):
            player, result = apply_agility_review_pure(
                player, (0.99, 0.0, 0.99, 0.99)
            )

        self.assertTrue(result["completed_activity"])
        self.assertEqual(player["current_agility"], "ape_atoll")
        self.assertEqual(
            player["agility_activity_state"]["pit_reward"]["course"],
            "ape_atoll",
        )
        self.assertEqual(player["agility_pit_origin_course"], "")

        player, claimed = apply_agility_command_pure(
            player,
            "gamble_pit_reward",
            {"remember_choice": True},
            roll=0.99,
        )
        self.assertTrue(claimed["allowed"])
        self.assertEqual(claimed["multiplier"], 2.0)
        self.assertEqual(
            player["review_context_preferences"]["pit_reward"],
            "gamble",
        )

    def test_leaving_pit_returns_to_origin_and_first_success_mask_does_not_repeat(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "the_pit",
            "agility_level": 50,
            "agility_pit_offer": False,
            "agility_pit_origin_course": "gnome_normal",
            "agility_pit_successes": 1,
            "inventory": {},
            "equipment": {},
            "agility_activity_state": {
                "pit": {
                    "challenge": "Crate Expectations",
                    "reviews": 5,
                    "successes": 4,
                    "origin_course": "gnome_normal",
                }
            },
        }

        completed, result = apply_agility_review_pure(
            player, (0.99, 0.0, 0.99, 0.99)
        )
        self.assertTrue(result["completed_activity"])
        self.assertNotIn("Gorilla mask", result["outputs"])

        active = {
            **player,
            "agility_pit_successes": 0,
        }
        left, result = apply_agility_command_pure(active, "abandon")
        self.assertTrue(result["allowed"])
        self.assertEqual(left["current_agility"], "gnome_normal")
        self.assertNotIn("pit", left["agility_activity_state"])
        self.assertEqual(left["agility_pit_origin_course"], "")
        self.assertIn("returned to Gnome Stronghold Course", result["message"])

    def test_one_review_advances_exactly_one_obstacle(self):
        player = {
            **default_agility_state_pure(),
            "agility_level": 99,
            "agility_exp": 0.0,
            "inventory": {},
        }
        updated, result = apply_agility_review_pure(player, (0.99, 0.99, 0.99, 0.99))
        self.assertTrue(result["allowed"])
        self.assertTrue(result["success"])
        self.assertEqual(result["action_id"], "log_beam")
        self.assertEqual(updated["agility_course_state"]["stage"], 1)
        self.assertEqual(updated["agility_actions_completed"], 1)

    def test_ape_atoll_ordered_lap_awards_exact_period_total(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "ape_atoll",
            "agility_level": 99,
            "agility_exp": 0.0,
            "inventory": {"Small ninja monkey greegree": 1},
            "quests": {"monkey_madness": {"completed": True}},
        }
        total = 0.0
        for _ in AGILITY_TARGETS_BY_ID["ape_atoll"].stages:
            player, result = apply_agility_review_pure(player, (0.99, 0.99, 0.99, 0.99))
            total += result["xp"]
        self.assertEqual(total, 580.0)
        self.assertTrue(result["completed_lap"])
        self.assertEqual(player["agility_lap_counts"]["total"], 1)

    def test_failed_barbarian_advanced_log_forfeits_only_that_lap_bonus(self):
        player = {
            "current_agility": "barbarian_advanced",
            "agility_level": 90,
            "quests": {"bar_crawl": {"completed": True}},
        }
        success_rolls = (0.99, 0.99, 0.99, 0.99)
        player, result = apply_agility_review_pure(player, success_rolls)
        self.assertEqual(result["action_id"], "rope_swing")
        self.assertTrue(result["success"])
        player, result = apply_agility_review_pure(player, (0.0, 0.99, 0.99, 0.99))
        self.assertEqual(result["action_id"], "log_balance")
        self.assertFalse(result["success"])
        self.assertEqual(result["xp"], 0.0)
        failed_state = player["agility_course_state"]
        self.assertEqual(failed_state["stage"], 1)
        self.assertFalse(failed_state["lap_xp_valid"])
        stages = AGILITY_TARGETS_BY_ID["barbarian_advanced"].stages
        for stage in stages[1:]:
            player, result = apply_agility_review_pure(player, success_rolls)
            self.assertEqual(result["action_id"], stage.id)
            self.assertTrue(result["success"])
        self.assertEqual(result["action_id"], "roof_slide")
        self.assertEqual(result["xp"], 15.0)
        self.assertTrue(result["completed_lap"])
        self.assertEqual(player["agility_lap_counts"]["total"], 1)
        self.assertEqual(player["agility_lap_counts"]["barbarian_advanced_flawless"], 0)
        for stage in stages:
            player, result = apply_agility_review_pure(player, success_rolls)
            self.assertEqual(result["action_id"], stage.id)
            self.assertTrue(result["success"])
        self.assertEqual(result["xp"], 630.0)
        self.assertEqual(player["agility_lap_counts"]["total"], 2)
        self.assertEqual(player["agility_lap_counts"]["barbarian_advanced_flawless"], 1)

    def test_other_course_failures_keep_lap_bonus(self):
        cases = (("barbarian_normal", 1, 90), ("barbarian_advanced", 0, 90), ("gnome_advanced", 4, 85))
        for target_id, failure_stage, level in cases:
            with self.subTest(target=target_id, failure_stage=failure_stage):
                player = {
                    "current_agility": target_id,
                    "agility_level": level,
                    "quests": {"bar_crawl": {"completed": True}},
                }
                target = AGILITY_TARGETS_BY_ID[target_id]
                success_rolls = (0.99, 0.99, 0.99, 0.99)
                for _ in range(failure_stage):
                    player, _ = apply_agility_review_pure(player, success_rolls)
                player, result = apply_agility_review_pure(player, (0.0, 0.99, 0.99, 0.99))
                self.assertFalse(result["success"])
                self.assertTrue(player["agility_course_state"]["lap_xp_valid"])
                for _ in target.stages[player["agility_course_state"]["stage"]:]:
                    player, result = apply_agility_review_pure(player, success_rolls)
                    self.assertTrue(result["success"])
                self.assertTrue(result["completed_lap"])
                self.assertAlmostEqual(result["xp"], target.stages[-1].xp + target.completion_bonus)
                self.assertEqual(player["agility_lap_counts"]["flawless"], 0)

    def test_failure_setback_is_stateful_and_zero_xp(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "combat_lifepoints": 1000,
            "inventory": {},
        }
        player["agility_course_state"] = {
            "target": "wilderness_course",
            "stage": 3,
            "checkpoint": "entrance",
            "flawless": True,
            "lap_xp_valid": True,
            "requested_item_valid": True,
            "status": "",
        }
        updated, result = apply_agility_review_pure(player, (0.0, 0.5, 0.5, 0.5))
        self.assertFalse(result["success"])
        self.assertEqual(result["xp"], 0.0)
        self.assertGreater(result["damage"], 0)
        self.assertEqual(updated["agility_course_state"]["stage"], 0)
        self.assertFalse(updated["agility_course_state"]["flawless"])

    def test_werewolf_failure_uses_actual_target_pack_and_equipment_weight(self):
        base = {
            **default_agility_state_pure(),
            "current_agility": "werewolf_course",
            "agility_level": 60,
            "strength_level": 60,
            "inventory": {"Ring of Charos": 1, "Dragon bones": 20},
            "equipment": {},
            "quests": {"creature_of_fenkenstrain": {"completed": True}},
            "agility_carried_weight_kg": 999,
        }
        base["agility_course_state"] = {
            "target": "werewolf_course",
            "stage": 4,
            "checkpoint": "start",
            "flawless": True,
            "lap_xp_valid": True,
            "requested_item_valid": True,
            "status": "",
        }

        without_pack, light = apply_agility_review_pure(base, (0.30, 0.5, 0.5, 0.5))
        with_pack_input = {
            **base,
            "carried_inventory": {
                "werewolf_course": {"Dragon bones": 20},
                "another_target": {"Dragon bones": 28},
            },
        }
        with_pack, heavy = apply_agility_review_pure(with_pack_input, (0.30, 0.5, 0.5, 0.5))

        self.assertTrue(light["success"])
        self.assertFalse(heavy["success"])
        self.assertEqual(without_pack["agility_course_state"]["stage"], 5)
        self.assertEqual(with_pack["agility_course_state"]["stage"], 5)
        self.assertAlmostEqual(light["expected_success_chance"], 0.75)
        self.assertAlmostEqual(heavy["expected_success_chance"], 0.675)

    def test_stale_carried_items_do_not_inflate_failure_weight(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "werewolf_course",
            "agility_level": 60,
            "strength_level": 60,
            "inventory": {"Ring of Charos": 1},
            "equipment": {},
            "quests": {"creature_of_fenkenstrain": {"completed": True}},
            "carried_inventory": {
                "werewolf_course": {
                    "Ring of Charos": 1,
                    "Dragon bones": 20,
                },
            },
        }
        player["agility_course_state"] = {
            "target": "werewolf_course",
            "stage": 4,
            "checkpoint": "start",
            "flawless": True,
            "lap_xp_valid": True,
            "requested_item_valid": True,
            "status": "",
        }

        _updated, result = apply_agility_review_pure(player, (0.30, 0.5, 0.5, 0.5))

        self.assertTrue(result["success"])
        self.assertAlmostEqual(result["expected_success_chance"], 0.75)

    def test_wilderness_completed_lap_rolls_one_pker_ambush_with_existing_hit_semantics(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "wilderness_course",
            "agility_level": 99,
            "combat_lifepoints": 1000,
            "inventory": {},
            "equipment": {},
        }
        player["agility_course_state"] = {
            "target": "wilderness_course",
            "stage": 5,
            "checkpoint": "start",
            "flawless": True,
            "lap_xp_valid": True,
            "requested_item_valid": True,
            "status": "",
        }

        updated, result = apply_agility_review_pure(player, (0.99, 0.99, 0.005, 0.50))

        self.assertTrue(result["completed_lap"])
        self.assertEqual(result["wilderness_ambush"], {"triggered": True, "damage": 125})
        self.assertEqual(result["damage"], 125)
        self.assertIn("PKer ambush", updated["agility_status"])

    def test_sanitizer_bounds_state_and_preserves_unrelated_data(self):
        sanitized = sanitize_agility_state_pure(
            {
                "current_agility": "not_real",
                "agility_course_state": {"stage": 999999},
                "agility_lap_counts": {"total": -8},
                "agility_activity_currencies": {"brianpoints": "12"},
                "agility_pit_origin_course": "not_real",
                "agility_pit_auto_accept": 0,
                "agility_activity_state": {
                    "pit": {
                        "challenge": "Floor Is Lava",
                        "reviews": 2,
                        "successes": 1,
                        "origin_course": "not_real",
                    }
                },
                "unrelated": {"keep": True},
            }
        )
        self.assertEqual(sanitized["current_agility"], "burthorpe_course")
        self.assertEqual(sanitized["agility_lap_counts"]["total"], 0)
        self.assertEqual(sanitized["agility_activity_currencies"]["brianpoints"], 12)
        self.assertEqual(sanitized["agility_pit_origin_course"], "")
        self.assertFalse(sanitized["agility_pit_auto_accept"])
        self.assertEqual(
            sanitized["agility_activity_state"]["pit"]["origin_course"],
            "burthorpe_course",
        )
        self.assertEqual(sanitized["unrelated"], {"keep": True})

    def test_course_modifiers_stack_in_order_and_consume_one_charge_each(self):
        player = {
            **default_agility_state_pure(),
            "agility_level": 99,
            "inventory": {"Penance horn": 1, "Prized pendant of Agility": 1},
            "equipment": {},
            "agility_effect_charges": {"Penance horn": 2, "Prized pendant of Agility": 2},
        }
        updated, result = apply_agility_review_pure(player, (0.99, 0.99, 0.99, 0.99))
        self.assertEqual(result["base_xp"], 5.5)
        self.assertEqual(result["xp"], 22.0)
        self.assertEqual(
            result["xp_modifiers"],
            (
                {"item": "Penance horn", "multiplier": 2.0},
                {"item": "Prized pendant of Agility", "multiplier": 2.0},
            ),
        )
        self.assertEqual(updated["agility_effect_charges"]["Penance horn"], 1)
        self.assertEqual(updated["agility_effect_charges"]["Prized pendant of Agility"], 1)

    def test_toy_mouse_attempt_is_bounded_and_never_uses_xp_modifiers(self):
        player = {
            **default_agility_state_pure(),
            "agility_level": 99,
            "inventory": {"Toy mouse": 1, "Penance horn": 1},
            "agility_effect_charges": {"Penance horn": 2},
        }
        player, command = apply_agility_command_pure(player, "wind_toy_mouse")
        self.assertTrue(command["allowed"])
        player, result = apply_agility_review_pure(player, (0.1, 0.9, 0.9, 0.9))
        self.assertEqual(result["xp"], 3.0)
        self.assertFalse(player["agility_toy_mouse_pending"])
        self.assertEqual(player["agility_effect_charges"]["Penance horn"], 2)

    def test_surefooted_prevents_a_standard_course_failure_and_ticks_by_action(self):
        player = {
            **default_agility_state_pure(),
            "agility_level": 1,
            "inventory": {"Surefooted aura": 1},
        }
        player, command = apply_agility_command_pure(player, "activate_surefooted")
        self.assertTrue(command["allowed"])
        player, result = apply_agility_review_pure(player, (0.0, 0.9, 0.9, 0.9))
        self.assertTrue(result["success"])
        self.assertEqual(player["agility_effect_charges"]["surefooted_reviews"], 332)
        self.assertEqual(player["agility_effect_charges"]["surefooted_cooldown_reviews"], 1999)

    def test_real_course_roll_takes_the_larger_potion_or_cape_boost(self):
        player = {
            **default_agility_state_pure(),
            "agility_level": 99,
            "agility_effective_boost": 3,
            "agility_boost_actions_remaining": 10,
            "equipment": {"cape": "Agility cape"},
        }
        with patch(
            "ankiscape.logic.agility_logic.agility_failure_probability_pure",
            wraps=agility_failure_probability_pure,
        ) as probability:
            updated, result = apply_agility_review_pure(
                player,
                (0.99, 0.99, 0.99, 0.99),
            )

        self.assertTrue(result["allowed"])
        self.assertEqual(probability.call_args.args[2], 102)
        self.assertEqual(updated["agility_boost_actions_remaining"], 9)

    def test_skillcape_boost_has_full_uptime_only_while_equipped(self):
        player = {
            **default_agility_state_pure(),
            "agility_level": 99,
            "inventory": {"Coins": 99_000},
            "equipment": {},
        }
        player, result = apply_agility_command_pure(player, "purchase_agility_cape")
        self.assertTrue(result["allowed"])
        self.assertEqual(player["inventory"]["Coins"], 0)
        self.assertEqual(player["inventory"]["Agility cape"], 1)
        self.assertEqual(player["inventory"]["Agility hood"], 1)
        self.assertEqual(agility_effective_level_pure(player), 99)

        equipped = {**player, "equipment": {"cape": "Agility cape"}}
        self.assertEqual(agility_effective_level_pure(equipped), 100)
        _same, result = apply_agility_command_pure(
            equipped,
            "activate_agility_cape",
        )
        self.assertFalse(result["allowed"])
        self.assertEqual(result["message"], "Unknown Agility command")


if __name__ == "__main__":
    unittest.main()
