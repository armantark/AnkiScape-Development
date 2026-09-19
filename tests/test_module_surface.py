import os
import subprocess
import sys
import unittest
from pathlib import Path

from tools.module_surface import _normalize


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "module_surface.py"

FIRST_WAVE_DIGESTS = {
    "core/constants.py": "b397c55b975a4da2bc8185f2bbadb4945eec8c9cc40bc50f2da4f87f068e2156",
    "data/quest_data.py": "25487154675ab19fa49642182d15fc34282ed1c275dd4c6bb420a22d82db15df",
    "data/combat_data.py": "c50b3baa6d135b56e2a0fc500f952e0e173c2873b820e60258799829837a8d0d",
    "data/slayer_data.py": "efc18af3d79cab7d1664347bef7071b28354ed3cba3344f14f7d06d023f93f9c",
    "logic_pure/logic_pure_combat_engine.py": "886cde5a31bb852ed696e8018c8954e707fff86c56dc0fc65633fd1b2f76f8c6",
    "tests/combat_roster/contract.py": "5249a887c334bd4ee8267ed6c27a6d663de19e01001b2c13c494e8b7a424aa7b",
    "tests/combat_roster/test_dragon_families.py": "0b8d1da74b5f39b217ddcd192d0b98a059e18a6f4e943f12c171d67d48a5c469",
    "tests/combat_roster/test_finisher_families.py": "bb4ee0075ffa8640410c1652ae215f850d7d4e1fb68ab7cc0358e178c81b342a",
    "tests/combat_roster/test_roster_contract.py": "c784877caf61c0fa6c1c294ad4f69f375d88913accacabba3d19c9d03dadf331",
    "tests/combat_roster/test_slayer_families.py": "5f232558b881023d500a3cd8d58c1aec523357ad352699c9681d4854d0a70e6f",
    "logic/shop_logic.py": "a8da050a08799e453b61e64ba16cefe90f049c5335a2142360931bf4bf5d105f",
    "ui/ui_tab_shop.py": "225495833df019eec919856eea981c85b114eec8327bd836bd791409ebde4c16",
    "data/achievement_diary_catalog.py": "7ca9174a194b3fdd266c741ca301dfb9a6ebb2917d827d85162f71ea5fc28b61",
    "runtime/runtime_actions_carried.py": "f9d6d6c35428d4cad48ae160a3847651eff3f2084161df6351ddcffb33c7ff78",
    "runtime/runtime_actions_activities.py": "bf7424f5569aa704db8976b1b14d0feff70ebfb9492d8b26cc65d821777427ae"
}
QT_DIGEST_OVERRIDES = {
    "ui/ui_tab_shop.py": "b0a6e20b73b866a6e7f4ce70c13cfc52c1c19ac57611e3a94e9f907adc22a0da"
}
ROOT_QT_DIGEST = "c81943a0fc224bafcefc85a0fa3bd1a1c6bc242b73c2c9949d65efa8e1bcf030"
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
            with self.subTest(environment=environment):
                result = run_tool(interpreter, "--digest-only", *FIRST_WAVE_DIGESTS, qt=qt)
                self.assertEqual(result.returncode, 0, f"{environment}: {result.stderr}")
                expected = {
                    module: QT_DIGEST_OVERRIDES.get(module, digest) if qt else digest
                    for module, digest in FIRST_WAVE_DIGESTS.items()
                }
                lines = result.stdout.splitlines()
                self.assertEqual(len(lines), len(expected))
                for line, (module_path, digest) in zip(lines, expected.items()):
                    with self.subTest(module=module_path):
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
                "    assert len(module.UTILITY_ACTIVITY_DATA) == 220",
                "if leaf == 'activity_assets':",
                "    owner = importlib.import_module('ankiscape.core.constants_parts.quest_items')",
                "    assert module._QUEST_REWARD_ITEM_DATA is owner.QUEST_REWARD_ITEM_DATA",
                "    assert len(module.UTILITY_ACTIVITY_DATA) == 220",
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
