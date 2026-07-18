import json
import unittest
from pathlib import Path

from combat_data import COMBAT_ENEMY_DATA


NEW_COMBAT_ENEMIES = (
    "baby_dragon",
    "baby_black_dragon",
    "lesser_demon",
    "greater_demon",
    "black_demon",
    "abyssal_demon",
    "nechryael",
    "death_spawn",
    "hellhound",
    "rock_crab",
    "ghoul",
    "werewolf",
    "ice_warrior",
    "earth_warrior",
    "jackal",
    "icefiend",
    "gelatinous_abomination",
    "young_grotworm",
    "monkey",
    "desert_lizard",
    "rockslug",
    "gargoyle",
    "mutated_zygomite_level_74",
    "mutated_zygomite_level_86",
    "banshee",
    "shade",
    "ghost_level_77",
    "cave_crawler",
    "cockatrice",
    "cave_bug",
    "cave_slime",
    "flesh_crawler_level_28",
    "flesh_crawler_level_35",
    "flesh_crawler_level_41",
    "crawling_hand",
    "ankou_level_75",
    "ankou_level_82",
    "ankou_level_86",
    "catablepon_level_49",
    "catablepon_level_64",
    "catablepon_level_68",
    "minotaur_level_12",
    "minotaur_level_27",
    "cave_goblin",
    "canifis_citizen",
    "tzhaar_hur",
)

REQUIRED_ENEMY_KEYS = {
    "display_name",
    "level",
    "group",
    "attack_style",
    "attack_speed",
    "respawn_delay",
    "slayer_xp",
    "stats",
    "bonuses",
    "drops",
    "source",
}

OPTIONAL_ENEMY_KEYS = {
    "max_hit",
    "poison_damage",
    "xp_multiplier",
    "protective_equipment",
    "finisher",
    "required_slayer_level",
    "environmental_hazard",
    "retaliation_stop_lifepoints",
    "regeneration",
    "source_status",
    "quest_gate",
    "quest_gate_label",
    "interaction_note",
}

REQUIRED_STAT_KEYS = {"hitpoints", "attack", "strength", "defence", "magic", "ranged"}

REQUIRED_BONUS_KEYS = {
    "attack_stab",
    "attack_slash",
    "attack_crush",
    "defence_stab",
    "defence_slash",
    "defence_crush",
    "defence_magic",
    "defence_ranged",
    "melee_strength",
}


