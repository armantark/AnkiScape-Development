from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    BONE_SOURCE_EXTRA_ITEM_DATA,
    COMBAT_ENEMY_DATA,
    EQUIPMENT_DATA,
    EXTRA_ITEM_DATA,
    ITEM_DEFINITIONS,
    UTILITY_ACTIVITY_DATA,
    UTILITY_SURFACE_ID,
)
from ankiscape.data.bone_sources_data import (
    COFFIN_OUTPUT_WEIGHTS,
    COMBAT_BONE_SOURCES,
    DARKAN_REV,
    SHAIKAHAN_SPEARS,
    bone_source_enemies_as_dict,
    bone_source_extra_items_as_dict,
    bone_source_utility_activities_as_dict,
)
from ankiscape.logic_pure.logic_pure import (
    apply_combat_burst_pure,
    apply_utility_activity_pure,
    combat_target_locked_reasons_pure,
)


class BoneSourceDataTests(unittest.TestCase):
    def test_four_combat_sources_have_exact_profiles_and_guaranteed_routes(self):
        self.assertEqual(
            [
                (
                    source.id,
                    source.level,
                    source.hitpoints,
                    source.attack,
                    source.strength,
                    source.defence,
                    source.magic,
                    source.ranged,
                    source.attack_style,
                    source.max_hit,
                    source.guaranteed_drops,
                )
                for source in COMBAT_BONE_SOURCES
            ],
            [
                (
                    "zogre", 44, 710, 20, 36, 35, 1, 1, "melee", 50,
                    (("Zogre bones", 1), ("Ogre coffin key", 1)),
                ),
                (
                    "jogre", 53, 600, 43, 43, 43, 1, 1, "melee", 73,
                    (("Jogre bones", 1),),
                ),
                (
                    "shaikahan", 83, 1000, 80, 80, 25, 1, 1, "melee", 94,
                    (("Shaikahan bones", 1),),
                ),
                (
                    "frost_dragon", 166, 1600, 213, 213, 213, 213, 213,
                    "ranged", 250, (("Frost dragon bones", 1),),
                ),
            ],
        )
        enemies = bone_source_enemies_as_dict()
        self.assertEqual(enemies["frost_dragon"]["stats"], {
            "hitpoints": 1600,
            "attack": 213,
            "strength": 213,
            "defence": 213,
            "magic": 213,
            "ranged": 213,
        })
        self.assertEqual(enemies["frost_dragon"]["special_max_hits"]["dragonfire"], 500)
        self.assertEqual(enemies["zogre"]["quest_gate"], "zogre_flesh_eaters")
        self.assertEqual(enemies["zogre"]["quest_gate_state"], "started")
        self.assertEqual(
            enemies["zogre"]["quest_gate_label"],
            "Open Jiggig during Zogre Flesh Eaters",
        )
        self.assertEqual(
            enemies["zogre"]["location_context"],
            "Jiggig zogre area after the guard opens the barricade",
        )
        self.assertNotIn("quest_gate", enemies["jogre"])
        self.assertEqual(
            enemies["jogre"]["location_context"],
            "Karamja jungle and Pothole Dungeon",
        )
        self.assertEqual(
            enemies["jogre"]["access_status"],
            "ordinary Karamja access; no quest gate",
        )
        self.assertEqual(enemies["shaikahan"]["quest_gate"], "tai_bwo_wannai_trio")
        self.assertNotIn("quest_gate_state", enemies["shaikahan"])
        self.assertEqual(
            enemies["shaikahan"]["quest_gate_label"],
            "Complete Tai Bwo Wannai Trio",
        )
        self.assertEqual(enemies["shaikahan"]["location_context"], "Eastern Karamja jungle")
        self.assertEqual(
            enemies["shaikahan"]["start_equipment"],
            {
                "slot": "weapon",
                "items": ("Steel spear (kp)",),
                "persistent": True,
                "warning": (
                    "Equip a karambwan-poisoned spear to damage The Shaikahan"
                ),
                "source_status": (
                    "period-authentic continuous weapon gate; the live prerequisite "
                    "route uses cache-decoded Steel spear (kp)"
                ),
            },
        )
        self.assertTrue(set(enemies).issubset(COMBAT_ENEMY_DATA))

    def test_utilities_cover_burnt_collection_coffin_and_steel_spear(self):
        activities = bone_source_utility_activities_as_dict()
        self.assertEqual(
            activities["gather_burnt_bones"],
            {
                "display_name": "Collect burnt bones",
                "requirements": {},
                "output_item": "Burnt bones",
                "output_qty": 1,
                "batch_size": 1,
                "group": "gathering",
                "source": "https://runescape.wiki/w/Burnt_bones?oldid=6351913",
            },
        )
        coffin = activities["loot_ogre_coffin"]
        self.assertEqual(coffin["icon_item"], "Zogre bones")
        self.assertEqual(coffin["requirements"], {"Ogre coffin key": 1})
        self.assertEqual(
            [(row["item"], row["weight"]) for row in coffin["weighted_outputs"]],
            [("Zogre bones", 63), ("Fayrg bones", 14), ("Raurg bones", 6), ("Ourg bones", 3)],
        )
        self.assertEqual(coffin["non_bone_output_weight"], 39)
        self.assertEqual(sum(weight for _item, weight in COFFIN_OUTPUT_WEIGHTS), 125)
        spear_rows = {
            activity_id: spec
            for activity_id, spec in activities.items()
            if activity_id.startswith("poison_")
        }
        self.assertEqual(SHAIKAHAN_SPEARS, (("Steel", 3172),))
        self.assertEqual(set(spear_rows), {"poison_steel_spear_with_karambwan"})
        steel_spear = spear_rows["poison_steel_spear_with_karambwan"]
        self.assertEqual(
            {key: value for key, value in steel_spear.items() if key != "source"},
            {
                "display_name": "Poison steel spear with karambwan paste",
                "icon_item": "Steel spear",
                "requirements": {"Steel spear": 1, "Karambwan paste": 1},
                "output_item": "Steel spear (kp)",
                "output_qty": 1,
                "batch_size": 1,
                "group": "weapon_preparation",
            },
        )
        self.assertIn("WeaponPoison.java:64-72,156-192", steel_spear["source"])
        self.assertTrue(set(activities).issubset(UTILITY_ACTIVITY_DATA))
        self.assertEqual(
            UTILITY_ACTIVITY_DATA["poison_steel_spear_with_karambwan"]["surface"],
            UTILITY_SURFACE_ID,
        )

    def test_exact_item_metadata_is_merged_into_the_item_catalog(self):
        items = bone_source_extra_items_as_dict()
        expected_bone_metadata = {
            "Burnt bones": (528, 4.5),
            "Zogre bones": (4812, 22.5),
            "Jogre bones": (3125, 15.0),
            "Shaikahan bones": (3123, 25.0),
            "Fayrg bones": (4830, 84.0),
            "Raurg bones": (4832, 96.0),
            "Ourg bones": (4834, 140.0),
            "Frost dragon bones": (18832, 180.0),
        }
        self.assertEqual(
            {
                name: (items[name]["source_item_id"], items[name]["exp"])
                for name in expected_bone_metadata
            },
            expected_bone_metadata,
        )
        self.assertEqual(items["Ogre coffin key"]["source_item_id"], 4850)
        self.assertEqual(items["Steel spear (kp)"]["source_item_id"], 3172)
        self.assertFalse(items["Steel spear (kp)"]["tradeable"])
        self.assertIn("OpenRS2 cache rev 727 item 3172", items["Steel spear (kp)"]["source"])
        self.assertEqual(BONE_SOURCE_EXTRA_ITEM_DATA, items)
        self.assertTrue(set(items).issubset(EXTRA_ITEM_DATA))
        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for item_name, (source_item_id, _xp) in expected_bone_metadata.items():
            with self.subTest(item=item_name):
                self.assertEqual(definitions[item_name].source_item_id, source_item_id)
                self.assertFalse(definitions[item_name].stackable)
        self.assertEqual(definitions["Ogre coffin key"].source_item_id, 4850)
        self.assertEqual(definitions["Steel spear (kp)"].source_item_id, 3172)
        self.assertEqual(definitions["Steel spear (kp)"].equipment_slot, "weapon")
        self.assertFalse(definitions["Steel spear (kp)"].tradeable)

    def test_shaikahan_prerequisite_chain_produces_the_equipped_weapon(self):
        inventory = {"Raw karambwan": 1, "Steel spear": 1}

        inventory, exp, ok, processed = apply_utility_activity_pure(
            "grind_raw_karambwan", inventory, UTILITY_ACTIVITY_DATA
        )
        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(inventory["Karambwan paste"], 1)

        inventory, exp, ok, processed = apply_utility_activity_pure(
            "poison_steel_spear_with_karambwan",
            inventory,
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(
            inventory,
            {
                "Raw karambwan": 0,
                "Steel spear": 0,
                "Karambwan paste": 0,
                "Steel spear (kp)": 1,
            },
        )

    def test_zogre_requires_started_zogre_flesh_eaters_on_surface_and_kernel(self):
        player = {
            "current_combat_target": "zogre",
            "combat_encounter": {"target_id": "zogre", "enemy_lifepoints": 1},
            "inventory": {},
            "equipment": {},
        }
        expected = ("Open Jiggig during Zogre Flesh Eaters",)
        self.assertEqual(
            combat_target_locked_reasons_pure(player, "zogre", COMBAT_ENEMY_DATA),
            expected,
        )
        unchanged, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: 0.0,
            allow_bank_run=False,
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged, player)
        self.assertEqual(result["reason"], "combat_locked")
        self.assertEqual(result["locked_reasons"], expected)

        started = {
            **player,
            "quests": {"zogre_flesh_eaters": {"started": True, "completed": False}},
        }
        self.assertEqual(
            combat_target_locked_reasons_pure(started, "zogre", COMBAT_ENEMY_DATA),
            (),
        )
        completed = {
            **player,
            "quests": {"zogre_flesh_eaters": {"started": True, "completed": True}},
        }
        self.assertEqual(
            combat_target_locked_reasons_pure(completed, "zogre", COMBAT_ENEMY_DATA),
            (),
        )

    def test_shaikahan_requires_tai_bwo_wannai_completion_and_poisoned_spear(self):
        quest_warning = "Complete Tai Bwo Wannai Trio"
        weapon_warning = "Equip a karambwan-poisoned spear to damage The Shaikahan"
        base_player = {
            "current_combat_target": "shaikahan",
            "combat_encounter": {},
            "inventory": {"Steel spear (kp)": 1},
        }
        equipped_without_quest = {
            **base_player,
            "equipment": {"weapon": "Steel spear (kp)"},
        }
        self.assertEqual(
            combat_target_locked_reasons_pure(
                equipped_without_quest, "shaikahan", COMBAT_ENEMY_DATA
            ),
            (quest_warning,),
        )
        unchanged, ok, result = apply_combat_burst_pure(
            equipped_without_quest,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged, equipped_without_quest)
        self.assertEqual(result["reason"], "combat_locked")
        self.assertEqual(result["locked_reasons"], (quest_warning,))

        started_quest = {
            **base_player,
            "quests": {"tai_bwo_wannai_trio": {"started": True, "completed": False}},
            "equipment": {"weapon": "Steel spear (kp)"},
        }
        self.assertEqual(
            combat_target_locked_reasons_pure(
                started_quest, "shaikahan", COMBAT_ENEMY_DATA
            ),
            (quest_warning,),
        )

        completed_quest = {
            **base_player,
            "quests": {"tai_bwo_wannai_trio": {"started": True, "completed": True}},
        }
        for equipment in ({}, {"weapon": "Steel spear"}):
            with self.subTest(equipment=equipment):
                player = {**completed_quest, "equipment": equipment}
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        player, "shaikahan", COMBAT_ENEMY_DATA
                    ),
                    (weapon_warning,),
                )
                out, ok, result = apply_combat_burst_pure(
                    player,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                    ticks=1,
                )
                self.assertFalse(ok)
                self.assertEqual(out, player)
                self.assertEqual(result["reason"], "combat_locked")
                self.assertEqual(result["locked_reasons"], (weapon_warning,))

        equipped = {
            **completed_quest,
            "equipment": {"weapon": "Steel spear (kp)"},
        }
        self.assertEqual(
            combat_target_locked_reasons_pure(
                equipped, "shaikahan", COMBAT_ENEMY_DATA
            ),
            (),
        )

    def test_shaikahan_damage_requires_the_poisoned_spear_in_the_weapon_slot(self):
        warning = "Equip a karambwan-poisoned spear to damage The Shaikahan"
        base_player = {
            "current_combat_target": "shaikahan",
            "combat_encounter": {},
            "inventory": {"Steel spear (kp)": 1},
            "quests": {"tai_bwo_wannai_trio": {"started": True, "completed": True}},
        }

        for equipment in ({}, {"weapon": "Steel spear"}):
            with self.subTest(equipment=equipment):
                player = {**base_player, "equipment": equipment}
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        player, "shaikahan", COMBAT_ENEMY_DATA
                    ),
                    (warning,),
                )
                out, ok, result = apply_combat_burst_pure(
                    player,
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                    ticks=1,
                )
                self.assertFalse(ok)
                self.assertEqual(out, player)
                self.assertEqual(result["reason"], "combat_locked")
                self.assertEqual(result["locked_reasons"], (warning,))

        equipped = {
            **base_player,
            "equipment": {"weapon": "Steel spear (kp)"},
        }
        self.assertEqual(
            combat_target_locked_reasons_pure(
                equipped, "shaikahan", COMBAT_ENEMY_DATA
            ),
            (),
        )

    def test_every_source_is_pinned_before_the_cutoff(self):
        enemies = bone_source_enemies_as_dict()
        self.assertEqual(DARKAN_REV, "a2568b880390ef697b1b17e825fdef7868bed67f")
        self.assertIn("Zogre?oldid=6547569", enemies["zogre"]["source"])
        self.assertIn("Jogre?oldid=6240856", enemies["jogre"]["source"])
        self.assertIn("The_Shaikahan?oldid=6552714", enemies["shaikahan"]["source"])
        self.assertIn("Frost_dragon?oldid=6565911", enemies["frost_dragon"]["source"])
        self.assertIn(DARKAN_REV, enemies["frost_dragon"]["source"])
        self.assertEqual(
            COFFIN_OUTPUT_WEIGHTS,
            (("Zogre bones", 63), ("Fayrg bones", 14), ("Raurg bones", 6), ("Ourg bones", 3), (None, 39)),
        )


if __name__ == "__main__":
    unittest.main()
