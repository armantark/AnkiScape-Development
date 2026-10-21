import copy
import sys
import types
import unittest
from unittest.mock import patch

from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


class TestFarmingReviewDispatch(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _configure(self, addon):
        addon.mw = _DummyMW(_DummyCol())
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _exp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)

    def _queued_plant_state(self, addon):
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
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
        addon._state.player_data = {"inventory": {}}
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.advance_shop_market_clock_pure = lambda data: order.append("shop") or dict(data)
        addon.advance_ge_market_tick_pure = (
            lambda data, **_kwargs: (order.append("ge") or dict(data), {})
        )
        addon.runtime_actions.advance_farming_clock_for_review = lambda _ctx: order.append("farm") or {}

        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        self.assertEqual(order, ["shop", "ge", "farm"])

    def test_ge_fills_leave_the_active_skill_working(self):
        addon = _load_addon_as_package("ankiscape_ge_bank_run_dispatch")
        self._configure(addon)
        addon._state.player_data = {"inventory": {}}
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.advance_ge_market_tick_pure = lambda data, **_kwargs: (
            dict(data),
            {
                "fills": [
                    {"side": "buy", "completed_quantity": 76, "original_quantity": 100},
                    {"side": "sell", "completed_quantity": 34, "original_quantity": 34},
                ]
            },
        )
        bank_runs = []
        addon._request_active_bank_run_state = lambda data: (
            bank_runs.append(data) or (dict(data), True, "", False)
        )

        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        self.assertEqual(bank_runs, [])

    def test_summoning_world_tick_runs_on_again_before_farming_clock(self):
        addon = _load_addon_as_package("ankiscape_summoning_world_dispatch")
        self._configure(addon)
        summoning_logic = sys.modules[f"{addon.__name__}.logic.summoning_logic"]
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
        addon._state.player_data = {
            "inventory": {},
            "summoning_level": 10,
            "summoning_state": state,
        }
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
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
        follower = addon._state.player_data["summoning_state"]["active_follower"]
        # The saved three cards migrate to 600 ticks; one speed-1 Again spends 6.
        self.assertEqual(follower["remaining_ticks"], 594)
        self.assertEqual(
            addon._state.player_data["summoning_state"]["summoning_points_current"],
            10,
        )
        self.assertEqual(follower["summoning_point_drain_residual"], 0)

    def test_outside_bunyip_cannot_heal_in_daemonheim_and_resumes_after_exit(self):
        addon = _load_addon_as_package("ankiscape_bunyip_daemonheim_dispatch")
        self._configure(addon)
        summoning = sys.modules[f"{addon.__name__}.logic.summoning_logic"]
        dungeon = sys.modules[f"{addon.__name__}.logic.dungeoneering_logic"]
        data = {
            "summoning_level": 68,
            "constitution_level": 10,
            "combat_lifepoints": 50,
            "inventory": {"Bunyip pouch": 1},
            "summoning_state": summoning.default_summoning_state_pure(),
        }
        data["summoning_state"]["summoning_points_current"] = 68
        data, summoned, _ = summoning.summon_familiar_pure(data, "bunyip")
        self.assertTrue(summoned)
        lifetime = data["summoning_state"]["active_follower"]["remaining_ticks"]
        points = data["summoning_state"]["summoning_points_current"]
        data, entered, _ = dungeon.apply_dungeoneering_command_pure(
            data, "enter", {"floor": 1}
        )
        self.assertTrue(entered)
        addon._state.player_data = data
        addon._state.current_skill = "Dungeoneering"

        for _ in range(5):
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        data = addon._state.player_data
        self.assertTrue(data["dungeoneering"]["active"])
        self.assertEqual(data["dungeoneering"]["floor"], 1)
        self.assertEqual(data["combat_lifepoints"], 50)
        follower = data["summoning_state"]["active_follower"]
        self.assertEqual(follower["entity_id"], "bunyip")
        self.assertEqual(follower["remaining_ticks"], lifetime - 5 * 6)
        # Thirty ticks of a 44-minute lifetime drain less than one point; the
        # drain still runs inside the floor.
        self.assertEqual(data["summoning_state"]["summoning_points_current"], points)
        self.assertGreater(follower["summoning_point_drain_residual"], 0)

        data, abandoned, _ = dungeon.apply_dungeoneering_command_pure(data, "abandon")
        self.assertTrue(abandoned)
        self.assertFalse(data["dungeoneering"]["active"])
        addon._state.player_data = data
        addon._state.current_skill = "None"
        for _ in range(5):
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        data = addon._state.player_data
        self.assertEqual(data["combat_lifepoints"], 70)
        self.assertEqual(
            data["summoning_state"]["active_follower"]["remaining_ticks"], lifetime - 10 * 6
        )

    def test_ge_fill_undo_and_reanswer_replay_the_same_market_transaction(self):
        addon = _load_addon_as_package("ankiscape_ge_review_dispatch")
        self._configure(addon)
        ge_logic = sys.modules[f"{addon.__name__}.logic.grand_exchange_logic"]
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
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        first_answer = copy.deepcopy(addon._state.player_data)
        self.assertEqual(first_answer["shop_market_clock"]["market_tick"], 8)
        self.assertGreater(
            first_answer["ge_player_orders"][0]["completed_quantity"],
            0,
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="Answer Card")
        )
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data, first_answer)

    def test_success_runs_the_farm_step_first_and_the_rest_of_the_card_on_the_skill(self):
        addon = _load_addon_as_package("ankiscape_farming_queue_dispatch")
        self._configure(addon)
        addon._review_action_multiplier = lambda: 10
        addon._state.player_data = self._queued_plant_state(addon)
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["farm_clock_minutes"], 6)
        self.assertEqual(addon._state.player_data["farm_queue"], [])
        self.assertEqual(addon._state.player_data["farm_patches"]["falador_allotment_north"]["crop_id"], "potato")
        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

    def test_farm_combat_xp_uses_one_review_combat_level_boundary(self):
        addon = _load_addon_as_package("ankiscape_farming_combat_popup_boundary")
        self._configure(addon)
        shared = sys.modules[f"{addon.__name__}.runtime.runtime_actions_shared"]
        addon._advance_world_events_after_review = lambda: None
        addon._state.player_data = self._queued_plant_state(addon)
        addon._state.player_data.update(
            {
                "attack_level": 1,
                "attack_exp": 0.0,
                "strength_level": 1,
                "defense_level": 1,
                "constitution_level": 10,
                "prayer_level": 1,
                "ranged_level": 1,
                "magic_level": 1,
                "summoning_level": 1,
            }
        )
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        checks = []
        addon._core_combat_level_up_check = lambda old, data: checks.append(
            (old, addon.player_combat_level_pure(data))
        )

        def farm_handler(ctx):
            ctx.player_data["attack_exp"] = 200.0
            ctx.level_up_check = lambda _skill, data: data.__setitem__("attack_level", 10)
            shared._refresh_combat_levels(ctx, {"attack_exp": 200.0})
            return True

        addon.runtime_actions.handle_farming_review_answer = farm_handler
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(len(checks), 1)
        self.assertLess(checks[0][0], checks[0][1])

    def test_queued_farming_step_checks_achievements_once_with_one_review_snapshot(self):
        addon = _load_addon_as_package("ankiscape_farming_achievement_dispatch")
        self._configure(addon)
        checks = []
        addon.check_achievements = lambda data: checks.append(copy.deepcopy(data["farming_counters"]))
        addon._state.player_data = self._queued_plant_state(addon)
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]["plants"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

    def test_queue_full_run_action_evaluates_achievement_before_saving(self):
        addon = _load_addon_as_package("ankiscape_farming_full_run_achievement")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        storage_pure = sys.modules[f"{addon.__name__}.core.storage_pure"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        state = storage_pure.default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        state["farming_level"] = 99
        state, ok, _ = farming_logic.set_farm_plan_pure(
            state, "falador_allotment_north", "potato"
        )
        self.assertTrue(ok)
        addon._state.player_data = state
        order = []
        addon.check_achievements = lambda data: order.append(("achievement", data["farming_counters"]["full_runs"]))
        addon.save_player_data = lambda: order.append(("save", addon._state.player_data["farming_counters"]["full_runs"]))
        addon.update_review_status_badge = lambda *_args: None
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)

        addon._on_main_menu()
        result = captured["on_farming_action"]("queue_full_run", {})

        self.assertTrue(result["ok"])
        self.assertEqual(order, [("achievement", 1), ("save", 1)])
        self.assertEqual(addon._state.player_data["farming_counters"]["full_runs"], 1)

    def test_failure_ticks_clock_but_never_consumes_queue_entry(self):
        addon = _load_addon_as_package("ankiscape_farming_failure_dispatch")
        self._configure(addon)
        addon._state.player_data = self._queued_plant_state(addon)
        before_step = copy.deepcopy(addon._state.player_data["farm_queue"])
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["farm_clock_minutes"], 6)
        self.assertEqual(addon._state.player_data["farm_queue"], before_step)
        self.assertEqual(addon._state.player_data["inventory"]["Potato seed"], 3)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

    def test_invalid_step_is_consumed_and_still_suppresses_active_action(self):
        addon = _load_addon_as_package("ankiscape_farming_skip_dispatch")
        self._configure(addon)
        addon._state.player_data = self._queued_plant_state(addon)
        addon._state.player_data["inventory"]["Potato seed"] = 0
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["farm_queue"], [])
        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 1)
        self.assertNotIn("Arrow shafts", addon._state.player_data["inventory"])
        self.assertEqual(addon._state.player_data["farming_counters"]["queue_steps_skipped"], 1)

    def test_queued_cure_runs_before_death_boundary_then_settles_growth_eagerly(self):
        addon = _load_addon_as_package("ankiscape_farming_cure_boundary")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
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
        addon._state.player_data = state
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        patch = addon._state.player_data["farm_patches"]["falador_allotment_north"]
        self.assertEqual(addon._state.player_data["farm_clock_minutes"], 24)
        self.assertFalse(patch["dead"])
        self.assertGreaterEqual(patch["stage"], 2)
        self.assertEqual(addon._state.player_data["farm_queue"], [])

    def test_rejected_active_action_persists_farming_clock_exactly_once(self):
        addon = _load_addon_as_package("ankiscape_farming_rejected_action_save")
        self._configure(addon)
        saves = []
        addon.save_player_data = lambda: saves.append(copy.deepcopy(addon._state.player_data))
        addon._state.player_data = {
            "inventory": {"Logs": 0},
            "fletching_level": 1,
            "fletching_exp": 0.0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon._state.player_data.update(sys.modules[f"{addon.__name__}.logic.farming_logic"].default_farming_state_pure())
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.show_error_message = lambda *_args: None

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["farm_clock_minutes"], 6)
        self.assertEqual(len(saves), 1)
        self.assertEqual(saves[0]["farm_clock_minutes"], 6)

    def test_farming_and_woodcutting_level_callbacks_see_pre_award_levels(self):
        addon = _load_addon_as_package("ankiscape_farming_level_notifications")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        constants = sys.modules[f"{addon.__name__}.core.constants"]
        seen = []

        def level_check(skill, data):
            key = f"{skill.lower()}_level"
            seen.append((skill, data[key]))
            data[key] += 1

        addon.level_up_check = level_check
        potato = self._queued_plant_state(addon)
        potato["farming_exp"] = constants.EXP_TABLE[1] - 1
        addon._state.player_data = potato
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertIn(("Farming", 1), seen)
        self.assertEqual(addon._state.player_data["farming_level"], 2)

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
        addon._state.player_data = tree
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertIn(("Woodcutting", 15), seen)
        self.assertEqual(addon._state.player_data["woodcutting_level"], 16)

    def test_one_snapshot_undo_restores_clock_rng_queue_inventory_and_xp_atomically(self):
        addon = _load_addon_as_package("ankiscape_farming_exact_undo")
        self._configure(addon)
        addon._state.player_data = self._queued_plant_state(addon)
        before = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon.random.random = lambda: 0.0

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertNotEqual(addon._state.player_data, before)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))

        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_answer_undo_restores_current_skill_and_rng_for_deterministic_replay(self):
        addon = _load_addon_as_package("ankiscape_farming_full_transaction_undo")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
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
        addon._state.player_data = state
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.show_error_message = lambda *_args: None
        addon.random.seed(7)
        before = copy.deepcopy(state)
        before_rng = addon.random.getstate()

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        first_disease = addon._state.player_data["farm_patches"]["falador_allotment_north"]["diseased"]
        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertNotEqual(addon.random.getstate(), before_rng)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon._state.current_skill, "Fletching")
        self.assertEqual(addon.random.getstate(), before_rng)

        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(
            addon._state.player_data["farm_patches"]["falador_allotment_north"]["diseased"],
            first_disease,
        )

    def test_undo_restores_a_boundary_rng_disease_outcome(self):
        addon = _load_addon_as_package("ankiscape_farming_boundary_undo")
        self._configure(addon)
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        state = self._queued_plant_state(addon)
        state["farm_queue"] = []
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(ok)
        state["farm_clock_minutes"] = 18
        state["farm_patches"]["falador_allotment_north"]["stage"] = 1
        addon._state.player_data = state
        before = copy.deepcopy(state)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        original_random = addon.random.random
        self.addCleanup(setattr, addon.random, "random", original_random)
        addon.random.random = lambda: 0.0

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertTrue(addon._state.player_data["farm_patches"]["falador_allotment_north"]["diseased"])
        self.assertEqual(addon._state.player_data["farm_clock_minutes"], 24)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))

        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon._state.review_undo_stack, [])

    # A Wild jade vine bind, death or flee in a queued step ends the card (decision 5).
    def _fight_wild_jade_vine(self, lifepoints, speed=3):
        addon = _load_addon_as_package("ankiscape_jade_vine_danger_stop")
        self._configure(addon)
        addon._review_action_multiplier = lambda: speed
        # At this fixed roll the vine first hits in the second six-tick slice,
        # and every hit rolls the one-in-six bind.
        self.enterContext(patch.object(addon.random, "random", lambda: 0.05))
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        state = {
            "inventory": {"Secateurs": 1, "Logs": 1},
            "toolbelt": {"woodcutting": ["bronze_hatchet"]},
            "equipment": {"weapon": "Bronze hatchet"},
            "quests": {"back_to_my_roots": {"completed": True}},
            "farming_level": 99,
            "woodcutting_level": 99,
            "slayer_level": 99,
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": lifepoints,
            "combat_auto_flee": False,
            "fletching_level": 1,
            "fletching_exp": 0.0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state["farm_patches"]["handelmort_jade_vine"].update(
            {"crop_id": "jade_vine", "last_crop_id": "jade_vine", "stage": 6, "health_checked": True, "jade_state": "wild"}
        )
        state, _, _ = farming_logic.add_farm_queue_step_pure(state, "chop", "handelmort_jade_vine")
        addon._state.player_data = state
        addon._state.current_skill = "Fletching"
        return addon

    def _answer_card(self, addon):
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        return addon._state.player_data

    def test_a_bind_ends_the_card_and_is_paid_inside_a_speed_three_card(self):
        addon = self._fight_wild_jade_vine(990)

        data = self._answer_card(addon)
        self.assertEqual(data["combat_lifepoints"], 982)
        self.assertNotIn("card_tick_debt", data)

        # Nothing carried, so the next card fights from its first step.
        data = self._answer_card(addon)
        self.assertEqual(data["combat_lifepoints"], 974)
        self.assertEqual(data["inventory"]["Logs"], 1)

    def test_at_speed_one_a_bind_holds_exactly_the_next_card(self):
        addon = self._fight_wild_jade_vine(990, speed=1)
        self._answer_card(addon)
        data = self._answer_card(addon)
        self.assertEqual((data["combat_lifepoints"], data["card_tick_debt"]), (982, 6))
        clock = data["farm_clock_minutes"]

        # The held card neither fights nor fletches, but the farm clock moves.
        data = self._answer_card(addon)
        self.assertEqual(data["combat_lifepoints"], 982)
        self.assertNotIn("card_tick_debt", data)
        self.assertGreater(data["farm_clock_minutes"], clock)

        data = self._answer_card(addon)
        self.assertEqual(data["combat_lifepoints"], 974)
        self.assertEqual(data["inventory"]["Logs"], 1)

    def test_a_death_ends_the_card_before_the_selected_skill_runs(self):
        addon = self._fight_wild_jade_vine(5)
        addon._state.player_data["farm_patches"]["handelmort_jade_vine"]["jade_combat_encounter"] = {
            "target_id": "wild_jade_vine", "enemy_lifepoints": 2500,
            "enemy_attack_ticks_remaining": 0,
        }
        engine = sys.modules[f"{addon.__name__}.logic_pure.logic_pure_combat_engine"]
        self.enterContext(patch.object(
            engine, "_combat_roll_hit",
            side_effect=lambda *_args, **kw: (False, 0) if "blocked" in kw else (True, 10),
        ))

        data = self._answer_card(addon)

        self.assertEqual(data["farm_queue"], [])
        self.assertEqual(data["inventory"]["Logs"], 1)
        self.assertNotIn("Arrow shafts", data["inventory"])


if __name__ == "__main__":
    unittest.main()
