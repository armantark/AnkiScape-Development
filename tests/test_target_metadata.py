import os
import unittest

from constants import (
    BIRD_NEST_OPEN_TABLES,
    BAR_IMAGES,
    COMBAT_ENEMY_DATA,
    COOKING_DATA,
    COOKING_ITEM_IMAGES,
    CRAFTED_ITEM_IMAGES,
    CRAFTING_DATA,
    DEFAULT_COMBAT_TARGET,
    DEFAULT_COOKING_TARGET,
    DEFAULT_FIREMAKING_TARGET,
    DEFAULT_FISHING_TARGET,
    DEFAULT_HUNTER_TARGET,
    DEFAULT_MINING_TARGET,
    DEFAULT_RUNECRAFTING_TARGET,
    DEFAULT_SMITHING_TARGET,
    DEFAULT_UTILITY_ACTIVITY,
    DEFAULT_WOODCUTTING_TARGET,
    FIREMAKING_DATA,
    FIREMAKING_ITEM_IMAGES,
    FISHING_DATA,
    FISHING_ITEM_IMAGES,
    FLETCHED_ITEM_IMAGES,
    FLETCHING_DATA,
    GEM_IMAGES,
    HUNTER_DATA,
    HUNTER_ITEM_IMAGES,
    EQUIPMENT_ITEM_DATA,
    MINING_PICKAXE_DATA,
    ORE_DATA,
    ORE_IMAGES,
    QUEST_UNLOCK_RULES,
    RUNECRAFTING_DATA,
    RUNECRAFTING_ITEM_IMAGES,
    RUNECRAFTING_POUCH_DATA,
    SMITHING_DATA,
    TREE_DATA,
    TREE_IMAGES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
    WOODCUTTING_AXE_DATA,
)
from target_metadata import (
    TargetRowMetadata,
    combat_target_rows,
    cooking_target_rows,
    crafting_target_rows,
    firemaking_target_rows,
    fishing_target_rows,
    fletching_target_rows,
    hunter_target_rows,
    mining_target_rows,
    runecrafting_target_rows,
    smithing_target_rows,
    utility_activity_rows,
    woodcutting_target_rows,
)


def _row(rows, target_id):
    for row in rows:
        if row.target_id == target_id:
            return row
    raise AssertionError(f"row {target_id!r} not found")


