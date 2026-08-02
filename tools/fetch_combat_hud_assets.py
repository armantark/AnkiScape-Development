#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the cutoff-era hitpoints, Prayer, and Summoning HUD orb icons."""

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


def asset_manifest() -> tuple[AssetRequest, ...]:
    provenance = ROOT / "assets_provenance.json"
    return (
        AssetRequest(
            item_name="Hitpoints orb icon",
            wiki_title="Constitution-icon.png",
            output_path=ROOT / "icon" / "hitpoints_orb.png",
            provenance_path=provenance,
        ),
        AssetRequest(
            item_name="Prayer orb icon",
            wiki_title="Prayer-icon.png",
            output_path=ROOT / "icon" / "prayer_orb.png",
            provenance_path=provenance,
        ),
        AssetRequest(
            item_name="Summoning orb icon",
            wiki_title="Summoning-icon.png",
            output_path=ROOT / "icon" / "summoning_orb.png",
            provenance_path=provenance,
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
    requests = asset_manifest()
    if not args.force and not args.dry_run:
        requests = tuple(request for request in requests if not request.output_path.exists())
    for request in requests:
        outcome = fetch_asset(
            request,
            client,
            force=args.force,
            dry_run=args.dry_run,
            sources=(RS3_WIKI,),
            preserve_source=True,
        )
        print(f"{outcome.item_name}: {outcome.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
