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
    def test_sorceress_garden_trip_and_cross_skill_reward_roll_back_together(self):
        addon = _load_addon_as_package("ankiscape_garden_undo_integration")
        garden_logic = sys.modules[
            "ankiscape_garden_undo_integration.logic.sorceress_garden_logic"
        ]

        calls = {"save": 0}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save", calls["save"] + 1
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _text: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        garden_state = garden_logic.default_sorceress_garden_state_pure()
        garden_state["introduced"] = True
        addon._state.player_data = {
            "inventory": {},
            "current_utility": "sorceress_garden",
            "farming_level": 1,
            "farming_exp": 0.0,
            "thieving_level": 1,
            "thieving_exp": 0.0,
            "quests": {
                "diamond_in_the_rough": {
                    "completed": True,
                }
            },
            "sorceress_garden": garden_state,
            "completed_achievements": [],
        }
        initial = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["inventory"]["Winter sq'irk"], 1)
        self.assertEqual(addon._state.player_data["farming_exp"], 30.0)
        self.assertEqual(
            addon._state.player_data["sorceress_garden"]["successful_trips"],
            1,
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(
                    study_queues=True,
                    card=True,
                ),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_penguin_spy_and_points_roll_back_as_one_review(self):
        addon = _load_addon_as_package("ankiscape_penguin_undo_integration")
        penguin_logic = sys.modules[
            "ankiscape_penguin_undo_integration.logic.penguin_hide_and_seek_logic"
        ]

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save", calls["save"] + 1
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        state = penguin_logic.default_penguin_state_pure()
        player = {
            "inventory": {},
            "equipment": {},
            "quests": {},
            "shop_market_clock": {"answered_cards": 0},
            "current_utility": "penguin_hide_and_seek",
            "penguin_hide_and_seek": state,
            "completed_achievements": [],
        }
        spawn_id = penguin_logic.penguin_roster_pure(player)[0]["id"]
        player, ok, _ = penguin_logic.apply_penguin_command_pure(
            player,
            "select_spy",
            {"spawn_id": spawn_id},
        )
        self.assertTrue(ok)
        addon._state.player_data = player
        initial = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["penguin_hide_and_seek"]["points"], 1)
        self.assertIn(
            spawn_id,
            addon._state.player_data["penguin_hide_and_seek"]["spotted_ids"],
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_livid_farm_cycle_and_cross_skill_xp_roll_back_as_one_review(self):
        addon = _load_addon_as_package("ankiscape_livid_farm_undo_integration")

        calls = {"save": 0}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save",
            calls["save"] + 1,
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {
                "Astral rune": 1_000,
                "Nature rune": 1_000,
                "Law rune": 1_000,
                "Earth rune": 1_000,
                "Water rune": 1_000,
            },
            "equipment": {},
            "quests": {"lunar_diplomacy": {"completed": True}},
            "magic_level": 99,
            "agility_level": 60,
            "crafting_level": 60,
            "farming_level": 60,
            "construction_level": 50,
            "magic_exp": 0.0,
            "agility_exp": 0.0,
            "crafting_exp": 0.0,
            "farming_exp": 0.0,
            "construction_exp": 0.0,
            "current_utility": "livid_farm",
            "completed_achievements": [],
        }
        before = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["livid_farm"]["cycles_completed"], 1)
        self.assertEqual(addon._state.player_data["livid_farm"]["produce_points"], 1_580)
        self.assertAlmostEqual(addon._state.player_data["magic_exp"], 3_737.0)
        self.assertAlmostEqual(addon._state.player_data["agility_exp"], 509.1)
        self.assertAlmostEqual(addon._state.player_data["crafting_exp"], 1_080.0)
        self.assertAlmostEqual(addon._state.player_data["farming_exp"], 2_754.0)
        self.assertAlmostEqual(addon._state.player_data["construction_exp"], 546.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_livid_more_planks_world_tick_advances_on_again_and_undo_restores_it(self):
        addon = _load_addon_as_package(
            "ankiscape_livid_wish_world_tick_integration"
        )
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        initial = {
            "inventory": {},
            "livid_farm": {
                "borrowed_power_claimed": True,
                "more_planks_ticks_remaining": 6,  # one speed-1 card
            },
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            1,
            lambda _self, _ease: "answered",
        )

        state = addon._state.player_data["livid_farm"]
        self.assertEqual(state["more_planks_ticks_remaining"], 0)
        self.assertTrue(state["more_planks_active_this_review"])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_livid_wish_purchase_uses_direct_action_undo(self):
        addon = _load_addon_as_package(
            "ankiscape_livid_wish_direct_action_integration"
        )
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Utility / Activities"
        initial = {
            "inventory": {},
            "livid_farm": {
                "borrowed_power_claimed": True,
                "produce_points": 18_000,
            },
        }
        addon._state.player_data = copy.deepcopy(initial)

        result = addon.on_livid_farm_wish("gimme_herbs")

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Grimy kwuarm"], 3)
        self.assertEqual(addon._state.player_data["livid_farm"]["produce_points"], 0)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_livid_protection_wish_flows_into_the_farming_action_surface(self):
        addon = _load_addon_as_package(
            "ankiscape_livid_protection_farming_integration"
        )
        farming_data = sys.modules[f"{addon.__name__}.data.farming_data"]
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Utility / Activities"
        state = {
            "inventory": {
                "Rake": 1,
                "Spade": 1,
                "Oak sapling": 1,
            },
            "farming_level": 99,
            "farming_exp": 0.0,
            "smithing_level": 1,
            "livid_farm": {
                "borrowed_power_claimed": True,
                "produce_points": 37_000,
            },
        }
        state.update(farming_logic.default_farming_state_pure())
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {
                "kind": "plant",
                "patch_id": "lumbridge_tree",
                "crop_id": "oak",
            },
        )
        self.assertTrue(ok)
        addon._state.player_data = state

        purchased = addon.on_livid_farm_wish("protect_patch")
        self.assertTrue(purchased["ok"])
        self.assertEqual(
            addon._state.player_data["inventory"][
                farming_data.LIVID_FARM_PROTECTION_SCROLL
            ],
            1,
        )

        addon._on_main_menu(initial_skill="Farming")
        activated = captured["on_farming_action"](
            "activate_livid_protection",
            {"patch_id": "lumbridge_tree"},
        )

        self.assertTrue(activated["ok"])
        self.assertTrue(
            addon._state.player_data["farm_patches"]["lumbridge_tree"][
                "livid_protected"
            ]
        )
        self.assertEqual(
            addon._state.player_data["farm_livid_protection_uses_remaining"],
            9,
        )
        self.assertNotIn(
            farming_data.LIVID_FARM_PROTECTION_SCROLL,
            addon._state.player_data["inventory"],
        )

    def test_arcane_capacitor_charge_uses_direct_action_undo(self):
        from ankiscape.data.livid_farm_data import (
            ARCANE_CAPACITOR_CHARGED,
            ARCANE_CAPACITOR_UNCHARGED,
        )

        addon = _load_addon_as_package(
            "ankiscape_arcane_capacitor_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.current_skill = "Utility / Activities"
        initial = {
            "inventory": {
                ARCANE_CAPACITOR_UNCHARGED: 1,
                "Air rune": 1_000,
                "Earth rune": 1_000,
                "Law rune": 1_000,
            },
            "equipment": {},
            "magic_level": 99,
            "quests": {"lunar_diplomacy": {"completed": True}},
            "livid_farm": {"borrowed_power_claimed": True},
            "smithing_level": 1,
        }
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_livid_farm_command"](
            "charge_capacitor",
            {"spell_id": "teleport_to_house"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            addon._state.player_data["inventory"][ARCANE_CAPACITOR_CHARGED],
            1,
        )
        self.assertEqual(
            addon._state.player_data["livid_farm"]["arcane_capacitor_charges"],
            1_000,
        )
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
