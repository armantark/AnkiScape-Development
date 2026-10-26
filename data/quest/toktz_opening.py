"""Sourced tablet-to-guide deeds; five reviews and journal copy are AnkiScape choices.

Period witnesses establish order and custody, not original dialogue or atomic
server internals. Transaction safeguards and pre-library recovery are modern
restoration behavior. See toktz_opening_sources.json for pinned excerpts.
"""

from pathlib import Path

from .contract import QuestStageRequirementCleanup

QUEST_ID = "toktz_ket_dill"
TABLET = "Stone tablet (TokTz-Ket-Dill)"
GUIDE = "Tzhaar tourist guide"
SERVICES = (
    "toktz_guard_commission",
    "toktz_grol_tablet",
    "toktz_librarian_referral",
    "toktz_reldo_instruction",
    "toktz_bookcase_search",
)
PROOFS = (
    "Agree to repair the collapsed TzHaar tunnels",
    "Complete Grol's stone tablet and library referral",
    "Receive the TzHaar librarian's Reldo referral",
    "Receive Reldo's palace bookcase instruction",
    "Search the palace bookcase and obtain the TzHaar Tourist Guide",
)
INTERACTIONS = (
    {"service_id": SERVICES[0], "npc_ids": (7746, 7747, 7748), "option": "Agree to help"},
    {"service_id": SERVICES[1], "npc_id": 7749, "option": "Tablet and library referral"},
    {"service_id": SERVICES[2], "npc_id": 7752, "option": "Reldo referral"},
    {"service_id": SERVICES[3], "npc_name": "Reldo", "option": "Palace bookcase instruction"},
    {"service_id": SERVICES[4], "object_id": 31207, "option": "Search"},
)
COMPLETED_LINES = (
    "I agreed to help make the collapsed TzHaar tunnels safe.",
    "Grol's stone tablet listed the materials in TzHaar, and he referred me to the TzHaar library.",
    "The librarian's human books had burnt to ashes. He sent me to Reldo in Varrock.",
    "Reldo told me to search the palace bookcases for the TzHaar Tourist Guide.",
    "I searched the second bookcase from the south on the western wall of Varrock Palace library. I had the TzHaar Tourist Guide when I finished.",
)
PENDING_LINES = (
    "Speak to one of the guards at the collapsed tunnel and agree to help.",
    "Speak to TzHaar-Ket-Grol for his stone tablet and library referral.",
    "Take the stone tablet to TzHaar-Mej-Lor in the TzHaar library.",
    "Ask Reldo in Varrock Palace library about the TzHaar language.",
    "Search the second bookcase from the south on the palace library's western wall for the TzHaar Tourist Guide.",
)
RECOVERY = "toktz_tablet_recovery"
INVALID = "toktz_invalid_opening"
RECOVERY_INSTRUCTION = "Return to Grol for a replacement stone tablet before visiting the librarian."
RECOVERY_MESSAGE = "Grol replaced the missing stone tablet. Take it to the TzHaar librarian."
LEGACY_LINE = "This save has no complete tablet-to-guide opening recorded."
OPENING_SOURCE = (
    "TokTz-Ket-Dill oldid6493266 (2012-10-29T18:11:47Z), lines53–63; "
    "RuneHQ capture20121103195426, lines257,264,271,278; "
    "Tip.It capture20120425170926, lines269–277. "
    "See toktz_opening_sources.json; Darkan ba45bbc92399fe303bc1c054a72040311b52ed77 "
    "(2026-07-18T09:07:18Z) transaction/recovery is modern restoration."
)
OPENING_CLEANUPS = (QuestStageRequirementCleanup(
    stage=1,
    remove_required_inventory=("A crush weapon", "Blocks of stone", "Oak planks"),
    remove_required_tools=("Hammer",),
    remove_required_actions=("Complete TokTz-Ket-Dill stage 1 objective",),
    add_required_actions=(PROOFS[-1],),
    source=OPENING_SOURCE,
),)
OPENING_ITEMS = {
    TABLET: {"category": "material", "item_id": 13243, "stackable": False,
             "tradeable": False, "examine": "A list of items carved onto a stone tablet.",
             "source": "Stone tablet (TokTz-Ket-Dill) oldid5512319; RuneHQ capture20090418134630; build727; " + OPENING_SOURCE},
    GUIDE: {"category": "material", "item_id": 13244, "stackable": False,
            "tradeable": False, "examine": "A book for those who want to visit the TzHaar city.",
            "source": "TzHaar Tourist Guide oldid6154887; RuneHQ capture20090418084844; build727; " + OPENING_SOURCE},
}
OPENING_IMAGES = {
    TABLET: str(Path(__file__).resolve().parent / "assets/toktz_opening/stone_tablet.png"),
    GUIDE: str(Path(__file__).resolve().parent / "assets/toktz_opening/tourist_guide.png"),
}
