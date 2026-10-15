import hashlib
import io
import json
import os
import runpy
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from itertools import product
from pathlib import Path
from unittest.mock import patch

from tools import generate_npc_shop_data as generator
from tools.generation import source_digests


OUTPUT_NAME = "data/shop_data.py"
OTHER_DIGESTS = {
    "data/equipment_data.py": {"equipment/input.kt": "equipment-pin"},
    "data/smithing_data.py": {"smithing/input.kt": "smithing-pin"},
    "data/summoning_data.py": {"summoning/input.kt": "summoning-pin"},
}
PARTIAL_MODES = (
    "stock-exclusions-only", "services-only", "vendor-actions-only", "currency-activation-only",
)


def _json_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _catalog(path):
    values = runpy.run_path(str(path))
    return {
        "version": values["SHOP_DATA_VERSION"],
        "shops": list(values["SHOP_DATA"].values()),
        "currencies": list(values["SHOP_CURRENCIES"].values()),
        "services": list(values["SHOP_SERVICES"].values()),
        "vendor_actions": list(values["SHOP_VENDOR_ACTIONS"].values()),
        "summary": values["SHOP_COVERAGE_SUMMARY"],
        "player_sell_prices": values["SHOP_PLAYER_SELL_PRICES"],
        "player_buy_prices": values["SHOP_PLAYER_BUY_PRICES"],
    }


class ShopSources:
    def __init__(self, root):
        self.root = root
        self.repo = root / "repo"
        self.raw = root / "raw"
        self.shops = self.raw / "shops"
        self.cache = self.raw / "cache"
        self.items = self.raw / "game-main/data/cfg/items.yml"
        self.core = self.raw / "core/core.jar"
        self.dependencies = [self.raw / "a/shared.jar", self.raw / "b/shared.jar"]
        self.catalog = root / "out/shop_data.py"
        self.ledger = root / "out/ledger.json"
        self.summary = root / "out/summary.md"
        self.manifest = self.repo / "generated/source_digests.json"
        self.calls = []
        self.shops.mkdir(parents=True)
        self.cache.mkdir(parents=True)
        self.items.parent.mkdir(parents=True)
        self.items.write_text(
            '- id: 100\n  name: "Fixture item"\n  tradeable: true\n'
            '- id: 101\n  name: "Unstocked fixture"\n  tradeable: true\n'
            '- id: 995\n  name: "Coins"\n  tradeable: false\n', encoding="utf-8",
        )
        _json_write(self.shops / "fixture_shop.json", {
            "name": "Fixture shop", "currency": 995, "generalStore": True,
            "items": [{"item": {"id": 100, "amount": 12}}],
        })
        _json_write(self.shops / "a_test_shop.json", {"name": "Excluded fixture", "items": []})
        _json_write(self.cache / "main_file_cache.dat2", {
            "100": {"value": 10, "sell_price": 3, "stackable": 1},
            "101": {"value": 20, "sell_price": 6, "stackable": 0},
        })
        for name, content in (("255", b"master-index"), ("0", b"index-zero"), ("00", b"")):
            (self.cache / f"main_file_cache.idx{name}").write_bytes(content)
        for path, content in ((self.core, b"core"), *zip(self.dependencies, (b"dependency-a", b"dependency-b"))):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

    @property
    def outputs(self):
        return self.catalog, self.ledger, self.summary

    def bindings(self):
        bindings = {"game-main/data/cfg/items.yml": self.items}
        bindings.update({f"darkan/shops/{path.name}": path for path in self.shops.glob("*.json")})
        bindings["darkan/cache/main_file_cache.dat2"] = self.cache / "main_file_cache.dat2"
        bindings.update({
            f"darkan/cache/{path.name}": path for path in self.cache.iterdir()
            if path.name.startswith("main_file_cache.idx") and path.name.removeprefix("main_file_cache.idx").isdigit()
        })
        bindings.update({
            f"darkan/decoder/classpath/{index:04d}": path
            for index, path in enumerate([self.core, *self.dependencies])
        })
        return bindings

    def digests(self):
        return {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in self.bindings().items()}

    def seed_manifest(self, *, include_npc=True):
        contents = deepcopy(OTHER_DIGESTS)
        if include_npc:
            contents[OUTPUT_NAME] = self.digests()
        _json_write(self.manifest, contents)

    def decoder(self, cache_path, item_ids, *, core_jar, dependency_jars, java_home):
        dependencies = list(dependency_jars)
        self.calls.append({
            "cache": cache_path, "core": core_jar, "dependencies": dependencies,
            "ids": set(item_ids), "java_home": java_home,
            "cache_bytes": {path.name: path.read_bytes() for path in cache_path.iterdir() if path.is_file()},
            "jar_bytes": [path.read_bytes() for path in [core_jar, *dependencies]],
        })
        rows = json.loads((cache_path / "main_file_cache.dat2").read_text(encoding="utf-8"))
        return {int(key): value for key, value in rows.items() if int(key) in self.calls[-1]["ids"]}

    def invoke(self, *extra, decoder=None, default_dependencies=False):
        argv = [
            "generate_npc_shop_data.py", "--darkan-shops", str(self.shops),
            "--darkan-cache", str(self.cache), "--items-2011", str(self.items),
            "--darkan-core-jar", str(self.core), "--darkan-java-home", str(self.raw / "jdk"),
            "--existing-shop-data", str(self.catalog), "--existing-ledger", str(self.ledger),
            "--shop-data-out", str(self.catalog), "--ledger-out", str(self.ledger),
            "--summary-out", str(self.summary),
        ]
        if not default_dependencies:
            for path in self.dependencies:
                argv.extend(("--darkan-dependency-jar", str(path)))
        argv.extend(extra)
        self.last_argv = argv
        stream = io.StringIO()
        error = None
        code = 0
        with patch.object(generator, "REPO_ROOT", self.repo), patch.object(
            generator, "DEFAULT_DARKAN_DEPENDENCY_JARS", tuple(self.dependencies),
        ), patch.object(generator, "load_darkan_shop_price_inputs", side_effect=decoder or self.decoder), patch.object(
            sys, "argv", argv,
        ), redirect_stdout(stream), redirect_stderr(stream):
            try:
                generator.main()
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
                error = exc if code else None
            except Exception as exc:
                error = exc
                code = 1
        return code, error, stream.getvalue()

    def state(self):
        return {
            path: (path.read_bytes(), path.stat().st_mtime_ns) if path.exists() else None
            for path in (*self.outputs, self.manifest)
        }

    def age_outputs(self):
        for path in (*self.outputs, self.manifest):
            if path.exists():
                os.utime(path, ns=(1_500_000_000_000_000_000, 1_500_000_000_000_000_000))


