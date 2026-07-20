import unittest

from equipment_instance_logic import (
    add_equipment_instance_pure,
    advance_equipped_condition_pure,
    condition_name_pure,
    discharge_equipped_on_unsafe_death_pure,
    remove_bank_equipment_instances_pure,
    sanitize_equipment_instance_state_pure,
    sync_equipment_instances_pure,
)
from fist_of_guthix_data import FIST_OF_GUTHIX_CONDITION_DATA


class EquipmentInstanceLogicTest(unittest.TestCase):
    def test_condition_names_follow_source_twenty_percent_identities(self):
        self.assertEqual(
            condition_name_pure("combat_hood", 90_000, FIST_OF_GUTHIX_CONDITION_DATA),
            "Combat hood 100",
        )
        self.assertEqual(
            condition_name_pure("combat_hood", 72_000, FIST_OF_GUTHIX_CONDITION_DATA),
            "Combat hood 80",
        )
        self.assertEqual(
            condition_name_pure("combat_hood", 1, FIST_OF_GUTHIX_CONDITION_DATA),
            "Combat hood 20",
        )
        self.assertEqual(
            condition_name_pure("combat_hood", 0, FIST_OF_GUTHIX_CONDITION_DATA),
            "Combat hood 0",
        )

    def test_add_preserves_two_non_stackable_copies_as_distinct_instances(self):
        player = {"inventory": {}, "equipment": {}}
        player, first_id = add_equipment_instance_pure(
            player, "combat_hood", FIST_OF_GUTHIX_CONDITION_DATA
        )
        player, second_id = add_equipment_instance_pure(
            player, "combat_hood", FIST_OF_GUTHIX_CONDITION_DATA
        )
        self.assertNotEqual(first_id, second_id)
        self.assertEqual(player["inventory"]["Combat hood 100"], 2)
        self.assertEqual(len(player["equipment_instances"]), 2)

    def test_equip_reconciliation_selects_the_healthiest_copy(self):
        player = {
            "inventory": {"Combat hood 100": 1},
            "equipment": {"head": "Combat hood 100"},
            "equipment_instances": {
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 80_000,
                    "location": "bank",
                },
                "equipment-2": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 89_000,
                    "location": "bank",
                },
            },
            "equipment_instance_next_id": 3,
        }
        synced = sync_equipment_instances_pure(
            player, {}, FIST_OF_GUTHIX_CONDITION_DATA
        )
        self.assertEqual(
            synced["equipment_instances"]["equipment-2"]["location"],
            "equipped:head",
        )
        self.assertEqual(
            synced["equipment_instances"]["equipment-1"]["location"], "bank"
        )

    def test_combat_ticks_change_only_the_equipped_copy_and_cross_identity(self):
        player = {
            "inventory": {"Combat hood 100": 1},
            "equipment": {"head": "Combat hood 100"},
            "equipment_instances": {
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 80_000,
                    "location": "bank",
                },
                "equipment-2": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 72_001,
                    "location": "equipped:head",
                    "last_slot": "head",
                },
            },
            "equipment_instance_next_id": 3,
        }
        updated, events = advance_equipped_condition_pure(
            player, 2, FIST_OF_GUTHIX_CONDITION_DATA
        )
        self.assertEqual(updated["equipment"]["head"], "Combat hood 80")
        self.assertEqual(updated["inventory"]["Combat hood 100"], 1)
        self.assertEqual(updated["equipment_instances"]["equipment-2"]["condition"], 71_999)
        self.assertEqual(events[0]["after_name"], "Combat hood 80")

    def test_unsafe_death_discharges_gauntlets_but_safe_paths_can_skip_hook(self):
        player = {
            "inventory": {},
            "equipment": {"hands": "Bronze gauntlets"},
            "equipment_instances": {
                "equipment-1": {
                    "family_id": "bronze_gauntlets",
                    "item_name": "Bronze gauntlets",
                    "condition": 1,
                    "location": "equipped:hands",
                    "last_slot": "hands",
                }
            },
            "equipment_instance_next_id": 2,
        }
        discharged, events = discharge_equipped_on_unsafe_death_pure(
            player, FIST_OF_GUTHIX_CONDITION_DATA
        )
        self.assertEqual(discharged["equipment"]["hands"], "Worn-out bronze gauntlets")
        self.assertEqual(discharged["equipment_instances"]["equipment-1"]["condition"], 0)
        self.assertEqual(events[0]["after_name"], "Worn-out bronze gauntlets")
        untouched = sanitize_equipment_instance_state_pure(
            player, FIST_OF_GUTHIX_CONDITION_DATA
        )
        self.assertEqual(untouched["equipment"]["hands"], "Bronze gauntlets")

    def test_holder_reconciliation_keeps_hidden_condition_when_item_moves_to_grave(self):
        player = {
            "inventory": {"Combat hood 100": 1},
            "equipment": {},
            "combat_grave": {"items": ["Combat hood 100"]},
            "equipment_instances": {
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 89_000,
                    "location": "bank",
                },
                "equipment-2": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 80_000,
                    "location": "equipped:head",
                    "last_slot": "head",
                },
            },
            "equipment_instance_next_id": 3,
        }
        reconciled = sanitize_equipment_instance_state_pure(
            player, FIST_OF_GUTHIX_CONDITION_DATA
        )
        self.assertEqual(reconciled["equipment_instances"]["equipment-1"]["location"], "bank")
        self.assertEqual(reconciled["equipment_instances"]["equipment-2"]["location"], "grave")
        self.assertEqual(reconciled["equipment_instances"]["equipment-2"]["condition"], 80_000)

    def test_discard_removes_the_most_spent_bank_copy_first(self):
        player = {
            "inventory": {"Combat hood 100": 2},
            "equipment": {},
            "equipment_instances": {
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 89_000,
                    "location": "bank",
                },
                "equipment-2": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 80_000,
                    "location": "bank",
                },
            },
            "equipment_instance_next_id": 3,
        }
        updated = remove_bank_equipment_instances_pure(
            player, "Combat hood 100", 1, FIST_OF_GUTHIX_CONDITION_DATA
        )
        self.assertEqual(updated["inventory"]["Combat hood 100"], 1)
        self.assertIn("equipment-1", updated["equipment_instances"])
        self.assertNotIn("equipment-2", updated["equipment_instances"])


if __name__ == "__main__":
    unittest.main()
