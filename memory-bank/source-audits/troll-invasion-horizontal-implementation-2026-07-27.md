# Troll Invasion horizontal implementation

Date: 2026-07-27

## Scope and cutoff

Breadth one implements both cutoff routes, all twenty Standard or seven Hard
wave markers, safe Combat failure, gatehouse Repair, partial cash-out, the
30-day answered-card reward allowance, reward-book redemption, persistence,
undo, UI, and period art. Exhaustive wave rosters and exact hidden tables remain
deferred under registered placeholders.

## Sources

- RuneScape Wiki `Troll Invasion`, oldid `6588736`,
  `2012-11-19T21:28:55Z`.
- `memory-bank/source-audits/troll-invasion-loop-2026-07-18.md`, introduced by
  commit `a9471fe0` and cadence-corrected by `34ba9465`.
- `memory-bank/source-audits/activity-cadence-reconciliation-2026-07-18.md`.
- `memory-bank/multi-enemy-encounter-contract-2026-07-18.md`.

No readable Darkan gameplay implementation or pinned item/NPC ID table was
used. The family therefore claims no production NPC or item IDs.

## Exact rules implemented

- Safe single-player Combat and Repair routes.
- Standard has 20 waves; attempting it unlocks 7-wave Hard.
- Combat advances through the shared six-tick Combat reducer and stops at each
  wave boundary. Standard and Hard both pay a full completion fraction of one.
- Up to five supply-table uses are available per wave; Dynamite can permanently
  destroy the table for the run.
- Repair tracks oil drums, ballista ammunition, walls, barricades, morale,
  trolls defeated, and eligible actions. One productive action credits ten
  trolls; the endpoints are 1,500 trolls or 167 eligible actions.
- Leaving or safe defeat ends the run. Completed wave fraction drives Combat
  partial cash-out; Repair uses its credited-troll fraction.
- One source month maps to 7,200 answered cards. Reward permission banks to the
  project default cap of two; play remains available when no monthly reward is
  banked.
- Reward XP is exactly `8 × completion_fraction × (L² - 2L + 100)` and is paid
  atomically to the selected trainable skill when the book is read.

## Registered placeholders

- `troll_invasion.wave_front_stats`: aggregate LP and combat values for every
  visible wave front, including Cliff's final front.
- `troll_invasion.dynamite_supply_chance`: the Dynamite destruction trigger.
- `troll_invasion.repair_values`: component values, job XP, pressure,
  interruption, morale, and automatic morale-power values.
- `troll_invasion.partial_reward_semantics`: completed-wave and credited-troll
  partial fractions plus the no-added-rounding XP application.

All are non-zero and exercise their mechanics. Nothing presents them as exact
period values.

## Art and full upload histories

`tools/fetch_troll_invasion_assets.py` installed:

- `activityicons/troll_invasion.png` from `File:Troll Invasion.png`, selected
  upload `2012-07-02T07:44:28Z`. Full API history checked: six uploads, two
  before cutoff.
- `activityitems/troll_invasion_reward_book.png` from `File:Reward book.png`,
  selected upload `2011-11-27T17:33:03Z`. Full API history checked: three
  uploads, two before cutoff.

Both selected records are in `assets_provenance.json`.

## Tests mapped to the contract

`tests/test_troll_invasion.py` drives the real Combat kernel through all twenty
Standard and all seven Hard fronts, a real safe death, partial leave and book
redemption, all four Repair jobs and all three repair-skill XP outputs, morale,
monthly allowance sync, migration, runtime dispatch, and the offscreen panel.
`tests/test_direct_action_undo_seam.py` restores both policy and active entry
through `commit_direct_action`.
