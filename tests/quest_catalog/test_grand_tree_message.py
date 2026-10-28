"""Hazelmere's translation is a journal insertion with no gameplay effects."""

import copy
import json
import unittest
from dataclasses import fields
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest.catalog import _quest_from_catalog, _quest_with_stage_requirements
from ankiscape.data.quest.catalog_overrides import QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID
from ankiscape.data.quest.ledger import QUESTS_BY_ID
from ankiscape.data.quest.serializers import quests_as_dict
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure


QUEST_ID = "the_grand_tree"
MESSAGE = (
    "A man came to me with the King's seal",
    "I gave the man Daconia rocks",
    "and Daconia rocks will kill the tree!",
)
UNRELATED_PROOF = "Collect a bucket of sap from an evergreen tree"


def _saved_states():
    return ((0, False, False), (1, True, False), (2, True, False),
            (3, True, False), (QUESTS_BY_ID[QUEST_ID].stages, True, True))


def _player(progress, started, completed):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["quests"][QUEST_ID] = dict(
        progress=progress, started=started, completed=completed,
    )
    return player


def _reload(player):
    return migrate_loaded_data(json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS)


def _journal(player):
    return quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)


class GrandTreeMessageTest(unittest.TestCase):
    def _assert_message_stays_in_stage_two(self, rows):
        for row in rows:
            for statement in MESSAGE:
                self.assertEqual(row["lines"].count(statement), int(row["stage"] == 2))

    def test_source_message_is_only_stage_two_journal_delta(self):
        raw = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        untouched = copy.deepcopy(raw)
        quest = QUESTS_BY_ID[QUEST_ID]
        expected = {}
        for stage in raw["journal_stages"]:
            lines = tuple(stage["journal"])
            if stage["stage"] == 2:
                lines = lines[:1] + MESSAGE + lines[1:]
            expected[stage["stage"]] = lines

        self.assertEqual(len(quest.journal_stages), len(raw["journal_stages"]))
        self.assertEqual(tuple(s.stage for s in quest.journal_stages),
                         tuple(s["stage"] for s in raw["journal_stages"]))
        self.assertEqual({s.stage: s.journal for s in quest.journal_stages}, expected)
        self.assertEqual(quests_as_dict()[QUEST_ID]["journal_stages"], expected)
        self.assertEqual(QUEST_DATA[QUEST_ID]["journal_stages"], expected)
        original = next(s["journal"] for s in raw["journal_stages"] if s["stage"] == 2)
        self.assertEqual(expected[2][:5], (original[0], *MESSAGE, original[1]))
        self.assertEqual(original[0], "After using the translation book, it reads:")
        self.assertTrue(original[1].startswith("Return to King Narnode Shareen in the Grand Tree."))

        replacements = QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID
        with patch.dict(replacements):
            del replacements[QUEST_ID]
            without_message = _quest_with_stage_requirements(_quest_from_catalog(raw), raw)
        self.assertEqual(quest, _quest_with_stage_requirements(_quest_from_catalog(raw), raw))
        for field in fields(quest):
            if field.name != "journal_stages":
                with self.subTest(field=field.name):
                    self.assertEqual(getattr(quest, field.name), getattr(without_message, field.name))
        self.assertEqual({s.stage: s.journal for s in without_message.journal_stages},
                         {s["stage"]: tuple(s["journal"]) for s in raw["journal_stages"]})
        self.assertEqual(raw, untouched)

    def test_projection_is_pure_at_each_saved_progress(self):
        for progress, started, completed in _saved_states():
            with self.subTest(progress=progress, completed=completed):
                player = _player(progress, started, completed)
                before = copy.deepcopy(player)
                rows = _journal(player)
                self.assertEqual(_journal(player), rows)
                self.assertEqual(player, before)
                self.assertEqual(tuple(row["stage"] for row in rows),
                                 tuple(stage.stage for stage in QUESTS_BY_ID[QUEST_ID].journal_stages
                                       if stage.stage <= progress))
                self._assert_message_stays_in_stage_two(rows)
                if progress >= 2:
                    stage_two = next(row for row in rows if row["stage"] == 2)
                    self.assertEqual(stage_two["current"], progress == 2)
                    self.assertEqual(stage_two["completed"], progress > 2)

    def test_saved_reopen_preserves_progress_and_proofs(self):
        unrelated = QUEST_DATA["the_eyes_of_glouphrie"]["stage_requirements"]
        self.assertTrue(any(UNRELATED_PROOF in row["required_actions"] for row in unrelated))
        for progress, started, completed in _saved_states():
            with self.subTest(progress=progress, completed=completed):
                player = _player(progress, started, completed)
                player["inventory"] = {"Coins": 321, "Bucket": 1}
                player["quest_action_proofs"] = [UNRELATED_PROOF] if progress == 2 else []
                player = _reload(player)
                before = copy.deepcopy(player)
                rows = _journal(player)
                self.assertEqual(player, before)
                reopened = _reload(player)
                self.assertEqual(_journal(reopened), rows)
                # Full equality includes XP, claims, achievements, inventory,
                # all quests, proofs and the save version, not just this journal.
                self.assertEqual(reopened, before)
                self.assertEqual(reopened["quest_action_proofs"], before["quest_action_proofs"])
                if progress == 2:
                    self.assertEqual(reopened["quest_action_proofs"], [UNRELATED_PROOF])


if __name__ == "__main__":
    unittest.main()
