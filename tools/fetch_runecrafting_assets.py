#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch Runecrafting item and skill icons for AnkiScape."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.fetch_assets import AssetRequest, HttpWikiClient, fetch_asset, wiki_title_for_item  # noqa: E402


@dataclass(frozen=True)
class AssetSpec:
    item_name: str
    output_path: Path
    wiki_title: Optional[str] = None


RUNECRAFTING_ITEMS = REPO_ROOT / "runecraftingitems"
PROVENANCE = REPO_ROOT / "assets_provenance.json"


MANIFEST: tuple[AssetSpec, ...] = (
    AssetSpec("Air rune", RUNECRAFTING_ITEMS / "air_rune.png"),
    AssetSpec("Mind rune", RUNECRAFTING_ITEMS / "mind_rune.png"),
    AssetSpec("Water rune", RUNECRAFTING_ITEMS / "water_rune.png"),
    AssetSpec("Earth rune", RUNECRAFTING_ITEMS / "earth_rune.png"),
    AssetSpec("Fire rune", RUNECRAFTING_ITEMS / "fire_rune.png"),
    AssetSpec("Body rune", RUNECRAFTING_ITEMS / "body_rune.png"),
    AssetSpec("Cosmic rune", RUNECRAFTING_ITEMS / "cosmic_rune.png"),
    AssetSpec("Chaos rune", RUNECRAFTING_ITEMS / "chaos_rune.png"),
    AssetSpec("Astral rune", RUNECRAFTING_ITEMS / "astral_rune.png"),
    AssetSpec("Nature rune", RUNECRAFTING_ITEMS / "nature_rune.png"),
    AssetSpec("Law rune", RUNECRAFTING_ITEMS / "law_rune.png"),
    AssetSpec("Death rune", RUNECRAFTING_ITEMS / "death_rune.png"),
    AssetSpec("Blood rune", RUNECRAFTING_ITEMS / "blood_rune.png"),
    AssetSpec("Mist rune", RUNECRAFTING_ITEMS / "mist_rune.png"),
    AssetSpec("Dust rune", RUNECRAFTING_ITEMS / "dust_rune.png"),
    AssetSpec("Mud rune", RUNECRAFTING_ITEMS / "mud_rune.png"),
    AssetSpec("Smoke rune", RUNECRAFTING_ITEMS / "smoke_rune.png"),
    AssetSpec("Steam rune", RUNECRAFTING_ITEMS / "steam_rune.png"),
    AssetSpec("Lava rune", RUNECRAFTING_ITEMS / "lava_rune.png"),
    AssetSpec("Air talisman", RUNECRAFTING_ITEMS / "air_talisman.png"),
    AssetSpec("Mind talisman", RUNECRAFTING_ITEMS / "mind_talisman.png"),
    AssetSpec("Water talisman", RUNECRAFTING_ITEMS / "water_talisman.png"),
    AssetSpec("Earth talisman", RUNECRAFTING_ITEMS / "earth_talisman.png"),
    AssetSpec("Fire talisman", RUNECRAFTING_ITEMS / "fire_talisman.png"),
    AssetSpec("Body talisman", RUNECRAFTING_ITEMS / "body_talisman.png"),
    AssetSpec("Cosmic talisman", RUNECRAFTING_ITEMS / "cosmic_talisman.png"),
    AssetSpec("Chaos talisman", RUNECRAFTING_ITEMS / "chaos_talisman.png"),
    AssetSpec("Nature talisman", RUNECRAFTING_ITEMS / "nature_talisman.png"),
    AssetSpec("Law talisman", RUNECRAFTING_ITEMS / "law_talisman.png"),
    AssetSpec("Death talisman", RUNECRAFTING_ITEMS / "death_talisman.png"),
    AssetSpec("Blood talisman", RUNECRAFTING_ITEMS / "blood_talisman.png"),
    AssetSpec("Air tiara", RUNECRAFTING_ITEMS / "air_tiara.png"),
    AssetSpec("Mind tiara", RUNECRAFTING_ITEMS / "mind_tiara.png"),
    AssetSpec("Water tiara", RUNECRAFTING_ITEMS / "water_tiara.png"),
    AssetSpec("Earth tiara", RUNECRAFTING_ITEMS / "earth_tiara.png"),
    AssetSpec("Fire tiara", RUNECRAFTING_ITEMS / "fire_tiara.png"),
    AssetSpec("Body tiara", RUNECRAFTING_ITEMS / "body_tiara.png"),
    AssetSpec("Cosmic tiara", RUNECRAFTING_ITEMS / "cosmic_tiara.png"),
    AssetSpec("Chaos tiara", RUNECRAFTING_ITEMS / "chaos_tiara.png"),
    AssetSpec("Nature tiara", RUNECRAFTING_ITEMS / "nature_tiara.png"),
    AssetSpec("Law tiara", RUNECRAFTING_ITEMS / "law_tiara.png"),
    AssetSpec("Death tiara", RUNECRAFTING_ITEMS / "death_tiara.png"),
    AssetSpec("Blood tiara", RUNECRAFTING_ITEMS / "blood_tiara.png"),
    AssetSpec("Small pouch", RUNECRAFTING_ITEMS / "small_pouch.png"),
    AssetSpec("Medium pouch", RUNECRAFTING_ITEMS / "medium_pouch.png"),
    AssetSpec("Medium pouch (worn)", RUNECRAFTING_ITEMS / "medium_pouch_worn.png", "Medium pouch (degraded).png"),
    AssetSpec("Large pouch", RUNECRAFTING_ITEMS / "large_pouch.png"),
    AssetSpec("Large pouch (worn)", RUNECRAFTING_ITEMS / "large_pouch_worn.png", "Large pouch (degraded).png"),
    AssetSpec("Giant pouch", RUNECRAFTING_ITEMS / "giant_pouch.png"),
    AssetSpec("Giant pouch (worn)", RUNECRAFTING_ITEMS / "giant_pouch_worn.png", "Giant pouch (degraded).png"),
    AssetSpec("Binding necklace", RUNECRAFTING_ITEMS / "binding_necklace.png"),
    AssetSpec("Wicked hood", RUNECRAFTING_ITEMS / "wicked_hood.png"),
)


def _request_for(spec: AssetSpec) -> AssetRequest:
    return AssetRequest(
        item_name=spec.item_name,
        wiki_title=wiki_title_for_item(spec.item_name, spec.wiki_title),
        output_path=spec.output_path,
        provenance_path=PROVENANCE,
    )


def fetch_manifest(specs: Iterable[AssetSpec]) -> int:
    client = HttpWikiClient()
    failures = []
    for spec in specs:
        try:
            outcome = fetch_asset(_request_for(spec), client=client, size=64)
            status = "skipped" if outcome.skipped_existing else "fetched"
            print(f"{status}: {spec.item_name} -> {outcome.output_path}")
        except Exception as exc:  # pragma: no cover - developer tool
            failures.append((spec.item_name, exc))
            print(f"failed: {spec.item_name}: {exc}", file=sys.stderr)
    if failures:
        print(f"{len(failures)} asset fetches failed.", file=sys.stderr)
        return 1
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    _ = argv
    return fetch_manifest(MANIFEST)


if __name__ == "__main__":
    raise SystemExit(main())
