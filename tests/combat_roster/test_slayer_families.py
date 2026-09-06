import unittest

from .contract import COMBAT_ENEMY_DATA


class CombatEnemyRosterDataTest(unittest.TestCase):
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

    def test_fire_giant_preserves_the_cutoff_ordinary_variant_and_selectors(self):
        giant = COMBAT_ENEMY_DATA["fire_giant"]

        self.assertEqual(giant["level"], 86)
        self.assertEqual(giant["attack_style"], "melee")
        self.assertEqual(giant["attack_speed"], 5)
        self.assertEqual(giant["respawn_delay"], 59)
        self.assertEqual(giant["max_hit"], 116)
        self.assertEqual(giant["slayer_xp"], 111.0)
        self.assertEqual(
            giant["stats"],
            {
                "hitpoints": 1110,
                "attack": 65,
                "strength": 65,
                "defence": 65,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(giant["drops"]["guaranteed"], (("Big bones", 1),))
        self.assertEqual(
            [(table["name"], table["total"]) for table in giant["drops"]["tables"]],
            [
                ("Darkan ordinary", 128),
                ("Darkan charms", 404),
                ("Long and curved bones", 100000),
            ],
        )
        for table in giant["drops"]["tables"]:
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]),
                table["total"],
            )
        self.assertIn("oldid=6555306", giant["source"])
        self.assertIn("non-Daemonheim", giant["source_status"])

    def test_cave_horror_preserves_cutoff_access_scream_and_drop_contract(self):
        horror = COMBAT_ENEMY_DATA["cave_horror"]

        self.assertEqual(horror["level"], 80)
        self.assertEqual(horror["required_slayer_level"], 58)
        self.assertEqual(horror["quest_gate"], "cabin_fever")
        self.assertEqual(horror["attack_style"], "magic_melee")
        self.assertEqual(horror["attack_speed"], 4)
        self.assertEqual(horror["respawn_delay"], 39)
        self.assertEqual(horror["max_hit"], 90)
        self.assertEqual(horror["slayer_xp"], 55.0)
        self.assertEqual(
            horror["stats"],
            {
                "hitpoints": 550,
                "attack": 80,
                "strength": 77,
                "defence": 62,
                "magic": 80,
                "ranged": 1,
            },
        )
        self.assertEqual(
            horror["protective_equipment"]["applies_to_player_classes"],
            ("melee",),
        )
        self.assertEqual(
            horror["protective_equipment"]["unprotected_effect"]["damage"],
            {"kind": "fixed", "amount": 87},
        )
        self.assertEqual(horror["drops"]["guaranteed"], (("Big bones", 1),))
        self.assertEqual(
            [
                (table["name"], table["total"])
                for table in horror["drops"]["tables"]
            ],
            [
                ("Darkan ordinary", 128),
                ("Darkan charms", 1212),
                ("Long and curved bones", 100000),
                ("Black mask (10)", 512),
                ("Hard clue", 128),
            ],
        )
        for table in horror["drops"]["tables"]:
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]),
                table["total"],
            )
        self.assertIn("oldid=6550392", horror["source"])
        self.assertIn("four ticks", horror["source_status"])

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
