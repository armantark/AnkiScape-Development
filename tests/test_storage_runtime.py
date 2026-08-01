"""Runtime persistence regressions that need an Anki-like collection facade."""
from __future__ import annotations

import importlib.util
import json
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
                "config_version": 105,
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


if __name__ == "__main__":
    unittest.main()
