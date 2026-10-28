"""Authored Animal Magnetism opening; paraphrases, not recovered dialogue."""

from ....contract import QuestStage, QuestStageRequirementCleanup
from ......generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG

# Retained evidence (paths relative to the evidence directory):
# /Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/
# 1460-animal-magnetism-candle-sconce-and-ava-s/
# Animal Magnetism revision 6571937, 2012-11-18T06:20:52Z: original
# line 69 supplies Search, access, commission, two and alive; lines 71–79
# separate the later poultry chain. sources/animal-magnetism-6571937.txt
# SHA-256 8510ddb556d2734505ac7a480692997462da0e8157005fc68740d198ba2343c7
# Quick guide revision 6333622, 2012-10-02T13:49:39Z: lines 36–41 separate
# Getting Started from Undead Poultry; line 37 says "must be pulled".
# Same wiki lineage, not independent corroboration. Search is the chosen verb.
# sources/animal-magnetism-quick-guide-6333622.txt
# SHA-256 828289b861a8b074ad45d311e64ce2a2f993fde700c6ba395d1855da601c8c5f
# Tip.It capture 20121119220934, 2012-11-19T22:09:34Z: HTML line 256
# independently corroborates Search, access and Ava's request; line 253
# lists no opening items. sources/tipit-20121119220934.html
# SHA-256 6c42e3dbbde162f7c23063bef92e8958c3d19a4802db921978f90867bf213541
# RuneHQ capture 20121103161628, 2012-11-03T16:16:28Z: HTML line 255
# corroborates Search, access and two chickens. sources/runehq-20121103161628.html
# SHA-256 715c9dfec456a44c111e4a6a4edf5e18740cfe5964fa13e732d2e8404be8ea91
# Sal's capture 20121018050430, 2012-10-18T05:04:30Z: HTML lines 206–208
# independently corroborate searching and two chickens that must be alive.
# sources/sals-20121018050430.html
# SHA-256 961d0c8d4ea30557e3eb63b66f5af0b6057f55533788b9ebc966fe45a03e9ef9
# Retained build-727 configuration also says Search; six-build receipt:
# sources/cache-six-builds-retained.json
# SHA-256 2348d3a10d149fd33b83ab531c7e0335f6a98e1b7eaf3d811e263bfcf6b8298e
# Configuration corroboration, not an Anki transaction specification.
# Darkan 517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed corroborates passage and
# commission, but has no durable sconce-performance flag. Passage commit
# c6fbe036b1743f4dd6067ec178332c69c3708856 is dated 2021-06-16; commission
# restoration 91676dbbb64864762cde650122e356d081e63e44 is dated 2026-07-16.
# This is not period server proof. Retained configured-667 game-main search
# found no opening handler. Exact dialogue, hidden mechanics and historical
# recovery remain not stated. Review/proof/Undo/save semantics are app design.
# Template:Questreq revision 6552449 lines 16–18 and independently captured
# guides also list Priest in Peril. This slice preserves current admission
# per the brief, without claiming full prerequisite parity. The disputed
# Thieving/buttons qualification remains unresolved outside this slice.

SOURCES = (
    "https://runescape.wiki/w/index.php?title=Animal_Magnetism&oldid=6571937",
    "https://runescape.wiki/w/index.php?title=Animal_Magnetism%2FQuick_guide&oldid=6333622",
    "https://web.archive.org/web/20121119220934id_/http://www.tip.it:80/runescape/index.php?rs2quest_id=152",
    "https://web.archive.org/web/20121103161628id_/http://www.runehq.com:80/quest/animal-magnetism",
    "https://web.archive.org/web/20121018050430id_/http://runescape.salmoneus.net/quests/animal-magnetism.html",
)

SCONCE_ACTION = "Search the candle sconce to enter Ava's room"
COMMISSION_ACTION = "Accept Ava's request for two living undead chickens"
OPENING_ACTIONS = (SCONCE_ACTION, COMMISSION_ACTION)
PENDING_OPENING = "Search the candle sconce to enter Ava's room, then speak with Ava about helping her home."
COMPLETED_OPENING = "I searched the candle sconce to reach Ava. She asked me to bring her two living undead chickens."

ANIMAL_MAGNETISM_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_actions=("Complete Animal Magnetism stage 1 objective",),
        add_auto_actions=OPENING_ACTIONS,
        source="; ".join(SOURCES),
    ),
)

ANIMAL_MAGNETISM_JOURNAL_STAGES = tuple(
    QuestStage(
        stage=row["stage"],
        journal={
            1: (PENDING_OPENING,),
            2: (
                "With a Ghostspeak amulet equipped, head to the farm West of the Ectofuntus.",
                "Talk to Alice.",
            ),
        }.get(row["stage"], tuple(row["journal"])),
    )
    for quest in PRE_EOC_QUEST_CATALOG
    if quest["id"] == "animal_magnetism"
    for row in quest["journal_stages"]
)
