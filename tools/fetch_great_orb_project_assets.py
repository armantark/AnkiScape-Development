#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch normalized cutoff-era Great Orb Project activity and reward art."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import (  # noqa: E402
    PRE_EOC_CUTOFF,
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    RS3_WIKI,
    fetch_asset,
)

VISUAL_FALLBACK_ITEMS = frozenset(
    f"{colour.title()} runecrafter hat"
    for colour in ("green", "blue", "yellow")
)


def _mark_visual_fallback(request: AssetRequest) -> None:
    with request.provenance_path.open("r", encoding="utf-8") as file_obj:
        provenance = json.load(file_obj)
    key = str(request.output_path.relative_to(ROOT))
    entry = dict(provenance[key])
    entry["source_wiki"] = "rs3-visual-fallback"
    entry["source_note"] = (
        "The cutoff page and rev-742 cache pin this exact item, but the renamed "
        "wiki file retains no pre-cutoff revision. The current sprite is visual "
        "art only and supplies no mechanic or item identity."
    )
    provenance[key] = entry
    with NamedTemporaryFile(
        "w", delete=False, dir=str(ROOT), encoding="utf-8"
    ) as temp_file:
        temp_name = temp_file.name
        json.dump(provenance, temp_file, indent=2, sort_keys=True)
        temp_file.write("\n")
    os.replace(temp_name, request.provenance_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    client = HttpWikiClient(
        min_interval_seconds=1.1,
        before_timestamp=PRE_EOC_CUTOFF,
    )
    current_client = HttpWikiClient(min_interval_seconds=1.1)
    requests = (
        AssetRequest(
            item_name="Great Orb Project",
            wiki_title="The_Great_Orb_Project.png",
            output_path=ROOT / "activityicons" / "great_orb_project.png",
            provenance_path=ROOT / "assets_provenance.json",
        ),
        *(
            AssetRequest(
                item_name=item_name,
                wiki_title=wiki_title,
                output_path=ROOT / "activityitems" / filename,
                provenance_path=ROOT / "assets_provenance.json",
            )
            for item_name, wiki_title, filename in (
                (
                    "Master runecrafter hat",
                    "Master_runecrafter_hat.png",
                    "master_runecrafter_hat.png",
                ),
                (
                    "Master runecrafter body",
                    "Master_runecrafter_robe.png",
                    "master_runecrafter_body.png",
                ),
                (
                    "Master runecrafter skirt",
                    "Master_runecrafter_skirt.png",
                    "master_runecrafter_skirt.png",
                ),
                (
                    "Master runecrafter boots",
                    "Master_runecrafter_boots.png",
                    "master_runecrafter_boots.png",
                ),
                *(
                    (
                        f"{colour.title()} runecrafter {part}",
                        (
                            f"Runecrafter_hat_({colour},_goggles_on).png"
                            if part == "hat"
                            else f"Runecrafter_{part}_({colour}).png"
                        ),
                        f"{colour}_runecrafter_{part}.png",
                    )
                    for colour in ("green", "blue", "yellow")
                    for part in ("hat", "robe", "skirt", "gloves")
                ),
            )
        ),
        *(
            AssetRequest(
                item_name=item_name,
                wiki_title=f"{item_name.replace(' ', '_')}.png",
                output_path=(
                    ROOT
                    / "runecraftingitems"
                    / f"{item_name.lower().replace(' ', '_').replace('-', '_')}.png"
                ),
                provenance_path=ROOT / "assets_provenance.json",
            )
            for item_name in (
                "Runecrafting staff",
                "Air talisman staff",
                "Mind talisman staff",
                "Water talisman staff",
                "Earth talisman staff",
                "Fire talisman staff",
                "Body talisman staff",
                "Cosmic talisman staff",
                "Chaos talisman staff",
                "Nature talisman staff",
                "Law talisman staff",
                "Death talisman staff",
                "Blood talisman staff",
                "Omni-talisman staff",
            )
        ),
        *(
            AssetRequest(
                item_name=item_name,
                wiki_title=f"{item_name.replace(' ', '_')}.png",
                output_path=(
                    ROOT
                    / "activityitems"
                    / f"{item_name.lower().replace(' ', '_')}.png"
                ),
                provenance_path=ROOT / "assets_provenance.json",
            )
            for item_name in (
                "Runecrafting guild teleport",
                "Air altar teleport",
                "Mind altar teleport",
                "Water altar teleport",
                "Earth altar teleport",
                "Fire altar teleport",
                "Body altar teleport",
                "Cosmic altar teleport",
                "Chaos altar teleport",
                "Astral altar teleport",
                "Nature altar teleport",
                "Law altar teleport",
                "Death altar teleport",
                "Blood altar teleport",
            )
        ),
    )
    for request in requests:
        try:
            outcome = fetch_asset(
                request,
                client,
                size=64,
                force=args.force,
                dry_run=args.dry_run,
                sources=(RS3_WIKI,),
            )
        except AssetFetchError:
            if request.item_name not in VISUAL_FALLBACK_ITEMS:
                raise
            outcome = fetch_asset(
                request,
                current_client,
                size=64,
                force=args.force,
                dry_run=args.dry_run,
                sources=(RS3_WIKI,),
            )
            if not args.dry_run:
                _mark_visual_fallback(request)
        print(f"{outcome.item_name}: {outcome.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
