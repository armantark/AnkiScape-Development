"""The 2012 tool belt: the tools a player never has to carry.

Source: RuneScape Wiki "Tool belt", oldid 6538396 (2012-11-06). The belt
released on 6 December 2011 with these 39 slots in four groups, and from
13 March 2012 every non-quest tool was added automatically, so skills,
quests, Farming and Vinesweeper treat a listed tool as present without
ownership. The pickaxe and hatchet keep AnkiScape's explicit Bank attach
path, which also accepts the upgrades the 2012 belt refused.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

TOOL_BELT_GROUPS = (
    (
        "General",
        (
            "Bronze pickaxe",
            "Hammer",
            "Chisel",
            "Bronze hatchet",
            "Knife",
            "Tinderbox",
            "Saw",
            "Pestle and mortar",
            "Machete",
            "Watch",
            "Chart",
            "Shears",
            "Noose wand",
        ),
    ),
    (
        "Fishing",
        (
            "Crayfish cage",
            "Fishing rod",
            "Small fishing net",
            "Big fishing net",
            "Fly fishing rod",
            "Harpoon",
            "Lobster pot",
            "Barbarian rod",
        ),
    ),
    (
        "Crafting",
        (
            "Needle",
            "Glassblowing pipe",
            "Amulet mould",
            "Bracelet mould",
            "Necklace mould",
            "Ring mould",
            "Tiara mould",
            "Ammo mould",
            "Bolt mould",
            "Holy mould",
            "Unholy mould",
            "Sickle mould",
            "Chain link mould",
        ),
    ),
    ("Farming", ("Rake", "Seed dibber", "Spade", "Gardening trowel", "Secateurs")),
)

_ATTACHED_TOOLS = frozenset({"Bronze pickaxe", "Bronze hatchet"})
ALWAYS_ON_TOOL_BELT = frozenset(
    name for _group, names in TOOL_BELT_GROUPS for name in names if name not in _ATTACHED_TOOLS
)
_ATTACH_FAMILY_BY_TOOL = {"pickaxe": "mining", "hatchet": "woodcutting", "axe": "woodcutting"}

# Quest steps where a belt tool did not work in 2012, so the tool must sit in
# the Bank. The same wiki revision names the Horror from the Deep lighthouse,
# the Shilo Village bone key and the Tai Bwo Wannai Trio knife, and says a belt
# spade "can't be used for digging at the ground". The ground digs are the
# steps Darkan resolves through the carried spade's Dig option (Spade.kt,
# LunarDiplomacy.kt "non-toolbelt spade", OlafsQuest.kt "carried spade",
# DefenderOfVarrock.kt "physical spade") or that dig at a clue or coordinate
# spot. Darkan's Great Brain Robbery hands the "carried hammer" to Dr
# Fenkenstrain (GreatBrainRobbery.kt:135,466).
QUEST_STAGES_NEEDING_HELD_TOOLS = {
    ("horror_from_the_deep", 5): ("Tinderbox",),
    ("shilo_village", 7): ("Chisel",),
    ("tai_bwo_wannai_trio", 4): ("Knife",),
    ("the_great_brain_robbery", 1): ("Hammer",),
    ("a_void_dance", 3): ("Spade",),
    ("defender_of_varrock", 3): ("Spade",),
    ("do_no_evil", 5): ("Spade",),
    ("ghosts_ahoy", 1): ("Spade",),
    ("lunar_diplomacy", 1): ("Spade",),
    ("making_history", 1): ("Spade",),
    ("olafs_quest", 1): ("Spade",),
    ("pirates_treasure", 3): ("Spade",),
    ("plague_city", 4): ("Spade",),
    ("ritual_of_the_mahjarrat", 5): ("Spade",),
}


def tool_on_belt(player_data: Mapping[str, Any], tool_name: str) -> bool:
    if tool_name in ALWAYS_ON_TOOL_BELT:
        return True
    family = _ATTACH_FAMILY_BY_TOOL.get(tool_name.lower())
    toolbelt = player_data.get("toolbelt")
    if family is None or not isinstance(toolbelt, Mapping):
        return False
    attached = toolbelt.get(family, ())
    if isinstance(attached, str):
        attached = (attached,)
    return isinstance(attached, Iterable) and any(str(tool) for tool in attached)
