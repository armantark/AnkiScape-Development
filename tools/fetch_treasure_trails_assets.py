#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Treasure Trails clue, casket and reward art."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import (  # noqa: E402
    AssetRequest,
    HttpWikiClient,
    RS3_WIKI,
    fetch_asset,
)


PRE_EOC_CUTOFF = "2012-11-20T23:59:59Z"

_ITEMS = (
    # The tier-named files were uploaded after the cutoff, so the period art is
    # the Treasure Trails banner and the untiered casket icon.
    ("Treasure Trails", "Mg treasuretrails.jpg", "treasure_trail", "activityicons"),
    ("Clue scroll (hard)", "Clue scroll (hard).png", "clue_scroll_hard", "activityitems"),
    ("Casket (easy)", "Casket.png", "casket_easy", "activityitems"),
    ("Black platebody (t)", "Black platebody (t).png", "black_platebody_t", "activityitems"),
    ("Black full helm (t)", "Black full helm (t).png", "black_full_helm_t", "activityitems"),
    ("Highwayman mask", "Highwayman mask.png", "highwayman_mask", "activityitems"),
    ("Amulet of magic (t)", "Amulet of magic (t).png", "amulet_of_magic_t", "activityitems"),
    ("Black cane", "Black cane.png", "black_cane", "activityitems"),
    ("Spiked helmet", "Spiked helmet.png", "spiked_helmet", "activityitems"),
    ("Purple sweets", "Purple sweets.png", "purple_sweets", "activityitems"),
)


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    return tuple(
        (
            AssetRequest(
                item_name=item_name,
                wiki_title=wiki_title,
                output_path=ROOT / folder / f"{slug}.png",
                provenance_path=provenance,
            ),
            64 if folder == "activityicons" else 48,
        )
        for item_name, wiki_title, slug, folder in _ITEMS
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    client = HttpWikiClient(
        min_interval_seconds=1.1,
        before_timestamp=PRE_EOC_CUTOFF,
    )
    for request, size in asset_manifest():
        outcome = fetch_asset(
            request,
            client,
            size=size,
            force=args.force,
            dry_run=args.dry_run,
            sources=(RS3_WIKI,),
        )
        print(f"{outcome.item_name}: {outcome.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
