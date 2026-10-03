#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Duel Arena and Duellist's cap art."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import (  # noqa: E402
    PRE_EOC_CUTOFF,
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    RS3_WIKI,
    fetch_asset,
)


CAP_TITLES = (
    "Duellist's cap (tier 1).png",
    "Duellist's cap (tier 2).png",
    "Duellist's cap (tier 3).png",
    "Duellist's cap (tier 4).png",
    "Duellist's cap (tier 5).png",
    "Duellist's cap (tier 6).png",
)


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    requests: list[tuple[AssetRequest, int]] = [
        (
            AssetRequest(
                item_name="Duel Arena",
                wiki_title=CAP_TITLES[0],
                output_path=ROOT / "activityicons" / "duel_arena.png",
                provenance_path=provenance,
            ),
            64,
        )
    ]
    for tier, title in enumerate(CAP_TITLES, start=1):
        requests.append(
            (
                AssetRequest(
                    item_name=f"Duellist's cap (tier {tier})",
                    wiki_title=title,
                    output_path=(
                        ROOT
                        / "activityitems"
                        / f"duellists_cap_tier_{tier}.png"
                    ),
                    provenance_path=provenance,
                ),
                64,
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
    current_client = HttpWikiClient(min_interval_seconds=1.1)
    for request, size in asset_manifest():
        try:
            outcome = fetch_asset(
                request,
                client,
                size=size,
                force=args.force,
                dry_run=args.dry_run,
                sources=(RS3_WIKI,),
            )
        except AssetFetchError:
            # The exact period cap sprites were named in the pinned 2012 pages,
            # but their migrated wiki file histories begin in 2022. Current
            # exact item art is an asset-only fallback, never mechanics evidence.
            outcome = fetch_asset(
                request,
                current_client,
                size=size,
                force=args.force,
                dry_run=args.dry_run,
                sources=(RS3_WIKI,),
            )
        print(f"{outcome.item_name}: {outcome.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
