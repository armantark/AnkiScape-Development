"""Source-backed opening transactions; review boundaries are application choices."""

from .contract import QuestStageRequirement

QUEST_ID = "the_grand_tree"
BARK_SAMPLE = "Bark sample"
TRANSLATION_BOOK = "Translation book"
HAZELMERES_SCROLL = "Hazelmere's scroll"

P1 = "Receive Narnode's commission, Bark sample and Translation book"
P2 = "Have Hazelmere examine the Bark sample and receive Hazelmere's scroll"
P3 = "Translate Hazelmere's scroll with the Translation book"
P4 = "Report Hazelmere's translated message to Narnode"
P5 = "Warn Glough of the Daconia rocks and hear his instruction to report back"
PROOFS = (P1, P2, P3, P4, P5)
EVENTS = tuple(("quest_service", "grand_tree_" + name) for name in (
    "commission", "examination", "translation", "report", "warning",
))
EVENT_RULES = {event: (PROOFS[:index], (PROOFS[index],)) for index, event in enumerate(EVENTS)}
REVIEW_BUNDLES = {
    "commission": (EVENTS[0],),
    "examination": (EVENTS[1],),
    "translation": (EVENTS[2],),
    "report_warning": (EVENTS[3], EVENTS[4]),
}

W = "https://runescape.wiki/w/The_Grand_Tree?oldid=6450823"
T = "https://web.archive.org/web/20121119221116id_/http://www.tip.it:80/runescape/index.php?rs2quest_id=33"
H = "https://web.archive.org/web/20121107193758id_/http://www.runehq.com:80/quest/grand-tree-the"
STAGE_SOURCES = {
    1: f"{W}:42,44,56; {T}:252,254; {H}:251,261; Bark sample oldid 5912140:23; Hazelmere's scroll oldid 6154711:20. Owner: examination requires bark only; retain book.",
    2: f"{W}:58–62,67,69,71; {T}:254,256,260; {H}:261,271,278; Translation book oldid 6162857:22; Hazelmere's scroll oldid 6154711:25–33. Scroll removal not stated; retain book and scroll.",
}
ITEM_ID_SOURCE = (
    "Darkan data/items/config.json @ 43c971faa9f3947f18db7269c80560e4be46de27 "
    "(2022-09-14T22:47:43Z); OpenRS2 cache 309/build 727 (2012-07-24) and "
    "cache 544/build 742 (2012-11-07); upstream configuration, not a period transaction"
)
GRAND_TREE_OPENING_ITEMS = {
    BARK_SAMPLE: {
        "category": "material", "item_id": 783, "stackable": False, "tradeable": False,
        "examine": "A sample of the bark from the Grand Tree.",
        "source": f"https://runescape.wiki/w/Bark_sample?oldid=5912140:17; {ITEM_ID_SOURCE}",
    },
    TRANSLATION_BOOK: {
        "category": "material", "item_id": 784, "stackable": False, "tradeable": False,
        "examine": "A book to translate the ancient gnome language into English.",
        "source": f"https://runescape.wiki/w/Translation_book?oldid=6162857:18; {ITEM_ID_SOURCE}",
    },
    HAZELMERES_SCROLL: {
        "category": "material", "item_id": 786, "stackable": False, "tradeable": False,
        "examine": "Hazelmere wrote something down on this scroll.",
        "source": f"https://runescape.wiki/w/Hazelmere%27s_scroll?oldid=6154711:17; {ITEM_ID_SOURCE}",
    },
}
PHASE_NOTICES = {
    "commission": "Narnode asked you to investigate the dying tree. Received 1 Bark sample and 1 Translation book.",
    "examination": "Hazelmere examined 1 Bark sample and gave you 1 Hazelmere's scroll.",
    "translation": "Used the Translation book to translate Hazelmere's scroll.",
    "report_warning": "Reported Hazelmere's translated message to Narnode and received his request to warn Glough. Warned Glough; he said he would handle the problem and told you to report back to Narnode.",
}


def compose_grand_tree_requirements(quest_id, requirements):
    """Replace only opening requirements; retain later objects and journal owners."""
    if quest_id != QUEST_ID:
        return requirements
    opening = {
        1: QuestStageRequirement(
            stage=1,
            description="Receive Narnode's commission and take the Bark sample to Hazelmere for examination.",
            required_actions=(P1, P2), source=STAGE_SOURCES[1],
        ),
        2: QuestStageRequirement(
            stage=2,
            description="Translate Hazelmere's scroll, report to Narnode and warn Glough.",
            required_actions=(P3, P4, P5), source=STAGE_SOURCES[2],
        ),
    }
    return tuple(opening.get(row.stage, row) for row in requirements)
