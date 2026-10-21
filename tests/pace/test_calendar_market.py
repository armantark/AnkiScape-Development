"""Shop and Exchange market ticks spend calendar time, including the daily gap."""

import pkg_alias  # noqa: F401
from tests.pace.test_short_timers import _HostCase


class CalendarMarketTests(_HostCase):
    def test_ten_speed_ten_answers_make_one_market_tick_including_again(self):
        addon = self._addon(10, {"inventory": {}})
        for card in range(1, 11):
            player = self._answer(addon, 1 if card % 2 else 3)
            self.assertEqual(player["shop_market_clock"]["answered_cards"], card)
            self.assertEqual(player["shop_market_clock"]["market_tick"], card // 10)

    def test_existing_market_time_is_kept_when_a_save_adopts_play_speed(self):
        addon = self._addon(10, {"inventory": {}, "shop_market_clock": {"answered_cards": 81, "market_tick": 81}})
        after = self._answer(addon, 1)
        self.assertEqual(after["shop_market_clock"], {"version": 1, "answered_cards": 82, "market_tick": 81})
        self.assertEqual(after["world_clock"]["in_day_ticks"], 48660)

    def test_logout_gap_restocks_a_depleted_shop(self):
        from tests.shops.test_shop_restock import TestShopRestock

        fixture = TestShopRestock()
        fixture.setUp()
        fixture.buy("Small fishing net", 5)
        player = fixture.player
        player.update({
            "shop_market_clock": {"answered_cards": 238, "market_tick": 23},
            "world_clock": {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 14280},
        })
        addon = self._addon(10, player)
        after = self._answer(addon, 1)
        self.assertEqual(after["shop_market_clock"]["market_tick"], 23)
        self.assertEqual(fixture.stock("Small fishing net", after), 0)
        after = self._answer(addon, 3)
        self.assertEqual(after["shop_market_clock"]["market_tick"], 240)
        self.assertGreater(fixture.stock("Small fishing net", after), 0)
