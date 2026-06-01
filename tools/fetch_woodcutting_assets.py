#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Batch-fetch the Woodcutting parity icons through a single rate-limited client.

This drives ``tools/fetch_assets.py`` for the whole Woodcutting manifest (tree
row sprites, hatchets, bird nests, and seed contents) in one process so the
wiki rate limiter is shared and provenance is recorded for each file. It is a
developer-only tool and never runs inside Anki.

Design notes:
- Icons are fetched *untrimmed-but-alpha-cropped* (no ``--size`` pad) so they
  land tight to the opaque box and render correctly with a plain QIcon — the
  same "preprocess, display as-is" contract as the rest of the item art.
- Item file names use the same slug as ``constants._asset_slug`` so the
  generated ``WOODCUTTING_EXTRA_ITEM_IMAGES`` map finds them.
- Egg bird-nests and bird's eggs are intentionally omitted: their wiki File
  titles don't resolve cleanly and they are vanishingly rare drops, so those
  rows stay iconless rather than blocking the batch.
- Re-runs skip files that already exist unless ``--force`` is passed.

Usage:
    uv run tools/fetch_woodcutting_assets.py
    uv run tools/fetch_woodcutting_assets.py --force
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

from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
    wiki_title_for_item,
)

PROVENANCE = Path("assets_provenance.json")
WC_ITEMS_DIR = "woodcuttingitems"


def _slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


def _wc_item(name: str) -> str:
    return f"{WC_ITEMS_DIR}/{_slug(name)}.png"


# (wiki item name, output path relative to repo root). Tree rows reuse the
# legacy display-name-keyed trees/ folder; bank items use the slugged folder.
HATCHETS = [
    "Bronze hatchet", "Iron hatchet", "Steel hatchet", "Black hatchet",
    "Mithril hatchet", "Adamant hatchet", "Rune hatchet", "Dragon hatchet",
]
SEEDS = [
    "Acorn", "Apple tree seed", "Willow seed", "Banana tree seed",
    "Orange tree seed", "Curry tree seed", "Maple seed", "Pineapple seed",
    "Papaya tree seed", "Yew seed", "Palm tree seed", "Calquat tree seed",
    "Spirit seed", "Magic seed",
]
NESTS = ["Bird's nest (seeds)", "Bird's nest (ring)", "Bird's nest (empty)"]

MANIFEST: List[Tuple[str, str]] = (
    [
        ("Achey tree logs", "trees/Achey.png"),
        ("Bark", "trees/Hollow.png"),
        ("Ivy", "trees/Ivy.png"),
    ]
    + [(name, _wc_item(name)) for name in HATCHETS]
    + [(name, _wc_item(name)) for name in NESTS]
    + [(name, _wc_item(name)) for name in SEEDS]
)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve without downloading.")
    args = parser.parse_args(argv)

    client = HttpWikiClient()
    ok = skipped = failed = 0
    failures: List[str] = []
    for item_name, out_rel in MANIFEST:
        request = AssetRequest(
            item_name=item_name,
            wiki_title=wiki_title_for_item(item_name),
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
