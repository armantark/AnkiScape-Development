import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest_data import quests_as_dict
from ankiscape.logic_pure.logic_pure import quest_locked_reasons_pure, start_quest_pure


# Expected start gates and readouts from the period-source ruling R1.
PERIOD_START_GATES = {
    "horror_from_the_deep": (
        (("agility", 35),),
        ("prayer",),
        ("Alfred Grimhand's Barcrawl", "Agility 35"),
    ),
    "monkey_madness": (
        (),
        ("prayer", "thieving"),
        ("The Grand Tree", "Tree Gnome Village"),
    ),
    "enakhras_lament": (
        (("crafting", 50), ("firemaking", 45), ("magic", 39), ("prayer", 43)),
        ("mining",),
        ("Crafting 50", "Firemaking 45", "Magic 39", "Prayer 43"),
    ),
    "eadgars_ruse": (
        (("agility", 15), ("herblore", 31)),
        ("prayer",),
        ("Druidic Ritual", "Troll Stronghold", "Death Plateau", "Agility 15", "Herblore 31"),
    ),
    "nature_spirit": (
        (),
        ("crafting", "prayer"),
        ("Priest in Peril", "The Restless Ghost"),
    ),
}


def _player_ready_to_start(quest_id):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    kept_skills, removed_skills, _ = PERIOD_START_GATES[quest_id]
    for skill_id, level in kept_skills:
        player[f"{skill_id}_level"] = level
    for skill_id in removed_skills:
        player[f"{skill_id}_level"] = 1
    for prerequisite in QUEST_DATA[quest_id]["required_quests"]:
        required_id = prerequisite["quest_id"]
        player["quests"][required_id] = {
            "started": True,
            "progress": QUEST_DATA[required_id]["stages"],
            "completed": True,
        }
    return player


class TestPeriodStartGates(unittest.TestCase):
    def test_recommended_levels_do_not_block_starting(self):
        for quest_id in PERIOD_START_GATES:
            with self.subTest(quest_id=quest_id):
                player = _player_ready_to_start(quest_id)
                self.assertEqual(quest_locked_reasons_pure(player, quest_id, QUEST_DATA), ())

                updated, started = start_quest_pure(player, quest_id, QUEST_DATA)

                self.assertTrue(started)
                self.assertTrue(updated["quests"][quest_id]["started"])
                self.assertEqual(updated["current_quest"], quest_id)
                self.assertFalse(player["quests"][quest_id]["started"])

    def test_retained_skill_gates_still_block_starting(self):
        for quest_id, (kept_skills, _, _) in PERIOD_START_GATES.items():
            for skill_id, level in kept_skills:
                with self.subTest(quest_id=quest_id, skill_id=skill_id):
                    player = _player_ready_to_start(quest_id)
                    player[f"{skill_id}_level"] = level - 1
                    self.assertEqual(
                        quest_locked_reasons_pure(player, quest_id, QUEST_DATA),
                        (f"{skill_id.title()} {level}",),
                    )

                    updated, started = start_quest_pure(player, quest_id, QUEST_DATA)

                    self.assertFalse(started)
                    self.assertEqual(updated, player)

    def test_start_skill_requirements_match_retained_gates(self):
        for quest_id, (kept_skills, _, _) in PERIOD_START_GATES.items():
            with self.subTest(quest_id=quest_id):
                self.assertEqual(
                    tuple(
                        (requirement["skill_id"], requirement["level"])
                        for requirement in QUEST_DATA[quest_id]["required_skills"]
                    ),
                    kept_skills,
                )

    def test_readout_lists_only_required_quests_and_levels(self):
        quests = quests_as_dict()
        for quest_id, (_, _, requirements) in PERIOD_START_GATES.items():
            with self.subTest(quest_id=quest_id):
                self.assertEqual(quests[quest_id]["requirements"], requirements)


if __name__ == "__main__":
    unittest.main()
