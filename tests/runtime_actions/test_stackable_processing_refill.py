"""Large bank stacks must not turn a review refill into one step per batch."""

import cProfile
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.item_values import STACKABLE_ITEM_NAMES
from ankiscape.logic import inventory_pure
from ankiscape.runtime.runtime_actions import (
    handle_fletching_answer,
    run_answer_with_carried_overlay,
)
from tests.test_runtime_actions import _context


class TestStackableProcessingRefill(unittest.TestCase):
    def test_review_refill_work_does_not_scale_with_bank_stock(self):
        player = default_player_data(ORE_DATA)
        player.update(current_fletch="headless_arrows",
                      inventory={"Arrow shafts": 15, "Feather": 15})
        ctx = _context(player, random_values=[1.0] * 4)
        self.assertTrue(run_answer_with_carried_overlay(ctx, "fletching", handle_fletching_answer))
        self.assertNotIn("headless_arrows", player["carried_inventory"])
        self.assertEqual(player["inventory"]["Headless arrows"], 15)

        player["inventory"].update({"Arrow shafts": 15_000_000, "Feather": 15_000_000})
        with cProfile.Profile() as profile:
            result = run_answer_with_carried_overlay(ctx, "fletching", handle_fletching_answer)

        self.assertTrue(result)
        self.assertEqual(player["carried_inventory"]["headless_arrows"],
                         {"Arrow shafts": 14_999_985, "Feather": 14_999_985})
        self.assertEqual(player["inventory"]["Arrow shafts"], 14_999_985)
        self.assertEqual(player["inventory"]["Feather"], 14_999_985)
        self.assertEqual(player["inventory"]["Headless arrows"], 30)
        self.assertEqual(player["skilling_bank_run"], {})
        self.assertEqual(inventory_pure.carried_slots_used(
            player["carried_inventory"]["headless_arrows"], STACKABLE_ITEM_NAMES), 2)
        slot_checks = sum(entry.callcount for entry in profile.getstats()
                          if entry.code == inventory_pure._processing_pack_slots.__code__)
        self.assertLessEqual(slot_checks, inventory_pure.CARRIED_CAPACITY)
