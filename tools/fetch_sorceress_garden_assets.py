#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Sorceress's Garden activity and item art."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset  # noqa: E402

PRE_EOC_CUTOFF = "2012-11-20T23:59:59Z"


def asset_manifest() -> tuple[tuple[AssetRequest, int | None], ...]:
    provenance = ROOT / "assets_provenance.json"
    requests: list[tuple[AssetRequest, int | None]] = [
        (
            AssetRequest(
                item_name="Sorceress's Garden",
                wiki_title="Summer sq'irk.png",
                output_path=ROOT / "activityicons" / "sorceress_garden.png",
                provenance_path=provenance,
            ),
            64,
        )
    ]
    for item_name, wiki_title, file_name in (
        ("Winter sq'irk", "Winter sq'irk.png", "winter_sq_irk.png"),
        ("Winter sq'irkjuice", "Winter sq'irkjuice.png", "winter_sq_irkjuice.png"),
        ("Spring sq'irk", "Spring sq'irk.png", "spring_sq_irk.png"),
        ("Spring sq'irkjuice", "Spring sq'irkjuice.png", "spring_sq_irkjuice.png"),
        ("Autumn sq'irk", "Autumn sq'irk.png", "autumn_sq_irk.png"),
        ("Autumn sq'irkjuice", "Autumn sq'irkjuice.png", "autumn_sq_irkjuice.png"),
        ("Summer sq'irk", "Summer sq'irk.png", "summer_sq_irk.png"),
        ("Summer sq'irkjuice", "Summer sq'irkjuice.png", "summer_sq_irkjuice.png"),
    ):
        requests.append(
            (
                AssetRequest(
                    item_name=item_name,
                    wiki_title=wiki_title,
                    output_path=ROOT / "activityitems" / file_name,
                    provenance_path=provenance,
                ),
                None,
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
