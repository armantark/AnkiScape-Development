#!/usr/bin/env python3
"""Regenerate construction_data.py from the pinned Darkan Construction tables."""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DARKAN = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server")
COMMIT = "7e7d67b481f1b94599de38a98c470419ab7c96b3"
BASE = "src/main/java/com/rs/game/content/skills/construction"
OBJECTS_PATH = f"{BASE}/playerOwnedHouse/HouseObjects.kt"
BUILDS_PATH = f"{BASE}/playerOwnedHouse/HouseBuilds.kt"
ITEM_NAMES_PATH = "developer-information/item_names.json"

CONSTANT_ITEMS = {
    "IRON_BAR": "Iron bar", "LIMESTONE_BRICKS": "Limestone brick",
    "SOFT_CLAY": "Soft clay", "MARBLE_BLOCK": "Marble block",
    "PLANK": "Plank", "NAILS": "Nails", "OAK_PLANK": "Oak plank",
    "TEAK_PLANK": "Teak plank", "MAHOGANY_PLANK": "Mahogany plank",
    "BOLT_OF_CLOTH": "Bolt of cloth", "STEEL_BAR": "Steel bar",
    "GOLD_LEAF": "Gold leaf", "MAGIC_STONE": "Magic stone",
    "MOLTEN_GLASS": "Molten glass",
}

NUMERIC_ITEMS = {
    33: "Lit candle", 35: "Excalibur", 36: "Candle", 526: "Bones",
    554: "Fire rune", 555: "Water rune", 556: "Air rune", 557: "Earth rune",
    559: "Body rune", 560: "Death rune", 561: "Nature rune", 562: "Chaos rune",
    563: "Law rune", 565: "Blood rune", 567: "Unpowered orb", 594: "Lit torch",
    954: "Rope", 960: "Plank", 964: "Skull", 995: "Coins",
    1052: "Cape of legends", 1085: "Mithril plateskirt", 1091: "Adamant plateskirt",
    1093: "Rune plateskirt", 1121: "Mithril platebody", 1123: "Adamant platebody",
    1127: "Rune platebody", 1159: "Mithril full helm", 1161: "Adamant full helm",
    1163: "Rune full helm", 1539: "Steel nails", 1540: "Anti-dragon shield",
    1704: "Amulet of glory", 1737: "Wool", 1761: "Soft clay", 1763: "Red dye",
    1775: "Molten glass", 1783: "Bucket of sand", 1905: "Asgarnian ale",
    1909: "Greenman's ale", 1911: "Dragon bitter", 1929: "Bucket of water",
    2351: "Iron bar", 2353: "Steel bar", 2357: "Gold bar", 2402: "Silverlight",
    3420: "Limestone brick", 4069: "Basic decorative platebody", 4071: "Basic decorative platelegs",
    4072: "Basic decorative helm", 4504: "Detailed decorative platebody",
    4506: "Detailed decorative platelegs", 4507: "Detailed decorative helm",
    4509: "Intricate decorative platebody", 4511: "Intricate decorative platelegs",
    4512: "Intricate decorative helm", 5755: "Chef's delight", 5763: "Cider",
    6570: "Fire cape", 6746: "Darklight", 7982: "Crawling hand", 7983: "Cockatrice head",
    7984: "Basilisk head", 7985: "Kurask head", 7986: "Abyssal head",
    7987: "King black dragon head", 7988: "Kalphite queen head", 7990: "Big bass",
    7992: "Big swordfish", 7994: "Big shark", 7995: "King Arthur portrait",
    7996: "Elena portrait", 7997: "Keldagrim portrait", 7998: "Miscellania portrait",
    7999: "Desert painting", 8000: "Isafdar painting", 8001: "Karamja painting",
    8002: "Lumbridge painting", 8003: "Morytania painting", 8004: "Small map",
    8005: "Medium map", 8006: "Large map", 8417: "Bagged dead tree",
    8419: "Bagged nice tree", 8421: "Bagged oak tree", 8423: "Bagged willow tree",
    8425: "Bagged maple tree", 8427: "Bagged yew tree", 8429: "Bagged magic tree",
    8431: "Bagged plant 1", 8433: "Bagged plant 2", 8435: "Bagged plant 3",
    8437: "Thorny hedge", 8439: "Nice hedge", 8441: "Small box hedge",
    8443: "Topiary hedge", 8445: "Fancy hedge", 8447: "Tall fancy hedge",
    8449: "Tall box hedge", 8451: "Bagged rosemary", 8453: "Bagged daffodils",
    8455: "Bagged bluebells", 8457: "Bagged sunflower", 8459: "Bagged marigolds",
    8461: "Bagged roses", 8778: "Oak plank", 8780: "Teak plank",
    8782: "Mahogany plank", 8784: "Gold leaf", 8786: "Marble block",
    8788: "Magic stone", 8790: "Bolt of cloth", 8792: "Clockwork",
    12158: "Gold charm", 12159: "Green charm", 12160: "Crimson charm",
    12163: "Blue charm", 12183: "Spirit shards", 15237: "Bagged cactus",
    15239: "Bagged evergreen", 18707: "Profound decorative platelegs",
    18708: "Profound decorative helm", 18709: "Profound decorative shield",
}

