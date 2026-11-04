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
| 00:41 | Full plain lane at `b9dbe833b` | — | 6,487 tests, 1 failure: `test_public_exports_preserve_names_and_original_order` (ticket 05 added two names to the quest_data facade, whose export list a hash pins) |
| 00:48 | Orchestrator fix: dye source beside its rows | `9576597f0` | 79 focused tests OK, including the split contract |
| 00:49 | Ticket 08 landed (bank rows) | `003e9030d` | Cause measured: the grid's host was sized for 11 columns at Qt's default 640 px before the reflow to 6; overlay scroll bars never resized it again. Fix: reflow before the scroll area sizes the host. 599 neighbour tests OK; orchestrator rerun 54 OK after rebase. Bank Claims line not cut in its own row (39 px label, 36 needed); it sits below the page edge until the player scrolls |
| 00:51 | Native check of 08, first run | — | Invalid: the runner's prompt named the default seed, so the tester used the 47-item save; runner fixed (packets name their own start state) |
| 00:56 | Native check of 08 with the owner's save (`native/check-08/`) at `fbc0c02bb` | — | 154 item kinds; no overlapping squares or headings at 749 x 776, 749 x 572 or after reopening; at 1728 wide no overlap, one row seen only at the scroll edge. Verdict "blocked" for that edge row only. Guard verify unchanged: true |
| 01:03 | Ticket 04 landed (supply steps, Goblin Diplomacy) | `4c2a2ec78` | 1,296 neighbour tests OK at `517f7a4f8`; orchestrator rerun 332 OK. Raw supplies finish in 10 reviews; the export-list hash re-pinned for `QuestSupplyRecipe` (precedent `87ff71c09`) |
| 01:49 | Full offscreen Qt lane at `fcb8b0ce9` | — | 6,487 tests, OK (skipped=5) |
| 01:53 | Ticket 01 landed (exact counts) | `428aba8fc` | Implementer: 4,815-run Monte Carlo sweep (4,751 exact, 62 stopped short with a reason, 2 dragon fights that land no kill at 1x without a queue either), 1,875-run Construction sweep; 1,089 neighbour tests OK. Orchestrator change: a whole lot (15 arrow shafts from one log) is kept instead of deleting products after their inputs were spent; new test red against the deleting version; 308 queue and runtime tests OK |
| 02:13 | Ticket 02 landed (ended entries, Clear) | `ec171382d` | 44 queue tests plus 340 neighbour tests OK; three mutation proofs red; orchestrator rerun 61 OK |
| 02:35 | Full plain lane at `e0e0874b6` (ticket 01 in) | — | 6,497 tests, OK (skipped=751) |
| 02:43 | Full offscreen Qt lane, snapshot at 02:35 = `c0cbe0804` (tickets 01 and 02 in) | — | 6,502 tests, OK (skipped=5) |
| 03:06 | Ticket 03 landed (queue box, fold, add feedback) | `9f199e588` | 701 focused tests OK; five mutation proofs red; orchestrator rerun 52 OK. The shared vertical_scroll helper now ignores preferred width, which also reaches the GE and Settings pages |
| 03:08 | Native check of 03 (`native/check-03/`) at `bee35c9c0` | — | First add: blue band and "Added ✓ (1 of 5)" (read by accessibility; the pointer covered part of the button in the brief screenshot); 5 entries whole with no scroll bar at default and about 572 tall; fold works and is remembered; Clear empties the box. Observations: GE offer controls whole at both heights; Settings readable; Smithing at 720 wide cut two rows with "..." (added to ticket 09). Guard verify unchanged: true |
| 03:32 | Ticket 10 landed (menu copy) | `236159ab6` | 1,586 focused tests OK; orchestrator rerun 238 OK; AGENTS.md gains the menu-text rule. Copy table: `evidence/10/copy-table.md` |
| 03:58 | Ticket 09 landed (GE test, wrapped skill target rows) | `0ae849395` | 703 focused tests OK; four mutation proofs red; orchestrator rerun 151 OK. GE offer panel needed no product change |
| 04:16 | Final native check (`native/final-check/`) at `bbe289398` | — | Exact counts in one card (6 Redberries, 3 Goblin mail, 30 Onion; "Queue finished after Pick onions."); Clear stopped hand-started Woodcutting, Resume offered it; Goblin Diplomacy completed in 9 cards from raw supplies with 3 mail held; copy clean; Smithing rows wrap at 720 and survive two resizes; GE whole with 5 entries; no crash. Verdict "blocked" only for test bookkeeping (a malformed note batch, per-card bank losses not each read). Guard verify unchanged: true |
| 04:04 | Two-axis review (Astra standards, Opus spec) | — | `ankiscape-pass18/review/aggregate.md`; fixes dispatched to one Opus agent |
| 04:20 | Kimi K3.1 taste review of 9 native and offscreen screens | — | "approve with fixes": accuracy label case and "pouch(es)" fixed at `43729037a`; the half-shown edge tab is how a scrolling bar works (dismissed); the duplicate Summoning points line left for the owner |
| 04:26 | Full lanes at `bbe289398` | — | Not run: the shared test mirror was blocked by an orphaned plain run (`plain-1793185741-a0c49b6c`, started 04:09, driver gone, workers still running); lanes rerun after the review fixes land |
| 04:34 | Review fixes landed | `7597fa7cc` | Full Goblin Diplomacy blocker tuple; skill-list layout test asserts presence; whole-lot docstring; explicit Event log reference for ended entries (two mutation proofs red); planner closure; Wyson's approved offer text restored; three stale play-checklist copies from ticket 09's rebase removed. 420 tests OK; orchestrator rerun 405 OK after rebase |
| 05:24 | Promotion gate at `b69c88b28` | — | Plain 6,510 tests OK (skipped=758); Qt 6,510 OK (skipped=5); docs audit passed |
| 05:56 | Landing refused | — | The loop's train landed first (main `8b187d67d`: Easy Treasure Trail searches, Fenkenstrain); merged main into the integration branch: shop data (both sides added vendor actions; main's Roavar kept by hand) and census pins (1,688 actions, 2,364 reachable items); vendor-count pins 6 and 7; 498 tests from both sides OK |
