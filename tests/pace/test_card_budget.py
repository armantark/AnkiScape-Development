"""One successful card buys six game ticks per unit of game speed (owner decision 4)."""

import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.tears_of_guthix_data import TEARS_OF_GUTHIX_TICKS_PER_REVIEW
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.logic.livid_farm_logic import livid_farm_cycles_for_steps_pure
from ankiscape.logic.tears_of_guthix_logic import apply_tears_of_guthix_command_pure
from ankiscape.runtime.runtime_actions import (
    ANSWER_HANDLERS,
    _combat_review_ticks,
    spend_card_budget,
)
from tests.test_fight_caves import _entered as _fight_caves_player
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_livid_farm_logic import _player as _livid_farm_player
from tests.test_runtime_actions import _context
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


class _ReviewDispatcherCase(unittest.TestCase):
    """Answers activity cards through the review dispatcher of a freshly loaded add-on."""

    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _addon(self, player: dict, speed: int, roll: float):
        addon = _load_addon_as_package("ankiscape_card_budget_dispatch")
        addon._state.player_data = player
        addon._state.current_skill = "Utility / Activities"
        addon._review_action_multiplier = lambda: speed
        # addon.random is the process-wide module, so the fixed roll must not outlive the test.
        self.enterContext(patch.object(addon.random, "random", lambda: roll))
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
        return addon

    def _answer(self, addon) -> dict:
        addon._state.exp_awarded = False
        addon.on_good_answer()
        return addon._state.player_data


class SpeedIsSpentOncePerCardTests(_ReviewDispatcherCase):
    """Activities that read the speed themselves must not be repeated by the dispatcher too."""

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
                self.assertEqual(units(self._answer(self._addon(player, SPEED, 0.01))), expected)


class ActivityKillEndsTheCardTests(_ReviewDispatcherCase):
    """A kill inside an activity's Combat slice ends the card; the next enemy waits."""

    def test_each_speed_ten_fight_cave_card_ends_at_its_kill(self):
        addon = self._addon(_fight_caves_player(), 10, 0.5)
        kills = [self._answer(addon)["fight_caves"]["total_kills"] for _card in range(3)]
        self.assertEqual(kills, [1, 2, 3])


class EveryRouteSpendsTheWholeCardTests(unittest.TestCase):
    """With nothing stopping it, a card at speed M spends all 6 x M ticks.

    Combat receives the whole budget in one call and spends it in its own tick
    loop. Quests and Dungeoneering take one stage or room per card, a declared
    divergence, and Agility keeps one obstacle per card; each call sees the
    whole budget too. Every other route takes M six-tick steps.
    """

    WHOLE_CARD_HANDLER_KEYS = frozenset({"combat", "quest", "dungeoneering", "agility"})

    def _spend(self, handler_key: str, action_id: str, speed: int) -> tuple[list[int], int]:
        player = {"current_utility": action_id} if handler_key == "utility" else {}
        ctx = _context(player, review_action_multiplier=speed)
        ctx.cadence_live_enabled = True
        offered: list[int] = []

        def step(step_ctx) -> bool:
            offered.append(_combat_review_ticks(step_ctx))
            return True

        spend_card_budget(ctx, handler_key, step, can_continue=lambda: True)
        return offered, ctx.card.ticks_remaining

    def test_every_declared_route_spends_six_ticks_per_step_until_the_card_is_spent(self):
        routes = [
            (row["handler_key"], row["action_id"])
            for row in cadence_coverage_rows_pure()
            if row["handler_key"] in ANSWER_HANDLERS
        ]
        self.assertGreater(len(routes), 2_000)
        mismatches = []
        for speed in (1, 3, 10):
            budget = 6 * speed
            for handler_key, action_id in routes:
                expected = (
                    [budget]
                    if handler_key in self.WHOLE_CARD_HANDLER_KEYS
                    else list(range(budget, 0, -6))
                )
                offered, left = self._spend(handler_key, action_id, speed)
                if (offered, left) != (expected, 0):
                    mismatches.append((speed, handler_key, action_id, offered, left))
        self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()
