# 01: The queue makes exactly the count the player picks

**What to build:** A queued entry makes exactly its count in every unit. The card's steps stop when the entry's remainder is reached, the step that reaches it makes only the remainder, and the rest of the card goes to the next entry (a skill or utility entry in the same card; a combat or quest entry on the next card; Bankstanding when none is left). Kill entries stop at their count like a Slayer task's last kill. See spec "Action queue: exact counts".

**Blocked by:** None (can start immediately)

**Status:** claimed by Opus 5.5 implementer on goal/pass18-01-queue-exact-counts

- [ ] Queuing 3 Goblin mail, 3 Redberries and 28 Onion at 10x, as the owner did, gives 3, 3 and 28, and the three entries finish in fewer cards than before.
- [ ] A queued 1 Iron platebody at 10x makes 1; the rest of that card runs the next entry.
- [ ] A kill entry stops at its count, also inside one combat burst; with a Slayer task, the smaller cap wins.
- [ ] A Monte Carlo sweep over every queueable skill target, utility and combat target the seeded bank can run, random counts from 1 to three batches, speeds 1x, 5x and 10x: every entry ends at exactly its count or stops short with a reason. Its table is saved under the evidence folder.
- [ ] The tests that pinned the overshoot now pin the exact count.
