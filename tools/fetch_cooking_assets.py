#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch Cooking icons needed by the skill expansion.

The manifest is derived from ``cooking_data.py``/``constants`` so new Cooking
targets or prep activities automatically acquire a fetch candidate. Existing
Fishing, Crafting, Mining, Smithing, and Woodcutting art is reused; the script
only writes Cooking-specific sprites to ``cookingitems/`` plus the skill icon.

Usage:
    uv run tools/fetch_cooking_assets.py
    uv run tools/fetch_cooking_assets.py --dry-run
    uv run tools/fetch_cooking_assets.py --force
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (  # noqa: E402
    BAR_IMAGES,
    COOKING_EXTRA_ITEM_DATA,
    COOKING_ITEMS_FOLDER,
    CRAFTED_ITEM_IMAGES,
    FISHING_ITEM_IMAGES,
    GEM_IMAGES,
    LOG_IMAGES,
    ORE_IMAGES,
    TREE_IMAGES,
    _asset_slug,
)
from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
    wiki_title_for_item,
)

PROVENANCE = Path("assets_provenance.json")
PRE_EOC_CUTOFF = "2012-11-20T00:00:00Z"
_COOKING_ITEMS_REL = Path(COOKING_ITEMS_FOLDER).relative_to(REPO_ROOT)

_COVERED_ELSEWHERE = (
    set(FISHING_ITEM_IMAGES)
    | set(CRAFTED_ITEM_IMAGES)
    | set(ORE_IMAGES)
    | set(GEM_IMAGES)
    | set(BAR_IMAGES)
    | set(LOG_IMAGES)
    | set(TREE_IMAGES)
)

WIKI_TITLE_OVERRIDES: Dict[str, str] = {
    "Cooking": "Cooking icon (detail).png",
    "Burnt fish": "Burnt fish (trout).png",
    "Cooked meat": "Cooked meat.png",
    "Mushrooms": "Mushroom.png",
    "Uncooked berry pie": "Uncooked berry pie.png",
    # The wiki files the cocktail articles use are title-cased.
    "Fruit blast": "Fruit Blast.png",
    "Pineapple punch": "Pineapple Punch.png",
    "Wizard blizzard": "Wizard Blizzard.png",
    "Short green guy": "Short Green Guy.png",
    "Drunk dragon": "Drunk Dragon.png",
    "Blurberry special": "Blurberry Special.png",
    "Dwarven stout (m)": "Dwarven stout (m).png",
}


def _manifest() -> List[Tuple[str, str, str, Optional[int]]]:
    manifest: List[Tuple[str, str, str, Optional[int]]] = []
    for item_name in sorted(COOKING_EXTRA_ITEM_DATA):
        if item_name in _COVERED_ELSEWHERE:
            continue
        out_rel = str(_COOKING_ITEMS_REL / f"{_asset_slug(item_name)}.png")
        manifest.append((item_name, WIKI_TITLE_OVERRIDES.get(item_name, item_name), out_rel, None))
    return manifest


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve without downloading.")
    parser.add_argument("--item", action="append", default=[], help="Fetch only this item name; repeat as needed.")
    args = parser.parse_args(argv)

    manifest = _manifest()
    if args.item:
        requested = set(args.item)
        manifest = [row for row in manifest if row[0] in requested]
    client = HttpWikiClient(before_timestamp=PRE_EOC_CUTOFF)
    ok = skipped = failed = 0
    failures: List[str] = []
    print(f"Resolving {len(manifest)} Cooking icons...")
    for item_name, wiki_title, out_rel, size in manifest:
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
