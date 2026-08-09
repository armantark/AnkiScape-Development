import unittest

import pkg_alias  # noqa: F401

from ankiscape.core.constants import COOKING_DATA, EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from ankiscape.logic.cooking_gauntlets_logic import (
    apply_family_gauntlet_conversion_pure,
    cooking_equipment_choice_pure,
    cooking_gauntlets_worn_pure,
    family_gauntlet_recovery_state_pure,
    recover_family_gauntlets_pure,
    reconcile_cooking_equipment_pure,
    set_cooking_equipment_choice_pure,
)
from ankiscape.logic_pure.logic_pure import (
    apply_cooking_action_pure,
    cooking_source_roll_chance_pure,
)


class CookingGauntletDataTests(unittest.TestCase):
    def test_period_no_burn_thresholds_are_exact(self):
        self.assertEqual(
            {
                target_id: COOKING_DATA[target_id]["cooking_gauntlet_no_burn_level"]
                for target_id in (
                    "cook_tuna",
                    "cook_trout",
                    "cook_lobster",
                    "cook_swordfish",
                    "cook_monkfish",
                    "cook_shark",
                    "cook_cavefish",
                    "cook_rocktail",
                )
            },
            {
                "cook_tuna": 63,
                "cook_trout": 50,
                "cook_lobster": 68,
                "cook_swordfish": 81,
                "cook_monkfish": 87,
                "cook_shark": 94,
                "cook_cavefish": 94,
                "cook_rocktail": 94,
            },
        )

    def test_gauntlets_guarantee_threshold_but_not_the_level_below(self):
        shark = COOKING_DATA["cook_shark"]
        self.assertLess(
            cooking_source_roll_chance_pure(
                93, shark, has_cooking_gauntlets=True
            ),
            1.0,
        )
        self.assertEqual(
            cooking_source_roll_chance_pure(
                94, shark, has_cooking_gauntlets=True
            ),
            1.0,
        )

    def test_gauntlets_never_reduce_an_already_better_ordinary_chance(self):
        trout = COOKING_DATA["cook_trout"]
        self.assertEqual(
            cooking_source_roll_chance_pure(
                49, trout, has_cooking_gauntlets=True
            ),
            cooking_source_roll_chance_pure(49, trout),
        )

    def test_action_uses_the_worn_gauntlet_modifier(self):
        shark = COOKING_DATA["cook_shark"]
        roll = 0.999
        plain, xp, processed, output, burned = apply_cooking_action_pure(
            "cook_shark",
            {"Raw shark": 1},
            COOKING_DATA,
            94,
            roll,
            use_source_probability=True,
        )
        self.assertTrue(processed)
        self.assertTrue(burned)
        self.assertEqual(xp, 0)
        self.assertEqual(output, "Burnt shark")
        self.assertEqual(plain["Burnt shark"], 1)

        protected, xp, processed, output, burned = apply_cooking_action_pure(
            "cook_shark",
            {"Raw shark": 1},
            COOKING_DATA,
            94,
            roll,
            use_source_probability=True,
            has_cooking_gauntlets=True,
        )
        self.assertTrue(processed)
        self.assertFalse(burned)
        self.assertEqual(xp, shark["exp"])
        self.assertEqual(output, "Shark")
        self.assertEqual(protected["Shark"], 1)

    def test_all_family_crest_gauntlets_are_registered_equipment(self):
        for item_name, item_id in (
            ("Cooking gauntlets", 775),
            ("Goldsmith gauntlets", 776),
            ("Chaos gauntlets", 777),
            ("Family gauntlets", 778),
        ):
            self.assertEqual(EQUIPMENT_DATA[item_name].slot, "hands")
            self.assertEqual(EQUIPMENT_DATA[item_name].source_item_id, item_id)
            self.assertEqual(EQUIPMENT_DATA[item_name].bonuses.defence_slash, 9)
            self.assertEqual(EQUIPMENT_DATA[item_name].bonuses.melee_strength, 2)


