from tests.test_integration_smoke import _DummyCol, _DummyMW, _load_addon_as_package, sys
from ankiscape.logic_pure.combat.ammunition import equipped_ammo, carried_runes
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_death_office_reclaim_callback_consumes_coins_and_saves(self):
        addon = _load_addon_as_package("ankiscape_death_office_reclaim_integration")
        addon.mw = _DummyMW(_DummyCol())
        calls = {"save": 0, "errors": [], "achievement_coins": []}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.check_achievements = lambda data: calls["achievement_coins"].append(data["inventory"]["Coins"])
        addon._refresh_skill_availability = lambda: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["errors"].append((title, message))

        addon._state.player_data = {
            "inventory": {"Coins": 150},
            "death_office": {"items": ["Bronze sword"], "source": "combat_stacked_grave"},
            "combat_grave": {},
        }

        self.assertTrue(addon.on_reclaim_death_office())
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Coins"], 50)
        self.assertEqual(addon._state.player_data["inventory"]["Bronze sword"], 1)
        self.assertEqual(addon._state.player_data["death_office"], {})
        self.assertEqual(calls["achievement_coins"], [50])

    def test_equipping_a_melee_weapon_returns_loaded_magic_runes_to_bank(self):
        addon = _load_addon_as_package("ankiscape_combat_weapon_loadout")
        addon.mw = _DummyMW(_DummyCol())
        calls = {"save": 0, "hud": 0, "refresh": 0}
        addon.save_player_data = lambda: calls.__setitem__(
            "save", calls["save"] + 1
        )
        addon.check_achievements = lambda _data: None
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__(
            "hud", calls["hud"] + 1
        )
        addon._refresh_skill_availability = lambda: calls.__setitem__(
            "refresh", calls["refresh"] + 1
        )
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "inventory": {'Rune scimitar': 1, 'Air rune': 5, 'Mind rune': 5},
            "equipment": {"weapon": "Staff"},
            "attack_level": 40,
            "magic_level": 99,
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "wind_strike",
            "combat_pack_mode": "max_output",
            "combat_vengeance": True,
            "combat_supply_loadout": {}, 'carried_inventory': {'chicken': {"Air rune": 5, "Mind rune": 5}},
            "combat_encounter": {},
            "constitution_level": 10,
        }

        self.assertTrue(addon.on_equip_item("Rune scimitar"))

        self.assertEqual(
            addon._state.player_data["equipment"], {"weapon": "Rune scimitar"}
        )
        self.assertEqual(
            carried_runes(addon._state.player_data), {}
        )
        self.assertEqual(addon._state.player_data["inventory"]["Air rune"], 5)
        self.assertEqual(addon._state.player_data["inventory"]["Mind rune"], 5)
        self.assertEqual(addon._state.player_data["inventory"]["Staff"], 1)
        self.assertEqual(calls, {"save": 1, "hud": 1, "refresh": 1})

    def test_combat_loadout_menu_callbacks_refill_and_unload_supplies(self):
        addon = _load_addon_as_package("ankiscape_combat_loadout_callbacks")
        addon.mw = _DummyMW(_DummyCol())
        calls = {
            "save": 0,
            "hud": 0,
            "refresh": 0,
            "achievement_runes": [],
            "activity": [],
        }
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.check_achievements = lambda data: calls["achievement_runes"].append(
            data["inventory"].get("Air rune", 0) + data["inventory"].get("Mind rune", 0)
        )
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon._refresh_skill_availability = lambda: calls.__setitem__("refresh", calls["refresh"] + 1)
        addon._show_activity_gain = lambda message: calls["activity"].append(message)
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.current_skill = "Combat"
        addon._state.player_data = {
            "inventory": {"Shark": 30, "Antipoison (2)": 1, "Air rune": 5, "Mind rune": 5, "Fire rune": 5},
            "equipment": {"weapon": "Staff of fire"},
            "combat_attack_style": "magic_standard",
            "current_combat_spell": "fire_strike",
            "combat_auto_eat_food": ["Shark"],
            "combat_supply_loadout": {},
            "combat_pack_mode": "max_safety",  # fill the 28-slot budget with food
            "combat_encounter": {},
            "constitution_level": 10,
        }

        self.assertTrue(addon.on_do_bank_run_now())
        self.assertEqual(
            addon._state.player_data["combat_bank_run"],
            {"ticks_remaining": 100, "target_id": "chicken"},
        )
        addon._state.player_data["combat_bank_run"] = {}
        addon._state.current_skill = "Mining"
        addon._state.player_data["current_ore"] = "coal"
        self.assertTrue(addon.on_do_bank_run_now())
        self.assertEqual(
            addon._state.player_data["skilling_bank_run_requested"], "coal"
        )
        addon._state.player_data.pop("skilling_bank_run_requested", None)
        registry = sys.modules[f"{addon.__name__}.core.skill_registry"]
        for skill in registry.CURRENT_SKILLS:
            if not skill.participates_in_review:
                continue
            if skill.current_target_key:
                addon._state.player_data[skill.current_target_key] = skill.default_target
            addon._state.current_skill = skill.display_name
            self.assertTrue(addon.on_do_bank_run_now(), skill.display_name)
            if skill.review_handler_key == "combat" or skill.id == "slayer":
                self.assertIn("combat_bank_run", addon._state.player_data)
                addon._state.player_data["combat_bank_run"] = {}
            elif skill.review_handler_key in addon.runtime_actions._BANK_RUN_TARGET_KEYS:
                target_key = addon.runtime_actions._BANK_RUN_TARGET_KEYS[
                    skill.review_handler_key
                ]
                expected_target = (
                    addon._state.player_data.get(target_key)
                    if target_key
                    else None
                ) or skill.review_handler_key
                self.assertEqual(
                    addon._state.player_data["skilling_bank_run_requested"],
                    expected_target,
                )
                addon._state.player_data.pop("skilling_bank_run_requested", None)
        for surface in ("Activities", "Utilities", "Quests"):
            addon._state.current_skill = surface
            self.assertTrue(addon.on_do_bank_run_now(), surface)
            self.assertIn("skilling_bank_run_requested", addon._state.player_data)
            addon._state.player_data.pop("skilling_bank_run_requested", None)
        addon._state.current_skill = "Farming"
        self.assertTrue(addon.on_do_bank_run_now())
        self.assertNotIn("skilling_bank_run_requested", addon._state.player_data)
        self.assertEqual(calls["activity"], ["Bank run — arrived and ready"])
        addon._state.current_skill = "Slayer"
        self.assertTrue(addon.on_do_bank_run_now())
        self.assertEqual(
            addon._state.player_data["combat_bank_run"],
            {"ticks_remaining": 100, "target_id": "chicken"},
        )
        addon._state.player_data["combat_bank_run"] = {}
        addon._state.current_skill = "Combat"

        self.assertTrue(addon.on_set_combat_auto_eat_threshold(65))
        self.assertEqual(addon._state.player_data["combat_auto_eat_threshold_percent"], 65)
        self.assertTrue(addon.on_set_combat_auto_eat_food("Lobster"))
        self.assertEqual(addon._state.player_data["combat_auto_eat_food"][0], "Lobster")

        addon._state.player_data["combat_auto_eat_food"] = ["Shark"]
        self.assertTrue(addon.on_refill_combat_loadout())
        self.assertEqual(addon._state.player_data["combat_supply_loadout"]["food"], {"Shark": 20})
        self.assertEqual(addon._state.player_data["combat_supply_loadout"]["potions"], {"Antipoison (2)": 1})
        self.assertEqual(carried_runes(addon._state.player_data), {"Air rune": 5, "Mind rune": 5})
        self.assertEqual(addon._state.player_data["inventory"]["Shark"], 10)
        self.assertEqual(addon._state.player_data["inventory"]["Antipoison (2)"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Fire rune"], 5)

        self.assertTrue(addon.on_set_combat_pack_mode("max_output"))
        self.assertEqual(
            addon._state.player_data["combat_supply_loadout"]["food"], {"Shark": 8}
        )
        self.assertEqual(calls["achievement_runes"], [10])

        self.assertTrue(addon.on_unload_combat_loadout())
        self.assertEqual(
            addon._state.player_data["combat_supply_loadout"],
            {"food": {}, "potions": {}, "stat_potions": {}, "finishers": {}, "hazards": {}, "cannonballs": 0},
        )
        self.assertEqual(addon._state.player_data["inventory"]["Shark"], 30)
        self.assertEqual(addon._state.player_data["inventory"]["Antipoison (2)"], 1)
        self.assertEqual(addon._state.player_data["inventory"]["Air rune"], 5)
        self.assertEqual(addon._state.player_data["inventory"]["Mind rune"], 5)
        self.assertEqual(calls["achievement_runes"], [10, 10])
        self.assertGreaterEqual(calls["save"], 5)
        self.assertGreaterEqual(calls["hud"], 4)
        self.assertGreaterEqual(calls["refresh"], 4)
