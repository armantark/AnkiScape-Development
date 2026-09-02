from __future__ import annotations

from typing import Dict, Tuple

from .mechanics import (
    ITEM_ID_SOURCE_PATH,
)

COMBAT_EXTRA_ITEM_DATA: Dict[str, dict] = {
    "Elemental shield": {"category": "equipment", "source_item_id": 2890, "source": f"{ITEM_ID_SOURCE_PATH}: item 2890; Skeletal Wyvern oldid=6569736"},
    "Mind shield": {"category": "equipment", "source_item_id": 9731, "source": f"{ITEM_ID_SOURCE_PATH}: item 9731; Skeletal Wyvern oldid=6569736"},
    "Body shield": {"category": "equipment", "source_item_id": 18691, "source": f"{ITEM_ID_SOURCE_PATH}: item 18691; Skeletal Wyvern oldid=6569736"},
    "Cosmic shield": {"category": "equipment", "source_item_id": 20436, "source": f"{ITEM_ID_SOURCE_PATH}: item 20436; Skeletal Wyvern oldid=6569736"},
    "Chaos shield": {"category": "equipment", "source_item_id": 20438, "source": f"{ITEM_ID_SOURCE_PATH}: item 20438; Skeletal Wyvern oldid=6569736"},
    "Dragonfire shield": {"category": "equipment", "source_item_id": 11284, "source": f"{ITEM_ID_SOURCE_PATH}: item 11284; Skeletal Wyvern oldid=6569736"},
    "Antipoison (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_1"},
    "Antipoison (2)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_2"},
    "Antipoison (3)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_3"},
    "Antipoison (4)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_4"},
    "Avantoe seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.AVANTOE_SEED"},
    "Banana": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BANANA"},
    "Bat bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BAT_BONES"},
    "Bear fur": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BEAR_FUR"},
    "Belladonna seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BELLADONNA_SEED"},
    "Big bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BIG_BONES"},
    "Black bead": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLACK_BEAD"},
    "Black claws": {
        "category": "equipment",
        "source": "game-main data/cfg/items.yml item 3098",
        "source_item_id": 3098,
        "stackable": False,
        "tradeable": True,
    },
    "Black kiteshield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLACK_KITESHIELD"},
    "Black mace": {
        "category": "equipment",
        "source": "game-main data/cfg/items.yml item 1426",
        "source_item_id": 1426,
        "stackable": False,
        "tradeable": True,
    },
    "Black scimitar": {
        "category": "equipment",
        "source": "game-main data/cfg/items.yml item 1327",
        "source_item_id": 1327,
        "stackable": False,
        "tradeable": True,
    },
    "Black spear": {
        "category": "equipment",
        "source": "game-main data/cfg/items.yml item 4580",
        "source_item_id": 4580,
        "stackable": False,
        "tradeable": True,
    },
    "Black sq shield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLACK_SQ_SHIELD"},
    "Bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BONES"},
    "Brass necklace": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRASS_NECKLACE"},
    "Brine sabre": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 11037; "
            "RuneScape Wiki Brine rat oldid=6555564"
        ),
        "source_item_id": 11037,
        "stackable": False,
        "tradeable": True,
    },
    "Bronze javelin": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRONZE_JAVELIN"},
    "Bronze spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRONZE_SPEAR"},
    "Buttons": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BUTTONS"},
    "Cactus seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CACTUS_SEED"},
    "Cape": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CAPE_1019"},
    "Coral bolts": {
        "category": "equipment",
        "source": "RuneScape Wiki Coral bolts oldid 6146806; Darkan item config 24304",
        "source_item_id": 24304,
        "stackable": True,
        "tradeable": False,
    },
    "Saradomin cape": {
        "category": "equipment",
        "source": "RuneScape cache item 2412; Mage Arena oldid=6512911",
        "source_item_id": 2412,
        "stackable": False,
        "tradeable": False,
    },
    "Guthix cape": {
        "category": "equipment",
        "source": "RuneScape cache item 2413; Mage Arena oldid=6512911",
        "source_item_id": 2413,
        "stackable": False,
        "tradeable": False,
    },
    "Zamorak cape": {
        "category": "equipment",
        "source": "RuneScape cache item 2414; Mage Arena oldid=6512911",
        "source_item_id": 2414,
        "stackable": False,
        "tradeable": False,
    },
    "Cadantine seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CADANTINE_SEED"},
    "Cadava berries": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CADAVA_BERRIES"},
    "Champion's scroll": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CHAMPIONS_SCROLL_6800"},
    "Chef's hat": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CHEFS_HAT"},
    "Chilli potato": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CHILLI_POTATO"},
    "Cabbage seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CABBAGE_SEED"},
    "Clue scroll (easy)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CLUE_SCROLL_EASY"},
    "Clue scroll (medium)": {
        "category": "material",
        "source_item_id": 2801,
        "stackable": False,
        "tradeable": False,
        "source": f"{ITEM_ID_SOURCE_PATH}: Items.CLUE_SCROLL_MEDIUM; OpenRS2 rev-742 item 2801",
    },
    "Coins": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COINS_995"},
    "Cowhide": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COWHIDE"},
    "Crystal teleport seed": {
        "category": "material",
        "source": (
            "RuneScape Wiki Elf warrior oldid=6547078; "
            "Darkan item config 6103"
        ),
        "source_item_id": 6103,
        "stackable": False,
        "tradeable": False,
    },
    "Desert goat horn": {
        "category": "material",
        "source": (
            "RuneScape Wiki Desert goat horn oldid=6555637; "
            "OpenRS2 rev-742 item 9735"
        ),
        "source_item_id": 9735,
        "stackable": False,
        "tradeable": True,
    },
    "Curved bone": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CURVED_BONE"},
    **{
        item_name: {
            "category": "equipment",
            "source": (
                f"RuneScape Wiki Defenders oldid=6513277; "
                f"Darkan cache item {item_id}"
            ),
            "source_item_id": item_id,
            "stackable": False,
            "tradeable": False,
        }
        for item_name, item_id in (
            ("Bronze defender", 8844),
            ("Iron defender", 8845),
            ("Steel defender", 8846),
            ("Black defender", 8847),
            ("Mithril defender", 8848),
            ("Adamant defender", 8849),
            ("Rune defender", 8850),
            ("Dragon defender", 20072),
        )
    },
    "Cyclopean helmet": {
        "category": "equipment",
        "source": "RuneScape Wiki Cyclopean helmet oldid=5825578; Darkan cache item 20070",
        "source_item_id": 20070,
        "stackable": False,
        "tradeable": True,
    },
    "Damaged armour": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.DAMAGED_ARMOUR"},
    "Beer": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BEER"},
    "Dragon spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.DRAGON_SPEAR"},
    "Dwarf weed seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.DWARF_WEED_SEED"},
    "Edible seaweed": {
        "category": "food",
        "source": f"{ITEM_ID_SOURCE_PATH}: Items.EDIBLE_SEAWEED",
        "source_item_id": 403,
        "stackable": False,
        "tradeable": True,
    },
    "Eye patch": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.EYE_PATCH"},
    "Fire battlestaff": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.FIRE_BATTLESTAFF"},
    "Fungicide": {
        "category": "material",
        "source": "Darkan cache item 7432; RuneScape Wiki Mutated zygomite oldid 6530349",
        "source_item_id": 7432,
        "stackable": False,
        "tradeable": False,
    },
    **{
        f"Fungicide spray {charges}": {
            "category": "tool",
            "source": (
                f"Darkan cache item {7431 - charges}; "
                "RuneScape Wiki Mutated zygomite oldid 6530349"
            ),
            "source_item_id": 7431 - charges,
            "stackable": False,
            "tradeable": False,
        }
        for charges in range(11)
    },
    "Gardening boots": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GARDENING_BOOTS"},
    "Goblin book": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GOBLIN_BOOK"},
    "Grapes": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRAPES"},
    "Grimy avantoe": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_AVANTOE"},
    "Grimy cadantine": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_CADANTINE"},
    "Grimy dwarf weed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_DWARF_WEED"},
    "Grimy guam": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_GUAM"},
    "Grimy harralander": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_HARRALANDER"},
    "Grimy irit": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_IRIT"},
    "Grimy kwuarm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_KWUARM"},
    "Grimy lantadyme": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_LANTADYME"},
    "Grimy marrentill": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_MARRENTILL"},
    "Grimy ranarr": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_RANARR"},
    "Grimy snapdragon": {
        "category": "material",
        "source": "Darkan cache item 3051; Darkan herb special table item 3051",
        "source_item_id": 3051,
        "stackable": False,
        "tradeable": True,
    },
    "Grimy tarromin": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_TARROMIN"},
    "Half an apple pie": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HALF_AN_APPLE_PIE"},
    "Half a summer pie": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HALF_A_SUMMER_PIE"},
    "H.A.M. boots": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_BOOTS"},
    "H.A.M. cloak": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_CLOAK"},
    "H.A.M. gloves": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_GLOVES"},
    "H.A.M. hood": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_HOOD"},
    "H.A.M. logo": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_LOGO"},
    "H.A.M. robe": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_ROBE"},
    "H.A.M. shirt": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_SHIRT"},
    "Harralander seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HARRALANDER_SEED"},
    "Irit seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.IRIT_SEED"},
    "Impious ashes": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.IMPIOUS_ASHES"},
    "Iron javelin": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.IRON_JAVELIN"},
    "Iron spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.IRON_SPEAR"},
    "Jangerberry seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.JANGERBERRY_SEED"},
    "Jug of wine": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.JUG_OF_WINE"},
    "Kebab": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.KEBAB"},
    "Jug": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.JUG"},
    "Knife": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.KNIFE"},
    "Kwuarm seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.KWUARM_SEED"},
    "Lantadyme seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LANTADYME_SEED"},
    "Limpwurt root": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LIMPWURT_ROOT"},
    "Limpwurt seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LIMPWURT_SEED"},
    "Loop half of a key": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LOOP_HALF_OF_A_KEY"},
    "Long bone": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LONG_BONE"},
    "Magic staff": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MAGIC_STAFF"},
    "Marrentill seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MARRENTILL_SEED"},
    "Lava battlestaff": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 3053; "
            "RuneScape Wiki Lava battlestaff oldid 6037449"
        ),
        "source_item_id": 3053,
        "stackable": False,
        "tradeable": True,
    },
    "Mystic hat (dark)": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4099; "
            "RuneScape Wiki Mystic hat oldid 5971728"
        ),
        "source_item_id": 4099,
        "stackable": False,
        "tradeable": True,
    },
    "Mystic boots (dark)": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4107; "
            "RuneScape Wiki Mystic boots oldid 6315992"
        ),
        "source_item_id": 4107,
        "stackable": False,
        "tradeable": True,
    },
    "Mystic robe bottom (dark)": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4103; "
            "RuneScape Wiki Mystic robe bottom oldid 6436814"
        ),
        "source_item_id": 4103,
        "stackable": False,
        "tradeable": True,
    },
    "Mystic hat (light)": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4109; "
            "RuneScape Wiki Basilisk oldid 6565796"
        ),
        "source_item_id": 4109,
        "stackable": False,
        "tradeable": True,
    },
    "Basilisk head": {
        "category": "material",
        "source": (
            "game-main data/cfg/items.yml item 7977; "
            "RuneScape Wiki Basilisk oldid 6565796"
        ),
        "source_item_id": 7977,
        "stackable": False,
        "tradeable": False,
    },
    "Black boots": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4125; "
            "RuneScape Wiki Black boots oldid 6426419"
        ),
        "source_item_id": 4125,
        "stackable": False,
        "tradeable": True,
    },
    "Mithril boots": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4127; "
            "RuneScape Wiki Mithril armoured boots oldid 6007782"
        ),
        "source_item_id": 4127,
        "stackable": False,
        "tradeable": True,
    },
    "Mithril spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MITHRIL_SPEAR"},
    "Mole claw": {
        "category": "material",
        "source": "Darkan cache item 7416; Darkan Molanisk drop table",
        "source_item_id": 7416,
        "stackable": False,
        "tradeable": True,
    },
    "Mystic robe bottom (light)": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4113; "
            "RuneScape Wiki Turoth oldid 6565315"
        ),
        "source_item_id": 4113,
        "stackable": False,
        "tradeable": True,
    },
    "Monkey bones": {
        "category": "material",
        "source": "RuneScape Wiki Monkey oldid 6552407; Darkan item config 3183",
        "source_item_id": 3183,
        "stackable": False,
        "tradeable": True,
    },
    "Muddy key": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MUDDY_KEY"},
    "Needle": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.NEEDLE"},
    "Obsidian cape": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.OBSIDIAN_CAPE"},
    "Obsidian charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.OBSIDIAN_CHARM"},
    "Onion seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ONION_SEED"},
    "Poison ivy seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.POISON_IVY_SEED"},
    "Potato seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.POTATO_SEED"},
    "Rake": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAKE"},
    "Ranarr seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RANARR_SEED"},
    "Raw rat meat": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAW_RAT_MEAT"},
    "Red bead": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RED_BEAD"},
    "Rusty sword": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RUSTY_SWORD"},
    "Rune javelin": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RUNE_JAVELIN"},
    "Rune spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RUNE_SPEAR"},
    "Royal cape": {
        "category": "equipment",
        "source": "RuneScape Wiki Royal cape oldid 6308196; Darkan item config 24315",
        "source_item_id": 24315,
        "stackable": False,
        "tradeable": True,
    },
    "Spiked gauntlets": {
        "category": "equipment",
        "source": "RuneScape Wiki Spiked gauntlets oldid 5827717; Darkan item config 23035",
        "source_item_id": 23035,
        "stackable": False,
        "tradeable": False,
    },
    "Secateurs": {
        "category": "tool",
        "source_item_id": 5329,
        "stackable": False,
        "tradeable": True,
        "source": (
            f"{ITEM_ID_SOURCE_PATH}: Items.SECATEURS; "
            "OpenRS2 rev-742 item 5329; Willow branch oldid 6092914"
        ),
    },
    "Seed dibber": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SEED_DIBBER"},
    "Shears": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SHEARS"},
    "Shield left half": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SHIELD_LEFT_HALF"},
    "Sling": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SLING"},
    "Snapdragon seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SNAPDRAGON_SEED"},
    "Spinach roll": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SPINACH_ROLL"},
    "Staff": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF"},
    "Staff of air": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_AIR"},
    "Staff of water": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_WATER"},
    "Staff of earth": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_EARTH"},
    "Staff of fire": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_FIRE"},
    "Steel spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STEEL_SPEAR"},
    "Leaf-bladed sword": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 13290; "
            "RuneScape Wiki Turoth oldid 6565315"
        ),
        "source_item_id": 13290,
        "stackable": False,
        "tradeable": True,
    },
    "Swamp weed": {
        "category": "material",
        "source": "Darkan cache item 10978; Darkan Molanisk drop table",
        "source_item_id": 10978,
        "stackable": False,
        "tradeable": True,
    },
    "Steel boots": {
        "category": "equipment",
        "source": (
            "game-main data/cfg/items.yml item 4123; "
            "OpenRS2 revision-742 item 4123"
        ),
        "source_item_id": 4123,
        "stackable": False,
        "tradeable": True,
    },
    "Strawberry seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STRAWBERRY_SEED"},
    "Super defence (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_DEFENCE_1"},
    "Super antipoison (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_1"},
    "Super antipoison (2)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_2"},
    "Super antipoison (3)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_3"},
    "Super antipoison (4)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_4"},
    "Super strength (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_STRENGTH_1"},
    "Sweetcorn seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SWEETCORN_SEED"},
    "Tarromin seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TARROMIN_SEED"},
    "Thread": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.THREAD"},
    "Toadflax seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOADFLAX_SEED"},
    "Tooth half of a key": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOOTH_HALF_OF_A_KEY"},
    "Tomato seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOMATO_SEED"},
    "Tokkul": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOKKUL"},
    "Toktz-ket-xil": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOKTZKETXIL"},
    "Torstol seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TORSTOL_SEED"},
    "Tzhaar-ket-om": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TZHAARKETOM"},
    "Unicorn horn": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.UNICORN_HORN"},
    "Vial": {"category": "crafted", "source": f"{ITEM_ID_SOURCE_PATH}: Items.VIAL"},
    "Vial of water": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.VIAL_OF_WATER"},
    "Vecna skull": {
        "category": "material",
        "source": (
            "Darkan cache item 20667; "
            "Darkan rdt_mega_rare special table item 20667"
        ),
        "source_item_id": 20667,
        "stackable": False,
        "tradeable": True,
    },
    "Watering can (8)": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WATERING_CAN_8"},
    "Watermelon seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WATERMELON_SEED"},
    "White bead": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WHITE_BEAD"},
    "Whiteberry seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WHITEBERRY_SEED"},
    "Wildblood seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WILDBLOOD_SEED"},
    "Wooden shield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WOODEN_SHIELD"},
    "Wolf bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WOLF_BONES"},
    "Wizard hat": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WIZARD_HAT"},
    "Yellow bead": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.YELLOW_BEAD"},
    "Zamorak robe bottom": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ZAMORAK_ROBE"},
    "Zamorak robe top": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ZAMORAK_ROBE_1035"},
    "Tinderbox": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TINDERBOX_590"},
    "Gold charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GOLD_CHARM"},
    "Green charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GREEN_CHARM"},
    "Crimson charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CRIMSON_CHARM"},
    "Blue charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLUE_CHARM"},
}


COMBAT_TARGET_GROUP_ORDER: Tuple[str, ...] = (
    "Lumbridge",
    "Spiders",
    "Scorpions",
    "Goblins",
    "Humanoids",
    "TzHaar",
    "Coastal",
    "Stronghold of Player Safety",
    "Wilderness bosses",
)
