import unittest

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest_data import quests_as_dict
from ankiscape.logic_pure.logic_pure import (
    can_start_quest_pure,
    quest_locked_reasons_pure,
    start_quest_pure,
)


class TestBlackKnightsFortressRequirements(unittest.TestCase):
    def test_readout_requires_thirteen_quest_points(self):
        quest = quests_as_dict()["black_knights_fortress"]
        self.assertEqual(quest["requirements"][0], "13 Quest Points")

    def test_disguised_player_can_start_only_at_thirteen_quest_points(self):
        quests = quests_as_dict()
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["equipment"] = {"body": "Iron chainbody", "head": "Bronze med helm"}
        player["quest_points"] = 12

        self.assertFalse(can_start_quest_pure(player, "black_knights_fortress", quests))
        self.assertEqual(
            quest_locked_reasons_pure(player, "black_knights_fortress", quests),
            ("13 quest points",),
        )
        player, started = start_quest_pure(player, "black_knights_fortress", quests)
        self.assertFalse(started)
        self.assertFalse(player["quests"].get("black_knights_fortress", {}).get("started", False))
        self.assertNotEqual(player.get("current_quest"), "black_knights_fortress")

        player["quest_points"] = 13
        self.assertTrue(can_start_quest_pure(player, "black_knights_fortress", quests))
        self.assertEqual(quest_locked_reasons_pure(player, "black_knights_fortress", quests), ())
        player, started = start_quest_pure(player, "black_knights_fortress", quests)
        self.assertTrue(started)
        self.assertTrue(player["quests"]["black_knights_fortress"]["started"])
        self.assertEqual(player["current_quest"], "black_knights_fortress")
