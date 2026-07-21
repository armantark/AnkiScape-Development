# Court Cases horizontal implementation

Date: `2026-07-21`

Status: **mechanic-complete horizontal slice implemented.**

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Period evidence

The literal pre-cutoff RuneScape Wiki revisions establish the live rules and
the three representative cases:

- `Court Cases`, oldid `6202025`, `2012-09-06T03:11:19Z`: King's Ransom;
  65 Attack to prosecute or 65 Defence to defend; up to three case reports;
  optional fingerprint work; evidence, witness, and jury choices; an undecided
  verdict that preserves preparation and permits a retry; loss of the case on
  giving up; the reward table; one held summons; and the Batch 2 fourteen-day
  cadence.
- `Mugger v. Roger Murray`, oldid `6130755`,
  `2012-08-23T17:59:01Z`: the free starter's three reports, fingerprint, exact
  prosecution and defence routes, 2,000 Attack/Defence XP, and no item reward.
- `River troll v. The People`, oldid `6134988`,
  `2012-08-24T09:50:53Z`: two reports, no fingerprint, exact routes, 3,500
  Attack/Defence XP, and twenty Sharks.
- `Party Pete v. His Neighbours`, oldid `6447758`,
  `2012-10-20T23:34:14Z`: the Batch 2 crime-scene and interview preparation,
  role-specific trial routes, 9,000 Attack/Defence XP, and one Rainbow afro.
- `Court summons`, oldid `6476690`, `2012-10-26T16:05:53Z`: non-stackable,
  non-tradeable, one held at a time, unavailable before the starter, and
  unobtainable while another case remains active.

OpenRS2 revision 742 independently identifies Court summons as item `18757`
and Rainbow afro as item `19747`. The local `data/cfg/items.yml` row for item
`19747` marks it tradeable and has no equipment bonus block, so the live
wearable uses the period head slot with zero combat bonuses rather than
invented stats. The period file history supplies the tight-cropped,
sub-`64x64` Court summons and Rainbow afro art recorded in
`assets_provenance.json`.

## Live mechanic boundary

The shipped slice includes:

- the King's Ransom and role-level entry gates;
- one free starter followed by summons entry, with a single-summons ownership
  gate applied to both Combat and Thieving acquisition;
- explicit report, fingerprint, interview, crime-scene, evidence, witness, and
  jury beats, one answered review per beat;
- saved Casual and Advanced policies, where Casual follows the pinned route
  and Advanced exposes exactly the current courtroom choice;
- an undecided verdict that returns to the first trial beat without repeating
  preparation, and a separate give-up action that loses the consumed summons;
- exact role XP and item rewards with atomic review undo;
- the Batch 2 fourteen-day wait as `3,360` answered cards on the shared world
  clock, never the wall clock;
- schema-69 persistence and sanitizer repair; and
- a compact Activities card, normalized art, cadence declaration, telemetry,
  runtime dispatch, and direct-action undo.

The source says choices can help, be inconsequential, or severely damage a
case and that several winning routes may exist, but it does not provide a
complete numerical jury formula. The horizontal implementation therefore uses
the page's published successful route as the one guaranteed winning route:
all pinned beats produce a decided verdict, while any weakened beat produces
an undecided retry. This is a disclosed bounded translation, not a claimed
historical probability.

## Data-depth boundary

The remaining thirteen cases, alternate winning routes, Batch 2 case order,
and the five/ten/sixteen-case Barrister gear milestones remain catalog depth.
Monster, pickpocket, casket, and hard-clue sources are period-listed; the live
single-summons gate is shared, while only already-implemented Combat and
Thieving acquisition paths can currently emit the item. No hidden drop rate is
invented.

The three-case catalog is deliberately chosen to exercise every shared
mechanic: starter versus summons, Batch 1 versus Batch 2, fingerprint versus no
fingerprint, simple reports versus crime-scene/interview preparation, unequal
role route lengths, both XP destinations, no-item and item rewards, retry, and
case loss. Adding later cases requires data and art only, not a new activity
state machine.

## UI taste boundary

Opus reviewed the compact card because Fable is on owner-requested reserve and
Kimi failed its quota safety gate. The accepted findings removed the duplicate
completion counter, authoring vocabulary, mode-label noise, and repeated
starter copy. The established `28x28` activity icon rhythm, two compact policy
selectors, and one-choice-at-a-time Advanced flow were retained.

## Verification ledger

Focused pure/runtime/cadence and real offscreen-Qt checks cover entry, both
roles, all three cases, exact rewards, summons filtering, the Batch 2 boundary,
undecided retry, give-up loss, migration, dispatch, normalized icons, and the
compact card. Full closure results are recorded in
`memory-bank/status-updates/court-cases-horizontal-results-2026-07-21.html`.
The mobile-safe copy is <https://nvblmw2z0ddz.postplan.dev>.

The complete non-Qt suite passes all `2,227` methods with `292` expected
dependency skips; the complete real offscreen-Qt suite passes the same `2,227`
methods with one intentional platform skip. A fully quit and freshly
relaunched native Anki process showed one launcher and one AnkiScape menu, the
paginated Distractions and Diversions page, the normalized Court Cases icon,
and the unclipped locked starter card without changing the owner save.

Broad verification caught and closed the activity-surface oracle and Rainbow
afro wearable-registry omissions. Isolating the wearable test then exposed a
pre-existing import-order defect: `constants.py` mutated the generated
`equipment_data.EQUIPMENT_DATA` mapping in place. Runtime extensions now build
on a copy and explicitly flatten that combined mapping, leaving the generated
roster stable and byte-reproducible while preserving Barrows and Fish Flingers
equipment.

Documentation, hard test quality, compilation, JSON, diff, normalized-asset,
reachability, and worktree-safety gates pass. The graph reports `1,442`
actions, `2,133` reachable items, `166` known orphan inputs, and `187`
unresolved actions; Rainbow afro resolves through `Utility:court_cases` and
this slice adds no orphan.
