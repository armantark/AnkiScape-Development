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

        self.assertEqual(len(ACHIEVEMENT_DEFINITIONS), 105)
        self.assertEqual(len(ACHIEVEMENTS), 105)
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
        self.assertEqual(names[-1], "Master Cook")

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
        self.assertEqual(achievement_difficulty_progress(ACHIEVEMENTS, player_data, "Easy"), (2, 34))
        self.assertEqual(achievement_progress(ACHIEVEMENTS, player_data), (2, 105, 2 / 105 * 100))

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

    def test_living_legend_uses_the_final_catalog_size(self):
        all_other_names = [name for name in ACHIEVEMENTS if name != "Living Legend"]
        player_data = {"inventory": {}, "completed_achievements": all_other_names}

        self.assertTrue(ACHIEVEMENTS["Living Legend"]["condition"](player_data))

        player_data["completed_achievements"] = all_other_names[:-1]
        self.assertFalse(ACHIEVEMENTS["Living Legend"]["condition"](player_data))


if __name__ == "__main__":
    unittest.main()
