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
    def test_miscellania_day_tick_and_review_undo_share_one_transaction(self):
        addon = _load_addon_as_package("ankiscape_miscellania_clock_integration")
        logic = sys.modules[f"{addon.__name__}.logic.managing_miscellania_logic"]
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        initial = {
            "inventory": {},
            "quests": {"throne_of_miscellania": {"completed": True}},
            "shop_market_clock": {"answered_cards": 239, "market_tick": 239},
        }
        initial.update(logic.default_managing_miscellania_state_pure(239))
        initial["managing_miscellania"]["coffer"] = 500_000
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        state = addon._state.player_data["managing_miscellania"]
        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 240)
        self.assertEqual(state["approval_basis_points"], 9_750)
        self.assertEqual(state["coffer"], 450_000)
        self.assertEqual(state["production_credit"], 975_000)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_wicked_hood_daily_refill_and_review_undo_share_one_transaction(self):
        addon = _load_addon_as_package("ankiscape_wicked_hood_clock_integration")
        hood_logic = sys.modules[f"{addon.__name__}.logic.wicked_hood_logic"]
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        initial = {
            "inventory": {},
            "shop_market_clock": {"answered_cards": 239, "market_tick": 239},
            "wicked_hood": hood_logic.default_wicked_hood_state_pure(0),
        }
        initial["wicked_hood"].update(
            {
                "essence_remaining": 7,
                "rune_withdrawals_remaining": 0,
                "teleports_remaining": 1,
            }
        )
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        hood = addon._state.player_data["wicked_hood"]
        self.assertEqual(addon._state.player_data["shop_market_clock"]["answered_cards"], 240)
        self.assertEqual(hood["allowance_day"], 1)
        self.assertEqual(hood["essence_remaining"], 100)
        self.assertEqual(hood["rune_withdrawals_remaining"], 1)
        self.assertEqual(hood["teleports_remaining"], 2)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_miscellania_direct_command_is_atomic_and_undoable(self):
        addon = _load_addon_as_package("ankiscape_miscellania_command_integration")
        logic = sys.modules[f"{addon.__name__}.logic.managing_miscellania_logic"]
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
            "inventory": {"Coins": 1_000_000},
            "quests": {"throne_of_miscellania": {"completed": True}},
            "shop_market_clock": {"answered_cards": 0},
            "smithing_level": 1,
        }
        initial.update(logic.default_managing_miscellania_state_pure())
        addon._state.player_data = copy.deepcopy(initial)

        addon._on_main_menu()
        result = captured["on_managing_miscellania_command"](
            "fund_days", {"days": 7}
        )

        self.assertTrue(result["ok"])
        self.assertEqual(addon._state.player_data["managing_miscellania"]["coffer"], 800_000)
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 200_000)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
