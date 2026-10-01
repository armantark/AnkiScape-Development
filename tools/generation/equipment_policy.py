"""Equipment generator selections that the acquisition data does not encode."""

from __future__ import annotations

# Drop-derived rows the live catalog does not carry: the six skill Brawling
# gloves already come from data/brawling_gloves_data.py.
DROP_ONLY_EXCLUDED_ITEM_IDS = frozenset({13850, 13851, 13852, 13855, 13856, 13857})

LEGACY_EQUIPMENT_ITEMS: tuple[
    tuple[str, int, str | None, int, bool, str, str], ...
] = (
    ("Air tiara", 5527, None, 1, False, "runecrafting_access", "Altar.kt; AIR_TIARA"),
    ("Binding necklace", 5521, None, 1, False, "binding_necklace", "legacy equipment_data.py; BINDING_NECKLACE"),
    ("Blood tiara", 5549, None, 1, False, "runecrafting_access", "Altar.kt; BLOOD_TIARA"),
    ("Body tiara", 5533, None, 1, False, "runecrafting_access", "Altar.kt; BODY_TIARA"),
    ("Brass necklace", 1009, None, 1, False, "necklace", "BRASS_NECKLACE"),
    ("Bronze spear", 1237, "attack", 1, True, "spear", "BRONZE_SPEAR"),
    ("Cape", 1019, None, 1, False, "cape", "CAPE_1019"),
    ("Chaos tiara", 5543, None, 1, False, "runecrafting_access", "Altar.kt; CHAOS_TIARA"),
    ("Chef's hat", 1949, None, 1, False, "hat", "CHEFS_HAT"),
    ("Mining helmet (lit)", 5013, "defense", 1, False, "head", "LightSource.java; MINING_HELMET_LIT"),
    ("Lit bug lantern", 7053, None, 1, False, "shield", "Lit bug lantern oldid=6591557; LightSource.java item 7053"),
    ("Mind shield", 9731, None, 1, False, "shield", "ElementalWorkshopIIIds.MIND_SHIELD"),
    ("Body shield", 18691, None, 1, False, "shield", "period elemental shield variant"),
    ("Cosmic shield", 20436, None, 1, False, "shield", "period elemental shield variant"),
    ("Chaos shield", 20438, None, 1, False, "shield", "period elemental shield variant"),
    ("Dragonfire shield", 11284, "defense", 75, False, "shield", "ItemForging.java: Anti-dragon shield plus Draconic visage"),
    ("Cosmic tiara", 5539, None, 1, False, "runecrafting_access", "Altar.kt; COSMIC_TIARA"),
    ("Death tiara", 5547, None, 1, False, "runecrafting_access", "Altar.kt; DEATH_TIARA"),
    ("Earth tiara", 5535, None, 1, False, "runecrafting_access", "Altar.kt; EARTH_TIARA"),
    ("Fire battlestaff", 1393, "attack", 30, False, "battlestaff", "FIRE_BATTLESTAFF"),
    ("Fire tiara", 5537, None, 1, False, "runecrafting_access", "Altar.kt; FIRE_TIARA"),
    ("Iron spear", 1239, "attack", 1, True, "spear", "IRON_SPEAR"),
    ("Law tiara", 5545, None, 1, False, "runecrafting_access", "Altar.kt; LAW_TIARA"),
    ("Mind tiara", 5529, None, 1, False, "runecrafting_access", "Altar.kt; MIND_TIARA"),
    ("Nature tiara", 5541, None, 1, False, "runecrafting_access", "Altar.kt; NATURE_TIARA"),
    ("Obsidian cape", 6568, None, 1, False, "obsidian_cape", "OBSIDIAN_CAPE"),
    ("Lava battlestaff", 3053, "attack", 30, False, "battlestaff", "LAVA_BATTLESTAFF"),
    ("Mystic hat (dark)", 4099, "defense", 20, False, "head", "MYSTIC_HAT_DARK"),
    ("Mystic robe bottom (dark)", 4103, "defense", 20, False, "legs", "MYSTIC_ROBE_BOTTOM_DARK"),
    ("Mystic boots (dark)", 4107, "defense", 20, False, "boots", "MYSTIC_BOOTS_DARK"),
    ("Mystic robe bottom (light)", 4113, "defense", 20, False, "legs", "MYSTIC_ROBE_BOTTOM_LIGHT"),
    ("Mystic hat (light)", 4109, "defense", 20, False, "head", "MYSTIC_HAT_LIGHT"),
    ("Leaf-bladed spear", 4158, "attack", 50, True, "spear", "LEAF_BLADED_SPEAR"),
    ("Leaf-bladed sword", 13290, "attack", 50, False, "sword", "LEAF_BLADED_SWORD"),
    ("Slayer's staff", 4170, "magic", 50, False, "staff", "SLAYER_STAFF"),
    ("Staff", 1379, None, 1, False, "staff", "STAFF"),
    ("Staff of air", 1381, None, 1, False, "elemental_staff", "STAFF_OF_AIR"),
    ("Staff of earth", 1385, None, 1, False, "elemental_staff", "STAFF_OF_EARTH"),
    ("Staff of fire", 1387, None, 1, False, "elemental_staff", "STAFF_OF_FIRE"),
    ("Staff of water", 1383, None, 1, False, "elemental_staff", "STAFF_OF_WATER"),
    ("Steel boots", 4123, "defense", 5, False, "boots", "STEEL_BOOTS"),
    ("Black boots", 4125, "defense", 10, False, "boots", "BLACK_BOOTS"),
    ("Mithril boots", 4127, "defense", 20, False, "boots", "MITHRIL_BOOTS"),
    ("Steel spear", 1241, "attack", 5, True, "spear", "STEEL_SPEAR"),
    ("Steel spear (kp)", 3172, "attack", 5, True, "spear", "STEEL_SPEAR"),
    ("Toktz-ket-xil", 6524, "defense", 60, False, "obsidian_shield", "TOKTZKETXIL"),
    ("Tzhaar-ket-om", 6528, "strength", 60, True, "obsidian_maul", "TZHAARKETOM"),
    ("Water tiara", 5531, None, 1, False, "runecrafting_access", "Altar.kt; WATER_TIARA"),
    ("Wicked hood", 22332, None, 1, False, "wicked_hood", "legacy equipment_data.py; WICKED_HOOD"),
)

LEGACY_EQUIPMENT_REQUIREMENT_OVERRIDES = {
    "Fire battlestaff": (("attack", 30), ("magic", 30)),
    "Lava battlestaff": (("attack", 30), ("magic", 30)),
    "Mystic hat (dark)": (("defense", 20), ("magic", 40)),
    "Mystic robe bottom (dark)": (("defense", 20), ("magic", 40)),
    "Mystic boots (dark)": (("defense", 20), ("magic", 20)),
    "Mystic robe bottom (light)": (("defense", 20), ("magic", 40)),
    "Mystic hat (light)": (("defense", 20), ("magic", 20)),
    "Leaf-bladed spear": (("attack", 50), ("slayer", 55)),
    "Leaf-bladed sword": (("attack", 50), ("slayer", 55)),
    "Slayer's staff": (("magic", 50),),
}

SOURCE_PROVENANCE_OVERRIDES = {
    3172: (
        "OpenRS2 cache rev 727 item 3172; Darkan WeaponPoison.java STEEL_SPEAR mapping",
        "period cache identity with exact Steel spear equipment stats",
    ),
}

