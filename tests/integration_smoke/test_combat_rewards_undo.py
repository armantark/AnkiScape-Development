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
    def test_undo_after_review_restores_awarded_game_progress(self):
        addon = _load_addon_as_package("ankiscape_undo_integration")

        calls = {"save": 0, "hud": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Fletching"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon._state.player_data["inventory"], {"Logs": 1})
        self.assertEqual(addon._state.player_data["fletching_exp"], 0)
        self.assertEqual(addon._state.player_data["current_fletch"], "arrow_shafts")
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [5.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_prayer_review_reward_and_consumed_bone_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_prayer_undo_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.player_data = {
            "inventory": {"Dragon bones": 1},
            "prayer_level": 1,
            "prayer_exp": 0,
            "current_prayer": "bury_dragon_bones",
            "completed_achievements": [],
        }
        addon._state.current_skill = "Prayer"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon._state.player_data["inventory"]["Dragon bones"], 0)
        self.assertEqual(addon._state.player_data["prayer_exp"], 72.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(
            types.SimpleNamespace(
                operation="Answer Card",
                changes=types.SimpleNamespace(study_queues=True, card=True),
            )
        )

        self.assertEqual(addon._state.player_data["inventory"], {"Dragon bones": 1})
        self.assertEqual(addon._state.player_data["prayer_exp"], 0)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(calls["xp"], [72.0])

    def test_carried_mining_urn_transition_and_progress_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_urn_undo_integration")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Cracked mining urn (r)": 1},
            "carried_inventory": {"copper": {"Cracked mining urn (r)": 1}},
            "mining_level": 1,
            "mining_exp": 0.0,
            "current_ore": "copper",
            "toolbelt": {"mining": ["bronze_pickaxe"]},
            "equipment": {},
            "quests": {},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Mining"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        rolls = iter((0.0, 0.0, 1.0, 0.0))
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Copper ore"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Cracked mining urn"], 1)
        self.assertEqual(addon._state.player_data["active_urn_mining"], "mining_cracked_urn")
        self.assertEqual(addon._state.player_data["urn_progress_mining"], 17.5)
        self.assertEqual(addon._state.player_data["mining_exp"], 17.5)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_living_rock_remains_bundle_persists_and_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_living_rock_remains_integration")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {},
            "mining_level": 73,
            "mining_exp": 0.0,
            "current_ore": "living_rock_remains",
            "toolbelt": {"mining": ["rune_pickaxe"]},
            "equipment": {},
            "quests": {},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Mining"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        rolls = iter((0.0, 0.0, 1.0, 0.0))
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Living minerals"], 5)
        self.assertEqual(addon._state.player_data["mining_exp"], 25.0)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_bonecrusher_kill_rewards_and_counters_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_bonecrusher_undo_integration")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Bonecrusher": 1},
            "equipment": {},
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 1,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "constitution_exp": 0.0,
            "ranged_exp": 0.0,
            "magic_exp": 0.0,
            "prayer_exp": 0.0,
            "current_combat_target": "chicken",
            "carried_advanced_targets": {"chicken": True},
            "carried_layout": {"chicken": {"Bonecrusher": 1}},
            "combat_attack_style": "aggressive",
            "combat_lifepoints": 990,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {},
            "combat_current_levels": {},
            "combat_status_effects": {},
            "combat_recovery_progress": {},
            "combat_encounter": {},
            "combat_kill_counts": {},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        rolls = iter((0.0, 0.999999, 0.0) * 1000)
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random

        kills = addon._state.player_data["combat_kill_counts"]["chicken"]
        self.assertGreater(kills, 0)
        self.assertEqual(addon._state.player_data["prayer_exp"], 4.5 * kills)
        self.assertEqual(addon._state.player_data["prayer_bonecrusher_triggers"], kills)
        self.assertEqual(addon._state.player_data["prayer_actions_completed"], kills)
        self.assertNotIn("Bones", addon._state.player_data["inventory"])
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_chaos_druid_drop_closes_the_unholy_symbol_crafting_chain(self):
        from ankiscape.core.constants import (
            COMBAT_ENEMY_DATA,
            CRAFTING_DATA,
            EQUIPMENT_DATA,
        )
        from ankiscape.logic_pure.logic_pure import (
            apply_combat_burst_pure,
            apply_crafting_pure,
        )

        enemies = dict(COMBAT_ENEMY_DATA)
        chaos_druid = dict(enemies["chaos_druid"])
        chaos_druid["stats"] = dict(
            chaos_druid["stats"], hitpoints=1, defence=1
        )
        enemies["chaos_druid"] = chaos_druid
        rolls = iter((0.0, 0.999999, 126 / 128))
        player = {
            "inventory": {"Silver bar": 1},
            "equipment": {},
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "current_combat_target": "chaos_druid",
            "combat_attack_style": "aggressive",
            "combat_auto_eat_food": [],
        }

        after_kill, combat_ok, combat_result = apply_combat_burst_pure(
            player,
            enemies,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: next(rolls, 0.5),
            stop_after_first_kill=True,
            allow_bank_run=False,
        )
        after_craft, crafting_xp, craft_ok = apply_crafting_pure(
            "silver_unstrung_emblem",
            after_kill["inventory"],
            CRAFTING_DATA,
        )

        self.assertTrue(combat_ok)
        self.assertEqual(
            combat_result["drops"], {"Bones": 1, "Unholy mould": 1}
        )
        self.assertTrue(craft_ok)
        self.assertEqual(crafting_xp, 50.0)
        self.assertEqual(after_craft["Silver bar"], 0)
        self.assertEqual(after_craft["Unholy mould"], 1)
        self.assertEqual(after_craft["Unstrung emblem"], 1)

    def test_snake_kill_closes_the_snakeskin_tanning_chain(self):
        from ankiscape.core.constants import (
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            UTILITY_ACTIVITY_DATA,
        )
        from ankiscape.logic_pure.logic_pure import (
            apply_combat_burst_pure,
            apply_utility_activity_pure,
        )

        enemies = dict(COMBAT_ENEMY_DATA)
        snake = dict(enemies["bush_snake"])
        snake["stats"] = dict(snake["stats"], hitpoints=1, defence=1)
        enemies["bush_snake"] = snake
        player = {
            "inventory": {"Coins": 15, "Machete": 1},
            "equipment": {},
            "quests": {"jungle_potion": {"completed": True}},
            "woodcutting_level": 10,
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "current_combat_target": "bush_snake",
            "combat_attack_style": "aggressive",
            "combat_auto_eat_food": [],
        }

        after_kill, combat_ok, combat_result = apply_combat_burst_pure(
            player,
            enemies,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: 0.0,
            stop_after_first_kill=True,
            allow_bank_run=False,
        )
        after_tan, _exp, tan_ok, processed = apply_utility_activity_pure(
            "tan_snakeskin",
            after_kill["inventory"],
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(combat_ok)
        self.assertEqual(combat_result["drops"], {"Bones": 1, "Snake hide": 1})
        self.assertTrue(tan_ok)
        self.assertEqual(processed, 1)
        self.assertEqual(after_tan["Snake hide"], 0)
        self.assertEqual(after_tan["Coins"], 0)
        self.assertEqual(after_tan["Snakeskin"], 1)

    def test_snake_hide_combat_review_persists_and_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_snake_hide_review_undo_integration")
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        addon.mw = _DummyMW(_DummyCol())
        saved_states = []
        addon.save_player_data = lambda: saved_states.append(
            copy.deepcopy(addon._state.player_data)
        )
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
                "current_combat_target": "bush_snake",
                "combat_attack_style": "aggressive",
                "combat_lifepoints": 990,
                "loot_value_threshold": 0,
                "woodcutting_level": 10,
            }
        )
        addon._state.player_data["inventory"]["Machete"] = 1
        addon._state.player_data["quests"]["jungle_potion"] = {
            "started": True,
            "progress": 5,
            "completed": True,
        }
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False
        addon._state.review_undo_stack.clear()
        initial = copy.deepcopy(addon._state.player_data)

        combat_runtime = sys.modules[
            f"{addon.__name__}.runtime.runtime_actions_combat"
        ]
        original_enemies = combat_runtime.COMBAT_ENEMY_DATA
        enemies = dict(original_enemies)
        snake = dict(enemies["bush_snake"])
        snake["stats"] = dict(snake["stats"], hitpoints=1, defence=1)
        enemies["bush_snake"] = snake
        original_random = addon.random.random
        combat_runtime.COMBAT_ENEMY_DATA = enemies
        addon.random.random = lambda: 0.0
        try:
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )
        finally:
            addon.random.random = original_random
            combat_runtime.COMBAT_ENEMY_DATA = original_enemies

        self.assertGreater(addon._state.player_data["inventory"]["Snake hide"], 0)
        self.assertTrue(
            any(state["inventory"].get("Snake hide", 0) > 0 for state in saved_states)
        )
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])

    def test_ectoplasmator_kill_rewards_and_counters_roll_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_ectoplasmator_undo_integration")
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        initial = {
            "inventory": {"Ectoplasmator": 1},
            "equipment": {},
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 1,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "constitution_exp": 0.0,
            "ranged_exp": 0.0,
            "magic_exp": 0.0,
            "prayer_exp": 0.0,
            "current_combat_target": "ghost",
            "carried_advanced_targets": {"ghost": True},
            "carried_layout": {"ghost": {"Ectoplasmator": 1}},
            "combat_attack_style": "aggressive",
            "combat_lifepoints": 990,
            "combat_auto_eat_food": ["Shrimps"],
            "combat_supply_loadout": {},
            "combat_current_levels": {},
            "combat_status_effects": {},
            "combat_recovery_progress": {},
            "combat_encounter": {},
            "combat_kill_counts": {},
            "completed_achievements": [],
        }
        addon._state.player_data = copy.deepcopy(initial)
        addon._state.current_skill = "Combat"
        addon._state.card_turned = True
        addon._state.answer_shown = True
        addon._state.exp_awarded = False

        original_enemy = copy.deepcopy(addon.COMBAT_ENEMY_DATA["ghost"])
        easy_ghost = copy.deepcopy(original_enemy)
        easy_ghost["stats"].update({"hitpoints": 1, "attack": 1, "strength": 1, "defence": 1})
        easy_ghost["drops"] = {"guaranteed": (), "tables": ()}
        addon.COMBAT_ENEMY_DATA["ghost"] = easy_ghost
        rolls = iter((0.0, 0.999999, 0.0) * 1000)
        original_random = addon.random.random
        addon.random.random = lambda: next(rolls, 0.5)
        try:
            addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        finally:
            addon.random.random = original_random
            addon.COMBAT_ENEMY_DATA["ghost"] = original_enemy

        kills = addon._state.player_data["combat_kill_counts"]["ghost"]
        self.assertGreater(kills, 0)
        self.assertEqual(addon._state.player_data["prayer_exp"], 4.5 * kills)
        self.assertEqual(addon._state.player_data["prayer_ectoplasmator_triggers"], kills)
        self.assertEqual(addon._state.player_data["prayer_actions_completed"], kills)
        self.assertEqual(len(addon._state.review_undo_stack), 1)

        addon._on_state_did_undo(types.SimpleNamespace(
            operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True),
        ))
        self.assertEqual(addon._state.player_data, initial)
        self.assertEqual(addon._state.review_undo_stack, [])
