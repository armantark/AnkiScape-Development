"""Bittercap planting accepts the spore name its producers grant.

Vinesweeper and the Master Farmer grant ``Bittercap mushroom spore`` while the
crop keeps its ``Mushroom spore`` key; both name item 5282 (Farming oldid
6565110, Exchange oldid 6561263). Every test drives the real Farming kernel or
the real review handler. Farming 53 and the Morytania flag below are fixtures,
not proof of ordinary access.
"""

import copy
import json
import sys
import types
import unittest
from dataclasses import replace
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.farming_data import FARMING_CROPS_BY_ID
from ankiscape.logic import farming_logic
from ankiscape.logic.farming_logic import (
    _consume,
    _has_items,
    _missing_items_reason,
    advance_farm_clock_pure,
    apply_farming_frontend_action_pure,
    apply_farming_review_with_queue_pure,
    default_farming_state_pure,
    execute_farm_field_step_pure,
    farming_frontend_projection_pure,
)
from tests import test_integration_smoke as runtime_fixture
from tests.item_tradeability.test_cape_tradeability import _JsonCollection


CANONICAL = "Mushroom spore"
ALTERNATE = "Bittercap mushroom spore"
PATCH = "canifis_mushroom"
MISSING = "Needs 1 Mushroom spore (0 in Bank)."
PLANT = {"kind": "plant", "patch_id": PATCH, "crop_id": "bittercap", "compost_tier": "none"}
# Six 40-minute stages at six farm minutes per answered card.
GROWTH_CARDS = 40


def _mushroom_state(stock, level=53):
    data = {
        "inventory": dict(stock),
        "farming_level": level,
        "farming_exp": 0.0,
        "unlocked_regions": ["morytania"],
    }
    data.update(default_farming_state_pure())
    return data


def _farming(data, action_id, **payload):
    return apply_farming_frontend_action_pure(data, action_id, payload)


def _planned(data, **plan):
    planned, ok, message = _farming(data, "set_plan", patch_id=PATCH, crop_id="bittercap", **plan)
    if not ok:
        raise AssertionError(message)
    return planned


def _queue_plant(data, compost_tier="none"):
    return _farming(
        data, "queue_action", patch_id=PATCH, kind="plant",
        details={"crop_id": "bittercap", "compost_tier": compost_tier},
    )


def _patch_view(data, patch_id=PATCH):
    return next(
        view
        for location in farming_frontend_projection_pure(data)["locations"]
        for view in location["patches"]
        if view["patch_id"] == patch_id
    )


def _action(view, key):
    action = view[key]
    return action["enabled"], action["locked_reason"]


