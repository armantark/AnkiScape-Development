"""Game speed is one Anki setting read the same way by the review and the menu.

Owner decision 1 allows x1 to x20, and an unreadable stored value plays the
recommended x10. Amendment F2 keeps x1 for a profile with no stored speed: the
pace dialog writes the recommendation, so the reader never guesses one.
"""

import sys
import unittest
from unittest.mock import patch

from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)

SPEED_KEY = "ankiscape_review_action_multiplier"

STORED_AND_PLAYED = (
    ({}, 1),
    ({SPEED_KEY: 20}, 20),
    ({SPEED_KEY: 50}, 20),
    ({SPEED_KEY: "not-a-number"}, 10),
    # The pre-speed XP multiplier key is read only by the pace dialog's plan.
    ({"ankiscape_xp_multiplier": 5}, 1),
)


class TheSpeedSettingTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_the_review_and_the_menu_play_the_same_stored_speed(self):
        from ankiscape.ui import ui

        addon = _load_addon_as_package("ankiscape_game_speed_setting")
        for store, played in STORED_AND_PLAYED:
            with self.subTest(store=store):
                mw = _DummyMW(_DummyCol(store))
                addon.mw = mw
                with patch.object(ui, "mw", mw):
                    self.assertEqual((addon._review_action_multiplier(), ui._game_speed()), (played, played))

    def test_a_speed_twenty_card_runs_twenty_fletching_steps(self):
        addon = _load_addon_as_package("ankiscape_game_speed_card")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._show_exp = lambda *_args, **_kwargs: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({SPEED_KEY: 20}))
        addon._state.player_data = {
            "inventory": {"Logs": 30},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 10)


if __name__ == "__main__":
    unittest.main()
