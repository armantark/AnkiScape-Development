# Pass 18 run log

Landings on `goal/pass18-integration`, native checks and test lanes, in order.
Times are PDT, 2026-10-28.

| Time | Event | Commit | Result |
|---|---|---|---|
| 00:01 | Spec, tickets, brief | `fe6663b54` | Ten tickets; six ready |
| 00:03 | Ticket 05 on Sol | — | Failed: "Selected model is at capacity." |
| 00:03, 00:04 | Tickets 06 and 05 on Sol | — | Stopped before any change: the brief and the standing contract's section 6 disagreed; brief fixed at `75a16f1fe` |
| 00:09 | Ticket 06 on Sol, second run | — | Failed mid-run on capacity; Opus finished the partial work |
| 00:18 | Ticket 06 landed (Wyson's woad) | `bedb779f0` | 242 focused tests OK; mutation proof red |
| 00:24 | Ticket 05 landed (dye mixing) | `5a5cfe1bf` | Sol's 168 tests; orchestrator rerun 167 tests OK; census pin for ticket 06's actions fixed here |
| 00:26 | Ticket 07 landed (tab arrows) | `b9dbe833b` | Rebased by the orchestrator; 593 neighbour tests OK before rebase, focused tests OK after |
| 00:28 | Native check of 05, 06, 07 (Terra, `native/check-05-06-07/`) at `ac93a440f` | — | Every step matched; verdict "blocked" only because the tester has no hover action and opened "Mix with" by keyboard. Tab arrows at both ends, greyed at their ends, all 11 tabs whole when selected; Mix with lists Yellow → Orange and Blue → Purple, one pair mixed; Utilities shows orange, green and purple mixing; Wyson's 20-coin offer moved 20 Coins and 2 leaves. Guard verify unchanged: true |
| 00:41 | Full plain lane at `b9dbe833b` | — | 6,487 tests, 1 failure: `test_public_exports_preserve_names_and_original_order` (ticket 05 added two names to the frozen quest_data facade) |
| 00:48 | Orchestrator fix: dye source beside its rows | `9576597f0` | 79 focused tests OK, including the split contract |
