"""Ranged manual finishers use the equipment context of the live review."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic_pure.logic_pure_combat_model import combat_finisher_state_pure
from tests import test_runtime_actions as _runtime


class RangedFinisherRuntimeTest(unittest.TestCase):
    def test_ranged_rockslug_finisher_spends_salt_and_records_one_kill(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Shortbow"},
            "current_combat_target": "rockslug",
            "combat_action": "finisher",
            "combat_attack_style": "ranged_accurate",
            "combat_lifepoints": 100,
            "constitution_level": 10,
            "ranged_level": 1,
            "slayer_level": 20,
            "combat_encounter": {
                "target_id": "rockslug",
                "enemy_lifepoints": 1,
            },
            "combat_supply_loadout": {
                "ammo": {"Bronze arrows": 2},
                "finishers": {"Bag of salt": 1},
            },
        }
        combat = _runtime.runtime_actions_combat
        state = combat_finisher_state_pure(player_data)
        self.assertTrue(state["ready"])
        self.assertTrue(state["available"])
        self.assertEqual(
            combat.combat_target_locked_reasons_pure(
                player_data,
                "rockslug",
                combat.COMBAT_ENEMY_DATA,
                equipment_data=combat.EQUIPMENT_DATA,
            ),
            (),
        )

        ok = _runtime.handle_combat_answer(
            _runtime._context(player_data, calls, [0.999999] * 40)
        )

        self.assertTrue(ok, calls["errors"])
        self.assertEqual(player_data["combat_kill_counts"], {"rockslug": 1})
        self.assertEqual(player_data["combat_encounter"], {})
        self.assertEqual(player_data["combat_action"], "attack")
        self.assertEqual(player_data["combat_supply_loadout"]["finishers"], {})
        self.assertEqual(
            player_data["combat_supply_loadout"]["ammo"], {"Bronze arrows": 2}
        )
        self.assertEqual(player_data["combat_lifepoints"], 100)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 1)
