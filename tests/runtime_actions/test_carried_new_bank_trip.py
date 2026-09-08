"""A newly due trip consumes credit and teleport only at its original boundary."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic.wicked_hood_logic import default_wicked_hood_state_pure
from ankiscape.runtime.runtime_actions_carried_overlay import _initialize_due_bank_trip
from tests.test_runtime_actions import _context


class TestInitializeDueBankTrip(unittest.TestCase):
    def test_credit_is_consumed_before_roll_and_teleport_after_roll(self):
        hood = default_wicked_hood_state_pure()
        hood.update(fed_altars=["air"], pending_altar_teleport="air")
        player = {"inventory": {}, "equipment": {"head": "Wicked hood"},
                  "agility_level": 1, "agility_run_energy_credit_pct": 50,
                  "wicked_hood": hood, "shop_market_clock": {"answered_cards": 0}}
        ctx = _context(player)
        observations = []

        def roll():
            observations.append(copy.deepcopy(player))
            return 0.0

        ctx.random_random = roll
        view = {"Rune essence": 28}
        before_view = copy.deepcopy(view)
        profile, cost, phases, teleported = _initialize_due_bank_trip(
            ctx, "runecrafting", "craft_air_runes", view, "air"
        )
        self.assertIs(ctx.player_data, player)
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]["agility_run_energy_credit_pct"], 0)
        self.assertEqual(observations[0]["wicked_hood"]["pending_altar_teleport"], "air")
        self.assertNotIn("agility_last_travel", observations[0])
        self.assertEqual(player["wicked_hood"]["pending_altar_teleport"], "")
        self.assertTrue(teleported)
        self.assertEqual((cost, [phase["id"] for phase in phases]), (5, ["return", "bank"]))
        self.assertEqual(player["agility_last_travel"]["scheduled_reviews"], 10)
        self.assertEqual(player["agility_last_travel"]["adjusted_reviews"], profile.adjusted_reviews)
        self.assertEqual(player["agility_last_travel"]["run_energy_credit_used_pct"], 50)
        self.assertEqual(view, before_view)

    def test_zero_duration_never_draws_and_only_moving_credit_is_consumed(self):
        for skill, target, credit_after in (("mining", "copper_ore", 0),
                                            ("hunter", "crimson_swift", 100)):
            with self.subTest(skill=skill):
                player = {"inventory": {}, "agility_run_energy_credit_pct": 100}
                ctx = _context(player)

                def forbidden_roll():
                    self.fail("A zero-duration trip must not draw RNG.")

                ctx.random_random = forbidden_roll
                profile, cost, phases, teleported = _initialize_due_bank_trip(
                    ctx, skill, target, {}, ""
                )
                self.assertEqual((profile.adjusted_reviews, cost, phases, teleported), (0, 0, (), False))
                self.assertEqual(player["agility_run_energy_credit_pct"], credit_after)
                self.assertEqual(player["agility_last_travel"]["charged_reviews"], 0)

    def test_fractional_trip_keeps_both_rounding_routes_and_nonmatching_teleport(self):
        for roll, cost in ((0.0, 20), (1.0, 19)):
            with self.subTest(roll=roll):
                hood = default_wicked_hood_state_pure()
                hood.update(fed_altars=["air", "water"], pending_altar_teleport="water")
                player = {"inventory": {}, "equipment": {"head": "Wicked hood"},
                          "agility_level": 1, "wicked_hood": hood,
                          "shop_market_clock": {"answered_cards": 0}}
                ctx = _context(player, random_values=[roll])
                _profile, actual, phases, teleported = _initialize_due_bank_trip(
                    ctx, "runecrafting", "craft_air_runes", {"Rune essence": 28}, "air"
                )
                self.assertEqual(actual, cost)
                self.assertEqual(sum(phase["reviews"] for phase in phases), cost)
                self.assertFalse(teleported)
                self.assertEqual(player["wicked_hood"]["pending_altar_teleport"], "water")
