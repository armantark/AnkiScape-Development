#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch every freeze-date pet stage image into the canonical asset tree."""

from __future__ import annotations

import sys
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.pet_data import pet_asset_manifest
from tools.fetch_assets import (
    OSRS_WIKI,
    RS3_WIKI,
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    fetch_asset,
)


def asset_manifest() -> tuple[AssetRequest, ...]:
    return tuple(
        AssetRequest(
            item_name=label,
            wiki_title=wiki_title,
            output_path=ROOT / relative_path,
            provenance_path=ROOT / "assets_provenance.json",
        )
        for label, wiki_title, relative_path in pet_asset_manifest()
    )


def _search_image_title(
    client: HttpWikiClient, request: AssetRequest
) -> str | None:
    stem = Path(request.wiki_title.replace("\u200e", "")).stem
    words = re.findall(r"[A-Za-z0-9]+", stem)
    useful = [
        word
        for word in words
        if word.casefold() not in {"inv", "icon", "sw"}
    ]
    pet_name = request.item_name.rsplit(" stage ", 1)[0]
    queries = tuple(
        dict.fromkeys(
            query
            for query in (" ".join(useful), pet_name)
            if query.strip()
        )
    )
    candidates: list[str] = []
    for query in queries:
        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "list": "search",
            "srnamespace": "6",
            "srsearch": query,
            "srlimit": "20",
        }
        payload = client._request_json(
            f"{RS3_WIKI.api_url}?{urllib.parse.urlencode(params)}"
        )
        for row in payload.get("query", {}).get("search", []):
            if isinstance(row, dict):
                title = str(row.get("title", "")).removeprefix("File:")
                if title.casefold().endswith((".png", ".gif")):
                    candidates.append(title)
        if candidates:
            break
    if not candidates:
        return None
    wanted = {word.casefold() for word in useful}

    def score(title: str) -> tuple[int, int]:
        folded = title.casefold()
        overlap = sum(word in folded for word in wanted)
        penalties = sum(
            marker in folded
            for marker in ("chathead", "concept", "detail", "interface")
        )
        preferred = 2 if " pet." in folded else 1 if folded.endswith(".png") else 0
        return overlap * 10 + preferred - penalties * 20, -len(title)

    return max(candidates, key=score)


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=0.15, retries=4)
    failures: list[str] = []
    for request in asset_manifest():
        if request.output_path.exists():
            print(f"{request.item_name}: existing -> {request.output_path}")
            continue
        try:
            outcome = fetch_asset(
                request,
                client,
                size=64,
                sources=(RS3_WIKI, OSRS_WIKI),
            )
            print(
                f"{outcome.item_name}: {outcome.source_wiki} "
                f"-> {outcome.output_path}"
            )
        except AssetFetchError:
            fallback_title = _search_image_title(client, request)
            if fallback_title:
                try:
                    outcome = fetch_asset(
                        AssetRequest(
                            item_name=request.item_name,
                            wiki_title=fallback_title,
                            output_path=request.output_path,
                            provenance_path=request.provenance_path,
                        ),
                        client,
                        size=64,
                        sources=(RS3_WIKI,),
                    )
                    print(
                        f"{outcome.item_name}: {outcome.source_wiki} search "
                        f"-> {outcome.output_path}"
                    )
                    continue
                except AssetFetchError:
                    pass
            failures.append(request.item_name)
    if failures:
        print("Unresolved pet assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
