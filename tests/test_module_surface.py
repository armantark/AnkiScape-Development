import os
import subprocess
import sys
import unittest
from pathlib import Path

from tools.module_surface import _normalize


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "module_surface.py"

FIRST_WAVE_DIGESTS = {
    "core/constants.py": "7d6ca7ea369a11f8b400419daf6980f966f6cf5d48234e795f6b284705e4126a",
    "data/quest_data.py": "ee950c1122dc8c4e93bf581239a606fa524bd1f04393ffb0dac7dde90b659e0e",
    "data/combat_data.py": "9c5f1e4a5ac66333c79295a857a0fa65ddefed6dde46a68fe9f9ae0b29d01b77",
    "data/slayer_data.py": "d7531550bd48ae4a1ec918b3a89dd3a39dadad06433f98102012f5d6d1093c94",
    "logic_pure/logic_pure_combat_engine.py": "145e6ffbceab33564764a43d4d48d20be30f95d3e085e01b135445f92e2fa850",
    "tests/test_combat_enemy_roster.py": "262b30960b6918d8a7427720a54b19c32f10dc38938d98dc983c6cae5af91816",
    "logic/shop_logic.py": "29902790dca0d3e452b1ecec8a29e0f5834af3b56b549c8f201ce4490d7d27a0",
    "ui/ui_tab_shop.py": "3a4cb59b8b9881f1eb788a745e37044532ecd1bbb309d7c6cbcf0463a6572056",
    "data/achievement_diary_catalog.py": "138caf7baf0201d11bb7815d971c450fabf20a536e242846433783f3f1e9e3e6",
    "runtime/runtime_actions_carried.py": "d3c2178bb94faa3f8c0f1c5537edf817b0323bb5566baedbb7c108da11d9c2be",
    "runtime/runtime_actions_activities.py": "0f9d099ae5e0099c76e4eac8c607546d2d97855aa980ad7343097297b0496294",
}
QT_DIGEST_OVERRIDES = {
    "ui/ui_tab_shop.py": "2ddacc925cbf537db4587117312620d7d1546e9fad2ff9c0f167afea710d09db",
}
ROOT_QT_DIGEST = "60268f8c330697f9303b0a4e5e59dd1b140b61b271228cd06628d95e5c020f17"


def run_tool(interpreter: Path, *args: str, qt: bool = False) -> subprocess.CompletedProcess[str]:
    environment = None
    if qt:
        environment = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    return subprocess.run(
        [str(interpreter), str(TOOL), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )


def interpreter_cases():
    plain = Path("/opt/homebrew/bin/python3")
    if not plain.exists():
        plain = Path(sys.executable)
    yield "plain", plain, False
    qt = ROOT / ".venv-qt" / "bin" / "python"
    if qt.exists():
        yield "qt", qt, True


class ModuleSurfaceTest(unittest.TestCase):
    def test_first_wave_digests(self):
        for environment, interpreter, qt in interpreter_cases():
            result = run_tool(interpreter, "--digest-only", *FIRST_WAVE_DIGESTS, qt=qt)
            self.assertEqual(result.returncode, 0, f"{environment}: {result.stderr}")
            expected = {
                module: QT_DIGEST_OVERRIDES.get(module, digest) if qt else digest
                for module, digest in FIRST_WAVE_DIGESTS.items()
            }
            lines = result.stdout.splitlines()
            self.assertEqual(len(lines), len(expected))
            for line, (module_path, digest) in zip(lines, expected.items()):
                self.assertEqual(line, f"MODULE_SURFACE_SHA256: {module_path} {digest}")

    def test_public_normalization_preserves_sequence_order_and_sorts_unordered_values(self):
        value = {"z": frozenset({3, 1, 2}), "a": ("second", "first")}
        normalized = _normalize(value, set())
        self.assertEqual([item[0] for item in normalized["items"]], ["a", "z"])
        self.assertEqual(normalized["items"][0][1]["items"], ["second", "first"])
        self.assertEqual(normalized["items"][1][1]["items"], [1, 2, 3])

    def test_unsupported_values_are_explicitly_unrepresentable(self):
        self.assertEqual(
            _normalize(object(), set()),
            {"type": "unrepresentable", "class": "builtins.object"},
        )

    def test_root_initializer_is_reported_as_unavailable_without_aqt(self):
        plain = next((case for case in interpreter_cases() if case[0] == "plain"), None)
        assert plain is not None
        result = run_tool(plain[1], "--digest-only", "__init__.py")
        if result.returncode:
            if "No module named 'aqt'" in result.stderr:
                self.skipTest("root initializer requires aqt; use the offscreen Qt interpreter")
            self.fail(result.stderr)
        self.assertEqual(result.stdout.strip(), f"MODULE_SURFACE_SHA256: __init__.py {ROOT_QT_DIGEST}")

    def test_root_initializer_digest_under_qt(self):
        qt = next((case for case in interpreter_cases() if case[0] == "qt"), None)
        if qt is None:
            self.skipTest("Qt interpreter is not installed")
        result = run_tool(qt[1], "--digest-only", "__init__.py", qt=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"MODULE_SURFACE_SHA256: __init__.py {ROOT_QT_DIGEST}")


if __name__ == "__main__":
    unittest.main()
