from tests.test_integration_smoke import _DummyCol, _DummyMW, _load_addon_as_package, types
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_attack_and_constitution_xp_break_down_in_popup_and_event_log(self):
        addon = _load_addon_as_package("ankiscape_event_log_skill_breakdown")
        popup_text = []
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": True}))
        addon.mw.exp_popup = types.SimpleNamespace(
            show_exp=lambda amount: popup_text.append(amount.display_text)
        )
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "attack_exp": 0.0,
            "constitution_exp": 0.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        addon._begin_review_feedback_context()
        attack = addon._award_skill_exp("attack_exp", 40)
        addon._show_exp(attack)
        constitution = addon._award_skill_exp("constitution_exp", 13.3)
        addon._show_exp(constitution)
        addon._finish_review_feedback_context()

        expected = "Attack +40 XP · Constitution +13 XP"
        self.assertEqual(popup_text, [expected])
        self.assertEqual(addon._state.player_data["review_event_log"][-1]["text"], expected)

    def test_fractional_constitution_xp_is_not_displayed_as_zero(self):
        addon = _load_addon_as_package("ankiscape_fractional_constitution_xp")

        amount = addon._NamedExperience(
            1.599,
            ("Attack", "Constitution"),
            (("Attack", 1.2), ("Constitution", 0.399)),
        )

        self.assertEqual(
            amount.display_text,
            "Attack +1 XP · Constitution +0.4 XP",
        )

    def test_xp_event_is_written_before_its_level_up_event(self):
        addon = _load_addon_as_package("ankiscape_xp_before_level_up")
        addon.mw = _DummyMW(
            _DummyCol(
                {
                    "ankiscape_floating_xp_enabled": False,
                    "ankiscape_popups_enabled": False,
                }
            )
        )
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Attack"
        addon._state.player_data = {
            "attack_level": 1,
            "attack_exp": 82.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }
        addon._core_level_up_check = lambda skill, data: (
            data.__setitem__("attack_level", 2),
            addon._record_review_event(
                "achievement",
                f"{skill} advanced to level 2",
                persist=False,
            ),
        )

        addon._begin_review_feedback_context()
        gained = addon._award_skill_exp("attack_exp", 1.0)
        addon.level_up_check("Attack", addon._state.player_data)
        addon._show_exp(gained)
        addon._finish_review_feedback_context()

        self.assertEqual(addon._state.player_data["attack_level"], 2)
        self.assertEqual(
            [row["text"] for row in addon._state.player_data["review_event_log"]],
            ["+1 XP · Attack", "Attack advanced to level 2"],
        )

    def test_xp_review_keeps_every_activity_event_without_replacing_the_xp_popup(self):
        addon = _load_addon_as_package("ankiscape_event_log_mixed_feedback")
        popup_calls = []
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": True}))
        addon.mw.exp_popup = types.SimpleNamespace(
            show_exp=lambda amount: popup_calls.append(("exp", amount)),
            show_text=lambda text: popup_calls.append(("text", text)),
        )
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "attack_exp": 0.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        addon._begin_review_feedback_context()
        gained = addon._award_skill_exp("attack_exp", 47)
        addon._show_exp(gained)
        addon._show_activity_gain("Defeated Goblin")
        addon._show_activity_gain("Combat switched off to stop you dying")
        addon._finish_review_feedback_context()

        self.assertEqual(
            [row["text"] for row in addon._state.player_data["review_event_log"]],
            [
                "+47 XP · Attack",
                "Defeated Goblin",
                "Combat switched off to stop you dying",
            ],
        )
        self.assertEqual(popup_calls, [("exp", 47.0)])

    def test_review_combat_level_boundary_collapses_multi_skill_gain_to_one_check(self):
        addon = _load_addon_as_package("ankiscape_combat_level_boundary")
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "constitution_level": 10,
            "prayer_level": 1,
            "ranged_level": 1,
            "magic_level": 1,
            "summoning_level": 1,
            "review_event_log": [],
        }
        checks = []
        addon._core_combat_level_up_check = lambda old, data: checks.append(
            (old, addon.player_combat_level_pure(data))
        )

        addon._begin_review_feedback_context()
        addon._state.player_data["attack_level"] = 10
        addon._state.player_data["strength_level"] = 10
        addon._finish_review_feedback_context()

        self.assertEqual(len(checks), 1)
        self.assertLess(checks[0][0], checks[0][1])

    def test_direct_xp_event_uses_the_awarded_skill_not_the_selected_skill(self):
        addon = _load_addon_as_package("ankiscape_direct_event_skill_name")
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": False}))
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Mining"
        addon._state.player_data = {
            "hunter_exp": 0.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        gained = addon._award_skill_exp("hunter_exp", 12)
        addon._show_exp(gained)

        self.assertEqual(
            addon._state.player_data["review_event_log"][-1]["text"],
            "+12 XP · Hunter",
        )

    def test_silent_award_cannot_name_a_later_unrelated_xp_event(self):
        addon = _load_addon_as_package("ankiscape_event_log_no_stale_skill")
        addon.mw = _DummyMW(_DummyCol({"ankiscape_floating_xp_enabled": False}))
        addon.storage_save_player_data = lambda _data, _skill: None
        addon.update_review_event_log_drawer = lambda _data: None
        addon._state.current_skill = "Activities"
        addon._state.player_data = {
            "summoning_exp": 0.0,
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "review_event_log": [],
        }

        addon._award_skill_exp("summoning_exp", 25.0)
        addon._show_exp(addon._NamedExperience(80.0, ("Hunter",)))

        self.assertEqual(
            addon._state.player_data["review_event_log"][-1]["text"],
            "+80 XP · Hunter",
        )
