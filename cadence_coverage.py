"""Auditable whole-addon cadence coverage catalog."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping

try:
    from .agility_data import AGILITY_TARGETS_BY_ID
    from .cadence_live import cadence_declaration_dict_pure, resolve_live_cadence_route_pure
    from .constants import (
        COMBAT_ENEMY_DATA,
        COOKING_DATA,
        CRAFTING_DATA,
        FIREMAKING_DATA,
        FISHING_DATA,
        FLETCHING_DATA,
        HERBLORE_DATA,
        HUNTER_DATA,
        MAGIC_DATA,
        ORE_DATA,
        PRAYER_DATA,
        QUEST_DATA,
        RUNECRAFTING_DATA,
        SMITHING_DATA,
        TREE_DATA,
        UTILITY_ACTIVITY_DATA,
    )
    from .construction_data import CONSTRUCTION_DATA
    from .summoning_data import SUMMONING_ACTIONS_BY_ID
    from .thieving_data import THIEVING_TARGETS
except ImportError:  # pragma: no cover - flat imports used by tests/tools
    from agility_data import AGILITY_TARGETS_BY_ID  # type: ignore
    from cadence_live import cadence_declaration_dict_pure, resolve_live_cadence_route_pure  # type: ignore
    from constants import (  # type: ignore
        COMBAT_ENEMY_DATA,
        COOKING_DATA,
        CRAFTING_DATA,
        FIREMAKING_DATA,
        FISHING_DATA,
        FLETCHING_DATA,
        HERBLORE_DATA,
        HUNTER_DATA,
        MAGIC_DATA,
        ORE_DATA,
        PRAYER_DATA,
        QUEST_DATA,
        RUNECRAFTING_DATA,
        SMITHING_DATA,
        TREE_DATA,
        UTILITY_ACTIVITY_DATA,
    )
    from construction_data import CONSTRUCTION_DATA  # type: ignore
    from summoning_data import SUMMONING_ACTIONS_BY_ID  # type: ignore
    from thieving_data import THIEVING_TARGETS  # type: ignore


FOREGROUND_ROUTE_TABLES: dict[str, Mapping[str, Any]] = {
    "mining": ORE_DATA,
    "woodcutting": TREE_DATA,
    "smithing": SMITHING_DATA,
    "crafting": CRAFTING_DATA,
    "fletching": FLETCHING_DATA,
    "firemaking": FIREMAKING_DATA,
    "fishing": FISHING_DATA,
    "hunter": HUNTER_DATA,
    "cooking": COOKING_DATA,
    "runecrafting": RUNECRAFTING_DATA,
    "herblore": HERBLORE_DATA,
    "prayer": PRAYER_DATA,
    "magic": MAGIC_DATA,
    "construction": CONSTRUCTION_DATA,
    "thieving": THIEVING_TARGETS,
    "agility": AGILITY_TARGETS_BY_ID,
    "summoning": SUMMONING_ACTIONS_BY_ID,
    "combat": COMBAT_ENEMY_DATA,
}

CADENCE_DECLARED_HANDLER_KEYS = frozenset(
    {*FOREGROUND_ROUTE_TABLES, "utility", "quest"}
)


def _catalog_player_data() -> dict[str, Any]:
    target_ids = {
        str(target_id)
        for table in FOREGROUND_ROUTE_TABLES.values()
        for target_id in table
    }
    return {
        "equipment": {"weapon": "Fire staff"},
        "carried_keep_drop": {target_id: "drop" for target_id in target_ids},
    }


def cadence_coverage_rows_pure() -> list[dict[str, Any]]:
    """Return one declaration for every selectable route plus explicit exemptions."""

    player_data = _catalog_player_data()
    rows: list[dict[str, Any]] = []
    for handler_key, table in FOREGROUND_ROUTE_TABLES.items():
        for action_id in table:
            row = cadence_declaration_dict_pure(
                resolve_live_cadence_route_pure(handler_key, str(action_id), player_data)
            )
            row["route_kind"] = "foreground"
            rows.append(row)

    for action_id, spec in UTILITY_ACTIVITY_DATA.items():
        rows.append(
            {
                "handler_key": "utility",
                "action_id": str(action_id),
                "mode": "exempt",
                "source_status": "not_applicable",
                "source_row": str(spec.get("source", "")) if isinstance(spec, Mapping) else "",
                "source_reason": "Utility/Activity review actions are batching or progression, not foreground XP/hour admissions",
                "includes": (),
                "multiplier_behavior": "M handler actions under the established dispatcher",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "same utility handler",
                "profile": None,
                "condition": "",
                "route_kind": "utility",
            }
        )

    for action_id, reason, includes in (
        ("stronghold_of_security", "finite no-XP landmark progression", ()),
        (
            "knight_waves",
            "finite non-repeatable landmark; final combat-stat XP cannot repeat",
            ("attack", "strength", "defence", "constitution"),
        ),
        ("mage_arena", "finite no-XP landmark progression", ()),
        ("mage_arena_attune:guthix", "finite no-XP spell attunement", ()),
        ("mage_arena_attune:saradomin", "finite no-XP spell attunement", ()),
        ("mage_arena_attune:zamorak", "finite no-XP spell attunement", ()),
    ):
        rows.append(
            {
                "handler_key": "utility",
                "action_id": action_id,
                "mode": "exempt",
                "source_status": "not_applicable",
                "source_row": "",
                "source_reason": reason,
                "includes": includes,
                "multiplier_behavior": "established landmark step transaction",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "same landmark handler",
                "profile": None,
                "condition": "",
                "route_kind": "utility_landmark",
            }
        )

    for quest_id, spec in QUEST_DATA.items():
        rewards = tuple(
            f"{reward.get('skill_id')}:{reward.get('amount')}"
            for reward in (spec.get("xp_rewards", ()) if isinstance(spec, Mapping) else ())
            if isinstance(reward, Mapping)
        )
        combat_stages = sum(
            bool(stage.get("combat_encounters"))
            for stage in (spec.get("stage_requirements", ()) if isinstance(spec, Mapping) else ())
            if isinstance(stage, Mapping)
        )
        rows.append(
            {
                "handler_key": "quest",
                "action_id": str(quest_id),
                "mode": "exempt",
                "source_status": "not_applicable",
                "source_row": str(spec.get("source", "")) if isinstance(spec, Mapping) else "",
                "source_reason": "finite quest-stage progression; completion XP is non-repeatable",
                "includes": rewards,
                "multiplier_behavior": "one collapsed stage per eligible review; never multiplied",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "same quest handler",
                "profile": None,
                "condition": f"{combat_stages} collapsed quest-combat stage(s)" if combat_stages else "",
                "route_kind": "quest",
            }
        )

    rows.extend(
        [
            {
                "handler_key": "summoning",
                "action_id": "attached:winter_storage",
                "mode": "passthrough",
                "source_status": "sourced",
                "source_row": "Pack Yak Winter Storage",
                "source_reason": "attached modifier owned by the host foreground review",
                "includes": ("one carried scroll", "12 special points", "4.8 Summoning XP"),
                "multiplier_behavior": "at most once per host kernel step",
                "undo_boundary": "same host answered-card transaction",
                "flag_off_behavior": "same carried-overlay modifier",
                "profile": None,
                "condition": "configured full-pack bank boundary",
                "route_kind": "attached",
            },
            {
                "handler_key": "farming",
                "action_id": "queued_background_simulation",
                "mode": "exempt",
                "source_status": "not_applicable",
                "source_row": "",
                "source_reason": "answered-card background clock and explicit queue preemption",
                "includes": ("growth clock", "farm queue"),
                "multiplier_behavior": "one queue/world step; never foreground-multiplied",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "same Farming simulation",
                "profile": None,
                "condition": "",
                "route_kind": "background",
            },
            {
                "handler_key": "slayer",
                "action_id": "future_attachment",
                "mode": "future_attachment",
                "source_status": "not_implemented",
                "source_row": "",
                "source_reason": "future Slayer XP must inherit the admitted ordinary Combat transaction",
                "includes": (),
                "multiplier_behavior": "inherits 6 * M combat ticks",
                "undo_boundary": "same combat review transaction",
                "flag_off_behavior": "must declare before handler registration",
                "profile": None,
                "condition": "",
                "route_kind": "planned",
            },
            {
                "handler_key": "dungeoneering",
                "action_id": "future_attachment",
                "mode": "future_attachment",
                "source_status": "not_implemented",
                "source_row": "",
                "source_reason": "future floor actions must declare cadence before handler registration",
                "includes": (),
                "multiplier_behavior": "must be settled with the implementation",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "must declare before handler registration",
                "profile": None,
                "condition": "",
                "route_kind": "planned",
            },
        ]
    )
    return rows


def validate_cadence_coverage_pure(
    implemented_handler_keys: Iterable[str],
) -> dict[str, Any]:
    """Fail closed when dispatch gains a handler or a route is omitted."""

    implemented = frozenset(str(key) for key in implemented_handler_keys)
    missing_handlers = sorted(implemented - CADENCE_DECLARED_HANDLER_KEYS)
    stale_handlers = sorted(CADENCE_DECLARED_HANDLER_KEYS - implemented)
    if missing_handlers or stale_handlers:
        raise ValueError(
            f"cadence handler coverage mismatch: missing={missing_handlers}, stale={stale_handlers}"
        )

    rows = cadence_coverage_rows_pure()
    actual = Counter((row["handler_key"], row["action_id"]) for row in rows)
    duplicates = sorted(key for key, count in actual.items() if count != 1)
    expected = {
        (handler_key, str(action_id))
        for handler_key, table in FOREGROUND_ROUTE_TABLES.items()
        for action_id in table
    }
    expected.update(("utility", str(action_id)) for action_id in UTILITY_ACTIVITY_DATA)
    expected.update(("quest", str(action_id)) for action_id in QUEST_DATA)
    missing_routes = sorted(expected - set(actual))
    invalid_rows = []
    for row in rows:
        mode = str(row.get("mode", ""))
        source_status = str(row.get("source_status", ""))
        source_row = str(row.get("source_row", ""))
        source_reason = str(row.get("source_reason", ""))
        if source_status == "source_blocked" and not source_reason:
            invalid_rows.append(
                (row["handler_key"], row["action_id"], "blocked without reason")
            )
        if mode == "rate_limited" and (
            source_status != "sourced"
            or not source_row
            or not isinstance(row.get("profile"), Mapping)
        ):
            invalid_rows.append(
                (
                    row["handler_key"],
                    row["action_id"],
                    "live rate lacks sourced profile",
                )
            )
        if mode == "source_blocked" and source_status != "source_blocked":
            invalid_rows.append(
                (
                    row["handler_key"],
                    row["action_id"],
                    "blocked mode/status mismatch",
                )
            )
    if duplicates or missing_routes or invalid_rows:
        raise ValueError(
            "cadence route coverage mismatch: "
            f"duplicates={duplicates}, missing={missing_routes}, invalid={invalid_rows}"
        )
    return {
        "handlers": len(implemented),
        "foreground_routes": len(expected),
        "total_rows": len(rows),
        "modes": dict(Counter(str(row["mode"]) for row in rows)),
    }
