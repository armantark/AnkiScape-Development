import unittest

from .contract import COMBAT_ENEMY_DATA


class CombatEnemyRosterDataTest(unittest.TestCase):
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
