from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _load_addon_as_package,
    copy,
    sys,
    types,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_court_case_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_court_entry_integration")
        logic = sys.modules[f"{addon.__name__}.logic.court_cases_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "quests": {"kings_ransom": {"completed": True}},
            "attack_level": 65,
            "defense_level": 65,
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "smithing_level": 1,
        }
        initial.update(logic.default_court_cases_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_court_cases_command"](
            "enter", {"role": "prosecution", "automation_mode": "casual"}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["court_cases"]["case_id"], "mugger")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_circus_policy_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_circus_policy_integration")
        logic = sys.modules[f"{addon.__name__}.logic.circus_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "circus": logic.default_circus_state_pure(),
            "inventory": {},
            "quests": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "make_soft_clay",
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_circus_command"](
            "set_policy",
            {
                "performance_id": "magic",
                "automation_mode": "casual",
                "strategy": "max_xp",
            },
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "make_soft_clay")
        self.assertEqual(addon._state.player_data["circus"]["selected_performance"], "magic")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_trouble_brewing_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_trouble_brewing_integration")
        logic = sys.modules[f"{addon.__name__}.logic.trouble_brewing_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "quests": {"cabin_fever": {"completed": True}},
            "cooking_level": 40,
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "smithing_level": 1,
        }
        initial.update(logic.default_trouble_brewing_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_trouble_brewing_command"](
            "enter", {"automation_mode": "advanced", "duty": "sabotage"}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "trouble_brewing")
        self.assertEqual(addon._state.player_data["trouble_brewing"]["duty"], "sabotage")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        addon._state.player_data["trouble_brewing_pieces_of_eight"] = 600
        before_purchase = copy.deepcopy(addon._state.player_data)
        result = captured["on_trouble_brewing_command"](
            "buy_reward", {"reward_id": "phasmatys_flag"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Phasmatys flag"], 1)
        self.assertEqual(addon._state.player_data["trouble_brewing_pieces_of_eight"], 0)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, before_purchase)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        addon._state.player_data["trouble_brewing_pieces_of_eight"] = 2
        before_rum = copy.deepcopy(addon._state.player_data)
        result = captured["on_trouble_brewing_command"](
            "buy_reward", {"reward_id": "red_rum"}
        )
        self.assertTrue(result["ok"])
        purchased_rum = copy.deepcopy(addon._state.player_data)
        result = captured["on_drink_trouble_brewing_rum"]("Red rum")
        self.assertTrue(result["ok"])
        self.assertNotIn("Red rum", addon._state.player_data["inventory"])
        self.assertEqual(result["destination"], "Trouble Brewing")

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, purchased_rum)
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, before_rum)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        addon._state.player_data["trouble_brewing_pieces_of_eight"] = 5_000
        before_clue = copy.deepcopy(addon._state.player_data)
        result = captured["on_trouble_brewing_command"](
            "buy_reward", {"reward_id": "medium_clue"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["inventory"]["Clue scroll (medium)"],
            1,
        )
        self.assertEqual(addon._state.player_data["trouble_brewing_pieces_of_eight"], 0)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, before_clue)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_castle_wars_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_castle_wars_integration")
        logic = sys.modules[f"{addon.__name__}.logic.castle_wars_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "combat_supply_loadout": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "smithing_level": 1,
        }
        initial.update(logic.default_castle_wars_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_castle_wars_command"](
            "enter",
            {"automation_mode": "advanced", "duty": "defend", "team": "zamorak"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "castle_wars")
        self.assertEqual(addon._state.player_data["castle_wars"]["duty"], "defend")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_pest_control_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_pest_control_integration")
        logic = sys.modules[f"{addon.__name__}.logic.pest_control_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "combat_supply_loadout": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 40,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_pest_control_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_pest_control_command"](
            "enter",
            {"automation_mode": "advanced", "lander_id": "novice", "duty": "defend"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "pest_control")
        self.assertEqual(addon._state.player_data["pest_control"]["duty"], "defend")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_conquest_setup_entry_and_resignation_are_direct_undoable_actions(self):
        addon = _load_addon_as_package("ankiscape_conquest_integration")
        logic = sys.modules[f"{addon.__name__}.logic.conquest_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "pest_control_commendations": 0,
            "music_log": {"version": 1, "unlocked_tracks": []},
            "achievement_diaries": {"completed_tasks": []},
            "quests": {},
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 40,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_conquest_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        callback = captured["on_conquest_command"]
        setup = callback(
            "set_policy",
            {"automation_mode": "casual", "doctrine": "aggressive"},
        )
        self.assertTrue(setup["ok"])
        after_setup = copy.deepcopy(addon._state.player_data)
        entered = callback("enter", {})
        self.assertTrue(entered["ok"])
        active = copy.deepcopy(addon._state.player_data)
        resigned = callback("resign", {})
        self.assertTrue(resigned["ok"])
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action"] * 3,
        )

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, active)
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, after_setup)
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_soul_wars_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_soul_wars_integration")
        logic = sys.modules[f"{addon.__name__}.logic.soul_wars_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "combat_encounter": {},
            "combat_supply_loadout": {"food": {}},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 40,
            "slayer_level": 40,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_soul_wars_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_soul_wars_command"](
            "enter",
            {"automation_mode": "advanced", "duty": "defend", "team": "creation"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "soul_wars")
        self.assertEqual(addon._state.player_data["soul_wars"]["duty"], "defend")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_shades_pyre_logs_are_direct_undoable_and_award_firemaking_xp(self):
        addon = _load_addon_as_package("ankiscape_shades_mortton_integration")
        logic = sys.modules[f"{addon.__name__}.logic.shades_of_mortton_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon.level_up_check = lambda *_args: None
        addon._show_exp = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Logs": 1, "Sacred oil (4)": 1},
            "equipment": {},
            "combat_encounter": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "quests": {"shades_of_mortton": {"completed": True}},
            "firemaking_level": 80,
            "firemaking_exp": 0.0,
            "smithing_level": 1,
        }
        initial.update(logic.default_shades_of_mortton_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_shades_of_mortton_command"](
            "make_pyre_logs",
            {"output_name": "Pyre logs"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Pyre logs"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Sacred oil (2)"], 1)
        self.assertEqual(addon._state.player_data["firemaking_exp"], 12.0)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
