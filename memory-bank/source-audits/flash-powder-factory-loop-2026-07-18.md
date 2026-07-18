# Flash Powder Factory Review Loop

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period structure pinned; finite review loop and multiplayer
abstraction settled; exact hidden rolls remain source work.**

## Pinned period evidence

`Flash Powder Factory` oldid `6559970`
(`2012-11-15T19:17:32Z`) establishes:

- the activity replaced the historical Rogues' Den maze;
- entry requires level 75 Thieving, level 75 Agility, and level 50 Herblore;
  boosted levels do not qualify, and a skulled player or one accompanied by a
  familiar or pet cannot enter;
- a source game lasts 15 minutes, with a Rogue top or Factory top adding two
  minutes;
- the production loop collects reagent A, reagent B, and catalytic powder,
  traverses obstacles and pressure doors, and mixes flash powder;
- every powder starts at 100 score, while charge, refining apparatus, residue,
  and Factory outfit effects add to the score;
- players start with six catalytic powder and three refining apparatus, may
  hold at most six apparatus for a maximum 15% bonus, and may gain or lose
  apparatus by pickpocketing other players;
- the period strategy section says pickpocketing is generally less efficient
  than focusing on production;
- fallen rubble can yield Rogue equipment, catalytic powder, apparatus, flash
  powder, or nothing;
- game score converts nonlinearly to Brianpoints, score beyond the source cap
  grants no additional currency, leaving too early applies the exact published
  penalty curve, and staying long enough grants 20 extra Brianpoints; and
- Brianpoints buy Agility XP, Thieving XP, Factory outfit pieces, and a
  multitool.

Source:

- <https://runescape.wiki/w/Flash_Powder_Factory?oldid=6559970>

The broader reward audit also pins `Factory outfit` oldid `6547053` and
`Fallen rubble` oldid `5130308` in
`agility-complete-content-inventory-2026-07-15.md`. Exact obstacle,
pickpocket, rubble, charge-availability, and hidden reward rolls still require
the full evidence-hierarchy pass.

## Settled finite session

One source game becomes **eight answered-card slots**, or **nine** while a
Rogue top or Factory top is equipped. This is a labeled pacing abstraction,
not a claim that one review equals a fixed number of source minutes. Eight is
anchored to the period page's representative 800-score example: one productive
review resolves one complete A + B + catalyst + mixer circuit whose unmodified
batch is worth at least 100 score.

Every answered card while the Factory is active consumes one slot:

- a non-`Again` answer completes one bounded production circuit; and
- `Again` represents standing idle while the live factory session advances,
  consumes the slot, produces no batch, and does not raise residue.

The eighth or ninth slot closes the session atomically, converts score to
Brianpoints through the source formula and cap, and applies the source
long-enough bonus. It does not ask the player to click a cash-out button at the
obvious endpoint.

The source did not support suspending a live game. Switching targets or
explicitly leaving therefore presents one destructive confirmation and closes
the run immediately with the source early-exit penalty translated
proportionally across the remaining **base** action budget. The top's bonus
slot does not make the early-exit penalty harsher, matching the source rule
that its extra two minutes do not count against the player. Merely opening
another UI page does not leave the Factory.

## One review-scale production circuit

A productive review summarizes the only consequential parts of one route:

1. collect reagent A and reagent B;
2. use one carried catalytic powder, detouring through the catalyst machine
   when the reserve is empty;
3. resolve at most one aggregate obstacle outcome;
4. apply the selected route's charge, rubble, and apparatus consequences; and
5. mix one flash powder batch and increase residue by the sourced 1%.

Reagents A and B are temporary per-circuit setup and are not persisted.
Catalyst reserve is consequential because Factory trousers start the session
with nine rather than six and rubble may replenish it. A forced catalyst
detour still completes the batch but can displace a charge or rubble
opportunity; it never creates an ingredient-babysitting review.

Charge is earned and spent inside the same circuit because the source effect is
temporary. Residue, apparatus count, catalyst reserve, and accumulated score
survive between slots because they change later batch value or route choice.
Obstacle failure may reduce that circuit's route bonus or opportunity, but a
correct card still completes the circuit; implementation must not replay
hidden pathing or turn one route into dozens of scenery checks.

## Player controls

Before entry, choose one standing strategy:

- **Max Brianpoints** prioritizes productive routes and active charge machines,
  ignores voluntary pickpocketing, and searches rubble only when it costs no
  useful route opportunity.
- **Rogue equipment** prioritizes rubble opportunities, accepting lower
  expected score in exchange for the authentic Rogue-equipment route.
- **Balanced** takes worthwhile charge routes and opportunistic rubble, and may
  attempt one inline apparatus theft when the bounded opportunity is favorable.

Casual defaults to **Max Brianpoints**. Advanced exposes the same saved
strategy and may separately set apparatus behavior to **Ignore** or
**Opportunistic**; it does not expose reagent machines, pressure doors, exact
paths, individual rubble piles, or per-review controls.

Brianpoint spending remains an instantaneous Activity Rewards shop choice.
Agility XP, Thieving XP, Factory pieces, and the multitool retain their exact
source prices and effects. Buying a reward consumes no review and is atomic
with undo.

## Pickpocketing and public-floor ruling

Pickpocketing survives, but not as a direct action or simulated opponent:

- the run stores only the player's temporary apparatus count, bounded by the
  source maximum of six;
- at most one visible **apparatus contest** can resolve inside a productive
  review;
- the selected strategy changes whether the player ignores, attempts, or is
  exposed to that contest;
- the result is gain one apparatus, lose one, or no change, and the review
  result line says which occurred; and
- no opponent inventory, identity, population, immunity timer, path, or
  background theft loop exists.

The exact contest weights remain `source_blocked` until implementation-time
source harvest. If the hierarchy cannot recover them, use a labeled bounded
abstraction calibrated so voluntary theft remains usually inferior to direct
production, as the period guide states. Factory gloves modify that one contest
through their sourced benefit.

This keeps the activity's interpersonal Thieving texture and apparatus economy
without creating a fake multiplayer simulation or a knowingly dominant
checkbox.

## Minimal persisted state

Persist only:

- active/inactive session;
- used and total slots;
- selected strategy;
- score;
- completed batch count/residue bonus;
- catalyst reserve;
- refining apparatus count; and
- temporary or real rewards found in rubble.

Charge, A/B reagents, doors, obstacles, other players, and map position are
per-review narration or bounded outcomes, not stored world state. Session close
atomically clears temporary Factory state and credits Brianpoints and any real
Rogue/Factory rewards. Undo restores the complete prior session snapshot.

## Independent design review

Fable agreed that pickpocketing should survive only as a bounded, review-priced
strategy effect without simulated players. Its proposed 45-review conversion
and residue penalty were rejected: the former invented a reviews-per-minute
scale and the latter contradicted the pinned source's positive 1%-per-batch
residue bonus. The eight-slot contract above is the integrated decision.
