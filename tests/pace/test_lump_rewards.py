"""Lump rewards pay the same XP at speed 1 and speed 10 (plan Part J item 2).

A quest, an XP lamp and Penguin points roll nothing, so both speeds pay exactly
the same. Tears of Guthix and Fish Flingers roll their rewards from the random
stream that world events also draw from. An Evil Tree spawning mid-game lands
on a different card at each speed, so the same seed hands each speed its game
rolls in a different order; those two are compared over 20 seeds and must
agree within four standard errors.
"""

import random
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.evil_tree_data import EVIL_TREE_INTERVAL_TICKS
from ankiscape.logic.evil_tree_logic import ensure_evil_tree_state_pure
from ankiscape.logic.penguin_hide_and_seek_logic import apply_penguin_command_pure, penguin_view_pure
from tests.pace.rates.rate_property import MAX_STANDARD_ERRORS, SEEDS, standard_errors_apart
from tests.pace.test_fish_flingers_length import _entered_player as _fish_flingers_entered
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)
from tests.test_tears_of_guthix import _entered as _tears_entered

_ACTIVITIES = "Utility / Activities"


def _evil_tree_spawns_in(player: dict, ticks: int) -> dict:
    """Put the Evil Tree's spawn slot ``ticks`` game ticks ahead.

    The spawn draws two randoms after the card that crosses the slot. World
    events wait for the player's first answered card and run on a long day.
    """
    player = ensure_evil_tree_state_pure(player)
    player["shop_market_clock"] = {**player["shop_market_clock"], "answered_cards": 1}
    player["world_clock"] = {
        "day": 0,
        "day_start_card": 0,
        "day_length": 1_000,
        "in_day_ticks": EVIL_TREE_INTERVAL_TICKS - ticks,
    }
    player["evil_tree"]["next_spawn_tick"] = EVIL_TREE_INTERVAL_TICKS
    return player


def _tears_visit() -> dict:
    return {**_tears_entered(), "current_utility": "tears_of_guthix"}


class LumpRewardTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        self._random_state = random.getstate()
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_lump_rewards")
        for name in ("level_up_check", "check_achievements", "save_player_data", "_refresh_skill_availability"):
            setattr(self.addon, name, lambda *_args: None)
        self.addon.update_review_hud = lambda *_args: None
        self.addon.update_review_status_badge = lambda *_args: None
        self.messages = []
        self.addon.show_error_message = lambda title, _message: self.messages.append(title)

    def tearDown(self):
        random.setstate(self._random_state)
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _start(self, speed: int, player: dict, skill: str) -> None:
        self.messages.clear()
        self.addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": speed}))
        self.addon._state.player_data = player
        self.addon._state.current_skill = skill

    def _answer(self) -> dict:
        state = self.addon._state
        state.card_turned = state.answer_shown = True
        state.exp_awarded = False
        self.addon.on_answer_card(_FakeReviewer(), 3, lambda _self, _ease: "answered")
        return state.player_data

    def _xp(self) -> float:
        return sum(self.addon._implemented_exp_keys_snapshot().values())

    def _quest_xp(self, speed: int) -> float:
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"].update({"Bucket": 1, "Empty pot": 1})
        player["current_quest"] = "cooks_assistant"
        self._start(speed, player, "Quests")
        before = self._xp()
        for _card in range(20):
            if self._answer()["quests"]["cooks_assistant"].get("completed"):
                self.assertEqual(self.messages, ["Quest complete"])
                return self._xp() - before
        self.fail(f"Cook's Assistant did not finish within 20 cards at x{speed}")

    def test_a_quest_pays_exactly_the_same_xp(self):
        xp = {speed: self._quest_xp(speed) for speed in (1, 10)}
        self.assertGreater(xp[1], 0)
        self.assertEqual(xp[10], xp[1])

    def _lamp_xp(self, speed: int) -> float:
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["troll_stronghold"] = {"started": True, "progress": 99, "completed": True}
        player["mining_level"] = 30
        self._start(speed, player, "Mining")
        before = self._xp()
        self.assertTrue(self.addon.on_claim_reward("troll_stronghold_xp_lamp_1", "mining"))
        return self._xp() - before

    def test_an_xp_lamp_pays_exactly_the_same_xp(self):
        xp = {speed: self._lamp_xp(speed) for speed in (1, 10)}
        self.assertGreater(xp[1], 0)
        self.assertEqual(xp[10], xp[1])

    def _penguin_xp(self, speed: int) -> float:
        player = {**default_player_data(ORE_DATA, ITEM_DEFINITIONS), "current_utility": "penguin_hide_and_seek"}
        self._start(speed, player, _ACTIVITIES)
        for row in penguin_view_pure(player)["roster"]:
            player, selected, info = apply_penguin_command_pure(
                self.addon._state.player_data, "select_spy", {"spawn_id": row["id"]}
            )
            self.assertTrue(selected, info)
            self.addon._state.player_data = player
            self._answer()
        self.assertEqual(self.messages, [])
        before = self._xp()
        player, redeemed, info = apply_penguin_command_pure(
            self.addon._state.player_data, "redeem_xp", {"skill_id": "mining"}
        )
        self.assertTrue(redeemed, info)
        self.addon._state.player_data = player
        return self._xp() - before

    def test_a_week_of_penguin_points_pays_exactly_the_same_xp(self):
        xp = {speed: self._penguin_xp(speed) for speed in (1, 10)}
        self.assertGreater(xp[1], 0)
        self.assertEqual(xp[10], xp[1])

    def _random_lump_xp(self, speed: int, seed: int, player: dict, finished) -> float:
        self._start(speed, player, _ACTIVITIES)
        random.seed(seed)
        before = self._xp()
        for _card in range(400):
            player = self._answer()
            if finished(player, self.addon._state.current_skill):
                self.assertTrue(player["evil_tree"]["active_event"], "the Evil Tree spawn did not interleave")
                self.assertEqual(self.messages, [])
                return self._xp() - before
        self.fail(f"the game at x{speed} did not finish within 400 cards")

    def _assert_random_lump_agrees(self, make_player, finished, spawn_ticks: int) -> None:
        xp = {
            speed: [
                self._random_lump_xp(speed, seed, _evil_tree_spawns_in(make_player(), spawn_ticks), finished)
                for seed in SEEDS
            ]
            for speed in (1, 10)
        }
        self.assertGreater(min(xp[1]), 0)
        apart = standard_errors_apart(xp[1], xp[10])
        self.assertLessEqual(abs(apart), MAX_STANDARD_ERRORS, f"x1 {xp[1]} x10 {xp[10]} ({apart:+.2f} SE)")

    def test_a_tears_of_guthix_visit_pays_the_same_xp_within_monte_carlo_tolerance(self):
        # The visit is 8 cards at x1 and one at x10; the spawn lands after the
        # fourth x1 card, in the middle of the visit's rolls.
        self._assert_random_lump_agrees(
            _tears_visit,
            lambda _player, skill: skill != _ACTIVITIES,
            spawn_ticks=24,
        )

    def test_a_fish_flingers_game_pays_the_same_xp_within_monte_carlo_tolerance(self):
        # The second catch lands at tick 250. The spawn slot at tick 241 comes
        # before that catch's roll at x1 and after it at x10, whose fifth card
        # covers ticks 241 to 300.
        self._assert_random_lump_agrees(
            _fish_flingers_entered,
            lambda player, _skill: player["fish_flingers_events_completed"],
            spawn_ticks=241,
        )


if __name__ == "__main__":
    unittest.main()
