import hashlib
import importlib.util
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit


ROOT = Path(__file__).resolve().parents[2]
FETCH_ASSETS_PATH = ROOT / "tools" / "fetch_assets.py"
SPEC = importlib.util.spec_from_file_location("fetch_assets_source_url_tool", FETCH_ASSETS_PATH)
fetch_assets = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = fetch_assets
SPEC.loader.exec_module(fetch_assets)


@contextmanager
def byte_server(response):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            content = response(self.path, len(requests))
            requests.append((self.path, content))
            self.send_response(200)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, *_args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}", requests
        finally:
            server.shutdown()
            thread.join()


def image_info(url, content):
    return fetch_assets.ImageInfo(
        source_wiki="rs3",
        file_title="Example.png",
        file_page_url="https://runescape.wiki/wiki/File:Example.png",
        image_url=url,
        sha1=hashlib.sha1(content).hexdigest(),
        size=len(content),
        mime="image/png",
        timestamp="2012-01-01T00:00:00Z",
        mediatype="BITMAP",
        license_string="unknown",
    )


class TestFetchAssetsSourceUrls(unittest.TestCase):
    def test_source_request_preserves_named_query_bytes_and_parameters(self):
        content = b"disposable original source\x00\xff"
        query = (
            "cb=20111119160524&format=original&tag=one&tag=two&empty="
            "&encoded=a%26b%3Dc%2B&space=a+b&%70ercent=%2526&flag"
        )
        path = "/runescape2/images/f/fe/Crumble_Undead_icon.png/revision/latest"

        def response(request_path, _index):
            received = urlsplit(request_path).query
            return content if received.startswith(query + "&") else b"wrong query"

        with byte_server(response) as (base_url, requests):
            info = image_info(f"{base_url}{path}?{query}#ignored", content)
            actual = fetch_assets._download_source_bytes(
                fetch_assets.HttpWikiClient(min_interval_seconds=0), info
            )

        self.assertEqual(actual, content)
        self.assertEqual(len(requests), 1)
        received = parse_qsl(urlsplit(requests[0][0]).query, keep_blank_values=True)
        self.assertEqual(received[:-2], parse_qsl(query, keep_blank_values=True))
        self.assertEqual(received[-2], ("source", "original"))
        self.assertEqual(received[-1][0], "cache_bust")
        self.assertEqual(urlsplit(requests[0][0]).path, path)

    def test_source_request_keeps_existing_source_values(self):
        content = b"source marker bytes"
        for query in (
            "source=pinned%2Bmarker&format=original",
            "source=&source=second&format=original",
            "%73ource=encoded%26marker&empty=",
        ):
            with self.subTest(query=query):
                with byte_server(lambda _path, _index: content) as (base_url, requests):
                    info = image_info(f"{base_url}/image?{query}", content)
                    self.assertEqual(fetch_assets._download_source_bytes(
                        fetch_assets.HttpWikiClient(min_interval_seconds=0), info
                    ), content)
                received = urlsplit(requests[0][0]).query
                self.assertTrue(received.startswith(query + "&cache_bust="), received)
                self.assertEqual(
                    parse_qsl(received, keep_blank_values=True)[:-1],
                    parse_qsl(query, keep_blank_values=True),
                )

    def test_source_request_retries_optimized_bytes_and_accepts_matching_sha1(self):
        content = b"original wiki bytes"
        with byte_server(
            lambda _path, index: b"optimized" if index == 0 else content
        ) as (base_url, requests):
            info = image_info(f"{base_url}/image?ad092", content)
            self.assertEqual(fetch_assets._download_source_bytes(
                fetch_assets.HttpWikiClient(min_interval_seconds=0), info
            ), content)

        queries = [parse_qsl(urlsplit(path).query) for path, _ in requests]
        self.assertEqual(len(requests), 2)
        self.assertEqual([query[0] for query in queries], [("source", "ad092")] * 2)
        self.assertNotEqual(queries[0][-1], queries[1][-1])

    def test_source_request_without_query_uses_original_marker(self):
        content = b"source without query"
        with byte_server(lambda _path, _index: content) as (base_url, requests):
            info = image_info(f"{base_url}/image", content)
            self.assertEqual(fetch_assets._download_source_bytes(
                fetch_assets.HttpWikiClient(min_interval_seconds=0), info
            ), content)
        self.assertEqual(parse_qsl(urlsplit(requests[0][0]).query)[0], ("source", "original"))

    def test_source_request_refuses_historical_sha1_mismatch_after_three_attempts(self):
        content = b"not the historical Crumble Undead asset"
        query = "cb=20111119160524&format=original"
        with byte_server(lambda _path, _index: content) as (base_url, requests):
            info = replace(
                image_info(f"{base_url}/image?{query}", content),
                sha1="263b75038c03b742bdfa93843623f38a656896b7",
            )
            with self.assertRaisesRegex(fetch_assets.AssetFetchError, "did not match the API SHA1"):
                fetch_assets._download_source_bytes(
                    fetch_assets.HttpWikiClient(min_interval_seconds=0), info
                )
        self.assertEqual(len(requests), 3)
        self.assertTrue(all(urlsplit(path).query.startswith(query + "&") for path, _ in requests))
        cache_busts = [dict(parse_qsl(urlsplit(path).query))["cache_bust"] for path, _ in requests]
        self.assertEqual(len(set(cache_busts)), 3)

    def test_ordinary_fetch_keeps_optimized_request_and_normalization(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is required for PNG normalization")
        image = Image.new("RGBA", (12, 10), (0, 0, 0, 0))
        image.paste((255, 0, 0, 255), (2, 3, 10, 7))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        content = buffer.getvalue()
        query = "ad092&format=optimized"

        with byte_server(lambda _path, _index: content) as (base_url, requests):
            info = image_info(f"{base_url}/image?{query}", content)

            class Client(fetch_assets.HttpWikiClient):
                def query_image_info(self, _source, _title):
                    return info

            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "image.png"
                provenance = Path(directory) / "provenance.json"
                request = fetch_assets.AssetRequest("Example", "Example.png", output, provenance)
                fetch_assets.fetch_asset(request, Client(min_interval_seconds=0), size=4)
                with Image.open(output) as normalized:
                    self.assertEqual(normalized.size, (4, 2))
                    self.assertEqual(normalized.getchannel("A").getbbox(), (0, 0, 4, 2))
                self.assertTrue(provenance.is_file())

        self.assertEqual([path for path, _ in requests], [f"/image?{query}"])


if __name__ == "__main__":
    unittest.main()
