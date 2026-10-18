#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the normalized icon vocabulary used by global and Combat UI."""

from __future__ import annotations

import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    ImageInfo,
    OSRS_WIKI,
    RS3_WIKI,
    _extract_license_string,
    fetch_asset,
    update_provenance,
    write_png,
)


CUTOFF = "2012-11-20T23:59:59Z"

CURRENT_ASSETS = (
    ("Combat", "Combat icon.png", "icon/combat_icon.png", OSRS_WIKI),
    ("Statistics", "Stats icon.png", "icon/stats_icon.png", OSRS_WIKI),
    (
        "Quest list",
        "Quest List tab icon.png",
        "icon/quest_icon.png",
        OSRS_WIKI,
    ),
    (
        "Achievement Diaries",
        "Achievement Diaries tab icon.png",
        "icon/achievement_icon.png",
        OSRS_WIKI,
    ),
    (
        "Grand Exchange guide prices",
        "Guide prices.png",
        "icon/grand_exchange_icon.png",
        OSRS_WIKI,
    ),
    ("Bank", "Bank icon.png", "icon/bank_icon.png", OSRS_WIKI),
    (
        "Worn Equipment",
        "Worn Equipment.png",
        "icon/equipment_icon.png",
        OSRS_WIKI,
    ),
    (
        "Distractions and Diversions",
        "Distraction & Diversion icon.png",
        "icon/dnd_icon.png",
        OSRS_WIKI,
    ),
    (
        "Minigames",
        "Minigame icon.png",
        "icon/minigame_icon.png",
        OSRS_WIKI,
    ),
)

PERIOD_INTERFACE_ASSETS = (
    (
        "Activities",
        "Activity icon.png",
        "icon/activities_icon.png",
    ),
    (
        "Skills",
        "Max cape.png",
        "icon/skills_icon.png",
    ),
    (
        "Shop",
        "Coins.png",
        "icon/shop_icon.png",
    ),
)

PERIOD_SKILL_ASSETS = (
    ("Attack", "attack"),
    ("Constitution", "constitution"),
    ("Mining", "mining"),
    ("Strength", "strength"),
    ("Agility", "agility"),
    ("Smithing", "smithing"),
    ("Defence", "defense"),
    ("Herblore", "herblore"),
    ("Fishing", "fishing"),
    ("Ranged", "ranged"),
    ("Thieving", "thieving"),
    ("Cooking", "cooking"),
    ("Prayer", "prayer"),
    ("Crafting", "crafting"),
    ("Firemaking", "firemaking"),
    ("Magic", "magic"),
    ("Fletching", "fletching"),
    ("Woodcutting", "woodcutting"),
    ("Runecrafting", "runecrafting"),
    ("Slayer", "slayer"),
    ("Farming", "farming"),
    ("Construction", "construction"),
    ("Hunter", "hunter"),
    ("Summoning", "summoning"),
    ("Dungeoneering", "dungeoneering"),
)

PERIOD_ASSETS = PERIOD_INTERFACE_ASSETS + tuple(
    (
        display_name,
        f"{display_name} icon highscores.png",
        f"icon/{file_stem}_icon.png",
    )
    for display_name, file_stem in PERIOD_SKILL_ASSETS
)


def _request(
    item_name: str, wiki_title: str, relative_path: str
) -> AssetRequest:
    return AssetRequest(
        item_name=item_name,
        wiki_title=wiki_title,
        output_path=ROOT / relative_path,
        provenance_path=ROOT / "assets_provenance.json",
    )


def period_image_info(
    client: HttpWikiClient, file_title: str
) -> ImageInfo:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
        "prop": "imageinfo",
        "iiprop": (
            "url|sha1|size|mime|timestamp|mediatype|extmetadata"
        ),
        "iistart": CUTOFF,
        "iilimit": "1",
        "titles": f"File:{file_title}",
    }
    url = f"{RS3_WIKI.api_url}?{urllib.parse.urlencode(params)}"
    payload = client._request_json(url)
    pages = payload.get("query", {}).get("pages", [])
    if not isinstance(pages, list) or not pages or "missing" in pages[0]:
        raise AssetFetchError(f"No RuneScape Wiki file matched {file_title}")
    page = pages[0]
    rows = page.get("imageinfo", [])
    if not isinstance(rows, list) or not rows:
        raise AssetFetchError(
            f"No revision at or before {CUTOFF} for {file_title}"
        )
    row = rows[0]
    timestamp = str(row.get("timestamp") or "")
    if not timestamp or timestamp > CUTOFF:
        raise AssetFetchError(f"No revision at or before {CUTOFF} for {file_title}")
    title = str(page.get("title") or f"File:{file_title}")
    return ImageInfo(
        source_wiki="rs3-period",
        file_title=title.removeprefix("File:"),
        file_page_url=str(row.get("descriptionurl") or ""),
        image_url=str(row["url"]),
        sha1=str(row.get("sha1") or ""),
        size=int(row.get("size") or 0),
        mime=str(row.get("mime") or ""),
        timestamp=timestamp,
        mediatype=str(row.get("mediatype") or ""),
        license_string=_extract_license_string(row.get("extmetadata")),
    )


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=1.1)
    failures: list[str] = []
    for item_name, wiki_title, relative_path, source in CURRENT_ASSETS:
        request = _request(item_name, wiki_title, relative_path)
        try:
            fetch_asset(
                request=request,
                client=client,
                size=64,
                force=True,
                dry_run=False,
                sources=(source,),
            )
            print(f"{item_name} -> {relative_path}")
        except AssetFetchError as exc:
            failures.append(f"{item_name}: {exc}")
    for item_name, wiki_title, relative_path in PERIOD_ASSETS:
        request = _request(item_name, wiki_title, relative_path)
        try:
            info = period_image_info(client, wiki_title)
            write_png(
                client.download_bytes(info.image_url),
                request.output_path,
                64,
            )
            update_provenance(
                request.provenance_path,
                request.output_path,
                info,
            )
            print(f"{item_name}: {info.timestamp} -> {relative_path}")
        except AssetFetchError as exc:
            failures.append(f"{item_name}: {exc}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
