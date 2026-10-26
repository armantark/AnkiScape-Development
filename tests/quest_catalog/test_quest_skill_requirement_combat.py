"""The extracted skill gate preserves real Combat 85 quest entry boundaries."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.logic_pure.logic_pure_combat_engine import player_combat_level_pure
from ankiscape.logic_pure.logic_pure_quest import quest_locked_reasons_pure, start_quest_pure
from tests.test_combat_quest_gate import _maxed_player_for_quest


def _player(quest_id, melee_level):
    player = _maxed_player_for_quest(quest_id)
    for skill in ("attack", "strength", "defense", "constitution", "prayer", "ranged", "magic", "summoning"):
        player[f"{skill}_level"] = 60
    player.update(attack_level=melee_level, strength_level=melee_level)
    return player


class QuestSkillRequirementCombatTest(unittest.TestCase):
    def test_combat_85_entry_refuses_below_threshold_without_mutation(self):
        for quest_id in ("smoking_kills", "dream_mentor"):
            with self.subTest(quest_id=quest_id):
                player = _player(quest_id, 60)
                before = copy.deepcopy(player)
                self.assertEqual(player_combat_level_pure(player), 84)
                self.assertEqual(quest_locked_reasons_pure(player, quest_id, QUEST_DATA), ("Combat 85",))
                result, started = start_quest_pure(player, quest_id, QUEST_DATA)
                self.assertFalse(started)
                self.assertEqual(result, before)
                self.assertEqual(player, before)

    def test_combat_85_entry_allows_exact_threshold(self):
        for quest_id in ("smoking_kills", "dream_mentor"):
            with self.subTest(quest_id=quest_id):
                player = _player(quest_id, 62)
                before = copy.deepcopy(player)
                self.assertEqual(player_combat_level_pure(player), 85)
                self.assertEqual(quest_locked_reasons_pure(player, quest_id, QUEST_DATA), ())
                result, started = start_quest_pure(player, quest_id, QUEST_DATA)
                expected = copy.deepcopy(before)
                expected["current_quest"] = quest_id
                expected["quests"][quest_id] = {"started": True, "progress": 0, "completed": False}
                self.assertTrue(started)
                self.assertEqual(result, expected)
                self.assertEqual(player, before)
