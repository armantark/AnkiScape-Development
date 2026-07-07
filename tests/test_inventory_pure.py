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
    bank_run_progress_pure,
    carried_bank_run_gate_pure,
    carried_fold_gains_pure,
    carried_action_churn_pure,
    carried_advanced_for,
    carried_keep_for,
    effective_carried_capacity,
    filter_loot_pure,
    inventory_delta_gains,
    pack_processing_inputs_pure,
    apply_carried_layout_pure,
    layout_to_grid_cells_pure,
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

    def test_keep_for_defaults_to_keep_and_reads_drop(self):
        self.assertTrue(carried_keep_for({}, "coal"))
        self.assertTrue(carried_keep_for({"carried_keep_drop": {"coal": "keep"}}, "coal"))
        self.assertFalse(carried_keep_for({"carried_keep_drop": {"coal": "drop"}}, "coal"))
        self.assertTrue(carried_keep_for({"carried_keep_drop": {"oak": "drop"}}, "coal"))

    def test_sanitize_keeps_only_drop_entries_and_positive_churn(self):
        data = {
            "carried_keep_drop": {"coal": "drop", "oak": "keep", 3: "drop"},
            "carried_churn": {"coal": 5, "oak": 0, "bad": "x"},
            "skilling_bank_run": {"reviews_remaining": 9, "target_id": "coal"},
        }
        sanitize_carried_state(data)
        self.assertEqual(data["carried_keep_drop"], {"coal": "drop"})
        self.assertEqual(data["carried_churn"], {"coal": 5})
        self.assertEqual(data["skilling_bank_run"], {"reviews_remaining": 1, "target_id": "coal"})

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


class TestLootFilter(unittest.TestCase):
    def test_splits_kept_and_left_by_value_with_safe_defaults(self):
        values = {"Rune bar": 2000, "Feather": 6, "Raw chicken": 60}
        stackable = {"Feather"}
        kept, left = filter_loot_pure(
            {"Rune bar": 1, "Feather": 100, "Raw chicken": 1, "Bones": 3, "Coins": 50},
            values, threshold=10, stackable_names=stackable,
        )
        # Rune bar (high value) kept; Feather stackable-kept; Raw chicken (h-alch 36
        # >= 10) kept; Bones unknown-value kept; Coins always kept.
        self.assertEqual(kept, {"Rune bar": 1, "Feather": 100, "Raw chicken": 1, "Bones": 3, "Coins": 50})
        self.assertEqual(left, {})

    def test_leaves_only_below_threshold_known_unstackable_junk(self):
        values = {"Feather": 6, "Rune bar": 2000}
        kept, left = filter_loot_pure(
            {"Feather": 40, "Rune bar": 1}, values, threshold=10, stackable_names=set(),
        )
        # Feather high-alch 3 < 10 and not stackable here -> left; Rune bar kept.
        self.assertEqual(kept, {"Rune bar": 1})
        self.assertEqual(left, {"Feather": 40})

    def test_overrides_win_over_threshold_and_value(self):
        values = {"Bones": 1, "Rune bar": 2000}
        overrides = {"Bones": "keep", "Rune bar": "leave"}
        kept, left = filter_loot_pure(
            {"Bones": 3, "Rune bar": 1, "Coins": 50}, values, threshold=10,
            stackable_names=set(), overrides=overrides,
        )
        # Force-keep a below-threshold item; force-leave a valuable one; coins are
        # exempt from a "leave" and always kept.
        self.assertEqual(kept, {"Bones": 3, "Coins": 50})
        self.assertEqual(left, {"Rune bar": 1})


