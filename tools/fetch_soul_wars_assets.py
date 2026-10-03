#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Soul Wars art."""

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
    RS3_WIKI,
    fetch_asset,
)


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    return (
        (
            AssetRequest(
                item_name="Soul Wars",
                wiki_title="Soul fragment.png",
                output_path=ROOT / "activityicons" / "soul_wars.png",
                provenance_path=provenance,
            ),
            64,
        ),
        (
            AssetRequest(
                item_name="Soul fragment",
                wiki_title="Soul fragment.png",
                output_path=ROOT / "activityitems" / "soul_wars_soul_fragment.png",
                provenance_path=provenance,
            ),
            48,
        ),
        (
            AssetRequest(
                item_name="Enemy team avatar",
                wiki_title="Avatar of Destruction.png",
                output_path=(
                    ROOT / "combatenemies" / "soul_wars_enemy_avatar.png"
                ),
                provenance_path=provenance,
            ),
            48,
        ),
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
