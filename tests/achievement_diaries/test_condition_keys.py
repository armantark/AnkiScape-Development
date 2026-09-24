"""Generator refusals for diary condition keys the runtime never counts."""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from tools.generate_achievement_diary_data import _task_block


class ConditionKeyRefusalTest(unittest.TestCase):
    def test_generator_refuses_a_top_level_counter_that_never_counts(self):
        # A missing name and a non-count save field both read zero forever.
        for key in ("no_such_counter_xyz", "inventory"):
            with self.subTest(key=key), self.assertRaisesRegex(
                SystemExit, f"ardougne_easy_boot_camp.*'{key}'"
            ):
                _task_block(
                    "ardougne",
                    "easy",
                    {"id": 0, "name": "Boot Camp", "description": "Source deed"},
                    "synthetic source",
                    conditions_override=(("counter", key, 1, "Bad key"),),
                )


if __name__ == "__main__":
    unittest.main()
