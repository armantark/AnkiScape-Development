"""Short timers drain by each card's time budget (owner assumption 4).

A card buys six ticks per unit of game speed. A countdown whose source value is
a duration counts those ticks, so it lasts the same play time at every speed:
fewer cards at a higher speed, never a different number of ticks.
"""

import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.summoning_data import SUMMONING_POUCHES_BY_ID
from ankiscape.logic.gnome_restaurant_logic import (
    apply_gnome_restaurant_command_pure,
    gnome_restaurant_view_pure,
    sanitize_gnome_restaurant_state_pure,
)
from ankiscape.logic.summoning_logic import (
    advance_summoning_world_tick_pure,
    default_summoning_state_pure,
    sanitize_summoning_state_pure,
    summon_familiar_pure,
)
from tests.test_gnome_restaurant import _hired, _rng
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


def _summoned(familiar_id: str, pouch_name: str) -> dict:
    data = {
        "summoning_level": 99,
        "constitution_level": 99,
        "inventory": {pouch_name: 1},
        "summoning_state": {
            **default_summoning_state_pure(),
            "summoning_points_current": 99,
        },
    }
    data, ok, _ = summon_familiar_pure(data, familiar_id)
    assert ok
    return data


class _HostCase(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _addon(self, speed: int, player_data: dict):
        addon = _load_addon_as_package("ankiscape_short_timers")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": speed}))
        addon._state.player_data = player_data
        addon._state.current_skill = "None"
        return addon

    @staticmethod
    def _answer(addon, ease: int) -> dict:
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), ease, lambda _self, _ease: "answered")
        return addon._state.player_data


class FamiliarLifetimeTests(_HostCase):
    def test_a_44_minute_familiar_lasts_74_cards_at_speed_ten(self):
        # 4,400 ticks at 60 a card: the 74th card ends it. Again spends time too.
        addon = self._addon(10, _summoned("bunyip", "Bunyip pouch"))
        for card in range(1, 75):
            player = self._answer(addon, 1 if card % 3 == 0 else 3)
            follower = player["summoning_state"]["active_follower"]
            if card < 74:
                self.assertEqual(follower["remaining_ticks"], 4_400 - 60 * card)
        self.assertEqual(follower, {})

    def test_a_44_minute_familiar_lasts_734_cards_at_speed_one(self):
        player = _summoned("bunyip", "Bunyip pouch")
        for card in range(1, 735):
            self.assertTrue(player["summoning_state"]["active_follower"], card)
            player, result = advance_summoning_world_tick_pure(player, card_ticks=6)
        self.assertEqual(result["expired_familiar"], "bunyip")

    def test_point_drain_totals_the_source_amount_at_both_speeds(self):
        pack_yak = SUMMONING_POUCHES_BY_ID["packyak"]
        for card_ticks in (6, 60):
            player = _summoned("packyak", "Pack yak pouch")
            before = player["summoning_state"]["summoning_points_current"]
            while player["summoning_state"]["active_follower"]:
                player, _ = advance_summoning_world_tick_pure(player, card_ticks=card_ticks)
            self.assertEqual(
                before - player["summoning_state"]["summoning_points_current"],
                pack_yak.level - pack_yak.summoning_point_cost,
                card_ticks,
            )


class SpecialMoveRechargeTests(unittest.TestCase):
    def test_recharge_is_fifteen_points_per_fifty_ticks_of_play_at_both_speeds(self):
        # 180 ticks of play: 30 cards at speed 1, 3 cards at speed 10.
        for card_ticks, cards in ((6, 30), (60, 3)):
            player = {
                "summoning_level": 99,
                "summoning_state": {
                    **default_summoning_state_pure(),
                    "special_move_points_current": 0,
                },
            }
            for _ in range(cards):
                player, _ = advance_summoning_world_tick_pure(player, card_ticks=card_ticks)
            state = player["summoning_state"]
            self.assertEqual(state["special_move_points_current"], 3 * 15, card_ticks)
            self.assertEqual(state["special_move_recharge_residual"], 30, card_ticks)


