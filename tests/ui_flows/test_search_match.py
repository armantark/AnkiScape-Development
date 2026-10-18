"""The shared search contract, including its short-token safety boundary."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.search_match import match_rank


class SearchMatchTest(unittest.TestCase):
    def test_tiers_prioritize_the_name_over_metadata(self):
        cases = (
            ("  STOLEN Hearts ", "Stolen Hearts", (), 0),
            ("stolen", "Stolen Hearts", (), 1),
            ("hearts stolen", "Stolen Hearts", (), 2),
            ("stolen hearts", "Contact!", ("Requires Stolen Hearts",), 3),
            ("tara", "Tiara", (), 4),
            ("tara air", "Bind air tiara", (), 4),
            ("tiaro", "Tiara", (), 4),
            ("taira", "Tiara", (), None),
            ("tr", "Tiara", (), None),
            ("taro", "Tiara", (), None),
            ("tara zz", "Tiara", (), None),
            ("", "Tiara", (), 0),
        )
        for query, name, metadata, expected in cases:
            with self.subTest(query=query, name=name):
                self.assertEqual(match_rank(query, name, *metadata), expected)

    def test_fuzzy_matching_uses_words_and_requires_every_token(self):
        self.assertEqual(match_rank("tara", "Silver tiara (Lvl 23)"), 4)
        self.assertIsNone(match_rank("tara", "Tanning rawhide"))
        self.assertEqual(match_rank("air tara", "Tiara", "Air altar"), 4)
        self.assertEqual(match_rank("iron ore", "Ore", "Iron"), 3)
        self.assertIsNone(match_rank("tara fire", "Air tiara"))


if __name__ == "__main__":
    unittest.main()
