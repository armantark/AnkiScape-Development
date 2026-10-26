from tests.test_integration_smoke import _FakeReviewer, _load_addon_as_package, types
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_super_prayer_mixing_uses_wyvern_bonemeal_and_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_super_prayer_mixing_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        ingredients = {
            "Prayer potion (3)": 1,
            "Wyvern bonemeal": 1,
            "Bonemeal": 5,
        }
        addon._state.player_data = {
            "inventory": ingredients.copy(),
            "herblore_level": 94,
            "herblore_exp": 0,
            "current_herblore": "finished_super_prayer",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Herblore"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Prayer potion (3)"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Wyvern bonemeal"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Bonemeal"], 5)
        self.assertEqual(addon._state.player_data["inventory"]["Super prayer (3)"], 1)
        self.assertEqual(addon._state.player_data["herblore_exp"], 270.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], ingredients)
        self.assertEqual(addon._state.player_data["herblore_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [270.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_overload_mixing_review_reward_and_vials_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_overload_mixing_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        ingredients = {
            "Extreme attack (3)": 1,
            "Extreme strength (3)": 1,
            "Extreme defence (3)": 1,
            "Extreme magic (3)": 1,
            "Extreme ranging (3)": 1,
            "Clean torstol": 1,
        }
        addon._state.player_data = {
            "inventory": ingredients.copy(),
            "herblore_level": 96,
            "herblore_exp": 0,
            "current_herblore": "finished_overload",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Herblore"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Overload (3)"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Vial"], 4)
        self.assertEqual(addon._state.player_data["herblore_exp"], 1000.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], ingredients)
        self.assertEqual(addon._state.player_data["herblore_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [1000.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_shrink_me_quick_mixing_rolls_back_atomically_on_review_undo(self):
        addon = _load_addon_as_package("ankiscape_shrink_me_quick_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        ingredients = {
            "Tarromin potion (unf)": 1,
            "Shrunk ogleroot": 1,
        }
        addon._state.player_data = {
            "inventory": ingredients.copy(),
            "herblore_level": 52,
            "herblore_exp": 0,
            "current_herblore": "finished_shrink_me_quick",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Herblore"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Tarromin potion (unf)"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Shrunk ogleroot"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Shrink-me-quick"], 1)
        self.assertEqual(addon._state.player_data["herblore_exp"], 6.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], ingredients)
        self.assertEqual(addon._state.player_data["herblore_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [6.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_cannonball_review_reward_and_mould_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_cannonball_smithing_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Steel bar": 1, "Ammo mould": 1},
            "smithing_level": 35,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "forge_cannonballs",
            "quests": {"dwarf_cannon": {"completed": True}},
            "completed_achievements": [],
        }
        addon._state.current_skill = "Smithing"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Steel bar": 0, "Ammo mould": 1, "Cannonball": 4})
        self.assertEqual(addon._state.player_data["smithing_exp"], 25.6)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Steel bar": 1, "Ammo mould": 1})
        self.assertEqual(addon._state.player_data["smithing_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [25.6])

    def test_utility_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_utility_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Anchovies": 2},
            "crafting_exp": 0,
            "current_utility": "grind_anchovies",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Anchovies": 0, "Anchovy paste": 2})
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Anchovies": 2})
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)
