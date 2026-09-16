"""Keep settlement preserves overflow, mutation order, and fold failures."""

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.runtime import runtime_actions_carried_overlay as overlay


class KeepSettlementTests(unittest.TestCase):
    def test_ordinary_gains_preserve_other_targets_and_uncapped_churn(self):
        player = {"carried_inventory": {"other": {"Logs": 1}},
                  "carried_churn": {"other": 3}}
        view = {"Coal": 27}
        overflow = overlay._fold_keep_gains_and_write_carried(
            player, "copper", view, {"Coal": 2}, 27, 2, 28, False,
        )
        self.assertEqual(overflow, {})
        self.assertEqual(view, {"Coal": 27})
        self.assertEqual(player["carried_inventory"],
                         {"other": {"Logs": 1}, "copper": {"Coal": 29}})
        self.assertEqual(player["carried_churn"], {"other": 3, "copper": 29})

    def test_blessing_preserves_overflow_identity_and_inventory_before_churn(self):
        overflow = {"Logs": 2}
        folded = {"Logs": 28}
        with patch.object(overlay.inventory_pure, "carried_fold_gains_with_overflow_pure",
                          return_value=(folded, overflow)), patch.object(
                              overlay, "_set_carried_target_map") as write:
            player = {}
            result = overlay._fold_keep_gains_and_write_carried(
                player, "tree", {"Logs": 28}, {"Logs": 2}, 28, 2, 28, True,
            )
        self.assertIs(result, overflow)
        self.assertEqual(write.call_args_list[0].args,
                         (player, "carried_inventory", "tree", folded))
        self.assertEqual(write.call_args_list[1].args,
                         (player, "carried_churn", "tree", 28))
        self.assertEqual(write.call_count, 2)

    def test_fold_exception_propagates_before_any_carried_write(self):
        player = {"carried_inventory": {"tree": {"Logs": 1}},
                  "carried_churn": {"tree": 1}}
        before = copy.deepcopy(player)
        error = RuntimeError("fold sentinel")
        with patch.object(overlay.inventory_pure, "carried_fold_gains_pure",
                          side_effect=error), self.assertRaises(RuntimeError) as raised:
            overlay._fold_keep_gains_and_write_carried(
                player, "tree", {"Logs": 1}, {"Logs": 1}, 1, 1, 28, False,
            )
        self.assertIs(raised.exception, error)
        self.assertEqual(player, before)
