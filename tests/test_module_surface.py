import os
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

from tools.module_surface import _normalize, dump_module


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "module_surface.py"

FIRST_WAVE_DIGESTS = {
    "core/constants.py": "36b1d926a23add2870130e2b762c282baf444981a54a7eac235392514b346e0c",
    "data/quest_data.py": "8d2521110b385044e17fcbaac1dc0dd95c245e4d2d92846c3e42c6efa3e008d7",
    "data/combat_data.py": "88a22f2dd67c72aa0e261a0f78d6e4b5c318b23f891c4cdf9a0da4e5c3dec1a4",
    "data/slayer_data.py": "7373a419da64c7bd1ac41dba45f772361fc0d4d78363c4625903b12b79cd86d6",
    "logic_pure/logic_pure_combat_engine.py": "991b4a3ec2830030d63850ef391f73690cec27d9d8128b96a8a1107ebab11b62",
    "tests/combat_roster/contract.py": "d12a75aa5058e4fb6bb2fb78529f03b146ab427dad7101383cb267a9b60d5ac3",
    "tests/combat_roster/test_dragon_families.py": "6f88bbfd4518bd4267d633640e8ec8871c8afec7c7a1490df01177ec81fb4b73",
    "tests/combat_roster/test_finisher_families.py": "daec4f059b5a5d80d13234f6dfb4b9dd7b920d3b2c81425890884e2bf2b12ed9",
    "tests/combat_roster/test_roster_contract.py": "b7960e7fe5be4f1dca4e084af515aaeb2541ff8809b2b8db4d9adb36dff71638",
    "tests/combat_roster/test_slayer_families.py": "f9d5dea98865963b02803910c9394ee2cac405e3f0a2dd1d5b9b8d2e009cb781",
    "logic/shop_logic.py": "3d562a9eae474a86958e563349772fda3236433a17bf49521503c787dfc190b9",
    "ui/ui_tab_shop.py": "333de4c12d8d75707aee95a2a2c58194cf3fd2568e9e2fe50ee451e082b4a9bf",
    "data/achievement_diary_catalog.py": "e4caca4baf314e00c680931d03f2d3d3cb234dcd16ab2e3a199d2782d3b74cad",
    "runtime/runtime_actions_carried.py": "7f2ffde33212231da7c33d642f97e435dc3e5246e6cb20f154a7d190800a7f16",
    "runtime/runtime_actions_activities.py": "96a6e1d706db2bfb44b69cde01f020e73899dbc9e1edc2ed8ae3b590960d3bdc"
}
QT_DIGEST_OVERRIDES = {
    "ui/ui_tab_shop.py": "e5931feac9312ba27adf4388579a4cefbade779a43e884aaf593f22ed7bf1152"
}
ROOT_QT_DIGEST = "316fc36a1e7e525e34445fd5d1c9a89142b00547cd7e2c5bd6fb4a7f276ee9e0"
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


def public_surface_fixture(
    *,
    defining_module: str,
    member_name: str = "operation",
    qualified_name: str = "operation",
    extra_parameter: bool = False,
    data_value: int = 1,
) -> types.ModuleType:
    module = types.ModuleType("published.api")
    if extra_parameter:
        def operation(value: int, increment: int = 0) -> int:
            return value + increment
    else:
        def operation(value: int) -> int:
            return value
    operation.__module__ = defining_module
    operation.__qualname__ = qualified_name
    setattr(module, member_name, operation)

    payload_type = type("Payload", (), {"__module__": defining_module})
    payload = payload_type()
    payload.value = data_value
    module.payload = payload
    return module


class ModuleSurfaceTest(unittest.TestCase):
    def test_reexported_objects_keep_identity_when_defining_module_moves(self):
        before = public_surface_fixture(defining_module="implementation.before")
        after = public_surface_fixture(defining_module="implementation.after")

        with mock.patch("tools.module_surface._load_module", return_value=before):
            before_dump, _ = dump_module("published.api")
        with mock.patch("tools.module_surface._load_module", return_value=after):
            after_dump, _ = dump_module("published.api")

        self.assertEqual(after_dump, before_dump)

    def test_member_signature_and_data_changes_still_change_identity(self):
        baseline = public_surface_fixture(defining_module="implementation")
        with mock.patch("tools.module_surface._load_module", return_value=baseline):
            _, baseline_digest = dump_module("published.api")

        changed_modules = {
            "member": public_surface_fixture(
                defining_module="implementation",
                member_name="renamed_operation",
            ),
            "qualified_name": public_surface_fixture(
                defining_module="implementation",
                qualified_name="Container.operation",
            ),
            "signature": public_surface_fixture(
                defining_module="implementation",
                extra_parameter=True,
            ),
            "data": public_surface_fixture(
                defining_module="implementation",
                data_value=2,
            ),
        }
        for change, changed_module in changed_modules.items():
            with self.subTest(change=change):
                with mock.patch("tools.module_surface._load_module", return_value=changed_module):
                    _, changed_digest = dump_module("published.api")
                self.assertNotEqual(changed_digest, baseline_digest)

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
                "    assert len(data) == 1049",
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
            {"type": "unrepresentable", "class": "object"},
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
