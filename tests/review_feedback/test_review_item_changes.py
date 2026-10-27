"""What one review added to and took from the Bank and carried pack.

The event log's XP line and the action queue both read these counts, so they
are compared save to save rather than collected from each handler.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.activity_feedback import item_changes_text
from ankiscape.logic.inventory_pure import review_item_changes_pure


class ReviewItemChangesTest(unittest.TestCase):
    def test_a_carried_item_counts_once_because_the_pack_is_a_view_over_the_bank(self):
        before = {
            "inventory": {"Iron ore": 10, "Coins": 50, "Antipoison (3)": 1},
            "carried_inventory": {"smelt_iron_bar": {"Iron ore": 8}},
        }
        after = {
            "inventory": {"Iron ore": 6, "Iron bar": 2, "Coins": 50, "Antipoison (3)": 0},
            "carried_inventory": {"smelt_iron_bar": {"Iron ore": 4, "Iron bar": 2}},
        }

        self.assertEqual(
            review_item_changes_pure(before, after),
            {"Iron ore": -4, "Iron bar": 2, "Antipoison (3)": -1},
        )

    def test_a_review_that_moved_no_items_has_no_changes(self):
        save = {"inventory": {"Iron ore": 10, "Bronze bar": 0}}

        self.assertEqual(review_item_changes_pure(save, {"inventory": {"Iron ore": 10}}), {})

    def test_the_line_lists_gains_before_losses(self):
        self.assertEqual(
            item_changes_text({"Iron ore": -4, "Antipoison (3)": -1, "Iron bar": 2}),
            "+2 Iron bar · −4 Iron ore · −1 Antipoison (3)",
        )


if __name__ == "__main__":
    unittest.main()
