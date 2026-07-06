#!/usr/bin/env python3
"""Generate AnkiScape NPC shop data from local 2011Scape/Darkan sources.

Runtime modules must not import the external source checkouts. This script
turns those checkouts into a source-backed Python catalog and a machine-readable
coverage ledger that can be reviewed independently.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DARKAN_SHOPS = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops")
DEFAULT_DARKAN_CONTENT = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content")
DEFAULT_2011_ITEMS = Path("/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml")

SHOP_DATA_PATH = REPO_ROOT / "shop_data.py"
LEDGER_PATH = REPO_ROOT / "memory-bank/source-audits/npc-shop-coverage-ledger-2026-07-06.json"
SUMMARY_PATH = REPO_ROOT / "memory-bank/source-audits/npc-shop-backend-audit-2026-07-06.md"

SHOP_DATA_VERSION = 1
DARKAN_DEFAULT_RESTOCK_TICKS = 50
DARKAN_SOURCE = "Darkan shop JSON"
SCAPE_2011_SOURCE = "2011Scape items.yml"

DEV_SHOP_IDS = {"a_test_shop"}
HIDDEN_SHOP_HINTS = (
    "stardust",
    "loyalty",
    "castle",
    "soul",
    "stealing_creation",
    "dungeoneering",
    "token",
)

# These prices are direct shop/action literals from Darkan content files. Shop
# rows without a Darkan customPrice remain read-only until a cache price extractor
# is committed, rather than borrowing values from a different era or wiki.
MANUAL_ITEM_PRICES = {
    1917: {"buy": 2, "sell": 1, "source": "BartenderUtils.kt / bartender dialogue literals"},
    1919: {"sell": 2, "source": "BartenderUtils.kt sellBeerGlass"},
    1971: {"buy": 1, "source": "world/areas/al_kharid/npcs/Karim.kt"},
    950: {"buy": 3, "source": "world/areas/al_kharid/npcs/SilkTrader.kt"},
    11169: {"buy": 50, "source": "world/areas/varrock/npcs/Benny.java"},
}

SERVICE_ROWS = [
    {
        "id": "al_kharid_tanner_soft_leather",
        "display_name": "Tan soft leather",
        "provider": "Ellis",
        "location": "Al Kharid",
        "currency_id": 995,
        "price": 1,
        "inputs": [{"item_id": 1739, "quantity": 1}],
        "outputs": [{"item_id": 1741, "quantity": 1}],
        "source": "Darkan Tanning.Leather.SOFT via Al Kharid Ellis/Lunar tan-leather references",
        "service_type": "processing",
    },
    {
        "id": "al_kharid_tanner_hard_leather",
        "display_name": "Tan hard leather",
        "provider": "Ellis",
        "location": "Al Kharid",
        "currency_id": 995,
        "price": 3,
        "inputs": [{"item_id": 1739, "quantity": 1}],
        "outputs": [{"item_id": 1743, "quantity": 1}],
        "source": "Darkan Tanning.Leather.HARD via Al Kharid Ellis/Lunar tan-leather references",
        "service_type": "processing",
    },
    {
        "id": "sawmill_normal_plank",
        "display_name": "Convert logs to planks",
        "provider": "Sawmill operator",
        "location": "Varrock sawmill",
        "currency_id": 995,
        "price": 100,
        "inputs": [{"item_id": 1511, "quantity": 1}],
        "outputs": [{"item_id": 960, "quantity": 1}],
        "source": "Darkan SawmillOperator planks and LunarSpellbook plank-make cost path",
        "service_type": "processing",
    },
    {
        "id": "sawmill_oak_plank",
        "display_name": "Convert oak logs to oak planks",
        "provider": "Sawmill operator",
        "location": "Varrock sawmill",
        "currency_id": 995,
        "price": 250,
        "inputs": [{"item_id": 1521, "quantity": 1}],
        "outputs": [{"item_id": 8778, "quantity": 1}],
        "source": "Darkan SawmillOperator planks and LunarSpellbook plank-make cost path",
        "service_type": "processing",
    },
]

VENDOR_ACTIONS = [
    {
        "id": "bartender_buy_beer",
        "display_name": "Buy a pint of beer",
        "provider": "Bartender",
        "location": "Common pubs",
        "currency_id": 995,
        "price": 2,
        "outputs": [{"item_id": 1917, "quantity": 1}],
        "source": "Darkan BartenderUtils.buyDrinkOrIngredients and pub dialogue literals",
        "action_type": "direct_purchase",
    },
    {
        "id": "bartender_sell_beer_glass",
        "display_name": "Sell empty beer glass",
        "provider": "Bartender",
        "location": "Common pubs",
        "currency_id": 995,
        "price": 0,
        "inputs": [{"item_id": 1919, "quantity": 1}],
        "outputs": [{"item_id": 995, "quantity": 2}],
        "source": "Darkan BartenderUtils.sellBeerGlass",
        "action_type": "direct_sale",
    },
    {
        "id": "benny_buy_varrock_herald",
        "display_name": "Buy a Varrock Herald",
        "provider": "Benny",
        "location": "Varrock Square",
        "currency_id": 995,
        "price": 50,
        "outputs": [{"item_id": 11169, "quantity": 1}],
        "source": "Darkan world/areas/varrock/npcs/Benny.java",
        "action_type": "direct_purchase",
    },
    {
        "id": "karim_buy_kebab",
        "display_name": "Buy a kebab",
        "provider": "Karim",
        "location": "Al Kharid",
        "currency_id": 995,
        "price": 1,
        "outputs": [{"item_id": 1971, "quantity": 1}],
        "source": "Darkan world/areas/al_kharid/npcs/Karim.kt",
        "action_type": "direct_purchase",
    },
]


@dataclass(frozen=True)
class ItemMeta:
    id: int
    name: str
    tradeable: bool
    equipment: Any


def _slug(text: str) -> str:
    parts = re.findall(r"[a-z0-9]+", text.lower())
    return "_".join(parts) or "unnamed"


def _safe_str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"null", "None"}:
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_2011_items(path: Path) -> dict[int, ItemMeta]:
    items: dict[int, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("- id:"):
            if current is not None and isinstance(current.get("id"), int):
                items[current["id"]] = current
            current = {"id": int(line.split(":", 1)[1].strip())}
            continue
        if current is None or not line.startswith("  ") or ":" not in line:
            continue
        key, raw_value = line.strip().split(":", 1)
        current[key] = _parse_scalar(raw_value)
    if current is not None and isinstance(current.get("id"), int):
        items[current["id"]] = current
    return {
        item_id: ItemMeta(
            id=item_id,
            name=str(spec.get("name") or f"Item {item_id}"),
            tradeable=bool(spec.get("tradeable", False)),
            equipment=spec.get("equipment"),
        )
        for item_id, spec in items.items()
    }


def _item_name(items: dict[int, ItemMeta], item_id: int, fallback: str | None = None) -> str:
    meta = items.get(item_id)
    if meta:
        return meta.name
    if fallback:
        return fallback
    return f"Item {item_id}"


def _currency_name(currency_id: int) -> str:
    return {
        995: "Coins",
        6529: "Tokkul",
        6306: "Trading sticks",
        13727: "Fist of Guthix tokens",
    }.get(currency_id, f"Currency {currency_id}")


def _visibility_for_shop(shop_id: str, currency_id: int) -> tuple[str, str]:
    if any(hint in shop_id for hint in HIDDEN_SHOP_HINTS):
        return "hidden", "activity_or_reward_system_not_implemented"
    if currency_id != 995:
        return "visible_locked", "currency_not_implemented"
    return "visible", ""


def _price_for_row(raw_item: dict[str, Any], item_id: int) -> tuple[int | None, int | None, str, str]:
    custom_price = raw_item.get("customPrice")
    if isinstance(custom_price, int) and custom_price > 0:
        return custom_price, max(0, custom_price // 3), "custom_price", "Darkan shop JSON customPrice"
    manual = MANUAL_ITEM_PRICES.get(item_id)
    if manual:
        buy = manual.get("buy")
        sell = manual.get("sell")
        if sell is None and isinstance(buy, int):
            sell = max(0, buy // 3)
        return buy if isinstance(buy, int) else None, sell if isinstance(sell, int) else None, "manual_source_literal", str(manual["source"])
    return None, None, "cache_price_unresolved", "Darkan ItemDefinitions.value not available in generated source"


def _stock_rows(
    shop_id: str,
    shop_path: Path,
    raw_items: Iterable[dict[str, Any]],
    currency_id: int,
    shop_visibility: str,
    shop_lock_reason: str,
    items: dict[int, ItemMeta],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items):
        raw_item_ref = raw_item.get("item", -1)
        if isinstance(raw_item_ref, dict):
            item_id = int(raw_item_ref.get("id", -1) or -1)
            amount = int(raw_item_ref.get("amount", raw_item.get("amount", 0)) or 0)
        else:
            item_id = int(raw_item_ref)
            amount = int(raw_item.get("amount", 0) or 0)
        restock_ticks = int(raw_item.get("restockTicks", DARKAN_DEFAULT_RESTOCK_TICKS) or DARKAN_DEFAULT_RESTOCK_TICKS)
        item_meta = items.get(item_id)
        fallback_name = _safe_str(raw_item.get("_name"), f"Item {item_id}")
        buy_price, sell_price, price_policy, price_source = _price_for_row(raw_item, item_id)
        row_visibility = shop_visibility
        lock_reason = shop_lock_reason
        disposition = "live"
        if item_meta is None:
            row_visibility = "hidden"
            lock_reason = "unknown_item"
            disposition = "blocked"
        elif row_visibility == "hidden":
            disposition = "hidden"
        elif row_visibility == "visible_locked":
            disposition = "locked"
        elif currency_id != 995:
            row_visibility = "visible_locked"
            lock_reason = "currency_not_implemented"
            disposition = "locked"
        elif buy_price is None:
            row_visibility = "visible_locked"
            lock_reason = "price_policy_unresolved"
            disposition = "locked"
        rows.append(
            {
                "id": f"{shop_id}:{index}:{item_id}",
                "item_id": item_id,
                "item_name": _item_name(items, item_id, fallback_name),
                "default_quantity": amount,
                "current_quantity": amount,
                "stock_type": "normal",
                "restock_ticks": max(1, restock_ticks),
                "restock_amount": 1,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "price_policy": price_policy,
                "price_source": price_source,
                "visibility": row_visibility,
                "lock_reason": lock_reason,
                "disposition": disposition,
                "source_path": str(shop_path),
                "source": DARKAN_SOURCE,
                "tradeable": bool(item_meta.tradeable) if item_meta else False,
            }
        )
    return rows


def build_catalog(darkan_shops: Path, items_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    items = load_2011_items(items_path)
    shops: list[dict[str, Any]] = []
    ledger_shops: list[dict[str, Any]] = []
    source_paths = sorted(darkan_shops.glob("*.json"))

    for path in source_paths:
        shop_id = _slug(path.stem)
        raw = json.loads(path.read_text(encoding="utf-8"))
        if shop_id in DEV_SHOP_IDS:
            ledger_shops.append(
                {
                    "id": shop_id,
                    "name": raw.get("name", path.stem),
                    "source_path": str(path),
                    "disposition": "excluded",
                    "reason": "developer_test_shop",
                    "stock_rows": [],
                }
            )
            continue
        currency_id = int(raw.get("currency", 995) or 995)
        visibility, lock_reason = _visibility_for_shop(shop_id, currency_id)
        rows = _stock_rows(
            shop_id,
            path,
            raw.get("items", []),
            currency_id,
            visibility,
            lock_reason,
            items,
        )
        shop_disposition = "hidden" if visibility == "hidden" else ("locked" if visibility == "visible_locked" else "visible")
        if rows and all(row["disposition"] == "blocked" for row in rows) and visibility != "hidden":
            shop_disposition = "blocked"
            visibility = "hidden"
            lock_reason = "all_rows_blocked"
        shop = {
            "id": shop_id,
            "display_name": _safe_str(raw.get("name"), path.stem.replace("_", " ").title()),
            "source_name": _safe_str(raw.get("name"), path.stem),
            "currency_id": currency_id,
            "currency_name": _currency_name(currency_id),
            "currency_item_name": _item_name(items, currency_id, _currency_name(currency_id)),
            "currency_implemented": currency_id == 995,
            "general_store": bool(raw.get("generalStore", False)),
            "buy_only": bool(raw.get("buyOnly", False)),
            "shared_stock_group": shop_id,
            "visibility": visibility,
            "lock_reason": lock_reason,
            "source_path": str(path),
            "source": DARKAN_SOURCE,
            "npc_ids": tuple(int(npc_id) for npc_id in raw.get("npcIds", []) if isinstance(npc_id, int)),
            "stock": rows,
        }
        shops.append(shop)
        ledger_shops.append(
            {
                "id": shop_id,
                "name": shop["display_name"],
                "source_path": str(path),
                "disposition": shop_disposition,
                "reason": lock_reason,
                "stock_rows": [
                    {
                        "id": row["id"],
                        "item_id": row["item_id"],
                        "item_name": row["item_name"],
                        "disposition": row["disposition"],
                        "visibility": row["visibility"],
                        "lock_reason": row["lock_reason"],
                        "price_policy": row["price_policy"],
                        "price_source": row["price_source"],
                    }
                    for row in rows
                ],
            }
        )

    currencies = sorted({shop["currency_id"] for shop in shops} | {995})
    services = _attach_item_names(SERVICE_ROWS, items)
    vendor_actions = _attach_item_names(VENDOR_ACTIONS, items)
    summary = _coverage_summary(source_paths, shops, ledger_shops, services, vendor_actions)
    catalog = {
        "version": SHOP_DATA_VERSION,
        "shops": shops,
        "currencies": [
            {
                "id": currency_id,
                "name": _currency_name(currency_id),
                "item_name": _item_name(items, currency_id, _currency_name(currency_id)),
                "implemented": currency_id == 995,
            }
            for currency_id in currencies
        ],
        "services": services,
        "vendor_actions": vendor_actions,
        "summary": summary,
    }
    ledger = {
        "generated_at": "2026-07-06",
        "shop_data_version": SHOP_DATA_VERSION,
        "source_roots": {
            "darkan_shops": str(darkan_shops),
            "items_2011scape": str(items_path),
        },
        "summary": summary,
        "shops": ledger_shops,
        "services": services,
        "vendor_actions": vendor_actions,
    }
    return catalog, ledger


def _attach_item_names(rows: Iterable[dict[str, Any]], items: dict[int, ItemMeta]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        clean = dict(row)
        for key in ("inputs", "outputs"):
            clean_rows = []
            for item in clean.get(key, []):
                item_id = int(item["item_id"])
                clean_item = dict(item)
                clean_item["item_name"] = _item_name(items, item_id)
                clean_item["tradeable"] = bool(items.get(item_id).tradeable) if item_id in items else False
                clean_rows.append(clean_item)
            clean[key] = clean_rows
        clean["currency_name"] = _currency_name(int(clean.get("currency_id", 995)))
        clean["currency_item_name"] = _item_name(items, int(clean.get("currency_id", 995)), clean["currency_name"])
        clean["currency_implemented"] = clean.get("currency_id", 995) == 995
        clean["visibility"] = "visible" if clean["currency_implemented"] else "visible_locked"
        clean["lock_reason"] = "" if clean["currency_implemented"] else "currency_not_implemented"
        clean["source"] = clean.get("source", "Darkan content source")
        out.append(clean)
    return out


def _coverage_summary(
    source_paths: list[Path],
    shops: list[dict[str, Any]],
    ledger_shops: list[dict[str, Any]],
    services: list[dict[str, Any]],
    vendor_actions: list[dict[str, Any]],
) -> dict[str, Any]:
    row_counter = Counter(row["disposition"] for shop in shops for row in shop["stock"])
    shop_counter = Counter(entry["disposition"] for entry in ledger_shops)
    currency_counter = Counter(str(shop["currency_id"]) for shop in shops)
    return {
        "source_shop_count": len(source_paths),
        "runtime_shop_count": len(shops),
        "excluded_shop_count": shop_counter.get("excluded", 0),
        "visible_shop_count": sum(1 for shop in shops if shop["visibility"] == "visible"),
        "locked_shop_count": sum(1 for shop in shops if shop["visibility"] == "visible_locked"),
        "hidden_shop_count": sum(1 for shop in shops if shop["visibility"] == "hidden"),
        "stock_row_count": sum(len(shop["stock"]) for shop in shops),
        "live_stock_row_count": row_counter.get("live", 0),
        "locked_stock_row_count": row_counter.get("locked", 0),
        "hidden_stock_row_count": row_counter.get("hidden", 0),
        "blocked_stock_row_count": row_counter.get("blocked", 0),
        "currency_counts": dict(sorted(currency_counter.items())),
        "service_count": len(services),
        "vendor_action_count": len(vendor_actions),
    }


def _py_repr(value: Any) -> str:
    if isinstance(value, tuple):
        inner = ", ".join(_py_repr(v) for v in value)
        return f"({inner},)" if len(value) == 1 else f"({inner})"
    if isinstance(value, list):
        return "[" + ", ".join(_py_repr(v) for v in value) + "]"
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            parts.append(f"{_py_repr(key)}: {_py_repr(item)}")
        return "{" + ", ".join(parts) + "}"
    return repr(value)


def write_shop_data(catalog: dict[str, Any], output_path: Path) -> None:
    shop_map = {shop["id"]: shop for shop in catalog["shops"]}
    currency_map = {str(currency["id"]): currency for currency in catalog["currencies"]}
    service_map = {service["id"]: service for service in catalog["services"]}
    vendor_map = {action["id"]: action for action in catalog["vendor_actions"]}
    item_specs = _extra_item_specs(catalog)
    body = f'''"""Generated NPC shop catalog for AnkiScape.

