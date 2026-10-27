"""Ordinary openings followed by explicitly seeded later sentinel compatibility."""

import unittest
import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.logic_pure.logic_pure_quest import apply_quest_progress_pure, apply_quest_combat_encounter_pure
from tests.quest_catalog.hazeel_helpers import fresh_player, complete_opening


class HazeelCompletionCompatibilityTest(unittest.TestCase):
    def test_hazeel_cult_routes_grant_only_their_own_artifact(self):
        quest_id = "hazeel_cult"
        route_cases = (
            (
                "Side with Ceril Carnillean",
                {"Carnillean armour": 1, "Coins": 2005},
            ),
            (
                "Side with Hazeel's cult",
                {"Coins": 2005, "Mark of Hazeel": 1},
            ),
        )
        for route_id, expected_grants in route_cases:
            with self.subTest(route=route_id):
                baseline = fresh_player()
                inventory_before = dict(baseline["inventory"])
                player_data = complete_opening("carnillean" if route_id == "Side with Ceril Carnillean" else "hazeel")
                if route_id == "Side with Hazeel's cult":
                    self.assertEqual(player_data["inventory"]["Mark of Hazeel"], 1)
                # Later sentinel fixtures test completion compatibility only;
                # they do not qualify ordinary later quest deeds.
                actions = player_data["quest_action_proofs"]
                actions.append("Complete Hazeel Cult stage 2 objective")
                if route_id == "Side with Ceril Carnillean":
                    player_data = self._resolve_later_alomone(player_data, quest_id)
                player_data, ok, completed_now = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["quests"][quest_id]["progress"], 3)
                if route_id == "Side with Ceril Carnillean":
                    self.assertEqual(player_data["inventory"]["Carnillean armour"], 2)

                actions = player_data["quest_action_proofs"]
                actions.append("Complete Hazeel Cult stage 3 objective")
                player_data, ok, completed_now = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertTrue(ok)
                self.assertTrue(completed_now)
                grants = {
                    item_name: amount - inventory_before.get(item_name, 0)
                    for item_name, amount in player_data["inventory"].items()
                    if amount > inventory_before.get(item_name, 0)
                }
                self.assertEqual(grants, expected_grants)
                if route_id == "Side with Hazeel's cult":
                    self.assertEqual(player_data["inventory"]["Mark of Hazeel"], 1)

    def _resolve_later_alomone(self, player_data, quest_id):
        player_data.update(
            {
                "attack_level": 99,
                "constitution_level": 99,
                "defense_level": 99,
                "strength_level": 99,
            }
        )
        for expected_remaining in (1, 0):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                quest_id,
                QUEST_DATA,
                "hazeel_cult_alomone_13",
            )
            self.assertTrue(ok, result)
            self.assertTrue(result["killed"], result)
            self.assertEqual(result["remaining_quantity"], expected_remaining)
        return player_data
