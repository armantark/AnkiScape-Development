import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA


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
    "killerwatt",
    "sea_snake_hatchling",
    "sea_snake_young",
    "bush_snake",
    "brine_rat",
    "molanisk",
    "turoth",
    "fire_giant",
    "blue_dragon",
    "baby_blue_dragon",
    "bronze_dragon",
    "iron_dragon",
    "steel_dragon",
    "red_dragon",
    "black_dragon",
    "baby_red_dragon",
    "cave_horror",
    "ogre",
    "mogre",
    "jackal",
    "goat",
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
    "elf_warrior",
    "elf_warrior_level_108",
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
    "attack_style_by_player_class",
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
    "skill_requirements",
    "environmental_hazard",
    "desert_context",
    "retaliation_stop_lifepoints",
    "regeneration",
    "source_status",
    "quest_gate",
    "quest_gate_label",
    "partial_quest_access",
    "required_items",
    "required_items_label",
    "required_item_options",
    "required_item_options_label",
    "lure",
    "light_source",
    "restricted_weapon",
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
