"""Period-pinned item data for the Stronghold of Security landmark.

The step math lives in logic_pure_landmarks.py; only the reward items need a
registry seam. Both boots exist in the generated EQUIPMENT_DATA table, but
_apply_equipment_metadata only enriches names that already have an item row, so
without this module the completion reward lands in the bank as an unknown,
uncategorised item.
"""

from __future__ import annotations

from typing import Any

STRONGHOLD_OF_SECURITY_SOURCE = (
    "data/cfg/items.yml items 9005/9006; Stronghold of Security reward"
)


# Item ids match equipment_data.py, which was generated from the same items.yml
# rows. Both boots are the stat-identical completion choice.
STRONGHOLD_BOOT_ITEM_IDS = {
    "Fancy boots": 9005,
    "Fighting boots": 9006,
}


def stronghold_of_security_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        item_name: {
            "category": "equipment",
            "source_item_id": item_id,
            "stackable": False,
            "tradeable": False,
            "source": STRONGHOLD_OF_SECURITY_SOURCE,
        }
        for item_name, item_id in STRONGHOLD_BOOT_ITEM_IDS.items()
    }
