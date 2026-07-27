#!/usr/bin/env python3
"""Harvest the period achievement-task roster from Darkan and the wiki.

Darkan owns task identity, tier membership, names, descriptions, and encoded
skill/quest requirements. Pinned pre-cutoff wiki revisions are retained only as
corroboration for tier rewards and requirement wording.

Output is a JSON document on stdout. Nothing here writes into the source tree.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


DARKAN_ROOT = Path(
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server"
)
DARKAN_ACHIEVEMENTS = DARKAN_ROOT / "src/main/java/com/rs/game/content/achievements"
DARKAN_ENUMS = DARKAN_ROOT / "developer-information/enums.txt"
DARKAN_QUESTS = DARKAN_ROOT / "src/main/java/com/rs/engine/quest/Quest.java"
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
MISCELLANEOUS_TASK_IDS = tuple(range(3000, 3035))


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


def darkan_task_names() -> dict[int, str]:
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


def _quest_slots() -> dict[int, str]:
    source = DARKAN_QUESTS.read_text(encoding="utf-8")
    return {
        int(slot): constant
        for constant, _quest_id, slot in re.findall(
            r"^\s*([A-Z0-9_]+)\((\d+), (\d+)\),?$", source, re.M
        )
    }


def _cache_params(body: str) -> dict[int, str]:
    return {
        int(param): value.strip()
        for param, value in re.findall(
            r"(\d+) \([^)]+\) = (.*?)(?=, \d+ \([^)]+\) =|, $)", body
        )
    }


def darkan_task_definitions(task_ids: set[int]) -> dict[str, dict]:
    """Decode the referenced achievement structs from rev-727 enum 3483."""

    source = DARKAN_ENUMS.read_text(encoding="utf-8", errors="ignore")
    section = source.split("3483: <int, Struct>", 1)[1].split("\n} ", 1)[0]
    quest_slots = _quest_slots()
    tasks: dict[str, dict] = {}
    for line in section.splitlines()[1:]:
        match = re.match(r"(\d+) = \d+: \{(.*)\}$", line)
        if not match:
            continue
        task_id = int(match.group(1))
        if task_id not in task_ids:
            continue
        params = _cache_params(match.group(2))
        requirements = []
        for key in range(1294, 1313, 2):
            if key not in params or key + 1 not in params:
                continue
            requirement_type = int(params[key])
            value = int(params[key + 1])
            if 1 <= requirement_type <= 25:
                requirements.append(
                    {"kind": "skill", "skill_type": requirement_type, "level": value}
                )
            elif requirement_type == 61:
                requirements.append(
                    {
                        "kind": "quest",
                        "quest_slot": value,
                        "quest": quest_slots.get(value, ""),
                    }
                )
            elif requirement_type == 62:
                requirements.append({"kind": "miscellaneous"})
        tasks[str(task_id)] = {
            "id": task_id,
            "name": params.get(1266, ""),
            "description": params.get(1273, ""),
            "difficulty": int(params.get(1272, "0")),
            "area": int(params.get(1267, "63")),
            "task_set": int(params.get(1293, params.get(1267, "63"))),
            "requirements": requirements,
            "source": "Darkan rev-727 cache enum 3483",
        }
    return tasks


def _wiki_record(title: str) -> dict:
    pinned = pinned_revision(title)
    if pinned is None:
        return {"title": title, "error": "no pre-cutoff revision"}
    oldid, timestamp, resolved = pinned
    return {
        "title": resolved,
        "oldid": oldid,
        "timestamp": timestamp,
        "permalink": f"https://runescape.wiki/w/Special:PermanentLink/{oldid}",
    }


def harvest() -> dict:
    names = darkan_task_names()
    out = {
        "cutoff": CUTOFF,
        "darkan_cache": "revision 727 enum 3483",
        "families": {},
    }
    referenced_ids: set[int] = set()
    for class_name, family_id, wiki_title in FAMILIES:
        record = darkan_family(class_name)
        record["darkan_class"] = class_name
        family_ids = {task_id for ids in record["tiers"].values() for task_id in ids}
        referenced_ids.update(family_ids)
        record["task_names"] = {
            str(task_id): names.get(task_id, "") for task_id in family_ids
        }
        record["wiki"] = _wiki_record(wiki_title)
        out["families"][family_id] = record

    referenced_ids.update(MISCELLANEOUS_TASK_IDS)
    out["families"]["miscellaneous"] = {
        "darkan_class": "Achievement.java IDs 3000-3034",
        "tiers": {"miscellaneous": list(MISCELLANEOUS_TASK_IDS)},
        "task_names": {
            str(task_id): names.get(task_id, "") for task_id in MISCELLANEOUS_TASK_IDS
        },
        "reward_items": {},
        "reward_effects": [],
        "wiki": {},
    }
    out["task_definitions"] = darkan_task_definitions(referenced_ids)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    data = harvest()
    text = json.dumps(data, indent=1, sort_keys=True)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
