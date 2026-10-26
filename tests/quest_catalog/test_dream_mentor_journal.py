"""Dream Mentor's two opening instructions preserve all existing quest behavior."""

import copy
import unittest
from dataclasses import replace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest.catalog import _quest_from_catalog, _quest_with_stage_requirements
from ankiscape.data.quest.catalog_overrides import QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID
from ankiscape.data.quest.ledger import QUESTS_BY_ID
from ankiscape.data.quest.serializers import quests_as_dict
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure


QUEST_ID = "dream_mentor"


def _generated_quest():
    return next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)


def _expected_journal():
    expected = {row["stage"]: list(row["journal"]) for row in _generated_quest()["journal_stages"]}
    expected[1].insert(6, "After four pieces of food, he opens his eyes. Speak with him.")
    expected[1].insert(
        8,
        "After you raise his Spirit status up, his appetite returns, so feed him four more pieces of food.",
    )
    return {stage: tuple(lines) for stage, lines in expected.items()}


def _projection_cases():
    # Metadata explicitly follows existing state boundaries: stage, completed, current.
    return (
        (None, ()),
        (dict(started=False, progress=0, completed=False), ()),
        (dict(started=True, progress=0, completed=False), ((1, False, True),)),
        (dict(started=True, progress=1, completed=False), ((1, False, True),)),
        (dict(started=True, progress=2, completed=False), ((1, True, False), (2, False, True))),
        (dict(started=True, progress=3, completed=False),
         ((1, True, False), (2, True, False), (3, False, True))),
        (dict(started=True, progress=4, completed=False),
         ((1, True, False), (2, True, False), (3, True, False), (4, False, True))),
        (dict(started=True, progress=5, completed=False),
         ((1, True, False), (2, True, False), (3, True, False), (4, True, False), (5, False, True))),
        (dict(started=True, progress=5, completed=True),
         ((1, True, False), (2, True, False), (3, True, False), (4, True, False), (5, True, False))),
    )


class TestDreamMentorJournal(unittest.TestCase):
    def test_composed_journal_inserts_only_two_paragraphs(self):
        original = {row["stage"]: tuple(row["journal"]) for row in _generated_quest()["journal_stages"]}
        expected = _expected_journal()
        self.assertEqual(len(original[1]), 9)
        self.assertEqual(tuple(expected), (1, 2, 3, 4, 5))
        self.assertEqual(tuple(map(len, expected.values())), (11, 8, 8, 8, 9))
        authored = QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID[QUEST_ID]
        composed = QUESTS_BY_ID[QUEST_ID]
        serialized = quests_as_dict()[QUEST_ID]
        for journal in (
            {row.stage: row.journal for row in authored},
            {row.stage: row.journal for row in composed.journal_stages},
            serialized["journal_stages"],
            QUEST_DATA[QUEST_ID]["journal_stages"],
        ):
            self.assertEqual(journal, expected)
            self.assertEqual(tuple(journal), (1, 2, 3, 4, 5))
            self.assertEqual(tuple(map(len, journal.values())), (11, 8, 8, 8, 9))
        self.assertEqual(len(composed.journal_stages), 5)
        # Existing stage requirements compose six gameplay stages from five
        # journal rows. This prose repair must preserve that baseline count.
        self.assertEqual(composed.stages, 6)
        self.assertEqual(serialized["stages"], 6)
        self.assertEqual(QUEST_DATA[QUEST_ID]["stages"], 6)
        opening = serialized["journal_stages"][1]
        self.assertEqual(tuple(line for i, line in enumerate(opening) if i not in (6, 8)), original[1])
        for stage in (2, 3, 4, 5):
            self.assertEqual(serialized["journal_stages"][stage], original[stage])
        self.assertEqual(opening[-2:], original[1][-2:])
        self.assertIn("stand up and speak coherently", opening[-2])
        self.assertIn("Feed him six more pieces of food", opening[-2])
        self.assertIn("Cyrisus's bank account", opening[-1])
        self.assertIn("a chest to carry the armour", opening[-1])
        self.assertIn("Select a helmet, top, legs, boots, and weapon.", opening[-1])
        self.assertEqual(tuple(opening.count(line) for line in original[1][-2:]), (1, 1))

    def test_nonjournal_definition_unchanged(self):
        generated = _generated_quest()
        other_overrides = dict(QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID)
        del other_overrides[QUEST_ID]
        with patch.dict(QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID, other_overrides, clear=True):
            baseline = _quest_with_stage_requirements(_quest_from_catalog(generated), generated)
        actual = QUESTS_BY_ID[QUEST_ID]
        self.assertEqual(replace(actual, journal_stages=baseline.journal_stages), baseline)
        self.assertEqual(QUEST_DATA[QUEST_ID], quests_as_dict()[QUEST_ID])

    def test_projection_order_and_view_purity(self):
        expected = _expected_journal()
        for state, metadata in _projection_cases():
            for salmon in (False, True):
                with self.subTest(state=state, salmon=salmon):
                    self._assert_projection_case(state, metadata, salmon, expected)

    def _assert_projection_case(self, state, metadata, salmon, journal):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["current_quest"] = QUEST_ID
        player["quests"].pop(QUEST_ID, None)
        if state is not None:
            player["quests"][QUEST_ID] = dict(state)
        if salmon:
            player["inventory"]["Salmon"] = 20
        before_player = copy.deepcopy(player)
        before_catalog = copy.deepcopy(QUEST_DATA)
        expected = tuple(
            dict(stage=stage, completed=done, current=current, lines=journal[stage])
            for stage, done, current in metadata
        )
        for _ in range(2):
            self.assertEqual(quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA), expected)
            self.assertEqual(player, before_player)
            self.assertEqual(QUEST_DATA, before_catalog)
