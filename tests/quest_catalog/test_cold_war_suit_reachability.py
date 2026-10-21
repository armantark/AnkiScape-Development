import unittest

from tests.reachability.live_report import live_reachability_report


class TestColdWarSuitReachability(unittest.TestCase):
    def test_suit_is_reachable_from_stage_two_without_finishing_cold_war(self):
        report = live_reachability_report()

        self.assertEqual(report["routes"].get("Clockwork suit"), "quest-stage:cold_war:2")
        self.assertIn(
            "Receive the Clockwork suit and test the penguin disguise with Larry",
            report["earned_quest_action_proofs"],
        )
        self.assertNotIn(
            "Build the clockwork penguin on a crafting table 3",
            report["earned_quest_action_proofs"],
        )
        self.assertFalse(any(
            "Clockwork suit" in row["products"]
            for row in report["blocked_quest_stage_products"]
        ))
