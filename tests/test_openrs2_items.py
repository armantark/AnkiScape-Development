from __future__ import annotations

import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "query_openrs2_cache.sh"
DEFAULT_CACHE = (
    Path.home()
    / "Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache"
)
CACHE = Path(os.environ.get("ANKISCAPE_OPENRS2_CACHE_727", DEFAULT_CACHE))
DEFAULT_CACHE_652 = (
    Path.home()
    / "Library/Caches/codex/2012scape-openrs2/extracted/652-2011-06-08/cache"
)
CACHE_652 = Path(os.environ.get("ANKISCAPE_OPENRS2_CACHE_652", DEFAULT_CACHE_652))
DEFAULT_CACHE_741 = (
    Path.home()
    / "Library/Caches/codex/2012scape-openrs2/extracted/741-2012-11-04/cache"
)
CACHE_741 = Path(os.environ.get("ANKISCAPE_OPENRS2_CACHE_741", DEFAULT_CACHE_741))
JAVA = Path(os.environ.get("JAVA_BIN", "/opt/homebrew/opt/openjdk@25/bin/java"))
CORE = Path.home() / ".gradle/caches/modules-2/files-2.1/rs.darkan/core/2.0.5"


@unittest.skipUnless(
    CACHE.joinpath("main_file_cache.dat2").is_file()
    and CACHE_741.joinpath("main_file_cache.dat2").is_file()
    and JAVA.is_file()
    and CORE.is_dir(),
    "local rev-727/rev-741 caches and Darkan Java runtime required",
)
class OpenRs2ItemQueryTest(unittest.TestCase):
    def test_exact_rows_pin_token_colors_and_goblin_raid_equipment(self):
        result = subprocess.run(
            [str(TOOL), str(CACHE), "--id", "7774", "7775", "7776"],
            check=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        lines = result.stdout.splitlines()
        self.assertIn("7774\tReward token\tmodel=14131\trecolors=null->null", lines[0])
        self.assertIn(
            "7775\tReward token\tmodel=14131\trecolors=[9164, 6742]->[571, 64167]",
            lines[1],
        )
        self.assertIn(
            "7776\tReward token\tmodel=14131\trecolors=[9164, 6742]->[42958, 42460]",
            lines[2],
        )
        self.assertTrue(all("bonuses=[0, 0, 0, 0, 0, 0" in line for line in lines))
        self.assertTrue(
            all("stackable=false\texchangeable=false" in line for line in lines)
        )

        raiders = subprocess.run(
            [
                str(TOOL),
                str(CACHE_741),
                "--id",
                "25350",
                "25351",
                "25352",
                "25353",
            ],
            check=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.splitlines()
        expected = (
            (
                "25350\tGoblin cower shield",
                "bonuses=[0, 0, 0, -8, -2, 13, 15, 14, -1, 14, 5",
            ),
            (
                "25351\tRaider axe",
                "bonuses=[-2, 18, 13, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 22",
            ),
            (
                "25352\tRaider chainbody",
                "bonuses=[0, 0, 0, -15, 0, 20, 29, 35, -3, 22, 8",
            ),
            (
                "25353\tRaider shield",
                "bonuses=[0, 0, 0, -6, -2, 14, 15, 13, 0, 14, 7",
            ),
        )
        for line, (identity, bonuses) in zip(raiders, expected):
            self.assertTrue(line.startswith(identity), line)
            self.assertIn(bonuses, line)
            self.assertIn("stackable=false\texchangeable=false", line)


@unittest.skipUnless(
    CACHE_652.joinpath("main_file_cache.dat2").is_file()
    and JAVA.is_file()
    and CORE.is_dir(),
    "local rev-652 cache and Darkan Java runtime required",
)
class OpenRs2PartialItemSearchTest(unittest.TestCase):
    def test_search_reports_unreadable_items_and_exits_three(self):
        result = subprocess.run(
            [str(TOOL), str(CACHE_652), "bank"],
            check=False,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("PARTIAL_SEARCH skipped_count=", result.stderr)
        self.assertIn("skipped_ids=[", result.stderr)
        self.assertIn("Bank", result.stdout)


if __name__ == "__main__":
    unittest.main()
