import ast
import copy
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data import quest_data
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure import quest_locked_reasons_pure, start_quest_pure


_LITERAL_QUEST_ID_MAPPING_NAMES = (
    "QUEST_CHOICE_REPLACEMENTS_BY_ID",
    "QUEST_REQUIRED_QUEST_REPLACEMENTS_BY_ID",
    "QUEST_REQUIRED_SKILL_REPLACEMENTS_BY_ID",
    "QUEST_REQUIREMENT_TEXT_REPLACEMENTS_BY_ID",
    "QUEST_STAGE_COUNT_REPLACEMENTS_BY_ID",
    "QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID",
    "QUEST_COMBAT_TEXT_REPLACEMENTS_BY_ID",
    "QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID",
    "QUEST_UNLOCK_REPLACEMENTS_BY_ID",
    "QUEST_XP_REWARD_REPLACEMENTS_BY_ID",
    "QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID",
    "QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID",
    "QUEST_STAGE_REQUIREMENT_ADDITIONS_BY_ID",
    "QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID",
    "QUEST_COMBAT_ENCOUNTER_REPLACEMENTS_BY_ID",
)
_LITERAL_QUEST_ID_MAPPING_ALIASES = {
    "_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID": "QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID",
    "_QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID": "QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID",
}


def _literal_quest_id_mapping_keys(module, expected_names, string_constants):
    for node in module.body:
        if not isinstance(node, ast.AnnAssign) or not isinstance(node.value, ast.Dict):
            continue
        source_name = getattr(node.target, "id", "")
        mapping_name = _LITERAL_QUEST_ID_MAPPING_ALIASES.get(source_name, source_name)
        if mapping_name not in expected_names:
            continue
        yield mapping_name, (
            key.value
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
            else string_constants[key.id]
            for key in node.value.keys
        )


class TestLiteralQuestMappings(unittest.TestCase):
    def test_miniquests_preserve_their_player_facing_titles(self):
        self.assertEqual(
            {
                quest_id: quest["display_name"]
                for quest_id, quest in QUEST_DATA.items()
                if quest["miniquest"]
            },
            {
                "bar_crawl": "Alfred Grimhand's Barcrawl",
                "hunt_for_surok": "The Hunt for Surok",
                "lair_of_tarn_razorlor": "The Lair of Tarn Razorlor",
                "skippy_and_the_mogres": "Skippy and the Mogres",
            },
        )

    def test_ghosts_ahoy_requires_both_completed_prerequisites(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data.update(agility_level=25, cooking_level=20)
        for completed_ids, reasons in (
            ((), ("The Restless Ghost", "Priest in Peril")),
            (("the_restless_ghost",), ("Priest in Peril",)),
            (("priest_in_peril",), ("The Restless Ghost",)),
            (("the_restless_ghost", "priest_in_peril"), ()),
        ):
            with self.subTest(completed=completed_ids):
                player_data["quests"] = {
                    quest_id: {
                        "started": True,
                        "progress": QUEST_DATA[quest_id]["stages"],
                        "completed": quest_id in completed_ids,
                    }
                    for quest_id in ("the_restless_ghost", "priest_in_peril")
                }
                before = copy.deepcopy(player_data)
                self.assertEqual(
                    quest_locked_reasons_pure(player_data, "ghosts_ahoy", QUEST_DATA),
                    reasons,
                )
                updated, started = start_quest_pure(player_data, "ghosts_ahoy", QUEST_DATA)
                self.assertEqual(started, not reasons)
                self.assertEqual(player_data, before)
                if reasons:
                    self.assertEqual(updated, before)
                else:
                    self.assertTrue(updated["quests"]["ghosts_ahoy"]["started"])

    def test_do_no_evil_requires_monkey_madness(self):
        quest_id = "do_no_evil"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for requirement in QUEST_DATA[quest_id]["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        prerequisite_ids = (
            "garden_of_tranquillity",
            "creature_of_fenkenstrain",
            "monkey_madness",
        )
        player_data["quests"] = {
            prerequisite_id: {
                "started": True,
                "progress": QUEST_DATA[prerequisite_id]["stages"],
                "completed": prerequisite_id != "monkey_madness",
            }
            for prerequisite_id in prerequisite_ids
        }

        self.assertEqual(
            quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Monkey Madness",),
        )
        unchanged, started = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertFalse(started)
        self.assertEqual(unchanged, player_data)

        player_data["quests"]["monkey_madness"]["completed"] = True
        self.assertEqual(
            quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )
        updated, started = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(started)
        self.assertTrue(updated["quests"][quest_id]["started"])

    def test_literal_quest_id_mappings_have_no_resolved_duplicate_keys(self):
        expected_keys_by_name = {
            name: set(getattr(quest_data, name))
            for name in _LITERAL_QUEST_ID_MAPPING_NAMES
        }
        string_constants = {
            name: value
            for name, value in vars(quest_data).items()
            if isinstance(value, str)
        }
        literal_keys_by_name = {}
        data_root = Path(quest_data.__file__).parent
        for source_path in sorted(data_root.rglob("*.py")):
            module = ast.parse(source_path.read_text(), filename=str(source_path))
            for mapping_name, keys in _literal_quest_id_mapping_keys(
                module, expected_keys_by_name, string_constants
            ):
                literal_keys_by_name.setdefault(mapping_name, []).extend(keys)

        self.assertTrue(literal_keys_by_name)
        self.assertEqual(set(literal_keys_by_name), set(expected_keys_by_name))
        for mapping_name, expected_keys in expected_keys_by_name.items():
            resolved_keys = literal_keys_by_name[mapping_name]
            with self.subTest(mapping=mapping_name):
                self.assertTrue(resolved_keys)
                self.assertEqual(len(resolved_keys), len(set(resolved_keys)))
                self.assertEqual(set(resolved_keys), expected_keys)


if __name__ == "__main__":
    unittest.main()
