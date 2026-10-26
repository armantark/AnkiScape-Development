import copy
import unittest

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.skill_registry import get_skill
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest.catalog import _quest_from_catalog
from ankiscape.data.quest.contract import QuestPrerequisite
from ankiscape.data.quest_data import quests_as_dict
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure,
    can_start_quest_pure,
    player_combat_level_pure,
    quest_locked_reasons_pure,
    quest_state_pure,
    start_quest_pure,
)


QUEST_ID = "legends_quest"
PREREQUISITES = (
    ("family_crest", "Family Crest"),
    ("heroes_quest", "Heroes' Quest"),
    ("shilo_village", "Shilo Village"),
    ("underground_pass", "Underground Pass"),
    ("waterfall_quest", "Waterfall Quest"),
)
REQUIREMENTS = (
    "108 quest points",
    "Family Crest",
    "Heroes' Quest",
    "Shilo Village",
    "Underground Pass",
    "Waterfall Quest",
    "Agility 50",
    "Crafting 50",
    "Herblore 45",
    "Magic 56",
    "Mining 52",
    "Prayer 42",
    "Smithing 50",
    "Strength 50",
    "Thieving 50",
    "Woodcutting 50",
)


def _ready_legends_player(attack_level=70):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    # Isolate start eligibility; prerequisite acquisition is outside this fixture.
    for quest_id, _name in PREREQUISITES:
        player["quests"][quest_id] = {
            "started": True,
            "progress": QUEST_DATA[quest_id]["stages"],
            "completed": True,
        }
    for requirement in QUEST_DATA[QUEST_ID]["required_skills"]:
        if requirement["skill_id"] != "combat":
            skill = get_skill(requirement["skill_id"])
            player[skill.level_key] = requirement["level"]
    player.update(
        attack_level=attack_level, defense_level=60, constitution_level=60,
        strength_level=50, prayer_level=42, magic_level=56, ranged_level=1, summoning_level=1,
    )
    player["quest_points"] = 108
    return player


