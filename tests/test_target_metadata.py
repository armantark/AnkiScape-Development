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
    HERBLORE_DATA,
    HERBLORE_ITEM_IMAGES,
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
    SUMMONING_ITEM_IMAGES,
    WOODCUTTING_AXE_DATA,
)
from target_metadata import (
    TargetRowMetadata,
    agility_target_rows,
    combat_target_rows,
    cooking_target_rows,
    crafting_target_rows,
    firemaking_target_rows,
    fishing_target_rows,
    fletching_target_rows,
    hunter_target_rows,
    herblore_target_rows,
    mining_target_rows,
    runecrafting_target_rows,
    smithing_target_rows,
    summoning_target_rows,
    thieving_target_rows,
    utility_activity_rows,
    woodcutting_target_rows,
)
from agility_data import AGILITY_ITEM_IMAGES, AGILITY_TARGETS, DEFAULT_AGILITY_TARGET
from thieving_data import DEFAULT_THIEVING_TARGET, THIEVING_ITEM_IMAGES, THIEVING_TARGETS
from summoning_data import (
    DEFAULT_SUMMONING_TARGET,
    SUMMONING_ACTIONS,
    SUMMONING_POUCHES_BY_ID,
)


def _row(rows, target_id):
    for row in rows:
        if row.target_id == target_id:
            return row
    raise AssertionError(f"row {target_id!r} not found")


