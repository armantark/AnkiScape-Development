#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Fish Flingers activity and reward art."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.fish_flingers_data import fish_flingers_extra_items_as_dict  # noqa: E402
from tools.fetch_assets import PRE_EOC_CUTOFF, AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset  # noqa: E402


def _slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    requests = [
        (
            AssetRequest(
                item_name="Fish Flingers",
                wiki_title="Fishing hat.png",
                output_path=ROOT / "activityicons" / "fish_flingers.png",
                provenance_path=provenance,
            ),
            64,
        )
    ]
    wiki_titles = {
        "Fishing hat": "Fishing hat.png",
        "Fishing jacket": "Fishing jacket.png",
        "Fishing waders": "Fishing waders.png",
        "Fishing boots": "Fishing boots.png",
        "Beginner's tackle box": "Beginner's tackle box.png",
        "Basic tackle box": "Basic_tackle_box.png",
        "Standard tackle box": "Standard_tackle_box.png",
        "Professional tackle box": "Professional tackle box.png",
        "Champion's tackle box": "Champion's_tackle_box.png",
    }
    for item_name in fish_flingers_extra_items_as_dict():
        requests.append(
            (
                AssetRequest(
                    item_name=item_name,
                    wiki_title=wiki_titles[item_name],
                    output_path=ROOT / "activityitems" / f"{_slug(item_name)}.png",
                    provenance_path=provenance,
                ),
                64,
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
