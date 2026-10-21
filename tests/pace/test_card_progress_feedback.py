"""Card progress messages describe the whole card, including its time debt."""

import copy
import importlib
import random
import types
from unittest.mock import patch

from tests.pace.test_short_timers import _HostCase
from tests.pace.test_stun_debt import _ThievingCardCase
from tests.pace.test_fish_flingers_length import _entered_player


class FishFlingersProgressFeedbackTests(_HostCase):
    def _answer_and_check_feedback(self, addon, speed, card):
        before = copy.deepcopy(addon._state.player_data["fish_flingers"])
        addon._state.player_data["review_event_log"] = []
        player = self._answer(addon, 3)
        after = player["fish_flingers"]
        lines = [row["text"] for row in player["review_event_log"] if row["kind"] == "activity"]
        waiting = [line for line in lines if line.startswith("Working on catch ")]
        no_catch = bool(after) and after["fish_caught"] == before["fish_caught"]
        self.assertEqual(len(waiting), int(no_catch), (speed, card, lines))
        if no_catch:
            self.assertEqual(lines, waiting)
        return bool(after)

    def _play_game(self, speed):
        addon = self._addon(speed, _entered_player())
        addon._state.current_skill = "Utility / Activities"
        with patch.object(addon.random, "random", random.Random(2012).random):
            for card in range(1, 200):
                if not self._answer_and_check_feedback(addon, speed, card):
                    return
        self.fail(f"Fish Flingers did not end at speed {speed}")

    def test_only_a_card_without_a_catch_shows_one_waiting_line(self):
        for speed in (1, 10, 20):
            with self.subTest(speed=speed):
                self._play_game(speed)


class ThievingRecoveryFeedbackTests(_ThievingCardCase):
    def test_a_held_card_says_why_and_undo_restores_its_cause(self):
        addon = self._addon(1, {1})
        self._answer(addon)
        before = copy.deepcopy(addon._state.player_data)
        self._answer(addon)
        line = "Stun recovery took this card; play resumes on the next card"
        self.assertEqual(addon._state.player_data["review_event_log"][-1]["text"], line)
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, before)
        self._answer(addon)
        self.assertEqual(addon._state.player_data["review_event_log"][-1]["text"], line)
        addon._state.player_data["review_event_log"] = []
        self._answer(addon)
        self.assertNotIn(line, [row["text"] for row in addon._state.player_data["review_event_log"]])

    def test_a_vine_bind_or_step_debt_does_not_claim_thieving_stun_recovery(self):
        for cause in ("vine", "step"):
            with self.subTest(cause=cause):
                addon = self._addon(1, set())
                if cause == "vine":
                    shared = importlib.import_module(f"{addon.__name__}.runtime.runtime_actions_shared")
                    shared._stop_card_at_farm_danger(addon._runtime_action_context(), {"bound": True})
                else:
                    addon._state.player_data["card_tick_debt"] = 6
                self._answer(addon)
                self.assertEqual(self._attempts(addon._state.player_data), (0, 0))
                lines = [row["text"] for row in addon._state.player_data.get("review_event_log", [])]
                self.assertFalse(any("Stun recovery" in line for line in lines), lines)