class TargetMetadataTest(unittest.TestCase):
    def test_combat_rows_expose_enabled_source_backed_enemy_targets(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "giant_rat",
                "combat_attack_style": "accurate",
                "attack_level": 10,
                "strength_level": 10,
                "defense_level": 10,
                "constitution_level": 10,
                "inventory": {"Shark": 2},
                "equipment": {},
                "combat_auto_eat_food": ["Shark"],
                "combat_supply_loadout": {"food": {"Shark": 1}},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        chicken = _row(rows, "chicken")
        giant_rat = _row(rows, "giant_rat")
        giant_rat_level_26 = _row(rows, "giant_rat_level_26")
        spider = _row(rows, "spider")
        giant_spider = _row(rows, "giant_spider")
        unicorn = _row(rows, "unicorn")
        black_unicorn = _row(rows, "black_unicorn")
        black_bear = _row(rows, "black_bear")
        wolf = _row(rows, "wolf")
        white_wolf = _row(rows, "white_wolf_level_25")
        big_wolf = _row(rows, "big_wolf")
        giant_bat = _row(rows, "giant_bat")
        hill_giant = _row(rows, "hill_giant")
        moss_giant = _row(rows, "moss_giant")
        ice_giant = _row(rows, "ice_giant")
        ghost = _row(rows, "ghost")
        zombie_level_13 = _row(rows, "zombie_level_13")
        zombie_level_25 = _row(rows, "zombie_level_25")
        skeleton_level_21 = _row(rows, "skeleton_level_21")
        skeleton_level_25 = _row(rows, "skeleton_level_25")
        duck_land = _row(rows, "duck_land")
        duck_water = _row(rows, "duck_water")
        goblin_unarmed = _row(rows, "goblin_level_2_unarmed")
        goblin_armed = _row(rows, "goblin_level_2_armed")
        goblin_level_11 = _row(rows, "goblin_level_11")
        cow = _row(rows, "cow")
        cow_calf = _row(rows, "cow_calf")
        farmer = _row(rows, "farmer")
        chaos_druid = _row(rows, "chaos_druid")
        highwayman = _row(rows, "highwayman")
        market_guard = _row(rows, "market_guard")
        pirate = _row(rows, "pirate")
        jail_guard = _row(rows, "jail_guard")
        black_knight = _row(rows, "black_knight")
        outlaw = _row(rows, "outlaw")
        white_knight_level_36 = _row(rows, "white_knight_level_36")
        white_knight_level_42 = _row(rows, "white_knight_level_42")
        monk_of_zamorak = _row(rows, "monk_of_zamorak_level_45")
        barbarian = _row(rows, "barbarian")
        barbarian_level_10 = _row(rows, "barbarian_level_10")
        barbarian_level_17 = _row(rows, "barbarian_level_17")
        seagull = _row(rows, "seagull")
        king_scorpion = _row(rows, "king_scorpion")
        pit_scorpion = _row(rows, "pit_scorpion")
        scorpion_level_59 = _row(rows, "scorpion_level_59")
        poison_spider_level_64 = _row(rows, "poison_spider_level_64")

        self.assertTrue(chicken.enabled)
        self.assertTrue(giant_rat.current)
        self.assertEqual(giant_rat.group, "Lumbridge")
        self.assertIn("Giant rat · combat level 2", giant_rat.tooltip)
        self.assertIn("Enemy LP: 50/50", giant_rat.tooltip)
        self.assertIn("Food: Shark x1 loaded + 2 bank", giant_rat.tooltip)
        self.assertIn("Raw rat meat", giant_rat.tooltip)
        self.assertIn("giant_rat_level_2.plugin.kts", giant_rat.tooltip)
        self.assertEqual(giant_rat_level_26.group, "Rats")
        self.assertIn("Giant rat · combat level 26", giant_rat_level_26.tooltip)
        self.assertIn("Enemy LP: 250/250", giant_rat_level_26.tooltip)
        self.assertIn("giant_rat_level_26.plugin.kts", giant_rat_level_26.tooltip)
        self.assertEqual(spider.group, "Spiders")
        self.assertIn("Gold charm x1 (5/200)", spider.tooltip)
        self.assertEqual(giant_spider.group, "Spiders")
        self.assertIn("Air rune x4-6 (7/48)", giant_spider.tooltip)
        self.assertIn("Staff of air", giant_spider.tooltip)
        self.assertIn("giant_spider_level_2.plugin.kts", giant_spider.tooltip)
        self.assertEqual(unicorn.group, "Animals")
        self.assertIn("Unicorn · combat level 15", unicorn.tooltip)
        self.assertIn("Unicorn horn", unicorn.tooltip)
        self.assertIn("Gold charm x1 (130/1000)", unicorn.tooltip)
        self.assertIn("unicorn_level_15.plugin.kts", unicorn.tooltip)
        self.assertEqual(black_unicorn.group, "Animals")
        self.assertIn("Black unicorn · combat level 27", black_unicorn.tooltip)
        self.assertIn("black_unicorn_level_27.plugin.kts", black_unicorn.tooltip)
        self.assertEqual(black_bear.group, "Animals")
        self.assertIn("Black bear · combat level 19", black_bear.tooltip)
        self.assertIn("Bear fur x1", black_bear.tooltip)
        self.assertIn("Raw bear meat x1", black_bear.tooltip)
        self.assertIn("Gold charm x1 (180/1000)", black_bear.tooltip)
        self.assertIn("black_bear_level_19.plugin.kts", black_bear.tooltip)
        self.assertEqual(wolf.group, "Animals")
        self.assertIn("Wolf · combat level 11", wolf.tooltip)
        self.assertIn("Wolf bones x1", wolf.tooltip)
        self.assertIn("Bones x1", wolf.tooltip)
        self.assertIn("Gold charm x1 (20/1000)", wolf.tooltip)
        self.assertIn("wolf_lvl_11.plugin.kts", wolf.tooltip)
        self.assertEqual(white_wolf.group, "Animals")
        self.assertIn("White wolf · combat level 25", white_wolf.tooltip)
        self.assertIn("Wolf bones x1", white_wolf.tooltip)
        self.assertIn("Crimson charm x1 (140/1000)", white_wolf.tooltip)
        self.assertIn("white_wolf_lvl_25.plugin.kts", white_wolf.tooltip)
        self.assertEqual(big_wolf.group, "Animals")
        self.assertIn("Big wolf · combat level 73", big_wolf.tooltip)
        self.assertIn("big_wolf_lvl_73.plugin.kts", big_wolf.tooltip)
        self.assertEqual(giant_bat.group, "Bats")
        self.assertIn("Giant bat · combat level 27", giant_bat.tooltip)
        self.assertIn("Bat bones x1", giant_bat.tooltip)
        self.assertIn("giant_bat_level_27.plugin.kts", giant_bat.tooltip)
        self.assertEqual(hill_giant.group, "Giants")
        self.assertIn("Hill giant · combat level 28", hill_giant.tooltip)
        self.assertIn("Big bones x1", hill_giant.tooltip)
        self.assertIn("Allotment seed table (18/128)", hill_giant.tooltip)
        self.assertIn("hill_giant_lvl_28.plugin.kts", hill_giant.tooltip)
        self.assertEqual(moss_giant.group, "Giants")
        self.assertIn("Moss giant · combat level 42", moss_giant.tooltip)
        self.assertIn("Uncommon seed table (35/128)", moss_giant.tooltip)
        self.assertIn("moss_giant_level_42.plugin.kts", moss_giant.tooltip)
        self.assertEqual(ice_giant.group, "Giants")
        self.assertIn("Ice giant · combat level 53", ice_giant.tooltip)
        self.assertIn("Black kiteshield x1 (32/1024)", ice_giant.tooltip)
        self.assertIn("Champion's scroll x1 (20/100000)", ice_giant.tooltip)
        self.assertIn("ice_giant_level_53.plugin.kts", ice_giant.tooltip)
        self.assertEqual(ghost.group, "Undead")
        self.assertIn("Ghost · combat level 19", ghost.tooltip)
        self.assertIn("No item drops", ghost.tooltip)
        self.assertIn("ghost_level_19.plugin.kts", ghost.tooltip)
        self.assertEqual(zombie_level_13.group, "Undead")
        self.assertIn("Zombie · combat level 13", zombie_level_13.tooltip)
        self.assertIn("Iron hatchet x1 (3/128)", zombie_level_13.tooltip)
        self.assertIn("Minor herb table (25/128)", zombie_level_13.tooltip)
        self.assertIn("zombie_lvl_13.plugin.kts", zombie_level_13.tooltip)
        self.assertEqual(zombie_level_25.group, "Undead")
        self.assertIn("Zombie · combat level 25", zombie_level_25.tooltip)
        self.assertIn("Iron hatchet x1 (5/128)", zombie_level_25.tooltip)
        self.assertIn("zombie_lvl_25.plugin.kts", zombie_level_25.tooltip)
        self.assertEqual(skeleton_level_21.group, "Undead")
        self.assertIn("Skeleton · combat level 21", skeleton_level_21.tooltip)
        self.assertIn("Bronze arrows x2 (56/1024)", skeleton_level_21.tooltip)
        self.assertIn("Gem table (8/1024)", skeleton_level_21.tooltip)
        self.assertIn("skeleton_lvl_21.plugin.kts", skeleton_level_21.tooltip)
        self.assertEqual(skeleton_level_25.group, "Undead")
        self.assertIn("Skeleton · combat level 25", skeleton_level_25.tooltip)
        self.assertIn("Iron med helm x1 (6/128)", skeleton_level_25.tooltip)
        self.assertIn("Minor herb table (20/128)", skeleton_level_25.tooltip)
        self.assertIn("skeleton_lvl_25.plugin.kts", skeleton_level_25.tooltip)
        self.assertEqual(duck_land.group, "Birds")
        self.assertIn("Duck (land) · combat level 1", duck_land.tooltip)
        self.assertIn("Bones", duck_land.tooltip)
        self.assertIn("land ids", duck_land.tooltip)
        self.assertEqual(duck_water.group, "Birds")
        self.assertIn("Duck (water) · combat level 1", duck_water.tooltip)
        self.assertIn("no death drop callback", duck_water.tooltip)
        self.assertEqual(goblin_unarmed.group, "Goblins")
        self.assertIn("Goblin (unarmed) · combat level 2", goblin_unarmed.tooltip)
        self.assertIn("Bronze spear x1 (32/1024)", goblin_unarmed.tooltip)
        self.assertIn("Goblin book x1 (16/1024)", goblin_unarmed.tooltip)
        self.assertIn("Clue scroll (easy) x1 (6/1024)", goblin_unarmed.tooltip)
        self.assertIn("unarmed ids", goblin_unarmed.tooltip)
        self.assertEqual(goblin_armed.group, "Goblins")
        self.assertIn("Goblin (armed) · combat level 2", goblin_armed.tooltip)
        self.assertIn("armed id", goblin_armed.tooltip)
        self.assertEqual(goblin_level_11.group, "Goblins")
        self.assertIn("Goblin · combat level 11", goblin_level_11.tooltip)
        self.assertIn("Bronze javelin x5 (2/128)", goblin_level_11.tooltip)
        self.assertIn("Minor herb table (2/128)", goblin_level_11.tooltip)
        self.assertIn("goblin_level_11.plugin.kts", goblin_level_11.tooltip)
        self.assertEqual(cow.sort_key[:2], (2, "Cow"))
        self.assertEqual(cow_calf.group, "Lumbridge")
        self.assertIn("Cowhide", cow_calf.tooltip)
        self.assertEqual(farmer.group, "Humanoids")
        self.assertIn("Farmer · combat level 7", farmer.tooltip)
        self.assertIn("Minor herb table (11/128)", farmer.tooltip)
        self.assertIn("Allotment seed table (27/128)", farmer.tooltip)
        self.assertIn("farmer_level_7.plugin.kts", farmer.tooltip)
        self.assertEqual(chaos_druid.group, "Humanoids")
        self.assertIn("Chaos druid · combat level 13", chaos_druid.tooltip)
        self.assertIn("Enemy LP: 200/200", chaos_druid.tooltip)
        self.assertIn("Mithril bolts x2-12 (5/128)", chaos_druid.tooltip)
        self.assertIn("Minor herb table (46/128)", chaos_druid.tooltip)
        self.assertIn("Vial of water x1 (10/128)", chaos_druid.tooltip)
        self.assertIn("Gem table (1/128)", chaos_druid.tooltip)
        self.assertIn("chaos_druid_lvl_13.plugin.kts", chaos_druid.tooltip)
        self.assertEqual(highwayman.group, "Humanoids")
        self.assertIn("Cape x1", highwayman.tooltip)
        self.assertIn("Iron bolts x2-12 (1/20)", highwayman.tooltip)
        self.assertIn("highwayman_level_5.plugin.kts", highwayman.tooltip)
        self.assertEqual(market_guard.group, "Humanoids")
        self.assertIn("Market guard · combat level 20", market_guard.tooltip)
        self.assertIn("Bones x1", market_guard.tooltip)
        self.assertIn("market_guard_level_20.plugin.kts", market_guard.tooltip)
        self.assertEqual(pirate.group, "Humanoids")
        self.assertIn("Pirate · combat level 23", pirate.tooltip)
        self.assertIn("Iron bolts x2-12 (80/1024)", pirate.tooltip)
        self.assertIn("Eye patch x1 (96/1024)", pirate.tooltip)
        self.assertIn("Gem table (8/1024)", pirate.tooltip)
        self.assertIn("pirate_level_23.plugin.kts", pirate.tooltip)
        self.assertEqual(jail_guard.group, "Humanoids")
        self.assertIn("Jail guard · combat level 26", jail_guard.tooltip)
        self.assertIn("Bones x1", jail_guard.tooltip)
        self.assertIn("jail_guard_level_26.plugin.kts", jail_guard.tooltip)
        self.assertEqual(black_knight.group, "Humanoids")
        self.assertIn("Black knight · combat level 33", black_knight.tooltip)
        self.assertIn("Enemy LP: 420/420", black_knight.tooltip)
        self.assertIn("Mithril arrows x3 (4/116)", black_knight.tooltip)
        self.assertIn("Allotment seed table (18/116)", black_knight.tooltip)
        self.assertIn("black_knight_level_33.plugin.kts", black_knight.tooltip)
        self.assertEqual(outlaw.group, "Humanoids")
        self.assertIn("Outlaw · combat level 35", outlaw.tooltip)
        self.assertIn("Enemy LP: 200/200", outlaw.tooltip)
        self.assertIn("Rope x1 (46/127)", outlaw.tooltip)
        self.assertIn("Minor herb table (32/127)", outlaw.tooltip)
        self.assertIn("Gold charm x1 (360/1000)", outlaw.tooltip)
        self.assertIn("outlaw_level_35.plugin.kts", outlaw.tooltip)
        self.assertEqual(white_knight_level_36.group, "Humanoids")
        self.assertIn("White knight · combat level 36", white_knight_level_36.tooltip)
        self.assertIn("Enemy LP: 520/520", white_knight_level_36.tooltip)
        self.assertIn("Body rune x9-13 (3/128)", white_knight_level_36.tooltip)
        self.assertIn("Half an apple pie x1 (1/128)", white_knight_level_36.tooltip)
        self.assertIn("Allotment seed table (15/128)", white_knight_level_36.tooltip)
        self.assertIn("white_knight_level_36.plugin.kts", white_knight_level_36.tooltip)
        self.assertEqual(white_knight_level_42.group, "Humanoids")
        self.assertIn("White knight · combat level 42", white_knight_level_42.tooltip)
        self.assertIn("Water rune x40-47 (3/127)", white_knight_level_42.tooltip)
        self.assertIn("Coins x51-55 (13/127)", white_knight_level_42.tooltip)
        self.assertIn("Allotment seed table (28/127)", white_knight_level_42.tooltip)
        self.assertIn("white_knight_level_42.plugin.kts", white_knight_level_42.tooltip)
        self.assertEqual(monk_of_zamorak.group, "Humanoids")
        self.assertIn("Monk of Zamorak · combat level 45", monk_of_zamorak.tooltip)
        self.assertIn("Zamorak robe top x1 (1/20)", monk_of_zamorak.tooltip)
        self.assertIn("Zamorak robe bottom x1 (1/20)", monk_of_zamorak.tooltip)
        self.assertIn("Green charm x1 (100/1000)", monk_of_zamorak.tooltip)
        self.assertIn("monk_of_zamorak_lvl_45.plugin.kts", monk_of_zamorak.tooltip)
        self.assertEqual(barbarian.group, "Humanoids")
        self.assertIn("Barbarian · combat level 8", barbarian.tooltip)
        self.assertIn("Enemy LP: 140/140", barbarian.tooltip)
        self.assertIn("Bronze hatchet x1 (48/1024)", barbarian.tooltip)
        self.assertIn("Staff x1 (32/1024)", barbarian.tooltip)
        self.assertIn("Coins x5 (341/1024)", barbarian.tooltip)
        self.assertIn("Clue scroll (easy) x1 (1/128)", barbarian.tooltip)
        self.assertIn("barbarian_lvl_8.plugin.kts", barbarian.tooltip)
        self.assertIn("barbarian_lvl_9.plugin.kts", barbarian.tooltip)
        self.assertEqual(barbarian_level_10.group, "Humanoids")
        self.assertIn("Barbarian · combat level 10", barbarian_level_10.tooltip)
        self.assertIn("Enemy LP: 180/180", barbarian_level_10.tooltip)
        self.assertIn("Bronze arrows x15 (24/1024)", barbarian_level_10.tooltip)
        self.assertIn("Law rune x2 (8/1024)", barbarian_level_10.tooltip)
        self.assertIn("barbarian_greataxe_lvl_10.plugin.kts", barbarian_level_10.tooltip)
        self.assertIn("barbarian_spear_lvl_10.plugin.kts", barbarian_level_10.tooltip)
        self.assertEqual(barbarian_level_17.group, "Humanoids")
        self.assertIn("Barbarian · combat level 17", barbarian_level_17.tooltip)
        self.assertIn("Enemy LP: 240/240", barbarian_level_17.tooltip)
        self.assertIn("Bronze hatchet x1 (48/1024)", barbarian_level_17.tooltip)
        self.assertIn("Crimson charm x1 (5/1000)", barbarian_level_17.tooltip)
        self.assertIn("barbarian_greataxe_lvl_17.plugin.kts", barbarian_level_17.tooltip)
        self.assertIn("barbarian_spear_lvl_17.plugin.kts", barbarian_level_17.tooltip)
        self.assertEqual(seagull.group, "Coastal")
        self.assertEqual(seagull.sort_key[:2], (2, "Seagull"))
        self.assertEqual(king_scorpion.group, "Scorpions")
        self.assertIn("King scorpion · combat level 32", king_scorpion.tooltip)
        self.assertIn("No item drops", king_scorpion.tooltip)
        self.assertIn("king_scorpion_level_32.plugin.kts", king_scorpion.tooltip)
        self.assertEqual(pit_scorpion.group, "Scorpions")
        self.assertIn("Pit scorpion · combat level 28", pit_scorpion.tooltip)
        self.assertIn("No item drops", pit_scorpion.tooltip)
        self.assertIn("pit_sorpion_lvl_28.plugin.kts", pit_scorpion.tooltip)
        self.assertEqual(scorpion_level_59.group, "Scorpions")
        self.assertIn("Scorpion · combat level 59", scorpion_level_59.tooltip)
        self.assertIn("Green charm x1 (70/1000)", scorpion_level_59.tooltip)
        self.assertIn("scorpion_level_59.plugin.kts", scorpion_level_59.tooltip)
        self.assertEqual(poison_spider_level_64.group, "Spiders")
        self.assertIn("Poison spider · combat level 64", poison_spider_level_64.tooltip)
        self.assertIn("Poison: 60 LP", poison_spider_level_64.tooltip)
        self.assertIn("poison_spider_lvl_64.plugin.kts", poison_spider_level_64.tooltip)

    def test_combat_rows_pass_equipment_data_for_ranged_ammo_locks(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "ranged_accurate",
                "ranged_level": 10,
                "defense_level": 10,
                "constitution_level": 10,
                "inventory": {"Bronze arrows": 50},
                "equipment": {"weapon": "Shortbow"},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        chicken = _row(rows, "chicken")

        self.assertTrue(chicken.enabled)
        self.assertIn("Your max hit:", chicken.tooltip)
        self.assertIn("Ammo: Bronze arrows x0 loaded + 50 bank", chicken.tooltip)

    def test_combat_rows_mark_death_possible_targets_for_confirmation(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_lifepoints": 20,
                "constitution_level": 10,
                "inventory": {},
                "equipment": {},
                "combat_auto_eat_food": ["Shark"],
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        barbarian = _row(rows, "barbarian_level_10")
        safe_rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_lifepoints": 100,
                "constitution_level": 10,
                "inventory": {},
                "equipment": {},
                "combat_auto_eat_food": ["Shark"],
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        safe_chicken = _row(safe_rows, "chicken")

        self.assertTrue(barbarian.enabled)
        self.assertTrue(barbarian.requires_confirmation)
        self.assertEqual(barbarian.confirmation_title, "Confirm dangerous combat")
        self.assertIn("Death possible", barbarian.tooltip)
        self.assertIn("Confirmation required before selecting this target.", barbarian.tooltip)
        self.assertIn("Barbarian is marked Death possible", barbarian.confirmation_message)
        self.assertFalse(safe_chicken.requires_confirmation)

    def test_combat_rows_show_magic_spell_and_rune_supply(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "magic_standard",
                "current_combat_spell": "wind_strike",
                "magic_level": 10,
                "defense_level": 10,
                "constitution_level": 10,
                "inventory": {"Air rune": 5, "Mind rune": 5},
                "equipment": {},
                "combat_supply_loadout": {"runes": {"Air rune": 1, "Mind rune": 1}},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        chicken = _row(rows, "chicken")

        self.assertTrue(chicken.enabled)
        self.assertIn("Spell: Wind Strike", chicken.tooltip)
        self.assertIn("Rune: Air rune x1; 1 loaded + 5 bank", chicken.tooltip)
        self.assertIn("Rune: Mind rune x1; 1 loaded + 5 bank", chicken.tooltip)

    def test_combat_rows_show_staff_covered_magic_runes(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "magic_standard",
                "current_combat_spell": "wind_strike",
                "magic_level": 10,
                "defense_level": 10,
                "constitution_level": 10,
                "inventory": {"Mind rune": 5},
                "equipment": {"weapon": "Staff of air"},
                "combat_supply_loadout": {"runes": {"Mind rune": 1}},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        chicken = _row(rows, "chicken")

        self.assertTrue(chicken.enabled)
        self.assertIn("Rune: Air rune x1; covered by Staff of air", chicken.tooltip)
        self.assertIn("Rune: Mind rune x1; 1 loaded + 5 bank", chicken.tooltip)

    def test_combat_rows_show_fire_wave_rune_supply(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "magic_standard",
                "current_combat_spell": "fire_wave",
                "magic_level": 75,
                "defense_level": 75,
                "constitution_level": 75,
                "inventory": {"Air rune": 10, "Blood rune": 3},
                "equipment": {"weapon": "Staff of fire"},
                "combat_supply_loadout": {"runes": {"Air rune": 5}},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        chicken = _row(rows, "chicken")

        self.assertTrue(chicken.enabled)
        self.assertIn("Spell: Fire Wave", chicken.tooltip)
        self.assertIn("Rune: Air rune x5; 5 loaded + 10 bank", chicken.tooltip)
        self.assertIn("Rune: Fire rune x7; covered by Staff of fire", chicken.tooltip)
        self.assertIn("Rune: Blood rune x1; 0 loaded + 3 bank", chicken.tooltip)

    def test_combat_rows_lock_magic_without_required_runes(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "magic_standard",
                "current_combat_spell": "wind_strike",
                "magic_level": 10,
                "defense_level": 10,
                "constitution_level": 10,
                "inventory": {},
                "equipment": {},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        chicken = _row(rows, "chicken")

        self.assertFalse(chicken.enabled)
        self.assertEqual(chicken.locked_reasons, ("runes: Air rune x1, Mind rune x1",))
        self.assertIn("Locked due to: runes: Air rune x1, Mind rune x1", chicken.tooltip)

    def test_smithing_grouped_rows_preserve_tier_sort_and_lock_reasons(self):
        rows = smithing_target_rows(
            {
                "smithing_level": 33,
                "inventory": {},
                "current_smith": "smelt_bronze_bar",
            },
            SMITHING_DATA,
            BAR_IMAGES,
            DEFAULT_SMITHING_TARGET,
        )

        bronze = _row(rows, "smelt_bronze_bar")
        rune_platebody = _row(rows, "forge_rune_platebody")

        self.assertEqual(bronze.group, "Bronze")
        self.assertTrue(bronze.current)
        self.assertFalse(bronze.enabled)
        self.assertIn("materials", bronze.locked_reasons)
        self.assertIn("Copper ore x1 (you have 0)", bronze.tooltip)
        self.assertEqual(bronze.sort_key[:2], (1, 0))
        self.assertFalse(rune_platebody.enabled)
        self.assertIn("level 99", rune_platebody.locked_reasons)
        self.assertNotIn("hammer", bronze.tooltip.lower())

    def test_crafting_grouped_rows_preserve_family_material_locks_and_live_targets(self):
        rows = crafting_target_rows(
            {
                "crafting_level": 99,
                "inventory": {},
                "current_craft": "cut_dragonstone",
            },
            CRAFTING_DATA,
            CRAFTED_ITEM_IMAGES,
        )

        dragonstone = _row(rows, "cut_dragonstone")
        gold_ring = _row(rows, "jewellery_gold_ring")

        self.assertEqual(dragonstone.group, "gems")
        self.assertTrue(dragonstone.current)
        self.assertFalse(dragonstone.enabled)
        self.assertEqual(dragonstone.locked_reasons, ("materials",))
        self.assertIn("Uncut dragonstone", dragonstone.tooltip)
        self.assertNotIn("input-starved", dragonstone.label.lower())
        self.assertNotIn("coming soon", dragonstone.tooltip.lower())
        self.assertEqual(gold_ring.group, "jewellery")

    def test_cooking_grouped_rows_apply_quest_unlock_rules_once(self):
        player_data = {
            "cooking_level": 99,
            "inventory": {"Slimy eel": 1, "Raw yak meat": 1},
            "quests": {},
            "current_cooking": "cook_slimy_eel",
        }
        rows = cooking_target_rows(
            player_data,
            COOKING_DATA,
            COOKING_ITEM_IMAGES,
            DEFAULT_COOKING_TARGET,
            QUEST_UNLOCK_RULES,
        )

        slimy_eel = _row(rows, "cook_slimy_eel")
        yak = _row(rows, "cook_yak")
        self.assertEqual(slimy_eel.group, "eels")
        self.assertTrue(slimy_eel.current)
        self.assertFalse(slimy_eel.enabled)
        self.assertEqual(slimy_eel.locked_reasons, ("Priest in Peril",))
        self.assertIn("Locked due to: Priest in Peril", slimy_eel.tooltip)
        self.assertFalse(yak.enabled)
        self.assertEqual(yak.locked_reasons, ("The Fremennik Isles",))

        player_data["quests"] = {
            "priest_in_peril": {"started": True, "progress": 6, "completed": True},
            "the_fremennik_isles": {"started": True, "progress": 6, "completed": True},
        }
        unlocked_rows = cooking_target_rows(
            player_data,
            COOKING_DATA,
            COOKING_ITEM_IMAGES,
            DEFAULT_COOKING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "cook_slimy_eel").enabled)
        self.assertTrue(_row(unlocked_rows, "cook_yak").enabled)

    def test_mining_rows_preserve_current_icon_and_deferred_note_contract(self):
        rows = mining_target_rows(
            {
                "mining_level": 33,
                "inventory": {},
                "toolbelt": {"mining": ["bronze_pickaxe"]},
                "current_ore": "coal",
            },
            ORE_DATA,
            ORE_IMAGES,
            GEM_IMAGES,
            MINING_PICKAXE_DATA,
            DEFAULT_MINING_TARGET,
            {"coal": "Concentrated coal deposits are deferred."},
        )

        coal = _row(rows, "coal")
        runite = _row(rows, "runite")

        self.assertIsInstance(coal, TargetRowMetadata)
        self.assertEqual(coal.label, "Coal (Lvl 30)")
        self.assertTrue(coal.current)
        self.assertTrue(coal.enabled)
        self.assertEqual(coal.icon_path, ORE_IMAGES["Coal"])
        self.assertIn("Best usable pickaxe: Bronze pickaxe", coal.tooltip)
        self.assertIn("Concentrated coal deposits are deferred.", coal.tooltip)
        self.assertFalse(runite.enabled)
        self.assertIn("level 85", runite.tooltip)

    def test_mining_rows_apply_quest_unlock_rules(self):
        rows = mining_target_rows(
            {
                "mining_level": 33,
                "inventory": {},
                "toolbelt": {"mining": ["bronze_pickaxe"]},
                "current_ore": "rune_essence",
            },
            ORE_DATA,
            ORE_IMAGES,
            GEM_IMAGES,
            MINING_PICKAXE_DATA,
            DEFAULT_MINING_TARGET,
            quest_unlock_rules=QUEST_UNLOCK_RULES,
        )

        rune_essence = _row(rows, "rune_essence")
        self.assertFalse(rune_essence.enabled)
        self.assertIn("Locked due to: Rune Mysteries", rune_essence.tooltip)

    def test_woodcutting_rows_preserve_xp_only_and_tool_lock_contract(self):
        rows = woodcutting_target_rows(
            {
                "woodcutting_level": 1,
                "inventory": {},
                "toolbelt": {"woodcutting": []},
                "current_tree": "ivy",
            },
            TREE_DATA,
            TREE_IMAGES,
            WOODCUTTING_AXE_DATA,
            DEFAULT_WOODCUTTING_TARGET,
        )

        tree = _row(rows, "tree")
        ivy = _row(rows, "ivy")

        self.assertFalse(tree.enabled)
        self.assertIn("no usable hatchet", tree.tooltip)
        self.assertEqual(ivy.label, "Ivy (Lvl 68) — XP only")
        self.assertTrue(ivy.current)
        self.assertIn("XP only — produces no logs.", ivy.tooltip)

    def test_fletching_rows_preserve_stable_id_material_lock_and_current_target(self):
        rows = fletching_target_rows(
            {
                "fletching_level": 99,
                "inventory": {},
                "current_fletch": "arrow_shafts",
            },
            FLETCHING_DATA,
            FLETCHED_ITEM_IMAGES,
            QUEST_UNLOCK_RULES,
        )

        shafts = _row(rows, "arrow_shafts")

        self.assertEqual(shafts.label, "Arrow shafts (Logs) (Lvl 1)")
        self.assertTrue(shafts.current)
        self.assertFalse(shafts.enabled)
        self.assertEqual(shafts.icon_path, FLETCHED_ITEM_IMAGES["Arrow shafts"])
        self.assertEqual(shafts.group, "whittling")
        self.assertIn("Logs x1 (you have 0)", shafts.tooltip)
        self.assertIn("Locked due to: materials", shafts.tooltip)

    def test_fletching_rows_apply_broad_fletching_unlock_rule(self):
        player_data = {
            "fletching_level": 99,
            "inventory": {
                "Headless arrows": 15,
                "Broad arrow heads": 15,
                "Unfinished broad bolts": 10,
                "Feather": 10,
            },
            "current_fletch": "broad_arrows",
            "unlocked_abilities": [],
        }
        rows = fletching_target_rows(player_data, FLETCHING_DATA, FLETCHED_ITEM_IMAGES, QUEST_UNLOCK_RULES)

        broad_arrows = _row(rows, "broad_arrows")
        broad_bolts = _row(rows, "feather_broad_bolts")

        self.assertEqual(broad_arrows.group, "arrows")
        self.assertFalse(broad_arrows.enabled)
        self.assertIn("Broad Fletching", broad_arrows.tooltip)
        self.assertFalse(broad_bolts.enabled)
        self.assertIn("Broad Fletching", broad_bolts.tooltip)

        player_data["unlocked_abilities"] = ["broad_fletching"]
        unlocked_rows = fletching_target_rows(player_data, FLETCHING_DATA, FLETCHED_ITEM_IMAGES, QUEST_UNLOCK_RULES)
        self.assertTrue(_row(unlocked_rows, "broad_arrows").enabled)
        self.assertTrue(_row(unlocked_rows, "feather_broad_bolts").enabled)

    def test_firemaking_rows_preserve_success_tooltip_and_default_current_target(self):
        rows = firemaking_target_rows(
            {
                "firemaking_level": 45,
                "inventory": {"Logs": 2, "Oak logs": 1},
            },
            FIREMAKING_DATA,
            FIREMAKING_ITEM_IMAGES,
            DEFAULT_FIREMAKING_TARGET,
        )

        logs = _row(rows, "logs")
        oak = _row(rows, "oak_logs")

        self.assertTrue(logs.current)
        self.assertTrue(oak.enabled)
        self.assertEqual(logs.icon_path, FIREMAKING_ITEM_IMAGES["Logs"])
        self.assertIn("Base XP: 40.0 per successful burn", logs.tooltip)
        self.assertIn("Input: Logs x1 (you have 2)", logs.tooltip)
        self.assertIn("Output: Ashes x1", logs.tooltip)
        self.assertIn("Success chance:", logs.tooltip)
        self.assertNotIn("FiremakingData.kt", logs.tooltip)

    def test_firemaking_rows_apply_region_quest_unlock_rules(self):
        player_data = {
            "firemaking_level": 99,
            "inventory": {"Arctic pine logs": 1},
            "current_firemaking": "arctic_pine_logs",
            "quests": {},
        }
        rows = firemaking_target_rows(
            player_data,
            FIREMAKING_DATA,
            FIREMAKING_ITEM_IMAGES,
            DEFAULT_FIREMAKING_TARGET,
            QUEST_UNLOCK_RULES,
        )

        arctic_pine = _row(rows, "arctic_pine_logs")
        self.assertFalse(arctic_pine.enabled)
        self.assertIn("The Fremennik Isles", arctic_pine.tooltip)

        player_data["quests"]["the_fremennik_isles"] = {"started": True, "progress": 6, "completed": True}
        unlocked_rows = firemaking_target_rows(
            player_data,
            FIREMAKING_DATA,
            FIREMAKING_ITEM_IMAGES,
            DEFAULT_FIREMAKING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "arctic_pine_logs").enabled)

    def test_fishing_rows_preserve_material_and_side_level_gates(self):
        rows = fishing_target_rows(
            {
                "fishing_level": 48,
                "strength_level": 1,
                "agility_level": 1,
                "inventory": {},
            },
            FISHING_DATA,
            FISHING_ITEM_IMAGES,
            DEFAULT_FISHING_TARGET,
        )

        sardine = _row(rows, "catch_sardine_herring")
        shrimp = _row(rows, "catch_shrimp_anchovies")
        leaping = _row(rows, "catch_leaping_fish")

        self.assertEqual(shrimp.label, "Catch shrimp (Lvl 1)/anchovies (Lvl 15)")
        self.assertEqual(sardine.label, "Catch sardine (Lvl 5)/herring (Lvl 10)")
        self.assertEqual(
            leaping.label,
            "Catch leaping trout (Lvl 48)/leaping salmon (Lvl 58)/leaping sturgeon (Lvl 70)",
        )
        self.assertFalse(sardine.enabled)
        self.assertIn("Materials: Fishing bait x1 (you have 0)", sardine.tooltip)
        self.assertIn("materials", sardine.tooltip)
        self.assertFalse(leaping.enabled)
        self.assertIn("side levels", leaping.tooltip)
        self.assertNotIn("rod", leaping.tooltip.lower())
        self.assertNotIn("harpoon", leaping.tooltip.lower())

    def test_fishing_rows_apply_quest_unlock_rules(self):
        rows = fishing_target_rows(
            {
                "fishing_level": 99,
                "strength_level": 99,
                "agility_level": 99,
                "inventory": {"Fishing bait": 1},
            },
            FISHING_DATA,
            FISHING_ITEM_IMAGES,
            DEFAULT_FISHING_TARGET,
            QUEST_UNLOCK_RULES,
        )

        monkfish = _row(rows, "catch_monkfish")
        karambwan = _row(rows, "catch_karambwan")
        slimy_eel = _row(rows, "catch_slimy_eel")
        self.assertFalse(monkfish.enabled)
        self.assertIn("Swan Song", monkfish.tooltip)
        self.assertFalse(karambwan.enabled)
        self.assertIn("Tai Bwo Wannai Trio", karambwan.tooltip)
        self.assertFalse(slimy_eel.enabled)
        self.assertIn("Priest in Peril", slimy_eel.tooltip)

    def test_hunter_rows_preserve_material_locks_and_current_target(self):
        rows = hunter_target_rows(
            {
                "hunter_level": 23,
                "inventory": {"Logs": 1},
                "current_hunter": "catch_wild_kebbit",
            },
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )

        wild_kebbit = _row(rows, "catch_wild_kebbit")
        barb_tailed = _row(rows, "catch_barb_tailed_kebbit")

        self.assertEqual(wild_kebbit.group, "deadfall")
        self.assertTrue(wild_kebbit.current)
        self.assertTrue(wild_kebbit.enabled)
        self.assertEqual(wild_kebbit.icon_path, HUNTER_ITEM_IMAGES["Kebbit claws"])
        self.assertIn("Outputs: Bones x1, Kebbit claws x1", wild_kebbit.tooltip)
        self.assertIn("Base XP: 128.0 per successful catch", wild_kebbit.tooltip)
        self.assertIn("Success chance:", wild_kebbit.tooltip)
        self.assertIn("Logs x1 (you have 1)", wild_kebbit.tooltip)
        self.assertIn("Reusable tools:", wild_kebbit.tooltip)
        self.assertIn("No reusable tools required", wild_kebbit.tooltip)
        self.assertFalse(barb_tailed.enabled)
        self.assertEqual(barb_tailed.locked_reasons, ("Hunter level 33",))

        locked_rows = hunter_target_rows(
            {
                "hunter_level": 23,
                "inventory": {},
                "current_hunter": "catch_wild_kebbit",
            },
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )
        locked_wild_kebbit = _row(locked_rows, "catch_wild_kebbit")
        self.assertFalse(locked_wild_kebbit.enabled)
        self.assertEqual(locked_wild_kebbit.locked_reasons, ("materials",))
        self.assertIn("Locked due to: materials", locked_wild_kebbit.tooltip)

        bird_rows = hunter_target_rows(
            {
                "hunter_level": 1,
                "inventory": {},
                "current_hunter": "catch_crimson_swift",
            },
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )
        crimson_swift = _row(bird_rows, "catch_crimson_swift")
        self.assertFalse(crimson_swift.enabled)
        self.assertEqual(crimson_swift.locked_reasons, ("Bird snare",))
        self.assertIn("Bird snare x1 (you have 0)", crimson_swift.tooltip)

    def test_hunter_rows_apply_quest_unlock_rules(self):
        player_data = {
            "hunter_level": 99,
            "inventory": {
                "Box trap": 1,
                "Butterfly net": 1,
                "Impling jar": 1,
                "Small fishing net": 1,
                "Rope": 1,
            },
            "quests": {},
            "current_hunter": "catch_ferret",
        }
        rows = hunter_target_rows(
            player_data,
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )

        ferret = _row(rows, "catch_ferret")
        pirate = _row(rows, "catch_pirate_impling_world")
        swamp_lizard = _row(rows, "catch_swamp_lizard")
        self.assertFalse(ferret.enabled)
        self.assertEqual(ferret.locked_reasons, ("Eagles' Peak",))
        self.assertIn("Eagles' Peak", ferret.tooltip)
        self.assertFalse(pirate.enabled)
        self.assertIn("Rocking Out", pirate.tooltip)
        self.assertFalse(swamp_lizard.enabled)
        self.assertIn("Priest in Peril", swamp_lizard.tooltip)

        player_data["quests"] = {
            "eagles_peak": {"started": True, "progress": 6, "completed": True},
            "rocking_out": {"started": True, "progress": 6, "completed": True},
            "priest_in_peril": {"started": True, "progress": 6, "completed": True},
        }
        unlocked_rows = hunter_target_rows(
            player_data,
            HUNTER_DATA,
            HUNTER_ITEM_IMAGES,
            DEFAULT_HUNTER_TARGET,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "catch_ferret").enabled)
        self.assertTrue(_row(unlocked_rows, "catch_pirate_impling_world").enabled)
        self.assertTrue(_row(unlocked_rows, "catch_swamp_lizard").enabled)

    def test_runecrafting_rows_apply_quest_unlock_rules(self):
        player_data = {
            "runecrafting_level": 99,
            "inventory": {"Pure essence": 1, "Cosmic talisman": 1},
            "equipment": {},
            "wicked_hood": {"fed_altars": []},
            "runecrafting_pouches": {},
            "quests": {
                "rune_mysteries": {"started": True, "progress": 6, "completed": True},
            },
            "current_runecrafting": "craft_cosmic_runes",
        }
        rows = runecrafting_target_rows(
            player_data,
            RUNECRAFTING_DATA,
            RUNECRAFTING_ITEM_IMAGES,
            RUNECRAFTING_POUCH_DATA,
            DEFAULT_RUNECRAFTING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        cosmic = _row(rows, "craft_cosmic_runes")
        self.assertFalse(cosmic.enabled)
        self.assertEqual(cosmic.locked_reasons, ("Lost City",))
        self.assertEqual(cosmic.group, "standard")
        self.assertEqual(cosmic.sort_key[:1], (27,))
        self.assertIn("Lost City", cosmic.tooltip)

        player_data["quests"]["lost_city"] = {"started": True, "progress": 6, "completed": True}
        unlocked_rows = runecrafting_target_rows(
            player_data,
            RUNECRAFTING_DATA,
            RUNECRAFTING_ITEM_IMAGES,
            RUNECRAFTING_POUCH_DATA,
            DEFAULT_RUNECRAFTING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "craft_cosmic_runes").enabled)

    def test_utility_rows_preserve_activity_icons_no_xp_text_and_locks(self):
        rows = utility_activity_rows(
            {"inventory": {}, "current_utility": "scavenge_chicken_feathers"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )

        feathers = _row(rows, "scavenge_chicken_feathers")
        nests = _row(rows, "open_bird_nest")

        self.assertTrue(feathers.current)
        self.assertTrue(feathers.enabled)
        self.assertEqual(os.path.basename(feathers.icon_path or ""), "scavenge_chicken_feathers.png")
        self.assertIn("No skill XP", feathers.tooltip)
        self.assertIn("Output: Feather x1", feathers.tooltip)
        self.assertIn("No materials required", feathers.tooltip)
        self.assertFalse(nests.enabled)
        self.assertIn("No XP", nests.tooltip)
        self.assertIn("Locked: cut trees until a bird nest drops.", nests.tooltip)

        hunter_supplies = _row(rows, "buy_hunter_supplies")
        self.assertFalse(hunter_supplies.enabled)
        self.assertIn("Runs once, then switches off", hunter_supplies.tooltip)
        self.assertIn("Bird snare x1", hunter_supplies.tooltip)
        self.assertIn("Butterfly jar x10", hunter_supplies.tooltip)
        self.assertIn("Coins x500 (you have 0)", hunter_supplies.tooltip)

        funded_rows = utility_activity_rows(
            {"inventory": {"Coins": 500}, "current_utility": "buy_hunter_supplies"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )
        funded_hunter_supplies = _row(funded_rows, "buy_hunter_supplies")
        self.assertTrue(funded_hunter_supplies.current)
        self.assertTrue(funded_hunter_supplies.enabled)
        self.assertEqual(os.path.basename(funded_hunter_supplies.icon_path or ""), "bird_snare.png")

    def test_utility_rows_apply_region_quest_unlock_rules(self):
        rows = utility_activity_rows(
            {"inventory": {}, "current_utility": "gather_thin_snails"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
            QUEST_UNLOCK_RULES,
        )

        snails = _row(rows, "gather_thin_snails")
        yak = _row(rows, "scavenge_raw_yak_meat")
        self.assertFalse(snails.enabled)
        self.assertIn("Priest in Peril", snails.tooltip)
        self.assertFalse(yak.enabled)
        self.assertIn("The Fremennik Isles", yak.tooltip)

        unlocked_rows = utility_activity_rows(
            {
                "inventory": {},
                "quests": {
                    "priest_in_peril": {"started": True, "progress": 6, "completed": True},
                    "the_fremennik_isles": {"started": True, "progress": 6, "completed": True},
                },
            },
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "gather_thin_snails").enabled)
        self.assertTrue(_row(unlocked_rows, "scavenge_raw_yak_meat").enabled)


if __name__ == "__main__":
    unittest.main()
