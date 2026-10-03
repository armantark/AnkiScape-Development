"""Lock reasons for Stats skill-guide rows.

Each skill's guide asks the same availability predicate its target list uses,
so a quest, material, tool, or region wall dims the guide row exactly when it
greys the list row.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from ..data.construction_data import NAIL_DATA, ROOM_DATA, SERVANT_DATA, WORKBENCH_TIERS
from ..data.thieving_data import THIEVING_TARGETS
from ..logic.agility_logic import agility_target_locked_reasons_pure
from ..logic.slayer_logic import slayer_family_locked_reasons_pure
from ..logic.summoning_logic import summoning_action_locked_reasons_pure
from ..logic_pure.logic_pure_construction import construction_target_locked_reasons_pure
from ..logic_pure.logic_pure_gathering import (
    fishing_method_locked_reasons_pure,
    hunter_target_locked_reasons_pure,
    mining_target_locked_reasons_pure,
    woodcutting_target_locked_reasons_pure,
)
from ..logic_pure.logic_pure_magic import magic_target_locked_reasons_pure
from ..logic_pure.logic_pure_prayer import prayer_target_locked_reasons_pure
from ..logic_pure.logic_pure_production import (
    cooking_target_locked_reasons_pure,
    crafting_target_locked_reasons_pure,
    firemaking_target_locked_reasons_pure,
    fletching_target_locked_reasons_pure,
    herblore_target_locked_reasons_pure,
)
from ..logic_pure.logic_pure_runecrafting import runecrafting_locked_reasons_pure
from ..logic_pure.logic_pure_smithing import smithing_target_locked_reasons_pure
from ..logic_pure.logic_pure_thieving import thieving_target_locked_reasons_pure
from .constants import (
    ALCH_VALUES,
    CONSTRUCTION_DATA,
    COOKING_DATA,
    CRAFTING_DATA,
    FIREMAKING_DATA,
    FISHING_DATA,
    FLETCHING_DATA,
    HERBLORE_DATA,
    HUNTER_DATA,
    MAGIC_DATA,
    MINING_PICKAXE_DATA,
    ORE_DATA,
    PRAYER_DATA,
    QUEST_UNLOCK_RULES,
    RUNECRAFTING_DATA,
    RUNECRAFTING_POUCH_DATA,
    SMITHING_DATA,
    TREE_DATA,
    WOODCUTTING_AXE_DATA,
)

# Above every skill's cap, so a predicate never reports the skill's own level.
_OWN_LEVEL_CLEARED = 200

_PREDICATES: dict[str, Callable[[Mapping[str, object], str], tuple[str, ...]]] = {
    "mining": lambda pd, tid: mining_target_locked_reasons_pure(pd, tid, ORE_DATA, MINING_PICKAXE_DATA, QUEST_UNLOCK_RULES),
    "woodcutting": lambda pd, tid: woodcutting_target_locked_reasons_pure(pd, tid, TREE_DATA, WOODCUTTING_AXE_DATA, QUEST_UNLOCK_RULES),
    "smithing": lambda pd, tid: smithing_target_locked_reasons_pure(pd, tid, SMITHING_DATA, QUEST_UNLOCK_RULES),
    "crafting": lambda pd, tid: crafting_target_locked_reasons_pure(pd, tid, CRAFTING_DATA, QUEST_UNLOCK_RULES),
    "fletching": lambda pd, tid: fletching_target_locked_reasons_pure(pd, tid, FLETCHING_DATA, QUEST_UNLOCK_RULES),
    "firemaking": lambda pd, tid: firemaking_target_locked_reasons_pure(pd, tid, FIREMAKING_DATA, QUEST_UNLOCK_RULES),
    "fishing": lambda pd, tid: fishing_method_locked_reasons_pure(pd, tid, FISHING_DATA, QUEST_UNLOCK_RULES),
    "hunter": lambda pd, tid: hunter_target_locked_reasons_pure(pd, tid, HUNTER_DATA, QUEST_UNLOCK_RULES),
    "cooking": lambda pd, tid: cooking_target_locked_reasons_pure(pd, tid, COOKING_DATA, QUEST_UNLOCK_RULES),
    "runecrafting": lambda pd, tid: runecrafting_locked_reasons_pure(pd, tid, RUNECRAFTING_DATA, RUNECRAFTING_POUCH_DATA, QUEST_UNLOCK_RULES),
    "herblore": lambda pd, tid: herblore_target_locked_reasons_pure(pd, tid, HERBLORE_DATA, QUEST_UNLOCK_RULES),
    "prayer": lambda pd, tid: prayer_target_locked_reasons_pure(pd, tid, PRAYER_DATA),
    "magic": lambda pd, tid: magic_target_locked_reasons_pure(pd, tid, MAGIC_DATA, ALCH_VALUES),
    "construction": lambda pd, tid: construction_target_locked_reasons_pure(pd, tid, CONSTRUCTION_DATA, ROOM_DATA, SERVANT_DATA, NAIL_DATA, WORKBENCH_TIERS),
    "thieving": lambda pd, tid: thieving_target_locked_reasons_pure(pd, tid, THIEVING_TARGETS),
    "agility": agility_target_locked_reasons_pure,
    "summoning": summoning_action_locked_reasons_pure,
}


def _own_level_cleared(player_data: Mapping[str, object], skill_id: str) -> dict[str, object]:
    return {**player_data, f"{skill_id}_level": _OWN_LEVEL_CLEARED}


def guide_target_lock_reasons_pure(
    player_data: Mapping[str, object],
    skill_id: str,
    target_id: str,
) -> tuple[str, ...]:
    """Why the target list greys this target, apart from the skill's own level.

    The guide already marks the skill's own level with the row badge and the
    current-level divider, and it uses the boosted level; a base-level reason
    here would dim a row the player can train.
    """

    predicate = _PREDICATES.get(skill_id)
    if predicate is None:
        return ()
    return tuple(predicate(_own_level_cleared(player_data, skill_id), target_id))


def guide_slayer_family_lock_reasons_pure(player_data: Mapping[str, object], family) -> tuple[str, ...]:
    return slayer_family_locked_reasons_pure(_own_level_cleared(player_data, "slayer"), family)
