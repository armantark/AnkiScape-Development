# Flash Powder Factory Horizontal MVP

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **mechanic-complete horizontal slice implemented; exhaustive hidden-roll
precision remains deferred data depth.**

## Authority and immutable evidence

The owner-settled design authority is
`flash-powder-factory-loop-2026-07-18.md`. Implementation-time harvesting read
the exact pre-cutoff wikitext through `tools/wiki_parity.py` and pinned:

- `Flash Powder Factory` oldid `6559970`,
  `2012-11-15T19:17:32Z`;
- `Factory outfit` oldid `6547053`,
  `2012-11-10T19:21:03Z`;
- `Fallen rubble` oldid `5130308`; and
- `Rogue kit` oldid `6293011`, `2012-09-25T01:04:53Z`.

The first page establishes all core loop and reward values used here: levels
75 Agility, 75 Thieving, and 50 Herblore; no boosted entry, skull, familiar, or
pet; fifteen source minutes plus two with a Rogue or Factory top; six starting
catalyst; three to six apparatus; 100 base score; 2.5% per apparatus; 20%
maximum charge; 1% residue per completed powder; the full-set ten-point bonus
once the ordinary batch is at least 120; 105/121 rubble powder; the nonlinear
Brianpoint formula, 155 cap, 20-point long-stay bonus, and published early-exit
penalty bands; the exact XP lots and 95/120 XP rates; and the Factory-piece and
multitool prices. The Factory-outfit page provides the item effects, including
the trousers' three extra catalyst, the gloves' ten-point pickpocket benefit,
and the boots' 30% failure-rate reduction.

## Shipped review model

- Entry is a direct, undoable action. It checks every period skill/skull gate,
  refuses a competing persistent activity, and offers one explicit shared pet
  or familiar dismissal confirmation.
- The run reserves `activity_session`, selects the Activities target, and
  snapshots eight slots or nine with either eligible top, six or nine catalyst,
  and three apparatus.
- Every successful answered card resolves one complete reagent, catalyst,
  route, and mixer circuit. Aggregate obstacle delay or a forced catalyst
  detour can remove the route opportunity but never turns a correct card into
  a replay.
- `Again` consumes one idle slot with no hidden RNG, batch, score, residue, or
  catalyst change. The final productive or idle slot closes and cashes out the
  session atomically.
- Switching or explicit leave uses one destructive confirmation and the same
  early-exit cash-out. Completion and every leave path clear only the Factory's
  own persistent reservation.
- Casual owns the apparatus choice through the selected strategy. Advanced
  may set Ignore or Opportunistic separately. No temporary reagent, map,
  opponent, door, or charge state is persisted.

## Exact scoring and proportional exit translation

One batch applies the sourced additive bonuses to 100, floors the result, and
adds ten points for a qualifying full Factory set. Rubble powder is added at
its sourced 105/121 value. Brianpoints are:

```text
floor(min(score, 500) × 0.20 + max(score - 500, 0) × 0.05)
```

The result is capped at 155 after the sourced long-stay bonus. Four used base
slots is the settled review translation of taking at least six of the source
fifteen minutes. Early exit maps base slots remaining back onto the fifteen
source minutes with `ceil(15 × remaining / 8)` before consulting the published
50/46/40/33/26/20/0 percent source curve. Because the settled model has only
eight base slots and explicitly does not claim one review equals one minute,
the reachable remaining-slot penalties are `50/50/50/50/50/40/26/0/0` for
eight through zero slots remaining. The ninth top slot never makes the penalty
harsher.

## Disclosed source-blocked weights

The period record names the outcomes but does not expose server weights. The
horizontal slice therefore uses the contract-authorized bounded abstractions:

- aggregate obstacle delay: `15%`, multiplied by `0.70` with Factory boots;
- free rubble opportunity by Max/Balanced/Rogue strategy: `10% / 35% / 70%`;
- opportunistic apparatus gain: `20%`, or `30%` with Factory gloves; loss:
  the following `15%`; Ignore still permits an `8%` incoming pickpocket;
- rubble weights: nothing/catalyst/apparatus/average/very nice/Rogue piece =
  `50/20/15/10/4/1`; and
- Factory-mask weights = `35/25/19/13/6/2`, implementing the sourced exact
  fifteen-point reduction to nothing while distributing it across every other
  named outcome.

These values are balance abstractions, not period claims. They remain later
data-depth candidates and do not block the complete mechanic surface.

## Reward and cross-skill closure

Brian O'Richard's shop is instantaneous and undoable. It supports exact
10/100/1,000/10,000-point Agility and Thieving lots, unique Factory pieces,
and stackable Rogue kits. A Bank context action consumes one kit and creates
the selected Chisel, Rope, Tinderbox, or Spade as a separate undoable operation.
Three worn Factory pieces provide the sourced 1/10
three-dose-to-four-dose potion result with period exclusions. The full set
adds the matching clean-herb XP to unfinished potions, excludes Spirit weed,
and retains the sourced 8/8.75 XP special cases for Weapon poison+/++. Prayer
renewal also stacks the Factory 10% with Morytania legs 4's 20% when that gear
is available. The implementation-time audit corrected the unfinished-potion
hook to Herblore's real `unf` group; the provisional `unfinished` key would
never have fired.

## UI, assets, and integration

Flash Powder Factory is an Activities-only Minigames row while retaining its
Agility logic target for storage and review dispatch. Its compact card exposes
session state, saved policy, leave confirmation, exact XP lots, and item
rewards without a nested scroll region. The period Factory-mask activity icon
and Rogue-kit item sprite are normalized by the shared UI scaling path and
recorded in `assets_provenance.json`.

The implementation also removed the retired 24/27-review five-objective loop
and its duplicate 95-XP-only reward commands. Cadence coverage declares one
foreground atomic production circuit and never foreground-multiplies it.

## Verification

- Focused pure, hook, runtime, Agility, Herblore, cadence, asset, integration,
  and Qt checks are green after replacing the retired oracle.
- The complete offscreen Activities/skills-menu suite found and closed one
  real `QFrame` shadowing crash plus one expected registry-set update; all
  reproduced cases pass afterward.
- Full non-Qt, full real offscreen Qt, native restarted-Anki, documentation,
  test-quality, reachability, and final specialist-review results are recorded
  in the corresponding result artifact once closure finishes.

No owner design gap surfaced. Exhaustive hidden-roll recovery and additional
source precision are deferred data depth under the horizontal-breadth goal.
