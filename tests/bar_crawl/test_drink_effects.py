"""Literal gameplay expectations for the approved provisional drink arithmetic."""
from __future__ import annotations

import copy
import math
import unittest
from unittest.mock import Mock, patch

import pkg_alias  # noqa: F401
from ankiscape.logic.bar_crawl_logic import apply_bar_crawl_drink_effects_pure as drink
from ankiscape.logic_pure.logic_pure_combat_supplies import _combat_recover_current_levels
from ankiscape.logic_pure.logic_pure_prayer import prayer_uptime_fraction_pure


SKILLS = (
    "attack", "defense", "strength", "smithing", "herblore", "cooking", "prayer",
    "fletching", "firemaking", "woodcutting", "mining", "crafting", "magic",
    "ranged", "fishing", "constitution", "agility",
)
# Deliberately literal expectations, independent of the product's reference table.
EXPECTED_50 = (
    {"attack": 42, "defense": 43, "strength": 43, "smithing": 44},
    {},
    {"attack": 42, "defense": 43, "herblore": 44, "cooking": 43},
    {"attack": 39, "defense": 40},
    {},
    {"attack": 42, "defense": 44, "fletching": 45, "firemaking": 45, "woodcutting": 45},
    {"attack": 42, "defense": 43, "mining": 44, "crafting": 44, "magic": 44, "strength": 44, "smithing": 44},
    {"attack": 42, "defense": 43},
    {"attack": 42, "defense": 44, "ranged": 44, "fishing": 44},
    {},
)


def level_player(level=50):
    player = {f"{skill}_level": level for skill in SKILLS}
    player.update({f"{skill}_exp": 123456.0 for skill in SKILLS})
    player.update(
        combat_current_levels={}, combat_lifepoints=level * 10,
        combat_prayer_points=level * 10,
        combat_recovery_progress={"stat_drain_ticks": 37, "lifepoint_ticks": 9},
        combat_rest_reviews=7, combat_selected_prayers=["thick_skin"],
        equipment={"body": "Bronze platebody"}, inventory={"Trout": 4},
    )
    return player


