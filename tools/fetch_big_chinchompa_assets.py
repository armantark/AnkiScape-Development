#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch period Big Chinchompa inventory art and a normalized activity icon."""

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
    RS3_WIKI,
    _extract_license_string,
    update_provenance,
    write_png,
)


CUTOFF = "2012-11-20T00:00:00Z"


def asset_manifest() -> tuple[AssetRequest, ...]:
    rows = (
        ("Big Chinchompa activity", "Moth jar.png", "activityicons/big_chinchompa.png"),
        ("Moth jar", "Moth jar.png", "hunteritems/moth_jar.png"),
        ("Protea flower", "Protea flower.png", "hunteritems/protea_flower.png"),
        (
            "Swamp lizard quota ticket",
            "Green salamander quota ticket.png",
            "hunteritems/swamp_lizard_quota_ticket.png",
        ),
        (
            "Carnivorous chinchompa quota ticket",
            "Carnivorous chinchompa quota ticket.png",
            "hunteritems/carnivorous_chinchompa_quota_ticket.png",
        ),
        (
            "Pawya quota ticket",
            "Pawya quota ticket.png",
            "hunteritems/pawya_quota_ticket.png",
        ),
        (
            "Polar kebbit quota ticket",
            "Polar kebbit quota ticket.png",
            "hunteritems/polar_kebbit_quota_ticket.png",
        ),
        (
            "Grenwall quota ticket",
            "Grenwall quota ticket.png",
            "hunteritems/grenwall_quota_ticket.png",
        ),
    )
    return tuple(
        AssetRequest(
            item_name=item_name,
            wiki_title=wiki_title,
            output_path=ROOT / relative_path,
            provenance_path=ROOT / "assets_provenance.json",
        )
        for item_name, wiki_title, relative_path in rows
    )


def _period_image_info(client: HttpWikiClient, file_title: str) -> ImageInfo:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
        "prop": "imageinfo",
        "iiprop": "url|sha1|size|mime|timestamp|mediatype|extmetadata",
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
    for request in asset_manifest():
        if request.output_path.exists():
            continue
        try:
            info = _period_image_info(client, request.wiki_title)
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
            print(
                f"{request.item_name}: {info.timestamp} -> "
                f"{request.output_path.relative_to(ROOT)}"
            )
        except AssetFetchError as exc:
            failures.append(f"{request.item_name}: {exc}")
    if failures:
        print("Unresolved Big Chinchompa assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
