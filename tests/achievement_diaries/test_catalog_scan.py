import ast
import json
import tempfile
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from tools.generate_achievement_diary_data import (
    FAMILIES,
    MORYTANIA_LEG_BONUSES,
    build,
)


ROOT = Path(__file__).resolve().parents[2]


def synthetic_items_yml():
    blocks = []
    expected_ids = {}
    source_id = 50_000
    for family in FAMILIES.values():
        for tier_index in range(1, 5):
            item_name = f"{family['item']} {tier_index}"
            if item_name in MORYTANIA_LEG_BONUSES:
                continue
            expected_ids[item_name] = (source_id, tier_index)
            blocks.append(
                f'- id: {source_id}\n  name: "{item_name}"\n'
                f"  equip_slot: 4\n  attack_stab: {tier_index}\n"
            )
            source_id += 1
    return "".join(blocks), expected_ids


def _task_rows(module_sources):
    rows = {}
    duplicates = []
    for module_source in module_sources:
        for node in ast.walk(ast.parse(module_source)):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "DiaryTask"
            ):
                continue
            source_id = ast.literal_eval(node.args[5])
            if source_id in rows:
                duplicates.append(source_id)
            rows[source_id] = ast.dump(node, include_attributes=False)
    return rows, duplicates


class AchievementDiaryCatalogScanTest(unittest.TestCase):
    def test_generator_reproduces_every_shipped_task_row(self):
        harvest = (
            ROOT
            / "memory-bank/source-audits"
            / "achievement-diary-harvest-2026-07-26.json"
        )
        document = json.loads(harvest.read_text(encoding="utf-8"))
        items_yml, _expected_ids = synthetic_items_yml()
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "items.yml"
            source.write_text(items_yml, encoding="utf-8")
            generated = build(document, source)

        generated_rows, generated_duplicates = _task_rows(generated.values())
        shipped_rows, shipped_duplicates = _task_rows(
            source_file.read_text(encoding="utf-8")
            for source_file in sorted(
                (ROOT / "data/achievement_diaries").glob("*.py")
            )
        )
        self.assertTrue(generated_rows)
        self.assertTrue(shipped_rows)
        self.assertEqual(len(generated_rows), 474)
        self.assertEqual(generated_duplicates, [])
        self.assertEqual(shipped_duplicates, [])
        self.assertEqual(set(shipped_rows), set(generated_rows))
        self.assertEqual(
            [
                source_id
                for source_id in sorted(generated_rows)
                if generated_rows[source_id] != shipped_rows[source_id]
            ],
            [],
        )


if __name__ == "__main__":
    unittest.main()
