import unittest

from achievement_metadata import (
    ACHIEVEMENT_DIFFICULTIES,
    achievement_difficulty_progress,
    achievement_progress,
    achievement_rows_for_difficulty,
)
from constants import ACHIEVEMENTS, ACHIEVEMENT_DEFINITIONS


class AchievementMetadataTest(unittest.TestCase):
    def test_catalog_preserves_legacy_export_shape(self):
        names = list(ACHIEVEMENTS)

        self.assertEqual(len(ACHIEVEMENT_DEFINITIONS), 168)
        self.assertEqual(len(ACHIEVEMENTS), 168)
        self.assertEqual(
            names[:5],
            [
                "First Steps",
                "Novice Miner",
                "Ore Collector",
                "Jack of All Ores",
                "Rune Essence Enthusiast",
            ],
        )
        self.assertEqual(names[names.index("Living Legend") + 1], "Gem Finder")
        self.assertEqual(names[-1], "Master Mage")

        for data in ACHIEVEMENTS.values():
            self.assertIn(data["difficulty"], ACHIEVEMENT_DIFFICULTIES)
            self.assertIsInstance(data["description"], str)
            self.assertTrue(callable(data["condition"]))

    def test_grouped_rows_share_difficulty_order_and_completion_counts(self):
        player_data = {
            "inventory": {},
            "completed_achievements": ["First Steps", "Rune Mysteries"],
        }

        self.assertEqual(
            ACHIEVEMENT_DIFFICULTIES,
            ("Easy", "Moderate", "Difficult", "Very Challenging"),
        )
        easy_rows = achievement_rows_for_difficulty(ACHIEVEMENTS, player_data, "Easy")
        completed_easy = {row.name for row in easy_rows if row.completed}

        self.assertIn("First Steps", completed_easy)
        self.assertIn("Rune Mysteries", completed_easy)
        self.assertEqual(achievement_difficulty_progress(ACHIEVEMENTS, player_data, "Easy"), (2, 58))
        self.assertEqual(achievement_progress(ACHIEVEMENTS, player_data), (2, 168, 2 / 168 * 100))

    def test_representative_conditions_cover_skill_quest_and_claim_state(self):
        player_data = {
            "inventory": {
                "Iron ore": 100,
                "Oak logs": 500,
                "Air rune": 1000,
                "Bronze bar": 1,
                "Raw shrimps": 1,
            },
            "quests": {"rune_mysteries": {"completed": True}},
            "claims": {"wicked_hood": {"claimed": True}},
            "completed_achievements": [],
        }

        self.assertTrue(ACHIEVEMENTS["Iron Initiate"]["condition"](player_data))
        self.assertTrue(ACHIEVEMENTS["Oak Enthusiast"]["condition"](player_data))
        self.assertTrue(ACHIEVEMENTS["Rune Stockpile"]["condition"](player_data))
        self.assertTrue(ACHIEVEMENTS["Novice Smith"]["condition"](player_data))
        self.assertTrue(ACHIEVEMENTS["First Catch"]["condition"](player_data))
        self.assertTrue(ACHIEVEMENTS["Rune Mysteries"]["condition"](player_data))
        self.assertTrue(ACHIEVEMENTS["Hooded Runecrafter"]["condition"](player_data))

    def test_pottery_and_activity_conditions_use_live_canonical_state(self):
        self.assertTrue(
            ACHIEVEMENTS["Pottery Apprentice"]["condition"](
                {"inventory": {"Empty pot": 100}}
            )
        )

        five_families = {
            family: 1
            for family in ("brimhaven", "skullball", "gnome_ball", "pit", "circus")
        }
        condition = ACHIEVEMENTS["Activity Circuit"]["condition"]
        self.assertFalse(condition({"agility_activity_completions": five_families}))
        five_families["flash_powder_factory"] = 1
        self.assertTrue(condition({"agility_activity_completions": five_families}))

    def test_farming_achievements_use_durable_backend_counters(self):
        player_data = {
            "inventory": {},
            "farming_level": 99,
            "farming_counters": {
                "plants": 1,
                "produce_harvested": 10_000,
                "tree_health_checks": 1,
                "full_runs": 1,
            },
        }
        farming_names = (
            "First Plant",
            "Novice Farmer",
            "Intermediate Farmer",
            "Expert Farmer",
            "Master Farmer",
            "Produce Collector",
            "Produce Hoarder",
            "Produce Stockpile",
            "Tree Doctor",
            "Full Farm Run",
        )
        for name in farming_names:
            self.assertTrue(ACHIEVEMENTS[name]["condition"](player_data), name)

        player_data["inventory"]["Potato"] = 1_000_000
        player_data["farming_counters"]["produce_harvested"] = 99
        self.assertFalse(ACHIEVEMENTS["Produce Collector"]["condition"](player_data))
        player_data["inventory"].clear()
        player_data["farming_counters"]["produce_harvested"] = 100
        self.assertTrue(ACHIEVEMENTS["Produce Collector"]["condition"](player_data))

    def test_every_farming_achievement_has_an_exact_boundary(self):
        boundaries = (
            ("First Plant", "plants", 1),
            ("Produce Collector", "produce_harvested", 100),
            ("Produce Hoarder", "produce_harvested", 1_000),
            ("Produce Stockpile", "produce_harvested", 10_000),
            ("Tree Doctor", "tree_health_checks", 1),
            ("Full Farm Run", "full_runs", 1),
        )
        for name, counter, threshold in boundaries:
            with self.subTest(name=name):
                player_data = {"farming_level": 1, "farming_counters": {counter: threshold - 1}}
                self.assertFalse(ACHIEVEMENTS[name]["condition"](player_data))
                player_data["farming_counters"][counter] = threshold
                self.assertTrue(ACHIEVEMENTS[name]["condition"](player_data))

        levels = (
            ("Novice Farmer", 10),
            ("Intermediate Farmer", 30),
            ("Expert Farmer", 60),
            ("Master Farmer", 99),
        )
        for name, threshold in levels:
            with self.subTest(name=name):
                self.assertFalse(ACHIEVEMENTS[name]["condition"]({"farming_level": threshold - 1}))
                self.assertTrue(ACHIEVEMENTS[name]["condition"]({"farming_level": threshold}))

    def test_thieving_achievements_use_durable_success_and_level_counters(self):
        boundaries = (
            ("First Lift", "thieving_success_count", 1),
            ("Sticky Fingers", "thieving_success_count", 100),
            ("Novice Thief", "thieving_level", 10),
            ("Master Thief", "thieving_level", 99),
        )
        for name, key, threshold in boundaries:
            with self.subTest(name=name):
                self.assertFalse(ACHIEVEMENTS[name]["condition"]({key: threshold - 1}))
                self.assertTrue(ACHIEVEMENTS[name]["condition"]({key: threshold}))

    def test_living_legend_uses_the_final_catalog_size(self):
        all_other_names = [name for name in ACHIEVEMENTS if name != "Living Legend"]
        player_data = {"inventory": {}, "completed_achievements": all_other_names}

        self.assertTrue(ACHIEVEMENTS["Living Legend"]["condition"](player_data))

        player_data["completed_achievements"] = all_other_names[:-1]
        self.assertFalse(ACHIEVEMENTS["Living Legend"]["condition"](player_data))


if __name__ == "__main__":
    unittest.main()
