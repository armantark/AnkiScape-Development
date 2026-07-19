# Slayer Turael/Spria runtime closure — 2026-07-17

Status: **implemented and verified**.
Cutoff: `2012-11-20T00:00:00Z`.

## Scope

This closes the first complete Slayer master role. Turael/Spria assignments are
management actions, not review-training targets: the user receives an eligible
weighted assignment, opens Combat with the task-only filter enabled, and earns
Slayer XP and task progress only from qualifying kills. The role intentionally
awards no points and does not advance a post-Smoking-Kills streak.

The 23-family pool, eligibility rules, provisional hidden weights, and count
ranges remain governed by
`slayer-turael-spria-pool-2026-07-17.md`. No values in that source audit were
reinterpreted during implementation.

## Closed target dependencies

The final three missing family representatives are now executable:

| Target | Period evidence | Live contract |
|---|---|---|
| Gelatinous abomination | `Gelatinous abomination` oldid `6079671`, 2012-08-12; `Spiked gauntlets` oldid `5827717`, 2012-06-25 | level 2, 50 LP, maximum hit 16, 5 Slayer XP; cannot die below 1 LP unless Spiked gauntlets are worn |
| Young grotworm | `Young grotworm` oldid `6490000`, 2012-10-28; Darkan `young_grotworm` combat/drop rows | level 10, 150 LP, Magic attack, maximum hit 20, 15 Slayer XP; one exact 50,000-slot Darkan selector |
| Monkey | `Monkey` oldid `6552407`, 2012-11-13; Darkan monkey combat/drop rows | level 3, 60 LP, approximate maximum hit 20, 6 Slayer XP, guaranteed Monkey bones |

Gelatinous-abomination non-guaranteed numerical drop rates remain
`source_blocked`; no rates were invented. Its worn-only finisher is reusable
and never enters the consumable finisher pack.

Young grotworm's two previously unregistered equipment drops are complete:

- Coral bolts use cache item `24304`, stack in the ammunition slot, are
  nontradeable, and preserve the period `+19` Ranged Strength from `Coral bolts`
  oldid `6146806` (2012-08-26).
- Royal cape uses cache item `24315`, is a tradeable nonstackable cape with zero
  combat bonuses, from `Royal cape` oldid `6308196` (2012-09-27).

The checked-in sprites are the pinned file revisions from 2012-05-22. Spiked
gauntlets use cache item `23035`, cost 6 coins in all eight Slayer-equipment
stocks, occupy the hands slot, and remain distinct from Slayer gloves.
Monkey bones retain cache item `3183` and their authentic nonstackable
inventory shape.

## Runtime and UI

- Assignment selection filters authentic Slayer and quest requirements, avoids
  the immediately previous family when another eligible family exists, and
  preserves the source-backed weighted roll.
- Matching Combat kills atomically decrement the assignment and grant target
  Slayer XP. Nonmatching kills do neither.
- Slayer is management-only and exposes `Assignment`, `Masters`, and `Rewards`
  tabs. `Open in Combat` enables the task-only filter without starting an
  encounter, and task-only results compose with shared Combat search.
- Rewards remain visibly locked behind Smoking Kills rather than exposing dead
  controls.
- Player data migration and direct-action undo include the complete Slayer
  assignment state.

## Verification

- Focused Slayer, Combat, equipment, shop, roster, and registry coverage:
  89 methods passed.
- Storage, hub, live assignment dispatch, and atomic Combat-credit coverage:
  37 methods passed.
- Real offscreen Qt Slayer management, Combat deep-link, and empty-filter
  recovery coverage: 4 methods passed.
- The shop-generator regression proves Spiked gauntlets remain live even when
  the older `items.yml` source omits item `23035`.
- Complete core discovery: 1,537 methods, 1,326 ordinary passes and 211
  declared environment skips.
- Complete real offscreen Qt discovery: all 1,536 methods passed without skips
  or failures; the latest item-only registry seams passed the five-method
  targeted holdout after that run.
- Test quality, documentation, compilation, JSON, diff, item reachability, and
  worktree-safety gates passed. Reachability reports 1,220 actions and 288
  known orphans: 111 root and 177 cascade.
- Fable's bounded read-only UI review found no wiring or dark-mode defect. Its
  two reproduced copy defects were fixed: internal readiness language is gone,
  and the persisted task-filter empty state now tells the player how to recover.

No owner-level design question emerged. Smoking Kills is the next Slayer batch.
The visual result is
`status-updates/slayer-turael-runtime-results-2026-07-17.html`
(<https://5k6wxpak7xkj.postplan.dev>).
