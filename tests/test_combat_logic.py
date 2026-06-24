import unittest

from combat_data import (
    COMBAT_ENEMY_DATA,
    COMBAT_MAGIC_SPELL_DATA,
    COMBAT_MAGIC_STAFF_DATA,
    COMBAT_RANGED_AMMO_DATA,
    COMBAT_RANGED_WEAPON_DATA,
    MAGIC_FORMULA_SOURCE_PATH,
    MAGIC_STRATEGY_SOURCE_PATH,
    RANGED_FORMULA_SOURCE_PATH,
    RANGED_STRATEGY_SOURCE_PATH,
)
from constants import EQUIPMENT_DATA
from logic_pure import (
    _combat_roll_drops,
    apply_combat_burst_pure,
    apply_combat_poison_effect_pure,
    apply_safe_combat_recovery_pure,
    combat_death_office_reclaim_cost_pure,
    combat_death_office_summary_pure,
    combat_poison_damage_for_ticks_pure,
    combat_poison_ticks_for_initial_damage_pure,
    combat_status_summary_pure,
    refill_combat_supply_loadout_pure,
    combat_target_locked_reasons_pure,
    combat_target_preview_pure,
    reclaim_death_office_items_pure,
    set_combat_auto_eat_food_pure,
    set_combat_auto_eat_threshold_pure,
    unload_combat_supply_loadout_pure,
)


def _rng(values):
    iterator = iter(values)

    def _next():
        try:
            return next(iterator)
        except StopIteration:
            return 0.999999

    return _next


def _player(**overrides):
    data = {
        "inventory": {},
        "equipment": {},
        "attack_level": 99,
        "strength_level": 99,
        "defense_level": 99,
        "ranged_level": 99,
        "magic_level": 99,
        "constitution_level": 10,
        "attack_exp": 0.0,
        "strength_exp": 0.0,
        "defense_exp": 0.0,
        "ranged_exp": 0.0,
        "magic_exp": 0.0,
        "constitution_exp": 0.0,
        "current_combat_target": "chicken",
        "combat_attack_style": "accurate",
        "current_combat_spell": "wind_strike",
        "combat_lifepoints": 100,
        "combat_auto_eat_threshold_percent": 40,
        "combat_auto_eat_food": ["Shrimps"],
        "combat_supply_loadout": {},
        "combat_special_attack_energy": 100,
        "combat_stat_drains": {},
        "combat_status_effects": {},
        "combat_recovery_progress": {},
        "combat_encounter": {},
        "combat_kill_counts": {},
    }
    data.update(overrides)
    return data


_KILLER_ENEMY_DATA = {
    "killer": {
        "display_name": "Killer",
        "level": 999,
        "group": "Test",
        "stats": {
            "attack": 99,
            "strength": 99,
            "defence": 99,
            "hitpoints": 1000,
        },
        "bonuses": {},
        "attack_speed": 1,
        "drops": {"guaranteed": (), "tables": ()},
        "source": "test",
    }
}