class TargetMetadataTest(unittest.TestCase):
    def test_summoning_rows_expose_all_targets_and_exact_recipe_state(self):
        rows = summoning_target_rows(
            {
                "summoning_level": 99,
                "current_summoning": "infuse_spiritwolf",
                "inventory": {
                    "Pouch": 1,
                    "Spirit shards": 7,
                    "Gold charm": 1,
                    "Wolf bones": 1,
                },
            },
            SUMMONING_ACTIONS,
            SUMMONING_POUCHES_BY_ID,
            SUMMONING_ITEM_IMAGES,
            DEFAULT_SUMMONING_TARGET,
        )

        self.assertEqual(len(rows), 145)
        spirit_wolf = _row(rows, "infuse_spiritwolf")
        self.assertTrue(spirit_wolf.enabled)
        self.assertTrue(spirit_wolf.current)
        self.assertEqual(spirit_wolf.group, "Infuse pouches")
        self.assertIn("Spirit shards x7 (you have 7)", spirit_wolf.tooltip)
        self.assertIn("Output: Spirit wolf pouch x1", spirit_wolf.tooltip)
        self.assertIsNotNone(spirit_wolf.icon_path)

        scroll = _row(rows, "scroll_calltoarms")
        self.assertFalse(scroll.enabled)
        self.assertEqual(scroll.group, "Create scrolls")
        self.assertIn("Output: Call to arms scroll x10", scroll.tooltip)

    def test_cockatrice_row_warns_about_missing_mirror_shield_without_locking_combat(self):
        rows = combat_target_rows(
            {
                "attack_level": 60,
                "strength_level": 60,
                "defense_level": 60,
                "ranged_level": 60,
                "magic_level": 60,
                "constitution_level": 60,
                "combat_lifepoints": 600,
                "inventory": {},
                "equipment": {},
                "current_combat_target": "cockatrice",
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        cockatrice = _row(rows, "cockatrice")
        self.assertTrue(cockatrice.enabled)
        self.assertIn("Missing Mirror shield", cockatrice.tooltip)
        self.assertIn("fixed damage and stat drain", cockatrice.tooltip)

    def test_banshee_row_warns_about_missing_earmuffs_without_locking_combat(self):
        rows = combat_target_rows(
            {
                "attack_level": 60,
                "strength_level": 60,
                "defense_level": 60,
                "ranged_level": 60,
                "magic_level": 60,
                "constitution_level": 60,
                "inventory": {},
                "equipment": {},
                "current_combat_target": "banshee",
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        banshee = _row(rows, "banshee")
        self.assertTrue(banshee.enabled)
        self.assertIn("Missing Earmuffs", banshee.tooltip)
        self.assertIn("drain eight skills", banshee.tooltip)

    def test_wilderness_agility_row_exposes_pker_food_and_grave_risk(self):
        rows = agility_target_rows(
            {
                "agility_level": 99,
                "current_agility": "wilderness_course",
                "inventory": {},
                "equipment": {},
            },
            AGILITY_TARGETS,
            AGILITY_ITEM_IMAGES,
            DEFAULT_AGILITY_TARGET,
        )

        wilderness = _row(rows, "wilderness_course")
        self.assertIn("1% PKer ambush", wilderness.tooltip)
        self.assertIn("maximum hit 250 LP", wilderness.tooltip)
        self.assertIn("carried food and grave rules apply", wilderness.tooltip)

    def test_thieving_rows_show_pickpocket_and_wall_safe_damage_ranges(self):
        rows = thieving_target_rows(
            {"thieving_level": 99, "current_thieving": DEFAULT_THIEVING_TARGET},
            THIEVING_TARGETS,
            THIEVING_ITEM_IMAGES,
            DEFAULT_THIEVING_TARGET,
        )

        self.assertIn("10–30 LP damage", _row(rows, "pickpocket_female_ham").tooltip)
        self.assertIn("20–60 LP damage", _row(rows, "wall_safe").tooltip)

    def test_cannonball_row_shows_quest_tool_output_and_rs_wiki_icon(self):
        from constants import SMITHING_EXTRA_ITEM_IMAGES

        inventory = {"Steel bar": 1, "Ammo mould": 1}
        smithing_images = dict(BAR_IMAGES)
        smithing_images.update(SMITHING_EXTRA_ITEM_IMAGES)
        locked_rows = smithing_target_rows(
            {"smithing_level": 35, "inventory": inventory, "quests": {}},
            SMITHING_DATA,
            smithing_images,
            DEFAULT_SMITHING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        self.assertFalse(_row(locked_rows, "forge_cannonballs").enabled)

        rows = smithing_target_rows(
            {
                "smithing_level": 35,
                "inventory": inventory,
                "quests": {"dwarf_cannon": {"completed": True}},
                "current_smith": "forge_cannonballs",
            },
            SMITHING_DATA,
            smithing_images,
            DEFAULT_SMITHING_TARGET,
            QUEST_UNLOCK_RULES,
        )
        cannonballs = _row(rows, "forge_cannonballs")
        self.assertTrue(cannonballs.enabled)
        self.assertTrue(cannonballs.current)
        self.assertIsNotNone(cannonballs.icon_path)
        self.assertIn("Output: Cannonball x4", cannonballs.tooltip)
        self.assertIn("Required tools:", cannonballs.tooltip)
        self.assertIn("Ammo mould x1", cannonballs.tooltip)
    def test_overload_row_exposes_exact_inputs_byproduct_and_icon(self):
        inputs = dict(HERBLORE_DATA["finished_overload"]["requirements"])
        rows = herblore_target_rows(
            {
                "current_herblore": "finished_overload",
                "herblore_level": 96,
                "inventory": inputs,
            },
            HERBLORE_DATA,
            HERBLORE_ITEM_IMAGES,
        )
        overload = _row(rows, "finished_overload")
        self.assertTrue(overload.enabled)
        self.assertTrue(overload.current)
        self.assertIsNotNone(overload.icon_path)
        self.assertIn("Base XP: 1000.0", overload.tooltip)
        self.assertIn("Byproduct: Vial x4", overload.tooltip)
        self.assertIn("Extreme ranging (3) x1", overload.tooltip)

    def test_combat_rows_expose_enabled_source_backed_enemy_targets(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "giant_rat",
                "combat_attack_style": "accurate",
                "attack_level": 10,
                "strength_level": 10,
                "defense_level": 10,
                "constitution_level": 10,
                "slayer_level": 99,
                "inventory": {"Shark": 2},
                "equipment": {},
                "combat_auto_eat_food": ["Shark"],
                "combat_supply_loadout": {
                    "food": {"Shark": 1},
                    "finishers": {"Ice cooler": 2},
                    "hazards": {"Waterskin (4)": 1},
                },
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
        hobgoblin_unarmed = _row(rows, "hobgoblin_unarmed")
        hobgoblin_armed = _row(rows, "hobgoblin_armed")
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
        chaos_dwarf = _row(rows, "chaos_dwarf")
        haakon = _row(rows, "haakon_the_champion")
        ham_guard_level_12 = _row(rows, "ham_guard_level_12")
        ham_guard_level_22 = _row(rows, "ham_guard_level_22")
        imp = _row(rows, "imp")
        tzhaar_ket = _row(rows, "tzhaar_ket")
        monk_of_zamorak = _row(rows, "monk_of_zamorak_level_45")
        barbarian = _row(rows, "barbarian")
        barbarian_level_10 = _row(rows, "barbarian_level_10")
        barbarian_level_17 = _row(rows, "barbarian_level_17")
        seagull = _row(rows, "seagull")
        king_scorpion = _row(rows, "king_scorpion")
        pit_scorpion = _row(rows, "pit_scorpion")
        scorpion_level_59 = _row(rows, "scorpion_level_59")
        poison_spider_level_64 = _row(rows, "poison_spider_level_64")
        desert_lizard = _row(rows, "desert_lizard")

        self.assertTrue(chicken.enabled)
        self.assertTrue(giant_rat.current)
        self.assertEqual(giant_rat.group, "Lumbridge")
        self.assertIn("Giant rat · combat level 2", giant_rat.tooltip)
        self.assertIn("Enemy LP: 50/50", giant_rat.tooltip)
        self.assertIn("Food: Shark x1 loaded + 2 bank", giant_rat.tooltip)
        self.assertIn("Raw rat meat", giant_rat.tooltip)
        self.assertIn("giant_rat_level_2.plugin.kts", giant_rat.tooltip)
        self.assertIn(
            "Finisher: Use Ice cooler at 1–30 LP · 2 loaded",
            desert_lizard.tooltip,
        )
        self.assertIn(
            "Desert heat: 1 Waterskin dose per Combat review · 1 loaded + 0 bank",
            desert_lizard.tooltip,
        )
        self.assertIn("oldid=6548273", desert_lizard.tooltip)
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
        self.assertEqual(hobgoblin_unarmed.group, "Hobgoblins")
        self.assertIn("Hobgoblin (unarmed) · combat level 28", hobgoblin_unarmed.tooltip)
        self.assertIn("Enemy LP: 290/290", hobgoblin_unarmed.tooltip)
        self.assertIn("Iron spear x1 (2/127)", hobgoblin_unarmed.tooltip)
        self.assertIn("Allotment seed table (18/127)", hobgoblin_unarmed.tooltip)
        self.assertIn("hobgoblin_unarmed_level_28.plugin.kts", hobgoblin_unarmed.tooltip)
        self.assertEqual(hobgoblin_armed.group, "Hobgoblins")
        self.assertIn("Hobgoblin (armed) · combat level 28", hobgoblin_armed.tooltip)
        self.assertIn("Enemy LP: 490/490", hobgoblin_armed.tooltip)
        self.assertIn("Iron javelin x5 (2/128)", hobgoblin_armed.tooltip)
        self.assertIn("Uncommon seed table (12/128)", hobgoblin_armed.tooltip)
        self.assertIn("hobgoblin_armed_lvl_28.plugin.kts", hobgoblin_armed.tooltip)
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
        self.assertEqual(chaos_dwarf.group, "Humanoids")
        self.assertIn("Chaos dwarf · combat level 48", chaos_dwarf.tooltip)
        self.assertIn("Enemy LP: 610/610", chaos_dwarf.tooltip)
        self.assertIn("Muddy key x1 (7/128)", chaos_dwarf.tooltip)
        self.assertIn("Mithril bar x1 (6/128)", chaos_dwarf.tooltip)
        self.assertIn("Green charm x1 (50/1000)", chaos_dwarf.tooltip)
        self.assertIn("chaos_dwarf_lvl_48.plugin.kts", chaos_dwarf.tooltip)
        self.assertEqual(haakon.group, "Humanoids")
        self.assertIn("Haakon the Champion · combat level 29", haakon.tooltip)
        self.assertIn("Enemy LP: 350/350", haakon.tooltip)
        self.assertIn("Bronze battleaxe x1 (32/1024)", haakon.tooltip)
        self.assertIn("Coins x8 (317/1024)", haakon.tooltip)
        self.assertIn("Clue scroll (easy) x1 (1/128)", haakon.tooltip)
        self.assertIn("haakon_the_champion_lvl_29.plugin.kts", haakon.tooltip)
        self.assertEqual(ham_guard_level_12.group, "Humanoids")
        self.assertIn("H.A.M. guard · combat level 12", ham_guard_level_12.tooltip)
        self.assertIn("Enemy LP: 150/150", ham_guard_level_12.tooltip)
        self.assertIn("H.A.M. gloves x1 (15/648)", ham_guard_level_12.tooltip)
        self.assertIn("Allotment seed table (57/648)", ham_guard_level_12.tooltip)
        self.assertIn("Clue scroll (easy) x1 (1/55)", ham_guard_level_12.tooltip)
        self.assertIn("ham_guard_level_12_18_22.plugin.kts", ham_guard_level_12.tooltip)
        self.assertEqual(ham_guard_level_22.group, "Humanoids")
        self.assertIn("H.A.M. guard · combat level 22", ham_guard_level_22.tooltip)
        self.assertIn("Enemy LP: 300/300", ham_guard_level_22.tooltip)
        self.assertIn("Coins x1-20 (81/648)", ham_guard_level_22.tooltip)
        self.assertIn("Thread x1-10 (12/648)", ham_guard_level_22.tooltip)
        self.assertEqual(imp.group, "Demons")
        self.assertIn("Imp · combat level 2", imp.tooltip)
        self.assertIn("Enemy LP: 80/80", imp.tooltip)
        self.assertIn("Impious ashes x1", imp.tooltip)
        self.assertIn("Black bead x1 (40/1024)", imp.tooltip)
        self.assertIn("Wizard hat x1 (64/1024)", imp.tooltip)
        self.assertIn("Chef's hat x1 (16/1024)", imp.tooltip)
        self.assertIn("imp_level_2.plugin.kts", imp.tooltip)
        self.assertEqual(tzhaar_ket.group, "TzHaar")
        self.assertIn("TzHaar-Ket · combat level 149", tzhaar_ket.tooltip)
        self.assertIn("Enemy LP: 1400/1400", tzhaar_ket.tooltip)
        self.assertIn("Tokkul x100-2000 (69/128)", tzhaar_ket.tooltip)
        self.assertIn("Fire battlestaff x1 (1/128)", tzhaar_ket.tooltip)
        self.assertIn("Tzhaar-ket-om x1 (1/512)", tzhaar_ket.tooltip)
        self.assertIn("Obsidian charm x2 (720/1000)", tzhaar_ket.tooltip)
        self.assertIn("tzhaar_ket_lvl_149.plugin.kts", tzhaar_ket.tooltip)
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

    def test_mutated_zygomite_rows_show_access_and_charged_spray_state(self):
        player = {
            "current_combat_target": "mutated_zygomite_level_74",
            "combat_attack_style": "accurate",
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "slayer_level": 57,
            "inventory": {},
            "equipment": {},
            "combat_supply_loadout": {
                "finishers": {
                    "Fungicide spray 7": 1,
                    "Fungicide": 2,
                },
            },
        }
        locked_rows = combat_target_rows(
            player,
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        locked = _row(locked_rows, "mutated_zygomite_level_74")
        self.assertFalse(locked.enabled)
        self.assertIn("Complete Lost City", locked.locked_reasons)

        player["quests"] = {"lost_city": {"completed": True}}
        ready_rows = combat_target_rows(
            player,
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        ready = _row(ready_rows, "mutated_zygomite_level_74")
        self.assertTrue(ready.enabled)
        self.assertIn(
            "Finisher: Spray with fungicide at 1–19 LP · "
            "7 spray charges + 2 canister reloads",
            ready.tooltip,
        )
        self.assertIn("Encounter: Pick the fungi", ready.tooltip)
        self.assertIn("oldid=6530349", ready.tooltip)

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

    def test_combat_rows_only_show_encounter_target_while_that_encounter_is_active(self):
        player_data = {
            "current_combat_target": "chicken",
            "combat_attack_style": "accurate",
            "attack_level": 10,
            "strength_level": 10,
            "defense_level": 10,
            "constitution_level": 10,
            "inventory": {},
            "equipment": {},
            "combat_supply_loadout": {},
        }

        ordinary_rows = combat_target_rows(
            player_data,
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        self.assertNotIn("menaphite_thug", {row.target_id for row in ordinary_rows})

        unrelated_encounter_rows = combat_target_rows(
            {**player_data, "combat_encounter": {"target_id": "chicken", "enemy_lifepoints": 30}},
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        self.assertNotIn("menaphite_thug", {row.target_id for row in unrelated_encounter_rows})

        active_encounter_rows = combat_target_rows(
            {
                **player_data,
                "current_combat_target": "menaphite_thug",
                "combat_encounter": {"target_id": "menaphite_thug", "enemy_lifepoints": 600},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        menaphite = _row(active_encounter_rows, "menaphite_thug")
        self.assertTrue(menaphite.enabled)
        self.assertTrue(menaphite.current)

    def test_combat_rows_use_enemy_images_instead_of_bones_fallback(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_attack_style": "accurate",
                "constitution_level": 10,
                "equipment": {},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {"Bones": "/tmp/bones.png"},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
            {"chicken": "/tmp/chicken.png"},
        )

        self.assertEqual(_row(rows, "chicken").icon_path, "/tmp/chicken.png")
        self.assertIsNone(_row(rows, "rat").icon_path)

    def test_ogre_row_exposes_the_live_seed_table_and_period_asset(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "ogre",
                "combat_attack_style": "accurate",
                "attack_level": 60,
                "strength_level": 60,
                "defense_level": 60,
                "constitution_level": 60,
                "slayer_level": 60,
                "inventory": {},
                "equipment": {},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
            {"ogre": "/tmp/ogre.png"},
        )

        ogre = _row(rows, "ogre")
        self.assertTrue(ogre.enabled)
        self.assertTrue(ogre.current)
        self.assertEqual(ogre.group, "Slayer")
        self.assertEqual(ogre.icon_path, "/tmp/ogre.png")
        self.assertIn("Ogre common seed table (19/128)", ogre.tooltip)
        self.assertIn("Guaranteed: Big bones x1", ogre.tooltip)
        self.assertIn("oldid=6565807", ogre.tooltip)

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

    def test_earth_warrior_row_requires_explicit_wilderness_risk_confirmation(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_lifepoints": 990,
                "constitution_level": 99,
                "inventory": {},
                "equipment": {
                    "weapon": "Rune sword",
                    "body": "Rune platebody",
                    "head": "Rune full helm",
                    "shield": "Iron kiteshield",
                },
                "combat_auto_eat_food": ["Shark"],
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        earth_warrior = _row(rows, "earth_warrior")

        self.assertTrue(earth_warrior.requires_confirmation)
        self.assertEqual(
            earth_warrior.confirmation_title,
            "Confirm Wilderness combat",
        )
        self.assertIn("1% PKer-ambush risk", earth_warrior.confirmation_message)
        self.assertIn("creates no grave", earth_warrior.confirmation_message)
        self.assertIn(
            "Wilderness risk confirmation required",
            earth_warrior.tooltip,
        )
        self.assertIn("keep 3 equipped", earth_warrior.tooltip)

    def test_green_dragon_row_exposes_dragonfire_and_wilderness_risk_together(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "combat_lifepoints": 990,
                "constitution_level": 99,
                "inventory": {},
                "equipment": {"shield": "Anti-dragon shield"},
                "combat_auto_eat_food": ["Shark"],
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        green_dragon = _row(rows, "green_dragon")

        self.assertTrue(green_dragon.requires_confirmation)
        self.assertIn(
            "Current dragonfire protection: Partial (maximum 50 LP).",
            green_dragon.confirmation_message,
        )
        self.assertIn(
            "Dragonfire: Partial protection · maximum hit 50 LP · 1/4 attacks",
            green_dragon.tooltip,
        )
        self.assertIn("Dragon bones x1", green_dragon.tooltip)
        self.assertIn("Green dragonhide x1", green_dragon.tooltip)

    def test_harpie_bug_swarm_row_exposes_the_continuous_lantern_gate(self):
        locked_rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "slayer_level": 33,
                "combat_lifepoints": 330,
                "constitution_level": 33,
                "inventory": {},
                "equipment": {"shield": "Unlit bug lantern"},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        locked = _row(locked_rows, "harpie_bug_swarm")
        self.assertFalse(locked.enabled)
        self.assertEqual(
            locked.locked_reasons,
            ("Equip a Lit bug lantern to damage Harpie bug swarms",),
        )

        ready_rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "slayer_level": 33,
                "combat_lifepoints": 330,
                "constitution_level": 33,
                "inventory": {},
                "equipment": {"shield": "Lit bug lantern"},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        ready = _row(ready_rows, "harpie_bug_swarm")
        self.assertTrue(ready.enabled)
        self.assertIn("Gold ore x1 (10514/100000)", ready.tooltip)
        self.assertIn("Green charm x1 (11/202)", ready.tooltip)

    def test_killerwatt_row_exposes_quest_boots_and_exact_drops(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "slayer_level": 37,
                "combat_lifepoints": 990,
                "constitution_level": 99,
                "quests": {"ernest_the_chicken": {"completed": True}},
                "inventory": {},
                "equipment": {},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        killerwatt = _row(rows, "killerwatt")

        self.assertTrue(killerwatt.enabled)
        self.assertIn("0–140 LP damage", killerwatt.tooltip)
        self.assertIn("Impious ashes x1", killerwatt.tooltip)
        self.assertIn("Grimy guam x1 (12016/100000)", killerwatt.tooltip)
        self.assertIn("Gold charm x1 (41/303)", killerwatt.tooltip)

    def test_sea_snake_rows_expose_quest_slayer_poison_and_drops(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "slayer_level": 40,
                "combat_lifepoints": 990,
                "constitution_level": 99,
                "quests": {"royal_trouble": {"completed": True}},
                "inventory": {},
                "equipment": {},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        hatchling = _row(rows, "sea_snake_hatchling")
        young = _row(rows, "sea_snake_young")

        self.assertTrue(hatchling.enabled)
        self.assertIn("Poison: 50 LP initial", hatchling.tooltip)
        self.assertIn("Casket x1 (11700/13000)", hatchling.tooltip)
        self.assertIn("Pearl bolt tips x3 (1/13000)", hatchling.tooltip)
        self.assertTrue(young.enabled)
        self.assertIn("Poison: 70 LP initial", young.tooltip)
        self.assertIn("Coins x44 (60/128)", young.tooltip)
        self.assertIn("Long bone x1 (250/100000)", young.tooltip)

    def test_brine_rat_row_exposes_access_and_exact_drop_selectors(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "slayer_level": 47,
                "combat_lifepoints": 990,
                "constitution_level": 99,
                "quests": {"olafs_quest": {"completed": True}},
                "inventory": {"Spade": 1},
                "equipment": {},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        brine_rat = _row(rows, "brine_rat")

        self.assertTrue(brine_rat.enabled)
        self.assertIn("Cavern access needs a real Spade", brine_rat.tooltip)
        self.assertIn("Coins x1 (84/512)", brine_rat.tooltip)
        self.assertIn("Brine sabre x1 (1/512)", brine_rat.tooltip)
        self.assertIn("Gold charm x1 (133/606)", brine_rat.tooltip)
        self.assertIn("Clue scroll (medium) x1 (1/128)", brine_rat.tooltip)

        missing_spade_rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "slayer_level": 47,
                "quests": {"olafs_quest": {"completed": True}},
                "inventory": {},
                "equipment": {},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        missing_spade = _row(missing_spade_rows, "brine_rat")
        self.assertFalse(missing_spade.enabled)
        self.assertIn("toolbelt does not count", missing_spade.tooltip)

    def test_molanisk_row_exposes_lure_light_and_exact_drop_selectors(self):
        rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "slayer_level": 39,
                "combat_lifepoints": 990,
                "constitution_level": 99,
                "quests": {"death_to_the_dorgeshuun": {"completed": True}},
                "inventory": {"Slayer bell": 1, "Lit torch": 1},
                "equipment": {},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )

        molanisk = _row(rows, "molanisk")

        self.assertTrue(molanisk.enabled)
        self.assertIn("ringing the non-consumed Slayer bell", molanisk.tooltip)
        self.assertIn("Grimy guam x1 (16791/100000)", molanisk.tooltip)
        self.assertIn("Mole claw x1 (207/100000)", molanisk.tooltip)
        self.assertIn("Death rune x50 (186/100000)", molanisk.tooltip)
        self.assertIn("Clue scroll (easy) x1 (1/128)", molanisk.tooltip)

        missing_light_rows = combat_target_rows(
            {
                "current_combat_target": "chicken",
                "slayer_level": 39,
                "quests": {"death_to_the_dorgeshuun": {"completed": True}},
                "inventory": {"Slayer bell": 1},
                "equipment": {},
                "combat_supply_loadout": {},
            },
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_ITEM_DATA,
            DEFAULT_COMBAT_TARGET,
        )
        missing_light = _row(missing_light_rows, "molanisk")
        self.assertFalse(missing_light.enabled)
        self.assertIn("One lit light source", missing_light.tooltip)

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
                "equipment": {"weapon": "Staff"},
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

    def test_combat_rows_ignore_magic_style_without_magic_equipment(self):
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

        self.assertTrue(chicken.enabled)
        self.assertEqual(chicken.locked_reasons, ())
        self.assertNotIn("Spell: Wind Strike", chicken.tooltip)

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

    def test_cooking_runtime_extra_rows_reuse_existing_icons(self):
        rows = cooking_target_rows(
            {"cooking_level": 0, "inventory": {}, "current_cooking": "gut_leaping_trout"},
            COOKING_DATA,
            COOKING_ITEM_IMAGES,
            DEFAULT_COOKING_TARGET,
            QUEST_UNLOCK_RULES,
        )

        for item_name in ("Leaping trout", "Leaping salmon", "Leaping sturgeon", "Roe", "Caviar", "Seaweed", "Soda ash"):
            self.assertIn(item_name, COOKING_ITEM_IMAGES)
            self.assertTrue(os.path.exists(COOKING_ITEM_IMAGES[item_name]))
        for target_id in ("gut_leaping_trout", "gut_leaping_salmon", "gut_leaping_sturgeon", "burn_seaweed"):
            row = _row(rows, target_id)
            self.assertIsNotNone(row.icon_path)
            self.assertTrue(os.path.exists(row.icon_path or ""))
            self.assertNotIn("(Lvl", row.label)

    def test_mining_rows_preserve_current_icon_and_include_concentrated_rocks(self):
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
        )

        coal = _row(rows, "coal")
        concentrated_coal = _row(rows, "concentrated_coal")
        runite = _row(rows, "runite")

        self.assertIsInstance(coal, TargetRowMetadata)
        self.assertEqual(coal.label, "Coal (Lvl 30)")
        self.assertTrue(coal.current)
        self.assertTrue(coal.enabled)
        self.assertEqual(coal.icon_path, ORE_IMAGES["Coal"])
        self.assertIn("Best usable pickaxe: Bronze pickaxe", coal.tooltip)
        self.assertEqual(concentrated_coal.label, "Concentrated coal (Lvl 77)")
        self.assertEqual(concentrated_coal.icon_path, ORE_IMAGES["Coal"])
        self.assertFalse(concentrated_coal.enabled)
        self.assertIn("level 77", concentrated_coal.tooltip)
        self.assertIn("Living Rock Caverns deposit", concentrated_coal.tooltip)
        self.assertIn("does not model rock depletion", concentrated_coal.tooltip)
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

    def test_fletching_rows_accept_coloured_feathers_as_materials(self):
        rows = fletching_target_rows(
            {
                "fletching_level": 1,
                "inventory": {"Arrow shafts": 15, "Orange feather": 15},
                "current_fletch": "headless_arrows",
            },
            FLETCHING_DATA,
            FLETCHED_ITEM_IMAGES,
            QUEST_UNLOCK_RULES,
        )

        headless_arrows = _row(rows, "headless_arrows")
        self.assertTrue(headless_arrows.enabled)
        self.assertIn("Orange feather x15 (you have 15)", headless_arrows.tooltip)

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
            {"inventory": {}, "current_utility": "gather_wool"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )

        wool = _row(rows, "gather_wool")
        nests = _row(rows, "open_bird_nest")

        self.assertTrue(wool.current)
        self.assertTrue(wool.enabled)
        self.assertEqual(os.path.basename(wool.icon_path or ""), "gather_wool.png")
        self.assertIn("No skill XP", wool.tooltip)
        self.assertIn("Output: Wool x1", wool.tooltip)
        self.assertIn("No materials required", wool.tooltip)
        self.assertFalse(nests.enabled)
        self.assertIn("No XP", nests.tooltip)
        self.assertIn("Locked: cut trees until a bird nest drops.", nests.tooltip)

        tanning = _row(rows, "tan_soft_leather")
        self.assertFalse(tanning.enabled)
        self.assertIn("Coins x1 (you have 0)", tanning.tooltip)

        funded_rows = utility_activity_rows(
            {"inventory": {"Coins": 1, "Cowhide": 1}, "current_utility": "tan_soft_leather"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )
        funded_tanning = _row(funded_rows, "tan_soft_leather")
        self.assertTrue(funded_tanning.current)
        self.assertTrue(funded_tanning.enabled)

        pestle_rows = utility_activity_rows(
            {"inventory": {"Anchovies": 1}, "current_utility": "grind_anchovies"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )
        anchovies = _row(pestle_rows, "grind_anchovies")
        self.assertTrue(anchovies.current)
        self.assertTrue(anchovies.enabled)
        self.assertIsNotNone(anchovies.icon_path)
        self.assertIn("Anchovy paste x1 per item", anchovies.tooltip)
        self.assertIn("No skill XP", anchovies.tooltip)

        lantern_rows = utility_activity_rows(
            {"inventory": {"Sapphire lantern (unlit)": 1}, "firemaking_level": 48},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )
        sapphire_lantern = _row(lantern_rows, "light_sapphire_lantern")
        self.assertFalse(sapphire_lantern.enabled)
        self.assertEqual(sapphire_lantern.locked_reasons, ("Firemaking 49",))
        self.assertIsNotNone(sapphire_lantern.icon_path)
        self.assertIn("Sapphire lantern (lit) x1 per item", sapphire_lantern.tooltip)

    def test_utility_rows_flag_one_shot_activities(self):
        # No live activity uses deactivate_after_run since buy_hunter_supplies
        # was retired, but the tooltip branch stays supported for future rows.
        activity_data = {
            "one_shot_bundle": {
                "display_name": "One-shot bundle",
                "requirements": {},
                "outputs": {"Bird snare": 1},
                "batch_size": 1,
                "deactivate_after_run": True,
                "group": "shopping",
                "source": "test fixture",
            },
        }
        rows = utility_activity_rows(
            {"inventory": {}, "current_utility": "one_shot_bundle"},
            activity_data,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
        )
        one_shot = _row(rows, "one_shot_bundle")
        self.assertIn("Runs once, then switches off", one_shot.tooltip)

    def test_utility_rows_apply_region_quest_unlock_rules(self):
        rows = utility_activity_rows(
            {"inventory": {}, "current_utility": "gather_lean_snails"},
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
            QUEST_UNLOCK_RULES,
        )

        # scavenge_raw_yak_meat retired 2026-07-07 (shop-covered); the
        # surviving Morytania snail bridges keep the region-lock coverage.
        snails = _row(rows, "gather_lean_snails")
        self.assertFalse(snails.enabled)
        self.assertIn("Priest in Peril", snails.tooltip)

        unlocked_rows = utility_activity_rows(
            {
                "inventory": {},
                "quests": {
                    "priest_in_peril": {"started": True, "progress": 6, "completed": True},
                },
            },
            UTILITY_ACTIVITY_DATA,
            UTILITY_ITEM_IMAGES,
            BIRD_NEST_OPEN_TABLES,
            DEFAULT_UTILITY_ACTIVITY,
            QUEST_UNLOCK_RULES,
        )
        self.assertTrue(_row(unlocked_rows, "gather_lean_snails").enabled)


if __name__ == "__main__":
    unittest.main()
