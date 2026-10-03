#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Clan Wars activity art."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.clan_wars_data import CLAN_WARS_ASSET_MANIFEST  # noqa: E402
from tools.fetch_assets import (  # noqa: E402
    PRE_EOC_CUTOFF,
    AssetRequest,
    HttpWikiClient,
    RS3_WIKI,
    fetch_asset,
)


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    return tuple(
        (
            AssetRequest(
                item_name=str(row["item_name"]),
                wiki_title=str(row["wiki_title"]),
                output_path=ROOT / str(row["output_path"]),
                provenance_path=provenance,
            ),
            int(row["size"]),
        )
        for row in CLAN_WARS_ASSET_MANIFEST
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
