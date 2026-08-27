import copy
import unittest
from typing import Dict, FrozenSet, Tuple

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.quest_data import (
    KINGS_RANSOM_SCROLL_SOURCE,
    QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID,
    QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID,
    QUEST_UNLOCK_REPLACEMENTS_BY_ID,
    QuestCombatEncounter,
    _combat_encounter_dict,
    quest_reward_items_as_dict,
)
from ankiscape.logic_pure.logic_pure import (
    apply_consumable_pure,
    apply_combat_stat_delta_pure,
    apply_combat_stat_boost_to_pure,
    _potion_boost_amount,
    prayer_potion_restore_amount_pure,
    _combat_effective_skill_level,
    get_exp_to_next_level,
    calculate_new_level,
    get_newly_completed_achievements,
    calculate_probability_with_level,
    pick_gem,
    can_smelt_any_bar_pure,
    can_smith_any_pure,
    can_smith_item_pure,
    create_soft_clay_pure,
    has_crafting_materials_pure,
    apply_crafting_pure,
    apply_utility_activity_pure,
    apply_fletching_pure,
    fletching_material_requirements_pure,
    apply_herblore_action_pure,
    can_herblore_target_pure,
    has_herblore_materials_pure,
    herblore_target_locked_reasons_pure,
    apply_cooking_action_pure,
    apply_firemaking_action_pure,
    apply_fishing_action_pure,
    apply_claim_pure,
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    apply_runecrafting_action_pure,
    apply_smelt_pure,
    apply_smithing_action_pure,
    apply_smithing_pure,
    apply_woodcutting_pure,
    apply_woodcutting_action_pure,
    apply_mining_pure,
    apply_mining_action_pure,
    apply_open_bird_nests_pure,
    action_telemetry_key_pure,
    attach_tool_to_toolbelt_pure,
    best_woodcutting_axe_pure,
    best_mining_pickaxe_pure,
    bank_gear_rows_pure,
    equipment_bonus_state_pure,
    can_equip_item_pure,
    equip_item_pure,
    unequip_item_pure,
    equipment_stat_totals_pure,
    normalize_review_success_probability_pure,
    record_action_telemetry_pure,
    summarize_action_telemetry_pure,
    calculate_woodcutting_success_probability_pure,
    woodcutting_source_roll_chance_pure,
    calculate_mining_success_probability_pure,
    mining_source_roll_chance_pure,
    can_mine_ore_pure,
    can_cut_tree_pure,
    can_craft_item_pure,
    can_fletch_item_pure,
    can_burn_any_firemaking_target_pure,
    can_burn_firemaking_target_pure,
    calculate_firemaking_success_probability_pure,
    firemaking_target_locked_reasons_pure,
    firemaking_source_roll_chance_pure,
    fishing_source_roll_chance_pure,
    calculate_fishing_success_probability_pure,
    calculate_hunter_success_probability_pure,
    hunter_source_roll_chance_pure,
    cooking_source_roll_chance_pure,
    cheese_wheel_slice_probability_pure,
    cheese_wheel_slice_yield_pure,
    calculate_cooking_success_probability_pure,
    cooking_target_locked_reasons_pure,
    can_cook_target_pure,
    can_fish_method_pure,
    eligible_fishing_fish_pure,
    has_fishing_bait_pure,
    can_perform_utility_activity_pure,
    utility_activity_locked_reasons_pure,
    hunter_target_locked_reasons_pure,
    apply_hunter_action_pure,
    can_runecraft_target_pure,
    binding_necklace_charges_pure,
    runecrafting_altar_access_source_pure,
    calculate_iron_smelting_success_probability_pure,
    claim_rows_pure,
    consume_ring_of_forging_charge_pure,
    has_ring_of_forging_pure,
    sanitize_review_action_multiplier,
    smithing_success_probability_pure,
    can_start_quest_pure,
    can_attempt_quest_review_pure,
    can_progress_quest_pure,
    start_quest_pure,
    quest_current_stage_blockers_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_current_stage_choices_pure,
    apply_quest_route_choice_pure,
    quest_current_stage_resolvable_combat_blockers_pure,
    quest_combat_encounter_has_stats_pure,
    quest_locked_reasons_pure,
    quest_availability_state_pure,
    quest_unlock_locked_reasons_pure,
    fletching_target_locked_reasons_pure,
    player_combat_level_pure,
    normalize_xp_rewards_pure,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.core.constants import (
    CRAFTING_DATA,
    ACHIEVEMENTS,
    CLAIM_DATA,
    GLORY_GEM_DROP_CHANCE,
    INCIDENTAL_GEM_DROP_TABLE,
    ITEM_DEFINITIONS,
    MINING_BONUS_ITEM_DATA,
    MINING_PICKAXE_DATA,
    WOODCUTTING_AXE_DATA,
    ORE_DATA,
    TREE_DATA,
    EQUIPMENT_DATA,
    FIREMAKING_DATA,
    FISHING_DATA,
    FLETCHING_DATA,
    COOKING_DATA,
    QUEST_DATA,
    QUEST_UNLOCK_RULES,
    HUNTER_DATA,
    RUNECRAFTING_DATA,
    RUNECRAFTING_POUCH_DATA,
    UTILITY_ACTIVITY_DATA,
)

# Exact unlock sets only for quests with a QUEST_UNLOCK_REPLACEMENTS_BY_ID
# entry. Item-replacement quests outside this dictionary are intentionally not
# claimed as unlock coverage.
QUEST_UNLOCK_REPLACEMENT_GUARD: Dict[str, FrozenSet[str]] = {
    "a_fairy_tale_iii_battle_at_orks_rift": frozenset({
        "Ability to fetch teeth to get a Tooth creature by speaking to the Tooth Fairy after the quest.",
        "Ability to sell suqah tooth to the Tooth Fairy for 2,000 coins each. You can also sell to her old teeth, monkey dentures, and kebbit teeth, for amounts ranging from 1 to 200 coins.",
        "Ability to use the Fairy Rings and get into Zanaris without a Lunar or Dramen staff.",
        "Access to Mos Le Harmless through K'Chunk's island; code D-I-P.",
        "Access to a new battle area in the Ork's Rift, which contains Ivory Bre'egth (cursed), Ivory Gromblod (cursed) and Ivory Shredflesh (cursed). They all have a combat level of 108 and have high gem and blue charm drop rates.",
        "Free access to the Zanaris Market",
        "To have your patches automatically weeded, talk to Martin the Master Gardener after the quest to unlock the ability to have gardeners keep your farming patches weed free.",
    }),
    "a_tail_of_two_cats": frozenset({"Talk to Historian Minas in the Varrock Museum to receive 5 Kudos."}),
    "another_slice_of_h_a_m": frozenset({
        "Ability to buy Goblin Village teleport orbs",
        "Free access to the Dorgesh-Kaan - Keldagrim Train System",
    }),
    "back_to_my_roots": frozenset({
        "A new maze Jade vine maze, slightly larger than Draynor Manor, containing 8 new creatures: Giant ant soldier level 58, Giant ant worker level 40, Tenacious toucan level 70, Giant Wasp level 66, Frog level 66, Pernicious parrot level 66, Wild jade vine level 167, Karamjan Jungle eagle.",
        "Ability to slay the Jade Vine for extra Slayer and Farming experience once every 15 hours.",
        "Transportation between Eagles' Peak and Karamja using the Karamjan Jungle eagle.",
        "Vine Farming Patch in East Ardougne",
    }),
    "biohazard": frozenset({
        "Ability to travel freely through the West Ardougne Gate",
        "Use of the Combat Training Camp north of Ardougne",
    }),
    "cabin_fever": frozenset({
        "Access to Mos Le'Harmless",
        "Access to kill Cave horrors.",
        "Charter Ship prices are halved.",
    }),
    "catapult_construction": frozenset({"Increased damage when using the Castle Wars catapults"}),
    "deadliest_catch": frozenset({
        "Bank deposit box north-east of Pollnivneach",
        "Bank deposit box north-west of Bedabin Camp",
        "Bank deposit box on the south coast of Ape Atoll",
        "Bank deposit box south of Brimhaven",
        "Bank deposit box south of Elf Camp",
        "Bank deposit box west of Harmony Island",
        "Bank deposit box west of Mort Myre Swamp",
        "Piscatoris - South of Falconry",
    }),
    "dealing_with_scabaras": frozenset({
        "Simon Templeton accepts noted Pyramid Plunder treasures after his post-quest errand, but noted gold artefacts still cannot be exchanged.",
        "The ability to craft an Enchanted water tiara - protects you from the Desert heat effect",
    }),
    "do_no_evil": frozenset({
        "Ability to pickpocket monkey knife fighters.",
        "Ability to run chimp ice for further rewards.",
        "Access to a passageway from the desert (rockslide south of the Kalphite Hive entrance) to a new area with Kalphites. This is unlocked if you left the room from the hole while you were in it.",
        "Access to the Monkey colony.",
        "New magic carpet destinations, connecting the Monkey colony with Shantay Pass and southern Pollnivneach.",
        "Players with level 80 Agility (boosts may be used) can enter the cavern in the south wall of the Monkey colony.",
        "The ability to add the camulet and catspeak amulet to the Cramulet.",
        "The ability to upgrade Ava's accumulator to Ava's alerter.",
    }),
    "dream_mentor": frozenset({
        "Access to the 'Random' option on NPC Contact",
        "Seven new spells added to the Lunar Spellbook",
    }),
    "eagles_peak": frozenset({
        "Ability to capture ferrets using box traps.",
        "Access to the Eagle transport system",
        "Use captured ferrets to flush rabbits from rabbit holes, trap them with a rabbit trap, and string a dropped rabbit's foot with a ball of wool to wear as a necklace when cutting trees to increase bird-nest chances.",
    }),
    "in_aid_of_the_myreque": frozenset({
        "Ability to make and use Rod of Ivandis and Guthix balance potion to fight and defeat Vampyre Juveniles and Juvinates.",
        "Ability to use a Gadderhammer, which is strong against shades.",
        "Access to Burgh de Rott",
        "Talk to Historian Minas to receive 5 Kudos in the Varrock Museum.",
        "You can now play Temple Trekking activity.",
    }),
    "meeting_history": frozenset({"Speak to Historian Minas at the Varrock Museum to earn 5 Kudos."}),
    "nomads_requiem": frozenset({
        "Access to a Bloodwood tree in the Soul Wars waiting area.",
        "Decaying Avatar and Nomad become available as bosses in the Dominion Tower.",
        "Soul Wars is added to the available respawn points.",
    }),
    "observatory_quest": frozenset({"Talk to Historian Minas at the Varrock Museum to receive 5 Kudos."}),
    "rocking_out": frozenset({
        "Ability to buy Braindeath 'rum' from The Rusty Anchor Inn",
        "Ability to catch Pirate implings with 76 Hunter",
        "Ability to raise Ex-ex-parrot by speaking to Bill Teach and 50 Ships Mufassah (requires 71 Summoning)",
        "Ability to steal from customs lockers",
        "Access to a Bank deposit box in Rimmington",
        "Access to the Rock Island Prison.",
        "Free access to the Brimhaven Agility Arena",
        "Removes need for the Book o' piracy when speaking to pirates on Mos Le'Harmless",
    }),
    "spirit_of_summer": frozenset({
        "Access to a Goth leprechaun in level 26 wilderness, as well as the flower patch he guards.",
        "Access to a new Spirit Realm",
        "Access to the Cursed Magic Tree",
        "Access to the alternative Axe Hut, in which axeless level 42 Ghostly warriors can be fought without the need of a lockpick.",
    }),
    "the_dig_site": frozenset({
        "Ability to do Varrock Museum Specimen Cleaning to obtain Kudos and a Digsite pendant.",
        "Access through the Varrock Museum back door and gate.",
    }),
    "the_golem": frozenset({
        "Ability to collect multiple Phoenix feathers",
        "Magic carpet route opened to the ruins of Uzer.",
    }),
    "the_grand_tree": frozenset({
        "Ability to use the Agility Shortcut from the Grand Tree to the Barbarian Outpost (with 37 Agility)",
        "Ability to use the Gnome glider transportation system",
        "Ability to use the Grand Tree mine under The Grand Tree",
        "Ability to use the Spirit Tree in the stronghold outside the Grand Tree (the Tree Gnome Village quest doesn't allow access to this tree)",
        "Talk to Historian Minas in the Varrock Museum to receive 5 Kudos.",
    }),
}


# Exact flat completion grants for every quest with a
# QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID entry.
QUEST_ITEM_REWARD_REPLACEMENT_GUARD: Dict[str, FrozenSet[Tuple[str, int]]] = {
    "a_fairy_tale_i_growing_pains": frozenset({}),
    "a_fairy_tale_iii_battle_at_orks_rift": frozenset({("Magic watering can", 1)}),
    "a_tail_of_two_cats": frozenset({("Catspeak amulet (e)", 1), ("Doctors hat", 1)}),
    "another_slice_of_h_a_m": frozenset({("Ancient mace", 1), ("Dorgesh-kaan sphere", 1)}),
    "back_to_my_roots": frozenset({("Jade vine seed", 1)}),
    "biohazard": frozenset({}),
    "cabin_fever": frozenset({("Book o' piracy", 1)}),
    "carnillean_rising": frozenset({("Coins", 5000), ("Mahogany plank", 10), ("Oak plank", 100), ("Philipe's sweets", 1), ("Teak plank", 30), ("Treasure chest (Carnillean Rising)", 1)}),
    "catapult_construction": frozenset({("Adamant halberd", 1), ("Coins", 2000), ("Sailor's hat", 1), ("Teak plank", 30)}),
    "clock_tower": frozenset({("Coins", 500)}),
    "cold_war": frozenset({}),
    "deadliest_catch": frozenset({("Small cast net", 1)}),
    "dealing_with_scabaras": frozenset({}),
    "diamond_in_the_rough": frozenset({}),
    "do_no_evil": frozenset({("Clue scroll (elite)", 1), ("Cramulet", 1)}),
    "dream_mentor": frozenset({}),
    "dwarf_cannon": frozenset({("Ammo mould", 1)}),
    "eagles_peak": frozenset({("Box trap", 1), ("Eagle costume", 1)}),
    "hazeel_cult": frozenset({("Coins", 2005)}),
    "hunt_for_red_raktuber": frozenset({}),
    "icthlarins_little_helper": frozenset({("Catspeak amulet", 1)}),
    "in_aid_of_the_myreque": frozenset({}),
    "let_them_eat_pie": frozenset({("Expensive spices", 1), ("Meat pie", 5)}),
    "meeting_history": frozenset({("Enchanted key", 1)}),
    "missing_my_mummy": frozenset({("Coins", 5000)}),
    "monks_friend": frozenset({("Law rune", 8)}),
    "nomads_requiem": frozenset({("Soul Wars cape", 1)}),
    "observatory_quest": frozenset({("Maple longbow", 1), ("Uncut sapphire", 1)}),
    "plague_city": frozenset({("A magic scroll", 1)}),
    "rocking_out": frozenset({}),
    "sheep_herder": frozenset({("Coins", 3100)}),
    "smoking_kills": frozenset({}),
    "some_like_it_cold": frozenset({("Pop costume", 1), ("Rock costume", 1)}),
    "song_from_the_depths": frozenset({("Coral bolts", 50), ("Coral crossbow", 1), ("Remora's necklace", 1)}),
    "spirit_of_summer": frozenset({("Jennica's ring", 1)}),
    "stolen_hearts": frozenset({("Coins", 2500)}),
    "the_dig_site": frozenset({("Fruit blast", 1), ("Gold bar", 2)}),
    "the_golem": frozenset({}),
    "the_grand_tree": frozenset({}),
    "tree_gnome_village": frozenset({("Gnome amulet", 1)}),
}


# Exact lamp definitions for every quest with a
# QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID entry.
QUEST_LAMP_REWARD_REPLACEMENT_GUARD: Dict[str, Tuple[Tuple[object, ...], ...]] = {
    "carnillean_rising": (
        (
            "Carnillean lamp",
            1500,
            (
                "agility",
                "attack",
                "constitution",
                "construction",
                "cooking",
                "crafting",
                "defense",
                "dungeoneering",
                "farming",
                "firemaking",
                "fishing",
                "fletching",
                "herblore",
                "hunter",
                "magic",
                "mining",
                "prayer",
                "ranged",
                "runecrafting",
                "slayer",
                "smithing",
                "strength",
                "summoning",
                "thieving",
                "woodcutting",
            ),
            31,
            "https://runescape.wiki/w/Carnillean_lamp?oldid=6153995",
            (
                "Two Carnillean lamps are awarded for completing the Carnillean Rising quest. "
                "They may be claimed from the chest by Ceril inside the Carnillean mansion. "
                "Each lamp gives 1,500 experience in a skill (above level 30) of your choice."
            ),
            2,
        ),
    ),
    "myths_of_the_white_lands": (
        (
            "Post-quest ice-cave Agility reward",
            10000,
            ("agility",),
            1,
            "https://runescape.wiki/w/Myths_of_the_White_Lands?oldid=6555850",
            "Optional reward for completing the additional ice-cave route.",
            1,
        ),
    ),
}


class TestLogic(unittest.TestCase):
    def test_exp_to_next_level_handles_progress_and_cap(self):
        cases = (
            ("progress", {"mining_level": 10, "total_exp": 1000}, {10: 1500}, 500),
            ("level cap", {"mining_level": 99, "total_exp": 200000}, {99: 200000}, 0),
        )
        for name, player_data, exp_table, expected in cases:
            with self.subTest(name):
                self.assertEqual(get_exp_to_next_level(player_data, exp_table), expected)

    def test_get_newly_completed_achievements_basic(self):
        # Mock achievements and player data
        achievements = {
            "A": {"condition": lambda p: p["score"] >= 10},
            "B": {"condition": lambda p: p["score"] >= 20},
            "C": {"condition": lambda p: p["score"] >= 30},
        }
        player_data = {"score": 25, "completed_achievements": ["A"]}
        result = get_newly_completed_achievements(player_data, achievements)
        self.assertIn("B", result)
        self.assertNotIn("A", result)
        self.assertNotIn("C", result)

    def test_get_newly_completed_achievements_none(self):
        achievements = {
            "A": {"condition": lambda p: p["score"] >= 10},
            "B": {"condition": lambda p: p["score"] >= 20},
        }
        player_data = {"score": 5, "completed_achievements": []}
        result = get_newly_completed_achievements(player_data, achievements)
        self.assertEqual(result, [])

    def test_get_newly_completed_achievements_all(self):
        achievements = {
            "A": {"condition": lambda p: True},
            "B": {"condition": lambda p: True},
        }
        player_data = {"score": 100, "completed_achievements": []}
        result = get_newly_completed_achievements(player_data, achievements)
        self.assertCountEqual(result, ["A", "B"])

    def test_calculate_new_level_basic(self):
        EXP_TABLE = {1: 0, 2: 100, 3: 300, 4: 600, 5: 1000}
        self.assertEqual(calculate_new_level(50, 1, EXP_TABLE), 1)
        self.assertEqual(calculate_new_level(150, 1, EXP_TABLE), 2)
        self.assertEqual(calculate_new_level(350, 2, EXP_TABLE), 3)

    def test_calculate_new_level_multiple_level_up(self):
        EXP_TABLE = {1: 0, 2: 100, 3: 300, 4: 600, 5: 1000}
        self.assertEqual(calculate_new_level(1200, 1, EXP_TABLE), 5)

    def test_calculate_new_level_max_level(self):
        EXP_TABLE = {98: 10000, 99: 20000}
        self.assertEqual(calculate_new_level(25000, 98, EXP_TABLE), 99)
        self.assertEqual(calculate_new_level(25000, 99, EXP_TABLE), 99)

    def test_calculate_probability_with_level(self):
        # Low level, no cap hit
        prob = calculate_probability_with_level(
            player_level=0,
            base_probability=0.8,
            level_bonus_factor=0.02,
            source_probability=0.5,
            cap=0.95,
        )
        self.assertAlmostEqual(prob, 0.4)

        # Higher level, cap applies: (0.8 + 10*0.02)=1.0 -> capped to 0.95; 0.95*0.5=0.475
        prob = calculate_probability_with_level(
            player_level=10,
            base_probability=0.8,
            level_bonus_factor=0.02,
            source_probability=0.5,
            cap=0.95,
        )
        self.assertAlmostEqual(prob, 0.475)

    def test_pick_gem(self):
        gem_data = {
            "Sapphire": {"probability": 0.5},
            "Emerald": {"probability": 0.3},
            "Ruby": {"probability": 0.2},
        }
        self.assertEqual(pick_gem(gem_data, 0.2), "Sapphire")
        self.assertEqual(pick_gem(gem_data, 0.6), "Emerald")
        self.assertEqual(pick_gem(gem_data, 0.85), "Ruby")
        # When r exceeds total probability mass (1.0 exactly picks last), use 0.99 -> Ruby, 1.1 -> None
        self.assertEqual(pick_gem(gem_data, 0.99), "Ruby")
        partial = {
            "Sapphire": {"probability": 0.4},
            "Emerald": {"probability": 0.4},
        }
        self.assertIsNone(pick_gem(partial, 0.9))

    def test_can_smelt_any_bar_pure(self):
        bar_data = {
            "Bronze bar": {"level": 1, "ore_required": {"Copper ore": 1, "Tin ore": 1}},
            "Iron bar": {"level": 15, "ore_required": {"Iron ore": 1}},
        }
        inv = {"Copper ore": 1, "Tin ore": 1}
        self.assertTrue(can_smelt_any_bar_pure(inv, 1, bar_data))
        self.assertFalse(can_smelt_any_bar_pure({}, 99, bar_data))
        self.assertFalse(can_smelt_any_bar_pure({"Copper ore": 1}, 99, bar_data))

    def test_apply_smithing_pure_smelt_and_forge(self):
        smithing_data = {
            "smelt_bronze_bar": {
                "level": 1,
                "exp": 6.2,
                "requirements": {"Tin ore": 1, "Copper ore": 1},
                "output_item": "Bronze bar",
                "output_qty": 1,
                "station": "furnace",
            },
            "forge_iron_pickaxe": {
                "level": 20,
                "exp": 50.0,
                "requirements": {"Iron bar": 2},
                "output_item": "Iron pickaxe",
                "output_qty": 1,
                "station": "anvil",
            },
        }
        inv = {"Tin ore": 1, "Copper ore": 1, "Iron bar": 2}

        self.assertTrue(can_smith_any_pure(inv, 1, smithing_data))
        self.assertFalse(can_smith_item_pure(19, inv, "forge_iron_pickaxe", smithing_data))
        self.assertTrue(can_smith_item_pure(20, inv, "forge_iron_pickaxe", smithing_data))

        after_smelt, smelt_exp, smelt_ok = apply_smithing_pure("smelt_bronze_bar", inv, smithing_data)
        self.assertTrue(smelt_ok)
        self.assertAlmostEqual(smelt_exp, 6.2)
        self.assertEqual(after_smelt["Tin ore"], 0)
        self.assertEqual(after_smelt["Copper ore"], 0)
        self.assertEqual(after_smelt["Bronze bar"], 1)

        after_forge, forge_exp, forge_ok = apply_smithing_pure("forge_iron_pickaxe", inv, smithing_data)
        self.assertTrue(forge_ok)
        self.assertAlmostEqual(forge_exp, 50.0)
        self.assertEqual(after_forge["Iron bar"], 0)
        self.assertEqual(after_forge["Iron pickaxe"], 1)
        self.assertEqual(inv["Iron bar"], 2)

    def test_iron_smelting_success_probability_matches_source_curve(self):
        # SmeltingAction success is nextInt(100) <= interp -> (interp+1)/100:
        # the exact source curve is 51%..81%, not the nominal 50..80 labels.
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(15), 0.51)
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(30), 0.66)
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(45), 0.81)
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(99), 0.81)
        self.assertAlmostEqual(calculate_iron_smelting_success_probability_pure(15, has_ring_of_forging=True), 1.0)

    def test_apply_smithing_action_pure_models_iron_failure_only(self):
        smithing_data = {
            "smelt_iron_bar": {
                "level": 15,
                "exp": 12.5,
                "requirements": {"Iron ore": 1},
                "output_item": "Iron bar",
                "output_qty": 1,
                "station": "furnace",
            },
            "smelt_bronze_bar": {
                "level": 1,
                "exp": 6.2,
                "requirements": {"Tin ore": 1, "Copper ore": 1},
                "output_item": "Bronze bar",
                "output_qty": 1,
                "station": "furnace",
            },
        }

        failed_inv, failed_exp, processed, output_item, failed = apply_smithing_action_pure(
            "smelt_iron_bar",
            {"Iron ore": 1},
            smithing_data,
            15,
            r_action=0.99,
        )
        self.assertTrue(processed)
        self.assertTrue(failed)
        self.assertEqual(failed_exp, 0)
        self.assertIsNone(output_item)
        self.assertEqual(failed_inv["Iron ore"], 0)
        self.assertNotIn("Iron bar", failed_inv)

        success_inv, success_exp, processed, output_item, failed = apply_smithing_action_pure(
            "smelt_iron_bar",
            {"Iron ore": 1},
            smithing_data,
            15,
            r_action=0.0,
        )
        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output_item, "Iron bar")
        self.assertAlmostEqual(success_exp, 12.5)
        self.assertEqual(success_inv["Iron ore"], 0)
        self.assertEqual(success_inv["Iron bar"], 1)

        bronze_inv, bronze_exp, processed, output_item, failed = apply_smithing_action_pure(
            "smelt_bronze_bar",
            {"Tin ore": 1, "Copper ore": 1},
            smithing_data,
            1,
            r_action=1.0,
        )
        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output_item, "Bronze bar")
        self.assertAlmostEqual(bronze_exp, 6.2)
        self.assertEqual(bronze_inv["Bronze bar"], 1)

    def test_apply_smithing_action_pure_assembles_dragon_sq_shield(self):
        smithing_data = {
            "repair_dragon_sq_shield": {
                "level": 60,
                "exp": 70.0,
                "requirements": {"Shield left half": 1, "Shield right half": 1},
                "output_item": "Dragon sq shield",
                "output_qty": 1,
                "station": "anvil",
            },
        }

        self.assertFalse(can_smith_item_pure(59, {"Shield left half": 1, "Shield right half": 1}, "repair_dragon_sq_shield", smithing_data))
        self.assertTrue(can_smith_item_pure(60, {"Shield left half": 1, "Shield right half": 1}, "repair_dragon_sq_shield", smithing_data))
        inventory, exp, processed, output_item, failed = apply_smithing_action_pure(
            "repair_dragon_sq_shield",
            {"Shield left half": 1, "Shield right half": 1},
            smithing_data,
            60,
        )

        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertAlmostEqual(exp, 70.0)
        self.assertEqual(output_item, "Dragon sq shield")
        self.assertEqual(inventory, {"Shield left half": 0, "Shield right half": 0, "Dragon sq shield": 1})

    def test_apply_smithing_action_pure_casts_four_cannonballs_and_keeps_mould(self):
        from ankiscape.core.constants import SMITHING_DATA

        self.assertFalse(can_smith_item_pure(35, {"Steel bar": 1}, "forge_cannonballs", SMITHING_DATA))
        inputs = {"Steel bar": 1, "Ammo mould": 1}
        self.assertTrue(can_smith_item_pure(35, inputs, "forge_cannonballs", SMITHING_DATA))
        inventory, exp, processed, output_item, failed = apply_smithing_action_pure(
            "forge_cannonballs", inputs, SMITHING_DATA, 35
        )

        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(exp, 25.6)
        self.assertEqual(output_item, "Cannonball")
        self.assertEqual(inventory, {"Steel bar": 0, "Ammo mould": 1, "Cannonball": 4})

    def test_ring_of_forging_guarantees_iron_and_consumes_charges(self):
        smithing_data = {
            "smelt_iron_bar": {
                "level": 15,
                "exp": 12.5,
                "requirements": {"Iron ore": 1},
                "output_item": "Iron bar",
                "output_qty": 1,
                "station": "furnace",
            },
        }
        player_data = {"equipment": {"ring": "Ring of forging"}, "item_charges": {"Ring of forging": 2}}
        self.assertTrue(has_ring_of_forging_pure(player_data))
        self.assertEqual(smithing_success_probability_pure("smelt_iron_bar", smithing_data["smelt_iron_bar"], 15, True), 1.0)

        inv, exp, processed, output_item, failed = apply_smithing_action_pure(
            "smelt_iron_bar",
            {"Iron ore": 1},
            smithing_data,
            15,
            r_action=0.99,
            has_ring_of_forging=True,
        )
        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output_item, "Iron bar")
        self.assertAlmostEqual(exp, 12.5)
        self.assertEqual(inv["Iron bar"], 1)

        one_charge = consume_ring_of_forging_charge_pure(player_data)
        self.assertEqual(one_charge["item_charges"]["Ring of forging"], 1)
        crumbled = consume_ring_of_forging_charge_pure(one_charge)
        self.assertNotIn("ring", crumbled["equipment"])
        self.assertNotIn("Ring of forging", crumbled["item_charges"])

    def test_create_soft_clay_pure(self):
        inv = {"Clay": 2}
        new_inv, ok = create_soft_clay_pure(inv)
        self.assertTrue(ok)
        self.assertEqual(new_inv["Clay"], 1)
        self.assertEqual(new_inv.get("Soft clay"), 1)
        # Original inventory not mutated
        self.assertEqual(inv["Clay"], 2)
        # Failure path
        new_inv2, ok2 = create_soft_clay_pure({})
        self.assertFalse(ok2)
        self.assertEqual(new_inv2, {})

    def test_apply_utility_activity_batches_without_xp(self):
        utility_data = {
            "make_soft_clay": {
                "requirements": {"Clay": 1},
                "output_item": "Soft clay",
                "output_qty": 1,
                "batch_size": 28,
            }
        }
        inv = {"Clay": 3}
        self.assertTrue(can_perform_utility_activity_pure(inv, "make_soft_clay", utility_data))

        new_inv, exp, ok, processed = apply_utility_activity_pure("make_soft_clay", inv, utility_data)

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 3)
        self.assertEqual(new_inv["Clay"], 0)
        self.assertEqual(new_inv["Soft clay"], 3)
        self.assertEqual(inv["Clay"], 3)

    def test_apply_utility_activity_caps_at_batch_size(self):
        utility_data = {
            "make_soft_clay": {
                "requirements": {"Clay": 1},
                "output_item": "Soft clay",
                "output_qty": 1,
                "batch_size": 28,
            }
        }
        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "make_soft_clay",
            {"Clay": 40},
            utility_data,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 28)
        self.assertEqual(new_inv["Clay"], 12)
        self.assertEqual(new_inv["Soft clay"], 28)

    def test_grinding_activities_batch_without_xp(self):
        cases = (
            ("anchovies", "grind_anchovies", {"Anchovies": 30}, "Anchovies", 2, "Anchovy paste", 28, 28),
            (
                "empty bird nests",
                "grind_birds_nest",
                {"Bird's nest (empty)": 3},
                "Bird's nest (empty)",
                0,
                "Crushed nest",
                3,
                3,
            ),
        )
        for name, action_id, inventory, input_item, remainder, output_item, output, processed in cases:
            with self.subTest(name):
                new_inv, exp, ok, actual_processed = apply_utility_activity_pure(
                    action_id, inventory, UTILITY_ACTIVITY_DATA
                )
                self.assertTrue(ok)
                self.assertEqual(exp, 0)
                self.assertEqual(actual_processed, processed)
                self.assertEqual(new_inv[input_item], remainder)
                self.assertEqual(new_inv[output_item], output)

    def test_light_source_actions_are_single_zero_xp_item_swaps_with_level_locks(self):
        prepared, exp, ok, processed = apply_utility_activity_pure(
            "insert_white_candle",
            {"Candle lantern (empty)": 1, "Candle": 1},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(
            prepared,
            {"Candle lantern (empty)": 0, "Candle": 0, "Candle lantern (unlit, 4529)": 1},
        )

        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "light_candle_lantern_4527",
            prepared,
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 1)
        self.assertEqual(new_inv["Candle lantern (unlit, 4529)"], 0)
        self.assertEqual(new_inv["Candle lantern (lit, 4531)"], 1)

        extinguished, exp, ok, processed = apply_utility_activity_pure(
            "extinguish_candle_lantern_4527",
            new_inv,
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 1)
        self.assertEqual(extinguished["Candle lantern (unlit, 4529)"], 1)
        self.assertEqual(extinguished["Candle lantern (lit, 4531)"], 0)
        self.assertEqual(
            utility_activity_locked_reasons_pure(
                {"inventory": {"Candle lantern (unlit, 4529)": 1}, "firemaking_level": 3},
                "light_candle_lantern_4527",
                UTILITY_ACTIVITY_DATA,
            ),
            ("Firemaking 4",),
        )
        self.assertEqual(
            utility_activity_locked_reasons_pure(
                {"inventory": {"Candle lantern (lit, 4531)": 1}, "firemaking_level": 1},
                "extinguish_candle_lantern_4527",
                UTILITY_ACTIVITY_DATA,
            ),
            (),
        )

    def test_bug_lantern_lights_at_33_and_extinguishes_without_a_level_gate(self):
        locked = utility_activity_locked_reasons_pure(
            {"inventory": {"Unlit bug lantern": 1}, "firemaking_level": 32},
            "light_bug_lantern",
            UTILITY_ACTIVITY_DATA,
        )
        self.assertEqual(locked, ("Firemaking 33",))

        lit, exp, ok, processed = apply_utility_activity_pure(
            "light_bug_lantern",
            {"Unlit bug lantern": 1},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(lit["Unlit bug lantern"], 0)
        self.assertEqual(lit["Lit bug lantern"], 1)

        extinguished, exp, ok, processed = apply_utility_activity_pure(
            "extinguish_bug_lantern",
            lit,
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(extinguished["Unlit bug lantern"], 1)
        self.assertEqual(extinguished["Lit bug lantern"], 0)

    def test_lamp_oil_chain_preserves_empty_unlit_and_lit_states(self):
        filled, exp, ok, processed = apply_utility_activity_pure(
            "fill_bullseye_lantern",
            {"Bullseye lantern (empty)": 1, "Swamp tar": 1},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(filled["Bullseye lantern (unlit)"], 1)
        lit, exp, ok, processed = apply_utility_activity_pure(
            "light_bullseye_lantern", filled, UTILITY_ACTIVITY_DATA
        )
        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(lit["Bullseye lantern (unlit)"], 0)
        self.assertEqual(lit["Bullseye lantern (lit)"], 1)

    def test_source_gathering_actions_generate_full_inventory_batches_without_xp(self):
        for action_id, output_item in (
            ("gather_wool", "Wool"),
            ("gather_swamp_toads", "Swamp toad"),
        ):
            with self.subTest(action_id=action_id):
                new_inv, exp, ok, processed = apply_utility_activity_pure(
                    action_id,
                    {},
                    UTILITY_ACTIVITY_DATA,
                )

                self.assertTrue(ok)
                self.assertEqual(exp, 0)
                self.assertEqual(processed, 28)
                self.assertEqual(new_inv, {output_item: 28})

    def test_blue_dragon_scale_trip_gathers_the_seven_ordinary_spawns(self):
        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "gather_blue_dragon_scales",
            {},
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 7))
        self.assertEqual(new_inv, {"Blue dragon scale": 7})

    def test_potato_cactus_trip_gathers_only_the_three_first_level_spawns(self):
        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "gather_potato_cacti",
            {},
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 3))
        self.assertEqual(new_inv, {"Potato cactus": 3})

    def test_black_mushroom_pickup_gathers_one_ground_spawn_without_xp(self):
        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "gather_black_mushrooms",
            {},
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(new_inv, {"Black mushroom": 1})

    def test_black_mushroom_ink_requires_and_consumes_an_empty_vial(self):
        locked_inv, exp, ok, processed = apply_utility_activity_pure(
            "grind_black_mushroom",
            {"Black mushroom": 1},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertFalse(ok)
        self.assertEqual((exp, processed), (0, 0))
        self.assertEqual(locked_inv, {"Black mushroom": 1})

        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "grind_black_mushroom",
            {"Black mushroom": 2, "Vial": 1},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(
            new_inv,
            {"Black mushroom": 1, "Vial": 0, "Black mushroom ink": 1},
        )

    def test_bankstanding_is_a_true_no_op_utility_action(self):
        inventory = {"Coins": 1_000, "Logs": 4}

        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "bankstanding",
            inventory,
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual((exp, processed), (0, 1))
        self.assertEqual(new_inv, inventory)
        self.assertIsNot(new_inv, inventory)
        self.assertNotIn("bankstanding", new_inv)

    def test_retired_shop_bridge_activities_stay_gone(self):
        # These temporary bridges were retired on 2026-07-06 once their outputs
        # became live NPC shop stock; a reappearance means a data regression.
        retired_ids = (
            "scavenge_chicken_feathers", "gather_fishing_bait", "buy_hunter_supplies",
            # Cooking pass 2026-07-07: outputs are live shop stock.
            "buy_bucket", "gather_potatoes", "gather_onions", "gather_eggs",
            "gather_redberries", "gather_cooking_apples", "gather_tomatoes",
            "gather_cheese", "gather_cabbage", "gather_sweetcorn", "gather_spice",
            "scavenge_raw_chicken", "scavenge_raw_beef", "scavenge_raw_bear_meat",
            "scavenge_raw_rat_meat", "scavenge_raw_rabbit", "scavenge_raw_yak_meat",
            "gather_thin_snails",
        )
        for retired in retired_ids:
            self.assertNotIn(retired, UTILITY_ACTIVITY_DATA)

    def test_combat_landed_hit_damage_matches_darkan_random_semantics(self):
        # CombatFormula.kt rolls Utils.random(1, maxHit) on landed hits, and
        # Utils.random(min, max) = min + nextInt(|max-min|): uniform
        # 1..maxHit-1 lifepoints, never 0 and never the displayed max.
        from ankiscape.logic_pure.logic_pure import _combat_roll_damage_lifepoints

        # max hit 5.0 old-HP = 50 lifepoints: rolls span 1..49.
        self.assertEqual(_combat_roll_damage_lifepoints(5.0, lambda: 0.0), 1)
        self.assertEqual(_combat_roll_damage_lifepoints(5.0, lambda: 0.999999999), 49)
        # A 1-lifepoint max hit always deals exactly 1 on a landed hit.
        self.assertEqual(_combat_roll_damage_lifepoints(0.1, lambda: 0.0), 1)
        self.assertEqual(_combat_roll_damage_lifepoints(0.1, lambda: 0.99), 1)
        # No max hit means no damage (accuracy-roll misses are handled upstream).
        self.assertEqual(_combat_roll_damage_lifepoints(0.0, lambda: 0.5), 0)

    def test_dragon_pickaxe_source_bonus_applies_by_item_id(self):
        # Mining.kt gives PickaxeType.DRAGON extra rolls at 1.12x base;
        # AnkiScape folds that source constant into every roll, keyed on the
        # cache item id (15261), never a display-name string. This pins the
        # bonus so a spec-shape change can't silently disable it again.
        from ankiscape.core.constants import MINING_PICKAXE_DATA, ORE_DATA
        from ankiscape.logic_pure.logic_pure import mining_source_roll_chance_pure

        dragon = MINING_PICKAXE_DATA["dragon_pickaxe"]
        self.assertEqual(dragon["item_id"], 15261)
        target = min(ORE_DATA.values(), key=lambda t: float(t.get("low_chance", 99)))
        same_ratio_non_dragon = dict(dragon, item_id=0)
        boosted = mining_source_roll_chance_pure(1, target, dragon)
        base = mining_source_roll_chance_pure(1, target, same_ratio_non_dragon)
        self.assertAlmostEqual(boosted / base, 1.12, places=6)

    def test_stat_delta_substrate_boosts_and_drains_toward_base(self):
        # Reusable current-level helper (shared with future potions): boosts
        # raise current above base, drains lower it, and landing back on base
        # drops the entry.
        data = {"attack_level": 60, "combat_current_levels": {}}
        apply_combat_stat_delta_pure(data, "attack", 5)
        self.assertEqual(data["combat_current_levels"], {"attack": 65})
        self.assertEqual(_combat_effective_skill_level(data, "attack", 1), 65)
        apply_combat_stat_delta_pure(data, "attack", -5)
        self.assertEqual(data["combat_current_levels"], {})
        apply_combat_stat_delta_pure(data, "attack", -70)
        self.assertEqual(_combat_effective_skill_level(data, "attack", 1), 1)  # clamps at 1

    def test_potion_boost_formulas_match_source(self):
        # PotionType.kt: regular = floor(base/10)+3, super = floor(15*base/100)+5.
        self.assertEqual(_potion_boost_amount(40, "r"), 7)
        self.assertEqual(_potion_boost_amount(99, "r"), 12)
        self.assertEqual(_potion_boost_amount(99, "s"), 19)
        self.assertEqual(_potion_boost_amount(1, "s"), 5)

    def test_manual_prayer_potions_restore_points_with_exact_formulas_and_cap(self):
        self.assertEqual(prayer_potion_restore_amount_pure(80, "prayer"), 27)
        self.assertEqual(prayer_potion_restore_amount_pure(80, "s_prayer"), 35)
        self.assertEqual(prayer_potion_restore_amount_pure(99, "prayer"), 31)
        self.assertEqual(prayer_potion_restore_amount_pure(99, "s_prayer"), 41)

        regular, regular_result = apply_consumable_pure(
            {
                "inventory": {"Prayer potion (3)": 1},
                "prayer_level": 80,
                "combat_prayer_points": 100,
                "combat_current_levels": {"attack": 77},
            },
            "Prayer potion (3)",
        )
        self.assertTrue(regular_result["allowed"])
        self.assertEqual(regular["combat_prayer_points"], 370)
        self.assertEqual(regular_result["prayer_points_restored"], 27.0)
        self.assertEqual(regular["combat_current_levels"], {"attack": 77})
        self.assertEqual(regular["inventory"], {"Prayer potion (2)": 1})

        super_prayer, super_result = apply_consumable_pure(
            {
                "inventory": {"Super prayer (3)": 1},
                "prayer_level": 80,
                "combat_prayer_points": 790,
                "combat_current_levels": {},
            },
            "Super prayer (3)",
        )
        self.assertEqual(super_prayer["combat_prayer_points"], 800)
        self.assertEqual(super_result["prayer_points_restored"], 1.0)
        self.assertNotIn("prayer", super_prayer["combat_current_levels"])
        self.assertEqual(super_prayer["inventory"], {"Super prayer (2)": 1})

    def test_summoning_potion_restores_exact_points_and_decrements_dose(self):
        restored, result = apply_consumable_pure(
            {
                "inventory": {"Summoning potion (3)": 1},
                "summoning_level": 80,
                "summoning_state": {
                    "summoning_points_current": 10,
                    "special_move_points_current": 40,
                },
            },
            "Summoning potion (3)",
        )

        self.assertTrue(result["allowed"])
        self.assertEqual(result["summoning_points_restored"], 27)
        self.assertEqual(result["special_move_points_restored"], 15)
        self.assertEqual(
            restored["summoning_state"]["summoning_points_current"], 37
        )
        self.assertEqual(restored["inventory"], {"Summoning potion (2)": 1})
        self.assertEqual(
            restored["summoning_state"]["special_move_points_current"], 55
        )

        capped, capped_result = apply_consumable_pure(
            {
                "inventory": {"Summoning flask (1)": 1},
                "summoning_level": 80,
                "summoning_state": {"summoning_points_current": 79},
            },
            "Summoning flask (1)",
        )
        self.assertEqual(capped_result["summoning_points_restored"], 1)
        self.assertEqual(capped["summoning_state"]["summoning_points_current"], 80)
        self.assertEqual(capped["inventory"], {"Potion flask": 1})

    def test_super_restore_repairs_stats_prayer_and_summoning_but_not_specials(self):
        restored, result = apply_consumable_pure(
            {
                "inventory": {"Super restore (3)": 1},
                "attack_level": 80,
                "strength_level": 80,
                "defense_level": 80,
                "ranged_level": 80,
                "magic_level": 80,
                "prayer_level": 80,
                "summoning_level": 80,
                "combat_current_levels": {"attack": 50, "magic": 90},
                "combat_prayer_points": 100,
                "summoning_state": {
                    "summoning_points_current": 10,
                    "special_move_points_current": 40,
                },
            },
            "Super restore (3)",
        )

        self.assertTrue(result["allowed"])
        self.assertEqual(result["stats_restored"], {"attack": 28})
        self.assertEqual(result["prayer_points_restored"], 28.0)
        self.assertEqual(result["summoning_points_restored"], 28)
        self.assertEqual(result["special_move_points_restored"], 0)
        self.assertEqual(restored["combat_current_levels"]["attack"], 78)
        self.assertEqual(restored["combat_current_levels"]["magic"], 90)
        self.assertEqual(restored["combat_prayer_points"], 380)
        self.assertEqual(
            restored["summoning_state"]["summoning_points_current"], 38
        )
        self.assertEqual(
            restored["summoning_state"]["special_move_points_current"], 40
        )
        self.assertEqual(restored["inventory"], {"Super restore (2)": 1})

    def test_potion_boost_is_a_floor_that_cures_drains_without_stacking(self):
        # boost-to-floor: sets current to base+boost, cures a drain, never
        # stacks past base+boost, never lowers a higher boost.
        data = {"strength_level": 50}
        apply_combat_stat_delta_pure(data, "strength", -5)  # drained to 45
        apply_combat_stat_boost_to_pure(data, "strength", 8)  # -> base+8 = 58
        self.assertEqual(_combat_effective_skill_level(data, "strength", 1), 58)
        apply_combat_stat_boost_to_pure(data, "strength", 8)  # no stack
        self.assertEqual(_combat_effective_skill_level(data, "strength", 1), 58)
        apply_combat_stat_boost_to_pure(data, "strength", 3)  # smaller, no lower
        self.assertEqual(_combat_effective_skill_level(data, "strength", 1), 58)

    def test_stat_potion_boosts_and_decrements_dose(self):
        pd = {"inventory": {"Strength potion (3)": 1}, "strength_level": 40}
        data, result = apply_consumable_pure(pd, "Strength potion (3)")
        self.assertTrue(result["allowed"])
        self.assertEqual(result["boosts"], {"strength": 7})
        self.assertEqual(_combat_effective_skill_level(data, "strength", 1), 47)
        self.assertEqual(data["inventory"].get("Strength potion (2)"), 1)
        self.assertNotIn("Strength potion (3)", data["inventory"])
        self.assertEqual(pd["inventory"]["Strength potion (3)"], 1)  # input untouched

    def test_combat_potion_boosts_both_and_last_dose_leaves_vial(self):
        pc = {"inventory": {"Combat potion (1)": 1}, "attack_level": 50, "strength_level": 60}
        data, result = apply_consumable_pure(pc, "Combat potion (1)")
        self.assertEqual(set(result["boosts"]), {"attack", "strength"})
        self.assertEqual(data["inventory"].get("Vial"), 1)
        self.assertNotIn("Combat potion (1)", data["inventory"])

    def test_beer_applies_source_potion_effect(self):
        # PotionType.BEER: +1 Constitution tick (10 LP), +4% current Strength,
        # -7% current Attack (floored).
        pd = {
            "inventory": {"Beer": 2}, "constitution_level": 10,
            "strength_level": 50, "attack_level": 60, "combat_lifepoints": 30,
        }
        data, result = apply_consumable_pure(pd, "Beer")
        self.assertTrue(result["allowed"])
        self.assertEqual(result["healed"], 10)
        self.assertEqual(result["boosts"], {"strength": 2})   # floor(50*0.04)
        self.assertEqual(result["drains"], {"attack": 4})     # floor(60*0.07)
        self.assertEqual(_combat_effective_skill_level(data, "strength", 1), 52)
        self.assertEqual(_combat_effective_skill_level(data, "attack", 1), 56)
        self.assertEqual(data["inventory"]["Beer"], 1)
        self.assertEqual(pd["inventory"]["Beer"], 2)  # input never mutated

    def test_kebab_random_effect_table_matches_source(self):
        # calculateKebabEffect roll bands (wiki oldid 4868155).
        pd = {
            "inventory": {"Kebab": 5}, "constitution_level": 99,
            "attack_level": 99, "strength_level": 99, "defense_level": 99,
            "combat_lifepoints": 100,
        }
        # roll 0.5 -> 50.0 -> common 10% heal band (99 LP of a 990 max).
        _d, common = apply_consumable_pure(pd, "Kebab", rng=lambda: 0.5)
        self.assertEqual(common["healed"], 99)
        self.assertEqual(common["boosts"], {})
        # roll 0.93 -> 93.0 -> rare boost band: heal 300 + 2..3 to Att/Str/Def.
        boost_rolls = iter([0.93, 0.0, 0.0, 0.0])
        d3, boost = apply_consumable_pure(pd, "Kebab", rng=lambda: next(boost_rolls))
        self.assertEqual(boost["healed"], 300)
        self.assertEqual(boost["boosts"], {"attack": 2, "strength": 2, "defense": 2})
        self.assertEqual(_combat_effective_skill_level(d3, "attack", 1), 101)
        # roll 0.99 -> 99.0 -> dodgy drain band.
        drain_rolls = iter([0.99, 0.0, 0.0])
        _d4, drain = apply_consumable_pure(pd, "Kebab", rng=lambda: next(drain_rolls))
        self.assertTrue(drain["drains"])

    def test_juju_farming_potion_uses_answer_driven_farm_clock_and_preserves_dose(self):
        pd = {"inventory": {"Juju farming potion (3)": 1}, "farm_clock_minutes": 17}

        data, result = apply_consumable_pure(pd, "Juju farming potion (3)")

        self.assertTrue(result["allowed"])
        self.assertEqual(data["farm_juju_active_until"], 22)
        self.assertEqual(data["inventory"], {"Juju farming potion (2)": 1})
        self.assertEqual(pd["inventory"], {"Juju farming potion (3)": 1})

    def test_run_energy_food_heals_and_banks_next_trip_credit(self):
        fruit = {
            "inventory": {"White tree fruit": 1},
            "constitution_level": 10,
            "combat_lifepoints": 40,
            "agility_run_energy_credit_pct": 0,
        }
        after_fruit, fruit_result = apply_consumable_pure(
            fruit,
            "White tree fruit",
        )
        self.assertTrue(fruit_result["allowed"])
        self.assertEqual(fruit_result["healed"], 30)
        self.assertEqual(fruit_result["run_energy_restored_pct"], 17)
        self.assertEqual(after_fruit["combat_lifepoints"], 70)
        self.assertEqual(after_fruit["agility_run_energy_credit_pct"], 17)

        pie = {
            "inventory": {"Summer pie": 1},
            "constitution_level": 99,
            "combat_lifepoints": 500,
            "agility_run_energy_credit_pct": 17,
        }
        after_pie, pie_result = apply_consumable_pure(pie, "Summer pie")
        self.assertEqual(pie_result["run_energy_restored_pct"], 20)
        self.assertEqual(after_pie["agility_run_energy_credit_pct"], 37)
        self.assertEqual(after_pie["inventory"]["Half a summer pie"], 1)

    def test_consumable_rejects_missing_and_non_consumable_items(self):
        _d, missing = apply_consumable_pure({"inventory": {}}, "Beer")
        self.assertFalse(missing["allowed"])
        self.assertEqual(missing["reason"], "missing_item")
        _d2, bad = apply_consumable_pure({"inventory": {"Logs": 1}}, "Logs")
        self.assertFalse(bad["allowed"])
        self.assertEqual(bad["reason"], "not_a_consumable")

    def test_molten_glass_smelt_returns_bucket_byproduct(self):
        # Shop-purchasable inputs close the glassblowing loop: smelting awards
        # the source 20 XP, consumes both inputs, and returns the emptied
        # bucket alongside the Molten glass.
        new_inv, exp, ok = apply_crafting_pure(
            "glass_molten_glass",
            {"Soda ash": 1, "Bucket of sand": 1},
            CRAFTING_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 20.0)
        self.assertEqual(new_inv["Molten glass"], 1)
        self.assertEqual(new_inv["Bucket"], 1)
        self.assertEqual(new_inv["Soda ash"], 0)
        self.assertEqual(new_inv["Bucket of sand"], 0)

    def test_item_combinations_and_button_polishing_execute_once(self):
        new_inv, exp, ok = apply_crafting_pure(
            "combine_bullseye_lantern",
            {"Bullseye lantern (unf)": 1, "Lantern lens": 1},
            CRAFTING_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 0.0)
        self.assertEqual(
            new_inv,
            {"Bullseye lantern (unf)": 0, "Lantern lens": 0, "Bullseye lantern (empty)": 1},
        )

        new_inv, exp, ok = apply_crafting_pure(
            "chisel_crab_helmet",
            {"Fresh crab shell": 1, "Chisel": 1},
            CRAFTING_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 32.5)
        self.assertEqual(new_inv, {"Fresh crab shell": 0, "Chisel": 1, "Crab helmet": 1})

        new_inv, exp, ok = apply_crafting_pure("polish_buttons", {"Buttons": 1}, CRAFTING_DATA)
        self.assertTrue(ok)
        self.assertEqual(exp, 5.0)
        self.assertEqual(new_inv, {"Buttons": 0, "Polished buttons": 1})

    def test_stringing_consumes_unstrung_amulet_and_cannot_repeat(self):
        furnace_inventory, furnace_xp, furnace_ok = apply_crafting_pure(
            "jewellery_gold_amulet",
            {"Gold bar": 1, "Amulet mould": 1},
            CRAFTING_DATA,
        )
        self.assertTrue(furnace_ok)
        self.assertEqual(furnace_xp, 30.0)
        self.assertEqual(furnace_inventory["Gold amulet (u)"], 1)

        strung_inventory, string_xp, string_ok = apply_crafting_pure(
            "string_gold_amulet",
            {**furnace_inventory, "Ball of wool": 1},
            CRAFTING_DATA,
        )
        self.assertTrue(string_ok)
        self.assertEqual(string_xp, 4.0)
        self.assertEqual(strung_inventory["Gold amulet (u)"], 0)
        self.assertEqual(strung_inventory["Gold amulet"], 1)

        unchanged, repeated_xp, repeated_ok = apply_crafting_pure(
            "string_gold_amulet",
            {**strung_inventory, "Ball of wool": 1},
            CRAFTING_DATA,
        )
        self.assertFalse(repeated_ok)
        self.assertEqual(repeated_xp, 0)
        self.assertEqual(unchanged["Gold amulet"], 1)

    def test_coin_paid_conversions_batch_with_per_unit_coins(self):
        # Tanning/sawmill conversions are review-paced no-XP batches with
        # coins consumed per unit, mirroring 2011's inventory-bounded runs
        # (they are deliberately NOT instant shop services).
        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "tan_soft_leather",
            {"Cowhide": 40, "Coins": 100},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 28)  # batch cap, not hides or coins
        self.assertEqual(new_inv["Leather"], 28)
        self.assertEqual(new_inv["Cowhide"], 12)
        self.assertEqual(new_inv["Coins"], 72)

        # Coins bound the batch when scarcer than inputs.
        new_inv, _exp, ok, processed = apply_utility_activity_pure(
            "tan_hard_leather",
            {"Cowhide": 28, "Coins": 10},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(processed, 3)  # 10 coins // 3 per hide
        self.assertEqual(new_inv["Hard leather"], 3)
        self.assertEqual(new_inv["Coins"], 1)

        new_inv, _exp, ok, processed = apply_utility_activity_pure(
            "convert_oak_logs_to_oak_planks",
            {"Oak logs": 5, "Coins": 600},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(processed, 2)  # 600 coins // 250 per plank
        self.assertEqual(new_inv["Oak plank"], 2)
        self.assertEqual(new_inv["Coins"], 100)

        self.assertFalse(
            can_perform_utility_activity_pure({"Logs": 5}, "convert_logs_to_planks", UTILITY_ACTIVITY_DATA)
        )

    def test_wet_flour_returns_empty_pot_and_bucket(self):
        inv = {"Pot of flour": 2, "Bucket of water": 2}
        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "wet_flour_to_pizza_base",
            inv,
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 2)
        self.assertEqual(new_inv["Pot of flour"], 0)
        self.assertEqual(new_inv["Bucket of water"], 0)
        self.assertEqual(new_inv["Pizza base"], 2)
        self.assertEqual(new_inv["Empty pot"], 2)
        self.assertEqual(new_inv["Bucket"], 2)

    def test_draw_bucket_of_water_requires_empty_bucket(self):
        inv = {"Bucket": 1}
        new_inv, exp, ok, processed = apply_utility_activity_pure(
            "draw_bucket_of_water",
            inv,
            UTILITY_ACTIVITY_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 1)
        self.assertEqual(new_inv["Bucket"], 0)
        self.assertEqual(new_inv["Bucket of water"], 1)

        empty_inv, _exp, ok, processed = apply_utility_activity_pure(
            "draw_bucket_of_water",
            {},
            UTILITY_ACTIVITY_DATA,
        )
        self.assertFalse(ok)
        self.assertEqual(processed, 0)
        self.assertEqual(empty_inv, {})

    def test_has_crafting_materials_and_apply(self):
        crafting_data = {
            "Soft clay": {"level": 1, "exp": 0, "requirements": {"Clay": 1}},
            "Gold ring": {"level": 5, "exp": 15, "requirements": {"Gold bar": 1}},
        }
        inv = {"Clay": 1, "Gold bar": 1}
        self.assertTrue(has_crafting_materials_pure("Soft clay", inv, crafting_data))
        self.assertTrue(has_crafting_materials_pure("Gold ring", inv, crafting_data))

        new_inv, exp, ok = apply_crafting_pure("Soft clay", inv, crafting_data)
        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(new_inv.get("Soft clay"), 1)
        self.assertEqual(new_inv.get("Clay"), 0)

        new_inv2, exp2, ok2 = apply_crafting_pure("Gold ring", inv, crafting_data)
        self.assertTrue(ok2)
        self.assertEqual(exp2, 15)
        self.assertEqual(new_inv2.get("Gold ring"), 1)
        self.assertEqual(new_inv2.get("Gold bar"), 0)

    def test_leather_crafting_requires_thread_and_consumes_only_on_source_roll(self):
        inventory = {"Leather": 1, "Thread": 1}

        self.assertFalse(has_crafting_materials_pure("leather_leather_gloves", {"Leather": 1}, CRAFTING_DATA))

        retained, exp, ok = apply_crafting_pure("leather_leather_gloves", inventory, CRAFTING_DATA, random_roll=2)
        self.assertTrue(ok)
        self.assertEqual(exp, 13.8)
        self.assertEqual(retained, {"Leather": 0, "Thread": 1, "Leather gloves": 1})

        consumed, exp, ok = apply_crafting_pure("leather_leather_gloves", inventory, CRAFTING_DATA, random_roll=1)
        self.assertTrue(ok)
        self.assertEqual(exp, 13.8)
        self.assertEqual(consumed, {"Leather": 0, "Thread": 0, "Leather gloves": 1})

    def test_mould_and_pipe_are_required_but_not_consumed(self):
        self.assertFalse(has_crafting_materials_pure("jewellery_gold_ring", {"Gold bar": 1}, CRAFTING_DATA))
        self.assertFalse(has_crafting_materials_pure("glass_beer_glass", {"Molten glass": 1}, CRAFTING_DATA))

        ring_inventory, ring_exp, ring_ok = apply_crafting_pure(
            "jewellery_gold_ring", {"Gold bar": 1, "Ring mould": 1}, CRAFTING_DATA
        )
        self.assertTrue(ring_ok)
        self.assertEqual(ring_exp, 15.0)
        self.assertEqual(ring_inventory, {"Gold bar": 0, "Ring mould": 1, "Gold ring": 1})

        glass_inventory, glass_exp, glass_ok = apply_crafting_pure(
            "glass_beer_glass", {"Molten glass": 1, "Glassblowing pipe": 1}, CRAFTING_DATA
        )
        self.assertTrue(glass_ok)
        self.assertEqual(glass_exp, 17.5)
        self.assertEqual(glass_inventory, {"Molten glass": 0, "Glassblowing pipe": 1, "Beer glass": 1})

    def test_crafting_readiness_requires_live_tools(self):
        cases = (
            ("clay ring", 4, {"Soft clay": 1}, "Ring mould", "form_clay_ring_unfired"),
            ("gold ring", 5, {"Gold bar": 1}, "Ring mould", "jewellery_gold_ring"),
        )
        for name, level, inventory, tool, recipe_id in cases:
            with self.subTest(name):
                self.assertFalse(can_craft_item_pure(level, inventory, recipe_id, CRAFTING_DATA))
                self.assertTrue(can_craft_item_pure(
                    level, {**inventory, tool: 1}, recipe_id, CRAFTING_DATA
                ))

    def test_unfired_clay_ring_consumes_clay_and_retains_ring_mould(self):
        inventory, exp, ok = apply_crafting_pure(
            "form_clay_ring_unfired", {"Soft clay": 1, "Ring mould": 1}, CRAFTING_DATA
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 11.3)
        self.assertEqual(inventory, {"Soft clay": 0, "Ring mould": 1, "Clay ring (unfired)": 1})

    def test_apply_crafting_pure_ignores_batch_size_for_xp_actions(self):
        crafting_data = {
            "Bow string": {
                "level": 10,
                "exp": 15,
                "requirements": {"Flax": 1},
                "batch_size": 28,
            }
        }
        inv = {"Flax": 30}

        new_inv, exp, ok = apply_crafting_pure("Bow string", inv, crafting_data)

        self.assertTrue(ok)
        self.assertEqual(exp, 15)
        self.assertEqual(new_inv["Flax"], 29)
        self.assertEqual(new_inv["Bow string"], 1)
        self.assertEqual(inv["Flax"], 30)

    def test_apply_crafting_pure_respects_output_quantity(self):
        crafting_data = {
            "Silver bolts (unf)": {
                "level": 21,
                "exp": 50,
                "requirements": {"Silver bar": 1},
                "output_qty": 10,
            }
        }

        new_inv, exp, ok = apply_crafting_pure("Silver bolts (unf)", {"Silver bar": 1}, crafting_data)

        self.assertTrue(ok)
        self.assertEqual(exp, 50)
        self.assertEqual(new_inv["Silver bar"], 0)
        self.assertEqual(new_inv["Silver bolts (unf)"], 10)

    def test_review_action_multiplier_validation(self):
        self.assertEqual(sanitize_review_action_multiplier("2.5"), 2)
        self.assertEqual(sanitize_review_action_multiplier("bad"), 1)
        self.assertEqual(sanitize_review_action_multiplier(True), 1)
        self.assertEqual(sanitize_review_action_multiplier(-5), 1)
        self.assertEqual(sanitize_review_action_multiplier(500), 10)

    def test_apply_smelt_pure(self):
        bar_data = {
            "Bronze bar": {"level": 1, "exp": 6.2, "ore_required": {"Copper ore": 1, "Tin ore": 1}},
            "Iron bar": {"level": 15, "exp": 12.5, "ore_required": {"Iron ore": 1}},
        }
        inv = {"Copper ore": 1, "Tin ore": 1}
        new_inv, exp, ok = apply_smelt_pure("Bronze bar", inv, bar_data)
        self.assertTrue(ok)
        self.assertAlmostEqual(exp, 6.2)
        self.assertEqual(new_inv.get("Bronze bar"), 1)
        self.assertEqual(new_inv.get("Copper ore"), 0)
        self.assertEqual(new_inv.get("Tin ore"), 0)

        # Failure when missing materials
        inv2 = {"Copper ore": 1}
        new_inv2, exp2, ok2 = apply_smelt_pure("Bronze bar", inv2, bar_data)
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertEqual(new_inv2, inv2)

    def test_apply_woodcutting_pure(self):
        tree_data = {"oak": {"exp": 15, "probability": 0.8, "output_item": "Oak logs"}}
        inv = {}
        # success when r < p
        new_inv, exp, ok = apply_woodcutting_pure("oak", inv, tree_data, r_action=0.1, success_probability=0.5)
        self.assertTrue(ok)
        self.assertEqual(exp, 15)
        self.assertEqual(new_inv.get("Oak logs"), 1)
        # failure when r >= p
        new_inv2, exp2, ok2 = apply_woodcutting_pure("oak", inv, tree_data, r_action=0.6, success_probability=0.5)
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertEqual(new_inv2, inv)

    def test_woodcutting_axe_selection_and_source_shaped_probability(self):
        axe_data = {
            "bronze_hatchet": {"display_name": "Bronze hatchet", "level": 1, "ratio": 1.0, "status": "implemented"},
            "rune_hatchet": {"display_name": "Rune hatchet", "level": 41, "ratio": 3.5, "status": "implemented"},
        }
        target = {"low_chance": 32, "high_chance": 100}

        bronze = best_woodcutting_axe_pure(50, {}, {"woodcutting": ["bronze_hatchet"]}, axe_data)
        still_bronze = best_woodcutting_axe_pure(
            50,
            {"Rune hatchet": 1},
            {"woodcutting": ["bronze_hatchet"]},
            axe_data,
        )
        rune = best_woodcutting_axe_pure(
            50,
            {},
            {"woodcutting": ["bronze_hatchet", "rune_hatchet"]},
            axe_data,
        )

        self.assertEqual(bronze["display_name"], "Bronze hatchet")
        self.assertEqual(still_bronze["display_name"], "Bronze hatchet")
        self.assertEqual(rune["display_name"], "Rune hatchet")
        self.assertGreater(
            calculate_woodcutting_success_probability_pure(50, target, rune),
            calculate_woodcutting_success_probability_pure(50, target, bronze),
        )

    def test_woodcutting_axe_selection_prefers_later_equal_ratio_source_row(self):
        axe_data = {
            "dragon_hatchet": {"display_name": "Dragon hatchet", "level": 61, "ratio": 3.75},
            "inferno_adze": {"display_name": "Inferno adze", "level": 61, "ratio": 3.75},
        }

        axe = best_woodcutting_axe_pure(
            61,
            {},
            {"woodcutting": ["dragon_hatchet", "inferno_adze"]},
            axe_data,
        )

        self.assertEqual(axe["display_name"], "Inferno adze")

    def test_apply_woodcutting_action_awards_output_and_bird_nest(self):
        tree_data = {"tree": {"exp": 25.0, "output_item": "Logs", "low_chance": 64, "high_chance": 200}}
        axe = {"display_name": "Bronze hatchet", "level": 1, "ratio": 1.0, "status": "implemented"}
        nest_table = (
            {"item": "Bird's nest (seeds)", "weight": 65},
            {"item": "Bird's nest (ring)", "weight": 35},
        )

        new_inv, exp, ok, output_item, nest_item = apply_woodcutting_action_pure(
            "tree",
            {},
            tree_data,
            1,
            axe,
            r_action=0.0,
            r_nest_drop=0.0,
            r_nest_type=0.0,
            nest_drop_table=nest_table,
            nest_drop_chance=1.0,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 25.0)
        self.assertEqual(output_item, "Logs")
        self.assertEqual(nest_item, "Bird's nest (seeds)")
        self.assertEqual(new_inv["Logs"], 1)
        self.assertEqual(new_inv["Bird's nest (seeds)"], 1)

    def test_apply_woodcutting_action_ivy_awards_xp_without_output(self):
        tree_data = {"ivy": {"exp": 332.5, "output_item": None, "low_chance": 7, "high_chance": 11}}
        axe = {"display_name": "Dragon hatchet", "level": 61, "ratio": 3.75, "status": "implemented"}

        new_inv, exp, ok, output_item, nest_item = apply_woodcutting_action_pure(
            "ivy",
            {},
            tree_data,
            99,
            axe,
            r_action=0.0,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 332.5)
        self.assertIsNone(output_item)
        self.assertIsNone(nest_item)
        self.assertEqual(new_inv, {})

    def test_special_tree_placeholders_preserve_their_sourced_outputs_and_xp(self):
        axe = {
            "display_name": "Rune hatchet",
            "level": 41,
            "ratio": 3.5,
            "status": "implemented",
        }
        for target_id, output_item, expected_xp, expected_quantity in (
            ("arctic_pine", "Arctic pine logs", 140.2, 1),
            ("eucalyptus", "Eucalyptus logs", 165.0, 1),
            ("curly_jade_root", "Curly root", 161.6, 4),
        ):
            with self.subTest(target_id=target_id):
                inventory, xp, ok, output, nest = apply_woodcutting_action_pure(
                    target_id,
                    {},
                    TREE_DATA,
                    99,
                    axe,
                    r_action=0.0,
                    r_nest_drop=1.0,
                )
                self.assertTrue(ok)
                self.assertEqual(xp, expected_xp)
                self.assertEqual(output, output_item)
                self.assertIsNone(nest)
                self.assertEqual(inventory, {output_item: expected_quantity})

    def test_apply_woodcutting_action_inferno_adze_incinerates_logs(self):
        tree_data = {"tree": {"exp": 25.0, "output_item": "Logs", "low_chance": 64, "high_chance": 200}}
        axe = {
            "display_name": "Inferno adze",
            "level": 61,
            "ratio": 3.75,
            "incinerates_logs": True,
            "incinerate_chance": 1 / 2,
            "status": "implemented",
        }

        new_inv, exp, ok, output_item, nest_item = apply_woodcutting_action_pure(
            "tree",
            {},
            tree_data,
            99,
            axe,
            r_action=0.0,
            r_inferno_adze=0.0,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 25.0)
        self.assertIsNone(output_item)
        self.assertIsNone(nest_item)
        self.assertEqual(new_inv, {})

    def test_open_bird_nests_batches_random_contents_without_xp(self):
        tables = {
            "Bird's nest (seeds)": {
                "guaranteed_item": "Bird's nest (empty)",
                "total_weight": 2,
                "rolls": (
                    {"item": "Acorn", "weight": 1},
                    {"item": "Magic seed", "weight": 1},
                ),
            }
        }

        new_inv, ok, opened, outputs = apply_open_bird_nests_pure(
            {"Bird's nest (seeds)": 2},
            tables,
            rolls=[0.0, 0.75],
            batch_size=28,
        )

        self.assertTrue(ok)
        self.assertEqual(opened, 2)
        self.assertEqual(new_inv["Bird's nest (seeds)"], 0)
        self.assertEqual(new_inv["Bird's nest (empty)"], 2)
        self.assertEqual(new_inv["Acorn"], 1)
        self.assertEqual(new_inv["Magic seed"], 1)
        self.assertEqual(outputs["Bird's nest (empty)"], 2)

    def test_apply_mining_pure_with_gem(self):
        ore_data = {"Iron ore": {"exp": 35, "probability": 0.8}}
        gem_data = {
            "Uncut sapphire": {"probability": 0.5, "exp": 50},
            "Uncut emerald": {"probability": 0.5, "exp": 67.5},
        }
        inv = {}
        # Force success and gem drop; pick first gem via r_gem_pick
        new_inv, exp, ok, gem = apply_mining_pure(
            "Iron ore", inv, ore_data, gem_data,
            r_action=0.1, success_probability=0.5,
            r_gem_chance=0.0, r_gem_pick=0.1, gem_drop_chance=1.0  # make drop guaranteed for test
        )
        self.assertTrue(ok)
        self.assertEqual(gem, "Uncut sapphire")
        self.assertEqual(new_inv.get("Iron ore"), 1)
        self.assertEqual(new_inv.get("Uncut sapphire"), 1)
        self.assertAlmostEqual(exp, 35 + 50)
        # Failure when action doesn't succeed
        new_inv2, exp2, ok2, gem2 = apply_mining_pure(
            "Iron ore", inv, ore_data, gem_data,
            r_action=0.9, success_probability=0.5,
            r_gem_chance=0.0, r_gem_pick=0.1,
        )
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertIsNone(gem2)
        self.assertEqual(new_inv2, inv)

    def test_best_mining_pickaxe_prefers_best_attached_usable_tool(self):
        pickaxe = best_mining_pickaxe_pure(
            41,
            {"Rune pickaxe": 1, "Inferno adze": 1},
            {"mining": ["bronze_pickaxe", "rune_pickaxe", "inferno_adze"]},
            MINING_PICKAXE_DATA,
        )
        self.assertEqual(pickaxe["display_name"], "Inferno adze")

        pickaxe = best_mining_pickaxe_pure(
            41,
            {"Dragon pickaxe": 1},
            {"mining": ["bronze_pickaxe", "rune_pickaxe"]},
            MINING_PICKAXE_DATA,
        )
        self.assertEqual(pickaxe["display_name"], "Rune pickaxe")

        pickaxe = best_mining_pickaxe_pure(
            61,
            {},
            {"mining": ["bronze_pickaxe", "rune_pickaxe", "dragon_pickaxe"]},
            MINING_PICKAXE_DATA,
        )
        self.assertEqual(pickaxe["display_name"], "Dragon pickaxe")

    def test_mining_success_probability_scales_by_pickaxe_and_target(self):
        bronze = MINING_PICKAXE_DATA["bronze_pickaxe"]
        rune = MINING_PICKAXE_DATA["rune_pickaxe"]
        iron = ORE_DATA["iron"]
        runite = ORE_DATA["runite"]

        self.assertGreater(
            calculate_mining_success_probability_pure(60, iron, rune),
            calculate_mining_success_probability_pure(60, iron, bronze),
        )
        self.assertGreater(
            calculate_mining_success_probability_pure(60, iron, rune),
            calculate_mining_success_probability_pure(60, runite, rune),
        )

    def test_apply_mining_action_outputs_pure_essence_without_random_gems(self):
        new_inv, exp, ok, output_item, gem, extra = apply_mining_action_pure(
            "rune_essence",
            {"Pure essence": 0, "Uncut sapphire": 0},
            ORE_DATA,
            30,
            MINING_PICKAXE_DATA["bronze_pickaxe"],
            0.0,
            0.0,
            0.0,
            0.0,
            INCIDENTAL_GEM_DROP_TABLE,
            1.0,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 5.0)
        self.assertEqual(output_item, "Pure essence")
        self.assertIsNone(gem)
        self.assertIsNone(extra)
        self.assertEqual(new_inv["Pure essence"], 1)
        self.assertEqual(new_inv["Uncut sapphire"], 0)

    def test_apply_mining_action_concentrated_rocks_suppress_random_gems(self):
        for target_id, output_item, exp in (
            ("concentrated_coal", "Coal", 50.0),
            ("concentrated_gold", "Gold ore", 65.0),
        ):
            new_inv, actual_exp, ok, actual_output, gem, _extra = apply_mining_action_pure(
                target_id,
                {output_item: 0, "Uncut sapphire": 0},
                ORE_DATA,
                80,
                MINING_PICKAXE_DATA["rune_pickaxe"],
                0.0,
                0.0,
                0.0,
                0.0,
                INCIDENTAL_GEM_DROP_TABLE,
                1.0,
            )

            self.assertTrue(ok)
            self.assertEqual(actual_exp, exp)
            self.assertEqual(actual_output, output_item)
            self.assertIsNone(gem)
            self.assertEqual(new_inv[output_item], 1)
            self.assertEqual(new_inv["Uncut sapphire"], 0)

    def test_apply_mining_action_living_rock_remains_uses_sourced_bundle_range(self):
        for roll, expected_quantity in ((0.0, 5), (0.999999, 24)):
            new_inv, exp, ok, output_item, gem, extra = apply_mining_action_pure(
                "living_rock_remains",
                {"Living minerals": 0},
                ORE_DATA,
                73,
                MINING_PICKAXE_DATA["rune_pickaxe"],
                0.0,
                roll,
                0.0,
                0.0,
                INCIDENTAL_GEM_DROP_TABLE,
                1.0,
            )

            self.assertTrue(ok)
            self.assertEqual(exp, 25.0)
            self.assertEqual(output_item, "Living minerals")
            self.assertIsNone(gem)
            self.assertIsNone(extra)
            self.assertEqual(new_inv["Living minerals"], expected_quantity)

    def test_apply_mining_action_weighted_outputs_use_output_xp(self):
        new_inv, exp, ok, output_item, _gem, _extra = apply_mining_action_pure(
            "sandstone",
            {},
            ORE_DATA,
            35,
            MINING_PICKAXE_DATA["rune_pickaxe"],
            0.0,
            0.99,
        )

        self.assertTrue(ok)
        self.assertEqual(output_item, "Sandstone (10kg)")
        self.assertEqual(exp, 60.0)
        self.assertEqual(new_inv["Sandstone (10kg)"], 1)

    def test_apply_mining_action_gems_are_inventory_only_side_drops(self):
        new_inv, exp, ok, output_item, gem, _extra = apply_mining_action_pure(
            "iron",
            {"Iron ore": 0, "Uncut sapphire": 0},
            ORE_DATA,
            60,
            MINING_PICKAXE_DATA["rune_pickaxe"],
            0.0,
            0.0,
            0.0,
            0.99,
            INCIDENTAL_GEM_DROP_TABLE,
            GLORY_GEM_DROP_CHANCE,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 35.0)
        self.assertEqual(output_item, "Iron ore")
        self.assertEqual(gem, "Uncut sapphire")
        self.assertEqual(new_inv["Iron ore"], 1)
        self.assertEqual(new_inv["Uncut sapphire"], 1)

    def test_mining_bonus_state_and_varrock_extra_output(self):
        bonus_state = equipment_bonus_state_pure(
            {"neck": "Amulet of glory (4)", "body": "Varrock armour 1"},
            MINING_BONUS_ITEM_DATA,
        )

        self.assertTrue(bonus_state["has_glory"])
        self.assertEqual(bonus_state["varrock_armour_tier"], 1)

        new_inv, exp, ok, output_item, _gem, extra = apply_mining_action_pure(
            "coal",
            {"Coal": 0},
            ORE_DATA,
            60,
            MINING_PICKAXE_DATA["rune_pickaxe"],
            0.0,
            0.0,
            None,
            None,
            INCIDENTAL_GEM_DROP_TABLE,
            varrock_armour_tier=bonus_state["varrock_armour_tier"],
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 50.0)
        self.assertEqual(output_item, "Coal")
        self.assertEqual(extra, "Coal")
        self.assertEqual(new_inv["Coal"], 2)

    def test_trimmed_glory_runtime_aliases_enable_the_existing_gem_bonus(self):
        for item_name in (
            "Amulet of glory",
            "Amulet of glory (1)",
            "Amulet of glory (2)",
            "Amulet of glory (3)",
            "Amulet of glory (4)",
            "Amulet of glory (t)",
            "Amulet of glory (t1)",
            "Amulet of glory (t2)",
            "Amulet of glory (t3)",
            "Amulet of glory (t4)",
        ):
            with self.subTest(item_name=item_name):
                bonus_state = equipment_bonus_state_pure({"neck": item_name}, MINING_BONUS_ITEM_DATA)
                self.assertTrue(bonus_state["has_glory"])

    def test_can_equip_uses_real_combat_level_gate(self):
        ok, reason = can_equip_item_pure("Bronze platebody", EQUIPMENT_DATA, {"defense_level": 1})
        self.assertTrue(ok)
        self.assertEqual(reason, "")

        ok, reason = can_equip_item_pure("Rune platebody", EQUIPMENT_DATA, {"defense_level": 1})
        self.assertFalse(ok)
        self.assertEqual(reason, "Requires level 40 Defense")

        ok, reason = can_equip_item_pure("Fire battlestaff", EQUIPMENT_DATA, {"attack_level": 30, "magic_level": 1})
        self.assertFalse(ok)
        self.assertEqual(reason, "Requires level 30 Magic")

        ok, reason = can_equip_item_pure("Fire battlestaff", EQUIPMENT_DATA, {"attack_level": 30, "magic_level": 30})
        self.assertTrue(ok)
        self.assertEqual(reason, "")

        ok, reason = can_equip_item_pure(
            "Insulated boots", EQUIPMENT_DATA, {"slayer_level": 36}
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "Requires level 37 Slayer")

        ok, reason = can_equip_item_pure(
            "Insulated boots", EQUIPMENT_DATA, {"slayer_level": 37}
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "")

    def test_equip_unequip_returns_displaced_items(self):
        inv = {"Bronze platebody": 1, "Iron platebody": 1}
        new_inv, equipment, ok = equip_item_pure("Bronze platebody", inv, {}, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(new_inv["Bronze platebody"], 0)
        self.assertEqual(equipment, {"body": "Bronze platebody"})

        new_inv, equipment, ok = equip_item_pure("Iron platebody", new_inv, equipment, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(new_inv["Iron platebody"], 0)
        self.assertEqual(new_inv["Bronze platebody"], 1)
        self.assertEqual(equipment, {"body": "Iron platebody"})

        new_inv, equipment, ok = unequip_item_pure("body", new_inv, equipment)
        self.assertTrue(ok)
        self.assertEqual(new_inv["Iron platebody"], 1)
        self.assertEqual(equipment, {})

    def test_shop_blackjack_uses_the_equippable_canonical_identity(self):
        inventory, equipment, ok = equip_item_pure(
            "Willow blackjack", {"Willow blackjack": 1}, {}, EQUIPMENT_DATA
        )

        self.assertTrue(ok)
        self.assertEqual(inventory["Willow blackjack"], 0)
        self.assertEqual(equipment, {"weapon": "Willow blackjack"})

    def test_live_quest_equipment_can_be_worn_with_sourced_level_gates(self):
        expected_slots = {
            "Ice arrows": "ammunition",
            "Pendant of lucien": "neck",
            "Armadyl pendant": "neck",
            "Gnome amulet": "neck",
            "Yew comp bow": "weapon",
            "Magic comp bow": "weapon",
            "Dark bow": "weapon",
        }
        for item_name, slot in expected_slots.items():
            with self.subTest(item_name=item_name):
                inventory, equipment, ok = equip_item_pure(
                    item_name, {item_name: 1}, {}, EQUIPMENT_DATA
                )
                self.assertTrue(ok)
                self.assertEqual(inventory[item_name], 0)
                self.assertEqual(equipment, {slot: item_name})

        for item_name, required_level in (
            ("Yew comp bow", 40),
            ("Magic comp bow", 50),
            ("Dark bow", 60),
        ):
            with self.subTest(item_name=item_name, required_level=required_level):
                ok, reason = can_equip_item_pure(
                    item_name, EQUIPMENT_DATA, {"ranged_level": required_level - 1}
                )
                self.assertFalse(ok)
                self.assertEqual(reason, f"Requires level {required_level} Ranged")

                ok, reason = can_equip_item_pure(
                    item_name, EQUIPMENT_DATA, {"ranged_level": required_level}
                )
                self.assertTrue(ok)
                self.assertEqual(reason, "")

    def test_two_handed_weapon_and_shield_displace_each_other(self):
        inv = {"Bronze 2h sword": 1, "Bronze sq shield": 1}
        inv, equipment, ok = equip_item_pure("Bronze sq shield", inv, {}, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(equipment, {"shield": "Bronze sq shield"})

        inv, equipment, ok = equip_item_pure("Bronze 2h sword", inv, equipment, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(equipment, {"weapon": "Bronze 2h sword"})
        self.assertEqual(inv["Bronze sq shield"], 1)

        inv, equipment, ok = equip_item_pure("Bronze sq shield", inv, equipment, EQUIPMENT_DATA)
        self.assertTrue(ok)
        self.assertEqual(equipment, {"shield": "Bronze sq shield"})
        self.assertEqual(inv["Bronze 2h sword"], 1)

    def test_equipment_stat_totals_sum_worn_bonuses(self):
        totals = equipment_stat_totals_pure(
            {"weapon": "Bronze sword", "body": "Bronze platebody"},
            EQUIPMENT_DATA,
        )
        self.assertEqual(totals.attack_stab, EQUIPMENT_DATA["Bronze sword"].bonuses.attack_stab)
        self.assertEqual(totals.defence_stab, EQUIPMENT_DATA["Bronze platebody"].bonuses.defence_stab)
        self.assertEqual(totals.melee_strength, EQUIPMENT_DATA["Bronze sword"].bonuses.melee_strength)

    def test_can_mine_and_cut_pure(self):
        ore_data = {"Copper ore": {"level": 1}, "Iron ore": {"level": 15}}
        tree_data = {"tree": {"level": 1}, "oak": {"level": 15}}
        self.assertTrue(can_mine_ore_pure(1, "Copper ore", ore_data))
        self.assertFalse(can_mine_ore_pure(1, "Iron ore", ore_data))
        self.assertTrue(can_cut_tree_pure(1, "tree", tree_data))
        self.assertFalse(can_cut_tree_pure(1, "oak", tree_data))

    def test_can_craft_item_pure(self):
        crafting_data = {
            "Gold ring": {"level": 5, "requirements": {"Gold bar": 1}},
            "Soft clay": {"level": 1, "requirements": {"Clay": 1}},
        }
        inv = {"Gold bar": 1, "Clay": 1}
        self.assertFalse(can_craft_item_pure(1, inv, "Gold ring", crafting_data))  # level too low
        self.assertTrue(can_craft_item_pure(5, inv, "Gold ring", crafting_data))
        self.assertTrue(can_craft_item_pure(1, inv, "Soft clay", crafting_data))
        self.assertFalse(can_craft_item_pure(1, {}, "Soft clay", crafting_data))  # missing material

    def test_apply_fletching_pure(self):
        fletching_data = {
            "arrow_shafts": {
                "level": 1,
                "exp": 5.0,
                "requirements": {"Logs": 1},
                "output_item": "Arrow shafts",
                "output_qty": 15,
            },
            "oak_shortbow_u": {
                "level": 20,
                "exp": 16.5,
                "requirements": {"Oak logs": 1},
                "output_item": "Oak shortbow (u)",
                "output_qty": 1,
            },
        }
        inv = {"Logs": 2}
        self.assertTrue(can_fletch_item_pure(1, inv, "arrow_shafts", fletching_data))

        new_inv, exp, ok = apply_fletching_pure("arrow_shafts", inv, fletching_data)
        self.assertTrue(ok)
        self.assertAlmostEqual(exp, 5.0)
        self.assertEqual(new_inv["Logs"], 1)
        self.assertEqual(new_inv["Arrow shafts"], 15)
        self.assertEqual(inv["Logs"], 2)

        self.assertFalse(can_fletch_item_pure(1, {"Oak logs": 1}, "oak_shortbow_u", fletching_data))
        new_inv2, exp2, ok2 = apply_fletching_pure("oak_shortbow_u", {}, fletching_data)
        self.assertFalse(ok2)
        self.assertEqual(exp2, 0)
        self.assertEqual(new_inv2, {})

    def test_crossbow_combinations_consume_each_source_pair_without_xp(self):
        inventory, exp, ok = apply_fletching_pure(
            "combine_bronze_cbow_u",
            {"Bronze limbs": 1, "Wooden stock": 1},
            FLETCHING_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 0.0)
        self.assertEqual(inventory, {"Bronze limbs": 0, "Wooden stock": 0, "Bronze c'bow (u)": 1})

        inventory["Crossbow string"] = 1
        inventory, exp, ok = apply_fletching_pure("combine_bronze_crossbow", inventory, FLETCHING_DATA)
        self.assertTrue(ok)
        self.assertEqual(exp, 0.0)
        self.assertEqual(inventory, {"Bronze limbs": 0, "Wooden stock": 0, "Bronze c'bow (u)": 0, "Crossbow string": 0, "Bronze crossbow": 1})

    def test_long_kebbit_bolts_require_but_do_not_consume_the_chisel(self):
        without_tool = {"Long kebbit spike": 1}
        self.assertFalse(
            can_fletch_item_pure(
                42,
                without_tool,
                "fletch_long_kebbit_bolts",
                FLETCHING_DATA,
            )
        )

        inventory, exp, ok = apply_fletching_pure(
            "fletch_long_kebbit_bolts",
            {"Long kebbit spike": 1, "Chisel": 1},
            FLETCHING_DATA,
        )

        self.assertTrue(ok)
        self.assertAlmostEqual(exp, 7.98)
        self.assertEqual(
            inventory,
            {"Long kebbit spike": 0, "Chisel": 1, "Long kebbit bolts": 6},
        )

    def test_fletching_coloured_feathers_select_and_consume_one_exact_available_type(self):
        blue_inventory = {"Arrow shafts": 15, "Blue feather": 15}
        self.assertTrue(can_fletch_item_pure(1, blue_inventory, "headless_arrows", FLETCHING_DATA))
        self.assertEqual(
            fletching_material_requirements_pure("headless_arrows", blue_inventory, FLETCHING_DATA),
            {"Arrow shafts": 15, "Blue feather": 15},
        )
        new_inventory, exp, ok = apply_fletching_pure("headless_arrows", blue_inventory, FLETCHING_DATA)
        self.assertTrue(ok)
        self.assertEqual(new_inventory["Blue feather"], 0)
        self.assertEqual(new_inventory["Headless arrows"], 15)
        self.assertAlmostEqual(exp, 15.0)

        mixed_inventory = {"Arrow shafts": 15, "Feather": 15, "Red feather": 15}
        self.assertEqual(
            fletching_material_requirements_pure("headless_arrows", mixed_inventory, FLETCHING_DATA),
            {"Arrow shafts": 15, "Feather": 15},
        )

    def test_apply_herblore_action_pure_three_stage_pipeline(self):
        from ankiscape.core.constants import HERBLORE_DATA

        # Clean stage: grimy -> clean herb, herb XP awarded, gated on herb level.
        clean = HERBLORE_DATA["clean_guam"]
        self.assertEqual(clean["exp"], 2.5)
        inv = {"Grimy guam": 2}
        self.assertTrue(can_herblore_target_pure(3, inv, "clean_guam", HERBLORE_DATA))
        self.assertFalse(can_herblore_target_pure(2, inv, "clean_guam", HERBLORE_DATA))
        new_inv, exp, ok = apply_herblore_action_pure("clean_guam", inv, HERBLORE_DATA)
        self.assertTrue(ok)
        self.assertAlmostEqual(exp, 2.5)
        self.assertEqual(new_inv["Grimy guam"], 1)
        self.assertEqual(new_inv["Clean guam"], 1)
        self.assertEqual(inv["Grimy guam"], 2)  # input untouched

        # Unfinished stage: clean + Vial of water -> unf potion, ZERO XP.
        unf_inv = {"Clean guam": 1, "Vial of water": 1}
        new_unf, unf_exp, unf_ok = apply_herblore_action_pure("unf_guam", unf_inv, HERBLORE_DATA)
        self.assertTrue(unf_ok)
        self.assertEqual(unf_exp, 0.0)
        self.assertEqual(new_unf["Guam potion (unf)"], 1)
        self.assertEqual(new_unf["Clean guam"], 0)
        self.assertEqual(new_unf["Vial of water"], 0)

        # Finished stage: unf + secondary -> potion, recipe XP awarded.
        fin = HERBLORE_DATA["finished_attack_potion"]
        self.assertEqual(fin["exp"], 25.0)
        fin_inv = {"Guam potion (unf)": 1, "Eye of newt": 1}
        self.assertTrue(has_herblore_materials_pure("finished_attack_potion", fin_inv, HERBLORE_DATA))
        new_fin, fin_exp, fin_ok = apply_herblore_action_pure("finished_attack_potion", fin_inv, HERBLORE_DATA)
        self.assertTrue(fin_ok)
        self.assertAlmostEqual(fin_exp, 25.0)
        self.assertEqual(new_fin["Attack potion (3)"], 1)

        overload_inputs = {
            "Extreme attack (3)": 1,
            "Extreme strength (3)": 1,
            "Extreme defence (3)": 1,
            "Extreme magic (3)": 1,
            "Extreme ranging (3)": 1,
            "Clean torstol": 1,
        }
        self.assertTrue(can_herblore_target_pure(96, overload_inputs, "finished_overload", HERBLORE_DATA))
        overload_inv, overload_exp, overload_ok = apply_herblore_action_pure(
            "finished_overload", overload_inputs, HERBLORE_DATA
        )
        self.assertTrue(overload_ok)
        self.assertEqual(overload_exp, 1000.0)
        self.assertEqual(overload_inv["Overload (3)"], 1)
        self.assertEqual(overload_inv["Vial"], 4)
        self.assertTrue(all(overload_inv[item] == 0 for item in overload_inputs))

        # Missing materials and level gate both refuse and award nothing.
        self.assertEqual(
            herblore_target_locked_reasons_pure(
                {"herblore_level": 1, "inventory": {}}, "clean_guam", HERBLORE_DATA
            ),
            ("Herblore level 3", "materials"),
        )
        no_inv, no_exp, no_ok = apply_herblore_action_pure("finished_attack_potion", {}, HERBLORE_DATA)
        self.assertFalse(no_ok)
        self.assertEqual(no_exp, 0)
        self.assertEqual(no_inv, {})

    def test_juju_hunter_potion_drink_consumes_a_dose_without_a_stat_boost(self):
        from ankiscape.core.constants import HERBLORE_DATA

        inventory, exp, ok = apply_herblore_action_pure(
            "finished_juju_hunting",
            {"Erzille potion (unf)": 1, "Corrupt vine": 1},
            HERBLORE_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 123.0)
        self.assertEqual(inventory["Juju hunter potion (3)"], 1)

        player_data = {
            "inventory": inventory,
            "hunter_level": 50,
            "skilling_current_levels": {"hunter": 50},
        }
        dose_two, result = apply_consumable_pure(
            player_data,
            "Juju hunter potion (3)",
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(result["boosts"], {})
        self.assertEqual(
            result["message"],
            "You decide that only plants are likely to enjoy the taste of this potion.",
        )
        self.assertEqual(dose_two["skilling_current_levels"], {"hunter": 50})
        self.assertEqual(dose_two["inventory"]["Juju hunter potion (2)"], 1)
        self.assertNotIn("Juju hunter potion (3)", dose_two["inventory"])
        self.assertEqual(player_data["inventory"]["Juju hunter potion (3)"], 1)

    def test_action_telemetry_records_expected_observed_and_outputs(self):
        player_data = {}

        record_action_telemetry_pure(
            player_data,
            "fishing",
            "catch_mackerel_cod_bass",
            False,
            expected_success_chance=0.4,
            failure_kind="dry",
        )
        record_action_telemetry_pure(
            player_data,
            "fishing",
            "catch_mackerel_cod_bass",
            True,
            expected_success_chance=0.4,
            output_item="Raw mackerel",
        )

        key = action_telemetry_key_pure("fishing", "catch_mackerel_cod_bass")
        record = player_data["action_telemetry"]["actions"][key]
        self.assertEqual(record["attempts"], 2)
        self.assertEqual(record["successes"], 1)
        self.assertEqual(record["failures"], 1)
        self.assertAlmostEqual(record["expected_successes"], 0.8)
        self.assertEqual(record["current_dry_streak"], 0)
        self.assertEqual(record["longest_dry_streak"], 1)
        self.assertEqual(record["outputs"], {"Raw mackerel": 1})
        self.assertEqual(record["failure_kinds"], {"dry": 1})

        summary = summarize_action_telemetry_pure(player_data)[0]
        self.assertEqual(summary["key"], key)
        self.assertAlmostEqual(summary["observed_success_rate"], 0.5)
        self.assertAlmostEqual(summary["expected_success_rate"], 0.4)

    def test_review_success_normalization_is_shared_for_source_odds(self):
        mining_target = ORE_DATA["coal"]
        rune_pickaxe = MINING_PICKAXE_DATA["rune_pickaxe"]
        woodcutting_target = TREE_DATA["willow"]
        rune_hatchet = WOODCUTTING_AXE_DATA["rune_hatchet"]
        crayfish = FISHING_DATA["catch_crayfish"]["fish"][0]
        kebbit = HUNTER_DATA["catch_wild_kebbit"]
        shrimps = COOKING_DATA["cook_shrimps"]

        self.assertAlmostEqual(
            calculate_mining_success_probability_pure(60, mining_target, rune_pickaxe),
            normalize_review_success_probability_pure(mining_source_roll_chance_pure(60, mining_target, rune_pickaxe)),
        )
        self.assertAlmostEqual(
            calculate_woodcutting_success_probability_pure(60, woodcutting_target, rune_hatchet),
            normalize_review_success_probability_pure(woodcutting_source_roll_chance_pure(60, woodcutting_target, rune_hatchet)),
        )
        self.assertAlmostEqual(
            calculate_fishing_success_probability_pure(1, crayfish),
            normalize_review_success_probability_pure(fishing_source_roll_chance_pure(1, crayfish)),
        )
        self.assertAlmostEqual(
            calculate_hunter_success_probability_pure(23, kebbit),
            normalize_review_success_probability_pure(hunter_source_roll_chance_pure(23, kebbit)),
        )
        self.assertAlmostEqual(
            calculate_cooking_success_probability_pure(1, shrimps),
            normalize_review_success_probability_pure(cooking_source_roll_chance_pure(1, shrimps)),
        )

    def test_firemaking_source_chance_and_tier_curve(self):
        logs = FIREMAKING_DATA["logs"]
        magic = FIREMAKING_DATA["magic_logs"]

        # 3-arg source interpolate adds +1 inside the helper: 66/255 at level 1.
        self.assertAlmostEqual(firemaking_source_roll_chance_pure(1, logs), 66 / 255)
        self.assertEqual(firemaking_source_roll_chance_pure(99, logs), 1.0)
        self.assertLess(
            firemaking_source_roll_chance_pure(40, {"low_chance": 40, "high_chance": 200}),
            firemaking_source_roll_chance_pure(40, {"low_chance": 80, "high_chance": 300}),
        )

        logs_at_unlock = calculate_firemaking_success_probability_pure(1, logs)
        logs_overleveled = calculate_firemaking_success_probability_pure(45, logs)
        magic_at_unlock = calculate_firemaking_success_probability_pure(75, magic)
        magic_overleveled = calculate_firemaking_success_probability_pure(99, magic)

        self.assertGreaterEqual(logs_at_unlock, 0.40)
        self.assertLessEqual(logs_at_unlock, 0.50)
        self.assertGreater(logs_overleveled, logs_at_unlock)
        self.assertGreater(logs_overleveled, magic_at_unlock)
        self.assertGreater(magic_overleveled, magic_at_unlock)
        self.assertLessEqual(magic_overleveled, 0.95)

    def test_firemaking_gating_and_action_application(self):
        self.assertTrue(can_burn_firemaking_target_pure(1, {"Logs": 1}, "logs", FIREMAKING_DATA))
        self.assertFalse(can_burn_firemaking_target_pure(1, {}, "logs", FIREMAKING_DATA))
        self.assertFalse(can_burn_firemaking_target_pure(14, {"Oak logs": 1}, "oak_logs", FIREMAKING_DATA))
        self.assertTrue(can_burn_any_firemaking_target_pure({"Logs": 1}, 1, FIREMAKING_DATA))
        self.assertFalse(can_burn_any_firemaking_target_pure({"Oak logs": 1}, 1, FIREMAKING_DATA))

        inv = {"Logs": 2, "Ashes": 4}
        new_inv, exp, ok, output_item = apply_firemaking_action_pure(
            "logs",
            inv,
            FIREMAKING_DATA,
            1,
            r_action=0.0,
        )
        self.assertTrue(ok)
        self.assertAlmostEqual(exp, 40.0)
        self.assertEqual(output_item, "Ashes")
        self.assertEqual(new_inv["Logs"], 1)
        self.assertEqual(new_inv["Ashes"], 5)
        self.assertEqual(inv["Logs"], 2)

        failed_inv, failed_exp, failed_ok, failed_output = apply_firemaking_action_pure(
            "logs",
            inv,
            FIREMAKING_DATA,
            1,
            r_action=1.0,
        )
        self.assertFalse(failed_ok)
        self.assertEqual(failed_exp, 0)
        self.assertIsNone(failed_output)
        self.assertEqual(failed_inv, inv)

    def test_fishing_source_odds_and_scaled_probability(self):
        crayfish = FISHING_DATA["catch_crayfish"]["fish"][0]
        shark = FISHING_DATA["catch_sharks"]["fish"][0]

        # Fish.kt roll cap 255, success on <=: probability (interp + 1)/255.
        self.assertAlmostEqual(fishing_source_roll_chance_pure(1, crayfish), 59 / 255)
        self.assertEqual(fishing_source_roll_chance_pure(99, crayfish), 1.0)
        self.assertLess(
            fishing_source_roll_chance_pure(76, shark),
            fishing_source_roll_chance_pure(99, shark),
        )

        scaled = calculate_fishing_success_probability_pure(1, crayfish)
        self.assertGreater(scaled, fishing_source_roll_chance_pure(1, crayfish))
        self.assertLessEqual(calculate_fishing_success_probability_pure(99, crayfish), 0.95)
        mackerel = FISHING_DATA["catch_mackerel_cod_bass"]["fish"][0]
        self.assertGreater(calculate_fishing_success_probability_pure(18, mackerel), 0.35)

    def test_fishing_ordered_rolls_and_bait_consumed_only_on_catch(self):
        inv = {"Fishing bait": 1}

        dry_inv, dry_exp, dry_ok, dry_output, dry_rewards = apply_fishing_action_pure(
            "catch_sardine_herring",
            inv,
            FISHING_DATA,
            fishing_level=10,
            rolls=(1.0, 1.0),
        )
        self.assertFalse(dry_ok)
        self.assertEqual(dry_exp, 0)
        self.assertIsNone(dry_output)
        self.assertEqual(dry_rewards, ())
        self.assertEqual(dry_inv["Fishing bait"], 1)

        catch_inv, catch_exp, catch_ok, catch_output, rewards = apply_fishing_action_pure(
            "catch_sardine_herring",
            inv,
            FISHING_DATA,
            fishing_level=10,
            rolls=(0.0, 0.0),
        )
        self.assertTrue(catch_ok)
        self.assertEqual(catch_output, "Raw sardine")
        self.assertAlmostEqual(catch_exp, 20.0)
        self.assertEqual(rewards, ({"skill_id": "fishing", "amount": 20.0},))
        self.assertEqual(catch_inv["Fishing bait"], 0)
        self.assertEqual(catch_inv["Raw sardine"], 1)
        self.assertEqual(inv["Fishing bait"], 1)

    def test_cave_eel_uses_level_38_rod_and_bait_target(self):
        self.assertFalse(
            can_fish_method_pure(
                37, {"Fishing bait": 1}, "catch_cave_eel", FISHING_DATA
            )
        )
        caught, xp, ok, output, rewards = apply_fishing_action_pure(
            "catch_cave_eel",
            {"Fishing bait": 1},
            FISHING_DATA,
            fishing_level=38,
            rolls=(0.0,),
        )
        self.assertTrue(ok)
        self.assertEqual(output, "Raw cave eel")
        self.assertEqual(xp, 80.0)
        self.assertEqual(rewards, ({"skill_id": "fishing", "amount": 80.0},))
        self.assertEqual(caught, {"Fishing bait": 0, "Raw cave eel": 1})

    def test_fishing_mixed_outputs_respect_source_order_after_level_filter(self):
        low_level_fish = eligible_fishing_fish_pure(
            FISHING_DATA["catch_shrimp_anchovies"],
            fishing_level=1,
        )
        self.assertEqual([fish["output_item"] for fish in low_level_fish], ["Raw shrimps"])

        inv, exp, ok, output_item, _rewards = apply_fishing_action_pure(
            "catch_shrimp_anchovies",
            {},
            FISHING_DATA,
            fishing_level=15,
            rolls=(1.0, 0.0),
        )
        self.assertTrue(ok)
        self.assertEqual(output_item, "Raw shrimps")
        self.assertAlmostEqual(exp, 10.0)
        self.assertEqual(inv["Raw shrimps"], 1)

        inv2, exp2, ok2, output_item2, _rewards2 = apply_fishing_action_pure(
            "catch_shrimp_anchovies",
            {},
            FISHING_DATA,
            fishing_level=15,
            rolls=(0.0, 0.0),
        )
        self.assertTrue(ok2)
        self.assertEqual(output_item2, "Raw anchovies")
        self.assertAlmostEqual(exp2, 40.0)
        self.assertEqual(inv2["Raw anchovies"], 1)

    def test_fishing_side_level_gates_and_hidden_side_xp_rewards(self):
        self.assertFalse(can_fish_method_pure(48, {"Feather": 1}, "catch_leaping_fish", FISHING_DATA, 14, 15))
        self.assertFalse(can_fish_method_pure(48, {"Feather": 1}, "catch_leaping_fish", FISHING_DATA, 15, 14))
        self.assertTrue(can_fish_method_pure(48, {"Feather": 1}, "catch_leaping_fish", FISHING_DATA, 15, 15))

        inv, exp, ok, output_item, rewards = apply_fishing_action_pure(
            "catch_leaping_fish",
            {"Feather": 1},
            FISHING_DATA,
            fishing_level=48,
            strength_level=15,
            agility_level=15,
            rolls=(0.0,),
        )
        self.assertTrue(ok)
        self.assertEqual(output_item, "Leaping trout")
        self.assertAlmostEqual(exp, 50.0)
        self.assertEqual(
            rewards,
            (
                {"skill_id": "fishing", "amount": 50.0},
                {"skill_id": "strength", "amount": 5.0},
                {"skill_id": "agility", "amount": 5.0},
            ),
        )
        self.assertEqual(inv["Feather"], 0)

    def test_xp_rewards_normalization_combines_duplicate_skills_and_falls_back(self):
        rewards = normalize_xp_rewards_pure(
            {
                "xp_rewards": (
                    {"skill_id": "fishing", "amount": 10},
                    {"skill_id": "fishing", "amount": 2.5},
                    ("agility", 3),
                    {"skill_id": "", "amount": 99},
                )
            }
        )
        self.assertEqual(
            rewards,
            (
                {"skill_id": "fishing", "amount": 12.5},
                {"skill_id": "agility", "amount": 3.0},
            ),
        )
        self.assertEqual(
            normalize_xp_rewards_pure({}, "fletching", 5),
            ({"skill_id": "fletching", "amount": 5.0},),
        )

    def test_fishing_material_gates(self):
        # Fishing bait itself now comes from live NPC shop stock (the
        # gather_fishing_bait bridge was retired), so only the gates remain.
        self.assertTrue(has_fishing_bait_pure({"Fishing bait": 1}, FISHING_DATA["catch_sardine_herring"]))
        self.assertFalse(has_fishing_bait_pure({}, FISHING_DATA["catch_sardine_herring"]))
        self.assertTrue(has_fishing_bait_pure({"Caviar": 1}, FISHING_DATA["catch_leaping_fish"]))
        self.assertFalse(can_fish_method_pure(5, {}, "catch_sardine_herring", FISHING_DATA))

    def test_utility_activity_supports_one_shot_multi_output_purchase(self):
        # The buy_hunter_supplies bridge is retired, but the one-shot
        # multi-output machinery it exercised stays supported for future
        # activities; cover it with a synthetic spec.
        activity_data = {
            "one_shot_bundle": {
                "display_name": "One-shot bundle",
                "requirements": {"Coins": 500},
                "outputs": {"Bird snare": 1, "Impling jar": 10},
                "batch_size": 1,
                "deactivate_after_run": True,
                "group": "shopping",
                "source": "test fixture",
            },
        }
        inv, exp, ok, processed = apply_utility_activity_pure(
            "one_shot_bundle",
            {"Coins": 500},
            activity_data,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(processed, 1)
        self.assertEqual(inv["Coins"], 0)
        self.assertEqual(inv["Bird snare"], 1)
        self.assertEqual(inv["Impling jar"], 10)

    def test_hunter_reusable_tools_gate_targets_without_being_consumed(self):
        self.assertEqual(
            hunter_target_locked_reasons_pure(
                {"hunter_level": 1, "inventory": {}},
                "catch_crimson_swift",
                HUNTER_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Bird snare",),
        )

        inv, exp, ok, _output_item, _rewards = apply_hunter_action_pure(
            "catch_crimson_swift",
            {"Bird snare": 1},
            HUNTER_DATA,
            1,
            0.0,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 34.0)
        self.assertEqual(inv["Bird snare"], 1)
        self.assertEqual(inv["Red feather"], 5)

        butterfly_inv, _exp, butterfly_ok, _output_item, _rewards = apply_hunter_action_pure(
            "catch_ruby_harvest",
            {"Butterfly net": 1, "Butterfly jar": 1},
            HUNTER_DATA,
            15,
            0.0,
        )
        self.assertTrue(butterfly_ok)
        self.assertEqual(butterfly_inv["Butterfly net"], 1)
        self.assertEqual(butterfly_inv["Butterfly jar"], 0)

    def test_common_jadinko_opens_all_five_vine_herb_seeds_at_level_70(self):
        target = "catch_common_jadinko"
        spec = HUNTER_DATA[target]
        self.assertEqual(spec["level"], 70)
        self.assertEqual(spec["exp"], 350.0)
        self.assertEqual(spec["source_npc_id"], 13119)
        self.assertEqual(
            tuple(table["chance"] for table in spec["secondary_drop_tables"]),
            (14 / 256, 16 / 256, 17 / 256),
        )

        seed_rolls = (
            (0.0, "Erzille seed"),
            (0.2, "Ugune seed"),
            (0.4, "Argway seed"),
            (0.6, "Shengo seed"),
            (0.8, "Samaden seed"),
        )
        for pick_roll, expected_seed in seed_rolls:
            with self.subTest(seed=expected_seed):
                inventory, exp, ok, output_item, _rewards = apply_hunter_action_pure(
                    target,
                    {"Marasamaw plant": 1},
                    HUNTER_DATA,
                    70,
                    0.0,
                    r_secondary_rolls=(
                        (1.0, 0.0),
                        (0.0, pick_roll),
                        (1.0, 0.0),
                    ),
                )
                self.assertTrue(ok)
                self.assertEqual(exp, 350.0)
                self.assertEqual(output_item, "Withered vine")
                self.assertEqual(inventory["Marasamaw plant"], 1)
                self.assertEqual(inventory["Withered vine"], 1)
                self.assertEqual(inventory[expected_seed], 1)

        no_seed, _exp, ok, _output_item, _rewards = apply_hunter_action_pure(
            target,
            {"Marasamaw plant": 1},
            HUNTER_DATA,
            70,
            0.0,
            r_secondary_rolls=(
                (1.0, 0.0),
                (16 / 256, 0.0),
                (1.0, 0.0),
            ),
        )
        self.assertTrue(ok)
        self.assertNotIn("Erzille seed", no_seed)

    def test_all_jadinko_live_secondary_tables_match_darkan(self):
        vine_herb_seeds = (
            "Erzille seed",
            "Ugune seed",
            "Argway seed",
            "Shengo seed",
            "Samaden seed",
        )
        bush_seeds = ("Lergberry seed", "Kalferberry seed")
        blossom_seeds = (
            "Red blossom seed",
            "Blue blossom seed",
            "Green blossom seed",
        )
        higher_vine_herb_seeds = vine_herb_seeds[1:]
        expected = {
            "track_shadow_jadinko": (
                (8 / 256, bush_seeds),
                (5 / 256, higher_vine_herb_seeds),
                (4 / 256, blossom_seeds),
            ),
            "track_diseased_jadinko": (
                (8 / 256, bush_seeds),
                (5 / 256, higher_vine_herb_seeds),
                (4 / 256, blossom_seeds),
            ),
            "track_camouflaged_jadinko": (
                (16 / 256, bush_seeds),
                (4 / 256, higher_vine_herb_seeds),
                (4 / 256, blossom_seeds),
            ),
            "catch_common_jadinko": (
                (14 / 256, bush_seeds),
                (16 / 256, vine_herb_seeds),
                (17 / 256, blossom_seeds),
            ),
            "catch_igneous_jadinko": ((13 / 256, bush_seeds),),
            "catch_cannibal_jadinko": ((12 / 256, bush_seeds),),
            "catch_aquatic_jadinko": ((12 / 256, blossom_seeds),),
            "catch_amphibious_jadinko": (
                (
                    20 / 256,
                    ("Apple tree seed", "Banana tree seed", "Orange tree seed"),
                ),
            ),
            "catch_carrion_jadinko": ((30 / 256, vine_herb_seeds),),
            "catch_draconic_jadinko": ((14 / 256, higher_vine_herb_seeds),),
            "catch_guthix_jadinko": (
                (6 / 256, bush_seeds),
                (5 / 256, higher_vine_herb_seeds),
                (4 / 256, blossom_seeds),
            ),
            "catch_saradomin_jadinko": (
                (6 / 256, bush_seeds),
                (5 / 256, higher_vine_herb_seeds),
                (4 / 256, blossom_seeds),
            ),
            "catch_zamorak_jadinko": (
                (6 / 256, bush_seeds),
                (5 / 256, higher_vine_herb_seeds),
                (4 / 256, blossom_seeds),
            ),
        }
        actual = {
            target
            for target in HUNTER_DATA
            if target.endswith("_jadinko")
            and (target.startswith("catch_") or target.startswith("track_"))
        }
        self.assertEqual(actual, set(expected))
        for target, expected_tables in expected.items():
            with self.subTest(target=target):
                actual_tables = tuple(
                    (
                        table["chance"],
                        tuple(row["item"] for row in table["outputs"]),
                    )
                    for table in HUNTER_DATA[target]["secondary_drop_tables"]
                )
                self.assertEqual(actual_tables, expected_tables)

    def test_all_jadinko_secondary_tables_run_independently_through_real_kernel(self):
        cases = {
            "track_shadow_jadinko": (
                "Shadow vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
            ),
            "track_diseased_jadinko": (
                "Corrupt vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
            ),
            "track_camouflaged_jadinko": (
                "Striped vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
            ),
            "catch_common_jadinko": (
                "Withered vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
            ),
            "catch_igneous_jadinko": ("Marble vine", ("Kalferberry seed",)),
            "catch_cannibal_jadinko": ("Plant teeth", ("Kalferberry seed",)),
            "catch_aquatic_jadinko": ("Aquatic vine", ("Green blossom seed",)),
            "catch_amphibious_jadinko": ("Oily vine", ("Orange tree seed",)),
            "catch_carrion_jadinko": ("Pungent vine", ("Samaden seed",)),
            "catch_draconic_jadinko": ("Draconic vine", ("Samaden seed",)),
            "catch_guthix_jadinko": (
                "Guthix vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
            ),
            "catch_saradomin_jadinko": (
                "Saradomin vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
            ),
            "catch_zamorak_jadinko": (
                "Zamorak vine",
                ("Kalferberry seed", "Samaden seed", "Green blossom seed"),
            ),
        }
        for target, (primary, secondaries) in cases.items():
            with self.subTest(target=target):
                spec = HUNTER_DATA[target]
                tables = spec["secondary_drop_tables"]
                inventory, _xp, ok, output_item, _rewards = apply_hunter_action_pure(
                    target,
                    spec["tools"],
                    HUNTER_DATA,
                    spec["level"],
                    0.0,
                    r_secondary_rolls=((0.0, 0.999999),) * len(tables),
                )
                self.assertTrue(ok)
                self.assertEqual(output_item, primary)
                self.assertEqual(inventory[primary], 1)
                self.assertEqual(
                    tuple(inventory.get(item, 0) for item in secondaries),
                    (1,) * len(secondaries),
                )
                for tool, amount in spec["tools"].items():
                    self.assertEqual(inventory[tool], amount)

    def test_all_catch_jadinkos_share_the_marasamaw_group(self):
        expected = {
            "catch_common_jadinko",
            "catch_igneous_jadinko",
            "catch_cannibal_jadinko",
            "catch_aquatic_jadinko",
            "catch_amphibious_jadinko",
            "catch_carrion_jadinko",
            "catch_draconic_jadinko",
            "catch_guthix_jadinko",
            "catch_saradomin_jadinko",
            "catch_zamorak_jadinko",
        }
        actual = {
            target
            for target, spec in HUNTER_DATA.items()
            if target.startswith("catch_")
            and target.endswith("_jadinko")
            and spec["group"] == "marasamaw_trapping"
        }
        self.assertEqual(actual, expected)
        for target in expected:
            self.assertEqual(HUNTER_DATA[target]["tools"], {"Marasamaw plant": 1})

    def test_polar_kebbit_tracking_preserves_noose_wand_and_awards_sourced_outputs(self):
        target = "catch_polar_kebbit"
        self.assertEqual(
            hunter_source_roll_chance_pure(1, HUNTER_DATA[target]),
            130 / 255,
        )
        self.assertEqual(
            hunter_target_locked_reasons_pure(
                {"hunter_level": 1, "inventory": {}},
                target,
                HUNTER_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Noose wand",),
        )

        inventory, exp, ok, output_item, _rewards = apply_hunter_action_pure(
            target,
            {"Noose wand": 1},
            HUNTER_DATA,
            1,
            0.0,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 30.0)
        self.assertEqual(output_item, "Polar kebbit fur")
        self.assertEqual(
            inventory,
            {
                "Noose wand": 1,
                "Bones": 1,
                "Raw beast meat": 1,
                "Polar kebbit fur": 1,
            },
        )

    def test_common_jadinko_preserves_trap_and_rolls_each_vine_herb_seed(self):
        target = "catch_common_jadinko"
        seeds = (
            "Erzille seed",
            "Ugune seed",
            "Argway seed",
            "Shengo seed",
            "Samaden seed",
        )
        self.assertEqual(
            hunter_target_locked_reasons_pure(
                {"hunter_level": 70, "inventory": {}},
                target,
                HUNTER_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Marasamaw plant",),
        )

        no_seed_inventory, exp, ok, output_item, _rewards = apply_hunter_action_pure(
            target,
            {"Marasamaw plant": 1},
            HUNTER_DATA,
            70,
            0.0,
            r_secondary_rolls=(
                (1.0, 0.0),
                (16 / 256, 0.0),
                (1.0, 0.0),
            ),
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 350.0)
        self.assertEqual(output_item, "Withered vine")
        self.assertEqual(no_seed_inventory["Marasamaw plant"], 1)
        self.assertEqual(no_seed_inventory["Withered vine"], 1)
        self.assertTrue(all(seed not in no_seed_inventory for seed in seeds))

        for index, expected_seed in enumerate(seeds):
            with self.subTest(seed=expected_seed):
                inventory, _exp, caught, _output_item, _rewards = apply_hunter_action_pure(
                    target,
                    {"Marasamaw plant": 1},
                    HUNTER_DATA,
                    70,
                    0.0,
                    r_secondary_rolls=(
                        (1.0, 0.0),
                        (0.0, (index + 0.1) / len(seeds)),
                        (1.0, 0.0),
                    ),
                )
                self.assertTrue(caught)
                self.assertEqual(inventory[expected_seed], 1)
                self.assertEqual(
                    {seed for seed in seeds if inventory.get(seed, 0)},
                    {expected_seed},
                )

    def test_razor_backed_kebbit_tracking_preserves_noose_wand_and_awards_chain_inputs(self):
        target = "track_razor_backed_kebbit"
        self.assertEqual(
            hunter_source_roll_chance_pure(49, HUNTER_DATA[target]),
            192 / 255,
        )
        self.assertEqual(
            hunter_target_locked_reasons_pure(
                {"hunter_level": 49, "inventory": {}},
                target,
                HUNTER_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Noose wand",),
        )

        inventory, exp, ok, output_item, _rewards = apply_hunter_action_pure(
            target,
            {"Noose wand": 1},
            HUNTER_DATA,
            49,
            0.0,
        )

        self.assertTrue(ok)
        self.assertEqual(exp, 348.0)
        self.assertEqual(output_item, "Long kebbit spike")
        self.assertEqual(
            inventory,
            {
                "Noose wand": 1,
                "Bones": 1,
                "Raw beast meat": 1,
                "Long kebbit spike": 1,
            },
        )

    def test_camouflaged_jadinko_tracker_is_reachable_and_rolls_independent_tables(self):
        target = "track_camouflaged_jadinko"
        self.assertEqual(
            hunter_target_locked_reasons_pure(
                {"hunter_level": 78, "inventory": {"Noose wand": 1}},
                target,
                HUNTER_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Hunter level 79",),
        )
        self.assertEqual(
            hunter_target_locked_reasons_pure(
                {"hunter_level": 79, "inventory": {"Noose wand": 1}},
                target,
                HUNTER_DATA,
                QUEST_UNLOCK_RULES,
            ),
            (),
        )

        spec = HUNTER_DATA[target]
        inventory, xp, ok, output_item, _rewards = apply_hunter_action_pure(
            target,
            {"Noose wand": 1},
            HUNTER_DATA,
            79,
            0.0,
            r_secondary_rolls=((0.0, 0.999999),) * 3,
        )
        self.assertTrue(ok)
        self.assertEqual(xp, 600.0)
        self.assertEqual(output_item, "Striped vine")
        self.assertEqual(spec["source_item_id"], 19978)
        self.assertEqual(
            inventory,
            {
                "Noose wand": 1,
                "Striped vine": 1,
                "Kalferberry seed": 1,
                "Samaden seed": 1,
                "Green blossom seed": 1,
            },
        )

    def test_jadinko_secondaries_use_reusable_tools_and_fixed_primary_outputs(self):
        cases = {
            "track_shadow_jadinko": (71, 475.0, "Noose wand", "Shadow vine"),
            "track_diseased_jadinko": (78, 580.5, "Noose wand", "Corrupt vine"),
            "catch_cannibal_jadinko": (75, 475.0, "Marasamaw plant", "Plant teeth"),
            "catch_guthix_jadinko": (81, 600.0, "Marasamaw plant", "Guthix vine"),
        }
        for target, (level, expected_xp, tool, output) in cases.items():
            with self.subTest(target=target):
                self.assertEqual(hunter_target_locked_reasons_pure({"hunter_level": level, "inventory": {}}, target, HUNTER_DATA, QUEST_UNLOCK_RULES), (tool,))
                inventory, xp, ok, output_item, _rewards = apply_hunter_action_pure(target, {tool: 1}, HUNTER_DATA, level, 0.0)
                self.assertTrue(ok)
                self.assertEqual(xp, expected_xp)
                self.assertEqual(output_item, output)
                self.assertEqual(inventory, {tool: 1, output: 1})

    def test_cannibal_jadinko_bush_seed_table_preserves_primary_output(self):
        target = "catch_cannibal_jadinko"
        tool = {"Marasamaw plant": 1}

        missed, _xp, ok, _output, _rewards = apply_hunter_action_pure(
            target,
            tool,
            HUNTER_DATA,
            75,
            0.0,
            r_secondary_rolls=((
                HUNTER_DATA[target]["secondary_drop_tables"][0]["chance"],
                0.0,
            ),),
        )
        self.assertTrue(ok)
        self.assertEqual(missed, {"Marasamaw plant": 1, "Plant teeth": 1})

        failed, _xp, ok, _output, _rewards = apply_hunter_action_pure(
            target,
            tool,
            HUNTER_DATA,
            75,
            1.0,
            r_secondary_rolls=((0.0, 0.5),),
        )
        self.assertFalse(ok)
        self.assertEqual(failed, tool)

        lergberry, _xp, ok, _output, _rewards = apply_hunter_action_pure(
            target,
            tool,
            HUNTER_DATA,
            75,
            0.0,
            r_secondary_rolls=((0.0, 0.0),),
        )
        self.assertTrue(ok)
        self.assertEqual(
            lergberry,
            {"Marasamaw plant": 1, "Plant teeth": 1, "Lergberry seed": 1},
        )

        kalferberry, _xp, ok, _output, _rewards = apply_hunter_action_pure(
            target,
            tool,
            HUNTER_DATA,
            75,
            0.0,
            r_secondary_rolls=((0.0, 0.5),),
        )
        self.assertTrue(ok)
        self.assertEqual(
            kalferberry,
            {"Marasamaw plant": 1, "Plant teeth": 1, "Kalferberry seed": 1},
        )

    def test_cooking_source_odds_and_scaled_probability(self):
        shrimps = COOKING_DATA["cook_shrimps"]
        shark = COOKING_DATA["cook_shark"]

        # 3-arg source interpolate adds +1 inside the helper: 129/255 at level 1.
        self.assertAlmostEqual(cooking_source_roll_chance_pure(1, shrimps), 129 / 255)
        self.assertEqual(cooking_source_roll_chance_pure(99, shrimps), 1.0)
        self.assertLess(
            cooking_source_roll_chance_pure(80, shark),
            cooking_source_roll_chance_pure(99, shark),
        )

        scaled = calculate_cooking_success_probability_pure(1, shrimps)
        self.assertGreater(scaled, cooking_source_roll_chance_pure(1, shrimps))
        self.assertLessEqual(calculate_cooking_success_probability_pure(99, shrimps), 0.98)

    def test_cooking_success_and_burn_consume_raw_item(self):
        self.assertTrue(can_cook_target_pure(1, {"Raw beef": 2}, "render_beef_sinew", COOKING_DATA))
        self.assertFalse(can_cook_target_pure(1, {}, "render_beef_sinew", COOKING_DATA))
        self.assertFalse(can_cook_target_pure(79, {"Raw shark": 1}, "cook_shark", COOKING_DATA))

        cooked_inv, cooked_exp, cooked_ok, cooked_output, cooked_burned = apply_cooking_action_pure(
            "render_beef_sinew",
            {"Raw beef": 2},
            COOKING_DATA,
            cooking_level=1,
            roll=0.0,
        )
        self.assertTrue(cooked_ok)
        self.assertFalse(cooked_burned)
        self.assertEqual(cooked_output, "Sinew")
        self.assertAlmostEqual(cooked_exp, 30.0)
        self.assertEqual(cooked_inv["Raw beef"], 1)
        self.assertEqual(cooked_inv["Sinew"], 1)

        burnt_inv, burnt_exp, burnt_ok, burnt_output, burnt_burned = apply_cooking_action_pure(
            "cook_shrimps",
            {"Raw shrimps": 1},
            COOKING_DATA,
            cooking_level=1,
            roll=1.0,
        )
        self.assertTrue(burnt_ok)
        self.assertTrue(burnt_burned)
        self.assertEqual(burnt_exp, 0)
        self.assertEqual(burnt_output, "Burnt shrimp")
        self.assertEqual(burnt_inv["Raw shrimps"], 0)
        self.assertEqual(burnt_inv["Burnt shrimp"], 1)

        lava_inv, lava_exp, lava_ok, lava_output, lava_burned = apply_cooking_action_pure(
            "cook_lava_eel",
            {"Raw lava eel": 1},
            COOKING_DATA,
            cooking_level=53,
            roll=1.0,
        )
        self.assertTrue(lava_ok)
        self.assertFalse(lava_burned)
        self.assertEqual(lava_output, "Lava eel")
        self.assertEqual(lava_exp, 30.0)
        self.assertEqual(lava_inv, {"Raw lava eel": 0, "Lava eel": 1})
        self.assertEqual(calculate_cooking_success_probability_pure(53, COOKING_DATA["cook_lava_eel"]), 1.0)

    def test_tiger_shark_cooking_uses_the_exact_level_xp_and_item_chain(self):
        self.assertFalse(
            can_cook_target_pure(
                94,
                {"Raw tiger shark": 1},
                "cook_tiger_shark",
                COOKING_DATA,
            )
        )
        cooked, xp, processed, output, burned = apply_cooking_action_pure(
            "cook_tiger_shark",
            {"Raw tiger shark": 1},
            COOKING_DATA,
            cooking_level=95,
            roll=0.0,
        )
        self.assertTrue(processed)
        self.assertFalse(burned)
        self.assertEqual(output, "Tiger shark")
        self.assertEqual(xp, 230.0)
        self.assertEqual(cooked, {"Raw tiger shark": 0, "Tiger shark": 1})

        burnt, xp, processed, output, burned = apply_cooking_action_pure(
            "cook_tiger_shark",
            {"Raw tiger shark": 1},
            COOKING_DATA,
            cooking_level=99,
            roll=1.0,
        )
        self.assertTrue(processed)
        self.assertTrue(burned)
        self.assertEqual(output, "Burnt tiger shark")
        self.assertEqual(xp, 0)
        self.assertEqual(burnt, {"Raw tiger shark": 0, "Burnt tiger shark": 1})

    def test_wine_resolves_success_or_bad_wine_without_a_timer(self):
        spec = COOKING_DATA["make_wine"]
        self.assertEqual(cooking_source_roll_chance_pure(35, spec), 0.6)
        self.assertEqual(cooking_source_roll_chance_pure(68, spec), 1.0)

        ingredients = {"Grapes": 1, "Jug of water": 1}
        wine, xp, processed, output, failed = apply_cooking_action_pure(
            "make_wine",
            ingredients,
            COOKING_DATA,
            cooking_level=35,
            roll=0.59,
        )
        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output, "Jug of wine")
        self.assertEqual(xp, 200.0)
        self.assertEqual(wine, {"Grapes": 0, "Jug of water": 0, "Jug of wine": 1})

        bad, xp, processed, output, failed = apply_cooking_action_pure(
            "make_wine",
            ingredients,
            COOKING_DATA,
            cooking_level=35,
            roll=0.61,
        )
        self.assertTrue(processed)
        self.assertTrue(failed)
        self.assertEqual(output, "Jug of bad wine")
        self.assertEqual(xp, 0.0)
        self.assertEqual(
            bad,
            {"Grapes": 0, "Jug of water": 0, "Jug of bad wine": 1},
        )

    def test_malting_barley_is_a_no_xp_range_conversion(self):
        malted, xp, processed, output, failed = apply_cooking_action_pure(
            "malt_barley",
            {"Barley": 1},
            COOKING_DATA,
            cooking_level=1,
            roll=1.0,
        )

        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output, "Barley malt")
        self.assertEqual(xp, 0.0)
        self.assertEqual(malted, {"Barley": 0, "Barley malt": 1})

    def test_karambwan_methods_keep_three_distinct_period_outcomes(self):
        poison_spec = COOKING_DATA["cook_poison_karambwan"]
        self.assertEqual(cooking_source_roll_chance_pure(1, poison_spec), 0.5)
        self.assertEqual(cooking_source_roll_chance_pure(20, poison_spec), 1.0)

        burnt, xp, processed, output, failed = apply_cooking_action_pure(
            "cook_poison_karambwan",
            {"Raw karambwan": 1},
            COOKING_DATA,
            cooking_level=1,
            roll=1.0,
        )
        self.assertTrue(processed)
        self.assertTrue(failed)
        self.assertEqual(output, "Burnt karambwan")
        self.assertEqual(xp, 0)
        self.assertEqual(burnt, {"Raw karambwan": 0, "Burnt karambwan": 1})

        cooked, xp, processed, output, failed = apply_cooking_action_pure(
            "cook_karambwan_thoroughly",
            {"Raw karambwan": 1},
            COOKING_DATA,
            cooking_level=30,
            roll=1.0,
        )
        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output, "Cooked karambwan")
        self.assertEqual(xp, 190.0)
        self.assertEqual(cooked, {"Raw karambwan": 0, "Cooked karambwan": 1})

        tiny, xp, processed, output, failed = apply_cooking_action_pure(
            "cook_karambwanji",
            {"Raw karambwanji": 1},
            COOKING_DATA,
            cooking_level=1,
            roll=0.0,
        )
        self.assertTrue(processed)
        self.assertFalse(failed)
        self.assertEqual(output, "Karambwanji")
        self.assertEqual(xp, 10.0)
        self.assertEqual(tiny, {"Raw karambwanji": 0, "Karambwanji": 1})

    def test_dwarven_stout_maturity_preserves_the_full_vat_on_both_outcomes(self):
        ingredients = {
            "Ale yeast": 1,
            "Bucket of water": 2,
            "Barley malt": 2,
            "Hammerstone hops": 4,
            "Beer glass": 8,
            "The stuff": 1,
        }
        original = dict(ingredients)
        mature, xp, processed, output, burned = apply_cooking_action_pure(
            "brew_dwarven_stout_with_the_stuff",
            ingredients,
            COOKING_DATA,
            cooking_level=19,
            roll=0.50,
        )
        self.assertEqual(ingredients, original)
        self.assertTrue(processed)
        self.assertFalse(burned)
        self.assertEqual(output, "Dwarven stout (m)")
        self.assertEqual(xp, 215.0)
        self.assertEqual(mature["Dwarven stout (m)"], 8)
        self.assertEqual(mature["Bucket"], 2)
        self.assertEqual(mature["The stuff"], 0)

        ordinary, xp, processed, output, burned = apply_cooking_action_pure(
            "brew_dwarven_stout",
            {key: value for key, value in ingredients.items() if key != "The stuff"},
            COOKING_DATA,
            cooking_level=19,
            roll=0.50,
        )
        self.assertTrue(processed)
        self.assertFalse(burned)
        self.assertEqual(output, "Dwarven stout")
        self.assertEqual(xp, 215.0)
        self.assertEqual(ordinary["Dwarven stout"], 8)
        self.assertEqual(ordinary["Bucket"], 2)

    def test_cooking_runtime_extra_formulas_and_inventory(self):
        trout = COOKING_DATA["gut_leaping_trout"]
        salmon = COOKING_DATA["gut_leaping_salmon"]
        sturgeon = COOKING_DATA["gut_leaping_sturgeon"]

        self.assertTrue(can_cook_target_pure(0, {"Leaping trout": 1}, "gut_leaping_trout", COOKING_DATA))
        self.assertAlmostEqual(cooking_source_roll_chance_pure(1, trout), 1.0 / 150.0)
        self.assertAlmostEqual(cooking_source_roll_chance_pure(99, trout), 66.0 / 150.0)
        self.assertAlmostEqual(cooking_source_roll_chance_pure(1, salmon), 1.25 / 100.0)
        self.assertEqual(cooking_source_roll_chance_pure(80, salmon), 1.0)
        self.assertEqual(cooking_source_roll_chance_pure(80, sturgeon), 1.0)
        self.assertEqual(calculate_cooking_success_probability_pure(1, trout), 1.0 / 150.0)
        self.assertEqual(calculate_cooking_success_probability_pure(1, COOKING_DATA["burn_seaweed"]), 1.0)

        trout_inv, trout_exp, trout_ok, trout_output, trout_failed = apply_cooking_action_pure(
            "gut_leaping_trout",
            {"Leaping trout": 1},
            COOKING_DATA,
            cooking_level=1,
            roll=1.0 / 150.0,
            byproduct_roll=0.5,
        )
        self.assertTrue(trout_ok)
        self.assertFalse(trout_failed)
        self.assertEqual(trout_output, "Roe")
        self.assertEqual(trout_exp, 10.0)
        self.assertEqual(trout_inv, {"Leaping trout": 0, "Roe": 1, "Fish offcuts": 1})

        salmon_inv, _salmon_exp, _salmon_ok, _salmon_output, _salmon_failed = apply_cooking_action_pure(
            "gut_leaping_salmon",
            {"Leaping salmon": 1},
            COOKING_DATA,
            cooking_level=80,
            roll=1.0,
            byproduct_roll=0.75,
        )
        self.assertEqual(salmon_inv, {"Leaping salmon": 0, "Roe": 1, "Fish offcuts": 1})

        sturgeon_inv, sturgeon_exp, _sturgeon_ok, sturgeon_output, _sturgeon_failed = apply_cooking_action_pure(
            "gut_leaping_sturgeon",
            {"Leaping sturgeon": 1},
            COOKING_DATA,
            cooking_level=80,
            roll=1.0,
            byproduct_roll=5.0 / 6.0,
        )
        self.assertEqual(sturgeon_output, "Caviar")
        self.assertEqual(sturgeon_exp, 15.0)
        self.assertEqual(sturgeon_inv, {"Leaping sturgeon": 0, "Caviar": 1, "Fish offcuts": 1})

        failed_inv, failed_exp, failed_ok, failed_output, failed = apply_cooking_action_pure(
            "gut_leaping_trout",
            {"Leaping trout": 1},
            COOKING_DATA,
            cooking_level=1,
            roll=1.0,
        )
        self.assertTrue(failed_ok)
        self.assertTrue(failed)
        self.assertEqual(failed_exp, 0)
        self.assertIsNone(failed_output)
        self.assertEqual(failed_inv, {"Leaping trout": 0})

        seaweed_inv, seaweed_exp, seaweed_ok, seaweed_output, seaweed_failed = apply_cooking_action_pure(
            "burn_seaweed",
            {"Seaweed": 1},
            COOKING_DATA,
            cooking_level=1,
            roll=1.0,
        )
        self.assertTrue(seaweed_ok)
        self.assertFalse(seaweed_failed)
        self.assertEqual(seaweed_output, "Soda ash")
        self.assertEqual(seaweed_exp, 1.0)
        self.assertEqual(seaweed_inv, {"Seaweed": 0, "Soda ash": 1})

    def test_cheese_wheel_churning_and_sample_calibrated_slice_all(self):
        churned, churn_xp, churn_ok, churn_output, churn_failed = apply_cooking_action_pure(
            "churn_milk_cheese_wheel",
            {"Bucket of milk": 1},
            COOKING_DATA,
            cooking_level=48,
            roll=1.0,
        )
        self.assertTrue(churn_ok)
        self.assertFalse(churn_failed)
        self.assertEqual(churn_output, "Cheese wheel")
        self.assertEqual(churn_xp, 40.5)
        self.assertEqual(
            churned,
            {"Bucket of milk": 0, "Cheese wheel": 1, "Bucket": 1},
        )

        minimum, minimum_xp, minimum_ok, output, failed = apply_cooking_action_pure(
            "slice_cheese_wheel",
            {"Cheese wheel": 1},
            COOKING_DATA,
            cooking_level=48,
            roll=0.0,
        )
        self.assertTrue(minimum_ok)
        self.assertFalse(failed)
        self.assertEqual(output, "Cheese")
        self.assertEqual(minimum, {"Cheese wheel": 0, "Cheese": 5})
        self.assertEqual(minimum_xp, 20.0)

        maximum, maximum_xp, *_ = apply_cooking_action_pure(
            "slice_cheese_wheel",
            {"Cheese wheel": 1},
            COOKING_DATA,
            cooking_level=99,
            roll=1.0,
        )
        self.assertEqual(maximum, {"Cheese wheel": 0, "Cheese": 35})
        self.assertEqual(maximum_xp, 140.0)
        self.assertEqual(cheese_wheel_slice_yield_pure(48, 0.0), 5)
        self.assertEqual(cheese_wheel_slice_yield_pure(99, 1.0), 35)
        self.assertAlmostEqual(
            5.0 + 30.0 * cheese_wheel_slice_probability_pure(57),
            8.87,
        )
        self.assertAlmostEqual(
            5.0 + 30.0 * cheese_wheel_slice_probability_pure(99),
            695.0 / 27.0,
        )

    def test_rune_mysteries_real_stage_emitters_complete_and_reward_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        player_data, ok = start_quest_pure(player_data, "rune_mysteries", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "rune_mysteries")
        self.assertEqual(player_data["inventory"]["Air talisman"], 1)
        self.assertNotIn("rune_mysteries", player_data["quest_stage_actions"])

        expected_steps = (
            (
                2,
                False,
                ("Deliver the strange talisman to Sedridor",),
                {"Air talisman": 0, "Research package": 1, "Research notes": 0},
            ),
            (
                3,
                False,
                ("Deliver the strange talisman to Sedridor",),
                {"Air talisman": 0, "Research package": 1, "Research notes": 0},
            ),
            (
                4,
                False,
                (
                    "Deliver the strange talisman to Sedridor",
                    "Deliver Sedridor's package to Aubury",
                ),
                {"Air talisman": 0, "Research package": 0, "Research notes": 1},
            ),
            (
                5,
                False,
                (
                    "Deliver the strange talisman to Sedridor",
                    "Deliver Sedridor's package to Aubury",
                ),
                {"Air talisman": 0, "Research package": 0, "Research notes": 1},
            ),
            (
                6,
                True,
                (
                    "Deliver the strange talisman to Sedridor",
                    "Deliver Sedridor's package to Aubury",
                    "Return Aubury's research notes to Sedridor",
                ),
                {"Air talisman": 1, "Research package": 0, "Research notes": 0},
            ),
        )
        for progress, completed, actions, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "rune_mysteries",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, completed)
            self.assertEqual(
                player_data["quests"]["rune_mysteries"]["progress"],
                progress,
            )
            self.assertEqual(
                tuple(player_data["quest_stage_actions"]["rune_mysteries"]),
                actions,
            )
            self.assertEqual(
                {
                    item_name: player_data["inventory"].get(item_name, 0)
                    for item_name in inventory
                },
                inventory,
            )

        self.assertTrue(player_data["quests"]["rune_mysteries"]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["runecrafting_exp"], 0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "rune_mysteries",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["inventory"]["Air talisman"], 1)
        self.assertEqual(after_complete["runecrafting_exp"], 0)
        self.assertEqual(after_complete["pending_skill_exp_rewards"], {})

    def test_tale_of_the_muspah_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "the_tale_of_the_muspah"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        reasons = quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA)
        self.assertIn("Firemaking 6", reasons)
        self.assertFalse(can_start_quest_pure(player_data, quest_id, QUEST_DATA))

        for skill_id in ("firemaking", "magic", "mining", "woodcutting"):
            player_data[f"{skill_id}_level"] = 10
        player_data["inventory"].update(
            {
                "Amulet of glory": 1,
                "Cosmic rune": 8,
                "Desert clothing": 1,
                "Explorer's ring": 1,
                "Hatchet": 1,
                "Knife": 1,
                "Sapphire": 8,
                "Spade": 1,
                "Tinderbox": 1,
                "Waterskin": 1,
                "Water rune": 8,
                "Water staff": 1,
                "Weight-reducing clothing": 1,
            }
        )
        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_steps = (
            (
                2,
                False,
                (
                    "Cast Enchant Level 1 Jewellery for the sapphire preparations",
                    "Reach the Muspah cave route through Rellekka and Pollnivneach",
                ),
                {"Sapphire": 8},
            ),
            (
                3,
                False,
                (
                    "Cast Enchant Level 1 Jewellery for the sapphire preparations",
                    "Reach the Muspah cave route through Rellekka and Pollnivneach",
                    "Reach Rellekka",
                ),
                {"Sapphire": 8},
            ),
            (
                4,
                False,
                (
                    "Cast Enchant Level 1 Jewellery for the sapphire preparations",
                    "Reach the Muspah cave route through Rellekka and Pollnivneach",
                    "Reach Rellekka",
                    "Reach Pollnivneach",
                ),
                {"Sapphire": 8},
            ),
            (
                5,
                False,
                (
                    "Cast Enchant Level 1 Jewellery for the sapphire preparations",
                    "Reach the Muspah cave route through Rellekka and Pollnivneach",
                    "Reach Rellekka",
                    "Reach Pollnivneach",
                    "Bore sapphires from the ice block and enchant them",
                    "Enchant the sapphires for Ali the Wise",
                ),
                {"Sapphire": 8},
            ),
            (
                6,
                True,
                (
                    "Cast Enchant Level 1 Jewellery for the sapphire preparations",
                    "Reach the Muspah cave route through Rellekka and Pollnivneach",
                    "Reach Rellekka",
                    "Reach Pollnivneach",
                    "Bore sapphires from the ice block and enchant them",
                    "Enchant the sapphires for Ali the Wise",
                    "Bore and enchant the sapphires around Jhallan",
                ),
                {"Sapphire": 8},
            ),
        )
        for progress, completed, actions, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, completed)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions)
            self.assertEqual(
                {item_name: player_data["inventory"].get(item_name, 0) for item_name in inventory},
                inventory,
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["firemaking_exp"], 500.0)
        self.assertEqual(player_data["magic_exp"], 1000.0)
        self.assertEqual(player_data["mining_exp"], 800.0)
        self.assertEqual(player_data["woodcutting_exp"], 800.0)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["firemaking_exp"], 500.0)

    def test_monks_friend_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "monks_friend"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"].update({"Jug of water": 1, "Logs": 1})

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_steps = (
            (
                2,
                False,
                ("Recover the child's blanket from the thieves' hideout",),
                {"Child's blanket": 1, "Jug of water": 1, "Logs": 1},
            ),
            (
                3,
                False,
                ("Recover the child's blanket from the thieves' hideout",),
                {"Child's blanket": 0, "Jug of water": 1, "Logs": 1},
            ),
            (
                4,
                False,
                (
                    "Recover the child's blanket from the thieves' hideout",
                    "Ask Brother Omad about Brother Cedric and the party",
                ),
                {"Child's blanket": 0, "Jug of water": 1, "Logs": 1},
            ),
            (
                5,
                False,
                (
                    "Recover the child's blanket from the thieves' hideout",
                    "Ask Brother Omad about Brother Cedric and the party",
                ),
                {"Child's blanket": 0, "Jug of water": 0, "Logs": 1},
            ),
            (
                6,
                False,
                (
                    "Recover the child's blanket from the thieves' hideout",
                    "Ask Brother Omad about Brother Cedric and the party",
                ),
                {"Child's blanket": 0, "Jug of water": 0, "Logs": 0},
            ),
            (
                7,
                True,
                (
                    "Recover the child's blanket from the thieves' hideout",
                    "Ask Brother Omad about Brother Cedric and the party",
                    "Return to Brother Omad and join the birthday party",
                ),
                {"Child's blanket": 0, "Jug of water": 0, "Logs": 0},
            ),
        )
        for progress, completed, actions, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, completed)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                actions,
            )
            self.assertEqual(
                {
                    item_name: player_data["inventory"].get(item_name, 0)
                    for item_name in inventory
                },
                inventory,
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["inventory"]["Law rune"], 8)
        self.assertNotIn("Law Rune", player_data["inventory"])
        self.assertEqual(player_data["woodcutting_exp"], 2000.0)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["inventory"]["Law rune"], 8)
        self.assertNotIn("Law Rune", after_complete["inventory"])
        self.assertEqual(after_complete["woodcutting_exp"], 2000.0)

    def test_tribal_totem_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "tribal_totem"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        reasons = quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA)
        self.assertIn("Thieving 21", reasons)
        self.assertFalse(can_start_quest_pure(player_data, quest_id, QUEST_DATA))

        player_data["thieving_level"] = 21
        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        cromperty_action = "Ask Wizard Cromperty about the teleportation block"
        depot_actions = (
            "Reach the Ardougne RPDT depot",
            "Take Lord Handelmort's address label from the RPDT crate",
        )
        switch_action = ("Switch the RPDT crate address labels and request delivery",)
        mansion_actions = (
            "Teleport into Handelmort Mansion",
            "Disarm Handelmort's trapped stairs",
            "Solve Handelmort's lock with KURT",
            "Loot the Rantuki totem",
        )

        expected_steps = (
            (2, False, (cromperty_action,), {"Address label": 0, "Totem": 0}),
            (3, False, (cromperty_action,) + depot_actions, {"Address label": 1, "Totem": 0}),
            (4, False, (cromperty_action,) + depot_actions + switch_action, {"Address label": 0, "Totem": 0}),
            (
                5,
                False,
                (cromperty_action,) + depot_actions + switch_action + mansion_actions,
                {"Address label": 0, "Totem": 1},
            ),
            (6, True, None, {"Address label": 0, "Totem": 0}),
        )
        for progress, completed, actions, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, completed)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            if actions is not None:
                self.assertEqual(
                    tuple(player_data["quest_stage_actions"][quest_id]),
                    actions,
                )
            self.assertEqual(
                {
                    item_name: player_data["inventory"].get(item_name, 0)
                    for item_name in inventory
                },
                inventory,
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["thieving_exp"], 1775.0)
        self.assertEqual(player_data["inventory"]["Swordfish"], 5)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["thieving_exp"], 1775.0)
        self.assertEqual(after_complete["inventory"]["Swordfish"], 5)

    def test_monkey_madness_ape_atoll_infiltration_emits_on_review(self):
        quest_id = "monkey_madness"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        quest = QUEST_DATA[quest_id]
        for requirement in quest["required_quests"]:
            prerequisite = QUEST_DATA[requirement["quest_id"]]
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": prerequisite["stages"],
                "completed": True,
            }
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        player_data["inventory"].update({"Gold bar": 1, "Ball of wool": 1, "Bananas": 5})

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            player_data["quest_stage_actions"][quest_id],
            [
                "Acquire the monkey dentures, m'amulet mould, and monkey talisman during the Ape Atoll infiltration"
            ],
        )

    def test_rat_catchers_rat_poison_emitter_advances_real_stage(self):
        quest_id = "rat_catchers"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for requirement in QUEST_DATA[quest_id]["required_quests"]:
            prerequisite = QUEST_DATA[requirement["quest_id"]]
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": prerequisite["stages"],
                "completed": True,
            }
        player_data["inventory"].update(
            {
                "Vial": 1,
                "Clean kwuarm": 1,
                "Red spiders' eggs": 1,
                "Cheese": 4,
                "Unicorn horn dust": 1,
                "Clean marrentill": 1,
                "Bucket of milk": 1,
                "Catspeak amulet": 1,
                "Pot of weeds": 1,
                "Coins": 600,
                "Snake Charm": 1,
                "Cat": 1,
                "Tinderbox": 1,
            }
        )

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            player_data["quest_stage_actions"][quest_id],
            ["Have Hooknosed Jack make rat poison"],
        )
        self.assertEqual(player_data["inventory"]["Vial"], 0)
        self.assertEqual(player_data["inventory"]["Clean kwuarm"], 0)
        self.assertEqual(player_data["inventory"]["Red spiders' eggs"], 0)
        self.assertEqual(player_data["inventory"]["Rat poison"], 1)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Action required: Complete Rat Catchers stage 2 objective",),
        )

    def test_kings_ransom_cromperty_scroll_emitter_advances_real_stage(self):
        quest_id = "kings_ransom"
        action = "Receive the animate rock scroll from Wizard Cromperty after recovering the Holy Grail"
        quest = QUEST_DATA[quest_id]
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for requirement in quest["required_quests"]:
            prerequisite = QUEST_DATA[requirement["quest_id"]]
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": prerequisite["stages"],
                "completed": True,
            }
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        player_data["inventory"].update(
            {
                "Bronze helm": 1,
                "Granite": 1,
                "Iron chainbody": 1,
                "Lockpick": 1,
            }
        )

        stage_one = next(
            requirement
            for requirement in quest["stage_requirements"]
            if requirement["stage"] == 1
        )
        self.assertEqual(stage_one["required_actions"], ())
        self.assertEqual(stage_one["auto_actions"], (action,))
        self.assertEqual(stage_one["source"], KINGS_RANSOM_SCROLL_SOURCE)

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(player_data["quest_stage_actions"][quest_id], [action])
        self.assertEqual(player_data["inventory"]["Animate rock scroll"], 1)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Action required: Complete King's Ransom stage 2 objective",),
        )

    def test_clock_tower_real_stage_emitters_complete_and_reward_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        player_data, ok = start_quest_pure(player_data, "clock_tower", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "clock_tower")
        self.assertNotIn("clock_tower", player_data["quest_stage_actions"])

        expected_actions = (
            "Pick up rat poison in the Clock Tower dungeon",
            "Poison the Clock Tower dungeon rats",
            "Find the white, black, blue, and red Clock Tower cogs",
            "Place the four Clock Tower cogs",
            "Report the repaired clock to Brother Kojo",
        )
        expected_inventory = (
            {"Rat poison": 1, "White cog": 0, "Black cog": 0, "Blue cog": 0, "Red cog": 0},
            {"Rat poison": 0, "White cog": 0, "Black cog": 0, "Blue cog": 0, "Red cog": 0},
            {"Rat poison": 0, "White cog": 1, "Black cog": 1, "Blue cog": 1, "Red cog": 1},
            {"Rat poison": 0, "White cog": 0, "Black cog": 0, "Blue cog": 0, "Red cog": 0},
            {"Rat poison": 0, "White cog": 0, "Black cog": 0, "Blue cog": 0, "Red cog": 0},
        )

        for stage, inventory in enumerate(expected_inventory, start=1):
            if stage == 4:
                self.assertEqual(
                    quest_current_stage_blocker_reasons_pure(player_data, "clock_tower", QUEST_DATA),
                    ("Needs Bucket of water x1 or Ice gloves x1",),
                )
                player_data["inventory"]["Bucket of water"] = 1
            self.assertEqual(
                quest_current_stage_blocker_reasons_pure(player_data, "clock_tower", QUEST_DATA),
                (),
            )

            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "clock_tower",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, stage == 5)
            self.assertEqual(player_data["quests"]["clock_tower"]["progress"], stage + 1)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"]["clock_tower"]),
                expected_actions[:stage],
            )
            self.assertEqual(
                {
                    item_name: player_data["inventory"].get(item_name, 0)
                    for item_name in inventory
                },
                inventory,
            )

        self.assertTrue(player_data["quests"]["clock_tower"]["completed"])
        self.assertEqual(player_data["inventory"]["Bucket of water"], 1)
        self.assertEqual(player_data["inventory"]["Coins"], 500)
        self.assertNotIn("Coin", player_data["inventory"])
        self.assertEqual(player_data["quest_points"], 1)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "clock_tower",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["inventory"]["Coins"], 500)
        self.assertNotIn("Coin", after_complete["inventory"])
        self.assertEqual(after_complete["quest_points"], 1)

    def test_kenniths_concerns_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "kenniths_concerns"
        quest = QUEST_DATA[quest_id]
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for requirement in quest["required_quests"]:
            prerequisite = QUEST_DATA[requirement["quest_id"]]
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": prerequisite["stages"],
                "completed": True,
            }
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        player_data["inventory"]["Pickaxe"] = 1

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_actions = (
            "Reach the Witchaven shrine tunnels",
            "Talk to a villager past the rocks",
            "Warn Kennith",
            "Speak to Kent near the Legends' Guild",
            "Trap the possessed villagers in the church",
            "Mine rubium and fill the steam vents",
            "Find Kennith's toy train",
            "Use the toy train on Kennith",
        )
        for stage, action_count in enumerate((2, 4, 5, 6, 8), start=1):
            self.assertEqual(
                quest_current_stage_blocker_reasons_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                ),
                (),
            )
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, stage == 5)
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage + 1)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                expected_actions[:action_count],
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["agility_exp"], 5000.0)
        self.assertEqual(player_data["mining_exp"], 12000.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["agility_exp"], 5000.0)
        self.assertEqual(after_complete["mining_exp"], 12000.0)

    def test_deadliest_catch_real_stage_emitters_complete_and_reward_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["fishing_level"] = 70
        player_data["hunter_level"] = 67
        player_data["thieving_level"] = 70
        player_data["quests"]["tower_of_life"] = {
            "started": True,
            "progress": QUEST_DATA["tower_of_life"]["stages"],
            "completed": True,
        }

        player_data, ok = start_quest_pure(player_data, "deadliest_catch", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "deadliest_catch")
        self.assertNotIn("deadliest_catch", player_data["quest_stage_actions"])

        expected_actions = (
            ("Pickpocket the Master fisher for the sea chart",),
            (
                "Pickpocket the Master fisher for the sea chart",
                "Recruit Linza",
                "Prepare the giant harpoon",
            ),
            (
                "Pickpocket the Master fisher for the sea chart",
                "Recruit Linza",
                "Prepare the giant harpoon",
                "Track the Thalassus",
                "Rescue Jones",
            ),
        )
        for stage, actions in enumerate(expected_actions, start=1):
            self.assertEqual(
                quest_current_stage_blocker_reasons_pure(
                    player_data,
                    "deadliest_catch",
                    QUEST_DATA,
                ),
                (),
            )
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "deadliest_catch",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, stage == 3)
            self.assertEqual(
                player_data["quests"]["deadliest_catch"]["progress"],
                stage + 1,
            )
            self.assertEqual(
                tuple(player_data["quest_stage_actions"]["deadliest_catch"]),
                actions,
            )

        self.assertTrue(player_data["quests"]["deadliest_catch"]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["inventory"]["Small cast net"], 1)
        self.assertEqual(player_data["fishing_exp"], 70000.0)
        self.assertEqual(player_data["hunter_exp"], 72660.0)
        self.assertEqual(player_data["thieving_exp"], 8000.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "deadliest_catch",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["fishing_exp"], 70000.0)
        self.assertEqual(after_complete["hunter_exp"], 72660.0)
        self.assertEqual(after_complete["thieving_exp"], 8000.0)

    def test_wolf_whistle_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "wolf_whistle"
        quest = QUEST_DATA[quest_id]
        self.assertEqual(len(quest["stage_requirements"]), 3)
        self.assertTrue(
            all(not requirement["required_actions"] for requirement in quest["stage_requirements"])
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_actions = (
            "Find Scalectrix at the Taverley well",
            "Collect the ancient wolf bone amulet",
            "Collect the embroidered pouch",
            "Collect the white hare meat",
            "Infuse the giant wolpertinger pouch",
            "Take the pouch to Scalectrix",
        )
        for stage, action_count in enumerate((1, 4, 6), start=1):
            self.assertEqual(
                quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
                (),
            )
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, stage == 3)
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage + 1)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                expected_actions[:action_count],
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["inventory"]["Gold charm"], 275)
        self.assertEqual(player_data["summoning_exp"], 276.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["inventory"]["Gold charm"], 275)
        self.assertEqual(after_complete["summoning_exp"], 276.0)

    def test_song_from_the_depths_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "song_from_the_depths"
        quest = QUEST_DATA[quest_id]
        self.assertEqual(len(quest["stage_requirements"]), 3)
        self.assertTrue(
            all(not requirement["required_actions"] for requirement in quest["stage_requirements"])
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        starting_constitution_exp = player_data["constitution_exp"]

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_actions = (
            "Drink the restless sleep potion",
            "Follow the souls to the cave entrance",
            "Complete the maze doors",
            "Solve the symbol rooms",
            "Move the saplings through the dream rooms",
            "Escape the dragon's stomach",
            "Return to Lucille",
        )
        for stage, action_count in enumerate((2, 5, 7), start=1):
            self.assertEqual(
                quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
                (),
            )
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, stage == 3)
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage + 1)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                expected_actions[:action_count],
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["inventory"]["Coral bolts"], 50)
        self.assertEqual(player_data["inventory"]["Coral crossbow"], 1)
        self.assertNotIn("Queen Black Dragon", player_data["inventory"])
        self.assertEqual(player_data["inventory"]["Remora's necklace"], 1)
        self.assertEqual(
            player_data["constitution_exp"],
            starting_constitution_exp + 700.0,
        )
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["inventory"]["Coral bolts"], 50)
        self.assertEqual(after_complete["inventory"]["Coral crossbow"], 1)
        self.assertEqual(
            after_complete["constitution_exp"],
            starting_constitution_exp + 700.0,
        )

    def test_some_like_it_cold_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "some_like_it_cold"
        quest = QUEST_DATA[quest_id]
        self.assertEqual(len(quest["stage_requirements"]), 6)
        self.assertTrue(
            all(not requirement["required_actions"] for requirement in quest["stage_requirements"])
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.assertFalse(can_start_quest_pure(player_data, quest_id, QUEST_DATA))
        for requirement in quest["required_quests"]:
            prerequisite = QUEST_DATA[requirement["quest_id"]]
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": prerequisite["stages"],
                "completed": True,
            }
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        starting_exp = {
            skill_id: player_data[f"{skill_id}_exp"]
            for skill_id in ("construction", "crafting", "fishing", "thieving")
        }
        self.assertTrue(can_start_quest_pure(player_data, quest_id, QUEST_DATA))

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_actions = (
            "Speak to Chuck again for teleport",
            "Entertain the seal",
            "Travel to the Iceberg",
            "Build Ping and Pong's rock costumes",
            "Give Ping and Pong their costumes",
            "Distract the Walrus",
            "Steal the egg from the table",
            "Defeat Astoria in Battlefish",
            "Collect camp repair supplies",
            "Repair the submarine engine",
            "Defeat the seals in Battlefish",
            "Escape in the submarine",
        )
        for stage, action_count in enumerate((3, 5, 7, 10, 11, 12), start=1):
            self.assertEqual(
                quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
                (),
            )
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, stage == 6)
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage + 1)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                expected_actions[:action_count],
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertNotIn("Penguin Hide and Seek", player_data["inventory"])
        self.assertEqual(player_data["inventory"]["Rock costume"], 1)
        self.assertEqual(player_data["inventory"]["Pop costume"], 1)
        self.assertEqual(
            {
                skill_id: player_data[f"{skill_id}_exp"] - starting_exp[skill_id]
                for skill_id in starting_exp
            },
            {
                "construction": 10000.0,
                "crafting": 40000.0,
                "fishing": 40000.0,
                "thieving": 10000.0,
            },
        )
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertNotIn("Penguin Hide and Seek", after_complete["inventory"])
        self.assertEqual(after_complete["inventory"]["Rock costume"], 1)
        self.assertEqual(after_complete["inventory"]["Pop costume"], 1)
        self.assertEqual(
            {
                skill_id: after_complete[f"{skill_id}_exp"] - starting_exp[skill_id]
                for skill_id in starting_exp
            },
            {
                "construction": 10000.0,
                "crafting": 40000.0,
                "fishing": 40000.0,
                "thieving": 10000.0,
            },
        )

    def test_dealing_with_scabaras_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "dealing_with_scabaras"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        quest = QUEST_DATA[quest_id]
        for requirement in quest["required_quests"]:
            prerequisite = QUEST_DATA[requirement["quest_id"]]
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": prerequisite["stages"],
                "completed": True,
            }
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (
                "Needs Ugthanki dung x1",
                "Needs Pyramid top x1",
            ),
        )

        player_data["inventory"].update({"Ugthanki dung": 1, "Pyramid top": 1})
        expected_actions = (
            "Prepare bronze equipment for the High Priest's tests",
            "Reach the Agility Pyramid",
            "Copy at least four distinct Scabarite note identities into the research book.",
            "Use the key, allocate four unique power settings, stoke the furnace, "
            "and complete all four rooms in one timed attempt.",
            "After pulling all the levers you will be allowed to enter the antechamber.",
            "Enter the newly opened hallway.",
            "I must endure two different attack styles and persuade the High Priest that the "
            "Devourer caused the heresy.",
            "The High Priest of Scabaras has recovered. I should return to Sophanem.",
        )

        stage_action_counts = (2, 3, 4, 5, 6, 7, 8)
        for stage, action_count in zip(range(1, 8), stage_action_counts):
            if stage == 6:
                self.assertEqual(
                    quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
                    ("Combat locked until battle support is enabled: Skeletons",),
                )
                player_data["quest_combat_encounters"] = {
                    quest_id: ["dealing_with_scabaras_skeletons_1"]
                }
            self.assertEqual(
                quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
                (),
            )

            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, stage == 7)
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage + 1)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                expected_actions[:action_count],
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertNotIn("Pyramid Plunder", player_data["inventory"])
        self.assertEqual(player_data["agility_exp"], 7000.0)
        self.assertEqual(player_data["prayer_exp"], 7000.0)
        self.assertEqual(player_data["strength_exp"], 7000.0)
        self.assertEqual(player_data["thieving_exp"], 7000.0)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertNotIn("Pyramid Plunder", after_complete["inventory"])
        self.assertEqual(after_complete["agility_exp"], 7000.0)
        self.assertEqual(after_complete["prayer_exp"], 7000.0)
        self.assertEqual(after_complete["strength_exp"], 7000.0)
        self.assertEqual(after_complete["thieving_exp"], 7000.0)

    def test_tears_of_guthix_final_lantern_stage_runs_before_completion(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["current_quest"] = "tears_of_guthix"
        player_data["quests"]["tears_of_guthix"] = {
            "started": True,
            "progress": 2,
            "completed": False,
        }
        player_data["inventory"]["Bullseye lantern (empty)"] = 1
        player_data["inventory"]["Sapphire"] = 1
        player_data["quest_stage_actions"] = {
            "tears_of_guthix": ["Complete Tears of Guthix stage 2 objective"]
        }

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "tears_of_guthix",
            QUEST_DATA,
        )

        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["tears_of_guthix"]["progress"], 3)
        self.assertIn(
            "Needs Sapphire lantern (lit) x1",
            quest_current_stage_blocker_reasons_pure(
                player_data,
                "tears_of_guthix",
                QUEST_DATA,
            ),
        )

        player_data["inventory"]["Sapphire lantern (lit)"] = 1
        player_data["quest_stage_actions"]["tears_of_guthix"].append(
            "Complete Tears of Guthix stage 3 objective"
        )
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "tears_of_guthix",
            QUEST_DATA,
        )

        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["tears_of_guthix"]["completed"])
        self.assertEqual(player_data["quests"]["tears_of_guthix"]["progress"], 4)
        self.assertEqual(player_data["crafting_exp"], 1000.0)

    def test_unlock_quests_enforce_strict_start_requirements(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["crafting_level"] = 31
        player_data["woodcutting_level"] = 36

        reasons = quest_locked_reasons_pure(player_data, "lost_city", QUEST_DATA)
        self.assertEqual(reasons, ())

        lunar_reasons = quest_locked_reasons_pure(player_data, "lunar_diplomacy", QUEST_DATA)
        self.assertIn("The Fremennik Trials", lunar_reasons)
        self.assertIn("Lost City", lunar_reasons)
        self.assertIn("Rune Mysteries", lunar_reasons)
        self.assertIn("Shilo Village", lunar_reasons)
        self.assertIn("Defence 40", lunar_reasons)
        # Herblore is now implemented, so its requirement drops the suffix.
        self.assertIn("Herblore 5", lunar_reasons)
        self.assertNotIn("Herblore 5 (not implemented)", lunar_reasons)
        self.assertIn("Magic 65", lunar_reasons)
        self.assertFalse(can_start_quest_pure(player_data, "lunar_diplomacy", QUEST_DATA))

    def test_quest_availability_separates_start_locks_from_progress(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            quest_availability_state_pure(player_data, "lost_city", QUEST_DATA),
            "locked",
        )
        self.assertEqual(
            quest_availability_state_pure(player_data, "cooks_assistant", QUEST_DATA),
            "can_start",
        )

        # Stage 1's Shamus action is emitted automatically now, so a fresh
        # start reads as in progress until the Tree spirit gate at stage 3.
        player_data["quests"]["lost_city"] = {"started": True, "progress": 1, "completed": False}
        self.assertEqual(
            quest_availability_state_pure(player_data, "lost_city", QUEST_DATA),
            "in_progress",
        )
        player_data["quests"]["lost_city"] = {"started": True, "progress": 3, "completed": False}
        self.assertEqual(
            quest_availability_state_pure(player_data, "lost_city", QUEST_DATA),
            "blocked_at_stage",
        )

        player_data["quests"]["lost_city"] = {"started": True, "progress": 6, "completed": True}
        self.assertEqual(
            quest_availability_state_pure(player_data, "lost_city", QUEST_DATA),
            "completed",
        )

    def test_knights_sword_blocks_and_consumes_redberry_pie_at_thurgo_stage(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["mining_level"] = 10

        player_data, ok = start_quest_pure(player_data, "the_knights_sword", QUEST_DATA)
        self.assertTrue(ok)
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "the_knights_sword", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["the_knights_sword"]["progress"], 2)
        self.assertEqual(
            quest_availability_state_pure(player_data, "the_knights_sword", QUEST_DATA),
            "blocked_at_stage",
        )
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "the_knights_sword", QUEST_DATA),
            ("Needs Redberry pie x1",),
        )
        self.assertFalse(can_progress_quest_pure(player_data, "the_knights_sword", QUEST_DATA))

        blocked_data, ok, completed_now = apply_quest_progress_pure(player_data, "the_knights_sword", QUEST_DATA)
        self.assertFalse(ok)
        self.assertFalse(completed_now)
        self.assertFalse(blocked_data["quests"]["the_knights_sword"]["completed"])
        self.assertEqual(blocked_data["quests"]["the_knights_sword"]["progress"], 2)
        self.assertEqual(blocked_data["smithing_exp"], 0)

        player_data["inventory"]["Redberry pie"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "the_knights_sword", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Redberry pie"], 0)
        self.assertEqual(player_data["quests"]["the_knights_sword"]["progress"], 3)

    def test_knights_sword_requires_later_materials_before_completion_reward(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["mining_level"] = 10
        player_data["inventory"]["Redberry pie"] = 1

        for _ in range(5):
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, "the_knights_sword", QUEST_DATA)
            self.assertTrue(ok)
            self.assertFalse(completed_now)

        self.assertEqual(player_data["quests"]["the_knights_sword"]["progress"], 6)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "the_knights_sword", QUEST_DATA),
            ("Needs Blurite ore x1", "Needs Iron bar x2"),
        )
        blocked_data, ok, completed_now = apply_quest_progress_pure(player_data, "the_knights_sword", QUEST_DATA)
        self.assertFalse(ok)
        self.assertFalse(completed_now)
        self.assertEqual(blocked_data["quest_points"], 0)
        self.assertEqual(blocked_data["smithing_exp"], 0)

        player_data["inventory"]["Blurite ore"] = 1
        player_data["inventory"]["Iron bar"] = 2
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "the_knights_sword", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["the_knights_sword"]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["smithing_exp"], 12725)
        self.assertEqual(player_data["inventory"]["Blurite ore"], 0)
        self.assertEqual(player_data["inventory"]["Iron bar"], 0)
        self.assertEqual(player_data["inventory"]["Blurite bar"], 0)

    def test_dwarf_cannon_real_stage_emitters_complete_and_reward_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"]["Hammer"] = 1

        player_data, ok = start_quest_pure(player_data, "dwarf_cannon", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["dwarf_cannon"]["progress"], 0)
        self.assertNotIn("dwarf_cannon", player_data["quest_stage_actions"])
        self.assertTrue(can_progress_quest_pure(player_data, "dwarf_cannon", QUEST_DATA))
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "dwarf_cannon", QUEST_DATA),
            (),
        )
        self.assertEqual(quest_current_stage_resolvable_combat_blockers_pure(player_data, "dwarf_cannon", QUEST_DATA), ())

        expected_steps = (
            (2, (6, 0, 0, 0, 0)),
            (3, (0, 0, 0, 0, 0)),
            (4, (0, 0, 0, 0, 0)),
            (5, (0, 1, 0, 0, 0)),
            (6, (0, 0, 0, 0, 0)),
        )
        inventory_names = ("Railing", "Dwarf remains", "Toolkit", "Ammo mould", "Nulodion's notes")
        for progress, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, "dwarf_cannon", QUEST_DATA)
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"]["dwarf_cannon"]["progress"], progress)
            self.assertEqual(tuple(player_data["inventory"].get(item_name, 0) for item_name in inventory_names), inventory)

        self.assertEqual(quest_current_stage_blocker_reasons_pure(player_data, "dwarf_cannon", QUEST_DATA), ())

        expected_steps = (
            (7, False, (0, 0, 0, 0, 0)),
            (8, False, (0, 0, 0, 0, 0)),
            (9, False, (0, 0, 1, 0, 0)),
            (10, False, (0, 0, 1, 0, 0)),
            (11, False, (0, 0, 1, 0, 0)),
            (12, False, (0, 0, 1, 1, 1)),
            (13, False, (0, 0, 1, 0, 0)),
            (14, True, (0, 0, 1, 1, 0)),
        )
        for progress, completed, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, "dwarf_cannon", QUEST_DATA)
            self.assertTrue(ok)
            self.assertEqual(completed_now, completed)
            self.assertEqual(player_data["quests"]["dwarf_cannon"]["progress"], progress)
            self.assertEqual(tuple(player_data["inventory"].get(item_name, 0) for item_name in inventory_names), inventory)

        self.assertEqual(
            player_data["quest_stage_actions"]["dwarf_cannon"],
            [
                "Accept replacement railings from Captain Lawgof",
                "Report the repaired stockade to Captain Lawgof",
                "Take Gilob's remains from the watchtower",
                "Reach the Dwarf Cannon goblin hideout",
                "Rescue Lollk from the goblin hideout",
                "Tell Captain Lawgof that Lollk is safe",
                "Repair the sabotaged cannon",
                "Tell Captain Lawgof that the cannon is repaired",
                "Speak to Nulodion about Captain Lawgof's cannon",
                "Receive Captain Lawgof's cannon recommendation",
            ],
        )
        self.assertTrue(player_data["quests"]["dwarf_cannon"]["completed"])
        self.assertEqual(player_data["inventory"]["Hammer"], 1)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["crafting_exp"], 750)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(quest_current_stage_resolvable_combat_blockers_pure(player_data, "dwarf_cannon", QUEST_DATA), ())

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "dwarf_cannon", QUEST_DATA)
        self.assertFalse(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["crafting_exp"], 750)

    def test_fishing_contest_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "fishing_contest"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["fishing_level"] = 10
        player_data["inventory"].update(
            {
                "Coins": 5,
                "Garlic": 1,
                "Fishing rod": 1,
                "Red vine worm": 1,
            }
        )

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 0)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )

        pass_action = "Receive a fishing pass from Austri or Vestri"
        catch_action = "Catch the winning giant carp"
        inventory_names = (
            "Fishing pass",
            "Coins",
            "Garlic",
            "Red vine worm",
            "Raw giant carp",
            "Fishing trophy",
        )
        expected_steps = (
            (2, False, (pass_action,), (1, 5, 1, 1, 0, 0)),
            (3, False, (pass_action,), (1, 0, 1, 1, 0, 0)),
            (4, False, (pass_action,), (1, 0, 0, 1, 0, 0)),
            (5, False, (pass_action, catch_action), (1, 0, 0, 0, 1, 0)),
            (6, False, (pass_action, catch_action), (1, 0, 0, 0, 0, 1)),
            (7, True, (pass_action, catch_action), (1, 0, 0, 0, 0, 0)),
        )
        for progress, completed, actions, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, completed)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                actions,
            )
            self.assertEqual(
                tuple(player_data["inventory"].get(item_name, 0) for item_name in inventory_names),
                inventory,
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["fishing_exp"], 2437.0)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["fishing_exp"], 2437.0)

    def test_scorpion_catcher_real_stage_emitters_preserve_jailer_gate_and_complete(self):
        quest_id = "scorpion_catcher"
        actions = (
            "Accept Thormac's scorpion cage",
            "Ask the Seer for all three scorpion locations",
            "Reach the Taverley Dungeon scorpion room",
            "Catch the Taverley Dungeon Kharid scorpion",
            "Reach the Barbarian Outpost scorpion room",
            "Catch the Barbarian Outpost Kharid scorpion",
            "Reach the Edgeville Monastery scorpion room",
            "Catch the Edgeville Monastery Kharid scorpion",
            "Return the caged scorpions to Thormac",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["agility_level"] = 35
        player_data["prayer_level"] = 31

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 0)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        for progress, expected_actions in ((2, actions[:1]), (3, actions[:2])):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                expected_actions,
            )
            self.assertEqual(player_data["inventory"]["Scorpion cage"], 1)

        blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_locked",))
        self.assertEqual(
            {
                key: blockers[0][key]
                for key in (
                    "encounter_id",
                    "display_name",
                    "level",
                    "quantity",
                    "completed_quantity",
                    "remaining_quantity",
                )
            },
            {
                "encounter_id": "scorpion_catcher_jailer",
                "display_name": "Jailer",
                "level": 39,
                "quantity": 1,
                "completed_quantity": 0,
                "remaining_quantity": 1,
            },
        )
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Combat locked until battle support is enabled: Jailer level 39",),
        )
        blocked, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_now)
        self.assertEqual(blocked["quests"][quest_id]["progress"], 3)
        self.assertEqual(tuple(blocked["quest_stage_actions"][quest_id]), actions[:2])
        self.assertEqual(blocked["strength_exp"], 0)

        player_data["quest_combat_encounters"] = {
            quest_id: ["scorpion_catcher_jailer"]
        }
        expected_steps = (
            (4, False, actions[:4], 1),
            (5, False, actions[:6], 1),
            (6, False, actions[:8], 1),
            (7, True, actions, 0),
        )
        for progress, completed, expected_actions, cage_count in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, completed)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                expected_actions,
            )
            self.assertEqual(player_data["inventory"].get("Scorpion cage", 0), cage_count)
            self.assertEqual(
                player_data["quest_combat_encounters"],
                {quest_id: ["scorpion_catcher_jailer"]},
            )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["strength_exp"], 6625.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["strength_exp"], 6625.0)
        self.assertEqual(after_complete["inventory"].get("Scorpion cage", 0), 0)

    def test_sheep_herder_real_stage_emitters_preserve_consumption_and_rewards(self):
        quest_id = "sheep_herder"
        self.assertEqual(QUEST_DATA[quest_id]["rewards"], {"Coins": 3100})
        actions = (
            "Accept poisoned sheep feed from Councillor Halgrive",
            "Reach the Ardougne sheep enclosure",
            "Pick up the cattleprod from the sheep enclosure barn",
            "Herd and poison the red sheep",
            "Herd and poison the green sheep",
            "Herd and poison the blue sheep",
            "Herd and poison the yellow sheep",
            "Incinerate the red sheep bones",
            "Incinerate the green sheep bones",
            "Incinerate the blue sheep bones",
            "Incinerate the yellow sheep bones",
            "Report the incinerated sheep to Councillor Halgrive",
        )
        inventory_names = (
            "Coins",
            "Sheep feed",
            "Plague jacket",
            "Plague trousers",
            "Cattleprod",
            "Red sheep bones",
            "Green sheep bones",
            "Blue sheep bones",
            "Yellow sheep bones",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"]["Coins"] = 100

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 0)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_steps = (
            (2, False, actions[:1], (100, 1, 0, 0, 0, 0, 0, 0, 0)),
            (3, False, actions[:1], (0, 1, 1, 1, 0, 0, 0, 0, 0)),
            (4, False, actions[:3], (0, 1, 1, 1, 1, 0, 0, 0, 0)),
            (5, False, actions[:7], (0, 1, 1, 1, 1, 1, 1, 1, 1)),
            (6, True, actions, (3100, 1, 1, 1, 1, 0, 0, 0, 0)),
        )
        for progress, completed, expected_actions, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, completed)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                expected_actions,
            )
            self.assertEqual(
                tuple(
                    player_data["inventory"].get(item_name, 0)
                    for item_name in inventory_names
                ),
                inventory,
            )
            if progress == 4:
                missing_gear = copy.deepcopy(player_data)
                for item_name in (
                    "Sheep feed",
                    "Plague jacket",
                    "Plague trousers",
                    "Cattleprod",
                ):
                    missing_gear["inventory"][item_name] = 0
                self.assertEqual(
                    quest_current_stage_blocker_reasons_pure(
                        missing_gear,
                        quest_id,
                        QUEST_DATA,
                    ),
                    (
                        "Needs Sheep feed x1",
                        "Needs Plague jacket",
                        "Needs Plague trousers",
                        "Needs Cattleprod",
                    ),
                )

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 4)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        terminal_inventory = tuple(
            player_data["inventory"].get(item_name, 0)
            for item_name in inventory_names
        )
        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 4)
        self.assertEqual(
            tuple(
                after_complete["inventory"].get(item_name, 0)
                for item_name in inventory_names
            ),
            terminal_inventory,
        )

    def test_plague_city_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "plague_city"
        actions = (
            "Pick up the picture of Elena in Alrena's house",
            "Talk to Edmond with the gas mask",
            "Soften Edmond's mud patch with four buckets of water",
            "Dig through Edmond's softened mud patch",
            "Pull the sewer grill",
            "Ask Edmond for help with the grill",
            "Tie rope to the sewer grill",
            "Ask Edmond to pull the sewer grill rope",
            "Reach West Ardougne through the sewer pipe",
            "Speak to Jethick about Elena",
            "Show Jethick the picture of Elena",
            "Agree to return Jethick's book",
            "Return Jethick's book to Ted Rehnison",
            "Ask Martha Rehnison about Elena",
            "Ask Milli Rehnison where Elena was taken",
            "Ask the mourners for prison house clearance",
            "Convince the Clerk to let you speak to Bravek",
            "Ask Bravek for his cure recipe",
            "Mix chocolate dust with milk and snape grass",
            "Give Bravek the hangover cure",
            "Ask Bravek for a prison house warrant",
            "Enter the prison house with Bravek's warrant",
            "Search the barrel for the small key",
            "Unlock Elena's cell",
            "Free Elena and report to Edmond",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"].update(
            {
                "Bucket of milk": 1,
                "Bucket of water": 4,
                "Chocolate dust": 1,
                "Dwellberries": 1,
                "Pestle and mortar": 1,
                "Rope": 1,
                "Snape grass": 1,
                "Spade": 1,
            }
        )

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        # Stage 1: give Alrena the dwellberries; she makes the gas mask, and
        # the picture of Elena is picked up inside her house.
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(player_data["inventory"]["Dwellberries"], 0)
        self.assertEqual(player_data["inventory"]["Gas mask"], 1)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:1],
        )

        # Stage 9 requires a picture of Elena produced back at stage 1.
        for expected_progress in range(3, 10):
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], expected_progress)
        self.assertEqual(player_data["inventory"]["Bucket of water"], 0)
        self.assertEqual(player_data["inventory"]["Bucket"], 4)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:10],
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 10)
        self.assertEqual(player_data["inventory"]["Turnip growing for beginners"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 11)
        self.assertEqual(player_data["inventory"]["Turnip growing for beginners"], 0)

        for expected_progress in (12, 13):
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], expected_progress)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:16],
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 14)
        self.assertEqual(player_data["inventory"]["Scruffy note"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 15)
        self.assertEqual(player_data["inventory"]["Hangover cure"], 1)
        self.assertEqual(player_data["inventory"]["Chocolate dust"], 0)
        self.assertEqual(player_data["inventory"]["Bucket of milk"], 0)
        self.assertEqual(player_data["inventory"]["Snape grass"], 0)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 16)
        self.assertEqual(player_data["inventory"]["Hangover cure"], 0)
        self.assertEqual(player_data["inventory"]["Warrant"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quests"][quest_id]["progress"], 17)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions,
        )
        self.assertEqual(player_data["inventory"]["A small key"], 1)
        self.assertEqual(player_data["inventory"]["A magic scroll"], 1)
        self.assertEqual(player_data["inventory"]["Gas mask"], 1)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["mining_exp"], 2425.0)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["inventory"]["A magic scroll"], 1)

    def test_waterfall_quest_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "waterfall_quest"
        actions = (
            "Speak to Hudon by the waterfall",
            "Search the Baxtorian bookcase",
            "Read the Book on Baxtorian",
            "Search the Tree Gnome Village crate for the old key",
            "Unlock Golrie's prison",
            "Reach Golrie under Tree Gnome Village",
            "Search the waterfall crate for the large old key",
            "Use Glarial's pebble on Glarial's tomb",
            "Search Glarial's tomb for the amulet and urn",
            "Place six water runes on the pillars",
            "Place six air runes on the pillars",
            "Place six earth runes on the pillars",
            "Place Glarial's amulet on Glarial's statue",
            "Use Glarial's urn on the chalice",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        reasons = quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA)
        self.assertIn("Fishing 68", reasons)
        self.assertFalse(can_start_quest_pure(player_data, quest_id, QUEST_DATA))

        player_data["fishing_level"] = 68
        self.assertTrue(can_start_quest_pure(player_data, quest_id, QUEST_DATA))
        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])
        player_data["inventory"].update({"Rope": 1, "Water rune": 6, "Air rune": 6, "Earth rune": 6})

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"].get(quest_id, ())),
            actions[:1],
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Book on Baxtorian"], 1)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 3)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:3])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Old key"], 1)
        self.assertEqual(player_data["inventory"]["Glarial's pebble"], 1)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 4)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:6])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Large old key"], 1)
        self.assertEqual(player_data["inventory"]["Glarial's amulet"], 1)
        self.assertEqual(player_data["inventory"]["Glarial's urn"], 1)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 5)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:9])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quests"][quest_id]["progress"], 6)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions)
        self.assertEqual(player_data["inventory"]["Water rune"], 0)
        self.assertEqual(player_data["inventory"]["Air rune"], 0)
        self.assertEqual(player_data["inventory"]["Earth rune"], 0)
        self.assertEqual(player_data["inventory"]["Glarial's amulet"], 0)
        self.assertEqual(player_data["inventory"]["Glarial's urn"], 0)
        self.assertEqual(player_data["inventory"]["Rope"], 1)
        self.assertEqual(player_data["inventory"]["Diamond"], 2)
        self.assertEqual(player_data["inventory"]["Gold bar"], 2)
        self.assertEqual(player_data["inventory"]["Mithril seeds"], 40)
        self.assertEqual(player_data["attack_exp"], 13750.0)
        self.assertEqual(player_data["strength_exp"], 13750.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertFalse(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 6)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["attack_exp"], 13750.0)
        self.assertEqual(player_data["strength_exp"], 13750.0)

    def test_biohazard_real_stage_emitters_complete_and_reward_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["agility_level"] = 33
        player_data["magic_level"] = 33
        player_data["quests"]["plague_city"] = {
            "started": True,
            "progress": 18,
            "completed": True,
        }

        player_data, ok = start_quest_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "biohazard")
        self.assertNotIn("biohazard", player_data["quest_stage_actions"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "biohazard", QUEST_DATA),
            (),
        )

        player_data["inventory"].update({"Priest gown": 2})
        expected_actions = (
            "Ask Jerico about crossing the West Ardougne wall",
            "Ask Omart about the rope ladder",
            "Ask Jerico about using messenger pigeons",
            "Search Jerico's cupboard for bird feed",
            "Take a pigeon cage from Jerico's house",
            "Reach Jerico's pigeon release tile",
            "Scatter bird feed on the watchtower fence",
            "Open the pigeon cage at Jerico's release tile",
            "Reach Omart by the south West Ardougne wall",
            "Cross the West Ardougne wall with Omart and Kilron",
            "Reach the Mourner HQ garden in West Ardougne",
            "Pick up a rotten apple from the Mourner HQ garden",
            "Put the rotten apple in the Mourner HQ cauldron",
            "Search the box for a doctors' gown",
            "Enter Mourner HQ wearing the doctors' gown",
            "Defeat and search the level 13 mourner",
            "Unlock the distillator cage with the key",
            "Search the crate for Elena's distillator",
            "Return Elena's distillator",
            "Ask the Rimmington chemist for touch paper for Guidor",
            "Reach Guidor's house without Varrock guards confiscating the vials",
            "Give sulphuric broline to Hops",
            "Give ethenea to Da Vinci",
            "Give liquid honey to Chancy",
            "Collect the sulphuric broline from Hops in Varrock",
            "Collect the ethenea from Da Vinci in Varrock",
            "Collect the liquid honey from Chancy in Varrock",
            "Enter Guidor's room wearing priest gowns",
            "Give Guidor the vials, plague sample, and touch paper",
            "Tell Elena that Guidor found no plague",
            "Report the plague hoax to King Lathas",
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 2)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 3)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 4)
        self.assertEqual(player_data["inventory"]["Bird feed"], 1)
        self.assertEqual(player_data["inventory"]["Pigeon cage"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 5)
        self.assertEqual(player_data["inventory"]["Bird feed"], 0)
        self.assertEqual(player_data["inventory"]["Pigeon cage"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 6)
        self.assertEqual(player_data["inventory"].get("Rotten apple", 0), 0)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 7)
        self.assertEqual(player_data["inventory"]["Rotten apple"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 8)
        self.assertEqual(player_data["inventory"]["Rotten apple"], 0)
        self.assertEqual(player_data["inventory"]["Doctors' gown"], 1)

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "biohazard", QUEST_DATA),
            ("Combat locked until battle support is enabled: Mourner level 13",),
        )
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 30
        player_data["strength_level"] = 30
        player_data["defense_level"] = 30
        player_data["constitution_level"] = 30
        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "biohazard",
            QUEST_DATA,
            "biohazard_mourner_13",
        )
        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_resolved")

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 9)
        self.assertEqual(player_data["inventory"]["Key"], 1)
        self.assertEqual(player_data["inventory"]["Distillator"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 10)
        self.assertEqual(player_data["inventory"]["Distillator"], 0)
        self.assertEqual(player_data["inventory"]["Liquid honey"], 1)
        self.assertEqual(player_data["inventory"]["Ethenea"], 1)
        self.assertEqual(player_data["inventory"]["Sulphuric broline"], 1)
        self.assertEqual(player_data["inventory"]["Plague sample"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 11)
        self.assertEqual(player_data["inventory"]["Touch paper"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 12)
        self.assertEqual(player_data["inventory"]["Liquid honey"], 0)
        self.assertEqual(player_data["inventory"]["Ethenea"], 0)
        self.assertEqual(player_data["inventory"]["Sulphuric broline"], 0)
        self.assertEqual(player_data["inventory"]["Plague sample"], 0)
        self.assertEqual(player_data["inventory"]["Touch paper"], 0)
        self.assertEqual(player_data["inventory"]["Priest gown"], 2)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 13)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "biohazard", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["biohazard"]["completed"])
        self.assertEqual(player_data["quests"]["biohazard"]["progress"], 14)
        self.assertEqual(player_data["quest_points"], 3)
        self.assertNotIn("Combat Training Camp", player_data["inventory"])
        self.assertEqual(
            QUEST_DATA["biohazard"]["unlocks"],
            (
                "Ability to travel freely through the West Ardougne Gate",
                "Use of the Combat Training Camp north of Ardougne",
            ),
        )
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(player_data["thieving_exp"], 1250.0)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"]["biohazard"]),
            expected_actions,
        )

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "biohazard",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 3)
        self.assertNotIn("Combat Training Camp", after_complete["inventory"])
        self.assertEqual(after_complete["thieving_exp"], 1250.0)

    def test_carnillean_rising_real_stage_emitters_complete_and_reward_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["construction_level"] = 31
        player_data["thieving_level"] = 33
        for quest_id in ("the_blood_pact", "hazeel_cult"):
            player_data["quests"][quest_id] = {
                "started": True,
                "progress": QUEST_DATA[quest_id]["stages"],
                "completed": True,
            }

        player_data, ok = start_quest_pure(player_data, "carnillean_rising", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "carnillean_rising")
        self.assertNotIn("carnillean_rising", player_data["quest_stage_actions"])
        expected_actions = (
            "Speak to Xenia",
            "Speak to Ceril Carnillean",
            "Collect the Carnillean family book",
            "Gather the mansion props",
            "Build the cave quest hotspots",
            "Recruit Sarsaparilla and Claus",
            "Guide Philipe through the cellar quest",
            "Report back to Philipe",
            "Report back to Ceril and Xenia",
        )
        expected_steps = (
            (2, False, expected_actions[:2]),
            (3, False, expected_actions[:4]),
            (4, False, expected_actions[:6]),
            (5, False, expected_actions[:7]),
            (6, True, expected_actions),
        )
        for progress, completed, actions in expected_steps:
            self.assertEqual(
                quest_current_stage_blocker_reasons_pure(player_data, "carnillean_rising", QUEST_DATA),
                (),
            )
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "carnillean_rising",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, completed)
            self.assertEqual(player_data["quests"]["carnillean_rising"]["progress"], progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"]["carnillean_rising"]),
                actions,
            )

        self.assertTrue(player_data["quests"]["carnillean_rising"]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["inventory"]["Coins"], 5000)
        self.assertEqual(player_data["inventory"]["Philipe's sweets"], 1)
        self.assertEqual(player_data["inventory"]["Treasure chest (Carnillean Rising)"], 1)
        self.assertEqual(player_data["construction_exp"], 2500.0)
        self.assertEqual(player_data["thieving_exp"], 2500.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "carnillean_rising",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["inventory"]["Coins"], 5000)
        self.assertEqual(after_complete["construction_exp"], 2500.0)
        self.assertEqual(after_complete["thieving_exp"], 2500.0)

    def test_heroes_quest_real_stage_emitters_complete_both_routes(self):
        quest_id = "heroes_quest"
        common_actions = (
            "Accept Achietties' three proof item challenge",
            "Ask Gerrant how to catch lava eels",
            "Reach a lava eel fishing spot in Taverley Dungeon or the Lava Maze",
            "Cook the raw Lava eel",
            "Clear the Ice Queen lair rockslide",
            "Reach the Ice Queen lair through a Dusty key or Agility shortcut route",
            "Reach Entrana without prohibited combat equipment",
        )
        route_cases = (
            (
                "Join the Black Arm Gang",
                (
                    "Ask Katrine about the Scarface Pete candlestick mission",
                    "Enter the Black Arm Brimhaven hideout with the Four leaved clover password",
                    "Accept Trobert's deputy guard impersonation mission",
                    "Show the Id papers to Garv",
                    "Search Scarface Pete's candlestick chest",
                    "Give Pete's candlestick to Katrine",
                ),
            ),
            (
                "Join the Phoenix Gang",
                (
                    "Ask Straven about the Scarface Pete candlestick mission",
                    "Ask Alfonse the waiter for gherkins",
                    "Ask Charlie the cook about the Phoenix guard inside Scarface Pete's mansion",
                    "Enter Scarface Pete's mansion through the Phoenix Gang secret panel",
                    "Unlock the window room with a Black Arm Gang partner's miscellaneous key",
                    "Receive one of Pete's candlesticks after the Black Arm Gang partner opens the chest with Grip's key",
                    "Give Pete's candlestick to Straven",
                ),
            ),
        )

        for route_id, route_actions in route_cases:
            with self.subTest(route=route_id):
                player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                for prerequisite in ("shield_of_arrav", "lost_city", "dragon_slayer", "merlins_crystal", "druidic_ritual"):
                    player_data["quests"][prerequisite] = {
                        "started": True,
                        "progress": QUEST_DATA[prerequisite]["stages"],
                        "completed": True,
                    }
                player_data.update(
                    {
                        "attack_level": 99,
                        "constitution_level": 99,
                        "cooking_level": 60,
                        "defense_level": 99,
                        "fishing_level": 60,
                        "herblore_level": 30,
                        "mining_level": 60,
                        "quest_points": 56,
                        "strength_level": 99,
                    }
                )
                self.assertTrue(can_start_quest_pure(player_data, quest_id, QUEST_DATA))
                player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertEqual(player_data["current_quest"], quest_id)
                self.assertNotIn(quest_id, player_data["quest_stage_actions"])
                self.assertNotIn(quest_id, player_data.get("quest_route_states", {}))

                # Stage 1: accepting Achietties' challenge emits with the start.
                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
                self.assertEqual(
                    tuple(player_data["quest_stage_actions"][quest_id]),
                    common_actions[:1],
                )

                # Stage 2: Gerrant hands over Blamish snail slime.
                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["quests"][quest_id]["progress"], 3)
                self.assertEqual(player_data["inventory"]["Blamish snail slime"], 1)

                player_data["inventory"]["Harralander potion (unf)"] = 1
                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["inventory"]["Blamish snail slime"], 0)
                self.assertEqual(player_data["inventory"]["Harralander potion (unf)"], 0)
                self.assertEqual(player_data["inventory"]["Blamish oil"], 1)

                player_data["inventory"]["Fishing rod"] = 1
                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["inventory"]["Fishing rod"], 0)
                self.assertEqual(player_data["inventory"]["Oily fishing rod"], 1)

                player_data["inventory"]["Fishing bait"] = 1
                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["inventory"]["Fishing bait"], 0)
                self.assertEqual(player_data["inventory"]["Raw lava eel"], 1)
                self.assertEqual(
                    tuple(player_data["quest_stage_actions"][quest_id]),
                    common_actions[:3],
                )

                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["inventory"]["Raw lava eel"], 0)
                self.assertEqual(player_data["inventory"]["Lava eel"], 1)
                self.assertEqual(
                    tuple(player_data["quest_stage_actions"][quest_id]),
                    common_actions[:4],
                )

                player_data["inventory"]["Bronze pickaxe"] = 1
                self.assertEqual(
                    quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
                    ("Combat locked until battle support is enabled: Ice Queen level 111",),
                )
                player_data["quest_combat_config"] = {"resolver_enabled": True}
                player_data, ok, result = apply_quest_combat_encounter_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                    f"{quest_id}_ice_queen_111",
                )
                self.assertTrue(ok, result)
                self.assertEqual(result["reason"], "combat_resolved")
                self.assertEqual(result["encounter_id"], f"{quest_id}_ice_queen_111")
                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["inventory"]["Ice gloves"], 1)
                self.assertEqual(
                    tuple(player_data["quest_stage_actions"][quest_id]),
                    common_actions[:6],
                )

                player_data, ok, result = apply_quest_combat_encounter_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                    f"{quest_id}_entrana_fire_bird_2",
                )
                self.assertTrue(ok, result)
                self.assertEqual(result["reason"], "combat_resolved")
                self.assertEqual(result["encounter_id"], f"{quest_id}_entrana_fire_bird_2")
                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["quests"][quest_id]["progress"], 9)
                self.assertEqual(player_data["inventory"]["Fire feather"], 1)
                self.assertEqual(
                    tuple(player_data["quest_stage_actions"][quest_id]),
                    common_actions,
                )

                # Stage 9 splits on the gang contact chosen at that stage.
                self.assertEqual(
                    quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
                    ("Choose path: Phoenix Gang or Black Arm Gang",),
                )
                player_data, ok = apply_quest_route_choice_pure(player_data, quest_id, QUEST_DATA, route_id)
                self.assertTrue(ok)
                self.assertEqual(player_data["quest_route_states"][quest_id], [route_id])

                if route_id == "Join the Black Arm Gang":
                    player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                    self.assertTrue(ok)
                    self.assertFalse(completed_now)
                    self.assertEqual(player_data["inventory"]["Id papers"], 1)

                    player_data["inventory"].update(
                        {"Black full helm": 1, "Black platebody": 1, "Black platelegs": 1}
                    )
                    player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                    self.assertTrue(ok)
                    self.assertFalse(completed_now)
                    self.assertEqual(player_data["inventory"]["Id papers"], 0)
                    self.assertEqual(player_data["inventory"]["Pete's candlestick"], 1)
                else:
                    coins_before_mansion = player_data["inventory"]["Coins"]
                    self.assertEqual(coins_before_mansion, 0)
                    player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                    self.assertTrue(ok)
                    self.assertFalse(completed_now)
                    self.assertEqual(
                        quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
                        ("Battle required: Grip level 22",),
                    )
                    player_data, ok, result = apply_quest_combat_encounter_pure(
                        player_data,
                        quest_id,
                        QUEST_DATA,
                        f"{quest_id}_grip_22",
                    )
                    self.assertTrue(ok, result)
                    self.assertEqual(result["reason"], "combat_resolved")
                    self.assertEqual(result["encounter_id"], f"{quest_id}_grip_22")
                    player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                    self.assertTrue(ok)
                    self.assertFalse(completed_now)
                    self.assertEqual(player_data["inventory"]["Coins"], coins_before_mansion)
                    self.assertEqual(player_data["inventory"]["Pete's candlestick"], 1)

                self.assertEqual(
                    tuple(player_data["quest_stage_actions"][quest_id]),
                    (*common_actions, *route_actions[:-1]),
                )

                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["inventory"]["Pete's candlestick"], 0)
                self.assertEqual(player_data["inventory"]["Thieves' armband"], 1)
                self.assertEqual(
                    tuple(player_data["quest_stage_actions"][quest_id]),
                    (*common_actions, *route_actions),
                )

                player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertTrue(completed_now)
                self.assertTrue(player_data["quests"][quest_id]["completed"])
                self.assertEqual(player_data["quests"][quest_id]["progress"], 13)
                self.assertEqual(player_data["quest_points"], 57)
                self.assertEqual(player_data["inventory"]["Lava eel"], 0)
                self.assertEqual(player_data["inventory"]["Fire feather"], 0)
                self.assertEqual(player_data["inventory"]["Thieves' armband"], 0)
                self.assertEqual(player_data["fishing_exp"], 2725.0)
                self.assertEqual(player_data["cooking_exp"], 2825.0)
                self.assertEqual(player_data["defense_exp"], 3075.0)
                # Herblore is now an implemented skill, so its quest reward is awarded
                # directly rather than held in pending_skill_exp_rewards.
                self.assertEqual(player_data["herblore_exp"], 1325.0)
                self.assertNotIn("herblore_exp", player_data["pending_skill_exp_rewards"])

                after_complete, ok, completed_again = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertFalse(ok)
                self.assertFalse(completed_again)
                self.assertEqual(after_complete["quest_points"], 57)

    def test_hazeel_cult_routes_grant_only_their_own_artifact(self):
        quest_id = "hazeel_cult"
        route_cases = (
            (
                "Side with Ceril Carnillean",
                {"Carnillean armour": 1, "Coins": 2005},
            ),
            (
                "Side with Hazeel's cult",
                {"Coins": 2005, "Mark of Hazeel": 1},
            ),
        )
        for route_id, expected_grants in route_cases:
            with self.subTest(route=route_id):
                player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                inventory_before = dict(player_data["inventory"])
                player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                player_data, ok = apply_quest_route_choice_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                    route_id,
                )
                self.assertTrue(ok)

                actions = player_data.setdefault("quest_stage_actions", {}).setdefault(quest_id, [])
                actions.append("Complete Hazeel Cult stage 1 objective")
                player_data, ok, completed_now = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertTrue(ok)
                self.assertFalse(completed_now)

                actions = player_data.setdefault("quest_stage_actions", {}).setdefault(quest_id, [])
                actions.append("Complete Hazeel Cult stage 2 objective")
                if route_id == "Side with Ceril Carnillean":
                    player_data.update(
                        {
                            "attack_level": 99,
                            "constitution_level": 99,
                            "defense_level": 99,
                            "strength_level": 99,
                        }
                    )
                    player_data["quest_combat_config"] = {"resolver_enabled": True}
                    for expected_remaining in (1, 0):
                        player_data, ok, result = apply_quest_combat_encounter_pure(
                            player_data,
                            quest_id,
                            QUEST_DATA,
                            "hazeel_cult_alomone_13",
                        )
                        self.assertTrue(ok, result)
                        self.assertTrue(result["killed"], result)
                        self.assertEqual(result["remaining_quantity"], expected_remaining)
                player_data, ok, completed_now = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["quests"][quest_id]["progress"], 3)
                if route_id == "Side with Ceril Carnillean":
                    self.assertEqual(player_data["inventory"]["Carnillean armour"], 2)

                actions = player_data.setdefault("quest_stage_actions", {}).setdefault(quest_id, [])
                actions.append("Complete Hazeel Cult stage 3 objective")
                player_data, ok, completed_now = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertTrue(ok)
                self.assertTrue(completed_now)
                grants = {
                    item_name: amount - inventory_before.get(item_name, 0)
                    for item_name, amount in player_data["inventory"].items()
                    if amount > inventory_before.get(item_name, 0)
                }
                self.assertEqual(grants, expected_grants)

    def test_quest_route_choices_require_started_stage_and_cover_heroes_inherited_shield_route(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(quest_current_stage_choices_pure(player_data, "hazeel_cult", QUEST_DATA), ())
        unstarted = copy.deepcopy(player_data)
        rejected, ok = apply_quest_route_choice_pure(
            player_data,
            "hazeel_cult",
            QUEST_DATA,
            "Side with Hazeel's cult",
        )
        self.assertFalse(ok)
        self.assertIs(rejected, player_data)
        self.assertEqual(player_data, unstarted)

        player_data, ok = start_quest_pure(player_data, "hazeel_cult", QUEST_DATA)
        self.assertTrue(ok)
        hazeel_choices = quest_current_stage_choices_pure(player_data, "hazeel_cult", QUEST_DATA)
        self.assertEqual(hazeel_choices[0]["stage"], 1)
        self.assertEqual(
            tuple(option["route_id"] for option in hazeel_choices[0]["options"]),
            ("Side with Ceril Carnillean", "Side with Hazeel's cult"),
        )
        player_data, ok = apply_quest_route_choice_pure(
            player_data,
            "hazeel_cult",
            QUEST_DATA,
            "Side with Hazeel's cult",
        )
        self.assertTrue(ok)
        self.assertEqual(player_data["quest_route_states"]["hazeel_cult"], ["Side with Hazeel's cult"])
        self.assertEqual(quest_current_stage_choices_pure(player_data, "hazeel_cult", QUEST_DATA), ())
        rejected, ok = apply_quest_route_choice_pure(
            player_data,
            "hazeel_cult",
            QUEST_DATA,
            "Side with Ceril Carnillean",
        )
        self.assertFalse(ok)
        self.assertIs(rejected, player_data)
        self.assertEqual(rejected["quest_route_states"]["hazeel_cult"], ["Side with Hazeel's cult"])
        self.assertTrue(player_data["quests"]["hazeel_cult"]["started"])

        heroes = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        heroes["quests"]["heroes_quest"] = {"started": True, "progress": 9, "completed": False}
        heroes["quest_route_states"] = {"shield_of_arrav": ["Join the Black Arm Gang"]}
        # The inherited Shield of Arrav route resolves the stage 9 gang choice,
        # and its contact dialogue now emits through ordinary review progress.
        self.assertEqual(quest_current_stage_choices_pure(heroes, "heroes_quest", QUEST_DATA), ())
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(heroes, "heroes_quest", QUEST_DATA),
            (),
        )

    def test_family_crest_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "family_crest"
        actions = (
            "Ask Caleb about the fish salad",
            "Ask Caleb where Avan is searching for treasure",
            "Ask the Al Kharid gem trader about Avan",
            "Ask Avan about perfect gold jewellery",
            "Ask Boot about perfect gold",
            "Reach the Witchaven perfect gold mine",
            "Solve the Witchaven dungeon lever puzzle",
            "Mine two perfect gold ores",
            "Smelt the perfect gold ore in a furnace",
            "Craft the perfect ruby ring and perfect ruby necklace",
            "Use an unnoted antipoison on Johnathon",
            "Ask Johnathon about Chronozon",
            "Reach Chronozon's lair in Edgeville Dungeon",
            "Hit Chronozon with Air, Water, Earth, and Fire Blast",
            "Combine the three crest parts",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data.update(
            {
                "crafting_level": 40,
                "mining_level": 40,
                "smithing_level": 40,
                "attack_level": 99,
                "strength_level": 99,
                "defense_level": 99,
                "constitution_level": 99,
                "magic_level": 59,
            }
        )
        player_data["inventory"].update(
            {
                "Shrimps": 1,
                "Salmon": 1,
                "Tuna": 1,
                "Bass": 1,
                "Swordfish": 1,
                "Bronze pickaxe": 1,
                "Ruby": 2,
                "Ring mould": 1,
                "Necklace mould": 1,
                # Any unnoted dose satisfies Johnathon; Darkan accepts ids
                # 2446/175/177/179 and rejects only the noted twins.
                "Antipoison (4)": 1,
                # Chronozon out-damages a burst without food healing.
                "Shark": 20,
            }
        )
        player_data["equipment"] = {"weapon": "Abyssal whip"}

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        # Stage 2: the Caleb fish-salad dialogue emits through normal review
        # progression, without any pre-seeded action flags.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 3)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:1])

        # Stages 4 through 7: the Avan dialogue chain.
        for expected_progress in range(4, 9):
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], expected_progress)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:5])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 9)
        self.assertEqual(player_data["inventory"]["Perfect gold ore"], 2)
        self.assertEqual(player_data["inventory"]["Shrimps"], 0)
        self.assertEqual(player_data["inventory"]["Swordfish"], 0)
        self.assertEqual(player_data["inventory"]["Caleb crest"], 1)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:8])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 10)
        self.assertEqual(player_data["inventory"]["Perfect gold ore"], 0)
        self.assertEqual(player_data["inventory"]["Perfect gold bar"], 2)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 11)
        self.assertEqual(player_data["inventory"]["Perfect gold bar"], 0)
        self.assertEqual(player_data["inventory"]["Ruby"], 0)
        self.assertEqual(player_data["inventory"]["Perfect ruby ring"], 1)
        self.assertEqual(player_data["inventory"]["Perfect ruby necklace"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 12)
        self.assertEqual(player_data["inventory"]["Perfect ruby ring"], 0)
        self.assertEqual(player_data["inventory"]["Perfect ruby necklace"], 0)
        self.assertEqual(player_data["inventory"]["Avan crest"], 1)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:10])

        # Stage 12: any unnoted antipoison dose satisfies Johnathon.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 13)
        self.assertEqual(player_data["inventory"]["Antipoison (4)"], 0)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:12])

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Combat locked until battle support is enabled: Chronozon level 170",),
        )
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        for _ in range(10):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                quest_id,
                QUEST_DATA,
                f"{quest_id}_chronozon_170",
                ticks=500,
                rng=lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            if result["killed"]:
                break
        self.assertTrue(result["killed"], result)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 14)
        self.assertEqual(player_data["inventory"]["Johnathon crest"], 1)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:14])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 15)
        self.assertEqual(player_data["inventory"]["Caleb crest"], 0)
        self.assertEqual(player_data["inventory"]["Avan crest"], 0)
        self.assertEqual(player_data["inventory"]["Johnathon crest"], 0)
        self.assertEqual(player_data["inventory"]["Family crest"], 1)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quests"][quest_id]["progress"], 16)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["inventory"]["Family gauntlets"], 1)
        self.assertEqual(player_data["family_gauntlet_enchantment"], "family")

    def test_temple_of_ikov_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "temple_of_ikov"
        actions = (
            "Enter the Temple of Ikov",
            "Cut through the Temple of Ikov web",
            "Pick up the Boots of lightness",
            "Cross the Temple of Ikov lava bridge at low weight",
            "Pick up the Temple of Ikov lever",
            "Place and pull the Temple of Ikov lever near the entrance",
            "Search the Temple of Ikov ice-arrow chests",
            "Search and disarm the trapped Fire Warrior lever",
            "Pull the disarmed Fire Warrior lever",
            "Ask Winelda to teleport across the lava",
            "Remove the Pendant of lucien and accept the Guardian cleansing",
            "Take the Staff of Armadyl from the guarded chamber",
            "Give the Staff of Armadyl to Lucien in Varrock",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        reasons = quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA)
        self.assertIn("Thieving 42", reasons)
        self.assertFalse(can_start_quest_pure(player_data, quest_id, QUEST_DATA))

        player_data["thieving_level"] = 42
        player_data["inventory"].update(
            {
                "Lit torch": 1,
                "Knife": 1,
                "Pendant of lucien": 1,
                "Yew shortbow": 1,
                "Limpwurt root": 20,
            }
        )
        player_data.update(
            {
                "attack_level": 120,
                "constitution_level": 120,
                "defense_level": 120,
                "ranged_level": 70,
                "strength_level": 120,
            }
        )
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        # Stages 1-3: entry emits its action; the web cut and boots pickup emit
        # together on stage 2, and the bridge crossing plus lever pickup emit
        # together on stage 3.
        for progress in (2, 3):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:3])
        self.assertEqual(player_data["inventory"]["Boots of lightness"], 1)

        # Stage 4 emits bridge and lever pickup; stage 5 consumes the lever.
        for progress in (4, 5):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
        self.assertEqual(player_data["inventory"]["Lever"], 0)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:6])

        # Stage 6 searches the ice chamber chests and produces ice arrows.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 6)
        self.assertEqual(player_data["inventory"]["Ice arrows"], 1)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:7])

        # Stage 7 disarms and pulls the trapped Fire Warrior lever.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 7)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:9],
        )

        blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["display_name"], "Fire Warrior of Lesarkus")
        player_data, ok, result = apply_quest_combat_encounter_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok, result)
        self.assertEqual(result["reason"], "combat_resolved")
        self.assertEqual(result["encounter_id"], "temple_of_ikov_fire_warrior_of_lesarkus_84")

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 8)
        self.assertEqual(player_data["inventory"]["Limpwurt root"], 20)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 9)
        self.assertEqual(player_data["inventory"]["Limpwurt root"], 0)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:10])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Choose path: Guardians of Armadyl or Lucien",),
        )

        def branch_progress(ready, route_id):
            data, ok = apply_quest_route_choice_pure(ready, quest_id, QUEST_DATA, route_id)
            self.assertTrue(ok)
            return data

        guardians_data = branch_progress(copy.deepcopy(player_data), "Side with the Guardians of Armadyl")
        guardians_data, ok, completed_now = apply_quest_progress_pure(guardians_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(guardians_data["quests"][quest_id]["progress"], 10)
        self.assertEqual(guardians_data["inventory"]["Armadyl pendant"], 1)
        self.assertEqual(
            tuple(guardians_data["quest_stage_actions"][quest_id]),
            (*actions[:10], actions[10]),
        )
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(guardians_data, quest_id, QUEST_DATA),
            ("Battle required: Lucien level 14",),
        )
        guardians_data, ok, result = apply_quest_combat_encounter_pure(guardians_data, quest_id, QUEST_DATA)
        self.assertTrue(ok, result)
        self.assertEqual(result["encounter_id"], "temple_of_ikov_lucien_14")

        guardians_data, ok, completed_now = apply_quest_progress_pure(guardians_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(guardians_data["quests"][quest_id]["progress"], 11)
        self.assertTrue(guardians_data["quests"][quest_id]["completed"])
        self.assertEqual(guardians_data["quest_points"], 1)
        self.assertEqual(guardians_data["inventory"]["Shiny key"], 1)

        lucien_data = branch_progress(copy.deepcopy(player_data), "Side with Lucien")
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(lucien_data, quest_id, QUEST_DATA),
            ("Battle required: Guardian of Armadyl level 45",),
        )
        lucien_data, ok, result = apply_quest_combat_encounter_pure(lucien_data, quest_id, QUEST_DATA)
        self.assertTrue(ok, result)
        self.assertEqual(result["encounter_id"], "temple_of_ikov_guardian_of_armadyl_45")

        lucien_data, ok, completed_now = apply_quest_progress_pure(lucien_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(lucien_data["quests"][quest_id]["progress"], 10)
        self.assertEqual(lucien_data["inventory"]["Staff of armadyl"], 1)
        self.assertEqual(
            tuple(lucien_data["quest_stage_actions"][quest_id]),
            (*actions[:10], actions[11]),
        )

        lucien_data, ok, completed_now = apply_quest_progress_pure(lucien_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(lucien_data["quests"][quest_id]["progress"], 11)
        self.assertTrue(lucien_data["quests"][quest_id]["completed"])
        self.assertEqual(lucien_data["quest_points"], 1)
        self.assertEqual(lucien_data["inventory"]["Staff of armadyl"], 0)
        self.assertEqual(lucien_data["inventory"]["Shiny key"], 1)
        self.assertEqual(
            tuple(lucien_data["quest_stage_actions"][quest_id]),
            (*actions[:10], actions[11], actions[12]),
        )

    def test_holy_grail_real_stage_emitters_gate_titan_and_complete_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["attack_level"] = 20
        player_data["quests"]["merlins_crystal"] = {
            "started": True,
            "progress": QUEST_DATA["merlins_crystal"]["stages"],
            "completed": True,
        }

        player_data, ok = start_quest_pure(player_data, "holy_grail", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "holy_grail")
        self.assertNotIn("holy_grail", player_data["quest_stage_actions"])
        expected_actions = (
            "Ask Merlin about the Holy Grail",
            "Travel to Entrana",
            "Ask the Entrana High Priest and crone about the Grail",
            "Ask Sir Galahad for an artifact from the Fisher Realm",
            "Reach the Draynor Manor whistle room",
            "Find the Magic whistles in Draynor Manor",
            "Reach the Fisher Realm crossing at the six stone heads",
            "Blow the Magic whistle at the six stone heads",
            "Ring the Grail bell and ask the Fisher King about Percival",
            "Ask King Arthur about Sir Percival",
            "Use the Magic gold feather to find Sir Percival",
            "Free Sir Percival from the sack",
            "Show Sir Percival the Magic whistle",
            "Take the Holy grail from the restored Fisher Realm",
        )

        stage_action_counts = (1, 3, 4, 6, 8)
        for offset, expected_progress in enumerate(range(2, 7)[:-1]):
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, "holy_grail", QUEST_DATA)
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"]["holy_grail"]["progress"], expected_progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"]["holy_grail"]),
                expected_actions[: stage_action_counts[offset]],
            )

        self.assertEqual(player_data["inventory"]["Holy table napkin"], 1)
        self.assertEqual(player_data["inventory"]["Magic whistle"], 2)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "holy_grail", QUEST_DATA),
            (
                "Needs Excalibur",
                "Combat locked until battle support is enabled: Black Knight Titan level 120",
            ),
        )

        player_data["inventory"]["Excalibur"] = 1
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "holy_grail", QUEST_DATA),
            ("Combat locked until battle support is enabled: Black Knight Titan level 120",),
        )
        player_data["quest_combat_encounters"] = {"holy_grail": ["holy_grail_black_knight_titan_120"]}
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "holy_grail", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["holy_grail"]["progress"], 6)
        self.assertEqual(player_data["inventory"]["Grail bell"], 1)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"]["holy_grail"]),
            expected_actions[:8],
        )

        for expected_progress, action_count in ((7, 9), (8, 10), (9, 13)):
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, "holy_grail", QUEST_DATA)
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"]["holy_grail"]["progress"], expected_progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"]["holy_grail"]),
                expected_actions[:action_count],
            )

        self.assertEqual(player_data["inventory"]["Magic whistle"], 1)
        self.assertEqual(player_data["inventory"]["Magic gold feather"], 1)
        self.assertEqual(player_data["inventory"].get("Holy grail", 0), 0)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "holy_grail", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["holy_grail"]["progress"], 10)
        self.assertEqual(player_data["inventory"]["Holy grail"], 1)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"]["holy_grail"]),
            expected_actions,
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "holy_grail", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["holy_grail"]["completed"])
        self.assertEqual(player_data["inventory"]["Holy grail"], 0)
        self.assertEqual(player_data["defense_exp"], 15300.0)
        self.assertEqual(player_data["prayer_exp"], 11000.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(player_data["quest_points"], 2)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "holy_grail",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 2)
        self.assertEqual(after_complete["defense_exp"], 15300.0)
        self.assertEqual(after_complete["prayer_exp"], 11000.0)

    def test_tree_gnome_village_real_stage_emitters_complete_after_commanders_and_warlord(self):
        quest_id = "tree_gnome_village"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"]["Logs"] = 6

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 0)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])
        self.assertNotIn(quest_id, player_data["quest_route_states"])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            (
                "Reach Commander Montai on the battlefield",
                "Ask Commander Montai how to help the gnome battlefield",
            ),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 3)
        self.assertEqual(player_data["inventory"]["Logs"], 0)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 4)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            (
                "Reach Commander Montai on the battlefield",
                "Ask Commander Montai how to help the gnome battlefield",
                "Ask Commander Montai about the tracker gnomes",
            ),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 5)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            (
                "Reach Commander Montai on the battlefield",
                "Ask Commander Montai how to help the gnome battlefield",
                "Ask Commander Montai about the tracker gnomes",
                "Get the first tracker coordinate",
                "Get the second tracker coordinate",
                "Get the third tracker coordinate",
                "Fire the battlefield ballista at the Khazard stronghold",
            ),
        )
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Combat locked until battle support is enabled: Khazard commander level 48 x2",),
        )

        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data.update(
            {
                "attack_level": 120,
                "strength_level": 120,
                "defense_level": 120,
                "constitution_level": 120,
                "prayer_level": 1,
            }
        )
        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(result["completed_quantity"], 1)
        self.assertEqual(result["remaining_quantity"], 1)
        self.assertEqual(
            player_data["quest_combat_encounter_counts"],
            {quest_id: {"tree_gnome_village_khazard_commander_48": 1}},
        )

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(result["completed_quantity"], 2)
        self.assertEqual(result["remaining_quantity"], 0)
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {quest_id: ["tree_gnome_village_khazard_commander_48"]},
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 6)
        self.assertEqual(player_data["inventory"]["Orb of protection"], 1)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            (
                "Reach Commander Montai on the battlefield",
                "Ask Commander Montai how to help the gnome battlefield",
                "Ask Commander Montai about the tracker gnomes",
                "Get the first tracker coordinate",
                "Get the second tracker coordinate",
                "Get the third tracker coordinate",
                "Fire the battlefield ballista at the Khazard stronghold",
                "Enter the Khazard stronghold through the broken wall",
                "Search the stronghold chest for the first Orb of protection",
            ),
        )
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Battle required: Khazard warlord level 112",),
        )

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(result["display_name"], "Khazard warlord")
        self.assertEqual(result["remaining_quantity"], 0)
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {
                quest_id: [
                    "tree_gnome_village_khazard_commander_48",
                    "tree_gnome_village_khazard_warlord_112",
                ]
            },
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 7)
        self.assertEqual(player_data["inventory"]["Orb of protection"], 0)
        self.assertEqual(player_data["inventory"]["Orbs of protection"], 1)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            (
                "Reach Commander Montai on the battlefield",
                "Ask Commander Montai how to help the gnome battlefield",
                "Ask Commander Montai about the tracker gnomes",
                "Get the first tracker coordinate",
                "Get the second tracker coordinate",
                "Get the third tracker coordinate",
                "Fire the battlefield ballista at the Khazard stronghold",
                "Enter the Khazard stronghold through the broken wall",
                "Search the stronghold chest for the first Orb of protection",
                "Return the first Orb of protection to King Bolren",
            ),
        )

        attack_before_reward = player_data["attack_exp"]
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quests"][quest_id]["progress"], 8)
        self.assertEqual(player_data["inventory"]["Logs"], 0)
        self.assertEqual(player_data["inventory"]["Orb of protection"], 0)
        self.assertEqual(player_data["inventory"]["Orbs of protection"], 0)
        self.assertEqual(player_data["inventory"]["Gnome amulet"], 1)
        self.assertAlmostEqual(player_data["attack_exp"] - attack_before_reward, 11450.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(player_data["quest_points"], 2)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["inventory"]["Gnome amulet"], 1)
        self.assertEqual(after_complete["attack_exp"], player_data["attack_exp"])
        self.assertEqual(after_complete["pending_skill_exp_rewards"], {})
        self.assertEqual(after_complete["quest_points"], 2)

    def test_shield_of_arrav_real_stage_emitters_complete_both_routes(self):
        quest_id = "shield_of_arrav"
        common_actions = (
            "Find and read the Shield of Arrav book",
            "Ask Reldo about the Phoenix Gang",
            "Bribe Baraek for the Phoenix hideout",
        )
        route_cases = (
            (
                "Join the Phoenix Gang",
                "shield_of_arrav_jonny_the_beard_2",
                (
                    "Ask Straven for the Phoenix loyalty task",
                    "Hand Straven Jonny's intelligence report",
                    "Search the Phoenix Gang shield chest",
                    "Show King Roald the Phoenix shield half",
                    "Have Curator Haig Halen authenticate the Phoenix shield half",
                    "Claim the Shield of Arrav reward from King Roald",
                ),
                "Intel report",
                1,
                "Broken shield (Phoenix half)",
                "Half certificate (Phoenix)",
            ),
            (
                "Join the Black Arm Gang",
                "shield_of_arrav_weaponsmaster_23",
                (
                    "Ask Charlie and Katrine for the Black Arm loyalty task",
                    "Hand Katrine two Phoenix crossbows",
                    "Search the Black Arm Gang cupboard",
                    "Show King Roald the Black Arm shield half",
                    "Have Curator Haig Halen authenticate the Black Arm shield half",
                    "Claim the Shield of Arrav reward from King Roald",
                ),
                "Phoenix crossbow",
                2,
                "Broken shield (Black Arm half)",
                "Half certificate (Black Arm)",
            ),
        )

        for (
            route_id,
            encounter_id,
            route_actions,
            proof_item,
            proof_quantity,
            shield_half,
            certificate_half,
        ) in route_cases:
            with self.subTest(route=route_id):
                player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                player_data["inventory"]["Coins"] = 20
                player_data["attack_level"] = 99
                player_data["strength_level"] = 99
                player_data["defense_level"] = 99
                player_data["constitution_level"] = 99

                player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
                self.assertTrue(ok)
                self.assertEqual(player_data["current_quest"], quest_id)
                self.assertNotIn(quest_id, player_data["quest_stage_actions"])

                for progress, action_count in ((2, 1), (3, 2), (4, 3)):
                    player_data, ok, completed_now = apply_quest_progress_pure(
                        player_data,
                        quest_id,
                        QUEST_DATA,
                    )
                    self.assertTrue(ok)
                    self.assertFalse(completed_now)
                    self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
                    self.assertEqual(
                        tuple(player_data["quest_stage_actions"][quest_id]),
                        common_actions[:action_count],
                    )

                self.assertEqual(player_data["inventory"]["Coins"], 0)
                self.assertEqual(player_data["inventory"]["Shield of Arrav book"], 1)
                self.assertEqual(
                    quest_current_stage_blocker_reasons_pure(
                        player_data,
                        quest_id,
                        QUEST_DATA,
                    ),
                    ("Choose path: Phoenix Gang or Black Arm Gang",),
                )
                player_data, ok = apply_quest_route_choice_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                    route_id,
                )
                self.assertTrue(ok)
                player_data, ok, completed_now = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["quests"][quest_id]["progress"], 5)
                self.assertEqual(
                    tuple(player_data["quest_stage_actions"][quest_id]),
                    common_actions + route_actions[:1],
                )

                player_data["quest_combat_config"] = {"resolver_enabled": True}
                player_data, ok, result = apply_quest_combat_encounter_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                    encounter_id,
                )
                self.assertTrue(ok)
                self.assertEqual(result["reason"], "combat_resolved")
                player_data, ok, completed_now = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertTrue(ok)
                self.assertFalse(completed_now)
                self.assertEqual(player_data["quests"][quest_id]["progress"], 6)
                self.assertEqual(player_data["inventory"][proof_item], proof_quantity)

                for stage, action_count in (
                    (6, 2),
                    (7, 3),
                    (8, 4),
                    (9, 5),
                    (10, 5),
                    (11, 6),
                ):
                    player_data, ok, completed_now = apply_quest_progress_pure(
                        player_data,
                        quest_id,
                        QUEST_DATA,
                    )
                    self.assertTrue(ok)
                    self.assertEqual(completed_now, stage == 11)
                    self.assertEqual(player_data["quests"][quest_id]["progress"], stage + 1)
                    self.assertEqual(
                        tuple(player_data["quest_stage_actions"][quest_id]),
                        common_actions + route_actions[:action_count],
                    )

                self.assertTrue(player_data["quests"][quest_id]["completed"])
                self.assertEqual(player_data["inventory"][proof_item], 0)
                self.assertEqual(player_data["inventory"].get(shield_half, 0), 0)
                self.assertEqual(player_data["inventory"][certificate_half], 1)
                self.assertEqual(player_data["inventory"].get("Certificate", 0), 0)
                self.assertEqual(player_data["inventory"]["Coins"], 600)
                self.assertEqual(player_data["quest_points"], 1)

                after_complete, ok, completed_again = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertFalse(ok)
                self.assertFalse(completed_again)
                self.assertEqual(after_complete["inventory"]["Coins"], 600)
                self.assertEqual(after_complete["quest_points"], 1)

    def test_shield_of_arrav_phoenix_route_blocks_combat_and_uses_contextual_certificate_half(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["shield_of_arrav"] = {"started": True, "progress": 4, "completed": False}

        choices = quest_current_stage_choices_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertEqual(choices[0]["prompt"], "Choose a gang.")
        self.assertEqual(
            tuple(option["route_id"] for option in choices[0]["options"]),
            ("Join the Phoenix Gang", "Join the Black Arm Gang"),
        )
        blockers = quest_current_stage_blockers_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("quest_choice",))
        self.assertEqual(
            tuple(blocker["reason"] for blocker in blockers),
            ("Choose path: Phoenix Gang or Black Arm Gang",),
        )
        selected, ok = apply_quest_route_choice_pure(player_data, "shield_of_arrav", QUEST_DATA, "Join the Phoenix Gang")
        self.assertTrue(ok)
        self.assertEqual(selected["quest_route_states"]["shield_of_arrav"], ["Join the Phoenix Gang"])
        selected_again, ok = apply_quest_route_choice_pure(
            selected,
            "shield_of_arrav",
            QUEST_DATA,
            "Join the Phoenix Gang",
        )
        self.assertTrue(ok)
        self.assertEqual(selected_again["quest_route_states"]["shield_of_arrav"], ["Join the Phoenix Gang"])
        rejected, ok = apply_quest_route_choice_pure(
            selected,
            "shield_of_arrav",
            QUEST_DATA,
            "Join the Black Arm Gang",
        )
        self.assertFalse(ok)
        self.assertEqual(rejected["quest_route_states"]["shield_of_arrav"], ["Join the Phoenix Gang"])

        player_data["quests"]["shield_of_arrav"]["progress"] = 5
        player_data["quest_route_states"] = {"shield_of_arrav": ["Join the Phoenix Gang"]}
        blockers = quest_current_stage_blockers_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_locked",))
        self.assertEqual(
            blockers[0]["reason"],
            "Combat locked until battle support is enabled: Jonny the beard level 2",
        )

        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 20
        player_data["strength_level"] = 20
        player_data["defense_level"] = 20
        player_data["constitution_level"] = 20
        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "shield_of_arrav",
            QUEST_DATA,
            "shield_of_arrav_jonny_the_beard_2",
        )
        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_resolved")

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["shield_of_arrav"]["progress"], 6)
        self.assertEqual(player_data["inventory"]["Intel report"], 1)

        player_data["quest_stage_actions"] = {"shield_of_arrav": ["Hand Straven Jonny's intelligence report"]}
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Intel report"], 0)
        self.assertEqual(player_data["inventory"]["Weapon store key"], 1)

        player_data["quest_stage_actions"]["shield_of_arrav"].append("Search the Phoenix Gang shield chest")
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Broken shield (Phoenix half)"], 1)

        player_data["quest_stage_actions"]["shield_of_arrav"].append("Show King Roald the Phoenix shield half")
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Broken shield (Phoenix half)"], 1)

        player_data["quest_stage_actions"]["shield_of_arrav"].append(
            "Have Curator Haig Halen authenticate the Phoenix shield half"
        )
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Broken shield (Phoenix half)"], 0)
        self.assertEqual(player_data["inventory"]["Half certificate (Phoenix)"], 2)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Half certificate (Phoenix)"], 1)
        self.assertEqual(player_data["inventory"].get("Half certificate (Black Arm)", 0), 0)
        self.assertEqual(player_data["inventory"]["Certificate"], 1)

        player_data["quest_stage_actions"]["shield_of_arrav"].append("Claim the Shield of Arrav reward from King Roald")
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["shield_of_arrav"]["completed"])
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["inventory"]["Certificate"], 0)
        self.assertEqual(player_data["inventory"]["Coins"], 600)

    def test_shield_of_arrav_black_arm_route_uses_contextual_contact_and_isolates_variant_rewards(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["shield_of_arrav"] = {"started": True, "progress": 5, "completed": False}
        player_data["quest_route_states"] = {"shield_of_arrav": ["Join the Black Arm Gang"]}

        blockers = quest_current_stage_blockers_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertEqual(
            tuple(blocker["kind"] for blocker in blockers),
            ("combat_locked",),
        )
        self.assertEqual(
            blockers[0]["reason"],
            "Combat locked until battle support is enabled: Weaponsmaster level 23",
        )

        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 40
        player_data["strength_level"] = 40
        player_data["defense_level"] = 40
        player_data["constitution_level"] = 40
        self.assertEqual(
            tuple(blocker["kind"] for blocker in quest_current_stage_blockers_pure(player_data, "shield_of_arrav", QUEST_DATA)),
            ("combat_encounter",),
        )

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "shield_of_arrav",
            QUEST_DATA,
            "shield_of_arrav_weaponsmaster_23",
        )
        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_resolved")
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "shield_of_arrav", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Weapon store key"], 1)
        self.assertEqual(player_data["inventory"]["Phoenix crossbow"], 2)
        self.assertEqual(player_data["inventory"].get("Intel report", 0), 0)

    def test_fight_arena_stage_gates_items_combat_and_reward(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"]["Coins"] = 5

        player_data, ok = start_quest_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertNotIn("fight_arena", player_data["quest_stage_actions"])
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 2)
        self.assertEqual(player_data["inventory"]["Khazard helmet"], 1)
        self.assertEqual(player_data["inventory"]["Khazard armour"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 3)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "fight_arena", QUEST_DATA),
            (),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 4)
        self.assertEqual(
            player_data["quest_stage_actions"]["fight_arena"],
            ["Talk to Jeremy about the key holder"],
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Coins"], 0)
        self.assertEqual(player_data["inventory"]["Khali brew"], 1)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 5)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Khali brew"], 0)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 6)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Khazard cell keys"], 1)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 7)
        self.assertEqual(
            player_data["quest_stage_actions"]["fight_arena"],
            [
                "Talk to Jeremy about the key holder",
                "Steal the Khazard cell keys from the lazy guard",
            ],
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 8)
        self.assertEqual(
            player_data["quest_stage_actions"]["fight_arena"],
            [
                "Talk to Jeremy about the key holder",
                "Steal the Khazard cell keys from the lazy guard",
                "Use the Khazard cell keys on Jeremy's cell",
            ],
        )
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "fight_arena", QUEST_DATA),
            ("Combat locked until battle support is enabled: Khazard ogre level 63",),
        )

        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 150
        player_data["strength_level"] = 150
        player_data["defense_level"] = 150
        player_data["constitution_level"] = 150
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "fight_arena", QUEST_DATA),
            ("Combat stats required before battle support can resolve: Khazard ogre level 63",),
        )
        blocked_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertFalse(ok)
        self.assertFalse(completed_now)
        self.assertEqual(blocked_data["quests"]["fight_arena"]["progress"], 8)
        self.assertEqual(blocked_data.get("attack_exp", 0), 0)
        self.assertEqual(blocked_data.get("thieving_exp", 0), 0)

        player_data["quest_combat_encounters"] = {"fight_arena": ["fight_arena_khazard_ogre_63"]}
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 9)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "fight_arena", QUEST_DATA),
            ("Combat stats required before battle support can resolve: Khazard scorpion level 44",),
        )

        player_data["quest_combat_encounters"]["fight_arena"].append("fight_arena_khazard_scorpion_44")
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 10)
        self.assertEqual(
            tuple(blocker["kind"] for blocker in quest_current_stage_blockers_pure(player_data, "fight_arena", QUEST_DATA)),
            ("combat_encounter",),
        )

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "fight_arena",
            QUEST_DATA,
            "fight_arena_bouncer_137",
        )
        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_resolved")
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["fight_arena"]["progress"], 11)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "fight_arena", QUEST_DATA),
            (),
        )
        self.assertEqual(
            player_data["quest_stage_actions"]["fight_arena"],
            [
                "Talk to Jeremy about the key holder",
                "Steal the Khazard cell keys from the lazy guard",
                "Use the Khazard cell keys on Jeremy's cell",
            ],
        )

        attack_before_reward = player_data["attack_exp"]
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "fight_arena", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["fight_arena"]["completed"])
        self.assertEqual(player_data["quest_points"], 2)
        self.assertEqual(player_data["attack_exp"] - attack_before_reward, 12175.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        self.assertEqual(player_data["thieving_exp"], 2175.0)
        self.assertEqual(player_data["inventory"]["Coins"], 1000)
        self.assertEqual(
            player_data["quest_stage_actions"]["fight_arena"],
            [
                "Talk to Jeremy about the key holder",
                "Steal the Khazard cell keys from the lazy guard",
                "Use the Khazard cell keys on Jeremy's cell",
                "Return to Lady Servil for the reward",
            ],
        )

    def test_witchs_house_stage_gates_items_route_combat_and_reward(self):
        quest_id = "witchs_house"
        actions = (
            "Enter the Witch's house with the door key",
            "Use cheese on the mouse hole and attach the magnet to the mouse",
            "Avoid the witch's patrol through the house",
            "Unlock the Witch's shed door with the backroom key",
            "Return the ball to Harvey",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 0)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(player_data["inventory"]["Door key"], 1)
        self.assertEqual(tuple(player_data["quest_stage_actions"].get(quest_id, ())), ())

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 3)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:1])
        self.assertEqual(player_data["inventory"]["Door key"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 4)
        self.assertEqual(player_data["inventory"]["Magnet"], 1)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Needs Cheese x1",),
        )

        player_data["inventory"]["Cheese"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 5)
        self.assertEqual(player_data["inventory"]["Cheese"], 0)
        self.assertEqual(player_data["inventory"]["Magnet"], 1)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:2])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 6)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:3])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Needs Leather gloves",),
        )

        player_data["inventory"]["Leather gloves"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 7)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 8)
        self.assertEqual(player_data["inventory"]["Backroom key"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 9)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:4])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (
                "Combat locked until battle support is enabled: Witch's experiment (Skavid form) level 19",
                "Combat locked until battle support is enabled: Witch's experiment (Spider form) level 30",
                "Combat locked until battle support is enabled: Witch's experiment (Bear form) level 42",
                "Combat locked until battle support is enabled: Witch's experiment (Wolf form) level 53",
            ),
        )

        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 60
        player_data["strength_level"] = 60
        player_data["defense_level"] = 60
        player_data["constitution_level"] = 60
        resolved_encounters = []
        for expected_remaining in (3, 2, 1, 0):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(result["reason"], "combat_resolved")
            resolved_encounters.append(result["encounter_id"])
            self.assertEqual(player_data["quests"][quest_id]["progress"], 9)
            blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
            self.assertEqual(len(blockers), expected_remaining)
        self.assertEqual(
            resolved_encounters,
            [
                "witchs_house_witchs_experiment_first_form",
                "witchs_house_witchs_experiment_second_form",
                "witchs_house_witchs_experiment_third_form",
                "witchs_house_witchs_experiment_fourth_form",
            ],
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 10)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 11)
        self.assertEqual(player_data["inventory"]["Ball"], 1)

        constitution_before_reward = player_data["constitution_exp"]
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 4)
        self.assertEqual(player_data["inventory"]["Ball"], 0)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions)
        self.assertEqual(player_data["constitution_exp"] - constitution_before_reward, 6325.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertFalse(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quest_points"], 4)
        self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions)

    def test_merlins_crystal_completes_from_a_normal_start(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        player_data, ok = start_quest_pure(player_data, "merlins_crystal", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["quests"]["merlins_crystal"]["progress"], 0)
        # Stage 1 round-table investigation is emitted automatically.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "merlins_crystal", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["merlins_crystal"]["progress"], 2)
        self.assertEqual(player_data["quest_points"], 0)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "merlins_crystal", QUEST_DATA),
            (),
        )
        self.assertIn(
            "Complete the round-table investigation with Sir Gawain, Sir Lucan, and Sir Lancelot",
            player_data["quest_stage_actions"]["merlins_crystal"],
        )

        # Stage 3 is the Sir Mordred combat gate; stage 2 emits the crate route.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "merlins_crystal", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["merlins_crystal"]["progress"], 3)
        self.assertIn(
            "Reach Keep Le Faye through the Catherby crate delivery",
            player_data["quest_stage_actions"]["merlins_crystal"],
        )
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "merlins_crystal", QUEST_DATA),
            ("Combat locked until battle support is enabled: Sir Mordred level 39",),
        )

        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 50
        player_data["strength_level"] = 50
        player_data["defense_level"] = 50
        player_data["constitution_level"] = 50
        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "merlins_crystal",
            QUEST_DATA,
            "merlins_crystal_sir_mordred_39",
        )
        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_resolved")
        self.assertEqual(result["display_name"], "Sir Mordred")
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {"merlins_crystal": ["merlins_crystal_sir_mordred_39"]},
        )

        # The combat resolution does not advance the stage; the review apply
        # moves past Sir Mordred, then the wax stage consumes its items and
        # emits Morgan's dialogue automatically.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "merlins_crystal", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["merlins_crystal"]["progress"], 4)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "merlins_crystal", QUEST_DATA),
            ("Needs Bucket x1", "Needs Insect repellent x1"),
        )
        player_data["inventory"]["Bucket"] = 1
        player_data["inventory"]["Insect repellent"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "merlins_crystal", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Bucket"], 0)
        self.assertEqual(player_data["inventory"]["Insect repellent"], 1)
        self.assertEqual(player_data["inventory"]["Bucket of wax"], 1)
        self.assertEqual(player_data["quests"]["merlins_crystal"]["progress"], 5)
        self.assertIn(
            "Question Morgan Le Faye about Excalibur and the binding words",
            player_data["quest_stage_actions"]["merlins_crystal"],
        )

        # Stage 5 candle-maker exchange and stage 6 Excalibur trial are both automatic.
        player_data["inventory"]["Bread"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "merlins_crystal", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Bucket of wax"], 0)
        self.assertEqual(player_data["inventory"]["Black candle"], 1)
        self.assertEqual(player_data["quests"]["merlins_crystal"]["progress"], 6)
        self.assertIn(
            "Ask the Catherby candle-maker for a black candle",
            player_data["quest_stage_actions"]["merlins_crystal"],
        )
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "merlins_crystal", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Bread"], 0)
        self.assertEqual(player_data["inventory"]["Excalibur"], 1)
        self.assertEqual(player_data["quests"]["merlins_crystal"]["progress"], 7)
        self.assertEqual(
            [
                action
                for action in (
                    "Accept the Lady of the Lake's test in Taverley",
                    "Give bread to the Port Sarim beggar",
                )
                if action not in player_data["quest_stage_actions"]["merlins_crystal"]
            ],
            [],
        )
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "merlins_crystal", QUEST_DATA),
            ("Needs Bat bones x1", "Needs Tinderbox"),
        )

        # Stage 7 ritual chain: inscription, binding, smash, report are all automatic.
        player_data["inventory"]["Bat bones"] = 1
        player_data["inventory"]["Tinderbox"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "merlins_crystal", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["inventory"]["Bat bones"], 0)
        self.assertEqual(player_data["inventory"]["Black candle"], 0)
        self.assertEqual(player_data["inventory"]["Lit black candle"], 1)
        self.assertEqual(player_data["quests"]["merlins_crystal"]["progress"], 8)
        self.assertTrue(player_data["quests"]["merlins_crystal"]["completed"])
        self.assertEqual(player_data["quest_points"], 6)
        self.assertEqual(player_data["inventory"]["Excalibur"], 1)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})
        for action in (
            "Read the chaos altar inscription",
            "Bind Thrantax with Snarthon Candtrick Termanto",
            "Shatter Merlin's crystal with Excalibur",
            "Report Merlin's freedom to King Arthur",
        ):
            self.assertIn(action, player_data["quest_stage_actions"]["merlins_crystal"])

    def test_stage_requirement_model_exposes_tool_action_route_and_combat_blockers(self):
        quest_data = {
            "proof_quest": {
                "stages": 3,
                "stage_requirements": (
                    {
                        "stage": 2,
                        "required_tools": {"Rope": 1},
                        "required_inventory_options": ({"Redberry pie": 1, "Cake": 1},),
                        "required_actions": ("Mine blurite ore",),
                        "required_routes": ("Reach Thurgo's cave",),
                        "combat_encounters": (
                            {
                                "encounter_id": "ice_giant",
                                "display_name": "Ice giant",
                                "level": 53,
                                "source": "source",
                            },
                        ),
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "quests": {"proof_quest": {"started": True, "progress": 2, "completed": False}},
        }

        blockers = quest_current_stage_blockers_pure(player_data, "proof_quest", quest_data)
        self.assertEqual(
            tuple(blocker["kind"] for blocker in blockers),
            ("missing_item_option", "missing_tool", "required_action", "unmet_route", "combat_locked"),
        )
        self.assertEqual(quest_current_stage_resolvable_combat_blockers_pure(player_data, "proof_quest", quest_data), ())
        self.assertFalse(can_attempt_quest_review_pure(player_data, "proof_quest", quest_data))
        self.assertEqual(blockers[0]["reason"], "Needs Redberry pie x1 or Cake x1")
        self.assertEqual(blockers[-1]["reason"], "Combat locked until battle support is enabled: Ice giant level 53")

        player_data["inventory"]["Cake"] = 1
        player_data["inventory"]["Rope"] = 1
        player_data["quest_stage_actions"] = {"proof_quest": ["Mine blurite ore"]}
        player_data["quest_route_states"] = {"proof_quest": ["Reach Thurgo's cave"]}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        blockers = quest_current_stage_blockers_pure(player_data, "proof_quest", quest_data)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_missing_stats",))
        self.assertEqual(quest_current_stage_resolvable_combat_blockers_pure(player_data, "proof_quest", quest_data), ())
        self.assertEqual(blockers[0]["reason"], "Combat stats required before battle support can resolve: Ice giant level 53")

        player_data["quest_combat_encounters"] = {"proof_quest": ["ice_giant"]}
        self.assertEqual(quest_current_stage_blockers_pure(player_data, "proof_quest", quest_data), ())

    def test_stage_requirement_variants_select_one_route_branch(self):
        quest_data = {
            "branch_quest": {
                "stages": 2,
                "point_reward": 0,
                "rewards": {},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "variant": "red",
                        "required_routes": ("Red route",),
                        "consumed_inventory": {"Red key": 1},
                        "produced_inventory": {"Red token": 1},
                        "source": "source",
                    },
                    {
                        "stage": 1,
                        "variant": "blue",
                        "required_routes": ("Blue route",),
                        "consumed_inventory": {"Blue key": 1},
                        "produced_inventory": {"Blue token": 1},
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "quests": {"branch_quest": {"started": True, "progress": 1, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
        }

        blockers = quest_current_stage_blockers_pure(player_data, "branch_quest", quest_data)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("unmet_route", "unmet_route"))
        self.assertEqual(
            tuple(blocker["reason"] for blocker in blockers),
            ("Route required: Red route", "Route required: Blue route"),
        )

        player_data["quest_route_states"] = {"branch_quest": ["Red route"]}
        blockers = quest_current_stage_blockers_pure(player_data, "branch_quest", quest_data)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("missing_item",))
        self.assertEqual(blockers[0]["reason"], "Needs Red key x1")

        player_data["quest_route_states"] = {"branch_quest": ["Blue route"]}
        player_data["inventory"]["Blue key"] = 1
        completed, ok, completed_now = apply_quest_progress_pure(player_data, "branch_quest", quest_data)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(completed["inventory"]["Blue key"], 0)
        self.assertEqual(completed["inventory"]["Blue token"], 1)
        self.assertEqual(completed["inventory"].get("Red token", 0), 0)

    def test_stage_requirement_options_preserve_independent_alternative_groups(self):
        quest_data = {
            "dye_quest": {
                "stages": 1,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_inventory_options": (
                            ({"Coins": 5}, {"Blue dye": 1}),
                            ({"Coins": 10}, {"Orange dye": 1}),
                        ),
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {"Blue dye": 1},
            "quests": {"dye_quest": {"started": True, "progress": 1, "completed": False}},
        }

        blockers = quest_current_stage_blockers_pure(player_data, "dye_quest", quest_data)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("missing_item_option",))
        self.assertEqual(blockers[0]["reason"], "Needs Coins x10 or Orange dye x1")

        player_data["inventory"]["Orange dye"] = 1
        self.assertEqual(quest_current_stage_blockers_pure(player_data, "dye_quest", quest_data), ())

    def test_required_item_alternative_accepts_an_equipped_exact_state(self):
        quest_data = {
            "cave_quest": {
                "stages": 1,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_inventory_options": (
                            ({"Bullseye lantern (lit)": 1}, {"Mining helmet (lit)": 1}),
                        ),
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "equipment": {"head": "Mining helmet (lit)"},
            "quests": {"cave_quest": {"started": True, "progress": 1, "completed": False}},
        }

        self.assertEqual(quest_current_stage_blockers_pure(player_data, "cave_quest", quest_data), ())

    def test_consumed_item_alternative_does_not_accept_an_equipped_item(self):
        quest_data = {
            "offering_quest": {
                "stages": 1,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "consumed_inventory_options": (({"Amulet of power": 1},),),
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "equipment": {"neck": "Amulet of power"},
            "quests": {"offering_quest": {"started": True, "progress": 1, "completed": False}},
        }

        blockers = quest_current_stage_blockers_pure(player_data, "offering_quest", quest_data)

        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("missing_item_option",))

    def test_consumed_inventory_options_block_and_consume_selected_alternative(self):
        quest_data = {
            "essence_quest": {
                "stages": 1,
                "point_reward": 0,
                "rewards": {},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "consumed_inventory_options": (({"Rune essence": 50}, {"Pure essence": 25}),),
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {"Rune essence": 49, "Pure essence": 24},
            "quests": {"essence_quest": {"started": True, "progress": 1, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
        }

        blockers = quest_current_stage_blockers_pure(player_data, "essence_quest", quest_data)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("missing_item_option",))
        self.assertEqual(blockers[0]["reason"], "Needs Rune essence x50 or Pure essence x25")

        player_data["inventory"]["Pure essence"] = 25
        completed, ok, completed_now = apply_quest_progress_pure(player_data, "essence_quest", quest_data)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(completed["inventory"]["Pure essence"], 0)
        self.assertEqual(completed["inventory"]["Rune essence"], 49)

    def test_stage_progress_can_produce_inventory_for_later_stage_gates(self):
        quest_data = {
            "key_quest": {
                "stages": 2,
                "point_reward": 0,
                "rewards": {},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "consumed_inventory": {"Karamja rum": 1},
                        "produced_inventory": {"Chest key": 1},
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {"Karamja rum": 1},
            "quests": {"key_quest": {"started": True, "progress": 1, "completed": False}},
            "quest_points": 0,
            "pending_skill_exp_rewards": {},
        }

        progressed, ok, completed_now = apply_quest_progress_pure(player_data, "key_quest", quest_data)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(progressed["inventory"]["Karamja rum"], 0)
        self.assertEqual(progressed["inventory"]["Chest key"], 1)

    def test_priest_in_peril_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "priest_in_peril"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        for skill_id in ("attack", "strength", "defense", "constitution", "ranged", "magic", "prayer"):
            player_data[f"{skill_id}_level"] = 99
        player_data["combat_lifepoints"] = 990
        player_data["equipment"].update({"weapon": "Rune sword", "shield": "Rune kiteshield"})

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            player_data["quest_stage_actions"][quest_id],
            ["Speak through the Paterdomus temple door"],
        )

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
            "priest_in_peril_temple_guardian_dog_30",
            ticks=500,
            rng=lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
            stop_after_first_kill=True,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["reason"], "combat_resolved")
        self.assertEqual(result["completed_quantity"], 1)
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 3)

        for progress, actions in (
            (
                4,
                [
                    "Speak through the Paterdomus temple door",
                    "Report the dead guard dog to King Roald",
                ],
            ),
            (
                5,
                [
                    "Speak through the Paterdomus temple door",
                    "Report the dead guard dog to King Roald",
                    "Find Drezel imprisoned in the Paterdomus cell",
                ],
            ),
        ):
            player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(player_data["quest_stage_actions"][quest_id], actions)

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
            "priest_in_peril_monk_of_zamorak_30",
            ticks=500,
            rng=lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
            stop_after_first_kill=True,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["reason"], "combat_resolved")
        self.assertEqual(result["completed_quantity"], 1)
        self.assertEqual(player_data["inventory"]["Golden key"], 1)
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 6)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 7)
        self.assertEqual(player_data["inventory"]["Golden key"], 0)
        self.assertEqual(
            player_data["quest_stage_actions"][quest_id],
            [
                "Speak through the Paterdomus temple door",
                "Report the dead guard dog to King Roald",
                "Find Drezel imprisoned in the Paterdomus cell",
                "Swap the golden key at the Paterdomus monument",
                "Unlock Drezel's cell",
            ],
        )

        player_data["inventory"]["Bucket"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 8)
        self.assertEqual(
            player_data["quest_stage_actions"][quest_id],
            [
                "Speak through the Paterdomus temple door",
                "Report the dead guard dog to King Roald",
                "Find Drezel imprisoned in the Paterdomus cell",
                "Swap the golden key at the Paterdomus monument",
                "Unlock Drezel's cell",
                "Bless Salve water with Drezel",
                "Pour blessed Salve water over the vampire coffin",
            ],
        )

        player_data["inventory"]["Pure essence"] = 25
        player_data["inventory"]["Rune essence"] = 3
        completed, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(completed["quests"][quest_id]["completed"])
        self.assertEqual(completed["inventory"]["Pure essence"], 0)
        self.assertEqual(completed["inventory"]["Rune essence"], 3)
        self.assertEqual(completed["inventory"]["Wolfbane dagger"], 1)
        self.assertEqual(completed["quest_points"], 1)
        self.assertEqual(completed["prayer_exp"], 1406.0)
        self.assertEqual(completed["pending_skill_exp_rewards"], {})

        completed_again, ok, completed_now = apply_quest_progress_pure(
            completed,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_now)
        self.assertEqual(completed_again["inventory"]["Wolfbane dagger"], 1)

    def test_nature_spirit_completes_after_normal_prerequisites_and_real_combat(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        for skill_id in (
            "attack",
            "strength",
            "defense",
            "constitution",
            "ranged",
            "magic",
            "prayer",
            "crafting",
        ):
            player_data[f"{skill_id}_level"] = 99
        player_data["combat_lifepoints"] = 990
        player_data["equipment"].update({"weapon": "Rune sword", "shield": "Rune kiteshield"})

        player_data, ok = start_quest_pure(player_data, "the_restless_ghost", QUEST_DATA)
        self.assertTrue(ok)
        for _ in range(3):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "the_restless_ghost",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "the_restless_ghost",
            QUEST_DATA,
            "the_restless_ghost_skeleton_warlock",
            ticks=500,
            rng=lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
            stop_after_first_kill=True,
        )
        self.assertTrue(ok, result)
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "the_restless_ghost",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["inventory"]["Ghostspeak amulet"], 1)

        player_data, ok = start_quest_pure(player_data, "priest_in_peril", QUEST_DATA)
        self.assertTrue(ok)
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "priest_in_peril",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        for encounter_id in (
            "priest_in_peril_temple_guardian_dog_30",
            "priest_in_peril_monk_of_zamorak_30",
        ):
            if encounter_id.endswith("monk_of_zamorak_30"):
                for _ in range(2):
                    player_data, ok, completed_now = apply_quest_progress_pure(
                        player_data,
                        "priest_in_peril",
                        QUEST_DATA,
                    )
                    self.assertTrue(ok)
                    self.assertFalse(completed_now)
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "priest_in_peril",
                QUEST_DATA,
                encounter_id,
                ticks=500,
                rng=lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "priest_in_peril",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "priest_in_peril",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        player_data["inventory"]["Bucket"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "priest_in_peril",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        player_data["inventory"]["Pure essence"] = 25
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "priest_in_peril",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)

        player_data["inventory"]["Silver sickle"] = 1
        player_data, ok = start_quest_pure(player_data, "nature_spirit", QUEST_DATA)
        self.assertTrue(ok)
        self.assertNotIn("nature_spirit", player_data["quest_stage_actions"])
        for expected_progress in range(2, 6):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "nature_spirit",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"]["nature_spirit"]["progress"], expected_progress)
        self.assertNotIn("Washing bowl", player_data["inventory"])
        self.assertNotIn("Mirror", player_data["inventory"])

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "nature_spirit",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Silver sickle"], 0)
        self.assertEqual(player_data["inventory"]["Silver sickle (b)"], 1)
        self.assertEqual(player_data["inventory"]["Druid pouch"], 1)
        self.assertEqual(player_data["quests"]["nature_spirit"]["progress"], 6)

        for completed_quantity in range(1, 4):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "nature_spirit",
                QUEST_DATA,
                "nature_spirit_ghast_30",
                ticks=500,
                rng=lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            self.assertEqual(result["completed_quantity"], completed_quantity)

        completed, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "nature_spirit",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(completed["quests"]["nature_spirit"]["completed"])
        self.assertEqual(completed["inventory"]["Apple pie"], 3)
        self.assertEqual(completed["quest_points"], 4)
        self.assertEqual(
            completed["quest_stage_actions"]["nature_spirit"][-4:],
            [
                "Operate the sickle in the swamp next to bushes, logs, or twigs.",
                "Collect what grows and fill the Druid pouch with them.",
                "Wander around until a Ghast attacks and kill it. (Or you could use the Druid pouch on the ghast, allowing them to be attacked)",
                "Kill a total of three ghasts and return to Filliman.",
            ],
        )

    def test_fairy_tale_i_completes_from_normal_prerequisite_progression(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        for skill_id in (
            "attack",
            "strength",
            "defense",
            "constitution",
            "ranged",
            "magic",
            "prayer",
            "crafting",
            "woodcutting",
            "farming",
            "herblore",
            "thieving",
        ):
            player_data[f"{skill_id}_level"] = 99
        player_data["combat_lifepoints"] = 990
        player_data["inventory"].update({"Bronze hatchet": 1, "Knife": 1})

        def advance(quest_id, count=1):
            nonlocal player_data
            completed_now = False
            for _ in range(count):
                player_data, ok, completed_now = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                self.assertTrue(ok)
            return completed_now

        def fight(quest_id, encounter_id):
            nonlocal player_data
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                quest_id,
                QUEST_DATA,
                encounter_id,
                ticks=500,
                rng=lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            self.assertEqual(result["reason"], "combat_resolved")
            return result

        player_data, ok = start_quest_pure(player_data, "lost_city", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(advance("lost_city", 2))
        player_data["equipment"].update({"weapon": "Rune sword", "shield": "Rune kiteshield"})
        fight("lost_city", "lost_city_tree_spirit")
        self.assertFalse(advance("lost_city", 2))
        self.assertTrue(advance("lost_city"))
        self.assertEqual(player_data["inventory"]["Dramen staff"], 1)

        player_data, ok = start_quest_pure(player_data, "the_restless_ghost", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(advance("the_restless_ghost", 3))
        fight("the_restless_ghost", "the_restless_ghost_skeleton_warlock")
        self.assertTrue(advance("the_restless_ghost"))

        player_data, ok = start_quest_pure(player_data, "priest_in_peril", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(advance("priest_in_peril"))
        fight("priest_in_peril", "priest_in_peril_temple_guardian_dog_30")
        self.assertFalse(advance("priest_in_peril", 3))
        fight("priest_in_peril", "priest_in_peril_monk_of_zamorak_30")
        self.assertFalse(advance("priest_in_peril", 2))
        player_data["inventory"]["Bucket"] = 1
        self.assertFalse(advance("priest_in_peril"))
        player_data["inventory"]["Pure essence"] = 25
        self.assertTrue(advance("priest_in_peril"))

        player_data["inventory"]["Silver sickle"] = 1
        player_data, ok = start_quest_pure(player_data, "nature_spirit", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(advance("nature_spirit", 5))
        for expected_quantity in range(1, 4):
            result = fight("nature_spirit", "nature_spirit_ghast_30")
            self.assertEqual(result["completed_quantity"], expected_quantity)
        self.assertTrue(advance("nature_spirit"))

        player_data["inventory"].update({"Secateurs": 1, "Spade": 1})
        player_data, ok = start_quest_pure(
            player_data,
            "a_fairy_tale_i_growing_pains",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertNotIn("a_fairy_tale_i_growing_pains", player_data["quest_stage_actions"])
        self.assertFalse(advance("a_fairy_tale_i_growing_pains", 2))
        self.assertEqual(player_data["inventory"]["Dramen staff"], 1)
        self.assertFalse(advance("a_fairy_tale_i_growing_pains"))
        self.assertEqual(player_data["inventory"]["Secateurs"], 0)
        self.assertEqual(player_data["inventory"]["Magic secateurs"], 1)
        player_data["inventory"]["Magic secateurs"] = 0
        player_data["equipment"]["weapon"] = "Magic secateurs"

        result = fight(
            "a_fairy_tale_i_growing_pains",
            "a_fairy_tale_i_growing_pains_tanglefoot_111",
        )
        self.assertEqual(result["completed_quantity"], 1)
        self.assertEqual(player_data["inventory"]["Queen's secateurs"], 1)
        self.assertFalse(advance("a_fairy_tale_i_growing_pains"))
        self.assertTrue(advance("a_fairy_tale_i_growing_pains"))

        self.assertTrue(player_data["quests"]["a_fairy_tale_i_growing_pains"]["completed"])
        self.assertEqual(player_data["inventory"]["Queen's secateurs"], 0)
        self.assertEqual(player_data["inventory"]["Magic secateurs"], 0)
        self.assertEqual(player_data["equipment"]["weapon"], "Magic secateurs")
        self.assertEqual(player_data["quest_points"], 9)
        self.assertTrue(
            can_start_quest_pure(
                player_data,
                "a_fairy_tale_ii_cure_a_queen",
                QUEST_DATA,
            )
        )
        self.assertEqual(
            player_data["quest_stage_actions"]["a_fairy_tale_i_growing_pains"],
            [
                "Martin thinks fairies may be responsible. I should ask the Fairy Godfather in Zanaris.",
                "Zandar Horfyre sent me to Malignius Mortifer near Port Sarim.",
                "Malignius will tell you to go ask the Nature Spirit to perform the spell 'Phasma Phasmatis Natura' on an ordinary secateurs, along with three or four specific items.",
                "Nature Spirit enchanted my secateurs. I must enter the shady grove and defeat the Tanglefoot.",
                "I have the Queen's secateurs. I should return them to the Fairy Godfather.",
            ],
        )

    def test_source_backed_starter_quests_progress_through_stage_gates(self):
        cook = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        cook["quests"]["cooks_assistant"] = {"started": True, "progress": 1, "completed": False}
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(cook, "cooks_assistant", QUEST_DATA),
            (),
        )
        cook, ok, completed_now = apply_quest_progress_pure(cook, "cooks_assistant", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(cook["quests"]["cooks_assistant"]["progress"], 2)
        self.assertEqual(cook["inventory"]["Super large egg"], 1)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(cook, "cooks_assistant", QUEST_DATA),
            ("Needs Bucket x1",),
        )
        cook["inventory"]["Bucket"] = 1
        cook, ok, completed_now = apply_quest_progress_pure(cook, "cooks_assistant", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(cook["quests"]["cooks_assistant"]["progress"], 3)
        self.assertEqual(cook["inventory"]["Bucket"], 0)
        self.assertEqual(cook["inventory"]["Top-quality milk"], 1)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(cook, "cooks_assistant", QUEST_DATA),
            ("Needs Empty pot x1",),
        )
        cook["inventory"]["Empty pot"] = 1
        cook, ok, completed_now = apply_quest_progress_pure(cook, "cooks_assistant", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(cook["quests"]["cooks_assistant"]["progress"], 4)
        self.assertEqual(cook["inventory"]["Empty pot"], 0)
        self.assertEqual(cook["inventory"]["Extra fine flour"], 1)
        cook, ok, completed_now = apply_quest_progress_pure(cook, "cooks_assistant", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(cook["inventory"]["Top-quality milk"], 0)
        self.assertEqual(cook["inventory"]["Extra fine flour"], 0)
        self.assertEqual(cook["inventory"]["Super large egg"], 0)
        self.assertEqual(cook["inventory"]["Coins"], 500)
        self.assertEqual(cook["inventory"]["Sardine"], 20)
        self.assertEqual(cook["cooking_exp"], 300.0)

        imp = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        imp["quests"]["imp_catcher"] = {"started": True, "progress": 1, "completed": False}
        imp["inventory"].update({"Black bead": 1, "Red bead": 1, "White bead": 1, "Yellow bead": 1})
        imp, ok, completed_now = apply_quest_progress_pure(imp, "imp_catcher", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(imp["inventory"]["Black bead"], 0)
        self.assertEqual(imp["inventory"]["Red bead"], 0)
        self.assertEqual(imp["inventory"]["White bead"], 0)
        self.assertEqual(imp["inventory"]["Yellow bead"], 0)
        self.assertEqual(imp["inventory"]["Amulet of accuracy"], 1)
        self.assertEqual(imp["inventory"]["Coins"], 0)
        self.assertEqual(imp["magic_exp"], 875.0)
        self.assertEqual(imp["pending_skill_exp_rewards"], {})

        druidic = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        druidic["quests"]["druidic_ritual"] = {"started": True, "progress": 1, "completed": False}
        druidic["quest_stage_actions"] = {"druidic_ritual": ["Speak to Sanfew about the ritual ingredients"]}
        druidic, ok, completed_now = apply_quest_progress_pure(druidic, "druidic_ritual", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(druidic["quests"]["druidic_ritual"]["progress"], 2)
        druidic["inventory"].update({"Raw bear meat": 1, "Raw rat meat": 1, "Raw beef": 1, "Raw chicken": 1})
        druidic["quest_stage_actions"]["druidic_ritual"].append("Dip the raw meats in the Cauldron of Thunder")
        druidic, ok, completed_now = apply_quest_progress_pure(druidic, "druidic_ritual", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(druidic["inventory"]["Raw bear meat"], 0)
        self.assertEqual(druidic["inventory"]["Raw rat meat"], 0)
        self.assertEqual(druidic["inventory"]["Raw beef"], 0)
        self.assertEqual(druidic["inventory"]["Raw chicken"], 0)
        self.assertEqual(druidic["inventory"]["Enchanted bear meat"], 1)
        self.assertEqual(druidic["inventory"]["Enchanted rat meat"], 1)
        self.assertEqual(druidic["inventory"]["Enchanted beef"], 1)
        self.assertEqual(druidic["inventory"]["Enchanted chicken"], 1)
        druidic["quest_stage_actions"]["druidic_ritual"].append("Give Sanfew the enchanted meats and return to Kaqemeex")
        druidic, ok, completed_now = apply_quest_progress_pure(druidic, "druidic_ritual", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(druidic["inventory"]["Enchanted bear meat"], 0)
        self.assertEqual(druidic["inventory"]["Enchanted rat meat"], 0)
        self.assertEqual(druidic["inventory"]["Enchanted beef"], 0)
        self.assertEqual(druidic["inventory"]["Enchanted chicken"], 0)
        self.assertEqual(druidic["quest_points"], 4)
        # Herblore is now implemented, so the Druidic Ritual reward lands on
        # herblore_exp directly and nothing is left pending.
        self.assertEqual(druidic["herblore_exp"], 250.0)
        self.assertEqual(druidic["pending_skill_exp_rewards"], {})

        vampyre = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        vampyre, ok = start_quest_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(vampyre["current_quest"], "vampyre_slayer")
        self.assertNotIn("vampyre_slayer", vampyre["quest_stage_actions"])
        blockers = quest_current_stage_blockers_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertEqual(blockers, ())
        vampyre, ok, completed_now = apply_quest_progress_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(vampyre["quest_stage_actions"]["vampyre_slayer"], ["Speak to Dr Harlow at the Blue Moon Inn"])
        blockers = quest_current_stage_blockers_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertEqual(blockers, ())
        vampyre, ok, completed_now = apply_quest_progress_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(
            vampyre["quest_stage_actions"]["vampyre_slayer"],
            ["Speak to Dr Harlow at the Blue Moon Inn", "Buy Dr Harlow a beer at the Blue Moon Inn"],
        )
        self.assertEqual(vampyre["inventory"].get("Beer", 0), 0)
        self.assertEqual(vampyre["inventory"]["Stake"], 1)
        self.assertEqual(vampyre["inventory"]["Stake hammer"], 1)
        blockers = quest_current_stage_blockers_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_locked",))
        vampyre.update(
            {
                "quest_combat_config": {"resolver_enabled": True},
                "attack_level": 40,
                "strength_level": 40,
                "defense_level": 35,
                "constitution_level": 40,
                "prayer_level": 20,
            }
        )
        blockers = quest_current_stage_blockers_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        vampyre, ok, result = apply_quest_combat_encounter_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "vampyre_slayer_count_draynor_37")
        self.assertEqual(vampyre["quests"]["vampyre_slayer"]["progress"], 3)
        vampyre, ok, completed_now = apply_quest_progress_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(vampyre["inventory"]["Stake"], 0)
        self.assertEqual(vampyre["quests"]["vampyre_slayer"]["progress"], 4)
        attack_before_reward = vampyre["attack_exp"]
        vampyre, ok, completed_now = apply_quest_progress_pure(vampyre, "vampyre_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(vampyre["quests"]["vampyre_slayer"]["progress"], 5)
        self.assertEqual(
            vampyre["quest_stage_actions"]["vampyre_slayer"],
            [
                "Speak to Dr Harlow at the Blue Moon Inn",
                "Buy Dr Harlow a beer at the Blue Moon Inn",
                "Tell Morgan that Count Draynor is dead",
            ],
        )
        self.assertEqual(vampyre["quest_points"], 3)
        self.assertEqual(vampyre["attack_exp"] - attack_before_reward, 4825.0)
        self.assertEqual(vampyre["pending_skill_exp_rewards"], {})

    def test_pirates_treasure_real_stage_emitters_complete_and_reward_once(self):
        pirate = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        pirate, ok = start_quest_pure(pirate, "pirates_treasure", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(pirate["current_quest"], "pirates_treasure")
        self.assertNotIn("pirates_treasure", pirate["quest_stage_actions"])

        pirate["inventory"]["Karamja rum"] = 1
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(pirate, "pirates_treasure", QUEST_DATA),
            (),
        )
        pirate, ok, completed_now = apply_quest_progress_pure(pirate, "pirates_treasure", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(pirate["quests"]["pirates_treasure"]["progress"], 2)
        self.assertEqual(
            pirate["quest_stage_actions"]["pirates_treasure"],
            ["Smuggle Karamja rum off Karamja"],
        )
        self.assertEqual(pirate["inventory"]["Karamja rum"], 0)
        self.assertEqual(pirate["inventory"]["Chest key"], 1)

        pirate, ok, completed_now = apply_quest_progress_pure(pirate, "pirates_treasure", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(pirate["quests"]["pirates_treasure"]["progress"], 3)
        self.assertEqual(
            pirate["quest_stage_actions"]["pirates_treasure"],
            [
                "Smuggle Karamja rum off Karamja",
                "Open One-Eyed Hector's chest at the Blue Moon Inn",
            ],
        )
        self.assertEqual(pirate["inventory"]["Chest key"], 0)
        self.assertEqual(pirate["inventory"]["Pirate message"], 1)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(pirate, "pirates_treasure", QUEST_DATA),
            ("Needs Spade",),
        )

        pirate["inventory"]["Spade"] = 1
        pirate, ok, completed_now = apply_quest_progress_pure(pirate, "pirates_treasure", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(pirate["quests"]["pirates_treasure"]["progress"], 4)
        self.assertEqual(
            pirate["quest_stage_actions"]["pirates_treasure"],
            [
                "Smuggle Karamja rum off Karamja",
                "Open One-Eyed Hector's chest at the Blue Moon Inn",
                "Read the pirate message and dig in Falador Park",
            ],
        )
        self.assertEqual(pirate["inventory"]["Pirate message"], 1)
        self.assertEqual(pirate["inventory"]["Casket (Pirate's Treasure)"], 1)
        self.assertEqual(pirate["quest_points"], 2)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            pirate,
            "pirates_treasure",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["inventory"]["Casket (Pirate's Treasure)"], 1)
        self.assertEqual(after_complete["quest_points"], 2)

    def test_early_darkan_quests_progress_through_source_backed_stage_gates(self):
        goblin = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        goblin["quests"]["goblin_diplomacy"] = {"started": True, "progress": 1, "completed": False}
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(goblin, "goblin_diplomacy", QUEST_DATA),
            ("Needs Orange goblin mail x1",),
        )

        goblin["inventory"].update({"Orange goblin mail": 1, "Blue goblin mail": 1, "Goblin mail": 1})
        goblin, ok, completed_now = apply_quest_progress_pure(goblin, "goblin_diplomacy", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(goblin["inventory"]["Orange goblin mail"], 0)
        self.assertEqual(goblin["quests"]["goblin_diplomacy"]["progress"], 2)

        goblin, ok, completed_now = apply_quest_progress_pure(goblin, "goblin_diplomacy", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(goblin["inventory"]["Blue goblin mail"], 0)
        self.assertEqual(goblin["quests"]["goblin_diplomacy"]["progress"], 3)

        goblin, ok, completed_now = apply_quest_progress_pure(goblin, "goblin_diplomacy", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(goblin["inventory"]["Goblin mail"], 0)
        self.assertEqual(goblin["inventory"]["Gold bar"], 1)
        self.assertEqual(goblin["quest_points"], 5)
        self.assertEqual(goblin["crafting_exp"], 200.0)

        ernest = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        ernest, ok = start_quest_pure(ernest, "ernest_the_chicken", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(ernest["current_quest"], "ernest_the_chicken")
        self.assertNotIn("ernest_the_chicken", ernest["quest_stage_actions"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(ernest, "ernest_the_chicken", QUEST_DATA),
            (),
        )

        ernest, ok, completed_now = apply_quest_progress_pure(ernest, "ernest_the_chicken", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(ernest["quests"]["ernest_the_chicken"]["progress"], 2)
        self.assertEqual(
            ernest["quest_stage_actions"]["ernest_the_chicken"],
            ["Ask Professor Oddenstein about Ernest"],
        )

        ernest, ok, completed_now = apply_quest_progress_pure(ernest, "ernest_the_chicken", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(ernest["quests"]["ernest_the_chicken"]["progress"], 3)
        self.assertEqual(
            ernest["quest_stage_actions"]["ernest_the_chicken"],
            [
                "Ask Professor Oddenstein about Ernest",
                "Agree to retrieve Oddenstein's machine parts",
            ],
        )

        ernest["inventory"].update({"Fish food": 1, "Poison": 1, "Spade": 1})
        ernest, ok, completed_now = apply_quest_progress_pure(ernest, "ernest_the_chicken", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(ernest["inventory"]["Fish food"], 0)
        self.assertEqual(ernest["inventory"]["Poison"], 0)
        self.assertEqual(ernest["inventory"]["Poisoned fish food"], 1)

        ernest, ok, completed_now = apply_quest_progress_pure(ernest, "ernest_the_chicken", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(ernest["inventory"]["Poisoned fish food"], 0)
        self.assertEqual(ernest["inventory"]["Pressure gauge"], 1)

        ernest, ok, completed_now = apply_quest_progress_pure(ernest, "ernest_the_chicken", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(ernest["inventory"]["Grimy key"], 1)

        ernest, ok, completed_now = apply_quest_progress_pure(ernest, "ernest_the_chicken", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(ernest["inventory"]["Rubber tube"], 1)

        ernest, ok, completed_now = apply_quest_progress_pure(ernest, "ernest_the_chicken", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(ernest["inventory"]["Oil can"], 1)
        self.assertEqual(
            ernest["quest_stage_actions"]["ernest_the_chicken"],
            [
                "Ask Professor Oddenstein about Ernest",
                "Agree to retrieve Oddenstein's machine parts",
                "Solve the Draynor Manor basement lever puzzle",
            ],
        )

        ernest, ok, completed_now = apply_quest_progress_pure(ernest, "ernest_the_chicken", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(ernest["inventory"]["Pressure gauge"], 0)
        self.assertEqual(ernest["inventory"]["Rubber tube"], 0)
        self.assertEqual(ernest["inventory"]["Oil can"], 0)
        self.assertEqual(ernest["inventory"]["Coins"], 3000)
        self.assertEqual(ernest["inventory"]["Egg"], 10)
        self.assertEqual(ernest["inventory"]["Feather"], 300)

        black = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        black["quest_points"] = 11
        self.assertFalse(can_start_quest_pure(black, "black_knights_fortress", QUEST_DATA))
        self.assertEqual(quest_locked_reasons_pure(black, "black_knights_fortress", QUEST_DATA), ("12 quest points",))

        black["quest_points"] = 12
        black["equipment"] = {"body": "Iron chainbody", "head": "Bronze med helm"}
        black, ok = start_quest_pure(black, "black_knights_fortress", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(black["current_quest"], "black_knights_fortress")
        self.assertNotIn("black_knights_fortress", black["quest_stage_actions"])
        self.assertEqual(quest_current_stage_blockers_pure(black, "black_knights_fortress", QUEST_DATA), ())

        black, ok, completed_now = apply_quest_progress_pure(black, "black_knights_fortress", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(black["quests"]["black_knights_fortress"]["progress"], 2)
        self.assertEqual(
            black["quest_stage_actions"]["black_knights_fortress"],
            ["Infiltrate the Black Knights' Fortress"],
        )

        black, ok, completed_now = apply_quest_progress_pure(black, "black_knights_fortress", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(black["quests"]["black_knights_fortress"]["progress"], 3)
        self.assertEqual(
            black["quest_stage_actions"]["black_knights_fortress"],
            [
                "Infiltrate the Black Knights' Fortress",
                "Listen at the grill above the Black Knights' meeting",
            ],
        )

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(black, "black_knights_fortress", QUEST_DATA),
            ("Needs Cabbage x1",),
        )
        black["inventory"]["Cabbage"] = 1
        black, ok, completed_now = apply_quest_progress_pure(black, "black_knights_fortress", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(black["quests"]["black_knights_fortress"]["progress"], 4)
        self.assertEqual(black["inventory"]["Cabbage"], 0)

        black, ok, completed_now = apply_quest_progress_pure(black, "black_knights_fortress", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(
            black["quest_stage_actions"]["black_knights_fortress"],
            [
                "Infiltrate the Black Knights' Fortress",
                "Listen at the grill above the Black Knights' meeting",
                "Report the ruined potion to Sir Amik Varze",
            ],
        )
        self.assertEqual(black["quest_points"], 15)
        self.assertEqual(black["inventory"]["Coins"], 2500)

    def test_quest_combat_resolver_uses_player_and_source_backed_npc_stats(self):
        self.assertEqual(
            player_combat_level_pure(
                {
                    "attack_level": 40,
                    "strength_level": 40,
                    "defense_level": 35,
                    "constitution_level": 40,
                    "prayer_level": 20,
                    "summoning_level": 1,
                    "ranged_level": 1,
                    "magic_level": 1,
                }
            ),
            47,
        )
        quest_data = {
            "proof_quest": {
                "stages": 2,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "combat_encounters": (
                            {
                                "encounter_id": "count_draynor",
                                "display_name": "Count Draynor",
                                "level": 37,
                                "quantity": 1,
                                "npc_stats": {
                                    "hitpoints": 350,
                                    "attack": 30,
                                    "strength": 25,
                                    "defence": 30,
                                    "magic": 1,
                                    "ranged": 1,
                                },
                                "source": "2011Scape Count Draynor combat def",
                            },
                        ),
                        "source": "source",
                    },
                ),
            }
        }
        low_level = {
            "inventory": {},
            "quest_combat_config": {"resolver_enabled": True},
            "quests": {"proof_quest": {"started": True, "progress": 1, "completed": False}},
        }
        blockers = quest_current_stage_blockers_pure(low_level, "proof_quest", quest_data)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_underpowered",))
        self.assertFalse(can_attempt_quest_review_pure(low_level, "proof_quest", quest_data))

        ready = dict(low_level)
        ready.update(
            {
                "attack_level": 40,
                "strength_level": 40,
                "defense_level": 35,
                "constitution_level": 40,
                "prayer_level": 20,
            }
        )
        blockers = quest_current_stage_blockers_pure(ready, "proof_quest", quest_data)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["reason"], "Battle required: Count Draynor level 37")
        self.assertTrue(can_attempt_quest_review_pure(ready, "proof_quest", quest_data))

        resolved, ok, result = apply_quest_combat_encounter_pure(ready, "proof_quest", quest_data)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "count_draynor")
        self.assertEqual(resolved["quest_combat_encounters"], {"proof_quest": ["count_draynor"]})
        self.assertEqual(quest_current_stage_blockers_pure(resolved, "proof_quest", quest_data), ())

    def test_quest_combat_can_use_a_sourced_player_requirement_below_enemy_level(self):
        quest_data = {
            "proof_quest": {
                "stages": 2,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "combat_encounters": (
                            {
                                "encounter_id": "boss_111",
                                "display_name": "Boss",
                                "level": 111,
                                "npc_stats": {
                                    "hitpoints": 2220,
                                    "attack": 111,
                                    "strength": 111,
                                    "defence": 111,
                                    "magic": 111,
                                    "ranged": 1,
                                },
                                "npc_configs": {"minimum_player_combat": 85},
                                "source": "quest requires combat 85",
                            },
                        ),
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "quest_combat_config": {"resolver_enabled": True},
            "quests": {"proof_quest": {"started": True, "progress": 1, "completed": False}},
            "attack_level": 74,
            "strength_level": 74,
            "defense_level": 74,
            "constitution_level": 74,
            "prayer_level": 1,
            "summoning_level": 1,
            "ranged_level": 1,
            "magic_level": 1,
        }
        self.assertEqual(player_combat_level_pure(player_data), 85)
        blockers = quest_current_stage_blockers_pure(player_data, "proof_quest", quest_data)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["level"], 111)
        self.assertEqual(blockers[0]["minimum_player_combat"], 85)

        player_data["attack_level"] = 73
        blockers = quest_current_stage_blockers_pure(player_data, "proof_quest", quest_data)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_underpowered",))
        self.assertIn("Requires combat level 85", blockers[0]["reason"])

    def test_quest_combat_quantity_resolves_one_enemy_per_review(self):
        quest_data = {
            "proof_quest": {
                "stages": 2,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "combat_encounters": (
                            {
                                "encounter_id": "ice_giant",
                                "display_name": "Ice giant",
                                "level": 2,
                                "quantity": 2,
                                "npc_stats": {
                                    "hitpoints": 100,
                                    "attack": 1,
                                    "strength": 1,
                                    "defence": 1,
                                },
                                "source": "source",
                            },
                        ),
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "quest_combat_config": {"resolver_enabled": True},
            "quests": {"proof_quest": {"started": True, "progress": 1, "completed": False}},
            "attack_level": 10,
            "strength_level": 10,
            "defense_level": 10,
            "constitution_level": 10,
            "prayer_level": 1,
        }

        blockers = quest_current_stage_blockers_pure(player_data, "proof_quest", quest_data)
        self.assertEqual(blockers[0]["reason"], "Battle required: Ice giant level 2 x2")
        self.assertEqual(blockers[0]["quantity"], 2)
        self.assertEqual(blockers[0]["total_quantity"], 2)
        self.assertEqual(blockers[0]["completed_quantity"], 0)
        self.assertEqual(blockers[0]["remaining_quantity"], 2)

        first, ok, result = apply_quest_combat_encounter_pure(player_data, "proof_quest", quest_data)
        self.assertTrue(ok)
        self.assertEqual(result["quantity"], 1)
        self.assertEqual(result["total_quantity"], 2)
        self.assertEqual(result["completed_quantity"], 1)
        self.assertEqual(result["remaining_quantity"], 1)
        self.assertEqual(first["quest_combat_encounter_counts"], {"proof_quest": {"ice_giant": 1}})
        self.assertEqual(first["quest_combat_encounters"], {})
        blockers = quest_current_stage_blockers_pure(first, "proof_quest", quest_data)
        self.assertEqual(blockers[0]["reason"], "Battle required: Ice giant level 2")
        self.assertEqual(blockers[0]["quantity"], 1)
        self.assertEqual(blockers[0]["total_quantity"], 2)
        self.assertEqual(blockers[0]["completed_quantity"], 1)
        self.assertEqual(blockers[0]["remaining_quantity"], 1)

        second, ok, result = apply_quest_combat_encounter_pure(first, "proof_quest", quest_data)
        self.assertTrue(ok)
        self.assertEqual(result["completed_quantity"], 2)
        self.assertEqual(result["remaining_quantity"], 0)
        self.assertEqual(second["quest_combat_encounter_counts"], {"proof_quest": {"ice_giant": 2}})
        self.assertEqual(second["quest_combat_encounters"], {"proof_quest": ["ice_giant"]})
        self.assertEqual(quest_current_stage_blockers_pure(second, "proof_quest", quest_data), ())

        legacy = dict(player_data)
        legacy["quest_combat_encounters"] = {"proof_quest": ["ice_giant"]}
        self.assertEqual(quest_current_stage_blockers_pure(legacy, "proof_quest", quest_data), ())

    def test_quest_combat_partial_burst_preserves_ordinary_combat_encounter(self):
        quest_data = {
            "proof_quest": {
                "stages": 2,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "combat_encounters": (
                            {
                                "encounter_id": "training_dummy",
                                "display_name": "Training dummy",
                                "level": 1,
                                "quantity": 1,
                                "npc_stats": {
                                    "hitpoints": 1000,
                                    "attack": 1,
                                    "strength": 1,
                                    "defence": 1,
                                },
                                "source": "source",
                            },
                        ),
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "current_combat_target": "chicken",
            "combat_encounter": {"target_id": "chicken", "enemy_lifepoints": 10},
            "quest_combat_config": {"resolver_enabled": True},
            "quests": {"proof_quest": {"started": True, "progress": 1, "completed": False}},
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "constitution_level": 80,
            "prayer_level": 1,
            "combat_lifepoints": 800,
        }

        partial, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "proof_quest",
            quest_data,
            ticks=1,
            rng=lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
        )

        self.assertTrue(ok)
        self.assertFalse(result["killed"])
        self.assertGreater(result["player_damage"], 0)
        self.assertEqual(partial["current_combat_target"], "chicken")
        self.assertEqual(partial["combat_encounter"], {"target_id": "chicken", "enemy_lifepoints": 10})
        self.assertEqual(partial["quest_combat_encounters"], {})
        self.assertIn("training_dummy", partial["quest_combat_active_encounters"]["proof_quest"])
        self.assertLess(partial["quest_combat_active_encounters"]["proof_quest"]["training_dummy"], 1000)

        resolved, ok, result = apply_quest_combat_encounter_pure(
            partial,
            "proof_quest",
            quest_data,
            ticks=500,
            rng=lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(resolved["current_combat_target"], "chicken")
        self.assertEqual(resolved["combat_encounter"], {"target_id": "chicken", "enemy_lifepoints": 10})
        self.assertEqual(resolved["quest_combat_active_encounters"], {})
        self.assertEqual(resolved["quest_combat_encounters"], {"proof_quest": ["training_dummy"]})

    def test_quest_combat_guaranteed_drop_enters_inventory_after_real_kill(self):
        encounter = QuestCombatEncounter(
            encounter_id="synthetic_dropper",
            display_name="Synthetic dropper",
            level=1,
            npc_stats=(
                ("hitpoints", 10),
                ("attack", 1),
                ("strength", 1),
                ("defence", 1),
            ),
            guaranteed_drops=(("Herb pouch", 1),),
            source="synthetic regression",
        )
        quest_data = {
            "proof_quest": {
                "stages": 2,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "combat_encounters": (_combat_encounter_dict(encounter),),
                        "source": "synthetic regression",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "quest_combat_config": {"resolver_enabled": True},
            "quests": {"proof_quest": {"started": True, "progress": 1, "completed": False}},
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "constitution_level": 80,
            "prayer_level": 1,
            "combat_lifepoints": 800,
        }

        resolved, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "proof_quest",
            quest_data,
            ticks=50,
            rng=lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
            stop_after_first_kill=True,
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(resolved["inventory"].get("Herb pouch", 0), 1)

    def test_quest_combat_kill_does_not_increment_ordinary_combat_kill_counts(self):
        quest_data = {
            "proof_quest": {
                "stages": 2,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "combat_encounters": (
                            {
                                "encounter_id": "quest_dummy",
                                "display_name": "Quest dummy",
                                "level": 1,
                                "npc_stats": {
                                    "hitpoints": 10,
                                    "attack": 1,
                                    "strength": 1,
                                    "defence": 1,
                                },
                                "source": "source",
                            },
                        ),
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "combat_kill_counts": {"chicken": 3},
            "quest_combat_config": {"resolver_enabled": True},
            "quests": {"proof_quest": {"started": True, "progress": 1, "completed": False}},
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "constitution_level": 80,
            "prayer_level": 1,
            "combat_lifepoints": 800,
        }

        resolved, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "proof_quest",
            quest_data,
            ticks=50,
            rng=lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
        )

        self.assertTrue(ok)
        self.assertTrue(result["killed"])
        self.assertEqual(resolved["quest_combat_encounters"], {"proof_quest": ["quest_dummy"]})
        self.assertEqual(resolved["combat_kill_counts"], {"chicken": 3})

    def test_quest_combat_death_clears_ordinary_combat_encounter(self):
        rolls = iter((0.999999, 0.0, 0.999999))
        quest_data = {
            "proof_quest": {
                "stages": 2,
                "stage_requirements": (
                    {
                        "stage": 1,
                        "combat_encounters": (
                            {
                                "encounter_id": "quest_killer",
                                "display_name": "Quest killer",
                                "level": 1,
                                "npc_stats": {
                                    "hitpoints": 1000,
                                    "attack": 99,
                                    "strength": 99,
                                    "defence": 99,
                                },
                                "npc_configs": {"attack_speed": 1, "max_hit": 100},
                                "source": "source",
                            },
                        ),
                        "source": "source",
                    },
                ),
            }
        }
        player_data = {
            "inventory": {},
            "equipment": {"weapon": "Iron sword"},
            "current_combat_target": "chicken",
            "combat_encounter": {"target_id": "chicken", "enemy_lifepoints": 10},
            "quest_combat_config": {"resolver_enabled": True},
            "quests": {"proof_quest": {"started": True, "progress": 1, "completed": False}},
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 1,
            "constitution_level": 10,
            "prayer_level": 1,
            "combat_lifepoints": 10,
        }

        defeated, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "proof_quest",
            quest_data,
            ticks=3,
            rng=lambda: next(rolls, 0.999999),
            equipment_data=EQUIPMENT_DATA,
        )

        self.assertTrue(ok)
        self.assertTrue(result["died"])
        self.assertEqual(defeated["current_combat_target"], "chicken")
        self.assertEqual(defeated["combat_encounter"], {})
        self.assertEqual(defeated["equipment"], {})
        self.assertEqual(defeated["combat_grave"]["items"], ["Iron sword"])
        self.assertEqual(defeated["quest_combat_encounters"], {})

    def test_quest_combat_stats_are_style_aware_for_magic_and_ranged_enemies(self):
        magic_encounter = {
            "npc_stats": {
                "hitpoints": 350,
                "attack": 0,
                "strength": 0,
                "defence": 30,
                "magic": 30,
                "ranged": 1,
            },
            "npc_configs": {"attack_style": "magic"},
        }
        ranged_encounter = {
            "npc_stats": {
                "hitpoints": 450,
                "attack": 0,
                "strength": 0,
                "defence": 29,
                "magic": 0,
                "ranged": 66,
            },
            "npc_configs": {"attack_style": "range"},
        }
        incomplete_melee = {
            "npc_stats": {
                "hitpoints": 8000,
                "attack": 0,
                "strength": 0,
                "defence": 180,
                "magic": 180,
                "ranged": 0,
            },
            "npc_configs": {"attack_style": "melee", "max_hit": 180},
        }
        explicit_zero_melee = {
            "npc_stats": {
                "hitpoints": 450,
                "attack": 0,
                "strength": 0,
                "defence": 0,
                "magic": 0,
                "ranged": 0,
            },
            "npc_configs": {"attack_style": "melee", "max_hit": 30},
        }

        self.assertTrue(quest_combat_encounter_has_stats_pure(magic_encounter))
        self.assertTrue(quest_combat_encounter_has_stats_pure(ranged_encounter))
        self.assertFalse(quest_combat_encounter_has_stats_pure(incomplete_melee))
        self.assertTrue(quest_combat_encounter_has_stats_pure(explicit_zero_melee))

    def test_beast_stat_fallback_ranged_rows_are_resolver_ready(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["toktz_ket_dill"] = {"started": True, "progress": 6, "completed": False}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 50
        player_data["strength_level"] = 50
        player_data["defense_level"] = 50
        player_data["constitution_level"] = 50
        player_data["prayer_level"] = 1

        blockers = quest_current_stage_blockers_pure(player_data, "toktz_ket_dill", QUEST_DATA)
        self.assertEqual(
            tuple(blocker["kind"] for blocker in blockers),
            ("required_action", "combat_missing_stats", "combat_encounter", "combat_missing_stats"),
        )
        self.assertEqual(blockers[2]["reason"], "Battle required: Lava monster level 47 x2")
        self.assertEqual(blockers[2]["quantity"], 2)
        self.assertEqual(blockers[2]["total_quantity"], 2)
        self.assertEqual(
            tuple(blocker["encounter_id"] for blocker in quest_current_stage_resolvable_combat_blockers_pure(player_data, "toktz_ket_dill", QUEST_DATA)),
            ("toktz_ket_dill_lava_monster_47",),
        )
        self.assertTrue(can_attempt_quest_review_pure(player_data, "toktz_ket_dill", QUEST_DATA))

        first, ok, result = apply_quest_combat_encounter_pure(player_data, "toktz_ket_dill", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "toktz_ket_dill_lava_monster_47")
        self.assertEqual(result["completed_quantity"], 1)
        self.assertEqual(result["remaining_quantity"], 1)
        self.assertEqual(first["quest_combat_encounter_counts"], {"toktz_ket_dill": {"toktz_ket_dill_lava_monster_47": 1}})
        self.assertEqual(first["quest_combat_encounters"], {})
        blockers = quest_current_stage_blockers_pure(first, "toktz_ket_dill", QUEST_DATA)
        self.assertEqual(
            tuple(blocker["kind"] for blocker in blockers),
            ("required_action", "combat_missing_stats", "combat_encounter", "combat_missing_stats"),
        )
        self.assertEqual(blockers[2]["reason"], "Battle required: Lava monster level 47")

        resolved, ok, result = apply_quest_combat_encounter_pure(first, "toktz_ket_dill", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["completed_quantity"], 2)
        self.assertEqual(result["remaining_quantity"], 0)
        self.assertEqual(resolved["quest_combat_encounters"], {"toktz_ket_dill": ["toktz_ket_dill_lava_monster_47"]})
        self.assertEqual(
            tuple(blocker["kind"] for blocker in quest_current_stage_blockers_pure(resolved, "toktz_ket_dill", QUEST_DATA)),
            ("required_action", "combat_missing_stats", "combat_missing_stats"),
        )

    def test_another_slice_ham_magic_fight_is_resolver_ready(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["another_slice_of_h_a_m"] = {"started": True, "progress": 4, "completed": False}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["quest_combat_encounters"] = {"another_slice_of_h_a_m": ["another_slice_of_h_a_m_sigmund_64"]}
        player_data["attack_level"] = 40
        player_data["strength_level"] = 40
        player_data["defense_level"] = 40
        player_data["constitution_level"] = 40

        blockers = quest_current_stage_blockers_pure(player_data, "another_slice_of_h_a_m", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("required_action", "combat_encounter", "combat_encounter"))
        self.assertEqual(blockers[1]["reason"], "Battle required: H.A.M. mage level 30")
        self.assertEqual(blockers[2]["reason"], "Battle required: H.A.M. ranger level 30")

        resolved, ok, result = apply_quest_combat_encounter_pure(player_data, "another_slice_of_h_a_m", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "another_slice_of_h_a_m_h_a_m_mage_30")
        self.assertEqual(
            resolved["quest_combat_encounters"],
            {
                "another_slice_of_h_a_m": [
                    "another_slice_of_h_a_m_h_a_m_mage_30",
                    "another_slice_of_h_a_m_sigmund_64",
                ]
            },
        )
        self.assertEqual(
            tuple(blocker["reason"] for blocker in quest_current_stage_blockers_pure(resolved, "another_slice_of_h_a_m", QUEST_DATA)),
            (
                "Action required: Complete Another Slice of H.A.M. stage 4 objective",
                "Battle required: H.A.M. ranger level 30",
            ),
        )

    def test_spirits_of_the_elid_golems_are_split_into_named_combat_gates(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["spirits_of_the_elid"] = {"started": True, "progress": 4, "completed": False}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 90
        player_data["strength_level"] = 90
        player_data["defense_level"] = 90
        player_data["constitution_level"] = 90

        blockers = quest_current_stage_blockers_pure(player_data, "spirits_of_the_elid", QUEST_DATA)
        self.assertEqual(
            tuple(blocker["reason"] for blocker in blockers),
            (
                "Action required: Complete Spirits of the Elid stage 4 objective",
                "Battle required: Black golem level 75",
                "Battle required: White golem level 75",
                "Battle required: Grey golem level 75",
            ),
        )
        self.assertEqual(
            tuple(
                blocker["encounter_id"]
                for blocker in quest_current_stage_resolvable_combat_blockers_pure(
                    player_data,
                    "spirits_of_the_elid",
                    QUEST_DATA,
                )
            ),
            (
                "spirits_of_the_elid_black_golem_75",
                "spirits_of_the_elid_white_golem_75",
                "spirits_of_the_elid_grey_golem_75",
            ),
        )
        self.assertTrue(can_attempt_quest_review_pure(player_data, "spirits_of_the_elid", QUEST_DATA))

        resolved, ok, result = apply_quest_combat_encounter_pure(player_data, "spirits_of_the_elid", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "spirits_of_the_elid_black_golem_75")
        self.assertEqual(
            resolved["quest_combat_encounters"],
            {"spirits_of_the_elid": ["spirits_of_the_elid_black_golem_75"]},
        )
        self.assertEqual(
            tuple(blocker["reason"] for blocker in quest_current_stage_blockers_pure(resolved, "spirits_of_the_elid", QUEST_DATA)),
            (
                "Action required: Complete Spirits of the Elid stage 4 objective",
                "Battle required: White golem level 75",
                "Battle required: Grey golem level 75",
            ),
        )

    def test_a_souls_bane_real_stage_emitter_completes_and_rewards_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        for level_key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
        ):
            player_data[level_key] = 100
        player_data, ok = start_quest_pure(player_data, "a_souls_bane", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "a_souls_bane")
        self.assertNotIn("a_souls_bane", player_data["quest_stage_actions"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(
                player_data,
                "a_souls_bane",
                QUEST_DATA,
            ),
            ("Needs Rope x1",),
        )

        player_data["inventory"]["Rope"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "a_souls_bane",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["a_souls_bane"]["progress"], 2)
        self.assertNotIn("a_souls_bane", player_data["quest_stage_actions"])

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "a_souls_bane",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["a_souls_bane"]["progress"], 3)
        self.assertEqual(
            player_data["quest_stage_actions"]["a_souls_bane"],
            ["Fill the rage meter with an anger weapon"],
        )

        stage_three_encounters = (
            *("a_souls_bane_fear_reaper_42",) * 5,
            *("a_souls_bane_confusion_beast_43",) * 5,
            *("a_souls_bane_hopeless_creature_40",) * 3,
        )
        for expected_encounter in stage_three_encounters:
            blockers = quest_current_stage_resolvable_combat_blockers_pure(
                player_data,
                "a_souls_bane",
                QUEST_DATA,
            )
            self.assertEqual(blockers[0]["encounter_id"], expected_encounter)
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "a_souls_bane",
                QUEST_DATA,
                expected_encounter,
                ticks=500,
                rng=lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            self.assertTrue(result["killed"], result)
            self.assertEqual(result["encounter_id"], expected_encounter)

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(
                player_data,
                "a_souls_bane",
                QUEST_DATA,
            ),
            (),
        )
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "a_souls_bane",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["a_souls_bane"]["progress"], 4)

        for _ in range(3):
            blockers = quest_current_stage_resolvable_combat_blockers_pure(
                player_data,
                "a_souls_bane",
                QUEST_DATA,
            )
            self.assertEqual(
                blockers[0]["encounter_id"],
                "a_souls_bane_tolna_head_46",
            )
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "a_souls_bane",
                QUEST_DATA,
                "a_souls_bane_tolna_head_46",
                ticks=500,
                rng=lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            self.assertTrue(result["killed"], result)

        pre_reward_constitution_exp = player_data["constitution_exp"]
        pre_reward_defense_exp = player_data["defense_exp"]
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "a_souls_bane",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["a_souls_bane"]["completed"])
        self.assertEqual(player_data["quests"]["a_souls_bane"]["progress"], 5)
        self.assertEqual(player_data["inventory"]["Coins"], 500)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(
            player_data["constitution_exp"],
            pre_reward_constitution_exp + 500.0,
        )
        self.assertEqual(
            player_data["defense_exp"],
            pre_reward_defense_exp + 500.0,
        )
        rewarded_constitution_exp = player_data["constitution_exp"]
        rewarded_defense_exp = player_data["defense_exp"]

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "a_souls_bane",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["inventory"]["Coins"], 500)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(
            after_complete["constitution_exp"],
            rewarded_constitution_exp,
        )
        self.assertEqual(after_complete["defense_exp"], rewarded_defense_exp)

    def test_death_to_dorgeshuun_senior_guards_are_multi_count_resolver_ready(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"].update({"Pickaxe": 1})
        player_data["quests"]["death_to_the_dorgeshuun"] = {"started": True, "progress": 5, "completed": False}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["quest_combat_encounters"] = {"death_to_the_dorgeshuun": ["death_to_the_dorgeshuun_sigmund_50"]}
        player_data["attack_level"] = 100
        player_data["strength_level"] = 100
        player_data["defense_level"] = 100
        player_data["constitution_level"] = 100

        blockers = quest_current_stage_blockers_pure(player_data, "death_to_the_dorgeshuun", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["reason"], "Battle required: Senior H.A.M. guard level 22 x3")
        self.assertTrue(can_attempt_quest_review_pure(player_data, "death_to_the_dorgeshuun", QUEST_DATA))

        first, ok, result = apply_quest_combat_encounter_pure(player_data, "death_to_the_dorgeshuun", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "death_to_the_dorgeshuun_senior_ham_guard_22")
        self.assertEqual(result["completed_quantity"], 1)
        self.assertEqual(result["remaining_quantity"], 2)
        self.assertEqual(
            first["quest_combat_encounter_counts"],
            {"death_to_the_dorgeshuun": {"death_to_the_dorgeshuun_senior_ham_guard_22": 1}},
        )
        self.assertEqual(
            first["quest_combat_encounters"],
            {"death_to_the_dorgeshuun": ["death_to_the_dorgeshuun_sigmund_50"]},
        )

    def test_no_combat_levels_beast_stat_fight_is_resolver_ready(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["forgiveness_of_a_chaos_dwarf"] = {"started": True, "progress": 4, "completed": False}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 80
        player_data["strength_level"] = 80
        player_data["defense_level"] = 80
        player_data["constitution_level"] = 80
        player_data["prayer_level"] = 80

        blockers = quest_current_stage_blockers_pure(player_data, "forgiveness_of_a_chaos_dwarf", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["reason"], "Battle required: Chaos dwarf hand cannoneer level 100")
        self.assertTrue(can_attempt_quest_review_pure(player_data, "forgiveness_of_a_chaos_dwarf", QUEST_DATA))

        resolved, ok, result = apply_quest_combat_encounter_pure(player_data, "forgiveness_of_a_chaos_dwarf", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "forgiveness_of_a_chaos_dwarf_chaos_dwarf_hand_cannoneer_100")
        self.assertEqual(
            resolved["quest_combat_encounters"],
            {"forgiveness_of_a_chaos_dwarf": ["forgiveness_of_a_chaos_dwarf_chaos_dwarf_hand_cannoneer_100"]},
        )
        self.assertEqual(quest_current_stage_blockers_pure(resolved, "forgiveness_of_a_chaos_dwarf", QUEST_DATA), ())

    def test_restless_ghost_skeleton_warlock_override_is_resolver_ready(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"]["Muddy skull"] = 1
        player_data["quests"]["the_restless_ghost"] = {"started": True, "progress": 4, "completed": False}
        player_data["quest_stage_actions"] = {"the_restless_ghost": ["Return the muddy skull to the ghost's coffin"]}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 20
        player_data["strength_level"] = 20
        player_data["defense_level"] = 20
        player_data["constitution_level"] = 20

        blockers = quest_current_stage_blockers_pure(player_data, "the_restless_ghost", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["reason"], "Battle required: Skeleton warlock level 11")
        self.assertTrue(can_attempt_quest_review_pure(player_data, "the_restless_ghost", QUEST_DATA))

        resolved, ok, result = apply_quest_combat_encounter_pure(player_data, "the_restless_ghost", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "the_restless_ghost_skeleton_warlock")
        self.assertEqual(
            resolved["quest_combat_encounters"],
            {"the_restless_ghost": ["the_restless_ghost_skeleton_warlock"]},
        )
        self.assertEqual(quest_current_stage_blockers_pure(resolved, "the_restless_ghost", QUEST_DATA), ())

    def test_restless_ghost_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "the_restless_ghost"
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 20
        player_data["strength_level"] = 20
        player_data["defense_level"] = 20
        player_data["constitution_level"] = 20

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_steps = (
            (
                2,
                ("Receive the ghostspeak amulet from Father Urhney",),
                {"Ghostspeak amulet": 1, "Muddy skull": 0},
            ),
            (
                3,
                (
                    "Receive the ghostspeak amulet from Father Urhney",
                    "Speak to the restless ghost",
                ),
                {"Ghostspeak amulet": 1, "Muddy skull": 0},
            ),
            (
                4,
                (
                    "Receive the ghostspeak amulet from Father Urhney",
                    "Speak to the restless ghost",
                    "Search the mining spot for the ghost's skull",
                ),
                {"Ghostspeak amulet": 1, "Muddy skull": 1},
            ),
        )
        for progress, actions, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"][quest_id]),
                actions,
            )
            self.assertEqual(
                {
                    item_name: player_data["inventory"].get(item_name, 0)
                    for item_name in inventory
                },
                inventory,
            )

        blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["encounter_id"], "the_restless_ghost_skeleton_warlock")

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
            rng=lambda: 0.5,
        )
        self.assertTrue(ok)
        self.assertEqual(result["reason"], "combat_resolved")
        self.assertEqual(
            player_data["quest_combat_encounters"],
            {quest_id: ["the_restless_ghost_skeleton_warlock"]},
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 5)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            (
                "Receive the ghostspeak amulet from Father Urhney",
                "Speak to the restless ghost",
                "Search the mining spot for the ghost's skull",
                "Return the muddy skull to the ghost's coffin",
            ),
        )
        self.assertEqual(player_data["inventory"].get("Muddy skull", 0), 0)
        self.assertEqual(player_data["inventory"]["Ancient bones"], 5)
        self.assertEqual(player_data["prayer_exp"], 125.0)
        self.assertEqual(player_data["quest_points"], 1)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["inventory"]["Ancient bones"], 5)
        self.assertEqual(after_complete["prayer_exp"], 125.0)
        self.assertEqual(after_complete["quest_points"], 1)

    def test_stolen_hearts_stage_chain_resolves_combat_items_and_exact_rewards(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["stolen_hearts"] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 99
        player_data["strength_level"] = 99
        player_data["defense_level"] = 99
        player_data["constitution_level"] = 99
        player_data["ranged_level"] = 99
        player_data["magic_level"] = 99
        player_data["prayer_level"] = 99

        for expected_progress in (2, 3):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "stolen_hearts",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(
                player_data["quests"]["stolen_hearts"]["progress"],
                expected_progress,
            )

        blockers = quest_current_stage_blockers_pure(
            player_data,
            "stolen_hearts",
            QUEST_DATA,
        )
        self.assertEqual(
            tuple(blocker["reason"] for blocker in blockers),
            (
                "Battle required: Mercenary Joe level 2",
                "Battle required: Skulls mercenary level 2 x2",
            ),
        )

        for expected_encounter in (
            "stolen_hearts_mercenary_joe",
            "stolen_hearts_skulls_mercenary",
            "stolen_hearts_skulls_mercenary",
        ):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "stolen_hearts",
                QUEST_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            self.assertEqual(result["encounter_id"], expected_encounter)
            self.assertTrue(result["killed"])

        for expected_progress in (4, 5):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "stolen_hearts",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(
                player_data["quests"]["stolen_hearts"]["progress"],
                expected_progress,
            )
            self.assertFalse(completed_now)

        constitution_before_reward = player_data["constitution_exp"]
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "stolen_hearts",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quests"]["stolen_hearts"]["progress"], 6)

        self.assertTrue(player_data["quests"]["stolen_hearts"]["completed"])
        self.assertEqual(player_data["inventory"]["Coins"], 2500)
        self.assertEqual(player_data["inventory"].get("Ransom note", 0), 0)
        self.assertEqual(player_data["inventory"].get("History of the Kharid-ib", 0), 0)
        self.assertEqual(
            player_data["constitution_exp"],
            constitution_before_reward + 250,
        )
        self.assertNotIn("combat_exp", player_data["pending_skill_exp_rewards"])

    def test_diamond_in_the_rough_stage_chain_resolves_two_fights_and_exact_rewards(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["stolen_hearts"] = {
            "started": True,
            "progress": 6,
            "completed": True,
        }
        player_data["quests"]["diamond_in_the_rough"] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 99
        player_data["strength_level"] = 99
        player_data["defense_level"] = 99
        player_data["constitution_level"] = 99

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "diamond_in_the_rough",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["diamond_in_the_rough"]["progress"], 2)
        self.assertEqual(player_data["inventory"]["Heavy weight"], 1)

        self.assertEqual(
            tuple(
                blocker["reason"]
                for blocker in quest_current_stage_blockers_pure(
                    player_data,
                    "diamond_in_the_rough",
                    QUEST_DATA,
                )
            ),
            (
                "Battle required: Bandit (Diamond in the Rough) level 2 x5",
                "Battle required: Bandit king level 3",
            ),
        )
        for expected_encounter in (
            "diamond_in_the_rough_bandit",
            "diamond_in_the_rough_bandit",
            "diamond_in_the_rough_bandit",
            "diamond_in_the_rough_bandit",
            "diamond_in_the_rough_bandit",
            "diamond_in_the_rough_bandit_king",
        ):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "diamond_in_the_rough",
                QUEST_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            self.assertEqual(result["encounter_id"], expected_encounter)
            self.assertTrue(result["killed"])

        for expected_progress in (3, 4):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "diamond_in_the_rough",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(
                player_data["quests"]["diamond_in_the_rough"]["progress"],
                expected_progress,
            )
        self.assertEqual(player_data["inventory"].get("Heavy weight", 0), 0)
        self.assertEqual(player_data["inventory"].get("Sundial gnomon", 0), 0)
        self.assertEqual(player_data["inventory"]["Waterskin (4)"], 4)
        self.assertEqual(
            {gem: player_data["inventory"][gem] for gem in ("Sapphire", "Emerald", "Ruby")},
            {"Sapphire": 1, "Emerald": 1, "Ruby": 1},
        )

        for expected_encounter in (
            "diamond_in_the_rough_apep",
            "diamond_in_the_rough_heru",
        ):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "diamond_in_the_rough",
                QUEST_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            self.assertEqual(result["encounter_id"], expected_encounter)
            self.assertTrue(result["killed"])

        xp_before = {
            "agility": player_data["agility_exp"],
            "constitution": player_data["constitution_exp"],
            "thieving": player_data["thieving_exp"],
            "mining": player_data["mining_exp"],
        }
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "diamond_in_the_rough",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quests"]["diamond_in_the_rough"]["progress"], 5)
        self.assertEqual(player_data["agility_exp"], xp_before["agility"] + 250)
        self.assertEqual(
            player_data["constitution_exp"],
            xp_before["constitution"] + 250,
        )
        self.assertEqual(player_data["thieving_exp"], xp_before["thieving"] + 250)
        self.assertEqual(player_data["mining_exp"], xp_before["mining"])

        hidden_claim_ids = (
            "diamond_in_the_rough_scabaras_tomb",
            "diamond_in_the_rough_apmeken_tomb",
        )
        hidden_items = ("Scabaras mask", "Was", "Apmeken mask", "Ankh")
        self.assertTrue(
            all(not player_data["claims"][claim_id]["claimed"] for claim_id in hidden_claim_ids)
        )
        self.assertEqual(
            {item: player_data["inventory"].get(item, 0) for item in hidden_items},
            {"Scabaras mask": 0, "Was": 0, "Apmeken mask": 0, "Ankh": 0},
        )

        player_data["mining_level"] = 79
        player_data["agility_level"] = 79
        rows = {row["claim_id"]: row for row in claim_rows_pure(player_data, CLAIM_DATA)}
        self.assertEqual(rows[hidden_claim_ids[0]]["locked_reasons"], ("Mining level 80",))
        self.assertEqual(rows[hidden_claim_ids[1]]["locked_reasons"], ("Agility level 80",))

        player_data["mining_level"] = 80
        player_data["agility_level"] = 80
        rows = {row["claim_id"]: row for row in claim_rows_pure(player_data, CLAIM_DATA)}
        self.assertTrue(all(rows[claim_id]["eligible"] for claim_id in hidden_claim_ids))

        player_data, ok = apply_claim_pure(player_data, hidden_claim_ids[0], CLAIM_DATA)
        self.assertTrue(ok)
        player_data, ok = apply_claim_pure(player_data, hidden_claim_ids[1], CLAIM_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["mining_exp"], xp_before["mining"] + 20000)
        self.assertEqual(player_data["agility_exp"], xp_before["agility"] + 20250)
        self.assertEqual(
            {item: player_data["inventory"].get(item, 0) for item in hidden_items},
            {"Scabaras mask": 1, "Was": 1, "Apmeken mask": 1, "Ankh": 1},
        )

    def test_icthlarins_little_helper_stage_chain_resolves_guardian_ceremony_and_priest(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["icthlarins_little_helper"] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 99
        player_data["strength_level"] = 99
        player_data["defense_level"] = 99
        player_data["constitution_level"] = 99
        player_data["ranged_level"] = 99
        player_data["magic_level"] = 99
        player_data["prayer_level"] = 99
        player_data["inventory"].update(
            {
                "Kitten": 1,
                "Tinderbox": 1,
                "Waterskin (4)": 1,
                "Coins": 30,
                "Willow logs": 1,
                "Bucket": 1,
                "Bag of salt": 1,
                "Knife": 1,
            }
        )

        for expected_progress in (2, 3):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "icthlarins_little_helper",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(
                player_data["quests"]["icthlarins_little_helper"]["progress"],
                expected_progress,
            )

        self.assertEqual(player_data["inventory"]["Canopic jar"], 1)
        self.assertEqual(player_data["inventory"]["Sphinx's token"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "icthlarins_little_helper",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(
            player_data["quests"]["icthlarins_little_helper"]["progress"],
            4,
        )
        self.assertEqual(player_data["inventory"].get("Canopic jar", 0), 0)
        self.assertEqual(player_data["inventory"].get("Sphinx's token", 0), 0)
        self.assertEqual(
            tuple(
                blocker["reason"]
                for blocker in quest_current_stage_blockers_pure(
                    player_data,
                    "icthlarins_little_helper",
                    QUEST_DATA,
                )
            ),
            ("Battle required: Canopic guardian level 81",),
        )

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "icthlarins_little_helper",
            QUEST_DATA,
            stop_after_first_kill=True,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["encounter_id"], "icthlarins_little_helper_canopic_guardian")
        self.assertTrue(result["killed"])

        for expected_progress in (5, 6, 7, 8):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "icthlarins_little_helper",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(
                player_data["quests"]["icthlarins_little_helper"]["progress"],
                expected_progress,
            )

        self.assertEqual(player_data["inventory"].get("Canopic jar", 0), 0)
        self.assertEqual(player_data["inventory"].get("Sphinx's token", 0), 0)
        self.assertEqual(
            player_data["inventory"].get("Holy symbol (Icthlarin's Little Helper)", 0),
            0,
        )
        self.assertEqual(
            player_data["inventory"].get("Unholy symbol (Icthlarin's Little Helper)", 0),
            0,
        )
        self.assertEqual(player_data["inventory"].get("Bucket", 0), 0)
        self.assertEqual(player_data["inventory"].get("Bag of salt", 0), 0)

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "icthlarins_little_helper",
            QUEST_DATA,
            stop_after_first_kill=True,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["encounter_id"], "icthlarins_little_helper_possessed_priest")
        self.assertTrue(result["killed"])

        xp_before = {
            "agility": player_data["agility_exp"],
            "thieving": player_data["thieving_exp"],
            "woodcutting": player_data["woodcutting_exp"],
        }
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "icthlarins_little_helper",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quests"]["icthlarins_little_helper"]["progress"], 9)
        self.assertEqual(player_data["inventory"]["Catspeak amulet"], 1)
        self.assertEqual(
            player_data["inventory"].get("Unholy symbol (Icthlarin's Little Helper)", 0),
            0,
        )
        self.assertEqual(player_data["agility_exp"], xp_before["agility"] + 4000)
        self.assertEqual(player_data["thieving_exp"], xp_before["thieving"] + 4500)
        self.assertEqual(player_data["woodcutting_exp"], xp_before["woodcutting"] + 4000)
        self.assertEqual(player_data["quest_points"], 2)

    def test_smoking_kills_stage_chain_resolves_tomb_items_banshees_and_unlock(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["smoking_kills"] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        for level_key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
            "ranged_level",
            "magic_level",
            "prayer_level",
        ):
            player_data[level_key] = 200
        player_data["combat_lifepoints"] = 2000
        player_data["inventory"].update(
            {
                "Kitten": 1,
                "Catspeak amulet": 1,
                "Pickaxe": 1,
                "Ghostspeak amulet": 1,
                "Face mask": 1,
                "Earmuffs": 1,
            }
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "smoking_kills",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["smoking_kills"]["progress"], 2)

        expected_encounters = (
            ("smoking_kills_ranged_tomb_guardians", 3),
            ("smoking_kills_ranged_mummy_warrior", 4),
        )
        for encounter_id, expected_progress in expected_encounters:
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "smoking_kills",
                QUEST_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            self.assertTrue(result["killed"])
            self.assertEqual(result["encounter_id"], encounter_id)
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "smoking_kills",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"]["smoking_kills"]["progress"], expected_progress)

        self.assertEqual(player_data["inventory"]["Ranged path key"], 1)
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "smoking_kills",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["smoking_kills"]["progress"], 5)
        self.assertEqual(player_data["inventory"].get("Ranged path key", 0), 0)

        for encounter_id, expected_progress in (
            ("smoking_kills_magic_tomb_guardians", 6),
            ("smoking_kills_magic_mummy_warrior", 7),
        ):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "smoking_kills",
                QUEST_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            self.assertTrue(result["killed"])
            self.assertEqual(result["encounter_id"], encounter_id)
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "smoking_kills",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"]["smoking_kills"]["progress"], expected_progress)

        self.assertEqual(player_data["inventory"]["Magic path key"], 1)
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "smoking_kills",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["smoking_kills"]["progress"], 8)
        self.assertEqual(player_data["inventory"].get("Magic path key", 0), 0)
        self.assertEqual(player_data["inventory"].get("Face mask", 0), 0)
        self.assertEqual(player_data["inventory"].get("Earmuffs", 0), 0)
        self.assertEqual(player_data["inventory"]["Masked earmuffs"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "smoking_kills",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["smoking_kills"]["progress"], 9)

        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "smoking_kills",
            QUEST_DATA,
            stop_after_first_kill=True,
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["killed"])
        self.assertEqual(result["encounter_id"], "smoking_kills_mighty_banshee")
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "smoking_kills",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["inventory"]["Banshee voice"], 1)

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "smoking_kills",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["smoking_kills"]["progress"], 11)
        self.assertEqual(player_data["inventory"].get("Banshee voice", 0), 0)

        result = {}
        for _ in range(4):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                "smoking_kills",
                QUEST_DATA,
                stop_after_first_kill=True,
            )
            self.assertTrue(ok, result)
            if result["killed"]:
                break
        self.assertTrue(result["killed"])
        self.assertEqual(result["encounter_id"], "smoking_kills_banshee_mistress")
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "smoking_kills",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["smoking_kills"]["progress"], 12)

        slayer_xp_before = player_data["slayer_exp"]
        points_before = player_data["slayer_points"]
        streak_before = player_data["slayer_qualifying_streak"]
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "smoking_kills",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quests"]["smoking_kills"]["progress"], 13)
        self.assertEqual(player_data["slayer_exp"], slayer_xp_before + 5000)
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["slayer_points"], points_before)
        self.assertEqual(player_data["slayer_qualifying_streak"], streak_before)

    def test_shilo_village_stage_chain_preserves_evidence_transforms_and_boss_order(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["jungle_potion"] = {
            "started": True,
            "progress": QUEST_DATA["jungle_potion"]["stages"],
            "completed": True,
        }
        for level_key in (
            "smithing_level",
            "crafting_level",
            "agility_level",
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
            "ranged_level",
            "magic_level",
            "prayer_level",
        ):
            player_data[level_key] = 200
        player_data["combat_lifepoints"] = 2000
        player_data["quest_combat_config"] = {"resolver_enabled": True}

        player_data, ok = start_quest_pure(player_data, "shilo_village", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Wampum belt"], 1)
        player_data["inventory"].update(
            {
                "Rope": 1,
                "Lit torch": 1,
                "Spade": 1,
                "Chisel": 1,
                "Bronze wire": 1,
                "Bones": 3,
            }
        )

        expected_progress_and_items = (
            (2, {"Wampum belt": 0}),
            (3, {"Rope": 0, "Lit torch": 0}),
            (
                4,
                {
                    "Stone-plaque": 1,
                    "Tattered scroll": 1,
                    "Crumpled scroll": 1,
                    "Zadimus corpse": 1,
                },
            ),
            (5, {"Zadimus corpse": 0, "Bone shard": 1}),
            (6, {"Sword pommel": 1, "Locating crystal": 1, "Bervirius notes": 1}),
            (7, {}),
            (8, {"Bone shard": 0, "Sword pommel": 0, "Bone key": 1, "Bone beads": 1}),
            (9, {"Bone beads": 0, "Bronze wire": 0, "Beads of the dead": 1}),
            (10, {"Bones": 0}),
        )
        for expected_progress, expected_items in expected_progress_and_items:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                "shilo_village",
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"]["shilo_village"]["progress"], expected_progress)
            for item_name, quantity in expected_items.items():
                self.assertEqual(player_data["inventory"].get(item_name, 0), quantity)
            if expected_progress == 4:
                player_data["inventory"]["Stone-plaque"] = 0

        for encounter_id in (
            "shilo_village_nazastarool_zombie_91",
            "shilo_village_nazastarool_skeleton_68",
            "shilo_village_nazastarool_ghost_93",
        ):
            result = {}
            for _ in range(12):
                player_data, ok, result = apply_quest_combat_encounter_pure(
                    player_data,
                    "shilo_village",
                    QUEST_DATA,
                    stop_after_first_kill=True,
                )
                self.assertTrue(ok, result)
                if result["killed"]:
                    break
            self.assertTrue(result["killed"])
            self.assertEqual(result["encounter_id"], encounter_id)

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "shilo_village",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["shilo_village"]["progress"], 11)
        self.assertEqual(player_data["inventory"]["Rashiliyia corpse"], 1)

        crafting_xp_before = player_data["crafting_exp"]
        quest_points_before = player_data["quest_points"]
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "shilo_village",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quests"]["shilo_village"]["progress"], 12)
        self.assertEqual(player_data["inventory"].get("Rashiliyia corpse", 0), 0)
        self.assertEqual(player_data["crafting_exp"], crafting_xp_before + 3875)
        self.assertEqual(player_data["quest_points"], quest_points_before + 2)

    def test_demon_slayer_real_stage_emitter_completes_and_rewards_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"]["Coins"] = 1

        player_data, ok = start_quest_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "demon_slayer")
        self.assertNotIn("demon_slayer", player_data["quest_stage_actions"])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 2)
        self.assertEqual(player_data["inventory"]["Coins"], 0)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 3)

        blockers = quest_current_stage_blockers_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("missing_item",))
        self.assertEqual(blockers[0]["reason"], "Needs Bucket of water x1")

        player_data["inventory"]["Bucket of water"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 4)
        self.assertEqual(player_data["inventory"]["Bucket of water"], 0)
        self.assertEqual(player_data["inventory"]["Bucket"], 1)
        self.assertEqual(player_data["inventory"]["Silverlight key"], 1)

        blockers = quest_current_stage_blockers_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("missing_item",))
        self.assertEqual(blockers[0]["reason"], "Needs Bones x25")

        player_data["inventory"]["Bones"] = 25
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 5)
        self.assertEqual(player_data["inventory"]["Bones"], 0)
        self.assertEqual(player_data["inventory"]["Silverlight key"], 2)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 6)
        self.assertEqual(player_data["inventory"]["Silverlight key"], 3)

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 7)
        self.assertEqual(player_data["inventory"]["Silverlight key"], 0)
        self.assertEqual(player_data["inventory"]["Silverlight"], 1)

        blockers = quest_current_stage_blockers_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_locked",))
        self.assertEqual(
            blockers[0]["reason"],
            "Combat locked until battle support is enabled: Delrith level 27",
        )

        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 30
        player_data["strength_level"] = 30
        player_data["defense_level"] = 30
        player_data["constitution_level"] = 30
        blockers = quest_current_stage_blockers_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["reason"], "Battle required: Delrith level 27")

        player_data, ok, result = apply_quest_combat_encounter_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "demon_slayer_delrith_27")
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 7)
        self.assertFalse(player_data["quests"]["demon_slayer"]["completed"])

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["demon_slayer"]["progress"], 8)

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, "demon_slayer", QUEST_DATA),
            (),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"]["demon_slayer"]["completed"])
        self.assertEqual(
            player_data["quest_stage_actions"]["demon_slayer"],
            ["Recite Aber, Gabindo, Purchai, Camerinthum, Carlem"],
        )
        self.assertEqual(player_data["quest_points"], 3)
        self.assertEqual(player_data["inventory"]["Silverlight"], 1)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "demon_slayer",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 3)
        self.assertEqual(after_complete["inventory"]["Silverlight"], 1)

    def test_gertrudes_cat_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "gertrudes_cat"
        actions = (
            "Speak to Shilop and Wilough in Varrock Marketplace",
            "Reach Fluffs in the Varrock Lumber Yard",
            "Try to pick up Fluffs in the Lumber Yard",
            "Search the shaking crate for Fluffs' kittens",
            "Tell Gertrude that Fluffs and the kittens are safe",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"].update(
            {
                "Bucket of milk": 1,
                "Coins": 1000,
                "Doogle leaves": 1,
                "Raw sardine": 1,
            }
        )

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_steps = (
            (2, actions[:1], {"Coins": 1000, "Bucket of milk": 1}),
            (3, actions[:1], {"Coins": 900, "Bucket of milk": 1}),
            (4, actions[:3], {"Bucket of milk": 1, "Bucket": 0}),
            (5, actions[:3], {"Bucket of milk": 0, "Bucket": 1}),
            (6, actions[:3], {"Raw sardine": 0, "Doogle leaves": 0, "Doogle sardine": 1}),
            (7, actions[:3], {"Doogle sardine": 0, "Three little kittens": 0}),
            (8, actions[:4], {"Three little kittens": 1}),
            (
                9,
                actions[:4],
                {"Three little kittens": 0, "Chocolate cake": 0, "Kitten": 0, "Stew": 0},
            ),
        )
        for progress, recorded_actions, inventory in expected_steps:
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"].get(quest_id, ())),
                recorded_actions,
            )
            self.assertEqual(
                {
                    item_name: player_data["inventory"].get(item_name, 0)
                    for item_name in inventory
                },
                inventory,
            )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions,
        )
        self.assertEqual(player_data["quest_points"], 1)
        self.assertEqual(player_data["inventory"]["Kitten"], 1)
        self.assertEqual(player_data["inventory"]["Chocolate cake"], 1)
        self.assertEqual(player_data["inventory"]["Stew"], 1)
        self.assertEqual(player_data["cooking_exp"], 1525.0)

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 1)
        self.assertEqual(after_complete["inventory"]["Kitten"], 1)

    def test_demon_slayer_delrith_source_backed_stats_are_resolver_ready(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"]["Silverlight"] = 1
        player_data["quests"]["demon_slayer"] = {"started": True, "progress": 7, "completed": False}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 30
        player_data["strength_level"] = 30
        player_data["defense_level"] = 30
        player_data["constitution_level"] = 30

        blockers = quest_current_stage_blockers_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["reason"], "Battle required: Delrith level 27")
        self.assertTrue(can_attempt_quest_review_pure(player_data, "demon_slayer", QUEST_DATA))

        resolved, ok, result = apply_quest_combat_encounter_pure(player_data, "demon_slayer", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "demon_slayer_delrith_27")
        self.assertEqual(resolved["quest_combat_encounters"], {"demon_slayer": ["demon_slayer_delrith_27"]})
        self.assertEqual(quest_current_stage_blockers_pure(resolved, "demon_slayer", QUEST_DATA), ())

    def test_fairy_tale_ii_real_stage_emitters_complete_from_normal_start(self):
        quest_id = "a_fairy_tale_ii_cure_a_queen"
        quest = QUEST_DATA[quest_id]
        actions = (
            "The crops are still failing. I should investigate Fairy Nuff's grotto in Zanaris.",
            "The Godfather gave me permission to use fairy rings. Nuff's message says AIR, DLR, DJQ, AJS in order.",
            "I must pickpocket the Queen's secateurs from the Fairy Godfather without being detected.",
            "Fairy Nuff needs Magic essence: a Star flower from CKP and powdered Gorak claws from DIR.",
            "Back at the hideout, use a dose of the magic essence potion on the queen, who finally regains her senses.",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        player_data["inventory"].update({"Dramen staff": 1, "Vial of water": 1})
        # Other generated-stub quests still occupy this quest's prerequisite chain.
        # Isolate this stage chain instead of fabricating prerequisite completion state.
        quest_data = {**QUEST_DATA, quest_id: {**quest, "required_quests": ()}}

        player_data, ok = start_quest_pure(player_data, quest_id, quest_data)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        for index, action in enumerate(actions, start=1):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                quest_data,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, index == len(actions))
            self.assertEqual(player_data["quests"][quest_id]["progress"], index + 1)
            self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[:index])

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 2)
        self.assertEqual(player_data["herblore_exp"], 3500.0)
        self.assertEqual(player_data["thieving_exp"], 2500.0)

    def test_lunar_diplomacy_real_stage_emitters_complete_from_normal_start(self):
        quest_id = "lunar_diplomacy"
        quest = QUEST_DATA[quest_id]
        actions = (
            "Brundt must issue me a Seal of passage before Lokar can take me to the Lady Zay.",
            "The Lady Zay is jinxed. I must follow Captain Bentley and Bird's-Eye Jack's investigation.",
            "The five emerald glyphs are visible. Captain Bentley can now sail to Lunar Isle.",
            "The Oneiromancer needs a Waking sleep vial, a Lunar staff, and eight ceremonial garments.",
            "I have the ritual equipment. I must wear the outfit and staff, soak the kindling, and light the brazier.",
            "I must complete all six lessons in the Dream World. Finished lessons survive a failed visit.",
            "I defeated Me and read My life. I should return to the Oneiromancer.",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        player_data["inventory"].update(
            {
                "Coins": 1,
                "Dramen staff": 1,
                "Wicked hood": 1,
                "Thread": 1,
                "Clean guam": 1,
                "Clean marrentill": 1,
                "Spade": 1,
                "Hammer": 1,
                "Pickaxe": 1,
            }
        )
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        for skill_id in ("attack", "strength", "defense", "constitution", "ranged", "magic", "prayer"):
            player_data[f"{skill_id}_level"] = 99
        player_data["combat_lifepoints"] = 990
        player_data["equipment"].update({"weapon": "Rune sword", "shield": "Rune kiteshield"})
        # Other generated-stub quests still occupy this quest's prerequisite chain.
        # Isolate this stage chain instead of fabricating prerequisite completion state.
        quest_data = {**QUEST_DATA, quest_id: {**quest, "required_quests": ()}}

        player_data, ok = start_quest_pure(player_data, quest_id, quest_data)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        for index in range(5):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                quest_data,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], index + 2)
            self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[: index + 1])
            if index == 0:
                self.assertEqual(player_data["inventory"]["Seal of passage"], 1)

        for encounter_id, quantity in (
            ("lunar_diplomacy_suqah_111", 5),
            ("lunar_diplomacy_me_79", 1),
        ):
            for completed_quantity in range(1, quantity + 1):
                player_data, ok, result = apply_quest_combat_encounter_pure(
                    player_data,
                    quest_id,
                    quest_data,
                    encounter_id,
                    ticks=500,
                    rng=lambda: 0.5,
                    equipment_data=EQUIPMENT_DATA,
                )
                self.assertTrue(ok, result)
                self.assertEqual(result["reason"], "combat_resolved")
                self.assertEqual(result["completed_quantity"], completed_quantity)

        for index in range(5, len(actions)):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                quest_data,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, index == len(actions) - 1)
            self.assertEqual(player_data["quests"][quest_id]["progress"], index + 2)
            self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), actions[: index + 1])

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 2)
        self.assertEqual(player_data["inventory"]["Astral rune"], 50)
        self.assertEqual(player_data["magic_exp"], 5000.0)
        self.assertEqual(player_data["runecrafting_exp"], 5000.0)

    def test_fremennik_trials_real_stage_emitters_complete_from_normal_start(self):
        quest_id = "the_fremennik_trials"
        quest = QUEST_DATA[quest_id]
        actions_by_stage = (
            (
                "Brundt requires seven distinct council votes. I may complete the trials in any order.",
            ),
            (
                "Offer the beer to the Council workman. He will give you a cherry bomb, something he picked up from his outings, as a gift.",
            ),
            (
                "The low-alcohol beer keeps you clear-headed and Manni concedes.",
                "You perform on the longhall stage. As you finish, Fossegrimen's quest blessing leaves the lyre.",
            ),
            ("You escaped my house. My vote remains yours.",),
            (
                "You completed the bargain. My vote is yours.",
                "You navigated the maze. My vote is yours.",
            ),
            (
                "The Draugen is defeated. You have my vote.",
                "Koschei tested your bravery. My vote is yours.",
            ),
            ("I am a citizen of Rellekka and have a Fremennik name.",),
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        player_data["inventory"].update(
            {
                "Beer": 1,
                "Tinderbox": 1,
                "Raw shark": 1,
                "Bronze hatchet": 1,
                "Potato": 1,
                "Cabbage": 1,
                "Onion": 1,
                "Knife": 1,
            }
        )
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        for skill_id in ("attack", "strength", "defense", "constitution", "ranged", "magic", "prayer"):
            player_data[f"{skill_id}_level"] = 99
        player_data["combat_lifepoints"] = 990
        player_data["equipment"].update({"weapon": "Rune sword", "shield": "Rune kiteshield"})

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        expected_actions = []
        for stage_index in range(5):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            expected_actions.extend(actions_by_stage[stage_index])
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage_index + 2)
            self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), tuple(expected_actions))

        self.assertEqual(player_data["inventory"]["Beer"], 0)
        self.assertEqual(player_data["inventory"]["Strange object"], 0)
        self.assertEqual(player_data["inventory"]["Lyre"], 1)
        for encounter_id in (
            "the_fremennik_trials_borrokar_48",
            "the_fremennik_trials_the_draugen_96",
        ):
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                quest_id,
                QUEST_DATA,
                encounter_id,
                ticks=500,
                rng=lambda: 0.5,
                equipment_data=EQUIPMENT_DATA,
            )
            self.assertTrue(ok, result)
            self.assertEqual(result["reason"], "combat_resolved")
            self.assertEqual(result["completed_quantity"], 1)

        for stage_index in range(5, len(actions_by_stage)):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(completed_now, stage_index == len(actions_by_stage) - 1)
            expected_actions.extend(actions_by_stage[stage_index])
            self.assertEqual(player_data["quests"][quest_id]["progress"], stage_index + 2)
            self.assertEqual(tuple(player_data["quest_stage_actions"][quest_id]), tuple(expected_actions))

        self.assertTrue(player_data["quests"][quest_id]["completed"])
        self.assertEqual(player_data["quest_points"], 3)
        self.assertEqual(player_data["inventory"]["Fremennik blade"], 1)
        self.assertEqual(player_data["inventory"]["Fremennik name"], 1)

    def test_elemental_workshop_ii_beaten_book_emits_and_is_produced_on_review(self):
        quest_id = "elemental_workshop_ii"
        quest = QUEST_DATA[quest_id]
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for requirement in quest["required_quests"]:
            prerequisite = QUEST_DATA[requirement["quest_id"]]
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": prerequisite["stages"],
                "completed": True,
            }
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        player_data["inventory"].update({"Battered key": 1, "Pickaxe": 1, "Hammer": 1})

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        stage_one = next(
            requirement
            for requirement in quest["stage_requirements"]
            if requirement["stage"] == 1
        )
        self.assertEqual(stage_one["required_actions"], ())
        self.assertEqual(
            stage_one["auto_actions"],
            ("Find the Beaten book in the Exam Centre and read its hidden scroll",),
        )
        self.assertEqual(stage_one["produced_inventory"], {"Beaten book": 1})
        source_markers = (
            "ElementalWorkshopII.kt @ fd901261fbf3a3ccee75236c422765c9d9383f4a",
            "extracted/727-2012-07-24/cache",
            "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml",
            "extracted/742-2012-11-07/cache",
            "Elemental_Workshop_II?oldid=6358871",
            "Elemental_Workshop_II%2FQuick_guide?oldid=6333340",
        )
        source_positions = tuple(stage_one["source"].index(marker) for marker in source_markers)
        self.assertEqual(source_positions, tuple(sorted(source_positions)))
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            player_data["quest_stage_actions"][quest_id],
            ["Find the Beaten book in the Exam Centre and read its hidden scroll"],
        )
        self.assertEqual(player_data["inventory"]["Beaten book"], 1)
        self.assertEqual(player_data["inventory"].get("Slashed book", 0), 0)

    def test_elemental_workshop_iii_ragged_book_emits_on_review(self):
        quest_id = "elemental_workshop_iii"
        quest = QUEST_DATA[quest_id]
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for requirement in quest["required_quests"]:
            prerequisite = QUEST_DATA[requirement["quest_id"]]
            player_data["quests"][requirement["quest_id"]] = {
                "started": True,
                "progress": prerequisite["stages"],
                "completed": True,
            }
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        stage_one = next(
            requirement
            for requirement in quest["stage_requirements"]
            if requirement["stage"] == 1
        )
        player_data["inventory"].update(stage_one["required_inventory"])
        player_data["inventory"].update(stage_one["required_tools"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            player_data["quest_stage_actions"][quest_id],
            ["Find and read the Ragged book in the workshop"],
        )

    def test_elemental_workshop_identical_darkan_sources_are_resolver_ready(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"].update({"Thread": 1, "Leather": 1})
        player_data["quests"]["elemental_workshop_i"] = {"started": True, "progress": 2, "completed": False}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 40
        player_data["strength_level"] = 40
        player_data["defense_level"] = 40
        player_data["constitution_level"] = 40

        blockers = quest_current_stage_blockers_pure(player_data, "elemental_workshop_i", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("required_action", "combat_encounter"))
        self.assertEqual(blockers[1]["reason"], "Battle required: Earth Elemental level 35")
        self.assertTrue(can_attempt_quest_review_pure(player_data, "elemental_workshop_i", QUEST_DATA))

        resolved, ok, result = apply_quest_combat_encounter_pure(player_data, "elemental_workshop_i", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "elemental_workshop_i_earth_elemental_35")
        self.assertEqual(
            resolved["quest_combat_encounters"],
            {"elemental_workshop_i": ["elemental_workshop_i_earth_elemental_35"]},
        )
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(resolved, "elemental_workshop_i", QUEST_DATA),
            ("Action required: Complete Elemental Workshop I stage 2 objective",),
        )

    def test_witchs_house_experiment_forms_are_resolver_ready(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["witchs_house"] = {"started": True, "progress": 9, "completed": False}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["attack_level"] = 60
        player_data["strength_level"] = 60
        player_data["defense_level"] = 60
        player_data["constitution_level"] = 60

        blockers = quest_current_stage_blockers_pure(player_data, "witchs_house", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",) * 4)
        self.assertEqual(
            tuple(blocker["reason"] for blocker in blockers),
            (
                "Battle required: Witch's experiment (Skavid form) level 19",
                "Battle required: Witch's experiment (Spider form) level 30",
                "Battle required: Witch's experiment (Bear form) level 42",
                "Battle required: Witch's experiment (Wolf form) level 53",
            ),
        )
        self.assertTrue(can_attempt_quest_review_pure(player_data, "witchs_house", QUEST_DATA))

        resolved, ok, result = apply_quest_combat_encounter_pure(player_data, "witchs_house", QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "witchs_house_witchs_experiment_first_form")
        self.assertEqual(
            resolved["quest_combat_encounters"],
            {"witchs_house": ["witchs_house_witchs_experiment_first_form"]},
        )
        self.assertEqual(resolved["quests"]["witchs_house"]["progress"], 9)

        blockers = quest_current_stage_blockers_pure(resolved, "witchs_house", QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",) * 3)
        self.assertEqual(blockers[0]["reason"], "Battle required: Witch's experiment (Spider form) level 30")

    def test_troll_stronghold_dad_conflict_override_is_resolver_ready(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"] = {"Coins": 12}
        player_data["quests"]["troll_stronghold"] = {"started": True, "progress": 2, "completed": False}
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data["quest_combat_encounters"] = {
            "troll_stronghold": ["troll_stronghold_twig_troll_71", "troll_stronghold_troll_general_171"]
        }
        player_data["attack_level"] = 100
        player_data["strength_level"] = 100
        player_data["defense_level"] = 100
        player_data["constitution_level"] = 100

        blockers = quest_current_stage_blockers_pure(player_data, "troll_stronghold", QUEST_DATA)
        dad_blocker = next(blocker for blocker in blockers if blocker.get("encounter_id") == "troll_stronghold_dad_101")
        self.assertEqual(dad_blocker["kind"], "combat_encounter")
        self.assertEqual(dad_blocker["reason"], "Battle required: Dad level 101")

        resolved, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "troll_stronghold",
            QUEST_DATA,
            "troll_stronghold_dad_101",
        )
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "troll_stronghold_dad_101")
        self.assertEqual(
            resolved["quest_combat_encounters"],
            {
                "troll_stronghold": [
                    "troll_stronghold_dad_101",
                    "troll_stronghold_troll_general_171",
                    "troll_stronghold_twig_troll_71",
                ]
            },
        )

    def test_lost_city_completion_unlocks_cosmic_runecrafting_gate(self):
        quest_id = "lost_city"
        actions = (
            "Find Shamus in the Lumbridge Swamp tree",
            "Speak to Shamus about the dramen staff",
            "Reach Entrana without combat gear",
            "Cut a dramen branch",
            "Craft a dramen staff",
            "Enter Zanaris through the Lumbridge Swamp shed",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["crafting_level"] = 31
        player_data["woodcutting_level"] = 36
        # Combat level 63+ meets the Tree spirit's minimum combat gate, and a
        # weapon plus shield let the resolver win the fight in one burst.
        player_data["attack_level"] = 70
        player_data["constitution_level"] = 80
        player_data["defense_level"] = 70
        player_data["strength_level"] = 70
        player_data["combat_lifepoints"] = 800
        player_data["equipment"]["weapon"] = "Rune sword"
        player_data["equipment"]["shield"] = "Rune kiteshield"

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 0)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        # Stage 1: chopping the swamp tree reveals Shamus.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:1],
        )

        # Stage 2: Shamus explains the dramen staff and the adventurer sails
        # to Entrana unarmed.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 3)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:3],
        )

        self.assertIn(
            "Combat locked until battle support is enabled: Tree spirit level 63",
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
        )
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["encounter_id"], "lost_city_tree_spirit")
        self.assertEqual(blockers[0]["display_name"], "Tree spirit")
        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
            ticks=500,
            rng=lambda: 0.5,
            equipment_data=EQUIPMENT_DATA,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["reason"], "combat_resolved")
        self.assertEqual(result["encounter_id"], "lost_city_tree_spirit")

        # Stage 4: cut a dramen branch from the Dramen tree. The branch is
        # produced as stage 4 resolves and its action is marked then.
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 4)
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 5)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:4],
        )
        self.assertEqual(player_data["inventory"]["Dramen branch"], 1)

        # Stage 5: craft the staff and enter Zanaris through the shed.
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            ("Needs Knife",),
        )
        player_data["inventory"]["Knife"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quest_points"], 3)
        self.assertEqual(player_data["inventory"]["Dramen branch"], 0)
        self.assertEqual(player_data["inventory"]["Dramen staff"], 1)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions,
        )
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "runecrafting", "craft_cosmic_runes", QUEST_UNLOCK_RULES),
            (),
        )

    def test_while_guthix_sleeps_real_stage_emitters_advance_first_stage(self):
        quest_id = "while_guthix_sleeps"
        quest = QUEST_DATA[quest_id]
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quest_points"] = quest["required_quest_points"]
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        for requirement in quest["required_quests"]:
            prerequisite = requirement["quest_id"]
            player_data["quests"][prerequisite] = {
                "started": True,
                "progress": QUEST_DATA[prerequisite]["stages"],
                "completed": True,
            }

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        stage_one = next(
            requirement
            for requirement in quest["stage_requirements"]
            if requirement["stage"] == 1
        )
        player_data["inventory"].update(stage_one["required_inventory"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            player_data["quest_stage_actions"][quest_id],
            ["Cast NPC Contact to reach the quest contacts"],
        )

    def test_within_the_light_real_stage_emitters_advance_first_stage(self):
        quest_id = "within_the_light"
        quest = QUEST_DATA[quest_id]
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quest_points"] = quest["required_quest_points"]
        for requirement in quest["required_skills"]:
            player_data[f"{requirement['skill_id']}_level"] = requirement["level"]
        for requirement in quest["required_quests"]:
            prerequisite = requirement["quest_id"]
            player_data["quests"][prerequisite] = {
                "started": True,
                "progress": QUEST_DATA[prerequisite]["stages"],
                "completed": True,
            }

        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        stage_one = next(
            requirement
            for requirement in quest["stage_requirements"]
            if requirement["stage"] == 1
        )
        player_data["inventory"].update(stage_one["required_inventory"])
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA),
            (),
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 2)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            (
                "Reach the Temple of Light through West Ardougne and Lletya",
                "Recover the Temple of Light keys and crystal puzzle pieces",
            ),
        )

    def test_quest_completion_awards_trainable_xp_and_parks_unimplemented_xp(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["lunar_diplomacy"] = {"started": True, "progress": 7, "completed": False}
        player_data["quest_stage_actions"] = {"lunar_diplomacy": ["Complete Lunar Diplomacy stage 7 objective"]}

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "lunar_diplomacy",
            QUEST_DATA,
        )

        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["inventory"]["Astral rune"], 50)
        self.assertEqual(player_data["runecrafting_exp"], 5000)
        self.assertEqual(player_data["magic_exp"], 5000.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

    def test_dragon_slayer_real_stage_emitters_complete_and_reward_once(self):
        quest_id = "dragon_slayer"
        actions = (
            "Accept Oziach's dragon-slaying challenge",
            "Complete the Guildmaster's Crandor briefing",
            "Ask Duke Horacio for an anti-dragon shield",
            "Ask the Oracle about Thalzar's map piece",
            "Recruit Ned as captain of the Lady Lumbridge",
            "Sail to Crandor with Captain Ned",
            "Report Elvarg's death to Oziach",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        reasons = quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA)
        self.assertIn("32 quest points", reasons)
        self.assertFalse(can_start_quest_pure(player_data, quest_id, QUEST_DATA))

        player_data.update(
            {
                "attack_level": 120,
                "constitution_level": 120,
                "defense_level": 120,
                "quest_points": 32,
                "strength_level": 120,
            }
        )
        player_data["inventory"].update(
            {
                "Bowl (unfired)": 1,
                "Coins": 12000,
                "Hammer": 1,
                "Plank": 3,
                "Silk": 1,
                "Steel nails": 90,
                "Wizard's mind bomb": 1,
            }
        )
        player_data, ok = start_quest_pure(player_data, quest_id, QUEST_DATA)
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], quest_id)
        self.assertNotIn(quest_id, player_data["quest_stage_actions"])

        for progress, action_count in ((2, 0), (3, 1), (4, 2), (5, 3)):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
            self.assertEqual(
                tuple(player_data["quest_stage_actions"].get(quest_id, ())),
                actions[:action_count],
            )

        self.assertEqual(player_data["inventory"]["Maze key"], 1)
        self.assertEqual(player_data["inventory"]["Anti-dragon shield"], 1)
        maze_encounters = (
            "dragon_slayer_zombie_rat_3",
            "dragon_slayer_ghost_19",
            "dragon_slayer_skeleton_22",
            "dragon_slayer_zombie_24",
            "dragon_slayer_melzar_the_mad_43",
            "dragon_slayer_lesser_demon_82",
        )
        blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
        self.assertEqual(
            tuple(blocker["kind"] for blocker in blockers),
            ("combat_locked",) * len(maze_encounters),
        )
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
        self.assertEqual(
            tuple(blocker["encounter_id"] for blocker in blockers),
            maze_encounters,
        )
        for encounter_id in maze_encounters:
            player_data, ok, result = apply_quest_combat_encounter_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok, result)
            self.assertEqual(result["reason"], "combat_resolved")
            self.assertEqual(result["encounter_id"], encounter_id)

        for progress in (6, 7, 8):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:4],
        )
        self.assertEqual(player_data["inventory"]["Coins"], 2000)
        self.assertEqual(player_data["inventory"]["Map part"], 2)
        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            ),
            ("Needs Crayfish cage x1 or Lobster pot x1",),
        )

        player_data["inventory"]["Lobster pot"] = 1
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 9)
        self.assertEqual(player_data["inventory"]["Wizard's mind bomb"], 0)
        self.assertEqual(player_data["inventory"]["Silk"], 0)
        self.assertEqual(player_data["inventory"]["Bowl (unfired)"], 0)
        self.assertEqual(player_data["inventory"]["Lobster pot"], 0)
        self.assertEqual(player_data["inventory"]["Map part"], 3)

        for progress in (10, 11, 12, 13, 14):
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data,
                quest_id,
                QUEST_DATA,
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][quest_id]["progress"], progress)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:6],
        )
        blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
        self.assertEqual(tuple(blocker["kind"] for blocker in blockers), ("combat_encounter",))
        self.assertEqual(blockers[0]["display_name"], "Elvarg")
        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["reason"], "combat_resolved")
        self.assertEqual(result["encounter_id"], "dragon_slayer_elvarg_83")

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 15)
        self.assertEqual(player_data["inventory"]["Elvarg's head"], 1)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions[:6],
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quests"][quest_id]["progress"], 16)
        self.assertEqual(
            tuple(player_data["quest_stage_actions"][quest_id]),
            actions,
        )
        self.assertEqual(player_data["quest_points"], 34)
        self.assertEqual(player_data["defense_exp"], 18650.0)
        self.assertEqual(player_data["strength_exp"], 18650.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quest_points"], 34)
        self.assertEqual(player_data["defense_exp"], 18650.0)
        self.assertEqual(player_data["strength_exp"], 18650.0)

    def test_tai_bwo_wannai_trio_real_stage_emitters_complete_and_reward_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data.update(
            {
                "agility_level": 120,
                "attack_level": 120,
                "constitution_level": 120,
                "cooking_level": 30,
                "defense_level": 120,
                "fishing_level": 5,
                "prayer_level": 120,
                "strength_level": 120,
            }
        )
        player_data["quests"]["jungle_potion"] = {
            "started": True,
            "progress": QUEST_DATA["jungle_potion"]["stages"],
            "completed": True,
        }
        player_data["inventory"].update(
            {
                "Raw karambwan": 2,
                "Small fishing net": 1,
                "Agility potion (4)": 1,
                "Steel spear": 1,
                "Karamjan rum": 1,
                "Seaweed": 1,
                "Banana": 1,
                "Jogre bones": 1,
                "Knife": 1,
                "Tinderbox": 1,
                "Pestle and mortar": 1,
            }
        )

        player_data, ok = start_quest_pure(
            player_data,
            "tai_bwo_wannai_trio",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(player_data["current_quest"], "tai_bwo_wannai_trio")
        self.assertNotIn("tai_bwo_wannai_trio", player_data["quest_stage_actions"])

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "tai_bwo_wannai_trio",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["tai_bwo_wannai_trio"]["progress"], 2)
        self.assertNotIn("tai_bwo_wannai_trio", player_data["quest_stage_actions"])

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "tai_bwo_wannai_trio",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["tai_bwo_wannai_trio"]["progress"], 3)
        self.assertEqual(
            player_data["quest_stage_actions"]["tai_bwo_wannai_trio"],
            ["Catch karambwanji for Tiadeche"],
        )

        # The source-backed Monkey encounter has no combat stats to resolve yet;
        # isolate action emission while the Jogre still runs through the real resolver.
        player_data["quest_combat_encounters"] = {
            "tai_bwo_wannai_trio": ["tai_bwo_wannai_trio_monkey"]
        }
        player_data["quest_combat_config"] = {"resolver_enabled": True}
        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            "tai_bwo_wannai_trio",
            QUEST_DATA,
            "tai_bwo_wannai_trio_jogre",
        )
        self.assertTrue(ok)
        self.assertEqual(result["encounter_id"], "tai_bwo_wannai_trio_jogre")
        self.assertEqual(result["remaining_quantity"], 0)

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "tai_bwo_wannai_trio",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["tai_bwo_wannai_trio"]["progress"], 4)
        self.assertEqual(
            player_data["quest_stage_actions"]["tai_bwo_wannai_trio"],
            [
                "Catch karambwanji for Tiadeche",
                "Repair and poison Tamayu's spear",
            ],
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "tai_bwo_wannai_trio",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertFalse(completed_now)
        self.assertEqual(player_data["quests"]["tai_bwo_wannai_trio"]["progress"], 5)
        self.assertEqual(
            player_data["quest_stage_actions"]["tai_bwo_wannai_trio"],
            [
                "Catch karambwanji for Tiadeche",
                "Repair and poison Tamayu's spear",
                "Prepare the sliced banana in rum",
                "Burn and grind the jogre bones",
            ],
        )

        attack_before_reward = player_data["attack_exp"]
        strength_before_reward = player_data["strength_exp"]
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data,
            "tai_bwo_wannai_trio",
            QUEST_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertEqual(player_data["quests"]["tai_bwo_wannai_trio"]["progress"], 6)
        self.assertEqual(
            player_data["quest_stage_actions"]["tai_bwo_wannai_trio"],
            [
                "Catch karambwanji for Tiadeche",
                "Repair and poison Tamayu's spear",
                "Prepare the sliced banana in rum",
                "Burn and grind the jogre bones",
            ],
        )
        self.assertEqual(player_data["quest_points"], 2)
        self.assertEqual(player_data["inventory"]["Coins"], 2000)
        self.assertEqual(player_data["inventory"]["Rune spear (kp)"], 1)
        self.assertEqual(player_data["cooking_exp"], 5000.0)
        self.assertEqual(player_data["fishing_exp"], 5000.0)
        self.assertEqual(player_data["attack_exp"] - attack_before_reward, 2500.0)
        self.assertEqual(player_data["strength_exp"] - strength_before_reward, 2500.0)
        self.assertEqual(player_data["pending_skill_exp_rewards"], {})

        after_complete, ok, completed_again = apply_quest_progress_pure(
            player_data,
            "tai_bwo_wannai_trio",
            QUEST_DATA,
        )
        self.assertFalse(ok)
        self.assertFalse(completed_again)
        self.assertEqual(after_complete["quest_points"], 2)
        self.assertEqual(after_complete["inventory"]["Coins"], 2000)
        self.assertEqual(after_complete["inventory"]["Rune spear (kp)"], 1)
        self.assertEqual(after_complete["cooking_exp"], 5000.0)
        self.assertEqual(after_complete["fishing_exp"], 5000.0)

    def test_fishing_unlock_rules_cover_swan_song_and_tai_bwo_wannai_trio(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_monkfish", QUEST_UNLOCK_RULES),
            ("Swan Song",),
        )
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_karambwan", QUEST_UNLOCK_RULES),
            ("Tai Bwo Wannai Trio",),
        )
        player_data["quests"]["swan_song"] = {"started": True, "progress": 6, "completed": True}
        player_data["quests"]["tai_bwo_wannai_trio"] = {"started": True, "progress": 6, "completed": True}
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_monkfish", QUEST_UNLOCK_RULES),
            (),
        )
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_karambwan", QUEST_UNLOCK_RULES),
            (),
        )

    def test_ability_unlock_rules_cover_barbarian_fishing_and_broad_fletching(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["fishing_level"] = 99
        player_data["fletching_level"] = 99
        player_data["inventory"].update(
            {
                "Feather": 10,
                "Headless arrows": 15,
                "Broad arrow heads": 15,
                "Unfinished broad bolts": 10,
            }
        )

        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_leaping_fish", QUEST_UNLOCK_RULES),
            ("Barbarian Fishing",),
        )
        self.assertEqual(
            fletching_target_locked_reasons_pure(player_data, "broad_arrows", FLETCHING_DATA, QUEST_UNLOCK_RULES),
            ("Broad Fletching",),
        )

        player_data["unlocked_abilities"] = ["barbarian_fishing", "broad_fletching"]
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_leaping_fish", QUEST_UNLOCK_RULES),
            (),
        )
        self.assertEqual(
            fletching_target_locked_reasons_pure(player_data, "broad_arrows", FLETCHING_DATA, QUEST_UNLOCK_RULES),
            (),
        )

    def test_shilo_village_gates_current_gem_rocks_target(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "mining", "gem_rocks", QUEST_UNLOCK_RULES),
            ("Shilo Village",),
        )

        player_data["quests"]["shilo_village"] = {"started": True, "progress": 7, "completed": True}
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "mining", "gem_rocks", QUEST_UNLOCK_RULES),
            (),
        )

    def test_region_precedent_quest_locks_cover_morytania_and_neitiznot_targets(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["fishing_level"] = 99
        player_data["cooking_level"] = 99
        player_data["firemaking_level"] = 99
        player_data["inventory"].update(
            {
                "Fishing bait": 1,
                "Slimy eel": 1,
                "Thin snail": 1,
                "Raw yak meat": 1,
                "Arctic pine logs": 1,
            }
        )

        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_slimy_eel", QUEST_UNLOCK_RULES),
            ("Priest in Peril",),
        )
        self.assertEqual(
            cooking_target_locked_reasons_pure(player_data, "cook_slimy_eel", COOKING_DATA, QUEST_UNLOCK_RULES),
            ("Priest in Peril",),
        )
        self.assertEqual(
            cooking_target_locked_reasons_pure(player_data, "cook_thin_snail", COOKING_DATA, QUEST_UNLOCK_RULES),
            ("Priest in Peril",),
        )
        self.assertEqual(
            utility_activity_locked_reasons_pure(
                player_data,
                "gather_lean_snails",
                UTILITY_ACTIVITY_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Priest in Peril",),
        )
        self.assertEqual(
            firemaking_target_locked_reasons_pure(
                player_data,
                "arctic_pine_logs",
                FIREMAKING_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Start The Fremennik Isles",),
        )
        player_data["quests"]["the_fremennik_isles"] = {"started": True}
        self.assertFalse(
            firemaking_target_locked_reasons_pure(
                player_data,
                "arctic_pine_logs",
                FIREMAKING_DATA,
                QUEST_UNLOCK_RULES,
            )
        )
        self.assertEqual(
            cooking_target_locked_reasons_pure(player_data, "cook_yak", COOKING_DATA, QUEST_UNLOCK_RULES),
            ("The Fremennik Isles",),
        )
        player_data["quests"]["priest_in_peril"] = {"started": True, "progress": 6, "completed": True}
        player_data["quests"]["the_fremennik_isles"] = {"started": True, "progress": 6, "completed": True}
        self.assertEqual(
            quest_unlock_locked_reasons_pure(player_data, "fishing", "catch_slimy_eel", QUEST_UNLOCK_RULES),
            (),
        )
        self.assertEqual(
            cooking_target_locked_reasons_pure(player_data, "cook_slimy_eel", COOKING_DATA, QUEST_UNLOCK_RULES),
            (),
        )
        self.assertEqual(
            firemaking_target_locked_reasons_pure(
                player_data,
                "arctic_pine_logs",
                FIREMAKING_DATA,
                QUEST_UNLOCK_RULES,
            ),
            (),
        )
    def test_wicked_hood_claim_requires_rune_mysteries(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        rows = claim_rows_pure(player_data, CLAIM_DATA)
        self.assertEqual(rows[0]["locked_reasons"], ("quest",))

        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        claimed_data, ok = apply_claim_pure(player_data, "wicked_hood", CLAIM_DATA)
        self.assertTrue(ok)
        self.assertEqual(claimed_data["inventory"]["Wicked hood"], 1)
        self.assertTrue(claimed_data["claims"]["wicked_hood"]["claimed"])

        claimed_again, ok = apply_claim_pure(claimed_data, "wicked_hood", CLAIM_DATA)
        self.assertFalse(ok)
        self.assertEqual(claimed_again["inventory"]["Wicked hood"], 1)

    def test_cabin_fever_bill_teach_claim_is_post_quest_and_once_only(self):
        claim_id = "cabin_fever_bill_teach_coins"
        self.assertEqual(
            CLAIM_DATA[claim_id]["source"],
            "https://runescape.wiki/w/Cabin_Fever?oldid=6533785",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        row = next(
            row for row in claim_rows_pure(player_data, CLAIM_DATA)
            if row["claim_id"] == claim_id
        )
        self.assertEqual(row["locked_reasons"], ("quest",))
        player_data["quests"]["cabin_fever"] = {
            "started": True,
            "progress": QUEST_DATA["cabin_fever"]["stages"],
            "completed": False,
        }

        completed_data, progressed, completed = apply_quest_progress_pure(
            player_data, "cabin_fever", QUEST_DATA
        )

        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertEqual(completed_data["inventory"].get("Coins", 0), 0)
        self.assertEqual(completed_data["inventory"].get("Book o' piracy", 0), 1)
        claimed_data, ok = apply_claim_pure(completed_data, claim_id, CLAIM_DATA)
        self.assertTrue(ok)
        self.assertEqual(claimed_data["inventory"]["Coins"], 10000)
        claimed_again, ok = apply_claim_pure(claimed_data, claim_id, CLAIM_DATA)
        self.assertFalse(ok)
        self.assertEqual(claimed_again["inventory"]["Coins"], 10000)

    def test_rocking_out_bill_teach_claim_is_post_quest_and_once_only(self):
        claim_id = "rocking_out_bill_teach_magical_cage"
        self.assertEqual(
            CLAIM_DATA[claim_id]["source"],
            "https://runescape.wiki/w/Rocking_Out?oldid=6521879",
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rocking_out"] = {
            "started": True,
            "progress": QUEST_DATA["rocking_out"]["stages"],
            "completed": False,
        }

        completed_data, progressed, completed = apply_quest_progress_pure(
            player_data, "rocking_out", QUEST_DATA
        )

        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertEqual(completed_data["inventory"].get("Magical cage", 0), 0)
        claimed_data, ok = apply_claim_pure(completed_data, claim_id, CLAIM_DATA)
        self.assertTrue(ok)
        self.assertEqual(claimed_data["inventory"]["Magical cage"], 1)
        claimed_again, ok = apply_claim_pure(claimed_data, claim_id, CLAIM_DATA)
        self.assertFalse(ok)
        self.assertEqual(claimed_again["inventory"]["Magical cage"], 1)

    def test_claim_tool_gate_honours_toolbelt_and_refuses_genuine_absence(self):
        claim_id = "pickaxe_tool_gate_probe"
        claim_data = {
            claim_id: {
                "item_name": "Tool gate proof",
                "required_tools": (("Pickaxe", 1),),
            }
        }
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["inventory"] = {
            name: quantity
            for name, quantity in player_data["inventory"].items()
            if not name.lower().endswith("pickaxe")
        }

        _, claimed = apply_claim_pure(player_data, claim_id, claim_data)

        self.assertTrue(claimed)

        player_data["toolbelt"]["mining"] = []

        _, claimed = apply_claim_pure(player_data, claim_id, claim_data)

        self.assertFalse(claimed)

    def test_the_golem_throne_claim_requires_tools_and_is_once_only(self):
        claim_id = "the_golem_thammarons_throne_gems"
        self.assertEqual(
            CLAIM_DATA[claim_id]["source"],
            "https://runescape.wiki/w/The_Golem?oldid=6543894",
        )
        self.assertEqual(
            CLAIM_DATA[claim_id]["required_tools"],
            (("Chisel", 1), ("Hammer", 1)),
        )
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["the_golem"] = {
            "started": True,
            "progress": QUEST_DATA["the_golem"]["stages"],
            "completed": False,
        }

        completed_data, progressed, completed = apply_quest_progress_pure(
            player_data, "the_golem", QUEST_DATA
        )

        self.assertTrue(progressed)
        self.assertTrue(completed)
        for gem in ("Ruby", "Emerald", "Sapphire"):
            self.assertEqual(completed_data["inventory"].get(gem, 0), 0)
        completed_data["inventory"]["Chisel"] = 1
        refused_data, ok = apply_claim_pure(completed_data, claim_id, CLAIM_DATA)
        self.assertFalse(ok)
        self.assertEqual(refused_data["inventory"].get("Ruby", 0), 0)
        completed_data["inventory"]["Hammer"] = 1
        claimed_data, ok = apply_claim_pure(completed_data, claim_id, CLAIM_DATA)
        self.assertTrue(ok)
        self.assertEqual(
            {gem: claimed_data["inventory"][gem] for gem in ("Ruby", "Emerald", "Sapphire")},
            {"Ruby": 2, "Emerald": 2, "Sapphire": 2},
        )
        self.assertEqual(claimed_data["inventory"]["Chisel"], 1)
        self.assertEqual(claimed_data["inventory"]["Hammer"], 1)
        claimed_again, ok = apply_claim_pure(claimed_data, claim_id, CLAIM_DATA)
        self.assertFalse(ok)
        self.assertEqual(claimed_again["inventory"]["Ruby"], 2)

    def test_tutorial_starter_kit_claim_grants_source_backed_bundle_once(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        rows = claim_rows_pure(player_data, CLAIM_DATA)
        row = next(row for row in rows if row["claim_id"] == "tutorial_island_starter_kit")
        self.assertTrue(row["eligible"])
        self.assertEqual(row["claim_type"], "item_bundle")
        self.assertEqual(
            row["items"],
            (
                ("Bronze sword", 1),
                ("Wooden shield", 1),
                ("Shortbow", 1),
                ("Bronze arrows", 50),
                ("Air rune", 5),
                ("Mind rune", 5),
                ("Bronze pickaxe", 1),
                ("Hammer", 1),
                ("Bronze hatchet", 1),
                ("Tinderbox", 1),
                ("Small fishing net", 1),
            ),
        )

        claimed_data, ok = apply_claim_pure(player_data, "tutorial_island_starter_kit", CLAIM_DATA)
        self.assertTrue(ok)
        for item_name, amount in row["items"]:
            self.assertEqual(claimed_data["inventory"][item_name], player_data["inventory"].get(item_name, 0) + amount)
        self.assertTrue(claimed_data["claims"]["tutorial_island_starter_kit"]["claimed"])

        claimed_again, ok = apply_claim_pure(claimed_data, "tutorial_island_starter_kit", CLAIM_DATA)
        self.assertFalse(ok)
        self.assertEqual(claimed_again["inventory"]["Bronze arrows"], claimed_data["inventory"]["Bronze arrows"])

    def test_every_quest_completion_grants_only_source_backed_items(self):
        expected_rewards = {
            "a_fairy_tale_iii_battle_at_orks_rift": {
                "Magic watering can": 1,
            },
            "a_souls_bane": {"Coins": 500},
            "a_tail_of_two_cats": {"Catspeak amulet (e)": 1, "Doctors hat": 1},
            "another_slice_of_h_a_m": {"Ancient mace": 1, "Dorgesh-kaan sphere": 1},
            "back_to_my_roots": {
                "Jade vine seed": 1,
            },
            "biohazard": {},
            "black_knights_fortress": {"Coins": 2500},
            "catapult_construction": {
                "Adamant halberd": 1,
                "Coins": 2000,
                "Sailor's hat": 1,
                "Teak plank": 30,
            },
            "clock_tower": {"Coins": 500},
            "cooks_assistant": {"Coins": 500, "Sardine": 20},
            "cabin_fever": {"Book o' piracy": 1},
            "deadliest_catch": {
                "Small cast net": 1,
            },
            "dealing_with_scabaras": {},
            "do_no_evil": {"Clue scroll (elite)": 1, "Cramulet": 1},
            "dream_mentor": {},
            "dwarf_cannon": {"Ammo mould": 1},
            "eagles_peak": {"Box trap": 1, "Eagle costume": 1},
            "family_crest": {"Family gauntlets": 1},
            "imp_catcher": {"Amulet of accuracy": 1},
            "in_aid_of_the_myreque": {},
            "legacy_of_seergaze": {
                "Blood talisman": 1,
                "Ivandis flail": 1,
                "Tome of xp 2nd ed (3)": 1,
            },
            "let_them_eat_pie": {"Expensive spices": 1, "Meat pie": 5},
            "meeting_history": {"Enchanted key": 1},
            "missing_my_mummy": {"Coins": 5000},
            "monks_friend": {"Law rune": 8},
            "nomads_requiem": {
                "Soul Wars cape": 1,
            },
            "observatory_quest": {"Maple longbow": 1, "Uncut sapphire": 1},
            "plague_city": {"A magic scroll": 1},
            "rocking_out": {},
            "rune_mysteries": {"Air talisman": 1},
            "sheep_herder": {"Coins": 3100},
            "shield_of_arrav": {"Coins": 600},
            "song_from_the_depths": {
                "Coral bolts": 50,
                "Coral crossbow": 1,
                "Remora's necklace": 1,
            },
            "spirit_of_summer": {"Jennica's ring": 1},
            "stolen_hearts": {"Coins": 2500},
            "temple_of_ikov": {"Shiny key": 1},
            "the_dig_site": {"Fruit blast": 1, "Gold bar": 2},
            "the_golem": {},
            "carnillean_rising": {
                "Coins": 5000,
                "Oak plank": 100,
                "Philipe's sweets": 1,
                "Teak plank": 30,
                "Mahogany plank": 10,
                "Treasure chest (Carnillean Rising)": 1,
            },
            "the_grand_tree": {},
            "the_restless_ghost": {"Ancient bones": 5},
            "tree_gnome_village": {"Gnome amulet": 1},
            "tribal_totem": {"Swordfish": 5},
            "waterfall_quest": {"Diamond": 2, "Gold bar": 2, "Mithril seeds": 40},
            "wolf_whistle": {"Gold charm": 275},
        }
        non_item_reward_names_by_quest = {
            "a_fairy_tale_iii_battle_at_orks_rift": {
                "Martin the Master Gardener",
                "Zanaris Market",
            },
            "a_tail_of_two_cats": {"Varrock Museum"},
            "another_slice_of_h_a_m": {"Dorgesh-Kaan - Keldagrim Train System"},
            "back_to_my_roots": {"Eagles' Peak", "East Ardougne", "Giant ant soldier", "Jade vine maze"},
            "catapult_construction": {"Castle Wars"},
            "carnillean_rising": {"Construction"},
            # Cabin Fever's generated "Charter ship" item row is filtered out
            # of quest_reward_items_as_dict(); auditing the name here keeps
            # that filter honest.
            "cabin_fever": {"Charter ship"},
            "deadliest_catch": {
                "Bank deposit box",
                "North-East of Pollnivneach",
                "North-west of Bedabin Camp",
                "South Coast of Ape Atoll",
                "South of Brimhaven",
                "South of Elf Camp",
                "Piscatoris - South of Falconry",
                "The concept art for Jones the fisherman",
                "The concept art for Thalassus",
                "West Coast of Harmony Island",
                "West Coast of Mort Myre Swamp",
            },
            "dealing_with_scabaras": {"Pyramid Plunder"},
            "do_no_evil": {
                "File:Apmeken's tomb entrance.jpg",
                "Magic carpet",
                "The Apmeken tomb.",
            },
            "dream_mentor": {"Lunar Spells"},
            "eagles_peak": {"Ferret"},
            "in_aid_of_the_myreque": {"Varrock Museum"},
            "legacy_of_seergaze": {"Tome of Experience, 2nd Ed."},
            "let_them_eat_pie": {
                "Expensive spices (necklace) (page does not exist)"
            },
            "meeting_history": {"Varrock Museum"},
            "missing_my_mummy": {
                "2,100 Cooking",
                "Construction",
                "3,000 Thieving",
                "3,350 Crafting",
                "5,000 Magic",
                "6,500 Prayer",
            },
            "nomads_requiem": {"Decaying Avatar", "Soul Wars", "Zeal points"},
            "observatory_quest": {"Varrock Museum"},
            "rocking_out": {"Brimhaven Agility Arena"},
            "spirit_of_summer": {"Spirit Realm"},
            "the_dig_site": {"Varrock Museum"},
            "the_golem": {"Magic carpet"},
            "the_grand_tree": {"Varrock Museum"},
        }
        non_item_reward_names = set().union(*non_item_reward_names_by_quest.values())
        previously_corrected_reward_names = {"Combat Training Camp", "Coin", "Law Rune"}
        prohibited_reward_names = non_item_reward_names | previously_corrected_reward_names
        expected_unlocks = {
            "a_fairy_tale_iii_battle_at_orks_rift": {
                "Free access to the Zanaris Market",
                "To have your patches automatically weeded, talk to Martin the Master Gardener after the quest "
                "to unlock the ability to have gardeners keep your farming patches weed free.",
            },
            "a_tail_of_two_cats": {
                "Talk to Historian Minas in the Varrock Museum to receive 5 Kudos."
            },
            "another_slice_of_h_a_m": {
                "Free access to the Dorgesh-Kaan - Keldagrim Train System"
            },
            "back_to_my_roots": {
                "Vine Farming Patch in East Ardougne",
                "Transportation between Eagles' Peak and Karamja using the Karamjan Jungle eagle.",
                "A new maze Jade vine maze, slightly larger than Draynor Manor, containing 8 new creatures: "
                "Giant ant soldier level 58, Giant ant worker level 40, Tenacious toucan level 70, Giant Wasp level 66, "
                "Frog level 66, Pernicious parrot level 66, Wild jade vine level 167, Karamjan Jungle eagle.",
            },
            "catapult_construction": {
                "Increased damage when using the Castle Wars catapults"
            },
            "cabin_fever": {
                "Access to Mos Le'Harmless",
                "Access to kill Cave horrors.",
                "Charter Ship prices are halved.",
            },
            "deadliest_catch": {
                "Bank deposit box north-west of Bedabin Camp",
                "Bank deposit box south of Elf Camp",
                "Bank deposit box west of Harmony Island",
                "Bank deposit box west of Mort Myre Swamp",
                "Bank deposit box north-east of Pollnivneach",
                "Bank deposit box on the south coast of Ape Atoll",
                "Bank deposit box south of Brimhaven",
                "Piscatoris - South of Falconry",
            },
            # Clean rewrite: the generated run-on paragraph is a capability
            # line plus a how-to explanation; the unlock keeps the capability
            # and drops the mechanics (Scabaras oldid=6581466).
            "dealing_with_scabaras": {
                "The ability to craft an Enchanted water tiara - protects you from the Desert heat effect",
                "Simon Templeton accepts noted Pyramid Plunder treasures after his post-quest errand, "
                "but noted gold artefacts still cannot be exchanged.",
            },
            "dream_mentor": {"Seven new spells added to the Lunar Spellbook"},
            "do_no_evil": {
                "New magic carpet destinations, connecting the Monkey colony with Shantay Pass "
                "and southern Pollnivneach.",
                "Ability to pickpocket monkey knife fighters.",
                "Ability to run chimp ice for further rewards.",
                "Access to a passageway from the desert (rockslide south of the Kalphite Hive entrance) "
                "to a new area with Kalphites. This is unlocked if you left the room from the hole while you were in it.",
                "The ability to upgrade Ava's accumulator to Ava's alerter.",
                "Access to the Monkey colony.",
                "Players with level 80 Agility (boosts may be used) can enter the cavern "
                "in the south wall of the Monkey colony.",
                "The ability to add the camulet and catspeak amulet to the Cramulet.",
            },
            "in_aid_of_the_myreque": {
                "Talk to Historian Minas to receive 5 Kudos in the Varrock Museum."
            },
            "meeting_history": {
                "Speak to Historian Minas at the Varrock Museum to earn 5 Kudos."
            },
            "nomads_requiem": {
                "Soul Wars is added to the available respawn points.",
                "Decaying Avatar and Nomad become available as bosses in the Dominion Tower.",
            },
            "observatory_quest": {
                "Talk to Historian Minas at the Varrock Museum to receive 5 Kudos."
            },
            "rocking_out": {
                # Clean rewrite of the pinned revision's broken skill-clickpic
                # render (Rocking Out oldid=6521879).
                "Ability to catch Pirate implings with 76 Hunter",
                "Ability to steal from customs lockers",
                "Ability to buy Braindeath 'rum' from The Rusty Anchor Inn",
                "Access to the Rock Island Prison.",
                "Access to a Bank deposit box in Rimmington",
                "Ability to raise Ex-ex-parrot by speaking to Bill Teach and 50 Ships Mufassah (requires 71 Summoning)",
                "Free access to the Brimhaven Agility Arena",
                "Removes need for the Book o' piracy when speaking to pirates on Mos Le'Harmless",
            },
            "spirit_of_summer": {"Access to a new Spirit Realm"},
            "the_dig_site": {"Access through the Varrock Museum back door and gate."},
            "the_golem": {
                "Magic carpet route opened to the ruins of Uzer.",
                "Ability to collect multiple Phoenix feathers",
            },
            "the_grand_tree": {
                "Talk to Historian Minas in the Varrock Museum to receive 5 Kudos."
            },
        }
        expected_missing_mummy_xp = {
            "cooking": 2100.0,
            "construction": 2100.0,
            "thieving": 3000.0,
            "crafting": 3350.0,
            "magic": 5000.0,
            "prayer": 6500.0,
        }
        self.assertEqual(len(non_item_reward_names_by_quest), 24)
        self.assertEqual(sum(map(len, non_item_reward_names_by_quest.values())), 47)
        self.assertLessEqual(
            set(expected_rewards) | set(non_item_reward_names_by_quest),
            set(QUEST_DATA),
        )
        self.assertTrue(prohibited_reward_names.isdisjoint(quest_reward_items_as_dict()))
        item_definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        self.assertEqual(item_definitions["Tome of xp 2nd ed (3)"].source_item_id, 13160)
        self.assertEqual(item_definitions["Expensive spices"].source_item_id, 23081)
        # Eagles' Peak's "A box trap." reward text normalises onto the real
        # rev-742 item 10008 (the placeable trap with the Lay action), so the
        # quest must keep granting it.
        self.assertEqual(item_definitions["Box trap"].source_item_id, 10008)
        # The strung rabbit foot is a real tradeable rev-742 item 10132 that no
        # quest grants; it is crafted later by hunting rabbits.
        rabbit_foot = item_definitions["Strung rabbit foot"]
        self.assertEqual(rabbit_foot.source_item_id, 10132)
        self.assertFalse(rabbit_foot.stackable)
        self.assertTrue(rabbit_foot.tradeable)
        for quest in QUEST_DATA.values():
            granted = dict(quest["rewards"])
            self.assertNotIn("Strung rabbit foot", granted)
        # Replacement-tuple quests get their exact pins in
        # test_quest_replacement_tuples_pin_the_complete_reward_and_unlock_sets;
        # the samples here stay deliberately partial for quests without one.
        for quest_id, expected in expected_unlocks.items():
            self.assertTrue(expected.issubset(set(QUEST_DATA[quest_id]["unlocks"])))
        # The "A box trap." override must stay: without it the name falls back
        # to a junk string even though Hunter data independently defines item
        # 10008 and keeps this dictionary green.
        self.assertNotIn("A box trap.", quest_reward_items_as_dict())

        for quest_id, quest in QUEST_DATA.items():
            with self.subTest(quest_id=quest_id):
                player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                player_data["quests"][quest_id] = {
                    "started": True,
                    "progress": quest["stages"],
                    "completed": False,
                }
                inventory_before = dict(player_data["inventory"])
                xp_before = {
                    skill_id: player_data[f"{skill_id}_exp"]
                    for skill_id in expected_missing_mummy_xp
                }

                completed_data, progressed, completed = apply_quest_progress_pure(
                    player_data,
                    quest_id,
                    QUEST_DATA,
                )
                granted = {
                    item_name: amount - inventory_before.get(item_name, 0)
                    for item_name, amount in completed_data["inventory"].items()
                    if amount > inventory_before.get(item_name, 0)
                }

                self.assertTrue(progressed)
                self.assertTrue(completed)
                self.assertTrue(
                    prohibited_reward_names.isdisjoint(granted),
                    f"{quest_id} granted non-item rewards: "
                    f"{sorted(prohibited_reward_names.intersection(granted))}",
                )
                if quest_id in expected_rewards:
                    self.assertEqual(granted, expected_rewards[quest_id])
                if quest_id == "missing_my_mummy":
                    for skill_id, amount in expected_missing_mummy_xp.items():
                        self.assertEqual(
                            completed_data[f"{skill_id}_exp"] - xp_before[skill_id],
                            amount,
                        )
                if quest_id == "nomads_requiem":
                    # The 70 Zeal points are a Soul Wars currency, not an
                    # inventory item; they land on the existing zeal wallet.
                    self.assertEqual(completed_data["soul_wars_zeal"], 70)

    def test_quest_replacement_guards_pin_all_replaced_items_lamps_and_unlocks(self):
        """Pin every item and lamp replacement, and only quests with unlock replacements."""
        self.assertEqual(
            set(QUEST_ITEM_REWARD_REPLACEMENT_GUARD),
            set(QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID),
        )
        self.assertEqual(
            set(QUEST_LAMP_REWARD_REPLACEMENT_GUARD),
            set(QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID),
        )
        self.assertEqual(
            set(QUEST_UNLOCK_REPLACEMENT_GUARD),
            set(QUEST_UNLOCK_REPLACEMENTS_BY_ID),
        )
        for quest_id, expected in QUEST_ITEM_REWARD_REPLACEMENT_GUARD.items():
            with self.subTest(reward_kind="items", quest_id=quest_id):
                self.assertEqual(
                    dict(expected),
                    dict(QUEST_DATA[quest_id]["rewards"]),
                    f"{quest_id} flat completion grant drifted from the pinned revision",
                )
        for quest_id, expected in QUEST_LAMP_REWARD_REPLACEMENT_GUARD.items():
            with self.subTest(reward_kind="lamps", quest_id=quest_id):
                actual = tuple(
                    (
                        reward["display_name"],
                        reward["amount"],
                        tuple(reward["skill_options"]),
                        reward["minimum_level"],
                        reward["source"],
                        reward["source_text"],
                        reward["quantity"],
                    )
                    for reward in QUEST_DATA[quest_id]["lamp_rewards"]
                )
                self.assertEqual(
                    expected,
                    actual,
                    f"{quest_id} lamp reward set drifted from the pinned revision",
                )
        for quest_id, expected in QUEST_UNLOCK_REPLACEMENT_GUARD.items():
            with self.subTest(reward_kind="unlocks", quest_id=quest_id):
                self.assertEqual(
                    expected,
                    frozenset(QUEST_DATA[quest_id]["unlocks"]),
                    f"{quest_id} unlock set drifted from the pinned revision",
                )

    def test_quest_completion_grants_generated_item_rewards(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["cooks_assistant"] = {"started": True, "progress": 4, "completed": False}
        player_data["inventory"]["Top-quality milk"] = 1
        player_data["inventory"]["Extra fine flour"] = 1
        player_data["inventory"]["Super large egg"] = 1
        data, progressed, completed = apply_quest_progress_pure(player_data, "cooks_assistant", QUEST_DATA)

        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertEqual(data["quest_points"], 1)
        self.assertEqual(data["inventory"]["Top-quality milk"], 0)
        self.assertEqual(data["inventory"]["Extra fine flour"], 0)
        self.assertEqual(data["inventory"]["Super large egg"], 0)
        self.assertEqual(data["inventory"]["Coins"], 500)
        self.assertEqual(data["inventory"]["Sardine"], 20)
        self.assertEqual(data["cooking_exp"], 300.0)

    def test_xp_lamp_claim_grants_chosen_trainable_skill(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["mining_level"] = 30
        player_data["quests"]["one_small_favour"] = {"started": True, "progress": 7, "completed": True}
        claimed_data, ok = apply_claim_pure(player_data, "one_small_favour_xp_lamp_1", CLAIM_DATA, "mining")

        self.assertTrue(ok)
        self.assertEqual(claimed_data["mining_exp"], player_data["mining_exp"] + 10000)
        self.assertTrue(claimed_data["claims"]["one_small_favour_xp_lamp_1"]["claimed"])

        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["stolen_hearts"] = {"started": True, "progress": 3, "completed": True}
        claimed_data, ok = apply_claim_pure(player_data, "stolen_hearts_xp_lamp_2", CLAIM_DATA, "agility")

        self.assertTrue(ok)
        self.assertEqual(claimed_data["agility_exp"], player_data["agility_exp"] + 250.0)
        self.assertNotIn("agility_exp", claimed_data["pending_skill_exp_rewards"])
        self.assertTrue(claimed_data["claims"]["stolen_hearts_xp_lamp_2"]["claimed"])

    def test_standard_runecrafting_uses_talisman_capacity_and_does_not_spill_into_pure_essence(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["inventory"]["Air talisman"] = 1
        player_data["inventory"]["Rune essence"] = 20
        player_data["inventory"]["Pure essence"] = 30

        self.assertTrue(can_runecraft_target_pure(
            player_data,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        ))
        new_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "+20 Air rune")
        self.assertAlmostEqual(exp, 100.0)
        self.assertEqual(new_data["inventory"]["Rune essence"], 0)
        self.assertEqual(new_data["inventory"]["Pure essence"], 30)
        self.assertEqual(new_data["inventory"]["Air rune"], 20)

    def test_runecrafting_tiara_and_small_pouch_raise_trip_capacity(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["equipment"]["head"] = "Air tiara"
        player_data["inventory"]["Small pouch"] = 1
        player_data["inventory"]["Rune essence"] = 31

        new_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "+31 Air rune")
        self.assertAlmostEqual(exp, 155.0)
        self.assertEqual(new_data["inventory"]["Rune essence"], 0)
        self.assertEqual(new_data["inventory"]["Air rune"], 31)
        self.assertEqual(new_data["inventory"]["Small pouch"], 1)
        self.assertEqual(new_data["runecrafting_pouches"]["small"], {"degradation": 0})

    def test_talisman_staff_binding_is_irreversible_and_grants_altar_access(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {
            "started": True,
            "progress": 6,
            "completed": True,
        }
        player_data["inventory"]["Runecrafting staff"] = 1
        player_data["inventory"]["Air talisman"] = 1

        bound, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "bind_air_talisman_staff",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertTrue(ok, message)
        self.assertEqual(exp, 0)
        self.assertEqual(bound["inventory"]["Runecrafting staff"], 0)
        self.assertEqual(bound["inventory"]["Air talisman"], 0)
        self.assertEqual(bound["inventory"]["Air talisman staff"], 1)
        self.assertEqual(player_data["inventory"]["Runecrafting staff"], 1)
        self.assertEqual(player_data["inventory"]["Air talisman"], 1)

        bound["equipment"]["weapon"] = "Air talisman staff"
        bound["inventory"]["Air talisman staff"] = 0
        bound["inventory"]["Rune essence"] = 28
        crafted, exp, ok, message = apply_runecrafting_action_pure(
            bound,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )
        self.assertTrue(ok, message)
        self.assertEqual(crafted["inventory"]["Air rune"], 28)
        self.assertEqual(exp, 140)

    def test_talisman_staff_quest_inheritance_and_omni_law_exclusion(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {
            "started": True,
            "progress": 6,
            "completed": True,
        }
        player_data["runecrafting_level"] = 99
        player_data["inventory"].update(
            {"Runecrafting staff": 1, "Cosmic talisman": 1}
        )
        self.assertFalse(
            can_runecraft_target_pure(
                player_data,
                "bind_cosmic_talisman_staff",
                RUNECRAFTING_DATA,
                RUNECRAFTING_POUCH_DATA,
                QUEST_UNLOCK_RULES,
            )
        )
        player_data["quests"]["lost_city"] = {
            "started": True,
            "progress": 6,
            "completed": True,
        }
        self.assertTrue(
            can_runecraft_target_pure(
                player_data,
                "bind_cosmic_talisman_staff",
                RUNECRAFTING_DATA,
                RUNECRAFTING_POUCH_DATA,
                QUEST_UNLOCK_RULES,
            )
        )

        player_data["equipment"]["weapon"] = "Omni-talisman staff"
        self.assertEqual(
            runecrafting_altar_access_source_pure(
                player_data, "air", RUNECRAFTING_DATA
            ),
            "staff",
        )
        self.assertEqual(
            runecrafting_altar_access_source_pure(
                player_data, "law", RUNECRAFTING_DATA
            ),
            "",
        )

    def test_combination_runecrafting_uses_binding_necklace_charge_counter(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["runecrafting_level"] = 23
        player_data["equipment"]["head"] = "Earth tiara"
        player_data["equipment"]["neck"] = "Binding necklace"
        player_data["inventory"]["Pure essence"] = 26
        player_data["inventory"]["Fire rune"] = 26
        player_data["inventory"]["Fire talisman"] = 1

        self.assertEqual(binding_necklace_charges_pure(player_data), 15)
        new_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "combo_lava_at_earth",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "+26 Lava rune")
        self.assertAlmostEqual(exp, 260.0)
        self.assertEqual(new_data["inventory"]["Pure essence"], 0)
        self.assertEqual(new_data["inventory"]["Fire rune"], 0)
        self.assertEqual(new_data["inventory"]["Fire talisman"], 0)
        self.assertEqual(new_data["inventory"]["Lava rune"], 26)
        self.assertEqual(new_data["equipment"]["neck"], "Binding necklace")
        self.assertEqual(new_data["item_charges"]["Binding necklace"], 14)

    def test_binding_necklace_breaks_at_zero_charges(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["runecrafting_level"] = 23
        player_data["equipment"]["head"] = "Earth tiara"
        player_data["equipment"]["neck"] = "Binding necklace"
        player_data["item_charges"]["Binding necklace"] = 1
        player_data["inventory"]["Pure essence"] = 1
        player_data["inventory"]["Fire rune"] = 1
        player_data["inventory"]["Fire talisman"] = 1

        new_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "combo_lava_at_earth",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "+1 Lava rune")
        self.assertAlmostEqual(exp, 10.0)
        self.assertNotIn("neck", new_data["equipment"])
        self.assertNotIn("Binding necklace", new_data["item_charges"])

    def test_wicked_hood_feed_consumes_access_item_and_unlocks_altar_capacity(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        player_data["inventory"]["Wicked hood"] = 1
        player_data["equipment"]["head"] = "Wicked hood"
        player_data["inventory"]["Air talisman"] = 1
        player_data["inventory"]["Rune essence"] = 28

        fed_data, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "feed_air_talisman_to_hood",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(message, "Air talisman fed")
        self.assertEqual(fed_data["inventory"]["Air talisman"], 0)
        self.assertEqual(fed_data["wicked_hood"]["fed_altars"], ["air"])

        crafted_data, exp, ok, message = apply_runecrafting_action_pure(
            fed_data,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )
        self.assertTrue(ok)
        self.assertEqual(message, "+28 Air rune")
        self.assertAlmostEqual(exp, 140.0)
        self.assertEqual(crafted_data["inventory"]["Rune essence"], 0)
        self.assertEqual(crafted_data["inventory"]["Air rune"], 28)

    def test_fed_altar_access_requires_an_operable_wicked_hood(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["rune_mysteries"] = {
            "started": True,
            "progress": 6,
            "completed": True,
        }
        player_data["wicked_hood"]["fed_altars"] = ["air"]
        player_data["inventory"]["Rune essence"] = 28

        unchanged, exp, ok, message = apply_runecrafting_action_pure(
            player_data,
            "craft_air_runes",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )

        self.assertFalse(ok)
        self.assertEqual(exp, 0)
        self.assertEqual(message, "Runecrafting target is locked: altar access")
        self.assertEqual(unchanged["inventory"]["Rune essence"], 28)

    def test_firemaking_achievements_unlock_from_durable_action_progress(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["achievement_progress"] = {
            "version": 1,
            "skills": {"firemaking": {"outputs": {"Ashes": 1}}},
        }

        newly_completed = get_newly_completed_achievements(player_data, ACHIEVEMENTS)

        self.assertIn("First Fire", newly_completed)

    def test_bank_gear_rows_does_not_auto_replace_from_bank_inventory(self):
        pd = {
            "mining_level": 41,
            "woodcutting_level": 1,
            "inventory": {"Rune pickaxe": 1},
            "toolbelt": {"mining": ["bronze_pickaxe"], "woodcutting": ["bronze_hatchet"]},
            "equipment": {},
        }
        gear = bank_gear_rows_pure(pd, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA, MINING_BONUS_ITEM_DATA)
        pick = dict(gear["toolbelt"])
        self.assertEqual(pick["Pickaxe"], "Bronze pickaxe")
        self.assertEqual(pick["Hatchet"], "Bronze hatchet")
        self.assertEqual(gear["equipped"], [])

    def test_bank_gear_rows_lists_equipped_with_slot(self):
        bonus_id = next(iter(MINING_BONUS_ITEM_DATA))
        pd = {
            "mining_level": 1,
            "woodcutting_level": 1,
            "inventory": {},
            "toolbelt": {"mining": ["bronze_pickaxe"], "woodcutting": ["bronze_hatchet"]},
            "equipment": {"neck": MINING_BONUS_ITEM_DATA[bonus_id]["display_name"]},
        }
        gear = bank_gear_rows_pure(pd, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA, MINING_BONUS_ITEM_DATA)
        self.assertEqual(len(gear["equipped"]), 1)
        slot, name = gear["equipped"][0]
        self.assertEqual(slot, "neck")
        self.assertEqual(name, MINING_BONUS_ITEM_DATA[bonus_id]["display_name"])

    def test_manual_attach_moves_mithril_hatchet_from_bank_to_toolbelt(self):
        inventory, toolbelt, attached = attach_tool_to_toolbelt_pure(
            "Mithril hatchet",
            {"Mithril hatchet": 1},
            {"mining": ["bronze_pickaxe"], "woodcutting": ["bronze_hatchet"]},
            MINING_PICKAXE_DATA,
            WOODCUTTING_AXE_DATA,
        )

        self.assertTrue(attached)
        self.assertNotIn("Mithril hatchet", inventory)
        self.assertEqual(
            toolbelt["woodcutting"],
            ["bronze_hatchet", "mithril_hatchet"],
        )

    def test_manual_attach_registers_inferno_adze_for_both_tool_families(self):
        inventory, toolbelt, attached = attach_tool_to_toolbelt_pure(
            "Inferno adze",
            {"Inferno adze": 1},
            {
                "mining": ["bronze_pickaxe"],
                "woodcutting": ["bronze_hatchet"],
            },
            MINING_PICKAXE_DATA,
            WOODCUTTING_AXE_DATA,
        )

        self.assertTrue(attached)
        self.assertNotIn("Inferno adze", inventory)
        self.assertIn("inferno_adze", toolbelt["mining"])
        self.assertIn("inferno_adze", toolbelt["woodcutting"])

    def test_bank_gear_rows_discloses_attached_tool_blocked_by_level(self):
        pd = {
            "mining_level": 1,
            "woodcutting_level": 1,
            "inventory": {},
            "toolbelt": {
                "mining": ["bronze_pickaxe"],
                "woodcutting": ["bronze_hatchet", "mithril_hatchet"],
            },
            "equipment": {},
        }
        gear = bank_gear_rows_pure(pd, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA, MINING_BONUS_ITEM_DATA)

        self.assertEqual(dict(gear["toolbelt"])["Hatchet"], "Bronze hatchet")
        self.assertIn(("Hatchet", "Mithril hatchet", "Woodcutting", 21), gear["toolbelt_blocked"])

    def test_bank_gear_rows_attached_tool_becomes_active_at_its_level(self):
        pd = {
            "mining_level": 1,
            "woodcutting_level": 21,
            "inventory": {},
            "toolbelt": {
                "mining": ["bronze_pickaxe"],
                "woodcutting": ["bronze_hatchet", "mithril_hatchet"],
            },
            "equipment": {},
        }
        gear = bank_gear_rows_pure(pd, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA, MINING_BONUS_ITEM_DATA)

        self.assertEqual(dict(gear["toolbelt"])["Hatchet"], "Mithril hatchet")
        self.assertEqual(gear["toolbelt_blocked"], [])

    def test_bank_gear_rows_discloses_blocked_attached_pickaxe(self):
        pd = {
            "mining_level": 1,
            "woodcutting_level": 1,
            "inventory": {},
            "toolbelt": {
                "mining": ["bronze_pickaxe", "rune_pickaxe"],
                "woodcutting": ["bronze_hatchet"],
            },
            "equipment": {},
        }
        gear = bank_gear_rows_pure(pd, MINING_PICKAXE_DATA, WOODCUTTING_AXE_DATA, MINING_BONUS_ITEM_DATA)

        self.assertEqual(
            gear["toolbelt_blocked"],
            [("Pickaxe", "Rune pickaxe", "Mining", MINING_PICKAXE_DATA["rune_pickaxe"]["level"])],
        )

if __name__ == "__main__":
    unittest.main()
