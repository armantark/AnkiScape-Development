import unittest

from logic_pure import quest_combat_encounter_has_stats_pure
from tools import build_pre_eoc_quest_catalog as builder


class TestPreEocQuestCatalogBuilder(unittest.TestCase):
    def test_combat_parser_handles_level_prefixed_names(self):
        encounters = builder.parse_combat_encounters("Lvl 2 Goblins", "source", "dwarf_cannon")

        self.assertEqual(encounters[0]["encounter_id"], "dwarf_cannon_goblins_2")
        self.assertEqual(encounters[0]["display_name"], "Goblins")
        self.assertEqual(encounters[0]["level"], 2)
        self.assertIn("goblin_level_2.plugin.kts", encounters[0]["npc_stats_source"])
        self.assertFalse(quest_combat_encounter_has_stats_pure(encounters[0]))

    def test_npc_matching_uses_token_safe_aliases_and_plurals(self):
        self.assertEqual(builder._matching_source_npc_stats("Bear", 2), {})

        spider = builder._matching_source_npc_stats("Poisonous Spider", 31)
        self.assertEqual(spider["display_name"], "Poison Spider")
        self.assertEqual(spider["stats"]["attack"], 28)
        self.assertTrue(spider["source"].endswith("poison_spider_lvl_31.plugin.kts"))

        guardian = builder._matching_source_npc_stats("Guardians of Armadyl", 45)
        self.assertEqual(guardian["display_name"], "Guardian of Armadyl")
        self.assertEqual(guardian["stats"]["attack"], 37)
        self.assertTrue(guardian["source"].endswith("guardian_of_armadyl_(45).json"))


if __name__ == "__main__":
    unittest.main()
