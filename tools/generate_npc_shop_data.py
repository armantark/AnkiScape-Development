#!/usr/bin/env python3
"""Generate AnkiScape NPC shop data from local 2011Scape/Darkan sources.

Runtime modules must not import the external source checkouts. This script
turns those checkouts into a source-backed Python catalog and a machine-readable
coverage ledger that can be reviewed independently.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DARKAN_SHOPS = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops")
DEFAULT_DARKAN_CONTENT = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content")
DEFAULT_DARKAN_CACHE = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-cache")
DEFAULT_DARKAN_JAVA_HOME = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/.jdks/jdk-24.0.2+12/Contents/Home")
DEFAULT_DARKAN_CORE_JAR = Path("/Users/ArmanTarkhanian1/.gradle/caches/modules-2/files-2.1/rs.darkan/core/2.0.5/5a13ad7bada8a9b1587bfa72fb013283102c6b7d/core-2.0.5.jar")
DEFAULT_DARKAN_DEPENDENCY_JARS = (
    Path("/Users/ArmanTarkhanian1/.gradle/caches/modules-2/files-2.1/it.unimi.dsi/fastutil/8.5.15/1e885b40c9563ab0d3899b871fd0b30e958705dc/fastutil-8.5.15.jar"),
    Path("/Users/ArmanTarkhanian1/.gradle/caches/modules-2/files-2.1/org.apache.logging.log4j/log4j-api/2.20.0/1fe6082e660daf07c689a89c94dc0f49c26b44bb/log4j-api-2.20.0.jar"),
    Path("/Users/ArmanTarkhanian1/.gradle/caches/modules-2/files-2.1/org.apache.logging.log4j/log4j-core/2.20.0/eb2a9a47b1396e00b5eee1264296729a70565cc0/log4j-core-2.20.0.jar"),
)
DEFAULT_2011_ITEMS = Path("/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml")

SHOP_DATA_PATH = REPO_ROOT / "shop_data.py"
LEDGER_PATH = REPO_ROOT / "memory-bank/source-audits/npc-shop-coverage-ledger-2026-07-06.json"
SUMMARY_PATH = REPO_ROOT / "memory-bank/source-audits/npc-shop-backend-audit-2026-07-06.md"
DARKAN_PRICE_HELPER = REPO_ROOT / "tools/DumpDarkanShopPriceInputs.java"

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

# Processing-type conversions (Ellis tanning, sawmill planks) are deliberately
# NOT shop services: 2011 tanning/plank runs were inventory-bounded (28
# unstackable items per bank run) and AnkiScape's review loop is the stand-in
# for that friction, so they live as no-XP Utility/Activities in constants.py
# (tan_soft_leather, tan_hard_leather, convert_logs_to_planks,
# convert_oak_logs_to_oak_planks) with the same Darkan source strings. An
# instant "Use x1000" shop service would delete source pacing. Only genuinely
# instant purchases/sales belong in VENDOR_ACTIONS below.
SERVICE_ROWS: list[dict[str, Any]] = []

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


# Storage-key normalizations where the items.yml cache name differs from the
# storage key another AnkiScape system already registered for the same item.
# 4600: items.yml spells it "Willow-blackjack" but The Feud quest catalog
# registers the identical weapon as "Willow blackjack"; without normalization
# the two keys slug-collide and the shop item silently loses its registry
# entry, icon, and Bank category.
ITEM_NAME_NORMALIZATIONS: dict[int, str] = {
    4600: "Willow blackjack",
}


def _item_name(items: dict[int, ItemMeta], item_id: int, fallback: str | None = None) -> str:
    normalized = ITEM_NAME_NORMALIZATIONS.get(item_id)
    if normalized:
        return normalized
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


def _raw_item_id(raw_item: dict[str, Any]) -> int:
    raw_item_ref = raw_item.get("item", -1)
    if isinstance(raw_item_ref, dict):
        return int(raw_item_ref.get("id", -1) or -1)
    return int(raw_item_ref)


def collect_source_shop_item_ids(darkan_shops: Path) -> set[int]:
    item_ids: set[int] = set()
    for path in sorted(darkan_shops.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        for raw_item in raw.get("items", []):
            if isinstance(raw_item, dict):
                item_id = _raw_item_id(raw_item)
                if item_id >= 0:
                    item_ids.add(item_id)
    return item_ids


def _java_tool(java_home: Path, name: str) -> str:
    tool_path = java_home / "bin" / name
    return str(tool_path if tool_path.exists() else name)


def _darkan_cache_arg(cache_path: Path) -> str:
    raw = str(cache_path)
    return raw if raw.endswith(os.sep) else raw + os.sep


def load_darkan_shop_price_inputs(
    cache_path: Path,
    item_ids: Iterable[int],
    *,
    core_jar: Path,
    dependency_jars: Iterable[Path],
    java_home: Path,
) -> dict[int, dict[str, Any]]:
    ids = sorted({int(item_id) for item_id in item_ids if int(item_id) >= 0})
    if not ids:
        return {}
    required_paths = [cache_path, core_jar, DARKAN_PRICE_HELPER, *dependency_jars]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Darkan price extraction input(s): " + ", ".join(missing))

    classpath = os.pathsep.join(str(path) for path in [core_jar, *dependency_jars])
    with tempfile.TemporaryDirectory(prefix="ankiscape-shop-prices-") as temp_dir:
        temp = Path(temp_dir)
        class_dir = temp / "classes"
        class_dir.mkdir()
        ids_path = temp / "item_ids.txt"
        output_path = temp / "prices.json"
        ids_path.write_text("\n".join(str(item_id) for item_id in ids) + "\n", encoding="utf-8")

        try:
            subprocess.run(
                [
                    _java_tool(java_home, "javac"),
                    "-cp",
                    classpath,
                    "-d",
                    str(class_dir),
                    str(DARKAN_PRICE_HELPER),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    _java_tool(java_home, "java"),
                    "-cp",
                    os.pathsep.join([str(class_dir), classpath]),
                    "DumpDarkanShopPriceInputs",
                    _darkan_cache_arg(cache_path),
                    str(ids_path),
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or str(exc)).strip()
            raise RuntimeError(f"Darkan shop price extraction failed: {detail}") from exc

        parsed = json.loads(output_path.read_text(encoding="utf-8"))
    rows = parsed.get("items", {})
    return {int(item_id): dict(row) for item_id, row in rows.items() if isinstance(row, dict)}


def _cache_int(price_inputs: dict[str, Any], key: str) -> int | None:
    value = price_inputs.get(key)
    if isinstance(value, int):
        return value
    return None


def _cache_base_price(price_inputs: dict[str, Any], key: str) -> int | None:
    value = _cache_int(price_inputs, key)
    if value is None:
        return None
    return max(1, value)


def _enum_override(price_inputs: dict[str, Any], key: str) -> int | None:
    value = _cache_int(price_inputs, key)
    if value is None or value == -1:
        return None
    return value


def _cache_shop_buy_price(price_inputs: dict[str, Any], currency_id: int) -> int | None:
    base_value = _cache_base_price(price_inputs, "value")
    if base_value is None:
        return None
    if currency_id == 995:
        override = _enum_override(price_inputs, "coin_buy_override")
        return override if override is not None else base_value
    if currency_id == 6529:
        override = _enum_override(price_inputs, "tokkul_buy_override")
        return override if override is not None else (base_value * 3 // 2)
    return base_value


def _cache_shop_sell_price(price_inputs: dict[str, Any], currency_id: int) -> int | None:
    base_value = _cache_base_price(price_inputs, "sell_price")
    if base_value is None:
        return None
    if currency_id == 995:
        override = _enum_override(price_inputs, "coin_sell_override")
        return override if override is not None else base_value
    if currency_id == 6529:
        override = _enum_override(price_inputs, "tokkul_sell_override")
        return override if override is not None else base_value
    return base_value


def _price_for_row(
    raw_item: dict[str, Any],
    item_id: int,
    currency_id: int,
    price_inputs: dict[int, dict[str, Any]],
) -> tuple[int | None, int | None, str, str]:
    cache_row = price_inputs.get(item_id, {})
    custom_price = raw_item.get("customPrice")
    if isinstance(custom_price, int) and custom_price > 0:
        sell_price = _cache_shop_sell_price(cache_row, currency_id)
        if sell_price is not None:
            return custom_price, sell_price, "custom_buy_darkan_sell_price", "Darkan shop JSON customPrice for buy; Darkan Shop.java getSellPrice for sell"
        return custom_price, None, "custom_buy_sell_unresolved", "Darkan shop JSON customPrice for buy; Darkan cache sell price unavailable"
    buy_price = _cache_shop_buy_price(cache_row, currency_id)
    sell_price = _cache_shop_sell_price(cache_row, currency_id)
    if buy_price is not None:
        return buy_price, sell_price, "darkan_shop_cache_price", "Darkan Shop.java getBuyPrice/getSellPrice via cache item definitions and enum overrides"
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
    price_inputs: dict[int, dict[str, Any]],
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
        buy_price, sell_price, price_policy, price_source = _price_for_row(raw_item, item_id, currency_id, price_inputs)
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


def build_catalog(
    darkan_shops: Path,
    items_path: Path,
    price_inputs: dict[int, dict[str, Any]] | None = None,
    darkan_cache: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    items = load_2011_items(items_path)
    resolved_price_inputs = price_inputs or {}
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
            resolved_price_inputs,
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
            "darkan_cache": str(darkan_cache) if darkan_cache is not None else "",
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


def _darkan_get_sell_price(price_inputs: dict[str, Any]) -> int | None:
    """Shop.java getSellPrice, exactly: cache sellPrice floored 0->1, then the
    coin sell enum override wins unfloored when present."""
    base = _cache_int(price_inputs, "sell_price")
    if base is None or base < 0:
        return None
    if base == 0:
        base = 1
    override = _enum_override(price_inputs, "coin_sell_override")
    return override if override is not None else base


def _darkan_get_buy_price(price_inputs: dict[str, Any]) -> int | None:
    """Shop.java getBuyPrice for a no-custom-price coin row, exactly: cache
    value floored 0->1, then the coin buy enum override wins unfloored."""
    base = _cache_int(price_inputs, "value")
    if base is None or base < 0:
        return None
    if base == 0:
        base = 1
    override = _enum_override(price_inputs, "coin_buy_override")
    return override if override is not None else base


def build_player_sell_prices(
    items: dict[int, ItemMeta],
    price_inputs: dict[int, dict[str, Any]],
    shops: Iterable[dict[str, Any]],
) -> tuple[dict[str, int], dict[str, int]]:
    """Coin sell price per storage name — absolute Darkan parity (owner
    decision 2026-07-06): the price is Shop.java getSellPrice for the name's
    canonical item id, identical at every shop. AnkiScape's flat inventory
    only has names, so the canonical id is the id live shop stock uses for
    that name (what players actually buy), falling back to the lowest
    tradeable id in items.yml. No clamping: buy-low/sell-high flips that the
    Darkan engine allows (custom-priced stock vs cache sellPrice) stay, and
    are bounded the way the engine bounds them — stock per review-paced
    restock interval. Also returns the matching getBuyPrice table (cache value
    floored 0->1 plus coin buy enum override) so buying back player-sold
    temporary stock prices exactly like the engine.
    """
    stock_id_by_name: dict[str, int] = {}
    for shop in shops:
        for row in shop.get("stock", []):
            name = row.get("item_name", "")
            item_id = row.get("item_id")
            if not name or not isinstance(item_id, int):
                continue
            if row.get("disposition") == "live" and name not in stock_id_by_name:
                stock_id_by_name[name] = item_id

    canonical: dict[str, int] = {}
    for item_id, meta in sorted(items.items()):
        if not meta.tradeable:
            continue
        name = _item_name(items, item_id)
        if not name or name.startswith("Item ") or name.lower().startswith("null"):
            continue
        canonical.setdefault(name, item_id)
    canonical.update(stock_id_by_name)

    sell_prices: dict[str, int] = {}
    buy_prices: dict[str, int] = {}
    for name, item_id in canonical.items():
        cache_row = price_inputs.get(item_id)
        if not cache_row:
            continue
        sell_price = _darkan_get_sell_price(cache_row)
        if sell_price is not None:
            sell_prices[name] = sell_price
        buy_price = _darkan_get_buy_price(cache_row)
        if buy_price is not None:
            buy_prices[name] = buy_price
    return dict(sorted(sell_prices.items())), dict(sorted(buy_prices.items()))


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

# Coin sell price for every tradeable 2011 item (Shop.java player-sale math:
# ItemDefinitions.sellPrice + coin sell enum override). General-store sales of
# items no shop stocks resolve through this table instead of failing closed.
SHOP_PLAYER_SELL_PRICES: Dict[str, int] = {_py_repr(catalog.get("player_sell_prices", {}))}

# Shop.java getBuyPrice for the same canonical ids (cache value floored 0->1
# plus the coin buy enum override); prices buy-backs of player-sold stock.
SHOP_PLAYER_BUY_PRICES: Dict[str, int] = {_py_repr(catalog.get("player_buy_prices", {}))}


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
        f"- Darkan cache price inputs: `{ledger['source_roots']['darkan_cache']}`",
        f"- 2011Scape item names/tradeability: `{ledger['source_roots']['items_2011scape']}`",
        "- 2011Scape shop model and Darkan shop model were used as behavior references for stock, restock, price policy, general-store sell policy, and player-sold temporary stock.",
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
        "- Coin stock rows with a source-backed custom price, Darkan cache value, or direct content literal are live.",
        "- Darkan cache prices mirror `Shop.java`: custom prices override buy price only; otherwise buy price uses ItemDefinitions.value plus coin/Tokkul enum overrides, while sell price uses ItemDefinitions.sellPrice plus sell enum overrides.",
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
        "Backend contract testing is pure-Python. Qt frontend passes should verify Shop-tab rendering and transactions through offscreen Qt tests plus a local visual smoke check.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--darkan-shops", type=Path, default=DEFAULT_DARKAN_SHOPS)
    parser.add_argument("--darkan-content", type=Path, default=DEFAULT_DARKAN_CONTENT)
    parser.add_argument("--darkan-cache", type=Path, default=DEFAULT_DARKAN_CACHE)
    parser.add_argument("--darkan-java-home", type=Path, default=DEFAULT_DARKAN_JAVA_HOME)
    parser.add_argument("--darkan-core-jar", type=Path, default=DEFAULT_DARKAN_CORE_JAR)
    parser.add_argument("--darkan-dependency-jar", type=Path, action="append", default=None)
    parser.add_argument("--items-2011", type=Path, default=DEFAULT_2011_ITEMS)
    parser.add_argument("--shop-data-out", type=Path, default=SHOP_DATA_PATH)
    parser.add_argument("--ledger-out", type=Path, default=LEDGER_PATH)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_PATH)
    args = parser.parse_args()

    items = load_2011_items(args.items_2011)
    item_ids = set(collect_source_shop_item_ids(args.darkan_shops))
    # Player sales at general stores follow the same Shop.java sell math as
    # stock rows, but for ANY tradeable item the player holds — so the cache
    # dump covers every tradeable 2011 item, not just shop stock.
    tradeable_ids = {item_id for item_id, meta in items.items() if meta.tradeable}
    price_inputs = load_darkan_shop_price_inputs(
        args.darkan_cache,
        item_ids | tradeable_ids,
        core_jar=args.darkan_core_jar,
        dependency_jars=tuple(args.darkan_dependency_jar or DEFAULT_DARKAN_DEPENDENCY_JARS),
        java_home=args.darkan_java_home,
    )
    catalog, ledger = build_catalog(args.darkan_shops, args.items_2011, price_inputs, args.darkan_cache)
    catalog["player_sell_prices"], catalog["player_buy_prices"] = build_player_sell_prices(
        items, price_inputs, catalog["shops"]
    )
    catalog["summary"]["player_sell_price_count"] = len(catalog["player_sell_prices"])
    ledger["summary"]["player_sell_price_count"] = len(catalog["player_sell_prices"])
    args.shop_data_out.parent.mkdir(parents=True, exist_ok=True)
    args.ledger_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    write_shop_data(catalog, args.shop_data_out)
    args.ledger_out.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(ledger, args.summary_out)
    print(json.dumps(catalog["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
