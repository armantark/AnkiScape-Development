import unittest
from unittest.mock import call, patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.logic import combat_level_up_check, level_up_check


class LevelUpCheckTest(unittest.TestCase):
    def test_multi_level_gain_reports_each_exact_transition(self) -> None:
        player_data = {
            "mining_level": 1,
            "mining_exp": 1_200.0,
            "review_event_log": [],
        }
        exp_table = {1: 0, 2: 100, 3: 300, 4: 600, 5: 1_000}

        with (
            patch("ankiscape.core.logic.exp_table_for_skill", return_value=exp_table),
            patch("ankiscape.core.logic.show_level_up_dialog") as show_dialog,
        ):
            level_up_check("Mining", player_data)

        self.assertEqual(player_data["mining_level"], 5)
        self.assertEqual(
            show_dialog.call_args_list,
            [
                call("Mining", 1, 2),
                call("Mining", 2, 3),
                call("Mining", 3, 4),
                call("Mining", 4, 5),
            ],
        )

    def test_combat_level_boundary_shows_one_popup_for_a_derived_increase(self) -> None:
        player_data = {
            "attack_level": 10,
            "strength_level": 10,
            "defense_level": 1,
            "constitution_level": 10,
            "prayer_level": 1,
            "ranged_level": 1,
            "magic_level": 1,
            "summoning_level": 1,
        }

        with (
            patch("ankiscape.core.logic._popups_enabled", return_value=True),
            patch("ankiscape.core.logic.show_level_up_dialog") as show_dialog,
        ):
            new_level = combat_level_up_check(3, player_data)

        self.assertGreater(new_level, 3)
        show_dialog.assert_called_once_with("Combat", 3, new_level)

    def test_non_combat_level_changes_do_not_move_combat_level(self) -> None:
        player_data = {
            "mining_level": 99,
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "constitution_level": 10,
            "prayer_level": 1,
            "ranged_level": 1,
            "magic_level": 1,
            "summoning_level": 1,
        }

        with (
            patch("ankiscape.core.logic._popups_enabled", return_value=True),
            patch("ankiscape.core.logic.show_level_up_dialog") as show_dialog,
        ):
            new_level = combat_level_up_check(3, player_data)

        self.assertEqual(new_level, 3)
        show_dialog.assert_not_called()


if __name__ == "__main__":
    unittest.main()
