#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the Magic target/material/output manifest derived from magic_data.py."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from magic_data import magic_extra_items_as_dict
from tools.fetch_assets import (
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    OSRS_WIKI,
    RS3_WIKI,
    fetch_asset,
    wiki_title_for_item,
)

WIKI_TITLES = {"Castle wars bracelet (3)": "Castle wars brace.png"}


def _slug(name: str) -> str:
    return "_".join(part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in name).split())


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=1.1)
    failures = []
    requests = [
        AssetRequest(
            item_name=name,
            wiki_title=wiki_title_for_item(name, WIKI_TITLES.get(name)),
            output_path=ROOT / "magicitems" / f"{_slug(name)}.png",
            provenance_path=ROOT / "assets_provenance.json",
        )
        for name in magic_extra_items_as_dict()
    ]
    for request in requests:
        try:
            outcome = fetch_asset(request, client, size=64, sources=(RS3_WIKI, OSRS_WIKI))
            print(f"{outcome.item_name}: {outcome.source_wiki} -> {outcome.output_path}")
        except AssetFetchError as exc:
            failures.append(f"{request.item_name}: {exc}")
    if failures:
        print("Unresolved Magic assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