class BittercapSporeKernelTest(unittest.TestCase):
    def test_each_stock_mix_matches_its_plant_preview_and_review(self):
        cases = (
            ("alternate only", {ALTERNATE: 1}, {ALTERNATE: 0}),
            ("canonical zero", {CANONICAL: 0, ALTERNATE: 1}, {CANONICAL: 0, ALTERNATE: 0}),
            ("canonical only", {CANONICAL: 1}, {CANONICAL: 0}),
            ("both", {CANONICAL: 1, ALTERNATE: 1}, {CANONICAL: 0, ALTERNATE: 1}),
            ("both depleted", {CANONICAL: 0, ALTERNATE: 0}, None),
            ("neither", {}, None),
        )
        for label, stock, after in cases:
            with self.subTest(label):
                planned = _planned(_mushroom_state(stock))
                queued, queued_ok, message = _queue_plant(planned)
                if after is None:
                    self.assertEqual(_action(_patch_view(planned), "primary_action"), (False, MISSING))
                    self.assertEqual((queued_ok, message), (False, MISSING))
                    refused, ok, info = execute_farm_field_step_pure(planned, PLANT)
                    self.assertEqual((ok, info["message"]), (False, "missing seeds or compost"))
                    self.assertEqual(refused["inventory"], stock)
                    continue
                self.assertEqual(_action(_patch_view(planned), "primary_action"), (True, ""))
                self.assertTrue(queued_ok, message)
                reviewed, consumed, info = apply_farming_review_with_queue_pure(queued)
                self.assertEqual((consumed, info["status"]), (True, "executed"))
                self.assertEqual(reviewed["inventory"], {**after, "Weeds": 3})
                self.assertEqual(reviewed["farm_patches"][PATCH]["crop_id"], "bittercap")
                self.assertEqual(reviewed["farming_exp"], 61.5)

    def test_harvest_and_replant_preview_and_queue_use_the_alternate_stack(self):
        planted, ok, _ = execute_farm_field_step_pure(_planned(_mushroom_state({CANONICAL: 1})), PLANT)
        self.assertTrue(ok)
        ready, _ = advance_farm_clock_pure(planted, GROWTH_CARDS)
        self.assertEqual(_action(_patch_view(ready), "shortcut_action"), (False, MISSING))
        ready["inventory"][ALTERNATE] = 1
        self.assertEqual(_action(_patch_view(ready), "shortcut_action"), (True, ""))

        queued, ok, message = _farming(ready, "harvest_replant", patch_id=PATCH)
        self.assertTrue(ok, message)
        harvested, _, harvest = apply_farming_review_with_queue_pure(queued)
        replanted, _, replant = apply_farming_review_with_queue_pure(harvested)

        self.assertEqual((harvest["kind"], harvest["outputs"]), ("harvest", {"Bittercap mushroom": 6}))
        self.assertEqual((replant["kind"], replant["status"]), ("plant", "executed"))
        self.assertEqual(
            {key: replanted["inventory"][key] for key in (CANONICAL, ALTERNATE, "Bittercap mushroom")},
            {CANONICAL: 0, ALTERNATE: 0, "Bittercap mushroom": 6},
        )
        self.assertEqual(replanted["farm_patches"][PATCH]["stage"], 0)

    def test_the_queued_plant_picks_its_stack_when_the_review_runs(self):
        cases = (
            ("canonical replaced by alternate", {CANONICAL: 1}, {CANONICAL: 0, ALTERNATE: 1}, {CANONICAL: 0, ALTERNATE: 0}),
            ("canonical arrives after queueing", {ALTERNATE: 1}, {CANONICAL: 1, ALTERNATE: 1}, {CANONICAL: 0, ALTERNATE: 1}),
            ("both gone", {ALTERNATE: 1}, {CANONICAL: 0, ALTERNATE: 0}, None),
        )
        for label, queued_with, at_review, after in cases:
            with self.subTest(label):
                queued, ok, message = _queue_plant(_planned(_mushroom_state(queued_with)))
                self.assertTrue(ok, message)
                queued["inventory"] = dict(at_review)
                reviewed, _, info = apply_farming_review_with_queue_pure(queued)
                if after is None:
                    self.assertEqual((info["status"], info["message"]), ("skipped", "missing seeds or compost"))
                    self.assertEqual(reviewed["inventory"], at_review)
                    self.assertEqual(reviewed["farming_counters"]["queue_steps_skipped"], 1)
                    continue
                self.assertEqual(info["status"], "executed")
                self.assertEqual(reviewed["inventory"], {**after, "Weeds": 3})

    def test_compost_and_tier_refusals_debit_neither_stack(self):
        planned = _planned(_mushroom_state({CANONICAL: 0, ALTERNATE: 1}), compost_tier="compost")
        self.assertEqual(
            _action(_patch_view(planned), "primary_action"),
            (False, "Needs 1 Compost (0 in Bank)."),
        )
        refused, ok, info = execute_farm_field_step_pure(planned, {**PLANT, "compost_tier": "compost"})
        self.assertEqual((ok, info["message"]), (False, "missing seeds or compost"))
        self.assertEqual(refused["inventory"], {CANONICAL: 0, ALTERNATE: 1})

        unknown, ok, info = execute_farm_field_step_pure(planned, {**PLANT, "compost_tier": "ultracompost"})
        self.assertEqual((ok, info["message"]), (False, "unknown compost tier"))
        self.assertEqual(unknown["inventory"], {CANONICAL: 0, ALTERNATE: 1})

        planned["inventory"]["Compost"] = 1
        planted, ok, _ = execute_farm_field_step_pure(planned, {**PLANT, "compost_tier": "compost"})
        self.assertTrue(ok)
        self.assertEqual(planted["inventory"], {CANONICAL: 0, ALTERNATE: 0, "Compost": 0, "Weeds": 3})
        self.assertEqual(planted["farm_patches"][PATCH]["lives"], 1)

    def test_fertile_soil_plants_from_the_alternate_stack_without_compost(self):
        planned = _planned(_mushroom_state({ALTERNATE: 1}), compost_tier="supercompost")
        planned["farm_plans"][PATCH]["fertile_soil_applied"] = True
        self.assertEqual(_action(_patch_view(planned), "primary_action"), (True, ""))
        planted, ok, _ = execute_farm_field_step_pure(planned, {**PLANT, "compost_tier": "supercompost"})
        self.assertTrue(ok)
        self.assertEqual(planted["inventory"], {ALTERNATE: 0, "Weeds": 3})
        self.assertEqual(planted["farm_patches"][PATCH]["compost_tier"], "supercompost")
        self.assertFalse(planted["farm_plans"][PATCH]["fertile_soil_applied"])

    def test_full_run_keeps_other_crops_on_their_own_seeds_and_refunds(self):
        state = _planned(_mushroom_state({ALTERNATE: 1, "Compost": 2}))
        state, ok, message = _farming(
            state, "set_plan", patch_id="falador_allotment_north", crop_id="potato", protection_intent=True,
        )
        self.assertTrue(ok, message)
        queued, ok, message = _farming(state, "queue_full_run")
        self.assertTrue(ok, message)
        self.assertEqual(queued["inventory"]["Compost"], 0)
        while queued["farm_queue"]:
            queued, _, _ = apply_farming_review_with_queue_pure(queued)
        self.assertEqual(queued["farm_patches"][PATCH]["crop_id"], "bittercap")
        self.assertIsNone(queued["farm_patches"]["falador_allotment_north"]["crop_id"])
        self.assertEqual(
            queued["inventory"],
            {ALTERNATE: 0, "Compost": 2, "Weeds": 3},
        )

        morchella = _mushroom_state({CANONICAL: 1, ALTERNATE: 1}, level=74)
        refused, ok, info = execute_farm_field_step_pure(morchella, {**PLANT, "crop_id": "morchella"})
        self.assertEqual((ok, info["message"]), (False, "missing seeds or compost"))
        self.assertEqual(refused["inventory"], {CANONICAL: 1, ALTERNATE: 1})
        refused, ok, info = execute_farm_field_step_pure(_mushroom_state({"Morchella mushroom spore": 1}), PLANT)
        self.assertEqual((ok, info["message"]), (False, "missing seeds or compost"))
        self.assertEqual(refused["inventory"], {"Morchella mushroom spore": 1})

    def test_alternate_stock_never_bypasses_a_patch_or_crop_gate(self):
        planted, ok, _ = execute_farm_field_step_pure(_mushroom_state({CANONICAL: 1}), PLANT)
        self.assertTrue(ok)
        planted["inventory"][ALTERNATE] = 1
        locked = _mushroom_state({ALTERNATE: 1})
        locked["unlocked_regions"] = []
        white_tree = _mushroom_state({ALTERNATE: 1})
        white_tree["quests"] = {"garden_of_tranquillity": {"completed": True}}
        blocked = {**FARMING_CROPS_BY_ID, "bittercap": replace(FARMING_CROPS_BY_ID["bittercap"], source_blocked=("stages",))}
        cases = (
            ("locked Morytania", locked, PLANT, "patch access is locked"),
            ("Farming 52", _mushroom_state({ALTERNATE: 1}, level=52), PLANT, "requires Farming level 53"),
            ("nonempty", planted, PLANT, "patch is not empty"),
            ("wrong patch", _mushroom_state({ALTERNATE: 1}), {**PLANT, "patch_id": "falador_allotment_north"},
             "crop does not fit this patch"),
            ("permanent patch", white_tree, {**PLANT, "patch_id": "varrock_white_tree"},
             "the permanent quest patch cannot be replanted"),
        )
        for label, state, step, message in cases:
            with self.subTest(label):
                refused, ok, info = execute_farm_field_step_pure(state, step)
                self.assertEqual((ok, info["message"]), (False, message))
                self.assertEqual(refused["inventory"][ALTERNATE], 1)
        level_52_options = _patch_view(_mushroom_state({ALTERNATE: 1}, level=52))["crop_options"]
        self.assertEqual(
            [(row["enabled"], row["locked_reason"]) for row in level_52_options if row["id"] == "bittercap"],
            [(False, "Requires Farming level 53.")],
        )
        with patch.object(farming_logic, "FARMING_CROPS_BY_ID", blocked):
            refused, ok, info = execute_farm_field_step_pure(_mushroom_state({ALTERNATE: 1}), PLANT)
        self.assertEqual((ok, info["message"]), (False, "Bittercap mushroom has source-blocked mechanics"))
        self.assertEqual(refused["inventory"][ALTERNATE], 1)

    def test_material_checks_neither_double_count_nor_pool_nor_mutate(self):
        both = {CANONICAL: 1, ALTERNATE: 1}
        inventory = {ALTERNATE: 1}
        snapshot = copy.deepcopy((both, inventory))
        self.assertFalse(_has_items(inventory, both))
        self.assertEqual(_missing_items_reason(inventory, both), MISSING)
        self.assertEqual((both, inventory), snapshot)

        inventory[ALTERNATE] = 2
        self.assertTrue(_has_items(inventory, both))
        _consume(inventory, both)
        self.assertEqual(inventory, {ALTERNATE: 0})
        self.assertEqual(both, {CANONICAL: 1, ALTERNATE: 1})

        pooled = {CANONICAL: 1, ALTERNATE: 1}
        self.assertFalse(_has_items(pooled, {CANONICAL: 2}))
        self.assertEqual(_missing_items_reason(pooled, {CANONICAL: 2}), "Needs 2 Mushroom spore (1 in Bank).")


