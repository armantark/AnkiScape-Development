import copy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest_data import BAR_CRAWL_ID, QUESTS_BY_ID
from ankiscape.logic.agility_logic import agility_target_locked_reasons_pure
from ankiscape.logic.shop_logic import apply_shop_vendor_action_pure
from ankiscape.logic_pure.logic_pure import (
    apply_quest_progress_pure,
    quest_current_stage_blocker_reasons_pure,
    start_quest_pure,
)
from tests.bar_crawl.test_vendor_actions import BAR_CRAWL_PURCHASES


class TestBarCrawlQuest(unittest.TestCase):
    def _assert_outpost_access(self, player, allowed):
        for course in ("barbarian_normal", "barbarian_advanced"):
            with self.subTest(course=course):
                self.assertEqual(
                    agility_target_locked_reasons_pure(player, course),
                    () if allowed else ("Bar Crawl",),
                )

    def _start_and_collect(self, order):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["agility_level"] = 99
        player["inventory"]["Coins"] = sum(row[1] for row in BAR_CRAWL_PURCHASES)
        self._assert_outpost_access(player, False)
        player, started = start_quest_pure(player, BAR_CRAWL_ID, QUEST_DATA)
        self.assertTrue(started)
        self.assertFalse(player["quests"][BAR_CRAWL_ID]["completed"])
        player, ok, completed = apply_quest_progress_pure(player, BAR_CRAWL_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(player["quests"][BAR_CRAWL_ID]["progress"], 2)
        self.assertEqual(player["inventory"]["Barcrawl card"], 1)
        for index in order:
            action_id, _, _, _ = BAR_CRAWL_PURCHASES[index]
            player, result = apply_shop_vendor_action_pure(player, action_id)
            self.assertTrue(result["allowed"], result)
            self.assertFalse(player["quests"][BAR_CRAWL_ID]["completed"])
            self._assert_outpost_access(player, False)
        return player

    def test_shuffled_drinks_then_guard_return_completes_and_opens_both_courses(self):
        player = self._start_and_collect((7, 2, 9, 0, 5, 8, 1, 6, 3, 4))
        self.assertEqual(quest_current_stage_blocker_reasons_pure(player, BAR_CRAWL_ID, QUEST_DATA), ())
        before = copy.deepcopy(player)
        player, ok, completed = apply_quest_progress_pure(player, BAR_CRAWL_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed)
        self.assertEqual(player["quests"][BAR_CRAWL_ID]["progress"], 3)
        self.assertTrue(player["quests"][BAR_CRAWL_ID]["completed"])
        self.assertEqual(player["inventory"], before["inventory"])
        self.assertEqual(player["quest_points"], before["quest_points"])
        self.assertEqual(
            {key: value for key, value in player.items() if key.endswith("_exp")},
            {key: value for key, value in before.items() if key.endswith("_exp")},
        )
        self.assertEqual(player.get("pending_skill_exp_rewards", {}), before.get("pending_skill_exp_rewards", {}))
        self.assertNotIn("bar_crawl_completed", player)
        self._assert_outpost_access(player, True)
        player, ok, completed = apply_quest_progress_pure(player, BAR_CRAWL_ID, QUEST_DATA)
        self.assertFalse(ok)
        self.assertFalse(completed)

    def test_any_missing_drink_blocks_the_guard_return(self):
        order = (7, 2, 9, 0, 5, 8, 1, 6, 3, 4)
        for missing in order:
            with self.subTest(missing=BAR_CRAWL_PURCHASES[missing][0]):
                player = self._start_and_collect(index for index in order if index != missing)
                self.assertEqual(
                    quest_current_stage_blocker_reasons_pure(player, BAR_CRAWL_ID, QUEST_DATA),
                    (f"Action required: {BAR_CRAWL_PURCHASES[missing][2]}",),
                )
                before = copy.deepcopy(player)
                player, ok, completed = apply_quest_progress_pure(player, BAR_CRAWL_ID, QUEST_DATA)
                self.assertFalse(ok)
                self.assertFalse(completed)
                self.assertEqual(player, before)
                self._assert_outpost_access(player, False)

    def test_metadata_and_proof_stage_match_the_settled_contract(self):
        quest = QUESTS_BY_ID[BAR_CRAWL_ID]
        self.assertEqual(quest.display_name, "Alfred Grimhand's Barcrawl")
        self.assertEqual(quest.stages, 3)
        self.assertTrue(quest.members)
        self.assertEqual(quest.difficulty, "none")
        self.assertEqual(quest.length, "Medium (Short if the Grand Tree quest is completed and the Lodestone Network is unlocked)")
        self.assertEqual(quest.release_date, "2002-03-25")
        self.assertIn("medium confidence", quest.source)
        self.assertEqual(quest.timeline, "PLACEHOLDER(quests.bar_crawl.timeline)")
        self.assertEqual(quest.requirements, ())
        self.assertEqual(quest.required_quests, ())
        self.assertEqual(quest.required_skills, ())
        self.assertEqual(quest.required_items, ())
        self.assertEqual(quest.point_reward, 0)
        self.assertEqual(quest.rewards, ())
        self.assertEqual(quest.xp_rewards, ())
        proof_stages = [stage for stage in quest.stage_requirements if stage.required_actions]
        self.assertEqual(len(proof_stages), 1)
        self.assertEqual(proof_stages[0].stage, 2)
        self.assertEqual(proof_stages[0].required_actions, tuple(row[2] for row in BAR_CRAWL_PURCHASES))
        self.assertTrue(all(not stage.combat_encounters for stage in quest.stage_requirements))


if __name__ == "__main__":
    unittest.main()
