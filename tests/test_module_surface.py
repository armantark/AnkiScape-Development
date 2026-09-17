import os
import subprocess
import sys
import unittest
from pathlib import Path

from tools.module_surface import _normalize


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "module_surface.py"

FIRST_WAVE_DIGESTS = {
    "core/constants.py": "ceeeb401bf29997444bedc26d9ed111237845161b154571aeab754df719fe2e2",
    "data/quest_data.py": "97ee2e1a884f4b3426934b44793dcaf72b42212671aca3253c5c9a82d404b85f",
    "data/combat_data.py": "9c5f1e4a5ac66333c79295a857a0fa65ddefed6dde46a68fe9f9ae0b29d01b77",
    "data/slayer_data.py": "d7531550bd48ae4a1ec918b3a89dd3a39dadad06433f98102012f5d6d1093c94",
    "logic_pure/logic_pure_combat_engine.py": "145e6ffbceab33564764a43d4d48d20be30f95d3e085e01b135445f92e2fa850",
    "tests/combat_roster/contract.py": "62e87b82a034f3ac9506ba7c91723e5824b8c7c7305c5577fca701802d834d69",
    "tests/combat_roster/test_dragon_families.py": "a5d7588cf00d96b87d650077d41ace47b7462717fc1cdcedf4785eeddd12375e",
    "tests/combat_roster/test_finisher_families.py": "b6af72cea193a28809ace2b1a769d77c65f47ce1a2b33325c8111cf4502544ce",
    "tests/combat_roster/test_roster_contract.py": "ef57c4b7b1f998e58983dcd63fcbf965e3ee4cc08261aa1da7a0eb7a7f998e04",
    "tests/combat_roster/test_slayer_families.py": "0e5b538c8b20032488f2f4a7687f54edd36ac259e32ed50d497c4fcee34156c9",
    "logic/shop_logic.py": "c6cf56b88bab5b9151e805bbb44466a30b322c1a24af2f472b8465577984678c",
    "ui/ui_tab_shop.py": "225495833df019eec919856eea981c85b114eec8327bd836bd791409ebde4c16",
    "data/achievement_diary_catalog.py": "7ca9174a194b3fdd266c741ca301dfb9a6ebb2917d827d85162f71ea5fc28b61",
    "runtime/runtime_actions_carried.py": "d91fdc997b4f44d1825438cfeb9f6f60b6db02f2f91ee41dde8e2f8894cfb8e8",
    "runtime/runtime_actions_activities.py": "fbd91b2b2bcc8e94e9826a859d74e8634e535a6c76c834fb7903ba0899a18050"
}
QT_DIGEST_OVERRIDES = {
    "ui/ui_tab_shop.py": "b0a6e20b73b866a6e7f4ce70c13cfc52c1c19ac57611e3a94e9f907adc22a0da"
}
ROOT_QT_DIGEST = "991fc2eb44ab06966832974851caaacbcc2cb2be306459675a019e463ce4690e"
CONSTANTS_EXPORT_ORDER_DIGEST = "d180a5355fcedac9a896e306b8749d53252999e855582441f16b0261391d0ccc"


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

    def test_constants_parts_import_standalone(self):
        script = "\n".join(
            (
                "import importlib, sys",
                "import pkg_alias",
                "module = importlib.import_module(sys.argv[1])",
                "assert 'ankiscape.core.constants' not in sys.modules",
                "leaf = sys.argv[1].rsplit('.', 1)[-1]",
                "if leaf == 'activity_updates':",
                "    assert len(module.UTILITY_ACTIVITY_DATA) == 218",
                "if leaf == 'activity_assets':",
                "    owner = importlib.import_module('ankiscape.core.constants_parts.quest_items')",
                "    assert module._QUEST_REWARD_ITEM_DATA is owner.QUEST_REWARD_ITEM_DATA",
                "    assert len(module.UTILITY_ACTIVITY_DATA) == 218",
                "    assert 'Clue scroll (medium)' in module.TROUBLE_BREWING_ITEM_IMAGES",
                "    assert not hasattr(module, 'EQUIPMENT_ITEM_DATA')",
                "if leaf == 'equipment_sources':",
                "    assert not hasattr(module, 'EQUIPMENT_DATA')",
                "if leaf == 'skill_assets':",
                "    assert not hasattr(module, 'EQUIPMENT_DATA')",
                "    base = module._BASE_EQUIPMENT_DATA.copy()",
                "    data = module._equipment_data_before_diaries()",
                "    assert data is not module._BASE_EQUIPMENT_DATA",
                "    diary = importlib.import_module('ankiscape.data.achievement_diary_data')",
                "    data.update(diary.diary_equipment_data_as_dict())",
                "    module._add_post_diary_equipment_data(data)",
                "    assert len(data) == 994",
                "    assert module._BASE_EQUIPMENT_DATA == base",
                "assert 'ankiscape.core.constants' not in sys.modules",
                "print('OK')",
            )
        )
        part_names = sorted(
            path.stem
            for path in (ROOT / "core" / "constants_parts").glob("*.py")
            if path.stem != "__init__"
        )
        for environment, interpreter, qt in interpreter_cases():
            process_environment = (
                {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
                if qt
                else None
            )
            for part_name in part_names:
                module_name = f"ankiscape.core.constants_parts.{part_name}"
                result = subprocess.run(
                    [str(interpreter), "-c", script, module_name],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                    env=process_environment,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{environment} {module_name}: {result.stderr}",
                )
                self.assertEqual(result.stdout.strip(), "OK")

    def test_constants_export_order(self):
        script = "\n".join(
            (
                "import hashlib, json",
                "import pkg_alias",
                "from ankiscape.core import constants",
                "from ankiscape.core.constants_parts.quest_items import QUEST_REWARD_ITEM_DATA",
                "assert constants.QUEST_REWARD_ITEM_DATA is QUEST_REWARD_ITEM_DATA",
                "names = set(constants.__all__)",
                "missing = [name for name in names if not hasattr(constants, name)]",
                "extra = sorted(name for name in vars(constants) if not name.startswith('_') and name not in names)",
                "assert not missing, missing",
                "assert not extra, extra",
                "payload = json.dumps(",
                "    constants.__all__,",
                "    ensure_ascii=False,",
                "    separators=(',', ':'),",
                ").encode()",
                "print(hashlib.sha256(payload).hexdigest())",
            )
        )
        for environment, interpreter, qt in interpreter_cases():
            process_environment = (
                {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
                if qt
                else None
            )
            result = subprocess.run(
                [str(interpreter), "-c", script],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                env=process_environment,
            )
            self.assertEqual(result.returncode, 0, f"{environment}: {result.stderr}")
            self.assertEqual(result.stdout.strip(), CONSTANTS_EXPORT_ORDER_DIGEST)

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
