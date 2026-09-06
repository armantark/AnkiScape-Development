import unittest

from .contract import COMBAT_ENEMY_DATA


class CombatEnemyRosterDataTest(unittest.TestCase):
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

    def test_blue_dragon_family_preserves_adult_and_baby_cutoff_variants(self):
        adult = COMBAT_ENEMY_DATA["blue_dragon"]
        baby = COMBAT_ENEMY_DATA["baby_blue_dragon"]

        self.assertEqual(adult["level"], 111)
        self.assertEqual(adult["attack_speed"], 6)
        self.assertEqual(adult["max_hit"], 110)
        self.assertEqual(adult["slayer_xp"], 107.6)
        self.assertEqual(
            adult["stats"],
            {
                "hitpoints": 1100,
                "attack": 95,
                "strength": 95,
                "defence": 95,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(adult["dragonfire"]["chance_numerator"], 1)
        self.assertEqual(adult["dragonfire"]["chance_denominator"], 4)
        self.assertEqual(adult["dragonfire"]["unprotected_max_hit"], 500)
        self.assertEqual(adult["drops"]["guaranteed"], (("Blue dragonhide", 1), ("Dragon bones", 1)))
        self.assertEqual(
            [(table["name"], table["total"]) for table in adult["drops"]["tables"]],
            [
                ("Darkan ordinary", 128),
                ("Darkan charms", 404),
                ("Blue dragon egg (Summoning 99)", 2000),
                ("Hard clue", 128),
            ],
        )
        for table in adult["drops"]["tables"]:
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]),
                table["total"],
            )
        self.assertEqual(
            adult["drops"]["tables"][2]["required_skill_levels"],
            (("summoning", 99),),
        )

        self.assertEqual(baby["level"], 48)
        self.assertEqual(baby["attack_speed"], 6)
        self.assertEqual(baby["max_hit"], 60)
        self.assertEqual(baby["slayer_xp"], 50.0)
        self.assertNotIn("dragonfire", baby)
        self.assertEqual(baby["drops"]["guaranteed"], (("Baby dragon bones", 1),))
        self.assertIn("oldid=6506510", adult["source"])
        self.assertIn("oldid=6516086", baby["source"])

    def test_bronze_dragon_preserves_cutoff_metal_dragon_contract(self):
        dragon = COMBAT_ENEMY_DATA["bronze_dragon"]

        self.assertEqual(dragon["level"], 131)
        self.assertEqual(dragon["attack_speed"], 6)
        self.assertEqual(dragon["max_hit"], 123)
        self.assertEqual(dragon["slayer_xp"], 125.0)
        self.assertEqual(
            dragon["stats"],
            {
                "hitpoints": 1220,
                "attack": 112,
                "strength": 112,
                "defence": 112,
                "magic": 100,
                "ranged": 1,
            },
        )
        self.assertEqual(dragon["dragonfire"]["chance_numerator"], 1)
        self.assertEqual(dragon["dragonfire"]["chance_denominator"], 2)
        self.assertEqual(dragon["dragonfire"]["unprotected_max_hit"], 500)
        self.assertEqual(
            dragon["drops"]["guaranteed"],
            (("Dragon bones", 1), ("Bronze bar", 5)),
        )
        self.assertEqual(
            [(table["name"], table["total"]) for table in dragon["drops"]["tables"]],
            [
                ("Darkan ordinary", 128),
                ("Darkan charms", 1212),
                ("Dragon plateskirt", 2048),
                ("Dragon platelegs", 2048),
                ("Hard clue", 128),
                ("Elite clue", 500),
            ],
        )
        for table in dragon["drops"]["tables"]:
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]),
                table["total"],
            )
        self.assertIn("oldid=6550367", dragon["source"])
        self.assertIn("one empty slot", dragon["source_status"])

    def test_iron_dragon_preserves_cutoff_metal_dragon_contract(self):
        dragon = COMBAT_ENEMY_DATA["iron_dragon"]

        self.assertEqual(dragon["level"], 189)
        self.assertEqual(dragon["attack_speed"], 6)
        self.assertEqual(dragon["max_hit"], 203)
        self.assertEqual(dragon["slayer_xp"], 173.2)
        self.assertEqual(
            dragon["stats"],
            {
                "hitpoints": 1650,
                "attack": 165,
                "strength": 165,
                "defence": 165,
                "magic": 100,
                "ranged": 1,
            },
        )
        self.assertEqual(dragon["dragonfire"]["chance_numerator"], 1)
        self.assertEqual(dragon["dragonfire"]["chance_denominator"], 2)
        self.assertEqual(dragon["dragonfire"]["unprotected_max_hit"], 500)
        self.assertEqual(
            dragon["drops"]["guaranteed"],
            (("Dragon bones", 1), ("Iron bar", 5)),
        )
        self.assertEqual(
            [(table["name"], table["total"]) for table in dragon["drops"]["tables"]],
            [
                ("Darkan ordinary", 128),
                ("Darkan charms", 1212),
                ("Dragon plateskirt", 1024),
                ("Dragon platelegs", 1024),
                ("Draconic visage", 10000),
                ("Hard clue", 128),
            ],
        )
        for table in dragon["drops"]["tables"]:
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]),
                table["total"],
            )
        self.assertIn("oldid=6530527", dragon["source"])
        self.assertIn("one empty slot", dragon["source_status"])

    def test_steel_dragon_preserves_cutoff_metal_dragon_contract(self):
        dragon = COMBAT_ENEMY_DATA["steel_dragon"]

        self.assertEqual(dragon["level"], 246)
        self.assertEqual(dragon["attack_speed"], 6)
        self.assertEqual(dragon["respawn_delay"], 59)
        self.assertEqual(dragon["max_hit"], 225)
        self.assertEqual(dragon["slayer_xp"], 220.4)
        self.assertEqual(
            dragon["stats"],
            {
                "hitpoints": 2100,
                "attack": 215,
                "strength": 215,
                "defence": 215,
                "magic": 100,
                "ranged": 1,
            },
        )
        self.assertEqual(dragon["dragonfire"]["chance_numerator"], 1)
        self.assertEqual(dragon["dragonfire"]["chance_denominator"], 2)
        self.assertEqual(dragon["dragonfire"]["unprotected_max_hit"], 500)
        self.assertEqual(
            dragon["drops"]["guaranteed"],
            (("Dragon bones", 1), ("Steel bar", 5)),
        )
        self.assertEqual(
            [(table["name"], table["total"]) for table in dragon["drops"]["tables"]],
            [
                ("Darkan ordinary with OSRS-lineage closure", 128),
                ("Darkan charms", 1212),
                ("Dragon plateskirt", 512),
                ("Dragon platelegs", 512),
                ("Draconic visage", 10000),
                ("Hard clue", 64),
                ("Elite clue", 500),
            ],
        )
        for table in dragon["drops"]["tables"]:
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]),
                table["total"],
            )
        self.assertIn("oldid=6582075", dragon["source"])
        self.assertIn("provisional/osrs-lineage", dragon["source_status"])
        self.assertIn("quantity-three charms", dragon["source_status"])

    def test_red_dragon_family_preserves_cutoff_adult_and_baby_contracts(self):
        adult = COMBAT_ENEMY_DATA["red_dragon"]
        baby = COMBAT_ENEMY_DATA["baby_red_dragon"]

        self.assertEqual(adult["level"], 152)
        self.assertEqual(adult["attack_speed"], 6)
        self.assertEqual(adult["max_hit"], 158)
        self.assertEqual(adult["slayer_xp"], 142.5)
        self.assertEqual(
            adult["stats"],
            {
                "hitpoints": 1400,
                "attack": 130,
                "strength": 130,
                "defence": 130,
                "magic": 1,
                "ranged": 1,
            },
        )
        self.assertEqual(adult["dragonfire"]["chance_numerator"], 1)
        self.assertEqual(adult["dragonfire"]["chance_denominator"], 4)
        self.assertEqual(adult["dragonfire"]["unprotected_max_hit"], 500)
        self.assertEqual(
            adult["drops"]["guaranteed"],
            (("Dragon bones", 1), ("Red dragonhide", 1)),
        )
        self.assertEqual(
            [(table["name"], table["total"]) for table in adult["drops"]["tables"]],
            [
                ("Darkan ordinary", 128),
                ("Darkan charms", 1212),
                ("Red dragon egg (Summoning 99)", 2000),
                ("Hard clue", 128),
            ],
        )
        for table in adult["drops"]["tables"]:
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]),
                table["total"],
            )
        self.assertIn("oldid=6506523", adult["source"])
        self.assertIn("three empty slots", adult["source_status"])
        self.assertIn("144-LP Darkan conflict", adult["source_status"])

        self.assertEqual(baby["level"], 48)
        self.assertEqual(baby["attack_speed"], 6)
        self.assertEqual(baby["max_hit"], 54)
        self.assertEqual(baby["slayer_xp"], 50.0)
        self.assertEqual(baby["stats"]["hitpoints"], 500)
        self.assertNotIn("dragonfire", baby)
        self.assertEqual(
            baby["drops"],
            {"guaranteed": (("Baby dragon bones", 1),), "tables": ()},
        )
        self.assertIn("oldid=6516030", baby["source"])
        self.assertIn("level-65 POH", baby["source_status"])

    def test_black_dragon_preserves_cutoff_ordinary_variant_contract(self):
        dragon = COMBAT_ENEMY_DATA["black_dragon"]

        self.assertEqual(dragon["level"], 227)
        self.assertEqual(dragon["attack_speed"], 6)
        self.assertEqual(dragon["respawn_delay"], 59)
        self.assertEqual(dragon["max_hit"], 214)
        self.assertEqual(dragon["slayer_xp"], 199.4)
        self.assertEqual(
            dragon["stats"],
            {
                "hitpoints": 1900,
                "attack": 200,
                "strength": 200,
                "defence": 200,
                "magic": 100,
                "ranged": 1,
            },
        )
        self.assertEqual(dragon["dragonfire"]["chance_numerator"], 1)
        self.assertEqual(dragon["dragonfire"]["chance_denominator"], 4)
        self.assertEqual(dragon["dragonfire"]["unprotected_max_hit"], 500)
        self.assertEqual(
            dragon["drops"]["guaranteed"],
            (("Dragon bones", 1), ("Black dragonhide", 1)),
        )
        self.assertEqual(
            [(table["name"], table["total"]) for table in dragon["drops"]["tables"]],
            [
                ("game-main ordinary", 128),
                ("Darkan charms", 1212),
                ("Black dragon egg (Summoning 99)", 2000),
                ("Draconic visage", 10000),
                ("Hard clue", 128),
                ("Elite clue", 500),
            ],
        )
        for table in dragon["drops"]["tables"]:
            self.assertEqual(
                sum(slot["slots"] for slot in table["slots"]),
                table["total"],
            )
        self.assertEqual(
            dragon["drops"]["tables"][2]["required_skill_levels"],
            (("summoning", 99),),
        )
        self.assertIn("oldid=6580941", dragon["source"])
        self.assertIn("six empty slots", dragon["source_status"])
        self.assertIn("quantity-three charms", dragon["source_status"])
        self.assertIn("Queen Black Dragon", dragon["source_status"])
