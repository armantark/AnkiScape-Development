"""A stun is a tick debt on the card's running budget (decision 5, ruling F4).

The stun ends the card. Once the stunning step is charged, the card's unspent
ticks pay the stun first; the rest carries, and the next card pays it before any
step starts. A step may start with fewer than six ticks left, and its overrun
carries too, so no tick is forfeited.
"""

import copy
import sys
import types
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)

# The Man / Woman pickpocket row: 10 LP damage and an 8-tick stun on a failure.
_PICKPOCKET_STUN_TICKS = 8


class _ThievingCardCase(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _addon(self, speed: int, failing_attempts: set[int]):
        """A pickpocket whose attempts in ``failing_attempts`` fail and all others succeed."""
        addon = _load_addon_as_package("ankiscape_stun_debt")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": speed}))
        addon._state.player_data = {
            "inventory": {},
            "thieving_level": 1,
            "thieving_exp": 0.0,
            "current_thieving": "pickpocket_man",
            "thieving_attempt_count": 0,
            "thieving_success_count": 0,
            "thieving_failure_count": 0,
            "combat_lifepoints": 990,
            "constitution_level": 99,
            "completed_achievements": [],
        }
        addon._state.current_skill = "Thieving"
        player = addon._state.player_data

        def roll() -> float:
            # The attempt count rises before the success roll, so it names the attempt.
            return 0.999 if player["thieving_attempt_count"] in failing_attempts else 0.0

        self.enterContext(patch.object(addon.random, "random", roll))
        return addon

    def _answer(self, addon) -> dict:
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 3, lambda _self, _ease: "answered")
        return addon._state.player_data

    @staticmethod
    def _attempts(player: dict) -> tuple[int, int]:
        return player["thieving_attempt_count"], player["thieving_failure_count"]


class StunDebtTests(_ThievingCardCase):
    def test_a_speed_ten_card_makes_ten_attempts_without_a_failure(self):
        player = self._answer(self._addon(10, set()))
        self.assertEqual(self._attempts(player), (10, 0))

    def test_a_speed_ten_card_ends_at_its_first_failure_and_pays_the_stun_inside_it(self):
        addon = self._addon(10, {4})
        player = self._answer(addon)
        self.assertEqual(self._attempts(player), (4, 1))
        self.assertNotIn("card_tick_debt", player)
        # Nothing carried, so the next card makes its full ten attempts.
        self.assertEqual(self._attempts(self._answer(addon)), (14, 1))

    def test_a_stun_on_the_last_step_of_a_speed_ten_card_carries_whole(self):
        player = self._answer(self._addon(10, {10}))
        self.assertEqual(self._attempts(player), (10, 1))
        self.assertEqual(player["card_tick_debt"], _PICKPOCKET_STUN_TICKS)

    def test_at_speed_one_a_stun_blocks_the_next_card_and_two_ticks_of_the_one_after(self):
        addon = self._addon(1, {1})
        player = self._answer(addon)
        self.assertEqual((self._attempts(player), player["card_tick_debt"]), ((1, 1), 8))

        player = self._answer(addon)
        self.assertEqual((self._attempts(player), player["card_tick_debt"]), ((1, 1), 2))

        # Four ticks are left once the last two are paid: the attempt starts and
        # its two-tick overrun carries, so no tick is forfeited.
        player = self._answer(addon)
        self.assertEqual((self._attempts(player), player["card_tick_debt"]), ((2, 1), 2))

    def test_undo_restores_the_stun_debt_exactly(self):
        addon = self._addon(1, {1})
        self._answer(addon)
        stunned = copy.deepcopy(addon._state.player_data)

        self._answer(addon)
        self.assertEqual(addon._state.player_data["card_tick_debt"], 2)
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, stunned)
        self.assertEqual(addon._state.player_data["card_tick_debt"], 8)


if __name__ == "__main__":
    unittest.main()
