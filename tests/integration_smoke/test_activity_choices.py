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
    def test_fatal_wilderness_lap_ambush_and_carried_pack_roll_back_as_one_review(self):
        addon = _load_addon_as_package("ankiscape_wilderness_agility_undo_integration")
        addon.mw = _DummyMW(_DummyCol())
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _exp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        initial = {
            "current_agility": "wilderness_course",
            "agility_level": 99,
            "agility_exp": 0.0,
            "combat_lifepoints": 100,
            "hitpoints_level": 10,
            "combat_auto_eat_threshold_percent": 40,
            "combat_auto_eat_food": ["Shark"],
            "inventory": {"Shark": 1, "Penance horn": 1},
            "equipment": {"weapon": "Bronze sword"},
            "completed_achievements": [],
            "agility_effect_charges": {"Penance horn": 2},
            "agility_lap_counts": {
                "total": 0,
                "flawless": 0,
                "gnome_advanced_flawless": 0,
                "barbarian_advanced_flawless": 0,
                "agile_legs_unlocked": False,
                "agile_top_unlocked": False,
            },
            "agility_course_state": {
                "target": "wilderness_course",
                "stage": 5,
                "checkpoint": "start",
                "flawless": True,
                "lap_xp_valid": True,
                "requested_item_valid": True,
                "status": "",
            },
            "agility_pit_offer": False,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Agility"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        rolls = iter((0.99, 0.0, 0.005, 0.90) + (0.5,) * 100)
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["agility_exp"], 0.0)
        self.assertEqual(addon._state.player_data["agility_lap_counts"]["total"], 0)
        self.assertEqual(addon._state.player_data["agility_effect_charges"]["Penance horn"], 2)
        self.assertEqual(
            addon._state.player_data["combat_grave"]["source"],
            "agility_wilderness_pker",
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_explicit_pit_reward_choice_is_directly_undoable_with_rng(self):
        addon = _load_addon_as_package("ankiscape_pit_context_direct_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        shown_xp = []
        addon._show_exp = shown_xp.append
        initial = {
            "agility_level": 50,
            "agility_exp": 10.0,
            "agility_activity_state": {
                "pit_reward": {"xp": 100.0, "course": "gnome_normal"}
            },
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Agility"
        addon.random.seed(314159)
        before_rng = addon.random.getstate()

        self.assertTrue(
            addon.resolve_review_context_action("pit_reward", "gamble")
        )

        self.assertNotIn(
            "pit_reward",
            addon._state.player_data["agility_activity_state"],
        )
        self.assertEqual(
            addon._state.player_data["review_context_preferences"]["pit_reward"],
            "gamble",
        )
        self.assertIn(shown_xp[-1], {50.0, 100.0, 200.0})
        self.assertEqual(
            addon._state.player_data["agility_exp"],
            10.0 + shown_xp[-1],
        )
        self.assertNotEqual(addon.random.getstate(), before_rng)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon.random.getstate(), before_rng)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_shooting_star_ready_banner_rejoins_in_one_undoable_action(self):
        addon = _load_addon_as_package("ankiscape_star_notice_direct_integration")
        from ankiscape_star_notice_direct_integration.logic.shooting_star_logic import (
            default_shooting_star_state_pure,
        )

        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        state = default_shooting_star_state_pure()
        state["active_event"] = {
            "event_id": "shooting-star-20",
            "slot_card": 20,
            "location": "Falador east mine",
            "starting_size": 1,
            "current_size": 1,
            "layer_remaining": 1_200,
        }
        state["watched_event_id"] = "shooting-star-20"
        state["notice"] = {
            "kind": "ready",
            "event_id": "shooting-star-20",
            "current_size": 1,
            "required_level": 10,
            "sprite_available": False,
        }
        initial = {
            "current_utility": "bankstanding",
            "mining_level": 10,
            "shooting_star": state,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Woodcutting"

        self.assertTrue(
            addon.resolve_review_context_action("shooting_star_notice", "mine")
        )

        self.assertEqual(addon._state.player_data["current_utility"], "shooting_stars")
        self.assertEqual(addon._state.current_skill, "Activities")
        self.assertEqual(addon._state.player_data["shooting_star"]["notice"], {})
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.current_skill, "Woodcutting")
        self.assertEqual(col.get_config("ankiscape_current_skill"), "Woodcutting")

    def test_explicit_phoenix_egg_choice_is_directly_undoable(self):
        addon = _load_addon_as_package("ankiscape_phoenix_context_direct_integration")
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        initial = {
            "inventory": {},
            "summoning_level": 71,
            "summoning_state": {
                "pet_instances": {},
                "pet_next_instance_id": 1,
            },
            "phoenix_lair": {
                "pending_egg": True,
                "runs_completed": 1,
            },
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Activities"

        self.assertTrue(
            addon.resolve_review_context_action("phoenix_egg", "kick")
        )

        self.assertEqual(addon._state.player_data["inventory"]["Cracked phoenix egg"], 1)
        self.assertEqual(
            addon._state.player_data["review_context_preferences"]["phoenix_egg"],
            "kick",
        )
        self.assertFalse(addon._state.player_data["phoenix_lair"]["pending_egg"])
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.direct_action_undo_stack, [])
