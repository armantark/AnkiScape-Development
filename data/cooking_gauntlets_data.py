"""Family Crest gauntlet equipment identities for Cooking automation."""

from __future__ import annotations

from .equipment_data import EquipmentBonuses, EquipmentItem


FAMILY_GAUNTLET_ITEMS = (
    "Family gauntlets",
    "Cooking gauntlets",
    "Goldsmith gauntlets",
    "Chaos gauntlets",
)
FAMILY_GAUNTLET_ENCHANTMENTS = {
    "family": "Family gauntlets",
    "cooking": "Cooking gauntlets",
    "goldsmith": "Goldsmith gauntlets",
    "chaos": "Chaos gauntlets",
}
FAMILY_GAUNTLET_ITEM_IDS = {
    "Cooking gauntlets": 775,
    "Goldsmith gauntlets": 776,
    "Chaos gauntlets": 777,
    "Family gauntlets": 778,
}
FAMILY_GAUNTLET_SOURCE = (
    "RuneScape Wiki Cooking gauntlets oldid=6556123; Family Crest quest sources; "
    "audited item definitions 775-778"
)


def cooking_gauntlets_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    return {
        item_name: EquipmentItem(
            item_name=item_name,
            slot="hands",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="family_crest_gauntlets",
            bonuses=EquipmentBonuses(
                attack_stab=2,
                attack_slash=2,
                attack_crush=2,
                defence_stab=8,
                defence_slash=9,
                defence_crush=7,
                melee_strength=2,
            ),
            attack_speed=4,
            source_item_id=item_id,
            source=FAMILY_GAUNTLET_SOURCE,
            source_status="period wiki and audited item definition",
        )
        for item_name, item_id in FAMILY_GAUNTLET_ITEM_IDS.items()
    }
