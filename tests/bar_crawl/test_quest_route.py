import ast
import copy
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest_data import BAR_CRAWL_ID, QUESTS_BY_ID, quest_reward_items_as_dict
from ankiscape.logic.agility_logic import agility_target_locked_reasons_pure
from ankiscape.logic.shop_logic import apply_shop_vendor_action_pure
from ankiscape.logic_pure.logic_pure import (
    apply_quest_progress_pure,
    quest_current_stage_blocker_reasons_pure,
    start_quest_pure,
)
from tests.bar_crawl.test_vendor_actions import BAR_CRAWL_PURCHASES


class TestBarCrawlQuest(unittest.TestCase):
    def test_guard_grants_a_registered_card_with_source_backed_identity(self):
        cards = [item for item in ITEM_DEFINITIONS if item.storage_key == "Barcrawl card"]
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertEqual(card.display_name, "Barcrawl card")
        self.assertEqual(card.source_item_id, 455)
        metadata = quest_reward_items_as_dict()[card.storage_key]
        self.assertEqual(metadata["model_id"], 2430)
        self.assertEqual(metadata["client_options"], ("Read", "Drop"))
        self.assertIn("bar-crawl-harvest-2026-09-02.md", metadata["source"])
        player = self._start_and_collect(())
        self.assertEqual(player["inventory"][card.storage_key], 1)

    def test_dependent_quests_require_completed_crawl_in_the_kernel(self):
        player = self._start_and_collect(range(len(BAR_CRAWL_PURCHASES)))
        for skill in ("agility", "prayer"):
            player[f"{skill}_level"] = 99
        for quest_id in ("horror_from_the_deep", "scorpion_catcher"):
            with self.subTest(quest_id=quest_id):
                prerequisites = QUESTS_BY_ID[quest_id].required_quests
                self.assertEqual([row.quest_id for row in prerequisites], [BAR_CRAWL_ID])
                before = copy.deepcopy(player)
                blocked, started = start_quest_pure(player, quest_id, QUEST_DATA)
                self.assertFalse(started)
                self.assertEqual(blocked, before)
                self.assertEqual(player, before)
        player, ok, completed = apply_quest_progress_pure(player, BAR_CRAWL_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed)
        for quest_id in ("horror_from_the_deep", "scorpion_catcher"):
            with self.subTest(quest_id=quest_id):
                updated, started = start_quest_pure(player, quest_id, QUEST_DATA)
                self.assertTrue(started)
                self.assertTrue(updated["quests"][quest_id]["started"])

    def test_outpost_scorpion_stage_cannot_bypass_the_crawl(self):
        player = self._start_and_collect(range(len(BAR_CRAWL_PURCHASES)))
        player["inventory"]["Scorpion cage"] = 1
        player["quests"]["scorpion_catcher"] = {
            "started": True, "completed": False, "progress": 4,
        }
        before = copy.deepcopy(player)
        updated, ok, completed = apply_quest_progress_pure(player, "scorpion_catcher", QUEST_DATA)
        self.assertFalse(ok)
        self.assertFalse(completed)
        self.assertEqual(updated, before)
        self.assertEqual(player, before)
        self.assertNotIn("Reach the Barbarian Outpost scorpion room", updated["quest_action_proofs"])
        player, ok, completed = apply_quest_progress_pure(player, BAR_CRAWL_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed)
        player, ok, completed = apply_quest_progress_pure(player, "scorpion_catcher", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(player["quests"]["scorpion_catcher"]["progress"], 5)
        self.assertIn("Reach the Barbarian Outpost scorpion room", player["quest_action_proofs"])
        self.assertIn("Catch the Barbarian Outpost Kharid scorpion", player["quest_action_proofs"])

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
        self.assertEqual(quest.difficulty, "Special")
        self.assertEqual(quest.length, "Medium")
        self.assertIn("Short if the Grand Tree quest is completed and the Lodestone Network is unlocked", quest.start_point)
        # Read the existing filter tables without importing Anki's UI runtime.
        ui_path = Path(__file__).resolve().parents[2] / "ui" / "ui_tab_quests.py"
        orders = {
            target.id: ast.literal_eval(node.value)
            for node in ast.walk(ast.parse(ui_path.read_text()))
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name) and target.id in {"difficulty_order", "length_order"}
        }
        self.assertIn(quest.difficulty, orders["difficulty_order"])
        self.assertIn(quest.length, orders["length_order"])
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
