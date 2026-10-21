import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest_data import QUEST_OVERRIDES_BY_ID, quests_as_dict
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
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
    "desert_treasure": (
        (("agility", 15), ("firemaking", 50), ("magic", 50), ("slayer", 10), ("thieving", 53)),
        ("mining",),
        (
            "The Dig Site", "The Tourist Trap", "Temple of Ikov", "Priest in Peril",
            "Troll Stronghold", "Death Plateau", "Waterfall Quest", "Agility 15",
            "Firemaking 50", "Magic 50", "Slayer 10", "Thieving 53",
        ),
    ),
    "one_small_favour": (
        (("agility", 36), ("crafting", 25), ("herblore", 18), ("smithing", 30)),
        (),
        (
            "Shilo Village", "Jungle Potion", "Rune Mysteries", "Agility 36",
            "Crafting 25", "Herblore 18", "Smithing 30",
        ),
    ),
    "defender_of_varrock": (
        (("agility", 51), ("hunter", 51), ("mining", 59), ("smithing", 54)),
        (),
        (
            "Shield of Arrav", "The Knight's Sword", "Family Crest", "What Lies Below",
            "Demon Slayer", "Temple of Ikov", "Garden of Tranquillity", "Agility 51",
            "Hunter 51", "Mining 59", "Smithing 54",
        ),
    ),
    "recruitment_drive": (
        (),
        (),
        ("Black Knights' Fortress", "Druidic Ritual"),
    ),
}

PERIOD_QUEST_PREREQUISITES = {
    "desert_treasure": (
        ("the_dig_site", "The Dig Site"),
        ("the_tourist_trap", "The Tourist Trap"),
        ("temple_of_ikov", "Temple of Ikov"),
        ("priest_in_peril", "Priest in Peril"),
        ("troll_stronghold", "Troll Stronghold"),
        ("death_plateau", "Death Plateau"),
        ("waterfall_quest", "Waterfall Quest"),
    ),
    "one_small_favour": (
        ("shilo_village", "Shilo Village"),
        ("jungle_potion", "Jungle Potion"),
        ("rune_mysteries", "Rune Mysteries"),
    ),
    "defender_of_varrock": (
        ("shield_of_arrav", "Shield of Arrav"),
        ("the_knights_sword", "The Knight's Sword"),
        ("family_crest", "Family Crest"),
        ("what_lies_below", "What Lies Below"),
        ("demon_slayer", "Demon Slayer"),
        ("temple_of_ikov", "Temple of Ikov"),
        ("garden_of_tranquillity", "Garden of Tranquillity"),
    ),
    "recruitment_drive": (
        ("black_knights_fortress", "Black Knights' Fortress"),
        ("druidic_ritual", "Druidic Ritual"),
    ),
}


def _player_ready_to_start(quest_id):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    kept_skills, removed_skills, _ = PERIOD_START_GATES[quest_id]
    for skill_id, level in kept_skills:
        player[f"{skill_id}_level"] = level
    for skill_id in removed_skills:
        player[f"{skill_id}_level"] = 1
    required_ids = (
        tuple(required_id for required_id, _ in PERIOD_QUEST_PREREQUISITES[quest_id])
        if quest_id in PERIOD_QUEST_PREREQUISITES
        else tuple(row["quest_id"] for row in QUEST_DATA[quest_id]["required_quests"])
    )
    for required_id in required_ids:
        player["quests"][required_id] = {
            "started": True,
            "progress": QUEST_DATA[required_id]["stages"],
            "completed": True,
        }
    return player


class TestPeriodStartGates(unittest.TestCase):
    def test_period_prerequisite_lists_match_source_order_and_names(self):
        for quest_id, expected in PERIOD_QUEST_PREREQUISITES.items():
            with self.subTest(quest_id=quest_id):
                self.assertEqual(
                    tuple(
                        (row["quest_id"], row["display_name"])
                        for row in QUEST_DATA[quest_id]["required_quests"]
                    ),
                    expected,
                )

    def test_desert_treasure_can_start_with_mining_one(self):
        player = _player_ready_to_start("desert_treasure")
        self.assertEqual(player["mining_level"], 1)
        self.assertEqual(quest_locked_reasons_pure(player, "desert_treasure", QUEST_DATA), ())
        updated, started = start_quest_pure(player, "desert_treasure", QUEST_DATA)
        self.assertTrue(started)
        self.assertTrue(updated["quests"]["desert_treasure"]["started"])

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

    def test_prerequisite_quests_still_block_starting(self):
        prerequisites = {
            "horror_from_the_deep": ("bar_crawl",),
            "monkey_madness": ("the_grand_tree", "tree_gnome_village"),
            "enakhras_lament": (),
            "eadgars_ruse": ("druidic_ritual", "troll_stronghold", "death_plateau"),
            "nature_spirit": ("priest_in_peril", "the_restless_ghost"),
            **{
                quest_id: tuple(required_id for required_id, _ in rows)
                for quest_id, rows in PERIOD_QUEST_PREREQUISITES.items()
            },
        }
        for quest_id, required_ids in prerequisites.items():
            for required_id in required_ids:
                with self.subTest(quest_id=quest_id, prerequisite=required_id):
                    player = _player_ready_to_start(quest_id)
                    player["quests"].pop(required_id, None)
                    self.assertEqual(
                        quest_locked_reasons_pure(player, quest_id, QUEST_DATA),
                        (QUEST_DATA[required_id]["display_name"],),
                    )

                    updated, started = start_quest_pure(player, quest_id, QUEST_DATA)

                    self.assertFalse(started)
                    self.assertEqual(updated, player)

    def test_readout_lists_only_required_quests_and_levels(self):
        quests = quests_as_dict()
        for quest_id, (_, _, requirements) in PERIOD_START_GATES.items():
            with self.subTest(quest_id=quest_id):
                self.assertEqual(quests[quest_id]["requirements"], requirements)

    def test_other_generated_quest_readouts_keep_the_source_requirements(self):
        quests = quests_as_dict()
        for row in PRE_EOC_QUEST_CATALOG:
            quest_id = row["id"]
            if quest_id in PERIOD_START_GATES or quest_id in QUEST_OVERRIDES_BY_ID or quest_id == "legends_quest":
                continue
            with self.subTest(quest_id=quest_id):
                self.assertEqual(quests[quest_id]["requirements"], row["requirements"])


if __name__ == "__main__":
    unittest.main()
