"""Safety stops and real Collection persistence for the native fixture helper."""

import json
from pathlib import Path
import tempfile
import types
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core import constants, storage_pure
from ankiscape.tools.native.review_fixture import prepare_state_fixture

try:
    from anki.collection import Collection
except ImportError:
    Collection = None


class _PathOnlyCollection:
    def __init__(self, path):
        self.path = str(path)

    def __getattr__(self, name):
        raise AssertionError(f"Collection access before the path guard: {name}")


class NativeReviewFixtureTests(unittest.TestCase):
    def test_wrong_path_and_symlink_escape_stop_before_collection_access(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / "base"
            base.mkdir()
            outside = root / "outside.anki2"
            outside.write_bytes(b"untouched collection sentinel")
            escaped = base / "collection.anki2"
            escaped.symlink_to(outside)
            for path, requested_base in (
                (outside, str(base)),
                (escaped, str(base)),
                (outside, "/"),
                (outside, "relative/base"),
            ):
                with self.subTest(path=path, requested_base=requested_base):
                    mw = types.SimpleNamespace(col=_PathOnlyCollection(path))
                    with self.assertRaises(ValueError):
                        prepare_state_fixture(mw, disposable_base=requested_base)
            self.assertEqual(outside.read_bytes(), b"untouched collection sentinel")

    @unittest.skipIf(Collection is None, "Anki Collection is unavailable")
    def test_real_fixture_survives_reopen_and_refuses_reseeding(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            profile = base / "Canary"
            profile.mkdir()
            path = profile / "collection.anki2"
            collection = Collection(str(path))
            try:
                collection.set_config(
                    "ankiscape_player_data",
                    storage_pure.default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS),
                )
                collection.set_config("ankiscape_current_skill", "None")
                report = prepare_state_fixture(
                    types.SimpleNamespace(col=collection), disposable_base=str(base)
                )
            finally:
                collection.close()

            collection = Collection(str(path))
            try:
                expected = storage_pure.default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
                expected["inventory"]["Logs"] = 1
                expected["inventory"]["Ashes"] = 0
                expected["firemaking_level"] = 1
                expected["firemaking_exp"] = 0
                expected["current_firemaking"] = "logs"
                # Collection.set_config persists the complete state as JSON.
                expected = json.loads(json.dumps(expected))
                self.assertEqual(collection.get_config("ankiscape_player_data"), expected)
                self.assertEqual(collection.get_config("ankiscape_current_skill"), "None")
                self.assertEqual(collection.note_count(), 20)
                self.assertEqual(len(collection.find_cards(f"did:{report['deck_id']}")), 20)
                for number, note_id in enumerate(report["note_ids"], 1):
                    note = collection.get_note(note_id)
                    self.assertEqual(note["Front"], f"AnkiScape state acceptance {number:02d}")
                with self.assertRaisesRegex(ValueError, "no existing notes"):
                    prepare_state_fixture(
                        types.SimpleNamespace(col=collection), disposable_base=str(base)
                    )
                self.assertEqual(collection.note_count(), 20)
                self.assertEqual(collection.get_config("ankiscape_player_data"), expected)
            finally:
                collection.close()
