"""Real answer/Undo transactions restore calendar consumers and chained Combat."""

import copy
import sys
import types
from unittest.mock import patch

import pkg_alias  # noqa: F401
from tests.pace.test_calendar_farming import herb_player
from tests.pace.test_combat_danger_stops import ENEMY
from tests.pace.test_short_timers import _HostCase
from tests.pace.test_study_volume import RevlogCollection
from tests.test_combat_logic import _player


class CalendarUndoTests(_HostCase):
    def _replay(self, addon):
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
        return first

    def _combat_replay(self, addon):
        addon._state.player_data.update(_player(current_combat_target="chicken", combat_auto_flee=False))
        addon._state.current_skill = "Combat"
        engine = sys.modules[f"{addon.__name__}.logic_pure.logic_pure_combat_engine"]
        enemy = {**ENEMY, "melee_recoil_damage": 33, "stats": {**ENEMY["stats"], "hitpoints": 1}}

        def hits(*_args, **kwargs):
            return (True, 10) if "blocked" in kwargs else (False, 0)

        with patch.dict(addon.runtime_actions.COMBAT_ENEMY_DATA, {"chicken": enemy}), patch.object(engine, "_combat_roll_hit", side_effect=hits):
            after = self._replay(addon)
        self.assertEqual(after["combat_last_result"]["kills"], 2)
        self.assertEqual(after["combat_last_result"]["stop_reason"], "low_lp_no_food")

    def _volume(self, addon, median=300):
        log = RevlogCollection()
        self.addCleanup(log.connection.close)
        for day in range(1, 8):
            log.add_day(day, median)
        addon.mw.col.set_config("ankiscape_world_day_follow_study_volume", True)
        addon.mw.col.db = log
        addon.mw.col.sched = log.sched
        return log

    def test_boundary_adopts_the_median_and_undo_restores_every_consumer_and_rng(self):
        player = herb_player()
        player.update({
            "shop_market_clock": {"answered_cards": 239, "market_tick": 23},
            "world_clock": {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 14340},
            "farm_clock_minutes": 143.4,
            "fish_flingers_tickets": 0,
            "fish_flingers_last_ticket_day": 0,
        })
        addon = self._addon(10, player)
        log = self._volume(addon)
        after = self._replay(addon)
        self.assertEqual(after["world_clock"], {"day": 1, "day_start_card": 240, "day_length": 300, "in_day_ticks": 0})
        self.assertEqual(after["farm_clock_minutes"], 1440)
        self.assertEqual(after["shop_market_clock"]["market_tick"], 240)
        self.assertEqual(after["fish_flingers_tickets"], 2)
        self.assertEqual(log.queries, 2)
        self._combat_replay(addon)

    def test_fixed_length_set_mid_day_takes_effect_only_on_the_boundary_and_replays(self):
        player = {"inventory": {}, "shop_market_clock": {"answered_cards": 238, "market_tick": 23},
                  "world_clock": {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 14280}}
        addon = self._addon(10, player)
        addon.mw.col.set_config("ankiscape_world_day_follow_study_volume", False)
        addon.mw.col.set_config("ankiscape_world_day_cards", 500)
        self.assertEqual(self._answer(addon, 3)["world_clock"]["day_length"], 240)
        after = self._replay(addon)
        self.assertEqual(after["world_clock"]["day_length"], 500)
        self.assertEqual(addon.mw.col.get_config("ankiscape_world_day_cards"), 500)
        self._combat_replay(addon)

    def test_speed_change_adds_six_then_sixty_ticks_and_undo_removes_exactly_sixty(self):
        player = {"inventory": {}, "world_clock": {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 0}}
        addon = self._addon(1, player)
        self.assertEqual(self._answer(addon, 3)["world_clock"]["in_day_ticks"], 6)
        addon.mw.col.set_config("ankiscape_review_action_multiplier", 10)
        after = self._replay(addon)
        self.assertEqual(after["world_clock"]["in_day_ticks"], 66)
        self.assertEqual(addon.mw.col.get_config("ankiscape_review_action_multiplier"), 10)
        self._combat_replay(addon)