class CombatLogicTest(unittest.TestCase):
    def test_standard_bow_and_arrow_rows_match_2011scape_source(self):
        expected_bows = {
            "Shortbow": ("shortbow", ("Bronze arrows", "Iron arrows")),
            "Longbow": ("longbow", ("Bronze arrows", "Iron arrows")),
            "Oak shortbow": ("oak_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows")),
            "Oak longbow": ("oak_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows")),
            "Willow shortbow": ("willow_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows")),
            "Willow longbow": ("willow_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows")),
            "Maple shortbow": ("maple_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows")),
            "Maple longbow": ("maple_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows")),
            "Yew shortbow": ("yew_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows")),
            "Yew longbow": ("yew_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows")),
            "Magic shortbow": ("magic_shortbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows")),
            "Magic longbow": ("magic_longbow", ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows")),
        }

        for bow_name, (equipment_type, ammo) in expected_bows.items():
            with self.subTest(bow_name=bow_name):
                spec = COMBAT_RANGED_WEAPON_DATA[bow_name]
                self.assertEqual(spec["equipment_type"], equipment_type)
                self.assertEqual(spec["compatible_ammo"], ammo)

        expected_ammo = {
            "Bronze arrows": (882, "Bronze arrow", 7),
            "Iron arrows": (884, "Iron arrow", 10),
            "Steel arrows": (886, "Steel arrow", 16),
            "Mithril arrows": (888, "Mithril arrow", 22),
            "Adamant arrows": (890, "Adamant arrow", 31),
            "Rune arrows": (892, "Rune arrow", 49),
        }
        for ammo_name, (source_item_id, source_item_name, ranged_strength) in expected_ammo.items():
            with self.subTest(ammo_name=ammo_name):
                spec = COMBAT_RANGED_AMMO_DATA[ammo_name]
                self.assertEqual(spec["source_item_id"], source_item_id)
                self.assertEqual(spec["source_item_name"], source_item_name)
                self.assertEqual(spec["ranged_strength"], ranged_strength)

    def test_standard_strike_spell_rows_match_2011scape_source(self):
        self.assertEqual(
            COMBAT_MAGIC_SPELL_DATA["water_strike"]["rune_cost"],
            {"Air rune": 1, "Mind rune": 1, "Water rune": 1},
        )
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["water_strike"]["required_magic_level"], 5)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["water_strike"]["max_hit_old_hp"], 4)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["water_strike"]["base_magic_xp"], 7.5)

        self.assertEqual(
            COMBAT_MAGIC_SPELL_DATA["earth_strike"]["rune_cost"],
            {"Air rune": 1, "Mind rune": 1, "Earth rune": 2},
        )
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["earth_strike"]["required_magic_level"], 9)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["earth_strike"]["max_hit_old_hp"], 6)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["earth_strike"]["base_magic_xp"], 9.5)

        self.assertEqual(
            COMBAT_MAGIC_SPELL_DATA["fire_strike"]["rune_cost"],
            {"Air rune": 1, "Mind rune": 1, "Fire rune": 3},
        )
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["fire_strike"]["required_magic_level"], 13)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["fire_strike"]["max_hit_old_hp"], 8)
        self.assertEqual(COMBAT_MAGIC_SPELL_DATA["fire_strike"]["base_magic_xp"], 11.5)
        self.assertEqual(COMBAT_MAGIC_STAFF_DATA["Staff of air"]["covered_runes"], ("Air rune",))
        self.assertEqual(COMBAT_MAGIC_STAFF_DATA["Staff of fire"]["covered_runes"], ("Fire rune",))

    def test_standard_bolt_blast_wave_spell_rows_match_2011scape_source(self):
        expected = {
            "wind_bolt": ("Wind Bolt", 17, {"Air rune": 2, "Chaos rune": 1}, 9, 13.5, 73, 34, 11),
            "water_bolt": ("Water Bolt", 23, {"Air rune": 2, "Water rune": 2, "Chaos rune": 1}, 10, 16.5, 76, 39, 13),
            "earth_bolt": ("Earth Bolt", 29, {"Air rune": 2, "Earth rune": 3, "Chaos rune": 1}, 11, 19.5, 79, 42, 15),
            "fire_bolt": ("Fire Bolt", 35, {"Air rune": 3, "Fire rune": 4, "Chaos rune": 1}, 12, 22.5, 82, 45, 17),
            "wind_blast": ("Wind Blast", 41, {"Air rune": 3, "Death rune": 1}, 13, 25.5, 85, 49, 19),
            "water_blast": ("Water Blast", 47, {"Air rune": 3, "Water rune": 3, "Death rune": 1}, 14, 28.5, 88, 52, 21),
            "earth_blast": ("Earth Blast", 53, {"Air rune": 3, "Earth rune": 4, "Death rune": 1}, 15, 31.5, 90, 58, 23),
            "fire_blast": ("Fire Blast", 59, {"Air rune": 4, "Fire rune": 5, "Death rune": 1}, 16, 34.5, 95, 63, 25),
            "wind_wave": ("Wind Wave", 62, {"Air rune": 5, "Blood rune": 1}, 17, 36.0, 96, 70, 27),
            "water_wave": ("Water Wave", 65, {"Air rune": 5, "Water rune": 7, "Blood rune": 1}, 18, 37.5, 98, 73, 29),
            "earth_wave": ("Earth Wave", 70, {"Air rune": 5, "Earth rune": 7, "Blood rune": 1}, 19, 40.0, 101, 77, 31),
            "fire_wave": ("Fire Wave", 75, {"Air rune": 5, "Fire rune": 7, "Blood rune": 1}, 20, 42.5, 102, 80, 33),
        }

        for spell_id, (display, level, runes, max_hit, base_xp, unique_id, component_id, autocast_id) in expected.items():
            with self.subTest(spell_id=spell_id):
                spell = COMBAT_MAGIC_SPELL_DATA[spell_id]
                self.assertEqual(spell["display_name"], display)
                self.assertEqual(spell["spellbook"], "standard")
                self.assertEqual(spell["required_magic_level"], level)
                self.assertEqual(spell["rune_cost"], runes)
                self.assertEqual(spell["max_hit_old_hp"], max_hit)
                self.assertEqual(spell["base_magic_xp"], base_xp)
                self.assertEqual(spell["attack_speed"], 5)
                self.assertEqual(spell["unique_id"], unique_id)
                self.assertEqual(spell["component_id"], component_id)
                self.assertEqual(spell["autocast_id"], autocast_id)
                self.assertIn(spell_id.upper(), spell["source"])

    def test_simple_enemy_import_rows_match_source(self):
        cow_calf = COMBAT_ENEMY_DATA["cow_calf"]
        ram = COMBAT_ENEMY_DATA["ram"]
        seagull = COMBAT_ENEMY_DATA["seagull"]

        self.assertEqual(cow_calf["stats"]["hitpoints"], 60)
        self.assertEqual(cow_calf["drops"]["guaranteed"], (("Bones", 1), ("Raw beef", 1), ("Cowhide", 1)))
        self.assertEqual(cow_calf["drops"]["tables"], ())
        self.assertTrue(cow_calf["source"].endswith("cow_calf_level_2.plugin.kts"))
        self.assertEqual(ram["stats"]["hitpoints"], 80)
        self.assertEqual(ram["drops"]["guaranteed"], (("Bones", 1),))
        self.assertTrue(ram["source"].endswith("ram_level_2.plugin.kts"))
        self.assertEqual(seagull["group"], "Coastal")
        self.assertEqual(seagull["slayer_xp"], 5.0)
        self.assertTrue(seagull["source"].endswith("seagull_level_2.plugin.kts"))

    def test_spider_import_rows_match_source_and_quantity_range(self):
        spider = COMBAT_ENEMY_DATA["spider"]
        giant_spider = COMBAT_ENEMY_DATA["giant_spider"]

        self.assertEqual(spider["stats"]["hitpoints"], 20)
        self.assertEqual(spider["respawn_delay"], 35)
        self.assertEqual(spider["drops"]["guaranteed"], ())
        self.assertEqual(spider["drops"]["tables"][0]["total"], 200)
        self.assertEqual(spider["drops"]["tables"][0]["slots"][0]["item"], "Gold charm")
        self.assertTrue(spider["source"].endswith("spider_level_1.plugin.kts"))
        self.assertEqual(giant_spider["stats"]["hitpoints"], 50)
        self.assertEqual(giant_spider["slayer_xp"], 5.0)
        self.assertEqual(giant_spider["drops"]["tables"][0]["slots"][0]["quantity_range"], (4, 6))
        self.assertEqual(giant_spider["drops"]["tables"][1]["slots"][0]["item"], "Bronze med helm")
        self.assertTrue(giant_spider["source"].endswith("giant_spider_level_2.plugin.kts"))

    def test_poison_enemy_rows_match_source_and_no_drop_handler(self):
        scorpion = COMBAT_ENEMY_DATA["poison_scorpion"]
        spider = COMBAT_ENEMY_DATA["poison_spider"]

        self.assertEqual(scorpion["level"], 20)
        self.assertEqual(scorpion["group"], "Scorpions")
        self.assertEqual(scorpion["attack_speed"], 4)
        self.assertEqual(scorpion["respawn_delay"], 25)
        self.assertEqual(scorpion["poison_damage"], 3)
        self.assertEqual(scorpion["stats"]["hitpoints"], 230)
        self.assertEqual(scorpion["stats"]["attack"], 16)
        self.assertEqual(scorpion["stats"]["strength"], 17)
        self.assertEqual(scorpion["stats"]["defence"], 15)
        self.assertEqual(scorpion["bonuses"]["defence_slash"], 15)
        self.assertEqual(scorpion["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("poison_scorpion_lvl_20.plugin.kts", scorpion["source"])
        self.assertIn("no DropTableFactory registration", scorpion["source"])

        self.assertEqual(spider["level"], 31)
        self.assertEqual(spider["group"], "Spiders")
        self.assertEqual(spider["poison_damage"], 3)
        self.assertEqual(spider["stats"]["hitpoints"], 250)
        self.assertEqual(spider["stats"]["attack"], 28)
        self.assertEqual(spider["bonuses"]["defence_stab"], 20)
        self.assertEqual(spider["drops"], {"guaranteed": (), "tables": ()})
        self.assertIn("poison_spider_lvl_31.plugin.kts", spider["source"])

    def test_scorpion_and_higher_spider_rows_match_source(self):
        scorpion = COMBAT_ENEMY_DATA["scorpion"]
        spider = COMBAT_ENEMY_DATA["spider_level_24"]
        deadly_red = COMBAT_ENEMY_DATA["deadly_red_spider"]
        giant = COMBAT_ENEMY_DATA["giant_spider_level_50"]

        self.assertEqual(scorpion["level"], 14)
        self.assertEqual(scorpion["group"], "Scorpions")
        self.assertEqual(scorpion["stats"]["hitpoints"], 170)
        self.assertEqual(scorpion["stats"]["strength"], 12)
        self.assertEqual(scorpion["bonuses"]["defence_slash"], 15)
        self.assertEqual(scorpion["drops"]["tables"][0]["total"], 1000)
        self.assertEqual(scorpion["drops"]["tables"][0]["slots"][1], {"item": "Green charm", "quantity": 1, "slots": 70})
        self.assertTrue(scorpion["source"].endswith("scorpion_level_14.plugin.kts"))

        self.assertEqual(spider["level"], 24)
        self.assertEqual(spider["respawn_delay"], 27)
        self.assertEqual(spider["stats"]["hitpoints"], 220)
        self.assertEqual(spider["bonuses"]["attack_stab"], 53)
        self.assertEqual(spider["drops"]["tables"][0]["total"], 200)
        self.assertTrue(spider["source"].endswith("spider_level_24.plugin.kts"))

        self.assertEqual(deadly_red["level"], 34)
        self.assertEqual(deadly_red["stats"]["hitpoints"], 350)
        self.assertEqual(deadly_red["stats"]["strength"], 25)
        self.assertEqual(deadly_red["drops"]["tables"][0]["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 260})
        self.assertTrue(deadly_red["source"].endswith("deadly_red_spider_level_34.plugin.kts"))

        self.assertEqual(giant["level"], 50)
        self.assertEqual(giant["respawn_delay"], 25)
        self.assertEqual(giant["stats"]["hitpoints"], 500)
        self.assertEqual(giant["stats"]["strength"], 51)
        self.assertEqual(giant["bonuses"]["attack_crush"], 10)
        self.assertEqual(giant["drops"]["tables"][0]["slots"][0]["quantity_range"], (4, 6))
        self.assertEqual(giant["drops"]["tables"][1]["slots"][0]["item"], "Bronze med helm")
        self.assertTrue(giant["source"].endswith("giant_spider_level_50.plugin.kts"))

    def test_highwayman_import_row_matches_source_and_quantity_range(self):
        highwayman = COMBAT_ENEMY_DATA["highwayman"]

        self.assertEqual(highwayman["level"], 5)
        self.assertEqual(highwayman["group"], "Humanoids")
        self.assertEqual(highwayman["respawn_delay"], 60)
        self.assertEqual(highwayman["stats"]["hitpoints"], 130)
        self.assertEqual(highwayman["stats"]["defence"], 4)
        self.assertEqual(highwayman["bonuses"]["attack_stab"], 6)
        self.assertEqual(highwayman["bonuses"]["melee_strength"], 7)
        self.assertEqual(highwayman["drops"]["guaranteed"], (("Bones", 1), ("Cape", 1)))
        self.assertEqual(highwayman["drops"]["tables"][0]["total"], 20)
        self.assertEqual(highwayman["drops"]["tables"][0]["slots"][0]["item"], "Iron bolts")
        self.assertEqual(highwayman["drops"]["tables"][0]["slots"][0]["quantity_range"], (2, 12))
        self.assertTrue(highwayman["source"].endswith("highwayman_level_5.plugin.kts"))

    def test_barbarian_import_row_groups_level_8_and_9_source_twins(self):
        barbarian = COMBAT_ENEMY_DATA["barbarian"]

        self.assertEqual(barbarian["level"], 8)
        self.assertEqual(barbarian["group"], "Humanoids")
        self.assertEqual(barbarian["attack_speed"], 6)
        self.assertEqual(barbarian["respawn_delay"], 25)
        self.assertEqual(barbarian["stats"]["hitpoints"], 140)
        self.assertEqual(barbarian["stats"]["attack"], 6)
        self.assertEqual(barbarian["stats"]["strength"], 5)
        self.assertEqual(barbarian["stats"]["defence"], 5)
        self.assertEqual(barbarian["bonuses"]["attack_stab"], 8)
        self.assertEqual(barbarian["bonuses"]["attack_crush"], 10)
        self.assertEqual(barbarian["bonuses"]["defence_stab"], 1)
        self.assertEqual(barbarian["drops"]["guaranteed"], (("Bones", 1),))

        main, charms, tertiary = barbarian["drops"]["tables"]
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Bronze hatchet", "quantity": 1, "slots": 48})
        self.assertEqual(main["slots"][1], {"item": "Staff", "quantity": 1, "slots": 32})
        self.assertEqual(main["slots"][9], {"item": "Coins", "quantity": 5, "slots": 341})
        self.assertEqual(main["slots"][14], {"item": "Tin ore", "quantity": 1, "slots": 8})
        self.assertEqual(main["slots"][15], {"item": "Bear fur", "quantity": 1, "slots": 8})
        self.assertEqual(main["slots"][18], {"item": "Ring mould", "quantity": 1, "slots": 8})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(charms["slots"][0], {"item": "Gold charm", "quantity": 1, "slots": 50})
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("barbarian_lvl_8.plugin.kts", barbarian["source"])
        self.assertIn("barbarian_lvl_9.plugin.kts", barbarian["source"])

    def test_barbarian_level_10_import_row_groups_weapon_source_variants(self):
        barbarian = COMBAT_ENEMY_DATA["barbarian_level_10"]

        self.assertEqual(barbarian["display_name"], "Barbarian")
        self.assertEqual(barbarian["level"], 10)
        self.assertEqual(barbarian["group"], "Humanoids")
        self.assertEqual(barbarian["attack_speed"], 4)
        self.assertEqual(barbarian["respawn_delay"], 50)
        self.assertEqual(barbarian["stats"]["hitpoints"], 180)
        self.assertEqual(barbarian["stats"]["attack"], 8)
        self.assertEqual(barbarian["stats"]["strength"], 7)
        self.assertEqual(barbarian["stats"]["defence"], 3)
        self.assertEqual(barbarian["bonuses"]["attack_stab"], 9)
        self.assertEqual(barbarian["bonuses"]["attack_crush"], 15)
        self.assertEqual(barbarian["bonuses"]["defence_slash"], 3)
        self.assertEqual(barbarian["bonuses"]["defence_magic"], -3)
        self.assertEqual(barbarian["drops"]["guaranteed"], (("Bones", 1),))

        main, charms, tertiary = barbarian["drops"]["tables"]
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][4], {"item": "Bronze arrows", "quantity": 15, "slots": 24})
        self.assertEqual(main["slots"][8], {"item": "Law rune", "quantity": 2, "slots": 8})
        self.assertEqual(main["slots"][18], {"item": "Ring mould", "quantity": 1, "slots": 8})
        self.assertEqual(charms["total"], 1000)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1000)
        self.assertEqual(tertiary["total"], 128)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1})
        self.assertIn("barbarian_greataxe_lvl_10.plugin.kts", barbarian["source"])
        self.assertIn("barbarian_spear_lvl_10.plugin.kts", barbarian["source"])
        self.assertIn("barbarian_twohand_sword_lvl_10.plugin.kts", barbarian["source"])
        self.assertIn("barbarian_2hsword_lvl_10.plugin.kts", barbarian["source"])

    def test_goblin_level_2_import_splits_armed_and_unarmed_source_variants(self):
        unarmed = COMBAT_ENEMY_DATA["goblin_level_2_unarmed"]
        armed = COMBAT_ENEMY_DATA["goblin_level_2_armed"]

        self.assertEqual(unarmed["level"], 2)
        self.assertEqual(unarmed["group"], "Goblins")
        self.assertEqual(unarmed["attack_speed"], 4)
        self.assertEqual(unarmed["respawn_delay"], 35)
        self.assertEqual(unarmed["slayer_xp"], 5.0)
        self.assertEqual(unarmed["stats"]["hitpoints"], 50)
        self.assertEqual(unarmed["stats"]["attack"], 1)
        self.assertEqual(unarmed["stats"]["defence"], 1)
        self.assertEqual(armed["stats"]["attack"], 3)
        self.assertEqual(armed["stats"]["defence"], 4)
        self.assertIs(unarmed["drops"], armed["drops"])

        main, charms, tertiary = unarmed["drops"]["tables"]
        self.assertEqual(unarmed["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Bronze sq shield", "quantity": 1, "slots": 24})
        self.assertEqual(main["slots"][1], {"item": "Bronze spear", "quantity": 1, "slots": 32})
        self.assertEqual(main["slots"][13], {"item": "Hammer", "quantity": 1, "slots": 120})
        self.assertEqual(main["slots"][14], {"item": "Goblin book", "quantity": 1, "slots": 16})
        self.assertEqual(main["slots"][18], {"item": "Brass necklace", "quantity": 1, "slots": 8})
        self.assertEqual(charms["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in charms["slots"]), 1024)
        self.assertEqual(tertiary["total"], 1024)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 6})
        self.assertIn("goblin_level_2.plugin.kts", unarmed["source"])
        self.assertIn("unarmed ids", unarmed["source"])
        self.assertIn("armed id", armed["source"])

    def test_higher_goblin_rows_match_source_and_share_minor_herb_table(self):
        expected_rows = {
            "goblin_level_5": (5, 6, 120, 3, 1, 4, 12.0, (12, 0, 12), "goblin_level_5.plugin.kts"),
            "goblin_level_11": (11, 4, 160, 12, 13, 7, 16.0, (4, 6, 8), "goblin_level_11.plugin.kts"),
            "goblin_level_13": (13, 4, 120, 12, 13, 7, 16.0, (4, 6, 8), "goblin_level_13.plugin.kts"),
            "goblin_level_16": (16, 4, 170, 16, 13, 10, 17.0, (4, 6, 8), "goblin_level_16.plugin.kts"),
            "goblin_level_25": (25, 4, 350, 22, 17, 15, 17.0, (4, 6, 8), "goblin_level_25.plugin.kts"),
        }

        shared_drops = COMBAT_ENEMY_DATA["goblin_level_5"]["drops"]
        for target_id, (level, speed, hp, attack, strength, defence, slayer_xp, bonuses, source_file) in expected_rows.items():
            goblin = COMBAT_ENEMY_DATA[target_id]
            self.assertEqual(goblin["display_name"], "Goblin")
            self.assertEqual(goblin["level"], level)
            self.assertEqual(goblin["group"], "Goblins")
            self.assertEqual(goblin["attack_speed"], speed)
            self.assertEqual(goblin["respawn_delay"], 35)
            self.assertEqual(goblin["slayer_xp"], slayer_xp)
            self.assertEqual(goblin["stats"]["hitpoints"], hp)
            self.assertEqual(goblin["stats"]["attack"], attack)
            self.assertEqual(goblin["stats"]["strength"], strength)
            self.assertEqual(goblin["stats"]["defence"], defence)
            self.assertEqual(
                (goblin["bonuses"]["attack_stab"], goblin["bonuses"]["attack_slash"], goblin["bonuses"]["attack_crush"]),
                bonuses,
            )
            self.assertIs(goblin["drops"], shared_drops)
            self.assertIn(source_file, goblin["source"])

        main, charms, tertiary = shared_drops["tables"]
        self.assertEqual(shared_drops["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 128)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 127)
        self.assertEqual(main["total"] - sum(slot["slots"] for slot in main["slots"]), 1)
        self.assertEqual(main["slots"][0], {"item": "Bronze spear", "quantity": 1, "slots": 9})
        self.assertEqual(main["slots"][2], {"item": "Bronze scimitar", "quantity": 1, "slots": 1})
        self.assertEqual(main["slots"][7], {"item": "Bronze javelin", "quantity": 5, "slots": 2})
        self.assertEqual(main["slots"][20]["slots"], 2)
        self.assertEqual(main["slots"][20]["table"]["name"], "Minor herb")
        self.assertEqual(charms["total"], 1024)
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 6})

    def test_al_kharid_warrior_row_matches_source_and_nested_minor_herbs(self):
        warrior = COMBAT_ENEMY_DATA["al_kharid_warrior"]

        self.assertEqual(warrior["level"], 9)
        self.assertEqual(warrior["group"], "Humanoids")
        self.assertEqual(warrior["attack_speed"], 4)
        self.assertEqual(warrior["respawn_delay"], 25)
        self.assertEqual(warrior["stats"]["hitpoints"], 190)
        self.assertEqual(warrior["stats"]["attack"], 7)
        self.assertEqual(warrior["stats"]["strength"], 5)
        self.assertEqual(warrior["stats"]["defence"], 4)
        self.assertEqual(warrior["bonuses"]["attack_stab"], 10)
        self.assertEqual(warrior["bonuses"]["attack_slash"], 10)
        self.assertEqual(warrior["bonuses"]["attack_crush"], 10)
        self.assertEqual(warrior["bonuses"]["melee_strength"], 9)

        main, tertiary = warrior["drops"]["tables"]
        self.assertEqual(warrior["drops"]["guaranteed"], (("Bones", 1),))
        self.assertEqual(main["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in main["slots"]), 1024)
        self.assertEqual(main["slots"][0], {"item": "Bronze med helm", "quantity": 1, "slots": 16})
        self.assertEqual(main["slots"][2], {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 146})
        self.assertEqual(main["slots"][8]["slots"], 84)
        minor_herbs = main["slots"][8]["table"]
        self.assertEqual(minor_herbs["total"], 1024)
        self.assertEqual(sum(slot["slots"] for slot in minor_herbs["slots"]), 1024)
        self.assertEqual(minor_herbs["slots"][0], {"item": "Grimy guam", "quantity": 1, "slots": 249})
        self.assertEqual(minor_herbs["slots"][-1], {"item": "Grimy dwarf weed", "quantity": 1, "slots": 24})
        self.assertEqual(tertiary["slots"][0], {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8})
        self.assertIn("alkharid_warrior_level_9.plugin.kts", warrior["source"])

    def test_giant_spider_quantity_range_drop_rolls_inclusive_high(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["giant_spider"],
            _rng([0.0, 0.999999, 0.999999, 0.999999, 0.999999]),
        )

        self.assertEqual(drops, {"Air rune": 6})

    def test_highwayman_quantity_range_drop_rolls_with_guaranteed_cape(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["highwayman"],
            _rng([0.0, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Cape": 1, "Iron bolts": 12})

    def test_barbarian_drop_rolls_include_main_charms_and_tertiary_tables(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["barbarian"],
            _rng([0.0, 0.0, 0.0]),
        )

        self.assertEqual(drops, {"Bones": 1, "Bronze hatchet": 1, "Gold charm": 1, "Clue scroll (easy)": 1})

    def test_barbarian_level_10_drop_rolls_include_tail_main_slot(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["barbarian_level_10"],
            _rng([0.999999, 0.999999, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Ring mould": 1})

    def test_goblin_level_2_drop_rolls_include_main_charms_and_tertiary_tables(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["goblin_level_2_unarmed"],
            _rng([0.0, 0.0, 0.0]),
        )

        self.assertEqual(drops, {"Bones": 1, "Bronze sq shield": 1, "Gold charm": 1, "Clue scroll (easy)": 1})

    def test_higher_goblin_drop_rolls_nested_minor_herb_table(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["goblin_level_11"],
            _rng([118 / 128, 0.0, 0.999999, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Grimy guam": 1})

    def test_al_kharid_warrior_drop_rolls_nested_minor_herb_table(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["al_kharid_warrior"],
            _rng([250 / 1024, 0.0, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Grimy guam": 1})

    def test_al_kharid_warrior_quantity_range_drop_rolls(self):
        drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["al_kharid_warrior"],
            _rng([24 / 1024, 0.999999, 0.999999]),
        )

        self.assertEqual(drops, {"Bones": 1, "Bronze bolts": 12})

    def test_scorpion_and_higher_spider_drop_rolls_use_source_tables(self):
        scorpion_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["scorpion"], _rng([0.03]))
        deadly_red_drops = _combat_roll_drops(COMBAT_ENEMY_DATA["deadly_red_spider"], _rng([0.259]))
        giant_drops = _combat_roll_drops(
            COMBAT_ENEMY_DATA["giant_spider_level_50"],
            _rng([0.0, 0.999999, 0.999999, 0.999999, 0.999999]),
        )

        self.assertEqual(scorpion_drops, {"Green charm": 1})
        self.assertEqual(deadly_red_drops, {"Gold charm": 1})
        self.assertEqual(giant_drops, {"Air rune": 6})

    def test_cow_calf_burst_grants_source_guaranteed_drops(self):
        player = _player(current_combat_target="cow_calf")

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=500,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["combat_kill_counts"], {"cow_calf": 1})
        self.assertEqual(new_data["inventory"]["Bones"], 1)
        self.assertEqual(new_data["inventory"]["Raw beef"], 1)
        self.assertEqual(new_data["inventory"]["Cowhide"], 1)

    def test_combat_burst_kills_once_awards_xp_and_rolls_source_backed_drops(self):
        player = _player()

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=500,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["combat_kill_counts"], {"chicken": 1})
        self.assertEqual(new_data["combat_encounter"], {})
        self.assertGreater(new_data["attack_exp"], 0)
        self.assertGreater(new_data["constitution_exp"], 0)
        self.assertEqual(new_data["inventory"]["Bones"], 1)
        self.assertEqual(new_data["inventory"]["Raw chicken"], 1)
        self.assertEqual(new_data["inventory"]["Feather"], 5)

    def test_aggressive_style_routes_melee_xp_to_strength(self):
        player = _player(combat_attack_style="aggressive")

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["attack_exp"], 0.0)
        self.assertGreater(new_data["strength_exp"], 0.0)

    def test_ranged_style_requires_supported_weapon_and_ammo(self):
        player = _player(combat_attack_style="ranged_accurate")

        self.assertEqual(
            combat_target_locked_reasons_pure(player, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("ranged weapon",),
        )

        with_bow = _player(combat_attack_style="ranged_accurate", equipment={"weapon": "Shortbow"})
        self.assertEqual(
            combat_target_locked_reasons_pure(with_bow, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("compatible ammunition",),
        )

        with_ammo = _player(
            combat_attack_style="ranged_accurate",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 3},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_ammo, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

    def test_ranged_burst_consumes_bronze_arrows_and_awards_ranged_xp(self):
        player = _player(
            combat_attack_style="ranged_accurate",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 2},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(result["combat_class"], "ranged")
        self.assertEqual(result["weapon"], "Shortbow")
        self.assertEqual(result["ammo"], "Bronze arrows")
        self.assertEqual(result["ammo_used"], {"Bronze arrows": 1})
        self.assertEqual(result["formula_source"], RANGED_FORMULA_SOURCE_PATH)
        self.assertEqual(result["xp_source"], RANGED_STRATEGY_SOURCE_PATH)
        self.assertEqual(new_data["inventory"]["Bronze arrows"], 0)
        self.assertEqual(new_data["combat_supply_loadout"]["ammo"], {"Bronze arrows": 1})
        self.assertEqual(new_data["attack_exp"], 0.0)
        self.assertGreater(new_data["ranged_exp"], 0.0)
        self.assertGreater(new_data["constitution_exp"], 0.0)

    def test_ranged_burst_accepts_higher_arrow_tiers_for_supported_bows(self):
        player = _player(
            combat_attack_style="ranged_accurate",
            equipment={"weapon": "Magic shortbow"},
            inventory={"Rune arrows": 2},
            current_combat_target="giant_rat",
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["weapon"], "Magic shortbow")
        self.assertEqual(result["ammo"], "Rune arrows")
        self.assertEqual(result["ammo_used"], {"Rune arrows": 1})
        self.assertEqual(new_data["combat_supply_loadout"]["ammo"], {"Rune arrows": 1})

    def test_ranged_longrange_splits_xp_between_ranged_and_defense(self):
        player = _player(
            combat_attack_style="ranged_longrange",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 2},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.0, 0.999999, 0.0]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertGreater(new_data["ranged_exp"], 0.0)
        self.assertAlmostEqual(new_data["ranged_exp"], new_data["defense_exp"])
        self.assertEqual(new_data["attack_exp"], 0.0)

    def test_magic_style_requires_wind_strike_runes(self):
        player = _player(combat_attack_style="magic_standard", inventory={})

        self.assertEqual(
            combat_target_locked_reasons_pure(player, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("runes: Air rune x1, Mind rune x1",),
        )

        with_runes = _player(
            combat_attack_style="magic_standard",
            inventory={"Air rune": 1, "Mind rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_runes, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

        with_staff = _player(
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff of air"},
            inventory={"Mind rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_staff, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

    def test_fire_strike_requires_level_and_uses_source_runes(self):
        underleveled = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_strike",
            magic_level=12,
            inventory={"Air rune": 1, "Mind rune": 1, "Fire rune": 3},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(underleveled, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("Magic level 13",),
        )

        with_fire_staff = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_strike",
            magic_level=13,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 1, "Mind rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_fire_staff, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

    def test_fire_wave_requires_level_and_blood_runes(self):
        underleveled = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_wave",
            magic_level=74,
            inventory={"Air rune": 5, "Fire rune": 7, "Blood rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(underleveled, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("Magic level 75",),
        )

        missing_blood = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_wave",
            magic_level=75,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 5},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(missing_blood, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            ("runes: Blood rune x1",),
        )

        with_fire_staff = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_wave",
            magic_level=75,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 5, "Blood rune": 1},
        )
        self.assertEqual(
            combat_target_locked_reasons_pure(with_fire_staff, "chicken", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA),
            (),
        )

    def test_magic_burst_consumes_wind_strike_runes_and_awards_magic_xp(self):
        player = _player(
            combat_attack_style="magic_standard",
            inventory={"Air rune": 2, "Mind rune": 2},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.0, 0.999999, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["combat_class"], "magic")
        self.assertEqual(result["spell_id"], "wind_strike")
        self.assertEqual(result["spell"], "Wind Strike")
        self.assertEqual(result["runes_used"], {"Air rune": 1, "Mind rune": 1})
        self.assertEqual(result["formula_source"], MAGIC_FORMULA_SOURCE_PATH)
        self.assertEqual(result["xp_source"], MAGIC_STRATEGY_SOURCE_PATH)
        self.assertEqual(new_data["inventory"]["Air rune"], 0)
        self.assertEqual(new_data["inventory"]["Mind rune"], 0)
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {"Air rune": 1, "Mind rune": 1})
        self.assertEqual(new_data["attack_exp"], 0.0)
        self.assertEqual(new_data["ranged_exp"], 0.0)
        self.assertGreater(new_data["magic_exp"], 5.5)
        self.assertGreater(new_data["constitution_exp"], 0.0)

    def test_magic_staff_substitution_does_not_load_or_consume_covered_rune(self):
        player = _player(
            combat_attack_style="magic_standard",
            equipment={"weapon": "Staff of air"},
            inventory={"Mind rune": 2},
            combat_supply_loadout={"runes": {"Air rune": 1}},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.0, 0.999999, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["runes_used"], {"Mind rune": 1})
        self.assertEqual(new_data["inventory"]["Air rune"], 1)
        self.assertEqual(new_data["inventory"]["Mind rune"], 0)
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {"Mind rune": 1})
        self.assertGreater(new_data["magic_exp"], 5.5)

    def test_fire_strike_with_staff_consumes_only_uncovered_runes(self):
        player = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_strike",
            magic_level=13,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 1, "Mind rune": 1},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["spell_id"], "fire_strike")
        self.assertEqual(result["spell"], "Fire Strike")
        self.assertEqual(result["runes_used"], {"Air rune": 1, "Mind rune": 1})
        self.assertEqual(new_data["inventory"].get("Fire rune", 0), 0)
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {})
        self.assertAlmostEqual(new_data["magic_exp"], 11.5)

    def test_fire_wave_with_staff_consumes_blood_and_air_runes_and_awards_base_xp_on_splash(self):
        player = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_wave",
            magic_level=75,
            equipment={"weapon": "Staff of fire"},
            inventory={"Air rune": 5, "Blood rune": 1},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(result["spell_id"], "fire_wave")
        self.assertEqual(result["spell"], "Fire Wave")
        self.assertEqual(result["runes_used"], {"Air rune": 5, "Blood rune": 1})
        self.assertEqual(new_data["inventory"].get("Fire rune", 0), 0)
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {})
        self.assertAlmostEqual(new_data["magic_exp"], 42.5)
        self.assertEqual(new_data["constitution_exp"], 0.0)

    def test_magic_splash_consumes_runes_and_awards_base_spell_xp(self):
        player = _player(
            combat_attack_style="magic_standard",
            inventory={"Air rune": 1, "Mind rune": 1},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["player_damage"], 0)
        self.assertEqual(result["runes_used"], {"Air rune": 1, "Mind rune": 1})
        self.assertAlmostEqual(new_data["magic_exp"], 5.5)
        self.assertEqual(new_data["constitution_exp"], 0.0)

    def test_active_magic_encounter_does_not_refill_runes_mid_fight(self):
        player = _player(
            combat_attack_style="magic_standard",
            inventory={"Air rune": 5, "Mind rune": 5},
            combat_supply_loadout={"runes": {"Air rune": 1, "Mind rune": 1}},
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 30},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=10,
            rng=_rng([0.999999] * 8),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["stop_reason"], "out_of_runes")
        self.assertEqual(result["runes_used"], {"Air rune": 1, "Mind rune": 1})
        self.assertEqual(new_data["inventory"]["Air rune"], 5)
        self.assertEqual(new_data["inventory"]["Mind rune"], 5)
        self.assertEqual(new_data["combat_supply_loadout"]["runes"], {})

    def test_active_ranged_encounter_does_not_refill_ammo_mid_fight(self):
        player = _player(
            combat_attack_style="ranged_rapid",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 5},
            combat_supply_loadout={"ammo": {"Bronze arrows": 1}},
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 30},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=10,
            rng=_rng([0.999999] * 8),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["stop_reason"], "out_of_ammo")
        self.assertEqual(result["ammo_used"], {"Bronze arrows": 1})
        self.assertEqual(new_data["inventory"]["Bronze arrows"], 5)
        self.assertEqual(new_data["combat_supply_loadout"]["ammo"], {})

    def test_ranged_rapid_uses_faster_bow_attack_speed(self):
        player = _player(
            combat_attack_style="ranged_rapid",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 10},
            current_combat_target="giant_rat",
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=7,
            rng=_rng([0.999999] * 12),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["ammo_used"], {"Bronze arrows": 3})
        self.assertEqual(new_data["combat_supply_loadout"]["ammo"], {"Bronze arrows": 7})

    def test_combat_burst_caps_to_one_kill_per_review_even_with_many_ticks(self):
        player = _player(current_combat_target="cow")

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1000,
            rng=_rng([0.0, 0.999999, 0.999999, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(new_data["combat_kill_counts"], {"cow": 1})

    def test_auto_eat_consumes_food_after_enemy_damage_under_threshold(self):
        player = _player(
            attack_level=1,
            strength_level=1,
            defense_level=1,
            inventory={"Shrimps": 1},
            combat_lifepoints=20,
            combat_auto_eat_threshold_percent=90,
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["died"])
        self.assertEqual(new_data["inventory"]["Shrimps"], 0)
        self.assertEqual(new_data["combat_supply_loadout"]["food"], {})
        self.assertEqual(result["food_used"], ({"item": "Shrimps", "healed_by": 30},))
        self.assertGreater(new_data["combat_lifepoints"], 20)

    def test_active_encounter_does_not_refill_food_loadout_from_bank_mid_fight(self):
        player = _player(
            current_combat_target="giant_rat",
            attack_level=1,
            strength_level=1,
            defense_level=1,
            inventory={"Shrimps": 1},
            combat_lifepoints=20,
            combat_auto_eat_threshold_percent=90,
            combat_encounter={"target_id": "giant_rat", "enemy_lifepoints": 50},
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertEqual(new_data["inventory"]["Shrimps"], 1)
        self.assertEqual(new_data["combat_supply_loadout"]["food"], {})
        self.assertEqual(result["food_used"], ())
        self.assertLess(new_data["combat_lifepoints"], 20)

    def test_combat_burst_regenerates_special_attack_energy_by_elapsed_ticks(self):
        player = _player(combat_special_attack_energy=40)

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=50,
            rng=_rng([0.999999] * 30),
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertEqual(result["ticks_elapsed"], 50)
        self.assertEqual(new_data["combat_special_attack_energy"], 50)

    def test_poison_status_uses_source_tick_formula_and_summary(self):
        player = _player()

        poisoned, ok, reason = apply_combat_poison_effect_pure(player, 3)

        self.assertTrue(ok, reason)
        self.assertEqual(combat_poison_ticks_for_initial_damage_pure(3), 11)
        self.assertEqual(combat_poison_damage_for_ticks_pure(11), 30)
        self.assertEqual(
            poisoned["combat_status_effects"]["poison"],
            {
                "ticks_left": 11,
                "tick_progress": 0,
                "source": "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/poison/Poison.kt",
            },
        )
        self.assertEqual(combat_status_summary_pure(poisoned), "Poisoned: 30 LP in 30 ticks")

    def test_safe_recovery_advances_poison_status_after_healing(self):
        player = _player(
            combat_lifepoints=40,
            combat_status_effects={
                "poison": {
                    "ticks_left": combat_poison_ticks_for_initial_damage_pure(3),
                    "tick_progress": 0,
                }
            },
        )

        recovered = apply_safe_combat_recovery_pure(player)

        self.assertEqual(recovered["combat_lifepoints"], 70)
        self.assertEqual(recovered["combat_status_effects"]["poison"]["ticks_left"], 10)
        self.assertEqual(recovered["combat_status_effects"]["poison"]["tick_progress"], 20)
        self.assertEqual(combat_status_summary_pure(recovered), "Poisoned: 30 LP in 10 ticks")

    def test_combat_burst_advances_poison_status_by_review_ticks(self):
        player = _player(
            combat_lifepoints=100,
            combat_status_effects={
                "poison": {
                    "ticks_left": combat_poison_ticks_for_initial_damage_pure(3),
                    "tick_progress": 29,
                }
            },
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=_rng([0.999999]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["died"])
        self.assertEqual(result["status_damage"], {"poison": 30})
        self.assertEqual(new_data["combat_lifepoints"], 70)
        self.assertEqual(new_data["combat_status_effects"]["poison"]["ticks_left"], 10)
        self.assertEqual(new_data["combat_status_effects"]["poison"]["tick_progress"], 0)

    def test_poison_enemy_applies_player_poison_on_source_chance(self):
        player = _player(
            current_combat_target="poison_scorpion",
            defense_level=1,
            combat_lifepoints=100,
        )

        new_data, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.999999, 0.0, 0.0, 0.0]),
        )

        self.assertTrue(ok)
        self.assertFalse(result["died"])
        self.assertEqual(result["status_applied"], {"poison": 30})
        self.assertEqual(result["status_damage"], {})
        self.assertEqual(new_data["combat_status_effects"]["poison"]["ticks_left"], 11)
        self.assertEqual(new_data["combat_status_effects"]["poison"]["tick_progress"], 0)
        self.assertEqual(combat_status_summary_pure(new_data), "Poisoned: 30 LP in 30 ticks")

    def test_safe_recovery_poison_death_uses_combat_grave_path(self):
        player = _player(
            combat_lifepoints=5,
            equipment={"weapon": "Iron sword"},
            combat_status_effects={
                "poison": {
                    "ticks_left": combat_poison_ticks_for_initial_damage_pure(11),
                    "tick_progress": 0,
                }
            },
        )

        recovered = apply_safe_combat_recovery_pure(player)

        self.assertEqual(recovered["combat_lifepoints"], 100)
        self.assertEqual(recovered["equipment"], {})
        self.assertEqual(recovered["combat_status_effects"], {})
        self.assertEqual(recovered["combat_grave"]["items"], ["Iron sword"])
        self.assertEqual(recovered["combat_grave"]["source"], "combat_poison_death")

    def test_safe_recovery_refills_loadout_regenerates_energy_and_recovers_drains(self):
        player = _player(
            inventory={"Shark": 30},
            combat_lifepoints=20,
            combat_special_attack_energy=35,
            combat_stat_drains={"attack": 2, "strength": 1},
            combat_recovery_progress={"stat_drain_ticks": 50},
            combat_auto_eat_food=["Shark"],
        )

        recovered = apply_safe_combat_recovery_pure(player)

        self.assertEqual(recovered["combat_lifepoints"], 100)
        self.assertEqual(recovered["combat_special_attack_energy"], 45)
        self.assertEqual(recovered["combat_stat_drains"], {"attack": 1})
        self.assertEqual(recovered["combat_recovery_progress"], {})
        self.assertEqual(recovered["combat_supply_loadout"]["food"], {"Shark": 28})
        self.assertEqual(recovered["inventory"]["Shark"], 2)

    def test_safe_recovery_refills_ranged_ammo_at_safe_boundary(self):
        player = _player(
            combat_attack_style="ranged_accurate",
            equipment={"weapon": "Shortbow"},
            inventory={"Bronze arrows": 12},
            combat_supply_loadout={"ammo": {"Bronze arrows": 3}},
        )

        recovered = apply_safe_combat_recovery_pure(player)

        self.assertEqual(recovered["combat_supply_loadout"]["ammo"], {"Bronze arrows": 15})
        self.assertEqual(recovered["inventory"]["Bronze arrows"], 0)

    def test_stacked_combat_death_moves_existing_grave_to_death_office(self):
        player = _player(
            current_combat_target="killer",
            attack_level=1,
            strength_level=1,
            combat_lifepoints=1,
            equipment={"weapon": "Iron sword"},
            combat_grave={"items": ["Bronze sword"], "reviews_remaining": 3, "source": "combat_death"},
            death_office={"items": ["Cape"], "source": "combat_stacked_grave"},
        )

        died, ok, result = apply_combat_burst_pure(
            player,
            _KILLER_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=5,
            rng=_rng([0.999999, 0.0, 0.999999]),
        )

        self.assertTrue(ok)
        self.assertTrue(result["died"])
        self.assertEqual(died["combat_grave"]["items"], ["Iron sword"])
        self.assertEqual(died["combat_grave"]["reviews_remaining"], 5)
        self.assertEqual(died["death_office"]["items"], ["Cape", "Bronze sword"])
        self.assertEqual(died["death_office"]["reclaim_cost"], 200)

    def test_death_office_reclaim_consumes_coins_and_returns_items_to_inventory(self):
        player = _player(
            inventory={"Coins": 250, "Bones": 1},
            death_office={"items": ["Bronze sword", "Cape"], "source": "combat_stacked_grave"},
        )

        self.assertEqual(combat_death_office_reclaim_cost_pure(player), 200)
        self.assertEqual(
            combat_death_office_summary_pure(player),
            {
                "items": ("Bronze sword", "Cape"),
                "item_count": 2,
                "reclaim_cost": 200,
                "coins": 250,
                "can_reclaim": True,
            },
        )

        reclaimed, ok, reason = reclaim_death_office_items_pure(player)

        self.assertTrue(ok, reason)
        self.assertEqual(reclaimed["inventory"]["Coins"], 50)
        self.assertEqual(reclaimed["inventory"]["Bones"], 1)
        self.assertEqual(reclaimed["inventory"]["Bronze sword"], 1)
        self.assertEqual(reclaimed["inventory"]["Cape"], 1)
        self.assertEqual(reclaimed["death_office"], {})

    def test_death_office_reclaim_requires_enough_coins(self):
        player = _player(
            inventory={"Coins": 99},
            death_office={"items": ["Bronze sword"], "source": "combat_stacked_grave"},
        )

        reclaimed, ok, reason = reclaim_death_office_items_pure(player)

        self.assertFalse(ok)
        self.assertIn("Need 100 Coins", reason)
        self.assertIs(reclaimed, player)
        self.assertEqual(player["inventory"], {"Coins": 99})

    def test_manual_refill_loadout_uses_food_queue_and_current_magic_spell(self):
        player = _player(
            combat_attack_style="magic_standard",
            current_combat_spell="fire_strike",
            equipment={"weapon": "Staff of fire"},
            inventory={"Shark": 30, "Air rune": 5, "Mind rune": 5, "Fire rune": 5},
            combat_auto_eat_food=["Shark"],
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(player, EQUIPMENT_DATA)

        self.assertTrue(ok, reason)
        self.assertEqual(refilled["combat_supply_loadout"]["food"], {"Shark": 28})
        self.assertEqual(refilled["combat_supply_loadout"]["runes"], {"Air rune": 5, "Mind rune": 5})
        self.assertEqual(refilled["inventory"]["Shark"], 2)
        self.assertEqual(refilled["inventory"]["Air rune"], 0)
        self.assertEqual(refilled["inventory"]["Mind rune"], 0)
        self.assertEqual(refilled["inventory"]["Fire rune"], 5)

    def test_manual_refill_loadout_blocks_inside_active_encounter(self):
        player = _player(
            inventory={"Shark": 30},
            combat_auto_eat_food=["Shark"],
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 30},
        )

        refilled, ok, reason = refill_combat_supply_loadout_pure(player, EQUIPMENT_DATA)

        self.assertFalse(ok)
        self.assertIn("active fight", reason)
        self.assertEqual(refilled["inventory"]["Shark"], 30)
        self.assertEqual(refilled["combat_supply_loadout"], {"food": {}, "potions": {}, "ammo": {}, "runes": {}, "cannonballs": 0})

    def test_unload_combat_supply_loadout_returns_supplies_to_bank(self):
        player = _player(
            inventory={"Shark": 2},
            combat_supply_loadout={
                "food": {"Shark": 3},
                "ammo": {"Bronze arrows": 5},
                "runes": {"Air rune": 7},
                "cannonballs": 2,
            },
        )

        unloaded, ok, reason = unload_combat_supply_loadout_pure(player)

        self.assertTrue(ok, reason)
        self.assertEqual(unloaded["inventory"]["Shark"], 5)
        self.assertEqual(unloaded["inventory"]["Bronze arrows"], 5)
        self.assertEqual(unloaded["inventory"]["Air rune"], 7)
        self.assertEqual(unloaded["inventory"]["Cannonball"], 2)
        self.assertEqual(unloaded["combat_supply_loadout"], {"food": {}, "potions": {}, "ammo": {}, "runes": {}, "cannonballs": 0})

    def test_combat_loadout_preferences_are_sanitized(self):
        player = _player(combat_auto_eat_food=["Shrimps", "Shark"], combat_auto_eat_threshold_percent=40)

        updated = set_combat_auto_eat_threshold_pure(player, 150)
        self.assertEqual(updated["combat_auto_eat_threshold_percent"], 99)

        updated, ok, reason = set_combat_auto_eat_food_pure(player, "Lobster")
        self.assertTrue(ok, reason)
        self.assertEqual(updated["combat_auto_eat_food"][:3], ["Lobster", "Shrimps", "Shark"])

        unchanged, ok, reason = set_combat_auto_eat_food_pure(player, "Burnt fish")
        self.assertFalse(ok)
        self.assertEqual(reason, "unsupported food")
        self.assertEqual(unchanged["combat_auto_eat_food"], ["Shrimps", "Shark"])

    def test_combat_preview_exposes_risk_and_source_metrics(self):
        preview = combat_target_preview_pure(_player(), "giant_rat", COMBAT_ENEMY_DATA, EQUIPMENT_DATA)

        self.assertEqual(preview["state"], "Ready")
        self.assertGreater(preview["accuracy"], 0)
        self.assertEqual(preview["enemy_max_lifepoints"], 50)
        self.assertTrue(str(preview["source"]).endswith("giant_rat_level_2.plugin.kts"))

    def test_combat_preview_marks_poison_enemies_as_food_advised(self):
        preview = combat_target_preview_pure(_player(), "poison_scorpion", COMBAT_ENEMY_DATA, EQUIPMENT_DATA)

        self.assertEqual(preview["risk_band"], "Food advised")
        self.assertEqual(preview["poison_damage"], 30)
        self.assertEqual(preview["poison_chance"], 0.4)


if __name__ == "__main__":
    unittest.main()
