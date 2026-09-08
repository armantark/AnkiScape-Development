import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure
from ankiscape.logic_pure.logic_pure_combat_specials import (
    _combat_enemy_prayer_drain,
)
from tests.test_combat_logic import _player, _rng


def prayer_drain_fixture(*, prayer_points=50, base=10, damage_scaled=True):
    target_id = "prayer_drain_test"
    enemy = {
        "display_name": "Prayer drain test",
        "level": 99,
        "group": "Test",
        "stats": {
            "attack": 99,
            "strength": 99,
            "defence": 99,
            "hitpoints": 1000,
        },
        "bonuses": {},
        "max_hit": 31,
        "attack_speed": 1,
        "prayer_drain_base": base,
        "prayer_drain_damage": damage_scaled,
        "drops": {"guaranteed": (), "tables": ()},
        "source": "test",
    }
    player = _player(
        current_combat_target=target_id,
        attack_level=1,
        strength_level=1,
        defense_level=1,
        constitution_level=99,
        combat_lifepoints=990,
        equipment={"cape": "Fire cape"},
        combat_auto_eat_food=[],
        combat_auto_flee=False,
        prayer_level=99,
        combat_prayer_points=prayer_points,
        combat_selected_prayers=["protect_from_melee"],
        combat_prayer_uptime="100",
        combat_encounter={
            "target_id": target_id,
            "enemy_lifepoints": 1000,
            "player_attack_ticks_remaining": 1,
            "enemy_attack_ticks_remaining": 0,
        },
    )
    return player, {target_id: enemy}


class PrayerDrainTest(unittest.TestCase):
    def test_disabled_and_enabled_zero_drain_are_distinct(self):
        self.assertIsNone(_combat_enemy_prayer_drain({}, 50, 0))
        self.assertIsNone(
            _combat_enemy_prayer_drain({"prayer_drain_base": "invalid"}, 50, 0)
        )
        self.assertEqual(
            _combat_enemy_prayer_drain({"prayer_drain_base": 10}, 50, 0),
            0,
        )
        self.assertEqual(
            _combat_enemy_prayer_drain(
                {"prayer_drain_base": 10, "prayer_drain_damage": True},
                5,
                12,
            ),
            12,
        )

    def test_damage_scaled_drain_uses_raw_hit_before_protection(self):
        player, enemies = prayer_drain_fixture()

        updated, ok, result = apply_combat_burst_pure(
            player,
            enemies,
            EQUIPMENT_DATA,
            ticks=1,
            live_cadence=True,
            rng=_rng([0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["enemy_damage"], 0)
        self.assertEqual(result["enemy_prayer_drain"], 40)
        self.assertEqual(result["prayer_points_before"], 50)
        self.assertEqual(result["prayer_points_after"], 10)
        self.assertEqual(updated["combat_prayer_points"], 10)


if __name__ == "__main__":
    unittest.main()
