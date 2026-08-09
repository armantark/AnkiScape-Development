#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Great Orb Project activity and reward art."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset  # noqa: E402

PRE_EOC_CUTOFF = "2012-11-20T23:59:59Z"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    client = HttpWikiClient(
        min_interval_seconds=1.1,
        before_timestamp=PRE_EOC_CUTOFF,
    )
    requests = (
        AssetRequest(
            item_name="Great Orb Project",
            wiki_title="The_Great_Orb_Project.png",
            output_path=ROOT / "activityicons" / "great_orb_project.png",
            provenance_path=ROOT / "assets_provenance.json",
        ),
        *(
            AssetRequest(
                item_name=item_name,
                wiki_title=wiki_title,
                output_path=ROOT / "activityitems" / filename,
                provenance_path=ROOT / "assets_provenance.json",
            )
            for item_name, wiki_title, filename in (
                (
                    "Master runecrafter hat",
                    "Master_runecrafter_hat.png",
                    "master_runecrafter_hat.png",
                ),
                (
                    "Master runecrafter body",
                    "Master_runecrafter_robe.png",
                    "master_runecrafter_body.png",
                ),
                (
                    "Master runecrafter skirt",
                    "Master_runecrafter_skirt.png",
                    "master_runecrafter_skirt.png",
                ),
                (
                    "Master runecrafter boots",
                    "Master_runecrafter_boots.png",
                    "master_runecrafter_boots.png",
                ),
            )
        ),
    )
    for request in requests:
        outcome = fetch_asset(
            request,
            client,
            size=64,
            force=args.force,
            dry_run=args.dry_run,
            sources=(RS3_WIKI,),
        )
        print(f"{outcome.item_name}: {outcome.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
