#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Enchanted key treasure-hunt art."""

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


def asset_manifest() -> tuple[tuple[AssetRequest, int | None], ...]:
    provenance = ROOT / "assets_provenance.json"
    rows = (
        # The RS3 file is disambiguated by quest, and only it carries a
        # pre-cutoff revision; the OSRS "Enchanted key.png" was re-uploaded in
        # 2021.
        ("Enchanted key", "Enchanted key (Making History).png", ROOT / "questitems" / "enchanted_key.png", None),
        ("Enchanted Key", "Enchanted key (Making History).png", ROOT / "activityicons" / "enchanted_key.png", 64),
        ("Guthix mjolnir", "Guthix mjolnir.png", ROOT / "activityitems" / "guthix_mjolnir.png", None),
        ("Saradomin mjolnir", "Saradomin mjolnir.png", ROOT / "activityitems" / "saradomin_mjolnir.png", None),
        ("Zamorak mjolnir", "Zamorak mjolnir.png", ROOT / "activityitems" / "zamorak_mjolnir.png", None),
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
                sources=(RS3_WIKI,),
            )
        except AssetFetchError:
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
