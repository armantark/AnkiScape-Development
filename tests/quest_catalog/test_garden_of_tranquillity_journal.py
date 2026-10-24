import copy
from dataclasses import replace
from itertools import product
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest.catalog import _quest_from_catalog, _quest_with_stage_requirements
from ankiscape.data.quest.catalog_overrides import QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID
from ankiscape.data.quest.ledger import QUESTS_BY_ID
from ankiscape.data.quest.serializers import quests_as_dict
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import (
    quest_current_stage_blockers_pure,
    quest_journal_rows_pure,
)


QUEST_ID = "garden_of_tranquillity"
EXPECTED_ANSWERS = (
    "Show them a range of colours so that they can come to a compromise.",
    "Take his generous gift even though you have no need for it.",
    "It's absolutely, unquestionably the most interesting thing I've ever done!",
    "Put on the silly helmet and jump into the cannon.",
    "You of course (Player Name), no one could ever challenge your greatness!",
    "Ask me nicely and I might consider it.",
    "No, especially not that wise old man, who doesn't look at all suspicious.",
)


class TestGardenOfTranquillityJournal(unittest.TestCase):
    def test_composed_journal_matches_source(self):
        raw = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        originals = {stage["stage"]: tuple(stage["journal"]) for stage in raw["journal_stages"]}
        self.assertEqual(len(originals[1]), 6)
        self.assertEqual(originals[1][4], "The answers to the questions are as follows:")
        expected = dict(originals)
        expected[1] = originals[1][:5] + EXPECTED_ANSWERS + originals[1][5:]
        catalog_before = copy.deepcopy(PRE_EOC_QUEST_CATALOG)
        live = QUESTS_BY_ID[QUEST_ID]
        journals = {stage.stage: stage.journal for stage in live.journal_stages}
        for _ in range(3):
            for actual in (journals, quests_as_dict()[QUEST_ID]["journal_stages"],
                           QUEST_DATA[QUEST_ID]["journal_stages"]):
                self.assertEqual(actual, expected)
                self.assertEqual(tuple(actual), tuple(range(1, 10)))
                self.assertEqual(len(actual), 9)
                self.assertEqual(len(actual[1]), 13)
                self.assertEqual(actual[1][:5], originals[1][:5])
                self.assertEqual(actual[1][5:12], EXPECTED_ANSWERS)
                self.assertEqual(actual[1][12], originals[1][5])
                for answer in EXPECTED_ANSWERS:
                    self.assertEqual(actual[1].count(answer), 1)
                for stage in range(2, 10):
                    self.assertEqual(actual[stage], originals[stage])
        self.assertEqual(PRE_EOC_QUEST_CATALOG, catalog_before)

    def test_composition_changes_only_journal(self):
        raw = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        live = QUESTS_BY_ID[QUEST_ID]
        with patch.dict(QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID):
            del QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID[QUEST_ID]
            baseline = _quest_with_stage_requirements(_quest_from_catalog(raw), raw)
            self.assertNotEqual(live.journal_stages, baseline.journal_stages)
            self.assertEqual(live, replace(baseline, journal_stages=live.journal_stages))
        self.assertEqual(QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID[QUEST_ID], live.journal_stages)

    def test_journal_projection_preserves_player_state(self):
        states = ((False, 0, False), (True, 0, False), (True, 1, False),
                  (True, 2, False), (True, 9, True))
        # inventory is the Bank. Include a banked spare with either custody.
        custody = ((2, {}), (1, {"ring": "Ring of Charos"}))
        for (started, progress, completed), (banked, equipment) in product(states, custody):
            with self.subTest(started=started, progress=progress, completed=completed,
                              equipment=equipment):
                # Disposable projection fixtures, not acquisition or prerequisite proofs.
                player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                player["quests"][QUEST_ID] = {
                    "started": started, "progress": progress, "completed": completed,
                }
                player["inventory"]["Ring of Charos"] = banked
                player["equipment"] = dict(equipment)
                player["quest_points"] = 7
                player["farming_exp"] = 1234
                player["pending_skill_exp_rewards"] = {"farming": 23}
                player_before = copy.deepcopy(player)
                quest_data_before = copy.deepcopy(QUEST_DATA)
                blockers_before = copy.deepcopy(
                    quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA)
                )
                visible = max(progress, int(started))
                expected_rows = tuple({
                    "stage": stage,
                    "lines": QUEST_DATA[QUEST_ID]["journal_stages"][stage],
                    "completed": completed or stage < visible,
                    "current": not completed and stage == visible,
                } for stage in range(1, visible + 1))
                for _ in range(3):
                    rows = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
                    self.assertEqual(rows, expected_rows)
                    for row in rows:
                        if row["stage"] == 1:
                            self.assertEqual(row["lines"][5:12], EXPECTED_ANSWERS)
                    self.assertEqual(
                        quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA),
                        blockers_before,
                    )
                    self.assertEqual(player, player_before)
                    self.assertEqual(QUEST_DATA, quest_data_before)


if __name__ == "__main__":
    unittest.main()
