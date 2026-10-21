"""Saved prayer choices stop a card only when a draining prayer is on."""

from dataclasses import replace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.data.prayer_data import COMBAT_PRAYERS_BY_ID
from tests.pace.test_combat_danger_stops import answer_combat
from tests.test_combat_logic import _player


class PrayerStopConfigurationTests(unittest.TestCase):
    def test_saved_selection_with_no_points_and_uptime_off_spends_the_card(self):
        player = _player(combat_auto_flee=False, combat_prayer_points=0,
                         combat_selected_prayers=["thick_skin"], combat_prayer_uptime="off")
        ctx, _calls, ok = answer_combat(player)
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 60)
        self.assertEqual(ctx.player_data["combat_prayer_points"], 0)

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

    def test_an_enabled_draining_prayer_with_no_points_stops_immediately(self):
        player = _player(combat_auto_flee=False, combat_prayer_points=0,
                         combat_selected_prayers=["thick_skin"], combat_prayer_uptime="100")
        ctx, _calls, ok = answer_combat(player)
        self.assertTrue(ok)
        self.assertEqual(ctx.card.stop_reason, "prayer_empty")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 1)
