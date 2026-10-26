from tests.test_integration_smoke import _load_addon_as_package
from tests.integration_smoke import fixtures


class TestIntegrationSmoke(fixtures.TestIntegrationSmoke):
    def test_skill_availability_cache_reuses_results_until_a_real_dependency_changes(self):
        addon = _load_addon_as_package("ankiscape_availability_cache")
        addon._state.player_data = {
            "inventory": {},
            "smithing_level": 1,
            "crafting_level": 1,
            "fletching_level": 1,
            "firemaking_level": 1,
            "hunter_level": 1,
            "cooking_level": 1,
            "runecrafting_level": 1,
            "quests": {},
            "equipment": {},
            "wicked_hood": {},
        }
        refreshes = []
        addon.refresh_skill_availability = lambda *values: refreshes.append(values)
        addon._state.skill_availability_cache_fingerprint = None

        addon._refresh_skill_availability()
        addon._refresh_skill_availability()
        addon._state.player_data["inventory"]["Unrelated profile marker"] = 1
        addon._refresh_skill_availability()

        self.assertEqual(len(refreshes), 1)
        self.assertEqual(len(refreshes[0]), 7)

        addon._state.player_data["inventory"]["Copper ore"] = 1
        addon._refresh_skill_availability()
        self.assertEqual(len(refreshes), 2)

    def test_skill_availability_refresh_uses_boosted_crafting_rules(self):
        addon = _load_addon_as_package("ankiscape_boosted_crafting_availability")
        addon._state.player_data = {
            "inventory": {"Cracked cooking urn (unf)": 3},
            "smithing_level": 1,
            "crafting_level": 1,
            "fletching_level": 1,
            "firemaking_level": 1,
            "hunter_level": 1,
            "cooking_level": 1,
            "runecrafting_level": 1,
            "skilling_current_levels": {"crafting": 2},
            "quests": {},
            "equipment": {},
            "wicked_hood": {},
        }
        refreshes = []
        addon.refresh_skill_availability = lambda *values: refreshes.append(values)
        addon._state.skill_availability_cache_fingerprint = None

        addon._refresh_skill_availability()
        self.assertEqual(len(refreshes), 1)
        self.assertTrue(refreshes[0][1])

        addon._state.player_data["skilling_current_levels"]["crafting"] = 1
        addon._refresh_skill_availability()
        self.assertEqual(len(refreshes), 2)
        self.assertFalse(refreshes[1][1])