class BittercapSporeRuntimeTest(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()

    def _addon(self, name, stock, collection=None):
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(collection or runtime_fixture._DummyCol())
        addon = runtime_fixture._load_addon_as_package(name)
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _exp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        # Fixtures: Farming 53 and Morytania access stand in for the earned route.
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player.update(farming_level=53, farming_exp=float(EXP_TABLE[52]), unlocked_regions=["morytania"])
        player["inventory"].update(stock)
        addon._state.player_data = player
        addon._state.current_skill = "None"
        menu = {}
        addon.ui.show_main_menu = lambda *_args, **kwargs: menu.update(kwargs)
        addon._on_main_menu()
        return addon, menu

    def _plan_and_queue(self, menu, compost_tier="none"):
        for action_id, payload in (
            ("set_plan", {"patch_id": PATCH, "crop_id": "bittercap", "compost_tier": compost_tier}),
            ("queue_action", {"patch_id": PATCH, "kind": "plant",
                              "details": {"crop_id": "bittercap", "compost_tier": compost_tier}}),
        ):
            result = menu["on_farming_action"](action_id, payload)
            self.assertTrue(result["ok"], result["message"])

    def _answer(self, addon):
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(runtime_fixture._FakeReviewer(), 3, lambda _self, _ease: "answered")

    def test_vinesweeper_spore_plants_through_real_reviews(self):
        addon, menu = self._addon("ankiscape_bittercap_vinesweeper", {})
        addon.save_player_data = lambda: None
        self.assertTrue(menu["on_set_utility"]("vinesweeper"))
        menu["on_save_skill"]("Utilities")
        self.assertTrue(menu["on_vinesweeper_command"]("enter", {})["ok"])
        # 0.79 is a correctly flagged seed in the existing operation table and
        # rolls no Farming disease.
        self.enterContext(patch.object(addon.random, "random", return_value=0.79))
        while addon._state.player_data["vinesweeper"]["points"] < 800:
            self._answer(addon)
        bought = menu["on_vinesweeper_command"]("buy_reward", {"reward_id": "bittercap_spore"})
        self.assertTrue(bought["ok"], bought)
        stock = addon._state.player_data["inventory"]
        self.assertEqual((stock[CANONICAL], stock[ALTERNATE]), (0, 1))

        self._plan_and_queue(menu)
        self._answer(addon)

        planted = addon._state.player_data
        self.assertEqual(planted["farm_patches"][PATCH]["crop_id"], "bittercap")
        self.assertEqual((planted["inventory"][CANONICAL], planted["inventory"][ALTERNATE]), (0, 0))
        self.assertEqual(planted["farming_exp"], EXP_TABLE[52] + 61.5)

    def test_review_undo_restores_both_stacks_and_the_whole_farm(self):
        addon, menu = self._addon("ankiscape_bittercap_undo", {CANONICAL: 0, ALTERNATE: 2, "Compost": 1})
        addon.save_player_data = lambda: None
        self._plan_and_queue(menu, "compost")
        before = copy.deepcopy(addon._state.player_data)
        addon.random.seed(5)

        self._answer(addon)
        answered = addon._state.player_data
        self.assertEqual(
            tuple(answered["inventory"][key] for key in (CANONICAL, ALTERNATE, "Compost")),
            (0, 1, 0),
        )
        self.assertEqual(answered["farm_patches"][PATCH]["crop_id"], "bittercap")

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before)

    def test_json_save_and_reload_keep_both_names_and_continue_the_crop(self):
        addon, menu = self._addon("ankiscape_bittercap_reload", {CANONICAL: 0, ALTERNATE: 2}, _JsonCollection())
        addon._state.player_data["bittercap_unknown_field"] = {"kept": [1, 2]}
        self._plan_and_queue(menu)
        addon.save_player_data()
        saved = json.loads(json.dumps(addon._state.player_data))

        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        loaded = addon._state.player_data
        self.assertEqual((loaded["inventory"][CANONICAL], loaded["inventory"][ALTERNATE]), (0, 2))
        for key in ("farm_plans", "farm_queue", "farm_patches", "bittercap_unknown_field"):
            with self.subTest(key=key):
                self.assertEqual(loaded[key], saved[key])

        # 0.99 rolls no Farming disease at any stage boundary.
        self.enterContext(patch.object(addon.random, "random", return_value=0.99))
        self._answer(addon)
        continued = addon._state.player_data["inventory"]
        self.assertEqual((continued[CANONICAL], continued[ALTERNATE]), (0, 1))
        for _card in range(GROWTH_CARDS):
            self._answer(addon)
        self.assertTrue(menu["on_farming_action"]("harvest_replant", {"patch_id": PATCH})["ok"])
        self._answer(addon)
        self._answer(addon)
        reloaded, _skill = addon.storage_load_player_data()
        self.assertEqual(
            tuple(reloaded["inventory"][key] for key in (CANONICAL, ALTERNATE, "Bittercap mushroom")),
            (0, 0, 6),
        )
        self.assertEqual(reloaded["farm_patches"][PATCH]["crop_id"], "bittercap")
        self.assertEqual(reloaded["farming_counters"]["plants"], 2)


if __name__ == "__main__":
    unittest.main()
