#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch every live overworld Herblore row asset and the skill-rail icon."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.herblore_data import CLEAN_TARGETS, FINISHED_TARGETS, UNF_TARGETS
from tools.fetch_assets import (
    RS3_WIKI,
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
)

PRE_EOC_CUTOFF = "2012-11-20T00:00:00Z"


def _slug(name: str) -> str:
    return "_".join(part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in name).split())


def _wiki_title(output_item: str) -> str:
    if output_item.endswith(" potion (unf)"):
        return f"{output_item.removesuffix(' potion (unf)')} potion (unfinished).png"
    if output_item == "Anti-p supermix (2)":
        return "Super antipoison mix (2).png"
    return f"{output_item}.png"


def asset_manifest() -> tuple[AssetRequest, ...]:
    live_outputs = tuple(
        AssetRequest(
            item_name=target.output_item,
            wiki_title=_wiki_title(target.output_item),
            output_path=ROOT / "herbloreitems" / f"{_slug(target.output_item)}.png",
            provenance_path=ROOT / "assets_provenance.json",
        )
        for target in CLEAN_TARGETS + UNF_TARGETS + FINISHED_TARGETS
    )
    return (
        AssetRequest(
            item_name="Shrunk ogleroot",
            wiki_title="Shrunk ogleroot.png",
            output_path=ROOT / "herbloreitems" / "shrunk_ogleroot.png",
            provenance_path=ROOT / "assets_provenance.json",
        ),
        AssetRequest(
            item_name="Toad's legs",
            wiki_title="Toad's legs.png",
            output_path=ROOT / "herbloreitems" / "toad_s_legs.png",
            provenance_path=ROOT / "assets_provenance.json",
        ),
        *live_outputs,
    )


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=1.1)
    period_client = HttpWikiClient(
        min_interval_seconds=1.1,
        before_timestamp=PRE_EOC_CUTOFF,
    )
    failures = []
    for request in asset_manifest():
        try:
            request_client = (
                period_client if request.item_name == "Toad's legs" else client
            )
            outcome = fetch_asset(
                request,
                request_client,
                size=64,
                sources=(RS3_WIKI,),
            )
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
