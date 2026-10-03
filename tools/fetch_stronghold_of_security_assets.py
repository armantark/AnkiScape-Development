#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Stronghold of Security reward art.

Separate from fetch_stronghold_player_safety_assets.py: the Stronghold of
Security is the one-time landmark whose completion pays out the two stat-identical
boots, while the Stronghold of Player Safety is the later activity with the
safety gloves. Only the boots need art here.

The item rows already exist (stronghold_of_security_data.py, ids 9005/9006), and
constants.py builds STRONGHOLD_OF_SECURITY_ITEM_IMAGES from
activityitems/stronghold_of_security_<slug>.png and then filters to files that
exist — so until these two land the map is empty and both boots render iconless.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import (  # noqa: E402
    PRE_EOC_CUTOFF,
    AssetRequest,
    HttpWikiClient,
    OSRS_WIKI,
    RS3_WIKI,
    fetch_asset,
)


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    return tuple(
        (
            AssetRequest(
                item_name=item_name,
                wiki_title=f"{item_name}.png",
                output_path=(
                    ROOT / "activityitems" / f"stronghold_of_security_{slug}.png"
                ),
                provenance_path=provenance,
            ),
            48,
        )
        # Slugs must match constants._asset_slug, which is what builds the
        # lookup the Bank and Equipment tabs read.
        for item_name, slug in (
            ("Fancy boots", "fancy_boots"),
            ("Fighting boots", "fighting_boots"),
        )
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
            sources=(RS3_WIKI, OSRS_WIKI),
        )
        print(f"{outcome.item_name}: {outcome.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
