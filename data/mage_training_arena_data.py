"""Period-pinned Mage Training Arena rooms and representative reward shop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


MAGE_TRAINING_ARENA_ACTIVITY_ID = "mage_training_arena"
MAGE_TRAINING_ARENA_ROOM_IDS = (
    "telekinetic",
    "alchemist",
    "enchantment",
    "graveyard",
)
MAGE_TRAINING_ARENA_POINT_CAPS = {
    "telekinetic": 4_000,
    "alchemist": 8_000,
    "enchantment": 16_000,
    "graveyard": 4_000,
}
MAGE_TRAINING_ARENA_ROOM_LEVELS = {
    "telekinetic": 33,
    "alchemist": 21,
    "enchantment": 7,
    "graveyard": 15,
}
MAGE_TRAINING_ARENA_APPROACHES = (
    ("fast_rewards", "Fast rewards"),
    ("conserve_runes", "Conserve runes"),
)
MAGE_TRAINING_ARENA_ROOM_POLICIES = (
    ("auto", "Auto — selected reward"),
    ("telekinetic", "Telekinetic Theatre"),
    ("alchemist", "Alchemist's Playground"),
    ("enchantment", "Enchanting Chamber"),
    ("graveyard", "Creature Graveyard"),
)

MAGE_TRAINING_ARENA_SOURCE = (
    "RuneScape Wiki Mage Training Arena oldid=6491109 "
    "(2012-10-28T20:51:43Z); Beginner wand oldid=6021040; Apprentice wand "
    "oldid=5825592; Teacher wand oldid=5832254; Master wand oldid=6291896; "
    "RuneHQ Mage Training Arena guide updated 2012-07-01; rev-742 NPCs "
    "3097-3103 and items 6883-6926; Darkan MageTrainingArena.java at c95aca409; "
    "memory-bank/source-audits/mage-training-arena-source-readiness-2026-07-21.md"
)


@dataclass(frozen=True)
class MageTrainingArenaReward:
    id: str
    display_name: str
    costs: tuple[int, int, int, int]
    output_item: str = ""
    output_count: int = 1
    required_item: str = ""
    unlock: str = ""

    def cost_map(self) -> dict[str, int]:
        return dict(zip(MAGE_TRAINING_ARENA_ROOM_IDS, self.costs))


# Breadth-one keeps the rows that exercise ordinary items, the complete wand
# upgrade chain, a spell unlock, and a repeatable rune purchase. The exact
# four-column prices are from oldid 6491109.
MAGE_TRAINING_ARENA_REWARDS = (
    MageTrainingArenaReward("battlestaff", "Battlestaff", (1, 2, 20, 2), "Battlestaff"),
    MageTrainingArenaReward("beginner_wand", "Beginner wand", (30, 30, 300, 30), "Beginner wand"),
    MageTrainingArenaReward(
        "apprentice_wand",
        "Apprentice wand",
        (60, 60, 600, 60),
        "Apprentice wand",
        required_item="Beginner wand",
    ),
    MageTrainingArenaReward(
        "teacher_wand",
        "Teacher wand",
        (150, 200, 1_500, 150),
        "Teacher wand",
        required_item="Apprentice wand",
    ),
    MageTrainingArenaReward(
        "master_wand",
        "Master wand",
        (240, 240, 2_400, 240),
        "Master wand",
        required_item="Teacher wand",
    ),
    MageTrainingArenaReward(
        "bones_to_peaches",
        "Bones to Peaches",
        (200, 300, 2_000, 200),
        unlock="bones_to_peaches",
    ),
    MageTrainingArenaReward("cosmic_rune", "Cosmic rune", (0, 0, 5, 0), "Cosmic rune"),
)
MAGE_TRAINING_ARENA_REWARDS_BY_ID = {
    reward.id: reward for reward in MAGE_TRAINING_ARENA_REWARDS
}
MAGE_TRAINING_ARENA_DEFAULT_GOAL = "bones_to_peaches"

# A cadence opportunity is one natural room-switching checkpoint. The first
# three rates are period observations from the pinned readiness audit. The
# Enchantment section of the dated observation is truncated.
MAGE_TRAINING_ARENA_CHECKPOINT_RATES = {
    # 100 points/hour, with 18 points per five mazes: 250/9 mazes/hour.
    "telekinetic": (250, 9),
    "alchemist": (120, 1),
    # PLACEHOLDER(mage_training_arena.enchantment_shapes_per_hour): a dated complete Enchantment throughput observation
    "enchantment": (600, 1),
    "graveyard": (300, 1),
}

# The period page states the hazard and damage but not its server-side roll.
MAGE_TRAINING_ARENA_FALLING_BONE_CHANCE = 0.1  # PLACEHOLDER(mage_training_arena.falling_bone_chance): authentic falling-bone hazard roll

# The reward sets are exact; only the selector weights are unresolved.
MAGE_TRAINING_ARENA_ENCHANTMENT_REWARD_RUNES = (  # PLACEHOLDER(mage_training_arena.enchantment_orb_rune_weights): authentic Blood/Death/Cosmic selector weights
    "Blood rune",
    "Death rune",
    "Cosmic rune",
)
MAGE_TRAINING_ARENA_GRAVEYARD_REWARD_RUNES = (  # PLACEHOLDER(mage_training_arena.graveyard_reward_rune_weights): authentic Blood/Death/Earth/Water/Nature selector weights
    "Blood rune",
    "Death rune",
    "Earth rune",
    "Water rune",
    "Nature rune",
)
MAGE_TRAINING_ARENA_MAZE_MOVES = (7, 8, 9, 10)  # PLACEHOLDER(mage_training_arena.maze_move_distribution): authentic seven-to-ten-move maze distribution
MAGE_TRAINING_ARENA_ALCHEMY_CASTS_PER_POINT = 5  # PLACEHOLDER(mage_training_arena.alchemy_casts_per_point): authentic cupboard-value distribution per 100 deposited coins
MAGE_TRAINING_ARENA_ALCHEMY_NATURE_RUNES_PER_POINT = 3  # PLACEHOLDER(mage_training_arena.free_alchemy_frequency): authentic free-cast frequency within one 100-coin deposit

_MAGE_TRAINING_ARENA_EQUIPMENT_ROWS = (
    ("Progress hat", 6885, "head", 1, 0, 0),
    ("Beginner wand", 6908, "weapon", 45, 5, 0),
    ("Apprentice wand", 6910, "weapon", 50, 10, 0),
    ("Teacher wand", 6912, "weapon", 55, 15, 0),
    ("Master wand", 6914, "weapon", 60, 20, 10),
)

MAGE_TRAINING_ARENA_ASSET_MANIFEST = (
    {
        "item_name": "Mage Training Arena",
        "wiki_title": "Infinity hat.png",
        "output_path": "activityicons/mage_training_arena.png",
        "size": 64,
    },
    *(
        {
            "item_name": item_name,
            "wiki_title": f"{item_name}.png",
            "output_path": "activityitems/mage_training_arena_"
            + item_name.lower().replace(" ", "_")
            + ".png",
            "size": 64,
        }
        for item_name in (
            "Beginner wand",
            "Apprentice wand",
            "Teacher wand",
            "Master wand",
        )
    ),
)


def mage_training_arena_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        MAGE_TRAINING_ARENA_ACTIVITY_ID: {
            "display_name": "Mage Training Arena",
            "requirements": {},
            "skill_requirements": {"magic": 7},
            "outputs": tuple(
                reward.output_item
                for reward in MAGE_TRAINING_ARENA_REWARDS
                if reward.output_item
            ),
            "batch_size": 1,
            "group": "minigames",
            "source": MAGE_TRAINING_ARENA_SOURCE,
        }
    }


def mage_training_arena_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        item_name: {
            "category": "equipment",
            "source_item_id": item_id,
            "stackable": False,
            "tradeable": item_name != "Progress hat",
            "equipment_slot": slot,
            "source": MAGE_TRAINING_ARENA_SOURCE,
        }
        for item_name, item_id, slot, _level, _attack, _damage in _MAGE_TRAINING_ARENA_EQUIPMENT_ROWS
    }


def mage_training_arena_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    return {
        item_name: EquipmentItem(
            item_name=item_name,
            slot=slot,
            combat_skill="magic" if slot == "weapon" else None,
            required_level=required_level,
            two_handed=False,
            equipment_type="wand" if slot == "weapon" else "progress_hat",
            bonuses=EquipmentBonuses(
                attack_magic=magic_attack,
                magic_damage=magic_damage,
            ),
            attack_speed=4,
            source_item_id=item_id,
            source=MAGE_TRAINING_ARENA_SOURCE,
            source_status="pinned pre-cutoff item revision",
            skill_requirements=(
                (("magic", required_level),) if slot == "weapon" else ()
            ),
            weapon_type=18 if slot == "weapon" else -1,
        )
        for item_name, item_id, slot, required_level, magic_attack, magic_damage in _MAGE_TRAINING_ARENA_EQUIPMENT_ROWS
    }
