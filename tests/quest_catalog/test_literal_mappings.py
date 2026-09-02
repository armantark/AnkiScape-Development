import ast
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data import quest_data


_LITERAL_QUEST_ID_MAPPING_NAMES = (
    "QUEST_CHOICE_REPLACEMENTS_BY_ID",
    "QUEST_REQUIRED_QUEST_REPLACEMENTS_BY_ID",
    "QUEST_REQUIRED_SKILL_REPLACEMENTS_BY_ID",
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
