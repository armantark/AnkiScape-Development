"""Real Bank dispatch and complete answer transactions, Undo and replay."""

import copy
import random
import sys
import types
import unittest
from contextlib import contextmanager
from unittest.mock import patch

from tests import test_integration_smoke as integration
from tests.treasure_trails.test_three_searches import SEARCH_ROWS, finite_draws


@contextmanager
def isolated_addon():
    modules = dict(sys.modules)
    rng_state = random.getstate()
    try:
        integration._install_runtime_fakes()
        yield integration._load_addon_as_package("ankiscape_seven_searches_review")
    finally:
        random.setstate(rng_state)
        sys.modules.clear()
        sys.modules.update(modules)


def prepare_addon(test, addon):
    """Replace presentation/Anki I/O, leaving gameplay and settlement live."""
    captured = {}
    addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
    addon.mw = integration._DummyMW(integration._DummyCol())
    addon.save_player_data = lambda: None
    addon.update_review_hud = lambda *_args: None
    addon._refresh_skill_availability = lambda: None
    addon._show_activity_gain = lambda *_args: None
    addon._show_exp = lambda *_args: None
    addon._show_pending_bankstanding_dialog = lambda: None
    addon._show_pending_review_dialogs = lambda: None
    addon.show_error_message = lambda _title, message: test.fail(message)
    storage = sys.modules[f"{addon.__name__}.core.storage_pure"]
    constants = sys.modules[f"{addon.__name__}.core.constants"]
    addon._state.player_data = storage.default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
    addon._state.player_data.update(
        inventory={"Clue scroll (easy)": 1, "Coins": 73, "Logs": 4},
        equipment={}, activity_session={"active_id": ""},
    )
    addon._state.current_skill = "Activities"
    addon._on_main_menu()
    return captured["on_treasure_trails_command"]


def start_from_real_bank(test, addon, step_id, count):
    callback = prepare_addon(test, addon)
    registry = sys.modules[f"{addon.__name__}.data.treasure_trails_data"].TREASURE_TRAILS_EASY_STEPS
    target_draw = (list(registry).index(step_id) + 0.5) / len(registry)
    rolls = (0.0 if count == 1 else 0.25,) + (target_draw,) * count
    original = addon.random.random
    try:
        addon.random.random = finite_draws(rolls)
        result = callback("start_from_bank", {"tier": "easy"})
    finally:
        addon.random.random = original
    test.assertTrue(result["ok"], result)
    test.assertEqual(addon._state.player_data["treasure_trail"]["steps"], [step_id] * count)
    test.assertEqual(addon._state.player_data["activity_session"], {"active_id": "treasure_trail"})
    test.assertEqual(addon._state.current_skill, "Activities")


def show_answer(addon):
    reviewer = integration._FakeReviewer()
    addon.on_card_did_show(None)
    addon.on_show_answer(reviewer)
    return reviewer


def answer(addon, reviewer, ease=4):
    return addon.on_answer_card(reviewer, ease, lambda _self, _ease: "answered")


def transaction_snapshot(addon):
    return (copy.deepcopy(addon._state.player_data), addon._state.current_skill,
            addon.random.getstate())


def assert_review_result(test, addon, step_id, count):
    save = addon._state.player_data
    test.assertEqual(save["treasure_trails_started"], 1)
    test.assertEqual(save["treasure_trail_retained"], {})
    if count == 2:
        test.assertEqual(save["treasure_trail"]["steps"], [step_id, step_id])
        test.assertEqual(save["treasure_trail"]["index"], 1)
        test.assertEqual(save["inventory"], {"Clue scroll (easy)": 1, "Coins": 73, "Logs": 4})
        test.assertEqual(save["treasure_trails_completed"], 0)
        test.assertEqual(save["activity_session"], {"active_id": "treasure_trail"})
        test.assertEqual(addon._state.current_skill, "Activities")
    else:
        test.assertEqual(save["treasure_trail"], {})
        test.assertEqual(save["inventory"], {"Casket (easy)": 1, "Coins": 73, "Logs": 4})
        test.assertEqual(save["treasure_trails_completed"], 1)
        test.assertEqual(save["activity_session"], {"active_id": ""})
        test.assertEqual(save["current_utility"], "bankstanding")
        test.assertEqual(addon._state.current_skill, "Utilities")
    telemetry = save["action_telemetry"]["actions"]["utility:treasure_trail"]
    test.assertEqual(telemetry["successes"], 1)


