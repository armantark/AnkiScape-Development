"""The loaded review hook owns context creation and the unconditional review tail."""

import unittest
from contextlib import ExitStack
from unittest.mock import patch

from tests import test_integration_smoke as integration


class TestUnproductiveActivityCaller(unittest.TestCase):
    setUp = integration.TestIntegrationSmoke.setUp
    tearDown = integration.TestIntegrationSmoke.tearDown

    def test_failed_review_builds_activity_context_only_for_a_match_and_keeps_tail(self):
        addon = integration._load_addon_as_package("ankiscape_unproductive_selector_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = integration._DummyMW(integration._DummyCol())
        for active in (False, True):
            with self.subTest(active=active), ExitStack() as patches:
                events = []
                context = object()
                addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                addon._state.player_data["current_utility"] = addon.runtime_actions.CASTLE_WARS_ACTIVITY_ID
                addon._state.current_skill = "Activities"
                addon._state.card_turned = addon._state.answer_shown = True
                addon._state.exp_awarded = False
                patches.enter_context(patch.object(addon, "_runtime_action_context", return_value=context))
                patches.enter_context(patch.object(addon, "_resolve_ignored_review_context_for_answer", return_value=7))
                patches.enter_context(patch.object(addon, "_show_exp", side_effect=lambda xp: events.append(["xp", xp])))
                patches.enter_context(patch.object(addon, "_advance_world_events_after_review", side_effect=lambda: events.append(["world"])))
                patches.enter_context(patch.object(addon.runtime_actions, "castle_wars_view_pure", return_value={"active": active}))
                handler = patches.enter_context(patch.object(addon.runtime_actions, "handle_castle_wars_answer", return_value=False))
                for name in ("advance_shared_review_state_for_review", "advance_farming_clock_for_review"):
                    patches.enter_context(patch.object(addon.runtime_actions, name))
                for name in ("_save_player_data_if_anki_ready", "_remember_review_award_snapshot",
                             "_show_pending_bankstanding_dialog", "_show_pending_review_dialogs",
                             "_update_review_context_surface", "_refresh_bank_run_surfaces"):
                    patches.enter_context(patch.object(addon, name))
                result = addon.on_answer_card(integration._FakeReviewer(), 1, lambda _self, _ease: "answered")
                self.assertEqual(result, "answered")
                self.assertEqual(events, [["xp", 7], ["world"]])
                self.assertEqual(addon._runtime_action_context.call_count, 2 + int(active))
                self.assertEqual(handler.call_count, int(active))
                if active:
                    handler.assert_called_once_with(context, productive=False)
