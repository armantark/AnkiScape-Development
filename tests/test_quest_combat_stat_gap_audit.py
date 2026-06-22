import unittest
from collections import Counter

from tools import audit_quest_combat_stat_gaps as audit


class TestQuestCombatStatGapAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gaps = audit.statless_combat_gaps()
        cls.darkan_groups = audit.darkan_candidate_groups()
        cls.partial_groups = audit.darkan_partial_metadata_groups()
        cls.by_quest_and_name = {
            (gap.quest_id, gap.display_name): gap
            for gap in cls.gaps
        }

    def test_gap_classification_summary_matches_current_catalog_debt(self):
        counts = Counter(audit.classify_gap(gap, self.darkan_groups, self.partial_groups) for gap in self.gaps)

        self.assertEqual(len(self.gaps), 137)
        self.assertEqual(
            counts,
            {
                "darkan_partial_metadata_available": 80,
                "darkan_same_name_wrong_level": 11,
                "no_local_source_match": 18,
                "parser_or_variant_level": 28,
            },
        )

    def test_known_combat_gap_examples_explain_why_rows_remain_statless(self):
        self.assertNotIn(("priest_in_peril", "Monk of Zamorak"), self.by_quest_and_name)
        self.assertNotIn(("troll_stronghold", "Dad"), self.by_quest_and_name)
        self.assertEqual(
            audit.classify_gap(self.by_quest_and_name[("lost_city", "Tree spirit")], self.darkan_groups, self.partial_groups),
            "darkan_same_name_wrong_level",
        )
        self.assertEqual(
            audit.classify_gap(self.by_quest_and_name[("monkey_madness", "Jungle demon")], self.darkan_groups, self.partial_groups),
            "darkan_partial_metadata_available",
        )
        self.assertEqual(
            audit.classify_gap(self.by_quest_and_name[("witchs_house", "Witch's experiment")], self.darkan_groups, self.partial_groups),
            "parser_or_variant_level",
        )


if __name__ == "__main__":
    unittest.main()