Do not edit this file by hand. Run tools/generate_npc_shop_data.py.
"""

from __future__ import annotations

from typing import Any, Dict


SHOP_DATA_VERSION = {SHOP_DATA_VERSION}
SHOP_MARKET_TICKS_PER_HOUR = 10
SHOP_MARKET_TICKS_PER_DAY = 240
SHOP_DEFAULT_RESTOCK_TICKS = {DARKAN_DEFAULT_RESTOCK_TICKS}
SHOP_ID_ALIASES: Dict[str, str] = {{}}

SHOP_CURRENCIES: Dict[str, Dict[str, Any]] = {_py_repr(currency_map)}

SHOP_DATA: Dict[str, Dict[str, Any]] = {_py_repr(shop_map)}

SHOP_SERVICES: Dict[str, Dict[str, Any]] = {_py_repr(service_map)}

SHOP_VENDOR_ACTIONS: Dict[str, Dict[str, Any]] = {_py_repr(vendor_map)}

SHOP_COVERAGE_SUMMARY: Dict[str, Any] = {_py_repr(catalog["summary"])}

SHOP_EXTRA_ITEM_DATA: Dict[str, Dict[str, Any]] = {_py_repr(item_specs)}


def shop_extra_items_as_dict() -> Dict[str, Dict[str, Any]]:
    return {{name: dict(spec) for name, spec in SHOP_EXTRA_ITEM_DATA.items()}}


def shop_coverage_summary_as_dict() -> Dict[str, Any]:
    return dict(SHOP_COVERAGE_SUMMARY)
'''
    output_path.write_text(body, encoding="utf-8")


def _extra_item_specs(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    specs: dict[str, dict[str, Any]] = {}

    def add(name: str, source: str, tradeable: bool = True) -> None:
        if not name or name.startswith("Item "):
            return
        specs.setdefault(
            name,
            {
                "category": "material",
                "tradeable": bool(tradeable),
                "source": source,
            },
        )

    for currency in catalog["currencies"]:
        add(currency["item_name"], "NPC shop currency", currency["id"] == 995)
    for shop in catalog["shops"]:
        for row in shop["stock"]:
            add(row["item_name"], f"NPC shop stock: {shop['display_name']}", row["tradeable"])
    for collection in (catalog["services"], catalog["vendor_actions"]):
        for row in collection:
            add(row["currency_item_name"], f"NPC shop currency: {row['display_name']}", True)
            for item in row.get("inputs", []):
                add(item["item_name"], f"NPC service input: {row['display_name']}", item["tradeable"])
            for item in row.get("outputs", []):
                add(item["item_name"], f"NPC service output: {row['display_name']}", item["tradeable"])
    return dict(sorted(specs.items()))


def write_summary(ledger: dict[str, Any], path: Path) -> None:
    summary = ledger["summary"]
    lines = [
        "# NPC Shop Backend Source Audit",
        "",
        "Generated: 2026-07-06",
        "",
        "## Sources",
        "",
        f"- Darkan shop JSON: `{ledger['source_roots']['darkan_shops']}`",
        f"- 2011Scape item names/tradeability: `{ledger['source_roots']['items_2011scape']}`",
        "- 2011Scape shop model and Darkan shop model were used as behavior references for stock, restock, general-store sell policy, and player-sold temporary stock.",
        "",
        "## Coverage",
        "",
        f"- Source shop files: {summary['source_shop_count']}",
        f"- Runtime shops: {summary['runtime_shop_count']}",
        f"- Visible shops: {summary['visible_shop_count']}",
        f"- Locked/read-only shops: {summary['locked_shop_count']}",
        f"- Hidden shops: {summary['hidden_shop_count']}",
        f"- Stock rows: {summary['stock_row_count']}",
        f"- Live stock rows: {summary['live_stock_row_count']}",
        f"- Locked stock rows: {summary['locked_stock_row_count']}",
        f"- Hidden stock rows: {summary['hidden_stock_row_count']}",
        f"- Blocked stock rows: {summary['blocked_stock_row_count']}",
        f"- Services: {summary['service_count']}",
        f"- Vendor actions: {summary['vendor_action_count']}",
        "",
        "## Disposition Policy",
        "",
        "- Coin stock rows with a source-backed custom price or direct content literal are live.",
        "- Coin stock rows without a resolved Darkan cache item value are visible but locked, so gameplay fails closed rather than inventing prices.",
        "- Non-coin shops are visible but read-only until their currencies exist in AnkiScape.",
        "- Reward/activity-dependent shop families are hidden from normal player search until their owning system exists.",
        "- The developer test shop is excluded and still appears in the JSON ledger with an explicit disposition.",
        "",
        "## Frontend Handoff Fixtures",
        "",
        "Use `shop_fixtures.build_shop_frontend_fixtures()` for deterministic examples covering live purchases, locked stock rows, hidden reward shops, shared-stock keys, player-sold stock, services, vendor actions, search results, error previews, and transaction history.",
        "",
        "## Manual Test Notes",
        "",
        "Backend manual testing is pure-Python for this turn. The future UI thread should verify Shop-tab rendering and transactions through Pinchtab after wiring the frontend surface.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--darkan-shops", type=Path, default=DEFAULT_DARKAN_SHOPS)
    parser.add_argument("--darkan-content", type=Path, default=DEFAULT_DARKAN_CONTENT)
    parser.add_argument("--items-2011", type=Path, default=DEFAULT_2011_ITEMS)
    parser.add_argument("--shop-data-out", type=Path, default=SHOP_DATA_PATH)
    parser.add_argument("--ledger-out", type=Path, default=LEDGER_PATH)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_PATH)
    args = parser.parse_args()

    catalog, ledger = build_catalog(args.darkan_shops, args.items_2011)
    args.shop_data_out.parent.mkdir(parents=True, exist_ok=True)
    args.ledger_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    write_shop_data(catalog, args.shop_data_out)
    args.ledger_out.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(ledger, args.summary_out)
    print(json.dumps(catalog["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
