#!/usr/bin/env python3
"""Harvest the period achievement-task roster from Darkan and the wiki.

Two sources, in the project's evidence order:

1. **Darkan** owns the structure. ``com/rs/game/content/achievements`` carries
   the ``Achievement`` id/name enum, one ``<Region>Tasks`` class per family with
   the exact per-tier task-id lists, the taskmaster NPC for each tier, the
   reward item ids, and several sourced tier reward effects. This is the
   authority for *which* tasks belong to *which* tier.
2. **The wiki**, pinned before the EOC cutoff, owns the per-task requirement
   text: the description, the quests needed and the skill levels needed. Darkan
   reads those from the cache at runtime, so they are not in its source.

Output is a JSON document on stdout. ``--markdown`` writes the source-audit
companion instead. Nothing here writes into the add-on.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


DARKAN_ACHIEVEMENTS = Path(
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server"
    "/src/main/java/com/rs/game/content/achievements"
)
CUTOFF = "2012-11-20T00:00:00Z"
USER_AGENT = "AnkiScape-source-audit/1.0 (pre-EOC parity harvest)"

# Darkan class -> (AnkiScape family id, wiki page title).
FAMILIES = (
    ("ArdougneTasks", "ardougne", "Ardougne Tasks"),
    ("FaladorTasks", "falador", "Falador Tasks"),
    ("FremennikTasks", "fremennik", "Fremennik Tasks"),
    ("KaramjaTasks", "karamja", "Karamja Tasks"),
    ("LumbridgeDraynorTasks", "lumbridge", "Lumbridge and Draynor Tasks"),
    ("MorytaniaTasks", "morytania", "Morytania Tasks"),
    ("SeersVillageTasks", "seers", "Seers' Village Tasks"),
    ("VarrockTasks", "varrock", "Varrock Tasks"),
    ("BurthorpeTaverleyTasks", "burthorpe", "Burthorpe and Taverley Tasks"),
)


def _api(params: dict) -> dict:
    url = "https://runescape.wiki/api.php?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as handle:
                return json.load(handle)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def pinned_revision(title: str) -> "tuple[int, str, str] | None":
    payload = _api(
        {
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "rvprop": "ids|timestamp",
            "rvlimit": 1,
            "rvstart": CUTOFF,
            "rvdir": "older",
            "format": "json",
            "formatversion": 2,
            "redirects": 1,
        }
    )
    page = payload["query"]["pages"][0]
    revisions = page.get("revisions") or []
    if not revisions:
        return None
    return revisions[0]["revid"], revisions[0]["timestamp"], page["title"]


def wikitext(oldid: int) -> str:
    payload = _api(
        {
            "action": "parse",
            "oldid": oldid,
            "prop": "wikitext",
            "format": "json",
            "formatversion": 2,
        }
    )
    return payload["parse"]["wikitext"]


def darkan_task_names() -> dict[int, str]:
    """Map task id to the period task name Darkan's enum preserves."""

    source = (DARKAN_ACHIEVEMENTS / "Achievement.java").read_text(encoding="utf-8")
    names: dict[int, str] = {}
    for constant, raw_id in re.findall(r"^\t([A-Z0-9_]+)\((\d+)\),?$", source, re.M):
        task_id = int(raw_id)
        names[task_id] = re.sub(rf"_{task_id}$", "", constant)
    return names


def darkan_family(class_name: str) -> dict:
    source = (DARKAN_ACHIEVEMENTS / f"{class_name}.java").read_text(encoding="utf-8")
    tiers = {
        match.group(1).lower(): [int(x) for x in re.findall(r"\d+", match.group(2))]
        for match in re.finditer(
            r"public static final int\[\] ([A-Z_]+)_TASK_IDS = \{([^}]*)\}", source
        )
    }
    rewards = {
        match.group(1): [int(x) for x in re.findall(r"\d+", match.group(2))]
        for match in re.finditer(
            r"public static final int\[\] ([A-Z_]+)_REWARD_ITEMS = \{([^}]*)\}", source
        )
    }
    effects = re.findall(
        r"public static (?:int|boolean) (\w+)\(Player player[^)]*\) \{", source
    )
    skip = {"isPeriodTask", "complete", "hasCompletedThrough", "completedCount", "ownsRewardItem"}
    return {
        "tiers": tiers,
        "reward_items": rewards,
        "reward_effects": [name for name in effects if name not in skip],
    }


