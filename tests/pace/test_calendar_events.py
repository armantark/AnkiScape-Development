"""World events retain their calendar intervals inside each day's play window."""

import copy
import types

import pkg_alias  # noqa: F401
from ankiscape.logic.big_chinchompa_logic import advance_big_chinchompa_world_clock_pure
from ankiscape.logic.crucible_logic import _supreme_event_active
from ankiscape.logic.evil_tree_logic import advance_evil_tree_world_clock_pure
from ankiscape.logic.goblin_raids_logic import advance_goblin_raids_world_clock_pure
from ankiscape.logic.pace.world_clock import advance_world_clock_pure
from ankiscape.logic.shooting_star_logic import advance_shooting_star_world_clock_pure
from tests.pace.test_short_timers import _HostCase


EVENTS = (
    ("goblin_raids", advance_goblin_raids_world_clock_pure),
    ("evil_tree", advance_evil_tree_world_clock_pure),
    ("shooting_star", advance_shooting_star_world_clock_pure),
    ("big_chinchompa", advance_big_chinchompa_world_clock_pure),
)


def _player(length=240):
    return {"inventory": {}, "shop_market_clock": {"answered_cards": 0},
            "world_clock": {"day": 0, "day_start_card": 0, "day_length": length, "in_day_ticks": 0}}


def _advance(player, speed):
    counted = copy.deepcopy(player)
    counted["shop_market_clock"]["answered_cards"] += 1
    counted, clock = advance_world_clock_pure(counted, speed=speed,
                                            next_day_length=counted["world_clock"]["day_length"])
    events = {}
    for key, advance in EVENTS:
        kwargs = {"card_ticks": speed * 6} if key in {"evil_tree", "big_chinchompa"} else {}
        counted, events[key] = advance(counted, **kwargs)
    return counted, events, clock


def _occurrences(speed):
    player = _player()
    observed = {key: [] for key in ("goblin_raids", "evil_tree", "shooting_star", "big_chinchompa", "crucible")}
    champion_active = False
    for card in range(1, 241):
        player, events, _ = _advance(player, speed)
        for key, rows in events.items():
            if any(row["kind"] in {"spawned", "announced"} for row in rows):
                observed[key].append(card)
        active = _supreme_event_active(player)
        if active and not champion_active:
            observed["crucible"].append(card)
        champion_active = active
    return observed


class CalendarEventTests(_HostCase):
    def test_each_event_has_the_ruled_occurrences_and_positions_at_all_three_speeds(self):
        expected = {
            1: {"goblin_raids": [1], "evil_tree": [1], "shooting_star": [1],
                "big_chinchompa": [60], "crucible": [1]},
            10: {"goblin_raids": [1, 200], "evil_tree": [1, 200], "shooting_star": [1, 200],
                 "big_chinchompa": [60, 180], "crucible": [1, 50, 100, 150, 200]},
            20: {"goblin_raids": [1, 100, 175], "evil_tree": [1, 100, 200], "shooting_star": [1, 100, 200],
                 "big_chinchompa": [60, 180], "crucible": [1, 25, 50, 75, 100, 125, 150, 175, 200, 225]},
        }
        # No player participation: raids remain for 90 minutes, trees for 30.
        # Existing active events retain their lifetime rather than being replaced.
        for speed, positions in expected.items():
            with self.subTest(speed=speed):
                observed = _occurrences(speed)
                self.assertEqual(observed, positions)

    def test_adaptive_hundred_card_day_uses_quarter_and_three_quarter_slots(self):
        for speed, expected in ((1, [25]), (10, [25, 75]), (20, [25, 75])):
            with self.subTest(speed=speed):
                player = _player(100)
                slots = []
                for card in range(1, 101):
                    player, events, _ = _advance(player, speed)
                    slots.extend(card for event in events["big_chinchompa"] if event["kind"] == "spawned")
                self.assertEqual(slots, expected)

    def test_running_chinchompa_skips_the_later_slot_and_the_jump_ends_it(self):
        player = _player()
        for _ in range(180):
            player, _, _ = _advance(player, 1)
        self.assertEqual(player["big_chinchompa"]["active_event"]["slot_card"], 60)
        self.assertEqual(player["big_chinchompa"]["last_resolved_slot_card"], 180)
        # Finish early after skipping slot 180: that slot must not start late.
        player["big_chinchompa"]["active_event"]["player_fullness_bps"] = 10_000
        player, events, _ = _advance(player, 1)
        self.assertEqual(events["big_chinchompa"], ({"kind": "resolved", "reason": "full"},))
        self.assertFalse(player["big_chinchompa"]["active_event"])

    def test_no_event_spawns_in_the_jump_and_period_events_return_on_next_play_card(self):
        for speed in (1, 10, 20):
            with self.subTest(speed=speed):
                self._assert_jump_and_resume(speed)

    def _assert_jump_and_resume(self, speed):
        player = _player()
        for _ in range(240):
            player, events, clock = _advance(player, speed)
        self.assertTrue(clock["day_rolled"])
        self.assertFalse(_supreme_event_active(player))
        for key, rows in events.items():
            self.assertFalse(any(row["kind"] in {"spawned", "announced"} for row in rows), key)
            field = "active_raid" if key == "goblin_raids" else "active_event"
            self.assertFalse(player[key][field], key)
        player, events, _ = _advance(player, speed)
        for key in ("goblin_raids", "evil_tree", "shooting_star"):
            self.assertTrue(any(row["kind"] in {"spawned", "announced"} for row in events[key]), key)
        self.assertTrue(_supreme_event_active(player))

    def test_crowd_pressure_follows_steps_at_equal_calendar_time(self):
        states = []
        for speed, cards in ((1, 100), (10, 10), (20, 5)):
            player = _player()
            # Spawn at an identical time, independent of the first card's size.
            player["shop_market_clock"]["answered_cards"] = 60
            player["world_clock"]["in_day_ticks"] = 0
            player, _ = advance_big_chinchompa_world_clock_pure(player)
            player, _ = advance_shooting_star_world_clock_pure(player)
            for _ in range(cards):
                player, _, _ = _advance(player, speed)
            states.append((player["big_chinchompa"]["active_event"]["crowd_fullness_bps"],
                           player["shooting_star"]["active_event"]["crowd_dust_removed"]))
        self.assertGreater(states[0][0], 0)
        self.assertGreater(states[0][1], 0)
        self.assertEqual(states, [states[0]] * 3)

    def test_answer_undo_and_reanswer_restore_spawn_expiry_and_rng(self):
        for card, ticks in ((59, 3540), (93, 5580), (239, 14340)):
            with self.subTest(card=card):
                player = _player()
                player["shop_market_clock"]["answered_cards"] = 60
                player["world_clock"]["in_day_ticks"] = 3600
                player, _ = advance_big_chinchompa_world_clock_pure(player, card_ticks=60)
                if card == 59:
                    player = _player()
                player["shop_market_clock"]["answered_cards"] = card
                player["world_clock"]["in_day_ticks"] = ticks
                addon = self._addon(10, player)
                before = copy.deepcopy(player)
                rng = addon.random.getstate()
                self.addCleanup(addon.random.setstate, rng)
                first = copy.deepcopy(self._answer(addon, 3))
                rng_after = addon.random.getstate()
                self.assertEqual(bool(first["big_chinchompa"]["active_event"]), card == 59)
                addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
                self.assertEqual(addon._state.player_data, before)
                self.assertEqual(addon.random.getstate(), rng)
                self.assertEqual(self._answer(addon, 3), first)
                self.assertEqual(addon.random.getstate(), rng_after)
