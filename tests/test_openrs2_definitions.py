from __future__ import annotations

import os
from pathlib import Path
import subprocess
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.dungeoneering_data import FROZEN_BOSS_COMBAT_LEVEL_LADDERS


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "query_openrs2_cache_definitions.sh"
DEFAULT_CACHE = (
    Path.home()
    / "Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache"
)
CACHE = Path(os.environ.get("ANKISCAPE_OPENRS2_CACHE_727", DEFAULT_CACHE))
CACHE_742 = Path(
    os.environ.get(
        "ANKISCAPE_OPENRS2_CACHE_742",
        Path.home()
        / "Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache",
    )
)
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
    def test_frozen_boss_series_match_both_period_caches_and_live_ladders(self):
        if not CACHE_742.joinpath("main_file_cache.dat2").is_file():
            self.skipTest("local rev-742 cache required")
        series = {
            "luminescent_icefiend": ("Luminescent icefiend", range(9912, 9929), 1),
            "plane_freezer_lakhrahnaz": (
                "Plane-freezer Lakhrahnaz",
                range(9929, 9948),
                1,
            ),
            "gluttonous_behemoth": ("Gluttonous behemoth", range(9948, 9965), 1),
            "astea_frostweb": ("Astea Frostweb", range(9965, 10022), 3),
            "tokash_bloodchiller": (
                "To'Kash the Bloodchiller",
                range(10024, 10040),
                1,
            ),
            "icy_bones": ("Icy Bones", range(10040, 10058), 1),
        }
        ids = [str(npc_id) for _, npc_ids, _ in series.values() for npc_id in npc_ids]
        outputs = []
        for cache in (CACHE, CACHE_742):
            result = subprocess.run(
                [str(TOOL), str(cache), "npc", "--combat-levels", *ids],
                check=True,
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )
            outputs.append(result.stdout)
        self.assertEqual(outputs[0], outputs[1])

        rows = {
            int(npc_id): (name, int(combat_level))
            for npc_id, name, combat_level in (
                line.split("\t") for line in outputs[0].splitlines()
            )
        }
        for boss_id, (name, npc_ids, copies_per_level) in series.items():
            with self.subTest(boss_id=boss_id):
                npc_ids = tuple(npc_ids)
                self.assertEqual({rows[npc_id][0] for npc_id in npc_ids}, {name})
                expected_levels = tuple(
                    level
                    for level in FROZEN_BOSS_COMBAT_LEVEL_LADDERS[boss_id]
                    for _ in range(copies_per_level)
                )
                self.assertEqual(
                    tuple(rows[npc_id][1] for npc_id in npc_ids),
                    expected_levels,
                )

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
