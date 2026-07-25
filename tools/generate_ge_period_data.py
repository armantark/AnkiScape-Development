#!/usr/bin/env python3
"""Generate pre-EOC Grand Exchange prices and buy limits for registered items.

The period wiki stored each market row under ``Exchange:<item>`` and kept a
complete buy-limit table. Network responses are checkpointed under
``tools/.cache/grand_exchange_period`` so interrupted harvests resume without
repeating successful requests.

Usage:
    python3 tools/generate_ge_period_data.py grand_exchange_period_generated.py
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "tools" / ".cache" / "grand_exchange_period"
API = "https://runescape.wiki/api.php"
CUTOFF = "2012-11-20T00:00:00Z"
BUY_LIMIT_TITLE = "Calculator:Grand Exchange buying limits"
USER_AGENT = "AnkiScape-GE-harvest/1.0 (personal project)"
WORKERS = 2

_FIELD_RE = re.compile(r"(?m)^\|([^=|]+)=([^\n\r]*)$")
_LIMIT_ROW_RE = re.compile(
    r"\[\[Exchange:([^|\]]+)(?:\|[^\]]+)?\]\]\s*\r?\n\|([\d,]+)"
)
_FRACTIONS = str.maketrans({"½": "1/2", "⅓": "1/3", "⅔": "2/3"})


def _request_json(params: Mapping[str, object]) -> Mapping[str, object]:
    query = urllib.parse.urlencode({**params, "format": "json", "formatversion": 2})
    request = urllib.request.Request(
        f"{API}?{query}",
        headers={"User-Agent": USER_AGENT},
    )
    for attempt in range(8):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 7:
                raise
            retry_after = error.headers.get("Retry-After")
            try:
                delay = max(1, int(retry_after))
            except (TypeError, ValueError):
                delay = min(30, 2**attempt)
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if attempt == 7:
                raise
            time.sleep(min(30, 2**attempt))
    raise RuntimeError("unreachable")


def _cache_path(title: str) -> Path:
    digest = hashlib.sha256(title.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def _fetch_cutoff_revision(title: str) -> dict[str, object] | None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _cache_path(title)
    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        return cached if isinstance(cached, dict) and cached else None

    payload = _request_json(
        {
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "redirects": 1,
            "rvlimit": 1,
            "rvprop": "ids|timestamp|content",
            "rvslots": "main",
            "rvstart": CUTOFF,
            "rvdir": "older",
        }
    )
    pages = payload.get("query", {}).get("pages", [])
    result: dict[str, object] | None = None
    if isinstance(pages, list):
        for page in pages:
            if not isinstance(page, Mapping) or page.get("missing"):
                continue
            revisions = page.get("revisions")
            if not isinstance(revisions, list) or not revisions:
                continue
            revision = revisions[0]
            slots = revision.get("slots") if isinstance(revision, Mapping) else None
            main = slots.get("main") if isinstance(slots, Mapping) else None
            content = main.get("content") if isinstance(main, Mapping) else None
            if not isinstance(content, str):
                continue
            result = {
                "title": str(page.get("title", title)),
                "revid": int(revision["revid"]),
                "timestamp": str(revision["timestamp"]),
                "content": content,
            }
            break
    cache_path.write_text(
        json.dumps(result or {}, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    return result


def _normalized_name(name: str) -> str:
    text = unicodedata.normalize("NFKC", name.translate(_FRACTIONS))
    return " ".join(text.casefold().split())


def _parse_fields(wikitext: str) -> dict[str, str]:
    return {
        key.strip().casefold(): value.strip()
        for key, value in _FIELD_RE.findall(wikitext)
    }


def _parse_positive_int(value: object) -> int | None:
    try:
        parsed = int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
def _registered_item_names() -> tuple[str, ...]:
    sys.path.insert(0, str(ROOT))
    try:
        from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
    finally:
        sys.path.pop(0)
    return tuple(sorted(GE_ITEM_CATALOG))


def _period_name_candidates(item_name: str) -> tuple[str, ...]:
    candidates = [item_name]
    if item_name.endswith("ies"):
        candidates.append(f"{item_name[:-3]}y")
    if item_name.endswith("s"):
        candidates.append(item_name[:-1])
    if item_name.endswith(" med helm"):
        candidates.append(f"{item_name[:-9]} helm")
    return tuple(dict.fromkeys(candidates))


def _buy_limit_table() -> tuple[dict[str, int], dict[str, str], dict[str, object]]:
    revision = _fetch_cutoff_revision(BUY_LIMIT_TITLE)
    if revision is None:
        raise RuntimeError(f"Missing cutoff revision for {BUY_LIMIT_TITLE}")
    limits: dict[str, int] = {}
    titles: dict[str, str] = {}
    for exchange_title, raw_limit in _LIMIT_ROW_RE.findall(str(revision["content"])):
        limit = _parse_positive_int(raw_limit)
        if limit is None:
            continue
        normalized = _normalized_name(exchange_title)
        limits[normalized] = limit
        titles[normalized] = exchange_title
    if not limits:
        raise RuntimeError("The period buy-limit table parsed no rows")
    return limits, titles, revision


def _price_row(item_name: str, exchange_title: str) -> tuple[str, dict[str, object] | None]:
    revision = _fetch_cutoff_revision(f"Exchange:{exchange_title}")
    if revision is None:
        return item_name, None
    fields = _parse_fields(str(revision["content"]))
    price = _parse_positive_int(fields.get("price"))
    if price is None:
        return item_name, None
    return item_name, {
        "price": price,
        "page_title": str(revision["title"]),
        "oldid": int(revision["revid"]),
        "timestamp": str(revision["timestamp"]),
        "price_date": str(fields.get("date", "")),
        "page_item": str(fields.get("item", "")),
        "item_id": _parse_positive_int(fields.get("itemid")),
        "cache_value": _parse_positive_int(fields.get("value")),
        "page_limit": _parse_positive_int(fields.get("limit")),
    }


def harvest() -> dict[str, object]:
    item_names = _registered_item_names()
    limit_by_normalized, title_by_normalized, limit_revision = _buy_limit_table()

    buy_limits: dict[str, int] = {}
    exchange_titles: dict[str, str] = {}
    for item_name in item_names:
        matched_name = next(
            (
                candidate
                for candidate in _period_name_candidates(item_name)
                if _normalized_name(candidate) in title_by_normalized
            ),
            item_name,
        )
        normalized = _normalized_name(matched_name)
        exchange_title = title_by_normalized.get(normalized, item_name)
        exchange_titles[item_name] = exchange_title
        limit = limit_by_normalized.get(normalized)
        if limit is not None:
            buy_limits[item_name] = limit

    prices: dict[str, int] = {}
    provenance: dict[str, dict[str, object]] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(_price_row, item_name, exchange_titles[item_name]): item_name
            for item_name in item_names
        }
        for completed, future in enumerate(as_completed(futures), 1):
            item_name, row = future.result()
            if row is not None:
                prices[item_name] = int(row["price"])
                provenance[item_name] = row
                page_limit = row.get("page_limit")
                if isinstance(page_limit, int):
                    buy_limits[item_name] = page_limit
            if completed % 100 == 0:
                print(
                    f"harvested {completed}/{len(futures)} pages "
                    f"({len(prices)} prices)",
                    file=sys.stderr,
                )

    return {
        "prices": prices,
        "buy_limits": buy_limits,
        "provenance": provenance,
        "buy_limit_source": {
            "title": str(limit_revision["title"]),
            "oldid": int(limit_revision["revid"]),
            "timestamp": str(limit_revision["timestamp"]),
        },
        "registered_count": len(item_names),
    }


def _python_literal(value: object) -> str:
    return repr(value)


def write_generated(output_path: Path, harvested: Mapping[str, object]) -> None:
    prices = harvested["prices"]
    buy_limits = harvested["buy_limits"]
    provenance = harvested["provenance"]
    lines = [
        '"""Generated pre-EOC Grand Exchange data. Do not hand-edit.',
        "",
        "Sources are cutoff RuneScape Wiki Exchange revisions and the complete",
        "period buy-limit table. Regenerate with tools/generate_ge_period_data.py.",
        '"""',
        "",
        f"PERIOD_GE_BUY_LIMIT_SOURCE = {_python_literal(harvested['buy_limit_source'])}",
        "",
        "PERIOD_GE_GUIDE_PRICES = {",
    ]
    lines.extend(f"    {name!r}: {prices[name]}," for name in sorted(prices))
    lines.extend(["}", "", "PERIOD_GE_BUY_LIMITS = {"])
    lines.extend(f"    {name!r}: {buy_limits[name]}," for name in sorted(buy_limits))
    lines.extend(["}", "", "PERIOD_GE_PRICE_PROVENANCE = {"])
    for name in sorted(provenance):
        lines.append(f"    {name!r}: {_python_literal(provenance[name])},")
    lines.extend(["}", ""])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_ge_period_data.py <output-py>")
    harvested = harvest()
    output_path = Path(sys.argv[1])
    write_generated(output_path, harvested)
    print(
        f"wrote {len(harvested['prices'])} prices and "
        f"{len(harvested['buy_limits'])} buy limits for "
        f"{harvested['registered_count']} registered items"
    )


if __name__ == "__main__":
    main()