ROOM_RANGES = (
    (12, 57, "garden"), (58, 86, "parlour"), (87, 126, "skill_hall"),
    (127, 165, "dungeon"), (166, 202, "costume_room"), (203, 220, "menagerie"),
    (221, 243, "throne_room"), (244, 276, "bedroom"), (277, 310, "portal_chamber"),
    (311, 357, "kitchen"), (358, 389, "dining_room"), (390, 420, "workshop"),
    (421, 446, "games_room"), (447, 455, "combat_room"), (456, 483, "quest_hall"),
    (484, 504, "treasure_room"), (505, 541, "study"), (542, 588, "formal_garden"),
    (589, 599, "costume_room"), (600, 647, "chapel"),
)

FLATPACK_NAMES = """Crude wooden chair|Wooden chair|Rocking chair|Oak chair|Oak armchair|Teak armchair|Mahogany armchair|Wooden bookcase|Oak bookcase|Mahogany bookcase|Beer barrel|Cider barrel|Asgarnian ale (barrel)|Greenman's ale (barrel)|Dragon bitter (barrel)|Chef's delight (barrel)|Wood kitchen table|Oak kitchen table|Teak kitchen table|Wood dining table|Oak dining table|Carved oak table|Teak table|Carved teak table|Mahogany table|Opulent table|Wooden bench|Oak bench|Carved oak bench|Teak dining bench|Carved teak bench|Mahogany bench|Gilded bench|Wooden bed|Oak bed|Large oak bed|Teak bed|Large teak bed|4-poster|Gilded 4-poster|Shaving stand|Oak shaving stand|Oak dresser|Teak dresser|Fancy teak dresser|Mahogany dresser|Gilded dresser|Shoe box|Oak drawers|Oak wardrobe|Teak drawers|Teak wardrobe|Mahogany 'drobe|Gilded wardrobe|Oak clock|Teak clock|Gilded clock|Oak cape rack|Teak cape rack|M'gany cape rack|Gilded cape rack|Marble cape rack|Magical cape rack|Oak magic wardrobe|Carved oak magic wardrobe|Teak magic wardrobe|Carved teak magic wardrobe|Mahogany magic wardrobe|Gilded magic wardrobe|Marble magic wardrobe|Oak armour case|Teak armour case|M'gany arm'r case|Oak treasure chest|Teak treas' chest|M'gany treas' chest|Oak costume box|Teak costume box|Mahogany cos box|Oak toy box|Teak toy box|Mahogany toy box""".split("|")
FLATPACK_ALIASES = {
    "4-poster": "mahogany_bed", "Gilded 4-poster": "large_mahogany_bed",
    "Mahogany 'drobe": "mahogany_wardrobe", "M'gany cape rack": "mahoganycaperack",
    "M'gany arm'r case": "mahogany_armour_case", "M'gany treas' chest": "mahogany_treasure_chest",
    "Mahogany cos box": "mahoganycostumebox", "Teak dining bench": "teak_bench",
}
DISPLAY_OVERRIDES = {
    "DUNGEON_ENTRACE": "Dungeon entrance", "BASALISK_HEAD": "Basilisk head",
    "ABBYSAL_DEMON": "Abyssal demon", "GUILDED_ALTAR": "Gilded altar",
    "INSCENCE_BURNER": "Incense burner", "OAK_LECTURN": "Oak lectern",
    "EAGLE_LECTURN": "Eagle lectern", "DEMON_LECTURN": "Demon lectern",
    "TEAK_EAGLE_LECTURN": "Teak eagle lectern", "TEAK_DEMON_LECTURN": "Teak demon lectern",
    "MAHOGANY_EAGLE_LECTURN": "Mahogany eagle lectern", "MAHOGANY_DEMON_LECTURN": "Mahogany demon lectern",
}


