from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _load_addon_as_package,
    types,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_material_exhaustion_falls_back_once_then_bankstands(self):
        addon = _load_addon_as_package(
            "ankiscape_material_fallback_bankstanding_integration"
        )
        calls = {"errors": [], "gains": []}
        modal_order = []
        addon.ui.show_bankstanding_dialog = lambda reason: modal_order.append(
            ("modal", reason)
        )
        finish_feedback = addon._finish_review_feedback_context

        def _finish_feedback(*args):
            modal_order.append(("feedback", "flushed"))
            finish_feedback(*args)

        addon._finish_review_feedback_context = _finish_feedback
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda title, message: calls["errors"].append(
            (title, message)
        )
        addon.mw = _DummyMW(
            _DummyCol({"ankiscape_review_action_multiplier": 1})
        )
        addon.mw.exp_popup = types.SimpleNamespace(
            show_text=lambda text: calls["gains"].append(text)
        )
        addon._state.player_data = {
            "inventory": {"Soft clay": 20},
            "crafting_level": 50,
            "current_craft": "fire_empty_pot",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Crafting"
        addon._state.pending_review_dialogs.append(
            lambda: modal_order.append(("queued", "prompt"))
        )

        for review in range(2):
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease, review=review: modal_order.append(
                    ("answer", review)
                )
                or "answered",
            )

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["gains"], [])
        self.assertEqual(
            [kind for kind, _value in modal_order],
            ["feedback", "answer", "modal", "queued", "feedback", "answer"],
        )
        modal_reasons = [value for kind, value in modal_order if kind == "modal"]
        self.assertEqual(len(modal_reasons), 1)
        self.assertIn("Pot (unfired)", modal_reasons[0])
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["market_tick"],
            0,
        )
        self.assertEqual(
            addon._state.player_data["ge_market_state"]["last_processed_tick"],
            0,
        )

    def test_one_shot_utility_purchase_runs_once_and_switches_off(self):
        # No shipped activity uses deactivate_after_run since the
        # buy_hunter_supplies bridge was retired (its gear is live NPC shop
        # stock), but the runtime one-shot path stays supported; exercise it
        # with an injected activity spec.
        addon = _load_addon_as_package("ankiscape_one_shot_purchase_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 10}))
        addon.mw.exp_popup = types.SimpleNamespace(show_text=lambda text: calls["gains"].append(text))
        addon.UTILITY_ACTIVITY_DATA["one_shot_bundle"] = {
            "display_name": "Buy one-shot bundle",
            "requirements": {"Coins": 500},
            "outputs": {"Bird snare": 1, "Impling jar": 10},
            "batch_size": 1,
            "deactivate_after_run": True,
            "group": "shopping",
            "source": "test fixture",
        }
        addon._state.player_data = {
            "inventory": {"Coins": 500},
            "current_utility": "one_shot_bundle",
            "completed_achievements": [],
        }

        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon.mw.col.get_config("ankiscape_current_skill"), "Utilities")
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Bird snare"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Impling jar"], 10)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Bought one-shot bundle"])

    def test_bad_review_action_multiplier_config_plays_at_speed_ten(self):
        addon = _load_addon_as_package("ankiscape_bad_review_multiplier_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": "not-a-number"}))
        addon._state.player_data = {
            "inventory": {"Logs": 20},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 50.0)

    def test_processing_multiplier_stops_when_materials_are_depleted(self):
        addon = _load_addon_as_package("ankiscape_review_multiplier_depletion")

        calls = {"xp": [], "errors": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: calls["errors"].append(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon.mw.exp_popup = types.SimpleNamespace(show_exp=lambda exp: calls["xp"].append(exp))
        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(calls["xp"], [5.0])
        self.assertEqual(calls["errors"], [])

    def test_firemaking_multiplier_stops_when_logs_are_depleted(self):
        addon = _load_addon_as_package("ankiscape_firemaking_multiplier_depletion")

        calls = {"xp": [], "errors": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: calls["errors"].append(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon.mw.exp_popup = types.SimpleNamespace(show_exp=lambda exp: calls["xp"].append(exp))
        addon._state.player_data = {
            "inventory": {"Logs": 2},
            "firemaking_level": 1,
            "firemaking_exp": 0,
            "current_firemaking": "logs",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Firemaking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Ashes"], 2)
        self.assertAlmostEqual(addon._state.player_data["firemaking_exp"], 80.0)
        self.assertEqual(calls["xp"], [80.0])
        self.assertEqual(calls["errors"], [])

    def test_fishing_multiplier_stops_when_bait_is_depleted(self):
        addon = _load_addon_as_package("ankiscape_fishing_multiplier_depletion")

        calls = {"xp": [], "errors": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: calls["errors"].append(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon.mw.exp_popup = types.SimpleNamespace(show_exp=lambda exp: calls["xp"].append(exp))
        addon._state.player_data = {
            "inventory": {"Fishing bait": 1},
            "fishing_level": 5,
            "fishing_exp": 0,
            "strength_level": 1,
            "agility_level": 1,
            "current_fishing": "catch_sardine_herring",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fishing"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Fishing bait"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Raw sardine"], 1)
        self.assertAlmostEqual(addon._state.player_data["fishing_exp"], 20.0)
        self.assertEqual(calls["xp"], [20.0])
        self.assertEqual(calls["errors"], [])
