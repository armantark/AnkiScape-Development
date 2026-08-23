import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.logic_pure.logic_pure import (
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    quest_current_stage_blocker_reasons_pure,
    start_quest_pure,
)

_ALL_SKILLS = (
    "attack",
    "strength",
    "defense",
    "constitution",
    "prayer",
    "mining",
    "smithing",
    "woodcutting",
    "firemaking",
    "cooking",
    "fishing",
    "farming",
    "herblore",
    "crafting",
    "thieving",
    "fletching",
    "slayer",
    "agility",
    "magic",
    "runecrafting",
    "construction",
    "hunter",
)

# Shared travel-kit inventory so each converted stage's non-route requirements clear.
_TRAVEL_KIT = {
    "Knife": 1,
    "Tinderbox": 1,
    "Secateurs": 1,
    "Spade": 1,
    "Hammer": 1,
    "Rope": 1,
    "Bow": 1,
    "Plank": 1,
    "Coal": 1,
    "Barrel of coal-tar": 1,
    "Barrel": 1,
    "Potatoes": 1,
    "Sapphire amulet": 1,
    "Dramen staff": 1,
    "Coins": 100000,
    "Pirate clothing": 1,
    "Book o' piracy": 1,
    "Explorer's ring 3": 1,
    "Plant pot": 1,
    "Antipoison": 1,
    "Soft clay": 1,
    "Empty Pot": 1,
    "Clean irit": 1,
    "Vial": 1,
    "Earth rune": 10,
    "Earth staff": 10,
    "Lava battlestaff": 1,
    "Mindspike (earth)": 1,
    "Mud battlestaff": 1,
    "Lyre": 1,
    "Staff": 1,
    "Pestle and mortar": 1,
    "Cosmic rune": 8,
    "Water rune": 8,
    "Water staff": 1,
    "Desert clothing": 1,
    "Weight-reducing clothing": 1,
    "Waterskin": 1,
    "Explorer's ring": 1,
    "Amulet of glory": 1,
    "Mourner gear": 1,
    "Death talisman": 1,
    "Death talisman staff": 1,
    "Death tiara": 1,
    "Wicked hood": 1,
    "Omni-talisman": 1,
    "Omni-talisman staff": 1,
    "Omni-tiara": 1,
    "Any woodcutting hatchet": 1,
    "Machete": 1,
    "Gardening trowel": 1,
}


def _player_with_prerequisites(prerequisite_ids):
    player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for skill_id in _ALL_SKILLS:
        player_data[f"{skill_id}_level"] = 99
    player_data["ranged_level"] = 75
    for quest_id in prerequisite_ids:
        player_data["quests"][quest_id] = {"started": True, "progress": 99, "completed": True}
    player_data["inventory"].update(_TRAVEL_KIT)
    player_data["quest_combat_config"] = {"resolver_enabled": True}
    return player_data


def _record_required_actions(player_data, quest_id):
    """Record the stage's required_action texts, standing in for the player performing them.

    Required actions are satisfied by performing the named step in production (a cast,
    an item use); only the converted route text must appear here without any manual step.
    """
    for reason in quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA):
        if reason.startswith("Action required: "):
            player_data.setdefault("quest_stage_actions", {}).setdefault(quest_id, []).append(
                reason[len("Action required: ") :]
            )


