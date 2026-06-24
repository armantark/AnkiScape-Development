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
        self.assertEqual(len(EQUIPMENT_DATA), 154)
        self.assertEqual(set(equipment_items_as_dict()), set(EQUIPMENT_DATA))
        self.assertEqual(EQUIPMENT_DATA["Cape"].slot, "cape")
        self.assertEqual(EQUIPMENT_DATA["Cape"].bonuses.defence_ranged, 2)
        self.assertEqual(EQUIPMENT_DATA["Air tiara"].slot, "head")
        self.assertEqual(EQUIPMENT_DATA["Wicked hood"].slot, "head")
        self.assertEqual(EQUIPMENT_DATA["Binding necklace"].slot, "neck")

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

    def test_standard_bows_are_ranged_weapons(self):
        bronze_knife = EQUIPMENT_DATA["Bronze knife"]
        self.assertEqual(bronze_knife.slot, "weapon")
        self.assertEqual(bronze_knife.combat_skill, "ranged")
        self.assertEqual(bronze_knife.required_level, 1)
        self.assertGreater(bronze_knife.bonuses.attack_ranged, 0)

        expected_bows = {
            "Shortbow": (841, "shortbow", 1, 4, 8),
            "Longbow": (839, "longbow", 1, 6, 8),
            "Oak shortbow": (843, "oak_shortbow", 5, 4, 14),
            "Oak longbow": (845, "oak_longbow", 5, 6, 14),
            "Willow shortbow": (849, "willow_shortbow", 20, 4, 20),
            "Willow longbow": (847, "willow_longbow", 20, 6, 20),
            "Maple shortbow": (853, "maple_shortbow", 30, 4, 29),
            "Maple longbow": (851, "maple_longbow", 30, 6, 29),
            "Yew shortbow": (857, "yew_shortbow", 40, 4, 47),
            "Yew longbow": (855, "yew_longbow", 40, 6, 47),
            "Magic shortbow": (861, "magic_shortbow", 50, 4, 69),
            "Magic longbow": (859, "magic_longbow", 50, 6, 69),
        }
        for item_name, (source_item_id, equipment_type, required_level, attack_speed, attack_ranged) in expected_bows.items():
            with self.subTest(item_name=item_name):
                bow = EQUIPMENT_DATA[item_name]
                self.assertEqual(bow.slot, "weapon")
                self.assertEqual(bow.combat_skill, "ranged")
                self.assertEqual(bow.required_level, required_level)
                self.assertEqual(bow.equipment_type, equipment_type)
                self.assertTrue(bow.two_handed)
                self.assertEqual(bow.attack_speed, attack_speed)
                self.assertEqual(bow.source_item_id, source_item_id)
                self.assertEqual(bow.bonuses.attack_ranged, attack_ranged)

    def test_goblin_drop_equipment_items_are_equippable(self):
        expected_spears = {
            "Bronze spear": (1237, 1, 5, 6),
            "Iron spear": (1239, 1, 8, 10),
            "Steel spear": (1241, 5, 12, 12),
        }
        for item_name, (source_item_id, required_level, attack_bonus, melee_strength) in expected_spears.items():
            with self.subTest(item_name=item_name):
                spear = EQUIPMENT_DATA[item_name]
                self.assertEqual(spear.slot, "weapon")
                self.assertEqual(spear.combat_skill, "attack")
                self.assertEqual(spear.required_level, required_level)
                self.assertEqual(spear.equipment_type, "spear")
                self.assertTrue(spear.two_handed)
                self.assertEqual(spear.attack_speed, 5)
                self.assertEqual(spear.source_item_id, source_item_id)
                self.assertEqual(spear.bonuses.attack_stab, attack_bonus)
                self.assertEqual(spear.bonuses.attack_slash, attack_bonus)
                self.assertEqual(spear.bonuses.attack_crush, attack_bonus)
                self.assertEqual(spear.bonuses.melee_strength, melee_strength)

        self.assertEqual(EQUIPMENT_DATA["Chef's hat"].slot, "head")
        self.assertEqual(EQUIPMENT_DATA["Chef's hat"].source_item_id, 1949)
        self.assertEqual(EQUIPMENT_DATA["Brass necklace"].slot, "neck")
        self.assertEqual(EQUIPMENT_DATA["Brass necklace"].source_item_id, 1009)

    def test_elemental_staves_are_equippable_magic_weapons(self):
        basic_staff = EQUIPMENT_DATA["Staff"]
        self.assertEqual(basic_staff.slot, "weapon")
        self.assertIsNone(basic_staff.combat_skill)
        self.assertEqual(basic_staff.required_level, 1)
        self.assertEqual(basic_staff.equipment_type, "staff")
        self.assertEqual(basic_staff.attack_speed, 5)
        self.assertEqual(basic_staff.source_item_id, 1379)
        self.assertEqual(basic_staff.bonuses.attack_magic, 4)
        self.assertEqual(basic_staff.bonuses.defence_magic, 4)
        self.assertEqual(basic_staff.bonuses.melee_strength, 3)

        expected = {
            "Staff of air": (1381, 0, 7, 3),
            "Staff of water": (1383, 0, 7, 3),
            "Staff of earth": (1385, 1, 9, 5),
            "Staff of fire": (1387, 3, 9, 6),
        }
        for item_name, (source_item_id, attack_stab, attack_crush, melee_strength) in expected.items():
            staff = EQUIPMENT_DATA[item_name]
            self.assertEqual(staff.slot, "weapon")
            self.assertIsNone(staff.combat_skill)
            self.assertEqual(staff.required_level, 1)
            self.assertEqual(staff.equipment_type, "elemental_staff")
            self.assertEqual(staff.attack_speed, 5)
            self.assertEqual(staff.source_item_id, source_item_id)
            self.assertEqual(staff.bonuses.attack_stab, attack_stab)
            self.assertEqual(staff.bonuses.attack_slash, -1)
            self.assertEqual(staff.bonuses.attack_crush, attack_crush)
            self.assertEqual(staff.bonuses.attack_magic, 10)
            self.assertEqual(staff.bonuses.defence_magic, 10)
            self.assertEqual(staff.bonuses.melee_strength, melee_strength)

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
