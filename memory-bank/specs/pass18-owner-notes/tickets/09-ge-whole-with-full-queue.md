# 09: The GE offer panel stays whole with a full queue box

**What to build:** With the queue box at 2 and 5 entries, at the default menu size and 560 points tall, every GE offer control (Offer, Quantity, Price each, -5%, Guide, +5%, the total line, Place offer) keeps its full height and the GE page scrolls. Fix whatever still squeezes it. See spec "GE with a full queue box".

Added by the orchestrator after the native check of ticket 03 (`/Users/armantarkhanian/Code/ankiscape-pass18/native/check-03/`, verdict notes and screenshots 10 to 14): in real Anki the GE panel already stayed whole with 5 entries at both heights, but at the 720-point minimum width the Smithing target list cut "Bronze bolts (unf) (Lvl 3) — m..." and "Bronze arrowtips (Lvl 5) — ma..." with Qt's default elision and no hover text. Four Smithing rows were already cut at 720 before Pass 18; the full queue box's page scroll bar adds a fifth. A skill target row shows its whole text at any menu size the dialog allows, by wrapping or by a layout that gives the list the width, not by elision.

**Blocked by:** 03 (The queue box shows every entry, folds, and confirms each add)

**Status:** claimed by Opus 5.5 implementer on goal/pass18-09-full-queue-pages

- [ ] The macOS layout test runs the GE tab with the queue box at 2 and 5 entries at both sizes and finds no squeezed control.
- [ ] No skill target list row (Smithing and every other skill's target list) is cut or elided at 720 x 540 and 720 x 560, with an empty queue and with the queue box at 5 entries; a Qt test checks every skill's list with text_fit_defects.
- [ ] The orchestrator's native look with a 5-entry queue shows the Woad leaf offer panel and the Smithing list whole in real Anki.
