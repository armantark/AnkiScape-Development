import ast
import unittest
from pathlib import Path

from agility_data import (
    AGILITY_ITEM_IMAGES,
    AGILITY_SHORTCUTS,
    AGILITY_TARGETS_BY_ID,
    ALL_AGILITY_SHORTCUTS,
    DORGESH_ROUTE_OPTIONS,
)
from agility_logic import (
    agility_failure_probability_pure,
    agility_target_locked_reasons_pure,
    apply_agility_command_pure,
    apply_agility_review_pure,
    default_agility_state_pure,
    sanitize_agility_state_pure,
)
from agility_travel import agility_carried_weight_pure, agility_travel_profile_pure, scheduled_travel_reviews_pure
from logic_pure import fishing_agility_double_catch_chance_pure


class TestAgilityCourseData(unittest.TestCase):
    def test_agility_gameplay_modules_do_not_read_wall_clock_time(self):
        repo_root = Path(__file__).resolve().parents[1]
        forbidden_modules = {"time", "datetime"}
        for filename in ("agility_data.py", "agility_logic.py", "agility_travel.py"):
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
        profile = agility_travel_profile_pure("prayer", "dragon_bones_gilded", 99, {"Dragon bones": 28}, {})
        self.assertEqual(scheduled_travel_reviews_pure(profile, 0.0), 3)
        self.assertEqual(scheduled_travel_reviews_pure(profile, 0.999), 2)

    def test_double_catch_is_limited_to_the_three_period_fish(self):
        self.assertEqual(fishing_agility_double_catch_chance_pure("Raw tuna", 35), 0.10)
        self.assertEqual(fishing_agility_double_catch_chance_pure("Raw swordfish", 50), 0.10)
        self.assertEqual(fishing_agility_double_catch_chance_pure("Raw shark", 76), 0.10)
        self.assertEqual(fishing_agility_double_catch_chance_pure("Baron shark", 99), 0.0)


class TestAgilityPureEngine(unittest.TestCase):
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

    def test_sanitizer_bounds_state_and_preserves_unrelated_data(self):
        sanitized = sanitize_agility_state_pure(
            {
                "current_agility": "not_real",
                "agility_course_state": {"stage": 999999},
                "agility_lap_counts": {"total": -8},
                "agility_activity_currencies": {"brianpoints": "12"},
                "unrelated": {"keep": True},
            }
        )
        self.assertEqual(sanitized["current_agility"], "burthorpe_course")
        self.assertEqual(sanitized["agility_lap_counts"]["total"], 0)
        self.assertEqual(sanitized["agility_activity_currencies"]["brianpoints"], 12)
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

    def test_flash_powder_outfit_passives_and_early_exit_are_review_native(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "flash_powder_factory",
            "agility_level": 99,
            "thieving_level": 99,
            "herblore_level": 99,
            "equipment": {
                "head": "Factory mask", "body": "Factory top", "legs": "Factory trousers",
                "hands": "Factory gloves", "feet": "Factory boots",
            },
            "inventory": {},
        }
        for _ in range(5):
            player, result = apply_agility_review_pure(player, (0.99, 0.0, 0.0, 0.99))
        session = player["agility_activity_state"]["flash_powder_factory"]
        self.assertEqual(session["reviews"], 5)
        self.assertEqual(session["deposits"], 1)
        self.assertEqual(session["catalyst_charges"], 2)
        self.assertEqual(result["expected_success_chance"], 0.895)
        self.assertTrue(result["outputs"])
        player, command = apply_agility_command_pure(player, "leave_activity")
        self.assertTrue(command["allowed"])
        self.assertEqual(player["agility_activity_currencies"]["brianpoints"], 15)

    def test_circus_closes_for_the_answered_card_week_and_reopens_next_week(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "circus_agility",
            "agility_level": 99,
            "inventory": {},
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7, "version": 1},
        }
        for _ in range(10):
            player, result = apply_agility_review_pure(player, (0.0, 0.9, 0.9, 0.9))
        self.assertTrue(result["completed_activity"])
        self.assertEqual(result["outputs"], {"Acrobat hood": 1})
        self.assertIn("next answered-card week", agility_target_locked_reasons_pure(player, "circus_agility"))
        player["shop_market_clock"]["answered_cards"] = 1680
        self.assertEqual(agility_target_locked_reasons_pure(player, "circus_agility"), ())

    def test_skillcape_purchase_and_action_boost_are_explicit_commands(self):
        player = {
            **default_agility_state_pure(),
            "agility_level": 99,
            "inventory": {"Coins": 99_000},
        }
        player, result = apply_agility_command_pure(player, "purchase_agility_cape")
        self.assertTrue(result["allowed"])
        self.assertEqual(player["inventory"]["Coins"], 0)
        self.assertEqual(player["inventory"]["Agility cape"], 1)
        self.assertEqual(player["inventory"]["Agility hood"], 1)
        player, result = apply_agility_command_pure(player, "activate_agility_cape")
        self.assertTrue(result["allowed"])
        self.assertEqual(player["agility_effective_boost"], 1)
        self.assertEqual(player["agility_boost_actions_remaining"], 10)


if __name__ == "__main__":
    unittest.main()
