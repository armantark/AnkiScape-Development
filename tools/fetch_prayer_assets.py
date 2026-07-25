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

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.prayer_data import prayer_extra_items_as_dict
from ankiscape.data.prayer_passive_data import prayer_passive_items_as_dict
from tools.fetch_assets import AssetFetchError, AssetRequest, HttpWikiClient, RS3_WIKI, fetch_asset


def _slug(name: str) -> str:
    return "_".join(part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in name).split())


def asset_manifest() -> tuple[AssetRequest, ...]:
    item_names = tuple(dict.fromkeys((*prayer_extra_items_as_dict(), *prayer_passive_items_as_dict())))
    requests = tuple(
        AssetRequest(
            item_name=name,
            wiki_title=f"{name}.png",
            output_path=ROOT / "prayeritems" / f"{_slug(name)}.png",
            provenance_path=ROOT / "assets_provenance.json",
        )
        for name in item_names
    )
    return requests


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=1.1)
    failures = []
    # Existing checked-in art is immutable for this closure. Skipping before the
    # resolver also means the network run touches only newly added manifest rows.
    requests = tuple(request for request in asset_manifest() if not request.output_path.exists())
    for request in requests:
        try:
            outcome = fetch_asset(request, client, size=64, sources=(RS3_WIKI,))
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
