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


def _assert_positive_int(self, value):
    self.assertIsInstance(value, int)
    self.assertGreater(value, 0)


def _assert_quantity_range_well_formed(self, quantity_range):
    self.assertEqual(len(quantity_range), 2)
    self.assertLessEqual(quantity_range[0], quantity_range[1])


def _assert_quantity_choices_well_formed(self, quantity_choices):
    self.assertTrue(quantity_choices)
    self.assertTrue(
        all(
            isinstance(quantity, int) and quantity > 0
            for quantity in quantity_choices
        )
    )


_QUANTITY_CHECKS = {
    "quantity": _assert_positive_int,
    "quantity_range": _assert_quantity_range_well_formed,
    "quantity_choices": _assert_quantity_choices_well_formed,
}


def _assert_item_slot_well_formed(self, slot):
    self.assertIsInstance(slot["item"], str)
    quantity_fields = {field for field in _QUANTITY_CHECKS if field in slot}
    self.assertEqual(len(quantity_fields), 1)
    (field,) = quantity_fields
    _QUANTITY_CHECKS[field](self, slot[field])


def _assert_slots_well_formed(self, slots):
    for slot in slots:
        self.assertIn("slots", slot)
        self.assertIsInstance(slot["slots"], int)
        self.assertGreater(slot["slots"], 0)
        if "item" in slot:
            _assert_item_slot_well_formed(self, slot)
        if "table" in slot:
            self.assertIn("name", slot["table"])
            self.assertIn("total", slot["table"])
            self.assertIn("slots", slot["table"])


def _assert_poison_immune_flag(self, poison_immune):
    self.assertIs(poison_immune, True)


def _assert_positive_float(self, value):
    self.assertIsInstance(value, float)
    self.assertGreater(value, 0.0)


def _assert_protective_equipment_well_formed(self, protection):
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


def _assert_start_equipment_well_formed(self, requirement):
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


def _assert_weakening_equipment_well_formed(self, weakness):
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


def _assert_bite_well_formed(self, bite):
    self.assertGreater(bite["chance_numerator"], 0)
    self.assertGreaterEqual(
        bite["chance_denominator"], bite["chance_numerator"]
    )
    self.assertGreater(bite["max_heal"], 0)
    self.assertTrue(bite["stat_drain_skills"])
    self.assertTrue(bite["source_status"])


def _assert_dragonfire_well_formed(self, dragonfire):
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


def _assert_finisher_well_formed(self, finisher):
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


def _assert_environmental_hazard_well_formed(self, hazard):
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


_OPTIONAL_ENEMY_SECTION_CHECKS = {
    "max_hit": _assert_positive_int,
    "poison_damage": _assert_positive_int,
    "poison_immune": _assert_poison_immune_flag,
    "xp_multiplier": _assert_positive_float,
    "protective_equipment": _assert_protective_equipment_well_formed,
    "start_equipment": _assert_start_equipment_well_formed,
    "weakening_equipment": _assert_weakening_equipment_well_formed,
    "bite": _assert_bite_well_formed,
    "dragonfire": _assert_dragonfire_well_formed,
    "finisher": _assert_finisher_well_formed,
    "required_slayer_level": _assert_positive_int,
    "environmental_hazard": _assert_environmental_hazard_well_formed,
}
