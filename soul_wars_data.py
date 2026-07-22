"""Period Soul Wars values and disclosed bounded-match abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SOUL_WARS_ACTIVITY_ID = "soul_wars"
SOUL_WARS_COMBAT_TARGET_ID = "soul_wars_enemy_avatar"
SOUL_WARS_SOURCE = (
    "RuneScape Wiki Soul Wars oldid=6492038 (2012-10-28T23:10:20Z); "
    "Zeal oldid=6016139 (2012-07-30T16:05:49Z); "
    "Reward Shop (Soul Wars) oldid=6556242 (2012-11-15T04:47:44Z)"
)

SOUL_WARS_AVATAR_COMBAT_LEVEL = 525
SOUL_WARS_AVATAR_LIFEPOINTS = 10_000
SOUL_WARS_AVATAR_STARTING_SLAYER = 100
SOUL_WARS_ZEAL_CAP = 50_000
SOUL_WARS_ZEAL_BY_OUTCOME = {"loss": 1, "draw": 2, "win": 3}

# A source game lasts twenty minutes, but the source does not define a stable
# discrete action count. Twelve review beats are the disclosed event-scaled
# translation. The pressure values preserve a bounded two-team race without
# claiming historical per-action rates.
SOUL_WARS_EVENT_REVIEWS = 12
SOUL_WARS_ACTIVITY_MAX = 3
SOUL_WARS_CONTROL_LIMIT = 3
SOUL_WARS_CONTROL_DUTY_PROGRESS = 3
SOUL_WARS_CONTROL_HOLD_PROGRESS = 1
SOUL_WARS_OPPONENT_CONTROL_PROGRESS = 1
SOUL_WARS_TEAM_FRAGMENT_PRESSURE = 18
SOUL_WARS_OPPONENT_FRAGMENT_PRESSURE = 12
SOUL_WARS_TEAM_AVATAR_DAMAGE = 1_250
SOUL_WARS_OPPONENT_AVATAR_DAMAGE = 1_000
SOUL_WARS_TEAM_ATTACK_SLAYER = 70
SOUL_WARS_BONE_PRAYER_RESTORE = 10

SOUL_WARS_DUTIES = (
    ("fragments", "Gather and offer soul fragments"),
    ("control", "Capture and hold the Soul Obelisk"),
    ("avatar", "Attack the enemy avatar"),
    ("defend", "Bury bones and defend your avatar"),
)
SOUL_WARS_DUTY_IDS = tuple(duty_id for duty_id, _label in SOUL_WARS_DUTIES)
SOUL_WARS_TEAMS = (
    ("balance", "Join the team with fewer players"),
    ("creation", "Avatar of Creation"),
    ("destruction", "Avatar of Destruction"),
)
SOUL_WARS_TEAM_IDS = tuple(team_id for team_id, _label in SOUL_WARS_TEAMS)


@dataclass(frozen=True)
class SoulWarsCharmReward:
    item_name: str
    zeal_cost: int
    quantities: tuple[int, ...]


SOUL_WARS_COMBAT_LEVEL_BANDS = (
    (13, 74),
    (75, 82),
    (83, 99),
    (100, 108),
    (109, 124),
    (125, 136),
    (137, 138),
)
SOUL_WARS_CHARM_REWARDS = (
    SoulWarsCharmReward("Gold charm", 4, (6, 14, 24, 34, 41, 47, 52)),
    SoulWarsCharmReward("Green charm", 5, (4, 9, 15, 22, 27, 31, 34)),
    SoulWarsCharmReward("Crimson charm", 12, (4, 9, 15, 22, 26, 30, 34)),
    SoulWarsCharmReward("Blue charm", 30, (5, 9, 19, 22, 36, 41, 45)),
)
SOUL_WARS_CHARM_REWARDS_BY_ITEM = {
    reward.item_name: reward for reward in SOUL_WARS_CHARM_REWARDS
}


def soul_wars_charm_quantity_pure(item_name: str, combat_level: int) -> int:
    reward = SOUL_WARS_CHARM_REWARDS_BY_ITEM.get(str(item_name))
    level = max(0, min(int(combat_level), 138))
    if reward is None or level <= 12:
        return 0
    for index, (minimum, maximum) in enumerate(SOUL_WARS_COMBAT_LEVEL_BANDS):
        if minimum <= level <= maximum:
            return reward.quantities[index]
    return 0


def soul_wars_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        SOUL_WARS_ACTIVITY_ID: {
            "display_name": "Soul Wars",
            "requirements": {},
            "skill_requirements": {},
            "outputs": tuple(reward.item_name for reward in SOUL_WARS_CHARM_REWARDS),
            "batch_size": 1,
            "group": "minigames",
            "source": SOUL_WARS_SOURCE,
        }
    }


def soul_wars_avatar_enemy_pure() -> dict[str, Any]:
    return {
        "display_name": "Enemy team avatar",
        "level": SOUL_WARS_AVATAR_COMBAT_LEVEL,
        "group": "Soul Wars",
        "stats": {
            "attack": 99,
            "strength": 99,
            "defence": 99,
            "magic": 1,
            "ranged": 1,
            "hitpoints": SOUL_WARS_AVATAR_LIFEPOINTS,
        },
        "bonuses": {},
        "attack_style": "melee",
        "attack_speed": 4,
        "max_hit": 250,
        "xp_multiplier": 1.0,
        "drops": {"guaranteed": (), "tables": ()},
        "source": SOUL_WARS_SOURCE + "; bounded engaged-avatar combat abstraction",
    }
