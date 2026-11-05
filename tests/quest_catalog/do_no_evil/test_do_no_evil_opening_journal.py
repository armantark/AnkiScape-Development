"""Sourced opening instructions use the existing, read-only journal projection."""

import copy
from dataclasses import replace
from itertools import product
import json
from pathlib import Path
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
from tests import test_storage_runtime as _storage_harness


QUEST_ID = "do_no_evil"
SOURCE_MAP = Path(__file__).resolve().parents[1] / "fixtures" / "do_no_evil_opening_journal_sources.json"
EXPECTED_OPENING = (
    "Before starting, Senliten must be restored to 100%.",
    "Speak to Leela in Draynor Village and accompany her to Senliten's tomb at Uzer Mastaba.",
    "Speak to Senliten and Leela. Ask the queen how you can help, and listen to her story about the desert monkeys.",
    "Travel to Sophanem to investigate Apmeken with Jex and the Sphinx. You may visit them in either order.",
    "Ask Jex at the wrecked temple about minor gods, then ask him all the questions about Apmeken.",
    "Have a cat or kitten out when speaking to the Sphinx. Ask her about minor gods, then Apmeken.",
    "After speaking to both, return to Senliten to hear her request to return the monkeys to their rightful place in the desert.",
)


def _raw_quest():
    return next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)


def _original_journals():
    return {row["stage"]: tuple(row["journal"]) for row in _raw_quest()["journal_stages"]}


def _player(started=True, progress=1, completed=False, inventory="default"):
    # Select display states only; no prerequisite, acquisition or deed acceptance.
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["quests"][QUEST_ID] = {
        "started": started, "progress": progress, "completed": completed,
    }
    player["quest_action_proofs"] = []
    if inventory != "default":
        player["inventory"]["Banana"] = 1
    if inventory == "carried":
        player["carried_inventory"]["Banana"] = 1
    return player


def _expected_rows(started, progress, completed):
    visible = max(progress, int(started))
    journals = _original_journals()
    journals[1] = EXPECTED_OPENING
    return tuple({
        "stage": stage,
        "lines": journals[stage],
        "completed": completed or stage < visible,
        "current": not completed and stage == visible,
    } for stage in range(1, min(visible, 9) + 1))


def _storage():
    collection = _storage_harness._LegacyTextCollection()
    collection.legacy_row = False
    collection.values = {}
    return collection, _storage_harness._load_storage_module(collection)


