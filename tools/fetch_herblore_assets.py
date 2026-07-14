#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the overworld Herblore row art and skill icon from RuneScape Wiki."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from herblore_data import CLEAN_TARGETS
from tools.fetch_assets import AssetFetchError, AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset


def _slug(name: str) -> str:
    return "_".join(part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in name).split())


def asset_manifest() -> tuple[AssetRequest, ...]:
    clean_herbs = tuple(
        AssetRequest(
            item_name=target.output_item,
            wiki_title=f"{target.output_item}.png",
            output_path=ROOT / "herbloreitems" / f"{_slug(target.output_item)}.png",
            provenance_path=ROOT / "assets_provenance.json",
        )
        for target in CLEAN_TARGETS
    )
    return (
        AssetRequest(
            item_name="Herblore skill icon",
            wiki_title="Herblore detail.png",
            output_path=ROOT / "icon" / "herblore_icon.png",
            provenance_path=ROOT / "assets_provenance.json",
        ),
        *clean_herbs,
    )


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=1.1)
    failures = []
    for request in asset_manifest():
        try:
            outcome = fetch_asset(request, client, size=64, sources=(RS3_WIKI,))
            print(f"{outcome.item_name}: {outcome.source_wiki} -> {outcome.output_path}")
        except AssetFetchError as exc:
            failures.append(f"{request.item_name}: {exc}")
    if failures:
        print("Unresolved Herblore assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
