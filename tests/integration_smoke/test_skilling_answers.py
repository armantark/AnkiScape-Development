from tests.test_integration_smoke import _DummyCol, _DummyMW, _load_addon_as_package
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_fletching_answer_updates_inventory_and_exp(self):
        addon = _load_addon_as_package("ankiscape_fletching_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Logs": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        addon.on_fletching_answer()

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon._state.player_data["fletching_exp"], 5.0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [5.0])

    def test_firemaking_answer_burns_log_adds_ashes_and_exp(self):
        addon = _load_addon_as_package("ankiscape_firemaking_integration")

        calls = {"save": 0, "xp": [], "achievements": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda data: calls["achievements"].append(data["inventory"].get("Ashes", 0))
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.show_error_message = lambda _title, message: self.fail(message)

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.player_data = {
                "inventory": {"Logs": 1},
                "firemaking_level": 1,
                "firemaking_exp": 0,
                "current_firemaking": "logs",
                "completed_achievements": [],
            }

            addon.on_firemaking_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Logs"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Ashes"], 1)
        self.assertEqual(
            addon._state.player_data["achievement_progress"]["skills"]["firemaking"]["outputs"]["Ashes"],
            1,
        )
        self.assertAlmostEqual(addon._state.player_data["firemaking_exp"], 40.0)
        self.assertEqual(calls["achievements"], [1])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [40.0])

    def test_fishing_answer_catches_fish_adds_exp_and_hidden_side_exp(self):
        addon = _load_addon_as_package("ankiscape_fishing_integration")

        calls = {"save": 0, "xp": [], "achievements": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda data: calls["achievements"].append(data["inventory"].get("Leaping trout", 0))
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.show_error_message = lambda _title, message: self.fail(message)

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon._state.player_data = {
                "inventory": {"Feather": 1},
                "fishing_level": 48,
                "fishing_exp": 0,
                "strength_level": 15,
                "strength_exp": 0,
                "agility_level": 15,
                "agility_exp": 0,
                "current_fishing": "catch_leaping_fish",
                "completed_achievements": [],
                "unlocked_abilities": ["barbarian_fishing"],
            }

            addon.on_fishing_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Feather"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Leaping trout"], 1)
        self.assertAlmostEqual(addon._state.player_data["fishing_exp"], 50.0)
        self.assertAlmostEqual(addon._state.player_data["strength_exp"], 5.0)
        self.assertAlmostEqual(addon._state.player_data["agility_exp"], 5.0)
        self.assertEqual(calls["achievements"], [1])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [50.0])

    def test_smithing_answer_forges_selected_recipe(self):
        addon = _load_addon_as_package("ankiscape_smithing_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.refresh_skill_availability = lambda *_args, **_kwargs: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Iron bar": 2},
            "smithing_level": 20,
            "smithing_exp": 0,
            "current_smith": "forge_iron_pickaxe",
            "completed_achievements": [],
        }

        addon.on_smithing_answer()

        self.assertEqual(addon._state.player_data["inventory"]["Iron bar"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Iron pickaxe"], 1)
        self.assertAlmostEqual(addon._state.player_data["smithing_exp"], 50.0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [50.0])

    def test_smithing_answer_iron_failure_consumes_ore_without_xp(self):
        addon = _load_addon_as_package("ankiscape_smithing_iron_failure_integration")

        calls = {"save": 0, "xp": [], "gains": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.refresh_skill_availability = lambda *_args, **_kwargs: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Iron ore": 1},
            "smithing_level": 15,
            "smithing_exp": 0,
            "crafting_level": 1,
            "current_smith": "smelt_iron_bar",
            "completed_achievements": [],
        }

        original_random = addon.random.random
        addon.random.random = lambda: 0.99
        try:
            addon.on_smithing_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Iron ore"], 0)
        self.assertNotIn("Iron bar", addon._state.player_data["inventory"])
        self.assertEqual(addon._state.player_data["smithing_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["gains"], ["The ore was too impure"])
        telemetry = addon._state.player_data["action_telemetry"]["actions"]["smithing:smelt_iron_bar"]
        self.assertEqual(telemetry["failure_kinds"], {"smelt_fail": 1})

    def test_equipment_callbacks_equip_and_unequip_items(self):
        addon = _load_addon_as_package("ankiscape_equipment_callbacks")
        addon.mw = _DummyMW(_DummyCol())
        calls = {"save": 0, "errors": []}
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.show_error_message = lambda title, message: calls["errors"].append((title, message))
        addon._state.player_data = {
            "inventory": {"Bronze platebody": 1, "Rune platebody": 1},
            "equipment": {},
            "defense_level": 1,
        }

        self.assertTrue(addon.on_equip_item("Bronze platebody"))
        self.assertEqual(addon._state.player_data["inventory"]["Bronze platebody"], 0)
        self.assertEqual(addon._state.player_data["equipment"], {"body": "Bronze platebody"})

        self.assertFalse(addon.on_equip_item("Rune platebody"))
        self.assertEqual(calls["errors"], [("Cannot equip item", "Requires level 40 Defense")])
        self.assertEqual(addon._state.player_data["equipment"], {"body": "Bronze platebody"})

        self.assertTrue(addon.on_unequip_slot("body"))
        self.assertEqual(addon._state.player_data["inventory"]["Bronze platebody"], 1)
        self.assertEqual(addon._state.player_data["equipment"], {})
        self.assertEqual(calls["save"], 2)

    def test_equipment_callbacks_move_degradable_instance_with_the_item(self):
        addon = _load_addon_as_package("ankiscape_equipment_instance_callbacks")
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon._state.player_data = {
            "inventory": {"Combat hood 100": 1},
            "equipment": {},
            "defense_level": 20,
            "magic_level": 20,
            "equipment_instances": {
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 80_000,
                    "location": "bank",
                }
            },
            "equipment_instance_next_id": 2,
        }
        self.assertTrue(addon.on_equip_item("Combat hood 100"))
        self.assertEqual(
            addon._state.player_data["equipment_instances"]["equipment-1"]["location"],
            "equipped:head",
        )
        self.assertTrue(addon.on_unequip_slot("head"))
        self.assertEqual(
            addon._state.player_data["equipment_instances"]["equipment-1"]["location"],
            "bank",
        )

    def test_utility_answer_batches_inventory_without_skill_xp(self):
        addon = _load_addon_as_package("ankiscape_utility_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {"Clay": 3},
            "crafting_exp": 0,
            "current_utility": "make_soft_clay",
            "completed_achievements": [],
        }

        addon.on_utility_answer()

        self.assertEqual(addon._state.player_data["inventory"]["Clay"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Soft clay"], 3)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        # No-XP activities still surface a floating "+N <item>" confirmation so the
        # player knows the review did something despite earning no XP.
        self.assertEqual(calls["gains"], ["+3 Soft clay"])

    def test_wool_gathering_utility_grants_wool_without_skill_xp(self):
        addon = _load_addon_as_package("ankiscape_wool_utility_integration")

        calls = {"save": 0, "gains": []}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon._state.player_data = {
            "inventory": {},
            "crafting_exp": 0,
            "current_utility": "gather_wool",
            "completed_achievements": [],
        }

        addon.on_utility_answer()

        self.assertEqual(addon._state.player_data["inventory"]["Wool"], 28)
        self.assertEqual(addon._state.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["gains"], ["+28 Wool"])

    def test_runecrafting_answer_crafts_air_runes_and_awards_exp(self):
        addon = _load_addon_as_package("ankiscape_runecrafting_integration")

        calls = {"save": 0, "xp": [], "achievements": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda data: calls["achievements"].append(data["inventory"].get("Air rune", 0))
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.show_error_message = lambda _title, message: self.fail(message)

        original_random = addon.random.random
        addon.random.random = lambda: 1.0
        try:
            addon._state.player_data = {
                "inventory": {"Rune essence": 30, "Air talisman": 1},
                "equipment": {},
                "runecrafting_level": 1,
                "runecrafting_exp": 0,
                "current_runecrafting": "craft_air_runes",
                "quests": {"rune_mysteries": {"started": True, "progress": 6, "completed": True}},
                "wicked_hood": {"fed_altars": []},
                "runecrafting_pouches": {},
                "item_charges": {},
                "completed_achievements": [],
            }

            addon.on_runecrafting_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon._state.player_data["inventory"]["Rune essence"], 3)
        self.assertEqual(addon._state.player_data["inventory"]["Air rune"], 27)
        self.assertEqual(
            addon._state.player_data["achievement_progress"]["skills"]["runecrafting"]["outputs"]["Air rune"],
            27,
        )
        self.assertAlmostEqual(addon._state.player_data["runecrafting_exp"], 135.0)
        self.assertEqual(calls["achievements"], [27])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [135.0])
