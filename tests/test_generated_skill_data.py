import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.generation.outputs import write_or_check
from tools.generation.source_digests import check_source_digests, source_digest_manifest


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_ROOT = Path("/Users/ArmanTarkhanian1/Downloads/game-main")
GAME_ROOT = Path(os.environ.get("ANKISCAPE_GAME_MAIN", PROVENANCE_ROOT))


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


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
class TestGeneratedSkillData(unittest.TestCase):
    def test_source_digest_manifest_refuses_changes_until_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "inputs" / "items.yml"
            source.parent.mkdir()
            source.write_bytes(b"original")
            manifest = root / "source_digests.json"
            output_name = "data/smithing_data.py"
            other_name = "generated/summoning_data_generated.py"
            manifest.write_text(source_digest_manifest(manifest, other_name, {"unchanged.kt": "pinned"}), encoding="utf-8")
            original = check_source_digests(manifest, output_name, [source], source_root=root)
            self.assertEqual(original, {"inputs/items.yml": hashlib.sha256(b"original").hexdigest()})
            manifest.write_text(source_digest_manifest(manifest, output_name, original), encoding="utf-8")

            source.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "inputs/items.yml; pass --accept-source-change"):
                check_source_digests(manifest, output_name, [source], source_root=root)
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))[output_name], original)
            accepted = check_source_digests(
                manifest, output_name, [source], source_root=root, accept_source_change=True,
            )
            manifest.write_text(source_digest_manifest(manifest, output_name, accepted), encoding="utf-8")
            records = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertNotEqual(records[output_name], original)
            self.assertEqual(records[other_name], {"unchanged.kt": "pinned"})

    def test_output_check_names_every_stale_file_without_writing_until_asked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            same, edited, missing = root / "same.py", root / "edited.py", root / "family" / "missing.py"
            same.write_bytes(b"A = 1\n")
            edited.write_bytes(b"B = 2\r\n")
            outputs = {same: "A = 1\n", edited: "B = 2\n", missing: "C = 3\n"}

            with patch("builtins.print") as printed:
                self.assertEqual(write_or_check(outputs, check=True), 1)
            self.assertEqual(
                [call.args[0] for call in printed.call_args_list],
                [f"differs: {edited}", f"differs: {missing}", "OUTPUT_CHECK: 1 of 3 files unchanged"],
            )
            self.assertEqual(edited.read_bytes(), b"B = 2\r\n")
            self.assertFalse(missing.exists())

            with patch("builtins.print"):
                self.assertEqual(write_or_check(outputs, check=False), 0)
                self.assertEqual(write_or_check(outputs, check=True), 0)
            self.assertEqual({path: path.read_bytes() for path in outputs}, {path: text.encode("utf-8") for path, text in outputs.items()})

    def test_explicit_game_root_wins_over_environment_for_generators(self):
        explicit_root = Path("/explicit/game-main")
        environment_root = Path("/environment/game-main")
        output_path = Path("/tmp/not-written.py")
        cases = (
            (
                generate_equipment_data,
                "_parse_items_yml",
                generate_equipment_data.ITEMS_YML_RELATIVE,
            ),
            (
                generate_smithing_data,
                "_parse_items_constants",
                generate_smithing_data.ITEMS_KT_RELATIVE,
            ),
        )
        for module, reader_name, relative_path in cases:
            with self.subTest(module=module.__name__), patch.dict(
                os.environ, {"ANKISCAPE_GAME_MAIN": str(environment_root)}
            ), patch.object(module, reader_name, side_effect=RuntimeError("source probe")) as reader:
                with self.assertRaisesRegex(RuntimeError, "source probe"):
                    module.generate(explicit_root, output_path)
                reader.assert_called_once_with(explicit_root / relative_path)

    def test_smithing_generator_reproduces_checked_in_dragon_sq_shield_recipe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "smithing_data.py"
            generate_smithing_data.generate(
                GAME_ROOT, output_path, provenance_root=PROVENANCE_ROOT,
                digest_manifest=output_path.with_suffix(".json"),
            )
            generated = output_path.read_text(encoding="utf-8")

        self.assertEqual(generated, (ROOT / "data" / "smithing_data.py").read_text(encoding="utf-8"))

    def test_equipment_generator_reproduces_checked_in_dragon_sq_shield_item_1187_block(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "equipment_data.py"
            generate_equipment_data.generate(
                GAME_ROOT, output_path, provenance_root=PROVENANCE_ROOT
            )
            generated = output_path.read_text(encoding="utf-8")

        checked_in = (ROOT / "data" / "equipment_data.py").read_text(encoding="utf-8")
        self.assertEqual(
            _equipment_item_block(generated, "Dragon sq shield"),
            _equipment_item_block(checked_in, "Dragon sq shield"),
        )
        self.assertIn("source_item_id=1187", _equipment_item_block(generated, "Dragon sq shield"))
        for item_name in (
            "Willow blackjack",
            "Ice arrows",
            "Pendant of lucien",
            "Armadyl pendant",
            "Gnome amulet",
            "Yew comp bow",
            "Magic comp bow",
            "Dark bow",
            "Dragon chainbody",
            "Mining helmet (unlit)",
            "Mining helmet (lit)",
            "Lit bug lantern",
            "Brine sabre",
            "Rainbow afro",
        ):
            self.assertEqual(
                _equipment_item_block(generated, item_name),
                _equipment_item_block(checked_in, item_name),
            )
        dragon_chainbody = _equipment_item_block(generated, "Dragon chainbody")
        self.assertIn("slot='body'", dragon_chainbody)
        self.assertIn("source_item_id=3140", dragon_chainbody)

        from ankiscape.core.constants import CRAFTING_DATA, FLETCHING_DATA

        live_recipe_outputs = {
            recipe.get("output_item")
            for data in (CRAFTING_DATA, FLETCHING_DATA)
            for recipe in data.values()
            if isinstance(recipe.get("output_item"), str)
        }
        for item_name in live_recipe_outputs:
            marker = f"    {item_name!r}: EquipmentItem("
            if marker in generated:
                self.assertIn(marker, checked_in, f"{item_name} is craftable but absent from live equipment data")


if __name__ == "__main__":
    unittest.main()
