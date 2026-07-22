#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Shades of Mort'ton art."""

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


def _slug(item_name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", item_name.lower()))


def asset_manifest() -> tuple[tuple[AssetRequest, int], ...]:
    provenance = ROOT / "assets_provenance.json"
    item_names = (
        *(f"Olive oil ({dose})" for dose in range(1, 5)),
        *(f"Sacred oil ({dose})" for dose in range(1, 5)),
        *(f"Serum 207 ({dose})" for dose in range(1, 5)),
        *(f"Serum 208 ({dose})" for dose in range(1, 5)),
        "Loar remains",
        "Bronze key red",
        "Bronze key brown",
        "Bronze key crimson",
        "Fine cloth",
        "Pyre logs",
        "Oak pyre logs",
        "Willow pyre logs",
        "Teak pyre logs",
        "Arctic pyre logs",
        "Maple pyre logs",
        "Mahogany pyre logs",
        "Eucalyptus pyre logs",
        "Yew pyre logs",
        "Magic pyre logs",
    )
    requests = [
        (
            AssetRequest(
                item_name="Shades of Mort'ton",
                wiki_title="Sacred oil (4).png",
                output_path=ROOT / "activityicons" / "shades_of_mortton.png",
                provenance_path=provenance,
            ),
            64,
        ),
        (
            AssetRequest(
                item_name="Loar Shade",
                wiki_title="Loar Shade.png",
                output_path=ROOT / "combatenemies" / "loar_shade.png",
                provenance_path=provenance,
            ),
            48,
        ),
    ]
    requests.extend(
        (
            AssetRequest(
                item_name=item_name,
                wiki_title=f"{item_name}.png",
                output_path=(
                    ROOT
                    / "activityitems"
                    / f"shades_of_mortton_{_slug(item_name)}.png"
                ),
                provenance_path=provenance,
            ),
            48,
        )
        for item_name in item_names
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
