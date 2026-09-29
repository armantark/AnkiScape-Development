import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic_pure.logic_pure_combat_model import sanitize_combat_state_pure
from tests import test_combat_logic as combat_logic


class CombatStateRepairTest(unittest.TestCase):
    def test_retired_attack_choices_fall_back_to_playable_ones(self):
        state = sanitize_combat_state_pure(
            combat_logic._player(
                current_combat_target="retired_monster",
                combat_attack_style="flurry",
                combat_attack_style_type="pierce",
                current_combat_spell="retired_spell",
                combat_borrowed_power_spell="wind_strike",
            )
        )

        self.assertEqual(
            [
                state[key]
                for key in (
                    "current_combat_target",
                    "combat_attack_style",
                    "combat_attack_style_type",
                    "current_combat_spell",
                    "combat_borrowed_power_spell",
                )
            ],
            ["chicken", "accurate", "auto", "wind_strike", ""],
        )

    def test_target_outside_the_callers_roster_falls_to_its_first_enemy(self):
        state = sanitize_combat_state_pure(combat_logic._player(), {"pressure": {}})

        self.assertEqual(state["current_combat_target"], "pressure")


if __name__ == "__main__":
    unittest.main()
