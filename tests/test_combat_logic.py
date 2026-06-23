import unittest

from combat_data import COMBAT_ENEMY_DATA
from constants import EQUIPMENT_DATA
from logic_pure import apply_combat_burst_pure, combat_target_preview_pure


def _rng(values):
    iterator = iter(values)

    def _next():
        try:
            return next(iterator)
        except StopIteration:
            return 0.999999

    return _next


def _player(**overrides):
    data = {
        "inventory": {},
        "equipment": {},
        "attack_level": 99,
        "strength_level": 99,
        "defense_level": 99,
        "constitution_level": 10,
        "attack_exp": 0.0,
        "strength_exp": 0.0,
        "defense_exp": 0.0,
        "constitution_exp": 0.0,
        "current_combat_target": "chicken",
        "combat_attack_style": "accurate",
        "combat_lifepoints": 100,
        "combat_auto_eat_threshold_percent": 40,
        "combat_auto_eat_food": ["Shrimps"],
        "combat_encounter": {},
        "combat_kill_counts": {},
    }
    data.update(overrides)
    return data


class CombatLogicTest(unittest.TestCase):
    def test_combat_burst_kills_once_awards_xp_and_rolls_source_backed_drops(self):
        player = _player()

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=500,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["combat_kill_counts"], {"chicken": 1})
        self.assertEqual(new_data["combat_encounter"], {})
        self.assertGreater(new_data["attack_exp"], 0)
        self.assertGreater(new_data["constitution_exp"], 0)
        self.assertEqual(new_data["inventory"]["Bones"], 1)
        self.assertEqual(new_data["inventory"]["Raw chicken"], 1)
        self.assertEqual(new_data["inventory"]["Feather"], 5)

    def test_aggressive_style_routes_melee_xp_to_strength(self):
        player = _player(combat_attack_style="aggressive")

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["attack_exp"], 0.0)
        self.assertGreater(new_data["strength_exp"], 0.0)

    def test_combat_burst_caps_to_one_kill_per_review_even_with_many_ticks(self):
        player = _player(current_combat_target="cow")

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1000,
            rng=_rng([0.0, 0.999999, 0.999999, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["combat_kill_counts"], {"cow": 1})

    def test_auto_eat_consumes_food_after_enemy_damage_under_threshold(self):
        player = _player(
            attack_level=1,
            strength_level=1,
            defense_level=1,
            inventory={"Shrimps": 1},
            combat_lifepoints=20,
            combat_auto_eat_threshold_percent=90,
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["died"])
        self.assertEqual(new_data["inventory"]["Shrimps"], 0)
        self.assertEqual(result["food_used"], ({"item": "Shrimps", "healed_by": 30},))
        self.assertGreater(new_data["combat_lifepoints"], 20)

    def test_combat_preview_exposes_risk_and_source_metrics(self):
        preview = combat_target_preview_pure(_player(), "giant_rat", COMBAT_ENEMY_DATA, EQUIPMENT_DATA)

        self.assertEqual(preview["state"], "Ready")
        self.assertGreater(preview["accuracy"], 0)
        self.assertEqual(preview["enemy_max_lifepoints"], 50)
        self.assertTrue(str(preview["source"]).endswith("giant_rat_level_2.plugin.kts"))


if __name__ == "__main__":
    unittest.main()
