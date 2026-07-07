import unittest

from inventory_pure import (
    CARRIED_CAPACITY,
    DEFAULT_LOOT_VALUE_THRESHOLD,
    carried_capacity_remaining,
    carried_has_room_for,
    carried_slots_used,
    default_carried_state,
    high_alch_value,
    loot_should_pick_up,
    money_pouch_balance,
    pack_carried_inventory_pure,
    sanitize_carried_state,
)


class TestInventoryPure(unittest.TestCase):
    def test_slots_used_counts_stackable_once_and_unstackable_by_count(self):
        stackable = {"Air rune", "Feather"}

        self.assertEqual(carried_slots_used({"Air rune": 500}, stackable), 1)
        self.assertEqual(carried_slots_used({"Oak logs": 5}, stackable), 5)
        self.assertEqual(carried_slots_used({"Oak logs": 0, "Shrimps": -2}, stackable), 0)
        self.assertEqual(
            carried_slots_used({"Air rune": 500, "Oak logs": 5, "Feather": 0, "Shrimps": -2}, stackable),
            6,
        )

    def test_capacity_remaining_and_room_boundary(self):
        carried_27 = {f"Oak logs {i}": 1 for i in range(CARRIED_CAPACITY - 1)}
        self.assertEqual(carried_capacity_remaining(carried_27, set()), 1)
        self.assertTrue(carried_has_room_for(carried_27, "Shrimps", 1, set()))
        self.assertFalse(carried_has_room_for(carried_27, "Shrimps", 2, set()))

        carried_28 = {f"Oak logs {i}": 1 for i in range(CARRIED_CAPACITY)}
        self.assertEqual(carried_capacity_remaining(carried_28, set()), 0)
        self.assertFalse(carried_has_room_for(carried_28, "Shrimps", 1, set()))

    def test_adding_existing_stackable_is_free(self):
        stackable = {"Air rune"}
        carried = {f"Oak logs {i}": 1 for i in range(CARRIED_CAPACITY - 1)}
        carried["Air rune"] = 10

        self.assertEqual(carried_slots_used(carried, stackable), CARRIED_CAPACITY)
        self.assertTrue(carried_has_room_for(carried, "Air rune", 1000, stackable))
        self.assertFalse(carried_has_room_for(carried, "Feather", 1, {"Air rune", "Feather"}))

    def test_high_alch_value_floors_and_loot_filter_branches(self):
        self.assertEqual(high_alch_value(99), 59)
        self.assertEqual(high_alch_value(0), 0)
        self.assertEqual(high_alch_value(-100), 0)

        stackable = {"Air rune"}
        self.assertTrue(loot_should_pick_up("Air rune", 0, DEFAULT_LOOT_VALUE_THRESHOLD, stackable))
        self.assertFalse(loot_should_pick_up("Oak logs", 83, 50, stackable))
        self.assertTrue(loot_should_pick_up("Oak logs", 84, 50, stackable))
        self.assertTrue(loot_should_pick_up("Oak logs", 100, 50, stackable))

    def test_money_pouch_balance_reads_flat_bank_coins(self):
        # The pouch is a read-only view of coins in the flat bank; no separate store.
        self.assertEqual(money_pouch_balance({}), 0)
        self.assertEqual(money_pouch_balance({"inventory": {"Coins": 1000}}), 1000)
        self.assertEqual(money_pouch_balance({"inventory": {}}), 0)
        self.assertEqual(money_pouch_balance({"inventory": {"Coins": -5}}), 0)

    def test_sanitize_carried_state_empty_dict_defaults(self):
        player_data = {}

        sanitize_carried_state(player_data)

        self.assertEqual(player_data, default_carried_state())

    def test_sanitize_carried_state_corrects_junk_types(self):
        player_data = {
            "carried_inventory": {"target": {"Oak logs": "2", "Shrimps": -5, 3: 1}, "bad": "items"},
            "carried_pack_mode": "unsafe",
            "loot_value_threshold": "bad",
        }

        sanitize_carried_state(player_data)

        self.assertEqual(player_data["carried_inventory"], {"target": {"Oak logs": 2}})
        self.assertEqual(player_data["carried_pack_mode"], "balanced")
        self.assertEqual(player_data["loot_value_threshold"], DEFAULT_LOOT_VALUE_THRESHOLD)


class TestPackCarriedInventory(unittest.TestCase):
    def test_balanced_reserves_food_then_fills_primary_capped_at_28(self):
        bank = {"Lobster": 100, "Coal": 100}
        spec = {"food": ["Lobster"], "food_reserve": 6, "primary": "Coal"}
        carried = pack_carried_inventory_pure(bank, spec, "balanced", set())
        self.assertEqual(carried["Lobster"], 6)
        self.assertEqual(carried["Coal"], CARRIED_CAPACITY - 6)
        self.assertEqual(carried_slots_used(carried, set()), CARRIED_CAPACITY)

    def test_max_output_drops_the_food_reserve(self):
        bank = {"Lobster": 100, "Coal": 100}
        spec = {"food": ["Lobster"], "food_reserve": 6, "primary": "Coal"}
        carried = pack_carried_inventory_pure(bank, spec, "max_output", set())
        self.assertNotIn("Lobster", carried)
        self.assertEqual(carried["Coal"], CARRIED_CAPACITY)

    def test_max_safety_doubles_the_food_reserve(self):
        bank = {"Lobster": 100, "Coal": 100}
        spec = {"food": ["Lobster"], "food_reserve": 6, "primary": "Coal"}
        carried = pack_carried_inventory_pure(bank, spec, "max_safety", set())
        self.assertEqual(carried["Lobster"], 12)
        self.assertEqual(carried["Coal"], CARRIED_CAPACITY - 12)

    def test_required_items_are_placed_first_and_capped_by_bank(self):
        bank = {"Ammo mould": 1, "Steel bar": 100}
        spec = {"required": {"Ammo mould": 1}, "primary": "Steel bar"}
        carried = pack_carried_inventory_pure(bank, spec, "balanced", set())
        self.assertEqual(carried["Ammo mould"], 1)
        self.assertEqual(carried["Steel bar"], CARRIED_CAPACITY - 1)

    def test_primary_never_exceeds_bank_supply(self):
        bank = {"Coal": 5}
        carried = pack_carried_inventory_pure(bank, {"primary": "Coal"}, "balanced", set())
        self.assertEqual(carried["Coal"], 5)
        self.assertEqual(carried_slots_used(carried, set()), 5)

    def test_stackable_primary_takes_one_slot(self):
        bank = {"Nature rune": 5000}
        carried = pack_carried_inventory_pure(bank, {"primary": "Nature rune"}, "balanced", {"Nature rune"})
        self.assertEqual(carried["Nature rune"], 5000)
        self.assertEqual(carried_slots_used(carried, {"Nature rune"}), 1)


if __name__ == "__main__":
    unittest.main()
