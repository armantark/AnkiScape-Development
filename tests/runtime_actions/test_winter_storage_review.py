"""A real answered card commits the failed attempt and genuine Undo restores it."""

import copy
import sys
import types
import unittest
from unittest.mock import patch

from tests.runtime_actions.test_winter_storage_rollback import _player
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


class TestWinterStorageReview(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_failed_review_keeps_winter_storage_until_genuine_answer_undo(self):
        addon = _load_addon_as_package("ankiscape_winter_storage_review")
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda _data: None
        saves = []
        addon.save_player_data = lambda: saves.append(copy.deepcopy(addon._state.player_data))
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon._state.player_data = _player("wall_safe")
        addon._state.player_data["summoning_state"]["active_follower"].update(
            remaining_reviews=100, max_reviews=100, lifepoints=100, max_lifepoints=100,
        )
        initial_state = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Thieving"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        with patch.object(addon.random, "random", side_effect=(85 / 255, 0.0)):
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        player = addon._state.player_data
        self.assertEqual(player["combat_lifepoints"], 80)
        # Speed 3: the 8-tick trap stun is paid inside the stopped card.
        self.assertNotIn("card_tick_debt", player)
        self.assertEqual(player["thieving_attempt_count"], 1)
        self.assertEqual(player["thieving_failure_count"], 1)
        self.assertEqual(player["cadence_profiles"]["thieving:wall_safe"]["assigned_reviews"], 1)
        self.assertEqual(player["inventory"]["Winter storage scroll"], 0)
        self.assertEqual(player["carried_inventory"]["wall_safe"], {"Copper ore": 26})
        self.assertEqual(player["carried_churn"]["wall_safe"], 27)
        self.assertEqual(player["summoning_exp"], 24.8)
        self.assertEqual(saves[-1], player)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, initial_state)
        self.assertEqual(addon._state.current_skill, "Thieving")
        self.assertEqual(saves[-1], initial_state)
