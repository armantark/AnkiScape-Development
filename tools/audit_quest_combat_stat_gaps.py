#!/usr/bin/env python3
"""Classify quest combat encounters that still lack resolver-ready NPC stats."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic_pure.logic_pure import quest_combat_encounter_has_stats_pure
from ankiscape.data.quest_data import QUESTS, QuestCombatEncounter, QuestDefinition, QuestStageRequirement
from tools import build_pre_eoc_quest_catalog as catalog_builder
from tools.combat.quest_stat_sources import reviewed_source


@dataclass(frozen=True)
class CombatGap:
    quest_id: str
    quest_name: str
    stage: int
    display_name: str
    level: int
    quantity: int
    source_text: str
    source: str


def statless_combat_gaps(quests: Sequence[QuestDefinition] = QUESTS) -> Tuple[CombatGap, ...]:
    gaps: List[CombatGap] = []
    for quest in quests:
        for requirement in quest.stage_requirements:
            gaps.extend(_statless_gaps_for_requirement(quest, requirement))
    return tuple(gaps)


def _statless_gaps_for_requirement(
    quest: QuestDefinition,
    requirement: QuestStageRequirement,
) -> Iterable[CombatGap]:
    for encounter in requirement.combat_encounters:
        if quest_combat_encounter_has_stats_pure(_encounter_mapping(encounter)):
            continue
        yield _gap_from_encounter(quest, requirement, encounter)


def _encounter_mapping(encounter: QuestCombatEncounter) -> Dict[str, object]:
    return {
        "encounter_id": encounter.encounter_id,
        "display_name": encounter.display_name,
        "level": encounter.level,
        "quantity": encounter.quantity,
        "source": encounter.source,
        "source_text": encounter.source_text,
        "npc_stats": dict(encounter.npc_stats),
        "npc_bonuses": dict(encounter.npc_bonuses),
        "npc_configs": dict(encounter.npc_configs),
        "npc_stats_source": encounter.npc_stats_source,
    }


def _gap_from_encounter(
    quest: QuestDefinition,
    requirement: QuestStageRequirement,
    encounter: QuestCombatEncounter,
) -> CombatGap:
    return CombatGap(
        quest_id=quest.id,
        quest_name=quest.display_name,
        stage=requirement.stage,
        display_name=encounter.display_name,
        level=encounter.level,
        quantity=encounter.quantity,
        source_text=encounter.source_text,
        source=encounter.source,
    )


def darkan_candidate_groups() -> Dict[Tuple[str, int], Tuple[Tuple[str, str, str], ...]]:
    by_id, levels_by_name = catalog_builder._load_darkan_npc_list()
    rows: Dict[Tuple[str, int], List[Tuple[str, str, str]]] = {}
    for path in catalog_builder.DARKAN_NPC_COMBATDEF_DIR.rglob("*.json"):
        payload = catalog_builder._darkan_combat_payload(path)
        if not payload:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        signature = _combat_signature(payload)
        for display_name, level in catalog_builder._darkan_name_level_pairs(data, by_id, levels_by_name):
            key = (catalog_builder._normalize_npc_lookup_name(display_name), level)
            rows.setdefault(key, []).append((signature, display_name, str(path)))
    return {key: tuple(sorted(values)) for key, values in rows.items()}


def darkan_partial_metadata_groups() -> Dict[Tuple[str, int], Tuple[Tuple[str, str, str], ...]]:
    by_id, levels_by_name = catalog_builder._load_darkan_npc_list()
    rows: Dict[Tuple[str, int], List[Tuple[str, str, str]]] = {}
    for path in catalog_builder.DARKAN_NPC_COMBATDEF_DIR.rglob("*.json"):
        payload = _partial_darkan_metadata_payload(path)
        if not payload:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        signature = _combat_signature(payload)
        for display_name, level in catalog_builder._darkan_name_level_pairs(data, by_id, levels_by_name):
            key = (catalog_builder._normalize_npc_lookup_name(display_name), level)
            rows.setdefault(key, []).append((signature, display_name, str(path)))
    return {
        key: tuple(sorted(values))
        for key, values in rows.items()
        if len({row[0] for row in values}) == 1
    }


def _partial_darkan_metadata_payload(path: Path) -> Dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    full_payload = catalog_builder._darkan_combat_payload(path)
    if full_payload:
        return {}
    hitpoints = catalog_builder._parse_optional_int(data.get("hitpoints"))
    if not hitpoints:
        return {}

    stats: Dict[str, int] = {"hitpoints": hitpoints}
    levels = data.get("combatLevels")
    if isinstance(levels, Mapping):
        for source_key, stat_key in (
            ("ATTACK", "attack"),
            ("STRENGTH", "strength"),
            ("DEFENSE", "defence"),
            ("MAGE", "magic"),
            ("RANGE", "ranged"),
        ):
            value = catalog_builder._parse_optional_int(levels.get(source_key))
            if value is not None:
                stats[stat_key] = value

    configs: Dict[str, object] = {}
    for source_key, config_key in (("maxHit", "max_hit"), ("attackRange", "attack_range")):
        value = catalog_builder._parse_optional_int(data.get(source_key))
        if value is not None:
            configs[config_key] = value
    for source_key, config_key in (("attackStyle", "attack_style"), ("attackBonus", "attack_bonus")):
        value = data.get(source_key)
        if isinstance(value, str) and value:
            configs[config_key] = value.lower()
    aggressiveness = data.get("agressivenessType") or data.get("aggressivenessType")
    if isinstance(aggressiveness, str) and aggressiveness:
        configs["aggressiveness_type"] = aggressiveness.lower()
    return {"stats": stats, "configs": configs, "source": str(path)}


def _combat_signature(payload: Mapping[str, object]) -> str:
    return json.dumps(
        {
            "stats": payload.get("stats", {}),
            "configs": payload.get("configs", {}),
        },
        sort_keys=True,
    )


def classify_gap(
    gap: CombatGap,
    darkan_groups: Mapping[Tuple[str, int], Tuple[Tuple[str, str, str], ...]],
    partial_groups: Mapping[Tuple[str, int], Tuple[Tuple[str, str, str], ...]] | None = None,
) -> str:
    partial_groups = partial_groups or {}
    reviewed = reviewed_source(gap.quest_id, gap.display_name, gap.level)
    if reviewed and reviewed.get("source_rejection") == "disclosed_calibration":
        return "darkan_calibration_rejected"
    if gap.level <= 0:
        return "parser_or_variant_level"
    if catalog_builder._matching_local_npc_stats(gap.display_name, gap.level):
        return "local_exact_available"
    normalized = catalog_builder._normalize_npc_lookup_name(gap.display_name)
    exact = darkan_groups.get((normalized, gap.level), ())
    signatures = {row[0] for row in exact}
    if len(signatures) == 1 and exact:
        return "darkan_identical_available"
    if len(signatures) > 1:
        return "darkan_conflict"
    partial = partial_groups.get((normalized, gap.level), ())
    if partial:
        return _partial_metadata_classification(partial)
    if any(name == normalized for name, _level in set(darkan_groups) | set(partial_groups)):
        return "darkan_same_name_wrong_level"
    return "no_local_source_match"


def _partial_metadata_classification(partial: Tuple[Tuple[str, str, str], ...]) -> str:
    try:
        payload = json.loads(partial[0][0])
    except (IndexError, json.JSONDecodeError):
        return "darkan_incomplete_metadata"
    stats = payload.get("stats", {})
    if not isinstance(stats, Mapping):
        return "darkan_incomplete_metadata"
    stat_keys = {str(key) for key in stats}
    if stat_keys == {"hitpoints"}:
        return "darkan_hitpoints_only_metadata"
    configs = payload.get("configs", {})
    if not isinstance(configs, Mapping):
        configs = {}
    style = catalog_builder._combat_payload_attack_style(configs)
    required_stats = {
        "magic": {"hitpoints", "defence", "magic"},
        "ranged": {"hitpoints", "defence", "ranged"},
    }.get(style, {"hitpoints", "attack", "strength", "defence"})
    if required_stats - stat_keys or not catalog_builder._combat_payload_has_resolver_stats(stats, configs):
        return "darkan_missing_resolver_stats"
    return "darkan_incomplete_metadata"


def recorded_block_reason(gap: CombatGap) -> str:
    row = reviewed_source(gap.quest_id, gap.display_name, gap.level)
    if row and row["status"] == "source_blocked":
        return str(row["reason"])
    return ""


def print_summary(gaps: Sequence[CombatGap]) -> None:
    darkan_groups = darkan_candidate_groups()
    partial_groups = darkan_partial_metadata_groups()
    classifications = Counter(classify_gap(gap, darkan_groups, partial_groups) for gap in gaps)
    print(f"statless_combat_encounters: {len(gaps)}")
    print(f"affected_quests: {len({gap.quest_id for gap in gaps})}")
    print(f"gaps_without_recorded_reason: {sum(not recorded_block_reason(gap) for gap in gaps)}")
    print("classifications:")
    for key in sorted(classifications):
        print(f"  {key}: {classifications[key]}")
    print("gaps:")
    for gap in gaps:
        classification = classify_gap(gap, darkan_groups, partial_groups)
        print(
            "\t".join(
                (
                    classification,
                    gap.quest_id,
                    gap.quest_name,
                    str(gap.stage),
                    gap.display_name,
                    str(gap.level),
                    str(gap.quantity),
                    gap.source_text,
                    gap.source,
                    recorded_block_reason(gap) or "UNRECORDED: review source evidence before adding stats",
                )
            )
        )


def main() -> None:
    print_summary(statless_combat_gaps())


if __name__ == "__main__":
    main()
