"""Pinned ordinary-dialogue facts and owner-selected Anki review pacing."""

QUEST_ID = "mournings_end_part_i"
REPAIR_STAGE = 3
DAMAGED_TROUSERS = "Mourner trousers (damaged)"
REPAIRED_TROUSERS = "Mourner trousers (repaired)"
REPAIR_INPUTS = ((DAMAGED_TROUSERS, 1), ("Silk", 2), ("Bear fur", 1))
PENDING_KEY = "mournings_end_part_i_oronwen_pending"
REPAIR_EVENT = ("quest_service", "oronwen_repair")
MOURNER_ENCOUNTER = "mournings_end_part_i_mourner_11"

_SOURCE_ROOT = "/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/0200-oronwen-trouser-repair/sources/"
WALKTHROUGH_SOURCE = "https://runescape.wiki/w/index.php?title=Mourning%27s_End_Part_I&oldid=6579284"
STATE_SOURCE = "https://runescape.wiki/w/index.php?title=Mourner_trousers&oldid=6392876"
GUIDE_SOURCE = "https://web.archive.org/web/20111129165708id_/http://www.zybez.net/quests/87/mournings_ends_part_i/"
REPAIR_STAGE_SOURCE = f"{WALKTHROUGH_SOURCE} lines 79, 81, 95; {GUIDE_SOURCE} text lines 44–53"

PERIOD_SOURCES = (
    dict(url=WALKTHROUGH_SOURCE, timestamp="2012-11-18T19:24:14Z",
         passages="79, 81: fight before repair; 95: two silk, one bear fur and trousers in custody",
         body_path=_SOURCE_ROOT + "mournings-end-part-i-6579284.txt",
         sha256="ab04ab921d538f7b7039a0dd824af3d0b948219d774e20a977ae885c3942651c"),
    dict(url=STATE_SOURCE, timestamp="2012-10-13T03:34:23Z",
         passages="17, 23: damaged/repaired states; 9, 11: non-tradeable, non-stackable",
         body_path=_SOURCE_ROOT + "mourner-trousers-6392876.txt",
         sha256="11d6a3cfa037d1c58e425e4b347a2094c5a5db222892fb159651b7df250d59ca"),
    dict(url=GUIDE_SOURCE, timestamp="2011-11-29T16:57:08Z",
         passages="text 44–53: fight, hand over trousers, speak again to collect",
         body_path=_SOURCE_ROOT + "zybez-guide-20111129165708.html",
         sha256="58ed829c43a46bd37f3056bdddf8df7a28f82a3584a750f441578e15cbe7679f",
         text_body_path=_SOURCE_ROOT + "zybez-guide-20111129165708.txt",
         text_sha256="43202a803e27fd03ef4ec43577d1f6e71588835d6a40d3b38c62f0073cdf5f90"),
)
OWNER_DECISIONS = (
    ("2026-10-20 18:59 PDT", "One additional eligible Anki quest review; no elapsed timer."),
    ("2026-10-20 18:38 PDT", "No Crafting gate, needle/thread requirement or consumption, or Crafting XP."),
)
UNRESOLVED_SOURCE_NOTES = (
    "Period one-minute and just-under-two-minute accounts conflict; neither sets runtime duration.",
    "W1–W7/G1–G6 bounded search found no repair-specific crafting values; owner decisions are not verified period absences.",
    "https://runescape.wiki/w/index.php?title=Oronwen&oldid=6288788, 2012-09-24T05:59:29Z, line 17; "
    + _SOURCE_ROOT + "oronwen-6288788.txt: special use-item account keeps trousers and prepays a free repair. Unresolved and excluded.",
    "State suffixes distinguish attested states, not period page titles. Numeric, model, equipment and cache state bindings remain unproven.",
    "Relocated encounter retains existing combat parameters; these sources do not newly verify them.",
)
ORONWEN_REPAIR_ITEMS = {
    name: dict(category="material", stackable=False, tradeable=False, source=STATE_SOURCE)
    for name in (DAMAGED_TROUSERS, REPAIRED_TROUSERS)
}
