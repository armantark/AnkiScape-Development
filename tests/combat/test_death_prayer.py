import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure
from ankiscape.logic_pure.logic_pure_combat_specials import _combat_death_prayer_damage
from tests.combat.test_prayer_drain import prayer_drain_fixture
from tests.test_combat_logic import _rng


def death_prayer_cases():
    for label, prayer, roll, safe, lifepoints, points, damage in (
        ("retribution-zero", "retribution", 0.0, False, 1, 50, 0),
        ("retribution-half", "retribution", 0.5, False, 1, 50, 12),
        ("retribution-one", "retribution", 1.0, False, 1, 50, 24),
        ("retribution-above-one", "retribution", 1.5, False, 1, 50, 24),
        ("retribution-negative", "retribution", -1.0, False, 1, 50, 0),
        ("retribution-invalid", "retribution", "invalid", False, 1, 50, 0),
        ("retribution-none", "retribution", None, False, 1, 50, 0),
        ("wrath", "wrath", 1.0, False, 1, 50, 247),
        ("safe-death", "retribution", 1.0, True, 1, 50, 24),
        ("no-prayer", None, None, False, 1, 50, 0),
        ("survives", "retribution", None, False, 990, 50, 0),
        ("no-points", "retribution", 1.0, False, 1, 0, 24),
    ):
        player, enemies = prayer_drain_fixture(base=0, prayer_points=points)
        player["combat_selected_prayers"] = [prayer] if prayer else []
        player["combat_lifepoints"] = lifepoints
        player["combat_prayer_book"] = "curses" if prayer == "wrath" else "standard"
        player["quests"] = {"the_temple_at_senntisten": {"completed": True}}
        prefix = (0.0, 0.999999)
        if prayer and lifepoints == 1:
            prefix += (roll,)
        yield label, player, enemies, prefix, safe, {
            "died": lifepoints == 1,
            "safe_death": safe,
            "death_prayer_damage": damage,
            "automatic_finishers": 0,
        }


class DeathPrayerTest(unittest.TestCase):
    def test_full_burst_routes_and_rng_order(self):
        for label, player, enemies, prefix, safe, expected in death_prayer_cases():
            with self.subTest(case=label):
                draws = []
                source = _rng(prefix)

                def rng():
                    value = source()
                    draws.append(value)
                    return value

                _, ok, result = apply_combat_burst_pure(
                    player, enemies, EQUIPMENT_DATA,
                    ticks=1, live_cadence=True, safe_death=safe, rng=rng,
                )
                self.assertTrue(ok)
                self.assertEqual({key: result[key] for key in expected}, expected)
                self.assertEqual(draws, list(prefix))

    def test_wrath_precedence_level_normalization_and_finisher_caps(self):
        for prayers, level, enemy_lp, finisher, expected in (
            (("wrath", "retribution"), 99, 1000, None, 247),
            (("wrath",), 0, 1000, None, 2),
            (("wrath",), True, 1000, None, 2),
            (("wrath",), 99, 0, None, 0),
            (("wrath",), 99, 10, None, 10),
            (("wrath",), 99, 10, {"must_be_worn": True}, 9),
        ):
            with self.subTest(prayers=prayers, level=level, enemy_lp=enemy_lp, finisher=finisher):
                data = {"prayer_level": level}
                self.assertEqual(
                    _combat_death_prayer_damage(data, prayers, finisher, enemy_lp, lambda: 1.5),
                    (expected, False),
                )
                self.assertEqual(data, {"prayer_level": level})

    def test_rng_exception_boundary(self):
        for error in (TypeError, ValueError):
            with self.subTest(error=error):
                def rng():
                    raise error("death prayer RNG failure")

                self.assertEqual(
                    _combat_death_prayer_damage({"prayer_level": 99}, ("wrath",), None, 1000, rng),
                    (0, False),
                )

        def unhandled():
            raise RuntimeError("death prayer RNG failure")

        with self.assertRaisesRegex(RuntimeError, "death prayer RNG failure"):
            _combat_death_prayer_damage({}, ("wrath",), None, 1000, unhandled)


if __name__ == "__main__":
    unittest.main()
