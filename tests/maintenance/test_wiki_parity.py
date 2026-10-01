import io
import json
import unittest
from unittest import mock

from tools import wiki_parity


class WikiParityTest(unittest.TestCase):
    def test_combined_titles_are_rejected_before_request(self):
        with mock.patch("tools.wiki_parity._get") as get:
            with self.assertRaisesRegex(ValueError, "one title per lookup"):
                wiki_parity.resolve("Jade|Red topaz", wiki_parity.EOC)
        get.assert_not_called()

    def test_api_error_with_http_success_raises_instead_of_looking_absent(self):
        payload = {
            "error": {
                "code": "invalidparammix",
                "info": "revision-bound parameters may only be used on a single page",
            }
        }
        response = io.StringIO(json.dumps(payload))
        with mock.patch("tools.wiki_parity.urllib.request.urlopen", return_value=response):
            with self.assertRaisesRegex(RuntimeError, "invalidparammix.*single page"):
                wiki_parity.resolve("Jade", wiki_parity.EOC)


if __name__ == "__main__":
    unittest.main()
