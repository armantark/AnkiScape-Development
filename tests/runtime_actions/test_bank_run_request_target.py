"""A queued bank run names one target: the HUD and the runtime agree on it."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic.review_strip_logic import review_bank_run_travel_view_pure
from ankiscape.runtime.runtime_actions_carried_overlay import (
    run_answer_with_carried_overlay,
)
from tests.test_runtime_actions import _context


class TestBankRunRequestTarget(unittest.TestCase):
    """Owner incident 2026-09-17: a Grand Exchange fill queued a trip for
    mackerel, the owner switched to tuna, and the HUD showed "Bank run queued"
    on every tuna review while the runtime never spent the trip."""

    def _review(self, player_data, calls):
        ctx = _context(player_data, calls)
        gathered = []
        self.assertTrue(
            run_answer_with_carried_overlay(
                ctx, "mining", lambda _ctx: gathered.append(True) or True
            )
        )
        return bool(gathered)

    def test_request_waits_for_its_own_target(self):
        player_data = {
            "inventory": {},
            "current_ore": "iron_ore",
            "skilling_bank_run_requested": "copper_ore",
        }
        calls = {"xp": [], "saves": 0, "errors": [], "activity": []}

        self.assertEqual(
            review_bank_run_travel_view_pure(player_data, "mining"),
            {"active": False, "queued": False},
        )
        self.assertTrue(self._review(player_data, calls))
        self.assertEqual(player_data["skilling_bank_run_requested"], "copper_ore")
        self.assertEqual(calls["activity"], [])

        player_data["current_ore"] = "copper_ore"
        self.assertTrue(review_bank_run_travel_view_pure(player_data, "mining")["queued"])
        self._review(player_data, calls)
        self.assertNotIn("skilling_bank_run_requested", player_data)
        self.assertEqual(
            review_bank_run_travel_view_pure(player_data, "mining"),
            {"active": False, "queued": False},
        )


if __name__ == "__main__":
    unittest.main()
