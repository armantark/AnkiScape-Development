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

    def test_quick_guide_parser_refuses_current_only_revisions(self):
        original_fetch = builder.fetch_wikitext

        def fake_fetch(title, before_cutoff=True):
            return builder.Revision(
                title=title,
                oldid=123,
                timestamp="2026-01-01T00:00:00Z",
                content="* Talk to someone.",
                fallback_current=True,
            )

        try:
            builder.fetch_wikitext = fake_fetch
            lines, source = builder.parse_quick_guide_lines("Example Quest", "Example Quest")
        finally:
            builder.fetch_wikitext = original_fetch

        self.assertEqual(lines, ())
        self.assertEqual(source, "")

    def test_stage_requirements_include_compact_source_checkpoint_actions(self):
        rows = builder.build_stage_requirements(
            quest_id="example_quest",
            display_name="Example Quest",
            stages=2,
            journal_stages=(
                {
                    "stage": 1,
                    "journal": ("Talk to the first NPC.", "Carry the example item across the map."),
                    "source_kind": "walkthrough_prose",
                },
                {"stage": 2, "journal": ("Quest complete!",), "source_kind": "walkthrough_prose"},
            ),
            journal_source="https://runescape.wiki/w/Example_Quest?oldid=1",
            item_requirements={"required_inventory": {"Example item": 1}},
            combat_encounters=(),
            source="https://runescape.wiki/w/Example_Quest?oldid=2",
        )

        self.assertEqual(rows[0]["stage"], 1)
        self.assertEqual(rows[0]["required_actions"], ("Complete Example Quest stage 1 objective",))
        self.assertLess(len(rows[0]["required_actions"][0]), 64)
        self.assertEqual(rows[0]["required_inventory"], {"Example item": 1})
        self.assertIn("oldid=1", rows[0]["source"])
        self.assertIn("oldid=2", rows[0]["source"])


if __name__ == "__main__":
    unittest.main()
