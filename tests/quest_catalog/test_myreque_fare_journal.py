"""Cyreg's journal prose changes without altering quest mechanics or viewing state."""

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


QUEST_ID = "in_search_of_the_myreque"


class TestMyrequeFareJournal(unittest.TestCase):
    def test_composed_journal_changes_only_two_passages(self):
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        expected = {row["stage"]: list(row["journal"]) for row in generated["journal_stages"]}
        self.assertEqual(expected[1][11], "Respond to Cyreg with the following:")
        self.assertEqual(expected[2][2], "Give him three Planks and then ten Coins.")
        expected[1][11] = (
            "Persuade Cyreg with four responses in order; the last two continue in the next journal stage:"
        )
        expected[2][2] = (
            "After all four responses, give Cyreg three ordinary planks and keep three more for the bridge. "
            "He will give you directions. To board, carry a blessed silver sickle and a Druid pouch with "
            "at least five current charges. The ten-coin fare applies after quest completion."
        )
        expected = {stage: tuple(lines) for stage, lines in expected.items()}
        serialized = quests_as_dict()[QUEST_ID]
        self.assertEqual(serialized["journal_stages"], expected)
        self.assertEqual(QUEST_DATA[QUEST_ID]["journal_stages"], expected)
        self.assertEqual(tuple(expected), (1, 2, 3))
        self.assertEqual(tuple(map(len, expected.values())), (14, 13, 14))
        self.assertEqual(serialized["stages"], 4)
        self.assertEqual(QUEST_DATA[QUEST_ID]["stages"], 4)
        self.assertEqual(generated["journal_stages"][0]["journal"][11], "Respond to Cyreg with the following:")
        self.assertEqual(generated["journal_stages"][1]["journal"][2], "Give him three Planks and then ten Coins.")

    def test_preparation_and_response_order(self):
        journal = QUEST_DATA[QUEST_ID]["journal_stages"]
        lines = tuple(line for row in journal.values() for line in row)
        responses = (
            "Well, I guess they'll just die without weapons...",
            "Resourceful enough to get their own steel weapons?",
            "If you don't tell me, their deaths are on your head!",
            "What kind of man are you to say that you don't care?",
        )
        self.assertEqual(journal[1][-2:], responses[:2])
        self.assertEqual(journal[2][:2], responses[2:])
        self.assertEqual(tuple(lines.count(response) for response in responses), (1, 1, 1, 1))
        self.assertEqual(journal[2][2], (
            "After all four responses, give Cyreg three ordinary planks and keep three more for the bridge. "
            "He will give you directions. To board, carry a blessed silver sickle and a Druid pouch with "
            "at least five current charges. The ten-coin fare applies after quest completion."
        ))
        self.assertEqual(journal[2][3], "Use the boat to get to the Hallows.")
        self.assertEqual(journal[2][5], "Repair the bridge with the 75 Steel nails, three planks, and a Hammer.")
        self.assertNotIn("Respond to Cyreg with the following:", lines)
        self.assertNotIn("Give him three Planks and then ten Coins.", lines)
        fare_sentences = tuple(
            sentence.strip() for line in lines for sentence in line.split(".")
            if "coin" in sentence.casefold()
        )
        self.assertEqual(fare_sentences, ("The ten-coin fare applies after quest completion",))

    def test_nonjournal_quest_definition_unchanged(self):
        actual = QUESTS_BY_ID[QUEST_ID]
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        other_overrides = {
            quest_id: rows for quest_id, rows in QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID.items()
            if quest_id != QUEST_ID
        }
        with patch.dict(QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID, other_overrides, clear=True):
            baseline = _quest_with_stage_requirements(_quest_from_catalog(generated), generated)
        self.assertEqual(replace(actual, journal_stages=baseline.journal_stages), baseline)
        self.assertEqual(QUEST_DATA[QUEST_ID], quests_as_dict()[QUEST_ID])

    def test_projection_is_read_only_at_existing_boundaries(self):
        # Metadata is (row number, completed, current), independent of possessions.
        states = (
            (False, 0, False, ()),
            (True, 0, False, ((1, False, True),)),
            (True, 1, False, ((1, False, True),)),
            (True, 2, False, ((1, True, False), (2, False, True))),
            (True, 3, False, ((1, True, False), (2, True, False), (3, False, True))),
            (True, 4, True, ((1, True, False), (2, True, False), (3, True, False))),
        )
        for started, progress, completed, metadata in states:
            for charges in (None, 0, 4, 5):
                with self.subTest(started=started, progress=progress, completed=completed, charges=charges):
                    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                    player["current_quest"] = QUEST_ID
                    player["quests"][QUEST_ID] = dict(started=started, progress=progress, completed=completed)
                    player["inventory"] = {
                        "Coins": 50, "Plank": 6, "Steel nails": 75, "Hammer": 1,
                        "Silver sickle (b)": 1, "Druid pouch": 1,
                    }
                    player["quest_action_proofs"] = []
                    if charges is None:
                        del player["inventory"]["Silver sickle (b)"]
                        del player["inventory"]["Druid pouch"]
                        player["temple_trekking"].pop("pouch_charges", None)
                    else:
                        player["temple_trekking"]["pouch_charges"] = charges
                    before_player = copy.deepcopy(player)
                    before_catalog = copy.deepcopy(QUEST_DATA)
                    expected = tuple(
                        dict(stage=stage, completed=done, current=current,
                             lines=before_catalog[QUEST_ID]["journal_stages"][stage])
                        for stage, done, current in metadata
                    )
                    for _ in range(2):
                        self.assertEqual(quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA), expected)
                        self.assertEqual(player, before_player)
                        self.assertEqual(QUEST_DATA, before_catalog)
