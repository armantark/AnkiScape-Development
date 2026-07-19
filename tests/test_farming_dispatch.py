import copy
import sys
import types
import unittest

from tests.test_integration_smoke import _FakeReviewer, _install_runtime_fakes, _load_addon_as_package


class TestFarmingReviewDispatch(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _configure(self, addon):
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _exp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)

    def _queued_plant_state(self, addon):
        farming_logic = sys.modules[f"{addon.__name__}.farming_logic"]
        state = {
            "inventory": {"Rake": 1, "Seed dibber": 1, "Potato seed": 3, "Logs": 1},
            "farming_level": 1,
            "farming_exp": 0.0,
            "fletching_level": 1,
            "fletching_exp": 0.0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state, _, _ = farming_logic.add_farm_queue_step_pure(
            state,
            "plant",
            "falador_allotment_north",
            crop_id="potato",
        )
        return state

    def test_dispatch_order_is_shop_then_ge_then_farm(self):
        addon = _load_addon_as_package("ankiscape_farming_dispatch_order")
        self._configure(addon)
        order = []
        addon.player_data = {"inventory": {}}
        addon.current_skill = "None"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.advance_shop_market_clock_pure = lambda data: order.append("shop") or dict(data)
        addon.advance_ge_market_tick_pure = (
            lambda data, **_kwargs: (order.append("ge") or dict(data), {})
        )
        addon.runtime_actions.advance_farming_clock_for_review = lambda _ctx: order.append("farm") or {}

        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        self.assertEqual(order, ["shop", "ge", "farm"])

    def test_summoning_world_tick_runs_on_again_before_farming_clock(self):
        addon = _load_addon_as_package("ankiscape_summoning_world_dispatch")
        self._configure(addon)
        summoning_logic = sys.modules[f"{addon.__name__}.summoning_logic"]
        state = summoning_logic.default_summoning_state_pure()
        state["summoning_points_current"] = 10
        state["active_follower"] = {
            "kind": "familiar",
            "entity_id": "spiritwolf",
            "remaining_reviews": 3,
            "max_reviews": 3,
            "lifepoints": 100,
            "max_lifepoints": 100,
            "storage": {},
        }
        addon.player_data = {
            "inventory": {},
            "summoning_level": 10,
            "summoning_state": state,
        }
        addon.current_skill = "None"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        order = []
        original_tick = addon.advance_summoning_world_tick_pure

        def tracked_tick(data, **kwargs):
            order.append("summoning")
            return original_tick(data, **kwargs)

        addon.advance_shop_market_clock_pure = (
            lambda data: order.append("shop") or dict(data)
        )
        addon.advance_summoning_world_tick_pure = tracked_tick
        addon.runtime_actions.advance_farming_clock_for_review = (
            lambda _ctx: order.append("farm") or {}
        )

        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        self.assertEqual(order, ["shop", "summoning", "farm"])
        follower = addon.player_data["summoning_state"]["active_follower"]
        self.assertEqual(follower["remaining_reviews"], 2)
        self.assertEqual(
            addon.player_data["summoning_state"]["summoning_points_current"],
            10,
        )
        self.assertEqual(follower["summoning_point_drain_residual"], 0)

    def test_ge_fill_undo_and_reanswer_replay_the_same_market_transaction(self):
        addon = _load_addon_as_package("ankiscape_ge_review_dispatch")
        self._configure(addon)
        ge_logic = sys.modules[f"{addon.__name__}.grand_exchange_logic"]
        logs = {
            "tradeable": True,
            "exchangeable": True,
            "guide_price": 100,
            "buy_limit": 25_000,
        }
        initial = {
            **ge_logic.default_ge_state_pure(),
            "inventory": {"Coins": 1_000},
            "shop_market_clock": {"answered_cards": 7, "market_tick": 7},
            "completed_achievements": [],
        }
        initial["ge_market_state"]["last_processed_tick"] = 7
        initial, placed = ge_logic.place_ge_offer_pure(
            initial,
            side="buy",
            item_name="Logs",
            quantity=2,
            unit_price=150,
            item_spec=logs,
        )
        self.assertTrue(placed["ok"])
        initial = copy.deepcopy(initial)

        def deterministic_tick(data, **_kwargs):
            draws = iter((0.5, 0.0, 0.5, 1.0))
            return ge_logic.advance_ge_market_tick_pure(
                data,
                item_catalog={"Logs": logs},
                random_draw=lambda: next(draws),
            )

        addon.advance_ge_market_tick_pure = deterministic_tick
        addon.player_data = copy.deepcopy(initial)
        addon.current_skill = "None"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        first_answer = copy.deepcopy(addon.player_data)
        self.assertEqual(first_answer["shop_market_clock"]["market_tick"], 8)
        self.assertGreater(
            first_answer["ge_player_orders"][0]["completed_quantity"],
            0,
        )
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="Answer Card")
        )
        self.assertEqual(addon.player_data, initial)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])

        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data, first_answer)

    def test_success_consumes_one_farm_step_and_preempts_active_skill_multiplier(self):
        addon = _load_addon_as_package("ankiscape_farming_queue_dispatch")
        self._configure(addon)
        addon._review_action_multiplier = lambda: 10
        addon.player_data = self._queued_plant_state(addon)
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["farm_clock_minutes"], 6)
        self.assertEqual(addon.player_data["farm_queue"], [])
        self.assertEqual(addon.player_data["farm_patches"]["falador_allotment_north"]["crop_id"], "potato")
        self.assertEqual(addon.player_data["inventory"]["Logs"], 1)
        self.assertNotIn("Arrow shafts", addon.player_data["inventory"])
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

    def test_queued_farming_step_checks_achievements_once_with_one_review_snapshot(self):
        addon = _load_addon_as_package("ankiscape_farming_achievement_dispatch")
        self._configure(addon)
        checks = []
        addon.check_achievements = lambda data: checks.append(copy.deepcopy(data["farming_counters"]))
        addon.player_data = self._queued_plant_state(addon)
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]["plants"], 1)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

    def test_queue_full_run_action_evaluates_achievement_before_saving(self):
        addon = _load_addon_as_package("ankiscape_farming_full_run_achievement")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.farming_logic"]
        storage_pure = sys.modules[f"{addon.__name__}.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.constants"]
        state = storage_pure.default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        state["farming_level"] = 99
        state, ok, _ = farming_logic.set_farm_plan_pure(
            state, "falador_allotment_north", "potato"
        )
        self.assertTrue(ok)
        addon.player_data = state
        order = []
        addon.check_achievements = lambda data: order.append(("achievement", data["farming_counters"]["full_runs"]))
        addon.save_player_data = lambda: order.append(("save", addon.player_data["farming_counters"]["full_runs"]))
        addon.update_farming_hud_badge = lambda *_args: None
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)

        addon._on_main_menu()
        result = captured["on_farming_action"]("queue_full_run", {})

        self.assertTrue(result["ok"])
        self.assertEqual(order, [("achievement", 1), ("save", 1)])
        self.assertEqual(addon.player_data["farming_counters"]["full_runs"], 1)

    def test_failure_ticks_clock_but_never_consumes_queue_entry(self):
        addon = _load_addon_as_package("ankiscape_farming_failure_dispatch")
        self._configure(addon)
        addon.player_data = self._queued_plant_state(addon)
        before_step = copy.deepcopy(addon.player_data["farm_queue"])
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["farm_clock_minutes"], 6)
        self.assertEqual(addon.player_data["farm_queue"], before_step)
        self.assertEqual(addon.player_data["inventory"]["Potato seed"], 3)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

    def test_invalid_step_is_consumed_and_still_suppresses_active_action(self):
        addon = _load_addon_as_package("ankiscape_farming_skip_dispatch")
        self._configure(addon)
        addon.player_data = self._queued_plant_state(addon)
        addon.player_data["inventory"]["Potato seed"] = 0
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["farm_queue"], [])
        self.assertEqual(addon.player_data["inventory"]["Logs"], 1)
        self.assertNotIn("Arrow shafts", addon.player_data["inventory"])
        self.assertEqual(addon.player_data["farming_counters"]["queue_steps_skipped"], 1)

    def test_queued_cure_runs_before_death_boundary_then_settles_growth_eagerly(self):
        addon = _load_addon_as_package("ankiscape_farming_cure_boundary")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.farming_logic"]
        state = self._queued_plant_state(addon)
        state["farm_queue"] = []
        state["inventory"]["Plant cure"] = 1
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(ok)
        patch = state["farm_patches"]["falador_allotment_north"]
        state["farm_clock_minutes"] = 18
        patch["stage"] = 1
        patch["diseased"] = True
        state, _, _ = farming_logic.add_farm_queue_step_pure(
            state, "cure", "falador_allotment_north"
        )
        addon.player_data = state
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        patch = addon.player_data["farm_patches"]["falador_allotment_north"]
        self.assertEqual(addon.player_data["farm_clock_minutes"], 24)
        self.assertFalse(patch["dead"])
        self.assertGreaterEqual(patch["stage"], 2)
        self.assertEqual(addon.player_data["farm_queue"], [])

    def test_rejected_active_action_persists_farming_clock_exactly_once(self):
        addon = _load_addon_as_package("ankiscape_farming_rejected_action_save")
        self._configure(addon)
        saves = []
        addon.save_player_data = lambda: saves.append(copy.deepcopy(addon.player_data))
        addon.player_data = {
            "inventory": {"Logs": 0},
            "fletching_level": 1,
            "fletching_exp": 0.0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon.player_data.update(sys.modules[f"{addon.__name__}.farming_logic"].default_farming_state_pure())
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.show_error_message = lambda *_args: None

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["farm_clock_minutes"], 6)
        self.assertEqual(len(saves), 1)
        self.assertEqual(saves[0]["farm_clock_minutes"], 6)

    def test_farming_and_woodcutting_level_callbacks_see_pre_award_levels(self):
        addon = _load_addon_as_package("ankiscape_farming_level_notifications")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.farming_logic"]
        constants = sys.modules[f"{addon.__name__}.constants"]
        seen = []

        def level_check(skill, data):
            key = f"{skill.lower()}_level"
            seen.append((skill, data[key]))
            data[key] += 1

        addon.level_up_check = level_check
        potato = self._queued_plant_state(addon)
        potato["farming_exp"] = constants.EXP_TABLE[1] - 1
        addon.player_data = potato
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertIn(("Farming", 1), seen)
        self.assertEqual(addon.player_data["farming_level"], 2)

        tree = {
            "inventory": {"Rake": 1, "Spade": 1, "Oak sapling": 1},
            "farming_level": 99,
            "farming_exp": 0.0,
            "woodcutting_level": 15,
            "woodcutting_exp": constants.EXP_TABLE[15] - 1,
            "toolbelt": {"woodcutting": ["bronze_hatchet"]},
            "completed_achievements": [],
        }
        tree.update(farming_logic.default_farming_state_pure())
        tree, ok, _ = farming_logic.execute_farm_field_step_pure(
            tree, {"kind": "plant", "patch_id": "lumbridge_tree", "crop_id": "oak"}
        )
        self.assertTrue(ok)
        tree_patch = tree["farm_patches"]["lumbridge_tree"]
        tree_patch["stage"] = 99
        tree_patch["health_checked"] = True
        tree, _, _ = farming_logic.add_farm_queue_step_pure(tree, "chop", "lumbridge_tree")
        addon.player_data = tree
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertIn(("Woodcutting", 15), seen)
        self.assertEqual(addon.player_data["woodcutting_level"], 16)

    def test_one_snapshot_undo_restores_clock_rng_queue_inventory_and_xp_atomically(self):
        addon = _load_addon_as_package("ankiscape_farming_exact_undo")
        self._configure(addon)
        addon.player_data = self._queued_plant_state(addon)
        before = copy.deepcopy(addon.player_data)
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        original_random = addon.random.random
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon.random.random = lambda: 0.0

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertNotEqual(addon.player_data, before)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))

        self.assertEqual(addon.player_data, before)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])

    def test_answer_undo_restores_current_skill_and_rng_for_deterministic_replay(self):
        addon = _load_addon_as_package("ankiscape_farming_full_transaction_undo")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.farming_logic"]
        state = self._queued_plant_state(addon)
        state["farm_queue"] = []
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(ok)
        state["inventory"]["Logs"] = 0
        state["farm_clock_minutes"] = 18
        state["farm_patches"]["falador_allotment_north"]["stage"] = 1
        addon.player_data = state
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.show_error_message = lambda *_args: None
        addon.random.seed(7)
        before = copy.deepcopy(state)
        before_rng = addon.random.getstate()

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        first_disease = addon.player_data["farm_patches"]["falador_allotment_north"]["diseased"]
        self.assertEqual(addon.current_skill, "None")
        self.assertNotEqual(addon.random.getstate(), before_rng)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon.player_data, before)
        self.assertEqual(addon.current_skill, "Fletching")
        self.assertEqual(addon.random.getstate(), before_rng)

        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(
            addon.player_data["farm_patches"]["falador_allotment_north"]["diseased"],
            first_disease,
        )

    def test_undo_restores_a_boundary_rng_disease_outcome(self):
        addon = _load_addon_as_package("ankiscape_farming_boundary_undo")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.farming_logic"]
        state = self._queued_plant_state(addon)
        state["farm_queue"] = []
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(ok)
        state["farm_clock_minutes"] = 18
        state["farm_patches"]["falador_allotment_north"]["stage"] = 1
        addon.player_data = state
        before = copy.deepcopy(state)
        addon.current_skill = "None"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        original_random = addon.random.random
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon.random.random = lambda: 0.0

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertTrue(addon.player_data["farm_patches"]["falador_allotment_north"]["diseased"])
        self.assertEqual(addon.player_data["farm_clock_minutes"], 24)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))

        self.assertEqual(addon.player_data, before)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])


if __name__ == "__main__":
    unittest.main()
