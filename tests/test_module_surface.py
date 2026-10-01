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
    "core/constants.py": "6340cbd7072dd70be082c33632e163be0dc57c00cb6683052f93075dd11dbd47",
    "data/quest_data.py": "d1e134733b893b69462ef7022123029f4548c68fca219bed559a24b46de0f49e",
    "data/combat_data.py": "88a22f2dd67c72aa0e261a0f78d6e4b5c318b23f891c4cdf9a0da4e5c3dec1a4",
    "data/slayer_data.py": "7373a419da64c7bd1ac41dba45f772361fc0d4d78363c4625903b12b79cd86d6",
    "logic_pure/logic_pure_combat_engine.py": "51c1b2bd97e6397bfc8c17c70823316b6b5e14f5393dcf96894d99cdffd320e7",
    "tests/combat_roster/contract.py": "d12a75aa5058e4fb6bb2fb78529f03b146ab427dad7101383cb267a9b60d5ac3",
    "tests/combat_roster/test_dragon_families.py": "6f88bbfd4518bd4267d633640e8ec8871c8afec7c7a1490df01177ec81fb4b73",
    "tests/combat_roster/test_finisher_families.py": "daec4f059b5a5d80d13234f6dfb4b9dd7b920d3b2c81425890884e2bf2b12ed9",
    "tests/combat_roster/test_roster_contract.py": "b7960e7fe5be4f1dca4e084af515aaeb2541ff8809b2b8db4d9adb36dff71638",
    "tests/combat_roster/test_slayer_families.py": "f9d5dea98865963b02803910c9394ee2cac405e3f0a2dd1d5b9b8d2e009cb781",
    "logic/shop_logic.py": "2e9bae9877e0f479c8ae899b88580957ac9afee4f336f9efd24a1c6f4353711d",
    "ui/ui_tab_shop.py": "bae1710a23febde767667dc9857ce2746d87e7a3d144078701d21a584a9a1ef4",
    "data/achievement_diary_catalog.py": "7c52991703757ec872b6f99533267ba3d65637c1dc6fda9e37f580f988ad8720",
    "runtime/runtime_actions_carried.py": "cb2f433223a0d04de7fc192d28943b7de330a362aead9bc48861ce3d22364d5a",
    "runtime/runtime_actions_activities.py": "3171f8e9df9c4fa1d9ebbb33394c61865aa475574c173a4772922f44301d6223"
}
QT_DIGEST_OVERRIDES = {
    "ui/ui_tab_shop.py": "055247d7a5cd4e194604e4d8b17ef34c39c671cc4fba727215560efccee7c1c5"
}
ROOT_QT_DIGEST = "1af448f8643e587c89ee14b1f6efa42d6215157224a7efb20b04447113577950"
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
