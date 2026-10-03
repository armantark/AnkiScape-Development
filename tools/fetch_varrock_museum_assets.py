#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Varrock Museum activity and find art."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import PRE_EOC_CUTOFF, AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset  # noqa: E402


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    requests = [
        (
            AssetRequest(
                item_name="Varrock Museum",
                wiki_title="Specimen brush.png",
                output_path=ROOT / "activityicons" / "varrock_museum.png",
                provenance_path=provenance,
            ),
            64,
        )
    ]
    for item_name in (
        "Trowel",
        "Rock pick",
        "Specimen brush",
        "Uncleaned find",
        "Pottery",
        "Old coin",
        "Ancient coin",
        "Ancient symbol",
        "Old symbol",
        "Clean necklace",
    ):
        requests.append(
            (
                AssetRequest(
                    item_name=item_name,
                    wiki_title=f"{item_name}.png",
                    output_path=(
                        ROOT
                        / "activityitems"
                        / f"varrock_museum_{item_name.lower().replace(' ', '_')}.png"
                    ),
                    provenance_path=provenance,
                ),
                48,
            )
        )
    return tuple(requests)


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
