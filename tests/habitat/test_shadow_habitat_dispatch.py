"""Actual answer/undo dispatcher coverage for maintained Shadow Habitat."""

import copy
import importlib
import sys
import types
import unittest
from unittest.mock import patch

from tests.test_integration_smoke import (
    _DummyCol, _DummyMW, _FakeReviewer, _install_runtime_fakes, _load_addon_as_package,
)
from tests.habitat.fixtures import setup_state, established_state, TARGET, PATCH


class ShadowHabitatDispatchTest(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _boot(self, data=None, speed=1):
        addon = _load_addon_as_package("ankiscape_shadow_dispatch")
        addon.mw = _DummyMW(_DummyCol())
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        self.messages = []
        self.xp = []
        addon._show_exp = self.xp.append
        addon._show_activity_gain = self.messages.append
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._review_action_multiplier = lambda: speed
        self.enterContext(patch.object(addon.random, "random", lambda: 0.0))
        state = data if data is not None else setup_state()
        state.update(current_hunter=TARGET, hunter_exp=0, hunter_success_count=0, completed_achievements=[])
        addon._state.player_data = state
        addon._state.current_skill = "Hunter"
        return addon

    def _answer(self, addon, ease=4):
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), ease, lambda _self, _ease: "answered")
        return addon._state.player_data

    def _undo(self, addon):
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True)))

    def test_plant_replaces_one_catch_then_next_action_hunts_immature_red(self):
        addon = self._boot()
        first = copy.deepcopy(self._answer(addon))
        self.assertEqual(first["farm_patches"][PATCH]["crop_id"], "red_blossom")
        self.assertEqual(first["habitat_feature"], "abandoned_house")
        self.assertEqual(first["farming_exp"], 52)
        self.assertEqual(first["inventory"]["Weeds"], 3)
        self.assertEqual(first["inventory"]["Red blossom seed"], 0)
        self.assertEqual(first["hunter_exp"], 0)
        self.assertNotIn("Shadow vine", first["inventory"])
        self.assertEqual(first["farm_clock_minutes"], 0.06)
        second = self._answer(addon)
        self.assertEqual(second["farm_clock_minutes"], 0.12)
        self.assertEqual(second["farm_patches"][PATCH]["stage"], 0)
        self.assertEqual(second["hunter_exp"], 475)
        self.assertEqual(second["inventory"]["Shadow vine"], 1)
        self.assertEqual(second["inventory"]["Red blossom seed"], 1)
        self.assertEqual(second["inventory"]["Coins"], 100000)
        self.assertEqual(second["construction_exp"], 0)

    def test_again_never_performs_setup(self):
        addon = self._boot()
        data = copy.deepcopy(addon._state.player_data)
        after = self._answer(addon, ease=1)
        self.assertIsNone(after["farm_patches"][PATCH]["crop_id"])
        self.assertEqual(after["inventory"], data["inventory"])
        self.assertEqual(after.get("habitat_feature"), data.get("habitat_feature"))
        self.assertEqual(after["farming_exp"], 0)
        self.assertEqual(after["hunter_exp"], 0)

    def test_faster_card_uses_existing_budget_for_plant_then_catches(self):
        addon = self._boot(speed=3)
        after = self._answer(addon)
        self.assertEqual(after["farming_exp"], 52)
        self.assertEqual(after["hunter_success_count"], 2)
        self.assertEqual(after["hunter_exp"], 950)
        self.assertEqual(after["inventory"]["Shadow vine"], 2)
        self.assertEqual(after["farm_clock_minutes"], 0.18)
        self.assertEqual(after["shop_market_clock"]["answered_cards"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

    def test_house_can_build_and_catch_in_same_action_without_a_seed_or_farming_level(self):
        data = established_state()
        data.update(habitat_feature=None, farming_level=1)
        data["inventory"]["Red blossom seed"] = 0
        addon = self._boot(data)
        after = self._answer(addon)
        self.assertEqual(after["habitat_feature"], "abandoned_house")
        self.assertEqual(after["hunter_exp"], 475)
        self.assertEqual(after["farming_exp"], 0)
        self.assertEqual(after["inventory"]["Coins"], 100000)

    def test_queue_has_priority_and_clock_only_advances_once(self):
        addon = self._boot(speed=3)
        farm = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        addon._state.player_data["inventory"]["Potato seed"] = 3
        data, _, _ = farm.add_farm_queue_step_pure(addon._state.player_data, "plant", "falador_allotment_north", crop_id="potato")
        addon._state.player_data = data
        after = self._answer(addon)
        self.assertEqual(after["farm_queue"], [])
        self.assertEqual(after["farm_patches"]["falador_allotment_north"]["crop_id"], "potato")
        self.assertEqual(after["farm_patches"][PATCH]["crop_id"], "red_blossom")
        events = [row["crop_id"] for row in after["farm_event_log"] if row["event"] == "queue_step_executed"]
        self.assertEqual(events, ["potato", "red_blossom"])
        self.assertEqual(after["hunter_success_count"], 1)
        self.assertEqual(after["farm_clock_minutes"], 0.18)

    def test_background_death_precedes_upkeep_and_is_not_retroactively_cured(self):
        data = established_state(stage=1, diseased=True)
        data["farm_clock_minutes"] = 9.94
        data["inventory"]["Plant cure"] = 1
        addon = self._boot(data)
        after = self._answer(addon)
        self.assertEqual(after["farm_clock_minutes"], 10)
        self.assertIsNone(after["farm_patches"][PATCH]["crop_id"])
        self.assertEqual(after["inventory"]["Plant cure"], 1)
        self.assertEqual(after["inventory"]["Red blossom seed"], 1)
        self.assertEqual(after["hunter_exp"], 0)
        self.assertEqual(after["farming_counters"]["clears"], 1)
        self.assertEqual(after["farming_counters"]["cures"], 0)

    def test_disease_uses_field_step_and_later_remaining_budget_catches(self):
        data = established_state(diseased=True)
        data["inventory"]["Plant cure"] = 1
        addon = self._boot(data, speed=2)
        after = self._answer(addon)
        self.assertEqual(after["inventory"]["Plant cure"], 0)
        self.assertEqual(after["farming_counters"]["cures"], 1)
        self.assertEqual(after["hunter_success_count"], 1)
        self.assertEqual(after["hunter_exp"], 475)

    def test_dead_clear_and_plant_are_distinct_steps_before_a_catch(self):
        addon = self._boot(established_state(dead=True), speed=3)
        after = self._answer(addon)
        self.assertEqual(after["farming_counters"]["clears"], 1)
        self.assertEqual(after["farming_counters"]["plants"], 1)
        self.assertEqual(after["hunter_success_count"], 1)
        self.assertEqual(after["hunter_exp"], 475)
        self.assertEqual(after["farming_exp"], 52)

    def test_waiting_ends_card_and_keeps_selected_hunter(self):
        addon = self._boot(established_state(crop_id="green_blossom"), speed=8)
        habitat = importlib.import_module(f"{addon.__name__}.runtime.runtime_habitat")
        with patch.object(habitat, "apply_shadow_setup_step_pure", wraps=habitat.apply_shadow_setup_step_pure) as upkeep:
            after = self._answer(addon)
        self.assertEqual(upkeep.call_count, 1)
        self.assertEqual(after["farm_patches"][PATCH]["crop_id"], "green_blossom")
        self.assertEqual(after["hunter_exp"], 0)
        self.assertEqual(addon._state.current_skill, "Hunter")
        self.assertEqual(after["current_hunter"], TARGET)
        self.assertTrue(any("mature" in message.lower() for message in self.messages), self.messages)

    def test_blocked_never_buys_or_switches_skill_and_resumes_when_supplies_restored(self):
        data = setup_state()
        data["inventory"]["Red blossom seed"] = 0
        addon = self._boot(data, speed=4)
        shop = sys.modules[f"{addon.__name__}.logic.shop_logic"]
        with patch.object(shop, "apply_shop_buy_pure", side_effect=AssertionError("automatic purchase")), patch.object(shop, "apply_shop_service_pure", side_effect=AssertionError("automatic paid construction")):
            after = self._answer(addon)
        self.assertEqual(after["inventory"]["Coins"], 100000)
        self.assertEqual(after.get("shop_stock_state", {}), {})
        self.assertEqual(after.get("shop_events", []), [])
        self.assertEqual(after["hunter_exp"], 0)
        self.assertEqual(addon._state.current_skill, "Hunter")
        self.assertEqual(after["current_hunter"], TARGET)
        self.assertIn("missing seeds or compost", addon.hunter_target_locked_reasons_pure(after, TARGET, addon.HUNTER_DATA, addon.QUEST_UNLOCK_RULES))
        bought, result = shop.apply_shop_buy_pure(after, "papa_mambos_shop", "papa_mambos_shop:0:19922", 1)
        self.assertTrue(result["allowed"])
        addon._state.player_data = bought
        addon._review_action_multiplier = lambda: 1
        self.assertEqual(self._answer(addon)["farm_patches"][PATCH]["crop_id"], "red_blossom")

    def test_missing_paid_house_blocks_with_coins_then_manual_service_resumes_route(self):
        data = setup_state()
        data["construction_level"] = 56
        addon = self._boot(data, speed=3)
        after = self._answer(addon)
        self.assertIsNone(after.get("habitat_feature"))
        self.assertEqual(after["inventory"]["Coins"], 100000)
        self.assertEqual(after["inventory"]["Red blossom seed"], 1)
        self.assertEqual(addon._state.current_skill, "Hunter")
        shop = sys.modules[f"{addon.__name__}.logic.shop_logic"]
        bought, result = shop.apply_shop_service_pure(after, "papa_mambo_build_abandoned_house")
        self.assertTrue(result["allowed"])
        addon._state.player_data = bought
        after = self._answer(addon)
        self.assertEqual(after["inventory"]["Coins"], 43000)
        self.assertEqual(after["farming_exp"], 52)
        self.assertEqual(after["hunter_exp"], 950)
        self.assertEqual(len(after["shop_events"]), 1)

    def test_no_upkeep_for_another_target_or_skill(self):
        addon = self._boot()
        addon._state.player_data["current_hunter"] = "track_diseased_jadinko"
        addon._state.player_data["hunter_level"] = 78
        after = self._answer(addon)
        self.assertIsNone(after["farm_patches"][PATCH]["crop_id"])
        self.assertEqual(after["inventory"]["Red blossom seed"], 2)  # One ordinary Diseased secondary.
        self.assertEqual(after["farming_exp"], 0)
        self.assertNotIn("habitat_feature", after)
        after["current_hunter"] = TARGET
        addon._state.current_skill = "Fletching"
        after.update(current_fletch="arrow_shafts", fletching_level=1, fletching_exp=0)
        after["inventory"]["Logs"] = 1
        after = self._answer(addon)
        self.assertEqual(after["inventory"]["Arrow shafts"], 15)
        self.assertIsNone(after["farm_patches"][PATCH]["crop_id"])

    def test_bank_supplies_in_casual_and_custom_carried_modes(self):
        addon = self._boot()
        for advanced in (False, True):
            data = setup_state()
            data.update(current_hunter=TARGET, hunter_exp=0, hunter_success_count=0, completed_achievements=[])
            data["carried_advanced_targets"] = {TARGET: advanced}
            data["carried_layout"] = {TARGET: {"Noose wand": 1}}
            data["carried_inventory"] = {TARGET: {"Noose wand": 1}}
            addon._state.player_data = data
            after = self._answer(addon)
            self.assertEqual(after["inventory"]["Red blossom seed"], 0)
            self.assertEqual(after["inventory"]["Weeds"], 3)
            self.assertEqual(after["farming_exp"], 52)
            self.assertEqual(after["hunter_exp"], 0)
            self.assertEqual(after["carried_inventory"][TARGET], {"Noose wand": 1})

    def test_hunter_admission_precedes_spending_setup_supplies(self):
        addon = self._boot()
        for missing in ("level", "tool"):
            data = setup_state()
            data.update(current_hunter=TARGET, hunter_exp=0)
            if missing == "level":
                data["hunter_level"] = 70
            else:
                data["inventory"]["Noose wand"] = 0
            addon._state.player_data = data
            after = self._answer(addon)
            self.assertEqual(after["inventory"]["Red blossom seed"], 1)
            self.assertIsNone(after.get("habitat_feature"))
            self.assertIsNone(after["farm_patches"][PATCH]["crop_id"])

    def test_direct_handler_refuses_absent_setup_without_upkeep_or_rng(self):
        from tests.test_runtime_actions import _context
        addon = self._boot()
        data = addon._state.player_data
        before = copy.deepcopy(data)
        ctx = _context(data)
        ctx.random_random = lambda: self.fail("catch RNG before strict attraction")
        self.assertFalse(addon.runtime_actions.handle_hunter_answer(ctx))
        self.assertEqual(data, before)

    def test_whole_review_undo_restores_all_state_rng_and_reanswer_reproduces(self):
        addon = self._boot(speed=3)
        # Restore a seeded real RNG, including secondary-drop settlement.
        rng = __import__("random").Random(9)
        self.enterContext(patch.object(addon.random, "random", rng.random))
        self.enterContext(patch.object(addon.random, "getstate", rng.getstate))
        self.enterContext(patch.object(addon.random, "setstate", rng.setstate))
        before = copy.deepcopy(addon._state.player_data)
        before_rng = rng.getstate()
        first = copy.deepcopy(self._answer(addon))
        self.assertNotEqual(first, before)
        self.assertNotEqual(rng.getstate(), before_rng)
        first_rng = rng.getstate()
        self.assertEqual(len(addon._state.review_undo_stack), 1)
        self._undo(addon)
        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon._state.current_skill, "Hunter")
        self.assertEqual(rng.getstate(), before_rng)
        self.assertEqual(addon._state.review_undo_stack, [])
        replay = self._answer(addon)
        self.assertEqual(replay, first)
        self.assertEqual(rng.getstate(), first_rng)
