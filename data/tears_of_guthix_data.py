"""Period-pinned Tears of Guthix Distraction and Diversion data.

Every value below is stated by a pinned pre-cutoff revision, except the one
marked placeholder and one AnkiScape mapping that is called out where it is
used. The 6 November 2012 "Go with the Flow" refresh is the cutoff state, so
the ornate bowl and the refreshed caps are in scope.
"""

from __future__ import annotations

from typing import Any


TEARS_OF_GUTHIX_ACTIVITY_ID = "tears_of_guthix"
TEARS_OF_GUTHIX_QUEST_ID = "tears_of_guthix"

TEARS_OF_GUTHIX_SOURCE = (
    "https://runescape.wiki/w/Tears_of_Guthix?oldid=6579712 "
    "(2012-11-19T02:37:17Z); "
    "https://runescape.wiki/w/Update:Tears_of_Guthix:_Go_with_the_Flow "
    "(2012-11-06); "
    "https://runescape.wiki/w/Ornate_bowl?oldid=6555677 (2012-11-14T21:40:33Z); "
    "memory-bank/source-audits/tears-of-guthix-cutoff-reconciliation-2026-07-17.md"
)

# "Waited at least 7 days" — one simulated week on the shared answered-card
# calendar, the same clock every other recurring activity reads.
TEARS_OF_GUTHIX_WEEK_REVIEWS = 1_680

# AnkiScape's recurring-entry carryover, not a period rule: one current entry
# plus one reserve, the default cap from `simulation-time-boundary-2026-07-16.md`
# Decision 2. The period record states "once per week" and says nothing either
# way about missed weeks, so nothing here claims the game banked entries.
TEARS_OF_GUTHIX_ENTRY_CAP = 2

# "Earned at least 100,000 total experience or one quest point since they last
# participated (unless they have never played before)."
TEARS_OF_GUTHIX_PROGRESS_EXP = 100_000.0
TEARS_OF_GUTHIX_PROGRESS_QUEST_POINTS = 1

# "The time a player has is the player's Quest Points in Ticks which is 0.6 of a
# second." / "The maximum a player can have is 3 minutes."
TEARS_OF_GUTHIX_TICKS_PER_QUEST_POINT = 1
TEARS_OF_GUTHIX_MAX_COLLECTION_TICKS = 300
TEARS_OF_GUTHIX_SECONDS_PER_TICK = 0.6

# AnkiScape mapping, not a period value: one answered card advances six game
# ticks, the same cadence the live Combat activities already use. It is what
# turns a 300-tick cavern timer into a finite run of review beats.
TEARS_OF_GUTHIX_TICKS_PER_REVIEW = 6

# "Level * 6 = Xp. The experience per tear is capped at 180" / "capped at 300
# for those who have made an ornate bowl".
TEARS_OF_GUTHIX_XP_PER_LEVEL = 6
TEARS_OF_GUTHIX_STONE_BOWL_XP_CAP = 180
TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP = 300

# "requiring 80 Mining and 80 Crafting ... Boosts cannot be used to create the
# bowl." The chisel is the stated tool.
ORNATE_BOWL_MINING_LEVEL = 80
ORNATE_BOWL_CRAFTING_LEVEL = 80
ORNATE_BOWL_TOOL = "Chisel"

# The streams themselves: "There are 3 spots with green tears and 3 spots with
# blue tears at all times", blue adds to the count and green subtracts, and the
# switching is "random and quite fast". No period source states a collection
# rate or a green-catch probability, and AnkiScape has no positional layer for
# the player to dodge a stream with, so both are hidden rolls.
TEARS_OF_GUTHIX_BLUE_SPOTS = 3
TEARS_OF_GUTHIX_GREEN_SPOTS = 3
# Darkan TearsOfGuthix.kt:496-510 accepts at most one collection update per
# server tick and adds exactly one tear for a blue stream.
TEARS_OF_GUTHIX_TEARS_PER_TICK = 1
# PLACEHOLDER(tears_of_guthix.green_tear_chance): the authentic stream-rotation
# cadence, selection rule, and player catch/movement policy. The cutoff page and
# its talk revision 6539293 expose observations but no probability; Darkan's
# restored controller deliberately leaves rotation source-blocked. The 267-tear
# record is therefore only a weak anchor for this reachability value.
TEARS_OF_GUTHIX_GREEN_TEAR_CHANCE = 0.055


def tears_of_guthix_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        TEARS_OF_GUTHIX_ACTIVITY_ID: {
            "display_name": "Tears of Guthix",
            "requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": TEARS_OF_GUTHIX_SOURCE,
        }
    }
