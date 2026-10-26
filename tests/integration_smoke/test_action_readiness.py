from tests.test_integration_smoke import _DummyCol, _DummyMW, _load_addon_as_package
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_utility_opens_bird_nests_without_skill_xp(self):
        addon = _load_addon_as_package("ankiscape_bird_nest_utility_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda _title, message: self.fail(message)

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.player_data = {
                "inventory": {"Bird's nest (seeds)": 1},
                "woodcutting_exp": 0,
                "current_utility": "open_bird_nest",
                "completed_achievements": [],
            }

            addon.on_utility_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Bird's nest (seeds)"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Bird's nest (empty)"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Acorn"], 1)
        self.assertEqual(addon._state.player_data["woodcutting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Opened 1 bird nest"])

    def test_utility_out_of_materials_switches_to_bankstanding_and_warns(self):
        # Material exhaustion warns once, then future cards keep the ordinary
        # market clock moving through the settled no-XP Bankstanding fallback.
        addon = _load_addon_as_package("ankiscape_utility_depleted")
        errors = []
        addon.check_achievements = lambda _d: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _t: self.fail("should not gain when out of materials")
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon._state.current_skill = "Utility / Activities"
        addon._state.player_data = {"inventory": {}, "current_utility": "make_soft_clay", "completed_achievements": []}

        addon.on_utility_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(errors, [])
        self.assertIn("Clay", addon._state.pending_bankstanding_notice["reason"])

    def test_crafting_missing_intermediate_names_material_and_uses_bankstanding(self):
        # "Pot" needs an "Unfired pot", not Soft clay directly. The error must name
        # the actual missing item (so a bank full of Soft clay doesn't look like a
        # bug) and switch future reviews to Bankstanding.
        addon = _load_addon_as_package("ankiscape_craft_depleted")
        errors = []
        addon.check_achievements = lambda _d: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon._state.current_skill = "Crafting"
        addon._state.player_data = {
            "inventory": {"Soft clay": 231},
            "crafting_level": 50,
            "current_craft": "fire_empty_pot",
            "completed_achievements": [],
        }

        addon.on_crafting_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(errors, [])
        self.assertIn("Pot (unfired)", addon._state.pending_bankstanding_notice["reason"])

    def test_changing_target_refreshes_review_hud(self):
        # Switching the active Utility activity (or any target) must push the new
        # state to the in-review HUD immediately, not on the next card.
        addon = _load_addon_as_package("ankiscape_target_hud_refresh")
        calls = {"hud": []}
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda data, skill: calls["hud"].append(skill)
        addon._state.current_skill = "Utility / Activities"
        addon._state.player_data = {"inventory": {}, "current_utility": "gather_flax"}
        addon.mw = _DummyMW(_DummyCol())

        addon._set_value("current_utility", "make_soft_clay")

        self.assertEqual(addon._state.player_data["current_utility"], "make_soft_clay")
        self.assertEqual(calls["hud"], ["Utility / Activities"])

    def test_review_handler_lookup_uses_action_registry_for_skills_and_utility(self):
        addon = _load_addon_as_package("ankiscape_action_dispatch_lookup")

        self.assertIs(addon._registered_answer_handler("Fletching"), addon.runtime_actions.handle_fletching_answer)
        self.assertIs(addon._registered_answer_handler("Firemaking"), addon.runtime_actions.handle_firemaking_answer)
        self.assertIs(addon._registered_answer_handler("Fishing"), addon.runtime_actions.handle_fishing_answer)
        self.assertIs(addon._registered_answer_handler("Utility / Activities"), addon.runtime_actions.handle_utility_answer)
        self.assertIs(addon._registered_answer_handler("Utility"), addon.runtime_actions.handle_utility_answer)
        self.assertIs(addon._registered_answer_handler("Utilities"), addon.runtime_actions.handle_utility_answer)
        self.assertIs(addon._registered_answer_handler("Activities"), addon.runtime_actions.handle_utility_answer)
        self.assertIs(addon._registered_answer_handler("Thieving"), addon.runtime_actions.handle_thieving_answer)

    def test_legacy_combined_no_xp_skill_normalizes_from_its_selected_target(self):
        addon = _load_addon_as_package("ankiscape_legacy_no_xp_surface")
        addon._state.player_data = {"current_utility": "make_soft_clay"}
        self.assertEqual(
            addon._normalize_legacy_utility_skill("Utility / Activities"),
            "Utilities",
        )
        addon._state.player_data["current_utility"] = "livid_farm"
        self.assertEqual(
            addon._normalize_legacy_utility_skill("Utility / Activities"),
            "Activities",
        )
        addon._state.player_data["current_utility"] = "mage_arena_attune:guthix"
        self.assertEqual(
            addon._normalize_legacy_utility_skill("Utility"),
            "Activities",
        )

    def test_can_start_current_action_uses_handler_keyed_readiness_checks(self):
        addon = _load_addon_as_package("ankiscape_action_dispatch_readiness")

        addon._state.current_skill = "Fletching"
        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "current_fletch": "arrow_shafts",
        }
        self.assertTrue(addon._can_start_current_action())

        addon._state.player_data["inventory"] = {}
        self.assertFalse(addon._can_start_current_action())

        addon._state.current_skill = "Firemaking"
        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "firemaking_level": 1,
            "current_firemaking": "logs",
        }
        self.assertTrue(addon._can_start_current_action())

        addon._state.player_data["inventory"] = {}
        self.assertFalse(addon._can_start_current_action())

        addon._state.current_skill = "Fishing"
        addon._state.player_data = {
            "inventory": {"Fishing bait": 1},
            "fishing_level": 5,
            "current_fishing": "catch_sardine_herring",
        }
        self.assertTrue(addon._can_start_current_action())

        addon._state.player_data["inventory"] = {}
        self.assertFalse(addon._can_start_current_action())

        addon._state.current_skill = "Utility"
        addon._state.player_data = {"inventory": {"Clay": 1}, "current_utility": "make_soft_clay"}
        self.assertTrue(addon._can_start_current_action())

        addon._state.player_data = {"inventory": {}, "current_utility": "make_soft_clay"}
        self.assertFalse(addon._can_start_current_action())
