# TzHaar Fight Pit horizontal readiness

Date: `2026-07-22`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **horizontal mechanic closure implemented and verified on canonical
main.**

Owning design: `memory-bank/source-audits/recon-coverage-closure-2026-07-18.md`.
The pattern-determined contract is a safe bounded-opponent, last-standing
activity with TokKul settlement. It does not reopen the settled competitive
solo-adaptation policy.

## Pinned period evidence

- `TzHaar Fight Pit` oldid `6516239`,
  `2012-11-01T16:20:05Z`:
  <https://runescape.wiki/w/TzHaar_Fight_Pit?oldid=6516239>.
  The literal cutoff wikitext establishes:
  - safe death with all items retained;
  - free-for-all last-player-standing victory;
  - a defeated player is ejected to the waiting room;
  - the winner may leave to collect TokKul or remain for the next game;
  - anything-goes equipment except a dwarf multicannon;
  - an equipped Fire cape doubles the TokKul reward;
  - late Tz-Kih, Tz-Kek, and Tok-Xil pressure followed by forced damage closes
    stalled rounds; and
  - TokKul equals the combined Combat levels of opponents defeated by the
    winner, excluding the winner and anyone who left.
- `RuneScape:Events Team/Fight Pits (24 Sept 2011)` oldid `4764019`,
  `2011-09-24T17:09:08Z`:
  <https://runescape.wiki/w/RuneScape%3AEvents_Team/Fight_Pits_%2824_Sept_2011%29?oldid=4764019>.
  This dated period-lineage page independently corroborates the last-standing,
  safe equipment, Fire-cape doubling, and waiting-room start shape.
- The current article retains an explicit worked example: defeating one
  Combat-138 opponent awards `138` TokKul. This corroborates that the period
  phrase “based on the combined combat levels” is literal summation rather
  than an unspecified multiplier:
  <https://runescape.wiki/w/TzHaar_Fight_Pit>.

## Cache identities

OpenRS2 revision 742 (`2012-11-07`) supplies:

- item `6529`, `Tokkul`, stackable currency identity;
- item `6570`, `Fire cape`, with `Wear`;
- item `21463`, `Battle-mage robe`, with `Wear`/`Destroy`;
- item `21468`, `Trickster robe`, with `Wear`/`Destroy`; and
- item `21473`, `Vanguard body`, with `Wear`/`Destroy`.

The cutoff Fight Pit page itself embeds `File:Redskull.png` as the champion
marker. The MediaWiki file history resolves the pre-EOC revision uploaded
`2012-04-14T02:06:32Z`: `25 × 25`, source SHA-1
`ebc4d2f4c63e9e37bf8a7141ed075105ec4ea84d`, local downloaded SHA-256
`b323fa6044077da6fd4700ae7e01d00b84fa0457b2948dbf41131a3c16ff8dfb`.
It is already icon-scale and should be copied losslessly rather than enlarged;
Qt owns the normalized display box.

The local Darkan item-config lineage independently supplies the three hybrid
top names, weights, and level requirements. Those identities prove existence,
not the hidden Fight Pit award chance or complete equipment effect.

## Horizontal implementation boundary

The smallest honest mechanic-complete route is:

1. direct entry creates a persistent safe match against three disclosed
   bounded simulated opponents;
2. one productive review advances one live six-tick engaged-opponent Combat
   slice plus bounded attrition among unengaged opponents;
3. safe death eliminates the player, restores match resources, pays no TokKul,
   and preserves ordinary inventory/equipment;
4. an opponent kill adds that opponent's Combat level to the pending TokKul
   purse and advances to the next surviving opponent;
5. one review of late-round pressure prevents an unwinnable hiding/stall state;
6. defeating the last opponent settles the exact summed TokKul, doubled when a
   Fire cape is equipped, and records the championship; and
7. explicit leave forfeits the pending purse and restores the prior Combat
   target.

Casual mode selects the next live opponent automatically. Advanced mode may
fix an aggressive or defensive match policy, but it does not invent target
choice among mechanically identical simulated players. Entry, policy changes,
leave, and reward collection are direct actions; match combat is review-owned.

## Disclosed abstractions

- `abstraction/owner-breadth-first`: three simulated opponents are the smallest
  roster that exercises multiple eliminations, attrition, last-standing state,
  and exact additive settlement. The period page specifies no fixed population.
- `abstraction/competitive-pattern`: opponent Combat levels are composed once
  at entry from a bounded band around the player's Combat level and persisted.
  The deterministic three-row band avoids spending a hidden RNG stream in a
  direct shop-style action and is never rerolled mid-match.
- `abstraction/anti-stall`: late arena pressure begins after twelve productive
  review beats and removes one tenth of maximum LP per further beat. This is a
  disclosed review-counted closer for the source-blocked monster/forced-damage
  timing, not a wall-clock simulation.
- `source_blocked`: exact monster-wave arrival and forced-damage timing. One
  late-round pressure beat is used only as an anti-stall closer and never as a
  wall-clock timer.

## Deliberately deferred data depth

- The three hybrid tops and their win/loss-shaped hidden chance are real cutoff
  rewards, but neither the cutoff page nor the dated cache exposes the award
  probability. Their complete degradation/protection/equipment behavior is a
  separate equipment-depth graph. They remain named reward depth rather than a
  fabricated horizontal roll.
- Full opponent archetype breadth, team/hiding strategies, exact late-monster
  rosters, global matchmaking history, and the wider TzHaar shop catalog are
  depth work. The shipped TokKul shops and existing Fire cape already make the
  horizontal currency and multiplier consequences real.

No owner design gap is present.

## Implemented closure

The canonical implementation uses schema 81 and the shared persistent-activity
arbiter. Direct entry and plan changes are undoable; productive reviews advance
one six-tick Combat slice; safe defeat, championship, and explicit leave settle
the persistent match atomically and restore the prior Combat target. The
Activities card exposes the saved policy, roster, pending TokKul, Fire-cape
multiplier, entry conflicts, and leave-forfeit consequence. The period red-skull
marker is stored losslessly and rendered inside the shared normalized icon box.

Focused pure, persistence, runtime, registry, integration, cadence, Combat, and
real offscreen-Qt interaction checks pass. The ordinary full discovery run
passes all `2,470` methods with `311` skips. Root inspected the ready and active
`1200 x 760` dark-palette renders: the period red-skull icon is normalized, the
card is compact, and neither state clips or requires internal scrolling.
The stable full real offscreen-Qt rerun also passes all `2,470` methods with
one declared skip.

A bounded read-only Sol-high Workflows pass exhausted its output budget before
returning a final review, so it is not counted as an independent sign-off. Its
partial evidence nevertheless exposed three candidates that root reproduced
and closed: loaded cannonballs now block entry, malformed empty rosters cannot
cash a pending purse, and the generic Combat auto-flee policy cannot create a
silent no-progress arena loop. Regression tests cover each failure mechanism.

Native Anki remains unclaimed because the native computer-use bridge failed to
start. Fable is deliberately reserved. Kimi's fresh gate reported only `4%`
weekly allowance and no required five-hour window, while the Claude quota probe
could return only stale auth data, so neither Kimi nor Opus was called and no
external taste approval is claimed for this slice.

Closure report:
`memory-bank/status-updates/tzhaar-fight-pit-horizontal-results-2026-07-22.html`
and <https://hebbv2uq7why.postplan.dev>.
