"""Real Vampyre bites preserve draw order, stat floors and healing limits."""

from copy import deepcopy
import unittest
from unittest.mock import Mock

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure
from tests.test_combat_logic import _player


def vampyre_player(enemy_lifepoints=300, **overrides):
    player = _player(
        current_combat_target="vampyre", attack_level=10, defense_level=1,
        constitution_level=99, combat_lifepoints=990, combat_auto_flee=False,
        quests={"priest_in_peril": {"completed": True}},
        combat_encounter={
            "target_id": "vampyre", "enemy_lifepoints": enemy_lifepoints,
            "enemy_attack_ticks_remaining": 0, "player_attack_ticks_remaining": 99,
        },
    )
    player.update(overrides)
    return player


class VampyreBiteTest(unittest.TestCase):
    def test_missed_or_invalid_bite_roll_does_not_draw_a_skill(self):
        for roll in (0.125, "invalid", None):
            with self.subTest(roll=roll):
                player = vampyre_player()
                supplied = deepcopy(player)
                rng = Mock(side_effect=(0.0, 0.999999, roll))
                out, ok, result = apply_combat_burst_pure(
                    player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA,
                    ticks=1, live_cadence=True, rng=rng,
                )
                self.assertTrue(ok, result)
                self.assertEqual(rng.call_count, 3)
                self.assertEqual(result["enemy_damage"], 73)
                self.assertEqual(result["vampyre_bites"], 0)
                self.assertEqual(result["stat_drains"], {})
                self.assertEqual(out["combat_encounter"]["enemy_lifepoints"], 300)
                self.assertEqual(player, supplied)

    def test_skill_selection_preserves_order_clamps_and_conversion_fallback(self):
        for roll, skill in ((0.05, "strength"), (-1.0, "attack"), (1.0, "summoning"),
                            ("invalid", "attack"), (None, "attack")):
            with self.subTest(roll=roll):
                rng = Mock(side_effect=(0.0, 0.999999, 0.0, roll))
                out, ok, result = apply_combat_burst_pure(
                    vampyre_player(summoning_level=10), COMBAT_ENEMY_DATA, EQUIPMENT_DATA,
                    ticks=1, live_cadence=True, rng=rng,
                )
                self.assertTrue(ok, result)
                self.assertEqual(rng.call_count, 4)
                self.assertEqual(result["vampyre_bites"], 1)
                self.assertEqual(result["stat_drains"], {skill: 1})
                self.assertEqual(result["vampyre_bite_healing"], 20)
                self.assertEqual(out["combat_encounter"]["enemy_lifepoints"], 320)

    def test_bite_healing_respects_damage_missing_lifepoints_and_stat_floor(self):
        for enemy_lp, damage_roll, healing in ((399, 0.999999, 1), (400, 0.999999, 0),
                                               (300, 0.0, 1)):
            with self.subTest(enemy_lp=enemy_lp, damage_roll=damage_roll):
                out, ok, result = apply_combat_burst_pure(
                    vampyre_player(enemy_lp, attack_level=1), COMBAT_ENEMY_DATA, EQUIPMENT_DATA,
                    ticks=1, live_cadence=True,
                    rng=Mock(side_effect=(0.0, damage_roll, 0.0, 0.0)),
                )
                self.assertTrue(ok, result)
                self.assertEqual(result["vampyre_bites"], 1)
                self.assertEqual(result["stat_drains"], {})
                self.assertEqual(result["vampyre_bite_healing"], healing)
                self.assertEqual(result["enemy_healing"], healing)
                self.assertEqual(out["combat_encounter"]["enemy_lifepoints"], enemy_lp + healing)
