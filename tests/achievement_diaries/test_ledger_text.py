"""Designed text rules for curated Achievement Diary deeds."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from tools.achievement_diary_ledger import CurationLedger, _validate_row_metadata
from tools.generate_achievement_diary_data import _task_block


class CurationLedgerTextTest(unittest.TestCase):
    def test_generator_emits_the_designed_translated_task_text(self):
        ledger = object.__new__(CurationLedger)
        ledger.rows = {
            "test_easy_source_deed": {
                "disposition": "translated",
                "designed_name": "A New Leaf",
                "designed_description": "Rake the Falador tree patch.",
            }
        }
        with patch(
            "tools.generate_achievement_diary_data.CURATION_LEDGER", ledger
        ):
            block = _task_block(
                "test",
                "easy",
                {"id": 0, "name": "Source Deed", "description": "Source sentence."},
                "synthetic source",
                conditions_override=(),
            )

        self.assertIn("'A New Leaf'", block)
        self.assertIn("'Rake the Falador tree patch.'", block)
        self.assertNotIn("'Source Deed'", block)
        self.assertNotIn("'Source sentence.'", block)

    def test_translated_row_without_designed_text_is_rejected(self):
        with self.assertRaisesRegex(
            SystemExit,
            "translated diary ledger task synthetic_translated has no designed task text",
        ):
            _validate_row_metadata(
                "synthetic_translated", {"disposition": "translated"}
            )

    def test_active_row_with_designed_text_is_rejected(self):
        with self.assertRaisesRegex(
            SystemExit,
            "active diary ledger task synthetic_active carries designed task text",
        ):
            _validate_row_metadata(
                "synthetic_active",
                {
                    "disposition": "active",
                    "designed_name": "Not allowed",
                    "designed_description": "Not allowed.",
                },
            )

    def test_designed_description_cannot_reuse_the_source_sentence(self):
        with self.assertRaisesRegex(SystemExit, "reuses its source description"):
            _validate_row_metadata(
                "synthetic_translated",
                {
                    "disposition": "translated",
                    "designed_name": "A New Leaf",
                    "designed_description": "Source sentence.",
                },
                "Source sentence.",
            )


if __name__ == "__main__":
    unittest.main()
