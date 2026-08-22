import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import HERBLORE_DATA, HUNTER_DATA
from ankiscape.logic.farming_logic import (
    advance_farm_clock_pure,
    default_farming_state_pure,
    execute_farm_field_step_pure,
)
from ankiscape.logic_pure.logic_pure import (
    apply_herblore_action_pure,
    apply_hunter_action_pure,
    can_herblore_target_pure,
)


class TestHabitatHerbChain(unittest.TestCase):
    def test_each_common_jadinko_seed_reaches_an_unfinished_potion(self):
        cases = (
            ("erzille", "Erzille", 0.0, 54, 10.0),
            ("ugune", "Ugune", 0.2, 56, 11.5),
            ("argway", "Argway", 0.4, 57, 11.6),
            ("shengo", "Shengo", 0.6, 58, 11.7),
            ("samaden", "Samaden", 0.8, 59, 11.7),
        )

        for crop_id, herb_name, seed_roll, herblore_level, cleaning_xp in cases:
            with self.subTest(herb=herb_name):
                inventory, hunter_xp, caught, primary_output, _rewards = (
                    apply_hunter_action_pure(
                        "catch_common_jadinko",
                        {"Marasamaw plant": 1},
                        HUNTER_DATA,
                        70,
                        0.0,
                        r_secondary_rolls=(
                            (1.0, 0.0),
                            (0.0, seed_roll),
                            (1.0, 0.0),
                        ),
                    )
                )
                seed_item = f"{herb_name} seed"
                grimy_herb = f"Grimy {herb_name.lower()}"
                clean_herb = f"Clean {herb_name.lower()}"
                unfinished_potion = f"{herb_name} potion (unf)"
                self.assertTrue(caught)
                self.assertEqual(hunter_xp, 350.0)
                self.assertEqual(primary_output, "Withered vine")
                self.assertEqual(inventory[seed_item], 1)

                state = {
                    "inventory": {
                        **inventory,
                        "Rake": 1,
                        "Seed dibber": 1,
                        "Spade": 1,
                        "Vial of water": 1,
                    },
                    "farming_level": 99,
                    "farming_exp": 0.0,
                    "agility_level": 99,
                }
                state.update(default_farming_state_pure())
                state, planted, plant_info = execute_farm_field_step_pure(
                    state,
                    {
                        "kind": "plant",
                        "patch_id": "habitat_vine_herb_east",
                        "crop_id": crop_id,
                    },
                )
                self.assertTrue(planted, plant_info)
                self.assertEqual(state["inventory"][seed_item], 0)

                state, clock_info = advance_farm_clock_pure(
                    state,
                    14,
                    lambda: 1.0,
                )
                self.assertEqual(clock_info["minutes"], 84)
                state, harvested, harvest_info = execute_farm_field_step_pure(
                    state,
                    {
                        "kind": "harvest",
                        "patch_id": "habitat_vine_herb_east",
                    },
                    lambda: 1.0,
                )
                self.assertTrue(harvested, harvest_info)
                self.assertEqual(harvest_info["outputs"], {grimy_herb: 3})

                clean_target = f"clean_{crop_id}"
                self.assertFalse(
                    can_herblore_target_pure(
                        herblore_level - 1,
                        state["inventory"],
                        clean_target,
                        HERBLORE_DATA,
                    )
                )
                self.assertTrue(
                    can_herblore_target_pure(
                        herblore_level,
                        state["inventory"],
                        clean_target,
                        HERBLORE_DATA,
                    )
                )
                inventory, clean_xp, cleaned = apply_herblore_action_pure(
                    clean_target,
                    state["inventory"],
                    HERBLORE_DATA,
                )
                self.assertTrue(cleaned)
                self.assertEqual(clean_xp, cleaning_xp)
                self.assertEqual(inventory[grimy_herb], 2)
                self.assertEqual(inventory[clean_herb], 1)

                unfinished_target = f"unf_{crop_id}"
                self.assertFalse(
                    can_herblore_target_pure(
                        herblore_level - 1,
                        inventory,
                        unfinished_target,
                        HERBLORE_DATA,
                    )
                )
                self.assertTrue(
                    can_herblore_target_pure(
                        herblore_level,
                        inventory,
                        unfinished_target,
                        HERBLORE_DATA,
                    )
                )
                inventory, unfinished_xp, mixed = apply_herblore_action_pure(
                    unfinished_target,
                    inventory,
                    HERBLORE_DATA,
                )
                self.assertTrue(mixed)
                self.assertEqual(unfinished_xp, 0.0)
                self.assertEqual(inventory[clean_herb], 0)
                self.assertEqual(inventory["Vial of water"], 0)
                self.assertEqual(inventory[unfinished_potion], 1)


if __name__ == "__main__":
    unittest.main()
