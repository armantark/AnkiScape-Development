#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Managing Miscellania activity art."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import PRE_EOC_CUTOFF, AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    outcome = fetch_asset(
        AssetRequest(
            item_name="Managing Miscellania",
            wiki_title="Managing_Miscellania_interface.png",
            output_path=ROOT / "activityicons" / "managing_miscellania.png",
            provenance_path=ROOT / "assets_provenance.json",
        ),
        HttpWikiClient(
            min_interval_seconds=1.1,
            before_timestamp=PRE_EOC_CUTOFF,
        ),
        size=64,
        force=args.force,
        dry_run=args.dry_run,
        sources=(RS3_WIKI,),
    )
    print(f"{outcome.item_name}: {outcome.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
