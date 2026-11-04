# 10: The route-checked item stops become supply steps

**What to build:** The rows of `route-check.tsv` with verdict `fold` become supply steps, as in ticket 09. The orchestrator produces that file with one structured call per row over the 47 unresolved class A rows in the 67 quests. Rows with other verdicts stay as they are and go in the report. Grill answer 20.

**Blocked by:** 09

**Status:** built; native Anki look waits for the orchestrator

- [x] Each folded quest plays past its row through the real handler with an empty bank, holding only what `player brings` rows name.
- [x] A table in the report gives each row's step, price, XP and period source quote, and the rows not folded with their reasons.
- [x] The item-reachability census moves by exactly this change.

Source decisions and exclusions: `memory-bank/source-audits/pass20-route-item-supplies-2026-11-04.md`. Thirteen of the seventeen fold candidates are built; the two Hazeel Cult candidates, Dealing with Scabaras and Defender of Varrock are excluded for their remaining required actions or unmodelled fight. The focused handler tests pass. The broader selection retains six widget expectations that also fail on the integration baseline; details are in the ticket 10 report.
