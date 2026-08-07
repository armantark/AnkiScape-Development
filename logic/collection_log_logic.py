"""Pure view data for the Collections Music and combat-drop logs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Optional

from ..logic_pure.logic_pure_combat_model import (
    combat_enemy_drop_item_names_pure,
    combat_observed_drops_for_target_pure,
)
from .music_log_logic import music_log_totals_pure


def _count(value: object) -> int:
    if isinstance(value, bool):
        return 0
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _target_rows(
    enemy_data: Mapping[str, Mapping[str, object]],
    group_order: Sequence[str],
) -> tuple[tuple[str, Mapping[str, object], tuple[str, ...]], ...]:
    group_positions = {name: index for index, name in enumerate(group_order)}
    rows = []
    for target_id, enemy in enemy_data.items():
        item_names = combat_enemy_drop_item_names_pure(enemy)
        if not item_names:
            continue
        rows.append((str(target_id), enemy, item_names))
    return tuple(
        sorted(
            rows,
            key=lambda row: (
                group_positions.get(
                    str(row[1].get("group", "")),
                    len(group_positions),
                ),
                _count(row[1].get("level", 0)),
                str(row[1].get("display_name", row[0])).casefold(),
                row[0],
            ),
        )
    )


def drop_log_view_pure(
    player_data: Mapping[str, Any],
    enemy_data: Mapping[str, Mapping[str, object]],
    *,
    target_id: Optional[str] = None,
    search: str = "",
    group_order: Sequence[str] = (),
) -> dict[str, Any]:
    """Project registry drops against durable kill and observation records."""

    kills_raw = player_data.get("combat_kill_counts", {}) or {}
    kills = kills_raw if isinstance(kills_raw, Mapping) else {}
    targets = []
    all_rows = _target_rows(enemy_data, group_order)
    total = 0
    collected = 0
    selected_rows: tuple[dict[str, Any], ...] = ()
    needle = search.strip().casefold()

    for current_id, enemy, item_names in all_rows:
        observed = combat_observed_drops_for_target_pure(
            player_data,
            current_id,
        )
        observed_names = set(observed).intersection(item_names)
        target_collected = len(observed_names)
        target_total = len(item_names)
        kill_count = _count(kills.get(current_id, 0))
        if bool(enemy.get("encounter_only")) and kill_count <= 0:
            continue
        target_name = str(enemy.get("display_name", current_id) or current_id)
        total += target_total
        collected += target_collected
        target_row = {
            "target_id": current_id,
            "name": target_name,
            "group": str(enemy.get("group", "") or ""),
            "level": _count(enemy.get("level", 0)),
            "kills": kill_count,
            "collected": target_collected,
            "total": target_total,
        }
        if target_id is None and (
            not needle or needle in target_name.casefold()
        ):
            targets.append(target_row)

        if current_id != target_id:
            continue
        discovered = kill_count > 0
        rows = []
        for item_name in item_names:
            observation = observed.get(item_name, {}) or {}
            state = (
                "undiscovered"
                if not discovered
                else "collected"
                if item_name in observed_names
                else "discovered"
            )
            label = item_name if discovered else "???"
            if needle and needle not in label.casefold():
                continue
            rows.append(
                {
                    "item_name": item_name,
                    "label": label,
                    "state": state,
                    "times_seen": _count(observation.get("times_seen", 0)),
                    "quantity_seen": _count(
                        observation.get("quantity_seen", 0)
                    ),
                }
            )
        selected_rows = tuple(rows)

    return {
        "targets": tuple(targets),
        "rows": selected_rows,
        "collected": collected,
        "total": total,
    }


def collection_totals_pure(
    player_data: Mapping[str, Any],
    enemy_data: Mapping[str, Mapping[str, object]],
) -> dict[str, dict[str, int]]:
    music = music_log_totals_pure(player_data)
    drops = drop_log_view_pure(player_data, enemy_data)
    music_totals = {
        "collected": int(music["unlocked"]),
        "total": int(music["total"]),
    }
    drop_totals = {
        "collected": int(drops["collected"]),
        "total": int(drops["total"]),
    }
    return {
        "music": music_totals,
        "drop_log": drop_totals,
        "global": {
            "collected": music_totals["collected"]
            + drop_totals["collected"],
            "total": music_totals["total"] + drop_totals["total"],
        },
    }
