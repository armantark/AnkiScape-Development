#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Castle Wars activity and reward art."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import PRE_EOC_CUTOFF, AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset  # noqa: E402


def asset_manifest() -> tuple[tuple[AssetRequest, int | None], ...]:
    provenance = ROOT / "assets_provenance.json"
    rows = (
        ("Castle wars ticket", "Castle wars ticket old.png"),
        ("Basic decorative platebody", "Basic decorative platebody.png"),
        ("Basic decorative platelegs", "Basic decorative platelegs.png"),
        ("Basic decorative shield", "Basic decorative shield.png"),
        ("Ballista base", "Ballista base.png"),
        ("Ballista bolt stack", "Ballista bolt stack.png"),
        ("Ballista bow", "Ballista bow.png"),
        ("Ballista chamber", "Ballista chamber.png"),
        ("Ballista ammo", "Ballista ammo.png"),
        ("Saradomin halo", "Saradomin halo.png"),
        ("Castle wars hobbyist cape", "Castle Wars hobbyist cape.png"),
        ("Castlewars chinchompa", "Castle Wars chinchompa.png"),
    )
    requests = [
        (
            AssetRequest(
                item_name="Castle Wars",
                wiki_title="Castle wars ticket old.png",
                output_path=ROOT / "activityicons" / "castle_wars.png",
                provenance_path=provenance,
            ),
            64,
        )
    ]
    requests.extend(
        (
            AssetRequest(
                item_name=item_name,
                wiki_title=wiki_title,
                output_path=(
                    ROOT
                    / "activityitems"
                    / f"castle_wars_{item_name.lower().replace(' ', '_')}.png"
                ),
                provenance_path=provenance,
            ),
            None,
        )
        for item_name, wiki_title in rows
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
