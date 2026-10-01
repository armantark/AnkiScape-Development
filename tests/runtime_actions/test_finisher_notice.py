"""The event log says once when a fight leaves an enemy waiting on its finisher."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_runtime_actions as _runtime


def _abomination_fight(**state):
    return {
        "inventory": {},
        "equipment": {"weapon": "Bronze mace"},
        "current_combat_target": "gelatinous_abomination",
        "combat_action": "attack",
        "combat_attack_style": "aggressive",
        "combat_lifepoints": 990,
        "constitution_level": 99,
        "attack_level": 99,
        "strength_level": 99,
        "defense_level": 99,
        "slayer_level": 99,
        "combat_encounter": {
            "target_id": "gelatinous_abomination",
            "enemy_lifepoints": 10,
        },
        **state,
    }


class FinisherNoticeRuntimeTest(unittest.TestCase):
    def _review(self, player_data):
        calls = {"xp": [], "saves": 0, "errors": []}
        ok = _runtime.handle_combat_answer(
            _runtime._context(player_data, calls, [0.0, 0.999999] * 200)
        )
        self.assertTrue(ok, calls["errors"])
        return [line for line in calls.get("activity", []) if " LP · " in line]

    def test_held_abomination_is_logged_once_and_worn_gauntlets_log_nothing(self):
        player_data = _abomination_fight()

        self.assertEqual(
            self._review(player_data),
            ["Gelatinous abomination at 1 LP · Wear Spiked gauntlets to finish"],
        )
        self.assertEqual(player_data["combat_encounter"]["enemy_lifepoints"], 1)
        self.assertEqual(self._review(player_data), [])
        self.assertEqual(player_data["combat_encounter"]["enemy_lifepoints"], 1)

        wearing = _abomination_fight(
            equipment={"weapon": "Bronze mace", "hands": "Spiked gauntlets"}
        )
        self.assertEqual(self._review(wearing), [])
        self.assertGreaterEqual(
            wearing["combat_kill_counts"]["gelatinous_abomination"], 1
        )


if __name__ == "__main__":
    unittest.main()