class TestDoNoEvilOpeningJournal(unittest.TestCase):
    def _assert_source_map(self):
        source_map = json.loads(SOURCE_MAP.read_text())
        self.assertEqual(tuple(source_map["journal"]), EXPECTED_OPENING)
        self.assertEqual([row["display_line"] for row in source_map["mapping"]], list(range(1, 8)))
        self.assertEqual(tuple(row["text"] for row in source_map["mapping"]), EXPECTED_OPENING)
        supplying_lines = ([31], [32, 70], [70], [70, 76], [76], [74, 76], [78])
        for row, lines in zip(source_map["mapping"], supplying_lines):
            primary = row["sources"][0]
            self.assertEqual(primary["source_id"], "W")
            self.assertEqual(primary["revision_or_actual_capture"], "6587790")
            self.assertEqual(primary["timestamp_utc"], "2012-11-19T14:55:38Z")
            self.assertEqual(primary["body_sha256"],
                             "d732e9701228c76068f6df58c8296c5ab1ea81e5394330b5a68e29a1e75c85bf")
            self.assertEqual([line["line"] for line in primary["literal_lines"]], lines)

    def test_composed_journal_matches_mapped_opening(self):
        self._assert_source_map()
        catalog_before = copy.deepcopy(PRE_EOC_QUEST_CATALOG)
        raw = _raw_quest()
        original = _original_journals()
        recomposed = _quest_with_stage_requirements(_quest_from_catalog(raw), raw)
        self.assertEqual(recomposed, QUESTS_BY_ID[QUEST_ID])
        serialized = quests_as_dict()[QUEST_ID]
        journals = {row.stage: row.journal for row in recomposed.journal_stages}
        expected = {**original, 1: EXPECTED_OPENING}
        for actual in (journals, serialized["journal_stages"], QUEST_DATA[QUEST_ID]["journal_stages"]):
            self.assertEqual(actual, expected)
            self.assertEqual(tuple(actual), tuple(range(1, 10)))
            self.assertTrue(all(heading not in actual[1] for heading in original[1]))
            self.assertEqual({stage: actual[stage] for stage in range(2, 10)},
                             {stage: original[stage] for stage in range(2, 10)})
        self.assertEqual(len(original[2]), 7)  # Keep the entire commission through guard-lure return.
        self.assertEqual(recomposed.stages, 10)
        self.assertEqual(serialized["stages"], 10)
        self.assertEqual(QUEST_DATA[QUEST_ID]["stages"], 10)
        self.assertEqual(PRE_EOC_QUEST_CATALOG, catalog_before)

    def test_only_stage_one_journal_changes(self):
        raw = _raw_quest()
        live = QUESTS_BY_ID[QUEST_ID]
        with patch.dict(QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID):
            del QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID[QUEST_ID]
            baseline = _quest_with_stage_requirements(_quest_from_catalog(raw), raw)
        self.assertEqual(live, replace(baseline, journal_stages=live.journal_stages))
        self.assertEqual([a.stage for a, b in zip(live.journal_stages, baseline.journal_stages) if a != b], [1])
        self.assertEqual(QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID[QUEST_ID], live.journal_stages)
        self.assertEqual(QUEST_DATA[QUEST_ID], quests_as_dict()[QUEST_ID])
        self.assertEqual(raw["source"], "https://runescape.wiki/w/Do_No_Evil?oldid=6587790")
        self.assertEqual(raw["journal_source"],
                         "https://runescape.wiki/w/Do_No_Evil%2FQuick_guide?oldid=6587806")
        self.assertEqual(raw["source_revision"], 6587790)
        self.assertEqual(raw["source_timestamp"], "2012-11-19T14:55:38Z")

    def test_journal_view_preserves_complete_state(self):
        states = ((False, 0, False), (True, 0, False), (True, 1, False),
                  (True, 2, False), (True, 10, True))
        for state, inventory in product(states, ("default", "banked", "carried")):
            with self.subTest(state=state, inventory=inventory):
                player = _player(*state, inventory=inventory)
                before = copy.deepcopy(player)
                catalog_before = copy.deepcopy(QUEST_DATA)
                blockers = copy.deepcopy(quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA))
                for _ in range(3):
                    self.assertEqual(quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA),
                                     _expected_rows(*state))
                    self.assertEqual(player, before)
                    self.assertEqual(QUEST_DATA, catalog_before)
                    self.assertEqual(quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA), blockers)

    def _assert_saved_projection(self, progress):
        player = _player(progress=progress)
        control_collection, control_storage = _storage()
        control_storage.save_player_data(copy.deepcopy(player), "Mining")
        control, control_skill = control_storage.load_player_data()
        # A no-view save/load path establishes existing normalization first.
        control_rounds = []
        for _ in range(2):
            control_storage.save_player_data(control, control_skill)
            control, control_skill = control_storage.load_player_data()
            control_rounds.append(copy.deepcopy((control, control_collection.values)))

        collection, storage = _storage()
        storage.save_player_data(copy.deepcopy(player), "Mining")
        viewed, skill = storage.load_player_data()
        catalog_before = copy.deepcopy(QUEST_DATA)
        for expected_player, expected_config in control_rounds:
            before = copy.deepcopy((viewed, collection.values))
            for _ in range(3):
                self.assertEqual(quest_journal_rows_pure(viewed, QUEST_ID, QUEST_DATA),
                                 _expected_rows(True, progress, False))
                self.assertEqual((viewed, collection.values), before)
            storage.save_player_data(viewed, skill)
            viewed, skill = storage.load_player_data()
            self.assertEqual(viewed, expected_player)
            self.assertEqual(collection.values, expected_config)
            self.assertEqual(viewed["quest_action_proofs"], [])
            self.assertEqual(QUEST_DATA, catalog_before)
            self.assertEqual(quest_journal_rows_pure(viewed, QUEST_ID, QUEST_DATA),
                             _expected_rows(True, progress, False))

    def test_saved_reopen_has_no_view_side_effects(self):
        for progress in (1, 2):
            with self.subTest(progress=progress):
                self._assert_saved_projection(progress)


if __name__ == "__main__":
    unittest.main()
