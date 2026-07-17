#!/usr/bin/env python3
"""Generate the complete freeze-date pet catalog from pinned wiki wikitext."""

from __future__ import annotations

import json
import pprint
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pet_data_generated.py"
PET_OLDID = 6579897
LEGACY_EVENT_PETS = frozenset({"Sparkles", "Eek", "Mackers"})
RELEASE_SOURCE_BLOCKED = frozenset({"Ex-ex-parrot", "Broav"})
STAGE_COUNT_OVERRIDES = {"Cat": 3}
FOOD_OVERRIDES = {
    "Broav": ("Mort myre fungus",),
}


def fetch_wikitext() -> str:
    url = (
        "https://runescape.wiki/api.php?action=parse"
        f"&oldid={PET_OLDID}&prop=wikitext&format=json&formatversion=2"
    )
    completed = subprocess.run(
        [
            "curl",
            "--fail",
            "--silent",
            "--show-error",
            "--retry",
            "3",
            "--retry-delay",
            "2",
            url,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)["parse"]["wikitext"]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def links(value: str) -> list[tuple[str, str]]:
    rows = []
    for match in re.finditer(r"\[\[([^]|]+)(?:\|([^]]+))?\]\]", value):
        target = match.group(1).strip()
        display = (match.group(2) or target).strip()
        if target.casefold().startswith(("file:", "image:")):
            continue
        rows.append((target, display))
    return rows


def file_names(value: str) -> tuple[str, ...]:
    return tuple(
        match.group(1).strip()
        for match in re.finditer(
            r"\[\[(?:File|Image):([^]|]+)", value, flags=re.IGNORECASE
        )
    )


def plain(value: str) -> str:
    value = re.sub(
        r"\[\[(?:File|Image):[^]]+\]\]", "", value, flags=re.IGNORECASE
    )
    value = re.sub(
        r"\[\[([^]|]+)\|([^]]+)\]\]", lambda match: match.group(2), value
    )
    value = re.sub(r"\[\[([^]]+)\]\]", lambda match: match.group(1), value)
    value = re.sub(r"<br\s*/?>", "; ", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"'{2,}", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" |;\n")


def table_rows(table_text: str) -> list[list[str]]:
    body = table_text.split("\n|-", 1)[1]
    rows = []
    for chunk in body.split("\n|-"):
        chunk = chunk.split("\n|}", 1)[0]
        cells = []
        current = []
        for line in chunk.splitlines():
            if line.startswith("|"):
                if current:
                    cells.append("\n".join(current))
                current = [line[1:]]
            elif current:
                current.append(line)
        if current:
            cells.append("\n".join(current))
        if cells:
            rows.append(cells)
    return rows


def named_pet_rows(
    cells: list[str], *, summoning_related: bool
) -> list[dict[str, object]]:
    if summoning_related:
        requirements, stages, pet_cell, food, obtained, colours = cells
        level_match = re.search(r"\d+", plain(requirements))
        level = int(level_match.group()) if level_match else 1
    else:
        stages, pet_cell, food, obtained, colours = cells
        requirements = ""
        level = 1

    pet_links = links(pet_cell)
    names = [display for _target, display in pet_links]
    if not names:
        names = [plain(pet_cell)]
    images = file_names(stages)
    if len(names) > 1:
        image_groups = [(image,) for image in images]
    else:
        image_groups = [images]
    foods = tuple(
        dict.fromkeys(display for _target, display in links(food))
    )
    colours_match = re.search(r"\d+", plain(colours))
    colour_count = int(colours_match.group()) if colours_match else 1
    result = []
    for index, name in enumerate(names):
        stage_images = image_groups[min(index, len(image_groups) - 1)]
        stage_count = len(stage_images)
        if name == "Tooth creature":
            stage_count = 2
        result.append(
            {
                "id": slug(name),
                "display_name": name,
                "summoning_level": level,
                "requirements": plain(requirements),
                "stage_images": stage_images,
                "stage_count": STAGE_COUNT_OVERRIDES.get(
                    name, max(1, stage_count)
                ),
                "foods": FOOD_OVERRIDES.get(name, foods),
                "food_summary": plain(food),
                "acquisition": plain(obtained),
                "colour_count": colour_count,
                "summoning_related": summoning_related,
                "obtainable": name not in LEGACY_EVENT_PETS,
                "legacy_compatibility_only": name in LEGACY_EVENT_PETS,
                "release_source_blocked": name in RELEASE_SOURCE_BLOCKED,
                "source": f"RuneScape Wiki Pet oldid={PET_OLDID}",
            }
        )
    return result


def build_catalog() -> list[dict[str, object]]:
    wikitext = fetch_wikitext()
    summoning_table = wikitext.split(
        "==List of Summoning pets==", 1
    )[1].split("==List of non-Summoning pets==", 1)[0]
    ordinary_table = wikitext.split(
        "==List of non-Summoning pets==", 1
    )[1].split("==Use and reception==", 1)[0]
    catalog = []
    for cells in table_rows(summoning_table):
        if len(cells) == 6:
            catalog.extend(named_pet_rows(cells, summoning_related=True))
    for cells in table_rows(ordinary_table):
        if len(cells) == 5:
            catalog.extend(named_pet_rows(cells, summoning_related=False))
    catalog.sort(
        key=lambda row: (
            int(row["summoning_level"]),
            str(row["display_name"]),
        )
    )
    if len(catalog) != 47:
        raise RuntimeError(f"Expected 47 stable pet definitions, got {len(catalog)}")
    if sum(bool(row["obtainable"]) for row in catalog) != 44:
        raise RuntimeError("Expected 44 obtainable pet definitions")
    if len({str(row["id"]) for row in catalog}) != len(catalog):
        raise RuntimeError("Pet IDs are not unique")
    return catalog


def main() -> None:
    catalog = build_catalog()
    output = f'''"""Generated freeze-date pet catalog.

Source: RuneScape Wiki Pet oldid={PET_OLDID}.
Do not hand-edit; run tools/generate_pet_catalog.py.
"""

PET_OLDID = {PET_OLDID}
PET_CATALOG = '''
    output += pprint.pformat(tuple(catalog), width=100, sort_dicts=False)
    output += "\n"
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"Wrote {len(catalog)} pet definitions to {OUTPUT}")


if __name__ == "__main__":
    main()
