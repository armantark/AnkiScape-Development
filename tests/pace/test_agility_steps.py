"""Agility spends the card's time budget, one obstacle per six-tick step (assumption 5)."""

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from tests.pace.test_card_budget import _ReviewDispatcherCase


def _course_player(agility_level: int, lifepoints: int) -> dict:
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(
        current_agility="burthorpe_course",
        agility_level=agility_level,
        combat_lifepoints=lifepoints,
    )
    return player


def _obstacle_attempts(player: dict) -> int:
    actions = player["action_telemetry"]["actions"]
    return sum(row["attempts"] for key, row in actions.items() if key.startswith("agility:"))


class AgilityStepTests(_ReviewDispatcherCase):
    def _course_card(self, player: dict, roll: float):
        addon = self._addon(player, 10, roll)
        addon._state.current_skill = "Agility"
        return addon, self._answer(addon)

    def test_a_speed_ten_card_crosses_ten_obstacles(self):
        _addon, player = self._course_card(_course_player(99, 990), 0.999)
        self.assertEqual(_obstacle_attempts(player), 10)

    def test_a_safety_stop_ends_the_card_at_the_first_failure(self):
        # One failure leaves 10 LP, which the course's next failure could take.
        addon, player = self._course_card(_course_player(1, 20), 0.0)
        self.assertEqual(_obstacle_attempts(player), 1)
        self.assertEqual(player["combat_lifepoints"], 10)
        self.assertNotEqual(addon._state.current_skill, "Agility")


if __name__ == "__main__":
    unittest.main()
