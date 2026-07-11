#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the Prayer manifest derived from prayer_data.py."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prayer_data import prayer_extra_items_as_dict
from tools.fetch_assets import AssetFetchError, AssetRequest, HttpWikiClient, fetch_asset


def _slug(name: str) -> str:
    return "_".join(part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in name).split())


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=1.1)
    failures = []
    requests = [
        AssetRequest(
            item_name=name,
            wiki_title=f"{name}.png",
            output_path=ROOT / "prayeritems" / f"{_slug(name)}.png",
            provenance_path=ROOT / "assets_provenance.json",
        )
        for name in prayer_extra_items_as_dict()
    ]
    requests.append(AssetRequest(
        item_name="Prayer skill icon",
        wiki_title="Prayer icon (detail).png",
        output_path=ROOT / "icon" / "prayer_icon.png",
        provenance_path=ROOT / "assets_provenance.json",
    ))
    for request in requests:
        try:
            outcome = fetch_asset(request, client, size=64)
            print(f"{outcome.item_name}: {outcome.source_wiki} -> {outcome.output_path}")
        except AssetFetchError as exc:
            failures.append(f"{request.item_name}: {exc}")
    if failures:
        print("Unresolved Prayer assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
