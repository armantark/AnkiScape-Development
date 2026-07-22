#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized Phoenix Lair activity, reward, and egg art."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    OSRS_WIKI,
    RS3_WIKI,
    fetch_asset,
)

PRE_EOC_CUTOFF = "2012-11-20T23:59:59Z"


def asset_manifest() -> tuple[tuple[AssetRequest, int | None], ...]:
    provenance = ROOT / "assets_provenance.json"
    rows = (
        (
            "Phoenix quill",
            "Phoenix quill.png",
            ROOT / "activityitems" / "phoenix_quill.png",
            None,
        ),
        (
            "Phoenix egg",
            "Phoenix egg.png",
            ROOT / "activityitems" / "phoenix_egg.png",
            None,
        ),
        (
            "Cracked phoenix egg",
            "Cracked phoenix egg.png",
            ROOT / "activityitems" / "cracked_phoenix_egg.png",
            None,
        ),
    )
    return tuple(
        (
            AssetRequest(
                item_name=item_name,
                wiki_title=wiki_title,
                output_path=output_path,
                provenance_path=provenance,
            ),
            size,
        )
        for item_name, wiki_title, output_path, size in rows
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    period_client = HttpWikiClient(
        min_interval_seconds=1.1,
        before_timestamp=PRE_EOC_CUTOFF,
    )
    current_client = HttpWikiClient(min_interval_seconds=1.1)
    for request, size in asset_manifest():
        try:
            outcome = fetch_asset(
                request,
                period_client,
                size=size,
                force=args.force,
                dry_run=args.dry_run,
                sources=(OSRS_WIKI, RS3_WIKI),
            )
        except AssetFetchError:
            outcome = fetch_asset(
                request,
                current_client,
                size=size,
                force=args.force,
                dry_run=args.dry_run,
                sources=(OSRS_WIKI, RS3_WIKI),
            )
        print(f"{outcome.item_name}: {outcome.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
