import os
import subprocess
import sys
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.firemaking_data import LIT_LIGHT_SOURCE_ITEMS, PERIOD_LIT_LIGHT_SOURCE_ITEMS
from ankiscape.logic_pure.logic_pure import quest_combat_encounter_has_stats_pure
from tools import build_pre_eoc_quest_catalog as builder


class TestPreEocQuestCatalogBuilder(unittest.TestCase):
    def test_mirrored_quest_sources_keep_canonical_provenance(self):
        game_mirror = "/tmp/disposable-game-main-mirror"
        darkan_mirror = "/tmp/disposable-darkan-mirror"
        environment = dict(
            os.environ,
            ANKISCAPE_GAME_MAIN=game_mirror,
            ANKISCAPE_DARKAN_WORLD_SERVER=darkan_mirror,
        )
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from tools import build_pre_eoc_quest_catalog as builder; "
                    "payload = f'{builder.SCAPE_2011_QUEST_IMPL_DIR}|{builder.DARKAN_NPC_LIST_PATH}'; "
                    "print(builder.GAME_MAIN_DIR); "
                    "print(builder._preserve_source_provenance(payload))"
                ),
            ],
            cwd=Path(__file__).resolve().parents[1],
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout.splitlines(),
            [
                game_mirror,
                (
                    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
                    "gg/rsmod/plugins/content/quests/impl|/Users/ArmanTarkhanian1/Documents/"
                    "2012scape with bots/darkan-world-server/developer-information/npcList.txt"
                ),
            ],
        )

    def test_light_source_options_match_the_runtime_exact_state_graph(self):
        self.assertEqual(builder.LIT_LIGHT_SOURCE_ITEMS, LIT_LIGHT_SOURCE_ITEMS)
        self.assertEqual(builder.PERIOD_LIT_LIGHT_SOURCE_ITEMS, PERIOD_LIT_LIGHT_SOURCE_ITEMS)

        rows = builder.build_stage_requirements(
            quest_id="example_quest",
            display_name="Example Quest",
            stages=1,
            journal_stages=(),
            journal_source="https://runescape.wiki/w/Example_Quest?oldid=1",
            item_requirements={"required_inventory": {"Light source": 1}},
            combat_encounters=(),
            source="https://runescape.wiki/w/Example_Quest?oldid=2",
        )

        self.assertEqual(rows[0]["required_inventory"], {})
        self.assertEqual(
            tuple(next(iter(option)) for option in rows[0]["required_inventory_options"][0]),
            LIT_LIGHT_SOURCE_ITEMS,
        )
        self.assertIn("oldid=6581760", rows[0]["source"])

    def test_source_blocked_stage_does_not_create_a_false_start_gate(self):
        rows = builder.build_stage_requirements(
            quest_id="watchtower",
            display_name="Watchtower",
            stages=5,
            journal_stages=(),
            journal_source="https://runescape.wiki/w/Watchtower?oldid=1",
            item_requirements={"required_inventory": {"Light source": 1}},
            combat_encounters=(),
            source="https://runescape.wiki/w/Watchtower?oldid=2",
        )

        self.assertFalse(any(row["required_inventory_options"] for row in rows))
        self.assertFalse(any("Light source" in row["required_inventory"] for row in rows))

    def test_combat_parser_handles_level_prefixed_names(self):
        encounters = builder.parse_combat_encounters("Lvl 2 Goblins", "source", "dwarf_cannon")

        self.assertEqual(encounters[0]["encounter_id"], "dwarf_cannon_goblins_2")
        self.assertEqual(encounters[0]["display_name"], "Goblins")
        self.assertEqual(encounters[0]["level"], 2)
        self.assertIn("goblin_level_2.plugin.kts", encounters[0]["npc_stats_source"])
        self.assertFalse(quest_combat_encounter_has_stats_pure(encounters[0]))

    def test_combat_parser_skips_source_list_headings(self):
        encounters = builder.parse_combat_encounters(
            "4 Guardians which are:\n*Dessous (level 139)",
            "source",
            "desert_treasure",
        )

        self.assertEqual([encounter["display_name"] for encounter in encounters], ["Dessous"])
        self.assertEqual(encounters[0]["level"], 139)

    def test_combat_parser_handles_prefix_quantity_and_leaves_ranges_unresolved(self):
        brawlers = builder.parse_combat_encounters(
            "4x Living rock brawler (level 2)",
            "source",
            "whats_mine_is_yours",
        )
        dwarves = builder.parse_combat_encounters(
            "3 dwarven gang members (levels 44-49)",
            "source",
            "one_small_favour",
        )

        self.assertEqual(brawlers[0]["quantity"], 4)
        self.assertEqual(brawlers[0]["level"], 2)
        self.assertEqual(dwarves[0]["quantity"], 3)
        self.assertEqual(dwarves[0]["level"], 0)

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
