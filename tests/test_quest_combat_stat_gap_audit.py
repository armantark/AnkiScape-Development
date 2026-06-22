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

        self.assertEqual(len(self.gaps), 103)
        self.assertEqual(
            counts,
            {
                "darkan_hitpoints_only_metadata": 51,
                "darkan_missing_resolver_stats": 18,
                "darkan_same_name_wrong_level": 7,
                "no_local_source_match": 10,
                "parser_or_variant_level": 17,
            },
        )

    def test_known_combat_gap_examples_explain_why_rows_remain_statless(self):
        self.assertNotIn(("priest_in_peril", "Monk of Zamorak"), self.by_quest_and_name)
        self.assertEqual(
            audit.classify_gap(
                self.by_quest_and_name[("priest_in_peril", "Temple guardian dog")],
                self.darkan_groups,
                self.partial_groups,
            ),
            "no_local_source_match",
        )
        self.assertNotIn(("troll_stronghold", "Dad"), self.by_quest_and_name)
        self.assertNotIn(("lost_city", "Tree spirit"), self.by_quest_and_name)
        self.assertNotIn(("observatory_quest", "Poisonous Spider"), self.by_quest_and_name)
        self.assertNotIn(("temple_of_ikov", "Guardians of Armadyl"), self.by_quest_and_name)
        self.assertNotIn(("dwarf_cannon", "Goblins"), self.by_quest_and_name)
        self.assertEqual(
            audit.classify_gap(self.by_quest_and_name[("wanted", "Black Knight")], self.darkan_groups, self.partial_groups),
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
        self.assertNotIn(("heroes_quest", "Entrana Fire Bird"), self.by_quest_and_name)
        self.assertNotIn(("spirits_of_the_elid", "Golem"), self.by_quest_and_name)
        self.assertNotIn(("another_slice_of_h_a_m", "H.A.M. ranger"), self.by_quest_and_name)
        self.assertNotIn(("witchs_house", "Witch's experiment"), self.by_quest_and_name)
        self.assertNotIn(("witchs_house", "Witch's experiment (Skavid form)"), self.by_quest_and_name)
        self.assertNotIn(("witchs_house", "Witch's experiment (Spider form)"), self.by_quest_and_name)
        self.assertNotIn(("witchs_house", "Witch's experiment (Bear form)"), self.by_quest_and_name)
        self.assertNotIn(("witchs_house", "Witch's experiment (Wolf form)"), self.by_quest_and_name)
        self.assertNotIn(("a_souls_bane", "Angry unicorn"), self.by_quest_and_name)
        self.assertNotIn(("a_souls_bane", "Angry bear"), self.by_quest_and_name)
        self.assertNotIn(("a_souls_bane", "Angry giant rat"), self.by_quest_and_name)
        self.assertNotIn(("a_souls_bane", "Angry goblin"), self.by_quest_and_name)
        self.assertNotIn(("a_souls_bane", "Fear reaper"), self.by_quest_and_name)
        self.assertNotIn(("a_souls_bane", "Confusion beast"), self.by_quest_and_name)
        self.assertNotIn(("a_souls_bane", "Hopeless creature"), self.by_quest_and_name)
        self.assertNotIn(("a_souls_bane", "Tolna head"), self.by_quest_and_name)
        self.assertNotIn(("death_to_the_dorgeshuun", "Senior guard x3"), self.by_quest_and_name)
        self.assertNotIn(("death_to_the_dorgeshuun", "Senior H.A.M. guard"), self.by_quest_and_name)
        self.assertNotIn(("shilo_village", "Nazastarool (Zombie)"), self.by_quest_and_name)
        self.assertNotIn(("shilo_village", "Nazastarool (Skeleton)"), self.by_quest_and_name)
        self.assertNotIn(("shilo_village", "Nazastarool (Ghost)"), self.by_quest_and_name)
        self.assertNotIn(("legends_quest", "Nezikchened"), self.by_quest_and_name)
        self.assertNotIn(("the_feud", "Tough guy"), self.by_quest_and_name)
        self.assertNotIn(("recipe_for_disaster_freeing_sir_amik_varze", "Black Dragon"), self.by_quest_and_name)


if __name__ == "__main__":
    unittest.main()
