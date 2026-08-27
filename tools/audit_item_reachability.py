#!/usr/bin/env python3
"""Audit whether live AnkiScape action inputs have an acquisition route.

This is deliberately a reachability audit, not a claim that every route has
full historical fidelity. It treats live shops, Combat drops, quest-granted
items and rewards, gathering outputs, and zero-input actions as source nodes,
then closes over the current action graph. The JSON output is stable enough for
tests and later completion-audit tooling.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _names(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value} if value else set()
    if isinstance(value, Mapping):
        return {str(name) for name in value if isinstance(name, str) and name}
    if isinstance(value, (tuple, list, set)):
        names: set[str] = set()
        for entry in value:
            if isinstance(entry, str):
                names.add(entry)
            elif isinstance(entry, Mapping):
                names.update(_names(entry.get("item") or entry.get("item_name") or entry.get("output_item")))
            elif isinstance(entry, (tuple, list)) and entry and isinstance(entry[0], str):
                names.add(entry[0])
        return names
    return set()


def _outputs(spec: Mapping[str, Any]) -> set[str]:
    outputs = _names(spec.get("outputs")) | _names(spec.get("byproducts"))
    for table in spec.get("secondary_drop_tables", ()) or ():
        if isinstance(table, Mapping):
            outputs |= _names(table.get("outputs"))
    outputs |= _names(spec.get("output_item")) | _names(spec.get("alternate_output_item"))
    outputs |= _names(spec.get("byproduct_item"))
    for fish in spec.get("fish", ()) or ():
        if isinstance(fish, Mapping):
            outputs |= _names(fish.get("output_item"))
    for weighted in spec.get("weighted_outputs", ()) or ():
        if isinstance(weighted, Mapping):
            outputs |= _names(weighted.get("item") or weighted.get("output_item"))
        elif isinstance(weighted, (tuple, list)) and weighted and isinstance(weighted[0], str):
            outputs.add(weighted[0])
    return outputs


def _requirements(spec: Mapping[str, Any]) -> tuple[set[str], tuple[set[str], ...]]:
    required = (
        _names(spec.get("requirements"))
        | _names(spec.get("required_items"))
        | _names(spec.get("tools"))
        | _names(spec.get("rune_cost"))
    )
    alternatives: list[set[str]] = []
    material_options = spec.get("material_options", {}) or {}
    if isinstance(material_options, Mapping):
        for material, options in material_options.items():
            option_names = _names(options)
            if material in required and option_names:
                required.remove(material)
                alternatives.append(option_names)
    for option_group in spec.get("required_item_options", ()) or ():
        option_names = _names(option_group)
        if option_names:
            alternatives.append(option_names)
    any_requirements = _names(spec.get("any_requirements"))
    if any_requirements:
        alternatives.append(any_requirements)
    essence = _names(spec.get("essence_items"))
    if essence:
        alternatives.append(essence)
    bait = _names(spec.get("bait_options"))
    if bait:
        alternatives.append(bait)
    reachability_inputs = _names(spec.get("reachability_inputs"))
    if reachability_inputs:
        alternatives.append(reachability_inputs)
    return required, tuple(alternatives)


def _drop_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in {"item", "item_name", "output_item"}:
                names |= _names(child)
            else:
                names |= _drop_names(child)
    elif isinstance(value, (tuple, list, set)):
        if value and isinstance(value, (tuple, list)) and isinstance(value[0], str):
            names.add(value[0])
        else:
            for child in value:
                names |= _drop_names(child)
    return names


def _quest_gate_reachable(
    quest_id: str,
    gate_state: str,
    completable_quests: set[str],
    startable_quests: set[str],
) -> bool:
    eligible_quests = (
        startable_quests if gate_state == "started" else completable_quests
    )
    return quest_id in eligible_quests


def _combat_drop_gate_reachable(
    enemy_id: str,
    enemy: Mapping[str, Any],
    player_data: Mapping[str, Any],
) -> bool:
    from ankiscape.core.constants import EQUIPMENT_DATA
    from ankiscape.logic_pure.logic_pure import (
        COMBAT_MAGIC_SPELL_DATA,
        DEFAULT_COMBAT_SPELL,
        combat_finisher_state_pure,
        combat_target_locked_reasons_pure,
    )

    enemy_data = {enemy_id: enemy}
    finisher = enemy.get("finisher")

    def loadout_reachable(candidate: Mapping[str, Any]) -> bool:
        if combat_target_locked_reasons_pure(
            candidate,
            enemy_id,
            enemy_data,
            equipment_data=EQUIPMENT_DATA,
        ):
            return False
        if not isinstance(finisher, Mapping):
            return True
        candidate = dict(candidate)
        candidate["combat_encounter"] = {
            "target_id": enemy_id,
            "enemy_lifepoints": max(
                1,
                int(finisher.get("threshold_lifepoints", 1) or 1),
            ),
        }
        return bool(
            combat_finisher_state_pure(candidate, enemy_id, enemy_data)["available"]
        )

    if loadout_reachable(player_data):
        return True

    restriction = enemy.get("restricted_weapon")
    restriction = restriction if isinstance(restriction, Mapping) else {}
    allowed_classes = set(enemy.get("allowed_combat_classes", ()) or ())
    inventory = player_data.get("inventory", {}) or {}
    reachable_items = set(inventory) if isinstance(inventory, Mapping) else set()
    base_equipment = dict(player_data.get("equipment", {}) or {})

    if restriction.get("ranged_ammunition") or "ranged" in allowed_classes:
        for weapon_name in sorted(reachable_items):
            equipment_spec = EQUIPMENT_DATA.get(weapon_name)
            combat_skill = (
                equipment_spec.get("combat_skill")
                if isinstance(equipment_spec, Mapping)
                else getattr(equipment_spec, "combat_skill", None)
            )
            if combat_skill != "ranged":
                continue
            candidate = dict(player_data)
            candidate["equipment"] = {
                **base_equipment,
                "weapon": weapon_name,
            }
            if loadout_reachable(candidate):
                return True

    magic_spell_ids = tuple(restriction.get("magic_spells", ()) or ())
    if not magic_spell_ids and "magic" in allowed_classes:
        magic_spell_ids = (DEFAULT_COMBAT_SPELL,)
    for spell_id in magic_spell_ids:
        spell_spec = COMBAT_MAGIC_SPELL_DATA.get(spell_id, {})
        required_weapon = str(spell_spec.get("required_weapon", "") or "")
        if required_weapon:
            weapon_names = (required_weapon,) if required_weapon in reachable_items else ()
        else:
            weapon_names = tuple(
                weapon_name
                for weapon_name in sorted(reachable_items)
                if (
                    EQUIPMENT_DATA[weapon_name].get("combat_skill")
                    if isinstance(EQUIPMENT_DATA.get(weapon_name), Mapping)
                    else getattr(EQUIPMENT_DATA.get(weapon_name), "combat_skill", None)
                )
                == "magic"
            )
        for weapon_name in weapon_names:
            candidate = dict(player_data)
            candidate["equipment"] = {
                **base_equipment,
                "weapon": weapon_name,
            }
            candidate["current_combat_spell"] = spell_id
            if loadout_reachable(candidate):
                return True
    return False


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)


def _close_actions(
    actions: Iterable[Mapping[str, Any]],
    seed_sources: Mapping[str, set[str]],
    *,
    active_action_ids: set[str] | None = None,
) -> tuple[set[str], dict[str, str], list[Mapping[str, Any]]]:
    reachable = set(seed_sources)
    route = {item: sorted(sources)[0] for item, sources in seed_sources.items()}
    unresolved = list(actions)
    changed = True
    while changed:
        changed = False
        remaining: list[Mapping[str, Any]] = []
        for action in unresolved:
            if (
                active_action_ids is not None
                and action.get("is_accessible")
                and action["id"] not in active_action_ids
            ):
                remaining.append(action)
                continue
            required_ok = action["required"].issubset(reachable)
            alternatives_ok = all(
                bool(group & reachable) for group in action["alternatives"]
            )
            if required_ok and alternatives_ok:
                for item in action["outputs"]:
                    if item not in reachable:
                        reachable.add(item)
                        route[item] = action["id"]
                        changed = True
            else:
                remaining.append(action)
        unresolved = remaining
    return reachable, route, unresolved


def _item_counts(value: Any) -> dict[str, int]:
    if isinstance(value, Mapping):
        return {
            str(name): max(1, int(amount or 1))
            for name, amount in value.items()
            if isinstance(name, str) and name
        }
    counts: dict[str, int] = {}
    if not isinstance(value, (tuple, list, set)):
        return counts
    for row in value:
        if isinstance(row, Mapping):
            name = row.get("item") or row.get("item_name") or row.get("display_name")
            amount = row.get("quantity", row.get("amount", 1))
        elif isinstance(row, (tuple, list)) and row and isinstance(row[0], str):
            name = row[0]
            amount = row[1] if len(row) > 1 else 1
        else:
            continue
        if isinstance(name, str) and name:
            counts[name] = max(counts.get(name, 0), max(1, int(amount or 1)))
    return counts


def _claim_item_sources(
    claim_data: Mapping[str, Mapping[str, Any]],
    completable_quests: set[str],
    registered_items: set[str],
    maximum_skill_levels: Mapping[str, int],
    available_counts: Mapping[str, int],
    repeatable_items: set[str],
) -> tuple[dict[str, set[str]], dict[str, int]]:
    sources: dict[str, set[str]] = defaultdict(set)
    item_counts: dict[str, int] = defaultdict(int)
    for claim_id, claim in claim_data.items():
        required_quest = str(claim.get("required_quest", "") or "")
        if required_quest and required_quest not in completable_quests:
            continue
        if claim.get("required_diary_tier"):
            continue
        required_runecrafting_level = max(
            1,
            int(claim.get("required_runecrafting_level", 1) or 1),
        )
        if required_runecrafting_level > maximum_skill_levels.get("runecrafting", 0):
            continue
        required_tools = _item_counts(claim.get("required_tools"))
        if any(
            not _tool_reachable(tool_name, amount, available_counts, repeatable_items)
            for tool_name, amount in required_tools.items()
        ):
            continue

        claim_type = str(claim.get("claim_type", "item"))
        if claim_type == "skill_reward":
            skill_options = tuple(claim.get("skill_options", ()) or ())
            if len(skill_options) != 1 or float(claim.get("xp_amount", 0) or 0) <= 0:
                continue
            minimum_level = max(1, int(claim.get("minimum_level", 1) or 1))
            if minimum_level > maximum_skill_levels.get(str(skill_options[0]), 0):
                continue
            claim_items = _item_counts(claim.get("items"))
        elif claim_type == "item_bundle":
            claim_items = _item_counts(claim.get("items"))
        elif claim_type == "item":
            item_name = str(claim.get("item_name", claim_id) or claim_id)
            claim_items = {
                item_name: max(1, int(claim.get("quantity", 1) or 1)),
            }
        else:
            continue

        for item_name, amount in claim_items.items():
            if item_name not in registered_items:
                continue
            sources[item_name].add(f"claim:{claim_id}")
            item_counts[item_name] += amount
    return sources, dict(item_counts)


def _item_option_groups(value: Any) -> tuple[dict[str, int], ...]:
    if isinstance(value, Mapping):
        return (_item_counts(value),) if value else ()
    if not isinstance(value, (tuple, list, set)):
        return ()
    rows = tuple(value)
    if rows and all(isinstance(row, Mapping) for row in rows):
        options = {
            name: amount
            for row in rows
            for name, amount in _item_counts(row).items()
        }
        return (options,) if options else ()
    return tuple(
        filter(
            None,
            (
                {
                    name: amount
                    for alternative in row
                    for name, amount in _item_counts(
                        tuple(alternative.items())
                        if isinstance(alternative, Mapping)
                        else (alternative,)
                    ).items()
                }
                for row in rows
                if isinstance(row, (tuple, list, set))
            ),
        )
    )


def _quantity_available(
    item_name: str,
    amount: int,
    available_counts: Mapping[str, int],
    repeatable_items: set[str],
) -> bool:
    return item_name in repeatable_items or available_counts.get(item_name, 0) >= amount


def _tool_reachable(
    tool_name: str,
    amount: int,
    available_counts: Mapping[str, int],
    repeatable_items: set[str],
) -> bool:
    if _quantity_available(tool_name, amount, available_counts, repeatable_items):
        return True
    lowered = tool_name.lower()
    if lowered == "pickaxe":
        return any(
            item.lower().endswith("pickaxe")
            and _quantity_available(item, amount, available_counts, repeatable_items)
            for item in available_counts
        )
    if lowered in {"hatchet", "axe"}:
        return any(
            (item.lower().endswith("hatchet") or item.lower().endswith(" axe"))
            and _quantity_available(item, amount, available_counts, repeatable_items)
            for item in available_counts
        )
    return False


def _stage_satisfiability(
    stage: Mapping[str, Any],
    available_counts: Mapping[str, int],
    repeatable_items: set[str],
    emitted_actions: set[str],
    available_routes: set[str],
    combat_encounter_satisfiable: Callable[[Mapping[str, Any]], bool],
) -> dict[str, Any]:
    required_items = _item_counts(stage.get("required_inventory"))
    consumed_inventory = (
        stage.get("consumed_inventory"),
        None,
    )[bool(stage.get("repeatable_until_consumed"))]
    for item_name, amount in _item_counts(consumed_inventory).items():
        required_items[item_name] = max(required_items.get(item_name, 0), amount)
    required_tools = _item_counts(stage.get("required_tools"))
    required_actions = _names(stage.get("required_actions"))
    required_routes = _names(stage.get("required_routes"))
    required_option_groups = _item_option_groups(stage.get("required_inventory_options"))
    consumed_option_groups = _item_option_groups(stage.get("consumed_inventory_options"))
    blocked_encounters = []
    for encounter in stage.get("combat_encounters", ()) or ():
        if isinstance(encounter, Mapping) and not combat_encounter_satisfiable(encounter):
            blocked_encounters.append(str(encounter.get("encounter_id", "unknown")))
    missing_options = [
        options
        for options, tool_semantics in (
            *((options, True) for options in required_option_groups),
            *((options, False) for options in consumed_option_groups),
        )
        if not any(
            _tool_reachable(item_name, amount, available_counts, repeatable_items)
            if tool_semantics
            else _quantity_available(item_name, amount, available_counts, repeatable_items)
            for item_name, amount in options.items()
        )
    ]
    return {
        "missing_required_items": {
            item_name: amount
            for item_name, amount in required_items.items()
            if not _quantity_available(item_name, amount, available_counts, repeatable_items)
        },
        "missing_required_tools": {
            tool_name: amount
            for tool_name, amount in required_tools.items()
            if not _tool_reachable(tool_name, amount, available_counts, repeatable_items)
        },
        "missing_required_actions": required_actions - emitted_actions,
        "missing_required_routes": required_routes - available_routes,
        "missing_item_alternatives": missing_options,
        "blocked_combat_encounters": blocked_encounters,
    }


def _blocked_diagnostic_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row["quest_id"],
        row["stage"],
        row["variant"],
        tuple(row["products"]),
        tuple(row["blocked_combat_encounters"]),
        tuple(row["missing_required_actions"]),
        tuple(row["missing_required_routes"]),
        tuple(row["missing_required_items"]),
        tuple(row["missing_required_tools"]),
        tuple(tuple(group) for group in row["missing_item_alternatives"]),
    )


def _quest_stage_sources(
    quest_data: Mapping[str, Mapping[str, Any]],
    registered_items: set[str],
    *,
    reachable_items: set[str] | None = None,
    repeatable_items: set[str] | None = None,
    finite_item_counts: Mapping[str, int] | None = None,
    selected_variants: Mapping[str, str] | None = None,
    eligible_quests: set[str] | None = None,
    combat_encounter_satisfiable: Callable[[Mapping[str, Any]], bool] | None = None,
    quest_progress_out: dict[str, int] | None = None,
) -> tuple[dict[str, set[str]], list[dict[str, Any]], set[str]]:
    sources: dict[str, set[str]] = defaultdict(set)
    blocked: list[dict[str, Any]] = []
    blocked_keys: set[tuple[Any, ...]] = set()
    action_completable: set[str] = set()
    reachable_items = set(reachable_items or ())
    repeatable_items = set(repeatable_items or ())
    finite_item_counts = dict(finite_item_counts or {})
    selected_variants = dict(selected_variants or {})
    available_base_counts = {
        item: max(1, finite_item_counts.get(item, 1))
        for item in reachable_items
    }
    combat_encounter_satisfiable = combat_encounter_satisfiable or (lambda _encounter: True)
    for quest_id, quest in quest_data.items():
        indexed_rows = [
            (index, row)
            for index, row in enumerate(quest.get("stage_requirements", ()) or ())
            if isinstance(row, Mapping)
        ]
        shared_rows = [(index, row) for index, row in indexed_rows if not row.get("variant")]
        rows_by_variant: dict[str, list[tuple[int, Mapping[str, Any]]]] = defaultdict(list)
        for index, row in indexed_rows:
            variant = str(row.get("variant", "") or "")
            if variant:
                rows_by_variant[variant].append((index, row))
        branches = sorted(rows_by_variant) if rows_by_variant else [""]
        if quest_id in selected_variants:
            branches = [selected_variants[quest_id]]
        choice_stages_by_route = {
            route: int(choice.get("stage", 0) or 0)
            for choice in quest.get("choices", ()) or ()
            if isinstance(choice, Mapping)
            for option in choice.get("options", ()) or ()
            if isinstance(option, Mapping)
            for route in _names(option.get("route_id"))
        }
        branch_rows_by_variant = {
            variant: sorted(
                shared_rows + rows_by_variant.get(variant, []),
                key=lambda indexed: (
                    int(indexed[1].get("stage", 0))
                    if str(indexed[1].get("stage", 0)).isdigit()
                    else 0,
                    indexed[0],
                ),
            )
            for variant in branches
        }
        branch_routes = {
            variant: {
                route
                for _index, row in rows_by_variant.get(variant, [])
                for route in _names(row.get("required_routes"))
                if route in choice_stages_by_route
            }
            for variant in branches
        }
        quest_completable = False
        first_blocked_without_products: dict[str, Any] | None = None
        branch_source_sets: list[dict[str, set[str]]] = []
        completed_branch_source_sets: list[dict[str, set[str]]] = []
        branch_progresses: list[int] = []
        for variant in branches:
            branch_rows = branch_rows_by_variant[variant]
            available_counts = dict(available_base_counts)
            for item_name, amount in _item_counts(quest.get("start_inventory")).items():
                available_counts[item_name] = available_counts.get(item_name, 0) + amount
            emitted_actions: set[str] = set()
            available_routes: set[str] = set()
            selected_routes = branch_routes[variant]
            branch_sources: dict[str, set[str]] = defaultdict(set)
            branch_blocked = False
            branch_progress = 1
            stage_ids = list(dict.fromkeys(row.get("stage", "unknown") for _index, row in branch_rows))
            for stage_id in stage_ids:
                numeric_stage = int(stage_id) if str(stage_id).isdigit() else 0
                branch_progress = max(branch_progress, numeric_stage)
                available_routes.update(
                    route
                    for route in selected_routes
                    if choice_stages_by_route[route] == numeric_stage
                )
                stage_rows = [row for _index, row in branch_rows if row.get("stage", "unknown") == stage_id]
                gates = [
                    _stage_satisfiability(
                        stage,
                        available_counts,
                        repeatable_items,
                        emitted_actions,
                        available_routes,
                        combat_encounter_satisfiable,
                    )
                    for stage in stage_rows
                ]
                stage_blocked = any(any(gate.values()) for gate in gates)
                products_all = set().union(*(_names(stage.get("produced_inventory")) for stage in stage_rows))
                products = products_all & registered_items
                combat_products_all: dict[str, set[str]] = {}
                for stage in stage_rows:
                    for encounter in stage.get("combat_encounters", ()) or ():
                        if not isinstance(encounter, Mapping):
                            continue
                        encounter_id = str(encounter.get("encounter_id", "unknown"))
                        combat_products_all[encounter_id] = _names(encounter.get("guaranteed_drops"))
                combat_products = {
                    encounter_id: items & registered_items
                    for encounter_id, items in combat_products_all.items()
                    if items & registered_items
                }
                if stage_blocked:
                    blocked_encounters = {
                        encounter_id
                        for gate in gates
                        for encounter_id in gate["blocked_combat_encounters"]
                    }
                    diagnostic_variant = variant if any(stage.get("variant") for stage in stage_rows) else ""
                    diagnostic = {
                        "quest_id": quest_id,
                        "quest": str(quest.get("display_name", quest_id)),
                        "stage": stage_id,
                        "variant": diagnostic_variant,
                        "products": sorted(products),
                        "combat_products": {
                            encounter_id: sorted(items)
                            for encounter_id, items in sorted(combat_products.items())
                        },
                        "blocked_combat_products": {
                            encounter_id: sorted(combat_products.get(encounter_id, ()))
                            for encounter_id in sorted(blocked_encounters)
                            if combat_products.get(encounter_id)
                        },
                        "required_actions": sorted(
                            set().union(*(_names(stage.get("required_actions")) for stage in stage_rows))
                        ),
                        "missing_required_actions": sorted(
                            set().union(*(gate["missing_required_actions"] for gate in gates))
                        ),
                        "missing_required_routes": sorted(
                            set().union(*(gate["missing_required_routes"] for gate in gates))
                        ),
                        "missing_required_items": sorted(
                            set().union(*(gate["missing_required_items"] for gate in gates))
                        ),
                        "missing_required_tools": sorted(
                            set().union(*(gate["missing_required_tools"] for gate in gates))
                        ),
                        "missing_item_alternatives": [
                            sorted(group)
                            for gate in gates
                            for group in gate["missing_item_alternatives"]
                        ],
                        "blocked_combat_encounters": sorted(blocked_encounters),
                    }
                    diagnostic_key = _blocked_diagnostic_key(diagnostic)
                    if (products or combat_products) and diagnostic_key not in blocked_keys:
                        blocked.append(diagnostic)
                        blocked_keys.add(diagnostic_key)
                    elif first_blocked_without_products is None:
                        first_blocked_without_products = diagnostic
                    branch_blocked = True
                    break
                if eligible_quests is None or quest_id in eligible_quests:
                    for item in products:
                        branch_sources[item].add(f"quest-stage:{quest_id}:{stage_id}")
                    for encounter_id, items in combat_products.items():
                        for item in items:
                            branch_sources[item].add(f"quest-combat:{quest_id}:{encounter_id}")
                for stage in stage_rows:
                    for item_name, amount in _item_counts(stage.get("consumed_inventory")).items():
                        if item_name not in repeatable_items:
                            available_counts[item_name] = max(0, available_counts.get(item_name, 0) - amount)
                    for options in _item_option_groups(stage.get("consumed_inventory_options")):
                        for item_name, amount in options.items():
                            if _quantity_available(item_name, amount, available_counts, repeatable_items):
                                if item_name not in repeatable_items:
                                    available_counts[item_name] = max(0, available_counts.get(item_name, 0) - amount)
                                break
                    for item_name, amount in _item_counts(stage.get("produced_inventory")).items():
                        available_counts[item_name] = available_counts.get(item_name, 0) + amount
                    emitted_actions.update(_names(stage.get("auto_actions")))
                for items in combat_products_all.values():
                    for item_name in items:
                        available_counts[item_name] = available_counts.get(item_name, 0) + 1
            if not branch_blocked:
                quest_completable = True
                completed_branch_source_sets.append(branch_sources)
            branch_source_sets.append(branch_sources)
            branch_progresses.append(branch_progress)
        if quest_progress_out is not None and (
            eligible_quests is None or quest_id in eligible_quests
        ):
            quest_progress_out[quest_id] = max(branch_progresses, default=0)
        if quest_completable:
            action_completable.add(quest_id)
        source_sets = completed_branch_source_sets or branch_source_sets
        common_items = set.intersection(*(set(branch_sources) for branch_sources in source_sets))
        for item in common_items:
            for branch_sources in source_sets:
                sources[item].update(branch_sources[item])
        if (
            not quest_completable
            and not any(row["quest_id"] == quest_id for row in blocked)
            and first_blocked_without_products
        ):
            blocked.append(first_blocked_without_products)
    return sources, blocked, action_completable


def _close_quest_reachability(
    actions: Iterable[Mapping[str, Any]],
    seed_sources: dict[str, set[str]],
    seed_item_counts: dict[str, int],
    repeatable_seed_items: set[str],
    quest_data: Mapping[str, Mapping[str, Any]],
    registered_items: set[str],
    combat_encounter_satisfiable: Callable[[Mapping[str, Any]], bool],
    *,
    claim_data: Mapping[str, Mapping[str, Any]] | None = None,
    maximum_skill_levels: Mapping[str, int] | None = None,
    conditional_seed_sources: Iterable[Mapping[str, Any]] = (),
    scenario_sources_out: list[dict[str, set[str]]] | None = None,
    scenario_action_ids_out: list[set[str]] | None = None,
) -> tuple[list[dict[str, Any]], set[str], set[str]]:
    variant_ids = {
        quest_id: tuple(sorted({
            str(row.get("variant") or "")
            for row in quest.get("stage_requirements", ()) or ()
            if isinstance(row, Mapping) and row.get("variant")
        }))
        for quest_id, quest in quest_data.items()
    }
    branch_quests = tuple(quest_id for quest_id, variants in variant_ids.items() if variants)
    claim_data = claim_data or {}
    maximum_skill_levels = maximum_skill_levels or {}
    actions = tuple(actions)
    conditional_actions = tuple(
        action for action in actions if callable(action.get("is_accessible"))
    )
    conditional_seed_sources = tuple(conditional_seed_sources)
    scenario_results = []
    for selected in itertools.product(*(variant_ids[quest_id] for quest_id in branch_quests)):
        selected_variants = dict(zip(branch_quests, selected))
        scenario_sources = {item: set(sources) for item, sources in seed_sources.items()}
        scenario_seed_item_counts = dict(seed_item_counts)
        scenario_repeatable_seed_items = set(repeatable_seed_items)
        active_conditional_sources: set[str] = set()
        active_action_ids: set[str] = set()
        previous_state: tuple[
            frozenset[str],
            frozenset[str],
            frozenset[str],
            frozenset[tuple[str, int]],
            frozenset[str],
            frozenset[str],
            frozenset[tuple[str, int]],
        ] | None = None
        blocked: list[dict[str, Any]] = []
        completable: set[str] = set()
        startable: set[str] = set()
        claim_item_counts: dict[str, int] = {}
        while True:
            reachable_items, route, _unresolved = _close_actions(
                actions,
                scenario_sources,
                active_action_ids=active_action_ids,
            )
            repeatable_items = scenario_repeatable_seed_items | {
                item_name
                for item_name, source in route.items()
                if not source.startswith(
                    ("quest:", "quest-start:", "quest-stage:", "quest-combat:", "claim:")
                )
            }
            finite_item_counts = dict(scenario_seed_item_counts)
            for item_name, amount in claim_item_counts.items():
                finite_item_counts[item_name] = finite_item_counts.get(item_name, 0) + amount
            _, blocked, stage_completable = _quest_stage_sources(
                quest_data,
                registered_items,
                reachable_items=reachable_items,
                repeatable_items=repeatable_items,
                finite_item_counts=finite_item_counts,
                selected_variants=selected_variants,
                eligible_quests=set(),
                combat_encounter_satisfiable=combat_encounter_satisfiable,
            )
            completable, startable = _quest_completion_sets(quest_data, stage_completable)
            quest_progress: dict[str, int] = {}
            quest_stage_sources, _, _ = _quest_stage_sources(
                quest_data,
                registered_items,
                reachable_items=reachable_items,
                repeatable_items=repeatable_items,
                finite_item_counts=finite_item_counts,
                selected_variants=selected_variants,
                eligible_quests=startable,
                combat_encounter_satisfiable=combat_encounter_satisfiable,
                quest_progress_out=quest_progress,
            )
            for quest_id in completable:
                quest = quest_data[quest_id]
                for item in _names(quest.get("rewards")) & registered_items:
                    scenario_sources.setdefault(item, set()).add(f"quest:{quest_id}")
            for quest_id in startable:
                quest = quest_data[quest_id]
                for item in _names(quest.get("start_inventory")) & registered_items:
                    scenario_sources.setdefault(item, set()).add(f"quest-start:{quest_id}")
            for item, sources in quest_stage_sources.items():
                scenario_sources.setdefault(item, set()).update(sources)
            for action in conditional_actions:
                action_id = str(action["id"])
                if action_id in active_action_ids or not action["is_accessible"](
                    completable,
                    startable,
                    reachable_items,
                    quest_progress,
                ):
                    continue
                active_action_ids.add(action_id)
            for source in conditional_seed_sources:
                source_id = str(source["id"])
                if source_id in active_conditional_sources or not source["is_accessible"](
                    completable,
                    startable,
                    reachable_items,
                    quest_progress,
                ):
                    continue
                active_conditional_sources.add(source_id)
                for item in source.get("items", ()):
                    scenario_sources.setdefault(str(item), set()).add(source_id)
                for item, amount in source.get("item_counts", {}).items():
                    scenario_seed_item_counts[str(item)] = (
                        scenario_seed_item_counts.get(str(item), 0) + int(amount)
                    )
                scenario_repeatable_seed_items.update(
                    str(item) for item in source.get("repeatable_items", ())
                )
            claim_sources, next_claim_item_counts = _claim_item_sources(
                claim_data,
                completable,
                registered_items,
                maximum_skill_levels,
                finite_item_counts,
                repeatable_items,
            )
            for item, sources in claim_sources.items():
                if item not in reachable_items:
                    scenario_sources.setdefault(item, set()).update(sources)
            state = (
                frozenset(scenario_sources),
                frozenset(completable),
                frozenset(startable),
                frozenset(next_claim_item_counts.items()),
                frozenset(active_conditional_sources),
                frozenset(active_action_ids),
                frozenset(quest_progress.items()),
            )
            claim_item_counts = next_claim_item_counts
            if state == previous_state:
                scenario_results.append(
                    (
                        scenario_sources,
                        blocked,
                        completable,
                        startable,
                        active_action_ids,
                    )
                )
                break
            previous_state = state

    if scenario_sources_out is not None:
        scenario_sources_out.extend(
            {item: set(item_sources) for item, item_sources in sources.items()}
            for sources, _blocked, _complete, _startable, _actions in scenario_results
        )
    if scenario_action_ids_out is not None:
        scenario_action_ids_out.extend(
            set(active_action_ids)
            for _sources, _blocked, _complete, _startable, active_action_ids in scenario_results
        )
    reachable_items = set.union(
        *(
            set(sources)
            for sources, _blocked, _complete, _startable, _actions in scenario_results
        )
    )
    for item in reachable_items:
        seed_sources.setdefault(item, set()).update(
            source
            for sources, _blocked, _complete, _startable, _actions in scenario_results
            for source in sources.get(item, ())
        )
    completable = set.union(
        *(
            set(complete)
            for _sources, _blocked, complete, _startable, _actions in scenario_results
        )
    )
    startable = set.union(
        *(
            set(startable)
            for _sources, _blocked, _complete, startable, _actions in scenario_results
        )
    )
    blocked_by_key = {}
    for _sources, rows, _complete, _startable, _actions in scenario_results:
        for row in rows:
            key = _blocked_diagnostic_key(row)
            blocked_by_key.setdefault(key, row)
    blocked = sorted(
        blocked_by_key.values(),
        key=lambda row: (row["quest_id"], int(row["stage"]) if str(row["stage"]).isdigit() else 0, row["variant"]),
    )
    return blocked, completable, startable


def _required_quest_ids(quest: Mapping[str, Any]) -> set[str]:
    return {
        str(row.get("quest_id", ""))
        for row in quest.get("required_quests", ()) or ()
        if isinstance(row, Mapping)
    }


def _quest_completion_sets(
    quest_data: Mapping[str, Mapping[str, Any]],
    action_completable: set[str],
) -> tuple[set[str], set[str]]:
    completed: set[str] = set()
    changed = True
    while changed:
        changed = False
        quest_points = sum(
            int(quest_data[quest_id].get("point_reward", 0) or 0)
            for quest_id in completed
        )
        for quest_id in action_completable - completed:
            quest = quest_data[quest_id]
            if (
                _required_quest_ids(quest) <= completed
                and int(quest.get("required_quest_points", 0) or 0) <= quest_points
            ):
                completed.add(quest_id)
                changed = True

    quest_points = sum(
        int(quest_data[quest_id].get("point_reward", 0) or 0)
        for quest_id in completed
    )
    startable = {
        quest_id
        for quest_id, quest in quest_data.items()
        if _required_quest_ids(quest) <= completed
        and int(quest.get("required_quest_points", 0) or 0) <= quest_points
    }
    return completed, startable


def _rank_root_orphans(
    root_orphans: Iterable[str],
    actions: Iterable[Mapping[str, Any]],
    seed_sources: Mapping[str, set[str]],
    baseline_reachable: set[str],
    baseline_unresolved_count: int,
    *,
    active_action_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for item in root_orphans:
        candidate_sources = dict(seed_sources)
        candidate_sources[item] = {f"candidate:{item}"}
        reachable, _route, unresolved = _close_actions(
            actions,
            candidate_sources,
            active_action_ids=active_action_ids,
        )
        newly_reachable = sorted(reachable - baseline_reachable)
        rows.append(
            {
                "item": item,
                "newly_reachable_item_count": len(newly_reachable),
                "newly_unblocked_action_count": (
                    baseline_unresolved_count - len(unresolved)
                ),
                "newly_reachable_items": newly_reachable,
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -row["newly_reachable_item_count"],
            -row["newly_unblocked_action_count"],
            row["item"],
        ),
    )


def build_reachability_report() -> dict[str, Any]:
    from ankiscape.data import combat_data
    from ankiscape.core import constants
    from ankiscape.data import farming_data
    from ankiscape.data import fist_of_guthix_data
    from ankiscape.data import pack_data
    from ankiscape.data import pyramid_plunder_data
    from ankiscape.data import shooting_star_data
    from ankiscape.data import shop_data
    from ankiscape.data.impling_jar_data import IMPLING_JAR_DATA
    from ankiscape.data.livid_farm_data import (
        ARCANE_CAPACITOR_CHARGED,
        ARCANE_CAPACITOR_MAX_CHARGES,
        LIVID_FARM_UNLOCKS,
    )
    from ankiscape.logic import shop_logic
    from ankiscape.logic.livid_farm_logic import (
        livid_farm_cycle_projection_pure,
        livid_farm_locked_reasons_pure,
    )
    from ankiscape.logic.mage_training_arena_logic import (
        mage_training_arena_view_pure,
    )
    from ankiscape.logic.varrock_museum_logic import (
        varrock_museum_cleaning_locked_reasons_pure,
    )
    from ankiscape.core.skill_registry import trainable_skill_definitions
    from ankiscape.data import sorceress_garden_data
    from ankiscape.data import thieving_data
    from ankiscape.data import woodcutting_data
    from ankiscape.data.warriors_guild_data import DEFENDER_TIERS
    from ankiscape.logic.warriors_guild_logic import (
        default_warriors_guild_state_pure,
        enter_warriors_guild_cyclops_room_pure,
        warriors_guild_activity_locked_reasons_pure,
    )
    from ankiscape.logic_pure.logic_pure import (
        magic_target_locked_reasons_pure,
        player_combat_level_pure,
        quest_combat_encounter_has_stats_pure,
        target_unlock_locked_reasons_pure,
        utility_activity_locked_reasons_pure,
    )

    registered_items = {definition.storage_key for definition in constants.ITEM_DEFINITIONS}
    maximum_skill_levels = {
        skill.id: (
            len(constants.DUNGEONEERING_EXP_TABLE)
            if skill.id == "dungeoneering"
            else len(constants.EXP_TABLE)
        )
        for skill in trainable_skill_definitions()
    }
    maximum_combat_level = player_combat_level_pure(
        {
            "attack_level": 99,
            "defense_level": 99,
            "strength_level": 99,
            "constitution_level": 99,
            "prayer_level": 99,
            "ranged_level": 99,
            "magic_level": 99,
            "summoning_level": 99,
        }
    )

    def closure_quest_states(
        completable_quests: set[str],
        startable_quests: set[str],
        quest_progress: Mapping[str, int],
    ) -> dict[str, dict[str, Any]]:
        return {
            quest_id: {
                "started": quest_id in startable_quests,
                "completed": quest_id in completable_quests,
                "progress": int(quest_progress.get(quest_id, 0)),
            }
            for quest_id in startable_quests | completable_quests
        }

    def closure_player_data(
        completable_quests: set[str],
        startable_quests: set[str],
        reachable_items: set[str],
        quest_progress: Mapping[str, int],
        *,
        enemy: Mapping[str, Any] | None = None,
        include_inventory: bool = False,
    ) -> dict[str, Any]:
        player_data: dict[str, Any] = {
            "quests": closure_quest_states(
                completable_quests,
                startable_quests,
                quest_progress,
            ),
            "quest_points": sum(
                int(constants.QUEST_DATA[quest_id].get("point_reward", 0) or 0)
                for quest_id in completable_quests
            ),
            **{
                f"{skill_id}_level": level
                for skill_id, level in maximum_skill_levels.items()
            },
        }
        if enemy is not None or include_inventory:
            player_data["inventory"] = {
                item_name: 2**31 - 1 for item_name in reachable_items
            }
        start_equipment = (enemy or {}).get("start_equipment")
        equipment: dict[str, str] = {}
        if isinstance(start_equipment, Mapping):
            slot = start_equipment.get("slot")
            required_items = tuple(start_equipment.get("items", ()) or ())
            equipped_item = next(
                (item for item in required_items if item in reachable_items),
                None,
            )
            if isinstance(slot, str) and isinstance(equipped_item, str):
                equipment[slot] = equipped_item
        restricted_weapon = (enemy or {}).get("restricted_weapon")
        if isinstance(restricted_weapon, Mapping):
            equipped_weapon = next(
                (
                    item
                    for item in restricted_weapon.get("melee_weapons", ()) or ()
                    if item in reachable_items
                ),
                None,
            )
            if isinstance(equipped_weapon, str):
                equipment["weapon"] = equipped_weapon
        finisher = (enemy or {}).get("finisher")
        if isinstance(finisher, Mapping):
            finisher_item = str(finisher.get("item", "") or "")
            if finisher.get("must_be_worn") and finisher_item in reachable_items:
                equipment["finisher"] = finisher_item
            finisher_items = {
                item_name
                for item_name in (
                    finisher_item,
                    str(finisher.get("empty_item", "") or ""),
                    str(finisher.get("reload_item", "") or ""),
                    *(
                        str(row[0])
                        for row in finisher.get("charge_items", ()) or ()
                        if isinstance(row, (tuple, list)) and row
                    ),
                )
                if item_name in reachable_items
            }
            if finisher_items:
                player_data["combat_supply_loadout"] = {
                    "finishers": {item_name: 2**31 - 1 for item_name in finisher_items}
                }
        if equipment:
            player_data["equipment"] = equipment
        if enemy is not None and enemy.get("warriors_guild_gate"):
            activity_id = "warriors_guild_attack_dummy"
            if not warriors_guild_activity_locked_reasons_pure(
                player_data,
                activity_id,
            ):
                guild_state = default_warriors_guild_state_pure()
                guild_state.update(
                    {
                        "automation_mode": "advanced",
                        "payment_mode": "single",
                        "single_token": "attack",
                    }
                )
                guild_state["tokens"]["attack"] = 65535
                player_data["warriors_guild"] = guild_state
                player_data, entered, _result = (
                    enter_warriors_guild_cyclops_room_pure(player_data)
                )
                rune_defender = str(DEFENDER_TIERS[-2]["name"])
                if (
                    entered
                    and enemy.get("warriors_guild_target") == "cyclossus"
                    and rune_defender in reachable_items
                ):
                    guild_state = dict(player_data["warriors_guild"])
                    guild_state["shown_defender_index"] = len(DEFENDER_TIERS) - 2
                    guild_state["cyclossus_pending"] = True
                    player_data["warriors_guild"] = guild_state
                    player_data["equipment"] = {
                        **(player_data.get("equipment", {}) or {}),
                        "shield": rune_defender,
                    }
        return player_data

    @lru_cache(maxsize=None)
    def closure_magic_player_data(
        completable_quests: frozenset[str],
        startable_quests: frozenset[str],
        reachable_items: frozenset[str],
        quest_progress: tuple[tuple[str, int], ...],
    ) -> dict[str, Any]:
        player_data = closure_player_data(
            set(completable_quests),
            set(startable_quests),
            set(reachable_items),
            dict(quest_progress),
            include_inventory=True,
        )
        arena_view = mage_training_arena_view_pure(player_data)
        if arena_view["can_enter"] and all(
            room["runnable"] for room in arena_view["room_options"]
        ):
            player_data["mage_training_arena"] = {"completed": True}

        museum_player = dict(player_data)
        museum_equipment = dict(museum_player.get("equipment", {}) or {})
        if "Leather gloves" in reachable_items:
            museum_equipment["hands"] = "Leather gloves"
        if "Leather boots" in reachable_items:
            museum_equipment["feet"] = "Leather boots"
        museum_player["equipment"] = museum_equipment
        if not varrock_museum_cleaning_locked_reasons_pure(museum_player):
            player_data["varrock_museum"] = {"digsite_pendant_unlocked": True}

        livid_projection = livid_farm_cycle_projection_pure(player_data)
        if (
            not livid_farm_locked_reasons_pure(player_data)
            and set(livid_projection["rune_cost"]) <= reachable_items
        ):
            player_data["livid_farm"] = {
                "unlocked_spells": [row[0] for row in LIVID_FARM_UNLOCKS],
                "borrowed_power_claimed": True,
            }
        return player_data

    def magic_player_data(
        spec: Mapping[str, Any],
        completable_quests: set[str],
        startable_quests: set[str],
        reachable_items: set[str],
        quest_progress: Mapping[str, int],
    ) -> dict[str, Any]:
        player_data = dict(
            closure_magic_player_data(
                frozenset(completable_quests),
                frozenset(startable_quests),
                frozenset(reachable_items),
                tuple(sorted(quest_progress.items())),
            )
        )
        borrowed_spell_id = str(spec.get("borrowed_spell_id", "") or "")
        if borrowed_spell_id and "livid_farm" in player_data:
            player_data["livid_farm"] = {
                **player_data["livid_farm"],
                "arcane_capacitor_spell": borrowed_spell_id,
                "arcane_capacitor_charges": ARCANE_CAPACITOR_MAX_CHARGES,
            }
            player_data["equipment"] = {
                **(player_data.get("equipment", {}) or {}),
                "neck": ARCANE_CAPACITOR_CHARGED,
            }
        return player_data

    def quest_combat_source_satisfiable(encounter: Mapping[str, Any]) -> bool:
        configs = encounter.get("npc_configs", {}) or {}
        minimum_combat = int(configs.get("minimum_player_combat", encounter.get("level", 0)) or 0)
        # Model the runtime with battle support enabled and a normal maxed player.
        return (
            quest_combat_encounter_has_stats_pure(encounter)
            and minimum_combat <= maximum_combat_level
        )

    target_unlock_keys = {
        (str(rule.get("skill_id", "")), target_id)
        for rule in constants.QUEST_UNLOCK_RULES
        if isinstance(rule, Mapping) and rule.get("gate_kind", "target") == "target"
        for target_id in _names(rule.get("target_ids"))
    }

    def action_access_reachable(
        skill_id: str,
        target_id: str,
        spec: Mapping[str, Any],
        completable_quests: set[str],
        startable_quests: set[str],
        reachable_items: set[str],
        quest_progress: Mapping[str, int],
    ) -> bool:
        player_data = closure_player_data(
            completable_quests,
            startable_quests,
            reachable_items,
            quest_progress,
            include_inventory=True,
        )
        if skill_id == "magic":
            player_data = magic_player_data(
                spec,
                completable_quests,
                startable_quests,
                reachable_items,
                quest_progress,
            )
            if magic_target_locked_reasons_pure(
                player_data,
                target_id,
                {target_id: spec},
            ):
                return False
        else:
            if skill_id == "utility":
                if not _names(spec.get("quest_requirements")) <= completable_quests:
                    return False
                if utility_activity_locked_reasons_pure(
                    player_data,
                    target_id,
                    constants.UTILITY_ACTIVITY_DATA,
                    constants.QUEST_UNLOCK_RULES,
                ):
                    return False
            quest_id = str(spec.get("quest_gate", "") or "")
            if quest_id and not _quest_gate_reachable(
                quest_id,
                str(spec.get("quest_gate_state", "completed") or "completed"),
                completable_quests,
                startable_quests,
            ):
                return False
        return not target_unlock_locked_reasons_pure(
            player_data,
            skill_id,
            target_id,
            constants.QUEST_UNLOCK_RULES,
        )

    action_tables = {
        "Mining": constants.ORE_DATA,
        "Woodcutting": constants.TREE_DATA,
        "Fishing": constants.FISHING_DATA,
        "Smithing": constants.SMITHING_DATA,
        "Crafting": constants.CRAFTING_DATA,
        "Fletching": constants.FLETCHING_DATA,
        "Firemaking": constants.FIREMAKING_DATA,
        "Cooking": constants.COOKING_DATA,
        "Runecrafting": constants.RUNECRAFTING_DATA,
        "Hunter": constants.HUNTER_DATA,
        "Herblore": constants.HERBLORE_DATA,
        "Magic": constants.MAGIC_DATA,
        "Prayer": constants.PRAYER_DATA,
        "Utility": constants.UTILITY_ACTIVITY_DATA,
    }

    actions: list[dict[str, Any]] = []
    consumers: dict[str, set[str]] = defaultdict(set)
    producers: dict[str, set[str]] = defaultdict(set)
    magic_runtime_gate_keys = {
        "borrowed_native_quest_gate",
        "borrowed_spell_id",
        "consumer_unavailable",
        "livid_unlock",
        "museum_unlock",
        "quest_gate",
    }
    utility_runtime_gate_keys = {
        "firemaking_level",
        "quest_requirements",
        "requires_no_follower",
        "requires_unskulled",
        "skill_requirements",
    }
    for family, table in action_tables.items():
        for action_id, raw_spec in table.items():
            if not isinstance(raw_spec, Mapping) or raw_spec.get("status", "implemented") != "implemented":
                continue
            required, alternatives = _requirements(raw_spec)
            outputs = _outputs(raw_spec)
            if not outputs:
                continue
            key = f"{family}:{action_id}"
            action = {
                "id": key,
                "required": required,
                "alternatives": alternatives,
                "outputs": outputs,
            }
            skill_id = family.lower()
            unlock_target_id = str(
                raw_spec.get("unlock_target_id", action_id) or action_id
            )
            if (
                (
                    skill_id == "magic"
                    and any(raw_spec.get(key) for key in magic_runtime_gate_keys)
                )
                or (
                    skill_id == "utility"
                    and any(raw_spec.get(key) for key in utility_runtime_gate_keys)
                )
                or raw_spec.get("quest_gate")
                or (skill_id, unlock_target_id) in target_unlock_keys
            ):
                action["is_accessible"] = (
                    lambda completed, startable, reachable, progress,
                    skill_id=skill_id, target_id=unlock_target_id, spec=raw_spec: (
                        action_access_reachable(
                            skill_id,
                            target_id,
                            spec,
                            completed,
                            startable,
                            reachable,
                            progress,
                        )
                    )
                )
            actions.append(action)
            for item in required | set().union(*alternatives) if alternatives else required:
                consumers[item].add(key)
            for item in outputs:
                producers[item].add(key)

    for crop_id, (seed, seedling, sapling) in farming_data.SAPLING_RECIPES.items():
        crop = farming_data.FARMING_CROPS_BY_ID[crop_id]
        if not crop.runnable:
            continue
        required = {seed, "Plant pot", "Gardening trowel"}
        alternatives = ({"Watering can", "Watering can (8)"},)
        outputs = {seedling, sapling}
        key = f"Farming:sapling:{crop_id}"
        actions.append(
            {
                "id": key,
                "required": required,
                "alternatives": alternatives,
                "outputs": outputs,
            }
        )
        for item in required | alternatives[0]:
            consumers[item].add(key)
        for item in outputs:
            producers[item].add(key)

    hatchets = {axe.display_name for axe in woodcutting_data.WOODCUTTING_AXES}
    for crop in farming_data.FARMING_CROPS:
        if not crop.runnable:
            continue
        plant_tool = (
            "Spade"
            if crop.patch_type in {"tree", "fruit_tree", "calquat", "spirit_tree"}
            else "Seed dibber"
        )
        required = {crop.seed_item, "Rake", plant_tool}
        alternatives: tuple[set[str], ...] = ()
        if crop.id == "willow":
            alternatives = ({"Secateurs", "Magic secateurs"},)
        elif crop.harvest_tool:
            required.add(crop.harvest_tool)
        if crop.output_item:
            key = f"Farming:{crop.id}"
            outputs = {crop.output_item}
            actions.append(
                {
                    "id": key,
                    "required": required,
                    "alternatives": alternatives,
                    "outputs": outputs,
                }
            )
            for item in required | set().union(*alternatives) if alternatives else required:
                consumers[item].add(key)
            producers[crop.output_item].add(key)
        if crop.root_item:
            key = f"Farming:clear:{crop.id}"
            root_requirements = required | {"Spade"}
            alternatives = (hatchets,)
            actions.append(
                {
                    "id": key,
                    "required": root_requirements,
                    "alternatives": alternatives,
                    "outputs": {crop.root_item},
                }
            )
            for item in root_requirements | hatchets:
                consumers[item].add(key)
            producers[crop.root_item].add(key)

    for target_id, spec in thieving_data.THIEVING_TARGETS.items():
        if spec.get("source_blocked"):
            continue
        outputs = _names(spec.get("guaranteed")) | _names(spec.get("loot"))
        if not outputs:
            continue
        alternatives: tuple[set[str], ...] = ()
        required_items_any = _names(spec.get("required_items_any"))
        if required_items_any:
            alternatives = (required_items_any,)
        key = f"Thieving:{target_id}"
        actions.append(
            {
                "id": key,
                "required": set(),
                "alternatives": alternatives,
                "outputs": outputs,
            }
        )
        for item in set().union(*alternatives) if alternatives else ():
            consumers[item].add(key)
        for item in outputs:
            producers[item].add(key)

    star_mining_key = "Activity:shooting_stars:mine"
    actions.append(
        {
            "id": star_mining_key,
            "required": set(),
            "alternatives": (),
            "outputs": {shooting_star_data.SHOOTING_STAR_STARDUST},
        }
    )
    producers[shooting_star_data.SHOOTING_STAR_STARDUST].add(
        star_mining_key
    )

    star_exchange_key = "Activity:shooting_stars:exchange"
    star_exchange_outputs = set(
        shooting_star_data.SHOOTING_STAR_REWARD_MAXIMA
    )
    actions.append(
        {
            "id": star_exchange_key,
            "required": {shooting_star_data.SHOOTING_STAR_STARDUST},
            "alternatives": (),
            "outputs": star_exchange_outputs,
        }
    )
    consumers[shooting_star_data.SHOOTING_STAR_STARDUST].add(
        star_exchange_key
    )
    for item in star_exchange_outputs:
        producers[item].add(star_exchange_key)

    fog_match_key = "Activity:fist_of_guthix:match"
    fog_token = "Fist of guthix token"
    actions.append(
        {
            "id": fog_match_key,
            "required": set(),
            "alternatives": (),
            "outputs": {fog_token},
        }
    )
    producers[fog_token].add(fog_match_key)
    for reward_id, reward in fist_of_guthix_data.FIST_OF_GUTHIX_REWARDS.items():
        family = fist_of_guthix_data.FIST_OF_GUTHIX_CONDITION_DATA[
            reward["family_id"]
        ]
        names_by_percent = family["names_by_percent"]
        charged = names_by_percent[max(names_by_percent)]
        spent = names_by_percent[min(names_by_percent)]
        buy_key = f"Activity:fist_of_guthix:buy:{reward_id}"
        actions.append(
            {
                "id": buy_key,
                "required": {fog_token},
                "alternatives": (),
                "outputs": {charged},
            }
        )
        consumers[fog_token].add(buy_key)
        producers[charged].add(buy_key)
        uncharge_key = f"Activity:fist_of_guthix:uncharge:{reward_id}"
        actions.append(
            {
                "id": uncharge_key,
                "required": {charged},
                "alternatives": (),
                "outputs": {spent},
            }
        )
        consumers[charged].add(uncharge_key)
        producers[spent].add(uncharge_key)
        recharge_key = f"Activity:fist_of_guthix:recharge:{reward_id}"
        actions.append(
            {
                "id": recharge_key,
                "required": {spent, fog_token},
                "alternatives": (),
                "outputs": {charged},
            }
        )
        consumers[spent].add(recharge_key)
        consumers[fog_token].add(recharge_key)
        producers[charged].add(recharge_key)
        ordered_names = [
            names_by_percent[percent]
            for percent in sorted(names_by_percent, reverse=True)
        ]
        for current, remainder in zip(ordered_names, ordered_names[1:]):
            degrade_key = (
                f"Activity:fist_of_guthix:degrade:{reward_id}:{current}"
            )
            actions.append(
                {
                    "id": degrade_key,
                    "required": {current},
                    "alternatives": (),
                    "outputs": {remainder},
                }
            )
            consumers[current].add(degrade_key)
            producers[remainder].add(degrade_key)

    garden_key = "Activity:sorceress_garden:harvest"
    garden_outputs = set(sorceress_garden_data.SORCERESS_GARDEN_HERB_POOL)
    garden_outputs.update(
        season.fruit
        for season in sorceress_garden_data.SORCERESS_GARDEN_SEASONS
    )
    garden_outputs.update(
        season.juice
        for season in sorceress_garden_data.SORCERESS_GARDEN_SEASONS
    )
    actions.append(
        {
            "id": garden_key,
            "required": set(),
            "alternatives": (),
            "outputs": garden_outputs,
        }
    )
    for item in garden_outputs:
        producers[item].add(garden_key)

    pyramid_key = "Activity:pyramid_plunder:loot"
    pyramid_outputs = {
        *pyramid_plunder_data.PYRAMID_PLUNDER_ARTIFACT_VALUES,
        *pyramid_plunder_data.PYRAMID_PLUNDER_BLACK_IBIS,
        *pyramid_plunder_data.PYRAMID_PLUNDER_PHARAOH_SCEPTRES,
        "Sceptre of the gods",
    }
    actions.append(
        {
            "id": pyramid_key,
            "required": set(),
            "alternatives": (),
            "outputs": pyramid_outputs,
        }
    )
    for item in pyramid_outputs:
        producers[item].add(pyramid_key)

    for item_name, spec in constants.CONSUMABLE_DATA.items():
        if not isinstance(spec, Mapping):
            continue
        leaves = _names(spec.get("leaves"))
        if not leaves:
            continue
        key = f"Item action:consume:{item_name}"
        actions.append({"id": key, "required": {item_name}, "alternatives": (), "outputs": leaves})
        consumers[item_name].add(key)
        for item in leaves:
            producers[item].add(key)

    for item_name, spec in pack_data.ITEM_PACK_DATA.items():
        content_item = str(spec["content_item"])
        key = f"Item action:open:{item_name}"
        actions.append({"id": key, "required": {item_name}, "alternatives": (), "outputs": {content_item}})
        consumers[item_name].add(key)
        producers[content_item].add(key)

    for item_name, rewards in IMPLING_JAR_DATA.items():
        outputs = {
            reward.item
            for reward in rewards
            if reward.item and int(reward.weight) > 0
        }
        if not outputs:
            continue
        key = f"Item action:loot:{item_name}"
        actions.append({"id": key, "required": {item_name}, "alternatives": (), "outputs": outputs})
        consumers[item_name].add(key)
        for output in outputs:
            producers[output].add(key)

    bob = shop_data.SHOP_SERVICES.get("bob_barter_decant_four", {})
    if bob.get("visibility") == "visible" and bob.get("action_type") == "decant_potions_to_dose":
        for base in shop_logic.DECANTABLE_FOUR_DOSE_POTION_BASES:
            # Reachability is quantity-free: a repeatable three-dose recipe can
            # supply enough copies for Bob to produce every lower/four-dose
            # remainder state while preserving the exact runtime dose math.
            required = {f"{base} (3)"}
            outputs = {f"{base} ({dose})" for dose in (1, 2, 4)} | {"Vial"}
            key = f"Shop service:bob_barter_decant_four:{base}"
            actions.append({"id": key, "required": required, "alternatives": (), "outputs": outputs})
            for item in required:
                consumers[item].add(key)
            for item in outputs:
                producers[item].add(key)

    teplin_fill = shop_data.SHOP_SERVICES.get(
        "teplin_fill_potion_flasks", {}
    )
    teplin_decant = shop_data.SHOP_SERVICES.get(
        "teplin_decant_flasks_to_vials", {}
    )
    if (
        teplin_fill.get("visibility") == "visible"
        and teplin_fill.get("action_type") == "fill_potion_flasks"
        and teplin_decant.get("visibility") == "visible"
        and teplin_decant.get("action_type") == "decant_flasks_to_vials"
    ):
        for base in shop_logic.DECANTABLE_FLASK_POTION_BASES:
            fill_required = {f"{base} (3)", "Potion flask"}
            fill_output = {shop_logic.potion_flask_name(base, 6)}
            fill_key = f"Shop service:teplin_fill_potion_flasks:{base}"
            fill_action = {
                "id": fill_key,
                "required": fill_required,
                "alternatives": (),
                "outputs": fill_output,
            }
            if isinstance(teplin_fill.get("access"), Mapping):
                fill_action["is_accessible"] = (
                    lambda completed, startable, reachable, progress, service=teplin_fill: (
                        shop_access_reachable(
                            service,
                            completed,
                            startable,
                            reachable,
                            progress,
                        )
                    )
                )
            actions.append(fill_action)
            for item in fill_required:
                consumers[item].add(fill_key)
            for item in fill_output:
                producers[item].add(fill_key)

            decant_required = {shop_logic.potion_flask_name(base, 3)}
            decant_outputs = {
                f"{base} ({dose})"
                for dose in (1, 2, 4)
            }
            decant_key = (
                f"Shop service:teplin_decant_flasks_to_vials:{base}"
            )
            decant_action = {
                "id": decant_key,
                "required": decant_required,
                "alternatives": (),
                "outputs": decant_outputs,
            }
            if isinstance(teplin_decant.get("access"), Mapping):
                decant_action["is_accessible"] = (
                    lambda completed, startable, reachable, progress, service=teplin_decant: (
                        shop_access_reachable(
                            service,
                            completed,
                            startable,
                            reachable,
                            progress,
                        )
                    )
                )
            actions.append(decant_action)
            for item in decant_required:
                consumers[item].add(decant_key)
            for item in decant_outputs:
                producers[item].add(decant_key)

    for service_id, service in shop_data.SHOP_SERVICES.items():
        if (
            service.get("visibility") != "visible"
            or service.get("action_type") != "item_conversion"
        ):
            continue
        required = _names(service.get("inputs"))
        if int(service.get("price", 0) or 0) > 0:
            required.add(str(service.get("currency_item_name", "Coins")))
        outputs = _names(service.get("outputs"))
        if not outputs:
            continue
        key = f"Shop service:{service_id}"
        action = {
            "id": key,
            "required": required,
            "alternatives": (),
            "outputs": outputs,
        }
        if isinstance(service.get("access"), Mapping):
            action["is_accessible"] = (
                lambda completed, startable, reachable, progress, service=service: (
                    shop_access_reachable(
                        service,
                        completed,
                        startable,
                        reachable,
                        progress,
                    )
                )
            )
        actions.append(action)
        for item in required:
            consumers[item].add(key)
        for item in outputs:
            producers[item].add(key)

    seen_charge_families: set[tuple[tuple[tuple[str, int], ...], str, str]] = set()
    for enemy_id, enemy in combat_data.COMBAT_ENEMY_DATA.items():
        finisher = enemy.get("finisher", {})
        if not isinstance(finisher, Mapping):
            continue
        charge_items = tuple(
            (str(row[0]), int(row[1]))
            for row in finisher.get("charge_items", ()) or ()
            if isinstance(row, (tuple, list))
            and len(row) >= 2
            and isinstance(row[0], str)
        )
        empty_item = str(finisher.get("empty_item", "") or "")
        reload_item = str(finisher.get("reload_item", "") or "")
        family = (charge_items, empty_item, reload_item)
        if not charge_items or family in seen_charge_families:
            continue
        seen_charge_families.add(family)
        ordered_states = [item for item, _charges in charge_items]
        if empty_item:
            ordered_states.append(empty_item)
        for current, remainder in zip(ordered_states, ordered_states[1:]):
            key = f"Combat finisher:{enemy_id}:{current}"
            actions.append(
                {
                    "id": key,
                    "required": {current},
                    "alternatives": (),
                    "outputs": {remainder},
                }
            )
            consumers[current].add(key)
            producers[remainder].add(key)
        if empty_item and reload_item:
            key = f"Combat refill:{enemy_id}"
            full_item = charge_items[0][0]
            actions.append(
                {
                    "id": key,
                    "required": {empty_item, reload_item},
                    "alternatives": (),
                    "outputs": {full_item},
                }
            )
            consumers[empty_item].add(key)
            consumers[reload_item].add(key)
            producers[full_item].add(key)

    for table in woodcutting_data.BIRD_NEST_OPEN_TABLES:
        table_spec = vars(table)
        input_item = table_spec["input_item"]
        outputs = _names(table_spec.get("guaranteed_item"))
        outputs |= {
            roll.item
            for roll in table_spec.get("rolls", ())
            if isinstance(getattr(roll, "item", None), str)
        }
        key = f"Item action:open:{input_item}"
        actions.append({"id": key, "required": {input_item}, "alternatives": (), "outputs": outputs})
        consumers[input_item].add(key)
        for item in outputs:
            producers[item].add(key)

    seed_sources: dict[str, set[str]] = defaultdict(set)
    seed_item_counts: dict[str, int] = defaultdict(int)
    repeatable_seed_items: set[str] = set()
    conditional_seed_sources: list[dict[str, Any]] = []

    def shop_access_reachable(
        shop: Mapping[str, Any],
        completable_quests: set[str],
        startable_quests: set[str],
        reachable_items: set[str],
        quest_progress: Mapping[str, int],
    ) -> bool:
        player_data = closure_player_data(
            completable_quests,
            startable_quests,
            reachable_items,
            quest_progress,
        )
        return shop_logic.shop_access_lock_reason_pure(player_data, shop) is None

    for shop_id, shop in shop_data.SHOP_DATA.items():
        if shop.get("visibility") != "visible" or not shop.get("currency_implemented"):
            continue
        source_id = f"shop:{shop_id}"
        item_counts: dict[str, int] = defaultdict(int)
        repeatable_items: set[str] = set()
        for row in shop.get("stock", ()) or ():
            if row.get("disposition") == "live" and int(row.get("default_quantity", 0) or 0) > 0:
                name = row.get("item_name")
                if isinstance(name, str) and name:
                    item_counts[name] += int(row.get("default_quantity", 0) or 0)
                    if int(row.get("restock_amount", 0) or 0) > 0:
                        repeatable_items.add(name)
        if not item_counts:
            continue
        if isinstance(shop.get("access"), Mapping):
            conditional_seed_sources.append(
                {
                    "id": source_id,
                    "items": set(item_counts),
                    "item_counts": dict(item_counts),
                    "repeatable_items": repeatable_items,
                    "is_accessible": lambda completed, startable, reachable, progress, shop=shop: shop_access_reachable(
                        shop,
                        completed,
                        startable,
                        reachable,
                        progress,
                    ),
                }
            )
            continue
        for item, amount in item_counts.items():
            seed_sources[item].add(source_id)
            seed_item_counts[item] += amount
        repeatable_seed_items.update(repeatable_items)

    for enemy_id, enemy in combat_data.COMBAT_ENEMY_DATA.items():
        items = _drop_names(enemy.get("drops", {}))
        if enemy_id == "cyclops" and enemy.get("warriors_guild_gate"):
            items.update(row["name"] for row in DEFENDER_TIERS[:-1])
        if not items:
            continue
        source_id = f"combat:{enemy_id}"
        conditional_seed_sources.append(
            {
                "id": source_id,
                "items": items,
                "repeatable_items": items,
                "is_accessible": lambda completed, startable, reachable, progress, enemy_id=enemy_id, enemy=enemy: _combat_drop_gate_reachable(
                    enemy_id,
                    enemy,
                    closure_player_data(
                        completed,
                        startable,
                        reachable,
                        progress,
                        enemy=enemy,
                    ),
                ),
            }
        )

    for row in constants.BIRD_NEST_DROP_TABLE:
        for item in _names(row.get("item")):
            seed_sources[item].add("woodcutting:bird_nest_roll")
            repeatable_seed_items.add(item)

    scenario_sources: list[dict[str, set[str]]] = []
    scenario_action_ids: list[set[str]] = []
    blocked_quest_stage_products, completable_quests, startable_quests = (
        _close_quest_reachability(
            actions,
            seed_sources,
            seed_item_counts,
            repeatable_seed_items,
            constants.QUEST_DATA,
            registered_items,
            quest_combat_source_satisfiable,
            claim_data=constants.CLAIM_DATA,
            maximum_skill_levels=maximum_skill_levels,
            conditional_seed_sources=conditional_seed_sources,
            scenario_sources_out=scenario_sources,
            scenario_action_ids_out=scenario_action_ids,
        )
    )

    scenario_closures = [
        _close_actions(
            actions,
            sources,
            active_action_ids=active_action_ids,
        )
        for sources, active_action_ids in zip(
            scenario_sources,
            scenario_action_ids,
        )
    ]
    reachable = set.union(*(items for items, _route, _unresolved in scenario_closures))
    route = {
        item: min(
            item_route[item]
            for items, item_route, _unresolved in scenario_closures
            if item in items
        )
        for item in reachable
    }
    resolved_action_ids = {
        action["id"]
        for action in actions
        if any(action not in scenario_unresolved for _items, _route, scenario_unresolved in scenario_closures)
    }
    unresolved = [action for action in actions if action["id"] not in resolved_action_ids]

    consumed = set(consumers)
    orphan_inputs = sorted(consumed - reachable)
    root_orphans = [item for item in orphan_inputs if not producers.get(item)]
    cascade_orphans = [item for item in orphan_inputs if producers.get(item)]
    unresolved_actions = []
    for action in unresolved:
        scenario_gaps = [
            (
                sorted(action["required"] - scenario_items),
                [
                    sorted(group)
                    for group in action["alternatives"]
                    if not group & scenario_items
                ],
            )
            for scenario_items, _route, _scenario_unresolved in scenario_closures
        ]
        missing = sorted({item for gaps, _options in scenario_gaps for item in gaps})
        missing_alternatives = sorted({
            tuple(group)
            for _gaps, options in scenario_gaps
            for group in options
        })
        unresolved_actions.append(
            {
                "id": action["id"],
                "missing": missing,
                "missing_alternatives": missing_alternatives,
                "outputs": sorted(action["outputs"]),
            }
        )
    # Root leverage remains an optimistic quantity-free diagnostic. Branch-local
    # conjunction truth is preserved in the primary reachable/unresolved figures.
    root_orphan_leverage = _rank_root_orphans(
        root_orphans,
        actions,
        seed_sources,
        reachable,
        len(unresolved),
        active_action_ids=set().union(*scenario_action_ids),
    )

    return {
        "schema_version": 1,
        "action_count": len(actions),
        "seed_item_count": len(seed_sources),
        "reachable_item_count": len(reachable),
        "consumed_item_count": len(consumed),
        "orphan_input_count": len(orphan_inputs),
        "root_orphan_count": len(root_orphans),
        "cascade_orphan_count": len(cascade_orphans),
        "unresolved_action_count": len(unresolved_actions),
        "orphan_inputs": [
            {
                "item": item,
                "kind": "cascade" if producers.get(item) else "root",
                "consumers": sorted(consumers[item]),
                "known_producers": sorted(producers.get(item, ())),
            }
            for item in orphan_inputs
        ],
        "root_orphan_leverage": root_orphan_leverage,
        "blocked_quest_stage_products": blocked_quest_stage_products,
        "unresolved_actions": sorted(unresolved_actions, key=lambda row: row["id"]),
        "routes": {item: route[item] for item in sorted(route)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit the full machine-readable report.")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print only the audit counts.",
    )
    parser.add_argument(
        "--rank-roots",
        type=int,
        metavar="N",
        help="Print the N root acquisitions with the largest transitive item gain.",
    )
    args = parser.parse_args()
    report = build_reachability_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.summary:
        print(
            f"{report['action_count']} actions; {report['reachable_item_count']} reachable items; "
            f"{report['orphan_input_count']} orphan inputs; {report['unresolved_action_count']} blocked actions"
        )
    elif args.rank_roots is not None:
        limit = max(args.rank_roots, 0)
        print(
            f"{report['action_count']} actions; {report['reachable_item_count']} reachable items; "
            f"{report['orphan_input_count']} orphan inputs; {report['unresolved_action_count']} blocked actions"
        )
        for row in report["root_orphan_leverage"][:limit]:
            print(
                f"- {row['item']}: +{row['newly_reachable_item_count']} items; "
                f"+{row['newly_unblocked_action_count']} actions"
            )
    else:
        print(
            f"{report['action_count']} actions; {report['reachable_item_count']} reachable items; "
            f"{report['orphan_input_count']} orphan inputs; {report['unresolved_action_count']} blocked actions"
        )
        for row in report["orphan_inputs"]:
            print(f"- {row['item']}: {', '.join(row['consumers'][:4])}")
    return 1 if report["orphan_input_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
