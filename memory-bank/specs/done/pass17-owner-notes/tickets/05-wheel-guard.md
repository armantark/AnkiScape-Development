# 05: Mouse wheel guard for number boxes

**What to build:** In every AnkiScape window and dialog, the mouse wheel never changes a number box; the wheel event goes to the scroll area under the pointer, so the page scrolls. One event filter, installed by AnkiScape's own windows and dialogs and never on Anki's own widgets, covers every number box, including boxes built in loops, without edits at each construction site. First check, in Anki's own widget style, whether the wheel changes a drop-down list; if it does, the same filter covers drop-down lists.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] An offscreen test sends a wheel event over a number box inside a scroll area: the value stays and the scroll area moves.
- [x] The guard covers the Settings game speed and world-day boxes, a Grand Exchange box and a box built in a loop.
- [x] The drop-down list finding is recorded in the ticket, with the guard covering lists when the wheel changes them.
- [x] One play-checklist line added.

**Drop-down finding:** Anki's default widget style ("Anki") is Fusion, and Fusion
lets the wheel change a drop-down list (`SH_ComboBox_AllowWheelScrolling` is 1
for Fusion and Windows, 0 only for the native macOS style). A probe confirmed
it: an unguarded Fusion list moved from item 1 to item 2 under the wheel. The
guard therefore covers drop-down lists too.
