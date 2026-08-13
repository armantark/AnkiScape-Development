from __future__ import annotations

import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "query_openrs2_interfaces.sh"
DEFAULT_CACHE = (
    Path.home()
    / "Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache"
)
CACHE = Path(os.environ.get("ANKISCAPE_OPENRS2_CACHE_727", DEFAULT_CACHE))
DEFAULT_CACHE_742 = (
    Path.home()
    / "Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache"
)
CACHE_742 = Path(os.environ.get("ANKISCAPE_OPENRS2_CACHE_742", DEFAULT_CACHE_742))
JAVA = Path(os.environ.get("JAVA_BIN", "/opt/homebrew/opt/openjdk@25/bin/java"))
CORE = Path.home() / ".gradle/caches/modules-2/files-2.1/rs.darkan/core/2.0.5"


@unittest.skipUnless(
    CACHE.joinpath("main_file_cache.dat2").is_file() and JAVA.is_file() and CORE.is_dir(),
    "local rev-727 cache and Darkan Java runtime required",
)
class OpenRs2InterfaceQueryTest(unittest.TestCase):
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

    def test_real_cache_interface_and_component_counts_are_stable(self):
        self.assertEqual(
            self._run("count"),
            "index=3 interfaces=1321 components=65239 firstId=0 lastId=1320\n",
        )

    def test_grand_exchange_heading_exposes_text_and_script_hook(self):
        output = self._run("dump", "105", "15")
        self.assertEqual(output, self._run("dump", "105", "15"))
        self.assertIn("==== interface 105 components=223\n", output)
        self.assertIn("-- component 105:15 uid=6881295 type=TEXT", output)
        self.assertIn('text="Grand Exchange" fontId=496', output)
        self.assertIn("usesScripts=true onLoad=[585]", output)

    def test_find_searches_client_text_and_action_labels(self):
        output = self._run("find", "Travel to the Grand Exchange")
        self.assertIn("-- component 889:15 uid=58261519 type=CONTAINER", output)
        self.assertIn('opName="Travel to the Grand Exchange"', output)


@unittest.skipUnless(
    CACHE_742.joinpath("main_file_cache.dat2").is_file()
    and JAVA.is_file()
    and CORE.is_dir(),
    "local rev-742 cache and Darkan Java runtime required",
)
class OpenRs2If1SearchTest(unittest.TestCase):
    def test_find_reports_partial_search_and_keeps_hits(self):
        skipped_ids = [
            548,
            628,
            629,
            633,
            634,
            635,
            691,
            976,
            1253,
            1311,
            1316,
            1358,
            1360,
            1361,
            1368,
        ]
        result = subprocess.run(
            [str(TOOL), str(CACHE_742), "find", "Grand Exchange"],
            check=False,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 3)
        marker = next(
            line for line in result.stderr.splitlines() if line.startswith("PARTIAL_SEARCH ")
        )
        self.assertIn("skipped_count=15", marker)
        for interface_id in skipped_ids:
            self.assertIn(str(interface_id), marker)
        self.assertIn('text="Grand Exchange"', result.stdout)


@unittest.skipUnless(
    CACHE.joinpath("main_file_cache.dat2").is_file()
    and JAVA.is_file()
    and CORE.is_dir(),
    "local rev-727 cache and Darkan Java runtime required",
)
class OpenRs2CompleteInterfaceSearchTest(unittest.TestCase):
    def test_rev_727_find_is_complete(self):
        result = subprocess.run(
            [str(TOOL), str(CACHE), "find", "Grand Exchange"],
            check=False,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("PARTIAL_SEARCH", result.stderr)
        self.assertIn('text="Grand Exchange"', result.stdout)


if __name__ == "__main__":
    unittest.main()
