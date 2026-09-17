import json
import unittest
from pathlib import Path

import pkg_alias

from .contract import (
    COMBAT_ENEMY_DATA,
    NEW_COMBAT_ENEMIES,
    OPTIONAL_ENEMY_KEYS,
    REQUIRED_BONUS_KEYS,
    REQUIRED_ENEMY_KEYS,
    REQUIRED_STAT_KEYS,
    _assert_slots_well_formed,
)
from ankiscape.logic_pure.logic_pure import combat_target_locked_reasons_pure


class CombatEnemyRosterDataTest(unittest.TestCase):
    _assert_slots_well_formed = _assert_slots_well_formed

    def test_no_enemy_id_collides_with_a_skilling_target_id(self):
        # carried_inventory is keyed by target id, and combat targets and skilling
        # targets share that one namespace. A collision would make a combat bank run
        # wipe a skilling pack's view, and a combat death drop that skill's carried
        # materials. There is no collision today; this keeps it that way loudly.
        from ankiscape.core.constants import (
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
                    base_keys = {
                        "warning",
                        "unprotected_effect",
                        "source_status",
                    }
                    if "alternatives" in protection:
                        self.assertEqual(
                            set(protection),
                            base_keys
                            | {"alternatives", "applies_to_player_classes"},
                        )
                        self.assertTrue(protection["alternatives"])
                        for alternative in protection["alternatives"]:
                            self.assertIn(
                                alternative["slot"],
                                {"head", "shield", "neck", "feet"},
                            )
                            self.assertTrue(alternative["items"])
                        self.assertTrue(
                            protection["applies_to_player_classes"]
                        )
                    else:
                        self.assertEqual(
                            set(protection),
                            base_keys | {"slot", "items"},
                        )
                        self.assertIn(
                            protection["slot"],
                            {"head", "shield", "neck", "feet"},
                        )
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

    def test_new_slayer_family_assets_are_present_and_provenanced(self):
        root = Path(pkg_alias.__file__).resolve().parent
        provenance = json.loads(
            (root / "assets_provenance.json").read_text(encoding="utf-8")
        )

        expected_timestamps = {
            'killerwatt': '2011-11-23T11:58:22Z',
            'sea_snake_hatchling': '2010-08-07T18:37:31Z',
            'sea_snake_young': '2012-03-09T03:02:36Z',
            'brine_rat': '2010-06-01T15:33:31Z',
            'dagannoth': '2011-11-19T16:36:18Z',
            'dagannoth_level_92': '2011-11-19T18:45:30Z',
            'elf_warrior': '2014-08-27T14:36:09Z',
            'elf_warrior_level_108': '2014-08-27T14:36:14Z',
            'molanisk': '2011-11-26T04:43:26Z',
            'turoth': '2011-11-30T02:42:28Z',
            'fire_giant': '2011-11-21T02:39:58Z',
            'blue_dragon': '2011-02-01T13:53:37Z',
            'baby_blue_dragon': '2012-05-10T09:54:19Z',
            'bronze_dragon': '2010-12-11T13:46:01Z',
            'iron_dragon': '2010-12-29T13:34:17Z',
            'red_dragon': '2010-07-05T19:36:16Z',
            'black_dragon': '2010-12-28T12:10:25Z',
            'baby_red_dragon': '2011-12-11T10:26:02Z',
            'cave_horror': '2010-06-01T15:33:33Z',
        }

        for target_id, file_title in (
            ("jackal", "Jackal.png"),
            ("goat", "Desert Goat.png"),
            ("ogre", "Ogre.png"),
            ("mogre", "Mogre icon.png"),
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
            # The art sweep recovered the period image under the wiki's
            # renamed "Green dragon 1.png" title; the creature is the same.
            ("green_dragon", "Green dragon 1.png"),
            ("harpie_bug_swarm", "Harpie Bugs Swarm.png"),
            ("killerwatt", "Killerwatt icon.png"),
            ("sea_snake_hatchling", "Sea Snake Hatchling.png"),
            ("sea_snake_young", "Sea Snake Young.png"),
            ("brine_rat", "Brine rat icon.png"),
            ("molanisk", "Molanisk icon.png"),
            ("turoth", "Turoth icon.png"),
            ("fire_giant", "Fire giant.png"),
            ("blue_dragon", "Blue dragon.png"),
            ("baby_blue_dragon", "Baby blue dragon.png"),
            ("bronze_dragon", "Bronze dragon.png"),
            ("iron_dragon", "Iron dragon.png"),
            ("steel_dragon", "Steel dragon.png"),
            ("red_dragon", "Red dragon old 5.png"),
            ("black_dragon", "Black dragon.png"),
            ("baby_red_dragon", "Baby red dragon.png"),
            ("cave_horror", "Cave horror icon.png"),
            ("dagannoth", "Dagannoth ranged.png"),
            ("dagannoth_level_92", "Dagannoth melee.png"),
            ("elf_warrior", "Elf warrior (Iorwerth ranger) (2010).png"),
            (
                "elf_warrior_level_108",
                "Elf warrior (Iorwerth warrior) (2010).png",
            ),
        ):
            with self.subTest(target=target_id):
                relative_path = f"combatenemies/{target_id}.png"
                self.assertTrue((root / relative_path).is_file())
                self.assertIn(relative_path, provenance)
                self.assertEqual(provenance[relative_path]["file_title"], file_title)
                expected_timestamp = expected_timestamps.get(target_id)
                if expected_timestamp is not None:
                    self.assertEqual(
                        provenance[relative_path]["timestamp"], expected_timestamp
                    )
                if target_id == "steel_dragon":
                    self.assertLess(
                        provenance[relative_path]["timestamp"],
                        "2012-11-20T00:00:00Z",
                    )

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
