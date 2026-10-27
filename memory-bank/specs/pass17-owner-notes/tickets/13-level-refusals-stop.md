# 13: Level refusals switch to Bankstanding, so a queue passes on

**What to build:** About ten skill handlers (Crafting, Fletching, Herblore, Smithing, Mining, Woodcutting, Fishing, Hunter, Firemaking, Summoning) answer a target above the player's level, or one whose potion boost has worn off, with an "Insufficient level" pop-up on every card and never switch to Bankstanding. The owner's Pass 11 ruling is that every refusal becomes Bankstanding ("I think everything should just become bankstanding", `memory-bank/codex-briefs/pass11-owner-notes-handoff-2026-08-22.md:28-29`). With the action queue (ticket 03) the stall is worse: a queued or resumed entry above the player's level stops the whole queue with a pop-up every card instead of passing to the next entry. Route each level refusal through the shared switch to Bankstanding with its reason, so the queue's stop takeover passes to the next entry and Resume shows the reason.

**Blocked by:** None (can start immediately)

**Status:** open

- [ ] Each of the listed handlers, given a target above the player's level through the real review handler, switches to Bankstanding once with the level reason and shows no repeated pop-up.
- [ ] A two-entry queue whose first entry is above the player's level gives that entry's notice and starts the second entry.
- [ ] The last action record keeps the level reason, so the review HUD shows it beside Resume.
