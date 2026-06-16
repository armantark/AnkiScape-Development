#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch Fishing icons needed by the v1 skill expansion.

The manifest is derived from ``fishing_data.py`` and intentionally contains no
reusable Fishing implements. Player-facing Fishing rows are output-first, and
only consumable materials need visible inventory art.

Usage:
    uv run tools/fetch_fishing_assets.py
    uv run tools/fetch_fishing_assets.py --force
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fishing_data import (  # noqa: E402
    FISHING_MATERIAL_ITEM_IDS,
    FISHING_METHODS,
    FISH_BY_ID,
)
from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
    wiki_title_for_item,
)

PROVENANCE = Path("assets_provenance.json")
FISHING_ITEMS_DIR = "fishingitems"

WIKI_TITLE_OVERRIDES = {
    "Fishing": "Fishing icon (detail).png",
}


def _slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


def _fishing_item(name: str) -> str:
    return f"{FISHING_ITEMS_DIR}/{_slug(name)}.png"


def _manifest() -> List[Tuple[str, str, str, Optional[int]]]:
    manifest: List[Tuple[str, str, str, Optional[int]]] = [
        ("Fishing", WIKI_TITLE_OVERRIDES["Fishing"], "icon/fishing_icon.png", 64),
        ("Fishing bait", wiki_title_for_item("Fishing bait"), _fishing_item("Fishing bait"), None),
        ("Fishing bait", wiki_title_for_item("Fishing bait"), "activityicons/gather_fishing_bait.png", None),
    ]
    seen = {"Fishing bait"}
    for method in FISHING_METHODS:
        for fish_id in method.fish_ids:
            fish = FISH_BY_ID[fish_id]
            if fish.output_item in seen:
                continue
            manifest.append((fish.output_item, wiki_title_for_item(fish.output_item), _fishing_item(fish.output_item), None))
            seen.add(fish.output_item)
        for material_name in method.bait_items:
            if material_name in seen:
                continue
            manifest.append((material_name, wiki_title_for_item(material_name), _fishing_item(material_name), None))
            seen.add(material_name)
    for material_name in FISHING_MATERIAL_ITEM_IDS:
        if material_name in seen:
            continue
        manifest.append((material_name, wiki_title_for_item(material_name), _fishing_item(material_name), None))
        seen.add(material_name)
    return manifest


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve without downloading.")
    args = parser.parse_args(argv)

    client = HttpWikiClient()
    ok = skipped = failed = 0
    failures: List[str] = []
    for item_name, wiki_title, out_rel, size in _manifest():
        request = AssetRequest(
            item_name=item_name,
            wiki_title=wiki_title_for_item(item_name, wiki_title),
            output_path=Path(out_rel),
            provenance_path=PROVENANCE,
        )
        try:
            outcome = fetch_asset(request, client, size=size, force=args.force, dry_run=args.dry_run)
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
