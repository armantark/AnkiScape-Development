#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Achievement Diary and Capes of Distinction art.

Every request is pinned before the EOC cutoff, so a modern RS3 redesign of a
cape or a diary item cannot leak into the add-on. Provenance for each file lands
in ``assets_provenance.json`` beside every other fetched asset.
"""

from __future__ import annotations

import argparse
import re
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

# The eight regional equipment families the design contract fixes, plus the
# Beginner-only Lumbridge/Draynor ring. Tier numbering is the period's own.
DIARY_REWARD_ITEMS = (
    *(f"Ardougne cloak {tier}" for tier in range(1, 5)),
    *(f"Falador shield {tier}" for tier in range(1, 5)),
    *(f"Fremennik sea boots {tier}" for tier in range(1, 5)),
    *(f"Karamja gloves {tier}" for tier in range(1, 5)),
    *(f"Morytania legs {tier}" for tier in range(1, 5)),
    *(f"Seers' headband {tier}" for tier in range(1, 5)),
    *(f"Varrock armour {tier}" for tier in range(1, 5)),
    *(f"Explorer's ring {tier}" for tier in range(1, 5)),
)

MILESTONE_CAPES = tuple(f"Milestone cape ({level})" for level in range(10, 100, 10))

DISTINCTION_CAPES = (
    "Max cape",
    "Completionist cape",
    "Quest point cape",
    "Veteran cape (5 year)",
    "Veteran cape (10 year)",
)


def _slug(item_name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", item_name.lower()))


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    requests: list[tuple[AssetRequest, int]] = [
        (
            AssetRequest(
                item_name="Achievement Cabinet",
                wiki_title="Achievement.png",
                output_path=ROOT / "activityicons" / "achievement_diaries.png",
                provenance_path=provenance,
            ),
            64,
        ),
    ]
    requests.extend(
        (
            AssetRequest(
                item_name=item_name,
                wiki_title=f"{item_name}.png",
                output_path=ROOT / "activityitems" / f"diary_{_slug(item_name)}.png",
                provenance_path=provenance,
            ),
            48,
        )
        for item_name in DIARY_REWARD_ITEMS
    )
    requests.extend(
        (
            AssetRequest(
                item_name=item_name,
                wiki_title=f"{item_name}.png",
                output_path=ROOT / "crafteditems" / f"{_slug(item_name)}.png",
                provenance_path=provenance,
            ),
            48,
        )
        for item_name in MILESTONE_CAPES
    )
    requests.extend(
        (
            AssetRequest(
                item_name=item_name,
                wiki_title=f"{item_name}.png",
                output_path=ROOT / "activityitems" / f"cape_{_slug(item_name)}.png",
                provenance_path=provenance,
            ),
            48,
        )
        for item_name in DISTINCTION_CAPES
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
