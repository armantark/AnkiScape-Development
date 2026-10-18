"""A Fish Flingers game lasts its 2012 ten minutes at every game speed (decision 7).

The eight catches spread over the 1,000-tick game (owner, Q4), so the card a
game ends on depends on the speed, but the same catch rolls give the same score,
medals, tokens and payout.
"""

import copy
import random
import re
import sys
import types
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.fish_flingers_data import FISH_FLINGERS_EVENT_CATCHES
from ankiscape.logic.fish_flingers_logic import (
    apply_fish_flingers_review_pure,
    enter_fish_flingers_pure,
)
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


def _entered_player() -> dict:
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["fishing_level"] = 99
    player, entered, info = enter_fish_flingers_pure(player)
    assert entered, info
    return player


def _catch_number(result: dict) -> int:
    return int(re.search(r"(\d+)/\d+ catches", result["status"]).group(1))


class FishFlingersGameLengthTests(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _addon(self, speed: int, seed: int):
        addon = _load_addon_as_package("ankiscape_fish_flingers_length")
        addon._state.player_data = _entered_player()
        addon._state.current_skill = "Utility / Activities"
        addon._review_action_multiplier = lambda: speed
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._show_exp = lambda *_args, **_kwargs: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        # A fresh sequence per game: only the step that lands a catch draws, so
        # every speed sees the same catch rolls.
        self.enterContext(patch.object(addon.random, "random", random.Random(seed).random))
        return addon

    @staticmethod
    def _answer(addon) -> dict:
        addon._state.exp_awarded = False
        addon.on_good_answer()
        return addon._state.player_data

    def _play_one_game(self, speed: int):
        addon = self._addon(speed, seed=2012)
        for card in range(1, 200):
            player = self._answer(addon)
            if player["fish_flingers_events_completed"]:
                return card, (
                    player["fish_flingers_game_log"][-1],
                    player["fish_flingers_tokens"],
                    player["fishing_exp"],
                )
        self.fail(f"the game at x{speed} did not end within 200 cards")

    def test_a_game_ends_on_its_ten_minute_card_with_the_same_result_at_every_speed(self):
        games = {speed: self._play_one_game(speed) for speed in (10, 1, 9)}
        self.assertEqual({speed: card for speed, (card, _result) in games.items()}, {10: 17, 1: 167, 9: 19})
        results = [result for _card, result in games.values()]
        self.assertEqual(results[1], results[0])
        self.assertEqual(results[2], results[0])
        self.assertEqual(results[0][0]["medals"], 2, "Junior and Master Angler are automatic")

    def test_undo_restores_the_game_exactly(self):
        addon = self._addon(10, seed=3)
        for _card in range(2):
            self._answer(addon)
        before = copy.deepcopy(addon._state.player_data)
        # The third x10 card crosses tick 125, where the first catch lands.
        after = self._answer(addon)
        self.assertEqual(after["fish_flingers"]["ticks_elapsed"], 180)
        self.assertGreater(after["fish_flingers"]["fish_caught"], 0)
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, before)


class FishFlingersSaveMigrationTests(unittest.TestCase):
    def test_an_active_version_2_game_resumes_at_its_next_catch(self):
        """A save from before ticks counted landed catches; none is lost or played twice."""
        rolls = random.Random(11)
        player = _entered_player()
        landed = 0
        while landed < 3:
            player, result = apply_fish_flingers_review_pure(player, rolls.random)
            landed += int(result["catch_landed"])
        legacy = copy.deepcopy(player)
        session = legacy["fish_flingers"]
        del session["ticks_elapsed"]
        session.update(version=2, review=3)
        legacy_rolls = copy.deepcopy(rolls)

        def finish(game: dict, game_rolls: random.Random) -> tuple[list[int], dict]:
            numbers = []
            for _step in range(1_000):
                game, result = apply_fish_flingers_review_pure(game, game_rolls.random)
                if result["catch_landed"]:
                    numbers.append(_catch_number(result))
                if result["terminal"]:
                    return numbers, game["fish_flingers_game_log"][-1]
            self.fail("the game did not end")

        resumed = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(resumed["fish_flingers"]["perfect_tackles"], 1)
        resumed_catches, resumed_record = finish(resumed, legacy_rolls)
        uninterrupted_catches, uninterrupted_record = finish(player, rolls)
        self.assertEqual(resumed_catches, list(range(4, FISH_FLINGERS_EVENT_CATCHES + 1)))
        self.assertEqual(resumed_catches, uninterrupted_catches)
        self.assertEqual(resumed_record, uninterrupted_record)


if __name__ == "__main__":
    unittest.main()
