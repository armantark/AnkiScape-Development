import unittest

from constants import (
    BAR_DATA,
    CRAFTING_DATA,
    FLETCHING_DATA,
    GEM_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    TREE_DATA,
    UTILITY_ACTIVITY_DATA,
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
            ("Mining", "Woodcutting", "Smithing", "Crafting", "Fletching"),
        )
        self.assertTrue(is_review_skill("Mining"))
        self.assertTrue(is_review_skill("woodcutting"))
        self.assertTrue(is_review_skill("Fletching"))
        self.assertEqual(review_handler_key("Fletching"), "fletching")
        self.assertEqual([skill.display_name for skill in CURRENT_SKILLS], list(implemented_review_skill_names()))

    def test_planned_catalog_contains_2011_era_targets_without_enabling_them(self):
        planned = {skill.id: skill for skill in planned_skill_definitions()}
        for skill_id in [
            "attack",
            "constitution",
            "magic",
            "summoning",
            "farming",
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

    def test_registry_generates_current_flat_save_defaults(self):
        self.assertEqual(
            default_skill_state(),
            {
                "mining_level": 1,
                "mining_exp": 0,
                "woodcutting_level": 1,
                "woodcutting_exp": 0,
                "smithing_level": 1,
                "smithing_exp": 0,
                "crafting_level": 1,
                "crafting_exp": 0,
                "fletching_level": 1,
                "fletching_exp": 0,
            },
        )
        self.assertEqual(
            default_target_state(),
            {
                "current_ore": "Rune essence",
                "current_tree": "Tree",
                "current_bar": "Bronze bar",
                "current_craft": "",
                "current_fletch": "arrow_shafts",
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
            if material not in TREE_DATA
        ]
        utility_outputs = [spec["output_item"] for spec in UTILITY_ACTIVITY_DATA.values()]
        utility_materials = [
            material
            for spec in UTILITY_ACTIVITY_DATA.values()
            for material in spec.get("requirements", {})
            if material not in ORE_DATA
        ]
        for item_name in (
            list(ORE_DATA)
            + list(TREE_DATA)
            + list(GEM_DATA)
            + list(BAR_DATA)
            + list(CRAFTING_DATA)
            + fletching_outputs
            + fletching_materials
            + utility_outputs
            + utility_materials
        ):
            self.assertIn(item_name, by_storage_key)

        by_id = item_definitions_by_id(ITEM_DEFINITIONS)
        self.assertEqual(len(by_id), len(ITEM_DEFINITIONS))
        self.assertEqual(set(item_storage_keys_by_category(ITEM_DEFINITIONS, "ore")), set(ORE_DATA))
        self.assertEqual(set(item_storage_keys_by_category(ITEM_DEFINITIONS, "log")), set(TREE_DATA))
        self.assertEqual(set(item_storage_keys_by_category(ITEM_DEFINITIONS, "bar")), set(BAR_DATA))
        self.assertIn("Arrow shafts", item_storage_keys_by_category(ITEM_DEFINITIONS, "fletched"))
        self.assertIn("Soft clay", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertIn("Wool", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))
        self.assertIn("Flax", item_storage_keys_by_category(ITEM_DEFINITIONS, "material"))

    def test_crafting_pilot_data_matches_utility_split(self):
        self.assertNotIn("Soft clay", CRAFTING_DATA)
        self.assertEqual(UTILITY_ACTIVITY_DATA["make_soft_clay"]["requirements"], {"Clay": 1})
        self.assertEqual(UTILITY_ACTIVITY_DATA["make_soft_clay"]["batch_size"], 28)
        self.assertEqual(CRAFTING_DATA["Unfired pot"]["requirements"], {"Soft clay": 1})
        self.assertEqual(CRAFTING_DATA["Pot"]["requirements"], {"Unfired pot": 1})
        self.assertEqual(CRAFTING_DATA["Pie dish"]["level"], 7)
        self.assertEqual(CRAFTING_DATA["Bowl"]["level"], 8)
        self.assertEqual(CRAFTING_DATA["Ball of wool"]["exp"], 2.5)
        self.assertEqual(CRAFTING_DATA["Bow string"]["batch_size"], 28)
        self.assertEqual(CRAFTING_DATA["Silver bolts (unf)"]["output_qty"], 10)

    def test_registered_asset_paths_exist_for_current_manifest(self):
        self.assertEqual(missing_required_asset_paths(ITEM_DEFINITIONS), ())


if __name__ == "__main__":
    unittest.main()
