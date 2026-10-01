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
    "core/constants.py": "8f11305cb0f746eacf554213c4cebf85a467e2036ee19c6c5c789e8ca687c7dc",
    "data/quest_data.py": "6b14162532ba197c21d7be5ff3569b48307bc1185e166d475ff38ccae3248985",
    "data/combat_data.py": "7509334687e47525e9e512f64bfca6753f04744635002d6cb73a68f6b43016d5",
    "data/slayer_data.py": "7373a419da64c7bd1ac41dba45f772361fc0d4d78363c4625903b12b79cd86d6",
    "logic_pure/logic_pure_combat_engine.py": "6a8dbc326f2fc768f1208b551adcfd922ec55d9e0ffad9f4dd46dc8b60ca9019",
    "tests/combat_roster/contract.py": "12eb272aee8af160bdfca308c6aaa184b04b9a9fc4ff4ae782a82874692eb6fc",
    "tests/combat_roster/test_dragon_families.py": "622ddc3df4746ca84dd13cb662ea0376a5f3ce826341ae6e7e92dbabf1637b73",
    "tests/combat_roster/test_finisher_families.py": "8342a393b890f48ec20e402f18deea3b566c51b85bbb3370c802f6fffd0a319b",
    "tests/combat_roster/test_roster_contract.py": "c8554f2ad3a5514a7fcf131a33165d20254f2a658982b7ebfaf1b220eb7e664c",
    "tests/combat_roster/test_slayer_families.py": "a53f5df80b97763d7be54130af3e46493faebff8e3fc725d259f74442cc4d833",
    "logic/shop_logic.py": "3d562a9eae474a86958e563349772fda3236433a17bf49521503c787dfc190b9",
    "ui/ui_tab_shop.py": "333de4c12d8d75707aee95a2a2c58194cf3fd2568e9e2fe50ee451e082b4a9bf",
    "data/achievement_diary_catalog.py": "e4caca4baf314e00c680931d03f2d3d3cb234dcd16ab2e3a199d2782d3b74cad",
    "runtime/runtime_actions_carried.py": "2adca47eb3dab754cf183492afb5cff7497742d57c2edb91b7faf963572cecb0",
    "runtime/runtime_actions_activities.py": "3887200096d2242e6fbf7f28d2b44f4ad76dd757415b52cb7d95be87ebd3d0e3"
}
QT_DIGEST_OVERRIDES = {
    "ui/ui_tab_shop.py": "e5931feac9312ba27adf4388579a4cefbade779a43e884aaf593f22ed7bf1152"
}
ROOT_QT_DIGEST = "82ee3fadd94c011bbc74b00002d9076646f2d8d35890bc2e7ddabb5302064684"
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