class TestQuestRootPrerequisites(unittest.TestCase):
    def test_legends_catalog_prerequisites_and_readout(self):
        before = copy.deepcopy(PRE_EOC_QUEST_CATALOG)
        raw = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)

        definition = _quest_from_catalog(raw)
        quest = QUEST_DATA[QUEST_ID]

        self.assertEqual(
            definition.required_quests,
            tuple(QuestPrerequisite(quest_id, name) for quest_id, name in PREREQUISITES),
        )
        self.assertEqual(
            quest["required_quests"],
            tuple({"quest_id": quest_id, "display_name": name} for quest_id, name in PREREQUISITES),
        )
        self.assertEqual(definition.required_quest_points, 108)
        self.assertEqual(quest["required_quest_points"], 108)
        self.assertEqual(definition.requirements, REQUIREMENTS)
        self.assertEqual(quest["requirements"], REQUIREMENTS)
        self.assertNotIn("Regicide", quest["requirements"])
        self.assertNotIn("regicide", tuple(req.quest_id for req in definition.required_quests))
        expected_skills = tuple(
            dict(req, level=42) if req["skill_id"] == "prayer" else dict(req)
            for req in raw["required_skills"]
            if req["skill_id"] != "combat"
        )
        self.assertEqual(
            next(req["level"] for req in raw["required_skills"] if req["skill_id"] == "combat"),
            75,
        )
        self.assertEqual(
            next(req["level"] for req in raw["required_skills"] if req["skill_id"] == "prayer"),
            43,
        )
        self.assertEqual(quest["required_skills"], expected_skills)
        self.assertEqual(
            tuple((req.skill_id, req.display_name, req.level) for req in definition.required_skills),
            tuple((req["skill_id"], req["display_name"], req["level"]) for req in expected_skills),
        )
        self.assertEqual(
            definition.source,
            raw["source"]
            + "; https://runescape.wiki/w/index.php?title=Template%3AQuestreq&oldid=6552449"
            + "; https://web.archive.org/web/20121018050049id_/http://runescape.salmoneus.net/quests/legends-quest.html"
            + "; " + raw["release_source"],
        )
        self.assertEqual(_quest_from_catalog(raw), definition)
        self.assertEqual(quests_as_dict()[QUEST_ID], quest)
        self.assertEqual(PRE_EOC_QUEST_CATALOG, before)

    def test_legends_combat_prayer_boundaries_and_start_nonmutation(self):
        for level in (41, 42, 43):
            for combat, attack in ((74, 70), (75, 73), (76, 76)):
                with self.subTest(prayer_level=level, combat=combat):
                    # Synthetic combat boundaries; Prayer 41 needs one extra Attack level.
                    player = _ready_legends_player(attack_level=attack + int(level == 41))
                    player["prayer_level"] = level
                    before = copy.deepcopy(player)
                    self.assertEqual(player_combat_level_pure(player), combat)
                    self.assertEqual(QUEST_DATA[QUEST_ID]["requirements"], REQUIREMENTS)
                    self.assertEqual(
                        quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA),
                        ("Prayer 42",) if level == 41 else (),
                    )
                    self.assertEqual(can_start_quest_pure(player, QUEST_ID, QUEST_DATA), level >= 42)
                    self.assertEqual(player, before)

                    result, started = start_quest_pure(player, QUEST_ID, QUEST_DATA)

                    self.assertEqual(started, level >= 42)
                    expected = copy.deepcopy(before)
                    if level == 41:
                        self.assertIs(result, player)
                    else:
                        expected["quests"][QUEST_ID] = {
                            "started": True, "progress": 0, "completed": False,
                        }
                        expected["current_quest"] = QUEST_ID
                    self.assertEqual(result, expected)
                    self.assertEqual(player, before)

    def test_legends_quest_point_boundary(self):
        for points in (107, 108, 109):
            with self.subTest(points=points):
                player = _ready_legends_player()
                player["quest_points"] = points
                before = copy.deepcopy(player)
                self.assertFalse(quest_state_pure(player, "regicide")["started"])
                self.assertEqual(player_combat_level_pure(player), 74)
                expected_reasons = ("108 quest points",) if points == 107 else ()
                self.assertEqual(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA), expected_reasons)
                self.assertEqual(can_start_quest_pure(player, QUEST_ID, QUEST_DATA), points >= 108)
                self.assertEqual(player, before)

                result, started = start_quest_pure(player, QUEST_ID, QUEST_DATA)

                self.assertEqual(started, points >= 108)
                expected = copy.deepcopy(before)
                if points == 107:
                    self.assertIs(result, player)
                else:
                    expected["quests"][QUEST_ID] = {
                        "started": True, "progress": 0, "completed": False,
                    }
                    expected["current_quest"] = QUEST_ID
                self.assertEqual(result, expected)
                self.assertEqual(player, before)

    def test_each_legends_prerequisite_is_required(self):
        for quest_id, name in PREREQUISITES:
            for started in (False, True):
                with self.subTest(quest=quest_id, started=started):
                    player = _ready_legends_player()
                    player["quests"][quest_id] = {
                        "started": started,
                        "progress": 1 if started else 0,
                        "completed": False,
                    }
                    before = copy.deepcopy(player)
                    self.assertEqual(player_combat_level_pure(player), 74)
                    for other_id, _other_name in PREREQUISITES:
                        if other_id != quest_id:
                            self.assertTrue(player["quests"][other_id]["completed"])
                    self.assertEqual(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA), (name,))
                    self.assertFalse(can_start_quest_pure(player, QUEST_ID, QUEST_DATA))
                    self.assertEqual(player, before)
                    result, accepted = start_quest_pure(player, QUEST_ID, QUEST_DATA)
                    self.assertFalse(accepted)
                    self.assertIs(result, player)
                    self.assertEqual(result, before)
                    self.assertEqual(player, before)

    def test_regicide_cannot_replace_the_five_prerequisites(self):
        for missing in (*PREREQUISITES, None):
            with self.subTest(missing=missing):
                player = _ready_legends_player()
                if missing is None:
                    for quest_id, _name in PREREQUISITES:
                        del player["quests"][quest_id]
                    reasons = tuple(name for _quest_id, name in PREREQUISITES)
                else:
                    quest_id, name = missing
                    player["quests"][quest_id] = {
                        "started": False, "progress": 0, "completed": False,
                    }
                    reasons = (name,)
                player["quests"]["regicide"] = {
                    "started": True,
                    "progress": QUEST_DATA["regicide"]["stages"],
                    "completed": True,
                }
                before = copy.deepcopy(player)
                self.assertEqual(player_combat_level_pure(player), 74)
                self.assertEqual(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA), reasons)
                self.assertFalse(can_start_quest_pure(player, QUEST_ID, QUEST_DATA))
                self.assertEqual(player, before)
                result, started = start_quest_pure(player, QUEST_ID, QUEST_DATA)
                self.assertFalse(started)
                self.assertIs(result, player)
                self.assertEqual(result, before)
                self.assertEqual(player, before)

    def test_legends_start_refusal_is_non_mutating(self):
        cases = [("points", False)] + [
            (quest_id, started) for quest_id, _name in PREREQUISITES for started in (False, True)
        ]
        for missing, started in cases:
            with self.subTest(missing=missing, started=started):
                player = _ready_legends_player()
                if missing == "points":
                    player["quest_points"] = 107
                else:
                    player["quests"][missing].update(started=started, progress=int(started), completed=False)
                before = copy.deepcopy(player)

                result, accepted = start_quest_pure(player, QUEST_ID, QUEST_DATA)

                self.assertFalse(accepted)
                self.assertEqual(result, before)
                self.assertEqual(player, before)

    def test_existing_legends_progress_is_preserved(self):
        for completed in (False, True):
            with self.subTest(completed=completed):
                player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                player["quests"][QUEST_ID] = {
                    "started": True,
                    "progress": QUEST_DATA[QUEST_ID]["stages"] if completed else 4,
                    "completed": completed,
                }
                player["prayer_level"] = 41
                before = copy.deepcopy(player)
                self.assertEqual(can_start_quest_pure(player, QUEST_ID, QUEST_DATA), not completed)
                self.assertEqual(
                    quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA),
                    ("completed",) if completed else (),
                )

                result, selected = start_quest_pure(player, QUEST_ID, QUEST_DATA)

                self.assertEqual(selected, not completed)
                self.assertEqual(result["quests"], before["quests"])
                expected = copy.deepcopy(before)
                if not completed:
                    expected["current_quest"] = QUEST_ID
                self.assertEqual(result, expected)
                self.assertEqual(player, before)
                if completed:
                    result, progressed, completed_now = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
                    self.assertFalse(progressed)
                    self.assertFalse(completed_now)
                    self.assertEqual(result, before)
                    self.assertEqual(player, before)


if __name__ == "__main__":
    unittest.main()
