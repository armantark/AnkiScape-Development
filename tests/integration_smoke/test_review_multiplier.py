from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _load_addon_as_package,
    copy,
    types,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_review_action_multiplier_runs_complete_live_cadence_steps(self):
        addon = _load_addon_as_package("ankiscape_review_multiplier_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 2}))
        addon.mw.exp_popup = types.SimpleNamespace(show_exp=lambda exp: calls["xp"].append(exp))

        addon._state.player_data = {
            "inventory": {},
            "woodcutting_level": 1,
            "woodcutting_exp": 0,
            "current_tree": "tree",
            "toolbelt": {"woodcutting": ["bronze_hatchet"]},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.current_skill = "Woodcutting"
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

            addon._state.current_skill = "Fletching"
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon._state.player_data["woodcutting_exp"], 25.0)
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(calls["xp"], [25.0, 5.0])

    def test_thieving_failure_is_one_attempt_under_multiplier_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_thieving_review_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon._state.player_data = {
            "inventory": {},
            "thieving_level": 1,
            "thieving_exp": 0.0,
            "current_thieving": "pickpocket_man",
            "thieving_attempt_count": 0,
            "thieving_success_count": 0,
            "thieving_failure_count": 0,
            "combat_lifepoints": 100,
            "completed_achievements": [],
        }
        initial_state = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Thieving"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        rolls = iter((0.999, 0.0, 0.0, 0.0, 0.0))
        addon.random.random = lambda: next(rolls)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["thieving_attempt_count"], 1)
        self.assertEqual(addon._state.player_data["thieving_failure_count"], 1)
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 90)
        self.assertNotIn("card_tick_debt", addon._state.player_data)  # stun paid in-card
        self.assertEqual(addon._state.player_data["thieving_exp"], 0.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, initial_state)
        self.assertEqual(addon._state.current_skill, "Thieving")
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_thieving_success_and_stall_cadence_spend_each_six_tick_step(self):
        addon = _load_addon_as_package("ankiscape_thieving_multiplier_cap_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon._state.current_skill = "Thieving"

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.player_data = {
                "inventory": {},
                "thieving_level": 50,
                "thieving_exp": 0.0,
                "current_thieving": "pickpocket_man",
                "thieving_attempt_count": 0,
                "thieving_success_count": 0,
                "thieving_failure_count": 0,
                    "combat_lifepoints": 100,
                "completed_achievements": [],
            }
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

            self.assertEqual(addon._state.player_data["thieving_attempt_count"], 3)
            self.assertEqual(addon._state.player_data["thieving_success_count"], 3)
            self.assertEqual(addon._state.player_data["inventory"]["Coins"], 9)
            self.assertEqual(addon._state.player_data["thieving_exp"], 24.0)

            addon._state.player_data = {
                "inventory": {},
                "thieving_level": 50,
                "thieving_exp": 0.0,
                "current_thieving": "stall_silver",
                "thieving_attempt_count": 0,
                "thieving_success_count": 0,
                "thieving_failure_count": 0,
                    "cadence_profiles": {},
                "combat_lifepoints": 100,
                "completed_achievements": [],
            }
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["thieving_attempt_count"], 1)
        self.assertEqual(addon._state.player_data["thieving_success_count"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Silver ore"], 1)
        self.assertEqual(addon._state.player_data["thieving_exp"], 54.0)
        self.assertEqual(  # the stall restocks over 50 ticks, so two steps wait
            addon._state.player_data["cadence_profiles"]["thieving:stall_silver"]["assigned_reviews"],
            3,
        )

    def test_wall_safe_failure_consumes_one_multiplied_review_and_undoes_cadence(self):
        addon = _load_addon_as_package("ankiscape_wall_safe_review_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 3}))
        addon._state.player_data = {
            "inventory": {},
            "thieving_level": 50,
            "thieving_exp": 0.0,
            "current_thieving": "wall_safe",
            "thieving_attempt_count": 0,
            "thieving_success_count": 0,
            "thieving_failure_count": 0,
            "cadence_profiles": {},
            "combat_lifepoints": 100,
            "completed_achievements": [],
        }
        initial_state = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Thieving"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        rolls = iter((85 / 255, 0.0, 0.0, 0.0, 0.0))
        addon.random.random = lambda: next(rolls)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["thieving_attempt_count"], 1)
        self.assertEqual(addon._state.player_data["thieving_failure_count"], 1)
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 80)
        self.assertNotIn("card_tick_debt", addon._state.player_data)  # stun paid in-card
        self.assertEqual(
            addon._state.player_data["cadence_profiles"]["thieving:wall_safe"]["assigned_reviews"],
            1,
        )

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, initial_state)
        self.assertEqual(addon._state.current_skill, "Thieving")

    def test_utility_multiplier_runs_wool_gathering_ticks(self):
        addon = _load_addon_as_package("ankiscape_wool_multiplier_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 2}))
        addon.mw.exp_popup = types.SimpleNamespace(show_text=lambda text: calls["gains"].append(text))
        addon._state.player_data = {
            "inventory": {},
            "crafting_exp": 0,
            "current_utility": "gather_wool",
            "completed_achievements": [],
        }

        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Wool"], 56)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["+56 Wool"])

    def test_a_gathering_row_quotes_what_one_card_gathers_at_the_game_speed(self):
        from ankiscape.core.constants import (
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
        )
        from ankiscape.core.target_metadata import utility_activity_rows

        addon = _load_addon_as_package("ankiscape_grain_speed_integration")
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 10}))
        shown = []
        addon.mw.exp_popup = types.SimpleNamespace(show_text=shown.append)
        addon._state.player_data = {"inventory": {}, "current_utility": "gather_grain", "completed_achievements": []}
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        rows = utility_activity_rows(
            {}, UTILITY_ACTIVITY_DATA, UTILITY_ITEM_IMAGES, BIRD_NEST_OPEN_TABLES, DEFAULT_UTILITY_ACTIVITY, speed=10
        )
        tooltip = next(row.tooltip for row in rows if row.target_id == "gather_grain")
        self.assertEqual(addon._state.player_data["inventory"]["Wheat"], 280)
        self.assertIn("+280 Wheat", shown)
        self.assertTrue(tooltip.startswith("Gathers up to 280 per successful card at 10x game speed. No skill XP.\n"), tooltip)

    def test_bankstanding_advances_only_the_normal_review_market_tick(self):
        addon = _load_addon_as_package("ankiscape_bankstanding_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save", calls["save"] + 1
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(
            _DummyCol({"ankiscape_review_action_multiplier": 10})
        )
        addon.mw.exp_popup = types.SimpleNamespace(
            show_text=lambda text: calls["gains"].append(text)
        )
        inventory = {"Coins": 1_000, "Logs": 4}
        addon._state.player_data = {
            "inventory": copy.deepcopy(inventory),
            "current_utility": "bankstanding",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["inventory"], inventory)
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["market_tick"],
            0,
        )
        self.assertEqual(
            addon._state.player_data["ge_market_state"]["last_processed_tick"],
            0,
        )
        # Bankstanding produces nothing by definition, so a review of it is
        # silent; the HUD already reads "idle at the Bank".
        self.assertEqual(calls["gains"], [])
