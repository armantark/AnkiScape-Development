import importlib.util
import json
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

    def test_batch_results_rejects_a_post_cutoff_revision(self):
        payload = {
            "query": {
                "pages": [
                    {
                        "title": "File:Sprite.png",
                        "imageinfo": [
                            {
                                "timestamp": "2013-01-01T00:00:00Z",
                                "sha1": "later",
                                "size": 100,
                                "url": "https://example.invalid/Sprite.png",
                            }
                        ],
                    }
                ]
            }
        }

        results = audit_asset_cutoff._batch_results(
            payload,
            ["Sprite.png"],
            audit_asset_cutoff.PRE_EOC_CUTOFF,
        )

        self.assertEqual(
            results["Sprite.png"],
            {
                "status": audit_asset_cutoff.UNRESOLVED,
                "reason": (
                    "The pre-cutoff revision lacks a valid timestamp, SHA-1, "
                    "size, or URL."
                ),
            },
        )

    def test_batch_results_follows_normalized_redirected_titles(self):
        earlier = {
            "timestamp": "2012-01-01T00:00:00Z",
            "sha1": "earlier",
            "size": 100,
            "url": "https://example.invalid/archive/Sprite.png",
        }
        payload = {
            "query": {
                "normalized": [
                    {"from": "File:sprite.png", "to": "File:Sprite.png"}
                ],
                "redirects": [
                    {
                        "from": "File:Sprite.png",
                        "to": "File:Historical sprite.png",
                    }
                ],
                "pages": [
                    {"title": "File:Historical sprite.png", "imageinfo": [earlier]}
                ],
            }
        }

        results = audit_asset_cutoff._batch_results(
            payload,
            ["sprite.png"],
            audit_asset_cutoff.PRE_EOC_CUTOFF,
        )

        self.assertEqual(
            results["sprite.png"],
            {
                "status": "revision",
                "earlier_revision": {
                    "archive_url": earlier["url"],
                    "sha1": "earlier",
                    "size": 100,
                    "timestamp": "2012-01-01T00:00:00Z",
                },
            },
        )

    def test_cross_wiki_candidate_requires_identity_inspection(self):
        entry = {
            "file_title": "Sprite.png",
            "source_wiki": "osrs",
            "image_url": "https://example.invalid/Sprite.png",
            "sha1": "recorded",
            "size": 200,
            "timestamp": "2020-01-01T00:00:00Z",
        }
        row = audit_asset_cutoff._make_row(
            entry,
            audit_asset_cutoff.WIKI_SOURCES_BY_NAME["osrs"],
            {
                "status": audit_asset_cutoff.NO_EARLIER_REVISION,
                "reason": "No file revision exists at or before the cutoff.",
            },
        )

        audit_asset_cutoff._apply_cross_wiki_result(
            row,
            entry,
            {
                "status": "revision",
                "earlier_revision": {
                    "archive_url": "https://example.invalid/archive/Sprite.png",
                    "sha1": "earlier",
                    "size": 100,
                    "timestamp": "2012-01-01T00:00:00Z",
                },
            },
        )

        self.assertEqual(row["status"], audit_asset_cutoff.NEEDS_INSPECTION)
        self.assertEqual(row["source_lookup"]["wiki"], "osrs")
        self.assertEqual(row["source_lookup"]["status"], "no_earlier_revision")
        self.assertEqual(row["cross_wiki_lookup"]["wiki"], "rs3")
        self.assertEqual(row["cross_wiki_lookup"]["status"], "different")

    def test_new_post_cutoff_provenance_requires_an_audit_row(self):
        provenance = json.loads(
            (ROOT / "assets_provenance.json").read_text(encoding="utf-8")
        )
        report = json.loads(
            (
                ROOT
                / "memory-bank"
                / "source-audits"
                / "post-cutoff-asset-revisions-2026-08-21.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            report.get("cutoff_timestamp"),
            audit_asset_cutoff.PRE_EOC_CUTOFF,
        )

        missing = audit_asset_cutoff.unreported_post_cutoff_paths(
            provenance,
            report,
        )

        self.assertEqual(
            missing,
            [],
            "Post-cutoff provenance entries missing or stale in the committed asset "
            f"audit: {', '.join(missing)}",
        )


if __name__ == "__main__":
    unittest.main()
