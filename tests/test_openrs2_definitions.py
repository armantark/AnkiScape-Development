from __future__ import annotations

import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "query_openrs2_cache_definitions.sh"
DEFAULT_CACHE = (
    Path.home()
    / "Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache"
)
CACHE = Path(os.environ.get("ANKISCAPE_OPENRS2_CACHE_727", DEFAULT_CACHE))
JAVA = Path(os.environ.get("JAVA_BIN", "/opt/homebrew/opt/openjdk@25/bin/java"))
JAVAC = Path(os.environ.get("JAVAC_BIN", "/opt/homebrew/opt/openjdk@25/bin/javac"))
CORE = Path.home() / ".gradle/caches/modules-2/files-2.1/rs.darkan/core/2.0.5"


@unittest.skipUnless(
    CACHE.joinpath("main_file_cache.dat2").is_file()
    and JAVA.is_file()
    and JAVAC.is_file()
    and CORE.is_dir(),
    "local rev-727 cache and Darkan Java runtime required",
)
class OpenRs2DefinitionQueryTest(unittest.TestCase):
    def test_foot_soldier_params_are_sorted_and_pin_the_period_cost(self):
        result = subprocess.run(
            [str(TOOL), str(CACHE), "npc", "--params", "12202", "12205"],
            check=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(
            result.stdout,
            "12202\tnull\t{1134=4, 1135=1, 1136=3, 1137=1, 1138=50, "
            "1139=Foot Soldier, 1140=F, 1141=0, 1142=14613, 1147=1, 1148=3289}\n"
            "12205\tnull\t{1134=4, 1135=1, 1136=3, 1137=1, 1138=50, "
            "1139=Foot Soldier, 1140=F, 1141=0, 1142=14613, 1147=0, 1148=3288}\n",
        )


if __name__ == "__main__":
    unittest.main()
