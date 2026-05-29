import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FETCH_ASSETS_PATH = ROOT / "tools" / "fetch_assets.py"
SPEC = importlib.util.spec_from_file_location("fetch_assets_tool", FETCH_ASSETS_PATH)
fetch_assets = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["fetch_assets_tool"] = fetch_assets
SPEC.loader.exec_module(fetch_assets)


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

    def test_existing_output_is_skipped_without_force(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "existing.png"
            out_path.write_bytes(b"keep me")
            request = fetch_assets.AssetRequest(
                item_name="Oak",
                wiki_title="Oak logs.png",
                output_path=out_path,
                provenance_path=Path(tmp_dir) / "provenance.json",
            )
            client = FakeWikiClient({("osrs", "Oak logs.png")})
            outcome = fetch_assets.fetch_asset(request, client, dry_run=False)

            self.assertTrue(outcome.skipped_existing)
            self.assertEqual(out_path.read_bytes(), b"keep me")
            self.assertEqual(client.downloads, [])


if __name__ == "__main__":
    unittest.main()
