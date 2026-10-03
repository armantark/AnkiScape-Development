#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch Daily Challenges reward art and the owner-selected top-level icon.

The reward items were released with the Challenge System on 19 September 2012,
so their newest revisions before the EOC cutoff are period art. The requested
Daily Challenge icon has no pre-cutoff wiki revision; its earliest archived
upload is pinned instead of silently taking the current image.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

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


DAILY_CHALLENGE_ICON_REVISION = "2014-04-18T11:21:12Z"
CHALLENGE_ICON_PATH = ROOT / "icon" / "challenges_icon.png"


def asset_manifest() -> tuple[tuple[AssetRequest, Optional[int], bool], ...]:
    provenance = ROOT / "assets_provenance.json"
    return (
        (
            AssetRequest(
                item_name="Challenge Mystery Bag",
                wiki_title="Challenge Mystery Bag.png",
                output_path=ROOT / "activityitems" / "challenge_mystery_bag.png",
                provenance_path=provenance,
            ),
            48,
            False,
        ),
        (
            AssetRequest(
                item_name="Challenge XP Lamp",
                wiki_title="Challenge XP Lamp.png",
                output_path=ROOT / "activityitems" / "challenge_xp_lamp.png",
                provenance_path=provenance,
            ),
            48,
            False,
        ),
        (
            AssetRequest(
                item_name="Daily Challenge icon",
                wiki_title="Daily Challenge icon.png",
                output_path=CHALLENGE_ICON_PATH,
                provenance_path=provenance,
            ),
            None,
            True,
        ),
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
    challenge_icon_client = HttpWikiClient(
        min_interval_seconds=1.1,
        before_timestamp=DAILY_CHALLENGE_ICON_REVISION,
    )
    requests = asset_manifest()
    if not args.force and not args.dry_run:
        requests = tuple(row for row in requests if not row[0].output_path.exists())
    for request, size, preserve_source in requests:
        is_challenge_icon = request.output_path == CHALLENGE_ICON_PATH
        outcome = fetch_asset(
            request,
            challenge_icon_client if is_challenge_icon else period_client,
            size=size,
            force=args.force,
            dry_run=args.dry_run,
            sources=(RS3_WIKI,),
            preserve_source=preserve_source,
        )
        print(f"{outcome.item_name}: {outcome.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
