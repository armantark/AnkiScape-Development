"""Live XP/hour parity checks for source-ready cadence routes.

The legacy review-probability adapter is still available behind the explicit
cadence rollback flag. Default gameplay instead resolves each selectable route
through ``cadence_live``. These tests therefore grade the live declarations,
not the retired adapter measurements.
"""

from fractions import Fraction
import unittest

from cadence_kernel import (
    EMBEDDED_PROBABILITY,
    R,
    RATE_LIMITED,
    advance_cadence_pure,
    default_cadence_profile_state_pure,
)
from cadence_live import (
    advance_live_cadence_route_pure,
    resolve_live_cadence_route_pure,
)
from constants import (
    COOKING_DATA,
    FIREMAKING_DATA,
    FISHING_DATA,
    HUNTER_DATA,
    ORE_DATA,
    TREE_DATA,
)
from tools.sourced_xp_rates import BY_SKILL


LIVE_TABLES = {
    "Mining": ("mining", ORE_DATA),
    "Woodcutting": ("woodcutting", TREE_DATA),
    "Fishing": ("fishing", FISHING_DATA),
    "Hunter": ("hunter", HUNTER_DATA),
    "Cooking": ("cooking", COOKING_DATA),
    "Firemaking": ("firemaking", FIREMAKING_DATA),
}


def _source_ready_routes(skill_name):
    handler_key, table = LIVE_TABLES[skill_name]
    player_data = {
        "carried_keep_drop": {
            str(action_id): "drop"
            for action_id in table
        }
    }
    routes = []
    for action_id in table:
        route = resolve_live_cadence_route_pure(
            handler_key,
            str(action_id),
            player_data,
        )
        if route.mode in (RATE_LIMITED, EMBEDDED_PROBABILITY):
            routes.append(route)
    return routes


class LiveXpHourParityTest(unittest.TestCase):
    def test_rate_limited_routes_encode_the_exact_lower_source_endpoint(self):
        checked = {}
        for skill_name in LIVE_TABLES:
            rates = BY_SKILL[skill_name]
            for route in _source_ready_routes(skill_name):
                if route.mode != RATE_LIMITED:
                    continue
                rate = rates[route.source_row]
                profile = route.profile
                self.assertIsNotNone(profile)
                actual_xp_hour = (
                    Fraction(
                        profile.increment_numerator,
                        profile.threshold_denominator,
                    )
                    * R
                    * Fraction(str(rate.xp_per_action))
                )
                expected_xp_hour = rate.base_xp_hr()[0]
                self.assertAlmostEqual(
                    float(actual_xp_hour),
                    expected_xp_hour,
                    places=7,
                    msg=f"{skill_name}/{route.action_id}",
                )
                self.assertIn("lower_source_endpoint", route.source_reason)
                checked[skill_name] = checked.get(skill_name, 0) + 1

        self.assertEqual(
            checked,
            {
                "Mining": 2,
                "Woodcutting": 7,
                "Fishing": 2,
                "Hunter": 4,
                "Cooking": 2,
            },
        )

    def test_every_live_rational_emits_its_exact_count_per_denominator(self):
        for skill_name in LIVE_TABLES:
            for route in _source_ready_routes(skill_name):
                if route.mode != RATE_LIMITED:
                    continue
                profile = route.profile
                state = default_cadence_profile_state_pure(
                    opening_ready=False
                )
                emitted = 0
                for _ in range(profile.threshold_denominator):
                    step = advance_cadence_pure(profile, state)
                    state = step.state
                    emitted += int(step.emitted)
                self.assertEqual(
                    emitted,
                    profile.increment_numerator,
                    f"{skill_name}/{route.action_id}",
                )
                self.assertEqual(state["credit"], 0)

    def test_live_ordering_matches_each_source_ready_skill(self):
        for skill_name in ("Mining", "Woodcutting", "Fishing", "Hunter"):
            rates = BY_SKILL[skill_name]
            rows = []
            for route in _source_ready_routes(skill_name):
                if route.mode != RATE_LIMITED:
                    continue
                profile = route.profile
                effective = (
                    Fraction(
                        profile.increment_numerator,
                        profile.threshold_denominator,
                    )
                    * Fraction(str(rates[route.source_row].xp_per_action))
                )
                rows.append(
                    (
                        route.action_id,
                        float(effective),
                        rates[route.source_row].base_xp_hr()[0],
                    )
                )

            live_order = [
                action_id
                for action_id, _live, _source in sorted(
                    rows,
                    key=lambda row: (-row[1], row[0]),
                )
            ]
            source_order = [
                action_id
                for action_id, _live, _source in sorted(
                    rows,
                    key=lambda row: (-row[2], row[0]),
                )
            ]
            self.assertEqual(live_order, source_order, skill_name)

    def test_embedded_routes_attempt_once_without_a_second_residual_gate(self):
        expected = {
            "Cooking": {"cook_tuna", "cook_lobster", "cook_monkfish"},
            "Firemaking": {"magic_logs"},
        }
        for skill_name, expected_actions in expected.items():
            routes = {
                route.action_id: route
                for route in _source_ready_routes(skill_name)
                if route.mode == EMBEDDED_PROBABILITY
            }
            self.assertEqual(set(routes), expected_actions)
            for route in routes.values():
                player_data = {"cadence_profiles": {}}
                for _ in range(25):
                    resolved, admitted = advance_live_cadence_route_pure(
                        player_data,
                        route.handler_key,
                        route.action_id,
                    )
                    self.assertEqual(resolved.mode, EMBEDDED_PROBABILITY)
                    self.assertTrue(admitted)
                self.assertEqual(player_data["cadence_profiles"], {})


if __name__ == "__main__":
    unittest.main()
