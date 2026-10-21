import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data import quest_data


ROOT = Path(__file__).resolve().parents[2]
EXPORT_ORDER_SHA256 = "c18f570c66aca04f5d57de8f1e8770e2904fb67d72340af46eeb5fa74fca4160"


class TestQuestSplitContract(unittest.TestCase):
    def test_reward_item_metadata_is_owned_by_each_projection(self):
        first = quest_data.quest_reward_items_as_dict()
        second = quest_data.quest_reward_items_as_dict()
        self.assertTrue(first)
        self.assertEqual(first, second)
        expected = copy.deepcopy(second)
        for name, metadata in first.items():
            with self.subTest(item=name):
                self.assertIsNot(metadata, second[name])
        for metadata in first.values():
            metadata["source"] = "Changed by the projection's caller"
        self.assertEqual(quest_data.quest_reward_items_as_dict(), expected)

    def test_every_quest_part_imports_without_loading_the_facade(self):
        module_names = []
        for path in sorted((ROOT / "data" / "quest").rglob("*.py")):
            parts = path.relative_to(ROOT).with_suffix("").parts
            if parts[-1] == "__init__":
                parts = parts[:-1]
            module_names.append("ankiscape." + ".".join(parts))
        self.assertTrue(module_names)
        self.assertEqual(len(module_names), len(set(module_names)))
        script = "\n".join(
            (
                "import importlib, sys",
                "import pkg_alias",
                "importlib.import_module(sys.argv[1])",
                "assert 'ankiscape.data.quest_data' not in sys.modules",
                "print('OK')",
            )
        )
        for module_name in module_names:
            with self.subTest(module=module_name):
                result = subprocess.run(
                    [sys.executable, "-c", script, module_name],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "OK\n")

    def test_public_exports_preserve_names_and_original_order(self):
        names = quest_data.__all__
        missing = [name for name in names if not hasattr(quest_data, name)]
        extra = sorted(
            name
            for name in vars(quest_data)
            if not name.startswith("_") and name not in names
        )
        self.assertEqual(missing, [])
        self.assertEqual(extra, [])
        payload = json.dumps(names, ensure_ascii=False, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), EXPORT_ORDER_SHA256)


if __name__ == "__main__":
    unittest.main()