_TIER_HEADING = re.compile(
    r"^==\s*(Beginner|Easy|Medium|Hard|Elite)\s+tasks?\s*==", re.M | re.I
)
_SKILL_REQ = re.compile(r"\{\{Skillreq\|([A-Za-z ]+)\|(\d+)")
# The other house style writes the level first and the skill as a click-pic.
_SKILL_PIC = re.compile(r"(\d+)\s*\{\{Skill ?clickpic\|([A-Za-z ]+)")


def wiki_tier_tasks(text: str) -> dict[str, list[dict]]:
    """Pull each tier's guide table into rows of name/description/quests/skills.

    The nine pages use two different table shapes and two different ways of
    writing a skill requirement, so the parser accepts both rather than
    silently returning an empty tier for six of the families.
    """

    sections: dict[str, str] = {}
    matches = list(_TIER_HEADING.finditer(text))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).lower()] = text[match.start() : end]

    tiers: dict[str, list[dict]] = {}
    for tier, body in sections.items():
        rows: list[dict] = []
        for table in re.findall(
            r"\{\|\s*class=\"wikitable[^\n]*\n(.*?)\n\|\}", body, re.S
        ):
            header, _, rest = table.partition("\n|-")
            if "!Task" not in header.replace(" ", ""):
                continue
            for block in re.split(r"\n\|-[^\n]*\n", rest):
                cells = _cells(block)
                # Karamja numbers its tasks in a column of their own, which
                # shifts every later column by one.
                if cells and re.fullmatch(r"\d+[.)]?", _plain(cells[0])):
                    cells = cells[1:]
                if len(cells) < 3:
                    continue
                name = _plain(cells[0])
                if not name or name.lower() in {"task", "notes"}:
                    continue
                rows.append(
                    {
                        "name": re.sub(r"^\d+[.)]\s*", "", name),
                        "description": re.sub(r"^\d+\s*-\s*", "", _plain(cells[1])),
                        "quests": _links(cells[2]),
                        "skills": _skill_reqs(cells[3]) if len(cells) > 3 else [],
                    }
                )
        if rows:
            tiers[tier] = rows
    return tiers


def _cells(block: str) -> list[str]:
    parts: list[str] = []
    for line in ("\n" + block).split("\n|"):
        if not line:
            continue
        for cell in line.split("||"):
            parts.append(re.sub(r'^\s*style="[^"]*"\s*\|', "", cell).strip())
    return [cell for cell in parts if cell != ""]


def _plain(cell: str) -> str:
    cell = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", cell)
    cell = re.sub(r"\{\{[^}]*\}\}", " ", cell)
    cell = re.sub(r"''+", "", cell)
    cell = re.sub(r"<[^>]+>", " ", cell)
    return re.sub(r"\s+", " ", cell).strip()


def _links(cell: str) -> list[str]:
    if re.search(r"^\s*(''None''|None)\s*$", cell.strip(), re.I):
        return []
    return [name.strip() for name in re.findall(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", cell)]


def _skill_reqs(cell: str) -> list[list]:
    found = [(skill, level) for skill, level in _SKILL_REQ.findall(cell)]
    found += [(skill, level) for level, skill in _SKILL_PIC.findall(cell)]
    seen: dict[str, int] = {}
    for skill, level in found:
        key = skill.strip()
        seen[key] = max(seen.get(key, 0), int(level))
    return [[skill, level] for skill, level in seen.items()]


def lamp_experience(text: str) -> list[str]:
    match = re.search(r"\|lamp\s*=\s*([^\n|]*)", text)
    if not match:
        return []
    return [part.strip() for part in re.split(r"<br\s*/?>", match.group(1)) if part.strip()]


def harvest() -> dict:
    names = darkan_task_names()
    out = {"cutoff": CUTOFF, "families": {}}
    for class_name, family_id, wiki_title in FAMILIES:
        record = darkan_family(class_name)
        record["darkan_class"] = class_name
        record["task_names"] = {
            str(task_id): names.get(task_id, "")
            for ids in record["tiers"].values()
            for task_id in ids
        }
        pinned = pinned_revision(wiki_title)
        if pinned is None:
            record["wiki"] = {"title": wiki_title, "error": "no pre-cutoff revision"}
        else:
            oldid, timestamp, resolved = pinned
            text = wikitext(oldid)
            record["wiki"] = {
                "title": resolved,
                "oldid": oldid,
                "timestamp": timestamp,
                "permalink": f"https://runescape.wiki/w/Special:PermanentLink/{oldid}",
                "lamp_experience": lamp_experience(text),
                "tiers": wiki_tier_tasks(text),
            }
            time.sleep(1.1)
        out["families"][family_id] = record
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    data = harvest()
    text = json.dumps(data, indent=1, sort_keys=True)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