class TestProcessingPackAndAdvancedLayout(unittest.TestCase):
    def test_pack_processing_inputs_splits_evenly_capped_by_bank(self):
        bank = {"Tin ore": 100, "Copper ore": 100}
        packed = pack_processing_inputs_pure(bank, {"Tin ore": 1, "Copper ore": 1}, 28, set())
        self.assertEqual(packed, {"Tin ore": 14, "Copper ore": 14})

    def test_pack_processing_inputs_caps_by_scarce_bank_supply(self):
        bank = {"Tin ore": 3, "Copper ore": 100}
        packed = pack_processing_inputs_pure(bank, {"Tin ore": 1, "Copper ore": 1}, 28, set())
        self.assertEqual(packed, {"Tin ore": 3, "Copper ore": 14})

    def test_pack_processing_inputs_single_requirement_fills_all_capacity(self):
        bank = {"Logs": 500}
        packed = pack_processing_inputs_pure(bank, {"Logs": 1}, 28, set())
        self.assertEqual(packed, {"Logs": 28})

    def test_pack_processing_inputs_stackable_takes_one_slot_then_unstackables_split_rest(self):
        bank = {"Nature rune": 9999, "Pure essence": 100}
        packed = pack_processing_inputs_pure(bank, {"Nature rune": 1, "Pure essence": 1}, 28, {"Nature rune"})
        self.assertEqual(packed["Nature rune"], 9999)
        self.assertEqual(packed["Pure essence"], 27)

    def test_pack_processing_inputs_empty_requirements_or_bank(self):
        self.assertEqual(pack_processing_inputs_pure({}, {"Logs": 1}, 28, set()), {})
        self.assertEqual(pack_processing_inputs_pure({"Logs": 5}, {}, 28, set()), {})

    def test_apply_carried_layout_caps_by_bank_and_capacity(self):
        bank = {"Iron ore": 10, "Ammo mould": 1}
        layout = {"Ammo mould": 1, "Iron ore": 50}
        applied = apply_carried_layout_pure(bank, layout, 28, set())
        self.assertEqual(applied["Ammo mould"], 1)
        self.assertEqual(applied["Iron ore"], 10)

    def test_apply_carried_layout_stops_at_capacity(self):
        bank = {f"Item {i}": 1 for i in range(30)}
        layout = {f"Item {i}": 1 for i in range(30)}
        applied = apply_carried_layout_pure(bank, layout, 5, set())
        self.assertEqual(sum(applied.values()), 5)

    def test_carried_advanced_for_defaults_false(self):
        self.assertFalse(carried_advanced_for({}, "smelt_bronze_bar"))
        self.assertTrue(carried_advanced_for({"carried_advanced_targets": {"smelt_bronze_bar": True}}, "smelt_bronze_bar"))
        self.assertFalse(carried_advanced_for({"carried_advanced_targets": {"other": True}}, "smelt_bronze_bar"))

    def test_sanitize_seeds_layout_and_advanced_targets(self):
        data = {}
        sanitize_carried_state(data)
        self.assertEqual(data["carried_layout"], {})
        self.assertEqual(data["carried_advanced_targets"], {})


class TestLayoutToGridCells(unittest.TestCase):
    def test_unstackable_takes_one_cell_per_unit_stackable_takes_one_cell(self):
        cells = layout_to_grid_cells_pure({"Logs": 3, "Nature rune": 500}, {"Nature rune"}, capacity=28)
        self.assertEqual(len(cells), 28)
        non_empty = [c for c in cells if c[0] is not None]
        self.assertEqual(non_empty.count(("Logs", 1)), 3)
        self.assertIn(("Nature rune", 500), non_empty)
        self.assertEqual(cells.count((None, 0)), 28 - 4)

    def test_empty_layout_is_all_empty_cells(self):
        self.assertEqual(layout_to_grid_cells_pure({}, set(), capacity=28), [(None, 0)] * 28)

    def test_overflow_beyond_capacity_is_simply_not_shown(self):
        cells = layout_to_grid_cells_pure({"Logs": 40}, set(), capacity=28)
        self.assertEqual(len(cells), 28)
        self.assertEqual(cells.count(("Logs", 1)), 28)


