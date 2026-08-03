from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "query_openrs2_cache_configs.sh"
DEFAULT_CACHE = (
    Path.home()
    / "Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache"
)
CACHE = Path(os.environ.get("ANKISCAPE_OPENRS2_CACHE_727", DEFAULT_CACHE))
JAVA = Path(os.environ.get("JAVA_BIN", "/opt/homebrew/opt/openjdk@25/bin/java"))
CORE = Path.home() / ".gradle/caches/modules-2/files-2.1/rs.darkan/core/2.0.5"


@unittest.skipUnless(
    CACHE.joinpath("main_file_cache.dat2").is_file() and JAVA.is_file() and CORE.is_dir(),
    "local rev-727 cache and Darkan Java runtime required",
)
class OpenRs2CacheConfigQueryTest(unittest.TestCase):
    def _run(self, *args: str) -> str:
        result = subprocess.run(
            [str(TOOL), str(CACHE), *args],
            check=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout

    def test_real_cache_exposes_all_three_definition_families(self):
        expected = {
            "enum": (6048, 0, 6047),
            "struct": (11389, 0, 11388),
            "param": (2583, 0, 2582),
        }
        for kind, counts in expected.items():
            output = self._run(kind, "count")
            match = re.fullmatch(
                rf"kind={kind} index=\d+ definitions=(\d+) firstId=(\d+) lastId=(\d+)\n",
                output,
            )
            self.assertIsNotNone(match, output)
            self.assertEqual(tuple(map(int, match.groups())), counts)

    def test_period_achievement_enum_decodes_deterministically(self):
        first = self._run("enum", "dump", "3483")
        second = self._run("enum", "dump", "3483")
        self.assertEqual(first, second)
        self.assertIn("==== enum 3483", first)
        self.assertIn(
            'keyType=i valueType=J defaultInt=1645 defaultString="null" entries=1096',
            first,
        )
        self.assertIn("0\t1592\n", first)

    def test_first_struct_and_param_decode_without_unknown_opcodes(self):
        self.assertEqual(
            self._run("struct", "dump", "0"),
            "==== struct 0\nentries=4\n130\t1804\n131\t1807\n134\t1805\n135\t1806\n",
        )
        self.assertEqual(
            self._run("param", "dump", "0"),
            "==== param 0\ntype=i defaultInt=0 defaultString=null autoDisable=true\n",
        )


if __name__ == "__main__":
    unittest.main()
