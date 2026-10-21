"""Calendar growth keeps fractional card time and crosses the logout gap."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic.farming_logic import advance_farm_clock_pure, sanitize_farming_state_pure
from tests.test_farming import _state
from tests.pace.test_short_timers import _HostCase


def herb_player():
    player = _state()
    player["farm_patches"]["falador_herb"].update({"crop_id": "guam", "planted_at": 0, "protected": True})
    return player


class CalendarFarmingTests(unittest.TestCase):
    def test_fractional_minutes_survive_sanitizing_and_mature_an_eighty_minute_herb(self):
        player = herb_player()
        for _ in range(133):
            player, _ = advance_farm_clock_pure(player, 0.6)
        self.assertEqual(player["farm_clock_minutes"], 79.8)
        self.assertEqual(player["farm_patches"]["falador_herb"]["stage"], 3)
        player, info = advance_farm_clock_pure(player, 0.6)
        self.assertEqual(player["farm_clock_minutes"], 80.4)
        self.assertEqual(player["farm_patches"]["falador_herb"]["stage"], 4)
        self.assertEqual(info["minutes"], 0.6)
        self.assertEqual(sanitize_farming_state_pure(player)["farm_clock_minutes"], 80.4)

    def test_disease_is_processed_stage_by_stage_during_a_large_jump(self):
        player = herb_player()
        player["farm_patches"]["falador_herb"].update({"stage": 1, "protected": False})
        before = copy.deepcopy(player)
        player, info = advance_farm_clock_pure(player, 1440, lambda: 0.0)
        patch = player["farm_patches"]["falador_herb"]
        self.assertTrue(patch["dead"])
        self.assertFalse(patch["diseased"])
        self.assertEqual([row["event"] for row in info["events"]], ["crop_diseased", "crop_died"])
        self.assertEqual(before["farm_clock_minutes"], 0)

    def test_fractional_plant_and_regrowth_timestamps_are_not_rounded_down(self):
        player = herb_player()
        player["farm_clock_minutes"] = 0.66
        record = player["farm_patches"]["falador_herb"]
        record.update({"planted_at": 0.66, "last_regrowth_at": 0.66, "next_regrowth_at": 20.66})
        clean = sanitize_farming_state_pure(player)
        self.assertEqual(clean["farm_clock_minutes"], 0.66)
        self.assertEqual(clean["farm_patches"]["falador_herb"]["planted_at"], 0.66)
        self.assertEqual(clean["farm_patches"]["falador_herb"]["next_regrowth_at"], 20.66)


class CalendarFarmingHostTests(_HostCase):
    def test_again_and_success_use_the_same_calendar_delta_and_boundary_jump(self):
        addon = self._addon(10, herb_player())
        addon._state.player_data.update({
            "shop_market_clock": {"answered_cards": 238, "market_tick": 0},
            "world_clock": {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 14280},
        })
        first = self._answer(addon, 1)
        self.assertEqual(first["farm_clock_minutes"], 0.6)
        boundary = self._answer(addon, 3)
        self.assertEqual(boundary["farm_clock_minutes"], 1297.2)
        self.assertEqual(boundary["farm_patches"]["falador_herb"]["stage"], 4)