def assert_review_undo_replay(test, addon, step_id, count):
    start_from_real_bank(test, addon, step_id, count)
    reviewer = show_answer(addon)
    before = transaction_snapshot(addon)
    undo_depth = len(addon._state.review_undo_stack)
    test.assertEqual(answer(addon, reviewer), "answered")
    assert_review_result(test, addon, step_id, count)
    after = transaction_snapshot(addon)
    test.assertEqual(
        {key: value for key, value in after[0].items() if key.endswith("_exp")},
        {key: value for key, value in before[0].items() if key.endswith("_exp")},
    )
    test.assertEqual(len(addon._state.review_undo_stack), undo_depth + 1)
    changes = types.SimpleNamespace(
        operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True)
    )
    addon._on_state_did_undo(changes)
    test.assertEqual(transaction_snapshot(addon), before)
    test.assertEqual(len(addon._state.review_undo_stack), undo_depth)
    test.assertEqual(answer(addon, show_answer(addon)), "answered")
    test.assertEqual(transaction_snapshot(addon), after)
    test.assertEqual(len(addon._state.review_undo_stack), undo_depth + 1)
    assert_review_result(test, addon, step_id, count)


class SavedBankCollection(integration._DummyCol):
    """Config values cross Anki's serialization boundary without live aliases."""

    accepts_undo = True

    def get_config(self, key, default=None):
        return copy.deepcopy(super().get_config(key, default))

    def set_config(self, key, value):
        super().set_config(key, copy.deepcopy(value))

    def add_custom_undo_entry(self, name):
        if not self.accepts_undo:
            raise RuntimeError("collection refused the undo entry")
        return super().add_custom_undo_entry(name)


def bank_start(test, addon, callback, retained=False):
    registry = sys.modules[f"{addon.__name__}.data.treasure_trails_data"].TREASURE_TRAILS_EASY_STEPS
    draws = finite_draws((0.25,) + tuple(
        (list(registry).index(step_id) + 0.5) / len(registry)
        for step_id in ("simple_hemenster_crate", "simple_port_khazard_cart_crate")
    ))
    original = addon.random.random

    def draw():
        if retained:
            test.fail("Retained Bank start must not draw again")
        original()  # Exercise real RNG rollback while selecting the exact searches.
        return draws()

    with patch.object(addon.random, "random", side_effect=draw):
        return callback("start_from_bank", {"tier": "easy"})


def prepare_saved_bank(test, addon, selected_skill, retained=False):
    save_player_data = addon.save_player_data
    show_pending_bankstanding = addon._show_pending_bankstanding_dialog
    callback = prepare_addon(test, addon)
    addon.mw.col = SavedBankCollection()
    sys.modules[f"{addon.__name__}.core.storage"].mw = addon.mw
    addon.save_player_data = save_player_data
    addon._show_pending_bankstanding_dialog = show_pending_bankstanding
    addon.ui.show_bankstanding_dialog = lambda *_args: None
    if retained:
        test.assertTrue(bank_start(test, addon, callback)["ok"])
        generated = copy.deepcopy(addon._state.player_data["treasure_trail"])
        test.assertTrue(callback("abandon", {})["ok"])
        addon._state.player_data, addon._state.current_skill = addon.storage_load_player_data()
        test.assertEqual(addon._state.player_data["treasure_trail"], {})
        test.assertEqual(addon._state.player_data["treasure_trail_retained"], generated)
    addon._state.current_skill = selected_skill
    addon.save_player_data()
    return callback


def bank_snapshot(addon):
    return (transaction_snapshot(addon), copy.deepcopy(addon.mw.col._store),
            copy.deepcopy(addon._state.direct_action_undo_stack),
            copy.deepcopy(addon._state.review_undo_stack))


