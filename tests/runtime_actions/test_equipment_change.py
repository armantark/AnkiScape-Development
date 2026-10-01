"""Gear, supply and bank moves refuse cleanly and stay in order with review Undo."""

import copy
from dataclasses import asdict
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

    def test_mogre_drops_equip_from_inventory_and_apply_their_bonuses(self):
        addon = integration._load_addon_as_package("ankiscape_mogre_equipment")
        addon.mw = integration._DummyMW(integration._DummyCol())
        addon.save_player_data = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Mudskipper hat": 1, "Flippers": 1},
            "equipment": {},
            "defense_level": 1,
        }
        expected_stats = {
            "Mudskipper hat": {
                field: 0 for field in addon.ui.EQUIPMENT_BONUS_FIELDS
            },
            "Flippers": {
                **{field: 0 for field in addon.ui.EQUIPMENT_BONUS_FIELDS},
                "attack_stab": -2,
                "attack_slash": -2,
                "attack_crush": -2,
                "defence_slash": 1,
                "defence_crush": 1,
            },
        }

        for item_name, slot in (("Mudskipper hat", "head"), ("Flippers", "feet")):
            with self.subTest(item_name=item_name):
                self.assertTrue(addon.on_equip_item(item_name))
                self.assertEqual(addon._state.player_data["inventory"][item_name], 0)
                self.assertEqual(addon._state.player_data["equipment"][slot], item_name)
                totals = addon.ui.equipment_stat_totals_pure(
                    addon._state.player_data["equipment"], addon.EQUIPMENT_DATA
                )
                self.assertEqual(asdict(totals), expected_stats[item_name])


class GearMoveAfterReviewUndoTest(unittest.TestCase):
    """Review Undo restores only the save keys the review changed, so a gear,
    supply or bank move made after the review must be its own Undo step, taken
    back first. Otherwise review Undo puts the bank back while the slot, toolbelt,
    supply loadout or Death's Office keeps the moved item, duplicating or
    deleting it."""

    setUp = undo_seam.DirectActionUndoSeamTest.setUp
    tearDown = undo_seam.DirectActionUndoSeamTest.tearDown

    def _undo_latest(self):
        self.addon._on_state_did_undo(SimpleNamespace(operation=self.collection.entries.pop()))

    def assert_review_then_move_undoes_in_order(self, move, **state):
        addon = self.addon
        addon._state.current_skill = "Mining"
        addon._state.player_data.update(
            current_ore="copper", toolbelt={"mining": ["bronze_pickaxe"]}, **state
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
            lambda: self.addon.on_equip_item("Bronze platebody"),
            inventory={"Bronze platebody": 1}, equipment={},
        )

    def test_unequip_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(
            lambda: self.addon.on_unequip_slot("body"),
            inventory={}, equipment={"body": "Bronze platebody"},
        )

    def test_tool_attach_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(
            lambda: self.addon.on_attach_tool("Iron pickaxe"),
            inventory={"Iron pickaxe": 1}, equipment={},
        )

    def test_supply_refill_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(
            self.addon.on_refill_combat_loadout,
            inventory={"Shark": 30}, combat_auto_eat_food=["Shark"],
        )

    def test_pack_mode_change_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(
            lambda: self.addon.on_set_combat_pack_mode("max_safety"),
            inventory={"Shark": 30}, combat_auto_eat_food=["Shark"],
            combat_pack_mode="max_output", combat_supply_loadout={"food": {"Shark": 8}},
        )

    def test_supply_unload_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(
            self.addon.on_unload_combat_loadout,
            inventory={}, combat_supply_loadout={"food": {"Shark": 20}},
        )

    def test_death_office_reclaim_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(
            self.addon.on_reclaim_death_office,
            inventory={"Coins": 150},
            death_office={"items": ["Bronze sword"], "source": "combat_stacked_grave"},
        )

    def test_bank_run_request_after_a_review_is_undone_before_the_review(self):
        self.assert_review_then_move_undoes_in_order(self.addon.on_do_bank_run_now, inventory={})

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

    def test_a_refused_undo_entry_leaves_supplies_and_death_office_alone(self):
        addon = self.addon
        errors = []
        addon.show_error_message = lambda title, message: errors.append((title, message))
        self.collection.accepts = False
        addon._state.current_skill = "Mining"
        addon._state.player_data.update(
            current_ore="copper",
            inventory={"Shark": 30, "Coins": 150},
            combat_auto_eat_food=["Shark"],
            combat_supply_loadout={"food": {"Lobster": 5}},
            death_office={"items": ["Bronze sword"], "source": "combat_stacked_grave"},
        )
        before = copy.deepcopy(addon._state.player_data)
        moves = (
            ("Cannot refill supplies", addon.on_refill_combat_loadout),
            ("Cannot clear inventory", addon.on_unload_combat_loadout),
            ("Cannot reclaim gear", addon.on_reclaim_death_office),
            ("Cannot make a bank run", addon.on_do_bank_run_now),
        )
        for title, move in moves:
            with self.subTest(title):
                errors.clear()

                self.assertFalse(move())

                self.assertEqual(
                    errors, [(title, "Anki could not create an undo entry, so nothing changed.")]
                )
                self.assertEqual(addon._state.player_data, before)
                self.assertEqual(self.saves, [])


if __name__ == "__main__":
    unittest.main()
