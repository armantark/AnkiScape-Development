#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch NPC shop stock icons derived from SHOP_DATA.

The manifest is every visible live/locked stock item whose registry entry has
no existing asset anywhere (cross-skill folders included), so the fetch can't
drift from the generated catalog and never re-downloads art another skill
already owns.

Usage:
    uv run tools/fetch_shop_assets.py
    uv run tools/fetch_shop_assets.py --force
    uv run tools/fetch_shop_assets.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from constants import ITEM_DEFINITIONS  # noqa: E402
from item_registry import item_definitions_by_storage_key  # noqa: E402
from shop_data import SHOP_DATA  # noqa: E402
from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
    wiki_title_for_item,
)

PROVENANCE = Path("assets_provenance.json")
SHOP_ITEMS_DIR = "shopitems"

# Titles whose wiki file name doesn't match the storage key. Dose/quantity
# variants and disambiguated pages land here as failures surface.
WIKI_TITLE_OVERRIDES = {
    "Dorgeshuun c'bow": "Dorgeshuun crossbow.png",
    "Mith crossbow": "Mithril crossbow.png",
    "Adamant brutal": "Adamant brutal 5.png",
    "Black brutal": "Black brutal 5.png",
    "Bronze brutal": "Bronze brutal 5.png",
    "Iron brutal": "Iron brutal 5.png",
    "Mithril brutal": "Mithril brutal 5.png",
    "Rune brutal": "Rune brutal 5.png",
    "Steel brutal": "Steel brutal 5.png",
}


def _slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


def _manifest() -> List[Tuple[str, str, str]]:
    defs = item_definitions_by_storage_key(ITEM_DEFINITIONS)
    names = set()
    for shop in SHOP_DATA.values():
        if shop.get("visibility") == "hidden":
            continue
        for row in shop.get("stock", []):
            item_name = str(row.get("item_name", ""))
            if not item_name or row.get("disposition") == "blocked":
                continue
            definition = defs.get(item_name)
            asset_path = getattr(definition, "asset_path", None) if definition else None
            if asset_path and os.path.exists(asset_path):
                continue
            names.add(item_name)
    return [
        (
            item_name,
            WIKI_TITLE_OVERRIDES.get(item_name, item_name),
            f"{SHOP_ITEMS_DIR}/{_slug(item_name)}.png",
        )
        for item_name in sorted(names)
    ]


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve without downloading.")
    args = parser.parse_args(argv)

    manifest = _manifest()
    print(f"{len(manifest)} shop stock items need icons.")
    client = HttpWikiClient()
    ok = skipped = failed = 0
    failures: List[str] = []
    for item_name, wiki_title, out_rel in manifest:
        request = AssetRequest(
            item_name=item_name,
            wiki_title=wiki_title_for_item(item_name, wiki_title),
            output_path=Path(out_rel),
            provenance_path=PROVENANCE,
        )
        try:
            outcome = fetch_asset(request, client, size=None, force=args.force, dry_run=args.dry_run)
        except AssetFetchError as exc:
            failed += 1
            failures.append(f"{item_name}: {exc}")
            print(f"  FAIL {item_name} -> {out_rel}: {exc}")
            continue
        if outcome.skipped_existing:
            skipped += 1
            print(f"  skip {item_name} (exists) -> {out_rel}")
        else:
            ok += 1
            print(f"  ok   {item_name} [{outcome.source_wiki}] -> {out_rel}")

    print(f"\nDone. {ok} fetched, {skipped} skipped, {failed} failed.")
    if failures:
        print("Failures:")
        for line in failures:
            print(f"  - {line}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
