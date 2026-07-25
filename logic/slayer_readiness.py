"""Pure completeness checks for source-declared Slayer master pools."""

from __future__ import annotations

from typing import Any, Mapping, Tuple

from ..data.slayer_data import SLAYER_MASTERS_BY_ID, SlayerAssignmentFamily


def slayer_family_readiness_blockers_pure(
    family: SlayerAssignmentFamily,
    enemy_data: Mapping[str, Mapping[str, Any]],
) -> Tuple[str, ...]:
    candidates = [
        enemy_data[target_id]
        for target_id in family.target_ids
        if target_id in enemy_data
    ]
    prefix = f"{family.id}:"
    if not candidates:
        return (prefix + "combat_target",)

    slayer_candidates = []
    for candidate in candidates:
        try:
            slayer_xp = float(candidate.get("slayer_xp", 0.0) or 0.0)
        except (TypeError, ValueError):
            slayer_xp = 0.0
        if slayer_xp > 0:
            slayer_candidates.append(candidate)
    if not slayer_candidates:
        return (prefix + "slayer_xp",)

    blockers = []
    for feature in family.readiness_features:
        if not any(candidate.get(feature) for candidate in slayer_candidates):
            blockers.append(prefix + feature)
    return tuple(blockers)


def slayer_master_readiness_pure(
    master_id: str,
    enemy_data: Mapping[str, Mapping[str, Any]],
) -> dict:
    master = SLAYER_MASTERS_BY_ID.get(master_id)
    if master is None:
        return {
            "master_id": master_id,
            "known": False,
            "certified": False,
            "runtime_enabled": False,
            "family_count": 0,
            "ready_family_count": 0,
            "blockers": ("master:unknown",),
        }

    blockers = tuple(
        blocker
        for family in master.assignments
        for blocker in slayer_family_readiness_blockers_pure(family, enemy_data)
    )
    blocked_families = {blocker.split(":", 1)[0] for blocker in blockers}
    return {
        "master_id": master.id,
        "known": True,
        "certified": not blockers,
        "runtime_enabled": master.runtime_enabled,
        "family_count": len(master.assignments),
        "ready_family_count": len(master.assignments) - len(blocked_families),
        "blockers": blockers,
    }


def slayer_catalog_integrity_issues_pure(
    enemy_data: Mapping[str, Mapping[str, Any]],
) -> Tuple[str, ...]:
    issues = []
    for master in SLAYER_MASTERS_BY_ID.values():
        if not master.assignments:
            issues.append(f"{master.id}:empty_pool")
            continue
        family_ids = [assignment.id for assignment in master.assignments]
        if len(family_ids) != len(set(family_ids)):
            issues.append(f"{master.id}:duplicate_family")
        if any(
            assignment.weight <= 0
            or assignment.count_min <= 0
            or assignment.count_max < assignment.count_min
            for assignment in master.assignments
        ):
            issues.append(f"{master.id}:invalid_roll_row")
        weight_total = sum(assignment.weight for assignment in master.assignments)
        if (
            master.expected_weight_total > 0
            and weight_total != master.expected_weight_total
        ):
            issues.append(
                f"{master.id}:weight_total:{weight_total}"
                f"!=expected:{master.expected_weight_total}"
            )

        readiness = slayer_master_readiness_pure(master.id, enemy_data)
        if master.runtime_enabled and not readiness["certified"]:
            issues.append(f"{master.id}:enabled_with_blockers")
        if not master.runtime_enabled and readiness["certified"]:
            issues.append(f"{master.id}:certified_but_hidden")
    return tuple(issues)
