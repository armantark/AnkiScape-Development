"""Quest and one-time claim data for AnkiScape."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Tuple

try:
    from .runecrafting_data import RUNEMYSTERIES_SOURCE_PATH, WICKED_HOOD_ITEM
except ImportError:  # pragma: no cover
    from runecrafting_data import RUNEMYSTERIES_SOURCE_PATH, WICKED_HOOD_ITEM  # type: ignore


RUNE_MYSTERIES_ID = "rune_mysteries"
DEFAULT_QUEST_TARGET = RUNE_MYSTERIES_ID


@dataclass(frozen=True)
class QuestStage:
    stage: int
    journal: Tuple[str, ...]


@dataclass(frozen=True)
class QuestDefinition:
    id: str
    display_name: str
    stages: int
    point_reward: int
    rewards: Tuple[Tuple[str, int], ...]
    start_point: str
    requirements: Tuple[str, ...]
    required_items: Tuple[Tuple[str, int], ...]
    combat: str
    source: str
    journal_stages: Tuple[QuestStage, ...]


@dataclass(frozen=True)
class ClaimDefinition:
    id: str
    display_name: str
    item_name: str
    quantity: int
    source: str
    required_quest: str = RUNE_MYSTERIES_ID
    required_runecrafting_level: int = 5


def _clean_journal(*lines: str) -> Tuple[str, ...]:
    cleaned = []
    for line in lines:
        stripped = re.sub(r"</?col(?:=[^>]*)?>", "", line)
        stripped = stripped.replace("<str>", "").strip()
        if stripped:
            cleaned.append(stripped)
    return tuple(cleaned)


RUNE_MYSTERIES_STAGES: Tuple[QuestStage, ...] = (
    QuestStage(
        1,
        _clean_journal(
            "I spoke to Duke Horacio in Lumbridge Castle. He told me",
            "that he'd found a Strange Talisman in the Castle which",
            "might be of use to the Order of Wizards at the Wizards'",
            "Tower. He asked me to take it there and give it to a wizard",
            "called Sedridor. I can find the Wizards' Tower south west of",
            "Lumbridge, across the bridge from Draynor Village.",
        ),
    ),
    QuestStage(
        2,
        _clean_journal(
            "I travelled toward the Wizards' Tower with the strange talisman.",
        ),
    ),
    QuestStage(
        3,
        _clean_journal(
            "I delivered the Strange Talisman to Sedridor in the",
            "basement of the Wizards' Tower. He believes it might be",
            "key to discovering a Teleportation Incantation to the lost",
            "Rune Essence Mine. He asked me to help confirm this by",
            "delivering a Package to Aubury, an expert on",
            "Runecrafting. I can find him in his Rune Shop in south east",
            "Varrock.",
        ),
    ),
    QuestStage(
        4,
        _clean_journal(
            "I carried Sedridor's package toward Aubury's Rune Shop in Varrock.",
        ),
    ),
    QuestStage(
        5,
        _clean_journal(
            "I delivered the Package to Aubury at his Rune Shop in",
            "south east Varrock. He confirmed Sedridor's suspicions",
            "and asked me to take some Research Notes back to him. I",
            "can find Sedridor in the basement of the Wizards' Tower.",
        ),
    ),
    QuestStage(
        6,
        _clean_journal(
            "I spoke to Duke Horacio and he showed me a strange",
            "talisman that had been found by one of his subjects.",
            "I agreed to take it to the Wizards' Tower, South West of",
            "Lumbridge for further examination by the wizards.",
            "I gave the Talisman to the Head of the Tower and",
            "agreed to help him with his research into rune stones.",
            "I took the research package to Varrock and delivered it.",
            "Aubury was interested in the research package and gave",
            "me his own research notes to deliver to Sedridor.",
            "I brought Sedridor the research notes that Aubury had",
            "compiled so that he could compare their research. They",
            "discovered that it was now possible to create new rune",
            "stones, a skill that had been thought lost forever.",
            "In return for all of my help they taught me how to do this,",
            "and will teleport me to mine blank runes anytime.",
            "Quest complete!",
        ),
    ),
)


QUESTS: Tuple[QuestDefinition, ...] = (
    QuestDefinition(
        id=RUNE_MYSTERIES_ID,
        display_name="Rune Mysteries",
        stages=6,
        point_reward=1,
        rewards=(("Air talisman", 1),),
        start_point="Speak to Duke Horacio, upstairs in Lumbridge Castle.",
        requirements=(),
        required_items=(),
        combat="None.",
        source=RUNEMYSTERIES_SOURCE_PATH,
        journal_stages=RUNE_MYSTERIES_STAGES,
    ),
)
QUESTS_BY_ID: Dict[str, QuestDefinition] = {quest.id: quest for quest in QUESTS}


CLAIMS: Tuple[ClaimDefinition, ...] = (
    ClaimDefinition(
        id="wicked_hood",
        display_name="Wicked hood",
        item_name=WICKED_HOOD_ITEM,
        quantity=1,
        source="https://runescape.wiki/w/Wicked_hood",
    ),
)
CLAIMS_BY_ID: Dict[str, ClaimDefinition] = {claim.id: claim for claim in CLAIMS}


def default_quest_states() -> Dict[str, Dict[str, object]]:
    return {
        quest.id: {"started": False, "progress": 0, "completed": False}
        for quest in QUESTS
    }


def default_claim_states() -> Dict[str, Dict[str, object]]:
    return {
        claim.id: {"claimed": False}
        for claim in CLAIMS
    }


def quests_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        quest.id: {
            "id": quest.id,
            "display_name": quest.display_name,
            "stages": quest.stages,
            "point_reward": quest.point_reward,
            "rewards": dict(quest.rewards),
            "start_point": quest.start_point,
            "requirements": quest.requirements,
            "required_items": dict(quest.required_items),
            "combat": quest.combat,
            "source": quest.source,
            "journal_stages": {
                stage.stage: stage.journal for stage in quest.journal_stages
            },
        }
        for quest in QUESTS
    }


def claims_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        claim.id: {
            "id": claim.id,
            "display_name": claim.display_name,
            "item_name": claim.item_name,
            "quantity": claim.quantity,
            "source": claim.source,
            "required_quest": claim.required_quest,
            "required_runecrafting_level": claim.required_runecrafting_level,
        }
        for claim in CLAIMS
    }

