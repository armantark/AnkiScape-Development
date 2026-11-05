from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _load_addon_as_package,
    copy,
    types,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_construction_review_reward_and_consumed_materials_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_construction_undo_integration")
        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Plank": 2, "Rune nails": 2},
            "construction_level": 1, "construction_exp": 0,
            "current_construction": "crude_wooden_chair",
            "house_owned": True, "house_rooms_bought": {"parlour": True, "garden": True},
            "house_servant": "", "house_built_flags": {}, "quests": {},
            "completed_achievements": [],
        }
        addon._state.current_skill = "Construction"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_random = addon.random.random
        addon.random.random = lambda: 0.999999
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random
        self.assertEqual(addon._state.player_data["inventory"]["Plank"], 0)
        self.assertEqual(addon._state.player_data["construction_exp"], 66.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data["inventory"], {"Plank": 2, "Rune nails": 2})
        self.assertEqual(addon._state.player_data["construction_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_undo_after_dragon_sq_shield_assembly_restores_both_halves(self):
        addon = _load_addon_as_package("ankiscape_dragon_sq_shield_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Shield left half": 1, "Shield right half": 1},
            "smithing_level": 60,
            "smithing_exp": 0,
            "current_smith": "repair_dragon_sq_shield",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Smithing"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"], {"Shield left half": 0, "Shield right half": 0, "Dragon sq shield": 1})
        self.assertAlmostEqual(addon._state.player_data["smithing_exp"], 70.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data["inventory"], {"Shield left half": 1, "Shield right half": 1})
        self.assertAlmostEqual(addon._state.player_data["smithing_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [70.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_coal_bag_smithing_consumption_rolls_back_on_review_undo(self):
        addon = _load_addon_as_package(
            "ankiscape_coal_bag_smithing_undo_integration"
        )

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "save",
            calls["save"] + 1,
        )
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Iron ore": 1},
            "smithing_level": 30,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "smelt_steel_bar",
            "completed_achievements": [],
            "dungeoneering": {
                "coal_bag_owned": True,
                "coal_bag_coal": 2,
            },
        }
        addon._state.current_skill = "Smithing"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        before = copy.deepcopy(addon._state.player_data)
        self.assertTrue(addon.can_smith_any())

        addon.on_answer_card(
            _FakeReviewer(),
            4,
            lambda _self, _ease: "answered",
        )

        self.assertEqual(addon._state.player_data["inventory"]["Iron ore"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Steel bar"], 1)
        self.assertNotIn("Coal", addon._state.player_data["inventory"])
        self.assertEqual(
            addon._state.player_data["dungeoneering"]["coal_bag_coal"],
            0,
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [17.5])
        self.assertGreaterEqual(calls["save"], 2)

    def test_undo_after_coloured_feather_fletching_restores_the_same_colour(self):
        addon = _load_addon_as_package("ankiscape_coloured_feather_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Arrow shafts": 15, "Yellow feather": 15},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "headless_arrows",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Yellow feather"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Headless arrows"], 15)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data["inventory"], {"Arrow shafts": 15, "Yellow feather": 15})
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 0)
        self.assertEqual(calls["xp"], [15.0])

    def test_undo_after_long_kebbit_bolts_restores_spike_and_keeps_chisel(self):
        addon = _load_addon_as_package("ankiscape_long_kebbit_bolt_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Long kebbit spike": 1, "Chisel": 1},
            "fletching_level": 42,
            "fletching_exp": 0,
            "current_fletch": "fletch_long_kebbit_bolts",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Long kebbit spike": 0, "Chisel": 1, "Long kebbit bolts": 6},
        )
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 7.98)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(
            addon._state.player_data["inventory"],
            {"Long kebbit spike": 1, "Chisel": 1},
        )
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 0)
        self.assertEqual(calls["xp"], [7.98])

    def test_successful_noncombat_review_advances_charge_and_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_charge_clock_integration")

        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 2}))
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Logs": 2},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
            "magic_charge_active": True,
            "magic_charge_ticks_remaining": 12,  # one speed-2 card
        }
        initial_state = copy.deepcopy(addon._state.player_data)
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertFalse(addon._state.player_data["magic_charge_active"])
        self.assertEqual(addon._state.player_data["magic_charge_ticks_remaining"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 30)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))

        self.assertEqual(addon._state.player_data, initial_state)

    def test_successful_noncombat_review_applies_one_safe_combat_recovery_and_undo_restores_it(self):
        addon = _load_addon_as_package("ankiscape_safe_recovery_integration")

        calls = {"save": 0, "xp": []}
        addon.mw = _DummyMW(_DummyCol({"ankiscape_review_action_multiplier": 2}))
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Logs": 2, "Shark": 30, "Bronze arrows": 10},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
            "constitution_level": 10,
            "combat_attack_style": "ranged_accurate",
            "combat_lifepoints": 20,
            "combat_special_attack_energy": 35,
            "combat_current_levels": {"attack": 2},
            "combat_recovery_progress": {},
            "combat_supply_loadout": {},
            "combat_auto_eat_food": ["Shark"],
            "equipment": {"weapon": "Shortbow"},
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertEqual(addon._state.player_data["inventory"]["Shark"], 30)
        self.assertEqual(addon._state.player_data["inventory"]["Bronze arrows"], 10)
        # Only the six-tick Fletching segment heals; travel takes the remainder.
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 23)
        self.assertEqual(addon._state.player_data["combat_special_attack_energy"], 36)
        self.assertEqual(addon._state.player_data["combat_current_levels"], {"attack": 2})
        self.assertEqual(addon._state.player_data["combat_recovery_progress"], {"stat_drain_ticks": 6})
        self.assertEqual(
            addon._state.player_data["combat_supply_loadout"],
            {"food": {}, "potions": {}, "stat_potions": {}, "finishers": {}, "hazards": {}, "cannonballs": 0},
        )
        self.assertEqual(addon._state.player_data["combat_bank_run"], {"ticks_remaining": 94, "target_id": "chicken"})
        self.assertEqual(addon._state.player_data["combat_last_result"]["reason"], "combat_bank_run")
        self.assertEqual(addon._state.player_data["combat_last_result"]["stop_reason"], "bank_trip")
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Logs": 2, "Shark": 30, "Bronze arrows": 10})
        self.assertEqual(addon._state.player_data["fletching_exp"], 0)
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 20)
        self.assertEqual(addon._state.player_data["combat_special_attack_energy"], 35)
        self.assertEqual(addon._state.player_data["combat_current_levels"], {"attack": 2})
        self.assertEqual(addon._state.player_data["combat_recovery_progress"], {})
        self.assertEqual(addon._state.player_data["combat_supply_loadout"], {})
