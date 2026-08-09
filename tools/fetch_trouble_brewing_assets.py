#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Trouble Brewing activity and reward art."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset  # noqa: E402

import pkg_alias  # noqa: E402,F401  (installs the ankiscape package alias)
from ankiscape.data.trouble_brewing_data import TROUBLE_BREWING_REWARDS  # noqa: E402

PRE_EOC_CUTOFF = "2012-11-20T23:59:59Z"
_WIKI_FILE_TITLES = {
    "Red rum": "Rum (red).png",
    "Blue rum": "Rum (blue).png",
}


def _asset_filename(item_name: str) -> str:
    if item_name == "Blue tricorn hat":
        return "blue_tricorn_hat.png"
    slug = "_".join(re.findall(r"[a-z0-9]+", item_name.lower()))
    return f"trouble_brewing_{slug}.png"


def asset_manifest() -> tuple[tuple[AssetRequest, int | None], ...]:
    provenance = ROOT / "assets_provenance.json"
    requests = [
        (
            AssetRequest(
                item_name="Trouble Brewing",
                wiki_title="Pieces of eight.png",
                output_path=ROOT / "activityicons" / "trouble_brewing.png",
                provenance_path=provenance,
            ),
            64,
        ),
    ]
    requests.extend(
        (
            AssetRequest(
                item_name=reward.display_name,
                wiki_title=_WIKI_FILE_TITLES.get(
                    reward.display_name, f"{reward.display_name}.png"
                ),
                output_path=(
                    ROOT / "activityitems" / _asset_filename(reward.display_name)
                ),
                provenance_path=provenance,
            ),
            48,
        )
        for reward in TROUBLE_BREWING_REWARDS
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
