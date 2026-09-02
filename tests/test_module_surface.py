import subprocess
import sys
import unittest
from pathlib import Path

from tools.module_surface import _normalize


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "module_surface.py"

FIRST_WAVE_DIGESTS = {
    "core/constants.py": "63f8d2ba7a75aeafad70893e9fa076728e33a2efbe7ea4a97b3887f652891cf6",
    "data/quest_data.py": "06f9a6b44c81e0932201a8ca9a47113ac93431738ff76ed96583679dbe0d39aa",
    "data/combat_data.py": "549057827efbb8f59131b1a5889bad65650229f1fa27c8861bace1bd8abd81a4",
    "data/slayer_data.py": "32b53ad13203e6c06b0892c6091d1c240c3abd487a61a0d341b2288f7c5e0b46",
    "logic_pure/logic_pure_combat_engine.py": "6b3f7ae2a47dcf3f1bab60e487de988b40ba1ba95bc0a0d1d644906309dd98ed",
    "tests/test_combat_enemy_roster.py": "afb7357f0e2c034e350972774dc62a5171623d71430ccb1f6b2f1a8b0fb6d5d4",
    "logic/shop_logic.py": "e8b1f6e4804481131131a6ecc67a2443e757b9ad4af57abd32c2731528bd45fd",
    "ui/ui_tab_shop.py": "fd5c86a0a9ce1e2712f0a38adfb4013fee216b69a99cdbc4859ba570739e84a9",
    "data/achievement_diary_catalog.py": "61b0484f91edaae552fd81c5c400af971af924c640b635e7b3dbec01b1fe32a9",
}


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class ModuleSurfaceTest(unittest.TestCase):
    def test_first_wave_digests(self):
        result = run_tool("--digest-only", *FIRST_WAVE_DIGESTS)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), len(FIRST_WAVE_DIGESTS))
        for line, (module_path, expected) in zip(lines, FIRST_WAVE_DIGESTS.items()):
            self.assertEqual(line, f"MODULE_SURFACE_SHA256: {module_path} {expected}")

    def test_public_normalization_sorts_nested_unordered_values(self):
        value = {"z": frozenset({3, 1, 2}), "a": ("second", "first")}
        normalized = _normalize(value, set())
        self.assertEqual([item[0] for item in normalized["items"]], ["a", "z"])
        self.assertEqual(normalized["items"][0][1]["items"], ["first", "second"])
        self.assertEqual(normalized["items"][1][1]["items"], [1, 2, 3])

    def test_root_initializer_is_reported_as_unavailable_without_aqt(self):
        result = run_tool("--digest-only", "__init__.py")
        if result.returncode:
            if "No module named 'aqt'" in result.stderr:
                self.skipTest("root initializer requires aqt; use the offscreen Qt interpreter")
            self.fail(result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "MODULE_SURFACE_SHA256: __init__.py 357e7725ed616467dde1113fb8eb4e99c748808f785bbc5a39ad5692059dc4a3",
        )


if __name__ == "__main__":
    unittest.main()
