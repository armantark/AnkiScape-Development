"""Sourced Utility routes for preparing pestle-and-mortar inputs."""

from __future__ import annotations

from typing import Dict


RUNE_SHARDS_SOURCE = "https://runescape.wiki/w/Rune_shards?oldid=6407335"


GRIND_SOURCE_ACTIVITIES = {
    "make_rune_shards": {
        "display_name": "Make rune shards",
        "requirements": {"Rune essence": 1},
        "material_options": {"Rune essence": ("Rune essence", "Pure essence")},
        "required_item_options": (("Chisel", "Hammer"),),
        "output_item": "Rune shards",
        "output_qty": 1,
        "batch_size": 1,
        "group": "input_preparation",
        "source": RUNE_SHARDS_SOURCE,
    },
}


def grind_source_activities_as_dict() -> Dict[str, Dict[str, object]]:
    return {activity_id: dict(spec) for activity_id, spec in GRIND_SOURCE_ACTIVITIES.items()}