class TestNpcShopSourceInputs(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="ankiscape-shop-input-test-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def fixture(self, name="fixture", *, generated=False):
        fixture = ShopSources(self.root / name)
        if generated:
            self.assert_success(fixture.invoke())
            fixture.seed_manifest()
            fixture.calls.clear()
        return fixture

    def assert_success(self, result):
        code, error, output = result
        self.assertEqual(code, 0, f"{error!r}\n{output}")
        self.assertIsNone(error)

    def assert_refused(self, fixture, before, result, *, changed=None):
        code, error, output = result
        self.assertTrue(fixture.state() == before, "Refusal changed an output or the manifest")
        self.assertNotEqual(code, 0, output)
        self.assertNotIn("unrecognized arguments", output)
        self.assertEqual(fixture.calls, [], "Source validation must precede the decoder")
        if changed is not None:
            self.assertIsInstance(error, ValueError)
            self.assertEqual(
                str(error), f"Source changed for {OUTPUT_NAME}: {', '.join(sorted(changed))}; pass --accept-source-change",
            )

    def test_existing_full_command_refuses_changed_source_before_publication(self):
        fixture = self.fixture()
        fixture.seed_manifest()
        for path, sentinel in zip(fixture.outputs, (b"catalog sentinel\n", b"ledger sentinel\n", b"summary sentinel\n")):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(sentinel)
        fixture.age_outputs()
        before = fixture.state()
        baseline = fixture.digests()
        fixture.items.write_text(fixture.items.read_text(encoding="utf-8") + "# changed source\n", encoding="utf-8")
        result = fixture.invoke()
        after = fixture.state()
        print("NPC_SOURCE_PRIMARY_OBSERVATION " + json.dumps({
            "decoder_calls": len(fixture.calls), "command_exit": result[0],
            "command_error": repr(result[1]), "changed_sentinels": [
                name for name, path in zip(("catalog", "ledger", "summary", "manifest"), (*fixture.outputs, fixture.manifest))
                if before[path] != after[path]
            ], "baseline_digests": baseline, "changed_digests": fixture.digests(),
            "manifest_bytes_unchanged": before[fixture.manifest][0] == after[fixture.manifest][0],
            "generator_argv": fixture.last_argv,
            "decoder_requested_ids": sorted(fixture.calls[0]["ids"]) if fixture.calls else [],
            "changed_sentinel_bytes": [
                name for name, path in zip(("catalog", "ledger", "summary", "manifest"), (*fixture.outputs, fixture.manifest))
                if before[path][0] != after[path][0]
            ],
            "sentinel_sha256_before": {
                name: hashlib.sha256(before[path][0]).hexdigest()
                for name, path in zip(("catalog", "ledger", "summary", "manifest"), (*fixture.outputs, fixture.manifest))
            },
            "sentinel_sha256_after": {
                name: hashlib.sha256(after[path][0]).hexdigest()
                for name, path in zip(("catalog", "ledger", "summary", "manifest"), (*fixture.outputs, fixture.manifest))
            },
        }, sort_keys=True))
        self.assert_refused(fixture, before, result, changed=["game-main/data/cfg/items.yml"])

    def test_each_external_source_family_is_guarded(self):
        families = ("metadata", "shop", "cache-data", "cache-index", "core", "dependency")
        for family in families:
            with self.subTest(family=family):
                fixture = self.fixture(family)
                fixture.seed_manifest()
                before = fixture.state()
                paths = {
                    "metadata": fixture.items, "shop": fixture.shops / "fixture_shop.json",
                    "cache-data": fixture.cache / "main_file_cache.dat2",
                    "cache-index": fixture.cache / "main_file_cache.idx0",
                    "core": fixture.core, "dependency": fixture.dependencies[0],
                }
                path = paths[family]
                original = fixture.digests()
                path.write_bytes(path.read_bytes() + b"\n")
                changed = [name for name, digest in fixture.digests().items() if original[name] != digest]
                self.assert_refused(fixture, before, fixture.invoke(), changed=changed)

    def test_added_removed_and_reordered_members_change_logical_map(self):
        cases = ("add-shop", "add-index", "add-dependency", "remove-shop", "remove-index", "remove-dependency", "reorder")
        for case in cases:
            with self.subTest(case=case):
                fixture = self.fixture(case)
                fixture.seed_manifest()
                original = fixture.digests()
                before = fixture.state()
                if case == "add-shop":
                    _json_write(fixture.shops / "new_shop.json", {"name": "New shop", "items": []})
                elif case == "add-index":
                    (fixture.cache / "main_file_cache.idx9").write_bytes(b"")
                elif case == "add-dependency":
                    extra = fixture.raw / "extra.jar"
                    extra.write_bytes(b"extra")
                    fixture.dependencies.append(extra)
                elif case == "remove-shop":
                    (fixture.shops / "a_test_shop.json").unlink()
                elif case == "remove-index":
                    (fixture.cache / "main_file_cache.idx00").unlink()
                elif case == "remove-dependency":
                    fixture.dependencies.pop()
                else:
                    fixture.dependencies.reverse()
                current = fixture.digests()
                changed = [name for name in original.keys() | current.keys() if original.get(name) != current.get(name)]
                self.assert_refused(fixture, before, fixture.invoke(), changed=changed)

    def test_missing_required_inputs_and_empty_shop_set_refuse_even_when_accepted(self):
        for case in ("shops-root", "cache-root", "metadata", "cache-data", "master-index", "core", "dependency", "empty-shops"):
            for accepted in (False, True):
                with self.subTest(case=case, accepted=accepted):
                    fixture = self.fixture(f"{case}-{accepted}")
                    fixture.seed_manifest()
                    before = fixture.state()
                    paths = {
                        "shops-root": fixture.shops, "cache-root": fixture.cache, "metadata": fixture.items,
                        "cache-data": fixture.cache / "main_file_cache.dat2",
                        "master-index": fixture.cache / "main_file_cache.idx255", "core": fixture.core,
                        "dependency": fixture.dependencies[0],
                    }
                    if case == "empty-shops":
                        for path in fixture.shops.iterdir():
                            path.unlink()
                    elif paths[case].is_dir():
                        shutil.rmtree(paths[case])
                    else:
                        paths[case].unlink()
                    result = fixture.invoke(*(["--accept-source-change"] if accepted else []))
                    self.assert_refused(fixture, before, result)
                    self.assertIsInstance(result[1], (FileNotFoundError, ValueError))
                    self.assertNotIn("pass --accept-source-change", str(result[1]))

    def test_refusal_does_not_create_output_parents_lock_or_publication_files(self):
        fixture = self.fixture()
        fixture.seed_manifest()
        fixture.items.write_bytes(fixture.items.read_bytes() + b"\n")
        fixture.catalog = fixture.root / "catalog-parent/catalog.py"
        fixture.ledger = fixture.root / "ledger-parent/ledger.json"
        fixture.summary = fixture.root / "summary-parent/summary.md"
        files_before = sorted(path.relative_to(fixture.root).as_posix() for path in fixture.root.rglob("*"))
        with patch.object(tempfile, "tempdir", str(fixture.root)):
            self.assert_refused(fixture, fixture.state(), fixture.invoke(), changed=["game-main/data/cfg/items.yml"])
        self.assertEqual(sorted(path.relative_to(fixture.root).as_posix() for path in fixture.root.rglob("*")), files_before)

    def test_bootstrap_manifest_has_exact_names_order_and_only_npc_addition(self):
        fixture = self.fixture()
        fixture.dependencies.append(fixture.dependencies[0])
        _json_write(fixture.shops / "Fixture-Shop.json", {"name": "Distinct filename", "items": []})
        (fixture.cache / "main_file_cache.idxnotes").write_bytes(b"not a numeric index")
        nested = fixture.shops / "nested"
        nested.mkdir()
        (nested / "ignored.json").write_text("invalid nested input", encoding="utf-8")
        fixture.seed_manifest(include_npc=False)
        self.assert_success(fixture.invoke())
        manifest = json.loads(fixture.manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest, {**OTHER_DIGESTS, OUTPUT_NAME: fixture.digests()})
        self.assertIn("darkan/cache/main_file_cache.idx00", manifest[OUTPUT_NAME])
        self.assertIn("darkan/cache/main_file_cache.idx0", manifest[OUTPUT_NAME])
        self.assertEqual(manifest[OUTPUT_NAME]["darkan/decoder/classpath/0001"], manifest[OUTPUT_NAME]["darkan/decoder/classpath/0003"])
        self.assertEqual(fixture.calls[0]["jar_bytes"], [b"core", b"dependency-a", b"dependency-b", b"dependency-a"])
        self.assertEqual(len(set(fixture.calls[0]["dependencies"])), 3)

    def test_default_dependency_order_is_bound_without_explicit_jar_flags(self):
        fixture = self.fixture()
        fixture.seed_manifest(include_npc=False)
        self.assert_success(fixture.invoke(default_dependencies=True))
        self.assertEqual(json.loads(fixture.manifest.read_text(encoding="utf-8"))[OUTPUT_NAME], fixture.digests())
        self.assertEqual(fixture.calls[0]["jar_bytes"], [b"core", b"dependency-a", b"dependency-b"])

    def test_snapshot_survives_original_replacement_and_is_cleaned_after_success(self):
        fixture = self.fixture()
        fixture.seed_manifest(include_npc=False)
        captured = fixture.digests()
        originals = fixture.bindings()

        def replace_originals(cache_path, item_ids, **kwargs):
            result = fixture.decoder(cache_path, item_ids, **kwargs)
            self.assertNotEqual(cache_path, fixture.cache)
            paths = [cache_path / name for name in fixture.calls[-1]["cache_bytes"]]
            paths.extend([kwargs["core_jar"], *kwargs["dependency_jars"]])
            for path in paths:
                self.assertFalse(path.is_symlink())
                for original in originals.values():
                    self.assertNotEqual((path.stat().st_dev, path.stat().st_ino), (original.stat().st_dev, original.stat().st_ino))
            fixture.items.write_text('- id: 100\n  name: "Replaced item"\n  tradeable: true\n', encoding="utf-8")
            _json_write(fixture.shops / "fixture_shop.json", {"name": "Replaced shop", "items": []})
            for original in [fixture.cache / "main_file_cache.dat2", fixture.core, *fixture.dependencies]:
                original.write_bytes(b"replaced after capture")
            return result

        self.assert_success(fixture.invoke(decoder=replace_originals))
        catalog = _catalog(fixture.catalog)
        shop = next(shop for shop in catalog["shops"] if shop["id"] == "fixture_shop")
        self.assertEqual(shop["display_name"], "Fixture shop")
        self.assertEqual(shop["stock"][0]["item_name"], "Fixture item")
        self.assertEqual(shop["stock"][0]["buy_price"], 10)
        self.assertEqual(catalog["player_sell_prices"]["Unstocked fixture"], 6)
        self.assertEqual(json.loads(fixture.manifest.read_text(encoding="utf-8"))[OUTPUT_NAME], captured)
        call = fixture.calls[0]
        self.assertFalse(call["cache"].exists())
        self.assertFalse(any(path.exists() for path in [call["core"], *call["dependencies"]]))

    def test_source_capture_reads_are_bounded_and_every_input_is_streamed(self):
        fixture = self.fixture()
        fixture.seed_manifest(include_npc=False)
        originals = set(fixture.bindings().values())
        reads = set()
        real_open = io.open

        class BoundedReader:
            def __init__(self, stream, path):
                self.stream = stream
                self.path = path

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return self.stream.__exit__(*args)

            def __getattr__(self, name):
                return getattr(self.stream, name)

            def read(self, size=-1):
                if size <= 0:
                    raise AssertionError(f"Unbounded source read: {self.path}: {size}")
                reads.add(self.path)
                return self.stream.read(size)

            def readinto(self, buffer):
                if not len(buffer):
                    raise AssertionError(f"Unbounded source readinto: {self.path}: {len(buffer)}")
                reads.add(self.path)
                return self.stream.readinto(buffer)

        def bounded_open(path, mode="r", *args, **kwargs):
            stream = real_open(path, mode, *args, **kwargs)
            candidate = Path(path) if not isinstance(path, int) else None
            return BoundedReader(stream, candidate) if candidate in originals and "r" in mode else stream

        with patch("io.open", side_effect=bounded_open):
            self.assert_success(fixture.invoke())
        self.assertEqual(reads, originals)

    def test_parse_and_decoder_failures_preserve_all_published_files_and_clean_snapshot(self):
        for case in ("invalid-shop", "invalid-metadata", "decoder"):
            with self.subTest(case=case):
                fixture = self.fixture(case, generated=True)
                if case == "invalid-shop":
                    (fixture.shops / "fixture_shop.json").write_text("{not-json", encoding="utf-8")
                elif case == "invalid-metadata":
                    fixture.items.write_text("- id: not-an-integer\n", encoding="utf-8")
                fixture.seed_manifest()
                before = fixture.state()

                def broken_decoder(cache_path, item_ids, **kwargs):
                    fixture.decoder(cache_path, item_ids, **kwargs)
                    raise RuntimeError("fixture decoder failure")

                result = fixture.invoke("--accept-source-change", decoder=broken_decoder if case == "decoder" else None)
                self.assertEqual(fixture.state(), before)
                self.assertNotEqual(result[0], 0)
                self.assertNotIn("unrecognized arguments", result[2])
                self.assertIsInstance(result[1], (ValueError, RuntimeError))
                if case == "decoder":
                    self.assertEqual(str(result[1]), "fixture decoder failure")
                    self.assertFalse(fixture.calls[0]["cache"].exists())
                    self.assertFalse(fixture.calls[0]["core"].exists())

    def test_explicit_manifest_overrides_default_and_preserves_other_entries(self):
        fixture = self.fixture()
        fixture.seed_manifest()
        default_before = fixture.manifest.read_bytes()
        custom = fixture.root / "custom/digests.json"
        _json_write(custom, OTHER_DIGESTS)
        self.assert_success(fixture.invoke("--digest-manifest", str(custom)))
        self.assertEqual(fixture.manifest.read_bytes(), default_before)
        self.assertEqual(json.loads(custom.read_text(encoding="utf-8")), {**OTHER_DIGESTS, OUTPUT_NAME: fixture.digests()})

    def test_full_generation_ignores_existing_partial_input_options(self):
        fixture = self.fixture()
        fixture.seed_manifest()
        poison = fixture.root / "poison.py"
        poison.write_text("raise AssertionError('full generation read partial input')\n", encoding="utf-8")
        self.assert_success(fixture.invoke("--existing-shop-data", str(poison), "--existing-ledger", str(poison)))
        self.assertEqual(_catalog(fixture.catalog)["shops"][0]["display_name"], "Fixture shop")

    def test_unchanged_full_runs_preserve_bytes_mtimes_and_do_not_create_manifest_lock(self):
        fixture = self.fixture(generated=True)
        fixture.age_outputs()
        lock = fixture.manifest.with_suffix(".json.lock")
        lock.unlink(missing_ok=True)
        before = fixture.state()
        self.assert_success(fixture.invoke("--check"))
        self.assertEqual(fixture.state(), before)
        self.assertFalse(lock.exists())
        self.assert_success(fixture.invoke())
        self.assertEqual(fixture.state(), before)
        self.assertFalse(lock.exists())

    def test_manifest_format_difference_is_checked_exactly_without_rewriting_equivalent_outputs(self):
        fixture = self.fixture(generated=True)
        contents = json.loads(fixture.manifest.read_text(encoding="utf-8"))
        fixture.manifest.write_text(json.dumps(contents), encoding="utf-8")
        fixture.age_outputs()
        before = fixture.state()
        result = fixture.invoke("--check")
        self.assertNotEqual(result[0], 0)
        self.assertNotIn("unrecognized arguments", result[2])
        self.assertEqual(fixture.state(), before)
        self.assert_success(fixture.invoke())
        self.assertEqual(fixture.manifest.read_text(encoding="utf-8"), json.dumps(contents, indent=2, sort_keys=True) + "\n")
        for path in fixture.outputs:
            self.assertEqual(fixture.state()[path], before[path])

    def test_full_command_preserves_shipped_summary_order_for_noop_and_bootstrap(self):
        for entry_exists in (False, True):
            with self.subTest(entry_exists=entry_exists):
                fixture = self.fixture(str(entry_exists), generated=True)
                catalog = _catalog(fixture.catalog)
                excluded = catalog["summary"].pop("excluded_stock_row_count")
                catalog["summary"]["excluded_stock_row_count"] = excluded
                self.assertEqual(list(catalog["summary"])[-3:], [
                    "access_gate_counts", "player_sell_price_count", "excluded_stock_row_count",
                ])
                generator.write_shop_data(catalog, fixture.catalog)
                if not entry_exists:
                    fixture.seed_manifest(include_npc=False)
                fixture.age_outputs()
                before = fixture.state()
                self.assert_success(fixture.invoke())
                for path in fixture.outputs:
                    self.assertEqual(fixture.state()[path], before[path], "Full generation rewrote the shipped catalog representation")
                if entry_exists:
                    self.assertEqual(fixture.state()[fixture.manifest], before[fixture.manifest])
                self.assertEqual(json.loads(fixture.manifest.read_text(encoding="utf-8")), {**OTHER_DIGESTS, OUTPUT_NAME: fixture.digests()})
                self.assert_success(fixture.invoke("--check"))

    def test_relocated_identical_sources_pass_check_and_keep_historical_output_bytes(self):
        first = self.fixture("first", generated=True)
        relocated = self.fixture("relocated")
        relocated.catalog, relocated.ledger, relocated.summary = first.outputs
        _json_write(relocated.manifest, json.loads(first.manifest.read_text(encoding="utf-8")))
        self.assertEqual(first.digests(), relocated.digests())
        shutil.rmtree(first.raw)
        relocated.age_outputs()
        before = relocated.state()
        self.assert_success(relocated.invoke("--check"))
        self.assertEqual(relocated.state(), before)
        self.assert_success(relocated.invoke())
        self.assertEqual(relocated.state(), before)
        self.assertFalse(relocated.manifest.with_suffix(".json.lock").exists())

    def test_absent_entry_check_is_read_only_and_bootstrap_preserves_equivalent_triplet(self):
        for manifest_exists in (False, True):
            with self.subTest(manifest_exists=manifest_exists):
                fixture = self.fixture(str(manifest_exists), generated=True)
                if manifest_exists:
                    fixture.seed_manifest(include_npc=False)
                else:
                    fixture.manifest.unlink()
                fixture.age_outputs()
                before = fixture.state()
                result = fixture.invoke("--check")
                self.assertNotEqual(result[0], 0)
                self.assertNotIn("unrecognized arguments", result[2])
                self.assertEqual(fixture.state(), before)
                self.assert_success(fixture.invoke())
                for path in fixture.outputs:
                    self.assertEqual(fixture.state()[path], before[path])
                expected = {**(OTHER_DIGESTS if manifest_exists else {}), OUTPUT_NAME: fixture.digests()}
                self.assertEqual(json.loads(fixture.manifest.read_text(encoding="utf-8")), expected)

    def test_bootstrap_creates_missing_manifest_parent_only_after_success(self):
        fixture = self.fixture()
        self.assertFalse(fixture.manifest.parent.exists())
        result = fixture.invoke("--check")
        self.assertNotEqual(result[0], 0)
        self.assertNotIn("unrecognized arguments", result[2])
        self.assertFalse(fixture.manifest.parent.exists())
        self.assertFalse(any(path.parent.exists() for path in fixture.outputs))
        self.assert_success(fixture.invoke())
        self.assertEqual(json.loads(fixture.manifest.read_text(encoding="utf-8")), {OUTPUT_NAME: fixture.digests()})

    def test_accepted_valid_price_change_publishes_actual_candidate_without_price_freeze(self):
        first = self.fixture("first", generated=True)
        fixture = self.fixture("changed")
        fixture.catalog, fixture.ledger, fixture.summary = first.outputs
        _json_write(fixture.manifest, json.loads(first.manifest.read_text(encoding="utf-8")))
        cache = json.loads((fixture.cache / "main_file_cache.dat2").read_text(encoding="utf-8"))
        cache["100"].update({"value": 42, "sell_price": 13})
        _json_write(fixture.cache / "main_file_cache.dat2", cache)
        self.assert_success(fixture.invoke("--accept-source-change"))
        catalog = _catalog(fixture.catalog)
        self.assertEqual(catalog["shops"][0]["stock"][0]["buy_price"], 42)
        self.assertEqual(catalog["player_buy_prices"]["Fixture item"], 42)
        self.assertEqual(catalog["player_sell_prices"]["Fixture item"], 13)
        self.assertEqual(catalog["shops"][0]["source_path"], str(fixture.shops / "fixture_shop.json"))
        ledger = json.loads(fixture.ledger.read_text(encoding="utf-8"))
        self.assertEqual(ledger["source_roots"]["darkan_shops"], str(fixture.shops))
        self.assertIn(f"`{fixture.shops}`", fixture.summary.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(fixture.manifest.read_text(encoding="utf-8")), {**OTHER_DIGESTS, OUTPUT_NAME: fixture.digests()})

    def test_accepted_check_reports_manifest_only_and_output_changes_without_publication(self):
        for case in ("digest-only", "price"):
            with self.subTest(case=case):
                fixture = self.fixture(case, generated=True)
                if case == "digest-only":
                    fixture.items.write_bytes(fixture.items.read_bytes() + b"# equivalent metadata\n")
                else:
                    cache = json.loads((fixture.cache / "main_file_cache.dat2").read_text(encoding="utf-8"))
                    cache["100"]["value"] = 42
                    _json_write(fixture.cache / "main_file_cache.dat2", cache)
                before = fixture.state()
                result = fixture.invoke("--check", "--accept-source-change")
                self.assertNotEqual(result[0], 0)
                self.assertNotIn("unrecognized arguments", result[2])
                self.assertEqual(len(fixture.calls), 1)
                self.assertEqual(fixture.state(), before)

    def alter_nonprovenance_output(self, fixture, case):
        catalog = _catalog(fixture.catalog)
        ledger = json.loads(fixture.ledger.read_text(encoding="utf-8"))
        if case == "lookalike":
            catalog["shops"][0]["display_name"] = str(fixture.shops) + "/lookalike"
        elif case in {"shop-filename", "outside-root"}:
            catalog["shops"][0]["source_path"] = str(fixture.shops / "wrong.json") if case == "shop-filename" else str(fixture.raw / "elsewhere/fixture_shop.json")
        elif case == "stock-filename":
            catalog["shops"][0]["stock"][0]["source_path"] = str(fixture.shops / "wrong.json")
        elif case == "excluded-filename":
            ledger["shops"][0]["source_path"] = str(fixture.shops / "wrong.json")
        elif case == "price":
            catalog["player_buy_prices"]["Fixture item"] = 999
        elif case == "ledger-fact":
            ledger["shops"][1]["reason"] = "changed fact"
        if case in {"excluded-filename", "ledger-fact"}:
            _json_write(fixture.ledger, ledger)
        elif case == "format":
            fixture.catalog.write_bytes(fixture.catalog.read_bytes() + b"# extra scaffolding\n")
        elif case == "summary-citation":
            text = fixture.summary.read_text(encoding="utf-8")
            fixture.summary.write_text(text.replace(str(fixture.cache), "/inconsistent/prior-cache"), encoding="utf-8")
        else:
            generator.write_shop_data(catalog, fixture.catalog)

    def test_full_check_preserves_exact_nonprovenance_bytes_and_relative_filenames(self):
        cases = ("lookalike", "shop-filename", "stock-filename", "excluded-filename", "outside-root", "price", "ledger-fact", "format", "summary-citation")
        for case in cases:
            with self.subTest(case=case):
                fixture = self.fixture(case, generated=True)
                self.alter_nonprovenance_output(fixture, case)
                before = fixture.state()
                result = fixture.invoke("--check")
                self.assertNotEqual(result[0], 0)
                self.assertNotIn("unrecognized arguments", result[2])
                self.assertEqual(fixture.state(), before)

    def test_relocation_does_not_normalize_root_lookalikes_in_names(self):
        first = self.fixture("first")
        fixture = self.fixture("relocated")
        raw = json.loads((fixture.shops / "fixture_shop.json").read_text(encoding="utf-8"))
        raw["name"] = str(fixture.shops / "lookalike")
        for source in (first, fixture):
            _json_write(source.shops / "fixture_shop.json", raw)
        self.assert_success(first.invoke())
        first.seed_manifest()
        fixture.catalog, fixture.ledger, fixture.summary = first.outputs
        _json_write(fixture.manifest, json.loads(first.manifest.read_text(encoding="utf-8")))
        catalog = _catalog(fixture.catalog)
        catalog["shops"][0]["display_name"] = str(first.shops / "lookalike")
        catalog["shops"][0]["source_name"] = str(first.shops / "lookalike")
        generator.write_shop_data(catalog, fixture.catalog)
        ledger = json.loads(fixture.ledger.read_text(encoding="utf-8"))
        ledger["shops"][1]["name"] = str(first.shops / "lookalike")
        _json_write(fixture.ledger, ledger)
        self.assertEqual(first.digests(), fixture.digests())
        before = fixture.state()
        result = fixture.invoke("--check")
        self.assertNotEqual(result[0], 0)
        self.assertNotIn("unrecognized arguments", result[2])
        self.assertEqual(fixture.state(), before)

    def test_missing_outputs_and_invalid_prior_provenance_are_differences_then_replaced(self):
        cases = ("catalog", "ledger", "summary", "invalid-json", "missing-root", "extra-root", "nonstr-root")
        for case in cases:
            with self.subTest(case=case):
                fixture = self.fixture(case, generated=True)
                if case in {"catalog", "ledger", "summary"}:
                    getattr(fixture, case).unlink()
                elif case == "invalid-json":
                    fixture.ledger.write_text("not-json", encoding="utf-8")
                else:
                    ledger = json.loads(fixture.ledger.read_text(encoding="utf-8"))
                    if case == "missing-root":
                        del ledger["source_roots"]["darkan_cache"]
                    elif case == "extra-root":
                        ledger["source_roots"]["extra"] = "unexpected"
                    else:
                        ledger["source_roots"]["darkan_cache"] = 7
                    _json_write(fixture.ledger, ledger)
                before = fixture.state()
                result = fixture.invoke("--check")
                self.assertNotEqual(result[0], 0)
                self.assertNotIn("unrecognized arguments", result[2])
                self.assertEqual(fixture.state(), before)
                self.assert_success(fixture.invoke())
                self.assert_success(fixture.invoke("--check"))

    def test_output_io_errors_are_errors_and_preserve_manifest(self):
        fixture = self.fixture(generated=True)
        fixture.catalog.unlink()
        fixture.catalog.mkdir()
        manifest_before = fixture.manifest.read_bytes()
        for flags in ((), ("--check",)):
            with self.subTest(flags=flags):
                result = fixture.invoke(*flags)
                self.assertNotEqual(result[0], 0)
                self.assertIsInstance(result[1], OSError)
                self.assertEqual(fixture.manifest.read_bytes(), manifest_before)

    def prepare_partial(self, fixture, mode):
        catalog = _catalog(fixture.catalog)
        ledger = json.loads(fixture.ledger.read_text(encoding="utf-8"))
        if mode in {"services-only", "vendor-actions-only"}:
            key = "services" if mode == "services-only" else "vendor_actions"
            catalog[key] = []
            ledger[key] = []
        elif mode == "stock-exclusions-only":
            shop = deepcopy(catalog["shops"][0])
            shop["id"] = "papa_mambos_shop"
            excluded = deepcopy(shop["stock"][0])
            excluded.update({"id": "papa_mambos_shop:1:19897", "item_id": 19897, "item_name": "Erzille seed"})
            shop["stock"].append(excluded)
            catalog["shops"].append(shop)
            ledger_shop = deepcopy(ledger["shops"][1])
            ledger_shop["id"] = shop["id"]
            ledger_shop["stock_rows"].append({**deepcopy(ledger_shop["stock_rows"][0]), "item_id": 19897})
            ledger["shops"].append(ledger_shop)
        else:
            catalog["currencies"][0]["implemented"] = False
            catalog["shops"][0].update({"currency_implemented": False, "visibility": "visible_locked", "lock_reason": "currency_not_implemented"})
            catalog["shops"][0]["stock"][0].update({"visibility": "visible_locked", "lock_reason": "currency_not_implemented", "disposition": "locked"})
            ledger["shops"][1].update({"reason": "currency_not_implemented", "disposition": "locked"})
            ledger["shops"][1]["stock_rows"][0].update({"visibility": "visible_locked", "lock_reason": "currency_not_implemented", "disposition": "locked"})
        generator.write_shop_data(catalog, fixture.catalog)
        _json_write(fixture.ledger, ledger)
        generator.write_summary(ledger, fixture.summary)
        return catalog, ledger

    def check_stock_exclusion_change(self, expected, after):
        rows = next(shop for shop in after["shops"] if shop["id"] == "papa_mambos_shop")["stock"]
        self.assertEqual([row["item_id"] for row in rows], [100])
        for shop in expected["shops"]:
            if shop["id"] == "papa_mambos_shop":
                shop["stock"] = [row for row in shop["stock"] if row["item_id"] != 19897]
        summary_keys = {
            "stock_row_count", "excluded_stock_row_count", "live_stock_row_count", "locked_stock_row_count",
            "hidden_stock_row_count", "blocked_stock_row_count",
        }
        expected["summary"].update({key: after["summary"][key] for key in summary_keys})
        self.assertEqual(after["summary"]["excluded_stock_row_count"], 1)
        self.assertEqual(after["summary"]["stock_row_count"], sum(len(shop["stock"]) for shop in expected["shops"]))

    def assert_partial_change(self, mode, before, after):
        expected = deepcopy(before)
        if mode == "services-only":
            self.assertEqual(before["services"], [])
            self.assertTrue(after["services"])
            expected["services"] = after["services"]
            expected["summary"]["service_count"] = len(after["services"])
        elif mode == "vendor-actions-only":
            self.assertEqual(before["vendor_actions"], [])
            self.assertTrue(after["vendor_actions"])
            expected["vendor_actions"] = after["vendor_actions"]
            expected["summary"]["vendor_action_count"] = len(after["vendor_actions"])
        elif mode == "stock-exclusions-only":
            self.check_stock_exclusion_change(expected, after)
        else:
            self.assertTrue(after["shops"][0]["currency_implemented"])
            self.assertEqual(after["shops"][0]["stock"][0]["visibility"], "visible")
            expected["currencies"][0]["implemented"] = True
            expected["shops"][0].update({"currency_implemented": True, "visibility": "visible", "lock_reason": ""})
            expected["shops"][0]["stock"][0].update({"visibility": "visible", "lock_reason": "", "disposition": "live"})
            summary_keys = {
                "visible_shop_count", "locked_shop_count", "hidden_shop_count", "live_stock_row_count",
                "locked_stock_row_count", "hidden_stock_row_count", "blocked_stock_row_count",
            }
            expected["summary"].update({key: after["summary"][key] for key in summary_keys})
        self.assertEqual(after, expected)

    def test_each_partial_mode_keeps_owned_behavior_without_full_sources_or_manifest_writes(self):
        for mode, manifest_exists, explicit_manifest in product(PARTIAL_MODES, (False, True), (False, True)):
            with self.subTest(mode=mode, manifest_exists=manifest_exists, explicit_manifest=explicit_manifest):
                fixture = self.fixture(f"{mode}-{manifest_exists}-{explicit_manifest}", generated=True)
                before_catalog, before_ledger = self.prepare_partial(fixture, mode)
                self.remove_full_sources(fixture, mode)
                if not manifest_exists:
                    fixture.manifest.unlink()
                manifest_before = fixture.state()[fixture.manifest]
                real_glob = Path.glob

                def no_raw_enumeration(path, pattern):
                    if path == fixture.raw or fixture.raw in path.parents:
                        raise AssertionError(f"Partial mode enumerated raw inputs: {path}")
                    return real_glob(path, pattern)

                flags = [f"--{mode}"]
                if explicit_manifest:
                    flags.extend(("--digest-manifest", str(fixture.manifest)))
                with patch.object(Path, "glob", no_raw_enumeration):
                    self.assert_success(fixture.invoke(*flags))
                self.assertEqual(fixture.calls, [])
                self.assertEqual(fixture.state()[fixture.manifest], manifest_before)
                after_catalog = _catalog(fixture.catalog)
                self.assert_partial_change(mode, before_catalog, after_catalog)
                after_ledger = json.loads(fixture.ledger.read_text(encoding="utf-8"))
                expected = deepcopy(before_ledger)
                expected["summary"] = after_catalog["summary"]
                if mode in {"services-only", "vendor-actions-only"}:
                    key = "services" if mode == "services-only" else "vendor_actions"
                    expected[key] = after_catalog[key]
                elif mode == "stock-exclusions-only":
                    expected["shops"][-1]["stock_rows"][-1].update({
                        "disposition": "excluded", "visibility": "hidden", "lock_reason": "period_source_exclusion",
                        "exclusion_source": generator.SHOP_STOCK_EXCLUSION_SOURCES["papa_mambos_shop"],
                    })
                else:
                    expected["shops"][1].update({"reason": "", "disposition": "visible"})
                    expected["shops"][1]["stock_rows"][0].update({"visibility": "visible", "lock_reason": "", "disposition": "live"})
                self.assertEqual(after_ledger, expected)

    def remove_full_sources(self, fixture, mode):
        metadata = fixture.items.read_bytes()
        shutil.rmtree(fixture.raw)
        if mode in {"services-only", "vendor-actions-only"}:
            fixture.items.parent.mkdir(parents=True)
            fixture.items.write_bytes(metadata)

    def test_partial_acceptance_is_rejected_before_reading_existing_inputs(self):
        for mode in PARTIAL_MODES:
            with self.subTest(mode=mode):
                fixture = self.fixture(mode)
                fixture.seed_manifest()
                shutil.rmtree(fixture.raw)
                before = fixture.state()
                result = fixture.invoke(f"--{mode}", "--accept-source-change")
                self.assert_refused(fixture, before, result)
                self.assertNotIsInstance(result[1], FileNotFoundError)
                self.assertIn("--accept-source-change", str(result[1]) + result[2])
                self.assertRegex((str(result[1]) + result[2]).lower(), f"partial|{mode}")

    def test_partial_check_stages_only_outputs_and_keeps_existing_input_paths(self):
        for mode in PARTIAL_MODES:
            with self.subTest(mode=mode):
                fixture = self.fixture(mode, generated=True)
                self.prepare_partial(fixture, mode)
                self.remove_full_sources(fixture, mode)
                before = fixture.state()
                result = fixture.invoke(f"--{mode}", "--check")
                self.assertNotEqual(result[0], 0)
                self.assertNotIn("unrecognized arguments", result[2])
                self.assertEqual(fixture.state(), before)

                self.assertEqual(fixture.calls, [])
                self.assert_success(fixture.invoke(f"--{mode}"))
                fixture.age_outputs()
                before = fixture.state()
                self.assert_success(fixture.invoke(f"--{mode}", "--check"))
                self.assertEqual(fixture.state(), before)

    def test_partial_check_creates_no_final_output_parent(self):
        for mode in PARTIAL_MODES:
            with self.subTest(mode=mode):
                fixture = self.fixture(mode, generated=True)
                existing_catalog, existing_ledger = fixture.catalog, fixture.ledger
                fixture.catalog = fixture.root / "new-catalog/catalog.py"
                fixture.ledger = fixture.root / "new-ledger/ledger.json"
                fixture.summary = fixture.root / "new-summary/summary.md"
                self.remove_full_sources(fixture, mode)
                before = fixture.state()
                result = fixture.invoke(
                    f"--{mode}", "--check", "--existing-shop-data", str(existing_catalog),
                    "--existing-ledger", str(existing_ledger),
                )
                self.assertNotEqual(result[0], 0)
                self.assertNotIn("unrecognized arguments", result[2])
                self.assertEqual(fixture.state(), before)
                self.assertFalse(any(path.parent.exists() for path in fixture.outputs))
                self.assertEqual(fixture.calls, [])

    def test_partial_precedence_remains_exclusions_then_vendor_or_services_then_currency(self):
        cases = (
            (PARTIAL_MODES, "stock-exclusions-only"),
            (("services-only", "vendor-actions-only", "currency-activation-only"), "vendor-actions-only"),
            (("services-only", "currency-activation-only"), "services-only"),
        )
        for index, (modes, chosen) in enumerate(cases):
            with self.subTest(modes=modes):
                fixture = self.fixture(str(index), generated=True)
                before, _ = self.prepare_partial(fixture, chosen)
                self.assert_success(fixture.invoke(*(f"--{mode}" for mode in modes)))
                self.assert_partial_change(chosen, before, _catalog(fixture.catalog))
                self.assertEqual(fixture.calls, [])

    def test_partial_check_does_not_apply_full_provenance_adjustment(self):
        fixture = self.fixture(generated=True)
        existing_catalog = fixture.root / "existing/catalog.py"
        existing_ledger = fixture.root / "existing/ledger.json"
        existing_catalog.parent.mkdir()
        shutil.copyfile(fixture.catalog, existing_catalog)
        shutil.copyfile(fixture.ledger, existing_ledger)
        ledger = json.loads(fixture.ledger.read_text(encoding="utf-8"))
        ledger["source_roots"]["darkan_cache"] = "/historical/cache"
        _json_write(fixture.ledger, ledger)
        generator.write_summary(ledger, fixture.summary)
        before = fixture.state()
        result = fixture.invoke(
            "--services-only", "--check", "--existing-shop-data", str(existing_catalog),
            "--existing-ledger", str(existing_ledger),
        )
        self.assertNotEqual(result[0], 0)
        self.assertNotIn("unrecognized arguments", result[2])
        self.assertEqual(fixture.state(), before)

    def test_value_comparator_reports_sorted_changes_and_accepts_only_digest_override(self):
        fixture = self.fixture()
        fixture.seed_manifest()
        compare = source_digests.check_source_digest_values
        original = fixture.digests()
        self.assertEqual(compare(fixture.manifest, OUTPUT_NAME, original), original)
        changed = {**original, "z-added": "new", "a-added": "new"}
        del changed["game-main/data/cfg/items.yml"]
        before = fixture.manifest.read_bytes()
        with self.assertRaisesRegex(ValueError, "a-added, game-main/data/cfg/items.yml, z-added; pass --accept-source-change"):
            compare(fixture.manifest, OUTPUT_NAME, changed)
        self.assertEqual(compare(fixture.manifest, OUTPUT_NAME, changed, accept_source_change=True), changed)
        self.assertEqual(fixture.manifest.read_bytes(), before)
        self.assertEqual(compare(fixture.manifest, "unrecorded", changed), changed)

    def test_existing_byte_map_interface_delegates_to_value_comparison(self):
        fixture = self.fixture()
        fixture.seed_manifest(include_npc=False)
        compare = source_digests.check_source_digest_values
        with patch.object(source_digests, "check_source_digest_values", wraps=compare) as checked:
            result = source_digests.check_source_digests(
                fixture.manifest, OUTPUT_NAME, {fixture.items: fixture.items.read_bytes()}, source_root=fixture.raw,
            )
        expected = {"game-main/data/cfg/items.yml": hashlib.sha256(fixture.items.read_bytes()).hexdigest()}
        self.assertEqual(result, expected)
        checked.assert_called_once_with(fixture.manifest, OUTPUT_NAME, expected, accept_source_change=False)