def git_show(path: str) -> str:
    return subprocess.check_output(["git", "-C", str(DARKAN), "show", f"{COMMIT}:{path}"], text=True)


def entries(text: str):
    current, start, depth = [], 0, 0
    for lineno, line in enumerate(text.splitlines(), 1):
        if not current and re.match(r"\s*[A-Z][A-Z0-9_]*\(", line):
            current, start = [line.strip()], lineno
            depth = line.count("(") - line.count(")")
        elif current:
            current.append(line.strip())
            depth += line.count("(") - line.count(")")
        if current and depth == 0:
            value = " ".join(current).rstrip(",")
            yield start, re.sub(r"\s+//.*$", "", value).rstrip(",;")
            current = []


def humanize(name: str) -> str:
    return name.replace("_", " ").capitalize()


def top_level_parts(value: str) -> list[str]:
    parts, current, depth = [], [], 0
    for char in value:
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
        if char == "(": depth += 1
        elif char == ")": depth -= 1
    if current: parts.append("".join(current).strip())
    return parts


def room_for(line: int) -> str:
    return next(room for lo, hi, room in ROOM_RANGES if lo <= line <= hi)


def normalize(name: str) -> str:
    name = name.lower().replace("'", "").replace("4-", "four ").replace("greenmans", "greenman").replace("wooden", "wood").replace("table", "dining").replace("mahogany", "mgany").replace("armour", "armr").replace("treasure", "treas")
    name = name.replace("(barrel)", "").replace("barrel", "")
    return re.sub(r"[^a-z0-9]", "", name)


