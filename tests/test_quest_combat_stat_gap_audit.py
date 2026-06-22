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

        self.assertEqual(len(self.gaps), 121)
        self.assertEqual(
            counts,
            {
                "darkan_hitpoints_only_metadata": 51,
                "darkan_missing_resolver_stats": 18,
                "darkan_same_name_wrong_level": 9,
                "no_local_source_match": 16,
                "parser_or_variant_level": 27,
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
            "darkan_missing_resolver_stats",
        )
        self.assertEqual(
            audit.classify_gap(self.by_quest_and_name[("land_of_the_goblins", "Snothead")], self.darkan_groups, self.partial_groups),
            "darkan_hitpoints_only_metadata",
        )
        self.assertNotIn(("another_slice_of_h_a_m", "H.A.M. mage"), self.by_quest_and_name)
        self.assertNotIn(("the_void_stares_back", "Torcher"), self.by_quest_and_name)
        self.assertNotIn(("the_void_stares_back", "Defiler"), self.by_quest_and_name)
        self.assertNotIn(("the_elder_kiln", "TokHaar-Xil"), self.by_quest_and_name)
        self.assertNotIn(("toktz_ket_dill", "Lava monster"), self.by_quest_and_name)
        self.assertNotIn(("nomads_requiem", "Nomad"), self.by_quest_and_name)
        self.assertEqual(
            audit.classify_gap(self.by_quest_and_name[("fight_arena", "Khazard scorpion")], self.darkan_groups, self.partial_groups),
            "darkan_missing_resolver_stats",
        )
        self.assertEqual(
            audit.classify_gap(self.by_quest_and_name[("another_slice_of_h_a_m", "H.A.M. ranger")], self.darkan_groups, self.partial_groups),
            "no_local_source_match",
        )
        self.assertNotIn(("witchs_house", "Witch's experiment"), self.by_quest_and_name)
        self.assertNotIn(("witchs_house", "Witch's experiment (Skavid form)"), self.by_quest_and_name)
        self.assertNotIn(("witchs_house", "Witch's experiment (Spider form)"), self.by_quest_and_name)
        self.assertNotIn(("witchs_house", "Witch's experiment (Bear form)"), self.by_quest_and_name)
        self.assertNotIn(("witchs_house", "Witch's experiment (Wolf form)"), self.by_quest_and_name)


if __name__ == "__main__":
    unittest.main()
