# 10: The route-checked item stops become supply steps

**What to build:** The rows of `route-check.tsv` with verdict `fold` become supply steps, as in ticket 09. The orchestrator produces that file with one structured call per row over the 47 unresolved class A rows in the 67 quests. Rows with other verdicts stay as they are and go in the report. Grill answer 20.

**Blocked by:** 09

**Status:** open

- [ ] Each folded quest plays past its row through the real handler with an empty bank, holding only what `player brings` rows name.
- [ ] A table in the report gives each row's step, price, XP and period source quote, and the rows not folded with their reasons.
- [ ] The item-reachability census moves by exactly this change.
