import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "tools" / "fetch_2012_icons.py"
FIXTURE_PATH = Path(__file__).with_name("fetch_2012_icons_history_fixture.json")
SPEC = importlib.util.spec_from_file_location("fetch_2012_icons_tool", TOOL_PATH)
fetch_2012_icons = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["fetch_2012_icons_tool"] = fetch_2012_icons
SPEC.loader.exec_module(fetch_2012_icons)


class Fetch2012IconsTest(unittest.TestCase):
    def test_selects_newest_revision_strictly_before_cutoff(self):
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        selected = fetch_2012_icons.select_newest_revision(fixture["mixed"])

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected["sha1"], "newest-before-cutoff")
        self.assertIsNone(
            fetch_2012_icons.select_newest_revision(fixture["at_or_after"])
        )


if __name__ == "__main__":
    unittest.main()
