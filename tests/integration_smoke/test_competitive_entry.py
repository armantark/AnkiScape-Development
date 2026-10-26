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
    def test_treasure_trail_read_and_casket_are_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_treasure_trails_e2e")
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
            "inventory": {"Casket (easy)": 1},
            "equipment": {},
            "combat_encounter": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "treasure_trail": {},
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_treasure_trails_command"](
            "open_casket", {"tier": "easy"}
        )
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["rewards"])
        self.assertNotIn("Casket (easy)", addon._state.player_data["inventory"])
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_daily_challenge_hand_in_is_direct_and_undoable(self):
        """The whole chain: a loaded add-on, a real hand-in, and one undo."""
        addon = _load_addon_as_package("ankiscape_daily_challenges_e2e")
        data_module = sys.modules[f"{addon.__name__}.data.daily_challenges_data"]
        logic = sys.modules[f"{addon.__name__}.logic.daily_challenges_logic"]
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
        spec = data_module.DAILY_CHALLENGE_DATA["mining_copper_ore"]
        initial = {
            "inventory": {"Copper ore": int(spec["required"])},
            "equipment": {},
            "combat_encounter": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "mining_level": 1,
            "mining_exp": 0.0,
            "smithing_level": 1,
        }
        initial.update(logic.default_daily_challenges_state_pure())
        initial["daily_challenges"] = [
            {
                "instance_id": "mining_copper_ore-1",
                "challenge_id": "mining_copper_ore",
                "day": 1,
                "progress": int(spec["required"]),
                "credited": {"Copper ore": int(spec["required"])},
            }
        ]
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_daily_challenges_command"](
            "claim", {"instance_id": "mining_copper_ore-1"}
        )
        self.assertTrue(result["ok"], result)
        self.assertEqual(addon._state.player_data["daily_challenges"], [])
        self.assertEqual(
            addon._state.player_data["inventory"][data_module.DAILY_CHALLENGE_MYSTERY_BAG_ITEM],
            1,
        )
        self.assertEqual(addon._state.player_data["mining_exp"], float(spec["reward_xp"]))
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_a_review_day_assigns_a_challenge_through_the_loaded_addon(self):
        addon = _load_addon_as_package("ankiscape_daily_challenges_clock")
        logic = sys.modules[f"{addon.__name__}.logic.daily_challenges_logic"]
        data_module = sys.modules[f"{addon.__name__}.data.daily_challenges_data"]
        day = int(data_module.DAILY_CHALLENGE_REVIEW_DAY)
        player = {
            "inventory": {},
            "shop_market_clock": {"answered_cards": day},
            "mining_level": 1,
            "cooking_level": 1,
            "fishing_level": 1,
            "firemaking_level": 1,
            "woodcutting_level": 1,
            "constitution_level": 10,
        }
        player.update(logic.default_daily_challenges_state_pure())

        updated, events = logic.advance_daily_challenges_day_pure(player, lambda: 0.0)

        self.assertEqual(len(events["assigned"]), 1)
        self.assertEqual(updated["daily_challenge_day"], 1)
        self.assertIn(
            "New Daily Challenge", updated["daily_challenge_last_result"]
        )

    def test_tzhaar_fight_pit_entry_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_fight_pit_integration")
        logic = sys.modules[f"{addon.__name__}.logic.tzhaar_fight_pit_logic"]
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
            "shop_market_clock": {"answered_cards": 0},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 60,
            "constitution_level": 60,
            "ranged_level": 1,
            "magic_level": 1,
            "prayer_level": 43,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_tzhaar_fight_pit_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_tzhaar_fight_pit_command"](
            "enter", {"policy": "aggressive"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "tzhaar_fight_pit")
        self.assertEqual(addon._state.player_data["tzhaar_fight_pit"]["policy"], "aggressive")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_duel_arena_entry_is_reachable_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_duel_arena_integration")
        logic = sys.modules[f"{addon.__name__}.logic.duel_arena_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Coins": 999},
            "equipment": {},
            "combat_encounter": {},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 60,
            "constitution_level": 60,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 43,
            "summoning_level": 1,
            "smithing_level": 1,
        }
        initial.update(logic.default_duel_arena_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_duel_arena_command"]("claim_cap", {})
        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["inventory"]["Duellist's cap (tier 1)"],
            1,
        )
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        result = captured["on_duel_arena_command"](
            "enter",
            {"rule_ids": ["no_food", "no_prayer"]},
        )
        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "duel_arena")
        self.assertEqual(
            addon._state.player_data["duel_arena"]["rule_ids"],
            ("no_food", "no_prayer"),
        )
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 999)
        self.assertEqual(
            col.custom_undo_entries,
            ["AnkiScape direct action", "AnkiScape direct action"],
        )
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_a_speed_ten_card_runs_duel_exchanges_until_the_duel_ends(self):
        addon = _load_addon_as_package("ankiscape_duel_arena_multiplier")
        logic = sys.modules[f"{addon.__name__}.logic.duel_arena_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        player = storage.default_player_data(
            constants.ORE_DATA,
            constants.ITEM_DEFINITIONS,
        )
        player, ok, _info = logic.enter_duel_arena_pure(player, ())
        self.assertTrue(ok)
        addon._state.player_data = player
        addon._state.current_skill = "Utility / Activities"
        addon._state.exp_awarded = False
        addon._review_action_multiplier = lambda: 10
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon._state.player_data)

        addon.on_good_answer(before)

        self.assertEqual(addon._state.player_data["duel_arena_wins"], 1)
        self.assertEqual(addon._state.player_data["duel_arena"], {})
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")

    def test_clan_wars_red_portal_entry_is_reachable_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_clan_wars_integration")
        logic = sys.modules[f"{addon.__name__}.logic.clan_wars_logic"]
        data = sys.modules[f"{addon.__name__}.data.clan_wars_data"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = {
            "inventory": {"Lobster": 4},
            "equipment": {"weapon": "Mithril scimitar"},
            "carried_inventory": {"chicken": {"Lobster": 4}},
            "combat_encounter": {},
            "current_combat_target": "chicken",
            "current_utility": "make_soft_clay",
            "activity_session": {"active_id": ""},
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 60,
            "constitution_level": 60,
            "ranged_level": 40,
            "magic_level": 40,
            "prayer_level": 43,
            "summoning_level": 1,
            "smithing_level": 1,
            "combat_current_levels": {"attack": 99, "strength": 99},
        }
        initial.update(logic.default_clan_wars_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_clan_wars_command"](
            "set_policy",
            {"mode": data.CLAN_WARS_RED_MODE},
        )
        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["clan_wars_policy"]["mode"],
            data.CLAN_WARS_RED_MODE,
        )
        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

        result = captured["on_clan_wars_command"](
            "enter",
            {"mode": data.CLAN_WARS_RED_MODE},
        )
        self.assertTrue(result["ok"])
        self.assertTrue(result["boosts_clamped"])
        self.assertEqual(addon._state.player_data["current_utility"], "clan_wars")
        self.assertEqual(
            addon._state.player_data["clan_wars"]["mode"],
            data.CLAN_WARS_RED_MODE,
        )
        # The carried pack follows the player into the portal, which is what
        # the red portal then puts at risk.
        self.assertEqual(
            addon._state.player_data["carried_inventory"][
                data.CLAN_WARS_COMBAT_TARGET_ID
            ],
            {"Lobster": 4},
        )
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_a_speed_ten_clan_wars_card_stops_at_low_lp_without_food_and_keeps_the_match_active(self):
        addon = _load_addon_as_package("ankiscape_clan_wars_multiplier")
        logic = sys.modules[f"{addon.__name__}.logic.clan_wars_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        player = storage.default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        player, ok, _info = logic.enter_clan_wars_pure(player, "white_ffa")
        self.assertTrue(ok)
        addon._state.player_data = player
        addon._state.current_skill = "Utility / Activities"
        addon._state.exp_awarded = False
        addon._review_action_multiplier = lambda: 10
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _message: None
        addon._advance_world_events_after_review = lambda: None
        addon._save_player_data_if_anki_ready = lambda: None
        before = copy.deepcopy(addon._state.player_data)
        review_ctx = addon._runtime_action_context()
        addon._runtime_action_context = lambda: review_ctx
        addon.on_good_answer(before)
        self.assertEqual(review_ctx.card.stop_reason, "low_lp_no_food")
        self.assertEqual(addon._state.player_data["clan_wars_losses"], 0)
        self.assertEqual(addon._state.player_data["activity_session"]["active_id"], "clan_wars")
