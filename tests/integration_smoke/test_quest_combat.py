from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _install_quest_combat_mid_rolls,
    _load_addon_as_package,
)
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_quest_answer_resolves_stat_backed_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Stake": 1, "Stake hammer": 1},
            "current_quest": "vampyre_slayer",
            "quests": {"vampyre_slayer": {"started": True, "progress": 3, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 35,
            "constitution_level": 40,
            "prayer_level": 20,
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(addon._state.player_data["quests"]["vampyre_slayer"]["progress"], 3)
        self.assertFalse(addon._state.player_data["quests"]["vampyre_slayer"]["completed"])
        self.assertEqual(addon._state.player_data["quest_combat_encounters"], {"vampyre_slayer": ["vampyre_slayer_count_draynor_37"]})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Count Draynor"])
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_resolves_shield_of_arrav_route_combat_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_shield_arrav_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "shield_of_arrav",
            "quests": {"shield_of_arrav": {"started": True, "progress": 5, "completed": False}},
            "quest_route_states": {"shield_of_arrav": ["Join the Black Arm Gang"]},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 40,
            "strength_level": 40,
            "defense_level": 40,
            "constitution_level": 40,
            "prayer_level": 1,
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(addon._state.player_data["quests"]["shield_of_arrav"]["progress"], 5)
        self.assertFalse(addon._state.player_data["quests"]["shield_of_arrav"]["completed"])
        self.assertEqual(
            addon._state.player_data["quest_combat_encounters"],
            {"shield_of_arrav": ["shield_of_arrav_weaponsmaster_23"]},
        )
        self.assertEqual(addon._state.player_data["inventory"].get("Weapon store key", 0), 0)
        self.assertEqual(addon._state.player_data["inventory"].get("Phoenix crossbow", 0), 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Defeated Weaponsmaster"])
        self.assertEqual(calls["dialogs"], [])

        addon.on_quest_answer()

        self.assertEqual(addon._state.player_data["quests"]["shield_of_arrav"]["progress"], 6)
        self.assertFalse(addon._state.player_data["quests"]["shield_of_arrav"]["completed"])
        self.assertEqual(addon._state.player_data["inventory"]["Weapon store key"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Phoenix crossbow"], 2)
        self.assertEqual(calls["save"], 2)
        self.assertEqual(calls["gains"][-1], "Shield of Arrav 6/12")

    def test_quest_answer_resolves_a_souls_bane_fear_reaper_gate(self):
        addon = _load_addon_as_package("ankiscape_quest_a_souls_bane_combat_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "a_souls_bane",
            "quests": {"a_souls_bane": {"started": True, "progress": 3, "completed": False}},
            "quest_action_proofs": ["Fill the rage meter with an anger weapon"],
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 100,
            "strength_level": 100,
            "defense_level": 100,
            "constitution_level": 100,
            "prayer_level": 1, "combat_prayers_enabled": False,
        }

        addon.on_quest_answer()

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(addon._state.player_data["quests"]["a_souls_bane"]["progress"], 3)
        self.assertFalse(addon._state.player_data["quests"]["a_souls_bane"]["completed"])
        self.assertEqual(
            addon._state.player_data["quest_combat_encounter_counts"],
            {"a_souls_bane": {"a_souls_bane_fear_reaper_42": 1}},
        )
        self.assertEqual(addon._state.player_data["quest_combat_encounters"], {})
        self.assertEqual(calls["save"], len(calls["gains"]))
        self.assertEqual(calls["gains"], ["Defeated Fear reaper", "Fear reaper: 275 damage dealt, 295 LP left"])
        self.assertEqual(calls["dialogs"], [])

    def test_stolen_hearts_review_flow_resolves_the_real_mercenary_stage(self):
        addon = _load_addon_as_package("ankiscape_stolen_hearts_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {},
            "current_quest": "stolen_hearts",
            "quests": {
                "stolen_hearts": {
                    "started": True,
                    "progress": 3,
                    "completed": False,
                }
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "ranged_level": 99,
            "magic_level": 99,
            "prayer_level": 99,
        }

        for _ in range(10):
            if addon._state.player_data["quests"]["stolen_hearts"]["progress"] > 3:
                break
            addon.on_quest_answer()
        self.assertEqual([gain for gain in calls["gains"] if gain.startswith("Defeated ")],
                         ['Defeated Mercenary Joe', 'Defeated Skulls mercenary', 'Defeated Skulls mercenary'])

        self.assertEqual(addon._state.player_data["quests"]["stolen_hearts"]["progress"], 4)
        self.assertEqual(addon._state.player_data["inventory"]["Ransom note"], 1)
        self.assertEqual(calls["gains"][-1], "Stolen Hearts 4/6")
        self.assertEqual(calls["save"], len(calls["gains"]))
        self.assertEqual(calls["dialogs"], [])

    def test_diamond_in_the_rough_review_flow_resolves_the_sundial_ambush(self):
        addon = _load_addon_as_package("ankiscape_diamond_in_the_rough_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Heavy weight": 1},
            "current_quest": "diamond_in_the_rough",
            "quests": {
                "stolen_hearts": {
                    "started": True,
                    "progress": 6,
                    "completed": True,
                },
                "diamond_in_the_rough": {
                    "started": True,
                    "progress": 2,
                    "completed": False,
                },
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 1,
        }

        for _ in range(10):
            if addon._state.player_data["quests"]["diamond_in_the_rough"]["progress"] > 2:
                break
            addon.on_quest_answer()
        self.assertEqual([gain for gain in calls["gains"] if gain.startswith("Defeated ")],
                         ["Defeated Bandit (Diamond in the Rough)"] * 5 + ["Defeated Bandit king"])

        self.assertEqual(
            addon._state.player_data["quests"]["diamond_in_the_rough"]["progress"],
            3,
        )
        self.assertEqual(addon._state.player_data["inventory"]["Sundial gnomon"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Waterskin (4)"], 4)
        self.assertEqual(calls["gains"][-1], "Diamond in the Rough 3/5")
        self.assertEqual(calls["save"], len(calls["gains"]))
        self.assertEqual(calls["dialogs"], [])

    def test_icthlarins_little_helper_review_flow_resolves_the_canopic_guardian(self):
        addon = _load_addon_as_package("ankiscape_icthlarins_little_helper_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {
                "Canopic jar": 1,
                "Sphinx's token": 1,
                "Coins": 30,
                "Willow logs": 1,
                "Bucket": 1,
                "Bag of salt": 1,
                "Knife": 1,
            },
            "current_quest": "icthlarins_little_helper",
            "quests": {
                "icthlarins_little_helper": {
                    "started": True,
                    "progress": 3,
                    "completed": False,
                },
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "prayer_level": 1, "combat_prayers_enabled": False,
        }

        addon.on_quest_answer()
        self.assertEqual(calls["gains"][-1], "Icthlarin's Little Helper 4/9")
        self.assertEqual(
            addon._state.player_data["quests"]["icthlarins_little_helper"]["progress"],
            4,
        )
        self.assertEqual(addon._state.player_data["inventory"].get("Canopic jar", 0), 0)
        self.assertEqual(addon._state.player_data["inventory"].get("Sphinx's token", 0), 0)

        addon.on_quest_answer()
        self.assertEqual(calls["gains"][-1], "Defeated Canopic guardian")
        self.assertEqual(
            addon._state.player_data["quests"]["icthlarins_little_helper"]["progress"],
            4,
        )

        addon.on_quest_answer()

        self.assertEqual(
            addon._state.player_data["quests"]["icthlarins_little_helper"]["progress"],
            5,
        )
        self.assertEqual(addon._state.player_data["inventory"]["Canopic jar"], 1)

        addon.on_quest_answer()

        self.assertEqual(
            addon._state.player_data["quests"]["icthlarins_little_helper"]["progress"],
            6,
        )
        self.assertEqual(
            addon._state.player_data["inventory"]["Holy symbol (Icthlarin's Little Helper)"],
            1,
        )
        self.assertEqual(addon._state.player_data["inventory"].get("Bucket", 0), 0)
        self.assertEqual(calls["gains"][-1], "Icthlarin's Little Helper 6/9")
        self.assertEqual(calls["save"], 4)
        self.assertEqual(calls["dialogs"], [])

    def test_smoking_kills_review_flow_resolves_mighty_banshee_and_voice(self):
        addon = _load_addon_as_package("ankiscape_smoking_kills_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Masked earmuffs": 1},
            "current_quest": "smoking_kills",
            "quests": {"smoking_kills": {"started": True, "progress": 9, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "ranged_level": 99,
            "magic_level": 99,
            "prayer_level": 99,
        }

        while calls["gains"][-1:] != ["Defeated Mighty banshee"] and len(calls["gains"]) < 10:
            addon.on_quest_answer()
        self.assertEqual(calls["gains"][-1], "Defeated Mighty banshee")
        self.assertTrue(all(gain.startswith("Mighty banshee: ") for gain in calls["gains"][:-1]))
        self.assertEqual(addon._state.player_data["quests"]["smoking_kills"]["progress"], 9)

        addon.on_quest_answer()

        self.assertEqual(addon._state.player_data["quests"]["smoking_kills"]["progress"], 10)
        self.assertEqual(addon._state.player_data["inventory"]["Banshee voice"], 1)
        self.assertEqual(calls["gains"][-1], "Smoking Kills 10/13")
        self.assertEqual(calls["save"], len(calls["gains"]))
        self.assertEqual(calls["dialogs"], [])

    def test_shilo_village_review_flow_resolves_all_nazastarool_forms_then_corpse(self):
        addon = _load_addon_as_package("ankiscape_shilo_village_integration")
        _install_quest_combat_mid_rolls(self, addon)

        calls = {"save": 0, "gains": [], "dialogs": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.mw = _DummyMW(_DummyCol({}))
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Bone key": 1, "Beads of the dead": 1},
            "current_quest": "shilo_village",
            "quests": {
                "shilo_village": {
                    "started": True,
                    "progress": 10,
                    "completed": False,
                },
            },
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
            "attack_level": 200,
            "strength_level": 200,
            "defense_level": 200,
            "constitution_level": 200,
            "ranged_level": 200,
            "magic_level": 200,
            "prayer_level": 200,
        }

        for _ in range(10):
            if addon._state.player_data["quests"]["shilo_village"]["progress"] > 10:
                break
            addon.on_quest_answer()
        self.assertEqual([gain for gain in calls["gains"] if gain.startswith("Defeated ")],
                         ['Defeated Nazastarool (Zombie)', 'Defeated Nazastarool (Skeleton)', 'Defeated Nazastarool (Ghost)'])

        self.assertEqual(addon._state.player_data["quests"]["shilo_village"]["progress"], 11)
        self.assertEqual(addon._state.player_data["inventory"]["Rashiliyia corpse"], 1)
        self.assertEqual(calls["gains"][-1], "Shilo Village 11/12")
        self.assertEqual(calls["save"], len(calls["gains"]))
        self.assertEqual(calls["dialogs"], [])

    def test_quest_answer_completes_holy_grail_final_handoff_and_consumes_grail(self):
        addon = _load_addon_as_package("ankiscape_holy_grail_completion_integration")

        calls = {"save": 0, "gains": [], "dialogs": [], "passes": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda title, message: calls["dialogs"].append((title, message))
        addon.level_up_check = lambda _skill, data: data.__setitem__("defense_level", 33)
        addon.mw = _DummyMW(
            _DummyCol(
                {
                    "ankiscape_popups_enabled": False,
                    "ankiscape_review_action_multiplier": 3,
                    "ankiscape_cadence_kernel": False,
                }
            )
        )
        addon._state.current_skill = "Quests"
        addon._state.player_data = {
            "inventory": {"Holy grail": 1},
            "current_quest": "holy_grail",
            "quests": {"holy_grail": {"started": True, "progress": 10, "completed": False}},
            "quest_points": 0,
            "claims": {"wicked_hood": {"claimed": False}},
            "wicked_hood": {"fed_altars": []},
            "pending_skill_exp_rewards": {},
            "runecrafting_pouches": {},
            "item_charges": {},
            "completed_achievements": [],
        }
        original_overlay = addon.runtime_actions.run_answer_with_carried_overlay

        def counted_overlay(*args, **kwargs):
            calls["passes"] += 1
            return original_overlay(*args, **kwargs)

        addon.runtime_actions.run_answer_with_carried_overlay = counted_overlay
        addon._state.exp_awarded = False

        addon.on_good_answer()

        self.assertEqual(calls["passes"], 1)
        self.assertEqual(addon._state.current_skill, "Utilities")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        self.assertEqual(addon._state.player_data["quests"]["holy_grail"]["progress"], 11)
        self.assertTrue(addon._state.player_data["quests"]["holy_grail"]["completed"])
        self.assertEqual(addon._state.player_data["inventory"]["Holy grail"], 0)
        self.assertEqual(addon._state.player_data["quest_points"], 2)
        self.assertEqual(addon._state.player_data["defense_exp"], 15300.0)
        self.assertGreater(addon._state.player_data["defense_level"], 1)
        self.assertEqual(addon._state.player_data["prayer_exp"], 11000.0)
        self.assertEqual(addon._state.player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["Holy Grail complete"])
        self.assertEqual(
            [title for title, _message in calls["dialogs"]],
            ["Quest complete"],
        )
