import unittest

from tools.audit_item_reachability import build_reachability_report


class TestItemReachabilityAudit(unittest.TestCase):
    def test_report_is_deterministic_and_accounts_for_live_action_inputs(self):
        report = build_reachability_report()
        self.assertEqual(report["schema_version"], 1)
        self.assertGreater(report["action_count"], 700)
        self.assertEqual(report["orphan_input_count"], len(report["orphan_inputs"]))
        self.assertEqual(
            report["orphan_input_count"],
            report["root_orphan_count"] + report["cascade_orphan_count"],
        )
        self.assertEqual(
            [row["item"] for row in report["orphan_inputs"]],
            sorted(row["item"] for row in report["orphan_inputs"]),
        )
        self.assertIn("Logs", report["routes"])
        self.assertIn("Bronze bar", report["routes"])
        self.assertIn("Crushed nest", report["routes"])
        self.assertNotIn("Bird's nest", {row["item"] for row in report["orphan_inputs"]})

        agility_four = next(
            row for row in report["orphan_inputs"]
            if row["item"] == "Agility potion (4)"
        )
        self.assertEqual(agility_four["kind"], "cascade")
        self.assertIn(
            "Shop service:bob_barter_decant_four:Agility potion",
            agility_four["known_producers"],
        )

        orphan_items = {row["item"] for row in report["orphan_inputs"]}
        for item_name in (
            "Candle lantern (empty)",
            "Candle lantern (unlit, 4529)",
            "Oil lamp (empty)",
            "Oil lamp (unlit)",
            "Oil lantern (empty)",
            "Oil lantern (unlit)",
            "Bullseye lantern (unf)",
            "Bullseye lantern (empty)",
            "Bullseye lantern (unlit)",
            "Sapphire lantern (empty)",
            "Sapphire lantern (unlit)",
            "Mining helmet (unlit)",
        ):
            self.assertNotIn(item_name, orphan_items)


if __name__ == "__main__":
    unittest.main()