class TestSingleValuedRoutesAreRecordedSteps(unittest.TestCase):
    """Owner ruling 4.17.1: a one-value required_routes gate is a recorded auto-step.

    Each case starts its quest normally and drives apply_quest_progress_pure through the
    converted stage without ever touching quest_route_states, then asserts the route's
    sourced text was recorded by the kernel.
    """

    def _drive_through_converted_stage(self, quest_id, target_stage, prerequisite_ids):
        player_data = _player_with_prerequisites(prerequisite_ids)
        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok, f"{quest_id} should start normally")

        guard = 0
        while player_data["quests"][quest_id]["progress"] < target_stage - 1 and guard < 15:
            _record_required_actions(player_data, quest_id)
            player_data, ok, _ = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
            self.assertTrue(ok, f"{quest_id} should pass stage {guard + 1}")
            guard += 1

        # The converted stage must present no route blocker at all.
        reasons = quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
        self.assertEqual(
            tuple(reason for reason in reasons if reason.startswith("Route required")),
            (),
            f"{quest_id} stage {target_stage} still gates on a route",
        )

        _record_required_actions(player_data, quest_id)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
            f"{quest_id} stage {target_stage} should clear after its real steps",
        )
        return player_data

    def test_mournings_end_part_i_reach_lletya_is_a_recorded_step(self):
        player_data = self._drive_through_converted_stage(
            "mournings_end_part_i",
            1,
            [
                "roving_elves",
                "regicide",
                "underground_pass",
                "biohazard",
                "plague_city",
                "waterfall_quest",
                "sheep_herder",
                "big_chompy_bird_hunting",
            ],
        )
        player_data, ok, _ = apply_quest_progress_pure(player_data, "mournings_end_part_i", QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn("Reach Lletya", player_data["quest_stage_actions"]["mournings_end_part_i"])

    def test_death_to_the_dorgeshuun_reach_tears_cavern_is_a_recorded_step(self):
        quest_id = "death_to_the_dorgeshuun"
        player_data = _player_with_prerequisites(["the_lost_tribe"])
        player_data["quest_combat_encounters"] = {quest_id: ["death_to_the_dorgeshuun_sigmund_50"]}
        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)

        guard = 0
        while player_data["quests"][quest_id]["progress"] < 5 and guard < 15:
            _record_required_actions(player_data, quest_id)
            if quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA):
                break
            player_data, ok, _ = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
            self.assertTrue(ok)
            guard += 1

        # Stage 5 itself carries no route blocker any more.
        reasons = quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
        self.assertEqual(
            tuple(reason for reason in reasons if reason.startswith("Route required")),
            (),
        )

        for _ in range(3):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                quest_id,
                QUEST_DATA,
                rng=lambda: 0.9,
                equipment_data=EQUIPMENT_DATA,
            )
            if not ok:
                break
        player_data, ok, _ = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn(
            "Reach the Tears of Guthix cavern",
            player_data["quest_stage_actions"][quest_id],
        )

    def test_enlightened_journey_reach_auguste_is_a_recorded_step(self):
        player_data = self._drive_through_converted_stage("enlightened_journey", 1, [])
        player_data, ok, _ = apply_quest_progress_pure(player_data, "enlightened_journey", QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn(
            "Reach Auguste on Entrana", player_data["quest_stage_actions"]["enlightened_journey"]
        )

    def test_making_history_travel_legs_are_a_recorded_step(self):
        player_data = self._drive_through_converted_stage(
            "making_history", 1, ["the_restless_ghost"]
        )
        player_data, ok, _ = apply_quest_progress_pure(player_data, "making_history", QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn(
            "Reach the Outpost, Rellekka, and Port Phasmatys travel legs",
            player_data["quest_stage_actions"]["making_history"],
        )

    def test_cabin_fever_charter_route_is_a_recorded_step(self):
        player_data = self._drive_through_converted_stage(
            "cabin_fever", 1, ["pirates_treasure", "rum_deal"]
        )
        player_data, ok, _ = apply_quest_progress_pure(player_data, "cabin_fever", QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn(
            "Reach the Port Phasmatys charter route",
            player_data["quest_stage_actions"]["cabin_fever"],
        )

    def test_in_pyre_need_phoenix_lair_is_a_recorded_step(self):
        player_data = self._drive_through_converted_stage("in_pyre_need", 1, [])
        player_data, ok, _ = apply_quest_progress_pure(player_data, "in_pyre_need", QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn("Reach the Phoenix lair", player_data["quest_stage_actions"]["in_pyre_need"])

    def test_back_to_my_roots_karamja_route_is_a_recorded_step(self):
        player_data = self._drive_through_converted_stage(
            "back_to_my_roots", 1, ["the_hand_in_the_sand", "tribal_totem"]
        )
        player_data, ok, _ = apply_quest_progress_pure(player_data, "back_to_my_roots", QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn(
            "Reach the Karamja jungle route",
            player_data["quest_stage_actions"]["back_to_my_roots"],
        )

    def test_rocking_out_customs_office_is_a_recorded_step(self):
        player_data = self._drive_through_converted_stage(
            "rocking_out",
            1,
            [
                "the_great_brain_robbery",
                "creature_of_fenkenstrain",
                "the_restless_ghost",
                "cabin_fever",
                "pirates_treasure",
                "rum_deal",
                "recipe_for_disaster_freeing_pirate_pete",
                "recipe_for_disaster_another_cooks_quest",
                "cooks_assistant",
            ],
        )
        player_data, ok, _ = apply_quest_progress_pure(player_data, "rocking_out", QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn(
            "Reach the Rimmington customs office",
            player_data["quest_stage_actions"]["rocking_out"],
        )

    def test_glorious_memories_rellekka_miscellania_is_a_recorded_step(self):
        player_data = self._drive_through_converted_stage(
            "glorious_memories",
            1,
            [
                "mountain_daughter",
                "the_fremennik_isles",
                "the_fremennik_trials",
                "royal_trouble",
                "throne_of_miscellania",
            ],
        )
        player_data, ok, _ = apply_quest_progress_pure(player_data, "glorious_memories", QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn(
            "Reach Rellekka and Miscellania",
            player_data["quest_stage_actions"]["glorious_memories"],
        )

    def test_tale_of_the_muspah_all_three_route_legs_are_recorded_steps(self):
        quest_id = "the_tale_of_the_muspah"
        player_data = self._drive_through_converted_stage(quest_id, 1, [])

        for expected_text in (
            "Reach the Muspah cave route through Rellekka and Pollnivneach",
            "Reach Rellekka",
            "Reach Pollnivneach",
        ):
            player_data, ok, _ = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
            self.assertTrue(ok)
            self.assertIn(expected_text, player_data["quest_stage_actions"][quest_id])
        self.assertEqual(player_data["quests"][quest_id]["progress"], 4)

    def test_within_the_light_temple_route_is_a_recorded_step(self):
        player_data = self._drive_through_converted_stage(
            "within_the_light",
            1,
            [
                "mournings_end_part_ii",
                "mournings_end_part_i",
                "roving_elves",
                "regicide",
                "underground_pass",
                "biohazard",
                "plague_city",
                "waterfall_quest",
                "sheep_herder",
                "big_chompy_bird_hunting",
            ],
        )
        player_data, ok, _ = apply_quest_progress_pure(player_data, "within_the_light", QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn(
            "Reach the Temple of Light through West Ardougne and Lletya",
            player_data["quest_stage_actions"]["within_the_light"],
        )


if __name__ == "__main__":
    unittest.main()
