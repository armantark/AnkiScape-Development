from tests.test_integration_smoke import _FakeReviewer, _load_addon_as_package, copy, sys, types
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_firemaking_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_firemaking_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        achievements = sys.modules[f"{addon.__name__}.core.constants"].ACHIEVEMENTS
        def complete_first_fire(data):
            if achievements["First Fire"]["condition"](data):
                data["completed_achievements"].append("First Fire")
        addon.check_achievements = complete_first_fire
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Logs": 1},
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

        self.assertEqual(addon._state.player_data["inventory"], {"Logs": 0, "Ashes": 1})
        self.assertAlmostEqual(addon._state.player_data["firemaking_exp"], 40.0)
        self.assertEqual(
            addon._state.player_data["achievement_progress"]["skills"]["firemaking"]["outputs"],
            {"Ashes": 1},
        )
        self.assertIn("First Fire", addon._state.player_data["completed_achievements"])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Logs": 1})
        self.assertEqual(addon._state.player_data["firemaking_exp"], 0)
        self.assertNotIn("achievement_progress", addon._state.player_data)
        self.assertEqual(addon._state.player_data["completed_achievements"], [])
        self.assertEqual(addon._state.player_data["current_firemaking"], "logs")
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [40.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_fishing_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_fishing_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Feather": 1},
            "fishing_level": 48,
            "fishing_exp": 0,
            "strength_level": 15,
            "strength_exp": 0,
            "agility_level": 15,
            "agility_exp": 0,
            "current_fishing": "catch_leaping_fish",
            "completed_achievements": [],
            "unlocked_abilities": ["barbarian_fishing"],
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

        self.assertEqual(addon._state.player_data["inventory"], {"Feather": 0, "Leaping trout": 1})
        self.assertAlmostEqual(addon._state.player_data["fishing_exp"], 50.0)
        self.assertAlmostEqual(addon._state.player_data["strength_exp"], 5.0)
        self.assertAlmostEqual(addon._state.player_data["agility_exp"], 5.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Feather": 1})
        self.assertEqual(addon._state.player_data["fishing_exp"], 0)
        self.assertEqual(addon._state.player_data["strength_exp"], 0)
        self.assertEqual(addon._state.player_data["agility_exp"], 0)
        self.assertEqual(addon._state.player_data["current_fishing"], "catch_leaping_fish")
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [50.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_eucalyptus_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_eucalyptus_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        initial = {
            "inventory": {},
            "woodcutting_level": 58,
            "woodcutting_exp": 0.0,
            "current_tree": "eucalyptus",
            "toolbelt": {"woodcutting": ["rune_hatchet"]},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Woodcutting"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Eucalyptus logs"], 1)
        self.assertEqual(addon._state.player_data["woodcutting_exp"], 165.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [165.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_seaweed_cooking_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_seaweed_cooking_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Seaweed": 1},
            "cooking_level": 1,
            "cooking_exp": 0,
            "current_cooking": "burn_seaweed",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 1.0
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"], {"Seaweed": 0, "Soda ash": 1})
        self.assertAlmostEqual(addon._state.player_data["cooking_exp"], 1.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Seaweed": 1})
        self.assertEqual(addon._state.player_data["cooking_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [1.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_cooking_gauntlet_auto_equip_and_success_roll_back_with_review(self):
        addon = _load_addon_as_package(
            "ankiscape_cooking_gauntlets_review_undo_integration"
        )
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Raw shark": 1, "Cooking gauntlets": 1},
            "equipment": {"hands": "Leather gloves"},
            "cooking_level": 94,
            "cooking_exp": 0,
            "current_cooking": "cook_shark",
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.999
        try:
            addon.on_answer_card(
                _FakeReviewer(), 4, lambda _self, _ease: "answered"
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(
            addon._state.player_data["equipment"]["hands"], "Cooking gauntlets"
        )
        self.assertEqual(addon._state.player_data["inventory"]["Leather gloves"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Shark"], 1)
        self.assertEqual(addon._state.player_data["cooking_exp"], 210.0)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_lava_eel_cooking_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_lava_eel_cooking_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Raw lava eel": 1},
            "cooking_level": 53,
            "cooking_exp": 0,
            "current_cooking": "cook_lava_eel",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Raw lava eel": 0, "Lava eel": 1})
        self.assertAlmostEqual(addon._state.player_data["cooking_exp"], 30.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Raw lava eel": 1})
        self.assertEqual(addon._state.player_data["cooking_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [30.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_bad_wine_review_outcome_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_bad_wine_undo_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: self.fail(f"bad wine awarded {exp} XP")
        addon._show_activity_gain = lambda _text: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Grapes": 1, "Jug of water": 1},
            "cooking_level": 35,
            "cooking_exp": 0.0,
            "current_cooking": "make_wine",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.61
        try:
            addon.on_answer_card(
                _FakeReviewer(), 4, lambda _self, _ease: "answered"
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Grapes": 0, "Jug of water": 0, "Jug of bad wine": 1},
        )
        self.assertEqual(addon._state.player_data["cooking_exp"], 0.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_barley_malt_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_barley_malt_undo_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: self.fail(f"barley malt awarded {exp} XP")
        addon._show_activity_gain = lambda _text: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Barley": 1},
            "cooking_level": 1,
            "cooking_exp": 0.0,
            "current_cooking": "malt_barley",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Barley": 0, "Barley malt": 1},
        )
        self.assertEqual(addon._state.player_data["cooking_exp"], 0.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_poison_karambwan_burn_rolls_back_on_review_undo(self):
        addon = _load_addon_as_package("ankiscape_poison_karambwan_undo_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: self.fail(f"burnt karambwan awarded {exp} XP")
        addon._show_activity_gain = lambda _text: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Raw karambwan": 1},
            "cooking_level": 1,
            "cooking_exp": 0.0,
            "current_cooking": "cook_poison_karambwan",
            "cooking_success_count": 0,
            "cooking_burn_count": 0,
            "completed_achievements": [],
            "quests": {
                "tai_bwo_wannai_trio": {
                    "started": True,
                    "progress": 1,
                    "completed": False,
                }
            },
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 1.0
        try:
            addon.on_answer_card(
                _FakeReviewer(), 4, lambda _self, _ease: "answered"
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Raw karambwan": 0, "Burnt karambwan": 1},
        )
        self.assertEqual(addon._state.player_data["cooking_exp"], 0.0)
        self.assertEqual(addon._state.player_data["cooking_burn_count"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_cheese_wheel_slice_all_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_cheese_wheel_undo_integration")

        calls = {"save": 0, "xp": [], "activity": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._show_activity_gain = lambda text: calls["activity"].append(text)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Cheese wheel": 1},
            "cooking_level": 48,
            "cooking_exp": 0.0,
            "current_cooking": "slice_cheese_wheel",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Cooking"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            addon.random.random = original_random

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Cheese wheel": 0, "Cheese": 5},
        )
        self.assertEqual(addon._state.player_data["cooking_exp"], 20.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)
        self.assertEqual(calls["activity"], ["+5 Cheese"])

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Cheese wheel": 1})
        self.assertEqual(addon._state.player_data["cooking_exp"], 0.0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [20.0])
        self.assertGreaterEqual(calls["save"], 2)
