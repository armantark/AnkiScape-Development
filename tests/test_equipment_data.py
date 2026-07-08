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
        self.assertEqual(len(EQUIPMENT_DATA), 553)
        self.assertEqual(set(equipment_items_as_dict()), set(EQUIPMENT_DATA))
        self.assertEqual(EQUIPMENT_DATA["Cape"].slot, "cape")
        self.assertEqual(EQUIPMENT_DATA["Cape"].bonuses.defence_ranged, 2)
        self.assertEqual(EQUIPMENT_DATA["Air tiara"].slot, "head")
        self.assertEqual(EQUIPMENT_DATA["Wicked hood"].slot, "head")
        self.assertEqual(EQUIPMENT_DATA["Binding necklace"].slot, "neck")
        self.assertEqual(EQUIPMENT_DATA["Leather gloves"].slot, "hands")
        self.assertEqual(EQUIPMENT_DATA["Leather boots"].slot, "feet")
        self.assertEqual(EQUIPMENT_DATA["Bronze arrows"].slot, "ammunition")
        self.assertEqual(EQUIPMENT_DATA["Gold ring"].slot, "ring")
        # Smithable-but-undropped wieldable tools reach the roster via the
        # smithing-recipe source, not the type-based armour/weapon selector.
        self.assertEqual(EQUIPMENT_DATA["Rune hatchet"].slot, "weapon")

    def test_weapon_type_is_captured_for_the_attack_type_selector(self):
        # The generator records the RS WeaponType id per weapon so the attack-type
        # selector can look up its AttackStyleData slots. Non-weapon and typeless
        # weapon rows carry -1 (they fall back to the UNARMED table).
        self.assertEqual(EQUIPMENT_DATA["Rune 2h sword"].weapon_type, 7)
        self.assertEqual(EQUIPMENT_DATA["Rune scimitar"].weapon_type, 6)
        self.assertEqual(EQUIPMENT_DATA["Cape"].weapon_type, -1)
        self.assertEqual(EQUIPMENT_DATA["Toy kite"].weapon_type, -1)

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

    def test_tzhaar_drop_equipment_items_are_equippable(self):
        fire_battlestaff = EQUIPMENT_DATA["Fire battlestaff"]
        self.assertEqual(fire_battlestaff.slot, "weapon")
        self.assertEqual(fire_battlestaff.combat_skill, "attack")
        self.assertEqual(fire_battlestaff.required_level, 30)
        self.assertEqual(fire_battlestaff.skill_requirements, (("attack", 30), ("magic", 30)))
        self.assertEqual(fire_battlestaff.equipment_type, "battlestaff")
        self.assertEqual(fire_battlestaff.attack_speed, 5)
        self.assertEqual(fire_battlestaff.source_item_id, 1393)
        self.assertEqual(fire_battlestaff.bonuses.attack_crush, 28)
        self.assertEqual(fire_battlestaff.bonuses.attack_magic, 10)
        self.assertEqual(fire_battlestaff.bonuses.melee_strength, 35)

        shield = EQUIPMENT_DATA["Toktz-ket-xil"]
        self.assertEqual(shield.slot, "shield")
        self.assertEqual(shield.combat_skill, "defense")
        self.assertEqual(shield.required_level, 60)
        self.assertEqual(shield.skill_requirements, (("defense", 60),))
        self.assertEqual(shield.source_item_id, 6524)
        self.assertEqual(shield.bonuses.defence_stab, 40)
        self.assertEqual(shield.bonuses.defence_slash, 42)
        self.assertEqual(shield.bonuses.defence_ranged, 65)

        maul = EQUIPMENT_DATA["Tzhaar-ket-om"]
        self.assertEqual(maul.slot, "weapon")
        self.assertEqual(maul.combat_skill, "strength")
        self.assertEqual(maul.required_level, 60)
        self.assertEqual(maul.skill_requirements, (("strength", 60),))
        self.assertTrue(maul.two_handed)
        self.assertEqual(maul.attack_speed, 7)
        self.assertEqual(maul.source_item_id, 6528)
        self.assertEqual(maul.bonuses.attack_crush, 80)
        self.assertEqual(maul.bonuses.melee_strength, 85)

        cape = EQUIPMENT_DATA["Obsidian cape"]
        self.assertEqual(cape.slot, "cape")
        self.assertIsNone(cape.combat_skill)
        self.assertEqual(cape.source_item_id, 6568)
        self.assertEqual(cape.bonuses.defence_stab, 9)
        self.assertEqual(cape.bonuses.defence_magic, 9)

        as_dict = equipment_items_as_dict()
        self.assertEqual(as_dict["Fire battlestaff"]["skill_requirements"], (("attack", 30), ("magic", 30)))

    def test_shop_and_combat_drop_equipment_items_are_equippable(self):
        expected_items = {
            "Bronze boots": ("feet", 4119, 1, 1, 2, 3, 0),
            "Iron boots": ("feet", 4121, 1, 2, 3, 4, 0),
            "Rune boots": ("feet", 4131, 40, 12, 13, 14, 2),
            "Dragon med helm": ("head", 1149, 60, 33, 35, 32, 0),
            "Abyssal whip": ("weapon", 4151, 70, 0, 0, 0, 82),
            "Mystic gloves": ("hands", 4095, 20, 0, 0, 0, 0),
            "Obsidian cape": ("cape", 6568, 1, 9, 9, 9, 0),
        }
        for item_name, (slot, source_item_id, required_level, stab_def, slash_def, crush_def, strength) in expected_items.items():
            with self.subTest(item_name=item_name):
                item = EQUIPMENT_DATA[item_name]
                self.assertEqual(item.slot, slot)
                self.assertEqual(item.source_item_id, source_item_id)
                self.assertEqual(item.required_level, required_level)
                self.assertEqual(item.attack_speed, 4)
                self.assertEqual(item.bonuses.defence_stab, stab_def)
                self.assertEqual(item.bonuses.defence_slash, slash_def)
                self.assertEqual(item.bonuses.defence_crush, crush_def)
                self.assertEqual(item.bonuses.melee_strength, strength)

        self.assertEqual(EQUIPMENT_DATA["Abyssal whip"].bonuses.attack_slash, 82)
        self.assertEqual(EQUIPMENT_DATA["Mystic gloves"].bonuses.attack_magic, 3)
        self.assertEqual(EQUIPMENT_DATA["Mystic gloves"].bonuses.defence_magic, 3)

    def test_drop_and_shop_ammunition_uses_existing_plural_rows(self):
        for singular_name in ("Bronze arrow", "Iron arrow"):
            self.assertNotIn(singular_name, EQUIPMENT_DATA)
        for plural_name in ("Bronze arrows", "Iron arrows", "Bronze bolts", "Iron bolts"):
            self.assertIn(plural_name, EQUIPMENT_DATA)
            self.assertEqual(EQUIPMENT_DATA[plural_name].slot, "ammunition")

    def test_fist_of_guthix_metal_gauntlets_remain_unobtainable(self):
        for item_name in (
            "Bronze gauntlets",
            "Iron gauntlets",
            "Steel gauntlets",
            "Mithril gauntlets",
            "Adamant gauntlets",
            "Rune gauntlets",
            "Dragon gauntlets",
        ):
            self.assertNotIn(item_name, EQUIPMENT_DATA)

    def test_components_are_excluded_but_equippable_shop_tools_are_included(self):
        for item_name in (
            "Bronze arrowtips",
            "Bronze bolts (unf)",
            "Bronze limbs",
            "Steel studs",
        ):
            self.assertNotIn(item_name, EQUIPMENT_DATA)
        self.assertEqual(EQUIPMENT_DATA["Bronze pickaxe"].slot, "weapon")
        self.assertEqual(EQUIPMENT_DATA["Bronze hatchet"].slot, "weapon")

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
