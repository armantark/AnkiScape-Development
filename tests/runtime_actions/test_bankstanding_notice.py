import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.runtime import runtime_actions
from ankiscape.runtime import runtime_actions_combat
from ankiscape.runtime import runtime_actions_utility
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _install_runtime_fakes,
    _load_addon_as_package,
)
from tests.test_runtime_actions import _bankstanding_context, _context


class BankstandingNoticeTest(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_runtime_popup_suppresses_the_redundant_bankstanding_modal(self):
        addon = _load_addon_as_package("ankiscape_bankstanding_popup_owner")
        addon.mw = _DummyMW(_DummyCol())
        addon.update_review_event_log_drawer = lambda _data: None
        addon.update_review_hud = lambda *_args: None
        addon.ui.update_menu_visibility = lambda *_args: None
        popups = []
        errors = []
        addon.ui.show_bankstanding_dialog = popups.append
        addon.show_error_message = lambda title, message: errors.append(
            (title, message)
        )
        addon._state.current_skill = "Activities"
        addon._state.player_data = {
            "current_utility": "temple_trekking",
            "review_event_log": [],
        }

        runtime_ctx = addon._runtime_action_context()
        runtime_ctx.deactivate_current_skill()
        runtime_ctx.show_error_message(
            "Temple Trekking unavailable",
            "Start or resume a trek before training.",
        )
        addon._show_pending_bankstanding_dialog()

        self.assertEqual(
            errors,
            [("Temple Trekking unavailable", "Start or resume a trek before training.")],
        )
        self.assertEqual(popups, [])
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)
        self.assertIn(
            "Start or resume a trek before training.",
            addon._state.player_data["review_event_log"][0]["text"],
        )

    def test_popup_ownership_resets_after_a_later_runtime_gain(self):
        addon = _load_addon_as_package("ankiscape_bankstanding_popup_reset")
        addon.mw = _DummyMW(_DummyCol())
        addon.update_review_hud = lambda *_args: None
        addon.ui.update_menu_visibility = lambda *_args: None
        popups = []
        errors = []
        gains = []
        addon.ui.show_bankstanding_dialog = popups.append
        addon.show_error_message = lambda title, message: errors.append(
            (title, message)
        )
        addon._show_activity_gain = gains.append
        addon._state.current_skill = "Crafting"
        addon._state.player_data = {
            "current_utility": "gather_wool",
            "review_event_log": [],
        }

        runtime_ctx = addon._runtime_action_context()
        runtime_ctx.show_error_message("Temporary refusal", "Try the next tick.")
        runtime_ctx.show_activity_gain("The next tick progressed.")
        runtime_ctx.switch_to_bankstanding("The action then ended.")
        addon._show_pending_bankstanding_dialog()

        self.assertEqual(errors, [("Temporary refusal", "Try the next tick.")])
        self.assertEqual(gains, ["The next tick progressed."])
        self.assertEqual(popups, ["The action then ended."])
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)

    def test_invalid_target_keeps_one_bankstanding_modal_and_event(self):
        addon = _load_addon_as_package("ankiscape_invalid_utility_target")
        popups = []
        addon.ui.show_bankstanding_dialog = popups.append
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.current_skill = "Utilities"
        addon._state.player_data = {
            "current_utility": "removed_target",
            "review_event_log": [],
        }

        addon.on_utility_answer()
        addon._show_pending_bankstanding_dialog()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(popups, ["Removed Target could not continue."])
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)

    def test_activity_end_keeps_one_reasoned_modal_and_event(self):
        addon = _load_addon_as_package("ankiscape_activity_end_notice")
        addon.mw = _DummyMW(_DummyCol())
        addon.update_review_hud = lambda *_args: None
        addon.ui.update_menu_visibility = lambda *_args: None
        popups = []
        addon.ui.show_bankstanding_dialog = popups.append
        addon._state.current_skill = "Activities"
        addon._state.player_data = {
            "current_utility": "conquest",
            "review_event_log": [],
        }
        reason = addon._activity_session_end_reason({"active_id": "conquest"})

        self.assertTrue(addon._switch_to_bankstanding(reason))
        addon._show_pending_bankstanding_dialog()

        self.assertEqual(popups, ["Conquest ended."])
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)

    def test_empty_combat_failure_reasons_use_the_non_material_popup(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "equipment": {},
            "current_combat_target": "cow",
            "combat_lifepoints": 990,
            "constitution_level": 99,
            "completed_achievements": [],
        }
        result = (dict(player_data), False, {})

        with patch.object(
            runtime_actions_combat,
            "apply_combat_burst_pure",
            return_value=result,
        ):
            self.assertFalse(
                runtime_actions.handle_combat_answer(
                    _bankstanding_context(player_data, calls)
                )
            )

        self.assertEqual(calls.get("bankstanding", 0), 0)
        self.assertTrue(calls["deactivated"])
        self.assertEqual(
            calls["errors"],
            [
                (
                    "Combat unavailable",
                    "Combat has been switched off because the selected target is unavailable.",
                )
            ],
        )

    def test_magic_material_reason_reaches_the_switch_seam_without_popup(self):
        for cadence_live in (False, True):
            with self.subTest(cadence_live=cadence_live):
                calls = {"xp": [], "saves": 0, "errors": []}
                player_data = {
                    "inventory": {"Rune platebody": 1},
                    "equipment": {},
                    "magic_level": 99,
                    "current_magic": "high_alchemy",
                    "magic_alchemy_item": "Rune platebody",
                }
                ctx = _bankstanding_context(player_data, calls)
                ctx.cadence_live_enabled = cadence_live

                self.assertFalse(runtime_actions.handle_magic_answer(ctx))

                self.assertEqual(player_data["current_utility"], "bankstanding")
                self.assertEqual(calls.get("bankstanding", 0), 1)
                self.assertEqual(calls["errors"], [])
                self.assertIn("Nature rune", calls["bankstanding_reasons"][0])

    def test_compost_failure_reason_reaches_the_switch_seam_without_popup(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "current_utility": "use_compost_potion",
            "inventory": {"Compost": 1, "Compost potion (4)": 1},
            "completed_achievements": [],
        }
        failure = (
            dict(player_data["inventory"]),
            False,
            {"reason": "A Compost potion dose is required."},
        )

        with patch.object(
            runtime_actions_utility,
            "apply_compost_potion_pure",
            return_value=failure,
        ):
            self.assertFalse(
                runtime_actions.handle_utility_answer(
                    _bankstanding_context(player_data, calls)
                )
            )

        self.assertEqual(player_data["current_utility"], "bankstanding")
        self.assertEqual(calls.get("bankstanding", 0), 1)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(
            calls["bankstanding_reasons"],
            ["A Compost potion dose is required."],
        )

    def test_material_reason_reaches_deactivation_when_switch_seam_is_absent(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "fishing_level": 38,
            "current_fishing": "catch_cave_eel",
            "completed_achievements": [],
        }

        self.assertFalse(
            runtime_actions.handle_fishing_answer(_context(player_data, calls))
        )

        self.assertIn("Fishing bait", calls["deactivation_reasons"][0])

    def test_fishing_material_reason_reaches_the_switch_seam_without_popup(self):
        calls = {"xp": [], "saves": 0, "errors": []}
        player_data = {
            "inventory": {},
            "fishing_level": 38,
            "current_fishing": "catch_cave_eel",
            "completed_achievements": [],
        }

        self.assertFalse(
            runtime_actions.handle_fishing_answer(
                _bankstanding_context(player_data, calls)
            )
        )

        self.assertEqual(player_data["current_utility"], "bankstanding")
        self.assertEqual(calls.get("bankstanding", 0), 1)
        self.assertEqual(calls["errors"], [])
        self.assertIn("Fishing bait", calls["bankstanding_reasons"][0])


if __name__ == "__main__":
    unittest.main()
