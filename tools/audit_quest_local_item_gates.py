#!/usr/bin/env python3
"""Find likely false quest-local item gates in the quest-stage contract."""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
import sys
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.quest_data import quests_as_dict


_USED_DURING_PREFIX = "Used during quest:"
_ITEM_WITH_QUANTITY_RE = re.compile(r"(?P<name>.+?)\s+x(?P<quantity>\d+)\b")
_ACTION_ACQUISITION_RE = re.compile(
    r"\b(ask|buy|bribe|collect|find|get|pick up|purchase|receive|recover|search|steal|take)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class QuestLocalGateCandidate:
    category: str
    quest_id: str
    quest_name: str
    stage: int
    item_name: str
    detail: str

    def as_tsv(self) -> str:
        return "\t".join(
            (
                self.category,
                self.quest_id,
                self.quest_name,
                str(self.stage),
                self.item_name,
                self.detail.replace("\t", " "),
            )
        )


def quest_local_gate_candidates(data: Mapping[str, Mapping[str, object]] | None = None) -> tuple[QuestLocalGateCandidate, ...]:
    data = data or quests_as_dict()
    candidates: list[QuestLocalGateCandidate] = []
    for quest_id, quest in data.items():
        quest_name = str(quest.get("display_name", quest_id))
        stage_requirements = tuple(quest.get("stage_requirements", ()) or ())
        produced_by_stage = _produced_items_by_stage(stage_requirements)
        quest_local_products = set(quest.get("start_inventory", {}) or {})
        for items in produced_by_stage.values():
            quest_local_products.update(items)

        for item_name in sorted(_quest_wide_used_during_items(quest) & quest_local_products):
            candidates.append(
                QuestLocalGateCandidate(
                    "quest_wide_same_quest_product",
                    quest_id,
                    quest_name,
                    _first_produced_stage(item_name, produced_by_stage),
                    item_name,
                    "Quest-wide Used during quest text lists an item produced by this quest.",
                )
            )

        produced_so_far = set(quest.get("start_inventory", {}) or {})
        for requirement in sorted(stage_requirements, key=lambda row: (row.get("stage", 0), row.get("variant", ""), row.get("description", ""))):
            stage = int(requirement.get("stage", 0) or 0)
            gated_items = _stage_inventory_items(requirement)
            for item_name in sorted(gated_items & quest_local_products - produced_so_far):
                candidates.append(
                    QuestLocalGateCandidate(
                        "stage_requires_same_quest_product_before_source",
                        quest_id,
                        quest_name,
                        stage,
                        item_name,
                        "Stage checks an item produced by this quest before any earlier stage produces it.",
                    )
                )

            action_text = " ".join(
                (
                    str(requirement.get("description", "")),
                    " ".join(str(action) for action in requirement.get("required_actions", ()) or ()),
                )
            )
            if _ACTION_ACQUISITION_RE.search(action_text):
                for item_name in sorted(gated_items - quest_local_products):
                    if item_name.lower() in action_text.lower():
                        candidates.append(
                            QuestLocalGateCandidate(
                                "stage_item_with_acquisition_action",
                                quest_id,
                                quest_name,
                                stage,
                                item_name,
                                action_text,
                            )
                        )

            produced_so_far.update(requirement.get("produced_inventory", {}) or {})
    return tuple(candidates)


def _quest_wide_used_during_items(quest: Mapping[str, object]) -> set[str]:
    items: set[str] = set()
    for requirement in quest.get("requirements", ()) or ():
        text = str(requirement)
        if _USED_DURING_PREFIX not in text:
            continue
        _, _, tail = text.partition(_USED_DURING_PREFIX)
        for chunk in re.split(r"[,;]", tail):
            for option in re.split(r"\s+or\s+", chunk):
                match = _ITEM_WITH_QUANTITY_RE.search(option.strip())
                if match:
                    items.add(match.group("name").strip())
    return items


def _stage_inventory_items(requirement: Mapping[str, object]) -> set[str]:
    items: set[str] = set()
    for key in ("required_inventory", "consumed_inventory", "required_tools"):
        value = requirement.get(key, {}) or {}
        if isinstance(value, Mapping):
            items.update(str(item_name) for item_name in value)
    for key in ("required_inventory_options", "consumed_inventory_options"):
        for option_group in requirement.get(key, ()) or ():
            for option in option_group:
                if isinstance(option, Mapping):
                    items.update(str(item_name) for item_name in option)
    return items


def _produced_items_by_stage(stage_requirements: Iterable[Mapping[str, object]]) -> dict[int, set[str]]:
    produced: dict[int, set[str]] = {}
    for requirement in stage_requirements:
        stage = int(requirement.get("stage", 0) or 0)
        items = requirement.get("produced_inventory", {}) or {}
        if isinstance(items, Mapping) and items:
            produced.setdefault(stage, set()).update(str(item_name) for item_name in items)
    return produced


def _first_produced_stage(item_name: str, produced_by_stage: Mapping[int, set[str]]) -> int:
    for stage in sorted(produced_by_stage):
        if item_name in produced_by_stage[stage]:
            return stage
    return 0


def main() -> None:
    candidates = quest_local_gate_candidates()
    print("category\tquest_id\tquest_name\tstage\titem_name\tdetail")
    for candidate in candidates:
        print(candidate.as_tsv())
    print(f"total_candidates\t{len(candidates)}")


if __name__ == "__main__":
    main()
