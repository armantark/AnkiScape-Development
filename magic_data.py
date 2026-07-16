"""Closed-contract Magic tables for the full pre-EOC skill surface.

Audited RuneScape values stay in this module; review pacing is implemented by
the runtime (one cast per successful review).  The 2011Scape rev-667 source is
primary where it has an implementation.  Gap rows cite the literal pre-EOC
RuneScape Wiki revision used by the Magic contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Tuple


GAME_MAGIC = "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic"
SPELLBOOK_SOURCE = f"{GAME_MAGIC}/SpellbookData.kt"
ALCHEMY_SOURCE = f"{GAME_MAGIC}/alchemy/alchemy.plugin.kts"
ENCHANT_SOURCE = f"{GAME_MAGIC}/jewelleryenchanting/EnchantmentData.kt"
SUPERHEAT_SOURCE = f"{GAME_MAGIC}/superheat/superheat.plugin.kts"
STANDARD_WIKI = "RuneScape Wiki Standard spells oldid=6545726 (2012-11-10)"
ANCIENT_WIKI = "RuneScape Wiki Ancient Magicks oldid=6468193 (2012-10-24)"
LUNAR_WIKI = "RuneScape Wiki Lunar spells oldid=6288542 (2012-09-24)"
BOLT_WIKI = "RuneScape Wiki Enchant Crossbow Bolt oldid=5831571 (2012-06-25)"
TELEGRAB_WIKI = "RuneScape Wiki Telekinetic Grab oldid=6587753 (2012-11-19)"
MAGE_ARENA_WIKI = "RuneScape Wiki Mage Arena oldid=6512911 (2012-10-31)"
CHARGE_WIKI = "RuneScape Wiki Charge oldid=6549273 (2012-11-12)"
DREAM_WIKI = "RuneScape Wiki Dream oldid=6587759 (2012-11-19)"
SWAP_WIKI = "RuneScape Wiki Spellbook Swap oldid=5827653 (2012-06-25)"
VENGEANCE_WIKI = "RuneScape Wiki Vengeance oldid=6587400 (2012-11-19)"

DEFAULT_MAGIC_TARGET = "low_alchemy"
MAGIC_GROUP_ORDER = (
    "Alchemy", "Teleports — Standard", "Teleports — Ancient", "Teleports — Lunar",
    "Enchant jewellery", "Enchant bolts", "Charge orbs", "Conversions",
    "Lunar skilling", "Pure casts",
)
ELEMENTAL_RUNES = ("Air rune", "Water rune", "Earth rune", "Fire rune")


def _spell(
    target_id: str, name: str, book: str, group: str, level: int, xp: float,
    runes: Mapping[str, int], action: str = "pure", *, requirements=None,
    outputs=None, quest_gate: Optional[str] = None, source: str = STANDARD_WIKI,
    batch: str = "one", secondary_skill: Optional[str] = None,
    secondary_xp: float = 0.0, secondary_level: int = 1, coin_cost: int = 0,
) -> dict:
    return {
        "id": target_id, "display_name": name, "spellbook": book, "group": group,
        "level": level, "exp": float(xp), "rune_cost": dict(runes), "action": action,
        "requirements": dict(requirements or {}), "outputs": dict(outputs or {}),
        "quest_gate": quest_gate, "source": source, "batch": batch,
        "secondary_skill": secondary_skill, "secondary_exp": float(secondary_xp),
        "secondary_level": int(secondary_level),
        "coin_cost": int(coin_cost),
    }


MAGIC_TARGETS: Dict[str, dict] = {}


def _add(*rows: dict) -> None:
    for row in rows:
        MAGIC_TARGETS[row["id"]] = row


# Standard noncombat spellbook. SpellbookData.kt establishes levels/runes;
# oldid=6545726 supplies the XP columns absent from the emulator enum.
_add(
    _spell("low_alchemy", "Low Level Alchemy", "standard", "Alchemy", 21, 31, {"Fire rune": 3, "Nature rune": 1}, "alchemy", source=f"{SPELLBOOK_SOURCE}: LOW_ALCHEMY; {ALCHEMY_SOURCE}: low=40% cache value, 31 XP; {STANDARD_WIKI}"),
    _spell("high_alchemy", "High Level Alchemy", "standard", "Alchemy", 55, 65, {"Fire rune": 5, "Nature rune": 1}, "alchemy", source=f"{SPELLBOOK_SOURCE}: HIGH_ALCHEMY; {ALCHEMY_SOURCE}: high=60% cache value, 65 XP; {STANDARD_WIKI}"),
)

for row in (
    ("mobilising_armies_teleport", "Mobilising Armies Teleport", 10, 19, {"Air rune": 1, "Water rune": 1, "Law rune": 1}, "mobilising_armies"),
    ("varrock_teleport", "Varrock Teleport", 25, 35, {"Air rune": 3, "Fire rune": 1, "Law rune": 1}, None),
    ("lumbridge_teleport", "Lumbridge Teleport", 31, 41, {"Air rune": 3, "Earth rune": 1, "Law rune": 1}, None),
    ("falador_teleport", "Falador Teleport", 37, 47, {"Air rune": 3, "Water rune": 1, "Law rune": 1}, None),
    ("teleport_to_house", "Teleport to House", 40, 30, {"Air rune": 1, "Earth rune": 1, "Law rune": 1}, None),
    ("camelot_teleport", "Camelot Teleport", 45, 55.5, {"Air rune": 5, "Law rune": 1}, None),
    ("ardougne_teleport", "Ardougne Teleport", 51, 61, {"Water rune": 2, "Law rune": 2}, "plague_city"),
    ("watchtower_teleport", "Watchtower Teleport", 58, 68, {"Earth rune": 2, "Law rune": 2}, "watchtower"),
    ("trollheim_teleport", "Trollheim Teleport", 61, 68, {"Fire rune": 2, "Law rune": 2}, "eadgars_ruse"),
    ("ape_atoll_teleport", "Teleport to Ape Atoll", 64, 74, {"Fire rune": 2, "Water rune": 2, "Law rune": 2}, "recipe_for_disaster_freeing_king_awowogei"),
):
    req = {"Banana": 1} if row[0] == "ape_atoll_teleport" else None
    _add(_spell(row[0], row[1], "standard", "Teleports — Standard", row[2], row[3], row[4], requirements=req, quest_gate=row[5], source=f"{SPELLBOOK_SOURCE}; {STANDARD_WIKI}"))

# Ancient solo teleports. Desert Treasure is the book gate for every row.
for target_id, name, level, xp, runes in (
    ("paddewwa_teleport", "Paddewwa Teleport", 54, 64, {"Air rune": 1, "Fire rune": 1, "Law rune": 2}),
    ("senntisten_teleport", "Senntisten Teleport", 60, 70, {"Soul rune": 1, "Law rune": 2}),
    ("kharyrll_teleport", "Kharyrll Teleport", 66, 76, {"Blood rune": 1, "Law rune": 2}),
    ("lassar_teleport", "Lassar Teleport", 72, 82, {"Water rune": 4, "Law rune": 2}),
    ("dareeyak_teleport", "Dareeyak Teleport", 78, 88, {"Air rune": 2, "Fire rune": 3, "Law rune": 2}),
    ("carrallangar_teleport", "Carrallangar Teleport", 84, 94, {"Soul rune": 2, "Law rune": 2}),
    ("annakarl_teleport", "Annakarl Teleport", 90, 100, {"Blood rune": 2, "Law rune": 2}),
    ("ghorrock_teleport", "Ghorrock Teleport", 96, 106, {"Water rune": 8, "Law rune": 2}),
):
    _add(_spell(target_id, name, "ancient", "Teleports — Ancient", level, xp, runes, quest_gate="desert_treasure", source=ANCIENT_WIKI))

# Lunar solo teleports; group/other-player variants and Livid Farm rows are
# intentionally absent per the closed contract.
for target_id, name, level, xp, runes, gate in (
    ("moonclan_teleport", "Moonclan Teleport", 69, 66, {"Astral rune": 2, "Law rune": 1, "Earth rune": 2}, "lunar_diplomacy"),
    ("ourania_teleport", "Ourania Teleport", 71, 69, {"Astral rune": 2, "Law rune": 1, "Earth rune": 6}, "lunar_diplomacy"),
    ("waterbirth_teleport", "Waterbirth Teleport", 72, 71, {"Astral rune": 2, "Law rune": 1, "Water rune": 1}, "lunar_diplomacy"),
    ("barbarian_teleport", "Barbarian Teleport", 75, 76, {"Astral rune": 2, "Law rune": 2, "Fire rune": 3}, "lunar_diplomacy"),
    ("khazard_teleport", "Khazard Teleport", 78, 80, {"Astral rune": 2, "Law rune": 2, "Water rune": 4}, "lunar_diplomacy"),
    ("fishing_guild_teleport", "Fishing Guild Teleport", 85, 89, {"Astral rune": 3, "Law rune": 3, "Water rune": 10}, "lunar_diplomacy"),
    ("catherby_teleport", "Catherby Teleport", 87, 92, {"Astral rune": 3, "Law rune": 3, "Water rune": 10}, "lunar_diplomacy"),
    ("ice_plateau_teleport", "Ice Plateau Teleport", 89, 96, {"Astral rune": 3, "Law rune": 3, "Water rune": 8}, "lunar_diplomacy"),
):
    _add(_spell(target_id, name, "lunar", "Teleports — Lunar", level, xp, runes, quest_gate=gate, source=LUNAR_WIKI))


# Jewellery: all six gem tiers x four jewellery forms from EnchantmentData.kt.
_JEWEL_TIERS = (
    (1, "Sapphire", 7, 17.5, {"Cosmic rune": 1, "Water rune": 1}, ("Ring of recoil", "Games necklace (8)", "Amulet of magic", "Bracelet of clay")),
    (2, "Emerald", 27, 37, {"Cosmic rune": 1, "Air rune": 3}, ("Ring of duelling (8)", "Binding necklace", "Amulet of defence", "Castle wars bracelet (3)")),
    (3, "Ruby", 49, 59, {"Cosmic rune": 1, "Fire rune": 5}, ("Ring of forging", "Digsite pendant (5)", "Amulet of strength", "Inoculation bracelet")),
    (4, "Diamond", 57, 67, {"Cosmic rune": 1, "Earth rune": 10}, ("Ring of life", "Phoenix necklace", "Amulet of power", "Forinthry bracelet (5)")),
    (5, "Dragonstone", 68, 78, {"Cosmic rune": 1, "Earth rune": 15, "Water rune": 15}, ("Ring of wealth", "Skills necklace (4)", "Amulet of glory (4)", "Combat bracelet (4)")),
    (6, "Onyx", 87, 97, {"Cosmic rune": 1, "Earth rune": 20, "Fire rune": 20}, ("Ring of stone", "Berserker necklace", "Amulet of fury", "Regen bracelet")),
)
for tier, gem, level, xp, runes, products in _JEWEL_TIERS:
    for form, product in zip(("ring", "necklace", "amulet", "bracelet"), products):
        raw = {
            ("Dragonstone", "necklace"): "Dragon necklace",
            ("Dragonstone", "amulet"): "Dragonstone ammy",
            ("Dragonstone", "bracelet"): "Dragon bracelet",
        }.get((gem, form), f"{gem} {form}")
        _add(_spell(f"enchant_{gem.lower()}_{form}", f"Enchant {raw}", "standard", "Enchant jewellery", level, xp, runes, "transform", requirements={raw: 1}, outputs={product: 1}, source=f"{ENCHANT_SOURCE}; {STANDARD_WIKI}"))


for gem, level, xp, runes in (
    ("Opal", 4, 9, {"Cosmic rune": 1, "Air rune": 2}),
    ("Sapphire", 7, 17, {"Cosmic rune": 1, "Water rune": 1, "Mind rune": 1}),
    ("Jade", 14, 19, {"Cosmic rune": 1, "Earth rune": 2}),
    ("Pearl", 24, 29, {"Cosmic rune": 1, "Water rune": 2}),
    ("Emerald", 27, 37, {"Cosmic rune": 1, "Air rune": 3, "Nature rune": 1}),
    ("Topaz", 29, 33, {"Cosmic rune": 1, "Fire rune": 2}),
    ("Ruby", 49, 59, {"Cosmic rune": 1, "Fire rune": 5, "Blood rune": 1}),
    ("Diamond", 57, 67, {"Cosmic rune": 1, "Earth rune": 10, "Law rune": 2}),
    ("Dragon", 68, 78, {"Cosmic rune": 1, "Earth rune": 15, "Soul rune": 1}),
    ("Onyx", 87, 97, {"Cosmic rune": 1, "Fire rune": 20, "Death rune": 1}),
):
    raw = f"{gem} bolts"
    _add(_spell(f"enchant_{gem.lower()}_bolts", f"Enchant {raw}", "standard", "Enchant bolts", level, xp, runes, "transform", requirements={raw: 10}, outputs={f"{gem} bolts (e)": 10}, source=BOLT_WIKI))


for element, level, xp in (("Water", 56, 56), ("Earth", 60, 70), ("Fire", 63, 73), ("Air", 66, 76)):
    _add(_spell(f"charge_{element.lower()}_orb", f"Charge {element} Orb", "standard", "Charge orbs", level, xp, {"Cosmic rune": 3, f"{element} rune": 30}, "transform", requirements={"Unpowered orb": 1}, outputs={f"{element} orb": 1}, source=f"{STANDARD_WIKI}; RuneScape Wiki Charge {element} Orb oldid=" + {"Air":"6587802","Water":"6587811","Earth":"6587805","Fire":"6587804"}[element]))


# Per-output targets keep inputs explicit and preserve stable selection IDs.
for ore, output, smith_level, smith_xp, req in (
    ("Copper ore", "Bronze bar", 1, 12.5, {"Copper ore": 1, "Tin ore": 1}),
    ("Iron ore", "Iron bar", 15, 12.5, {"Iron ore": 1}),
    ("Iron ore", "Steel bar", 30, 17.5, {"Iron ore": 1, "Coal": 2}),
    ("Silver ore", "Silver bar", 20, 13.7, {"Silver ore": 1}),
    ("Gold ore", "Gold bar", 40, 22.5, {"Gold ore": 1}),
    ("Mithril ore", "Mithril bar", 50, 30, {"Mithril ore": 1, "Coal": 4}),
    ("Adamantite ore", "Adamant bar", 70, 37.5, {"Adamantite ore": 1, "Coal": 6}),
    ("Runite ore", "Rune bar", 85, 50, {"Runite ore": 1, "Coal": 8}),
):
    _add(_spell(f"superheat_{output.lower().replace(' ', '_')}", f"Superheat {output}", "standard", "Conversions", 43, 53, {"Fire rune": 4, "Nature rune": 1}, "transform", requirements=req, outputs={output: 1}, source=SUPERHEAT_SOURCE, secondary_skill="smithing", secondary_xp=smith_xp, secondary_level=smith_level))

_add(
    _spell("bones_to_bananas", "Bones to Bananas", "standard", "Conversions", 15, 25, {"Water rune": 2, "Earth rune": 2, "Nature rune": 1}, "bones_conversion", outputs={"Banana": 1}, source=f"{STANDARD_WIKI}; RuneScape Wiki Bones to Bananas oldid=6586873", batch="all"),
    _spell("bones_to_peaches", "Bones to Peaches", "standard", "Conversions", 60, 65, {"Water rune": 4, "Earth rune": 2, "Nature rune": 2}, "bones_conversion", outputs={"Peach": 1}, quest_gate="mage_training_arena", source=f"{STANDARD_WIKI}; RuneScape Wiki Bones to Peaches oldid=6586898", batch="all"),
    _spell("telegrab_wine_of_zamorak", "Telegrab Wine of Zamorak", "standard", "Pure casts", 33, 43, {"Air rune": 1, "Law rune": 1}, "produce", outputs={"Wine of zamorak": 1}, source=TELEGRAB_WIKI),
    _spell("charge", "Charge", "standard", "Pure casts", 80, 180, {"Air rune": 3, "Fire rune": 3, "Blood rune": 3}, "charge", quest_gate="mage_arena", source=f"{CHARGE_WIKI}; {MAGE_ARENA_WIKI}"),
)


# Lunar functional and pure-cast ledger. Authentic inventory-wide semantics are
# represented by the named batch actions; their per-item secondary XP remains
# separate from the single audited Magic XP award.
_add(
    _spell("bake_pie", "Bake Pie", "lunar", "Lunar skilling", 65, 60, {"Astral rune": 1, "Fire rune": 5, "Water rune": 4}, "bake_pie", quest_gate="lunar_diplomacy", source=f"{LUNAR_WIKI}; RuneScape Wiki Bake Pie oldid=6587779", secondary_skill="cooking"),
    _spell("humidify", "Humidify", "lunar", "Lunar skilling", 68, 65, {"Astral rune": 1, "Water rune": 3, "Fire rune": 1}, "humidify", quest_gate="dream_mentor", source=f"{LUNAR_WIKI}; RuneScape Wiki Humidify oldid=6587438", batch="all"),
    _spell("hunter_kit", "Hunter Kit", "lunar", "Lunar skilling", 71, 70, {"Astral rune": 2, "Earth rune": 2}, "produce", outputs={"Noose wand": 1, "Butterfly net": 1, "Bird snare": 1, "Rabbit snare": 1, "Teasing stick": 1, "Unlit torch": 1, "Box trap": 1}, quest_gate="dream_mentor", source=f"{LUNAR_WIKI}; RuneScape Wiki Hunter Kit (spell) oldid=6587781"),
    _spell("superglass_make", "Superglass Make", "lunar", "Lunar skilling", 77, 78, {"Astral rune": 2, "Air rune": 10, "Fire rune": 6}, "superglass", quest_gate="lunar_diplomacy", source=f"{LUNAR_WIKI}; RuneScape Wiki Superglass Make oldid=6587788", batch="all", secondary_skill="crafting", secondary_xp=10),
    _spell("tan_leather", "Tan Leather", "lunar", "Lunar skilling", 78, 81, {"Astral rune": 2, "Fire rune": 5, "Body rune": 1}, "tan_leather", quest_gate="lunar_diplomacy", source=f"{LUNAR_WIKI}; RuneScape Wiki Make Leather oldid=6587732; closed contract batch of five", batch="five"),
    _spell("string_jewellery", "String Jewellery", "lunar", "Lunar skilling", 80, 87, {"Astral rune": 2, "Earth rune": 10, "Water rune": 5}, "string_jewellery", quest_gate="lunar_diplomacy", source=f"{LUNAR_WIKI}; RuneScape Wiki String Jewellery oldid=6587350", batch="all", secondary_skill="crafting", secondary_xp=4),
    _spell("magic_imbue", "Magic Imbue", "lunar", "Lunar skilling", 82, 86, {"Astral rune": 2, "Fire rune": 7, "Water rune": 7}, "magic_imbue", quest_gate="lunar_diplomacy", source=f"{LUNAR_WIKI}; RuneScape Wiki Magic Imbue oldid=6587782"),
)
for log, plank, coins in (("Logs", "Plank", 70), ("Oak logs", "Oak plank", 175), ("Teak logs", "Teak plank", 350), ("Mahogany logs", "Mahogany plank", 1050)):
    _add(_spell(f"plank_make_{log.lower().replace(' ', '_')}", f"Plank Make — {log}", "lunar", "Lunar skilling", 86, 90, {"Astral rune": 2, "Nature rune": 1, "Earth rune": 15}, "transform", requirements={log: 1, "Coins": coins}, outputs={plank: 1}, quest_gate="dream_mentor", source=f"{LUNAR_WIKI}; RuneScape Wiki Plank Make oldid=6587322", coin_cost=coins))

for target_id, name, level, xp, runes, gate, action, source in (
    ("cure_plant", "Cure Plant", 66, 60, {"Astral rune": 1, "Earth rune": 8}, "lunar_diplomacy", "pure", "RuneScape Wiki Cure Plant oldid=6587291"),
    ("monster_examine", "Monster Examine", 66, 61, {"Astral rune": 1, "Cosmic rune": 1, "Mind rune": 1}, "dream_mentor", "monster_examine", "RuneScape Wiki Monster Examine oldid=6587508"),
    ("npc_contact", "NPC Contact", 67, 63, {"Astral rune": 1, "Cosmic rune": 1, "Air rune": 2}, "lunar_diplomacy", "pure", "RuneScape Wiki NPC Contact oldid=6462073"),
    ("cure_me", "Cure Me", 71, 69, {"Astral rune": 2, "Cosmic rune": 2}, "lunar_diplomacy", "cure_me", LUNAR_WIKI),
    ("fertile_soil", "Fertile Soil", 83, 87, {"Astral rune": 3, "Nature rune": 2, "Earth rune": 15}, "lunar_diplomacy", "pure", "RuneScape Wiki Fertile Soil oldid=6587339"),
):
    _add(_spell(target_id, name, "lunar", "Pure casts", level, xp, runes, action, quest_gate=gate, source=f"{LUNAR_WIKI}; {source}"))


MAGIC_NOT_APPLICABLE = (
    "Teleother Lumbridge", "Teleother Falador", "Teleother Camelot",
    "Tele Group Moonclan", "Tele Group Waterbirth", "Tele Group Barbarian",
    "Tele Group Khazard", "Tele Group Fishing Guild", "Tele Group Catherby",
    "Tele Group Ice Plateau", "Cure Other", "Cure Group", "Heal Other",
    "Heal Group", "Stat Spy", "Stat Restore Pot Share", "Boost Potion Share",
    "Energy Transfer", "Vengeance Other", "Teleport Block",
)
MAGIC_DEPENDENCY_BLOCKED = (
    "Livid Farm spell set", "Cure Plant real Farming function",
    "Fertile Soil real Farming function", "Plank consumers", "Hunter Kit consumers",
    "Slayer staff acquisition",
)


def magic_targets_as_dict() -> Dict[str, dict]:
    return {target_id: dict(spec) for target_id, spec in MAGIC_TARGETS.items()}


def magic_extra_items_as_dict() -> Dict[str, dict]:
    names = {item for spec in MAGIC_TARGETS.values() for field in ("requirements", "outputs", "rune_cost") for item in spec.get(field, {})}
    names.update({"Peach"})
    return {
        name: {
            "category": "material",
            "source": "Magic target input/output; source is recorded on MAGIC_TARGETS",
            "stackable": name.endswith(" rune") or name == "Coins",
        }
        for name in sorted(names)
    }


@dataclass(frozen=True)
class CombatMagicSpell:
    id: str
    display_name: str
    spellbook: str
    level: int
    runes: Tuple[Tuple[str, int], ...]
    xp: float
    max_hit: int
    effect: str = ""
    effect_value: float = 0.0
    quest_gate: Optional[str] = None
    required_weapon: Optional[str] = None
    source: str = STANDARD_WIKI


def _combat(pid, name, book, level, runes, xp, hit, effect="", value=0.0, gate=None, weapon=None, source=STANDARD_WIKI):
    return CombatMagicSpell(pid, name, book, level, tuple(runes.items()), float(xp), int(hit), effect, float(value), gate, weapon, source)


STANDARD_COMBAT_GAPS = (
    _combat("wind_rush", "Wind Rush", "standard", 1, {"Air rune": 2}, 2.7, 1, source=f"{SPELLBOOK_SOURCE}: WIND_RUSH; {STANDARD_WIKI}"),
    _combat("confuse", "Confuse", "standard", 3, {"Water rune": 3, "Earth rune": 2, "Body rune": 1}, 13, 0, "attack_drain", .05),
    _combat("weaken", "Weaken", "standard", 11, {"Water rune": 3, "Earth rune": 2, "Body rune": 1}, 21, 0, "strength_drain", .05),
    _combat("curse", "Curse", "standard", 19, {"Water rune": 2, "Earth rune": 3, "Body rune": 1}, 29, 0, "defence_drain", .05),
    _combat("bind", "Bind", "standard", 20, {"Water rune": 3, "Earth rune": 3, "Nature rune": 2}, 30, 0, "freeze", 5),
    _combat("crumble_undead", "Crumble Undead", "standard", 39, {"Air rune": 2, "Earth rune": 2, "Chaos rune": 1}, 24.5, 15, "undead_only", source=STANDARD_WIKI),
    _combat("iban_blast", "Iban Blast", "standard", 50, {"Fire rune": 5, "Death rune": 1}, 61, 25, gate="underground_pass", weapon="Iban's staff"),
    _combat("snare", "Snare", "standard", 50, {"Water rune": 4, "Earth rune": 4, "Nature rune": 3}, 60, 3, "freeze", 10),
    _combat("magic_dart", "Magic Dart", "standard", 50, {"Mind rune": 4, "Death rune": 1}, 61, 15, weapon="Slayer staff", source="RuneScape Wiki Slayer Dart oldid=6003441 (2012-07-27)"),
    _combat("vulnerability", "Vulnerability", "standard", 66, {"Water rune": 5, "Earth rune": 5, "Soul rune": 1}, 76, 0, "defence_drain", .10),
    _combat("enfeeble", "Enfeeble", "standard", 73, {"Water rune": 8, "Earth rune": 8, "Soul rune": 1}, 83, 0, "strength_drain", .10),
    _combat("storm_of_armadyl", "Storm of Armadyl", "standard", 77, {"Armadyl rune": 1}, 70, 27, "defence_flat", 1, "ritual_of_the_mahjarrat", source="RuneScape Wiki Storm of Armadyl oldid=6497017 (2012-10-29)"),
    _combat("entangle", "Entangle", "standard", 79, {"Water rune": 5, "Earth rune": 5, "Nature rune": 4}, 89, 5, "freeze", 15),
    _combat("stun", "Stun", "standard", 80, {"Water rune": 12, "Earth rune": 12, "Soul rune": 1}, 90, 0, "attack_drain", .10),
    _combat("wind_surge", "Wind Surge", "standard", 81, {"Air rune": 7, "Death rune": 1, "Blood rune": 1}, 75, 22, source=f"{SPELLBOOK_SOURCE}: WIND_SURGE; {STANDARD_WIKI}"),
    _combat("water_surge", "Water Surge", "standard", 85, {"Air rune": 7, "Water rune": 10, "Death rune": 1, "Blood rune": 1}, 80, 24, source=f"{SPELLBOOK_SOURCE}: WATER_SURGE; {STANDARD_WIKI}"),
    _combat("earth_surge", "Earth Surge", "standard", 90, {"Air rune": 7, "Earth rune": 10, "Death rune": 1, "Blood rune": 1}, 85, 26, source=f"{SPELLBOOK_SOURCE}: EARTH_SURGE; {STANDARD_WIKI}"),
    _combat("fire_surge", "Fire Surge", "standard", 95, {"Air rune": 7, "Fire rune": 10, "Death rune": 1, "Blood rune": 1}, 90, 28, source=f"{SPELLBOOK_SOURCE}: FIRE_SURGE; {STANDARD_WIKI}"),
)
GOD_SPELLS = tuple(
    _combat(pid, name, "standard", 60, runes, 61, 20, effect, .05, "mage_arena", weapon, f"{SPELLBOOK_SOURCE}; {STANDARD_WIKI}; {MAGE_ARENA_WIKI}; {CHARGE_WIKI}")
    for pid, name, runes, effect, weapon in (
        ("saradomin_strike", "Saradomin Strike", {"Air rune": 4, "Fire rune": 2, "Blood rune": 2}, "prayer_drain", "Saradomin staff"),
        ("claws_of_guthix", "Claws of Guthix", {"Air rune": 4, "Fire rune": 1, "Blood rune": 2}, "defence_drain", "Guthix staff"),
        ("flames_of_zamorak", "Flames of Zamorak", {"Air rune": 1, "Fire rune": 4, "Blood rune": 2}, "magic_drain", "Zamorak staff"),
    )
)


_ANCIENT_ROWS = (
    ("smoke_rush",50,{"Air rune":1,"Fire rune":1,"Chaos rune":2,"Death rune":2},30,13,"poison",20),
    ("shadow_rush",52,{"Air rune":1,"Soul rune":1,"Chaos rune":2,"Death rune":2},31,14,"attack_drain",.10),
    ("blood_rush",56,{"Chaos rune":2,"Death rune":2,"Blood rune":1},33,15,"blood_heal",.25),
    ("ice_rush",58,{"Water rune":2,"Chaos rune":2,"Death rune":2},34,16,"freeze",5),
    ("smoke_burst",62,{"Air rune":2,"Fire rune":2,"Chaos rune":4,"Death rune":2},36,17,"poison",20),
    ("shadow_burst",64,{"Air rune":1,"Soul rune":2,"Chaos rune":4,"Death rune":2},37,18,"attack_drain",.10),
    ("blood_burst",68,{"Chaos rune":4,"Death rune":2,"Blood rune":2},39,21,"blood_heal",.25),
    ("ice_burst",70,{"Water rune":4,"Chaos rune":4,"Death rune":2},40,22,"freeze",10),
    ("smoke_blitz",74,{"Air rune":2,"Fire rune":2,"Blood rune":2,"Death rune":2},42,23,"poison",40),
    ("shadow_blitz",76,{"Air rune":2,"Soul rune":2,"Blood rune":2,"Death rune":2},43,24,"attack_drain",.15),
    ("blood_blitz",80,{"Death rune":2,"Blood rune":4},45,25,"blood_heal",.25),
    ("ice_blitz",82,{"Water rune":3,"Blood rune":2,"Death rune":2},46,26,"freeze",15),
    ("smoke_barrage",86,{"Air rune":4,"Fire rune":4,"Blood rune":2,"Death rune":4},48,27,"poison",40),
    ("shadow_barrage",88,{"Air rune":4,"Soul rune":3,"Blood rune":2,"Death rune":4},48,28,"attack_drain",.15),
    ("blood_barrage",92,{"Death rune":4,"Blood rune":4,"Soul rune":1},51,29,"blood_heal",.25),
    ("ice_barrage",94,{"Water rune":6,"Blood rune":2,"Death rune":4},52,30,"freeze",20),
)
ANCIENT_COMBAT_SPELLS = tuple(_combat(pid, pid.replace("_", " ").title(), "ancient", level, runes, xp, hit, effect, value, "desert_treasure", source=ANCIENT_WIKI) for pid, level, runes, xp, hit, effect, value in _ANCIENT_ROWS)

# Miasmics are part of the pinned pre-EOC Ancient roster. Darkan supplies the
# exact levels, XP, damage, rune sets, Zuriel's staff gate, and 12/24/36/48s
# attack-speed slowdown in CombatSpell.kt:426-478.
DARKAN_COMBAT_SPELLS = "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/combat/CombatSpell.kt"
MIASMIC_COMBAT_SPELLS = tuple(
    _combat(pid, pid.replace("_", " ").title(), "ancient", level, runes, xp, hit,
            "attack_slow", duration, "desert_treasure", "Zuriel's staff",
            f"{DARKAN_COMBAT_SPELLS}:{line}; {ANCIENT_WIKI}")
    for pid, level, runes, xp, hit, duration, line in (
        ("miasmic_rush", 61, {"Soul rune": 1, "Chaos rune": 2, "Earth rune": 1}, 36, 18, 12, 426),
        ("miasmic_burst", 73, {"Soul rune": 2, "Chaos rune": 4, "Earth rune": 2}, 42, 24, 24, 439),
        ("miasmic_blitz", 85, {"Soul rune": 3, "Blood rune": 2, "Earth rune": 1}, 48, 28, 36, 452),
        ("miasmic_barrage", 97, {"Soul rune": 4, "Blood rune": 4, "Earth rune": 4}, 54, 32, 48, 465),
    )
)


COMBAT_MAGIC_ADDITIONS = STANDARD_COMBAT_GAPS + GOD_SPELLS + ANCIENT_COMBAT_SPELLS + MIASMIC_COMBAT_SPELLS


def combat_magic_additions_as_dict() -> Dict[str, dict]:
    return {
        spell.id: {
            "display_name": spell.display_name, "spellbook": spell.spellbook,
            "required_magic_level": spell.level, "rune_cost": dict(spell.runes),
            "max_hit_old_hp": spell.max_hit, "base_magic_xp": spell.xp,
            "attack_speed": 5, "effect": spell.effect,
            "effect_value": spell.effect_value, "quest_gate": spell.quest_gate,
            "required_weapon": spell.required_weapon, "source": spell.source,
        }
        for spell in COMBAT_MAGIC_ADDITIONS
    }


SPELLBOOK_SWAP_COST = {"Astral rune": 3, "Cosmic rune": 2, "Law rune": 1}
# Four astral, ten earth, and two death runes; level 94 and Lunar/Dream Mentor
# gates are enforced by the combat preset translator. Source: VENGEANCE_WIKI.
VENGEANCE_COST = {"Astral rune": 4, "Earth rune": 10, "Death rune": 2}
DREAM_COST = {"Astral rune": 2, "Cosmic rune": 1, "Body rune": 5}
# Dream restores 50 life points/minute (old HP: 5/minute). One review pays one
# cast and advances one five-old-HP healing chunk: a documented AnkiScape knob.
DREAM_HEAL_OLD_HP_PER_REVIEW = 5


CASUAL_MAGIC_DIAL = {
    "balanced": {"prayer_uptime": "40", "vengeance": False, "dream": False},
    "max_output": {"prayer_uptime": "70", "vengeance": True, "dream": False},
    "max_safety": {"prayer_uptime": "40", "vengeance": False, "dream": True},
}
