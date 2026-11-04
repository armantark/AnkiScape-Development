# 04: A queue change shows no popup

**What to build:** When the queue continues, the quest-complete, "Activity locked", "Activity switched off" and Wilderness notices become one event log line and one Review HUD line. Lamp text moves to the line. An entry that cannot start is skipped with a line. The Wilderness confirmation with its kept and lost preview runs at add time. The old popup text runs only when the queue has nothing left to continue with. Also fix the adjacent items the spec names: the "Now" label, the stale panel after a takeover, the missing "Queue: <name> done" line, and "1 reviews remaining". Grill answers 7 and 17.

**Blocked by:** 01

**Status:** built; native Anki check waits for the orchestrator

- [x] Played: Pirate's Treasure completes with a next entry; no dialog appears, and the line reads "Pirate's Treasure complete. Next: <entry>." plus lamp text when lamps wait.
- [x] Played: the same quest with nothing next shows the popup with its old text.
- [x] A locked entry is skipped with a line, and the next entry runs in the same review.
- [x] A Wilderness add shows the confirmation; declining adds nothing. A gear change before the entry starts skips it with a line and no dialog.
- [x] Offscreen PNG of the Review HUD line, dark and light; no clipped text.