class TestGateForceTrigger(unittest.TestCase):
    def test_force_triggers_a_bank_run_even_with_low_churn(self):
        # A lopsided recipe can run out of one input long before churn hits
        # capacity; `force` lets the caller (processing) trigger banking anyway.
        state, view, churn, event, act = carried_bank_run_gate_pure(
            {"Iron ore": 0, "Coal": 20}, churn=2, keep=True, stackable_names=set(),
            target_id="smelt_iron_bar", bank_run_state={}, force=True,
        )
        self.assertFalse(act)
        self.assertTrue(event["active"])

    def test_no_force_no_full_churn_means_act_normally(self):
        state, view, churn, event, act = carried_bank_run_gate_pure(
            {"Iron ore": 5}, churn=2, keep=True, stackable_names=set(),
            target_id="smelt_iron_bar", bank_run_state={}, force=False,
        )
        self.assertTrue(act)
        self.assertFalse(event["active"])


class TestBagCapacity(unittest.TestCase):
    def test_coal_bag_raises_capacity_only_when_carrying_coal(self):
        self.assertEqual(effective_carried_capacity({"Coal": 5}, set()), CARRIED_CAPACITY)
        self.assertEqual(effective_carried_capacity({"Coal": 5}, {"Coal bag"}), CARRIED_CAPACITY + 27)
        # Owned but not carrying coal -> no bump.
        self.assertEqual(effective_carried_capacity({"Oak logs": 5}, {"Coal bag"}), CARRIED_CAPACITY)

    def test_gate_uses_the_raised_capacity(self):
        # With a coal bag (capacity 55), churn 40 does not yet force a bank-run.
        state, view, churn, event, act = carried_bank_run_gate_pure(
            {"Coal": 40}, 40, keep=True, stackable_names=set(), target_id="coal",
            bank_run_state={}, capacity=CARRIED_CAPACITY + 27,
        )
        self.assertTrue(act)
        self.assertFalse(event["active"])
        # At 55 it does.
        state, view, churn, event, act = carried_bank_run_gate_pure(
            {"Coal": 55}, 55, keep=True, stackable_names=set(), target_id="coal",
            bank_run_state={}, capacity=CARRIED_CAPACITY + 27,
        )
        self.assertFalse(act)
        self.assertTrue(event["completed"])


class TestBankRunStateMachine(unittest.TestCase):
    def test_one_review_run_starts_and_completes_in_one_answer(self):
        state, event = bank_run_progress_pure({}, needed=True, target_id="coal", reviews_cost=1)
        self.assertEqual(state, {})
        self.assertTrue(event["started"])
        self.assertTrue(event["completed"])

    def test_no_run_when_not_needed(self):
        state, event = bank_run_progress_pure({}, needed=False, target_id="coal", reviews_cost=1)
        self.assertEqual(state, {})
        self.assertFalse(event["active"])
        self.assertFalse(event["completed"])

    def test_two_review_run_takes_two_answers(self):
        # First answer starts the run and consumes one review, still in progress.
        state, event = bank_run_progress_pure({}, needed=True, target_id="rats", reviews_cost=2)
        self.assertEqual(state, {"reviews_remaining": 1, "target_id": "rats"})
        self.assertTrue(event["started"])
        self.assertFalse(event["completed"])
        # Second answer completes it (needed is irrelevant once a run is active).
        state, event = bank_run_progress_pure(state, needed=False, target_id="rats", reviews_cost=2)
        self.assertEqual(state, {})
        self.assertTrue(event["completed"])

    def test_switching_target_abandons_an_active_run(self):
        active = {"reviews_remaining": 1, "target_id": "rats"}
        state, event = bank_run_progress_pure(active, needed=False, target_id="coal", reviews_cost=2)
        self.assertEqual(state, {})
        self.assertFalse(event["active"])

    def test_sanitize_caps_remaining_at_cost_and_drops_empty(self):
        state, _ = bank_run_progress_pure({"reviews_remaining": 99, "target_id": "rats"}, False, "rats", 2)
        # capped to 2 then decremented to 1
        self.assertEqual(state, {"reviews_remaining": 1, "target_id": "rats"})


