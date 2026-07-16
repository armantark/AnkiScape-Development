# Bob Barter Potion Decanting Audit

Date: 2026-07-15  
Cutoff: RuneScape immediately before EOC, `2012-11-20T00:00:00Z`

## Period evidence

- RuneScape Wiki, `Bob Barter (herbs)`, oldid `6222086`, timestamp
  `2012-09-09T19:34:58Z`: Bob is at the Grand Exchange and combines 1-, 2-,
  and 3-dose potions into four-dose vials. The revision explicitly includes
  noted and unnoted potions.
- OpenRS2 revision-742 cache, NPC `6524`: `Bob Barter (herbs)` exposes
  `Talk-to`, `Info-herbs`, `Decant`, and `Decant-X` actions. Verified with
  `tools/query_openrs2_cache_definitions.sh` against the extracted
  `742-2012-11-07` cache.
- Darkan `BobBarter.java` for NPC `6524`: the `Decant` action targets four-dose
  vials, totals doses by potion family, emits full target-dose vials plus one
  partial remainder, and returns unused empty vials.

## AnkiScape contract

Bob Barter is a free shop service at the Grand Exchange, not a Herblore target
and not a review-paced Utility action. A single invocation processes the whole
inventory immediately. It does not award XP, consume reviews, advance the shop
market clock, or consult the wall clock.

The runtime derives eligible families from the live non-Daemonheim Herblore
finished-potion catalog and admits only families whose period item table
contains all four vial-dose identities. Two-dose barbarian mixes are excluded
because they are not four-dose vial families. For every eligible family:

1. Total doses are conserved exactly.
2. The result uses as many four-dose vials as possible and at most one partial
   vial for the remainder.
3. Any reduction in occupied potion vials returns the same number of empty
   `Vial` items.
4. An inventory requiring no consolidation is rejected as a no-op.
5. The complete inventory delta is one shop event and can be rolled back
   independently through the existing shop-event undo path.

The reachability audit models the quantity-free consequence of the repeatable
service: a craftable three-dose potion can produce its one-, two-, and
four-dose family states through repeated crafting and decanting. Exact
quantities remain enforced by the runtime service, not the graph audit.

## Verification

- The derived runtime catalog contains 45 ordinary four-dose vial families,
  including Agility potion and excluding Daemonheim and barbarian-mix rows.
- Focused shop-data, pure-logic, and reachability coverage passes 35 tests.
- The real offscreen Qt shop flow passes with Bob's provider row, icon, dose
  preview, one-click inventory mutation, and shop-history event.
- `python3 run_tests.py` passes all 1,244 collected tests with 183 environment
  skips and the three existing expected XP-parity failures.
- `git diff --check`, module compilation, and `tools/worktree_guard.py audit`
  pass.
