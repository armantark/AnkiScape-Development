"""Source-backed acquisition routes for early quest items."""

from __future__ import annotations

from pathlib import Path
from typing import Any


_ROOT = Path(__file__).resolve().parents[1]


DARKAN_REV = "6277992980582f7b3da3a48e722e96cfa5b0a57d"
DARKAN_ROOT = "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server"
UGTHANKI_DUNG_SOURCE = (
    "https://runescape.wiki/w/Ugthanki_dung?oldid=6288566; "
    f"{DARKAN_ROOT}/src/main/java/com/rs/game/content/quests/the_feud/TheFeud.kt "
    f"@ {DARKAN_REV}"
)
FISH_FOOD_SOURCE = (
    "https://runescape.wiki/w/Fish_food?oldid=6358390; "
    f"{DARKAN_ROOT}/data/items/spawns/spawns.json; "
    f"{DARKAN_ROOT}/src/main/java/com/rs/game/content/quests/ernestthechicken/"
    f"ErnestTheChicken.java @ {DARKAN_REV}"
)
INSECT_REPELLENT_SOURCE = (
    "https://runescape.wiki/w/Insect_repellent?oldid=5865450; "
    f"{DARKAN_ROOT}/src/main/java/com/rs/game/content/world/areas/catherby/npcs/"
    f"Beekeeper.java @ {DARKAN_REV}"
)
EVERGREEN_SAP_SOURCE = (
    "https://runescape.wiki/w/Bucket_of_sap?oldid=6288759; "
    "https://runescape.wiki/w/Evergreen?oldid=6310045"
)


def quest_item_acquisition_activities_as_dict() -> dict[str, dict[str, Any]]:
    return {
        "collect_evergreen_sap": {
            "display_name": "Collect evergreen sap",
            "icon_path": str(_ROOT / "questitems" / "bucket_of_sap.png"),
            "requirements": {"Bucket": 1},
            "required_items": {"Knife": 1},
            "output_item": "Bucket of sap",
            "output_qty": 1,
            "batch_size": 1,
            "group": "gathering",
            "source": EVERGREEN_SAP_SOURCE,
            "source_status": "pinned/period-wiki",
        },
        "collect_ugthanki_dung": {
            "display_name": "Collect Ugthanki dung",
            "icon_path": str(_ROOT / "questitems" / "bucket.png"),
            "requirements": {"Bucket": 1},
            "output_item": "Ugthanki dung",
            "output_qty": 1,
            "batch_size": 1,
            "group": "gathering",
            "source": UGTHANKI_DUNG_SOURCE,
            "source_status": "pinned/Darkan+period-wiki",
        },
        "collect_fish_food": {
            "display_name": "Collect fish food",
            "icon_path": str(_ROOT / "questitems" / "fish_food.png"),
            "requirements": {},
            "output_item": "Fish food",
            "output_qty": 1,
            "batch_size": 1,
            "group": "gathering",
            "source": FISH_FOOD_SOURCE,
            "source_status": "pinned/Darkan+period-wiki",
        },
        "collect_insect_repellent": {
            "display_name": "Collect insect repellent",
            "icon_path": str(_ROOT / "questitems" / "insect_repellent.png"),
            "requirements": {},
            "output_item": "Insect repellent",
            "output_qty": 1,
            "batch_size": 1,
            "group": "gathering",
            "source": INSECT_REPELLENT_SOURCE,
            "source_status": "pinned/Darkan+period-wiki",
        },
    }


def quest_item_acquisition_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        "Ugthanki dung": {
            "category": "material",
            "item_id": 4601,
            "stackable": False,
            "tradeable": False,
            "source": UGTHANKI_DUNG_SOURCE,
        }
    }
