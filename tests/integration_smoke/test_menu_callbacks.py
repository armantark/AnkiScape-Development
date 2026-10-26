from tests.test_integration_smoke import _DummyCol, _DummyMW, _load_addon_as_package, copy, types
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_slayer_assignment_roll_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_slayer_assignment_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Combat"
        initial = {
            "inventory": {},
            "quests": {},
            "slayer_level": 1,
            "slayer_exp": 0.0,
            "slayer_assignment": {},
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        original_random = addon.random.random
        rolls = iter((0.0, 0.0))
        addon.random.random = lambda: next(rolls)
        self.addCleanup(setattr, addon.random, "random", original_random)

        addon._on_main_menu()
        result = captured["on_slayer_command"](
            "get_assignment", {"master_id": "turael_spria"}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["slayer_assignment"]["family_id"], "bats")
        self.assertEqual(addon._state.player_data["slayer_assignment"]["remaining"], 15)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_grand_exchange_buy_and_sell_offers_are_direct_bank_run_actions(self):
        addon = _load_addon_as_package(
            "ankiscape_grand_exchange_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Utility / Activities"
        initial = {
            "inventory": {"Coins": 10_000},
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        bank_runs = []

        def request_bank_run(data):
            bank_runs.append(copy.deepcopy(data))
            return copy.deepcopy(data), True, "", False

        addon._request_active_bank_run_state = request_bank_run

        addon._on_main_menu()
        guide_price = int(addon.GE_ITEM_CATALOG["Logs"]["guide_price"])
        payload = {
            "side": "buy",
            "item_name": "Logs",
            "quantity": 1,
            "unit_price": guide_price,
        }
        preview = captured["on_ge_action"]("preview_offer", payload)
        self.assertTrue(preview["ok"])
        self.assertEqual(addon._state.direct_action_undo_stack, [])
        self.assertEqual(bank_runs, [])

        result = captured["on_ge_action"]("place_offer", payload)
        self.assertTrue(result["ok"])
        self.assertTrue(result["bank_run_triggered"])
        self.assertEqual(len(bank_runs), 1)
        self.assertEqual(
            addon._state.player_data["inventory"]["Coins"],
            10_000 - guide_price,
        )
        self.assertEqual(len(addon._state.player_data["ge_player_orders"]), 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        addon._state.player_data["inventory"]["Logs"] = 2
        sell_initial = copy.deepcopy(addon._state.player_data)
        sell = captured["on_ge_action"](
            "place_offer",
            {
                "side": "sell",
                "item_name": "Logs",
                "quantity": 1,
                "unit_price": guide_price,
            },
        )
        self.assertTrue(sell["ok"])
        self.assertTrue(sell["bank_run_triggered"])
        self.assertEqual(len(bank_runs), 2)
        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, sell_initial)

        settings = captured["on_ge_action"](
            "set_offer_safety",
            {
                "high_value_confirmation": 1_000_000,
                "low_price_percent": 10,
                "high_price_multiplier": 5,
            },
        )
        self.assertTrue(settings["ok"])
        self.assertNotIn("bank_run_triggered", settings)
        self.assertEqual(len(bank_runs), 2)

    def test_combat_current_target_drives_main_menu_carried_pack_callbacks(self):
        addon = _load_addon_as_package("ankiscape_combat_carried_target_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        save_calls = []
        addon.save_player_data = lambda: save_calls.append(copy.deepcopy(addon._state.player_data))
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "current_combat_target": "ghost",
            "current_prayer": "bury_bones",
            "inventory": {"Bonecrusher": 1, "Ectoplasmator": 1},
            "smithing_level": 1,
            "carried_advanced_targets": {"ghost": True},
            "carried_layout": {
                "ghost": {"Bonecrusher": 1},
                "bury_bones": {"Bones": 1},
            },
        }

        addon._on_main_menu()

        captured["on_save_player_data"]()
        self.assertEqual(save_calls, [addon._state.player_data])
        self.assertTrue(captured["carried_pack_target_active"])
        self.assertTrue(captured["carried_advanced_state"])
        cells = captured["get_carried_layout_cells"]()
        self.assertIn(("Bonecrusher", 1), cells)
        self.assertNotIn(("Bones", 1), cells)
        self.assertTrue(captured["on_set_carried_layout_quantity"]("Ectoplasmator", 4))
        self.assertEqual(
            addon._state.player_data["carried_layout"]["ghost"],
            {"Bonecrusher": 1, "Ectoplasmator": 4},
        )
        self.assertIn("Air rune", captured["carried_stackable_names"])

    def test_combat_main_menu_loot_rows_only_include_observed_drops(self):
        addon = _load_addon_as_package("ankiscape_combat_observed_loot_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "current_combat_target": "cyclops",
            "combat_observed_drops": {
                "cyclops": {
                    "Coins": {"times_seen": 1, "quantity_seen": 3},
                },
            },
            "inventory": {},
            "smithing_level": 1,
        }

        addon._on_main_menu()

        row_names = {row["item"] for row in captured["loot_override_rows"]}
        self.assertIn("Coins", row_names)
        self.assertNotIn("Big bones", row_names)

    def test_agility_current_target_projects_auto_food_requirements_and_weight_in_main_menu(self):
        addon = _load_addon_as_package("ankiscape_agility_carried_target_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon._state.current_skill = "Agility"
        addon._state.player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "inventory": {"Shark": 2},
            "equipment": {},
            "combat_auto_eat_food": ["Shark"],
            "smithing_level": 1,
        }

        addon._on_main_menu()

        self.assertTrue(captured["carried_pack_target_active"])
        self.assertFalse(captured["carried_auto_is_combat"])
        summary = captured["get_carried_auto_summary"]()
        self.assertIn("Wilderness Agility Course Auto pack", summary)
        self.assertIn("Food: Shark x2", summary)
        self.assertIn("Weight: 1.2 kg carried", summary)
        self.assertEqual(captured["get_carried_bank_run_summary"](), "Bank run: ready")

    def test_gnome_ball_activity_exposes_its_dangerous_carried_pack_in_main_menu(self):
        addon = _load_addon_as_package("ankiscape_gnome_ball_carried_target_integration")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon._state.current_skill = "Utility / Activities"
        addon._state.player_data = {
            "current_utility": "gnome_ball",
            "inventory": {"Shark": 2},
            "carried_inventory": {"gnome_ball": {"Shark": 2}},
            "smithing_level": 1,
        }

        addon._on_main_menu()

        self.assertTrue(captured["carried_pack_target_active"])
        self.assertEqual(captured["active_carried_target_id"], "gnome_ball")
        self.assertIn("gnome_ball Auto pack", captured["get_carried_auto_summary"]())

    def test_agility_main_menu_summary_ignores_stale_carried_items(self):
        addon = _load_addon_as_package("ankiscape_agility_stale_carried_summary")
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon._state.current_skill = "Agility"
        addon._state.player_data = {
            "current_agility": "wilderness_course",
            "agility_level": 53,
            "inventory": {"Shark": 1},
            "equipment": {},
            "combat_auto_eat_food": ["Shark"],
            "smithing_level": 1,
            "carried_primed_targets": {"wilderness_course": True},
            "carried_inventory": {
                "wilderness_course": {
                    "Shark": 1,
                    "Dragon bones": 20,
                },
            },
        }

        addon._on_main_menu()

        summary = captured["get_carried_auto_summary"]()
        self.assertIn("Food: Shark x1", summary)
        self.assertIn("Weight: 0.6 kg carried", summary)
