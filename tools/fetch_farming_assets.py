#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the data-derived Farming item and interface asset manifests."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from constants import ITEM_DEFINITIONS
from farming_data import FARMING_ASSET_MANIFEST, FARMING_INTERFACE_ASSET_MANIFEST
from item_registry import item_definitions_by_id, item_definitions_by_storage_key
from tools.fetch_assets import (
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    ImageInfo,
    OSRS_WIKI,
    RS3_WIKI,
    WikiSource,
    fetch_asset,
    wiki_title_for_item,
)

PROVENANCE = ROOT / "assets_provenance.json"
SOURCES = (RS3_WIKI, OSRS_WIKI)

TITLE_OVERRIDES = {
    "Blue blossom": "Blue vine blossom detail.png",
    "Cave nightshade": "Cave nightshade (item).png",
    "Green blossom": "Green vine blossom detail.png",
    "Jade vine branch": "Jade vine (grown).png",
    "Red blossom": "Red vine blossom detail.png",
}

PAGE_TITLE_OVERRIDES = {}


@dataclass(frozen=True)
class FarmingAssetBinding:
    asset_id: str
    item_id: Optional[str]
    item_name: str
    output_path: Path
    wiki_title: str
    provenance_path: Path
    reused: bool = False

    def request(self) -> AssetRequest:
        return AssetRequest(
            item_name=self.item_name,
            wiki_title=self.wiki_title,
            output_path=self.output_path,
            provenance_path=self.provenance_path,
        )


def item_asset_manifest() -> tuple[FarmingAssetBinding, ...]:
    by_storage_key = item_definitions_by_storage_key(ITEM_DEFINITIONS)
    by_id = item_definitions_by_id(ITEM_DEFINITIONS)
    bindings = []
    for row in FARMING_ASSET_MANIFEST:
        definition = by_storage_key.get(row.item_name)
        if definition is None or by_id.get(definition.id) is not definition:
            raise AssetFetchError(f"Farming asset {row.item_name!r} does not join a canonical item registry entry.")
        farming_path = ROOT / row.relative_path
        existing_path = Path(definition.asset_path) if definition.asset_path else None
        reuse_existing = bool(
            existing_path
            and existing_path.exists()
            and existing_path.resolve() != farming_path.resolve()
        )
        output_path = existing_path if reuse_existing else farming_path
        bindings.append(
            FarmingAssetBinding(
                asset_id=row.item_id,
                item_id=definition.id,
                item_name=row.item_name,
                output_path=output_path,
                wiki_title=wiki_title_for_item(row.item_name, TITLE_OVERRIDES.get(row.item_name)),
                provenance_path=PROVENANCE,
                reused=reuse_existing,
            )
        )
    return tuple(bindings)


def interface_asset_manifest(
    item_bindings: Optional[Sequence[FarmingAssetBinding]] = None,
) -> tuple[FarmingAssetBinding, ...]:
    item_bindings = tuple(item_bindings or item_asset_manifest())
    by_item_name = {binding.item_name: binding for binding in item_bindings}
    bindings = []
    for row in FARMING_INTERFACE_ASSET_MANIFEST:
        if row.reuse_item:
            source = by_item_name.get(row.reuse_item)
            if source is None:
                raise AssetFetchError(f"Interface asset {row.id!r} reuses unknown item {row.reuse_item!r}.")
            bindings.append(
                FarmingAssetBinding(
                    asset_id=row.id,
                    item_id=source.item_id,
                    item_name=row.display_name,
                    output_path=source.output_path,
                    wiki_title=source.wiki_title,
                    provenance_path=PROVENANCE,
                    reused=True,
                )
            )
            continue
        if not row.relative_path or not row.wiki_title:
            raise AssetFetchError(f"Interface asset {row.id!r} has no fetch path/title or reusable item.")
        bindings.append(
            FarmingAssetBinding(
                asset_id=row.id,
                item_id=None,
                item_name=row.display_name,
                output_path=ROOT / row.relative_path,
                wiki_title=wiki_title_for_item(row.display_name, row.wiki_title),
                provenance_path=PROVENANCE,
            )
        )
    return tuple(bindings)


def asset_manifest() -> tuple[FarmingAssetBinding, ...]:
    items = item_asset_manifest()
    return items + interface_asset_manifest(items)


