import json
import os
import unittest

from action_registry import (
    is_combat_review_action,
    is_review_action,
    is_utility_review_action,
    review_action_display_names,
    review_action_handler_key,
)
from constants import (
    BAR_DATA,
    COMBAT_ITEM_IMAGES,
    COOKING_BURNT_ITEMS,
    COOKING_DATA,
    COOKING_EXTRA_ITEM_DATA,
    COOKING_ITEM_IMAGES,
    COOKING_OUTPUT_ITEMS,
    CRAFTING_DATA,
    CRAFTING_REQUIRED_ITEM_DATA,
    CRAFTED_ITEM_IMAGES,
    EQUIPMENT_DATA,
    FIREMAKING_DATA,
    FIREMAKING_EXTRA_ITEM_DATA,
    FIREMAKING_ITEM_IMAGES,
    FIREMAKING_LOG_ITEMS,
    FIREMAKING_OUTPUT_ITEMS,
    FISHING_DATA,
    FISHING_ITEM_IMAGES,
    FISHING_OUTPUT_ITEMS,
    FLETCHED_ITEM_IMAGES,
    FARMING_ITEM_IMAGES,
    FLETCHING_DATA,
    GEM_DATA,
    HUNTER_DATA,
    HUNTER_EXTRA_ITEM_DATA,
    HUNTER_ITEM_IMAGES,
    HUNTER_OUTPUT_ITEMS,
    HERBLORE_DATA,
    HERBLORE_EXTRA_ITEM_DATA,
    ITEM_DEFINITIONS,
    MINING_BONUS_ITEM_DATA,
    MINING_OUTPUT_ITEMS,
    MINING_PICKAXE_DATA,
    ORE_DATA,
    PRAYER_EXTRA_ITEM_DATA,
    QUEST_ITEM_IMAGES,
    RUNECRAFTING_ACCESS_ITEMS,
    RUNECRAFTING_DATA,
    RUNECRAFTING_EXTRA_ITEM_DATA,
    RUNECRAFTING_ITEM_IMAGES,
    RUNECRAFTING_OUTPUT_ITEMS,
    RUNECRAFTING_POUCH_DATA,
    SHOP_ITEM_IMAGES,
    SMITHING_OUTPUT_ITEMS,
    UTILITY_ACTIVITY_DATA,
    WOODCUTTING_AXE_DATA,
    WOODCUTTING_LOG_ITEMS,
)
from crafting_data import CRAFTING_REQUIRED_ITEM_SOURCE_IDS
from item_registry import (
    item_definitions_by_id,
    item_definitions_by_storage_key,
    item_storage_keys_by_category,
    missing_required_asset_paths,
)
from skill_registry import (
    ALL_SKILLS,
    CURRENT_SKILLS,
    default_skill_state,
    default_target_state,
    get_skill,
    implemented_review_skill_names,
    is_review_skill,
    planned_skill_definitions,
    partial_skill_definitions,
    review_handler_key,
    trainable_skill_definitions,
)


