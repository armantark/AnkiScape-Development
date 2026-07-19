# Grand Exchange interface and Bankstanding closure

Date: 2026-07-19

Status: **implemented and verified; period interface supersession applied.**

## Authority

- `fake-grand-exchange-design.md` remains the base market/product contract.
- `ge-relitigation-2026-07-19.md` remains the market-engine amendment.
- `grand-exchange-slot-count-supersession-2026-07-19.md` is the newest
  authority for the interface: six member offer slots and Guide / ±5% / custom
  price controls replace every older eight-slot or ±20% clause.

## Period interface harvest

RuneScape Wiki `Grand Exchange`, oldid `6367453`, timestamp
`2012-10-08T01:30:21Z`, is the nearest useful pre-cutoff interface record read
as literal wikitext:

<https://runescape.wiki/w/Grand_Exchange?oldid=6367453>

It establishes:

- members had six trading spaces; free players had two;
- fully and partially finished trades were collectible at banks;
- chatbox messages reported updated offer status;
- the post-2011 interface exposed guide prices, ±5% buttons, and custom offers;
- chronological priority mattered among competing offers; and
- players could wait and change a price when an offer did not complete.

AnkiScape has no membership tier, so its normal surface uses the period member
count of six. The period page does not attest ±20% buttons, so they are absent.
It also does not attest an in-game price-history graph or trend indicator.
Those visual trend surfaces remain `source_blocked` and excluded under
`ge-relitigation-2026-07-19.md`; the external price database remains separate.

## Implemented surface

- The main menu now has a top-level Grand Exchange tab with six offer slots.
- Buy search spans the registered exchangeable catalog; sell search contains
  only exchangeable items currently owned.
- Quantity defaults to one. Guide, -5%, +5%, and custom integer prices feed
  preview, safety confirmation, placement, and editing.
- Open offers can edit price or remaining quantity; editing preserves
  completed portions and resets queue age at the current market tick.
- Slot detail supports partial collection, cancellation, and collect-all.
- Configurable high-total and extreme-price confirmation thresholds live in a
  collapsed safety panel.
- Ironman mode disables only the GE and cannot activate while an offer remains
  open or collectible.
- A persistent green review-HUD notice remains visible while any offer has
  collectible contents; it never interrupts review with a modal.
- Bankstanding is a no-XP Economy Utility/Activity. Missing materials or empty
  source stock switch future reviews to Bankstanding after one warning; level,
  quest, equipment, and configuration locks still deactivate instead.
- The Bankstanding transition participates in the answered-card transaction.
  It no longer performs a duplicate mid-review save, so Farming/background
  advancement, the active-skill switch, RNG state, and undo persist atomically.

## Review evidence

Read-only Fable Workflow `41d86f07-00f2-4993-9d3a-920f098b3374` reviewed the
dark-mode Qt surface and found three concrete interaction defects that were
independently reproduced and fixed: stale selected-slot state, unowned items
shown on the sell side, and active quick-price buttons that rounded to no
change. It made no repository writes. An earlier invocation
`30b34c23-...` failed before creating a useful provider session and supplied no
evidence.

The later period harvest superseded Fable's eight-slot / ±20% visual review.
The final Qt assertions require exactly six slots and no ±20% controls.

## Verification

- 296 focused GE, pure-logic, and integration tests pass.
- Three focused real offscreen Qt GE/HUD tests pass.
- The complete non-Qt suite passes: 1,737 tests, 219 intentional skips.
- The complete real offscreen Qt suite passes: 215 tests.
- `git diff --check`, Python compilation, test-quality, documentation, and
  worktree-layout audits pass.
- The item-reachability audit reproduces the established repository baseline:
  1,253 actions, 1,882 reachable items, 283 orphan inputs, and 304 blocked
  actions. This slice adds no item producer or consumer, so it introduces no
  new reachability row. No asset audit applies because the GE surface uses
  standard Qt controls and adds no asset.

No owner-facing design gap remains in this slice.

Results artifact:

- `memory-bank/status-updates/grand-exchange-interface-bankstanding-results-2026-07-19.html`
- mobile copy: <https://e62v7fq2zr2o.postplan.dev>
