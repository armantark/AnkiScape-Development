"""Equipment panel gear moves refuse cleanly and stay in order with review Undo."""

import copy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tests import test_direct_action_undo_seam as undo_seam
from tests import test_integration_smoke as integration


class TestEquipmentChange(unittest.TestCase):
    setUp = integration.TestIntegrationSmoke.setUp
    tearDown = integration.TestIntegrationSmoke.tearDown

    def test_unequipping_an_empty_slot_refuses_and_leaves_the_save_alone(self):
        addon = integration._load_addon_as_package("ankiscape_equipment_change_refusal")
        saves = []
        errors = []
        addon.save_player_data = lambda: saves.append(copy.deepcopy(addon._state.player_data))
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon._state.player_data = {
            "inventory": {"Bronze platebody": 1},
            "equipment": {"head": "Bronze full helm"},
        }
        before = copy.deepcopy(addon._state.player_data)

        self.assertFalse(addon.on_unequip_slot("body"))

        self.assertEqual(errors, [("Cannot unequip item", "That equipment slot is already empty.")])
        self.assertEqual(saves, [])
        self.assertEqual(addon._state.player_data, before)


class GearMoveAfterReviewUndoTest(unittest.TestCase):
    """Review Undo restores only the save keys the review changed, so a gear move
    made after the review must be its own Undo step, taken back first. Otherwise
    review Undo puts the bank back while the slot or toolbelt keeps the moved
    item, duplicating or deleting it."""

    setUp = undo_seam.DirectActionUndoSeamTest.setUp
    tearDown = undo_seam.DirectActionUndoSeamTest.tearDown

    def _undo_latest(self):
        self.addon._on_state_did_undo(SimpleNamespace(operation=self.collection.entries.pop()))

    def assert_review_then_move_undoes_in_order(self, inventory, equipment, move):
        addon = self.addon
        addon._state.current_skill = "Mining"
        addon._state.player_data.update(
            current_ore="copper", inventory=inventory, equipment=equipment,
            toolbelt={"mining": ["bronze_pickaxe"]},
        )
        before_review = copy.deepcopy(addon._state.player_data)
        snapshot = addon._capture_player_data_snapshot(review_answer=True)
        # Mine and bank one ore with no gem; later draws miss the Shattered Heart swap.
        rolls = iter((0.0, 0.0, 1.0, 0.0))
        with patch.object(addon.random, "random", side_effect=lambda: next(rolls, 0.5)):
            self.assertTrue(addon.on_mining_answer())
        addon._remember_review_award_snapshot(snapshot)
        self.collection.entries.append("Answer Card")
        after_review = copy.deepcopy(addon._state.player_data)
        self.assertEqual(after_review["inventory"]["Copper ore"], 1)

        self.assertTrue(move())
        self._undo_latest()
        self.assertEqual(addon._state.player_data, after_review)
        self._undo_latest()
        self.assertEqual(addon._state.player_data, before_review)

    def test_equip_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(
            {"Bronze platebody": 1}, {}, lambda: self.addon.on_equip_item("Bronze platebody")
        )

    def test_unequip_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(
            {}, {"body": "Bronze platebody"}, lambda: self.addon.on_unequip_slot("body")
        )

    def test_tool_attach_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(
            {"Iron pickaxe": 1}, {}, lambda: self.addon.on_attach_tool("Iron pickaxe")
        )

    def test_a_refused_undo_entry_blames_anki_not_the_gear(self):
        addon = self.addon
        errors = []
        addon.show_error_message = lambda title, message: errors.append((title, message))
        self.collection.accepts = False
        moves = (
            ("Cannot equip item", lambda: addon.on_equip_item("Bronze platebody")),
            ("Cannot unequip item", lambda: addon.on_unequip_slot("body")),
            ("Cannot attach tool", lambda: addon.on_attach_tool("Iron pickaxe")),
        )
        for title, move in moves:
            with self.subTest(title):
                addon._state.player_data.update(
                    inventory={"Bronze platebody": 1, "Iron pickaxe": 1},
                    equipment={"body": "Rune platebody"},
                )
                before = copy.deepcopy(addon._state.player_data)
                errors.clear()

                self.assertFalse(move())

                self.assertEqual(
                    errors, [(title, "Anki could not create an undo entry, so nothing changed.")]
                )
                self.assertEqual(addon._state.player_data, before)
                self.assertEqual(self.saves, [])


if __name__ == "__main__":
    unittest.main()
