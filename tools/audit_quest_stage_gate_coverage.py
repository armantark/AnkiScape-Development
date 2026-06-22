#!/usr/bin/env python3
"""Summarize generated quest-stage blocker coverage.

This is intentionally read-only: it imports the runtime quest contract and
prints the current blocker coverage plus explicit gaps for future source-audit
passes.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quest_data import quests_as_dict
from logic_pure import quest_combat_encounter_has_stats_pure


def main() -> None:
    data = quests_as_dict()
    total = len(data)
    stage_rows = 0
    combat_rows = 0
    combat_with_any_stats = 0
    combat_with_resolver_stats = 0
    item_quests = 0
    combat_quests = 0
    no_stage_requirements = []
    kinds = Counter()

    for quest_id, quest in data.items():
        requirements = quest.get("stage_requirements", ()) or ()
        if not requirements:
            no_stage_requirements.append((quest_id, quest.get("display_name", quest_id)))
            continue
        stage_rows += len(requirements)
        quest_has_item = False
        quest_has_combat = False
        for requirement in requirements:
            has_inventory = bool(requirement.get("required_inventory"))
            has_consumed_inventory = bool(requirement.get("consumed_inventory"))
            has_produced_inventory = bool(requirement.get("produced_inventory"))
            has_tools = bool(requirement.get("required_tools"))
            has_options = bool(requirement.get("required_inventory_options"))
            has_consumed_options = bool(requirement.get("consumed_inventory_options"))
            if (
                has_inventory
                or has_consumed_inventory
                or has_produced_inventory
                or has_tools
                or has_options
                or has_consumed_options
            ):
                quest_has_item = True
                if has_inventory:
                    kinds["inventory"] += 1
                if has_consumed_inventory:
                    kinds["consumed_inventory"] += 1
                if has_produced_inventory:
                    kinds["produced_inventory"] += 1
                if has_tools:
                    kinds["tools"] += 1
                if has_options:
                    kinds["inventory_options"] += 1
                if has_consumed_options:
                    kinds["consumed_inventory_options"] += 1
            encounters = requirement.get("combat_encounters", ()) or ()
            if encounters:
                quest_has_combat = True
                combat_rows += len(encounters)
                combat_with_any_stats += sum(1 for encounter in encounters if encounter.get("npc_stats"))
                combat_with_resolver_stats += sum(1 for encounter in encounters if _has_resolver_stats(encounter))
        if quest_has_item:
            item_quests += 1
        if quest_has_combat:
            combat_quests += 1

    print(f"quests: {total}")
    print(f"quests_with_stage_requirements: {total - len(no_stage_requirements)}")
    print(f"stage_requirement_rows: {stage_rows}")
    print(f"quests_with_item_or_tool_blockers: {item_quests}")
    print(f"quests_with_combat_blockers: {combat_quests}")
    print(f"combat_encounter_rows: {combat_rows}")
    print(f"combat_encounters_with_any_stats: {combat_with_any_stats}")
    print(f"combat_encounters_with_resolver_stats: {combat_with_resolver_stats}")
    print("requirement_row_kinds:")
    for key in sorted(kinds):
        print(f"  {key}: {kinds[key]}")
    print("quests_without_stage_requirements:")
    for quest_id, display_name in no_stage_requirements:
        print(f"  {quest_id}: {display_name}")


def _has_resolver_stats(encounter):
    return quest_combat_encounter_has_stats_pure(encounter)


if __name__ == "__main__":
    main()