def assert_bank_start_undo_replay(test, addon, callback, retained):
    before = bank_snapshot(addon)
    test.assertTrue(bank_start(test, addon, callback, retained)["ok"])
    save = addon._state.player_data
    test.assertEqual(save["treasure_trail"]["steps"],
                     ["simple_hemenster_crate", "simple_port_khazard_cart_crate"])
    test.assertEqual(save["treasure_trail"]["index"], 0)
    test.assertEqual(save["treasure_trails_started"], 1)
    test.assertEqual(save["treasure_trail_retained"], {})
    test.assertEqual(save["activity_session"], {"active_id": "treasure_trail"})
    test.assertEqual(addon._state.current_skill, "Activities")
    test.assertEqual(addon.mw.col.get_config("ankiscape_current_skill"), "Activities")
    test.assertEqual(addon.mw.col.get_config("ankiscape_player_data"), save)
    test.assertEqual(len(addon._state.direct_action_undo_stack), len(before[2]) + 1)
    after = bank_snapshot(addon)
    addon._on_state_did_undo(types.SimpleNamespace(operation="AnkiScape direct action"))
    test.assertEqual(bank_snapshot(addon), before)
    test.assertTrue(bank_start(test, addon, callback, retained)["ok"])
    test.assertEqual(bank_snapshot(addon), after)


def assert_good_review_undo_replay(test, addon, index):
    reviewer = show_answer(addon)
    before = bank_snapshot(addon)
    test.assertEqual(answer(addon, reviewer, ease=3), "answered")
    save = addon._state.player_data
    test.assertEqual(save["treasure_trails_completed"], index - 1)
    test.assertEqual(save["inventory"].get("Clue scroll (easy)", 0), 2 - index)
    test.assertEqual(save["inventory"].get("Casket (easy)", 0), index - 1)
    if index == 1:
        test.assertEqual(save["treasure_trail"]["index"], 1)
    else:
        test.assertEqual(save["treasure_trail"], {})
        test.assertEqual(save["activity_session"], {"active_id": ""})
    test.assertEqual(addon.mw.col.get_config("ankiscape_player_data"), save)
    test.assertEqual(len(addon._state.review_undo_stack), len(before[3]) + 1)
    after = bank_snapshot(addon)
    addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
    test.assertEqual(bank_snapshot(addon), before)
    test.assertEqual(answer(addon, show_answer(addon), ease=3), "answered")
    test.assertEqual(bank_snapshot(addon), after)


class SevenSearchReviewTest(unittest.TestCase):
    def test_bank_start_selects_activities_with_complete_undo_and_good_replay(self):
        for selected_skill in ("None", "Mining"):
            for retained in (False, True):
                with self.subTest(skill=selected_skill, retained=retained), isolated_addon() as addon:
                    callback = prepare_saved_bank(self, addon, selected_skill, retained)
                    assert_bank_start_undo_replay(self, addon, callback, retained)
                    for index in (1, 2):
                        assert_good_review_undo_replay(self, addon, index)

    def test_refused_bank_start_preserves_full_live_saved_rng_and_undo_state(self):
        for selected_skill in ("None", "Mining"):
            for refusal in ("missing_scroll", "undo_unavailable"):
                with self.subTest(skill=selected_skill, refusal=refusal), isolated_addon() as addon:
                    callback = prepare_saved_bank(self, addon, selected_skill)
                    if refusal == "missing_scroll":
                        addon._state.player_data["inventory"].pop("Clue scroll (easy)")
                    else:
                        addon.mw.col.accepts_undo = False
                    addon.save_player_data()
                    before = bank_snapshot(addon)
                    entries = list(addon.mw.col.custom_undo_entries)
                    result = bank_start(self, addon, callback)
                    self.assertFalse(result["ok"], result)
                    self.assertEqual(bank_snapshot(addon), before)
                    self.assertEqual(addon.mw.col.custom_undo_entries, entries)

    def test_each_search_review_undo_replay(self):
        for step_id, _text in SEARCH_ROWS:
            with self.subTest(step_id=step_id), isolated_addon() as addon:
                assert_review_undo_replay(self, addon, step_id, 2)

    def test_each_search_final_review_undo_replay(self):
        for step_id, _text in SEARCH_ROWS:
            with self.subTest(step_id=step_id), isolated_addon() as addon:
                assert_review_undo_replay(self, addon, step_id, 1)

    def test_failed_answer_does_not_resolve_new_searches(self):
        for step_id, _text in SEARCH_ROWS:
            with self.subTest(step_id=step_id), isolated_addon() as addon:
                start_from_real_bank(self, addon, step_id, 2)
                before = copy.deepcopy(addon._state.player_data)
                self.assertEqual(answer(addon, show_answer(addon), ease=1), "answered")
                after = addon._state.player_data
                for key in ("treasure_trail", "treasure_trail_retained", "inventory",
                            "treasure_trails_completed", "treasure_trails_started",
                            "treasure_trails_caskets_opened", "activity_session"):
                    self.assertEqual(after[key], before[key], key)