class CookingGauntletLifecycleTests(unittest.TestCase):
    def _player(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        data["quests"]["family_crest"] = {
            "started": True,
            "progress": 16,
            "completed": True,
        }
        return data

    def test_family_conversion_is_free_and_reenchantment_costs_25000(self):
        data = self._player()
        data["inventory"]["Family gauntlets"] = 1
        converted, ok, _message = apply_family_gauntlet_conversion_pure(
            data, "Family gauntlets"
        )
        self.assertTrue(ok)
        self.assertEqual(converted["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(converted["inventory"]["Coins"], data["inventory"]["Coins"])
        self.assertEqual(converted["family_gauntlet_enchantment"], "cooking")

        data = self._player()
        data["inventory"].update({"Goldsmith gauntlets": 1, "Coins": 25_000})
        converted, ok, _message = apply_family_gauntlet_conversion_pure(
            data, "Goldsmith gauntlets"
        )
        self.assertTrue(ok)
        self.assertEqual(converted["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(converted["inventory"]["Coins"], 0)

    def test_reenchantment_refuses_without_payment(self):
        data = self._player()
        data["inventory"].update({"Chaos gauntlets": 1, "Coins": 24_999})
        unchanged, ok, message = apply_family_gauntlet_conversion_pure(
            data, "Chaos gauntlets"
        )
        self.assertFalse(ok)
        self.assertIn("25,000", message)
        self.assertEqual(unchanged["inventory"]["Chaos gauntlets"], 1)

    def test_lost_pair_is_recovered_in_its_remembered_enchantment(self):
        data = self._player()
        data["family_gauntlet_enchantment"] = "cooking"
        state = family_gauntlet_recovery_state_pure(data)
        self.assertTrue(state["enabled"])
        recovered, ok, _message = recover_family_gauntlets_pure(data)
        self.assertTrue(ok)
        self.assertEqual(recovered["inventory"]["Cooking gauntlets"], 1)

        duplicate, ok, _message = recover_family_gauntlets_pure(recovered)
        self.assertFalse(ok)
        self.assertEqual(duplicate["inventory"]["Cooking gauntlets"], 1)

    def test_target_policy_equips_displaces_and_restores_only_its_own_swap(self):
        data = self._player()
        data["inventory"]["Cooking gauntlets"] = 1
        data["equipment"]["hands"] = "Leather gloves"
        equipped = reconcile_cooking_equipment_pure(
            data, "cook_shark", beneficial=True
        )
        self.assertTrue(cooking_gauntlets_worn_pure(equipped))
        self.assertEqual(equipped["inventory"]["Leather gloves"], 1)
        self.assertEqual(
            equipped["cooking_equipment_swap"]["displaced_item"],
            "Leather gloves",
        )

        restored = reconcile_cooking_equipment_pure(
            equipped, "cook_bass", beneficial=False
        )
        self.assertEqual(restored["equipment"]["hands"], "Leather gloves")
        self.assertEqual(restored["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(restored["cooking_equipment_swap"], {})

    def test_advanced_none_does_not_unequip_manually_worn_gauntlets(self):
        data = self._player()
        data["equipment"]["hands"] = "Cooking gauntlets"
        data, ok = set_cooking_equipment_choice_pure(
            data, "cook_shark", "none"
        )
        self.assertTrue(ok)
        self.assertEqual(cooking_equipment_choice_pure(data, "cook_shark"), "none")
        reconciled = reconcile_cooking_equipment_pure(
            data, "cook_shark", beneficial=True
        )
        self.assertEqual(reconciled["equipment"]["hands"], "Cooking gauntlets")
        self.assertEqual(reconciled["cooking_equipment_swap"], {})

    def test_migration_infers_remembered_enchantment_from_owned_pair(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        data["config_version"] = CURRENT_CONFIG_VERSION - 1
        data.pop("family_gauntlet_enchantment", None)
        data["inventory"]["Goldsmith gauntlets"] = 1
        migrated = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["family_gauntlet_enchantment"], "goldsmith")

    def test_migration_repairs_completed_quest_with_no_surviving_pair(self):
        data = self._player()
        data["config_version"] = CURRENT_CONFIG_VERSION - 1
        data.pop("family_gauntlet_enchantment", None)
        migrated = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["family_gauntlet_enchantment"], "family")
        self.assertTrue(family_gauntlet_recovery_state_pure(migrated)["enabled"])


if __name__ == "__main__":
    unittest.main()
