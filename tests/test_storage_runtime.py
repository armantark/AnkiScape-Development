"""Runtime persistence regressions that need an Anki-like collection facade."""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from anki.collection import Collection
except Exception:  # pragma: no cover - pure-Python test environment
    Collection = None


class DBError(Exception):
    pass


class _LegacyTextCollection:
    def __init__(self) -> None:
        self.values = {
            "ankiscape_player_data": {"config_version": 1, "coins": 7},
        }
        self.legacy_row = True
        self.db = self

    def get_config(self, key, default=None):
        return self.values.get(key, default)

    def set_config(self, key, value):
        if key == "ankiscape_player_data" and self.legacy_row:
            raise DBError('DbError { info: "InvalidColumnType(0, \'val\', Text)" }')
        self.values[key] = value

    def remove_config(self, key):
        self.values.pop(key, None)

    def execute(self, sql, key):
        if sql == "DELETE FROM config WHERE key = ?":
            self.values.pop(key, None)
            self.legacy_row = False


def _load_storage_module(collection):
    root = Path(__file__).resolve().parents[1]
    package_name = "ankiscape_storage_runtime_test"
    package = types.ModuleType(package_name)
    package.__path__ = [str(root)]
    sys.modules[package_name] = package

    aqt = types.ModuleType("aqt")
    aqt.mw = types.SimpleNamespace(col=collection)
    spec = importlib.util.spec_from_file_location(
        f"{package_name}.core.storage",
        root / "core" / "storage.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    with patch.dict(sys.modules, {"aqt": aqt}):
        spec.loader.exec_module(module)
    return module


class StorageRuntimeTest(unittest.TestCase):
    def test_save_repairs_legacy_text_config_without_losing_player_data(self):
        collection = _LegacyTextCollection()
        storage = _load_storage_module(collection)
        player_data = {"config_version": 72, "coins": 99}

        storage.save_player_data(player_data, "Agility")

        self.assertEqual(collection.values["ankiscape_player_data"], player_data)
        self.assertEqual(collection.values["ankiscape_current_skill"], "Agility")
        self.assertNotIn("ankiscape_player_data_recovery", collection.values)

    def test_load_uses_recovery_copy_when_canonical_row_is_missing(self):
        collection = _LegacyTextCollection()
        collection.values = {
            "ankiscape_player_data_recovery": {"config_version": 72, "coins": 13},
            "ankiscape_current_skill": "None",
        }
        storage = _load_storage_module(collection)

        player_data, current_skill = storage.load_player_data()

        self.assertEqual(player_data["coins"], 13)
        self.assertEqual(current_skill, "None")

    def test_load_does_not_activate_an_under_started_activity(self):
        collection = _LegacyTextCollection()
        collection.values = {
            "ankiscape_player_data": {
                "config_version": 104,
                "current_utility": "shooting_stars",
                "activity_session": {"active_id": ""},
            },
            "ankiscape_current_skill": "None",
        }
        collection.legacy_row = False
        storage = _load_storage_module(collection)

        player_data, current_skill = storage.load_player_data()

        self.assertEqual(player_data["current_utility"], "shooting_stars")
        self.assertEqual(player_data["activity_session"], {"active_id": ""})
        self.assertEqual(current_skill, "None")
        self.assertEqual(collection.values["ankiscape_current_skill"], "None")

    @unittest.skipIf(Collection is None, "Anki runtime is not installed")
    def test_real_anki_collection_repairs_text_backed_config_row(self):
        with tempfile.TemporaryDirectory() as directory:
            collection = Collection(str(Path(directory) / "collection.anki2"))
            try:
                collection.db.execute(
                    "INSERT OR REPLACE INTO config "
                    "(key, usn, mtime_secs, val) VALUES (?, ?, ?, ?)",
                    "ankiscape_player_data",
                    0,
                    0,
                    json.dumps({"config_version": 1, "coins": 7}),
                )
                storage = _load_storage_module(collection)
                player_data = {"config_version": 72, "coins": 99}

                storage.save_player_data(player_data, "Agility")

                self.assertEqual(
                    collection.db.scalar(
                        "SELECT typeof(val) FROM config WHERE key = ?",
                        "ankiscape_player_data",
                    ),
                    "blob",
                )
                self.assertEqual(
                    collection.get_config("ankiscape_player_data"), player_data
                )
                self.assertIsNone(
                    collection.get_config("ankiscape_player_data_recovery")
                )
            finally:
                collection.close()

    @unittest.skipIf(Collection is None, "Anki runtime is not installed")
    def test_next_game_write_after_full_sync_download_puts_back_the_old_save(self):
        """Pins the known defect: a full sync download loses the other device's save.

        The fix waits on the owner's choice (design-thread queue section 3.39).
        When it lands, the final assertion expects the downloaded 4500.0.

        This replays aqt 25.09.4 opening a profile whose automatic sync needs a
        full download: `loadProfile` fires `profile_did_open` (the legacy
        `profileLoaded` runs `load_player_data`) and only then syncs
        (`aqt/main.py` 568-569). `full_download` closes the collection, the
        backend replaces the file, and aqt reopens the same `Collection` object
        (`aqt/sync.py` 238-250), then fires `sync_did_finish` (`aqt/main.py`
        1107). The player then changes a target, which writes the save.
        """
        from tests.test_integration_smoke import (
            _DummyMW,
            _install_runtime_fakes,
            _load_addon_as_package,
        )

        original_modules = dict(sys.modules)
        self.addCleanup(sys.modules.update, original_modules)
        self.addCleanup(sys.modules.clear)

        with tempfile.TemporaryDirectory() as directory:
            server_path = Path(directory) / "ankiweb" / "collection.anki2"
            local_path = Path(directory) / "desktop" / "collection.anki2"
            server_path.parent.mkdir()
            local_path.parent.mkdir()
            server = Collection(str(server_path))
            server.set_config(
                "ankiscape_player_data", {"config_version": 1, "mining_exp": 4500.0}
            )
            server.close()
            collection = Collection(str(local_path))
            try:
                collection.set_config(
                    "ankiscape_player_data", {"config_version": 1, "mining_exp": 120.0}
                )
                _install_runtime_fakes()
                aqt = sys.modules["aqt"]
                aqt.mw = _DummyMW(collection)
                gui_hooks = aqt.gui_hooks
                for name in (
                    "sync_will_start",
                    "collection_will_temporarily_close",
                    "collection_did_temporarily_close",
                    "state_did_reset",
                    "sync_did_finish",
                ):
                    setattr(gui_hooks, name, [])

                def fire(hook, *args):
                    for callback in list(hook):
                        callback(*args)

                addon = _load_addon_as_package("ankiscape_full_sync_download")

                addon.load_player_data()
                fire(gui_hooks.sync_will_start)
                fire(gui_hooks.collection_will_temporarily_close, collection)
                collection.close()
                shutil.copyfile(server_path, local_path)
                collection.reopen()
                fire(gui_hooks.collection_did_temporarily_close, collection)
                fire(gui_hooks.state_did_reset)
                fire(gui_hooks.sync_did_finish)
                fire(gui_hooks.state_did_reset)
                self.assertEqual(
                    collection.get_config("ankiscape_player_data")["mining_exp"],
                    4500.0,
                )

                self.assertTrue(
                    addon._set_value("current_hunter", "catch_carrion_jadinko")
                )

                saved = collection.get_config("ankiscape_player_data")
                self.assertEqual(saved["current_hunter"], "catch_carrion_jadinko")
                self.assertEqual(
                    saved["mining_exp"],
                    120.0,
                    "the pre-download save in memory no longer overwrites the "
                    "downloaded save; flip this to 4500.0",
                )
            finally:
                if collection.db:
                    collection.close()


@unittest.skipIf(Collection is None, "Anki runtime is not installed")
class InterruptedLegacyRepairTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = str(Path(directory.name) / "collection.anki2")
        self.collection = Collection(self.path)
        self.addCleanup(lambda: self.collection.close())
        self.collection.db.execute(
            "INSERT OR REPLACE INTO config "
            "(key, usn, mtime_secs, val) VALUES (?, ?, ?, ?)",
            "ankiscape_player_data", 0, 0,
            json.dumps({"config_version": 72, "mining_exp": 7}),
        )
        self.storage = _load_storage_module(self.collection)
        self.player_data = {"config_version": 72, "mining_exp": 99}

    def _reopen(self):
        self.collection.close()
        self.collection = Collection(self.path)
        self.storage = _load_storage_module(self.collection)

    def test_real_interrupted_before_delete_preserves_both_copies(self):
        with patch.object(self.collection.db, "execute", side_effect=RuntimeError("interrupted")):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                self.storage.save_player_data(self.player_data, "Mining")

        self._reopen()
        primary = self.collection.db.scalar(
            "SELECT val FROM config WHERE key = ?", "ankiscape_player_data"
        )
        self.assertEqual(json.loads(primary)["mining_exp"], 7)
        self.assertEqual(self.collection.get_config("ankiscape_player_data_recovery")["mining_exp"], 99)
        loaded, skill = self.storage.load_player_data()
        self.assertEqual(loaded["mining_exp"], 99)
        self.storage.save_player_data(loaded, skill)
        self._reopen()
        self.assertEqual(self.storage.load_player_data()[0]["mining_exp"], 99)
        self.assertIsNone(self.collection.get_config("ankiscape_player_data_recovery"))

    def test_interrupted_after_delete_loads_recovery_copy(self):
        execute = self.collection.db.execute

        def delete_then_interrupt(*args):
            execute(*args)
            raise RuntimeError("interrupted")

        with patch.object(self.collection.db, "execute", side_effect=delete_then_interrupt):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                self.storage.save_player_data(self.player_data, "Mining")

        self._reopen()
        self.assertIsNone(self.collection.get_config("ankiscape_player_data"))
        self.assertEqual(self.storage.load_player_data()[0]["mining_exp"], 99)

    def test_later_save_preserves_newest_durable_copy_until_cleanup_succeeds(self):
        with patch.object(self.collection, "remove_config", side_effect=RuntimeError("interrupted")):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                self.storage.save_player_data(self.player_data, "Mining")
            self.player_data["mining_exp"] = 100
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                self.storage.save_player_data(self.player_data, "Mining")

        self._reopen()
        self.assertEqual(self.storage.load_player_data()[0]["mining_exp"], 100)
        self.player_data["mining_exp"] = 101
        with patch.object(self.collection, "set_config", side_effect=RuntimeError("interrupted")):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                self.storage.save_player_data(self.player_data, "Mining")

        self._reopen()
        loaded, skill = self.storage.load_player_data()
        self.assertEqual(loaded["mining_exp"], 100)
        self.storage.save_player_data(loaded, skill)
        self._reopen()
        self.assertEqual(self.storage.load_player_data()[0]["mining_exp"], 100)
        self.assertIsNone(self.collection.get_config("ankiscape_player_data_recovery"))

    def test_failed_recovery_write_preserves_existing_save(self):
        set_config = self.collection.set_config

        def fail_recovery(key, value):
            if key == "ankiscape_player_data_recovery":
                raise RuntimeError("recovery write failed")
            return set_config(key, value)

        with patch.object(self.collection, "set_config", side_effect=fail_recovery):
            with self.assertRaisesRegex(RuntimeError, "recovery write failed"):
                self.storage.save_player_data(self.player_data, "Mining")

        self._reopen()
        primary = self.collection.db.scalar(
            "SELECT val FROM config WHERE key = ?", "ankiscape_player_data"
        )
        self.assertEqual(json.loads(primary)["mining_exp"], 7)
        self.assertIsNone(self.collection.get_config("ankiscape_player_data_recovery"))

    def test_existing_repaired_primary_is_newer_than_leftover_recovery(self):
        self.collection.db.execute(
            "DELETE FROM config WHERE key = ?", "ankiscape_player_data"
        )
        self.collection.set_config("ankiscape_player_data_recovery", self.player_data)
        self.collection.set_config(
            "ankiscape_player_data", {"config_version": 72, "mining_exp": 100}
        )

        self._reopen()
        loaded, skill = self.storage.load_player_data()
        self.assertEqual(loaded["mining_exp"], 100)
        self.storage.save_player_data(loaded, skill)
        self._reopen()
        self.assertEqual(self.storage.load_player_data()[0]["mining_exp"], 100)
        self.assertIsNone(self.collection.get_config("ankiscape_player_data_recovery"))


if __name__ == "__main__":
    unittest.main()
