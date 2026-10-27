# 06: Move the combat setup panel into its own module

**What to build:** Prefactor with no visible change: the combat setup panel, everything from "Combat mode" to "Current target" including the advanced preset editor and the loot rules, moves out of the main menu module into its own module, so that ticket 07 can rebuild it without growing the main menu file.

**Blocked by:** None (can start immediately)

**Status:** open

- [ ] The panel's offscreen captures before and after the move match at 560 points tall.
- [ ] The existing combat panel tests pass unchanged.
- [ ] The main menu file shrinks by the moved block.
