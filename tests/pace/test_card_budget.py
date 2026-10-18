"""One successful card buys six game ticks per unit of game speed (decision 4)."""

import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.tears_of_guthix_data import TEARS_OF_GUTHIX_TICKS_PER_REVIEW
from ankiscape.logic.livid_farm_logic import livid_farm_cycles_for_steps_pure
from ankiscape.logic.tears_of_guthix_logic import apply_tears_of_guthix_command_pure
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_livid_farm_logic import _player as _livid_farm_player
from tests.test_vinesweeper import _entered as _vinesweeper_player

SPEED = 3


def _tears_of_guthix_player() -> dict:
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["quests"]["tears_of_guthix"] = {"started": True, "progress": 3, "completed": True}
    # Enough Quest Points for more cavern beats than a doubly repeated card spends.
    data["quest_points"] = 100
    entered, ok, info = apply_tears_of_guthix_command_pure(data, "enter")
    if not ok:
        raise AssertionError(info)
    entered["current_utility"] = "tears_of_guthix"
    return entered


def _tears_beats(start_ticks: int):
    def beats(after: dict) -> int:
        spent = start_ticks - after["tears_of_guthix"]["remaining_ticks"]
        return spent // TEARS_OF_GUTHIX_TICKS_PER_REVIEW

    return beats


def _vinesweeper_operations(after: dict) -> int:
    return after["vinesweeper"]["operations"]


def _livid_farm_cycles(after: dict) -> tuple[int, int]:
    state = after["livid_farm"]
    return state["cycles_completed"], state["cadence_credit"]


class SpeedIsSpentOncePerCardTests(unittest.TestCase):
    """Activities that read the speed themselves must not be repeated by the dispatcher too."""

    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _answer_one_card(self, player: dict) -> dict:
        addon = _load_addon_as_package("ankiscape_card_budget_speed")
        addon._state.player_data = player
        addon._state.current_skill = "Utility / Activities"
        addon._state.exp_awarded = False
        addon._review_action_multiplier = lambda: SPEED
        addon.random.random = lambda: 0.01
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda *_args, **_kwargs: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        addon._remember_review_award_snapshot = lambda _before: None
        addon.on_good_answer()
        return addon._state.player_data

    def test_a_card_at_speed_three_runs_three_units_not_nine(self):
        tears = _tears_of_guthix_player()
        cases = (
            (
                "tears_of_guthix",
                tears,
                _tears_beats(tears["tears_of_guthix"]["remaining_ticks"]),
                SPEED,
            ),
            ("vinesweeper", _vinesweeper_player(), _vinesweeper_operations, SPEED),
            (
                "livid_farm",
                {**_livid_farm_player(), "current_utility": "livid_farm"},
                _livid_farm_cycles,
                livid_farm_cycles_for_steps_pure(0, SPEED),
            ),
        )
        for activity_id, player, units, expected in cases:
            with self.subTest(activity_id):
                self.assertEqual(units(self._answer_one_card(player)), expected)


if __name__ == "__main__":
    unittest.main()
