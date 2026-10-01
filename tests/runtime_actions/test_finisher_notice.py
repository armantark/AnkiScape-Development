"""The event log says once per encounter when an enemy waits on its finisher."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_runtime_actions as _runtime


_HIT = [0.0, 0.999999] * 200
_MISS = [0.999999] * 400


def _fight(target_id, enemy_lifepoints, **state):
    return {
        "inventory": {},
        "equipment": {"weapon": "Bronze mace"},
        "current_combat_target": target_id,
        "combat_action": "attack",
        "combat_attack_style": "aggressive",
        "combat_lifepoints": 990,
        "constitution_level": 99,
        "attack_level": 99,
        "strength_level": 99,
        "defense_level": 99,
        "slayer_level": 99,
        "combat_encounter": {
            "target_id": target_id,
            "enemy_lifepoints": enemy_lifepoints,
        },
        **state,
    }


class FinisherNoticeRuntimeTest(unittest.TestCase):
    def _review(self, player_data, rolls=_HIT):
        calls = {"xp": [], "saves": 0, "errors": []}
        ok = _runtime.handle_combat_answer(
            _runtime._context(player_data, calls, rolls)
        )
        self.assertTrue(ok, calls["errors"])
        return [line for line in calls.get("activity", []) if " LP · " in line]

    def test_held_abomination_is_logged_once_and_worn_gauntlets_log_nothing(self):
        player_data = _fight("gelatinous_abomination", 10)

        self.assertEqual(
            self._review(player_data),
            ["Gelatinous abomination at 1 LP · Wear Spiked gauntlets to finish"],
        )
        self.assertEqual(player_data["combat_encounter"]["enemy_lifepoints"], 1)
        self.assertEqual(self._review(player_data), [])
        self.assertEqual(player_data["combat_encounter"]["enemy_lifepoints"], 1)

        wearing = _fight(
            "gelatinous_abomination",
            10,
            equipment={"weapon": "Bronze mace", "hands": "Spiked gauntlets"}
        )
        self.assertEqual(self._review(wearing), [])
        self.assertGreaterEqual(
            wearing["combat_kill_counts"]["gelatinous_abomination"], 1
        )

    def test_next_slug_held_after_the_last_salt_is_logged(self):
        player_data = _fight(
            "rockslug",
            1,
            slayer_quick_finishers_unlocked=True,
            combat_supply_loadout={"finishers": {"Bag of salt": 1}},
        )

        self.assertEqual(
            self._review(player_data),
            ["Rock slug at 1 LP · Finisher blocked: no loaded Bag of salt"],
        )
        self.assertEqual(player_data["combat_kill_counts"]["rockslug"], 1)
        self.assertEqual(player_data["combat_encounter"]["enemy_lifepoints"], 1)
        self.assertEqual(self._review(player_data), [])

    def test_gargoyle_regenerating_out_of_range_is_not_logged_again(self):
        player_data = _fight("gargoyle", 100, combat_auto_flee=False)
        logged = []
        for rolls in (_HIT, _MISS, _HIT):
            player_data["combat_lifepoints"] = 990
            logged.append(self._review(player_data, rolls))
            logged.append(player_data["combat_encounter"]["enemy_lifepoints"])

        self.assertEqual(
            logged,
            [
                ["Gargoyle at 11 LP · Finisher blocked: no loaded Rock hammer"],
                11,
                [],
                131,
                [],
                11,
            ],
        )
        self.assertEqual(player_data["combat_kill_counts"], {})


if __name__ == "__main__":
    unittest.main()