class TestDrinkEffects(unittest.TestCase):
    def test_all_ten_drinks_at_level_50(self):
        for stage, currents in enumerate(EXPECTED_50, 2):
            with self.subTest(stage=stage):
                original = level_player()
                before = copy.deepcopy(original)
                rng = Mock(return_value=0.0)
                result = drink(original, stage, rng=rng)
                expected = copy.deepcopy(before)
                expected["combat_current_levels"] = currents
                expected["combat_prayer_points"] = 440 if stage == 4 else 500
                expected["combat_lifepoints"] = 400 if stage == 6 else 500
                self.assertEqual(result, expected)
                self.assertEqual(original, before)
                self.assertNotIn("defence", result["combat_current_levels"])
                self.assertNotIn("defence_level", result)
                self.assertEqual(rng.call_count, int(stage in (2, 3, 6, 10)))

    def test_all_skill_scaling_at_25_and_99(self):
        expectations = {
            25: (
                {"attack": 21, "defense": 22, "strength": 22, "smithing": 22}, {},
                {"attack": 21, "defense": 22, "herblore": 22, "cooking": 22},
                {"attack": 20, "defense": 20}, {},
                {"attack": 21, "defense": 22, "fletching": 23, "firemaking": 23, "woodcutting": 23},
                {"attack": 21, "defense": 22, "mining": 22, "crafting": 22, "magic": 22, "strength": 22, "smithing": 22},
                {"attack": 21, "defense": 22},
                {"attack": 21, "defense": 22, "ranged": 22, "fishing": 22}, {},
            ),
            99: (
                {"attack": 84, "defense": 86, "strength": 86, "smithing": 88}, {},
                {"attack": 84, "defense": 86, "herblore": 88, "cooking": 86},
                {"attack": 78, "defense": 80}, {},
                {"attack": 84, "defense": 88, "fletching": 90, "firemaking": 90, "woodcutting": 90},
                {"attack": 84, "defense": 86, "mining": 88, "crafting": 88, "magic": 88, "strength": 88, "smithing": 88},
                {"attack": 84, "defense": 86},
                {"attack": 84, "defense": 88, "ranged": 88, "fishing": 88}, {},
            ),
        }
        for level, rows in expectations.items():
            for stage, expected in enumerate(rows, 2):
                with self.subTest(level=level, stage=stage):
                    result = drink(level_player(level), stage, rng=lambda: 0)
                    self.assertEqual(result["combat_current_levels"], expected)
                    self.assertEqual(result["combat_prayer_points"], (220 if level == 25 else 872) if stage == 4 else level * 10)

    def test_minimum_request_floor_and_composition(self):
        player = level_player(2)
        result = drink(player, 8)
        self.assertEqual(result["combat_current_levels"], dict.fromkeys(
            ("attack", "defense", "mining", "crafting", "magic", "strength", "smithing"), 1))
        player = level_player(1)
        self.assertEqual(drink(player, 8)["combat_current_levels"], {})
        player = level_player()
        player["combat_current_levels"] = {"attack": 58, "defense": 46, "strength": 60, "agility": 55}
        before = copy.deepcopy(player)
        result = drink(player, 2, rng=lambda: 0)
        self.assertEqual(result["combat_current_levels"], {"defense": 39, "strength": 53, "smithing": 44, "agility": 55})
        self.assertEqual(player, before)

    def test_prayer_resource_default_and_exhaustion_preserve_selection(self):
        player = level_player()
        del player["combat_prayer_points"]
        self.assertEqual(drink(player, 4)["combat_prayer_points"], 440)
        player["combat_prayer_points"] = 20
        player["combat_prayer_uptime"] = "100"
        self.assertEqual(prayer_uptime_fraction_pure(player), 1)
        result = drink(player, 4)
        self.assertEqual(result["combat_prayer_points"], 0)
        self.assertEqual(result["prayer_level"], 50)
        self.assertNotIn("prayer", result["combat_current_levels"])
        self.assertEqual(result["combat_selected_prayers"], ["thick_skin"])
        self.assertEqual(prayer_uptime_fraction_pure(result), 0)

    def test_health_endpoints_and_interior_at_each_constitution(self):
        # (stage, lower, upper, damage at r=0.5), hand-written expected bounds.
        bounds = {
            25: ((2, 0, 10, 5), (3, 0, 23, 12), (6, 50, 75, 63), (10, 0, 100, 50)),
            50: ((2, 0, 20, 10), (3, 0, 47, 24), (6, 100, 150, 125), (10, 0, 200, 100)),
            99: ((2, 0, 20, 10), (3, 0, 47, 24), (6, 198, 297, 248), (10, 0, 200, 100)),
        }
        for level, rows in bounds.items():
            for stage, lower, upper, interior in rows:
                for draw, damage in ((0.0, lower), (0.5, interior), (math.nextafter(1.0, 0.0), upper)):
                    with self.subTest(level=level, stage=stage, draw=draw):
                        rng = Mock(return_value=draw)
                        result = drink(level_player(level), stage, rng=rng)
                        self.assertEqual(result["combat_lifepoints"], level * 10 - damage)
                        rng.assert_called_once_with()

    def test_health_floor_zero_absent_overheal_and_minimum_maximum(self):
        for stage, damage in ((2, 20), (3, 47), (6, 150), (10, 200)):
            for health, expected in ((3, 1), (0, 0), (800, 800 - damage), (None, 500 - damage)):
                with self.subTest(stage=stage, health=health):
                    player = level_player()
                    if health is None:
                        del player["combat_lifepoints"]
                    else:
                        player["combat_lifepoints"] = health
                    player["combat_auto_eat_food"] = ["Trout"]
                    player["combat_auto_eat_threshold_percent"] = 100
                    player["combat_selected_prayers"] = ["protect_from_melee"]
                    player["combat_prayer_uptime"] = "100"
                    before = copy.deepcopy(player)
                    rng = Mock(return_value=0.999999)
                    result = drink(player, stage, rng=rng)
                    self.assertEqual(result["combat_lifepoints"], expected)
                    self.assertEqual(player, before)
                    expected_data = copy.deepcopy(before)
                    expected_data["combat_lifepoints"] = expected
                    expected_data["combat_current_levels"] = EXPECTED_50[stage - 2]
                    self.assertEqual(result, expected_data)
                    self.assertEqual(result["equipment"], before["equipment"])
                    self.assertEqual(result["inventory"], before["inventory"])
                    self.assertEqual(result["combat_recovery_progress"], before["combat_recovery_progress"])
                    rng.assert_called_once_with()
        for stage in (2, 3):
            player = level_player(1)
            self.assertEqual(drink(player, stage, rng=lambda: 0.999999)["combat_lifepoints"], 9)

    def test_stage_admission_and_default_rng(self):
        for stage in (-1, 0, 1, 12, 13, 99):
            player = level_player()
            before = copy.deepcopy(player)
            rng = Mock(side_effect=AssertionError("unexpected draw"))
            self.assertEqual(drink(player, stage, rng=rng), before)
            self.assertEqual(player, before)
            rng.assert_not_called()
        with patch("ankiscape.logic.bar_crawl_logic.random.random", return_value=0.5) as rng:
            self.assertEqual(drink(level_player(), 2)["combat_lifepoints"], 490)
            rng.assert_called_once_with()

    def test_existing_recovery_restores_one_level_without_experience(self):
        player = level_player()
        result = drink(player, 2, rng=lambda: 0)
        before_xp = {key: value for key, value in result.items() if key.endswith("_exp")}
        _combat_recover_current_levels(result, 100)
        self.assertEqual(result["combat_current_levels"], {"attack": 43, "defense": 44, "strength": 44, "smithing": 45})
        self.assertEqual(result["combat_recovery_progress"]["stat_drain_ticks"], 37)
        self.assertEqual({key: value for key, value in result.items() if key.endswith("_exp")}, before_xp)
        self.assertEqual(player["combat_current_levels"], {})
