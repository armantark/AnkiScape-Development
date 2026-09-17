"""Source-backed NPC service catalog used by the shop generator."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# Processing-type conversions (Ellis tanning, sawmill planks) are deliberately
# NOT shop services: 2011 tanning/plank runs were inventory-bounded (28
# unstackable items per bank run) and AnkiScape's review loop is the stand-in
# for that friction, so they live as no-XP Utility/Activities in constants.py
# (tan_soft_leather, tan_hard_leather, convert_logs_to_planks,
# convert_oak_logs_to_oak_planks) with the same Darkan source strings. An
# instant "Use x1000" shop service would delete source pacing. Bob Barter's
# inventory-wide potion consolidation is genuinely instantaneous and therefore
# belongs here rather than in Utility/Activities.
SERVICE_ROWS: list[dict[str, Any]] = [
    {
        "id": "blandebir_fill_ale_yeast",
        "display_name": "Fill pots with ale yeast",
        "provider": "Blandebir",
        "location": "Keldagrim",
        "currency_id": 995,
        "price": 25,
        "inputs": [
            {
                "item_id": 1931,
                "quantity": 1,
                "item_name": "Empty pot",
            }
        ],
        "outputs": [
            {
                "item_id": 5767,
                "quantity": 1,
                "item_name": "Ale yeast",
            }
        ],
        "icon_item_name": "Ale yeast",
        "action_type": "item_conversion",
        "batchable": True,
        "access": {
            "kind": "quest",
            "quest_id": "the_giant_dwarf",
            "stage": "started",
            "label": "The Giant Dwarf",
        },
        "source": "RuneScape Wiki Ale yeast oldid 4227753, 2011-05-03",
    },
    {
        "id": "bob_barter_decant_four",
        "display_name": "Decant all vial potions",
        "provider": "Bob Barter (herbs)",
        "location": "Grand Exchange",
        "currency_id": 995,
        "price": 0,
        "inputs": [],
        "outputs": [],
        "icon_item_name": "Agility potion (4)",
        "action_type": "decant_potions_to_dose",
        "default_target_dose": 4,
        "source": (
            "RuneScape Wiki Bob Barter (herbs) oldid 6222086, 2012-09-09; "
            "OpenRS2 rev 742 NPC 6524 Decant/Decant-X; "
            "Death Hats, Draynor and Upgrades, 2011-05-25; Darkan BobBarter.java"
        ),
    },
    {
        "id": "teplin_fill_potion_flasks",
        "display_name": "Fill 6-dose potion flasks",
        "provider": "Teplin Macagan",
        "location": "Oo'glog",
        "currency_id": 995,
        "price": 0,
        "inputs": [],
        "outputs": [],
        "icon_item_name": "Attack flask (6)",
        "action_type": "fill_potion_flasks",
        "access": {
            "kind": "quest",
            "quest_id": "as_a_first_resort",
            "label": "As a First Resort",
        },
        "source": (
            "RuneScape Wiki Teplin Macagan oldid 6225976, 2012-09-09; "
            "Potion flask oldid 6394714, 2012-10-13"
        ),
    },
    {
        "id": "teplin_decant_flasks_to_vials",
        "display_name": "Decant flasks into 4-dose vials",
        "provider": "Teplin Macagan",
        "location": "Oo'glog",
        "currency_id": 995,
        "price": 0,
        "inputs": [],
        "outputs": [],
        "icon_item_name": "Attack potion (4)",
        "action_type": "decant_flasks_to_vials",
        "access": {
            "kind": "quest",
            "quest_id": "as_a_first_resort",
            "label": "As a First Resort",
        },
        "source": (
            "RuneScape Wiki Teplin Macagan oldid 6225976, 2012-09-09; "
            "Potion flask oldid 6394714, 2012-10-13"
        ),
    },
    {
        "id": "leon_fletch_long_kebbit_bolts",
        "display_name": "Fletch long kebbit bolts",
        "provider": "Leon",
        "location": "Yanille",
        "currency_id": 995,
        "price": 40,
        "inputs": [
            {
                "item_id": 10107,
                "quantity": 1,
                "item_name": "Long kebbit spike",
            }
        ],
        "outputs": [
            {
                "item_id": 10159,
                "quantity": 6,
                "item_name": "Long kebbit bolts",
            }
        ],
        "icon_item_name": "Long kebbit bolts",
        "action_type": "item_conversion",
        "batchable": True,
        "source": "RuneScape Wiki Hunter oldid 6484443, 2012-10-27",
    },
    {
        "id": "thakkrad_cure_yak_hide",
        "display_name": "Cure yak-hide",
        "provider": "Thakkrad Sigmundson",
        "location": "Neitiznot",
        "currency_id": 995,
        "price": 5,
        "inputs": [
            {
                "item_id": 10818,
                "quantity": 1,
                "item_name": "Yak-hide",
            }
        ],
        "outputs": [
            {
                "item_id": 10820,
                "quantity": 1,
                "item_name": "Cured yak-hide",
            }
        ],
        "icon_item_name": "Cured yak-hide",
        "action_type": "item_conversion",
        "batchable": True,
        "access": {
            "kind": "quest",
            "quest_id": "the_fremennik_isles",
            "stage": 5,
            "label": "The Fremennik Isles",
        },
        "source": (
            "RuneScape Wiki Cured yak-hide oldid 5967010, 2012-07-20; "
            "Thakkrad Sigmundson oldid 6225987, 2012-09-09"
        ),
    },
]


def _bogrog_exchange_service_rows() -> list[dict[str, Any]]:
    generated = runpy.run_path(str(REPO_ROOT / "generated" / "summoning_data_generated.py"))
    rows: list[dict[str, Any]] = []
    for pouch in generated["SUMMONING_CATALOG"]:
        required_level = pouch.get("bogrog_level")
        refunded_shards = pouch.get("bogrog_shards")
        if required_level is None or refunded_shards is None:
            continue
        rows.append(
            {
                "id": f"bogrog_exchange_{pouch['id']}",
                "display_name": (
                    f"Exchange {pouch['pouch_name']} for "
                    f"{int(refunded_shards)} spirit shards"
                ),
                "provider": "Bogrog",
                "location": "Gu'Tanoth",
                "currency_id": 995,
                "price": 0,
                "inputs": [
                    {
                        "item_id": int(pouch["pouch_item_id"]),
                        "quantity": 1,
                        "item_name": str(pouch["pouch_name"]),
                    }
                ],
                "outputs": [
                    {
                        "item_id": 12183,
                        "quantity": int(refunded_shards),
                        "item_name": "Spirit shards",
                    }
                ],
                "icon_item_name": str(pouch["pouch_name"]),
                "action_type": "bogrog_pouch_exchange",
                "batchable": True,
                "required_skill": "summoning",
                "required_level": int(required_level),
                "familiar_id": str(pouch["id"]),
                "source": (
                    "RuneScape Wiki Bogrog oldid 6222092; Summoning pouches "
                    "oldid 6438719 exact exchange columns"
                ),
            }
        )
    return rows


SERVICE_ROWS.extend(_bogrog_exchange_service_rows())
