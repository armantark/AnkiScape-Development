from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

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
    QuestStage(2, _clean_journal("I travelled toward the Wizards' Tower with the strange talisman.")),
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
    QuestStage(4, _clean_journal("I carried Sedridor's package toward Aubury's Rune Shop in Varrock.")),
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

QUEST = QuestDefinition(
        id=RUNE_MYSTERIES_ID,
        display_name="Rune Mysteries",
        stages=6,
        point_reward=1,
        rewards=(("Air talisman", 1),),
        start_point="Speak to Duke Horacio, upstairs in Lumbridge Castle.",
        requirements=(),
        required_items=(),
        combat="None.",
        source=(
            f"{RUNEMYSTERIES_SOURCE_PATH}; {RUNE_MYSTERIES_DUKE_SOURCE_PATH}; "
            f"{RUNE_MYSTERIES_SEDRIDOR_SOURCE_PATH}; {RUNE_MYSTERIES_AUBURY_SOURCE_PATH}"
        ),
        journal_stages=RUNE_MYSTERIES_STAGES,
        release_date="2003-12-01",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        start_inventory=(("Air talisman", 1),),
        unlocks=("Ability to craft runes", "Ability to mine rune essence"),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    RUNE_MYSTERIES_ID: (
        _stage_req(
            1,
            "Deliver the strange talisman to Sedridor and receive his research package.",
            f"{RUNEMYSTERIES_SOURCE_PATH}; {RUNE_MYSTERIES_DUKE_SOURCE_PATH}; {RUNE_MYSTERIES_SEDRIDOR_SOURCE_PATH}",
            consumed_inventory=(("Air talisman", 1),),
            produced_inventory=(("Research package", 1),),
            auto_actions=("Deliver the strange talisman to Sedridor",),
        ),
        _stage_req(
            3,
            "Deliver Sedridor's package to Aubury and receive his research notes.",
            f"{RUNEMYSTERIES_SOURCE_PATH}; {RUNE_MYSTERIES_SEDRIDOR_SOURCE_PATH}; {RUNE_MYSTERIES_AUBURY_SOURCE_PATH}",
            consumed_inventory=(("Research package", 1),),
            produced_inventory=(("Research notes", 1),),
            auto_actions=("Deliver Sedridor's package to Aubury",),
        ),
        _stage_req(
            5,
            "Return Aubury's research notes to Sedridor.",
            f"{RUNEMYSTERIES_SOURCE_PATH}; {RUNE_MYSTERIES_SEDRIDOR_SOURCE_PATH}; {RUNE_MYSTERIES_AUBURY_SOURCE_PATH}",
            consumed_inventory=(("Research notes", 1),),
            auto_actions=("Return Aubury's research notes to Sedridor",),
        ),
    ),
}

__all__ = (
    'RUNE_MYSTERIES_STAGES',
)