def _page_image_title(
    client: HttpWikiClient,
    item_name: str,
    sources: Sequence[WikiSource] = SOURCES,
) -> Optional[str]:
    title = PAGE_TITLE_OVERRIDES.get(item_name, item_name)
    for source in sources:
        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
            "titles": title,
            "prop": "pageimages",
            "piprop": "name",
        }
        payload = client._request_json(f"{source.api_url}?{urllib.parse.urlencode(params)}")
        pages = payload.get("query", {}).get("pages", [])
        if isinstance(pages, list) and pages and isinstance(pages[0], dict):
            page_image = pages[0].get("pageimage")
            if isinstance(page_image, str) and page_image:
                return page_image
    return None


def _provenance_key(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def _load_provenance() -> dict[str, object]:
    if not PROVENANCE.exists():
        return {}
    with PROVENANCE.open("r", encoding="utf-8") as file_obj:
        loaded = json.load(file_obj)
    return loaded if isinstance(loaded, dict) else {}


def _write_provenance(provenance: dict[str, object]) -> None:
    with NamedTemporaryFile("w", delete=False, dir=str(ROOT), encoding="utf-8") as temp_file:
        temp_name = temp_file.name
        json.dump(provenance, temp_file, indent=2, sort_keys=True)
        temp_file.write("\n")
    os.replace(temp_name, PROVENANCE)


def _resolve_image_info(binding: FarmingAssetBinding, client: HttpWikiClient) -> ImageInfo:
    for source in SOURCES:
        info = client.query_image_info(source, binding.wiki_title)
        if info is not None:
            return info
    page_image = _page_image_title(client, binding.item_name)
    if page_image:
        for source in SOURCES:
            info = client.query_image_info(source, page_image)
            if info is not None:
                return info
    raise AssetFetchError(f"Could not resolve an exact or page-image asset for {binding.item_name}.")


def _record_reused_provenance(binding: FarmingAssetBinding, client: HttpWikiClient) -> None:
    provenance = _load_provenance()
    key = _provenance_key(binding.output_path)
    if key in provenance:
        return
    info = _resolve_image_info(binding, client)
    entry = asdict(info)
    entry["reused_from"] = key
    entry["source_note"] = "Existing canonical AnkiScape asset reused; source metadata resolved without replacing the file."
    provenance[key] = entry
    _write_provenance(provenance)


def _fetch_binding(
    binding: FarmingAssetBinding,
    client: HttpWikiClient,
    *,
    force: bool,
    dry_run: bool,
) -> str:
    provenance = _load_provenance()
    key = _provenance_key(binding.output_path)
    if binding.output_path.exists() and key in provenance and not force:
        return "existing"
    if binding.reused and binding.output_path.exists():
        if not dry_run:
            _record_reused_provenance(binding, client)
        return "reused"

    request = binding.request()
    try:
        outcome = fetch_asset(
            request,
            client,
            size=64,
            force=force,
            dry_run=dry_run,
            sources=SOURCES,
        )
    except AssetFetchError:
        page_image = _page_image_title(client, binding.item_name)
        if not page_image:
            raise
        outcome = fetch_asset(
            replace(request, wiki_title=page_image),
            client,
            size=64,
            force=force,
            dry_run=dry_run,
            sources=SOURCES,
        )
    return "existing" if outcome.skipped_existing else "fetched"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Refresh Farming-owned files; shared canonical files stay reused.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve sources without writing files or provenance.")
    args = parser.parse_args(argv)

    client = HttpWikiClient(min_interval_seconds=0.15, retries=4)
    counts = {"fetched": 0, "existing": 0, "reused": 0, "failed": 0}
    failures = []
    seen_paths = set()
    for binding in asset_manifest():
        key = _provenance_key(binding.output_path)
        if key in seen_paths:
            continue
        seen_paths.add(key)
        try:
            outcome = _fetch_binding(
                binding,
                client,
                force=bool(args.force and not binding.reused),
                dry_run=args.dry_run,
            )
            counts[outcome] += 1
            print(f"{outcome:>8} {binding.item_name} -> {binding.output_path}")
        except AssetFetchError as exc:
            counts["failed"] += 1
            failures.append(f"{binding.item_name}: {exc}")
            print(f"  failed {binding.item_name}: {exc}", file=sys.stderr)

    print(
        "Farming assets: "
        f"{counts['fetched']} fetched, {counts['reused']} reused, "
        f"{counts['existing']} existing, {counts['failed']} failed."
    )
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
