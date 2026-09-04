import os
import subprocess
import sys
import unittest
from pathlib import Path

from tools.module_surface import _normalize


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "module_surface.py"

FIRST_WAVE_DIGESTS = {
    "core/constants.py": "d5a79ddfd6c50efa7df57cfbd9b0e615a39cf51a0635d315b6ebe9b814777b47",
    "data/quest_data.py": "ee950c1122dc8c4e93bf581239a606fa524bd1f04393ffb0dac7dde90b659e0e",
    "data/combat_data.py": "9c5f1e4a5ac66333c79295a857a0fa65ddefed6dde46a68fe9f9ae0b29d01b77",
    "data/slayer_data.py": "d7531550bd48ae4a1ec918b3a89dd3a39dadad06433f98102012f5d6d1093c94",
    "logic_pure/logic_pure_combat_engine.py": "145e6ffbceab33564764a43d4d48d20be30f95d3e085e01b135445f92e2fa850",
    "tests/test_combat_enemy_roster.py": "262b30960b6918d8a7427720a54b19c32f10dc38938d98dc983c6cae5af91816",
    "logic/shop_logic.py": "a9455907c8b77f84fc2b3e8434ef3c91b903b9a63d3d2d4eb89eddba7c972887",
    "ui/ui_tab_shop.py": "2ddacc925cbf537db4587117312620d7d1546e9fad2ff9c0f167afea710d09db",
    "data/achievement_diary_catalog.py": "7ca9174a194b3fdd266c741ca301dfb9a6ebb2917d827d85162f71ea5fc28b61",
    "runtime/runtime_actions_carried.py": "d80cf82f807cff357b4655119717c28c0bd69e46698734a3c6c12401eedfa5f6",
    "runtime/runtime_actions_activities.py": "f24614aeb194bb68c3c71694dc57962f00a5f95b8c24c6308e365889eb850c55",
}
QT_DIGEST_OVERRIDES = {
    "ui/ui_tab_shop.py": "2ddacc925cbf537db4587117312620d7d1546e9fad2ff9c0f167afea710d09db",
}
ROOT_QT_DIGEST = "2625d3d2bb6110c0faee0a33863cf1bf8e921fe0591460eed25d071bec85e26d"


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
