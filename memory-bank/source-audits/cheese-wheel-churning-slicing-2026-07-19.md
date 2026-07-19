# Cheese-wheel churning and slicing closure

Date: 2026-07-19

Status: **verified and closed.**

## Period evidence

### Dairy churn

RuneScape Wiki `Dairy churn`, oldid `6474695`, timestamp
`2012-10-26T06:25:08Z`:

<https://runescape.wiki/w/Dairy_churn?oldid=6474695>

The cutoff record establishes that:

- level 48 Cooking is required to make a cheese wheel;
- a bucket of milk can become cream, butter, or a cheese wheel;
- a pat of butter can become only a cheese wheel;
- each cheese-wheel route awards 40.5 Cooking XP;
- churning a dairy item takes eight game ticks;
- the milk container is returned as a Bucket; and
- dairy-churn actions do not fill Cooking urns.

The live cadence declaration therefore uses the exact eight-tick action time:
`6000 / 8 = 750` churn actions per in-game hour. It does not derive gameplay
from the article's rounded four-second prose.

### Cheese wheel and Slice-all

RuneScape Wiki `Cheese wheel`, oldid `6288901`, timestamp
`2012-09-24T09:43:17Z`:

<https://runescape.wiki/w/Cheese_wheel?oldid=6288901>

RuneScape Wiki `Talk:Cheese wheel`, oldid `5942573`, timestamp
`2012-07-16T00:50:23Z`:

<https://runescape.wiki/w/Talk:Cheese_wheel?oldid=5942573>

The cutoff item record establishes that:

- Cheese wheels are made by churning milk or butter at level 48;
- an unsliced wheel is untradeable;
- `Slice-all` consumes one wheel in one player action;
- the result is a random minimum of five Cheese, increases with Cooking level,
  and can exceed 30 at level 99;
- each Cheese sliced awards 4 Cooking XP; and
- receiving 30 at level 99 is described as very rare.

The talk record preserves two useful samples without establishing an authentic
formula:

- level 57: 887 Cheese from 100 wheels, mean 8.87; and
- level 99: 695 Cheese from 27 wheels, mean approximately 25.74.

The exact period distribution and interpolation formula remain
`source_blocked`. The settled source-harvest program permits a labeled bounded
abstraction where a value is necessary. AnkiScape uses the smallest model that
honours the period shape: `5 + Binomial(30, p(level))`, with `p` linearly
interpolated between the two observed means and clamped to levels 1-99. This
guarantees 5-35 Cheese, preserves increasing level benefit, makes 31-35
possible but uncommon at level 99, and keeps the two observed means exact.
The slice itself remains a discrete one-review action because the cutoff record
does not close an actions-per-hour rate.

## Item identities and assets

The pinned Darkan cache/item constants establish:

- Bucket of milk: item `1927`;
- Bucket: item `1925`;
- Pat of butter: item `6697`;
- Cheese wheel: item `18789`;
- the transient sliced-wheel animation identity: item `18790`; and
- Cheese: item `1985`.

The transient sliced-wheel identity is not exposed as a stored inventory item;
the one-review Slice-all transaction directly emits the final Cheese stack.

`cookingitems/cheese_wheel.png` is authentic RS3-wiki artwork archived
`2011-11-19T02:01:27Z`, fetched through the repository asset pipeline with
explicit `--source rs3`. Its provenance entry records SHA-1
`590716023612e9c186a7162ceceab8c17c5fa45d`. Existing period assets are reused
for Bucket of milk, Pat of butter, Bucket, and Cheese.

## Implemented behavior

- Cooking has a compact `Dairy` target family containing milk churn, butter
  churn, and Slice-all.
- Both churn actions are deterministic, award 40.5 Cooking XP, and create one
  Cheese wheel. Milk churning also returns one Bucket.
- Slice-all consumes one wheel, produces 5-35 Cheese from the calibrated
  bounded model, and awards 4 Cooking XP per Cheese actually produced.
- Dynamic output quantities and the returned Bucket appear in activity gains
  and action telemetry.
- Dairy actions deliberately bypass Cooking-urn progress, matching the cutoff
  churn record.
- The normal answered-card transaction owns inventory, XP, RNG, telemetry, and
  answer undo atomically.
- Tooltips disclose level, outputs, the Slice-all range, XP per slice,
  deterministic success, materials, and the returned Bucket without adding a
  bespoke panel.

## UI taste review

The owner required both Kimi K3 and Fable to review every UI surface added in
this implementation pass, not just Dairy. Both received the Bank search, six
slot GE, GE HUD notice, Bankstanding, and Dairy surfaces as a single bounded
read-only review.

- Kimi K3 inspected all five screenshots and the relevant code. It found the
  GE's ragged `4 + 2` slot layout, conflated empty-list copy, misleading
  Bankstanding toast, specification-like collectible copy, and raw
  `item(s)` detail text.
- Fable's harness could read the code and wheel asset but was denied `/tmp`
  screenshot access. Its independent code review confirmed the slot and
  Bankstanding problems, then found that Bankstanding's generic tooltip/HUD
  falsely claimed a produced item, the UI exposed the review-native limit as a
  literal four-hour wait, the safety controls lacked explanations, a fixed
  green could lose light-mode contrast, and the tab mixed `gp` with `Coins`.

The primary agent reproduced and fixed those concrete findings:

- the six GE slots now render as balanced `3 x 2`;
- buy, sell-with-no-owned-stock, and query-no-match states have distinct copy;
- Bankstanding is explicitly an idle no-op in its row, HUD, and activity toast;
- the buy-limit label says `per 40 cards`, with no wall-clock implication;
- collectible status/detail text names only real proceeds;
- safety thresholds explain both their guide-price reference and confirmation
  consequence;
- the GE consistently says `Coins` and uses palette text for its light/dark
  status contrast; and
- final light and dark offscreen screenshots exposed a native cyan selection
  block in the grouped-tree indentation gutter. Grouped targets now use a
  bold current-target marker without native row selection, removing the
  artifact while leaving item activation and the current-item API intact.

Kimi's suggestion to hide Bank's unfiltered item count was not adopted because
the count remains useful inventory information and is not misleading. Fable's
suggestion to add a confirmation before disabling Ironman mode was not adopted:
that changes the settled gameplay interaction rather than correcting a
presentation defect.

## Verification

- 520 focused tests pass across Cooking pure logic, runtime dispatch, answer
  undo, metadata, registries, urn behavior, and live cadence.
- 37 source-row, cadence, and Cooking-data parity tests pass.
- The complete non-Qt suite passes: 1,744 tests, including 222 intentional
  skips.
- The complete Qt-enabled offscreen suite passes: 1,744 tests with no skips.
  The 218-test main-menu surface also passes independently after the dual taste
  review.
- The item-reachability audit now reports 1,256 actions, 1,883 reachable items,
  283 orphan inputs, and 304 blocked actions. Compared with the preceding GE
  closure this slice adds three Cooking actions and one reachable item without
  increasing either unresolved count.
- Documentation and test-quality audits pass with zero hard issues.
- Compilation, `git diff --check`, and the canonical-checkout worktree audit
  pass.

No owner-facing creative-design gap has emerged. The missing authentic slice
formula is a disclosed source gap resolved by the already-authorized bounded
abstraction policy, not a reopened design fork.

Results artifact:
`memory-bank/status-updates/cheese-wheel-churning-slicing-results-2026-07-19.html`;
mobile copy: <https://dcxvx0rn6jgx.postplan.dev>.
