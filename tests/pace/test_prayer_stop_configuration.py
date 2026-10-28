"""Prayer reaching zero ends the card it happens in whenever a draining
prayer runs, whether the player chose it or the game picked it; a card that
starts at zero fights on without prayer (decision 5)."""

from dataclasses import replace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.data.prayer_data import COMBAT_PRAYERS_BY_ID
from tests.pace.test_combat_chain import player_hits_only
from tests.pace.test_combat_danger_stops import answer_combat
from tests.test_combat_logic import _player


class PrayerStopConfigurationTests(unittest.TestCase):
    def test_a_save_with_the_retired_off_uptime_prays_like_a_ticked_box(self):
        player = _player(combat_auto_flee=False, prayer_level=99, combat_prayer_points=1,
                         combat_prayer_drain_counter=59.0,
                         combat_selected_prayers=["thick_skin"], combat_prayer_uptime="off")
        ctx, _calls, ok = answer_combat(player)
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "prayer_empty")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 1)

    def test_the_game_picked_prayers_running_out_of_points_end_the_card(self):
        player = _player(combat_auto_flee=False, prayer_level=10, combat_prayer_points=1)
        ctx, _calls, ok = answer_combat(player)
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertTrue(result["prayers"])
        self.assertEqual(ctx.card.stop_reason, "prayer_empty")
        self.assertLess(result["ticks_elapsed"], 60)
        self.assertEqual(ctx.player_data["combat_prayer_points"], 0)

    def test_running_out_keeps_the_chosen_prayers_for_the_fight_after_a_refill(self):
        player = _player(combat_auto_flee=False, prayer_level=10, combat_prayer_points=1,
                         combat_selected_prayers=["thick_skin"])
        ctx, _calls, ok = answer_combat(player)
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "prayer_empty")
        self.assertEqual(ctx.player_data["combat_selected_prayers"], ["thick_skin"])
        refilled = dict(ctx.player_data, combat_prayer_points=100)
        ctx, _calls, ok = answer_combat(refilled)
        self.assertTrue(ok)
        self.assertEqual(ctx.player_data["combat_last_result"]["prayers"], ("thick_skin",))

    def test_disabled_prayers_with_saved_uptime_and_no_points_spend_the_card(self):
        player = _player(combat_auto_flee=False, combat_prayer_points=0,
                         combat_prayers_enabled=False, combat_selected_prayers=["thick_skin"],
                         combat_prayer_uptime="100")
        ctx, _calls, ok = answer_combat(player)
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 60)

    def test_a_prayer_without_point_drain_does_not_stop_an_empty_card(self):
        player = _player(combat_auto_flee=False, combat_prayer_points=0,
                         combat_selected_prayers=["thick_skin"], combat_prayer_uptime="100")
        with patch.dict(COMBAT_PRAYERS_BY_ID, {
            "thick_skin": replace(COMBAT_PRAYERS_BY_ID["thick_skin"], drain=0),
        }):
            ctx, _calls, ok = answer_combat(player)
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 60)

    def test_prayer_running_out_ends_that_card_and_the_next_card_fights_on_without_it(self):
        player = _player(combat_auto_flee=False, prayer_level=99, combat_prayer_points=1,
                         combat_prayer_drain_counter=59.0,
                         combat_selected_prayers=["thick_skin"], combat_prayer_uptime="100")
        ctx, _calls, ok = answer_combat(player, hits=player_hits_only)
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "prayer_empty")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 1)
        enemy_lifepoints = ctx.player_data["combat_encounter"]["enemy_lifepoints"]
        ctx, _calls, ok = answer_combat(ctx.player_data, hits=player_hits_only)
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((ctx.card.stop_reason, result["ticks_elapsed"]), ("", 60))
        self.assertLess(ctx.player_data["combat_encounter"]["enemy_lifepoints"], enemy_lifepoints)
        self.assertEqual(ctx.player_data["combat_selected_prayers"], ["thick_skin"])
