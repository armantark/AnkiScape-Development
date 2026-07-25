import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS
from ankiscape.logic_pure.logic_pure import resolve_prayer_kill_effects_pure
from ankiscape.data.prayer_passive_data import (
    BONECRUSHER_ITEM_ID,
    BONECRUSHER_ITEM_NAME,
    ECTOPLASMATOR_ITEM_ID,
    ECTOPLASMATOR_ITEM_NAME,
    ECTOPLASMATOR_XP_BY_ENEMY_ID,
)


class PrayerPassiveMechanicsTest(unittest.TestCase):
    def test_passive_items_are_registered_without_invented_acquisition(self):
        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        bonecrusher = definitions[BONECRUSHER_ITEM_NAME]
        ectoplasmator = definitions[ECTOPLASMATOR_ITEM_NAME]
        self.assertEqual(BONECRUSHER_ITEM_ID, 18337)
        self.assertEqual(ECTOPLASMATOR_ITEM_ID, 25354)
        self.assertEqual((bonecrusher.category, bonecrusher.tradeable, bonecrusher.stackable), ("tool", False, False))
        self.assertEqual((ectoplasmator.category, ectoplasmator.tradeable, ectoplasmator.stackable), ("tool", False, False))
        self.assertEqual(bonecrusher.source_item_id, BONECRUSHER_ITEM_ID)
        self.assertEqual(ectoplasmator.source_item_id, ECTOPLASMATOR_ITEM_ID)
        self.assertTrue(bonecrusher.asset_path)
        self.assertTrue(ectoplasmator.asset_path)

    def test_ectoplasmator_mapping_contains_only_source_closed_targets(self):
        self.assertEqual(
            ECTOPLASMATOR_XP_BY_ENEMY_ID,
            {"ghost": 4.5, "ghost_level_77": 4.5, "banshee": 4.5},
        )
        self.assertNotIn("shade", ECTOPLASMATOR_XP_BY_ENEMY_ID)

    def test_bonecrusher_precedes_auto_prayer_without_duplicate_xp_or_ticks(self):
        player = {
            "inventory": {BONECRUSHER_ITEM_NAME: 1},
            "carried_inventory": {"banshee": {BONECRUSHER_ITEM_NAME: 1}},
        }
        updated, drops, prayer_xp, ticks, info = resolve_prayer_kill_effects_pure(
            player,
            "banshee",
            {"Bones": 1, "Long bone": 1, "Impious ashes": 1},
            True,
        )
        self.assertEqual(prayer_xp, 8.5)
        self.assertEqual(ticks, 1)
        self.assertEqual(drops, {"Long bone": 1})
        self.assertEqual(info, {"bonecrusher": 1, "ectoplasmator": 0, "urn_ashes": 0, "auto_prayer": 1})
        self.assertEqual(updated["prayer_bonecrusher_triggers"], 1)
        self.assertEqual(updated["prayer_actions_completed"], 2)

    def test_ectoplasmator_and_bonecrusher_rewards_are_distinct(self):
        player = {
            "inventory": {BONECRUSHER_ITEM_NAME: 1, ECTOPLASMATOR_ITEM_NAME: 1},
            "carried_inventory": {
                "banshee": {BONECRUSHER_ITEM_NAME: 1, ECTOPLASMATOR_ITEM_NAME: 1}
            },
        }
        updated, drops, prayer_xp, ticks, info = resolve_prayer_kill_effects_pure(
            player,
            "banshee",
            {"Bones": 1},
            True,
        )
        self.assertEqual(prayer_xp, 9.0)
        self.assertEqual(ticks, 0)
        self.assertEqual(drops, {})
        self.assertEqual(info["bonecrusher"], 1)
        self.assertEqual(info["ectoplasmator"], 1)
        self.assertEqual(info["auto_prayer"], 0)
        self.assertEqual(updated["prayer_bonecrusher_triggers"], 1)
        self.assertEqual(updated["prayer_ectoplasmator_triggers"], 1)
        self.assertEqual(updated["prayer_actions_completed"], 2)

    def test_prayer_urn_intercepts_ash_before_auto_prayer(self):
        player = {
            "inventory": {"Impious urn (r)": 1},
            "carried_inventory": {"imp": {"Impious urn (r)": 1}},
        }
        updated, drops, prayer_xp, ticks, info = resolve_prayer_kill_effects_pure(
            player,
            "imp",
            {"Impious ashes": 1},
            True,
        )
        self.assertEqual((prayer_xp, ticks, drops), (0.0, 0, {}))
        self.assertEqual(info["urn_ashes"], 1)
        self.assertEqual(info["auto_prayer"], 0)
        self.assertEqual(updated["active_urn_prayer"], "prayer_impious_urn")
        self.assertEqual(updated["urn_progress_prayer"], 4.0)
        self.assertEqual(updated["inventory"]["Impious urn (r)"], 0)
        self.assertEqual(updated["inventory"]["Impious urn"], 1)
        self.assertEqual(updated["prayer_urn_ashes_collected"], 1)
        self.assertNotIn("prayer_exp", updated)

    def test_auto_prayer_handles_ash_when_no_urn_can_intercept(self):
        updated, drops, prayer_xp, ticks, info = resolve_prayer_kill_effects_pure(
            {"inventory": {}},
            "imp",
            {"Impious ashes": 1},
            True,
        )
        self.assertEqual((prayer_xp, ticks, drops), (4.0, 1, {}))
        self.assertEqual(info["urn_ashes"], 0)
        self.assertEqual(info["auto_prayer"], 1)
        self.assertEqual(updated["prayer_actions_completed"], 1)

    def test_bank_only_and_other_target_passives_are_inert(self):
        player = {
            "inventory": {
                BONECRUSHER_ITEM_NAME: 1,
                ECTOPLASMATOR_ITEM_NAME: 1,
                "Impious urn (r)": 1,
            },
            "carried_inventory": {
                "ghost": {
                    BONECRUSHER_ITEM_NAME: 1,
                    ECTOPLASMATOR_ITEM_NAME: 1,
                    "Impious urn (r)": 1,
                }
            },
        }
        updated, drops, prayer_xp, ticks, info = resolve_prayer_kill_effects_pure(
            player,
            "banshee",
            {"Bones": 1, "Impious ashes": 1},
            True,
        )
        self.assertEqual((prayer_xp, ticks), (8.5, 2))
        self.assertEqual(drops, {})
        self.assertEqual(info, {"bonecrusher": 0, "ectoplasmator": 0, "urn_ashes": 0, "auto_prayer": 2})
        self.assertEqual(updated["prayer_bonecrusher_triggers"], 0)
        self.assertEqual(updated["prayer_ectoplasmator_triggers"], 0)
        self.assertEqual(updated["inventory"]["Impious urn (r)"], 1)

    def test_source_blocked_spectral_target_does_not_trigger_ectoplasmator(self):
        updated, drops, prayer_xp, ticks, info = resolve_prayer_kill_effects_pure(
            {
                "inventory": {ECTOPLASMATOR_ITEM_NAME: 1},
                "carried_inventory": {"shade": {ECTOPLASMATOR_ITEM_NAME: 1}},
            },
            "shade",
            {},
            False,
        )
        self.assertEqual((prayer_xp, ticks, drops), (0.0, 0, {}))
        self.assertEqual(info["ectoplasmator"], 0)
        self.assertNotIn("prayer_ectoplasmator_triggers", updated)


if __name__ == "__main__":
    unittest.main()
