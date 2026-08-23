import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.firemaking_data import LIT_LIGHT_SOURCE_ITEMS
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG, PRE_EOC_QUEST_CATALOG_SOURCE
from ankiscape.core.constants import ITEM_DEFINITIONS
from ankiscape.data.quest_data import CLAIMS_BY_ID, QUESTS, QUESTS_BY_ID, quest_reward_items_as_dict, quests_as_dict
from tools.audit_quest_local_item_gates import quest_local_gate_candidates


class TestQuestCatalog(unittest.TestCase):
    def test_live_stage_counts_preserve_a_completion_sentinel_after_every_requirement(self):
        live_quests = quests_as_dict()
        for quest_id, quest in live_quests.items():
            max_requirement_stage = max(
                (stage["stage"] for stage in quest["stage_requirements"]),
                default=0,
            )
            with self.subTest(quest_id=quest_id):
                self.assertLess(max_requirement_stage, quest["stages"])

        self.assertEqual(live_quests["tears_of_guthix"]["stages"], 4)
        self.assertEqual(live_quests["land_of_the_goblins"]["stages"], 8)
        self.assertEqual(live_quests["hazeel_cult"]["stages"], 4)

    def test_lantern_quest_gates_use_reachable_exact_item_states(self):
        live_quests = quests_as_dict()
        light_source_stages = {
            "temple_of_ikov": 1,
            "tears_of_guthix": 1,
            "the_lost_tribe": 2,
            "wanted": 5,
            "rag_and_bone_man": 2,
            "land_of_the_goblins": 7,
            "defender_of_varrock": 4,
            "the_chosen_commander": 3,
        }
        for quest_id, expected_stage in light_source_stages.items():
            rows = [
                stage
                for stage in live_quests[quest_id]["stage_requirements"]
                if any(
                    "Bullseye lantern (lit)" in option
                    for group in stage["required_inventory_options"]
                    for option in group
                )
            ]
            self.assertEqual([stage["stage"] for stage in rows], [expected_stage], quest_id)
            allowed_items = tuple(next(iter(option)) for option in rows[0]["required_inventory_options"][-1])
            self.assertEqual(
                allowed_items,
                ("Bullseye lantern (lit)",) if quest_id == "tears_of_guthix" else LIT_LIGHT_SOURCE_ITEMS,
                quest_id,
            )

        generated_and_live_quests = (*PRE_EOC_QUEST_CATALOG, *live_quests.values())
        for quest in generated_and_live_quests:
            for stage in quest["stage_requirements"]:
                self.assertNotIn("Light source", stage["required_inventory"])
                self.assertNotIn("Light sources", stage["required_inventory"])
                self.assertNotIn("Light source", stage["required_tools"])
                self.assertNotIn("Light sources", stage["required_tools"])
                for option_group in stage["required_inventory_options"]:
                    for option in option_group:
                        self.assertNotIn("Light source", option)
                        self.assertNotIn("Light sources", option)
        self.assertNotIn("Light source", quest_reward_items_as_dict())
        self.assertNotIn(
            "Light source x1",
            " ".join(live_quests["temple_of_ikov"]["requirements"]),
        )

        tears_stage = next(
            stage for stage in live_quests["tears_of_guthix"]["stage_requirements"] if stage["stage"] == 2
        )
        self.assertEqual(
            tears_stage["required_inventory"],
            {"Bullseye lantern (empty)": 1, "Sapphire": 1},
        )
        self.assertEqual(tears_stage["required_inventory_options"], ())
        tears_lit_stage = next(
            stage for stage in live_quests["tears_of_guthix"]["stage_requirements"] if stage["stage"] == 3
        )
        self.assertEqual(tears_lit_stage["required_inventory"], {"Sapphire lantern (lit)": 1})

        for quest_id in ("watchtower", "another_slice_of_h_a_m"):
            self.assertFalse(
                any(
                    any("Bullseye lantern (lit)" in option for option in group)
                    for stage in live_quests[quest_id]["stage_requirements"]
                    for group in stage["required_inventory_options"]
                ),
                quest_id,
            )

        wgs_stage = next(
            stage
            for stage in live_quests["while_guthix_sleeps"]["stage_requirements"]
            if stage["stage"] == 6
        )
        self.assertEqual(wgs_stage["required_inventory"], {"Sapphire lantern (lit)": 1})

    def test_pre_eoc_catalog_has_expected_cutoff_shape(self):
        ids = {quest["id"] for quest in PRE_EOC_QUEST_CATALOG}

        self.assertEqual(PRE_EOC_QUEST_CATALOG_SOURCE["cutoff_date"], "2012-11-20")
        self.assertEqual(len(PRE_EOC_QUEST_CATALOG), 194)
        self.assertEqual(len([quest for quest in QUESTS if not quest.miniquest]), 194)
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
        ordered = sorted(
            (quest for quest in data.values() if not quest["miniquest"]),
            key=lambda quest: quest["release_order"],
        )

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

    def test_biohazard_has_source_backed_stage_requirements(self):
        data = quests_as_dict()
        quest = data["biohazard"]

        self.assertEqual(quest["stages"], 14)
        self.assertEqual(quest["required_items"], {})
        self.assertEqual(quest["combat"], "You will need to defeat a level 13 mourner.")
        self.assertEqual(
            tuple(requirement["display_name"] for requirement in quest["required_skills"]),
            ("Agility", "Magic"),
        )

        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}
        self.assertIn("darkan-world-server", by_stage[8]["source"])
        self.assertEqual(by_stage[1]["required_inventory_options"], ())
        self.assertEqual(by_stage[3]["produced_inventory"], {"Bird feed": 1, "Pigeon cage": 1})
        self.assertEqual(by_stage[4]["consumed_inventory"], {"Bird feed": 1})
        self.assertEqual(by_stage[4]["required_tools"], {"Pigeon cage": 1})
        self.assertEqual(by_stage[6]["produced_inventory"], {"Rotten apple": 1})
        self.assertEqual(by_stage[7]["consumed_inventory"], {"Rotten apple": 1})
        self.assertEqual(by_stage[7]["produced_inventory"], {"Doctors' gown": 1})
        self.assertEqual(by_stage[9]["consumed_inventory"], {"Distillator": 1})
        self.assertEqual(
            by_stage[9]["produced_inventory"],
            {"Liquid honey": 1, "Ethenea": 1, "Sulphuric broline": 1, "Plague sample": 1},
        )
        self.assertEqual(by_stage[11]["required_tools"], {"Priest gown": 2})
        self.assertEqual(
            by_stage[11]["consumed_inventory"],
            {"Liquid honey": 1, "Ethenea": 1, "Sulphuric broline": 1, "Plague sample": 1, "Touch paper": 1},
        )

        mourner = by_stage[8]["combat_encounters"][0]
        self.assertEqual(mourner["encounter_id"], "biohazard_mourner_13")
        self.assertEqual(mourner["display_name"], "Mourner")
        self.assertEqual(mourner["level"], 13)
        self.assertEqual(
            mourner["npc_stats"],
            {"hitpoints": 190, "attack": 24, "strength": 24, "defence": 24, "magic": 1, "ranged": 0},
        )
        self.assertEqual(mourner["npc_configs"]["max_hit"], 20)
        self.assertEqual(mourner["npc_configs"]["attack_style"], "melee")
        self.assertTrue(mourner["npc_stats_source"].endswith("mourner_(13).json"))

    def test_heroes_quest_has_source_backed_stage_requirements(self):
        data = quests_as_dict()
        quest = data["heroes_quest"]

        self.assertEqual(quest["stages"], 13)
        self.assertEqual(quest["required_items"], {})
        self.assertEqual(quest["required_quest_points"], 56)
        self.assertIn("Used during quest: Harralander potion (unf) x1", quest["requirements"][11])
        self.assertNotIn("Blamish snail slime", quest["requirements"][11])
        self.assertIn("contextual contact", quest["requirements"][12])
        self.assertEqual(quest["choices"][0]["stage"], 9)
        self.assertEqual(
            tuple(option["route_id"] for option in quest["choices"][0]["options"]),
            ("Join the Phoenix Gang", "Join the Black Arm Gang"),
        )
        self.assertEqual(
            tuple(requirement["quest_id"] for requirement in quest["required_quests"]),
            ("shield_of_arrav", "lost_city", "dragon_slayer", "merlins_crystal", "druidic_ritual"),
        )
        self.assertEqual(
            tuple((requirement["skill_id"], requirement["level"]) for requirement in quest["required_skills"]),
            (("cooking", 53), ("fishing", 53), ("herblore", 25), ("defense", 25), ("mining", 50)),
        )

        rows = quest["stage_requirements"]
        by_stage = {row["stage"]: row for row in rows if not row["variant"]}
        by_stage_variant = {(row["stage"], row["variant"]): row for row in rows if row["variant"]}
        self.assertEqual(by_stage[2]["produced_inventory"], {"Blamish snail slime": 1})
        self.assertEqual(
            by_stage[3]["consumed_inventory"],
            {"Blamish snail slime": 1, "Harralander potion (unf)": 1},
        )
        self.assertEqual(by_stage[3]["produced_inventory"], {"Blamish oil": 1})
        self.assertEqual(by_stage[4]["consumed_inventory"], {"Blamish oil": 1, "Fishing rod": 1})
        self.assertEqual(by_stage[4]["produced_inventory"], {"Oily fishing rod": 1})
        self.assertEqual(by_stage[5]["required_tools"], {"Oily fishing rod": 1})
        self.assertEqual(by_stage[5]["consumed_inventory"], {"Fishing bait": 1})
        self.assertEqual(by_stage[5]["produced_inventory"], {"Raw lava eel": 1})
        self.assertEqual(by_stage[6]["consumed_inventory"], {"Raw lava eel": 1})
        self.assertEqual(by_stage[6]["produced_inventory"], {"Lava eel": 1})
        self.assertEqual(by_stage[7]["required_tools"], {"Pickaxe": 1})
        self.assertEqual(by_stage[7]["produced_inventory"], {"Ice gloves": 1})
        self.assertEqual(by_stage[8]["required_tools"], {"Ice gloves": 1})
        self.assertEqual(by_stage[8]["produced_inventory"], {"Fire feather": 1})

        ice_queen = by_stage[7]["combat_encounters"][0]
        self.assertEqual(ice_queen["encounter_id"], "heroes_quest_ice_queen_111")
        self.assertEqual(ice_queen["npc_stats"]["hitpoints"], 1050)
        self.assertTrue(ice_queen["npc_stats_source"].endswith("ice_queen.json"))
        firebird = by_stage[8]["combat_encounters"][0]
        self.assertEqual(firebird["encounter_id"], "heroes_quest_entrana_fire_bird_2")
        self.assertTrue(firebird["npc_stats_source"].endswith("entrana_firebird.json"))

        black_arm_setup = by_stage_variant[(9, "black_arm")]
        phoenix_setup = by_stage_variant[(9, "phoenix")]
        self.assertEqual(black_arm_setup["produced_inventory"], {"Id papers": 1})
        self.assertEqual(black_arm_setup["required_routes"], ("Join the Black Arm Gang",))
        self.assertEqual(phoenix_setup["required_routes"], ("Join the Phoenix Gang",))

        black_arm_mansion = by_stage_variant[(10, "black_arm")]
        self.assertEqual(
            black_arm_mansion["required_tools"],
            {"Black full helm": 1, "Black platebody": 1, "Black platelegs": 1},
        )
        self.assertEqual(black_arm_mansion["consumed_inventory"], {"Id papers": 1})
        self.assertEqual(black_arm_mansion["produced_inventory"], {"Pete's candlestick": 1})
        phoenix_mansion = by_stage_variant[(10, "phoenix")]
        self.assertEqual(phoenix_mansion["consumed_inventory"], {"Coins": 1000})
        self.assertNotIn("Coordinate with a Black Arm partner", phoenix_mansion["required_actions"])
        self.assertEqual(phoenix_mansion["produced_inventory"], {"Pete's candlestick": 1})
        self.assertEqual(phoenix_mansion["combat_encounters"][0]["encounter_id"], "heroes_quest_grip_22")

        self.assertEqual(by_stage_variant[(11, "black_arm")]["produced_inventory"], {"Thieves' armband": 1})
        self.assertEqual(by_stage_variant[(11, "phoenix")]["produced_inventory"], {"Thieves' armband": 1})
        self.assertEqual(
            by_stage[12]["consumed_inventory"],
            {"Lava eel": 1, "Thieves' armband": 1, "Fire feather": 1},
        )

    def test_family_crest_has_source_backed_stage_requirements(self):
        data = quests_as_dict()
        quest = data["family_crest"]

        self.assertEqual(quest["stages"], 16)
        self.assertEqual(quest["required_items"], {})
        self.assertEqual(quest["rewards"], {"Family gauntlets": 1})
        self.assertIn("Used during quest: Shrimps x1", quest["requirements"][4])
        self.assertIn("Ruby x2", quest["requirements"][4])
        self.assertIn("level 170", quest["combat"])
        self.assertIn("level 84", quest["combat"])
        self.assertEqual(
            tuple((requirement["skill_id"], requirement["level"]) for requirement in quest["required_skills"]),
            (("crafting", 40), ("magic", 59), ("mining", 40), ("smithing", 40)),
        )

        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}
        self.assertIn("darkan-world-server", by_stage[3]["source"])
        self.assertEqual(
            by_stage[3]["consumed_inventory"],
            {"Shrimps": 1, "Salmon": 1, "Tuna": 1, "Bass": 1, "Swordfish": 1},
        )
        self.assertEqual(by_stage[3]["produced_inventory"], {"Caleb crest": 1})
        self.assertEqual(by_stage[8]["required_tools"], {"Pickaxe": 1})
        self.assertEqual(by_stage[8]["produced_inventory"], {"Perfect gold ore": 2})
        self.assertEqual(by_stage[9]["consumed_inventory"], {"Perfect gold ore": 2})
        self.assertEqual(by_stage[9]["produced_inventory"], {"Perfect gold bar": 2})
        self.assertEqual(by_stage[10]["consumed_inventory"], {"Perfect gold bar": 2, "Ruby": 2})
        self.assertEqual(by_stage[10]["required_tools"], {"Ring mould": 1, "Necklace mould": 1})
        self.assertEqual(
            by_stage[10]["produced_inventory"],
            {"Perfect ruby ring": 1, "Perfect ruby necklace": 1},
        )
        self.assertEqual(by_stage[11]["consumed_inventory"], {"Perfect ruby ring": 1, "Perfect ruby necklace": 1})
        self.assertEqual(by_stage[11]["produced_inventory"], {"Avan crest": 1})
        self.assertEqual(by_stage[12]["required_inventory"], {"Antipoison": 1})
        self.assertEqual(by_stage[12]["required_tools"], {"Caleb crest": 1, "Avan crest": 1})
        self.assertEqual(by_stage[13]["produced_inventory"], {"Johnathon crest": 1})
        self.assertEqual(
            by_stage[14]["consumed_inventory"],
            {"Caleb crest": 1, "Avan crest": 1, "Johnathon crest": 1},
        )
        self.assertEqual(by_stage[14]["produced_inventory"], {"Family crest": 1})
        self.assertEqual(by_stage[15]["consumed_inventory"], {"Family crest": 1})

        chronozon = by_stage[13]["combat_encounters"][0]
        self.assertEqual(chronozon["encounter_id"], "family_crest_chronozon_170")
        self.assertEqual(chronozon["display_name"], "Chronozon")
        self.assertEqual(chronozon["level"], 170)
        self.assertEqual(
            chronozon["npc_stats"],
            {"hitpoints": 600, "attack": 173, "strength": 172, "defence": 173, "magic": 1, "ranged": 1},
        )
        self.assertEqual(chronozon["npc_configs"]["max_hit"], 180)
        self.assertEqual(chronozon["npc_configs"]["attack_style"], "melee")
        self.assertTrue(chronozon["npc_stats_source"].endswith("chronozon (noanims).json"))

    def test_temple_of_ikov_has_source_backed_stage_requirements(self):
        data = quests_as_dict()
        quest = data["temple_of_ikov"]

        self.assertEqual(quest["stages"], 11)
        self.assertEqual(quest["required_items"], {})
        self.assertEqual(quest["rewards"], {"Shiny key": 1})
        self.assertEqual(
            tuple((requirement["skill_id"], requirement["level"]) for requirement in quest["required_skills"]),
            (("thieving", 42),),
        )
        self.assertIn("Fire Warrior of Lesarkus (level 84)", quest["combat"])
        self.assertIn("Guardian of Armadyl (level 45)", quest["combat"])
        self.assertIn("Lucien (level 14)", quest["combat"])
        self.assertEqual(quest["choices"][0]["stage"], 9)
        self.assertEqual(
            tuple(option["route_id"] for option in quest["choices"][0]["options"]),
            ("Side with the Guardians of Armadyl", "Side with Lucien"),
        )

        by_stage = {row["stage"]: row for row in quest["stage_requirements"] if not row["variant"]}
        by_stage_variant = {(row["stage"], row["variant"]): row for row in quest["stage_requirements"]}

        self.assertEqual(by_stage[1]["required_inventory"], {})
        self.assertEqual(
            tuple(next(iter(option)) for option in by_stage[1]["required_inventory_options"][0]),
            LIT_LIGHT_SOURCE_ITEMS,
        )
        self.assertEqual(by_stage[1]["required_tools"], {"Pendant of lucien": 1})
        self.assertEqual(by_stage[2]["required_tools"], {"Knife": 1})
        self.assertEqual(by_stage[2]["produced_inventory"], {"Boots of lightness": 1})
        self.assertEqual(by_stage[3]["produced_inventory"], {"Lever": 1})
        self.assertEqual(by_stage[4]["consumed_inventory"], {"Lever": 1})
        self.assertEqual(by_stage[5]["produced_inventory"], {"Ice arrows": 1})
        self.assertEqual(by_stage[7]["required_tools"], {"Ice arrows": 1})
        self.assertEqual(
            by_stage[7]["required_inventory_options"],
            ((
                {"Yew shortbow": 1},
                {"Yew longbow": 1},
                {"Yew comp bow": 1},
                {"Magic shortbow": 1},
                {"Magic longbow": 1},
                {"Magic comp bow": 1},
                {"Dark bow": 1},
            ),),
        )
        self.assertEqual(by_stage[8]["consumed_inventory"], {"Limpwurt root": 20})

        fire_warrior = by_stage[7]["combat_encounters"][0]
        self.assertEqual(fire_warrior["encounter_id"], "temple_of_ikov_fire_warrior_of_lesarkus_84")
        self.assertEqual(fire_warrior["display_name"], "Fire Warrior of Lesarkus")
        self.assertEqual(fire_warrior["level"], 84)
        self.assertEqual(fire_warrior["npc_stats"]["hitpoints"], 590)
        self.assertEqual(fire_warrior["npc_configs"]["attack_style"], "magic")

        guardian_branch = by_stage_variant[(9, "guardians")]
        lucien_branch = by_stage_variant[(9, "lucien")]
        self.assertEqual(guardian_branch["required_routes"], ("Side with the Guardians of Armadyl",))
        self.assertEqual(guardian_branch["produced_inventory"], {"Armadyl pendant": 1})
        self.assertEqual(lucien_branch["required_routes"], ("Side with Lucien",))
        self.assertEqual(lucien_branch["produced_inventory"], {"Staff of armadyl": 1})
        self.assertEqual(lucien_branch["combat_encounters"][0]["encounter_id"], "temple_of_ikov_guardian_of_armadyl_45")

        guardian_finish = by_stage_variant[(10, "guardians")]
        lucien_finish = by_stage_variant[(10, "lucien")]
        self.assertEqual(guardian_finish["required_tools"], {"Armadyl pendant": 1})
        self.assertEqual(guardian_finish["combat_encounters"][0]["encounter_id"], "temple_of_ikov_lucien_14")
        self.assertEqual(lucien_finish["consumed_inventory"], {"Staff of armadyl": 1})

    def test_holy_grail_has_source_backed_stage_requirements(self):
        data = quests_as_dict()
        quest = data["holy_grail"]

        self.assertEqual(quest["stages"], 11)
        self.assertEqual(quest["required_items"], {})
        self.assertEqual(quest["rewards"], {})
        self.assertNotIn("Brimhaven", str(quest["stage_requirements"]))
        self.assertIn("Black Knight Titan (level 120)", quest["combat"])
        self.assertEqual(
            tuple((requirement["skill_id"], requirement["level"]) for requirement in quest["required_skills"]),
            (("attack", 20),),
        )
        self.assertEqual(
            tuple(requirement["quest_id"] for requirement in quest["required_quests"]),
            ("merlins_crystal",),
        )
        self.assertEqual(
            quest["xp_rewards"],
            ({"skill_id": "defense", "amount": 15300.0}, {"skill_id": "prayer", "amount": 11000.0}),
        )

        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}
        self.assertEqual(by_stage[3]["produced_inventory"], {"Holy table napkin": 1})
        self.assertEqual(by_stage[4]["required_tools"], {"Holy table napkin": 1})
        self.assertEqual(by_stage[4]["produced_inventory"], {"Magic whistle": 2})
        self.assertEqual(by_stage[5]["required_tools"], {"Magic whistle": 1, "Excalibur": 1})
        self.assertEqual(by_stage[5]["produced_inventory"], {"Grail bell": 1})
        self.assertEqual(by_stage[6]["required_tools"], {"Grail bell": 1})
        self.assertEqual(by_stage[7]["produced_inventory"], {"Magic gold feather": 1})
        self.assertEqual(by_stage[8]["consumed_inventory"], {"Magic whistle": 1})
        self.assertEqual(by_stage[8]["required_tools"], {"Magic gold feather": 1})
        self.assertEqual(by_stage[9]["produced_inventory"], {"Holy grail": 1})
        self.assertEqual(by_stage[10]["consumed_inventory"], {"Holy grail": 1})

        titan = by_stage[5]["combat_encounters"][0]
        self.assertEqual(titan["encounter_id"], "holy_grail_black_knight_titan_120")
        self.assertEqual(titan["display_name"], "Black Knight Titan")
        self.assertEqual(titan["level"], 120)
        self.assertEqual(
            titan["npc_stats"],
            {"hitpoints": 1420, "attack": 91, "strength": 100, "defence": 91, "magic": 1, "ranged": 1},
        )
        self.assertEqual(titan["npc_configs"]["max_hit"], 150)
        self.assertEqual(titan["npc_configs"]["attack_style"], "melee")
        self.assertTrue(titan["npc_stats_source"].endswith("black_knight_titan.json"))

    def test_tree_gnome_village_has_source_backed_stage_requirements(self):
        data = quests_as_dict()
        quest = data["tree_gnome_village"]

        self.assertEqual(quest["stages"], 8)
        self.assertEqual(quest["required_items"], {})
        self.assertEqual(quest["rewards"], {"Gnome amulet": 1})
        self.assertNotIn("Spirit Tree", quest["rewards"])
        self.assertIn("Two Khazard commanders (level 48)", quest["combat"])
        self.assertIn("Khazard warlord (level 112)", quest["combat"])
        self.assertEqual(quest["xp_rewards"], ({"skill_id": "attack", "amount": 11450.0},))

        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}
        self.assertEqual(by_stage[1]["required_routes"], ())
        self.assertEqual(by_stage[1]["auto_actions"], ("Reach Commander Montai on the battlefield",))
        self.assertEqual(by_stage[5]["auto_actions"], ("Enter the Khazard stronghold through the broken wall",))
        self.assertEqual(by_stage[2]["consumed_inventory"], {"Logs": 6})
        self.assertEqual(
            by_stage[4]["required_actions"],
            (
                "Get the first tracker coordinate",
                "Get the second tracker coordinate",
                "Get the third tracker coordinate",
                "Fire the battlefield ballista at the Khazard stronghold",
            ),
        )
        self.assertEqual(by_stage[5]["produced_inventory"], {"Orb of protection": 1})
        self.assertEqual(by_stage[6]["consumed_inventory"], {"Orb of protection": 1})
        self.assertEqual(by_stage[6]["produced_inventory"], {"Orbs of protection": 1})
        self.assertEqual(by_stage[7]["consumed_inventory"], {"Orbs of protection": 1})

        commander = by_stage[5]["combat_encounters"][0]
        self.assertEqual(commander["encounter_id"], "tree_gnome_village_khazard_commander_48")
        self.assertEqual(commander["quantity"], 2)
        self.assertEqual(commander["npc_stats"]["hitpoints"], 220)
        self.assertEqual(commander["npc_configs"]["attack_bonus"], "stab_att")
        self.assertTrue(commander["npc_stats_source"].endswith("khazard_commander (noanims).json"))

        warlord = by_stage[6]["combat_encounters"][0]
        self.assertEqual(warlord["encounter_id"], "tree_gnome_village_khazard_warlord_112")
        self.assertEqual(warlord["level"], 112)
        self.assertEqual(warlord["npc_stats"]["hitpoints"], 1690)
        self.assertEqual(warlord["npc_configs"]["max_hit"], 92)
        self.assertTrue(warlord["npc_stats_source"].endswith("khazard_warlord (noanims).json"))

    def test_shield_of_arrav_has_source_backed_route_stage_requirements(self):
        data = quests_as_dict()
        quest = data["shield_of_arrav"]

        self.assertEqual(quest["stages"], 12)
        self.assertEqual(quest["rewards"], {"Coins": 600})
        self.assertEqual(quest["required_items"], {})
        self.assertIn("Coins x20", quest["requirements"][0])
        self.assertIn("contextual Phoenix contact", quest["requirements"][2])
        self.assertEqual(quest["choices"][0]["stage"], 4)
        self.assertEqual(
            tuple(option["route_id"] for option in quest["choices"][0]["options"]),
            ("Join the Phoenix Gang", "Join the Black Arm Gang"),
        )
        self.assertIn("darkan-world-server", quest["source"])

        stage3 = next(row for row in quest["stage_requirements"] if row["stage"] == 3)
        self.assertEqual(stage3["consumed_inventory"], {"Coins": 20})

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

        black_arm_crossbows = next(
            row
            for row in quest["stage_requirements"]
            if row["stage"] == 5 and row["variant"] == "black_arm"
        )
        self.assertEqual(black_arm_crossbows["required_tools"], {})
        self.assertEqual(black_arm_crossbows["required_actions"], ())
        self.assertEqual(
            black_arm_crossbows["produced_inventory"],
            {"Weapon store key": 1, "Phoenix crossbow": 2},
        )

        stage10 = {
            row["variant"]: row
            for row in quest["stage_requirements"]
            if row["stage"] == 10
        }
        self.assertEqual(
            stage10["phoenix"]["consumed_inventory"],
            {"Half certificate (Phoenix)": 1},
        )
        self.assertEqual(
            stage10["black_arm"]["consumed_inventory"],
            {"Half certificate (Black Arm)": 1},
        )
        self.assertEqual(stage10["phoenix"]["produced_inventory"], {"Certificate": 1})
        self.assertEqual(stage10["black_arm"]["produced_inventory"], {"Certificate": 1})

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
        self.assertEqual(by_stage[11]["auto_actions"], ("Return to Lady Servil for the reward",))

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
        self.assertEqual(by_stage[2]["required_routes"], ())
        self.assertEqual(by_stage[2]["auto_actions"], ("Reach Keep Le Faye through the Catherby crate delivery",))

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
        quests_with_narrative_actions = [
            quest_id
            for quest_id, quest in data.items()
            if any(
                requirement["required_actions"] or requirement["auto_actions"]
                for requirement in quest["stage_requirements"]
            )
        ]

        self.assertEqual(len(quests_with_stage_requirements), 196)
        self.assertGreaterEqual(len(quests_with_combat), 110)
        self.assertGreaterEqual(len(quests_with_item_requirements), 160)
        self.assertGreaterEqual(len(quests_with_narrative_actions), 190)

        hazeel = data["hazeel_cult"]
        self.assertEqual(hazeel["rewards"], {"Coins": 2005})
        self.assertEqual(hazeel["choices"][0]["stage"], 1)
        self.assertEqual(
            tuple(option["route_id"] for option in hazeel["choices"][0]["options"]),
            ("Side with Ceril Carnillean", "Side with Hazeel's cult"),
        )
        self.assertIn("oldid=6579784", hazeel["choices"][0]["source"])
        hazeel_stage_1 = next(row for row in hazeel["stage_requirements"] if row["stage"] == 1)
        self.assertEqual(hazeel_stage_1["required_actions"], ("Complete Hazeel Cult stage 1 objective",))
        self.assertLess(len(hazeel_stage_1["required_actions"][0]), 80)
        self.assertIn("oldid=6579784", hazeel_stage_1["source"])

        cooks_by_stage = {row["stage"]: row for row in data["cooks_assistant"]["stage_requirements"]}
        self.assertEqual(data["cooks_assistant"]["stages"], 5)
        self.assertEqual(set(cooks_by_stage), {1, 2, 3, 4})
        self.assertEqual(cooks_by_stage[1]["produced_inventory"], {"Super large egg": 1})
        self.assertEqual(cooks_by_stage[2]["required_inventory"], {"Bucket": 1})
        self.assertEqual(cooks_by_stage[2]["consumed_inventory"], {"Bucket": 1})
        self.assertEqual(cooks_by_stage[2]["produced_inventory"], {"Top-quality milk": 1})
        self.assertEqual(cooks_by_stage[3]["required_inventory"], {"Empty pot": 1})
        self.assertEqual(cooks_by_stage[3]["consumed_inventory"], {"Empty pot": 1})
        self.assertEqual(cooks_by_stage[3]["produced_inventory"], {"Extra fine flour": 1})
        self.assertEqual(
            cooks_by_stage[4]["consumed_inventory"],
            {"Top-quality milk": 1, "Extra fine flour": 1, "Super large egg": 1},
        )

        self.assertEqual(data["vampyre_slayer"]["requirements"], ())
        vampyre_by_stage = {row["stage"]: row for row in data["vampyre_slayer"]["stage_requirements"]}
        self.assertEqual(vampyre_by_stage[1]["required_actions"], ())
        self.assertEqual(vampyre_by_stage[1]["auto_actions"], ("Speak to Dr Harlow at the Blue Moon Inn",))
        self.assertEqual(vampyre_by_stage[2]["consumed_inventory"], {})
        self.assertEqual(vampyre_by_stage[2]["produced_inventory"], {"Stake": 1, "Stake hammer": 1})
        self.assertEqual(vampyre_by_stage[2]["required_actions"], ())
        self.assertEqual(vampyre_by_stage[2]["auto_actions"], ("Buy Dr Harlow a beer at the Blue Moon Inn",))
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
            demon_requirements[8]["auto_actions"],
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
        self.assertEqual(restless["rewards"], {"Ancient bones": 5})
        self.assertEqual(restless["xp_rewards"], ({"skill_id": "prayer", "amount": 125},))
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

        shilo_fights = {
            encounter["display_name"]: encounter
            for requirement in data["shilo_village"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        }
        self.assertEqual(
            set(shilo_fights),
            {"Nazastarool (Zombie)", "Nazastarool (Skeleton)", "Nazastarool (Ghost)"},
        )
        self.assertEqual(shilo_fights["Nazastarool (Zombie)"]["level"], 91)
        self.assertEqual(shilo_fights["Nazastarool (Skeleton)"]["level"], 68)
        self.assertEqual(shilo_fights["Nazastarool (Ghost)"]["level"], 93)
        self.assertEqual(shilo_fights["Nazastarool (Ghost)"]["npc_stats"]["hitpoints"], 1000)

        legends_nezikchened = next(
            encounter
            for requirement in data["legends_quest"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Nezikchened"
        )
        self.assertEqual(legends_nezikchened["quantity"], 3)
        self.assertEqual(legends_nezikchened["npc_stats"]["attack"], 330)

        feud_tough_guy = next(
            encounter
            for requirement in data["the_feud"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Tough guy"
        )
        self.assertEqual(feud_tough_guy["level"], 75)
        self.assertEqual(feud_tough_guy["npc_stats"]["hitpoints"], 750)

        rfd_black_dragon = next(
            encounter
            for requirement in data["recipe_for_disaster_freeing_sir_amik_varze"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
            if encounter["display_name"] == "Black Dragon"
        )
        self.assertEqual(rfd_black_dragon["level"], 227)
        self.assertEqual(rfd_black_dragon["npc_stats"]["hitpoints"], 1900)

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
        self.assertEqual(witch_by_stage[5]["required_routes"], ())
        self.assertEqual(witch_by_stage[5]["auto_actions"], ("Avoid the witch's patrol through the house",))
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
        self.assertEqual(souls_by_stage[2]["auto_actions"], ("Fill the rage meter with an anger weapon",))
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

        void = data["the_void_stares_back"]
        self.assertEqual(void["choices"][0]["stage"], 5)
        self.assertEqual(
            tuple(option["route_id"] for option in void["choices"][0]["options"]),
            ("Sacrifice Korasi", "Sacrifice Jessika"),
        )
        self.assertIn("oldid=6549181", void["choices"][0]["source"])
        void_fights = [
            encounter
            for requirement in void["stage_requirements"]
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

    def test_same_quest_products_are_not_required_before_they_are_produced(self):
        violations = []
        for quest_id, quest in quests_as_dict().items():
            stage_requirements = quest["stage_requirements"]
            quest_products = {
                item_name
                for requirement in stage_requirements
                for item_name in requirement["produced_inventory"]
            }
            produced = set(quest["start_inventory"])
            for requirement in sorted(
                stage_requirements,
                key=lambda row: (row["stage"], row["variant"], row["description"]),
            ):
                checked = set(requirement["required_inventory"])
                checked.update(requirement["consumed_inventory"])
                checked.update(requirement["required_tools"])
                for option_group in requirement["required_inventory_options"]:
                    for option in option_group:
                        checked.update(option)
                for option_group in requirement["consumed_inventory_options"]:
                    for option in option_group:
                        checked.update(option)
                for item_name in sorted(checked & quest_products):
                    if item_name not in produced:
                        violations.append((quest_id, requirement["stage"], item_name))
                produced.update(requirement["produced_inventory"])

        self.assertEqual(violations, [])

    def test_quest_wide_used_during_lines_do_not_gate_same_quest_products(self):
        violations = [
            (candidate.category, candidate.quest_id, candidate.stage, candidate.item_name)
            for candidate in quest_local_gate_candidates()
            if candidate.category
            in {
                "quest_wide_same_quest_product",
                "stage_requires_same_quest_product_before_source",
            }
        ]

        self.assertEqual(violations, [])

    def test_generated_pseudo_items_are_not_inventory_stage_blockers(self):
        data = quests_as_dict()
        forbidden_by_quest = {
            "monkey_madness": {"Monkey Dentures", "M'Amulet mould", "Monkey talisman"},
            "rat_catchers": {"Rat poison"},
            "mournings_end_part_i": {"Lletya", "Oronwen", "Rotten apple"},
            "death_to_the_dorgeshuun": {"Tears of Guthix cavern"},
            "elemental_workshop_ii": {"Beaten Book", "Slashed book"},
            "enlightened_journey": {"Willow branch"},
            "icthlarins_little_helper": {
                "About 750 coins",
                "Poison Purge",
                "Nardah Teleport Scroll",
                "Bucket of sap",
            },
            "making_history": {
                "Ardougne",
                "Enchanted lyre",
                "Rellekka",
                "Teleport to House",
                "Magic tablet",
                "Castle_Wars",
                "Ectophial",
                "Ecto-token",
                "Port Sarim",
                "Port Phasmatys",
                "Fairy Tale III - Orks Rift",
            },
            "cabin_fever": {"Ghosts Ahoy"},
            "cold_war": {"Crafting table 3"},
            "myths_of_the_white_lands": {
                "Lumbridge Teleport",
                "Glory Amulet",
                "Runecrafting guild teleport",
                "Wicked hood",
                "Fairy Ring",
                "Wizard's Tower",
            },
            "in_pyre_need": {"Fairy Rings", "Phoenix lair teleport"},
            "kings_ransom": {"Animate rock scroll"},
            "dealing_with_scabaras": {"Agility Pyramid", "Random Bronze armours/weapons"},
            "roving_elves": {"Good Food"},
            "rum_deal": {"Armour", "Food"},
            "spirits_of_the_elid": {"Telegrab"},
            "enakhras_lament": {"Crumble Undead"},
            "in_aid_of_the_myreque": {"Food", "Enchant sapphire"},
            "dream_mentor": {"Food"},
            "back_to_my_roots": {"Food", "Shilo Village"},
            "rocking_out": {"Brimhaven tablet", "Ectophial", "Rimmington", "Rimmington tablet", "Love Story"},
            "glorious_memories": {
                "Teleport to House",
                "Player-owned house",
                "Rellekka",
                "Rellekka tablet",
                "Ring of wealth",
            },
            "elemental_workshop_iii": {"Ragged book", "Elemental Workshop I"},
            "the_eyes_of_glouphrie": {"Bucket of sap"},
            "the_tale_of_the_muspah": {
                "Enchant Level 1 Jewellery",
                "Magic carpet",
                "Teleportation methods",
                "Dramen staff",
                "Lunar staff",
                "Fairy rings",
                "Enchanted lyre",
                "Rellekka tablet",
                "Pollnivneach tablet",
                "Slayer ring",
                "Broomstick",
                "Sorceress's Garden",
                "Rellekka",
                "Pollnivneach",
                "Enchant sapphire",
                "Food",
            },
            "legacy_of_seergaze": {"Enchant Level 2 Jewellery"},
            "meeting_history": {"Making History"},
            "while_guthix_sleeps": {"NPC Contact"},
            "blood_runs_deep": {"Food", "Prayer Potion", "Armour"},
            "desert_treasure": {"Thieving"},
            "troll_romance": {"Combat gear and good food"},
            "the_fremennik_isles": {"Mining", "Yak hide armour", "Fremennik round shield"},
            "within_the_light": {
                "Ardougne",
                "Teleport crystal",
                "New key",
                "Tarnished key",
                "Crystal trinket",
                "Colour wheel",
                "Shadow",
                "Prayer potions",
            },
            "the_firemakers_curse": {"Food", "Let Them Eat Pie"},
        }
        violations = []
        for quest_id, forbidden_items in forbidden_by_quest.items():
            for requirement in data[quest_id]["stage_requirements"]:
                blocked_items = set(requirement["required_inventory"])
                blocked_items.update(requirement["consumed_inventory"])
                blocked_items.update(requirement["required_tools"])
                for option_group in requirement["required_inventory_options"]:
                    for option in option_group:
                        blocked_items.update(option)
                for option_group in requirement["consumed_inventory_options"]:
                    for option in option_group:
                        blocked_items.update(option)
                for item_name in sorted(blocked_items & forbidden_items):
                    violations.append((quest_id, requirement["stage"], item_name))

        self.assertEqual(violations, [])

        enlightened_stage_2 = next(
            row for row in data["enlightened_journey"]["stage_requirements"] if row["stage"] == 2
        )
        self.assertEqual(enlightened_stage_2["consumed_inventory"]["Sack"], 8)
        self.assertEqual(enlightened_stage_2["produced_inventory"], {"Sandbag": 8})

        rat_catchers_stage_1 = next(
            row for row in data["rat_catchers"]["stage_requirements"] if row["stage"] == 1
        )
        self.assertEqual(
            rat_catchers_stage_1["consumed_inventory"],
            {"Vial": 1, "Clean kwuarm": 1, "Red spiders' eggs": 1},
        )
        self.assertEqual(rat_catchers_stage_1["produced_inventory"], {"Rat poison": 1})

    def test_generated_catalog_enriches_safe_combat_name_matches(self):
        data = quests_as_dict()

        temple_combat = [
            encounter
            for requirement in data["temple_of_ikov"]["stage_requirements"]
            for encounter in requirement["combat_encounters"]
        ]
        guardians = next(encounter for encounter in temple_combat if encounter["display_name"] == "Guardian of Armadyl")
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

        self.assertEqual(quest["stages"], 14)
        self.assertEqual(quest["combat"], "None.")
        self.assertEqual(quest["rewards"], {"Ammo mould": 1})
        self.assertEqual(quest["xp_rewards"], ({"skill_id": "crafting", "amount": 750.0},))
        self.assertEqual(quest["journal_stages"][14], ("Captain Lawgof gave his recommendation.", "Quest complete!"))
        self.assertEqual(len(quest["stage_requirements"]), 13)
        self.assertTrue(all(not row["combat_encounters"] for row in quest["stage_requirements"]))
        self.assertEqual(by_stage[1]["produced_inventory"], {"Railing": 6})
        self.assertEqual(by_stage[2]["consumed_inventory"], {"Railing": 6})
        self.assertEqual(by_stage[2]["required_tools"], {"Hammer": 1})
        self.assertEqual(by_stage[4]["produced_inventory"], {"Dwarf remains": 1})
        self.assertEqual(by_stage[5]["consumed_inventory"], {"Dwarf remains": 1})
        self.assertEqual(by_stage[6]["auto_actions"], ("Reach the Dwarf Cannon goblin hideout",))
        self.assertEqual(by_stage[7]["auto_actions"], ("Rescue Lollk from the goblin hideout",))
        self.assertEqual(by_stage[8]["produced_inventory"], {"Toolkit": 1})
        self.assertEqual(by_stage[9]["required_tools"], {"Toolkit": 1})
        self.assertEqual(by_stage[11]["produced_inventory"], {"Ammo mould": 1, "Nulodion's notes": 1})
        self.assertEqual(by_stage[12]["consumed_inventory"], {"Ammo mould": 1, "Nulodion's notes": 1})
        self.assertIn("DwarfCannon.java", by_stage[2]["source"])

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
        self.assertEqual(gertrude_by_stage[3]["required_routes"], ())
        self.assertEqual(gertrude_by_stage[3]["auto_actions"], ("Reach Fluffs in the Varrock Lumber Yard",))
        self.assertEqual(gertrude_by_stage[4]["consumed_inventory"], {"Bucket of milk": 1})
        self.assertEqual(gertrude_by_stage[4]["produced_inventory"], {"Bucket": 1})
        self.assertEqual(gertrude_by_stage[5]["consumed_inventory"], {"Raw sardine": 1, "Doogle leaves": 1})
        self.assertEqual(gertrude_by_stage[5]["produced_inventory"], {"Doogle sardine": 1})
        self.assertEqual(gertrude_by_stage[6]["consumed_inventory"], {"Doogle sardine": 1})
        self.assertEqual(gertrude_by_stage[7]["produced_inventory"], {"Three little kittens": 1})
        self.assertEqual(gertrude_by_stage[8]["consumed_inventory"], {"Three little kittens": 1})

        clock = data["clock_tower"]
        clock_by_stage = {row["stage"]: row for row in clock["stage_requirements"]}
        self.assertEqual(clock["stages"], 6)
        self.assertEqual(clock["combat"], "None.")
        self.assertEqual(clock_by_stage[1]["produced_inventory"], {"Rat poison": 1})
        self.assertEqual(clock_by_stage[2]["consumed_inventory"], {"Rat poison": 1})
        self.assertEqual(
            clock_by_stage[3]["produced_inventory"],
            {"White cog": 1, "Black cog": 1, "Blue cog": 1, "Red cog": 1},
        )
        self.assertEqual(clock_by_stage[4]["required_inventory_options"], (({"Bucket of water": 1}, {"Ice gloves": 1}),))
        self.assertEqual(
            clock_by_stage[4]["consumed_inventory"],
            {"White cog": 1, "Black cog": 1, "Blue cog": 1, "Red cog": 1},
        )

        monks = data["monks_friend"]
        monks_by_stage = {row["stage"]: row for row in monks["stage_requirements"]}
        self.assertEqual(monks["stages"], 7)
        self.assertEqual(monks["combat"], "Optional: two level 21 thieves and a level 25 head thief.")
        self.assertEqual(monks_by_stage[1]["produced_inventory"], {"Child's blanket": 1})
        self.assertEqual(monks_by_stage[2]["consumed_inventory"], {"Child's blanket": 1})
        self.assertEqual(monks_by_stage[4]["consumed_inventory"], {"Jug of water": 1})
        self.assertEqual(monks_by_stage[5]["consumed_inventory"], {"Logs": 1})

        tribal = data["tribal_totem"]
        tribal_by_stage = {row["stage"]: row for row in tribal["stage_requirements"]}
        self.assertEqual(tribal["stages"], 6)
        self.assertEqual(tribal["combat"], "None.")
        self.assertEqual(tribal_by_stage[2]["required_routes"], ())
        self.assertEqual(tribal_by_stage[2]["auto_actions"], ("Reach the Ardougne RPDT depot",))
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
        self.assertEqual(sheep["stages"], 6)
        self.assertEqual(sheep["combat"], "None.")
        self.assertEqual(sheep_by_stage[1]["produced_inventory"], {"Sheep feed": 1})
        self.assertEqual(sheep_by_stage[2]["consumed_inventory"], {"Coins": 100})
        self.assertEqual(sheep_by_stage[2]["produced_inventory"], {"Plague jacket": 1, "Plague trousers": 1})
        self.assertEqual(sheep_by_stage[3]["produced_inventory"], {"Cattleprod": 1})
        self.assertEqual(sheep_by_stage[4]["required_inventory"], {"Sheep feed": 1})
        self.assertEqual(
            sheep_by_stage[4]["required_tools"],
            {"Plague jacket": 1, "Plague trousers": 1, "Cattleprod": 1},
        )
        self.assertEqual(
            sheep_by_stage[4]["produced_inventory"],
            {"Red sheep bones": 1, "Green sheep bones": 1, "Blue sheep bones": 1, "Yellow sheep bones": 1},
        )
        self.assertEqual(
            sheep_by_stage[5]["consumed_inventory"],
            {"Red sheep bones": 1, "Green sheep bones": 1, "Blue sheep bones": 1, "Yellow sheep bones": 1},
        )
        for stage in (3, 4, 5):
            self.assertEqual(sheep_by_stage[stage]["required_routes"], ())
            self.assertEqual(sheep_by_stage[stage]["auto_actions"], ("Reach the Ardougne sheep enclosure",))
        self.assertIn("SheepHerder.kt", sheep_by_stage[4]["source"])

        plague = data["plague_city"]
        plague_by_stage = {row["stage"]: row for row in plague["stage_requirements"]}
        self.assertEqual(plague["stages"], 17)
        self.assertEqual(plague["combat"], "None.")
        self.assertEqual(plague["rewards"], {"A magic scroll": 1})
        self.assertEqual(plague_by_stage[1]["consumed_inventory"], {"Dwellberries": 1})
        self.assertEqual(plague_by_stage[1]["produced_inventory"], {"Gas mask": 1})
        self.assertEqual(plague_by_stage[3]["consumed_inventory"], {"Bucket of water": 4})
        self.assertEqual(plague_by_stage[3]["produced_inventory"], {"Bucket": 4})
        self.assertEqual(plague_by_stage[8]["auto_actions"], ("Reach West Ardougne through the sewer pipe",))
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
        self.assertEqual(waterfall_by_stage[3]["auto_actions"], ("Reach Golrie under Tree Gnome Village",))
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

    def test_stolen_hearts_is_a_playable_source_backed_dependency(self):
        quest = quests_as_dict()["stolen_hearts"]
        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}

        self.assertEqual(quest["rewards"], {"Coins": 2500})
        self.assertEqual(
            quest["xp_rewards"],
            ({"skill_id": "constitution", "amount": 250.0},),
        )
        self.assertEqual(len(quest["lamp_rewards"]), 3)
        self.assertNotIn("Khnum", quest["rewards"])
        self.assertFalse(
            any(
                action.startswith("Complete Stolen Hearts stage")
                for row in by_stage.values()
                for action in row["required_actions"]
            )
        )
        self.assertEqual(
            [encounter["display_name"] for encounter in by_stage[3]["combat_encounters"]],
            ["Mercenary Joe", "Skulls mercenary"],
        )
        self.assertEqual(by_stage[3]["combat_encounters"][1]["quantity"], 2)
        self.assertEqual(by_stage[3]["produced_inventory"], {"Ransom note": 1})
        self.assertEqual(
            by_stage[4]["produced_inventory"],
            {"History of the Kharid-ib": 1},
        )
        self.assertEqual(
            by_stage[5]["consumed_inventory"],
            {"Ransom note": 1, "History of the Kharid-ib": 1},
        )

        items = quest_reward_items_as_dict()
        self.assertEqual(items["Ransom note"]["item_id"], 25127)
        self.assertEqual(items["History of the Kharid-ib"]["item_id"], 25128)
        self.assertFalse(items["Ransom note"]["tradeable"])

    def test_diamond_in_the_rough_is_a_playable_source_backed_dependency(self):
        quest = quests_as_dict()["diamond_in_the_rough"]
        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}

        self.assertEqual(quest["rewards"], {})
        self.assertEqual(
            quest["xp_rewards"],
            (
                {"skill_id": "agility", "amount": 250},
                {"skill_id": "constitution", "amount": 250},
                {"skill_id": "thieving", "amount": 250},
            ),
        )
        self.assertEqual(len(quest["lamp_rewards"]), 1)
        self.assertFalse(
            any(
                action.startswith("Complete Diamond in the Rough stage")
                for row in by_stage.values()
                for action in row["required_actions"]
            )
        )
        self.assertEqual(by_stage[1]["produced_inventory"], {"Heavy weight": 1})
        self.assertEqual(
            [
                (encounter["display_name"], encounter["level"], encounter["quantity"])
                for encounter in by_stage[2]["combat_encounters"]
            ],
            [
                ("Bandit (Diamond in the Rough)", 2, 5),
                ("Bandit king", 3, 1),
            ],
        )
        self.assertEqual(
            by_stage[2]["produced_inventory"],
            {"Sundial gnomon": 1, "Waterskin (4)": 4},
        )
        self.assertEqual(
            by_stage[3]["consumed_inventory"],
            {"Heavy weight": 1, "Sundial gnomon": 1},
        )
        self.assertEqual(
            by_stage[3]["produced_inventory"],
            {"Sapphire": 1, "Emerald": 1, "Ruby": 1},
        )
        self.assertEqual(
            [encounter["display_name"] for encounter in by_stage[4]["combat_encounters"]],
            ["Apep", "Heru"],
        )

        items = quest_reward_items_as_dict()
        self.assertEqual(items["Heavy weight"]["item_id"], 25116)
        self.assertEqual(items["Sundial gnomon"]["item_id"], 25118)
        self.assertFalse(items["Heavy weight"]["stackable"])
        self.assertFalse(items["Sundial gnomon"]["tradeable"])
        self.assertEqual(
            {
                item_name: (items[item_name]["item_id"], items[item_name]["equipment_slot"])
                for item_name in ("Apmeken mask", "Ankh", "Scabaras mask", "Was")
            },
            {
                "Apmeken mask": (25122, "head"),
                "Ankh": (25123, "shield"),
                "Scabaras mask": (25124, "head"),
                "Was": (25125, "weapon"),
            },
        )
        self.assertEqual(
            {
                claim_id: (
                    CLAIMS_BY_ID[claim_id].claim_type,
                    CLAIMS_BY_ID[claim_id].required_quest,
                    CLAIMS_BY_ID[claim_id].xp_amount,
                    CLAIMS_BY_ID[claim_id].skill_options,
                    CLAIMS_BY_ID[claim_id].minimum_level,
                    CLAIMS_BY_ID[claim_id].items,
                )
                for claim_id in (
                    "diamond_in_the_rough_scabaras_tomb",
                    "diamond_in_the_rough_apmeken_tomb",
                )
            },
            {
                "diamond_in_the_rough_scabaras_tomb": (
                    "skill_reward",
                    "diamond_in_the_rough",
                    20000,
                    ("mining",),
                    80,
                    (("Scabaras mask", 1), ("Was", 1)),
                ),
                "diamond_in_the_rough_apmeken_tomb": (
                    "skill_reward",
                    "diamond_in_the_rough",
                    20000,
                    ("agility",),
                    80,
                    (("Apmeken mask", 1), ("Ankh", 1)),
                ),
            },
        )

    def test_icthlarins_little_helper_is_a_playable_source_backed_dependency(self):
        quest = quests_as_dict()["icthlarins_little_helper"]
        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}

        self.assertEqual(quest["stages"], 9)
        self.assertEqual(quest["point_reward"], 2)
        self.assertEqual(quest["rewards"], {"Catspeak amulet": 1})
        self.assertEqual(
            quest["xp_rewards"],
            (
                {"skill_id": "agility", "amount": 4000},
                {"skill_id": "thieving", "amount": 4500},
                {"skill_id": "woodcutting", "amount": 4000},
            ),
        )
        self.assertFalse(
            any(
                action.startswith("Complete Icthlarin's Little Helper stage")
                for row in by_stage.values()
                for action in row["required_actions"]
            )
        )
        self.assertEqual(
            by_stage[1]["required_inventory_options"],
            (({"Kitten": 1}, {"Cat": 1}, {"Overgrown cat": 1}, {"Hellcat": 1}),),
        )
        self.assertEqual(
            by_stage[1]["consumed_inventory"],
            {"Tinderbox": 1, "Waterskin (4)": 1},
        )
        self.assertEqual(by_stage[1]["produced_inventory"], {"Canopic jar": 1})
        self.assertEqual(by_stage[2]["produced_inventory"], {"Sphinx's token": 1})
        self.assertEqual(
            by_stage[3]["consumed_inventory"],
            {"Canopic jar": 1, "Sphinx's token": 1},
        )
        guardian = by_stage[4]["combat_encounters"][0]
        self.assertEqual(
            (guardian["display_name"], guardian["level"], guardian["npc_stats"]["hitpoints"]),
            ("Canopic guardian", 81, 750),
        )
        self.assertEqual(by_stage[4]["produced_inventory"], {"Canopic jar": 1})
        self.assertEqual(
            by_stage[5]["consumed_inventory_options"],
            (({"Pile of salt": 1}, {"Bag of salt": 1}),),
        )
        self.assertEqual(
            by_stage[5]["consumed_inventory"],
            {"Canopic jar": 1, "Coins": 30, "Willow logs": 1, "Bucket": 1},
        )
        self.assertEqual(by_stage[5]["required_tools"], {"Knife": 1})
        self.assertEqual(
            by_stage[6]["produced_inventory"],
            {"Unholy symbol (Icthlarin's Little Helper)": 1},
        )
        self.assertEqual(
            by_stage[7]["consumed_inventory"],
            {"Unholy symbol (Icthlarin's Little Helper)": 1},
        )
        priest = by_stage[8]["combat_encounters"][0]
        self.assertEqual(
            (priest["display_name"], priest["level"], priest["npc_stats"]["hitpoints"]),
            ("Possessed Priest", 126, 800),
        )
        self.assertEqual(priest["npc_configs"]["max_hit"], 140)

        items = quest_reward_items_as_dict()
        self.assertEqual(items["Canopic jar"]["item_id"], 4678)
        self.assertEqual(items["Sphinx's token"]["item_id"], 4691)
        self.assertEqual(items["Holy symbol (Icthlarin's Little Helper)"]["item_id"], 4682)
        self.assertEqual(items["Unholy symbol (Icthlarin's Little Helper)"]["item_id"], 4683)
        self.assertEqual(items["Catspeak amulet"]["item_id"], 4677)
        self.assertFalse(items["Catspeak amulet"]["tradeable"])

    def test_smoking_kills_is_a_playable_source_backed_slayer_unlock(self):
        quest = quests_as_dict()["smoking_kills"]
        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}

        self.assertEqual(quest["stages"], 13)
        self.assertEqual(quest["point_reward"], 1)
        self.assertEqual(quest["xp_rewards"], ({"skill_id": "slayer", "amount": 5000},))
        self.assertEqual(quest["rewards"], {})
        self.assertFalse(
            any(
                action.startswith("Complete Smoking Kills stage")
                for row in by_stage.values()
                for action in row["required_actions"]
            )
        )
        self.assertEqual(tuple(by_stage), tuple(range(1, 13)))
        self.assertEqual(
            by_stage[1]["required_inventory_options"],
            (({"Kitten": 1}, {"Cat": 1}, {"Overgrown cat": 1}, {"Hellcat": 1}),),
        )
        self.assertEqual(by_stage[2]["required_tools"], {"Catspeak amulet": 1, "Pickaxe": 1})
        self.assertEqual(
            by_stage[3]["produced_inventory"],
            {"Ranged path key": 1},
        )
        self.assertEqual(by_stage[4]["consumed_inventory"], {"Ranged path key": 1})
        self.assertEqual(
            by_stage[6]["produced_inventory"],
            {"Magic path key": 1},
        )
        self.assertEqual(
            by_stage[7]["consumed_inventory"],
            {"Magic path key": 1, "Face mask": 1, "Earmuffs": 1},
        )
        self.assertEqual(by_stage[7]["produced_inventory"], {"Masked earmuffs": 1})
        self.assertEqual(by_stage[7]["required_tools"], {"Ghostspeak amulet": 1})
        for stage in (8, 9, 10, 11):
            self.assertEqual(by_stage[stage]["required_tools"], {"Masked earmuffs": 1})

        ranged_wave = by_stage[2]["combat_encounters"][0]
        mummy = by_stage[3]["combat_encounters"][0]
        mighty = by_stage[9]["combat_encounters"][0]
        mistress = by_stage[11]["combat_encounters"][0]
        self.assertEqual(
            (ranged_wave["display_name"], ranged_wave["level"], ranged_wave["npc_stats"]["hitpoints"]),
            ("Ranged-wing tomb guardians", 20, 800),
        )
        self.assertEqual((mummy["level"], mummy["npc_configs"]["max_hit"]), (54, 80))
        self.assertEqual((mighty["level"], mighty["npc_stats"]["hitpoints"]), (90, 850))
        self.assertEqual((mistress["level"], mistress["npc_stats"]["hitpoints"]), (111, 2220))
        self.assertEqual(mistress["npc_configs"]["minimum_player_combat"], 85)
        self.assertIn("four level 141 Insectoid Assassins", mistress["source_text"])

        items = quest_reward_items_as_dict()
        self.assertNotIn("Amulet of ghostspeak", items)
        for item_name, item_id in (
            ("Ghostspeak amulet", 552),
            ("Kitten", 1555),
            ("Ranged path key", 13259),
            ("Magic path key", 13260),
            ("Banshee voice", 13276),
            ("Masked earmuffs", 13277),
        ):
            self.assertEqual(items[item_name]["item_id"], item_id)
            self.assertFalse(items[item_name]["tradeable"])
            self.assertFalse(items[item_name]["stackable"])

    def test_jungle_potion_is_a_playable_source_backed_shilo_dependency(self):
        quest = quests_as_dict()["jungle_potion"]
        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}

        self.assertEqual(quest["stages"], 11)
        self.assertEqual(quest["point_reward"], 1)
        self.assertEqual(quest["rewards"], {})
        self.assertEqual(quest["xp_rewards"], ({"skill_id": "herblore", "amount": 775},))
        self.assertEqual(
            quest["required_quests"],
            ({"quest_id": "druidic_ritual", "display_name": "Druidic Ritual"},),
        )
        self.assertEqual(
            quest["required_skills"],
            ({"skill_id": "herblore", "display_name": "Herblore", "level": 3},),
        )
        self.assertNotIn("Firemaking 33", quest["requirements"])
        self.assertNotIn("Slayer 33", quest["requirements"])
        self.assertEqual(tuple(by_stage), tuple(range(1, 11)))
        self.assertFalse(
            any(
                action.startswith("Complete Jungle Potion stage")
                for row in by_stage.values()
                for action in row["required_actions"]
            )
        )
        self.assertTrue(all(not row["required_actions"] for row in by_stage.values()))

        herb_rows = (
            (1, 2, "Grimy snake weed", "Clean snake weed", 1525, 1526),
            (3, 4, "Grimy ardrigal", "Clean ardrigal", 1527, 1528),
            (5, 6, "Grimy sito foil", "Clean sito foil", 1529, 1530),
            (7, 8, "Grimy volencia moss", "Clean volencia moss", 1531, 1532),
            (9, 10, "Grimy rogue's purse", "Clean rogue's purse", 1533, 1534),
        )
        item_by_name = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for search_stage, turn_in_stage, grimy_name, clean_name, grimy_id, clean_id in herb_rows:
            self.assertEqual(by_stage[search_stage]["produced_inventory"], {grimy_name: 1})
            self.assertEqual(by_stage[turn_in_stage]["consumed_inventory"], {clean_name: 1})
            self.assertEqual(item_by_name[grimy_name].source_item_id, grimy_id)
            self.assertEqual(item_by_name[clean_name].source_item_id, clean_id)

        self.assertIn("Access to Tai Bwo Wannai Cleanup", quest["unlocks"])
        self.assertIn("Eligibility to start Shilo Village", quest["unlocks"])

    def test_shilo_village_is_a_playable_source_backed_slayer_dependency(self):
        quest = quests_as_dict()["shilo_village"]
        by_stage = {row["stage"]: row for row in quest["stage_requirements"]}

        self.assertEqual(quest["stages"], 12)
        self.assertEqual(quest["point_reward"], 2)
        self.assertEqual(quest["xp_rewards"], ({"skill_id": "crafting", "amount": 3875},))
        self.assertEqual(quest["start_inventory"], {"Wampum belt": 1})
        self.assertEqual(
            quest["required_skills"],
            (
                {"skill_id": "smithing", "display_name": "Smithing", "level": 4},
                {"skill_id": "crafting", "display_name": "Crafting", "level": 20},
                {"skill_id": "agility", "display_name": "Agility", "level": 32},
            ),
        )
        self.assertIn(
            "Used during quest: Rope x1, lit light source x1, Spade x1, Chisel x1, Bronze wire x1, Bones x3",
            quest["requirements"],
        )
        self.assertEqual(tuple(by_stage), tuple(range(1, 12)))
        self.assertFalse(
            any(
                action.startswith("Complete Shilo Village stage")
                for row in by_stage.values()
                for action in row["required_actions"]
            )
        )
        self.assertEqual(by_stage[1]["consumed_inventory"], {"Wampum belt": 1})
        self.assertEqual(
            tuple(option for option in by_stage[2]["consumed_inventory_options"]),
            (tuple({item_name: 1} for item_name in LIT_LIGHT_SOURCE_ITEMS),),
        )
        self.assertEqual(
            by_stage[3]["produced_inventory"],
            {
                "Stone-plaque": 1,
                "Tattered scroll": 1,
                "Crumpled scroll": 1,
                "Zadimus corpse": 1,
            },
        )
        self.assertEqual(by_stage[3]["required_tools"], {})
        self.assertEqual(
            by_stage[4]["required_inventory"],
            {"Tattered scroll": 1, "Crumpled scroll": 1},
        )
        self.assertEqual(by_stage[4]["consumed_inventory"], {"Zadimus corpse": 1})
        self.assertEqual(by_stage[4]["produced_inventory"], {"Bone shard": 1})
        self.assertEqual(
            by_stage[5]["produced_inventory"],
            {"Sword pommel": 1, "Locating crystal": 1, "Bervirius notes": 1},
        )
        self.assertEqual(
            by_stage[7]["produced_inventory"],
            {"Bone key": 1, "Bone beads": 1},
        )
        self.assertEqual(
            by_stage[8]["consumed_inventory"],
            {"Bone beads": 1, "Bronze wire": 1},
        )
        self.assertEqual(by_stage[8]["produced_inventory"], {"Beads of the dead": 1})
        self.assertEqual(by_stage[9]["consumed_inventory"], {"Bones": 3})
        self.assertEqual(
            tuple(encounter["display_name"] for encounter in by_stage[10]["combat_encounters"]),
            ("Nazastarool (Zombie)", "Nazastarool (Skeleton)", "Nazastarool (Ghost)"),
        )
        self.assertEqual(by_stage[10]["produced_inventory"], {"Rashiliyia corpse": 1})
        self.assertEqual(by_stage[11]["consumed_inventory"], {"Rashiliyia corpse": 1})

        items = quest_reward_items_as_dict()
        for item_name, item_id in (
            ("Bone shard", 604),
            ("Bone key", 605),
            ("Stone-plaque", 606),
            ("Tattered scroll", 607),
            ("Crumpled scroll", 608),
            ("Rashiliyia corpse", 609),
            ("Zadimus corpse", 610),
            ("Locating crystal", 611),
            ("Beads of the dead", 616),
            ("Bone beads", 618),
            ("Sword pommel", 623),
            ("Bervirius notes", 624),
            ("Wampum belt", 625),
        ):
            self.assertEqual(items[item_name]["item_id"], item_id)
            self.assertFalse(items[item_name]["tradeable"])
            self.assertFalse(items[item_name]["stackable"])

    def test_generated_rewards_journals_and_lamps_are_structured(self):
        data = quests_as_dict()

        cooks = data["cooks_assistant"]
        self.assertEqual(cooks["rewards"]["Coins"], 500)
        self.assertEqual(cooks["rewards"]["Sardine"], 20)
        self.assertGreaterEqual(len(cooks["journal_stages"]), 5)
        joined_cook_journal = " ".join(" ".join(stage) for stage in cooks["journal_stages"].values())
        self.assertIn("top-quality milk", joined_cook_journal)
        self.assertIn("extra fine flour", joined_cook_journal)
        self.assertIn("super large egg", joined_cook_journal)

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
