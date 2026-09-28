"""Pre-EOC training-urn data and source-backed action eligibility.

Runtime code imports only this checked-in module.  The pinned wiki revision is
used because rev-667 game-main implements urn Crafting but not charging or
teleport behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Optional, Tuple


URN_SOURCE = "RuneScape Wiki Urns oldid=6386501 (2012-10-11)"
URN_CRAFTING_SOURCE_ROOT = "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting"
URN_POTTERY_SOURCE = f"{URN_CRAFTING_SOURCE_ROOT}/pottery/PotteryData.kt"
URN_RUNE_SOURCE = f"{URN_CRAFTING_SOURCE_ROOT}/pottery/AddRuneAction.kt"
URN_ITEM_SOURCE = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
URN_SKILLS = ("mining", "cooking", "fishing", "woodcutting", "smithing", "prayer")
URN_CARRIED_TARGET_KEYS = {
    "mining": "current_ore",
    "cooking": "current_cooking",
    "fishing": "current_fishing",
    "woodcutting": "current_tree",
    "smithing": "current_smith",
    # Prayer urns charge from demon ashes in Combat, so their physical carried
    # target is the selected enemy rather than a Prayer training row.
    "prayer": "current_combat_target",
}
MAX_NONEMPTY_URNS_PER_SKILL = 10


@dataclass(frozen=True)
class UrnTier:
    id: str
    skill_id: str
    tier_name: str
    item_base: str
    source_enum: str
    crafting_level: int
    forming_xp: float
    firing_xp: float
    rune: str
    max_resource_level: Optional[int]
    capacity_base_xp: float
    teleport_xp: float
    members: bool
    item_unf: str
    item_nr: str
    item_r: str
    item_active: str
    item_full: str
    source_item_ids: Tuple[int, int, int, int, int]
    accepted_resource_ids: Tuple[str, ...] = ()
    excluded_resource_ids: Tuple[str, ...] = ()
    source: str = URN_SOURCE


def _tier(
    skill_id: str,
    tier_name: str,
    item_base: str,
    crafting_level: int,
    forming_xp: float,
    firing_xp: float,
    rune: str,
    max_resource_level: Optional[int],
    teleport_xp: float,
    *,
    members: bool = False,
    accepted_resource_ids: Tuple[str, ...] = (),
    excluded_resource_ids: Tuple[str, ...] = (),
    capacity_base_xp: Optional[float] = None,
    source_item_ids: Tuple[int, int, int, int, int],
) -> UrnTier:
    stable_tier = tier_name.lower().replace(" ", "_")
    source_enum_prefix = "SMELTING" if skill_id == "smithing" else skill_id.upper()
    return UrnTier(
        id=f"{skill_id}_{stable_tier}_urn",
        skill_id=skill_id,
        tier_name=tier_name,
        item_base=item_base,
        source_enum=f"{source_enum_prefix}_URNS",
        crafting_level=crafting_level,
        forming_xp=float(forming_xp),
        firing_xp=float(firing_xp),
        rune=rune,
        max_resource_level=max_resource_level,
        capacity_base_xp=float(capacity_base_xp if capacity_base_xp is not None else teleport_xp * 5.0),
        teleport_xp=float(teleport_xp),
        members=members,
        item_unf=f"{item_base} (unf)",
        item_nr=f"{item_base} (nr)",
        item_r=f"{item_base} (r)",
        item_active=item_base,
        item_full=f"{item_base} (full)",
        source_item_ids=source_item_ids,
        accepted_resource_ids=accepted_resource_ids,
        excluded_resource_ids=excluded_resource_ids,
    )


URN_TIERS: Tuple[UrnTier, ...] = (
    _tier("mining", "cracked", "Cracked mining urn", 1, 11.8, 16.8, "Earth rune", 1, 87.5, source_item_ids=(20379, 20380, 20382, 20383, 20384)),
    _tier("mining", "fragile", "Fragile mining urn", 17, 21.2, 31.8, "Earth rune", 20, 200, source_item_ids=(20385, 20386, 20388, 20389, 20390)),
    _tier("mining", "plain", "Mining urn", 32, 27.2, 40.8, "Earth rune", 40, 325, source_item_ids=(20391, 20392, 20394, 20395, 20396)),
    _tier("mining", "strong", "Strong mining urn", 48, 30.8, 49.2, "Earth rune", 55, 400, members=True, source_item_ids=(20397, 20398, 20400, 20401, 20402)),
    _tier("mining", "decorated", "Decorated mining urn", 59, 38.0, 57.0, "Earth rune", 85, 625, members=True, source_item_ids=(20403, 20404, 20406, 20407, 20408)),
    _tier("cooking", "cracked", "Cracked cooking urn", 2, 12.0, 18.0, "Fire rune", 10, 400, source_item_ids=(20349, 20350, 20352, 20353, 20354)),
    _tier("cooking", "fragile", "Fragile cooking urn", 12, 16.0, 24.0, "Fire rune", 25, 550, source_item_ids=(20355, 20356, 20358, 20359, 20360)),
    _tier("cooking", "plain", "Cooking urn", 36, 28.6, 42.8, "Fire rune", 40, 950, source_item_ids=(20361, 20362, 20364, 20365, 20366)),
    _tier("cooking", "strong", "Strong cooking urn", 51, 35.0, 52.5, "Fire rune", 55, 1050, members=True, source_item_ids=(20367, 20368, 20370, 20371, 20372)),
    _tier("cooking", "decorated", "Decorated cooking urn", 81, 52.0, 78.0, "Fire rune", 95, 1547.5, members=True, source_item_ids=(20373, 20374, 20376, 20377, 20378)),
    _tier("fishing", "cracked", "Cracked fishing urn", 2, 12.0, 18.0, "Water rune", 10, 150, source_item_ids=(20319, 20320, 20322, 20323, 20324)),
    _tier("fishing", "fragile", "Fragile fishing urn", 15, 20.0, 30.0, "Water rune", 30, 350, source_item_ids=(20325, 20326, 20328, 20329, 20330)),
    _tier("fishing", "plain", "Fishing urn", 41, 31.2, 46.8, "Water rune", 50, 500, source_item_ids=(20331, 20332, 20334, 20335, 20336)),
    _tier("fishing", "strong", "Strong fishing urn", 53, 36.0, 54.0, "Water rune", 70, 600, members=True, source_item_ids=(20337, 20338, 20340, 20341, 20342)),
    _tier("fishing", "decorated", "Decorated fishing urn", 76, 48.0, 72.0, "Water rune", 96, 1900, members=True, source_item_ids=(20343, 20344, 20346, 20347, 20348)),
    _tier("woodcutting", "cracked", "Cracked woodcutting urn", 4, 15.4, 23.1, "Earth rune", 10, 160, source_item_ids=(20295, 20296, 20298, 20299, 20300)),
    _tier("woodcutting", "fragile", "Fragile woodcutting urn", 15, 20.0, 30.0, "Earth rune", 35, 425, source_item_ids=(20301, 20302, 20304, 20305, 20306)),
    _tier("woodcutting", "plain", "Woodcutting urn", 44, 32.0, 48.0, "Earth rune", 58, 825, source_item_ids=(20307, 20308, 20310, 20311, 20312)),
    _tier("woodcutting", "strong", "Strong woodcutting urn", 61, 38.8, 58.2, "Earth rune", 75, 1662.5, members=True, source_item_ids=(20313, 20314, 20316, 20317, 20318)),
    _tier("smithing", "cracked", "Cracked smelting urn", 4, 15.4, 23.8, "Fire rune", 1, 40, excluded_resource_ids=("Gold bar", "Silver bar"), source_item_ids=(20271, 20272, 20274, 20275, 20276)),
    _tier("smithing", "fragile", "Fragile smelting urn", 17, 21.2, 31.8, "Fire rune", 20, 62.5, excluded_resource_ids=("Gold bar", "Silver bar"), source_item_ids=(20277, 20278, 20280, 20281, 20282)),
    _tier("smithing", "plain", "Smelting urn", 35, 28.0, 42.0, "Fire rune", 50, 150, excluded_resource_ids=("Gold bar", "Silver bar"), source_item_ids=(20283, 20284, 20286, 20287, 20288)),
    _tier("smithing", "strong", "Strong smelting urn", 49, 33.8, 50.8, "Fire rune", 85, 250, members=True, excluded_resource_ids=("Gold bar", "Silver bar"), source_item_ids=(20289, 20290, 20292, 20293, 20294)),
    _tier(
        "prayer", "impious", "Impious urn", 2, 12.0, 18.0, "Air rune", None, 120,
        accepted_resource_ids=("Impious ashes",), capacity_base_xp=100,
        source_item_ids=(20409, 20410, 20412, 20413, 20414),
    ),
    _tier(
        "prayer", "accursed", "Accursed urn", 26, 25.0, 37.5, "Air rune", None, 375,
        accepted_resource_ids=("Impious ashes", "Accursed ashes"), capacity_base_xp=312.5,
        source_item_ids=(20415, 20416, 20418, 20419, 20420),
    ),
    _tier(
        "prayer", "infernal", "Infernal urn", 62, 40.0, 60.0, "Air rune", None, 1875,
        members=True, accepted_resource_ids=("Impious ashes", "Accursed ashes", "Infernal ashes"),
        capacity_base_xp=1562.5, source_item_ids=(20421, 20422, 20424, 20425, 20426),
    ),
)

URN_TIERS_BY_ID = {tier.id: tier for tier in URN_TIERS}
URN_TIERS_BY_SKILL = {
    skill_id: tuple(tier for tier in URN_TIERS if tier.skill_id == skill_id)
    for skill_id in URN_SKILLS
}
URN_TIERS_BY_UNF_ITEM = {tier.item_unf: tier for tier in URN_TIERS}
URN_TIERS_BY_ACTIVE_ITEM = {tier.item_active: tier for tier in URN_TIERS}
URN_TIERS_BY_FULL_ITEM = {tier.item_full: tier for tier in URN_TIERS}
URN_TIERS_BY_STATE_ITEM = {
    item_name: tier
    for tier in URN_TIERS
    for item_name in (tier.item_r, tier.item_active, tier.item_full)
}
URN_PLAIN_TO_RUNED_ITEM = {tier.item_active: tier.item_r for tier in URN_TIERS}
URN_PHYSICAL_ITEM_NAMES = frozenset(
    item_name
    for tier in URN_TIERS
    for item_name in (tier.item_unf, tier.item_nr, tier.item_r, tier.item_active, tier.item_full)
)
# Runtime substitutions are limited to runed -> active -> full. Unfired and
# non-runed urns are ordinary Crafting inputs/outputs and keep normal overlay
# gain, Drop, and churn semantics.
URN_STATE_ITEM_NAMES = frozenset(
    item_name
    for tier in URN_TIERS
    for item_name in (tier.item_r, tier.item_active, tier.item_full)
)


def materialize_urn_layout_pure(inventory: Mapping[str, object], layout: Mapping[str, object]) -> dict:
    """Follow each saved urn slot through its runed -> active -> full states."""
    materialized = {
        str(item_name): _non_negative_int(amount)
        for item_name, amount in layout.items()
        if str(item_name) not in URN_TIERS_BY_STATE_ITEM and _non_negative_int(amount) > 0
    }
    requested_by_tier = {}
    for item_name, amount in layout.items():
        tier = URN_TIERS_BY_STATE_ITEM.get(str(item_name))
        if tier is not None:
            requested_by_tier[tier.id] = requested_by_tier.get(tier.id, 0) + _non_negative_int(amount)
    for tier_id, requested in requested_by_tier.items():
        tier = URN_TIERS_BY_ID[tier_id]
        remaining = requested
        # Keep the one charge-bearing object in the pack first, then full urns
        # awaiting teleport, then untouched runed urns.
        for item_name in (tier.item_active, tier.item_full, tier.item_r):
            count = min(remaining, _non_negative_int(inventory.get(item_name, 0)))
            if count > 0:
                materialized[item_name] = materialized.get(item_name, 0) + count
                remaining -= count
            if remaining <= 0:
                break
    return materialized

# The pinned table says "ore", "logs", "fish", "food", and smelted bars.
# These exact current actions are the source-closed subset of those nouns.
MINING_URN_SOURCE_BLOCKED_ACTIONS = frozenset(
    {"rune_essence", "clay", "limestone", "sandstone", "gem_rocks", "granite"}
)
MINING_URN_RESOURCE_LEVELS = {
    "copper": 1,
    "tin": 1,
    "blurite": 10,
    "iron": 15,
    "silver": 20,
    "coal": 30,
    "gold": 40,
    "mithril": 55,
    "adamantite": 70,
    "concentrated_coal": 77,
    "concentrated_gold": 80,
    "runite": 85,
}
WOODCUTTING_URN_SOURCE_BLOCKED_ACTIONS = frozenset({"hollow", "ivy"})
WOODCUTTING_URN_RESOURCE_LEVELS = {
    "tree": 1,
    "achey": 1,
    "oak": 15,
    "willow": 30,
    "teak": 35,
    "maple": 45,
    "mahogany": 50,
    "yew": 60,
    "magic": 75,
}
COOKING_URN_BLOCKED_ACTIONS = frozenset(
    {
        # Explicit oldid=6386501 exclusions and current non-food transformations.
        "cook_stew",
        "cook_curry",
        "render_beef_sinew",
        "render_bear_sinew",
        "gut_leaping_trout",
        "gut_leaping_salmon",
        "gut_leaping_sturgeon",
        "burn_seaweed",
    }
)
FISHING_URN_SOURCE_BLOCKED_OUTPUTS = frozenset({"Frog spawn"})
SMITHING_URN_ELIGIBLE_STATION = "furnace"


def default_urn_state_pure() -> dict:
    state = {}
    for skill_id in URN_SKILLS:
        state[f"active_urn_{skill_id}"] = ""
        state[f"urn_progress_{skill_id}"] = 0.0
    state.update(
        {
            "prayer_bonecrusher_triggers": 0,
            "prayer_ectoplasmator_triggers": 0,
            "prayer_urn_ashes_collected": 0,
            "prayer_urns_teleported": 0,
        }
    )
    return state


def _non_negative_int(value: object) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError, OverflowError):
        return 0


def _finite_non_negative_float(value: object) -> float:
    try:
        number = float(value or 0.0)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    return max(0.0, number) if isfinite(number) else 0.0


def _owns_partial_urn(player_data: Mapping[str, object], item_name: str) -> bool:
    inventory = player_data.get("inventory", {})
    if isinstance(inventory, Mapping) and _non_negative_int(inventory.get(item_name, 0)) > 0:
        return True
    for state_key in ("combat_grave", "death_office"):
        state = player_data.get(state_key, {})
        items = state.get("items", ()) if isinstance(state, Mapping) else ()
        if isinstance(items, (list, tuple)) and item_name in items:
            return True
    return False


def sanitize_urn_state_pure(player_data: Mapping[str, object]) -> dict:
    """Return valid flat urn pointers/progress and passive counters.

    A partial urn remains valid in the bank, grave, or Death's Office.
    Carried presence is an action-time rule, not a load-time ownership rule.
    """
    sanitized = default_urn_state_pure()
    for skill_id in URN_SKILLS:
        active_key = f"active_urn_{skill_id}"
        progress_key = f"urn_progress_{skill_id}"
        tier_id = str(player_data.get(active_key, "") or "")
        tier = URN_TIERS_BY_ID.get(tier_id)
        if tier is None or tier.skill_id != skill_id or not _owns_partial_urn(player_data, tier.item_active):
            continue
        sanitized[active_key] = tier.id
        sanitized[progress_key] = min(tier.capacity_base_xp, _finite_non_negative_float(player_data.get(progress_key, 0.0)))
    for counter_key in (
        "prayer_bonecrusher_triggers",
        "prayer_ectoplasmator_triggers",
        "prayer_urn_ashes_collected",
        "prayer_urns_teleported",
    ):
        sanitized[counter_key] = _non_negative_int(player_data.get(counter_key, 0))
    return sanitized


def urn_extra_items_as_dict() -> dict[str, dict]:
    items: dict[str, dict] = {}
    for tier in URN_TIERS:
        for item_name, source_item_id, tradeable in zip(
            (tier.item_unf, tier.item_nr, tier.item_r, tier.item_active, tier.item_full),
            tier.source_item_ids,
            (True, True, False, False, False),
        ):
            items[item_name] = {
                "category": "crafted",
                "tradeable": tradeable,
                "stackable": False,
                "source_item_id": source_item_id,
                "source": f"{tier.source}; {URN_ITEM_SOURCE}",
            }
    return items


def urn_tier_accepts_event_pure(tier: UrnTier, resource_id: str, resource_level: Optional[int]) -> bool:
    if tier.accepted_resource_ids and resource_id not in tier.accepted_resource_ids:
        return False
    if resource_id in tier.excluded_resource_ids:
        return False
    if tier.max_resource_level is not None:
        if resource_level is None or int(resource_level) > tier.max_resource_level:
            return False
    return True


def urn_action_event_pure(
    skill_id: str,
    action_id: str,
    action_spec: Mapping[str, object],
    base_xp: float,
    output_item: Optional[str] = None,
) -> Optional[tuple[str, int, float]]:
    """Return ``(resource_id, resource_level, base_xp)`` for source-closed actions."""
    if base_xp <= 0:
        return None
    if skill_id == "mining":
        if action_id in MINING_URN_SOURCE_BLOCKED_ACTIONS:
            return None
        level = MINING_URN_RESOURCE_LEVELS.get(action_id)
        return (action_id, level, float(base_xp)) if level is not None else None
    if skill_id == "woodcutting":
        if action_id in WOODCUTTING_URN_SOURCE_BLOCKED_ACTIONS or not output_item:
            return None
        level = WOODCUTTING_URN_RESOURCE_LEVELS.get(action_id)
        return (action_id, level, float(base_xp)) if level is not None else None
    if skill_id == "cooking":
        if action_id in COOKING_URN_BLOCKED_ACTIONS or not action_id.startswith("cook_"):
            return None
        return (action_id, int(action_spec.get("level", 1) or 1), float(base_xp))
    if skill_id == "smithing":
        if action_spec.get("station") != SMITHING_URN_ELIGIBLE_STATION or not output_item or not output_item.endswith(" bar"):
            return None
        return (output_item, int(action_spec.get("level", 1) or 1), float(base_xp))
    if skill_id == "fishing":
        if not output_item or output_item in FISHING_URN_SOURCE_BLOCKED_OUTPUTS:
            return None
        for fish in action_spec.get("fish", ()) or ():
            if isinstance(fish, Mapping) and fish.get("output_item") == output_item:
                return (output_item, int(fish.get("level", 1) or 1), float(base_xp))
    return None
