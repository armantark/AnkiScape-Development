import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.big_chinchompa_data import (
    BIG_CHINCHOMPA_COMPETENCE_CAP,
    BIG_CHINCHOMPA_MOTH_TIERS,
)
from ankiscape.logic.big_chinchompa_logic import (
    advance_big_chinchompa_world_clock_pure,
    apply_big_chinchompa_review_pure,
    apply_big_chinchompa_reward_purchase_pure,
    big_chinchompa_crowd_target_bps_pure,
    big_chinchompa_view_pure,
    consume_hunter_quota_ticket_pure,
    default_big_chinchompa_state_pure,
    hunter_private_ground_status_pure,
    set_hunter_private_ground_pure,
    set_world_population_profile_pure,
)
from ankiscape.core.constants import EXP_TABLE


def _player(answered_cards=0, hunter_level=1):
    return {
        "shop_market_clock": {"answered_cards": answered_cards},
        "hunter_level": hunter_level,
        "hunter_exp": 0.0,
        "inventory": {},
        "big_chinchompa": default_big_chinchompa_state_pure(),
        "world_population_profile": "normal",
        "hunter_private_ground_targets": [],
    }


class BigChinchompaLogicTests(unittest.TestCase):
    def test_two_review_day_slots_and_rational_twenty_minute_window(self):
        player = _player(59)
        player["world_population_profile"] = "quiet"
        player, events = advance_big_chinchompa_world_clock_pure(player)
        self.assertEqual(events, ())
        self.assertEqual(big_chinchompa_view_pure(player)["next_reviews"], 1)

        player["shop_market_clock"]["answered_cards"] = 60
        player, events = advance_big_chinchompa_world_clock_pure(player)
        self.assertEqual(events[0]["kind"], "spawned")
        view = big_chinchompa_view_pure(player)
        self.assertEqual(view["minutes_remaining"], 20)
        self.assertEqual(view["reviews_remaining"], 3)

        player["shop_market_clock"]["answered_cards"] = 62
        player, _ = advance_big_chinchompa_world_clock_pure(player)
        self.assertTrue(big_chinchompa_view_pure(player)["active"])
        self.assertEqual(big_chinchompa_view_pure(player)["reviews_remaining"], 1)

        player["shop_market_clock"]["answered_cards"] = 63
        player, events = advance_big_chinchompa_world_clock_pure(player)
        self.assertFalse(big_chinchompa_view_pure(player)["active"])
        self.assertEqual(events[0], {"kind": "resolved", "reason": "expired"})
        self.assertEqual(big_chinchompa_view_pure(player)["next_reviews"], 117)

        player["shop_market_clock"]["answered_cards"] = 180
        player, events = advance_big_chinchompa_world_clock_pure(player)
        self.assertEqual(events[0]["kind"], "spawned")

    def test_late_entry_keeps_only_remaining_window(self):
        player = _player(62)
        player, events = advance_big_chinchompa_world_clock_pure(player)
        self.assertEqual(events[0]["slot_card"], 60)
        view = big_chinchompa_view_pure(player)
        self.assertEqual(view["minutes_remaining"], 8)
        self.assertEqual(view["reviews_remaining"], 1)

    def test_late_entry_never_spawns_without_a_complete_review_quantum(self):
        player = _player(63)
        player, events = advance_big_chinchompa_world_clock_pure(player)
        self.assertEqual(events, ())
        self.assertFalse(big_chinchompa_view_pure(player)["active"])
        self.assertEqual(big_chinchompa_view_pure(player)["next_reviews"], 117)

    def test_crowd_curve_is_constant_work_deterministic_and_monotonic(self):
        values = [
            big_chinchompa_crowd_target_bps_pure(
                slot_card=60,
                answered_cards=card,
                seed=12345,
                profile="normal",
            )
            for card in (60, 61, 62, 63, 64)
        ]
        self.assertEqual(values, sorted(values))
        self.assertEqual(
            values,
            [
                big_chinchompa_crowd_target_bps_pure(
                    slot_card=60,
                    answered_cards=card,
                    seed=12345,
                    profile="normal",
                )
                for card in (60, 61, 62, 63, 64)
            ],
        )

    def test_one_review_resolves_whole_jars_and_stops_at_fullness(self):
        player = _player(60, hunter_level=91)
        player, _ = advance_big_chinchompa_world_clock_pure(player)
        player["big_chinchompa"]["active_event"]["player_fullness_bps"] = 9_900
        player, ok, result = apply_big_chinchompa_review_pure(
            player,
            circuits=5,
        )
        self.assertTrue(ok)
        self.assertEqual(result["circuits"], 1)
        self.assertEqual(result["moths"], 15)
        self.assertEqual(result["hunter_xp"], 15 * 450.0)
        self.assertEqual(result["event_points"], 15 * 21)
        self.assertEqual(result["fullness_percent"], 100.0)

    def test_personal_cap_stops_points_but_not_hunter_xp(self):
        player = _player(60, hunter_level=99)
        player, _ = advance_big_chinchompa_world_clock_pure(player)
        event = player["big_chinchompa"]["active_event"]
        event["event_points"] = 1_490
        player, ok, result = apply_big_chinchompa_review_pure(player)
        self.assertTrue(ok)
        self.assertEqual(result["event_points"], 10)
        self.assertEqual(result["hunter_xp"], 6_750.0)
        self.assertTrue(result["personal_cap_reached"])

        player, ok, result = apply_big_chinchompa_review_pure(player)
        self.assertTrue(ok)
        self.assertEqual(result["event_points"], 0)
        self.assertEqual(result["hunter_xp"], 6_750.0)

    def test_all_moth_tiers_preserve_period_rows(self):
        self.assertEqual(
            [
                (tier.hunter_level, tier.xp, tier.points)
                for tier in BIG_CHINCHOMPA_MOTH_TIERS
            ],
            [
                (1, 15.0, 1),
                (13, 50.0, 2),
                (26, 150.0, 5),
                (39, 250.0, 8),
                (52, 300.0, 12),
                (65, 320.0, 15),
                (78, 400.0, 18),
                (91, 450.0, 21),
            ],
        )

    def test_resolution_converts_points_one_for_one_and_caps_wallet(self):
        player = _player(60, hunter_level=99)
        player, _ = advance_big_chinchompa_world_clock_pure(player)
        player["big_chinchompa"]["competence_points"] = 19_900
        player, _ok, _result = apply_big_chinchompa_review_pure(player)
        player["big_chinchompa"]["active_event"]["event_points"] = 315
        player["shop_market_clock"]["answered_cards"] = 64
        player, events = advance_big_chinchompa_world_clock_pure(player)
        self.assertEqual(events[0]["reason"], "expired")
        self.assertEqual(
            player["big_chinchompa"]["competence_points"],
            BIG_CHINCHOMPA_COMPETENCE_CAP,
        )

    def test_reward_shop_items_and_exact_direct_hunter_xp(self):
        player = _player(0, hunter_level=77)
        player["big_chinchompa"]["competence_points"] = 20
        player, ok, result = apply_big_chinchompa_reward_purchase_pure(
            player,
            "grenwall_ticket",
            exp_table=EXP_TABLE,
        )
        self.assertTrue(ok)
        self.assertEqual(result["cost"], 10)
        self.assertEqual(player["inventory"]["Grenwall quota ticket"], 1)

        player, ok, result = apply_big_chinchompa_reward_purchase_pure(
            player,
            "hunter_xp",
            exp_table=EXP_TABLE,
        )
        self.assertTrue(ok)
        self.assertEqual(result["hunter_xp"], 5.0)
        self.assertEqual(player["hunter_exp"], 5.0)

    def test_private_ground_consumes_only_after_success_and_last_ticket_turns_off(self):
        player = _player(0, hunter_level=77)
        player["inventory"]["Grenwall quota ticket"] = 1
        player, ok, result = set_hunter_private_ground_pure(
            player,
            "catch_grenwall",
            True,
        )
        self.assertFalse(ok)
        self.assertIn("carried pack", result["reason"])

        player["carried_inventory"] = {
            "catch_grenwall": {"Grenwall quota ticket": 1}
        }
        player, ok, _ = set_hunter_private_ground_pure(
            player,
            "catch_grenwall",
            True,
        )
        self.assertTrue(ok)
        self.assertTrue(
            hunter_private_ground_status_pure(
                player, "catch_grenwall"
            )["active"]
        )

        # Failed catches never call the successful-catch consumer.
        self.assertEqual(player["inventory"]["Grenwall quota ticket"], 1)
        player, consumed = consume_hunter_quota_ticket_pure(
            player,
            "catch_grenwall",
        )
        self.assertEqual(consumed, "Grenwall quota ticket")
        self.assertEqual(player["inventory"]["Grenwall quota ticket"], 0)
        self.assertFalse(
            hunter_private_ground_status_pure(
                player, "catch_grenwall"
            )["configured"]
        )

    def test_population_profile_is_shared_saved_state(self):
        player, ok, result = set_world_population_profile_pure(
            _player(),
            "busy",
        )
        self.assertTrue(ok)
        self.assertEqual(result["profile"], "busy")
        self.assertEqual(player["world_population_profile"], "busy")


if __name__ == "__main__":
    unittest.main()
