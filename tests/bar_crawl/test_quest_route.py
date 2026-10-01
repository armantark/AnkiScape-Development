import ast
import copy
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest_data import BAR_CRAWL_ID, QUESTS_BY_ID, quest_reward_items_as_dict
from ankiscape.logic.agility_logic import agility_target_locked_reasons_pure
from ankiscape.logic_pure.logic_pure import start_quest_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.test_runtime_actions import _context

# Ruling 4.28 item 5 bar order; prices from Bar Crawl oldid 6304383.
BAR_ROUTE = (
    ("Uncle Humphrey's Gutrot", "Blue Moon Inn", 50),
    ("Fire Toad Blast", "Blurberry's Bar", 10),
    ("Supergrog", "Dead Man's Chest", 15),
    ("Fire Brandy", "Dragon Inn", 12),
    ("Heart Stopper", "Flying Horse Inn", 8),
    ("Liverbane Ale", "Forester's Arms", 18),
    ("Olde Suspiciouse", "Jolly Boar Inn", 10),
    ("Ape Bite Liqueur", "Karamja Wines, Spirits, and Beers", 7),
    ("Hand of Death Cocktail", "Rising Sun", 70),
    ("Black Skull Ale", "Rusty Anchor", 8),
)
RETURN_STAGE = len(BAR_ROUTE) + 2


class TestBarCrawlQuest(unittest.TestCase):
    def _player(self, coins=sum(row[2] for row in BAR_ROUTE)):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["agility_level"] = 99
        player["inventory"]["Coins"] = coins
        player["current_quest"] = BAR_CRAWL_ID
        self._assert_outpost_access(player, False)
        return player

    def _review(self, player):
        calls = {"xp": [], "saves": 0, "errors": []}
        return handle_quest_answer(_context(player, calls)), calls

    def _review_to(self, player, progress):
        while player["quests"].get(BAR_CRAWL_ID, {}).get("progress", 0) < progress:
            ok, calls = self._review(player)
            self.assertTrue(ok, calls["errors"])
        return player

    def _assert_outpost_access(self, player, allowed):
        for course in ("barbarian_normal", "barbarian_advanced"):
            with self.subTest(course=course):
                self.assertEqual(
                    agility_target_locked_reasons_pure(player, course),
                    () if allowed else ("Bar Crawl",),
                )

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
        player = self._review_to(self._player(), 2)
        self.assertEqual(player["inventory"][card.storage_key], 1)

    def test_each_review_drinks_at_the_next_bar_then_the_guard_return_completes(self):
        player = self._review_to(self._player(), 2)
        for index, (drink, bar, price) in enumerate(BAR_ROUTE):
            with self.subTest(bar=bar):
                coins = player["inventory"]["Coins"]
                ok, calls = self._review(player)
                self.assertTrue(ok)
                self.assertEqual(calls["errors"], [])
                self.assertEqual(player["quests"][BAR_CRAWL_ID]["progress"], index + 3)
                self.assertEqual(player["inventory"]["Coins"], coins - price)
                self.assertEqual(player["inventory"]["Barcrawl card"], 1)
                self.assertIn(f"Drink {drink} at {bar}", player["quest_action_proofs"])
                for later_drink, later_bar, _ in BAR_ROUTE[index + 1:]:
                    self.assertNotIn(f"Drink {later_drink} at {later_bar}", player["quest_action_proofs"])
                self.assertFalse(player["quests"][BAR_CRAWL_ID]["completed"])
                self._assert_outpost_access(player, False)
        self.assertEqual(player["inventory"]["Coins"], 0)

        before = copy.deepcopy(player)
        ok, calls = self._review(player)
        self.assertTrue(ok)
        self.assertEqual(player["quests"][BAR_CRAWL_ID]["progress"], RETURN_STAGE + 1)
        self.assertTrue(player["quests"][BAR_CRAWL_ID]["completed"])
        self.assertEqual(calls["errors"][0][0], "Quest complete")
        self.assertEqual(player["inventory"], before["inventory"])
        self.assertEqual(player["quest_points"], before["quest_points"])
        self.assertEqual(
            {key: value for key, value in player.items() if key.endswith("_exp")},
            {key: value for key, value in before.items() if key.endswith("_exp")},
        )
        self.assertNotIn("bar_crawl_completed", player)
        self._assert_outpost_access(player, True)

    def test_short_coins_or_lost_card_switch_questing_off_with_one_reason_per_line(self):
        player = self._review_to(self._player(), 4)
        player["inventory"]["Coins"] = 14
        del player["inventory"]["Barcrawl card"]
        before = copy.deepcopy(player)
        ok, calls = self._review(player)
        self.assertFalse(ok)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(player, before)
        self.assertEqual(calls["errors"], [(
            "Quest blocked",
            "Alfred Grimhand's Barcrawl is blocked:\n"
            "• Needs Barcrawl card x1\n"
            "• Needs Coins x15\n\n"
            "Questing has been switched off until this is resolved.",
        )])
        player["inventory"]["Barcrawl card"] = 1
        player["inventory"]["Coins"] = 15
        ok, calls = self._review(player)
        self.assertTrue(ok)
        self.assertEqual(player["quests"][BAR_CRAWL_ID]["progress"], 5)
        self.assertEqual(player["inventory"]["Coins"], 0)

    def test_dependent_quests_require_completed_crawl_in_the_kernel(self):
        player = self._review_to(self._player(), RETURN_STAGE)
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
        player = self._review_to(player, RETURN_STAGE + 1)
        self.assertTrue(player["quests"][BAR_CRAWL_ID]["completed"])
        for quest_id in ("horror_from_the_deep", "scorpion_catcher"):
            with self.subTest(quest_id=quest_id):
                updated, started = start_quest_pure(player, quest_id, QUEST_DATA)
                self.assertTrue(started)
                self.assertTrue(updated["quests"][quest_id]["started"])

    def test_metadata_matches_the_settled_contract(self):
        quest = QUESTS_BY_ID[BAR_CRAWL_ID]
        self.assertEqual(quest.display_name, "Alfred Grimhand's Barcrawl")
        self.assertEqual(quest.stages, RETURN_STAGE + 1)
        self.assertEqual(len(quest.journal_stages), quest.stages)
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
        self.assertEqual(quest.release_date, "PLACEHOLDER(quests.bar_crawl.release_date)")
        self.assertIn("Release date unrecovered", quest.source)
        self.assertEqual(quest.timeline, "PLACEHOLDER(quests.bar_crawl.timeline)")
        self.assertEqual(quest.requirements, ())
        self.assertEqual(quest.required_quests, ())
        self.assertEqual(quest.required_skills, ())
        self.assertEqual(quest.required_items, ())
        self.assertEqual(quest.point_reward, 0)
        self.assertEqual(quest.rewards, ())
        self.assertEqual(quest.xp_rewards, ())
        self.assertTrue(all(not stage.combat_encounters for stage in quest.stage_requirements))


if __name__ == "__main__":
    unittest.main()
