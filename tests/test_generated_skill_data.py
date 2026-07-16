import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME_ROOT = Path("/Users/ArmanTarkhanian1/Downloads/game-main")


def _load_tool(module_name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


generate_smithing_data = _load_tool("generate_smithing_data_tool", "tools/generate_smithing_data.py")
generate_equipment_data = _load_tool("generate_equipment_data_tool", "tools/generate_equipment_data.py")


def _equipment_item_block(data: str, item_name: str) -> str:
    start = data.index(f"    {item_name!r}: EquipmentItem(")
    try:
        end = data.index("    ),\n", start) + len("    ),\n")
    except ValueError:
        end = data.index("    )\n}", start) + len("    )\n")
    return data[start:end]


class TestGeneratedSkillData(unittest.TestCase):
    def test_smithing_generator_reproduces_checked_in_dragon_sq_shield_recipe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "smithing_data.py"
            generate_smithing_data.generate(GAME_ROOT, output_path)
            generated = output_path.read_text(encoding="utf-8")

        self.assertEqual(generated, (ROOT / "smithing_data.py").read_text(encoding="utf-8"))

    def test_equipment_generator_reproduces_checked_in_dragon_sq_shield_item_1187_block(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "equipment_data.py"
            generate_equipment_data.generate(GAME_ROOT, output_path)
            generated = output_path.read_text(encoding="utf-8")

        checked_in = (ROOT / "equipment_data.py").read_text(encoding="utf-8")
        self.assertEqual(
            _equipment_item_block(generated, "Dragon sq shield"),
            _equipment_item_block(checked_in, "Dragon sq shield"),
        )
        self.assertIn("source_item_id=1187", _equipment_item_block(generated, "Dragon sq shield"))
        for item_name in ("Mining helmet (unlit)", "Mining helmet (lit)"):
            self.assertEqual(
                _equipment_item_block(generated, item_name),
                _equipment_item_block(checked_in, item_name),
            )


if __name__ == "__main__":
    unittest.main()
