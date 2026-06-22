import unittest

from quest_catalog_generated import PRE_EOC_QUEST_CATALOG, PRE_EOC_QUEST_CATALOG_SOURCE
from quest_data import QUESTS, QUESTS_BY_ID, quests_as_dict


class TestQuestCatalog(unittest.TestCase):
    def test_pre_eoc_catalog_has_expected_cutoff_shape(self):
        ids = {quest["id"] for quest in PRE_EOC_QUEST_CATALOG}

        self.assertEqual(PRE_EOC_QUEST_CATALOG_SOURCE["cutoff_date"], "2012-11-20")
        self.assertEqual(len(PRE_EOC_QUEST_CATALOG), 194)
        self.assertEqual(len(QUESTS), 194)
        self.assertEqual(PRE_EOC_QUEST_CATALOG[0]["display_name"], "Cook's Assistant")
        self.assertEqual(PRE_EOC_QUEST_CATALOG[-1]["display_name"], "What's Mine is Yours")

        for quest_id in ("demon_slayer", "imp_catcher", "black_knights_fortress", "rune_mysteries"):
            self.assertIn(quest_id, ids)

        for quest_id in ("dorics_quest", "prince_ali_rescue", "romeo_and_juliet", "rune_memories"):
            self.assertNotIn(quest_id, ids)
        self.assertNotIn("recipe_for_disaster", ids)
        self.assertIn("recipe_for_disaster_another_cooks_quest", ids)
        self.assertIn("recipe_for_disaster_defeating_the_culinaromancer", ids)

    def test_generated_prerequisite_graph_resolves_to_playable_quests(self):
        ids = set(QUESTS_BY_ID)
        data = quests_as_dict()
        missing = []
        self_refs = []
        for quest_id, quest in data.items():
            for requirement in quest.get("required_quests", ()):
                required_id = requirement["quest_id"]
                if required_id not in ids:
                    missing.append((quest_id, required_id))
                if required_id == quest_id:
                    self_refs.append(quest_id)

        self.assertEqual(missing, [])
        self.assertEqual(self_refs, [])
        self.assertIn(
            {"quest_id": "while_guthix_sleeps", "display_name": "While Guthix Sleeps"},
            data["ritual_of_the_mahjarrat"]["required_quests"],
        )
        self.assertIn(
            {"quest_id": "jungle_potion", "display_name": "Jungle Potion"},
            data["shilo_village"]["required_quests"],
        )
        self.assertIn(
            {"quest_id": "recipe_for_disaster_freeing_pirate_pete", "display_name": "Recipe for Disaster: Freeing Pirate Pete"},
            data["recipe_for_disaster_defeating_the_culinaromancer"]["required_quests"],
        )

    def test_priority_overrides_keep_hand_audited_requirements_and_rewards(self):
        data = quests_as_dict()

        lunar = data["lunar_diplomacy"]
        self.assertIn({"quest_id": "rune_mysteries", "display_name": "Rune Mysteries"}, lunar["required_quests"])
        self.assertIn({"quest_id": "shilo_village", "display_name": "Shilo Village"}, lunar["required_quests"])
        self.assertEqual(
            lunar["xp_rewards"],
            ({"skill_id": "magic", "amount": 5000}, {"skill_id": "runecrafting", "amount": 5000}),
        )

        swan_song = data["swan_song"]
        self.assertIn({"quest_id": "one_small_favour", "display_name": "One Small Favour"}, swan_song["required_quests"])
        self.assertEqual(swan_song["required_quest_points"], 101)

    def test_release_order_is_real_game_catalog_order(self):
        data = quests_as_dict()
        ordered = sorted(data.values(), key=lambda quest: quest["release_order"])

        self.assertEqual(ordered[0]["display_name"], "Cook's Assistant")
        self.assertEqual(ordered[1]["display_name"], "Demon Slayer")
        self.assertEqual(ordered[7]["display_name"], "Black Knights' Fortress")
        self.assertEqual(ordered[-1]["display_name"], "What's Mine is Yours")
        self.assertEqual(data["rune_mysteries"]["release_order"], 45)

    def test_knights_sword_stage_requirements_are_machine_readable_override_data(self):
        data = quests_as_dict()
        quest = data["the_knights_sword"]

        self.assertEqual(quest["stages"], 7)
        self.assertEqual(quest["required_items"], {})
        self.assertIn("Used during quest: Redberry pie x1, Blurite ore x1, Iron bar x2", quest["requirements"])
        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}
        self.assertEqual(by_stage[2]["consumed_inventory"], {"Redberry pie": 1})
        self.assertEqual(by_stage[6]["consumed_inventory"], {"Blurite ore": 1, "Iron bar": 2})

    def test_shield_of_arrav_has_source_backed_route_stage_requirements(self):
        data = quests_as_dict()
        quest = data["shield_of_arrav"]

        self.assertEqual(quest["stages"], 12)
        self.assertEqual(quest["rewards"], {"Coins": 1200})
        self.assertEqual(quest["required_items"], {})
        self.assertIn("darkan-world-server", quest["source"])

        stage4 = [row for row in quest["stage_requirements"] if row["stage"] == 4]
        self.assertEqual({row["variant"] for row in stage4}, {"phoenix", "black_arm"})
        self.assertEqual(
            {
                row["variant"]: row["required_routes"]
                for row in stage4
            },
            {
                "phoenix": ("Join the Phoenix Gang",),
                "black_arm": ("Join the Black Arm Gang",),
            },
        )

        combat_rows = [
            encounter
            for requirement in quest["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        ]
        jonny = next(encounter for encounter in combat_rows if encounter["display_name"] == "Jonny the beard")
        self.assertEqual(jonny["level"], 2)
        self.assertEqual(jonny["npc_stats"]["hitpoints"], 80)
        self.assertEqual(jonny["npc_stats"]["attack"], 1)
        self.assertEqual(jonny["npc_configs"]["max_hit"], 10)
        self.assertTrue(jonny["npc_stats_source"].endswith("jonny_the_beard.json"))

        weaponsmaster = next(encounter for encounter in combat_rows if encounter["display_name"] == "Weaponsmaster")
        self.assertEqual(weaponsmaster["level"], 23)
        self.assertEqual(weaponsmaster["npc_stats"]["hitpoints"], 200)
        self.assertEqual(weaponsmaster["npc_stats"]["attack"], 21)
        self.assertEqual(weaponsmaster["npc_configs"]["max_hit"], 50)
        self.assertTrue(weaponsmaster["npc_stats_source"].endswith("weaponsmaster.json"))

        stage10 = next(row for row in quest["stage_requirements"] if row["stage"] == 10)
        self.assertEqual(
            stage10["consumed_inventory"],
            {"Half certificate (Phoenix)": 1, "Half certificate (Black Arm)": 1},
        )
        self.assertEqual(stage10["produced_inventory"], {"Certificate": 1})

    def test_fight_arena_has_source_backed_stage_requirements(self):
        data = quests_as_dict()
        quest = data["fight_arena"]

        self.assertEqual(quest["stages"], 12)
        self.assertEqual(quest["rewards"], {"Coins": 1000})
        self.assertEqual(quest["required_items"], {})
        self.assertIn("darkan-world-server", quest["source"])
        self.assertIn("General Khazard is optional", quest["combat"])

        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}
        self.assertEqual(by_stage[1]["produced_inventory"], {"Khazard helmet": 1, "Khazard armour": 1})
        self.assertEqual(by_stage[2]["required_tools"], {"Khazard helmet": 1, "Khazard armour": 1})
        self.assertEqual(by_stage[4]["consumed_inventory"], {"Coins": 5})
        self.assertEqual(by_stage[4]["produced_inventory"], {"Khali brew": 1})
        self.assertEqual(by_stage[5]["consumed_inventory"], {"Khali brew": 1})
        self.assertEqual(by_stage[6]["produced_inventory"], {"Khazard cell keys": 1})
        self.assertEqual(by_stage[7]["required_tools"], {"Khazard cell keys": 1})
        self.assertEqual(by_stage[11]["required_actions"], ("Return to Lady Servil for the reward",))

        ogre = by_stage[8]["combat_encounters"][0]
        self.assertEqual(ogre["display_name"], "Khazard ogre")
        self.assertEqual(ogre["level"], 63)
        self.assertEqual(ogre["npc_stats"], {"hitpoints": 600})
        self.assertEqual(ogre["npc_configs"]["max_hit"], 1)
        self.assertTrue(ogre["npc_stats_source"].endswith("khazard_ogre (nostats).json"))

        scorpion = by_stage[9]["combat_encounters"][0]
        self.assertEqual(scorpion["display_name"], "Khazard scorpion")
        self.assertEqual(scorpion["level"], 44)
        self.assertEqual(scorpion["npc_stats"], {"hitpoints": 400})
        self.assertEqual(scorpion["npc_configs"]["max_hit"], 50)
        self.assertTrue(scorpion["npc_stats_source"].endswith("khazard_scorpion (nostats) (noanims).json"))

        bouncer = by_stage[10]["combat_encounters"][0]
        self.assertEqual(bouncer["display_name"], "Bouncer")
        self.assertEqual(bouncer["level"], 137)
        self.assertEqual(bouncer["npc_stats"]["attack"], 120)
        self.assertEqual(bouncer["npc_stats"]["strength"], 120)
        self.assertEqual(bouncer["npc_configs"]["max_hit"], 140)
        self.assertTrue(bouncer["npc_stats_source"].endswith("bouncer_(137).json"))

    def test_merlins_crystal_has_source_backed_stage_requirements(self):
        data = quests_as_dict()
        quest = data["merlins_crystal"]

        self.assertEqual(quest["stages"], 8)
        self.assertEqual(quest["rewards"], {})
        self.assertEqual(quest["required_items"], {})
        self.assertIn("darkan-world-server", quest["source"])
        self.assertIn("Thrantax is bound through ritual dialogue rather than killed", quest["combat"])

        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}
        self.assertEqual(by_stage[1]["required_inventory"], {})
        self.assertEqual(
            by_stage[1]["required_actions"],
            ("Complete the round-table investigation with Sir Gawain, Sir Lucan, and Sir Lancelot",),
        )
        self.assertEqual(by_stage[2]["required_routes"], ("Reach Keep Le Faye through the Catherby crate delivery",))

        mordred = by_stage[3]["combat_encounters"][0]
        self.assertEqual(mordred["encounter_id"], "merlins_crystal_sir_mordred_39")
        self.assertEqual(mordred["display_name"], "Sir Mordred")
        self.assertEqual(mordred["level"], 39)
        self.assertEqual(
            mordred["npc_stats"],
            {"hitpoints": 500, "attack": 33, "strength": 33, "defence": 33, "magic": 1, "ranged": 1},
        )
        self.assertEqual(mordred["npc_configs"]["max_hit"], 57)
        self.assertEqual(mordred["npc_configs"]["attack_style"], "melee")
        self.assertTrue(mordred["npc_stats_source"].endswith("sir_mordred (noanims).json"))

        self.assertEqual(by_stage[4]["required_inventory"], {"Bucket": 1, "Insect repellent": 1})
        self.assertEqual(by_stage[4]["consumed_inventory"], {"Bucket": 1})
        self.assertEqual(by_stage[4]["produced_inventory"], {"Bucket of wax": 1})
        self.assertEqual(
            by_stage[4]["required_actions"],
            ("Question Morgan Le Faye about Excalibur and the binding words",),
        )
        self.assertEqual(by_stage[5]["consumed_inventory"], {"Bucket of wax": 1})
        self.assertEqual(by_stage[5]["produced_inventory"], {"Black candle": 1})
        self.assertEqual(by_stage[6]["consumed_inventory"], {"Bread": 1})
        self.assertEqual(by_stage[6]["produced_inventory"], {"Excalibur": 1})
        self.assertEqual(by_stage[7]["required_inventory"], {"Bat bones": 1, "Black candle": 1})
        self.assertEqual(by_stage[7]["consumed_inventory"], {"Bat bones": 1, "Black candle": 1})
        self.assertEqual(by_stage[7]["produced_inventory"], {"Lit black candle": 1})
        self.assertEqual(by_stage[7]["required_tools"], {"Tinderbox": 1, "Excalibur": 1})
        self.assertEqual(
            by_stage[7]["required_actions"],
            (
                "Read the chaos altar inscription",
                "Bind Thrantax with Snarthon Candtrick Termanto",
                "Shatter Merlin's crystal with Excalibur",
                "Report Merlin's freedom to King Arthur",
            ),
        )
        self.assertNotIn(8, by_stage)

    def test_generated_catalog_stage_requirements_cover_items_and_combat(self):
        data = quests_as_dict()

        quests_with_stage_requirements = [
            quest_id for quest_id, quest in data.items() if quest["stage_requirements"]
        ]
        quests_with_combat = [
            quest_id
            for quest_id, quest in data.items()
            if any(requirement["combat_encounters"] for requirement in quest["stage_requirements"])
        ]
        quests_with_item_requirements = [
            quest_id
            for quest_id, quest in data.items()
            if any(
                requirement["required_inventory"]
                or requirement["required_tools"]
                or requirement["required_inventory_options"]
                for requirement in quest["stage_requirements"]
            )
        ]

        self.assertEqual(len(quests_with_stage_requirements), 194)
        self.assertGreaterEqual(len(quests_with_combat), 110)
        self.assertGreaterEqual(len(quests_with_item_requirements), 160)

        cooks = data["cooks_assistant"]["stage_requirements"][0]
        self.assertEqual(cooks["stage"], 1)
        self.assertEqual(
            cooks["consumed_inventory"],
            {"Top-quality milk": 1, "Extra fine flour": 1, "Super large egg": 1},
        )

        vampyre_by_stage = {row["stage"]: row for row in data["vampyre_slayer"]["stage_requirements"]}
        self.assertEqual(vampyre_by_stage[2]["consumed_inventory"], {"Beer": 1})
        self.assertEqual(vampyre_by_stage[2]["produced_inventory"], {"Stake": 1, "Stake hammer": 1})
        vampyre = vampyre_by_stage[3]
        self.assertEqual(vampyre["required_inventory"], {"Stake": 1})
        self.assertEqual(vampyre["consumed_inventory"], {"Stake": 1})
        self.assertEqual(vampyre["required_tools"], {"Stake hammer": 1})
        count_draynor = vampyre["combat_encounters"][0]
        self.assertEqual(count_draynor["display_name"], "Count Draynor")
        self.assertEqual(count_draynor["level"], 37)
        self.assertEqual(count_draynor["npc_stats"]["hitpoints"], 350)
        self.assertTrue(count_draynor["npc_stats_source"].endswith("count_draynor_level_37.plugin.kts"))

        goblin = data["goblin_diplomacy"]
        self.assertEqual(goblin["stages"], 4)
        goblin_by_stage = {row["stage"]: row for row in goblin["stage_requirements"]}
        self.assertEqual(goblin_by_stage[1]["consumed_inventory"], {"Orange goblin mail": 1})
        self.assertEqual(goblin_by_stage[2]["consumed_inventory"], {"Blue goblin mail": 1})
        self.assertEqual(goblin_by_stage[3]["consumed_inventory"], {"Goblin mail": 1})
        self.assertEqual(goblin_by_stage[1]["required_inventory_options"], ())

        ernest = data["ernest_the_chicken"]
        self.assertEqual(ernest["stages"], 9)
        ernest_by_stage = {row["stage"]: row for row in ernest["stage_requirements"]}
        self.assertEqual(ernest_by_stage[3]["consumed_inventory"], {"Fish food": 1, "Poison": 1})
        self.assertEqual(ernest_by_stage[3]["produced_inventory"], {"Poisoned fish food": 1})
        self.assertEqual(ernest_by_stage[4]["consumed_inventory"], {"Poisoned fish food": 1})
        self.assertEqual(ernest_by_stage[4]["produced_inventory"], {"Pressure gauge": 1})
        self.assertEqual(ernest_by_stage[8]["consumed_inventory"], {"Pressure gauge": 1, "Rubber tube": 1, "Oil can": 1})

        black_knights = data["black_knights_fortress"]
        self.assertEqual(black_knights["stages"], 5)
        self.assertEqual(black_knights["required_quest_points"], 12)
        black_by_stage = {row["stage"]: row for row in black_knights["stage_requirements"]}
        self.assertEqual(black_by_stage[1]["required_tools"], {"Iron chainbody": 1, "Bronze med helm": 1})
        self.assertEqual(black_by_stage[3]["consumed_inventory"], {"Cabbage": 1})

        demon = data["demon_slayer"]
        self.assertEqual(demon["stages"], 9)
        self.assertEqual(demon["point_reward"], 3)
        self.assertEqual(demon["rewards"], {})
        demon_requirements = {requirement["stage"]: requirement for requirement in demon["stage_requirements"]}
        self.assertEqual(demon_requirements[1]["consumed_inventory"], {"Coins": 1})
        self.assertEqual(demon_requirements[3]["consumed_inventory"], {"Bucket of water": 1})
        self.assertEqual(demon_requirements[3]["produced_inventory"], {"Bucket": 1, "Silverlight key": 1})
        self.assertEqual(demon_requirements[4]["consumed_inventory"], {"Bones": 25})
        self.assertEqual(demon_requirements[4]["produced_inventory"], {"Silverlight key": 1})
        self.assertEqual(demon_requirements[5]["produced_inventory"], {"Silverlight key": 1})
        self.assertEqual(demon_requirements[6]["consumed_inventory"], {"Silverlight key": 3})
        self.assertEqual(demon_requirements[6]["produced_inventory"], {"Silverlight": 1})
        self.assertEqual(demon_requirements[7]["required_tools"], {"Silverlight": 1})
        self.assertEqual(
            demon_requirements[8]["required_actions"],
            ("Recite Aber, Gabindo, Purchai, Camerinthum, Carlem",),
        )
        delrith = next(
            encounter
            for requirement in demon["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Delrith"
        )
        self.assertEqual(delrith["level"], 27)
        self.assertEqual(delrith["npc_stats"]["hitpoints"], 70)
        self.assertEqual(delrith["npc_stats"]["attack"], 11)
        self.assertEqual(delrith["npc_stats"]["strength"], 10)
        self.assertEqual(delrith["npc_stats"]["defence"], 5)
        self.assertEqual(delrith["npc_configs"]["max_hit"], 30)
        self.assertEqual(delrith["npc_configs"]["attack_style"], "melee")
        self.assertIn("darkan-world-server", delrith["npc_stats_source"])
        self.assertTrue(delrith["npc_stats_source"].endswith("delrith (nostats).json"))

        dragon_slayer = data["dragon_slayer"]
        self.assertEqual(dragon_slayer["stages"], 16)
        self.assertEqual(dragon_slayer["required_quest_points"], 32)
        dragon_by_stage = {row["stage"]: row for row in dragon_slayer["stage_requirements"]}
        self.assertEqual(dragon_by_stage[3]["produced_inventory"], {"Maze key": 1})
        self.assertEqual(dragon_by_stage[4]["produced_inventory"], {"Anti-dragon shield": 1})
        self.assertEqual(dragon_by_stage[5]["required_tools"], {"Maze key": 1})
        self.assertEqual(dragon_by_stage[5]["produced_inventory"], {"Map part": 1})
        self.assertEqual(dragon_by_stage[6]["consumed_inventory"], {"Coins": 10000})
        self.assertEqual(dragon_by_stage[6]["produced_inventory"], {"Map part": 1})
        self.assertEqual(
            dragon_by_stage[8]["consumed_inventory"],
            {"Wizard's mind bomb": 1, "Silk": 1, "Bowl (unfired)": 1},
        )
        self.assertEqual(
            dragon_by_stage[8]["consumed_inventory_options"],
            (({"Crayfish cage": 1}, {"Lobster pot": 1}),),
        )
        self.assertEqual(dragon_by_stage[9]["consumed_inventory"], {"Map part": 3})
        self.assertEqual(dragon_by_stage[9]["produced_inventory"], {"Crandor map": 1})
        self.assertEqual(dragon_by_stage[10]["consumed_inventory"], {"Coins": 2000})
        self.assertEqual(dragon_by_stage[11]["consumed_inventory"], {"Plank": 3, "Steel nails": 90})
        self.assertEqual(dragon_by_stage[11]["required_tools"], {"Hammer": 1})
        self.assertEqual(dragon_by_stage[12]["consumed_inventory"], {"Crandor map": 1})
        self.assertEqual(dragon_by_stage[14]["required_tools"], {"Anti-dragon shield": 1})
        self.assertEqual(dragon_by_stage[14]["produced_inventory"], {"Elvarg's head": 1})
        self.assertEqual(dragon_by_stage[15]["required_inventory"], {"Elvarg's head": 1})

        combat_rows = [
            encounter
            for requirement in dragon_slayer["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        ]
        self.assertEqual(
            [encounter["display_name"] for encounter in dragon_by_stage[5]["combat_encounters"]],
            ["Zombie rat", "Ghost", "Skeleton", "Zombie", "Melzar the Mad", "Lesser demon"],
        )
        self.assertIn("Elvarg", {encounter["display_name"] for encounter in combat_rows})
        lesser_demon = next(encounter for encounter in combat_rows if encounter["display_name"] == "Lesser demon")
        self.assertEqual(lesser_demon["npc_stats"]["hitpoints"], 790)
        self.assertTrue(lesser_demon["npc_stats_source"].endswith("lesser_demon_lvl_82.plugin.kts"))
        elvarg = next(encounter for encounter in combat_rows if encounter["display_name"] == "Elvarg")
        self.assertEqual(elvarg["npc_stats"]["hitpoints"], 800)
        self.assertEqual(elvarg["npc_stats"]["attack"], 70)
        self.assertEqual(elvarg["npc_configs"]["max_hit"], 100)
        self.assertTrue(elvarg["npc_stats_source"].endswith("elvarg.json"))

        toktz = data["toktz_ket_dill"]
        lava_monster = next(
            encounter
            for requirement in toktz["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["encounter_id"] == "toktz_ket_dill_lava_monster_47"
        )
        self.assertEqual(lava_monster["npc_stats"]["hitpoints"], 260)
        self.assertEqual(lava_monster["npc_stats"]["attack"], 28)
        self.assertEqual(lava_monster["npc_stats"]["strength"], 0)
        self.assertEqual(lava_monster["npc_stats"]["defence"], 38)
        self.assertEqual(lava_monster["npc_stats"]["ranged"], 38)
        self.assertEqual(lava_monster["quantity"], 2)
        self.assertEqual(lava_monster["npc_configs"]["attack_style"], "range")
        self.assertEqual(lava_monster["npc_configs"]["max_hit"], 80)
        self.assertIn("lava_monster_(47) (nostats) (noanims).json", lava_monster["npc_stats_source"])
        self.assertTrue(lava_monster["npc_stats_source"].endswith("developer-information/beasts.txt"))
        fire_monster = next(
            encounter
            for requirement in toktz["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["encounter_id"] == "toktz_ket_dill_fire_monster_47"
        )
        self.assertEqual(fire_monster["quantity"], 2)

        desert_treasure = data["desert_treasure"]
        ice_troll = next(
            encounter
            for requirement in desert_treasure["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["encounter_id"] == "desert_treasure_ice_troll_ice_path_120"
        )
        self.assertEqual(ice_troll["quantity"], 5)

        nomad = data["nomads_requiem"]
        nomad_boss = next(
            encounter
            for requirement in nomad["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["encounter_id"] == "nomads_requiem_nomad_699"
        )
        self.assertEqual(nomad_boss["npc_stats"]["hitpoints"], 10000)
        self.assertEqual(nomad_boss["npc_stats"]["attack"], 75)
        self.assertEqual(nomad_boss["npc_stats"]["strength"], 0)
        self.assertEqual(nomad_boss["npc_stats"]["defence"], 75)
        self.assertEqual(nomad_boss["npc_stats"]["magic"], 75)
        self.assertEqual(nomad_boss["npc_stats"]["ranged"], 75)
        self.assertEqual(nomad_boss["npc_configs"]["attack_style"], "range")
        self.assertEqual(nomad_boss["npc_configs"]["max_hit"], 322)
        self.assertIn("nomad (nostats) (noanims).json", nomad_boss["npc_stats_source"])
        self.assertTrue(nomad_boss["npc_stats_source"].endswith("developer-information/beasts.txt"))

        restless = data["the_restless_ghost"]
        restless_combat = [
            encounter
            for requirement in restless["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        ]
        self.assertEqual(restless_combat[0]["display_name"], "Skeleton warlock")
        self.assertEqual(restless_combat[0]["level"], 11)
        self.assertEqual(restless_combat[0]["npc_stats"]["hitpoints"], 180)
        self.assertEqual(restless_combat[0]["npc_stats"]["magic"], 8)
        self.assertEqual(restless_combat[0]["npc_configs"]["attack_style"], "magic")
        self.assertTrue(restless_combat[0]["npc_stats_source"].endswith("skeleton_warlock_lvl_11.plugin.kts"))

        lost_city = data["lost_city"]
        lost_city_combat = [
            encounter
            for requirement in lost_city["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        ]
        self.assertEqual(lost_city_combat[0]["display_name"], "Tree spirit")
        self.assertEqual(lost_city_combat[0]["level"], 63)
        self.assertEqual(lost_city_combat[0]["npc_stats"]["hitpoints"], 220)
        self.assertEqual(lost_city_combat[0]["npc_stats"]["attack"], 90)
        self.assertEqual(lost_city_combat[0]["npc_stats"]["strength"], 95)
        self.assertEqual(lost_city_combat[0]["npc_stats"]["defence"], 80)
        self.assertEqual(lost_city_combat[0]["npc_configs"]["attack_style"], "melee")
        self.assertTrue(lost_city_combat[0]["npc_stats_source"].endswith("tree_spirit_lv_101.plugin.kts"))
        self.assertNotIn(101, {encounter["level"] for encounter in lost_city_combat})

        elemental_i = data["elemental_workshop_i"]
        earth_elemental = next(
            encounter
            for requirement in elemental_i["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Earth Elemental"
        )
        self.assertEqual(earth_elemental["level"], 35)
        self.assertEqual(earth_elemental["npc_stats"]["hitpoints"], 350)
        self.assertEqual(earth_elemental["npc_stats"]["attack"], 20)
        self.assertEqual(earth_elemental["npc_stats"]["strength"], 35)
        self.assertEqual(earth_elemental["npc_stats"]["defence"], 35)
        self.assertIn("earth_elemental.json", earth_elemental["npc_stats_source"])
        self.assertIn("earth_elemental_rock.json", earth_elemental["npc_stats_source"])

        tai_bwo = data["tai_bwo_wannai_trio"]
        jogre = next(
            encounter
            for requirement in tai_bwo["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Jogre"
        )
        self.assertEqual(jogre["level"], 53)
        self.assertEqual(jogre["npc_stats"]["hitpoints"], 600)
        self.assertTrue(jogre["npc_stats_source"].endswith("jogre_(53).json"))

        swan_song = data["swan_song"]
        queen = next(
            encounter
            for requirement in swan_song["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Sea Troll Queen"
        )
        self.assertEqual(queen["level"], 170)
        self.assertEqual(queen["npc_stats"]["hitpoints"], 2000)
        self.assertTrue(queen["npc_stats_source"].endswith("sea_troll_queen (noanims).json"))

        firebird = next(
            encounter
            for requirement in data["heroes_quest"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Entrana Fire Bird"
        )
        self.assertEqual(firebird["level"], 2)
        self.assertEqual(firebird["npc_stats"]["hitpoints"], 50)
        self.assertEqual(firebird["npc_stats"]["strength"], 1)
        self.assertEqual(firebird["npc_configs"]["attack_style"], "melee")
        self.assertTrue(firebird["npc_stats_source"].endswith("entrana_firebird.json"))

        spirits = [
            encounter
            for requirement in data["spirits_of_the_elid"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        ]
        self.assertEqual(
            [encounter["display_name"] for encounter in spirits],
            ["Black golem", "White golem", "Grey golem"],
        )
        self.assertEqual([encounter["quantity"] for encounter in spirits], [1, 1, 1])
        self.assertEqual(spirits[0]["npc_stats"]["hitpoints"], 800)
        self.assertEqual(spirits[0]["npc_stats"]["strength"], 30)
        self.assertEqual(spirits[0]["npc_configs"]["max_hit"], 90)
        self.assertTrue(spirits[0]["npc_stats_source"].endswith("black_golem (noanims).json"))

        priest = data["priest_in_peril"]
        self.assertEqual(priest["stages"], 9)
        self.assertEqual(priest["rewards"], {"Wolfbane dagger": 1})
        self.assertEqual(priest["unlocks"], ("Access to Morytania",))
        priest_by_stage = {requirement["stage"]: requirement for requirement in priest["stage_requirements"]}
        self.assertEqual(tuple(priest_by_stage), (1, 2, 3, 4, 5, 6, 7, 8))
        self.assertEqual(
            priest_by_stage[8]["consumed_inventory_options"],
            (({"Rune essence": 50}, {"Pure essence": 25}),),
        )
        self.assertNotIn("Varrock Museum", priest["rewards"])

        dog = priest_by_stage[2]["combat_encounters"][0]
        self.assertEqual(dog["display_name"], "Temple guardian dog")
        self.assertEqual(dog["level"], 30)
        self.assertEqual(dog["npc_stats"]["hitpoints"], 450)
        self.assertEqual(dog["npc_configs"]["max_hit"], 30)
        self.assertEqual(dog["npc_configs"]["magic_damage_immune"], True)
        self.assertTrue(dog["npc_stats_source"].endswith("cerberus (noanims).json"))

        monk = priest_by_stage[5]["combat_encounters"][0]
        self.assertEqual(monk["display_name"], "Monk of Zamorak")
        self.assertEqual(monk["npc_stats"]["hitpoints"], 250)
        self.assertEqual(monk["npc_stats"]["attack"], 25)
        self.assertEqual(monk["npc_stats"]["strength"], 25)
        self.assertEqual(monk["npc_stats"]["defence"], 25)
        self.assertEqual(monk["npc_configs"]["attack_style"], "magic")
        self.assertTrue(monk["npc_stats_source"].endswith("monk_of_zamorak_(30).json"))

        dad = next(
            encounter
            for requirement in data["troll_stronghold"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Dad"
        )
        self.assertEqual(dad["npc_stats"]["hitpoints"], 1200)
        self.assertEqual(dad["npc_stats"]["attack"], 60)
        self.assertEqual(dad["npc_stats"]["strength"], 120)
        self.assertEqual(dad["npc_stats"]["defence"], 50)
        self.assertEqual(dad["npc_configs"]["max_hit"], 275)
        self.assertTrue(dad["npc_stats_source"].endswith("areas/death_plateau/dad.json"))

        witch = data["witchs_house"]
        self.assertEqual(witch["stages"], 12)
        self.assertEqual(witch["required_items"], {})
        witch_by_stage = {requirement["stage"]: requirement for requirement in witch["stage_requirements"]}
        self.assertEqual(witch_by_stage[1]["produced_inventory"], {"Door key": 1})
        self.assertEqual(witch_by_stage[2]["required_tools"], {"Door key": 1})
        self.assertEqual(witch_by_stage[2]["required_actions"], ("Enter the Witch's house with the door key",))
        self.assertEqual(witch_by_stage[3]["produced_inventory"], {"Magnet": 1})
        self.assertEqual(witch_by_stage[4]["consumed_inventory"], {"Cheese": 1})
        self.assertEqual(witch_by_stage[4]["required_tools"], {"Magnet": 1})
        self.assertEqual(
            witch_by_stage[4]["required_actions"],
            ("Use cheese on the mouse hole and attach the magnet to the mouse",),
        )
        self.assertEqual(witch_by_stage[5]["required_routes"], ("Avoid the witch's patrol through the house",))
        self.assertEqual(witch_by_stage[6]["required_tools"], {"Leather gloves": 1})
        self.assertEqual(witch_by_stage[7]["produced_inventory"], {"Backroom key": 1})
        self.assertEqual(witch_by_stage[8]["required_tools"], {"Backroom key": 1})
        self.assertEqual(witch_by_stage[8]["required_actions"], ("Unlock the Witch's shed door with the backroom key",))
        self.assertEqual(witch_by_stage[10]["produced_inventory"], {"Ball": 1})
        self.assertEqual(witch_by_stage[11]["consumed_inventory"], {"Ball": 1})
        self.assertEqual(witch_by_stage[11]["required_actions"], ("Return the ball to Harvey",))
        experiment_forms = [
            encounter
            for requirement in (witch_by_stage[9],)
            for encounter in requirement["combat_encounters"]
        ]
        self.assertEqual(
            [encounter["display_name"] for encounter in experiment_forms],
            [
                "Witch's experiment (Skavid form)",
                "Witch's experiment (Spider form)",
                "Witch's experiment (Bear form)",
                "Witch's experiment (Wolf form)",
            ],
        )
        self.assertEqual([encounter["level"] for encounter in experiment_forms], [19, 30, 42, 53])
        self.assertEqual(experiment_forms[0]["npc_stats"]["hitpoints"], 1130)
        self.assertEqual(experiment_forms[0]["npc_stats"]["attack"], 18)
        self.assertEqual(experiment_forms[0]["npc_stats"]["strength"], 10)
        self.assertEqual(experiment_forms[0]["npc_stats"]["defence"], 19)
        self.assertEqual(experiment_forms[-1]["npc_configs"]["max_hit"], 150)
        self.assertIn("Witch's_House?oldid=6474931", experiment_forms[0]["source"])
        self.assertTrue(experiment_forms[0]["npc_stats_source"].endswith("witch's_experiment_(19) (noanims).json"))

        souls = data["a_souls_bane"]
        souls_by_stage = {requirement["stage"]: requirement for requirement in souls["stage_requirements"]}
        self.assertEqual(souls_by_stage[1]["required_inventory"], {"Rope": 1})
        self.assertEqual(souls_by_stage[2]["required_actions"], ("Fill the rage meter with an anger weapon",))
        self.assertEqual(
            [encounter["display_name"] for encounter in souls_by_stage[3]["combat_encounters"]],
            ["Fear reaper", "Confusion beast", "Hopeless creature"],
        )
        self.assertEqual(
            [encounter["quantity"] for encounter in souls_by_stage[3]["combat_encounters"]],
            [5, 5, 3],
        )
        fear, confusion, hopeless = souls_by_stage[3]["combat_encounters"]
        self.assertEqual(fear["level"], 42)
        self.assertEqual(fear["npc_stats"]["hitpoints"], 570)
        self.assertEqual(fear["npc_stats"]["strength"], 41)
        self.assertEqual(fear["npc_configs"]["attack_style"], "melee")
        self.assertTrue(fear["npc_stats_source"].endswith("fear_reaper_(42) (noanims).json"))
        self.assertEqual(confusion["level"], 43)
        self.assertEqual(confusion["npc_stats"]["hitpoints"], 640)
        self.assertTrue(confusion["npc_stats_source"].endswith("confusion_beast_(43) (noanims).json"))
        self.assertEqual(hopeless["level"], 40)
        self.assertEqual(hopeless["npc_stats"]["hitpoints"], 1)
        self.assertEqual(hopeless["npc_configs"]["max_hit"], 1)
        self.assertTrue(hopeless["npc_stats_source"].endswith("hopeless_creature_(40) (noanims).json"))
        tolna = souls_by_stage[4]["combat_encounters"][0]
        self.assertEqual(tolna["display_name"], "Tolna head")
        self.assertEqual(tolna["level"], 46)
        self.assertEqual(tolna["quantity"], 3)
        self.assertEqual(tolna["npc_stats"]["hitpoints"], 450)
        self.assertEqual(tolna["npc_configs"]["attack_bonus"], "stab_att")
        self.assertTrue(tolna["npc_stats_source"].endswith("tolna (noanims).json"))

        ham_mage = next(
            encounter
            for requirement in data["another_slice_of_h_a_m"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "H.A.M. mage"
        )
        self.assertEqual(ham_mage["level"], 30)
        self.assertEqual(ham_mage["npc_stats"]["hitpoints"], 350)
        self.assertEqual(ham_mage["npc_stats"]["strength"], 0)
        self.assertEqual(ham_mage["npc_stats"]["magic"], 30)
        self.assertEqual(ham_mage["npc_configs"]["attack_style"], "magic")
        self.assertIn("h.a.m._mage (noanims).json", ham_mage["npc_stats_source"])
        self.assertTrue(ham_mage["npc_stats_source"].endswith("developer-information/beasts.txt"))

        ham_ranger = next(
            encounter
            for requirement in data["another_slice_of_h_a_m"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "H.A.M. ranger"
        )
        self.assertEqual(ham_ranger["level"], 30)
        self.assertEqual(ham_ranger["npc_stats"]["hitpoints"], 350)
        self.assertEqual(ham_ranger["npc_stats"]["strength"], 0)
        self.assertEqual(ham_ranger["npc_stats"]["ranged"], 30)
        self.assertEqual(ham_ranger["npc_configs"]["attack_style"], "range")
        self.assertIn("h.a.m._archer (noanims).json", ham_ranger["npc_stats_source"])
        self.assertTrue(ham_ranger["npc_stats_source"].endswith("developer-information/beasts.txt"))

        senior_guard = next(
            encounter
            for requirement in data["death_to_the_dorgeshuun"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Senior H.A.M. guard"
        )
        self.assertEqual(senior_guard["level"], 22)
        self.assertEqual(senior_guard["quantity"], 3)
        self.assertEqual(senior_guard["npc_stats"]["hitpoints"], 300)
        self.assertEqual(senior_guard["npc_stats"]["strength"], 20)
        self.assertEqual(senior_guard["npc_configs"]["max_hit"], 26)
        self.assertEqual(senior_guard["npc_configs"]["attack_bonus"], "crush_att")
        self.assertTrue(senior_guard["npc_stats_source"].endswith("h.a.m._guard_(22) (noanims).json"))

        hand_cannoneer = next(
            encounter
            for requirement in data["forgiveness_of_a_chaos_dwarf"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Chaos dwarf hand cannoneer"
        )
        self.assertEqual(hand_cannoneer["level"], 100)
        self.assertEqual(hand_cannoneer["npc_stats"]["hitpoints"], 1220)
        self.assertEqual(hand_cannoneer["npc_stats"]["defence"], 50)
        self.assertEqual(hand_cannoneer["npc_stats"]["ranged"], 50)
        self.assertEqual(hand_cannoneer["npc_configs"]["attack_style"], "range")
        self.assertIn("chaos_dwarf_hand_cannoneer (nostats).json", hand_cannoneer["npc_stats_source"])
        self.assertTrue(hand_cannoneer["npc_stats_source"].endswith("developer-information/beasts.txt"))

        caitlin = next(
            encounter
            for requirement in data["the_blood_pact"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Caitlin"
        )
        self.assertEqual(caitlin["npc_stats"]["hitpoints"], 20)
        self.assertEqual(caitlin["npc_stats"]["magic"], 1)
        self.assertEqual(caitlin["npc_configs"]["attack_style"], "magic")
        self.assertIn("caitlin (nostats) (noanims).json", caitlin["npc_stats_source"])

        salt_fights = [
            encounter
            for requirement in data["salt_in_the_wound"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        ]
        forgotten_mage = next(encounter for encounter in salt_fights if encounter["display_name"] == "Forgotten mage")
        forgotten_ranger = next(encounter for encounter in salt_fights if encounter["display_name"] == "Forgotten ranger")
        self.assertEqual(forgotten_mage["level"], 74)
        self.assertEqual(forgotten_mage["npc_stats"]["magic"], 70)
        self.assertEqual(forgotten_mage["npc_configs"]["attack_style"], "magic")
        self.assertEqual(forgotten_ranger["level"], 75)
        self.assertEqual(forgotten_ranger["npc_stats"]["ranged"], 70)
        self.assertEqual(forgotten_ranger["npc_configs"]["attack_style"], "range")

        pit_iron_dragon = next(
            encounter
            for requirement in data["love_story"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Pit iron dragon"
        )
        self.assertEqual(pit_iron_dragon["npc_stats"], {})

        void_fights = [
            encounter
            for requirement in data["the_void_stares_back"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        ]
        torcher = next(encounter for encounter in void_fights if encounter["display_name"] == "Torcher")
        defiler = next(encounter for encounter in void_fights if encounter["display_name"] == "Defiler")
        self.assertEqual(torcher["npc_stats"]["magic"], 85)
        self.assertEqual(torcher["npc_configs"]["attack_style"], "magic")
        self.assertTrue(torcher["npc_stats_source"].endswith("torcher_(63) (nostats).json"))
        self.assertEqual(defiler["npc_stats"]["ranged"], 66)
        self.assertEqual(defiler["npc_stats"]["strength"], 0)
        self.assertEqual(defiler["npc_configs"]["attack_style"], "range")
        self.assertTrue(defiler["npc_stats_source"].endswith("defiler_(50) (nostats).json"))

        tokhaar_xil = next(
            encounter
            for requirement in data["the_elder_kiln"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "TokHaar-Xil"
        )
        self.assertEqual(tokhaar_xil["level"], 140)
        self.assertEqual(tokhaar_xil["quantity"], 8)
        self.assertEqual(tokhaar_xil["npc_stats"]["ranged"], 140)
        self.assertEqual(tokhaar_xil["npc_configs"]["attack_style"], "range")
        self.assertIn("fight_kiln/tokhaar-xil.json", tokhaar_xil["npc_stats_source"])
        self.assertTrue(tokhaar_xil["npc_stats_source"].endswith("developer-information/beasts.txt"))

        self.assertTrue(data["jungle_potion"]["stage_requirements"])
        self.assertTrue(data["wolf_whistle"]["stage_requirements"])
        self.assertTrue(data["some_like_it_cold"]["stage_requirements"])

    def test_generated_catalog_enriches_safe_combat_name_matches(self):
        data = quests_as_dict()

        temple_combat = [
            encounter
            for requirement in data["temple_of_ikov"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        ]
        guardians = next(encounter for encounter in temple_combat if encounter["display_name"] == "Guardians of Armadyl")
        self.assertEqual(guardians["level"], 45)
        self.assertEqual(guardians["npc_stats"]["attack"], 37)
        self.assertEqual(guardians["npc_stats"]["strength"], 37)
        self.assertTrue(guardians["npc_stats_source"].endswith("guardian_of_armadyl_(45).json"))

        observatory = next(
            encounter
            for requirement in data["observatory_quest"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Poisonous Spider"
        )
        self.assertEqual(observatory["npc_stats"]["attack"], 28)
        self.assertTrue(observatory["npc_stats_source"].endswith("poison_spider_lvl_31.plugin.kts"))

    def test_dwarf_cannon_has_source_backed_noncombat_stage_requirements(self):
        data = quests_as_dict()
        quest = data["dwarf_cannon"]
        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}

        self.assertEqual(quest["stages"], 11)
        self.assertEqual(quest["combat"], "None.")
        self.assertEqual(quest["xp_rewards"], ({"skill_id": "crafting", "amount": 750.0},))
        self.assertEqual(quest["journal_stages"][11], ("Captain Lawgof gave his recommendation.", "Quest complete!"))
        self.assertEqual(len(quest["stage_requirements"]), 10)
        self.assertTrue(all(not row["combat_encounters"] for row in quest["stage_requirements"]))
        self.assertEqual(by_stage[1]["consumed_inventory"], {"Railing": 6})
        self.assertEqual(by_stage[1]["required_tools"], {"Hammer": 1})
        self.assertEqual(by_stage[3]["consumed_inventory"], {"Dwarf remains": 1})
        self.assertEqual(by_stage[4]["required_routes"], ("Reach the Dwarf Cannon goblin hideout",))
        self.assertEqual(by_stage[5]["required_actions"], ("Rescue Lollk from the goblin hideout",))
        self.assertEqual(by_stage[6]["produced_inventory"], {"Toolkit": 1})
        self.assertEqual(by_stage[7]["required_tools"], {"Toolkit": 1})
        self.assertEqual(by_stage[9]["consumed_inventory"], {"Ammo mould": 1, "Nulodion's notes": 1})
        self.assertIn("DwarfCannon.java", by_stage[1]["source"])

    def test_local_source_batch_quest_stage_replacements_are_structured(self):
        data = quests_as_dict()

        fishing = data["fishing_contest"]
        fishing_by_stage = {row["stage"]: row for row in fishing["stage_requirements"]}
        self.assertEqual(fishing["stages"], 7)
        self.assertEqual(fishing["combat"], "None.")
        self.assertEqual(fishing_by_stage[1]["produced_inventory"], {"Fishing pass": 1})
        self.assertEqual(fishing_by_stage[2]["required_inventory"], {"Fishing pass": 1})
        self.assertEqual(fishing_by_stage[2]["consumed_inventory"], {"Coins": 5})
        self.assertEqual(fishing_by_stage[3]["consumed_inventory"], {"Garlic": 1})
        self.assertEqual(fishing_by_stage[4]["required_tools"], {"Fishing rod": 1})
        self.assertEqual(
            fishing_by_stage[4]["consumed_inventory_options"],
            (({"Red vine worm": 1}, {"Fishing bait": 1}),),
        )
        self.assertEqual(fishing_by_stage[4]["produced_inventory"], {"Raw giant carp": 1})
        self.assertEqual(fishing_by_stage[5]["consumed_inventory"], {"Raw giant carp": 1})
        self.assertEqual(fishing_by_stage[5]["produced_inventory"], {"Fishing trophy": 1})
        self.assertEqual(fishing_by_stage[6]["consumed_inventory"], {"Fishing trophy": 1})

        gertrude = data["gertrudes_cat"]
        gertrude_by_stage = {row["stage"]: row for row in gertrude["stage_requirements"]}
        self.assertEqual(gertrude["stages"], 10)
        self.assertEqual(gertrude["combat"], "None.")
        self.assertEqual(gertrude_by_stage[2]["consumed_inventory"], {"Coins": 100})
        self.assertEqual(gertrude_by_stage[3]["required_routes"], ("Reach Fluffs in the Varrock Lumber Yard",))
        self.assertEqual(gertrude_by_stage[4]["consumed_inventory"], {"Bucket of milk": 1})
        self.assertEqual(gertrude_by_stage[4]["produced_inventory"], {"Bucket": 1})
        self.assertEqual(gertrude_by_stage[5]["consumed_inventory"], {"Raw sardine": 1, "Doogle leaves": 1})
        self.assertEqual(gertrude_by_stage[5]["produced_inventory"], {"Doogle sardine": 1})
        self.assertEqual(gertrude_by_stage[6]["consumed_inventory"], {"Doogle sardine": 1})
        self.assertEqual(gertrude_by_stage[7]["produced_inventory"], {"Three little kittens": 1})
        self.assertEqual(gertrude_by_stage[8]["consumed_inventory"], {"Three little kittens": 1})

        clock = data["clock_tower"]
        clock_by_stage = {row["stage"]: row for row in clock["stage_requirements"]}
        self.assertEqual(clock["stages"], 4)
        self.assertEqual(clock["combat"], "None.")
        self.assertEqual(clock_by_stage[1]["consumed_inventory"], {"Rat poison": 1})
        self.assertEqual(clock_by_stage[2]["required_inventory_options"], (({"Bucket of water": 1}, {"Ice gloves": 1}),))
        self.assertEqual(
            clock_by_stage[2]["consumed_inventory"],
            {"White cog": 1, "Black cog": 1, "Blue cog": 1, "Red cog": 1},
        )

        monks = data["monks_friend"]
        monks_by_stage = {row["stage"]: row for row in monks["stage_requirements"]}
        self.assertEqual(monks["stages"], 6)
        self.assertEqual(monks["combat"], "Optional: two level 21 thieves and a level 25 head thief.")
        self.assertEqual(monks_by_stage[1]["consumed_inventory"], {"Child's blanket": 1})
        self.assertEqual(monks_by_stage[3]["consumed_inventory"], {"Jug of water": 1})
        self.assertEqual(monks_by_stage[4]["consumed_inventory"], {"Logs": 1})

        tribal = data["tribal_totem"]
        tribal_by_stage = {row["stage"]: row for row in tribal["stage_requirements"]}
        self.assertEqual(tribal["stages"], 6)
        self.assertEqual(tribal["combat"], "None.")
        self.assertEqual(tribal_by_stage[2]["required_routes"], ("Reach the Ardougne RPDT depot",))
        self.assertEqual(tribal_by_stage[2]["produced_inventory"], {"Address label": 1})
        self.assertEqual(tribal_by_stage[3]["consumed_inventory"], {"Address label": 1})
        self.assertEqual(tribal_by_stage[4]["produced_inventory"], {"Totem": 1})
        self.assertEqual(tribal_by_stage[5]["consumed_inventory"], {"Totem": 1})

        scorpion = data["scorpion_catcher"]
        scorpion_by_stage = {row["stage"]: row for row in scorpion["stage_requirements"]}
        self.assertEqual(scorpion["stages"], 7)
        self.assertEqual(scorpion["combat"], "You will need to defeat a level 39 jailer.")
        jailer = scorpion_by_stage[3]["combat_encounters"][0]
        self.assertEqual(jailer["display_name"], "Jailer")
        self.assertEqual(jailer["level"], 39)
        self.assertEqual(jailer["npc_stats"]["hitpoints"], 470)
        self.assertTrue(jailer["npc_stats_source"].endswith("jailer.json"))
        self.assertEqual(scorpion_by_stage[6]["consumed_inventory"], {"Scorpion cage": 1})

        sheep = data["sheep_herder"]
        sheep_by_stage = {row["stage"]: row for row in sheep["stage_requirements"]}
        self.assertEqual(sheep["stages"], 4)
        self.assertEqual(sheep["combat"], "None.")
        self.assertEqual(sheep_by_stage[1]["produced_inventory"], {"Sheep feed": 1})
        self.assertEqual(sheep_by_stage[2]["consumed_inventory"], {"Coins": 100})
        self.assertEqual(sheep_by_stage[2]["produced_inventory"], {"Plague jacket": 1, "Plague trousers": 1})
        self.assertEqual(sheep_by_stage[3]["required_inventory"], {"Sheep feed": 1})
        self.assertEqual(
            sheep_by_stage[3]["consumed_inventory"],
            {"Red sheep bones": 1, "Green sheep bones": 1, "Blue sheep bones": 1, "Yellow sheep bones": 1},
        )
        self.assertEqual(
            sheep_by_stage[3]["required_tools"],
            {"Plague jacket": 1, "Plague trousers": 1, "Cattleprod": 1},
        )
        self.assertEqual(sheep_by_stage[3]["required_routes"], ("Reach the Ardougne sheep enclosure",))
        self.assertIn("SheepHerder.kt", sheep_by_stage[3]["source"])

        plague = data["plague_city"]
        plague_by_stage = {row["stage"]: row for row in plague["stage_requirements"]}
        self.assertEqual(plague["stages"], 17)
        self.assertEqual(plague["combat"], "None.")
        self.assertEqual(plague["rewards"], {"A magic scroll": 1})
        self.assertEqual(plague_by_stage[1]["consumed_inventory"], {"Dwellberries": 1})
        self.assertEqual(plague_by_stage[1]["produced_inventory"], {"Gas mask": 1})
        self.assertEqual(plague_by_stage[3]["consumed_inventory"], {"Bucket of water": 4})
        self.assertEqual(plague_by_stage[3]["produced_inventory"], {"Bucket": 4})
        self.assertEqual(plague_by_stage[9]["required_inventory"], {"Picture of Elena": 1})
        self.assertEqual(plague_by_stage[9]["produced_inventory"], {"Turnip growing for beginners": 1})
        self.assertEqual(
            plague_by_stage[14]["consumed_inventory"],
            {"Chocolate dust": 1, "Bucket of milk": 1, "Snape grass": 1},
        )
        self.assertEqual(plague_by_stage[14]["produced_inventory"], {"Hangover cure": 1})
        self.assertEqual(plague_by_stage[15]["produced_inventory"], {"Warrant": 1})
        self.assertEqual(plague_by_stage[16]["required_inventory"], {"Warrant": 1})
        self.assertEqual(plague_by_stage[16]["produced_inventory"], {"A small key": 1})

        waterfall = data["waterfall_quest"]
        waterfall_by_stage = {row["stage"]: row for row in waterfall["stage_requirements"]}
        self.assertEqual(waterfall["stages"], 6)
        self.assertTrue(waterfall["combat"].startswith("None required"))
        self.assertEqual(waterfall_by_stage[2]["produced_inventory"], {"Book on Baxtorian": 1})
        self.assertEqual(waterfall_by_stage[3]["produced_inventory"], {"Old key": 1, "Glarial's pebble": 1})
        self.assertEqual(
            waterfall_by_stage[4]["produced_inventory"],
            {"Large old key": 1, "Glarial's amulet": 1, "Glarial's urn": 1},
        )
        self.assertEqual(waterfall_by_stage[5]["required_inventory"], {"Glarial's urn": 1})
        self.assertEqual(
            waterfall_by_stage[5]["consumed_inventory"],
            {"Water rune": 6, "Air rune": 6, "Earth rune": 6, "Glarial's amulet": 1},
        )

    def test_source_backed_starter_quest_stage_overrides_replace_generated_guesses(self):
        data = quests_as_dict()

        imp = data["imp_catcher"]
        self.assertEqual(imp["rewards"], {"Amulet of accuracy": 1})
        self.assertEqual(
            imp["stage_requirements"][0]["consumed_inventory"],
            {"Black bead": 1, "Red bead": 1, "White bead": 1, "Yellow bead": 1},
        )

        druidic_by_stage = {row["stage"]: row for row in data["druidic_ritual"]["stage_requirements"]}
        self.assertEqual(data["druidic_ritual"]["rewards"], {})
        self.assertEqual(
            druidic_by_stage[2]["consumed_inventory"],
            {"Raw bear meat": 1, "Raw rat meat": 1, "Raw beef": 1, "Raw chicken": 1},
        )
        self.assertEqual(
            druidic_by_stage[2]["produced_inventory"],
            {"Enchanted bear meat": 1, "Enchanted rat meat": 1, "Enchanted beef": 1, "Enchanted chicken": 1},
        )
        self.assertEqual(
            druidic_by_stage[3]["consumed_inventory"],
            {"Enchanted bear meat": 1, "Enchanted rat meat": 1, "Enchanted beef": 1, "Enchanted chicken": 1},
        )

        pirate_by_stage = {row["stage"]: row for row in data["pirates_treasure"]["stage_requirements"]}
        self.assertEqual(data["pirates_treasure"]["rewards"], {"Casket (Pirate's Treasure)": 1})
        self.assertEqual(pirate_by_stage[1]["consumed_inventory"], {"Karamja rum": 1})
        self.assertEqual(pirate_by_stage[1]["produced_inventory"], {"Chest key": 1})
        self.assertEqual(pirate_by_stage[2]["consumed_inventory"], {"Chest key": 1})
        self.assertEqual(pirate_by_stage[2]["produced_inventory"], {"Pirate message": 1})
        self.assertEqual(pirate_by_stage[3]["required_inventory"], {"Pirate message": 1})
        self.assertEqual(pirate_by_stage[3]["required_tools"], {"Spade": 1})

    def test_generated_rewards_journals_and_lamps_are_structured(self):
        data = quests_as_dict()

        cooks = data["cooks_assistant"]
        self.assertEqual(cooks["rewards"]["Coins"], 500)
        self.assertEqual(cooks["rewards"]["Sardine"], 20)
        self.assertGreaterEqual(len(cooks["journal_stages"]), 2)
        self.assertIn("top-quality milk", " ".join(cooks["journal_stages"][1]))

        one_small_favour = data["one_small_favour"]
        self.assertEqual(one_small_favour["lamp_rewards"][0]["quantity"], 2)
        self.assertEqual(one_small_favour["lamp_rewards"][0]["amount"], 10000)
        self.assertEqual(one_small_favour["lamp_rewards"][0]["minimum_level"], 30)

        final_rfd = data["recipe_for_disaster_defeating_the_culinaromancer"]
        rfd_requirements = {req["quest_id"] for req in final_rfd["required_quests"]}
        self.assertIn("recipe_for_disaster_another_cooks_quest", rfd_requirements)
        self.assertIn("recipe_for_disaster_freeing_skrach_uglogwee", rfd_requirements)
        self.assertEqual(final_rfd["lamp_rewards"][0]["amount"], 20000)

    def test_all_generated_quests_have_source_backed_journals(self):
        missing = [
            (quest["id"], quest["display_name"], quest["journal_source_kind"])
            for quest in PRE_EOC_QUEST_CATALOG
            if not quest["journal_stages"] or quest["journal_source_kind"] == "generated_fallback"
        ]

        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
