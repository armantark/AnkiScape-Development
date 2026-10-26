from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _load_addon_as_package,
    copy,
    sys,
    types,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_reward_claim_recomputes_level_before_achievements_and_is_undoable(self):
        addon = _load_addon_as_package("ankiscape_reward_claim_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        initial = {
            "inventory": {},
            "claims": {},
            "quests": {
                "stolen_hearts": {"started": True, "progress": 3, "completed": True},
            },
            "agility_level": 1,
            "agility_exp": 0.0,
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Agility"
        calls = {"levels": [], "achievement_levels": [], "xp": []}

        def _level_up(skill_name, data):
            calls["levels"].append(skill_name)
            data["agility_level"] = addon.calculate_new_level(
                data["agility_exp"], data["agility_level"], addon.EXP_TABLE
            )

        addon.level_up_check = _level_up
        addon.check_achievements = lambda data: calls["achievement_levels"].append(data["agility_level"])
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None

        self.assertTrue(addon.on_claim_reward("stolen_hearts_xp_lamp_2", "agility"))
        self.assertEqual(addon._state.player_data["agility_exp"], 250.0)
        self.assertEqual(addon._state.player_data["agility_level"], 3)
        self.assertEqual(calls, {"levels": ["Agility"], "achievement_levels": [3], "xp": [250.0]})
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(addon.mw.undo_updates, 1)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_stronghold_reward_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_stronghold_reward_direct_action_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        initial = {
            "inventory": {"Coins": 5},
            "stronghold_of_security": {"step": 4, "completed": True, "boots_choice": None},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Mining"
        addon.ui.show_stronghold_reward_dialog = lambda: "Fancy boots"
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None

        self.assertTrue(addon._claim_stronghold_reward())
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 5 + addon.STRONGHOLD_REWARD_COINS)
        self.assertEqual(addon._state.player_data["inventory"]["Fancy boots"], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(addon.mw.undo_updates, 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_mage_arena_statue_switch_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_mage_arena_cape_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Magic"
        initial = {
            "inventory": {
                "Saradomin cape": 1,
                "Guthix staff": 1,
            },
            "equipment": {},
            "mage_arena": {
                "step": 5,
                "completed": True,
                "alignment": "saradomin",
                "attuned_spells": ["saradomin_strike"],
            },
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None

        addon._on_main_menu()
        apply_action = captured["on_mage_arena_action"]
        self.assertTrue(apply_action("cape", "guthix"))
        self.assertEqual(addon._state.player_data["mage_arena"]["alignment"], "guthix")
        self.assertEqual(addon._state.player_data["inventory"]["Saradomin cape"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Guthix cape"], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_shooting_star_exchange_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_shooting_star_exchange_integration"
        )
        star_logic = sys.modules[
            f"{addon.__name__}.logic.shooting_star_logic"
        ]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(
            kwargs
        )
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Stardust": 200},
            "shop_market_clock": {"answered_cards": 20},
            "world_population_profile": "normal",
            "shooting_star": star_logic.default_shooting_star_state_pure(),
            "smithing_level": 1,
        }
        initial, _ = star_logic.advance_shooting_star_world_clock_pure(
            initial
        )
        initial["shooting_star"]["active_event"].update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_card": 22,
            }
        )
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None

        addon._on_main_menu()
        result = captured["on_shooting_star_command"]("exchange", {})

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Stardust"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 50_002)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_fist_of_guthix_reward_purchase_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_fist_of_guthix_reward_integration"
        )
        fog_logic = sys.modules[f"{addon.__name__}.logic.fist_of_guthix_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "equipment_instances": {},
            "equipment_instance_next_id": 1,
            "fist_of_guthix": fog_logic.default_fist_of_guthix_state_pure(),
            "smithing_level": 1,
        }
        initial["fist_of_guthix"]["tokens"] = 100
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None

        addon._on_main_menu()
        result = captured["on_fist_of_guthix_command"](
            "buy_reward", {"reward_id": "combat_hood"}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Combat hood 100"], 1)
        self.assertEqual(addon._state.player_data["fist_of_guthix"]["tokens"], 50)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_penguin_selection_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_penguin_selection_integration"
        )
        penguin_logic = sys.modules[
            f"{addon.__name__}.logic.penguin_hide_and_seek_logic"
        ]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "equipment": {},
            "quests": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "penguin_hide_and_seek",
            "penguin_hide_and_seek": penguin_logic.default_penguin_state_pure(),
            "completed_achievements": [],
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.check_achievements = lambda *_args: None

        spawn_id = penguin_logic.penguin_roster_pure(initial)[0]["id"]
        addon._on_main_menu()
        result = captured["on_penguin_command"](
            "select_spy",
            {"spawn_id": spawn_id},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["penguin_hide_and_seek"]["selected_id"],
            spawn_id,
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)
        selected = copy.deepcopy(addon._state.player_data)

        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )
        self.assertIn(
            spawn_id,
            addon._state.player_data["penguin_hide_and_seek"]["spotted_ids"],
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="Answer Card")
        )
        self.assertEqual(addon._state.player_data, selected)
        self.assertEqual(addon._state.review_undo_stack, [])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_penguin_point_redemption_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package(
            "ankiscape_penguin_redemption_integration"
        )
        penguin_logic = sys.modules[
            f"{addon.__name__}.logic.penguin_hide_and_seek_logic"
        ]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {},
            "penguin_hide_and_seek": penguin_logic.default_penguin_state_pure(),
            "smithing_level": 1,
        }
        initial["penguin_hide_and_seek"]["points"] = 2
        addon._state.player_data = copy.deepcopy(initial)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None

        addon._on_main_menu()
        result = captured["on_penguin_command"]("redeem_coins", {})

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 13_000)
        self.assertEqual(addon._state.player_data["penguin_hide_and_seek"]["points"], 0)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_vinesweeper_loaded_addon_review_and_direct_actions_are_undoable(self):
        addon = _load_addon_as_package("ankiscape_vinesweeper_e2e")
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        hooks = sys.modules["aqt"].gui_hooks
        self.assertEqual(len(hooks.state_did_undo), 1)
        undo = hooks.state_did_undo[0]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon.level_up_check = lambda *_args: None
        addon._show_activity_gain = lambda *_args: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._review_action_multiplier = lambda: 1
        addon._state.current_skill = "Activities"

        initial = storage.default_player_data(
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        initial["inventory"].update({"Spade": 1, "Coins": 10})
        initial["farming_level"] = 40
        addon._state.player_data = copy.deepcopy(initial)
        addon._on_main_menu()

        entered_result = captured["on_vinesweeper_command"]("enter", {})
        self.assertTrue(entered_result["ok"], entered_result)
        captured["on_set_utility"]("vinesweeper")
        entered = copy.deepcopy(addon._state.player_data)
        self.assertTrue(entered["vinesweeper"]["active"])
        self.assertEqual(entered["vinesweeper"]["flags"], 10)
        self.assertEqual(entered["current_utility"], "vinesweeper")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(addon.mw.undo_updates, 1)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        original_random = addon.random.random
        addon.random.random = lambda: 0.99
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        reviewer = sys.modules["aqt.reviewer"].Reviewer()
        self.assertIsNone(reviewer._answerCard(4))

        earned = copy.deepcopy(addon._state.player_data)
        self.assertEqual(earned["vinesweeper"]["operations"], 1)
        self.assertEqual(earned["vinesweeper"]["rabbits_repulsed"], 1)
        self.assertEqual(earned["vinesweeper"]["points"], 280)
        self.assertEqual(earned["inventory"]["Coins"], 0)
        self.assertEqual(earned["hunter_exp"], 30.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        bought = captured["on_vinesweeper_command"](
            "buy_reward",
            {"reward_id": "cabbage_seed", "quantity": 2},
        )
        self.assertTrue(bought["ok"], bought)
        self.assertEqual(addon._state.player_data["inventory"]["Cabbage seed"], 2)
        self.assertEqual(addon._state.player_data["vinesweeper"]["points"], 260)
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action"] * 2,
        )
        self.assertEqual(addon.mw.undo_updates, 2)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 2)
        undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, earned)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        redeemed = captured["on_vinesweeper_command"](
            "redeem_farming_xp",
            {"points": 280},
        )
        self.assertTrue(redeemed["ok"], redeemed)
        self.assertEqual(addon._state.player_data["vinesweeper"]["points"], 0)
        self.assertEqual(
            addon._state.player_data["farming_exp"],
            earned["farming_exp"] + 280.0,
        )
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action"] * 3,
        )
        self.assertEqual(addon.mw.undo_updates, 3)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 2)
        undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, earned)
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, entered)
        self.assertEqual(addon._state.review_undo_stack, [])

        undo(types.SimpleNamespace(operation="AnkiScape direct action"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
