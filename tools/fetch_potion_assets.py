#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch every registered vial-potion and potion-flask asset."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.potion_data import EMPTY_FLASK_ITEM, POTION_FAMILIES, potion_dose_name, potion_flask_name
from tools.fetch_assets import RS3_WIKI, AssetFetchError, AssetRequest, HttpWikiClient, fetch_asset


def _slug(name: str) -> str:
    return "_".join(
        part
        for part in "".join(
            ch.lower() if ch.isalnum() else " " for ch in name
        ).split()
    )


def asset_manifest() -> tuple[AssetRequest, ...]:
    item_names = [EMPTY_FLASK_ITEM[0]]
    for base, spec in POTION_FAMILIES.items():
        item_names.extend(
            potion_dose_name(base, dose)
            for dose in sorted(spec["doses"])  # type: ignore[arg-type]
        )
        item_names.extend(
            potion_flask_name(base, dose)
            for dose in sorted(spec["flask_doses"])  # type: ignore[arg-type]
        )
    return tuple(
        AssetRequest(
            item_name=item_name,
            wiki_title=f"{item_name}.png",
            output_path=ROOT / "herbloreitems" / f"{_slug(item_name)}.png",
            provenance_path=ROOT / "assets_provenance.json",
        )
        for item_name in item_names
    )


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=1.1)
    failures = []
    for request in asset_manifest():
        try:
            outcome = fetch_asset(
                request,
                client,
                size=64,
                sources=(RS3_WIKI,),
            )
            print(
                f"{outcome.item_name}: "
                f"{outcome.source_wiki} -> {outcome.output_path}"
            )
        except AssetFetchError as exc:
            failures.append(f"{request.item_name}: {exc}")
    if failures:
        print("Unresolved potion assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
