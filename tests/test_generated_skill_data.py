import hashlib
import importlib.util
import json
import multiprocessing
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import generate_summoning_catalog
from tools.generation.outputs import write_or_check
from tools.generation.source_digests import check_source_digests, save_source_digests

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


def _write_sources(root, files):
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _smithing_sources(root):
    tool = generate_smithing_data
    constants = ("SHIELD_LEFT_HALF", "SHIELD_RIGHT_HALF", "DRAGON_SQ_SHIELD",
                 "CANNONBALL", "STEEL_BAR", "AMMO_MOULD", "COAL", "IRON_ORE")
    files = {
        tool.ITEMS_KT_RELATIVE: "\n".join(f"const val {name} = {i}" for i, name in enumerate(constants)),
        tool.ITEMS_YML_RELATIVE: "\n".join(
            f"- id: {i}\n  name: {name.replace('_', ' ').capitalize()}"
            for i, name in enumerate(constants)
        ),
        tool.DRAGON_SQ_SHIELD_PLUGIN_RELATIVE: "// fixture provenance\n",
        tool.SMITHING_RELATIVE / "BarType.kt": "",
        tool.SMITHING_RELATIVE / "SmithingType.kt": "",
        tool.SMITHING_RELATIVE / "BarProducts.kt": "",
        tool.SMITHING_RELATIVE / "SmeltingData.kt": (
            "\n    STEEL(product = Items.STEEL_BAR, primaryOre = Items.IRON_ORE, "
            "levelRequired = 30, experience = 17.5)\n"
        ),
    }
    _write_sources(root, files)


def _summoning_sources(root):
    constants = ["const val CHARM = 1", "const val TERTIARY = 2"]
    constants.extend(f"const val POUCH_{i} = {1000 + i}" for i in range(78))
    constants.extend(f"const val SCROLL_{i} = {2000 + i}" for i in range(67))
    pouches = [f"    FAMILIAR_{i}(arrayOf(Items.TERTIARY), Items.CHARM, 1, 0.1, 1, Items.POUCH_{i})"
               for i in range(78)]
    scrolls = []
    for i in range(67):
        ids = ", ".join(f"Items.POUCH_{j}" for j in range(i, 78, 67))
        scrolls.append(f"    SPELL_{i}_SCROLL(1, Items.SCROLL_{i}, 1, arrayOf({ids}))")
    _write_sources(root, {
        "Items.kt": "\n".join(constants) + "\n",
        "SummoningPouchData.kt": "enum class Pouches {\n" + ",\n".join(pouches) + "\n    ;\n}",
        "SummoningScrollData.kt": "enum class Scrolls {\n" + ",\n".join(scrolls) + "\n    ;\n}",
    })


def _vertical_wiki_table(rows):
    return "{|\n" + "\n".join("|-\n|" + "\n|".join(row) for row in rows) + "\n|}"


def _summoning_wikitext():
    tool = generate_summoning_catalog
    pouches = [["1", "", f"[[Familiar {i}]]", "1", "Gold", "[[Tertiary]]",
                "1", "", "", "1", "1", ""] for i in range(78)]
    familiar_names = [f"Familiar {i}" for i in range(78)] + ["Meerkats", "Ghast familiar"]
    familiars = [["1", "", f"[[{name}]]", "1", "1", "", "10", "", "", ""]
                 for name in familiar_names]
    scroll_names = [f"Spell {i} scroll" for i in range(67)] + ["Fetch casket scroll"]
    return {
        tool.POUCH_OLDID: _vertical_wiki_table(pouches),
        tool.FAMILIAR_OLDID: _vertical_wiki_table(familiars),
        tool.SCROLL_OLDID: "\n".join(f"|1 || || [[{name}]] || || 1 || 1 || 1" for name in scroll_names),
    }


def _paused_digest_save(manifest, output_name, read_ready, release, signal_lock=False):
    import fcntl

    read_text = Path.read_text
    flock = fcntl.flock

    def observed_lock(descriptor, operation):
        if signal_lock:
            read_ready.set()
        return flock(descriptor, operation)

    def paused_read(path, *args, **kwargs):
        content = read_text(path, *args, **kwargs)
        if path.resolve() == manifest.resolve():
            read_ready.set()
            if not release.wait(10):
                raise TimeoutError("manifest writer was not released")
        return content

    with patch.object(Path, "read_text", paused_read), patch.object(fcntl, "flock", observed_lock):
        save_source_digests(manifest, output_name, {"input.kt": output_name})


