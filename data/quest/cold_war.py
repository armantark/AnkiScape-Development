from .contract import QuestStage, QuestStageRequirementCleanup
from ...generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG


COLD_WAR_SOURCE = "https://runescape.wiki/w/index.php?title=Cold_War&oldid=6579802"
# AnkiScape owner decisions, 2026-10-20: 18:35 removes book reading and
# possession gates; 19:00 supplies one Bank suit and automatic disguise changes.
# This automatic grant supersedes manufacture; it is an AnkiScape adaptation.
COLD_WAR_ADAPTATION_SOURCE = (
    COLD_WAR_SOURCE
    + "; AnkiScape owner decisions 2026-10-20 18:35 PDT and 19:00 PDT: "
    "automatic suit grant and disguise changes; no book reading or possession gate"
)
COLD_WAR_STAGE_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_inventory=("Plank", "Silk", "Steel bar", "Clockwork mechanism"),
        remove_required_actions=("Complete Cold War stage 1 objective",),
        add_auto_actions=("Receive the Clockwork book from Larry",),
        source=COLD_WAR_ADAPTATION_SOURCE,
    ),
    QuestStageRequirementCleanup(
        stage=2,
        remove_required_inventory=("Crafting table 3",),
        remove_required_actions=("Complete Cold War stage 2 objective",),
        add_auto_actions=("Receive the Clockwork suit and test the penguin disguise with Larry",),
        add_produced_inventory=(("Clockwork suit", 1),),
        source=COLD_WAR_ADAPTATION_SOURCE,
    ),
)

# The manufacture-output ID is unresolved and intentionally unmapped.
# Neither cache variant is selected: the owner approved one combined Bank item.
COLD_WAR_SUIT_ITEMS = {
    "Clockwork suit": {
        "category": "material",
        "stackable": False,
        "tradeable": False,
        "source": (
            "https://runescape.wiki/w/index.php?title=Clockwork_suit&oldid=6424777; "
            "OpenRS2 cache 544/build 742 definitions 10595 and 10596; "
            "AnkiScape owner's combined representation, 2026-10-20 19:00 PDT"
        ),
    },
}

COLD_WAR_UNLOCKS = (
    "Penguin disguise changes are handled automatically during Cold War.",
    "Ability to use the Penguin Agility Course",
    "Ability to contact Larry through the NPC Contact spell.",
)


def _adapt_journal_stage(raw_stage):
    stage = raw_stage["stage"]
    journal = list(raw_stage["journal"])
    if stage == 1:
        journal[5] = journal[5].replace(
            "by creating a penguin clockwork suit.",
            "by using a penguin clockwork suit.",
        ).replace(
            "He gives you a book filled with instructions on how to make one.",
            "Larry gives you the Clockwork book. You do not need to read or carry it; "
            "the suit is supplied automatically during the next stage.",
        )
    elif stage == 2:
        journal[0] = (
            "Completing this stage grants one Clockwork suit to your Bank automatically. "
            "Crafting materials, a crafting table, and reading or carrying the Clockwork "
            "book are not required. Disguise changes are handled automatically."
        )
        journal[2] = journal[2].replace(" after finishing the suit", "")
        journal[3] = journal[3].replace(
            "Free your hands and cape and talk to Larry. He casts a magic spell, "
            "causing the player to shrink and enter the penguin suit!",
            "Larry handles your penguin disguise automatically; your equipment stays in place.",
        )
        del journal[1]
    elif stage == 3:
        journal[0] = journal[0].replace(
            "Exit the enclosure and speak to Larry to get out of the suit.",
            "Exit the enclosure; your disguise changes automatically.",
        )
        journal[1] = journal[1].replace(
            "; use the 'tuxedo-time' option with him.",
            ". Your penguin disguise is handled automatically.",
        )
        journal[3] = journal[3].replace(
            "Re-tuxedo before entering the penguin enclosure and speak to the penguin again.",
            "Your penguin disguise changes automatically when you enter the enclosure. "
            "Speak to the penguin again.",
        )
    elif stage == 4:
        journal[0] = journal[0].replace(
            " and penguin suit up!", ". Your penguin disguise is handled automatically.",
        )
        journal[3] = journal[3].replace(
            "Wear the penguin disguise again and head north-west",
            "Your penguin disguise changes automatically. Head north-west",
        )
    elif stage == 5:
        journal[1] = "Disguise changes are automatic. The Clockwork suit remains in your Bank."
        journal[3] = journal[3].replace(
            "Have Larry put you back into the suit and return to the outpost",
            "Your disguise changes automatically. Return to the outpost",
        )
    elif stage == 6:
        journal[2] = journal[2].replace(
            "The penguins in the room take your suit, and you are teleported to a cage "
            "filled with Icelords.",
            "Your disguise is exposed, and you are teleported to a cage filled with Icelords.",
        )
    return QuestStage(stage, tuple(journal))


COLD_WAR_JOURNAL_STAGES = tuple(
    _adapt_journal_stage(stage)
    for quest in PRE_EOC_QUEST_CATALOG if quest["id"] == "cold_war"
    for stage in quest["journal_stages"]
)
