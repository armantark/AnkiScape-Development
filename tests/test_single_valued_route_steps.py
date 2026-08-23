import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure import (
    _mark_quest_stage_actions,
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    quest_current_stage_blockers_pure,
    quest_current_stage_pure,
    start_quest_pure,
)

_ALL_SKILLS = (
    "agility",
    "attack",
    "constitution",
    "construction",
    "cooking",
    "crafting",
    "defense",
    "farming",
    "firemaking",
    "fishing",
    "fletching",
    "herblore",
    "hunter",
    "magic",
    "mining",
    "prayer",
    "ranged",
    "runecrafting",
    "slayer",
    "smithing",
    "strength",
    "thieving",
    "woodcutting",
)


def _stage_rows(quest_id, stage):
    return tuple(
        requirement
        for requirement in QUEST_DATA[quest_id]["stage_requirements"]
        if requirement["stage"] == stage and not requirement.get("variant")
    )


def _player_ready_through_stage(quest_id, target_stage):
    player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for skill_id in _ALL_SKILLS:
        player_data[f"{skill_id}_level"] = 200
    player_data["quest_points"] = 200
    for requirement in QUEST_DATA[quest_id].get("required_quests", ()):
        prerequisite_id = requirement["quest_id"]
        player_data["quests"][prerequisite_id] = {"started": True, "progress": 999, "completed": True}

    inventory = player_data["inventory"]
    for requirement in QUEST_DATA[quest_id]["stage_requirements"]:
        if requirement["stage"] > target_stage:
            continue
        for field in ("required_inventory", "consumed_inventory", "required_tools"):
            for item_name, amount in requirement.get(field, {}).items():
                inventory[item_name] = max(inventory.get(item_name, 0), amount * 20)
        for field in ("required_inventory_options", "consumed_inventory_options"):
            for options in requirement.get(field, ()):
                for option in options:
                    for item_name, amount in option.items():
                        inventory[item_name] = max(inventory.get(item_name, 0), amount * 20)
    inventory["Coins"] = max(inventory.get("Coins", 0), 1_000_000)
    player_data["quest_combat_config"] = {"resolver_enabled": True}
    return player_data


class TestSingleValuedRoutesAreRecordedSteps(unittest.TestCase):
    def _drive_route_stages(self, quest_id, expected_by_stage):
        target_stage = max(expected_by_stage)
        player_data = _player_ready_through_stage(quest_id, target_stage)
        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok, f"{quest_id} should start normally")
        self.assertEqual(player_data["quest_stage_actions"], {})
        self.assertEqual(player_data["quest_route_states"], {})

        while player_data["quests"][quest_id]["progress"] <= target_stage:
            stage = quest_current_stage_pure(player_data, quest_id, QUEST_DATA)
            rows = _stage_rows(quest_id, stage)
            if stage in expected_by_stage:
                self.assertTrue(rows, f"{quest_id} stage {stage} should have requirements")
                route_blockers = tuple(
                    blocker
                    for blocker in quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
                    if blocker["kind"] == "required_route"
                )
                self.assertEqual(route_blockers, (), f"{quest_id} stage {stage} still requires a route choice")

            for requirement in rows:
                _mark_quest_stage_actions(player_data, quest_id, requirement.get("required_actions", ()))

            guard = 0
            while guard < 20:
                combat_blockers = tuple(
                    blocker
                    for blocker in quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
                    if blocker["kind"] == "combat_encounter"
                )
                if not combat_blockers:
                    break
                player_data, ok, result = apply_quest_combat_encounter_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                    combat_blockers[0]["encounter_id"],
                    rng=lambda: 0.0,
                    equipment_data=EQUIPMENT_DATA,
                )
                self.assertTrue(ok, f"{quest_id} stage {stage} combat should resolve: {result}")
                guard += 1
            self.assertLess(guard, 20, f"{quest_id} stage {stage} combat should terminate")

            blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
            self.assertEqual(blockers, (), f"{quest_id} stage {stage} should be ready: {blockers}")
            player_data, ok, _ = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
            self.assertTrue(ok, f"{quest_id} stage {stage} should progress")
            for expected_text in expected_by_stage.get(stage, ()):
                self.assertIn(expected_text, player_data["quest_stage_actions"][quest_id])

        self.assertNotIn(quest_id, player_data.get("quest_route_states", {}))

    def test_kenniths_concerns_shrine_tunnels_are_recorded(self):
        self._drive_route_stages(
            "kenniths_concerns",
            {1: ("Reach the Witchaven shrine tunnels",)},
        )

    def test_lost_city_entrana_travel_is_recorded(self):
        self._drive_route_stages(
            "lost_city",
            {2: ("Reach Entrana without combat gear",)},
        )

    def test_merlins_crystal_crate_delivery_is_recorded(self):
        self._drive_route_stages(
            "merlins_crystal",
            {2: ("Reach Keep Le Faye through the Catherby crate delivery",)},
        )

    def test_heroes_quest_travel_steps_are_recorded(self):
        self._drive_route_stages(
            "heroes_quest",
            {
                5: ("Reach a lava eel fishing spot in Taverley Dungeon or the Lava Maze",),
                7: ("Reach the Ice Queen lair through a Dusty key or Agility shortcut route",),
                8: ("Reach Entrana without prohibited combat equipment",),
            },
        )

    def test_family_crest_dungeon_routes_are_recorded(self):
        self._drive_route_stages(
            "family_crest",
            {
                8: ("Reach the Witchaven perfect gold mine",),
                13: ("Reach Chronozon's lair in Edgeville Dungeon",),
            },
        )

    def test_temple_of_ikov_travel_steps_are_recorded(self):
        self._drive_route_stages(
            "temple_of_ikov",
            {
                1: ("Enter the Temple of Ikov",),
                3: ("Cross the Temple of Ikov lava bridge at low weight",),
            },
        )

    def test_witchs_house_patrol_avoidance_is_recorded(self):
        self._drive_route_stages(
            "witchs_house",
            {5: ("Avoid the witch's patrol through the house",)},
        )

    def test_myths_of_the_white_lands_ice_cave_route_is_recorded(self):
        self._drive_route_stages(
            "myths_of_the_white_lands",
            {1: ("Reach the Wizard's Tower ice cave",)},
        )


if __name__ == "__main__":
    unittest.main()
