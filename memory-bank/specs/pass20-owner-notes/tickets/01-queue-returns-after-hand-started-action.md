# 01: The queue returns after a hand-started action

**What to build:** A manual pause and a hand-started action become different queue states. An action started ahead of the queue runs until it stops by itself, and the queue continues from its top entry, with no Bankstanding between them. A free pickup runs until Stop or an add, and Stop returns to the queue. Stop on a running entry pauses at Bankstanding. A hand start from a paused queue leaves it paused. A finished quest removes every entry for that quest in the same review. Skill entries count only work done while they run. Grill answers 1 and 6.

**Blocked by:** None (can start immediately)

**Status:** claimed by gpt-6.1-sol on goal/pass20-01

- [ ] Played through the review handler: a hand-started Mining ahead of a two-entry queue runs out of supplies, and the next card runs the top entry.
- [ ] A hand-run quest that completes leaves the queue in that review, with all its entries, and the queue continues or stays paused by its earlier state.
- [ ] A free pickup ahead of the queue stops only on Stop or add; Stop starts the top entry.
- [ ] Stop on a running entry ends at Bankstanding and the queue stays paused; a hand start then leaves it paused.
- [ ] Clear ends at Bankstanding. An old save's `paused` queue stays paused.
- [ ] A Monte Carlo sweep of add, hand-start, Stop, Clear and finish sequences holds the spec's invariants.
