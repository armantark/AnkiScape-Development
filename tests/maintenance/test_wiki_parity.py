import io
import json
import unittest
from contextlib import redirect_stderr
from unittest import mock

from tools import wiki_parity


class WikiParityTest(unittest.TestCase):
    def test_combined_titles_are_rejected_before_request(self):
        with mock.patch("tools.wiki_parity._get") as get:
            with self.assertRaisesRegex(ValueError, "one title per cutoff lookup"):
                wiki_parity.resolve("Jade|Red topaz", wiki_parity.EOC)
        get.assert_not_called()

    def test_single_title_resolution_and_missing_pages_keep_their_meaning(self):
        resolved = {
            "query": {
                "pages": {
                    "1": {
                        "title": "Jade",
                        "revisions": [{"revid": 123, "timestamp": "2012-11-19T12:00:00Z"}],
                    }
                }
            }
        }
        missing = {"query": {"pages": {"-1": {"title": "Absent", "missing": ""}}}}
        with mock.patch("tools.wiki_parity._get", return_value=resolved):
            self.assertEqual(
                wiki_parity.resolve("Jade", wiki_parity.EOC),
                (123, "2012-11-19T12:00:00Z", "Jade"),
            )
        with mock.patch("tools.wiki_parity._get", return_value=missing):
            self.assertIsNone(wiki_parity.resolve("Absent", wiki_parity.EOC))

    def test_api_errors_preserve_code_and_info_without_exposing_owner_identity(self):
        payload = {
            "error": {
                "code": "invalidparammix",
                "info": "revision-bound parameters may only be used on a single page",
            }
        }

        def open_request(request, timeout):
            self.assertEqual(timeout, 30)
            self.assertEqual(request.get_header("User-agent"), "AnkiScape parity audit")
            return io.StringIO(json.dumps(payload))

        with mock.patch("tools.wiki_parity.urllib.request.urlopen", side_effect=open_request):
            with self.assertRaisesRegex(
                wiki_parity.WikiAPIError,
                "invalidparammix.*single page",
            ):
                wiki_parity._get({"action": "query"})

    def test_cli_reports_api_errors_instead_of_not_found(self):
        error = wiki_parity.WikiAPIError("invalidparammix: one page only")
        stderr = io.StringIO()
        with (
            mock.patch("tools.wiki_parity.resolve", side_effect=error),
            redirect_stderr(stderr),
        ):
            returncode = wiki_parity.main(["resolve", "Jade"])

        self.assertEqual(returncode, 1)
        self.assertIn("invalidparammix: one page only", stderr.getvalue())
        self.assertNotIn("NOT FOUND", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
