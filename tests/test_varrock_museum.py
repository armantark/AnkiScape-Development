import os
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.varrock_museum_data import (
    KUDOS_THRESHOLD_REWARDS,
    QUEST_KUDOS,
    QUIZ_DISPLAYS,
    SPECIMEN_DISPLAYS,
    VARROCK_MUSEUM_IMPLEMENTED_MAX_KUDOS,
    VARROCK_MUSEUM_SOURCE_MAX_KUDOS,
)
from ankiscape.logic.varrock_museum_logic import (
    apply_varrock_museum_command_pure,
    apply_varrock_museum_review_pure,
    sanitize_varrock_museum_state_pure,
    varrock_museum_cleaning_locked_reasons_pure,
    varrock_museum_kudos_pure,
    varrock_museum_view_pure,
)


def _player():
    return {
        "inventory": {},
        "equipment": {},
        "quests": {},
        "hunter_exp": 0.0,
        "slayer_exp": 0.0,
        "mining_exp": 0.0,
        "crafting_exp": 0.0,
        "prayer_exp": 0.0,
        "smithing_exp": 0.0,
    }


class VarrockMuseumPureTest(unittest.TestCase):
    def test_cadence_ledger_discloses_the_rate_free_landmark_translation(self):
        from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure

        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["action_id"] == "varrock_museum"
        )
        self.assertEqual(row["mode"], "activity_group")
        self.assertEqual(row["source_status"], "sourced_with_disclosed_translation")
        self.assertIn("no unrecovered probability", row["source_reason"])

    def test_activity_and_period_item_identities_have_normalized_assets(self):
        from ankiscape.core.constants import ITEM_DEFINITIONS, UTILITY_ACTIVITY_DATA

        icon_path = UTILITY_ACTIVITY_DATA["varrock_museum"].get("icon_path")
        self.assertTrue(icon_path)
        self.assertTrue(os.path.exists(icon_path))
        items = {item.storage_key: item for item in ITEM_DEFINITIONS}
        expected_ids = {
            "Trowel": 676,
            "Rock pick": 675,
            "Specimen brush": 670,
            "Uncleaned find": 11175,
            "Pottery": 11178,
            "Old coin": 11179,
            "Ancient coin": 11180,
            "Ancient symbol": 11181,
            "Old symbol": 11182,
            "Clean necklace": 11195,
        }
        for item_name, source_item_id in expected_ids.items():
            with self.subTest(item_name=item_name):
                self.assertEqual(items[item_name].source_item_id, source_item_id)
                self.assertTrue(items[item_name].asset_path)
                self.assertTrue(os.path.exists(items[item_name].asset_path))

    def test_period_tables_preserve_the_source_totals(self):
        self.assertEqual(len(QUIZ_DISPLAYS), 14)
        self.assertEqual(len(SPECIMEN_DISPLAYS), 5)
        self.assertEqual(sum(int(row["kudos"]) for row in QUEST_KUDOS), 85)
        self.assertEqual(
            [int(row["kudos"]) for row in KUDOS_THRESHOLD_REWARDS],
            [51, 101, 151],
        )
        self.assertEqual(VARROCK_MUSEUM_IMPLEMENTED_MAX_KUDOS, 173)
        self.assertEqual(VARROCK_MUSEUM_SOURCE_MAX_KUDOS, 183)

    def test_state_repair_discards_unknown_rows_and_invalid_route(self):
        state = sanitize_varrock_museum_state_pure(
            {
                "route": "broken",
                "quiz_completed": ["Lizard", "Lizard", "Fake"],
                "specimens_displayed": ["pottery", "fake"],
                "quest_stories_claimed": ["demon_slayer", "fake"],
                "threshold_rewards_claimed": ["kudos_51", "fake"],
                "cleaning_reviews": -5,
            }
        )
        self.assertEqual(state["route"], "quiz")
        self.assertEqual(state["quiz_completed"], ["Lizard"])
        self.assertEqual(state["specimens_displayed"], ["pottery"])
        self.assertEqual(state["quest_stories_claimed"], ["demon_slayer"])
        self.assertEqual(state["threshold_rewards_claimed"], ["kudos_51"])
        self.assertEqual(state["cleaning_reviews"], 0)

    def test_quiz_is_fourteen_review_beats_then_orlando_is_one_time(self):
        player = _player()
        for display in QUIZ_DISPLAYS:
            player, ok, result = apply_varrock_museum_review_pure(player)
            self.assertTrue(ok, result)
            self.assertEqual(result["display"], display)
            self.assertEqual(result["kudos"], 2)
        self.assertEqual(varrock_museum_kudos_pure(player), 28)
        self.assertTrue(varrock_museum_view_pure(player)["can_claim_orlando"])
        player, ok, result = apply_varrock_museum_command_pure(
            player, "claim_orlando_reward"
        )
        self.assertTrue(ok, result)
        self.assertEqual(player["hunter_exp"], 1000.0)
        self.assertEqual(player["slayer_exp"], 1000.0)
        _unchanged, ok, result = apply_varrock_museum_command_pure(
            player, "claim_orlando_reward"
        )
        self.assertFalse(ok)
        self.assertIn("already claimed", result["reason"])

    def test_cleaning_requires_quest_worn_leather_and_three_tools(self):
        player = _player()
        self.assertEqual(
            varrock_museum_cleaning_locked_reasons_pure(player),
            (
                "complete The Dig Site",
                "wear Leather gloves",
                "wear Leather boots",
                "carry Trowel",
                "carry Rock pick",
                "carry Specimen brush",
            ),
        )
        player, ok, result = apply_varrock_museum_command_pure(
            player, "take_cleaning_kit"
        )
        self.assertTrue(ok, result)
        self.assertEqual(
            set(player["inventory"]),
            {"Trowel", "Rock pick", "Specimen brush", "Leather gloves", "Leather boots"},
        )
        player["quests"]["the_dig_site"] = {"completed": True}
        player["equipment"] = {
            "hands": "Leather gloves",
            "feet": "Leather boots",
        }
        player["carried_inventory"] = {
            "varrock_museum": {
                "Trowel": 1,
                "Rock pick": 1,
                "Specimen brush": 1,
            }
        }
        player["inventory"].pop("Leather gloves")
        player["inventory"].pop("Leather boots")
        self.assertEqual(varrock_museum_cleaning_locked_reasons_pure(player), ())

    def test_cleaning_flattens_missing_rates_without_inventing_probability(self):
        player = _player()
        player["quests"]["the_dig_site"] = {"completed": True}
        player["equipment"] = {"hands": "Leather gloves", "feet": "Leather boots"}
        player["inventory"] = {"Trowel": 1, "Rock pick": 1, "Specimen brush": 1}
        player["carried_inventory"] = {
            "varrock_museum": {
                "Trowel": 1,
                "Rock pick": 1,
                "Specimen brush": 1,
            }
        }
        player, ok, _result = apply_varrock_museum_command_pure(
            player, "set_route", {"route": "cleaning"}
        )
        self.assertTrue(ok)
        for specimen in SPECIMEN_DISPLAYS:
            player, ok, result = apply_varrock_museum_review_pure(player)
            self.assertTrue(ok, result)
            self.assertEqual(result["specimen_id"], specimen["id"])
            self.assertNotIn("chance", result)
        self.assertEqual(varrock_museum_kudos_pure(player), 50)
        player, ok, result = apply_varrock_museum_review_pure(player)
        self.assertTrue(ok, result)
        self.assertEqual(result["unlock"], "digsite_pendant")
        self.assertTrue(player["varrock_museum"]["digsite_pendant_unlocked"])
        self.assertFalse(varrock_museum_view_pure(player)["can_review"])

    def test_minas_claims_only_completed_and_item_ready_stories_once(self):
        player = _player()
        for row in QUEST_KUDOS:
            player["quests"][row["id"]] = {"completed": True}
        player["inventory"] = {"Dagon'hai history": 1}
        player["carried_inventory"] = {
            "varrock_museum": {"Dagon'hai history": 1}
        }
        player, ok, result = apply_varrock_museum_command_pure(
            player, "claim_quest_stories"
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["kudos"], 75)
        self.assertNotIn("glorious_memories", result["quest_ids"])
        self.assertEqual(varrock_museum_kudos_pure(player), 75)
        player["inventory"]["Prophecy tablet"] = 1
        player["carried_inventory"]["varrock_museum"]["Prophecy tablet"] = 1
        player, ok, result = apply_varrock_museum_command_pure(
            player, "claim_quest_stories"
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["kudos"], 10)
        self.assertEqual(varrock_museum_kudos_pure(player), 85)
        _unchanged, ok, _result = apply_varrock_museum_command_pure(
            player, "claim_quest_stories"
        )
        self.assertFalse(ok)

    def test_first_shattered_heart_statue_supplies_its_ten_kudos(self):
        player = _player()
        self.assertEqual(varrock_museum_kudos_pure(player), 0)
        player["shattered_heart"] = {"statues_completed": 1}
        self.assertEqual(varrock_museum_kudos_pure(player), 10)

    def test_all_three_threshold_packages_are_direct_and_one_time(self):
        player = _player()
        player["varrock_museum"] = {
            "quiz_completed": list(QUIZ_DISPLAYS),
            "specimens_displayed": [row["id"] for row in SPECIMEN_DISPLAYS],
            "quest_stories_claimed": [row["id"] for row in QUEST_KUDOS],
        }
        self.assertEqual(varrock_museum_kudos_pure(player), 163)
        player, ok, result = apply_varrock_museum_command_pure(
            player, "claim_threshold_rewards"
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["reward_ids"], ("kudos_51", "kudos_101", "kudos_151"))
        self.assertEqual(player["mining_exp"], 3500.0)
        self.assertEqual(player["crafting_exp"], 6500.0)
        self.assertEqual(player["hunter_exp"], 4000.0)
        self.assertEqual(player["prayer_exp"], 4000.0)
        self.assertEqual(player["slayer_exp"], 4000.0)
        self.assertEqual(player["smithing_exp"], 4000.0)
        _unchanged, ok, _result = apply_varrock_museum_command_pure(
            player, "claim_threshold_rewards"
        )
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
