# 01: Quests that cannot be finished show "Coming soon"

**What to build:** A generated set of Coming soon quests, taken from the reachability audit and pinned to it by a test. Each Coming soon quest gets the start lock reason "Coming soon", so the Quests tab disables Start and "Hide unable to start" hides it. A started Coming soon quest keeps its saved state, shows the same label, and cannot continue. See spec "Which quests are Coming soon" and the glossary's "Coming soon".

**Blocked by:** None (can start immediately)

**Status:** not started

- [ ] Monkey Madness shows "Coming soon" on the Quests tab, and its Start button is disabled.
- [ ] "Hide unable to start" hides Monkey Madness and does not hide Cook's Assistant.
- [ ] A save with Monkey Madness started keeps its stage, shows "Coming soon", and its Continue button and quest reviews are refused.
- [ ] A test fails when the generated set differs from the live audit's completable quests.
- [ ] The label shows whole at 560 points tall in light and dark mode.
