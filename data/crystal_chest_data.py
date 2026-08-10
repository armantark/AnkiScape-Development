"""Pre-EOC Crystal key and Taverley Crystal chest data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .equipment_data import EquipmentBonuses, EquipmentItem


CRYSTAL_CHEST_ACTIVITY_ID = "open_crystal_chest"
CRYSTAL_CHEST_KEY_SOURCE = "https://runescape.wiki/w/Crystal_key?oldid=6428315"
CRYSTAL_CHEST_LOOT_SOURCE = "https://runescape.wiki/w/Crystal_chest?oldid=6491268"
CRYSTAL_CHEST_TOTAL_WEIGHT = 10_000

# PLACEHOLDER(crystal_chest.ring_of_wealth_improvement): replace with a
# period server routine or measured cutoff-era modifier.
CRYSTAL_CHEST_RING_IMPROVEMENT_CHANCE = 0.25


@dataclass(frozen=True)
class CrystalChestReward:
    id: str
    weight: int
    outputs: Tuple[Tuple[str, int], ...]
    value_rank: int


CRYSTAL_CHEST_REWARDS: Tuple[CrystalChestReward, ...] = (
    CrystalChestReward(
        "spinach_roll",
        3969,
        (("Uncut dragonstone", 1), ("Spinach roll", 1), ("Coins", 2000)),
        2,
    ),
    CrystalChestReward("dragonstone_only", 1672, (("Uncut dragonstone", 1),), 0),
    CrystalChestReward(
        "runes",
        773,
        (
            ("Uncut dragonstone", 1),
            ("Air rune", 50),
            ("Water rune", 50),
            ("Earth rune", 50),
            ("Fire rune", 50),
            ("Mind rune", 50),
            ("Body rune", 50),
            ("Chaos rune", 10),
            ("Cosmic rune", 10),
            ("Death rune", 10),
            ("Nature rune", 10),
            ("Law rune", 10),
            ("Dust rune", 10),
            ("Lava rune", 10),
            ("Mist rune", 10),
            ("Mud rune", 10),
            ("Smoke rune", 10),
            ("Steam rune", 10),
        ),
        7,
    ),
    CrystalChestReward(
        "rune_bars",
        351,
        (("Uncut dragonstone", 1), ("Rune bar", 3)),
        11,
    ),
    CrystalChestReward(
        "coal",
        655,
        (("Uncut dragonstone", 1), ("Coal", 100)),
        8,
    ),
    CrystalChestReward(
        "iron_ore",
        275,
        (("Uncut dragonstone", 1), ("Iron ore", 150)),
        9,
    ),
    CrystalChestReward(
        "gems",
        423,
        (("Uncut dragonstone", 1), ("Ruby", 2), ("Diamond", 2)),
        6,
    ),
    CrystalChestReward(
        "swordfish",
        1057,
        (("Uncut dragonstone", 1), ("Raw swordfish", 5), ("Coins", 1000)),
        3,
    ),
    CrystalChestReward(
        "loop_half",
        326,
        (("Uncut dragonstone", 1), ("Loop half of a key", 1), ("Coins", 750)),
        4,
    ),
    CrystalChestReward(
        "tooth_half",
        367,
        (("Uncut dragonstone", 1), ("Tooth half of a key", 1), ("Coins", 750)),
        5,
    ),
    CrystalChestReward(
        "adamant_sq_shield",
        106,
        (("Uncut dragonstone", 1), ("Adamant sq shield", 1)),
        1,
    ),
    CrystalChestReward(
        "rune_platelegs",
        26,
        (("Uncut dragonstone", 1), ("Rune platelegs", 1)),
        10,
    ),
)


def crystal_chest_utility_spec() -> Dict[str, object]:
    return {
        "display_name": "Open Crystal chest",
        "requirements": {"Crystal key": 1},
        "output_item": "Uncut dragonstone",
        "output_qty": 1,
        "batch_size": 1,
        "random_reward_table": True,
        "group": "containers_opening",
        "source": f"{CRYSTAL_CHEST_KEY_SOURCE}; {CRYSTAL_CHEST_LOOT_SOURCE}",
    }


def crystal_chest_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    source = "OpenRS2 rev-742 item definitions; Crystal chest oldid 6491268"
    return {
        "Crystal key": {
            "category": "crafted",
            "source": source,
            "source_item_id": 989,
            "stackable": False,
            "tradeable": True,
        },
        "Uncut dragonstone": {
            "category": "gem",
            "source": source,
            "source_item_id": 1631,
            "stackable": False,
            "tradeable": True,
        },
        "Loop half of a key": {
            "category": "material",
            "source": source,
            "source_item_id": 987,
            "stackable": False,
            "tradeable": True,
        },
        "Tooth half of a key": {
            "category": "material",
            "source": source,
            "source_item_id": 985,
            "stackable": False,
            "tradeable": True,
        },
        "Spinach roll": {
            "category": "food",
            "source": source,
            "source_item_id": 1969,
            "stackable": False,
            "tradeable": False,
        },
        "Ruby": {
            "category": "crafted",
            "source": source,
            "source_item_id": 1603,
            "stackable": False,
            "tradeable": True,
        },
        "Diamond": {
            "category": "crafted",
            "source": source,
            "source_item_id": 1601,
            "stackable": False,
            "tradeable": True,
        },
        "Ring of wealth": {
            "category": "equipment",
            "source": source,
            "source_item_id": 2572,
            "stackable": False,
            "tradeable": True,
        },
    }


def crystal_chest_equipment_data_as_dict() -> Dict[str, EquipmentItem]:
    return {
        "Ring of wealth": EquipmentItem(
            item_name="Ring of wealth",
            slot="ring",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="ring",
            bonuses=EquipmentBonuses(),
            attack_speed=4,
            source_item_id=2572,
            source="OpenRS2 rev-742 item 2572",
            source_status="rev-742 item definition",
        )
    }