class SummoningMigrationTests(unittest.TestCase):
    def test_saved_card_counts_keep_their_remaining_source_minutes(self):
        # Before ticks, one answered card stood for two source minutes.
        state = sanitize_summoning_state_pure(
            {
                "active_follower": {
                    "kind": "familiar",
                    "entity_id": "packyak",
                    "remaining_reviews": 5,
                    "max_reviews": 29,
                    "summoning_point_drain_residual": 7,
                },
                "triple_charm_reviews_remaining": 3,
                "cargo_events": [
                    {
                        "event_id": 1,
                        "items": {"Coal": 1},
                        "remaining_reviews": 2,
                    }
                ],
            },
            summoning_level=99,
        )
        follower = state["active_follower"]
        self.assertEqual(
            (follower["remaining_ticks"], follower["max_ticks"]), (1_000, 5_800)
        )
        self.assertEqual(follower["summoning_point_drain_residual"], 1_400)
        self.assertNotIn("remaining_reviews", follower)
        self.assertNotIn("max_reviews", follower)
        self.assertEqual(state["triple_charm_ticks_remaining"], 600)
        self.assertEqual(state["cargo_events"][0]["remaining_ticks"], 400)
        self.assertNotIn("triple_charm_reviews_remaining", state)


class GnomeRestaurantWindowTests(_HostCase):
    def test_the_easy_window_lasts_ten_successful_other_target_cards_at_speed_ten(self):
        player, ok, info = apply_gnome_restaurant_command_pure(
            _hired(), "accept_order", {"difficulty": "easy"}, _rng([0.0])
        )
        self.assertTrue(ok, info)
        addon = self._addon(10, player)
        for card in range(1, 11):
            self._answer(addon, 1)
            order = addon._state.player_data["gnome_restaurant"]["order"]
            self.assertEqual(order["ticks_left"], 600 - 60 * (card - 1), "Again pauses")
            self._answer(addon, 3)
            self.assertEqual(
                addon._state.player_data["gnome_restaurant"]["order"]["ticks_left"],
                600 - 60 * card,
            )
        view = gnome_restaurant_view_pure(addon._state.player_data)
        self.assertEqual((view["order_minutes_left"], view["punctuality_pct"]), (0, 0))

    def test_shown_minutes_round_up_from_the_ticks_left(self):
        player, _ok, _info = apply_gnome_restaurant_command_pure(
            _hired(), "accept_order", {"difficulty": "hard"}, _rng([0.0])
        )
        player["gnome_restaurant"]["order"]["ticks_left"] = 1_040
        view = gnome_restaurant_view_pure(player)
        self.assertEqual((view["order_minutes_left"], view["order_limit_minutes"]), (11, 11))
        self.assertEqual(view["punctuality_pct"], 95)

    def test_a_saved_minutes_window_keeps_its_remaining_minutes(self):
        player, _ok, _info = apply_gnome_restaurant_command_pure(
            _hired(), "accept_order", {"difficulty": "hard"}, _rng([0.0])
        )
        order = dict(player["gnome_restaurant"]["order"])
        del order["ticks_left"]
        order["minutes_left"] = 5
        state = sanitize_gnome_restaurant_state_pure(
            {**player["gnome_restaurant"], "order": order}
        )
        self.assertEqual(state["order"]["ticks_left"], 500)
        self.assertNotIn("minutes_left", state["order"])


class TemporaryEffectTests(_HostCase):
    def test_magic_charge_lasts_twelve_successful_non_combat_cards_at_speed_ten(self):
        # 700 ticks at 60 a card; Again spends none of it.
        addon = self._addon(
            10, {"magic_charge_active": True, "magic_charge_ticks_remaining": 700}
        )
        for card in range(1, 13):
            self.assertTrue(self._answer(addon, 1)["magic_charge_active"])
            player = self._answer(addon, 3)
            self.assertEqual(
                player["magic_charge_ticks_remaining"], max(0, 700 - 60 * card)
            )
            self.assertEqual(player["magic_charge_active"], card < 12)


if __name__ == "__main__":
    unittest.main()
