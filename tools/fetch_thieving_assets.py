#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the small source-visible Thieving asset manifest."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import AssetFetchError, AssetRequest, HttpWikiClient, OSRS_WIKI, RS3_WIKI, fetch_asset


def asset_manifest() -> tuple[AssetRequest, ...]:
    provenance = ROOT / "assets_provenance.json"
    return (
        AssetRequest(
            item_name="Thieving skill icon",
            wiki_title="Thieving-icon.png",
            output_path=ROOT / "icon" / "thieving_icon.png",
            provenance_path=provenance,
        ),
        AssetRequest(
            item_name="Desert Phoenix",
            wiki_title="Desert Phoenix.png",
            output_path=ROOT / "activityicons" / "desert_phoenix.png",
            provenance_path=provenance,
        ),
    )


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=1.1)
    failures: list[str] = []
    for request in asset_manifest():
        if request.output_path.exists():
            continue
        try:
            outcome = fetch_asset(request, client, size=64, sources=(RS3_WIKI, OSRS_WIKI))
            print(f"{outcome.item_name}: {outcome.source_wiki} -> {outcome.output_path}")
        except AssetFetchError as exc:
            failures.append(f"{request.item_name}: {exc}")
    if failures:
        print("Unresolved Thieving assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
