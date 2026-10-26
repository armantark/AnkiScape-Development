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
    def test_evil_tree_spawns_on_shared_review_clock_and_undo_restores_world(self):
        addon = _load_addon_as_package("ankiscape_evil_tree_clock_integration")
        from ankiscape_evil_tree_clock_integration.logic.evil_tree_logic import (
            default_evil_tree_state_pure,
        )

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        world_event_gains = []
        addon._show_activity_gain = world_event_gains.append
        addon.check_achievements = lambda *_args: None
        initial = {
            "inventory": {},
            "shop_market_clock": {"answered_cards": 19, "market_tick": 19},
            "world_clock": {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 11_994},
            "evil_tree": {**default_evil_tree_state_pure(), "next_spawn_tick": 12_000},
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
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

        event = addon._state.player_data["evil_tree"]["active_event"]
        self.assertEqual(event["tier_id"], "normal")
        self.assertEqual(event["ticks_remaining"], 3_000)
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["answered_cards"], 20
        )
        # The spawn is silent. These messages ran after the per-review feedback
        # context had closed, so each one became its own floating popup.
        self.assertEqual(world_event_gains, [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(
                    study_queues=True,
                    card=True,
                ),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_big_chinchompa_spawns_on_review_clock_and_undo_restores_world(self):
        addon = _load_addon_as_package(
            "ankiscape_big_chinchompa_clock_integration"
        )
        from ankiscape_big_chinchompa_clock_integration.logic.big_chinchompa_logic import (
            default_big_chinchompa_state_pure,
        )

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        world_event_gains = []
        addon._show_activity_gain = world_event_gains.append
        initial = {
            "inventory": {},
            "shop_market_clock": {
                "answered_cards": 59,
                "market_tick": 59,
            },
            "world_population_profile": "quiet",
            "big_chinchompa": default_big_chinchompa_state_pure(),
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        event = addon._state.player_data["big_chinchompa"]["active_event"]
        self.assertEqual(event["slot_card"], 60)
        self.assertIn("Hunter area", event["location"])
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["answered_cards"],
            60,
        )
        self.assertEqual(world_event_gains, [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(
                    study_queues=True,
                    card=True,
                ),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_shooting_star_spawns_on_review_clock_and_undo_restores_world(self):
        addon = _load_addon_as_package(
            "ankiscape_shooting_star_clock_integration"
        )
        from ankiscape_shooting_star_clock_integration.logic.shooting_star_logic import (
            default_shooting_star_state_pure,
        )

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        world_event_gains = []
        addon._show_activity_gain = world_event_gains.append
        initial = {
            "inventory": {},
            "shop_market_clock": {
                "answered_cards": 19,
                "market_tick": 19,
            },
            "world_population_profile": "normal",
            "shooting_star": default_shooting_star_state_pure(),
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        event = addon._state.player_data["shooting_star"]["active_event"]
        self.assertEqual(event["slot_card"], 20)
        self.assertIn(event["starting_size"], range(1, 10))
        self.assertEqual(
            addon._state.player_data["shop_market_clock"]["answered_cards"],
            20,
        )
        self.assertEqual(world_event_gains, [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(
                    study_queues=True,
                    card=True,
                ),
            )
        )
        self.assertEqual(addon._state.player_data, initial)

    def test_shooting_star_unminable_review_exit_and_banner_undo_together(self):
        addon = _load_addon_as_package("ankiscape_star_unminable_undo")
        from ankiscape_star_unminable_undo.logic.shooting_star_logic import (
            default_shooting_star_state_pure,
        )

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        refreshed = {"context": 0, "events": 0}
        addon.update_review_context_action_strip = lambda *_args: refreshed.__setitem__(
            "context", refreshed["context"] + 1
        )
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: refreshed.__setitem__(
            "events", refreshed["events"] + 1
        )
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        state = default_shooting_star_state_pure()
        state["active_event"] = {
            "event_id": "shooting-star-20",
            "slot_card": 20,
            "location": "Falador east mine",
            "starting_size": 9,
            "current_size": 9,
            "layer_remaining": 15,
        }
        initial = {
            "current_utility": "shooting_stars",
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "equipment": {},
            "mining_level": 10,
            "mining_exp": 0.0,
            "completed_achievements": [],
            "shop_market_clock": {"answered_cards": 20, "market_tick": 20},
            "shooting_star": state,
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Activities"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(
            addon._state.player_data["shooting_star"]["notice"]["kind"],
            "unminable",
        )
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)
        self.assertEqual(refreshed, {"context": 1, "events": 1})

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.current_skill, "Activities")
