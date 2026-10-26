from tests.test_integration_smoke import _DummyCol, _DummyMW, _load_addon_as_package, copy, types
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_review_undo_rolls_back_the_event_log_atomically(self):
        addon = _load_addon_as_package("ankiscape_event_log_undo")
        addon.save_player_data = lambda: None
        addon._state.player_data = {
            "shop_market_clock": {"answered_cards": 12, "market_tick": 12},
            "review_event_log": [],
        }
        addon._state.current_skill = "Mining"
        addon._state.review_undo_stack.clear()
        before = addon._capture_player_data_snapshot()

        addon._record_review_event("activity", "+1 Iron ore", persist=False)
        addon._remember_review_award_snapshot(before)
        self.assertEqual(len(addon._state.player_data["review_event_log"]), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data["review_event_log"], [])

    def test_conquest_review_undo_restores_the_exact_pre_exchange_match(self):
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data
        from ankiscape.logic.conquest_logic import (
            apply_conquest_review_pure,
            enter_conquest_pure,
        )

        addon = _load_addon_as_package("ankiscape_conquest_review_undo")
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
            "ranged_level",
            "magic_level",
            "prayer_level",
        ):
            player[key] = 40
        player["activity_session"] = {"active_id": ""}
        player["combat_encounter"] = {}
        player, ok, info = enter_conquest_pure(player, {}, lambda: 0.25)
        self.assertTrue(ok, info)
        addon._state.player_data = player
        addon._state.current_skill = "Activities"
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._state.review_undo_stack.clear()
        exact_before = copy.deepcopy(addon._state.player_data)
        snapshot = addon._capture_player_data_snapshot()

        advanced, ok, result = apply_conquest_review_pure(
            addon._state.player_data, lambda: 0.5
        )
        self.assertTrue(ok, result)
        addon._state.player_data.clear()
        addon._state.player_data.update(advanced)
        self.assertNotEqual(addon._state.player_data["conquest"], exact_before["conquest"])
        addon._remember_review_award_snapshot(snapshot)
        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, exact_before)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_direct_leave_command_lands_on_bankstanding_and_undoes_atomically(self):
        # Owner clause 2: a direct command that ends an active activity session
        # must leave the surface on Bankstanding (never "None"), and the
        # transaction undo must restore the former activity whole.
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data
        from ankiscape.logic.conquest_logic import (
            apply_conquest_command_pure,
            enter_conquest_pure,
        )

        addon = _load_addon_as_package("ankiscape_session_clear_bankstanding")
        addon.mw = _DummyMW(_DummyCol())
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
            "ranged_level",
            "magic_level",
            "prayer_level",
        ):
            player[key] = 40
        player["activity_session"] = {"active_id": ""}
        player["combat_encounter"] = {}
        player, ok, info = enter_conquest_pure(player, {}, lambda: 0.25)
        self.assertTrue(ok, info)
        addon._state.player_data = player
        addon._state.current_skill = "Activities"
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda *_args: None
        addon._state.direct_action_undo_stack.clear()

        self.assertTrue(
            addon.commit_direct_action(
                lambda current: apply_conquest_command_pure(
                    current, "resign", {}, lambda: 0.25
                )[:2]
            )
        )

        self.assertEqual(addon._state.player_data["activity_session"], {"active_id": ""})
        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")

        addon._restore_direct_action_snapshot(addon._state.direct_action_undo_stack.pop())

        self.assertEqual(addon._state.player_data["activity_session"], {"active_id": "conquest"})
        self.assertEqual(addon._state.player_data["current_utility"], "conquest")
        self.assertEqual(addon._state.current_skill, "Activities")
