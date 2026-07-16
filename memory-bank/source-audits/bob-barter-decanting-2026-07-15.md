# Bob Barter Potion Decanting Audit

Date: 2026-07-15  
Cutoff: RuneScape immediately before EOC, `2012-11-20T00:00:00Z`

## Period evidence

- RuneScape Wiki, `Bob Barter (herbs)`, oldid `6222086`, timestamp
  `2012-09-09T19:34:58Z`: Bob is at the Grand Exchange and combines 1-, 2-,
  and 3-dose potions into four-dose vials through the ordinary `Decant` action.
  The revision explicitly includes noted and unnoted potions.
- OpenRS2 revision-742 cache, NPC `6524`: `Bob Barter (herbs)` exposes
  `Talk-to`, `Info-herbs`, `Decant`, and `Decant-X` actions. Verified with
  `tools/query_openrs2_cache_definitions.sh` against the extracted
  `742-2012-11-07` cache.
- Jagex, `Death Hats, Draynor and Upgrades`, `2011-05-25`: the update added
  two- and three-dose choices to Bob's existing four-dose decanting. The
  period decanting documentation explicitly says Bob does not decant to
  one-dose potions.
- Darkan `BobBarter.java` for NPC `6524` supplies the exact redistribution
  shape: total each potion family, emit full target-dose vials, then emit one
  partial vial for a nonzero remainder. Its modern one-dose option conflicts
  with the period documentation and is not adopted.

## AnkiScape contract

Bob Barter is a free shop service at the Grand Exchange, not a Herblore target
and not a review-paced Utility action. A single invocation processes the whole
inventory immediately. It does not award XP, consume reviews, advance the shop
market clock, or consult the wall clock.

The runtime derives eligible families from the live non-Daemonheim Herblore
finished-potion catalog and admits only families whose period item table
contains all four vial-dose identities. Two-dose barbarian mixes are excluded
because they are not ordinary vial families. The player selects a target of
two, three, or four doses; four is the default. For every eligible family:

1. Total doses are conserved exactly.
2. The result uses as many target-dose vials as possible and at most one
   partial vial for the remainder.
3. Vial containers are also conserved. Consolidating returns the reduction in
   occupied potion vials as empty `Vial` items; splitting consumes the required
   number of player-owned empty vials.
4. An inventory requiring no consolidation is rejected as a no-op.
5. The complete inventory delta is one shop event and can be rolled back
   independently through the existing shop-event undo path.

Period documentation says Bob could supply extra vials at the current Grand
Exchange price. AnkiScape's fake Grand Exchange is deliberately parked and the
period price is dynamic, so automatic vial purchasing remains `source_blocked`.
The service denies a split when the inventory lacks the necessary empty vials
instead of inventing a fixed price.

The reachability audit models the quantity-free consequence of the repeatable
service: a craftable three-dose potion can produce its one-, two-, and
four-dose family states through repeated crafting and decanting. Exact
quantities remain enforced by the runtime service, not the graph audit.

## Verification

- The derived runtime catalog contains 45 ordinary four-dose vial families,
  including Agility potion and excluding Daemonheim and barbarian-mix rows.
- Focused shop-data, pure-logic, and reachability coverage passes 37 tests.
- The real offscreen Qt shop flow passes with Bob's provider row, 2-4 dose
  selector, remainder preview, one-click inventory mutation, and shop-history
  event.
- `python3 run_tests.py` passes all 1,246 collected tests with 183 environment
  skips and the three existing expected XP-parity failures.
- `git diff --check`, module compilation, and `tools/worktree_guard.py audit`
  pass.
