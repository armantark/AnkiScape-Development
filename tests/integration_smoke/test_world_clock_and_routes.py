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
    def test_wicked_hood_withdrawal_is_direct_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_wicked_hood_direct_integration")
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
        addon._state.current_skill = "Runecrafting"
        initial = storage.default_player_data(
            constants.ORE_DATA, constants.ITEM_DEFINITIONS
        )
        initial["claims"]["wicked_hood"] = {"claimed": True}
        initial["equipment"]["head"] = "Wicked hood"
        initial["current_runecrafting"] = "craft_air_runes"
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_wicked_hood_command"]("essence", {})

        self.assertTrue(result["ok"], result)
        self.assertEqual(addon._state.player_data["inventory"]["Rune essence"], 100)
        self.assertEqual(addon._state.player_data["wicked_hood"]["essence_remaining"], 0)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_court_case_review_and_world_clock_undo_together(self):
        addon = _load_addon_as_package("ankiscape_court_review_integration")
        logic = sys.modules[f"{addon.__name__}.logic.court_cases_logic"]
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        base = {
            "inventory": {},
            "quests": {"kings_ransom": {"completed": True}},
            "attack_level": 65,
            "attack_exp": 0.0,
            "defense_level": 65,
            "defense_exp": 0.0,
            "shop_market_clock": {"answered_cards": 41, "market_tick": 41},
            "activity_session": {"active_id": ""},
        }
        base.update(logic.default_court_cases_state_pure())
        entered, ok, _info = logic.enter_court_case_pure(base)
        self.assertTrue(ok)
        addon._state.player_data = copy.deepcopy(entered)
        initial = copy.deepcopy(entered)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 3, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 42)
        self.assertEqual(addon._state.player_data["court_cases"]["prep_index"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_combat_strip_bank_button_queues_the_engine_route_and_refreshes(self):
        addon = _load_addon_as_package("ankiscape_combat_strip_bank_run")
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon._state.current_skill = "Combat"
        addon._state.player_data = {"combat_encounter": {}}
        surfaces = []
        addon.update_review_bank_run_button = (
            lambda data, handler, callback, target_id=None, *, ammo_pickup_action=None: surfaces.append(
                {
                    "handler": handler,
                    "target_id": target_id,
                    "callback": callback,
                    "ammo_pickup_action": ammo_pickup_action,
                    "bank_run": copy.deepcopy(data.get("combat_bank_run")),
                }
            )
        )

        addon._update_review_bank_run_surface()
        committed = surfaces[-1]["callback"]()

        self.assertTrue(committed)
        self.assertEqual(surfaces[0]["handler"], "combat")
        self.assertEqual(surfaces[0]["target_id"], "chicken")
        self.assertIs(surfaces[0]["ammo_pickup_action"], addon.on_pickup_review_ammo)
        self.assertEqual(
            addon._state.player_data["combat_bank_run"],
            {"ticks_remaining": 100, "target_id": "chicken"},
        )
        self.assertEqual(surfaces[-1]["bank_run"], addon._state.player_data["combat_bank_run"])
        self.assertEqual(len(addon.mw.col.custom_undo_entries), 1)
        self.assertEqual(addon.mw.undo_updates, 1)

    def test_circus_review_and_world_clock_undo_together(self):
        addon = _load_addon_as_package("ankiscape_circus_review_integration")
        logic = sys.modules[f"{addon.__name__}.logic.circus_logic"]
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon.check_achievements = lambda *_args: None
        addon._state.player_data = {
            "circus": logic.default_circus_state_pure(),
            "inventory": {},
            "quests": {},
            "agility_level": 99,
            "agility_exp": 0.0,
            "shop_market_clock": {"answered_cards": 41, "market_tick": 41},
            "current_utility": "big_top_bonanza",
            "activity_session": {"active_id": ""},
            "completed_achievements": [],
        }
        initial = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 3, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 42)
        self.assertEqual(
            addon._state.player_data["circus"]["session"]["active_performance"],
            "agility",
        )
        self.assertEqual(
            addon._state.player_data["circus"]["session"]["trick_index"],
            1,
        )
        self.assertGreater(addon._state.player_data["agility_exp"], 0.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])
