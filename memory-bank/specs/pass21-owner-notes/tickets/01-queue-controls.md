# 01: Queue chevrons, entry 1 remove, move flash and the stale Next line

**What to build:** The Chevrons, Remove entry 1, Move confirmation and HUD Next line decisions in the spec.

**Blocked by:** None (can start immediately)

**Status:** claimed by claude-opus-5-5 on goal/pass21-01

- [ ] Real widget flow: chevrons show, disabled at the ends, with no cut text at the default size and 560 tall, dark and light.
- [ ] Played: remove a running entry 1 and the next entry runs on the next card; remove the last entry and the queue ends at Bankstanding; a paused queue only changes its list; undo restores.
- [ ] A move flashes the destination row, and a refused move does not.
- [ ] Reproduce "Pirate's Treasure complete. Next: Combat." then a move: the HUD line clears and the Event log keeps it.
