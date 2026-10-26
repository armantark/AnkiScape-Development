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
    def test_phoenix_lair_loaded_addon_chain_rewards_daily_charge_and_review_undo(self):
        addon = _load_addon_as_package("ankiscape_phoenix_lair_e2e")
        logic = sys.modules[f"{addon.__name__}.logic.phoenix_lair_logic"]
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
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
        initial["quests"]["in_pyre_need"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        initial.update(
            {
                "slayer_level": 99,
                "summoning_level": 99,
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
                "magic_level": 99,
                "ranged_level": 99,
                "combat_lifepoints": 990,
            }
        )
        initial["inventory"].update(
            {"Knife": 1, "Secateurs": 1, "Tinderbox": 1}
        )
        initial["carried_advanced_targets"]["phoenix_lair"] = True
        initial["carried_layout"]["phoenix_lair"] = {
            "Knife": 1,
            "Secateurs": 1,
            "Tinderbox": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)

        def _kill_current_encounter(data, *_args, **_kwargs):
            updated = copy.deepcopy(data)
            updated["combat_encounter"] = {}
            return updated, True, {
                "reason": "combat_burst",
                "killed": True,
                "died": False,
                "fled": False,
                "enemy_lifepoints": 0,
                "xp_rewards": {},
                "drops": {},
            }

        logic.apply_combat_burst_pure = _kill_current_encounter

        addon._on_main_menu()
        entered = captured["on_phoenix_lair_command"]("enter", {})
        self.assertTrue(entered["ok"], entered)
        self.assertEqual(addon._state.player_data["phoenix_lair"]["phase"], "guardians")
        self.assertEqual(
            addon._state.player_data["carried_inventory"]["phoenix_lair"],
            {"Knife": 1, "Secateurs": 1, "Tinderbox": 1},
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        addon._on_main_menu()
        self.assertTrue(captured["carried_pack_target_active"])
        self.assertEqual(captured["active_carried_target_id"], "phoenix_lair")

        def _answer_review():
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )

        _answer_review()
        self.assertEqual(addon._state.player_data["phoenix_lair"]["phase"], "prepare")
        self.assertEqual(addon._state.player_data["inventory"]["Ashes"], 5)

        _answer_review()
        self.assertEqual(addon._state.player_data["phoenix_lair"]["phase"], "phoenix")
        before_completion = copy.deepcopy(addon._state.player_data)

        _answer_review()
        self.assertFalse(addon._state.player_data["phoenix_lair"]["active"])
        self.assertEqual(addon._state.player_data["inventory"]["Phoenix quill"], 5)
        self.assertEqual(addon._state.player_data["phoenix_lair"]["last_completed_world_day"], 0)
        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 3)
        blocked = captured["on_phoenix_lair_command"]("enter", {})
        self.assertFalse(blocked["ok"])
        self.assertIn("world day", blocked["message"])

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, before_completion)
        self.assertEqual(addon._state.player_data["phoenix_lair"]["phase"], "phoenix")
        self.assertEqual(addon._state.player_data["phoenix_lair"]["last_completed_world_day"], -1)
        self.assertEqual(addon._state.player_data["inventory"].get("Phoenix quill", 0), 0)

    def test_barbarian_assault_entry_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_barbarian_assault_integration")
        logic = sys.modules[f"{addon.__name__}.logic.barbarian_assault_logic"]
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
        initial.update(logic.default_barbarian_assault_state_pure())
        initial["barbarian_assault_tutorial_complete"] = True
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_barbarian_assault_command"](
            "enter",
            {"automation_mode": "advanced", "role": "defender"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["current_utility"], "barbarian_assault")
        self.assertEqual(addon._state.player_data["barbarian_assault"]["role"], "defender")
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_dagannoth_kings_entry_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_dagannoth_kings_integration")
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
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
        initial = storage.default_player_data(
            constants.ORE_DATA, constants.ITEM_DEFINITIONS
        )
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_dagannoth_kings_command"]("enter", {})

        self.assertTrue(result["ok"], result)
        self.assertTrue(addon._state.player_data["dagannoth_kings"]["active"])
        self.assertEqual(
            addon._state.player_data["activity_session"],
            {"active_id": "dagannoth_kings"},
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_stronghold_chest_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_stronghold_safety_integration")
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
            "combat_grave": {},
            "death_office": {},
            "smithing_level": 1,
            "stronghold_player_safety": {
                "version": 2,
                "stage": 3,
                "crevice_unlocked": True,
                "chest_claimed": False,
                "safety_first_emote_unlocked": False,
                "last_result": "Reached the reward passage.",
            },
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_stronghold_player_safety_command"](
            "claim_chest", {}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 10_000)
        self.assertEqual(addon._state.player_data["inventory"]["Safety gloves"], 1)
        for claim_id in result["claim_ids"]:
            self.assertEqual(
                addon._state.player_data["claims"][claim_id],
                {"claimed": False, "delivered": True},
            )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_varrock_museum_kit_is_a_direct_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_varrock_museum_integration")
        logic = sys.modules[f"{addon.__name__}.logic.varrock_museum_logic"]
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
            "quests": {},
            "smithing_level": 1,
            "varrock_museum": logic.default_varrock_museum_state_pure(),
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_varrock_museum_command"]("take_cleaning_kit", {})

        self.assertTrue(result["ok"])
        self.assertEqual(
            set(addon._state.player_data["inventory"]),
            {"Trowel", "Rock pick", "Specimen brush", "Leather gloves", "Leather boots"},
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_phoenix_lair_entry_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_phoenix_entry_integration")
        storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Activities"
        initial = storage.default_player_data(
            constants.ORE_DATA, constants.ITEM_DEFINITIONS
        )
        initial["quests"]["in_pyre_need"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        initial.update(
            {
                "slayer_level": 99,
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
            }
        )
        initial["inventory"].update(
            {"Knife": 1, "Secateurs": 1, "Tinderbox": 1}
        )
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_phoenix_lair_command"]("enter", {})

        self.assertTrue(result["ok"], result)
        self.assertTrue(addon._state.player_data["phoenix_lair"]["active"])
        self.assertEqual(
            addon._state.player_data["activity_session"], {"active_id": "phoenix_lair"}
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
