"""Ancient Effigies stages, skill pairs and the Dragonkin lamp.

The values here are the settled period table: four stage items, the eight
ordered skill pairs, and the lamp's 25 selectable skills and exact formula.
Each value names the retained source that supplies it. The source copies live
in ``evidence/``; their ``saved_path`` fields are relative to
``EVIDENCE_ORIGINAL_ROOT``, where the originals were saved and hashed.

This module is data only. It must not import ``core.constants`` or the item
registry, because the registry imports it.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


EVIDENCE_ORIGINAL_ROOT = (
    "/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/"
    "1520-ancient-effigies-own-level-progression"
)
_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_DIR = os.path.join(_PACKAGE_DIR, "evidence")
ASSET_DIR = os.path.join(_PACKAGE_DIR, "assets")
# All four stages share one period inventory image.
EFFIGY_ASSET_PATH = os.path.join(ASSET_DIR, "ancient_effigy.png")
LAMP_ASSET_PATH = os.path.join(ASSET_DIR, "dragonkin_lamp.png")
EFFIGY_ASSET_SHA256 = "c9440cab86a55e6169c9f6bf26c8220b96ff48b8451d2a3e4bd25217f7d564f2"
LAMP_ASSET_SHA256 = "f99260fb6c82e144c2179d62465804d3193e3a37838b81d025acd65c98caf522"
EFFIGY_ASSET_UPLOADED_UTC = "2011-11-17T09:49:30Z"
LAMP_ASSET_UPLOADED_UTC = "2011-11-20T06:50:54Z"

STARVED_EFFIGY_ID = 18778
NOURISHED_EFFIGY_ID = 18779
SATED_EFFIGY_ID = 18780
GORGED_EFFIGY_ID = 18781
DRAGONKIN_LAMP_ID = 18782
DRAGONKIN_LAMP_NAME = "Dragonkin lamp"


@dataclass(frozen=True)
class EffigyStage:
    item_id: int
    name: str
    required_level: int
    # Experience in the one selected skill. Kept apart from the registry's
    # generic base_exp, which means ordinary training XP.
    reward_xp: int
    output_item_id: int
    output_name: str


# Sources: A:94-97, J:653-656 and 661, TI:373-393; IDs DK:39 and cache C.
STAGES: tuple[EffigyStage, ...] = (
    EffigyStage(STARVED_EFFIGY_ID, "Starved ancient effigy", 91, 15000, NOURISHED_EFFIGY_ID, "Nourished ancient effigy"),
    EffigyStage(NOURISHED_EFFIGY_ID, "Nourished ancient effigy", 93, 20000, SATED_EFFIGY_ID, "Sated ancient effigy"),
    EffigyStage(SATED_EFFIGY_ID, "Sated ancient effigy", 95, 25000, GORGED_EFFIGY_ID, "Gorged ancient effigy"),
    EffigyStage(GORGED_EFFIGY_ID, "Gorged ancient effigy", 97, 30000, DRAGONKIN_LAMP_ID, DRAGONKIN_LAMP_NAME),
)
STAGES_BY_ITEM_ID: dict[int, EffigyStage] = {stage.item_id: stage for stage in STAGES}
STAGE_ITEM_IDS: tuple[int, ...] = tuple(stage.item_id for stage in STAGES)
ITEM_NAMES_BY_ID: dict[int, str] = {
    **{stage.item_id: stage.name for stage in STAGES},
    DRAGONKIN_LAMP_ID: DRAGONKIN_LAMP_NAME,
}
ITEM_IDS_BY_NAME: dict[str, int] = {name: item_id for item_id, name in ITEM_NAMES_BY_ID.items()}

# Index order is part of the save format: records store an index into this
# tuple. Sources: A:119-141, J:608-645, TI:407-414; DK:37-38 orders them.
SKILL_PAIRS: tuple[tuple[str, str], ...] = (
    ("crafting", "agility"),
    ("construction", "thieving"),
    ("cooking", "firemaking"),
    ("farming", "fishing"),
    ("fletching", "woodcutting"),
    ("herblore", "hunter"),
    ("smithing", "mining"),
    ("runecrafting", "summoning"),
)

# The lamp's skill list in its retained supplying order (L:29, DL:78).
LAMP_SKILL_IDS: tuple[str, ...] = (
    "attack", "magic", "mining", "woodcutting", "agility", "fletching",
    "thieving", "strength", "ranged", "smithing", "firemaking", "herblore",
    "slayer", "construction", "defense", "prayer", "fishing", "crafting",
    "farming", "hunter", "summoning", "constitution", "dungeoneering",
    "cooking", "runecrafting",
)
LAMP_LEVEL_CAP = 99
DUNGEONEERING_LAMP_LEVEL_CAP = 120
LAMP_DESTROY_WARNING = (
    "Rub this lamp to claim your reward - it will be destroyed in the process. "
    "If you choose to destroy it now, you cannot replace it."
)


def lamp_level_cap(skill_id: str) -> int:
    """Highest level the lamp formula reads: 120 for Dungeoneering, else 99 (DS:653, DG:23)."""
    return DUNGEONEERING_LAMP_LEVEL_CAP if skill_id == "dungeoneering" else LAMP_LEVEL_CAP


def dragonkin_lamp_xp(level: int) -> int:
    """Exact lamp reward, floored once (L:36-38, TI:443, DL:204-205).

    RuneHQ (RH:269) gives level cubed over 20; A:99 and J:657 call that an
    approximation, so it is not used.
    """
    return (level**3 - 2 * level**2 + 100 * level) // 20


_STAGE_SOURCE = (
    "Ancient effigies oldid 6510644 (2012-10-31T13:23:42Z) lines 94-101; "
    "Jagex Ancient Effigy capture 20121009063538 lines 653-661; "
    "Tip.It Ancient Effigy capture 20120419054059 lines 372-393; "
    "item IDs from Darkan AncientEffigies.java:39 and six retained cache builds"
)
_LAMP_SOURCE = (
    "Dragonkin lamp oldid 6350210 (2012-10-05T11:47:40Z) lines 8-14, 22, 29, 32; "
    "item ID from Darkan AncientEffigies.java:39 and the retained cache builds"
)
_EFFIGY_LICENSE = (
    "RuneScape Wiki File:Ancient effigy.png, uploaded 2011-11-17T09:49:30Z; "
    "provenance in data/ancient_effigies/assets/provenance.json"
)
_LAMP_LICENSE = (
    "RuneScape Wiki File:Dragonkin lamp.png, uploaded 2011-11-20T06:50:54Z; "
    "provenance in data/ancient_effigies/assets/provenance.json"
)

# The five item definitions the registry overlays by storage key. Every one is
# untradeable, unstackable and unequipable (L:8-10; effigies per A:14).
ITEM_DEFINITION_ROWS: tuple[dict[str, object], ...] = (
    *(
        {
            "name": stage.name,
            "source_item_id": stage.item_id,
            "source": _STAGE_SOURCE,
            "license_note": _EFFIGY_LICENSE,
            "asset_path": EFFIGY_ASSET_PATH,
        }
        for stage in STAGES
    ),
    {
        "name": DRAGONKIN_LAMP_NAME,
        "source_item_id": DRAGONKIN_LAMP_ID,
        "source": _LAMP_SOURCE,
        "license_note": _LAMP_LICENSE,
        "asset_path": LAMP_ASSET_PATH,
    },
)


@dataclass(frozen=True)
class SourceRef:
    source_id: str
    title: str
    url: str
    revision: str
    timestamp_utc: str
    # Relative to EVIDENCE_ORIGINAL_ROOT.
    saved_path: str
    sha256: str
    # (original line number, literal original line)
    lines: tuple[tuple[int, str], ...]


# Literal supplying lines, copied from evidence/source-lines.md. Darkan rows
# are a modern reconstruction (AncientEffigies.java supplying edit
# 3a7f766de555d586cfa15109d3d6c0b03d9e93eb, own-level behavior restored by
# e50bbaa084d2168e5786a2c4fefda8f6e79c4c45), not the original server.
SOURCES: tuple[SourceRef, ...] = (
    SourceRef(
        source_id='A',
        title='Ancient effigies',
        url='https://runescape.wiki/w/Ancient_effigies?oldid=6510644',
        revision='6510644',
        timestamp_utc='2012-10-31T13:23:42Z',
        saved_path='sources/ancient-effigies-6510644.txt',
        sha256='f76b81ecfc9d92c7caba649ff788cf9b90d6807b53fbca71ba6b8e786226edcf',
        lines=(
            (10, 'When an effigy is nourished, the skills its next level needs are reset. For example, an effigy that first wants nourishment in Hunter or Herblore will next want nourishment in two different skills (say, Thieving and Construction).'),
            (94, '# [[Starved ancient effigy]] - This will require at least a level of 91 in one of the two skills to investigate; after investigation it becomes nourished, rewarding 15,000 experience in the skill used.'),
            (95, '# [[Nourished ancient effigy]] - This will require at least a level of 93 in one of the two skills to investigate; after investigation it becomes sated, rewarding 20,000 experience in the skill used.'),
            (96, '# [[Sated ancient effigy]] - This will require at least a level of 95 in one of the two skills to investigate; after investigation it becomes gorged, rewarding 25,000 experience in the skill used.'),
            (97, '# [[Gorged ancient effigy]] - This will require at least a level of 97 in one of the two skills to investigate; after investigation it provides 30,000 experience in the skill used and, then crumbles to dust, leaving behind a [[dragonkin lamp]].'),
            (99, 'The formula for the lamp is <math>\\frac{x^3-2x^2+100x}{20}</math>, in which <math>x</math> is the skill level. For example, at a skill level of 60, the experience gained would be <math>\\frac{60^3-2*60^2+100*60}{20}=10,740</math>. A complete table can be found [[Dragonkin lamp|here]]. A rough estimate of the exp gained can be found by simply cubing the level and then dividing by 20.'),
            (101, 'After players have enlightened an entire ancient effigy - from its starved form to its gorged form - they will have received a total of 90,000 experience across the skills used and a [[Dragonkin lamp]] which has the same use as a regular experience lamp but with a larger amount of experience depending upon the level in the skill used.'),
            (119, '| {{Skill clickpic|crafting}} [[Crafting]]'),
            (120, '| {{Skill clickpic|agility}} [[Agility]]'),
            (122, '| {{Skill clickpic|construction}} [[Construction]]'),
            (123, '| {{Skill clickpic|thieving}} [[Thieving]]'),
            (125, '| {{Skill clickpic|cooking}} [[Cooking]]'),
            (126, '| {{Skill clickpic|firemaking}} [[Firemaking]]'),
            (128, '| {{Skill clickpic|farming}} [[Farming]]'),
            (129, '| {{Skill clickpic|fishing}} [[Fishing]]'),
            (131, '| {{Skill clickpic|fletching}} [[Fletching]]'),
            (132, '| {{Skill clickpic|woodcutting}} [[Woodcutting]]'),
            (134, '| {{Skill clickpic|herblore}} [[Herblore]]'),
            (135, '| {{Skill clickpic|hunter}} [[Hunter]]'),
            (137, '| {{Skill clickpic|smithing}} [[Smithing]]'),
            (138, '| {{Skill clickpic|mining}} [[Mining]]'),
            (140, '| {{Skill clickpic|runecrafting}} [[Runecrafting]]'),
            (141, '| {{Skill clickpic|summoning}} [[Summoning]]'),
            (157, 'Note that only visible boosts can be used to open effigies.'),
        ),
    ),
    SourceRef(
        source_id='L',
        title='Dragonkin lamp',
        url='https://runescape.wiki/w/Dragonkin_lamp?oldid=6350210',
        revision='6350210',
        timestamp_utc='2012-10-05T11:47:40Z',
        saved_path='sources/dragonkin-lamp-6350210.txt',
        sha256='19be1abf94d1cc11fe2484835bc2f3901594d3aacc4553ad44a24148a7d7ce88',
        lines=(
            (8, '|tradeable = No'),
            (10, '|stackable = No'),
            (14, '|destroy = Rub this lamp to claim your reward - it will be destroyed in the process. If you choose to destroy it now, you cannot replace it.'),
            (22, "A '''Dragonkin lamp''' is the final reward from the [[Ancient Effigies]] [[Distraction and Diversion]]. Its name references the [[Dragonkin]], though their connection to this artefact is currently unknown. It is an easy way for players who only use combat to level non-combat skills. It is received after investigating a [[gorged ancient effigy]] and receiving experience from it. This will require a level of at least 97 in one of the two skills that the effigy craves knowledge in, or using an assist from a player who already has the required levels if you do not. The fastest way to get assistance is by posting in the dedicated thread on the official Runescape forums and asking for it. Like most xp lamps, the dragonkin lamp may '''not''' be banked."),
            (29, 'The dragonkin lamp can be used to gain experience in any skill. The amount of experience gained depends on the player\'s level in that skill (see calculator and chart below). After using a Dragonkin Lamp the player receives the message: "As you focus on your chosen memories, you feel a burning malevolence in the back of your mind. You have gained new insight into \'\'[skill]\'\'... but at what cost?". The significance of this message is unknown and could hint at a sinister aspect of the lamp\'s powers.     '),
            (36, "The '''exact''' experience gained is shown in the following table based on the following equation, where the floor function, <math>\\lfloor x \\rfloor</math>, means to round down to the nearest integer:"),
            (38, '<math>\\text{experience} = \\left \\lfloor \\frac{\\text{level}^3 - 2 \\times \\text{level}^2 + 100 \\times \\text{level}}{20}\\right \\rfloor</math>'),
        ),
    ),
    SourceRef(
        source_id='J',
        title='Jagex: Ancient Effigy',
        url='https://web.archive.org/web/20121009063538id_/http://services.runescape.com:80/m=rswiki/en/Ancient_Effigy',
        revision='20121009063538',
        timestamp_utc='2012-10-09T06:35:38Z',
        saved_path='sources/official-singular-20121009063538.html',
        sha256='2dd693577ad0ad6a0f656d4bbc12d4d12423a08387c3e31e54e4fd3252c64451',
        lines=(
            (608, '<td align="center"><a href="/m=rswiki/en/Crafting" title="Crafting">Crafting</a></td>'),
            (610, '<td align="center"><a href="/m=rswiki/en/Agility" title="Agility">Agility</a></td>'),
            (613, '<td align="center"><a href="/m=rswiki/en/Construction" title="Construction">Construction</a></td>'),
            (615, '<td align="center"><a href="/m=rswiki/en/Thieving" title="Thieving">Thieving</a></td>'),
            (618, '<td align="center"><a href="/m=rswiki/en/Cooking" title="Cooking">Cooking</a></td>'),
            (620, '<td align="center"><a href="/m=rswiki/en/Firemaking" title="Firemaking">Firemaking</a></td>'),
            (623, '<td align="center"><a href="/m=rswiki/en/Farming" title="Farming">Farming</a></td>'),
            (625, '<td align="center"><a href="/m=rswiki/en/Fishing" title="Fishing">Fishing</a></td>'),
            (628, '<td align="center"><a href="/m=rswiki/en/Fletching" title="Fletching">Fletching</a></td>'),
            (630, '<td align="center"><a href="/m=rswiki/en/Woodcutting" title="Woodcutting">Woodcutting</a></td>'),
            (633, '<td align="center"><a href="/m=rswiki/en/Herblore" title="Herblore">Herblore</a></td>'),
            (635, '<td align="center"><a href="/m=rswiki/en/Hunter" title="Hunter">Hunter</a></td>'),
            (638, '<td align="center"><a href="/m=rswiki/en/Smithing" title="Smithing">Smithing</a></td>'),
            (640, '<td align="center"><a href="/m=rswiki/en/Mining" title="Mining">Mining</a></td>'),
            (643, '<td align="center"><a href="/m=rswiki/en/Runecrafting" title="Runecrafting">Runecrafting</a></td>'),
            (645, '<td align="center"><a href="/m=rswiki/en/Summoning" title="Summoning">Summoning</a></td>'),
            (653, '<li><a href="/m=rswiki/en/Starved_ancient_effigy" title="Starved ancient effigy">Starved ancient effigies</a> require a skill level of at least 91 to investigate, and become nourished.</li>'),
            (654, '<li><a href="/m=rswiki/en/Nourished_ancient_effigy" title="Nourished ancient effigy">Nourished ancient effigies</a> require a skill level of at least 93 to investigate, and become sated.</li>'),
            (655, '<li><a href="/m=rswiki/en/Sated_ancient_effigy" title="Sated ancient effigy">Sated ancient effigiesrequire</a> a skill level of at least 95 to investigate, and become gorged.</li>'),
            (656, '<li><a href="/m=rswiki/en/Gorged_ancient_effigy" title="Gorged ancient effigy">Gorged ancient effigies</a> require a skill level of at least 97 to investigate, and will crumble to dust, producing a dragonkin lamp, their mysterious purpose fulfilled.</li>'),
            (657, '<li><a href="/m=rswiki/en/Dragonkin_lamp" title="Dragonkin lamp">Dragonkin lamps</a> may be spent on a skill and provide approximately  one-twentieth of the skill level cubed in experience (see the item article for a complete accurate table of values for each level).</li>'),
            (661, '<p>Each time you successfully investigate an ancient effigy, it will reward you with experience in the skill that you used to feed it. Starved effigies award 15,000XP; nourished effigies award 20,000XP; sated effigies award 25,000XP; and gorged effigies award 30,000XP.</p>'),
        ),
    ),
    SourceRef(
        source_id='TI',
        title='Tip.It: Ancient Effigy',
        url='https://web.archive.org/web/20120419054059id_/http://www.tip.it/runescape/?page=ancient_effigy.htm',
        revision='20120419054059',
        timestamp_utc='2012-04-19T05:40:59Z',
        saved_path='sources/tipit-old-20120419054059.html',
        sha256='785f5ce5949bd14f692179c31ebb46ba62a48ea58d6013b96f28a9f049726ba6',
        lines=(
            (361, '<p>Feeding an Effigy requires a certain pairing of skills, and each type of Effigy has a different skill level requirement. Having either one of the skills in the pairing at the required level is sufficient. For example, if an Effigy requires level 91 Mining or Smithing to investigate, having either skill at level 91 will allow you to do so. After feeding the Effigy, you will gain some experience, and it will either change into an Effigy of another type or crumble to dust and reveal a Dragonkin lamp. Note that if the Effigy changes type, the required skill pairing will change.</p>'),
            (373, '  <td>91</td>'),
            (374, '  <td><a href="?rs2item_id=10264">Nourished</a></td>'),
            (375, '  <td>15,000 XP</td>'),
            (379, '  <td>93</td>'),
            (380, '  <td><a href="?rs2item_id=10265">Sated</a></td>'),
            (381, '  <td>20,000 XP</td>'),
            (385, '  <td>95</td>'),
            (386, '  <td><a href="?rs2item_id=10266">Gorged</a></td>'),
            (387, '  <td>25,000 XP</td>'),
            (391, '  <td>97</td>'),
            (392, '  <td><a href="?rs2item_id=10267">Dragonkin lamp</a></td>'),
            (393, '  <td>30,000 XP</td>'),
            (407, '<tr><td>Crafting</td><td>Agility</td></tr>'),
            (408, '<tr><td>Construction</td><td>Thieving</td></tr>'),
            (409, '<tr><td>Cooking</td><td>Firemaking</td></tr>'),
            (410, '<tr><td>Farming</td><td>Fishing</td></tr>'),
            (411, '<tr><td>Fletching</td><td>Woodcutting</td></tr>'),
            (412, '<tr><td>Herblore</td><td>Hunter</td></tr>'),
            (413, '<tr><td>Smithing</td><td>Mining</td></tr>'),
            (414, '<tr><td>Runecrafting</td><td>Summoning</td></tr>'),
            (419, 'If a player feeds an Effigy until it crumbles to dust, they will receive a <a href="?rs2item_id=10267">Dragonkin lamp</a>. This lamp can be used to gain experience in a skill of your choice and cannot be banked. The exact amount of experience gained can be calculated with the formula <i>XP = (level^3 - 2 * level^2 + 100 * level) / 20</i>, where <i>level</i> is the level of the skill you wish to earn experience in.</p>'),
            (443, '  var xp = Math.floor((Math.pow(level,3) - 2 * Math.pow(level,2) + 100 * level) / 20);'),
            (446, "  printhtml = 'You will gain ' + outputComma(xp) + ' XP.';"),
        ),
    ),
    SourceRef(
        source_id='RH',
        title='RuneHQ: Ancient Effigies',
        url='https://web.archive.org/web/20120702024058id_/http://www.runehq.com:80/distraction/ancient-effigies',
        revision='20120702024058',
        timestamp_utc='2012-07-02T02:40:58Z',
        saved_path='sources/runehq-20120702024058.html',
        sha256='b77046a243d90002bd0bf03079a370fc9f5753dfa3d6dc0055be0404919cd4fc',
        lines=(
            (269, '<li><a href="/database.php?type=item&amp;id=20424">Gorged ancient effigy</a> - 30k experience in the skill you choose to feed it as well as a Dragonkin lamp, which gives experience (Level^3/20).</li>'),
        ),
    ),
    SourceRef(
        source_id='DK',
        title='src/main/java/com/rs/game/content/AncientEffigies.java',
        url='/Users/armantarkhanian/Documents/CodexWorktrees/.treehouse/darkan-world-server-0e01c4/2/darkan-world-server/src/main/java/com/rs/game/content/AncientEffigies.java',
        revision='517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed',
        timestamp_utc='2026-10-14T16:43:55Z',
        saved_path='sources/darkan-AncientEffigies.java.txt',
        sha256='77efd801a8de0503ad516881738b128e25201d98ff3c1874459c480d98d88d2a',
        lines=(
            (37, '\tpublic static final int[] SELF_SKILLS = { Constants.AGILITY, Constants.THIEVING, Constants.FIREMAKING, Constants.FISHING, Constants.WOODCUTTING, Constants.HUNTER, Constants.MINING, Constants.SUMMONING };'),
            (38, '\tpublic static final int[] ASSISTABLE_SKILLS = { Constants.CRAFTING, Constants.CONSTRUCTION, Constants.COOKING, Constants.FARMING, Constants.FLETCHING, Constants.HERBLORE, Constants.SMITHING, Constants.RUNECRAFTING };'),
            (39, '\tpublic static final int STARVED_ANCIENT_EFFIGY = 18778, NOURISHED_ANCIENT_EFFIGY = 18779, SATED_ANCIENT_EFFIGY = 18780, GORGED_ANCIENT_EFFIGY = 18781, DRAGONKIN_LAMP = 18782, MINAS_LAMP = 18783;'),
            (109, '\t\ttype = Utils.getRandomInclusive(7);'),
            (123, '\tpublic static int nextType(int currentType, int roll) {'),
            (124, '\t\tif (currentType < 0 || currentType >= SELF_SKILLS.length || roll < 0 || roll >= SELF_SKILLS.length - 1)'),
            (125, '\t\t\tthrow new IllegalArgumentException("Invalid effigy pair transition");'),
            (126, '\t\treturn roll >= currentType ? roll + 1 : roll;'),
            (172, '\t\tint nextItemId = item.getId() + 1;'),
            (173, '\t\tint nextType = nextType(currentType, Utils.getRandomInclusive(6));'),
            (174, '\t\tinventory.replace(item, new Item(nextItemId, 1).addMetaData(TYPE_KEY, nextType));'),
        ),
    ),
    SourceRef(
        source_id='DL',
        title='src/main/java/com/rs/game/content/items/Lamps.java',
        url='/Users/armantarkhanian/Documents/CodexWorktrees/.treehouse/darkan-world-server-0e01c4/2/darkan-world-server/src/main/java/com/rs/game/content/items/Lamps.java',
        revision='517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed',
        timestamp_utc='2026-09-30T01:17:20Z',
        saved_path='sources/darkan-Lamps.java.txt',
        sha256='3edbbcc3feaebc9781dff1b044422ef9a324e221bb1eebe67524e425386962a4',
        lines=(
            (78, '\tprivate static final int[] DIALOGUE_INTERFACE_CS2 = { Skills.ATTACK, Skills.MAGIC, Skills.MINING, Skills.WOODCUTTING, Skills.AGILITY, Skills.FLETCHING, Skills.THIEVING, Skills.STRENGTH, Skills.RANGE, Skills.SMITHING, Skills.FIREMAKING, Skills.HERBLORE, Skills.SLAYER, Skills.CONSTRUCTION, Skills.DEFENSE, Skills.PRAYER, Skills.FISHING, Skills.CRAFTING, Skills.FARMING, Skills.HUNTER, Skills.SUMMONING, Skills.HITPOINTS, Skills.DUNGEONEERING, Skills.COOKING, Skills.RUNECRAFTING };'),
            (146, '\t\t\tint lvl = player.getSkills().getLevelForXp(lamp.getSelectedSkill());'),
            (164, '\t\t\tif (lamp.getId() == 18782)'),
            (165, '\t\t\t\txpAmt = dragonkinLampXp(lvl);'),
            (204, '\tpublic static int dragonkinLampXp(int level) {'),
            (205, '\t\treturn (int) Math.floor((Math.pow(level, 3) - 2 * Math.pow(level, 2) + 100 * level) / 20.0);'),
        ),
    ),
    SourceRef(
        source_id='DS',
        title='src/main/java/com/rs/game/model/entity/player/Skills.java',
        url='/Users/armantarkhanian/Documents/CodexWorktrees/.treehouse/darkan-world-server-0e01c4/2/darkan-world-server/src/main/java/com/rs/game/model/entity/player/Skills.java',
        revision='517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed',
        timestamp_utc='2026-09-27T07:15:00Z',
        saved_path='sources/darkan-Skills.java.txt',
        sha256='6dcc260df69a90462b0bc54c5fec42e83d373c672cb16242b8bd2dfc561eeda0',
        lines=(
            (649, '\tpublic int getLevelForXp(int skill) {'),
            (653, '\t\tfor (int lvl = 1; lvl <= (skill == Constants.DUNGEONEERING ? 120 : 99); lvl++) {'),
            (660, '\t}'),
        ),
    ),
    SourceRef(
        source_id='DG',
        title='Dungeoneering',
        url='https://runescape.wiki/w/index.php?title=Dungeoneering&oldid=6579699&action=raw',
        revision='6579699',
        timestamp_utc='2012-11-19T02:31:37Z',
        saved_path='sources/dungeoneering-6579699.txt',
        sha256='e7a3b744db3d2d14c7e2c2e306e8f5e8c70d6c4a005d71ded6c7859861b30c64',
        lines=(
            (23, 'Players can train Dungeoneering past [[level 99]] up to [[level 120]], at which point players will have over 104 million experience. This new maximum level, which is only applied to Dungeoneering, is called "[[True Skill Mastery]]".'),
            (776, '*It has a maximum level of 120, whereas all other skills are capped at level 99.'),
        ),
    ),
    SourceRef(
        source_id='C',
        title='OpenRS2 effigy item/interface/enum fields',
        url='https://archive.openrs2.org/caches',
        revision='727/728/729/736/741/742',
        timestamp_utc='2012-07-24; 2012-08-01; 2012-08-11; 2012-10-09; 2012-11-04; 2012-11-07',
        saved_path='sources/openrs2-cache-727-742-ancient-effigies.json',
        sha256='4f29927f7adb8ff04e99b4990fd955572d222ebf3999fe7fce113d47a1e1cc99',
        lines=(),
    ),
    SourceRef(
        source_id='ART',
        title='File:Ancient effigy.png',
        url='https://runescape.wiki/images/archive/20140223053121%21Ancient_effigy.png?26cce',
        revision='2011-11-17T09:49:30Z',
        timestamp_utc='2011-11-17T09:49:30Z',
        saved_path='sources/media-ancient-effigy.png',
        sha256='c9440cab86a55e6169c9f6bf26c8220b96ff48b8451d2a3e4bd25217f7d564f2',
        lines=(),
    ),
    SourceRef(
        source_id='LART',
        title='File:Dragonkin lamp.png',
        url='https://runescape.wiki/images/archive/20140223053621%21Dragonkin_lamp.png?ccca9',
        revision='2011-11-20T06:50:54Z',
        timestamp_utc='2011-11-20T06:50:54Z',
        saved_path='sources/media-dragonkin-lamp.png',
        sha256='f99260fb6c82e144c2179d62465804d3193e3a37838b81d025acd65c98caf522',
        lines=(),
    ),
)
SOURCES_BY_ID: dict[str, SourceRef] = {source.source_id: source for source in SOURCES}
DARKAN_HEAD = "517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed"
DARKAN_EFFIGY_SUPPLYING_EDIT = "3a7f766de555d586cfa15109d3d6c0b03d9e93eb"
DARKAN_EFFIGY_OWN_LEVEL_RESTORE = "e50bbaa084d2168e5786a2c4fefda8f6e79c4c45"
