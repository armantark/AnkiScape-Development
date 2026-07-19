import json
import unittest
from pathlib import Path

from combat_data import COMBAT_ENEMY_DATA
from logic_pure import combat_target_locked_reasons_pure


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
    "green_dragon",
    "harpie_bug_swarm",
    "ogre",
    "jackal",
    "icefiend",
    "pyrefiend",
    "jelly",
    "bloodveld",
    "infernal_mage",
    "dust_devil",
    "aberrant_spectre",
    "basilisk",
    "crocodile",
    "otherworldly_being",
    "jungle_horror",
    "shadow_warrior",
    "kalphite_soldier",
    "wall_beast",
    "vampyre",
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
    "poison_immune",
    "xp_multiplier",
    "protective_equipment",
    "start_equipment",
    "weakening_equipment",
    "bite",
    "finisher",
    "required_slayer_level",
    "environmental_hazard",
    "desert_context",
    "retaliation_stop_lifepoints",
    "regeneration",
    "source_status",
    "quest_gate",
    "quest_gate_label",
    "interaction_note",
    "wilderness_risk",
    "dragonfire",
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
                self.assertIn(
                    enemy["attack_style"],
                    {"melee", "magic", "ranged", "magic_melee"},
                )
                self.assertGreater(enemy["level"], 0)
                if "max_hit" in enemy:
                    self.assertIsInstance(enemy["max_hit"], int)
                    self.assertGreater(enemy["max_hit"], 0)
                if "poison_damage" in enemy:
                    self.assertIsInstance(enemy["poison_damage"], int)
                    self.assertGreater(enemy["poison_damage"], 0)
                if "poison_immune" in enemy:
                    self.assertIs(enemy["poison_immune"], True)
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
                if "start_equipment" in enemy:
                    requirement = enemy["start_equipment"]
                    self.assertEqual(
                        set(requirement),
                        {"slot", "items", "warning", "source_status"}
                        | ({"persistent"} if "persistent" in requirement else set()),
                    )
                    if "persistent" in requirement:
                        self.assertIs(requirement["persistent"], True)
                    self.assertIn(requirement["slot"], {"head", "shield", "neck"})
                    self.assertTrue(requirement["items"])
                    self.assertTrue(requirement["warning"])
                    self.assertTrue(requirement["source_status"])
                if "weakening_equipment" in enemy:
                    weakness = enemy["weakening_equipment"]
                    self.assertEqual(
                        set(weakness),
                        {
                            "slot",
                            "items",
                            "display_name",
                            "enemy_accuracy_multiplier",
                            "enemy_damage_multiplier",
                            "source_status",
                        },
                    )
                    self.assertIn(weakness["slot"], {"head", "shield", "neck"})
                    self.assertTrue(weakness["items"])
                    self.assertGreater(weakness["enemy_accuracy_multiplier"], 0.0)
                    self.assertLess(weakness["enemy_accuracy_multiplier"], 1.0)
                    self.assertGreater(weakness["enemy_damage_multiplier"], 0.0)
                    self.assertLess(weakness["enemy_damage_multiplier"], 1.0)
                    self.assertTrue(weakness["source_status"])
                if "bite" in enemy:
                    bite = enemy["bite"]
                    self.assertGreater(bite["chance_numerator"], 0)
                    self.assertGreaterEqual(
                        bite["chance_denominator"], bite["chance_numerator"]
                    )
                    self.assertGreater(bite["max_heal"], 0)
                    self.assertTrue(bite["stat_drain_skills"])
                    self.assertTrue(bite["source_status"])
                if "dragonfire" in enemy:
                    dragonfire = enemy["dragonfire"]
                    self.assertEqual(
                        set(dragonfire),
                        {
                            "chance_numerator",
                            "chance_denominator",
                            "unprotected_max_hit",
                            "partial_max_hit",
                            "shield_items",
                            "source",
                            "source_status",
                        },
                    )
                    self.assertGreater(dragonfire["chance_numerator"], 0)
                    self.assertGreaterEqual(
                        dragonfire["chance_denominator"],
                        dragonfire["chance_numerator"],
                    )
                    self.assertGreater(dragonfire["unprotected_max_hit"], 0)
                    self.assertGreater(dragonfire["partial_max_hit"], 0)
                    self.assertTrue(dragonfire["shield_items"])
                    self.assertTrue(dragonfire["source"])
                    self.assertTrue(dragonfire["source_status"])
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
            ("ogre", "Ogre.png"),
            ("icefiend", "Icefiend.png"),
            ("pyrefiend", "Pyrefiend.png"),
            ("jelly", "Jelly.png"),
            ("bloodveld", "Bloodveld.png"),
            ("infernal_mage", "Infernal Mage.png"),
            ("aberrant_spectre", "Aberrant spectre.png"),
            ("basilisk", "Basilisk.png"),
            ("crocodile", "Crocodile.png"),
            ("otherworldly_being", "Otherworldly being.png"),
            ("jungle_horror", "Jungle horror.png"),
            ("shadow_warrior", "Shadow warrior.png"),
            ("kalphite_soldier", "Kalphite Soldier.png"),
            ("wall_beast", "Wall beast icon.png"),
            ("vampyre", "Vampire (historical) (level 61).png"),
            ("gelatinous_abomination", "Gelatinous abomination icon.png"),
            ("young_grotworm", "Young grotworm.png"),
            ("monkey", "Karamja monkey.png"),
            ("desert_lizard", "Desert lizard (green).png"),
            ("rockslug", "Rock slug icon.png"),
            ("gargoyle", "Gargoyle icon.png"),
            ("mutated_zygomite_level_74", "Mutated zygomite icon.png"),
            ("mutated_zygomite_level_86", "Mutated zygomite icon.png"),
            ("green_dragon", "Green dragon.png"),
            ("harpie_bug_swarm", "Harpie Bugs Swarm.png"),
        ):
            with self.subTest(target=target_id):
                relative_path = f"combatenemies/{target_id}.png"
                self.assertTrue((root / relative_path).is_file())
                self.assertIn(relative_path, provenance)
                self.assertEqual(provenance[relative_path]["file_title"], file_title)

    def test_green_dragon_preserves_cutoff_combat_and_drop_selectors(self):
        dragon = COMBAT_ENEMY_DATA["green_dragon"]

        self.assertEqual(dragon["level"], 79)
        self.assertEqual(dragon["attack_speed"], 6)
        self.assertEqual(dragon["respawn_delay"], 59)
        self.assertEqual(dragon["max_hit"], 85)
        self.assertEqual(dragon["slayer_xp"], 75.0)
        self.assertEqual(
            dragon["stats"],
            {
                "hitpoints": 750,
                "attack": 68,
                "strength": 68,
                "defence": 68,
                "magic": 68,
                "ranged": 1,
            },
        )
        self.assertEqual(
            dragon["drops"]["guaranteed"],
            (("Dragon bones", 1), ("Green dragonhide", 1)),
        )
        main, tertiary = dragon["drops"]["tables"]
        self.assertEqual(main["total"], 1024)
        # The pinned emulator table itself overbooks its 1024 selector by five
        # slots. Preserve that source row instead of silently rewriting odds.
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1029)
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in tertiary["slots"]), 128)
        self.assertEqual(dragon["dragonfire"]["chance_numerator"], 1)
        self.assertEqual(dragon["dragonfire"]["chance_denominator"], 4)
        self.assertEqual(dragon["dragonfire"]["unprotected_max_hit"], 500)
        self.assertEqual(dragon["dragonfire"]["partial_max_hit"], 50)
        self.assertIn("provisional/darkan", dragon["dragonfire"]["source_status"])
        self.assertNotIn("charms", dragon["drops"])

    def test_ogre_preserves_the_cutoff_ordinary_variant_and_exact_seed_roll(self):
        ogre = COMBAT_ENEMY_DATA["ogre"]

        self.assertEqual(ogre["level"], 53)
        self.assertEqual(ogre["attack_style"], "melee")
        self.assertEqual(ogre["attack_speed"], 4)
        self.assertEqual(ogre["respawn_delay"], 59)
        self.assertEqual(ogre["slayer_xp"], 60.0)
        self.assertEqual(ogre["max_hit"], 73)
        self.assertEqual(
            ogre["stats"],
            {
                "hitpoints": 600,
                "attack": 43,
                "strength": 43,
                "defence": 43,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(ogre["drops"]["guaranteed"], (("Big bones", 1),))
        main, tertiary = ogre["drops"]["tables"]
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        seed_table = main["slots"][0]["table"]
        self.assertEqual(seed_table["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in seed_table["slots"]), 1000)
        self.assertEqual(tertiary["total"], 100000)
        self.assertEqual(sum(slot["slots"] for slot in tertiary["slots"]), 100000)
        self.assertIn("oldid=6565807", ogre["source"])

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

    def test_pyrefiend_preserves_the_cutoff_ordinary_variant_and_drop_table(self):
        pyrefiend = COMBAT_ENEMY_DATA["pyrefiend"]

        self.assertEqual(pyrefiend["level"], 43)
        self.assertEqual(pyrefiend["required_slayer_level"], 30)
        self.assertEqual(pyrefiend["attack_style"], "magic_melee")
        self.assertEqual(pyrefiend["slayer_xp"], 45.0)
        self.assertEqual(pyrefiend["max_hit"], 44)
        self.assertEqual(pyrefiend["stats"]["hitpoints"], 450)
        self.assertEqual(pyrefiend["stats"]["attack"], 52)
        self.assertEqual(pyrefiend["stats"]["strength"], 30)
        self.assertEqual(pyrefiend["stats"]["defence"], 22)
        self.assertEqual(
            pyrefiend["drops"]["guaranteed"],
            (("Impious ashes", 1),),
        )
        main = pyrefiend["drops"]["tables"][0]
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertIn("oldid=6565806", pyrefiend["source"])

    def test_slayer_targets_require_their_source_levels(self):
        for target_id, required_level in (
            ("pyrefiend", 30),
            ("basilisk", 40),
            ("infernal_mage", 45),
            ("bloodveld", 50),
            ("jelly", 52),
            ("aberrant_spectre", 60),
        ):
            with self.subTest(target_id=target_id):
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        {
                            "slayer_level": required_level - 1,
                            "quests": {
                                "priest_in_peril": {"completed": True}
                            },
                        },
                        target_id,
                        COMBAT_ENEMY_DATA,
                    ),
                    (f"Slayer level {required_level}",),
                )
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        {
                            "slayer_level": required_level,
                            "quests": {
                                "priest_in_peril": {"completed": True}
                            },
                        },
                        target_id,
                        COMBAT_ENEMY_DATA,
                    ),
                    (),
                )

    def test_jelly_preserves_the_cutoff_ordinary_variant_and_drop_table(self):
        jelly = COMBAT_ENEMY_DATA["jelly"]

        self.assertEqual(jelly["level"], 78)
        self.assertEqual(jelly["required_slayer_level"], 52)
        self.assertEqual(jelly["attack_style"], "magic_melee")
        self.assertEqual(jelly["attack_speed"], 6)
        self.assertEqual(jelly["respawn_delay"], 59)
        self.assertEqual(jelly["slayer_xp"], 75.0)
        self.assertEqual(jelly["max_hit"], 60)
        self.assertEqual(
            jelly["stats"],
            {
                "hitpoints": 750,
                "attack": 45,
                "strength": 45,
                "defence": 120,
                "magic": 45,
                "ranged": 1,
            },
        )
        self.assertEqual(jelly["drops"]["guaranteed"], ())
        main = jelly["drops"]["tables"][0]
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertIn("oldid=6530513", jelly["source"])
        self.assertIn("Soul Wars variant excluded", jelly["source_status"])

    def test_bloodveld_preserves_the_cutoff_level_76_variant_and_drop_table(self):
        bloodveld = COMBAT_ENEMY_DATA["bloodveld"]

        self.assertEqual(bloodveld["level"], 76)
        self.assertEqual(bloodveld["required_slayer_level"], 50)
        self.assertEqual(bloodveld["attack_style"], "magic_melee")
        self.assertEqual(bloodveld["attack_speed"], 6)
        self.assertEqual(bloodveld["respawn_delay"], 59)
        self.assertEqual(bloodveld["slayer_xp"], 120.0)
        self.assertEqual(bloodveld["max_hit"], 59)
        self.assertEqual(
            bloodveld["stats"],
            {
                "hitpoints": 1200,
                "attack": 75,
                "strength": 45,
                "defence": 30,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(bloodveld["drops"]["guaranteed"], (("Bones", 1),))
        main = bloodveld["drops"]["tables"][0]
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertIn("oldid=6565794", bloodveld["source"])
        self.assertIn("level-81 God Wars variant excluded", bloodveld["source_status"])

    def test_infernal_mage_preserves_the_cutoff_variant_and_drop_selector(self):
        mage = COMBAT_ENEMY_DATA["infernal_mage"]

        self.assertEqual(mage["level"], 66)
        self.assertEqual(mage["required_slayer_level"], 45)
        self.assertEqual(mage["attack_style"], "magic")
        self.assertEqual(mage["attack_speed"], 6)
        self.assertEqual(mage["respawn_delay"], 59)
        self.assertEqual(mage["slayer_xp"], 60.0)
        self.assertEqual(mage["max_hit"], 89)
        self.assertEqual(
            mage["stats"],
            {
                "hitpoints": 600,
                "attack": 1,
                "strength": 1,
                "defence": 60,
                "magic": 75,
                "ranged": 1,
            },
        )
        self.assertEqual(mage["drops"]["guaranteed"], (("Bones", 1),))
        (main,) = mage["drops"]["tables"]
        self.assertEqual(main["total"], 64000)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 64000)
        rare_slots = {
            slot.get("item"): slot["slots"]
            for slot in main["slots"]
            if slot.get("item")
            in {"Mystic boots (dark)", "Mystic hat (dark)", "Lava battlestaff"}
        }
        self.assertEqual(
            rare_slots,
            {
                "Mystic boots (dark)": 125,
                "Mystic hat (dark)": 125,
                "Lava battlestaff": 64,
            },
        )
        self.assertIn("oldid=6446423", mage["source"])
        self.assertIn("charm distribution remains source_blocked", mage["source_status"])

    def test_basilisk_preserves_the_cutoff_variant_and_drop_selector(self):
        basilisk = COMBAT_ENEMY_DATA["basilisk"]

        self.assertEqual(basilisk["level"], 61)
        self.assertEqual(basilisk["required_slayer_level"], 40)
        self.assertEqual(basilisk["attack_style"], "melee")
        self.assertEqual(basilisk["attack_speed"], 6)
        self.assertEqual(basilisk["respawn_delay"], 59)
        self.assertEqual(basilisk["slayer_xp"], 75.0)
        self.assertEqual(basilisk["max_hit"], 59)
        self.assertEqual(basilisk["stats"]["hitpoints"], 750)
        self.assertEqual(basilisk["drops"]["guaranteed"], (("Bones", 1),))
        (main,) = basilisk["drops"]["tables"]
        self.assertEqual(main["total"], 64000)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 64000)
        rare_slots = {
            slot.get("item"): slot["slots"]
            for slot in main["slots"]
            if slot.get("item") in {"Mystic hat (light)", "Basilisk head"}
        }
        self.assertEqual(
            rare_slots,
            {"Mystic hat (light)": 125, "Basilisk head": 32},
        )
        self.assertTrue(
            basilisk["protective_equipment"]["unprotected_effect"][
                "protection_prayer_applies"
            ]
        )
        self.assertIn("oldid=6565796", basilisk["source"])
        self.assertIn(
            "charm distribution remains source_blocked", basilisk["source_status"]
        )

    def test_aberrant_spectre_preserves_stench_and_exact_tables(self):
        spectre = COMBAT_ENEMY_DATA["aberrant_spectre"]

        self.assertEqual(spectre["level"], 96)
        self.assertEqual(spectre["required_slayer_level"], 60)
        self.assertEqual(spectre["quest_gate"], "priest_in_peril")
        self.assertEqual(spectre["attack_style"], "magic")
        self.assertEqual(spectre["attack_speed"], 6)
        self.assertEqual(spectre["respawn_delay"], 59)
        self.assertEqual(spectre["slayer_xp"], 90.0)
        self.assertEqual(spectre["max_hit"], 119)
        self.assertEqual(spectre["stats"]["hitpoints"], 900)
        self.assertEqual(spectre["drops"]["guaranteed"], ())
        self.assertEqual(len(spectre["drops"]["tables"]), 2)
        for table in spectre["drops"]["tables"]:
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]), table["total"]
            )
        effect = spectre["protective_equipment"]["unprotected_effect"]
        self.assertEqual(effect["damage"]["cap"], 160)
        self.assertEqual(effect["stat_drain_protection_prayer"], "protect_magic")
        self.assertEqual(effect["stat_drain"]["floor"], 0)
        main, charms = spectre["drops"]["tables"]
        self.assertEqual(main["total"], 512)
        self.assertEqual(main["slots"][-1], {"slots": 71})
        self.assertEqual(
            charms["slots"][:4],
            (
                {"item": "Gold charm", "quantity": 1, "slots": 97},
                {"item": "Green charm", "quantity": 1, "slots": 25},
                {"item": "Crimson charm", "quantity": 1, "slots": 15},
                {"item": "Blue charm", "quantity": 1, "slots": 19},
            ),
        )
        self.assertIn("oldid=6555339", spectre["source"])
        self.assertIn("exact 512-slot ordinary selector", spectre["source_status"])

    def test_dust_devil_preserves_cutoff_damage_gate_and_exact_selectors(self):
        devil = COMBAT_ENEMY_DATA["dust_devil"]

        self.assertEqual(devil["level"], 93)
        self.assertEqual(devil["required_slayer_level"], 65)
        self.assertEqual(devil["attack_style"], "melee")
        self.assertEqual(devil["attack_speed"], 6)
        self.assertEqual(devil["respawn_delay"], 59)
        self.assertEqual(devil["slayer_xp"], 105.0)
        self.assertEqual(devil["max_hit"], 90)
        self.assertEqual(
            devil["stats"],
            {
                "hitpoints": 1050,
                "attack": 105,
                "strength": 70,
                "defence": 40,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(devil["drops"]["guaranteed"], (("Bones", 1),))
        main, charms = devil["drops"]["tables"]
        self.assertEqual(main["total"], 32768)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 32768)
        self.assertEqual(main["slots"][-2]["item"], "Dragon chainbody")
        self.assertEqual(main["slots"][-2]["slots"], 1)
        self.assertEqual(main["slots"][-1], {"slots": 255})
        self.assertEqual(charms["total"], 606)
        self.assertEqual(
            tuple(slot["slots"] for slot in charms["slots"]),
            (31, 13, 115, 3, 444),
        )
        self.assertTrue(devil["start_equipment"]["persistent"])
        self.assertIn("Face mask", devil["start_equipment"]["items"])
        self.assertIn("Masked earmuffs", devil["start_equipment"]["items"])
        self.assertIn("oldid=6529409", devil["source"])

    def test_crocodile_preserves_the_level_63_desert_variant(self):
        crocodile = COMBAT_ENEMY_DATA["crocodile"]

        self.assertEqual(crocodile["level"], 63)
        self.assertEqual(crocodile["required_slayer_level"], 10)
        self.assertEqual(crocodile["attack_style"], "melee")
        self.assertEqual(crocodile["attack_speed"], 5)
        self.assertEqual(crocodile["respawn_delay"], 59)
        self.assertEqual(crocodile["slayer_xp"], 62.0)
        self.assertEqual(crocodile["max_hit"], 67)
        self.assertEqual(
            crocodile["stats"],
            {
                "hitpoints": 630,
                "attack": 53,
                "strength": 54,
                "defence": 54,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(crocodile["drops"], {
            "guaranteed": (("Bones", 1),),
            "tables": (),
        })
        self.assertEqual(
            crocodile["environmental_hazard"]["display_name"], "Desert heat"
        )
        self.assertTrue(crocodile["desert_context"])
        self.assertIn("oldid=6529105", crocodile["source"])
        self.assertIn("level-89 marsh variant", crocodile["source_status"])

    def test_otherworldly_being_preserves_zanaris_identity_and_exact_table(self):
        being = COMBAT_ENEMY_DATA["otherworldly_being"]

        self.assertEqual(being["level"], 64)
        self.assertEqual(being["required_slayer_level"], 1)
        self.assertEqual(being["quest_gate"], "lost_city")
        self.assertEqual(being["attack_style"], "melee")
        self.assertEqual(being["attack_speed"], 6)
        self.assertEqual(being["respawn_delay"], 59)
        self.assertEqual(being["slayer_xp"], 66.0)
        self.assertEqual(being["max_hit"], 70)
        self.assertEqual(
            being["stats"],
            {
                "hitpoints": 660,
                "attack": 56,
                "strength": 56,
                "defence": 46,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(being["drops"]["guaranteed"], ())
        main = being["drops"]["tables"][0]
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertIn("oldid=6554205", being["source"])

    def test_jungle_horror_preserves_route_identity_and_drop_selector(self):
        horror = COMBAT_ENEMY_DATA["jungle_horror"]

        self.assertEqual(horror["level"], 70)
        self.assertEqual(horror["required_slayer_level"], 1)
        self.assertEqual(horror["quest_gate"], "cabin_fever")
        self.assertEqual(horror["attack_style"], "melee")
        self.assertEqual(horror["attack_speed"], 6)
        self.assertEqual(horror["respawn_delay"], 59)
        self.assertEqual(horror["slayer_xp"], 45.0)
        self.assertEqual(horror["max_hit"], 84)
        self.assertEqual(
            horror["stats"],
            {
                "hitpoints": 450,
                "attack": 70,
                "strength": 70,
                "defence": 55,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(horror["drops"]["guaranteed"], (("Bones", 1),))
        (main,) = horror["drops"]["tables"]
        self.assertEqual(main["total"], 100000)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 100000)
        self.assertEqual(main["slots"][-1], {"slots": 142})
        self.assertIn("oldid=6534099", horror["source"])

    def test_shadow_warrior_preserves_route_identity_and_drop_selectors(self):
        warrior = COMBAT_ENEMY_DATA["shadow_warrior"]

        self.assertEqual(warrior["level"], 48)
        self.assertEqual(warrior["required_slayer_level"], 1)
        self.assertEqual(warrior["quest_gate"], "legends_quest")
        self.assertEqual(warrior["attack_style"], "melee")
        self.assertEqual(warrior["attack_speed"], 6)
        self.assertEqual(warrior["respawn_delay"], 59)
        self.assertEqual(warrior["slayer_xp"], 67.0)
        self.assertEqual(warrior["max_hit"], 65)
        self.assertEqual(
            warrior["stats"],
            {
                "hitpoints": 670,
                "attack": 36,
                "strength": 36,
                "defence": 33,
                "magic": 0,
                "ranged": 0,
            },
        )
        self.assertEqual(warrior["drops"]["guaranteed"], ())
        ordinary_table, charm_table = warrior["drops"]["tables"]
        self.assertEqual(ordinary_table["total"], 128)
        self.assertEqual(
            sum(slot["slots"] for slot in ordinary_table["slots"]), 128
        )
        self.assertEqual(ordinary_table["slots"][-1], {"slots": 22})
        self.assertEqual(charm_table["total"], 606)
        self.assertEqual(
            tuple(slot.get("slots") for slot in charm_table["slots"]),
            (26, 11, 44, 3, 522),
        )
        self.assertIn("oldid=6555920", warrior["source"])

    def test_kalphite_soldier_preserves_the_cutoff_variant_and_drop_table(self):
        soldier = COMBAT_ENEMY_DATA["kalphite_soldier"]

        self.assertEqual(soldier["level"], 85)
        self.assertEqual(soldier["attack_style"], "melee")
        self.assertEqual(soldier["attack_speed"], 6)
        self.assertEqual(soldier["respawn_delay"], 59)
        self.assertEqual(soldier["slayer_xp"], 90.0)
        self.assertEqual(soldier["max_hit"], 80)
        self.assertEqual(soldier["poison_damage"], 5)
        self.assertIn("nearest representable 50-LP", soldier["source_status"])
        self.assertEqual(
            soldier["stats"],
            {
                "hitpoints": 900,
                "attack": 70,
                "strength": 70,
                "defence": 70,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(soldier["drops"]["guaranteed"], ())
        main = soldier["drops"]["tables"][0]
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 128)
        self.assertIn("oldid=6565809", soldier["source"])

    def test_wall_beast_preserves_the_cutoff_variant_and_drop_table(self):
        wall_beast = COMBAT_ENEMY_DATA["wall_beast"]

        self.assertEqual(wall_beast["level"], 49)
        self.assertEqual(wall_beast["required_slayer_level"], 35)
        self.assertEqual(wall_beast["attack_style"], "melee")
        self.assertEqual(wall_beast["attack_speed"], 4)
        self.assertEqual(wall_beast["respawn_delay"], 39)
        self.assertEqual(wall_beast["slayer_xp"], 105.0)
        self.assertEqual(wall_beast["max_hit"], 44)
        self.assertIs(wall_beast["poison_immune"], True)
        self.assertEqual(
            wall_beast["stats"],
            {
                "hitpoints": 1050,
                "attack": 30,
                "strength": 30,
                "defence": 16,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(
            wall_beast["start_equipment"],
            {
                "slot": "head",
                "items": ("Spiny helmet",),
                "warning": "Equip a Spiny helmet to start fighting Wall beasts",
                "source_status": (
                    "period-exact start-only helmet gate; other equivalent helmets "
                    "remain excluded until their equipment identities are live"
                ),
            },
        )
        self.assertEqual(wall_beast["drops"]["guaranteed"], ())
        main = wall_beast["drops"]["tables"][0]
        self.assertEqual(main["total"], 100000)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 100000)
        self.assertIn("oldid=6079584", wall_beast["source"])

    def test_vampyre_preserves_the_cutoff_variant_and_lossless_drop_table(self):
        vampyre = COMBAT_ENEMY_DATA["vampyre"]

        self.assertEqual(vampyre["level"], 61)
        self.assertEqual(vampyre["attack_style"], "melee")
        self.assertEqual(vampyre["attack_speed"], 6)
        self.assertEqual(vampyre["respawn_delay"], 59)
        self.assertEqual(vampyre["slayer_xp"], 40.0)
        self.assertEqual(vampyre["max_hit"], 74)
        self.assertEqual(vampyre["quest_gate"], "priest_in_peril")
        self.assertEqual(
            vampyre["stats"],
            {
                "hitpoints": 400,
                "attack": 55,
                "strength": 60,
                "defence": 55,
                "magic": 0,
                "ranged": 0,
            },
        )
        self.assertEqual(vampyre["drops"]["guaranteed"], (("Vampyre dust", 1),))
        main = vampyre["drops"]["tables"][0]
        self.assertEqual(main["total"], 100000)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 100000)
        self.assertEqual(main["slots"][-1], {"slots": 167})
        self.assertEqual(
            vampyre["weakening_equipment"]["items"], ("Holy symbol",)
        )
        self.assertEqual(vampyre["bite"]["chance_denominator"], 8)
        self.assertIn("oldid=6545273", vampyre["source"])

    def test_young_grotworm_uses_one_exact_darkan_selector(self):
        grotworm = COMBAT_ENEMY_DATA["young_grotworm"]

        self.assertEqual(grotworm["drops"]["guaranteed"], (("Bones", 1),))
        (main,) = grotworm["drops"]["tables"]
        self.assertEqual(main["total"], 50000)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 50000)
        self.assertEqual(main["slots"][-1], {"slots": 4})

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
        (main,) = lizard["drops"]["tables"]
        self.assertEqual(main["total"], 100000)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 100000)
        self.assertEqual(main["slots"][-1], {"slots": 19})

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
        main, charms = rockslug["drops"]["tables"]
        self.assertEqual(main["total"], 100000)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 100000)
        self.assertEqual(main["slots"][-1], {"slots": 7})
        self.assertEqual(charms["total"], 1000)

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
        main, charms = gargoyle["drops"]["tables"]
        self.assertEqual(main["total"], 512)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 512)
        self.assertEqual(main["slots"][-1], {"slots": 1})
        self.assertEqual(charms["total"], 1000)

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
                fungicide, main = zygomite["drops"]["tables"]
                self.assertEqual(fungicide["name"], "Period-common abstraction: Fungicide")
                self.assertEqual(main["total"], 100000)
                self.assertEqual(
                    sum(slot["slots"] for slot in main["slots"]), 100000
                )
                self.assertEqual(main["slots"][-1], {"slots": 20})
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
