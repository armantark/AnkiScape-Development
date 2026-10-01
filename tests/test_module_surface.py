import os
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

from tools.module_surface import _normalize, dump_module


ROOT = Path(__file__).resolve().parents[1]


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

    def test_constants_parts_import_standalone(self):
        script = "\n".join(
            (
                "import importlib, sys",
                "import pkg_alias",
                "module = importlib.import_module(sys.argv[1])",
                "assert 'ankiscape.core.constants' not in sys.modules",
                "leaf = sys.argv[1].rsplit('.', 1)[-1]",
                "if leaf == 'activity_assets':",
                "    owner = importlib.import_module('ankiscape.core.constants_parts.quest_items')",
                "    assert module._QUEST_REWARD_ITEM_DATA is owner.QUEST_REWARD_ITEM_DATA",
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

    def test_constants_exports_match_all(self):
        script = "\n".join(
            (
                "import pkg_alias",
                "from ankiscape.core import constants",
                "from ankiscape.core.constants_parts.quest_items import QUEST_REWARD_ITEM_DATA",
                "assert constants.QUEST_REWARD_ITEM_DATA is QUEST_REWARD_ITEM_DATA",
                "names = set(constants.__all__)",
                "missing = [name for name in names if not hasattr(constants, name)]",
                "extra = sorted(name for name in vars(constants) if not name.startswith('_') and name not in names)",
                "assert not missing, missing",
                "assert not extra, extra",
                "print('OK')",
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
            self.assertEqual(result.stdout.strip(), "OK")

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


if __name__ == "__main__":
    unittest.main()
