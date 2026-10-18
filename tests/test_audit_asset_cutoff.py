import importlib.util
import json
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "audit_asset_cutoff.py"
SPEC = importlib.util.spec_from_file_location("audit_asset_cutoff_tool", TOOL_PATH)
audit_asset_cutoff = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["audit_asset_cutoff_tool"] = audit_asset_cutoff
SPEC.loader.exec_module(audit_asset_cutoff)


class AuditAssetCutoffTest(unittest.TestCase):
    def test_history_request_uses_supported_cutoff_parameters(self):
        queries = []
        earlier = {
            "timestamp": "2011-11-29T14:12:02Z", "sha1": "earlier", "size": 100,
            "url": "https://example.invalid/archive/Sprite.png",
        }

        class Client:
            def _request_json(self, url):
                params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
                queries.append(params)
                if "iidir" in params:
                    return {"error": {"code": "unrecognizedparam", "info": "Unrecognized parameter: iidir."}}
                return {"query": {"pages": [{"title": "File:Sprite.png", "imageinfo": [earlier]}]}}

        with patch.object(audit_asset_cutoff.time, "sleep", return_value=None):
            payload = audit_asset_cutoff._request_batch(
                Client(), audit_asset_cutoff.RS3_WIKI, ["Sprite.png"], audit_asset_cutoff.PRE_EOC_CUTOFF,
            )
        result = audit_asset_cutoff._batch_results(payload, ["Sprite.png"], audit_asset_cutoff.PRE_EOC_CUTOFF)
        self.assertEqual(result["Sprite.png"]["status"], "revision")
        self.assertEqual(result["Sprite.png"]["earlier_revision"]["timestamp"], earlier["timestamp"])
        self.assertEqual(len(queries), 1)
        self.assertEqual(queries[0]["iistart"], [audit_asset_cutoff.PRE_EOC_CUTOFF])
        self.assertEqual(queries[0]["iilimit"], ["1"])
        self.assertNotIn("iidir", queries[0])

    def test_history_api_error_remains_unresolved_after_four_attempts(self):
        calls = []

        class Client:
            def _request_json(self, url):
                calls.append(url)
                return {"error": {"code": "maxlag", "info": "lagged"}}

        with (
            patch.object(audit_asset_cutoff.time, "sleep", return_value=None),
            self.assertRaisesRegex(audit_asset_cutoff.AssetFetchError, "after 4 attempts:.*maxlag: lagged"),
        ):
            audit_asset_cutoff._request_batch(
                Client(), audit_asset_cutoff.RS3_WIKI, ["Sprite.png"], audit_asset_cutoff.PRE_EOC_CUTOFF,
            )
        self.assertEqual(len(calls), 4)

    @staticmethod
    def _missing_cross_wiki_paths(report):
        assets = report.get("assets")
        if not isinstance(assets, dict):
            return []
        return sorted(
            path
            for path, row in assets.items()
            if isinstance(row, dict)
            and row.get("source_lookup", {}).get("wiki") == "osrs"
            and row.get("source_lookup", {}).get("status")
            == audit_asset_cutoff.NO_EARLIER_REVISION
            and not isinstance(row.get("cross_wiki_lookup"), dict)
        )

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

        missing_cross_wiki = self._missing_cross_wiki_paths(report)
        self.assertEqual(
            missing_cross_wiki,
            [],
            "OSRS source lookups missing an RS3 cross-wiki result: "
            f"{', '.join(missing_cross_wiki)}",
        )

        class NoRevisionClient:
            def _request_json(self, url):
                return {
                    "query": {
                        "pages": [
                            {
                                "title": "File:Sprite.png",
                                "imageinfo": [],
                            }
                        ]
                    }
                }

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            temp_provenance = temp_root / "assets_provenance.json"
            temp_report = temp_root / "report.json"
            temp_provenance.write_text(
                json.dumps(
                    {
                        "sprite.png": {
                            "file_title": "Sprite.png",
                            "source_wiki": "osrs",
                            "image_url": "https://example.invalid/Sprite.png",
                            "sha1": "recorded",
                            "size": 200,
                            "timestamp": "2020-01-01T00:00:00Z",
                        }
                    }
                ),
                encoding="utf-8",
            )
            generated = audit_asset_cutoff.audit_assets(
                temp_provenance,
                temp_report,
                audit_asset_cutoff.PRE_EOC_CUTOFF,
                40,
                NoRevisionClient(),
            )

        missing_cross_wiki = self._missing_cross_wiki_paths(generated)
        self.assertEqual(
            missing_cross_wiki,
            [],
            "OSRS source lookups missing an RS3 cross-wiki result: "
            f"{', '.join(missing_cross_wiki)}",
        )


if __name__ == "__main__":
    unittest.main()
