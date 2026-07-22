import unittest

from achievement_metadata import (
    ACHIEVEMENT_DIFFICULTIES,
    achievement_difficulty_progress,
    achievement_progress,
    achievement_rows_for_difficulty,
)
from constants import ACHIEVEMENTS, ACHIEVEMENT_DEFINITIONS
from logic_pure import get_newly_completed_achievements, record_achievement_progress_pure


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
            "inventory": {},
            "achievement_progress": {
                "version": 1,
                "skills": {
                    "mining": {"outputs": {"Iron ore": 100}},
                    "woodcutting": {"outputs": {"Oak logs": 500}},
                    "runecrafting": {"outputs": {"Air rune": 1000}},
                    "smithing": {"outputs": {"Bronze bar": 1}},
                    "fishing": {"outputs": {"Raw shrimps": 1}},
                },
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

    def test_pottery_and_activity_conditions_use_durable_canonical_state(self):
        self.assertTrue(
            ACHIEVEMENTS["Pottery Apprentice"]["condition"](
                {"achievement_progress": {"skills": {"crafting": {"outputs": {"Empty pot": 100}}}}}
            )
        )

        four_families = {
            family: 1
            for family in ("brimhaven", "skullball", "gnome_ball", "pit")
        }
        condition = ACHIEVEMENTS["Activity Circuit"]["condition"]
        self.assertFalse(condition({"agility_activity_completions": four_families}))
        four_families["flash_powder_factory"] = 1
        self.assertTrue(condition({"agility_activity_completions": four_families}))

    def test_smithing_conditions_use_durable_canonical_bar_names(self):
        progress = {
            "skills": {
                "smithing": {"outputs": {"Adamant bar": 250, "Rune bar": 100}}
            }
        }

        self.assertTrue(ACHIEVEMENTS["Adamantite Artisan"]["condition"]({"achievement_progress": progress}))
        self.assertTrue(ACHIEVEMENTS["Runite Refiner"]["condition"]({"achievement_progress": progress}))

    def test_action_achievements_survive_spending_their_outputs(self):
        player_data = {"inventory": {"Iron ore": 100}}
        for _ in range(100):
            record_achievement_progress_pure(
                player_data,
                "mining",
                "iron_rock",
                True,
                output_item="Iron ore",
            )
        player_data["inventory"]["Iron ore"] = 0

        self.assertTrue(ACHIEVEMENTS["Iron Initiate"]["condition"](player_data))
        self.assertFalse(ACHIEVEMENTS["Bronze Master"]["condition"](player_data))

    def test_cumulative_progress_unlocks_after_the_output_has_left_the_bank(self):
        player_data = {"inventory": {}, "completed_achievements": []}
        record_achievement_progress_pure(
            player_data,
            "firemaking",
            "normal_logs",
            True,
            output_item="Ashes",
        )
        player_data["inventory"]["Ashes"] = 0

        newly_completed = get_newly_completed_achievements(player_data, ACHIEVEMENTS)

        self.assertIn("First Fire", newly_completed)

    def test_potion_hold_achievements_are_dose_invariant(self):
        condition = ACHIEVEMENTS["Potion Collector"]["condition"]

        self.assertTrue(condition({"inventory": {"Attack potion (4)": 100}}))
        self.assertTrue(condition({"inventory": {"Attack potion (2)": 200}}))
        self.assertTrue(condition({"inventory": {"Attack flask (6)": 66, "Attack potion (4)": 1}}))
        self.assertFalse(condition({"inventory": {"Attack potion (4)": 99}}))

    def test_explicit_hold_achievement_remains_live_inventory_state(self):
        player_data = {
            "inventory": {"Agility arena ticket": 100},
            "achievement_progress": {
                "skills": {"agility": {"outputs": {"Agility arena ticket": 500}}}
            },
        }
        condition = ACHIEVEMENTS["Arena Regular"]["condition"]

        self.assertTrue(condition(player_data))
        player_data["inventory"]["Agility arena ticket"] = 0
        self.assertFalse(condition(player_data))

    def test_action_credit_belongs_to_the_explicit_owner_skill(self):
        player_data = {"inventory": {}}
        record_achievement_progress_pure(
            player_data,
            "magic",
            "superheat_item",
            True,
            output_item="Bronze bar",
        )
        record_achievement_progress_pure(
            player_data,
            "construction",
            "make_tablet",
            True,
            output_item="Varrock teleport",
        )

        self.assertFalse(ACHIEVEMENTS["Novice Smith"]["condition"](player_data))
        self.assertEqual(
            player_data["achievement_progress"]["skills"]["construction"]["actions"],
            {"make_tablet": 1},
        )

    def test_rune_stockpile_excludes_tiara_outputs(self):
        player_data = {
            "achievement_progress": {
                "skills": {"runecrafting": {"outputs": {"Air tiara": 1_000}}}
            }
        }

        self.assertFalse(ACHIEVEMENTS["Rune Stockpile"]["condition"](player_data))

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

    def test_final_other_achievement_unlocks_living_legend_in_same_dispatch(self):
        completed = [
            name
            for name in ACHIEVEMENTS
            if name not in {"Living Legend", "Master Mage"}
        ]
        player_data = {
            "inventory": {},
            "magic_level": 99,
            "completed_achievements": completed,
        }

        self.assertEqual(
            get_newly_completed_achievements(player_data, ACHIEVEMENTS),
            ["Master Mage", "Living Legend"],
        )


if __name__ == "__main__":
    unittest.main()
