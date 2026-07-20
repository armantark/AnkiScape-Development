import unittest

from logic_pure import advance_temporary_effects_pure
from shooting_star_data import (
    SHOOTING_STAR_ORE_BONUS_TICKS,
    SHOOTING_STAR_STARDUST_CAP,
)
from shooting_star_logic import (
    advance_shooting_star_world_clock_pure,
    apply_shooting_star_exchange_pure,
    apply_shooting_star_review_pure,
    default_shooting_star_state_pure,
    ensure_shooting_star_state_pure,
    set_shooting_star_preferences_pure,
    shooting_star_view_pure,
)


def _player(*, answered=20, mining_level=99):
    return {
        "shop_market_clock": {
            "version": 1,
            "answered_cards": answered,
            "market_tick": answered,
        },
        "mining_level": mining_level,
        "mining_exp": 0.0,
        "inventory": {},
        "world_population_profile": "normal",
        "shooting_star": default_shooting_star_state_pure(),
    }


class TestShootingStarLogic(unittest.TestCase):
    def test_review_clock_spawns_a_period_layer_and_reports_next_star(self):
        waiting = _player(answered=19)
        waiting, events = advance_shooting_star_world_clock_pure(waiting)
        self.assertEqual(events, ())
        self.assertEqual(shooting_star_view_pure(waiting)["next_reviews"], 1)

        waiting["shop_market_clock"]["answered_cards"] = 20
        active, events = advance_shooting_star_world_clock_pure(waiting)
        self.assertEqual(events[0]["kind"], "spawned")
        view = shooting_star_view_pure(active)
        self.assertTrue(view["active"])
        self.assertIn(view["current_size"], range(1, 10))
        self.assertEqual(view["required_level"], view["current_size"] * 10)

    def test_advanced_preferences_constrain_the_next_starting_size(self):
        player, ok, _ = set_shooting_star_preferences_pure(
            _player(answered=20),
            automation_mode="advanced",
            preferred_sizes=(2, 4),
            population_profile="quiet",
        )
        self.assertTrue(ok)
        player, _ = advance_shooting_star_world_clock_pure(player)
        view = shooting_star_view_pure(player)
        self.assertIn(view["starting_size"], {2, 4})
        self.assertEqual(view["population_profile"], "quiet")

    def test_tag_requires_no_pickaxe_but_only_the_first_attempt(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        event = player["shooting_star"]["active_event"]
        event["tag_candidate"] = True
        event["crowd_dust_removed"] = 0

        tagged, ok, result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=False,
        )
        self.assertTrue(ok)
        self.assertTrue(result["tag_only"])
        self.assertEqual(result["tag_xp"], 75 * 99)

        _same, ok, result = apply_shooting_star_review_pure(
            tagged,
            has_usable_pickaxe=False,
        )
        self.assertFalse(ok)
        self.assertIn("pickaxe", result["reason"])

    def test_casual_waits_through_inaccessible_layers(self):
        player, _ = advance_shooting_star_world_clock_pure(
            _player(mining_level=10)
        )
        event = player["shooting_star"]["active_event"]
        event["current_size"] = 9
        event["starting_size"] = 9
        event["layer_remaining"] = 15
        player["shooting_star"]["active_event"] = event

        waited, ok, result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )
        self.assertTrue(ok)
        self.assertTrue(result["waiting"])
        self.assertEqual(result["required_level"], 90)
        self.assertEqual(waited["inventory"].get("Stardust", 0), 0)

    def test_dust_cap_does_not_stop_layer_xp_or_depletion(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        player["inventory"]["Stardust"] = SHOOTING_STAR_STARDUST_CAP
        before = player["shooting_star"]["active_event"]["layer_remaining"]
        updated, ok, result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )
        self.assertTrue(ok)
        self.assertGreater(result["dust_xp"], 0)
        self.assertEqual(result["dust_added"], 0)
        self.assertEqual(
            updated["shooting_star"]["active_event"]["layer_remaining"],
            before - 1,
        )

    def test_final_dust_releases_sprite_and_manual_exchange_scales_rewards(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        event = player["shooting_star"]["active_event"]
        event.update(
            {
                "starting_size": 1,
                "current_size": 1,
                "layer_remaining": 1,
                "total_mass": 1_200,
                "crowd_dust_removed": 1_199,
                "player_dust_mined": 0,
            }
        )
        player["shooting_star"]["active_event"] = event
        player["inventory"]["Stardust"] = 99

        released, ok, result = apply_shooting_star_review_pure(
            player,
            has_usable_pickaxe=True,
        )
        self.assertTrue(ok)
        self.assertTrue(result["sprite_released"])
        self.assertTrue(shooting_star_view_pure(released)["can_exchange"])

        exchanged, ok, reward = apply_shooting_star_exchange_pure(released)
        self.assertTrue(ok)
        self.assertEqual(reward["dust"], 100)
        self.assertEqual(reward["rewards"]["Cosmic rune"], 76)
        self.assertEqual(reward["rewards"]["Astral rune"], 26)
        self.assertEqual(reward["rewards"]["Gold ore"], 10)
        self.assertEqual(reward["rewards"]["Coins"], 25_001)
        self.assertEqual(exchanged["inventory"]["Stardust"], 0)
        self.assertEqual(
            exchanged["shooting_star"]["ore_bonus_ticks_remaining"],
            SHOOTING_STAR_ORE_BONUS_TICKS,
        )

    def test_sprite_expiry_preserves_dust_for_a_later_star(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        event = player["shooting_star"]["active_event"]
        event.update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_card": 22,
            }
        )
        player["shooting_star"]["active_event"] = event
        player["inventory"]["Stardust"] = 50
        player["shop_market_clock"]["answered_cards"] = 22

        expired, events = advance_shooting_star_world_clock_pure(player)
        self.assertEqual(events[0]["reason"], "sprite_expired")
        self.assertEqual(expired["inventory"]["Stardust"], 50)
        self.assertEqual(expired["shooting_star"]["active_event"], {})

    def test_released_sprite_does_not_repeat_its_world_event(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        event = player["shooting_star"]["active_event"]
        event.update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_card": 22,
            }
        )
        player["shooting_star"]["active_event"] = event
        player["shop_market_clock"]["answered_cards"] = 21

        still_released, events = advance_shooting_star_world_clock_pure(player)
        self.assertEqual(events, ())
        self.assertTrue(
            still_released["shooting_star"]["active_event"]["sprite_released"]
        )

    def test_corrupt_zero_size_event_is_repaired_before_mining(self):
        player, _ = advance_shooting_star_world_clock_pure(_player())
        player["shooting_star"]["active_event"]["current_size"] = 0
        repaired = ensure_shooting_star_state_pure(player)
        self.assertEqual(
            repaired["shooting_star"]["active_event"]["current_size"],
            repaired["shooting_star"]["active_event"]["starting_size"],
        )

    def test_ore_bonus_uses_the_shared_review_tick_clock(self):
        player = _player()
        player["shooting_star"]["ore_bonus_ticks_remaining"] = 1_500

        advanced = advance_temporary_effects_pure(
            player,
            elapsed_ticks=50,
        )

        self.assertEqual(
            advanced["shooting_star"]["ore_bonus_ticks_remaining"],
            1_450,
        )
        self.assertEqual(
            player["shooting_star"]["ore_bonus_ticks_remaining"],
            1_500,
        )


if __name__ == "__main__":
    unittest.main()
