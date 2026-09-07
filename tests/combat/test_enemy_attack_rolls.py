"""Enemy attack calculations retain selected styles and current defence."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.logic_pure import logic_pure_combat_engine as engine
from tests import test_combat_logic as fixtures


def attack_fixture(style="melee", **enemy_fields):
    player, equipment = fixtures.CombatEnemyAttackStyleTest._magic_robe_setup()
    player.update(
        constitution_level=99,
        combat_lifepoints=990,
        combat_auto_flee=False,
        combat_encounter={
            "target_id": "x",
            "enemy_lifepoints": 500,
            "player_attack_ticks_remaining": 99,
            "enemy_attack_ticks_remaining": 0,
        },
    )
    enemies = fixtures.CombatEnemyAttackStyleTest._enemy(style, **enemy_fields)
    return player, enemies, {**EQUIPMENT_DATA, **equipment}


def weakening_fixture(active):
    player, enemies, equipment = attack_fixture(
        max_hit=100,
        weakening_equipment={
            "slot": "neck", "items": ("Holy symbol",),
            "enemy_accuracy_multiplier": 0.5,
            "enemy_damage_multiplier": 0.5,
        },
    )
    if active:
        player["equipment"]["neck"] = "Holy symbol"
    return player, enemies, equipment


def draining_fixture():
    return attack_fixture(
        attack_speed=1,
        max_hit=40,
        bite={
            "chance_numerator": 1, "chance_denominator": 1, "max_heal": 1,
            "stat_drain_skills": ("defense",), "stat_drain_amount": 25,
        },
    )


class CombatEnemyAttackRollsTest(unittest.TestCase):
    def test_selected_style_overrides_the_player_class_mapping(self):
        player, enemies, equipment = attack_fixture(
            "ranged",
            attack_style_by_player_class={"melee": "magic"},
            attack_table=[{"kind": "attack", "style": "ranged", "weight": 1}],
        )
        ordinary = deepcopy(enemies)
        ordinary["x"].pop("attack_style_by_player_class")
        actual = engine.apply_combat_burst_pure(
            player, enemies, equipment, ticks=5, live_cadence=True, rng=lambda: 0.5
        )
        expected = engine.apply_combat_burst_pure(
            player, ordinary, equipment, ticks=5, live_cadence=True, rng=lambda: 0.5
        )
        initial = engine.apply_combat_burst_pure(
            player, enemies, equipment, ticks=1, rng=lambda: 0.5
        )
        self.assertTrue(actual[1] and expected[1] and initial[1])
        self.assertEqual(actual[2]["enemy_accuracy"], expected[2]["enemy_accuracy"])
        self.assertEqual(actual[2]["enemy_damage"], expected[2]["enemy_damage"])
        self.assertGreater(actual[2]["enemy_accuracy"], initial[2]["enemy_accuracy"])

    def test_weakening_is_sampled_once_and_applies_to_each_attack(self):
        results = []
        for active in (False, True):
            player, enemies, equipment = weakening_fixture(active)
            with patch.object(
                engine, "_combat_weakening_equipment_state",
                wraps=engine._combat_weakening_equipment_state,
            ) as weakening:
                updated, ok, result = engine.apply_combat_burst_pure(
                    player, enemies, equipment, ticks=9, live_cadence=True,
                    rng=fixtures._rng((0.0, 0.5) * 3),
                )
            self.assertTrue(ok, result)
            self.assertEqual(weakening.call_count, 1)
            self.assertGreater(result["enemy_damage"], 0)
            results.append(result)
        self.assertLess(results[1]["enemy_accuracy"], results[0]["enemy_accuracy"])
        self.assertLess(results[1]["enemy_damage"], results[0]["enemy_damage"])

    def test_defence_drained_by_one_attack_changes_the_next_accuracy(self):
        player, enemies, equipment = draining_fixture()
        first = engine.apply_combat_burst_pure(
            player, enemies, equipment, ticks=1, live_cadence=True,
            rng=fixtures._rng((0.0, 0.5, 0.0, 0.0)),
        )
        second = engine.apply_combat_burst_pure(
            player, enemies, equipment, ticks=2, live_cadence=True,
            rng=fixtures._rng((0.0, 0.5, 0.0, 0.0) * 2),
        )
        self.assertTrue(first[1] and second[1])
        self.assertEqual(first[2]["vampyre_bites"], 1)
        self.assertEqual(second[2]["vampyre_bites"], 2)
        self.assertGreater(second[2]["enemy_accuracy"], first[2]["enemy_accuracy"])
        self.assertLess(
            second[0]["combat_current_levels"]["defense"],
            first[0]["combat_current_levels"]["defense"],
        )
