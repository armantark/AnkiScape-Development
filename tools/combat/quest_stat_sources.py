"""Reviewed quest-specific NPC variants and explicit source blocks."""

from functools import lru_cache
import json
from pathlib import Path


SOURCE_PATH = Path(__file__).with_name("quest_stat_sources.json")


@lru_cache(maxsize=1)
def reviewed_sources():
    rows = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))["encounters"]
    return {(row["quest_id"], row["display_name"], row["input_level"]): row for row in rows}


def reviewed_source(quest_id, display_name, level):
    return reviewed_sources().get((quest_id, display_name, level))


def matching_quest_stats(quest_id, display_name, level, fallback):
    reviewed = reviewed_source(quest_id, display_name, level)
    if reviewed is None:
        return fallback(display_name, level)
    # A complete emulator payload can still be a disclosed calibration, not evidence.
    return reviewed.get("payload", {})
