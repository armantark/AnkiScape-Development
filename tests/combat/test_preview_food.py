from copy import deepcopy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
import ankiscape.logic_pure.logic_pure as combat_facade
import ankiscape.logic_pure.logic_pure_combat_engine as combat_engine
import ankiscape.logic_pure.logic_pure_combat_food as combat_food
import ankiscape.logic_pure.logic_pure_combat_model as combat_model
import ankiscape.logic_pure.logic_pure_combat_supplies as combat_supplies
import ankiscape.logic_pure.logic_pure_consumables as combat_consumables
import ankiscape.logic_pure.logic_pure_thieving as combat_thieving
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.logic_pure.logic_pure_combat_engine import (
    combat_target_preview_pure,
)
from ankiscape.logic_pure.logic_pure_combat_food import (
    _combat_preview_food_available,
)
from tests.test_combat_logic import _player


def preview_food_player(**overrides):
    values = dict(
        constitution_level=1,
        combat_lifepoints=1,
        combat_auto_eat_food=["Shrimps"],
    )
    values.update(overrides)
    return _player(**values)


class PreviewFoodAvailabilityTest(unittest.TestCase):
    def test_baseline_food_reexports_keep_identity_and_default_order(self):
        default_order = (
            "Shark",
            "Monkfish",
            "Swordfish",
            "Bass",
            "Lobster",
            "Tuna",
            "Salmon",
            "Pike",
            "Trout",
            "Cod",
            "Mackerel",
            "Herring",
            "Cooked meat",
            "Cooked chicken",
            "Sardine",
            "Shrimps",
            "Crayfish",
        )
        model_exports = (
            combat_facade,
            combat_engine,
            combat_model,
            combat_supplies,
            combat_consumables,
            combat_thieving,
        )
        supply_exports = (
            combat_facade,
            combat_engine,
            combat_supplies,
            combat_consumables,
        )

        self.assertEqual(combat_food._DEFAULT_COMBAT_AUTO_EAT_FOOD, default_order)
        for module in model_exports:
            self.assertIs(
                module._DEFAULT_COMBAT_AUTO_EAT_FOOD,
                combat_food._DEFAULT_COMBAT_AUTO_EAT_FOOD,
            )
            self.assertIs(
                module._combat_consume_auto_food,
                combat_food._combat_consume_auto_food,
            )
        for module in supply_exports:
            self.assertIs(
                module._combat_loaded_food_count,
                combat_food._combat_loaded_food_count,
            )
            self.assertIs(
                module._combat_banked_auto_food_count,
                combat_food._combat_banked_auto_food_count,
            )
            self.assertIs(
                module._combat_auto_eat_food_available,
                combat_food._combat_auto_eat_food_available,
            )
        self.assertIs(
            combat_engine._combat_preview_food_available,
            _combat_preview_food_available,
        )
        self.assertFalse(
            hasattr(combat_supplies, "_combat_preview_food_available")
        )

    def test_missing_empty_and_none_food_selections_remain_distinct(self):
        self.assertTrue(
            _combat_preview_food_available(
                {"inventory": {"Shrimps": 1}}, False
            )
        )
        self.assertFalse(
            _combat_preview_food_available(
                {
                    "combat_auto_eat_food": [],
                    "inventory": {"Shrimps": 1},
                },
                False,
            )
        )
        with self.assertRaises(TypeError):
            _combat_preview_food_available(
                {
                    "combat_auto_eat_food": None,
                    "inventory": {"Shrimps": 1},
                },
                False,
            )

    def test_catalog_counts_and_encounter_bank_gate_remain_exact(self):
        player = {
            "combat_auto_eat_food": ["Burnt fish", "Shrimps"],
            "combat_supply_loadout": {
                "food": {"Burnt fish": 10, "Shrimps": -1}
            },
            "inventory": {"Burnt fish": 10, "Shrimps": 1},
        }

        self.assertTrue(_combat_preview_food_available(player, False))
        self.assertFalse(_combat_preview_food_available(player, True))
        player["combat_supply_loadout"]["food"]["Shrimps"] = 1
        self.assertTrue(_combat_preview_food_available(player, True))

    def test_invalid_inputs_and_per_item_short_circuit_remain_exact(self):
        invalid_inventory = {
            "combat_auto_eat_food": ["Shrimps"],
            "inventory": "truthy invalid inventory",
        }
        with self.assertRaises(AttributeError):
            _combat_preview_food_available(invalid_inventory, False)
        self.assertFalse(
            _combat_preview_food_available(invalid_inventory, True)
        )

        with self.assertRaises(TypeError):
            _combat_preview_food_available(
                {"combat_auto_eat_food": ["Shrimps", []]}, False
            )
        self.assertTrue(
            _combat_preview_food_available(
                {
                    "combat_auto_eat_food": ["Shrimps", []],
                    "inventory": {"Shrimps": 1},
                },
                False,
            )
        )

    def test_preview_uses_loadout_during_an_active_encounter(self):
        player = preview_food_player(
            inventory={"Shrimps": 1},
        )
        supplied = deepcopy(player)

        ready = combat_target_preview_pure(
            player, "giant_rat", COMBAT_ENEMY_DATA, EQUIPMENT_DATA
        )
        active = combat_target_preview_pure(
            {
                **player,
                "combat_encounter": {"target_id": "giant_rat"},
            },
            "giant_rat",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )
        loaded = combat_target_preview_pure(
            {
                **player,
                "combat_encounter": {"target_id": "giant_rat"},
                "combat_supply_loadout": {"food": {"Shrimps": 1}},
            },
            "giant_rat",
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
        )

        self.assertEqual(ready["risk_band"], "Food advised")
        self.assertEqual(active["risk_band"], "Death possible")
        self.assertEqual(active["state"], "Fighting")
        self.assertEqual(loaded["risk_band"], "Food advised")
        self.assertEqual(player, supplied)


if __name__ == "__main__":
    unittest.main()
