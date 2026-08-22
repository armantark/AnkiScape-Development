import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "audit_asset_cutoff.py"
SPEC = importlib.util.spec_from_file_location("audit_asset_cutoff_tool", TOOL_PATH)
audit_asset_cutoff = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["audit_asset_cutoff_tool"] = audit_asset_cutoff
SPEC.loader.exec_module(audit_asset_cutoff)


class AuditAssetCutoffTest(unittest.TestCase):
    def test_classification_distinguishes_absent_identical_and_different_revisions(self):
        self.assertEqual(
            audit_asset_cutoff.classify_revision("recorded", None),
            audit_asset_cutoff.NO_EARLIER_REVISION,
        )
        self.assertEqual(
            audit_asset_cutoff.classify_revision("same", {"sha1": "same"}),
            audit_asset_cutoff.BYTE_IDENTICAL,
        )
        self.assertEqual(
            audit_asset_cutoff.classify_revision("recorded", {"sha1": "earlier"}),
            audit_asset_cutoff.DIFFERENT,
        )

    def test_differing_row_keeps_both_revision_measurements(self):
        entry = {
            "file_title": "Sprite.png",
            "source_wiki": "rs3",
            "image_url": "https://example.invalid/Sprite.png",
            "sha1": "recorded",
            "size": 200,
            "timestamp": "2020-01-01T00:00:00Z",
        }
        earlier = {
            "archive_url": "https://example.invalid/archive/Sprite.png",
            "sha1": "earlier",
            "size": 100,
            "timestamp": "2012-01-01T00:00:00Z",
        }

        row = audit_asset_cutoff._make_row(
            entry,
            audit_asset_cutoff.WIKI_SOURCES_BY_NAME["rs3"],
            {"status": "revision", "earlier_revision": earlier},
        )

        self.assertEqual(row["status"], audit_asset_cutoff.DIFFERENT)
        self.assertEqual(
            row["recorded_revision"],
            {
                "image_url": entry["image_url"],
                "sha1": "recorded",
                "size": 200,
                "timestamp": "2020-01-01T00:00:00Z",
            },
        )
        self.assertEqual(row["earlier_revision"], earlier)


if __name__ == "__main__":
    unittest.main()
