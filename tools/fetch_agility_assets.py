#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the frozen pre-EOC Agility asset manifest from period file revisions."""

from __future__ import annotations

import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import (
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    ImageInfo,
    RS3_WIKI,
    _extract_license_string,
    update_provenance,
    write_png,
)


CUTOFF = "2012-11-20T00:00:00Z"


def _request(item_name: str, wiki_title: str, relative_path: str) -> AssetRequest:
    return AssetRequest(
        item_name=item_name,
        wiki_title=wiki_title,
        output_path=ROOT / relative_path,
        provenance_path=ROOT / "assets_provenance.json",
    )


def asset_manifest() -> tuple[AssetRequest, ...]:
    rows = (
        ("Agility skill icon", "Agility-icon.png", "icon/agility_icon.png"),
        ("Agility arena ticket", "Agility Arena ticket.png", "agilityitems/agility_arena_ticket.png"),
        ("Pyramid top", "Pyramid top.png", "agilityitems/pyramid_top.png"),
        ("Agile top", "Agile top.png", "agilityitems/agile_top.png"),
        ("Agile legs", "Agile legs.png", "agilityitems/agile_legs.png"),
        ("Gnomeball", "Gnomeball.png", "agilityitems/gnomeball.png"),
        ("Gorilla mask", "Gorilla mask.png", "agilityitems/gorilla_mask.png"),
        ("Factory mask", "Factory mask.png", "agilityitems/factory_mask.png"),
        ("Factory top", "Factory top.png", "agilityitems/factory_top.png"),
        ("Factory trousers", "Factory trousers.png", "agilityitems/factory_trousers.png"),
        ("Factory gloves", "Factory gloves.png", "agilityitems/factory_gloves.png"),
        ("Factory boots", "Factory boots.png", "agilityitems/factory_boots.png"),
        ("Rogue mask", "Rogue mask.png", "agilityitems/rogue_mask.png"),
        ("Rogue top", "Rogue top.png", "agilityitems/rogue_top.png"),
        ("Rogue trousers", "Rogue trousers.png", "agilityitems/rogue_trousers.png"),
        ("Rogue gloves", "Rogue gloves.png", "agilityitems/rogue_gloves.png"),
        ("Rogue boots", "Rogue boots.png", "agilityitems/rogue_boots.png"),
        ("Pirate's hook", "Pirate hook (left).png", "agilityitems/pirates_hook.png"),
        ("Werewolf stick", "Stick.png", "agilityitems/werewolf_stick.png"),
        ("Generator part", "Power box.png", "agilityitems/generator_part.png"),
        ("Acrobat hood", "Acrobat hood (male).png", "agilityitems/acrobat_hood.png"),
        ("Acrobat shirt", "Acrobat shirt (male).png", "agilityitems/acrobat_shirt.png"),
        ("Acrobat pants", "Acrobat pants (male).png", "agilityitems/acrobat_pants.png"),
        ("Acrobat shoes", "Acrobat shoes (male).png", "agilityitems/acrobat_shoes.png"),
        ("Toy mouse", "Toy mouse.png", "agilityitems/toy_mouse.png"),
        ("Boots of lightness", "Boots of lightness.png", "agilityitems/boots_of_lightness.png"),
        ("Spotted cape", "Spotted cape.png", "agilityitems/spotted_cape.png"),
        ("Spottier cape", "Spottier cape.png", "agilityitems/spottier_cape.png"),
        ("Karamja gloves 4", "Karamja gloves 4.png", "agilityitems/karamja_gloves_4.png"),
        ("Penance horn", "Penance horn.png", "agilityitems/penance_horn.png"),
        ("Penance master horn", "Penance master horn.png", "agilityitems/penance_master_horn.png"),
        ("Brawling gloves (Agility)", "Brawling gloves (Agility).png", "agilityitems/brawling_gloves_agility.png"),
        ("Sköll boots", "Sköll boots.png", "agilityitems/skoll_boots.png"),
        ("Pendant of Agility", "Pendant of Agility.png", "agilityitems/pendant_of_agility.png"),
        ("Prized pendant of Agility", "Prized pendant of Agility.png", "agilityitems/prized_pendant_of_agility.png"),
        ("Surefooted aura", "Surefooted aura.png", "agilityitems/surefooted_aura.png"),
        ("Greater surefooted aura", "Greater surefooted aura.png", "agilityitems/greater_surefooted_aura.png"),
        ("Agility cape", "Agility cape.png", "agilityitems/agility_cape.png"),
        ("Agility hood", "Agility hood.png", "agilityitems/agility_hood.png"),
        ("Agility potion (4)", "Agility potion (4).png", "agilityitems/agility_potion_4.png"),
        ("Agility mix (2)", "Agility mix (2).png", "agilityitems/agility_mix_2.png"),
        ("Summer pie", "Summer pie.png", "agilityitems/summer_pie.png"),
        ("Mith grapple", "Mith grapple.png", "agilityitems/mith_grapple.png"),
    )
    return tuple(_request(*row) for row in rows)


def _period_image_info(client: HttpWikiClient, file_title: str) -> ImageInfo:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
        "prop": "imageinfo",
        "iiprop": "url|sha1|size|mime|timestamp|mediatype|extmetadata",
        "iistart": CUTOFF,
        "iidir": "older",
        "iilimit": "1",
        "titles": f"File:{file_title}",
    }
    payload = client._request_json(f"{RS3_WIKI.api_url}?{urllib.parse.urlencode(params)}")
    pages = payload.get("query", {}).get("pages", [])
    if not isinstance(pages, list) or not pages or "missing" in pages[0]:
        raise AssetFetchError(f"No RuneScape Wiki file matched {file_title}")
    page = pages[0]
    rows = page.get("imageinfo", [])
    if not isinstance(rows, list) or not rows:
        raise AssetFetchError(f"No revision at or before {CUTOFF} for {file_title}")
    row = rows[0]
    title = str(page.get("title") or f"File:{file_title}")
    return ImageInfo(
        source_wiki="rs3-period",
        file_title=title.removeprefix("File:"),
        file_page_url=str(row.get("descriptionurl") or f"{RS3_WIKI.page_base_url}/wiki/{urllib.parse.quote(title.replace(' ', '_'), safe=':/')}"),
        image_url=str(row["url"]),
        sha1=str(row.get("sha1") or ""),
        size=int(row.get("size") or 0),
        mime=str(row.get("mime") or ""),
        timestamp=str(row.get("timestamp") or ""),
        mediatype=str(row.get("mediatype") or ""),
        license_string=_extract_license_string(row.get("extmetadata")),
    )


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=1.1)
    failures = []
    for request in asset_manifest():
        if request.output_path.exists():
            continue
        try:
            info = _period_image_info(client, request.wiki_title)
            write_png(client.download_bytes(info.image_url), request.output_path, 64)
            update_provenance(request.provenance_path, request.output_path, info)
            print(f"{request.item_name}: {info.timestamp} -> {request.output_path}")
        except AssetFetchError as exc:
            failures.append(f"{request.item_name}: {exc}")
    if failures:
        print("Unresolved Agility assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
