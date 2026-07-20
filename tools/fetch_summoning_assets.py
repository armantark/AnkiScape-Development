#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the complete surface Summoning item manifest and skill icon."""

from __future__ import annotations

import sys
import urllib.parse
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from summoning_data import summoning_extra_items_as_dict
from tools.fetch_assets import (
    OSRS_WIKI,
    RS3_WIKI,
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
    wiki_title_for_item,
)

PRE_EOC_CUTOFF = "2012-11-20T00:00:00Z"


def _slug(name: str) -> str:
    return "_".join(
        "".join(ch.lower() if ch.isalnum() else " " for ch in name).split()
    )


TITLE_OVERRIDES = {
    "Ghast pouch": "Ghastly familiar pouch.png",
}


def _page_image_title(
    client: HttpWikiClient, item_name: str
) -> str | None:
    for source in (RS3_WIKI, OSRS_WIKI):
        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
            "titles": item_name,
            "prop": "pageimages",
            "piprop": "name",
        }
        payload = client._request_json(
            f"{source.api_url}?{urllib.parse.urlencode(params)}"
        )
        pages = payload.get("query", {}).get("pages", [])
        if (
            isinstance(pages, list)
            and pages
            and isinstance(pages[0], dict)
        ):
            pageimage = pages[0].get("pageimage")
            if isinstance(pageimage, str) and pageimage:
                return pageimage
    return None


def asset_manifest() -> tuple[AssetRequest, ...]:
    items = tuple(
        AssetRequest(
            item_name=item_name,
            wiki_title=wiki_title_for_item(
                item_name, TITLE_OVERRIDES.get(item_name)
            ),
            output_path=ROOT / "summoningitems" / f"{_slug(item_name)}.png",
            provenance_path=ROOT / "assets_provenance.json",
        )
        for item_name in summoning_extra_items_as_dict()
    )
    return (
        AssetRequest(
            item_name="Summoning skill icon",
            wiki_title="Summoning-icon.png",
            output_path=ROOT / "icon" / "summoning_icon.png",
            provenance_path=ROOT / "assets_provenance.json",
        ),
        *items,
    )


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=0.15, retries=4)
    period_client = HttpWikiClient(
        min_interval_seconds=0.15,
        retries=4,
        before_timestamp=PRE_EOC_CUTOFF,
    )
    unresolved: list[AssetRequest] = []
    for request in asset_manifest():
        if request.output_path.exists():
            print(f"{request.item_name}: existing -> {request.output_path}")
            continue
        try:
            request_client = (
                period_client if request.item_name == "Swamp toad" else client
            )
            outcome = fetch_asset(
                request,
                request_client,
                size=64,
                sources=(RS3_WIKI, OSRS_WIKI),
            )
            print(
                f"{outcome.item_name}: {outcome.source_wiki} "
                f"-> {outcome.output_path}"
            )
        except AssetFetchError:
            unresolved.append(request)

    failures = []
    for request in unresolved:
        page_image = _page_image_title(client, request.item_name)
        if page_image:
            try:
                outcome = fetch_asset(
                    replace(request, wiki_title=page_image),
                    client,
                    size=64,
                    sources=(RS3_WIKI, OSRS_WIKI),
                )
                print(
                    f"{outcome.item_name}: {outcome.source_wiki} page image "
                    f"-> {outcome.output_path}"
                )
                continue
            except AssetFetchError:
                pass
        failures.append(request.item_name)

    if failures:
        print("Unresolved Summoning assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
