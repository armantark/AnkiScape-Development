"""Period cape slots, bonuses and wield gates for Ava's recovery devices."""

from dataclasses import replace

from ..equipment_data import EQUIPMENT_DATA, EquipmentBonuses


def ava_equipment_data_as_dict():
    base = EQUIPMENT_DATA["Ava's attractor"]
    devices = (("Ava's attractor", 10498, 30, 2, 0, 6528946),
               ("Ava's accumulator", 10499, 50, 4, 0, 6549921),
               ("Ava's alerter", 20068, 50, 5, 1, 6319486))
    return {
        name: replace(base, item_name=name, source_item_id=item_id,
                      combat_skill="ranged", required_level=level, skill_requirements=(("ranged", level),),
                      bonuses=EquipmentBonuses(attack_ranged=bonus, defence_magic=bonus, defence_slash=slash),
                      source=f"https://runescape.wiki/w/index.php?title={name.replace(' ', '_')}&oldid={oldid}",
                      source_status="pre-EOC worn bonuses; Pass 21 ammo-facts section A")
        for name, item_id, level, bonus, slash, oldid in devices
    }
