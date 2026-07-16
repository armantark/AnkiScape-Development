import unittest

from herblore_data import (
    CLEAN_TARGETS,
    DUNGEONEERING_CLEAN_TARGETS,
    DUNGEONEERING_FINISHED_TARGETS,
    DUNGEONEERING_HERBLORE_TARGETS,
    DUNGEONEERING_UNF_TARGETS,
    FINISHED_TARGETS,
    HERBLORE_TARGETS,
    UNF_TARGETS,
    herblore_extra_items_as_dict,
    herblore_targets_as_dict,
)
from logic_pure import apply_herblore_action_pure, can_herblore_target_pure


class HerbloreDataTests(unittest.TestCase):
    def test_magic_essence_mix_preserves_its_distinct_item_identity(self):
        target = next(target for target in FINISHED_TARGETS if target.id == "finished_magic_essence_mix")
        self.assertEqual(target.display_name, "Magic essence mix (2)")
        self.assertEqual(target.output_item, "Magic essence mix (2)")
        self.assertEqual(target.requirements, (("Magic essence (2)", 1), ("Caviar", 1)))
        self.assertEqual(herblore_extra_items_as_dict()["Magic essence mix (2)"]["item_id"], 11489)

    def test_daemonheim_target_family_is_not_in_overworld_catalog(self):
        herb_ids = {
            "sagawort",
            "featherfoil",
            "valerian",
            "aloe",
            "wormwood",
            "magebane",
            "winter_grip",
            "lycopus",
            "buckthorn",
        }
        self.assertEqual(
            {target.id.removeprefix("clean_") for target in DUNGEONEERING_CLEAN_TARGETS},
            herb_ids,
        )
        self.assertEqual(
            {target.id.removeprefix("unf_") for target in DUNGEONEERING_UNF_TARGETS},
            herb_ids,
        )
        self.assertEqual(len(DUNGEONEERING_CLEAN_TARGETS), 9)
        self.assertEqual(len(DUNGEONEERING_UNF_TARGETS), 9)
        self.assertEqual(len(DUNGEONEERING_FINISHED_TARGETS), 36)
        self.assertEqual(len(DUNGEONEERING_HERBLORE_TARGETS), 54)

        deferred_ids = {target.id for target in DUNGEONEERING_HERBLORE_TARGETS}
        active_ids = {target.id for target in HERBLORE_TARGETS}
        self.assertTrue(deferred_ids.isdisjoint(active_ids))
        self.assertTrue(all(target.subgroup != "dungeoneering" for target in HERBLORE_TARGETS))
        self.assertTrue(deferred_ids.isdisjoint(herblore_targets_as_dict()))

        self.assertEqual(len(CLEAN_TARGETS), 22)
        self.assertEqual(len(UNF_TARGETS), 22)
        self.assertEqual(len(FINISHED_TARGETS), 69)

    def test_daemonheim_item_identities_remain_registered_for_old_saves(self):
        registered_items = herblore_extra_items_as_dict()
        deferred_items = {
            item_name
            for target in DUNGEONEERING_HERBLORE_TARGETS
            for item_name in (
                target.output_item,
                *(name for name, _quantity in target.requirements),
                *(name for name, _quantity in target.byproducts),
            )
        }

        self.assertTrue(deferred_items)
        self.assertTrue(deferred_items.issubset(registered_items))
        self.assertIn("Grimy sagewort", registered_items)
        self.assertIn("Strong survivalist's potion", registered_items)

    def test_daemonheim_recipe_cannot_run_through_overworld_pure_logic(self):
        active_data = herblore_targets_as_dict()
        inventory = {"Grimy sagewort": 1}

        self.assertFalse(can_herblore_target_pure(99, inventory, "clean_sagawort", active_data))
        result, exp, ok = apply_herblore_action_pure("clean_sagawort", inventory, active_data)
        self.assertFalse(ok)
        self.assertEqual(exp, 0)
        self.assertIs(result, inventory)


if __name__ == "__main__":
    unittest.main()
