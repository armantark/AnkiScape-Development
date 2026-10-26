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


QUEST_ID = "desert_treasure"
EXPECTED_SUPPLIES = (
    "6 Steel bars", "12 Magic logs", "6 Molten glass", "1 Charcoal",
    "1 Blood rune", "1 Ashes", "1 Bones",
)
NOTING_QUALIFICATION = (
    "The steel bars, magic logs, molten glass, bones, and ashes may be noted. "
    "The charcoal must be unnoted."
)
SUPPLY_INVENTORY = {
    "Steel bar": 6, "Magic logs": 12, "Molten glass": 6, "Charcoal": 1,
    "Blood rune": 1, "Ashes": 1, "Bones": 1,
}


class TestDesertTreasureMirrorJournal(unittest.TestCase):
    def test_composed_journal_matches_source(self):
        catalog_before = copy.deepcopy(PRE_EOC_QUEST_CATALOG)
        raw = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        original = {row["stage"]: tuple(row["journal"]) for row in raw["journal_stages"]}
        self.assertEqual(len(original[1]), 9)
        self.assertEqual(original[1][5], "Items Needed:")
        self.assertEqual(original[1][6], NOTING_QUALIFICATION)
        expected = dict(original)
        expected[1] = original[1][:6] + EXPECTED_SUPPLIES + original[1][6:]
        live = QUESTS_BY_ID[QUEST_ID]
        serialized = quests_as_dict()[QUEST_ID]
        journals = {row.stage: row.journal for row in live.journal_stages}
        for actual in (journals, serialized["journal_stages"], QUEST_DATA[QUEST_ID]["journal_stages"]):
            self.assertEqual(actual, expected)
            self.assertEqual(tuple(actual), tuple(range(1, 10)))
            self.assertEqual(len(actual[1]), 16)
            self.assertEqual(actual[1][5:14], ("Items Needed:",) + EXPECTED_SUPPLIES + (NOTING_QUALIFICATION,))
            self.assertEqual(actual[1][:6] + actual[1][13:], original[1])
            for supply in EXPECTED_SUPPLIES:
                self.assertEqual(actual[1].count(supply), 1)
            for stage in range(2, 10):
                self.assertEqual(actual[stage], original[stage])
        self.assertEqual(live.stages, 10)
        self.assertEqual(serialized["stages"], 10)
        self.assertEqual(QUEST_DATA[QUEST_ID]["stages"], 10)
        self.assertEqual(PRE_EOC_QUEST_CATALOG, catalog_before)

    def test_only_journal_definition_changes(self):
        raw = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        live = QUESTS_BY_ID[QUEST_ID]
        with patch.dict(QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID):
            del QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID[QUEST_ID]
            baseline = _quest_with_stage_requirements(_quest_from_catalog(raw), raw)
        self.assertNotEqual(live.journal_stages, baseline.journal_stages)
        self.assertEqual(live, replace(baseline, journal_stages=live.journal_stages))
        self.assertEqual(QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID[QUEST_ID], live.journal_stages)

    def test_view_preserves_player_and_blockers(self):
        states = ((False, 0, False), (True, 0, False), (True, 1, False),
                  (True, 2, False), (True, 10, True))
        for (started, progress, completed), mode in product(states, ("absent", "banked", "carried")):
            with self.subTest(started=started, progress=progress, completed=completed, mode=mode):
                # Disposable projection fixtures establish no acquisition or performed deed.
                player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                player["quests"][QUEST_ID] = {
                    "started": started, "progress": progress, "completed": completed,
                }
                if mode != "absent":
                    key = "inventory" if mode == "banked" else "carried_inventory"
                    player[key].update(SUPPLY_INVENTORY)
                player["quest_action_proofs"] = {}
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
                } for stage in range(1, min(visible, 9) + 1))
                for _ in range(3):
                    rows = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
                    self.assertEqual(rows, expected_rows)
                    if rows:
                        self.assertEqual(rows[0]["lines"][6:13], EXPECTED_SUPPLIES)
                    self.assertEqual(player, player_before)
                    self.assertEqual(QUEST_DATA, quest_data_before)
                    self.assertEqual(
                        quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA),
                        blockers_before,
                    )


if __name__ == "__main__":
    unittest.main()
