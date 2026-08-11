import unittest
from unittest.mock import call, patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.logic import level_up_check


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


if __name__ == "__main__":
    unittest.main()
