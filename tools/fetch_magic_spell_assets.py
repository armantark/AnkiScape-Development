#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow>=10"]
# ///
"""Fetch cutoff-pinned spellbook icons for every live Magic target."""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from magic_data import MAGIC_TARGETS  # noqa: E402
from tools.fetch_assets import (  # noqa: E402
    AssetFetchError,
    AssetRequest,
    HttpWikiClient,
    ImageInfo,
    OSRS_WIKI,
    WikiSource,
    update_provenance,
    write_png,
)
from tools.fetch_navigation_icons import CUTOFF, period_image_info  # noqa: E402


WIKI_TITLE_OVERRIDES: dict[str, str] = {
    "ape_atoll_teleport": "Ape Atoll Teleport icon.png",
    "telegrab_wine_of_zamorak": "Telekinetic Grab icon.png",
    "plank_make_logs": "Plank Make icon.png",
    "plank_make_oak_logs": "Plank Make icon.png",
    "plank_make_teak_logs": "Plank Make icon.png",
    "plank_make_mahogany_logs": "Plank Make icon.png",
}
WIKI_TITLE_OVERRIDES.update(
    {
        target_id: "Make Leather icon.png"
        for target_id in MAGIC_TARGETS
        if target_id.startswith("make_")
    }
)
for gem, spell_level in (
    ("sapphire", 1),
    ("emerald", 2),
    ("ruby", 3),
    ("diamond", 4),
    ("dragonstone", 5),
    ("onyx", 6),
):
    WIKI_TITLE_OVERRIDES.update(
        {
            target_id: f"Lvl-{spell_level} Enchant icon.png"
            for target_id in MAGIC_TARGETS
            if target_id.startswith(f"enchant_{gem}_")
            and not target_id.endswith("_bolts")
        }
    )
WIKI_TITLE_OVERRIDES.update(
    {
        target_id: "Enchant Crossbow Bolt icon.png"
        for target_id in MAGIC_TARGETS
        if target_id.startswith("enchant_") and target_id.endswith("_bolts")
    }
)
WIKI_TITLE_OVERRIDES.update(
    {
        target_id: "Superheat Item icon.png"
        for target_id in MAGIC_TARGETS
        if target_id.startswith("superheat_")
    }
)

# The migrated RuneScape Wiki does not expose every pre-EOC file revision.
# These exact legacy sprites remain available from the former RuneScape Wiki
# host with period timestamps.
LEGACY_PERIOD_TITLES = {
    "teleport_to_house": "Teleport to House icon.png",
    "spiritualise_food": "Spiritualise Food icon.png",
    **{
        target_id: "Make Leather icon.png"
        for target_id in MAGIC_TARGETS
        if target_id.startswith("make_")
    },
}

# These spells lack a cutoff-pinned file revision on either surviving wiki.
# Use their exact classic spellbook sprite as a visual fallback and label the
# exception honestly in provenance.
OSRS_VISUAL_FALLBACK_TITLES = {
    "tan_leather": "Tan Leather.png",
    "magic_imbue": "Magic Imbue.png",
    "cure_plant": "Cure Plant.png",
    "fertile_soil": "Fertile Soil.png",
}
LEGACY_VISUAL_FALLBACK_TITLES = {
    "mobilising_armies_teleport": "Mobilising armies teleport.png",
    "borrowed_telegrab_wine_of_zamorak": "Borrowed Power icon.png",
    "borrowed_teleport_to_house": "Borrowed Power icon.png",
    "borrowed_high_alchemy": "Borrowed Power icon.png",
    "borrowed_bones_to_peaches": "Borrowed Power icon.png",
}

LEGACY_PERIOD_WIKI = WikiSource(
    name="rs3-fandom-period",
    api_url="https://runescape.fandom.com/api.php",
    page_base_url="https://runescape.fandom.com",
)
LEGACY_VISUAL_FALLBACK_WIKI = WikiSource(
    name="rs3-fandom-visual-fallback",
    api_url="https://runescape.fandom.com/api.php",
    page_base_url="https://runescape.fandom.com",
)


def _original_fandom_image(info: ImageInfo) -> ImageInfo:
    separator = "&" if "?" in info.image_url else "?"
    return replace(
        info,
        image_url=f"{info.image_url}{separator}format=original",
    )


def _required_image_info(
    client: HttpWikiClient,
    source: WikiSource,
    title: str,
) -> ImageInfo:
    info = client.query_image_info(source, title)
    if info is None:
        raise AssetFetchError(
            f"No {source.name} file matched {title}"
        )
    if "fandom.com" in source.api_url:
        return _original_fandom_image(info)
    return info


def main() -> int:
    client = HttpWikiClient(min_interval_seconds=0.8)
    legacy_period_client = HttpWikiClient(
        min_interval_seconds=0.8,
        before_timestamp=CUTOFF,
    )
    fallback_client = HttpWikiClient(min_interval_seconds=0.8)
    failures: list[str] = []
    for target_id, spec in MAGIC_TARGETS.items():
        display_name = str(spec["display_name"])
        wiki_title = WIKI_TITLE_OVERRIDES.get(
            target_id,
            f"{display_name} icon.png",
        )
        request = AssetRequest(
            item_name=f"{display_name} spell icon",
            wiki_title=wiki_title,
            output_path=ROOT / "magicspells" / f"{target_id}.png",
            provenance_path=ROOT / "assets_provenance.json",
        )
        try:
            if target_id in LEGACY_PERIOD_TITLES:
                info = _required_image_info(
                    legacy_period_client,
                    LEGACY_PERIOD_WIKI,
                    LEGACY_PERIOD_TITLES[target_id],
                )
            elif target_id in OSRS_VISUAL_FALLBACK_TITLES:
                info = replace(
                    _required_image_info(
                        fallback_client,
                        OSRS_WIKI,
                        OSRS_VISUAL_FALLBACK_TITLES[target_id],
                    ),
                    source_wiki="osrs-visual-fallback",
                )
            elif target_id in LEGACY_VISUAL_FALLBACK_TITLES:
                info = _required_image_info(
                    fallback_client,
                    LEGACY_VISUAL_FALLBACK_WIKI,
                    LEGACY_VISUAL_FALLBACK_TITLES[target_id],
                )
            else:
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
            print(
                f"{target_id}: {info.timestamp} -> "
                f"{request.output_path.relative_to(ROOT)}"
            )
        except AssetFetchError as exc:
            failures.append(f"{target_id} ({wiki_title}): {exc}")
    if failures:
        print("Unresolved Magic spell assets:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