class TestCarriedOverlayAdvance(unittest.TestCase):
    def test_delta_gains_excludes_coins_and_losses(self):
        before = {"Coal": 5, "Coins": 100, "Bronze bar": 2}
        after = {"Coal": 8, "Coins": 150, "Bronze bar": 1}
        self.assertEqual(inventory_delta_gains(before, after), {"Coal": 3})

    def test_churn_is_max_of_gained_and_consumed_slots(self):
        # Gather: gain 1, consume 0 -> 1.
        self.assertEqual(carried_action_churn_pure({}, {"Coal": 1}, set()), 1)
        # Consumption (firemaking): consume 1 log, gain nothing -> 1.
        self.assertEqual(carried_action_churn_pure({"Logs": 5}, {"Logs": 4}, set()), 1)
        # Multi-output gather: gain 3 -> 3.
        self.assertEqual(carried_action_churn_pure({}, {"Coal": 3}, set()), 3)
        # 1:1 processing: consume 1 bar, gain 1 item -> max(1,1) = 1.
        self.assertEqual(
            carried_action_churn_pure({"Steel bar": 2}, {"Steel bar": 1, "Dart tip": 1}, set()), 1
        )

    def _gather_tick(self, view, churn, state, gain=None, consume_before=None, consume_after=None):
        """One tick: gate, and if acting apply the churn and fold gains."""
        state, view, churn, event, act = carried_bank_run_gate_pure(
            view, churn, keep=True, stackable_names=set(), target_id="coal", bank_run_state=state,
        )
        if act:
            if consume_before is not None:
                churn += carried_action_churn_pure(consume_before, consume_after, set())
            else:
                churn += carried_action_churn_pure({}, gain or {}, set())
                view = carried_fold_gains_pure(view, gain or {}, set())
        return view, churn, state, event, act

    def test_gathering_fills_then_a_tick_banks_no_xp_then_resumes(self):
        view, churn, state = {}, 0, {}
        acted = 0
        for _ in range(28):
            view, churn, state, event, act = self._gather_tick(view, churn, state, gain={"Coal": 1})
            acted += 1 if act else 0
        self.assertEqual(acted, 28)
        self.assertEqual(churn, CARRIED_CAPACITY)
        self.assertEqual(carried_slots_used(view, set()), CARRIED_CAPACITY)
        # 29th tick is spent banking: no action, run completes, view + churn reset.
        view, churn, state, event, act = self._gather_tick(view, churn, state, gain={"Coal": 1})
        self.assertFalse(act)
        self.assertTrue(event["completed"])
        self.assertEqual(view, {})
        self.assertEqual(churn, 0)
        # 30th gathers again.
        view, churn, state, event, act = self._gather_tick(view, churn, state, gain={"Coal": 1})
        self.assertTrue(act)
        self.assertEqual(carried_slots_used(view, set()), 1)

    def test_consumption_skill_gets_teeth_with_an_empty_view(self):
        # Firemaking burns a log per tick and produces nothing carried; churn still
        # accrues from consumed input slots, so it banks at 28 with an empty view.
        view, churn, state = {}, 0, {}
        logs = 100
        for _ in range(28):
            view, churn, state, event, act = self._gather_tick(
                view, churn, state, consume_before={"Logs": logs}, consume_after={"Logs": logs - 1}
            )
            if act:
                logs -= 1
        self.assertEqual(churn, CARRIED_CAPACITY)
        self.assertEqual(view, {})  # nothing carried, but teeth still bite
        view, churn, state, event, act = self._gather_tick(
            view, churn, state, consume_before={"Logs": logs}, consume_after={"Logs": logs - 1}
        )
        self.assertFalse(act)
        self.assertTrue(event["completed"])

    def test_drop_always_acts_and_never_banks(self):
        # Drop never banks; it also does not destroy items already in the pack.
        state, view, churn, event, act = carried_bank_run_gate_pure(
            {"Coal": 28}, 999, keep=False, stackable_names=set(), target_id="coal", bank_run_state={},
        )
        self.assertTrue(act)
        self.assertEqual(view, {"Coal": 28})
        self.assertFalse(event["active"])

    def test_fold_excludes_coins(self):
        view = carried_fold_gains_pure({}, {"Coins": 500, "Coal": 2}, set())
        self.assertEqual(view, {"Coal": 2})


if __name__ == "__main__":
    unittest.main()
