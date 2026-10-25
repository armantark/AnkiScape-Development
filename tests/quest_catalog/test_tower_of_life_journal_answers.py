import copy
import unittest
from dataclasses import replace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest import catalog, catalog_overrides
from ankiscape.data.quest_data import QUESTS_BY_ID, quests_as_dict
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure


QUEST_ID = "tower_of_life"
RAW_TOWER = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
STATES = (
    ("unstarted", False, 0, False),
    ("Black-eye", True, 1, False),
    ("Bonafido", True, 2, False),
    ("completed", True, 6, True),
)


def _expected_journal(black_eye, bonafido):
    expected = {stage["stage"]: stage["journal"] for stage in RAW_TOWER["journal_stages"]}
    expected[1] = expected[1][:11] + black_eye + expected[1][11:]
    expected[2] = expected[2][:6] + bonafido + expected[2][6:]
    return expected


def _player(started, progress, completed):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["quests"][QUEST_ID] = {
        "started": started, "progress": progress, "completed": completed,
    }
    return player


class TestTowerOfLifeJournalAnswers(unittest.TestCase):
    def test_composed_blocks_restore_exact_source_associations(self):
        black_eye = (
            "How many nails does it take to make a rocking chair? — 3 nails",
            "What takes 3 planks, 3 cloth and 3 nails to make, and help remove light from a room? — Torn curtains",
            "I like fish and I want to put some in my garden, but I need a special water feature. "
            "What materials would I require? — 10 clay pieces",
        )
        bonafido = (
            "You've plenty of work to do, but you need a drink fast - what do you go for? — Tea",
            "Now, let's hear you whistle! — Whistle for attention",
            "What's a good sign that you need to repair your trousers? — Your legs are getting a bit cold",
            "What do you do if you cut your finger? — Carry on, it'll fix itself.",
        )
        expected = _expected_journal(black_eye, bonafido)
        self.assertEqual(expected[1][10], "He will ask three questions. The answer are as follows:")
        self.assertEqual(expected[1][14], "Talk to 'Gummy'.")
        self.assertEqual(expected[2][5], "He will give a test of which the answers are as follows:")
        self.assertEqual(
            expected[2][10],
            "On the ground floor of the tower, take four Coloured balls, three Metal sheets, "
            "and four Valve wheels from the crates.",
        )
        self.assertEqual(
            {stage.stage: stage.journal for stage in QUESTS_BY_ID[QUEST_ID].journal_stages},
            expected,
        )
        self.assertEqual(quests_as_dict()[QUEST_ID]["journal_stages"], expected)
        self.assertEqual(QUEST_DATA[QUEST_ID]["journal_stages"], expected)
        self.assertEqual(tuple(map(len, expected.values())), (16, 17, 13, 13, 14))
        raw_snapshot = copy.deepcopy(RAW_TOWER)
        stages = catalog_overrides._tower_of_life_journal_stages()
        self.assertEqual({stage.stage: stage.journal for stage in stages}, expected)
        self.assertEqual(RAW_TOWER, raw_snapshot)

    def test_nonjournal_definition_and_completion_sentinel_are_unchanged(self):
        replacements = catalog_overrides.QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID
        without_tower = {key: value for key, value in replacements.items() if key != QUEST_ID}
        with patch.dict(replacements, without_tower, clear=True):
            baseline = catalog._quest_with_stage_requirements(
                catalog._quest_from_catalog(RAW_TOWER), RAW_TOWER,
            )
        repaired = catalog._quest_with_stage_requirements(
            catalog._quest_from_catalog(RAW_TOWER), RAW_TOWER,
        )
        self.assertEqual(replace(repaired, journal_stages=baseline.journal_stages), baseline)
        self.assertEqual(repaired, QUESTS_BY_ID[QUEST_ID])
        self.assertEqual(repaired.stages, 6)
        self.assertEqual(QUEST_DATA[QUEST_ID]["stages"], 6)
        self.assertEqual(tuple(stage.stage for stage in repaired.journal_stages), (1, 2, 3, 4, 5))

    def test_journal_projection_preserves_visibility_and_completion_flags(self):
        expected = _expected_journal(
            (
                "How many nails does it take to make a rocking chair? — 3 nails",
                "What takes 3 planks, 3 cloth and 3 nails to make, and help remove light from a room? — Torn curtains",
                "I like fish and I want to put some in my garden, but I need a special water feature. "
                "What materials would I require? — 10 clay pieces",
            ),
            (
                "You've plenty of work to do, but you need a drink fast - what do you go for? — Tea",
                "Now, let's hear you whistle! — Whistle for attention",
                "What's a good sign that you need to repair your trousers? — Your legs are getting a bit cold",
                "What do you do if you cut your finger? — Carry on, it'll fix itself.",
            ),
        )
        expected_rows = (
            (),
            ({"stage": 1, "lines": expected[1], "completed": False, "current": True},),
            (
                {"stage": 1, "lines": expected[1], "completed": True, "current": False},
                {"stage": 2, "lines": expected[2], "completed": False, "current": True},
            ),
            tuple(
                {"stage": stage, "lines": expected[stage], "completed": True, "current": False}
                for stage in (1, 2, 3, 4, 5)
            ),
        )
        for (name, started, progress, completed), rows in zip(STATES, expected_rows):
            with self.subTest(state=name):
                player = _player(started, progress, completed)
                self.assertEqual(quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA), rows)

    def test_repeated_projection_does_not_mutate_player_or_catalog(self):
        for name, started, progress, completed in STATES:
            with self.subTest(state=name):
                player = _player(started, progress, completed)
                player_snapshot = copy.deepcopy(player)
                catalog_snapshot = copy.deepcopy(QUEST_DATA[QUEST_ID])
                first = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
                second = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
                self.assertEqual(first, second)
                self.assertEqual(player, player_snapshot)
                self.assertEqual(QUEST_DATA[QUEST_ID], catalog_snapshot)
