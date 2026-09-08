import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure
from ankiscape.logic_pure import logic_pure_combat_specials as specials
from tests.combat.test_prayer_drain import prayer_drain_fixture
from tests.test_combat_logic import _rng


def enemy_poison_cases():
    for label, damage, roll, effects, potions, applied in (
        ("missing", None, None, {}, {}, False),
        ("invalid", "invalid", None, {}, {}, False),
        ("negative", -3, None, {}, {}, False),
        ("zero", 0, None, {}, {}, False),
        ("apply", 3, 0.0, {}, {}, True),
        ("negative-roll", 3, -1.0, {}, {}, True),
        ("threshold", 3, 0.4, {}, {}, False),
        ("invalid-roll", 3, "invalid", {}, {}, False),
        ("none-roll", 3, None, {}, {}, False),
        ("immune", 3, 0.0, {"poison_immunity": {"ticks_left": 100}}, {}, False),
        ("stronger", 3, 0.0, {"poison": {"ticks_left": 31, "tick_progress": 0}}, {}, False),
        ("cure", 3, 0.0, {}, {"Antipoison (1)": 1}, True),
    ):
        player, enemies = prayer_drain_fixture(base=0)
        enemy = next(iter(enemies.values()))
        if damage is not None:
            enemy["poison_damage"] = damage
        player["combat_status_effects"] = effects
        player["combat_supply_loadout"] = {"potions": potions}
        prefix = (1.0,) if label in {"missing", "invalid", "negative", "zero"} else (1.0, roll)
        yield label, player, enemies, prefix, {
            "status_applied": {"poison": 30} if applied else {},
            "potion_items": ["Antipoison (1)"] if potions else [],
        }


class EnemyPoisonApplicationTest(unittest.TestCase):
    def test_burst_poison_routes_preserve_consumption_and_draws(self):
        for label, player, enemies, prefix, expected in enemy_poison_cases():
            with self.subTest(case=label):
                draws = []
                source = _rng(prefix)

                def rng():
                    value = source()
                    draws.append(value)
                    return value

                _, ok, result = apply_combat_burst_pure(
                    player, enemies, EQUIPMENT_DATA,
                    ticks=1, live_cadence=True, rng=rng,
                )
                self.assertTrue(ok)
                self.assertEqual(result["status_applied"], expected["status_applied"])
                self.assertEqual([event["item"] for event in result["potions_used"]], expected["potion_items"])
                self.assertEqual(draws, list(prefix))

    def test_status_is_written_before_antipoison_consumption(self):
        status = {}
        data = {}
        event = {"effect": "poison_cure"}

        def consume(supplied):
            self.assertIs(supplied, data)
            self.assertEqual(status, {"poison": 30})
            self.assertIn("poison", data["combat_status_effects"])
            return event

        with patch.object(specials, "_combat_consume_antipoison_if_needed", consume):
            self.assertIs(
                specials._combat_enemy_poison_application(data, 3, lambda: 0.0, status),
                event,
            )

    def test_unhandled_rng_errors_propagate(self):
        def rng():
            raise RuntimeError("poison RNG failure")

        with self.assertRaisesRegex(RuntimeError, "poison RNG failure"):
            specials._combat_enemy_poison_application({}, 3, rng, {})


if __name__ == "__main__":
    unittest.main()
