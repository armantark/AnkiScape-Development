#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch the small source-visible Thieving asset manifest."""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.fetch_assets import PRE_EOC_CUTOFF, AssetFetchError, AssetRequest, HttpWikiClient, OSRS_WIKI, RS3_WIKI, fetch_asset


THIEVING_NPC_TITLES = {
    "pickpocket_man": "Man.png",
    "pickpocket_farmer": "Farmer.png",
    "pickpocket_female_ham": "H.A.M. Member (female).png",
    "pickpocket_male_ham": "H.A.M. Member (male).png",
    "pickpocket_warrior": "Al Kharid warrior.png",
    "pickpocket_rogue": "Rogue.png",
    "pickpocket_cave_goblin": "Cave goblin (monster, 3).png",
    "pickpocket_master_farmer": "Master Farmer.png",
    "pickpocket_guard": "Guard (Varrock).png",
    "pickpocket_fremennik": "Fremennik citizen.png",
    "pickpocket_desert_bandit": "Bandit (Pollnivneach).png",
    "pickpocket_ardougne_knight": "Knight of Ardougne.png",
    "pickpocket_watchman": "Watchman (2006).png",
    "pickpocket_paladin": "Paladin.png",
    "pickpocket_gnome": "Gnome woman.png",
    "pickpocket_hero": "Hero.png",
    "pickpocket_pompous_merchant": "Pompous merchant chathead.png",
    "blackjack_menaphite_thug": "Menaphite Thug.png",
    # These files were uploaded after the cutoff, but their titles identify the
    # historical 2010 Iorwerth and 2006 Watchman models. The latter matches the
    # same red-trousered, blue-shirted model in the cutoff Watchman screenshot.
    "pickpocket_lletya_elf": "Elf warrior (Iorwerth ranger) (2010).png",
}

POST_CUTOFF_HISTORICAL_TARGETS = frozenset(
    {"pickpocket_lletya_elf", "pickpocket_watchman"}
)


def asset_manifest() -> tuple[AssetRequest, ...]:
    provenance = ROOT / "assets_provenance.json"
    common = (
        AssetRequest(
            item_name="Desert Phoenix",
            wiki_title="Desert Phoenix.png",
            output_path=ROOT / "activityicons" / "desert_phoenix.png",
            provenance_path=provenance,
        ),
    )
    portraits = tuple(
        AssetRequest(
            item_name=target_id,
            wiki_title=wiki_title,
            output_path=ROOT / "combatenemies" / f"{target_id}.png",
            provenance_path=provenance,
        )
        for target_id, wiki_title in THIEVING_NPC_TITLES.items()
    )
    return common + portraits


def main() -> int:
    period_client = HttpWikiClient(
        min_interval_seconds=1.1,
        before_timestamp=PRE_EOC_CUTOFF,
    )
    archive_client = HttpWikiClient(min_interval_seconds=1.1)
    failures: list[str] = []
    for request in asset_manifest():
        if request.output_path.exists():
            continue
        target_id = request.output_path.stem
        client = (
            archive_client
            if target_id in POST_CUTOFF_HISTORICAL_TARGETS
            else period_client
        )
        try:
            outcome = fetch_asset(request, client, size=64, sources=(RS3_WIKI, OSRS_WIKI))
            print(asdict(outcome))
        except AssetFetchError as exc:
            failures.append(f"{request.item_name}: {exc}")
    if failures:
        print("Unresolved Thieving assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