class TestSkillAndItemRegistry(unittest.TestCase):
    def test_mage_arena_capes_keep_cache_identity_and_economy_rules(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for item_name, item_id in {
            "Saradomin cape": 2412,
            "Guthix cape": 2413,
            "Zamorak cape": 2414,
        }.items():
            with self.subTest(item_name=item_name):
                definition = by_storage_key[item_name]
                self.assertEqual(definition.source_item_id, item_id)
                self.assertEqual(definition.category, "equipment")
                self.assertEqual(definition.equipment_slot, "cape")
                self.assertFalse(definition.stackable)
                self.assertFalse(definition.tradeable)
                self.assertIsNotNone(definition.asset_path)
                self.assertTrue(os.path.exists(definition.asset_path))

    def test_slayer_shop_items_keep_source_identity_and_stackability(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        expected = {
            "Bag of salt": (4161, True),
            "Rock hammer": (4162, False),
            "Ice cooler": (6696, True),
            "Fungicide spray 10": (7421, False),
        }
        for item_name, (item_id, stackable) in expected.items():
            with self.subTest(item_name=item_name):
                definition = by_storage_key[item_name]
                self.assertEqual(definition.source_item_id, item_id)
                self.assertEqual(definition.stackable, stackable)

    def test_agility_consumable_dose_families_share_canonical_tradeability(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        expected_ids = {
            "Agility potion (4)": 3032,
            "Agility potion (3)": 3034,
            "Agility potion (2)": 3036,
            "Agility potion (1)": 3038,
            "Agility mix (2)": 11461,
            "Agility mix (1)": 11463,
        }
        for item_name, item_id in expected_ids.items():
            with self.subTest(item_name=item_name):
                definition = by_storage_key[item_name]
                self.assertTrue(definition.tradeable)
                self.assertEqual(definition.source_item_id, item_id)

    def test_current_skills_preserve_existing_display_contract(self):
        self.assertEqual(
            implemented_review_skill_names(),
            (
                "Mining",
                "Woodcutting",
                "Fishing",
                "Smithing",
                "Crafting",
                "Fletching",
                "Firemaking",
                "Cooking",
                "Runecrafting",
                "Hunter",
                "Herblore",
                "Prayer",
                "Magic",
                "Construction",
                "Thieving",
                "Agility",
                "Summoning",
            ),
        )
        self.assertTrue(is_review_skill("Mining"))
        self.assertTrue(is_review_skill("woodcutting"))
        self.assertTrue(is_review_skill("Fishing"))
        self.assertTrue(is_review_skill("Fletching"))
        self.assertTrue(is_review_skill("Firemaking"))
        self.assertTrue(is_review_skill("Cooking"))
        self.assertTrue(is_review_skill("Runecrafting"))
        self.assertTrue(is_review_skill("Hunter"))
        self.assertTrue(is_review_skill("Herblore"))
        self.assertTrue(is_review_skill("Prayer"))
        self.assertTrue(is_review_skill("Magic"))
        self.assertTrue(is_review_skill("Construction"))
        self.assertTrue(is_review_skill("Thieving"))
        self.assertTrue(is_review_skill("Agility"))
        self.assertTrue(is_review_skill("Summoning"))
        self.assertEqual(review_handler_key("Fishing"), "fishing")
        self.assertEqual(review_handler_key("Fletching"), "fletching")
        self.assertEqual(review_handler_key("Firemaking"), "firemaking")
        self.assertEqual(review_handler_key("Cooking"), "cooking")
        self.assertEqual(review_handler_key("Runecrafting"), "runecrafting")
        self.assertEqual(review_handler_key("Hunter"), "hunter")
        self.assertEqual(review_handler_key("Herblore"), "herblore")
        self.assertEqual(review_handler_key("Prayer"), "prayer")
        self.assertEqual(review_handler_key("Magic"), "magic")
        self.assertEqual(review_handler_key("Construction"), "construction")
        self.assertEqual(review_handler_key("Thieving"), "thieving")
        self.assertEqual(review_handler_key("Agility"), "agility")
        self.assertEqual(review_handler_key("Summoning"), "summoning")
        self.assertEqual(
            [skill.display_name for skill in CURRENT_SKILLS if skill.participates_in_review],
            list(implemented_review_skill_names()),
        )
        self.assertIn("Farming", [skill.display_name for skill in CURRENT_SKILLS])

    def test_review_action_registry_includes_quests_and_utility_without_making_them_skills(self):
        self.assertFalse(is_review_skill("Utility / Activities"))
        self.assertFalse(is_review_skill("Quests"))
        self.assertFalse(is_review_skill("Combat"))
        self.assertTrue(is_review_action("Utility / Activities"))
        self.assertTrue(is_review_action("Quests"))
        self.assertTrue(is_review_action("Combat"))
        self.assertTrue(is_utility_review_action("Utility"))
        self.assertTrue(is_combat_review_action("Combat"))
        self.assertEqual(review_action_handler_key("Utility / Activities"), "utility")
        self.assertEqual(review_action_handler_key("Quests"), "quest")
        self.assertEqual(review_action_handler_key("Combat"), "combat")
        self.assertEqual(review_action_handler_key("Fishing"), "fishing")
        self.assertEqual(review_action_handler_key("Fletching"), "fletching")
        self.assertEqual(review_action_handler_key("Firemaking"), "firemaking")
        self.assertEqual(review_action_handler_key("Cooking"), "cooking")
        self.assertEqual(review_action_handler_key("Runecrafting"), "runecrafting")
        self.assertEqual(review_action_handler_key("Hunter"), "hunter")
        self.assertEqual(review_action_handler_key("Herblore"), "herblore")
        self.assertEqual(review_action_handler_key("Thieving"), "thieving")
        self.assertEqual(
            review_action_display_names(),
            (
                "Mining",
                "Woodcutting",
                "Fishing",
                "Smithing",
                "Crafting",
                "Fletching",
                "Firemaking",
                "Cooking",
                "Runecrafting",
                "Hunter",
                "Herblore",
                "Prayer",
                "Magic",
                "Construction",
                "Thieving",
                "Agility",
                "Summoning",
                "Combat",
                "Quests",
                "Utility / Activities",
            ),
        )

    def test_planned_catalog_contains_2011_era_targets_without_enabling_them(self):
        planned = {skill.id: skill for skill in planned_skill_definitions()}
        for skill_id in [
            "attack",
            "constitution",
            "dungeoneering",
            "slayer",
        ]:
            self.assertIn(skill_id, planned)
            self.assertFalse(planned[skill_id].implemented)
            self.assertFalse(planned[skill_id].participates_in_review)
        self.assertEqual(len({skill.id for skill in ALL_SKILLS}), len(ALL_SKILLS))

        thieving = get_skill("Thieving")
        self.assertIsNotNone(thieving)
        self.assertTrue(thieving.implemented)
        self.assertTrue(thieving.participates_in_review)
        self.assertEqual(thieving.category, "support")
        self.assertEqual(thieving.current_target_key, "current_thieving")

    def test_farming_is_complete_background_training_without_a_reviewer_target(self):
        farming = get_skill("Farming")
        self.assertIsNotNone(farming)
        self.assertTrue(farming.implemented)
        self.assertTrue(farming.trainable)
        self.assertTrue(farming.visible_in_skill_hub)
        self.assertFalse(farming.participates_in_review)
        self.assertIsNone(farming.current_target_key)
        self.assertIsNone(farming.review_handler_key)
        self.assertIsNone(review_handler_key("Farming"))

    def test_partial_combat_skills_are_truthfully_trainable_without_complete_surfaces(self):
        partial = {skill.id: skill for skill in partial_skill_definitions()}
        self.assertEqual(
            set(partial),
            {"attack", "constitution", "defense", "ranged", "strength"},
        )
        self.assertTrue(all(skill.trainable for skill in partial.values()))
        self.assertTrue(all(skill.training_source == "Combat" for skill in partial.values()))
        self.assertTrue(all(not skill.implemented for skill in partial.values()))
        self.assertTrue(all(not skill.participates_in_review for skill in partial.values()))
        trainable = {skill.id for skill in trainable_skill_definitions()}
        self.assertTrue(set(partial).issubset(trainable))
        self.assertIn("prayer", trainable)
        self.assertIn("magic", trainable)

    def test_fletching_is_fully_playable_after_frontend_handoff(self):
        fletching = get_skill("Fletching")
        self.assertIsNotNone(fletching)
        self.assertTrue(fletching.implemented)
        self.assertTrue(fletching.participates_in_review)
        # Frontend target panel landed, so the hub gate is now open.
        self.assertTrue(fletching.visible_in_skill_hub)

    def test_firemaking_is_current_and_playable(self):
        firemaking = get_skill("Firemaking")
        self.assertIsNotNone(firemaking)
        self.assertTrue(firemaking.implemented)
        self.assertTrue(firemaking.participates_in_review)
        self.assertEqual(firemaking.current_target_key, "current_firemaking")
        self.assertEqual(firemaking.default_target, "logs")
        self.assertTrue(firemaking.visible_in_skill_hub)

    def test_fishing_is_current_and_playable(self):
        fishing = get_skill("Fishing")
        self.assertIsNotNone(fishing)
        self.assertTrue(fishing.implemented)
        self.assertTrue(fishing.participates_in_review)
        self.assertEqual(fishing.current_target_key, "current_fishing")
        self.assertEqual(fishing.default_target, "catch_crayfish")
        self.assertTrue(fishing.visible_in_skill_hub)

    def test_cooking_is_current_and_playable(self):
        cooking = get_skill("Cooking")
        self.assertIsNotNone(cooking)
        self.assertTrue(cooking.implemented)
        self.assertTrue(cooking.participates_in_review)
        self.assertEqual(cooking.current_target_key, "current_cooking")
        self.assertEqual(cooking.default_target, "cook_shrimps")
        self.assertTrue(cooking.visible_in_skill_hub)

    def test_runecrafting_is_current_and_playable_after_quest_unlock(self):
        runecrafting = get_skill("Runecrafting")
        self.assertIsNotNone(runecrafting)
        self.assertTrue(runecrafting.implemented)
        self.assertTrue(runecrafting.participates_in_review)
        self.assertEqual(runecrafting.current_target_key, "current_runecrafting")
        self.assertEqual(runecrafting.default_target, "craft_air_runes")
        self.assertTrue(runecrafting.visible_in_skill_hub)

    def test_hunter_is_current_and_playable(self):
        hunter = get_skill("Hunter")
        self.assertIsNotNone(hunter)
        self.assertTrue(hunter.implemented)
        self.assertTrue(hunter.participates_in_review)
        self.assertEqual(hunter.current_target_key, "current_hunter")
        self.assertEqual(hunter.default_target, "catch_crimson_swift")
        self.assertTrue(hunter.visible_in_skill_hub)

    def test_registry_generates_current_flat_save_defaults(self):
        self.assertEqual(
            default_skill_state(),
            {
                "mining_level": 1,
                "mining_exp": 0,
                "woodcutting_level": 1,
                "woodcutting_exp": 0,
                "farming_level": 1,
                "farming_exp": 0,
                "fishing_level": 1,
                "fishing_exp": 0,
                "smithing_level": 1,
                "smithing_exp": 0,
                "crafting_level": 1,
                "crafting_exp": 0,
                "fletching_level": 1,
                "fletching_exp": 0,
                "firemaking_level": 1,
                "firemaking_exp": 0,
                "cooking_level": 1,
                "cooking_exp": 0,
                "runecrafting_level": 1,
                "runecrafting_exp": 0,
                "hunter_level": 1,
                "hunter_exp": 0,
                "herblore_level": 1,
                "herblore_exp": 0,
                "prayer_level": 1,
                "prayer_exp": 0,
                "magic_level": 1,
                "magic_exp": 0,
                "construction_level": 1,
                "construction_exp": 0,
                "thieving_level": 1,
                "thieving_exp": 0,
                "agility_level": 1,
                "agility_exp": 0,
                "summoning_level": 1,
                "summoning_exp": 0,
            },
        )
        self.assertEqual(
            default_target_state(),
            {
                "current_ore": "rune_essence",
                "current_tree": "tree",
                "current_fishing": "catch_crayfish",
                "current_smith": "smelt_bronze_bar",
                "current_craft": "form_pot_unfired",
                "current_fletch": "arrow_shafts",
                "current_firemaking": "logs",
                "current_cooking": "cook_shrimps",
                "current_runecrafting": "craft_air_runes",
                "current_hunter": "catch_crimson_swift",
                "current_herblore": "clean_guam",
                "current_prayer": "bury_bones",
                "current_magic": "low_alchemy",
                "current_construction": "crude_wooden_chair",
                "current_thieving": "pickpocket_man",
                "current_agility": "burthorpe_course",
                "current_summoning": "infuse_spiritwolf",
            },
        )
        self.assertEqual(get_skill("Crafting").exp_key, "crafting_exp")

    def test_item_manifest_covers_existing_backend_item_tables(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        fletching_outputs = [spec["output_item"] for spec in FLETCHING_DATA.values()]
        fletching_materials = [
            material
            for spec in FLETCHING_DATA.values()
            for material in spec.get("requirements", {})
            if material not in WOODCUTTING_LOG_ITEMS
        ]
        utility_outputs = [spec["output_item"] for spec in UTILITY_ACTIVITY_DATA.values() if "output_item" in spec]
        utility_bundle_outputs = [
            item_name
            for spec in UTILITY_ACTIVITY_DATA.values()
            if isinstance(spec.get("outputs"), dict)
            for item_name in spec.get("outputs", {})
        ]
        utility_materials = [
            material
            for spec in UTILITY_ACTIVITY_DATA.values()
            for material in spec.get("requirements", {})
            if material not in MINING_OUTPUT_ITEMS
        ]
        hunter_materials = [
            material
            for spec in HUNTER_DATA.values()
            for material in spec.get("requirements", {})
        ]
        for item_name in (
            list(MINING_OUTPUT_ITEMS)
            + list(WOODCUTTING_LOG_ITEMS)
            + list(GEM_DATA)
            + list(SMITHING_OUTPUT_ITEMS)
            + [spec["output_item"] for spec in CRAFTING_DATA.values()]
            + fletching_outputs
            + fletching_materials
            + list(FIREMAKING_LOG_ITEMS)
            + list(FIREMAKING_OUTPUT_ITEMS)
            + list(FISHING_OUTPUT_ITEMS)
            + list(COOKING_OUTPUT_ITEMS)
            + list(COOKING_BURNT_ITEMS)
            + [
                material
                for spec in COOKING_DATA.values()
                for material in spec.get("requirements", {})
            ]
            + utility_outputs
            + utility_bundle_outputs
            + utility_materials
            + list(RUNECRAFTING_OUTPUT_ITEMS)
            + list(RUNECRAFTING_ACCESS_ITEMS)
            + list(RUNECRAFTING_EXTRA_ITEM_DATA)
            + list(HUNTER_OUTPUT_ITEMS)
            + hunter_materials
            + [spec["display_name"] for spec in WOODCUTTING_AXE_DATA.values()]
            + [spec["display_name"] for spec in MINING_PICKAXE_DATA.values()]
            + [spec["display_name"] for spec in MINING_BONUS_ITEM_DATA.values()]
        ):
            self.assertIn(item_name, by_storage_key)

        by_id = item_definitions_by_id(ITEM_DEFINITIONS)
        self.assertEqual(len(by_id), len(ITEM_DEFINITIONS))
        self.assertIn("Rune essence", item_storage_keys_by_category(ITEM_DEFINITIONS, "ore"))
        self.assertIn("Runite ore", item_storage_keys_by_category(ITEM_DEFINITIONS, "ore"))
        self.assertIn("Granite (5kg)", item_storage_keys_by_category(ITEM_DEFINITIONS, "ore"))
        self.assertIn("Uncut opal", item_storage_keys_by_category(ITEM_DEFINITIONS, "gem"))
        self.assertEqual(
            set(item_storage_keys_by_category(ITEM_DEFINITIONS, "log")),
            set(WOODCUTTING_LOG_ITEMS) | set(FIREMAKING_LOG_ITEMS),
        )
        self.assertEqual(set(item_storage_keys_by_category(ITEM_DEFINITIONS, "bar")), set(BAR_DATA))
        self.assertIn("Bronze dagger", item_storage_keys_by_category(ITEM_DEFINITIONS, "smithed"))
        self.assertIn("Rune platebody", item_storage_keys_by_category(ITEM_DEFINITIONS, "smithed"))
        self.assertIn("Blurite bolts (unf)", item_storage_keys_by_category(ITEM_DEFINITIONS, "smithed"))
        self.assertIn("Bronze hatchet", item_storage_keys_by_category(ITEM_DEFINITIONS, "tool"))
        self.assertIn("Bronze pickaxe", item_storage_keys_by_category(ITEM_DEFINITIONS, "tool"))
        self.assertIn("Varrock armour 1", item_storage_keys_by_category(ITEM_DEFINITIONS, "equipment"))
        self.assertIn("Arrow shafts", item_storage_keys_by_category(ITEM_DEFINITIONS, "fletched"))
        self.assertIn("Soft clay", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertIn("Wool", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertIn("Flax", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertIn("Feather", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertIn("Fishing bait", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertIn("Ashes", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertIn("Raw crayfish", item_storage_keys_by_category(ITEM_DEFINITIONS, "fish"))
        self.assertIn("Raw shark", item_storage_keys_by_category(ITEM_DEFINITIONS, "fish"))
        self.assertIn("Leaping sturgeon", item_storage_keys_by_category(ITEM_DEFINITIONS, "fish"))
        self.assertIn("Crayfish", item_storage_keys_by_category(ITEM_DEFINITIONS, "food"))
        self.assertIn("Cooked meat", item_storage_keys_by_category(ITEM_DEFINITIONS, "food"))
        self.assertIn("Burnt fish", item_storage_keys_by_category(ITEM_DEFINITIONS, "food"))
        self.assertIn("Air rune", item_storage_keys_by_category(ITEM_DEFINITIONS, "runecrafting"))
        self.assertIn("Air talisman", item_storage_keys_by_category(ITEM_DEFINITIONS, "runecrafting"))
        self.assertIn("Air tiara", item_storage_keys_by_category(ITEM_DEFINITIONS, "runecrafting"))
        self.assertIn("Binding necklace", item_storage_keys_by_category(ITEM_DEFINITIONS, "runecrafting"))
        self.assertIn("Wicked hood", item_storage_keys_by_category(ITEM_DEFINITIONS, "runecrafting"))
        self.assertIn("Red feather", item_storage_keys_by_category(ITEM_DEFINITIONS, "hunter"))
        self.assertIn("Imp-in-a-box (2)", item_storage_keys_by_category(ITEM_DEFINITIONS, "hunter"))
        self.assertIn("Bird snare", item_storage_keys_by_category(ITEM_DEFINITIONS, "tool"))
        self.assertIn("Box trap", item_storage_keys_by_category(ITEM_DEFINITIONS, "tool"))
        self.assertIn("Butterfly net", item_storage_keys_by_category(ITEM_DEFINITIONS, "tool"))
        self.assertIn("Small fishing net", item_storage_keys_by_category(ITEM_DEFINITIONS, "tool"))
        self.assertIn("Butterfly jar", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertIn("Impling jar", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertFalse(by_storage_key["Blurite ore"].tradeable)
        self.assertFalse(by_storage_key["Cursed magic logs"].tradeable)
        self.assertFalse(by_storage_key["Burnt fish"].tradeable)
        self.assertTrue(by_storage_key["Dragon pickaxe"].tradeable)
        self.assertFalse(by_storage_key["Inferno adze"].tradeable)
        self.assertFalse(by_storage_key["Varrock armour 4"].tradeable)
        self.assertEqual(by_storage_key["Varrock armour 4"].equipment_slot, "body")
        for item_name in (
            "Amulet of glory",
            "Amulet of glory (t)",
            "Amulet of glory (t1)",
            "Amulet of glory (t2)",
            "Amulet of glory (t3)",
            "Amulet of glory (t4)",
        ):
            self.assertEqual(by_storage_key[item_name].category, "equipment")
            self.assertEqual(by_storage_key[item_name].equipment_slot, "neck")
        for item_name in (
            "Amulet of glory (t)",
            "Amulet of glory (t1)",
            "Amulet of glory (t2)",
            "Amulet of glory (t3)",
            "Amulet of glory (t4)",
        ):
            asset_path = by_storage_key[item_name].asset_path
            self.assertIsNotNone(asset_path, f"{item_name} should have a Mining icon")
            self.assertTrue(os.path.exists(asset_path), f"{item_name} Mining icon is missing")
        self.assertEqual(by_storage_key["Rune platebody"].equipment_slot, "body")
        self.assertEqual(by_storage_key["Rune platebody"].equipment_tier, 40)
        self.assertEqual(by_storage_key["Rune knife"].equipment_slot, "weapon")

    def test_firemaking_item_assets_are_registered(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for item_name in (
            "Ashes",
            "Arctic pine logs",
            "Eucalyptus logs",
            "Curly root",
            "Cursed magic logs",
        ):
            self.assertIn(item_name, by_storage_key)
            self.assertIn(item_name, FIREMAKING_ITEM_IMAGES)
            self.assertTrue(os.path.exists(FIREMAKING_ITEM_IMAGES[item_name]))
            self.assertEqual(by_storage_key[item_name].asset_path, FIREMAKING_ITEM_IMAGES[item_name])
        self.assertEqual(FIREMAKING_DATA["cursed_magic_logs"]["requirements"], {"Cursed magic logs": 1})

    def test_light_source_items_and_icons_are_registered(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        expected = {
            "Unlit torch": 596,
            "Lit torch": 594,
            "Candle lantern (empty)": 4527,
            "Candle lantern (unlit, 4529)": 4529,
            "Candle lantern (lit, 4531)": 4531,
            "Oil lamp (empty)": 4525,
            "Oil lamp (unlit)": 4522,
            "Oil lantern (empty)": 4535,
            "Oil lantern (unlit)": 4537,
            "Bullseye lantern (unf)": 4544,
            "Bullseye lantern (empty)": 4546,
            "Bullseye lantern (unlit)": 4548,
            "Sapphire lantern (empty)": 4700,
            "Sapphire lantern (unlit)": 4701,
            "Mining helmet (unlit)": 5014,
            "Mining helmet (lit)": 5013,
        }
        for item_name, item_id in expected.items():
            self.assertIn(item_name, by_storage_key)
            self.assertEqual(by_storage_key[item_name].source_item_id, item_id)
            self.assertIn(item_name, FIREMAKING_ITEM_IMAGES)
            self.assertTrue(os.path.exists(FIREMAKING_ITEM_IMAGES[item_name]))
            self.assertEqual(by_storage_key[item_name].asset_path, FIREMAKING_ITEM_IMAGES[item_name])
        self.assertEqual(by_storage_key["Mining helmet (unlit)"].equipment_slot, "head")
        self.assertEqual(by_storage_key["Mining helmet (lit)"].equipment_slot, "head")
        self.assertEqual(by_storage_key["Mining helmet (unlit)"].category, "equipment")
        self.assertEqual(by_storage_key["Mining helmet (lit)"].category, "equipment")

    def test_fishing_items_and_assets_are_registered(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for item_name in (
            "Raw crayfish",
            "Raw shrimps",
            "Raw anchovies",
            "Raw salmon",
            "Raw shark",
            "Leaping sturgeon",
            "Fishing bait",
            "Living minerals",
        ):
            self.assertIn(item_name, by_storage_key)
            self.assertIn(item_name, FISHING_ITEM_IMAGES)
            self.assertTrue(os.path.exists(FISHING_ITEM_IMAGES[item_name]), f"{item_name} Fishing icon is missing")
        self.assertEqual(by_storage_key["Raw crayfish"].category, "fish")
        self.assertEqual(by_storage_key["Raw crayfish"].base_exp, 10.0)
        self.assertEqual(FISHING_DATA["catch_sardine_herring"]["requirements"], {"Fishing bait": 1})
        self.assertEqual(FISHING_DATA["catch_crayfish"]["requirements"], {})

    def test_crafting_source_data_uses_stable_ids_and_live_targets(self):
        self.assertNotIn("Soft clay", CRAFTING_DATA)
        self.assertIn("form_pot_unfired", CRAFTING_DATA)
        self.assertEqual(CRAFTING_DATA["form_pot_unfired"]["requirements"], {"Soft clay": 1})
        self.assertEqual(CRAFTING_DATA["fire_empty_pot"]["requirements"], {"Pot (unfired)": 1})
        self.assertEqual(CRAFTING_DATA["cut_emerald"]["exp"], 67.0)
        self.assertEqual(CRAFTING_DATA["jewellery_sapphire_necklace"]["exp"], 55.0)
        self.assertEqual(CRAFTING_DATA["spin_wool_to_ball_of_wool"]["exp"], 2.5)
        self.assertNotIn("batch_size", CRAFTING_DATA["spin_flax_to_bow_string"])
        self.assertEqual(CRAFTING_DATA["silver_silver_bolts_unf"]["output_qty"], 10)
        self.assertIn("cut_dragonstone", CRAFTING_DATA)
        self.assertIn("jewellery_dragonstone_ring", CRAFTING_DATA)
        self.assertIn("input-starved", CRAFTING_DATA["cut_dragonstone"].get("notes", ""))
        self.assertEqual(UTILITY_ACTIVITY_DATA["make_soft_clay"]["batch_size"], 28)

    def test_combination_and_polishing_outputs_register_as_crafted_items(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for item_name in (
            "Strange skull",
            "Skull sceptre",
            "Emerald lantern (unlit)",
            "Studded chaps",
            "Spiky vambraces",
            "Crab helmet",
            "Empty seaweed net",
            "Armadyl battlestaff",
            "Unblessed symbol",
            "Unpowered symbol",
            "Polished buttons",
        ):
            self.assertIn(item_name, by_storage_key)
            self.assertEqual(by_storage_key[item_name].category, "crafted")

    def test_unstrung_amulets_are_distinct_non_equipment_registry_items(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for unstrung, strung, source_item_id in (
            ("Gold amulet (u)", "Gold amulet", 1673),
            ("Sapphire amulet (u)", "Sapphire amulet", 1675),
            ("Emerald amulet (u)", "Emerald amulet", 1677),
            ("Ruby amulet (u)", "Ruby amulet", 1679),
            ("Diamond amulet (u)", "Diamond amulet", 1681),
            ("Dragonstone ammy (u)", "Dragonstone ammy", 1683),
            ("Onyx amulet (u)", "Onyx amulet", 6579),
        ):
            with self.subTest(unstrung=unstrung):
                self.assertEqual(by_storage_key[unstrung].category, "crafted")
                self.assertEqual(by_storage_key[unstrung].source_item_id, source_item_id)
                self.assertIsNone(by_storage_key[unstrung].equipment_slot)
                self.assertEqual(by_storage_key[strung].equipment_slot, "neck")

    def test_pestle_and_mortar_remainder_matches_2011scape_item_pairs(self):
        expected = {
            "grind_anchovies": ("Anchovies", 319, "Anchovy paste", 11266),
            "grind_tchiki_monkey_nuts": ("Tchiki monkey nuts", 7573, "Tchiki nut paste", 7575),
            "grind_dramen_branch": ("Dramen branch", 771, "Cinnamon", 7472),
            "grind_garlic": ("Garlic", 1550, "Garlic powder", 4668),
            "grind_astral_rune_shards": ("Astral rune shards", 11156, "Ground astral rune", 11155),
            "grind_bat_bones": ("Bat bones", 530, "Ground bat bones", 2391),
            "grind_charcoal": ("Charcoal", 973, "Ground charcoal", 704),
            "grind_clean_guam": ("Clean guam", 249, "Ground guam", 6681),
            "grind_crab_meat": ("Crab meat", 7518, "Ground crab meat", 7527),
            "grind_raw_cod": ("Raw cod", 341, "Ground cod", 7528),
            "grind_suqah_tooth": ("Suqah tooth", 9079, "Ground tooth", 9082),
            "grind_kelp": ("Kelp", 7516, "Ground kelp", 7517),
            "grind_rune_shards": ("Rune shards", 6466, "Rune dust", 6467),
            "grind_dried_thistle": ("Dried thistle", 3263, "Ground thistle", 3264),
            "grind_gorak_claws": ("Gorak claws", 9016, "Gorak claw powder", 9018),
            "grind_ashes": ("Ashes", 592, "Ground ashes", 8865),
            "grind_raw_karambwan": ("Raw karambwan", 3142, "Karambwan paste", 3152),
            "grind_cooked_karambwan": ("Cooked karambwan", 3144, "Karambwan paste", 3154),
            "grind_poison_karambwan": ("Poison karambwan", 3146, "Karambwan paste", 3153),
            "grind_diamond_root": ("Diamond root", 14703, "Diamond root dust", 14704),
            "grind_black_mushroom": ("Black mushroom", 4620, "Black mushroom ink", 4622),
            "grind_shards_of_armadyl": ("Shards of armadyl", 21776, "Dust of armadyl", 21774),
            "grind_fishing_bait": ("Fishing bait", 313, "Ground fishing bait", 12129),
            "grind_seaweed": ("Seaweed", 401, "Ground seaweed", 6683),
        }
        self.assertEqual(set(expected), {key for key, spec in UTILITY_ACTIVITY_DATA.items() if spec.get("group") == "grinding"} - {
            "grind_unicorn_horn", "grind_chocolate_bar", "grind_kebbit_teeth", "grind_birds_nest",
            "grind_desert_goat_horn", "grind_blue_dragon_scale", "grind_mud_rune",
        })
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for activity_id, (source_item, source_item_id, output_item, output_item_id) in expected.items():
            activity = UTILITY_ACTIVITY_DATA[activity_id]
            self.assertEqual(activity["requirements"], {source_item: 1})
            self.assertEqual(activity["source_item_id"], source_item_id)
            self.assertEqual(activity["output_item"], output_item)
            self.assertEqual(activity["output_item_id"], output_item_id)
            self.assertEqual(activity["output_qty"], 1)
            self.assertEqual(activity["batch_size"], 28)
            self.assertEqual(activity["group"], "grinding")
            self.assertIn(source_item, by_storage_key)
            self.assertIsNotNone(by_storage_key[output_item].asset_path)
        grinding_rows = {
            key: spec for key, spec in UTILITY_ACTIVITY_DATA.items() if spec.get("group") == "grinding"
        }
        self.assertEqual(len(grinding_rows), 31)
        prep_rows = {
            key: spec for key, spec in UTILITY_ACTIVITY_DATA.items() if spec.get("group") == "input_preparation"
        }
        self.assertEqual(set(prep_rows), {"fill_vial_of_water", "remove_swamp_toad_legs"})
        self.assertTrue(all(float(spec.get("exp", 0.0) or 0.0) == 0.0 for spec in prep_rows.values()))
        self.assertTrue(all(spec.get("batch_size") == 28 for spec in prep_rows.values()))

        self.assertEqual(
            HERBLORE_DATA["finished_super_prayer"]["requirements"],
            {"Prayer potion (3)": 1, "Wyvern bonemeal": 1},
        )
        self.assertEqual(PRAYER_EXTRA_ITEM_DATA["Bonemeal"]["item_id"], 4255)
        self.assertEqual(PRAYER_EXTRA_ITEM_DATA["Wyvern bonemeal"]["item_id"], 6810)
        self.assertEqual(HERBLORE_EXTRA_ITEM_DATA["Wyvern bonemeal"]["item_id"], 6810)
        self.assertNotEqual(
            PRAYER_EXTRA_ITEM_DATA["Bonemeal"]["item_id"],
            HERBLORE_EXTRA_ITEM_DATA["Wyvern bonemeal"]["item_id"],
        )
        self.assertIn("Bonemeal", by_storage_key)
        self.assertIn("Wyvern bonemeal", by_storage_key)
        self.assertIsNotNone(by_storage_key["Bonemeal"].asset_path)
        self.assertIsNotNone(by_storage_key["Wyvern bonemeal"].asset_path)
        overload = HERBLORE_DATA["finished_overload"]
        self.assertEqual(overload["level"], 96)
        self.assertEqual(overload["exp"], 1000.0)
        self.assertEqual(overload["byproducts"], {"Vial": 4})
        self.assertEqual(HERBLORE_EXTRA_ITEM_DATA["Overload (3)"]["item_id"], 15333)
        self.assertFalse(HERBLORE_EXTRA_ITEM_DATA["Overload (3)"]["tradeable"])
        for item in (
            "Extreme attack (3)",
            "Extreme strength (3)",
            "Extreme defence (3)",
            "Extreme magic (3)",
            "Extreme ranging (3)",
        ):
            self.assertFalse(HERBLORE_EXTRA_ITEM_DATA[item]["tradeable"])

    def test_crossbow_combination_items_register_as_fletching_items(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for item_name in (
            "Bronze c'bow (u)",
            "Blurite c'bow (u)",
            "Iron c'bow (u)",
            "Steel c'bow (u)",
            "Mithril c'bow (u)",
            "Adamant c'bow (u)",
            "Runite c'bow (u)",
            "Bronze crossbow",
            "Blurite crossbow",
            "Iron crossbow",
            "Steel crossbow",
            "Mith crossbow",
            "Adamant crossbow",
            "Rune crossbow",
        ):
            self.assertEqual(by_storage_key[item_name].category, "fletched")
            self.assertIsNotNone(by_storage_key[item_name].asset_path)

    def test_utility_activities_have_purpose_built_icon_contract(self):
        expected_files = {
            "make_soft_clay": "make_soft_clay.png",
            "gather_wool": "gather_wool.png",
            "gather_flax": "gather_flax.png",
            "open_bird_nest": "open_bird_nest.png",
        }
        self.assertTrue(set(expected_files).issubset(UTILITY_ACTIVITY_DATA))
        for activity_key, file_name in expected_files.items():
            icon_path = UTILITY_ACTIVITY_DATA[activity_key].get("icon_path")
            self.assertIsInstance(icon_path, str, activity_key)
            self.assertEqual(os.path.basename(icon_path), file_name)
            self.assertEqual(os.path.basename(os.path.dirname(icon_path)), "activityicons")
            self.assertTrue(os.path.exists(icon_path), f"{activity_key} icon path is missing")
        # Retired 2026-07-06: their outputs are live NPC shop stock now.
        self.assertNotIn("scavenge_chicken_feathers", UTILITY_ACTIVITY_DATA)
        self.assertNotIn("gather_fishing_bait", UTILITY_ACTIVITY_DATA)
        self.assertNotIn("buy_hunter_supplies", UTILITY_ACTIVITY_DATA)
        self.assertIn("gather_grain", UTILITY_ACTIVITY_DATA)
        self.assertEqual(UTILITY_ACTIVITY_DATA["gather_grain"]["group"], "gathering")
        self.assertIn("assemble_uncooked_pizza", UTILITY_ACTIVITY_DATA)
        self.assertEqual(UTILITY_ACTIVITY_DATA["assemble_uncooked_pizza"]["group"], "cooking_prep")

    def test_registered_asset_paths_exist_for_current_manifest(self):
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())

    def test_npc_shop_actionable_item_assets_are_registered(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        expected = (
            "Newspaper",
            "Kebab",
            "Antlers",
            "Lizard skull",
            "Feather headdress",
            "Spirit shards",
            "Pouch",
            "Spirit shard pack",
            # Backfill pass: derived from SHOP_DATA by tools/fetch_shop_assets.py.
            # (Spade resolves through the quest item registry, not shopitems/.)
            "Rake",
            "Seed dibber",
            "Secateurs",
            "Gardening trowel",
            "Watering can",
        )
        for item_name in expected:
            self.assertIn(item_name, SHOP_ITEM_IMAGES)
            self.assertEqual(by_storage_key[item_name].asset_path, SHOP_ITEM_IMAGES[item_name])
        for item_name in ("Erzille seed", "Ugune seed", "Argway seed", "Shengo seed", "Samaden seed"):
            self.assertIn(item_name, by_storage_key)
            self.assertEqual(by_storage_key[item_name].asset_path, FARMING_ITEM_IMAGES[item_name])
            self.assertTrue(os.path.exists(FARMING_ITEM_IMAGES[item_name]))
        # Coin-paid conversion outputs register through the Utility path now
        # (the sawmill/tanning shop services became review-paced activities),
        # but must still resolve their existing art.
        for item_name in ("Oak plank", "Plank", "Leather", "Hard leather"):
            self.assertTrue(by_storage_key[item_name].asset_path, item_name)
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())

    def test_npc_shop_visible_stock_icon_coverage_has_only_known_gaps(self):
        """Every visible live/locked shop row resolves an icon except a pinned
        set of wiki-unresolvable items (color-variant clothing files). New
        gaps mean the shop generator grew stock without a matching asset
        fetch."""
        import os

        from shop_data import SHOP_DATA

        known_gaps = {
            "Boots", "Damaged book", "Fremennik cloak", "Fremennik shirt",
            "Gloves", "Hat", "Karidian headpiece", "Pirate bandana",
            "Pirate leggings", "Robe bottoms", "Robe top", "Shantay pass",
            "Shirt", "Shorts", "Skirt", "Stripy pirate shirt", "Tribal top",
            "Trousers", "Villager armband", "Villager hat", "Villager robe",
            "Villager sandals", "Woven top",
        }
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        missing = set()
        for shop in SHOP_DATA.values():
            if shop.get("visibility") == "hidden":
                continue
            for row in shop.get("stock", []):
                name = row.get("item_name", "")
                if not name or row.get("disposition") == "blocked":
                    continue
                definition = by_storage_key.get(name)
                asset_path = definition.asset_path if definition else None
                if not (asset_path and os.path.exists(asset_path)):
                    missing.add(name)
        self.assertEqual(missing - known_gaps, set())

    def test_combat_items_are_registered_with_icons(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        expected = {
            "Banana": "food",
            "Bat bones": "material",
            "Bear fur": "material",
            "Big bones": "material",
            "Black bead": "material",
            "Black kiteshield": "equipment",
            "Black sq shield": "equipment",
            "Brass necklace": "equipment",
            "Bronze spear": "equipment",
            "Wooden shield": "equipment",
            "Champion's scroll": "material",
            "Tinderbox": "tool",
            "Cape": "equipment",
            "Cadava berries": "material",
            "Chef's hat": "equipment",
            "Chilli potato": "food",
            "Clue scroll (easy)": "material",
            "Clue scroll (medium)": "material",
            "Coins": "material",
            "Cowhide": "material",
            "Beer": "food",
            "Buttons": "material",
            "Curved bone": "material",
            "Damaged armour": "material",
            "Dragon spear": "equipment",
            "Eye patch": "equipment",
            "Fire battlestaff": "equipment",
            "Goblin book": "material",
            "Half an apple pie": "food",
            "Half a summer pie": "food",
            "Kebab": "food",
            "H.A.M. boots": "equipment",
            "H.A.M. cloak": "equipment",
            "H.A.M. gloves": "equipment",
            "H.A.M. hood": "equipment",
            "H.A.M. logo": "equipment",
            "H.A.M. robe": "equipment",
            "H.A.M. shirt": "equipment",
            "Impious ashes": "material",
            "Iron javelin": "material",
            "Iron spear": "equipment",
            "Jug": "material",
            "Jug of wine": "food",
            "Loop half of a key": "material",
            "Long bone": "material",
            "Magic staff": "equipment",
            "Mithril spear": "equipment",
            "Muddy key": "material",
            "Needle": "material",
            "Obsidian cape": "equipment",
            "Obsidian charm": "material",
            "Red bead": "material",
            "Rune javelin": "equipment",
            "Rune spear": "equipment",
            "Rusty sword": "material",
            "Shears": "tool",
            "Shield left half": "material",
            "Spinach roll": "food",
            "Staff": "equipment",
            "Staff of air": "equipment",
            "Staff of water": "equipment",
            "Staff of earth": "equipment",
            "Staff of fire": "equipment",
            "Steel spear": "equipment",
            "Super defence (1)": "material",
            "Super strength (1)": "material",
            "Thread": "material",
            "Tokkul": "material",
            "Toktz-ket-xil": "equipment",
            "Tooth half of a key": "material",
            "Tzhaar-ket-om": "equipment",
            "Unicorn horn": "material",
            "Vial of water": "material",
            "White bead": "material",
            "Wolf bones": "material",
            "Wizard hat": "equipment",
            "Yellow bead": "material",
            "Zamorak robe bottom": "equipment",
            "Zamorak robe top": "equipment",
            "Gold charm": "material",
            "Green charm": "material",
            "Crimson charm": "material",
            "Blue charm": "material",
        }
        for item_name, category in expected.items():
            self.assertIn(item_name, by_storage_key)
            self.assertEqual(by_storage_key[item_name].category, category)
            self.assertIn(item_name, COMBAT_ITEM_IMAGES)
            self.assertTrue(os.path.exists(COMBAT_ITEM_IMAGES[item_name]), f"{item_name} Combat icon is missing")
            self.assertEqual(by_storage_key[item_name].asset_path, COMBAT_ITEM_IMAGES[item_name])
        for herb_name in (
            "Grimy guam",
            "Grimy marrentill",
            "Grimy tarromin",
            "Grimy harralander",
            "Grimy ranarr",
            "Grimy irit",
            "Grimy avantoe",
            "Grimy kwuarm",
            "Grimy cadantine",
            "Grimy lantadyme",
            "Grimy dwarf weed",
        ):
            self.assertIn(herb_name, by_storage_key)
            self.assertEqual(by_storage_key[herb_name].category, "material")
        for item_name in ("Bronze javelin", "Grapes", "Knife"):
            self.assertIn(item_name, by_storage_key)
            self.assertEqual(by_storage_key[item_name].category, "material")
        for item_name in (
            "Antipoison (1)",
            "Antipoison (2)",
            "Antipoison (3)",
            "Antipoison (4)",
            "Avantoe seed",
            "Belladonna seed",
            "Potato seed",
            "Onion seed",
            "Cabbage seed",
            "Cactus seed",
            "Cadantine seed",
            "Tomato seed",
            "Sweetcorn seed",
            "Dwarf weed seed",
            "Harralander seed",
            "Irit seed",
            "Jangerberry seed",
            "Kwuarm seed",
            "Lantadyme seed",
            "Limpwurt seed",
            "Marrentill seed",
            "Poison ivy seed",
            "Ranarr seed",
            "Snapdragon seed",
            "Strawberry seed",
            "Super antipoison (1)",
            "Super antipoison (2)",
            "Super antipoison (3)",
            "Super antipoison (4)",
            "Tarromin seed",
            "Toadflax seed",
            "Torstol seed",
            "Watermelon seed",
            "Whiteberry seed",
            "Wildblood seed",
            "Gardening boots",
        ):
            self.assertIn(item_name, by_storage_key)
            self.assertEqual(by_storage_key[item_name].category, "material")
        self.assertIn("Vial", by_storage_key)
        self.assertEqual(by_storage_key["Vial"].category, "crafted")
        for item_name in ("Rake", "Seed dibber", "Secateurs", "Watering can (8)"):
            self.assertIn(item_name, by_storage_key)
            self.assertEqual(by_storage_key[item_name].category, "tool")
        self.assertIn("Bronze scimitar", by_storage_key)
        self.assertEqual(by_storage_key["Bronze scimitar"].category, "smithed")
        self.assertIn("Nature rune", by_storage_key)
        self.assertEqual(by_storage_key["Nature rune"].category, "runecrafting")
        self.assertEqual(EQUIPMENT_DATA["Cape"].slot, "cape")
        self.assertEqual(EQUIPMENT_DATA["Cape"].bonuses.defence_ranged, 2)
        self.assertEqual(EQUIPMENT_DATA["Bronze spear"].slot, "weapon")
        self.assertEqual(EQUIPMENT_DATA["Bronze spear"].bonuses.melee_strength, 6)
        self.assertEqual(EQUIPMENT_DATA["Iron spear"].slot, "weapon")
        self.assertEqual(EQUIPMENT_DATA["Iron spear"].bonuses.melee_strength, 10)
        self.assertEqual(EQUIPMENT_DATA["Steel spear"].slot, "weapon")
        self.assertEqual(EQUIPMENT_DATA["Steel spear"].required_level, 5)
        self.assertEqual(EQUIPMENT_DATA["Staff"].slot, "weapon")
        self.assertEqual(EQUIPMENT_DATA["Staff"].bonuses.attack_magic, 4)
        self.assertEqual(EQUIPMENT_DATA["Staff of air"].slot, "weapon")
        self.assertEqual(EQUIPMENT_DATA["Staff of air"].bonuses.attack_magic, 10)
        self.assertEqual(by_storage_key["Dragon sq shield"].category, "smithed")
        self.assertIsNotNone(by_storage_key["Dragon sq shield"].asset_path)
        self.assertEqual(EQUIPMENT_DATA["Dragon sq shield"].slot, "shield")
        self.assertEqual(EQUIPMENT_DATA["Dragon sq shield"].required_level, 60)
        self.assertEqual(EQUIPMENT_DATA["Dragon sq shield"].bonuses.defence_slash, 52)
        for item_name in (
            "Shortbow",
            "Longbow",
            "Oak shortbow",
            "Oak longbow",
            "Willow shortbow",
            "Willow longbow",
            "Maple shortbow",
            "Maple longbow",
            "Yew shortbow",
            "Yew longbow",
            "Magic shortbow",
            "Magic longbow",
            "Bronze arrows",
            "Iron arrows",
            "Steel arrows",
            "Mithril arrows",
            "Adamant arrows",
            "Rune arrows",
        ):
            self.assertIn(item_name, by_storage_key)
            self.assertEqual(by_storage_key[item_name].asset_path, FLETCHED_ITEM_IMAGES[item_name])
            self.assertTrue(os.path.exists(FLETCHED_ITEM_IMAGES[item_name]), f"{item_name} Fletching icon is missing")

    def test_woodcutting_bank_items_have_icons(self):
        # Logs reuse the trees/ sprites; hatchets and bird nests were fetched
        # into woodcuttingitems/. All three surfaces should resolve an icon so
        # the Bank/Stats panels don't show blank rows for real Woodcutting drops.
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for name in ("Logs", "Oak logs", "Bark", "Achey tree logs", "Magic logs"):
            self.assertIsNotNone(by_storage_key[name].asset_path, f"{name} should have a log icon")
        for name in [spec["display_name"] for spec in WOODCUTTING_AXE_DATA.values()]:
            self.assertIsNotNone(by_storage_key[name].asset_path, f"{name} should have a hatchet icon")
        self.assertIsNotNone(by_storage_key["Bird's nest (seeds)"].asset_path)

    def test_mining_target_rows_have_output_icons(self):
        # Every Mining target row resolves an icon from its output: a single
        # output_item for ordinary rocks, or the representative first weighted
        # output for the variable rocks (Sandstone/Granite/Gem rocks). These were
        # fetched by tools/fetch_mining_assets.py; a missing one means a blank row.
        try:
            from ui import ORE_IMAGES, GEM_IMAGES  # type: ignore
        except Exception:
            from constants import ORE_IMAGES, GEM_IMAGES  # type: ignore
        for target_id, spec in ORE_DATA.items():
            weighted = spec.get("weighted_outputs") or ()
            if weighted:
                icon_key = weighted[0]["item"]
            else:
                icon_key = spec.get("output_item")
            self.assertIsNotNone(icon_key, f"{target_id} has no resolvable output for an icon")
            self.assertTrue(
                bool(ORE_IMAGES.get(icon_key) or GEM_IMAGES.get(icon_key)),
                f"Mining target {target_id!r} row icon missing for {icon_key!r}",
            )

    def test_mining_bank_items_have_icons(self):
        # Ores, gem-rock gems, and standard pickaxes should all carry an
        # asset_path so Bank/Stats rows aren't blank for real Mining drops/tools.
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for name in ("Blurite ore", "Limestone", "Pure essence", "Sandstone (10kg)", "Granite (5kg)"):
            self.assertIsNotNone(by_storage_key[name].asset_path, f"{name} should have an ore icon")
        for name in ("Uncut opal", "Uncut jade", "Uncut red topaz"):
            self.assertIsNotNone(by_storage_key[name].asset_path, f"{name} should have a gem icon")
        for name in ("Bronze pickaxe", "Rune pickaxe", "Inferno adze", "Dragon pickaxe"):
            self.assertIsNotNone(by_storage_key[name].asset_path, f"{name} should have a pickaxe icon")

    def test_every_smithing_output_resolves_an_icon(self):
        # The full forge table (tools/fetch_smithing_assets.py derives its manifest
        # from SMITHING_DATA) is fetched, so every distinct smelt/forge output must
        # resolve an asset_path -- no blank rows in the ~166-row panel. Forged
        # pickaxes/hatchets resolve via the gathering art they share a name with;
        # the rest resolve from smithingitems/ (forged) or bars/ (Blurite bar).
        from constants import SMITHING_DATA  # local import: large module

        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        iconless = sorted(
            {
                spec["output_item"]
                for spec in SMITHING_DATA.values()
                if not (
                    spec["output_item"] in by_storage_key
                    and by_storage_key[spec["output_item"]].asset_path
                )
            }
        )
        self.assertEqual(iconless, [], f"Smithing outputs missing icons: {iconless}")
        self.assertIsNotNone(by_storage_key["Blurite bar"].asset_path)
        self.assertIsNotNone(by_storage_key["Rune pickaxe"].asset_path)  # reuses mining art
        # The wiring is existence-guarded, so no registered path may be dead.
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())

    def test_every_crafting_output_resolves_an_icon(self):
        # tools/fetch_crafting_assets.py derives its manifest from CRAFTING_DATA,
        # so every distinct craft *output* must resolve an asset_path -- no blank
        # rows in the family-grouped panel, including the dependency-heavy
        # dragonstone/onyx/hide/glass/battlestaff targets that are wired live.
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        iconless = sorted(
            {
                spec["output_item"]
                for spec in CRAFTING_DATA.values()
                if not (
                    spec["output_item"] in by_storage_key
                    and by_storage_key[spec["output_item"]].asset_path
                )
            }
        )
        self.assertEqual(iconless, [], f"Crafting outputs missing icons: {iconless}")
        # Spot-check a few input-only materials wired through crafteditems/ so the
        # Bank isn't blank for raw crafting inputs that have no other skill's art.
        for material in ("Leather", "Molten glass", "Water orb"):
            self.assertIsNotNone(
                by_storage_key[material].asset_path, f"{material} should have a crafting icon"
            )
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())

    def test_crafting_tool_gates_are_registered_with_icons(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for item_name, source_item_id in CRAFTING_REQUIRED_ITEM_SOURCE_IDS.items():
            self.assertEqual(CRAFTING_REQUIRED_ITEM_DATA[item_name]["item_id"], source_item_id)
            self.assertEqual(by_storage_key[item_name].category, "tool")
            self.assertIn(item_name, CRAFTED_ITEM_IMAGES)
            self.assertTrue(os.path.exists(CRAFTED_ITEM_IMAGES[item_name]), f"{item_name} Crafting icon is missing")
            self.assertEqual(by_storage_key[item_name].asset_path, CRAFTED_ITEM_IMAGES[item_name])
        for item_name, source_item_id in {
            "Unholy mould": 1594,
            "Conductor mould": 4200,
            "Demonic sigil mould": 6747,
            "Rod clay mould": 7649,
            "Chain link mould": 13153,
        }.items():
            self.assertEqual(CRAFTING_REQUIRED_ITEM_DATA[item_name]["item_id"], source_item_id)
            self.assertFalse(CRAFTING_REQUIRED_ITEM_DATA[item_name]["tradeable"])
            self.assertFalse(by_storage_key[item_name].tradeable)

    def test_crafting_tool_registration_preserves_existing_item_identities(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for item_name, item_id, category in (
            ("Bronze wire", "smithed_bronze_wire", "smithed"),
            ("Steel studs", "smithed_steel_studs", "smithed"),
            ("Oil lantern frame", "smithed_oil_lantern_frame", "smithed"),
            ("Sinew", "food_sinew", "food"),
        ):
            self.assertEqual(by_storage_key[item_name].id, item_id)
            self.assertEqual(by_storage_key[item_name].category, category)

    def test_every_fishing_output_resolves_an_icon(self):
        # tools/fetch_fishing_assets.py derives its manifest from FISHING_DATA,
        # so every live catch output must resolve an asset_path -- no blank rows
        # in the output-first Fishing target list.
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        iconless = sorted(
            item_name
            for item_name in FISHING_OUTPUT_ITEMS
            if not (
                item_name in by_storage_key
                and by_storage_key[item_name].asset_path
            )
        )
        self.assertEqual(iconless, [], f"Fishing outputs missing icons: {iconless}")
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())

    def test_every_cooking_item_resolves_an_icon(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        iconless = sorted(
            item_name
            for item_name in COOKING_EXTRA_ITEM_DATA
            if not (
                item_name in by_storage_key
                and by_storage_key[item_name].asset_path
            )
        )
        self.assertEqual(iconless, [], f"Cooking items missing icons: {iconless}")
        for item_name in ("Cooking apple", "Burnt fish", "Cooked meat", "Raw wild pie", "Redberry pie", "Raw lava eel", "Lava eel"):
            self.assertIn(item_name, COOKING_ITEM_IMAGES)
            self.assertTrue(os.path.exists(COOKING_ITEM_IMAGES[item_name]))
        for item_name in ("Redberry pie", "Blurite ore", "Iron bar"):
            self.assertIn(item_name, by_storage_key)
            self.assertIsNotNone(by_storage_key[item_name].asset_path, f"{item_name} should have a quest-stage icon")
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())

    def test_quest_stage_items_resolve_icons(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for item_name in (
            "Silverlight",
            "Silverlight key",
            "Railing",
            "Dwarf remains",
            "Toolkit",
            "Nulodion's notes",
            "Ammo mould",
            "Orange goblin mail",
            "Blue goblin mail",
            "Goblin mail",
            "Fish food",
            "Poison",
            "Poisoned fish food",
            "Pressure gauge",
            "Grimy key",
            "Rubber tube",
            "Oil can",
            "Maze key",
            "Anti-dragon shield",
            "Map part",
            "Crandor map",
            "Wizard's mind bomb",
            "Silk",
            "Crayfish cage",
            "Lobster pot",
            "Plank",
            "Hammer",
            "Elvarg's head",
            "Shield of Arrav book",
            "Intel report",
            "Weapon store key",
            "Phoenix crossbow",
            "Broken shield (Phoenix half)",
            "Broken shield (Black Arm half)",
            "Half certificate (Phoenix)",
            "Half certificate (Black Arm)",
            "Certificate",
            "Khazard helmet",
            "Khazard armour",
            "Khali brew",
            "Khazard cell keys",
            "Door key",
            "Magnet",
            "Backroom key",
            "Ball",
            "Insect repellent",
            "Bucket of wax",
            "Black candle",
            "Lit black candle",
            "Excalibur",
            "Bat bones",
            "Fishing pass",
            "Red vine worm",
            "Raw giant carp",
            "Fishing trophy",
            "Garlic",
            "Fishing rod",
            "Bucket of milk",
            "Doogle leaves",
            "Doogle sardine",
            "Three little kittens",
            "Pet kitten",
            "White cog",
            "Black cog",
            "Blue cog",
            "Red cog",
            "Rat poison",
            "Ice gloves",
            "Child's blanket",
            "Jug of water",
            "Address label",
            "Totem",
            "Scorpion cage",
            "Sheep feed",
            "Plague jacket",
            "Plague trousers",
            "Cattleprod",
            "Red sheep bones",
            "Green sheep bones",
            "Blue sheep bones",
            "Yellow sheep bones",
            "Dwellberries",
            "Gas mask",
            "Picture of Elena",
            "Turnip growing for beginners",
            "Scruffy note",
            "Hangover cure",
            "Warrant",
            "A small key",
            "Chocolate dust",
            "Snape grass",
            "Bucket",
            "Pestle and mortar",
            "Spade",
            "Bird feed",
            "Pigeon cage",
            "Rotten apple",
            "Doctors' gown",
            "Key",
            "Distillator",
            "Liquid honey",
            "Ethenea",
            "Sulphuric broline",
            "Plague sample",
            "Touch paper",
            "Priest gown",
            "Blamish snail slime",
            "Harralander potion (unf)",
            "Blamish oil",
            "Oily fishing rod",
            "Raw lava eel",
            "Lava eel",
            "Fire feather",
            "Id papers",
            "Black full helm",
            "Black platebody",
            "Black platelegs",
            "Pete's candlestick",
            "Thieves' armband",
            "Ring mould",
            "Necklace mould",
            "Antipoison",
            "Perfect gold ore",
            "Perfect gold bar",
            "Perfect ruby ring",
            "Perfect ruby necklace",
            "Caleb crest",
            "Avan crest",
            "Johnathon crest",
            "Family crest",
            "Family gauntlets",
            "Cooking gauntlets",
            "Goldsmith gauntlets",
            "Chaos gauntlets",
            "Book on Baxtorian",
            "Old key",
            "Large old key",
            "Glarial's pebble",
            "Glarial's amulet",
            "Glarial's urn",
            "A magic scroll",
            "Limpwurt root",
            "Ice arrows",
            "Lever",
            "Staff of armadyl",
            "Shiny key",
            "Pendant of lucien",
            "Armadyl pendant",
            "Boots of lightness",
            "Yew comp bow",
            "Magic comp bow",
            "Dark bow",
            "Holy table napkin",
            "Magic whistle",
            "Grail bell",
            "Magic gold feather",
            "Holy grail",
            "Orb of protection",
            "Orbs of protection",
            "Gnome amulet",
            "Ransom note",
            "History of the Kharid-ib",
        ):
            self.assertIn(item_name, QUEST_ITEM_IMAGES)
            self.assertTrue(os.path.exists(QUEST_ITEM_IMAGES[item_name]))
            self.assertIn(item_name, by_storage_key)
            self.assertEqual(by_storage_key[item_name].asset_path, QUEST_ITEM_IMAGES[item_name])
            self.assertIsNotNone(by_storage_key[item_name].asset_path, f"{item_name} should have a quest-stage icon")
        with open(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets_provenance.json"),
            encoding="utf-8",
        ) as file_obj:
            provenance = json.load(file_obj)
        for asset_key in (
            "questitems/ransom_note.png",
            "questitems/history_of_the_kharid_ib.png",
        ):
            self.assertLess(provenance[asset_key]["timestamp"], "2012-11-20T00:00:00Z")
            self.assertIn("/archive/", provenance[asset_key]["image_url"])
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())

    def test_every_registry_item_declared_equippable_has_live_equipment_data(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for item_name, definition in by_storage_key.items():
            if definition.equipment_slot is None:
                continue
            with self.subTest(item_name=item_name):
                self.assertIn(item_name, EQUIPMENT_DATA)
                self.assertEqual(definition.equipment_slot, EQUIPMENT_DATA[item_name].slot)

        self.assertEqual(by_storage_key["Staff of armadyl"].category, "material")
        self.assertIsNone(by_storage_key["Staff of armadyl"].equipment_slot)

    def test_runecrafting_items_targets_and_assets_are_registered(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        self.assertEqual(len(RUNECRAFTING_DATA), 61)
        self.assertEqual(RUNECRAFTING_DATA["craft_air_runes"]["output_item"], "Air rune")
        self.assertEqual(RUNECRAFTING_DATA["combo_lava_at_earth"]["consumed_talisman"], "Fire talisman")
        self.assertEqual(RUNECRAFTING_POUCH_DATA["small"]["capacity"], 3)
        self.assertEqual(RUNECRAFTING_POUCH_DATA["giant"]["degradation_threshold"], 10)

        for item_name in (
            "Air rune",
            "Lava rune",
            "Air talisman",
            "Air tiara",
            "Small pouch",
            "Medium pouch (worn)",
            "Binding necklace",
            "Wicked hood",
        ):
            self.assertIn(item_name, by_storage_key)
            self.assertIn(item_name, RUNECRAFTING_ITEM_IMAGES)
            self.assertTrue(os.path.exists(RUNECRAFTING_ITEM_IMAGES[item_name]), f"{item_name} Runecrafting icon is missing")
            self.assertEqual(by_storage_key[item_name].asset_path, RUNECRAFTING_ITEM_IMAGES[item_name])

        self.assertEqual(by_storage_key["Air rune"].category, "runecrafting")
        self.assertEqual(by_storage_key["Binding necklace"].equipment_slot, "neck")
        self.assertEqual(by_storage_key["Wicked hood"].equipment_slot, "head")
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())

    def test_hunter_items_targets_and_assets_are_registered(self):
        by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        self.assertEqual(len(HUNTER_DATA), 59)
        self.assertEqual(
            HUNTER_DATA["barehand_ruby_harvest"]["xp_rewards"],
            ({"skill_id": "hunter", "amount": 300.0}, {"skill_id": "agility", "amount": 50.0}),
        )
        self.assertEqual(HUNTER_DATA["barehand_ruby_harvest"]["outputs"], {})
        self.assertEqual(HUNTER_DATA["catch_crimson_swift"]["outputs"]["Red feather"], 5)
        self.assertEqual(HUNTER_DATA["catch_crimson_swift"]["tools"], {"Bird snare": 1})
        self.assertEqual(HUNTER_DATA["catch_ferret"]["tools"], {"Box trap": 1})
        self.assertEqual(HUNTER_DATA["catch_swamp_lizard"]["tools"], {"Small fishing net": 1, "Rope": 1})
        self.assertEqual(HUNTER_DATA["catch_baby_impling_puro_puro"]["tools"], {"Butterfly net": 1})
        self.assertEqual(HUNTER_DATA["catch_baby_impling_world"]["tools"], {})
        self.assertEqual(HUNTER_DATA["catch_wild_kebbit"]["requirements"], {"Logs": 1})
        self.assertEqual(HUNTER_DATA["catch_imp_magic_box"]["output_item"], "Imp-in-a-box (2)")
        self.assertEqual(HUNTER_DATA["catch_gourmet_impling_world"]["output_item"], "Gourm' impling jar")
        self.assertEqual(HUNTER_DATA["catch_essence_impling_puro_puro"]["output_item"], "Ess' impling jar")

        for item_name in (
            "Red feather",
            "Stripy feather",
            "Kebbit claws",
            "Black salamander",
            "Imp-in-a-box (2)",
            "Gourm' impling jar",
            "Ess' impling jar",
            "Impling jar",
            "Butterfly jar",
            "Magic box",
            "Bird snare",
            "Box trap",
            "Butterfly net",
            "Small fishing net",
            "Rope",
            "Noose wand",
            "Teasing stick",
            "Rabbit snare",
        ):
            self.assertIn(item_name, by_storage_key)
            self.assertIn(item_name, HUNTER_ITEM_IMAGES)
            self.assertTrue(os.path.exists(HUNTER_ITEM_IMAGES[item_name]), f"{item_name} Hunter icon is missing")

        self.assertEqual(by_storage_key["Red feather"].category, "hunter")
        self.assertEqual(by_storage_key["Bird snare"].category, "tool")
        self.assertEqual(by_storage_key["Box trap"].category, "tool")
        self.assertEqual(by_storage_key["Impling jar"].category, "material")
        self.assertEqual(by_storage_key["Magic box"].category, "material")
        self.assertEqual(HUNTER_EXTRA_ITEM_DATA["Magic box"]["item_id"], 10025)
        self.assertEqual(HUNTER_EXTRA_ITEM_DATA["Bird snare"]["item_id"], 10006)

        iconless = sorted(
            item_name
            for item_name in HUNTER_OUTPUT_ITEMS
            if not (
                item_name in by_storage_key
                and by_storage_key[item_name].asset_path
            )
        )
        self.assertEqual(iconless, [], f"Hunter outputs missing icons: {iconless}")
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())


if __name__ == "__main__":
    unittest.main()
