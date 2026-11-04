from tests.test_integration_smoke import _FakeReviewer, _load_addon_as_package, types
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_leather_thread_consumption_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_leather_thread_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Leather": 1, "Thread": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "leather_leather_gloves",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Crafting"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        self.addCleanup(setattr, addon.random, "random", original_random)

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Leather": 0, "Thread": 0, "Leather gloves": 1})
        self.assertAlmostEqual(addon._state.player_data["crafting_exp"], 13.8)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Leather": 1, "Thread": 1})
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_glassblowing_pipe_requirement_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_glassblowing_pipe_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Molten glass": 1, "Glassblowing pipe": 1},
            "crafting_level": 1,
            "crafting_exp": 0,
            "current_craft": "glass_beer_glass",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Crafting"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Molten glass": 0, "Glassblowing pipe": 1, "Beer glass": 1})
        self.assertAlmostEqual(addon._state.player_data["crafting_exp"], 17.5)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Molten glass": 1, "Glassblowing pipe": 1})
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_light_source_review_action_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_light_source_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Sapphire lantern (unlit)": 1},
            "firemaking_level": 49,
            "current_utility": "light_sapphire_lantern",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Sapphire lantern (unlit)": 0, "Sapphire lantern (lit)": 1})
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Sapphire lantern (unlit)": 1})
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_lamp_oil_preparation_review_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_lamp_oil_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Bullseye lantern (empty)": 1, "Swamp tar": 1},
            "current_utility": "fill_bullseye_lantern",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Bullseye lantern (empty)": 0, "Swamp tar": 0, "Bullseye lantern (unlit)": 1},
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Bullseye lantern (empty)": 1, "Swamp tar": 1},
        )
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_tanning_review_batches_28_hides_and_rolls_back_on_undo(self):
        # Review-paced conversion: one answered card tans up to 28 hides for
        # 28 coins (1 coin per hide), and Anki undo restores both.
        addon = _load_addon_as_package("ankiscape_tanning_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Cowhide": 30, "Coins": 100},
            "crafting_exp": 0,
            "current_utility": "tan_soft_leather",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Leather"], 28)
        self.assertEqual(addon._state.player_data["inventory"]["Cowhide"], 2)
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 72)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Cowhide": 30, "Coins": 100})
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_source_gathering_actions_roll_back_on_answer_undo(self):
        cases = (
            ("gather_wool", "Wool", 28),
            ("gather_swamp_toads", "Swamp toad", 28),
            ("gather_blue_dragon_scales", "Blue dragon scale", 7),
            ("gather_potato_cacti", "Potato cactus", 3),
            ("gather_black_mushrooms", "Black mushroom", 1),
            ("gather_doogle_leaves", "Doogle leaves", 2),
            ("gather_goblin_mail", "Goblin mail", 3),
            ("pick_cabbages", "Cabbage", 28),
            ("pick_potatoes", "Potato", 28),
            ("pick_onions", "Onion", 28),
            ("pick_redberries", "Redberries", 4),
            ("pick_cadava_berries", "Cadava berries", 2),
            ("pick_bananas", "Banana", 28),
            ("pick_pineapples", "Pineapple", 1),
        )
        for action_id, output_item, output_qty in cases:
            with self.subTest(action_id=action_id):
                addon = _load_addon_as_package(
                    f"ankiscape_{action_id}_undo_integration"
                )
                calls = {"save": 0}
                addon.check_achievements = lambda _data: None
                addon.save_player_data = lambda: calls.__setitem__(
                    "save",
                    calls["save"] + 1,
                )
                addon.update_review_hud = lambda _data, _skill: None
                addon._refresh_skill_availability = lambda: None
                addon.show_error_message = lambda _title, message: self.fail(message)
                addon._state.player_data = {
                    "inventory": {},
                    "crafting_exp": 0,
                    "current_utility": action_id,
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

                self.assertEqual(addon._state.player_data["inventory"], {output_item: output_qty})
                self.assertEqual(addon._state.player_data["crafting_exp"], 0)
                self.assertEqual(len(addon._state.review_undo_stack), 1)

                changes = types.SimpleNamespace(
                    operation="Answer Card",
                    changes=types.SimpleNamespace(study_queues=True, card=True),
                )
                addon._on_state_did_undo(changes)

                self.assertEqual(addon._state.player_data["inventory"], {})
                self.assertEqual(addon._state.player_data["crafting_exp"], 0)
                self.assertEqual(addon._state.review_undo_stack, [])
                self.assertGreaterEqual(calls["save"], 2)

    def test_goblin_diplomacy_processing_actions_roll_back_on_answer_undo(self):
        cases = (
            ("aggie_make_red_dye", {"Redberries": 3, "Coins": 5}, "Red dye"),
            ("aggie_make_yellow_dye", {"Onion": 2, "Coins": 5}, "Yellow dye"),
            ("mix_orange_dye", {"Red dye": 1, "Yellow dye": 1}, "Orange dye"),
            ("aggie_make_blue_dye", {"Woad leaf": 2, "Coins": 5}, "Blue dye"),
            ("dye_goblin_mail_orange", {"Goblin mail": 1, "Orange dye": 1}, "Orange goblin mail"),
            ("dye_goblin_mail_blue", {"Goblin mail": 1, "Blue dye": 1}, "Blue goblin mail"),
        )
        for action_id, starting_inventory, output_item in cases:
            with self.subTest(action_id=action_id):
                addon = _load_addon_as_package(
                    f"ankiscape_{action_id}_undo_integration"
                )
                calls = {"save": 0}
                addon.check_achievements = lambda _data: None
                addon.save_player_data = lambda: calls.__setitem__(
                    "save",
                    calls["save"] + 1,
                )
                addon.update_review_hud = lambda _data, _skill: None
                addon._refresh_skill_availability = lambda: None
                addon.show_error_message = lambda _title, message: self.fail(message)
                addon._state.player_data = {
                    "inventory": dict(starting_inventory),
                    "crafting_exp": 0,
                    "current_utility": action_id,
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

                self.assertEqual(addon._state.player_data["inventory"][output_item], 1)
                for item_name in starting_inventory:
                    self.assertEqual(addon._state.player_data["inventory"][item_name], 0)
                self.assertEqual(addon._state.player_data["crafting_exp"], 0)
                self.assertEqual(len(addon._state.review_undo_stack), 1)

                changes = types.SimpleNamespace(
                    operation="Answer Card",
                    changes=types.SimpleNamespace(study_queues=True, card=True),
                )
                addon._on_state_did_undo(changes)

                self.assertEqual(addon._state.player_data["inventory"], starting_inventory)
                self.assertEqual(addon._state.player_data["crafting_exp"], 0)
                self.assertEqual(addon._state.review_undo_stack, [])
                self.assertGreaterEqual(calls["save"], 2)

    def test_crystal_chest_answer_and_undo_are_atomic(self):
        addon = _load_addon_as_package("ankiscape_crystal_chest_undo_integration")
        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Crystal key": 1},
            "equipment": {},
            "current_utility": "open_crystal_chest",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Utility / Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        addon.random.random = lambda: 0.4
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Crystal key"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Uncut dragonstone"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Crystal key": 1})
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertGreaterEqual(calls["save"], 2)