class CombatEnemyRosterDataTest(unittest.TestCase):
    def test_no_enemy_id_collides_with_a_skilling_target_id(self):
        # carried_inventory is keyed by target id, and combat targets and skilling
        # targets share that one namespace. A collision would make a combat bank run
        # wipe a skilling pack's view, and a combat death drop that skill's carried
        # materials. There is no collision today; this keeps it that way loudly.
        from constants import (
            ORE_DATA, TREE_DATA, FISHING_DATA, HUNTER_DATA, COOKING_DATA, CRAFTING_DATA,
            FLETCHING_DATA, FIREMAKING_DATA, SMITHING_DATA, RUNECRAFTING_DATA,
        )

        skilling_ids = set()
        for table in (ORE_DATA, TREE_DATA, FISHING_DATA, HUNTER_DATA, COOKING_DATA,
                      CRAFTING_DATA, FLETCHING_DATA, FIREMAKING_DATA, SMITHING_DATA,
                      RUNECRAFTING_DATA):
            skilling_ids |= set(table)

        self.assertEqual(set(COMBAT_ENEMY_DATA) & skilling_ids, set())


    def test_new_enemies_have_required_schema(self):
        for enemy_name in NEW_COMBAT_ENEMIES:
            with self.subTest(enemy=enemy_name):
                enemy = COMBAT_ENEMY_DATA[enemy_name]

                self.assertEqual(set(enemy) - OPTIONAL_ENEMY_KEYS, REQUIRED_ENEMY_KEYS)
                self.assertEqual(set(enemy) - REQUIRED_ENEMY_KEYS, set(enemy) & OPTIONAL_ENEMY_KEYS)
                self.assertEqual(set(enemy["stats"]), REQUIRED_STAT_KEYS)
                self.assertEqual(set(enemy["bonuses"]), REQUIRED_BONUS_KEYS)
                self.assertIn(enemy["attack_style"], {"melee", "magic", "ranged"})
                self.assertGreater(enemy["level"], 0)
                if "max_hit" in enemy:
                    self.assertIsInstance(enemy["max_hit"], int)
                    self.assertGreater(enemy["max_hit"], 0)
                if "poison_damage" in enemy:
                    self.assertIsInstance(enemy["poison_damage"], int)
                    self.assertGreater(enemy["poison_damage"], 0)
                if "xp_multiplier" in enemy:
                    self.assertIsInstance(enemy["xp_multiplier"], float)
                    self.assertGreater(enemy["xp_multiplier"], 0.0)
                if "protective_equipment" in enemy:
                    protection = enemy["protective_equipment"]
                    self.assertEqual(
                        set(protection),
                        {"slot", "items", "warning", "unprotected_effect", "source_status"},
                    )
                    self.assertIn(protection["slot"], {"head", "shield", "neck"})
                    self.assertTrue(protection["items"])
                    self.assertTrue(protection["warning"])
                    self.assertTrue(protection["unprotected_effect"])
                    self.assertTrue(protection["source_status"])
                if "finisher" in enemy:
                    finisher = enemy["finisher"]
                    required_finisher_keys = {
                        "item",
                        "threshold_lifepoints",
                        "consume",
                        "action_label",
                        "source_status",
                    }
                    self.assertTrue(required_finisher_keys <= set(finisher))
                    self.assertTrue(
                        {"quick_unlock_key", "must_be_worn"} & set(finisher)
                    )
                    self.assertTrue(finisher["item"])
                    self.assertGreater(finisher["threshold_lifepoints"], 0)
                    self.assertIsInstance(finisher["consume"], bool)
                    self.assertTrue(finisher["action_label"])
                    if "quick_unlock_key" in finisher:
                        self.assertTrue(finisher["quick_unlock_key"])
                    if "must_be_worn" in finisher:
                        self.assertTrue(finisher["must_be_worn"])
                    self.assertTrue(finisher["source_status"])
                if "required_slayer_level" in enemy:
                    self.assertIsInstance(enemy["required_slayer_level"], int)
                    self.assertGreater(enemy["required_slayer_level"], 0)
                if "environmental_hazard" in enemy:
                    hazard = enemy["environmental_hazard"]
                    self.assertEqual(
                        set(hazard),
                        {
                            "display_name",
                            "dose_items",
                            "empty_item",
                            "reviews_per_dose",
                            "loadout_cap",
                            "source_status",
                        },
                    )
                    self.assertTrue(hazard["dose_items"])
                    self.assertGreater(hazard["reviews_per_dose"], 0)
                    self.assertGreater(hazard["loadout_cap"], 0)
                    self.assertTrue(hazard["source_status"])
                self.assertGreater(enemy["stats"]["hitpoints"], 0)

    def test_jackal_preserves_the_cutoff_dogs_family_combat_row(self):
        jackal = COMBAT_ENEMY_DATA["jackal"]

        self.assertEqual(jackal["level"], 21)
        self.assertEqual(jackal["slayer_xp"], 27.0)
        self.assertEqual(jackal["max_hit"], 80)
        self.assertEqual(jackal["stats"]["hitpoints"], 270)
        self.assertEqual(jackal["stats"]["attack"], 17)
        self.assertEqual(jackal["stats"]["strength"], 18)
        self.assertEqual(jackal["stats"]["defence"], 15)
        self.assertEqual(jackal["drops"]["guaranteed"], (("Bones", 1),))
        self.assertIn("oldid=6493724", jackal["source"])

    def test_new_slayer_family_assets_are_present_and_provenanced(self):
        root = Path(__file__).resolve().parents[1]
        provenance = json.loads(
            (root / "assets_provenance.json").read_text(encoding="utf-8")
        )

        for target_id, file_title in (
            ("jackal", "Jackal.png"),
            ("icefiend", "Icefiend.png"),
            ("gelatinous_abomination", "Gelatinous abomination icon.png"),
            ("young_grotworm", "Young grotworm.png"),
            ("monkey", "Karamja monkey.png"),
            ("desert_lizard", "Desert lizard (green).png"),
            ("rockslug", "Rock slug icon.png"),
            ("gargoyle", "Gargoyle icon.png"),
            ("mutated_zygomite_level_74", "Mutated zygomite icon.png"),
            ("mutated_zygomite_level_86", "Mutated zygomite icon.png"),
        ):
            with self.subTest(target=target_id):
                relative_path = f"combatenemies/{target_id}.png"
                self.assertTrue((root / relative_path).is_file())
                self.assertIn(relative_path, provenance)
                self.assertEqual(provenance[relative_path]["file_title"], file_title)

    def test_icefiend_preserves_the_cutoff_ordinary_variant(self):
        icefiend = COMBAT_ENEMY_DATA["icefiend"]

        self.assertEqual(icefiend["level"], 13)
        self.assertEqual(icefiend["attack_style"], "melee")
        self.assertEqual(icefiend["slayer_xp"], 15.0)
        self.assertEqual(icefiend["max_hit"], 20)
        self.assertEqual(icefiend["stats"]["hitpoints"], 150)
        self.assertEqual(icefiend["stats"]["attack"], 10)
        self.assertEqual(icefiend["stats"]["strength"], 10)
        self.assertEqual(icefiend["stats"]["defence"], 12)
        self.assertEqual(
            icefiend["drops"]["guaranteed"],
            (("Impious ashes", 1),),
        )
        main = icefiend["drops"]["tables"][0]
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertIn("oldid=6419875", icefiend["source"])

    def test_desert_lizard_preserves_the_period_finisher_variant(self):
        lizard = COMBAT_ENEMY_DATA["desert_lizard"]

        self.assertEqual(lizard["level"], 24)
        self.assertEqual(lizard["required_slayer_level"], 22)
        self.assertEqual(lizard["slayer_xp"], 25.0)
        self.assertEqual(lizard["max_hit"], 40)
        self.assertEqual(lizard["attack_speed"], 6)
        self.assertEqual(lizard["respawn_delay"], 59)
        self.assertEqual(
            lizard["stats"],
            {
                "hitpoints": 250,
                "attack": 20,
                "strength": 22,
                "defence": 20,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(lizard["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(
            lizard["finisher"],
            {
                "item": "Ice cooler",
                "threshold_lifepoints": 30,
                "consume": True,
                "action_label": "Use Ice cooler",
                "quick_unlock_key": "slayer_quick_finishers_unlocked",
                "source_status": (
                    "period-exact threshold/item/consumption; Darkan ConditionalDeath "
                    "confirms the same item-gated death family"
                ),
            },
        )
        self.assertEqual(
            lizard["environmental_hazard"],
            {
                "display_name": "Desert heat",
                "dose_items": (
                    "Waterskin (4)",
                    "Waterskin (3)",
                    "Waterskin (2)",
                    "Waterskin (1)",
                ),
                "empty_item": "Waterskin (0)",
                "reviews_per_dose": 1,
                "loadout_cap": 8,
                "source_status": (
                    "period-exact water requirement and dose preservation; one dose "
                    "per damaging Combat review is a bounded review-native abstraction"
                ),
            },
        )
        self.assertIn("oldid=6548273", lizard["source"])
        self.assertEqual(len(lizard["drops"]["tables"]), 31)
        self.assertTrue(
            all(table["total"] == 100000 for table in lizard["drops"]["tables"])
        )

    def test_rockslug_preserves_the_period_finisher_and_frozen_state(self):
        rockslug = COMBAT_ENEMY_DATA["rockslug"]

        self.assertEqual(rockslug["level"], 29)
        self.assertEqual(rockslug["required_slayer_level"], 20)
        self.assertEqual(rockslug["max_hit"], 41)
        self.assertEqual(rockslug["slayer_xp"], 27.0)
        self.assertEqual(rockslug["retaliation_stop_lifepoints"], 10)
        self.assertEqual(
            rockslug["stats"],
            {
                "hitpoints": 270,
                "attack": 22,
                "strength": 27,
                "defence": 27,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(
            rockslug["finisher"]["item"],
            "Bag of salt",
        )
        self.assertEqual(rockslug["finisher"]["threshold_lifepoints"], 39)
        self.assertTrue(rockslug["finisher"]["consume"])
        self.assertIn("oldid=6530509", rockslug["source"])
        self.assertEqual(len(rockslug["drops"]["tables"]), 21)

    def test_gargoyle_preserves_the_period_reusable_finisher_and_regeneration(self):
        gargoyle = COMBAT_ENEMY_DATA["gargoyle"]

        self.assertEqual(gargoyle["level"], 111)
        self.assertEqual(gargoyle["required_slayer_level"], 75)
        self.assertEqual(gargoyle["attack_speed"], 6)
        self.assertEqual(gargoyle["max_hit"], 119)
        self.assertEqual(gargoyle["slayer_xp"], 105.0)
        self.assertEqual(
            gargoyle["regeneration"],
            {
                "lifepoints_per_tick_numerator": 12,
                "lifepoints_per_tick_denominator": 5,
                "source_status": (
                    "period page reports roughly 20 LP per five seconds; expressed "
                    "as the exact equivalent 12/5 LP per 0.6-second gameplay tick"
                ),
            },
        )
        self.assertEqual(gargoyle["finisher"]["item"], "Rock hammer")
        self.assertEqual(gargoyle["finisher"]["threshold_lifepoints"], 89)
        self.assertFalse(gargoyle["finisher"]["consume"])
        self.assertNotIn(
            "Ferocious ring (5)",
            {
                slot.get("item")
                for table in gargoyle["drops"]["tables"]
                for slot in table["slots"]
            },
        )
        self.assertIn("oldid=6579781", gargoyle["source"])
        self.assertEqual(len(gargoyle["drops"]["tables"]), 23)

    def test_mutated_zygomites_preserve_period_variants_and_charged_finisher(self):
        expected = {
            "mutated_zygomite_level_74": (74, 650, 65, 65.0),
            "mutated_zygomite_level_86": (86, 750, 75, 75.0),
        }
        for target_id, (level, lifepoints, combat_stat, slayer_xp) in expected.items():
            with self.subTest(target=target_id):
                zygomite = COMBAT_ENEMY_DATA[target_id]
                self.assertEqual(zygomite["level"], level)
                self.assertEqual(zygomite["required_slayer_level"], 57)
                self.assertEqual(zygomite["quest_gate"], "lost_city")
                self.assertEqual(zygomite["quest_gate_label"], "Complete Lost City")
                self.assertEqual(zygomite["stats"]["hitpoints"], lifepoints)
                for stat in ("attack", "strength", "defence", "magic", "ranged"):
                    self.assertEqual(zygomite["stats"][stat], combat_stat)
                self.assertEqual(zygomite["slayer_xp"], slayer_xp)
                self.assertEqual(zygomite["max_hit"], 88)
                self.assertEqual(zygomite["drops"]["guaranteed"], (("Ashes", 1),))
                fungicide = zygomite["drops"]["tables"][0]
                self.assertEqual(fungicide["name"], "Period-common abstraction: Fungicide")
                self.assertEqual(fungicide["total"], 8)
                self.assertEqual(
                    fungicide["slots"],
                    (
                        {"item": "Fungicide", "quantity": 1, "slots": 1},
                        {"slots": 7},
                    ),
                )
                self.assertIn("oldid=6530349", zygomite["source"])
                self.assertIn("source_blocked", zygomite["source_status"])

                finisher = zygomite["finisher"]
                self.assertEqual(finisher["item"], "Fungicide spray 10")
                self.assertEqual(finisher["display_item"], "Fungicide spray")
                self.assertEqual(finisher["threshold_lifepoints"], 19)
                self.assertTrue(finisher["consume"])
                self.assertEqual(
                    finisher["charge_items"],
                    tuple(
                        (f"Fungicide spray {charges}", charges)
                        for charges in range(10, 0, -1)
                    ),
                )
                self.assertEqual(finisher["empty_item"], "Fungicide spray 0")
                self.assertEqual(finisher["reload_item"], "Fungicide")
                self.assertEqual(finisher["reload_charges"], 10)

    def test_new_enemy_drops_are_well_formed(self):
        for enemy_name in NEW_COMBAT_ENEMIES:
            with self.subTest(enemy=enemy_name):
                drops = COMBAT_ENEMY_DATA[enemy_name]["drops"]

                self.assertEqual(set(drops), {"guaranteed", "tables"})
                for drop in drops["guaranteed"]:
                    self.assertEqual(len(drop), 2)
                    self.assertIsInstance(drop[0], str)
                    self.assertIsInstance(drop[1], int)
                    self.assertGreater(drop[1], 0)

                for table in drops["tables"]:
                    self.assertIn("name", table)
                    self.assertIn("total", table)
                    self.assertIn("slots", table)
                    self.assertIsInstance(table["total"], int)
                    self.assertGreater(table["total"], 0)
                    self._assert_slots_well_formed(table["slots"])

    def _assert_slots_well_formed(self, slots):
        for slot in slots:
            self.assertIn("slots", slot)
            self.assertIsInstance(slot["slots"], int)
            self.assertGreater(slot["slots"], 0)
            if "item" in slot:
                self.assertIsInstance(slot["item"], str)
                quantity_fields = {
                    field
                    for field in ("quantity", "quantity_range", "quantity_choices")
                    if field in slot
                }
                self.assertEqual(len(quantity_fields), 1)
                if "quantity" in slot:
                    self.assertIsInstance(slot["quantity"], int)
                    self.assertGreater(slot["quantity"], 0)
                if "quantity_range" in slot:
                    self.assertEqual(len(slot["quantity_range"]), 2)
                    self.assertLessEqual(slot["quantity_range"][0], slot["quantity_range"][1])
                if "quantity_choices" in slot:
                    self.assertTrue(slot["quantity_choices"])
                    self.assertTrue(
                        all(
                            isinstance(quantity, int) and quantity > 0
                            for quantity in slot["quantity_choices"]
                        )
                    )
            if "table" in slot:
                self.assertIn("name", slot["table"])
                self.assertIn("total", slot["table"])
                self.assertIn("slots", slot["table"])


if __name__ == "__main__":
    unittest.main()
