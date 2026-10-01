"""A target switch cancels the pending bank trip of the target it replaces."""

import importlib
import sys
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic.review_strip_logic import review_bank_run_travel_view_pure
from tests.test_direct_action_undo_seam import _DummyMW, _FakeCollection, _load_addon

_UNDO = type("Changes", (), {"operation": "AnkiScape direct action"})()
_REQUESTS = (
    "skilling_bank_run_requested",
    "review_bank_run_requested_target",
    "review_bank_run_requested_handler",
)


class TestBankRunRequestTarget(unittest.TestCase):
    """Owner incident 2026-09-17: a Grand Exchange offer queued a trip for
    mackerel, the owner switched to tuna, and the trip stayed in the save to
    fire the next time mackerel ran."""

    def setUp(self):
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.addon.save_player_data = lambda: None
        self.addon.mw = _DummyMW(_FakeCollection())
        self.activity = []
        self.addon._show_activity_gain = self.activity.append

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _pending(self):
        data = self.addon._state.player_data
        return {key: data[key] for key in _REQUESTS if data.get(key)}

    def _review(self, handler_key):
        addon = self.addon
        handled = []
        addon.runtime_actions.run_answer_with_carried_overlay(
            addon._runtime_action_context(), handler_key, lambda _ctx: handled.append(True) or True
        )
        return bool(handled)

    def test_switching_fish_cancels_the_old_fishs_trip(self):
        addon = self.addon
        data = addon._state.player_data
        addon._state.current_skill = "Fishing"
        data["current_fishing"] = "catch_mackerel_cod_bass"
        self.assertTrue(addon.on_do_bank_run_now())
        self.assertTrue(addon.on_request_review_bank_run())
        self.assertEqual(
            self._pending(),
            {
                "skilling_bank_run_requested": "catch_mackerel_cod_bass",
                "review_bank_run_requested_target": "catch_mackerel_cod_bass",
            },
        )

        self.assertTrue(addon._set_value("current_fishing", "catch_tuna_swordfish"))
        self.assertEqual(self._pending(), {})
        self.assertTrue(self._review("fishing"))
        self.assertTrue(addon._set_value("current_fishing", "catch_mackerel_cod_bass"))
        self.assertFalse(review_bank_run_travel_view_pure(data, "fishing")["queued"])
        self.assertTrue(self._review("fishing"))
        self.assertEqual(self.activity, [])

        addon._on_state_did_undo(_UNDO)
        addon._on_state_did_undo(_UNDO)
        self.assertEqual(data["current_fishing"], "catch_mackerel_cod_bass")
        self.assertEqual(len(self._pending()), 2, "Undo of the switch restores its trip")

    def test_a_switch_on_another_skill_keeps_the_trip(self):
        addon = self.addon
        addon._state.current_skill = "Fishing"
        addon._state.player_data["current_fishing"] = "catch_tuna_swordfish"
        self.assertTrue(addon.on_do_bank_run_now())

        self.assertTrue(addon._set_value("current_ore", "iron_ore"))
        cooking = importlib.import_module(f"{addon.__name__}.core.menu_cooking")
        self.assertTrue(cooking.set_cooking_target(addon, "cook_anchovies"))

        self.assertEqual(self._pending(), {"skilling_bank_run_requested": "catch_tuna_swordfish"})

    def test_every_target_command_cancels_its_own_trip(self):
        addon = self.addon
        cooking = importlib.import_module(f"{addon.__name__}.core.menu_cooking")
        for skill, request, switch in (
            ("Cooking", addon.on_request_review_bank_run,
             lambda: cooking.set_cooking_target(addon, "cook_anchovies")),
            ("Utilities", addon.on_request_review_bank_run,
             lambda: addon._set_value("current_utility", "make_robust_glass")),
            ("Quests", addon.on_do_bank_run_now, lambda: addon.on_set_quest("cooks_assistant")),
        ):
            with self.subTest(skill=skill):
                addon._state.current_skill = skill
                self.assertTrue(request())
                self.assertEqual(len(self._pending()), 1)
                self.assertTrue(switch())
                self.assertEqual(self._pending(), {})


if __name__ == "__main__":
    unittest.main()
