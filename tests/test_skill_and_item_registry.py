import os
import unittest

from action_registry import (
    is_review_action,
    is_utility_review_action,
    review_action_display_names,
    review_action_handler_key,
)
from constants import (
    BAR_DATA,
    CRAFTING_DATA,
    FIREMAKING_DATA,
    FIREMAKING_ITEM_IMAGES,
    FIREMAKING_LOG_ITEMS,
    FIREMAKING_OUTPUT_ITEMS,
    FISHING_DATA,
    FISHING_ITEM_IMAGES,
    FISHING_OUTPUT_ITEMS,
    FLETCHING_DATA,
    GEM_DATA,
    ITEM_DEFINITIONS,
    MINING_BONUS_ITEM_DATA,
    MINING_OUTPUT_ITEMS,
    MINING_PICKAXE_DATA,
    ORE_DATA,
    SMITHING_OUTPUT_ITEMS,
    UTILITY_ACTIVITY_DATA,
    WOODCUTTING_AXE_DATA,
    WOODCUTTING_LOG_ITEMS,
)
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
    review_handler_key,
)


class TestSkillAndItemRegistry(unittest.TestCase):
    def test_current_skills_preserve_existing_display_contract(self):
        self.assertEqual(
            implemented_review_skill_names(),
            ("Mining", "Woodcutting", "Fishing", "Smithing", "Crafting", "Fletching", "Firemaking"),
        )
        self.assertTrue(is_review_skill("Mining"))
        self.assertTrue(is_review_skill("woodcutting"))
        self.assertTrue(is_review_skill("Fishing"))
        self.assertTrue(is_review_skill("Fletching"))
        self.assertTrue(is_review_skill("Firemaking"))
        self.assertEqual(review_handler_key("Fishing"), "fishing")
        self.assertEqual(review_handler_key("Fletching"), "fletching")
        self.assertEqual(review_handler_key("Firemaking"), "firemaking")
        self.assertEqual([skill.display_name for skill in CURRENT_SKILLS], list(implemented_review_skill_names()))

    def test_review_action_registry_includes_utility_without_making_it_a_skill(self):
        self.assertFalse(is_review_skill("Utility / Activities"))
        self.assertTrue(is_review_action("Utility / Activities"))
        self.assertTrue(is_utility_review_action("Utility"))
        self.assertEqual(review_action_handler_key("Utility / Activities"), "utility")
        self.assertEqual(review_action_handler_key("Fishing"), "fishing")
        self.assertEqual(review_action_handler_key("Fletching"), "fletching")
        self.assertEqual(review_action_handler_key("Firemaking"), "firemaking")
        self.assertIsNone(review_action_handler_key("Thieving"))
        self.assertEqual(
            review_action_display_names(),
            ("Mining", "Woodcutting", "Fishing", "Smithing", "Crafting", "Fletching", "Firemaking", "Utility / Activities"),
        )

    def test_planned_catalog_contains_2011_era_targets_without_enabling_them(self):
        planned = {skill.id: skill for skill in planned_skill_definitions()}
        for skill_id in [
            "attack",
            "constitution",
            "magic",
            "summoning",
            "farming",
            "hunter",
            "dungeoneering",
            "slayer",
            "thieving",
        ]:
            self.assertIn(skill_id, planned)
            self.assertFalse(planned[skill_id].implemented)
            self.assertFalse(planned[skill_id].participates_in_review)
        self.assertEqual(len({skill.id for skill in ALL_SKILLS}), len(ALL_SKILLS))

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

    def test_registry_generates_current_flat_save_defaults(self):
        self.assertEqual(
            default_skill_state(),
            {
                "mining_level": 1,
                "mining_exp": 0,
                "woodcutting_level": 1,
                "woodcutting_exp": 0,
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
        utility_materials = [
            material
            for spec in UTILITY_ACTIVITY_DATA.values()
            for material in spec.get("requirements", {})
            if material not in MINING_OUTPUT_ITEMS
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
            + utility_outputs
            + utility_materials
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
        self.assertFalse(by_storage_key["Blurite ore"].tradeable)
        self.assertFalse(by_storage_key["Cursed magic logs"].tradeable)
        self.assertTrue(by_storage_key["Dragon pickaxe"].tradeable)
        self.assertFalse(by_storage_key["Inferno adze"].tradeable)
        self.assertFalse(by_storage_key["Varrock armour 4"].tradeable)
        self.assertEqual(by_storage_key["Varrock armour 4"].equipment_slot, "body")
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

    def test_utility_activities_have_purpose_built_icon_contract(self):
        expected_files = {
            "make_soft_clay": "make_soft_clay.png",
            "gather_wool": "gather_wool.png",
            "gather_flax": "gather_flax.png",
            "scavenge_chicken_feathers": "scavenge_chicken_feathers.png",
            "gather_fishing_bait": "gather_fishing_bait.png",
            "open_bird_nest": "open_bird_nest.png",
        }
        self.assertEqual(set(UTILITY_ACTIVITY_DATA), set(expected_files))
        for activity_key, file_name in expected_files.items():
            icon_path = UTILITY_ACTIVITY_DATA[activity_key].get("icon_path")
            self.assertIsInstance(icon_path, str, activity_key)
            self.assertEqual(os.path.basename(icon_path), file_name)
            self.assertEqual(os.path.basename(os.path.dirname(icon_path)), "activityicons")
            self.assertTrue(os.path.exists(icon_path), f"{activity_key} icon path is missing")
        feather_source = UTILITY_ACTIVITY_DATA["scavenge_chicken_feathers"]["source"]
        self.assertIn("ranged_instructor.plugin.kts", feather_source)
        self.assertIn("chicken_level_1.plugin.kts", feather_source)
        bait_source = UTILITY_ACTIVITY_DATA["gather_fishing_bait"]["source"]
        self.assertIn("lumbridge_fishing_supplies.plugin.kts", bait_source)

    def test_registered_asset_paths_exist_for_current_manifest(self):
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())

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
        for name in ("Bronze pickaxe", "Rune pickaxe", "Dragon pickaxe"):
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


if __name__ == "__main__":
    unittest.main()
