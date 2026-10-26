import unittest
import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import QUEST_DATA
from tests.reachability.live_report import live_reachability_report


class TestItemReachabilityAudit(unittest.TestCase):
    def test_report_matches_player_finishable_quest_baseline(self):
        report = live_reachability_report()

        self.assertEqual(report["action_count"], 1675)
        self.assertEqual(report["reachable_item_count"], 2359)
        self.assertEqual(report["routes"].get("Living water"), "quest-stage:druidic_ritual:2")
        self.assertEqual(report["routes"].get("Wandering wyrmwood"), "quest-stage:druidic_ritual:3")
        self.assertEqual(report["routes"].get("Stone fish"), "quest-stage:druidic_ritual:4")
        self.assertEqual((report["routes"].get("Black prism"), report["routes"].get("Book o' piracy")), ("quest:zogre_flesh_eaters", "quest:cabin_fever"))
        self.assertEqual((report["routes"].get("Fishbowl and net"), report["routes"].get("Holy wrench"), report["routes"].get("Relicym's balm")), ("quest:rum_deal", "quest:rum_deal", None))
        self.assertEqual(report["routes"].get("Stone scales"), "quest-stage:druidic_ritual:5")
        self.assertEqual(report["routes"].get("Ourg bones"), "quest-combat:zogre_flesh_eaters:zogre_flesh_eaters_slash_bash_111")
        self.assertEqual(
            report["routes"].get("Ointment of imbalance"),
            "quest-stage:druidic_ritual:6",
        )
        self.assertTrue(
            {"Combat Training Camp", "Coin", "Law Rune"}.isdisjoint(report["routes"])
        )
        self.assertEqual(report["orphan_input_count"], 161)
        self.assertEqual(report["root_orphan_count"], 30)
        self.assertEqual(report["cascade_orphan_count"], 131)
        self.assertEqual(report["unresolved_action_count"], 246)
        self.assertEqual(report["seed_item_count"], 1241)
        self.assertEqual(report["completable_quest_count"], 57)
        self.assertIn("Use the rotten apple to sabotage the mourner food stores", report["earned_quest_action_proofs"])
        self.assertEqual(len(report["blocked_quest_stage_products"]), 135)
        blocked_quest_ids = {row["quest_id"] for row in report["blocked_quest_stage_products"]}
        self.assertEqual(
            {
                "clock_tower",
                "deadliest_catch",
                "gertrudes_cat",
                "goblin_diplomacy",
                "icthlarins_little_helper",
                "lost_city",
                "monks_friend",
                "smoking_kills",
                "some_like_it_cold",
                "song_from_the_depths",
                "the_restless_ghost",
                "tribal_totem",
                "wolf_whistle",
            }
            & blocked_quest_ids,
            set(),
        )
        self.assertNotIn("the_lost_tribe", blocked_quest_ids)
        self.assertTrue({"zogre_flesh_eaters", "rum_deal", "cabin_fever"}.isdisjoint(blocked_quest_ids))
        orphan_items = {row["item"] for row in report["orphan_inputs"]}
        quest_reward_items = {
            item
            for quest in QUEST_DATA.values()
            for item in quest.get("rewards", {})
        }
        self.assertEqual(
            orphan_items & quest_reward_items,
            {"Blood talisman", "Jade vine seed"},
        )
