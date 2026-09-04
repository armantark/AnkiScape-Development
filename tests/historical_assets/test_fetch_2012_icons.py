import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "tools" / "historical_assets" / "fetch_2012_icons.py"
FIXTURE_PATH = Path(__file__).with_name("fetch_2012_icons_history_fixture.json")
SPEC = importlib.util.spec_from_file_location("fetch_2012_icons_tool", TOOL_PATH)
fetch_2012_icons = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["fetch_2012_icons_tool"] = fetch_2012_icons
SPEC.loader.exec_module(fetch_2012_icons)


class HistoryClient:
    def __init__(self, responses, downloads=()):
        self.responses = list(responses)
        self.downloads = list(downloads)
        self.query_urls = []
        self.download_urls = []

    def _request_json(self, url):
        self.query_urls.append(url)
        return self.responses.pop(0)

    def download_bytes(self, url):
        self.download_urls.append(url)
        return self.downloads.pop(0)


class Fetch2012IconsTest(unittest.TestCase):
    def test_selects_newest_revision_strictly_before_cutoff(self):
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        selected = fetch_2012_icons.select_newest_revision(fixture["mixed"])

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected["sha1"], "newest-before-cutoff")
        self.assertIsNone(
            fetch_2012_icons.select_newest_revision(fixture["at_or_after"])
        )

    def test_offset_timestamps_are_compared_in_utc(self):
        revisions = [
            {
                "sha1": "equal-in-utc",
                "timestamp": "2012-11-19T19:00:00-05:00",
            },
            {
                "sha1": "one-second-before",
                "timestamp": "2012-11-19T18:59:59-05:00",
            },
        ]

        selected = fetch_2012_icons.select_newest_revision(revisions)

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected["sha1"], "one-second-before")

    def test_history_query_follows_pagination_and_requests_redirects(self):
        client = HistoryClient(
            [
                {
                    "continue": {"continue": "-||", "iicontinue": "next-page"},
                    "query": {
                        "pages": {
                            "1": {
                                "title": "File:Example.png",
                                "imageinfo": [
                                    {
                                        "sha1": "post-cutoff",
                                        "timestamp": "2014-01-01T00:00:00Z",
                                        "url": "https://runescape.wiki/images/Example.png",
                                    }
                                ],
                            }
                        }
                    },
                },
                {
                    "query": {
                        "pages": {
                            "1": {
                                "title": "File:example.png",
                                "imageinfo": [
                                    {
                                        "archivename": "20121101000000!example.png",
                                        "sha1": "pre-cutoff",
                                        "timestamp": "2012-11-01T00:00:00Z",
                                        "url": "https://runescape.wiki/images/archive/20121101000000%21example.png",
                                    }
                                ],
                            }
                        }
                    }
                },
            ]
        )

        revision, reason = fetch_2012_icons.query_pre_cutoff_revision(
            client, "Example.png"
        )

        self.assertEqual(reason, "")
        self.assertIsNotNone(revision)
        assert revision is not None
        self.assertEqual(revision.file_title, "example.png")
        self.assertEqual(revision.sha1, "pre-cutoff")
        self.assertEqual(len(client.query_urls), 2)
        first_query = urllib.parse.parse_qs(
            urllib.parse.urlsplit(client.query_urls[0]).query
        )
        second_query = urllib.parse.parse_qs(
            urllib.parse.urlsplit(client.query_urls[1]).query
        )
        self.assertEqual(first_query["redirects"], ["1"])
        self.assertEqual(second_query["iicontinue"], ["next-page"])

    def test_hash_mismatch_is_missing_and_leaves_asset_untouched(self):
        expected_bytes = b"expected archive bytes"
        expected_sha1 = hashlib.sha1(expected_bytes).hexdigest()
        revision_payload = {
            "query": {
                "pages": {
                    "1": {
                        "title": "File:Example.png",
                        "imageinfo": [
                            {
                                "archivename": "20120101000000!Example.png",
                                "sha1": expected_sha1,
                                "timestamp": "2012-01-01T00:00:00Z",
                                "url": "https://runescape.wiki/images/archive/20120101000000%21Example.png",
                            }
                        ],
                    }
                }
            }
        }
        client = HistoryClient(
            [revision_payload],
            downloads=[b"wrong"] * fetch_2012_icons.DOWNLOAD_ATTEMPTS,
        )
        provenance_entry = {
            "file_page_url": "https://oldschool.runescape.wiki/wiki/File:Example.png",
            "file_title": "Example.png",
            "image_url": "https://oldschool.runescape.wiki/images/Example.png",
            "sha1": "old-source",
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            asset_path = root / "shopitems" / "example.png"
            asset_path.parent.mkdir()
            asset_path.write_bytes(b"original local asset")
            provenance_path = root / "assets_provenance.json"
            provenance_path.write_text(
                json.dumps({"shopitems/example.png": provenance_entry}),
                encoding="utf-8",
            )
            audit_path = root / "audit.md"
            checkpoint_path = root / "tmp" / "checkpoint.json"

            with mock.patch.object(fetch_2012_icons, "REPO_ROOT", root):
                counts = fetch_2012_icons.run_sweep(
                    provenance_path, audit_path, checkpoint_path, client
                )

            self.assertEqual(counts, {"fetched": 0, "unchanged": 0, "missing": 1})
            self.assertEqual(asset_path.read_bytes(), b"original local asset")
            self.assertEqual(
                json.loads(provenance_path.read_text(encoding="utf-8")),
                {"shopitems/example.png": provenance_entry},
            )
            audit_rows = [
                line
                for line in audit_path.read_text(encoding="utf-8").splitlines()
                if line.startswith("| `")
            ]
            wrong_sha1 = hashlib.sha1(b"wrong").hexdigest()
            self.assertEqual(
                audit_rows,
                [
                    "| `shopitems/example.png` | `File:Example.png` | "
                    f"Archive SHA-1 mismatch after 4 attempts: expected "
                    f"{expected_sha1}, last got {wrong_sha1}. |"
                ],
            )
            self.assertEqual(len(client.download_urls), 4)
            self.assertTrue(all("%21" not in url for url in client.download_urls))
            self.assertTrue(all("!Example.png" in url for url in client.download_urls))

    def test_already_replaced_asset_is_a_no_op(self):
        written_bytes = b"already normalized PNG bytes"
        written_sha1 = hashlib.sha1(written_bytes).hexdigest()

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "example.png"
            output_path.write_bytes(written_bytes)
            with mock.patch.object(
                fetch_2012_icons,
                "write_png",
                side_effect=AssertionError("normalization must not run"),
            ), mock.patch.object(
                fetch_2012_icons,
                "write_source_png",
                side_effect=AssertionError("source write must not run"),
            ):
                changed, result_bytes = fetch_2012_icons._replace_asset(
                    output_path,
                    b"source bytes",
                    written_sha1,
                    already_current=True,
                )

        self.assertFalse(changed)
        self.assertEqual(result_bytes, written_bytes)
        revision = fetch_2012_icons.HistoricalRevision(
            file_title="Example.png",
            image_url="https://runescape.wiki/images/Example.png",
            timestamp="2012-01-01T00:00:00Z",
            sha1="api-source-sha1",
            archivename="",
        )
        provenance = fetch_2012_icons._provenance_entry(revision, written_bytes)
        self.assertEqual(provenance["sha1"], written_sha1)
        self.assertEqual(provenance["size"], len(written_bytes))
        self.assertNotIn("fetch_date", provenance)


if __name__ == "__main__":
    unittest.main()