class TestGeneratorDigestRaces(unittest.TestCase):
    def test_summoning_uses_bytes_captured_before_source_replacement(self):
        tool = generate_summoning_catalog
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _summoning_sources(root)
            output = root / "summoning.py"
            manifest = root / "digests.json"
            source = root / "SummoningPouchData.kt"
            original = source.read_bytes()
            argv = ["generate", "--output", str(output), "--digest-manifest", str(manifest)]
            with patch.object(tool, "GAME_MAIN", root), patch.object(tool, "SUMMONING_SOURCE", root), \
                    patch.object(tool, "ITEMS_SOURCE", root / "Items.kt"), patch.object(sys, "argv", argv), \
                    patch.object(tool, "fetch_wikitext", side_effect=_summoning_wikitext().__getitem__):
                tool.main()
                expected = output.read_bytes()
                read_bytes = Path.read_bytes

                def replace_after_read(path):
                    content = read_bytes(path)
                    if path == source:
                        source.write_bytes(original.replace(b"1, 0.1, 1", b"1, 99.9, 1"))
                    return content

                with patch.object(Path, "read_bytes", replace_after_read):
                    tool.main()
                self.assertEqual(output.read_bytes(), expected)
                recorded = json.loads(manifest.read_text())[tool.OUTPUT_NAME]
                self.assertEqual(recorded[source.name], hashlib.sha256(original).hexdigest())

    def test_smithing_rejects_parsed_changes_even_when_source_is_restored(self):
        tool = generate_smithing_data
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _smithing_sources(root)
            output = root / "smithing.py"
            manifest = root / "digests.json"
            tool.generate(root, output, digest_manifest=manifest)
            expected = output.read_bytes(), manifest.read_bytes()
            source = root / tool.ITEMS_YML_RELATIVE
            original = source.read_bytes()
            source.write_bytes(original.replace(b"Steel bar", b"Changed bar"))
            read_text, read_bytes = Path.read_text, Path.read_bytes

            def restore_after_read(path, *args, **kwargs):
                content = read_text(path, *args, **kwargs)
                if path == source:
                    source.write_bytes(original)
                return content

            def restore_after_bytes(path):
                content = read_bytes(path)
                if path == source:
                    source.write_bytes(original)
                return content

            with patch.object(Path, "read_text", restore_after_read), \
                    patch.object(Path, "read_bytes", restore_after_bytes):
                with self.assertRaisesRegex(ValueError, "pass --accept-source-change"):
                    tool.generate(root, output, digest_manifest=manifest)
            self.assertEqual((output.read_bytes(), manifest.read_bytes()), expected)

    def test_concurrent_manifest_writers_preserve_both_outputs(self):
        context = multiprocessing.get_context("fork")
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "digests.json"
            save_source_digests(manifest, "untouched", {"original": "pinned"})
            ready, release = context.Event(), context.Event()
            second_ready, second_release = context.Event(), context.Event()
            second_release.set()
            first = context.Process(target=_paused_digest_save, args=(manifest, "smithing", ready, release))
            second = context.Process(target=_paused_digest_save, args=(manifest, "summoning", second_ready, second_release, True))
            first.start()
            try:
                self.assertTrue(ready.wait(10), "first writer did not read the manifest")
                second.start()
                self.assertTrue(second_ready.wait(10), "second writer did not reach the manifest")
            finally:
                release.set()
                first.join(10)
            second.join(10)
            self.assertEqual((first.exitcode, second.exitcode), (0, 0))
            self.assertEqual(json.loads(manifest.read_text()), {
                "untouched": {"original": "pinned"},
                "smithing": {"input.kt": "smithing"},
                "summoning": {"input.kt": "summoning"},
            })

    def test_open_manifest_reader_keeps_complete_previous_document(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "digests.json"
            save_source_digests(manifest, "smithing", {"input.kt": "old"})
            with manifest.open(encoding="utf-8") as reader:
                save_source_digests(manifest, "summoning", {"input.kt": "new"})
                self.assertEqual(json.load(reader), {"smithing": {"input.kt": "old"}})
            self.assertEqual(set(json.loads(manifest.read_text())), {"smithing", "summoning"})

    def test_failed_manifest_publication_preserves_previous_document(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "digests.json"
            save_source_digests(manifest, "smithing", {"input.kt": "old"})
            expected = manifest.read_bytes()
            files = set(Path(temp).iterdir())
            with patch("os.replace", side_effect=OSError("publication denied")):
                with self.assertRaisesRegex(OSError, "publication denied"):
                    save_source_digests(manifest, "summoning", {"input.kt": "new"})
            self.assertEqual(manifest.read_bytes(), expected)
            self.assertEqual(set(Path(temp).iterdir()), files)
            save_source_digests(manifest, "summoning", {"input.kt": "new"})
            self.assertEqual(set(json.loads(manifest.read_text())), {"smithing", "summoning"})


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
            save_source_digests(manifest, other_name, {"unchanged.kt": "pinned"})
            original = check_source_digests(manifest, output_name, {source: source.read_bytes()}, source_root=root)
            self.assertEqual(original, {"inputs/items.yml": hashlib.sha256(b"original").hexdigest()})
            save_source_digests(manifest, output_name, original)

            source.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "inputs/items.yml; pass --accept-source-change"):
                check_source_digests(manifest, output_name, {source: source.read_bytes()}, source_root=root)
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))[output_name], original)
            accepted = check_source_digests(
                manifest, output_name, {source: source.read_bytes()}, source_root=root, accept_source_change=True,
            )
            save_source_digests(manifest, output_name, accepted)
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

    def test_generator_check_accepts_the_manifest_its_locked_write_published(self):
        tool = generate_smithing_data
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _smithing_sources(root)
            output, manifest = root / "smithing.py", root / "digests.json"
            with patch("builtins.print") as printed:
                self.assertEqual(tool.generate(root, output, digest_manifest=manifest, check=True), 1)
                self.assertEqual(tool.generate(root, output, digest_manifest=manifest), 0)
                self.assertEqual(tool.generate(root, output, digest_manifest=manifest, check=True), 0)
            self.assertEqual(printed.call_args_list[-1].args[0], "OUTPUT_CHECK: 2 of 2 files unchanged")

    def test_explicit_game_root_wins_over_environment_for_generators(self):
        explicit_root = Path("/explicit/game-main")
        environment_root = Path("/environment/game-main")
        output_path = Path("/tmp/not-written.py")
        cases = (
            (
                generate_equipment_data,
                generate_equipment_data,
                "_parse_items_yml",
                generate_equipment_data.ITEMS_YML_RELATIVE,
            ),
            (
                generate_smithing_data,
                Path,
                "read_bytes",
                generate_smithing_data.ITEMS_KT_RELATIVE,
            ),
        )
        for module, reader_owner, reader_name, relative_path in cases:
            with self.subTest(module=module.__name__), patch.dict(
                os.environ, {"ANKISCAPE_GAME_MAIN": str(environment_root)}
            ), patch.object(reader_owner, reader_name, autospec=True, side_effect=RuntimeError("source probe")) as reader:
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

    def test_equipment_generator_reproduces_checked_in_catalog(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "equipment_data.py"
            self.assertEqual(
                generate_equipment_data.generate(
                    GAME_ROOT, output_path, provenance_root=PROVENANCE_ROOT
                ),
                0,
            )
            generated = output_path.read_text(encoding="utf-8")
            with patch("builtins.print") as printed:
                self.assertEqual(
                    generate_equipment_data.generate(
                        GAME_ROOT,
                        output_path,
                        provenance_root=PROVENANCE_ROOT,
                        check=True,
                    ),
                    0,
                )
            self.assertEqual(
                printed.call_args_list[-1].args[0],
                "OUTPUT_CHECK: 1 of 1 files unchanged",
            )

        checked_in = (ROOT / "data" / "equipment_data.py").read_text(encoding="utf-8")
        self.assertEqual(generated, checked_in)
        steel_spear = _equipment_item_block(generated, "Steel spear (kp)")
        self.assertIn("source_item_id=3172", steel_spear)
        self.assertIn("OpenRS2 cache rev 727 item 3172", steel_spear)
        self.assertIn("Darkan WeaponPoison.java STEEL_SPEAR mapping", steel_spear)
        for item_name in (
            "Mudskipper hat",
            "Flippers",
            "Brawling gloves (wc)",
            "Brawling gloves (fm)",
            "Brawling gloves (mining)",
            "Brawling gloves (smithing)",
            "Brawling gloves (fishing)",
            "Brawling gloves (cooking)",
        ):
            self.assertNotIn(f"    {item_name!r}: EquipmentItem(", generated)
        self.assertIn("    'Brawling gloves (Agility)': EquipmentItem(", generated)


if __name__ == "__main__":
    unittest.main()
