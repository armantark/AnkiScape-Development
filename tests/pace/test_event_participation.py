"""Active event rewards must not depend on how cards batch equal play time."""

import copy
import types

import pkg_alias  # noqa: F401
from ankiscape.logic.big_chinchompa_logic import advance_big_chinchompa_world_clock_pure
from ankiscape.logic.shooting_star_logic import (
    advance_shooting_star_world_clock_pure,
    apply_shooting_star_review_pure,
)
from tests.pace.test_calendar_events import _player
from tests.pace.test_short_timers import _HostCase


def _chinchompa():
    player = _player()
    player.update(hunter_level=99, hunter_exp=0.0, current_utility="big_chinchompa")
    player["shop_market_clock"]["answered_cards"] = 60
    player["world_clock"]["in_day_ticks"] = 3600
    player, _ = advance_big_chinchompa_world_clock_pure(player, card_ticks=60)
    player["shop_market_clock"]["answered_cards"] = 82
    player["world_clock"]["in_day_ticks"] = 4920
    player, _ = advance_big_chinchompa_world_clock_pure(player, card_ticks=60)
    return player


def _star():
    player = _player()
    player.update(mining_level=99, mining_exp=0.0, current_utility="shooting_stars",
                  toolbelt={"mining": ["bronze_pickaxe"]})
    player["shop_market_clock"]["answered_cards"] = 1
    player["world_clock"]["in_day_ticks"] = 60
    player, _ = advance_shooting_star_world_clock_pure(player)
    player["shop_market_clock"]["answered_cards"] = 82
    player["world_clock"]["in_day_ticks"] = 4920
    player, _ = advance_shooting_star_world_clock_pure(player)
    # An already-worked star with twenty dust left exposes crowd/player racing.
    while True:
        event = player["shooting_star"]["active_event"]
        remaining = event["total_mass"] - event["crowd_dust_removed"] - event["player_dust_mined"]
        if remaining <= 20:
            return player
        player, ok, info = apply_shooting_star_review_pure(player, has_usable_pickaxe=True)
        assert ok, info


class EventParticipationTests(_HostCase):
    def _play(self, start, speed, ticks=120):
        addon = self._addon(speed, copy.deepcopy(start))
        addon._state.current_skill = "Utility / Activities"
        addon._review_action_multiplier = lambda: speed
        addon.show_error_message = lambda _title, _message: None
        rng = addon.random.getstate()
        self.addCleanup(addon.random.setstate, rng)
        addon.random.seed(2012)
        for _ in range(ticks // (6 * speed)):
            self._answer(addon, 3)
        self.assertEqual(addon._state.player_data["world_clock"]["in_day_ticks"], 4920 + ticks)
        return addon, copy.deepcopy(addon._state.player_data)

    def test_chinchompa_circuits_and_xp_match_for_120_ticks_at_every_speed(self):
        start = _chinchompa()
        outcomes = []
        for speed in (1, 10, 20):
            _, player = self._play(start, speed)
            state = player["big_chinchompa"]
            resolved = [row for row in state["event_log"] if row["kind"] == "resolved"]
            self.assertEqual(len(resolved), 1, speed)
            outcomes.append((resolved[0]["circuits_completed"], player["hunter_exp"],
                             state["competence_points"], player["inventory"]))
        self.assertEqual(outcomes[0][:2], (18, 121500.0))
        self.assertEqual(outcomes, [outcomes[0]] * 3)

    def test_star_mining_attempts_xp_and_seeded_drops_match_for_equal_time(self):
        start = _star()
        before = start["shooting_star"]["active_event"]["player_dust_mined"]
        outcomes = []
        for speed in (1, 10, 20):
            _, player = self._play(start, speed)
            event = player["shooting_star"]["active_event"]
            self.assertTrue(event["sprite_released"], speed)
            attempts = event["player_dust_mined"] - before
            self.assertGreater(attempts, 0)
            self.assertLess(attempts, 20)
            outcomes.append((attempts, player["mining_exp"], player["inventory"],
                             event["crowd_dust_removed"], event["sprite_expires_tick"]))
        self.assertEqual(outcomes, [outcomes[0]] * 3)

    def test_crowd_step_settlement_undo_restores_the_complete_save_and_rng(self):
        for fixture in (_chinchompa, _star):
            for speed in (1, 10, 20):
                with self.subTest(event=fixture.__name__, speed=speed):
                    addon = self._addon(speed, fixture())
                    addon._review_action_multiplier = lambda: speed
                    addon._state.current_skill = "Utility / Activities"
                    before = copy.deepcopy(addon._state.player_data)
                    rng = addon.random.getstate()
                    self.addCleanup(addon.random.setstate, rng)
                    first = copy.deepcopy(self._answer(addon, 3))
                    after_rng = addon.random.getstate()
                    addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
                    self.assertEqual(addon._state.player_data, before)
                    self.assertEqual(addon.random.getstate(), rng)
                    self.assertEqual(self._answer(addon, 3), first)
                    self.assertEqual(addon.random.getstate(), after_rng)
