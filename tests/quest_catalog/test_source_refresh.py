import http.client
import io
import json
import socket
import ssl
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from tools.generation import refresh_quest_sources as refresh


class TestQuestSourceRefresh(unittest.TestCase):
    def test_api_errors_never_enter_the_cache_or_retained_responses(self):
        for cached in (False, True):
            with self.subTest(cached=cached), tempfile.TemporaryDirectory() as directory:
                cache = Path(directory)
                payload = json.dumps({"error": {"code": "maxlag", "info": "Try again"}})
                if cached:
                    (cache / "quest.json").write_text(payload, encoding="utf-8")
                wiki = refresh.WikiSources(cache, offline=cached)
                with patch.object(refresh.urllib.request, "urlopen", return_value=io.BytesIO(payload.encode())):
                    with self.assertRaisesRegex(RuntimeError, "maxlag"):
                        wiki.read("quest", {})
                self.assertEqual(wiki.responses, {})
                self.assertEqual((cache / "quest.json").exists(), cached)
                self.assertFalse((cache / "quest.tmp").exists())

    def test_transient_transport_and_http_errors_retry_before_caching_success(self):
        for error in (
            ConnectionResetError("connection reset"),
            http.client.IncompleteRead(b"partial"),
            urllib.error.URLError(socket.timeout("timed out")),
            urllib.error.URLError(ConnectionRefusedError("connection refused")),
            urllib.error.HTTPError("url", 429, "limited", {}, None),
            urllib.error.HTTPError("url", 503, "unavailable", {}, None),
        ):
            with self.subTest(error=error), tempfile.TemporaryDirectory() as directory:
                cache = Path(directory)
                wiki = refresh.WikiSources(cache, offline=False)
                payload = {"query": {"pages": [{"title": "Quest"}]}}
                with (
                    patch.object(refresh.urllib.request, "urlopen", side_effect=[error, io.BytesIO(json.dumps(payload).encode())]) as request,
                    patch.object(refresh.time, "sleep") as sleep,
                ):
                    self.assertEqual(wiki.read("quest", {}), payload)
                self.assertEqual(request.call_count, 2)
                sleep.assert_called_once()
                self.assertEqual(json.loads((cache / "quest.json").read_text()), payload)
                if isinstance(error, urllib.error.HTTPError):
                    error.close()

    def test_permanent_transport_errors_fail_without_retry_or_caching(self):
        for error in (
            PermissionError("permission denied"),
            urllib.error.URLError(ssl.SSLCertVerificationError("invalid certificate")),
        ):
            with self.subTest(error=error), tempfile.TemporaryDirectory() as directory:
                wiki = refresh.WikiSources(Path(directory), offline=False)
                with (
                    patch.object(refresh.urllib.request, "urlopen", side_effect=error) as request,
                    patch.object(refresh.time, "sleep") as sleep,
                ):
                    with self.assertRaises(type(error)) as raised:
                        wiki.read("quest", {})
                self.assertIs(raised.exception, error)
                request.assert_called_once()
                sleep.assert_not_called()
                self.assertEqual(list(Path(directory).iterdir()), [])
                self.assertEqual(wiki.responses, {})

    def test_non_retryable_http_errors_fail_without_caching(self):
        for code in (400, 403, 404):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                wiki = refresh.WikiSources(Path(directory), offline=False)
                error = urllib.error.HTTPError("url", code, "rejected", {}, None)
                with (
                    patch.object(refresh.urllib.request, "urlopen", side_effect=error) as request,
                    patch.object(refresh.time, "sleep") as sleep,
                ):
                    with self.assertRaises(urllib.error.HTTPError):
                        wiki.read("quest", {})
                request.assert_called_once()
                sleep.assert_not_called()
                self.assertEqual(list(Path(directory).iterdir()), [])
                self.assertEqual(wiki.responses, {})
                error.close()
