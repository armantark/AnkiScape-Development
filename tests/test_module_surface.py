import os
import subprocess
import sys
import unittest
from pathlib import Path

from tools.module_surface import _normalize


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "module_surface.py"

FIRST_WAVE_DIGESTS = {
    "core/constants.py": "5f5d6f649ff67dc3dd359c7926ed06417536da633075c12df1058f8353b6f6d6",
    "data/quest_data.py": "ee950c1122dc8c4e93bf581239a606fa524bd1f04393ffb0dac7dde90b659e0e",
    "data/combat_data.py": "9c5f1e4a5ac66333c79295a857a0fa65ddefed6dde46a68fe9f9ae0b29d01b77",
    "data/slayer_data.py": "d7531550bd48ae4a1ec918b3a89dd3a39dadad06433f98102012f5d6d1093c94",
    "logic_pure/logic_pure_combat_engine.py": "145e6ffbceab33564764a43d4d48d20be30f95d3e085e01b135445f92e2fa850",
    "tests/test_combat_enemy_roster.py": "262b30960b6918d8a7427720a54b19c32f10dc38938d98dc983c6cae5af91816",
    "logic/shop_logic.py": "8c380c41068723337c44482afb1abcd58bcfecd9dd6e5b912c7330c71accccba",
    "ui/ui_tab_shop.py": "3a4cb59b8b9881f1eb788a745e37044532ecd1bbb309d7c6cbcf0463a6572056",
    "data/achievement_diary_catalog.py": "5792b40a38c64b546ae399551dfef7d75f3423825cb01ea367b02862370b8d59",
    "runtime/runtime_actions_carried.py": "ac57041e4265ac634d403094c17ba6c9da173a301cf10ab590222bbacd06ae2b",
    "runtime/runtime_actions_activities.py": "1eb9b324c1065d4bd37a922234cf9d00c002f15d8825742b5b33c5b72ae0bca6",
}
QT_DIGEST_OVERRIDES = {
    "ui/ui_tab_shop.py": "2ddacc925cbf537db4587117312620d7d1546e9fad2ff9c0f167afea710d09db",
}
ROOT_QT_DIGEST = "0c01c65f4e1503d57b91c7bfc20fbd4f2247340b9b12431c03f9fe711264a175"


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
