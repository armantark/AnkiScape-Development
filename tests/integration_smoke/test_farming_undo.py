from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _load_addon_as_package,
    copy,
    sys,
    types,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_cure_plant_runtime_cast_and_answer_undo_are_atomic(self):
        addon = _load_addon_as_package("ankiscape_cure_plant_undo_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda xp: calls["xp"].append(xp)
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {
                "Astral rune": 1,
                "Earth rune": 8,
                "Rake": 1,
                "Seed dibber": 1,
                "Potato seed": 3,
            },
            "magic_level": 99,
            "magic_exp": 0.0,
            "current_magic": "cure_plant",
            "quests": {"lunar_diplomacy": {"completed": True}},
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(ok)
        state["farm_patches"]["falador_allotment_north"]["diseased"] = True
        state["farming_spell_patch"] = "falador_allotment_north"
        before = copy.deepcopy(state)
        addon._state.player_data = state
        addon._state.current_skill = "Magic"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertFalse(addon._state.player_data["farm_patches"]["falador_allotment_north"]["diseased"])
        self.assertEqual(addon._state.player_data["inventory"]["Astral rune"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Earth rune"], 0)
        self.assertEqual(addon._state.player_data["magic_exp"], 60.0)
        self.assertEqual(calls["save"], 1)
        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before)

    def test_livid_remote_farm_cast_cures_all_patches_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_livid_remote_farm_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        calls = {"save": 0, "gains": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {
                "Astral rune": 2,
                "Earth rune": 2,
                "Nature rune": 3,
            },
            "magic_level": 99,
            "magic_exp": 0.0,
            "current_magic": "remote_farm",
            "quests": {"lunar_diplomacy": {"completed": True}},
            "livid_farm": {"unlocked_spells": ["remote_farm"]},
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        for patch_id in ("falador_allotment_north", "falador_allotment_south"):
            state["farm_patches"][patch_id].update(
                {
                    "crop_id": "potato",
                    "last_crop_id": "potato",
                    "diseased": True,
                }
            )
        before = copy.deepcopy(state)
        addon._state.player_data = state
        addon._state.current_skill = "Magic"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertFalse(
            addon._state.player_data["farm_patches"]["falador_allotment_north"][
                "diseased"
            ]
        )
        self.assertFalse(
            addon._state.player_data["farm_patches"]["falador_allotment_south"][
                "diseased"
            ]
        )
        self.assertEqual(addon._state.player_data["magic_exp"], 79.0)
        self.assertEqual(
            calls["gains"],
            ["Remote Farm checked 2 active patches and cured 2."],
        )
        self.assertEqual(calls["save"], 1)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )
        self.assertEqual(addon._state.player_data, before)

    def test_livid_consumer_block_message_is_player_facing(self):
        addon = _load_addon_as_package("ankiscape_livid_block_message_integration")
        calls = {"errors": []}
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = (
            lambda title, message: calls["errors"].append((title, message))
        )
        addon._state.player_data = {
            "inventory": {
                "Astral rune": 3,
                "Blood rune": 3,
                "Body rune": 10,
            },
            "magic_level": 99,
            "current_magic": "disruption_shield",
            "quests": {"lunar_diplomacy": {"completed": True}},
            "livid_farm": {"unlocked_spells": ["disruption_shield"]},
        }
        addon._state.current_skill = "Magic"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(
            calls["errors"],
            [
                (
                    "Magic target unavailable",
                    "Disruption Shield is unavailable: Requires PvP combat. "
                    "Magic has been switched off.",
                )
            ],
        )

    def test_queued_farming_dig_up_preempts_one_review_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_farming_dig_up_undo_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {
                "Rake": 1,
                "Seed dibber": 1,
                "Spade": 1,
                "Redberry seed": 1,
            },
            "farming_level": 99,
            "farming_exp": 0.0,
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "agility_level": 99,
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "champions_bush", "crop_id": "redberry"},
        )
        self.assertTrue(ok)
        state, _ = farming_logic.advance_farm_clock_pure(state, 102, lambda: 1.0)
        state, step_id, _ = farming_logic.add_farm_queue_step_pure(
            state, "dig_up", "champions_bush"
        )
        self.assertIsNotNone(step_id)
        before = copy.deepcopy(state)
        addon._state.player_data = state
        addon._state.current_skill = "Mining"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertIsNone(addon._state.player_data["farm_patches"]["champions_bush"]["crop_id"])
        self.assertEqual(addon._state.player_data["farming_counters"]["dig_ups"], 1)
        self.assertEqual(addon._state.player_data["farm_queue"], [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before)

    def test_queued_white_tree_harvest_preempts_one_review_and_undoes_atomically(self):
        addon = _load_addon_as_package("ankiscape_white_tree_undo_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {},
            "farming_level": 25,
            "farming_exp": 0.0,
            "quests": {"garden_of_tranquillity": {"completed": True}},
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state, step_ids = farming_logic.queue_full_run_pure(state)
        self.assertEqual(len(step_ids), 1)
        before = copy.deepcopy(state)
        addon._state.player_data = state
        addon._state.current_skill = "Mining"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["White tree fruit"], 4)
        self.assertEqual(addon._state.player_data["farming_exp"], 48.0)
        self.assertEqual(
            addon._state.player_data["farm_patches"]["varrock_white_tree"]["produce_count"],
            0,
        )
        self.assertEqual(addon._state.player_data["farm_queue"], [])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before)

    def test_jade_branch_from_again_waits_for_a_successful_review_and_undoes(self):
        addon = _load_addon_as_package("ankiscape_jade_vine_queue_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {"Secateurs": 1},
            "farming_level": 99,
            "farming_exp": 0.0,
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "agility_level": 99,
            "slayer_level": 99,
            "slayer_exp": 0.0,
            "quests": {"back_to_my_roots": {"completed": True}},
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        record = state["farm_patches"]["handelmort_jade_vine"]
        record.update({
            "crop_id": "jade_vine",
            "last_crop_id": "jade_vine",
            "stage": 6,
            "health_checked": True,
            "jade_state": "prunable",
            "next_regrowth_at": 0.06,
        })
        addon._state.player_data = state
        addon._state.current_skill = "Mining"

        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "again")
        self.assertEqual(
            addon._state.player_data["farm_patches"]["handelmort_jade_vine"]["produce_count"],
            1,
        )
        self.assertEqual(
            [step["kind"] for step in addon._state.player_data["farm_queue"]],
            ["harvest"],
        )

        before_prune = copy.deepcopy(addon._state.player_data)
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(
            addon._state.player_data["farm_patches"]["handelmort_jade_vine"]["produce_count"],
            0,
        )
        self.assertEqual(addon._state.player_data["farm_queue"], [])
        self.assertEqual(addon._state.player_data["inventory"].get("Jade vine branch", 0), 0)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, before_prune)

    def test_jade_seed_claim_is_a_direct_undoable_farming_action(self):
        addon = _load_addon_as_package(
            "ankiscape_jade_vine_direct_action_integration"
        )
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        col = _DummyCol()
        addon.mw = _DummyMW(col)
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._state.current_skill = "Farming"
        state = {
            "inventory": {},
            "farming_level": 53,
            "farming_exp": 0.0,
            "smithing_level": 1,
            "quests": {"back_to_my_roots": {"completed": True}},
        }
        state.update(addon.logic.farming_logic.default_farming_state_pure())
        addon._state.player_data = copy.deepcopy(state)

        addon._on_main_menu(initial_skill="Farming")
        claimed = captured["on_farming_action"](
            "claim_jade_vine_seed",
            {},
        )

        self.assertTrue(claimed["ok"])
        self.assertEqual(addon._state.player_data["inventory"]["Jade vine seed"], 1)
        self.assertEqual(col.custom_undo_entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._state.direct_action_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(operation="AnkiScape direct action")
        )
        self.assertEqual(addon._state.player_data, state)
        self.assertEqual(addon._state.direct_action_undo_stack, [])

    def test_willow_full_run_health_checks_then_prunes_on_successive_reviews(self):
        addon = _load_addon_as_package("ankiscape_willow_full_run_integration")
        farming_logic = sys.modules[f"{addon.__name__}.logic.farming_logic"]
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda _xp: None
        addon._show_activity_gain = lambda _message: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        state = {
            "inventory": {
                "Rake": 1,
                "Spade": 1,
                "Secateurs": 1,
                "Willow sapling": 2,
            },
            "farming_level": 99,
            "farming_exp": 0.0,
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "agility_level": 99,
            "completed_achievements": [],
        }
        state.update(farming_logic.default_farming_state_pure())
        state["shop_market_clock"] = {"answered_cards": 238, "market_tick": 239}
        state["world_clock"] = {"day": 0, "day_start_card": 0, "day_length": 240, "in_day_ticks": 143494}
        state, ok, _ = farming_logic.set_farm_plan_pure(
            state,
            "lumbridge_tree",
            "willow",
        )
        self.assertTrue(ok)
        state, ok, _ = farming_logic.execute_farm_field_step_pure(
            state,
            {
                "kind": "plant",
                "patch_id": "lumbridge_tree",
                "crop_id": "willow",
            },
        )
        self.assertTrue(ok)
        state, _ = farming_logic.advance_farm_clock_pure(
            state,
            240,
            lambda: 1.0,
        )
        state, step_ids = farming_logic.queue_full_run_pure(state)
        self.assertEqual(len(step_ids), 5)
        addon._state.player_data = state
        addon._state.current_skill = "Mining"

        for _ in range(2):
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )

        patch = addon._state.player_data["farm_patches"]["lumbridge_tree"]
        self.assertTrue(patch["health_checked"])
        self.assertEqual(patch["produce_count"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Willow branch"], 1)
        self.assertEqual(
            [step["kind"] for step in addon._state.player_data["farm_queue"]],
            ["chop", "clear", "plant"],
        )
        self.assertEqual(addon._state.player_data["farming_exp"], 1481.3)
