#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the Construction build/material/output manifest from construction_data.py."""

from __future__ import annotations

import json
import os
import shutil
import sys
import urllib.parse
from dataclasses import replace
from pathlib import Path
from tempfile import NamedTemporaryFile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.construction_data import ALL_CONSTRUCTION_TARGETS, construction_asset_items_as_dict
from tools.fetch_assets import AssetFetchError, AssetRequest, HttpWikiClient, OSRS_WIKI, RS3_WIKI, fetch_asset, wiki_title_for_item


def _slug(name: str) -> str:
    return "_".join(part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in name).split())


TITLE_OVERRIDES = {
    "Guilded altar": "Gilded altar.png", "Basalisk head": "Basilisk head.png",
    "Abbysal demon": "Abyssal demon head.png", "Inscence burner": "Incense burner.png",
    "Oak lecturn": "Oak lectern.png", "Eagle lecturn": "Eagle lectern.png",
    "Demon lecturn": "Demon lectern.png", "Teak eagle lecturn": "Teak eagle lectern.png",
    "Teak demon lecturn": "Teak demon lectern.png", "Mahogany eagle lecturn": "Mahogany eagle lectern.png",
    "Mahogany demon lecturn": "Mahogany demon lectern.png", "Nails": "Steel nails.png",
}

PAGE_TITLE_OVERRIDES = {
    "Fern": "Fern (small plant)",
}


def _page_image_title(client: HttpWikiClient, item_name: str) -> str | None:
    title = PAGE_TITLE_OVERRIDES.get(item_name, item_name)
    for source in (RS3_WIKI, OSRS_WIKI):
        params = {
            "action": "query", "format": "json", "formatversion": "2",
            "redirects": "1", "titles": title, "prop": "pageimages",
            "piprop": "name",
        }
        payload = client._request_json(f"{source.api_url}?{urllib.parse.urlencode(params)}")
        pages = payload.get("query", {}).get("pages", [])
        if isinstance(pages, list) and pages and isinstance(pages[0], dict):
            pageimage = pages[0].get("pageimage")
            if isinstance(pageimage, str) and pageimage:
                return pageimage
    return None


def _fallback_assets() -> dict[str, str]:
    fallbacks: dict[str, str] = {}
    for row in ALL_CONSTRUCTION_TARGETS:
        name = str(row.get("asset_name", ""))
        requirements = row.get("requirements", {}) or {}
        fallback = next((str(item) for item in requirements if item != "Nails"), "")
        if name and fallback:
            fallbacks.setdefault(name, fallback)
        output_item = row.get("output_item")
        if isinstance(output_item, str) and output_item and fallback:
            fallbacks.setdefault(output_item, fallback)
    return fallbacks


def _copy_with_provenance(request: AssetRequest, source_path: Path) -> None:
    request.output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, request.output_path)
    with request.provenance_path.open("r", encoding="utf-8") as file_obj:
        provenance = json.load(file_obj)
    source_key = str(source_path.relative_to(ROOT))
    output_key = str(request.output_path.relative_to(ROOT))
    entry = dict(provenance.get(source_key, {}))
    entry["reused_from"] = source_key
    entry["source_note"] = "Construction object has no standalone wiki item sprite; authentic build-material sprite reused."
    provenance[output_key] = entry
    with NamedTemporaryFile("w", delete=False, dir=str(ROOT), encoding="utf-8") as temp_file:
        temp_name = temp_file.name
        json.dump(provenance, temp_file, indent=2, sort_keys=True)
        temp_file.write("\n")
    os.replace(temp_name, request.provenance_path)


def asset_manifest():
    return tuple(
        AssetRequest(
            item_name=name,
            wiki_title=wiki_title_for_item(name, TITLE_OVERRIDES.get(name)),
            output_path=ROOT / "constructionitems" / f"{_slug(name)}.png",
            provenance_path=ROOT / "assets_provenance.json",
        )
        for name in construction_asset_items_as_dict()
    )


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=0.15, retries=4)
    unresolved = []
    for request in asset_manifest():
        if request.output_path.exists():
            print(f"{request.item_name}: existing -> {request.output_path}")
            continue
        try:
            outcome = fetch_asset(request, client, size=64, sources=(RS3_WIKI, OSRS_WIKI))
            print(f"{outcome.item_name}: {outcome.source_wiki} -> {outcome.output_path}")
        except AssetFetchError:
            page_image = _page_image_title(client, request.item_name)
            if page_image:
                try:
                    outcome = fetch_asset(replace(request, wiki_title=page_image), client, size=64, sources=(RS3_WIKI, OSRS_WIKI))
                    print(f"{outcome.item_name}: {outcome.source_wiki} page image -> {outcome.output_path}")
                    continue
                except AssetFetchError:
                    pass
            unresolved.append(request)
    fallbacks = _fallback_assets()
    failures = []
    for request in unresolved:
        fallback_name = fallbacks.get(request.item_name)
        fallback_path = ROOT / "constructionitems" / f"{_slug(fallback_name)}.png" if fallback_name else None
        if fallback_path is not None and fallback_path.exists():
            _copy_with_provenance(request, fallback_path)
            print(f"{request.item_name}: reused {fallback_name} -> {request.output_path}")
        else:
            failures.append(f"{request.item_name}: no exact, page-image, or material asset resolved")
    if failures:
        print("Unresolved Construction assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
