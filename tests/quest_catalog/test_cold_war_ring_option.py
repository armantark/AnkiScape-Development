import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure,
    quest_current_stage_blockers_pure,
)


class TestColdWarRingOption(unittest.TestCase):
    def _player(self, inventory, equipment=None):
        return {
            "inventory": inventory,
            "equipment": equipment or {},
            "quests": {
                "cold_war": {"started": True, "progress": 3, "completed": False},
            },
            # Isolate the item gate from the rest of the stage route.
            "quest_action_proofs": ["Complete Cold War stage 3 objective"],
        }

    def _assert_accepted(self, player):
        self.assertEqual(quest_current_stage_blockers_pure(player, "cold_war", QUEST_DATA), ())

        updated, progressed, completed = apply_quest_progress_pure(player, "cold_war", QUEST_DATA)

        self.assertTrue(progressed)
        self.assertFalse(completed)
        self.assertEqual(updated["quests"]["cold_war"]["progress"], 4)
        self.assertEqual(player["quests"]["cold_war"]["progress"], 3)

    def _assert_refused(self, player):
        blockers = quest_current_stage_blockers_pure(player, "cold_war", QUEST_DATA)
        self.assertEqual([row["kind"] for row in blockers], ["missing_item_option"])
        self.assertEqual(
            blockers[0]["options"],
            (
                {"item_name": "Raw cod", "quantity": 1},
                {"item_name": "Ring of charos (a)", "quantity": 1},
            ),
        )

        updated, progressed, completed = apply_quest_progress_pure(player, "cold_war", QUEST_DATA)

        self.assertFalse(progressed)
        self.assertFalse(completed)
        self.assertEqual(updated, player)
        self.assertEqual(updated["quests"]["cold_war"]["progress"], 3)

    def test_activated_ring_accepts_stage_in_inventory_or_equipped(self):
        for location in ("inventory", "equipment"):
            with self.subTest(location=location):
                player = self._player(
                    {"Ring of charos (a)": 1} if location == "inventory" else {},
                    {"ring": "Ring of charos (a)"} if location == "equipment" else {},
                )
                self._assert_accepted(player)

    def test_raw_cod_accepts_stage_without_ring(self):
        self._assert_accepted(self._player({"Raw cod": 1}))

    def test_unactivated_ring_refuses_stage_in_inventory_or_equipped(self):
        for location in ("inventory", "equipment"):
            with self.subTest(location=location):
                player = self._player(
                    {"Ring of Charos": 1} if location == "inventory" else {},
                    {"ring": "Ring of Charos"} if location == "equipment" else {},
                )
                self._assert_refused(player)

    def test_missing_items_refuse_stage(self):
        for inventory in ({}, {"Raw cod": 0, "Ring of charos (a)": 0}):
            with self.subTest(inventory=inventory):
                self._assert_refused(self._player(inventory))
