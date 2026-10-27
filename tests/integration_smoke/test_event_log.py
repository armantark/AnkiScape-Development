from tests.test_integration_smoke import _DummyCol, _DummyMW, _load_addon_as_package, sys, types
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_floating_xp_and_activity_results_share_the_event_log_seam(self):
        addon = _load_addon_as_package("ankiscape_event_log_emissions")
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": False}))
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Mining"
        addon._state.player_data = {
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        addon._show_exp(25)
        addon._show_activity_gain("+1 Iron ore")
        addon._show_activity_gain("Bank run — arrived and restocked")

        self.assertEqual(
            [row["kind"] for row in addon._state.player_data["review_event_log"]],
            ["xp", "activity", "activity"],
        )
        self.assertEqual(
            [row["text"] for row in addon._state.player_data["review_event_log"]],
            [
                "+25 XP · Mining",
                "+1 Iron ore",
                "Bank run — arrived and restocked",
            ],
        )

    def test_bankstanding_transition_logs_once_and_defers_the_reasoned_modal(self):
        addon = _load_addon_as_package("ankiscape_bankstanding_transition")
        addon.mw = _DummyMW(_DummyCol())
        addon.update_review_event_log_drawer = lambda _data: None
        addon.update_review_hud = lambda *_args: None
        popups = []
        gains = []
        rewards = []
        scheduled = []
        sys.modules["aqt.qt"].QTimer = types.SimpleNamespace(
            singleShot=lambda _delay, callback: scheduled.append(callback)
        )
        addon.ui.show_bankstanding_dialog = popups.append
        addon._show_activity_gain = gains.append
        addon._claim_stronghold_reward = lambda: rewards.append("reward")
        addon._state.current_skill = "Utilities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.player_data = {
            "current_utility": "stronghold_of_security",
            "review_event_log": [],
        }
        reason = "Stronghold of Security cleared — claim your reward!"

        runtime_ctx = addon._runtime_action_context()
        runtime_ctx.show_activity_gain(reason)
        runtime_ctx.deactivate_current_skill()
        self.assertFalse(addon._switch_to_bankstanding("A duplicate reason."))

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)
        self.assertEqual(popups, [])
        self.assertEqual(gains, [reason])
        self.assertIn(
            reason,
            addon._state.player_data["review_event_log"][0]["text"],
        )

        addon._prompt_stronghold_reward()
        addon._state.card_turned = False
        addon._state.answer_shown = False
        addon._show_pending_bankstanding_dialog()
        addon._show_pending_review_dialogs()

        self.assertEqual(popups, [])
        self.assertEqual(rewards, [])
        self.assertEqual(len(scheduled), 2)
        scheduled[0]()
        self.assertEqual(popups, [reason])
        self.assertEqual(rewards, [])
        scheduled[1]()
        self.assertEqual(rewards, ["reward"])

    def test_bankstanding_reason_backpatch_updates_the_live_sanitized_log(self):
        from ankiscape.core.review_event_log import sanitize_review_event_log_pure

        addon = _load_addon_as_package("ankiscape_bankstanding_reason_backpatch")
        addon.mw = _DummyMW(_DummyCol())
        addon.update_review_hud = lambda *_args: None
        addon.show_error_message = lambda *_args: None
        addon._state.current_skill = "Crafting"
        addon._state.player_data = {
            "current_utility": "gather_wool",
            "review_event_log": [],
        }
        runtime_ctx = addon._runtime_action_context()

        runtime_ctx.switch_to_bankstanding()
        detached_entry = addon._state.player_data["review_event_log"][-1]
        addon._state.player_data["review_event_log"] = sanitize_review_event_log_pure(
            addon._state.player_data["review_event_log"]
        )
        live_entry = addon._state.player_data["review_event_log"][-1]
        self.assertIsNot(live_entry, detached_entry)

        reason = "You need 1 Soft clay to craft an Unfired pot."
        runtime_ctx.show_error_message("Out of materials", reason)

        self.assertIn(reason, live_entry["text"])
        self.assertNotIn(reason, detached_entry["text"])

    def test_ge_status_navigation_focuses_or_opens_the_ge_tab(self):
        addon = _load_addon_as_package("ankiscape_ge_status_navigation")
        opened = []
        addon.ui._MAIN_MENU_CTX["open_grand_exchange"] = lambda: opened.append(
            "focused"
        )
        addon.ui.focus_main_menu_if_open = lambda: True
        addon._on_main_menu = lambda **_kwargs: self.fail(
            "an open menu must be reused"
        )

        addon._open_grand_exchange_sheet()
        self.assertEqual(opened, ["focused"])

        addon.ui.focus_main_menu_if_open = lambda: False
        addon._on_main_menu = lambda **kwargs: opened.append(kwargs)
        addon._open_grand_exchange_sheet()
        self.assertEqual(opened[-1], {"initial_global_tab": "Grand Exchange"})
