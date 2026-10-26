from tests.test_integration_smoke import (
    QUEST_DATA,
    _DummyCol,
    _DummyMW,
    _load_addon_as_package,
    quest_action_proofs_for_quest,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_quest_answer_completes_rune_mysteries_and_switches_off(self):
        addon = _load_addon_as_package("ankiscape_quest_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Research notes": 1},
            "current_quest": "rune_mysteries",
            "quests": {"rune_mysteries": {"started": True, "progress": 5, "completed": False}},
            "quest_action_proofs": ["Return Aubury's research notes to Sedridor"],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "runecrafting_level": 1,
            "runecrafting_exp": 0,
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertTrue(addon._state.player_data["quests"]["rune_mysteries"]["completed"])
        self.assertEqual(addon._state.player_data["quest_points"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Air talisman"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Research notes"], 0)
        self.assertEqual(addon._state.player_data["runecrafting_exp"], 0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Rune Mysteries complete"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest complete")
        self.assertIn("Rune Mysteries is complete", calls["dialogs"][0][1])
        self.assertIn("questing has been switched off", calls["dialogs"][0][1])

    def test_quest_answer_blocks_knights_sword_without_stage_item(self):
        addon = _load_addon_as_package("ankiscape_quest_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "the_knights_sword",
            "quests": {"the_knights_sword": {"started": True, "progress": 2, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "smithing_level": 10,
            "smithing_exp": 0,
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertFalse(addon._state.player_data["quests"]["the_knights_sword"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["the_knights_sword"]["progress"], 2)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["smithing_exp"], 0)
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("Needs Redberry pie x1", calls["dialogs"][0][1])

    def test_quest_answer_progresses_dwarf_cannon_repairs_without_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_dwarf_cannon_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Railing": 6, "Hammer": 1},
            "current_quest": "dwarf_cannon",
            "quests": {"dwarf_cannon": {"started": True, "progress": 2, "completed": False}},
            "quest_points": 0,
            "crafting_exp": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["dwarf_cannon"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["dwarf_cannon"]["progress"], 3)
        self.assertEqual(addon._state.player_data["inventory"]["Railing"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Hammer"], 1)
        self.assertEqual(addon._state.player_data["quest_combat_encounters"], {})
        self.assertEqual(addon._state.player_data["quest_combat_encounter_counts"], {})
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Dwarf Cannon 3/14"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_fishing_contest_pass_emitter(self):
        addon = _load_addon_as_package("ankiscape_fishing_contest_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "fishing_contest",
            "quests": {"fishing_contest": {"started": True, "progress": 1, "completed": False}},
            "quest_points": 0,
            "fishing_exp": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["fishing_contest"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["fishing_contest"]["progress"], 2)
        self.assertEqual(addon._state.player_data["inventory"]["Fishing pass"], 1)
        self.assertEqual(quest_action_proofs_for_quest(addon._state.player_data, "fishing_contest", QUEST_DATA), ("Receive a fishing pass from Austri or Vestri",))
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["fishing_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Fishing Contest 2/7"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_waterfall_book_gate(self):
        addon = _load_addon_as_package("ankiscape_waterfall_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "waterfall_quest",
            "quests": {"waterfall_quest": {"started": True, "progress": 2, "completed": False}},
            "quest_action_proofs": ["Search the Baxtorian bookcase", "Read the Book on Baxtorian"],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["waterfall_quest"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["waterfall_quest"]["progress"], 3)
        self.assertEqual(addon._state.player_data["inventory"]["Book on Baxtorian"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Waterfall Quest 3/6"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_biohazard_pigeon_setup_gate(self):
        addon = _load_addon_as_package("ankiscape_biohazard_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "biohazard",
            "quests": {"biohazard": {"started": True, "progress": 3, "completed": False}},
            "quest_action_proofs": [
                "Ask Jerico about using messenger pigeons",
                "Search Jerico's cupboard for bird feed",
                "Take a pigeon cage from Jerico's house",
            ],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["biohazard"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["biohazard"]["progress"], 4)
        self.assertEqual(addon._state.player_data["inventory"]["Bird feed"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Pigeon cage"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Biohazard 4/14"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_heroes_gerrant_slime_gate(self):
        addon = _load_addon_as_package("ankiscape_heroes_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "heroes_quest",
            "quests": {"heroes_quest": {"started": True, "progress": 2, "completed": False}},
            "quest_action_proofs": ["Ask Gerrant how to catch lava eels"],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["heroes_quest"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["heroes_quest"]["progress"], 3)
        self.assertEqual(addon._state.player_data["inventory"]["Blamish snail slime"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Heroes' Quest 3/13"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_progresses_family_crest_caleb_fish_gate(self):
        addon = _load_addon_as_package("ankiscape_family_crest_stage_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {
                "Shrimps": 1,
                "Salmon": 1,
                "Tuna": 1,
                "Bass": 1,
                "Swordfish": 1,
            },
            "current_quest": "family_crest",
            "quests": {"family_crest": {"started": True, "progress": 3, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertFalse(addon._state.player_data["quests"]["family_crest"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["family_crest"]["progress"], 4)
        self.assertEqual(addon._state.player_data["inventory"]["Shrimps"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Swordfish"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Caleb crest"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Family Crest 4/16"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_blocks_witchs_house_mouse_puzzle_without_stage_item(self):
        addon = _load_addon_as_package("ankiscape_witchs_house_mouse_gate_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Magnet": 1},
            "current_quest": "witchs_house",
            "quests": {"witchs_house": {"started": True, "progress": 8, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertFalse(addon._state.player_data["quests"]["witchs_house"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["witchs_house"]["progress"], 8)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("Needs Cheese x1", calls["dialogs"][0][1])
        self.assertNotIn("Use cheese on the mouse hole", calls["dialogs"][0][1])

    def test_quest_answer_blocks_merlins_crystal_wax_without_repellent(self):
        addon = _load_addon_as_package("ankiscape_merlins_crystal_wax_gate_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Bucket": 1},
            "current_quest": "merlins_crystal",
            "quests": {"merlins_crystal": {"started": True, "progress": 4, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertFalse(addon._state.player_data["quests"]["merlins_crystal"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["merlins_crystal"]["progress"], 4)
        self.assertEqual(addon._state.player_data["inventory"]["Bucket"], 1)
        self.assertEqual(addon._state.player_data["inventory"].get("Bucket of wax", 0), 0)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("Needs Insect repellent x1", calls["dialogs"][0][1])

    def test_quest_answer_blocks_fight_arena_statless_combat(self):
        addon = _load_addon_as_package("ankiscape_fight_arena_missing_stats_integration")

        calls = {"save": 0, "gains": [], "xp": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda amount: calls["xp"].append(amount)
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Khazard helmet": 1, "Khazard armour": 1, "Khazard cell keys": 1},
            "current_quest": "fight_arena",
            "quests": {"fight_arena": {"started": True, "progress": 8, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 150,
            "strength_level": 150,
            "defense_level": 150,
            "constitution_level": 150,
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertFalse(addon._state.player_data["quests"]["fight_arena"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["fight_arena"]["progress"], 8)
        self.assertEqual(addon._state.player_data["quest_points"], 0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["gains"], [])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["dialogs"][0][0], "Quest blocked")
        self.assertIn("This fight is not modelled yet (combat stats missing): Khazard ogre level 63", calls["dialogs"][0][1])

    def test_quest_answer_progresses_black_knights_disguise_from_equipment(self):
        addon = _load_addon_as_package("ankiscape_black_knights_stage_integration")

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.level_up_check = lambda _skill, _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "equipment": {"body": "Iron chainbody", "head": "Bronze med helm"},
            "current_quest": "black_knights_fortress",
            "quests": {"black_knights_fortress": {"started": True, "progress": 1, "completed": False}},
            "quest_action_proofs": ["Infiltrate the Black Knights' Fortress"],
            "quest_points": 12,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(addon._state.player_data["quests"]["black_knights_fortress"]["progress"], 2)
        self.assertFalse(addon._state.player_data["quests"]["black_knights_fortress"]["completed"])
        self.assertEqual(addon._state.player_data["quest_points"], 12)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Black Knights' Fortress 2/5"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_consumes_priest_in_peril_essence_at_completion_gate(self):
        addon = _load_addon_as_package("ankiscape_priest_in_peril_essence_integration")

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.level_up_check = lambda _skill, _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Rune essence": 50, "Pure essence": 24},
            "current_quest": "priest_in_peril",
            "quests": {"priest_in_peril": {"started": True, "progress": 8, "completed": False}},
            "quest_points": 0,
            "prayer_exp": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertTrue(addon._state.player_data["quests"]["priest_in_peril"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["priest_in_peril"]["progress"], 9)
        self.assertEqual(addon._state.player_data["inventory"]["Rune essence"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Pure essence"], 24)
        self.assertEqual(addon._state.player_data["inventory"]["Wolfbane dagger"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 1)
        self.assertEqual(addon._state.player_data["prayer_exp"], 1406.0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["dialogs"][0][0], "Quest complete")

    def test_quest_answer_completes_temple_of_ikov_lucien_branch_and_consumes_staff(self):
        addon = _load_addon_as_package("ankiscape_temple_of_ikov_lucien_integration")

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.level_up_check = lambda _skill, _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Staff of armadyl": 1},
            "current_quest": "temple_of_ikov",
            "quests": {"temple_of_ikov": {"started": True, "progress": 10, "completed": False}},
            "quest_route_states": {"temple_of_ikov": ["Side with Lucien"]},
            "quest_action_proofs": ["Give the Staff of Armadyl to Lucien in Varrock"],
            "quest_points": 0,
            "thieving_level": 42,
            "fletching_level": 1,
            "fletching_exp": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertTrue(addon._state.player_data["quests"]["temple_of_ikov"]["completed"])
        self.assertEqual(addon._state.player_data["quests"]["temple_of_ikov"]["progress"], 11)
        self.assertEqual(addon._state.player_data["inventory"]["Staff of armadyl"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Shiny key"], 1)
        self.assertEqual(addon._state.player_data["quest_points"], 1)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Temple of Ikov complete"])
        self.assertEqual(calls["dialogs"][0][0], "Quest complete")
