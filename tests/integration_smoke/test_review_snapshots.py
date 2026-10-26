from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _load_addon_as_package,
    copy,
    dataclasses,
    sys,
    types,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_answer_advances_before_save_without_copying_the_full_state(self):
        addon = _load_addon_as_package("ankiscape_answer_hot_path_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        events = []
        addon.save_player_data = lambda: events.append("save")
        original_deepcopy = addon.copy.deepcopy

        def reject_full_copy(value, *args, **kwargs):
            if value is addon._state.player_data:
                self.fail("the review-undo snapshot must not deep-copy the full player state")
            return original_deepcopy(value, *args, **kwargs)

        addon.copy.deepcopy = reject_full_copy
        self.addCleanup(setattr, addon.copy, "deepcopy", original_deepcopy)

        result = addon.on_answer_card(
            _FakeReviewer(),
            1,
            lambda _self, _ease: events.append("advance") or "answered",
        )

        self.assertEqual(result, "answered")
        self.assertEqual(events[:2], ["advance", "save"])

    def test_carried_inventory_review_undo_restores_the_exact_save(self):
        addon = _load_addon_as_package("ankiscape_carried_review_undo_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.player_data["inventory"]["Logs"] = 1
        addon._state.player_data["fletching_level"] = 1
        addon._state.player_data["fletching_exp"] = 0.0
        addon._state.player_data["current_fletch"] = "arrow_shafts"
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon._state.review_undo_stack.clear()
        initial = copy.deepcopy(addon._state.player_data)

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertTrue(addon._state.player_data["carried_primed_targets"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, initial)

    def test_level_one_player_catches_polar_kebbit_through_real_kernels(self):
        addon = _load_addon_as_package("ankiscape_polar_tracking_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data
        from ankiscape.logic.shop_logic import apply_shop_buy_pure

        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        ctx = self._runtime_context(addon, rolls=(0.0, 0.0, 0.0, 0.0))
        addon._state.player_data["current_thieving"] = "pickpocket_man"
        self.assertTrue(addon.runtime_actions.handle_thieving_answer(ctx))
        self.assertTrue(addon.runtime_actions.handle_thieving_answer(ctx))
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 4)

        addon._state.player_data, bought = apply_shop_buy_pure(
            addon._state.player_data,
            "alecks_hunter_emporium",
            "alecks_hunter_emporium:7:10150",
            1,
        )
        self.assertTrue(bought["allowed"])
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Noose wand"], 1)

        ctx = dataclasses.replace(ctx, player_data=addon._state.player_data)
        addon._state.player_data["current_hunter"] = "catch_polar_kebbit"
        self.assertTrue(addon.runtime_actions.handle_hunter_answer(ctx))

        self.assertEqual(addon._state.player_data["hunter_level"], 1)
        self.assertEqual(addon._state.player_data["hunter_exp"], 30.0)
        self.assertEqual(addon._state.player_data["inventory"]["Noose wand"], 1)
        # Shattered Heart may replace the first two ordinary outputs with Hunter
        # strange rocks; the Polar kebbit fur is third and always survives.
        self.assertEqual(addon._state.player_data["inventory"]["Polar kebbit fur"], 1)

    def test_level_seventy_player_buys_and_uses_polar_kebbit_quota_ticket(self):
        addon = _load_addon_as_package("ankiscape_polar_quota_integration")
        from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data
        from ankiscape.data.item_values import STACKABLE_ITEM_NAMES
        from ankiscape.logic.big_chinchompa_logic import (
            apply_big_chinchompa_reward_purchase_pure,
            set_hunter_private_ground_pure,
        )
        from ankiscape.logic.inventory_pure import set_carried_layout_quantity_pure

        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.player_data["hunter_level"] = 70
        addon._state.player_data["hunter_exp"] = float(EXP_TABLE[69])
        addon._state.player_data["big_chinchompa"]["competence_points"] = 15
        addon._state.player_data["inventory"]["Noose wand"] = 1

        addon._state.player_data, bought, reward = apply_big_chinchompa_reward_purchase_pure(
            addon._state.player_data,
            "polar_kebbit_ticket",
            exp_table=EXP_TABLE,
        )
        self.assertTrue(bought)
        ticket = "Polar kebbit quota ticket"
        self.assertEqual(reward["item_name"], ticket)
        self.assertEqual(addon._state.player_data["big_chinchompa"]["competence_points"], 0)
        self.assertEqual(addon._state.player_data["inventory"][ticket], 1)

        target = "catch_polar_kebbit"
        layout, configured = set_carried_layout_quantity_pure(
            {}, ticket, 1, STACKABLE_ITEM_NAMES
        )
        self.assertTrue(configured)
        addon._state.player_data["carried_layout"][target] = layout
        addon._state.player_data["carried_advanced_targets"][target] = True
        addon._state.player_data, enabled, result = set_hunter_private_ground_pure(
            addon._state.player_data,
            target,
            True,
        )
        self.assertTrue(enabled)
        self.assertEqual(result["ticket"], ticket)

        calls = {"xp": [], "activity": []}
        ctx = self._runtime_context(addon, rolls=(0.0,), calls=calls)
        addon._state.player_data["current_hunter"] = target
        self.assertTrue(
            addon.runtime_actions.run_answer_with_carried_overlay(
                ctx,
                "hunter",
                addon.runtime_actions.handle_hunter_answer,
            )
        )

        self.assertEqual(addon._state.player_data["hunter_level"], 70)
        self.assertEqual(addon._state.player_data["hunter_exp"], float(EXP_TABLE[69]) + 30.0)
        self.assertEqual(addon._state.player_data["inventory"][ticket], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Polar kebbit fur"], 1)
        self.assertEqual(
            addon._state.player_data["carried_inventory"][target]["Polar kebbit fur"], 1
        )
        self.assertNotIn(ticket, addon._state.player_data["carried_inventory"][target])
        self.assertNotIn(target, addon._state.player_data["hunter_private_ground_targets"])
        self.assertIn(ticket, calls["activity"][-1])

    def test_razor_backed_tracking_review_and_undo_use_the_real_hunter_path(self):
        addon = _load_addon_as_package("ankiscape_razor_tracking_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.player_data["inventory"]["Noose wand"] = 1
        addon._state.player_data["hunter_level"] = 49
        addon._state.player_data["hunter_exp"] = 0.0
        addon._state.player_data["current_hunter"] = "track_razor_backed_kebbit"
        addon._state.current_skill = "Hunter"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon._state.review_undo_stack.clear()
        initial = copy.deepcopy(addon._state.player_data)
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

        self.assertEqual(addon._state.player_data["inventory"]["Noose wand"], 1)
        # Shattered Heart may replace up to two ordinary outputs with the
        # target's strange rocks. Long kebbit spike is third in the sourced
        # output order, so the downstream-chain item is always retained.
        self.assertEqual(addon._state.player_data["inventory"]["Long kebbit spike"], 1)
        self.assertEqual(addon._state.player_data["hunter_exp"], 348.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_combat_carried_inventory_review_undo_restores_the_exact_save(self):
        addon = _load_addon_as_package("ankiscape_combat_carried_review_undo_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.player_data.update(
            {
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
                "current_combat_target": "chicken",
                "combat_attack_style": "aggressive",
                "combat_lifepoints": 990,
                "loot_value_threshold": 0,
            }
        )
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon._state.review_undo_stack.clear()
        initial = copy.deepcopy(addon._state.player_data)

        combat_runtime = sys.modules[
            f"{addon.__name__}.runtime.runtime_actions_combat"
        ]
        original_apply_combat_burst = combat_runtime.apply_combat_burst_pure

        def combat_burst_with_kept_loot(data, *_args, **_kwargs):
            updated = dict(data)
            inventory = dict(updated["inventory"])
            inventory["Bones"] = int(inventory.get("Bones", 0) or 0) + 1
            updated["inventory"] = inventory
            return updated, True, {
                "reason": "combat_burst",
                "target_id": "chicken",
                "display_name": "Chicken",
                "drops": {"Bones": 1},
                "xp_rewards": {},
                "kills": 1,
            }

        combat_runtime.apply_combat_burst_pure = combat_burst_with_kept_loot
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            combat_runtime.apply_combat_burst_pure = original_apply_combat_burst

        self.assertTrue(addon._state.player_data["carried_inventory"]["chicken"])
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, initial)

    def test_review_undo_stack_matches_ankis_thirty_transaction_depth(self):
        addon = _load_addon_as_package("ankiscape_review_undo_cap_integration")
        addon._state.review_undo_stack.clear()
        for value in range(32):
            addon._state.player_data = {"counter": value + 1}
            addon._remember_review_award_snapshot(
                {
                    "player_data": {"counter": value},
                    "current_skill": "None",
                    "random_state": addon.random.getstate(),
                }
            )

        self.assertEqual(addon._MAX_REVIEW_UNDO_SNAPSHOTS, 30)
        self.assertEqual(len(addon._state.review_undo_stack), 30)
        self.assertEqual(addon._state.review_undo_stack[0]["values"]["counter"], 2)

    def test_ignored_pit_reward_resolves_on_next_answer_and_review_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_pit_context_review_integration")
        addon.mw = _DummyMW(_DummyCol())
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_context_action_strip = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        shown_xp = []
        addon._show_exp = shown_xp.append
        initial = {
            "agility_level": 50,
            "agility_exp": 10.0,
            "agility_activity_state": {
                "pit_reward": {"xp": 100.0, "course": "gnome_normal"}
            },
            "review_context_preferences": {"pit_reward": "take_xp"},
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "None"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(
            _FakeReviewer(),
            1,
            lambda _self, _ease: "answered",
        )

        self.assertNotIn(
            "pit_reward",
            addon._state.player_data["agility_activity_state"],
        )
        self.assertEqual(addon._state.player_data["agility_exp"], 110.0)
        self.assertEqual(shown_xp, [100.0])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_unrelated_undo_does_not_consume_review_snapshot(self):
        addon = _load_addon_as_package("ankiscape_unrelated_undo_integration")

        addon.save_player_data = lambda: self.fail("unrelated undo should not save")
        addon._state.player_data = {
            "inventory": {"Logs": 0, "Arrow shafts": 15},
            "fletching_level": 1,
            "fletching_exp": 5.0,
            "current_fletch": "arrow_shafts",
        }
        addon._state.review_undo_stack.append(
            {
                "values": {"inventory": {"Logs": 1}, "fletching_exp": 0},
                "remove": [],
            }
        )

        changes = types.SimpleNamespace(
            operation="Set Due Date",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)
