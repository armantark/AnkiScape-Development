"""The performed chapel opening; subsequent workshop requirements stay intact."""

from .contract import QuestStage, QuestStageRequirement

QUEST_ID = "elemental_workshop_iii"
RAGGED_BOOK = "Ragged book"
ACQUIRE_PROOF = "Search the chapel bookcase and obtain the Ragged book"
READ_PROOF = "Read the Ragged book"
ACQUIRE_EVENT = ("quest_service", "elemental_workshop_iii_chapel_acquire")
READ_EVENT = ("quest_service", "elemental_workshop_iii_ragged_book_read")

WIKI_SOURCE = "https://runescape.wiki/w/Elemental_Workshop_III?oldid=6448817"
TIPIT_SOURCE = (
    "https://web.archive.org/web/20120825005143id_/"
    "http://www.tip.it:80/runescape/index.php?rs2quest_id=219"
)
OPENING_SOURCE = f"{WIKI_SOURCE}:53; {TIPIT_SOURCE} HTML:245, text:69,82"
ELIGIBILITY_SOURCE = (
    f"{WIKI_SOURCE}:29–32 (all skills can be boosted); {TIPIT_SOURCE} text:71–72; "
    "https://runescape.wiki/w/Template:Questreq?oldid=6552449:282–284"
)
PREPARATION_SOURCE = (
    f"{WIKI_SOURCE}:34–40,53–66; {TIPIT_SOURCE} text:82–86. "
    "Mould-order disagreement: wiki makes the mould after workshop entry; "
    "Tip.It makes it before entry. Neither order is performed by this opening."
)

OPENING_JOURNAL = (
    "Search the bookcase in Seers' Village chapel to obtain the Ragged book, then read it.",
)
PREPARATION_JOURNAL = (
    "Next, take the Ragged book into the workshop through the odd-looking wall in the anvil house.",
    "Workshop access needs the Battered key, a Knife to recover it, or a Steel key ring containing that key.",
    "For the later preparation, use a Pickaxe and Hammer, obtain 3 elemental ores, and use 12 Coal to smelt 3 elemental bars. A toolbelt Hammer works.",
    "After reading the Ragged book, use one Soft clay with it to make a Key mould. Use one elemental bar with the mould to make the Ragged elemental key.",
    "Prime the remaining two bars; do not make mind bars. Unlock the Body door before working the puzzle.",
)

RAGGED_BOOK_ITEMS = {
    RAGGED_BOOK: {
        "category": "material",
        "item_id": 18685,
        "model_id": 57485,
        "stackable": False,
        "tradeable": False,
        "inventory_options": ("Read", None, None, None, "Destroy"),
        "examine": "Book of the Elemental Body, there is a raised relief on the front.",
        "source": (
            "https://runescape.wiki/w/Ragged_book?oldid=6154831:3,9,11,15,18,22; "
            "OpenRS2 309/build 727 and 544/build 742 item 18685, model 57485"
        ),
    },
}


def compose_opening(quest_id, requirements, journal):
    """Replace only the two opening projections, retaining later row objects."""
    if quest_id != QUEST_ID:
        return requirements, journal
    opening = QuestStageRequirement(
        stage=1,
        description="Search the bookcase in Seers' Village chapel and read the Ragged book.",
        required_actions=(READ_PROOF,),
        source=OPENING_SOURCE,
    )
    requirements = tuple(opening if row.stage == 1 else row for row in requirements)
    replacements = {1: OPENING_JOURNAL, 2: PREPARATION_JOURNAL}
    journal = tuple(
        QuestStage(row.stage, replacements[row.stage]) if row.stage in replacements else row
        for row in journal
    )
    return requirements, journal
