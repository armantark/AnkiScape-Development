#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch Fletching icons from the source-backed target manifest.

The manifest is generated from ``fletching_data.py`` so row additions and asset
coverage stay tied together. Existing files are skipped unless ``--force`` is
provided.

Usage:
    uv run tools/fetch_fletching_assets.py
    uv run tools/fetch_fletching_assets.py --force
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

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.fletching_data import FLETCHING_TARGETS, fletching_item_names  # noqa: E402
from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
    wiki_title_for_item,
)

PROVENANCE = Path("assets_provenance.json")
FLETCHING_ITEMS_DIR = "fletcheditems"

WIKI_TITLE_OVERRIDES = {
    "Fletching": "Fletching icon (detail).png",
    "Adamant arrows": "Adamant arrow.png",
    "Adamant darts": "Adamant dart.png",
    "Arrow shafts": "Arrow shaft.png",
    "Broad arrow heads": "Broad arrowheads.png",
    "Broad-tipped bolts": "Broad bolts.png",
    "Bronze arrows": "Bronze arrow.png",
    "Bronze darts": "Bronze dart.png",
    "Dragon arrows": "Dragon arrow.png",
    "Dragon darts": "Dragon dart.png",
    "Dragon bolt tips": "Dragonstone bolt tips.png",
    "Flighted ogre arrows": "Flighted ogre arrow.png",
    "Headless arrows": "Headless arrow.png",
    "Iron arrows": "Iron arrow.png",
    "Iron darts": "Iron dart.png",
    "Mithril arrows": "Mithril arrow.png",
    "Mithril darts": "Mithril dart.png",
    "Rune arrows": "Rune arrow.png",
    "Rune darts": "Rune dart.png",
    "Steel arrows": "Steel arrow.png",
    "Steel darts": "Steel dart.png",
}


def _slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


def _fletching_item(name: str) -> str:
    return f"{FLETCHING_ITEMS_DIR}/{_slug(name)}.png"


def _manifest() -> List[Tuple[str, str, str, Optional[int]]]:
    manifest: List[Tuple[str, str, str, Optional[int]]] = []
    seen = set()
    for target in FLETCHING_TARGETS:
        seen.add(target.output_item)
    for item_name in fletching_item_names():
        seen.add(item_name)
    for item_name in sorted(seen):
        manifest.append(
            (
                item_name,
                WIKI_TITLE_OVERRIDES.get(item_name, item_name),
                _fletching_item(item_name),
                None,
            )
        )
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