def main() -> None:
    objects_text = git_show(OBJECTS_PATH)
    builds_text = git_show(BUILDS_PATH)
    item_names = {
        int(item_id): name.strip()
        for item_id, name in re.findall(r"(?m)^(\d+) - (.*?)(?: - \[.*)?$", git_show(ITEM_NAMES_PATH))
    }
    water = set()
    for _, entry in entries(builds_text):
        if re.search(r"\btrue\b", entry):
            water.update(re.findall(r"HouseObjects\.([A-Z0-9_]+)", entry))
    rows = []
    for line, entry in entries(objects_text):
        match = re.match(r"^([A-Z0-9_]+)\((.*)\)$", entry)
        if not match:
            continue
        enum, body = match.groups()
        parts = top_level_parts(body)
        item_id = parts[0]
        if len(parts) < 4:
            continue
        if parts[1].isdigit() and parts[2].replace(".", "", 1).isdigit() and parts[3].startswith("Item("):
            level, xp, requirement_parts = parts[1], parts[2], parts[3:]
        else:
            level, xp, requirement_parts = parts[2], parts[3], parts[4:]
        requirements_text = ", ".join(requirement_parts)
        requirements = {}
        for token, amount in re.findall(r"Item\(([^,)]+)(?:,\s*(\d+))?\)", requirements_text):
            token = token.strip()
            qty = int(amount or 1)
            if token.startswith("HouseConstants."):
                item = CONSTANT_ITEMS[token.split(".")[-1]]
            else:
                item = NUMERIC_ITEMS[int(token)]
            requirements[item] = requirements.get(item, 0) + qty
        target_id = enum.lower()
        display = DISPLAY_OVERRIDES.get(enum, humanize(enum))
        if enum == "TEAKTOYBOX":
            level = "68"
        rows.append({
            "id": target_id, "display_name": display, "item_id": int(item_id),
            "asset_name": item_names.get(int(item_id), display),
            "level": int(level), "xp": float(xp), "requirements": requirements,
            "room": room_for(line), "water": enum in water,
            "stateful": any(word in enum for word in ("ALTAR", "BURNER", "WORKBENCH", "LECTERN")),
            "source": f"{OBJECTS_PATH}:{line} @ {COMMIT}",
        })
    by_norm = {normalize(row["display_name"]): row for row in rows}
    flatpacks = []
    for display in FLATPACK_NAMES:
        if display in FLATPACK_ALIASES:
            row = next((candidate for candidate in rows if candidate["id"] == FLATPACK_ALIASES[display]), None)
            if row is None:
                raise RuntimeError(f"Flatpack alias missing: {display} -> {FLATPACK_ALIASES[display]}")
            row["display_name"] = display
            gate = 17 if row["level"] <= 20 else 32 if row["level"] <= 40 else 46 if row["level"] <= 60 else 62 if row["level"] <= 80 else 77
            flatpacks.append({**row, "id": f"flatpack_{row['id']}", "display_name": f"{display} flatpack", "output_item": display, "asset_name": item_names.get(row['item_id'], display), "workbench_level": gate, "source": f"{row['source']}; RuneScape Wiki Flatpack oldid=6579365 (2012-11-18)"})
            continue
        key = normalize(display)
        row = by_norm.get(key)
        if row is None:
            candidates = [candidate for candidate in rows if key in normalize(candidate["display_name"]) or normalize(candidate["display_name"]) in key]
            if len(candidates) != 1:
                raise RuntimeError(f"Flatpack match failed: {display}: {[c['display_name'] for c in candidates]}")
            row = candidates[0]
        row["display_name"] = display
        gate = 17 if row["level"] <= 20 else 32 if row["level"] <= 40 else 46 if row["level"] <= 60 else 62 if row["level"] <= 80 else 77
        flatpacks.append({**row, "id": f"flatpack_{row['id']}", "display_name": f"{display} flatpack", "output_item": display, "asset_name": item_names.get(row['item_id'], display), "workbench_level": gate, "source": f"{row['source']}; RuneScape Wiki Flatpack oldid=6579365 (2012-11-18)"})

    header = '''"""Closed-contract pre-EOC Construction tables.

Generated from Darkan commit 7e7d67b481f1b94599de38a98c470419ab7c96b3.
Every build row carries its source line; wiki gap-fill revisions are literal pins.
"""
from __future__ import annotations

DARKAN_COMMIT = "7e7d67b481f1b94599de38a98c470419ab7c96b3"
HOUSE_OBJECTS_SOURCE = "src/main/java/com/rs/game/content/skills/construction/playerOwnedHouse/HouseObjects.kt"
DEFAULT_CONSTRUCTION_TARGET = "crude_wooden_chair"
INITIAL_HOUSE_PRICE = 1000
INITIAL_HOUSE_SOURCE = "RuneScape Wiki Player-owned house oldid=6560168 (2012-11-15)"
FLATPACK_SOURCE = "RuneScape Wiki Flatpack oldid=6579365 (2012-11-18)"
NAILS_SOURCE = "RuneScape Wiki Nails oldid=6106079 (2012-08-18); 2009scape NailType.java numeric gap-fill"
LIMESTONE_BRICK_SOURCE = "RuneScape Wiki Limestone brick oldid=6308408 (2012-09-27)"
SPECIALTY_SHOP_SOURCE = "RuneScape Wiki Bolt of cloth oldid=5917052; Gold leaf oldid=5947638; Marble block oldid=6453264; Magic stone oldid=6381870"
HOUSE_STYLE_SOURCE = "EstateAgentDialogue.java @ 7e7d67b481f1b94599de38a98c470419ab7c96b3; RuneScape Wiki Estate agent oldid=6404820 (Fremennik 25,000 correction)"
CHAPEL_SOURCE = "RuneScape Wiki Chapel oldid=6405871 (2012-10-14)"
MAHOGANY_BURNER_SOURCE = "RuneScape Wiki Mahogany incense burners oldid=5023214 (2011-12-06)"

'''
    rooms = [
        ("parlour", "Parlour", 1, 1000), ("garden", "Garden", 1, 1000), ("kitchen", "Kitchen", 5, 5000),
        ("dining_room", "Dining room", 10, 5000), ("workshop", "Workshop", 15, 10000), ("bedroom", "Bedroom", 20, 10000),
        ("skill_hall", "Skill hall", 25, 15000), ("games_room", "Games room", 30, 25000), ("combat_room", "Combat room", 32, 25000),
        ("quest_hall", "Quest hall", 35, 25000), ("menagerie", "Menagerie", 37, 30000), ("study", "Study", 40, 50000),
        ("costume_room", "Costume room", 42, 50000), ("chapel", "Chapel", 45, 50000), ("portal_chamber", "Portal chamber", 50, 100000),
        ("formal_garden", "Formal garden", 55, 75000), ("throne_room", "Throne room", 60, 150000), ("oubliette", "Oubliette", 65, 150000),
        ("dungeon", "Dungeon", 70, 7500), ("dungeon_junction", "Dungeon junction", 70, 7500), ("dungeon_stairs", "Dungeon stairs", 70, 7500),
        ("dungeon_pit", "Dungeon pit", 70, 10000), ("treasure_room", "Treasure room", 75, 250000),
    ]
    servants = [("rick", "Rick", 20, 375, 6, 100), ("maid", "Maid", 25, 750, 10, 50), ("cook", "Cook", 30, 2250, 16, 28), ("butler", "Butler", 40, 3750, 20, 20), ("demon_butler", "Demon butler", 50, 7500, 26, 12)]
    styles = [("basic_wood", "Basic wood", 1, 2500, None), ("basic_stone", "Basic stone", 10, 10000, None), ("whitewashed_stone", "Whitewashed stone", 20, 15000, None), ("fremennik_wood", "Fremennik-style wood", 30, 25000, None), ("tropical_wood", "Tropical wood", 40, 50000, None), ("fancy_stone", "Fancy stone", 50, 100000, None), ("dark_stone", "Dark stone", 68, 500000, "love_story")]
    tablets = [
        ("onyx_enchant", "Lvl-6 enchant", 8021, 87, 72.8, {"Soft clay":1,"Cosmic rune":1,"Earth rune":20,"Fire rune":20}, 9),
        ("lumbridge_teleport", "Lumbridge teleport", 8008, 31, 41, {"Soft clay":1,"Air rune":3,"Earth rune":1,"Law rune":1}, 13),
        ("diamond_enchant", "Lvl-4 enchant", 8019, 57, 50.3, {"Soft clay":1,"Cosmic rune":1,"Earth rune":10}, 6),
        ("watchtower_teleport", "Watchtower teleport", 8012, 58, 68, {"Soft clay":1,"Earth rune":2,"Law rune":2}, 16),
        ("house_teleport", "Teleport to house", 8013, 40, 30, {"Soft clay":1,"Air rune":1,"Earth rune":1,"Law rune":1}, 14),
        ("emerald_enchant", "Lvl-2 enchant", 8017, 27, 27.8, {"Soft clay":1,"Cosmic rune":1,"Air rune":3}, 8),
        ("sapphire_enchant", "Lvl-1 enchant", 8016, 7, 13.2, {"Soft clay":1,"Cosmic rune":1,"Water rune":1}, 11),
        ("falador_teleport", "Falador teleport", 8009, 37, 48, {"Soft clay":1,"Air rune":3,"Water rune":1,"Law rune":1}, 12),
        ("ardougne_teleport", "Ardougne teleport", 8011, 51, 63.5, {"Soft clay":1,"Water rune":2,"Law rune":2}, 2),
        ("bones_to_bananas", "Bones to bananas", 8014, 15, 25, {"Soft clay":1,"Water rune":2,"Earth rune":2,"Nature rune":1}, 3),
        ("dragonstone_enchant", "Lvl-5 enchant", 8020, 68, 58.5, {"Soft clay":1,"Cosmic rune":1,"Water rune":15,"Earth rune":15}, 7),
        ("ruby_enchant", "Lvl-3 enchant", 8018, 49, 44.3, {"Soft clay":1,"Cosmic rune":1,"Fire rune":5}, 10),
        ("varrock_teleport", "Varrock teleport", 8007, 25, 35, {"Soft clay":1,"Air rune":3,"Law rune":1,"Fire rune":1}, 15),
        ("camelot_teleport", "Camelot teleport", 8010, 45, 55.5, {"Soft clay":1,"Air rune":5,"Law rune":1}, 5),
        ("bones_to_peaches", "Bones to peaches", 8015, 60, 35.5, {"Soft clay":1,"Water rune":4,"Earth rune":4,"Nature rune":2}, 4),
    ]
    payload = header
    payload += f"CONSTRUCTION_BUILD_TARGETS = {rows!r}\n\n"
    payload += f"FLATPACK_TARGETS = {flatpacks!r}\n\n"
    payload += f"ROOMS = {rooms!r}\nROOM_SOURCE_LINES = {{'parlour': 13, 'garden': 14, 'kitchen': 25, 'dining_room': 26, 'workshop': 27, 'bedroom': 28, 'skill_hall': 29, 'games_room': 40, 'combat_room': 41, 'quest_hall': 42, 'menagerie': 53, 'study': 64, 'costume_room': 65, 'chapel': 76, 'portal_chamber': 77, 'formal_garden': 78, 'throne_room': 89, 'oubliette': 90, 'dungeon': 101, 'dungeon_junction': 102, 'dungeon_stairs': 113, 'dungeon_pit': 124, 'treasure_room': 135}}\nROOM_DATA = {{row[0]: {{'id': row[0], 'display_name': row[1], 'level': row[2], 'price': row[3], 'source': f\"src/main/java/com/rs/game/content/skills/construction/playerOwnedHouse/HouseRooms.kt:{{ROOM_SOURCE_LINES[row[0]]}} @ {{DARKAN_COMMIT}}\"}} for row in ROOMS}}\n\n"
    payload += f"SERVANTS = {servants!r}\nSERVANT_SOURCE_LINES = {{'rick': 13, 'maid': 14, 'cook': 15, 'butler': 16, 'demon_butler': 17}}\nSERVANT_DATA = {{row[0]: {{'id': row[0], 'display_name': row[1], 'level': row[2], 'wage': row[3], 'batch_size': row[4], 'bank_delay': row[5], 'source': f\"src/main/java/com/rs/game/content/skills/construction/playerOwnedHouse/HouseServants.kt:{{SERVANT_SOURCE_LINES[row[0]]}} @ {{DARKAN_COMMIT}}\"}} for row in SERVANTS}}\n\n"
    payload += f"STYLES = {styles!r}\nSTYLE_SOURCE_LINES = {{'basic_wood': 58, 'basic_stone': 60, 'whitewashed_stone': 62, 'fremennik_wood': 64, 'tropical_wood': 66, 'fancy_stone': 68, 'dark_stone': 70}}\nHOUSE_STYLE_DATA = {{row[0]: {{'id': row[0], 'display_name': row[1], 'level': row[2], 'price': row[3], 'quest_gate': row[4], 'source': f\"src/main/java/com/rs/game/content/skills/construction/EstateAgentDialogue.java:{{STYLE_SOURCE_LINES[row[0]]}} @ {{DARKAN_COMMIT}}; {{HOUSE_STYLE_SOURCE}}\"}} for row in STYLES}}\n\n"
    payload += "NAIL_DATA = {\n    'Bronze nails': {'item_id': 4819, 'bend_rate': 5}, 'Iron nails': {'item_id': 4820, 'bend_rate': 7},\n    'Steel nails': {'item_id': 1539, 'bend_rate': 10}, 'Mithril nails': {'item_id': 4822, 'bend_rate': 13},\n    'Adamantite nails': {'item_id': 4823, 'bend_rate': 15}, 'Rune nails': {'item_id': 4824, 'bend_rate': 20},\n}\nfor _row in NAIL_DATA.values(): _row['source'] = NAILS_SOURCE\n\n"
    payload += f"TABLET_ASSET_NAMES = {dict((row[2], item_names.get(row[2], row[1] + ' tablet')) for row in tablets)!r}\n"
    payload += f"TABLETS = {tablets!r}\nTABLET_TARGETS = [{{'id': 'tablet_' + row[0], 'display_name': row[1] + ' tablet', 'output_item': row[1] + ' tablet', 'asset_name': TABLET_ASSET_NAMES[row[2]], 'item_id': row[2], 'magic_level': row[3], 'xp': float(row[4]), 'requirements': row[5], 'lectern_component': row[6], 'room': 'study', 'source': f\"src/main/java/com/rs/game/content/skills/construction/TabletMaking.java:{{33 + index}} @ {{DARKAN_COMMIT}}\"}} for index, row in enumerate(TABLETS)]\n\n"
    payload += "WORKBENCH_TIERS = ((17, 'wooden_workbench'), (32, 'oak_workbench'), (46, 'steel_framed_workbench'), (62, 'bench_with_vice'), (77, 'bench_with__a_lathe'))\n"
    payload += "ALL_CONSTRUCTION_TARGETS = tuple(CONSTRUCTION_BUILD_TARGETS + FLATPACK_TARGETS + TABLET_TARGETS)\nCONSTRUCTION_DATA = {row['id']: row for row in ALL_CONSTRUCTION_TARGETS}\n\n"
    payload += '''def construction_extra_items_as_dict():
    items = {}
    for row in CONSTRUCTION_BUILD_TARGETS:
        for name in row['requirements']:
            if name == 'Nails':
                continue
            items.setdefault(name, {'category': 'material', 'source': row['source']})
    for row in FLATPACK_TARGETS + TABLET_TARGETS:
        items[row['output_item']] = {'category': 'crafted', 'source_item_id': row['item_id'], 'source': row['source']}
    items['Crystal saw'] = {'category': 'tool', 'source_item_id': 9625, 'source': 'House.kt:468 @ ' + DARKAN_COMMIT}
    items['Clean marrentill'] = {'category': 'material', 'source_item_id': 251, 'source': 'RuneScape Wiki Chapel oldid=6405871'}
    for name, row in NAIL_DATA.items():
        items[name] = {'category': 'material', 'source_item_id': row['item_id'], 'source': row['source']}
    return items

def construction_asset_items_as_dict():
    items = {}
    for row in ALL_CONSTRUCTION_TARGETS:
        items.setdefault(row['asset_name'], {'source_item_id': row['item_id'], 'source': row['source']})
        for name in row.get('requirements', {}):
            if name != 'Nails':
                items.setdefault(name, {'source': row['source']})
    items.update(construction_extra_items_as_dict())
    return items
'''
    (ROOT / "data" / "construction_data.py").write_text(payload, encoding="utf-8")
    print(f"wrote {len(rows)} builds, {len(flatpacks)} flatpacks, {len(tablets)} tablets")


if __name__ == "__main__":
    main()
