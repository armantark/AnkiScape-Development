import unittest

from equipment_data import EQUIPMENT_DATA, EQUIPMENT_SLOTS, equipment_items_as_dict


class TestEquipmentData(unittest.TestCase):
    def test_generated_equipment_contract_shape(self):
        self.assertEqual(len(EQUIPMENT_SLOTS), 11)
        self.assertEqual([slot.id for slot in EQUIPMENT_SLOTS], [
            "head",
            "cape",
            "neck",
            "ammunition",
            "weapon",
            "body",
            "shield",
            "legs",
            "hands",
            "feet",
            "ring",
        ])
        self.assertEqual(len(EQUIPMENT_DATA), 117)
        self.assertEqual(set(equipment_items_as_dict()), set(EQUIPMENT_DATA))

    def test_smithed_armour_and_weapon_requirements(self):
        self.assertEqual(EQUIPMENT_DATA["Bronze platebody"].slot, "body")
        self.assertEqual(EQUIPMENT_DATA["Bronze platebody"].combat_skill, "defense")
        self.assertEqual(EQUIPMENT_DATA["Bronze platebody"].required_level, 1)
        self.assertGreater(EQUIPMENT_DATA["Bronze platebody"].bonuses.defence_stab, 0)

        self.assertEqual(EQUIPMENT_DATA["Rune platebody"].combat_skill, "defense")
        self.assertEqual(EQUIPMENT_DATA["Rune platebody"].required_level, 40)
        self.assertGreater(EQUIPMENT_DATA["Rune platebody"].bonuses.defence_slash, 0)

        self.assertEqual(EQUIPMENT_DATA["Rune 2h sword"].slot, "weapon")
        self.assertEqual(EQUIPMENT_DATA["Rune 2h sword"].combat_skill, "attack")
        self.assertEqual(EQUIPMENT_DATA["Rune 2h sword"].required_level, 40)
        self.assertTrue(EQUIPMENT_DATA["Rune 2h sword"].two_handed)

    def test_throwing_knives_are_ranged_weapons(self):
        bronze_knife = EQUIPMENT_DATA["Bronze knife"]
        self.assertEqual(bronze_knife.slot, "weapon")
        self.assertEqual(bronze_knife.combat_skill, "ranged")
        self.assertEqual(bronze_knife.required_level, 1)
        self.assertGreater(bronze_knife.bonuses.attack_ranged, 0)

    def test_components_and_gathering_tools_are_excluded(self):
        for item_name in (
            "Bronze pickaxe",
            "Bronze hatchet",
            "Bronze arrowtips",
            "Bronze bolts (unf)",
            "Bronze limbs",
            "Steel studs",
        ):
            self.assertNotIn(item_name, EQUIPMENT_DATA)

    def test_mining_bonus_items_are_equipment_with_combat_bonuses(self):
        glory = EQUIPMENT_DATA["Amulet of glory (4)"]
        self.assertEqual(glory.slot, "neck")
        self.assertIsNone(glory.combat_skill)
        self.assertEqual(glory.required_level, 1)
        self.assertEqual(glory.equipment_type, "gem_chance")
        self.assertGreater(glory.bonuses.attack_stab, 0)

        varrock = EQUIPMENT_DATA["Varrock armour 1"]
        self.assertEqual(varrock.slot, "body")
        self.assertIsNone(varrock.combat_skill)
        self.assertEqual(varrock.equipment_type, "extra_ore")
        self.assertGreater(varrock.bonuses.defence_stab, 0)


if __name__ == "__main__":
    unittest.main()
