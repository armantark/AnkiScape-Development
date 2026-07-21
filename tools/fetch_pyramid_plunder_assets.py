#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Pyramid Plunder activity and reward art."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pyramid_plunder_data import pyramid_plunder_extra_items_as_dict  # noqa: E402
from tools.fetch_assets import AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset  # noqa: E402

PRE_EOC_CUTOFF = "2012-11-20T23:59:59Z"


def _slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    requests = [
        (
            AssetRequest(
                item_name="Pyramid Plunder",
                wiki_title="Pharaoh's sceptre.png",
                output_path=ROOT / "activityicons" / "pyramid_plunder.png",
                provenance_path=provenance,
            ),
            64,
        )
    ]
    wiki_title_overrides = {
        "Pharaoh's sceptre (3)": "Pharaoh's sceptre.png",
        "Pharaoh's sceptre (2)": "Pharaoh's sceptre.png",
        "Pharaoh's sceptre (1)": "Pharaoh's sceptre.png",
        "Pharaoh's sceptre": "Pharaoh's sceptre.png",
    }
    for item_name in pyramid_plunder_extra_items_as_dict():
        wiki_title = wiki_title_overrides.get(item_name, f"{item_name}.png")
        requests.append(
            (
                AssetRequest(
                    item_name=item_name,
                    wiki_title=wiki_title,
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
