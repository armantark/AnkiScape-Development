# 09: The GE offer panel stays whole with a full queue box

**What to build:** With the queue box at 2 and 5 entries, at the default menu size and 560 points tall, every GE offer control (Offer, Quantity, Price each, -5%, Guide, +5%, the total line, Place offer) keeps its full height and the GE page scrolls. Fix whatever still squeezes it. See spec "GE with a full queue box".

**Blocked by:** 03 (The queue box shows every entry, folds, and confirms each add)

**Status:** open

- [ ] The macOS layout test runs the GE tab with the queue box at 2 and 5 entries at both sizes and finds no squeezed control.
- [ ] The orchestrator's native look with a 5-entry queue shows the Woad leaf offer panel whole in real Anki.
