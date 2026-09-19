import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
FETCH_ASSETS_PATH = ROOT / "tools" / "fetch_assets.py"
SPEC = importlib.util.spec_from_file_location("fetch_assets_tool", FETCH_ASSETS_PATH)
fetch_assets = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["fetch_assets_tool"] = fetch_assets
SPEC.loader.exec_module(fetch_assets)

try:
    from PIL import Image

    HAS_PIL = True
except Exception:
    HAS_PIL = False


class FakeWikiClient:
    def __init__(self, hits):
        self.hits = hits
        self.queries = []
        self.downloads = []

    def query_image_info(self, source, file_title):
        self.queries.append((source.name, file_title))
        if (source.name, file_title) not in self.hits:
            return None
        return fetch_assets.ImageInfo(
            source_wiki=source.name,
            file_title=file_title,
            file_page_url=f"{source.page_base_url}/wiki/File:{file_title.replace(' ', '_')}",
            image_url=f"https://images.example/{source.name}/{file_title}",
            sha1="abc123",
            size=123,
            mime="image/png",
            timestamp="2026-05-29T00:00:00Z",
            mediatype="BITMAP",
            license_string="Jagex fan content",
        )

    def download_bytes(self, url):
        self.downloads.append(url)
        return b"not-used-in-dry-run-tests"


