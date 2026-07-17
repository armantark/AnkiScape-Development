#!/usr/bin/env python3
"""Regenerate the pre-EOC surface Summoning catalog.

The historical values come from pinned RuneScape Wiki revisions. The 2011Scape
snapshot supplies stable item IDs and explicit pouch-to-scroll relationships;
Darkan supplies the two non-infusion familiar item IDs that are absent from the
ordinary 2011 crafting enum.
"""

from __future__ import annotations

import json
import pprint
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "summoning_data_generated.py"
GAME_MAIN = Path("/Users/ArmanTarkhanian1/Downloads/game-main")
SUMMONING_SOURCE = (
    GAME_MAIN
    / "game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/summoning"
)
ITEMS_SOURCE = (
    GAME_MAIN
    / "game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt"
)
DARKAN_COMMIT = "d02d8b88a1c7f654a24cdd3cc5a4fb7c9a11a87a"

POUCH_OLDID = 6438719
SCROLL_OLDID = 6520851
FAMILIAR_OLDID = 6579789

EXTRA_ITEM_IDS = {
    "Meerkats pouch": 19622,
    "Fetch casket scroll": 19621,
    "Ghast pouch": 21444,
    "Ghastly attack scroll": 21453,
}


def fetch_wikitext(oldid: int) -> str:
    url = (
        "https://runescape.wiki/api.php?action=parse"
        f"&oldid={oldid}&prop=wikitext&format=json&formatversion=2"
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


def top_level_parts(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in value:
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
    if current:
        parts.append("".join(current).strip())
    return parts


def enum_entries(path: Path) -> list[tuple[str, list[str]]]:
    text = path.read_text(encoding="utf-8")
    start = text.index("{", text.index("enum class")) + 1
    end = text.index("\n    ;", start)
    body = text[start:end]
    entries: list[tuple[str, list[str]]] = []
    cursor = 0
    pattern = re.compile(r"(?m)^    ([A-Z][A-Z0-9_]*)\(")
    while match := pattern.search(body, cursor):
        name = match.group(1)
        open_paren = match.end() - 1
        depth = 0
        close_paren = open_paren
        for close_paren in range(open_paren, len(body)):
            char = body[close_paren]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    break
        entries.append(
            (name, top_level_parts(body[open_paren + 1 : close_paren]))
        )
        cursor = close_paren + 1
    return entries


def item_constants() -> dict[str, int]:
    return {
        name: int(item_id)
        for name, item_id in re.findall(
            r"(?m)^\s*const val ([A-Z][A-Z0-9_]*) = (\d+)$",
            ITEMS_SOURCE.read_text(encoding="utf-8"),
        )
    }


def item_token(token: str) -> str:
    match = re.fullmatch(r"Items\.([A-Z][A-Z0-9_]*)", token.strip())
    if match is None:
        raise ValueError(f"Unsupported item token: {token}")
    return match.group(1)


def item_array(token: str) -> tuple[str, ...]:
    return tuple(re.findall(r"Items\.([A-Z][A-Z0-9_]*)", token))


def wiki_links(value: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for target, display in re.findall(
        r"\[\[([^]|]+)(?:\|([^]]+))?\]\]", value
    ):
        if target.startswith(("File:", "Image:")):
            continue
        links.append((target.strip(), (display or target).strip()))
    return links


def first_link(value: str) -> str:
    links = wiki_links(value)
    if not links:
        raise ValueError(f"No wiki link in {value!r}")
    return links[0][1]


def plain_wiki(value: str) -> str:
    value = re.sub(
        r"\[\[([^]|]+)\|([^]]+)\]\]", lambda match: match.group(2), value
    )
    value = re.sub(r"\[\[([^]]+)\]\]", lambda match: match.group(1), value)
    value = re.sub(r"\[\[(?:File|Image):[^]]+\]\]", "", value)
    value = re.sub(r"<br\s*/?>", "; ", value, flags=re.IGNORECASE)
    value = re.sub(r"\{\{[^{}]*\}\}", "", value)
    value = value.replace("'''", "").replace("''", "")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" ;")


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def familiar_key(value: str) -> str:
    return normalized(re.sub(r"\s*\(?(?:familiar)\)?\s*$", "", value, flags=re.I))


def parse_vertical_table(
    wikitext: str,
    *,
    stop_heading: str | None = None,
) -> list[tuple[int, list[str]]]:
    if stop_heading is not None:
        wikitext = wikitext.split(stop_heading, 1)[0]
    rows: list[tuple[int, list[str]]] = []
    current: list[str] = []
    current_line = 0
    for line_number, line in enumerate(wikitext.splitlines(), 1):
        if line.startswith("|-"):
            if current:
                rows.append((current_line, current))
            current = []
            current_line = line_number + 1
        elif line.startswith("|") and not line.startswith("|}"):
            current.append(line[1:].strip())
        elif current and line.startswith(("*", ":")):
            current[-1] += " " + line
    if current:
        rows.append((current_line, current))
    return [
        (line_number, row)
        for line_number, row in rows
        if row and row[0].strip().isdigit()
    ]


def parse_pouch_rows(wikitext: str) -> list[dict[str, object]]:
    rows = parse_vertical_table(
        wikitext, stop_heading="==Dungeoneering pouches=="
    )
    if len(rows) != 78 or {len(row) for _, row in rows} != {12}:
        raise RuntimeError("Pinned pouch table shape changed")
    parsed: list[dict[str, object]] = []
    for line, row in rows:
        familiar = first_link(row[2])
        charm = next(
            (
                name
                for name in ("Gold", "Green", "Crimson", "Blue")
                if re.search(rf"\b{name}\b", row[4])
            ),
            None,
        )
        if charm is None:
            raise RuntimeError(f"Charm missing for {familiar}")
        tertiaries = tuple(
            dict.fromkeys(
                display[:1].upper() + display[1:]
                for target, display in wiki_links(row[5])
                if not target.startswith(("Exchange:", "Grand Exchange:"))
            )
        )
        if not tertiaries:
            raise RuntimeError(f"Tertiary missing for {familiar}")
        file_match = re.search(r"\[\[File:([^]|]+)", row[1])
        pouch_name = (
            re.sub(
                r"\.png$",
                "",
                file_match.group(1).replace("\u200e", ""),
                flags=re.IGNORECASE,
            )
            if file_match
            else f"{familiar} pouch"
        )
        parsed.append(
            {
                "id": familiar_key(familiar),
                "familiar_name": familiar,
                "pouch_name": pouch_name,
                "level": int(row[0]),
                "shards": int(row[3]),
                "charm": f"{charm} charm",
                "tertiaries": tertiaries,
                "tertiary_mode": "any" if re.search(r"\]\]\s*/\s*\[\[", row[5]) else "all",
                "creation_xp": float(row[6]),
                "bogrog_level": int(row[9]),
                "bogrog_shards": int(row[10]),
                "craftable": True,
                "source": (
                    f"RuneScape Wiki Summoning pouches oldid={POUCH_OLDID}"
                    f":{line}"
                ),
            }
        )
    return parsed


def parse_scroll_rows(wikitext: str) -> list[dict[str, object]]:
    surface = wikitext.split("==Dungeoneering scrolls==", 1)[0]
    lines = surface.splitlines()
    parsed: list[dict[str, object]] = []
    for line_number, line in enumerate(lines, 1):
        if not re.match(r"^\|\s*\d+\s*\|\|", line):
            continue
        row = [part.strip() for part in line[1:].split("||")]
        if len(row) != 7:
            raise RuntimeError(f"Unexpected scroll row at {line_number}")
        name = first_link(row[2])
        familiars = tuple(display for _, display in wiki_links(row[3]))
        parsed.append(
            {
                "id": normalized(name.removesuffix(" scroll")),
                "name": name,
                "level": int(row[0]),
                "familiars": familiars,
                "creation_xp": (
                    None if row[4].casefold() == "n/a" else float(row[4])
                ),
                "use_xp": (
                    None if row[5].casefold() == "n/a" else float(row[5])
                ),
                "special_points": int(row[6]),
                "source": (
                    f"RuneScape Wiki Summoning scrolls oldid={SCROLL_OLDID}"
                    f":{line_number}"
                ),
            }
        )
    if len(parsed) != 68:
        raise RuntimeError(f"Expected 68 surface scroll rows, got {len(parsed)}")
    return parsed


def familiar_roles(combat: str, boost: str, ability: str) -> tuple[str, ...]:
    lowered = ability.casefold()
    roles: list[str] = []
    if "non-combatant" not in combat.casefold():
        roles.append("combat")
    if "beast of burden" in lowered:
        roles.append("beast_of_burden")
    if "forages" in lowered and "stores" not in lowered:
        roles.append("forager_drop")
    if "forages and stores" in lowered:
        roles.append("forager_storage")
    if any(word in lowered for word in ("heal", "cure", "life points")):
        roles.append("healer")
    if "teleport" in lowered:
        roles.append("teleporter")
    if boost:
        roles.append("skill_booster")
    if not roles:
        roles.append("utility")
    return tuple(roles)


def parse_familiar_rows(wikitext: str) -> list[dict[str, object]]:
    table_start = wikitext.index("{|")
    table_end = wikitext.index("|}", table_start) + 2
    rows = parse_vertical_table(wikitext[table_start:table_end])
    if len(rows) != 80:
        raise RuntimeError(f"Expected 80 familiar rows, got {len(rows)}")
    parsed: list[dict[str, object]] = []
    source_line_offset = wikitext[:table_start].count("\n")
    for line, raw_row in rows:
        row = raw_row + [""] * (10 - len(raw_row))
        familiar = first_link(row[2])
        special = plain_wiki(row[7])
        boost = plain_wiki(row[8])
        ability = plain_wiki(row[9])
        capacity_match = re.search(
            r"beast of burden\s*\((\d+)", ability, flags=re.IGNORECASE
        )
        delivery_mode = (
            "drop_to_player"
            if "forages" in ability.casefold()
            and "stores" not in ability.casefold()
            else "familiar_storage"
            if "forages and stores" in ability.casefold()
            else None
        )
        parsed.append(
            {
                "id": familiar_key(familiar),
                "name": familiar,
                "level": int(row[0]),
                "duration_minutes": int(row[3]),
                "summoning_point_cost": int(row[4]),
                "combat": plain_wiki(row[5]),
                "lifepoints": (
                    None
                    if row[6].strip().casefold() == "n/a"
                    else int(re.sub(r"\D", "", row[6]))
                ),
                "special_name": special or None,
                "boost": boost or None,
                "ability_summary": ability or None,
                "roles": familiar_roles(row[5], boost, ability),
                "bob_capacity": int(capacity_match.group(1))
                if capacity_match
                else 0,
                "delivery_mode": delivery_mode,
                "forage_capacity": 30
                if delivery_mode == "familiar_storage"
                else 0,
                "source": (
                    f"RuneScape Wiki Summoning familiars oldid={FAMILIAR_OLDID}"
                    f":{source_line_offset + line}"
                ),
            }
        )
    return parsed


def parse_emulator_pouches(
    constants: dict[str, int],
) -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    path = SUMMONING_SOURCE / "SummoningPouchData.kt"
    for enum_name, parts in enum_entries(path):
        pouch_constant = item_token(parts[5])
        rows[normalized(enum_name)] = {
            "enum": enum_name,
            "pouch_item_id": constants[pouch_constant],
            "tertiary_item_ids": tuple(
                constants[constant] for constant in item_array(parts[0])
            ),
            "charm_item_id": constants[item_token(parts[1])],
            "summon_xp": float(parts[3]),
            "source_emulator": (
                "2011Scape rev-667 "
                "SummoningPouchData.kt"
            ),
        }
    if len(rows) != 78:
        raise RuntimeError(f"Expected 78 emulator pouches, got {len(rows)}")
    return rows


def parse_emulator_scrolls(
    constants: dict[str, int],
) -> tuple[list[dict[str, object]], dict[int, dict[str, object]]]:
    rows: list[dict[str, object]] = []
    by_pouch_id: dict[int, dict[str, object]] = {}
    path = SUMMONING_SOURCE / "SummoningScrollData.kt"
    for enum_name, parts in enum_entries(path):
        row = {
            "enum": enum_name,
            "scroll_item_id": constants[item_token(parts[1])],
            "pouch_item_ids": tuple(
                constants[constant] for constant in item_array(parts[3])
            ),
            "source_emulator": (
                "2011Scape rev-667 "
                "SummoningScrollData.kt"
            ),
        }
        rows.append(row)
        for pouch_id in row["pouch_item_ids"]:
            by_pouch_id[pouch_id] = row
    if len(rows) != 67 or len(by_pouch_id) != 78:
        raise RuntimeError("Unexpected emulator scroll relationship count")
    return rows, by_pouch_id


def closest_by_name(
    wanted: str, rows: list[dict[str, object]], key: str
) -> dict[str, object]:
    wanted_key = normalized(wanted)
    exact = [row for row in rows if normalized(str(row[key])) == wanted_key]
    if len(exact) == 1:
        return exact[0]
    raise RuntimeError(
        f"Could not uniquely match {wanted!r} by {key}: "
        f"{[row[key] for row in exact]}"
    )


def build_catalog() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    constants = item_constants()
    pouch_rows = parse_pouch_rows(fetch_wikitext(POUCH_OLDID))
    scroll_rows = parse_scroll_rows(fetch_wikitext(SCROLL_OLDID))
    familiar_rows = parse_familiar_rows(fetch_wikitext(FAMILIAR_OLDID))
    emulator_pouches = parse_emulator_pouches(constants)
    _, scroll_by_pouch = parse_emulator_scrolls(constants)

    familiar_by_key = {familiar_key(str(row["name"])): row for row in familiar_rows}
    scroll_by_name = {
        normalized(str(row["name"]).removesuffix(" scroll")): row
        for row in scroll_rows
    }

    catalog: list[dict[str, object]] = []
    for pouch in pouch_rows:
        emulator = emulator_pouches[familiar_key(str(pouch["familiar_name"]))]
        pouch_id = int(emulator["pouch_item_id"])
        scroll_emulator = scroll_by_pouch[pouch_id]
        scroll_constant_name = str(scroll_emulator["enum"]).removesuffix("_SCROLL")
        scroll = scroll_by_name.get(normalized(scroll_constant_name))
        if scroll is None:
            aliases = {
                "vampiretouch": "vampyretouch",
                "rishfromtheashes": "risefromtheashes",
                "volcanicstrength": "volcanicstr",
                "adamantbullrush": "addybullrush",
                "titansconstitution": "titanscon",
            }
            wanted = normalized(scroll_constant_name)
            alias = aliases.get(wanted)
            scroll = (
                scroll_by_name.get(alias)
                if alias
                else next(
                    (
                        candidate
                        for key, candidate in scroll_by_name.items()
                        if key.startswith(wanted) or wanted.startswith(key)
                    ),
                    None,
                )
            )
        if scroll is None:
            raise RuntimeError(
                f"Scroll row missing for {scroll_emulator['enum']}"
            )
        familiar = familiar_by_key[familiar_key(str(pouch["familiar_name"]))]
        catalog.append(
            {
                **pouch,
                **emulator,
                "duration_minutes": familiar["duration_minutes"],
                "summoning_point_cost": familiar["summoning_point_cost"],
                "roles": familiar["roles"],
                "bob_capacity": familiar["bob_capacity"],
                "delivery_mode": familiar["delivery_mode"],
                "forage_capacity": familiar["forage_capacity"],
                "boost": familiar["boost"],
                "ability_summary": familiar["ability_summary"],
                "scroll_id": scroll["id"],
                "scroll_name": scroll["name"],
                "scroll_item_id": scroll_emulator["scroll_item_id"],
                "scroll_creation_xp": scroll["creation_xp"],
                "scroll_use_xp": scroll["use_xp"],
                "special_points": scroll["special_points"],
                "special_name": familiar["special_name"],
                "scroll_source": scroll["source"],
            }
        )

    extras = (
        {
            "familiar_name": "Meerkats",
            "pouch_name": "Meerkats pouch",
            "scroll_name": "Fetch casket scroll",
            "summon_xp": 0.1,
            "craftable": False,
            "acquisition": "Treasure Trails casket reward",
        },
        {
            "familiar_name": "Ghast familiar",
            "pouch_name": "Ghast pouch",
            "scroll_name": "Ghastly attack scroll",
            "summon_xp": 3.0,
            "craftable": False,
            "acquisition": "Temple Trekking / Burgh de Rott Ramble reward",
        },
    )
    for extra in extras:
        familiar = familiar_by_key[familiar_key(str(extra["familiar_name"]))]
        scroll = (
            closest_by_name(
                str(extra["scroll_name"]), scroll_rows, "name"
            )
            if extra["familiar_name"] == "Meerkats"
            else {
                "id": "ghastlyattack",
                "name": "Ghastly attack scroll",
                "creation_xp": None,
                "use_xp": 3.0,
                "special_points": 6,
                "source": (
                    "RuneScape Wiki Summoning familiars "
                    f"oldid={FAMILIAR_OLDID}"
                ),
            }
        )
        catalog.append(
            {
                "id": familiar_key(str(extra["familiar_name"])),
                "familiar_name": extra["familiar_name"],
                "pouch_name": extra["pouch_name"],
                "pouch_item_id": EXTRA_ITEM_IDS[str(extra["pouch_name"])],
                "level": familiar["level"],
                "shards": 0,
                "charm": None,
                "charm_item_id": None,
                "tertiaries": (),
                "tertiary_mode": "all",
                "tertiary_item_ids": (),
                "creation_xp": None,
                "summon_xp": extra["summon_xp"],
                "bogrog_level": None,
                "bogrog_shards": None,
                "craftable": False,
                "acquisition": extra["acquisition"],
                "source": familiar["source"],
                "source_emulator": (
                    f"Darkan Pouch.java @ {DARKAN_COMMIT}"
                ),
                "duration_minutes": familiar["duration_minutes"],
                "summoning_point_cost": familiar["summoning_point_cost"],
                "roles": familiar["roles"],
                "bob_capacity": familiar["bob_capacity"],
                "delivery_mode": familiar["delivery_mode"],
                "forage_capacity": familiar["forage_capacity"],
                "boost": familiar["boost"],
                "ability_summary": familiar["ability_summary"],
                "scroll_id": scroll["id"],
                "scroll_name": scroll["name"],
                "scroll_item_id": EXTRA_ITEM_IDS[str(extra["scroll_name"])],
                "scroll_creation_xp": scroll["creation_xp"],
                "scroll_use_xp": scroll["use_xp"],
                "special_points": scroll["special_points"],
                "special_name": familiar["special_name"],
                "scroll_source": scroll["source"],
            }
        )

    catalog.sort(key=lambda row: (int(row["level"]), str(row["familiar_name"])))
    scroll_rows.sort(key=lambda row: (int(row["level"]), str(row["name"])))
    return catalog, scroll_rows


def main() -> None:
    catalog, scroll_rows = build_catalog()
    header = f'''"""Generated pre-EOC surface Summoning catalog.

Sources are pinned RuneScape Wiki oldids {POUCH_OLDID}, {SCROLL_OLDID}, and
{FAMILIAR_OLDID}, reconciled with 2011Scape item IDs and pouch/scroll mappings.
Daemonheim and Stealing Creation rows are excluded by construction.
Do not hand-edit; run tools/generate_summoning_catalog.py.
"""

SUMMONING_POUCH_OLDID = {POUCH_OLDID}
SUMMONING_SCROLL_OLDID = {SCROLL_OLDID}
SUMMONING_FAMILIAR_OLDID = {FAMILIAR_OLDID}
SUMMONING_CATALOG = '''
    output = (
        header
        + pprint.pformat(tuple(catalog), width=100, sort_dicts=False)
        + "\n\nSUMMONING_SCROLLS = "
        + pprint.pformat(tuple(scroll_rows), width=100, sort_dicts=False)
        + "\n"
    )
    OUTPUT.write_text(output, encoding="utf-8")
    print(
        f"Wrote {len(catalog)} surface familiars and "
        f"{len(scroll_rows)} surface scrolls to {OUTPUT}"
    )


if __name__ == "__main__":
    main()
