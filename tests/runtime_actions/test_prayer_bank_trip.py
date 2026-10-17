"""Burying and scattering refill at the bank; only the altar methods walk."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.runtime.runtime_actions import handle_prayer_answer, run_answer_with_carried_overlay
from tests.test_runtime_actions import _context


def _answer_reviews(target_id: str, bank: dict, reviews: int):
    player = default_player_data(ORE_DATA)
    player.update(current_prayer=target_id, inventory=dict(bank))
    calls = {"xp": [], "saves": 0, "errors": []}
    ctx = _context(player, calls)
    for _ in range(reviews):
        run_answer_with_carried_overlay(ctx, "prayer", handle_prayer_answer)
    return player, calls


class TestPrayerBankTrip(unittest.TestCase):
    def test_bury_and_scatter_refill_a_28_pack_with_no_travel_review(self):
        for target_id, item, xp in (("bury_bones", "Bones", 4.5),
                                    ("scatter_impious_ashes", "Impious ashes", 4.0)):
            with self.subTest(target_id=target_id):
                player, calls = _answer_reviews(target_id, {item: 30}, 30)
                self.assertEqual(calls["xp"], [xp] * 30)
                self.assertEqual(player["inventory"].get(item, 0), 0)
                self.assertEqual(calls.get("activity", []), [])
                travel = player["agility_last_travel"]
                self.assertEqual((travel["route_label"], travel["charged_reviews"]), ("Working at the bank", 0))

    def test_altar_methods_keep_the_altar_trip(self):
        for target_id, bank in (("gilded_altar_bones", {"Bones": 30}),
                                ("ectofuntus_bones", {"Bonemeal": 30, "Bucket of slime": 30})):
            with self.subTest(target_id=target_id):
                player, calls = _answer_reviews(target_id, bank, 40)
                self.assertIn("Bank run — Running to the altar · 1/3 travel reviews", calls["activity"])
                travel = player["agility_last_travel"]
                self.assertEqual((travel["base_reviews"], travel["charged_reviews"]), (2.678, 3))


if __name__ == "__main__":
    unittest.main()