class TestFetchAssets(unittest.TestCase):
    @unittest.skipUnless(HAS_PIL, "Pillow is required for PNG normalization")
    def test_write_png_limits_visible_art_without_reintroducing_padding(self):
        source = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        for x in range(22, 42):
            for y in range(18, 47):
                source.putpixel((x, y), (255, 0, 0, 255))
        source.putpixel((0, 0), (255, 255, 255, 1))
        source_bytes = BytesIO()
        source.save(source_bytes, format="PNG")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "normalized.png"
            fetch_assets.write_png(source_bytes.getvalue(), output_path, size=64)
            with Image.open(output_path) as output:
                self.assertEqual(output.size, (20, 29))
                self.assertEqual(output.getchannel("A").getbbox(), (0, 0, 20, 29))

    def test_source_image_url_removes_wiki_optimization_query(self):
        image_url = "https://runescape.wiki/images/archive/example.png?ad092"
        self.assertEqual(
            fetch_assets._source_image_url(image_url),
            "https://runescape.wiki/images/archive/example.png?source=ad092",
        )

    def test_download_source_bytes_retries_optimized_response(self):
        source_bytes = b"original source"
        info = fetch_assets.ImageInfo(
            source_wiki="rs3",
            file_title="Example.png",
            file_page_url="https://runescape.wiki/wiki/File:Example.png",
            image_url="https://runescape.wiki/images/archive/Example.png?abc12",
            sha1=hashlib.sha1(source_bytes).hexdigest(),
            size=len(source_bytes),
            mime="image/png",
            timestamp="2012-01-01T00:00:00Z",
            mediatype="BITMAP",
            license_string="unknown",
        )

        class OptimizingClient:
            def __init__(self):
                self.responses = [b"optimized", source_bytes]

            def download_bytes(self, url):
                return self.responses.pop(0)

        self.assertEqual(
            fetch_assets._download_source_bytes(OptimizingClient(), info),
            source_bytes,
        )

    @unittest.skipUnless(HAS_PIL, "Pillow is required for PNG validation")
    def test_write_source_png_preserves_api_bytes_exactly(self):
        source = Image.new("RGBA", (23, 22), (255, 0, 0, 255))
        source_bytes = BytesIO()
        source.save(source_bytes, format="PNG")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "source.png"
            fetch_assets.write_source_png(source_bytes.getvalue(), output_path)
            self.assertEqual(output_path.read_bytes(), source_bytes.getvalue())

    def test_historical_lookup_requests_newest_revision_before_cutoff(self):
        class RecordingClient(fetch_assets.HttpWikiClient):
            def __init__(self):
                super().__init__(before_timestamp="2012-11-20T00:00:00Z")
                self.url = ""

            def _request_json(self, url):
                self.url = url
                return {
                    "query": {
                        "pages": [
                            {
                                "title": "File:Canopic jar.png",
                                "imageinfo": [
                                    {
                                        "url": "https://runescape.wiki/images/archive/example.png",
                                        "sha1": "period",
                                        "size": 123,
                                        "mime": "image/png",
                                        "timestamp": "2012-09-28T00:00:00Z",
                                        "mediatype": "BITMAP",
                                    },
                                    {
                                        "url": "https://runescape.wiki/images/example.png",
                                        "sha1": "post-cutoff",
                                        "size": 456,
                                        "mime": "image/png",
                                        "timestamp": "2014-01-01T00:00:00Z",
                                        "mediatype": "BITMAP",
                                    }
                                ],
                            }
                        ]
                    }
                }

        client = RecordingClient()
        info = client.query_image_info(fetch_assets.RS3_WIKI, "Canopic jar.png")
        query = parse_qs(urlparse(client.url).query)

        self.assertEqual(query["iistart"], ["2012-11-20T00:00:00Z"])
        self.assertEqual(query["iilimit"], ["max"])
        self.assertEqual(info.timestamp, "2012-09-28T00:00:00Z")
        self.assertIn("/archive/", info.image_url)

    def test_historical_lookup_refuses_file_without_pre_cutoff_revision(self):
        class PostCutoffOnlyClient(fetch_assets.HttpWikiClient):
            def __init__(self):
                super().__init__(before_timestamp="2012-11-20T00:00:00Z")

            def _request_json(self, _url):
                return {
                    "query": {
                        "pages": [
                            {
                                "title": "File:Future reward.png",
                                "imageinfo": [
                                    {
                                        "url": "https://runescape.wiki/images/future.png",
                                        "sha1": "future",
                                        "size": 123,
                                        "mime": "image/png",
                                        "timestamp": "2014-01-01T00:00:00Z",
                                        "mediatype": "BITMAP",
                                    }
                                ],
                            }
                        ]
                    }
                }

        info = PostCutoffOnlyClient().query_image_info(
            fetch_assets.RS3_WIKI,
            "Future reward.png",
        )

        self.assertIsNone(info)

    def test_wiki_title_mapping_uses_tree_log_overrides(self):
        self.assertEqual(fetch_assets.wiki_title_for_item("Tree"), "Logs.png")
        self.assertEqual(fetch_assets.wiki_title_for_item("Oak"), "Oak logs.png")
        self.assertEqual(fetch_assets.wiki_title_for_item("Rune essence"), "Rune essence.png")
        self.assertEqual(fetch_assets.wiki_title_for_item("Magic logs"), "Magic logs.png")
        self.assertEqual(fetch_assets.wiki_title_for_item("Ignored", "File:Custom icon"), "Custom icon.png")

    def test_key_resolution_accepts_storage_slug_and_returns_manifest_path(self):
        request = fetch_assets.resolve_asset_request(
            item_name=None,
            key="rune_essence",
            out_path=None,
            wiki_title_override=None,
            provenance_path=Path("assets_provenance.json"),
        )
        self.assertEqual(request.item_name, "Rune essence")
        self.assertEqual(request.wiki_title, "Rune essence.png")
        self.assertEqual(request.output_path.name, "RuneEssence.png")

    def test_dry_run_osrs_hit_does_not_download_or_write(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "Yew.png"
            request = fetch_assets.AssetRequest(
                item_name="Yew",
                wiki_title=fetch_assets.wiki_title_for_item("Yew"),
                output_path=out_path,
                provenance_path=Path(tmp_dir) / "provenance.json",
            )
            client = FakeWikiClient({("osrs", "Yew logs.png")})
            outcome = fetch_assets.fetch_asset(request, client, dry_run=True)

            self.assertEqual(outcome.source_wiki, "osrs")
            self.assertEqual(outcome.wiki_title, "Yew logs.png")
            self.assertFalse(out_path.exists())
            self.assertEqual(client.downloads, [])

    def test_rs3_fallback_when_osrs_misses(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            request = fetch_assets.AssetRequest(
                item_name="Divination shard",
                wiki_title="Divination shard.png",
                output_path=Path(tmp_dir) / "divination.png",
                provenance_path=Path(tmp_dir) / "provenance.json",
            )
            client = FakeWikiClient({("rs3", "Divination shard.png")})
            outcome = fetch_assets.fetch_asset(request, client, dry_run=True)

            self.assertEqual(outcome.source_wiki, "rs3")
            self.assertEqual(
                client.queries,
                [("osrs", "Divination shard.png"), ("rs3", "Divination shard.png")],
            )

    def test_source_restriction_skips_the_other_wiki(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            request = fetch_assets.AssetRequest(
                item_name="Overload (3)",
                wiki_title="Overload (3).png",
                output_path=Path(tmp_dir) / "overload.png",
                provenance_path=Path(tmp_dir) / "provenance.json",
            )
            client = FakeWikiClient({("osrs", "Overload (3).png"), ("rs3", "Overload (3).png")})
            outcome = fetch_assets.fetch_asset(
                request,
                client,
                dry_run=True,
                sources=(fetch_assets.RS3_WIKI,),
            )

            self.assertEqual(outcome.source_wiki, "rs3")
            self.assertEqual(client.queries, [("rs3", "Overload (3).png")])

    def test_existing_output_is_skipped_without_force(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "existing.png"
            out_path.write_bytes(b"keep me")
            provenance_path = Path(tmp_dir) / "provenance.json"
            provenance_path.write_bytes(b"keep the recorded provenance exactly")
            request = fetch_assets.AssetRequest(
                item_name="Oak",
                wiki_title="Oak logs.png",
                output_path=out_path,
                provenance_path=provenance_path,
            )
            client = FakeWikiClient(set())
            outcome = fetch_assets.fetch_asset(request, client, dry_run=False)

            self.assertTrue(outcome.skipped_existing)
            self.assertEqual(out_path.read_bytes(), b"keep me")
            self.assertEqual(
                provenance_path.read_bytes(), b"keep the recorded provenance exactly"
            )
            self.assertEqual(client.queries, [])
            self.assertEqual(client.downloads, [])
            self.assertEqual(
                (outcome.source_wiki, outcome.image_url, outcome.file_page_url),
                (None, None, None),
            )

    def test_output_directory_is_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output = Path(tmp_dir)
            request = fetch_assets.AssetRequest(
                "Oak", "Oak logs.png", output, output / "provenance.json"
            )
            client = FakeWikiClient(set())
            with self.assertRaisesRegex(fetch_assets.AssetFetchError, "Output path is not a file"):
                fetch_assets.fetch_asset(request, client)
            self.assertEqual(client.queries, [])
            self.assertEqual(client.downloads, [])
            self.assertEqual(list(output.iterdir()), [])

    def test_dry_run_resolves_existing_output_without_changing_it(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "existing.png"
            out_path.write_bytes(b"keep me")
            request = fetch_assets.AssetRequest(
                "Oak", "Oak logs.png", out_path, Path(tmp_dir) / "provenance.json"
            )
            client = FakeWikiClient({("osrs", "Oak logs.png")})

            outcome = fetch_assets.fetch_asset(request, client, dry_run=True)

            self.assertTrue(outcome.skipped_existing)
            self.assertEqual(outcome.source_wiki, "osrs")
            self.assertEqual(client.queries, [("osrs", "Oak logs.png")])
            self.assertEqual(client.downloads, [])
            self.assertEqual(out_path.read_bytes(), b"keep me")
            self.assertFalse(request.provenance_path.exists())

    def test_force_replaces_existing_output_and_records_resolved_source(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "existing.png"
            out_path.write_bytes(b"replace me")
            request = fetch_assets.AssetRequest(
                "Oak", "Oak logs.png", out_path, Path(tmp_dir) / "provenance.json"
            )
            client = FakeWikiClient({("osrs", "Oak logs.png")})
            with patch.object(
                fetch_assets,
                "write_png",
                side_effect=lambda content, output, _size: output.write_bytes(content),
            ):
                outcome = fetch_assets.fetch_asset(request, client, force=True)

            self.assertFalse(outcome.skipped_existing)
            self.assertEqual(client.queries, [("osrs", "Oak logs.png")])
            self.assertEqual(client.downloads, [outcome.image_url])
            self.assertEqual(out_path.read_bytes(), b"not-used-in-dry-run-tests")
            provenance = json.loads(request.provenance_path.read_text())
            self.assertEqual(provenance[str(out_path)]["source_wiki"], "osrs")

    def test_hunter_manifest_leaves_shared_images_with_their_owning_fetcher(self):
        from tools.fetch_hunter_assets import _manifest
        from ankiscape.core.constants_parts.hunter_assets import HUNTER_SHARED_ITEM_IMAGES

        manifest = _manifest()
        names = [row[0] for row in manifest]
        paths = [row[2] for row in manifest]
        self.assertTrue(set(names).isdisjoint(HUNTER_SHARED_ITEM_IMAGES))
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(paths), len(set(paths)))


if __name__ == "__main__":
    unittest.main()
