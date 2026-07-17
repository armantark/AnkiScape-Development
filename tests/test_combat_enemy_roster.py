import unittest

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

OPTIONAL_ENEMY_KEYS = {"poison_damage"}

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


# The source gates these kills on an item the combat model cannot express
# (`on_item_on_npc`): a Gargoyle must be smashed with a rock hammer, a Rockslug
# salted with a bag of salt. Adding them as ordinary melee enemies would let you
# kill them without the item, deviating from the source. They stay out until a
# required-finisher mechanic exists.
ITEM_GATED_ENEMIES_NOT_MODELLED = ("gargoyle", "rockslug")


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


    def test_item_gated_enemies_stay_out_until_the_mechanic_exists(self):
        for enemy_name in ITEM_GATED_ENEMIES_NOT_MODELLED:
            self.assertNotIn(enemy_name, COMBAT_ENEMY_DATA)

    def test_new_enemies_have_required_schema(self):
        for enemy_name in NEW_COMBAT_ENEMIES:
            with self.subTest(enemy=enemy_name):
                enemy = COMBAT_ENEMY_DATA[enemy_name]

                self.assertEqual(set(enemy) - OPTIONAL_ENEMY_KEYS, REQUIRED_ENEMY_KEYS)
                self.assertEqual(set(enemy) - REQUIRED_ENEMY_KEYS, set(enemy) & OPTIONAL_ENEMY_KEYS)
                self.assertEqual(set(enemy["stats"]), REQUIRED_STAT_KEYS)
                self.assertEqual(set(enemy["bonuses"]), REQUIRED_BONUS_KEYS)
                self.assertEqual(enemy["attack_style"], "melee")
                self.assertGreater(enemy["level"], 0)
                if "poison_damage" in enemy:
                    self.assertIsInstance(enemy["poison_damage"], int)
                    self.assertGreater(enemy["poison_damage"], 0)
                self.assertGreater(enemy["stats"]["hitpoints"], 0)

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
                self.assertTrue("quantity" in slot or "quantity_range" in slot)
                if "quantity" in slot:
                    self.assertIsInstance(slot["quantity"], int)
                    self.assertGreater(slot["quantity"], 0)
                if "quantity_range" in slot:
                    self.assertEqual(len(slot["quantity_range"]), 2)
                    self.assertLessEqual(slot["quantity_range"][0], slot["quantity_range"][1])
            if "table" in slot:
                self.assertIn("name", slot["table"])
                self.assertIn("total", slot["table"])
                self.assertIn("slots", slot["table"])


if __name__ == "__main__":
    unittest.main()
