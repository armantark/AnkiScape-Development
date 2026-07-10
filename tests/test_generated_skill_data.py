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


class TestGeneratedSkillData(unittest.TestCase):
    def test_smithing_generator_reproduces_checked_in_dragon_sq_shield_recipe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "smithing_data.py"
            generate_smithing_data.generate(GAME_ROOT, output_path)
            generated = output_path.read_text(encoding="utf-8")

        self.assertEqual(generated, (ROOT / "smithing_data.py").read_text(encoding="utf-8"))
        self.assertIn("id='repair_dragon_sq_shield'", generated)

    def test_equipment_generator_reproduces_checked_in_dragon_sq_shield_block(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "equipment_data.py"
            generate_equipment_data.generate(GAME_ROOT, output_path)
            generated = output_path.read_text(encoding="utf-8")

        self.assertEqual(generated, (ROOT / "equipment_data.py").read_text(encoding="utf-8"))
        self.assertIn("'Dragon sq shield': EquipmentItem(", generated)


if __name__ == "__main__":
    unittest.main()
